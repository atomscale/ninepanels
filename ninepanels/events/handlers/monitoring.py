import rollbar

from ... import pydmodels as pyd


async def report_exc_error(event: pyd.Event):
    rollbar.report_message(message=event.type, extra_data=event.payload, level="error")


async def report_exc_warn(event: pyd.Event):
    rollbar.report_message(message=event.type, extra_data=event.payload, level="warn")


async def report_exc_info(event: pyd.Event):
    rollbar.report_message(message=event.type, extra_data=event.payload, level="info")


async def report_info(event: pyd.Event):
    rollbar.report_message(message=event.type, extra_data=event.payload, level="info")
