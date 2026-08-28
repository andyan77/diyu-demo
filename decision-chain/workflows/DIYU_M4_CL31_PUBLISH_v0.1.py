#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 最终窄收口 · 定向发布（只更新实际受影响对象）

Prompt v1.5 §5.2：只更新实际受影响对象，不得机械重发全部八个应用。
本轮受影响对象经节点级 diff 证明**只有 Capability Seam**：
  六个能力子应用与 Founder Canvas 的全部节点定义逐字节零变化。

N-20：接缝重发布**不会**自动刷新它作为 workflow tool 的 provider 版本，
      因此发布后必须无条件刷新 seam provider，否则 Founder Canvas 仍调旧版。

凭据只在内存中使用，不写入任何文件、commit 或账本。
"""
import hashlib, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CL31_PUBLISH.json")

spec = importlib.util.spec_from_file_location(
    "m4pub", os.path.join(HERE, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
m4pub = importlib.util.module_from_spec(spec); spec.loader.exec_module(m4pub)

SEAM_APP_ID = "de0cb1e9-2af8-415a-9762-31b6cf348c22"
SEAM_FILE = m4pub.SEAM_FILE


def main():
    # ── 写前：受保护应用完整性 ────────────────────────────────────────────
    diffs = m4pub.protected_integrity()
    if diffs:
        print("中止：受保护应用已发生变化，禁止写入。")
        for d in diffs: print("   [DIFF]", d)
        return 1
    print("写前受保护应用完整性：零变化")

    text = open(SEAM_FILE, encoding="utf-8").read()
    dsl_sha = hashlib.sha256(text.encode()).hexdigest()

    rows = m4pub.psql("SELECT a.workflow_id, md5(w.graph), "
                      "encode(sha256(convert_to(w.graph,'UTF8')),'hex') "
                      "FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % SEAM_APP_ID)
    before = rows[0] if rows else None
    print("回滚锚点（发布前）:", before)

    c = m4pub.Console(); c.login()
    resp = c.import_dsl(text, app_id=SEAM_APP_ID)
    c.publish(SEAM_APP_ID)

    rows = m4pub.psql("SELECT a.workflow_id, md5(w.graph), "
                      "encode(sha256(convert_to(w.graph,'UTF8')),'hex') "
                      "FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % SEAM_APP_ID)
    after = rows[0] if rows else None
    print("目标系统确认（发布后）:", after)

    # ── N-20：无条件刷新 seam provider ────────────────────────────────────
    params = m4pub.params_from_start(SEAM_FILE)
    provider_id = m4pub.resolve_provider(c, SEAM_APP_ID)
    pv_before = m4pub.psql("SELECT version FROM tool_workflow_providers WHERE app_id='%s';" % SEAM_APP_ID)
    if provider_id != "PENDING_PUBLISH":
        c.update_workflow_tool(provider_id, "diyu_m4_capability_seam",
                               "DIYU %s · Capability Seam" % m4pub.APP_TAG, params)
    pv_after = m4pub.psql("SELECT version FROM tool_workflow_providers WHERE app_id='%s';" % SEAM_APP_ID)
    print("seam provider %s  version %s -> %s" % (provider_id, pv_before, pv_after))

    post = m4pub.protected_integrity()
    print("写后受保护应用完整性：%s" % ("零变化" if not post else "**变化，需立即上报**"))

    rec = {"criterion": "M4-CL31-08 前置", "scope": "targeted_publish_seam_only",
           "reason_only_seam": "节点级 diff 证明六个能力子应用与 Founder Canvas 零变化",
           "seam_app_id": SEAM_APP_ID, "dsl_sha256": dsl_sha,
           "rollback_anchor_before": before, "target_confirmed_after": after,
           "graph_changed": before != after,
           "seam_provider_id": provider_id,
           "seam_provider_version_before": pv_before, "seam_provider_version_after": pv_after,
           "provider_rebound": pv_before != pv_after,
           "protected_integrity_before_ok": True,
           "protected_integrity_after_ok": not post,
           "protected_integrity_after_diffs": post,
           "apps_republished": ["capability_seam"],
           "apps_not_touched": ["matrix", "campaign", "content_brief", "creative_script",
                                "production_director", "publishing_packaging", "founder_canvas"],
           "import_response": resp if isinstance(resp, dict) else {}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("evidence ->", os.path.relpath(OUT, ROOT))
    return 0 if not post else 1


if __name__ == "__main__":
    sys.exit(main())
