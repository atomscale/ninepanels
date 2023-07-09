from . import sqlmodels as sql
from .errors import UserNotCreated

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import OperationalError



def create_user(db: Session, new_user: dict):
    """Create a user in the db.

    Args:
        db: an sqlalchemy Session instance
        new_user: a dict with new user data

    Returns:
        new_user: an sqlalchemy User instance

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
    """ read all users in the db """

    users = db.query(sql.User).all()

    return users

def read_all_panels(db: Session) -> list:
    """ read all panels for all users """

    panels = db.query(sql.Panel).all()

    return panels

def read_all_entries(db: Session) -> list:
    """ read all entries for all users """

    entries = db.query(sql.Entry).all()

    return entries

def read_latest_panel_status_for_user(db: Session, user_id: int) -> list:
    """ return only the latest status for each panel belonging to a user """

    all_user_panels = (
        db.query(sql.Panel)
        .join(sql.User)
        .where(sql.User.id == user_id)
        .all()
    )

    latest_user_panels = []

    for panel in all_user_panels:
        latest_panel = (
            db.query(sql.Entry)
            .where(sql.Entry.panel_id == panel.id)
            .order_by(sql.Entry.timestamp.desc())
            .first()
        )

        if latest_panel:
            latest_user_panels.append(latest_panel)

    return latest_user_panels