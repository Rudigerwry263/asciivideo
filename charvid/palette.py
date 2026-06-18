"""Terminal / CLI character-video color palette.

Derived from the Studio Dumbar OpenAI DevDay reference: a black canvas with
phosphor-green primary text, crisp white, and orange / blue accents.
"""

# Core
BG = "#000000"
GREEN = "#52E06A"        # phosphor terminal green (primary)
GREEN_DIM = "#2E8B4A"    # dim green for de-emphasised / background grids
WHITE = "#F2F2F2"        # crisp off-white
GRAY = "#8A8A8A"
ORANGE = "#FF6A1A"       # accent / highlight
BLUE = "#4C8DFF"         # secondary accent
YELLOW = "#FFD23F"
RED = "#FF4D4D"
CYAN = "#46E5D0"

# Named groups for ambient particle fields (chosen to read on black)
ACCENTS = [GREEN, WHITE, ORANGE, BLUE]
GREENS = [GREEN, GREEN_DIM, "#7CF08E", "#3CC457"]


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgba(h, a=1.0):
    r, g, b = hex_to_rgb(h)
    return (r, g, b, int(round(255 * max(0.0, min(1.0, a)))))
