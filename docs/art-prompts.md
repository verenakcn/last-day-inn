# Art prompts for the remaining assets (#7–#18)

Copy-paste prompts for Gemini (or the "Last Day Inn Art" Gem). The asset list is [art-asset-list.md](art-asset-list.md); this file only holds the prompts. Bring the results back for a check before marking them done.

## How to use

- **One asset per message.** Start a new chat per group (rooms, scene objects, items, moments) and re-attach the references.
- **Attach what each prompt names.** "Style ref" is `docs/art-style-reference.jpg`. "Lobby" is `web/art/room_lobby_day.png`, the approved room the others must match.
- **Transparent assets:** Gemini can't make transparency. Every transparent asset is generated on a flat green background; remove it afterwards and check the edges for a green fringe.
- **Fixes:** "Keep everything the same, change only …" instead of regenerating.
- **Afterwards:** save under the exact file name in `web/art/`, and add a line to `web/art/SOURCES.md` (tool, date, prompt).

Every prompt starts with the style block from the asset list. It is written out in full here so each prompt can be copied on its own.

---

## Rooms

### #7 Guest Room → `room_guest.png`

Attach: style ref, Lobby, `docs/art-guides/guide_guest_room.png`.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. Cozy winter inn, warm and a little whimsical, never dark or scary. No text, no lettering, no logos.

Asset #7: the guest's small bedroom at the same inn, as an empty room background for a game. Match the attached Lobby exactly in style, line weight, colours and eye level: it is the same building.

The room: a small room under the eaves with a sloping ceiling. A bed with a heavy patchwork quilt, a small wooden bedside table with a drawer, a plain wooden door to the hallway, a radiator under a small frosted window that looks down on a snowy garden. Warm peach-salmon walls and warm timber like the Lobby.

Composition (use the attached layout image only for composition: keep the lower third as plain floor, leave the marked areas uncluttered, and paint the room empty with no people; do not copy its shapes, colours or lines):
- Painted from the eye level of a standing adult, matching the Lobby.
- The bed, bedside drawer, door and window all sit in the upper two thirds of the image, clearly visible.
- The lower third is plain wooden floor, perhaps the edge of a small rug, with nothing important in it.
- The top-left and top-right corners stay low in detail (interface sits there).

Light: soft, even morning daylight from the window with no strong colour cast (other times of day are added later as colour tints).

No people, no text. Wide image, 16:9.
```

Check: empty; the drawer, door and window are clearly readable; nothing important in the lower third; it feels like the same inn as the Lobby.

### #8 Garden → `room_garden.png`

Attach: style ref, Lobby, `docs/art-guides/guide_garden.png`, `web/art/npc_mira.png` (for scale only).

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. Cozy winter inn, warm and a little whimsical, never dark or scary. No text, no lettering, no logos.

Asset #8: the inn's walled back garden in winter, as an empty background for a game. Match the attached Lobby in style, line weight and colour warmth: it is the same inn.

The garden: a small walled garden asleep under snow. A tall hedge and an old brick wall, a few stubborn bushes, terracotta flowerpots, and an iron back gate set in the hedge, closed and locked. Sky blue and white snow, warm terracotta pots, dark iron.

Composition (use the attached layout image only for composition: keep the lower third as plain snowy ground, leave the marked areas uncluttered, and paint the scene empty with no people; do not copy its shapes, colours or lines):
- Painted from the eye level of a standing adult, matching the Lobby.
- Right side: the iron back gate in the hedge, with one terracotta flowerpot on the ground beside it.
- Left side: a thorny, bare bush at about chest height, clearly visible (a ribbon will be added to it later, so leave its branches uncluttered).
- Centre: open snowy ground where one person will stand (the attached figure shows her size; do not paint her). The light box to the right of the grey figure stays plain hedge or sky with no objects.
- The lower third is plain snowy ground with nothing important in it.
- The top-left and top-right corners stay low in detail (interface sits there).

Light: soft, even winter daylight with no strong colour cast (evening and night are added later as colour tints).

No people, no text. Wide image, 16:9.
```

Check: the gate, the flowerpot and the bush all read clearly above the lower third; nothing in the speech box area; the snow isn't pure flat white (the hatching and texture should carry across it).

---

## Scene objects (placed on rooms)

### #9 Pie on the desk → `scene_pie.png`

Attach: style ref, Lobby, and the first pie (as "what to change").

First version (2026-11-09) was seen from too high and blended into the warm wall and desk. Version 2:

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. No text, no lettering, no logos.

Asset #9: a single object to place on the reception desk in the attached Lobby. A whole homemade apple and cranberry pie, still warm, in a simple cream ceramic pie dish with a thin rust-red band around the rim.

Angle: seen from the side, from just above table height, the same low view as the desk in the attached Lobby. The top of the pie is only a thin, flat oval, about one fifth as tall as it is wide, so the lattice is seen at a shallow angle. The side of the dish is clearly visible.

Colour, so it stands out against a warm peach wall and a brown wooden desk: a deep golden-brown lattice crust with crisp dark pencil outlines; glossy deep crimson cranberries and filling showing through the gaps in the lattice and bubbling a little at the edge; a few whole cranberries on top. A faint wisp of pale steam. No green garnish.

One object only, nothing else: no desk, no table, no plate under the dish, no cast shadow. Soft, even light with no strong colour cast. Flat, plain solid green background with no texture, so it can be removed cleanly. Wide image, about 2:1.
```

Check: the top reads as a thin oval like the desk top; the crimson is visible at 90px wide; no green on the pie itself (it would be cut out with the background).

### #10 Ribbon caught on the bush → `scene_ribbon.png`

Attach: style ref, `web/art/room_garden.png` (once approved), `web/art/ref_mira.png` (for the ribbon colour).

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. No text, no lettering, no logos.

Asset #10: a small torn scrap of cornflower blue ribbon caught on a short thorny twig, to place on the bush in the attached Garden. The ribbon is the same blue as the ribbon in the attached character's hair, slightly faded by many winters but still clearly blue, with one torn, frayed end, fluttering a little. The twig matches the bush in the Garden painting.

One object only: the ribbon and the short twig, nothing else, no snow, no cast shadow. Soft, even light. Flat, plain solid green background with no texture, so it can be removed cleanly. Square image.
```

Check: clearly the same blue as Mira's ribbon (it's a clue); visible against the snow; the twig blends with the painted bush.

---

## Item cards (512×512, shown large and as 40px thumbnails)

All six use the same framing so they look like a set: one object, centred, seen straight on or slightly from above, filling about 80% of the square, on flat green.

### #11 Sealed envelope → `item_note.png`

Attach: style ref.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #11: an item card for a game. A sealed cream paper envelope, a little creased and soft at the corners, as if it has been kept somewhere for a long time. On the front, a short handwritten scrawl in dark ink where a name would be, loose and completely unreadable (not real letters or words). Seen straight on, centred, filling about 80% of the image.

One object only, no cast shadow, soft even light. Flat, plain solid green background with no texture, so it can be removed cleanly. Square image.
```

Check: the scrawl must not form readable letters (the player is never named); it still reads as an envelope at 40px.

### #12 Closing notice → `item_closing_notice.png`

Attach: style ref.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #12: an item card for a game. A neat sheet of good cream paper in portrait orientation, with a thin printed decorative border, a small pin hole at the top, and a completely blank centre (text will be added later in code, so leave the inside empty and evenly lit). Seen straight on, flat, not tilted, centred, filling about 80% of the image.

One object only, no writing, no letters, no cast shadow, soft even light. Flat, plain solid green background with no texture, so it can be removed cleanly. Square image.
```

Check: no writing at all; the blank area is flat and even enough for text on top.

### #13 Torn blue ribbon → `item_ribbon.png`

Attach: style ref, `web/art/ref_mira.png`, and `scene_ribbon.png` if done.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #13: an item card for a game. A short length of torn cornflower blue satin ribbon, the same blue as the ribbon in the attached character's hair, slightly faded by many winters but still clearly blue, with one torn, frayed end. Lying in a loose curl, seen from slightly above, centred, filling about 80% of the image.

One object only, no twig, no snow, no cast shadow, soft even light. Flat, plain solid green background with no texture, so it can be removed cleanly. Square image.
```

Check: the same blue as Mira's ribbon and the garden scrap.

### #14 Old photo → `item_old_photo.png`

Attach: style ref, `web/art/ref_innkeeper.png`, `web/art/ref_mira.png`, Lobby (for the clock).

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #14: an item card for a game. An old photograph with a white border and soft, worn corners, slightly faded and warm-toned with age, but the colours still visible. In the photo, standing beside the grandfather clock from the attached Lobby:
- the innkeeper from the attached sheet, about 25 years younger: hair still mostly dark with a little grey, the same kind face and round wire spectacles, a knit cardigan;
- a little girl of about seven with lively wavy brown hair and a single cornflower blue ribbon in her hair, smiling, one hand on the clock case.
They look happy and close, like family. The girl should share the hair colour and ribbon of the attached adult woman, but do not make her an exact miniature of her.

The photo seen straight on, centred, filling about 80% of the image. No cast shadow. Flat, plain solid green background with no texture, so it can be removed cleanly. Square image.
```

Check: the ribbon is still visibly blue despite the fading; the clock is recognisable; the younger innkeeper is clearly him; the girl only hints at Mira (players should infer it, not be told).

### #15 Clock inscription → `item_inscription.png`

Attach: style ref, Lobby.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #15: an item card for a game. A close-up of the carved wooden base of the grandfather clock from the attached Lobby (same rust-brown polished wood): a decorative carved frame around a smooth, completely blank panel in the centre (words will be added later in code, so the panel stays empty and evenly lit). Seen straight on, centred, filling about 80% of the image.

No letters or words anywhere, no cast shadow, soft even light. Flat, plain solid green background around the carving, with no texture, so it can be removed cleanly. Square image.
```

Check: the panel is blank and flat; the wood matches the Lobby clock.

### #16 Gate key → `item_gate_key.png`

Attach: style ref, `web/art/room_garden.png` (once approved, for the iron of the gate).

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #16: an item card for a game. A small old iron key with a simple round bow and a plain bit, a little rust and a few crumbs of frozen soil on it, as if it had been kept under a flowerpot. It matches the iron of the gate in the attached Garden. Lying at a slight diagonal, seen from slightly above, centred, filling about 80% of the image.

One object only, no cast shadow, soft even light. Flat, plain solid green background with no texture, so it can be removed cleanly. Square image.
```

Check: reads as a key at 40px.

---

## Moments and screens

### #17 Midnight → `fx_midnight.png`

Attach: style ref, Lobby (for the clock face), `room_lobby_night.png`.

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture.

Asset #17: the moment of midnight, for a full-screen transition in a cozy mystery game. The cream face of the grandfather clock from the attached Lobby, seen straight on, centred, with both hands pointing straight up to twelve. Simple painted hour marks only, no numbers. Soft rings of pale gold light spread outward from the clock face in gentle, slightly uneven painted circles, as if the chime were visible. Strange and quietly magical, never scary.

Only the clock face and the rings, nothing else. Flat, plain solid green background with no texture, so it can be removed cleanly (keep the rings clearly lighter than the background). Square image.
```

Check: both hands exactly at twelve; no numerals; the rings survive background removal (if they don't, generate the rings on dark navy instead and we'll use a blend mode in code).

### #18 Title art → `title.png`

Attach: style ref, Lobby, `room_lobby_night.png` (for the evening mood).

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. Cozy winter inn, warm and a little whimsical, never dark or scary. No text, no lettering, no logos.

Asset #18: the title image for the game, also used behind the end screen. A small, old two-storey country inn seen from outside at dusk, deep in snow: steep roof with eaves and a small window under them, warm golden light in the windows, smoke curling from the chimney, a hanging inn sign that is completely blank, a snowy lane leading to the door, a hedge and a glimpse of a walled garden at the side. A soft deep blue sky with the first stars and gently falling snow. It should feel like the last evening of something loved.

Composition: the inn in the lower right two thirds; the upper left area is calm, empty sky with little detail, where the title will be added later in code. Painted from a standing adult's eye level.

No people, no text, nothing written on the sign. Wide image, 16:9.
```

Check: the sign is blank; the sky area top left is calm enough for a large title; it reads as cozy, not spooky.

---

### #19 Bell and guest book on the desk → `scene_desk_items.png`

Added 2026-11-09 so the desk matches its text in `world.json` ("A brass bell, the guest book…"). It is a separate object on the desk, like the pie, so both Lobby paintings stay as they are and stay aligned. It shows all day, at the right end of the desk.

Attach: style ref, Lobby, `web/art/scene_pie.png` (for the low angle).

```text
Expressive painterly graphic novel illustration in a dynamic faceted gouache style: angular geometric planes, textured pencil sketch hatching marks, vivid hand-painted gouache layers, rich paper texture. No text, no lettering, no logos.

Asset #19: two small objects side by side, to place on the reception desk in the attached Lobby: on the left, a polished brass service bell that gleams; on the right, a thick old guest book lying open, cream pages filled with faint, unreadable pencil scribbles (no real letters or words), a ribbon bookmark, and a fountain pen resting across it.

Angle: seen from the side, from just above table height, the same low view as the attached pie and the desk in the Lobby. Tops are thin, flat shapes; the side of the book's cover is visible.

Colour, so they stand out against a warm peach wall and a brown wooden desk: bright warm brass with crisp highlights; a deep burgundy leather cover with worn edges; cream pages.

Only the bell, the book and the pen, nothing else: no desk, no table, no cast shadow. Soft, even light with no strong colour cast. No green on the objects. Flat, plain solid green background with no texture, so it can be removed cleanly. Wide image, about 2:1.
```

Check: the angle matches the pie; nothing readable on the pages; both read at about 140px wide for the pair.

## Text and art that don't match yet

The painted Lobby differs from the room text in `world.json`. Decide which to change before players see both:

- ~~`locations.lobby`: "worn armchairs, a crackling fire"~~ Fixed 2026-11-09: the Lobby text and Mira's two armchair lines now match the painting (rug, desk, snowy window; Mira at the desk).
- `reception_desk`: "a brass bell, the guest book". Being added as a desk object (#19). The painted notice staying after it's taken is fixed in the text: the player takes one of a stack of copies (2026-11-09).
- `grandfather_clock`: "polished walnut". The painted clock is a reddish rust-brown, which is close enough unless you want it exact.
