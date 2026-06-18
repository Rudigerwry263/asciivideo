"""Export a Movie to a self-contained HTML file driven by charvid.js (Canvas 2D).

The Python timeline semantics (scenes / elements / animations) are serialized
to a JSON spec and inlined, together with the JS runtime, into a single .html.
ASCII sprites and block-letter banners are pre-expanded to plain lines so the
JS side needs no sprite library.
"""
import json
import os

from . import elements as E

_HERE = os.path.dirname(os.path.abspath(__file__))
_WEB = os.path.join(os.path.dirname(_HERE), "web")

_COMMON = ("start", "dur", "color", "glow", "anim_in", "in_dur", "anim_out",
           "out_dur", "ease_in", "ease_out", "idle", "seed")


def _common(el):
    d = {k: getattr(el, k) for k in _COMMON}
    d["alpha"] = el.base_alpha
    return d


def element_to_spec(el):
    d = _common(el)
    if isinstance(el, E.GlyphBlock):
        d["kind"] = "glyph"
        d["lines"] = list(el.lines)
        d["col"] = el.col
        d["row"] = el.row
        d["cx"] = el.cx
        d["cy"] = el.cy
        blink = getattr(el, "_blink", None)
        d["blink_lines"] = list(blink) if blink else None
        d["blink_every"] = getattr(el, "blink_every", 2.6)
        return d
    if isinstance(el, E.LoadBar):
        d.update(kind="loadbar", width=el.width, label=el.label,
                 fill_char=el.fill_char, empty_char=el.empty_char,
                 cx=el.cx, cy=el.cy, fill_color=el.fill_color,
                 label_color=el.label_color, fill_dur=el.fill_dur)
        return d
    if isinstance(el, E.Particles):
        d.update(kind="particles", count=el.count, chars=list(el.chars),
                 colors=list(el.colors), speed=el.speed, twinkle=el.twinkle,
                 region=list(el.region) if el.region else None)
        return d
    if isinstance(el, E.Border):
        d.update(kind="border", symbol=el.symbol, margin=el.margin,
                 draw_on=el.draw_on)
        return d
    if isinstance(el, E.SymbolGrid):
        d.update(kind="symgrid", cols_n=el.cols_n, rows_n=el.rows_n,
                 symbols=el.symbols, hollow=el.hollow, cx=el.cx, cy=el.cy)
        return d
    if isinstance(el, E.Clock):
        d.update(kind="clock", radius=el.radius, cx=el.cx, cy=el.cy,
                 period=el.period, ring_char=el.ring_char,
                 tick_char=el.tick_char, hand_char=el.hand_char,
                 hand_color=el.hand_color)
        return d
    if isinstance(el, E.Timer):
        d.update(kind="timer", from_s=el.from_s, rate=el.rate, cx=el.cx,
                 cy=el.cy, prefix=el.prefix)
        return d
    raise TypeError(f"Cannot serialize element {type(el).__name__}")


def movie_to_spec(movie):
    c = movie._make_canvas()
    return {
        "width": movie.width,
        "height": movie.height,
        "fps": movie.fps,
        "font_size": movie.font_size,
        "line_spacing": movie.line_spacing,
        "glow_radius": movie.glow_radius,
        "glow_gain": movie.glow_gain,
        "seed": movie.seed,
        "cell_w": c.cell_w,
        "cell_h": c.cell_h,
        "cols": c.cols,
        "rows": c.rows,
        "scenes": [
            {
                "duration": s.duration,
                "bg": s.bg,
                "elements": [element_to_spec(el) for el in s.elements],
            }
            for s in movie.scenes
        ],
    }


def to_html(movie, path, title="char-cli-video", loop=True, controls=True,
            autoplay=True):
    spec = movie_to_spec(movie)
    with open(os.path.join(_WEB, "charvid.js"), encoding="utf-8") as f:
        runtime = f.read()
    with open(os.path.join(_WEB, "template.html"), encoding="utf-8") as f:
        tmpl = f.read()
    spec_json = json.dumps(spec, ensure_ascii=False)
    opts_json = json.dumps({"loop": loop, "controls": controls,
                            "autoplay": autoplay}, ensure_ascii=False)
    html = (tmpl
            .replace("/*__CHARVID_JS__*/", runtime)
            .replace("__TITLE__", title)
            .replace('"__SPEC__"', spec_json)
            .replace('"__OPTS__"', opts_json))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
