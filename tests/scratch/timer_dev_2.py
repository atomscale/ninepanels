import time
from collections import deque
from datetime import datetime


class Timer:

    """single, ephemeral per request"""

    def __init__(self, factory: object, request_id: str, path: str) -> None:
        self._request_id = request_id
        self._path = path
        self._start_ts: datetime = None
        self._stop_ts: datetime = None
        self._factory = factory

        self.diff_ms: float = None
        self.is_running: bool = False

    def start(self):
        self._start_ts = datetime.utcnow()
        self.is_running = True

    def stop(self) -> float:
        self._stop_ts = datetime.utcnow()
        self.is_running = False
        diff_timedelta = self._stop_ts - self._start_ts

        self.diff_ms: float = diff_timedelta.total_seconds() * 1000
        self._factory.update(path=self._path)


class TimerFactory:
    timers = {}
    timings = {}

    def __init__(self, window_size: int):
        self.window_size = window_size

    def create_timer(self, request_id, path) -> Timer:
        # TODO singleton on request_id?
        timer = Timer(factory=self, request_id=request_id, path=path)
        if path not in self.timers:
            self.timers[path] = deque(maxlen=self.window_size)  # window_size
            self.timers[path].append(timer)
        else:
            self.timers[path].append(timer)
        return timer

    def update(self, path):
        path_timer_stats = {}
        times = [i.diff_ms for i in self.timers[path] if not i.is_running and i.diff_ms]
        if times:
            path_timer_stats = {
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
            }
            self.timings[path] = path_timer_stats
        self.monitor_performance()

    def monitor_performance(self):
        alert_thresholds = {"/": 350, "/users": 350}
        for path in self.timings:
            if self.timings[path]["avg"] > alert_thresholds[path]:
                print(f"path {path} would alert")
                # TODO logging and moniting code here

    @property
    def show_performance(self) -> list[dict]:
        output = []

        for path in self.timings:
            output.append({path: self.timings[path]})
        return output


timers = TimerFactory(window_size=10)

a = timers.create_timer("abcd", "/")
b = timers.create_timer("bcde", "/users")
c = timers.create_timer("cdef", "/")

# print()
# print("TIMERS:")
# a.start()
# time.sleep(2)
# a.stop()

# b.start()
# time.sleep(0.2)
# b.stop()

# c.start()
# time.sleep(1)
# c.stop()

print(timers.show_performance)
