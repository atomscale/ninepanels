# v5

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status

from pydantic import EmailStr


from starlette.requests import Request

from sqlalchemy.orm import Session

from ...db.database import get_db
from ... import crud
from ... import auth
from ... import pydmodels as pyd
from ... import exceptions
from ...events import event_models
from ...events import queues

users = APIRouter(prefix="/users")

@users.post("", response_model=pyd.User)
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

    event = event_models.NewUserCreated(email=user.email, user_name=user.name)
    await queues.event_queue.put(event)

    return user


@users.get("", response_model=pyd.User)
async def read_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    user = crud.read_user_by_id(db=db, user_id=user.id)

    return user


@users.delete("")
async def delete_user_by_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    # TODO event emission here
    is_deleted = crud.delete_user_by_id(db=db, user_id=user.id)

    return {"success": is_deleted}