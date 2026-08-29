#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 最后一轮新鲜留出运行器 · FINAL-P0-HOLDOUT-01 / 02。

**只在 V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.4_FINAL_P0.yaml 冻结之后运行。**

纪律与 v1.1_RB 相同，并且这一轮把隔离做得更严：
  - **先跑、后读判据。** 本文件只把留出原文送进系统、把产出原样存下来，不做任何判定。
  - **输出带标签、只增不覆盖。** 无标签输出覆盖正式证据这件事真发生过一次。
  - **环境预置全部由 custodian 的 ENV_SETUP_FINAL_P0.json 驱动**，
    运行器里不硬编码任何场景事实。上一轮 RB 运行器把素材名、artifact 标签写死在代码里，
    等于施工侧看过场景；这一轮改成机械消费规格文件，施工侧不打印其内容。
  - **路由公开可审计**，写在 ROUTE 里并附理由，不藏在代码路径中。

两份留出的运行纪律按保管清单 v1.2：
  01  三轮，**同一次会话**（M3 无状态，会话由 user_request 显式承载）。
      轮与轮之间运行器**不替用户在 M2 里执行任何动作**——该不该撤回、该不该标失效，
      是被测系统的判断，运行器替他做了就把考题做掉了。
  02  两个变体，**各用一个全新独立会话，各只发一次**，各自独立 bootstrap。
      按规格 needs_m2_setup=false：不预置任何历史行。预置会给系统提供可据以自选的
      历史上下文，正好污染这份留出要测的东西。
"""
import hashlib, importlib.util, json, os, re, sys
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CUSTODY = os.path.join(ROOT, "decision-chain", "fixtures",
                       "V1_M5_HOLDOUT_CUSTODY_MANIFEST_v1.2_FINAL_P0.yaml")
CANDIDATE = os.path.join(ROOT, "decision-chain", "docs",
                         "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.4_FINAL_P0.yaml")
ENV_SPEC = "/home/faye/diyu-demo-holdout-custody/m5-final-p0/ENV_SETUP_FINAL_P0.json"
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5-final-p0")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
RB = _load("rb", os.path.join(ROOT, "decision-chain", "workflows",
                              "DIYU_M5_HOLDOUT_RUNNER_v1.1_RB.py"))
RT = FS.RT
DE = _load("de", os.path.join(ROOT, "decision-chain", "workflows",
                              "DIYU_M5_DIRECT_ENTRY_SUITE_v1.0.py"))

# 路由与理由：由保管清单公开的 scope 标签推出，不需要读正文。
ROUTE = {
    "FINAL-P0-HOLDOUT-01": {
        "caps": [],
        "why": "scope=撤回影响面与副作用真实性。全是撤回、影响面、记账与写入真实性的问题，"
               "没有一轮要求产出内容成品；按「不为进入某组件暗中补跑前置组件」，"
               "只走 M3 运营判断，不进内容生产。"},
    "FINAL-P0-HOLDOUT-02": {
        "caps": ["CONTENT_BRIEF"],
        "why": "scope=缺关键输入时的停口与自选替代。这是单条内容契约编译请求，进 Content Brief；"
               "要测的正是「缺关键输入时链路该不该停」，所以必须让链路有机会往下走，"
               "由被测系统自己决定停不停，运行器不预先拦截。"},
}

# 冻结清单的数据政策优先于规格：发布与反馈一律 is_test / is_simulated 为真。
IS_TEST = True
IS_SIMULATED = True


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def verify_custody():
    cm = yaml.safe_load(open(CUSTODY, encoding="utf-8"))
    rows = []
    for h in cm["holdouts"]:
        got = sha256_file(h["body_path"])
        rows.append({"id": h["id"], "expected": h["body_sha256"], "observed": got,
                     "match": got == h["body_sha256"]})
    got = sha256_file(cm["sealed_oracles_path"])
    rows.append({"id": "SEALED_ORACLES_FINAL_P0_v1.0.md",
                 "expected": cm["sealed_oracles_sha256"], "observed": got,
                 "match": got == cm["sealed_oracles_sha256"]})
    for r in rows:
        print("  %-30s %s" % (r["id"], "哈希一致" if r["match"] else "**哈希不一致，中止**"), flush=True)
    if not all(r["match"] for r in rows):
        raise SystemExit("保管哈希不一致：判据被污染，本轮不产生正式 PASS")
    return cm, rows


def split_turns(text):
    parts = re.split(r"^第\s*(\d+)\s*轮\s*$", text, flags=re.MULTILINE)
    return [(int(parts[i]), parts[i + 1].strip().strip("-").strip())
            for i in range(1, len(parts), 2)]


def bootstrap(tag, spec):
    """按 custodian 规格建环境。规格没写的表一律不写。"""
    st, user = RT.m2("POST", "/users", {"external_ref": "m5-%s" % tag})
    assert st == 200, ("user", st, user)
    a = user["external_ref"]
    st, ws = RT.m2("POST", "/workspaces", {"name": "ws-m5-%s" % tag, "kind": "personal",
                                           "owner_user_id": user["id"]}, actor=a)
    assert st == 200, ("ws", st, ws)
    W = ws["id"]
    st, subj = RT.m2("POST", "/workspaces/%s/subjects" % W, {"name": "苏禾", "kind": "person"}, actor=a)
    assert st == 200, ("subject", st, subj)
    st, acct = RT.m2("POST", "/workspaces/%s/accounts" % W,
                     {"platform": "weixin_channels", "handle": "suhe-channels"}, actor=a)
    assert st == 200, ("account", st, acct)
    boot = {"actor": a, "user": user, "ws": W, "account": acct["id"], "tag": tag}
    setup = {"spec_source": "custodian ENV_SETUP_FINAL_P0.json（只含环境事实）",
             "spec_sha256": sha256_file(ENV_SPEC),
             "workspace": W, "account": acct["id"], "subject": subj["id"],
             "needs_m2_setup": bool(spec.get("needs_m2_setup"))}
    if not spec.get("needs_m2_setup"):
        setup["preseeded"] = "无。规格 needs_m2_setup=false。"
        return boot, setup

    now = FS._now_iso()
    st, cyc = RT.m2("POST", "/workspaces/%s/cycles" % W, {
        "idempotency_key": "cycle-%s" % tag, "account_id": acct["id"], "label": "本周期",
        "start_at": now, "baseline_capacity": 3,
        "baseline_capacity_source": "fixture:序里集素材与资源夹具",
        "expected_publish_count": 3, "expected_publish_count_source": "fixture:同上"}, actor=a)
    assert st == 200, ("cycle", st, cyc)
    boot["cycle"] = cyc["id"]

    mats = {}
    for m in spec.get("materials") or []:
        st, r = RT.m2("POST", "/workspaces/%s/materials" % W, {
            "source": m["source"], "owner_ref": "苏禾",
            "analysis_authorized": bool(m.get("analysis_authorized")),
            "generation_authorized": bool(m.get("generation_authorized")),
            "publish_authorized": bool(m.get("publish_authorized")),
            "content_ref": m["ref"]}, actor=a)
        assert st == 200, ("material", m["ref"], st, r)
        mats[m["ref"]] = r["id"]

    tasks = {}
    for t in spec.get("tasks") or []:
        st, r = RT.m2("POST", "/workspaces/%s/tasks" % W, {
            "idempotency_key": "%s-%s" % (tag, t["ref"]), "account_id": acct["id"],
            "cycle_id": cyc["id"], "kind": "content-task"}, actor=a)
        assert st == 200, ("task", t["ref"], st, r)
        tasks[t["ref"]] = {"id": r["id"], "label": t["label"]}
    if tasks:
        boot["task"] = list(tasks.values())[0]["id"]
        boot["tasks"] = list(tasks.values())

    arts = {}
    for A in spec.get("artifacts") or []:
        tref = A.get("task_ref") or (list(tasks)[0] if len(tasks) == 1 else None)
        if tref is None:
            raise RuntimeError("artifact %s 没有 task_ref 且任务不唯一，规格不足" % A["ref"])
        st, art = RT.m2("POST", "/workspaces/%s/tasks/%s/artifacts" % (W, tasks[tref]["id"]),
                        {"kind": "final", "content_hash": "h-%s" % A["ref"]}, actor=a)
        assert st == 200, ("artifact", A["ref"], st, art)
        st, ver = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions" % (W, art["id"]), {
            "idempotency_key": "%s-v1" % A["ref"], "content_hash": "h-%s-v1" % A["ref"],
            "content_ref": A["label"], "produced_by": "FINAL-P0 环境预置",
            "material_ids": [mats[A["material_ref"]]] if A.get("material_ref") else []}, actor=a)
        assert st == 200, ("version", A["ref"], st, ver)
        promote = None
        if A.get("promote_to_version"):
            promote, _ = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions/%s/promote"
                               % (W, art["id"], ver["id"]), {}, actor=a)
        arts[A["ref"]] = {"artifact": art["id"], "version": ver["id"], "promote_http": promote,
                          "material_ref": A.get("material_ref"), "published_flag": A.get("published")}

    pubs = {}
    for P in spec.get("publish_instances") or []:
        st, pub = RT.m2("POST", "/workspaces/%s/publish-instances" % W, {
            "idempotency_key": "%s-%s-pub" % (tag, P["artifact_ref"]),
            "content_version_id": arts[P["artifact_ref"]]["version"], "account_id": acct["id"],
            "platform": "weixin_channels", "published_at": now,
            "is_test": IS_TEST, "is_simulated": IS_SIMULATED}, actor=a)
        assert st == 200, ("publish", st, pub)
        pubs[P["artifact_ref"]] = pub["id"]

    rss = {}
    for R in spec.get("run_states") or []:
        body = {k: R.get(k) for k in ("last_success_step", "failed_step", "resumable_from")}
        body["side_effects"] = R.get("side_effects") or {}
        st, _ = RT.m2("PUT", "/workspaces/%s/tasks/%s/run-state" % (W, tasks[R["task_ref"]]["id"]),
                      body, actor=a)
        assert st == 200, ("run-state", R["task_ref"], st)
        rss[R["task_ref"]] = body

    setup.update({"materials": mats, "artifacts": arts, "publish_instances": pubs,
                  "tasks": {k: v["id"] for k, v in tasks.items()}, "run_states": rss,
                  "feedback_records_preseeded": len(spec.get("feedback_records") or []),
                  "data_policy_override": "is_test / is_simulated 一律取 true（冻结清单 "
                                          "test_data_policy 优先于规格；custodian 不是数据政策权威）",
                  "runner_initiated_changes_between_turns": "无。轮与轮之间运行器不发起任何 M2 变更。"})
    return boot, setup


def run_h01(rt, text, refs, spec):
    boot, setup = bootstrap("fp01", spec)
    acct, _ = FS.projection_text(boot)
    rec = {"id": "FINAL-P0-HOLDOUT-01", "route": ROUTE["FINAL-P0-HOLDOUT-01"], "boot": boot,
           "m2_setup": setup, "account_context": acct,
           "refs_sha256": FS.refs_sha256(refs), "turns": []}
    prior = []
    for n, t in split_turns(text):
        ur = RB.compose_session(prior, n, t)
        m = rt.m3_operate(account_context=acct, user_request=ur, loaded_references=refs)
        j = (m["outputs"] or {}).get("operating_judgment") or ""
        rec["turns"].append({"turn": n, "user_request_chars": len(ur), "user_text": t,
                             "run_id": m["run_id"], "attempts": m.get("attempts"),
                             "gate_status": (m["outputs"] or {}).get("gate_status"), "judgment": j})
        print("    第 %d 轮 run=%s chars=%d" % (n, m["run_id"], len(j)), flush=True)
        prior.append((n, t, j))
    return rec


def run_h02(rt, text, refs, spec):
    facts = FS.registered_facts()
    rec = {"id": "FINAL-P0-HOLDOUT-02", "route": ROUTE["FINAL-P0-HOLDOUT-02"],
           "isolation": "每个变体独立 bootstrap 独立 M2 工作区；变体之间零上下文共享",
           "refs_sha256": FS.refs_sha256(refs), "variants": []}
    for label, body in RB.split_variants(text):
        boot, vsetup = bootstrap("fp02" + label.lower(), spec)
        t0 = DE.db_now()
        acct, _ = FS.projection_text(boot)
        m = rt.m3_operate(account_context=acct, user_request=body, loaded_references=refs)
        j = (m["outputs"] or {}).get("operating_judgment") or ""
        v = {"variant": label, "user_text": body, "boot": boot, "m2_setup": vsetup,
             "account_context": acct, "m3_run_id": m["run_id"],
             "m3_gate_status": (m["outputs"] or {}).get("gate_status"), "m3_judgment": j}
        h = rt.hop("CONTENT_BRIEF", m3_judgment=j, registered_facts=facts,
                   account_context=acct, user_request=body)
        ho = h["outputs"] or {}
        v.update({"hop_run_id": h["run_id"], "hop_gaps": ho.get("extraction_gaps_text"),
                  "hop_source_map": ho.get("source_map_json"),
                  "capability_call": ho.get("capability_call")})
        if (ho.get("capability_call") or "").strip():
            r = rt.seam("CONTENT_BRIEF", capability_call=ho["capability_call"],
                        professional_input=ho.get("professional_input") or "")
            v.update({"seam_run_id": r["run_id"],
                      "business_delivery_outcome": r["business_delivery_outcome"],
                      "delivered": RT.delivered(r), "component_return": RT.is_component_return(r),
                      "user_delivery": r.get("user_delivery"), "artifact": r.get("artifact"),
                      "returns_json": (r.get("outputs") or {}).get("returns_json")})
            v["capability_side"] = DE.capability_run_outputs("CONTENT_BRIEF", t0)
        else:
            v["note"] = "适配器未产出 capability_call，未进入能力侧"
        print("    变体 %s  m3=%s  outcome=%s" % (label, m["run_id"],
                                                v.get("business_delivery_outcome")), flush=True)
        rec["variants"].append(v)
    return rec


def main():
    cand = yaml.safe_load(open(CANDIDATE, encoding="utf-8"))
    assert cand["status"] == "FROZEN", "候选清单未冻结"
    cm, custody_rows = verify_custody()
    spec_all = json.load(open(ENV_SPEC, encoding="utf-8"))
    refs = FS.m3_loaded_references()
    bodies = {h["id"]: h["body_path"] for h in cm["holdouts"]}

    only = set((os.environ.get("FP_HOLDOUT_ONLY") or "").split(",")) - {""}
    tag = os.environ.get("FP_HOLDOUT_TAG") or "formal"
    rt = RT.Runtime()

    out = {"candidate_commit": cand["git"]["candidate_commit"],
           "candidate_manifest": os.path.basename(CANDIDATE),
           "bind": RT.BIND_NAME, "seam_app": RT.SEAM_APP, "m3_app": RT.M3_APP,
           "env_spec_sha256": sha256_file(ENV_SPEC),
           "custody_verification": custody_rows,
           "execution_order": "先跑、后读判据。本文件不做任何判定。",
           "results": []}

    for hid, fn in (("FINAL-P0-HOLDOUT-01", run_h01), ("FINAL-P0-HOLDOUT-02", run_h02)):
        if only and hid not in only:
            continue
        text = open(bodies[hid], encoding="utf-8").read().strip()
        print(">>> %s（%s）" % (hid, ROUTE[hid]["why"]), flush=True)
        rec = fn(rt, text, refs, spec_all[hid])
        rec["body_sha256"] = sha256_file(bodies[hid])
        out["results"].append(rec)

    os.makedirs(EV, exist_ok=True)
    p = os.path.join(EV, "HOLDOUT_FINAL_P0_RUNS_%s.json" % tag)
    if os.path.exists(p):
        raise SystemExit("证据文件已存在，拒绝覆盖：%s" % p)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n产出已原样存下，**本文件不做任何判定**。SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
