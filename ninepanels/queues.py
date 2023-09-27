import asyncio

from . import comms
from . import performance

event_queue = asyncio.Queue()

comms_dispatcher = {
    # always ensure a list of funcs, even if only one.
    # asyncio.gather is run across the list
    'password_reset_requested': [comms.password_reset, comms.rollbar_message],
    'new_user_signed_up': [comms.welcome],
    'timer_completed': [performance.example_timing_handler]
    # TODO in 'timer_completed is where persitence, perf monitoring and ws event emission will happen
}

async def event_worker():
    while True:
        # note that all events in the system are pydantic pyd.Event instances
        # all event handlers are expected to accept the full Event instance as their single param
        event = await event_queue.get()
        event_type = event.type

        if event_type in comms_dispatcher:
            tasks = []
            for fn in comms_dispatcher[event_type]:
                tasks.append(fn(event))
            asyncio.gather(*tasks)
