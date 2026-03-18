from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


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


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return scored[:k]

    def _score(self, user: UserProfile, song: Song) -> float:
        score, _ = score_song(
            {
                "favorite_genre": user.favorite_genre,
                "favorite_mood": user.favorite_mood,
                "target_energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
                "target_valence": user.target_valence,
                "preferred_mood_tags": user.preferred_mood_tags,
                "target_popularity": user.target_popularity,
                "preferred_decade": user.preferred_decade,
            },
            {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "valence": song.valence,
                "acousticness": song.acousticness,
                "popularity": song.popularity,
                "release_decade": song.release_decade,
                "mood_tags": song.mood_tags,
            },
        )
        return score

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = score_song(
            {
                "favorite_genre": user.favorite_genre,
                "favorite_mood": user.favorite_mood,
                "target_energy": user.target_energy,
                "likes_acoustic": user.likes_acoustic,
                "target_valence": user.target_valence,
                "preferred_mood_tags": user.preferred_mood_tags,
                "target_popularity": user.target_popularity,
                "preferred_decade": user.preferred_decade,
            },
            {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "valence": song.valence,
                "acousticness": song.acousticness,
                "popularity": song.popularity,
                "release_decade": song.release_decade,
                "mood_tags": song.mood_tags,
            },
        )
        return "\n  ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to int/float."""
    import csv

    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    int_fields = {"id", "popularity", "release_decade"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in float_fields:
                row[field] = float(row[field])
            for field_name in int_fields:
                row[field_name] = int(row[field_name])
            row["mood_tags"] = row["mood_tags"].split("|")
            songs.append(dict(row))

    print(f"Loaded {len(songs)} songs")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Return a (score, reasons) tuple.

    Weights (must sum to 1.0):
      genre       0.28  categorical match
      mood        0.20  categorical match
      energy      0.18  proximity: 1 - |target - value|
      valence     0.10  proximity: 1 - |target - value|
      acousticness 0.06 proximity: 1 - |target - value|
      mood_tags   0.10  overlap: matched_tags / user_tags_count
      popularity  0.05  proximity: 1 - |target - song_pop_normalized|
      decade      0.03  proximity: 1 - distance/50 (max 50 years apart)
    """
    reasons = []

    # --- Categorical features ---
    if song["genre"] == user_prefs["favorite_genre"]:
        genre_score = 1.0
        reasons.append(f"genre match: {song['genre']} (+{0.28:.2f})")
    else:
        genre_score = 0.0

    if song["mood"] == user_prefs["favorite_mood"]:
        mood_score = 1.0
        reasons.append(f"mood match: {song['mood']} (+{0.20:.2f})")
    else:
        mood_score = 0.0

    # --- Proximity features ---
    energy_score = 1 - abs(user_prefs["target_energy"] - song["energy"])
    reasons.append(f"energy proximity: {energy_score:.2f} (+{energy_score * 0.18:.2f})")

    valence_score = 1 - abs(user_prefs.get("target_valence", 0.7) - song["valence"])
    reasons.append(f"valence proximity: {valence_score:.2f} (+{valence_score * 0.10:.2f})")

    acoustic_target = 1.0 if user_prefs["likes_acoustic"] else 0.0
    acoustic_score = 1 - abs(acoustic_target - song["acousticness"])
    reasons.append(f"acousticness proximity: {acoustic_score:.2f} (+{acoustic_score * 0.06:.2f})")

    # --- Mood tags: fraction of user's desired tags present in the song ---
    user_tags = set(user_prefs.get("preferred_mood_tags", []))
    if user_tags:
        song_tags = set(song.get("mood_tags", []))
        overlap = len(user_tags & song_tags)
        tag_score = overlap / len(user_tags)
        matched = user_tags & song_tags
        reasons.append(
            f"mood tags: {overlap}/{len(user_tags)} matched "
            f"({', '.join(matched) or 'none'}) (+{tag_score * 0.10:.2f})"
        )
    else:
        tag_score = 0.5  # neutral when user has no tag preference
        reasons.append(f"mood tags: no preference (neutral +{tag_score * 0.10:.2f})")

    # --- Popularity: proximity to user's mainstream preference (0=niche, 1=mainstream) ---
    song_pop_normalized = song["popularity"] / 100.0
    pop_score = 1 - abs(user_prefs.get("target_popularity", 0.5) - song_pop_normalized)
    reasons.append(
        f"popularity: {song['popularity']}/100 → proximity {pop_score:.2f} (+{pop_score * 0.05:.2f})"
    )

    # --- Release decade: each 10 years away costs 0.2; max distance capped at 50 years ---
    decade_distance = abs(user_prefs.get("preferred_decade", 2020) - song["release_decade"])
    decade_score = max(0.0, 1.0 - decade_distance / 50)
    reasons.append(
        f"decade: {song['release_decade']} (distance {decade_distance}yr) "
        f"→ {decade_score:.2f} (+{decade_score * 0.03:.2f})"
    )

    total = (
        0.28 * genre_score
        + 0.20 * mood_score
        + 0.18 * energy_score
        + 0.10 * valence_score
        + 0.06 * acoustic_score
        + 0.10 * tag_score
        + 0.05 * pop_score
        + 0.03 * decade_score
    )

    return total, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, and return the top k as (song, score, explanation) tuples."""
    scored = [
        (song, score, "\n  ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    return ranked[:k]
