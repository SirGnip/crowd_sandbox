# Minimal implementation of "central counter" in multiprocessor fashion (using shared memory for shared state, not server manager)
# Run takes about 8 seconds
import multiprocessing
import time
from common.timer import Timer


def multi_countup(iters, central_counter, lock):
    proc = multiprocessing.current_process()
    print('worker', proc.name, proc.ident, proc._identity, id(central_counter))

    for i in range(iters):
        time.sleep(0.0001)  # represents "local" work that doesn't need the lock
        with lock:
            cur = central_counter.value
            time.sleep(0.0001)  # represents work on shared data
            cur += 1
            central_counter.value = cur


def main():
    with Timer() as t:
        central_counter = multiprocessing.Value('i', 0)  # "i" = signed integer
        lock = multiprocessing.Lock()
        print('central counter init', central_counter, central_counter.value)
        worker_count = 5
        iters = 100
    with Timer() as t:
        procs = [multiprocessing.Process(target=multi_countup, args=(iters, central_counter, lock), daemon=True) for p in range(worker_count)]
    with Timer() as t:
        print('starting', len(procs), 'threads with', iters, 'iterations each')
        [p.start() for p in procs]
    [p.join() for p in procs]

    print('central counter final', central_counter.value)


if __name__ == '__main__':
    # import timeit
    # print('time:', timeit.timeit(main, number=1))
    with Timer() as t:
        main()


