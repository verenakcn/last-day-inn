# The Last Day Inn: UI handoff

Use this when building the visual web version of the game.

**Priority:** `CLAUDE.md` and `world.json` win over this document on story, rules and text. This document covers how the game looks and how the screens behave. If they disagree, stop and ask the designer.

**Design reference: Figma** (a private file kept by the designer). Build from the page **Screens 16:9**. The **Components** page holds the buttons, name tag and speech box; text styles and colour variables match `web/tokens.css`. The page **Screens** (800px column) and the earlier claude.ai canvas are kept for comparison only.

## Layout

Desktop: 16:9, full screen. Designed at 1600×900 and scaled to fit the window; letterbox in the panel colour if the window isn't 16:9.

1. **Painting**, full bleed, with the time-of-day light over it. Characters stand in the foreground on the floor, sized to the room's eye level; on desktop the panel hides their legs (changed 2026-11-09 from feet just above the panel, which made them look like giants on the back wall). Name tags sit on the character just above the panel line (y about 570 in the 1600×900 frame), so they stay visible on desktop; speech box beside the speaker. The Figma frames still show the old spots and need updating.
2. **Over the painting:** clock with time and actions left, and the place name, top left; Journal button top right.
3. **Bottom panel**, 300px tall, paper colour, a rust line on top. Padding 24px top and bottom, 48px left and right, 48px between the two columns:
   - **Story column (left):** story text up to 640px wide, about 6 lines. Longer moments scroll inside it. The **"You know:" strip** sits at its bottom, only while the player holds the clock inscription.
   - **Action column (right, 736px):** the **warning** (`ui.midnight_soon`) sits at the top, only before the last action of the night. Under it: Go 124px, Look 252px in two columns, Show the remaining width in two columns, 16px apart. Buttons are at least 48px tall and may wrap to two lines. **Continue** replaces the actions, bottom right.

The real menu needs up to 2 Go, 4 Look and 6 Show entries (fullest case: Lobby, Evening); it fits the panel, with the warning too. See "Fullest action menu (Lobby, Evening)".

Phone frame 390×844: top bar with clock, place, time and Journal; scene 390×219 (the whole painting, so the bottom third that the desktop panel covers shows here); spoken line under the scene; story; Go and Look side by side; Show below. Longer turns scroll.

Other screens on **Screens 16:9**: title, the four midnight steps, the end screen, and the phone.

## Tokens

Use `web/tokens.css`.

- Literata for story, Figtree for interface, Patrick Hand for the journal only.
- Sizes, desktop: title 64/72, place on scene 32/40, story 21/34, inner thought 21/34 italic, room description 19/31, speech 19/28 bold, journal 23/32, action 17/20, small interface 15/20, labels 13/16 in caps.
- Sizes, phone: story 19/31, inner thought 19/31 italic, room description 18/29, journal 21/30.
- **Four kinds of text look different:** room description (smaller, soft ink), narration (story size, ink), the player's inner thought (italic, no quote marks; the `thought` field, e.g. the wake-up question), and speech (bold, only in the speech box, never in the story area).
- Nothing below 14px, except the 13px caps labels.
- Smallest click area 44px.
- Cornflower is for Mira's ribbon in the art only, never in the interface.

Scene light: a multiply layer over the same painting, using the `--light-*` tokens. The Lobby at Night uses `room_lobby_night.png` (see `docs/art-asset-list.md`).

## Behaviour

- **Show:** click a carried item, and it appears large over the scene with its content (the note's line, the notice's text, what the photo shows). The Show column swaps to the people in the room, with Cancel beside the heading. Clicking a person plays the response and costs one action. Cancel costs nothing.
- **Clock inscription:** it can be shown, so it appears in the Show list as well as under "You know:". It resets at midnight like other items; the journal keeps the fact.
- **Hidden sections:** hide any section with nothing in it. Show is hidden when nobody else is present or the player has nothing to show.
- **✓ marks** come from the engine, on Go, Look and Show actions already taken that day. In Show, the ✓ belongs on the person, for that item.
- **Spoken lines** appear in a speech box beside the speaker, with a small arrow pointing back at the speaker's face, in Literata 19/28 bold, and stay until the next action. The other character is slightly muted. Narration stays in the story area. The box takes about 130 characters. Use `display.speech` and `display.narration` from `world.json`; Mira's first-meeting lines are already split (`lines`).
- **Positions:** where each character stands in each room, and which side their speech box opens, live in `web/layout.json` (presentation only, not story). A spot with `"flip": true` shows the figure mirrored (Mira in the Garden faces right, toward the gate).
- **New items** (2026-11-10, designer playtest): when the player finds or picks up something (the envelope on waking, the photo, the notice, the inscription, the ribbon, the key), it appears large in the centre of the scene with what it says or shows, and a "Keep it" button. The "It reads / It shows" line is not repeated in the story panel, so the clue can't get lost in the text.
- **Your things:** a bag button beside the Journal opens a list of everything carried or known, each with its picture and content; tapping one shows it large. A red dot marks a new item.
- **Journal** is the lowest priority element. The button shows a red dot when a fact is added (was "New note" until 2026-11-10). It opens from the top-right corner, sized to its notes, with no dimming, and scrolls if taller than the screen. Opening it costs nothing. It splits into "From before you woke" and "Today" after the first reset. It must disappear when the journal is turned off for testing.
- **Clock:** four quarters, one per time of day, with two marks each. The hand reaches the top at midnight.
- **When an action ends a time of day:** keep the scene, people, place and time as they were, and show the reply with "No actions left". Replace the actions with Continue. Clicking Continue updates the time, clock, light, people and actions together. This means characters never vanish mid-sentence, and the player can't choose an action based on someone who has left. A character's leaving line ("The innkeeper says goodnight and heads up to bed.") shows just after Continue, as the first line of the new time of day. See "Last action of a time of day".
- **Midnight:** four steps, each moved on by Continue: (1) the painting dims and the lead-in line shows in the panel; (2) MIDNIGHT, full screen; (3) the clock at twelve with the chime line; (4) the fade line over a pale wash, then the next morning. Use the right scene from `loops.midnight_scenes`: `in_lobby`, `elsewhere` or `escaped` (`escaped` has no lead-in, so it starts at step 2). The frames show `in_lobby`.
- **Reveal:** Mira's line appears in the speech box: "Morning…", a pause of 1.5 seconds, then the rest in the same box. Keep the pause length as one setting in the web layer so it can be tuned later. The game then ends: replace the actions with Continue, which leads to the end screen.
- **The note's envelope** shows an unreadable handwritten scrawl where a name would be. The player is never named.
- **Text input:** the end screen only.
- **Never show** Day or Loop numbers.

## Build notes

- Keep all story text in `world.json`. Keep rules in `engine.py`. The web layer shows what the engine reports.
- `observe()` returns one block of plain text. The web page needs the same facts as separate fields: time, actions left, place, room text, story lines, people, carried items, known items, journal sections, warning, and grouped actions. Add this without changing `observe()`, because the playtest agent depends on it.
- Run `test_engine.py` and `test_agent.py` after engine changes.
- `**…**` in `world.json` marks bold key lines.

## Settled decisions (2026-11-09)

- **Speech:** `world.json` keeps `text` for the terminal and the playtest agent, and adds `display.speech` / `display.narration` for the web; `test_engine.py` checks the two agree. The wording is a draft for the designer to review.
- **Scope:** `CLAUDE.md` §10 now covers the UI; graphics are in scope.
- **Reference:** Figma, page **Screens 16:9**.

## Art and text

- Art files and names: `docs/art-asset-list.md`. Files go in `web/art/`.
- `web/art/ref_innkeeper.png` and `web/art/ref_mira.png` are the designer's character sheets. Clean faint red and yellow specks from cut-out edges, because they show on dark screens.
- The bottom panel covers the lowest third of each room painting on desktop: keep it plain floor or ground, open enough for the characters to stand on. Leave clear space beside each character for the speech box.
- Mock text comes from `world.json`, except these samples: the title tagline, the Evening and Night story lines, and the journal-open story line. Always use `world.json` in the build.
