import uuid


def _legacy_snapshot(goal="帮我看看这周三条内容能不能按时发", confirmed=True):
    task_obj = {"goal": goal, "target_object": "本周排期"}
    return {
        "schema_version": 1,
        "task_id": f"legacy-{uuid.uuid4().hex[:8]}",
        "revision": 3,
        "phase": "READY" if confirmed else "FORMING",
        "candidate_skill": "CAMPAIGN",
        "draft_task": task_obj,
        "confirmed_task": task_obj if confirmed else None,
        "pending_action": None,
        "authorization": {
            "skill": "CAMPAIGN",
            "task_revision": 3,
            "confirmation_id": "conf-1",
            "granted": confirmed,
            "consumed": confirmed,
        },
        "artifacts": {"matrix": None, "campaign": None, "content_brief": None},
        "blocking_gap": None,
        "last_result_ref": None,
        "last_error": None,
    }


def test_valid_legacy_import_creates_readable_snapshot(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    r = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={
            "idempotency_key": f"legacy-{unique}",
            "account_id": account_id,
            "legacy_snapshot": _legacy_snapshot(),
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    task_id = body["task"]["id"]
    assert body["snapshot"]["source"] == "legacy_dify_v1_task_snapshot_import"

    projection = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/projection", headers=headers).json()
    assert projection["latest_snapshot"]["payload"]["note"] == "帮我看看这周三条内容能不能按时发"
    assert projection["latest_snapshot"]["source"] == "legacy_dify_v1_task_snapshot_import"


def test_legacy_import_is_idempotent(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]
    key = f"legacy-idem-{unique}"

    r1 = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": key, "account_id": account_id, "legacy_snapshot": _legacy_snapshot()},
        headers=headers,
    )
    r2 = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": key, "account_id": account_id, "legacy_snapshot": _legacy_snapshot(goal="换一个原话也不该生效")},
        headers=headers,
    )
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["task"]["id"] == r2.json()["task"]["id"]
    assert r1.json()["snapshot"]["id"] == r2.json()["snapshot"]["id"], (
        "retrying the same idempotency_key must return the original import, never create a second task/snapshot"
    )


def test_legacy_import_rejects_missing_required_key(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    broken = _legacy_snapshot()
    del broken["authorization"]

    r = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": f"legacy-broken-{unique}", "legacy_snapshot": broken},
        headers=headers,
    )
    assert r.status_code == 422
    assert "authorization" in r.json()["detail"]


def test_legacy_import_provenance_reflects_old_confirmation_state(client, bootstrapped, unique):
    """A snapshot imported from an old CONFIRMED task is tagged fact/confirmed;
    one imported from an old un-confirmed draft is tagged preference/inferred.
    Either way `source` makes clear it's an import, not a live M2 confirmation.
    """

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    confirmed = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={
            "idempotency_key": f"legacy-confirmed-{unique}",
            "legacy_snapshot": _legacy_snapshot(confirmed=True),
        },
        headers=headers,
    ).json()
    assert confirmed["snapshot"]["info_nature"] == "fact"
    assert confirmed["snapshot"]["confirmation_status"] == "confirmed"
    assert confirmed["snapshot"]["source"] == "legacy_dify_v1_task_snapshot_import"

    draft = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={
            "idempotency_key": f"legacy-draft-{unique}",
            "legacy_snapshot": _legacy_snapshot(confirmed=False),
        },
        headers=headers,
    ).json()
    assert draft["snapshot"]["info_nature"] == "preference"
    assert draft["snapshot"]["confirmation_status"] == "inferred"
    assert draft["snapshot"]["source"] == "legacy_dify_v1_task_snapshot_import"


def test_legacy_import_empty_confirmed_task_falls_back_to_draft_goal(client, bootstrapped, unique):
    """Regression: an earlier version picked which goal to read using
    isinstance(confirmed_task, dict) but classified confirmed-vs-draft using
    `if confirmed_task:` truthiness -- for confirmed_task={} (present but
    empty, distinct from None) those two checks disagreed: it read the
    (nonexistent) goal from the empty dict while classifying itself as an
    unconfirmed draft, silently losing draft_task's real goal and leaving
    payload.note == None.
    """

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    snapshot = _legacy_snapshot(goal="draft 里的真实诉求")
    snapshot["confirmed_task"] = {}

    r = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": f"legacy-empty-confirmed-{unique}", "legacy_snapshot": snapshot},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["snapshot"]["payload"]["note"] == "draft 里的真实诉求"
    assert body["snapshot"]["info_nature"] == "preference"
    assert body["snapshot"]["confirmation_status"] == "inferred"


def test_legacy_import_never_collides_with_a_live_task_idempotency_key(client, bootstrapped, unique):
    """Regression for a confirmed cross-namespace collision: an earlier
    version of legacy-import looked up (and created) its Task row keyed by
    the SAME (workspace_id, idempotency_key) space as live task creation.
    A live task and a legacy import choosing the same key string by pure
    coincidence would collide -- whichever ran second silently got back the
    first's row (a false-success 200 with the wrong task/no snapshot, or a
    live user-confirmed task quietly gaining a legacy-tagged snapshot).
    Both directions must now be impossible.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]
    shared_key = f"shared-key-{unique}"

    live_task = client.post(
        f"/workspaces/{ws_id}/tasks",
        json={"idempotency_key": shared_key, "account_id": account_id, "kind": "test"},
        headers=headers,
    ).json()

    legacy = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": shared_key, "account_id": account_id, "legacy_snapshot": _legacy_snapshot()},
        headers=headers,
    )
    assert legacy.status_code == 200, legacy.text
    legacy_body = legacy.json()
    assert legacy_body["task"]["id"] != live_task["id"], (
        "a legacy import must never be handed back an unrelated live task just because "
        "the idempotency_key string happened to collide"
    )
    assert legacy_body["snapshot"] is not None, (
        "a legacy import must always actually import, never silently no-op with snapshot: null"
    )

    other_key = f"shared-key-reverse-{unique}"
    legacy_first = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": other_key, "account_id": account_id, "legacy_snapshot": _legacy_snapshot()},
        headers=headers,
    ).json()
    live_second = client.post(
        f"/workspaces/{ws_id}/tasks",
        json={"idempotency_key": other_key, "account_id": account_id, "kind": "test"},
        headers=headers,
    ).json()
    assert live_second["id"] != legacy_first["task"]["id"], (
        "a live task-creation call must never be handed back a legacy-imported task just "
        "because the idempotency_key string happened to collide"
    )
    assert live_second["kind"] == "test"


def test_legacy_import_retry_survives_a_later_snapshot_added_to_the_same_task(client, bootstrapped, unique):
    """Regression: closing-verification found that adding a second snapshot
    to a legacy-imported task via the normal snapshots endpoint (nothing
    forbids this -- a legacy-imported task can keep receiving live
    snapshots afterward) made a subsequent legacy-import retry raise
    MultipleResultsFound (a 500) instead of returning cleanly.
    """

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    key = f"legacy-plus-snapshot-{unique}"

    first = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": key, "legacy_snapshot": _legacy_snapshot()},
        headers=headers,
    ).json()

    client.post(
        f"/workspaces/{ws_id}/tasks/{first['task']['id']}/snapshots",
        json={"idempotency_key": f"live-followup-{unique}", "payload": {}, "info_nature": "fact"},
        headers=headers,
    )

    retry = client.post(
        f"/workspaces/{ws_id}/tasks/legacy-import",
        json={"idempotency_key": key, "legacy_snapshot": _legacy_snapshot()},
        headers=headers,
    )
    assert retry.status_code == 200, retry.text
    assert retry.json()["task"]["id"] == first["task"]["id"]
