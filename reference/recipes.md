# Scene recipes

Copy-paste starting points. All assume:

```python
from charvid import Movie, palette as P
m = Movie(width=1080, height=1440, fps=30, font_size=46)
c = m._make_canvas(); CX, CY = c.cols/2, c.rows/2
```

Render with `m.render("out.mp4")`. Sizes below are for the vertical 1080x1440
social format; for 1920x1080 landscape use `font_size=40` (grid ~48x27).

## 1. Boot / loading intro

```python
s = m.scene(4.0)
s.particles(count=24, colors=[P.GREEN_DIM, P.GREEN], speed=0.5)
s.text("user@cli:~$ play demo", col=2, row=1, color=P.GREEN, anim_in="type",
       in_dur=1.2)
s.loadbar(width=12, cx=CX, cy=CY, label="Loading", start=1.4, dur=2.2,
          fill_color=P.GREEN, label_color=P.WHITE)
s.text("READY", cx=CX, cy=CY+2.5, color=P.ORANGE, anim_in="scramble",
       start=3.0, dur=1.0)
```

## 2. Mascot reveal (the signature "made of characters" move)

```python
s = m.scene(3.6)
s.border(symbol="|§|", color=P.GREEN_DIM, glow=0.55)
s.text("creatures/", col=3, row=2, color=P.GRAY, anim_in="type", in_dur=0.6)
s.sprite("bunny", cx=CX, cy=CY-0.5, color=P.WHITE, idle="blink",
         anim_in="scatter", in_dur=1.3, anim_out="scatter", out_dur=0.4)
s.text("just arrange the symbols", cx=CX, cy=c.rows-3, color=P.GREEN,
       anim_in="fade", start=1.6, dur=1.8)
```

## 3. Logo lock-up

```python
s = m.scene(3.6)
s.banner("CHAR",  cx=CX, cy=CY-2.6, color=P.WHITE,  anim_in="scatter", in_dur=1.2)
s.banner("VIDEO", cx=CX, cy=CY+3.2, color=P.ORANGE, anim_in="scatter",
         in_dur=1.2, start=0.7, anim_out="dissolve", out_dur=0.5)
s.border(symbol="+--", color=P.GREEN_DIM, glow=0.5, in_dur=1.4)
```

## 4. Data hook (big number)

```python
s = m.scene(3.5)
s.text("downloads/", col=3, row=2, color=P.GRAY, anim_in="type")
s.banner("100K", cx=CX, cy=CY, color=P.ORANGE, anim_in="scramble", in_dur=1.0)
s.text("and counting", cx=CX, cy=CY+5, color=P.WHITE, anim_in="fade", start=1.2)
```

(For a live count-up, use a `timer`, or animate by splitting into scenes.)

## 5. System / structure texture

```python
s = m.scene(3.4)
s.text("system/structure", col=3, row=2, color=P.GRAY, anim_in="type")
s.symgrid(cols_n=11, rows_n=15, cx=CX, cy=CY+0.5, color=P.ORANGE,
          symbols="§|<>/\\_=", anim_in="scramble", in_dur=1.4,
          anim_out="fade", out_dur=0.3)
```

## 6. Outro with timer + caption

```python
s = m.scene(4.0)
s.particles(count=22, colors=[P.GREEN_DIM, P.GREEN, P.WHITE], speed=0.45)
s.sprite("turtle", cx=CX, cy=CY-1.5, color=P.GREEN, idle="bob",
         anim_in="scatter", in_dur=1.2)
s.timer(from_s=8, cx=CX, cy=CY+2.5, color=P.ORANGE, start=0.5, dur=3.3)
s.text("made of characters", cx=CX, cy=c.rows-3, color=P.WHITE,
       anim_in="scramble", start=1.2, dur=2.6)
```

## 7. Clock animation

```python
s = m.scene(4.0)
s.text("system/clock", col=2, row=2, color=P.GRAY, anim_in="type")
s.clock(radius=5, cx=CX, cy=CY-0.5, period=3.0, color=P.GREEN,
        hand_color=P.ORANGE, start=0.2, dur=3.5)          # period = s per turn
s.timer(from_s=0, cx=CX, cy=CY+5, color=P.ORANGE, start=0.4, dur=3.3)
```

## 8. Chinese title (CJK auto-fallback)

```python
m = Movie(width=1080, height=1440, fps=30, font_size=50)  # CJK works as-is
s = m.scene(4.5)
s.text("gorden@cli:~$ ./run", col=2, row=2, color=P.GREEN, anim_in="type")
s.text("命令行风格视频", cx=CX, cy=CY, color=P.WHITE, anim_in="scatter",
       in_dur=1.5, glow=1.1)                              # each 汉字 = 2 cells
s.text("=" * 18, cx=CX, cy=CY+2, color=P.GREEN, anim_in="wipe")
```

A 7-character Chinese title spans 14 cells. On a 34-col grid (`font_size=50`)
it sits centered with margin. For longer Chinese lines, raise `font_size`
(fewer, bigger cells) or split across rows with `"\n"`.

## Pacing cheatsheet

| Goal | Scene length | Pattern |
|---|---|---|
| Social hook (TikTok/Reels) | 12-20s total, 6-10 scenes | fast cuts, one subject each |
| Logo sting | 3-5s | scatter-in banner + border draw-on + hold |
| Explainer beat | 4-6s per scene | eyebrow + subject + caption |
| Ambient loop | match `start`/`dur` to total; end where you began | particles + idle motion |

## Tips

- **Aspect ratios**: `1080x1440` (4:5 social), `1080x1920` (9:16 story),
  `1920x1080` (landscape). Always even numbers.
- **Density**: smaller `font_size` -> more cells -> finer art; larger -> bolder.
- **Determinism**: every render of the same script is byte-identical. Change
  `Movie(seed=...)` to reshuffle particle / scatter layouts.
- **One accent color per scene.** Green is the bed; white is the hero; orange
  is the single highlight. Resist rainbows.
