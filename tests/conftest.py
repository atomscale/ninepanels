import pytest
from fastapi.testclient import TestClient

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlite3 import Connection as SQLiteConnection

from ninepanels import sqlmodels as sql
from ninepanels.main import api, get_db



@pytest.fixture(scope="session")
def test_db():

    # set up env vars required for test runs
    # dont worry, these credentials are local only, staging and prod have different ones :)
    # set up a sqlite test engine connection NOT IN MEMORY!
    test_engine = create_engine(
        "sqlite:///./test.db", connect_args={"check_same_thread": False}
    )

    # ensure pragma for FK constraint is set if it is an Sqlite db
    @event.listens_for(test_engine, "connect")
    def _set_fk_pragma(conn, conn_record):
        if isinstance(conn, SQLiteConnection):
            cur = conn.cursor()
            cur.execute("pragma foreign_keys=1;")
            cur.close()


    sql.Base.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    db = SessionLocal()

    # \/\/\/\/\/\/\/\/ set up any req data here

    test_users = [
        sql.User(name='Bennyboy', email="ben@ben.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja"), # "password"
        sql.User(name='Prof. Hobo', email="hobo@hobo.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja"),
        sql.User(name='Christoph', email="chris@chris.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja")
    ]

    db.add_all(test_users)
    db.commit()

    test_panels = [
        sql.Panel(title="workout", user_id=1),
        sql.Panel(title="write code", user_id=1),
        sql.Panel(title="walk harris", user_id=1),
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
        sql.Entry(is_complete=True, panel_id=1, timestamp=ts),
        sql.Entry(is_complete=False, panel_id=2, timestamp=ts),
        sql.Entry(is_complete=True, panel_id=3, timestamp=ts),
        sql.Entry(is_complete=False, panel_id=1, timestamp=ts + diff),
        sql.Entry(is_complete=True, panel_id=5, timestamp=ts),
        sql.Entry(is_complete=True, panel_id=6, timestamp=ts),
    ]
    db.add_all(test_entries)
    db.commit()


    # /\/\/\/\/\/\ more logic can go above here to set up more data

    try:
        yield db
    finally:
        sql.Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="session")
def test_server(test_db):

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    api.dependency_overrides[get_db] = override_get_db

    client = TestClient(api)

    yield client