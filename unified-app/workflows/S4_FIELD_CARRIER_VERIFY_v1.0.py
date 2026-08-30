#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TD-UAPP-20 最小修复的零模型调用验证｜11 项，全部在任何模型调用之前落盘。

主证据是**历史失败回放**：把 S4-PC-T2…T6 真实记录下来的 hop 外壳与缺口，
按原顺序喂进新的合成节点，看被观测到的三处字段丢失还在不在。
不新建场景、不改被测对象、不碰真实证据目录。
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EV = os.path.join(UAPP, "evidence", "stages", "s4_phase_c")
OUT = os.path.join(UAPP, "evidence", "stages", "s4_phase_c", "FIELD_CARRIER_VERIFICATION.json")

_s = importlib.util.spec_from_file_location("s4build", os.path.join(HERE, "S4_BUILD_v1.0.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
_s2 = importlib.util.spec_from_file_location("scope", os.path.join(HERE, "S4_SCOPE_ISOLATION_PREFLIGHT_v1.0.py"))
SC = importlib.util.module_from_spec(_s2)
_s2.loader.exec_module(SC)

PROTECTED = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
             "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
             "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
             "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
             "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
             "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
             "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
             "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
             "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df"}


def load(src, name):
    m = types.ModuleType(name)
    exec(compile(src, name, "exec"), m.__dict__)
    return m


F = load(B.FIELDS_SRC, "fields_node")
P = load(B.PERSIST_SRC, "persist_node")

RES = []


def chk(cid, text, cond, detail=""):
    RES.append({"id": cid, "text": text, "result": "PASS" if cond else "FAIL",
                "detail": detail if isinstance(detail, (dict, list)) else str(detail)[:900]})
    print("  %s  %s %s" % ("PASS" if cond else "FAIL", cid, text))
    if not cond:
        print("        " + json.dumps(detail, ensure_ascii=False)[:700]
              if isinstance(detail, (dict, list)) else "        " + str(detail)[:700])


def env_field(env, key):
    m = re.search(r"^\s*`%s`\s*:\s*(.*)$" % re.escape(key), env or "", re.M)
    return (m.group(1).strip() if m else "")


def gapset(text):
    return {x.strip() for x in re.split(r"[；;]", text or "") if x.strip() and x.strip() != "无"}


def real(i):
    d = json.load(io.open(os.path.join(EV, "S4-PC-T%d.json" % i), encoding="utf-8"))
    N = {n["node_id"]: n for n in d["node_detail"]}
    ho = json.loads(N["uapp_hop"]["outputs"])
    art = json.loads(N["uapp_seam_merge"]["outputs"])["artifact"]["output"]
    return ho["capability_call"], (ho["extraction_gaps_text"] or ""), \
        json.loads(N["uapp_route"]["outputs"])["target_capability"], art


TASK = "200efb2e-a08c-4da8-8bb7-183882ce55ca"


def replay(task_key=TASK, turns=(2, 3, 4, 5, 6), carrier=""):
    out = []
    for i in turns:
        cc, gt, cap, art = real(i)
        r = F.main(carrier, task_key, cc, gt, cap)
        carrier = r["task_fields_json"]
        out.append({"turn": i, "cap": cap, "in_gaps": sorted(gapset(gt)),
                    "out_gaps": sorted(gapset(r["gaps_text"])), "r": r, "art": art})
    return out, carrier


def main():
    print("=== 历史失败回放：真实 T2–T6 外壳按原顺序过新合成节点 ===")
    rp, carrier_end = replay()
    by = {x["turn"]: x for x in rp}

    # F-01 用户本轮确认的 content_origin_mode 进入载体
    c4 = json.loads(by[4]["r"]["task_fields_json"])
    f4 = (c4["fields"].get("content_origin_mode") or {})
    chk("F-01", "用户确认的 content_origin_mode 进入任务作用域载体",
        f4.get("v", "").startswith("使用门店已有素材剪辑") and f4.get("lvl") == "A",
        {"value": f4.get("v"), "level": f4.get("lvl"),
         "T3_asked": json.loads(by[3]["r"]["task_fields_json"])["asked"]})

    # F-02 下一轮抽取器留空也不得擦除
    t5 = by[5]
    chk("F-02", "T5 抽取器返回空值时不擦除 content_origin_mode",
        "content_origin_mode" in t5["in_gaps"]
        and "content_origin_mode" not in t5["out_gaps"]
        and env_field(t5["r"]["capability_call"], "content_origin_mode").startswith("使用门店已有素材剪辑"),
        {"in_gaps": t5["in_gaps"], "out_gaps": t5["out_gaps"],
         "carried": t5["r"]["carried_fields"],
         "value_in_envelope": env_field(t5["r"]["capability_call"], "content_origin_mode")})

    # F-03 已确认字段在整个任务内被保留，并在成为缺口时由载体补齐
    # 判据说明：能力必填清单由各能力合同决定，audience_problem 本就不在 CREATIVE_SCRIPT
    # 的清单里。往非必填的能力外壳里硬塞字段会破坏能力合同，不是"保留"。
    # 因此这一条判的是裁决真正要求的三件事：
    #   (a) 已确认字段在整个任务内不被移出载体（单调不减）
    #   (b) 任一已确认字段成为本轮缺口时，一律由载体补齐，不留空
    #   (c) 合成之后不存在"载体本可补而没补"的残留缺口
    keep = ("content_promise", "primary_goal", "audience_problem", "expected_change",
            "facts_registered", "expression_subject_and_boundary")
    seen, shrunk, unfilled, missed = set(), [], [], []
    for i in (2, 3, 4, 5, 6):
        c = json.loads(by[i]["r"]["task_fields_json"])
        have = {k for k, v in c["fields"].items() if (v.get("v") or "").strip()}
        shrunk += [{"turn": i, "lost": sorted(seen - have)}] if (seen - have) else []
        seen |= have
        for g in by[i]["in_gaps"]:
            filled = bool(env_field(by[i]["r"]["capability_call"], g))
            prev_c = json.loads(by[i - 1]["r"]["task_fields_json"])["fields"] if i > 2 else {}
            could = bool((prev_c.get(g) or {}).get("v"))
            if could and not filled:
                missed.append({"turn": i, "gap": g})
        for g in by[i]["out_gaps"]:
            prev_c = json.loads(by[i - 1]["r"]["task_fields_json"])["fields"] if i > 2 else {}
            if (prev_c.get(g) or {}).get("v"):
                unfilled.append({"turn": i, "gap": g})
    confirmed_keep = sorted(k for k in keep if k in seen)
    chk("F-03", "已确认字段全任务保留（载体单调不减）、成为缺口时必由载体补齐",
        not shrunk and not missed and not unfilled and len(confirmed_keep) == len(keep),
        {"carrier_never_shrank": not shrunk, "shrunk": shrunk,
         "gaps_the_carrier_could_fill_but_did_not": missed,
         "residual_gaps_carrier_could_have_filled": unfilled,
         "named_fields_confirmed_in_carrier": confirmed_keep,
         "per_turn_carried": {("T%d" % i): by[i]["r"]["carried_fields"] for i in (3, 4, 5, 6)}})

    # F-04 用户明确纠正：新值生效，旧值不再下行，并登记 STALE
    cc4, gt4, cap4, _ = real(4)
    pre = json.dumps({"task_key": TASK, "rev": 1,
                      "fields": {"content_origin_mode": {"v": "全部重新拍摄", "lvl": "E", "turn": 1}},
                      "asked": ["content_origin_mode"], "stale": []}, ensure_ascii=False)
    r4 = F.main(pre, TASK, cc4, gt4, cap4)
    c = json.loads(r4["task_fields_json"])
    chk("F-04", "用户明确纠正时新值生效、旧值不再下行、登记下游 STALE",
        c["fields"]["content_origin_mode"]["v"].startswith("使用门店已有素材剪辑")
        and c["fields"]["content_origin_mode"]["lvl"] == "A"
        and "全部重新拍摄" not in r4["capability_call"]
        and "content_origin_mode" in c["stale"],
        {"new": c["fields"]["content_origin_mode"], "stale": c["stale"],
         "old_still_downstream": "全部重新拍摄" in r4["capability_call"]})

    # F-05 新任务不继承
    cc5, gt5, cap5, _ = real(5)
    r5n = F.main(carrier_end, "NEW-TASK-0000", cc5, gt5, cap5)
    cn = json.loads(r5n["task_fields_json"])
    chk("F-05", "新内容任务不继承上一任务的 content_origin_mode",
        "content_origin_mode" in gapset(r5n["gaps_text"])
        and not env_field(r5n["capability_call"], "content_origin_mode")
        and cn["task_key"] == "NEW-TASK-0000" and cn["rev"] == 1,
        {"gaps": sorted(gapset(r5n["gaps_text"])), "carried": r5n["carried_fields"],
         "task_key": cn["task_key"]})

    # F-06 来源真空负例：合成器不造事实
    cc2, gt2, cap2, _ = real(2)
    stripped = re.sub(r"^`facts_registered`:.*$", "", cc2, flags=re.M)
    r6 = F.main("", TASK, stripped, "facts_registered", cap2)
    chk("F-06", "来源真空时仍精确停在 facts_registered，合成器不制造事实",
        gapset(r6["gaps_text"]) == {"facts_registered"}
        and not env_field(r6["capability_call"], "facts_registered")
        and r6["carried_fields"] == "",
        {"gaps": sorted(gapset(r6["gaps_text"])), "carried": r6["carried_fields"]})

    # F-07 抽取值与已确认值冲突时不静默采纳
    pre7 = json.dumps({"task_key": TASK, "rev": 1,
                       "fields": {"primary_goal": {"v": "锁定的主目标", "lvl": "A", "turn": 1}},
                       "asked": [], "stale": []}, ensure_ascii=False)
    cc3, gt3, cap3, _ = real(3)
    r7 = F.main(pre7, TASK, cc3, gt3, cap3)
    chk("F-07", "本轮抽取与已确认值冲突时不静默采纳，维持已确认值并登记",
        env_field(r7["capability_call"], "primary_goal") == "锁定的主目标"
        and "primary_goal" in (r7["held_fields"] or "")
        and json.loads(r7["task_fields_json"])["fields"]["primary_goal"]["v"] == "锁定的主目标",
        {"envelope": env_field(r7["capability_call"], "primary_goal"),
         "held": r7["held_fields"],
         "note": "A/B > E，不是同权威冲突，因此维持而非追问；新值不被静默采纳，登记在 held_fields"})

    # F-08 空 artifact 不覆盖最后一个成功上游（写回闸门未变，回放）
    keep_prev = P.main("", "CREATIVE_SCRIPT", "上一份成功产物", "CONTENT_BRIEF")
    write_new = P.main("新产物", "CREATIVE_SCRIPT", "上一份成功产物", "CONTENT_BRIEF")
    first = P.main("", "CONTENT_BRIEF", "", "")
    chk("F-08", "空 artifact 不覆盖最后一个成功上游产物；有真产出正常覆盖；首轮不造值",
        keep_prev["artifact_to_persist"] == "上一份成功产物"
        and keep_prev["persist_action"] == "KEEP_PREVIOUS"
        and write_new["artifact_to_persist"] == "新产物"
        and first["artifact_to_persist"] == "" and first["persist_action"] == "KEEP_PREVIOUS",
        {"keep": keep_prev, "write": write_new, "first": first})

    # F-09 首轮无历史字段时是恒等变换
    ident = []
    for i in (2, 3):
        cc, gt, cap, _ = real(i)
        r = F.main("", TASK, cc, gt, cap)
        ident.append({"turn": i, "envelope_identical": r["capability_call"] == cc,
                      "gaps_identical": gapset(r["gaps_text"]) == gapset(gt),
                      "carried": r["carried_fields"], "held": r["held_fields"]})
    chk("F-09", "载体为空时合成节点是恒等变换，不改变现有 C1/C2 充分输入",
        all(x["envelope_identical"] and x["gaps_identical"] and not x["carried"] and not x["held"]
            for x in ident), ident)

    # F-10 受保护面与未授权对象零漂移（对照 Phase C 冻结绑定）
    bind = json.load(io.open(os.path.join(UAPP, "stages", "S4_PHASE_C_BINDING_v1.0.json"),
                             encoding="utf-8"))
    drift = {}
    for k, v in PROTECTED.items():
        now = SC.psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                      "where a.id='%s';" % v).strip()
        if now != bind["protected_apps_graph_md5"][k]:
            drift[k] = {"frozen": bind["protected_apps_graph_md5"][k], "now": now}
    chk("F-10", "九个受保护应用零漂移（本次修改只动候选画布）", drift == {}, drift)

    # F-11 作用域隔离预检正负控制
    rc = subprocess.run([sys.executable, os.path.join(HERE, "S4_SCOPE_ISOLATION_PREFLIGHT_v1.0.py"),
                         "--selfcheck"], capture_output=True, text=True)
    chk("F-11", "作用域隔离预检正负控制均通过（无关第三方允许／触碰任务作用域拒绝）",
        rc.returncode == 0, rc.stdout.strip().splitlines()[-1] if rc.stdout else rc.stderr[:200])

    # ---- 结构检查：新图只多一个节点、两条连线、一个会话变量 ----
    graph, features, _ = B.build_graph()
    ids = sorted(n["id"] for n in graph["nodes"])
    gsha = hashlib.sha256(json.dumps(graph, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()
    struct = {"node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
              "has_uapp_fields": "uapp_fields" in ids, "graph_sha256_dry_run": gsha}
    print("\n结构（干跑构建，未写 Dify）：%s" % json.dumps(struct, ensure_ascii=False))

    doc = {"document": {"id": "S4_FIELD_CARRIER_VERIFICATION_v1.0",
                        "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
                        "authority": "规划侧裁决 TD-UAPP-20/21/22；second_repair_iteration = "
                                     "AUTHORIZED_ONCE_FOR_TD-UAPP-20_ONLY",
                        "model_calls": 0, "dify_writes": 0},
           "checks": RES, "dry_run_structure": struct,
           "replay": [{"turn": x["turn"], "capability": x["cap"], "in_gaps": x["in_gaps"],
                       "out_gaps": x["out_gaps"], "carried": x["r"]["carried_fields"],
                       "held": x["r"]["held_fields"],
                       "user_answered": x["r"]["user_answered_fields"],
                       "note": x["r"]["merge_note"]} for x in rp]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    bad = [r for r in RES if r["result"] != "PASS"]
    print("\n零模型调用验证 %d/%d 通过 -> %s" % (len(RES) - len(bad), len(RES), os.path.basename(OUT)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
