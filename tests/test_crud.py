import pytest
from ninepanels import crud
from ninepanels import exceptions
from ninepanels import utils
from datetime import datetime, timedelta


def test_read_all_users(test_db):
    test_users = crud.read_all_users(test_db)

    assert isinstance(test_users, list)


def test_create_user(test_db):
    # note that db has no email validation, this lives in pydantic models,
    # which check the api route request body
    new = {"name": "Harris", "email": "harris@harris.com", "hashed_password": "hashed"}

    new_user = crud.create_user(test_db, new)
    assert isinstance(new_user.id, int)


def test_read_user_by_id(test_db):
    user_id = 1

    user = crud.read_user_by_id(test_db, user_id)

    assert user.id == 1
    assert user.email == "ben@ben.com"

    # check cexected errors:

    with pytest.raises(exceptions.UserNotFound):
        user_id = 42
        user = crud.read_user_by_id(test_db, user_id)


def test_read_user_by_email(test_db):
    email = "ben@ben.com"

    ben = crud.read_user_by_email(test_db, email)

    assert ben.email == email
    assert ben.id == 1


def test_update_user_by_id(test_db):
    # get user obejct and check name reads 'bennyboy'
    user = crud.read_user_by_id(db=test_db, user_id=1)

    assert user.name == "Bennyboy"

    # udpate  a non-existant column and check for fialure

    with pytest.raises(exceptions.UserNotUpdated):
        crud.update_user_by_id(
            db=test_db, user_id=user.id, update={"col_not_exist": "newname"}
        )

    # update user name and check has changed

    updated_user = crud.update_user_by_id(
        db=test_db, user_id=user.id, update={"name": "newname"}
    )

    assert updated_user.name == "newname"


def test_delete_user_by_id(test_db):
    user_id = 2  # delete christy

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


def test_read_panels_with_current_entry_by_user_id(test_db):
    test_user_id = 1
    panels = crud.read_panels_with_current_entry_by_user_id(test_db, test_user_id)

    # test there is is either one (complete) or 0 (incomplete) entries:
    for panel in panels:
        assert (
            len(panel["entries"]) <= 1
        )  # check max one or none for every panel['entries'] list
        if panel["id"] == 1:
            assert len(panel["entries"]) == 1

    # test that the panels are coming out in asc order of position:
    for i, panel in enumerate(panels):
        assert panel["position"] == i


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
    new_pos = 6
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
    user_email = "ben@ben.com"

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
