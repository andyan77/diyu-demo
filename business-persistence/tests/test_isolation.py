from tests.conftest import create_account, create_task, create_user, create_workspace


def test_task_not_visible_from_other_workspace(client, unique):
    user = create_user(client, unique)
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    task = create_task(client, ws_a["id"], unique)

    r = client.get(f"/workspaces/{ws_b['id']}/tasks/{task['id']}/projection")
    assert r.status_code == 404


def test_user_workspace_listing_only_shows_own_memberships(client, unique):
    user_1 = create_user(client, unique + "-1")
    user_2 = create_user(client, unique + "-2")
    ws_1 = create_workspace(client, unique + "-1", user_1["id"])
    ws_2 = create_workspace(client, unique + "-2", user_2["id"])

    r = client.get(f"/users/{user_1['id']}/workspaces")
    assert r.status_code == 200
    ids = {w["id"] for w in r.json()}
    assert ws_1["id"] in ids
    assert ws_2["id"] not in ids


def test_nonexistent_workspace_is_404_not_500(client, unique):
    import uuid

    r = client.get(f"/workspaces/{uuid.uuid4()}/tasks/{uuid.uuid4()}/projection")
    assert r.status_code == 404


def test_account_not_visible_from_other_workspace(client, unique):
    user = create_user(client, unique)
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    create_account(client, ws_a["id"], unique)

    r = client.get(f"/workspaces/{ws_b['id']}/accounts")
    assert r.status_code == 200
    assert r.json() == []
