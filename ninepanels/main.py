from pydantic import EmailStr
from .database import get_db, engine
from . import crud
from . import sqlmodels as sql
from . import pydmodels as pyd
from . import auth
from . import config
from . import errors
from . import utils

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi import BackgroundTasks
from fastapi import Form
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

import rollbar
from rollbar.contrib.fastapi import ReporterMiddleware as RollbarMiddleware

from typing import List

from sqlalchemy.orm import Session

from alembic.config import Config
from alembic import command

from pprint import PrettyPrinter

import time
import random
from datetime import datetime

pp = PrettyPrinter(indent=4)

rollbar.init(access_token=config.ROLLBAR_KEY, environment=config.CURRENT_ENV)


api = FastAPI()

api_origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
]

api.add_middleware(RollbarMiddleware)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_migrations():
    """this function ensures that the entire vcs comitted alembic migraiton hisotry is applied to the
    taregt database.

    on main branch, this means that all that needs to happen is the staging branch is merged

    this assumes a fix forward approach, with no use of downgrade

    """
    alembic_cfg = Config("alembic.ini")  # Path to your Alembic configuration file
    command.upgrade(alembic_cfg, "head")
    return None


run_migrations()

# sql.Base.metadata.create_all(bind=engine)

version_ts = datetime.utcnow()

version_date = f"{version_ts.strftime('%d')} {version_ts.strftime('%B')}"

print(
    f"this is the ninepanels api in env: {config.CURRENT_ENV}. Version: {version_date}. Branch: {config.RENDER_GIT_BRANCH}, commit: {config.RENDER_GIT_COMMIT}"
)


@api.get("/")
def index():
    return {"branch": f"{config.RENDER_GIT_BRANCH}", "release_date": f"{version_date}"}


@api.post("/token", response_model=pyd.AccessToken)
def post_credentials_for_access_token(
    credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = credentials.username
    plain_password = credentials.password

    user = auth.authenticate_user(db=db, email=email, password=plain_password)

    access_token = auth.create_access_token({"sub": email})

    if user:
        crud.invalidate_all_user_prts(db=db, user_id=user.id)

    return {"access_token": access_token}


@api.post("/users", response_model=pyd.User)
def create_user(
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
    except errors.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"undefined error: {str(e)}"
        )

    # rollbar.report_message(
    #     message=f"new user {user.name} just signed up!", level="info"
    # )

    return user


@api.get("/users", response_model=pyd.User)
def read_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    user = crud.read_user_by_id(db=db, user_id=user.id)

    return user


@api.delete("/users")
def delete_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    is_deleted = crud.delete_user_by_id(db=db, user_id=user.id)

    return {"success": is_deleted}


@api.post("/panels", response_model=pyd.Panel)
def post_panel_by_user_id(
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
        return new_panel
    except errors.PanelNotCreated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create panel"
        )


@api.get("/panels")  # response_model=List[pyd.PanelResponse])
def get_panels_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    panels = crud.read_panels_with_current_entry_by_user_id(db=db, user_id=user.id)

    return panels


@api.patch("/panels/{panel_id}", response_model=pyd.Panel)
def update_panel_by_id(
    panel_id: int,
    update: dict = Body(),
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    if update:
        try:
            updated_panel = crud.update_panel_by_id(db, user.id, panel_id, update)
            return updated_panel
        except errors.PanelNotUpdated as e:
            raise HTTPException(status_code=422, detail=f"{str(e)}")

    else:
        raise HTTPException(status_code=422, detail="No update object")


@api.delete("/panels/{panel_id}")
def delete_panel_by_id(
    panel_id: int,
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        is_deleted = crud.delete_panel_by_panel_id(db, user.id, panel_id)
        return is_deleted
    except errors.PanelNotDeleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error deleting panel"
        )


@api.post(
    "/entries", response_model=pyd.Entry
)  # TODO this needs to change to /panels/{id}/entries
def post_entry_by_panel_id(
    new_entry: pyd.EntryCreate,
    user: pyd.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    entry = crud.create_entry_by_panel_id(db, **new_entry.model_dump(), user_id=user.id)

    return entry


@api.delete("/panels/{panel_id}/entries")
def delete_all_entries_by_panel_id(
    panel_id: int,
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        conf = crud.delete_all_entries_by_panel_id(
            db=db, user_id=user.id, panel_id=panel_id
        )
    except errors.EntriesNotDeleted as e:
        print("error here")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entries not deleted: {str(e)}",
        )

    return conf


@api.get("/metrics/panels/consistency")
def get_panel_consistency_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    resp = crud.calc_consistency(db=db, user_id=user.id)

    return resp


@api.post("/request_password_reset")
def initiate_password_reset_flow(
    email: str = Form(),
    db: Session = Depends(get_db),
):
    try:
        prt_user, prt = crud.create_password_reset_token(db=db, email=email)
    except errors.PasswordResetTokenException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create password reset token",
        )
    except errors.UserNotFound:
        raise HTTPException(
            status_code=404,
            detail="That email doesn't exist",
        )

    if prt_user:
        # create url
        url = f"{config.NINEPANELS_URL_ROOT}/password_reset?email={prt_user.email}&password_reset_token={prt}"

        # dispatch email
        try:
            if utils.dispatch_password_reset_email(
                recipient_email=prt_user.email, recipient_name=prt_user.name, url=url
            ):
                return True # initiation of password flow successful
            else:
                raise HTTPException(
                400, detail="Having trouble sending your password reset email. Sorry."
            )
        except errors.PasswordResetTokenException:
            raise HTTPException(
                400, detail="Having trouble sending your password reset email. Sorry."
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not start password reset process, sorry.",
        )


@api.post("/password_reset")
def password_reset(
    new_password: str = Form(),
    email: str = Form(),
    password_reset_token: str = Form(),
    db: Session = Depends(get_db),
):
    try:
        user = crud.read_user_by_email(db=db, email=email)
    except errors.UserNotFound:
        raise HTTPException(404, detail="user not found")

    try:
        token_valid = crud.check_password_reset_token_is_valid(
            db=db, password_reset_token=password_reset_token, user_id=user.id
        )
    except errors.PasswordResetTokenException:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Problem with the password reset process...",
        )

    if token_valid:
        new_password_hash = auth.get_password_hash(new_password)

        update = {'hashed_password': new_password_hash}

        try:
            updated_user = crud.update_user_by_id(db=db, user_id=user.id, update=update)
        except errors.UserNotUpdated:
            raise HTTPException(400, detail="Could not update your password.")

        try:
            token_invalidated = crud.invalidate_password_reset_token(db=db, password_reset_token=password_reset_token, user_id=user.id)
        except errors.PasswordResetTokenException:
            raise HTTPException(400, detail="Error in invalidating password")

        return True # password updated
    else:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Please request a new password reset token.",
        )
