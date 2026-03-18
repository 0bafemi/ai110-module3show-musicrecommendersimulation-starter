"""
Command line runner for the Music Recommender Simulation.

Usage:
  python -m src.main                     # runs all profiles in balanced mode
  python -m src.main --mode genre_first  # runs all profiles in genre_first mode
  python -m src.main --compare           # runs one profile across all modes side-by-side

Available modes:
  balanced       equal emphasis across all features (default)
  genre_first    genre dominates — stays in your lane
  mood_first     mood dominates — context-driven listening
  energy_focused energy + valence dominate — activity-based playlists
  vibe_match     mood_tags dominate — nuanced emotional fit over genre
"""

import sys
from src.recommender import load_songs, recommend_songs, SCORING_MODES


PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "target_valence": 0.85,
        "likes_acoustic": False,
        "preferred_mood_tags": ["uplifting", "driven"],
        "target_popularity": 0.80,
        "preferred_decade": 2020,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "target_valence": 0.60,
        "likes_acoustic": True,
        "preferred_mood_tags": ["calm", "introspective"],
        "target_popularity": 0.40,
        "preferred_decade": 2020,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.92,
        "target_valence": 0.40,
        "likes_acoustic": False,
        "preferred_mood_tags": ["aggressive", "powerful"],
        "target_popularity": 0.35,
        "preferred_decade": 2010,
    },
}


def print_recommendations(
    label: str,
    user_prefs: dict,
    songs: list,
    mode: str = "balanced",
    k: int = 5,
) -> None:
    """Print a formatted recommendation block for one profile + mode."""
    recommendations = recommend_songs(user_prefs, songs, k=k, mode=mode)

    print("\n" + "=" * 50)
    print(f"  Profile : {label}")
    print(f"  Mode    : {mode}")
    print(f"  Top {len(recommendations)} Recommendations")
    print("=" * 50)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  --  {song['artist']}")
        print(f"    Score : {score:.3f}")
        print(f"    Why   :")
        for line in explanation.split("\n"):
            print(f"      {line.strip()}")

    print("\n" + "=" * 50)


def run_compare(songs: list, profile_name: str = "High-Energy Pop", k: int = 3) -> None:
    """
    Run one profile through every scoring mode and print the #1 result for each.
    Makes it easy to see how mode choice changes the top recommendation.
    """
    prefs = PROFILES[profile_name]

    print(f"\n{'=' * 50}")
    print(f"  COMPARE: '{profile_name}' across all modes (top {k})")
    print(f"{'=' * 50}")

    for mode_name in SCORING_MODES:
        recs = recommend_songs(prefs, songs, k=k, mode=mode_name)
        titles = [f"#{i+1} {r[0]['title']}" for i, r in enumerate(recs)]
        print(f"\n  [{mode_name:>14}]  {' | '.join(titles)}")

    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Parse simple CLI flags
    args = sys.argv[1:]
    compare_mode = "--compare" in args
    mode = "balanced"
    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 < len(args):
            requested = args[idx + 1]
            if requested in SCORING_MODES:
                mode = requested
            else:
                print(f"Unknown mode '{requested}'. Available: {list(SCORING_MODES)}")
                sys.exit(1)

    if compare_mode:
        run_compare(songs)
    else:
        for label, prefs in PROFILES.items():
            print_recommendations(label, prefs, songs, mode=mode)


if __name__ == "__main__":
    main()
