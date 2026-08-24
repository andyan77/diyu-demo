#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拍摄前生产链 · 两段式控制器 / PRE Chain two-stage controller.

为什么是两段：
    Dify 本机 `WORKFLOW_MAX_EXECUTION_TIME = 1200s`，且该时限只在节点边界
    （NodeRunSucceeded / NodeRunFailed）判定。P02 实测 CS 505.7s + PD 559.6s
    + PP 403.9s = 1469.3s，单链会在 PP 跑完后的边界判定处被 abort——
    三段 token 全部烧掉、汇总与 End 都不执行、产出为零。
    因此拆成 Stage 1（CS→PD，1065.4s）与 Stage 2（PP，403.9s）。
    切点同时对齐业务边界：PP 本就要跑两次（现在 PRE，素材回来后 FINAL）。

本控制器只做三件事，全部确定性：
    1. 调 Stage 1，取回其 End 输出；
    2. 把 Stage 1 的产物与哈希**逐字**塞进 Stage 2 的 Start（数组用 JSON 编码，
       不改写、不摘录、不重排）；
    3. 调 Stage 2，落盘完整记录。

它**不**做：不接受回改、不触发内容层面的重跑、不给任何产物盖 USER_ACCEPTED、
不因产生回改而标下游 STALE、不预填 mode。三个 Skill 一律经 Workflow Tool
在 Dify 内部调用，控制器不接触 Skill 正文，也不在段间人工搬运模型输出。

重试放在这一层，不放在 Tool 节点上：
    单次 LLM 调用受 `PLUGIN_MAX_EXECUTION_TIMEOUT = 600s` 硬顶（超时报
    `PluginDaemonInternalServerError: killed by timeout`）。若把重试配在 Tool 节点上，
    那 600s 的失败会叠进父流同一份 1200s 预算里，把本来跑得完的成功路径挤爆——
    Run 001 就是这样：600.2s 失败 ＋ 重试 397s，父流到 1000s 仍未进 PD。
    改由控制器重发，则重试是一次**全新的父流运行**，另获完整 1200s 预算，
    且第一次失败的 run 记录原样留在 Dify 里，不被覆盖。
    只重试一次，且只针对基础设施失败（TOOL_FAILED / 运行未成功），
    **不因内容原因重跑，也不因产生回改而重跑**。

凭据只从环境变量读，绝不落盘、绝不回显：
    DIFY_BASE_URL              默认 http://localhost/v1
    DIFY_PRE_CHAIN_STAGE1_KEY  Stage 1 应用的 Service API Key
    DIFY_PRE_CHAIN_STAGE2_KEY  Stage 2 应用的 Service API Key

用法：
    python3 pre_chain_controller.py --inputs <九槽位.json> --out <记录.json>
"""
import argparse, hashlib, json, os, sys, time, urllib.request, urllib.error

BASE = os.environ.get("DIFY_BASE_URL", "http://localhost/v1")

# Stage 1 需要的 13 项输入（= 九槽位 ＋ content_brief / available_assets /
# fact_refs / example_reference_requested）
STAGE1_INPUTS = [
    "content_brief", "production_profile", "expression_subject", "content_origin_mode",
    "subject_domain", "duration_band", "platform", "cta_contract",
    "account_positioning", "constraints", "available_assets", "fact_refs",
    "example_reference_requested",
]
# Stage 2 从原始输入里直接沿用的部分。subject_domain 与 duration_band 必须在列：
# 缺 subject_domain 则 PP 的 Reference Projection 选不出行业块、投影节点空跑；
# 缺 duration_band 则 PP-1 的候选取向只能反推，并被迫在 assumptions[] 挂一条
# 本不必要的假设。
STAGE2_PASSTHROUGH = [
    "content_brief", "platform", "cta_contract", "account_positioning",
    "subject_domain", "duration_band", "constraints", "fact_refs",
    "example_reference_requested",
]


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def run_workflow(key, inputs, user, timeout=1800):
    body = json.dumps({"inputs": inputs, "response_mode": "blocking", "user": user},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE.rstrip("/") + "/workflows/run", data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    t0 = time.time()
    try:
        raw = opener.open(req, timeout=timeout).read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code,
                "_body": e.read()[:1500].decode("utf-8", "replace"),
                "_wall": round(time.time() - t0, 1)}
    d = json.loads(raw)
    d["_wall"] = round(time.time() - t0, 1)
    return d


def summarize(tag, resp):
    d = resp.get("data") or {}
    print("[%s] status=%s wall=%ss elapsed=%s tokens=%s run_id=%s" % (
        tag, d.get("status"), resp.get("_wall"), d.get("elapsed_time"),
        d.get("total_tokens"), d.get("id")), flush=True)
    if d.get("error"):
        print("[%s] error=%s" % (tag, str(d["error"])[:400]), flush=True)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--user", default="diyu-pre-chain")
    a = ap.parse_args()

    k1 = os.environ.get("DIFY_PRE_CHAIN_STAGE1_KEY")
    k2 = os.environ.get("DIFY_PRE_CHAIN_STAGE2_KEY")
    if not k1 or not k2:
        sys.exit("缺少 DIFY_PRE_CHAIN_STAGE1_KEY / DIFY_PRE_CHAIN_STAGE2_KEY 环境变量")

    src = json.load(open(a.inputs, encoding="utf-8"))
    missing = [k for k in STAGE1_INPUTS if not str(src.get(k) or "").strip()]
    if missing:
        sys.exit("输入文件缺少: " + ", ".join(missing))

    rec = {"stage1": {}, "stage2": {}, "handoff": {}}

    # ---------- Stage 1: CS -> PD ----------
    in1 = {k: src[k] for k in STAGE1_INPUTS}
    attempts = []
    for attempt in (1, 2):                       # 基础设施失败最多重试一次
        print("[stage1] 发起 CS -> PD …（第 %d 次）" % attempt, flush=True)
        r1 = run_workflow(k1, in1, a.user)
        d1 = summarize("stage1", r1)
        attempts.append({"attempt": attempt, "response": r1})
        o1 = d1.get("outputs") or {}
        if d1.get("status") == "succeeded" and o1.get("creative_script_artifact"):
            break
        if attempt == 1:
            print("[stage1] 第 1 次未成功，记录已保留，重发一次全新父流运行。", flush=True)
    rec["stage1"] = {"request_inputs": in1, "attempts": attempts, "response": r1}
    o1 = (d1.get("outputs") or {})
    if d1.get("status") != "succeeded" or not o1.get("creative_script_artifact"):
        rec["chain_status"] = (o1.get("chain_status") or "STAGE1_FAILED")
        rec["note"] = "Stage 1 未成功，按失败处理，不调用 Stage 2。"
        json.dump(rec, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[chain] " + rec["chain_status"] + " —— 已停止，不调用下游。", flush=True)
        return 1

    cs, pd = o1["creative_script_artifact"], o1["realization_plan_artifact"]
    # 控制器侧独立复算，确认段间搬运逐字无损
    rec["handoff"] = {
        "cs_hash_from_stage1": o1.get("creative_script_hash"),
        "cs_hash_recomputed": sha(cs), "cs_len": len(cs),
        "pd_hash_from_stage1": o1.get("production_plan_hash"),
        "pd_hash_recomputed": sha(pd), "pd_len": len(pd),
    }
    rec["handoff"]["cs_verdict"] = "MATCH" if sha(cs) == o1.get("creative_script_hash") else "MISMATCH"
    rec["handoff"]["pd_verdict"] = "MATCH" if sha(pd) == o1.get("production_plan_hash") else "MISMATCH"
    print("[handoff] cs=%s %s len=%d | pd=%s %s len=%d" % (
        rec["handoff"]["cs_verdict"], sha(cs)[:16], len(cs),
        rec["handoff"]["pd_verdict"], sha(pd)[:16], len(pd)), flush=True)
    if "MISMATCH" in (rec["handoff"]["cs_verdict"], rec["handoff"]["pd_verdict"]):
        rec["chain_status"] = "INPUT_BLOCKED"
        rec["note"] = "Stage 1 产物与其自报哈希不一致，拒绝进入 Stage 2。"
        json.dump(rec, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 1

    # ---------- Stage 2: PP (PRE) ----------
    in2 = {k: src[k] for k in STAGE2_PASSTHROUGH}
    in2.update({
        "cs_final": cs, "cs_hash": o1.get("creative_script_hash"),
        "pd_final": pd, "pd_hash": o1.get("production_plan_hash"),
        # 数组用 JSON 编码原样转运，不摘录、不重排、不改写
        "pd_return_to_script": json.dumps(o1.get("return_to_script") or [], ensure_ascii=False),
        "pd_return_to_production": json.dumps(o1.get("return_to_production") or [], ensure_ascii=False),
        "pd_advisory_notes": json.dumps(o1.get("advisory_notes") or [], ensure_ascii=False),
        "stage1_models": json.dumps(o1.get("stage_models") or [], ensure_ascii=False),
        "stage1_run_status": json.dumps(o1.get("stage_run_status") or [], ensure_ascii=False),
    })
    att2 = []
    for attempt in (1, 2):
        print("[stage2] 发起 PP（PRE）…（第 %d 次）" % attempt, flush=True)
        r2 = run_workflow(k2, in2, a.user)
        d2 = summarize("stage2", r2)
        att2.append({"attempt": attempt, "response": r2})
        if d2.get("status") == "succeeded" and (d2.get("outputs") or {}).get("publishing_pre_artifact"):
            break
        if attempt == 1:
            print("[stage2] 第 1 次未成功，记录已保留，重发一次全新父流运行。", flush=True)
    rec["stage2"] = {"request_inputs": in2, "attempts": att2, "response": r2}
    o2 = d2.get("outputs") or {}
    rec["chain_status"] = o2.get("chain_status") or ("STAGE2_FAILED" if d2.get("status") != "succeeded" else "")
    print("[chain] chain_status = %s | pp_mode = %s" % (
        rec["chain_status"], o2.get("pp_mode")), flush=True)
    json.dump(rec, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[chain] 记录已写入 " + a.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
