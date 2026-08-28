#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-FND-029 修复的定向发布：六个能力子应用 + provider 刷新（N-20）。

节点级 diff 证明每个子应用只有 delivery_finalize 变化，Founder Canvas 零变化，
接缝 DSL 自上次发布后未再变化，因此本次不重发接缝与 Canvas。
凭据只在内存中使用。
"""
import hashlib, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CL31_PUBLISH_CAPS.json")

sp = importlib.util.spec_from_file_location("m4pub", os.path.join(HERE, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
m4pub = importlib.util.module_from_spec(sp); sp.loader.exec_module(m4pub)
sb = importlib.util.spec_from_file_location("m4build", os.path.join(HERE, "DIYU_M4_DSL_BUILD_v0.1.py"))
m4build = importlib.util.module_from_spec(sb); sb.loader.exec_module(m4build)

APPS = {"MATRIX": "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3",
        "CAMPAIGN": "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b",
        "CONTENT_BRIEF": "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1",
        "CREATIVE_SCRIPT": "8d518554-bfbc-4be0-8a57-3b1f04983edf",
        "PRODUCTION_DIRECTOR": "57ebc138-ed9e-4202-bce2-38e44da0ec1d",
        "PUBLISHING_PACKAGING": "10056fcf-9237-4889-a3e3-81e3a695cae0"}


def gsha(app_id):
    r = m4pub.psql("SELECT a.workflow_id||'|'||encode(sha256(convert_to(w.graph,'UTF8')),'hex') "
                   "FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % app_id)
    return r[0] if r else None


def main():
    d = m4pub.protected_integrity()
    if d:
        print("中止：受保护应用已变化"); [print("  ", x) for x in d]; return 1
    print("写前受保护应用完整性：零变化")

    c = m4pub.Console(); c.login()
    ex = c.list_workflow_tools()
    by_app = {t["workflow_app_id"]: t for t in
              (ex if isinstance(ex, list) else ex.get("data", [])) if t.get("workflow_app_id")}

    rec = {"reason": "M4-FND-029 恢复路径 thinking 剥离修复；每个子应用仅 delivery_finalize 变化",
           "apps": {}, "apps_not_touched": ["capability_seam", "founder_canvas"]}
    for cap in m4build.CAPABILITIES:
        k = cap["key"].upper()
        aid = APPS[k]
        path = os.path.join(cap["out_dir"], cap["out_file"])
        text = open(path, encoding="utf-8").read()
        before = gsha(aid)
        c.import_dsl(text, app_id=aid); c.publish(aid)
        after = gsha(aid)
        params = m4pub.params_from_start(path)
        pv0 = m4pub.psql("SELECT version FROM tool_workflow_providers WHERE app_id='%s';" % aid)
        pid = m4pub.resolve_provider(c, aid)
        if pid != "PENDING_PUBLISH":
            c.update_workflow_tool(pid, cap["tool_name"], cap["app_name"], params)
        pv1 = m4pub.psql("SELECT version FROM tool_workflow_providers WHERE app_id='%s';" % aid)
        rec["apps"][k] = {"app_id": aid, "dsl_sha256": hashlib.sha256(text.encode()).hexdigest(),
                          "rollback_anchor_before": before, "target_confirmed_after": after,
                          "graph_changed": before != after, "provider_id": pid,
                          "provider_version_before": pv0, "provider_version_after": pv1,
                          "provider_rebound": pv0 != pv1}
        print("[pub] %-22s graph %s -> %s  provider_rebound=%s"
              % (k, (before or "|").split("|")[1][:10], (after or "|").split("|")[1][:10], pv0 != pv1))

    post = m4pub.protected_integrity()
    rec["protected_integrity_after_ok"] = not post
    rec["protected_integrity_after_diffs"] = post
    json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("写后受保护应用完整性：%s" % ("零变化" if not post else "**变化**"))
    return 0 if not post else 1


if __name__ == "__main__":
    sys.exit(main())
