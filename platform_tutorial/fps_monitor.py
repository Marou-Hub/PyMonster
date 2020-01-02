from collections import deque
from statistics import mean


class FpsMonitor:
    def __init__(self, max_size=100):
        self.queue = deque(maxlen=max_size)

    def update(self, delta_time):
        self.queue.append(delta_time)

    def __str__(self):
        if len(self.queue) == 0:
            return '-'
        return str(round(1/mean(self.queue), 2))
