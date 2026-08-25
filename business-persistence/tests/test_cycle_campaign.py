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
