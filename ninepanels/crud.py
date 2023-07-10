from . import sqlmodels as sql
from . import pydmodels as pyd
from .errors import UserNotCreated
from .errors import EntryNotCreated

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import OperationalError

from datetime import datetime, timedelta


def create_user(db: Session, new_user: dict):
    """Create a user in the db.

    Args:
        db: an sqlalchemy Session instance
        new_user: a dict with new user data

    Returns:
        user: an sqlalchemy User instance

    Raises:
        UserNotCreated: the new user was not created

    """

    try:
        user = sql.User(**new_user)
        db.add(user)
        db.commit()
    except (SQLAlchemyError, TypeError, IntegrityError) as e:
        msg = f"error creating new user"
        logging.warning(msg + str(e))
        db.rollback()
        raise UserNotCreated(msg)

    return user


def read_all_users(db: Session) -> list:
    """read all users in the db"""

    users = db.query(sql.User).all()

    return users


def read_all_panels(db: Session) -> list:
    """read all panels for all users"""

    panels = db.query(sql.Panel).all()

    return panels

def read_all_panels_by_user_id(db: Session, user_id: int) -> list:
    """ read all panels  by user id"""

    user_panels = (
        db.query(sql.Panel)
        .join(sql.User)
        .where(sql.User.id == user_id)
        .all()
    )

    return user_panels

def create_entry_by_panel_id(db: Session, is_complete: bool, panel_id: int):
    """Create an entry in the db. Appends timestamp in utc

    Args:
        db: an sqlalchemy Session instance
        new_entry: a pydantic model with new entry data

    Returns:
        entry: an sqlalchemy Entry instance

    Raises:
        EntryNotCreated: the new entry was not created

    """

    try:
        panel = db.query(sql.Panel).where(sql.Panel.id == panel_id).first()
        entry = sql.Entry(
            is_complete=is_complete, panel_id=panel_id, timestamp=datetime.utcnow()
        )
        panel.entries.append(entry)
        db.commit()
    except (SQLAlchemyError, TypeError, IntegrityError) as e:
        msg = f"error creating new entry"
        logging.warning(msg + str(e))
        db.rollback()
        raise EntryNotCreated(msg)

    return entry


def read_all_entries(db: Session) -> list:
    """read all entries for all users"""

    entries = db.query(sql.Entry).all()

    return entries

def read_current_entries_by_user_id(db: Session, user_id: int) -> list:
    """return only the latest status for each panel belonging to a user"""

    all_user_panels = (
        db.query(sql.Panel).join(sql.User).where(sql.User.id == user_id).all()
    )

    latest_user_panels = []

    now = datetime.utcnow()
    # mock now for testing as one day ahead of entries
    # now = now + timedelta(days=1)
    trimmed_now = now.replace(hour=0, minute=0, second=0, microsecond=1)

    for panel in all_user_panels:
        latest_panel = (
            db.query(sql.Entry)
            .where(sql.Entry.panel_id == panel.id)
            .where(sql.Entry.timestamp > trimmed_now)
            .order_by(sql.Entry.timestamp.desc())
            .first()
        )

        if latest_panel:
            latest_user_panels.append(latest_panel)

    return latest_user_panels






