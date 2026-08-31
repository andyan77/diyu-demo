#!/usr/bin/env python3
"""Create and discriminate the bounded EQUIV/FULL scenario successor."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
PARENT = UAPP_ROOT / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.1.json"
OUTPUT = UAPP_ROOT / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.2.json"
CONTROLS = (
    UAPP_ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "UAPP_S5_FINAL_FIXTURE_CONTROLS_v1.0.json"
)
EXPRESSION_SUBJECT = "由品牌搭配师真实出镜表达"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def turns_by_key(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(turn["key"]): turn for turn in value["turns"]}


def check(checks: list[dict[str, Any]], identifier: str, condition: bool, detail: Any) -> None:
    checks.append({"id": identifier, "result": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        raise RuntimeError(f"{identifier}: {detail}")


def build(parent: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(parent)
    candidate["document"] = {
        **candidate["document"],
        "id": "UAPP_S5_FROZEN_SCENARIOS_v1.2",
        "authority_event": "UAPP_S5_FINAL_TECHNICAL_CONVERGENCE_REBASE_v1.0",
        "parent": "UAPP_S5_FROZEN_SCENARIOS_v1.1",
    }
    candidate["source"] = {
        **candidate["source"],
        "semantic_delta": "NONE",
        "input_delta": (
            "EQUIV a/b/c add one equivalent expression subject; EQUIV n is mechanically "
            "derived from b by deleting expected change only; FULL T1 adds the same subject."
        ),
    }
    turns = turns_by_key(candidate)
    turns["UAPP-EQUIV-01a"]["conversation_group"] = "EQUIV01AV12"
    turns["UAPP-EQUIV-01a"]["query"] = turns["UAPP-EQUIV-01a"]["query"].replace(
        "只讲穿搭方法和真实上身效果，", f"{EXPRESSION_SUBJECT}。只讲穿搭方法和真实上身效果，"
    )
    turns["UAPP-EQUIV-01b"]["conversation_group"] = "EQUIV01BV12"
    b_lines = turns["UAPP-EQUIV-01b"]["query"].splitlines()
    b_lines.insert(4, f'表达主体: "{EXPRESSION_SUBJECT}"')
    turns["UAPP-EQUIV-01b"]["query"] = "\n".join(b_lines)
    turns["UAPP-EQUIV-01c"]["conversation_group"] = "EQUIV01CV12"
    turns["UAPP-EQUIV-01c"]["query"] = turns["UAPP-EQUIV-01c"]["query"].replace(
        '"表达边界":', f'"表达主体": "{EXPRESSION_SUBJECT}", "表达边界":'
    )
    turns["UAPP-EQUIV-01n"]["conversation_group"] = "EQUIV01NV12"
    turns["UAPP-EQUIV-01n"]["query"] = "\n".join(
        line
        for line in turns["UAPP-EQUIV-01b"]["query"].splitlines()
        if not line.startswith("希望她看完明白:")
    )
    turns["UAPP-WITHDRAW-01:W0"]["conversation_group"] = "WITHDRAW01V12"
    turns["UAPP-WITHDRAW-01:W1"]["conversation_group"] = "WITHDRAW01V12"
    turns["UAPP-FULL-01:T1"]["conversation_group"] = "FULL01V12"
    turns["UAPP-FULL-01:T1"]["query"] = turns["UAPP-FULL-01:T1"]["query"].replace(
        "库存充足、可以出镜。内容说给", f"库存充足、可以出镜。这条{EXPRESSION_SUBJECT}。内容说给"
    )
    for key in (
        "UAPP-FULL-01:T2",
        "UAPP-FULL-01:T3",
        "UAPP-FULL-01:T4",
        "UAPP-RECOVERY-01:R1",
    ):
        turns[key]["conversation_group"] = "FULL01V12"
    return candidate


def controls(parent: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    before = turns_by_key(parent)
    after = turns_by_key(candidate)
    check(
        checks,
        "FSC-01_formal_order_unchanged",
        parent["formal_order"] == candidate["formal_order"],
        candidate["formal_order"],
    )
    protected_queries = [
        key
        for key in parent["formal_order"]
        if key
        not in {
            "UAPP-EQUIV-01a",
            "UAPP-EQUIV-01b",
            "UAPP-EQUIV-01c",
            "UAPP-EQUIV-01n",
            "UAPP-FULL-01:T1",
        }
    ]
    check(
        checks,
        "FSC-02_protected_queries_byte_equal",
        all(before[key]["query"] == after[key]["query"] for key in protected_queries),
        protected_queries,
    )
    positives = [after[key]["query"] for key in ("UAPP-EQUIV-01a", "UAPP-EQUIV-01b", "UAPP-EQUIV-01c")]
    check(
        checks,
        "FSC-03_equiv_subject_present_in_all_formats",
        all(EXPRESSION_SUBJECT in query for query in positives),
        [query.count(EXPRESSION_SUBJECT) for query in positives],
    )
    b_lines = after["UAPP-EQUIV-01b"]["query"].splitlines()
    n_lines = after["UAPP-EQUIV-01n"]["query"].splitlines()
    removed = [line for line in b_lines if line not in n_lines]
    added = [line for line in n_lines if line not in b_lines]
    check(
        checks,
        "FSC-04_negative_is_single_variable_deletion",
        len(removed) == 1 and removed[0].startswith("希望她看完明白:") and not added,
        {"removed": removed, "added": added},
    )
    check(
        checks,
        "FSC-05_negative_retains_expression_subject",
        EXPRESSION_SUBJECT in after["UAPP-EQUIV-01n"]["query"],
        after["UAPP-EQUIV-01n"]["query"],
    )
    check(
        checks,
        "FSC-06_full_t1_only_adds_subject",
        after["UAPP-FULL-01:T1"]["query"].replace(f"这条{EXPRESSION_SUBJECT}。", "")
        == before["UAPP-FULL-01:T1"]["query"],
        {"subject": EXPRESSION_SUBJECT},
    )
    check(
        checks,
        "FSC-07_full_t2_t3_t4_recovery_queries_unchanged",
        all(
            before[key]["query"] == after[key]["query"]
            for key in (
                "UAPP-FULL-01:T2",
                "UAPP-FULL-01:T3",
                "UAPP-FULL-01:T4",
                "UAPP-RECOVERY-01:R1",
            )
        ),
        "T2/T3/T4/R1",
    )
    negative_mutation = after["UAPP-EQUIV-01n"]["query"].replace(
        f'表达主体: "{EXPRESSION_SUBJECT}"\n', ""
    )
    check(
        checks,
        "FSC-08_negative_control_detects_second_missing_variable",
        EXPRESSION_SUBJECT not in negative_mutation
        and negative_mutation != after["UAPP-EQUIV-01n"]["query"],
        "remove expression subject",
    )
    format_mutation = positives[2].replace(EXPRESSION_SUBJECT, "品牌负责人")
    check(
        checks,
        "FSC-09_equivalence_control_detects_semantic_format_drift",
        EXPRESSION_SUBJECT not in format_mutation,
        "JSON-like subject changed alone",
    )
    return {
        "document": "UAPP_S5_FINAL_FIXTURE_CONTROLS_v1.0",
        "model_calls": 0,
        "checks": checks,
        "all_pass": all(item["result"] == "PASS" for item in checks),
    }


def main() -> int:
    if OUTPUT.exists() or CONTROLS.exists():
        raise FileExistsError("Fixture successor output already exists")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    candidate = build(parent)
    report = controls(parent, candidate)
    scenario_text = json.dumps(candidate, ensure_ascii=False, indent=2) + "\n"
    report["parent_sha256"] = hashlib.sha256(PARENT.read_bytes()).hexdigest()
    report["scenario_sha256"] = sha256_text(scenario_text)
    OUTPUT.write_text(scenario_text, encoding="utf-8")
    CONTROLS.parent.mkdir(parents=True, exist_ok=True)
    CONTROLS.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scenario_sha256": report["scenario_sha256"], "checks": len(report["checks"]), "all_pass": report["all_pass"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
