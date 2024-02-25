from datetime import datetime
from datetime import date
from datetime import timedelta
import random

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..db import crud
from .. import pydmodels as pyd
from .. import sqlmodels as sql
from .. import exceptions
from .. import utils


def all_panels_with_current_entry_by_user_id(db: Session, user_id: int) -> list[dict]:
    """DEPRECATED

    return only the latest status for each panel belonging to a user
    ie the up do date daily view

    TODO examine if this can be refactored into the db call, and i think it can be optimised
    TODO this needs error handling

    """

    panels = crud.read_all_panels_by_user_id(db=db, user_id=user_id)

    panels_with_latest_entry_only = []

    if panels:
        for panel in panels:
            panel_d = utils.instance_to_dict(panel)

            panel_id = panel_d["id"]

            current_entry = crud.read_current_entry_by_panel_id(
                db=db, panel_id=panel_id
            )

            if current_entry:
                current_entry_d = utils.instance_to_dict(current_entry)
                panel_d["is_complete"] = current_entry_d["is_complete"]
            else:
                panel_d["is_complete"] = False

            panels_with_latest_entry_only.append(panel_d)

    return panels_with_latest_entry_only


# as panel.graph
graph_response_model = {
    "days": [
        {
            "panel_date": "dd.mm.YYYY",  # 0 index must always be a sunday ie have day_of_week == 6
            "is_complete": False,  # reads from entries tabel to derive this using current functionality ish
            "is_pad": True,  # can not render any visible ui for this, exlucded from stats.
            # "is_paused": False, # can set hasehd border on this
            # "has_note": False, # sticking with current fucntionality just for now
            "id": 1234,  # or random hash generated for pad
            "panel_id": 267,  # as normal
            "last_updated": "ts",
            # "user_id": 1, # future proof for a global query perhaps?    NO, this is denoramilsing the data schem before necessity is clear
            "day_of_week": 3,  # for ui month border render, 0 = Mon, 6 = sun, and USED for padding. nice.
            "day_date": 24,  # max 31 etc, the dd part of timestamp.
        },
        # test padding: len must always be a multiple of 7 (+1) using the ~ thing?, min len 1
        # test padding: zero index must always be day_of_week == 6 and [-1] must always be a monday after padding opeation
        # test: all day_grids can never be all padded.
        # i feel like this grid array coudl be persisted, replacing entries table completely, called panel_day
        #   would allow really realible sorting on timestamp from sql
        #   and fast reteival
        # logic to update a panel's completion status is about updating the panel_day
        # select from panel_days by panel_id where date = today
        # if not there, create new panel_days using an update_to_today type function:
        # and create backwards until find one incrementingthe day each time
        # set to is_complete = false, is_pad = false etc
        # this means table is updted even if no writes for many days, updatign itself on every write
        # frist day write is done during panel create so will always find that one
        # if panel_day is there, just toggle is_complete in the table row
        # with panel_days, padding becomes easier:
        # read all panel days sorted desc by timestamp sql query (nice reusbale func)
        # if panel_day[0].day_of_week is not 6:
        # add in 6 - day_of_week pad entries, incremting date by 6 - day owf week days
        # if panel_day[-1].day_of_week is not 0, pad accordingly. nice.
        # resetggin of panels each day can be achived using a last_updated date on the panel itself: may not even be needed if panel_days logic is performed on read too
        # currently panel does not have actual is_complete in schema, its a vitrual response field, lets keep it that way for now, or make it more explicit
        # where the panel is_cmpleote status is the is_complete of the 0th index posiiton in panel.graph of response payload, lets assume they all, always, come together YES
        # to read a panel, GET req comes in
        # with panel_id in url? lets say yes for now (an ALL route can be constructed later)
        # read from panels table with id
        # if last_updated date of panel is same as current date (as per user time, needs implemented)
        # read panel_days, assemble response data and send, no need to run update to today function?
        # if its not the same
        # run the update_to_today type function to complete missed days on panel_days back to a previous entry
        # then assemble the response data
        # tapping a day on the grid is a very close feature, does this schema support that?
        # yes, a day tap in the grid opens a rightTray with props of the day that has all the required data
        # from there notes coudl be fetched (future) and a form field coudl perform an update to a day (planned):
        # need a PATCH day route, using the day based limits for updating day status.
    ],
    "stats": {
        # derive after day_grid is assembled
        "full_age_days": 176,  # including paused in count, exclude is_pad - just calc_age function usign panel.created_at
        # "unpaused_age_days": 144, # need a new fucn to sum just paused for a pnel in a sql query
        "complete_days": 98,  # do i have func for this?
        # further things like longest streka etc if needed. ALL calced on server
    },
    "week_column": [
        # funciton outline to generate week column:
        # loop through day grid after assembly
        # chunk into 7 len arrays of day_dates (equating to weeks)
        # if 1 is in array of day dates, insert the mm yy of that 1, ie "Jan 24"
        # else insert null:
        None,
        "Jan 24",
        None,
        None,
        None,
        None,
        "Dec 23",  # render in ui separately just mathcing row height of graph
    ],
}


def fill_missed_days(db: Session, current_user_date: datetime, panel_id: int) -> None:
    """Coordinate the assessment and creation of Days

    is_complete = False, is_filled = True, is_pad = False

    Attrs:
        db
        current_user_date
        panel_id

    Returns:
        None

    Raises:
        exceptions.FillMissedDaysException

    """

    try:
        most_recent_day: sql.Day = crud.read_most_recent_day_for_panel(
            db=db, panel_id=panel_id
        )
    except SQLAlchemyError as e:
        raise exceptions.FillMissedDaysException(
            f"exc in reading most recent day {str(e)}"
        )

    last_date: date = most_recent_day.panel_date.date()

    if current_user_date > last_date:
        td: timedelta = current_user_date - last_date

        fill_list = []
        for i in range(td.days):

            filled_date = current_user_date - timedelta(days=i)

            filler_day = pyd.DayCreate(
                panel_date=filled_date,
                day_of_week=filled_date.weekday(),
                day_date_num=filled_date.day,
                last_updated=datetime.utcnow(),
                is_complete=False,
                is_pad=False,
                is_fill=True,
                panel_id=panel_id,
            )

            fill_list.append(sql.Day(**filler_day.model_dump()))

        try:
            crud.create_filled_days(db=db, filled_days=fill_list)
        except SQLAlchemyError as e:
            raise exceptions.FillMissedDaysException(
                f"exc in writing filled days to db {str(e)}"
            )

        return True


def calculate_panel_stats(days: list[dict | sql.Day]) -> dict:
    """Calc stats for given list of days

    Returns:
        dict of stats

    MOCKING AN EMTPY DICT RETURN

    """

    return {}


def calculate_panel_week_column(days: list[dict | sql.Day]) -> list:
    """Create the list of weeks tobe used in graph

    MOCKING AN EMPTY LIST RETURN

    """

    return []


def pad_days_to_grid(arr: list[sql.Day], panel_id: int) -> list[dict]:
    """Ensures response is padded for nx7 grid
    Called every time to form panel.graph.days

    Returns:
        list of dict objects of both actual day instances and created padded ones

    """

    try:
        padded = [*arr]

        # pad start
        if arr[0].day_of_week != 6:
            days_to_pad = 6 - arr[0].day_of_week
            for i in range(0, days_to_pad):
                pad_date = arr[0].panel_date + timedelta(days=days_to_pad - i)
                pad_day = {
                    "day_of_week": pad_date.weekday(),
                    "day_date_num": pad_date.day,
                    "panel_id": panel_id,
                    "is_complete": False,
                    "is_fill": False,
                    "last_updated": datetime.utcnow(),
                    "id": random.randint(1_000_000_000, 9_999_999_999),
                    "is_pad": True,
                    "panel_date": pad_date,
                }
                padded.insert(i, pad_day)

        # pad end
        if arr[-1].day_of_week != 0:
            days_to_pad = arr[-1].day_of_week
            for i in range(days_to_pad):
                pad_date = arr[-1].panel_date - timedelta(days=i + 1)
                pad_day = {
                    "day_of_week": pad_date.weekday(),
                    "day_date_num": pad_date.day,
                    "panel_id": panel_id,
                    "is_complete": False,
                    "is_fill": False,
                    "last_updated": datetime.utcnow(),
                    "id": random.randint(1_000_000_000, 9_999_999_999),
                    "is_pad": True,
                    "panel_date": pad_date,
                }
                padded.append(pad_day)
    except Exception as e:
        # TODO refine exc type as
        raise exceptions.PadDaysException(f"could not pad days: {str(e)}")

    return padded


def orchestrate_panel_response(
    db: Session, panel_id: int, user_id: int, current_user_date: date | None = None
) -> pyd.PanelResponse:
    """Coordinate the assembly of a full panel response instance.
    Utilise in all areas where a panel or panels is returned.



    Attrs:
        db: Session
        panel_id: int
        user_id: int
        current_user_date: optional datetime, for testing

    Returns:
        pyd.PanelResponse instance

    Raises:
        exceptions.OrchestratePanelResponseException
    """

    # get the user's current time

    if current_user_date is None:
        try:
            user_ts: datetime = crud.read_user_current_time(db=db, user_id=user_id)
        except Exception as e:
            # TODO refine exc type as
            raise exceptions.OrchestratePanelResponseException(
                f"could not read current user time: {str(e)}"
            )
        current_user_date: date = user_ts.date()

    # read the panel
    try:
        panel: sql.Panel = crud.read_panel_by_id(
            db=db, panel_id=panel_id, user_id=user_id
        )
        panel: dict = utils.instance_to_dict(panel)
    except exceptions.PanelNotFound as e:
        # TODO refine exc type as
        raise exceptions.OrchestratePanelResponseException(
            f"could not read panel {str(e)}"
        )

    panel_last_date: date = panel["last_updated"].date()

    if panel_last_date != current_user_date:
        fill_missed_days(db=db, current_user_date=current_user_date, panel_id=panel_id)

    try:
        raw_days = crud.read_days_for_panel(db=db, panel_id=panel_id)
    except exceptions.DayNotFound as e:
        # TODO refine exc type as
        raise exceptions.OrchestratePanelResponseException(
            f"could not read days for panel: {str(e)}"
        )

    try:
        padded_days = pad_days_to_grid(arr=raw_days, panel_id=panel_id)
    except exceptions.PadDaysException as e:
        # TODO refine exc type as
        raise exceptions.OrchestratePanelResponseException(
            f"could nor read current user time: {str(e)}"
        )

    stats = calculate_panel_stats(days=raw_days)
    week_column = calculate_panel_week_column(days=padded_days)

    panel_response: dict = {
        **panel,
        "is_complete": raw_days[0].is_complete,
        "day_id": raw_days[0].id,
        "graph": {"days": padded_days, "stats": stats, "week_column": week_column},
    }

    panel: pyd.PanelResponse = pyd.PanelResponse(**panel_response)

    return panel


def orchestrate_panel_create(
    db: Session, user_id: int, new_panel: pyd.PanelCreate
) -> pyd.PanelResponse:
    """Orchestrates the creation of a panel

    - creates Panel
    - creates associated Day

    Returns
        pyd.PanelResponse ready to http out the door ;)

    """

    # create panel

    new_panel = crud.create_panel_by_user_id(
        db, user_id=user_id, **new_panel.model_dump()
    )
    # create Day
    user_current_day = crud.read_user_current_time(db=db, user_id=user_id).date()

    new_day = pyd.DayCreate(
        panel_date=user_current_day,
        day_of_week=user_current_day.weekday(),
        day_date_num=user_current_day.day,
        last_updated=datetime.utcnow(),
        is_complete=False,
        is_pad=False,
        is_fill=False,
        panel_id=new_panel.id,
    )

    new_day = crud.create_day(db=db, new_day=new_day)

    if new_day and new_panel:

        panel: pyd.PanelResponse = orchestrate_panel_response(
            db=db, panel_id=new_panel.id, user_id=new_panel.user_id
        )

        return panel


def orchestrate_panel_update(
    db: Session, user_id: int, panel_id: int, update: dict
) -> pyd.PanelResponse:
    """Coordinate a panel udpate

    Returns:
        pyd.PanelResponse with updated panel
    """

    # if update to title or desc just call reg update func

    if "is_complete" not in update.keys():
        try:
            updated_panel = crud.update_panel_by_id(
                db=db, user_id=user_id, panel_id=panel_id, update=update
            )
        except exceptions.PanelNotUpdated as e:
            # TODO emit event
            raise exceptions.OrchestratePanelUpdateException(
                f"panel update orch service layer exc at update for not _is_complete: {str(e)}"
            )

    # if a toggle of is_complete (which is virtual, not a panel attr but a panel.graph[0] surfaced element)
    # then

    if "is_complete" in update.keys():
        if "day_id" not in update.keys():
            raise exceptions.OrchestratePanelUpdateException(
                f"day_id is missing from is_complete request"
            )

        # drop day_id from update dict as do not wnat to update the id in the Days table
        day_id = update["day_id"]
        del update["day_id"]

        try:
            updated_day: sql.Day = crud.update_day_completion_by_id(
                db=db, day_id=day_id, update=update
            )
        except exceptions.DayNotUpdated as e:
            raise exceptions.OrchestratePanelUpdateException(f"exc in day update for is_complete")


    # then call orch response
    try:
        panel_response: pyd.PanelResponse = orchestrate_panel_response(
            db=db, panel_id=panel_id, user_id=user_id
        )
    except exceptions.OrchestratePanelResponseException as e:
        # TODO emit event
        raise exceptions.OrchestratePanelUpdateException(
            f"panel update orch service layer exc at update for not _is_complete: {str(e)}"
        )

    return panel_response
