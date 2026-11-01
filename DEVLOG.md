# Dev log

One entry per completed build step: what was built, what we learned, and why we made any design change.
The "Why" lines are the designer's own words. Decisions with full reasons live in the Dev Status doc's decisions log.

## 2026-11-01 · Setup
- **Built:** git repo with `.gitignore` (excludes `.env` and session logs), connected to the private GitHub repo `last-day-inn`.
- **Learned:** pushing needs a fine-grained token with Contents read/write; a token pasted at the shell prompt counts as leaked.
- **Why:** Least access: the token only reaches this test project, so if it leaks, nothing else is exposed.

## 2026-11-01 · M1.1 world.json from the brief
- **Built:** `world.json` from CLAUDE.md only; gaps marked TODO, then filled from designer answers (Q1–Q15, D1–D7), with all Claude-written text marked draft.
- **Learned:** the brief left 15 gaps a game can't run without (map, note pickup, gate rules, what "near the clock" means); at 1 action per phase the Loop 1 escape used every turn.
- **Why:** 8 actions (2 per phase) give players room to explore without feeling rushed; we'll tune it after playtests. The sealed envelope makes the story hold together. An always-locked gate keeps the MVP simple: one rule, less to remember, fewer edge cases.

## 2026-11-01 · M1.2 Engine + CLI
- **Built:** `engine.py` (reads all text from world.json; `observe` / `actions` / `act`), `play.py` terminal menu, JSON session logs, tests.
- **Learned:** playing it caught Mira "in her armchair" in the Garden, and "show item to a place" options buried the key choice (6 of 12 menu lines).
- **Why:** Showing an item to a place (an object to another object) rarely means anything, so it added menu noise without adding discovery. Revisit after the MVP.

## 2026-11-01 · M1.3 Loop 2 opening with the memory anomaly
- **Built:** Mira's first-meeting line per loop; "You still haven't tried the pie." ends the game when she was by the clock at midnight.
- **Learned:** Mira's clock myth can never trigger, because the anomaly ends the game the moment you meet her.
- **Why:** Making it reachable adds complexity and scope; the MVP only needs to prove the first reset makes players want to try again.

## 2026-11-01 · M1.4 + M2.1 Playtest agent
- **Built:** `agent.py` plays through the same interface as a human; curious and escape personas, journal on/off, per-run and aggregate reports; Claude or Gemini.
- **Learned:** report facts must come from the game log, not the AI; `gemini-3.8-flash` was listed for our key but never answered, `gemini-3.5-flash` does.
- **Why:** Gemini's free tier lets us run playtests without paying; Claude stays available as an option.
