from .database import get_db, engine
from . import crud
from . import sqlmodels as sql
from . import pydmodels as pyd

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException, status
from fastapi import Form

from typing import List

from sqlalchemy.orm import Session

api = FastAPI()

sql.Base.metadata.create_all(bind=engine)

@api.get("/")
def index():
    return {"yo": "it works"}

@api.get("/panels", response_model=List[pyd.Panel])
def get_panels_by_user_id(
    db: Session = Depends(get_db)
    # auth dep will inject user id
):
    user_id =1

    panels = crud.read_all_panels_by_user_id(db=db, user_id=user_id)

    return panels

@api.get("/entries", response_model=List[pyd.Entry])
def get_current_entries_by_user_id(
    db: Session = Depends(get_db)
    # auth dependency will inject user_id here
):
    user_id = 1 # replace with auth dependency
    entries = crud.read_current_entries_by_user_id(db=db, user_id=user_id)

    return entries

@api.post("/entries", response_model=pyd.Entry)
def post_entry(
    new_entry: pyd.EntryCreate,
    db: Session = Depends(get_db)
):

    new_entry_data = new_entry.model_dump()
    if new_entry_data['user_id'] == 1:
        del new_entry_data['user_id']
        entry = crud.create_entry_by_panel_id(
            db,
            **new_entry_data
            )

        return entry
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)