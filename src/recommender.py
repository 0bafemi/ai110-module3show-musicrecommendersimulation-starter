from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to int/float."""
    import csv

    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    int_fields = {"id"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in float_fields:
                row[field] = float(row[field])
            for field in int_fields:
                row[field] = int(row[field])
            songs.append(dict(row))

    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a (score, reasons) tuple: weighted 0.0–1.0 match score and a per-feature explanation list."""
    reasons = []

    # Categorical features
    if song["genre"] == user_prefs["favorite_genre"]:
        genre_score = 1.0
        reasons.append(f"genre match: {song['genre']} (+{0.35:.2f})")
    else:
        genre_score = 0.0

    if song["mood"] == user_prefs["favorite_mood"]:
        mood_score = 1.0
        reasons.append(f"mood match: {song['mood']} (+{0.25:.2f})")
    else:
        mood_score = 0.0

    # Proximity features (1 - gap)
    energy_score = 1 - abs(user_prefs["target_energy"] - song["energy"])
    reasons.append(f"energy proximity: {energy_score:.2f} (+{energy_score * 0.20:.2f})")

    valence_score = 1 - abs(user_prefs["target_valence"] - song["valence"])
    reasons.append(f"valence proximity: {valence_score:.2f} (+{valence_score * 0.12:.2f})")

    acoustic_target = 1.0 if user_prefs["likes_acoustic"] else 0.0
    acoustic_score = 1 - abs(acoustic_target - song["acousticness"])
    reasons.append(f"acousticness proximity: {acoustic_score:.2f} (+{acoustic_score * 0.08:.2f})")

    total = (
        0.35 * genre_score
        + 0.25 * mood_score
        + 0.20 * energy_score
        + 0.12 * valence_score
        + 0.08 * acoustic_score
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
