import logging

from . import pydmodels as pyd


async def log_error(event: pyd.Event):
    logging.error(event.model_dump())


async def log_warn(event: pyd.Event):
    logging.warn(event.model_dump())


async def log_info(event: pyd.Event):
    logging.info(event.model_dump())
