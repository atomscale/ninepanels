import pytest

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlite3 import Connection as SQLiteConnection

from ninepanels import sqlmodels as sql

@pytest.fixture(scope="session")
def test_db():

    # set up a sqlite test engine connection NOT IN MEMORY!
    test_engine = create_engine(
        "sqlite:///./pytest.db", connect_args={"check_same_thread": False}
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
        sql.User(name='Bennyboy'),
        sql.User(name='Prof. Hobo'),
        sql.User(name='Christoph')
    ]

    db.add_all(test_users)
    db.commit()

    test_panels = [
    sql.Panel(title="workout", owner_id=1),
    sql.Panel(title="write code", owner_id=1),
    sql.Panel(title="walk harris", owner_id=1),
    sql.Panel(title="cure cancer", owner_id=2),
    sql.Panel(title="move to oz", owner_id=3),
    sql.Panel(title="make pickles", owner_id=3),
    sql.Panel(title="move house again", owner_id=2),
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
    ]
    db.add_all(test_entries)
    db.commit()


    # /\/\/\/\/\/\ more logic can go above here to set up more data

    try:
        yield db
    finally:
        sql.Base.metadata.drop_all(bind=test_engine)