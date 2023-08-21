import os
import subprocess

from . import errors


def get_git_branch():
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
        return branch_name
    except subprocess.CalledProcessError:
        print("An error occurred while trying to fetch the Git branch.")
        return None
    except FileNotFoundError:
        print("Git is not installed or not in the PATH.")
        return None

def get_git_commit():
    try:
        branch_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
        return branch_commit
    except subprocess.CalledProcessError:
        print("An error occurred while trying to fetch the Git branch.")
        return None
    except FileNotFoundError:
        print("Git is not installed or not in the PATH.")
        return None

### DATABASE ###

CURRENT_ENV = os.environ.get("NINEPANELS_ENV")
DB_HOSTNAME = os.environ.get("DB_HOSTNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")

SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/postgres"

### ENVIRONMENT ###

branch = get_git_branch()
commit = get_git_commit()

def compare_env_and_branch():
    if CURRENT_ENV == "FEATURE":
        if branch == "main" or branch == "staging":
            raise errors.ConfigurationException(f"you are on the wrong branch (main or staging) to run a local feature branch")

if branch:
    compare_env_and_branch()

if commit:
    CURRENT_COMMIT = commit
else:
    CURRENT_COMMIT = "no data"

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


