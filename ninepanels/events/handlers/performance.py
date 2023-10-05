""" Classes and coroutine event handlers for application performance monitoring

"""

import uuid
import asyncio
import re

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from pprint import PrettyPrinter
from datetime import datetime

from ... import sqlmodels as sql
from ... import exceptions
from ... import utils
from .. import event_models


pp = PrettyPrinter()

pattern = re.compile(r"(?<=/)\d+(?=/|$)")


def replace_numbers_in_path(path: str) -> str:
    return pattern.sub("x", path)


class RouteTimer:
    """Ephemeral per request.

    Produces event_models.RouteTimingCreated
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
        self.method_path: event_models.MethodPath = f"{self.method}_{self.path}"

    def start(self) -> None:
        self.start_ts = datetime.utcnow()

    async def stop(self) -> None:

        from .. import queues

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
            diff_ms=self.diff_ms,
        )

        await queues.event_queue.put(timing_event)


class RouteTimingsBuffer:
    def __init__(
        self,
    ) -> None:
        self.buffers: dict[event_models.MethodPath : list[sql.Timing]] = {}
        self.batch_sizes: dict[event_models.MethodPath : int] = {}
        self.lock = asyncio.Lock()

    async def add_timing_to_buffer(
        self, timing: event_models.RouteTimingCreated
    ) -> bool:
        """Buffers `sql.Timing` instances  per `method_path`
        and flushes db writes when `batch_size` for `method_path` met.

        Returns:
            `method_path`: method_path of the buffer just flushed

        Raises:
            `exceptions.RouteTimerError`

        """
        async with self.lock:
            new_timing = sql.Timing(**timing.model_dump(exclude={"type"}))

            if timing.method_path in self.buffers:
                self.buffers[timing.method_path].append(new_timing)
            else:
                self.buffers[timing.method_path] = [
                    new_timing,
                ]

            batch_size = self.batch_sizes.get(timing.method_path, 10)

            if len(self.buffers[timing.method_path]) >= batch_size:
                try:
                    success = self._insert_timings(timing.method_path)
                    if success:
                        self.buffers[timing.method_path] = []
                        return success
                except exceptions.RouteTimerError:
                    raise

    def _insert_timings(self, method_path: event_models.MethodPath) -> bool:
        from ...db import database

        db = database.SessionLocal()

        try:
            db.add_all(self.buffers[method_path])
            db.commit()
            return method_path
        except SQLAlchemyError as e:
            db.rollback()
            raise exceptions.RouteTimerError(detail="error bd buffer flush")
        finally:
            db.close()


class RouteStatsProcessor:
    def __init__(self) -> None:
        self.last_alert_id = {}

    def performance_params(self, method_path: event_models.MethodPath) -> dict:
        """Supply the window_size and alert_thresholds per method_path

        Args:
            method_path

        Returns:
            dict of params

        """
        # TODO need to work out the mechanics to get this to a db, and be cient updatable?
        method_path_params = {
            "GET_/": {"window_size": 100, "alert_threshold_ms": 60},
            "GET_/users": {"window_size": 100, "alert_threshold_ms": 60},
            "GET_/panels": {"window_size": 100, "alert_threshold_ms": 60},
            "GET_/admin/performance/route": {
                "window_size": 100,
                "alert_threshold_ms": 60,
            },
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

        return params

    def calculate_stats_for_route(self, event: event_models.RouteTimingsPersisted):
        """FOR THE SINGLE EVENT ROUTE ONLY!!! makes sense now: a new row per method_path on timing persisted event"""

        from ...db import database

        db = database.SessionLocal()

        method_path = event.method_path
        method, path = method_path.split("_")

        params = self.performance_params(method_path=method_path)

        window_size = params["window_size"]
        alert_threshold_ms = params["alert_threshold_ms"]

        try:
            timings = (
                db.query(sql.Timing)
                .filter(sql.Timing.method_path == method_path)
                .order_by(desc(sql.Timing.created_at))
                .limit(window_size)
                .all()
            )
        except SQLAlchemyError as e:
            raise exceptions.RouteStatsProcessorError(
                detail="error getting timings from db",
                context_msg=str(e),
                context_data={"method_path": method_path},
            )
        finally:
            db.close()

        if not timings:
            raise exceptions.RouteStatsProcessorError(
                detail="no timings to process",
                context_data={"method_path": method_path},
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

        stats.update({"method": method})
        stats.update({"path": path})
        stats.update({"method_path": method_path})

        stats.update({"alert_threshold_ms": alert_threshold_ms})
        stats.update({"in_alert": False})
        stats.update({"alert_id": None})

        if stats["avg"] > alert_threshold_ms:
            stats.update({"in_alert": True})
            existing_alert_id = self.last_alert_id.get(method_path, None)

            if not existing_alert_id:
                alert_id = str(uuid.uuid4())
                self.last_alert_id[method_path] = {
                    "alert_id": alert_id,
                    "is_dispatched": False,
                }
                stats.update({"alert_id": alert_id})

        else:
            existing_alert_id = self.last_alert_id.get(method_path, None)
            if existing_alert_id:
                self.last_alert_id[method_path] = None

        try:
            db_stats = sql.TimingStats(**stats)
            db.add(db_stats)
            db.commit()
            return utils.instance_to_dict(db_stats)
        except SQLAlchemyError as e:
            raise exceptions.RouteStatsProcessorError(
                detail="error writing stats to db",
                context_msg=str(e),
                context_data={"method_path": method_path, "stats": stats},
            )
        finally:
            db.close()


route_timings_buffer = RouteTimingsBuffer()


async def handle_route_timing_created(event: event_models.RouteTimingCreated) -> None:
    """Coro to coordinated buffering and flushing of new route timing events

    Args:
        event: event_models.RouteTimingCreated - produced by `perforance.RouteTimer`

    """
    from .. import queues

    method_path = None

    try:
        method_path = await route_timings_buffer.add_timing_to_buffer(event)
    except exceptions.RouteTimerError as e:
        # await queues.event_queue.put(
        #     pyd.Event(type=event_types.EXC_RAISED_ERROR, payload=e)
        # )
        ...

    if method_path:
        # TODO produce an event_models.RouteTimingsPersisted event
        # print(f"produce an event_models.RouteTimingsPersisted event for {method_path}")

        await queues.event_queue.put(
            event_models.RouteTimingsPersisted(method_path=method_path)
        )


stats_processor = RouteStatsProcessor()


async def handle_route_timings_persisted(event: event_models.RouteTimingsPersisted):
    from .. import queues

    route_stats = await asyncio.to_thread(
        stats_processor.calculate_stats_for_route, event
    )

    print(f"route stats for {event.method_path} created: {route_stats}")
    # await queues.event_queue.put(
    #     pyd.Event(
    #         type=event_types.TIMING_STATS_PERSISTED,
    #         payload=stats,
    #     )
    # )

    # method_path = stats["method_path"]

    # if last_alert_id[method_path] and not last_alert_id[method_path]['is_dispatched']:
    #     await queues.event_queue.put(
    #         pyd.Event(
    #             type=event_types.TIMING_ALERT,
    #             payload=stats,
    #         )
    #     )
    #     last_alert_id[method_path]['is_dispatched'] = True
