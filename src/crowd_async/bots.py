"""Various Bot implementations, each Bot following its own distinct logic"""
import math
import random
import asyncio

import arcade
from arcade.utils import _Vec2

from common import utl


class Bot(arcade.Sprite):
    """Simple bot that moves in the direction of its given angle"""
    def __init__(self, x, y, bots, color):
        super().__init__()
        self.debug = False
        self.bots = bots
        self.center_x = x
        self.center_y = y
        self.angle = 0.0
        self.orig_x: float = 0
        self.orig_y: float = 0
        self.is_blocked: bool = False
        square_texture = arcade.make_soft_square_texture(10, color, 255, 255)
        self.append_texture(square_texture)
        self.set_texture(0)

    def pos(self) -> _Vec2:
        """Convenience method to return current sprite position as a Vector"""
        return _Vec2(self.center_x, self.center_y)

    def set_goal(self, goal: _Vec2) -> None:
        self.angle = utl.angle_between(self.pos(), goal)

    def step_forward(self, dist):
        self.center_x += math.cos(self.radians) * dist
        self.center_y += math.sin(self.radians) * dist

    def save_pos(self):
        self.orig_x = self.center_x
        self.orig_y = self.center_y

    def restore_pos(self):
        self.center_x = self.orig_x
        self.center_y = self.orig_y

    def update(self):
        super().update()
        self.save_pos()
        if not self.is_blocked:
            self.step_forward(2.0)
        overlaps = self.collides_with_list(self.bots)
        if len(overlaps) > 0:  # if movement would have this Sprite overlap another Sprite, cancel movement
            self.restore_pos()


class AsyncBot(Bot):
    """A very rough initial attempt at creating an async bot"""
    def __init__(self, x, y, bots, color):
        super().__init__(x, y, bots, color)
        self.task = asyncio.create_task(self.async_update())

    async def async_update(self):
        dly = 0.5
        while True:
            self.angle = 0
            await asyncio.sleep(dly)
            self.angle = 90
            await asyncio.sleep(dly)
            self.angle = 45
            await asyncio.sleep(dly)

class StationaryBot(Bot):
    """A Bot that just stays in one place (for creating obstacles, etc)"""
    def update(self):
        pass


class OctWalkBot(Bot):
    """Bot walks in an octagon path"""
    def __init__(self, x, y, bots, color):
        super().__init__(x, y, bots, color)
        self.frame_count = 0

    def update(self):
        super().update()
        self.frame_count += 1
        if self.frame_count > 20:
            self.frame_count = 0
            self.angle += 45


class RandomWalkBot(Bot):
    """Bot walks in random directions for random lengths of time"""
    def __init__(self, x, y, bots, color):
        super().__init__(x, y, bots, color)
        self.frame_count = 0
        self.next_change_frame = 0

    def update(self):
        self.frame_count += 1
        if self.frame_count > self.next_change_frame:
            self.frame_count = 0
            self.next_change_frame = random.randint(10, 20)
            self.angle = random.randint(0, 360)
        super().update()


class BounceBot(Bot):
    """Bot that reverses direction with it touches another Bot"""
    def update(self):
        self.save_pos()
        if not self.is_blocked:
            self.step_forward(2.0)
        overlaps = self.collides_with_list(self.bots)
        if len(overlaps) > 0:  # if movement would have this Sprite overlap another Sprite, cancel movement and reflect
            self.restore_pos()
            self.angle += 180


class RunAwayBot(Bot):
    """Moves slowly. When it gets bumped, it runs away quickly then stops. After a time it moves again."""
    def __init__(self, x, y, bots, color):
        super().__init__(x, y, bots, color)
        self.state = 'normal'
        self.frame_count = 0
        self.angle = 180

    def update(self):
        self.save_pos()
        if self.state == "bumped" and self.frame_count <= 0:
            self.state = "waiting"
            self.frame_count = 60
        elif self.state == "waiting":
            self.frame_count -= 1
            if self.frame_count <= 0:
                self.state = "normal"
                self.angle += 180
        if self.state != "waiting" and not self.is_blocked:
            if self.state == "normal":
                self.step_forward(1.0)
            elif self.state == "bumped":
                self.step_forward(5.0)
                self.frame_count -= 1
        overlaps = self.collides_with_list(self.bots)
        if len(overlaps) > 0:  # if movement would have this Sprite overlap another Sprite, cancel movement and reflect
            self.restore_pos()
            self.angle += 180
            self.state = 'bumped'
            self.frame_count = 15
