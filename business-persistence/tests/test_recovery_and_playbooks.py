def test_run_state_upsert_and_read_roundtrip(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    task_id = bootstrapped["task"]["id"]

    before = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/run-state")
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
    )
    assert r1.status_code == 200
    assert r1.json()["last_success_step"] == "snapshot_saved"
    assert r1.json()["failed_step"] == "publish_registration"

    read_back = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/run-state")
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
    )
    assert r2.status_code == 200
    assert r2.json()["failed_step"] is None
    assert r2.json()["side_effects"]["publish_instance_id"] == "def-456"


def test_run_state_requires_task_in_workspace(client, bootstrapped):
    import uuid

    ws_id = bootstrapped["workspace"]["id"]
    r = client.get(f"/workspaces/{ws_id}/tasks/{uuid.uuid4()}/run-state")
    assert r.status_code == 404


def test_playbook_versioning_chains_history(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    name = f"playbook-{unique}"

    v1 = client.post(
        f"/workspaces/{ws_id}/playbooks",
        json={
            "name": name,
            "proposed_by": "M3-stub",
            "observation_status": "verified across 3 tasks",
            "rationale": "consistent lift on Tuesday posts",
        },
    ).json()
    assert v1["version_no"] == 1
    assert v1["is_current"] is True
    assert v1["supersedes_playbook_id"] is None

    current = client.get(f"/workspaces/{ws_id}/playbooks/{name}/current").json()
    assert current["id"] == v1["id"]

    v2 = client.post(
        f"/workspaces/{ws_id}/playbooks",
        json={
            "name": name,
            "proposed_by": "M3-stub",
            "observation_status": "revised after 2 more tasks",
            "rationale": "narrowed to weekday-only",
        },
    ).json()
    assert v2["version_no"] == 2
    assert v2["supersedes_playbook_id"] == v1["id"]

    current_after = client.get(f"/workspaces/{ws_id}/playbooks/{name}/current").json()
    assert current_after["id"] == v2["id"]

    versions = client.get(f"/workspaces/{ws_id}/playbooks/{name}/versions").json()
    assert [v["version_no"] for v in versions] == [1, 2]
    assert versions[0]["is_current"] is False, "superseded version must remain readable, not deleted"
    assert versions[0]["rationale"] == "consistent lift on Tuesday posts", "history must not be rewritten"


def test_playbook_not_found_when_no_current_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.get(f"/workspaces/{ws_id}/playbooks/never-created-{unique}/current")
    assert r.status_code == 404
