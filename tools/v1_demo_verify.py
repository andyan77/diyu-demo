#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""笛语 V1 Demo 校验脚本。

无凭据、无网络、无 Dify 依赖。它做三件事：

1. 核验冻结资产的 SHA-256（三份 Skill、夹具、账号责任卡、Golden、项目基线）；
2. 对四份 DSL 做静态结构检查（可达性、变量指向、保留输出名、Golden 泄漏、凭据扫描、
   结构化输出 schema 禁 boolean 与嵌套对象、LLM 节点必须 reasoning_format=separated、
   不得自行补写 temperature）；
3. **从已发布的 DSL 里取出 Code 节点原文**，按 Dify 沙箱的调用形态跑完整单元测试。

第 3 步是重点：测试跑的是仓库里真正会被导入 Dify 的那份代码，不是脚本自带的副本。

    python3 v1_demo_verify.py

【2026-08-24 同步说明】
- 目录重组后本脚本一度因路径失效而无法启动，已改用 `_repo_paths.rpath()` 按文件名解析，
  验证逻辑与判据一字未改。
- `笛语项目基线.md` 本轮做了语义对齐同步，其 SHA-256 钉子已同步更新（不放宽校验，只换基准值）。
- **本脚本仍只校验 v0.1 主 Chatflow**。集成后的 v0.2（56 节点）、对话编排修复 001 新增的
  `side_question` / `open_threads` / `last_acceptance` / `REVOKE_LAST_ACCEPTANCE`
  **尚未纳入本脚本的单元测试**。该承接属于施工范围，须等预检结论与新授权，本轮不做。
"""
import hashlib
import json
import os
import re
import sys

import yaml

from _repo_paths import ROOT as REPO, rpath  # 目录重组后按文件名解析
CHATFLOW = rpath("DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml")

FROZEN = {
    "Matrix_Architect_v0.1.2.md": "7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838",
    "Campaign_Orchestrator_v0.1.md": "c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb",
    "Content_Brief_Architect_v0.1.md": "a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f",
    "一页纸夹具品牌事实 v0.1.md": "8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a",
    "序里集_Campaign当前素材与资源夹具_v0.1.md": "53ea76e93c6529d211bcc41161e9771f7cc5818fe99caf54c4af5f7539ae0074",
    "序里集_Campaign最小承接条件夹具_v0.1.md": "17b41d3ae37635fcd1e97f6af1136c71afa6310a9c51e1db12948b0b2e1e2b06",
    "序里集_四张账号责任卡_CONFIRMED_v0.1.md": "8e21454f53a34b7dce13b7eab547727bb1ce8bce9bac5f86df6d7dc3078f503f",
    "序里集_CONTENT_BRIEF_GOLDEN_v0.1.md": "3b6cbcd7c79d49815ec1de8db472950ab84ac04a754b3342355285d706fe04bd",
    "笛语项目基线.md": "6b964cc042313a93a23ec1910656399772ee9ce8d3559be7abff50c6de19f90b",
}


def sha_file(path):
    """SHA-256 of a file's bytes. Deliberately NOT named `sha`: the static-check
    section below defines a string hasher with that name."""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check_frozen():
    print("=" * 96)
    print("1. 冻结资产 SHA-256 核验")
    print("=" * 96)
    bad = []
    for name, want in sorted(FROZEN.items()):
        p = rpath(name)
        if not os.path.exists(p):
            bad.append(name + "（文件缺失）")
            print("  FAIL %-44s 文件缺失" % name)
            continue
        got = sha_file(p)
        if got == want:
            print("  PASS %-44s %s" % (name, got[:16]))
        else:
            bad.append(name)
            print("  FAIL %-44s 期望 %s 实际 %s" % (name, want[:16], got[:16]))
    return bad


def node_code(node_id_prefix):
    """Pull a Code node's source straight out of the shipped chatflow DSL."""
    dsl = yaml.safe_load(open(CHATFLOW, encoding="utf-8"))
    for n in dsl["workflow"]["graph"]["nodes"]:
        if n["data"].get("type") == "code" and n["id"].startswith(node_id_prefix):
            return n["data"]["code"]
    raise SystemExit("在 %s 中找不到代码节点 %s*" % (CHATFLOW, node_id_prefix))


STATE_CODE = node_code("v1_state")
PRECHECK_CODE = node_code("pre_matrix")
FINALIZE_CODE = node_code("fin_matrix")
EXEC_FAIL_CODE = node_code("v1_toolfail")

SKILL_FILES = {
    "Matrix Architect v0.1.2": "Matrix_Architect_v0.1.2.md",
    "Campaign Orchestrator v0.1": "Campaign_Orchestrator_v0.1.md",
    "Content Brief Architect v0.1": "Content_Brief_Architect_v0.1.md",
}
RESERVED_OUTPUT = {"text", "json", "files"}
GOLDEN_CANARY = "CB-GOLDEN-NOT-FOR-MODEL-20260821"
GOLDEN_FILE = "序里集_CONTENT_BRIEF_GOLDEN_v0.1.md"
CRED_PATTERNS = {
    "Bearer 令牌": r"Bearer\s+[A-Za-z0-9_\-\.]{20,}",
    "Dify 服务密钥": r"app-[A-Za-z0-9]{24,}",
    "JWT": r"eyJ[A-Za-z0-9_\-]{20,}\.",
    "cookie 令牌": r"(access_token|refresh_token|csrf_token)\s*[=:]\s*\S{10,}",
    "口令赋值": r"(?i)(password|secret_key|api_key)\s*[=:]\s*[A-Za-z0-9/+=]{8,}",
}
fails = []



def fail(msg):
    fails.append(msg)
    print("  FAIL %s" % msg)


def ok(msg):
    print("  PASS %s" % msg)


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def validate_graph(name, dsl, expect_mode):
    g = dsl["workflow"]["graph"]
    nodes = {n["id"]: n for n in g["nodes"]}
    edges = g["edges"]

    if dsl.get("kind") != "app" or dsl.get("version") != "0.7.0":
        fail("%s kind/version 不是 app/0.7.0" % name)
    if dsl["app"]["mode"] != expect_mode:
        fail("%s app.mode=%s 期望 %s" % (name, dsl["app"]["mode"], expect_mode))

    # every edge endpoint exists
    for e in edges:
        if e["source"] not in nodes:
            fail("%s 边 %s 的 source 不存在" % (name, e["id"]))
        if e["target"] not in nodes:
            fail("%s 边 %s 的 target 不存在" % (name, e["id"]))
        st = nodes.get(e["source"], {}).get("data", {}).get("type")
        tt = nodes.get(e["target"], {}).get("data", {}).get("type")
        if e["data"]["sourceType"] != st or e["data"]["targetType"] != tt:
            fail("%s 边 %s 的 sourceType/targetType 与节点实际类型不符" % (name, e["id"]))

    # reachability from start
    starts = [i for i, n in nodes.items() if n["data"]["type"] == "start"]
    if len(starts) != 1:
        fail("%s start 节点数量=%d" % (name, len(starts)))
    adj = {}
    for e in edges:
        adj.setdefault(e["source"], []).append(e["target"])
    seen, stack = set(starts), list(starts)
    while stack:
        cur = stack.pop()
        for nxt in adj.get(cur, []):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    unreachable = sorted(set(nodes) - seen)
    if unreachable:
        fail("%s 存在不可达节点: %s" % (name, unreachable))
    else:
        ok("%s 全部 %d 个节点从 start 可达，%d 条边端点合法" % (name, len(nodes), len(edges)))

    # every variable selector points at a real node output or a legal namespace
    legal_ns = {"sys", "conversation", "env"}
    def check_sel(sel, where):
        if not sel:
            return
        head = sel[0]
        if head in legal_ns or head in nodes:
            return
        fail("%s %s 引用了不存在的节点 %s" % (name, where, head))

    for nid, n in nodes.items():
        d = n["data"]
        for v in d.get("variables", []) or []:
            check_sel(v.get("value_selector"), "节点 %s 的变量 %s" % (nid, v.get("variable")))
        for o in d.get("outputs", []) or []:
            if isinstance(o, dict):
                check_sel(o.get("value_selector"), "节点 %s 的输出 %s" % (nid, o.get("variable")))
        for item in d.get("items", []) or []:
            check_sel(item.get("variable_selector"), "赋值节点 %s" % nid)
            if item.get("input_type") == "variable":
                check_sel(item.get("value"), "赋值节点 %s 的取值" % nid)
        for case in d.get("cases", []) or []:
            for c in case.get("conditions", []):
                check_sel(c.get("variable_selector"), "条件节点 %s" % nid)
        for k, tp in (d.get("tool_parameters") or {}).items():
            if tp.get("type") == "variable":
                check_sel(tp.get("value"), "工具节点 %s 参数 %s" % (nid, k))
        if d.get("type") == "llm":
            if d.get("reasoning_format") != "separated":
                fail("%s LLM 节点 %s 未开启 reasoning_format=separated" % (name, nid))
            if d.get("structured_output_enabled"):
                schema = json.dumps(d.get("structured_output") or {}, ensure_ascii=False)
                # Dify's prompt-based structured-output template tells the model
                # "Do not output boolean value, use string type instead", so a
                # boolean-typed schema is self-contradictory and starves the model.
                if '"boolean"' in schema:
                    fail("%s LLM 节点 %s 的结构化输出 schema 含 boolean 类型" % (name, nid))
                if '"object"' in schema.replace('"type": "object"', "", 1):
                    fail("%s LLM 节点 %s 的结构化输出 schema 含嵌套对象" % (name, nid))
            # A Judge that is asked about fabricated facts must be shown the facts,
            # and the facts it is shown must be the SAME frozen bundle the Skill saw.
            if nid.startswith("judge_"):
                slot = nid[len("judge_"):]
                adapter = {
                    "matrix": "DIYU_DEMO_V1_TOOL_MATRIX_v0.1.yml",
                    "campaign": "DIYU_DEMO_V1_TOOL_CAMPAIGN_v0.1.yml",
                    "content_brief": "DIYU_DEMO_V1_TOOL_CONTENT_BRIEF_v0.1.yml",
                }.get(slot)
                user = [p for p in d["prompt_template"] if p["role"] == "user"][0]["text"]
                seg = user[user.find("===== BEGIN SOURCE"):user.rfind("=====") + 5]
                ap = rpath(adapter) if adapter else None
                if not ap or not os.path.exists(ap):
                    fail("%s Judge 节点 %s 找不到对应适配 Workflow" % (name, nid))
                else:
                    adsl = yaml.safe_load(open(ap, encoding="utf-8"))
                    want = [n2["data"]["template"] for n2 in adsl["workflow"]["graph"]["nodes"]
                            if n2["id"].endswith("_fixture_sha")][0]
                    if sha(seg) != want:
                        fail("%s Judge 节点 %s 嵌入的夹具与适配 Workflow 的 bundle 不一致"
                             % (name, nid))
                    else:
                        ok("%s Judge 节点 %s 嵌入的夹具与 Skill 实际所见 bundle 逐字一致 (%s)"
                           % (name, nid, want[:12]))
            cp = d["model"]["completion_params"]
            if "temperature" in cp:
                fail("%s LLM 节点 %s 自行补写了 temperature" % (name, nid))
    return nodes


def scan_text(name, blob):
    for label, pat in CRED_PATTERNS.items():
        if re.search(pat, blob):
            fail("%s 命中凭据模式「%s」" % (name, label))
    if GOLDEN_CANARY in blob:
        fail("%s 含 Golden 金丝雀标记，Golden 已泄漏进模型可见面" % name)


def run_static():
    print()
    print("=" * 96)
    print("2. DSL 静态结构检查")
    print("=" * 96)

    golden_body = open(rpath(GOLDEN_FILE), encoding="utf-8").read()
    # A Golden line only proves leakage if it is UNIQUE to the Golden. The Golden
    # quotes frozen upstream sources (C1—C6, the fixtures) and the Skills' own status
    # tokens verbatim; those lines legitimately reach the model through the frozen
    # inputs, so counting them would flag the legal input path as a leak.
    legit_sources = sorted(set(
        list(SKILL_FILES.values()) + [
            "一页纸夹具品牌事实 v0.1.md",
            "序里集_Campaign当前素材与资源夹具_v0.1.md",
            "序里集_Campaign最小承接条件夹具_v0.1.md",
        ] + ["C%d_FOUNDER_CONFIRMED_v0.1.md" % i for i in range(1, 7)]
    ))
    legit_blob = "\n".join(open(rpath(f), encoding="utf-8").read()
                           for f in legit_sources)
    golden_lines = [l.strip() for l in golden_body.split("\n")
                    if len(l.strip()) >= 24 and not l.strip().startswith(("#", ">", "|", "-", "*"))]
    golden_only = [l for l in golden_lines if l not in legit_blob]
    print("Golden 实质行 %d 条，其中 %d 条为 Golden 独有（其余来自冻结合法输入，逐字复现属正常）"
          % (len(golden_lines), len(golden_only)))
    golden_lines = golden_only

    targets = [t for t in sys.argv[1:]] or [
        "DIYU_DEMO_V1_TOOL_MATRIX_v0.1.yml",
        "DIYU_DEMO_V1_TOOL_CAMPAIGN_v0.1.yml",
        "DIYU_DEMO_V1_TOOL_CONTENT_BRIEF_v0.1.yml",
        "DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml",
    ]
    for fname in targets:
        path = rpath(fname)
        if not os.path.exists(path):
            print("\n-- %s（尚未生成，跳过）" % fname)
            continue
        raw = open(path, encoding="utf-8").read()
        dsl = yaml.safe_load(raw)
        mode = dsl["app"]["mode"]
        print("\n-- %s  mode=%s  %d bytes" % (fname, mode, len(raw.encode())))
        nodes = validate_graph(fname, dsl, mode)
        scan_text(fname, raw)

        # Golden verbatim leakage
        leaked = [l for l in golden_lines if l in raw]
        if leaked:
            fail("%s 逐字包含 Golden 行 %d 条，例如：%s" % (fname, len(leaked), leaked[0][:40]))
        else:
            ok("%s 未包含 Golden 逐字内容（比对 %d 条实质行）" % (fname, len(golden_lines)))

        # end-node output names must not collide with tool reserved keys
        for nid, n in nodes.items():
            if n["data"]["type"] == "end":
                names = {o["variable"] for o in n["data"]["outputs"]}
                bad = names & RESERVED_OUTPUT
                if bad:
                    fail("%s end 节点 %s 使用了保留输出名 %s" % (fname, nid, bad))
                else:
                    ok("%s end 输出 %s 未与 text/json/files 冲突" % (fname, sorted(names)))

        # Skill body must be byte-identical to the repo file
        for nid, n in nodes.items():
            if n["data"]["type"] != "llm":
                continue
            for msg in n["data"]["prompt_template"]:
                if msg["role"] != "system":
                    continue
                for label, sf in SKILL_FILES.items():
                    body = open(rpath(sf), encoding="utf-8").read()
                    if sha(msg["text"]) == sha(body):
                        ok("%s 节点 %s 的 System 提示词与 %s 逐字一致 (%s)"
                           % (fname, nid, sf, sha(body)[:12]))
                        break
        # code node limits
        for nid, n in nodes.items():
            if n["data"]["type"] == "code":
                code = n["data"]["code"]
                if n["data"]["code_language"] != "python3":
                    fail("%s 代码节点 %s 不是 python3" % (fname, nid))
                for outname, spec in n["data"]["outputs"].items():
                    if spec["type"] not in ("string", "number", "object", "boolean",
                                            "array[string]", "array[number]",
                                            "array[object]", "array[boolean]"):
                        fail("%s 代码节点 %s 输出 %s 类型 %s 不在 Dify 允许集"
                             % (fname, nid, outname, spec["type"]))
                if "def main(" not in code:
                    fail("%s 代码节点 %s 缺少 main 入口" % (fname, nid))
                try:
                    compile(code, "<%s>" % nid, "exec")
                except SyntaxError as exc:
                    fail("%s 代码节点 %s 语法错误: %s" % (fname, nid, exc))
                else:
                    ok("%s 代码节点 %s 语法通过，%d 字符" % (fname, nid, len(code)))

    print("\n静态检查 FAIL=%d" % len(fails))
    return fails




FAILS = []


def load(code):
    ns = {"json": json}
    exec(compile(code, "<node>", "exec"), ns)
    return ns["main"]


state_main = load(STATE_CODE)
precheck_main = load(PRECHECK_CODE)
finalize_main = load(FINALIZE_CODE)
execfail_main = load(EXEC_FAIL_CODE)


def check(name, cond, detail=""):
    if cond:
        print("  PASS %s" % name)
    else:
        FAILS.append(name)
        print("  FAIL %s  %s" % (name, detail))


def patch(**kw):
    base = {"route_intent": "DISCUSS", "task_action": "NONE", "change_goal": "",
            "change_target_object": "", "confirmation_signal": "NONE",
            "requested_skill": "NONE", "acceptance_signal": "NONE",
            "continue_signal": "NO", "user_message_summary": ""}
    base.update(kw)
    return base


def snap_of(res):
    return json.loads(res["snapshot_json"])


print()
print("=" * 96)
print("3. 状态机与合同检查单元测试（代码取自已发布 DSL）")
print("=" * 96)
print()
print("=" * 96)
print("A. 状态机基础 / 路由")
print("=" * 96)

r = state_main("你们这套东西大概怎么用？", "", patch(route_intent="DISCUSS"))
check("A1 空快照 + 纯讨论 → DISCUSS，不建任务", r["effective_route"] == "DISCUSS"
      and snap_of(r)["phase"] == "IDLE" and snap_of(r)["confirmed_task"] is None, r["effective_route"])

r = state_main("我想让几个账号别老发一样的东西", "",
               patch(route_intent="FOCUS", task_action="CREATE",
                     change_goal="减少多个账号内容重复"))
s1 = snap_of(r)
check("A2 模糊需求 → FOCUS，形成 draft_task，进入待确认",
      r["effective_route"] == "FOCUS" and s1["draft_task"]["goal"] == "减少多个账号内容重复"
      and s1["phase"] == "AWAITING_CONFIRMATION" and s1["pending_action"]["kind"] == "CONFIRM_TASK",
      json.dumps(s1, ensure_ascii=False)[:300])

r2 = state_main("对，就这个", r["snapshot_json"], patch(route_intent="CONFIRM_TASK",
                                                    confirmation_signal="AFFIRM"))
s2 = snap_of(r2)
check("A3 确认 → confirmed_task 落地，phase=READY",
      s2["confirmed_task"]["goal"] == "减少多个账号内容重复" and s2["phase"] == "READY"
      and s2["pending_action"] is None, json.dumps(s2, ensure_ascii=False)[:300])

print()
print("=" * 96)
print("B. 授权与执行门")
print("=" * 96)

r3 = state_main("那就跑一下矩阵吧", r2["snapshot_json"],
                patch(route_intent="EXECUTE_REQUEST", requested_skill="MATRIX"))
s3 = snap_of(r3)
check("B1 已确认任务 + 明确要求 → EXECUTE_MATRIX，授权已消费",
      r3["effective_route"] == "EXECUTE_MATRIX" and s3["authorization"]["consumed"] is True
      and s3["phase"] == "RUNNING", r3["effective_route"])

r4 = state_main("直接做 Campaign", r2["snapshot_json"],
                patch(route_intent="EXECUTE_REQUEST", requested_skill="CAMPAIGN"))
check("B2 无 Matrix 产物 → Campaign 被上游门拦下，不执行",
      r4["effective_route"] == "HUMAN_DECISION"
      and snap_of(r4)["blocking_gap"].startswith("UPSTREAM_MISSING"), r4["effective_route"])

# Matrix VALIDATED but not accepted
sv = snap_of(r3)
sv["artifacts"]["matrix"] = {"artifact_id": "art_matrix_001", "artifact_type": "MATRIX",
                             "revision": 1, "status": "VALIDATED", "content_hash": "sha256:x",
                             "parent_artifact_id": None, "parent_hash": None,
                             "skill_name": "Matrix Architect v0.1.2", "skill_sha": "7a6a",
                             "run_id": "run1", "accepted_turn_id": None,
                             "summary": "s", "ref": "conversation.matrix_artifact"}
sv["last_result_ref"] = "matrix"
sv["phase"] = "COMPLETED"
r5 = state_main("接着做 Campaign", json.dumps(sv, ensure_ascii=False),
                patch(route_intent="EXECUTE_REQUEST", requested_skill="CAMPAIGN"))
check("B3 Matrix 仅 VALIDATED（未接受）→ Campaign 不得运行",
      r5["effective_route"] == "HUMAN_DECISION"
      and "UPSTREAM_NOT_ACCEPTED" in (snap_of(r5)["blocking_gap"] or ""), r5["effective_route"])

r6 = state_main("这个矩阵可以，接受并继续做 Campaign", json.dumps(sv, ensure_ascii=False),
                patch(route_intent="EXECUTE_REQUEST", acceptance_signal="ACCEPT_CURRENT_ARTIFACT",
                      continue_signal="YES"))
s6 = snap_of(r6)
check("B4 「接受并继续」→ Matrix 转 USER_ACCEPTED 且同轮授权 Campaign 执行",
      s6["artifacts"]["matrix"]["status"] == "USER_ACCEPTED"
      and r6["effective_route"] == "EXECUTE_CAMPAIGN", r6["effective_route"])

r7 = state_main("接受", json.dumps(sv, ensure_ascii=False),
                patch(route_intent="CONFIRM_TASK", acceptance_signal="ACCEPT_CURRENT_ARTIFACT",
                      continue_signal="NO"))
s7 = snap_of(r7)
check("B5 只接受、不继续 → 接受生效但不执行任何 Skill",
      s7["artifacts"]["matrix"]["status"] == "USER_ACCEPTED"
      and not r7["effective_route"].startswith("EXECUTE_"), r7["effective_route"])

print()
print("=" * 96)
print("C. 纠正 / 取消 / 跑题")
print("=" * 96)

r8 = state_main("不对，我要的是提高到店预约", r2["snapshot_json"],
                patch(route_intent="CORRECT", task_action="UPDATE",
                      change_goal="提高到店预约量"))
s8 = snap_of(r8)
check("C1 实质纠正 → 旧确认失效、授权撤销、重新待确认",
      s8["confirmed_task"] is None and s8["authorization"]["granted"] is False
      and s8["pending_action"]["kind"] == "CONFIRM_TASK"
      and s8["revision"] == s2["revision"] + 1, json.dumps(s8, ensure_ascii=False)[:300])

# The old authorization must never survive a correction. Plant a granted,
# unconsumed authorization against the OLD revision, then correct the goal.
s_auth = snap_of(r2)
s_auth["authorization"] = {"skill": "MATRIX", "task_revision": s_auth["revision"],
                           "confirmation_id": "confirm_old", "granted": True,
                           "consumed": False}
r8a = state_main("等一下，我要的是提高到店预约", json.dumps(s_auth, ensure_ascii=False),
                 patch(route_intent="CORRECT", task_action="UPDATE",
                       change_goal="提高到店预约量"))
s8a = snap_of(r8a)
check("C2a 纠正后旧授权立即作废，且本轮不执行",
      s8a["authorization"]["granted"] is False
      and not r8a["effective_route"].startswith("EXECUTE_"),
      json.dumps(s8a["authorization"], ensure_ascii=False))

r8b = state_main("那就跑矩阵", r8["snapshot_json"],
                 patch(route_intent="EXECUTE_REQUEST", requested_skill="MATRIX"))
s8b = snap_of(r8b)
check("C2b 纠正后重新要求执行 → 针对新任务重新确认并授权，不复用旧授权（§17 禁止形式主义确认）",
      r8b["effective_route"] == "EXECUTE_MATRIX"
      and s8b["confirmed_task"]["goal"] == "提高到店预约量"
      and s8b["authorization"]["task_revision"] == s8b["revision"]
      and s8b["authorization"]["confirmation_id"] != "confirm_old",
      "%s / %s" % (r8b["effective_route"], json.dumps(s8b["authorization"], ensure_ascii=False)))

# A carried-over authorization bound to a stale revision must never fire on its own.
s_stale = snap_of(r8)
s_stale["authorization"] = {"skill": "MATRIX", "task_revision": s_stale["revision"] - 1,
                            "confirmation_id": "confirm_stale", "granted": True,
                            "consumed": False}
r8c = state_main("嗯", json.dumps(s_stale, ensure_ascii=False), patch(route_intent="DISCUSS"))
check("C2c 过期版本上的未消费授权，在没有本轮明确请求时不会触发执行",
      not r8c["effective_route"].startswith("EXECUTE_"), r8c["effective_route"])

r9 = state_main("算了这个先不做了", r2["snapshot_json"], patch(route_intent="CANCEL"))
s9 = snap_of(r9)
check("C3 取消 → phase=CANCELLED，确认与授权全部作废",
      s9["phase"] == "CANCELLED" and s9["confirmed_task"] is None
      and s9["authorization"]["granted"] is False, json.dumps(s9, ensure_ascii=False)[:200])

r9b = state_main("那跑一下矩阵", r9["snapshot_json"],
                 patch(route_intent="EXECUTE_REQUEST", requested_skill="MATRIX"))
check("C4 取消后 → 仍不得执行 Skill", not r9b["effective_route"].startswith("EXECUTE_"),
      r9b["effective_route"])

r10 = state_main("话说你们支持导出 PDF 吗", r2["snapshot_json"], patch(route_intent="SIDE_TOPIC"))
s10 = snap_of(r10)
check("C5 跑题 → SIDE_TOPIC 且任务核心字段零改动",
      r10["effective_route"] == "SIDE_TOPIC"
      and s10["confirmed_task"] == s2["confirmed_task"]
      and s10["revision"] == s2["revision"] and s10["phase"] == s2["phase"],
      json.dumps(s10, ensure_ascii=False)[:200])

r11 = state_main("好，回到刚才那个矩阵的事，跑吧", r10["snapshot_json"],
                 patch(route_intent="EXECUTE_REQUEST", requested_skill="MATRIX"))
check("C6 跑题后返回 → 原任务仍可直接执行", r11["effective_route"] == "EXECUTE_MATRIX",
      r11["effective_route"])

print()
print("=" * 96)
print("D. 影子补丁失败与非法输入（Fail Open，且绝不误执行）")
print("=" * 96)

for label, bad in [
    ("空对象", {}),
    ("非法枚举", patch(route_intent="RUN_EVERYTHING")),
    ("未知字段", dict(patch(), tenant_id="t1")),
    ("直接写授权", dict(patch(), authorization={"granted": True})),
    ("非 JSON 字符串", "not json at all"),
    ("None", None),
    ("列表", [1, 2, 3]),
    ("补丁塞入未知字段", dict(patch(change_goal="x"), budget=100)),
]:
    rr = state_main("跑一下矩阵", r2["snapshot_json"], bad)
    passed = (rr["effective_route"] == "DISCUSS" and rr["patch_ok"] == "false"
              and rr["state_saved"] == "false"
              and snap_of(rr)["confirmed_task"] == s2["confirmed_task"]
              and snap_of(rr)["revision"] == s2["revision"])
    check("D:%s → 降级 DISCUSS、旧快照保留、不执行 Skill" % label, passed,
          "%s / %s" % (rr["effective_route"], rr["reject_reason"]))

rr = state_main("跑矩阵", "{broken json", patch(route_intent="EXECUTE_REQUEST",
                                              requested_skill="MATRIX"))
check("D:快照解析失败 → 从初始状态重建且拒绝执行",
      not rr["effective_route"].startswith("EXECUTE_"), rr["effective_route"])

print()
print("=" * 96)
print("E. Tool 输出确定性合同检查")
print("=" * 96)

GOOD_CB = ("# Content Brief Pack\n\n## 0. 运行结论\n- 顶层状态：READY_WITH_CONDITIONS\n"
           "## 1. 内容单元索引\n## 2. 已授权发布内容的独立 Brief\n### brief_id：BRF-001\n")
CB_SHA = "a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f"
CB_FB = "8ad330625089bd04fce7186c7d497bf656f29ad5dcecb88269c7ad68aa6f6277"


NAMES = {"matrix": "Matrix Architect v0.1.2",
         "campaign": "Campaign Orchestrator v0.1",
         "content_brief": "Content Brief Architect v0.1"}


def pre(slot, final, present="true", sha=None, fb=None, upstream=""):
    shas = {"content_brief": CB_SHA}
    fbs = {"content_brief": CB_FB}
    return precheck_main(slot, final, present,
                         NAMES[slot], sha or shas.get(slot, ""),
                         "deepseek-v4-flash", fb or fbs.get(slot, ""), upstream)


p1 = pre("content_brief", GOOD_CB)
check("E1 合规输出 → precheck_ok", p1["precheck_ok"] == "true", p1["precheck_report"][:300])

p2 = pre("content_brief", "MODEL_OUTPUT_NO_FINAL", present="false")
check("E2 无 Final → precheck 失败", p2["precheck_ok"] == "false", p2["precheck_report"][:200])

p3 = pre("content_brief", "<think>想一想</think>" + GOOD_CB)
check("E3 输出含 think → precheck 失败", p3["precheck_ok"] == "false", p3["precheck_report"][:200])

p4 = pre("content_brief", "# Content Brief Pack\n- 顶层状态：随便写的\n")
check("E4 顶层状态非法 → precheck 失败", p4["precheck_ok"] == "false", p4["precheck_report"][:200])

p5 = pre("content_brief", GOOD_CB, sha="deadbeef")
check("E5 Skill SHA 不符 → precheck 失败", p5["precheck_ok"] == "false", p5["precheck_report"][:200])

p6 = pre("content_brief", GOOD_CB, fb="deadbeef")
check("E6 夹具 bundle SHA 不符 → precheck 失败", p6["precheck_ok"] == "false", p6["precheck_report"][:200])

p7 = pre("content_brief", "# Content Brief Pack\n- 顶层状态：INPUT_INSUFFICIENT\n缺失信息：\n- 上游\n")
check("E7 合法停机状态 → precheck 通过但标记为非产物",
      p7["precheck_ok"] == "true" and p7["is_stop_status"] == "true", p7["precheck_report"][:200])

p8 = pre("content_brief", GOOD_CB + ("填充" * 120000))
check("E8 超出会话变量可保存上限 → precheck 失败",
      p8["precheck_ok"] == "false" and "TOO_LARGE" in p8["precheck_report"], p8["precheck_report"][:200])

up = ("主讲账号：周宁。周宁负责选品比较。周宁本轮为主讲。\n"
      "参战账号：苏禾。苏禾负责试穿验证。苏禾与周宁接力。\n"
      "本轮不发布：陈晚。陈晚为事实确认人。陈晚承接申请。\n"
      "有限参战：林序。林序默认不发布。林序按触发条件启用。\n"
      "统一入口：企业微信。企业微信官方客服确认。企业微信为唯一入口。\n"
      "内容数量上限：三条主要短视频。三条为上限。三条不要求用满。")
p9 = pre("content_brief", GOOD_CB + "\n主讲账号周宁，苏禾接力，陈晚不发布，林序有限参战，统一入口企业微信，内容数量上限三条。", upstream=up)
p10 = pre("content_brief", GOOD_CB + ("\n主讲改为张三。张三负责全部。张三独立发布。"
                                    "李四接力。李四负责收尾。李四确认事实。"
                                    "王五承接。王五处理咨询。王五为入口。"), upstream=up)
check("E9 继承上游命名 → 漂移指标高", float(json.loads(p9["precheck_report"])["upstream_overlap"]) >= 0.6,
      p9["precheck_report"][:300])
check("E10 完全替换上游命名 → 零重合被判定为硬漂移并失败",
      p10["precheck_ok"] == "false" and "UPSTREAM_DRIFT" in p10["precheck_report"],
      p10["precheck_report"][:300])

p11 = pre("matrix", "## 第一部分：矩阵选择理由\n\n夹具已提供六类信息，因此不进入 `INPUT_INSUFFICIENT`。\n"
                    "## 第二部分：账号责任卡\n**账号责任**\n- **唯一使命（顾客决定与进展）**：略\n",
          sha="7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838",
          fb="7f9f0730f02149133178b14917b9e7a197ba7947539a230dc75bc66a8e289c91")
check("E11 正文中「不进入 INPUT_INSUFFICIENT」不得被误判为停机（build3 实测缺陷）",
      p11["precheck_ok"] == "true" and p11["is_stop_status"] == "false",
      p11["precheck_report"][:300])

p12 = pre("matrix", "```text\nINPUT_INSUFFICIENT\n\n缺失信息：\n- 缺少候选角色\n```",
          sha="7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838",
          fb="7f9f0730f02149133178b14917b9e7a197ba7947539a230dc75bc66a8e289c91")
check("E12 真正的整行停机声明仍被正确识别",
      p12["is_stop_status"] == "true" and p12["status_token"] == "INPUT_INSUFFICIENT",
      p12["precheck_report"][:300])


print()
print("=" * 96)
print("F. Artifact 落盘、STALE 传播与失败语义")
print("=" * 96)

base = snap_of(r3)
fin = finalize_main("matrix", GOOD_CB, "true", "Matrix Architect v0.1.2", "7a6a",
                    "deepseek-v4-flash", "fbsha", r3["snapshot_json"],
                    json.dumps({"precheck_ok": True, "status_token": "READY",
                                "is_stop_status": False, "chars": len(GOOD_CB)}, ensure_ascii=False),
                    {"contract_ok": "yes", "upstream_drift": "no", "fact_overreach": "no",
                     "notes": "ok"}, "run-abc")
sf = json.loads(fin["snapshot_json"])
check("F1 通过合同与 Judge → Artifact VALIDATED、写入 ref/hash/skill_sha",
      sf["artifacts"]["matrix"]["status"] == "VALIDATED"
      and sf["artifacts"]["matrix"]["content_hash"].startswith("sha256:")
      and sf["artifacts"]["matrix"]["run_id"] == "run-abc"
      and sf["last_result_ref"] == "matrix" and sf["phase"] == "COMPLETED",
      json.dumps(sf["artifacts"]["matrix"], ensure_ascii=False)[:300])
check("F2 完整产物不进快照，只留摘要与引用",
      len(fin["snapshot_json"]) < 4000
      and sf["artifacts"]["matrix"]["ref"] == "conversation.matrix_artifact",
      str(len(fin["snapshot_json"])))
check("F3 artifact_value 逐字等于 Tool Final", fin["artifact_value"] == GOOD_CB)

# downstream present, then matrix re-run → both go STALE
s_down = json.loads(fin["snapshot_json"])
for slot, typ in (("campaign", "CAMPAIGN"), ("content_brief", "CONTENT_BRIEF")):
    s_down["artifacts"][slot] = {"artifact_id": "a_" + slot, "artifact_type": typ,
                                 "revision": 1, "status": "USER_ACCEPTED",
                                 "content_hash": "sha256:old", "parent_artifact_id": None,
                                 "parent_hash": None, "skill_name": "x", "skill_sha": "y",
                                 "run_id": "r", "accepted_turn_id": "t",
                                 "summary": "s", "ref": "conversation." + slot + "_artifact"}
fin2 = finalize_main("matrix", GOOD_CB + "\n修改过的矩阵", "true", "Matrix Architect v0.1.2",
                     "7a6a", "deepseek-v4-flash", "fbsha",
                     json.dumps(s_down, ensure_ascii=False),
                     json.dumps({"precheck_ok": True, "status_token": "READY",
                                 "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                     {"contract_ok": "yes", "upstream_drift": "no", "fact_overreach": "no"},
                     "run-def")
sf2 = json.loads(fin2["snapshot_json"])
check("F4 Matrix 重出 → Campaign 与 Content Brief 同时 STALE",
      sf2["artifacts"]["campaign"]["status"] == "STALE"
      and sf2["artifacts"]["content_brief"]["status"] == "STALE",
      json.dumps({k: (v or {}).get("status") for k, v in sf2["artifacts"].items()}, ensure_ascii=False))

s_c = json.loads(fin2["snapshot_json"])
s_c["artifacts"]["campaign"]["status"] = "USER_ACCEPTED"
s_c["artifacts"]["content_brief"]["status"] = "USER_ACCEPTED"
fin3 = finalize_main("campaign", GOOD_CB, "true", "Campaign Orchestrator v0.1", "c7ef",
                     "deepseek-v4-flash", "fb", json.dumps(s_c, ensure_ascii=False),
                     json.dumps({"precheck_ok": True, "status_token": "READY",
                                 "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                     {"contract_ok": "yes", "upstream_drift": "no", "fact_overreach": "no"}, "r3")
sf3 = json.loads(fin3["snapshot_json"])
check("F5 Campaign 重出 → 只有 Content Brief STALE，Matrix 不受影响",
      sf3["artifacts"]["content_brief"]["status"] == "STALE"
      and sf3["artifacts"]["matrix"]["status"] != "STALE",
      json.dumps({k: (v or {}).get("status") for k, v in sf3["artifacts"].items()}, ensure_ascii=False))

fin4 = finalize_main("matrix", GOOD_CB, "true", "Matrix Architect v0.1.2", "7a6a",
                     "deepseek-v4-flash", "fb", r3["snapshot_json"],
                     json.dumps({"precheck_ok": True, "status_token": "READY",
                                 "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                     {"contract_ok": "yes", "upstream_drift": "yes", "fact_overreach": "no",
                      "notes": "主讲被换掉"}, "r4")
sf4 = json.loads(fin4["snapshot_json"])
check("F6 Judge 判定上游漂移 → Artifact FAILED，不进 VALIDATED，不声称完成",
      sf4["artifacts"]["matrix"]["status"] == "FAILED" and sf4["phase"] == "FAILED"
      and fin4["completed"] == "false", json.dumps(sf4["artifacts"]["matrix"], ensure_ascii=False)[:200])

fin5 = finalize_main("matrix", GOOD_CB, "true", "Matrix Architect v0.1.2", "7a6a",
                     "deepseek-v4-flash", "fb", r3["snapshot_json"],
                     json.dumps({"precheck_ok": True, "status_token": "READY",
                                 "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                     {}, "r5")
check("F7 Judge 结构化输出缺失 → 按失败处理（Fail Closed）",
      json.loads(fin5["snapshot_json"])["phase"] == "FAILED" and fin5["completed"] == "false",
      fin5["completed"])

ef = execfail_main(r3["snapshot_json"], "EXECUTE_MATRIX", "TOOL_INVOCATION",
                   "Server Unavailable Error")
se = json.loads(ef["snapshot_json"])
check("F8 Tool 调用失败 → phase=FAILED、记录 last_error、不写 Artifact",
      se["phase"] == "FAILED" and "TOOL_INVOCATION" in se["last_error"]
      and se["artifacts"]["matrix"] is None, json.dumps(se, ensure_ascii=False)[:200])

j1 = finalize_main("matrix", GOOD_CB, "true", "Matrix Architect v0.1.2", "7a6a",
                   "deepseek-v4-flash", "fb", r3["snapshot_json"],
                   json.dumps({"precheck_ok": True, "status_token": "READY",
                               "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                   {"contract_ok": "yes", "upstream_drift": "no", "fact_overreach": "yes",
                    "notes": "第 3 节出现输入里没有的经营事实"}, "rj1")
check("F12 Judge 只判事实越界时 → 失败原因必须是 JUDGE_FACT_OVERREACH，不能误报为合同不符",
      "JUDGE_FACT_OVERREACH" in j1["finalize_report"]
      and "JUDGE_CONTRACT_NOT_MET" not in j1["finalize_report"],
      j1["finalize_report"][:260])

h1 = finalize_main("matrix", GOOD_CB, "true", "Matrix Architect v0.1.2", "7a6a",
                   "deepseek-v4-flash", "fb", r3["snapshot_json"],
                   json.dumps({"precheck_ok": True, "status_token": "READY",
                               "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                   {"contract_ok": "yes", "upstream_drift": "no", "fact_overreach": "no",
                    "notes": "ok"}, "rh1")
check("F9 Judge 以字符串枚举回答（Dify prompt-based 结构化输出的实际形态）→ 正确判为通过",
      json.loads(h1["snapshot_json"])["artifacts"]["matrix"]["status"] == "VALIDATED",
      h1["finalize_report"][:200])

h2 = finalize_main("matrix", GOOD_CB, "true", "Matrix Architect v0.1.2", "7a6a",
                   "deepseek-v4-flash", "fb", r3["snapshot_json"],
                   json.dumps({"precheck_ok": True, "status_token": "READY",
                               "is_stop_status": False, "chars": 10}, ensure_ascii=False),
                   {"contract_ok": "maybe", "upstream_drift": "no", "fact_overreach": "no"}, "rh2")
check("F10 Judge 回答不在枚举内 → 视为结论缺失，Fail Closed",
      h2["completed"] == "false"
      and "JUDGE_VERDICT_MISSING" in h2["finalize_report"], h2["finalize_report"][:200])

hb = state_main("接受并继续", json.dumps(sv, ensure_ascii=False),
                patch(route_intent="EXECUTE_REQUEST",
                      acceptance_signal="ACCEPT_CURRENT_ARTIFACT", continue_signal=True))
check("F11 影子仍回布尔 true（旧形态）→ 兼容接受，不因此判负",
      hb["patch_ok"] == "true" and hb["effective_route"] == "EXECUTE_CAMPAIGN",
      hb["effective_route"])

print()
print("=" * 96)
print("G. 已修复缺陷的回归（build2 实测暴露）")
print("=" * 96)

g1 = state_main("把四个账号的分工定下来，减少内容重复，提高到店试穿转化。就按这个做。", "",
                patch(route_intent="EXECUTE_REQUEST", task_action="CREATE",
                      change_goal="把四个账号的分工定下来，减少内容重复，提高到店试穿转化",
                      change_target_object="四个账号"))
sg1 = snap_of(g1)
check("G1 一轮内「陈述任务＋就按这个做」→ 任务当场确认，路由 CONFIRM_TASK，且不执行",
      sg1["confirmed_task"] is not None and g1["effective_route"] == "CONFIRM_TASK",
      "%s / %s" % (g1["effective_route"], sg1["phase"]))

g2 = state_main("跑账号矩阵。", g1["snapshot_json"],
                patch(route_intent="EXECUTE_REQUEST", requested_skill="MATRIX"))
check("G2 下一轮点名 Skill → 立即执行，不再要求形式主义确认",
      g2["effective_route"] == "EXECUTE_MATRIX", g2["effective_route"])

g3 = state_main("跑矩阵", g1["snapshot_json"], {"goal": "x", "target_object": "y"})
check("G3 影子只回嵌套子对象（build2 实测失败形态）→ 整体拒绝、Fail Open、不执行",
      g3["patch_ok"] == "false" and g3["effective_route"] == "DISCUSS", g3["reject_reason"])

i1 = state_main("把四个账号的分工定下来，减少内容重复，提高到店试穿转化。就按这个做，现在跑账号矩阵。", "",
                patch(route_intent="EXECUTE_REQUEST", task_action="NONE",
                      requested_skill="MATRIX",
                      change_goal="把四个账号的分工定下来，减少内容重复，提高到店试穿转化"))
si1 = snap_of(i1)
check("I1 影子填了 change_goal 却把 task_action 标成 NONE（build7 实测形态）→ 仍按任务陈述处理并执行",
      i1["effective_route"] == "EXECUTE_MATRIX" and si1["confirmed_task"] is not None,
      "%s / %s" % (i1["effective_route"], json.dumps(si1["draft_task"], ensure_ascii=False)))

i2 = state_main("跑一下", "", patch(route_intent="EXECUTE_REQUEST", task_action="NONE",
                                  requested_skill="MATRIX", change_goal="跑一下"))
check("I2 同样形态但目标只是命令 → 仍被薄目标下限拦下",
      not i2["effective_route"].startswith("EXECUTE_")
      and snap_of(i2)["blocking_gap"] == "SAME_TURN_GOAL_TOO_THIN", i2["effective_route"])

i3 = state_main("我们几个账号发的内容老是撞车。", "",
                patch(route_intent="FOCUS", task_action="NONE",
                      change_goal="我们几个账号发的内容老是撞车"))
si3 = snap_of(i3)
check("I3 只描述症状不要求执行 → 记为草稿任务，但不执行",
      not i3["effective_route"].startswith("EXECUTE_")
      and (si3["draft_task"] or {}).get("goal") == "我们几个账号发的内容老是撞车",
      i3["effective_route"])

print()
print("=" * 96)
print("H. 取消后与薄目标的执行拦截（build6 实测暴露）")
print("=" * 96)

# Exactly the live S06 sequence: run → accept → cancel → "把矩阵跑一下吧"
h_1 = state_main("帮我把四个账号的分工理清楚，减少内容重复。", "",
                 patch(route_intent="EXECUTE_REQUEST", task_action="CREATE",
                       requested_skill="MATRIX",
                       change_goal="把四个账号的分工理清楚，减少内容重复"))
check("H1 首轮陈述业务目标并要求执行 → 允许执行", h_1["effective_route"] == "EXECUTE_MATRIX",
      h_1["effective_route"])

h_2 = state_main("算了，这个先不做了，取消吧。", h_1["snapshot_json"],
                 patch(route_intent="CANCEL", task_action="CANCEL"))
sh2 = snap_of(h_2)
check("H2 取消 → phase=CANCELLED，draft 与 confirmed 全清",
      sh2["phase"] == "CANCELLED" and sh2["confirmed_task"] is None
      and (sh2["draft_task"] or {}).get("goal") is None,
      json.dumps(sh2["draft_task"], ensure_ascii=False))

h_3 = state_main("那你还是把矩阵跑一下吧。", h_2["snapshot_json"],
                 patch(route_intent="EXECUTE_REQUEST", task_action="CREATE",
                       requested_skill="MATRIX", change_goal="把矩阵跑一下"))
sh3 = snap_of(h_3)
check("H3 取消后用一句命令想重启 → 拒绝执行，要求重新说清经营问题（build6 实测 Hard Gate 缺口）",
      not h_3["effective_route"].startswith("EXECUTE_")
      and sh3["blocking_gap"] == "CANCELLED_NEEDS_EXPLICIT_RECONFIRM",
      "%s / %s" % (h_3["effective_route"], sh3["blocking_gap"]))

h_4 = state_main("跑一下吧。", "", patch(route_intent="EXECUTE_REQUEST", task_action="CREATE",
                                    requested_skill="MATRIX", change_goal="跑一下"))
sh4 = snap_of(h_4)
check("H4 空会话里把执行命令当成任务目标 → 拒绝执行",
      not h_4["effective_route"].startswith("EXECUTE_")
      and sh4["blocking_gap"] == "SAME_TURN_GOAL_TOO_THIN",
      "%s / %s" % (h_4["effective_route"], sh4["blocking_gap"]))

h_5 = state_main("这次要解决的是：把四个账号分工定清楚，减少内容重复。现在跑矩阵。",
                 h_2["snapshot_json"],
                 patch(route_intent="EXECUTE_REQUEST", task_action="CREATE",
                       requested_skill="MATRIX",
                       change_goal="把四个账号分工定清楚，减少内容重复"))
check("H5 取消后重新说清经营问题 → 本轮仍需确认，不立即执行",
      not h_5["effective_route"].startswith("EXECUTE_"), h_5["effective_route"])

h_6 = state_main("对，就这个。", h_5["snapshot_json"],
                 patch(route_intent="CONFIRM_TASK", confirmation_signal="AFFIRM"))
h_7 = state_main("现在跑矩阵。", h_6["snapshot_json"],
                 patch(route_intent="EXECUTE_REQUEST", requested_skill="MATRIX"))
check("H6 取消后重新确认任务 → 恢复可执行", h_7["effective_route"] == "EXECUTE_MATRIX",
      h_7["effective_route"])


print("=" * 96)
frozen_bad = check_frozen()
static_bad = run_static()
print()
print("=" * 96)
print("总计：冻结资产不符 %d 项；静态检查失败 %d 项；单元测试失败 %d 项"
      % (len(frozen_bad), len(static_bad), len(FAILS)))
for f in FAILS:
    print("  单元测试失败 - %s" % f)
for f in frozen_bad:
    print("  冻结资产不符 - %s" % f)
print("=" * 96)
sys.exit(1 if (frozen_bad or static_bad or FAILS) else 0)
