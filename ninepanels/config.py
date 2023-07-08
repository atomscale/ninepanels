import os

### DATABASE ###

DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOSTNAME = os.environ.get("DB_HOSTNAME")

SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
# SQLALCHEMY_DATABASE_URI = "sqlite:///./tempdb.db"
# SQLALCHEMY_DATABASE_URI = (
#     f"postgresql://postgres:{DB_PASSWORD}@{DB_HOSTNAME}:5432/postgres"
# )

os.environ["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI


def get_db_uri():
    return SQLALCHEMY_DATABASE_URI


### LOGGING ###

import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s (%(filename)s:%(lineno)d): %(message)s ",
    level=logging.INFO,
)