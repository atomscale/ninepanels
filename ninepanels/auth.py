from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from .config import (
    SECRET_KEY,
    JWT_ALGORITHM,
    AUTH_CODE_EXPIRE_MINUTES,
    AUTH_CODE_LEN,
)
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

from . import sqlmodels as sql
from . import pydmodels as pyd
from . import crud
from .database import get_db

from datetime import datetime, timedelta

import random

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    return hash_context.verify(
        plain_password, hashed_password
    )  # returns a bool of match/no match


def get_password_hash(password):
    return hash_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):

    """ find the user in the db and check their stored password


    returns User

    raises HTTP Unauth error if user not found
    """

    user = crud.read_user_by_email(db, email)  # will return None if not found

    if not user:  # authenticate_user func return false if password hashes do not match
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # the cool status helper
            detail="Incorrect username or password - email not found",  # some extra info
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(
        password, user.hashed_password
    ):  # note user is a pydantic instance of UserInDb, can see that if hover over user
        # this verify_password is a function of passlib and hashes the plain password and compares to the hash retrived from db
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # the cool status helper
            detail="Incorrect username or password",  # some extra info
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user  # returns the User sqlA instance


def create_access_token(
    data: dict,  # data to encode in claims
    expires_delta: timedelta
    | None = None,
):

    """ compose the JWT with encoded claims and expiry

    NOTE: expiry set to 100 days!!


    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=100
        )  # essentially infiinite for purposes of first tests

     # adding expiry as "exp" to claims
    to_encode.update(
        {"exp": expire}
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), access_token: str = Depends(oauth2_scheme)
):

    """Checks provided access_token is valid and if so, looks up user using the email in "sub" of claims.

    Used as a base dependency.

    - valid JWT (not in blacklist) - NOT IMPLEMENT YET
    - email is in JWT
    - email is in db

    returns user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )  # minimising code dup as can be raised in three places below, note is very vague and apilied to many type of auth failure

    try:
        # this func is being called in the path for a user to see logged in stuff ("/me")
        # the client will send back the JWT is recieved after hitting the token endpoint at somepoint in the past,
        # having stored it locally on the device / browser

        # check if jwt  is in blacklist
        # func will return the
        # if crud.get_blacklisted_access_token(db, token):
        #     # if it is in blacklist raise an exception, client can handle redirect to relogin
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="session expired, please log in again",
        #     )

        # if not in blacklist proceed
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: int = payload.get(
            "sub"
        )  # check if there is a "sub" claim in the JWT
        if email is None:  # if there is no "sub", then could not authenticate
            raise credentials_exception

    except JWTError:
        # handle some decode error, perhaps if JWT is malformed due to network interrupt or soemthing.
        raise credentials_exception
    # check if the user is in the db using the email we decoded out from the JWT "sub" field
    user = crud.read_user_by_email(db, email)

    # if it fails to find a user, again raise auth expcetion
    if user is None:
        raise credentials_exception

    # if it does find the user, return all the user data
    return user


def get_current_verified_user(
    current_user: pyd.User = Depends(get_current_user),
):
    """
    NOT IMPLEMENTED YET

    Checks user is verified. Can be injected into user facing routes

    If so, returns User pydantic instance"""

    # this is the func used across the "logged in" routes to verify JWT was valid, the user exists and that the user has not been set to "disabled" in the db
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unverified user"
        )
    return current_user


def get_current_admin_user(
    current_user: pyd.User = Depends(get_current_verified_user),
):
    """
    NOT IMPLEMENTED YET - USE auth.get_current_user in dep injection

    Checks is the current user is an admin and verified.

    If so, returns UserInDb pydantic instance"""

    if current_user.role == pyd.Role.admin:
        return current_user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def create_auth_code(db: Session, user_id: int):

    """ NOT IMPLEMENETED YET """

    code_data = {
        "code": random.randint(10 ** (AUTH_CODE_LEN - 1), 10**AUTH_CODE_LEN - 1),
        "user_id": user_id,
        "expiry": datetime.utcnow() + timedelta(minutes=AUTH_CODE_EXPIRE_MINUTES),
        "is_valid": True,
    }

    auth_code_db = sql.AuthCode(**code_data)

    db.add(auth_code_db)
    db.commit()


    return auth_code_db.code


def invalidate_prev_auth_codes_for_user(db: Session, user_id: int):
    """ NOT IMPLEMENETED YET """

    prev_codes_for_user = (
        db.query(sql.AuthCode).where(sql.AuthCode.user_id == user_id).all()
    )

    if prev_codes_for_user:
        for prev_code in prev_codes_for_user:
            prev_code.is_valid = False

    db.commit()