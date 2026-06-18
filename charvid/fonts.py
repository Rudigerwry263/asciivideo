"""Monospace font resolution.

Resolution order:
  1. explicit path passed by the caller
  2. CHARVID_FONT env var
  3. bundled font in assets/fonts/ (run scripts/install_fonts.py to fetch one)
  4. common system monospace fonts (macOS / Linux)
"""
import os
from PIL import ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
_BUNDLED_DIR = os.path.join(os.path.dirname(_HERE), "assets", "fonts")

_BUNDLED = [
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMonoNL-Regular.ttf",
    "DejaVuSansMono.ttf",
    "SpaceMono-Regular.ttf",
]

_SYSTEM = [
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
]

# CJK fallback fonts (used per-character for Chinese/Japanese/Korean glyphs).
# Each entry is (path, ttc_index).
_CJK_BUNDLED = ["NotoSansMonoCJKsc-Regular.otf", "SarasaMonoSC-Regular.ttf"]
_CJK_SYSTEM = [
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ("/System/Library/Fonts/STHeiti Light.ttc", 0),
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 0),
    ("/usr/share/fonts/truetype/sarasa-gothic/Sarasa-Regular.ttc", 0),
    ("/usr/share/fonts/wenquanyi/wqy-microhei/wqy-microhei.ttc", 0),
]


def candidate_paths(explicit=None):
    out = []
    if explicit:
        out.append(explicit)
    env = os.environ.get("CHARVID_FONT")
    if env:
        out.append(env)
    for name in _BUNDLED:
        out.append(os.path.join(_BUNDLED_DIR, name))
    out.extend(_SYSTEM)
    return out


def resolve_path(explicit=None):
    for p in candidate_paths(explicit):
        if p and os.path.exists(p):
            return p
    raise FileNotFoundError(
        "No monospace font found. Pass font=... , set CHARVID_FONT, or run "
        "python scripts/install_fonts.py to bundle JetBrains Mono."
    )


def load(size, explicit=None):
    path = resolve_path(explicit)
    return ImageFont.truetype(path, size), path


def load_cjk(size, explicit=None):
    """Load a CJK-capable font for Chinese/Japanese/Korean glyphs.

    Returns (font, path) or (None, None) if none is found (CJK then renders
    blank). ``explicit`` may be a path string or a (path, index) tuple.
    """
    cands = []
    if explicit:
        cands.append(explicit if isinstance(explicit, tuple) else (explicit, 0))
    env = os.environ.get("CHARVID_CJK_FONT")
    if env:
        cands.append((env, 0))
    for name in _CJK_BUNDLED:
        cands.append((os.path.join(_BUNDLED_DIR, name), 0))
    cands.extend(_CJK_SYSTEM)
    for path, idx in cands:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=idx), path
            except Exception:
                continue
    return None, None
