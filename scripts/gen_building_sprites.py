"""Generate original Kairosoft-inspired isometric building sprites for CarbonSim.

Authored procedurally (no third-party / Kairosoft assets) so the set is
license-clean and reproducible. Outputs 64x64 RGBA PNGs into web/assets/
to the Building Sprite Spec in docs/design-language.md:
  - 64x64 canvas, transparent bg
  - shared 64x32 isometric footprint centred at (32, 46) so every sprite
    aligns on the isocity grid (ground + structures use the same offset)
  - palette = Sprint-1 tokens; 1px dark-warm outline; top-left light

Run:  python scripts/gen_building_sprites.py
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw

SIZE = 64
CX, BY = 32, 46          # footprint centre
FOOT_W = 56              # default footprint width (<=64 to leave outline room)
OUT = (58, 47, 34, 255)  # dark warm outline (~ --bevel-shadow)

ASSETS = os.path.join(os.path.dirname(__file__), "..", "web", "assets")
SPRITES = os.path.join(ASSETS, "sprites")
TILES = os.path.join(ASSETS, "tiles")

# Sprint-1 palette
GRASS = (126, 200, 80)
GRASS_D = (78, 155, 58)
WALL_DIRTY = (170, 156, 130)
WALL_CLEAN = (232, 220, 192)
AZURE = (31, 147, 199)
GREEN = (76, 175, 80)
RED = (226, 85, 63)
ORANGE = (245, 166, 35)
SMOKE = (74, 64, 54)
SILO = (200, 190, 170)


def shade(c, f):
    return tuple(max(0, min(255, int(x * f))) for x in c[:3]) + (255,)


def new():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def P(pt):
    return (int(round(pt[0])), int(round(pt[1])))


def diamond(cx, cy, w):
    hw, hh = w / 2, w / 4
    return [P((cx - hw, cy)), P((cx, cy - hh)), P((cx + hw, cy)), P((cx, cy + hh))]


def cuboid(d, cx, by, fw, h, wall):
    """Draw an isometric box; base diamond centred at (cx,by), height h up."""
    hw, hh = fw / 2, fw / 4
    Bl, Bt, Br, Bb = (cx - hw, by), (cx, by - hh), (cx + hw, by), (cx, by + hh)
    Tl, Tt, Tr, Tb = (cx - hw, by - h), (cx, by - hh - h), (cx + hw, by - h), (cx, by + hh - h)
    top, left, right = shade(wall, 1.18), shade(wall, 0.96), shade(wall, 0.74)
    d.polygon([P(Bl), P(Bb), P(Tb), P(Tl)], fill=left, outline=OUT)
    d.polygon([P(Bb), P(Br), P(Tr), P(Tb)], fill=right, outline=OUT)
    d.polygon([P(Tl), P(Tt), P(Tr), P(Tb)], fill=top, outline=OUT)
    return {"Tl": Tl, "Tt": Tt, "Tr": Tr, "Tb": Tb, "topcx": cx, "topcy": by - hh / 1 - h}


def stack(d, x, top_y, h, w, body, tip):
    """A simple smokestack/chimney (vertical bar)."""
    d.rectangle([P((x - w / 2, top_y - h)), P((x + w / 2, top_y))], fill=shade(body, 1.0), outline=OUT)
    d.rectangle([P((x - w / 2, top_y - h)), P((x + w / 2, top_y - h + 3))], fill=tip, outline=OUT)


def silo(d, x, base_y, h, w, col):
    d.rectangle([P((x - w / 2, base_y - h)), P((x + w / 2, base_y))], fill=shade(col, 0.9), outline=OUT)
    d.ellipse([P((x - w / 2, base_y - h - w / 3)), P((x + w / 2, base_y - h + w / 3))],
              fill=shade(col, 1.1), outline=OUT)


def roof_panel(d, top, col):
    """Small panel (solar/green) on the top face for 'clean' variants."""
    cx, cy = top["topcx"], int((top["Tt"][1] + top["Tb"][1]) / 2)
    d.polygon([P((cx - 8, cy)), P((cx, cy - 4)), P((cx + 8, cy)), P((cx, cy + 4))],
              fill=col, outline=OUT)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def make_ground():
    img = new()
    d = ImageDraw.Draw(img)
    d.polygon(diamond(CX, BY, 60), fill=GRASS, outline=shade(GRASS_D, 0.8))
    # a couple of darker grass speckles
    for sx, sy in [(24, 44), (40, 48), (32, 40)]:
        d.point((sx, sy), fill=GRASS_D)
    return img


def make_building(sector, clean):
    img = new()
    d = ImageDraw.Draw(img)
    d.polygon(diamond(CX, BY, 60), fill=GRASS, outline=shade(GRASS_D, 0.8))
    wall = WALL_CLEAN if clean else WALL_DIRTY
    if sector == "thermal":
        top = cuboid(d, CX, BY, FOOT_W, 18, wall)
        stack(d, 24, BY - 18, 22, 7, SMOKE, (GREEN + (255,)) if clean else (SMOKE[0]+10, SMOKE[1], SMOKE[2], 255))
        stack(d, 40, BY - 18, 16, 6, SMOKE, (GREEN + (255,)) if clean else (40, 35, 30, 255))
        if clean:
            roof_panel(d, top, AZURE + (255,))
    elif sector == "steel":
        top = cuboid(d, CX, BY, FOOT_W, 24, wall)
        # furnace chimney with hot tip (dirty) / cool tip (clean)
        stack(d, 38, BY - 24, 26, 8, (120, 110, 100), (AZURE + (255,)) if clean else (ORANGE + (255,)))
        # glow door
        d.rectangle([P((26, BY - 6)), P((33, BY + 2))],
                    fill=(AZURE + (255,)) if clean else (ORANGE + (255,)), outline=OUT)
    elif sector == "cement":
        cuboid(d, CX, BY, FOOT_W - 8, 14, wall)
        silo(d, 22, BY - 2, 26, 12, SILO if not clean else shade(SILO, 1.12)[:3])
        silo(d, 40, BY - 4, 22, 11, SILO if not clean else shade(SILO, 1.12)[:3])
        if clean:
            d.line([P((16, BY - 28)), P((28, BY - 28))], fill=GREEN + (255,), width=2)
    else:  # generic
        top = cuboid(d, CX, BY, FOOT_W, 20, wall)
        d.rectangle([P((28, BY - 6)), P((36, BY + 2))], fill=shade(wall, 0.6), outline=OUT)
        if clean:
            roof_panel(d, top, GREEN + (255,))
    return img


def make_smog():
    img = new()
    d = ImageDraw.Draw(img)
    for (x, y, r, a) in [(28, 18, 11, 90), (40, 14, 9, 80), (22, 22, 8, 70), (46, 22, 7, 70)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 110, 100, a))
    return img


def make_player_marker():
    img = new()
    d = ImageDraw.Draw(img)
    # cheerful pin/flag near the top
    d.line([P((32, 4)), P((32, 22))], fill=OUT, width=2)
    d.polygon([P((32, 4)), P((50, 9)), P((32, 14))], fill=GREEN + (255,), outline=OUT)
    return img


def make_district():
    img = new()
    d = ImageDraw.Draw(img)
    d.polygon(diamond(CX, BY, 60), fill=GRASS, outline=shade(GRASS_D, 0.8))
    cuboid(d, 24, BY + 2, 26, 12, WALL_DIRTY)
    cuboid(d, 42, BY - 2, 24, 16, WALL_CLEAN)
    cuboid(d, 33, BY + 6, 22, 10, WALL_DIRTY)
    return img


def make_tree():
    img = new()
    d = ImageDraw.Draw(img)
    d.rectangle([P((30, BY - 6)), P((34, BY + 2))], fill=(120, 84, 50, 255), outline=OUT)
    d.ellipse([P((22, BY - 24)), P((42, BY - 4))], fill=GRASS_D + (255,), outline=OUT)
    d.ellipse([P((25, BY - 22)), P((39, BY - 10))], fill=GRASS + (255,))
    return img


def main():
    written = []
    written.append(save(make_ground(), os.path.join(TILES, "ground.png")))
    for sector in ("thermal", "steel", "cement", "generic"):
        written.append(save(make_building(sector, False),
                            os.path.join(SPRITES, f"bldg_{sector}_dirty.png")))
        written.append(save(make_building(sector, True),
                            os.path.join(SPRITES, f"bldg_{sector}_clean.png")))
    written.append(save(make_smog(), os.path.join(SPRITES, "smog.png")))
    written.append(save(make_player_marker(), os.path.join(SPRITES, "player_marker.png")))
    written.append(save(make_district(), os.path.join(SPRITES, "district.png")))
    written.append(save(make_tree(), os.path.join(SPRITES, "decor_tree.png")))
    for p in written:
        print("wrote", os.path.relpath(p, os.path.join(os.path.dirname(__file__), "..")))


if __name__ == "__main__":
    main()
