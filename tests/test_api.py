import pytest


def test_index(test_server):
    resp = test_server.get("/")

    assert resp.status_code == 200

    payload = resp.json()

    assert "success" in payload.keys()


def test_create_user(test_server):
    resp = test_server.post(
        "/users",
        json={
            "email": "new@new.com",
            "name": "NewPerson",
            "plain_password": "password",
        },
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload["id"], int)


@pytest.fixture
def test_access_token(test_server):
    resp = test_server.post(
        "/token", data={"username": "ben@ben.com", "password": "password"}
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
    print(payload)
    assert payload['email'] == "ben@ben.com"


def test_delete_user_by_id(test_server):
    user_to_delete_token = test_server.post(
        "/token", data={"username": "hobo@hobo.com", "password": "password"}
    )

    resp = test_server.delete(
        "/users", headers={"Authorization": "Bearer " + user_to_delete_token.json()['access_token']}
    )

    assert resp.status_code == 200
    payload = resp.json()

    assert payload['success'] == True

def test_get_panels_by_user_id(test_server, test_access_token):
    resp = test_server.get(
        "/panels", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload, list)




def test_post_entry_on_panel(test_server, test_access_token):
    resp = test_server.post(
        "/entries",
        json={"panel_id": 2, "is_complete": True},
        headers={"Authorization": "Bearer " + test_access_token},
    )

    assert resp.status_code == 200


def test_get_current_entries_by_user_id(test_server, test_access_token):
    resp = test_server.get(
        "/entries", headers={"Authorization": "Bearer " + test_access_token}
    )

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload, list)

