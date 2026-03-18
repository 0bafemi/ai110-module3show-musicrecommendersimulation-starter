# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder is designed to suggest songs that match a user's stated mood, genre preference, and energy level. It is built for classroom exploration — not production use — and is intended to demonstrate how a simple content-based recommender works step by step. It assumes the user can accurately describe their own taste through a small set of preferences, and that those preferences stay consistent within a single session.

**Not intended for:** real deployment, personalization at scale, or users who want discovery beyond their stated preferences.

---

## 3. How the Model Works

VibeFinder looks at five things about each song — its genre, mood, energy level, emotional positivity (valence), and how acoustic it sounds — and compares them to what the user said they like. For categorical features like genre and mood, it gives full credit for a match and no credit for a mismatch. For numerical features like energy, it gives more credit the closer the song is to the user's target — a song at exactly the right energy scores perfectly, and songs further away score lower on both sides. Each feature is weighted by importance: genre counts the most (35%), followed by mood (25%), energy (20%), valence (12%), and acousticness (8%). The five weighted scores are added together to produce a single relevance number between 0 and 1 for each song. All songs are then sorted by that number and the top results are returned with a plain-language explanation of why each was chosen.

---

## 4. Data

The catalog contains 18 songs, expanded from an original 10. Genres represented include pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, edm, folk, metal, soul, and reggae. Moods covered include happy, chill, intense, euphoric, romantic, melancholic, nostalgic, angry, sad, peaceful, relaxed, focused, and moody. The original dataset was heavily skewed toward lofi (3 songs) and lacked genres like hip-hop, classical, and folk entirely. Eight songs were added to improve diversity. Even so, most genres still have only one representative, which limits how varied recommendations can be for niche taste profiles.

---

## 5. Strengths

The system works best for users whose taste aligns with well-represented genres like lofi or pop, where multiple candidates exist to fill a ranked list. The scoring correctly captures the difference between calm and intense music — energy and acousticness together do a good job separating ambient/jazz/lofi from pop/rock/edm without needing any outside data. The weighted-sum approach is fully transparent: every score can be traced back to individual feature contributions, making it easy to explain why a song was recommended. Users with a clear, consistent preference (e.g., always wants chill and acoustic) get results that reliably match their stated intent.

---

## 6. Limitations and Bias

The most significant weakness is that genre matching dominates the scoring at a 0.35 weight, causing the system to over-prioritize genre alignment over every other dimension of taste combined. A user who prefers chill, low-energy music will reliably receive lofi recommendations above all others — not because lofi is the best match on energy, mood, or acousticness, but simply because lofi has three songs in the catalog while ambient and jazz each have one, giving it a statistical advantage that has nothing to do with quality or fit. This uneven genre distribution means the system unintentionally favors users whose tastes align with overrepresented genres: a pop or lofi listener receives a diverse shortlist of reasonable candidates, while a metal, classical, or reggae listener hits a hard ceiling of one song and cannot receive a varied top-5 no matter how well their profile is tuned. The system also ignores features entirely outside its scoring model — lyrics, cultural context, language, and listening history — meaning two songs can receive identical scores despite feeling completely different to a real listener. Because the system has no memory across sessions and no novelty signal, a user with a stable profile will receive the exact same recommendations indefinitely, reinforcing a filter bubble rather than helping them discover anything new.

---

## 7. Evaluation

Three profiles were tested: a Happy Pop listener wanting upbeat high-energy music, a Chill Lofi listener wanting low-energy focus music, and a Melancholic Classical listener wanting something slow and emotionally heavy. The most surprising result was that Gym Hero consistently ranked in the top three for the Happy Pop profile — despite having an "intense" mood, not "happy." The system saw a genre match and a close energy score and rewarded it anyway, with no understanding that intense and happy feel completely different to a real listener. The Chill Lofi profile confirmed the dataset representation problem: lofi dominated every result not because it was the best fit, but simply because three lofi songs exist while ambient and jazz each have one. The Classical profile exposed the dataset ceiling most clearly — after ranking Winter Sonata first, the system ran out of strong candidates and drifted toward soul and folk, which share high acousticness but not the same emotional character.

---

## 8. Future Work

- **Mood proximity instead of exact match.** Rather than treating every mood mismatch as a zero, group moods by emotional similarity (e.g., "relaxed" and "chill" are close; "angry" and "happy" are not) so the system can give partial credit for near matches.
- **Diversity enforcement in the ranking step.** Add a rule that prevents the same genre from appearing more than once in the top 5, forcing the system to surface the best non-lofi and non-pop candidates even when they score slightly lower.
- **Collaborative signals.** Track which songs real users skip or replay and use that behavioral data to adjust scores over time, moving the system from pure content-based filtering toward a hybrid approach that can discover taste patterns the user never explicitly stated.

---

## 9. Personal Reflection

The biggest learning moment was realizing how much a simple math formula can *feel* intelligent without actually understanding anything. When VibeFinder returned a reasonable-looking list for the Happy Pop profile, it looked like the system "got it" — but it was just arithmetic. The Gym Hero bug made that clear: the algorithm had no idea that intense and happy are opposites; it only saw numbers that were close together. Using AI tools throughout this project was genuinely helpful for working through the scoring math, articulating biases, and drafting documentation — but every output needed verification against the actual data. The AI suggested valence as a strong feature, and checking the CSV confirmed it: valence really does separate moody synthwave from happy indie pop in a way that mood labels alone miss. What surprised me most is that even a 5-feature weighted formula, applied to 18 songs, produces output that a real person would look at and say "yeah, that makes sense" — which makes it easy to see how users could trust these systems far more than they should. If I extended this project, I would build a session-history layer that tracks what the user has already heard and penalizes repeated recommendations, then test whether adding even basic collaborative filtering — just "users who liked X also liked Y" — meaningfully reduces the filter bubble problem compared to the content-only version.
