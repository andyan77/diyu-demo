def _create_material(client, ws_id, unique, headers):
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
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def _create_version_with_material(client, ws_id, artifact_id, content_hash, material_id, headers):
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={
            "idempotency_key": content_hash,
            "content_hash": content_hash,
            "content_ref": "s3://x",
            "material_ids": [material_id],
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_withdrawal_invalidates_only_unpublished_dependents(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    material = _create_material(client, ws_id, unique, headers)

    unpublished = _create_version_with_material(
        client, ws_id, artifact_id, f"h-unpub-{unique}", material["id"], headers
    )
    published = _create_version_with_material(
        client, ws_id, artifact_id, f"h-pub-{unique}", material["id"], headers
    )
    client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{published['id']}/promote",
        json={},
        headers=headers,
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
        headers=headers,
    )
    assert pub.status_code == 200, pub.text

    r = client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)
    assert r.status_code == 200
    result = r.json()
    assert unpublished["id"] in result["invalidated_version_ids"]
    assert published["id"] not in result["invalidated_version_ids"], (
        "a published version must never be invalidated by a later material withdrawal"
    )

    all_versions = {
        v["id"]: v
        for v in client.get(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions", headers=headers
        ).json()
    }
    assert all_versions[unpublished["id"]]["invalidated_at"] is not None
    assert all_versions[published["id"]]["invalidated_at"] is None


def test_withdrawal_is_idempotent(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    material = _create_material(client, ws_id, unique, headers)

    r1 = client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)
    assert r1.status_code == 200
    assert r1.json()["already_withdrawn"] is False

    r2 = client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["already_withdrawn"] is True
    assert r2.json()["withdrawn_at"] == r1.json()["withdrawn_at"], (
        "retrying withdrawal must not move the withdrawal timestamp"
    )


def test_withdrawn_material_content_not_servable(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    material = _create_material(client, ws_id, unique, headers)

    client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)
    r = client.get(f"/workspaces/{ws_id}/materials/{material['id']}", headers=headers)
    assert r.status_code == 200
    assert r.json()["content_ref"] is None, "withdrawn material content must not be returned"


def test_unaffected_artifact_not_touched_by_unrelated_withdrawal(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    unrelated_material = _create_material(client, ws_id, unique, headers)

    version = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"idempotency_key": f"v-{unique}", "content_hash": f"h-{unique}", "content_ref": "s3://x"},
        headers=headers,
    ).json()

    client.post(f"/workspaces/{ws_id}/materials/{unrelated_material['id']}/withdraw", headers=headers)

    refreshed = {
        v["id"]: v
        for v in client.get(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions", headers=headers
        ).json()
    }
    assert refreshed[version["id"]]["invalidated_at"] is None


def test_withdrawn_material_cannot_be_attached_to_a_new_version(client, bootstrapped, unique):
    """Closes the withdrawal-bypass channel: once a material is withdrawn,
    it must not be usable as a dependency for a NEW version either -- not
    just excluded from cascading invalidation of versions that already
    referenced it.
    """

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    material = _create_material(client, ws_id, unique, headers)

    client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)

    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={
            "idempotency_key": f"post-withdraw-{unique}",
            "content_hash": f"h-{unique}",
            "content_ref": "s3://x",
            "material_ids": [material["id"]],
        },
        headers=headers,
    )
    assert r.status_code == 409


def test_withdraw_and_publish_race_never_invalidates_a_published_version(client, bootstrapped, unique):
    """Regression for the confirmed race: withdraw_material used to
    SELECT-then-write which publish_instances existed, leaving a window
    where a concurrent register_publish_instance could commit between the
    SELECT and the invalidation write. This drives the two calls back to
    back against the same dependent version and asserts the invariant
    (never both published AND invalidated) rather than trying to hit the
    exact race window, which the atomic UPDATE...WHERE NOT EXISTS in
    withdraw_material now closes by construction.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    material = _create_material(client, ws_id, unique, headers)
    version = _create_version_with_material(
        client, ws_id, artifact_id, f"h-race-{unique}", material["id"], headers
    )
    client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{version['id']}/promote",
        json={},
        headers=headers,
    )
    client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-race-{unique}",
            "content_version_id": version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
        headers=headers,
    )

    client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)

    refreshed = client.get(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/current", headers=headers
    ).json()
    assert refreshed["id"] == version["id"]
    assert refreshed["invalidated_at"] is None, (
        "a published version must never end up invalidated, no matter how withdraw and publish interleave"
    )


def test_withdraw_and_publish_race_never_invalidates_a_published_version_concurrent(
    client, bootstrapped, unique
):
    """The sequential version above proves the happy-path ordering; this
    drives register_publish_instance and withdraw_material at the literal
    SAME content_version from two threads at once, repeated across many
    trials, because the actual defect this regresses (a stale read past a
    SQLAlchemy identity-map cache hit past a real Postgres row lock) only
    ever showed up under genuine concurrent load in testing -- never on a
    single sequential run.
    """

    import concurrent.futures
    import uuid as uuid_mod

    import httpx

    from tests.conftest import BASE_URL

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    def hit(method, path, body):
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as cc:
            return getattr(cc, method)(path, json=body, headers=headers)

    TRIALS = 20
    for trial in range(TRIALS):
        material = _create_material(client, ws_id, f"{unique}-{trial}", headers)
        version = _create_version_with_material(
            client, ws_id, artifact_id, f"h-crace-{unique}-{trial}", material["id"], headers
        )

        def do_publish():
            return hit(
                "post",
                f"/workspaces/{ws_id}/publish-instances",
                {
                    "idempotency_key": f"crace-{unique}-{trial}-{uuid_mod.uuid4().hex[:8]}",
                    "content_version_id": version["id"],
                    "account_id": account_id,
                    "platform": "test-platform",
                    "published_at": "2026-08-25T00:00:00Z",
                },
            )

        def do_withdraw():
            return hit("post", f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            f_pub = pool.submit(do_publish)
            f_wd = pool.submit(do_withdraw)
            r_pub, r_wd = f_pub.result(), f_wd.result()

        assert r_pub.status_code in (200, 409), f"unexpected publish status: {r_pub.status_code} {r_pub.text}"
        assert r_wd.status_code == 200, f"unexpected withdraw status: {r_wd.status_code} {r_wd.text}"

        published = client.get(
            f"/workspaces/{ws_id}/content-versions/{version['id']}/publish-instances", headers=headers
        ).json()
        refreshed = client.get(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions", headers=headers
        ).json()
        by_id = {v["id"]: v for v in refreshed}

        assert not (published and by_id[version["id"]]["invalidated_at"] is not None), (
            f"trial {trial}: version is both published ({len(published)} instance) and invalidated -- "
            "a published version must never end up invalidated regardless of thread interleaving"
        )
