"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "target_valence": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "target_valence": 0.60,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.92,
        "target_valence": 0.40,
        "likes_acoustic": False,
    },
}


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a formatted recommendation block for one user profile."""
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print("\n" + "=" * 40)
    print(f"  Profile : {label}")
    print(f"  Top {len(recommendations)} Recommendations")
    print("=" * 40)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  --  {song['artist']}")
        print(f"    Score : {score:.3f}")
        print(f"    Why   :")
        for line in explanation.split("\n"):
            print(f"      {line.strip()}")

    print("\n" + "=" * 40)


def main() -> None:
    songs = load_songs("data/songs.csv")

    for label, prefs in PROFILES.items():
        print_recommendations(label, prefs, songs)


if __name__ == "__main__":
    main()
