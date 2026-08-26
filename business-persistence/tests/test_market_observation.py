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
