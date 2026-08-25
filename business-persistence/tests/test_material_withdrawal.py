def _create_material(client, ws_id, unique):
    r = client.post(
        f"/workspaces/{ws_id}/materials",
        json={
            "source": "user-upload",
            "owner_ref": "user:founder",
            "analysis_authorized": True,
            "generation_authorized": True,
            "publish_authorized": True,
            "content_ref": f"s3://material-{unique}",
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


def _create_version_with_material(client, ws_id, artifact_id, content_hash, material_id):
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"content_hash": content_hash, "content_ref": "s3://x", "material_ids": [material_id]},
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_withdrawal_invalidates_only_unpublished_dependents(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]

    material = _create_material(client, ws_id, unique)

    unpublished = _create_version_with_material(
        client, ws_id, artifact_id, f"h-unpub-{unique}", material["id"]
    )
    published = _create_version_with_material(
        client, ws_id, artifact_id, f"h-pub-{unique}", material["id"]
    )
    client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{published['id']}/promote",
        json={"promoted_by": "user:founder"},
    )
    pub = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-{unique}",
            "content_version_id": published["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
    )
    assert pub.status_code == 200, pub.text

    r = client.post(
        f"/workspaces/{ws_id}/materials/{material['id']}/withdraw",
        json={"withdrawn_by": "user:founder"},
    )
    assert r.status_code == 200
    result = r.json()
    assert unpublished["id"] in result["invalidated_version_ids"]
    assert published["id"] not in result["invalidated_version_ids"], (
        "a published version must never be invalidated by a later material withdrawal"
    )

    all_versions = {
        v["id"]: v
        for v in client.get(f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions").json()
    }
    assert all_versions[unpublished["id"]]["invalidated_at"] is not None
    assert all_versions[published["id"]]["invalidated_at"] is None


def test_withdrawal_is_idempotent(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    material = _create_material(client, ws_id, unique)

    r1 = client.post(
        f"/workspaces/{ws_id}/materials/{material['id']}/withdraw",
        json={"withdrawn_by": "user:founder"},
    )
    assert r1.status_code == 200
    assert r1.json()["already_withdrawn"] is False

    r2 = client.post(
        f"/workspaces/{ws_id}/materials/{material['id']}/withdraw",
        json={"withdrawn_by": "user:someone_else"},
    )
    assert r2.status_code == 200
    assert r2.json()["already_withdrawn"] is True
    assert r2.json()["withdrawn_at"] == r1.json()["withdrawn_at"], (
        "retrying withdrawal must not move the withdrawal timestamp"
    )


def test_withdrawn_material_content_not_servable(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    material = _create_material(client, ws_id, unique)

    client.post(
        f"/workspaces/{ws_id}/materials/{material['id']}/withdraw",
        json={"withdrawn_by": "user:founder"},
    )
    r = client.get(f"/workspaces/{ws_id}/materials/{material['id']}")
    assert r.status_code == 200
    assert r.json()["content_ref"] is None, "withdrawn material content must not be returned"


def test_unaffected_artifact_not_touched_by_unrelated_withdrawal(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    unrelated_material = _create_material(client, ws_id, unique)

    version = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"content_hash": f"h-{unique}", "content_ref": "s3://x"},
    ).json()

    client.post(
        f"/workspaces/{ws_id}/materials/{unrelated_material['id']}/withdraw",
        json={"withdrawn_by": "user:founder"},
    )

    refreshed = {
        v["id"]: v
        for v in client.get(f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions").json()
    }
    assert refreshed[version["id"]]["invalidated_at"] is None
