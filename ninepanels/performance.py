import uuid
import asyncio
import threading

from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from . import pydmodels as pyd
from . import sqlmodels as sql
from . import queues
from . import event_types
from . import exceptions
from . import utils

from pprint import PrettyPrinter

pp = PrettyPrinter()


def insert_timing(timer_dict: dict):
    from . import database


    try:
        db = database.SessionLocal()
        timing = sql.Timing(**timer_dict)
        db.add(timing)
        db.commit()

    except SQLAlchemyError as e:
        raise exceptions.TimingError(
            detail="error in setting up db conneciton in persist timing "
        )

    return utils.instance_to_dict(timing)


async def handle_timing_created(event: pyd.Event):
    timer_dict = event.payload.__dict__


    try:
        timing = await asyncio.to_thread(insert_timing, timer_dict)
        await queues.event_queue.put(
            pyd.Event(type=event_types.TIMING_PERSISTED, payload=timing)
        )
    except exceptions.TimingError as e:
        await queues.event_queue.put(
            pyd.Event(type=event_types.EXC_RAISED_ERROR, payload=e)
        )


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
            last_alert_id[method_path] = alert_id
            stats.update({"alert_id": alert_id})

    else:
        existing_alert_id = last_alert_id.get(method_path, None)
        if existing_alert_id:
            last_alert_id[method_path] = None


    db_stats = sql.TimingStats(**stats)
    db.add(db_stats)
    db.commit()

    return utils.instance_to_dict(db_stats)


async def handle_timing_persisted(event: pyd.Event):
    stats = await asyncio.to_thread(calculate_stats_for_route, event)

    await queues.event_queue.put(
        pyd.Event(
            type=event_types.TIMING_STATS_PERSISTED,
            payload=stats,
        )
    )

    if stats["in_alert"]:
        await queues.event_queue.put(
            pyd.Event(
                type=event_types.TIMING_ALERT,
                payload=stats,
            )
        )


