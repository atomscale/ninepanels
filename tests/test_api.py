import pytest
from fastapi import HTTPException


def test_index(test_server):
    resp = test_server.get("/")

    assert resp.status_code == 200

    payload = resp.json()

    assert "branch" in payload.keys()


def test_create_user(test_server):
    resp = test_server.post(
        "/users",
        data={
            "email": "new@new.com",
            "name": "NewPerson",
            "password": "password",
        },
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload["id"], int)


@pytest.fixture
def test_access_token(test_server):
    resp = test_server.post(
        "/token", data={"username": "chris@chris.com", "password": "password"}
    )

    assert resp.status_code == 200

    payload = resp.json()

    return payload["access_token"]


def test_read_user_by_id(test_server, test_access_token):
    resp = test_server.get(
        "/users", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert payload["email"] == "chris@chris.com"


def test_delete_user_by_id(test_server):
    user_to_delete_token = test_server.post(
        "/token", data={"username": "hobo@hobo.com", "password": "password"}
    )

    resp = test_server.delete(
        "/users",
        headers={
            "Authorization": "Bearer " + user_to_delete_token.json()["access_token"]
        },
    )

    assert resp.status_code == 200
    payload = resp.json()

    assert payload["success"] == True


def test_post_panel_by_user_id(test_server, test_access_token):

    # test with both title and desc
    resp = test_server.post(
        "/panels",
        data={"position": 4, "title": "test api panel", "description": "this is the api testy testy panel desc"},  # form
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

    assert isinstance(payload, list)


def test_update_panel_by_id(test_server, test_access_token):
    headers = {"Authorization": "Bearer " + test_access_token}

    # create new panel for test:

    resp = test_server.post(
        "/panels", data={"position": 4, "title": "test api panel for udpate", "description": "testy desc"}, headers=headers
    )
    assert resp.status_code == 200

    test_panel_id = resp.json()['id']
    # test failure:

    # panel id wrong
    resp = test_server.patch(
        "/panels/9876",
        json={"title": "new updated title from api"},
        headers=headers,
    )

    assert resp.status_code == 422
    assert "Panel not updated" in resp.text

    # panel json empty
    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        # json={},
        headers=headers,
    )

    assert resp.status_code == 422 # pydantic will send back 'unprocessable
    assert "detail" in resp.json() # just check pydantic respd with detail


    # panel update field that not in pydantic PanelUpdate obj caught
    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        json={"not_exist": "new updated title from api"},
        headers=headers,
    )

    assert resp.status_code == 422 # this is not validated by pydantic
    assert "detail" in resp.json()

    ### test success ###

    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        json={"title": "the update worked", "description": "test description"},
        headers=headers,
    )

    resp_body = resp.json()

    assert resp_body['id'] == test_panel_id
    assert resp_body['title'] == "the update worked"
    assert resp_body['position']

    resp = test_server.patch(
        f"/panels/{test_panel_id}",
        json={"position": 1},
        headers=headers,
    )

    resp_body = resp.json()

    assert resp_body['id'] == test_panel_id
    assert resp_body['title'] == "the update worked"
    assert resp_body['position'] == 1


def test_delete_panel_by_id(test_server, test_access_token):
    resp = test_server.delete(
        f"/panels/4",
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200


def test_post_entry_on_panel(test_server, test_access_token):
    resp = test_server.post(
        "/entries",
        json={"panel_id": 5, "is_complete": True},
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200
