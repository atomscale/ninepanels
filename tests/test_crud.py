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

def test_read_all_entries(test_db):
    test_entries = crud.read_all_entries(test_db)

    assert isinstance(test_entries, list)
    assert len(test_entries) == 5 # conftest 4 + 1 test post

def test_create_entry(test_db):
    new_entry = crud.create_entry(test_db, is_complete=False, panel_id=3)
    assert isinstance(new_entry.id, int)

def test_read_latest_entries_for_user(test_db):
    test_user_id = 1
    latest_panels = crud.read_latest_entries_for_user(test_db, test_user_id)

    assert len(latest_panels) == 3

    for lp in latest_panels:
        print(lp.timestamp, lp.panel.title)
        if lp.panel_id == 1:
            assert lp.is_complete == False


