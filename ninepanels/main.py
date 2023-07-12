from .database import get_db, engine
from . import crud
from . import sqlmodels as sql
from . import pydmodels as pyd
from . import auth

from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException, status
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware


from typing import List

from sqlalchemy.orm import Session, sessionmaker

api = FastAPI()

api_origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# sql.Base.metadata.drop_all(bind=engine)
sql.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

# check if db is empty (first time run after manual delete maybe)

user = db.query(sql.User).first()

if not user:

    test_users = [
        sql.User(name='Bennyboy', email="ben@ben.com", hashed_password="$2b$12$v9zcspKOpiOZ7SA1LRo44er.TwmDigIVLevTnNBa4esI81ZarWKUW"),
        sql.User(name='Prof. Hobo', email="hobo@hobo.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja"),
        sql.User(name='Christoph', email="chris@chris.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja")
    ]

    db.add_all(test_users)
    db.commit()

    test_panels = [
        sql.Panel(title="strength base", user_id=1),
        sql.Panel(title="aerobic topper", user_id=1),
        sql.Panel(title="two meals, no snacks", user_id=1),
        sql.Panel(title="homemade meals", user_id=1),
        sql.Panel(title="loving presence", user_id=1),
        sql.Panel(title="house improvement", user_id=1),
        sql.Panel(title="asc", user_id=1),
        sql.Panel(title="atomscale", user_id=1),
        sql.Panel(title="time rich: up at 6", user_id=1),
        sql.Panel(title="cure cancer", user_id=2),
        sql.Panel(title="move to oz", user_id=3),
        sql.Panel(title="make pickles", user_id=3),
        sql.Panel(title="move house again", user_id=2),
    ]

    db.add_all(test_panels)
    db.commit()

    ts = datetime.utcnow()
    diff = timedelta(seconds=1)

    test_entries = [
        # sql.Entry(is_complete=True, panel_id=1, timestamp=ts),
        # sql.Entry(is_complete=True, panel_id=2, timestamp=ts),
        # sql.Entry(is_complete=True, panel_id=3, timestamp=ts),
        # sql.Entry(is_complete=False, panel_id=1, timestamp=ts + diff),
        # sql.Entry(is_complete=True, panel_id=5, timestamp=ts),
        # sql.Entry(is_complete=True, panel_id=6, timestamp=ts),
    ]
    db.add_all(test_entries)
    db.commit()

@api.get("/")
def index():
    return {"yep": "this is the nine panels api :)"}

@api.post("/token", response_model=pyd.AccessToken)
def post_credentials_for_access_token(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = credentials.username
    plain_password = credentials.password

    user = auth.authenticate_user(db=db, email=email, password=plain_password)

    access_token = auth.create_access_token({"sub": email})

    return {"access_token": access_token}

@api.get("/panels", response_model=List[pyd.Panel])
def get_panels_by_user_id(
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user)
):
    user_id = 1
    panels = crud.read_all_panels_by_user_id(db=db, user_id=user.id)

    return panels

@api.get("/entries", response_model=List[pyd.Entry])
def get_current_entries_by_user_id(
    db: Session = Depends(get_db),
    user: pyd.User = Depends(auth.get_current_user)
):
    entries = crud.read_current_entries_by_user_id(db=db, user_id=user.id)

    return entries

@api.post("/entries", response_model=pyd.Entry)
def post_entry_by_panel_id(
    new_entry: pyd.EntryCreate,
    user: pyd.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):

    entry = crud.create_entry_by_panel_id(
        db,
        **new_entry.model_dump(),
        user_id=user.id
        )

    return entry
