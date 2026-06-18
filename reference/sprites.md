# Figures: pick one, or draw your own

There are **two ways** to get a character-art figure on screen. Choose by how
confident you are at drawing ASCII art.

## A. Pick from the built-in library (easiest)

78 sprites across 5 categories, each with a name + 中文 description. Just:

```python
s.sprite("dog")                      # by name
s.sprite("cat", idle="blink")        # faces with eyes can blink
```

**Browse to choose:**
- Visual grid of every sprite → **[gallery.png](gallery.png)**
- Name + 描述 + ASCII for each → **[gallery.md](gallery.md)**
- Programmatically: `sprites.names_by_category()`, `sprites.info("dog")`,
  `sprites.categories()`.

**Categories:** `animal` (36) · `face` (9) · `object` (19) · `nature` (6) ·
`tech` (8). Examples by category:

| cat | names |
|---|---|
| animal | bunny cat dog puppy kitten bear panda pig mouse fox penguin duck cow sheep monkey koala lion whale dolphin octopus crab snake butterfly bee dino hedgehog elephant bat owl bird snail turtle frog frog_big fish fish_school |
| face | person wave smiley cool alien2 ghost robot robot2 skull |
| object | star heart coffee tree flower house car boat rocket gift crown bulb sword snowman mushroom camera laptop mail balloon |
| nature | sun moon cloud rain mountain wave_sea |
| tech | bug9 folder terminal wifi battery atom cube code |

Sprites with eyes ship a **blink** frame (see the `(blink)` tag in gallery.md);
enable with `idle="blink"` and tune `blink_every=2.6`.

## B. Draw your own (free-form — for capable models)

`custom_sprite` takes any multi-line ASCII art. This is how an AI invents a
**new** figure on the spot — no library entry needed:

```python
s.custom_sprite(r'''
   .--.
  |o_o |
  |:_/ |
 //   \ \
(|     | )
''', color=P.WHITE, anim_in="scatter", idle="bob")
```

Add a `blink` frame (alternate art, usually just the eye row changed) so a
self-drawn creature can blink too:

```python
s.custom_sprite(
    art=r'''
 (o_o)
<(   )>
 / \
''',
    blink=r'''
 (-_-)
<(   )>
 / \
''',
    idle="blink", color=P.ORANGE)
```

Register a figure once and reuse it by name across scenes:

```python
from charvid import sprites
sprites.register("mascot", art="...", blink="...", cat="custom", desc="吉祥物")
s.sprite("mascot", idle="blink")
```

### ASCII authoring rules (so it renders cleanly)

1. **Pure ASCII** glyphs only: letters, digits, `( ) [ ] { } < > / \ | _ - = ^
   ~ . , ' " : ; @ # * +`. Avoid box-drawing / emoji (font-dependent).
2. **Leading spaces are significant** — they position glyphs. Keep the shape
   left-aligned to column 0; the engine centers the whole block.
3. **Keep it small**: ≤ 6 rows tall, ≤ ~14 columns wide reads best on a
   vertical 1080×1440 grid (≈ 34 cols). Bigger art crowds the frame.
4. **Eyes on their own row** make blink frames trivial: copy the art and
   swap the eye characters (`o o` → `- -`, `@,@` → `-,-`).
5. **Triple-quoted strings**: a single leading/trailing blank line is trimmed
   automatically, so you can write `r'''<newline>art<newline>'''`.
6. **Avoid a literal `"""`** inside a `"""..."""` block (use `~~~` or `---`).

## Block-letter banner font

`s.banner("TEXT")` renders 5-row block letters (logos / hero words). Supports
`A-Z 0-9` and `! ? . , : - + / > < * _ [ ]`. Args: `fill="█"` (try `"#"`,
`"▓"`, `"@"`), `gap=1`. Keep words short (~7 letters per line on a 34-col grid).

## Chinese / CJK in figures

CJK is auto-supported (each 汉字 = 2 cells, centered, font fallback). You can
put Chinese inside `custom_sprite` too, but it costs 2 cells per character.

## Glyph coverage

System mono fonts cover ASCII + most box/math symbols. If a glyph renders
blank, swap it or run `python scripts/install_fonts.py`. The block char `█`,
`●` and common punctuation are universally safe.

## Refresh the gallery after adding sprites

```bash
python scripts/gallery.py    # regenerates gallery.png + gallery.md
```
