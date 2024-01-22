from fastapi import APIRouter
from fastapi import Depends

from typing import List

from starlette.requests import Request

from sqlalchemy.orm import Session

from ..db.database import get_db
from .. import crud
from .. import auth
from .. import pydmodels as pyd


admin = APIRouter()

# TODO examin braking this into am admin api module that doesn thaveperformance timing on it
@admin.get(
    "/routes",
)
async def read_route_performance(
    request: Request, db: Session = Depends(get_db)
):  # user: pyd.User = Depends(auth.get_current_user)): # TODO reenable auth
    resp = crud.read_all_routes(db=db)

    return resp


@admin.get(
    "/routes/timings",
)
async def read_route_timings(
    method_path: str, window_size: int | None = 100, db: Session = Depends(get_db)
):  # user: pyd.User = Depends(auth.get_current_user)): # TODO reenable auth
    resp = crud.read_route_timings(
        db=db, method_path=method_path, window_size=window_size
    )
    return resp


@admin.get(
    "/requests",
)
def read_request_performance(user: pyd.User = Depends(auth.get_current_user)):
    ...

@admin.get("/users", response_model=List[pyd.User])
async def read_all_users(
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_admin_user)
):

    users = crud.read_all_users(db=db)

    return users