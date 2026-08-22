#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""笛语 V1 Demo 自动回归重放器。

对主 Chatflow 走**正式 Dify Service API** 执行真实多轮会话，不做任何静态模拟。
每一轮的判定事实全部取自 Dify 后台（`workflow_runs` / `workflow_node_executions` /
`workflow_conversation_variables`），不取自模型的自述，也不取自用户可见文本。

凭据：只从环境变量 `DIFY_API_KEY`，或 `DIFY_API_KEY_FILE` 指向的文件读取。
     不打印、不写入产物、不写入仓库。

用法：
    python3 v1_demo_e2e_replay.py --suite scenarios --out <dir>
    python3 v1_demo_e2e_replay.py --suite e2e      --out <dir>
    python3 v1_demo_e2e_replay.py --suite both     --out <dir> --resume
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
CASES_FILE = os.path.join(REPO, "V1_E2E_CASES_v0.1.json")

BASE = os.environ.get("DIFY_BASE", "http://localhost/v1")
PG = os.environ.get("DIFY_PG_CONTAINER", "docker-db_postgres-1")
APP_ID = "310ddfcf-e0fb-4211-af98-3d101725e07a"
TOOL_NODES = {"tool_matrix": "matrix", "tool_campaign": "campaign",
              "tool_content_brief": "content_brief"}

# 基础设施失败：允许一次完全相同的重试。
INFRA_PAT = re.compile(
    r"SSLEOFError|UNEXPECTED_EOF_WHILE_READING|NameResolutionError|"
    r"Server Unavailable|Max retries exceeded|Connection aborted|"
    r"Read timed out|502 Bad Gateway|503 Service|504 Gateway", re.I)
# 以下一律不重试，必须计入结果。
NO_RETRY_PAT = re.compile(
    r"Failed to parse structured output|NO_FINAL|JUDGE_VERDICT_MISSING|"
    r"CONTRACT_|FIXTURE_BUNDLE_SHA_MISMATCH|SKILL_SHA_MISMATCH", re.I)


def api_key():
    """显式传入的 DIFY_API_KEY_FILE 优先于环境里可能残留的 DIFY_API_KEY。

    修复记录：首版把 `DIFY_API_KEY` 排在前面，而本机 profile 中本就存在一个属于
    别的应用的同名变量，导致首次冒烟以 HTTP 401 全轮失败（原始失败记录保留为
    `replay_scenarios.FAILED_401_UNAUTHORIZED.jsonl`）。显式参数必须压过隐式环境。
    """
    k = None
    p = os.environ.get("DIFY_API_KEY_FILE")
    if p and os.path.exists(p):
        k = open(p, encoding="utf-8").read().strip()
    if not k:
        k = os.environ.get("DIFY_API_KEY")
    if not k:
        sys.exit("缺少凭据：请设置 DIFY_API_KEY_FILE 或 DIFY_API_KEY。")
    return k


def psql(sql):
    """只读查询 Dify 后台。返回原始 stdout 文本。"""
    r = subprocess.run(
        ["docker", "exec", PG, "psql", "-U", "postgres", "-d", "dify", "-tAc", sql],
        capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError("psql 失败: " + r.stderr.strip()[:400])
    return r.stdout


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- API

def send_turn(key, query, conversation_id, user, timeout=900):
    """流式发送一轮。返回 (answer, message_id, conversation_id, usage, err)。

    用流式而非阻塞：Skill 轮实测可达 250 秒，流式可避免中间层空闲超时。
    """
    body = json.dumps({
        "inputs": {}, "query": query, "response_mode": "streaming",
        "conversation_id": conversation_id or "", "user": user,
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + "/chat-messages", data=body,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"})
    answer, mid, cid, usage, err = [], None, conversation_id, {}, None
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as resp:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                try:
                    ev = json.loads(line[5:].strip())
                except Exception:
                    continue
                et = ev.get("event")
                if et in ("message", "agent_message"):
                    answer.append(ev.get("answer", ""))
                    mid = mid or ev.get("message_id")
                    cid = cid or ev.get("conversation_id")
                elif et == "message_end":
                    mid = mid or ev.get("message_id")
                    cid = cid or ev.get("conversation_id")
                    usage = (ev.get("metadata") or {}).get("usage") or {}
                elif et == "error":
                    err = json.dumps(ev, ensure_ascii=False)[:600]
    except urllib.error.HTTPError as e:
        err = "HTTP %s %s" % (e.code, e.read()[:400].decode("utf-8", "replace"))
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:400])
    return "".join(answer), mid, cid, usage, err


# ------------------------------------------------------------------- 后台确定性读取

def run_facts(message_id):
    """由 message_id 取回该轮 workflow_run 与全部节点执行的确定性事实。"""
    out = {"workflow_run_id": None, "run_status": None, "elapsed": None,
           "total_tokens": None, "total_steps": None, "node_path": [],
           "node_errors": [], "state": {}, "skills_called": [], "run_error": None}
    row = psql("select workflow_run_id from messages where id='%s';" % message_id).strip()
    if not row:
        return out
    out["workflow_run_id"] = row
    r = psql("select status||'|'||coalesce(round(elapsed_time::numeric,2)::text,'')||'|'||"
             "coalesce(total_tokens::text,'')||'|'||coalesce(total_steps::text,'')||'|'||"
             "coalesce(replace(replace(error,chr(10),' '),'|','/'),'') "
             "from workflow_runs where id='%s';" % row).strip()
    if r:
        p = (r.split("|") + [""] * 5)[:5]
        out["run_status"], out["elapsed"] = p[0], p[1]
        out["total_tokens"], out["total_steps"] = p[2], p[3]
        out["run_error"] = p[4] or None
    rows = psql(
        "select node_id||chr(9)||status||chr(9)||coalesce(replace(replace(error,chr(10),' '),chr(9),' '),'') "
        "from workflow_node_executions where workflow_run_id='%s' order by index;" % row)
    for ln in rows.splitlines():
        if not ln.strip():
            continue
        parts = (ln.split("\t") + ["", "", ""])[:3]
        nid, st, er = parts
        out["node_path"].append(nid)
        if er:
            out["node_errors"].append({"node": nid, "status": st, "error": er[:400]})
        if nid in TOOL_NODES:
            out["skills_called"].append({"skill": TOOL_NODES[nid], "status": st})
    st = psql("select outputs from workflow_node_executions "
              "where workflow_run_id='%s' and node_id='v1_state' limit 1;" % row).strip()
    if st:
        try:
            o = json.loads(st)
            out["state"] = {k: o.get(k) for k in
                            ("effective_route", "patch_ok", "reject_reason", "skill_slot",
                             "state_saved", "task_goal", "turn_report", "snapshot_json")}
        except Exception:
            pass
    return out


def tail_message_error(conversation_id):
    """流被截断、拿不到 message_id 时，回后台取该会话最后一条消息的错误文本。

    修复记录：首版在 `message_id` 缺失时直接把整轮记成 SEMANTIC，错误文本随流一起丢失，
    于是一次 `Read timed out` 这类**已登记的传输失败**被误判为语义失败、不予重试。
    显式回查后台可恢复真实错误，分类才不会失真。
    """
    if not conversation_id:
        return ""
    try:
        rows = psql("select coalesce(status,'')||' | '||coalesce(replace(error,chr(10),' '),'') "
                    "from messages where conversation_id='%s' "
                    "order by created_at desc limit 1;" % conversation_id)
        return rows.strip()
    except Exception:
        return ""


def conv_state(conversation_id):
    """会话变量里的权威落定状态（Artifact 状态在状态机之后才写）。"""
    res = {"task_snapshot": None, "artifacts": {}}
    # 逐个变量单独查：Artifact 正文含换行，整表一次查再按行切会把正文截成第一行。
    snapv = psql("select data::json->>'value' from workflow_conversation_variables "
                 "where conversation_id='%s' and data::json->>'name'='task_snapshot_json';"
                 % conversation_id).strip()
    if snapv:
        try:
            res["task_snapshot"] = json.loads(snapv)
        except Exception:
            res["task_snapshot"] = {"_unparsable": snapv[:300]}
    for slot in ("matrix", "campaign", "content_brief"):
        val = psql("select data::json->>'value' from workflow_conversation_variables "
                   "where conversation_id='%s' and data::json->>'name'='%s_artifact';"
                   % (conversation_id, slot))
        val = val[:-1] if val.endswith("\n") else val
        if val:
            res["artifacts"][slot] = {"chars": len(val), "sha256": sha(val)}
    snap = res["task_snapshot"] or {}
    arts = snap.get("artifacts") or {}
    for k in ("matrix", "campaign", "content_brief"):
        a = arts.get(k)
        res.setdefault("status", {})[k] = (a or {}).get("status") if a else None
    return res


def leak_scan(text, markers):
    return {m: text.count(m) for m in markers if text.count(m)}


# ------------------------------------------------------------------------- 执行

def run_conversation(key, label, turns, markers, outf, resume_done):
    """跑完一个独立 conversation。每轮落盘一条 JSONL。"""
    cid, records = None, []
    for i, q in enumerate(turns, 1):
        rid = "%s#T%d" % (label, i)
        if rid in resume_done:
            prev = resume_done[rid]
            cid = prev.get("conversation_id") or cid
            records.append(prev)
            print("  跳过(已完成) %s" % rid, flush=True)
            continue
        attempt, rec = 0, None
        while True:
            attempt += 1
            t0 = time.time()
            ans, mid, cid2, usage, err = send_turn(key, q, cid, "v1-e2e-" + label)
            wall = round(time.time() - t0, 2)
            facts = run_facts(mid) if mid else {}
            rec = {
                "record_id": rid, "case": label, "turn": i, "attempt": attempt,
                "query": q, "query_sha256": sha(q), "answer": ans,
                "answer_chars": len(ans), "wall_seconds": wall,
                "conversation_id": cid2 or cid, "message_id": mid,
                "transport_error": err, "usage": usage,
                "leak_hits": leak_scan(ans, markers),
            }
            rec.update(facts)
            recovered = "" if mid else tail_message_error(cid2 or cid)
            if recovered:
                rec["recovered_backend_error"] = recovered[:600]
            blob = (err or "") + json.dumps(facts.get("node_errors", []), ensure_ascii=False) + \
                   (facts.get("run_error") or "") + recovered
            turn_failed = bool(err) or facts.get("run_status") == "failed" or not mid
            infra = bool(INFRA_PAT.search(blob)) and not NO_RETRY_PAT.search(blob)
            rec["failure_class"] = ("INFRA" if infra else "SEMANTIC") if turn_failed else None
            # 只对「整轮失败且属基础设施」允许一次完全相同的重试。
            if turn_failed and infra and attempt == 1:
                rec["retried"] = True
                records.append(rec)
                outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                outf.flush()
                print("  %s 基础设施失败，按预注册允许重试一次" % rid, flush=True)
                time.sleep(5)
                continue
            break
        cid = rec.get("conversation_id") or cid
        records.append(rec)
        outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        outf.flush()
        print("  %-16s route=%-18s skills=%-28s %5.1fs %s" % (
            rid, (rec.get("state") or {}).get("effective_route") or "-",
            ",".join(s["skill"] for s in rec.get("skills_called", [])) or "-",
            rec["wall_seconds"],
            ("ERR:" + str(rec.get("failure_class"))) if rec.get("failure_class") else ""),
            flush=True)
    final = conv_state(cid) if cid else {}
    tail = {"record_id": "%s#FINAL" % label, "case": label, "turn": None,
            "conversation_id": cid, "final_state": final}
    outf.write(json.dumps(tail, ensure_ascii=False) + "\n")
    outf.flush()
    return records, tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", choices=["scenarios", "e2e", "both"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--only", default="", help="逗号分隔，只跑指定 case_id / scenario_id")
    a = ap.parse_args()

    doc = json.load(open(CASES_FILE, encoding="utf-8"))
    markers = doc["leak_markers"]
    key = api_key()
    os.makedirs(a.out, exist_ok=True)

    jobs = []
    if a.suite in ("scenarios", "both"):
        for s in doc["scenario_replays"]:
            jobs.append((s["scenario_id"], s["turns"]))
    if a.suite in ("e2e", "both"):
        for c in doc["e2e_cases"]:
            if c["turns"]:
                jobs.append((c["case_id"], c["turns"]))
            else:
                jobs.append((c["case_id"], None))
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        jobs = [j for j in jobs if j[0] in want]

    path = os.path.join(a.out, "replay_%s.jsonl" % a.suite)
    done = {}
    if a.resume and os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("record_id") and not r.get("retried"):
                done[r["record_id"]] = r
        print("resume：已载入 %d 条既有记录" % len(done), flush=True)

    t0 = time.time()
    with open(path, "a", encoding="utf-8") as outf:
        for n, (label, turns) in enumerate(jobs, 1):
            if turns is None:
                rec = {"record_id": "%s#SKIP" % label, "case": label,
                       "status": "NOT_RUN_REQUIRES_FAULT_INJECTION"}
                outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                outf.flush()
                print("[%d/%d] %s  预注册为需故障注入，未运行" % (n, len(jobs), label), flush=True)
                continue
            print("[%d/%d] %s  %d 轮" % (n, len(jobs), label, len(turns)), flush=True)
            run_conversation(key, label, turns, markers, outf, done)
    print("完成，用时 %.1f 分钟 → %s" % ((time.time() - t0) / 60.0, path), flush=True)


if __name__ == "__main__":
    main()
