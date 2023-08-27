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


def create_panel_by_user_id(
    db: Session,
    user_id: int,
    title: str,
    position: int | None = None,
    description: str = None,
):
    """create a panel for a user by id"""

    user = db.query(sql.User).where(sql.User.id == user_id).first()

    try:
        if description:
            new_panel = sql.Panel(
                title=title, description=description, user_id=user_id, position=position
            )
        else:
            new_panel = sql.Panel(title=title, user_id=user_id, position=position)

        user.panels.append(new_panel)
        db.commit()
        return new_panel
    except SQLAlchemyError as e:
        raise PanelNotCreated(e)


def update_panel_by_id(db: Session, user_id: int, panel_id: int, update: dict):
    """
    update dict will contain only the fields to be updated
    grab the panel, assing the new value, commit

    return the upate panel instance
    """
    if update:
        panel = db.query(sql.Panel).filter(sql.Panel.id == panel_id).first()

        if panel:
            for update_field, update_value in update.items():
                if hasattr(panel, update_field):
                    if update_field == "position":
                        print()
                        print(f"RUNNING udpate fpr {update_field}")

                        print(f"running sort on {panel.title=}")
                        panel_sort_on_update(db, user_id, panel_id, update_value)
                    else:
                        print(f"RUNNING udpate fpr {update_field}")
                        setattr(panel, update_field, update_value)
                        try:
                            db.commit()
                        except Exception as e:
                            raise PanelNotUpdated(f"some issue in this commit {e}")
                else:
                    raise PanelNotUpdated(f"no field '{update_field}' found on panel")
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
        # capture pos for re-sort on delete
        panel_pos = panel.position

        db.delete(panel)
        db.commit()

        # call re-sort here
        # TODO this needs erorr handled as if
        try:
            panel_sort_on_delete(db=db, del_panel_pos=panel_pos, user_id=user_id)
        except PanelNotUpdated:
            pass

        return True
    else:
        raise PanelNotDeleted


def read_all_panels(db: Session) -> list:
    """read all panels for all users"""

    panels = db.query(sql.Panel).all()

    return panels


def read_all_panels_by_user(db: Session, user_id: int) -> list:
    """Returns a list of all panels for a user sorted by position"""

    panels = (
        db.query(sql.Panel)
        .join(sql.User)
        .where(sql.User.id == user_id)
        .order_by(sql.Panel.position)
        .all()
    )

    return panels


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
    """return only the latest status for each panel belonging to a user
    ie the up do date daily view

    TODO examine if this can be refactored into the db, and i think it can be optimised

    """

    panels = read_all_panels_by_user(db=db, user_id=user_id)

    panels_with_latest_entry_only = []

    now = datetime.utcnow()
    # mock now for testing as one day ahead of entries
    # now = now + timedelta(days=1)
    trimmed_now = now.replace(hour=0, minute=0, second=0, microsecond=1)

    for panel in panels:
        # convert the user_panel to a regular dict:
        panel_d = instance_to_dict(panel)
        # pp.pprint("user_panel_d in loop:", user_panel_d )

        # clear the list of entries on the object: TODO this is a hack
        panel_d["entries"] = []

        # get the current entry for the panel
        current_entry = (
            db.query(sql.Entry)
            .where(sql.Entry.panel_id == panel_d["id"])
            .where(sql.Entry.timestamp > trimmed_now)
            .order_by(sql.Entry.timestamp.desc())
            .first()
        )

        if current_entry:
            current_entry_d = instance_to_dict(current_entry)
            panel_d["entries"].append(current_entry_d)

        panels_with_latest_entry_only.append(panel_d)

    return panels_with_latest_entry_only


def set_null_panel_position_to_index(db: Session, user_id: int) -> bool:
    """This is to fix null positions on panels


    Look up all panels for a user, unsorted - assume no position
    TODO add sort flag to get_panels_by_user_id
    check each panel for a position, loop enum get index
    if a position, including 0s, check by being an int, skip
    if position is null and null only


    """
    pass


def panel_sort_on_update(db: Session, user_id: int, panel_id: int, new_pos: int):
    panels = read_all_panels_by_user(db=db, user_id=user_id)
    for p in panels:
        print(p.position, p.title)

    max_pos = len(panels) - 1
    print(f"{max_pos=}")
    min_pos = 0

    for i, panel in enumerate(panels):
        if panel.id == panel_id:
            panel_to_move = panel  # essentially saved to memeory
            panel_to_move_cur_index = i

    if panel_to_move.position:
        cur_pos = panel_to_move.position
    else:
        cur_pos = panel_to_move_cur_index

    # remove from the list that will be iterated over to update the other positions
    # this panel will have had its position update already in the caller func
    panels.pop(panel_to_move_cur_index)
    print(f"moving {panel_to_move.title} from {cur_pos} -> {new_pos}")

    if new_pos != cur_pos:
        if new_pos <= max_pos:
            if new_pos >= min_pos:
                panel_to_move.position = new_pos
                try:
                    if new_pos < cur_pos:
                        for panel in panels:
                            # everything below the cur pos until the new_pos must be incremented by one
                            if panel.position < cur_pos and panel.position >= new_pos:
                                panel.position = panel.position + 1
                        db.commit()

                    if new_pos > cur_pos:
                        for panel in panels:
                            # everything above the cur pos until the new_pos must be decremented by one
                            if panel.position > cur_pos and panel.position <= new_pos:
                                panel.position = panel.position - 1
                        db.commit()
                except Exception as e:
                    raise PanelNotUpdated(f"wihtin the try block: {e}")

                user = db.query(sql.User).where(sql.User.id == user_id).first()
                user.panels.append(panel_to_move)
                db.commit()
        else:
            raise PanelNotUpdated(f"That's where the panel already is 🙂")

    else:
        raise PanelNotUpdated(f"That's where the panel already is 🙂")
    print("FINAL POSITIONS:")
    panels = read_all_panels_by_user(db=db, user_id=user_id)
    for p in panels:
        print(p.position, p.title)
    print("END ")


def panel_sort_on_delete(db: Session, del_panel_pos: int, user_id: int):
    """

    panel is gone from table, but know the positon it did occupy

    every panel above that position needs to be decremented by 1

    so if it del_panel_pos=0,
    loop all panels (that are left)
    if the panels pos > del_panel_pos, postion - 1
    else just leave it, so panel at pos 1 becomes pos 0, panel at pos 5, becomes 4 etc. yes

    for del_panel_pos =5
    panel pos 6 is decremented to 5, but not panel 4

    """

    panels = read_all_panels_by_user(db=db, user_id=user_id)

    try:
        for panel in panels:
            if panel.position > del_panel_pos:
                panel.position = panel.position - 1

        db.commit()
    except Exception as e:
        raise PanelNotUpdated(f"{str(e)}")
