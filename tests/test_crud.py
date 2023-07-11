import pytest
import logging
from ninepanels import crud


def test_read_all_users(test_db):
    test_users = crud.read_all_users(test_db)

    assert isinstance(test_users, list)
    assert len(test_users) == 3

def test_create_user(test_db):
    new_user = crud.create_user(test_db, {"name": "Harris"})

    assert isinstance(new_user.id, int)

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
        print(lp.timestamp, lp.panel.title)
        if lp.panel_id == 1:
            assert lp.is_complete == False


