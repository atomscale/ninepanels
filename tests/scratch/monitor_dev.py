import time

import logging

from dataclasses import dataclass
from collections import deque
from datetime import datetime
from typing import Dict


class MonitorError(Exception):
    pass


class Monitor:

    """Calculate an average of monitored times and ensure over threshold results are logged and sent to monitoring.


    name: str of unique name
    window_size: int of timing events to average over
    alert_threshold: int of the monitored time in ms over which to trigger an alert


    """

    def __init__(self, name: str, window_size: int, alert_threshold: int) -> None:
        self.name = name
        self.window_size = window_size
        self.alert_threshold = alert_threshold

        self.running: bool = False
        self.readings: deque[float] = deque([], maxlen=self.window_size)
        self.start_ts: datetime = None
        self.stop_ts: datetime = None
        self.avg: float = None

    def start(self):
        self.running = True
        self.start_ts = datetime.utcnow()

    def stop(self):
        if not self.running:
            raise MonitorError(f"cannot stop as not started")
        self.running = False
        self.stop_ts = datetime.utcnow()
        self._measure()

    def _measure(self):
        if not self.start_ts:
            raise MonitorError(f"Monitor {self.name} has not started")
        if self.running == True:
            self.stop()

        diff_timedelta = self.stop_ts - self.start_ts

        diff_ms: float = diff_timedelta.total_seconds() * 1000
        self.readings.append(diff_ms)

        print(f"{self.name} {self.readings=}")

    def report(self):
        if len(self.readings) == self.window_size:
            self.avg = sum(self.readings) / len(self.readings)

            if self.avg > self.alert_threshold:
                return f"monitor name: `{self.name}` at avg {round(self.avg, 3)}ms, over threshold {self.alert_threshold}ms"


class MonitorFactory:
    _existing_monitors: Dict[str, Monitor] = {}

    @classmethod
    def create_monitor(
        cls, name: str, window_size: int, alert_threshold: int
    ) -> Monitor:
        if name not in cls._existing_monitors:
            cls._existing_monitors[name] = Monitor(
                name=name, window_size=window_size, alert_threshold=alert_threshold
            )
        else:
            raise MonitorError(f"monitor {name} already exists")
        return cls._existing_monitors[name]

    @classmethod
    def report_all(cls):
        for name, monitor in cls._existing_monitors.items():
            print(f"{name}: {monitor.report()}")


mf = MonitorFactory()

foo = mf.create_monitor(name="foo", window_size=2, alert_threshold=1000)
bar = mf.create_monitor(name="bar", window_size=1, alert_threshold=1000)

foo.start()
bar.start()

time.sleep(1)
foo.stop()

foo.start()
time.sleep(1)
foo.stop()

foo.start()
time.sleep(1)
foo.stop()
bar.avg
bar.stop()

for n, m in mf._existing_monitors.items():
    print(len(m.readings))

mf.report_all()
