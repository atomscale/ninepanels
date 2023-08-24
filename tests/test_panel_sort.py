from ninepanels import panel_sort
import pytest

# mock of sorted panels for user_id
mock_db_output = [
    {"id": 20, "position": 0},
    {"id": 30, "position": 1},
    {"id": 10, "position": 2},
    {"id": 80, "position": 3},
    {"id": 70, "position": 4},
    {"id": 73, "position": 5},
    {"id": 74, "position": 6},
    {"id": 888, "position": 7},
    {"id": 13, "position": 8},
]

mock_incoming_request = {"id":70, "new_pos": 7}

def test_panel_sort():
    pass