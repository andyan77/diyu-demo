import uuid

from tests.conftest import actor_headers


def _create_version(client, ws_id, artifact_id, content_hash, headers, key=None):
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"idempotency_key": key or content_hash, "content_hash": content_hash, "content_ref": "s3://x"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_promotion_is_atomic_and_history_is_preserved(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    v1 = _create_version(client, ws_id, artifact_id, f"h1-{unique}", headers)
    v2 = _create_version(client, ws_id, artifact_id, f"h2-{unique}", headers)

    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["is_current"] is True
    assert r.json()["promoted_by"] == bootstrapped["actor_ref"], (
        "promoted_by must always be the authenticated actor, never a free-text body field"
    )

    current = client.get(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/current", headers=headers
    ).json()
    assert current["id"] == v1["id"]

    # promote v2 -- v1 must flip off, v2 flips on, both rows still readable
    r2 = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v2['id']}/promote",
        json={},
        headers=headers,
    )
    assert r2.status_code == 200

    all_versions = client.get(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions", headers=headers
    ).json()
    by_id = {v["id"]: v for v in all_versions}
    assert by_id[v1["id"]]["is_current"] is False
    assert by_id[v1["id"]]["superseded_at"] is not None
    assert by_id[v2["id"]]["is_current"] is True

    current_2 = client.get(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/current", headers=headers
    ).json()
    assert current_2["id"] == v2["id"]


def test_promoting_already_current_version_is_a_noop(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    v1 = _create_version(client, ws_id, artifact_id, f"h-{unique}", headers)

    r1 = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={},
        headers=headers,
    )
    assert r1.status_code == 200
    row_version_after_first = r1.json()["row_version"]

    r2 = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={},
        headers=headers,
    )
    assert r2.status_code == 200
    assert r2.json()["row_version"] == row_version_after_first, "no-op must not bump row_version again"


def test_promotion_rejects_stale_expected_row_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    v1 = _create_version(client, ws_id, artifact_id, f"hA-{unique}", headers)
    v2 = _create_version(client, ws_id, artifact_id, f"hB-{unique}", headers)

    # promote v1 first so it has a real row_version to go stale
    client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
        json={},
        headers=headers,
    )

    stale_row_version = v2["row_version"]  # v2 hasn't actually changed, but pretend caller read it long ago
    r_ok = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v2['id']}/promote",
        json={"expected_row_version": stale_row_version},
        headers=headers,
    )
    assert r_ok.status_code == 200, "correct expected_row_version must succeed"

    v3 = _create_version(client, ws_id, artifact_id, f"hC-{unique}", headers)
    r_conflict = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v3['id']}/promote",
        json={"expected_row_version": 999},
        headers=headers,
    )
    assert r_conflict.status_code == 409, "wrong expected_row_version must be rejected, never silently applied"


def test_promote_unknown_version_is_404(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{uuid.uuid4()}/promote",
        json={},
        headers=bootstrapped["headers"],
    )
    assert r.status_code == 404


def test_version_creation_retry_returns_same_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    key = f"retry-{unique}"

    v1 = _create_version(client, ws_id, artifact_id, f"h-{unique}", headers, key=key)
    v2 = _create_version(client, ws_id, artifact_id, f"h-{unique}", headers, key=key)
    assert v1["id"] == v2["id"], "retrying create_version with the same idempotency_key must not create a second candidate"


def test_create_version_rejects_material_from_another_workspace(client, bootstrapped, unique):
    """A version must not be able to declare a dependency on a material it
    cannot actually see -- a material_id from a different workspace is
    exactly as invalid as one that doesn't exist at all.
    """

    from tests.conftest import create_user, create_workspace

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    other_user = create_user(client, unique + "-other")
    other_ws = create_workspace(client, unique + "-other", other_user["id"])
    foreign_material = client.post(
        f"/workspaces/{other_ws['id']}/materials",
        json={"source": "foreign", "content_ref": "s3://foreign"},
        headers=actor_headers(other_user["external_ref"]),
    ).json()

    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={
            "idempotency_key": f"cross-ws-{unique}",
            "content_hash": f"h-{unique}",
            "content_ref": "s3://x",
            "material_ids": [foreign_material["id"]],
        },
        headers=headers,
    )
    assert r.status_code == 404


def test_promote_requires_membership_not_viewer_role(client, bootstrapped):
    """This only proves the endpoint is auth-gated at all; a dedicated
    viewer-role rejection is exercised once real member-invite tooling
    exists to create a viewer membership without going around the API.
    """

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{uuid.uuid4()}/promote",
        json={},
    )
    assert r.status_code == 401
