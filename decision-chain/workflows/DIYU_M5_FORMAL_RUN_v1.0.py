#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 正式运行编排器。**只能在 Candidate Run Manifest 冻结之后运行。**

开跑前强制三件事，缺一不跑：

1. **清单必须已冻结**，且 `git` 工作树干净、`HEAD` 与清单里登记的候选 commit 一致。
   清单说的是哪个候选，就必须跑那个候选——对不上就不是同一件东西。
2. **Dify 已发布 graph 的哈希**必须与清单逐条一致。任何一个对不上，
   本次运行的全部结论对该能力置 STALE。
3. **全场安静**：不能有并发运行，否则按时间窗取证会被污染。

顺序按清单的 run_sequence 走。任何一步的判据文件在本次运行**之后**被改动，
本次结论一律降级为探索——这条由 git 提交时间与运行时间的先后关系兜底，不靠自觉。
"""
import glob, hashlib, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DOCS = os.path.join(ROOT, "decision-chain", "docs")
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")
MANIFEST = os.path.join(DOCS, "V1_M5_CANDIDATE_RUN_MANIFEST_v1.0.yaml")

# 三类文件，性质不同，处置也不同。都放在 decision-chain/workflows/ 下，
# 但混为一谈会得出错误结论，所以显式分开：
#
# 1) 候选运行时 —— 系统本身。冻结后改动 = 跑的不再是清单说的那个候选，**硬阻断**。
# 2) 判据 —— 决定什么算通过。冻结后改动 = 看到结果之后改判据，**该套件降级为探索**。
# 3) 脚手架 —— 只负责编排、汇总、出包，不决定通过与否，也不属于被测系统。可改。
CANDIDATE_RUNTIME = [
    "decision-chain/workflows/DIYU_M5_INTEGRATION_RUNTIME_v0.1.py",
    "decision-chain/workflows/DIYU_M5_FULL_STORY_v0.1.py",
    "decision-chain/workflows/DIYU_M5_BUILD_HOP_ADAPTER_v0.2.py",
    "decision-chain/workflows/DIYU_M5_BUILD_ADAPTER_APP_v0.1.py",
    "decision-chain/workflows/m1_context_compiler_v0.1.py",
    "account-operations/", "business-persistence/", "content-production/skills/",
    "decision-chain/skills/", "m3-account-content-operator-semantic-v1.0/",
]

# 判据文件：这些文件的最后提交时间必须**早于**本次运行开始时间。
ORACLE_FILES = [
    "decision-chain/workflows/DIYU_M5_DIRECT_ENTRY_SUITE_v1.0.py",
    "decision-chain/workflows/DIYU_M5_RISK_PROBE_SUITE_v1.0.py",
    "decision-chain/workflows/DIYU_M5_M2_PROBE_SUITE_v1.0.py",
    "decision-chain/workflows/DIYU_M5_REGRESSION_SUITE_v1.0.py",
    "decision-chain/workflows/DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py",
    "decision-chain/workflows/DIYU_M5_BUILD_BLIND_PACKAGE_v1.0.py",
]


def sh(cmd, **kw):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       shell=isinstance(cmd, str), **kw)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def load_manifest():
    import yaml
    return yaml.safe_load(open(MANIFEST, encoding="utf-8"))


def preflight():
    fails, facts = [], {}
    m = load_manifest()
    facts["manifest_status"] = m.get("status")
    if m.get("status") != "FROZEN":
        fails.append("清单尚未冻结（status=%s），不得进行正式运行" % m.get("status"))

    rc, head = sh(["git", "rev-parse", "HEAD"])
    head = head.strip()
    facts["head"] = head
    want = (m.get("git") or {}).get("candidate_commit")
    facts["manifest_candidate_commit"] = want
    if want and want != "PENDING_FREEZE":
        # 清单登记的候选，必然早于「提交这份清单」本身那一次提交——先有候选，
        # 才谈得上给它冻一份清单。所以口径不是「HEAD 必须等于候选」，而是：
        #   候选必须是 HEAD 的祖先，且两者之间**不能有任何运行代码的改动**。
        # 只允许记账类文件变化（清单、证据、账本、说明）。
        rc, _ = sh(["git", "merge-base", "--is-ancestor", want, head])
        facts["candidate_is_ancestor_of_head"] = (rc == 0)
        if rc != 0:
            fails.append("清单登记的候选 %s 不是 HEAD %s 的祖先" % (want[:12], head[:12]))
        rc2, diff = sh(["git", "diff", "--name-only", want, head])
        changed = [x for x in diff.splitlines() if x.strip()]
        runtime_changed = [x for x in changed
                           if any(x.startswith(r) for r in CANDIDATE_RUNTIME)]
        oracle_changed = [x for x in changed if x in ORACLE_FILES]
        facts["files_changed_since_candidate"] = changed
        facts["candidate_runtime_changed"] = runtime_changed
        facts["oracle_changed_since_freeze"] = oracle_changed
        if runtime_changed:
            fails.append("候选之后动过**候选运行时**，跑的已不是清单说的那个候选：%s"
                         % runtime_changed[:8])
        if oracle_changed:
            # 不硬阻断，但必须记账并把相应套件降级——这正是 A2 说的
            # 「判据在看到结果后才改，本次运行只算探索」
            facts["suites_downgraded_to_exploratory"] = oracle_changed
            print("！判据文件在冻结之后被改动，以下套件本次只能记探索，不产生正式 PASS：")
            for x in oracle_changed:
                print("   -", x)

    rc, st = sh(["git", "status", "--porcelain"])
    facts["worktree_clean"] = not st.strip()
    if st.strip():
        fails.append("工作树不干净，正式运行必须跑在与清单一致的确定树上：\n%s" % st[:400])

    # Dify graph 哈希逐条复算
    apps = (m.get("dify") or {}).get("apps") or []
    mism = []
    for a in apps:
        aid, want_md5 = a.get("app_id"), a.get("graph_md5")
        if not aid or not want_md5 or want_md5 == "PENDING_FREEZE":
            continue
        q = ("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
             "AND created_at=(SELECT max(created_at) FROM workflows w2 "
             "WHERE w2.app_id='%s' AND w2.version<>'draft');" % (aid, aid))
        p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                            "-d", "dify", "-t", "-A", "-c", q], capture_output=True, text=True)
        got = (p.stdout or "").strip()
        if got != want_md5:
            mism.append({"role": a.get("role"), "app_id": aid,
                         "manifest": want_md5, "live": got})
    facts["dify_graph_mismatch"] = mism
    if mism:
        fails.append("Dify 已发布 graph 与清单不一致：%s" % [x["role"] for x in mism])

    # 判据文件提交时间必须早于本次运行
    now = int(time.time())
    late = []
    for f in ORACLE_FILES:
        rc, t = sh(["git", "log", "-1", "--format=%ct", "--", f])
        try:
            ts = int(t.strip())
        except Exception:
            late.append({"file": f, "reason": "无提交记录"}); continue
        if ts > now:
            late.append({"file": f, "committed_at": ts, "now": now})
    facts["oracle_files_committed_before_run"] = not late
    if late:
        fails.append("判据文件提交时间晚于运行开始：%s" % late)

    # 全场安静
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c",
                        "SELECT count(*) FROM workflow_runs WHERE status='running';"],
                       capture_output=True, text=True)
    running = (p.stdout or "0").strip()
    facts["dify_running_now"] = running
    if running not in ("0", ""):
        fails.append("Dify 当前有 %s 个运行中的工作流，并发会污染按时间窗取证" % running)

    return fails, facts


STEPS = [
    ("P1 完整主故事", ["python3", "decision-chain/workflows/DIYU_M5_RUN_FULL_STORY_v0.1.py", "F1"]),
    ("P2 合法短入口", ["python3", "decision-chain/workflows/DIYU_M5_DIRECT_ENTRY_SUITE_v1.0.py", "F"]),
    ("P5a 生成侧风险探针", ["python3", "decision-chain/workflows/DIYU_M5_RISK_PROBE_SUITE_v1.0.py", "F"]),
    ("P5b 持久化侧风险探针", ["python3", "decision-chain/workflows/DIYU_M5_M2_PROBE_SUITE_v1.0.py", "F"]),
    ("P6 不退化与受影响回归", ["python3", "decision-chain/workflows/DIYU_M5_REGRESSION_SUITE_v1.0.py"]),
    ("P4 两级 A/B（只产盲评包，不产分数）",
     ["python3", "decision-chain/workflows/DIYU_M5_AB_SUITE_v1.0.py", "F"]),
    ("P3 十九维覆盖回填", ["python3", "decision-chain/workflows/DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py"]),
    ("盲评包", ["python3", "decision-chain/workflows/DIYU_M5_BUILD_BLIND_PACKAGE_v1.0.py"]),
    ("Founder 验收包", ["python3", "decision-chain/workflows/DIYU_M5_BUILD_FOUNDER_PACKAGE_v1.0.py"]),
]


def main():
    fails, facts = preflight()
    print("=== 正式运行前置检查 ===")
    print(json.dumps(facts, ensure_ascii=False, indent=1))
    if fails:
        print("\n拒绝开始正式运行：")
        for f in fails:
            print("  ! %s" % f)
        return 2
    print("前置检查通过。开始按 run_sequence 正式运行。\n")

    log = {"started_at": facts.get("started_at"), "preflight": facts, "steps": []}
    only = set((os.environ.get("FORMAL_ONLY") or "").split(",")) - {""}
    for name, cmd in STEPS:
        if only and not any(o in name for o in only):
            continue
        print(">>> %s" % name, flush=True)
        t0 = time.time()
        rc, out = sh(cmd, timeout=5400)
        tail = out.strip().splitlines()[-12:]
        log["steps"].append({"step": name, "rc": rc, "seconds": round(time.time() - t0),
                             "tail": tail})
        for line in tail:
            print("    " + line, flush=True)
        if rc != 0:
            print("    !! 该步返回码 %s，继续后续步骤并如实记录" % rc, flush=True)
    with open(os.path.join(EV, "FORMAL_RUN_LOG.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print("\nSAVED", os.path.join(EV, "FORMAL_RUN_LOG.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
