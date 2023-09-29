from sqlalchemy import desc

from . import pydmodels as pyd
from . import sqlmodels as sql
from . import queues
from . import event_types

from pprint import PrettyPrinter

pp = PrettyPrinter()


def insert_timing(timer_dict: dict):
    from . import database

    db = database.SessionLocal()

    timing = sql.Timing(**timer_dict)
    db.add(timing)
    db.commit()

    return timing


async def calculate_stats(window_size: int | None = None) -> dict:
    """ "

    Returns:
        dict of form {
            method_path: {stats for method path}
            }

    """
    from . import database

    db = database.SessionLocal()

    if window_size:
        window = window_size
    else:
        window = 10

    method_paths = db.query(sql.Timing.method_path).distinct().all()

    method_path_stats = {}

    for method_path in method_paths:
        mp = method_path[0]
        mp_result = (
            db.query(sql.Timing)
            .filter(sql.Timing.method_path == mp)
            .order_by(desc(sql.Timing.created_at))
            .limit(window)
            .all()
        )

        method_path_stats[mp] = {
            "readings": [timer.diff_ms for timer in mp_result],
            "timestamps": [timer.created_at for timer in mp_result],
        }

        avg = sum(method_path_stats[mp]["readings"]) / len(
            method_path_stats[mp]["readings"]
        )
        method_path_stats[mp].update({"avg": avg})

        minimum = min(method_path_stats[mp]["readings"])
        method_path_stats[mp].update({"min": minimum})

        maximum = max(method_path_stats[mp]["readings"])
        method_path_stats[mp].update({"max": maximum})

        last = method_path_stats[mp]["readings"][0]
        method_path_stats[mp].update({"last": last})

    # TODO move this to a db table so that thresholds can be updated via the API
    alert_thresholds = {
        "GET_/": 10,
        "GET_/users": 60,
        "GET_/panels": 60,
        "GET_/admin/performance/route": 60,
        "GET_/metrics/panels/consistency": 60,
        "POST_/panels/x": 60,
        "POST_/panels/x/entries": 60,
        "PATCH_/panels/x": 60,
        "DELETE_/panels/x": 60,
        "DELETE_/panels/x/entries": 60,
        "POST_/token": 500,
        "GET_/docs": 60,
        "GET_/openapi.json": 60,
    }
    alert_threshold = 100

    for method_path in method_path_stats:

        alert_threshold = alert_thresholds.get(method_path, alert_threshold)

        method_path_stats[method_path].update({"alert_threshold": alert_threshold})
        method_path_stats[method_path].update({"in_alert": False})

        if method_path_stats[method_path]["avg"] > alert_threshold:
            method_path_stats[method_path].update({"in_alert": True})
            await queues.event_queue.put(
                pyd.Event(
                    type=event_types.TIMING_ALERT,
                    payload={"method_path": method_path, "stats": method_path_stats[method_path]},
                )
            )

    return method_path_stats


async def timing_event_handler(event: pyd.Event):
    timer_dict = event.payload.__dict__

    # persist to 'timings' table
    # TODO exc handling here
    timing = insert_timing(timer_dict)

    # process stats and produce stats payload if timing insert successful
    if timing:
        method_path_stats = await calculate_stats()

    await queues.event_queue.put(
        pyd.Event(type=event_types.TIMING_PROCESSED, payload=method_path_stats)
    )
