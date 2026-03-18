from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.7
    preferred_mood_tags: List[str] = field(default_factory=list)
    target_popularity: float = 0.5   # 0.0 = niche, 1.0 = mainstream
    preferred_decade: int = 2020


# ---------------------------------------------------------------------------
# Strategy: ScoringWeights
#
# Each ScoringWeights instance is one scoring "mode." All eight weights must
# sum to 1.0. Swap the mode to change how songs are ranked without touching
# any other code.
# ---------------------------------------------------------------------------

@dataclass
class ScoringWeights:
    """
    Controls how much each feature contributes to a song's final score.

    All weights must sum to 1.0.
    """
    genre: float        # categorical match
    mood: float         # categorical match
    energy: float       # proximity: 1 - |target - value|
    valence: float      # proximity: 1 - |target - value|
    acousticness: float # proximity: 1 - |target - value|
    mood_tags: float    # overlap: matched_tags / user_tags_count
    popularity: float   # proximity: 1 - |target - normalized_pop|
    decade: float       # proximity: 1 - distance_years / 50

    def validate(self) -> None:
        total = (
            self.genre + self.mood + self.energy + self.valence
            + self.acousticness + self.mood_tags + self.popularity + self.decade
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"ScoringWeights must sum to 1.0, got {total:.4f}")


# ---------------------------------------------------------------------------
# Named scoring modes (the strategy registry)
#
# BALANCED    — equal emphasis across all features (default)
# GENRE_FIRST — genre dominates; good for users who never leave their lane
# MOOD_FIRST  — mood dominates; good for context-driven listening (gym, study)
# ENERGY      — energy + valence dominate; useful for activity-based playlists
# VIBE_MATCH  — mood_tags dominate; rewards nuanced emotional fit over genre
# ---------------------------------------------------------------------------

SCORING_MODES: Dict[str, ScoringWeights] = {
    "balanced": ScoringWeights(
        genre=0.28, mood=0.20, energy=0.18, valence=0.10,
        acousticness=0.06, mood_tags=0.10, popularity=0.05, decade=0.03,
    ),
    "genre_first": ScoringWeights(
        genre=0.45, mood=0.18, energy=0.13, valence=0.08,
        acousticness=0.05, mood_tags=0.06, popularity=0.03, decade=0.02,
    ),
    "mood_first": ScoringWeights(
        genre=0.12, mood=0.40, energy=0.18, valence=0.12,
        acousticness=0.06, mood_tags=0.07, popularity=0.03, decade=0.02,
    ),
    "energy_focused": ScoringWeights(
        genre=0.12, mood=0.12, energy=0.38, valence=0.18,
        acousticness=0.10, mood_tags=0.04, popularity=0.04, decade=0.02,
    ),
    "vibe_match": ScoringWeights(
        genre=0.10, mood=0.15, energy=0.15, valence=0.12,
        acousticness=0.08, mood_tags=0.28, popularity=0.07, decade=0.05,
    ),
}


# ---------------------------------------------------------------------------
# OOP interface (used by tests)
# ---------------------------------------------------------------------------

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        mode: str = "balanced",
    ) -> List[Song]:
        weights = SCORING_MODES[mode]
        scored = sorted(
            self.songs,
            key=lambda s: self._score(user, s, weights),
            reverse=True,
        )
        return scored[:k]

    def _score(self, user: UserProfile, song: Song, weights: ScoringWeights) -> float:
        score, _ = score_song(_user_to_dict(user), _song_to_dict(song), weights)
        return score

    def explain_recommendation(
        self,
        user: UserProfile,
        song: Song,
        mode: str = "balanced",
    ) -> str:
        weights = SCORING_MODES[mode]
        _, reasons = score_song(_user_to_dict(user), _song_to_dict(song), weights)
        return "\n  ".join(reasons)


# ---------------------------------------------------------------------------
# Internal helpers — convert dataclass instances to dicts for score_song
# ---------------------------------------------------------------------------

def _user_to_dict(user: UserProfile) -> Dict:
    return {
        "favorite_genre": user.favorite_genre,
        "favorite_mood": user.favorite_mood,
        "target_energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
        "target_valence": user.target_valence,
        "preferred_mood_tags": user.preferred_mood_tags,
        "target_popularity": user.target_popularity,
        "preferred_decade": user.preferred_decade,
    }


def _song_to_dict(song: Song) -> Dict:
    return {
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "valence": song.valence,
        "acousticness": song.acousticness,
        "popularity": song.popularity,
        "release_decade": song.release_decade,
        "mood_tags": song.mood_tags,
    }


# ---------------------------------------------------------------------------
# Functional interface (used by main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to int/float."""
    import csv

    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    int_fields = {"id", "popularity", "release_decade"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for f_name in float_fields:
                row[f_name] = float(row[f_name])
            for f_name in int_fields:
                row[f_name] = int(row[f_name])
            row["mood_tags"] = row["mood_tags"].split("|")
            songs.append(dict(row))

    print(f"Loaded {len(songs)} songs")
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[ScoringWeights] = None,
) -> Tuple[float, List[str]]:
    """
    Return a (score, reasons) tuple using the given ScoringWeights strategy.
    Defaults to 'balanced' if no weights are provided.
    """
    if weights is None:
        weights = SCORING_MODES["balanced"]

    reasons = []

    # --- Categorical features ---
    if song["genre"] == user_prefs["favorite_genre"]:
        genre_score = 1.0
        reasons.append(f"genre match: {song['genre']} (+{weights.genre:.2f})")
    else:
        genre_score = 0.0

    if song["mood"] == user_prefs["favorite_mood"]:
        mood_score = 1.0
        reasons.append(f"mood match: {song['mood']} (+{weights.mood:.2f})")
    else:
        mood_score = 0.0

    # --- Proximity features ---
    energy_score = 1 - abs(user_prefs["target_energy"] - song["energy"])
    reasons.append(f"energy proximity: {energy_score:.2f} (+{energy_score * weights.energy:.2f})")

    valence_score = 1 - abs(user_prefs.get("target_valence", 0.7) - song["valence"])
    reasons.append(f"valence proximity: {valence_score:.2f} (+{valence_score * weights.valence:.2f})")

    acoustic_target = 1.0 if user_prefs["likes_acoustic"] else 0.0
    acoustic_score = 1 - abs(acoustic_target - song["acousticness"])
    reasons.append(f"acousticness proximity: {acoustic_score:.2f} (+{acoustic_score * weights.acousticness:.2f})")

    # --- Mood tags: fraction of user's desired tags present in the song ---
    user_tags = set(user_prefs.get("preferred_mood_tags", []))
    if user_tags:
        song_tags = set(song.get("mood_tags", []))
        overlap = len(user_tags & song_tags)
        tag_score = overlap / len(user_tags)
        matched = user_tags & song_tags
        reasons.append(
            f"mood tags: {overlap}/{len(user_tags)} matched "
            f"({', '.join(matched) or 'none'}) (+{tag_score * weights.mood_tags:.2f})"
        )
    else:
        tag_score = 0.5
        reasons.append(f"mood tags: no preference (neutral +{tag_score * weights.mood_tags:.2f})")

    # --- Popularity: proximity to user's mainstream preference ---
    song_pop_normalized = song["popularity"] / 100.0
    pop_score = 1 - abs(user_prefs.get("target_popularity", 0.5) - song_pop_normalized)
    reasons.append(
        f"popularity: {song['popularity']}/100 → proximity {pop_score:.2f} (+{pop_score * weights.popularity:.2f})"
    )

    # --- Release decade: each 10 years away costs 0.2; capped at 50 years ---
    decade_distance = abs(user_prefs.get("preferred_decade", 2020) - song["release_decade"])
    decade_score = max(0.0, 1.0 - decade_distance / 50)
    reasons.append(
        f"decade: {song['release_decade']} (distance {decade_distance}yr) "
        f"→ {decade_score:.2f} (+{decade_score * weights.decade:.2f})"
    )

    total = (
        weights.genre        * genre_score
        + weights.mood       * mood_score
        + weights.energy     * energy_score
        + weights.valence    * valence_score
        + weights.acousticness * acoustic_score
        + weights.mood_tags  * tag_score
        + weights.popularity * pop_score
        + weights.decade     * decade_score
    )

    return total, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song using the named mode, sort descending, return top k
    as (song, score, explanation) tuples.
    """
    weights = SCORING_MODES[mode]
    scored = [
        (song, score, "\n  ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song, weights)]
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
