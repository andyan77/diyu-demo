#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为统一 Canvas 建立任务命名的 workflow tool provider。

只**新建**，不改任何既有 provider。参数清单从目标应用**当前已发布的 start 节点**
派生，不硬编码——参数只有一个真源，硬编码必然漂移（M4 现场教训）。

凭据只在内存中使用：不打印、不写证据、不提交 Git。
"""
import importlib.util, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations/tools/dify_client.py"))
DC = importlib.util.module_from_spec(_s); _s.loader.exec_module(DC)

TARGETS = [
    {"key": "M3",   "app_id": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
     "name": "diyu_uapp_m3",
     "label": "DIYU V1 UAPP · M3 单账号持续运营（最终 FP）"},
    {"key": "SEAM", "app_id": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
     "name": "diyu_uapp_seam",
     "label": "DIYU V1 UAPP · 六能力统一接缝（最终 FP）"},
    {"key": "HOP",  "app_id": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
     "name": "diyu_uapp_hop",
     "label": "DIYU V1 UAPP · 跨能力抽取适配 hop v0.2"},
]


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-Atc", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:300])
    return p.stdout.strip()


def start_params(app_id):
    g = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                        "where a.id='%s';" % app_id))
    for n in g["nodes"]:
        if (n.get("data") or {}).get("type") == "start":
            return [{"name": v["variable"], "form": "llm",
                     "required": bool(v.get("required")), "type": "string",
                     "description": v.get("label") or v["variable"]}
                    for v in n["data"].get("variables", [])]
    raise RuntimeError("找不到 start 节点：%s" % app_id)


def main():
    c = DC.Console()
    existing = {r.split("|")[1]: r.split("|")[0]
                for r in psql("select id, app_id from tool_workflow_providers;").splitlines() if r}
    out = {"created": [], "already_present": [], "protected_untouched": []}
    for t in TARGETS:
        if t["app_id"] in existing:
            out["already_present"].append({**t, "provider_id": existing[t["app_id"]]})
            print("已存在，跳过：%-6s %s" % (t["key"], existing[t["app_id"]]))
            continue
        params = start_params(t["app_id"])
        c.call("POST", "/console/api/workspaces/current/tool-provider/workflow/create", {
            "workflow_app_id": t["app_id"], "name": t["name"], "label": t["label"],
            "icon": {"content": "🧩", "background": "#E4FBCC"},
            "description": "DIYU V1 统一 Founder Canvas 专用 provider；只调用，不修改目标应用",
            "parameters": params, "privacy_policy": "",
        })
        pid = psql("select id from tool_workflow_providers where app_id='%s';" % t["app_id"])
        out["created"].append({**t, "provider_id": pid,
                               "params": [p["name"] for p in params]})
        print("已建：%-6s provider=%s  params=%s" % (t["key"], pid, [p["name"] for p in params]))

    # 保护面：旧 provider 与旧 Canvas 一个字节都不能动
    old = psql("select id||'|'||app_id||'|'||version from tool_workflow_providers "
               "where id='2daa2d27-4305-4d24-95ec-3cb424eaeb2f';")
    canvas = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                  "where a.id='f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8';")
    out["protected_untouched"] = {"old_seam_provider": old, "old_canvas_graph_md5": canvas}
    print("\n旧 provider:", old)
    print("旧 Canvas graph md5:", canvas)

    p = os.path.join(ROOT, "unified-app/evidence/UAPP_PROVIDERS_CREATED.json")
    if os.path.exists(p):
        raise SystemExit("证据文件已存在，拒绝覆盖：%s" % p)
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("SAVED", p)


if __name__ == "__main__":
    main()
