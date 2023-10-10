import asyncio

from . import dispatcher

event_queue = asyncio.Queue()

async def event_worker():
    while True:

        # TODO reimplement with events.
        # qsize = event_queue.qsize()
        # if qsize > 100:
        #     await event_queue.put(
        #     pyd.Event(
        #         type=event_types.EXC_RAISED_WARN,
        #         payload={"qsize": qsize},
        #     )
        # )
        event = await event_queue.get()
        event_type = event.type

        if event_type in dispatcher.dispatcher:
            tasks = []
            for fn in dispatcher.dispatcher[event_type]:
                tasks.append(fn(event))
            await asyncio.gather(*tasks)

