import logging

from .. import event_models


async def log_info(event: event_models.BaseEvent):
    logging.info(event.model_dump())


async def log_warn(event: event_models.BaseEvent):
    logging.warning(event.model_dump())


async def log_error(event: event_models.BaseEvent):
    logging.error(event.model_dump())
