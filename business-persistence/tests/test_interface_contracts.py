"""M2-AC-15: pins, against the EXISTING API surface, that M2 stays inside
its own responsibility and does not secretly do M1's (dialogue), M3's
(operational judgment), or M4's (content generation) job. These are
contract tests, not feature tests -- each one is written to actually FAIL
if the boundary were crossed, not just to exercise a happy path.
"""

DIALOGUE_SHAPED_KEYS = {
    "reply",
    "response_text",
    "message",
    "assistant_message",
    "next_question",
    "chat_response",
    "suggestion_text",
}


def _assert_no_dialogue_shape(obj, path="$"):
    """Recursively asserts a response has no natural-language/dialogue-
    shaped field anywhere -- M2's job is to hand back the row, not to
    address the user. A real M1 boundary violation would add exactly this
    kind of key to some projection response.
    """

    if isinstance(obj, dict):
        for key, value in obj.items():
            assert key not in DIALOGUE_SHAPED_KEYS, (
                f"{path}.{key} looks like a dialogue-shaped field -- M2 must never generate what M1 "
                "is responsible for producing"
            )
            _assert_no_dialogue_shape(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _assert_no_dialogue_shape(item, f"{path}[{i}]")


def test_m1_boundary_projection_endpoints_return_plain_data_no_dialogue_fields(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    task_id = bootstrapped["task"]["id"]
    headers = bootstrapped["headers"]

    # Populate real content first -- checking these endpoints while every
    # field is still null/empty would pass even if M1's boundary were
    # crossed, since there'd be almost no payload for the recursive check
    # to actually inspect.
    client.put(
        f"/workspaces/{ws_id}/tasks/{task_id}/run-state",
        json={"last_success_step": "snapshot_saved", "side_effects": {"note": "已经存好了"}},
        headers=headers,
    )
    run_state_resp = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/run-state", headers=headers)
    assert run_state_resp.status_code == 200
    _assert_no_dialogue_shape(run_state_resp.json())

    cycle_resp = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"contract-cycle-{unique}",
            "account_id": account_id,
            "label": f"contract-cycle-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
            "baseline_capacity": 10,
            "expected_publish_count": 12,
        },
        headers=headers,
    )
    assert cycle_resp.status_code == 200
    current_cycle_resp = client.get(
        f"/workspaces/{ws_id}/accounts/{account_id}/cycles/current", headers=headers
    )
    assert current_cycle_resp.status_code == 200
    _assert_no_dialogue_shape(current_cycle_resp.json())

    client.post(
        f"/workspaces/{ws_id}/tasks/{task_id}/snapshots",
        json={
            "idempotency_key": f"contract-snapshot-{unique}",
            "payload": {"note": "帮我看看这周能不能按时发"},
            "info_nature": "fact",
        },
        headers=headers,
    )
    projection_resp = client.get(f"/workspaces/{ws_id}/tasks/{task_id}/projection", headers=headers)
    assert projection_resp.status_code == 200
    projection = projection_resp.json()
    assert projection["latest_snapshot"]["payload"]["note"] == "帮我看看这周能不能按时发", (
        "sanity check that this test is actually inspecting a populated, non-trivial payload"
    )
    _assert_no_dialogue_shape(projection)


def test_m3_boundary_m2_stores_playbook_and_cycle_values_verbatim_without_judging_them(
    client, bootstrapped, unique
):
    """M2 must never evaluate whether a playbook is good or a cycle's
    numbers make sense -- that professional judgment belongs to M3. This
    test deliberately supplies an internally-inconsistent / low-quality-
    looking value set and asserts M2 accepts and returns it byte-for-byte,
    proving M2 performs no content-based evaluation.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    headers = bootstrapped["headers"]

    # A cycle where expected_publish_count wildly exceeds both capacity
    # numbers -- a professionally dubious plan. M2 must not reject, clamp,
    # or "correct" it; it just stores what the caller (M3/user) asserted.
    cycle = client.post(
        f"/workspaces/{ws_id}/cycles",
        json={
            "idempotency_key": f"contract-judge-cycle-{unique}",
            "account_id": account_id,
            "label": f"contract-judge-cycle-{unique}",
            "start_at": "2026-08-01T00:00:00Z",
            "baseline_capacity": 5,
            "actual_capacity": 2,
            "expected_publish_count": 500,
        },
        headers=headers,
    )
    assert cycle.status_code == 200, cycle.text
    assert cycle.json()["expected_publish_count"] == 500, (
        "M2 must store an operationally implausible expected_publish_count unchanged -- "
        "judging feasibility is M3's job, not M2's"
    )

    playbook = client.post(
        f"/workspaces/{ws_id}/playbooks",
        json={
            "idempotency_key": f"contract-playbook-{unique}",
            "name": f"contract-playbook-{unique}",
            "proposed_by": "M3",
            "observation_status": "仅一次样本，效果未知，甚至可能是负面打法",
            "rationale": "故意写一个听起来很差的理由",
        },
        headers=headers,
    )
    assert playbook.status_code == 200, playbook.text
    assert playbook.json()["observation_status"] == "仅一次样本，效果未知，甚至可能是负面打法", (
        "M2 must record whatever observation_status the caller supplies verbatim, "
        "never silently reject or rewrite a playbook it judges to be weak"
    )

    openapi = client.get("/openapi.json").json()
    playbook_paths = [p for p in openapi["paths"] if "playbook" in p.lower()]
    for p in playbook_paths:
        assert "evaluate" not in p.lower() and "score" not in p.lower() and "judge" not in p.lower(), (
            f"found a playbook-judging endpoint {p} -- M2 must not decide whether a playbook is good"
        )


def test_m4_boundary_content_version_requires_preexisting_content_never_generates_it(
    client, bootstrapped, unique
):
    """M4 (Production Director / Publishing) is responsible for actually
    producing creative content. M2 must only ever accept an
    already-produced content_hash/content_ref as a fait accompli -- there
    must be no request shape or endpoint that hands M2 a brief/prompt and
    gets generated content back.
    """

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    exact_ref = f"s3://already-produced/{unique}.mp4"
    exact_hash = f"hash-preexisting-{unique}"
    version = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"idempotency_key": f"contract-version-{unique}", "content_hash": exact_hash, "content_ref": exact_ref},
        headers=headers,
    )
    assert version.status_code == 200, version.text
    body = version.json()
    assert body["content_ref"] == exact_ref and body["content_hash"] == exact_hash, (
        "content_version must echo back exactly the pre-produced reference/hash supplied -- "
        "any transformation would mean M2 is doing M4's generation work"
    )

    openapi = client.get("/openapi.json").json()
    version_create_schema = openapi["components"]["schemas"]["CreateVersionRequest"]["properties"]
    generation_shaped_fields = {"prompt", "brief", "generate", "instructions", "generation_request"}
    assert not (generation_shaped_fields & version_create_schema.keys()), (
        "CreateVersionRequest must never grow a prompt/brief/generation field -- "
        "that would mean M2's create_version is doing M4's content-generation job"
    )

    for p, methods in openapi["paths"].items():
        assert "generate" not in p.lower(), f"found a content-generation-shaped endpoint path: {p} ({list(methods)})"


def test_m3_m4_boundary_market_observation_projection_is_a_plain_minimal_projection(
    client, bootstrapped, unique
):
    """M2 post-DONE Rebase v1.2 R-04: M2 only saves and projects market
    observations -- it must never interpret them (no causal/dialogue-shaped
    field) and it must never emit a fabricated competitive conclusion (no
    scarcity/uniqueness/"already avoided homogeneity" claim), whether the
    projection is empty or populated.
    """

    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    empty = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers)
    assert empty.status_code == 200
    _assert_no_dialogue_shape(empty.json())

    client.post(
        f"/workspaces/{ws_id}/market-observations",
        json={
            "source": f"contract-obs-{unique}",
            "collected_at": "2026-08-01T00:00:00Z",
            "permission_status": "allowed",
            "mechanism_summary": "对照组数据仅一次样本，结论未知",
        },
        headers=headers,
    )
    populated = client.get(f"/workspaces/{ws_id}/market-observations/current", headers=headers)
    assert populated.status_code == 200
    body = populated.json()
    assert body["observations"], "sanity check that this test actually inspects a populated payload"
    _assert_no_dialogue_shape(body)
