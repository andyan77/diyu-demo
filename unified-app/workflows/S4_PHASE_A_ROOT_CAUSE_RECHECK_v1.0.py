#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase A｜规范任务状态载体根因复核。**零模型调用**。

规划侧 CONTINUE EXECUTION PROMPT v1.0 第三节列了九条必须先确认的现场事实。
本模块逐条用**已有 T1–T6 原始证据 + 当前 uapp_fields 代码**确定性复核，
任一条与现场不符就 FAIL，调用方必须停在 CHECKPOINT，不得进入修复。

证据只来自三处，不来自模型自述：
  1 unified-app/evidence/stages/s4_narrow_chain/S4-NC-T{1..6}.json 的 node_detail
  2 unified-app/workflows/S4_BUILD_v1.0.py 里 FIELDS_SRC 的真实源码（原地 exec 后重放）
  3 content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md 逐字引用
  4 候选应用已发布图（只读 select，判断 stale_downstream 有没有下游消费者）

    python3 S4_PHASE_A_ROOT_CAUSE_RECHECK_v1.0.py
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
NC = os.path.join(ROOT, "unified-app/evidence/stages/s4_narrow_chain")
BUILD = os.path.join(HERE, "S4_BUILD_v1.0.py")
CONTRACT = os.path.join(ROOT, "content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md")
CANDIDATE = "85c01f85-a081-43e9-ab09-9993289cc200"
OUT = os.path.join(ROOT, "unified-app/evidence/stages/s4_canonical_state",
                   "S4_PHASE_A_ROOT_CAUSE_RECHECK.json")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def load_fields_module():
    """把当前线上 uapp_fields 的源码原样取出来跑。不重写、不改写。"""
    src = io.open(BUILD, encoding="utf-8").read()
    m = re.search(r"FIELDS_SRC = r'''(.*?)'''", src, re.S)
    assert m, "FIELDS_SRC 取不到"
    body = m.group(1)
    ns = {}
    exec(compile(body, "<uapp_fields>", "exec"), ns)
    return ns, hashlib.sha256(body.encode("utf-8")).hexdigest()


def turn(t):
    return json.load(io.open(os.path.join(NC, "S4-NC-T%d.json" % t), encoding="utf-8"))


def node(d, nid):
    for n in d["node_detail"]:
        if n.get("node_id") == nid:
            return n
    return None


def io_of(d, nid):
    n = node(d, nid)
    if not n:
        return None, None
    return json.loads(n["inputs"] or "{}"), json.loads(n["outputs"] or "{}")


def main():
    ns, fields_sha = load_fields_module()
    T = {t: turn(t) for t in range(1, 7)}
    F = {}
    for t in range(1, 7):
        i, o = io_of(T[t], "uapp_fields")
        F[t] = {"in": i, "out": o, "carrier": json.loads(o["task_fields_json"])}

    R = []

    def rec(cid, name, ok, detail):
        R.append({"id": cid, "name": name, "result": "PASS" if ok else "FAIL", "detail": detail})

    # A-01 T6 的真实上游是 CREATIVE_SCRIPT，9031 字 PP 属 PRE 短入口，不是 PD→PP 血缘
    cs_art = T[4]["conversation_variables_after_turn"]["uapp_last_artifact"]
    after5 = T[5]["conversation_variables_after_turn"]
    seam6_in, _ = io_of(T[6], "uapp_seam")
    env6 = seam6_in["capability_call"]
    m = re.search(r"^`content_body_or_beats`: (.*)$", env6, re.M)
    body6 = m.group(1) if m else ""
    pd_out = None
    for t in (5,):
        _, so = io_of(T[t], "uapp_seam")
        pd_out = (so or {}).get("artifact") or ""
    ok = (after5["uapp_last_capability"].get("head") == "CREATIVE_SCRIPT"
          and after5["uapp_last_artifact"]["len"] == cs_art["len"] == 6843
          and body6.startswith("# Creative Script 完整产出")
          and len(pd_out or "") == 0)
    rec("A-01", "T6 PP 的上游是 CS 不是 PD；PD 无产物", ok, {
        "uapp_last_capability_after_T5": after5["uapp_last_capability"].get("head"),
        "uapp_last_artifact_len_after_T4": cs_art["len"],
        "uapp_last_artifact_len_after_T5": after5["uapp_last_artifact"]["len"],
        "T6_content_body_or_beats_head": body6[:60],
        "T5_seam_artifact_len": len(pd_out or ""),
        "T6_pp_artifact_len": T[6]["conversation_variables_after_turn"]["uapp_last_artifact"]["len"],
        "结论": "9031 字 PP 由 CS artifact 直达生成，属 PRE 短入口，不是完整 PD→PP 血缘"})

    # A-02 uapp_fields 当前以文本正则解析字段，没有规范字段表
    src = io.open(BUILD, encoding="utf-8").read()
    body = re.search(r"FIELDS_SRC = r'''(.*?)'''", src, re.S).group(1)
    has_regex = "FIELD_LINE = re.compile" in body and "`([A-Za-z_][A-Za-z0-9_]*)`" in body
    has_spec = bool(re.search(r"FIELD_SPECS|canonical_id|CANONICAL", body))
    rec("A-02", "字段靠文本正则识别，无规范字段表", has_regex and not has_spec, {
        "FIELD_LINE": [l for l in body.split("\n") if "FIELD_LINE = " in l],
        "含 canonical/FIELD_SPECS": has_spec, "uapp_fields_src_sha256": fields_sha})

    # A-03 E 级字段能在后续轮次补缺口
    e_carried = []
    for t in range(2, 7):
        prev = F[t - 1]["carrier"]["fields"]
        for k in (F[t]["out"]["carried_fields"] or "").split(","):
            if k and (prev.get(k) or {}).get("lvl") == "E":
                e_carried.append({"turn": t, "field": k, "lvl": "E",
                                  "set_at_turn": prev[k]["turn"], "value": prev[k]["v"][:40]})
    rec("A-03", "E 级（模型抽取）字段可以补后续轮次缺口", len(e_carried) > 0, {"实例": e_carried})

    # A-04 缺失占位符被当成非空值
    PLACE = re.compile(r"未明确写出|未声明|UNDECLARED|UNKNOWN|待确认|无法确定|未提供")
    ph = []
    for t in range(1, 7):
        for k, v in F[t]["carrier"]["fields"].items():
            if PLACE.search(v["v"]):
                ph.append({"turn": t, "field": k, "lvl": v["lvl"], "value": v["v"]})
    ph_carried = [x for x in e_carried if any(p["field"] == x["field"] for p in ph)]
    rec("A-04", "缺失占位符作为真实值入载体并被跨轮携带", len(ph) > 0 and len(ph_carried) > 0, {
        "占位值": ph[:6], "被携带的占位值": ph_carried})

    # A-05 别名没有规范身份
    alias = {"gap 前缀被 rsplit 掉":
             [{"turn": t, "raw_gap": F[t]["in"]["gaps_text"], "out_gap": F[t]["out"]["gaps_text"]}
              for t in (1, 3) if "objective." in (F[t]["in"]["gaps_text"] or "")]}
    # goal_family 在外壳里是非反引号写法，永远进不了载体
    seam_env = {}
    for t in range(1, 7):
        si, _ = io_of(T[t], "uapp_seam")
        seam_env[t] = si.get("capability_call") or ""
    gf_backtick = any(re.search(r"^\s*`goal_family`\s*:", seam_env[t], re.M) for t in range(1, 7))
    gf_plain = [t for t in range(1, 7) if re.search(r"^\s*goal_family\s*:", seam_env[t], re.M)]
    gf_in_carrier = any("goal_family" in F[t]["carrier"]["fields"] for t in range(1, 7))
    gf_still_gap = [t for t in range(1, 7) if "goal_family" in (F[t]["out"]["gaps_text"] or "")]
    dup_subject = sorted(set(k for t in range(1, 7) for k in F[t]["carrier"]["fields"]
                             if k.startswith("expression_subject")))
    ok = (not gf_backtick) and gf_plain and (not gf_in_carrier) and gf_still_gap and len(dup_subject) > 1
    rec("A-05", "字段别名无规范身份：goal_family 非反引号永不入载体；同义槽位并存", ok, {
        "goal_family 有反引号写法": gf_backtick, "goal_family 无反引号出现的轮次": gf_plain,
        "goal_family 进过载体": gf_in_carrier, "goal_family 仍是缺口的轮次": gf_still_gap,
        "同义并存槽位": dup_subject, **alias})

    # A-06 运营 time_window 与生产 time_window 无作用域隔离
    tw = None
    for t in range(1, 7):
        if "time_window" in F[t]["carrier"]["fields"]:
            tw = F[t]["carrier"]["fields"]["time_window"]
            break
    tw_carried_to_pd = "time_window" in (F[5]["out"]["carried_fields"] or "").split(",")
    fixture_cycle = "四周内" in tw["v"] if tw else False
    rec("A-06", "运营周期时间窗被原样当成生产时间窗", bool(tw) and tw_carried_to_pd and fixture_cycle, {
        "载体 time_window": tw, "T5 目标能力": T[5]["expect_capability"],
        "T5 carried_fields": F[5]["out"]["carried_fields"],
        "夹具原文": "当前经营任务：初秋通勤衣橱第一阶段上新……四周内目标",
        "结论": "'四周内' 是运营周期窗口，被无作用域区分地补进 PRODUCTION_DIRECTOR 的 time_window"})

    # A-07 用户主动纠正未被询问的字段时，旧值覆盖新值（确定性重放）
    prev = json.dumps(F[5]["carrier"], ensure_ascii=False)
    old_cp = F[5]["carrier"]["fields"]["content_promise"]["v"]
    corrected = "改口：这条只讲怎么判断，不讲方法论，也不提衣橱使用率。"
    probe_env = "provenance:\n  target_capability: PUBLISHING_PACKAGING\n`content_promise`: %s\n" % corrected
    out = ns["main"](prev, F[5]["carrier"]["task_key"], probe_env, "无", "PUBLISHING_PACKAGING")
    reverted = old_cp in out["capability_call"] and corrected not in out["capability_call"]
    c2 = json.loads(out["task_fields_json"])
    kept_old = c2["fields"]["content_promise"]["v"] == old_cp
    no_stale = not c2["stale"]
    rec("A-07", "用户主动纠正未被询问的字段时旧值覆盖新值，且不产生 STALE",
        reverted and kept_old and no_stale, {
            "载体旧值": old_cp[:50], "用户纠正值": corrected,
            "合成后外壳采用的是": "旧值" if reverted else "新值",
            "载体保留的是": "旧值" if kept_old else "新值",
            "held_fields": out["held_fields"], "stale_downstream": out["stale_downstream"],
            "重放来源": "T5 后真实载体 + 当前线上 uapp_fields 源码，零模型调用"})

    # A-08 stale_downstream 有没有下游消费者
    graph = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                            "where a.id='%s';" % CANDIDATE))
    blob = json.dumps(graph, ensure_ascii=False)
    refs = re.findall(r"uapp_fields[^\"]{0,40}stale_downstream|stale_downstream", blob)
    producers = [n["id"] for n in graph["nodes"]
                 if "stale_downstream" in json.dumps(n, ensure_ascii=False)]
    consumers = [p for p in producers if p != "uapp_fields"]
    rec("A-08", "stale_downstream 只被产出，无任何下游消费者", len(consumers) == 0, {
        "出现 stale_downstream 的节点": producers, "消费者": consumers,
        "结论": "它不进入任何变量赋值、条件分支或下游入参，因此不能阻止旧 artifact 继续向下游传播"})

    # A-09 Production Profile 合同：缺失时询问，人给出，默认值只在无人可问时才允许
    txt = io.open(CONTRACT, encoding="utf-8").read()
    q1 = "| `production_profile` | Production Profile | 询问 |"
    q2 = "在真实生产运行开始前必须由人给出"
    q3 = "在**工作流无人可问**时才允许使用"
    q4 = "生产运行不得把这些默认值当成上游已确认输入"
    hits = {k: (k in txt) for k in (q1, q2, q3, q4)}
    rec("A-09", "PD 合同：production_profile 缺失时询问、必须由人给出", all(hits.values()),
        {"逐字命中": hits, "文件": os.path.relpath(CONTRACT, ROOT),
         "sha256": hashlib.sha256(io.open(CONTRACT, "rb").read()).hexdigest(),
         "结论": "T5 追问制作规模符合合同；上一轮 N-07 的 FAIL 属冻结场景未提供该输入，不是 PD 越权"})

    npass = sum(1 for x in R if x["result"] == "PASS")
    rep = {"document": {"id": "S4_PHASE_A_ROOT_CAUSE_RECHECK_v1.0",
                        "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
                        "model_calls": 0, "dify_writes": 0,
                        "evidence_scope": "已有 T1–T6 原始 node_detail + 当前 uapp_fields 源码 + 只读 select",
                        "uapp_fields_src_sha256": fields_sha},
           "summary": {"pass": npass, "total": len(R),
                       "verdict": "PASS" if npass == len(R) else "FAIL"},
           "checks": R}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    for x in R:
        print("%-5s %-4s %s" % (x["id"], x["result"], x["name"]))
    print("---- %d/%d ----" % (npass, len(R)))
    print(os.path.relpath(OUT, ROOT))
    return 0 if npass == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
