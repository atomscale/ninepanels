from pydantic import EmailStr
from .database import get_db, engine
from . import crud
from . import sqlmodels as sql
from . import pydmodels as pyd
from . import auth
from . import config
from . import errors

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException, status
from fastapi import Form
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from typing import List

from sqlalchemy.orm import Session

from alembic.config import Config
from alembic import command

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

from datetime import datetime

api = FastAPI()

api_origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
]

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

sql.Base.metadata.create_all(bind=engine)

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

    return user


@api.get("/users", response_model=pyd.User)
def read_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    found = crud.read_user_by_id(db=db, user_id=user.id)

    return found


@api.delete("/users")
def delete_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    is_deleted = crud.delete_user_by_id(db=db, user_id=user.id)

    return {"success": is_deleted}


@api.post("/panels", response_model=pyd.Panel)
def post_panel_by_user_id(
    title: str = Form(),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user),
):
    try:
        if description:
            new_panel = crud.create_panel_by_user_id(db, user.id, title, description)
        else:
            new_panel = crud.create_panel_by_user_id(db, user.id, title)
        return new_panel
    except errors.PanelNotCreated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create panel"
        )


@api.get("/panels", response_model=List[pyd.Panel])
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
            updated_panel = crud.update_panel_by_id(db, panel_id, update)
            return updated_panel
        except errors.PanelNotUpdated as e:
            raise HTTPException(status_code=422, detail=f"Panel not updated: {str(e)}")

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


@api.get("/entries", response_model=List[pyd.Entry])
def get_current_entries_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    entries = crud.read_current_entries_by_user_id(db=db, user_id=user.id)

    return entries


@api.post("/entries", response_model=pyd.Entry)
def post_entry_by_panel_id(
    new_entry: pyd.EntryCreate,
    user: pyd.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    entry = crud.create_entry_by_panel_id(db, **new_entry.model_dump(), user_id=user.id)

    return entry
