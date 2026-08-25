import uuid


def _version(client, ws_id, artifact_id, unique, headers):
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"idempotency_key": f"v-{unique}", "content_hash": f"h-{unique}", "content_ref": "s3://x"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_publish_requires_real_content_version_in_workspace(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    r = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": "no-such-version",
            "content_version_id": str(uuid.uuid4()),
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
        headers=bootstrapped["headers"],
    )
    assert r.status_code == 404


def test_feedback_requires_real_publish_instance(client, bootstrapped):
    ws_id = bootstrapped["workspace"]["id"]
    r = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": "no-such-instance",
            "publish_instance_id": str(uuid.uuid4()),
            "kind": "observation",
        },
        headers=bootstrapped["headers"],
    )
    assert r.status_code == 404


def test_feedback_kind_is_validated(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    version = _version(client, ws_id, artifact_id, unique, headers)
    pub = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-{unique}",
            "content_version_id": version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
        headers=headers,
    ).json()

    bad = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"fb-bad-{unique}",
            "publish_instance_id": pub["id"],
            "kind": "not_a_real_kind",
        },
        headers=headers,
    )
    assert bad.status_code == 422


def test_feedback_requires_exactly_one_of_publish_instance_or_content_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    version = _version(client, ws_id, artifact_id, unique, headers)
    pub = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-{unique}",
            "content_version_id": version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
        headers=headers,
    ).json()

    neither = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={"idempotency_key": f"fb-neither-{unique}", "kind": "observation"},
        headers=headers,
    )
    assert neither.status_code == 422

    both = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"fb-both-{unique}",
            "publish_instance_id": pub["id"],
            "content_version_id": version["id"],
            "kind": "observation",
        },
        headers=headers,
    )
    assert both.status_code == 422


def test_pre_publish_review_binds_to_content_version_not_a_publish_instance(client, bootstrapped, unique):
    """§5.6 发布前人工评价: a review written before anything is published
    yet has nowhere to attach except the candidate content_version itself.
    """

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]
    version = _version(client, ws_id, artifact_id, unique, headers)

    review = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"pre-{unique}",
            "content_version_id": version["id"],
            "kind": "interpretation",
            "is_pre_publish_review": True,
        },
        headers=headers,
    )
    assert review.status_code == 200, review.text
    assert review.json()["content_version_id"] == version["id"]
    assert review.json()["publish_instance_id"] is None

    # is_pre_publish_review must match which id was actually provided
    mismatched = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"pre-mismatch-{unique}",
            "content_version_id": version["id"],
            "kind": "interpretation",
            "is_pre_publish_review": False,
        },
        headers=headers,
    )
    assert mismatched.status_code == 422


def test_evidence_isolation_flags_round_trip(client, bootstrapped, unique):
    """Real, test, and simulated publishes/feedback are structurally
    distinguishable, not merged by a shared string field a query could
    forget to filter on.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    real_version = _version(client, ws_id, artifact_id, unique + "-real", headers)
    test_version = _version(client, ws_id, artifact_id, unique + "-test", headers)

    real_pub = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-real-{unique}",
            "content_version_id": real_version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
            "is_test": False,
            "is_simulated": False,
        },
        headers=headers,
    ).json()
    test_pub = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-test-{unique}",
            "content_version_id": test_version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
            "is_test": True,
            "is_simulated": False,
        },
        headers=headers,
    ).json()

    assert real_pub["is_test"] is False
    assert test_pub["is_test"] is True

    fb_real = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"fb-real-{unique}",
            "publish_instance_id": real_pub["id"],
            "kind": "observation",
            "is_test": False,
            "is_simulated": False,
        },
        headers=headers,
    ).json()
    fb_sim = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"fb-sim-{unique}",
            "publish_instance_id": test_pub["id"],
            "kind": "observation",
            "is_simulated": True,
        },
        headers=headers,
    ).json()

    assert fb_real["is_simulated"] is False
    assert fb_sim["is_simulated"] is True

    # the two feedback rows are attached to DIFFERENT publish instances
    # (one real, one test) -- listing feedback scoped to the real instance
    # must return only fb_real and never fb_sim, proving the scoping is a
    # real filter and not just a flag nobody reads.
    real_feedback_list = client.get(
        f"/workspaces/{ws_id}/publish-instances/{real_pub['id']}/feedback", headers=headers
    ).json()
    ids = {f["id"] for f in real_feedback_list}
    assert fb_real["id"] in ids
    assert fb_sim["id"] not in ids, (
        "feedback attached to the test/simulated publish instance must not leak into the real instance's list"
    )
    assert all(f["is_simulated"] is False for f in real_feedback_list)


def test_publish_rejects_an_invalidated_content_version(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    headers = bootstrapped["headers"]

    material = client.post(
        f"/workspaces/{ws_id}/materials",
        json={"source": "s", "content_ref": f"s3://m-{unique}"},
        headers=headers,
    ).json()
    version = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={
            "idempotency_key": f"v-{unique}",
            "content_hash": f"h-{unique}",
            "content_ref": "s3://x",
            "material_ids": [material["id"]],
        },
        headers=headers,
    ).json()
    client.post(f"/workspaces/{ws_id}/materials/{material['id']}/withdraw", headers=headers)

    r = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-invalid-{unique}",
            "content_version_id": version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
        headers=headers,
    )
    assert r.status_code == 409
