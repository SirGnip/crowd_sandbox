# Minimal implementation of "central counter" in threaded fashion
# Run takes about 8 seconds
import threading
import time


class CentralCounter:
    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0

    def incr(self):
        time.sleep(0.0001)  # represents "local" work that doesn't need the lock
        with self.lock:
            cur = self.count
            time.sleep(0.0001)  # represents work on shared data
            cur += 1
            self.count = cur


def multi_countup(iters, ctr):
    for i in range(iters):
        ctr.incr()


def main():
    central_counter = CentralCounter()  # object shared by threads
    print('central counter init', central_counter.count)
    worker_count = 5
    iters = 100
    threads = [threading.Thread(target=multi_countup, args=(iters, central_counter), daemon=True) for t in range(worker_count)]

    [t.start() for t in threads]
    [t.join() for t in threads]

    print('central counter final', central_counter.count)


if __name__ == '__main__':
    import timeit
    print('time:', timeit.timeit(main, number=1))
