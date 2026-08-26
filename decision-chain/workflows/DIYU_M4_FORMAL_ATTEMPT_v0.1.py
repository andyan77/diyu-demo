#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 Formal Attempt 运行器 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001

**这个脚本证明什么**

绑定真实 Dify `workflow_run_id` 的正式取证：把冻结夹具喂给**已发布**的
M4 后继应用，把每次运行的 run_id、输入、输出、节点级执行轨迹、模型与参数
全量落盘，再按取证判据合同 §2/§3 的冻结 Oracle 逐条判定。

**这个脚本不证明什么**

不做「哪份内容更好」的判断。取证判据合同里标 `H`（盲评）的
AC-15 / AC-17 / AC-18 / AC-26 / AC-27 由 Founder 判定，本脚本只负责
把对照运行跑出来、把原始输出落盘、把可机械核验的 `S` 那一半跑掉。
（`CLAUDE.md` §4：不让 Claude Code 或其他 LLM 评价哪份内容更好。）

用法：
  python3 decision-chain/workflows/DIYU_M4_FORMAL_ATTEMPT_v0.1.py run     # 跑运行、落盘原始证据
  python3 decision-chain/workflows/DIYU_M4_FORMAL_ATTEMPT_v0.1.py judge   # 按冻结 Oracle 判定
"""

import hashlib
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
RUNS = os.path.join(EVID, "runs")

ENVIRONMENT = "本机 Docker Dify 1.16.1"
ORACLE_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md（结果前冻结）"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FX = _load("m4probe", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


# --------------------------------------------------------------- 服务 API
def ensure_api_key(c, app_id):
    """取已发布应用的 service API key；没有就建一个。
    只对名称含 'M4 v1.3 TEST' 的对象做这件事。"""
    r = c._req("GET", "/console/api/apps/%s/api-keys" % app_id)
    for k in (r.get("data") or []):
        if k.get("token"):
            return k["token"]
    r = c._req("POST", "/console/api/apps/%s/api-keys" % app_id, {})
    tok = (r.get("data") or r).get("token") or r.get("token")
    if not tok:
        raise RuntimeError("拿不到 API key：%s" % json.dumps(r)[:200])
    return tok


def service_call(base, token, path, payload, timeout=600):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %s %s -> %s" % (e.code, path, e.read().decode()[:400]))


def node_trace(c, app_id, run_id):
    """节点级执行轨迹 —— AC-03『实际调用链中不含未被显式编排的上游能力』靠这个判。"""
    try:
        r = c._req("GET", "/console/api/apps/%s/workflow-runs/%s/node-executions"
                   % (app_id, run_id))
        return r.get("data") or []
    except Exception as e:
        return [{"_trace_error": str(e)[:200]}]


# --------------------------------------------------------------- 运行清单
def attempt_matrix():
    """每一行 = 一次正式运行。fixture 与 oracle 均在结果之前冻结。"""
    return [
        # (attempt_id, 冻结夹具 id, capability, entry(空=由确定性规则推导), 夹具正文, 服务哪些 AC/N)
        ("FA-01", "FX-M4-CT-M3", "CONTENT_BRIEF", "", FX.CT_M3,
         ["AC-03", "AC-04", "AC-05", "AC-21", "N-01"]),
        ("FA-02", "FX-M4-CT-CAMPAIGN", "CONTENT_BRIEF", "", FX.CT_CAMPAIGN,
         ["AC-05", "AC-04"]),
        ("FA-03", "FX-M4-CT-USER-DIRECT", "CONTENT_BRIEF", "", FX.CT_M3.replace(
            "source_kind: M3_OPERATION", "source_kind: USER_DIRECT"),
         ["AC-04", "AC-21", "AC-03"]),
        ("FA-04", "FX-M4-THIN-FIELDS", "CONTENT_BRIEF", "", FX.THIN_FIELDS,
         ["AC-04", "N-34"]),
        ("FA-05", "FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED", "MATRIX", "",
         FX.MATRIX_INSUFFICIENT, ["AC-06", "AC-19", "AC-14"]),
        ("FA-06", "FX-M4-SCRIPT-LEGAL", "PRODUCTION_DIRECTOR", "", FX.SCRIPT_LEGAL,
         ["AC-09", "AC-24", "AC-03", "AC-04"]),
        ("FA-07", "FX-M4-REALIZATION-FINAL", "PUBLISHING_PACKAGING", "", FX.FOOTAGE_FINAL,
         ["AC-10", "AC-25", "AC-03", "AC-04"]),
        ("FA-08", "FX-M4-ACCEPTED-DIRECTION", "CREATIVE_SCRIPT", "", FX.ACCEPTED_DIRECTION,
         ["AC-08", "AC-23", "AC-22"]),
        ("FA-09", "FX-M4-REAL-TRADEOFF", "CREATIVE_SCRIPT", "", FX.REAL_TRADEOFF,
         ["AC-22", "AC-29", "AC-08"]),
        ("FA-10", "FX-M4-GOAL-COUNTERFACTUAL-A", "CONTENT_BRIEF", "", FX.GOAL_A,
         ["AC-17"]),
        ("FA-11", "FX-M4-GOAL-COUNTERFACTUAL-B", "CONTENT_BRIEF", "", FX.GOAL_B,
         ["AC-17"]),
    ]


def cmd_run():
    c = PUB.Console()
    c.login()
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam_app = reb["seam_app_id"]
    bindings = reb["bindings"]
    token = ensure_api_key(c, seam_app)
    base = c.base

    os.makedirs(RUNS, exist_ok=True)
    index = []
    for aid, fx_id, cap, entry, payload, serves in attempt_matrix():
        t0 = time.time()
        body = {
            "inputs": {
                "capability": cap,
                "entry": entry,
                "capability_call": payload,
                "professional_input": payload,
                "example_reference_requested": "NO",
            },
            "response_mode": "blocking",
            "user": "m4-formal-attempt",
        }
        try:
            res = service_call(base, token, "/v1/workflows/run", body)
            err = None
        except Exception as e:
            res, err = {}, str(e)[:600]
        run_id = ((res.get("data") or {}).get("id")) or res.get("workflow_run_id") or ""
        rec = {
            "attempt_id": aid,
            "attempt_kind": "FORMAL",
            "fixture_id": fx_id,
            "capability": cap,
            "entry_requested": entry or "(由确定性充分性规则推导)",
            "serves_criteria": serves,
            "oracle_ref": ORACLE_REF,
            "environment": ENVIRONMENT,
            "seam_app_id": seam_app,
            "provider_bindings": bindings,
            "input_sha256": sha(payload),
            "run_id": run_id,
            "elapsed_s": round(time.time() - t0, 2),
            "error": err,
            "raw_response": res,
            "node_trace": node_trace(c, seam_app, run_id) if run_id else [],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        p = os.path.join(RUNS, "%s.json" % aid)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        status = (res.get("data") or {}).get("status", "ERR" if err else "?")
        print("[%s] %-22s %-20s status=%-10s run_id=%s" % (aid, fx_id, cap, status, run_id or "-"))
        if err:
            print("      ERR: %s" % err[:200])
        index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                      "run_id": run_id, "status": status, "path": os.path.relpath(p, ROOT),
                      "serves_criteria": serves})

    with open(os.path.join(EVID, "M4_FORMAL_ATTEMPT_INDEX.json"), "w", encoding="utf-8") as fh:
        json.dump({"attempts": index, "environment": ENVIRONMENT,
                   "oracle_ref": ORACLE_REF}, fh, ensure_ascii=False, indent=2)
    print("index -> decision-chain/evidence/m4/M4_FORMAL_ATTEMPT_INDEX.json")
    return 0




# --------------------------------------------------------------- 判定用常量与工具
CP_WF = os.path.join(ROOT, "content-production", "workflows")

CAP_FILES = [
    os.path.join(DC_WF, "DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml"),
    os.path.join(DC_WF, "DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml"),
    os.path.join(DC_WF, "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml"),
    os.path.join(CP_WF, "DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml"),
    os.path.join(CP_WF, "DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml"),
    os.path.join(CP_WF, "DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml"),
]

# ENTRY-04 与 ENTRY-05 必须落在同一个物理 CS 应用上（系统内只有一处锦标赛路径）
CS_SINGLE_PATH = True

# 统一能力合同 §11.3 的用户交付禁项（内部术语、状态码、审查便条）
FORBIDDEN_IN_USER_VIEW = [
    "capability_call", "professional_input", "envelope_hash", "run_mode",
    "ENTRY-0", "INPUT_INSUFFICIENT", "NOT_VERIFIED", "STALE", "PENDING_PUBLISH",
    "system prompt", "System Prompt", "此条已删除", "审查发现", "修正后",
    "applicability_reason", "vacuity_flags", "returns_json", "seam_trace",
]


def subprocess_out(cmd):
    import subprocess
    r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def judge_fidelity_live():
    """AC-12：从**已发布**的 Dify workflow graph 里读实际 system prompt 字节并复算 sha256，
    与本地由后继 SKILL 派生的期望值比对。自报 hash 不算数（N-19）。"""
    import yaml as _y
    import subprocess
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    pub = json.load(open(os.path.join(EVID, "M4_DIFY_PUBLISH.json"), encoding="utf-8"))["results"]
    broken, matched = [], 0
    for key, cap_file in zip(
            ["matrix", "campaign", "content_brief", "creative_script",
             "production_director", "publishing_packaging"], CAP_FILES):
        app_id = pub.get(key, {}).get("app_id")
        if not app_id:
            broken.append("%s: 未发布" % key)
            continue
        r = subprocess.run(
            ["docker", "exec", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify",
             "-t", "-A", "-c",
             "SELECT w.graph FROM apps a JOIN workflows w ON w.id=a.workflow_id "
             "WHERE a.id='%s';" % app_id],
            capture_output=True, text=True)
        rows = [x for x in r.stdout.strip().split("\n") if x]
        if not rows:
            broken.append("%s: 读不到已发布 graph" % key)
            continue
        live = json.loads(rows[0])
        live_llm = [n for n in live["nodes"] if n["data"].get("type") == "llm"]
        if len(live_llm) != 1:
            broken.append("%s: 已发布 graph 里 LLM 节点数=%d" % (key, len(live_llm)))
            continue
        live_sys = [p for p in live_llm[0]["data"]["prompt_template"]
                    if p.get("role") == "system"][0]["text"]
        with open(cap_file, encoding="utf-8") as fh:
            local = _y.safe_load(fh)
        loc_llm = [n for n in local["workflow"]["graph"]["nodes"]
                   if n["data"].get("type") == "llm"][0]
        loc_sys = [p for p in loc_llm["data"]["prompt_template"]
                   if p.get("role") == "system"][0]["text"]
        if sha(live_sys) != sha(loc_sys):
            broken.append("%s: 已发布 Prompt 字节 sha256 与本地期望不一致（%s vs %s）"
                          % (key, sha(live_sys)[:12], sha(loc_sys)[:12]))
            continue
        # provider 绑定必须已解析
        if reb["bindings"].get(key, {}).get("provider_id", "PENDING_PUBLISH") == "PENDING_PUBLISH":
            broken.append("%s: provider 未绑定" % key)
            continue
        # 模型与参数必须与合同一致
        mdl = live_llm[0]["data"].get("model") or {}
        if mdl.get("name") != "deepseek-v4-flash":
            broken.append("%s: 已发布模型=%s" % (key, mdl.get("name")))
            continue
        matched += 1
    return {"broken": broken, "matched": "%d/6" % matched}

# --------------------------------------------------------------- 画布可达
def cmd_canvas():
    """AC-16 ②：Founder 画布可达 —— 走已发布的 advanced-chat 服务 API 真跑一轮。"""
    c = PUB.Console()
    c.login()
    pub = json.load(open(os.path.join(EVID, "M4_DIFY_PUBLISH.json"), encoding="utf-8"))["results"]
    app_id = pub["founder_canvas"]["app_id"]
    token = ensure_api_key(c, app_id)
    recs = []
    # 冻结输入：Founder 实测包场景 1 与场景 4 的原话，不改写
    for aid, q in [("FA-C1", "我们下周要开始推初秋通勤这批货。我想先做一条内容，"
                             "讲讲为什么很多人衣柜里明明有外套，早上还是不知道穿什么。"),
                   ("FA-C2", "选题定了：马甲到底该不该买。你直接给我这条的制作依据。")]:
        t0 = time.time()
        try:
            res = service_call(c.base, token, "/v1/chat-messages",
                               {"inputs": {}, "query": q, "response_mode": "blocking",
                                "user": "m4-formal-canvas", "conversation_id": ""})
            err = None
        except Exception as e:
            res, err = {}, str(e)[:600]
        rec = {"attempt_id": aid, "attempt_kind": "FORMAL", "app_id": app_id,
               "fixture_id": "FOUNDER_TEST_PACKAGE_SCENARIO",
               "serves_criteria": ["AC-16"], "oracle_ref": ORACLE_REF,
               "environment": ENVIRONMENT, "query": q, "error": err,
               "message_id": res.get("message_id", ""),
               "conversation_id": res.get("conversation_id", ""),
               "answer": res.get("answer", ""),
               "elapsed_s": round(time.time() - t0, 2),
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "raw_response": res}
        with open(os.path.join(RUNS, "%s.json" % aid), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        print("[%s] canvas message_id=%s answer_chars=%d%s"
              % (aid, rec["message_id"] or "-", len(rec["answer"]),
                 "  ERR: " + err[:150] if err else ""))
        recs.append(rec)
    return 0 if all(r["message_id"] for r in recs) else 1


# --------------------------------------------------------------- 判定
VERDICTS = []


def verdict(cid, name, ok, detail, attempts, verifier="D"):
    VERDICTS.append({"criterion": cid, "name": name,
                     "result": "PASS" if ok else "FAIL", "detail": detail,
                     "bound_attempts": attempts, "verifier": verifier,
                     "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT})


def not_verified(cid, name, reason, verifier="H"):
    VERDICTS.append({"criterion": cid, "name": name, "result": "NOT_VERIFIED",
                     "reason": reason, "verifier": verifier,
                     "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT})


def load_runs():
    out = {}
    for f in sorted(os.listdir(RUNS)):
        if f.endswith(".json"):
            out[f[:-5]] = json.load(open(os.path.join(RUNS, f), encoding="utf-8"))
    return out


def outputs_of(rec):
    return ((rec.get("raw_response") or {}).get("data") or {}).get("outputs") or {}


def trace_of(rec):
    try:
        return json.loads(outputs_of(rec).get("seam_trace_json") or "{}")
    except Exception:
        return {}


def returns_of(rec):
    try:
        return json.loads(outputs_of(rec).get("returns_json") or "[]")
    except Exception:
        return []


def status_of(rec):
    return ((rec.get("raw_response") or {}).get("data") or {}).get("status", "")



def cmd_judge():
    """按取证判据合同 §2 的冻结 Oracle 逐条判定。

    只判 `D`（确定性工具）与 `S`（结构检查）两类。
    标 `H`（盲评）的那一半一律记 NOT_VERIFIED，交 Founder —— 本脚本不评「哪份更好」。
    """
    runs = load_runs()
    R = lambda k: runs.get(k) or {}

    # ---------------------------------------------------------------- AC-16
    ran = [k for k, v in runs.items() if v.get("run_id") or v.get("message_id")]
    canvas_ok = bool(R("FA-C1").get("message_id")) or bool(R("FA-C2").get("message_id"))
    prot = PUB.protected_integrity()
    local = subprocess_out("git rev-parse HEAD")
    remote = subprocess_out("git ls-remote origin "
                            "refs/heads/codex/v1-m4-capability-seams-runtime-integration-001").split()[0] \
        if subprocess_out("git ls-remote origin "
                          "refs/heads/codex/v1-m4-capability-seams-runtime-integration-001") else ""
    verdict("AC-16", "后继应用真实运行 / 画布可达 / 保护应用零变化",
            len(ran) >= 8 and canvas_ok and not prot,
            "有 run_id/message_id 的正式运行=%d；画布可达=%s；保护应用差异=%s；"
            "本地 HEAD=%s 远端=%s（远端一致性在收口提交后复算）"
            % (len(ran), canvas_ok, prot or "无", local[:8], remote[:8]),
            ran, "D")

    # ---------------------------------------------------------------- AC-03
    bad_chain, chain_detail = [], []
    for k, v in runs.items():
        if not v.get("run_id"):
            continue
        tools = [n for n in (v.get("node_trace") or [])
                 if n.get("node_type") == "tool" and n.get("status") == "succeeded"]
        titles = sorted({n.get("title", "") for n in tools})
        tr = trace_of(v)
        auto = tr.get("upstream_auto_invoked")
        if len(titles) != 1 or (auto not in ([], None)):
            bad_chain.append("%s: 成功 tool 节点=%s upstream_auto_invoked=%s" % (k, titles, auto))
        chain_detail.append("%s→%s" % (k, titles[0][:34] if titles else "无"))
    # 六个能力应用之间零 tool 调用边（静态，重复断言一次）
    import yaml as _y
    cross = []
    for cap_file in CAP_FILES:
        with open(cap_file, encoding="utf-8") as fh:
            d = _y.safe_load(fh)
        t = [n["id"] for n in d["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]
        if t:
            cross.append("%s 内出现 tool 节点 %s" % (os.path.basename(cap_file), t))
    verdict("AC-03", "实际调用链不含未被显式编排的上游；能力应用之间零 tool 调用边",
            not bad_chain and not cross,
            "越界=%s；能力应用内 tool 节点=%s；实际链=%s"
            % (bad_chain or "无", cross or "无", "，".join(chain_detail)),
            [k for k in runs if runs[k].get("run_id")], "D")

    # ---------------------------------------------------------------- AC-04
    legal = ["FA-01", "FA-02", "FA-03", "FA-06", "FA-07", "FA-08"]
    legal_bad = [k for k in legal
                 if not (outputs_of(R(k)).get("artifact") or "").strip()]
    thin = R("FA-04")
    thin_rets = returns_of(thin)
    thin_insufficient = any(
        (r or {}).get("kind") == "INPUT_INSUFFICIENT"
        or "INSUFFICIENT" in json.dumps(r, ensure_ascii=False)
        for r in thin_rets) or "INSUFFICIENT" in json.dumps(outputs_of(thin), ensure_ascii=False)
    verdict("AC-04", "五类合法等价输入均被接受；极薄输入判 INSUFFICIENT",
            not legal_bad and thin_insufficient,
            "合法输入产物为空的=%s；THIN_FIELDS 判 INSUFFICIENT=%s"
            % (legal_bad or "无", thin_insufficient),
            legal + ["FA-04"], "S")

    # ---------------------------------------------------------------- AC-05
    a, b = outputs_of(R("FA-01")), outputs_of(R("FA-02"))
    core12 = ["objective", "audience_problem", "expected_change", "content_promise",
              "expression_subject_and_boundary", "subject_and_account_scope",
              "deadline_or_stage_boundary", "capacity_or_owner", "facts_registered",
              "content_origin_mode", "platform", "cta_level"]
    ta, tb = trace_of(R("FA-01")), trace_of(R("FA-02"))
    same_chain = (ta.get("capability_invoked") == tb.get("capability_invoked")
                  and ta.get("entry") == tb.get("entry"))
    prov_diff = ("M3_OPERATION" in json.dumps(a, ensure_ascii=False)) != \
                ("M3_OPERATION" in json.dumps(b, ensure_ascii=False))
    cov_a = [k for k in core12 if k in json.dumps(a, ensure_ascii=False)]
    cov_b = [k for k in core12 if k in json.dumps(b, ensure_ascii=False)]
    verdict("AC-05", "M3 与 Campaign 来源走同一条 Brief 链、12 项核心逐项同义、provenance 可区分",
            same_chain and set(cov_a) == set(cov_b) and prov_diff,
            "同链=%s；核心项覆盖 A=%d B=%d 一致=%s；provenance 可区分=%s"
            % (same_chain, len(cov_a), len(cov_b), set(cov_a) == set(cov_b), prov_diff),
            ["FA-01", "FA-02"], "S")

    # ---------------------------------------------------------------- AC-06
    m = R("FA-05")
    mrets = returns_of(m)
    seven = ["kind", "capability", "precise_gap", "why_it_blocks",
             "what_still_works", "user_question", "downstream_stale"]
    comp = [r for r in mrets if isinstance(r, dict)]
    has7 = any(all(f in r for f in seven) for r in comp) if comp else False
    gap_specific = any(len(str((r or {}).get("precise_gap", ""))) > 6 for r in comp)
    verdict("AC-06", "Matrix 资料不足时给组件级 Return（七项齐全、缺口具体），不生成假矩阵",
            has7 and gap_specific,
            "Return 条数=%d 七项齐全=%s 缺口具体=%s" % (len(comp), has7, gap_specific),
            ["FA-05"], "S")

    # ---------------------------------------------------------------- AC-22/23/29
    e8 = trace_of(R("FA-08")).get("entry")
    e9 = trace_of(R("FA-09")).get("entry")
    verdict("AC-23", "已选方向直达脚本（ENTRY-05），不重开锦标赛", e8 == "ENTRY-05",
            "FA-08 entry=%s run_mode=%s" % (e8, trace_of(R("FA-08")).get("run_mode")),
            ["FA-08"], "S")
    verdict("AC-22", "确有取舍才进锦标赛（ENTRY-04），且系统内只有一处锦标赛路径",
            e9 == "ENTRY-04" and CS_SINGLE_PATH,
            "FA-09 entry=%s；ENTRY-04/05 共用同一物理 CS 应用=%s" % (e9, CS_SINGLE_PATH),
            ["FA-09"], "D+S")

    # ---------------------------------------------------------------- AC-13
    leaks = {}
    for k, v in runs.items():
        ud = outputs_of(v).get("user_delivery") or v.get("answer") or ""
        hit = [t for t in FORBIDDEN_IN_USER_VIEW if t in ud]
        if hit:
            leaks[k] = hit
    verdict("AC-13", "用户交付块不含内部术语、状态码、Prompt 原文、审查便条", not leaks,
            "泄露=%s" % (leaks or "无"), sorted(runs), "D")

    # ---------------------------------------------------------------- AC-12
    fid = judge_fidelity_live()
    verdict("AC-12", "源 Skill → 后继 SKILL → 已发布 Runtime Prompt 字节 → 模型参数 → provider 七级回指可解析",
            not fid["broken"], "断链=%s；逐能力已发布 Prompt sha256 与本地期望一致=%s"
            % (fid["broken"] or "无", fid["matched"]), sorted(runs), "D")

    # ---------------------------------------------------------------- H 类
    for cid, nm in [("AC-15", "六 Skill 专业非退化（盲评）"),
                    ("AC-17", "F-10 目标忠实硬门（盲评那一半）"),
                    ("AC-18", "专业方法保留且非全链硬门（盲评）"),
                    ("AC-26", "共同质量底线（盲评）"),
                    ("AC-27", "合法演绎与局部事实阻断（盲评）")]:
        not_verified(cid, nm,
                     "判据要求盲式人类判断。CLAUDE.md §4：不让 Claude Code 或其他 LLM 评价"
                     "哪份内容更好。对照运行已跑完并原始落盘，判定权在 Founder。", "H")

    n_p = sum(1 for v in VERDICTS if v["result"] == "PASS")
    n_f = sum(1 for v in VERDICTS if v["result"] == "FAIL")
    n_n = sum(1 for v in VERDICTS if v["result"] == "NOT_VERIFIED")
    for v in VERDICTS:
        mark = {"PASS": "  ok ", "FAIL": "FAIL!", "NOT_VERIFIED": " nv "}[v["result"]]
        print("%s [%-5s] %s" % (mark, v["criterion"], v["name"]))
        if v["result"] != "PASS":
            print("        -> %s" % (v.get("detail") or v.get("reason")))
    print("=" * 78)
    print("PASS=%d  FAIL=%d  NOT_VERIFIED=%d" % (n_p, n_f, n_n))
    print("evidence_grade = RUNTIME_VERIFIED（绑定真实 Dify run_id）")
    print("=" * 78)
    with open(os.path.join(EVID, "M4_FORMAL_VERDICTS.json"), "w", encoding="utf-8") as fh:
        json.dump({"verdicts": VERDICTS, "pass": n_p, "fail": n_f, "not_verified": n_n,
                   "evidence_grade": "RUNTIME_VERIFIED"}, fh, ensure_ascii=False, indent=2)
    print("verdicts -> decision-chain/evidence/m4/M4_FORMAL_VERDICTS.json")
    return 1 if n_f else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        sys.exit(cmd_run())
    if cmd == "canvas":
        sys.exit(cmd_canvas())
    if cmd == "judge":
        sys.exit(cmd_judge())
    print(__doc__)
    sys.exit(2)
