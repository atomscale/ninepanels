from . import sqlmodels as sql
from .errors import UserNotCreated
from .errors import UserAlreadyExists
from .errors import UserNotFound
from .errors import UserNotDeleted
from .errors import EntryNotCreated
from .errors import PanelNotDeleted
from .errors import PanelNotCreated
from .errors import PanelNotUpdated

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

from datetime import datetime

from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)


def instance_to_dict(instance):
    _dict = {}
    for key in instance.__mapper__.c.keys():
        _dict[key] = getattr(instance, key)
    return _dict


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
    except TypeError as e:
        msg = f"error creating new user"
        logging.error(msg + str(e))
        db.rollback()
        raise UserNotCreated(msg)
    except IntegrityError as e:
        msg = f"error creating new user"
        logging.error(msg + str(e))
        db.rollback()
        raise UserAlreadyExists(msg)

    return user


def read_user_by_id(db: Session, user_id: int):
    """read user by user_id"""

    user = db.query(sql.User).where(sql.User.id == user_id).first()

    if user:
        return user
    else:
        raise UserNotFound


def delete_user_by_id(db: Session, user_id: int):
    """delete a user by id"""

    user = db.query(sql.User).where(sql.User.id == user_id).first()

    if user:
        db.delete(user)
        db.commit()
        return True  # TODO what is the best way to confirmt he success of a delete op?
    else:
        raise UserNotDeleted


def read_user_by_email(db: Session, email: str):
    """read user by email"""

    user = db.query(sql.User).where(sql.User.email == email).first()

    return user


def read_all_users(db: Session) -> list:
    """read all users in the db"""

    users = db.query(sql.User).all()

    return users


def create_panel_by_user_id(db: Session, user_id: int, title: str):
    """create a panel for a user by id"""

    user = db.query(sql.User).where(sql.User.id == user_id).first()

    try:
        new_panel = sql.Panel(title=title, user_id=user_id)
        user.panels.append(new_panel)
        db.commit()
        return new_panel
    except SQLAlchemyError as e:
        raise PanelNotCreated(e)


def update_panel_by_id(db: Session, panel_id: int, update: dict):
    """assume the 'update' dict has been validated by pydantic
    update dict will contain only the fields to be updated, min len 1, max len unknown
    grab the panel, assing the new value, commit

    return the upate panel instance
    """
    if update:


        panel = db.query(sql.Panel).filter(sql.Panel.id == panel_id).first()
        # print(panel.title)
        if panel:
            for update_field, update_value in update.items():
                if hasattr(panel, update_field):
                    setattr(panel, update_field, update_value)
                else:
                    raise PanelNotUpdated(f"no field '{update_field}' found on panel")
            print(update)
            print(panel.id)
            # print(panel.title)
            try:
                db.commit()
            except Exception as e:
                raise PanelNotUpdated(f"some issue in this commit {e}")
            return panel
        else:
            raise PanelNotUpdated(f"panel with id {panel_id} not found")

    else:
        raise PanelNotUpdated(f"no update body in call to ")


def delete_panel_by_panel_id(db: Session, user_id: int, panel_id: int) -> bool:
    """delete a panel by panel id, constrained to user_id

    returns: true on success

    raises: PanelNotDeleted on failure
    """

    panel = (
        db.query(sql.Panel)
        .join(sql.User)
        .filter(sql.Panel.id == panel_id)
        .filter(sql.User.id == user_id)
        .first()
    )

    if panel:
        db.delete(panel)
        db.commit()
        return True
    else:
        raise PanelNotDeleted


def read_all_panels(db: Session) -> list:
    """read all panels for all users"""

    panels = db.query(sql.Panel).all()

    return panels


def read_all_panels_by_user_id(db: Session, user_id: int) -> list:
    """read all panels  by user id"""

    user_panels = db.query(sql.Panel).join(sql.User).where(sql.User.id == user_id).all()

    return user_panels


def create_entry_by_panel_id(
    db: Session, is_complete: bool, panel_id: int, user_id: int
):
    """Create an entry in the db. Appends timestamp in utc

    Args:
        db: an sqlalchemy Session instance
        new_entry: a pydantic model with new entry data

    Returns:
        entry: an sqlalchemy Entry instance

    Raises:
        EntryNotCreated: the new entry was not created

    """

    panel = db.query(sql.Panel).where(sql.Panel.id == panel_id).first()

    # check user_id on panel matches supplied user_id
    if not panel.user_id == user_id:
        msg = f"error creating new entry"
        logging.error(msg)
        raise EntryNotCreated(msg)

    try:
        entry = sql.Entry(
            is_complete=is_complete, panel_id=panel_id, timestamp=datetime.utcnow()
        )
        panel.entries.append(entry)
        db.commit()

    except (SQLAlchemyError, TypeError, IntegrityError) as e:
        msg = f"error creating new entry"
        logging.error(msg + str(e))
        db.rollback()
        raise EntryNotCreated(msg)

    return entry


def read_all_entries(db: Session) -> list:
    """read all entries for all users"""

    entries = db.query(sql.Entry).all()

    return entries


def read_panels_with_current_entry_by_user_id(db: Session, user_id: int) -> list[dict]:
    """return only the latest status for each panel belonging to a user"""

    user_panels = db.query(sql.Panel).join(sql.User).where(sql.User.id == user_id).all()

    user_panels_with_latest_entry_only = []

    now = datetime.utcnow()
    # mock now for testing as one day ahead of entries
    # now = now + timedelta(days=1)
    trimmed_now = now.replace(hour=0, minute=0, second=0, microsecond=1)

    for user_panel in user_panels:
        # convert the user_panel to a regular dict:
        user_panel_d = instance_to_dict(user_panel)
        # pp.pprint("user_panel_d in loop:", user_panel_d )

        # clear the list of entries on the object: TODO this is a hack
        user_panel_d["entries"] = []

        # get the current entry for the panel
        current_entry = (
            db.query(sql.Entry)
            .where(sql.Entry.panel_id == user_panel_d["id"])
            .where(sql.Entry.timestamp > trimmed_now)
            .order_by(sql.Entry.timestamp.desc())
            .first()
        )

        if current_entry:
            current_entry_d = instance_to_dict(current_entry)
            user_panel_d["entries"].append(current_entry_d)

        user_panels_with_latest_entry_only.append(user_panel_d)

    return user_panels_with_latest_entry_only
