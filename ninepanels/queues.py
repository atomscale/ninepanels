import asyncio

from . import events

event_queue = asyncio.Queue()

async def event_worker():
    while True:
        # note that all events in the system are pydantic pyd.Event instances
        # all event handlers are expected to accept the full Event instance as their single param
        event = await event_queue.get()
        event_type = event.type

        if event_type in events.dispatcher:
            tasks = []
            for fn in events.dispatcher[event_type]:
                tasks.append(fn(event))
            asyncio.gather(*tasks)
