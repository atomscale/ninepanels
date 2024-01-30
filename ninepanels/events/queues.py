import asyncio

from . import dispatcher

event_queue = asyncio.Queue()

async def event_worker():
    while True:

        event = await event_queue.get()
        event_type = event.name

        if event_type in dispatcher.dispatcher:
            tasks = []
            for fn in dispatcher.dispatcher[event_type]:
                tasks.append(fn(event))
            await asyncio.gather(*tasks)

