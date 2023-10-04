import asyncio

from . import event_dispatcher
from . import event_types
from .. import pydmodels as pyd

event_queue = asyncio.Queue()

async def event_worker():
    while True:

        qsize = event_queue.qsize()
        if qsize > 100:
            await event_queue.put(
            pyd.Event(
                type=event_types.EXC_RAISED_WARN,
                payload={"qsize": qsize},
            )
        )
        event = await event_queue.get()
        event_type = event.type

        if event_type in event_dispatcher.dispatcher:
            tasks = []
            for fn in event_dispatcher.dispatcher[event_type]:
                tasks.append(fn(event))
            await asyncio.gather(*tasks)

