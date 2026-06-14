# Research Brief: Kairosoft Visual Style for CarbonSim

**Date:** 2026-06-14
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** Understand Kairosoft's graphic style thoroughly to improve CarbonSim's isometric city renderer (`web/js/isocity.js`) and design system; include concrete, reproducible visual specs.

---

## Synthesis

Kairosoft's look is a recognizable, much-imitated **cute pixel-art tycoon** style — bright/saturated palette, chibi (super-deformed) characters, chunky outlined buildings on a tile grid, and constant lively feedback (floating coins, reaction emotes, pop-up bubbles). It's enough of a "thing" that artists sell "Kairosoft-style" sprite commissions referencing *Game Dev Story*/*Dream House Days* ([pixeljoint thread](https://pixeljoint.com/forum/forum_posts.asp?TID=17047)). Hard, numeric specs are **not published** by Kairosoft; the detailed conventions below are informed inference from the widely-seen style and standard pixel-art practice, flagged as such.

A key, decision-forcing finding: **Kairosoft games are predominantly a 3/4 oblique / dimetric top-down view, not a true 2:1 isometric diamond.** Buildings and characters are drawn near-front-facing with a slight diagonal so faces and signage read clearly; oblique needs only ~3 sprite sets (side mirrored, front, back) and "tend[s] to be simpler" than side-scrollers ([cxong, perspectives](https://cxong.github.io/2022/03/how-many-sprites-do-different-perspectives-need)). CarbonSim currently renders a **true isometric** scene (`web/js/isocity.js`, 2:1 diamond, `TILE_W=64`/`TILE_H=32`), so matching Kairosoft means either shifting projection toward oblique or — cheaper — keeping iso but adopting Kairosoft's *sprite style, palette, characters, and feedback juice*, which is where the visual gap actually is.

[NOTE] CarbonSim's current palette is a **muted retro-earth** scheme (cream `#f7f1e7`, teal `#3b6f76`, per `web/css/style.css`) and its sprites are plain flat 64×64 tiles with **no people, no animation, no floating feedback** — the opposite of Kairosoft's bright, busy, character-driven charm. The biggest wins are therefore palette brightening, character/citizen sprites, and game-feel feedback, not the projection math.

---

## Domain

### Discovery
- [cxong — "How many sprites do different perspectives need?"](https://cxong.github.io/2022/03/how-many-sprites-do-different-perspectives-need) — perspective taxonomy (oblique vs top-down vs iso) and sprite-count implications.
- [Pixel Joint — "[PAID] Isometric Kairosoft Style Sprites"](https://pixeljoint.com/forum/forum_posts.asp?TID=17047) — confirms "Kairosoft style" is a recognized, commissioned look; reference titles *Game Dev Story*, *Dream House Days*.
- [The Kairosoft Wiki](https://kairosoft.wiki.gg/) and [Game Dev Story — Wikipedia](https://en.wikipedia.org/wiki/Game_Dev_Story) — studio/catalog context (Game Dev Story, Venture Towns, Dungeon Village, Dream House Days, etc.).

### Verification
- **Verified:** Oblique 3/4 view "can show off characters and scenery well … feeling natural to move around in," needs ~3 sprite sets, and is "simpler" than side-scrollers ([cxong](https://cxong.github.io/2022/03/how-many-sprites-do-different-perspectives-need)). Top-down needs only 1 set but "can't show off their face" (ibid).
- **Verified (existence of style):** "Kairosoft style" is a discrete, requestable aesthetic referencing Game Dev Story / Dream House Days ([pixeljoint](https://pixeljoint.com/forum/forum_posts.asp?TID=17047)).
- **Flagged / sparse:** No source gives Kairosoft's exact palette, tile dimensions, or outline rules. The fetched pages describe the style via images, not numbers. Detailed specs below are **informed inference**, not documented fact.

### Comparison (projection options to "get there")
| Option | Pros | Cons |
|---|---|---|
| **Keep true isometric** (current) + restyle sprites/palette | No renderer math change; reuse `isocity.js` projection & plot system | Slightly less "Kairosoft," whose buildings read more front-facing |
| **Shift to 3/4 oblique / dimetric** (true Kairosoft) | Most authentic; faces/signage read; fewer sprite sets ([cxong]) | Rewrite `tileToScreen` + redraw all sprites in oblique |
| **Hybrid: oblique-leaning tiles in the iso grid** | Cheaper than full reprojection; buildings drawn front-ish on iso ground | Mild visual inconsistency |

### Synthesis
The authentic Kairosoft hallmark is **3/4 oblique**, but the *felt* gap for CarbonSim is the **art content and juice**, not the grid. Recommended: keep the existing iso plot system and invest in (a) brighter saturated palette, (b) characterful outlined building sprites with variety, (c) animated chibi citizens/workers, (d) floating feedback (coins/emotes/popups), (e) Kairosoft-style rounded UI chrome. Treat full oblique reprojection as optional/later.

### Confidence
Medium — perspective taxonomy is well-sourced; the detailed Kairosoft aesthetic is widely recognizable but not numerically documented, so specifics are inference.

## Codebase

### Discovery
- `web/js/isocity.js` — current renderer: **true isometric** `tileToScreen` (2:1 diamond), `TILE_W=64`, `TILE_H=32`, `GRID_SIZE=6`, `MAX_PLOTS=16`; blits 64×64 PNG sprites; smog/compliance tint; pixel-style particle bursts; ResizeObserver; reduced-motion fallback.
- `web/assets/` — flat 64×64 sprites: `tiles/ground.png`, `sprites/{factory_dirty,factory_clean,smog,player_marker,district}.png`; font `PressStart2P-Regular.ttf`; `manifest.json` + `web/js/assets.js` loader.
- `web/css/style.css` — retro tycoon tokens: `--bg:#f7f1e7`, `--accent:#3b6f76`, `--green:#5a8f4e`, beveled panels; `@font-face` Press Start 2P.
- `docs/design-language.md` — the design system doc to update.

### Verification
- Observed directly in-repo (this session): projection is isometric not oblique; sprites are static, no character/citizen sprites, no floating feedback emotes; palette is muted-earth. These are facts from the current files, not inference.

### Comparison (current vs Kairosoft target)
| Element | CarbonSim now | Kairosoft target | Gap |
|---|---|---|---|
| Projection | True iso 2:1 diamond | 3/4 oblique/dimetric [inferred] | Optional reproject |
| Palette | Muted retro-earth | Bright, saturated, cheerful | Brighten/retune |
| Buildings | Plain flat 64² tiles | Outlined, characterful, varied | Re-art |
| Characters | None | Chibi citizens/workers, animated | Add |
| Feedback juice | Particle bursts only | Floating coins/emotes/pop-ups | Add |
| UI chrome | Beveled retro panels + Press Start 2P | Rounded gradient panels, cute icons, notification bubbles, rounded pixel font | Restyle |

### Synthesis
`isocity.js`'s plot/loop/lifecycle, the `AssetLoader`/manifest pipeline, and `effects.js` particle system are all reusable. To get to Kairosoft: add a richer sprite set (buildings + animated citizens) via the existing manifest, retune `style.css` tokens brighter, add a floating-feedback layer (extend `effects.js`/`isocity.js` triggers), and update `docs/design-language.md`. The renderer can stay isometric initially.

### Confidence
High — grounded in direct reading of the current repo files.

## Sources
- [cxong — How many sprites do different perspectives need?](https://cxong.github.io/2022/03/how-many-sprites-do-different-perspectives-need) — practitioner write-up; perspective/sprite specs.
- [Pixel Joint — Isometric Kairosoft Style Sprites (commission thread)](https://pixeljoint.com/forum/forum_posts.asp?TID=17047) — evidence the style is a recognized target; reference titles.
- [The Kairosoft Wiki](https://kairosoft.wiki.gg/) — studio/catalog context.
- [Game Dev Story — Wikipedia](https://en.wikipedia.org/wiki/Game_Dev_Story) — Kairosoft's flagship title; release/context.
- In-repo (observed): `web/js/isocity.js`, `web/assets/manifest.json`, `web/css/style.css`, `docs/design-language.md`.
