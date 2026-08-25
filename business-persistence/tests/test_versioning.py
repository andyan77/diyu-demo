def _create_version(client, ws_id, artifact_id, content_hash):
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"content_hash": content_hash, "content_ref": "s3://x"},
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_promotion_is_atomic_and_history_is_preserved(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]

    v1 = _create_version(client, ws_id, artifact_id, f"h1-{unique}")
    v2 = _create_version(client, ws_id, artifact_id, f"h2-{unique}")

    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={"promoted_by": "user:founder"},
    )
    assert r.status_code == 200
    assert r.json()["is_current"] is True

    current = client.get(f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/current").json()
    assert current["id"] == v1["id"]

    # promote v2 -- v1 must flip off, v2 flips on, both rows still readable
    r2 = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v2['id']}/promote",
        json={"promoted_by": "user:founder"},
    )
    assert r2.status_code == 200

    all_versions = client.get(f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions").json()
    by_id = {v["id"]: v for v in all_versions}
    assert by_id[v1["id"]]["is_current"] is False
    assert by_id[v1["id"]]["superseded_at"] is not None
    assert by_id[v2["id"]]["is_current"] is True

    current_2 = client.get(f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/current").json()
    assert current_2["id"] == v2["id"]


def test_promoting_already_current_version_is_a_noop(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    v1 = _create_version(client, ws_id, artifact_id, f"h-{unique}")

    r1 = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={"promoted_by": "user:founder"},
    )
    assert r1.status_code == 200
    row_version_after_first = r1.json()["row_version"]

    r2 = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={"promoted_by": "user:founder"},
    )
    assert r2.status_code == 200
    assert r2.json()["row_version"] == row_version_after_first, "no-op must not bump row_version again"


def test_promotion_rejects_stale_expected_row_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    v1 = _create_version(client, ws_id, artifact_id, f"hA-{unique}")
    v2 = _create_version(client, ws_id, artifact_id, f"hB-{unique}")

    # promote v1 first so it has a real row_version to go stale
    client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={"promoted_by": "user:a"},
    )

    stale_row_version = v2["row_version"]  # v2 hasn't actually changed, but pretend caller read it long ago
    r_ok = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v2['id']}/promote",
        json={"promoted_by": "user:b", "expected_row_version": stale_row_version},
    )
    assert r_ok.status_code == 200, "correct expected_row_version must succeed"

    v3 = _create_version(client, ws_id, artifact_id, f"hC-{unique}")
    r_conflict = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v3['id']}/promote",
        json={"promoted_by": "user:c", "expected_row_version": 999},
    )
    assert r_conflict.status_code == 409, "wrong expected_row_version must be rejected, never silently applied"


def test_promote_unknown_version_is_404(client, bootstrapped):
    import uuid

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{uuid.uuid4()}/promote",
        json={"promoted_by": "user:founder"},
    )
    assert r.status_code == 404
