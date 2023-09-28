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


def calculate_stats(window_size: int = 10):
    from . import database
    db = database.SessionLocal()

    method_paths = db.query(sql.Timing.method_path).distinct().all()

    method_path_stats = {}

    for method_path in method_paths:
        mp = method_path[0]
        mp_result = (
            db.query(sql.Timing)
            .filter(sql.Timing.method_path == mp)
            .order_by(desc(sql.Timing.created_at))
            .limit(window_size)
            .all()
        )

        method_path_stats[mp] = {
            "readings": [timer.diff_ms for timer in mp_result],
            "timestamps": [timer.created_at for timer in mp_result]
            }

        avg = sum(method_path_stats[mp]['readings']) / len(method_path_stats[mp]['readings'])
        method_path_stats[mp].update({"avg": avg})

        minimum = min(method_path_stats[mp]['readings'])
        method_path_stats[mp].update({"min": minimum})

        maximum = max(method_path_stats[mp]['readings'])
        method_path_stats[mp].update({"max": maximum})

        last = method_path_stats[mp]['readings'][0]
        method_path_stats[mp].update({"last": last})

    # pp.pprint(method_path_stats)



async def process_timing_event(event: pyd.Event):
    timer_dict = event.payload.__dict__
    # persist to 'timings' table

    # process stats and emit
    timing = insert_timing(timer_dict)

    if timing:
        calculate_stats()

    await queues.event_queue.put(
        pyd.Event(type=event_types.TIMING_PROCESSED, payload={})
    )
