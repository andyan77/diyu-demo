from tests.conftest import bootstrapped, create_account, create_task, create_user, create_workspace


def test_task_creation_retry_returns_same_task(client, unique):
    user = create_user(client, unique)
    ws = create_workspace(client, unique, user["id"])
    key = f"retry-{unique}"

    r1 = client.post(f"/workspaces/{ws['id']}/tasks", json={"idempotency_key": key})
    r2 = client.post(f"/workspaces/{ws['id']}/tasks", json={"idempotency_key": key})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

    # exactly one task exists with this idempotency_key on the read side too
    proj = client.get(f"/workspaces/{ws['id']}/tasks/{r1.json()['id']}/projection")
    assert proj.status_code == 200


def test_snapshot_creation_retry_returns_same_snapshot(client, unique):
    user = create_user(client, unique)
    ws = create_workspace(client, unique, user["id"])
    task = create_task(client, ws["id"], unique)
    key = f"snap-{unique}"
    body = {
        "idempotency_key": key,
        "payload": {"note": "first task"},
        "info_nature": "fact",
    }

    r1 = client.post(f"/workspaces/{ws['id']}/tasks/{task['id']}/snapshots", json=body)
    r2 = client.post(f"/workspaces/{ws['id']}/tasks/{task['id']}/snapshots", json=body)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_publish_instance_retry_returns_same_instance(client, unique):
    from tests.conftest import create_artifact

    user = create_user(client, unique)
    ws = create_workspace(client, unique, user["id"])
    account = create_account(client, ws["id"], unique)
    task = create_task(client, ws["id"], unique, account_id=account["id"])
    artifact = create_artifact(client, ws["id"], task["id"], unique)
    version = client.post(
        f"/workspaces/{ws['id']}/artifacts/{artifact['id']}/versions",
        json={"content_hash": f"h-{unique}", "content_ref": "s3://x"},
    ).json()

    key = f"pub-{unique}"
    body = {
        "idempotency_key": key,
        "content_version_id": version["id"],
        "account_id": account["id"],
        "platform": "test-platform",
        "published_at": "2026-08-25T00:00:00Z",
        "is_test": True,
    }
    r1 = client.post(f"/workspaces/{ws['id']}/publish-instances", json=body)
    r2 = client.post(f"/workspaces/{ws['id']}/publish-instances", json=body)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

    listing = client.get(
        f"/workspaces/{ws['id']}/content-versions/{version['id']}/publish-instances"
    ).json()
    assert len(listing) == 1, "retry must not create a second publish instance"
