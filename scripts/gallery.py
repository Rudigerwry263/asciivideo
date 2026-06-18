"""Render the whole sprite library to a preview image + a markdown gallery.

    python scripts/gallery.py

Outputs:
  reference/gallery.png   - visual grid of every sprite (colored by category)
  reference/gallery.md    - per-category list with name, 描述 and ASCII art
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from charvid.canvas import CharCanvas
from charvid import sprites as S, palette as P

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(HERE, "reference")

FS = 22
NCOL = 6
CELL_COLS = 20     # grid cells per tile (width)
CELL_ROWS = 9      # grid cells per tile (art<=7 + label + gap)
CAT_COLOR = {"animal": P.GREEN, "face": P.WHITE, "object": P.ORANGE,
             "nature": P.CYAN, "tech": P.BLUE, "misc": P.GRAY}


def ordered():
    out = []
    by = S.names_by_category()
    for cat in S.categories():
        for n in by[cat]:
            out.append((n, cat))
    return out


def render_png(path):
    probe = CharCanvas(100, 100, font_size=FS)
    cw, chh = probe.cell_w, probe.cell_h
    items = ordered()
    n_rows_grid = math.ceil(len(items) / NCOL) * CELL_ROWS
    W = int(NCOL * CELL_COLS * cw) + 24
    H = int(n_rows_grid * chh) + 24
    W += W % 2
    H += H % 2
    C = CharCanvas(W, H, font_size=FS, glow_radius=6, glow_gain=0.6)
    C.new_frame()
    for i, (name, cat) in enumerate(items):
        cc, rr = i % NCOL, i // NCOL
        oc = cc * CELL_COLS + 1
        orow = rr * CELL_ROWS + 1
        art = S.get(name)
        C.line(oc, orow, name, P.GRAY, 0.9, 0.2)
        C.block(oc, orow + 1.4, art, CAT_COLOR.get(cat, P.GRAY), 1.0, 0.7)
    C.render_rgb("#0a0a0a").save(path)
    return path, (W, H), len(items)


def render_md(path):
    by = S.names_by_category()
    lines = ["# Sprite gallery (auto-generated)", "",
             "Run `python scripts/gallery.py` to refresh. Visual grid: "
             "![gallery](gallery.png)", "",
             "Use `s.sprite(\"name\")`. Faces marked (blink) support "
             "`idle=\"blink\"`.", ""]
    for cat in S.categories():
        lines.append("## " + cat + " (" + str(len(by[cat])) + ")")
        lines.append("")
        for name in by[cat]:
            inf = S.info(name)
            tag = " (blink)" if inf["blink"] else ""
            lines.append("**" + name + "** — " + inf["desc"] + tag)
            lines.append("```")
            lines.extend(inf["art"])
            lines.append("```")
            lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


if __name__ == "__main__":
    os.makedirs(REF, exist_ok=True)
    p, size, n = render_png(os.path.join(REF, "gallery.png"))
    print("wrote", p, size, n, "sprites")
    m = render_md(os.path.join(REF, "gallery.md"))
    print("wrote", m)
