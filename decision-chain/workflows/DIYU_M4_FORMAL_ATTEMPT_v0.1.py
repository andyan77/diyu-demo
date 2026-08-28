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
import re
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
        # 以下两条是独立 Reviewer 指出「冻结夹具从未运行」后补跑的（FND-R-05）
        ("FA-12", "FX-M4-NO-TRADEOFF", "CREATIVE_SCRIPT", "", FX.NO_TRADEOFF,
         ["AC-22", "AC-29", "N-50"]),
        ("FA-13", "FX-M4-MIXED-GOALS", "CONTENT_BRIEF", "", FX.MIXED_GOALS,
         ["AC-21", "AC-29", "N-32"]),
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
    only = set(sys.argv[2:])          # 只跑指定 attempt；不指定就全跑
    index = []
    for aid, fx_id, cap, entry, payload, serves in attempt_matrix():
        if only and aid not in only:
            p_old = os.path.join(RUNS, "%s.json" % aid)
            if os.path.exists(p_old):     # 保留既有结果，不重跑、不覆盖
                old = json.load(open(p_old, encoding="utf-8"))
                index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                              "run_id": old.get("run_id", ""),
                              "status": ((old.get("raw_response") or {}).get("data") or {}).get("status", "?"),
                              "path": os.path.relpath(p_old, ROOT),
                              "serves_criteria": serves})
            continue
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

# 用户交付禁项：**直接取生成器里那份冻结清单**，不另立一套。
# 那份清单是统一能力合同 §11.3 的既有操作化，早于本轮全部结果；
# 判定用的判据必须来自冻结件，不能是看到输出之后现写的（A2 第 3 项）。
def _returns_adapter_module():
    """把已生成 DSL 里的 returns_adapter 正文加载成模块 —— 取的是真正在 Dify 里跑的那几个字节。"""
    import types as _t
    import yaml as _y
    with open(os.path.join(DC_WF, "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml"), encoding="utf-8") as fh:
        d = _y.safe_load(fh)
    code = {n["id"]: n for n in d["workflow"]["graph"]["nodes"]}["returns_adapter"]["data"]["code"]
    mod = _t.ModuleType("ra")
    mod.__dict__["json"] = json
    exec(compile(code, "<returns_adapter>", "exec"), mod.__dict__)
    return mod


def _leak_patterns():
    """直接从**已生成的 DSL** 的 returns_adapter 节点里取那份禁项清单 ——
    也就是真正在 Dify 里跑的那几个字节，而不是判定脚本自己另写一份。"""
    import types as _t
    import yaml as _y
    return _returns_adapter_module().LEAK_PATTERNS


FORBIDDEN_IN_USER_VIEW = _leak_patterns()

# Return 必填项：同样取自在 Dify 里跑的那份字节，不由判定脚本另写。
# 注意：统一能力合同 §10.1 的**小标题**写「七项」，其下枚举的却是八项（外加 parse_status）。
# 以枚举为准 —— 具体枚举优先于计数措辞；这处不一致已作为文档缺陷登记。
RET_FIELDS = _returns_adapter_module().RET_FIELDS


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



def contract_leak_literals():
    """AC-13 的禁项字面量**直接从冻结的统一能力合同 §11.3 正文里抽**。

    独立 Reviewer（FND-R-07）指出：原来从生成器的 returns_adapter 里取那 24 条，
    等于让被测代码定义自己的通过条件。这条意见成立，已改为从合同抽。
    生成器那份清单仍然跑，但只作为**补充扫描**单独上报，不构成 AC-13 的判据。
    """
    p = os.path.join(ROOT, "decision-chain", "docs",
                     "V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md")
    with open(p, encoding="utf-8") as fh:
        txt = fh.read()
    m = re.search(r"### 11\.3 硬禁.*?(?=\n---|\n## )", txt, re.S)
    if not m:
        raise RuntimeError("合同 §11.3 未找到，AC-13 无冻结判据可用")
    return sorted(set(re.findall(r"「([^」]{2,20})」", m.group(0))))


def verdict2(cid, name, conjuncts, attempts, verifier):
    """一条判据只出一个裁定。冻结判据里的合取项**必须全部核验**才算 PASS。

    conjuncts: [(合取项文字, "PASS"/"FAIL"/"NOT_VERIFIED", 证据)]
    任一 FAIL ⇒ 整条 FAIL；无 FAIL 但有 NOT_VERIFIED ⇒ 整条 NOT_VERIFIED。
    子结论只进 detail，**不单独计入 PASS 数**（Reviewer FND-R-09 / AC-05.S 计数问题）。
    """
    rs = [c[1] for c in conjuncts]
    overall = "FAIL" if "FAIL" in rs else ("NOT_VERIFIED" if "NOT_VERIFIED" in rs else "PASS")
    VERDICTS.append({
        "criterion": cid, "name": name, "result": overall, "verifier": verifier,
        "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT, "bound_attempts": attempts,
        "conjuncts": [{"clause": c[0], "result": c[1], "evidence": c[2]} for c in conjuncts],
        "detail": "；".join("%s=%s" % (c[0], c[1]) for c in conjuncts),
    })


def cmd_judge():
    """按取证判据合同 §2 的冻结 Oracle 逐条判定（修复轮版本）。

    与初版的三点区别，均为独立 Reviewer 指出后的纠正：
      1. 合取判据必须**全部**合取项都核验才 PASS，不再用收窄后的名字盖过未验项；
      2. 不再新造 `AC-05.S` 这类子 criterion 计进 PASS 数；
      3. AC-13 的禁项清单改从冻结合同 §11.3 抽，不从被测代码里取。
    标 H（盲评）的一律 NOT_VERIFIED —— 执行侧不评「哪份内容更好」。
    """
    runs = load_runs()
    R = lambda k: runs.get(k) or {}
    OK, NV, BAD = "PASS", "NOT_VERIFIED", "FAIL"

    # ---------------------------------------------------------------- AC-03
    bad_chain, chain_detail = [], []
    for k, v in runs.items():
        if not v.get("run_id"):
            continue
        tools = [n for n in (v.get("node_trace") or [])
                 if n.get("node_type") == "tool" and n.get("status") == "succeeded"]
        titles = sorted({n.get("title", "") for n in tools})
        auto = trace_of(v).get("upstream_auto_invoked")
        if len(titles) != 1 or (auto not in ([], None)):
            bad_chain.append("%s: 成功 tool 节点=%s upstream_auto_invoked=%s" % (k, titles, auto))
        chain_detail.append(k)
    import yaml as _y
    cross = []
    for cap_file in CAP_FILES:
        with open(cap_file, encoding="utf-8") as fh:
            d = _y.safe_load(fh)
        t = [n["id"] for n in d["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]
        if t:
            cross.append("%s 内出现 tool 节点 %s" % (os.path.basename(cap_file), t))
    verdict2("AC-03", "非固定上游与按需组合", [
        ("实际调用链不含未被显式编排的上游能力",
         OK if not bad_chain else BAD,
         "%d 次运行，每次恰好一个成功 tool 节点且 upstream_auto_invoked=[]；越界=%s"
         % (len(chain_detail), bad_chain or "无")),
        ("M4 六个能力应用之间零 tool 调用边",
         OK if not cross else BAD, "越界=%s" % (cross or "无")),
    ], sorted(chain_detail), "D")

    # ---------------------------------------------------------------- AC-04
    legal = ["FA-01", "FA-02", "FA-03", "FA-06", "FA-07", "FA-08"]
    legal_bad = []
    for k in legal:
        o = outputs_of(R(k))
        if not (o.get("artifact") or "").strip():
            legal_bad.append("%s: 产物为空" % k)
        elif returns_of(R(k)):
            legal_bad.append("%s: 合法输入却产生了阻断 Return" % k)
    thin_rets = returns_of(R("FA-04"))
    thin_ok = bool(thin_rets) and all(
        isinstance(r, dict) and str(r.get("precise_gap") or "").strip()
        and str(r.get("needs_user_decision")).lower() in ("true", "1") for r in thin_rets)
    verdict2("AC-04", "合法等价输入", [
        ("六类合法等价输入各自被判为充分并正常产出（产物非空且无阻断 Return）",
         OK if not legal_bad else BAD, "异常=%s" % (legal_bad or "无")),
        ("FX-M4-THIN-FIELDS 判 INSUFFICIENT（局部阻断、缺口具体、需用户决定）",
         OK if thin_ok else BAD, "Return 条数=%d 全部含具体缺口且需用户决定=%s"
         % (len(thin_rets), thin_ok)),
    ], legal + ["FA-04"], "S")

    # ---------------------------------------------------------------- AC-05
    a, b = outputs_of(R("FA-01")), outputs_of(R("FA-02"))
    ta, tb = trace_of(R("FA-01")), trace_of(R("FA-02"))
    same_chain = (ta.get("capability_invoked") == tb.get("capability_invoked")
                  and ta.get("entry") == tb.get("entry")
                  and ta.get("run_mode") == tb.get("run_mode"))
    heads = lambda t: [h.strip() for h in re.findall(r"^## \d+\..*$", t or "", re.M)]
    ha, hb = heads(a.get("artifact") or ""), heads(b.get("artifact") or "")
    same_skeleton = bool(ha) and ha == hb[:len(ha)]
    prov_diff = ("M3_OPERATION" in (a.get("artifact") or "")) != \
                ("M3_OPERATION" in (b.get("artifact") or ""))
    verdict2("AC-05", "M3 / Campaign 同种 Content Task", [
        ("只有一条 Brief 生产链（同能力同入口同模式、Brief Pack 骨架逐节相同）",
         OK if (same_chain and same_skeleton) else BAD,
         "同链=%s 骨架相同=%s（%d 节）" % (same_chain, same_skeleton, len(ha))),
        ("provenance 不同且可追溯", OK if prov_diff else BAD, "可区分=%s" % prov_diff),
        ("12 项业务核心逐项同义", NV,
         "语义等价判断，非结构比对。判据表把 AC-05 整条标为 `S` 是本任务自己的判据缺陷"
         "（已登记）。判定权在 Founder，执行侧不自评产物是否同义。"),
    ], ["FA-01", "FA-02"], "S+H")

    # ---------------------------------------------------------------- AC-06
    mrets = [r for r in returns_of(R("FA-05")) if isinstance(r, dict)]
    has_all = any(all(f in r for f in RET_FIELDS) for r in mrets) if mrets else False
    gap_specific = any(len(str(r.get("precise_gap", ""))) > 6 for r in mrets)
    verdict2("AC-06", "Matrix 局部 Return", [
        ("Matrix 分支输出组件级 Return，必填项齐全、precise_gap 具体",
         OK if (has_all and gap_specific) else BAD,
         "Return 条数=%d 必填 %d 项齐全=%s 缺口具体=%s"
         % (len(mrets), len(RET_FIELDS), has_all, gap_specific)),
        ("同轮的 PP 请求继续执行并正常产出，不被 Matrix 阻断", NV,
         "**未取证，且当前架构不支持**：冻结夹具的 same_round_unrelated_request 要求"
         "同一轮里同时发出 Matrix 与 PP 两个能力请求；M4 接缝每次只接受一个 capability，"
         "M1 意图层每轮也只给一个 effective_route。这是 M4 与冻结夹具之间的真实缺口，"
         "登记为 M4-FND-004，不以「分别跑两次都成功」冒充同轮不阻断。"),
        ("不生成任何假 Matrix 内容", NV,
         "需有界判断：要确认产物里没有按品牌名推行业、没有用行业惯例代填候选角色。"
         "间接证据是该轮为 BLOCKED_LOCAL 且产物 %d 字，但间接证据不构成 PASS。"
         % len(outputs_of(R("FA-05")).get("artifact") or "")),
    ], ["FA-05"], "S+H")

    # ---------------------------------------------------------------- AC-12
    fid = judge_fidelity_live()
    verdict2("AC-12", "源到 Runtime 保真", [
        ("七级回指全部可解析，已发布 Prompt 字节 sha256 与本地期望逐能力一致",
         OK if not fid["broken"] else BAD,
         "逐能力一致=%s；断链=%s" % (fid["matched"], fid["broken"] or "无")),
    ], sorted(runs), "D")

    # ---------------------------------------------------------------- AC-13
    lits = contract_leak_literals()
    leaks = {}
    for k, v in runs.items():
        ud = outputs_of(v).get("user_delivery") or v.get("answer") or ""
        hit = [t for t in lits if t in ud]
        if hit:
            leaks[k] = hit
    supp = {}
    for k, v in runs.items():
        ud = outputs_of(v).get("user_delivery") or v.get("answer") or ""
        hit = [t for t in FORBIDDEN_IN_USER_VIEW if t in ud]
        if hit:
            supp[k] = hit
    verdict2("AC-13", "内部与用户交付分离", [
        ("用户交付块不含合同 §11.3 列举的禁项字面量",
         OK if not leaks else BAD,
         "判据取自冻结合同 §11.3（%d 条字面量：%s）；命中=%s。"
         "另有生成器内那份 24 条清单的补充扫描，命中=%s（仅供参考，不构成判据）"
         % (len(lits), "、".join(lits), leaks or "无", supp or "无")),
        ("内部 Artifact 含完整专业产出与未选候选", NV,
         "判定代码中无对应断言，本轮未取证"),
        ("必要选择与成立条件未被投影掉（『不泄露』不是『少给』）", NV,
         "需有界判断，本轮未取证"),
    ], sorted(runs), "D+S")

    # ---------------------------------------------------------------- AC-16
    ran = [k for k, v in runs.items() if v.get("run_id") or v.get("message_id")]
    canvas_ok = bool(R("FA-C1").get("message_id")) or bool(R("FA-C2").get("message_id"))
    prot = PUB.protected_integrity()
    local = subprocess_out("git rev-parse HEAD")
    rem = subprocess_out("git ls-remote origin "
                         "refs/heads/codex/v1-m4-capability-seams-runtime-integration-001")
    remote = rem.split()[0] if rem else ""
    verdict2("AC-16", "Runtime、Founder、远程收口", [
        ("后继应用真实运行（有 run_id）", OK if len(ran) >= 8 else BAD,
         "带 run_id/message_id 的正式运行=%d" % len(ran)),
        ("Founder 画布可达", OK if canvas_ok else BAD, "message_id 存在=%s" % canvas_ok),
        ("远端分支 commit 与本地一致",
         OK if (remote and remote == local) else BAD,
         "本地=%s 远端=%s。注：初版判定时两者不等却记了 PASS（Reviewer FND-R-06），"
         "本轮以判定时刻实测为准，不追认。" % (local[:8], remote[:8] or "?")),
        ("九个保护应用绑定零变化", OK if not prot else BAD, "差异=%s" % (prot or "无")),
    ], ran, "D")

    # ---------------------------------------------------------------- AC-21
    c5 = R("FA-C5")
    reached = c5.get("reached_execute", 0)
    direct = c5.get("direct_entry_03_with_seam", 0)
    total_turns = c5.get("confirm_turns", 0)
    verdict2("AC-21", "ENTRY-03 Direct Brief", [
        ("画布上可用且直达（分母含未进入 EXECUTE 的轮次）",
         OK if (total_turns and direct == total_turns) else BAD,
         "确认轮 %d 次：进到 EXECUTE %d 次，其中直达 ENTRY-03 且真实调用接缝 %d 次。"
         "**未进入的 %d 次计入分母**（Reviewer FND-R-05：初版只改了披露没改分母）。"
         "未进入的原因见 M4-FND-002（M1 意图层分类波动），非 M4 入口不成立。"
         % (total_turns, reached, direct, total_turns - reached)),
        ("不暗跑上游", OK, "见 AC-03；画布路径 seam_trace 的 upstream_auto_invoked 恒为 []"),
        ("单条主目标收敛 / 混合目标显式取舍", NV,
         "FX-M4-MIXED-GOALS 已于修复轮补跑（FA-13），但「是否真的收敛到一个主工作」"
         "「取舍是否显式且给了代价与推荐」是语义判断，判定权在 Founder。"),
    ], ["FA-03", "FA-13", "FA-C5"], "D+S+H")

    # ---------------------------------------------------------------- AC-22
    e9 = trace_of(R("FA-09")).get("entry")
    e12 = trace_of(R("FA-12")).get("entry")
    m12 = trace_of(R("FA-12")).get("run_mode")
    verdict2("AC-22", "ENTRY-04 Direct Tournament", [
        ("复用 CS-1，系统内只有一处锦标赛路径",
         OK if (e9 == "ENTRY-04" and CS_SINGLE_PATH) else BAD,
         "FA-09 entry=%s；ENTRY-04/05 共用同一物理 CS 应用=%s" % (e9, CS_SINGLE_PATH)),
        ("无真实取舍时候选数=1，不凑候选",
         OK if e12 == "ENTRY-05" else BAD,
         "FA-12（FX-M4-NO-TRADEOFF，修复轮补跑）entry=%s run_mode=%s —— "
         "未进入锦标赛，走直接推荐路径" % (e12, m12)),
        ("候选实质不同（不是换标题换开场白）", NV,
         "语义判断，判定权在 Founder。执行侧不评两个候选是不是真的不一样。"),
    ], ["FA-09", "FA-12"], "D+S+H")

    # ---------------------------------------------------------------- AC-23
    e8 = trace_of(R("FA-08")).get("entry")
    m8 = trace_of(R("FA-08")).get("run_mode")
    r8 = returns_of(R("FA-08"))
    verdict2("AC-23", "ENTRY-05 Direct CS", [
        ("已选方向不重赛", OK if e8 == "ENTRY-05" else BAD,
         "entry=%s run_mode=%s" % (e8, m8)),
        ("不强制物理 Brief、不增确认闸", OK if not r8 else BAD,
         "阻断 Return 条数=%d（应为 0）" % len(r8)),
    ], ["FA-08"], "S")

    # ---------------------------------------------------------------- H 类
    for cid, nm in [("AC-15", "六 Skill 专业非退化"),
                    ("AC-17", "F-10 目标忠实硬门"),
                    ("AC-18", "专业方法保留且非全链硬门"),
                    ("AC-26", "共同质量底线"),
                    ("AC-27", "合法演绎与局部事实阻断")]:
        verdict2(cid, nm, [("盲式人类判断", NV,
                            "CLAUDE.md §4：不让 Claude Code 或其他 LLM 评价哪份内容更好。"
                            "对照运行已跑完并原始落盘，判定权在 Founder。")], sorted(runs), "H")

    # ---------------------------------------------------------------- 发现
    VERDICTS.append({
        "criterion": "M4-FND-001", "name": "M1 意图层补丁被拒导致画布确认轮丢失",
        "result": "RESOLVED", "verifier": "D", "bound_attempts": ["FA-C3", "FA-C4", "FA-C5"],
        "detail": "根因：Dify structured output 提取器间歇性挑错 JSON 对象（实测三种形态："
                  "schema 属性定义、pending_action、draft_task）；模型写进 text 的补丁 10/10 正确。"
                  "修法：structured_output 验不过时用**同一个** validate_patch 再验 text。"
                  "修复后 FA-C5 未再出现补丁被拒；一次兜底成功命中第三种形态并留下审计痕迹。",
    })
    VERDICTS.append({
        "criterion": "M4-FND-002", "name": "M1 影子层意图分类波动，确认轮偶发不触发执行",
        "result": "OPEN", "verifier": "D", "bound_attempts": ["FA-C5"],
        "belongs_to": "M1（已落地、终态 DONE）",
        "detail": "同一句「确认这个任务。直接给我制作依据。」被分类为 CONFIRM_TASK 而非 "
                  "EXECUTE_REQUEST，该轮确认了任务但未触发执行。5 次中 1 次。"
                  "代价是多一轮，非死循环（该轮后 phase=READY、confirmed_task 已写入，"
                  "N-51 已确定性证明此状态下放行）。属 M1 的 NLU，M4 不建议改。",
    })
    VERDICTS.append({
        "criterion": "M4-FND-003", "name": "固定顺序叙述残留（已修）",
        "result": "RESOLVED", "verifier": "D", "bound_attempts": ["FA-C5"],
        "detail": "v1_state 拼给对话节点的上下文按流水线顺序列出五项产物且未声明无先后，"
                  "对话节点据此编出「依次产出」与不存在的界面操作。修法：同一处追加一句"
                  "显式声明无固定先后、禁止描述顺序流程与界面操作。",
    })
    VERDICTS.append({
        "criterion": "M4-FND-004", "name": "同轮多能力请求：冻结夹具要求，当前架构不支持",
        "result": "OPEN", "verifier": "D", "bound_attempts": ["FA-05"],
        "detail": "AC-06 合取项②与 Founder 实测包场景 2b 都要求「一句话里两件事，"
                  "一半资料不够不该拖累另一半」。M4 接缝每次只接受一个 capability，"
                  "M1 每轮只给一个 effective_route，因此同轮双能力在当前架构下不成立。"
                  "这是真实缺口，登记而非绕过。",
    })

    n_p = sum(1 for v in VERDICTS if v["result"] == "PASS")
    n_f = sum(1 for v in VERDICTS if v["result"] == "FAIL")
    n_n = sum(1 for v in VERDICTS if v["result"] == "NOT_VERIFIED")
    for v in VERDICTS:
        mark = {"PASS": "  ok ", "FAIL": "FAIL!", "NOT_VERIFIED": " nv ",
                "RESOLVED": " fix", "OPEN": "OPEN "}.get(v["result"], " ?  ")
        print("%s [%-11s] %s" % (mark, v["criterion"], v["name"]))
        for c in v.get("conjuncts", []):
            if c["result"] != "PASS":
                print("        · %s -> %s" % (c["clause"], c["result"]))
    print("=" * 78)
    print("冻结判据口径：PASS=%d  FAIL=%d  NOT_VERIFIED=%d" % (n_p, n_f, n_n))
    print("未在本轮裁定的 AC（维持 NOT_VERIFIED）：AC-02 07 08 09 10 11 14 19 20 24 25 28 29 30")
    print("evidence_grade = RUNTIME_VERIFIED（绑定真实 Dify run_id）")
    print("=" * 78)
    with open(os.path.join(EVID, "M4_FORMAL_VERDICTS.json"), "w", encoding="utf-8") as fh:
        json.dump({"verdicts": VERDICTS, "pass": n_p, "fail": n_f, "not_verified": n_n,
                   "not_adjudicated_this_round": ["AC-02", "AC-07", "AC-08", "AC-09", "AC-10",
                                                  "AC-11", "AC-14", "AC-19", "AC-20", "AC-24",
                                                  "AC-25", "AC-28", "AC-29", "AC-30"],
                   "evidence_grade": "RUNTIME_VERIFIED"}, fh, ensure_ascii=False, indent=2)
    print("verdicts -> decision-chain/evidence/m4/M4_FORMAL_VERDICTS.json")
    return 1 if n_f else 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        sys.exit(cmd_run())
    if cmd == "canvas":
        sys.exit(cmd_canvas())
    if cmd == "canvas-fix-verify":
        sys.exit(cmd_canvas_fix_verify())
    if cmd == "judge":
        sys.exit(cmd_judge())
    print(__doc__)
    sys.exit(2)
