#!/usr/bin/env python3
"""Bundle a monospace font into assets/fonts/ for consistent, portable renders.

charvid works out of the box with system monospace fonts (SF Mono / Menlo /
DejaVu Sans Mono), so this is optional. Run it to pin a known-good font:

    python scripts/install_fonts.py

Downloads JetBrains Mono (OFL) - nice rounded glyphs + broad symbol coverage.
"""
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(os.path.dirname(HERE), "assets", "fonts")

# Direct TTF (JetBrains Mono, OFL-1.1)
FONTS = {
    "JetBrainsMono-Regular.ttf":
        "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/"
        "fonts/ttf/JetBrainsMono-Regular.ttf",
}


def main():
    os.makedirs(DEST, exist_ok=True)
    ok = 0
    for name, url in FONTS.items():
        out = os.path.join(DEST, name)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            print(f"[skip] {name} already present")
            ok += 1
            continue
        try:
            print(f"[get ] {name} <- {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "charvid"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            with open(out, "wb") as f:
                f.write(data)
            print(f"[ok  ] {name} ({len(data)} bytes)")
            ok += 1
        except Exception as e:
            print(f"[fail] {name}: {e}", file=sys.stderr)
    if ok == 0:
        print("No fonts installed; charvid will fall back to system monospace.")
        return 1
    print(f"Done. Set CHARVID_FONT or pass font=... to use a specific file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
