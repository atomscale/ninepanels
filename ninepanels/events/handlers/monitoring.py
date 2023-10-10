import rollbar

from .. import event_models

async def report_exc_error(event: event_models.BaseEvent):
    rollbar.report_message(message=event.type, extra_data=event.model_dump(), level="error")


async def report_exc_warn(event: event_models.BaseEvent):
    rollbar.report_message(message=event.type, extra_data=event.model_dump(), level="warn")


async def report_exc_info(event: event_models.BaseEvent):
    rollbar.report_message(message=event.type, extra_data=event.model_dump(), level="info")


async def report_info(event: event_models.BaseEvent):
    rollbar.report_message(message=event.type, extra_data=event.model_dump(), level="info")
