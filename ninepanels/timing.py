import re

from collections import deque
from collections import defaultdict

from datetime import datetime

from . import pydmodels as pyd
from . import queues



pattern = re.compile(r"(?<=/)\d+(?=/|$)")

def replace_numbers_in_path(path: str) -> str:
    return pattern.sub("x", path)

class Timer:

    """single, ephemeral per request"""

    def __init__(
        self, factory: object, method: str, request_id: str, path: str
    ) -> None:
        self.request_id = request_id
        self.path = path
        self.method = method
        self.start_ts: datetime = None
        self.stop_ts: datetime = None
        self.factory = factory

        self.diff_ms: float = None
        self.is_running: bool = False

    def start(self):
        self.start_ts = datetime.utcnow()
        self.is_running = True

    async def stop(self) -> float:
        self.stop_ts = datetime.utcnow()
        self.is_running = False
        diff_timedelta = self.stop_ts - self.start_ts

        self.diff_ms: float = diff_timedelta.total_seconds() * 1000
        self.factory.update(
            method_path=f"{self.method}_{self.path}", request_id=self.request_id
        )

        timing_payload = {
            "request_id": self.request_id,
            "method": self.method,
            "path": self.path,
            "start_ts": self.start_ts,
            "stop_ts": self.stop_ts,
            "diff_ms": self.diff_ms,
        }

        timing_event = pyd.Event(
            type="timer_completed",
            payload=timing_payload
        )

        await queues.event_queue.put(timing_event)



class TimerFactory:
    timers = {}
    stats = {}

    window_size = 100
    alert_thresholds = {
        "GET_/": 10,
        "GET_/users": 20,
        "GET_/panels": 40,
        "GET_/admin/performance/route": 10,
        "POST_/panels/x": 50,
        "POST_/panels/x/entries": 40,
        "PATCH_/panels/x": 40,
        "DELETE_/panels/x": 40,
        "DELETE_/panels/x/entries": 40,
        "POST_/token": 500,
        "GET_/docs": 10,
        "GET_/openapi.json": 40
    }
    alert_threshold = 40

    def __init__(self) -> None:
        self.readings =  defaultdict(lambda: deque([], maxlen=self.window_size))
        self.request_ids = deque([], maxlen=self.window_size)
        self.component_timers = deque([], maxlen=self.window_size)

    def create_timer(self, request_id, method, path) -> Timer:
        path = replace_numbers_in_path(path)
        method_path = f"{method}_{path}"

        timer = Timer(factory=self, method=method, request_id=request_id, path=path)

        if method_path not in self.timers:
            self.timers[method_path] = deque(maxlen=self.window_size)
            self.timers[method_path].append(timer)
        else:
            self.timers[method_path].append(timer)
        return timer

    def update(self, method_path, request_id):
        path_timer_stats = {}
        times = [
            i.diff_ms
            for i in self.timers[method_path]
            if not i.is_running and i.diff_ms
        ]
        if times:
            path_timer_stats = {
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "last": times[len(times) - 1],
            }

            self.stats[method_path] = path_timer_stats

            reading = {
                "timestamp": datetime.utcnow(),
                "request_id": request_id,
                "reading": path_timer_stats["last"],
            }
            self.readings[method_path].append(reading)
            self.request_ids.append(reading)

        self.assess_performance()

    def assess_performance(self):
        for method_path in self.stats:
            if method_path in self.alert_thresholds:
                self.alert_threshold = self.alert_thresholds[method_path]

            self.stats[method_path]["alert_threshold"] = self.alert_threshold
            self.stats[method_path]["in_alert"] = False

            if self.stats[method_path]["avg"] > self.alert_threshold:
                self.stats[method_path]["in_alert"] = True
                # TODO logging and monitoring code here

    @property
    def route_performance(self) -> list[dict]:
        output = []


        for method_path in self.stats:
            ts_arr = []
            req_arr = []
            read_arr = []
            for mp_reading in self.readings[method_path]:
                ts_arr.append(mp_reading['timestamp'])
                req_arr.append(mp_reading['request_id'])
                read_arr.append(mp_reading['reading'])

            reading_out = {
                'timestamp': ts_arr,
                'request_id': req_arr,
                'reading': read_arr
            }

            method, path = method_path.split("_")
            output.append(
                {
                    "id": method_path,
                    "method": method,
                    "path": path,
                    "stats": self.stats[method_path],
                    "readings": reading_out
                }
            )





        return output

    @property
    def request_performance(self) -> list[dict]:
        return self.request_ids