def test_index(test_server):
    resp = test_server.get("/")

    assert resp.status_code == 200

    payload = resp.json()

    assert "yo" in payload.keys()

def test_post_entry(test_server):
    resp = test_server.post("/entries", json={"panel_id": 2, "is_complete": True})

    assert resp.status_code == 200

def test_get_all_entries(test_server):
    resp = test_server.get("/entries")

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload, list)
    assert len(payload) == 5 # conftest 4 + 1 test post

