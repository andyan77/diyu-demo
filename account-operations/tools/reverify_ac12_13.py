#!/usr/bin/env python3
"""AC-12 / AC-13 / AC-09（适用范围半）对当前 M2 接口 main@a7b8101 的**定向复验**。

为什么是定向复验而不是重跑全部：A3 要求失效沿依赖下行，且不多算。
`ep13-a3-main-moved/A3_IMPACT_MAIN_MOVED.md` §3 已经把失效面逐字段算清——
只有四行差异 + AC-09 的一半。本脚本逐条证明这五项在 v1.1 下闭合，
其余不曾失效的证据不重跑、也不声称重跑过。

每一项都必须是**推导**：从运行中的 M2 抓到的真实响应出发，跑投影，断言结果。
断言失败就退出非零，不写证据文件。
"""
import hashlib, json, os, subprocess, sys

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
REPO = "/home/faye/diyu-demo"
sys.path.insert(0, os.path.join(WT, "account-operations/interfaces"))
import projection as P                                              # noqa: E402

CAP = json.load(open(os.path.join(WT, "account-operations/fixtures/m2_live_capture_v2.json"),
                     encoding="utf-8"))
NOW = CAP["capture_meta"]["frozen_now"]
OUT = os.path.join(WT, "account-operations/evidence/ep16-ac12-13-reverify")

checks = []


def check(cid, desc, fn):
    try:
        detail = fn()
        checks.append({"id": cid, "desc": desc, "result": "PASS", "detail": detail})
    except AssertionError as e:
        checks.append({"id": cid, "desc": desc, "result": "FAIL", "detail": str(e)})


# ---------------------------------------------------------------- §0 绑定实证
def c_binding():
    """运行中的 M2 到底是不是 a7b8101 —— 不问，量。"""
    same = {}
    for f in ("app/api/knowledge.py", "app/models/knowledge.py"):
        got = subprocess.run(["docker", "exec", "diyu-m2-app", "sha256sum", f"/srv/app/{f}"],
                             capture_output=True, text=True).stdout.split()[0]
        want = hashlib.sha256(subprocess.run(
            ["git", "-C", REPO, "show", f"a7b8101:business-persistence/{f}"],
            capture_output=True).stdout).hexdigest()
        assert got == want, f"{f} 容器内 {got[:16]}… ≠ a7b8101 {want[:16]}…"
        same[f] = got
    return same


# ------------------------------------------------- §1 A3 §3 表格四行，逐行闭合
# 用**读端点**返回的行，不用 create 响应：create 响应是 {fixture_name, response} 包装，
# 且不带 M2 计算出的 currently_usable / is_expired / excluded_reason。
ROWS = CAP["reads"]["market_observations"]


def proj_v11():
    return P._project_market_observations_v11(ROWS, None, NOW)


def c_source():
    """行 1：来源四分，不坍缩成单一 source。

    v1.1 把四项摊平在观察对象顶层（source / source_type / source_reference /
    source_provider），不是嵌在 source 里 —— 判据要的是"四项各自承载、不坍缩"，
    嵌不嵌套不影响这一点，因此按实际形状核对。
    """
    obs = proj_v11()
    need = {"source", "source_type", "source_reference", "source_provider"}
    for o in obs:
        assert need <= set(o.keys()), f"来源未四分，缺：{sorted(need - set(o.keys()))}"
    # 光"键在"不够：必须有至少一条把四项都填满，证明它们真的各自承载不同的值
    full = [o for o in obs if all(o[k] for k in need)]
    assert full, "没有任何一条同时带齐四项来源值 —— 无法证明四项各自承载"
    assert len({str(full[0][k]) for k in need}) == 4, "四项来源取到了相同的值"
    return {"observations": len(obs), "source_keys": sorted(need),
            "fully_populated_rows": len(full),
            "example": {k: full[0][k] for k in sorted(need)}}


def c_two_gates():
    """行 2：可用性与可发布性是两道**互不推导**的闸。

    只证明"两个字段都在"不够——那只是并列摆着。真正要证的是：
    第一道闸放行**不蕴含**第二道闸放行。"""
    obs = proj_v11()
    usable = [o for o in obs if o["usage_permission"]["currently_usable"]]
    assert usable, "没有任何一条当前可用，无法检验两闸独立性"
    leaked = [o for o in usable
              if o["external_publish_permission"]["availability"] != "UNKNOWN"]
    assert not leaked, (f"{len(leaked)} 条由第一道闸推出了第二道闸 —— "
                        "这正是执行侧越域创造产品语义")
    return {"currently_usable": len(usable),
            "external_publish_all_unknown": True,
            "why": "M2 未定义 usage_limits 结构，M3 不得代它发明"}


def c_fail_closed():
    """行 2 续：permission_status 未知时必须 fail-closed。"""
    unknown = [o for o in proj_v11() if o["usage_permission"]["status"] == "unknown"]
    assert unknown, "抓取里没有 unknown 权限的观察，无法检验 fail-closed"
    bad = [o for o in unknown if o["usable_for_inference"]]
    assert not bad, f"{len(bad)} 条 unknown 权限却可用于推理 —— fail-open"
    return {"unknown_rows": len(unknown), "all_excluded": True,
            "allow_list": list(P.M2_CURRENTLY_USABLE_PERMISSION_STATUSES)}


def c_scope():
    """行 3：适用范围四键齐备（账号 / 任务 / 期间起讫）。"""
    obs = proj_v11()
    need = {"account_id", "applicable_task_id",
            "applicable_period_start", "applicable_period_end"}
    for o in obs:
        got = set(o["applicable_scope"].keys())
        assert need <= got, f"适用范围缺键：{sorted(need - got)}"
    return {"scope_keys": sorted(obs[0]["applicable_scope"].keys())}


def c_digest():
    """行 4：证据身份进入投影。"""
    obs = proj_v11()
    for o in obs:
        assert "evidence_digest" in o, "投影未携带 evidence_digest"
    return {"present_on": len(obs)}


# ------------------------------------ §2 AC-09 的一半：适用范围能不能机械排除
def c_mechanical_exclusion():
    """要证的是「能被机械排除」，**不是**「M3 自己去排除」。

    第一版我把判据写成「M3 必须自己判定期间窗已过」，跑出来 FAIL。
    回头看，那条判据本身是错的：`applicable_period_*` 是这条观察**适用于哪段经营期间**，
    与它自身是否还有效（`valid_until`）是两件事；由 M3 把前者读成后者、
    再据以排除，恰好就是 V-2 要挡的那种越域发明。M2 自己在 `/current` 里做范围过滤，
    M3 的义务是把它的判断逐字带过来、并保证字段是机器可读的。

    **这条判据是在看到 FAIL 之后改的**，不是事先冻结的。按 A2，本项因此
    不能算「判据先于结果」的正式取证，见文件末 `criteria_provenance`。
    """
    obs = proj_v11()
    machine = {}
    for o in obs:
        sc = o["applicable_scope"]
        for k in ("account_id", "applicable_task_id",
                  "applicable_period_start", "applicable_period_end"):
            v = sc.get(k)
            assert v is None or isinstance(v, str), f"{k} 不是机器可读值：{type(v).__name__}"
        machine[o["observation_id"][:8]] = {
            "account_id": bool(sc.get("account_id")),
            "task_id": sc.get("applicable_task_id") is not None,
        }

    # M2 自己的范围排除，必须被逐字带过来
    q = P.project_market_observation_query(CAP["reads"]["market_observations__current_other_account"])
    assert q["available"] is False, "别的账号查询下 available 应为 False"
    assert q["gap_reason"] == "no_observation_in_scope", f"缺口理由丢失：{q['gap_reason']}"
    assert len(q["excluded"]) == 7, f"排除清单条数不符：{len(q['excluded'])}"
    assert all(e["reason"] == "scope_mismatch" for e in q["excluded"]), "排除理由被坍缩"

    # 三种"空"必须仍然可区分（消融：把 gap_reason 拿掉就区分不了）
    no_filter = P.project_market_observation_query(
        CAP["reads"]["market_observations__current_no_filter"])
    mismatch = P.project_market_observation_query(
        CAP["reads"]["market_observations__current_track_mismatch"])
    kinds = {
        "有可用的": (no_filter["available"], no_filter["gap_reason"]),
        "全被排除·别的账号": (q["available"], q["gap_reason"]),
        "全被排除·赛道不符": (mismatch["available"], mismatch["gap_reason"]),
    }
    assert len(set(kinds.values())) >= 2, f"三种空塌成一种：{kinds}"
    return {"scope_fields_machine_readable": machine,
            "m2_scope_exclusion_carried": {"available": q["available"],
                                           "gap_reason": q["gap_reason"],
                                           "excluded": len(q["excluded"])},
            "three_empties": {k: list(v) for k, v in kinds.items()},
            "not_asserted": "M3 不自行判定 applicable_period_* 是否已过 —— "
                            "那是 M2 的域；M3 只保证字段机器可读并带回 M2 的排除结论"}


# ------------------------------------------- §3 A3 不多算：v1.0 路径原样还在
def c_v10_intact():
    """v1.1 落地不得改变 v1.0 的行为 —— 否则就是让不受影响的证据失效。"""
    row = dict(ROWS[0]); row["permission_status"] = "unknown"
    v10 = P._project_market_observations([row], None, NOW)[0]
    assert P.SCHEMA_VERSION == "1.0" and P.M2_INTERFACE_BASELINE.endswith("df2c595")
    return {"v10_usable_for_inference_on_unknown": v10["usable_for_inference"],
            "note": "v1.0 的 fail-open 行为**原样保留**，未被追溯修改；"
                    "它属于 df2c595 绑定下的历史事实，改它才是篡改"}


# --------------------------------------------- §4 AC-13：写回面有没有被动到
def c_writeback_surface():
    """M2 在 a7b8101 零删除路由、新增两条读/权限路由。
    M3 的写回候选必须**不含**权限设置——设权限不是 M3 的域。"""
    dif = subprocess.run(["git", "-C", REPO, "diff", "df2c595", "a7b8101",
                          "--", "business-persistence/app/api/knowledge.py"],
                         capture_output=True, text=True).stdout
    removed = [l for l in dif.splitlines() if l.startswith("-") and "@router." in l]
    added = [l.strip("+ ") for l in dif.splitlines()
             if l.startswith("+") and "@router." in l]
    assert not removed, f"M2 删除了路由：{removed}"

    src = open(os.path.join(WT, "account-operations/interfaces/projection.py"),
               encoding="utf-8").read()
    i = src.index("def validate_writeback_candidate")
    body = src[i:i + 4000]
    assert "permission" not in body.lower(), "写回候选校验里出现 permission —— M3 越域"
    return {"routes_removed": 0, "routes_added": added,
            "writeback_touches_permission": False}


for cid, desc, fn in [
    ("V-0", "运行中的 M2 = main@a7b8101（容器内文件哈希 vs git show）", c_binding),
    ("V-1", "A3§3 行1 来源四分不坍缩", c_source),
    ("V-2", "A3§3 行2 可用性与可发布性是两道互不推导的闸", c_two_gates),
    ("V-3", "A3§3 行2 权限未知时 fail-closed（M2 允许清单逐字复制）", c_fail_closed),
    ("V-4", "A3§3 行3 适用范围四键齐备", c_scope),
    ("V-5", "A3§3 行4 证据身份进入投影", c_digest),
    ("V-6", "AC-09 半：适用范围机器可读 + M2 的范围排除逐字带回 + 三种空可区分", c_mechanical_exclusion),
    ("V-7", "A3 不多算：v1.0 路径行为原样保留", c_v10_intact),
    ("V-8", "AC-13：M2 写回面零删除，M3 写回候选不碰权限", c_writeback_surface),
]:
    check(cid, desc, fn)

failed = [c for c in checks if c["result"] == "FAIL"]
report = {
    "what": "AC-12 / AC-13 / AC-09（适用范围半）对 main@a7b8101 的定向复验",
    "why_directed": "A3 §3 已逐字段算清失效面（四行 + AC-09 一半）；"
                    "不曾失效的证据不重跑，也不声称重跑过",
    "m2_binding_reverified": "business-persistence@main:a7b8101",
    "checks": checks,
    "criteria_provenance": {
        "governing_criteria_frozen_before_everything": [
            "M3_ECC_REBIND_004_FROZEN_v1.0.md §4.2 五组必须保留、不得坍缩的语义（提交 70a121b）",
            "Founder 2026-08-26 CONTINUE_TASK 第 2 条（来源／当前可用性／对外发布权限／"
            "账号任务期间适用范围／证据身份）",
        ],
        "instrument_iterated_while_building": [
            {"check": "V-1", "changed": "读取形状（四项在顶层摊平，非嵌套）",
             "criterion_itself_changed": False,
             "note": "命题仍是「四分不坍缩」，且改后**加严**了：新增「必须有一条四项齐备且四值互不相同」"},
            {"check": "V-6", "changed": "命题由「M3 自行判定期间窗已过」改为"
                                        "「字段机器可读 + M2 的排除结论逐字带回 + 三种空可区分」",
             "criterion_itself_changed": True,
             "changed_after_seeing_result": True,
             "why": "原命题要求 M3 把 applicable_period_* 读成有效期并据以排除，"
                    "那正是 V-2 所禁止的越域发明；原命题与冻结判据 §4.2 相抵触",
             "a2_consequence": "本项为**探索级**，不作为「判据先于结果」的正式取证；"
                               "若需正式化，须先版本化冻结新命题再重跑"},
            {"check": "ROWS", "changed": "输入由 create 响应改为读端点返回行",
             "criterion_itself_changed": False,
             "note": "create 响应是 {fixture_name, response} 包装且不含 M2 计算字段，"
                     "喂错了对象，属执行侧脚本缺陷"},
        ],
    },
    "summary": {"total": len(checks), "pass": len(checks) - len(failed), "fail": len(failed)},
}
if failed:
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n{len(failed)} 项 FAIL —— 不写证据文件", file=sys.stderr)
    sys.exit(1)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "AC12_AC13_REVERIFY.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
for c in checks:
    print(f"  {c['id']}  {c['result']}  {c['desc']}")
print(f"\n{report['summary']}")
