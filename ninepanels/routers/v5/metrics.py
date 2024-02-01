# v5 TODO move to /panels

from rollbar.contrib.fastapi import ReporterMiddleware as RollbarMiddleware

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from ...db.database import get_db
from ... import pydmodels as pyd
from ... import crud
from ... import auth

metrics = APIRouter(prefix="/metrics")

@metrics.get("/panels/consistency")
async def get_panel_consistency_by_user_id(
    db: Session = Depends(get_db), user: pyd.User = Depends(auth.get_current_user)
):
    resp = crud.calc_consistency(db=db, user_id=user.id)

    return resp