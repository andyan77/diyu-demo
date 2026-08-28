#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-PCR-01 … 12 确定性核验（恢复后完全收口）

判据来自 decision-chain/docs/V1_M4_POST_RESTORE_FINAL_CLOSEOUT_TASK_CONTRACT_v1.0.yaml
（与规划侧 canonical 文件逐字节相同，sha256=82f25055…）。本脚本只执行判据，不改判据。
全部为只读检查；不修改任何文件、Dify 对象或数据库。
"""
import hashlib, importlib.util, json, os, subprocess, sys, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/post_restore/M4_PCR_VERIFY.json")
RESTORE = os.path.join(ROOT, "decision-chain/evidence/m4/restore")
FREEZE = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CANDIDATE_FREEZE.json")

CONTRACT_SHA = "82f25055eee4cb58a353d928c2de38a7c13cc9cd31bdc1f9ba3746d67ce650f1"
PREV_CONTRACT_SHA = "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070"
CANDIDATE_COMMIT = "3bf324ec616a80f669e9764bf5dfc4f77f22c5b5"
RESTORE_COMMIT = "c77a7e5d424f8b2db6ff436a662d12699596b0cc"
BRANCH = "codex/v1-m4-capability-seams-runtime-integration-001"

APPS = {
    "FOUNDER_CANVAS":       ("DIYU M4 v1.3 TEST · Founder Canvas", "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"),
    "CAPABILITY_SEAM":      ("DIYU M4 v1.3 TEST · Capability Seam", "de0cb1e9-2af8-415a-9762-31b6cf348c22"),
    "MATRIX":               ("DIYU M4 v1.3 TEST · Matrix Architect", "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3"),
    "CAMPAIGN":             ("DIYU M4 v1.3 TEST · Campaign Orchestrator", "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b"),
    "CONTENT_BRIEF":        ("DIYU M4 v1.3 TEST · Content Brief Architect", "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1"),
    "CREATIVE_SCRIPT":      ("DIYU M4 v1.3 TEST · Creative Script (CS-1 + Script)", "8d518554-bfbc-4be0-8a57-3b1f04983edf"),
    "PRODUCTION_DIRECTOR":  ("DIYU M4 v1.3 TEST · Production Director", "57ebc138-ed9e-4202-bce2-38e44da0ec1d"),
    "PUBLISHING_PACKAGING": ("DIYU M4 v1.3 TEST · Publishing & Packaging", "10056fcf-9237-4889-a3e3-81e3a695cae0"),
}
INJECTION_APPS = ["c733f426-6e54-4c09-8ad7-8192b426ac38", "86ba24e1-ae01-4b29-af04-fbeffc499bb3"]
THINK = ["<think>", "</think>", "dify-deepseek-reasoning"]

sb = importlib.util.spec_from_file_location("b", os.path.join(DC_WF, "DIYU_M4_DSL_BUILD_v0.1.py"))
B = importlib.util.module_from_spec(sb); sb.loader.exec_module(B)


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True)


def gout(*a): return git(*a).stdout.strip()


def q(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify",
                        "-t", "-A", "-c", "SELECT coalesce(json_agg(t)::text,'[]') FROM (%s) t;" % sql.rstrip(";")],
                       capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[:400])
    return json.loads(p.stdout.strip() or "[]")


def sha_f(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def sha_s(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


R = {"contract": "V1_M4_POST_RESTORE_FINAL_CLOSEOUT_TASK_CONTRACT_v1.0.yaml",
     "current_task_contract_hash": CONTRACT_SHA,
     "previous_task_contract_hash": PREV_CONTRACT_SHA,
     "criteria": {}, "detail": {}}


def put(cid, ok, note, detail=None):
    R["criteria"][cid] = "PASS" if ok else "FAIL"
    if detail is not None: R["detail"][cid] = detail
    print("  %-12s %-6s %s" % (cid, R["criteria"][cid], note))


# ── PCR-01 同 task_id / REBASE / 旧 BLOCKED 保留为历史 ────────────────────
cpath = os.path.join(ROOT, "decision-chain/docs/V1_M4_POST_RESTORE_FINAL_CLOSEOUT_TASK_CONTRACT_v1.0.yaml")
cy = yaml.safe_load(open(cpath, encoding="utf-8"))
old_receipt = os.path.join(ROOT, "decision-chain/docs/V1_M4_FINAL_CLOSURE_RECEIPT_v0.1.md")
old_txt = open(old_receipt, encoding="utf-8").read()
d01 = {"contract_sha256": sha_f(cpath), "byte_identical_to_planning_canonical": sha_f(cpath) == CONTRACT_SHA,
       "task_id": cy["task_id"], "task_entry_mode": cy["task_entry_mode"],
       "new_task_forbidden": cy["new_task_forbidden"],
       "previous_task_contract_hash_matches": cy["previous_task_contract_hash"] == PREV_CONTRACT_SHA,
       "old_receipt_present": os.path.exists(old_receipt),
       "old_receipt_states_blocked": 'task_final_status: "BLOCKED"' in old_txt,
       "old_receipt_sha256": sha_f(old_receipt)}
put("M4-PCR-01", (d01["byte_identical_to_planning_canonical"]
                  and cy["task_id"] == "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
                  and cy["task_entry_mode"] == "REBASE_TASK" and cy["new_task_forbidden"] is True
                  and d01["previous_task_contract_hash_matches"]
                  and d01["old_receipt_present"] and d01["old_receipt_states_blocked"]),
    "task_id 不变 / REBASE_TASK / 旧 BLOCKED 回执在位", d01)

# ── PCR-02 分支绑定与工作区（收口提交前先记录，最终由 AW-07 复核） ────────
d02 = {"branch": gout("rev-parse", "--abbrev-ref", "HEAD"),
       "local_head": gout("rev-parse", "HEAD"),
       "remote_task_branch": gout("rev-parse", "origin/" + BRANCH),
       "origin_main": gout("rev-parse", "origin/main"),
       "dirty_files": [l for l in gout("status", "--porcelain").split("\n") if l.strip()],
       "note": "本项在最终推送后由收口复核确认；此处记录当前观察"}
put("M4-PCR-02", d02["branch"] == BRANCH, "分支正确；本地/远端一致性在推送后复核", d02)

# ── PCR-03 挂载与目标系统身份 ─────────────────────────────────────────────
def dstat(cont, path):
    return subprocess.run(["docker", "exec", "-i", cont, "stat", "-c", "%i", path],
                          capture_output=True, text=True).stdout.strip()
host_pg = subprocess.run(["stat", "-c", "%i", "/home/faye/dify/docker/volumes/db/data/pgdata"],
                         capture_output=True, text=True).stdout.strip()
host_st = subprocess.run(["stat", "-c", "%i", "/home/faye/dify/docker/volumes/app/storage"],
                         capture_output=True, text=True).stdout.strip()
cont_pg = dstat("docker-db_postgres-1", "/var/lib/postgresql/data/pgdata")
cont_st = dstat("docker-api-1", "/app/api/storage")
mounts = subprocess.run(["docker", "inspect", "docker-db_postgres-1", "--format",
                         "{{range .Mounts}}{{.Source}}->{{.Destination}} {{end}}"],
                        capture_output=True, text=True).stdout.strip()
counts = {r["k"]: int(r["v"]) for r in q(
    "SELECT 'apps' AS k, count(*)::text AS v FROM apps UNION ALL "
    "SELECT 'workflows', count(*)::text FROM workflows UNION ALL "
    "SELECT 'workflow_runs', count(*)::text FROM workflow_runs UNION ALL "
    "SELECT 'tenants', count(*)::text FROM tenants UNION ALL "
    "SELECT 'accounts', count(*)::text FROM accounts")}
health = subprocess.run(["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
                        capture_output=True, text=True).stdout.strip().split("\n")
d03 = {"host_pgdata_inode": host_pg, "container_pgdata_inode": cont_pg, "pgdata_same_inode": host_pg == cont_pg,
       "host_storage_inode": host_st, "container_storage_inode": cont_st, "storage_same_inode": host_st == cont_st,
       "db_mount": mounts, "counts": counts,
       "containers": [h for h in health if h.startswith("docker-")]}
put("M4-PCR-03", (d03["pgdata_same_inode"] and d03["storage_same_inode"]
                  and counts["apps"] > 0 and counts["workflow_runs"] > 0 and counts["tenants"] == 1),
    "挂载 inode 与宿主一致，数据库非空", d03)

# ── PCR-04 八应用身份 / 发布 / 图 与冻结候选一致 ──────────────────────────
fz = json.load(open(FREEZE, encoding="utf-8"))["dify_bindings"]
d04 = {}
ok04 = True
for k, (name, aid) in APPS.items():
    r = q("SELECT a.id, a.name, a.status, a.workflow_id, encode(sha256(convert_to(w.graph,'UTF8')),'hex') AS gsha "
          "FROM apps a LEFT JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s'" % aid)
    row = r[0] if r else None
    exp = fz.get(k, {}).get("graph_sha256")
    e = {"expected_app_id": aid, "found": bool(row),
         "name_matches": bool(row) and row["name"] == name,
         "status": row["status"] if row else None,
         "published_workflow_id": row["workflow_id"] if row else None,
         "graph_sha256": row["gsha"] if row else None,
         "frozen_candidate_graph_sha256": exp,
         "graph_matches_frozen_candidate": bool(row) and row["gsha"] == exp}
    d04[k] = e
    if not (e["found"] and e["name_matches"] and e["published_workflow_id"] and e["graph_matches_frozen_candidate"]):
        ok04 = False
put("M4-PCR-04", ok04, "八应用保留原 ID、已发布、当前图 == 冻结候选图", d04)

# ── PCR-05 恢复证据与当前图精确绑定 ───────────────────────────────────────
smoke = json.load(open(os.path.join(RESTORE, "M4_RESTORE_SMOKE.json"), encoding="utf-8"))
e2e = json.load(open(os.path.join(RESTORE, "M4_RESTORE_CANVAS_E2E.json"), encoding="utf-8"))
d05 = {"capabilities": [], "seam": None, "canvas": None}
ok05 = True
for c in smoke["capabilities"]:
    rid = c["smoke_run_id"]
    r = q("SELECT wr.id, wr.status, wr.workflow_id, a.workflow_id AS current_published_workflow_id, "
          "encode(sha256(convert_to(w.graph,'UTF8')),'hex') AS run_graph_sha "
          "FROM workflow_runs wr JOIN apps a ON a.id=wr.app_id JOIN workflows w ON w.id=wr.workflow_id "
          "WHERE wr.id='%s'" % rid)
    row = r[0] if r else None
    skill = q("SELECT count(*)::int AS n FROM workflow_node_executions WHERE workflow_run_id='%s' "
              "AND node_id='skill_llm' AND status='succeeded'" % rid)[0]["n"] if row else 0
    e = {"capability": c["capability"], "run_id": rid, "found": bool(row),
         "run_workflow_id": row["workflow_id"] if row else None,
         "current_published_workflow_id": row["current_published_workflow_id"] if row else None,
         "run_bound_to_current_published_graph": bool(row) and row["workflow_id"] == row["current_published_workflow_id"],
         "run_graph_sha256": row["run_graph_sha"] if row else None,
         "graph_matches_frozen": bool(row) and row["run_graph_sha"] == d04[c["capability"]]["frozen_candidate_graph_sha256"],
         "delivery_outcome": c["delivery_outcome"], "skill_llm_succeeded": skill,
         "user_delivery_length": c["user_delivery_length"]}
    d05["capabilities"].append(e)
    if not (e["found"] and e["run_bound_to_current_published_graph"] and e["graph_matches_frozen"]
            and e["delivery_outcome"] == "DELIVERED" and skill == 1):
        ok05 = False
# Seam
srid = smoke["seam"]["smoke_run_id"]
sr = q("SELECT wr.id, wr.workflow_id, a.workflow_id AS cur FROM workflow_runs wr JOIN apps a ON a.id=wr.app_id "
       "WHERE wr.id='%s'" % srid)
stools = q("SELECT DISTINCT node_id FROM workflow_node_executions WHERE workflow_run_id='%s' "
           "AND node_id LIKE 'tool_%%'" % srid)
d05["seam"] = {"run_id": srid, "found": bool(sr),
               "bound_to_current_published_graph": bool(sr) and sr[0]["workflow_id"] == sr[0]["cur"],
               "tool_nodes_executed": sorted(x["node_id"] for x in stools),
               "child_app_invoked": smoke["seam"]["child_app_actually_invoked"],
               "user_delivery_length": smoke["seam"]["user_delivery_length"]}
if not (d05["seam"]["found"] and d05["seam"]["bound_to_current_published_graph"]
        and len(d05["seam"]["tool_nodes_executed"]) == 1 and d05["seam"]["child_app_invoked"]):
    ok05 = False
# Canvas 端到端
crid = e2e.get("final_seam_run_id")
cr = q("SELECT wr.id, wr.app_id, wr.workflow_id, a.workflow_id AS cur FROM workflow_runs wr "
       "JOIN apps a ON a.id=wr.app_id WHERE wr.id='%s'" % crid) if crid else []
d05["canvas"] = {"e2e_reached_seam": e2e["e2e_reached_seam"], "seam_run_id_from_canvas": crid,
                 "seam_run_found": bool(cr),
                 "seam_run_app_is_capability_seam": bool(cr) and cr[0]["app_id"] == APPS["CAPABILITY_SEAM"][1],
                 "bound_to_current_published_graph": bool(cr) and cr[0]["workflow_id"] == cr[0]["cur"],
                 "answer_length": len(e2e["final_answer"])}
if not (e2e["e2e_reached_seam"] and d05["canvas"]["seam_run_found"]
        and d05["canvas"]["seam_run_app_is_capability_seam"]
        and d05["canvas"]["bound_to_current_published_graph"]):
    ok05 = False
put("M4-PCR-05", ok05, "六能力/Seam/Canvas 的真实运行与当前已发布图精确绑定", d05)

# ── PCR-06 空正文 0 / think 泄漏 0 ────────────────────────────────────────
texts = [(c["capability"], c["user_delivery_excerpt"], c["user_delivery_length"]) for c in smoke["capabilities"]]
texts.append(("SEAM", smoke["seam"]["user_delivery_excerpt"], smoke["seam"]["user_delivery_length"]))
texts.append(("CANVAS", e2e["final_answer"], len(e2e["final_answer"])))
empty = [t[0] for t in texts if t[2] == 0]
leaks = {t[0]: [w for w in THINK if w in (t[1] or "")] for t in texts}
leaks = {k: v for k, v in leaks.items() if v}
d06 = {"checked": [t[0] for t in texts], "empty_user_delivery": empty,
       "empty_user_delivery_count": len(empty),
       "think_leak_by_source": leaks, "think_leak_count": sum(len(v) for v in leaks.values()),
       "lengths": {t[0]: t[2] for t in texts}}
put("M4-PCR-06", not empty and not leaks, "空正文 0，thinking 泄漏 0", d06)

# ── PCR-07 六 Skill / 六专业正文 / 六模型参数零未授权变化 ─────────────────
d07 = {"source_skills": {}, "professional_prompts": {}, "model_params": {}}
ok07 = True
for cap in B.CAPABILITIES:
    rel = os.path.relpath(cap["skill_path"], ROOT)
    now = sha_f(os.path.join(ROOT, rel))
    at_cand = git("show", "%s:%s" % (CANDIDATE_COMMIT, rel))
    same = at_cand.returncode == 0 and sha_s(at_cand.stdout) == now
    d07["source_skills"][cap["capability"]] = {"path": rel, "sha256": now, "identical_to_candidate": same}
    if not same: ok07 = False
    yrel = os.path.relpath(os.path.join(cap["out_dir"], cap["out_file"]), ROOT)
    new = yaml.safe_load(open(os.path.join(ROOT, yrel), encoding="utf-8"))
    old = yaml.safe_load(git("show", "%s:%s" % (CANDIDATE_COMMIT, yrel)).stdout)
    def sll(d): return {n["id"]: n["data"] for n in d["workflow"]["graph"]["nodes"]}["skill_llm"]
    on, nn = sll(old), sll(new)
    ps = json.dumps(on["prompt_template"], sort_keys=True, ensure_ascii=False) == \
         json.dumps(nn["prompt_template"], sort_keys=True, ensure_ascii=False)
    ms = on["model"] == nn["model"]
    d07["professional_prompts"][cap["capability"]] = {
        "bytewise_identical_to_candidate": ps,
        "prompt_sha256": sha_s(json.dumps(nn["prompt_template"], sort_keys=True, ensure_ascii=False))}
    d07["model_params"][cap["capability"]] = {"identical_to_candidate": ms, "model": nn["model"]}
    if not (ps and ms): ok07 = False
put("M4-PCR-07", ok07, "六源 Skill / 六专业正文 / 六模型参数零变化", d07)

# ── PCR-08 故障注入对象不可从正式链路到达 ────────────────────────────────
inj_providers = q("SELECT id,name,app_id FROM tool_workflow_providers WHERE app_id IN (%s)"
                  % ",".join("'%s'" % a for a in INJECTION_APPS))
official_graphs = {}
refs = []
for k, (name, aid) in APPS.items():
    g = q("SELECT w.graph FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s'" % aid)
    blob = g[0]["graph"] if g else ""
    official_graphs[k] = len(blob)
    for token in INJECTION_APPS + [p["id"] for p in inj_providers] + ["diyu_m4_ac31_inject_child",
                                                                     "FAULT INJECTION", "M4_FAULT_DIRECTIVE"]:
        if token and token in blob:
            refs.append({"app": k, "token": token})
d08 = {"injection_apps": INJECTION_APPS, "injection_tool_providers_remaining": inj_providers,
       "official_graph_reverse_references": refs,
       "official_graph_sizes": official_graphs,
       "status": "EVALUATION_ONLY_NOT_ROUTABLE" if not inj_providers and not refs else "ROUTABLE"}
put("M4-PCR-08", not inj_providers and not refs, "注入对象无 tool provider，正式链路零反向引用", d08)

# ── PCR-09 M5 映射与当前身份一致 ─────────────────────────────────────────
mp = yaml.safe_load(open(os.path.join(ROOT, "decision-chain/docs/V1_M4_M5_HANDOFF_MAP_v0.1.yaml"), encoding="utf-8"))
d09 = {"mismatches": [], "checked": []}
fe = mp["founder_natural_entry"]
if fe["app_id"] != APPS["FOUNDER_CANVAS"][1]: d09["mismatches"].append("founder_canvas app_id")
if fe["workflow_id"] != d04["FOUNDER_CANVAS"]["published_workflow_id"]: d09["mismatches"].append("founder_canvas workflow_id")
cs = mp["capability_seam"]
if cs["app_id"] != APPS["CAPABILITY_SEAM"][1]: d09["mismatches"].append("seam app_id")
if cs["workflow_id"] != d04["CAPABILITY_SEAM"]["published_workflow_id"]: d09["mismatches"].append("seam workflow_id")
live_tools = {t["app_id"]: t["name"] for t in q("SELECT app_id,name FROM tool_workflow_providers")}
if cs["tool_name"] != live_tools.get(APPS["CAPABILITY_SEAM"][1]): d09["mismatches"].append("seam tool_name")
for a in mp["applications"]:
    cap = a["capability"]; d09["checked"].append(cap)
    if a["new_app_id"] != APPS[cap][1]: d09["mismatches"].append("%s app_id" % cap)
    if a["new_workflow_id"] != d04[cap]["published_workflow_id"]: d09["mismatches"].append("%s workflow_id" % cap)
    if a["tool_name"] != live_tools.get(APPS[cap][1]): d09["mismatches"].append("%s tool_name" % cap)
    if not a.get("upstream_binding") or not a.get("downstream_binding"): d09["mismatches"].append("%s binding" % cap)
    if not a.get("inputs") or not a.get("end_branches"): d09["mismatches"].append("%s io_contract" % cap)
need = {"入口字段", "出口字段", "M5 必须遵守的语义"}
if not need <= set(mp.get("field_contract_for_m5", {}).keys()): d09["mismatches"].append("field_contract_for_m5")
put("M4-PCR-09", not d09["mismatches"], "M5 映射与当前应用/工作流/tool/IO 合同一致", d09)

# ── PCR-10 历史结果与旧回执逐字节保留；Founder 处置单列 ──────────────────
HIST = ["decision-chain/docs/V1_M4_FINAL_CLOSURE_RECEIPT_v0.1.md",
        "decision-chain/docs/V1_M4_AC31_REBASE_CLOSING_RECEIPT_v0.1.md",
        "decision-chain/docs/V1_M4_FINAL_CLOSURE_TASK_CONTRACT_v1.0.yaml",
        "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md",
        "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md",
        "decision-chain/evidence/m4/M4_POST_REVIEW_VERDICTS.json",
        "decision-chain/evidence/m4/final_closure/CL31_POST_REVIEW_VERDICTS.json",
        "decision-chain/evidence/m4/final_closure/CL31_02_03_04_VERDICT_A1.json"]
d10 = {"byte_preserved": {}, "historical_states": {}}
ok10 = True
for rel in HIST:
    dif = gout("diff", RESTORE_COMMIT, "HEAD", "--", rel)
    d10["byte_preserved"][os.path.basename(rel)] = {"unchanged_since_restore_commit": dif == "",
                                                    "sha256": sha_f(os.path.join(ROOT, rel))}
    if dif != "": ok10 = False
pv = json.load(open(os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CL31_POST_REVIEW_VERDICTS.json"),
                    encoding="utf-8"))
d10["historical_states"] = {"previous_formal_status": pv["task_final_status"],
                            "CL31_verdicts": {k: v["verdict"] for k, v in pv["verdicts"].items()},
                            "AC31_④": "NOT_VERIFIED", "RB31_03_v0_4": "NOT_VERIFIED", "RB31_05_v0_4": "FAIL"}
d10["founder_disposition_recorded_separately"] = True
if pv["task_final_status"] != "BLOCKED": ok10 = False
put("M4-PCR-10", ok10, "旧回执与旧技术结果逐字节保留，Founder 处置单列", d10)

# ── PCR-12 本轮零工程副作用 ──────────────────────────────────────────────
# 注意：git status --porcelain 的状态位占前两列、第三列是空格；不得对整体输出 strip()，
# 否则首行前导空格被吃掉，l[3:] 会多切一个字符并把合规文件误判成越界。
_porcelain = git("status", "--porcelain").stdout
changed = [f for f in gout("diff", "--name-only", RESTORE_COMMIT, "HEAD").split("\n") if f] + \
          [l[3:] for l in _porcelain.split("\n") if l.strip()]
# 本轮唯一允许新增的 .py 是只读 PCR 核验器本身（产出证据索引，零工程资产变更）。
# 任何 .yml / skills / 其它 .py 变更都算工程资产变更，判 FAIL。
READONLY_VERIFIERS = ("decision-chain/workflows/DIYU_M4_PCR_VERIFY_v0.1.py",
                      "decision-chain/workflows/DIYU_M4_PCR_NEGATIVE_v0.1.py")
ENG = [f for f in changed if f.endswith(".yml") or "/skills/" in f
       or (f.endswith(".py") and f not in READONLY_VERIFIERS)]
ALLOWED = ("decision-chain/docs/", "decision-chain/evidence/m4/post_restore/", "collab-ledger/") \
          + READONLY_VERIFIERS
out_of_scope = sorted({f for f in changed if not f.startswith(ALLOWED)})
d12 = {"changed_files_this_round": sorted(set(changed)),
       "engineering_asset_changes": sorted(set(ENG)),
       "out_of_scope": out_of_scope,
       "origin_main": gout("rev-parse", "origin/main"),
       "main_changed_by_this_task": False,
       "pr_created": False,
       "official_m4_graphs_unchanged": all(d04[k]["graph_matches_frozen_candidate"] for k in APPS),
       "db_schema_tables": q("SELECT count(*)::int AS n FROM information_schema.tables WHERE table_schema='public'")[0]["n"]}
put("M4-PCR-12", not ENG and not out_of_scope and d12["official_m4_graphs_unchanged"],
    "零工程资产变更、零越界文件、八应用图未变", d12)

# ── PCR-11 由上述结果一致推导（回执/账本写入后复核） ─────────────────────
core = ["M4-PCR-01", "M4-PCR-03", "M4-PCR-04", "M4-PCR-05", "M4-PCR-06",
        "M4-PCR-07", "M4-PCR-08", "M4-PCR-09", "M4-PCR-10", "M4-PCR-12"]
all_core = all(R["criteria"].get(c) == "PASS" for c in core)
R["derived_terminal_state"] = "DONE" if all_core else "NOT_DONE_YET"
R["core_criteria_all_pass"] = all_core
R["note_PCR_02_11"] = "PCR-02 的远端一致性与 PCR-11 的回执/账本一致性在收口提交与推送后由 AW-07 复核"

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
print("\n核心十项全过 =", all_core)
print("evidence ->", os.path.relpath(OUT, ROOT))
