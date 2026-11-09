# Art asset list (draft)

Assets for the visual web version of The Last Day Inn, to be made with AI image tools. Layout and screens: `docs/ui-handoff.md` and the Figma page **Screens 16:9**.

## Style

**Chosen style:** expressive painterly graphic-novel illustration: faceted gouache with angular planes, pencil hatching and paper texture. Reference image: [art-style-reference.jpg](art-style-reference.jpg) (Lobby, Morning; made with Gemini).

Start every prompt with this block, so assets from different tools and sessions match. It holds only the style; describe the asset after it.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. Cozy winter inn, warm and a little whimsical, never dark or scary. Palette: warm peach-salmon walls, sky blue and white snow, warm timber wood, rust terracotta grandfather clock with a brass pendulum, cornflower blue only for Mira's ribbon. No text, no lettering, no logos.
```

Character details to repeat whenever a character appears:
- **Innkeeper:** older man, kind and tired face, expressive white hair, round wire spectacles, a mustard cable-knit cardigan with buttons over a grey shirt, brown corduroy trousers, dark brown shoes. Unnamed in the game: don't give him a name in prompts.
- **Mira:** an adult woman about 30 (not a child or teenager), lively wavy brown hair, a single cornflower blue ribbon tied at the back of her hair, a bright coral knit scarf, a coral zip jacket over a grey top, dark charcoal trousers, brown boots.

Clothing follows the character intros in `world.json` (cardigan, bright scarf), so what the player reads matches what they see.

Notes on the reference image:
- Mira is an adult here, as she should be: the little girl in the old photo (#14) is Mira as a child, so adult Mira must not look like a child.
- Two clothing details still differ: the innkeeper wears a cable-knit pullover (should be a cardigan), and Mira's scarf is tan (should be bright coral; her coral jacket is fine). Fix these in the character sheets (#1, #2), not here.
- The image has characters and lettering painted in. That is fine for a style reference, but game assets follow the rules below.

## Rules for consistent assets

- **Characters first.** The two reference sheets (#1, #2) are done; use them as references for every image with a character, including the old photo.
- **Describe the style, don't name it.** No game or artist names in prompts, so the art stays original.
- **No text in images.** The closing notice and the inscription are added in code. The envelope shows an unreadable handwritten scrawl where a name would be (the player is never named), painted into the art.
- **Rooms are empty.** Characters move between rooms by time of day (CLAUDE.md §4), so they are separate transparent images. So are things that appear and disappear: the pie and the ribbon.
- **One daytime painting per room.** Evening and night are colour tints in code. Only the Lobby gets a night painting, because its lamps are lit.
- **The bottom third is covered.** On desktop a 300px panel covers the lowest third of every room painting (y 600–900 at 1600×900). Keep it open floor or ground with nothing important in it; on a phone it shows, so it should still look finished.
- **Standing spots.** Characters stand in the foreground on that open floor, so on desktop the panel hides their legs. They are sized so their eyes sit at the room's eye level (paint rooms from a standing adult's eye level). Keep clear space beside each one for the speech box. Spots and speech sides are recorded in `web/layout.json` (changed 2026-11-09: feet just above the panel made them look like giants on the back wall).
- **Composition guides** in [art-guides/](art-guides/), one per room, drawn from `web/layout.json`:
  - `guide_<room>.png` (2560×1440, no text): attach it to the room prompt as a layout reference.
  - `guide_<room>_labelled.png`: the same layout with notes, for you.

  Grey band = bottom third, open floor where characters stand. Grey figures = where characters will stand (paint the room empty). Light boxes = speech space, keep plain. Dashed boxes top left and right = interface over the painting, keep low detail. Add to the prompt: *"Use the attached layout image only for composition: keep the lower third as plain floor, leave the marked areas uncluttered, and paint the room empty with no people. Do not copy its shapes, colours or lines."* If you move a standing spot, update `web/layout.json` and redraw the clean guides with `python3 docs/art-guides/make_guides.py web/layout.json docs/art-guides`. The labelled versions come from Figma (page Screens 16:9, frames "Guide / …") and still show the old spots until those frames are updated.
- **Licence and source.** Check each tool's terms for public use, and note the tool and prompt for every asset in `web/art/SOURCES.md`.

## Files

Folder `web/art/`, PNG, file names exactly as below. Rooms and the title are full screen, so make them 2560×1440 (16:9).

## MVP list (19 assets)

### Characters

| # | Asset | File | Size | Background | Notes | Status |
|---|---|---|---|---|---|---|
| 1 | Innkeeper reference sheet | `ref_innkeeper.png` | 2048×1024 | plain | Front, ¾ and side views. Clean the red and yellow specks from the edges. | done |
| 2 | Mira reference sheet | `ref_mira.png` | 2048×1024 | plain | Same views. Clean the specks. | done |
| 3 | Innkeeper in scene | `npc_innkeeper.png` | ~800×1200 | transparent | Full body, standing, turned toward Mira (right). Shown about 610px tall at 1600×900, legs under the panel on desktop. | done |
| 4 | Mira in scene | `npc_mira.png` | ~800×1200 | transparent | Full body, standing, turned toward the innkeeper (left; mirrored from the original). Used in the Lobby and the Garden. | done |

### Rooms (empty, no people)

| # | Asset | File | Size | Background | Notes | Status |
|---|---|---|---|---|---|---|
| 5 | Lobby, day | `room_lobby_day.png` | 2560×1440 | full | Grandfather clock as the hero object, snowy window, reception desk, front door, rug. Two standing spots, each with speech space. Upscaled with plain resizing; replace with an AI upscale if one is available. | done |
| 6 | Lobby, night | `room_lobby_night.png` | 2560×1440 | full | Same framing as #5, lamps lit, soft deep blue outside. Must line up with #5 (checked: no shift, only small redrawn-line differences). Mira may stand here alone at night; her figure needs a light night tint of its own. Upscaled with plain resizing. | done |
| 7 | Guest Room | `room_guest.png` | 2560×1440 | full | Bed, bedside drawer, door, window showing the snowy garden. Nobody stands here. Time of day by tint only, no night painting (checked 2026-11-09). Upscaled with plain resizing. | done |
| 8 | Garden | `room_garden.png` | 2560×1440 | full | Snowy garden, locked back gate, flowerpot, a bush. One standing spot (Mira) with speech space. Gate fixed (closed, lock plate). The pot by the gate still sits under the desktop panel, so the visible pots at the back count as "the flowerpot" (fully visible on phones). Time of day by tint only. Upscaled with plain resizing. | done |

### Things that appear and disappear (placed on rooms)

| # | Asset | File | Size | Background | Notes | Status |
|---|---|---|---|---|---|---|
| 9 | Pie on the desk | `scene_pie.png` | 400×212 | transparent | Lobby, Evening only. Version 2 (apple and cranberry, low side view, cream dish) so it reads against the desk and matches its angle. Shown 90px wide on the desk between the two characters (spot in `web/layout.json`). | done |
| 10 | Ribbon caught on the bush | `scene_ribbon.png` | 253×280 | transparent | Garden, until picked up. Shown 100px wide on the upper branches of the bare bush (spot in `web/layout.json`); readable by day and at night. | done |
| 19 | Bell and guest book on the desk | `scene_desk_items.png` | 400×104 | transparent | Lobby, all day, right end of the desk. Matches the desk text in `world.json`. Added 2026-11-09. Flattened to 75% height to match the desk's low angle; shown 130px wide (spot in `web/layout.json`). | done |

### Item cards (shown large when shown to someone, and as 40px thumbnails on the Show buttons)

| # | Asset | File | Size | Background | Notes | Status |
|---|---|---|---|---|---|---|
| 11 | Sealed envelope | `item_note.png` | 512×512 | transparent | An unreadable handwritten scrawl where a name would be. Shows the flap side with the scrawl on it; reads as an envelope at 40px. | done |
| 12 | Closing notice | `item_closing_notice.png` | 512×512 | transparent | Blank framed paper card; text added in code. Nearly square with a laurel border and a pin hole (transparent); the blank centre is about 300×300 at 512. | done |
| 13 | Torn blue ribbon | `item_ribbon.png` | 512×512 | transparent | Same blue as Mira's ribbon (faded, like the Garden scrap). Torn at both ends. | done |
| 14 | Old photo | `item_old_photo.png` | 512×512 | transparent | Faded photo: a younger innkeeper and a little girl with a blue ribbon beside the clock. Use #1 and #2 as references. The girl closely resembles Mira; the ribbon is visible at full size but tiny at 40px. | done |
| 15 | Clock inscription | `item_inscription.png` | 512×512 | transparent | Close-up of the clock's carved base with a blank plaque; text added in code. The panel is dark rust wood, so the inscription needs light or engraved-looking text. | done |
| 16 | Gate key | `item_gate_key.png` | 512×512 | transparent | Old iron key, with rust and crumbs of frozen soil. Reads at 40px. | done |

### Moments and screens

| # | Asset | File | Size | Background | Notes | Status |
|---|---|---|---|---|---|---|
| 17 | Midnight | `fx_midnight.png` | 1024×1024 | transparent | Clock face at midnight with soft rings spreading out. Strange, not scary. Hands at twelve; has simple Roman numerals. Glow warmed to pale gold after background removal. | done |
| 18 | Title art | `title.png` | 2560×1440 | full | The inn in snow at dusk, warm windows. Empty space for the title, added in code. Also used behind the end screen. Deep blue night sky top left, so the title needs light text. Upscaled with plain resizing. | done |

Icons (clock, check mark, warning, chevron) are drawn in code and need no art.

## Later (not needed for the MVP)

- Cut on 2026-11-09: the note under the door (it is picked up on waking, so never seen on the floor), a pie slice item card (the pie is never carried), and the two neutral portraits (nothing in the layout uses them)
- More expressions: Mira hesitant and knowing; innkeeper sad and nostalgic
- Lobby, Evening painting
- Paper texture for the interface
- Sound: clock chime, wind
