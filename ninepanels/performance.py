from . import pydmodels as pyd

async def example_timing_handler(event: pyd.Event):
    print(f"timing event handler")