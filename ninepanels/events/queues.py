import asyncio

from . import dispatcher

event_queue = asyncio.Queue()

async def event_worker():
    while True:

        event = await event_queue.get()
        event_name = event.name
        print(event_name)

        if event_name in dispatcher.dispatcher:
            tasks = []
            print(dispatcher.dispatcher[event_name])
            for fn in dispatcher.dispatcher[event_name]:
                tasks.append(fn(event))
            await asyncio.gather(*tasks)

