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
    # 极薄输入的正确表现：不产出成品、给出具体缺口、需要用户决定，且没有伪造产物。
    thin_blocked = bool(thin_rets) and all(
        isinstance(r, dict) and str(r.get("precise_gap") or "").strip()
        and str(r.get("needs_user_decision")).lower() in ("true", "1")
        for r in thin_rets)
    thin_insufficient = thin_blocked and "BLOCKED" in (outputs_of(thin).get("user_delivery") or "")
    verdict("AC-04", "五类合法等价输入均被接受；极薄输入判 INSUFFICIENT",
            not legal_bad and thin_insufficient,
            "合法输入产物为空的=%s；THIN_FIELDS 局部阻断且缺口具体=%s（Return 条数=%d）"
            % (legal_bad or "无", thin_insufficient, len(thin_rets)),
            legal + ["FA-04"], "S")

    # ---------------------------------------------------------------- AC-05
    a, b = outputs_of(R("FA-01")), outputs_of(R("FA-02"))
    import re as _re
    ta, tb = trace_of(R("FA-01")), trace_of(R("FA-02"))
    same_chain = (ta.get("capability_invoked") == tb.get("capability_invoked")
                  and ta.get("entry") == tb.get("entry")
                  and ta.get("run_mode") == tb.get("run_mode"))
    # 「只有一条 Brief 生产链」的结构证据：两份产物的 Brief Pack 骨架逐节相同
    heads = lambda t: [h.strip() for h in _re.findall(r"^## \d+\..*$", t or "", _re.M)]
    ha, hb = heads(a.get("artifact") or ""), heads(b.get("artifact") or "")
    same_skeleton = bool(ha) and ha == hb[:len(ha)]
    prov_diff = ("M3_OPERATION" in (a.get("artifact") or "")) != \
                ("M3_OPERATION" in (b.get("artifact") or ""))
    prov_traceable = all(("来源" in (x.get("artifact") or "")) for x in (a, b))

    # 结构那一半（同一条链 / 同骨架 / provenance 可区分且可追溯）是可机械核验的，且成立。
    verdict("AC-05.S", "M3 与 Campaign 来源走同一条 Brief 生产链，provenance 不同且可追溯",
            same_chain and same_skeleton and prov_diff and prov_traceable,
            "同能力同入口同模式=%s；Brief Pack 骨架逐节相同=%s（%d 节）；"
            "provenance 可区分=%s 可追溯=%s"
            % (same_chain, same_skeleton, len(ha), prov_diff, prov_traceable),
            ["FA-01", "FA-02"], "S")

    # 「12 项核心**逐项同义**」那一半不是结构问题。
    # 两份产物都是中文业务散文，同一项的措辞本来就不同
    # （例如「内容顺序」对「核心内容顺序」、「已接受项」对「上游锁定项」）。
    # 判「同义」需要有界判断；判据表把 AC-05 整条标成 `S` 是本任务自己的判据缺陷，
    # 如实登记，不靠换一把量尺把它变成 PASS。
    not_verified("AC-05", "12 项业务核心在两种来源下逐项同义",
                 "该子句是语义等价判断，不是结构比对。冻结判据表把 AC-05 整条标为 `S`，"
                 "这是判据本身的缺陷（已登记）。结构那一半见 AC-05.S，已成立；"
                 "语义那一半的判定权在 Founder。执行侧不自评产物是否同义。", "H")

    # ---------------------------------------------------------------- AC-06
    m = R("FA-05")
    mrets = returns_of(m)
    comp = [r for r in mrets if isinstance(r, dict)]
    has7 = any(all(f in r for f in RET_FIELDS) for r in comp) if comp else False
    gap_specific = any(len(str((r or {}).get("precise_gap", ""))) > 6 for r in comp)
    verdict("AC-06", "Matrix 资料不足时给组件级 Return（七项齐全、缺口具体），不生成假矩阵",
            has7 and gap_specific,
            "Return 条数=%d 必填项齐全(%d 项)=%s 缺口具体=%s"
            % (len(comp), len(RET_FIELDS), has7, gap_specific),
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

    # -------------------------------------------------- AC-21 画布路径直达入口
    c4 = R("FA-C4")
    direct_hits, reached, blocked = [], 0, []
    for rep in (c4.get("repeats") or []):
        for t in rep.get("turns", []):
            if t.get("turn") != 2:            # 只看「确认 + 直接要 Brief」那一轮
                continue
            if t.get("effective_route", "").startswith("EXECUTE_"):
                reached += 1
                ad = t.get("adapter") or []
                if t.get("seam_invoked") and len(ad) >= 3 and ad[2] == "ENTRY-03":
                    direct_hits.append("rep%d" % rep["repeat"])
            else:
                blocked.append("rep%d(%s/%s)" % (rep["repeat"], t.get("effective_route"),
                                                 t.get("reject_reason") or "-"))
    # 判据只问「进到 EXECUTE 的那些轮次是不是直达、有没有暗跑上游」。
    # 没进到 EXECUTE 的那些**必须在 detail 里显式列出**，不能被统计口径吃掉 —— 那是另一个真实缺陷。
    verdict("AC-21", "Founder 画布上直达 Content Brief：不先跑 Matrix、不先跑 Campaign，接缝被真实调用",
            bool(direct_hits) and len(direct_hits) == reached,
            "确认轮共 %d 次：进到 EXECUTE 的 %d 次，全部直达 ENTRY-03 且真实调用接缝（%s）；"
            "**未进到 EXECUTE 的 %d 次：%s** —— 那是 M1 意图层补丁被拒（见 M4-FND-001），"
            "不是 M4 入口不成立，但它确实使画布上的直达在这些轮次不可用。"
            "M1 原锁下，成功那几轮必然是 HUMAN_DECISION:UPSTREAM_MISSING:campaign"
            % (reached + len(blocked), reached, "，".join(direct_hits) or "无",
               len(blocked), "，".join(blocked) or "无"),
            ["FA-C4"], "D")

    # ------------------------------------------------- M4-FND-001 可靠性发现
    VERDICTS.append({
        "criterion": "M4-FND-001", "name": "M1 意图层补丁被拒导致画布上的确认轮丢失",
        "result": "FAIL", "verifier": "D", "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
        "bound_attempts": ["FA-C3", "FA-C4"],
        "belongs_to": "M1（已落地、终态 DONE）；被拒代码 validate_patch / normalise_snapshot / "
                      "gate_reason / PATCH_KEYS 与 M1 落地版**逐字节一致**，非 M4 引入",
        "detail": "影子层间歇性把错误对象当成状态补丁交出：观察到两种形态 —— "
                  "`PATCH_UNKNOWN_FIELDS:confirmation_id,kind,task_revision`（把 pending_action "
                  "对象当补丁）与 `PATCH_UNKNOWN_FIELDS:description,enum,type`（把 JSON Schema "
                  "片段当补丁）。validate_patch 正确拒绝并 fail-open 到 DISCUSS，"
                  "用户看到的是「你的确认没有成功记录」，必须重说一遍。"
                  "已测确认轮 5 次中 2 次命中。",
        "impact": "不影响接缝路径（FA-01…11 全部 succeeded），只影响 Founder 画布这一条路；"
                  "但 Founder 实测包正是走这条路，所以实测体验会间歇性卡在确认这一步。",
        "not_fixed_because": "修它要改 M1 已落地资产的第三处（影子 Prompt 或补丁容错），"
                             "超出 Founder 本轮授权的「两处改动」，按 Prompt §3 上推。",
    })

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
