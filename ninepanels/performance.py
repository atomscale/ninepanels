from . import pydmodels as pyd
from . import sqlmodels as sql
from . import queues
from . import event_types


def insert_timing(timer_dict: dict):
    from . import database
    db = database.SessionLocal()

    print("will write to db here")
    ...

async def process_timing_event(event: pyd.Event):
    timer_dict = event.payload.__dict__
    # persist to 'timings' table

    # process stats and emit
    insert_timing(timer_dict)

    await queues.event_queue.put(pyd.Event(
        type=event_types.TIMING_PROCESSED,
        payload={}
    ))
    ...

