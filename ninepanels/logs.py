import logging

from .events import event_models


async def log_error(event: event_models.BaseEvent):
    # TODO utilise the pyd.LogMessage model
    logging.error(event.model_dump())


async def log_warn(event: event_models.BaseEvent):
    logging.warn(event.model_dump())


async def log_info(event: event_models.BaseEvent):
    logging.info(event.model_dump())
