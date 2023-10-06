import pytest
from fastapi.testclient import TestClient

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlite3 import Connection as SQLiteConnection

from ninepanels import sqlmodels as sql
from ninepanels.main import api, get_db
from ninepanels.core import config
from ninepanels.db import data_mgmt



@pytest.fixture(scope="session")
def test_db():

    # test_engine = create_engine(
    #     "sqlite:///./test.db", connect_args={"check_same_thread": False}
    # )

    # # ensure pragma for FK constraint is set if it is an Sqlite db
    # @event.listens_for(test_engine, "connect")
    # def _set_fk_pragma(conn, conn_record):
    #     if isinstance(conn, SQLiteConnection):
    #         cur = conn.cursor()
    #         cur.execute("pragma foreign_keys=1;")
    #         cur.close()

    test_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)


    sql.Base.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    test_db = SessionLocal()

    # \/\/\/\/\/\/\/\/ set up any req data here

    # test_users = [
    #     sql.User(name='Bennyboy', email="ben@ben.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja"), # "password"
    #     sql.User(name='Christoph', email="chris@chris.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja"),
    #     sql.User(name='Prof. Hobo', email="hobo@hobo.com", hashed_password="$2b$12$XWhJLQ9EdIzRX3imhGqQkuTApZ2LUTyPfrGj/yNkRCoWTggymtBja"),
    # ]

    # db.add_all(test_users)
    # db.commit()

    # test_panels = [
    #     sql.Panel(title="one", description="some funky desoon you know", position=0, user_id=1),
    #     # nulls get returned first, ie if position not speficied, panel "two" will be first:
    #     sql.Panel(title="two", description="some funky descrtioonou know", position=1, user_id=1),
    #     sql.Panel(title="three", description="somy descrtioon  know", position=2, user_id=1),
    #     sql.Panel(title="A", position=0, user_id=2),
    #     sql.Panel(title="B", position=1, user_id=2),
    # ]

    # db.add_all(test_panels)
    # db.commit()

    # ts = datetime.utcnow()
    # diff = timedelta(days=2)

    # test_entries = [
    #     sql.Entry(is_complete=True, panel_id=1, timestamp=ts),
    #     sql.Entry(is_complete=False, panel_id=2, timestamp=ts),
    #     sql.Entry(is_complete=True, panel_id=3, timestamp=ts),

    # ]
    # db.add_all(test_entries)
    # db.commit()


    # /\/\/\/\/\/\ more logic can go above here to set up more data

    data_mgmt.create_data(engine=test_engine, db=test_db)

    try:
        yield test_db
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