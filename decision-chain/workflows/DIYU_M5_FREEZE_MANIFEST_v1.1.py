#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冻结 M5 AC-07 Rebase 的 Candidate Run Manifest v1.1（Gate 2）。

和 v1.0 同一条纪律：**每个值都是现场读出来的**，不从草稿抄。
清单一旦 FROZEN 就不许原地改；要改就出下一个版本。

v1.1 相对 v1.0 的绑定变化：
  - 新增七个 M4 解析 successor（六能力 + 接缝）与一个 M3 恢复权威 successor；
    M4/M3 的源应用**仍然列在清单里并标 protected**，因为「它们没变」本身
    就是本轮要复算的事实；
  - 新增第二份留出保管清单（新鲜留出），旧留出降级为确定性回归；
  - 绑定 Rebase Prompt 与 v1.1 合同的 SHA-256；
  - 记录正式证据的选取规则：只按 Formal Evidence Manifest 的显式路径与 sha256。

拒绝冻结的条件和 v1.0 一样：工作树不干净、Dify 有运行中的工作流、清单已是 FROZEN。
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DOCS = os.path.join(ROOT, "decision-chain", "docs")
V10 = os.path.join(DOCS, "V1_M5_CANDIDATE_RUN_MANIFEST_v1.0.yaml")
V11 = os.path.join(DOCS, "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.2_AC07_REBASE.yaml")
V11_SUPERSEDED = ("V1_M5_CANDIDATE_RUN_MANIFEST_v1.1_AC07_REBASE.yaml（INVALID_BINDING_DEFECT）"
                  " / V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.1_AC07_REBASE.yaml"
                  "（SUPERSEDED：候选运行时在其冻结后发生变化，见下）")
PLAN = "/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning"

RB_PROMPT = "M5_AC07_BLOCKER_REMEDIATION_AND_EVIDENCE_REBASE_EXECUTION_PROMPT_v1.0.md"
RB_CONTRACT = "M5_ENGINEERING_TASK_CONTRACT_v1.1_AC07_REBASE.yaml"


def psql(q, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-t", "-A", "-c", q],
                       capture_output=True, text=True, timeout=180)
    return [l for l in (p.stdout or "").strip().splitlines() if l.strip()]


def sh(cmd):
    return (subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).stdout or "").strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    import yaml
    if os.path.exists(V11):
        m = yaml.safe_load(open(V11, encoding="utf-8"))
        if m.get("status") == "FROZEN":
            print("v1.1 已是 FROZEN。冻结件不得原地修改；要改请出下一个版本。")
            return 2

    dirty = sh(["git", "status", "--porcelain"])
    if dirty:
        print("拒绝冻结：工作树不干净。冻结的必须是一棵确定的树。\n" + dirty[:800])
        return 2
    running = psql("SELECT count(*) FROM workflow_runs WHERE status='running';")
    if running and running[0] not in ("0", ""):
        print("拒绝冻结：Dify 当前有 %s 个运行中的工作流，现场还在变。" % running[0])
        return 2

    base = yaml.safe_load(open(V10, encoding="utf-8"))
    head = sh(["git", "rev-parse", "HEAD"])
    now = psql("SELECT to_char(now() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"');")[0]

    # 用 JSON 取，不用分隔符切。v1.1 曾用 -F "|" 切分，而**七个应用的名字里本身带竖线**
    # （M3 那个就是「… | DIYU-V1-M3-… | CANDIDATE TEST ONLY …」），字段整体错位，
    # 写进冻结件的 graph_md5 是应用名。v1.0 没踩到只是因为它没查 name 列。
    rows = psql("""
        SELECT row_to_json(t) FROM (
          SELECT a.id AS id, a.name AS name, md5(w.graph) AS graph_md5,
                 coalesce(w.marked_name,'') AS marked_name,
                 w.created_at::text AS published_at
          FROM apps a JOIN workflows w ON w.app_id=a.id
          WHERE w.version<>'draft'
            AND w.created_at=(SELECT max(created_at) FROM workflows w2
                              WHERE w2.app_id=a.id AND w2.version<>'draft')) t;""")
    live = {}
    for r in rows:
        try:
            j = json.loads(r)
        except Exception:
            continue
        live[j["id"]] = j

    m4 = json.load(open(os.path.join(ROOT, "decision-chain", "evidence", "m5-rb",
                                     "M4_PARSER_SUCCESSOR_BUILD.json"), encoding="utf-8"))
    m3 = json.load(open(os.path.join(ROOT, "decision-chain", "evidence", "m5-rb",
                                     "M3_RECOVERY_SUCCESSOR_BUILD.json"), encoding="utf-8"))

    apps = []

    def add(app_id, role, protected, note=None):
        if app_id not in live:
            raise RuntimeError("应用没有已发布版本，不能进冻结清单：%s（%s）" % (app_id, role))
        e = {"role": role, "app_id": app_id, "graph_md5": live[app_id]["graph_md5"],
             "app_name": live[app_id]["name"], "published_at": live[app_id]["published_at"],
             "protected": protected}
        if live[app_id]["marked_name"]:
            e["marked_name"] = live[app_id]["marked_name"]
        if note:
            e["note"] = note
        apps.append(e)

    # 受保护面：M4 八个 + M3 源。它们「没变」是本轮要复算的事实，所以必须在清单里。
    for a in base["dify"]["apps"]:
        if a.get("protected"):
            add(a["app_id"], a["role"], True,
                "受保护，本轮零改动；graph_md5 必须仍等于 v1.0 冻结值 %s" % a["graph_md5"])
    # 本轮候选实际调用的 successor
    for cap, v in m4["successors"].items():
        add(v["successor_app"], "M5 RB successor · 能力 %s（只换 envelope_check 的 _find_scalar）" % cap,
            False, "源 %s，patched_node=%s" % (v["source_app"], v["patched_node"]))
    add(m4["seam"]["successor_app"], "M5 RB successor · 统一能力接缝（只把 6 个 tool 节点改指新能力）",
        False, "源 %s，改指 %d 个 tool 节点" % (m4["seam"]["source_app"],
                                             len(m4["seam"]["tool_nodes_remapped"])))
    add(m3["successor_app"], "M5 RB successor · M3 单账号持续运营（恢复状态权威）", False,
        "源 %s，只在 O-11 末尾补 %d 字符" % (m3["source_app"], m3["added_chars"]))
    # M5 自建件沿用 v1.0 的绑定
    for a in base["dify"]["apps"]:
        if not a.get("protected"):
            add(a["app_id"], a["role"], False, a.get("note") or a.get("why_new"))

    out = dict(base)
    out.update({
        "manifest_id": "M5-CANDIDATE-RUN-MANIFEST-v1.1-AC07-REBASE",
        "entry_mode": "REBASE_TASK",
        "supersedes": [
            "V1_M5_CANDIDATE_RUN_MANIFEST_v1.0.yaml（保留不删；原候选 %s 只读留存）"
            % base["git"]["candidate_commit"],
            V11_SUPERSEDED,
            "v1.1.1 被取代的原因：新鲜留出的环境规格要求一个账号上同时存在三个 task "
            "各带一份运行状态，而 v1.1.1 的候选投影只投一个 task —— 这是候选运行时的"
            "真实缺口，由留出的形状在它运行**之前**暴露出来。修投影就是改候选运行时，"
            "按冻结语义必须版本化后重新冻结。v1.1.1 之上的正式运行在 P1 阶段被我主动中止，"
            "未产生任何完成的正式证据。",
        ],
        "parent_candidate": {"commit": base["git"]["candidate_commit"],
                             "frozen_at": base["frozen_at"]},
        "rebase_authority": {
            "prompt": {"path": os.path.join(PLAN, RB_PROMPT), "sha256": sha(os.path.join(PLAN, RB_PROMPT))},
            "contract": {"path": os.path.join(PLAN, RB_CONTRACT),
                         "sha256": sha(os.path.join(PLAN, RB_CONTRACT))},
        },
        "frozen_at": now,
        "frozen_by": "EXECUTION",
        "status": "FROZEN",
    })
    out["git"] = dict(base["git"])
    out["git"].update({"candidate_commit": head,
                       "parent_candidate_commit": base["git"]["candidate_commit"],
                       "origin_main_at_freeze": sh(["git", "rev-parse", "origin/main"])})
    out["dify"] = dict(base["dify"])
    out["dify"]["apps"] = apps
    out["dify"]["binding_switch"] = {
        "env": "M5_BIND", "default": "rb",
        "rb": "本轮候选：M3/M4 的 successor",
        "legacy": "M4 已接受的八个应用与 M3 源，只读、只用于同输入对照",
    }
    out["holdout"] = {
        "regression_custody_manifest": "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.0.yaml",
        "regression_custody_sha256": sha(os.path.join(
            ROOT, "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.0.yaml")),
        "fresh_custody_manifest": "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.1_RB.yaml",
        "fresh_custody_sha256": sha(os.path.join(
            ROOT, "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.1_RB.yaml")),
        "exposed_cases_are_regressions_only": ["HOLDOUT-M5-05", "RISK-M4-030+031"],
        "fresh_holdouts": ["HOLDOUT-M5-RB-01", "HOLDOUT-M5-RB-02"],
        "construction_owner_access_before_this_freeze":
            "IDENTITY_AND_HASH_ONLY_BODIES_PROHIBITED（新鲜留出正文在本次冻结前未被施工侧读取）",
        "unseal_condition": "本清单 FROZEN 之后，由取证执行单元解封",
        "unseal_executed": False,
    }
    out["formal_evidence_selection"] = {
        "rule": "只按 FORMAL_EVIDENCE_MANIFEST_<tag>.json 的显式路径与 sha256 取证据",
        "prohibited": "glob / 排序 / 「最新」「最好」推断",
        "builder_behaviour_without_manifest": "非零退出，不降级为猜",
        "why": "v1.0 的 sorted(glob)[-1] 系统性反选：正式产物带大写 F 标签排在前，"
               "结果索引里绑定的全是冻结前诊断件",
    }
    out["freeze_semantics"] = dict(base.get("freeze_semantics") or {})
    out["freeze_semantics"]["changing_any_binding_after_freeze"] = \
        "本次正式运行降级为探索，受影响验收项置 STALE，必须版本化后重新冻结"

    with open(V11, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, allow_unicode=True, sort_keys=False, width=100)
    print("FROZEN %s" % now)
    print("candidate_commit %s" % head)
    print("apps %d（受保护 %d / RB successor %d / M5 自建 %d）"
          % (len(apps), sum(1 for a in apps if a["protected"]),
             8, sum(1 for a in apps if not a["protected"]) - 8))
    print("SAVED", V11)
    return 0


if __name__ == "__main__":
    sys.exit(main())
