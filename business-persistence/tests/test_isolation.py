import uuid

from tests.conftest import actor_headers, create_account, create_task, create_user, create_workspace


def test_task_not_visible_from_other_workspace(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    task = create_task(client, ws_a["id"], unique, actor_ref)

    r = client.get(
        f"/workspaces/{ws_b['id']}/tasks/{task['id']}/projection", headers=actor_headers(actor_ref)
    )
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
    r = client.get(f"/workspaces/{uuid.uuid4()}/tasks/{uuid.uuid4()}/projection")
    assert r.status_code == 404


def test_account_not_visible_from_other_workspace(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    create_account(client, ws_a["id"], unique, actor_ref)

    r = client.get(f"/workspaces/{ws_b['id']}/accounts", headers=actor_headers(actor_ref))
    assert r.status_code == 200
    assert r.json() == []


def test_missing_actor_header_is_401(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.get(f"/workspaces/{ws_id}/accounts")
    assert r.status_code == 401


def test_unknown_actor_is_401(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.get(f"/workspaces/{ws_id}/accounts", headers=actor_headers("no-such-actor"))
    assert r.status_code == 401


def test_non_member_cannot_read_or_write_another_workspace(client, unique):
    """A real, authenticated user who simply isn't a member of this
    workspace -- as opposed to an unknown actor or a missing header -- must
    still be rejected. Checking that workspace_id merely exists is not
    isolation: an outsider who has ever seen this workspace's UUID
    (returned in every API response) must not be able to read or write it.
    """

    owner = create_user(client, unique + "-owner")
    outsider = create_user(client, unique + "-outsider")
    ws = create_workspace(client, unique, owner["id"])

    r_read = client.get(
        f"/workspaces/{ws['id']}/accounts", headers=actor_headers(outsider["external_ref"])
    )
    assert r_read.status_code == 403

    r_write = client.post(
        f"/workspaces/{ws['id']}/accounts",
        json={"platform": "test-platform", "handle": f"handle-{unique}"},
        headers=actor_headers(outsider["external_ref"]),
    )
    assert r_write.status_code == 403


def test_non_member_cannot_write_a_task_into_this_workspace(client, unique):
    owner = create_user(client, unique + "-owner")
    outsider = create_user(client, unique + "-outsider")
    ws = create_workspace(client, unique, owner["id"])

    r = client.post(
        f"/workspaces/{ws['id']}/tasks",
        json={"idempotency_key": f"task-{unique}", "kind": "test"},
        headers=actor_headers(outsider["external_ref"]),
    )
    assert r.status_code == 403
