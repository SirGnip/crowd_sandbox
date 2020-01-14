import math

from arcade.utils import _Vec2


def cycler(items):
    """Generator-based iterator that returns items in order, cycling to front of list when done."""
    if len(items) == 0:
        raise IndexError("Empty sequence was provided")
    idx = 0
    while True:
        yield items[idx]
        idx += 1
        if idx >= len(items):
            idx = 0


class Cycler:
    """Class that cycles through items in a sequence, remembering the last value returned.

    On initialization, the first value in the cycle is pre-loaded.

    NOTE: This is NOT an iterator. If you want an iterator, use the "cycler" generator function."""
    def __init__(self, items):
        if len(items) == 0:
            raise IndexError("Empty sequence was provided")
        self.cycler = cycler(items)
        self.current = next(self.cycler)

    def get(self):
        return self.current

    def next(self):
        self.current = next(self.cycler)
        return self.current


def angle_between(a: _Vec2, b: _Vec2):
    """Given two points, return the angle between them"""
    delta = b - a
    rad = math.atan2(delta.y, delta.x)
    return math.degrees(rad)
