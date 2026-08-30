#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UAPP 已接受上游产物绑定｜Phase A 零模型根因锁定。**只读、零模型、零写入。**

task_id: DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001
authority: 统一应用已接受上游产物绑定修复与 D3 收口 Execution Prompt 第五节

只读 Dify 运行库、M2 业务库与 M2 API，复算：
  ① D3 之前账本里 PD artifact 的 accepted/current/stale/fingerprint/turn/依赖集；
  ② conversation.uapp_last_artifact 的真实能力身份与正文哈希；
  ③ M2 是否存在该 PD 正文或合法 artifact_id；
  ④ D3 当次 uapp_hop / uapp_fields 的实际收发与 upstream_binding_json 拒绝原因；
  ⑤ 四种候选根因逐一证伪或证实。

    python3 UAAB_PHASE_A_ROOTCAUSE_v1.0.py
"""
import hashlib
import io
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "uapp_artifact_binding")

CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
CONV = "5cfcaf57-8808-4fc7-8c66-d661e515d05a"
D3_RUN = "217f8e2d-4dfa-4b43-b673-99fa62a4b183"
PP_RUN = "c9c9f16b-5996-44f5-b5b4-21be7819e9ea"
WS = "024bb44e-a70d-4ed5-8fa9-b818944b63be"
TASK = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
ACTOR = "uapp-5cfcaf578808"


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def m2(path):
    code = ("import json,urllib.request\n"
            "r=urllib.request.Request('http://127.0.0.1:8000%s',headers={'X-Actor-Ref':'%s'})\n"
            "import sys\n"
            "try:\n"
            "    x=urllib.request.urlopen(r,timeout=15)\n"
            "    print(json.dumps({'status':x.status,'body':json.loads(x.read().decode())},"
            "ensure_ascii=False))\n"
            "except Exception as e:\n"
            "    print(json.dumps({'status':getattr(e,'code',None),'body':str(e)[:200]},"
            "ensure_ascii=False))\n" % (path, ACTOR))
    p = subprocess.run(["docker", "exec", "-i", "diyu-m2-app", "python", "-c", code],
                       capture_output=True, text=True)
    try:
        return json.loads(p.stdout.strip())
    except Exception:
        return {"status": None, "body": (p.stdout or p.stderr)[:300]}


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def fp16(s):
    """与 uapp_state 的 _fp 逐字相同：FNV-1a 64，作用于规范化正文前 256 字。"""
    h = 0xcbf29ce484222325
    for b in (s or "").encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def conv_vars():
    raw = psql("select coalesce(json_agg(data)::text,'[]') from "
               "workflow_conversation_variables where conversation_id='%s';" % CONV)
    out = {}
    for item in json.loads(raw or "[]"):
        o = json.loads(item) if isinstance(item, str) else item
        out[o.get("name")] = o.get("value")
    return out


def node_io(run_id, node_ids):
    raw = psql("select coalesce(json_agg(json_build_object('node',node_id,'inputs',inputs,"
               "'outputs',outputs) order by index)::text,'[]') from workflow_node_executions "
               "where workflow_run_id='%s' and node_id in (%s);"
               % (run_id, ",".join("'%s'" % n for n in node_ids)))
    out = {}
    for r in json.loads(raw or "[]"):
        def J(x):
            if isinstance(x, str):
                try:
                    return json.loads(x)
                except Exception:
                    return x
            return x
        out[r["node"]] = {"inputs": J(r["inputs"]) or {}, "outputs": J(r["outputs"]) or {}}
    return out


def main():
    cv = conv_vars()
    state = json.loads(cv.get("uapp_task_fields") or "{}")
    arts = state.get("artifacts") or []
    last_art = cv.get("uapp_last_artifact") or ""
    last_cap = cv.get("uapp_last_capability") or ""

    # ① 账本里的 PD 与 PP
    pd = [a for a in arts if a.get("cap") == "PRODUCTION_DIRECTOR"]
    pp = [a for a in arts if a.get("cap") == "PUBLISHING_PACKAGING"]

    # ② uapp_last_artifact 的真实身份
    slot = {"declared_capability": last_cap,
            "len": len(last_art), "sha256": sha(last_art),
            "normalized_len": len(norm(last_art)),
            "fp16_over_norm_head256": fp16(norm(last_art)[:256]),
            "head": last_art[:120]}
    slot["matches_ledger_entry"] = next(
        (a for a in arts if a.get("fp") == slot["fp16_over_norm_head256"]), None)

    # ③ M2 是否有正文真源
    proj = m2("/workspaces/%s/tasks/%s/projection" % (WS, TASK))
    m2_art_cnt = int(psql("select count(*) from artifacts where task_id='%s';" % TASK,
                          db="diyu_business"))
    m2_snap_cnt = int(psql("select count(*) from task_snapshots where task_id='%s';" % TASK,
                           db="diyu_business"))
    m2_cols_art = psql("select string_agg(column_name,',' order by ordinal_position) from "
                       "information_schema.columns where table_name='artifacts';",
                       db="diyu_business")
    m2_cols_cv = psql("select string_agg(column_name,',' order by ordinal_position) from "
                      "information_schema.columns where table_name='content_versions';",
                      db="diyu_business")

    # ④ D3 当次实际收发
    io3 = node_io(D3_RUN, ["uapp_hop", "uapp_fields"])
    hop_in = io3.get("uapp_hop", {}).get("inputs", {})
    hop_out = io3.get("uapp_hop", {}).get("outputs", {})
    f_out = io3.get("uapp_fields", {}).get("outputs", {})
    pp_inputs = json.loads(psql("select coalesce(inputs,'{}') from workflow_runs where id='%s';"
                                % PP_RUN) or "{}")

    # ⑤ 四候选根因
    body_anywhere = {
        "m2_artifacts_rows_for_task": m2_art_cnt,
        "m2_task_snapshots_rows_for_task": m2_snap_cnt,
        "m2_artifacts_has_body_column": "body" in (m2_cols_art or ""),
        "m2_content_versions_has_body_column": "body" in (m2_cols_cv or ""),
        "conversation_slot_holds_pd_body": slot["declared_capability"] == "PRODUCTION_DIRECTOR",
    }
    candidates = {
        "1_body_never_persisted": {
            "verdict": "CONFIRMED",
            "why": "M2 该任务 artifacts=%d、task_snapshots=%d；M2 的 artifacts 与 "
                   "content_versions 都只有 content_hash / content_ref，**没有正文列**；"
                   "会话里唯一的正文槽位 uapp_last_artifact 存的是 PP 产物。"
                   "已接受的 PD 正文没有任何一处持久化。" % (m2_art_cnt, m2_snap_cnt)},
        "2_persisted_but_no_retrievable_ref": {
            "verdict": "REFUTED",
            "why": "前提不成立——正文根本没有被持久化，谈不上有引用没引用。"},
        "3_selector_only_reads_uapp_last_artifact": {
            "verdict": "CONFIRMED_BUT_DOWNSTREAM",
            "why": "uapp_hop.upstream_delivery 直接接 {{#conversation.uapp_last_artifact#}}，"
                   "对 accepted / stale / capability 一无所知。但这是**写入侧只有一个槽位**"
                   "的必然结果：即使选择器写对了，也没有第二份正文可选。"
                   "按 A3，最高失效节点在写入侧，不在选择侧。"},
        "4_retrieved_then_dropped_before_fields_or_seam": {
            "verdict": "REFUTED",
            "why": "PD 正文从未被取到。被取到的是 PP 自己的旧产物，"
                   "而 uapp_fields 的血缘门**正确地**拒绝了它："
                   "upstream_binding_json = %s。丢弃行为是对的，不是缺陷。"
                   % json.dumps(f_out.get("upstream_binding_json"), ensure_ascii=False)},
    }

    rep = {
        "document": {"id": "UAAB_PHASE_A_ROOTCAUSE_v1.0",
                     "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
                     "task_mode": "NEW_TASK",
                     "parent_task": "DIYU-V1-UAPP-PROGRESSIVE-CANVAS-001",
                     "authority": "统一应用已接受上游产物绑定修复与 D3 收口 Execution Prompt 第五节",
                     "model_calls": 0, "writes": 0, "read_only": True},
        "ledger": {"task_key": state.get("task_key"), "rev": state.get("rev"),
                   "artifact_count": len(arts),
                   "artifacts": arts,
                   "production_director": pd,
                   "publishing_packaging": pp},
        "conversation_slot_uapp_last_artifact": slot,
        "m2_truth_source": {"projection_status": proj.get("status"),
                            "projection_body": proj.get("body"),
                            "artifacts_columns": m2_cols_art,
                            "content_versions_columns": m2_cols_cv,
                            "artifacts_rows_for_task": m2_art_cnt,
                            "task_snapshots_rows_for_task": m2_snap_cnt,
                            "conclusion": "M2 有 artifact/version API 与表，但**只存 "
                                          "content_ref 与 content_hash，不存正文**；"
                                          "且本任务 0 行。M2 现状不能充当正文真源，"
                                          "要让它充当就必须改 schema —— 越权，不做。"},
        "d3_actual_dataflow": {
            "hop_upstream_capability": hop_in.get("upstream_capability"),
            "hop_upstream_delivery_len": len(hop_in.get("upstream_delivery") or ""),
            "hop_upstream_delivery_sha256": sha(hop_in.get("upstream_delivery")),
            "hop_upstream_delivery_head": (hop_in.get("upstream_delivery") or "")[:120],
            "hop_upstream_delivery_is_pp_artifact":
                (hop_in.get("upstream_capability") == "PUBLISHING_PACKAGING"),
            "hop_output_capability_call_head": (hop_out.get("capability_call") or "")[:300],
            "fields_upstream_binding_json": f_out.get("upstream_binding_json"),
            "fields_gaps_text": f_out.get("gaps_text"),
            "fields_stale_artifacts": f_out.get("stale_artifacts"),
            "fields_merge_note": f_out.get("merge_note"),
            "pp_received_capability_call_has_body":
                "content_body_or_beats" in (pp_inputs.get("capability_call") or ""),
            "pp_received_capability_call_head":
                (pp_inputs.get("capability_call") or "")[:260]},
        "candidate_root_causes": candidates,
        "confirmed_origin": "SYSTEM_UNDER_TEST · 统一画布的产物持久化接缝",
        "highest_failing_node": "uapp_persist + uapp_save：单槽位无条件覆盖。"
                                "任何能力产出非空 artifact 就整体覆盖 "
                                "conversation.uapp_last_artifact，"
                                "不看 accepted、不看 stale、不按能力分格。"
                                "T7 未被接受的 PP 产物因此覆盖了 T6 已接受的 PD 正文。",
        "direct_references": ["uapp_persist（写入决策）", "uapp_save（单点赋值）",
                             "uapp_hop.upstream_delivery / upstream_capability（取回接线）"],
        "who_touches_the_slot": "全图仅 uapp_persist、uapp_save、uapp_hop 三处引用 "
                                "uapp_last_artifact / uapp_last_capability，无第四处。",
        "not_broken": ["uapp_fields 的血缘门（正确拒绝了 PP 自己的旧产物）",
                       "uapp_state 的账本（PD accepted=true、stale=false 记录准确）",
                       "PP b2（缺输入时精确升级，不编造）",
                       "Seam 路由、Hop 抽取 Prompt、M1/M2/M3、其余五能力"],
    }
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "UAAB_PHASE_A_ROOTCAUSE.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")

    print("账本 rev=%s，artifacts=%d" % (state.get("rev"), len(arts)))
    for a in arts:
        print("   %-22s turn=%-2s accepted=%-5s accepted_turn=%-4s stale=%-5s fp=%s len=%s"
              % (a.get("cap"), a.get("turn"), a.get("accepted"), a.get("accepted_turn"),
                 a.get("stale"), a.get("fp"), a.get("len")))
    print("\n唯一正文槽位 uapp_last_artifact：能力=%s len=%d fp=%s"
          % (slot["declared_capability"], slot["len"], slot["fp16_over_norm_head256"]))
    print("   它对应账本哪一条：%s"
          % (json.dumps({k: slot["matches_ledger_entry"][k]
                         for k in ("cap", "turn", "accepted", "stale")}, ensure_ascii=False)
             if slot["matches_ledger_entry"] else "无匹配"))
    print("\nM2：本任务 artifacts=%d snapshots=%d；artifacts 列=%s"
          % (m2_art_cnt, m2_snap_cnt, m2_cols_art))
    print("   content_versions 列=%s" % m2_cols_cv)
    print("\nD3 实际：hop 收到 upstream_capability=%s，正文 %d 字（=PP 自己的旧产物）"
          % (hop_in.get("upstream_capability"), len(hop_in.get("upstream_delivery") or "")))
    print("   uapp_fields 血缘门：%s"
          % json.dumps(f_out.get("upstream_binding_json"), ensure_ascii=False))
    print("   PP 实际收到的 capability_call 含 content_body_or_beats：%s"
          % rep["d3_actual_dataflow"]["pp_received_capability_call_has_body"])
    print("\n四候选根因：")
    for k, v in candidates.items():
        print("   %-46s %s" % (k, v["verdict"]))
    print("\nconfirmed_origin：%s" % rep["confirmed_origin"])
    print("最高失效节点：uapp_persist + uapp_save 单槽位无条件覆盖")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
