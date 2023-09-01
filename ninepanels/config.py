import os
import subprocess

from . import errors


def get_git_branch():
    try:
        branch_name = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        return branch_name
    except subprocess.CalledProcessError:
        print("An error occurred while trying to fetch the Git branch.")
        return None
    except FileNotFoundError:
        print("Git is not installed or not in the PATH.")
        return None


def get_git_commit():
    try:
        branch_commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("utf-8")
        )
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

SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}"


def get_db_uri():
    return SQLALCHEMY_DATABASE_URI


### SERVER ###

SERVER_ROOT = os.environ.get("NINEPANELS_SERVER_ROOT")

### ENVIRONMENT ###

branch = get_git_branch()
commit = get_git_commit()


def compare_env_and_branch():
    if CURRENT_ENV == "FEATURE":
        if branch == "main" or branch == "staging":
            raise errors.ConfigurationException(
                f"you are on the wrong branch (main or staging) to run a local feature branch"
            )


# if branch:
#     compare_env_and_branch()


RENDER_GIT_BRANCH = os.environ.get("RENDER_GIT_BRANCH")
RENDER_GIT_COMMIT = os.environ.get("RENDER_GIT_COMMIT")

if not RENDER_GIT_BRANCH:
    RENDER_GIT_BRANCH = "local feature"

### LOGGING ###

import logging


def set_up_logger():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s (%(filename)s:%(lineno)d): %(message)s ",
        level=logging.INFO,
    )


set_up_logger()

### MONITORING ###

# import rollbar

ROLLBAR_KEY = os.environ.get("ROLLBAR_KEY")
# rollbar.init(access_token=ROLLBAR_KEY, environment=CURRENT_ENV)

# rollbar.report_message(message='rollbar init from config', level='info')

# logger = logging.getLogger(__name__)
# handler = rollbar.Rollbar


### SECURITY ###

SECRET_KEY = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 100
PASSWORD_ACCESS_TOKEN_MINUTES = int(os.environ.get("PASSWORD_ACCESS_TOKEN_MINUTES"))

### COMMUNICATION ###

POSTMARK_API_KEY = os.environ.get("POSTMARK_API_KEY")
