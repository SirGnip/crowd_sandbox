# Minimal implementation of "central counter" with asyncio
# Run takes about 2 seconds
import asyncio


class CentralCounter:
    def __init__(self):
        self.count = 0

    async def incr(self):
        await asyncio.sleep(0.0002)  # represents waiting for work to complete
        cur = self.count
        # if `await asyncio.sleep` was here, the results would be incorrect because the coro was yielding while the data was in an inconsistent state.
        cur += 1
        self.count = cur


async def multi_countup(iters, ctr):
    for i in range(iters):
        await ctr.incr()


async def runner(how_many, iters, central_counter):
    tasks = [asyncio.create_task(multi_countup(iters, central_counter)) for t in range(how_many)]
    results = await asyncio.gather(*tasks)


def main():
    central_counter = CentralCounter()
    print('central counter init', central_counter.count)
    counter_count = 5
    iters = 100
    asyncio.run(runner(counter_count, iters, central_counter))
    print('central counter final', central_counter.count)


if __name__ == '__main__':
    import timeit
    print('time:', timeit.timeit(main, number=1))

