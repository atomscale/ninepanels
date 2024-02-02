import asyncio

import rollbar
from rollbar.contrib.fastapi import ReporterMiddleware as RollbarMiddleware

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi import Form
from fastapi import Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request

from sqlalchemy.orm import Session

from alembic.config import Config
from alembic import command

from pprint import PrettyPrinter

from datetime import datetime

from ...db.database import get_db
from ... import crud
from ... import auth
from ... import pydmodels as pyd
from ... import sqlmodels as sql
from ... import exceptions
from ... import utils
from ...core import config
from ...events import event_models
from ...events import queues

auth_router = APIRouter(prefix="/auth")




@auth_router.post("/request_password_reset")
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
            email=prt_user.email, user_name=prt_user.name, url=url
        )
        await queues.event_queue.put(event)

        return True  # initiation of password flow successful, used for ui logic only

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not start password reset process, sorry.",
        )


@auth_router.post("/password_reset")
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
