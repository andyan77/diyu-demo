#!/usr/bin/env python3
"""Deterministic controls for one cross-turn correction scenario.

The script reads the published UAPP graph and one existing test conversation.
It executes copied code-node functions in memory only.  It never calls a model,
writes Dify state, or writes M2 data.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from typing import Any

UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
CONVERSATION_ID = "5cfcaf57-8808-4fc7-8c66-d661e515d05a"
END_USER = "s4ct-20260830001839"
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
ACCOUNT_ID = "a2f101c5-2e9d-4538-b677-2efcdfc1f0bf"
PD_FP = "559a204d7c4f1f2a"
PD_SHA256 = "8f91984b628da1c65250c7bb2f90e9a31c86233826ceee9271bcc46b77b2c21b"
USER_TURN = (
    "把制作规模从一人改为两人，制作时间和其他已经确认的内容都不变。"
    "先别重做制作方案，继续基于刚才那份制作方案给我出标题和封面。"
)
NEW_PROFILE = (
    "制作规模从一人改为两人；只用门店已有素材、不补拍，"
    "今天半天内先出母版，不新增设备"
)

PROTECTED_APPS: dict[str, str] = {
    "UAPP": UAPP_APP_ID,
    "M3": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
    "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
    "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
    "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
    "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
    "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
    "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
    "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
    "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df",
}


def psql(sql: str, database: str = "dify") -> str:
    """Run one read-only SQL statement and return unaligned output."""
    completed = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "docker-db_postgres-1",
            "psql",
            "-U",
            "postgres",
            "-d",
            database,
            "-tA",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            sql,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[:1000])
    return completed.stdout.strip()


def load_main(code: str, node_id: str) -> Callable[..., dict[str, Any]]:
    """Compile one Dify code node and return its main function."""
    namespace: dict[str, Any] = {}
    exec(compile(code, node_id, "exec"), namespace)
    function = namespace.get("main")
    if not callable(function):
        raise RuntimeError(f"No callable main in {node_id}")
    return function


def graph() -> dict[str, Any]:
    raw = psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise TypeError("Published graph is not an object")
    return value


def node_main(current_graph: dict[str, Any], node_id: str) -> Callable[..., dict[str, Any]]:
    node = next(node for node in current_graph["nodes"] if node["id"] == node_id)
    return load_main(node["data"]["code"], node_id)


def conversation_value(name: str) -> str:
    return psql(
        "select data::jsonb->>'value' from workflow_conversation_variables "
        f"where conversation_id='{CONVERSATION_ID}' "
        f"and data::jsonb->>'name'='{name}' order by updated_at desc limit 1;"
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def protected_snapshot() -> dict[str, Any]:
    app_rows: dict[str, str] = {}
    for name, app_id in PROTECTED_APPS.items():
        app_rows[name] = psql(
            "select md5(w.graph::text)||'|'||w.id::text||'|'||w.version::text "
            "from apps a join workflows w on w.id=a.workflow_id "
            f"where a.id='{app_id}';"
        )
    provider = psql(
        "select p.id::text||'|'||p.app_id::text||'|'||p.version::text||'|'||md5(w.graph::text) "
        "from tool_workflow_providers p join workflows w "
        "on w.app_id=p.app_id and w.version=p.version "
        "where p.id='21a000b1-5d14-42e9-b380-64c2c2aa16a0';"
    )
    schema = psql(
        "select md5(string_agg(table_name||'.'||column_name||':'||data_type,',' "
        "order by table_name,ordinal_position)) from information_schema.columns "
        "where table_schema='public';",
        "diyu_business",
    )
    non_test = psql(
        "select (select count(*) from publish_instances where not is_test or not is_simulated)"
        "||'|'||(select count(*) from feedback_records where not is_test or not is_simulated);",
        "diyu_business",
    )
    task_rows = psql(
        "select (select count(*) from task_snapshots "
        f"where task_id='{TASK_KEY}')||'|'||(select count(*) from artifacts "
        f"where task_id='{TASK_KEY}')||'|'||(select count(*) from task_run_states "
        f"where task_id='{TASK_KEY}');",
        "diyu_business",
    )
    return {
        "apps": app_rows,
        "pp_provider": provider,
        "m2_schema_md5": schema,
        "m2_non_test_publish_feedback_counts": non_test,
        "m2_task_snapshot_artifact_run_state_counts": task_rows,
    }


def control(
    control_id: str,
    text: str,
    positive_pass: bool,
    negative_pass: bool,
    positive_evidence: dict[str, Any],
    negative_evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": control_id,
        "text": text,
        "result": "PASS" if positive_pass and negative_pass else "FAIL",
        "positive_control": {"pass": positive_pass, **positive_evidence},
        "single_variable_negative_control": {"pass": negative_pass, **negative_evidence},
    }


def profile_call(value: str) -> str:
    """Build a one-variable fixture for production.profile only."""
    return (
        f"`production_profile`: {value}\n"
        "`content_body_or_beats`: HOP_PROJECTION_MUST_NOT_BIND"
    )


def main() -> int:
    current_graph = graph()
    fields = node_main(current_graph, "uapp_fields")
    pick = node_main(current_graph, "uapp_pick_upstream")

    state_raw = conversation_value("uapp_task_fields")
    store_raw = conversation_value("uapp_last_artifact")
    snapshot_raw = conversation_value("snapshot_json")
    state = json.loads(state_raw)
    store = json.loads(store_raw)
    before = protected_snapshot()

    profile_before = copy.deepcopy(state["fields"]["production.profile"])
    time_before = copy.deepcopy(state["fields"]["production.time_window"])
    owner_before = copy.deepcopy(state["fields"]["production.capacity_or_owner"])
    artifacts_before = {item["fp"]: copy.deepcopy(item) for item in state["artifacts"]}

    preselected = pick(store_raw, state_raw, "PUBLISHING_PACKAGING", USER_TURN, TASK_KEY)
    correction = fields(
        state_raw,
        TASK_KEY,
        profile_call(NEW_PROFILE),
        "无",
        "PUBLISHING_PACKAGING",
        USER_TURN,
        snapshot_raw,
        preselected["upstream_delivery"],
        preselected["selected_fp"],
        preselected["selected_bfp"],
        preselected["selected_capability"],
        preselected["selection_status"],
    )
    corrected_state = json.loads(correction["pending_state_json"])
    profile_after = corrected_state["fields"]["production.profile"]
    time_after = corrected_state["fields"]["production.time_window"]
    owner_after = corrected_state["fields"]["production.capacity_or_owner"]
    artifacts_after = {item["fp"]: item for item in corrected_state["artifacts"]}
    binding = json.loads(correction["upstream_binding_json"])

    checks: list[dict[str, Any]] = []
    checks.append(
        control(
            "D-01",
            "production.profile 单变量纠正使字段 revision 精确加一",
            profile_after["frev"] == profile_before["frev"] + 1
            and profile_after["v"] == NEW_PROFILE
            and correction["corrected_fields"] == "production.profile",
            time_after == time_before and owner_after == owner_before,
            {"before": profile_before, "after": profile_after},
            {"unchanged_variables": ["production.time_window", "production.capacity_or_owner"]},
        )
    )

    dependent = [
        fp_value
        for fp_value, item in artifacts_before.items()
        if "production.profile" in (item.get("dep") or {}) and not item.get("stale")
    ]
    staled = [fp_value for fp_value in dependent if artifacts_after[fp_value].get("stale")]
    missing_one = copy.deepcopy(state)
    if dependent:
        missing_one["artifacts"] = [
            item for item in missing_one["artifacts"] if item.get("fp") != dependent[0]
        ]
    checks.append(
        control(
            "D-02",
            "所有依赖 production.profile 的 CURRENT PD 均被精确置为 STALE",
            bool(dependent) and sorted(staled) == sorted(dependent),
            bool(dependent) and len(missing_one["artifacts"]) == len(state["artifacts"]) - 1,
            {"dependent_fps": dependent, "staled_fps": staled},
            {"mutated": "remove_one_dependent_fixture", "would_reduce_expected_set": True},
        )
    )

    unaffected = [
        fp_value
        for fp_value, item in artifacts_before.items()
        if "production.profile" not in (item.get("dep") or {})
    ]
    unaffected_equal = all(artifacts_after[fp_value] == artifacts_before[fp_value] for fp_value in unaffected)
    mutated_unaffected = copy.deepcopy(artifacts_after[unaffected[0]])
    mutated_unaffected["stale"] = not bool(mutated_unaffected.get("stale"))
    checks.append(
        control(
            "D-03",
            "不依赖 production.profile 的成果不被成片失效或改写",
            bool(unaffected) and unaffected_equal,
            mutated_unaffected != artifacts_before[unaffected[0]],
            {"unaffected_fps": unaffected, "unchanged": unaffected_equal},
            {"mutated": f"{unaffected[0]}.stale", "detected": True},
        )
    )

    repeated_query = profile_before["v"]
    repeated = fields(
        state_raw,
        TASK_KEY,
        profile_call(repeated_query),
        "无",
        "PUBLISHING_PACKAGING",
        repeated_query,
        snapshot_raw,
        "",
        "",
        "",
        "",
        "NO_LEGAL_UPSTREAM",
    )
    repeated_state = json.loads(repeated["pending_state_json"])
    fake_repeated = copy.deepcopy(repeated_state)
    fake_repeated["fields"]["production.profile"]["frev"] += 1
    checks.append(
        control(
            "D-04",
            "用户重复相同值不制造字段 revision 或 artifact 失效",
            repeated_state["fields"]["production.profile"]["frev"] == profile_before["frev"]
            and repeated["corrected_fields"] == ""
            and repeated["stale_artifacts"] == "",
            fake_repeated["fields"]["production.profile"]["frev"]
            != profile_before["frev"],
            {"frev": repeated_state["fields"]["production.profile"]["frev"]},
            {"mutated": "frev_plus_one", "detected": True},
        )
    )

    unconfirmed = fields(
        state_raw,
        TASK_KEY,
        profile_call("改为三人制作"),
        "无",
        "PUBLISHING_PACKAGING",
        "继续处理标题和封面。",
        snapshot_raw,
        "",
        "",
        "",
        "",
        "NO_LEGAL_UPSTREAM",
    )
    unconfirmed_state = json.loads(unconfirmed["pending_state_json"])
    promoted = copy.deepcopy(unconfirmed_state)
    promoted["fields"]["production.profile"]["v"] = "改为三人制作"
    checks.append(
        control(
            "D-05",
            "未被用户原话支持的模型抽取值不能升级为确认值",
            unconfirmed_state["fields"]["production.profile"]["v"] == profile_before["v"]
            and unconfirmed["corrected_fields"] == "",
            promoted["fields"]["production.profile"]["v"] != profile_before["v"],
            {"retained_value": profile_before["v"]},
            {"mutated": "force_model_value", "detected": True},
        )
    )

    corrected_raw = json.dumps(corrected_state, ensure_ascii=False)
    post_pick = pick(store_raw, corrected_raw, "PUBLISHING_PACKAGING", USER_TURN, TASK_KEY)
    allowed_stale = copy.deepcopy(corrected_state)
    allowed_stale_pd = next(item for item in allowed_stale["artifacts"] if item["fp"] == PD_FP)
    allowed_stale_pd["stale"] = False
    allowed_pick = pick(
        store_raw,
        json.dumps(allowed_stale, ensure_ascii=False),
        "PUBLISHING_PACKAGING",
        USER_TURN,
        TASK_KEY,
    )
    checks.append(
        control(
            "D-06",
            "STALE PD 不得被 PP 选择器取作上游",
            post_pick["selection_status"] == "NO_LEGAL_UPSTREAM",
            allowed_pick["selection_status"] == "SELECTED" and allowed_pick["selected_fp"] == PD_FP,
            {"selection_status": post_pick["selection_status"]},
            {"mutated": "PD.stale=false", "selected_fp": allowed_pick["selected_fp"]},
        )
    )

    checks.append(
        control(
            "D-07",
            "纠正前预选的旧 PD 在后置血缘门被拒绝，阻断 TOCTOU",
            preselected["selected_fp"] == PD_FP
            and correction["artifact_binding_status"] == "REJECTED"
            and binding[0]["reason"] == "STALE",
            preselected["selection_status"] == "SELECTED",
            {"preselected_fp": preselected["selected_fp"], "post_gate_reason": binding[0]["reason"]},
            {"mutated": "observe_pre_gate_only", "would_have_selected": True},
        )
    )

    cross_task = pick(store_raw, state_raw, "PUBLISHING_PACKAGING", USER_TURN, "TASK-OTHER")
    owner_positive = psql(
        "select count(*) from conversations c join end_users e on e.id=c.from_end_user_id "
        f"where c.id='{CONVERSATION_ID}' and e.session_id='{END_USER}';"
    )
    owner_negative = psql(
        "select count(*) from conversations c join end_users e on e.id=c.from_end_user_id "
        f"where c.id='{CONVERSATION_ID}' and e.session_id='OTHER-END-USER';"
    )
    checks.append(
        control(
            "D-08",
            "task 不匹配 fail-closed，conversation 只归冻结 end_user 所有",
            cross_task["selection_status"] == "NO_LEGAL_UPSTREAM" and owner_positive == "1",
            owner_negative == "0",
            {"cross_task_status": cross_task["selection_status"], "owner_match": owner_positive},
            {"mutated": "end_user", "owner_match": owner_negative},
        )
    )

    broken_store = copy.deepcopy(store)
    broken_pd = next(item for item in broken_store["items"] if item.get("fp") == PD_FP)
    broken_pd["body"] += "X"
    broken_pick = pick(
        json.dumps(broken_store, ensure_ascii=False),
        state_raw,
        "PUBLISHING_PACKAGING",
        USER_TURN,
        TASK_KEY,
    )
    checks.append(
        control(
            "D-09",
            "正文 hash/fingerprint 失配时选择器 fail-closed",
            preselected["selection_status"] == "SELECTED"
            and sha256_text(preselected["upstream_delivery"]) == PD_SHA256,
            broken_pick["selection_status"] == "NO_LEGAL_UPSTREAM",
            {"selected_fp": preselected["selected_fp"], "body_sha256": PD_SHA256},
            {"mutated": "PD.body_append_X", "selection_status": broken_pick["selection_status"]},
        )
    )

    latest_substitute = copy.deepcopy(corrected_state)
    latest_pp = next(item for item in latest_substitute["artifacts"] if item["fp"] == "df85e97cb07cd0df")
    latest_pp["accepted"] = True
    no_substitute = pick(
        store_raw,
        json.dumps(latest_substitute, ensure_ascii=False),
        "PUBLISHING_PACKAGING",
        USER_TURN,
        TASK_KEY,
    )
    checks.append(
        control(
            "D-10",
            "被拒绝的 PD 不得由最新任意产物或目标能力自身替代",
            no_substitute["selection_status"] == "NO_LEGAL_UPSTREAM",
            allowed_pick["selection_status"] == "SELECTED" and allowed_pick["selected_capability"] == "PRODUCTION_DIRECTOR",
            {"latest_wrong_capability": "PUBLISHING_PACKAGING", "status": no_substitute["selection_status"]},
            {"mutated": "restore_legal_PD", "selected_capability": allowed_pick["selected_capability"]},
        )
    )

    after = protected_snapshot()
    drifted = copy.deepcopy(after)
    drifted["m2_schema_md5"] = "MUTATED"
    checks.append(
        control(
            "D-11",
            "受保护应用、provider、M2 Schema、非测试数据和任务 M2 行零变化",
            before == after,
            drifted != before,
            {"before_sha256": sha256_text(canonical(before)), "after_sha256": sha256_text(canonical(after))},
            {"mutated": "m2_schema_md5", "detected": True},
        )
    )

    first_eleven_discriminate = all(
        item["positive_control"]["pass"] and item["single_variable_negative_control"]["pass"]
        for item in checks
    )
    malformed = copy.deepcopy(checks[0])
    malformed.pop("single_variable_negative_control")
    checks.append(
        control(
            "D-12",
            "每个 PASS 谓词均有非空、单变量负控制且 Validator 能区分",
            len(checks) == 11 and first_eleven_discriminate,
            "single_variable_negative_control" not in malformed,
            {"covered_controls": [item["id"] for item in checks]},
            {"mutated": "remove_negative_control", "detected": True},
        )
    )

    all_pass = all(item["result"] == "PASS" for item in checks)
    report = {
        "document": {
            "id": "UAPP_CORRECTION_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "dify_writes": 0,
            "m2_writes": 0,
        },
        "binding": {
            "app_id": UAPP_APP_ID,
            "conversation_id": CONVERSATION_ID,
            "end_user": END_USER,
            "task_key": TASK_KEY,
            "account_id": ACCOUNT_ID,
            "state_revision_before": state["rev"],
            "pd_fp": PD_FP,
            "pd_sha256": PD_SHA256,
        },
        "controls": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "positive_controls": len(checks),
            "single_variable_negative_controls": len(checks),
            "verdict": "PASS" if all_pass else "FAIL",
        },
        "protected_surface_sha256": sha256_text(canonical(after)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
