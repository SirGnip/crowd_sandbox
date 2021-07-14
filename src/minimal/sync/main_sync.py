# Minimal implementation of "central counter" in synchronous fashion
# Run takes about 15-16 seconds
#
# This "central counter" app is just an app that has a shared counter that is
# being incremented by multiple "workers" (Whatever the workers happen to be
# in a given implementation. Could be threads, processes, asyncio coroutines, etc).
# It is expected the "workers" will have some kind of concurrency, though in this
# specific synchronous example there is no concurrency. Everything is sequential.
import time


class CentralCounter:
    def __init__(self):
        self.count = 0

    def incr(self):
        time.sleep(0.0001)  # represents "local" work that doesn't need the lock
        cur = self.count
        time.sleep(0.0001)  # represents work on shared data
        cur += 1
        self.count = cur


def multi_countup(iters, ctr):
    for i in range(iters):
        ctr.incr()


def main():
    central_counter = CentralCounter()
    print('central counter init', central_counter.count)
    worker_count = 5
    iters = 100
    for c in range(worker_count):
        multi_countup(iters, central_counter)
    print('central counter final', central_counter.count)


if __name__ == '__main__':
    import timeit
    print('time:', timeit.timeit(main, number=1))

