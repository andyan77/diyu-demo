#!/usr/bin/env python3
"""Zero-model controls for the single shared human-delivery source."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_4_HUMAN_DELIVERY.yml",
    ROOT / "decision-chain/workflows/DIYU_M4_TOOL_CAMPAIGN_v1_4_HUMAN_DELIVERY.yml",
    ROOT / "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_4_HUMAN_DELIVERY.yml",
    ROOT / "content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_4_HUMAN_DELIVERY.yml",
    ROOT / "content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_4_HUMAN_DELIVERY.yml",
    ROOT / "content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4_HUMAN_DELIVERY.yml",
]


def main() -> int:
    codes, report = [], []
    forbidden = ("这一步我还差一样东西", "只补这一项就够了", "不依赖这一步", "status: READY")
    leaks = ("PASS", "FAIL", "READY_WITH_CONDITIONS", "precise_gap", "capability_call",
             "professional_input", "returns_json", "uapp_")
    for path in FILES:
        dsl = yaml.safe_load(path.read_text(encoding="utf-8"))
        nodes = {n["id"]: n for n in dsl["workflow"]["graph"]["nodes"]}
        code = nodes["component_return"]["data"]["code"]
        ns: dict[str, object] = {}
        exec(code, ns)
        ret = ns["main"]("INPUT_INSUFFICIENT", "", ["expression_subject_and_boundary"],
                          "ENTRY-03", "abc123", "`expected_change`: 观众知道怎么搭配")
        text = ret["user_delivery"]
        report.append({"file": str(path.relative_to(ROOT)),
                       "old_template_absent": not any(word in code for word in forbidden),
                       "one_question": text.count("？") == 1,
                       "context_continuation": "已经记住" in text,
                       "internal_leaks_absent": not any(word in text for word in leaks),
                       "machine_schema_present": all(k in ret for k in ("returns_json", "single_most_discriminating_question"))})
        codes.append(code)
    all_same_source = len({code.replace('CAPABILITY = "MATRIX"', 'CAPABILITY = "X"')
                           .replace('CAPABILITY = "CAMPAIGN"', 'CAPABILITY = "X"')
                           .replace('CAPABILITY = "CONTENT_BRIEF"', 'CAPABILITY = "X"')
                           .replace('CAPABILITY = "CREATIVE_SCRIPT"', 'CAPABILITY = "X"')
                           .replace('CAPABILITY = "PRODUCTION_DIRECTOR"', 'CAPABILITY = "X"')
                           .replace('CAPABILITY = "PUBLISHING_PACKAGING"', 'CAPABILITY = "X"')
                           .replace('LAYER = "MATRIX_INPUT_SUFFICIENCY"', 'LAYER = "X"')
                           .replace('LAYER = "CAMPAIGN_INPUT_SUFFICIENCY"', 'LAYER = "X"')
                           .replace('LAYER = "CONTENT_BRIEF_INPUT_SUFFICIENCY"', 'LAYER = "X"')
                           .replace('LAYER = "CREATIVE_SCRIPT_INPUT_SUFFICIENCY"', 'LAYER = "X"')
                           .replace('LAYER = "PRODUCTION_DIRECTOR_INPUT_SUFFICIENCY"', 'LAYER = "X"')
                           .replace('LAYER = "PUBLISHING_PACKAGING_INPUT_SUFFICIENCY"', 'LAYER = "X"')
                           for code in codes}) == 1
    ok = all(all(v for k, v in item.items() if k != "file") for item in report) and all_same_source
    print(json.dumps({"document": "DIYU_M4_HUMAN_DELIVERY_DETERMINISTIC_CONTROLS_v1.0",
                      "model_calls": 0, "six_apps": report,
                      "single_shared_source": all_same_source,
                      "summary": "PASS" if ok else "FAIL"}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
