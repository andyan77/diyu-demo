#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜Phase E 点对点模型验证运行器 v1.1。**只发起、只记录，不判定。**

v1.1 相对 v1.0 只改一处：**D3 分支的夹具上传调用**。授权来源 =
unified-app/docs/PPBS_B2_FAILURE_TRIAGE_003_D3_TRANSPORT.md 的 mutation_target
＋ Founder 2026-08-30「授权重跑 D3」。判据、输入、b2 实现一律不动。

v1.0 的缺陷（该分支本次之前从未被执行过）：
  fx = R.upload("file", FIXTURE, user)
      ① upload() 第一参是 **API Key**，传了字面量 "file" → Authorization: Bearer file → 401
      ② upload() 返回 (status, body) **元组**，未解包；元组非空即为真，
         于是 {"upload_file_id": (401, {...})} 被塞进 files[] → 服务端参数校验 400
v1.1：用与 chat 同一把 app key 上传；解包 (status, body)；
      **上传不成功就中止，绝不带着坏 payload 去发起顶层调用**（保护最后一次 run 预算）。

    python3 PPBS_B2_D_RUNNER_v1.1.py D3 --preflight   # 只上传并自检，不发起对话
    python3 PPBS_B2_D_RUNNER_v1.1.py D3               # 复用 preflight 的 file_id 发起一次

输入在 unified-app/stages/PPBS_INPUTS_v1.0.json 已冻结并提交（调用之前）。
本文件不读通过条件，不做任何判定。判定由 PPBS_D_ADJUDICATE 按冻结 Gate 另行重算。

    python3 PPBS_B2_D_RUNNER_v1.1.py D1
    python3 PPBS_B2_D_RUNNER_v1.1.py D2
    python3 PPBS_B2_D_RUNNER_v1.1.py D3
"""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
INPUTS = os.path.join(UAPP, "stages", "PPBS_INPUTS_v1.0.json")
GATE = os.path.join(UAPP, "stages", "PPBS_GATE_v2.0.json")
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
FIXTURE = os.path.join(REPO, "decision-chain/fixtures/一页纸夹具品牌事实 v0.1.md")

_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(REPO, "account-operations/tools/dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)
_r = importlib.util.spec_from_file_location("s42run", os.path.join(HERE, "S4_2_RUN_v1.0.py"))
R = importlib.util.module_from_spec(_r)
_r.loader.exec_module(R)


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def node_detail(run_id):
    raw = psql("select coalesce(json_agg(json_build_object('idx',e.index,'node_id',e.node_id,"
               "'title',e.title,'type',e.node_type,'status',e.status,'error',e.error,"
               "'inputs',e.inputs,'outputs',e.outputs) order by e.index)::text,'[]') "
               "from workflow_node_executions e where e.workflow_run_id='%s';" % run_id)
    return json.loads(raw or "[]")


def llm_count(t0, t1):
    raw = psql("select coalesce(json_agg(x)::text,'[]') from (select e.status, count(*) c "
               "from workflow_node_executions e where e.node_type='llm' "
               "and e.created_at between timestamp '%s' and timestamp '%s' group by e.status) x;"
               % (t0, t1))
    return json.loads(raw or "[]")


def harvest(which, run_id):
    """从只读运行库收割一次**已经发生**的运行。不发起任何新调用。"""
    row = psql("select app_id||'\u0001'||status||'\u0001'||created_at::text||'\u0001'||"
               "elapsed_time::text||'\u0001'||coalesce(outputs,'')||'\u0001'||"
               "coalesce(inputs,'') from workflow_runs where id='%s';" % run_id)
    app_id, status, created, elapsed, outs, ins = row.split("\u0001", 5)
    frozen = json.load(io.open(INPUTS, encoding="utf-8"))
    key = "D1_positive" if which == "D1" else "D2_conflict_negative"
    spec = frozen[key]
    got = json.loads(ins or "{}")
    rec = {"case": which, "harvested_from_readonly_db": True,
           "why_harvested": "运行器在解包 HTTP 返回值时抛错，但调用已真实完成；"
                            "按 retries=0 不重跑，从只读运行库还原该次运行。",
           "inputs_sha256": shaf(INPUTS), "gate_sha256": shaf(GATE),
           "workflow_run_id": run_id, "app_id": app_id, "run_status": status,
           "created_at": created, "elapsed_seconds": float(elapsed), "attempts": 1,
           "http_status": 200,
           "input_matches_frozen": {k: sha(got.get(k)) == sha(spec["inputs"][k])
                                    for k in spec["inputs"]},
           "end_user": got.get("sys.user_id"),
           "outputs": json.loads(outs or "{}"),
           "node_detail": node_detail(run_id),
           "pp_provider_pin_at_run": psql("select p.version from tool_workflow_providers p "
                                          "where p.name='diyu_m5fp_publishing_packaging';"),
           "pp_published_version_at_run": psql(
               "select w.version from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % PP_APP),
           "pp_graph_md5_at_run": psql(
               "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % PP_APP)}
    rec["llm_node_executions_in_run"] = [
        {"node_id": n["node_id"], "status": n["status"]}
        for n in rec["node_detail"] if n["type"] == "llm"]
    p = os.path.join(EVDIR, "PPBS_B2_%s_RAW.json" % which)
    os.makedirs(EVDIR, exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
    print("%s 收割 run=%s status=%s %.1fs 输入与冻结一致=%s LLM=%s"
          % (which, run_id, status, float(elapsed),
             all(rec["input_matches_frozen"].values()), rec["llm_node_executions_in_run"]))
    return 0


PREFLIGHT_ONLY = False


def main():
    global PREFLIGHT_ONLY
    PREFLIGHT_ONLY = "--preflight" in sys.argv
    if len(sys.argv) > 2 and sys.argv[2] == "--harvest":
        return harvest(sys.argv[1].upper(), sys.argv[3])
    which = (sys.argv[1] if len(sys.argv) > 1 else "").upper()
    if which not in ("D1", "D2", "D3"):
        raise SystemExit("用法：PPBS_B2_D_RUNNER_v1.1.py D1|D2|D3")
    frozen = json.load(io.open(INPUTS, encoding="utf-8"))
    env = DC.load_env(ENV)
    t0 = psql("select now()::text;")
    rec = {"case": which, "inputs_sha256": shaf(INPUTS), "gate_sha256": shaf(GATE),
           "window_start": t0, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}

    if which in ("D1", "D2"):
        key = "D1_positive" if which == "D1" else "D2_conflict_negative"
        spec = frozen[key]
        pin = psql("select p.version from tool_workflow_providers p "
                   "where p.name='diyu_m5fp_publishing_packaging';")
        rec["pp_provider_pin_at_run"] = pin
        rec["pp_published_version_at_run"] = psql(
            "select w.version from workflows w join apps a on a.workflow_id=w.id "
            "where a.id='%s';" % PP_APP)
        rec["pp_graph_md5_at_run"] = psql(
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
            "where a.id='%s';" % PP_APP)
        akey = DC.Console(env=env).app_api_key(PP_APP)
        payload = {"inputs": spec["inputs"], "response_mode": "blocking",
                   "user": "ppbsb2-%s-%s" % (which.lower(), time.strftime("%Y%m%d%H%M%S"))}
        rec["end_user"] = payload["user"]
        t = time.time()
        r = DC.http_json("POST", "/v1/workflows/run",
                         headers={"Authorization": "Bearer " + akey,
                                  "Content-Type": "application/json"},
                         body=payload, timeout=1800)
        st = r["status"]
        try:
            body = json.loads(r["body"])
        except Exception:
            body = {"_raw": r["body"][:2000]}
        rec["http_status"] = st
        rec["elapsed_seconds"] = round(time.time() - t, 2)
        rec["attempts"] = 1
        data = (body or {}).get("data") or {}
        rec["workflow_run_id"] = data.get("id") or (body or {}).get("workflow_run_id")
        rec["run_status"] = data.get("status")
        rec["outputs"] = data.get("outputs") or {}
        if rec["workflow_run_id"]:
            rec["node_detail"] = node_detail(rec["workflow_run_id"])
    else:
        spec = frozen["D3_unified_entry"]
        rec["pp_provider_pin_at_run"] = psql(
            "select p.version from tool_workflow_providers p "
            "where p.name='diyu_m5fp_publishing_packaging';")
        rec["pp_provider_pinned_graph_md5_at_run"] = psql(
            "select md5(graph) from workflows where app_id='%s' and version="
            "(select version from tool_workflow_providers where "
            "name='diyu_m5fp_publishing_packaging');" % PP_APP)
        rec["pp_published_version_at_run"] = psql(
            "select w.version from workflows w join apps a on a.workflow_id=w.id "
            "where a.id='%s';" % PP_APP)
        akey = DC.Console(env=env).app_api_key(CAND)

        # —— 夹具上传（v1.1 修复点）——
        # 与 chat 同一把 app key；解包 (status, body)；不成功即中止，不发起顶层调用。
        pf = os.path.join(EVDIR, "PPBS_B2_D3_PREFLIGHT.json")
        if os.path.exists(pf) and not PREFLIGHT_ONLY:
            up = json.load(io.open(pf, encoding="utf-8"))
            up["reused_from_preflight"] = True
        else:
            st_up, body_up = R.upload(akey, FIXTURE, spec["end_user"])
            up = {"http_status": st_up, "file_id": (body_up or {}).get("id"),
                  "name": os.path.basename(FIXTURE),
                  "sha256": hashlib.sha256(io.open(FIXTURE, "rb").read()).hexdigest(),
                  "reused_from_preflight": False,
                  "response_head": str(body_up)[:300]}
            os.makedirs(EVDIR, exist_ok=True)
            io.open(pf, "w", encoding="utf-8").write(
                json.dumps(up, ensure_ascii=False, indent=1) + "\n")
        rec["uploaded_fixture"] = up
        if up["http_status"] not in (200, 201) or not up.get("file_id"):
            raise SystemExit("夹具上传失败，拒绝发起顶层调用（保护 run 预算）：%s %s"
                             % (up["http_status"], up.get("response_head")))
        if PREFLIGHT_ONLY:
            print("PREFLIGHT ok | upload http=%s file_id=%s sha256=%s"
                  % (up["http_status"], up["file_id"], up["sha256"][:16]))
            print("PP 当前发布=%s | provider 钉住的图=%s"
                  % (rec["pp_published_version_at_run"],
                     rec["pp_provider_pinned_graph_md5_at_run"]))
            print("会话=%s end_user=%s" % (spec["conversation_id"], spec["end_user"]))
            print("未发起 /v1/chat-messages。顶层 run 预算未消耗。")
            return 0

        payload = {"query": spec["query"], "inputs": {}, "response_mode": "blocking",
                   "user": spec["end_user"], "conversation_id": spec["conversation_id"],
                   "files": [{"type": "document", "transfer_method": "local_file",
                              "upload_file_id": up["file_id"]}]}
        rec["end_user"] = spec["end_user"]
        rec["query"] = spec["query"]
        t = time.time()
        r = DC.http_json("POST", "/v1/chat-messages",
                         headers={"Authorization": "Bearer " + akey,
                                  "Content-Type": "application/json"},
                         body=payload, timeout=1800)
        st = r["status"]
        try:
            body = json.loads(r["body"])
        except Exception:
            body = {"_raw": r["body"][:2000]}
        rec["http_status"] = st
        rec["elapsed_seconds"] = round(time.time() - t, 2)
        rec["attempts"] = 1
        rec["message_id"] = (body or {}).get("message_id")
        rec["conversation_id"] = (body or {}).get("conversation_id")
        rec["answer"] = (body or {}).get("answer")
        wr = psql("select w.id from workflow_runs w where w.app_id='%s' "
                  "and w.created_at > timestamp '%s' order by w.created_at desc limit 1;"
                  % (CAND, t0))
        rec["workflow_run_id"] = wr or None
        if wr:
            rec["node_detail"] = node_detail(wr)
        nested = {}
        for name, aid in (("MATRIX", "fd25ebfa-db67-40c3-82e5-202e1254facf"),
                          ("CAMPAIGN", "1f9d65ea-8af5-45f0-a1d0-a80223d354e2"),
                          ("CONTENT_BRIEF", "b1dcf784-540e-4b3f-8ba2-3812f477f3ce"),
                          ("CREATIVE_SCRIPT", "44b55f9d-3792-40c3-b095-f2696464b4ec"),
                          ("PRODUCTION_DIRECTOR", "13cfabd5-f592-4354-a304-47098b765697"),
                          ("PUBLISHING_PACKAGING", PP_APP),
                          ("SEAM", "5fca0162-e26b-4545-a00b-66b1a2a2a077"),
                          ("HOP", "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"),
                          ("M3", "a4c3b19b-243f-490b-9aca-3aa19767d6a5")):
            raw = psql("select coalesce(json_agg(json_build_object('id',id,'status',status,"
                       "'version_used',null,'created_at',created_at::text))::text,'[]') "
                       "from workflow_runs where app_id='%s' and created_at > timestamp '%s';"
                       % (aid, t0))
            nested[name] = {"app_id": aid, "runs": json.loads(raw or "[]")}
        rec["nested_app_runs"] = nested

    t1 = psql("select now()::text;")
    rec["window_end"] = t1
    rec["llm_node_executions_in_window"] = llm_count(t0, t1)
    os.makedirs(EVDIR, exist_ok=True)
    p = os.path.join(EVDIR, "PPBS_B2_%s_RAW.json" % which)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
    print("%s http=%s %.1fs run=%s LLM窗口内=%s"
          % (which, rec["http_status"], rec["elapsed_seconds"], rec.get("workflow_run_id"),
             rec["llm_node_executions_in_window"]))
    print("落盘：", os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
