#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 M4 → M5 接入映射（Founder 复原指令 §9）

只写 M5 接入所需的运行身份与字段契约，不夹带任何历史审计过程。
"""
import json, os, subprocess, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/docs/V1_M4_M5_HANDOFF_MAP_v0.1.yaml")
SMOKE = os.path.join(ROOT, "decision-chain/evidence/m4/restore/M4_RESTORE_SMOKE.json")

SEAM = "de0cb1e9-2af8-415a-9762-31b6cf348c22"
CANVAS = "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"
CAP_FILE = {
    "MATRIX": "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml",
    "CAMPAIGN": "decision-chain/workflows/DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml",
    "CONTENT_BRIEF": "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml",
    "CREATIVE_SCRIPT": "content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml",
    "PRODUCTION_DIRECTOR": "content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml",
    "PUBLISHING_PACKAGING": "content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml",
}


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify",
                        "-t", "-A", "-c", "SELECT coalesce(json_agg(t)::text,'[]') FROM (%s) t;" % sql.rstrip(";")],
                       capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[:400])
    return json.loads(p.stdout.strip() or "[]")


def app_row(aid):
    r = psql("SELECT a.id, a.name, a.mode, a.status, a.workflow_id, w.version AS wf_version "
             "FROM apps a LEFT JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s'" % aid)
    return r[0] if r else None


def provider_of(aid):
    r = psql("SELECT id, name, version FROM tool_workflow_providers WHERE app_id='%s'" % aid)
    return r[0] if r else None


def io_of(path):
    d = yaml.safe_load(open(os.path.join(ROOT, path), encoding="utf-8"))
    n = {x["id"]: x["data"] for x in d["workflow"]["graph"]["nodes"]}
    start = next(v for v in n.values() if v.get("type") == "start")
    inputs = [{"variable": v["variable"], "required": v.get("required", False), "type": v["type"]}
              for v in start["variables"]]
    ends = {k: [o["variable"] for o in v["outputs"]] for k, v in n.items() if v.get("type") == "end"}
    model = n.get("skill_llm", {}).get("model")
    return inputs, ends, model


smoke = json.load(open(SMOKE, encoding="utf-8")) if os.path.exists(SMOKE) else {}
sm_cap = {c["capability"]: c for c in smoke.get("capabilities", [])}

seam_row, seam_pv = app_row(SEAM), provider_of(SEAM)
canvas_row = app_row(CANVAS)
seam_in, seam_ends, _ = io_of("decision-chain/workflows/DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")

apps = []
for cap, f in CAP_FILE.items():
    ins, ends, model = io_of(f)
    row = app_row(json.load(open(os.path.join(ROOT, "decision-chain/evidence/m4/restore/_ids.json"),
                                 encoding="utf-8"))[cap]) if False else None
    aid = {c["capability"]: c["app_id"] for c in smoke.get("capabilities", [])}.get(cap)
    row = app_row(aid) if aid else None
    pv = provider_of(aid) if aid else None
    apps.append({
        "capability": cap,
        "application_name": row["name"] if row else None,
        "new_app_id": aid,
        "new_workflow_id": row["workflow_id"] if row else None,
        "published_status": (row["status"] == "normal" and bool(row["workflow_id"])) if row else False,
        "tool_name": pv["name"] if pv else None,
        "tool_provider_id": pv["id"] if pv else None,
        "upstream_binding": "DIYU M4 v1.3 TEST · Capability Seam (tool_%s)" % cap.lower(),
        "downstream_binding": "无（六个能力应用之间零调用边）",
        "model_provider": (model or {}).get("provider"),
        "model_name": (model or {}).get("name"),
        "smoke_run_id": sm_cap.get(cap, {}).get("smoke_run_id"),
        "inputs": ins,
        "end_branches": ends,
    })

M = {
    "handoff": "M4 → M5 接入映射",
    "task_id": "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001",
    "scope": "M5_INTEGRATION_HANDOFF",
    "m5_engineering_execution_started": False,

    "founder_natural_entry": {
        "application_name": canvas_row["name"] if canvas_row else None,
        "app_id": CANVAS,
        "workflow_id": canvas_row["workflow_id"] if canvas_row else None,
        "mode": canvas_row["mode"] if canvas_row else None,
        "published_status": bool(canvas_row and canvas_row["workflow_id"]),
        "how_to_call": "服务 API POST /v1/chat-messages（advanced-chat），字段 query 传自然语言",
        "downstream_binding": "DIYU M4 v1.3 TEST · Capability Seam",
        "smoke_run_id": smoke.get("canvas", {}).get("smoke_run_id"),
    },

    "capability_seam": {
        "application_name": seam_row["name"] if seam_row else None,
        "app_id": SEAM,
        "workflow_id": seam_row["workflow_id"] if seam_row else None,
        "published_status": bool(seam_row and seam_row["workflow_id"]),
        "tool_name": seam_pv["name"] if seam_pv else None,
        "tool_provider_id": seam_pv["id"] if seam_pv else None,
        "upstream_binding": "DIYU M4 v1.3 TEST · Founder Canvas (tool_seam)",
        "downstream_binding": "六个专业能力应用，按 capability 分派，一次只调一个",
        "how_to_call": "服务 API POST /v1/workflows/run",
        "inputs": seam_in,
        "end_branches": seam_ends,
        "smoke_run_id": smoke.get("seam", {}).get("smoke_run_id"),
    },

    "applications": apps,

    "field_contract_for_m5": {
        "入口字段": {
            "capability": "六项能力之一：MATRIX / CAMPAIGN / CONTENT_BRIEF / CREATIVE_SCRIPT / PRODUCTION_DIRECTOR / PUBLISHING_PACKAGING",
            "capability_call": "统一业务能力外壳（不强制物理字段名）",
            "professional_input": "本能力专业输入",
            "entry": "可留空，由确定性规则推导",
            "example_reference_requested": "YES / NO",
        },
        "出口字段": {
            "user_delivery": "给用户看的自然语言正文。**所有终止分支都保证非空**，不含内部字段名、状态码或模型 thinking",
            "artifact": "内部专业产出，与 user_delivery 分离，不直接交付用户",
            "business_delivery_outcome": "DELIVERED / DELIVERED_AFTER_RECOVERY / NOT_DELIVERED。**平台技术状态 succeeded 不代表业务交付成功，以此字段为准**",
            "returns_json": "组件级 Return 数组，七项字段：return_id / source / highest_damaged_layer / precise_gap / affected_objects / proposed_disposition / needs_user_decision",
            "seam_trace_json": "本次实际调用与跳过的能力、失效集",
            "binding_json": "保真绑定记录",
        },
        "M5 必须遵守的语义": [
            "一次调用只进入一个专业能力；六个能力应用之间零调用边，不得由 M5 拼成固定全链",
            "读业务结果看 business_delivery_outcome，不要拿平台 status 当交付成功",
            "user_delivery 是唯一可以直接呈现给用户的字段；artifact 不得整份透出",
            "组件级 Return 是本分支结果，不是整任务终态，不触发全局硬停",
        ],
    },
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    yaml.safe_dump(M, fh, allow_unicode=True, sort_keys=False, width=200, default_flow_style=False)
print("M5 接入映射 ->", os.path.relpath(OUT, ROOT))
for a in apps:
    print("  %-22s app=%s wf=%s tool=%s published=%s" % (
        a["capability"], (a["new_app_id"] or "-")[:8], (a["new_workflow_id"] or "-")[:8],
        a["tool_name"], a["published_status"]))
