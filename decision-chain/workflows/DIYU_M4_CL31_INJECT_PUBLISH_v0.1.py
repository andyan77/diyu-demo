#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布两个隔离故障注入对象（Prompt v1.5 §5.3）。凭据只在内存中使用。"""
import importlib.util, json, os, subprocess, sys, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/INJECTION_OBJECTS.json")

spec = importlib.util.spec_from_file_location("m4pub", os.path.join(HERE, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
m4pub = importlib.util.module_from_spec(spec); spec.loader.exec_module(m4pub)
spec2 = importlib.util.spec_from_file_location("m4inj", os.path.join(HERE, "DIYU_M4_CL31_INJECT_BUILD_v0.1.py"))
m4inj = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(m4inj)

GUARD = "M4 AC31 FAULT INJECTION EVAL ONLY"


def app_by_name(name):
    rows = m4pub.psql("SELECT id FROM apps WHERE name=%s;" % _q(name))
    return rows[0] if rows else None


def _q(s):
    return "'" + s.replace("'", "''") + "'"


def main():
    diffs = m4pub.protected_integrity()
    if diffs:
        print("中止：受保护应用已变化"); [print("  ", d) for d in diffs]; return 1

    c = m4pub.Console(); c.login()
    rec = {"criterion": "Prompt v1.5 §5.3", "created": [], "published": [],
           "naming_guard": GUARD, "routable_from_canvas": False}

    # ── EVAL-1 子应用 ──────────────────────────────────────────────────────
    m4inj.build_eval1()
    t1 = open(m4inj.EVAL1, encoding="utf-8").read()
    assert GUARD in yaml.safe_load(t1)["app"]["name"], "命名护栏未命中"
    prior1 = app_by_name(m4inj.NAME1)
    r1 = c.import_dsl(t1, app_id=prior1)
    id1 = prior1 or (r1.get("app_id") or r1.get("id") or (r1.get("data") or {}).get("app_id")) or app_by_name(m4inj.NAME1)
    c.publish(id1)
    print("[EVAL-1] app_id =", id1)

    existing = c.list_workflow_tools()
    by_app = {t["workflow_app_id"]: t for t in
              (existing if isinstance(existing, list) else existing.get("data", []))
              if t.get("workflow_app_id")}
    params = m4pub.params_from_start(m4inj.EVAL1)
    if id1 not in by_app:
        c.create_workflow_tool(id1, "diyu_m4_ac31_inject_child", m4inj.NAME1, params)
    pid1 = m4pub.resolve_provider(c, id1)
    if pid1 != "PENDING_PUBLISH":
        c.update_workflow_tool(pid1, "diyu_m4_ac31_inject_child", m4inj.NAME1, params)
    print("[EVAL-1] provider_id =", pid1)

    # ── EVAL-2 接缝副本，唯一差异是 CONTENT_BRIEF 分支指向 EVAL-1 ──────────
    e1 = yaml.safe_load(open(m4inj.EVAL1, encoding="utf-8"))
    e2 = m4inj.build_eval2(pid1)
    t2 = open(m4inj.EVAL2, encoding="utf-8").read()
    assert GUARD in yaml.safe_load(t2)["app"]["name"], "命名护栏未命中"
    prior2 = app_by_name(m4inj.NAME2)
    r2 = c.import_dsl(t2, app_id=prior2)
    id2 = prior2 or (r2.get("app_id") or r2.get("id") or (r2.get("data") or {}).get("app_id")) or app_by_name(m4inj.NAME2)
    c.publish(id2)
    print("[EVAL-2] app_id =", id2)

    rep = m4inj.equivalence_report(e1, e2)

    for k, aid, nm in (("EVAL-1", id1, m4inj.NAME1), ("EVAL-2", id2, m4inj.NAME2)):
        rows = m4pub.psql("SELECT a.workflow_id, encode(sha256(convert_to(w.graph,'UTF8')),'hex'), a.status "
                          "FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % aid)
        rec["published"].append({"tag": k, "app_id": aid, "name": nm,
                                 "target_confirmed": rows[0] if rows else None})
        rec["created"].append(aid)

    # Canvas 未被指向任何注入对象
    canvas = yaml.safe_load(open(os.path.join(HERE, "DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml"), encoding="utf-8"))
    ptr = [n["data"].get("provider_id") for n in canvas["workflow"]["graph"]["nodes"]
           if n["data"].get("type") == "tool"]
    rec["canvas_tool_providers"] = ptr
    rec["canvas_points_at_injection"] = any(p in (pid1,) for p in ptr)

    rec["eval1_provider_id"] = pid1
    rec["equivalence"] = rep
    post = m4pub.protected_integrity()
    rec["protected_integrity_after_ok"] = not post
    rec["protected_integrity_after_diffs"] = post
    json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("Canvas 指向注入对象:", rec["canvas_points_at_injection"])
    print("受保护应用写后完整性:", "零变化" if not post else "**变化**")
    print("evidence ->", os.path.relpath(OUT, ROOT))
    return 0 if not post else 1


if __name__ == "__main__":
    sys.exit(main())
