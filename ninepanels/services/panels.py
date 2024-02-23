from datetime import datetime
import pytz

from sqlalchemy.orm import Session

from ..db import crud
from .. import utils


def all_panels_with_current_entry_by_user_id(db: Session, user_id: int) -> list[dict]:
    """return only the latest status for each panel belonging to a user
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
            "timestamp": "dd.mm.YYYY", # 0 index must always be a sunday ie have day_of_week == 6
            "is_complete": False, # reads from entries tabel to derive this using current functionality ish
            "is_pad": True, # can not render any visible ui for this, exlucded from stats.
            # "is_paused": False, # can set hasehd border on this
            # "has_note": False, # sticking with current fucntionality just for now
            "id": 1234, # or random hash generated for pad
            "panel_id": 267, # as normal
            # "user_id": 1, # future proof for a global query perhaps?    NO, this is denoramilsing the data schem before necessity is clear
            "day_of_week": 3, # for ui month border render, 0 = Mon, 6 = sun, and USED for padding. nice.
            "day_date": 24 # max 31 etc, the dd part of timestamp.
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
                # read panel_days, assemble response data and send
            # if its not the same
                # run the update_to_today type function to complete missed days on panel_days back to a previous entry
                # then assemble the response data

        # tapping a day on the grid is a very clsoe feature, does this schema support that?
        # yes, a day tap in the grid opena rightTray with props of the day that has all the required data
        # from there notes coudl be fetched (future) and a form field coudl perform an update to a day (planned):
            # need a PATCH day route, using the day based limits for updating day status.


    ],
    "stats": {
        # derive after day_grid is assembled
        "full_age_days": 176, # including paused in count, exclude is_pad - just calc_age function usign panel.created_at
        # "unpaused_age_days": 144, # need a new fucn to sum just paused for a pnel in a sql query
        "complete_days": 98 # do i have func for this?
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
        "Dec 23" # render in ui separately just mathcing row height of graph
    ]
}