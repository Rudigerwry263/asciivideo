"""charvid demo - a character/terminal animation that mirrors the reference:
black canvas, phosphor-green glyphs, ASCII creatures, loading bar, symbol
grid, restrained one-idea-per-scene pacing with hard cuts.

    python examples/demo.py            # -> examples/demo.mp4
    python examples/demo.py out.mp4 fps=20   # quick preview
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from charvid import Movie, palette as P

W, H, FS = 1080, 1440, 46


def build():
    m = Movie(width=W, height=H, fps=30, font_size=FS, glow_radius=11, glow_gain=1.0)
    c = m._make_canvas()
    CX, CY = c.cols / 2.0, c.rows / 2.0

    # ---- Scene 1 : boot + loading -----------------------------------------
    s = m.scene(4.0)
    s.particles(count=26, colors=[P.GREEN_DIM, P.GREEN], speed=0.5, start=0, dur=4)
    s.text("user@cli:~$ play charvid", col=2, row=1, color=P.GREEN,
           anim_in="type", in_dur=1.2, start=0.1, dur=3.9, glow=0.9)
    s.text("> initializing character engine", col=2, row=3, color=P.GRAY,
           anim_in="type", in_dur=1.0, start=1.3, dur=2.7, glow=0.5)
    s.loadbar(width=12, cx=CX, cy=CY, label="Loading", start=1.6, dur=2.2,
              fill_color=P.GREEN, label_color=P.WHITE, anim_in="fade", in_dur=0.3)
    s.text("SYSTEM READY", cx=CX, cy=CY + 2.5, color=P.ORANGE,
           anim_in="scramble", in_dur=0.8, start=3.0, dur=1.0, glow=1.0)

    # ---- Scene 2 : a creature made of characters --------------------------
    s = m.scene(3.6)
    s.border(symbol="|§|", color=P.GREEN_DIM, glow=0.55, start=0, dur=3.6,
             in_dur=1.0, anim_out="fade", out_dur=0.4)
    s.text("creatures/", col=3, row=2, color=P.GRAY, anim_in="type",
           in_dur=0.6, start=0.2, dur=3.4, glow=0.5)
    s.sprite("bunny", cx=CX, cy=CY - 0.5, color=P.WHITE, idle="blink",
             anim_in="scatter", in_dur=1.3, start=0.3, dur=3.0,
             anim_out="scatter", out_dur=0.4, glow=1.0)
    s.text("just arrange the symbols", cx=CX, cy=c.rows - 3, color=P.GREEN,
           anim_in="fade", in_dur=0.6, start=1.6, dur=1.8, glow=0.9)

    # ---- Scene 3 : another creature, idle motion --------------------------
    s = m.scene(3.4)
    s.particles(count=18, region=(2, 2, c.cols - 2, c.rows - 2),
                colors=[P.GREEN, P.BLUE], speed=0.4, start=0, dur=3.4)
    s.sprite("frog_big", cx=CX, cy=CY, color=P.GREEN, idle="blink",
             blink_every=1.8, anim_in="scatter", in_dur=1.1, start=0.2,
             dur=2.9, anim_out="fade", out_dur=0.3, glow=1.0)
    s.text("alive, but restrained", cx=CX, cy=c.rows - 3, color=P.WHITE,
           anim_in="fade", in_dur=0.6, start=1.4, dur=1.7, glow=0.8)

    # ---- Scene 4 : the logo, built from keyboard symbols ------------------
    s = m.scene(3.6)
    s.banner("CHAR", cx=CX, cy=CY - 2.6, color=P.WHITE, anim_in="scatter",
             in_dur=1.2, start=0.2, dur=3.2, glow=1.0)
    s.banner("VIDEO", cx=CX, cy=CY + 3.2, color=P.ORANGE, anim_in="scatter",
             in_dur=1.2, start=0.7, dur=2.7, glow=1.0, anim_out="dissolve",
             out_dur=0.5)
    s.border(symbol="+--", color=P.GREEN_DIM, glow=0.5, start=0.0, dur=3.6,
             in_dur=1.4)

    # ---- Scene 5 : dense symbol grid (system / structure) -----------------
    s = m.scene(3.4)
    s.text("system/structure", col=3, row=2, color=P.GRAY, anim_in="type",
           in_dur=0.6, start=0.2, dur=3.2, glow=0.5)
    s.symgrid(cols_n=11, rows_n=15, cx=CX, cy=CY + 0.5, color=P.ORANGE,
              symbols="§|<>/\\_=", anim_in="scramble", in_dur=1.4, start=0.2,
              dur=2.9, anim_out="fade", out_dur=0.3, glow=0.9)

    # ---- Scene 6 : outro --------------------------------------------------
    s = m.scene(4.0)
    s.particles(count=22, colors=[P.GREEN_DIM, P.GREEN, P.WHITE], speed=0.45,
                start=0, dur=4)
    s.sprite("turtle", cx=CX, cy=CY - 1.5, color=P.GREEN, idle="bob",
             anim_in="scatter", in_dur=1.2, start=0.2, dur=3.6, glow=1.0)
    s.timer(from_s=8, cx=CX, cy=CY + 2.5, color=P.ORANGE, start=0.5, dur=3.3,
            anim_in="fade", in_dur=0.4, glow=0.9)
    s.text("made of characters", cx=CX, cy=c.rows - 3, color=P.WHITE,
           anim_in="scramble", in_dur=0.8, start=1.2, dur=2.6, glow=0.9)
    return m


if __name__ == "__main__":
    out = "examples/demo.mp4"
    kw = {}
    for a in sys.argv[1:]:
        if "=" in a:
            k, v = a.split("=", 1)
            kw[k] = int(v) if v.isdigit() else v
        else:
            out = a
    build().render(out, **kw)
