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

from .db.database import get_db
from . import middleware
from . import crud
from . import pydmodels as pyd
from . import sqlmodels as sql

from .core import config
from . import exceptions
from .events import queues
from .events import event_models
from . import utils
from . import auth



pp = PrettyPrinter(indent=4)


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



from .routers.v5.admin import admin as v5_admin
from .routers.v5.users import users as v5_users
from .routers.v5.panels import panels as v5_panels
from .routers.v5.metrics import metrics as v5_metrics
from .routers.v5.auth import auth_router as v5_auth


v5_router = APIRouter()
v5_router.include_router(v5_admin, tags=[])
v5_router.include_router(v5_users)
v5_router.include_router(v5_panels)
v5_router.include_router(v5_metrics)
v5_router.include_router(v5_auth)


api.include_router(v5_router, prefix="/v5", tags=['v5'])


from fastapi.openapi.utils import get_openapi



# def custom_openapi():
#     if api.openapi_schema:
#         return api.openapi_schema
#     openapi_schema = get_openapi(
#         title="Your API",
#         version="1.0.0",
#         description="API documentation",
#         routes=api.routes,
#     )
#     # Customize the schema here
#     openapi_schema["components"]["securitySchemes"] = {
#         "BearerAuth": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "v5/auth/token",
#                     "scopes": {},
#                 }
#             },
#         }
#     }
#     api.openapi_schema = openapi_schema
#     return api.openapi_schema

# api.openapi = custom_openapi




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
    try:
        user = auth.authenticate_user_password_flow(
            db=db, email=credentials.username, password=credentials.password
        )
    except (exceptions.UserNotFound, exceptions.IncorrectPassword) as e:
        event = event_models.ExceptionRaisedInfo(
            exc_msg=str(e), exc_type=str(type(e))
        )
        await queues.event_queue.put(event)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        access_token = auth.create_access_token(
            data={"sub": credentials.username},
            expires_delta=config.ACCESS_TOKEN_EXPIRE_DAYS,
        )
    except (TypeError, ValueError) as e:
        event = event_models.ExceptionRaisedError(
            exc_msg=str(e), exc_type=type(e), user_id=user.id
        )
        await queues.event_queue.put(event)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Issue creating the access token",
        )

    try:
        crud.invalidate_all_user_prts(db=db, user_id=user.id)
    except exceptions.PasswordResetTokenException as e:
        event = event_models.ExceptionRaisedError(
            exc_msg=str(e), exc_type=type(e), user_id=user.id
        )
        await queues.event_queue.put(event)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Issue invalidating user PRTs",
        )

    # invalidate all user passcodes

    event = event_models.UserLoggedIn(user_id=user.id, user_name=user.name)
    await queues.event_queue.put(event)

    event = event_models.UserActivity(user_id=user.id)
    await queues.event_queue.put(event)

    print(access_token)
    return {"access_token": access_token}