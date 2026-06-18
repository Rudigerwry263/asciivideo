---
name: asciivideo
description: >-
  Generate command-line / terminal-style animated videos built entirely from
  characters - arrange ASCII & keyboard symbols into text, creatures, mascots,
  logos and borders on a black phosphor-glow canvas, then render
  deterministically to MP4. Ships a Python engine (charvid) with a scene
  timeline; element types (block-letter banners, ASCII-art sprites, loading
  bars, particle fields, decorative borders, symbol grids, timers); entrance
  animations (typewriter, scatter-assemble, scramble-decode, wipe, fade,
  slide); idle motion (blink, bob, flicker, drift); a terminal-green / white /
  orange / blue palette; and an ffmpeg renderer. Use when the user asks for an
  ASCII / character / 字符 animation, a terminal or CLI-aesthetic video, kinetic
  ASCII art, a symbol-built logo or mascot, a "code-feel" 代码感 visual, or wants
  to turn text / a figure / a logo into a glowing character-grid animation.
---

# asciivideo

Build **character-art animated videos** with a command-line aesthetic: a black
canvas, glowing monospace glyphs in terminal-green / white / orange / blue, and
figures, logos and text **made out of characters**. One movie = a list of
scenes; each scene = character-art elements with deterministic, restrained
animation. Rendered frame-by-frame to MP4 via ffmpeg.

The look is modeled on Studio Dumbar's OpenAI DevDay "code-feel" system:
**restrained, one-idea-per-scene, hard cuts between black frames**.

## Setup (once)

```bash
python3 -c "import PIL, numpy"   # need Pillow + numpy
which ffmpeg                      # need ffmpeg on PATH
python scripts/install_fonts.py   # OPTIONAL: pin JetBrains Mono for portability
```

Works out of the box with system monospace fonts (SF Mono / Menlo / DejaVu).

**Chinese / CJK is supported automatically.** Latin & symbols use the mono
font; Chinese/Japanese/Korean glyphs are rendered with a CJK fallback font
(auto-detected: Hiragino Sans GB / STHeiti / PingFang / Noto Sans CJK) and
each CJK glyph occupies **2 grid cells**, centered. Override the CJK font with
`Movie(cjk_font="/path/to/SourceHanSans.otf")` or `CHARVID_CJK_FONT=...`. Just
put Chinese straight into `s.text("命令行风格视频", ...)` - no flags needed.

## Quick start

Author a movie as a short Python script, then render:

```python
# run from the repo root, or add the repo root to sys.path
from charvid import Movie, palette as P

m = Movie(width=1080, height=1440, fps=30, font_size=46)   # vertical / social
s = m.scene(4.0)                                           # 4-second scene
s.border(symbol="|§|", color=P.GREEN_DIM, glow=0.55)
s.sprite("bunny", color=P.WHITE, idle="blink", anim_in="scatter", in_dur=1.2)
s.text("just arrange the symbols", cy=20, color=P.GREEN, anim_in="fade",
       start=1.5, dur=2.0)
m.render("out.mp4")
```

```bash
python my_video.py                      # full render
# iterate fast at low fps / quality:
python -c "import my_video"  # or call m.render('p.mp4', fps=15, preset='ultrafast', crf=26)
```

Examples (both render to MP4 beside the script):
- **[`examples/demo.py`](examples/demo.py)** - 6-scene English reference.
- **[`examples/cli_style_video.py`](examples/cli_style_video.py)** - 8-scene
  **Chinese** piece: CLI title 命令行风格视频 -> Made By Gorden -> dog / cat /
  owl / bunny / frog + loading + analog clock + outro. Run with a `.html`
  output to get the HTML version (`examples/cli_style_video.html`).

## Mental model

- **`Movie(width, height, fps, font_size, glow_radius, glow_gain, font)`** -
  the canvas is a *monospace character grid*. `font_size` sets the grid: at
  `1080x1440 / font_size=46` the grid is **37 cols x 23 rows**. Inspect with
  `c = m._make_canvas(); c.cols, c.rows`.
- **`s = m.scene(duration, bg="#000000")`** - scenes play back-to-back with
  **hard cuts**. Keep one main subject per scene.
- **Positioning** (cell coordinates, floats allowed):
  - `col=`, `row=` -> top-left of the block
  - `cx=`, `cy=` -> *center* of the block (use canvas center `c.cols/2, c.rows/2`)
  - neither -> auto-centered on the canvas
- **Timing** (seconds, relative to the scene): `start`, `dur`, `anim_in`,
  `in_dur`, `anim_out`, `out_dur`, `ease_in`, `ease_out`.
- **Color & glow**: `color="#RRGGBB"`, `glow=0..1.5` (phosphor halo), `alpha`.

## Elements (scene builder methods)

| Method | What it makes | Key args |
|---|---|---|
| `s.text(text, ...)` | One or multi-line characters (`"\n"` for rows) | `col/row` or `cx/cy` |
| `s.banner(text, ...)` | BIG 5-row block letters (A-Z 0-9 + punctuation) - logos / hero words | `fill="█"`, `gap=1` |
| `s.sprite(name, ...)` | A built-in ASCII creature/mascot | `idle`, `blink_every` |
| `s.custom_sprite(art, ...)` | Your own multi-line ASCII art (triple-quoted string) | — |
| `s.loadbar(...)` | `Loading NN% [████ ]` that fills over its duration | `width`, `label`, `fill_char`, `fill_dur` |
| `s.particles(...)` | Ambient drifting/twinkling character field | `count`, `chars`, `colors`, `speed`, `region` |
| `s.border(...)` | Decorative frame of repeated symbols, draws on | `symbol="|§|"`, `margin`, `draw_on` |
| `s.symgrid(...)` | Dense block/frame of shimmering keyboard symbols | `cols_n`, `rows_n`, `symbols`, `hollow` |
| `s.clock(...)` | Analog clock: char ring + rotating hands | `radius`, `period` (s/turn), `hand_color` |
| `s.timer(...)` | Digital `MM:SS` counter | `from_s`, `rate`, `prefix` |

### Figures: pick one, or invent one

Two ways to get a character-art figure (see **[reference/sprites.md](reference/sprites.md)**):

1. **Pick from the library (easiest, best for any model)** — 78 built-in
   sprites in 5 categories (`animal` 36 · `face` 9 · `object` 19 · `nature` 6
   · `tech` 8), each with a 中文 description and (for faces) a blink frame:

   ```python
   s.sprite("dog");  s.sprite("cat", idle="blink")
   ```
   Browse to choose: **[reference/gallery.png](reference/gallery.png)** (visual
   grid) and **[reference/gallery.md](reference/gallery.md)** (name + 描述 +
   ASCII). Or query: `sprites.names_by_category()`, `sprites.info("dog")`.
   A few names: `bunny cat dog puppy bear panda fox penguin cow owl octopus
   dino · person smiley cool alien2 robot skull · star heart coffee tree house
   car rocket crown laptop · sun moon cloud mountain · folder terminal wifi
   battery atom code`.

2. **Invent a new one (free-form, for capable models)** — draw any ASCII art
   inline; this is how an AI develops a brand-new figure:

   ```python
   s.custom_sprite(r'''
    (o_o)
   <(   )>
    / \
   ''', blink=r'''
    (-_-)
   <(   )>
    / \
   ''', idle="blink", color=P.ORANGE)
   ```
   Register to reuse by name: `sprites.register("mascot", art="...", blink="...")`.
   ASCII rules (pure-ASCII, ≤6 rows, eyes on their own row for blink) are in
   **[reference/sprites.md](reference/sprites.md)**. Regenerate the gallery with
   `python scripts/gallery.py` after adding sprites.

## Animations

**Entrance** (`anim_in`, with `in_dur`):

| value | effect | best for |
|---|---|---|
| `fade` | opacity ramp | anything (default) |
| `type` | typewriter reveal, reading order | prompts, labels, code lines |
| `scatter` | glyphs fly in from random spots and **assemble** | creatures, logos (signature look) |
| `scramble` | per-cell symbol decode -> resolves (matrix style) | technical labels, "READY", grids |
| `wipe` | row-by-row curtain | blocks, banners |
| `rise` / `drop` / `slide_left` / `slide_right` | translate + fade | captions, eyebrows |
| `none` | instant | borders, backgrounds |

**Exit** (`anim_out`, with `out_dur`): `fade`, `dissolve` (random glyphs
vanish), `scatter` (glyphs fly apart), `none`.

**Idle** (`idle=`, while fully visible): `blink` (sprite eyes), `bob` (gentle
vertical float), `flicker` (alpha jitter). Particles drift automatically.

**Easing** (`ease_in` / `ease_out`): `linear ease_in ease_out ease_out_cubic
ease_in_out_cubic ease_out_quart ease_out_expo ease_out_back ease_out_elastic`.

## Palette (`from charvid import palette as P`)

`P.GREEN` (phosphor primary) · `P.GREEN_DIM` (grids/borders) · `P.WHITE` ·
`P.GRAY` · `P.ORANGE` (accent) · `P.BLUE` · `P.YELLOW` · `P.RED` · `P.CYAN`.
Groups: `P.ACCENTS`, `P.GREENS`. Background is black; everything glows.

## Design rules (what makes it look right)

1. **Restraint.** One main subject per scene. The reference's motion is *简洁克制*
   - a single assemble or blink, not a fireworks show.
2. **Black + glow.** Keep `bg="#000000"`. Glow (`glow_radius`, `glow_gain`)
   is the phosphor CRT signature - don't disable it.
3. **Color discipline.** Green is primary; **white** for the hero subject;
   **orange** for ONE accent (a number, a logo word, a highlight); blue
   sparingly in particles. Don't rainbow.
4. **Hard cuts.** Scenes cut on black. Let elements `fade`/`scatter` out near
   the end of their scene rather than cross-fading scenes.
5. **Eyebrow + caption pattern.** Small `type`-in label top-left
   (`col=3,row=2`, `P.GRAY`), hero subject centered, short caption bottom
   (`cy=c.rows-3`).
6. **Use `scatter` for the wow.** Assembling a creature/logo out of scattered
   floating characters is the strongest move - it literally shows the thing is
   "made of characters". Pair with an ambient `particles()` field.

## Rendering

```python
m.render("out.mp4", fps=30, crf=18, preset="medium")   # final video
m.render("p.mp4",  fps=15, crf=26, preset="ultrafast") # fast preview
m.snap("frame.png", t=2.5)                              # single debug frame
```

### Export to HTML (no video)

The same movie can be exported as a **single self-contained `.html`** that
animates live in the browser via a Canvas-2D runtime (`web/charvid.js`) — same
glow, CJK, sprites and animations, plus play/pause/seek/loop controls.

```python
m.to_html("out.html", title="命令行风格视频")            # one double-clickable file
m.to_html("out.html", controls=False, loop=True)        # kiosk loop, no UI
```

- Same Python script produces both: `m.render("x.mp4")` and `m.to_html("x.html")`.
- Double-click the file to open it (real browsers allow `file://`).
- Controls: Space = play/pause, click canvas or `R` = replay, drag the seek bar,
  toggle loop. Grid metrics are baked into the spec so positions match the video.

Renders are **deterministic** (seeded RNG) - same script -> same MP4. ~0.07s
per 1080x1440 frame. H.264 / yuv420p; use **even** width/height.

## Common recipes

```python
# boot screen
s.text("user@cli:~$ run", col=2, row=1, color=P.GREEN, anim_in="type")
s.loadbar(width=12, cx=CX, cy=CY, fill_color=P.GREEN, label_color=P.WHITE)

# logo lock-up from keyboard symbols
s.banner("CHAR",  cx=CX, cy=CY-3, color=P.WHITE,  anim_in="scatter", in_dur=1.2)
s.banner("VIDEO", cx=CX, cy=CY+3, color=P.ORANGE, anim_in="scatter", in_dur=1.2)

# mascot in a frame
s.border(symbol="|§|", color=P.GREEN_DIM, glow=0.55)
s.sprite("frog_big", color=P.GREEN, idle="blink", anim_in="scatter")

# your own art
s.custom_sprite('''
 ____
( o  )=
 \\__/
''', color=P.WHITE, anim_in="scatter")
```

More patterns (data hooks, mascot intros, social loops):
**[reference/recipes.md](reference/recipes.md)**.

## Troubleshooting

- **Blank glyphs / boxes** -> the font lacks that glyph. Stick to ASCII +
  common box/math symbols, or pass a broader `font=`. CJK needs a CJK mono.
- **Element off-screen** -> check `c.cols/c.rows`; `cy` must be `< rows`.
- **Text unreadable on particles** -> lower particle `count`, or give the
  subject `glow=1.0` and particles `glow=0.5`.
- **`ffmpeg not found`** -> install ffmpeg.
- **Want bigger/smaller grid** -> change `font_size` (smaller font = more
  cells = denser art).
