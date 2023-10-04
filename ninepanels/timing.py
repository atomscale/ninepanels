import re

from datetime import datetime

from .events import queues
from .events import event_models


pattern = re.compile(r"(?<=/)\d+(?=/|$)")


def replace_numbers_in_path(path: str) -> str:
    return pattern.sub("x", path)


class RouteTimer:

    """single, ephemeral per request

    produces event_models.TimingCreated
    """

    def __init__(
        self,
        # factory: object,
        method: str,
        request_id: str,
        path: str,
    ) -> None:
        self.request_id = request_id
        self.path = replace_numbers_in_path(path)
        self.method = method
        self.start_ts: datetime = None
        self.stop_ts: datetime = None
        self.created_at = datetime.utcnow()
        self.diff_ms: float = None
        self.method_path: str = f"{self.method}_{self.path}"

    def start(self):
        self.start_ts = datetime.utcnow()

    async def stop(self) -> float:
        self.stop_ts = datetime.utcnow()

        diff_timedelta = self.stop_ts - self.start_ts

        self.diff_ms: float = diff_timedelta.total_seconds() * 1000

        # timing_event = pyd.Event(type=event_types.TIMING_CREATED, payload=self)
        timing_event = event_models.RouteTimingCreated(
            request_id=self.request_id,
            method_path=self.method_path,
            method=self.method,
            path=self.path,
            start_ts=self.start_ts,
            stop_ts=self.stop_ts,
            diff_ms=self.diff_ms
        )

        await queues.event_queue.put(timing_event)

