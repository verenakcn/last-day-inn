"""Draw clean composition guides (no text) from web/layout.json at 2560x1440. Pure Python, no Pillow."""
import json, struct, sys, zlib

layout = json.load(open(sys.argv[1]))
out_dir = sys.argv[2]
DW, DH = layout["design_size"]
S = 1.6
W, H = int(DW * S), int(DH * S)

WHITE, BAND, FIG, BOX, LINE, DASH = (255, 255, 255), (217, 217, 217), (138, 143, 156), (242, 242, 242), (154, 160, 174), (122, 53, 21)


def draw(room):
    px = bytearray(bytes(WHITE) * (W * H))

    def put(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            px[i:i + 3] = bytes(c)

    def rect(x1, y1, x2, y2, c):
        x1, x2 = max(0, int(x1)), min(W, int(x2))
        row = bytes(c) * (x2 - x1)
        for y in range(max(0, int(y1)), min(H, int(y2))):
            i = (y * W + x1) * 3
            px[i:i + len(row)] = row

    def dashed_rect(x1, y1, x2, y2, c, t=3, on=13, off=10):
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
        for x in range(x1, x2):
            if (x - x1) % (on + off) < on:
                for k in range(t):
                    put(x, y1 + k, c); put(x, y2 - 1 - k, c)
        for y in range(y1, y2):
            if (y - y1) % (on + off) < on:
                for k in range(t):
                    put(x1 + k, y, c); put(x2 - 1 - k, y, c)

    rect(0, (DH - layout["panel_height"]) * S, W, H, BAND)  # bottom third, covered by the panel
    spots = layout["rooms"][room]["spots"].values()
    if spots:  # feet line: characters stand on the floor in the foreground, below the panel top
        feet_y = max(s["feet_y"] for s in spots)
        for x in range(W):
            if x % 32 < 19:
                for k in range(3):
                    put(x, int(feet_y * S) - 1 + k, DASH)
    for x1, y1, x2, y2 in [v for k, v in layout["overlay_zones"].items() if not k.startswith("_")]:
        dashed_rect(x1 * S, y1 * S, x2 * S, y2 * S, LINE)

    fw, sb = layout["figure_width"], layout["speech_box"]
    for spot in layout["rooms"][room]["spots"].values():
        cx, feet, h = spot["center_x"], spot["feet_y"], spot["height"]
        top = feet - h
        x0 = cx - fw / 2
        sx = x0 - sb["gap"] - sb["width"] if spot["speech"] == "left" else x0 + fw + sb["gap"]
        rect(sx * S, sb["top"] * S, (sx + sb["width"]) * S, (sb["top"] + 170) * S, BOX)
        dashed_rect(sx * S, sb["top"] * S, (sx + sb["width"]) * S, (sb["top"] + 170) * S, LINE)
        # body: rect with a rounded top (radius 70)
        bx1, bx2, by1, by2, r = x0 * S, (x0 + fw) * S, (top + 88) * S, feet * S, 70 * S
        for y in range(int(by1), int(by2)):
            dy = min(r, max(0, by1 + r - y))
            inset = r - (r * r - dy * dy) ** 0.5 if dy else 0
            rect(bx1 + inset, y, bx2 - inset, y + 1, FIG)
        # head: ellipse 84x96
        hcx, hcy, rx, ry = cx * S, (top + 48) * S, 42 * S, 48 * S
        for y in range(int(hcy - ry), int(hcy + ry) + 1):
            d = 1 - ((y - hcy) / ry) ** 2
            if d > 0:
                half = rx * d ** 0.5
                rect(hcx - half, y, hcx + half, y + 1, FIG)

    raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open("%s/guide_%s.png" % (out_dir, room), "wb").write(png)


for room in layout["rooms"]:
    draw(room)
    print("wrote guide_%s.png" % room)
