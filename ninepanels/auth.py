from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from .core.config import SECRET_KEY, JWT_ALGORITHM, CRYPT_CONTEXT_SCHEME
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

from . import sqlmodels as sql
from . import pydmodels as pyd
from . import crud
from . import exceptions
from .db.database import get_db

from datetime import datetime, timedelta

import random

hash_context = CryptContext(schemes=[CRYPT_CONTEXT_SCHEME], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password) -> bool:
    """verfify users password

    Returns:
        bool: truthy for match

    Raises:
        exceptions.IncorrectPassword if passwords do not match, or if verify call raises exc

    """

    match = False

    try:
        match = hash_context.verify(plain_password, hashed_password)
    except [ValueError, TypeError] as e:
        raise exceptions.IncorrectPassword(
            context_msg=f"failure of hash_context.verify with {str(e)}"
        )

    if match:
        return match
    else:
        raise exceptions.IncorrectPassword(context_msg=f"failure to match")


def get_password_hash(password: str) -> str:
    return hash_context.hash(password)

def verify_passcode(plain_passcode, hashed_passcode) -> bool:
    """verfify users passcode

    Returns:
        bool: truthy for match

    Raises:
        exceptions.IncorrectPassword if passwords do not match, or if verify call raises exc

    """

    match = False

    try:
        match = hash_context.verify(plain_passcode, hashed_passcode)
    except [ValueError, TypeError] as e:
        raise exceptions.IncorrectPasscode(
            context_msg=f"failure of hash_context.verify with {str(e)}"
        )

    if match:
        return match
    else:
        raise exceptions.IncorrectPasscode(context_msg=f"failure to match")

def get_passcode_hash(passcode: int) -> str:
    return hash_context.hash(passcode)

def authenticate_user_password_flow(db: Session, email: str, password: str) -> sql.User:
    """Finds the user in the db and checks their stored password

    Used in the /token endpoint

    Returns:
        sql.User

    Raises:
        exceptions.UserNotFound,
        exceptions.IncorrectPassword
    """

    try:
        user = crud.read_user_by_email(db, email)
    except exceptions.UserNotFound as e:
        raise exceptions.UserNotFound(
            detail="user not found",
            context_msg="reading user by email in auth user",
            context_data={"email": email},
        )

    try:
        verify_password(password, user.hashed_password)
    except exceptions.IncorrectPassword as e:
        raise exceptions.IncorrectPassword(detail="password verification error")

    return user



def authenticate_user_passcode_flow(db: Session, email: str, passcode: int):
    """

    Used in the /passcode_token endpoint

    Look up user in db to check exists
    Look up latest passcode for that user from passcodes table
        passcode func will handle no, or invalid passcode for user
    verift the cupplied passcode against supplied

    if verfies return user


    """

    try:
        user = crud.read_user_by_email(db=db, email=email)
    except exceptions.UserNotFound as e:
        rai

    ...







def create_access_token(data: dict, expires_delta: str):
    """Compose the JWT with encoded claims and expiry

    Returns:
        encoded_jwt: str

    Raises;
        TypeError: if args are not of correct type
        ValueError: if values are un-encodable

    """
    if not isinstance(data, dict) or not isinstance(expires_delta, str):
        raise TypeError(f"wrong type(s) passed to create JWT")

    to_encode = data.copy()

    expires = datetime.utcnow() + timedelta(days=int(expires_delta))

    to_encode.update({"exp": expires})

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        return encoded_jwt
    except JWTError:
        raise ValueError


def get_current_user(
    db: Session = Depends(get_db), access_token: str = Depends(oauth2_scheme)
):
    """Checks provided access_token is valid and if so, looks up user using the email in "sub" of claims.

    Used as a base dependency.

    - valid JWT (not in blacklist)
    - email is in JWT
    - email is in db

    Returns:
        sql.User

    """

    # TODO http exception in wrong layer
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # check if jwt  is in blacklist
        if crud.access_token_is_blacklisted(db=db, access_token=access_token):
            # if it is in blacklist raise an exception, client can handle redirect to relogin
            # TODO http exception in wrong layer
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="session expired, please log in again",
            )

        # if not in blacklist proceed
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: int = payload.get("sub")  # check if there is a "sub" claim in the JWT
        if email is None:  # if there is no "sub", then could not authenticate
            # TODO http exception in wrong layer
            raise credentials_exception

    except JWTError:
        # handle some decode error, perhaps if JWT is malformed due to network interrupt or soemthing.
        # TODO http exception in wrong layer
        raise credentials_exception
    # check if the user is in the db using the email we decoded out from the JWT "sub" field

    try:
        user = crud.read_user_by_email(db, email)
    except exceptions.UserNotFound:
        # TODO http exception in wrong layer
        raise credentials_exception

    # if it fails to find a user, again raise auth expcetion
    if not user:
        # TODO http exception in wrong layer
        raise credentials_exception

    # if it does find the user, return all the user data
    return user


def get_current_admin_user(
    current_user: pyd.User = Depends(get_current_user),
):
    """Checks if the current user is an admin and verified.

    If so, returns UserInDb pydantic instance"""

    if current_user.is_admin:
        return current_user
    else:
        # TODO http exception in wrong layer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="not an admin user"
        )
