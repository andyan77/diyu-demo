def test_expired_observation_is_flagged_not_silently_current(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"survey-{unique}",
            "platform": "test-platform",
            "collected_at": "2020-01-01T00:00:00Z",
            "valid_until": "2020-02-01T00:00:00Z",
            "layer": "raw",
        },
        headers=headers,
    )
    client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"survey-fresh-{unique}",
            "platform": "test-platform",
            "collected_at": "2026-08-01T00:00:00Z",
            "valid_until": "2099-01-01T00:00:00Z",
            "layer": "raw",
        },
        headers=headers,
    )

    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    by_source = {r["source"]: r for r in rows}
    assert by_source[f"survey-{unique}"]["is_expired"] is True
    assert by_source[f"survey-fresh-{unique}"]["is_expired"] is False


def test_missing_observation_is_an_honest_empty_list(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=bootstrapped["headers"]).json()
    assert rows == [], "a brand-new workspace must report no comparison, never fabricate one"


def test_layer_is_validated(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"bad-{unique}",
            "collected_at": "2026-08-01T00:00:00Z",
            "layer": "definitely_not_a_real_layer",
        },
        headers=bootstrapped["headers"],
    )
    assert r.status_code == 422


# --- M2 post-DONE Rebase v1.2 (R-03/R-04/R-05/R-06): market observation
# permission semantics ---------------------------------------------------

import concurrent.futures

import httpx

from tests.conftest import BASE_URL, actor_headers, create_account, create_task, create_user, create_workspace


def _create_observation(client, ws_id, headers, unique, **overrides):
    body = {
        "source": f"obs-{unique}",
        "collected_at": "2026-08-01T00:00:00Z",
        "valid_until": "2099-01-01T00:00:00Z",
        "layer": "raw",
    }
    body.update(overrides)
    r = client.post(f"/workspaces/{ws_id}/market-observations", json=body, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


def test_source_type_accepts_representative_and_novel_values_not_a_closed_enum(
    client, bootstrapped, unique
):
    for i, source_type in enumerate(
        ["web_search", "user_provided_sample", "manual_import", "live_stream_scrape_not_in_any_list"]
    ):
        obs = _create_observation(
            client,
            bootstrapped["workspace"]["id"],
            bootstrapped["headers"],
            f"{unique}-{i}",
            source_type=source_type,
        )
        assert obs["source_type"] == source_type


def test_permission_status_defaults_to_unknown_never_allowed(client, bootstrapped, unique):
    obs = _create_observation(client, bootstrapped["workspace"]["id"], bootstrapped["headers"], unique)
    assert obs["permission_status"] == "unknown", (
        "an absent permission decision must never be silently treated as 'allowed'"
    )


def test_permission_status_five_states_validated(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    for i, status in enumerate(["allowed", "unknown", "missing", "denied", "restricted"]):
        obs = _create_observation(client, ws_id, headers, f"{unique}-{i}", permission_status=status)
        assert obs["permission_status"] == status

    r = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"bad-perm-{unique}",
            "collected_at": "2026-08-01T00:00:00Z",
            "permission_status": "definitely_not_a_real_status",
        },
        headers=headers,
    )
    assert r.status_code == 422


def test_current_projection_only_returns_allowed_or_restricted_and_unexpired(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    for i, status in enumerate(["allowed", "unknown", "missing", "denied", "restricted"]):
        _create_observation(
            client, ws_id, headers, f"{unique}-{i}", source=f"perm-{status}-{unique}", permission_status=status
        )

    current = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    sources = {o["source"] for o in current["observations"]}
    assert sources == {f"perm-allowed-{unique}", f"perm-restricted-{unique}"}
    assert current["available"] is True
    assert current["gap_reason"] is None

    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    by_source = {r["source"]: r for r in rows}
    assert by_source[f"perm-unknown-{unique}"]["excluded_reason"] == "permission_unknown"
    assert by_source[f"perm-missing-{unique}"]["excluded_reason"] == "permission_missing"
    assert by_source[f"perm-denied-{unique}"]["excluded_reason"] == "permission_denied"
    assert by_source[f"perm-allowed-{unique}"]["excluded_reason"] is None
    assert by_source[f"perm-allowed-{unique}"]["currently_usable"] is True


def test_expired_observation_excluded_from_current_even_when_permission_allowed(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    _create_observation(
        client,
        ws_id,
        headers,
        unique,
        permission_status="allowed",
        collected_at="2020-01-01T00:00:00Z",
        valid_until="2020-02-01T00:00:00Z",
    )

    current = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    assert current["observations"] == []
    assert current["gap_reason"] == "all_observations_excluded"

    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    assert rows[0]["excluded_reason"] == "expired"


def test_scope_mismatch_excludes_from_current_projection_but_stays_in_history(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    account_a = bootstrapped["account"]["id"]
    account_b = create_account(client, ws_id, f"{unique}-b", bootstrapped["actor_ref"])["id"]

    _create_observation(
        client, ws_id, headers, unique, permission_status="allowed", account_id=account_a
    )

    matching = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"account_id": account_a},
        headers=headers,
    ).json()
    assert len(matching["observations"]) == 1

    mismatched = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"account_id": account_b},
        headers=headers,
    ).json()
    assert mismatched["observations"] == []
    assert mismatched["gap_reason"] == "no_observation_in_scope"
    # scope-excluded, but NOT silently dropped -- it must show up with a reason
    assert len(mismatched["excluded"]) == 1
    assert mismatched["excluded"][0]["reason"] == "scope_mismatch"

    # still fully present in the unfiltered audit history
    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    assert any(r["account_id"] == account_a for r in rows)


def test_current_projection_states_a_reason_for_every_non_usable_record_mixed_case(
    client, bootstrapped, unique
):
    """A workspace can simultaneously hold an in-scope-and-usable
    observation and an out-of-scope one -- the out-of-scope one must still
    surface with its own reason, not vanish just because something else
    satisfied the query."""

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    account_a = bootstrapped["account"]["id"]
    account_b = create_account(client, ws_id, f"{unique}-b", bootstrapped["actor_ref"])["id"]

    usable_obs = _create_observation(
        client, ws_id, headers, f"{unique}-usable", permission_status="allowed", account_id=account_a
    )
    excluded_obs = _create_observation(
        client, ws_id, headers, f"{unique}-excluded", permission_status="allowed", account_id=account_b
    )

    result = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"account_id": account_a},
        headers=headers,
    ).json()
    assert {o["id"] for o in result["observations"]} == {usable_obs["id"]}
    assert {(e["id"], e["reason"]) for e in result["excluded"]} == {
        (excluded_obs["id"], "scope_mismatch")
    }
    # every observation that exists must be accounted for exactly once
    all_ids = {o["id"] for o in result["observations"]} | {e["id"] for e in result["excluded"]}
    assert all_ids == {usable_obs["id"], excluded_obs["id"]}


def test_current_projection_rejects_out_of_workspace_scope_filters(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    other_user = create_user(client, unique + "-other")
    other_ws = create_workspace(client, unique + "-other", other_user["id"])
    other_account = create_account(client, other_ws["id"], unique + "-other", other_user["external_ref"])

    r = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"account_id": other_account["id"]},
        headers=headers,
    )
    assert r.status_code == 404

    r = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"task_id": bootstrapped["task"]["id"]},  # belongs to ws_id itself -- must be accepted
        headers=headers,
    )
    assert r.status_code == 200

    other_task = create_task(client, other_ws["id"], unique + "-other", other_user["external_ref"])
    r = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"task_id": other_task["id"]},
        headers=headers,
    )
    assert r.status_code == 404


def test_layers_are_stored_verbatim_never_upgraded_into_each_other(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    for i, layer in enumerate(["raw", "analysis", "homogeneous_judgment"]):
        obs = _create_observation(
            client, ws_id, headers, f"{unique}-{i}", source=f"layer-{layer}-{unique}", layer=layer
        )
        assert obs["layer"] == layer

    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    stored_layers = {r["source"]: r["layer"] for r in rows if r["source"] and "layer-" in r["source"]}
    assert stored_layers == {
        f"layer-raw-{unique}": "raw",
        f"layer-analysis-{unique}": "analysis",
        f"layer-homogeneous_judgment-{unique}": "homogeneous_judgment",
    }


def test_no_observation_returns_explicit_gap_not_ambiguous_empty_list(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    current = client.get(
        f"/workspaces/{ws_id}/market-observations/current", headers=bootstrapped["headers"]
    ).json()
    assert current["available"] is False
    assert current["observations"] == []
    assert current["gap_reason"] == "no_observation_recorded"


_FORBIDDEN_CONCLUSION_KEYS = {
    "is_scarce",
    "is_unique",
    "avoided_homogeneity",
    "conclusion",
    "insight",
    "recommendation",
    "competitive_summary",
}


def _assert_no_conclusion_shape(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert k not in _FORBIDDEN_CONCLUSION_KEYS, f"found a fabricated-conclusion-shaped key: {k}"
            _assert_no_conclusion_shape(v)
    elif isinstance(obj, list):
        for item in obj:
            _assert_no_conclusion_shape(item)


def test_current_projection_never_carries_a_fabricated_competitive_conclusion(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    empty = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    _assert_no_conclusion_shape(empty)

    _create_observation(client, ws_id, headers, unique, permission_status="allowed")
    populated = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    _assert_no_conclusion_shape(populated)


def test_market_observations_isolated_across_workspaces(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])

    _create_observation(client, ws_a["id"], actor_headers(actor_ref), unique, permission_status="allowed")

    rows_b = client.get(f"/workspaces/{ws_b['id']}/market-observations", headers=actor_headers(actor_ref)).json()
    assert rows_b == []
    current_b = client.get(
        f"/workspaces/{ws_b['id']}/market-observations/current", headers=actor_headers(actor_ref)
    ).json()
    assert current_b["observations"] == []


def test_idempotency_key_retry_returns_same_row_not_a_duplicate(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    body = {
        "source": f"idem-{unique}",
        "collected_at": "2026-08-01T00:00:00Z",
        "idempotency_key": f"key-{unique}",
    }
    first = client.post(f"/workspaces/{ws_id}/market-observations", json=body, headers=headers).json()
    second = client.post(f"/workspaces/{ws_id}/market-observations", json=body, headers=headers).json()
    assert first["id"] == second["id"]

    rows = client.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    assert sum(1 for r in rows if r["idempotency_key"] == f"key-{unique}") == 1


def test_idempotency_key_does_not_collide_across_workspaces(client, unique):
    user = create_user(client, unique)
    actor_ref = user["external_ref"]
    ws_a = create_workspace(client, unique + "-a", user["id"])
    ws_b = create_workspace(client, unique + "-b", user["id"])
    headers = actor_headers(actor_ref)
    shared_key = f"shared-key-{unique}"

    obs_a = client.post(
        f"/workspaces/{ws_a['id']}/market-observations",
        json={"source": "a", "collected_at": "2026-08-01T00:00:00Z", "idempotency_key": shared_key},
        headers=headers,
    ).json()
    obs_b = client.post(
        f"/workspaces/{ws_b['id']}/market-observations",
        json={"source": "b", "collected_at": "2026-08-01T00:00:00Z", "idempotency_key": shared_key},
        headers=headers,
    ).json()
    assert obs_a["id"] != obs_b["id"]


def test_concurrent_create_with_same_idempotency_key_never_5xxs_and_persists_exactly_one_row(
    bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    N = 8
    key = f"concurrent-{unique}"

    def create(_i):
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
            return c.post(
                f"/workspaces/{ws_id}/market-observations",
                json={"source": f"race-{unique}", "collected_at": "2026-08-01T00:00:00Z", "idempotency_key": key},
                headers=headers,
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=N) as pool:
        results = list(pool.map(create, range(N)))

    statuses = [r.status_code for r in results]
    assert all(s == 200 for s in statuses), f"expected all {N} racing creates to succeed, got {statuses}"
    ids = {r.json()["id"] for r in results}
    assert len(ids) == 1, f"expected exactly one row to win the race, got {len(ids)} distinct ids"

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        rows = c.get(f"/workspaces/{ws_id}/market-observations", headers=headers).json()
    assert sum(1 for r in rows if r["idempotency_key"] == key) == 1


def test_permission_confirmation_updates_status_and_records_confirmer(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    actor_ref = bootstrapped["actor_ref"]
    obs = _create_observation(client, ws_id, headers, unique)
    assert obs["permission_status"] == "unknown"

    r = client.post(
        f"/workspaces/{ws_id}/market-observations/{obs['id']}/permission",
        json={
            "permission_status": "allowed",
            "confirmed_by": actor_ref,
            "permission_basis": {"note": "Founder confirmed via screenshot"},
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    confirmed = r.json()
    assert confirmed["permission_status"] == "allowed"
    assert confirmed["permission_confirmed_by"] == actor_ref
    assert confirmed["permission_confirmed_at"] is not None

    current = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    assert any(o["id"] == obs["id"] for o in current["observations"])


def test_confirm_permission_rejects_nonexistent_and_cross_workspace_observation(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    r = client.post(
        f"/workspaces/{ws_id}/market-observations/00000000-0000-0000-0000-000000000000/permission",
        json={"permission_status": "allowed", "confirmed_by": bootstrapped["actor_ref"]},
        headers=headers,
    )
    assert r.status_code == 404

    obs = _create_observation(client, ws_id, headers, unique)
    other_user = create_user(client, unique + "-other")
    other_ws = create_workspace(client, unique + "-other", other_user["id"])
    r = client.post(
        f"/workspaces/{other_ws['id']}/market-observations/{obs['id']}/permission",
        json={"permission_status": "allowed", "confirmed_by": other_user["external_ref"]},
        headers=actor_headers(other_user["external_ref"]),
    )
    assert r.status_code == 404


def test_permission_confirmation_partial_update_preserves_omitted_fields(client, bootstrapped, unique):
    """A second confirm call that only corrects confirmed_by (say, a typo)
    must not silently wipe a previously recorded usage_limits/
    permission_basis back to null -- that would make a 'restricted'
    observation indistinguishable from unrestricted-allowed."""

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    actor_ref = bootstrapped["actor_ref"]
    obs = _create_observation(client, ws_id, headers, unique)

    first = client.post(
        f"/workspaces/{ws_id}/market-observations/{obs['id']}/permission",
        json={
            "permission_status": "restricted",
            "confirmed_by": actor_ref,
            "usage_limits": {"no_publish": True},
            "permission_basis": {"note": "internal reference only"},
        },
        headers=headers,
    ).json()
    assert first["usage_limits"] == {"no_publish": True}

    # re-confirm without repeating usage_limits/permission_basis
    second = client.post(
        f"/workspaces/{ws_id}/market-observations/{obs['id']}/permission",
        json={"permission_status": "restricted", "confirmed_by": actor_ref},
        headers=headers,
    ).json()
    assert second["usage_limits"] == {"no_publish": True}, "omitted field must be preserved, not wiped"
    assert second["permission_basis"] == {"note": "internal reference only"}

    current = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    match = next(o for o in current["observations"] if o["id"] == obs["id"])
    assert match["usage_limits"] == {"no_publish": True}, "restricted limits must travel with the projection"

    # explicitly clearing IS honored (distinguishes 'omitted' from 'set to null')
    third = client.post(
        f"/workspaces/{ws_id}/market-observations/{obs['id']}/permission",
        json={"permission_status": "restricted", "confirmed_by": actor_ref, "usage_limits": None},
        headers=headers,
    ).json()
    assert third["usage_limits"] is None


def test_idempotency_key_does_not_collide_across_different_accounts_in_same_workspace(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    account_a = bootstrapped["account"]["id"]
    account_b = create_account(client, ws_id, f"{unique}-b", bootstrapped["actor_ref"])["id"]
    shared_key = f"acct-shared-key-{unique}"

    obs_a = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": "a",
            "collected_at": "2026-08-01T00:00:00Z",
            "account_id": account_a,
            "idempotency_key": shared_key,
        },
        headers=headers,
    ).json()
    obs_b = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": "b",
            "collected_at": "2026-08-01T00:00:00Z",
            "account_id": account_b,
            "idempotency_key": shared_key,
        },
        headers=headers,
    ).json()
    assert obs_a["id"] != obs_b["id"], (
        "two different accounts sharing an idempotency_key string must never collide onto the same row"
    )

    # but a genuine retry for the SAME account still dedupes
    retry = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": "a-retry",
            "collected_at": "2026-08-01T00:00:00Z",
            "account_id": account_a,
            "idempotency_key": shared_key,
        },
        headers=headers,
    ).json()
    assert retry["id"] == obs_a["id"]


def test_workspace_wide_idempotency_key_still_dedupes_with_no_account_set(client, bootstrapped, unique):
    """NULLS NOT DISTINCT: two workspace-wide (no account_id) creates with
    the same key must dedupe as a retry, not silently create duplicates --
    plain NULL-distinct SQL semantics would otherwise treat every
    account_id=NULL row as unique regardless of idempotency_key."""

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    key = f"no-account-key-{unique}"
    body = {"source": "x", "collected_at": "2026-08-01T00:00:00Z", "idempotency_key": key}

    first = client.post(f"/workspaces/{ws_id}/market-observations", json=body, headers=headers).json()
    second = client.post(f"/workspaces/{ws_id}/market-observations", json=body, headers=headers).json()
    assert first["id"] == second["id"]


def test_applicable_period_validates_mixed_naive_and_aware_datetimes_without_500(
    client, bootstrapped, unique
):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    # naive start, aware end, valid order -- must succeed, not 500
    r = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"period-ok-{unique}",
            "collected_at": "2026-08-01T00:00:00Z",
            "applicable_period_start": "2026-01-01T00:00:00",
            "applicable_period_end": "2026-02-01T00:00:00Z",
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text

    # naive start after aware end -- must still be caught as a clean 422
    r = client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"period-bad-{unique}",
            "collected_at": "2026-08-01T00:00:00Z",
            "applicable_period_start": "2026-03-01T00:00:00",
            "applicable_period_end": "2026-02-01T00:00:00Z",
        },
        headers=headers,
    )
    assert r.status_code == 422


def test_at_parameter_evaluates_usability_as_of_a_reference_time(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    _create_observation(
        client,
        ws_id,
        headers,
        unique,
        permission_status="allowed",
        applicable_period_start="2030-01-01T00:00:00Z",
        applicable_period_end="2030-02-01T00:00:00Z",
    )

    now_result = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers).json()
    assert now_result["observations"] == [], "not yet applicable as of 'now'"

    future_result = client.get(
        f"/workspaces/{ws_id}/market-observations/current",
        params={"at": "2030-01-15T00:00:00Z"},
        headers=headers,
    ).json()
    assert len(future_result["observations"]) == 1, "must be usable as of a reference time inside its period"
