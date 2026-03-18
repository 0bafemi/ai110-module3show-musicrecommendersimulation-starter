# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify's Discover Weekly operate in two stages: a massive retrieval pass that scores millions of songs using collaborative filtering (what users with similar profiles to me listened to) combined with audio feature analysis, followed by a ranking pass that reorders candidates based on context signals like time of day, device, or recent listening history. These systems also blend in NLP signals — scanning music blogs and playlist names to understand cultural meaning that raw audio features miss. Our simulation focuses on the content-based half of that pipeline: given a user's stated taste preferences, score every song by how closely its attributes match, then rank by score and return the top K. We will prioritize explainability over accuracy — every recommendation will have a human-readable reason attached to it, which real production systems rarely surface to users but is essential for understanding what the algorithm is actually doing.

## Feature Specification

*Song
├── id, title, artist       → identity only (never scored)
├── genre                   → categorical, weighted 0.35
├── mood                    → categorical, weighted 0.25
├── energy      (0.0–1.0)   → proximity scored, weighted 0.20
├── valence     (0.0–1.0)   → proximity scored, weighted 0.12
├── acousticness(0.0–1.0)   → proximity scored, weighted 0.08
├── tempo_bpm               → stored, excluded from v1 scoring
└── danceability            → stored, excluded from v1 scoring

*UserProfile
├── favorite_genre    (str)          → "pop", "lofi", "rock" etc.
├── favorite_mood     (str)          → "happy", "chill", "intense" etc.
├── target_energy     (float 0–1)    → how calm vs. intense they want
├── target_valence    (float 0–1)    → how positive vs. dark they want
└── likes_acoustic    (bool)         → converted to 1.0/0.0 for scoring

*My Scoring Rules
genre_score    = 1.0 if song.genre == user.favorite_genre else 0.0
mood_score     = 1.0 if song.mood  == user.favorite_mood  else 0.0
energy_score   = 1 - |user.target_energy  - song.energy|
valence_score  = 1 - |user.target_valence - song.valence|
acoustic_score = 1 - |float(user.likes_acoustic) - song.acousticness|

total = (0.35 × genre_score)
      + (0.25 × mood_score)
      + (0.20 × energy_score)
      + (0.12 × valence_score)
      + (0.08 × acoustic_score)

Result: one float between 0.0 and 1.0 per song.

*My Reccommenation Alg
┌─────────────────┐
│   songs.csv     │  ← all 10 songs loaded into memory
└────────┬────────┘
         │  for each song
         ▼
┌─────────────────┐
│  Scoring Rule   │  ← compute weighted proximity score (0.0–1.0)
│  (per song)     │
└────────┬────────┘
         │  list of (song, score) pairs
         ▼
┌─────────────────┐
│  Ranking Rule   │  ← sort descending by score
│  (across all)   │
└────────┬────────┘
         │  top K songs + scores
         ▼
┌─────────────────┐
│  Explanation    │  ← generate human-readable reason per song
│  Generator      │
└────────┬────────┘
         ▼
    Final output: [(song, score, explanation), ...]

This system may over-prioritize genre matching, causing it to ignore songs that perfectly match a user's energy, mood, and emotional tone simply because they come from a different genre — a user who loves chill lofi might never discover that ambient or jazz would feel identical to them. Because it relies entirely on content-based filtering with no awareness of what other users enjoy, it creates a filter bubble: the more someone uses it, the narrower their recommendations become, reinforcing existing taste rather than expanding it. The dataset's uneven genre distribution compounds this — lofi has three songs while most other genres have one, so low-energy users will be over-served while niche taste profiles like metal or classical hit a hard ceiling on recommendation diversity. Finally, since the system has no memory between sessions and no novelty signal, a user with a stable profile will receive the same songs every time — there is no mechanism to surface something new just because the user hasn't heard it yet.




---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

---

![Terminal output showing top recommendations](Screenshot%202026-03-18%20125630.png)

*Figure 1: Top 5 recommendations for a pop/happy user profile*