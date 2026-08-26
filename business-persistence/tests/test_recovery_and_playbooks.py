import uuid


def test_run_state_upsert_and_read_roundtrip(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    task_id = bootstrapped["task"]["id"]
    headers = bootstrapped["headers"]

    before = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/run-state", headers=headers)
    assert before.status_code == 200
    assert before.json()["recovery_state"] == "none_recorded"

    r1 = client.put(
        f"/workspaces/{ws_id}/tasks/{task_id}/run-state",
        json={
            "last_success_step": "snapshot_saved",
            "failed_step": "publish_registration",
            "resumable_from": "publish_registration",
            "side_effects": {"snapshot_id": "abc-123"},
        },
        headers=headers,
    )
    assert r1.status_code == 200
    assert r1.json()["last_success_step"] == "snapshot_saved"
    assert r1.json()["failed_step"] == "publish_registration"

    read_back = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/run-state", headers=headers)
    assert read_back.status_code == 200
    assert read_back.json()["resumable_from"] == "publish_registration"
    assert read_back.json()["side_effects"] == {"snapshot_id": "abc-123"}

    # simulate resuming and completing: upsert again, doesn't create a second row
    r2 = client.put(
        f"/workspaces/{ws_id}/tasks/{task_id}/run-state",
        json={
            "last_success_step": "publish_registration",
            "failed_step": None,
            "resumable_from": None,
            "side_effects": {"snapshot_id": "abc-123", "publish_instance_id": "def-456"},
        },
        headers=headers,
    )
    assert r2.status_code == 200
    assert r2.json()["failed_step"] is None
    assert r2.json()["side_effects"]["publish_instance_id"] == "def-456"


def test_run_state_partial_update_never_erases_prior_success_or_side_effects(client, bootstrapped):
    """The actual recovery guarantee: a resume attempt that only reports a
    NEW failed_step (last_success_step and side_effects omitted from the
    request entirely, not sent as null) must not erase the previously
    recorded successful step or the side effects that step already
    produced. This is the merge-vs-replace distinction upsert_run_state
    exists to enforce -- a naive "PUT replaces the row" implementation
    would wipe both fields here.
    """

    ws_id = bootstrapped["workspace"]["id"]
    task_id = bootstrapped["task"]["id"]
    headers = bootstrapped["headers"]

    client.put(
        f"/workspaces/{ws_id}/tasks/{task_id}/run-state",
        json={
            "last_success_step": "snapshot_saved",
            "side_effects": {"snapshot_id": "abc-123"},
        },
        headers=headers,
    )

    # a resume attempt that fails at a later step and only reports THAT --
    # last_success_step and side_effects are simply absent from this body.
    partial = client.put(
        f"/workspaces/{ws_id}/tasks/{task_id}/run-state",
        json={"failed_step": "publish_registration"},
        headers=headers,
    )
    assert partial.status_code == 200
    assert partial.json()["failed_step"] == "publish_registration"
    assert partial.json()["last_success_step"] == "snapshot_saved", (
        "a partial update must not erase the previously recorded successful step"
    )
    assert partial.json()["side_effects"] == {"snapshot_id": "abc-123"}, (
        "a partial update must not erase previously recorded side effects"
    )

    # a later partial update contributing a NEW side_effects key must union
    # it in, not replace the whole dict
    unioned = client.put(
        f"/workspaces/{ws_id}/tasks/{task_id}/run-state",
        json={"side_effects": {"publish_instance_id": "def-456"}},
        headers=headers,
    )
    assert unioned.status_code == 200
    assert unioned.json()["side_effects"] == {
        "snapshot_id": "abc-123",
        "publish_instance_id": "def-456",
    }, "a new side_effects key must be unioned into the existing dict, not replace it"


def test_run_state_requires_task_in_workspace(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.get(f"/workspaces/{ws_id}/tasks/{uuid.uuid4()}/run-state", headers=bootstrapped["headers"])
    assert r.status_code == 404


def test_playbook_versioning_chains_history(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    name = f"playbook-{unique}"

    v1 = client.post(
        f"/workspaces/{ws_id}/playbooks",
        json={
            "idempotency_key": f"pb-1-{unique}",
            "name": name,
            "proposed_by": "M3-stub",
            "observation_status": "verified across 3 tasks",
            "rationale": "consistent lift on Tuesday posts",
        },
        headers=headers,
    ).json()
    assert v1["version_no"] == 1
    assert v1["is_current"] is True
    assert v1["supersedes_playbook_id"] is None

    current = client.get(f"/workspaces/{ws_id}/playbooks/{name}/current", headers=headers).json()
    assert current["id"] == v1["id"]

    v2 = client.post(
        f"/workspaces/{ws_id}/playbooks",
        json={
            "idempotency_key": f"pb-2-{unique}",
            "name": name,
            "proposed_by": "M3-stub",
            "observation_status": "revised after 2 more tasks",
            "rationale": "narrowed to weekday-only",
        },
        headers=headers,
    ).json()
    assert v2["version_no"] == 2
    assert v2["supersedes_playbook_id"] == v1["id"]

    current_after = client.get(f"/workspaces/{ws_id}/playbooks/{name}/current", headers=headers).json()
    assert current_after["id"] == v2["id"]

    versions = client.get(f"/workspaces/{ws_id}/playbooks/{name}/versions", headers=headers).json()
    assert [v["version_no"] for v in versions] == [1, 2]
    assert versions[0]["is_current"] is False, "superseded version must remain readable, not deleted"
    assert versions[0]["rationale"] == "consistent lift on Tuesday posts", "history must not be rewritten"


def test_playbook_creation_retry_returns_same_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    name = f"playbook-retry-{unique}"
    key = f"pb-retry-{unique}"
    body = {"idempotency_key": key, "name": name, "rationale": "x"}

    r1 = client.post(f"/workspaces/{ws_id}/playbooks", json=body, headers=headers).json()
    r2 = client.post(f"/workspaces/{ws_id}/playbooks", json=body, headers=headers).json()
    assert r1["id"] == r2["id"], "retrying with the same idempotency_key must not create a second version"


def test_playbook_not_found_when_no_current_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.get(
        f"/workspaces/{ws_id}/playbooks/never-created-{unique}/current", headers=bootstrapped["headers"]
    )
    assert r.status_code == 404
