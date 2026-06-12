#!/usr/bin/env python3
"""Generate retro isometric placeholder assets for CarbonSim Online.

These assets are intentionally simple, deterministic, and released as CC0
so the repo can ship a working asset pipeline without depending on external
pack downloads during build. They are designed to be replaced by vetted
free+attribution packs in a future pass if desired.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).parent.parent / "web" / "assets"
TILE_W, TILE_H = 64, 64

# Retro tycoon palette
COLORS = {
    "ground_top": (120, 180, 90),
    "ground_left": (80, 140, 60),
    "ground_right": (60, 110, 45),
    "ground_edge": (40, 80, 30),
    "factory_wall": (160, 160, 150),
    "factory_wall_dark": (120, 120, 115),
    "factory_roof": (140, 140, 135),
    "factory_window": (70, 80, 90),
    "smoke_dark": (60, 60, 60),
    "smoke_light": (120, 120, 120),
    "clean_accent": (80, 180, 160),
    "clean_roof": (100, 200, 180),
    "marker": (255, 215, 0),
    "marker_dark": (200, 160, 0),
}


def new_tile() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (TILE_W, TILE_H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def iso_diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, w: int, h: int,
                top: tuple[int, int, int], left: tuple[int, int, int],
                right: tuple[int, int, int], outline: tuple[int, int, int] | None = None) -> None:
    """Draw a 2:1 isometric diamond centered at (cx, cy)."""
    half_w = w // 2
    half_h = h // 2
    top_p = (cx, cy - half_h)
    right_p = (cx + half_w, cy)
    bottom_p = (cx, cy + half_h)
    left_p = (cx - half_w, cy)
    # Top face
    draw.polygon([top_p, right_p, bottom_p, left_p], fill=top, outline=outline)
    # Left face (pseudo-depth)
    draw.polygon([left_p, bottom_p, (bottom_p[0], bottom_p[1] + half_h // 2),
                  (left_p[0], left_p[1] + half_h // 2)], fill=left, outline=outline)
    # Right face
    draw.polygon([right_p, bottom_p, (bottom_p[0], bottom_p[1] + half_h // 2),
                  (right_p[0], right_p[1] + half_h // 2)], fill=right, outline=outline)


def draw_ground() -> Image.Image:
    img, draw = new_tile()
    cx, cy = TILE_W // 2, TILE_H // 2 + 6
    iso_diamond(draw, cx, cy, 56, 28,
                COLORS["ground_top"], COLORS["ground_left"],
                COLORS["ground_right"], COLORS["ground_edge"])
    # Add a little path/grass detail
    draw.rectangle([cx - 8, cy - 2, cx + 8, cy + 2], fill=(100, 160, 75))
    return img


def draw_factory(dirty: bool = True) -> Image.Image:
    img, draw = new_tile()
    cx, cy = TILE_W // 2, TILE_H // 2 + 4
    base_y = cy + 4

    # Building footprint on ground diamond
    iso_diamond(draw, cx, cy, 56, 28,
                COLORS["ground_top"], COLORS["ground_left"],
                COLORS["ground_right"], COLORS["ground_edge"])

    wall = COLORS["factory_wall"] if dirty else (180, 190, 185)
    wall_dark = COLORS["factory_wall_dark"] if dirty else (140, 150, 145)
    roof = COLORS["factory_roof"] if dirty else COLORS["clean_roof"]
    accent = COLORS["factory_window"] if dirty else COLORS["clean_accent"]

    # Main building block (isometric box)
    bw, bh = 32, 24
    bx, by = cx - bw // 2, base_y - bh
    # Left face
    draw.polygon([(bx, by), (bx, by + bh), (cx - 2, base_y), (cx - 2, base_y - bh)],
                 fill=wall_dark)
    # Right face
    draw.polygon([(bx + bw, by), (bx + bw, by + bh), (cx + 2, base_y), (cx + 2, base_y - bh)],
                 fill=wall)
    # Roof
    draw.polygon([(bx, by), (bx + bw, by), (cx + 2, base_y - bh), (cx - 2, base_y - bh)],
                 fill=roof)

    # Windows / accents
    draw.rectangle([bx + 6, by + 4, bx + 10, by + 10], fill=accent)
    draw.rectangle([bx + 18, by + 4, bx + 22, by + 10], fill=accent)

    # Smokestacks
    stack_h = 14
    for sx in (bx + 4, bx + bw - 8):
        draw.rectangle([sx, by - stack_h, sx + 4, by], fill=wall_dark)
        # Smoke puffs
        if dirty:
            draw.ellipse([sx - 2, by - stack_h - 5, sx + 6, by - stack_h + 1],
                         fill=COLORS["smoke_dark"])
            draw.ellipse([sx, by - stack_h - 9, sx + 8, by - stack_h - 3],
                         fill=COLORS["smoke_light"])
        else:
            # Clean factory has small clean vapor
            draw.ellipse([sx, by - stack_h - 3, sx + 4, by - stack_h + 1],
                         fill=(200, 230, 240, 120))

    if not dirty:
        # Solar panel / green badge on roof
        draw.rectangle([cx - 6, base_y - bh - 2, cx + 6, base_y - bh + 2],
                       fill=COLORS["clean_accent"])

    return img


def draw_smog() -> Image.Image:
    img, draw = new_tile()
    # Semi-transparent smoke cloud designed to overlay a factory
    for i, (x, y, r, alpha) in enumerate([
        (20, 20, 10, 120),
        (32, 16, 12, 140),
        (44, 22, 9, 110),
        (28, 26, 11, 100),
    ]):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(80, 80, 80, alpha))
    return img


def draw_player_marker() -> Image.Image:
    img, draw = new_tile()
    cx = TILE_W // 2
    # Gold arrow pointing down at the plot
    draw.polygon([(cx, 8), (cx - 10, 22), (cx - 4, 22), (cx - 4, 32),
                  (cx + 4, 32), (cx + 4, 22), (cx + 10, 22)],
                 fill=COLORS["marker"], outline=COLORS["marker_dark"])
    return img


def draw_district() -> Image.Image:
    """Industrial district tile representing aggregated companies."""
    img, draw = new_tile()
    cx, cy = TILE_W // 2, TILE_H // 2 + 4
    iso_diamond(draw, cx, cy, 56, 28,
                COLORS["ground_top"], COLORS["ground_left"],
                COLORS["ground_right"], COLORS["ground_edge"])
    # Cluster of small darker factories
    wall = COLORS["factory_wall_dark"]
    for offset in [(-12, -4), (4, -8), (-4, 4)]:
        bx, by = cx + offset[0], cy + offset[1] - 8
        draw.rectangle([bx - 6, by - 10, bx + 6, by], fill=wall)
        draw.rectangle([bx - 7, by - 12, bx - 3, by - 10], fill=wall)
        draw.rectangle([bx + 2, by - 12, bx + 6, by - 10], fill=wall)
    return img


def main() -> None:
    tiles_dir = ASSETS_DIR / "tiles"
    sprites_dir = ASSETS_DIR / "sprites"
    tiles_dir.mkdir(parents=True, exist_ok=True)
    sprites_dir.mkdir(parents=True, exist_ok=True)

    draw_ground().save(tiles_dir / "ground.png")
    draw_factory(dirty=True).save(sprites_dir / "factory_dirty.png")
    draw_factory(dirty=False).save(sprites_dir / "factory_clean.png")
    draw_smog().save(sprites_dir / "smog.png")
    draw_player_marker().save(sprites_dir / "player_marker.png")
    draw_district().save(sprites_dir / "district.png")

    print("Generated assets:")
    for path in sorted(tiles_dir.iterdir()) + sorted(sprites_dir.iterdir()):
        print(f"  {path.relative_to(ASSETS_DIR.parent)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
