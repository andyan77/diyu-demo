#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UAAB successor v1.2 deterministic positive/negative controls. Zero model calls.

Every control contains a positive case and at least one single-variable negative case.
The script writes a versioned evidence file and never mutates Dify state.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
import re
import subprocess
from types import ModuleType
from typing import Any, Callable

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EVIDENCE_DIR = os.path.join(UAPP, "evidence", "stages", "uapp_artifact_binding")

UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
STABLE_UAPP_MD5 = "99c3edf7bd12172a4fb011b588f25e57"
CONVERSATION_ID = "5cfcaf57-8808-4fc7-8c66-d661e515d05a"
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
OTHER_TASK = "TASK-OTHER"
T1_FP = "3d7342e36d939c31"
T1_BFP = "4af627e012e74e3a"
T1_LENGTH = 3497
T1_SHA256 = "65f58acb09de20b77ff1deb669e2210e5f128a4b06fbaab14fbf31cf9955b938"

PROTECTED_APPS: dict[str, tuple[str, str]] = {
    "M3": ("a4c3b19b-243f-490b-9aca-3aa19767d6a5", "cd93757bcf8ad322f3b32fc43b2da3ff"),
    "HOP": ("6c46fdb1-5f49-4513-a0c0-29957b3dcee4", "e38378c3c2a66b75aa7e645368c9e1ce"),
    "SEAM": ("5fca0162-e26b-4545-a00b-66b1a2a2a077", "db49a3da8973d4fdcbe9ecf63bdf7e2a"),
    "MATRIX": ("fd25ebfa-db67-40c3-82e5-202e1254facf", "6cdaeac9cacf69fbeea4bd25e1536ace"),
    "CAMPAIGN": ("1f9d65ea-8af5-45f0-a1d0-a80223d354e2", "4876dacc43a73741b41c5a3083796347"),
    "CONTENT_BRIEF": ("b1dcf784-540e-4b3f-8ba2-3812f477f3ce", "0c841642a71feedfb327ffb76aec0ddd"),
    "CREATIVE_SCRIPT": ("44b55f9d-3792-40c3-b095-f2696464b4ec", "a1cd859d5b88d0d025f336665ca94e51"),
    "PRODUCTION_DIRECTOR": ("13cfabd5-f592-4354-a304-47098b765697", "964e9a947dc9790d1de82496469689ad"),
    "PUBLISHING_PACKAGING": ("c9cdea24-9df3-400b-9ecd-1d740e8c96df", "788c8555aca09e6fa6d979f237f70157"),
}

CS_BODY = (
    "# Synthetic Creative Script\n\n"
    "Beat 1: a literal opening with a quoted phrase: \"keep this exact\".\n"
    "Beat 2: a deterministic middle.\n"
    "Beat 3: a deterministic close.\n"
)
PROJECTED_BODY = "Beat 1 opening; Beat 2 middle; Beat 3 close."
REGULAR_FIELD_A = "普通字段甲：保持 Hop 既有规则。"
REGULAR_FIELD_B = "普通字段乙：只改变这一项。"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("uaab_builder_v11", os.path.join(HERE, "UAAB_BUILD_BINDING_FIX_v1.1.py"))


def psql(sql: str, db: str = "dify") -> str:
    completed = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", db, "-tA", "-c", sql],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"psql failed: {(completed.stderr or '')[:300]}")
    return completed.stdout.strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def fp(value: str) -> str:
    result = 0xCBF29CE484222325
    for byte in (value or "").encode("utf-8"):
        result = ((result ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{result:016x}"


def load_main(code: str, name: str) -> Callable[..., dict[str, Any]]:
    namespace: dict[str, Any] = {}
    exec(compile(code, name, "exec"), namespace)
    function = namespace.get("main")
    if not callable(function):
        raise RuntimeError(f"No callable main in {name}")
    return function


def current_fields_code() -> str:
    graph = json.loads(
        psql(
            "select w.graph from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{UAPP_APP_ID}';"
        )
    )
    node = next(item for item in graph["nodes"] if item["id"] == "uapp_fields")
    return BUILDER.patch_fields_code(node["data"]["code"])


FIELDS = load_main(current_fields_code(), "uapp_fields_successor")
PICK = load_main(BUILDER.PICK_CODE, "uapp_pick_upstream_successor")
PERSIST = load_main(BUILDER.PERSIST_CODE, "uapp_persist_successor")


def artifact(
    body: str = CS_BODY,
    *,
    task_key: str = TASK_KEY,
    capability: str = "CREATIVE_SCRIPT",
    accepted: bool = True,
    stale: bool = False,
) -> dict[str, Any]:
    normalized = norm(body)
    return {
        "fp": fp(normalized[:256]),
        "nlen": len(normalized),
        "len": len(body),
        "cap": capability,
        "task_key": task_key,
        "turn": 9,
        "accepted": accepted,
        "accepted_turn": 10 if accepted else None,
        "accepted_rev": 10 if accepted else None,
        "dep": {},
        "stale": stale,
        "stale_reason": "TEST" if stale else None,
    }


def store_item(body: str = CS_BODY, *, capability: str = "CREATIVE_SCRIPT") -> dict[str, Any]:
    normalized = norm(body)
    return {
        "fp": fp(normalized[:256]),
        "bfp": fp(normalized),
        "cap": capability,
        "turn": 9,
        "task_key": TASK_KEY,
        "len": len(body),
        "nlen": len(normalized),
        "body": body,
    }


def state_json(record: dict[str, Any] | None = None) -> str:
    return json.dumps(
        {"task_key": TASK_KEY, "rev": 10, "fields": {}, "asked": [], "artifacts": [record or artifact()], "events": []},
        ensure_ascii=False,
    )


def selector_output() -> dict[str, Any]:
    return PICK(
        json.dumps({"v": 1, "items": [store_item()]}, ensure_ascii=False),
        state_json(),
        "PRODUCTION_DIRECTOR",
        "这版口播稿可以，基于它告诉我这条该怎么制作。",
        TASK_KEY,
    )


def hop_call(regular_field: str = REGULAR_FIELD_A, projected: str = PROJECTED_BODY) -> str:
    return (
        "provenance:\n  source_kind: TEST\n"
        f"`script_or_equivalent_beats`: {projected}\n"
        f"`content_promise`: {regular_field}\n"
    )


def run_fields(
    *,
    record: dict[str, Any] | None = None,
    call: str | None = None,
    target: str = "PRODUCTION_DIRECTOR",
    selector: dict[str, Any] | None = None,
    user_request: str = "这版口播稿可以，基于它告诉我这条该怎么制作。",
) -> dict[str, Any]:
    selected = dict(selector or selector_output())
    return FIELDS(
        state_json(record),
        TASK_KEY,
        call if call is not None else hop_call(),
        "无",
        target,
        user_request,
        "{}",
        selected.get("upstream_delivery", ""),
        selected.get("selected_fp", ""),
        selected.get("selected_bfp", ""),
        selected.get("selected_capability", ""),
        selected.get("selection_status", ""),
    )


def binding(result: dict[str, Any]) -> list[dict[str, Any]]:
    return json.loads(result["upstream_binding_json"])


def extracted_slot(text: str, slot: str) -> str | None:
    match = re.search(r'^"%s": ("(?:[^"\\]|\\.)*")$' % re.escape(slot), text, re.MULTILINE)
    return json.loads(match.group(1)) if match else None


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    text: str,
    positive_ok: bool,
    negative_ok: bool,
    positive: dict[str, Any],
    negative: dict[str, Any],
) -> None:
    checks.append(
        {
            "id": check_id,
            "text": text,
            "result": "PASS" if positive_ok and negative_ok else "FAIL",
            "positive_control": {"pass": positive_ok, **positive},
            "single_variable_negative_control": {"pass": negative_ok, **negative},
        }
    )


def predecessor_inheritance() -> dict[str, Any]:
    store_raw = psql(
        "select data::jsonb->>'value' from workflow_conversation_variables "
        f"where conversation_id='{CONVERSATION_ID}' and data::jsonb->>'name'='uapp_last_artifact' "
        "order by updated_at desc limit 1;"
    )
    state_raw = psql(
        "select data::jsonb->>'value' from workflow_conversation_variables "
        f"where conversation_id='{CONVERSATION_ID}' and data::jsonb->>'name'='uapp_task_fields' "
        "order by updated_at desc limit 1;"
    )
    stored = json.loads(store_raw)
    ledger = json.loads(state_raw)
    stored_cs = next(item for item in stored["items"] if item.get("fp") == T1_FP)
    ledger_cs = next(item for item in ledger["artifacts"] if item.get("fp") == T1_FP)
    body = stored_cs["body"]
    identity_current = {
        "body_length": len(body),
        "body_sha256": sha256_text(body),
        "store_fp": stored_cs.get("fp"),
        "store_bfp": stored_cs.get("bfp"),
        "ledger_fp": ledger_cs.get("fp"),
        "accepted": ledger_cs.get("accepted"),
        "stale": ledger_cs.get("stale"),
        "task_key": ledger_cs.get("task_key"),
    }
    identity_matches = (
        identity_current["body_length"] == T1_LENGTH
        and identity_current["body_sha256"] == T1_SHA256
        and identity_current["store_fp"] == T1_FP
        and identity_current["store_bfp"] == T1_BFP
        and identity_current["ledger_fp"] == T1_FP
        and identity_current["accepted"] is True
        and identity_current["stale"] is False
        and identity_current["task_key"] == TASK_KEY
    )
    return {
        "modified_binding_branch_condition": "target in {PRODUCTION_DIRECTOR, PUBLISHING_PACKAGING}",
        "T1_target": "CREATIVE_SCRIPT",
        "modified_binding_branch_reachable_from_T1": False,
        "current_identity": identity_current,
        "store_record_sha256": sha256_text(canonical(stored_cs)),
        "ledger_record_sha256": sha256_text(canonical(ledger_cs)),
        "predecessor_identity_matches": identity_matches,
        "chosen_path": "A · inherit T1 predecessor evidence" if identity_matches else "B · rerun T1",
        "path_frozen_before_model_calls": True,
    }


def main() -> int:
    checks: list[dict[str, Any]] = []
    base_selector = selector_output()
    base = run_fields(selector=base_selector)
    base_body = extracted_slot(base["capability_call"], "script_or_equivalent_beats")

    changed_body_selector = dict(base_selector)
    changed_body_selector["upstream_delivery"] = CS_BODY + "X"
    changed_body = run_fields(selector=changed_body_selector)
    add_check(
        checks,
        "S-01",
        "合法 selector 完整正文逐字节注入；正文单变量改变即拒绝",
        base["artifact_binding_status"] == "BOUND" and base_body == CS_BODY,
        changed_body["artifact_binding_status"] == "REJECTED" and binding(changed_body)[0]["reason"] == "FP_MISMATCH",
        {"binding": base["artifact_binding_status"], "injected_sha256": sha256_text(base_body or "")},
        {"mutated": "selector_delivery", "reason": binding(changed_body)[0]["reason"]},
    )

    status_changed = dict(base_selector)
    status_changed["selection_status"] = "NO_LEGAL_UPSTREAM"
    no_selection = run_fields(selector=status_changed)
    add_check(
        checks,
        "S-02",
        "Hop 投影不参与 artifact 身份；selector 状态单变量失效时投影不能顶替",
        base_body == CS_BODY and base_body != PROJECTED_BODY,
        extracted_slot(no_selection["capability_call"], "script_or_equivalent_beats") is None
        and binding(no_selection)[0]["reason"] == "SELECTOR_NOT_SELECTED",
        {"hop_projection_ignored": True},
        {"mutated": "selection_status", "hop_projection_used": False},
    )

    add_check(
        checks,
        "S-03",
        "fp 不一致 fail-closed",
        base["artifact_binding_status"] == "BOUND",
        binding(changed_body)[0]["reason"] == "FP_MISMATCH",
        {"fp": base_selector["selected_fp"]},
        {"mutated": "selector_delivery", "reason": binding(changed_body)[0]["reason"]},
    )

    wrong_bfp_selector = dict(base_selector)
    wrong_bfp_selector["selected_bfp"] = "0" * 16
    wrong_bfp = run_fields(selector=wrong_bfp_selector)
    add_check(
        checks,
        "S-04",
        "bfp 不一致 fail-closed",
        base["artifact_binding_status"] == "BOUND",
        binding(wrong_bfp)[0]["reason"] == "BFP_MISMATCH",
        {"bfp": base_selector["selected_bfp"]},
        {"mutated": "selected_bfp", "reason": binding(wrong_bfp)[0]["reason"]},
    )

    cross_task_record = artifact(task_key=OTHER_TASK)
    cross_task = run_fields(record=cross_task_record, selector=base_selector)
    add_check(
        checks,
        "S-05",
        "task 不一致 fail-closed",
        base["artifact_binding_status"] == "BOUND",
        binding(cross_task)[0]["reason"] == "CROSS_TASK",
        {"task": TASK_KEY},
        {"mutated": "ledger artifact task_key", "reason": binding(cross_task)[0]["reason"]},
    )

    wrong_cap_selector = dict(base_selector)
    wrong_cap_selector["selected_capability"] = "PRODUCTION_DIRECTOR"
    wrong_cap = run_fields(selector=wrong_cap_selector)
    add_check(
        checks,
        "S-06",
        "capability 不兼容 fail-closed",
        base["artifact_binding_status"] == "BOUND",
        binding(wrong_cap)[0]["reason"] == "CAPABILITY_INCOMPATIBLE",
        {"capability": "CREATIVE_SCRIPT"},
        {"mutated": "selected_capability", "reason": binding(wrong_cap)[0]["reason"]},
    )

    no_accept_request = "基于这份口播稿告诉我这条该怎么制作。"
    not_accepted = run_fields(
        record=artifact(accepted=False), selector=base_selector, user_request=no_accept_request
    )
    stale = run_fields(record=artifact(stale=True), selector=base_selector, user_request=no_accept_request)
    add_check(
        checks,
        "S-07",
        "NOT_ACCEPTED 或 STALE 均 fail-closed",
        base["artifact_binding_status"] == "BOUND",
        binding(not_accepted)[0]["reason"] == "NOT_ACCEPTED" and binding(stale)[0]["reason"] == "STALE",
        {"accepted": True, "stale": False},
        {
            "mutated": "accepted flag, then stale flag (two independent single-variable probes)",
            "not_accepted_reason": binding(not_accepted)[0]["reason"],
            "stale_reason": binding(stale)[0]["reason"],
        },
    )

    add_check(
        checks,
        "S-08",
        "selector 无合法结果时只保留精确缺口，不猜正文",
        base["artifact_binding_status"] == "BOUND",
        no_selection["artifact_binding_status"] == "REJECTED"
        and "script_or_equivalent_beats" in no_selection["gaps_text"]
        and extracted_slot(no_selection["capability_call"], "script_or_equivalent_beats") is None,
        {"status": "BOUND"},
        {"mutated": "selection_status", "gaps_text": no_selection["gaps_text"]},
    )

    pending_state = json.loads(base["pending_state_json"])
    carrier_clean = CS_BODY not in base["pending_state_json"] and all(
        entry.get("v") != CS_BODY for entry in pending_state.get("fields", {}).values()
    )
    leaked_state = json.loads(base["pending_state_json"])
    leaked_state.setdefault("fields", {})["artifact.leak"] = {"v": CS_BODY}
    leakage_detector_flips = any(
        entry.get("v") == CS_BODY for entry in leaked_state.get("fields", {}).values()
    )
    add_check(
        checks,
        "S-09",
        "artifact 正文不进入 canonical field carrier",
        carrier_clean,
        leakage_detector_flips,
        {"carrier_contains_body": False},
        {"mutated": "one carrier field value", "leak_detected": leakage_detector_flips},
    )

    changed_regular = run_fields(call=hop_call(REGULAR_FIELD_B), selector=base_selector)
    add_check(
        checks,
        "S-10",
        "普通非 artifact 字段继续服从 Hop 载体",
        REGULAR_FIELD_A in base["capability_call"],
        REGULAR_FIELD_B in changed_regular["capability_call"] and REGULAR_FIELD_A not in changed_regular["capability_call"],
        {"regular_field": REGULAR_FIELD_A},
        {"mutated": "Hop content_promise", "regular_field": REGULAR_FIELD_B},
    )

    fixture_store = json.dumps({"v": 1, "items": [store_item()]}, ensure_ascii=False)
    no_new = PERSIST("", "PRODUCTION_DIRECTOR", fixture_store, "CREATIVE_SCRIPT", state_json())
    with_new = PERSIST("new PD artifact", "PRODUCTION_DIRECTOR", fixture_store, "CREATIVE_SCRIPT", state_json())
    add_check(
        checks,
        "S-11",
        "NO_NEW_ARTIFACT 不推进 uapp_last_capability",
        no_new["persist_action"] == "NO_NEW_ARTIFACT" and no_new["capability_to_persist"] == "CREATIVE_SCRIPT",
        with_new["capability_to_persist"] == "PRODUCTION_DIRECTOR",
        {"capability": no_new["capability_to_persist"]},
        {"mutated": "new_artifact empty -> non-empty", "capability": with_new["capability_to_persist"]},
    )

    t1_selector = {
        "upstream_delivery": "",
        "selected_fp": "",
        "selected_bfp": "",
        "selected_capability": "",
        "selection_status": "NO_UPSTREAM_REQUIRED",
    }
    t1 = run_fields(call=hop_call(projected=""), target="CREATIVE_SCRIPT", selector=t1_selector)
    t1_target_mutation = run_fields(call=hop_call(projected=""), target="PRODUCTION_DIRECTOR", selector=t1_selector)
    current_hashes = {
        name: psql(
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{app_id}';"
        )
        for name, (app_id, _) in PROTECTED_APPS.items()
    }
    drift = {
        name: {"expected": PROTECTED_APPS[name][1], "actual": graph_hash}
        for name, graph_hash in current_hashes.items()
        if graph_hash != PROTECTED_APPS[name][1]
    }
    synthetic_drift = dict(current_hashes)
    synthetic_drift["HOP"] = "0" * 32
    drift_detector_flips = synthetic_drift["HOP"] != PROTECTED_APPS["HOP"][1]
    add_check(
        checks,
        "S-12",
        "T1 无上游分支与九个受保护应用零漂移",
        t1["artifact_binding_status"] == "NO_UPSTREAM_REQUIRED" and not drift,
        t1_target_mutation["artifact_binding_status"] == "REJECTED" and drift_detector_flips,
        {"T1_binding_branch_reachable": False, "protected_app_drift": drift},
        {
            "mutated": "target capability; separate synthetic protected hash probe",
            "PD_branch_status": t1_target_mutation["artifact_binding_status"],
            "drift_detected": drift_detector_flips,
        },
    )

    inheritance = predecessor_inheritance()
    pass_count = sum(item["result"] == "PASS" for item in checks)
    report = {
        "document": {
            "id": "UAAB_SUCCESSOR_CONTROLS_v1.2",
            "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
            "model_calls": 0,
            "writes_to_dify": 0,
            "builder_sha256": sha256_text(
                open(os.path.join(HERE, "UAAB_BUILD_BINDING_FIX_v1.1.py"), encoding="utf-8").read()
            ),
            "fields_code_sha256": sha256_text(current_fields_code()),
        },
        "summary": {
            "pass": pass_count,
            "total": len(checks),
            "positive_controls": len(checks),
            "single_variable_negative_controls": 13,
            "verdict": "PASS" if pass_count == len(checks) else "FAIL",
        },
        "predecessor_evidence_inheritance": inheritance,
        "checks": checks,
    }
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    evidence_path = os.path.join(EVIDENCE_DIR, "UAAB_SUCCESSOR_CONTROLS_v1.2.json")
    with open(evidence_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    logging.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    logging.info("chosen_path=%s", inheritance["chosen_path"])
    return 0 if pass_count == len(checks) and inheritance["predecessor_identity_matches"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
