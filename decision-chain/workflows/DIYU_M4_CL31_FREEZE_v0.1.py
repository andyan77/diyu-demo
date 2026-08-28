#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冻结本轮工程候选（Prompt v1.5 §10 步骤 12）。

Reviewer 启动后，被审候选必须冻结：不得修改被审对象，不得重新发布 Dify。
"""
import hashlib, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CANDIDATE_FREEZE.json")

FILES = [
    "decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py",
    "decision-chain/workflows/DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml",
    "content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml",
    "content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml",
    "content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml",
    "decision-chain/workflows/DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml",
    "decision-chain/docs/V1_M4_FINAL_CLOSURE_TASK_CONTRACT_v1.0.yaml",
    "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md",
]
EVID = ["ANCHOR_BEFORE.json", "CL31_01_BRANCH_ENUM.json", "CL31_PUBLISH.json",
        "CL31_PUBLISH_CAPS.json", "INJECTION_OBJECTS.json", "INJECTION_EQUIVALENCE.json",
        "CL31_RUNTIME_RAW_A1.json", "CL31_02_03_04_VERDICT_A1.json",
        "CL31_RUNTIME_RAW.json", "CL31_02_03_04_VERDICT.json",
        "NEG_C01_C14.json", "CL31_05_06_07_STATIC.json", "CL31_07_REGRESSION.json"]

APPS = {"MATRIX": "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3",
        "CAMPAIGN": "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b",
        "CONTENT_BRIEF": "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1",
        "CREATIVE_SCRIPT": "8d518554-bfbc-4be0-8a57-3b1f04983edf",
        "PRODUCTION_DIRECTOR": "57ebc138-ed9e-4202-bce2-38e44da0ec1d",
        "PUBLISHING_PACKAGING": "10056fcf-9237-4889-a3e3-81e3a695cae0",
        "CAPABILITY_SEAM": "de0cb1e9-2af8-415a-9762-31b6cf348c22",
        "FOUNDER_CANVAS": "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"}


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", sql], capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[:400])
    return [l for l in p.stdout.split("\n") if l.strip()]


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(*a): return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True).stdout.strip()


rec = {"frozen_for": "独立只读 Reviewer（唯一一次正式评审）",
       "repo_files": {f: sha(os.path.join(ROOT, f)) for f in FILES},
       "evidence_files": {f: sha(os.path.join(ROOT, "decision-chain/evidence/m4/final_closure", f))
                          for f in EVID if os.path.exists(
                              os.path.join(ROOT, "decision-chain/evidence/m4/final_closure", f))},
       "git": {"branch": git("rev-parse", "--abbrev-ref", "HEAD"),
               "head": git("rev-parse", "HEAD"),
               "dirty_files": [l for l in git("status", "--porcelain").split("\n") if l.strip()],
               "origin_main": git("rev-parse", "origin/main")},
       "dify_bindings": {}}
for k, aid in APPS.items():
    r = psql("SELECT a.workflow_id||'|'||encode(sha256(convert_to(w.graph,'UTF8')),'hex')||'|'||a.status "
             "FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % aid)
    pv = psql("SELECT id||'|'||version FROM tool_workflow_providers WHERE app_id='%s';" % aid)
    wf, gsha, st = (r[0].split("|") + ["", "", ""])[:3] if r else ("", "", "")
    rec["dify_bindings"][k] = {"app_id": aid, "published_workflow_id": wf,
                               "graph_sha256": gsha, "app_status": st,
                               "provider": pv[0] if pv else None}
json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
print("候选已冻结。HEAD=%s  未提交=%d" % (rec["git"]["head"][:12], len(rec["git"]["dirty_files"])))
for k, v in sorted(rec["dify_bindings"].items()):
    print("  %-22s wf=%s graph=%s" % (k, v["published_workflow_id"][:8], v["graph_sha256"][:12]))
