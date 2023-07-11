def test_index(test_server):
    resp = test_server.get("/")

    assert resp.status_code == 200

    payload = resp.json()

    assert "yo" in payload.keys()

def test_get_panels_by_user_id(test_server):
    resp = test_server.get("/panels")

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload, list)

    print(payload)
    print()

def test_post_entry_on_panel(test_server):
    resp = test_server.post("/entries", json={"panel_id": 2, "is_complete": True, "user_id": 1})

    assert resp.status_code == 200

def test_get_current_entries_by_user_id(test_server):
    resp = test_server.get("/entries")

    assert resp.status_code == 200

    payload = resp.json()

    assert isinstance(payload, list)

    print(payload)
