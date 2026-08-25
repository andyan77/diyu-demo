import concurrent.futures

import httpx

from tests.conftest import BASE_URL


def test_concurrent_promotion_of_different_versions_never_leaves_two_current(bootstrapped, unique):
    """Two callers race to promote two DIFFERENT candidate versions of the
    same artifact at (as close to) the same instant. This is a genuine
    mutual-exclusion race, not two independent writes -- both versions are
    competing for the single is_current slot on that artifact. Either both
    happen to succeed (if they get serialized far enough apart) or the
    loser gets an honest 409 to retry; what must never happen is an opaque
    5xx, or the database ending up with two current rows, or zero.
    """

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        v1 = client.post(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
            json={"content_hash": f"c1-{unique}", "content_ref": "s3://x"},
        ).json()
        v2 = client.post(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
            json={"content_hash": f"c2-{unique}", "content_ref": "s3://x"},
        ).json()

    def promote(version_id, actor):
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
            return c.post(
                f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{version_id}/promote",
                json={"promoted_by": actor},
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(promote, v1["id"], "user:racer-1")
        f2 = pool.submit(promote, v2["id"], "user:racer-2")
        r1 = f1.result()
        r2 = f2.result()

    statuses = sorted([r1.status_code, r2.status_code])
    assert statuses in ([200, 200], [200, 409]), (
        f"expected a clean win plus either a clean second win or an honest 409 loser, got {statuses}"
    )
    for r in (r1, r2):
        if r.status_code not in (200, 409):
            raise AssertionError(f"unexpected status {r.status_code}: {r.text}")

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        all_versions = client.get(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions"
        ).json()

    current_ones = [v for v in all_versions if v["is_current"]]
    assert len(current_ones) == 1, (
        f"exactly one version must be current after concurrent promotions, got {len(current_ones)}"
    )


def test_concurrent_promotion_of_the_same_version_is_not_double_charged(bootstrapped, unique):
    """Two callers race to promote the SAME candidate version at once.

    Exactly one of them performs the real state transition; the other must
    get an honest, recoverable signal -- either a clean 200 no-op (if it
    happens to observe the row only after the winner's commit) or a 409
    conflict (if its UPDATE raced against the winner's in-flight
    transaction and matched zero rows). What must NEVER happen is both
    silently "succeeding" while the underlying row gets bumped twice, or
    either racer getting an opaque 5xx. A 409 loser is expected to retry
    and then observe the already-promoted state cleanly.
    """

    ws_id = bootstrapped["workspace"]["id"]
    artifact_id = bootstrapped["artifact"]["id"]

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        v1 = client.post(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions",
            json={"content_hash": f"same-{unique}", "content_ref": "s3://x"},
        ).json()

    def promote(actor):
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
            return c.post(
                f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/{v1['id']}/promote",
                json={"promoted_by": actor},
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(promote, "user:racer-a")
        f2 = pool.submit(promote, "user:racer-b")
        r1 = f1.result()
        r2 = f2.result()

    statuses = sorted([r1.status_code, r2.status_code])
    assert statuses in ([200, 200], [200, 409]), (
        f"expected exactly one clean win and an honest no-op-or-conflict loser, got {statuses}"
    )

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        current = client.get(
            f"/workspaces/{ws_id}/artifacts/{artifact_id}/versions/current"
        ).json()
    assert current["id"] == v1["id"]
    assert current["row_version"] == v1["row_version"] + 1, (
        "racing to promote the same row must bump row_version exactly once, not twice"
    )

    # the loser retrying now must see a clean idempotent no-op, never another conflict
    retry = promote("user:racer-a-retry")
    assert retry.status_code == 200
    assert retry.json()["row_version"] == current["row_version"]
