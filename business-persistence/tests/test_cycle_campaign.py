def test_cycle_transition_chains_history_and_flips_current(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle_1 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-1-{unique}",
            "account_id": account_id,
            "label": f"cycle-1-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
            "baseline_capacity": 10,
            "baseline_capacity_source": "team default",
            "actual_capacity": 8,
            "actual_capacity_source": "current headcount",
            "expected_publish_count": 12,
            "expected_publish_count_source": "user request",
        },
        headers=headers,
    ).json()
    assert cycle_1["is_current"] is True
    assert cycle_1["supersedes_cycle_id"] is None

    cycle_2 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-2-{unique}",
            "account_id": account_id,
            "label": f"cycle-2-{unique}",
            "start_at": "2026-09-01T00:00:00Z",
        },
        headers=headers,
    ).json()
    assert cycle_2["is_current"] is True
    assert cycle_2["supersedes_cycle_id"] == cycle_1["id"]

    current = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/current", headers=headers
    ).json()
    assert current["id"] == cycle_2["id"]

    history = client.get(f"/workspaces/{ws_id}/accounts/{account_id}/cycles", headers=headers).json()
    ids = {c["id"] for c in history}
    assert {cycle_1["id"], cycle_2["id"]} <= ids, "history must keep both cycles readable"

    by_id = {c["id"]: c for c in history}
    assert by_id[cycle_1["id"]]["is_current"] is False


def test_cycle_decision_kept_unchanged_is_recorded_without_touching_the_cycle(client, bootstrapped, unique):
    """M2-AC-07's second branch: M3 evaluates a cycle's evidence and decides
    nothing should change. That decision must be observable -- not just
    absence of a new cycle -- and the current cycle must stay exactly as it
    was (no row touched, no version bump).
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-keep-{unique}",
            "account_id": account_id,
            "label": f"cycle-keep-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()

    r = client.post(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions",
        json={
            "idempotency_key": f"decision-keep-{unique}",
            "cycle_id": cycle["id"],
            "decision": "kept_unchanged",
            "source": "M3",
            "rationale": "反馈显示当前节奏有效，无需调整",
            "based_on": {"feedback_ids": ["fb-1", "fb-2"]},
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    decision = r.json()
    assert decision["decision"] == "kept_unchanged"
    assert decision["resulting_cycle_id"] is None
    assert decision["source"] == "M3"

    latest = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions/latest", headers=headers
    ).json()
    assert latest["id"] == decision["id"]

    still_current = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/current", headers=headers
    ).json()
    assert still_current["id"] == cycle["id"]
    assert still_current["row_version"] == cycle["row_version"], (
        "recording a kept_unchanged decision must not touch the cycle row at all"
    )


def test_cycle_decision_adjusted_must_reference_a_real_superseding_cycle(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle_1 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-adj-1-{unique}",
            "account_id": account_id,
            "label": f"cycle-adj-1-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()
    cycle_2 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-adj-2-{unique}",
            "account_id": account_id,
            "label": f"cycle-adj-2-{unique}",
            "start_at": "2026-09-01T00:00:00Z",
        },
        headers=headers,
    ).json()

    r = client.post(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions",
        json={
            "idempotency_key": f"decision-adj-{unique}",
            "cycle_id": cycle_1["id"],
            "decision": "adjusted",
            "source": "M3",
            "rationale": "完播率下降，建议提高节奏",
            "resulting_cycle_id": cycle_2["id"],
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["resulting_cycle_id"] == cycle_2["id"]

    retry = client.post(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions",
        json={
            "idempotency_key": f"decision-adj-{unique}",
            "cycle_id": cycle_1["id"],
            "decision": "adjusted",
            "resulting_cycle_id": cycle_2["id"],
        },
        headers=headers,
    )
    assert retry.status_code == 200
    assert retry.json()["id"] == r.json()["id"], "same idempotency_key must not create a second decision row"


def test_cycle_decision_rejects_mismatched_decision_and_resulting_cycle(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle_1 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-neg-1-{unique}",
            "account_id": account_id,
            "label": f"cycle-neg-1-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()
    cycle_2 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-neg-2-{unique}",
            "account_id": account_id,
            "label": f"cycle-neg-2-{unique}",
            "start_at": "2026-09-01T00:00:00Z",
        },
        headers=headers,
    ).json()

    adjusted_without_target = client.post(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions",
        json={
            "idempotency_key": f"decision-neg-1-{unique}",
            "cycle_id": cycle_1["id"],
            "decision": "adjusted",
        },
        headers=headers,
    )
    assert adjusted_without_target.status_code == 422
    assert "resulting_cycle_id" in adjusted_without_target.json()["detail"]

    kept_with_target = client.post(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions",
        json={
            "idempotency_key": f"decision-neg-2-{unique}",
            "cycle_id": cycle_1["id"],
            "decision": "kept_unchanged",
            "resulting_cycle_id": cycle_2["id"],
        },
        headers=headers,
    )
    assert kept_with_target.status_code == 422
    assert "must not set resulting_cycle_id" in kept_with_target.json()["detail"]


def test_cycle_decision_rejects_kept_unchanged_on_an_already_superseded_cycle(client, bootstrapped, unique):
    """A structural (not judgment) check: recording kept_unchanged only
    makes sense against whatever cycle was current at decision time. If
    cycle_1 has already been superseded by cycle_2 by the time this call
    arrives, accepting a kept_unchanged verdict on cycle_1 would leave
    decisions/latest and /cycles/current visibly disagreeing about it.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle_1 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-stale-1-{unique}",
            "account_id": account_id,
            "label": f"cycle-stale-1-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()
    client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-stale-2-{unique}",
            "account_id": account_id,
            "label": f"cycle-stale-2-{unique}",
            "start_at": "2026-09-01T00:00:00Z",
        },
        headers=headers,
    )

    r = client.post(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/decisions",
        json={
            "idempotency_key": f"decision-stale-{unique}",
            "cycle_id": cycle_1["id"],
            "decision": "kept_unchanged",
        },
        headers=headers,
    )
    assert r.status_code == 422
    assert "no longer the current cycle" in r.json()["detail"]


def test_cycle_idempotency_is_scoped_per_account_not_just_workspace(client, bootstrapped, unique):
    """Regression: create_cycle and record_cycle_decision used to scope
    their idempotency lookup by workspace_id alone. Two different accounts
    in the same workspace picking the same idempotency_key string by
    coincidence would collide -- whichever called second silently got back
    the first account's cycle/decision instead of creating its own.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_a = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]
    account_b = client.post(
        f"/workspaces/{ws_id}/accounts",
        json={"platform": "test-platform", "handle": f"handle-b-{unique}"},
        headers=headers,
    ).json()["id"]

    shared_key = f"shared-cycle-key-{unique}"
    cycle_a = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": shared_key,
            "account_id": account_a,
            "label": "account-a-cycle",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()
    cycle_b = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": shared_key,
            "account_id": account_b,
            "label": "account-b-cycle",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()
    assert cycle_a["id"] != cycle_b["id"], (
        "two different accounts must never collide on the same idempotency_key string"
    )
    assert cycle_a["account_id"] == account_a
    assert cycle_b["account_id"] == account_b

    shared_decision_key = f"shared-decision-key-{unique}"
    decision_a = client.post(
        f"/workspaces/{ws_id}/accounts/{account_a}/cycles/decisions",
        json={"idempotency_key": shared_decision_key, "cycle_id": cycle_a["id"], "decision": "kept_unchanged"},
        headers=headers,
    ).json()
    decision_b = client.post(
        f"/workspaces/{ws_id}/accounts/{account_b}/cycles/decisions",
        json={"idempotency_key": shared_decision_key, "cycle_id": cycle_b["id"], "decision": "kept_unchanged"},
        headers=headers,
    ).json()
    assert decision_a["id"] != decision_b["id"]
    assert decision_a["account_id"] == account_a
    assert decision_b["account_id"] == account_b


def test_cycle_idempotency_key_is_scoped_per_workspace(client, unique):
    """Regression for the confirmed cross-workspace write-corruption finding:
    create_cycle's "prior current cycle" lookup, and its idempotency check,
    must both be scoped to the calling workspace_id -- an unscoped lookup
    let workspace A's cycle creation chain off of (and be confused for a
    retry of) workspace B's cycle when the two picked the same account_id-
    shaped coincidence.
    """

    from tests.conftest import actor_headers, create_account, create_user, create_workspace

    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    account_a = create_account(client, ws_a["id"], unique + "-a", actor_ref)
    account_b = create_account(client, ws_b["id"], unique + "-b", actor_ref)

    key = f"shared-cycle-key-{unique}"
    cycle_a = client.post(
        f"/workspaces/{ws_a['id']}/cycles",
        json={"idempotency_key": key, "account_id": account_a["id"], "label": "a", "start_at": "2026-08-01T00:00:00Z"},
        headers=actor_headers(actor_ref),
    ).json()
    cycle_b = client.post(
        f"/workspaces/{ws_b['id']}/cycles",
        json={"idempotency_key": key, "account_id": account_b["id"], "label": "b", "start_at": "2026-08-01T00:00:00Z"},
        headers=actor_headers(actor_ref),
    ).json()

    assert cycle_a["id"] != cycle_b["id"]
    assert cycle_a["workspace_id"] == ws_a["id"]
    assert cycle_b["workspace_id"] == ws_b["id"]
    assert cycle_a["supersedes_cycle_id"] is None, "workspace B's cycle must never appear as A's prior cycle"
    assert cycle_b["supersedes_cycle_id"] is None, "workspace A's cycle must never appear as B's prior cycle"


def test_capacity_triple_split_kept_separate(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"cycle-{unique}",
            "account_id": account_id,
            "label": f"cycle-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
            "baseline_capacity": 20,
            "actual_capacity": 15,
            "expected_publish_count": 30,
        },
        headers=headers,
    ).json()
    assert cycle["baseline_capacity"] == 20
    assert cycle["actual_capacity"] == 15
    assert cycle["expected_publish_count"] == 30
    assert len({cycle["baseline_capacity"], cycle["actual_capacity"], cycle["expected_publish_count"]}) == 3


def test_campaign_override_targets_positions_and_ends_cleanly(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"c-{unique}",
            "account_id": account_id,
            "label": f"c-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()

    override = client.post(
        f"/workspaces/{ws_id}/campaign-overrides",
        json={
            "account_id": account_id,
            "cycle_id": cycle["id"],
            "name": f"launch-{unique}",
            "scope_start": "2026-08-10T00:00:00Z",
            "scope_end": "2026-08-20T00:00:00Z",
            "targeted_positions": ["monday-slot", "wednesday-slot"],
        },
        headers=headers,
    ).json()
    assert override["status"] == "active"

    active = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/campaign-overrides/active", headers=headers
    ).json()
    assert any(o["id"] == override["id"] for o in active)

    ended = client.post(
        f"/workspaces/{ws_id}/campaign-overrides/{override['id']}/end", json={}, headers=headers
    ).json()
    assert ended["status"] == "ended"
    assert ended["ended_at"] is not None

    active_after = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/campaign-overrides/active", headers=headers
    ).json()
    assert all(o["id"] != override["id"] for o in active_after)

    # ending is idempotent -- calling it again just returns the same ended state
    ended_again = client.post(
        f"/workspaces/{ws_id}/campaign-overrides/{override['id']}/end", json={}, headers=headers
    ).json()
    assert ended_again["ended_at"] == ended["ended_at"]

    # cycle baseline is untouched by the override lifecycle
    current_cycle = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/current", headers=headers
    ).json()
    assert current_cycle["id"] == cycle["id"]


def test_campaign_override_rejects_account_cycle_mismatch(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    from tests.conftest import create_account

    other_account = create_account(client, ws_id, unique + "-other", bootstrapped["actor_ref"])
    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"c-{unique}",
            "account_id": account_id,
            "label": f"c-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
        },
        headers=headers,
    ).json()

    r = client.post(
        f"/workspaces/{ws_id}/campaign-overrides",
        json={
            "account_id": other_account["id"],
            "cycle_id": cycle["id"],
            "name": f"mismatch-{unique}",
            "scope_start": "2026-08-10T00:00:00Z",
            "targeted_positions": [],
        },
        headers=headers,
    )
    assert r.status_code == 422
