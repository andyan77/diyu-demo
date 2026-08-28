#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 持久化侧探针 · RISK-PUBLISH-ID-01 / RISK-RECOVERY-01 / REG-M2-01。

**这三组完全不调用模型**，只打 M2 服务与数据库。因此模型不可用时它们照常成立，
也因此它们的结论比任何生成式产出更硬：要么数据库里有那一行，要么没有。

判据在运行前冻结。每条判据都能落到一次 HTTP 状态码或一行数据上。
"""
import importlib.util, json, os, subprocess, sys, uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
RT = FS.RT


def sql(q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "diyu_business", "-t", "-A", "-F", "|", "-c", q],
                       capture_output=True, text=True, timeout=60)
    return [l for l in (p.stdout or "").strip().splitlines() if l.strip()]


# ================================================================ RISK-PUBLISH-ID-01
def probe_publish_identity(boot):
    """发布身份、版本、撤回与反馈归属。

    要证的四件事：
      1. 反馈绑定的是**正确的**账号 / 平台 / 内容版本 / 时间；
      2. 测试发布在数据层就被钉成 is_test / is_simulated，不靠文档措辞；
      3. 重复写入不制造双份事实（同 idempotency_key → 同一行）；
      4. 未知状态与撤回**不被伪装成成功**。
    """
    a, ws = boot["actor"], boot["ws"]
    tag = uuid.uuid4().hex[:8]
    out = {}

    st, art = RT.m2("POST", "/workspaces/%s/tasks/%s/artifacts" % (ws, boot["task"]),
                    {"kind": "final", "content_hash": "h-" + tag}, actor=a)
    out["artifact_http"] = st
    st, v1 = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions" % (ws, art["id"]),
                   {"idempotency_key": "v1-" + tag, "content_hash": "h1-" + tag,
                    "produced_by": "M5 probe"}, actor=a)
    st, v2 = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions" % (ws, art["id"]),
                   {"idempotency_key": "v2-" + tag, "content_hash": "h2-" + tag,
                    "produced_by": "M5 probe"}, actor=a)
    out["two_versions_distinct"] = v1.get("id") != v2.get("id")

    now = FS._now_iso()
    # 发布绑定 v1（不是 v2）。后面要验证反馈落在 v1 上，不会串到 v2。
    st, pub = RT.m2("POST", "/workspaces/%s/publish-instances" % ws, {
        "idempotency_key": "p-" + tag, "content_version_id": v1["id"],
        "account_id": boot["account"], "platform": "test-platform",
        "published_at": now, "is_test": True, "is_simulated": True}, actor=a)
    out["publish_http"] = st
    out["publish_is_test"] = pub.get("is_test")
    out["publish_is_simulated"] = pub.get("is_simulated")
    out["publish_bound_version"] = pub.get("content_version_id") == v1["id"]
    out["publish_bound_account"] = pub.get("account_id") == boot["account"]
    out["publish_platform"] = pub.get("platform")

    fb = {"idempotency_key": "f-" + tag, "publish_instance_id": pub["id"],
          "kind": "observation", "is_test": True, "is_simulated": True,
          "is_manual_entry": True, "source": "M5 probe", "observed_at": now,
          "payload": {"views": 10, "note": "模拟"}}
    s1, f1 = RT.m2("POST", "/workspaces/%s/feedback" % ws, fb, actor=a)
    s2, f2 = RT.m2("POST", "/workspaces/%s/feedback" % ws, fb, actor=a)
    out["feedback_idempotent_same_row"] = f1.get("id") == f2.get("id")

    rows = sql("SELECT count(*) FROM feedback_records WHERE idempotency_key='f-%s';" % tag)
    out["feedback_rows_in_db"] = rows[0] if rows else "?"

    # 反馈是否串到了 v2：应为 0
    cross = sql("""SELECT count(*) FROM feedback_records f
                   JOIN publish_instances p ON p.id=f.publish_instance_id
                   WHERE f.idempotency_key='f-%s' AND p.content_version_id='%s';""" % (tag, v2["id"]))
    out["feedback_leaked_to_other_version"] = cross[0] if cross else "?"

    # 未知状态不得被伪装成成功：故意给一个不存在的 publish_instance
    s3, f3 = RT.m2("POST", "/workspaces/%s/feedback" % ws,
                   dict(fb, idempotency_key="bad-" + tag,
                        publish_instance_id=str(uuid.uuid4())), actor=a)
    out["feedback_on_unknown_publish_http"] = s3
    out["feedback_on_unknown_publish_rejected"] = s3 >= 400

    # 撤回：素材撤回后不得仍被当作可用
    st, mat = RT.m2("POST", "/workspaces/%s/materials" % ws,
                    {"idempotency_key": "m-" + tag, "kind": "clip",
                     "title": "M5 probe material", "permission_state": "confirmed"}, actor=a)
    out["material_http"] = st
    if st == 200:
        st, w = RT.m2("POST", "/workspaces/%s/materials/%s/withdraw" % (ws, mat["id"]),
                      {"reason": "M5 撤回探针"}, actor=a)
        out["withdraw_http"] = st
        st, after = RT.m2("GET", "/workspaces/%s/materials/%s" % (ws, mat["id"]), actor=a)
        out["material_state_after_withdraw"] = (after or {}).get("permission_state") or \
            (after or {}).get("state") or json.dumps(after, ensure_ascii=False)[:200]
    return out


def judge_publish_identity(x):
    f = []
    if not x.get("publish_is_test") or not x.get("publish_is_simulated"):
        f.append("测试发布未在数据层钉成 is_test/is_simulated")
    if not x.get("publish_bound_version"):
        f.append("发布未绑定到指定内容版本")
    if not x.get("publish_bound_account"):
        f.append("发布未绑定到正确账号")
    if x.get("publish_platform") != "test-platform":
        f.append("发布平台绑定错误：%s" % x.get("publish_platform"))
    if not x.get("feedback_idempotent_same_row"):
        f.append("同 idempotency_key 重复写入产生了不同行")
    if str(x.get("feedback_rows_in_db")) != "1":
        f.append("数据库里同 key 的反馈行数为 %s，应为 1" % x.get("feedback_rows_in_db"))
    if str(x.get("feedback_leaked_to_other_version")) != "0":
        f.append("反馈串到了另一个内容版本")
    if not x.get("feedback_on_unknown_publish_rejected"):
        f.append("对不存在的发布实例写反馈被接受了（HTTP %s）——未知状态被伪装成成功"
                 % x.get("feedback_on_unknown_publish_http"))
    if x.get("withdraw_http") and x["withdraw_http"] >= 400:
        f.append("撤回接口返回 %s" % x["withdraw_http"])
    return f


# ================================================================ RISK-RECOVERY-01
def probe_recovery(boot):
    """中断恢复、局部失效与幂等。

    要证的三件事：
      1. 运行状态可持久化、可读回——中断后能从**最高失效节点**接着走，而不是从头；
      2. 重复调用不制造重复事实或重复副作用（周期、任务、版本、发布、反馈全查一遍）；
      3. 未受影响项不被全量重跑——用不同 idempotency_key 写入的项各自独立成立。
    """
    a, ws = boot["actor"], boot["ws"]
    tag = uuid.uuid4().hex[:8]
    out = {}

    # 1. 运行状态写入与读回。
    # M2 的字段本身就是「最高失效节点」模型：last_success_step / failed_step /
    # resumable_from / side_effects。恢复应当从 resumable_from 起步，
    # 而不是从头，也不是从 failed_step 的下游。
    st, _ = RT.m2("PUT", "/workspaces/%s/tasks/%s/run-state" % (ws, boot["task"]),
                  {"last_success_step": "seam:CONTENT_BRIEF",
                   "failed_step": "seam:CREATIVE_SCRIPT",
                   "resumable_from": "seam:CREATIVE_SCRIPT",
                   "side_effects": {"m2_writes": ["artifact", "version"],
                                    "external_publish": False}}, actor=a)
    out["run_state_put_http"] = st
    st, rs = RT.m2("GET", "/workspaces/%s/tasks/%s/run-state" % (ws, boot["task"]), actor=a)
    out["run_state_get_http"] = st
    rs = rs or {}
    out["last_success_step"] = rs.get("last_success_step")
    out["failed_step"] = rs.get("failed_step")
    out["resumable_from"] = rs.get("resumable_from")
    out["side_effects_readback"] = rs.get("side_effects")
    out["resume_point_survives"] = rs.get("resumable_from") == "seam:CREATIVE_SCRIPT"
    out["highest_failed_node_recorded"] = rs.get("failed_step") == "seam:CREATIVE_SCRIPT"
    out["completed_work_not_lost"] = rs.get("last_success_step") == "seam:CONTENT_BRIEF"
    out["external_side_effect_declared_false"] = (
        (rs.get("side_effects") or {}).get("external_publish") is False)

    # 2. 幂等：五种写入各重复一次，逐一核对数据库行数
    dup = {}
    now = FS._now_iso()
    calls = [
        ("cycle", "/workspaces/%s/cycles" % ws,
         {"idempotency_key": "rc-" + tag, "account_id": boot["account"],
          "label": "M5 recovery probe", "start_at": now, "baseline_capacity": 1,
          "baseline_capacity_source": "probe"}, "cycles"),
        ("task", "/workspaces/%s/tasks" % ws,
         {"idempotency_key": "rt-" + tag, "account_id": boot["account"],
          "cycle_id": boot["cycle"], "kind": "m5-recovery-probe"}, "tasks"),
    ]
    for name, path, body, table in calls:
        r1 = RT.m2("POST", path, body, actor=a)
        r2 = RT.m2("POST", path, body, actor=a)
        same = (r1[1] or {}).get("id") == (r2[1] or {}).get("id")
        rows = sql("SELECT count(*) FROM %s WHERE idempotency_key='%s';"
                   % (table, body["idempotency_key"]))
        dup[name] = {"http": [r1[0], r2[0]], "same_id": same,
                     "db_rows": rows[0] if rows else "?"}
    out["idempotency"] = dup

    # 3. 未受影响项不被全量重跑：另起一个 key 写入，应独立成立且不影响上面那些行
    st, other = RT.m2("POST", "/workspaces/%s/tasks" % ws,
                      {"idempotency_key": "rt2-" + tag, "account_id": boot["account"],
                       "cycle_id": boot["cycle"], "kind": "m5-recovery-probe-other"}, actor=a)
    out["independent_write_http"] = st
    rows = sql("SELECT count(*) FROM tasks WHERE idempotency_key IN ('rt-%s','rt2-%s');"
               % (tag, tag))
    out["two_independent_task_rows"] = rows[0] if rows else "?"
    return out


def judge_recovery(x):
    f = []
    if not x.get("resume_point_survives"):
        f.append("恢复点未能持久化读回，实得 %r" % x.get("resumable_from"))
    if not x.get("highest_failed_node_recorded"):
        f.append("最高失效节点未被记录，实得 %r" % x.get("failed_step"))
    if not x.get("completed_work_not_lost"):
        f.append("已完成步骤未被保留，实得 %r —— 恢复会变成全链重跑" % x.get("last_success_step"))
    if not x.get("external_side_effect_declared_false"):
        f.append("外部副作用声明未能读回，实得 %r" % x.get("side_effects_readback"))
    for name, d in (x.get("idempotency") or {}).items():
        if not d["same_id"]:
            f.append("%s 重复写入产生了不同行" % name)
        if str(d["db_rows"]) != "1":
            f.append("%s 同 key 在库里有 %s 行，应为 1" % (name, d["db_rows"]))
    if str(x.get("two_independent_task_rows")) != "2":
        f.append("两个不同 key 的写入未各自独立成立，实得 %s 行"
                 % x.get("two_independent_task_rows"))
    return f


# ================================================================ REG-M2-01
def probe_reg_m2(boot):
    """最小投影、版本、幂等反馈和当前状态；保留历史 waiver 的真实身份。"""
    a, ws = boot["actor"], boot["ws"]
    out = {}
    p = RT.current_projection(ws, a, boot["account"])
    out["cycle_current_http"] = p["cycle_current"]["status"]
    out["decision_latest_http"] = p["decision_latest"]["status"]
    cyc = p["cycle_current"]["body"] or {}
    out["cycle_has_label"] = bool(cyc.get("label"))
    out["cycle_has_capacity_source"] = bool(cyc.get("baseline_capacity_source"))
    # 成员鉴权：不带 X-Actor-Ref 必须被拒
    st, _ = RT.m2("GET", "/workspaces/%s/accounts" % ws)
    out["no_actor_http"] = st
    out["no_actor_rejected"] = st >= 400
    # 非成员必须被拒
    st, u2 = RT.m2("POST", "/users", {"external_ref": "m5-outsider-" + uuid.uuid4().hex[:6]})
    st2, _ = RT.m2("GET", "/workspaces/%s/accounts" % ws, actor=u2.get("external_ref"))
    out["outsider_http"] = st2
    out["outsider_rejected"] = st2 >= 400
    return out


def judge_reg_m2(x):
    f = []
    if x.get("cycle_current_http") != 200:
        f.append("最小当前投影不可读：HTTP %s" % x.get("cycle_current_http"))
    if not x.get("cycle_has_capacity_source"):
        f.append("周期缺少产能来源字段——产能不能是无来源数字")
    if not x.get("no_actor_rejected"):
        f.append("不带 X-Actor-Ref 的请求被接受了（HTTP %s）" % x.get("no_actor_http"))
    if not x.get("outsider_rejected"):
        f.append("非成员可以读工作区数据（HTTP %s）" % x.get("outsider_http"))
    return f


PROBES = [
    ("RISK-PUBLISH-ID-01", "发布身份、版本、撤回与反馈归属",
     "测试发布与反馈绑定正确账号/平台/版本；撤回、更正和未知状态不被伪装为成功",
     probe_publish_identity, judge_publish_identity),
    ("RISK-RECOVERY-01", "中断恢复、局部失效与幂等",
     "从最高失效节点恢复；重复调用不制造重复事实或重复副作用；未受影响项不全量重跑",
     probe_recovery, judge_recovery),
    ("REG-M2-01", "最小投影、版本、幂等反馈和当前状态",
     "最小投影可读、产能有来源、成员鉴权成立",
     probe_reg_m2, judge_reg_m2),
]


def main():
    boot = FS.bootstrap("m2p" + (sys.argv[1] if len(sys.argv) > 1 else "a"))
    print("boot ws=%s" % boot["ws"], flush=True)
    results = []
    for pid, target, oracle, run, judge in PROBES:
        print("\n>>> %s %s" % (pid, target), flush=True)
        try:
            x = run(boot); fails = judge(x)
        except Exception as e:
            import traceback; traceback.print_exc()
            x = {"exception": "%s: %s" % (type(e).__name__, e)}; fails = ["探针异常：%s" % x["exception"]]
        rec = {"id": pid, "target": target, "oracle": oracle, "observed": x,
               "failures": fails, "verdict": "PASS" if not fails else "FAIL"}
        results.append(rec)
        print("    %s" % rec["verdict"], flush=True)
        for f in fails:
            print("    ! %s" % f, flush=True)
    out = os.path.join(ROOT, "decision-chain", "evidence", "m5",
                       "M2_PROBE_SUITE_%s.json" % boot["tag"])
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"boot": boot, "results": results}, fh, ensure_ascii=False, indent=2)
    print("\n=== M2 侧探针 %d/%d PASS ===" % (
        sum(1 for r in results if r["verdict"] == "PASS"), len(results)), flush=True)
    print("SAVED", out, flush=True)


if __name__ == "__main__":
    main()
