#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase B 收口｜把 diyu_uapp_hop provider 的版本钉重新指向新发布的 hop workflow。

**为什么必须做这一步**：Dify 的 workflow-as-tool 是**按版本钉死取图**的，不是取最新发布版。
证据（Dify 1.x 源码，本机容器内读取）：

    core/tools/workflow_as_tool/tool.py:_get_workflow()
        if not version: 取最新已发布
        else:           select(Workflow).where(app_id==..., version==db_provider.version)
    core/tools/workflow_as_tool/provider.py:104 同样按 db_provider.version 取图

现场：hop 应用已发布 `hop-v0.3-fact-floor`（version 2026-08-30 03:38:31），
但 provider `diyu_uapp_hop` 的 version 仍是 `2026-08-28 07:28:55`（m5-hop-adapt-v0.4）。
不重钉的话，画布仍然调用**旧 hop**，本轮修复发布了却够不着——会造成假通过。

**为什么重钉而不是清空**：清空后 provider 取「最新已发布」，任何一次无关发布都会
静默改变被测行为（A2/A3 危害）。版本钉是可复算性的一部分，只把它指向经过验证的新版本。

改什么：只改 provider 的 version（由服务端按 app.workflow.version 自动写入）。
        name / label / icon / description / parameters / privacy_policy 逐字段原样回填，
        不借这次更新夹带任何其它变化。

用法：
    python3 S4_HOP_PROVIDER_REPIN_v1.0.py --dry-run
    python3 S4_HOP_PROVIDER_REPIN_v1.0.py --apply
"""
import argparse
import importlib.util
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
HOP_APP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"
PROVIDER_NAME = "diyu_uapp_hop"
OUT_DIR = os.path.join(HERE, "..", "evidence", "stages", "s4_fact_chain_root_cause")

# 重钉后必须指向的目标版本对应的图指纹（先冻结，后动手）
EXPECT_COMPOSE_SHA = "6474b902c81c7d91fe8f6143c0a3ece9bbde55dc58b64a822e595b088f2ee855"

_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations/tools/dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def state():
    row = psql("select p.id||'|'||p.version from tool_workflow_providers p "
               "where p.name='%s';" % PROVIDER_NAME)
    pid, pver = row.split("|", 1)
    appver = psql("select w.version from apps a join workflows w on w.id=a.workflow_id "
                  "where a.id='%s';" % HOP_APP)
    return {"provider_id": pid, "provider_pinned_version": pver,
            "app_published_version": appver, "pin_matches_published": pver == appver}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "HOP_PROVIDER_REPIN_REPORT.json"))
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        raise SystemExit("必须显式选择 --dry-run 或 --apply")

    before = state()
    console = DC.Console(env=DC.load_env(ENV))
    st, tool = console.call(
        "GET", "/console/api/workspaces/current/tool-provider/workflow/get"
               "?workflow_app_id=%s" % HOP_APP)
    assert st == 200, ("get provider", st, str(tool)[:400])

    payload = {
        "workflow_tool_id": tool["workflow_tool_id"],
        "name": tool["name"],
        "label": tool["label"],
        "icon": tool["icon"],
        "description": tool["description"],
        "parameters": tool["parameters"],
        "privacy_policy": tool.get("privacy_policy") or "",
        "labels": [x["name"] if isinstance(x, dict) else x for x in (tool.get("tool") or {}).get("labels", [])] or [],
    }
    rep = {"before": before,
           "provider_id_from_api": tool["workflow_tool_id"],
           "fields_echoed_verbatim": sorted(k for k in payload if k != "workflow_tool_id"),
           "parameter_names": [p.get("name") for p in payload["parameters"]],
           "model_calls": 0, "applied": False}

    if a.apply:
        st, res = console.call(
            "POST", "/console/api/workspaces/current/tool-provider/workflow/update",
            body=payload, timeout=300)
        assert st in (200, 201), ("update provider", st, str(res)[:400])
        after = state()
        rep["after"] = after
        rep["applied"] = True
        # 重钉后 provider 指向的那一版，其 m5_compose 必须是修复版
        code_sha = psql(
            "select encode(sha256(convert_to("
            "(select n->'data'->>'code' from workflows w, "
            " jsonb_array_elements(w.graph::jsonb->'nodes') n "
            " where w.app_id='%s' and w.version='%s' and n->>'id'='m5_compose'"
            "), 'UTF8')), 'hex');" % (HOP_APP, after["provider_pinned_version"]))
        rep["pinned_m5_compose_sha256"] = code_sha
        rep["pinned_m5_compose_is_repaired"] = code_sha == EXPECT_COMPOSE_SHA
        assert after["pin_matches_published"], ("重钉后仍未对齐", after)
        assert rep["pinned_m5_compose_is_repaired"], ("钉住的版本不是修复版", code_sha)

    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(a.out, "w", encoding="utf-8").write(
        json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
