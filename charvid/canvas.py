"""CharCanvas: a pixel surface addressed as a monospace character grid.

Two RGBA layers are kept per frame:
  * ``base``  - crisp glyphs
  * ``glow``  - the same glyphs, blurred at finalize() for a phosphor halo

finalize() composites: black + additive(blur(glow)) + (base over).
"""
import unicodedata

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from . import palette
from . import fonts


def char_cells(ch):
    """Display width of a character in grid cells (CJK / fullwidth = 2)."""
    if not ch:
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def line_cells(s):
    return sum(char_cells(c) for c in s)


class CharCanvas:
    def __init__(self, width, height, font_size=40, line_spacing=1.12,
                 font_path=None, cjk_font_path=None, glow_radius=10,
                 glow_gain=0.9):
        self.w = width
        self.h = height
        self.font_size = font_size
        self.font, self.font_path = fonts.load(font_size, font_path)
        self.cjk_font, self.cjk_font_path = fonts.load_cjk(font_size, cjk_font_path)
        self.glow_radius = glow_radius
        self.glow_gain = glow_gain

        # cell metrics from the font (monospace advance + line height)
        bbox = self.font.getbbox("M")
        self.ascent, self.descent = self.font.getmetrics()
        try:
            self.cell_w = self.font.getlength("M")
        except Exception:
            self.cell_w = bbox[2] - bbox[0]
        self.cell_h = (self.ascent + self.descent) * line_spacing
        self.cols = int(self.w // self.cell_w)
        self.rows = int(self.h // self.cell_h)

        self._stamp_cache = {}
        self.new_frame()

    # ---- coordinate helpers -------------------------------------------------
    def cell_px(self, col, row):
        """Top-left pixel of grid cell (col,row). Floats allowed."""
        return col * self.cell_w, row * self.cell_h

    def center_origin(self, n_cols, n_rows):
        """Top-left (col,row) that centers an n_cols x n_rows block."""
        return (self.cols - n_cols) / 2.0, (self.rows - n_rows) / 2.0

    # ---- frame lifecycle ----------------------------------------------------
    def new_frame(self):
        self.base = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        self.glow = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        self._dbase = ImageDraw.Draw(self.base)
        self._dglow = ImageDraw.Draw(self.glow)

    # ---- low-level drawing --------------------------------------------------
    def _font_for(self, ch):
        """Return (font, is_wide) - CJK glyphs use the fallback font."""
        if char_cells(ch) == 2 and self.cjk_font is not None:
            return self.cjk_font, True
        return self.font, char_cells(ch) == 2

    def glyph(self, x, y, ch, color, alpha=1.0, glow=1.0):
        """Draw one glyph; (x,y) is the cell top-left in pixels. Wide (CJK)
        glyphs are centered within their 2-cell box."""
        if alpha <= 0 or ch == " " or ch == "":
            return
        font, wide = self._font_for(ch)
        fill = palette.rgba(color, alpha)
        if wide:
            # center horizontally in the 2-cell span, align ascender top
            px = x + self.cell_w
            self._dbase.text((px, y), ch, font=font, fill=fill, anchor="ma")
            if glow > 0:
                gfill = palette.rgba(color, alpha * glow)
                self._dglow.text((px, y), ch, font=font, fill=gfill, anchor="ma")
        else:
            self._dbase.text((x, y), ch, font=font, fill=fill)
            if glow > 0:
                gfill = palette.rgba(color, alpha * glow)
                self._dglow.text((x, y), ch, font=font, fill=gfill)

    def glyph_centered(self, cx, cy, ch, color, alpha=1.0, glow=1.0):
        if alpha <= 0 or ch == " " or ch == "":
            return
        font, _ = self._font_for(ch)
        fill = palette.rgba(color, alpha)
        self._dbase.text((cx, cy), ch, font=font, fill=fill, anchor="mm")
        if glow > 0:
            gfill = palette.rgba(color, alpha * glow)
            self._dglow.text((cx, cy), ch, font=font, fill=gfill, anchor="mm")

    def line(self, col, row, text, color, alpha=1.0, glow=1.0):
        x0, y0 = self.cell_px(col, row)
        x = x0
        for ch in text:
            if ch != " ":
                self.glyph(x, y0, ch, color, alpha, glow)
            x += char_cells(ch) * self.cell_w

    def block(self, col, row, lines, color, alpha=1.0, glow=1.0):
        for r, ln in enumerate(lines):
            self.line(col, row + r, ln, color, alpha, glow)

    # ---- stamp cache (fast path for static blocks) --------------------------
    def text_stamp(self, lines, color, glow=1.0):
        """Render a multi-line block once into a tight RGBA stamp; cached."""
        key = ("\n".join(lines), color, round(glow, 3), self.font_size)
        st = self._stamp_cache.get(key)
        if st is not None:
            return st
        n_cols = max((line_cells(l) for l in lines), default=0)
        n_rows = len(lines)
        w = max(1, int(round(n_cols * self.cell_w)) + 4)
        h = max(1, int(round(n_rows * self.cell_h)) + 4)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        fill = palette.rgba(color, 1.0)
        for r, ln in enumerate(lines):
            x = 0.0
            y = r * self.cell_h
            for ch in ln:
                if ch != " ":
                    font, wide = self._font_for(ch)
                    if wide:
                        d.text((x + self.cell_w, y), ch, font=font, fill=fill,
                               anchor="ma")
                    else:
                        d.text((x, y), ch, font=font, fill=fill)
                x += char_cells(ch) * self.cell_w
        st = (img, glow, (w, h))
        self._stamp_cache[key] = st
        return st

    def paste_stamp(self, stamp, x, y, alpha=1.0):
        img, glow, _ = stamp
        if alpha <= 0:
            return
        if alpha < 1.0:
            a = img.split()[3].point(lambda v: int(v * alpha))
            img2 = img.copy()
            img2.putalpha(a)
        else:
            img2 = img
        ix, iy = int(round(x)), int(round(y))
        self.base.alpha_composite(img2, (ix, iy))
        if glow > 0:
            if glow < 1.0:
                a = img2.split()[3].point(lambda v: int(v * glow))
                g = img2.copy()
                g.putalpha(a)
            else:
                g = img2
            self.glow.alpha_composite(g, (ix, iy))

    # ---- finalize -----------------------------------------------------------
    def render_rgb(self, bg="#000000"):
        bg_rgb = np.array(palette.hex_to_rgb(bg), dtype=np.float32)
        out = np.zeros((self.h, self.w, 3), dtype=np.float32) + bg_rgb

        if self.glow_radius > 0 and self.glow_gain > 0:
            gl = self.glow.filter(ImageFilter.GaussianBlur(self.glow_radius))
            ga = np.asarray(gl, dtype=np.float32)
            grgb, ga4 = ga[..., :3], (ga[..., 3:4] / 255.0)
            out = out + grgb * ga4 * self.glow_gain

        b = np.asarray(self.base, dtype=np.float32)
        brgb, ba = b[..., :3], (b[..., 3:4] / 255.0)
        out = brgb * ba + out * (1.0 - ba)

        np.clip(out, 0, 255, out=out)
        return Image.fromarray(out.astype(np.uint8), "RGB")
