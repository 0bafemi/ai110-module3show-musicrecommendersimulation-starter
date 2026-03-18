"""
Command line runner for the Music Recommender Simulation.

Usage:
  python -m src.main                     # all profiles, balanced mode
  python -m src.main --mode genre_first  # all profiles, chosen mode
  python -m src.main --compare           # one profile across all modes side-by-side
  python -m src.main --diversity         # show before/after diversity penalty comparison

Available modes:
  balanced       equal emphasis across all features (default)
  genre_first    genre dominates — stays in your lane
  mood_first     mood dominates — context-driven listening
  energy_focused energy + valence dominate — activity-based playlists
  vibe_match     mood_tags dominate — nuanced emotional fit over genre
"""

import sys
from tabulate import tabulate
from src.recommender import load_songs, recommend_songs, SCORING_MODES, DiversityConfig

# Feature display order and short labels for the reasons breakdown table
REASON_LABELS = [
    "genre",
    "mood tags",   # must come before "mood" — "mood tags" starts with "mood "
    "mood",
    "energy proximity",
    "valence proximity",
    "acousticness proximity",
    "popularity",
    "decade",
]


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


def _parse_reason_value(reason_line: str) -> str:
    """Extract the last +X.XX) value from a reason string."""
    import re
    # Matches either (+0.10) or (neutral +0.05) — both end with +digits)
    match = re.search(r'\+([0-9.]+)\)$', reason_line.strip())
    return f"+{match.group(1)}" if match else "-"


def _build_reason_row(reason_lines: list) -> dict:
    """
    Map each raw reason line to its short label and extract the (+X.XX) value.
    Uses prefix + delimiter matching to avoid 'mood' swallowing 'mood tags'.
    """
    row = {label: "" for label in REASON_LABELS}
    for line in reason_lines:
        stripped = line.strip().lower()
        for label in REASON_LABELS:
            # Require label to be followed by ':' or ' ' to avoid prefix collisions
            prefix = label.lower()
            if stripped.startswith(prefix) and len(stripped) > len(prefix) \
                    and stripped[len(prefix)] in (':', ' '):
                row[label] = _parse_reason_value(line)
                break
    return row


def print_recommendations(
    label: str,
    user_prefs: dict,
    songs: list,
    mode: str = "balanced",
    diversity: DiversityConfig = None,
    k: int = 5,
) -> None:
    """
    Print two tables per profile:
      1. Summary table  — rank, title, artist, genre, mood, score
      2. Reasons table  — one row per song, one column per scoring feature
    """
    recommendations = recommend_songs(user_prefs, songs, k=k, mode=mode, diversity=diversity)

    # ── Header ────────────────────────────────────────────────────────────────
    div_note = f"  diversity on (artist*{diversity.artist_penalty} genre*{diversity.genre_penalty})" \
               if diversity else ""
    print(f"\n{'=' * 72}")
    print(f"  Profile : {label}   |   Mode : {mode}{div_note}")
    print(f"{'=' * 72}")

    # ── Table 1: Summary ──────────────────────────────────────────────────────
    summary_rows = []
    reason_rows  = []

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        summary_rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            song["genre"],
            song["mood"],
            song["energy"],
            f"{score:.3f}",
        ])

        raw_lines = [ln.strip() for ln in explanation.split("\n") if ln.strip()]
        reason_row = _build_reason_row(raw_lines)
        # Check for diversity penalty note
        penalty_lines = [ln for ln in raw_lines if "diversity penalty" in ln.lower()]
        reason_row["diversity penalty"] = penalty_lines[0].replace("diversity penalty: ", "") \
                                          if penalty_lines else ""
        reason_row["#"] = f"#{rank}"
        reason_rows.append(reason_row)

    summary_headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score"]
    print("\n" + tabulate(summary_rows, headers=summary_headers, tablefmt="simple"))

    # ── Table 2: Score breakdown (reasons) ────────────────────────────────────
    reason_table_headers = ["#"] + REASON_LABELS
    has_penalty = any(r.get("diversity penalty") for r in reason_rows)
    if has_penalty:
        reason_table_headers.append("diversity penalty")

    reason_table_rows = [
        [r["#"]] + [r[col] for col in reason_table_headers[1:]]
        for r in reason_rows
    ]

    print("\n  Score breakdown (contribution per feature):")
    print(tabulate(reason_table_rows, headers=reason_table_headers, tablefmt="simple"))
    print()


def run_compare(songs: list, profile_name: str = "High-Energy Pop", k: int = 3) -> None:
    """Run one profile through every scoring mode, print top-k titles per mode."""
    prefs = PROFILES[profile_name]

    print(f"\n{'=' * 50}")
    print(f"  COMPARE: '{profile_name}' across all modes (top {k})")
    print(f"{'=' * 50}")

    for mode_name in SCORING_MODES:
        recs = recommend_songs(prefs, songs, k=k, mode=mode_name)
        titles = [f"#{i+1} {r[0]['title']}" for i, r in enumerate(recs)]
        print(f"\n  [{mode_name:>14}]  {' | '.join(titles)}")

    print()


def run_diversity_comparison(songs: list, k: int = 5) -> None:
    """
    For each profile, print the top-k list WITHOUT and WITH diversity penalty
    side-by-side so the re-ranking effect is clearly visible.
    """
    diversity = DiversityConfig(artist_penalty=0.4, genre_penalty=0.6)

    for label, prefs in PROFILES.items():
        without = recommend_songs(prefs, songs, k=k, mode="balanced")
        with_d  = recommend_songs(prefs, songs, k=k, mode="balanced", diversity=diversity)

        print(f"\n{'=' * 60}")
        print(f"  Profile: {label}")
        print(f"  {'WITHOUT diversity':<28}  WITH diversity (artist*0.4  genre*0.6)")
        print(f"  {'-' * 56}")

        for i in range(k):
            left  = without[i][0] if i < len(without) else None
            right = with_d[i][0]  if i < len(with_d)  else None
            left_str  = f"{left['title']} [{left['genre']}]"   if left  else "-"
            right_str = f"{right['title']} [{right['genre']}]" if right else "-"

            marker = "  " if (left and right and left["title"] == right["title"]) else ">>"
            print(f"  #{i+1}  {left_str:<28}  {marker}  {right_str}")

        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    args = sys.argv[1:]
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

    if "--compare" in args:
        run_compare(songs)
    elif "--diversity" in args:
        run_diversity_comparison(songs)
    else:
        diversity = DiversityConfig() if "--with-diversity" in args else None
        for label, prefs in PROFILES.items():
            print_recommendations(label, prefs, songs, mode=mode, diversity=diversity)


if __name__ == "__main__":
    main()
