#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UAPP 已接受上游产物绑定｜Phase C 确定性正负控制 C-01…C-12。**零模型调用、零写入。**

直接从构建器取 PERSIST_CODE 与 PICK_CODE 的**同一份源**离线执行，
用合成夹具驱动。夹具正文全部是中性合成文本，不含任何真实案例内容。

C-11 是单点变异：把选择器里某一条合法性条件的判断式替换成 False（单点、可复算），
对应的负控制必须由「拒绝」翻成「选中」——证明那条条件真的在起作用。

    python3 UAAB_PHASE_C_CONTROLS_v1.0.py
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "uapp_artifact_binding")

_b = importlib.util.spec_from_file_location(
    "uaab_build", os.path.join(HERE, "UAAB_BUILD_BINDING_FIX_v1.0.py"))
B = importlib.util.module_from_spec(_b)
_b.loader.exec_module(B)

CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
CAND_MD5_FROZEN = "99c3edf7bd12172a4fb011b588f25e57"
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_STABLE_MD5 = "788c8555aca09e6fa6d979f237f70157"
PP_B2_MD5 = "8366328bf827bd0f460455d750d45c4f"
HOP_PIN = "2026-08-30 03:38:31.449618"
PROTECTED = {"M1_HOST": ("a4c3b19b-243f-490b-9aca-3aa19767d6a5", "cd93757bcf8ad322f3b32fc43b2da3ff"),
             "HOP": ("6c46fdb1-5f49-4513-a0c0-29957b3dcee4", "e38378c3c2a66b75aa7e645368c9e1ce"),
             "SEAM": ("5fca0162-e26b-4545-a00b-66b1a2a2a077", "db49a3da8973d4fdcbe9ecf63bdf7e2a"),
             "MATRIX": ("fd25ebfa-db67-40c3-82e5-202e1254facf", "6cdaeac9cacf69fbeea4bd25e1536ace"),
             "CAMPAIGN": ("1f9d65ea-8af5-45f0-a1d0-a80223d354e2", "4876dacc43a73741b41c5a3083796347"),
             "CONTENT_BRIEF": ("b1dcf784-540e-4b3f-8ba2-3812f477f3ce", "0c841642a71feedfb327ffb76aec0ddd"),
             "CREATIVE_SCRIPT": ("44b55f9d-3792-40c3-b095-f2696464b4ec", "a1cd859d5b88d0d025f336665ca94e51"),
             "PRODUCTION_DIRECTOR": ("13cfabd5-f592-4354-a304-47098b765697", "964e9a947dc9790d1de82496469689ad")}

TASK = "TASK-A"
OTHER_TASK = "TASK-B"
PD_BODY = ("## 制作方案（合成夹具）\n\n本段是控制用合成文本，不含任何真实案例内容。\n"
           "镜头一：说明判断依据。镜头二：给出三步做法。镜头三：收束。\n"
           "素材状态：待检索。场地：门店。人手：一人。时间窗：半天。\n") * 3
CS_BODY = "## 口播稿（合成夹具）\n\n第一段。第二段。第三段。合成文本，无真实内容。\n" * 3
PP_BODY = "## 包装产出（合成夹具）\n\n标题候选。封面文字。发布文案。合成文本，无真实内容。\n" * 3


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def fp(s):
    h = 0xcbf29ce484222325
    for b in (s or "").encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def load(code, name):
    ns = {}
    exec(compile(code, name, "exec"), ns)
    return ns["main"]


PICK = load(B.PICK_CODE, "pick")
PERSIST = load(B.PERSIST_CODE, "persist")


def art(cap, body, turn, accepted, stale, task_key=TASK):
    n = norm(body)
    return {"fp": fp(n[:256]), "nlen": len(n), "len": len(body), "cap": cap,
            "task_key": task_key, "turn": turn,
            "accepted": accepted, "accepted_turn": turn + 1 if accepted else None,
            "accepted_rev": turn + 1 if accepted else None,
            "dep": {}, "stale": stale, "stale_reason": "X" if stale else None}


def item(cap, body, turn, task_key=TASK, break_body=False, wrong_cap=None):
    n = norm(body)
    it = {"fp": fp(n[:256]), "bfp": fp(n), "cap": wrong_cap or cap, "turn": turn,
          "task_key": task_key, "len": len(body), "nlen": len(n), "body": body}
    if break_body:
        it["body"] = body + "\n被篡改的一行，正文与登记摘要不再一致。"
    return it


def store(items):
    return json.dumps({"v": 1, "items": items}, ensure_ascii=False)


def state(arts, task_key=TASK, rev=9):
    return json.dumps({"task_key": task_key, "rev": rev, "artifacts": arts, "fields": {}},
                      ensure_ascii=False)


def run(pick_fn, arts, items, uq, tgt="PUBLISHING_PACKAGING", task_key=TASK):
    return pick_fn(store(items), state(arts, task_key), tgt, uq, task_key)


def main():
    R = []

    def add(cid, ok, text, obs):
        R.append({"id": cid, "text": text, "result": "PASS" if ok else "FAIL", "observed": obs})

    PD_OK = art("PRODUCTION_DIRECTOR", PD_BODY, 6, True, False)
    PP_ACC = art("PUBLISHING_PACKAGING", PP_BODY, 7, True, False)
    PP_NEW = art("PUBLISHING_PACKAGING", PP_BODY, 7, False, False)
    CS_OK = art("CREATIVE_SCRIPT", CS_BODY, 4, True, False)
    I_PD = item("PRODUCTION_DIRECTOR", PD_BODY, 6)
    I_PP = item("PUBLISHING_PACKAGING", PP_BODY, 7)
    I_CS = item("CREATIVE_SCRIPT", CS_BODY, 4)
    ASK = "基于刚才那份制作方案，重新给我一版标题和封面。"

    # ---------- C-01 已接受 PD + 后续未接受 PP → 选 PD ----------
    r = run(PICK, [CS_OK, PD_OK, PP_NEW], [I_CS, I_PD, I_PP], ASK)
    add("C-01", r["selection_status"] == "SELECTED"
        and r["upstream_capability"] == "PRODUCTION_DIRECTOR"
        and r["upstream_delivery"] == PD_BODY,
        "已接受 PD + 后续未接受 PP → PP 再次调用时选择 PD，不选择 PP",
        {"status": r["selection_status"], "cap": r["upstream_capability"],
         "fp": r["selected_fp"], "delivery_is_pd_body": r["upstream_delivery"] == PD_BODY,
         "delivery_is_pp_body": r["upstream_delivery"] == PP_BODY,
         "note": r["selection_note"][:300]})

    # ---------- C-02 正文摘要与账本一致 → 允许进入 ----------
    add("C-02", r["selected_fp"] == PD_OK["fp"] and r["selected_bfp"] == I_PD["bfp"]
        and fp(norm(r["upstream_delivery"])[:256]) == PD_OK["fp"],
        "PD body hash 与 ledger hash 一致 → 允许进入 content_body_or_beats",
        {"ledger_fp": PD_OK["fp"], "selected_fp": r["selected_fp"],
         "store_bfp": I_PD["bfp"], "selected_bfp": r["selected_bfp"],
         "recomputed_from_delivery": fp(norm(r["upstream_delivery"])[:256])})

    # ---------- C-03 经过中间能力轮次后仍可取回 ----------
    s1 = store([I_CS, I_PD])
    st1 = state([CS_OK, PD_OK], rev=7)
    p1 = PERSIST(PP_BODY, "PUBLISHING_PACKAGING", s1, "PRODUCTION_DIRECTOR", st1)
    st2 = state([CS_OK, PD_OK, PP_NEW], rev=8)
    p2 = PERSIST("", "PUBLISHING_PACKAGING", p1["store_to_persist"], "PUBLISHING_PACKAGING", st2)
    r3 = PICK(p2["store_to_persist"], st2, "PUBLISHING_PACKAGING", ASK, TASK)
    add("C-03", r3["selection_status"] == "SELECTED" and r3["upstream_delivery"] == PD_BODY,
        "经过一个或多个中间能力轮次后 → 已接受 PD 仍可取回",
        {"persist_action_t7": p1["persist_action"], "persist_action_t8": p2["persist_action"],
         "store_items": p2["store_item_count"], "status": r3["selection_status"],
         "cap": r3["upstream_capability"], "delivery_is_pd_body": r3["upstream_delivery"] == PD_BODY,
         "store_note": p2["store_note"]})

    # ---------- C-04 点名「刚才的制作方案」→ 解析到 PD ----------
    r4a = run(PICK, [CS_OK, PD_OK, PP_NEW], [I_CS, I_PD, I_PP], ASK)
    # 真正的「未点名」用例：不出现任何能力词，只能靠兼容优先级落到 PD。
    # 原写法用了「口播稿」——那是点名 CREATIVE_SCRIPT，不是未点名（夹具错误，已更正）。
    r4b = run(PICK, [CS_OK, PD_OK, PP_NEW], [I_CS, I_PD, I_PP], "再给我一版标题和封面。")
    r4c = run(PICK, [CS_OK, PD_OK, PP_NEW], [I_CS, I_PD, I_PP], "接着把这条的口播稿再顺一遍。")
    add("C-04", r4a["upstream_capability"] == "PRODUCTION_DIRECTOR"
        and "点名=PRODUCTION_DIRECTOR" in r4a["selection_note"]
        and r4b["upstream_capability"] == "PRODUCTION_DIRECTOR"
        and r4c["upstream_capability"] == "CREATIVE_SCRIPT",
        "用户明确说「基于刚才的制作方案」→ 解析到 PD artifact",
        {"named_pd_case_cap": r4a["upstream_capability"],
         "named_marker_in_note": "点名=PRODUCTION_DIRECTOR" in r4a["selection_note"],
         "unnamed_case_cap_by_priority": r4b["upstream_capability"],
         "named_cs_case_cap": r4c["upstream_capability"],
         "named_cs_marker": "点名=CREATIVE_SCRIPT" in r4c["selection_note"],
         "priority_order": "PUBLISHING_PACKAGING → [PRODUCTION_DIRECTOR, CREATIVE_SCRIPT]",
         "meaning": "点名 PD → PD；不点名 → 按优先级仍是 PD；点名 CS → CS（点名压过优先级）"})

    # ---------- C-05 accepted=false → 不得选择 ----------
    PD_NA = art("PRODUCTION_DIRECTOR", PD_BODY, 6, False, False)
    r5 = run(PICK, [PD_NA], [I_PD], "再给我一版标题和封面。")
    add("C-05", r5["selection_status"] == "NO_LEGAL_UPSTREAM"
        and "NOT_ACCEPTED" in r5["selection_note"] and not r5["upstream_delivery"],
        "PD accepted=false → 不得选择",
        {"status": r5["selection_status"], "delivery_len": len(r5["upstream_delivery"]),
         "reason_in_note": "NOT_ACCEPTED" in r5["selection_note"]})

    # ---------- C-06 stale=true → 不得选择 ----------
    PD_ST = art("PRODUCTION_DIRECTOR", PD_BODY, 6, True, True)
    r6 = run(PICK, [PD_ST], [I_PD], "再给我一版标题和封面。")
    add("C-06", r6["selection_status"] == "NO_LEGAL_UPSTREAM"
        and "STALE" in r6["selection_note"] and not r6["upstream_delivery"],
        "PD stale=true → 不得选择",
        {"status": r6["selection_status"], "delivery_len": len(r6["upstream_delivery"]),
         "reason_in_note": "STALE" in r6["selection_note"]})

    # ---------- C-07 跨 task → 不得选择 ----------
    PD_X = art("PRODUCTION_DIRECTOR", PD_BODY, 6, True, False, task_key=OTHER_TASK)
    r7 = PICK(store([item("PRODUCTION_DIRECTOR", PD_BODY, 6, task_key=OTHER_TASK)]),
              state([PD_X], task_key=TASK), "PUBLISHING_PACKAGING", ASK, TASK)
    add("C-07", r7["selection_status"] == "NO_LEGAL_UPSTREAM"
        and "CROSS_TASK" in r7["selection_note"] and not r7["upstream_delivery"],
        "PD 属于其他 task/account → 不得选择",
        {"status": r7["selection_status"], "reason_in_note": "CROSS_TASK" in r7["selection_note"],
         "ledger_task": TASK, "artifact_task": OTHER_TASK})

    # ---------- C-08 正文与登记摘要不一致 → fail-closed ----------
    I_BAD = item("PRODUCTION_DIRECTOR", PD_BODY, 6, break_body=True)
    r8 = run(PICK, [PD_OK], [I_BAD], ASK)
    add("C-08", r8["selection_status"] == "NO_LEGAL_UPSTREAM"
        and "BODY_DIGEST_MISMATCH" in r8["selection_note"] and not r8["upstream_delivery"],
        "body hash 与 ledger 不一致 → fail-closed",
        {"status": r8["selection_status"], "delivery_len": len(r8["upstream_delivery"]),
         "reason_in_note": "BODY_DIGEST_MISMATCH" in r8["selection_note"]})

    # ---------- C-09 只有未接受 PP，无合法 PD → 精确询问，不自循环 ----------
    r9 = run(PICK, [PP_NEW], [I_PP], "再给我一版标题和封面。")
    add("C-09", r9["selection_status"] == "NO_LEGAL_UPSTREAM"
        and not r9["upstream_delivery"] and bool(r9["selection_question"])
        and "SELF_UPSTREAM_FORBIDDEN" in r9["selection_note"],
        "只有未接受 PP artifact，没有合法 PD → 精确询问缺口，不自循环",
        {"status": r9["selection_status"], "delivery_len": len(r9["upstream_delivery"]),
         "question": r9["selection_question"],
         "self_upstream_blocked": "SELF_UPSTREAM_FORBIDDEN" in r9["selection_note"]})

    # ---------- C-10 并列候选无法唯一消歧 → 询问用户 ----------
    PD_A = art("PRODUCTION_DIRECTOR", PD_BODY, 6, True, False)
    PD_B = art("PRODUCTION_DIRECTOR", PD_BODY + "另一份并列产物。", 6, True, False)
    r10 = run(PICK, [PD_A, PD_B],
              [I_PD, item("PRODUCTION_DIRECTOR", PD_BODY + "另一份并列产物。", 6)], ASK)
    add("C-10", r10["selection_status"] == "AMBIGUOUS" and not r10["upstream_delivery"]
        and bool(r10["selection_question"]),
        "两个候选无法唯一消歧 → 询问用户，不自行选择",
        {"status": r10["selection_status"], "delivery_len": len(r10["upstream_delivery"]),
         "question": r10["selection_question"], "note": r10["selection_note"][:200]})

    # ---------- C-11 单点变异：删掉任一条件，对应负控制必须翻 FAIL ----------
    MUT = [
        {"id": "accepted", "old": 'elif not (a.get("accepted") or fp == accepted_now_fp):',
         "new": "elif False:",
         "case": lambda f: run(f, [PD_NA], [I_PD], "再给我一版标题和封面。"),
         "baseline": "NO_LEGAL_UPSTREAM"},
        {"id": "stale", "old": 'elif a.get("stale"):', "new": "elif False:",
         "case": lambda f: run(f, [PD_ST], [I_PD], "再给我一版标题和封面。"),
         "baseline": "NO_LEGAL_UPSTREAM"},
        {"id": "same_task",
         "old": 'elif tk and (a.get("task_key") or ledger_task) and \\\n'
                '                (a.get("task_key") or ledger_task) != tk:',
         "new": "elif False:",
         "case": lambda f: f(store([item("PRODUCTION_DIRECTOR", PD_BODY, 6,
                                         task_key=OTHER_TASK)]),
                             state([PD_X], task_key=TASK), "PUBLISHING_PACKAGING", ASK, TASK),
         "baseline": "NO_LEGAL_UPSTREAM"},
        # 兼容性条件由两道守卫实现（自上游禁令 + 兼容清单），且对任意 cap 二者必然同时命中
        # （COMPAT[tgt] 永不含 tgt）。因此隔离该条件必须同时去掉两道守卫；
        # 夹具用「已接受、未 STALE 的 PP 产物」，让兼容性成为唯一拦阻理由。
        {"id": "compatible_and_not_self",
         "old": '"PUBLISHING_PACKAGING": ["PRODUCTION_DIRECTOR", "CREATIVE_SCRIPT"],',
         "new": '"PUBLISHING_PACKAGING": ["PUBLISHING_PACKAGING", "PRODUCTION_DIRECTOR", '
                '"CREATIVE_SCRIPT"],',
         "old2": 'if cap == tgt:', "new2": "if False:",
         "case": lambda f: run(f, [PP_ACC], [I_PP], "再给我一版标题和封面。"),
         "baseline": "NO_LEGAL_UPSTREAM"},
        {"id": "body_digest", "old": 'elif it.get("bfp") and _fp(nb) != it.get("bfp"):',
         "new": "elif False:",
         "case": lambda f: run(f, [PD_OK], [I_BAD], ASK),
         "baseline": "NO_LEGAL_UPSTREAM"},
    ]
    mres = []
    for m in MUT:
        cnt = B.PICK_CODE.count(m["old"])
        if cnt != 1:
            mres.append({"id": m["id"], "error": "变异锚点出现 %d 次" % cnt, "flipped": False})
            continue
        mutated = B.PICK_CODE.replace(m["old"], m["new"], 1)
        if m.get("old2"):
            if mutated.count(m["old2"]) != 1:
                mres.append({"id": m["id"], "error": "第二处变异锚点不唯一", "flipped": False})
                continue
            mutated = mutated.replace(m["old2"], m["new2"], 1)
        mf = load(mutated, "pick_mut_" + m["id"])
        base = m["case"](PICK)
        after = m["case"](mf)
        flipped = (base["selection_status"] == m["baseline"]
                   and after["selection_status"] == "SELECTED")
        mres.append({"id": m["id"], "baseline_status": base["selection_status"],
                     "after_mutation_status": after["selection_status"],
                     "after_mutation_delivery_len": len(after["upstream_delivery"]),
                     "flipped": flipped})
    # 子探针：只去掉自上游禁令，结果仍被拦住，但拒绝理由从 SELF_UPSTREAM_FORBIDDEN
    # 变为 CAPABILITY_INCOMPATIBLE —— 证明两道守卫各自留下可观察的不同证据（A5 不可互换）。
    COMPAT_OLD = '"PUBLISHING_PACKAGING": ["PRODUCTION_DIRECTOR", "CREATIVE_SCRIPT"],'
    COMPAT_NEW = ('"PUBLISHING_PACKAGING": ["PUBLISHING_PACKAGING", "PRODUCTION_DIRECTOR", '
                  '"CREATIVE_SCRIPT"],')
    only_self = B.PICK_CODE.replace("if cap == tgt:", "if False:", 1)
    only_list = B.PICK_CODE.replace(COMPAT_OLD, COMPAT_NEW, 1)
    r_self = run(load(only_self, "pick_only_self"), [PP_ACC], [I_PP], "再给我一版标题和封面。")
    r_list = run(load(only_list, "pick_only_list"), [PP_ACC], [I_PP], "再给我一版标题和封面。")
    r_base = run(PICK, [PP_ACC], [I_PP], "再给我一版标题和封面。")
    guard_probe = {
        "baseline_status": r_base["selection_status"],
        "baseline_reason_is_self_upstream": "SELF_UPSTREAM_FORBIDDEN" in r_base["selection_note"],
        "remove_self_guard_only": {
            "status": r_self["selection_status"],
            "still_blocked": r_self["selection_status"] == "NO_LEGAL_UPSTREAM",
            "reason_now_capability_incompatible":
                "CAPABILITY_INCOMPATIBLE" in r_self["selection_note"]},
        "remove_compat_list_only": {
            "status": r_list["selection_status"],
            "still_blocked": r_list["selection_status"] == "NO_LEGAL_UPSTREAM",
            "reason_still_self_upstream":
                "SELF_UPSTREAM_FORBIDDEN" in r_list["selection_note"]},
        "meaning": "兼容性条件由两道守卫实现（自上游禁令 + 兼容清单），互为冗余但不可互换："
                   "去掉任一道，拒绝仍成立而留下的证据不同；两道同时去掉才放行。"
                   "因此隔离该条件必须双点变异——这是冗余，不是覆盖缺口。"}

    add("C-11", all(x.get("flipped") for x in mres)
        and guard_probe["remove_self_guard_only"]["still_blocked"]
        and guard_probe["remove_self_guard_only"]["reason_now_capability_incompatible"]
        and guard_probe["remove_compat_list_only"]["still_blocked"]
        and guard_probe["remove_compat_list_only"]["reason_still_self_upstream"],
        "删除「accepted / current-non-stale / same-task / compatible / body-hash」任一条件 → "
        "对应负控制必须转 FAIL",
        {"mutations": mres, "count": len(mres), "guard_redundancy_probe": guard_probe})

    # ---------- C-12 保护面零漂移 ----------
    now = {k: psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % v[0]).strip() for k, v in sorted(PROTECTED.items())}
    drift = {k: {"frozen": PROTECTED[k][1], "now": v}
             for k, v in now.items() if v != PROTECTED[k][1]}
    cand_pub = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                    "where a.id='%s';" % CAND)
    pp_pub = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                  "where a.id='%s';" % PP_APP)
    pp_pin_md5 = psql("select md5(graph) from workflows where app_id='%s' and version="
                      "(select version from tool_workflow_providers where "
                      "name='diyu_m5fp_publishing_packaging');" % PP_APP)
    b2_row = psql("select count(*) from workflows where app_id='%s' and md5(graph)='%s';"
                  % (PP_APP, PP_B2_MD5))
    hop = psql("select version from tool_workflow_providers where name='diyu_uapp_hop';")
    add("C-12", not drift and cand_pub == CAND_MD5_FROZEN and pp_pub == PP_STABLE_MD5
        and pp_pin_md5 == PP_STABLE_MD5 and hop == HOP_PIN and int(b2_row) >= 1,
        "保护面及无关节点零漂移",
        {"other_eight_drift": drift, "candidate_published_md5": cand_pub,
         "candidate_frozen": CAND_MD5_FROZEN,
         "pp_published_md5": pp_pub, "pp_provider_pinned_graph_md5": pp_pin_md5,
         "pp_b2_row_preserved": int(b2_row), "hop_pin": hop,
         "note": "本阶段只改候选画布的 draft，尚未发布；已发布图仍为冻结值"})

    npass = sum(1 for x in R if x["result"] == "PASS")
    rep = {"document": {"id": "UAAB_PHASE_C_CONTROLS_v1.0",
                        "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
                        "model_calls": 0, "writes": 0,
                        "persist_code_sha256": sha(B.PERSIST_CODE),
                        "pick_code_sha256": sha(B.PICK_CODE),
                        "fixtures": "全部为中性合成文本，不含任何真实案例内容"},
           "summary": {"pass": npass, "total": len(R),
                       "verdict": "PASS" if npass == len(R) else "FAIL"},
           "checks": R}
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "UAAB_PHASE_C_CONTROLS.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    for x in R:
        print("%-6s %-4s %s" % (x["id"], x["result"], x["text"][:64]))
        if x["result"] != "PASS":
            print("       " + json.dumps(x["observed"], ensure_ascii=False)[:900])
    print("---- %d/%d ----" % (npass, len(R)))
    return 0 if npass == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
