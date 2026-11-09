# Dev log

One entry per completed build step: what was built, what we learned, and why we made any design change.
The "Why" lines are the designer's own words. Decisions with full reasons live in the Dev Status doc's decisions log.

## 2026-11-01 · Setup
- **Built:** git repo with `.gitignore` (excludes `.env` and session logs), connected to the private GitHub repo `last-day-inn`.
- **Learned:** pushing needs a fine-grained token with Contents read/write, kept out of chat, the shell and the repo.
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

## 2026-11-01 · Playtest agent limits
- **Built:** one run per command (`--all` is opt-in), a 40-action cap, `--dry-run` with a fake model, API-call count in every report, reports that never overwrite, partial reports when a run fails.
- **Learned:** Gemini's free tier allows 5 requests a minute and 20 a day per model; a full run needs about 15–27, so a free-tier run may not fit in one day.
- **Why:** To keep API usage under control: no runaway runs or surprise costs, and `--dry-run` tests the pipeline for free.

## 2026-11-01 · Designer playtest fixes
- **Built:** room text shows on arrival in (parentheses), then a one-line intro the first time you meet each character; ✓ marks actions taken this loop; Mira's Loop 1 line now sets up the pie: "You're new here. Try the pie tonight; it's the best thing about this place." "Examine Pie" now appears only in the Evening, when the pie is served.
- **Learned:** playing it ourselves caught what the tests couldn't: Mira's old line referred to a pie the player had never heard of, so the Loop 2 "still" line had nothing to contrast with.
- **Why:** Playing it myself showed readability problems: the room and characters should come first, and Mira's pie line made no sense to a new player. The ✓ reminds players what they've already done so they don't waste actions; later we may hide repeated options or let them cost no action.

## 2026-11-01 · Playtest interview
- **Built:** `--interview` asks a finished run's player follow-up questions; reports now save the full conversation so interviews replay it exactly.
- **Learned:** the first live player guessed Mira was the girl in the photo but never showed it to her, because nothing hinted that would matter; it only learned what the photo shows from the journal (with the journal off, the clue never appears); the clock's little door and the old pie line both read as false promises.
- **Why:** Some of the player's choices had unclear motives. For example, the photo led it to the Lobby even though the game never said what the photo showed. Asking follow-up questions explains the "why" behind the move log.

## 2026-11-01 · Bug fix: picked-up items show their content
- **Built:** picking up an item now shows what it says or depicts (the photo and the closing notice were silent); one engine rule covers every item.
- **Learned:** the agent interview exposed it: with the journal off, the game's central clue (the girl with the blue ribbon) never appeared.
- **Why:** Making players check the journal for key details adds friction to solving the mystery. Showing an item's content when you pick it up gives immediate feedback and helps players piece the story together.

## 2026-11-01 · M2.2 Report-driven fix: the clock's little door
- **Built:** first full run → read report → one world.json change → re-run → compare (commits `c41857d` before, `6a654af` after). A second look at the clock now says "The little door won't open."
- **Learned:** repeat door attempts in one loop went 2 → 1, and the player later wrote "since the door wouldn't open before"; the reveal can still be missed when the photo reaches Mira only in Loop 3. One run per side is a hint, not proof.
- **Why:** A door that never opens, with no explanation, feels like a false promise and discourages players.

## 2026-11-02 · Report-driven fix 2: the clock door as a clue (backfired)
- **Built:** second clock look shows a child's scratched star (commits `9a0014c` before, `4ab5681` after); smarter waste counter (a repeat only counts if it showed the same text again).
- **Learned:** a physical mark on a door reads as a mechanism to activate: clock looks 4 → 5, door/star notes 8 → 11. It did strengthen the girl → Mira link (1 → 3 notes), but no one acted on it. A clue should point at a person or a question, not at an object that looks interactive.
- **Why:** A clue on a second look could make checking again feel fun and rewarded, but the star widened the misleading gap and backfired.

## 2026-11-02 · No loop counter on screen; clearer turn layout
- **Built:** the status line and journal no longer show "Loop" numbers; the journal splits into "From before you woke" and "Today" after waking again; MIDNIGHT and MORNING banners mark the reset; `▶ You:` echo and separators between turns; the agent's reset prompt no longer says "a new loop".
- **Learned:** showing "Loop 1" gave the mystery away, and our agent had been partly told about the loop, so earlier "it discovered the loop" results were weaker than they looked. Without any hint, both personas still inferred a time loop after the first reset.
- **Why:** Hiding the loop keeps the mystery and lets players discover it on their second attempt, instead of being told everything from the beginning.

## 2026-11-02 · Report-driven fix 3: clock door removed
- **Built:** the clock no longer mentions a little door ("the case tall enough to hide a child"); commits `f937d34` before, `e1bc6d1` after, both personas. Also a "You know:" line for the inscription.
- **Learned:** door talk fell 6 → 1 (curious) and 5 → 0 (escape), and the curious player reached the reveal in 12 moves; but the escape player still tried to open the clock after Mira said she hid in it. The clock pulls attention because it's the heart of the story, not only because of one line.
- **Why:** The door misled players too much; removing it keeps the clock's story without promising something that never opens.

## 2026-11-02 · M2.1 live: both personas × journal on/off + aggregate
- **Built:** the first live `--all` run (commit `97a3281`) and its aggregate report; also unique session-log names (two sessions in the same second used to share a log).
- **Learned:** all 4 players found the photo → Mira trigger, but the reveal showed in only 2: both misses happened on day 3, with no next morning left. Journal off didn't block the reveal. The blue ribbon was never found. Players' theories lean toward "grief" and "purgatory", a darker read than the cozy tone intends.
- **Why:** To see whether the mystery works for both kinds of player, with and without the journal.

## 2026-11-02 · Designer playtest 2: a softer midnight and a clearer screen
- **Built:** a warning before the last action of the night ("The clock will strike twelve soon."), a lead-in line when the day runs out, a fade line after the chime, a wake-up thought from the second morning ("Something isn't right. What happened last night, and why?"; "Again? …" on day 3), bold for key lines in the terminal. Every screen now reads time → place → room → what happened → who's here → what you carry → journal → "What do you do?", with actions grouped under Go / Look / Show and separator lines between turns and sections; the "You could examine" and "Exits" lines are gone (the menu already shows them).
- **Learned:** my own run caught what 15 agent runs didn't: my last action cut straight to midnight with no warning, the screen repeated the menu, and the reading order made the key text hard to find. I also found the blue ribbon, which no AI player did. A shorter journal (only new lines each turn) is parked as a later idea: it adds a free action and changes the agent's journal-on condition.
- **Why:** Playing it myself, waking up again made me ask "What happened, and why?", and I wanted to keep going to understand it and find another way out. But midnight felt like a sharp cut after my last action, there were too many options for two actions per phase, and the screen was hard to read. A proper end-of-day flow, a line from "you" on waking, and a clearer, leaner screen keep the curiosity without the confusion.

## 2026-11-02 · Screen fixes found while recording the GIF
- **Built:** a one-line exit when a character walks away as time moves on ("Mira slips away, her scarf trailing behind her."; "The innkeeper says goodnight and heads up to bed."), and the reveal now shows the place and room before Mira's line, with a break before the end question. Plus `docs/reveal.tape`, a scripted vhs recording of the reveal path.
- **Learned:** recording the reveal showed two glitches no test or report had flagged: Mira spoke, then "Nobody else is here." in the same screen, and the reveal had no place header. An agent had noticed the first one earlier ("Everyone has suddenly vanished") but nobody acted on its note.
- **Why:** A character who vanishes mid-conversation feels like a bug, not a mystery, so people should leave with a line. The reveal is the most important moment in the game, so players need to know where they are when Mira remembers.

## 2026-11-03 · Correction: door-note recount
- **Correction:** a recount from the reports found that the door-note numbers in the fix 2 and fix 3 entries also counted "front door" mentions. Counting only notes about the clock's door or the star, fix 2 went 4 → 9 and fix 3 went 2 → 0 (curious) and 4 → 0 (escape); the direction of each result holds.

## 2026-11-04 · Next-phase plan: Mira reacts, then remembers
- **Built:** a revised AI plan in the README and CLAUDE.md §11: step 1, Mira reacts to shown items through an LLM under `world.json` rules; step 2, if she was by the clock at midnight, she adds a fragment of what you showed her to her pie line. A "Tell Mira" action was considered and parked.
- **Learned:** 105 reachable situations can still be written by hand, so "AI is required" doesn't hold in a game this small; what grows past hand-writing is player history across days. Generated lines must stay the same for the same situation, or they hide the repeated lines that reveal the loop.
- **Why:** I want players to feel the world remembers them, not that an AI is clever, so Mira remembering what you showed her makes the memory rule something you discover through your own actions. I'd rather make a claim I can measure than a big one: hand-written lines grow with every case, and the model doesn't. Doing it in two steps gives me enough lines to test and fix in step 1 before trusting the model with the reveal in step 2.

## 2026-11-09 · UI mock in Figma: 16:9 full screen
- **Built:** a Figma mock with tokens, text styles and components; all play states, title, the four midnight steps, the end screen and a phone frame at 16:9 full screen (painting full bleed, a 300px bottom panel with story left and actions right). `docs/ui-handoff.md` now points to Figma and records the settled behaviour (warning above the actions, speech only in the speech box, italic inner thought, leaving line after Continue, 1.5 s reveal pause, a scrawl on the envelope); CLAUDE.md §10 is now the UI section; the art list is 18 assets at 2560×1440 with the bottom third kept plain.
- **Learned:** the engine already holds what the screens need (the wake-up thought is its own field, the speech split is in `display`), but it moves time on in the same step as the last action, so "Continue" needs the web layer to keep the old scene until the player clicks.
- **Why:** (waiting for designer's words)

## 2026-11-09 · Art: 19 assets in one style, checked in the scene
- **Built:** all 19 MVP art assets in `web/art/`, made with Gemini from one style block and two character sheets: the innkeeper and Mira, the Lobby by day and by night, the Guest Room, the Garden, the pie and the bell with the guest book on the desk, the ribbon on the bush, six item cards, the midnight clock and the title. Each was cut out of a green background, sized, and checked by placing it in the room with the characters. `web/layout.json` now holds the characters' standing spots (Mira mirrored in the Garden, toward the gate) and the desk and bush objects; `docs/art-prompts.md` keeps every prompt; the art guides are redrawn from the layout. `world.json` text now matches the art: the Lobby has a rug, a desk and a snowy window instead of armchairs and a fire, Mira leans on the desk, and you take one of a stack of notices so the painted one can stay.
- **Learned:** checking each asset in the scene caught what looking at it alone didn't. The first standing spots put the characters' feet on the back wall, so they looked like giants standing on the desk; sizing them to the room's eye level fixed it with no new art. Gemini kept painting objects from too high (the pie, the guest book) and ignored "move this" requests and layout images, but followed numbers ("the top is one fifth as tall as it is wide") and two-step edits. The art also exposed text that described things nobody painted, and a clue that stayed on the desk after you took it.
- **Why:** A playtest with a friend showed the plain terminal is too hard to read: it takes a lot of cognitive load, and players may lose interest during the second run, which is exactly when the mystery needs them. One style block and two character sheets keep every asset looking like the same game, even when most of them are made in separate sessions; there may be a better way to automate this. I kept the characters at natural size to leave space for text during the MVP; that may change depending on playtest feedback. Where the text and the art disagreed, I changed the text: it's quicker and simpler, especially when those details don't affect the key story.
