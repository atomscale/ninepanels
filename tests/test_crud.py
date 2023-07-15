import pytest
from ninepanels import crud
from ninepanels import errors


def test_read_all_users(test_db):
    test_users = crud.read_all_users(test_db)

    assert isinstance(test_users, list)


def test_create_user(test_db):
    # note that db has no email validation, this lives in pydantic models,
    # which check the api route request body
    new = {"name":'Harris', "email": "harris@harris.com", "hashed_password": "hashed"}

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
    user_id = 3 # delete christy

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
    assert len(test_panels) == 7

def test_read_all_panels_by_user_id(test_db):
    test_user_panels = crud.read_all_panels_by_user_id(test_db, user_id=1)

    assert isinstance(test_user_panels, list)
    assert len(test_user_panels) == 3

def test_read_all_entries(test_db):
    test_entries = crud.read_all_entries(test_db)

    assert isinstance(test_entries, list)
    assert len(test_entries) > 2

def test_create_entry_by_panel_id(test_db):
    new_entry = crud.create_entry_by_panel_id(test_db, is_complete=False, panel_id=3, user_id=1)
    assert isinstance(new_entry.id, int)

def test_read_current_entries_by_user_id(test_db):
    test_user_id = 1
    current_panels = crud.read_current_entries_by_user_id(test_db, test_user_id)

    assert len(current_panels) == 3

    for lp in current_panels:
        if lp.panel_id == 1:
            assert lp.is_complete == False


