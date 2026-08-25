import os
import uuid

import httpx
import pytest


BASE_URL = os.environ.get("APP_BASE_URL", "http://diyu-m2-app:8000")


@pytest.fixture()
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.fixture()
def unique():
    return uuid.uuid4().hex


def create_user(client, unique):
    r = client.post("/users", json={"external_ref": f"user-{unique}"})
    assert r.status_code == 200, r.text
    return r.json()


def create_workspace(client, unique, owner_user_id):
    r = client.post(
        "/workspaces", json={"name": f"ws-{unique}", "kind": "personal", "owner_user_id": owner_user_id}
    )
    assert r.status_code == 200, r.text
    return r.json()


def create_account(client, workspace_id, unique):
    r = client.post(
        f"/workspaces/{workspace_id}/accounts",
        json={"platform": "test-platform", "handle": f"handle-{unique}"},
    )
    assert r.status_code == 200, r.text
    return r.json()


def create_task(client, workspace_id, unique, account_id=None):
    r = client.post(
        f"/workspaces/{workspace_id}/tasks",
        json={"idempotency_key": f"task-{unique}", "account_id": account_id, "kind": "test"},
    )
    assert r.status_code == 200, r.text
    return r.json()


def create_artifact(client, workspace_id, task_id, unique):
    r = client.post(
        f"/workspaces/{workspace_id}/tasks/{task_id}/artifacts",
        json={"kind": "final", "content_hash": f"hash-{unique}"},
    )
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture()
def bootstrapped(client, unique):
    """A user + workspace + account + task + artifact, ready for
    version/publish/feedback tests to build on.
    """

    user = create_user(client, unique)
    ws = create_workspace(client, unique, user["id"])
    account = create_account(client, ws["id"], unique)
    task = create_task(client, ws["id"], unique, account_id=account["id"])
    artifact = create_artifact(client, ws["id"], task["id"], unique)
    return {
        "user": user,
        "workspace": ws,
        "account": account,
        "task": task,
        "artifact": artifact,
    }
