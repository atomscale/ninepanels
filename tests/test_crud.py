import pytest
from ninepanels import crud
from ninepanels import errors


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

    with pytest.raises(errors.UserNotFound):
        user_id = 42
        user = crud.read_user_by_id(test_db, user_id)


def test_delete_user_by_id(test_db):
    user_id = 2  # delete christy

    conf = crud.delete_user_by_id(test_db, user_id)

    assert conf == True

    # check user no longer in db
    with pytest.raises(errors.UserNotFound):
        crud.read_user_by_id(test_db, user_id)

    # check correct error raised when try to delete again
    with pytest.raises(errors.UserNotDeleted):
        conf = crud.delete_user_by_id(test_db, user_id)


def test_read_user_by_email(test_db):
    email = "ben@ben.com"

    ben = crud.read_user_by_email(test_db, email)

    assert ben.email == email
    assert ben.id == 1


def test_read_all_panels(test_db):
    test_panels = crud.read_all_panels(test_db)

    assert isinstance(test_panels, list)


def test_read_all_entries(test_db):
    test_entries = crud.read_all_entries(test_db)

    assert isinstance(test_entries, list)
    assert len(test_entries) > 2


def test_create_entry_by_panel_id(test_db):
    new_entry = crud.create_entry_by_panel_id(
        test_db, is_complete=False, panel_id=3, user_id=1
    )
    assert isinstance(new_entry.id, int)


def test_read_panels_with_current_entry_by_user_id(test_db):
    test_user_id = 1
    current_panels = crud.read_panels_with_current_entry_by_user_id(
        test_db, test_user_id
    )

    for panel in current_panels:
        assert (
            len(panel["entries"]) <= 1
        )  # check max one or none for every panel['entries'] list
        if panel["id"] == 1:
            # for this test case we know we want the roginal True from two days ago
            # to be flipped to None
            assert len(panel["entries"]) == 1


@pytest.fixture
def test_create_panel_by_user_id(test_db):
    test_user_id = 1
    test_panel_title = "testing panel"
    test_description = "this is a nice test descritpooooon"

    new_panel = crud.create_panel_by_user_id(test_db, test_user_id, test_panel_title, test_description)

    assert isinstance(new_panel.id, int)

    return new_panel.id


def test_update_panel_by_panel_id(test_db):
    # create a new panel for this test:
    new_panel = crud.create_panel_by_user_id(test_db, 1, "test panel for update", "test_desc")

    # test failure cases:

    # test non-existent panel_id
    with pytest.raises(errors.PanelNotUpdated):
        crud.update_panel_by_id(
            db=test_db, panel_id=9999, update={"title": "won't work?"}
        )

    # test empty update obj
    with pytest.raises(errors.PanelNotUpdated):
        crud.update_panel_by_id(db=test_db, panel_id=9999, update={})

    # test update obj with keys that dont exist on object
    with pytest.raises(errors.PanelNotUpdated) as e:
        crud.update_panel_by_id(test_db, new_panel.id, {"not_there": "update value"})
        assert "no field" in str(e)

    # test success:

    # update new panel and check title changes
    update_d = {"title": "updated test panel", "description": "updated description"}

    updated_panel = crud.update_panel_by_id(test_db, new_panel.id, update_d)

    assert updated_panel.id == new_panel.id
    assert updated_panel.title == "updated test panel"
    assert updated_panel.description == "updated description"

    # update new panel without desc and check title changes
    update_d = {"title": "updated test panel no desc"}

    updated_panel = crud.update_panel_by_id(test_db, new_panel.id, update_d)

    assert updated_panel.id == new_panel.id
    assert updated_panel.title == "updated test panel no desc"


def test_delete_panel_by_panel_id(test_db, test_create_panel_by_user_id):
    test_user_id = 1
    is_deleted = crud.delete_panel_by_panel_id(
        test_db, test_user_id, test_create_panel_by_user_id
    )

    assert is_deleted

    # try again, shoudl be idempotent
    with pytest.raises(errors.PanelNotDeleted):
        is_deleted = crud.delete_panel_by_panel_id(
            test_db, test_user_id, test_create_panel_by_user_id
        )
