"""命令行风格视频 - a Chinese-titled character/terminal animation.

Arc:  CLI title (命令行风格视频)  ->  Made By Gorden  ->  dogs & friends,
loading, and clock animations interspersed.

    python examples/cli_style_video.py                  # -> examples/cli_style_video.mp4
    python examples/cli_style_video.py out.mp4 fps=15   # quick preview
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from charvid import Movie, palette as P

W, H, FS = 1080, 1440, 50


def build():
    m = Movie(width=W, height=H, fps=30, font_size=FS, glow_radius=12,
              glow_gain=1.0)
    c = m._make_canvas()
    CX, CY = c.cols / 2.0, c.rows / 2.0
    BOT = c.rows - 3

    # ===== Scene 1 : CLI title 命令行风格视频 ==============================
    s = m.scene(4.8)
    s.particles(count=22, colors=[P.GREEN_DIM, P.GREEN], speed=0.45, start=0, dur=4.8)
    s.text("gorden@cli:~$ ./charvid --title", col=2, row=2, color=P.GREEN,
           anim_in="type", in_dur=1.4, start=0.1, dur=4.6, glow=0.85)
    s.text("命令行风格视频", cx=CX, cy=CY - 0.5, color=P.WHITE,
           anim_in="scatter", in_dur=1.5, start=1.4, dur=3.3,
           anim_out="dissolve", out_dur=0.5, glow=1.1)
    s.text("=" * 18, cx=CX, cy=CY + 2.2, color=P.GREEN, anim_in="wipe",
           in_dur=0.8, start=2.6, dur=2.0, glow=0.8)
    s.text("█", cx=CX + 9, cy=CY + 2.2, color=P.GREEN, idle="flicker",
           anim_in="fade", start=3.0, dur=1.8, glow=0.9)

    # ===== Scene 2 : Made By Gorden =======================================
    s = m.scene(4.2)
    s.text("// author", col=2, row=2, color=P.GRAY, anim_in="type",
           in_dur=0.6, start=0.2, dur=3.8, glow=0.5)
    s.banner("MADE BY", cx=CX, cy=CY - 3.2, color=P.WHITE, gap=1,
             anim_in="scatter", in_dur=1.0, start=0.3, dur=3.6, glow=1.0)
    s.banner("GORDEN", cx=CX, cy=CY + 2.6, color=P.ORANGE, gap=1,
             anim_in="scatter", in_dur=1.3, start=0.8, dur=3.1,
             anim_out="dissolve", out_dur=0.5, glow=1.1)
    s.border(symbol="+--", color=P.GREEN_DIM, glow=0.45, start=0, dur=4.2,
             in_dur=1.6)

    # ===== Scene 3 : 小狗 the dog ==========================================
    s = m.scene(3.6)
    s.text("pets/dog", col=2, row=2, color=P.GRAY, anim_in="type",
           in_dur=0.5, start=0.2, dur=3.4, glow=0.5)
    s.sprite("dog", cx=CX, cy=CY - 0.5, color=P.WHITE, idle="bob",
             anim_in="scatter", in_dur=1.2, start=0.3, dur=3.0,
             anim_out="fade", out_dur=0.3, glow=1.0)
    s.text("woof :)", cx=CX, cy=BOT, color=P.GREEN, anim_in="fade",
           in_dur=0.5, start=1.4, dur=2.0, glow=0.9)

    # ===== Scene 4 : more friends (cat + owl) =============================
    s = m.scene(3.4)
    s.particles(count=14, colors=[P.GREEN, P.BLUE], speed=0.4, start=0, dur=3.4)
    s.sprite("cat", cx=CX - 7, cy=CY, color=P.GREEN, idle="blink",
             blink_every=1.7, anim_in="scatter", in_dur=1.0, start=0.2,
             dur=3.0, anim_out="fade", out_dur=0.3, glow=1.0)
    s.sprite("owl", cx=CX + 7, cy=CY, color=P.WHITE, idle="blink",
             blink_every=2.1, anim_in="scatter", in_dur=1.0, start=0.5,
             dur=2.7, anim_out="fade", out_dur=0.3, glow=1.0)
    s.text("more friends", cx=CX, cy=BOT, color=P.ORANGE, anim_in="fade",
           in_dur=0.5, start=1.3, dur=1.8, glow=0.9)

    # ===== Scene 5 : bunny + frog =========================================
    s = m.scene(3.4)
    s.sprite("bunny", cx=CX - 7, cy=CY, color=P.WHITE, idle="blink",
             anim_in="scatter", in_dur=1.0, start=0.2, dur=3.0,
             anim_out="scatter", out_dur=0.4, glow=1.0)
    s.sprite("frog_big", cx=CX + 7, cy=CY, color=P.GREEN, idle="blink",
             blink_every=1.6, anim_in="scatter", in_dur=1.0, start=0.5,
             dur=2.5, anim_out="fade", out_dur=0.3, glow=1.0)
    s.text("made of characters", cx=CX, cy=BOT, color=P.GREEN,
           anim_in="fade", in_dur=0.5, start=1.3, dur=1.8, glow=0.9)

    # ===== Scene 6 : loading animation ====================================
    s = m.scene(3.8)
    s.text("gorden@cli:~$ load assets", col=2, row=2, color=P.GREEN,
           anim_in="type", in_dur=0.9, start=0.1, dur=3.7, glow=0.8)
    s.loadbar(width=14, cx=CX, cy=CY - 1, label="Loading", start=0.8, dur=2.4,
              fill_color=P.GREEN, label_color=P.WHITE, glow=1.0)
    s.loadbar(width=14, cx=CX, cy=CY + 1, label="Sprites", start=1.2, dur=2.2,
              fill_color=P.ORANGE, label_color=P.GRAY, fill_char="#",
              empty_char=".", glow=0.9)
    s.text("READY", cx=CX, cy=CY + 3.5, color=P.ORANGE, anim_in="scramble",
           in_dur=0.8, start=3.0, dur=0.8, glow=1.1)

    # ===== Scene 7 : clock animation ======================================
    s = m.scene(4.0)
    s.text("system/clock", col=2, row=2, color=P.GRAY, anim_in="type",
           in_dur=0.5, start=0.2, dur=3.8, glow=0.5)
    s.clock(radius=5, cx=CX, cy=CY - 0.5, period=3.0, color=P.GREEN,
            hand_color=P.ORANGE, start=0.2, dur=3.5, in_dur=0.6,
            anim_out="fade", out_dur=0.4, glow=0.95)
    s.timer(from_s=0, cx=CX, cy=BOT - 1, color=P.ORANGE, start=0.4, dur=3.3,
            anim_in="fade", in_dur=0.4, glow=0.9)
    s.text("tick ... tock", cx=CX, cy=BOT + 1, color=P.WHITE, anim_in="fade",
           in_dur=0.6, start=1.2, dur=2.4, glow=0.8)

    # ===== Scene 8 : outro ================================================
    s = m.scene(4.2)
    s.particles(count=20, colors=[P.GREEN_DIM, P.GREEN, P.WHITE], speed=0.45,
                start=0, dur=4.2)
    s.sprite("turtle", cx=CX, cy=CY - 2.5, color=P.GREEN, idle="bob",
             anim_in="scatter", in_dur=1.1, start=0.2, dur=3.8, glow=1.0)
    s.text("命令行风格视频", cx=CX, cy=CY + 2.0, color=P.WHITE,
           anim_in="fade", in_dur=0.8, start=1.0, dur=3.0,
           anim_out="fade", out_dur=0.8, glow=1.0)
    s.text("Made By Gorden", cx=CX, cy=CY + 4.0, color=P.ORANGE,
           anim_in="scramble", in_dur=1.0, start=1.6, dur=2.6, glow=0.95)
    return m


if __name__ == "__main__":
    out = "examples/cli_style_video.mp4"
    kw = {}
    for a in sys.argv[1:]:
        if "=" in a:
            k, v = a.split("=", 1)
            kw[k] = int(v) if v.isdigit() else v
        else:
            out = a
    m = build()
    if out.endswith(".html"):
        m.to_html(out, title="命令行风格视频")
        print("wrote", out)
    else:
        m.render(out, **kw)
