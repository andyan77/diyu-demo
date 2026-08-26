"""M2-AC-14 (旧产物半): explicit import of real historical Matrix/Campaign/
Content Brief production artifacts from the frozen Dify Demo A/B evidence
directory (decision-chain/evidence/, outside this backend's own tree and
outside its Docker build context -- the app/test containers cannot read
those files directly).

This deliberately reuses the EXISTING create_task/create_artifact/
create_version endpoints rather than adding a new import mechanism: an old
production artifact is, structurally, exactly a ContentVersion whose
content lives in an external, already-produced, hash-addressed reference
-- which is precisely what create_version already accepts. No new schema,
table, or endpoint was needed for this half of AC-14; the discriminators
(Task.kind, Artifact.kind, ContentVersion.produced_by) are what mark these
rows as legacy imports rather than fresh production output.

The content_hash values below are the REAL sha256 of the actual files as
they exist in the repository right now (independently recomputed via
`sha256sum`, not copied from the files' own self-declared headers -- those
headers hash only the extracted business text after their own pipeline
stripped the metadata table, which is a DIFFERENT byte string from the .md
file as stored; that discrepancy is itself recorded below rather than
glossed over). Anyone can re-verify:

    sha256sum decision-chain/evidence/MATRIX_QWEN_RUN_001_RAW.md
    sha256sum decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_FINAL.md
    sha256sum decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md

These source files are frozen evidence (CLAUDE.md §6) -- this test only
ever reads their hash as a literal, pre-computed string; it never opens,
modifies, or copies them, and the import path itself never touches them.
"""

REAL_LEGACY_ARTIFACTS = [
    {
        "artifact_kind": "matrix",
        "content_ref": "decision-chain/evidence/MATRIX_QWEN_RUN_001_RAW.md",
        # real sha256 of the file as stored in the repo (computed via sha256sum)
        "content_hash": "d4fa22a005d290d812ff0817519f70e4c1b9bbbf176e4577c82f9cea3be1ee62",
        "produced_by": "legacy_ab_demo_import:qwen",
    },
    {
        "artifact_kind": "campaign",
        "content_ref": "decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_FINAL.md",
        "content_hash": "bbe0fea3a5c0644f5de3fd6a5008ee934e7f84911db5c79c06e117deaee243e4",
        # the file's own metadata table separately self-declares SHA-256 =
        # 03dfc5cac7aaba5e526a362cd69c4ed34bd88225e0f859832dfef4392b51207a for
        # the extracted business text alone (post their Final-extraction
        # step, header stripped) -- a DIFFERENT byte string from the .md
        # file as stored, which is what content_hash above actually
        # addresses. Both are real; they hash different things. Recorded
        # here rather than picking one and hiding the discrepancy.
        "produced_by": "legacy_ab_demo_import:deepseek-v4-flash:run_id=c484b072-da64-49cf-9808-18627732bf93",
    },
    {
        "artifact_kind": "content_brief",
        "content_ref": "decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md",
        "content_hash": "981cdda9834542ea44a05f3e3c837a40d6da5cbca432300e03048433cf0d53e5",
        "produced_by": "legacy_ab_demo_import:deepseek-v4-flash",
    },
]


def test_real_historical_ab_demo_artifacts_are_explicitly_importable(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]

    for spec in REAL_LEGACY_ARTIFACTS:
        task = client.post(
            f"/workspaces/{ws_id}/tasks",
            json={
                "idempotency_key": f"legacy-ab-task-{spec['artifact_kind']}-{unique}",
                "kind": "legacy_ab_demo_import",
            },
            headers=headers,
        ).json()

        artifact = client.post(
            f"/workspaces/{ws_id}/tasks/{task['id']}/artifacts",
            json={"kind": spec["artifact_kind"], "content_hash": f"artifact-{spec['artifact_kind']}-{unique}"},
            headers=headers,
        ).json()

        version = client.post(
            f"/workspaces/{ws_id}/artifacts/{artifact['id']}/versions",
            json={
                "idempotency_key": f"legacy-ab-version-{spec['artifact_kind']}-{unique}",
                "content_ref": spec["content_ref"],
                "content_hash": spec["content_hash"],
                "produced_by": spec["produced_by"],
            },
            headers=headers,
        )
        assert version.status_code == 200, version.text
        body = version.json()
        assert body["content_ref"] == spec["content_ref"]
        assert body["content_hash"] == spec["content_hash"]
        assert body["produced_by"] == spec["produced_by"]
        assert body["produced_by"].startswith("legacy_ab_demo_import:"), (
            "must always carry an explicit legacy-import discriminator, distinguishable from a "
            "produced_by value a live M4 production run would supply"
        )
        assert body["is_current"] is False, (
            "importing an old artifact must never silently make it the current version -- "
            "promotion is a separate, explicit, auditable action"
        )

        readback = client.get(
            f"/workspaces/{ws_id}/artifacts/{artifact['id']}/versions", headers=headers
        ).json()
        assert any(v["id"] == body["id"] for v in readback)


def test_legacy_ab_demo_import_never_duplicates_on_retry(client, bootstrapped, unique):
    ws_id = bootstrapped["workspace"]["id"]
    headers = bootstrapped["headers"]
    spec = REAL_LEGACY_ARTIFACTS[0]

    task = client.post(
        f"/workspaces/{ws_id}/tasks",
        json={"idempotency_key": f"legacy-ab-retry-task-{unique}", "kind": "legacy_ab_demo_import"},
        headers=headers,
    ).json()
    artifact = client.post(
        f"/workspaces/{ws_id}/tasks/{task['id']}/artifacts",
        json={"kind": spec["artifact_kind"], "content_hash": f"artifact-retry-{unique}"},
        headers=headers,
    ).json()

    def do_import():
        return client.post(
            f"/workspaces/{ws_id}/artifacts/{artifact['id']}/versions",
            json={
                "idempotency_key": f"legacy-ab-retry-version-{unique}",
                "content_ref": spec["content_ref"],
                "content_hash": spec["content_hash"],
                "produced_by": spec["produced_by"],
            },
            headers=headers,
        ).json()

    first = do_import()
    second = do_import()
    assert first["id"] == second["id"]
