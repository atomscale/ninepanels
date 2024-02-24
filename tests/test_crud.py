import pytest
from ninepanels.db import crud
from ninepanels import exceptions
from ninepanels import utils
from ninepanels import pydmodels as pyd
from ninepanels import sqlmodels as sql
from datetime import datetime, timedelta
from pprint import PrettyPrinter

pp = PrettyPrinter()


def test_create_user(test_db):
    # note that db has no email validation, this lives in pydantic models,
    # which check the api route request body
    new = {"name": "Harris", "email": "harris@harris.com", "hashed_password": "hashed"}

    new_user = crud.create_user(test_db, new)
    assert isinstance(new_user.id, int)
    assert isinstance(new_user.name, str)
    assert new_user.name == "Harris"

    # tested expected errors:

    bad_params = {
        "nam": "Harris",
        "email": "harris@harris.com",
        "hashed_password": "hashed",
    }

    with pytest.raises(exceptions.UserNotCreated):
        new_user = crud.create_user(test_db, bad_params)

    test_users = crud.read_all_users(test_db)

    assert len(test_users) == 3
    assert test_users[-1].id == 3


def test_read_all_users(test_db):
    test_users = crud.read_all_users(test_db)

    assert isinstance(test_users, list)
    assert len(test_users) == 2


def test_read_user_by_id(test_db):
    user_id = 1

    user = crud.read_user_by_id(test_db, user_id)

    assert user.id == 1
    assert user.email == "bwdyer@gmail.com"

    # check errors:

    with pytest.raises(exceptions.UserNotFound):
        user_id = 42
        user = crud.read_user_by_id(test_db, user_id)


def test_read_user_by_email(test_db):
    email = "bwdyer@gmail.com"

    user = crud.read_user_by_email(test_db, email)

    assert user.email == email
    assert user.id == 1

    # check errors:

    with pytest.raises(exceptions.UserNotFound):
        user = crud.read_user_by_email(test_db, "nouser@testing.com")


def test_update_user_by_id(test_db):
    user = crud.read_user_by_id(db=test_db, user_id=1)

    # udpate  a non-existant column and check for failure

    with pytest.raises(exceptions.UserNotUpdated):
        crud.update_user_by_id(
            db=test_db, user_id=user.id, update={"col_not_exist": "newname"}
        )

    # update a DateTime column with wrong type
    with pytest.raises(exceptions.UserNotUpdated):
        crud.update_user_by_id(
            db=test_db, user_id=user.id, update={"last_login": "not a date"}
        )

    # update user name and check has changed

    updated_user = crud.update_user_by_id(
        db=test_db, user_id=user.id, update={"name": "newname"}
    )

    assert updated_user.name == "newname"

    # update last_login and check has changed

    ts = datetime.utcnow()
    updated_user = crud.update_user_by_id(
        db=test_db, user_id=user.id, update={"last_login": ts}
    )

    assert updated_user.last_login == ts


def test_delete_user_by_id(test_db):
    user_id = 2  # delete ben@atomscale.co

    conf = crud.delete_user_by_id(test_db, user_id)

    assert conf == True

    # check user no longer in db
    with pytest.raises(exceptions.UserNotFound):
        crud.read_user_by_id(test_db, user_id)

    # check correct error raised when try to delete again
    with pytest.raises(exceptions.UserNotDeleted):
        conf = crud.delete_user_by_id(test_db, user_id)


def test_create_entry_by_panel_id(test_db):
    new_entry = crud.create_entry_by_panel_id(
        test_db, is_complete=False, panel_id=3, user_id=1
    )
    assert isinstance(new_entry.id, int)

    # test fails on user_id not existing
    with pytest.raises(exceptions.PanelNotCreated):
        bad_entry = crud.create_entry_by_panel_id(
            test_db, is_complete=False, panel_id=3333, user_id=1
        )


@pytest.mark.skip
def test_read_panels_with_current_entry_by_user_id(test_db):
    test_user_id = 1
    panels = crud.read_panels_with_current_entry_by_user_id(test_db, test_user_id)

    for i, panel in enumerate(panels):
        # test that the panels are coming out in asc order of position:
        assert panel["position"] == i
        # check is bool
        assert isinstance(panel["is_complete"], bool)


def test_create_panel_by_user_id(test_db):
    test_user_id = 1
    test_panel_title = "four"
    test_description = "this is a nice test descritpooooon"

    new_panel = crud.create_panel_by_user_id(
        db=test_db,
        position=3,
        user_id=test_user_id,
        title=test_panel_title,
        description=test_description,
    )

    assert isinstance(new_panel.id, int)
    assert new_panel.position == 3


def test_update_panel_by_panel_id(test_db):
    test_user_id = 1
    # create a new panel for this test:
    new_panel = crud.create_panel_by_user_id(
        db=test_db,
        user_id=test_user_id,
        position=4,
        title="test panel for update",
        description="test_desc",
    )

    # test failure cases:

    # test non-existent panel_id
    with pytest.raises(exceptions.PanelNotUpdated):
        crud.update_panel_by_id(
            db=test_db,
            user_id=test_user_id,
            panel_id=9999,
            update={"title": "won't work?"},
        )

    # test empty update obj
    with pytest.raises(exceptions.PanelNotUpdated):
        crud.update_panel_by_id(
            db=test_db, user_id=test_user_id, panel_id=9999, update={}
        )

    # test update obj with keys that dont exist on object
    with pytest.raises(exceptions.PanelNotUpdated) as e:
        crud.update_panel_by_id(
            db=test_db,
            user_id=test_user_id,
            panel_id=new_panel.id,
            update={"not_there": "update value"},
        )
        assert "no field" in str(e)

    # test success:

    # update new panel and check title changes
    update_d = {"title": "updated test panel", "description": "updated description"}

    updated_panel = crud.update_panel_by_id(
        db=test_db, user_id=test_user_id, panel_id=new_panel.id, update=update_d
    )

    assert updated_panel.id == new_panel.id
    assert updated_panel.title == "updated test panel"
    assert updated_panel.description == "updated description"

    # update new panel without desc and check title changes
    update_d = {"title": "THE MOVING ONE"}

    updated_panel = crud.update_panel_by_id(
        db=test_db, user_id=test_user_id, panel_id=new_panel.id, update=update_d
    )

    assert updated_panel.id == new_panel.id
    assert updated_panel.title == "THE MOVING ONE"

    # update position
    new_pos = 0
    update_d = {"position": new_pos}

    updated_panel = crud.update_panel_by_id(
        db=test_db, user_id=test_user_id, panel_id=new_panel.id, update=update_d
    )

    assert updated_panel.id == new_panel.id
    assert updated_panel.position == new_pos

    # update position
    new_pos = 3
    update_d = {"position": new_pos}

    updated_panel = crud.update_panel_by_id(
        db=test_db, user_id=test_user_id, panel_id=new_panel.id, update=update_d
    )

    assert updated_panel.id == new_panel.id
    assert updated_panel.position == new_pos

    # check failure using out of rnage index pf panels
    new_pos = 69
    update_d = {"position": new_pos}

    with pytest.raises(exceptions.PanelNotUpdated):
        updated_panel = crud.update_panel_by_id(
            db=test_db, user_id=test_user_id, panel_id=new_panel.id, update=update_d
        )

    # check failure using same
    new_pos = 3
    update_d = {"position": new_pos}

    with pytest.raises(exceptions.PanelNotUpdated):
        updated_panel = crud.update_panel_by_id(
            db=test_db, user_id=test_user_id, panel_id=new_panel.id, update=update_d
        )


def test_delete_panel_by_panel_id(test_db):
    test_user_id = 1
    is_deleted = crud.delete_panel_by_panel_id(
        db=test_db, user_id=test_user_id, panel_id=2
    )

    assert is_deleted

    # try again, shoudl be idempotent
    with pytest.raises(exceptions.PanelNotDeleted):
        is_deleted = crud.delete_panel_by_panel_id(
            db=test_db, user_id=test_user_id, panel_id=2
        )


def test_access_token_blacklist(test_db):
    # insert a token

    test_token_to_blacklist = utils.generate_random_hash()

    conf = crud.blacklist_an_access_token(
        db=test_db, access_token=test_token_to_blacklist
    )

    assert conf.access_token == test_token_to_blacklist

    # check if the token is in the blacklist table

    blacklisted_check = crud.access_token_is_blacklisted(
        db=test_db, access_token=test_token_to_blacklist
    )

    assert blacklisted_check == True

    # check a non balcklisted token returns false

    non_blacklisted_token = utils.generate_random_hash()

    non_blacklisted_check = crud.access_token_is_blacklisted(
        db=test_db, access_token=non_blacklisted_token
    )

    assert non_blacklisted_check == False


def test_create_password_reset_token(test_db):
    # check a sql object is returned successfully
    user_id = 1
    user_email = "bwdyer@gmail.com"

    test_prt, token_hash = crud.create_password_reset_token(
        db=test_db, email=user_email
    )

    assert test_prt.id
    assert test_prt.id == user_id

    # check the created prt is valid

    test_prt_is_valid = crud.check_password_reset_token_is_valid(
        db=test_db, password_reset_token=token_hash, user_id=user_id
    )

    assert test_prt_is_valid

    # invalidate the prt

    invalid_prt = crud.invalidate_password_reset_token(
        db=test_db, password_reset_token=token_hash, user_id=user_id
    )

    # check prt is now invalid
    assert invalid_prt.user_id == 1
    assert invalid_prt.password_reset_token == token_hash
    assert invalid_prt.is_valid == False
    assert isinstance(invalid_prt.invalidated_at, datetime)

    # create past prt to test expiry and check invalid
    past_time = datetime.utcnow() + timedelta(hours=-1)

    test_prt, toekn_hash = crud.create_password_reset_token(
        db=test_db, email=user_email, ts=past_time
    )

    assert test_prt.id
    assert test_prt.id == user_id

    # check the created prt is invalid due to exprity

    test_prt_is_valid = crud.check_password_reset_token_is_valid(
        db=test_db, password_reset_token=token_hash, user_id=user_id
    )

    assert not test_prt_is_valid


def test_entry_padding(test_db):
    from pydantic import BaseModel

    class MockEntry(BaseModel):
        id: int
        timestamp: datetime
        is_complete: bool
        panel_id: int

    test_unpadded_entries = [
        MockEntry(
            id=1,
            panel_id=1,
            timestamp=datetime.utcnow() + timedelta(days=-6),
            is_complete=True,
        ),
        MockEntry(
            id=2,
            panel_id=1,
            timestamp=datetime.utcnow() + timedelta(days=-5),
            is_complete=True,
        ),
        MockEntry(
            id=3,
            panel_id=1,
            timestamp=datetime.utcnow() + timedelta(days=-3) + timedelta(hours=1),
            is_complete=True,
        ),
        MockEntry(
            id=4,
            panel_id=1,
            timestamp=datetime.utcnow() + timedelta(days=-3) + timedelta(hours=2),
            is_complete=False,
        ),
        MockEntry(
            id=5,
            panel_id=1,
            timestamp=datetime.utcnow() + timedelta(days=-1),
            is_complete=True,
        ),
    ]



    test_created_at = datetime.utcnow() + timedelta(days=-10)

    limit = None

    padded = crud.pad_entries(
        db=test_db,
        unpadded_entries=test_unpadded_entries,
        limit=limit,
        panel_id=1,
        test_created_at=test_created_at.date(),
    )

    assert isinstance(padded, list)


def test_create_day(test_db):
    """Given a new panel in db  and related Days table with no Day rows
    when a Day is created
    then a sql.Day isntance with id is returned
    """
    new_panel = crud.create_panel_by_user_id(
        db=test_db, title="testing panel", user_id=1
    )

    # TODO evntuall this will be 1 day as upon create need to creat the first day
    check = crud.read_days_for_panel(db=test_db, panel_id=new_panel.id)

    assert isinstance(check, list)
    assert len(check) == 0

    now_date = datetime.utcnow().date()

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

    new_day = crud.create_day(db=test_db, day=day)

    assert new_day.id == 1


def test_read_days_for_panel(test_db): ...


def test_pad_days(test_db):
    """given a freah panel wtih one day entry created
    on a specific hardcoded date
    when the padding is applied,
    the len should be seven with"""

    new_panel = crud.create_panel_by_user_id(
        db=test_db, title="testing panel", user_id=1
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

    new_day = crud.create_day(db=test_db, day=day)

    assert new_day.day_of_week == 4
    assert new_day.day_date_num == 23

    days = crud.read_days_for_panel(db=test_db, panel_id=new_panel.id)

    assert len(days) == 1
    assert isinstance(days, list)
    assert isinstance(days[0], sql.Day)

    # we have established we have a single sql.Day in a list

    padded_days = crud.pad_days_to_grid(arr=days, panel_id=new_panel.id)

    assert len(padded_days) == 7
    assert isinstance(padded_days[0], dict)
    assert isinstance(padded_days[2], sql.Day)


def test_fill_missed_days(test_db):
    """given a Day tbale with one entry on a given date,
    and given the current user time multiple days after that one entry
    then the days shoudl be filled iwht non-pad false days with a generated id

    """

    new_panel = crud.create_panel_by_user_id(
        db=test_db, title="testing back fill", user_id=1
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

    old_day = crud.create_day(db=test_db, day=day)

    current_user_date = datetime(day=10, month=3, year=2024).date()

    success = crud.fill_missed_days(
        db=test_db, current_user_date=current_user_date, panel_id=new_panel.id
    )

    assert success

    days = crud.read_days_for_panel(db=test_db, panel_id=new_panel.id)

    assert days[0].panel_date.date() == current_user_date
    assert days[-1].panel_date.date() == old_date


def test_assemble_panel_response(test_db):
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
        db=test_db, title="testing assembple panel", user_id=1, last_updated=create_date
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

    old_day = crud.create_day(db=test_db, day=day)

    current_user_date = datetime(day=23, month=2, year=2024).date()

    panel = crud.assemble_panel_response(db=test_db, panel_id=new_panel.id, user_id=1, current_user_date=current_user_date)

    pp.pprint(panel.model_dump())

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
