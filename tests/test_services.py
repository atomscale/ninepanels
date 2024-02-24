from datetime import datetime
from datetime import date
from datetime import timedelta
from pprint import PrettyPrinter

from ninepanels.db import crud
from ninepanels.services import services
from ninepanels import pydmodels as pyd
from ninepanels import sqlmodels as sql

pp = PrettyPrinter()

def test_pad_days(test_db):
    """given a freah panel wtih one day entry created
    on a specific hardcoded date
    when the padding is applied,
    the len should be seven with"""

    new_panel = crud.create_panel_by_user_id(
        db=test_db, title="testing panel", user_id=1, position=7
    )

    # a friday, = weekday 4
    now_date = datetime(day=23, month=2, year=2024).date()

    day = pyd.DayCreate(
        panel_date=now_date,
        day_of_week=now_date.weekday(),
        day_date_num=now_date.day,
        last_updated=datetime.utcnow(),
        is_complete=False,
        is_pad=False,
        is_fill=False,
        panel_id=new_panel.id,
    )

    new_day = crud.create_day(db=test_db, new_day=day)

    assert new_day.day_of_week == 4
    assert new_day.day_date_num == 23

    days = crud.read_days_for_panel(db=test_db, panel_id=new_panel.id)

    assert len(days) == 1
    assert isinstance(days, list)
    assert isinstance(days[0], sql.Day)

    # we have established we have a single sql.Day in a list

    padded_days = services.pad_days_to_grid(arr=days, panel_id=new_panel.id)

    assert len(padded_days) == 7
    assert isinstance(padded_days[0], dict)
    assert isinstance(padded_days[2], sql.Day)


def test_fill_missed_days(test_db):
    """given a Day tbale with one entry on a given date,
    and given the current user time multiple days after that one entry
    then the days shoudl be filled iwht non-pad false days with a generated id

    """

    new_panel = crud.create_panel_by_user_id(
        db=test_db, title="testing back fill", user_id=1, position=7
    )

    old_date = datetime(day=29, month=2, year=2024).date()

    day = pyd.DayCreate(
        panel_date=old_date,
        day_of_week=old_date.weekday(),
        day_date_num=old_date.day,
        last_updated=datetime.utcnow(),
        is_complete=False,
        is_pad=False,
        is_fill=False,
        panel_id=new_panel.id,
    )

    old_day = crud.create_day(db=test_db, new_day=day)

    current_user_date = datetime(day=10, month=3, year=2024).date()

    success = services.fill_missed_days(
        db=test_db, current_user_date=current_user_date, panel_id=new_panel.id
    )

    assert success

    days = crud.read_days_for_panel(db=test_db, panel_id=new_panel.id)

    assert days[0].panel_date.date() == current_user_date
    assert days[-1].panel_date.date() == old_date


def test_orchestrate_panel_response(test_db):
    """
    Given a panel effectivley created on a midweek date with one entry,
    Tuesday 20th Feb,
    When no user action unitl Friday 23rd when the next read happens
    then the response be a pyd.Panel model
    should have sat 24 and sun 25th padded
    the 23 back to the 21 filled as false
    the 19th padded


    """
    create_date = datetime(day=20, month=2, year=2024).date()

    new_panel = crud.create_panel_by_user_id(
        db=test_db, title="testing assembple panel", user_id=1, last_updated=create_date, position=7, created_at=create_date
    )


    day = pyd.DayCreate(
        panel_date=create_date,
        day_of_week=create_date.weekday(),
        day_date_num=create_date.day,
        last_updated=datetime.utcnow(),
        is_complete=False,
        is_fill=False,
        is_pad=False,
        panel_id=new_panel.id,
    )

    old_day = crud.create_day(db=test_db, new_day=day)

    current_user_date = datetime(day=23, month=2, year=2024).date()

    panel = services.orchestrate_panel_response(db=test_db, panel_id=new_panel.id, user_id=1, current_user_date=current_user_date)

    # pp.pprint(panel.model_dump())

    assert create_date.weekday() == 1 # is a Tuesday
    assert current_user_date.weekday() == 4 # is a Friday

    assert isinstance(panel, pyd.PanelResponse)
    assert isinstance(panel.graph, pyd.Graph)
    assert isinstance(panel.graph.days, list)
    assert isinstance(panel.graph.days[6], pyd.Day)

    assert panel.graph.days[0].panel_date.day == 25
    assert panel.graph.days[0].day_of_week == 6
    assert panel.graph.days[0].day_date_num == 25

    assert panel.graph.days[0].is_pad == True
    assert panel.graph.days[1].is_pad == True
    assert panel.graph.days[2].is_pad == False
    assert panel.graph.days[2].is_fill == True
    assert panel.graph.days[5].is_pad == False
    assert panel.graph.days[5].is_fill == False

    assert panel.graph.days[6].panel_date.day == 19
    assert panel.graph.days[6].day_of_week == 0
    assert panel.graph.days[6].day_date_num == 19

def test_orchestrate_panel_create(test_db):
    """Given no prior data apart from mocked panel create pyd instance from request data
    when a new panel is created
    then a new panel must be entered to the Panels table
    then a new Day corr to user current time must be created in the Days table

    """

    panel_create = pyd.PanelCreate(
        title="orch create test",
        position=7
    )

    new_panel = services.orchestrate_panel_create(db=test_db, user_id=1, new_panel=panel_create)

    assert new_panel
    assert isinstance(new_panel, pyd.PanelResponse)
    assert isinstance(new_panel, pyd.PanelResponse)
    assert isinstance(new_panel.graph, pyd.Graph)
    assert isinstance(new_panel.graph.days, list)
    assert isinstance(new_panel.graph.days[0], pyd.Day)

    assert new_panel.title == panel_create.title

    # pp.pprint(new_panel.model_dump())

