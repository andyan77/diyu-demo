def test_cycle_transition_chains_history_and_flips_current(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]

    cycle_1 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
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
    ).json()
    assert cycle_1["is_current"] is True
    assert cycle_1["supersedes_cycle_id"] is None

    cycle_2 = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "account_id": account_id,
            "label": f"cycle-2-{unique}",
            "start_at": "2026-09-01T00:00:00Z",
        },
    ).json()
    assert cycle_2["is_current"] is True
    assert cycle_2["supersedes_cycle_id"] == cycle_1["id"]

    current = client.get(f"/workspaces/{ws_id}/accounts/{account_id}/cycles/current").json()
    assert current["id"] == cycle_2["id"]

    history = client.get(f"/workspaces/{ws_id}/accounts/{account_id}/cycles").json()
    ids = {c["id"] for c in history}
    assert {cycle_1["id"], cycle_2["id"]} <= ids, "history must keep both cycles readable"

    by_id = {c["id"]: c for c in history}
    assert by_id[cycle_1["id"]]["is_current"] is False


def test_capacity_triple_split_kept_separate(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]

    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "account_id": account_id,
            "label": f"cycle-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
            "baseline_capacity": 20,
            "actual_capacity": 15,
            "expected_publish_count": 30,
        },
    ).json()
    assert cycle["baseline_capacity"] == 20
    assert cycle["actual_capacity"] == 15
    assert cycle["expected_publish_count"] == 30
    assert len({cycle["baseline_capacity"], cycle["actual_capacity"], cycle["expected_publish_count"]}) == 3


def test_campaign_override_targets_positions_and_ends_cleanly(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]

    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={"account_id": account_id, "label": f"c-{unique}", "start_at": "2026-08-01T00:00:00Z"},
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
    ).json()
    assert override["status"] == "active"

    active = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/campaign-overrides/active"
    ).json()
    assert any(o["id"] == override["id"] for o in active)

    ended = client.post(
        f"/workspaces/{ws_id}/campaign-overrides/{override['id']}/end", json={}
    ).json()
    assert ended["status"] == "ended"
    assert ended["ended_at"] is not None

    active_after = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/campaign-overrides/active"
    ).json()
    assert all(o["id"] != override["id"] for o in active_after)

    # ending is idempotent -- calling it again just returns the same ended state
    ended_again = client.post(
        f"/workspaces/{ws_id}/campaign-overrides/{override['id']}/end", json={}
    ).json()
    assert ended_again["ended_at"] == ended["ended_at"]

    # cycle baseline is untouched by the override lifecycle
    current_cycle = client.get(f"/workspaces/{ws_id}/accounts/{account_id}/cycles/current").json()
    assert current_cycle["id"] == cycle["id"]
