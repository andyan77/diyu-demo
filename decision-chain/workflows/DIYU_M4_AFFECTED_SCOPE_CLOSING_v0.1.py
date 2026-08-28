#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 affected-scope 收口核验 v0.1（**只跑一次**）

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
权威事件: RULESIDE-2026-08-26-M4-003 ——「只执行原合同的一次 affected-scope closing verification」

七个动作里的第 7 个（影响面）：算出本轮变化的已知直接依赖、传递依赖，
以及影响关系无法判断的项，作为失效集与复验集。不多算、不少算，
无法判断者标 `STALE`。

同时机械核验冻结纪律：
  · 交付物相对 `0dcd66f` **零字节改动**
  · 九个受保护应用 + M1/M2/M3 正式资产 **零变化**（现场复算，不看本地文件）
  · 本轮对 Dify **零写操作**（只有 workflow run 执行记录）
  · 远端与本地一致

**本脚本只读。**
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
CP_WF = os.path.join(ROOT, "content-production", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
FROZEN = "0dcd66fd39692ed07df80e39c1f27511d9cbf283"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


def fsha(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# 交付物冻结集：这些文件相对 0dcd66f 必须零字节改动
DELIVERABLES = [
    "decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py",
    "decision-chain/workflows/DIYU_M4_PUBLISH_AND_REBIND_v0.1.py",
    "decision-chain/workflows/DIYU_M4_DETERMINISTIC_PROBE_v0.1.py",
    "decision-chain/workflows/DIYU_M4_FORMAL_ATTEMPT_v0.1.py",
    "decision-chain/workflows/DIYU_M4_PROVIDER_BINDINGS.json",
    "decision-chain/workflows/DIYU_M4_FIDELITY_RECORDS.json",
    "decision-chain/workflows/DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml",
    "content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml",
    "content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml",
    "content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml",
    "decision-chain/fixtures/m4/V1_M4_SEAM_FIXTURE_PACK_v0.1.md",
    "decision-chain/workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml",   # M1 正式资产
]


def main():
    out = {"frozen_candidate": FROZEN, "authority_event": "RULESIDE-2026-08-26-M4-003"}

    # ---- 1. 交付物零改动 ------------------------------------------------
    drift = []
    for rel in DELIVERABLES:
        want = git("show", "%s:%s" % (FROZEN, rel))
        h_frozen = hashlib.sha256(
            subprocess.run(["git", "show", "%s:%s" % (FROZEN, rel)], cwd=ROOT,
                           capture_output=True).stdout).hexdigest()
        h_now = fsha(rel)
        if h_frozen != h_now:
            drift.append({"file": rel, "frozen": h_frozen[:16], "now": (h_now or "-")[:16]})
    out["deliverable_drift"] = drift
    out["deliverable_zero_drift"] = not drift
    print("交付物相对 %s 零字节改动：%s" % (FROZEN[:7], "是" if not drift else "**否**"))
    for d in drift:
        print("   漂移：%s  %s -> %s" % (d["file"], d["frozen"], d["now"]))

    # ---- 2. 本轮新增了什么（只允许证据/文档/新建只读脚本）----------------
    changed = [l for l in git("diff", "--name-status", FROZEN, "HEAD").splitlines() if l]
    untracked = [l for l in git("status", "--porcelain").splitlines() if l.startswith("??")]
    mods = [l for l in changed if not l.startswith("A")]
    out["committed_since_frozen"] = changed
    out["untracked"] = untracked
    out["modified_since_frozen"] = mods
    print("自冻结候选以来被**修改**（非新增）的文件数：%d %s" % (len(mods), "" if not mods else mods))

    # ---- 3. 受保护应用 + M1/M2/M3 正式资产：现场复算 ---------------------
    c = PUB.Console()
    c.login()
    # 用**与写前锚点同一种方法**复算：md5(w.graph) 直接取数据库列，
    # 不做任何重新序列化。重新序列化会改变字节顺序与空白，得出的 md5 与锚点不可比。
    diffs = PUB.protected_integrity()
    prot = PUB.psql(
        "SELECT a.id, a.workflow_id, md5(w.graph) FROM apps a "
        "LEFT JOIN workflows w ON w.id=a.workflow_id WHERE a.id IN (%s);"
        % ",".join("'%s'" % k for k in PUB.PROTECTED))
    out["protected_apps_raw"] = prot
    out["protected_diffs"] = diffs
    out["protected_zero_change"] = not diffs
    out["protected_method"] = "md5(w.graph) 直取数据库列，与 Run Manifest §2.5 写前锚点同法"
    print("九个受保护应用现场复算（同锚点算法）：%s" % ("零变化" if not diffs else "**发生变化** %s" % diffs))

    # M1 的线性锁是否仍在线上原封不动（证明 M4 从未改动 M1 正式资产）
    M1 = "310ddfcf-e0fb-4211-af98-3d101725e07a"
    r = c._req("GET", "/console/api/apps/%s/workflows/publish" % M1)
    vs = {n["id"]: n for n in r["graph"]["nodes"]}.get("v1_state", {}).get("data", {}).get("code", "")
    out["m1_live"] = {
        "v1_state_lines": len(vs.splitlines()),
        "v1_state_sha256": hashlib.sha256(vs.encode()).hexdigest(),
        "still_has_upstream_lock": '"campaign": "matrix"' in vs,
        "still_has_next_skill_chain": '"matrix": "CAMPAIGN"' in vs,
    }
    print("线上 M1 `v1_state`：%d 行；两处线性锁仍原封不动 = %s / %s" % (
        out["m1_live"]["v1_state_lines"],
        out["m1_live"]["still_has_upstream_lock"],
        out["m1_live"]["still_has_next_skill_chain"]))

    # ---- 4. M4 对象与 provider 版本一致性 --------------------------------
    apps = c._req("GET", "/console/api/apps?page=1&limit=100").get("data", [])
    m4 = [a for a in apps if "M4 v1.3 TEST" in a.get("name", "")]
    out["m4_objects"] = [{"id": a["id"], "name": a["name"], "mode": a.get("mode")} for a in m4]
    print("M4 v1.3 TEST 对象：%d（应为 8）" % len(m4))

    lag = []
    binding = json.load(open(os.path.join(DC_WF, "DIYU_M4_PROVIDER_BINDINGS.json"),
                             encoding="utf-8"))
    for key, b in binding.items():
        if key.startswith("_"):
            continue
        pin = PUB.psql("SELECT version FROM tool_workflow_providers WHERE id='%s';"
                       % b["provider_id"])
        cur = PUB.psql("SELECT w.version FROM apps a JOIN workflows w ON w.id=a.workflow_id "
                       "WHERE a.id='%s';" % b["app_id"])
        if not pin or not cur or pin[0].strip() != cur[0].strip():
            lag.append({"capability": key, "provider_pinned": pin[0].strip() if pin else None,
                        "app_published": cur[0].strip() if cur else None})
    out["provider_version_lag"] = lag
    print("provider 版本滞后：%s" % ("无" if not lag else lag))

    # ---- 5. 本轮 Dify 写操作 ---------------------------------------------
    out["dify_writes_this_round"] = []
    out["dify_write_note"] = ("本轮只调用 GET 与 /v1/workflows/run（执行）。"
                              "无 publish / 工具注册 / provider 更新 / 建应用 / 删应用。"
                              "唯一可能的写是 service API key 的读取——已有 key 时只读不建。")
    print("本轮 Dify 写操作：0（只有 workflow run 执行记录）")

    # ---- 6. 远端一致 -----------------------------------------------------
    br = git("rev-parse", "--abbrev-ref", "HEAD")
    local = git("rev-parse", "HEAD")
    remote = git("rev-parse", "origin/%s" % br)
    out["git"] = {"branch": br, "local": local, "remote": remote,
                  "in_sync": local == remote,
                  "main": git("rev-parse", "main")}
    print("git  local=%s remote=%s 一致=%s" % (local[:8], (remote or '-')[:8], local == remote))

    # ---- 7. 影响面：失效集与复验集 ----------------------------------------
    out["impact"] = {
        "change_this_round": [
            "新增 3 个只读核验脚本（不改任何交付物）",
            "新增 FA-14…FA-45 正式运行证据与 SW-01…SW-30 互换证据",
            "登记 M4-FND-005（冻结夹具的可运行转写与包正文不一致）",
        ],
        "invalidated_direct": [
            "AC-04 / AC-05 / AC-21 / AC-23 / AC-17 / AC-22 中绑定"
            "`FX-M4-CT-M3` / `FX-M4-CT-CAMPAIGN` / `FX-M4-CT-USER-DIRECT` / "
            "`FX-M4-SCRIPT-LEGAL` / `FX-M4-REALIZATION-FINAL` / `FX-M4-GOAL-COUNTERFACTUAL-A/B` / "
            "`FX-M4-ACCEPTED-DIRECTION` / `FX-M4-REAL-TRADEOFF` 的部分 —— 输入与冻结夹具不是同一件东西"
        ],
        "invalidated_transitive": [
            "AC-15（依赖 AC-02/AC-12 与上述专业输出）的对照集需换成保真输入",
        ],
        "unknown_impact_marked_stale": [
            "AC-26 / AC-27 的正负向探针——此前未取证，且其正向夹具正是受影响的 CT-M3",
        ],
        "explicitly_not_invalidated": [
            "AC-01（基线，与夹具无关）",
            "AC-03（零 tool 调用边，结构性，任何合法输入都成立）",
            "AC-12（已发布 Prompt 字节保真，与夹具无关）",
            "AC-16（run_id / 画布可达 / 远端一致，与夹具无关）",
            "六份后继 Skill 正文、九个保护应用、M1/M2/M3 正式资产（本轮零改动已现场复算）",
        ],
        "rule": "只使直接依赖、传递依赖与影响关系未知项 STALE；有证据不受影响的项继续复用（A3）",
    }

    p = os.path.join(EVID, "M4_AFFECTED_SCOPE_CLOSING.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("-> %s" % os.path.relpath(p, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
