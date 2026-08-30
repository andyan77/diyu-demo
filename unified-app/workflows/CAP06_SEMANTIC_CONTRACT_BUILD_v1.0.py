#!/usr/bin/env python3
"""Build/publish the bounded UAPP + PP CAP-06 deterministic seam candidate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
REPO = UAPP_ROOT.parent
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
PP_APP_ID = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
BASE_UAPP_MD5 = "07ea334bfcbe6e87ba8c5cd5d5dac380"
BASE_PP_MD5 = "8366328bf827bd0f460455d750d45c4f"
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0" / "build.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("cap06_base", HERE / "UAPP_S5_INLINE_ARTIFACT_BUILD_v1.0.py")
NODES = load_module("cap06_nodes", HERE / "CAP06_SEMANTIC_CONTRACT_NODES_v1.0.py")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def graph_md5(app_id: str) -> str:
    return BASE.psql(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{app_id}';"
    )


def published_graph(app_id: str) -> dict[str, Any]:
    value = json.loads(
        BASE.psql(
            "select w.graph from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{app_id}';"
        )
    )
    if not isinstance(value, dict):
        raise RuntimeError(f"Graph is not an object: {app_id}")
    return value


def patch_uapp(graph: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    nodes = {node["id"]: node for node in candidate["nodes"]}
    inline = nodes["uapp_inline_artifact"]["data"]
    start = inline["code"].index("def _companions(")
    end = inline["code"].index("def _result(", start)
    inline["code"] = (
        inline["code"][:start]
        + NODES.INLINE_COMPANION_FUNCTION.strip()
        + "\n\n\n"
        + inline["code"][end:]
    )
    inline["desc"] = "同轮成片正文、兑现点、平台与 CTA 授权同源规范化；不代写 CTA、不自动持久化"

    fields = nodes["uapp_fields"]["data"]
    new_request_check = '''                elif companion_record.get("artifact_bfp") != sbfp:
                    reason = "COMPANION_BFP_MISMATCH"
                elif companion_record.get("request_bfp") and \\
                        companion_record.get("request_bfp") != _fp(_norm(uq)):
                    reason = "COMPANION_REQUEST_BFP_MISMATCH"
                elif not isinstance(raw_values, dict):
                    reason = "COMPANION_VALUES_INVALID"
                else:
                    allowed = ("content.origin_mode", "content.promise", "cta.contract",
                               "delivery.platform")
                    for cid, val in raw_values.items():
                        if cid in allowed and isinstance(val, str) and _norm(val):
                            companion_values[cid] = _norm(val)
                    derived_values = companion_record.get("derived_values") or {}
                    for cid, item in derived_values.items():
                        if not isinstance(item, dict):
                            continue
                        source_excerpt = _norm(item.get("source_excerpt") or "")
                        rule = item.get("derivation_rule") or ""
                        value = _norm(item.get("value") or "")
                        if cid == "cta.level" and value == "LOW_RISK_INTERACTION" and \\
                                rule == "NATURAL_CTA_WITH_COMMERCIAL_EXCLUSIONS" and \\
                                source_excerpt and source_excerpt in _norm(uq) and \\
                                re.search(r"自然\\s*CTA|自然引导语|自然互动", uq or "") and \\
                                re.search(r"不(?:写|做|包含|承诺)[^。！？]*(?:价格|折扣)"
                                          r"[^。！？]*(?:站外|购买|成交|下单)", uq or ""):
                            companion_values[cid] = value
                    missing_companions = [cid for cid in required
                                          if cid not in companion_values]
                    unsupported = [cid for cid, val in companion_values.items()
                                   if cid != "cta.level" and _norm(val) not in _norm(uq)]
                    if missing_companions:
                        reason = "COMPANION_MISSING:" + ",".join(missing_companions)
                    elif unsupported:
                        reason = "COMPANION_UNSUPPORTED:" + ",".join(unsupported)
'''
    check_start = fields["code"].index(
        '                elif companion_record.get("artifact_bfp") != sbfp:'
    )
    check_end = fields["code"].index("        else:\n            if scap", check_start)
    fields["code"] = (
        fields["code"][:check_start] + new_request_check + fields["code"][check_end:]
    )
    fields["desc"] = "同源复核完整正文、兑现点、平台和 CTA 授权；原文不自动持久化"

    after = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        node_id for node_id in before if canonical(before[node_id]) != canonical(after[node_id])
    )
    if touched != ["uapp_fields", "uapp_inline_artifact"]:
        raise RuntimeError(f"Unexpected UAPP impact: {touched}")
    return candidate, touched


def patch_pp(graph: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    node = next(item for item in candidate["nodes"] if item["id"] == "envelope_check")
    data = node["data"]
    code = data["code"]
    old_required = (
        'REQUIRED = ["content_body_or_beats", "content_promise", '
        '"explicit_non_promise", "facts_registered", "cta_contract", '
        '"asset_publish_permission"]'
    )
    if code.count(old_required) != 1:
        raise RuntimeError("PP REQUIRED anchor mismatch")
    code = code.replace(old_required, NODES.PP_REQUIRED, 1)
    old_cta = '''    cta_level = (_find_scalar(blob, "cta_level") or _find_scalar(blob, "cta_contract") or "").upper()
    if cta_level not in CTA_LEVELS:
        cta_level = "NO_CTA"
'''
    if code.count(old_cta) != 1:
        raise RuntimeError("PP CTA resolution anchor mismatch")
    code = code.replace(old_cta, NODES.PP_CTA_RESOLUTION + "\n", 1)
    old_conditional = '''    if vacuity_flags:
        conditionalized.append("疑似语义单薄项：%s" % ", ".join(vacuity_flags))
'''
    new_conditional = old_conditional + '''    if cta_policy_status != "AUTHORIZED":
        conditionalized.append(cta_policy_note)
'''
    if code.count(old_conditional) != 1:
        raise RuntimeError("PP conditionalization anchor mismatch")
    code = code.replace(old_conditional, new_conditional, 1)
    old_return = '''        "cta_level": cta_level,
        "source_kind": source_kind,
'''
    new_return = '''        "cta_level": cta_level,
        "cta_level_requested": cta_requested,
        "cta_policy_status": cta_policy_status,
        "cta_policy_note": cta_policy_note,
        "source_kind": source_kind,
'''
    if code.count(old_return) != 1:
        raise RuntimeError("PP return anchor mismatch")
    data["code"] = code.replace(old_return, new_return, 1)
    for output in ("cta_level_requested", "cta_policy_status", "cta_policy_note"):
        data["outputs"][output] = {"children": None, "type": "string"}
    data["desc"] = "结构充分性、CTA 局部授权与绑定计算；CTA 缺口不阻断无依赖包装"
    after = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        node_id for node_id in before if canonical(before[node_id]) != canonical(after[node_id])
    )
    if touched != ["envelope_check"]:
        raise RuntimeError(f"Unexpected PP impact: {touched}")
    return candidate, touched


def llm_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [node for node in graph["nodes"] if node.get("data", {}).get("type") == "llm"]


def publish(app_id: str, graph: dict[str, Any], label: str) -> dict[str, Any]:
    console = BASE.DC.Console(env=BASE.DC.load_env(ENV_FILE))
    draft = BASE.console_call(console, "GET", f"/console/api/apps/{app_id}/workflows/draft")
    BASE.console_call(
        console,
        "POST",
        f"/console/api/apps/{app_id}/workflows/draft",
        {
            "graph": graph,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or [],
        },
    )
    readback = BASE.console_call(console, "GET", f"/console/api/apps/{app_id}/workflows/draft")
    if canonical(readback["graph"]) != canonical(graph):
        raise RuntimeError(f"Draft readback differs: {app_id}")
    return BASE.console_call(
        console,
        "POST",
        f"/console/api/apps/{app_id}/workflows/publish",
        {"marked_name": label, "marked_comment": "CAP-06 semantic contract and local CTA sufficiency"},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if graph_md5(UAPP_APP_ID) != BASE_UAPP_MD5 or graph_md5(PP_APP_ID) != BASE_PP_MD5:
        raise RuntimeError("Published candidate differs from frozen CAP-06 predecessor")
    if int(BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    uapp, uapp_touched = patch_uapp(published_graph(UAPP_APP_ID))
    pp, pp_touched = patch_pp(published_graph(PP_APP_ID))
    report: dict[str, Any] = {
        "document": {"id": "CAP06_SEMANTIC_CONTRACT_BUILD_v1.0", "model_calls": 0},
        "base": {"UAPP": BASE_UAPP_MD5, "PP": BASE_PP_MD5},
        "touched": {"UAPP": uapp_touched, "PP": pp_touched},
        "candidate": {
            "UAPP_canonical_sha256": sha256_text(canonical(uapp)),
            "PP_canonical_sha256": sha256_text(canonical(pp)),
            "UAPP_node_count": len(uapp["nodes"]),
            "PP_node_count": len(pp["nodes"]),
        },
        "protected": {
            "PP_professional_prompt_unchanged": canonical(
                llm_nodes(published_graph(PP_APP_ID))
            ) == canonical(llm_nodes(pp)),
            "conversation_variables_added": [],
        },
        "published": False,
    }
    if args.publish:
        report["publish_response"] = {
            "UAPP": publish(UAPP_APP_ID, uapp, "cap06-contract-v1"),
            "PP": publish(PP_APP_ID, pp, "cap06-shell-v1"),
        }
        report["published"] = True
        report["published_graph_md5"] = {
            "UAPP": graph_md5(UAPP_APP_ID),
            "PP": graph_md5(PP_APP_ID),
        }
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("%s", OUTPUT)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
