import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ninepanels import sqlmodels as sql
from ninepanels.main import api, get_db
from ninepanels.core import config
from ninepanels.db import data_mgmt


@pytest.fixture()
def test_db():

    test_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

    # sql.Base.metadata.drop_all(bind=test_engine)

    sql.Base.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    test_db = SessionLocal()

    data_mgmt.create_data(engine=test_engine, db=test_db)

    try:
        # print("yielding test_db")
        yield test_db
        # print("yield complete")
    finally:
        # print("entering finally block")
        test_db.rollback()
        test_engine.dispose()
        sql.Base.metadata.drop_all(bind=test_engine)
        test_db.close()
        # print("closed and dropped....?")

@pytest.fixture()
def test_server(test_db):

    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()

    api.dependency_overrides[get_db] = override_get_db

    client = TestClient(api)

    yield client