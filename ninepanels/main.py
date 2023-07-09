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


@api.get("/entries", response_model=List[pyd.Entry])
def get_all_entries(
    db: Session = Depends(get_db)
):
    entries = crud.read_all_entries(db=db)

    return entries

@api.post("/entries", response_model=pyd.Entry)
def post_entry(
    new_entry: pyd.EntryCreate,
    db: Session = Depends(get_db)
):
    entry = crud.create_entry(
        db,
        **new_entry.model_dump()
        )

    return entry