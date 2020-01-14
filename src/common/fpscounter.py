import time


class FpsCounter:
    """Utility that calculates FPS"""
    def __init__(self, frame_interval=30):
        self.start: float
        self.frames: int
        self._reset()
        self.frame_interval = frame_interval

    def _reset(self):
        self.start = time.perf_counter()
        self.frames = 0

    def tick(self) -> None:
        self.frames += 1

    def get_fps(self) -> float:
        delta = time.perf_counter() - self.start
        fps = self.frames / delta
        self._reset()
        return fps

    def is_ready(self) -> bool:
        return self.frames > self.frame_interval
