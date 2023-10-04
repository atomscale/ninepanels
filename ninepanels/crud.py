import pytz
import logging
import uuid

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta

from pprint import PrettyPrinter

from . import sqlmodels as sql
from . import exceptions
from . import utils
from .core import config


pp = PrettyPrinter(indent=4)


def create_user(db: Session, new_user: dict) -> sql.User:
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
    except IntegrityError as e:
        db.rollback()
        raise exceptions.UserNotCreated(
            detail=f"Do you have an account already?",
            context_msg=f"user not created due to account exisitng and integrity error: {str(e)}",
            **new_user,
        )
    except (SQLAlchemyError, TypeError) as e:
        db.rollback()

        raise exceptions.UserNotCreated(
            detail=f"Error creating your account",
            context_msg=f"user not created due to: {str(e)}",
            **new_user,
        )

    return user


def read_user_by_id(db: Session, user_id: int) -> sql.User:
    """read user by user_id

    Returns:
        sql.User

    Raises:
        UserNotFound

    """

    try:
        user = db.query(sql.User).filter(sql.User.id == user_id).first()
    except SQLAlchemyError as e:
        raise exceptions.UserNotFound(detail=f"db error checking for {user_id=}")

    if user:
        return user
    else:
        raise exceptions.UserNotFound(detail=f"user not found")


def read_user_by_email(db: Session, email: str) -> sql.User:
    """read user by email

    Returns
        sql.User

    Raises:
        UserNotFound - in case of DB error and not found
    """

    try:
        user = db.query(sql.User).filter(sql.User.email == email).first()
    except SQLAlchemyError as e:
        raise exceptions.UserNotFound(detail=f"db error {str(e)}")

    if user:
        return user
    else:
        raise exceptions.UserNotFound(
            detail=f"Email not found",
            context_msg="lookup of user by email failed",
            email=email,
        )


def read_all_users(db: Session) -> list[sql.User]:
    """read all users in the db"""

    users = db.query(sql.User).all()

    return users


def update_user_by_id(db: Session, user_id: str, update: dict) -> sql.User:
    """Update the user instance and commit to db

    Params:
        user_id
        update - a dict of the col: new_value.

    Returns:
        sql.User - the update user instance

    Raises:
        UserNotUpdated
    """

    try:
        user = read_user_by_id(db=db, user_id=user_id)
    except exceptions.UserNotFound:
        raise exceptions.UserNotUpdated(detail=f"user was not found {user_id=}")

    for col, new_value in update.items():
        if hasattr(user, col):
            setattr(user, col, new_value)
        else:
            raise exceptions.UserNotUpdated(
                detail=f"user instance does not have attr {col=}"
            )

    try:
        db.commit()
        return user
    except SQLAlchemyError as e:
        raise exceptions.UserNotUpdated(
            detail=f"db error writing updated user back to db {str(e)}"
        )


def delete_user_by_id(db: Session, user_id: int):
    """delete a user by id"""

    user = db.query(sql.User).where(sql.User.id == user_id).first()

    if user:
        db.delete(user)
        db.commit()
        return True  # TODO what is the best way to confirm the success of a delete op?
    else:
        raise exceptions.UserNotDeleted(user_id=user_id)


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
                created_at=datetime.utcnow(),
                title=title,
                description=description,
                user_id=user_id,
                position=position,
            )
        else:
            new_panel = sql.Panel(
                created_at=datetime.utcnow(),
                title=title,
                user_id=user_id,
                position=position,
            )

        user.panels.append(new_panel)
        db.commit()
        return new_panel
    except SQLAlchemyError as e:
        raise exceptions.PanelNotCreated(context_msg=str(e))


def read_all_panels_by_user_id(db: Session, user_id: int) -> list[sql.Panel]:
    """Returns a list of all panels for a user sorted by position

    Returns:
        List of sql.Panel instances - can be empty

    Raises:
        Panel Not Found - in all failure cases

    """

    try:
        panels = (
            db.query(sql.Panel)
            .join(sql.User)
            .filter(sql.User.id == user_id)
            .order_by(sql.Panel.position)
            .all()
        )
    except SQLAlchemyError as e:
        raise exceptions.PanelNotFound(
            detail=f"error in db call to find panels {str(e)}"
        )

    if panels:
        return panels


def read_panel_by_id(db: Session, panel_id: int, user_id: int) -> sql.Panel:
    """Read a panel by id and user_id to check ownership

    Returns:
        sql.Panel

    Raises:
        PanelNotFound
    """

    try:
        panel = (
            db.query(sql.Panel)
            .join(sql.User)
            .filter(sql.Panel.id == panel_id, sql.User.id == user_id)
            .first()
        )
    except SQLAlchemyError as e:
        raise exceptions.PanelNotFound(
            detail=f"panel not foudn due to db error: {str(e)}"
        )

    if panel:
        return panel
    else:
        raise exceptions.PanelNotFound(
            detail=f"panel with id {panel_id=} not found for user {user_id=}"
        )


def update_panel_by_id(
    db: Session, user_id: int, panel_id: int, update: dict
) -> sql.Panel:
    """
    update dict will contain only the fields to be updated
    grab the panel, assing the new value, commit

    Returns:
        sql.Panel - the update panel instance

    Raises:
        PanelNotUpdated - all failure cases
    """
    if update:
        try:
            panel = read_panel_by_id(db=db, panel_id=panel_id, user_id=user_id)
        except exceptions.PanelNotFound:
            raise exceptions.PanelNotUpdated(detail=f"Panel not found")

        if panel:
            for update_field, update_value in update.items():
                if hasattr(panel, update_field):
                    if update_field == "position":
                        # print()
                        # print(f"RUNNING udpate fpr {update_field}")

                        # print(f"running sort on {panel.title=}")
                        panel_sort_on_update(db, user_id, panel_id, update_value)
                    else:
                        # print(f"RUNNING udpate fpr {update_field}")
                        setattr(panel, update_field, update_value)
                        try:
                            db.commit()
                        except Exception as e:
                            raise exceptions.PanelNotUpdated(
                                detail=f"some issue in this commit {e}"
                            )
                else:
                    raise exceptions.PanelNotUpdated(
                        detail=f"no field '{update_field}' found on panel"
                    )
            return panel
        else:
            raise exceptions.PanelNotUpdated(
                detail=f"panel with id {panel_id} not found"
            )

    else:
        raise exceptions.PanelNotUpdated(detail=f"no update body in call to ")


def delete_panel_by_panel_id(db: Session, user_id: int, panel_id: int) -> bool:
    """delete a panel by panel id, constrained to user_id

    returns: true on success

    raises: PanelNotDeleted on failure
    """

    try:
        panel = (
            db.query(sql.Panel)
            .join(sql.User)
            .filter(sql.Panel.id == panel_id)
            .filter(sql.User.id == user_id)
            .first()
        )

        if not panel:
            raise exceptions.PanelNotDeleted(
                detail="Panel not found",
                context_msg="in outer scope of crud.py call",
                user_id=user_id,
                panel_id=panel_id,
            )

        panel_pos = panel.position

        db.delete(panel)
        db.commit()

        panel_sort_on_delete(db=db, del_panel_pos=panel_pos, user_id=user_id)

        return True

    except (SQLAlchemyError, exceptions.PanelNotUpdated) as e:
        db.rollback()
        raise exceptions.PanelNotDeleted(
            detail="panel was not updated",
            context_msg=f"transaction rolled back, panel was found, must be error in panel_sort_on_delete...: {str(e)}",
            user_id=user_id,
            panel_id=panel_id,
        )


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
        raise exceptions.EntryNotCreated(msg)

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
        raise exceptions.EntryNotCreated(msg)

    return entry


def read_panels_with_current_entry_by_user_id(db: Session, user_id: int) -> list[dict]:
    """return only the latest status for each panel belonging to a user
    ie the up do date daily view

    TODO examine if this can be refactored into the db call, and i think it can be optimised
    TODO this needs error handling

    """

    panels = read_all_panels_by_user_id(db=db, user_id=user_id)

    panels_with_latest_entry_only = []

    # could lookup user sepcified timezone once set in db, create it here
    uk_tz = pytz.timezone("Europe/London")
    now = datetime.now(uk_tz)
    # print(now)

    trimmed_now = now.replace(hour=0, minute=0, second=0, microsecond=1)

    if panels:
        for panel in panels:
            panel_d = utils.instance_to_dict(panel)

            current_entry = (
                db.query(sql.Entry)
                .where(sql.Entry.panel_id == panel_d["id"])
                .where(sql.Entry.timestamp > trimmed_now)
                .order_by(sql.Entry.timestamp.desc())
                .first()
            )

            if current_entry:
                current_entry_d = utils.instance_to_dict(current_entry)
                panel_d["is_complete"] = current_entry_d["is_complete"]
            else:
                panel_d["is_complete"] = False

            panels_with_latest_entry_only.append(panel_d)

    return panels_with_latest_entry_only


def read_entries_by_panel_id(
    db: Session,
    panel_id: int,
    offset: int,
    limit: int,
    sort_key: str,
    sort_direction: str,
):

    entries = (
        db.query(sql.Entry)
        .filter(sql.Entry.panel_id == panel_id)
        .order_by(getattr(getattr(sql.Entry, sort_key), sort_direction)())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return entries


def panel_sort_on_update(db: Session, user_id: int, panel_id: int, new_pos: int):
    """
    TODO this needs error hadnling
    """
    panels = read_all_panels_by_user_id(db=db, user_id=user_id)

    max_pos = len(panels) - 1

    min_pos = 0

    for i, panel in enumerate(panels):
        if panel.id == panel_id:
            panel_to_move = panel  # essentially saved to memeory
            panel_to_move_cur_index = i

    if panel_to_move.position:
        cur_pos = panel_to_move.position
    else:
        cur_pos = panel_to_move_cur_index

    panels.pop(panel_to_move_cur_index)

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
                    raise exceptions.PanelNotUpdated(f"wihtin the try block: {e}")

                user = db.query(sql.User).where(sql.User.id == user_id).first()
                user.panels.append(panel_to_move)
                db.commit()
        else:
            raise exceptions.PanelNotUpdated(f"That's where the panel already is 🙂")

    else:
        raise exceptions.PanelNotUpdated(f"That's where the panel already is 🙂")

    panels = read_all_panels_by_user_id(db=db, user_id=user_id)


def panel_sort_on_delete(db: Session, del_panel_pos: int, user_id: int) -> None:
    """Resort panels when a panel is deleted

    Returns: None
    Raises: PanelsNotSorted

    """

    try:
        panels = read_all_panels_by_user_id(db=db, user_id=user_id)
        for panel in panels:
            if panel.position > del_panel_pos:
                panel.position = panel.position - 1
        db.commit()
    except (SQLAlchemyError, AttributeError, TypeError, exceptions.PanelNotFound) as e:
        db.rollback()
        raise exceptions.PanelsNotSorted(context_msg=f"{str(e)}", user_id=user_id)


def today() -> datetime:
    """TODO wherever this is called it can just be 'date'"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return today


def calc_panel_age(created_at: datetime) -> int:
    panel_age = today() - created_at
    return panel_age.days + 2


def calc_consistency(db: Session, user_id: int):
    panels = read_all_panels_by_user_id(db=db, user_id=user_id)

    panel_consistencies = []
    if panels:
        for panel in panels:
            # print(f"Panel '{panel.title}':")

            panel_age = calc_panel_age(created_at=panel.created_at)
            # print(f"{panel_age=}")

            date_range = []
            start_date = panel.created_at
            start_date = start_date.replace(
                hour=23, minute=59, second=59, microsecond=100000
            )

            date_range = []
            date_range.append(start_date)

            day_counter = 0

            for i in range(panel_age):
                day_counter += 1
                new_date = start_date + timedelta(days=day_counter)
                date_range.append(new_date)

            # # pp.pprint(date_range)

            days_complete = 0
            for date in date_range:
                day_matches = []

                for entry in panel.entries:
                    if (
                        date.date() == entry.timestamp.date()
                    ):  #  TODO needs to compare whole dates
                        day_matches.append(entry)

                if day_matches:
                    sorted_day_match = sorted(
                        day_matches, key=lambda x: x.timestamp, reverse=True
                    )
                    if sorted_day_match[0].is_complete == True:
                        days_complete += 1

            if panel_age > 0:
                panel_consistency = days_complete / panel_age
            else:
                panel_consistency = 0
            # print(f"{days_complete=}")
            # print(f"consistency for panel '{panel.title}': {panel_consistency}")

            panel_consistencies.append(
                {
                    "panel_pos": panel.position,
                    "consistency": panel_consistency,
                    "panel_age": panel_age,
                    "days_complete": days_complete,
                }
            )

    return panel_consistencies


def delete_all_entries_by_panel_id(db: Session, user_id: int, panel_id: int) -> bool:
    panel = (
        db.query(sql.Panel)
        .join(sql.User)
        .filter(sql.User.id == user_id, sql.Panel.id == panel_id)
        .first()
    )

    if panel:
        try:
            panel.entries = []
            panel.created_at = datetime.utcnow()
            db.commit()
            return True
        except SQLAlchemyError as e:
            raise exceptions.EntriesNotDeleted(
                f"unable to delete entries on {panel_id=} for {user_id=} during db call"
            )
    else:
        raise exceptions.EntriesNotDeleted(
            f"unable to delete entries as no panel exists with that {panel_id=} for {user_id=}"
        )


def blacklist_an_access_token(
    db: Session, access_token: str
) -> sql.BlacklistedAccessToken:
    """Insert an entry in the table `blacklisted_access_tokens`.

    `blacklisted_at` is generated within this fucntion.

    Returns:
        sql.BlacklistedAccessToken: the new row from the db

    Raises:
        BlacklistedAccessTokenException if problems with db

    """

    access_token_to_blacklist = sql.BlacklistedAccessToken(
        access_token=access_token, blacklisted_at=datetime.utcnow()
    )
    try:
        db.add(access_token_to_blacklist)
        db.commit()
        return access_token_to_blacklist

    except SQLAlchemyError as e:
        raise exceptions.BlacklistedAccessTokenException(
            f"problem inserting token to blacklist table {str(e)}"
        )


def access_token_is_blacklisted(db: Session, access_token: str) -> bool:
    """lookup access_token in `blacklisted_access_tokens`

    Returns:
        true if token found - it has been blacklisted
        false if not found - it has not been blacklisted

    Raises:
        BlacklistedAccessTokenException if problems with db
    """
    try:
        blacklisted_access_token = (
            db.query(sql.BlacklistedAccessToken)
            .filter(sql.BlacklistedAccessToken.access_token == access_token)
            .first()
        )
    except SQLAlchemyError as e:
        raise exceptions.BlacklistedAccessTokenException(
            f"problem reading blacklist table {str(e)}"
        )

    if blacklisted_access_token:
        return True
    else:
        return False


def create_password_reset_token(
    db: Session, email: int, ts: datetime | None = None
) -> (sql.User, str):
    """Check user exists by email (This needs to work both for a logged in
    and logged out user based on email), create a random hash for token, store in db.

    db cols set in this function:
        `password_reset_token`
        `issued_at`
        `expiry`

    not set:
        `is_valid` - default to true in sqlmodel
        `invalidated_at` - remains null in db until invalidation

    Params:
        email: email address for a user
        ts: for testing only

    Returns:
        tuple of (
            sql.User - so that calling route can interpolate user identifiers in the url;
            token_hash - the token to be used as the password_reset_token

    Raises:
        PasswordResetTokenException(exception detail)

    """

    user = read_user_by_email(db=db, email=email)

    # TODO this needs error handled

    invalidate_all_user_prts(db=db, user_id=user.id)

    if user:
        token_hash = utils.generate_random_hash()

        if ts:
            password_reset_token_obj = sql.PasswordResetToken(
                password_reset_token=token_hash,
                issued_at=datetime.utcnow(),
                expiry=ts + timedelta(minutes=config.PASSWORD_ACCESS_TOKEN_MINUTES),
            )
        else:
            password_reset_token_obj = sql.PasswordResetToken(
                password_reset_token=token_hash,
                issued_at=datetime.utcnow(),
                expiry=datetime.utcnow()
                + timedelta(minutes=config.PASSWORD_ACCESS_TOKEN_MINUTES),
            )

        try:
            user.password_reset_tokens.append(password_reset_token_obj)
            db.commit()
            return user, token_hash
        except SQLAlchemyError as e:
            raise exceptions.PasswordResetTokenException(str(e))

    else:
        raise exceptions.UserNotFound("user not found")


def check_password_reset_token_is_valid(
    db: Session, password_reset_token: str, user_id: int
) -> bool:
    """Check if password reset token:
    - has expiry >= now
    - is_valid == True
    - user_id matches requesting user.id

    Returns:
        bool: true means is valid... false, not valid

    Raises:
        PasswordResetTokenException on db failure, passes failure in args

    """

    try:
        prt = (
            db.query(sql.PasswordResetToken)
            .filter(
                sql.PasswordResetToken.password_reset_token == password_reset_token,
                sql.PasswordResetToken.expiry >= datetime.utcnow(),
                sql.PasswordResetToken.is_valid == True,
                sql.PasswordResetToken.user_id == user_id,
            )
            .first()
        )
    except SQLAlchemyError as e:
        raise exceptions.PasswordResetTokenException(str(e))

    if prt:
        return True
    else:
        return False


def invalidate_password_reset_token(
    db: Session, password_reset_token: str, user_id
) -> sql.PasswordResetToken:
    """update the password_reset_tokens table to invalidate the prt

    Returns:
        updated sql.PasswordResetToken

    Raises:
        PasswordResetTokenException

    """

    try:
        prt = (
            db.query(sql.PasswordResetToken)
            .filter(
                sql.PasswordResetToken.password_reset_token == password_reset_token,
                sql.PasswordResetToken.expiry >= datetime.utcnow(),
                sql.PasswordResetToken.is_valid == True,
                sql.PasswordResetToken.user_id == user_id,
            )
            .first()
        )
    except SQLAlchemyError as e:
        raise exceptions.PasswordResetTokenException(str(e))

    if prt:
        try:
            prt.is_valid = False
            prt.invalidated_at = datetime.utcnow()
            db.commit()
            return prt
        except SQLAlchemyError as e:
            raise exceptions.PasswordResetTokenException(
                f"could not update prt {str(e)}"
            )
    else:
        raise exceptions.PasswordResetTokenException(f"prt does not exist {str(e)}")


def invalidate_all_user_prts(db: Session, user_id: int) -> None:
    """Invalidates all prior Password Reset Tokens (prts) for a user that:

    - belong to the user,
    - are currently valid

    Returns:
        None

    Raises:
        exceptions.PasswordResetTokenException if reading or updating prts fails

    """

    try:
        user_prts = (
            db.query(sql.PasswordResetToken)
            .filter(
                sql.PasswordResetToken.user_id == user_id,
                sql.PasswordResetToken.is_valid == True,
            )
            .all()
        )
    except SQLAlchemyError as e:
        raise exceptions.PasswordResetTokenException(
            context_msg="issue getting the prts from the db for the user",
            context_data={"user_id": user_id},
        )

    if user_prts:
        try:
            for prt in user_prts:
                prt.is_valid = False
                prt.invalidated_at = datetime.utcnow()
            db.commit()
        except SQLAlchemyError as e:
            raise exceptions.PasswordResetTokenException(
                context_msg="issue invalidating the prts for the user",
                context_data={"user_id": user_id},
            )


def read_all_routes(db: Session):
    method_paths = db.query(sql.TimingStats.method_path).distinct()

    output = []
    for method_path in method_paths:
        mp = method_path.method_path
        stats = (
            db.query(sql.TimingStats)
            .filter(sql.TimingStats.method_path == mp)
            .order_by(desc(sql.TimingStats.id))
            .first()
        )
        output.append(stats)

    return output


def read_route_timings(db: Session, method_path: str, window_size: int):
    timings = (
        db.query(sql.Timing)
        .filter(sql.Timing.method_path == method_path)
        .order_by(desc(sql.Timing.created_at))
        .limit(window_size)
        .all()
    )

    output = {
        "readings": [t.diff_ms for t in timings],
        "timestamps": [t.created_at for t in timings],
    }

    return output

def read_panel_created_date(db: Session, panel_id: int) -> datetime:

    panel = db.query(sql.Panel).filter(sql.Panel.id == panel_id).first()

    panel_created = panel.created_at

    return panel_created.date()

def pad_entries(db: Session, unpadded_entries: list[sql.Entry], limit: int, panel_id: int) -> list[dict]:


    today = datetime.utcnow().date()

    padded_entries = []

    panel_created_at = read_panel_created_date(db=db, panel_id=panel_id)
    panel_age_td: timedelta = (today - panel_created_at)
    lookback_days: int = panel_age_td.days +1

    if lookback_days > limit:
        lookback_days = limit


    date_range = []
    for n in range(lookback_days):
        d = today + timedelta(days=-n)
        date_range.append(d)


    for date in date_range:
        existing_entry = None
        for entry in unpadded_entries:
            entry_date = entry.timestamp.date()
            if entry_date == date:
                existing_entry = entry
                break
        if existing_entry:
            padded_entries.append(utils.instance_to_dict(existing_entry))
        else:
            padded_entries.append({
                'id': f"{str(uuid.uuid4())}_padded",
                "is_complete": False,
                "timestamp": date,
                "panel_id": panel_id
            })

    return padded_entries