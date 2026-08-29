#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冻结 M5 最后一轮最小修复的 Candidate Run Manifest v1.1.4（Step 4）。

纪律与 v1.0/v1.1 相同：**每个值都是现场读出来的**，不从草稿抄；
清单一旦 FROZEN 就不许原地改，要改就出下一个版本。

拒绝冻结的条件：工作树不干净、Dify 有运行中的工作流、目标清单已存在。
"""
import hashlib, importlib.util, json, os, subprocess, sys
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DOCS = os.path.join(ROOT, "decision-chain", "docs")
OUT = os.path.join(DOCS, "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.4_FINAL_P0.yaml")

PROMPTS = {
    "final_p0_prompt": "/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/M5_FINAL_MINIMAL_P0_REMEDIATION_AND_NEXT_STAGE_EXECUTION_PROMPT_v1.0.md",
    "parent_prompt": "/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/M5_AC07_BLOCKER_REMEDIATION_AND_EVIDENCE_REBASE_EXECUTION_PROMPT_v1.0.md",
    "parent_contract": "/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/M5_ENGINEERING_TASK_CONTRACT_v1.1_AC07_REBASE.yaml",
}
HANDOFF = ["decision-chain/docs/V1_M5_RB3_DIRECTED_REVERIFICATION_v1.0.md",
           "decision-chain/docs/V1_M5_RB_HOLDOUT_VERDICT_v1.0.md",
           "decision-chain/docs/V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.3_AC07_REBASE.yaml"]
REPO_FILES = ["decision-chain/docs/V1_M5_FINAL_P0_FAILURE_TRIAGE_v1.0.md",
              "decision-chain/evidence/m5/FINAL_P0_TRIAGE_NODE_BINDING.json",
              "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.2_FINAL_P0.yaml",
              "decision-chain/workflows/DIYU_M5_BUILD_M3_FINAL_P0_SUCCESSOR_v1.2.py",
              "decision-chain/workflows/DIYU_M5_BUILD_CAPABILITY_FINAL_P0_SUCCESSOR_v1.2.py",
              "decision-chain/workflows/DIYU_M5_INTEGRATION_RUNTIME_v0.1.py"]


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def psql(q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", q], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:300])
    return p.stdout.strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def app_facts(app_id):
    md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
               "ORDER BY created_at DESC LIMIT 1;" % app_id)
    g = json.loads(psql("SELECT graph FROM workflows WHERE app_id='%s' AND version<>'draft' "
                        "ORDER BY created_at DESC LIMIT 1;" % app_id))
    models = []
    for n in g.get("nodes", []):
        d = n.get("data") or {}
        if d.get("type") == "llm":
            m = d.get("model") or {}
            models.append({"node": n["id"], "provider": m.get("provider"), "name": m.get("name"),
                           "mode": m.get("mode"),
                           "completion_params": m.get("completion_params") or {}})
    name = psql("SELECT name FROM apps WHERE id='%s';" % app_id)
    return {"app_id": app_id, "app_name": name, "graph_md5": md5,
            "node_count": len(g.get("nodes", [])), "llm_models": models}


def main():
    if os.path.exists(OUT):
        print("BLOCKED: 目标清单已存在，不原地改。要改出下一个版本。", file=sys.stderr)
        return 2
    dirty = sh("git status --porcelain")
    if dirty:
        print("BLOCKED: 工作树不干净：\n" + dirty, file=sys.stderr)
        return 3
    running = psql("SELECT count(*) FROM workflow_runs WHERE status='running';")
    if running != "0":
        print("BLOCKED: Dify 有 %s 个运行中的工作流" % running, file=sys.stderr)
        return 4

    rt = importlib.util.spec_from_file_location(
        "rt", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_INTEGRATION_RUNTIME_v0.1.py"))
    RT = importlib.util.module_from_spec(rt); rt.loader.exec_module(RT)
    assert RT.BIND_NAME == "fp", "默认绑定必须是 fp，实得 %s" % RT.BIND_NAME

    custody = yaml.safe_load(open(os.path.join(
        ROOT, "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.2_FINAL_P0.yaml"),
        encoding="utf-8"))

    out = {
        "manifest_id": "M5-CANDIDATE-RUN-MANIFEST-v1.1.4-FINAL-P0",
        "task_id": "DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001",
        "entry_mode": "REBASE_TASK",
        "step": "STEP_4_FREEZE_FINAL_CANDIDATE",
        "status": "FROZEN",
        "frozen_at": sh("date -u +%Y-%m-%dT%H:%M:%SZ"),
        "supersedes": "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.3_AC07_REBASE.yaml"
                      "（保留不删，只读留存；其证据与判定不回改）",

        "authority": {k: {"path": v, "sha256": sha(v)} for k, v in PROMPTS.items()},
        "handoff_evidence": {os.path.basename(p): {"path": p, "sha256": sha(os.path.join(ROOT, p))}
                             for p in HANDOFF},
        "repo_binding": {os.path.basename(p): {"path": p, "sha256": sha(os.path.join(ROOT, p))}
                         for p in REPO_FILES},

        "git": {
            "branch": sh("git rev-parse --abbrev-ref HEAD"),
            "candidate_commit": sh("git rev-parse HEAD"),
            "candidate_commit_subject": sh("git log -1 --pretty=%s"),
            "worktree_clean": True,
            "origin_main": sh("git rev-parse origin/main"),
            "remote_reachable": bool(sh("git ls-remote origin -h refs/heads/main 2>/dev/null")),
            "remote_note": "远端不可达时只记 NOT_VERIFIED(INPUT_ENVIRONMENT_OR_TOOL)，不伪造状态。",
        },

        "runtime_binding": {
            "env": "M5_BIND", "default": RT.BIND_NAME,
            "accepted_values": ["fp", "rb", "legacy"],
            "fp_note": "本轮候选。rb 与 legacy 一个字节都不动，继续可用于同输入新旧对照。",
            "apps": {},
        },

        "modified_successors": {},
        "protected_source_apps": {},

        "fresh_holdouts": {
            "custody_manifest": "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.2_FINAL_P0.yaml",
            "custody_manifest_sha256": sha(os.path.join(
                ROOT, "decision-chain/fixtures/V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.2_FINAL_P0.yaml")),
            "custodian": custody["custodian"],
            "items": [{"id": h["id"], "body_sha256": h["body_sha256"], "body_bytes": h["body_bytes"],
                       "scope": h["scope"]} for h in custody["holdouts"]],
            "sealed_oracles_sha256": custody["sealed_oracles_sha256"],
            "bodies_included_here": False,
            "construction_owner_access": custody["construction_owner_access"],
            "unseal_condition": "本清单 status=FROZEN 且 worktree clean 之后方可解封；"
                                "解封时现场复算三个文件 sha256 与保管清单逐条一致。",
        },

        "allowed_reverification_only": [
            "R1 Group A/B 最小单元的正例、负例与原失败回归（确定性，已在 Step 3 完成一轮）",
            "R2 HOLDOUT-M5-RB-01 / HOLDOUT-M5-RB-02 / HOLDOUT-M5-05 重跑",
            "R3 候选冻结后解封并各运行一次 FINAL-P0-HOLDOUT-01 / 02",
            "R4 RISK-M4-030+031 按新判据运行一次四形式检查",
            "R5 一条完整输入的 M3→M4 正常主路径（证明没有把正常业务误挡）",
            "R6 被修改文件/图的直接确定性测试与必要回归",
            "R7 机械重算十九维索引与 AC 状态（不新增十九维案例）",
        ],
        "reuse_without_rerun": [
            "FULL-02、纯 M1/M2、十类短入口中无依赖项、M2 3/3、REG-M4-01 8/8",
            "理由：这些不经过本轮被改的 M3 successor 与六能力/接缝 successor，依赖边不成立。",
        ],
        "ab_dependency_judgment": {
            "conclusion": "AFFECTED_MUST_REBUILD",
            "reason": "AB-M3-01 的 B 组直接调用 M3_APP；AB-FINAL-01 的 B 组走完整链路，"
                      "经过接缝与能力应用。三者在本轮全部被替换为 fp successor，"
                      "评分文本因此受影响。",
            "action": "只重建受影响的 A/B 案例并生成新 sealed mapping；"
                      "旧盲评包 AB_BLIND_abFRB3.json 与 AB_MAPPING_SEALED_abFRB3.json "
                      "原样保留并标 STALE / INVALID_FOR_FINAL_SCORING，不删除、不覆盖。",
            "sealed_mapping_rule": "评分完成前不得打开任何 sealed mapping。",
        },

        "no_overwrite_rules": [
            "历史运行、原留出、原判定、原 Manifest、原盲评包与全部失败记录只增不覆盖",
            "证据文件名必须带 run_tag；不带标签的复验会覆盖正式证据（已发生过一次事故）",
            "rb 与 legacy 绑定的应用一个字节都不动",
            "六份受保护 Skill、M1–M4 已发布应用、M3 已冻结闸门不得修改",
        ],
        "prohibited": {
            "force_push": "PROHIBITED", "remote_branch_delete": "PROHIBITED",
            "real_external_publish": "NOT_AUTHORIZED", "destructive_migration": "PROHIBITED",
            "non_test_data_mutation": "PROHIBITED", "silent_model_substitution": False,
            "new_full_formal_round": "NOT_AUTHORIZED",
            "main_merge": "NOT_ALLOWED_UNTIL_ALL_HARD_GATES_PASS_AND_FOUNDER_ACCEPTS",
        },
        "task_state": {"task_progress": "IN_PROGRESS", "terminal_state": None,
                       "partial_is_not_legal_terminal_for_m5": True},
    }

    for role, app_id in sorted(RT._BIND.items()):
        out["runtime_binding"]["apps"][role] = app_id
        out["modified_successors"][role] = app_facts(app_id)
    for role, app_id in sorted(RT.RB_BIND.items()):
        out["protected_source_apps"]["rb_" + role] = {"app_id": app_id,
                                                      "graph_md5": psql(
            "SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
            "ORDER BY created_at DESC LIMIT 1;" % app_id)}
    for role, app_id in sorted(RT.LEGACY_BIND.items()):
        out["protected_source_apps"]["legacy_" + role] = {"app_id": app_id,
                                                          "graph_md5": psql(
            "SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
            "ORDER BY created_at DESC LIMIT 1;" % app_id)}

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(out, f, allow_unicode=True, sort_keys=False, width=100)
    print("FROZEN", OUT)
    print("candidate_commit =", out["git"]["candidate_commit"])
    print("fp 应用数 =", len(out["runtime_binding"]["apps"]))
    print("sha256 =", sha(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
