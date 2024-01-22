import pytest

from pprint import PrettyPrinter

from ninepanels import pydmodels as pyd

pp = PrettyPrinter()


def test_index(test_server):
    resp = test_server.get("/")

    assert resp.status_code == 200

    payload = resp.json()

    assert pyd.WrappedResponse(**payload)


def test_create_user(test_server):
    resp = test_server.post(
        "/users",
        data={
            "email": "ben@ninepanels.com",
            "name": "Testing Ben",
            "password": "password",
        },
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload["data"]["id"], int)


@pytest.fixture
def test_access_token(test_server):
    resp = test_server.post(
        "/token", data={"username": "bwdyer@gmail.com", "password": "newpassword"}
    )

    assert resp.status_code == 200

    payload = resp.json()

    return payload["data"]["access_token"]


def test_read_user_by_id(test_server, test_access_token):
    resp = test_server.get(
        "/users", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert payload["data"]["email"] == "bwdyer@gmail.com"


def test_delete_user_by_id(test_server):
    user_to_delete_token = test_server.post(
        "/token", data={"username": "ben@atomscale.co", "password": "newpassword"}
    )

    resp = test_server.delete(
        "/users",
        headers={
            "Authorization": "Bearer "
            + user_to_delete_token.json()["data"]["access_token"]
        },
    )

    assert resp.status_code == 200
    payload = resp.json()

    assert payload["data"]["success"] == True


def test_post_panel_by_user_id(test_server, test_access_token):
    # test with both title and desc
    resp = test_server.post(
        "/panels",
        data={
            "position": 4,
            "title": "test api panel",
            "description": "this is the api testy testy panel desc",
        },  # form
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200

    # test with just required title
    resp = test_server.post(
        "/panels",
        data={"position": 4, "title": "test api panel"},  # form
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200

    # test with just required title and blank "" desc
    resp = test_server.post(
        "/panels",
        data={"position": 4, "title": "test api panel", "description": ""},  # form
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200


def test_get_panels_by_user_id(test_server, test_access_token):
    resp = test_server.get(
        "/panels", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload["data"], list)


def test_update_panel_by_id(test_server, test_access_token):
    headers = {"Authorization": "Bearer " + test_access_token}

    # create new panel for test:

    resp = test_server.post(
        "/panels",
        data={
            "position": 4,
            "title": "test api panel for udpate",
            "description": "testy desc",
        },
        headers=headers,
    )
    assert resp.status_code == 200

    test_panel = resp.json()
    test_panel_id = test_panel["data"]["id"]

    # test failure:

    # panel id wrong
    resp = test_server.patch(
        "/panels/9876",
        json={"title": "new updated title from api"},
        headers=headers,
    )

    test_panel = resp.json()
    assert test_panel["status_code"] == 400

    # panel json empty
    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        # json={},
        headers=headers,
    )

    test_panel = resp.json()
    assert test_panel["status_code"] == 422  # pydantic will send back 'unprocessable

    # panel update field that not in pydantic PanelUpdate obj caught
    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        json={"not_exist": "new updated title from api"},
        headers=headers,
    )

    test_panel = resp.json()
    assert test_panel["status_code"] == 400  # this is not validated by pydantic

    ### test success ###

    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        json={"title": "the update worked", "description": "test description"},
        headers=headers,
    )

    resp_body = resp.json()

    assert resp_body["data"]["id"] == test_panel_id
    assert resp_body["data"]["title"] == "the update worked"
    assert resp_body["data"]["position"]

    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        json={"position": 1},
        headers=headers,
    )

    resp_body = resp.json()

    assert resp_body["data"]["id"] == test_panel_id
    assert resp_body["data"]["title"] == "the update worked"
    assert resp_body["data"]["position"] == 1


def test_delete_panel_by_id(test_server, test_access_token):
    resp = test_server.delete(
        f"/panels/4",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200

    delete_op = resp.json()
    assert delete_op["data"]["success"] == True


def test_post_entry_on_panel(test_server, test_access_token):
    resp = test_server.post(
        "/panels/5/entries",
        json={"is_complete": True},
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200


def test_get_entries_by_panel_id(test_server, test_access_token):
    panel_id = 1

    all = test_server.get(
        f"/panels/{panel_id}/entries",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    all_data = all.json()["data"]

    assert isinstance(all_data, list)

    print("ALL")
    for e in all_data[:7]:
        print(e["timestamp"], e["is_complete"])
    print()

    seven = test_server.get(
        f"/panels/{panel_id}/entries?limit=7",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    seven_data = seven.json()["data"]

    assert isinstance(seven_data, list)

    print("seven")
    for e in seven_data:
        print(e["timestamp"], e["is_complete"])
    print()

    fourteen = test_server.get(
        f"/panels/{panel_id}/entries?limit=14",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    fourteen_data = fourteen.json()["data"]

    assert isinstance(fourteen_data, list)

    print("fourteen")
    for e in fourteen_data:
        print(e["timestamp"], e["is_complete"])
    print()


def test_initial_password_reset_flow(test_server):
    """route must handle unauth users"""

    resp = test_server.post(
        "/request_password_reset", data={"email": "bwdyer@gmail.com"}
    )

    assert resp.status_code == 200

    resp = resp.json()
    assert resp
