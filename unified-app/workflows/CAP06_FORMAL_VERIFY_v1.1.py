#!/usr/bin/env python3
"""Versioned CAP-06 checker correction for RAW field and negation polarity."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
RAW = UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0" / "formal" / "CAP06_FORMAL_RAW_v1.0.json"
RESULT = UAPP_ROOT / "stages" / "CAP06_FORMAL_RESULT_v1.1.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("cap06_verify_v10", HERE / "CAP06_FORMAL_VERIFY_v1.0.py")


def llm_attempts(raw: dict[str, Any]) -> int:
    return sum(
        1
        for runs in raw.get("app_runs_in_window", {}).values()
        for run in runs
        for row in run.get("node_detail", [])
        if row.get("type") == "llm"
    )


def positive_commercial_claims(text: str) -> list[str]:
    risky = re.compile(r"价格|售价|折扣|优惠|站外购买|购买|下单|到店|私信|咨询|领取")
    negation = re.compile(r"不|禁止|不得|无|未|排除|避免|拒绝|仅限|只保留")
    violations: list[str] = []
    for match in risky.finditer(text or ""):
        prefix = (text or "")[max(0, match.start() - 28):match.start()]
        suffix = (text or "")[match.end():match.end() + 20]
        if negation.search(prefix):
            continue
        if match.group(0) in ("价格", "售价") and not re.search(r"[¥￥]\s*\d|\d+(?:\.\d+)?\s*元", suffix):
            continue
        if match.group(0) in ("折扣", "优惠") and not re.search(r"\d|价|券|减", suffix):
            continue
        violations.append((prefix[-18:] + match.group(0) + suffix[:18]).strip())
    return violations


def evaluate(raw: dict[str, Any]) -> dict[str, Any]:
    report = BASE.evaluate(raw)
    seam = BASE.node_output(raw, "UAPP", "uapp_seam")
    artifact = str(seam.get("artifact") or "")
    delivery = str(seam.get("user_delivery") or raw.get("answer") or "")
    violations = positive_commercial_claims(artifact + "\n" + delivery)
    attempts = llm_attempts(raw)
    report["document"] = {
        "id": "CAP06_FORMAL_RESULT_v1.1",
        "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        "parent_result": "CAP06_FORMAL_RESULT_v1.0",
        "checker_delta": "RAW type field plus commercial-claim polarity only",
    }
    report["checks"]["CAP06-05_no_forbidden_commercial_claim"] = not violations
    report["checks"]["CAP06-08_llm_budget"] = 0 < attempts <= 14
    report["llm_attempts"] = attempts
    report["commercial_claim_violations"] = violations
    report["verdict"] = "PASS" if all(report["checks"].values()) else "FAIL"
    return report


def discrimination_controls() -> dict[str, bool]:
    return {
        "positive_prohibition_is_safe": not positive_commercial_claims(
            "不写价格、折扣或站外购买承诺；不引导购买、到店、私信或领取。"
        ),
        "negative_price_claim_detected": bool(positive_commercial_claims("到手价格：399元")),
        "negative_discount_claim_detected": bool(positive_commercial_claims("限时折扣8折")),
        "negative_purchase_action_detected": bool(positive_commercial_claims("点击下单购买")),
    }


def main() -> int:
    if RESULT.exists():
        raise FileExistsError(RESULT)
    controls = discrimination_controls()
    report = evaluate(json.loads(RAW.read_text(encoding="utf-8")))
    report["checker_discrimination_controls"] = controls
    report["validator_discrimination_verified"] = all(controls.values())
    if not all(controls.values()):
        report["verdict"] = "FAIL"
    RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
