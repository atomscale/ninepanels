import os

### DATABASE ###

ninepanels_env = os.environ.get('NINEPANELS_ENV')

if ninepanels_env == "PRODUCTION" or ninepanels_env == "STAGING":
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOSTNAME = os.environ.get("DB_HOSTNAME")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://postgres:{DB_PASSWORD}@{DB_HOSTNAME}:5432/postgres"
    )
else:
    SQLALCHEMY_DATABASE_URI = "sqlite:///./localdev.db"

os.environ["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

def get_db_uri():
    return SQLALCHEMY_DATABASE_URI


### LOGGING ###

import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s (%(filename)s:%(lineno)d): %(message)s ",
    level=logging.INFO,
)

### SECURITY ###

SECRET_KEY = os.environ.get("JWT_SECRET")
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_DAYS=100
AUTH_CODE_EXPIRE_MINUTES = 10
AUTH_CODE_LEN = 4


