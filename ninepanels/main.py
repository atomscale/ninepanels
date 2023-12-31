import asyncio

import rollbar
from rollbar.contrib.fastapi import ReporterMiddleware as RollbarMiddleware

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi import Form
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request

from pydantic import EmailStr

from sqlalchemy.orm import Session

from alembic.config import Config
from alembic import command

from pprint import PrettyPrinter

from datetime import datetime

from .db.database import get_db
from . import middleware
from . import crud
from . import pydmodels as pyd
from . import sqlmodels as sql
from . import auth
from .core import config
from . import exceptions
from .events import queues
from .events import event_types
from .events import event_models
from . import utils

from .routers import admin


pp = PrettyPrinter(indent=4)

# rollbar.init(access_token=config.ROLLBAR_KEY, environment=config.CURRENT_ENV)

api = FastAPI()

api_origins = [
    "http://localhost:5173",
    "https://preview.ninepanels.com",
    "https://ninepanels.com",
]

api.add_middleware(middleware.ResponseWrapperMiddleware)
api.add_middleware(middleware.RouteTimingMiddleware)
api.add_middleware(RollbarMiddleware)
api.add_middleware(
    CORSMiddleware,
    allow_origins=api_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(admin.admin, prefix="/admin")


def run_migrations():
    """this function ensures that the entire vcs comitted alembic migraiton hisotry is applied to the
    taregt database.

    on main branch, this means that all that needs to happen is the staging branch is merged

    this assumes a fix forward approach, with no use of downgrade

    """
    alembic_cfg = Config("alembic.ini")  # Path to your Alembic configuration file
    command.upgrade(alembic_cfg, "head")
    return None


if config.CURRENT_ENV not in ["TEST", "CI"]:
    run_migrations()


version_ts = datetime.utcnow()

version_date = f"{version_ts.strftime('%d')} {version_ts.strftime('%B')}"


@api.on_event("startup")
def init_async_workers():
    asyncio.create_task(queues.event_worker())


@api.get("/")
async def index(request: Request):
    return {"branch": f"{config.RENDER_GIT_BRANCH}", "release_date": f"{version_date}"}


@api.post(
    "/token",
    response_model=pyd.AccessToken,
    responses={401: {"model": pyd.HTTPError, "description": "Unauthorised"}},
)
async def post_credentials_for_access_token(
    credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = credentials.username
    plain_password = credentials.password

    try:
        user = auth.authenticate_user(db=db, email=email, password=plain_password)
    except (exceptions.UserNotFound, exceptions.IncorrectPassword) as e:
        await queues.event_queue.put(
            pyd.Event(
                type=event_types.EXC_RAISED_WARN,
                payload=e.__dict__,
                payload_type=type(e),
            )
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        access_token = auth.create_access_token(
            data={"sub": email}, expires_delta=config.ACCESS_TOKEN_EXPIRE_DAYS
        )
    except (TypeError, ValueError) as e:
        await queues.event_queue.put(
            pyd.Event(
                type=event_types.EXC_RAISED_ERROR,
                payload=e,
                payload_type=type(e),
            )
        )
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Issue creating the access token",
        )

    try:
        crud.invalidate_all_user_prts(db=db, user_id=user.id)
    except exceptions.PasswordResetTokenException as e:
        await queues.event_queue.put(
            pyd.Event(
                type=event_types.EXC_RAISED_WARN,
                payload=e.__dict__,
                payload_type=type(e),
            )
        )

    event = event_models.UserLoggedIn(user_id=user.id, name=user.name)
    await queues.event_queue.put(event)

    return {"access_token": access_token}


@api.post("/users", response_model=pyd.User)
async def create_user(
    email: EmailStr = Form(),
    name: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    hashed_password = auth.get_password_hash(password)

    try:
        user = crud.create_user(
            db, {"name": name, "email": email, "hashed_password": hashed_password}
        )
    except exceptions.UserNotCreated as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e.detail}"
        )

    event = event_models.NewUserCreated(email=user.email, name=user.name)
    await queues.event_queue.put(event)

    return user


@api.get("/users", response_model=pyd.User)
async def read_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    user = crud.read_user_by_id(db=db, user_id=user.id)

    return user


@api.delete("/users")
async def delete_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    # TODO event emission here
    is_deleted = crud.delete_user_by_id(db=db, user_id=user.id)

    return {"success": is_deleted}


@api.post("/panels", response_model=pyd.Panel)
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
        rollbar.report_message(message=f"{user.name} created a panel", level="info")
        return new_panel
    except exceptions.PanelNotCreated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create panel"
        )


@api.get("/panels")  # response_model=List[pyd.PanelResponse])
async def get_panels_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    panels = crud.read_panels_with_current_entry_by_user_id(db=db, user_id=user.id)

    return panels


@api.patch(
    "/panels/{panel_id}",
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

            return updated_panel
        except exceptions.PanelNotUpdated as e:
            raise HTTPException(status_code=400, detail=f"Panel was not updated")

    else:
        raise HTTPException(status_code=400, detail="No update object")


@api.delete("/panels/{panel_id}")
async def delete_panel_by_id(
    panel_id: int,
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        is_deleted = crud.delete_panel_by_panel_id(db, user.id, panel_id)
        return {"success": is_deleted}
    except exceptions.PanelNotDeleted as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{str(e.detail)}"
        )


@api.post("/panels/{panel_id}/entries", response_model=pyd.Entry)
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

    return entry


@api.get("/panels/{panel_id}/entries")
async def get_entries_by_panel_id(
    panel_id: int,
    offset: int = 0,
    limit: int = 100,
    sort_by: str = "timestamp.desc",
    db: Session = Depends(get_db),
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

    return padded_entries


@api.delete("/panels/{panel_id}/entries")
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


@api.get("/metrics/panels/consistency")
async def get_panel_consistency_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    resp = crud.calc_consistency(db=db, user_id=user.id)

    return resp


@api.post("/request_password_reset")
async def initiate_password_reset_flow(
    email: str = Form(),
    db: Session = Depends(get_db),
):
    try:
        prt_user, prt = crud.create_password_reset_token(db=db, email=email)
    except exceptions.PasswordResetTokenException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create password reset token",
        )
    except exceptions.UserNotFound as e:
        raise HTTPException(
            status_code=404,
            detail=e.detail,
        )

    if prt_user:
        url = f"{config.NINEPANELS_URL_ROOT}/password_reset?email={prt_user.email}&password_reset_token={prt}"

        event = event_models.PasswordResetRequested(
            email=prt_user.email, name=prt_user.name, url=url
        )
        await queues.event_queue.put(event)

        return True  # initiation of password flow successful, used for ui logic only

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not start password reset process, sorry.",
        )


@api.post("/password_reset")
async def password_reset(
    new_password: str = Form(),
    email: str = Form(),
    password_reset_token: str = Form(),
    db: Session = Depends(get_db),
):
    try:
        user = crud.read_user_by_email(db=db, email=email)
    except exceptions.UserNotFound as e:
        raise HTTPException(404, detail=e.detail)

    try:
        token_valid = crud.check_password_reset_token_is_valid(
            db=db, password_reset_token=password_reset_token, user_id=user.id
        )
    except exceptions.PasswordResetTokenException:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Problem with the password reset process...",
        )

    if token_valid:
        new_password_hash = auth.get_password_hash(new_password)

        update = {"hashed_password": new_password_hash}

        try:
            updated_user = crud.update_user_by_id(db=db, user_id=user.id, update=update)
        except exceptions.UserNotUpdated:
            raise HTTPException(400, detail="Could not update your password.")

        try:
            token_invalidated = crud.invalidate_password_reset_token(
                db=db, password_reset_token=password_reset_token, user_id=user.id
            )
        except exceptions.PasswordResetTokenException:
            raise HTTPException(400, detail="Error in invalidating password")

        rollbar.report_message(
            message=f"{user.name} successfully updated their password", level="info"
        )
        return True  # password updated
    else:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Please request a new password reset token.",
        )
