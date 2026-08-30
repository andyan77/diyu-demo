#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase B 最小修复｜为 hop 适配器的 facts_registered 建立确定性下限。

依据：unified-app/docs/S4_FACT_SUFFICIENCY_FAILURE_TRIAGE_FINAL_v1.0.md
最高失效节点：app 6c46fdb1 的 m5_compose 代码节点。

修什么：`facts_registered` 的在场与缺口判定，此前**整条**取自抽取器 LLM 的输出。
        同一个 m5_compose 在同一次执行里，把 registered_facts 原样写进 professional_input，
        却因为抽取器留空而把它判成缺口。本修复只补一条确定性下限：
        自身参数 registered_facts 非空而抽取器留空时，按来源绑定据实标为在场。

不改什么：m5_extract 的 prompt / 模型 / 参数；六能力与 SEAM 等最终 FP 应用；
          必填清单；其余任何字段的判定；任何历史证据与判据。

充分性闸门不放松：registered_facts 本身为空时一律不合成，照旧计入缺口。

用法：
    python3 S4_HOP_FACT_FLOOR_REPAIR_v1.0.py --dry-run   # 只算差异，不写 Dify
    python3 S4_HOP_FACT_FLOOR_REPAIR_v1.0.py --apply     # 写草稿并发布
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
HOP_APP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"
OUT_DIR = os.path.join(HERE, "..", "evidence", "stages", "s4_fact_chain_root_cause")
BEFORE_PATH = os.path.join(OUT_DIR, "HOP_GRAPH_BEFORE.json")

# 修复前必须匹配的现场指纹（A2：先冻结，后动手）
EXPECT_COMPOSE_SHA = "f444166c7beef5f78045a7708857698a51ba6c14623c06a48798dcb696c1e171"

_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations/tools/dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)

ANCHOR = "    # ---- 组装扁平外壳：只写目标能力真正需要的键 + 不放松边界的附加键 ----"

PATCH = '''    # ---- 第三条允许的合成规则：事实在不在场是确定性事实，不由模型裁决 ----
    # registered_facts 由画布 uapp_ctx 代码节点从「用户本轮上传资料原文」与
    # 「M1 已登记证据条目（带 nature/scope 标签）」确定性拼装，全程不经模型。
    # 它非空 ⇒「本轮有可用的已登记事实」在结构上成立，这是来源绑定的事实，
    # 不是需要专业判断的结论。本函数下面已经把**同一份字节**原样写进 professional_input；
    # 这里据实标为在场，没有引入任何新事实，只是不让抽取器把已在场的来源随机抹成不在场。
    #
    # 实测依据：同一条会话六轮，registered_facts 恒非空（2367/2459/2459/2541/2541/2541），
    # 外壳 facts_registered 却四轮在场、两轮为空（S4-CO-T2/T3）。
    #
    # 边界：来源本身为空时一律不合成，照旧计入缺口——充分性闸门不因此放松。
    # 事实**如何组织成专业输入**仍归抽取器，本规则只兜「在不在场」这一层。
    if "facts_registered" in required and not f["facts_registered"]:
        _reg = _clean(registered_facts)
        if _reg:
            f["facts_registered"] = _reg[:6000]
            smap["facts_registered"] = "DERIVED(registered_facts)"

'''

MARKER = 'smap["facts_registered"] = "DERIVED(registered_facts)"'


def sha(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def patch_code(code):
    """幂等：已打过就不再插入。锚点不在场一律拒绝，不盲改。"""
    if MARKER in code:
        return code, False
    if ANCHOR not in code:
        raise SystemExit("锚点不在场，拒绝盲改")
    return code.replace(ANCHOR, PATCH + ANCHOR, 1), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "HOP_FACT_FLOOR_REPAIR_REPORT.json"))
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        raise SystemExit("必须显式选择 --dry-run 或 --apply")

    console = DC.Console(env=DC.load_env(ENV))
    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % HOP_APP)
    assert st == 200, ("read draft", st, str(draft)[:400])
    graph = draft["graph"]
    before_graph_sha = sha(json.dumps(graph, ensure_ascii=False, sort_keys=True))
    before_nodes = json.loads(json.dumps(graph["nodes"], ensure_ascii=False))
    nodes = {n["id"]: n for n in graph["nodes"]}
    before_code = nodes["m5_compose"]["data"]["code"]
    before_code_sha = sha(before_code)

    fresh = {"graph_sha256_before": before_graph_sha,
             "m5_compose_sha256_before": before_code_sha,
             "m5_compose_sha256_expected_from_diagnosis": EXPECT_COMPOSE_SHA,
             "compose_matches_diagnosed_state": before_code_sha == EXPECT_COMPOSE_SHA}
    if not fresh["compose_matches_diagnosed_state"]:
        print(json.dumps(fresh, ensure_ascii=False, indent=1))
        raise SystemExit("现场与诊断时不一致，拒绝修改（A3：先算影响面）")

    after_code, changed = patch_code(before_code)
    nodes["m5_compose"]["data"]["code"] = after_code
    after_graph_sha = sha(json.dumps(graph, ensure_ascii=False, sort_keys=True))

    B = {n["id"]: n for n in before_nodes}
    touched = sorted(k for k in nodes
                     if json.dumps(nodes[k], sort_keys=True, ensure_ascii=False)
                     != json.dumps(B.get(k), sort_keys=True, ensure_ascii=False))

    rep = dict(fresh, changed=changed, nodes_touched=touched,
               node_count=len(graph["nodes"]), edge_count=len(graph["edges"]),
               m5_compose_sha256_after=sha(after_code),
               graph_sha256_after=after_graph_sha,
               extractor_prompt_untouched=(
                   json.dumps(nodes["m5_extract"], sort_keys=True, ensure_ascii=False)
                   == json.dumps(B["m5_extract"], sort_keys=True, ensure_ascii=False)),
               model_calls=0, applied=False)

    if a.apply:
        assert touched == ["m5_compose"], ("影响面超出单节点，拒绝写入", touched)
        st, res = console.call("POST", "/console/api/apps/%s/workflows/draft" % HOP_APP, body={
            "graph": graph, "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or []}, timeout=600)
        assert st == 200, ("draft sync", st, str(res)[:400])
        st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % HOP_APP, body={
            "marked_name": "hop-v0.3-fact-floor",
            "marked_comment": "facts_registered 建立确定性下限：registered_facts 非空而抽取器"
                              "留空时按来源绑定据实标为在场；来源为空仍照旧计入缺口"}, timeout=600)
        assert st in (200, 201), ("publish", st, str(pub)[:400])
        rep["applied"] = True
        rep["publish_status"] = st

    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(a.out, "w", encoding="utf-8").write(
        json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
