import rollbar

from .. import event_models
from ...db import crud
from ... import exceptions


async def report_exc_error(event: event_models.BaseEvent):
    rollbar.report_message(
        message=event.name, extra_data=event.model_dump(), level="error"
    )


async def report_exc_warn(event: event_models.BaseEvent):
    rollbar.report_message(
        message=event.name, extra_data=event.model_dump(), level="warn"
    )


async def report_exc_info(event: event_models.BaseEvent):
    rollbar.report_message(
        message=event.name, extra_data=event.model_dump(), level="info"
    )


async def report_info(event: event_models.BaseEvent):
    rollbar.report_message(
        message=event.name, extra_data=event.model_dump(), level="info"
    )


async def update_user_login(event: event_models.BaseEvent):
    try:
        from ...db import database

        db = database.SessionLocal()

        crud.update_user_by_id(db=db, user_id=event.user_id, update={"last_login": event.created_at})
    except exceptions.UserNotUpdated:
        raise

async def update_user_activity(event: event_models.BaseEvent):
    try:
        from ...db import database

        db = database.SessionLocal()

        crud.update_user_by_id(db=db, user_id=event.user_id, update={"last_activity": event.created_at})
    except exceptions.UserNotUpdated:
        raise

