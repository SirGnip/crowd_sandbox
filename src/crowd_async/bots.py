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
        self.speed = 2.0
        self.orig_x: float = 0
        self.orig_y: float = 0
        self.is_blocked: bool = False
        self.set_color(color)

    def set_color(self, color):
        self.textures = []
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
            self.step_forward(self.speed)
        overlaps = self.collides_with_list(self.bots)
        if len(overlaps) > 0:  # if movement would have this Sprite overlap another Sprite, cancel movement
            self.restore_pos()


async def is_true(predicate):
    """utility coroutine that blocks until the given predicate evaluates to true, returning the argument."""
    try:
        while not predicate():
            await asyncio.sleep(0)
    except Exception as exc:
        # Try to make exception more obvious.
        # Very easy for a typo in a predicate to not generate a visible error (probably because I don't
        # understand coroutines/Tasks fully yet).
        print('ERROR! Exception in is_true:', exc)


class AsyncBot(Bot):
    def __init__(self, x, y, bots, color):
        super().__init__(x, y, bots, color)
        self.frames = 0
        self.task = asyncio.create_task(self.async_update())

    async def until_frames_elapsed(self, elapsed):
        end_at_frame = self.frames + elapsed
        while self.frames < end_at_frame:
            await asyncio.sleep(0)

    def update(self):
        super().update()
        self.frames += 1


class StationaryBot(Bot):
    """A Bot that just stays in one place (for creating obstacles, etc)"""
    def update(self):
        pass


class AsyncOctWalkBot(AsyncBot):
    """Uses frame counts with a custom coro, not sleep/time. More deterministic."""
    async def async_update(self):
        while True:
            await self.until_frames_elapsed(20)
            self.angle = (self.angle + 45) % 360


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
