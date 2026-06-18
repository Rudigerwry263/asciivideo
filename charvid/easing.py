"""Deterministic easing functions. All map t in [0,1] -> [0,1]."""
import math


def linear(t):
    return t


def ease_in(t):
    return t * t


def ease_out(t):
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out(t):
    return 2 * t * t if t < 0.5 else 1.0 - (-2 * t + 2) ** 2 / 2


def ease_out_cubic(t):
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1.0 - (-2 * t + 2) ** 3 / 2


def ease_out_quart(t):
    return 1.0 - (1.0 - t) ** 4


def ease_out_expo(t):
    return 1.0 if t >= 1.0 else 1.0 - 2 ** (-10 * t)


def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_elastic(t):
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


_REG = {
    "linear": linear,
    "ease_in": ease_in,
    "ease_out": ease_out,
    "ease_in_out": ease_in_out,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_out_quart": ease_out_quart,
    "ease_out_expo": ease_out_expo,
    "ease_out_back": ease_out_back,
    "ease_out_elastic": ease_out_elastic,
}


def get(name):
    if callable(name):
        return name
    return _REG.get(name, ease_out_cubic)


def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def lerp(a, b, t):
    return a + (b - a) * t
