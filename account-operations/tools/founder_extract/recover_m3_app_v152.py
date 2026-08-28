#!/usr/bin/env python3
"""从 ep37 冻结 DSL 恢复 M3 任务专用候选 App（RECOVERY_TASK，零模型调用）。

Founder 授权 §4。恢复前的六项只读核验在 `RECOVERY_PRECHECK.json` 里另行落盘。
本文件只做：建管理员（库为空，无账号，导入前必须有）→ 登录 → 导入 DSL →
以 `m3-cand-v1.5.2` 发布 → 只读回读落盘。

**不运行任何测试输入，不触发任何模型，不恢复历史运行记录。**
凭据只从 gitignore 的 `.env` 读，不落盘、不打印。
"""
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)

import dify_client as D  # noqa: E402

DSL = os.path.join(WT, "account-operations/evidence/ep37-rollback-drill-v152/"
                       "m3_candidate_app_v152.dsl.yaml")
DSL_SHA = "bd676f291b8e108c906b606549da357f0dfc5153e3ccccb3ca15d97670811620"
OUT = os.path.join(WT, "account-operations/evidence/ep40-dify-recovery-v152")
TASK_ID = "DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001"
MARKED_NAME = "m3-cand-v1.5.2"
MARKED_COMMENT = ("Recovered from ep37 frozen DSL after DB reinit; "
                  "execution content identical to frozen v1.5.2")
FROZEN_PROMPT_SHA = "3a3c657d82d45e96dfbf9abdcb88adf66c58bb74f69f1e1e0412591242898028"
FROZEN_SKILL_SHA = "90596da5170730b90bfa87089d456e7a2f4d670c46f98ea6ae60138e1f4d3c41"


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def main():
    assert len(MARKED_NAME) <= 20 and len(MARKED_COMMENT) <= 100
    os.makedirs(OUT, exist_ok=True)
    env = D.load_env()
    dsl = io.open(DSL, encoding="utf-8").read()
    assert sha(dsl) == DSL_SHA, "DSL 哈希不符，停止"

    log = {"started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "dsl_sha256": sha(dsl), "model_calls": 0, "steps": []}

    # ---- 1. setup：库里没有账号，导入前必须建一个 ----
    st, s = D.http_json("GET", "/console/api/setup"), None
    step = json.loads(st["body"])
    log["steps"].append({"step": "setup_state_before", "value": step})
    if step.get("step") != "finished":
        r = D.http_json("POST", "/console/api/setup",
                        body={"email": env["DIFY_CONSOLE_EMAIL"],
                              "name": env["DIFY_CONSOLE_EMAIL"].split("@")[0],
                              "password": env["DIFY_CONSOLE_PASSWORD"]}, timeout=60)
        log["steps"].append({"step": "setup", "status": r["status"]})
        assert r["status"] in (200, 201), r["body"][:300]
    after = json.loads(D.http_json("GET", "/console/api/setup")["body"])
    log["steps"].append({"step": "setup_state_after", "value": after})

    # ---- 2. 登录 ----
    c = D.Console(env)
    log["transport"] = c.transport
    log["steps"].append({"step": "login", "transport": c.transport})

    # ---- 3. 导入 DSL ----
    st, imp = c.call("POST", "/console/api/apps/imports",
                     body={"mode": "yaml-content", "yaml_content": dsl}, timeout=300)
    log["steps"].append({"step": "import", "status": st,
                         "result": {k: v for k, v in imp.items() if k != "yaml_content"}})
    assert st in (200, 201), (st, imp)
    app_id = imp.get("app_id") or imp.get("id")
    assert app_id, imp
    print("import status =", imp.get("status"), "| app_id =", app_id)
    if imp.get("status") not in ("completed", "completed-with-warnings"):
        print("依赖缺口:", json.dumps(imp.get("leaked_dependencies"), ensure_ascii=False)[:400])

    # ---- 4. 以冻结版本名发布 ----
    st, pub = c.call("POST", f"/console/api/apps/{app_id}/workflows/publish",
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT})
    log["steps"].append({"step": "publish", "status": st, "result": pub})
    assert st in (200, 201), (st, pub)

    # ---- 5. 只读回读 ----
    st, app = c.call("GET", f"/console/api/apps/{app_id}")
    st2, draft = c.call("GET", f"/console/api/apps/{app_id}/workflows/draft")
    st3, published = c.call("GET", f"/console/api/apps/{app_id}/workflows/publish")
    for name, obj in (("app_meta.json", app), ("draft_graph.json", draft),
                      ("published_graph.json", published)):
        write(os.path.join(OUT, name), json.dumps(obj, ensure_ascii=False, indent=2))

    log["recovered"] = {
        "app_id": app_id, "app_name": app.get("name"),
        "app_mode": app.get("mode"), "app_description": app.get("description"),
        "published_version": published.get("version"),
        "published_marked_name": published.get("marked_name"),
        "published_dify_hash": published.get("hash"),
        "draft_dify_hash": draft.get("hash"),
    }
    log["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    write(os.path.join(OUT, "RECOVERY_LOG.json"), json.dumps(log, ensure_ascii=False, indent=2))
    print(json.dumps(log["recovered"], ensure_ascii=False, indent=2))
    return app_id


if __name__ == "__main__":
    main()
