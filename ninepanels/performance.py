import uuid
import asyncio
import re

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from pprint import PrettyPrinter
from datetime import datetime

from . import pydmodels as pyd
from . import sqlmodels as sql
from . import queues
from . import event_types
from . import exceptions
from . import utils
from . import event_models


pp = PrettyPrinter()

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

class RouteTimingBuffer:

    def __init__(self, batch_size: int = 10) -> None:
        self.buffer: list[sql.Timing] = []
        self.batch_size: int = batch_size

    def add_timing_to_buffer(self, timing: event_models.RouteTimingCreated):
        """ Buffers `sql.Timing` instances created from `event_models.RouteTimingCreated` events
        and flushes db writes when `batch_size` met.

        Returns:


        """

        new_timing = sql.Timing(**timing.model_dump(exclude={'type'}))
        self.buffer.append(new_timing)

        if len(self.buffer) >= self.batch_size:
            try:
                success = self._insert_timings()
                if success:
                    self.buffer = []
                    return success
            except exceptions.RouteTimerError:
                raise

    def _insert_timings(self) -> bool:
        from . import database
        db = database.SessionLocal()

        try:
            db.add_all(self.buffer)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise exceptions.RouteTimerError(
                detail="error in setting up db conneciton in persist timing"
            )
        finally:
            db.close()

route_timer_persist = RouteTimingBuffer()

async def handle_timing_created(event: event_models.RouteTimingCreated) -> None:


    success = await asyncio.to_thread(route_timer_persist.add_timing_to_buffer, event)

    if success:
        # TODO produce an event_models.RouteTimingsPersisted event
        print(f"produce an event_models.RouteTimingsPersisted event")

    # await queues.event_queue.put(
    #     event_models.RouteTimingsPersisted(

    #     )
    # )
    # except exceptions.TimingError as e:
    #     await queues.event_queue.put(
    #         pyd.Event(type=event_types.EXC_RAISED_ERROR, payload=e)
    #     )






last_alert_id = {}


def calculate_stats_for_route(event: pyd.Event):
    """FOR THE SINGLE EVENT ROUTE ONLY!!! makes sense now: a new row per method_path on timing persisted event"""


    from . import database

    db = database.SessionLocal()

    timing_in_db = event.payload

    method_path = timing_in_db["method_path"]

    # TODO need to work out the mechanics to get this to a db, and be cient updatable?
    method_path_params = {
        "GET_/": {"window_size": 100, "alert_threshold_ms": 60},
        "GET_/users": {"window_size": 100, "alert_threshold_ms": 60},
        "GET_/panels": {"window_size": 100, "alert_threshold_ms": 60},
        "GET_/admin/performance/route": {"window_size": 100, "alert_threshold_ms": 60},
        "GET_/metrics/panels/consistency": {
            "window_size": 100,
            "alert_threshold_ms": 60,
        },
        "POST_/panels/x": {"window_size": 100, "alert_threshold_ms": 60},
        "POST_/panels/x/entries": {"window_size": 100, "alert_threshold_ms": 60},
        "PATCH_/panels/x": {"window_size": 100, "alert_threshold_ms": 60},
        "DELETE_/panels/x": {"window_size": 100, "alert_threshold_ms": 60},
        "DELETE_/panels/x/entries": {"window_size": 100, "alert_threshold_ms": 60},
        "POST_/token": {"window_size": 100, "alert_threshold_ms": 500},
        "GET_/docs": {"window_size": 100, "alert_threshold_ms": 60},
        "GET_/openapi.json": {"window_size": 100, "alert_threshold_ms": 60},
    }

    default_params = {"window_size": 100, "alert_threshold_ms": 60}
    params = method_path_params.get(method_path, default_params)
    window_size = params["window_size"]
    alert_threshold_ms = params["alert_threshold_ms"]

    timings = (
        db.query(sql.Timing)
        .filter(sql.Timing.method_path == method_path)
        .order_by(desc(sql.Timing.created_at))
        .limit(window_size)
        .all()
    )

    stats = {}


    readings = [timer.diff_ms for timer in timings]

    avg = sum(readings) / len(readings)
    stats.update({"avg": avg})

    minimum = min(readings)
    stats.update({"min": minimum})

    maximum = max(readings)
    stats.update({"max": maximum})

    last = readings[0]
    stats.update({"last": last})

    stats.update({"method": timing_in_db["method"]})
    stats.update({"path": timing_in_db["path"]})
    stats.update({"method_path": method_path})

    stats.update({"alert_threshold_ms": alert_threshold_ms})
    stats.update({"in_alert": False})
    stats.update({"alert_id": None})

    if stats["avg"] > alert_threshold_ms:
        stats.update({"in_alert": True})
        existing_alert_id = last_alert_id.get(method_path, None)

        if not existing_alert_id:
            alert_id = str(uuid.uuid4())
            last_alert_id[method_path] = {'alert_id': alert_id, 'is_dispatched': False}
            stats.update({"alert_id": alert_id})

    else:
        existing_alert_id = last_alert_id.get(method_path, None)
        if existing_alert_id:
            last_alert_id[method_path] = None


    db_stats = sql.TimingStats(**stats)
    db.add(db_stats)
    db.commit()

    return utils.instance_to_dict(db_stats)


async def handle_timings_persisted(event: pyd.Event):
    stats = await asyncio.to_thread(calculate_stats_for_route, event)

    await queues.event_queue.put(
        pyd.Event(
            type=event_types.TIMING_STATS_PERSISTED,
            payload=stats,
        )
    )

    method_path = stats["method_path"]

    if last_alert_id[method_path] and not last_alert_id[method_path]['is_dispatched']:
        await queues.event_queue.put(
            pyd.Event(
                type=event_types.TIMING_ALERT,
                payload=stats,
            )
        )
        last_alert_id[method_path]['is_dispatched'] = True


