import pytest
import logging
from ninepanels import crud

def test_read_all_users(test_db):
    test_users = crud.read_all_users(test_db)

    assert isinstance(test_users, list)
    assert len(test_users) == 3

    for user in test_users:
        logging.info(user.name)

def test_read_all_panels(test_db):
    test_panels = crud.read_all_panels(test_db)

    assert isinstance(test_panels, list)
    assert len(test_panels) == 7

    for panel in test_panels:
        logging.info(panel.title)

def test_read_all_entries(test_db):
    test_entries = crud.read_all_entries(test_db)

    assert isinstance(test_entries, list)
    # assert len(test_entries) == 7

    for entry in test_entries:
        logging.info(f"{entry.is_complete}, {entry.panel.title}, {entry.panel.owner.name}")


def test_read_latest_panel_for_user(test_db):
    test_user_id = 1
    latest_panels = crud.read_latest_panel_status_for_user(test_db, test_user_id)

    assert len(latest_panels) == 3

    for lp in latest_panels:
        if lp.panel_id == 1:
            assert lp.is_complete == False
            