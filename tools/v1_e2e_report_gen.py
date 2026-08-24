#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由重放记录与评估结果生成 RAW / TRACE / EVAL 三份归档文档。

所有数字来自 `eval_result.json` 与重放 JSONL，不做任何人工誊写。
"""
import argparse, json, os
from collections import Counter, defaultdict

from _repo_paths import ROOT as REPO, rpath  # 目录重组后按文件名解析
CASES = json.load(open(rpath("V1_E2E_CASES_v0.1.json"), encoding="utf-8"))
TITLE = {}
for s in CASES["scenario_replays"]:
    TITLE[s["scenario_id"]] = s["title"]
for c in CASES["e2e_cases"]:
    TITLE[c["case_id"]] = c["group"]


def load_turns(runs):
    turns, finals, retries = defaultdict(list), {}, []
    for suite in ("scenarios", "e2e"):
        p = os.path.join(runs, "replay_%s.jsonl" % suite)
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            rid = r.get("record_id") or ""
            if r.get("retried"):
                retries.append(r)
            elif rid.endswith("#FINAL"):
                finals[r["case"]] = r
            elif r.get("turn"):
                turns[r["case"]].append(r)
    for k in turns:
        turns[k].sort(key=lambda x: x["turn"])
    return turns, finals, retries


def w(path, parts):
    open(path, "w", encoding="utf-8").write("".join(parts))
    print("%-46s %8d 字节" % (os.path.basename(path), os.path.getsize(path)))


def gen_raw(turns, finals, retries, out):
    L = ["""# 笛语 V1 E2E RUN_002 原始记录

> 每一轮的用户输入与用户可见输出**逐字原样**保存，未做润色、删减或重排。
> 失败轮次一律保留，未用成功样本覆盖。供应商未提供的隐藏推理不在此归档，也未伪造。

"""]
    L.append("| 会话 | 轮数 | conversation_id |\n|---|---|---|\n")
    for cid in sorted(turns):
        L.append("| `%s` | %d | `%s` |\n" % (cid, len(turns[cid]),
                 (finals.get(cid) or {}).get("conversation_id") or
                 (turns[cid][0].get("conversation_id") or "")))
    if retries:
        L.append("\n## 基础设施重试记录（首次失败已保留）\n\n| 记录 | 分类 | 错误 |\n|---|---|---|\n")
        for r in retries:
            L.append("| `%s` | %s | %s |\n" % (r.get("record_id"), r.get("failure_class"),
                     ((r.get("transport_error") or "") or "见 node_errors")[:150].replace("|", "/")))
    for cid in sorted(turns):
        L.append("\n---\n\n## %s ｜ %s\n\n" % (cid, TITLE.get(cid, "")))
        for t in turns[cid]:
            st = t.get("state") or {}
            L.append("### %s（route `%s`，%.1f 秒）\n\n" % (
                t["record_id"], st.get("effective_route") or "-", t.get("wall_seconds") or 0))
            L.append("**用户输入**\n\n````text\n%s\n````\n\n" % t.get("query", ""))
            L.append("**用户可见输出**\n\n````text\n%s\n````\n\n" % (t.get("answer") or "（空）"))
            if t.get("node_errors"):
                L.append("**本轮节点错误**\n\n````text\n%s\n````\n\n" %
                         json.dumps(t["node_errors"], ensure_ascii=False, indent=2)[:2500])
    w(os.path.join(out, "V1_E2E_RUN_002_RAW.md"), L)


def gen_trace(turns, finals, out):
    L = ["""# 笛语 V1 E2E RUN_002 执行追踪

> 全部字段取自 Dify 后台 `workflow_runs` / `workflow_node_executions` /
> `workflow_conversation_variables`，不取模型自述。

| 记录 | workflow_run_id | 状态 | route | patch_ok | state_saved | Skill | 节点数 | 服务端秒 | tokens |
|---|---|---|---|---|---|---|---|---|---|
"""]
    for cid in sorted(turns):
        for t in turns[cid]:
            st = t.get("state") or {}
            L.append("| `%s` | `%s` | %s | %s | %s | %s | %s | %d | %s | %s |\n" % (
                t["record_id"], (t.get("workflow_run_id") or "")[:8], t.get("run_status"),
                st.get("effective_route") or "-", st.get("patch_ok"), st.get("state_saved"),
                ",".join(s["skill"] for s in (t.get("skills_called") or [])) or "-",
                len(t.get("node_path") or []), t.get("elapsed"), t.get("total_tokens")))
    L.append("\n## 逐会话终态\n\n| 会话 | matrix | campaign | content_brief |\n|---|---|---|---|\n")
    for cid in sorted(finals):
        s = ((finals[cid].get("final_state") or {}).get("status") or {})
        L.append("| `%s` | %s | %s | %s |\n" % (cid, s.get("matrix"), s.get("campaign"),
                                                s.get("content_brief")))
    L.append("\n## 逐轮节点路径\n\n")
    for cid in sorted(turns):
        L.append("### %s\n\n" % cid)
        for t in turns[cid]:
            L.append("- `%s` → %s\n" % (t["record_id"], " → ".join(t.get("node_path") or []) or "（无）"))
    w(os.path.join(out, "V1_E2E_RUN_002_TRACE.md"), L)


def gen_eval(ev, turns, out):
    res, sh = ev["results"], ev["shadow"]
    sc = {k: v for k, v in res.items() if v["suite"] == "scenarios"}
    e2 = {k: v for k, v in res.items() if v["suite"] == "e2e"}
    cnt = lambda d: Counter(v["verdict"] for v in d.values())
    cs, ce = cnt(sc), cnt(e2)
    wall = sum(t.get("wall_seconds") or 0 for ts in turns.values() for t in ts)
    tok = sum(int(t.get("total_tokens") or 0) for ts in turns.values() for t in ts)

    L = ["""# 笛语 V1 E2E RUN_002 评估

> 本文件的每一条判定都来自确定性核对。**没有任何一条结论由模型给出。**
>
> 判据分两类，分开计分：**AUTO** 由后台事实机器判定，产出 PASS / FAIL；
> **OBSERVED** 只能靠人读回复文本才能判定，**不自动判通过**，证据原样列出。
> 把 OBSERVED 计成 PASS 就是假绿，本文件不这么做。

## A. 总览

| 项 | 值 |
|---|---|
| 十场景重放 | 通过 %d / 失败 %d / 未运行 %d |
| 40 类 E2E | 通过 %d / 失败 %d / 未运行 %d |
| 实际执行轮数 | %d |
| 累计墙钟 | %.1f 分钟 |
| 累计 tokens | %s |
| OBSERVED 待人核项 | %d |
| 基础设施重试次数 | %d |

## B. 影子状态尾部失败率

| 指标 | 值 |
|---|---|
| 有效影子节点轮数 | %d |
| `shadow_patch_success_rate` | %s |
| `fail_open_rate` | %s |
| `empty_turn_rate` | %s |
| `unauthorized_execution_rate` | %s |

节点错误分布：`%s`
错误类型分布：`%s`

""" % (cs.get("PASS", 0), cs.get("FAIL", 0), cs.get("NOT_RUN", 0),
       ce.get("PASS", 0), ce.get("FAIL", 0), ce.get("NOT_RUN", 0),
       sum(len(t) for t in turns.values()), wall / 60.0, "{:,}".format(tok),
       ev.get("observed_total", 0), sh.get("infra_retries", 0),
       sh.get("shadow_node_turns"), sh.get("shadow_patch_success_rate"),
       sh.get("fail_open_rate"), sh.get("empty_turn_rate"),
       sh.get("unauthorized_execution_rate"),
       json.dumps(sh.get("node_error_counts"), ensure_ascii=False),
       json.dumps(sh.get("node_error_kinds"), ensure_ascii=False))]

    for name, d in (("C. 十场景重放逐项", sc), ("D. 40 类 E2E 逐类", e2)):
        L.append("\n## %s\n\n| 用例 | 结果 | 轮数 | 逐轮 route | Skill 调用 | 终态 Artifact |\n|---|---|---|---|---|---|\n" % name)
        for cid in sorted(d):
            v = d[cid]
            L.append("| `%s` | **%s** | %s | %s | %s | %s |\n" % (
                cid, v["verdict"], v.get("turns", "-"),
                " → ".join(str(x) for x in (v.get("routes") or [])) or "-",
                ",".join(v.get("skills") or []) or "-",
                json.dumps({k: x for k, x in (v.get("artifact_final") or {}).items() if x},
                           ensure_ascii=False) or "-"))
    L.append("\n## E. 未通过项逐条\n\n")
    any_fail = False
    for cid in sorted(res):
        v = res[cid]
        if v["verdict"] == "PASS":
            continue
        any_fail = True
        L.append("### %s — %s\n\n" % (cid, v["verdict"]))
        if v["verdict"] == "NOT_RUN":
            L.append("未运行原因：`%s`\n\n" % v.get("reason"))
            continue
        for x in v.get("auto", []):
            if not x["pass"]:
                L.append("- **未通过** `%s`：%s\n" % (x["criterion"], x["detail"]))
        errs = v.get("node_errors") or []
        if errs:
            L.append("\n本用例节点错误：\n\n````text\n%s\n````\n" %
                     json.dumps(errs, ensure_ascii=False, indent=2)[:1800])
        L.append("\n")
    if not any_fail:
        L.append("无。\n")
    L.append("""
## F. OBSERVED 待人核清单

以下判据无法由后台事实机器判定，必须人读回复文本。**本轮不自动判通过。**

| 用例 | 判据 |
|---|---|
""")
    for cid in sorted(res):
        for o in (res[cid].get("observed") or []):
            L.append("| `%s` | `%s` |\n" % (cid, o["criterion"]))
    w(os.path.join(out, "V1_E2E_RUN_002_EVAL.md"), L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--eval", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ev = json.load(open(os.path.join(a.eval, "eval_result.json"), encoding="utf-8"))
    turns, finals, retries = load_turns(a.runs)
    gen_raw(turns, finals, retries, a.out)
    gen_trace(turns, finals, a.out)
    gen_eval(ev, turns, a.out)


if __name__ == "__main__":
    main()
