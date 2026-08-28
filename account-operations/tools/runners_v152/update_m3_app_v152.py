#!/usr/bin/env python3
"""最终候选 v1.5.2：把批准的两句输出形状硬规则（SKILL.md）与已继承的 DD-5 部署进任务专用候选 App。

**图形状不变**（7 节点 6 边），模型与温度不变。本轮变的是 `SKILL.md`（两句硬规则 + 去掉审计块模板围栏）
与三个代码节点的自报版本号；闸门判据逻辑继承 v1.5.1 的 DD-5，未再改动。


为什么是薄薄一层而不是把 v14 那份拷一遍：构图、节点代码拼装、输出契约自检
只应该有**一份**实现。这里 `import` 它们，只重写 `main()` 里两件必须变的事——
发布标签，和证据落盘目录（v14 那份写进 `ep23-candidate-v14-freeze/`，
那是第 8 轮的历史证据，**不能覆盖**）。
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "runners_v14"))

from dify_client import Console, read                                   # noqa: E402
from create_m3_app import FEATURES, TASK_ID, APP_ID                     # noqa: E402
import update_m3_app_v14 as V14                                         # noqa: E402

MARKED_NAME = "m3-cand-v1.5.2"        # Dify 限 20 字符
MARKED_COMMENT = ("M3 v1.5.2 FINAL: audit-block must follow body and carry no code fence; "
                  "inherits DD-5 period-word fix")                        # Dify 限 100 字符
EVID = os.path.join(WT, "account-operations/evidence/ep35-candidate-v152-freeze")


def main():
    assert len(MARKED_NAME) <= 20, len(MARKED_NAME)
    assert len(MARKED_COMMENT) <= 100, len(MARKED_COMMENT)

    c = Console()
    hits = c.find_app(TASK_ID)
    assert len(hits) == 1, f"任务专用 App 应当唯一，实得 {len(hits)}"
    app_id = hits[0]["id"]
    assert app_id == APP_ID, f"App 不是授权的那一个：{app_id}"
    print("app", app_id, hits[0]["name"][:60], "| 传输", c.transport)

    skill_md = read(V14.SKILL_PATH)
    gate = V14.build_node_code("gate_main.py")
    asm = V14.build_node_code("assemble_main.py")
    pg = V14.build_node_code("post_gate_main.py")
    for nm, cd in (("gate", gate), ("assemble", asm), ("post_gate", pg)):
        assert "from shared_checks" not in cd, f"{nm} 仍带本地 import，进不了沙箱"
        ns = {"__builtins__": __builtins__}
        exec(compile(cd, f"<{nm}>", "exec"), ns)
        assert callable(ns.get("main")), nm
        print(f"  {nm}: {len(cd)} chars, main() ok")

    graph = V14.build_graph(skill_md, gate, asm, pg)
    V14.verify_output_contract(graph, gate, asm, pg)

    st, cur = c.call("GET", f"/console/api/apps/{app_id}/workflows/draft")
    assert st == 200, (st, cur)
    prev_hash = cur.get("hash")
    print("prev draft hash", prev_hash)

    st, res = c.call("POST", f"/console/api/apps/{app_id}/workflows/draft", body={
        "graph": graph, "features": FEATURES, "hash": prev_hash,
        "environment_variables": [], "conversation_variables": [],
    }, timeout=300)
    assert st == 200, (st, res)
    print("DRAFT SYNCED")

    st, pub = c.call("POST", f"/console/api/apps/{app_id}/workflows/publish",
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT},
                     timeout=300)
    assert st in (200, 201), (st, pub)
    print("PUBLISH", st, json.dumps(pub, ensure_ascii=False)[:160])

    st, draft = c.call("GET", f"/console/api/apps/{app_id}/workflows/draft")
    assert st == 200
    os.makedirs(EVID, exist_ok=True)
    json.dump(draft, open(os.path.join(EVID, "m3_app_draft_graph_v152.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=2)

    freeze = {
        "what": "最终候选 v1.5.2 冻结绑定（部署后读回，不是部署前声明）",
        "task_id": TASK_ID, "app_id": app_id, "marked_name": MARKED_NAME,
        "transport": c.transport,
        "prev_draft_hash": prev_hash, "draft_hash": draft.get("hash"),
        "published_version": pub.get("version"),
        "graph_nodes": [n["data"]["type"] for n in draft["graph"]["nodes"]],
        "graph_edges": len(draft["graph"]["edges"]),
        "sha256": {
            "SKILL.md": hashlib.sha256(skill_md.encode()).hexdigest(),
            "gate_node_code": hashlib.sha256(gate.encode()).hexdigest(),
            "assemble_node_code": hashlib.sha256(asm.encode()).hexdigest(),
            "post_gate_node_code": hashlib.sha256(pg.encode()).hexdigest(),
        },
        "unchanged_vs_v151": ["图形状", "模型", "温度", "闸门判据逻辑", "assemble_main.py", "shared_checks.py"],
        "changed_vs_v151": ["SKILL.md（两句硬规则 + 去掉审计块模板围栏）", "gate_main.py（仅版本号）", "post_gate_main.py（仅版本号）"],
    }
    json.dump(freeze, open(os.path.join(EVID, "CANDIDATE_FREEZE_v1.5.2.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    print("draft hash", draft.get("hash"), "version", draft.get("version"))
    print("nodes", freeze["graph_nodes"], "edges", freeze["graph_edges"])
    print("已落盘", EVID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
