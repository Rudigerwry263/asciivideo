r"""ASCII / character-art sprite library + a block-letter banner generator.

Each sprite is a list of equal-intent lines (leading spaces are significant).
Some sprites ship a ``blink`` variant so the eyes can be animated.
"""

# ---------------------------------------------------------------------------
# Creatures & objects.  Designed with widely-supported monospace glyphs.
# ---------------------------------------------------------------------------
_SPRITES = {
    "bunny": {
        "art": [
            r" (\_/) ",
            r" (o.o) ",
            r"/(\")(\")",
        ],
        "blink": [
            r" (\_/) ",
            r" (-.-) ",
            r"/(\")(\")",
        ],
    },
    "frog": {
        "art": [
            r"  @,@  ",
            r" (-.-) ",
            r" (\")(\")",
        ],
        "blink": [
            r"  -,-  ",
            r" (-.-) ",
            r" (\")(\")",
        ],
    },
    "frog_big": {
        "art": [
            r"  @,@  ",
            r" (<=>)",
            r"<~~~~~>",
            r" ^^ ^^ ",
        ],
        "blink": [
            r"  -,-  ",
            r" (<=>)",
            r"<~~~~~>",
            r" ^^ ^^ ",
        ],
    },
    "cat": {
        "art": [
            r" /\_/\ ",
            r"( o.o )",
            r" > ^ < ",
        ],
        "blink": [
            r" /\_/\ ",
            r"( -.- )",
            r" > ^ < ",
        ],
    },
    "turtle": {
        "art": [
            r"    _____    ",
            r"  _/ . . \_  ",
            r" / |_____| \ ",
            r"(__/     \__)",
        ],
        "blink": [
            r"    _____    ",
            r"  _/ - - \_  ",
            r" / |_____| \ ",
            r"(__/     \__)",
        ],
    },
    "dog": {
        "art": [
            r"  / \__   ",
            r" (    @\__ ",
            r"  /         o",
            r" /   (_____/ ",
            r"/_____/      ",
        ],
    },
    "fish": {
        "art": [
            r"><(((°>",
        ],
    },
    "fish_school": {
        "art": [
            r"  ><(((°>      ",
            r"        ><(((°> ",
            r"   ><(((°>     ",
        ],
    },
    "owl": {
        "art": [
            r" ,___, ",
            r" {O,O} ",
            r" /)_)  ",
            r'  " "  ',
        ],
        "blink": [
            r" ,___, ",
            r" {-,-} ",
            r" /)_)  ",
            r'  " "  ',
        ],
    },
    "ghost": {
        "art": [
            r" .-. ",
            r"(o o)",
            r"| O |",
            r"'~~~'",
        ],
    },
    "robot": {
        "art": [
            r" [#_#] ",
            r" /|=|\ ",
            r"  | |  ",
            r" _| |_ ",
        ],
        "blink": [
            r" [-_-] ",
            r" /|=|\ ",
            r"  | |  ",
            r" _| |_ ",
        ],
    },
    "bird": {
        "art": [
            r" __     ",
            r"<o )___ ",
            r" \ <_  )",
            r'  `-=="`',
        ],
    },
    "snail": {
        "art": [
            r"     _@/  ",
            r" ___(_)   ",
            r"(_______) ",
        ],
    },
    "rocket": {
        "art": [
            r"   /\   ",
            r"  /  \  ",
            r" |    | ",
            r" |asci| ",
            r" |    | ",
            r"/______\\",
            r" /|||\\ ",
            r"  ^^^   ",
        ],
    },
    "heart": {
        "art": [
            r" __  __ ",
            r"/  \/  \\",
            r"\      /",
            r" \    / ",
            r"  \  /  ",
            r"   \/   ",
        ],
    },
    # The reference's "9-bug" mascot, rebuilt from keyboard symbols.
    "bug9": {
        "art": [
            r"  (   )  ",
            r"   | |   ",
            r" \ ___ / ",
            r"=( /9\ )=",
            r" ( \_/ ) ",
            r"  /   \  ",
        ],
    },
}

def _art(block):
    """Triple-quoted block -> list of lines (trims a leading/trailing blank)."""
    lines = block.split("\n")
    if lines and lines[0] == "":
        lines = lines[1:]
    while lines and lines[-1].strip() == "":
        lines = lines[:-1]
    return lines


# Backfill category + description for the original sprites.
_BACKFILL = {
    "bunny": ("animal", "兔子"), "frog": ("animal", "青蛙"),
    "frog_big": ("animal", "大青蛙(带腿)"), "cat": ("animal", "猫"),
    "turtle": ("animal", "乌龟"), "dog": ("animal", "小狗(侧面)"),
    "fish": ("animal", "小鱼"), "fish_school": ("animal", "鱼群"),
    "owl": ("animal", "猫头鹰"), "ghost": ("face", "幽灵"),
    "robot": ("face", "机器人"), "bird": ("animal", "小鸟"),
    "snail": ("animal", "蜗牛"), "rocket": ("object", "火箭"),
    "heart": ("object", "爱心"), "bug9": ("tech", "9号瓢虫吉祥物"),
}
for _n, (_c, _d) in _BACKFILL.items():
    if _n in _SPRITES:
        _SPRITES[_n].setdefault("cat", _c)
        _SPRITES[_n].setdefault("desc", _d)


# ---------------------------------------------------------------------------
# Expanded library.  All pure-ASCII so any monospace font renders them.
# Faces with eyes ship a "blink" frame (use idle="blink").
# ---------------------------------------------------------------------------
_SPRITES.update({
    # ----- animals -----------------------------------------------------
    "puppy": {"cat": "animal", "desc": "小狗脸", "art": _art(r"""
 /^-^\
( o.o )
 > w <
"""), "blink": _art(r"""
 /^-^\
( -.- )
 > w <
""")},
    "kitten": {"cat": "animal", "desc": "小猫脸", "art": _art(r"""
 /\_/\
(=o.o=)
 (")_(")
"""), "blink": _art(r"""
 /\_/\
(=-.-=)
 (")_(")
""")},
    "bear": {"cat": "animal", "desc": "小熊", "art": _art(r"""
(\.-./)
( o.o )
 (  v  )
  '~~~'
"""), "blink": _art(r"""
(\.-./)
( -.- )
 (  v  )
  '~~~'
""")},
    "panda": {"cat": "animal", "desc": "熊猫", "art": _art(r"""
 .--.--.
( o  o )
(   <  )
 '----'
"""), "blink": _art(r"""
 .--.--.
( -  - )
(   <  )
 '----'
""")},
    "pig": {"cat": "animal", "desc": "小猪", "art": _art(r"""
 .---.
( o.o )
( -O- )
 '---'
"""), "blink": _art(r"""
 .---.
( -.- )
( -O- )
 '---'
""")},
    "mouse": {"cat": "animal", "desc": "老鼠", "art": _art(r"""
(o)_(o)
( o.o )
 '> <'
"""), "blink": _art(r"""
(o)_(o)
( -.- )
 '> <'
""")},
    "fox": {"cat": "animal", "desc": "狐狸", "art": _art(r"""
/\   /\
(  o.o  )
 )  ^  (
 (__ __)
"""), "blink": _art(r"""
/\   /\
(  -.-  )
 )  ^  (
 (__ __)
""")},
    "penguin": {"cat": "animal", "desc": "企鹅", "art": _art(r"""
 .--.
( oo )
(>  <)
/'  '\
 ^  ^
"""), "blink": _art(r"""
 .--.
( -- )
(>  <)
/'  '\
 ^  ^
""")},
    "duck": {"cat": "animal", "desc": "鸭子", "art": _art(r"""
  __
<o )___
 ( ._> /
  `---'
""")},
    "cow": {"cat": "animal", "desc": "奶牛", "art": _art(r"""
 ^__^
(oo)\_______
(__)\       )
    ||----w |
    ||     ||
"""), "blink": _art(r"""
 ^__^
(--)\_______
(__)\       )
    ||----w |
    ||     ||
""")},
    "sheep": {"cat": "animal", "desc": "绵羊", "art": _art(r"""
.-~~~-.
( o o  )
 \  ^  /
  '---'
"""), "blink": _art(r"""
.-~~~-.
( - -  )
 \  ^  /
  '---'
""")},
    "monkey": {"cat": "animal", "desc": "猴子", "art": _art(r"""
 .-"-.
(.o o.)
( =Y= )
 `---'
"""), "blink": _art(r"""
 .-"-.
(.- -.)
( =Y= )
 `---'
""")},
    "koala": {"cat": "animal", "desc": "考拉", "art": _art(r"""
@     @
 ( o.o )
  (   )
"""), "blink": _art(r"""
@     @
 ( -.- )
  (   )
""")},
    "lion": {"cat": "animal", "desc": "狮子", "art": _art(r"""
 ,@@@@@,
@( o o )@
 (  v  )
 @\___/@
"""), "blink": _art(r"""
 ,@@@@@,
@( - - )@
 (  v  )
 @\___/@
""")},
    "whale": {"cat": "animal", "desc": "鲸鱼", "art": _art(r"""
  .----.
 ( o    )><
  `----'~
""")},
    "dolphin": {"cat": "animal", "desc": "海豚", "art": _art(r"""
      __
   _.-~  ~-._
  (  o       >
   `-._____.-'
""")},
    "octopus": {"cat": "animal", "desc": "章鱼", "art": _art(r"""
 .-""-.
( o  o )
 `>  <`
 /|/|\|\
"""), "blink": _art(r"""
 .-""-.
( -  - )
 `>  <`
 /|/|\|\
""")},
    "crab": {"cat": "animal", "desc": "螃蟹", "art": _art(r"""
(V)(;,,;)(V)
""")},
    "snake": {"cat": "animal", "desc": "蛇", "art": _art(r"""
 _,.--.
( o.o   )
 `~~~~~~~>
"""), "blink": _art(r"""
 _,.--.
( -.-   )
 `~~~~~~~>
""")},
    "butterfly": {"cat": "animal", "desc": "蝴蝶", "art": _art(r"""
\    /
 (\../)
 //  \\
/    \
""")},
    "bee": {"cat": "animal", "desc": "蜜蜂", "art": _art(r"""
  __
 (oo)
\(  )/
 (==)
"""), "blink": _art(r"""
  __
 (--)
\(  )/
 (==)
""")},
    "dino": {"cat": "animal", "desc": "恐龙", "art": _art(r"""
       __
      / _)
.-^^^-/ /
__/    /
<__.|_|-|_|
""")},
    "hedgehog": {"cat": "animal", "desc": "刺猬", "art": _art(r"""
 \\|//
('o.o')
 `---`
"""), "blink": _art(r"""
 \\|//
('-.-')
 `---`
""")},
    "elephant": {"cat": "animal", "desc": "大象", "art": _art(r"""
  __
 /  \____
( o      \
 \    |~~~~
  \___|
"""), "blink": _art(r"""
  __
 /  \____
( -      \
 \    |~~~~
  \___|
""")},
    "bat": {"cat": "animal", "desc": "蝙蝠", "art": _art(r"""
=/\=(o.o)=/\=
""")},

    # ----- faces / people ----------------------------------------------
    "person": {"cat": "face", "desc": "小人(站立)", "art": _art(r"""
  O
 /|\
 / \
""")},
    "wave": {"cat": "face", "desc": "挥手的小人", "art": _art(r"""
\O
 |\
/ \
""")},
    "alien2": {"cat": "face", "desc": "外星人", "art": _art(r"""
 .---.
( o o )
( === )
 ^^ ^^
"""), "blink": _art(r"""
 .---.
( - - )
( === )
 ^^ ^^
""")},
    "skull": {"cat": "face", "desc": "骷髅头", "art": _art(r"""
 .---.
( x x )
 | ^ |
 'uuu'
""")},
    "smiley": {"cat": "face", "desc": "笑脸", "art": _art(r"""
 .---.
( ^ ^ )
(  u  )
 '---'
"""), "blink": _art(r"""
 .---.
( - - )
(  u  )
 '---'
""")},
    "cool": {"cat": "face", "desc": "墨镜酷脸", "art": _art(r"""
 .---.
[ - - ]
(  ~  )
 '---'
""")},
    "robot2": {"cat": "face", "desc": "方头机器人", "art": _art(r"""
 .-----.
 |o   o|
 | === |
 '-----'
  /| |\
"""), "blink": _art(r"""
 .-----.
 |-   -|
 | === |
 '-----'
  /| |\
""")},

    # ----- objects -----------------------------------------------------
    "star": {"cat": "object", "desc": "星星", "art": _art(r"""
 \ | /
'-(*)-'
 / | \
""")},
    "coffee": {"cat": "object", "desc": "咖啡杯", "art": _art(r"""
 ( (
  ) )
.____.
|    |]
\____/
""")},
    "tree": {"cat": "object", "desc": "松树", "art": _art(r"""
  /\
 /  \
/____\
  ||
""")},
    "flower": {"cat": "object", "desc": "花", "art": _art(r"""
 @
\|/
 |
\|/
""")},
    "house": {"cat": "object", "desc": "房子", "art": _art(r"""
  /\
 /  \
/____\
|  []|
|____|
""")},
    "car": {"cat": "object", "desc": "汽车", "art": _art(r"""
   ___
 _/   \__
|        |
'o------o'
""")},
    "boat": {"cat": "object", "desc": "帆船", "art": _art(r"""
   |
  /|
 / |
/__|__
\____/
~~~~~~
""")},
    "gift": {"cat": "object", "desc": "礼物盒", "art": _art(r"""
 _____
|_|_|_|
|     |
|_____|
""")},
    "crown": {"cat": "object", "desc": "皇冠", "art": _art(r"""
. . .
|\|/|
|   |
'---'
""")},
    "bulb": {"cat": "object", "desc": "灯泡", "art": _art(r"""
 .-.
(   )
 ) (
 |_|
""")},
    "sword": {"cat": "object", "desc": "剑", "art": _art(r"""
  /\
  ||
<>||<>
  ||
  \/
""")},
    "snowman": {"cat": "object", "desc": "雪人", "art": _art(r"""
 _==_
( o o )
( (") )
(  :  )
"""), "blink": _art(r"""
 _==_
( - - )
( (") )
(  :  )
""")},
    "mushroom": {"cat": "object", "desc": "蘑菇", "art": _art(r"""
.-~~~-.
/_______\
  |   |
  |___|
""")},
    "camera": {"cat": "object", "desc": "相机", "art": _art(r"""
 ___ __
|[O]  o|
|______|
""")},
    "laptop": {"cat": "object", "desc": "笔记本电脑", "art": _art(r"""
 ________
|  ____  |
| |    | |
|_|____|_|
\________/
""")},
    "mail": {"cat": "object", "desc": "信封", "art": _art(r"""
 ________
|\      /|
| \    / |
|  \  /  |
|___\/___|
""")},
    "balloon": {"cat": "object", "desc": "气球", "art": _art(r"""
 __
/  \
\  /
 \/
 '
""")},

    # ----- nature ------------------------------------------------------
    "sun": {"cat": "nature", "desc": "太阳", "art": _art(r"""
 \ | /
- (#) -
 / | \
""")},
    "moon": {"cat": "nature", "desc": "月亮", "art": _art(r"""
 ,-.
(   `.
 )   )
(   .'
 `-'
""")},
    "cloud": {"cat": "nature", "desc": "云", "art": _art(r"""
 .--.
(    )
(______)
""")},
    "rain": {"cat": "nature", "desc": "雨云", "art": _art(r"""
 .--.
(    )
(______)
 ' ' '
""")},
    "mountain": {"cat": "nature", "desc": "山", "art": _art(r"""
   /\
  /  \
 / /\ \
/_/  \_\
""")},
    "wave_sea": {"cat": "nature", "desc": "海浪", "art": _art(r"""
~^~^~^~^~
 ~^~^~^~
~^~^~^~^~
""")},

    # ----- tech / CLI --------------------------------------------------
    "folder": {"cat": "tech", "desc": "文件夹", "art": _art(r"""
 ____
/    \____
|         |
|_________|
""")},
    "terminal": {"cat": "tech", "desc": "终端窗口", "art": _art(r"""
 __________
| $ _      |
|          |
|__________|
""")},
    "wifi": {"cat": "tech", "desc": "WiFi 信号", "art": _art(r"""
((( o )))
 (( o ))
  ( o )
""")},
    "battery": {"cat": "tech", "desc": "电池", "art": _art(r"""
 ______
|####  |]
|####  |]
'------'
""")},
    "atom": {"cat": "tech", "desc": "原子", "art": _art(r"""
 ,-~-.
( (o) )
 `-~-'
""")},
    "cube": {"cat": "tech", "desc": "立方体", "art": _art(r"""
 ____
/   /|
/___/ |
|   | /
|___|/
""")},
    "code": {"cat": "tech", "desc": "代码框", "art": _art(r"""
 _______
| </>   |
|  {}   |
|_______|
""")},
})


# ---------------------------------------------------------------------------
# Block-letter banner font (5 rows tall).  Renders big character-art words.
# ---------------------------------------------------------------------------
_BLOCK = {
    "A": ["███", "█ █", "███", "█ █", "█ █"],
    "B": ["██ ", "█ █", "██ ", "█ █", "██ "],
    "C": ["███", "█  ", "█  ", "█  ", "███"],
    "D": ["██ ", "█ █", "█ █", "█ █", "██ "],
    "E": ["███", "█  ", "██ ", "█  ", "███"],
    "F": ["███", "█  ", "██ ", "█  ", "█  "],
    "G": ["███", "█  ", "█ █", "█ █", "███"],
    "H": ["█ █", "█ █", "███", "█ █", "█ █"],
    "I": ["███", " █ ", " █ ", " █ ", "███"],
    "J": ["███", "  █", "  █", "█ █", "███"],
    "K": ["█ █", "██ ", "█  ", "██ ", "█ █"],
    "L": ["█  ", "█  ", "█  ", "█  ", "███"],
    "M": ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
    "N": ["█  █", "██ █", "█ ██", "█  █", "█  █"],
    "O": ["███", "█ █", "█ █", "█ █", "███"],
    "P": ["███", "█ █", "███", "█  ", "█  "],
    "Q": ["███", "█ █", "█ █", "███", "  █"],
    "R": ["███", "█ █", "██ ", "█ █", "█ █"],
    "S": ["███", "█  ", "███", "  █", "███"],
    "T": ["███", " █ ", " █ ", " █ ", " █ "],
    "U": ["█ █", "█ █", "█ █", "█ █", "███"],
    "V": ["█ █", "█ █", "█ █", "█ █", " █ "],
    "W": ["█   █", "█   █", "█ █ █", "██ ██", "█   █"],
    "X": ["█ █", "█ █", " █ ", "█ █", "█ █"],
    "Y": ["█ █", "█ █", " █ ", " █ ", " █ "],
    "Z": ["███", "  █", " █ ", "█  ", "███"],
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", " █ ", " █ ", " █ "],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    " ": ["  ", "  ", "  ", "  ", "  "],
    "!": [" █ ", " █ ", " █ ", "   ", " █ "],
    "?": ["███", "  █", " ██", "   ", " █ "],
    ".": ["   ", "   ", "   ", "   ", " █ "],
    ",": ["   ", "   ", "   ", " █ ", "█  "],
    ":": ["   ", " █ ", "   ", " █ ", "   "],
    "-": ["   ", "   ", "███", "   ", "   "],
    "+": ["   ", " █ ", "███", " █ ", "   "],
    "/": ["  █", "  █", " █ ", "█  ", "█  "],
    ">": ["█  ", " █ ", "  █", " █ ", "█  "],
    "<": ["  █", " █ ", "█  ", " █ ", "  █"],
    "*": ["█ █", " █ ", "█ █", "   ", "   "],
    "_": ["   ", "   ", "   ", "   ", "███"],
    "[": ["██", "█ ", "█ ", "█ ", "██"],
    "]": ["██", " █", " █", " █", "██"],
}


def names():
    return sorted(_SPRITES.keys())


def categories():
    """Sorted list of category names present in the library."""
    return sorted({s.get("cat", "misc") for s in _SPRITES.values()})


def names_by_category():
    """{category: [name, ...]} for browsing/selection."""
    out = {}
    for n, s in _SPRITES.items():
        out.setdefault(s.get("cat", "misc"), []).append(n)
    for k in out:
        out[k].sort()
    return out


def info(name):
    """{'name','cat','desc','blink','art'} for one sprite (or None)."""
    s = _SPRITES.get(name)
    if not s:
        return None
    return {"name": name, "cat": s.get("cat", "misc"),
            "desc": s.get("desc", ""), "blink": "blink" in s,
            "art": list(s["art"])}


def register(name, art, blink=None, cat="custom", desc=""):
    """Add a sprite at runtime so it can be used via sprite(name).

    ``art`` / ``blink`` may be a multi-line string or a list of lines.
    """
    def norm(a):
        lines = a.split("\n") if isinstance(a, str) else list(a)
        if lines and lines[0] == "":
            lines = lines[1:]
        while lines and lines[-1].strip() == "":
            lines = lines[:-1]
        return lines
    entry = {"art": norm(art), "cat": cat, "desc": desc}
    if blink:
        entry["blink"] = norm(blink)
    _SPRITES[name] = entry
    return name


def get(name):
    """Return the sprite's lines (list of str). Falls back to a '?' box."""
    s = _SPRITES.get(name)
    if not s:
        return ["[?]"]
    return list(s["art"])


def blink(name):
    """Return the blink-frame lines, or the normal art if none exists."""
    s = _SPRITES.get(name)
    if not s:
        return ["[?]"]
    return list(s.get("blink", s["art"]))


def has_blink(name):
    s = _SPRITES.get(name)
    return bool(s and "blink" in s)


def banner(text, fill="█", gap=1):
    """Render text as 5-row block letters. Returns a list of 5 strings."""
    text = text.upper()
    rows = ["", "", "", "", ""]
    sep = " " * gap
    for idx, ch in enumerate(text):
        glyph = _BLOCK.get(ch, _BLOCK["?"])
        for r in range(5):
            rows[r] += glyph[r]
            if idx != len(text) - 1:
                rows[r] += sep
    if fill != "█":
        rows = [r.replace("█", fill) for r in rows]
    return rows
