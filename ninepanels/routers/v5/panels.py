# v5

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Body
from fastapi import HTTPException
from fastapi import status

from typing import List

from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db import crud
from ... import auth
from ... import pydmodels as pyd
from ... import sqlmodels as sql
from ... import exceptions
from ... import utils
from ...events import event_models
from ...events import queues
from ...services import services as pn

panels = APIRouter(prefix="/panels")

@panels.post("", response_model=pyd.Panel)
async def post_panel_by_user_id(
    position: int = Form(default=None),  # TODO temp until client updates
    title: str = Form(),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        if description:
            new_panel = crud.create_panel_by_user_id(
                db=db,
                position=position,
                user_id=user.id,
                title=title,
                description=description,
            )
        else:
            new_panel = crud.create_panel_by_user_id(
                db=db, position=position, user_id=user.id, title=title
            )
        # rollbar.report_message(message=f"{user.name} created a panel", level="info")
    except exceptions.PanelNotCreated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create panel"
        )

    event = event_models.UserActivity(user_id=user.id)
    await queues.event_queue.put(event)

    return new_panel


@panels.get("")# , response_model=List[pyd.PanelResponse])
async def get_panels_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    panels = pn.all_panels_with_current_entry_by_user_id(db=db, user_id=user.id)

    # await asyncio.sleep(4)

    return panels


@panels.patch(
    "/{panel_id}",
    response_model=pyd.Panel,
    responses={400: {"model": pyd.HTTPError, "description": "Panel was not updated"}},
)
async def update_panel_by_id(
    panel_id: int,
    update: dict = Body(),
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    if update:
        try:
            updated_panel = crud.update_panel_by_id(db, user.id, panel_id, update)

        except exceptions.PanelNotUpdated as e:
            raise HTTPException(status_code=400, detail=f"Panel was not updated")

    else:
        raise HTTPException(status_code=400, detail="No update object")

    event = event_models.UserActivity(user_id=user.id)
    await queues.event_queue.put(event)

    return updated_panel


@panels.delete("/{panel_id}")
async def delete_panel_by_id(
    panel_id: int,
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        is_deleted = crud.delete_panel_by_panel_id(db, user.id, panel_id)
    except exceptions.PanelNotDeleted as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{str(e.detail)}"
        )

    event = event_models.UserActivity(user_id=user.id)
    await queues.event_queue.put(event)

    return {"success": is_deleted}


@panels.post("/{panel_id}/entries", response_model=pyd.Entry)
async def post_entry_by_panel_id(
    panel_id: int,
    new_entry: pyd.EntryCreate,
    user: pyd.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        entry = crud.create_entry_by_panel_id(
            db, panel_id=panel_id, **new_entry.model_dump(), user_id=user.id
        )
    except exceptions.EntryNotCreated as e:
        raise HTTPException(status_code=400, detail=e.detail)

    event = event_models.UserActivity(user_id=user.id)
    await queues.event_queue.put(event)


    return entry


@panels.get("/{panel_id}/entries")
async def get_entries_by_panel_id(
    panel_id: int,
    offset: int = 0,
    limit: int = 100,
    sort_by: str = "timestamp.desc",
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    # TODO all exc handling all the way down
    sort_key, sort_direction = utils.parse_sort_by(sql.Entry, sort_by=sort_by)

    # this needs to be all entries, as the limit is days, not entries (many entires per day)
    unpadded_entries = crud.read_entries_by_panel_id(
        db=db,
        panel_id=panel_id,
        offset=offset,
        sort_key=sort_key,
        sort_direction=sort_direction,
    )

    limit_days = limit
    padded_entries = crud.pad_entries(
        db=db, unpadded_entries=unpadded_entries, limit=limit_days, panel_id=panel_id
    )

    # await asyncio.sleep(2)

    return padded_entries


@panels.delete("/{panel_id}/entries")
async def delete_all_entries_by_panel_id(
    panel_id: int,
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        conf = crud.delete_all_entries_by_panel_id(
            db=db, user_id=user.id, panel_id=panel_id
        )
    except exceptions.EntriesNotDeleted as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entries not deleted: {str(e)}",
        )

    return conf