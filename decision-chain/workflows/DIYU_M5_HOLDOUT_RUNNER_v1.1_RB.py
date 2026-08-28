#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 AC-07 Rebase 新鲜留出运行器 · HOLDOUT-M5-RB-01 / RB-02。

**只在 V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.1_AC07_REBASE.yaml 冻结之后运行。**

和 v1.0 同一条纪律，且这次写死成代码：
  - **先跑、后读判据。** 本文件只把留出原文送进系统、把产出原样存下来，
    **不做任何判定**；判定在读过封存 oracle 之后单独进行。
  - **输出带标签、只增不覆盖。** 无标签输出覆盖正式证据这件事真发生过一次。
  - **路由公开可审计**，写在 ROUTE 里，不藏在代码路径中。

两份留出的运行纪律不同，按保管清单：
  RB-01  四轮，**同一次会话**。M3 是无状态工作流，所以「同一次会话」由运行器
         显式承担：user_request 里带轮次标记的完整往来（含前几轮系统回复原文），
         最后一段是本轮新话；account_context 只放 M2 投影，**不把系统自己说过的话
         混进去冒充 M2 事实**。
  RB-02  四个变体，**各用一个全新独立会话，各只发一次**。每个变体单独 bootstrap
         一个 M2 工作区，互不共享上下文。任何一段的上下文泄漏进另一段，
         按保管清单本份留出整体记 NOT_VERIFIED。
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CUSTODY_MANIFEST = os.path.join(ROOT, "decision-chain", "fixtures",
                                "V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.1_RB.yaml")
CANDIDATE = os.path.join(ROOT, "decision-chain", "docs",
                         "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.2_AC07_REBASE.yaml")
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5-rb")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
RT = FS.RT
# 复用短入口套件里已经写死的能力侧读法与库时钟，不另造第二套观测。
DE = _load("de", os.path.join(ROOT, "decision-chain", "workflows",
                              "DIYU_M5_DIRECT_ENTRY_SUITE_v1.0.py"))

# 路由与理由。写在这里，可审计。
ROUTE = {
    "HOLDOUT-M5-RB-01": {
        "caps": [],
        "why": "四轮全是恢复、影响面、素材授权与记账问题，没有一轮要求产出内容成品；"
               "按「不为进入某组件暗中补跑前置组件」，只走 M3 运营判断，不进内容生产。",
    },
    "HOLDOUT-M5-RB-02": {
        "caps": ["CONTENT_BRIEF"],
        "why": "四个变体都是「这周出一条、片子还没拍、要不要加承接引导」，"
               "是单条内容契约编译，进 Content Brief；四段各走完全相同的路径，"
               "差别只在输入的书写形式。",
    },
}


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def verify_custody():
    """解封当刻现场复算。任一不一致即中止，并按判据被污染登记。"""
    import yaml
    cm = yaml.safe_load(open(CUSTODY_MANIFEST, encoding="utf-8"))
    rows, ok = [], True
    for h in cm["holdouts"]:
        got = sha256_file(h["body_path"])
        same = got == h["body_sha256"]
        ok = ok and same
        rows.append({"id": h["id"], "path": h["body_path"], "expected": h["body_sha256"],
                     "observed": got, "match": same})
    got = sha256_file(cm["sealed_oracles_path"])
    same = got == cm["sealed_oracles_sha256"]
    ok = ok and same
    rows.append({"id": "SEALED_ORACLES_RB_v1.0.md", "path": cm["sealed_oracles_path"],
                 "expected": cm["sealed_oracles_sha256"], "observed": got, "match": same})
    return ok, rows, cm


def split_turns(text):
    """按「第 N 轮」切分。切不出恰好 4 轮就报错，不猜。"""
    parts = re.split(r"^第\s*(\d+)\s*轮\s*$", text, flags=re.MULTILINE)
    turns = []
    for i in range(1, len(parts), 2):
        turns.append((int(parts[i]), parts[i + 1].strip()))
    return turns


def split_variants(text):
    """按「变体 X」切分，忽略首部的运行说明。"""
    parts = re.split(r"^变体\s*([A-Za-z])\s*$", text, flags=re.MULTILINE)
    out = []
    for i in range(1, len(parts), 2):
        body = parts[i + 1].strip().strip("-").strip()
        out.append((parts[i], body))
    return out


def compose_session(prior, turn_no, turn_text):
    """把同一次会话的往来拼成本轮 user_request。轮次标记显式，不含任何判据提示。"""
    if not prior:
        return turn_text
    lines = ["（本轮是同一次会话的第 %d 轮。以下是此前的往来，最后一段是本轮用户新说的话。）" % turn_no, ""]
    for n, u, a in prior:
        lines.append("【第 %d 轮 · 用户】" % n)
        lines.append(u)
        lines.append("")
        lines.append("【第 %d 轮 · 你上一轮的回复】" % n)
        lines.append(a)
        lines.append("")
    lines.append("【第 %d 轮 · 用户】" % turn_no)
    lines.append(turn_text)
    return "\n".join(lines)


# ---------------------------------------------------------------- RB-01 环境预置
# 规格由上下文隔离的 custodian 给出（只给环境事实，未给任何期望行为或判据）。
# 一处**故意偏离**并如实记录：custodian 写 is_test=false / is_simulated=true，
# 但冻结清单 test_data_policy 要求发布与反馈一律 is_test=true 且 is_simulated=true。
# custodian 不是数据政策的权威，按冻结清单取 true/true。这两个标志不进 M3 投影，
# 不改变本留出考察的恢复与影响面语义。
IS_TEST = True
IS_SIMULATED = True


def setup_rb01():
    """按规格把「昨天」的真实状态摆进 M2。全部经服务端点写入，不直连数据库。"""
    tag = "rb01"
    st, user = RT.m2("POST", "/users", {"external_ref": "m5-%s" % tag})
    assert st == 200, ("user", st, user)
    a = user["external_ref"]
    st, ws = RT.m2("POST", "/workspaces", {"name": "ws-m5-%s" % tag, "kind": "personal",
                                           "owner_user_id": user["id"]})
    assert st == 200, ("ws", st, ws)
    W = ws["id"]
    st, subj = RT.m2("POST", "/workspaces/%s/subjects" % W, {"name": "苏禾", "kind": "person"}, actor=a)
    assert st == 200, ("subject", st, subj)
    st, acct = RT.m2("POST", "/workspaces/%s/accounts" % W,
                     {"platform": "weixin_channels", "handle": "suhe-channels"}, actor=a)
    assert st == 200, ("account", st, acct)
    now = FS._now_iso()
    st, cyc = RT.m2("POST", "/workspaces/%s/cycles" % W, {
        "idempotency_key": "cycle-%s" % tag, "account_id": acct["id"], "label": "本周周期",
        "start_at": now, "baseline_capacity": 3, "baseline_capacity_source": "fixture:序里集素材与资源夹具",
        "expected_publish_count": 3, "expected_publish_count_source": "fixture:同上"}, actor=a)
    assert st == 200, ("cycle", st, cyc)

    mats = {}
    for key, src in (("MAT-C01-1", "苏禾内部试穿第一组（会议与接送连续场景）"),
                     ("MAT-C01-2", "苏禾内部试穿第二组（衬衫/马甲/轻外套三层叠穿）"),
                     ("MAT-C01-3", "苏禾内部试穿第三组（西装/阔腿裤/半裙场景切换）")):
        st, m = RT.m2("POST", "/workspaces/%s/materials" % W, {
            "source": src, "owner_ref": "苏禾", "analysis_authorized": True,
            "generation_authorized": True, "publish_authorized": True,
            "content_ref": key}, actor=a)
        assert st == 200, ("material", key, st, m)
        mats[key] = m["id"]

    tasks = {}
    for key, label, kind in (("TASK-A", "本周内容安排（昨天那次）", "weekly-content-plan"),
                             ("TASK-B", "上周内容的发布登记与首波反馈（昨天那次）", "publish-and-feedback"),
                             ("TASK-C", "本周第三条的推进（昨天那次）", "content-item-3")):
        st, t = RT.m2("POST", "/workspaces/%s/tasks" % W, {
            "idempotency_key": "%s-%s" % (tag, key), "account_id": acct["id"],
            "cycle_id": cyc["id"], "kind": kind}, actor=a)
        assert st == 200, ("task", key, st, t)
        tasks[key] = {"id": t["id"], "label": label}

    arts = {}
    for key, task_key, mat_key, label in (
            ("ART-W1", "TASK-B", "MAT-C01-3", "上周已发布内容「西装配裤子还是配半裙」"),
            ("ART-T1", "TASK-A", "MAT-C01-3", "本周第一条「西装一件多穿」"),
            ("ART-T2", "TASK-A", "MAT-C01-2", "本周第二条「马甲三层叠穿」"),
            ("ART-T3", "TASK-C", "MAT-C01-3", "本周第三条「半裙怎么挑」")):
        st, art = RT.m2("POST", "/workspaces/%s/tasks/%s/artifacts" % (W, tasks[task_key]["id"]),
                        {"kind": "final", "content_hash": "h-%s" % key}, actor=a)
        assert st == 200, ("artifact", key, st, art)
        st, ver = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions" % (W, art["id"]), {
            "idempotency_key": "%s-v1" % key, "content_hash": "h-%s-v1" % key,
            "content_ref": label, "produced_by": "RB-01 环境预置",
            "material_ids": [mats[mat_key]]}, actor=a)
        assert st == 200, ("version", key, st, ver)
        st, pr = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions/%s/promote"
                       % (W, art["id"], ver["id"]), {}, actor=a)
        arts[key] = {"artifact": art["id"], "version": ver["id"], "promote_http": st,
                     "material": mat_key, "label": label}

    st, pub = RT.m2("POST", "/workspaces/%s/publish-instances" % W, {
        "idempotency_key": "xuli-w1-publish-2026-08-21",
        "content_version_id": arts["ART-W1"]["version"], "account_id": acct["id"],
        "platform": "weixin_channels", "published_at": "2026-08-21T10:00:00Z",
        "is_test": IS_TEST, "is_simulated": IS_SIMULATED}, actor=a)
    assert st == 200, ("publish", st, pub)

    runstates = {
        "TASK-A": {"last_success_step": "three_directions_confirmed",
                   "failed_step": "shooting_plan_item2",
                   "resumable_from": "shooting_plan_item2",
                   "side_effects": {"failure_note": "连接中断"}},
        "TASK-B": {"last_success_step": "publish_instance_registered",
                   "failed_step": "feedback_record_write",
                   "resumable_from": "feedback_record_write",
                   "side_effects": {"publish_instance_id": pub["id"],
                                    "failure_note": "连接中断"}},
        "TASK-C": {"last_success_step": None, "failed_step": "material_authorization_check",
                   "resumable_from": None,
                   "side_effects": {"failure_note": "MAT-C01-3 使用授权未确认"}},
    }
    for key, rs in runstates.items():
        st, _ = RT.m2("PUT", "/workspaces/%s/tasks/%s/run-state" % (W, tasks[key]["id"]),
                      rs, actor=a)
        assert st == 200, ("run-state", key, st)

    boot = {"actor": a, "user": user, "ws": W, "account": acct["id"], "cycle": cyc["id"],
            "task": tasks["TASK-A"]["id"], "tag": tag,
            "tasks": [tasks["TASK-A"], tasks["TASK-B"], tasks["TASK-C"]]}
    setup = {"spec_source": "custodian 环境预置规格（只含环境事实）",
             "deviation_from_spec": "is_test 取 true（规格写 false）：冻结清单 test_data_policy "
                                    "要求发布与反馈一律 is_test=true 且 is_simulated=true；"
                                    "custodian 不是数据政策权威。该标志不进 M3 投影。",
             "workspace": W, "account": acct["id"], "subject": subj["id"],
             "materials": mats, "artifacts": arts, "publish_instance": pub["id"],
             "publish_is_test": pub.get("is_test"), "publish_is_simulated": pub.get("is_simulated"),
             "tasks": tasks, "run_states": runstates,
             "feedback_records_preseeded": 0,
             "artifact_task_mapping_note": "规格未约束 artifact 挂哪个 task；"
                                           "按语义挂：ART-W1→TASK-B，ART-T1/T2→TASK-A，ART-T3→TASK-C",
             "runner_initiated_changes_between_turns": "无。四轮之间运行器不发起任何 M2 变更。"}
    return boot, setup

def run_rb01(rt, text, refs, setup_fn=None):
    """四轮同一次会话。每轮之间**不替用户在 M2 里执行任何动作**——
    该不该登记、该不该撤回，是被测系统的判断，运行器替他做了就把考题做掉了。"""
    boot, setup = setup_rb01()
    acct, proj = FS.projection_text(boot)
    rec = {"id": "HOLDOUT-M5-RB-01", "route": ROUTE["HOLDOUT-M5-RB-01"], "boot": boot,
           "m2_setup": setup, "account_context": acct,
           "refs_sha256": FS.refs_sha256(refs), "turns": []}
    prior = []
    for n, t in split_turns(text):
        ur = compose_session(prior, n, t)
        m = rt.m3_operate(account_context=acct, user_request=ur, loaded_references=refs)
        j = (m["outputs"] or {}).get("operating_judgment") or ""
        rec["turns"].append({"turn": n, "user_request_chars": len(ur), "user_text": t,
                             "run_id": m["run_id"], "attempts": m.get("attempts"),
                             "gate_status": (m["outputs"] or {}).get("gate_status"),
                             "judgment": j})
        print("    第 %d 轮 run=%s chars=%d" % (n, m["run_id"], len(j)), flush=True)
        prior.append((n, t, j))
    return rec


def setup_rb02_variant(label):
    """RB-02 每个变体一份**全新独立**环境。四份预置走同一段代码、参数只差 label，
    因此逐字节相同；四段之间唯一的差别是 user_request 本身。
    按规格：只预置 workspace + subject 苏禾 + account 苏禾·视频号 + 三条未撤回素材；
    不预置 cycle、artifact、content_version、publish_instance、feedback。"""
    tag = "rb02" + label.lower()
    st, user = RT.m2("POST", "/users", {"external_ref": "m5-%s" % tag})
    assert st == 200, ("user", st, user)
    a = user["external_ref"]
    st, ws = RT.m2("POST", "/workspaces", {"name": "ws-m5-%s" % tag, "kind": "personal",
                                           "owner_user_id": user["id"]})
    assert st == 200, ("ws", st, ws)
    W = ws["id"]
    st, subj = RT.m2("POST", "/workspaces/%s/subjects" % W, {"name": "苏禾", "kind": "person"}, actor=a)
    assert st == 200, ("subject", st, subj)
    st, acct = RT.m2("POST", "/workspaces/%s/accounts" % W,
                     {"platform": "weixin_channels", "handle": "suhe-channels"}, actor=a)
    assert st == 200, ("account", st, acct)
    mats = {}
    for key, src in (("MAT-C01-1", "苏禾内部试穿第一组（会议与接送连续场景）"),
                     ("MAT-C01-2", "苏禾内部试穿第二组（衬衫/马甲/轻外套三层叠穿）"),
                     ("MAT-C01-3", "苏禾内部试穿第三组（西装/阔腿裤/半裙场景切换）")):
        st, m = RT.m2("POST", "/workspaces/%s/materials" % W, {
            "source": src, "owner_ref": "苏禾", "analysis_authorized": True,
            "generation_authorized": True, "publish_authorized": True,
            "content_ref": key}, actor=a)
        assert st == 200, ("material", key, st, m)
        mats[key] = m["id"]
    boot = {"actor": a, "user": user, "ws": W, "account": acct["id"], "tag": tag}
    return boot, {"workspace": W, "account": acct["id"], "subject": subj["id"],
                  "materials": mats, "cycle": None, "artifacts": None,
                  "publish_instance": None, "feedback_records_preseeded": 0}


def run_rb02(rt, text, refs):
    """四个变体，各一个全新独立会话，各只发一次。"""
    facts = FS.registered_facts()
    rec = {"id": "HOLDOUT-M5-RB-02", "route": ROUTE["HOLDOUT-M5-RB-02"],
           "isolation": "每个变体独立 bootstrap 独立 M2 工作区；变体之间零上下文共享",
           "refs_sha256": FS.refs_sha256(refs), "variants": []}
    for label, body in split_variants(text):
        boot, vsetup = setup_rb02_variant(label)
        t0 = DE.db_now()
        acct, _ = FS.projection_text(boot)
        m = rt.m3_operate(account_context=acct, user_request=body, loaded_references=refs)
        j = (m["outputs"] or {}).get("operating_judgment") or ""
        v = {"variant": label, "user_text": body, "boot": boot, "m2_setup": vsetup,
             "account_context": acct,
             "m3_run_id": m["run_id"], "m3_gate_status": (m["outputs"] or {}).get("gate_status"),
             "m3_judgment": j}
        h = rt.hop("CONTENT_BRIEF", m3_judgment=j, registered_facts=facts,
                   account_context=acct, user_request=body)
        ho = h["outputs"] or {}
        v["hop_run_id"] = h["run_id"]
        v["hop_gaps"] = ho.get("extraction_gaps_text")
        v["hop_source_map"] = ho.get("source_map_json")
        v["capability_call"] = ho.get("capability_call")
        if (ho.get("capability_call") or "").strip():
            r = rt.seam("CONTENT_BRIEF", capability_call=ho["capability_call"],
                        professional_input=ho.get("professional_input") or "")
            v.update({"seam_run_id": r["run_id"],
                      "business_delivery_outcome": r["business_delivery_outcome"],
                      "delivered": RT.delivered(r),
                      "component_return": RT.is_component_return(r),
                      "user_delivery": r.get("user_delivery"),
                      "artifact": r.get("artifact"),
                      "returns_json": (r.get("outputs") or {}).get("returns_json")})
            # 解析器层的原始判定单独记：「解析器有没有一视同仁」和「散文写得像不像」
            # 是两件事，混在一起判会得出假结论。
            # 注意取值位置：status / missing / can_run 挂在**能力应用**自己的运行上，
            # 不在接缝返回里；从接缝读会全读到 null（这一条已经踩过三次）。
            v["capability_side"] = DE.capability_run_outputs("CONTENT_BRIEF", t0)
        else:
            v["note"] = "适配器未产出 capability_call，未进入能力侧"
        print("    变体 %s  m3=%s  outcome=%s" % (label, m["run_id"],
                                                v.get("business_delivery_outcome")), flush=True)
        rec["variants"].append(v)
    return rec


def main(setup_fn=None):
    import yaml
    cand = yaml.safe_load(open(CANDIDATE, encoding="utf-8"))
    if cand.get("status") != "FROZEN":
        print("拒绝运行：新候选清单尚未冻结，留出不得在冻结前使用。")
        return 2
    ok, rows, cm = verify_custody()
    for r in rows:
        print("  %-28s %s" % (r["id"], "哈希一致" if r["match"] else "**哈希不一致**"), flush=True)
    if not ok:
        print("中止：留出或封存判据的哈希与保管清单不一致，本轮按判据被污染登记，不产生正式 PASS。")
        return 2

    rt = RT.Runtime()
    refs = FS.m3_loaded_references()
    only = set((os.environ.get("RB_HOLDOUT_ONLY") or "").split(",")) - {""}
    out = {"candidate_commit": cand["git"]["candidate_commit"],
           "candidate_frozen_at": cand["frozen_at"],
           "bind": RT.BIND_NAME, "seam_app": RT.SEAM_APP, "m3_app": RT.M3_APP,
           "custody_verification": rows,
           "execution_order": "先跑、后读判据。本文件不做任何判定。",
           "results": []}
    bodies = {h["id"]: h["body_path"] for h in cm["holdouts"]}
    for hid in ("HOLDOUT-M5-RB-01", "HOLDOUT-M5-RB-02"):
        if only and hid not in only:
            continue
        text = open(bodies[hid], encoding="utf-8").read().strip()
        print(">>> %s（%s）" % (hid, ROUTE[hid]["why"]), flush=True)
        rec = run_rb01(rt, text, refs, setup_fn) if hid.endswith("01") \
            else run_rb02(rt, text, refs)
        rec["body_sha256"] = sha256_file(bodies[hid])
        out["results"].append(rec)

    tag = os.environ.get("RB_HOLDOUT_TAG") or "formal"
    p = os.path.join(EV, "HOLDOUT_RB_RUNS_%s.json" % tag)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n产出已原样存下，**本文件不做任何判定**。SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
