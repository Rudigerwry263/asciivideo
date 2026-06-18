"""Timeline elements. Each element renders itself for a given scene-local time.

Common timing model
--------------------
start / dur        : visibility window inside the scene (seconds)
anim_in / in_dur   : entrance animation + its length
anim_out / out_dur : exit animation + its length
ease_in / ease_out : easing names (see easing.py)
idle               : per-frame idle behaviour while fully visible
                     ("blink", "bob", "flicker", "drift" or None)
"""
import math
import random as _random

from . import easing
from . import sprites as _sprites
from .canvas import char_cells

SCRAMBLE_CHARS = "!@#$%^&*()_+-={}[]|;:<>?/01XY01<>~"
PARTICLE_CHARS = list('.,`\'"^~*+-/\\|<>:;=°•∙')


def _rng(seed):
    if isinstance(seed, (tuple, list)):
        seed = "|".join(str(s) for s in seed)
    return _random.Random(seed)


def _layout(lines):
    """Return ([(display_col, row, char)...], display_width). CJK = 2 cols."""
    glyphs = []
    ncols = 0
    for ri, ln in enumerate(lines):
        d = 0
        for ch in ln:
            if ch != " ":
                glyphs.append((d, ri, ch))
            d += char_cells(ch)
        ncols = max(ncols, d)
    return glyphs, ncols


class Element:
    kind = "element"

    def __init__(self, start=0.0, dur=3.0, color="#52E06A", glow=1.0,
                 alpha=1.0, anim_in="fade", in_dur=0.6, anim_out="fade",
                 out_dur=0.5, ease_in="ease_out_cubic", ease_out="ease_out_cubic",
                 idle=None, seed=0):
        self.start = start
        self.dur = dur
        self.color = color
        self.glow = glow
        self.base_alpha = alpha
        self.anim_in = anim_in
        self.in_dur = max(1e-4, in_dur)
        self.anim_out = anim_out
        self.out_dur = max(1e-4, out_dur)
        self.ease_in = ease_in
        self.ease_out = ease_out
        self.idle = idle
        self.seed = seed

    # phase helpers ----------------------------------------------------------
    def window(self, t):
        """Return (visible, in_p, out_p, local) for scene-local time t."""
        end = self.start + self.dur
        if t < self.start - 1e-6 or t > end + 1e-6:
            return False, 0.0, 0.0, 0.0
        local = t - self.start
        in_p = easing.clamp01(local / self.in_dur)
        out_p = easing.clamp01((end - t) / self.out_dur)
        return True, in_p, out_p, local

    def draw(self, canvas, t):
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Glyph block: shared base for text, sprites and banners
# ---------------------------------------------------------------------------
class GlyphBlock(Element):
    kind = "glyph"

    def __init__(self, lines, col=None, row=None, cx=None, cy=None,
                 align="center", **kw):
        super().__init__(**kw)
        self.lines = [l.rstrip("\n") for l in lines]
        self.n_rows = len(self.lines)
        self.col = col
        self.row = row
        self.cx = cx          # block-center cell coords (optional)
        self.cy = cy
        self.align = align
        self._glyphs, self.n_cols = _layout(self.lines)

    def origin(self, canvas):
        """Top-left (col,row) of the block in cell coordinates."""
        if self.col is not None and self.row is not None:
            return float(self.col), float(self.row)
        if self.cx is not None and self.cy is not None:
            return self.cx - self.n_cols / 2.0, self.cy - self.n_rows / 2.0
        oc, orow = canvas.center_origin(self.n_cols, self.n_rows)
        return oc, orow

    def _idle_offset(self, t):
        if self.idle == "bob":
            return 0.0, math.sin(t * 2.0) * 0.18  # cells
        return 0.0, 0.0

    def _idle_alpha(self, t):
        if self.idle == "flicker":
            r = _rng((self.seed, int(t * 12)))
            return 0.78 + 0.22 * r.random()
        return 1.0

    def current_lines(self, t):
        """Allow blink idle to swap to an alternate frame (sprite override)."""
        return self.lines

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        cw, ch = canvas.cell_w, canvas.cell_h
        oc, orow = self.origin(canvas)
        dx, dy = self._idle_offset(t)
        oc += dx
        orow += dy
        ox, oy = oc * cw, orow * ch
        ei = easing.get(self.ease_in)
        eo = easing.get(self.ease_out)
        out_factor = eo(out_p) if self.anim_out in ("fade", "dissolve", "scatter") else 1.0
        base_a = self.base_alpha * self._idle_alpha(t)

        lines = self.current_lines(t)
        glyphs = self._glyphs if lines is self.lines else _layout(lines)[0]

        # ---- entrance styles -------------------------------------------
        if self.anim_in == "scatter" and in_p < 1.0:
            self._draw_scatter(canvas, glyphs, ox, oy, cw, ch, ei(in_p),
                               base_a, out_factor)
            return
        if self.anim_in == "scramble" and in_p < 1.0:
            self._draw_scramble(canvas, glyphs, ox, oy, cw, ch, in_p,
                                base_a, out_factor)
            return
        if self.anim_in == "type" and in_p < 1.0:
            self._draw_type(canvas, glyphs, ox, oy, cw, ch, in_p,
                            base_a, out_factor)
            return
        if self.anim_in == "wipe" and in_p < 1.0:
            self._draw_wipe(canvas, glyphs, ox, oy, cw, ch, ei(in_p),
                            base_a, out_factor)
            return
        if self.anim_in in ("rise", "drop", "slide_left", "slide_right") and in_p < 1.0:
            self._draw_slide(canvas, lines, oc, orow, ei(in_p), base_a, out_factor)
            return

        # fade entrance (and fully-in hold) ------------------------------
        a = base_a * out_factor
        if self.anim_in == "fade" and in_p < 1.0:
            a *= ei(in_p)
        # exit: dissolve / scatter
        if self.anim_out == "dissolve" and out_p < 1.0:
            self._draw_dissolve(canvas, glyphs, ox, oy, cw, ch, out_p, base_a)
            return
        if self.anim_out == "scatter" and out_p < 1.0:
            self._draw_scatter(canvas, glyphs, ox, oy, cw, ch, out_p,
                               base_a, 1.0, reverse=True)
            return
        self._draw_block(canvas, lines, oc, orow, a)

    # fast static path (cached stamp) -----------------------------------
    def _draw_block(self, canvas, lines, oc, orow, alpha):
        stamp = canvas.text_stamp(lines, self.color, self.glow)
        canvas.paste_stamp(stamp, oc * canvas.cell_w, orow * canvas.cell_h, alpha)

    def _draw_slide(self, canvas, lines, oc, orow, p, base_a, out_factor):
        travel = 1.6  # cells
        if self.anim_in == "rise":
            orow = orow + travel * (1 - p)
        elif self.anim_in == "drop":
            orow = orow - travel * (1 - p)
        elif self.anim_in == "slide_left":
            oc = oc + travel * (1 - p)
        else:
            oc = oc - travel * (1 - p)
        self._draw_block(canvas, lines, oc, orow, base_a * p * out_factor)

    def _draw_type(self, canvas, glyphs, ox, oy, cw, ch, in_p, base_a, out_factor):
        # reveal in reading order
        n = len(glyphs)
        revealed = int(round(in_p * n))
        order = sorted(range(n), key=lambda i: (glyphs[i][1], glyphs[i][0]))
        a = base_a * out_factor
        for k, i in enumerate(order):
            if k >= revealed:
                break
            ci, ri, c = glyphs[i]
            canvas.glyph(ox + ci * cw, oy + ri * ch, c, self.color, a, self.glow)

    def _draw_wipe(self, canvas, glyphs, ox, oy, cw, ch, p, base_a, out_factor):
        cutoff = p * self.n_rows
        a = base_a * out_factor
        for ci, ri, c in glyphs:
            if ri <= cutoff:
                la = a * easing.clamp01(cutoff - ri)
                canvas.glyph(ox + ci * cw, oy + ri * ch, c, self.color, la, self.glow)

    def _draw_scatter(self, canvas, glyphs, ox, oy, cw, ch, p, base_a,
                      out_factor, reverse=False):
        rng = _rng((self.seed, "scatter"))
        spread = max(canvas.w, canvas.h) * 0.30
        pp = (1 - p) if reverse else p
        a = base_a * out_factor * (pp if reverse else easing.clamp01(p * 1.4))
        for ci, ri, c in glyphs:
            ang = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(0.25, 1.0) * spread
            sx = ox + ci * cw + math.cos(ang) * dist
            sy = oy + ri * ch + math.sin(ang) * dist
            tx = ox + ci * cw
            ty = oy + ri * ch
            gx = easing.lerp(sx, tx, p)
            gy = easing.lerp(sy, ty, p)
            canvas.glyph(gx, gy, c, self.color, a, self.glow)

    def _draw_scramble(self, canvas, glyphs, ox, oy, cw, ch, in_p, base_a, out_factor):
        rng = _rng((self.seed, "scramble"))
        resolve = {}
        for g in glyphs:
            resolve[g] = rng.uniform(0.0, 0.7)
        tick = int(in_p * 30)
        a = base_a * out_factor
        for ci, ri, c in glyphs:
            rt = resolve[(ci, ri, c)]
            if in_p >= rt + 0.18:
                canvas.glyph(ox + ci * cw, oy + ri * ch, c, self.color, a, self.glow)
            elif in_p >= rt - 0.05:
                rr = _rng((self.seed, ci, ri, tick))
                rc = SCRAMBLE_CHARS[rr.randrange(len(SCRAMBLE_CHARS))]
                canvas.glyph(ox + ci * cw, oy + ri * ch, rc, self.color,
                             a * 0.75, self.glow)

    def _draw_dissolve(self, canvas, glyphs, ox, oy, cw, ch, out_p, base_a):
        rng = _rng((self.seed, "dissolve"))
        for ci, ri, c in glyphs:
            thr = rng.random()
            if out_p > thr:
                canvas.glyph(ox + ci * cw, oy + ri * ch, c, self.color,
                             base_a * out_p, self.glow)


# ---------------------------------------------------------------------------
# Concrete elements
# ---------------------------------------------------------------------------
class Text(GlyphBlock):
    def __init__(self, text, **kw):
        lines = text.split("\n") if isinstance(text, str) else list(text)
        super().__init__(lines, **kw)


class Banner(GlyphBlock):
    def __init__(self, text, fill="█", gap=1, **kw):
        super().__init__(_sprites.banner(text, fill=fill, gap=gap), **kw)


def _normalize_art(art):
    """Split a string / list into lines, trimming a leading/trailing blank
    line so triple-quoted blocks work cleanly."""
    lines = art.split("\n") if isinstance(art, str) else list(art)
    if lines and lines[0] == "":
        lines = lines[1:]
    while lines and lines[-1].strip() == "":
        lines = lines[:-1]
    return lines


class Sprite(GlyphBlock):
    def __init__(self, name, blink_every=2.6, **kw):
        self.name = name
        self.blink_every = blink_every
        super().__init__(_sprites.get(name), **kw)
        self._blink = _sprites.blink(name) if _sprites.has_blink(name) else None

    def current_lines(self, t):
        if self.idle == "blink" and self._blink and (t % self.blink_every) < 0.14:
            return self._blink
        return self.lines


class CustomSprite(GlyphBlock):
    """A sprite from inline multi-line text. Pass ``blink`` (alternate art)
    plus ``idle='blink'`` to animate the eyes."""
    def __init__(self, art, blink=None, blink_every=2.6, **kw):
        self.blink_every = blink_every
        self._blink = _normalize_art(blink) if blink else None
        super().__init__(_normalize_art(art), **kw)

    def current_lines(self, t):
        if self.idle == "blink" and self._blink and (t % self.blink_every) < 0.14:
            return self._blink
        return self.lines


class LoadBar(Element):
    """`Loading NN%  [######    ]` that fills across its duration."""
    kind = "loadbar"

    def __init__(self, width=10, label="Loading", fill_char="●",
                 empty_char=" ", cx=None, cy=None, pct_color="#52E06A",
                 fill_color="#52E06A", label_color="#F2F2F2",
                 fill_dur=None, **kw):
        super().__init__(**kw)
        self.width = width
        self.label = label
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.cx = cx
        self.cy = cy
        self.pct_color = pct_color
        self.fill_color = fill_color
        self.label_color = label_color
        self.fill_dur = fill_dur

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        fill_dur = self.fill_dur if self.fill_dur is not None else self.dur - self.out_dur
        p = easing.get(self.ease_in)(easing.clamp01(local / max(1e-4, fill_dur)))
        pct = int(round(p * 100))
        filled = int(round(p * self.width))
        bar = "[" + self.fill_char * filled + self.empty_char * (self.width - filled) + "]"
        head = f"{self.label} {pct}%"
        a = self.base_alpha * (easing.get(self.ease_in)(in_p)) * (out_p if self.anim_out == "fade" else 1.0)
        cx = self.cx if self.cx is not None else canvas.cols / 2.0
        cy = self.cy if self.cy is not None else canvas.rows / 2.0
        canvas.line(cx - len(head) / 2.0, cy - 1, head, self.label_color, a, self.glow)
        # color the percentage portion of the label differently
        canvas.line(cx - len(bar) / 2.0, cy, bar, self.fill_color, a, self.glow)


class Particles(Element):
    """Ambient drifting character field (the reference's floating marks)."""
    kind = "particles"

    def __init__(self, count=40, chars=None, colors=None, speed=0.6,
                 twinkle=True, region=None, **kw):
        kw.setdefault("anim_in", "fade")
        kw.setdefault("in_dur", 1.0)
        super().__init__(**kw)
        self.count = count
        self.chars = chars or PARTICLE_CHARS
        self.colors = colors or ["#52E06A", "#F2F2F2", "#4C8DFF"]
        self.speed = speed
        self.twinkle = twinkle
        self.region = region  # (col0,row0,col1,row1) in cells, else full

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        a_env = self.base_alpha * easing.get("ease_out")(in_p) * (out_p if self.anim_out == "fade" else 1.0)
        c0, r0, c1, r1 = self.region or (0, 0, canvas.cols, canvas.rows)
        cw, ch = canvas.cell_w, canvas.cell_h
        for i in range(self.count):
            rng = _rng((self.seed, "p", i))
            bx = rng.uniform(c0, c1)
            by = rng.uniform(r0, r1)
            vy = rng.uniform(-1, 1) * self.speed
            vx = rng.uniform(-1, 1) * self.speed * 0.4
            x = (bx + vx * local)
            y = (by + vy * local)
            # wrap inside region
            x = c0 + (x - c0) % max(1e-3, (c1 - c0))
            y = r0 + (y - r0) % max(1e-3, (r1 - r0))
            ch_ = self.chars[rng.randrange(len(self.chars))]
            col = self.colors[rng.randrange(len(self.colors))]
            tw = 1.0
            if self.twinkle:
                tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.4 + i))
            canvas.glyph(x * cw, y * ch, ch_, col, a_env * tw, self.glow)


class Border(Element):
    """Decorative frame made of repeated symbols, optionally drawn-on."""
    kind = "border"

    def __init__(self, symbol="|§|", margin=1, draw_on=True, **kw):
        kw.setdefault("anim_in", "none")
        super().__init__(**kw)
        self.symbol = symbol
        self.margin = margin
        self.draw_on = draw_on

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        m = self.margin
        cols, rows = canvas.cols, canvas.rows
        cells = []
        for c in range(m, cols - m):
            cells.append((c, m))
            cells.append((c, rows - m - 1))
        for r in range(m, rows - m):
            cells.append((m, r))
            cells.append((cols - m - 1, r))
        a = self.base_alpha * (out_p if self.anim_out == "fade" else 1.0)
        reveal = easing.get(self.ease_in)(in_p) if self.draw_on else 1.0
        nshow = int(reveal * len(cells))
        sym = self.symbol
        for idx, (c, r) in enumerate(cells):
            if self.draw_on and idx > nshow:
                continue
            ch = sym[idx % len(sym)] if sym else "|"
            canvas.glyph(c * canvas.cell_w, r * canvas.cell_h, ch, self.color, a, self.glow)


class SymbolGrid(Element):
    """A dense block / frame of shimmering keyboard symbols."""
    kind = "symgrid"

    def __init__(self, cols_n=9, rows_n=14, symbols="§|⌐¬⌐_/\\<>", hollow=True,
                 cx=None, cy=None, **kw):
        kw.setdefault("anim_in", "scramble")
        super().__init__(**kw)
        self.cols_n = cols_n
        self.rows_n = rows_n
        self.symbols = symbols
        self.hollow = hollow
        self.cx = cx
        self.cy = cy

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        cx = self.cx if self.cx is not None else canvas.cols / 2.0
        cy = self.cy if self.cy is not None else canvas.rows / 2.0
        c0 = cx - self.cols_n / 2.0
        r0 = cy - self.rows_n / 2.0
        a = self.base_alpha * (out_p if self.anim_out == "fade" else 1.0)
        cw, ch = canvas.cell_w, canvas.cell_h
        for rr in range(self.rows_n):
            for cc in range(self.cols_n):
                if self.hollow and 0 < cc < self.cols_n - 1 and 0 < rr < self.rows_n - 1:
                    continue
                rng = _rng((self.seed, cc, rr))
                resolve = rng.uniform(0, 0.6)
                if self.anim_in == "scramble" and in_p < resolve + 0.18:
                    if in_p < resolve - 0.05:
                        continue
                    tick = int(in_p * 24)
                    rr2 = _rng((self.seed, cc, rr, tick))
                    sym = self.symbols[rr2.randrange(len(self.symbols))]
                    aa = a * 0.7
                else:
                    sym = self.symbols[rng.randrange(len(self.symbols))]
                    aa = a
                tw = 0.82 + 0.18 * math.sin(t * 2 + cc + rr)
                canvas.glyph((c0 + cc) * cw, (r0 + rr) * ch, sym,
                             self.color, aa * tw, self.glow)


class Clock(Element):
    """An analog clock drawn from characters: a ring of marks + rotating
    hour/minute hands. ``period`` = seconds for the minute hand to do a full
    turn (the hour hand turns 12x slower)."""
    kind = "clock"

    def __init__(self, radius=6, cx=None, cy=None, period=6.0, ring_char="·",
                 tick_char="+", hand_char="o", hand_color=None, **kw):
        kw.setdefault("anim_in", "fade")
        super().__init__(**kw)
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.period = period
        self.ring_char = ring_char
        self.tick_char = tick_char
        self.hand_char = hand_char
        self.hand_color = hand_color

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        a = self.base_alpha * easing.get(self.ease_in)(in_p) * \
            (out_p if self.anim_out == "fade" else 1.0)
        cw, ch = canvas.cell_w, canvas.cell_h
        cx = (self.cx if self.cx is not None else canvas.cols / 2.0) * cw
        cy = (self.cy if self.cy is not None else canvas.rows / 2.0) * ch
        R = self.radius * cw
        # ring + 12 hour ticks
        for k in range(60):
            ang = -math.pi / 2 + 2 * math.pi * k / 60
            major = (k % 5 == 0)
            rr = R if not major else R * 1.04
            x = cx + math.cos(ang) * rr
            y = cy + math.sin(ang) * rr
            canvas.glyph_centered(x, y, self.tick_char if major else self.ring_char,
                                  self.color, a * (1.0 if major else 0.5), self.glow)
        hand_col = self.hand_color or self.color
        # minute hand (long) + hour hand (short)
        ma = -math.pi / 2 + 2 * math.pi * (local / self.period)
        ha = -math.pi / 2 + 2 * math.pi * (local / (self.period * 12))
        for f in [0.22, 0.40, 0.58, 0.76, 0.92]:
            canvas.glyph_centered(cx + math.cos(ma) * R * f,
                                  cy + math.sin(ma) * R * f,
                                  self.hand_char, hand_col, a, self.glow)
        for f in [0.20, 0.40, 0.60]:
            canvas.glyph_centered(cx + math.cos(ha) * R * 0.6 * f,
                                  cy + math.sin(ha) * R * 0.6 * f,
                                  self.hand_char, hand_col, a, self.glow)
        canvas.glyph_centered(cx, cy, "O", hand_col, a, self.glow)


class Timer(Element):
    """A monospace MM:SS counter."""
    kind = "timer"

    def __init__(self, from_s=0, rate=1.0, cx=None, cy=None, prefix="", **kw):
        super().__init__(**kw)
        self.from_s = from_s
        self.rate = rate
        self.cx = cx
        self.cy = cy
        self.prefix = prefix

    def draw(self, canvas, t):
        vis, in_p, out_p, local = self.window(t)
        if not vis:
            return
        secs = int(self.from_s + local * self.rate)
        txt = f"{self.prefix}{secs // 60:02d}:{secs % 60:02d}"
        a = self.base_alpha * easing.get(self.ease_in)(in_p) * (out_p if self.anim_out == "fade" else 1.0)
        cx = self.cx if self.cx is not None else canvas.cols / 2.0
        cy = self.cy if self.cy is not None else canvas.rows / 2.0
        canvas.line(cx - len(txt) / 2.0, cy, txt, self.color, a, self.glow)
