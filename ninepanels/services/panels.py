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

            current_entry = crud.read_current_entry_by_panel_id(db=db, panel_id=panel_id)

            if current_entry:
                current_entry_d = utils.instance_to_dict(current_entry)
                panel_d["is_complete"] = current_entry_d["is_complete"]
            else:
                panel_d["is_complete"] = False

            panels_with_latest_entry_only.append(panel_d)

    return panels_with_latest_entry_only