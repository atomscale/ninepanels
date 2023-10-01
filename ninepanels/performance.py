import uuid
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

last_alert_id = {}



async def calculate_stats(window_size: int | None = None) -> dict:
    """

    Returns:
        dict of form {
            method_path: {stats for method path}
            }

    """
    from . import database

    db = database.SessionLocal()

    if window_size and window_size > 0:
        window = window_size
    else:
        window = 10

    method_paths = db.query(sql.Timing.method_path).distinct().all()

    output = []

    for method_path in method_paths:
        method_path_stats = {}
        mp = method_path[0]
        method_path_stats.update({"id": mp})
        mp_result = (
            db.query(sql.Timing)
            .filter(sql.Timing.method_path == mp)
            .order_by(desc(sql.Timing.created_at))
            .limit(window)
            .all()
        )

        method_path_stats.update({
            "readings": [timer.diff_ms for timer in mp_result],
            "timestamps": [timer.created_at for timer in mp_result],
        })

        avg = sum(method_path_stats["readings"]) / len(
            method_path_stats["readings"]
        )
        method_path_stats.update({"avg": avg})

        minimum = min(method_path_stats["readings"])
        method_path_stats.update({"min": minimum})

        maximum = max(method_path_stats["readings"])
        method_path_stats.update({"max": maximum})

        last = method_path_stats["readings"][0]
        method_path_stats.update({"last": last})


        method, path = method_path[0].split("_")
        method_path_stats.update({"method": method})
        method_path_stats.update({"path": path})

        # TODO move this to a db table so that thresholds can be updated via the API
        alert_thresholds = {
            "GET_/": 10,
            "GET_/users": 60,
            "GET_/panels": 40,
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

        # TODO move this to another handler for a timing_stats_persisted event or soemthing.
        alert_threshold = alert_thresholds.get(mp, alert_threshold)

        method_path_stats.update({"alert_threshold": alert_threshold})
        method_path_stats.update({"in_alert": False}) # move up
        method_path_stats.update({"alert_id": None}) # move u to ncilude in default timing analysis row in db

        if method_path_stats["avg"] > alert_threshold:

            method_path_stats.update({"in_alert": True})
            existing_alert_id = last_alert_id.get(mp, None)

            if not existing_alert_id:
                alert_id = str(uuid.uuid4())
                last_alert_id[mp] = alert_id
                method_path_stats.update({"alert_id": alert_id})

                await queues.event_queue.put(
                    pyd.Event(
                        type=event_types.TIMING_ALERT,
                        payload={"method_path": mp, "stats": method_path_stats},
                    )
                )
        else:
            existing_alert_id = last_alert_id.get(mp, None)
            if existing_alert_id:
                last_alert_id[mp] = None

        output.append(method_path_stats)

    # persist this and query the db from sync crud in path op func - do not call directly.
    return {"data": output, "meta": {"window": window}}


async def timing_event_handler(event: pyd.Event):
    # TODO split this into hadnler for persitence, stats calc, alert calc
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
