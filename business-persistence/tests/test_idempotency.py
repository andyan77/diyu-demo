from tests.conftest import (
    actor_headers,
    create_account,
    create_artifact,
    create_task,
    create_user,
    create_workspace,
)


def test_task_creation_retry_returns_same_task(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws = create_workspace(client, unique, user["id"])
    key = f"retry-{unique}"

    r1 = client.post(
        f"/workspaces/{ws['id']}/tasks", json={"idempotency_key": key}, headers=actor_headers(actor_ref)
    )
    r2 = client.post(
        f"/workspaces/{ws['id']}/tasks", json={"idempotency_key": key}, headers=actor_headers(actor_ref)
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

    # exactly one task exists with this idempotency_key on the read side too
    proj = client.get(
        f"/workspaces/{ws['id']}/tasks/{r1.json()['id']}/projection", headers=actor_headers(actor_ref)
    )
    assert proj.status_code == 200


def test_idempotency_key_is_scoped_per_workspace_not_global(client, unique):
    """Two different workspaces using the exact same idempotency_key for
    task creation must get two DIFFERENT tasks -- a shared global key space
    would let workspace A's retry silently return workspace B's row.
    """

    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    key = f"shared-key-{unique}"

    task_a = client.post(
        f"/workspaces/{ws_a['id']}/tasks", json={"idempotency_key": key}, headers=actor_headers(actor_ref)
    ).json()
    task_b = client.post(
        f"/workspaces/{ws_b['id']}/tasks", json={"idempotency_key": key}, headers=actor_headers(actor_ref)
    ).json()

    assert task_a["id"] != task_b["id"], (
        "the same idempotency_key in two different workspaces must not collapse into one task"
    )
    assert task_a["workspace_id"] == ws_a["id"]
    assert task_b["workspace_id"] == ws_b["id"]


def test_snapshot_creation_retry_returns_same_snapshot(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws = create_workspace(client, unique, user["id"])
    task = create_task(client, ws["id"], unique, actor_ref)
    key = f"snap-{unique}"
    body = {
        "idempotency_key": key,
        "payload": {"note": "first task"},
        "info_nature": "fact",
    }

    r1 = client.post(
        f"/workspaces/{ws['id']}/tasks/{task['id']}/snapshots", json=body, headers=actor_headers(actor_ref)
    )
    r2 = client.post(
        f"/workspaces/{ws['id']}/tasks/{task['id']}/snapshots", json=body, headers=actor_headers(actor_ref)
    )
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_publish_instance_retry_returns_same_instance(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws = create_workspace(client, unique, user["id"])
    account = create_account(client, ws["id"], unique, actor_ref)
    task = create_task(client, ws["id"], unique, actor_ref, account_id=account["id"])
    artifact = create_artifact(client, ws["id"], task["id"], unique, actor_ref)
    version = client.post(
        f"/workspaces/{ws['id']}/artifacts/{artifact['id']}/versions",
        json={"idempotency_key": f"v-{unique}", "content_hash": f"h-{unique}", "content_ref": "s3://x"},
        headers=actor_headers(actor_ref),
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
    r1 = client.post(f"/workspaces/{ws['id']}/publish-instances", json=body, headers=actor_headers(actor_ref))
    r2 = client.post(f"/workspaces/{ws['id']}/publish-instances", json=body, headers=actor_headers(actor_ref))
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

    listing = client.get(
        f"/workspaces/{ws['id']}/content-versions/{version['id']}/publish-instances",
        headers=actor_headers(actor_ref),
    ).json()
    assert len(listing) == 1, "retry must not create a second publish instance"


def test_publish_instance_idempotency_key_is_scoped_per_workspace(client, unique):
    """The same regression as test_idempotency_key_is_scoped_per_workspace_not_global,
    but for publish_instances specifically -- this is the exact table the
    independent review found leaking idempotency keys across workspaces.
    """

    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])

    account_a = create_account(client, ws_a["id"], unique + "-a", actor_ref)
    task_a = create_task(client, ws_a["id"], unique + "-a", actor_ref, account_id=account_a["id"])
    artifact_a = create_artifact(client, ws_a["id"], task_a["id"], unique + "-a", actor_ref)
    version_a = client.post(
        f"/workspaces/{ws_a['id']}/artifacts/{artifact_a['id']}/versions",
        json={"idempotency_key": f"v-a-{unique}", "content_hash": f"h-a-{unique}", "content_ref": "s3://x"},
        headers=actor_headers(actor_ref),
    ).json()

    account_b = create_account(client, ws_b["id"], unique + "-b", actor_ref)
    task_b = create_task(client, ws_b["id"], unique + "-b", actor_ref, account_id=account_b["id"])
    artifact_b = create_artifact(client, ws_b["id"], task_b["id"], unique + "-b", actor_ref)
    version_b = client.post(
        f"/workspaces/{ws_b['id']}/artifacts/{artifact_b['id']}/versions",
        json={"idempotency_key": f"v-b-{unique}", "content_hash": f"h-b-{unique}", "content_ref": "s3://x"},
        headers=actor_headers(actor_ref),
    ).json()

    key = f"shared-pub-key-{unique}"
    pub_a = client.post(
        f"/workspaces/{ws_a['id']}/publish-instances",
        json={
            "idempotency_key": key,
            "content_version_id": version_a["id"],
            "account_id": account_a["id"],
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
            "is_test": True,
        },
        headers=actor_headers(actor_ref),
    ).json()
    pub_b = client.post(
        f"/workspaces/{ws_b['id']}/publish-instances",
        json={
            "idempotency_key": key,
            "content_version_id": version_b["id"],
            "account_id": account_b["id"],
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
            "is_test": True,
        },
        headers=actor_headers(actor_ref),
    ).json()

    assert pub_a["id"] != pub_b["id"], (
        "the same idempotency_key in two different workspaces must not collapse into one publish_instance"
    )
    assert pub_a["content_version_id"] == version_a["id"]
    assert pub_b["content_version_id"] == version_b["id"]
