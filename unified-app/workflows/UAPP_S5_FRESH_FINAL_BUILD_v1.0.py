#!/usr/bin/env python3
"""Build the fresh-environment S5 two-blocker UAPP successor.

The patch is deliberately limited to two UAPP-owned seams:

* format-neutral current-turn normalization before the M3 request assembly;
* test-only publish, feedback and cycle writeback through the existing M2 API.

No model is called by this builder.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APP_ID = "dbb14eec-a935-445c-9764-280c8fd3375b"
BASE_GRAPH_MD5 = "32c02eb1b960c7d9b1e13a8bde23f2c1"
ENV_FILE = Path("/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env")
M2_BASE = "http://diyu-m2-app:8000"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DC = load_module("uapp_fresh_final_dc", ROOT / "account-operations/tools/dify_client.py")


NORMALIZE_SRC = r'''
import json
import re


def _clean(value):
    text = (value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    return text


def _pairs(text):
    raw = (text or "").strip()
    pairs = []
    left, right = raw.find("{"), raw.rfind("}")
    if 0 <= left < right:
        try:
            value = json.loads(raw[left:right + 1])
            if isinstance(value, dict):
                pairs = [(str(k).strip(), str(v).strip()) for k, v in value.items()
                         if str(k).strip() and str(v).strip()]
        except Exception:
            pairs = []
    if pairs:
        return pairs, "JSON_LIKE"
    for line in raw.splitlines():
        match = re.match(r"^\s*([^：:\n]{1,40})\s*[：:]\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.group(1).strip(), _clean(match.group(2))
        if key and value:
            pairs.append((key, value))
    return (pairs, "YAML_LIKE") if len(pairs) >= 2 else ([], "PLAIN")


def main(user_query):
    raw = (user_query or "").strip()
    pairs, mode = _pairs(raw)
    if not pairs:
        return {"normalized_query": raw, "format_mode": mode,
                "pair_count": "0", "source_preserved": "true"}
    lines = [raw, "", "【以下仅把本轮用户逐项写出的原值改成统一读法，不补充新事实】"]
    for key, value in pairs:
        lines.append("用户明确写出的「%s」是「%s」。" % (key, value))
    return {"normalized_query": "\n".join(lines), "format_mode": mode,
            "pair_count": str(len(pairs)), "source_preserved": "true"}
'''


PUBLISH_PREP_SRC = r'''
import hashlib
import json
import re
import time


CONTENT_CAPS = ("CONTENT_BRIEF", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR",
                "PUBLISHING_PACKAGING")


def _norm(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _explicitly_published(text):
    value = _norm(text)
    happened = bool(re.search(r"(?:已经|已|刚刚|刚才).{0,5}(?:发出|发布|发了|上线)", value))
    planned = bool(re.search(r"(?:准备|打算|计划|等会|稍后|将要).{0,5}(?:发|发布|上线)", value))
    return happened and not planned


def main(action, user_query, store_json, state_json, task_id, account_id,
         workspace_id, platform_text, previous_binding):
    empty = {"mode": "INVALID", "reason": "还没有可以对应到本次发布的当前内容。",
             "artifact_body": "{}", "version_body": "{}", "publish_template": "{}",
             "state_after": state_json or "", "selected_fp": "", "content_hash": ""}
    if action != "RECORD_PUBLISH" or not _explicitly_published(user_query):
        empty["reason"] = "只有明确已经发布的内容才能登记；准备发布不会被记成已发布。"
        return empty
    if not all((task_id, account_id, workspace_id)):
        empty["reason"] = "当前任务身份还不完整，暂时不能登记发布。"
        return empty
    try:
        store = json.loads(store_json or "{}")
        state = json.loads(state_json or "{}")
    except Exception:
        return empty
    if not isinstance(store, dict) or not isinstance(state, dict):
        return empty
    task_key = state.get("task_key")
    ledger = {row.get("fp"): row for row in state.get("artifacts", [])
              if isinstance(row, dict) and row.get("fp")}
    selected = None
    for item in reversed(store.get("items", [])):
        if not isinstance(item, dict) or not (item.get("body") or "").strip():
            continue
        record = ledger.get(item.get("fp")) or {}
        if (item.get("task_key") == task_key and item.get("cap") in CONTENT_CAPS
                and record.get("task_key") == task_key
                and record.get("cap") == item.get("cap") and not record.get("stale")):
            selected = item
            break
    if selected is None:
        return empty
    body = selected["body"].strip()
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    selected_fp = selected.get("fp") or ""
    try:
        prior = json.loads(previous_binding or "{}")
    except Exception:
        prior = {}
    if (prior.get("task_id") == task_id and prior.get("selected_fp") == selected_fp
            and prior.get("content_hash") == digest and prior.get("publish_id")
            and prior.get("version_id")):
        return {**empty, "mode": "REUSE", "reason": "这次发布已经登记过，不会重复写入。",
                "selected_fp": selected_fp, "content_hash": digest,
                "state_after": state_json or ""}
    revision = int(state.get("rev") or 0) + 1
    state["rev"] = revision
    for row in state.get("artifacts", []):
        if isinstance(row, dict) and row.get("fp") == selected_fp:
            row["accepted"] = True
            row["accepted_turn"] = revision
            row["accepted_rev"] = revision
    state.setdefault("events", []).append({"kind": "ACCEPT_AND_RECORD_PUBLISH",
                                             "turn": revision, "fp": selected_fp})
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    platform = (platform_text or "test-platform").strip()
    return {
        "mode": "CREATE", "reason": "",
        "artifact_body": json.dumps({"kind": "final", "content_hash": digest}, ensure_ascii=False),
        "version_body": json.dumps({"idempotency_key": "ver-%s" % digest[:24],
                                      "content_ref": "uapp://conversation-artifact/%s" % selected_fp,
                                      "content_hash": digest,
                                      "produced_by": "unified-app/%s" % selected.get("cap")},
                                     ensure_ascii=False),
        "publish_template": json.dumps({"idempotency_key": "pub-%s-%s" %
                                          (digest[:20], hashlib.sha256(platform.encode()).hexdigest()[:8]),
                                          "account_id": account_id, "platform": platform,
                                          "published_at": now, "is_test": True,
                                          "is_simulated": True}, ensure_ascii=False),
        "state_after": json.dumps(state, ensure_ascii=False),
        "selected_fp": selected_fp, "content_hash": digest,
    }
'''


PARSE_SRC = r'''
import json


def main(raw, status):
    try:
        body = json.loads(raw or "{}")
    except Exception:
        body = {}
    ok = str(status) in ("200", "201") and bool(body.get("id"))
    return {"ok": "true" if ok else "false", "id": body.get("id") or "",
            "status": str(status or ""),
            "detail": "" if ok else json.dumps(body, ensure_ascii=False)[:500]}
'''


PUBLISH_BODY_SRC = r'''
import json


def main(template, version_id):
    try:
        body = json.loads(template or "{}")
    except Exception:
        body = {}
    if version_id:
        body["content_version_id"] = version_id
    return {"body": json.dumps(body, ensure_ascii=False),
            "has_target": "true" if version_id else "false"}
'''


PUBLISH_FINAL_SRC = r'''
import json


def main(artifact_ok, version_ok, promote_ok, publish_ok, artifact_id, version_id,
         publish_id, state_after, task_id, selected_fp, content_hash):
    ok = all(str(value) == "true" for value in
             (artifact_ok, version_ok, promote_ok, publish_ok))
    binding = ""
    if ok:
        binding = json.dumps({"task_id": task_id, "selected_fp": selected_fp,
                              "content_hash": content_hash, "artifact_id": artifact_id,
                              "version_id": version_id, "publish_id": publish_id},
                             ensure_ascii=False)
    return {"ok": "true" if ok else "false", "binding": binding,
            "state_after": state_after or "",
            "user_text": ("这条已经按测试记录登记好了。之后的反馈会只对应这条内容。"
                          if ok else "这次发布记录没有完整写成，我先不把它算作已经登记。")}
'''


FEEDBACK_PREP_SRC = r'''
import hashlib
import json
import re
import time


def main(action, feedback_text, publish_id):
    text = re.sub(r"\s+", " ", feedback_text or "").strip()
    if action != "RECORD_FEEDBACK" or not text:
        return {"valid": "false", "body": "{}",
                "reason": "这一轮没有明确可登记的实际反馈。"}
    if not publish_id:
        return {"valid": "false", "body": "{}",
                "reason": "这条反馈还没有对应的已登记发布内容，请先确认是哪一条。"}
    key = hashlib.sha256((publish_id + "\n" + text).encode("utf-8")).hexdigest()[:24]
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    body = {"idempotency_key": "fb-%s" % key, "publish_instance_id": publish_id,
            "kind": "observation", "source": "user_reported", "observed_at": now,
            "is_test": True, "is_simulated": True, "is_manual_entry": True,
            "is_pre_publish_review": False, "payload": {"note": text}}
    return {"valid": "true", "body": json.dumps(body, ensure_ascii=False), "reason": ""}
'''


CYCLE_PREP_SRC = r'''
import hashlib
import json
import re
import time


def main(action, user_query, account_id, current_cycle_id, publish_id, feedback_id,
         prior_transition):
    text = re.sub(r"\s+", " ", user_query or "").strip()
    fp = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
    try:
        prior = json.loads(prior_transition or "{}")
    except Exception:
        prior = {}
    if action != "NEXT_CYCLE":
        return {"mode": "INVALID", "body": "{}", "reason": "没有明确要求结束当前周期。",
                "request_fp": fp}
    if prior.get("request_fp") == fp and prior.get("next_cycle_id"):
        return {"mode": "REUSE", "body": "{}", "reason": "这个周期转换已经完成，不会重复建立。",
                "request_fp": fp}
    if not all((account_id, current_cycle_id, publish_id, feedback_id)):
        return {"mode": "INVALID", "body": "{}",
                "reason": "发布和反馈链还不完整，当前周期暂时不能收口。", "request_fp": fp}
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    body = {"idempotency_key": "next-%s-%s" % (current_cycle_id, fp[:12]),
            "account_id": account_id, "label": "下一个周期", "start_at": now}
    return {"mode": "CREATE", "body": json.dumps(body, ensure_ascii=False),
            "reason": "", "request_fp": fp}
'''


CYCLE_FINAL_SRC = r'''
import json


def main(ok, cycle_id, request_fp):
    passed = str(ok) == "true" and bool(cycle_id)
    binding = (json.dumps({"request_fp": request_fp, "next_cycle_id": cycle_id},
                          ensure_ascii=False) if passed else "")
    return {"ok": "true" if passed else "false", "binding": binding,
            "user_text": ("当前周期已经收好，下一周期也已经建立，可以从这里继续。"
                          if passed else "当前周期没有完整收口，我先不把下一周期算作已经建立。")}
'''


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def variable(name: str, selector: list[str]) -> dict[str, Any]:
    return {"variable": name, "value_selector": selector}


def code_node(node_id: str, title: str, source: str,
              variables: list[dict[str, Any]], outputs: list[str],
              x: int, y: int) -> dict[str, Any]:
    return {
        "id": node_id, "type": "custom", "width": 244, "height": 98,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "sourcePosition": "right", "targetPosition": "left", "selected": False,
        "zIndex": 0,
        "data": {"type": "code", "title": title, "desc": "", "selected": False,
                 "code_language": "python3", "code": source, "variables": variables,
                 "outputs": {key: {"type": "string", "children": None} for key in outputs}},
    }


def http_node(node_id: str, title: str, url: str, body: str,
              x: int, y: int) -> dict[str, Any]:
    return {
        "id": node_id, "type": "custom", "width": 244, "height": 98,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "sourcePosition": "right", "targetPosition": "left", "selected": False,
        "zIndex": 0,
        "data": {"type": "http-request", "title": title, "desc": "仅写测试域；失败即关闭",
                 "method": "post", "url": url, "authorization": {"type": "no-auth", "config": None},
                 "headers": "X-Actor-Ref:{{#conversation.uapp_actor#}}", "params": "",
                 "selected": False, "timeout": {"connect": 10, "read": 60, "write": 20},
                 "error_strategy": "default-value",
                 "default_value": [{"key": "body", "type": "string", "value": ""},
                                   {"key": "status_code", "type": "number", "value": 0},
                                   {"key": "headers", "type": "object", "value": {}},
                                   {"key": "files", "type": "array[file]", "value": []}],
                 "body": {"type": "json", "data": [{"key": "", "type": "text", "value": body}]}},
    }


def gate_node(node_id: str, title: str, selector: list[str], cases: list[tuple[str, str]],
              x: int, y: int) -> dict[str, Any]:
    return {
        "id": node_id, "type": "custom", "width": 244, "height": 98,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "sourcePosition": "right", "targetPosition": "left", "selected": False,
        "zIndex": 0,
        "data": {"type": "if-else", "title": title, "desc": "", "selected": False,
                 "logical_operator": "and",
                 "cases": [{"case_id": case_id, "logical_operator": "and",
                            "conditions": [{"comparison_operator": "is", "value": value,
                                            "variable_selector": selector}]}
                           for case_id, value in cases]},
    }


def answer_node(node_id: str, title: str, value: str, x: int, y: int) -> dict[str, Any]:
    return {
        "id": node_id, "type": "custom", "width": 244, "height": 98,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "sourcePosition": "right", "targetPosition": "left", "selected": False,
        "zIndex": 0,
        "data": {"type": "answer", "title": title, "desc": "", "answer": value,
                 "variables": [], "selected": False},
    }


def assign_node(node_id: str, title: str,
                assignments: list[tuple[list[str], str]], x: int, y: int) -> dict[str, Any]:
    return {
        "id": node_id, "type": "custom", "width": 244, "height": 98,
        "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
        "sourcePosition": "right", "targetPosition": "left", "selected": False,
        "zIndex": 0,
        "data": {"type": "assigner", "version": "2", "title": title, "desc": "",
                 "selected": False,
                 "items": [{"input_type": "variable", "operation": "over-write",
                            "write_mode": "over-write", "value": source,
                            "variable_selector": ["conversation", target]}
                           for source, target in assignments]},
    }


def edge(source: str, target: str, handle: str = "source",
         source_type: str = "code", target_type: str = "code") -> dict[str, Any]:
    return {"id": f"{source}-{handle}-{target}", "type": "custom", "source": source,
            "target": target, "sourceHandle": handle, "targetHandle": "target", "zIndex": 0,
            "data": {"isInIteration": False, "isInLoop": False,
                     "sourceType": source_type, "targetType": target_type}}


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    nodes = {item["id"]: item for item in candidate["nodes"]}
    required = {"m1_compiler", "uapp_action", "uapp_route", "uapp_withdraw_gate", "uapp_m3_gate"}
    if not required.issubset(nodes):
        raise RuntimeError(f"missing nodes: {sorted(required - set(nodes))}")
    reserved = {"uapp_format_normalize", "uapp_writeback_gate", "uapp_publish_prepare"}
    if reserved & set(nodes):
        raise RuntimeError("successor nodes already exist")

    # Format-neutral projection changes only the route input, not M1 or M3.
    normalize = code_node(
        "uapp_format_normalize", "归一｜结构化表达原值", NORMALIZE_SRC,
        [variable("user_query", ["sys", "query"])],
        ["normalized_query", "format_mode", "pair_count", "source_preserved"], 2800, 1660,
    )
    candidate["nodes"].append(normalize)
    route_vars = nodes["uapp_route"]["data"]["variables"]
    user_var = [item for item in route_vars if item.get("variable") == "user_query"]
    if len(user_var) != 1 or user_var[0].get("value_selector") != ["sys", "query"]:
        raise RuntimeError("uapp_route user_query binding drift")
    user_var[0]["value_selector"] = ["uapp_format_normalize", "normalized_query"]
    candidate["edges"] = [item for item in candidate["edges"]
                          if item["id"] != "m1_compiler-source-uapp_action"]
    candidate["edges"].extend([
        edge("m1_compiler", "uapp_format_normalize"),
        edge("uapp_format_normalize", "uapp_action"),
    ])

    # Writeback dispatch is before M3: write actions never need a professional capability.
    candidate["edges"] = [item for item in candidate["edges"]
                          if item["id"] != "uapp_withdraw_gate-false-uapp_m3_gate"]
    candidate["nodes"].append(gate_node(
        "uapp_writeback_gate", "分流｜测试域写回", ["uapp_route", "action"],
        [("publish", "RECORD_PUBLISH"), ("feedback", "RECORD_FEEDBACK"),
         ("cycle", "NEXT_CYCLE")], 7200, 1180,
    ))
    candidate["edges"].extend([
        edge("uapp_withdraw_gate", "uapp_writeback_gate", "false", "if-else", "if-else"),
        edge("uapp_writeback_gate", "uapp_m3_gate", "false", "if-else", "if-else"),
    ])

    # Publish branch: select and accept the exact current conversation artifact, then create
    # artifact -> version -> current promotion -> one simulated publish row.
    candidate["nodes"].extend([
        code_node("uapp_publish_prepare", "选择｜当前合法内容并组装测试发布", PUBLISH_PREP_SRC,
                  [variable("action", ["uapp_route", "action"]),
                   variable("user_query", ["sys", "query"]),
                   variable("store_json", ["conversation", "uapp_last_artifact"]),
                   variable("state_json", ["conversation", "uapp_task_fields"]),
                   variable("task_id", ["conversation", "uapp_task"]),
                   variable("account_id", ["conversation", "uapp_account"]),
                   variable("workspace_id", ["conversation", "uapp_ws"]),
                   variable("platform_text", ["uapp_route", "platform_text"]),
                   variable("previous_binding", ["conversation", "uapp_publish_binding"])],
                  ["mode", "reason", "artifact_body", "version_body", "publish_template",
                   "state_after", "selected_fp", "content_hash"], 7520, 700),
        gate_node("uapp_publish_mode", "发布是否可写", ["uapp_publish_prepare", "mode"],
                  [("create", "CREATE"), ("reuse", "REUSE")], 7840, 700),
        http_node("uapp_publish_artifact", "写 M2｜发布内容产物", M2_BASE +
                  "/workspaces/{{#conversation.uapp_ws#}}/tasks/{{#conversation.uapp_task#}}/artifacts",
                  "{{#uapp_publish_prepare.artifact_body#}}", 8160, 500),
        code_node("uapp_publish_artifact_parse", "复核｜发布内容产物", PARSE_SRC,
                  [variable("raw", ["uapp_publish_artifact", "body"]),
                   variable("status", ["uapp_publish_artifact", "status_code"])],
                  ["ok", "id", "status", "detail"], 8480, 500),
        http_node("uapp_publish_version", "写 M2｜发布内容版本", M2_BASE +
                  "/workspaces/{{#conversation.uapp_ws#}}/artifacts/"
                  "{{#uapp_publish_artifact_parse.id#}}/versions",
                  "{{#uapp_publish_prepare.version_body#}}", 8800, 500),
        code_node("uapp_publish_version_parse", "复核｜发布内容版本", PARSE_SRC,
                  [variable("raw", ["uapp_publish_version", "body"]),
                   variable("status", ["uapp_publish_version", "status_code"])],
                  ["ok", "id", "status", "detail"], 9120, 500),
        http_node("uapp_publish_promote", "写 M2｜设为当前内容版本", M2_BASE +
                  "/workspaces/{{#conversation.uapp_ws#}}/artifacts/"
                  "{{#uapp_publish_artifact_parse.id#}}/versions/"
                  "{{#uapp_publish_version_parse.id#}}/promote", "{}", 9440, 500),
        code_node("uapp_publish_promote_parse", "复核｜当前内容版本", PARSE_SRC,
                  [variable("raw", ["uapp_publish_promote", "body"]),
                   variable("status", ["uapp_publish_promote", "status_code"])],
                  ["ok", "id", "status", "detail"], 9760, 500),
        code_node("uapp_publish_body", "组装｜测试发布请求", PUBLISH_BODY_SRC,
                  [variable("template", ["uapp_publish_prepare", "publish_template"]),
                   variable("version_id", ["uapp_publish_version_parse", "id"])],
                  ["body", "has_target"], 10080, 500),
        http_node("uapp_publish_post", "写 M2｜登记测试发布", M2_BASE +
                  "/workspaces/{{#conversation.uapp_ws#}}/publish-instances",
                  "{{#uapp_publish_body.body#}}", 10400, 500),
        code_node("uapp_publish_parse", "复核｜测试发布", PARSE_SRC,
                  [variable("raw", ["uapp_publish_post", "body"]),
                   variable("status", ["uapp_publish_post", "status_code"])],
                  ["ok", "id", "status", "detail"], 10720, 500),
        code_node("uapp_publish_final", "收口｜发布写回", PUBLISH_FINAL_SRC,
                  [variable("artifact_ok", ["uapp_publish_artifact_parse", "ok"]),
                   variable("version_ok", ["uapp_publish_version_parse", "ok"]),
                   variable("promote_ok", ["uapp_publish_promote_parse", "ok"]),
                   variable("publish_ok", ["uapp_publish_parse", "ok"]),
                   variable("artifact_id", ["uapp_publish_artifact_parse", "id"]),
                   variable("version_id", ["uapp_publish_version_parse", "id"]),
                   variable("publish_id", ["uapp_publish_parse", "id"]),
                   variable("state_after", ["uapp_publish_prepare", "state_after"]),
                   variable("task_id", ["conversation", "uapp_task"]),
                   variable("selected_fp", ["uapp_publish_prepare", "selected_fp"]),
                   variable("content_hash", ["uapp_publish_prepare", "content_hash"])],
                  ["ok", "binding", "state_after", "user_text"], 11040, 500),
        gate_node("uapp_publish_result_gate", "发布写回完整吗", ["uapp_publish_final", "ok"],
                  [("ok", "true")], 11360, 500),
        assign_node("uapp_publish_assign", "记住｜测试发布绑定",
                    [(["uapp_publish_version_parse", "id"], "uapp_last_version"),
                     (["uapp_publish_parse", "id"], "uapp_last_publish"),
                     (["uapp_publish_final", "binding"], "uapp_publish_binding"),
                     (["uapp_publish_final", "state_after"], "uapp_task_fields")], 11680, 420),
        answer_node("uapp_publish_ok_answer", "回复｜发布已登记",
                    "{{#uapp_publish_final.user_text#}}", 12000, 420),
        answer_node("uapp_publish_fail_answer", "回复｜发布未登记",
                    "这次发布记录没有完整写成，我先不把它算作已经登记。", 11680, 660),
        answer_node("uapp_publish_reuse_answer", "回复｜发布幂等",
                    "这次发布已经登记过，不会重复写入。", 8160, 760),
        answer_node("uapp_publish_gap_answer", "回复｜发布缺口",
                    "{{#uapp_publish_prepare.reason#}}", 8160, 920),
    ])

    publish_chain = [
        ("uapp_writeback_gate", "uapp_publish_prepare", "publish", "if-else", "code"),
        ("uapp_publish_prepare", "uapp_publish_mode", "source", "code", "if-else"),
        ("uapp_publish_mode", "uapp_publish_artifact", "create", "if-else", "http-request"),
        ("uapp_publish_artifact", "uapp_publish_artifact_parse", "source", "http-request", "code"),
        ("uapp_publish_artifact_parse", "uapp_publish_version", "source", "code", "http-request"),
        ("uapp_publish_version", "uapp_publish_version_parse", "source", "http-request", "code"),
        ("uapp_publish_version_parse", "uapp_publish_promote", "source", "code", "http-request"),
        ("uapp_publish_promote", "uapp_publish_promote_parse", "source", "http-request", "code"),
        ("uapp_publish_promote_parse", "uapp_publish_body", "source", "code", "code"),
        ("uapp_publish_body", "uapp_publish_post", "source", "code", "http-request"),
        ("uapp_publish_post", "uapp_publish_parse", "source", "http-request", "code"),
        ("uapp_publish_parse", "uapp_publish_final", "source", "code", "code"),
        ("uapp_publish_final", "uapp_publish_result_gate", "source", "code", "if-else"),
        ("uapp_publish_result_gate", "uapp_publish_assign", "ok", "if-else", "assigner"),
        ("uapp_publish_assign", "uapp_publish_ok_answer", "source", "assigner", "answer"),
        ("uapp_publish_result_gate", "uapp_publish_fail_answer", "false", "if-else", "answer"),
        ("uapp_publish_mode", "uapp_publish_reuse_answer", "reuse", "if-else", "answer"),
        ("uapp_publish_mode", "uapp_publish_gap_answer", "false", "if-else", "answer"),
    ]
    candidate["edges"].extend(edge(*item) for item in publish_chain)

    # Feedback branch: exactly one current test publish, stable content-based idempotency.
    candidate["nodes"].extend([
        code_node("uapp_feedback_prepare", "组装｜测试反馈", FEEDBACK_PREP_SRC,
                  [variable("action", ["uapp_route", "action"]),
                   variable("feedback_text", ["uapp_route", "feedback_text"]),
                   variable("publish_id", ["conversation", "uapp_last_publish"])],
                  ["valid", "body", "reason"], 7520, 1180),
        gate_node("uapp_feedback_gate", "反馈可写吗", ["uapp_feedback_prepare", "valid"],
                  [("ok", "true")], 7840, 1180),
        http_node("uapp_feedback_post", "写 M2｜登记测试反馈", M2_BASE +
                  "/workspaces/{{#conversation.uapp_ws#}}/feedback",
                  "{{#uapp_feedback_prepare.body#}}", 8160, 1100),
        code_node("uapp_feedback_parse", "复核｜测试反馈", PARSE_SRC,
                  [variable("raw", ["uapp_feedback_post", "body"]),
                   variable("status", ["uapp_feedback_post", "status_code"])],
                  ["ok", "id", "status", "detail"], 8480, 1100),
        gate_node("uapp_feedback_result_gate", "反馈写回完整吗", ["uapp_feedback_parse", "ok"],
                  [("ok", "true")], 8800, 1100),
        assign_node("uapp_feedback_assign", "记住｜测试反馈",
                    [(["uapp_feedback_parse", "id"], "uapp_last_feedback")], 9120, 1040),
        answer_node("uapp_feedback_ok_answer", "回复｜反馈已登记",
                    "这条反馈已经对应到刚才那次测试发布；重复提交也不会多记一条。", 9440, 1040),
        answer_node("uapp_feedback_fail_answer", "回复｜反馈未登记",
                    "这条反馈没有完整写成，我先不把它算作已经登记。", 9120, 1220),
        answer_node("uapp_feedback_gap_answer", "回复｜反馈缺口",
                    "{{#uapp_feedback_prepare.reason#}}", 8160, 1360),
    ])
    feedback_chain = [
        ("uapp_writeback_gate", "uapp_feedback_prepare", "feedback", "if-else", "code"),
        ("uapp_feedback_prepare", "uapp_feedback_gate", "source", "code", "if-else"),
        ("uapp_feedback_gate", "uapp_feedback_post", "ok", "if-else", "http-request"),
        ("uapp_feedback_post", "uapp_feedback_parse", "source", "http-request", "code"),
        ("uapp_feedback_parse", "uapp_feedback_result_gate", "source", "code", "if-else"),
        ("uapp_feedback_result_gate", "uapp_feedback_assign", "ok", "if-else", "assigner"),
        ("uapp_feedback_assign", "uapp_feedback_ok_answer", "source", "assigner", "answer"),
        ("uapp_feedback_result_gate", "uapp_feedback_fail_answer", "false", "if-else", "answer"),
        ("uapp_feedback_gate", "uapp_feedback_gap_answer", "false", "if-else", "answer"),
    ]
    candidate["edges"].extend(edge(*item) for item in feedback_chain)

    # Cycle branch: M2 atomically supersedes the previous current cycle. A conversation
    # binding makes the same close request idempotent even after uapp_cycle changes.
    candidate["nodes"].extend([
        code_node("uapp_cycle_prepare", "组装｜周期收口与下一周期", CYCLE_PREP_SRC,
                  [variable("action", ["uapp_route", "action"]),
                   variable("user_query", ["sys", "query"]),
                   variable("account_id", ["conversation", "uapp_account"]),
                   variable("current_cycle_id", ["conversation", "uapp_cycle"]),
                   variable("publish_id", ["conversation", "uapp_last_publish"]),
                   variable("feedback_id", ["conversation", "uapp_last_feedback"]),
                   variable("prior_transition", ["conversation", "uapp_cycle_transition"])],
                  ["mode", "body", "reason", "request_fp"], 7520, 1660),
        gate_node("uapp_cycle_mode", "周期可以转换吗", ["uapp_cycle_prepare", "mode"],
                  [("create", "CREATE"), ("reuse", "REUSE")], 7840, 1660),
        http_node("uapp_cycle_post", "写 M2｜建立下一周期", M2_BASE +
                  "/workspaces/{{#conversation.uapp_ws#}}/cycles",
                  "{{#uapp_cycle_prepare.body#}}", 8160, 1560),
        code_node("uapp_cycle_parse", "复核｜下一周期", PARSE_SRC,
                  [variable("raw", ["uapp_cycle_post", "body"]),
                   variable("status", ["uapp_cycle_post", "status_code"])],
                  ["ok", "id", "status", "detail"], 8480, 1560),
        code_node("uapp_cycle_final", "收口｜周期转换", CYCLE_FINAL_SRC,
                  [variable("ok", ["uapp_cycle_parse", "ok"]),
                   variable("cycle_id", ["uapp_cycle_parse", "id"]),
                   variable("request_fp", ["uapp_cycle_prepare", "request_fp"])],
                  ["ok", "binding", "user_text"], 8800, 1560),
        gate_node("uapp_cycle_result_gate", "周期转换完整吗", ["uapp_cycle_final", "ok"],
                  [("ok", "true")], 9120, 1560),
        assign_node("uapp_cycle_assign", "记住｜下一周期",
                    [(["uapp_cycle_parse", "id"], "uapp_cycle"),
                     (["uapp_cycle_final", "binding"], "uapp_cycle_transition")], 9440, 1500),
        answer_node("uapp_cycle_ok_answer", "回复｜下一周期已建立",
                    "{{#uapp_cycle_final.user_text#}}", 9760, 1500),
        answer_node("uapp_cycle_fail_answer", "回复｜周期未收口",
                    "当前周期没有完整收口，我先不把下一周期算作已经建立。", 9440, 1700),
        answer_node("uapp_cycle_reuse_answer", "回复｜周期幂等",
                    "这个周期转换已经完成，不会重复建立。", 8160, 1800),
        answer_node("uapp_cycle_gap_answer", "回复｜周期缺口",
                    "{{#uapp_cycle_prepare.reason#}}", 8160, 1980),
    ])
    cycle_chain = [
        ("uapp_writeback_gate", "uapp_cycle_prepare", "cycle", "if-else", "code"),
        ("uapp_cycle_prepare", "uapp_cycle_mode", "source", "code", "if-else"),
        ("uapp_cycle_mode", "uapp_cycle_post", "create", "if-else", "http-request"),
        ("uapp_cycle_post", "uapp_cycle_parse", "source", "http-request", "code"),
        ("uapp_cycle_parse", "uapp_cycle_final", "source", "code", "code"),
        ("uapp_cycle_final", "uapp_cycle_result_gate", "source", "code", "if-else"),
        ("uapp_cycle_result_gate", "uapp_cycle_assign", "ok", "if-else", "assigner"),
        ("uapp_cycle_assign", "uapp_cycle_ok_answer", "source", "assigner", "answer"),
        ("uapp_cycle_result_gate", "uapp_cycle_fail_answer", "false", "if-else", "answer"),
        ("uapp_cycle_mode", "uapp_cycle_reuse_answer", "reuse", "if-else", "answer"),
        ("uapp_cycle_mode", "uapp_cycle_gap_answer", "false", "if-else", "answer"),
    ]
    candidate["edges"].extend(edge(*item) for item in cycle_chain)

    report = {
        "document": {"id": "UAPP_S5_FRESH_FINAL_BUILD_v1.0", "model_calls": 0},
        "base_graph_md5": BASE_GRAPH_MD5,
        "candidate_canonical_sha256": digest(candidate),
        "nodes_before": len(graph["nodes"]), "nodes_after": len(candidate["nodes"]),
        "edges_before": len(graph["edges"]), "edges_after": len(candidate["edges"]),
        "existing_nodes_touched": ["uapp_route"],
        "protected_tool_nodes_unchanged": all(
            canonical(nodes[key]) == canonical({item["id"]: item for item in graph["nodes"]}[key])
            for key in ("uapp_m3", "uapp_hop", "uapp_seam")
        ),
    }
    return candidate, report


def patch_conversation_variables(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = copy.deepcopy(values)
    existing = {item.get("name") for item in result}
    additions = {
        "uapp_publish_binding": "当前测试发布与 conversation artifact 的同任务绑定。",
        "uapp_last_feedback": "本会话最近一条测试反馈记录 id。",
        "uapp_cycle_transition": "本会话最近一次周期转换的幂等绑定。",
    }
    for name, description in additions.items():
        if name in existing:
            continue
        result.append({"id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"diyu:uapp:{name}")),
                       "name": name, "value": "", "value_type": "string",
                       "description": description})
    return result


def database_value(sql: str) -> str:
    import subprocess

    result = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
         "-d", "dify", "-tA", "-c", sql], capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def published_graph() -> dict[str, Any]:
    raw = database_value(
        "select w.graph::text from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{APP_ID}';"
    )
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("choose exactly one of --dry-run or --publish")
    if database_value(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{APP_ID}';"
    ) != BASE_GRAPH_MD5:
        raise RuntimeError("fresh UAPP baseline drift")
    candidate, report = patch_graph(published_graph())
    if args.publish:
        console = DC.Console(env=DC.load_env(ENV_FILE))
        status, draft = console.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
        if status != 200:
            raise RuntimeError((status, draft))
        conversation_variables = patch_conversation_variables(
            draft.get("conversation_variables") or []
        )
        payload = {"graph": candidate, "features": draft.get("features") or {},
                   "hash": draft.get("hash"),
                   "environment_variables": draft.get("environment_variables") or [],
                   "conversation_variables": conversation_variables}
        status, response = console.call(
            "POST", f"/console/api/apps/{APP_ID}/workflows/draft", body=payload, timeout=900
        )
        if status != 200:
            raise RuntimeError((status, response))
        status, response = console.call(
            "POST", f"/console/api/apps/{APP_ID}/workflows/publish",
            body={"marked_name": "fresh-s5-final",
                  "marked_comment": "Fresh baseline S5 equivalence and test writeback successor"},
            timeout=900,
        )
        if status not in (200, 201):
            raise RuntimeError((status, response))
        report["published"] = True
        report["published_graph_md5"] = database_value(
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{APP_ID}';"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
