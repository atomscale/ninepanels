import os
import subprocess
import rollbar

from .. import exceptions


def get_git_branch():
    try:
        branch_name = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        return branch_name
    except subprocess.CalledProcessError:
        # print("An error occurred while trying to fetch the Git branch.")
        return None
    except FileNotFoundError:
        # print("Git is not installed or not in the PATH.")
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
        # print("An error occurred while trying to fetch the Git branch.")
        return None
    except FileNotFoundError:
        # print("Git is not installed or not in the PATH.")
        return None


def get_env_var(var):
    value = os.environ.get(var)
    if not value:
        raise EnvironmentError(f"env var {var} is missing")
    return value


### DATABASE ###

try:
    CURRENT_ENV = get_env_var("NINEPANELS_ENV")
    DB_HOSTNAME = get_env_var("DB_HOSTNAME")
    DB_PASSWORD = get_env_var("DB_PASSWORD")
    DB_PORT = get_env_var("DB_PORT")
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)

SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}"
print(SQLALCHEMY_DATABASE_URI)

def get_db_uri():
    return SQLALCHEMY_DATABASE_URI


### SERVER ###

try:
    SERVER_ROOT = get_env_var("NINEPANELS_URL_ROOT")
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)

### ENVIRONMENT ###

branch = get_git_branch()
commit = get_git_commit()


def compare_env_and_branch():
    if CURRENT_ENV == "FEATURE":
        if branch == "main" or branch == "staging":
            raise exceptions.ConfigurationException(
                detail=f"you are on the wrong branch (main or staging) to run a local feature branch"
            )


try:
    RENDER_GIT_BRANCH = get_env_var("RENDER_GIT_BRANCH")
    RENDER_GIT_COMMIT = get_env_var("RENDER_GIT_COMMIT")
except EnvironmentError as e:
    RENDER_GIT_BRANCH = "local feature"

### FRONT END URL ###

try:
    NINEPANELS_URL_ROOT = get_env_var("NINEPANELS_URL_ROOT")
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)

### LOGGING ###

import logging


def set_up_logger():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s (%(filename)s:%(lineno)d): %(message)s ",
        level=logging.INFO,
    )


set_up_logger()

### MONITORING ###



try:
    ROLLBAR_KEY = get_env_var("ROLLBAR_KEY")
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)

if not CURRENT_ENV == 'TEST':
    rollbar.init(access_token=ROLLBAR_KEY, environment=CURRENT_ENV)


### PERFORMANCE ###

try:
    DB_CALL_AVG_WINDOW = 100
    DB_PERF_ALERT_THRESHOLD = 100
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)

### SECURITY ###

try:
    CRYPT_CONTEXT_SCHEME = get_env_var("CRYPT_CONTEXT_SCHEME")
    SECRET_KEY = get_env_var("JWT_SECRET")
    JWT_ALGORITHM = get_env_var("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_DAYS = get_env_var("ACCESS_TOKEN_EXPIRE_DAYS")
    PASSWORD_ACCESS_TOKEN_MINUTES = int(get_env_var("PASSWORD_ACCESS_TOKEN_MINUTES"))
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)

### COMMUNICATION ###

try:
    POSTMARK_API_KEY = get_env_var("POSTMARK_API_KEY")
except EnvironmentError as e:
    print(f"missing env var error! startup aborted {e}")
    exit(1)
