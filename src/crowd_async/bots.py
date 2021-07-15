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
        self.step_forward(self.speed)
        overlaps = self.collides_with_list(self.bots)
        if len(overlaps) > 0:  # if movement would have this Sprite overlap another Sprite, cancel movement
            self.restore_pos()
            self.on_collided()

    def on_collided(self):
        pass


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


class OctWalkBot(AsyncBot):
    """Uses frame counts with a custom coro, not sleep/time. More deterministic."""
    async def async_update(self):
        while True:
            await self.until_frames_elapsed(20)
            self.angle = (self.angle + 45) % 360


class RandomWalkBot(AsyncBot):
    """Bot walks in random directions for random lengths of time"""
    async def async_update(self):
        while True:
            self.angle = random.randint(0, 360)
            await self.until_frames_elapsed(random.randint(10, 20))


class BounceBot(Bot):
    """Bot that reverses direction with it touches another Bot"""
    def on_collided(self):
        self.angle += 180


class RunAwayBot(AsyncBot):
    """Moves slowly. When it gets bumped, it runs away quickly then stops. After a time it moves again."""
    async def async_update(self):
        self.angle = 180
        self.collided = False
        while True:
            # normal
            self.speed = 1.0
            await is_true(lambda: self.collided)
            self.collided = False

            # bumped
            self.speed = 5.0
            self.angle += 180
            await self.until_frames_elapsed(15)

            # waiting
            self.speed = 0.0
            self.angle += 180
            await self.until_frames_elapsed(60)

    def on_collided(self):
        self.collided = True


