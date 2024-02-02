import pytest

from pprint import PrettyPrinter

from ninepanels import pydmodels as pyd

pp = PrettyPrinter()

base_url = "/v5"

def test_index(test_server):
    resp = test_server.get("/")

    assert resp.status_code == 200

    payload = resp.json()

    assert pyd.WrappedResponse(**payload)


def test_create_user(test_server):
    resp = test_server.post(base_url +
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
    resp = test_server.get(base_url +
        "/users", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert payload["data"]["email"] == "bwdyer@gmail.com"


def test_read_all_users(test_server, test_access_token):
    """Given an admin user, request for all users should not fail"""
    resp = test_server.get(base_url +
        "/admin/users", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    users = resp.json()["data"]

    assert isinstance(users, list)
    assert len(users) == 2


def test_read_all_users_auth_fail(test_server):
    """once given a token for an non-admin user that exists in db,
    when a call to an admin only route is made,
    the reposnse code should be 401"""

    resp = test_server.post(
        "/token", data={"username": "ben@atomscale.co", "password": "newpassword"}
    )

    assert resp.status_code == 200

    non_admin_token = resp.json()["data"]["access_token"]

    non_auth_call = test_server.get(base_url +
        "/admin/users", headers={"Authorization": "Bearer " + non_admin_token}
    )

    assert non_auth_call.status_code == 401


def test_delete_user_by_id(test_server):
    user_to_delete_token = test_server.post(
        "/token", data={"username": "ben@atomscale.co", "password": "newpassword"}
    )

    resp = test_server.delete(base_url +
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
    resp = test_server.post(base_url +
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
    resp = test_server.post(base_url +
        "/panels",
        data={"position": 4, "title": "test api panel"},  # form
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200

    # test with just required title and blank "" desc
    resp = test_server.post(base_url +
        "/panels",
        data={"position": 4, "title": "test api panel", "description": ""},  # form
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200


def test_get_panels_by_user_id(test_server, test_access_token):
    resp = test_server.get(base_url +
        "/panels", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload["data"], list)


def test_update_panel_by_id(test_server, test_access_token):
    headers = {"Authorization": "Bearer " + test_access_token}

    # create new panel for test:

    resp = test_server.post(base_url +
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
    resp = test_server.patch(base_url +
        "/panels/9876",
        json={"title": "new updated title from api"},
        headers=headers,
    )

    test_panel = resp.json()
    assert test_panel["status_code"] == 400

    # panel json empty
    resp = test_server.patch(base_url +
        f"/panels/{test_panel_id}",
        # json={},
        headers=headers,
    )

    test_panel = resp.json()
    assert test_panel["status_code"] == 422  # pydantic will send back 'unprocessable

    # panel update field that not in pydantic PanelUpdate obj caught
    resp = test_server.patch(base_url +
        f"/panels/{test_panel_id}",
        json={"not_exist": "new updated title from api"},
        headers=headers,
    )

    test_panel = resp.json()
    assert test_panel["status_code"] == 400  # this is not validated by pydantic

    ### test success ###

    resp = test_server.patch(base_url +
        f"/panels/{test_panel_id}",
        json={"title": "the update worked", "description": "test description"},
        headers=headers,
    )

    resp_body = resp.json()

    assert resp_body["data"]["id"] == test_panel_id
    assert resp_body["data"]["title"] == "the update worked"
    assert resp_body["data"]["position"]

    resp = test_server.patch(base_url +
        f"/panels/{test_panel_id}",
        json={"position": 1},
        headers=headers,
    )

    resp_body = resp.json()

    assert resp_body["data"]["id"] == test_panel_id
    assert resp_body["data"]["title"] == "the update worked"
    assert resp_body["data"]["position"] == 1


def test_delete_panel_by_id(test_server, test_access_token):
    resp = test_server.delete(base_url +
        f"/panels/4",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200

    delete_op = resp.json()
    assert delete_op["data"]["success"] == True


def test_post_entry_on_panel(test_server, test_access_token):
    resp = test_server.post(base_url +
        "/panels/5/entries",
        json={"is_complete": True},
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200


def test_get_entries_by_panel_id(test_server, test_access_token):
    panel_id = 1

    all = test_server.get(base_url +
        f"/panels/{panel_id}/entries",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    all_data = all.json()["data"]

    assert isinstance(all_data, list)

    print("ALL")
    for e in all_data[:7]:
        print(e["timestamp"], e["is_complete"])
    print()

    seven = test_server.get(base_url +
        f"/panels/{panel_id}/entries?limit=7",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    seven_data = seven.json()["data"]

    assert isinstance(seven_data, list)

    print("seven")
    for e in seven_data:
        print(e["timestamp"], e["is_complete"])
    print()

    fourteen = test_server.get(base_url +
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

    resp = test_server.post(base_url +
        "/auth/request_password_reset", data={"email": "bwdyer@gmail.com"}
    )

    assert resp.status_code == 200

    resp = resp.json()
    assert resp


# WIP test auth on get all users for the admin and non admin users

# test users api route
