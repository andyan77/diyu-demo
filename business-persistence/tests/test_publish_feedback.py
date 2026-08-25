import uuid


def _version(client, ws_id, artifact_id, unique):
    r = client.post(
        f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
        json={"content_hash": f"h-{unique}", "content_ref": "s3://x"},
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
    )
    assert r.status_code == 404


def test_feedback_requires_real_publish_instance(client):
    r = client.post(
        f"/workspaces/{uuid.uuid4()}/feedback",
        json={
            "idempotency_key": "no-such-instance",
            "publish_instance_id": str(uuid.uuid4()),
            "kind": "observation",
        },
    )
    assert r.status_code == 404


def test_feedback_kind_is_validated(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]
    version = _version(client, ws_id, artifact_id, unique)
    pub = client.post(
        f"/workspaces/{ws_id}/publish-instances",
        json={
            "idempotency_key": f"pub-{unique}",
            "content_version_id": version["id"],
            "account_id": account_id,
            "platform": "test-platform",
            "published_at": "2026-08-25T00:00:00Z",
        },
    ).json()

    bad = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"fb-bad-{unique}",
            "publish_instance_id": pub["id"],
            "kind": "not_a_real_kind",
        },
    )
    assert bad.status_code == 422


def test_evidence_isolation_flags_round_trip(client, bootstrapped, unique):
    """Real, test, and simulated publishes/feedback are structurally
    distinguishable, not merged by a shared string field a query could
    forget to filter on.
    """

    ws_id = bootstrapped["workspace"]["id"]
    account_id = bootstrapped["account"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]

    real_version = _version(client, ws_id, artifact_id, unique + "-real")
    test_version = _version(client, ws_id, artifact_id, unique + "-test")

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
    ).json()
    fb_sim = client.post(
        f"/workspaces/{ws_id}/feedback",
        json={
            "idempotency_key": f"fb-sim-{unique}",
            "publish_instance_id": test_pub["id"],
            "kind": "observation",
            "is_simulated": True,
        },
    ).json()

    assert fb_real["is_simulated"] is False
    assert fb_sim["is_simulated"] is True

    real_feedback_list = client.get(
        f"/workspaces/{ws_id}/publish-instances/{real_pub['id']}/feedback"
    ).json()
    assert all(f["is_simulated"] is False for f in real_feedback_list), (
        "feedback attached to a real publish instance must never carry simulated data"
    )
