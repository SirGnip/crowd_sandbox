"""
ABANDONED and INCOMPLETE multiprocessing version.

Was planning on doing the collision tests in a worker process, returning it and caching the results on the
game object. Didn't work because there was pickling exceptions thrown when trying to queue.put() the self.bots
list. Seems like the data in question only got added after init was complete (first update? first draw?) as
sending the self.bots via arg to Process ctor worked fine at the beginning of the app.

SUMMARY: Simple crowd simulation. Multiple "Bots" with different logic that controls them.

Observation: It is common for Bots to deadlock against each other and stop moving. It isn't worth making more
sophisticated collision resolution logic as this is just an experiment.
"""
import random
import sys
import time
import statistics
import random
import multiprocessing
from typing import Optional

import arcade
from arcade.utils import _Vec2

from crowd_multiproc import bots
from common.fpsscanner import FpsScanner
from common import utl
from common.fpscounter import FpsCounter
from common.timer import Timer


def worker_run(queue, bots):
    print('worker starting...')
    print('got bots', bots)
    while True:
        bots = queue.get(block=True, timeout=5.0)
        result = {}
        # for bot in bots[:5]:
        #     colliding = bot.collides_with_list(self.bots)
        #     result[bot] = len(colliding)
        # queue.put(result, block=True, timeout=5.0)
        # print('worker just got msg:', msg)
        # while True:
        #
        # msg = 'MSG' + random.randint(0, 10)
        # queue.put(msg, True, 5.0)
        # time.sleep(0.0001)
    print('worker ending...')


class MyGame(arcade.Window):
    def __init__(self):
        self.times_init = []
        self.times_draw = []
        self.times_update = []
        self.total_timer = Timer()
        self.total_timer.start()

        with Timer() as init_timer:
            self.cnt = 0
            super().__init__(800, 600, sys.argv[0])  # update_rate=1/60
            self.paused = False
            self.frame_advance = False
            self.sleep: Optional[float] = None
            self.click_mode = 'goal'
            self.clicked_bot = None
            self.scanner = FpsScanner()
            self.fps = FpsCounter(120)
            self.bots = arcade.SpriteList()
            self.bot_factories = utl.Cycler((
                (arcade.color.RED, bots.Bot),
                (arcade.color.DARK_GRAY, bots.StationaryBot),
                (arcade.color.YELLOW, bots.OctWalkBot),
                (arcade.color.GREEN, bots.RandomWalkBot),
                (arcade.color.BLUE, bots.BounceBot),
                (arcade.color.PURPLE, bots.RunAwayBot),
            ))

            goal = _Vec2(700, 300)
            seq = 0
            for x in range(50, 150, 25):
                for y in range(50, 550, 25):
                    b = bots.Bot(x, y, self.bots, arcade.color.RED)
                    b.id = seq
                    seq += 1
                    b.set_goal(goal)
                    self.bots.append(b)
            self.bots[9].angle = 355

            self.bots.append(bots.OctWalkBot(400, 300, self.bots, arcade.color.YELLOW))
            self.bots.append(bots.RunAwayBot(500, 350, self.bots, arcade.color.PURPLE))
            self.bots.append(bots.RunAwayBot(475, 340, self.bots, arcade.color.PURPLE))

            for x in range(550, 650, 25):
                for y in range(450, 550, 25):
                    self.bots.append(bots.RandomWalkBot(x, y, self.bots, arcade.color.GREEN))

            for x in (500, 600, 625, 650, 700):
                b = bots.BounceBot(x, 300, self.bots, arcade.color.BLUE)
                b.angle = 180
                self.bots.append(b)

            for y in range(200, 400, 20):
                self.bots.append(bots.StationaryBot(723, y, self.bots, arcade.color.DARK_GRAY))

            print(f'There are {len(self.bots)} starting Bots')

        self.times_init.append(init_timer.last_elapsed)

        self._create_worker()
        # Experimntal code to get ready to test if the results dict from the proc could be keyed into
        # with local bot objects.
        b1 = self.bots[0]
        b2 = self.bots[20]
        b3 = self.bots[100]
        self.colliding = {}
        self.colliding[b1] = 0
        self.colliding[b2] = 7
        self.colliding[b3] = 1
        print(self.colliding)
        print(self.colliding[b1], self.colliding[b2], self.colliding[b3])

    def _create_worker(self):
        self.worker_queue = multiprocessing.Queue()
        self.worker = multiprocessing.Process(target=worker_run, args=(self.worker_queue, self.bots), daemon=True)
        self.worker.start()

    def on_draw(self):
        with Timer(logger=None) as draw_timer:
            arcade.start_render()
            self.scanner.draw()
            self.bots.draw()
        self.times_draw.append(draw_timer.last_elapsed)

    def update(self, delta_time: float):
        # self.worker_queue.put(self.bots, block=True, timeout=5.0)
        # self.worker_queue.put(self.bots, block=True, timeout=5.0)
        # results = self.worker_queue.get(block=True, timeout=5.0)
        self._create_worker()
        with Timer(logger=None) as update_timer:
            self.fps.tick()
            if self.fps.is_ready():
                print('FPS', self.fps.get_fps())
            if not self.paused or self.frame_advance:
                if self.frame_advance:
                    self.frame_advance = False
                if self.sleep is not None:
                    time.sleep(self.sleep)
                self.scanner.update()
                self.bots.update()
        self.times_update.append(update_timer.last_elapsed)

    def on_key_press(self, symbol: int, modifiers: int):
        # pause
        if symbol == arcade.key.P:
            self.paused = not self.paused
        elif symbol == arcade.key.SPACE:
            self.frame_advance = True
        # frame rate sleeping
        elif symbol == arcade.key.KEY_0:
            self.sleep = None
        elif symbol == arcade.key.KEY_1:
            self.sleep = 0.02  # about 30 fps
        elif symbol == arcade.key.KEY_2:
            self.sleep = 0.1
        elif symbol == arcade.key.KEY_3:
            self.sleep = 1.0
        # click mode
        elif symbol == arcade.key.A:
            self.click_mode = 'add'
            if modifiers & arcade.key.MOD_SHIFT:  # Shift+A cycles through Bot factories
                self.bot_factories.next()
            print('Current Bot add factory: %s' % self.bot_factories.get()[1].__name__)
        elif symbol == arcade.key.G:
            if modifiers & arcade.key.MOD_SHIFT:
                self.click_mode = 'goal_reverse'
            else:
                self.click_mode = 'goal'
        elif symbol == arcade.key.D:
            self.click_mode = 'delete'
        # move
        elif symbol == arcade.key.M:
            self.click_mode = 'move'
            self.clicked_bot = None
        elif symbol == arcade.key.ESCAPE:
            self.on_closing()
            self.close()
        print('Mouse Click Mode:', self.click_mode)

    def _times_summary(self, tag, times):
        min_times = min(times)
        max_times = max(times)
        sum_times = sum(times)
        mode_times = statistics.mode(times)
        avg_times = statistics.mean(times)
        txt = '{} {:0.6f} {:0.6f} {:0.6f} {:0.6f} {:0.6f}'.format(tag, min_times, mode_times, avg_times, max_times, sum_times)
        print(txt)

    def on_closing(self):
        self._times_summary('init  ', self.times_init)
        self._times_summary('draw  ', self.times_draw)
        self._times_summary('update', self.times_update)
        print('total', self.total_timer.stop())

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        super().on_mouse_press(x, y, button, modifiers)
        print('mouse click', x, y, button)
        if button == 1:
            if self.click_mode in ('goal', 'goal_reverse'):
                print('changing goal')
                # change goal
                goal = _Vec2(x, y)
                for bot in [b for b in self.bots if type(b) is bots.Bot]:
                    bot.set_goal(goal)
                    if self.click_mode == 'goal_reverse':
                        bot.angle += 180
            elif self.click_mode == 'add':
                print('adding bot....')
                # add new bot
                clr, bot_factory = self.bot_factories.get()
                b = bot_factory(x, y, self.bots, clr)
                b.id = 999999
                self.bots.append(b)
            elif self.click_mode == 'delete':
                touched = arcade.get_sprites_at_point((x, y), self.bots)
                print('Removing', len(touched), 'Bots')
                for b in touched:
                    self.bots.remove(b)
            elif self.click_mode == 'move':
                touched = arcade.get_sprites_at_point((x, y), self.bots)
                if len(touched) > 0:
                    self.clicked_bot = touched[0]
        else:
            # set debugging flag on a bot
            touched = arcade.get_sprites_at_point((x, y), self.bots)
            for b in touched:
                print('  touched', b.id, b)
                b.debug = True

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        if self.clicked_bot is not None:
            self.clicked_bot.center_x = x
            self.clicked_bot.center_y = y


if __name__ == '__main__':
    random.seed(12345)  # repeatable randomness
    game = MyGame()
    game.set_location(600, 50)
    arcade.run()
