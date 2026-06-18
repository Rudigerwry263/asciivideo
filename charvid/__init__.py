"""charvid - character / terminal-style animated video engine.

Compose a Movie of Scenes from character-art elements (text, ASCII sprites,
block-letter banners, loading bars, particle fields, borders, symbol grids,
timers) and render deterministically to MP4 via ffmpeg.

Quick start
-----------
    from charvid import Movie, palette as P

    m = Movie(width=1080, height=1440, fps=30, font_size=44)  # add cjk_font=... for Chinese
    s = m.scene(4.0)
    s.banner("OPENAI", color=P.WHITE, cy=10, anim_in="scatter", in_dur=1.0)
    s.sprite("bunny", color=P.GREEN, idle="blink", anim_in="scatter")
    m.render("out.mp4")
"""
from .movie import Movie, Scene
from . import palette
from . import sprites
from . import easing
from . import elements

__all__ = ["Movie", "Scene", "palette", "sprites", "easing", "elements"]
