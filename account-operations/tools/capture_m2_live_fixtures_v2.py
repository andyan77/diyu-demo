"""从**运行中的 M2 实例**抓取真实响应，落成 M3 契约测试的实样夹具（v2）。

与 v1 的唯一区别：v1 抓取时那两个"市场观察权限语义"文件还只在 M2 任务分支上，
因此 v1 的 market_observations 一族对绑定基线 `main@df2c595` 记为 STALE。
**现在它们已经合入 `main@a7b8101`，而运行中的容器与该 commit 逐字节相同**——
实测：`/srv/app/app/api/knowledge.py` 与 `/srv/app/app/models/knowledge.py`
的 sha256 与 `git show a7b8101:business-persistence/...` 完全一致。
因此 v2 整份抓取的绑定基线就是 `main@a7b8101`，不再有分歧栏。

v2 另加三组**范围过滤**读取，用来实测 M2 的 `_scope_exclusion_reason`：
按账号问、按任务问、按一个不匹配的赛道问。没有这三组，
「这个账号没有相关观察」与「压根没按这个账号问」在夹具里就分不开。

**只读 + 只增**：只调用 M2 自己的公开 API 建立带 task_id 标识的独立演示数据
（与 M2 自带的 bootstrap_demo_workspace.py 完全同一种用法），
不碰 M2 源码、迁移，也不读写其他 workspace 的数据。全部 idempotency_key 带 task_id 前缀，可重复运行。

跑法（宿主上，M2 容器内有 httpx，宿主没有）：

    docker exec -i diyu-m2-app python3 - < account-operations/tools/capture_m2_live_fixtures_v2.py \
        > account-operations/fixtures/m2_live_capture_v2.json
"""

import json
import os
import sys

import httpx

API_BASE = os.environ.get("M2_API_BASE", "http://127.0.0.1:8000")
TASK_ID = "DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001"
SLUG = "m3-acco-001"

# 冻结的时间锚。所有夹具时间都相对它写死，让"过期/未过期/观察窗未结束"三种
# 状态不随真实时钟漂移——否则同一份夹具明天跑就换了含义。
NOW = "2026-08-26T00:00:00+00:00"


def _key(name):
    return "%s:%s" % (SLUG, name)


def _ok(response, what):
    """任何非 2xx 都必须立刻炸。

    第一版脚本没有这层检查，结果一条 `register_feedback` 被 M2 以 422 拒绝，
    错误体被 `.json()` 原样收进夹具，看上去和一条成功创建的记录一样是"抓到的真实
    响应"。**静默失败伪装成证据**是取证脚本最危险的失效模式，因为它不报错。
    """

    if response.status_code // 100 != 2:
        raise SystemExit(
            "捕获中止：%s 返回 %s —— %s" % (what, response.status_code, response.text[:400])
        )
    return response.json()


def _expect_rejected(response, what, expected_status):
    """刻意的负例：M2 **必须**拒绝的输入。被接受了才是问题。"""

    if response.status_code != expected_status:
        raise SystemExit(
            "捕获中止：%s 本应被拒(%s)，实际 %s —— %s"
            % (what, expected_status, response.status_code, response.text[:400])
        )
    return {"status_code": response.status_code, "body": response.json()}


def main():
    captured = {
        "capture_meta": {
            "task_id": TASK_ID,
            "api_base": API_BASE,
            "frozen_now": NOW,
            "note": "真实 M2 实例响应，未经任何手工编辑",
            "bound_baseline": "business-persistence@main:a7b8101",
            "baseline_equivalence_claim": {
                "actual_build": "diyu-m2-app（运行中）",
                "verified_files": ["app/api/knowledge.py", "app/models/knowledge.py"],
                "method": ("docker exec sha256sum /srv/app/<f> 对 "
                           "git show a7b8101:business-persistence/<f> | sha256sum"),
                "result": "两个文件逐字节相同 ⇒ 本次抓取整份绑定 main@a7b8101，无分歧栏",
                "note": ("v1 抓取时这两个文件只在 M2 任务分支上，因此 v1 的 market_observations "
                         "一族对 main@df2c595 记 STALE。该 STALE 现在由 v2 定向复验解除，"
                         "**v1 的抓取文件不删不改**，作为历史记录保留。"),
            },
        }
    }

    with httpx.Client(base_url=API_BASE, timeout=20.0) as c:
        captured["healthz"] = _ok(c.get("/healthz"), "healthz")

        user = _ok(
            c.post(
                "/users",
                json={"external_ref": "%s-founder" % SLUG, "display_name": "M3 契约取证账号"},
            ),
            "create user",
        )
        actor = user["external_ref"]
        H = {"X-Actor-Ref": actor}

        ws = _ok(
            c.post(
                "/workspaces",
                json={"name": "M3 契约取证 workspace", "kind": "personal", "owner_user_id": user["id"]},
            ),
            "create workspace",
        )
        wid = ws["id"]
        captured["user"] = user
        captured["workspace"] = ws

        # 两个账号：一个三类产能齐全，一个 actual_capacity 真的为 null。
        # 后者是 M3-AC-12 反证探针的真实来源——"M2 给了 null"这件事必须从真实
        # 响应里长出来，不能靠我们自己填一个 None 进去。
        acc_full = _ok(
            c.post(
                "/workspaces/%s/accounts" % wid,
                json={"platform": "douyin", "handle": "%s-full" % SLUG},
                headers=H,
            ),
            "create account(full)",
        )
        acc_sparse = _ok(
            c.post(
                "/workspaces/%s/accounts" % wid,
                json={"platform": "douyin", "handle": "%s-sparse" % SLUG},
                headers=H,
            ),
            "create account(sparse)",
        )
        captured["account_full"] = acc_full
        captured["account_sparse"] = acc_sparse

        captured["cycle_full_create_response"] = _ok(
            c.post(
                "/workspaces/%s/cycles" % wid,
                json={
                    "idempotency_key": _key("cycle-full"),
                    "account_id": acc_full["id"],
                    "label": "2026-08 周期（三类产能齐全）",
                    "start_at": "2026-08-01T00:00:00+00:00",
                    "baseline_capacity": 10,
                    "baseline_capacity_source": "团队自述",
                    "actual_capacity": 2,
                    "actual_capacity_source": "本周排班",
                    "expected_publish_count": 21,
                    "expected_publish_count_source": "用户本轮要求",
                },
                headers=H,
            ),
            "create cycle(full)",
        )
        cycle_full = captured["cycle_full_create_response"]
        # 刻意只给期望值，不给 baseline / actual：让 M2 自己产出 null。
        captured["cycle_sparse_create_response"] = _ok(
            c.post(
                "/workspaces/%s/cycles" % wid,
                json={
                    "idempotency_key": _key("cycle-sparse"),
                    "account_id": acc_sparse["id"],
                    "label": "2026-08 周期（产能未知）",
                    "start_at": "2026-08-01T00:00:00+00:00",
                    "expected_publish_count": 21,
                    "expected_publish_count_source": "用户本轮要求",
                },
                headers=H,
            ),
            "create cycle(sparse)",
        )

        captured["campaign_override_create_response"] = _ok(
            c.post(
                "/workspaces/%s/campaign-overrides" % wid,
                json={
                    "account_id": acc_full["id"],
                    "cycle_id": cycle_full["id"],
                    "name": "秋上新冲刺",
                    "scope_start": "2026-08-20T00:00:00+00:00",
                    "scope_end": "2026-08-31T00:00:00+00:00",
                    "targeted_positions": ["slot-2", "slot-5"],
                    "rationale": "新品到货窗口",
                },
                headers=H,
            ),
            "create campaign override",
        )

        observations = []
        for spec in (
            {
                "name": "obs-current",
                "source": "平台榜单",
                "applicable_track": "女装",
                "layer": "analysis",
                "collected_at": "2026-08-20T00:00:00+00:00",
                "valid_until": "2026-09-30T00:00:00+00:00",
                "mechanism_summary": "通勤场景内容集中度上升",
                "scope_ref": {"region": "华东"},
            },
            {
                "name": "obs-stale",
                "source": "旧报告",
                "applicable_track": "女装",
                "layer": "raw",
                "collected_at": "2026-03-01T00:00:00+00:00",
                "valid_until": "2026-05-01T00:00:00+00:00",
                "mechanism_summary": "春季通勤",
                "scope_ref": {},
            },
            {
                "name": "obs-other-track",
                "source": "平台榜单",
                "applicable_track": "母婴",
                "layer": "raw",
                "collected_at": "2026-08-20T00:00:00+00:00",
                "valid_until": None,
                "mechanism_summary": "与本账号无关",
                "scope_ref": {},
            },
            # ---- v2 新增：把五组语义各自逼出一条真实响应 ----
            # v1 建的三条全是 permission_status=unknown、无 usage_limits、无 evidence_digest、
            # 无期间窗，因此 v1 的夹具**证明不了**新语义有没有被投影正确承载——
            # 用它去测 v1.1 等于什么都没测。
            {
                "name": "obs-allowed-full-provenance",
                "source": "第三方行业报告",
                "source_type": "industry_report",
                "source_reference": "https://example.invalid/report/2026-q3",
                "source_provider": "某咨询机构",
                "applicable_track": "女装",
                "layer": "analysis",
                "collected_at": "2026-08-25T00:00:00+00:00",
                "valid_until": "2026-12-31T00:00:00+00:00",
                "mechanism_summary": "通勤品类搜索词结构变化",
                "scope_ref": {"region": "华东"},
                "permission_status": "allowed",
                "evidence_digest": "sha256:0000demo0000allowed",
            },
            {
                "name": "obs-restricted-with-limits",
                "source": "合作方后台数据",
                "source_type": "partner_backend",
                "source_reference": "partner://dashboard/2026-08",
                "source_provider": "合作门店",
                "applicable_track": "女装",
                "layer": "raw",
                "collected_at": "2026-08-26T00:00:00+00:00",
                "valid_until": "2026-10-31T00:00:00+00:00",
                "mechanism_summary": "门店试穿转化",
                "scope_ref": {},
                "permission_status": "restricted",
                "usage_limits": {"internal_only": True, "note": "仅供内部判断，禁止对外引用"},
                "evidence_digest": "sha256:0000demo0000restricted",
            },
            {
                "name": "obs-denied",
                "source": "来源不明的截图",
                "source_type": "screenshot",
                "applicable_track": "女装",
                "layer": "raw",
                "collected_at": "2026-08-26T00:00:00+00:00",
                "valid_until": None,
                "mechanism_summary": "无法确认出处",
                "scope_ref": {},
                "permission_status": "denied",
            },
            {
                "name": "obs-period-window",
                "source": "期间限定活动数据",
                "source_type": "campaign_report",
                "applicable_track": "女装",
                "layer": "analysis",
                "collected_at": "2026-08-01T00:00:00+00:00",
                "valid_until": None,
                "mechanism_summary": "只在活动期内适用",
                "scope_ref": {},
                "permission_status": "allowed",
                "applicable_period_start": "2026-08-01T00:00:00+00:00",
                "applicable_period_end": "2026-08-15T00:00:00+00:00",
                "evidence_digest": "sha256:0000demo0000period",
            },
        ):
            body = dict(spec)
            name = body.pop("name")
            body["idempotency_key"] = _key(name)
            body["platform"] = "douyin"
            body["account_id"] = acc_full["id"]
            observations.append(
                {
                    "fixture_name": name,
                    "response": _ok(
                        c.post("/workspaces/%s/market-observations" % wid, json=body, headers=H),
                        "create observation %s" % name,
                    ),
                }
            )
        captured["market_observation_create_responses"] = observations

        # 反馈必须挂在真实 publish_instance / content_version 上，所以要走完
        # task → artifact → version → publish 这条真实链路。
        task = _ok(
            c.post(
                "/workspaces/%s/tasks" % wid,
                json={
                    "idempotency_key": _key("task"),
                    "account_id": acc_full["id"],
                    "cycle_id": cycle_full["id"],
                    "kind": "content_task",
                },
                headers=H,
            ),
            "create task",
        )
        artifact = _ok(
            c.post(
                "/workspaces/%s/tasks/%s/artifacts" % (wid, task["id"]),
                json={"kind": "content", "content_hash": "sha256:%s" % ("a" * 8)},
                headers=H,
            ),
            "create artifact",
        )
        version = _ok(
            c.post(
                "/workspaces/%s/artifacts/%s/versions" % (wid, artifact["id"]),
                json={
                    "idempotency_key": _key("version-1"),
                    "content_hash": "sha256:%s" % ("b" * 8),
                    "produced_by": "m3-contract-capture",
                },
                headers=H,
            ),
            "create content version",
        )
        publish = _ok(
            c.post(
                "/workspaces/%s/publish-instances" % wid,
                json={
                    "idempotency_key": _key("publish-1"),
                    "content_version_id": version["id"],
                    "account_id": acc_full["id"],
                    "platform": "douyin",
                    "published_at": "2026-08-21T00:00:00+00:00",
                    "is_test": False,
                    "is_simulated": False,
                },
                headers=H,
            ),
            "register publish instance",
        )
        captured["task"] = task
        captured["artifact"] = artifact
        captured["content_version"] = version
        captured["publish_instance"] = publish

        feedbacks = []
        # ① 真实发布观察，挂 publish_instance，观察窗已结束
        feedbacks.append(
            _ok(
                c.post(
                    "/workspaces/%s/feedback" % wid,
                    json={
                        "idempotency_key": _key("fb-real"),
                        "publish_instance_id": publish["id"],
                        "kind": "observation",
                        "is_test": False,
                        "is_simulated": False,
                        "is_manual_entry": False,
                        "is_pre_publish_review": False,
                        "source": "平台后台",
                        "observed_at": "2026-08-22T00:00:00+00:00",
                        "window_start": "2026-08-21T00:00:00+00:00",
                        "window_end": "2026-08-24T00:00:00+00:00",
                        "goal_at_the_time": "吸粉",
                        "payload": {"views": 12000},
                    },
                    headers=H,
                ),
                "register feedback(real)",
            )
        )
        # ② 发布前人工评审：M2 强制它挂 content_version 而**不是** publish_instance。
        #    `is_pre_publish_review` 必须与 content_version_id 同真同假。
        feedbacks.append(
            _ok(
                c.post(
                    "/workspaces/%s/feedback" % wid,
                    json={
                        "idempotency_key": _key("fb-prepublish"),
                        "content_version_id": version["id"],
                        "kind": "observation",
                        "is_test": True,
                        "is_simulated": True,
                        "is_manual_entry": True,
                        "is_pre_publish_review": True,
                        "source": "工程夹具",
                        "observed_at": "2026-08-25T00:00:00+00:00",
                        "window_end": "2026-09-30T00:00:00+00:00",
                        "goal_at_the_time": "吸粉",
                        "payload": {"note": "模拟"},
                    },
                    headers=H,
                ),
                "register feedback(pre-publish review)",
            )
        )
        captured["feedback_create_responses"] = feedbacks

        # 冲突输入负例（真实响应，不是我们编的错误码）：
        # 发布前评审若挂到 publish_instance 上，M2 必须拒绝——否则"这条证据来自
        # 真实发布之后"的证据层级边界就被抹平了。
        captured["rejected__prepublish_bound_to_publish_instance"] = _expect_rejected(
            c.post(
                "/workspaces/%s/feedback" % wid,
                json={
                    "idempotency_key": _key("fb-illegal-1"),
                    "publish_instance_id": publish["id"],
                    "kind": "observation",
                    "is_pre_publish_review": True,
                },
                headers=H,
            ),
            "pre-publish review 挂 publish_instance",
            422,
        )
        captured["rejected__feedback_bound_to_both"] = _expect_rejected(
            c.post(
                "/workspaces/%s/feedback" % wid,
                json={
                    "idempotency_key": _key("fb-illegal-2"),
                    "publish_instance_id": publish["id"],
                    "content_version_id": version["id"],
                    "kind": "observation",
                    "is_pre_publish_review": True,
                },
                headers=H,
            ),
            "feedback 同时挂两个绑定对象",
            422,
        )

        captured["cycle_decision_create_response"] = _ok(
            c.post(
                "/workspaces/%s/accounts/%s/cycles/decisions" % (wid, acc_full["id"]),
                json={
                    "idempotency_key": _key("decision-1"),
                    "cycle_id": cycle_full["id"],
                    "decision": "kept_unchanged",
                    "source": "m3-contract-capture",
                    "rationale": "证据不足，保持不变",
                    "based_on": {"feedback_ids": [feedbacks[0]["id"]]},
                },
                headers=H,
            ),
            "record cycle decision",
        )

        # --- 以下是 M3 投影真正消费的读端点，逐个原样抓下来 ------------------
        reads = {}
        reads["cycles_current__full"] = _ok(
            c.get("/workspaces/%s/accounts/%s/cycles/current" % (wid, acc_full["id"]), headers=H),
            "GET cycles/current(full)",
        )
        reads["cycles_current__sparse"] = _ok(
            c.get("/workspaces/%s/accounts/%s/cycles/current" % (wid, acc_sparse["id"]), headers=H),
            "GET cycles/current(sparse)",
        )
        reads["campaign_overrides_active__full"] = _ok(
            c.get(
                "/workspaces/%s/accounts/%s/campaign-overrides/active" % (wid, acc_full["id"]),
                headers=H,
            ),
            "GET campaign-overrides/active(full)",
        )
        reads["campaign_overrides_active__sparse"] = _ok(
            c.get(
                "/workspaces/%s/accounts/%s/campaign-overrides/active" % (wid, acc_sparse["id"]),
                headers=H,
            ),
            "GET campaign-overrides/active(sparse)",
        )
        reads["cycle_decisions_latest__full"] = _ok(
            c.get(
                "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (wid, acc_full["id"]),
                headers=H,
            ),
            "GET cycles/decisions/latest(full)",
        )
        # sparse 账号从未记录过任何决策 —— 这是 `none_recorded` 的真实来源
        reads["cycle_decisions_latest__sparse"] = _ok(
            c.get(
                "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (wid, acc_sparse["id"]),
                headers=H,
            ),
            "GET cycles/decisions/latest(sparse)",
        )
        reads["market_observations"] = _ok(
            c.get("/workspaces/%s/market-observations" % wid, headers=H, params={"at": NOW}),
            "GET market-observations",
        )
        reads["market_observations__current_track"] = _ok(
            c.get(
                "/workspaces/%s/market-observations/current" % wid,
                headers=H,
                params={"account_id": acc_full["id"], "applicable_track": "女装", "at": NOW},
            ),
            "GET market-observations/current",
        )
        # ---- v2 新增：实测 M2 的范围过滤（_scope_exclusion_reason）----
        # 没有这三组，「这个账号没有相关观察」与「压根没按这个账号问」在夹具里分不开。
        reads["market_observations__current_no_filter"] = _ok(
            c.get("/workspaces/%s/market-observations/current" % wid,
                  headers=H, params={"at": NOW}),
            "GET market-observations/current(no filter)",
        )
        reads["market_observations__current_other_account"] = _ok(
            c.get("/workspaces/%s/market-observations/current" % wid, headers=H,
                  params={"account_id": acc_sparse["id"], "at": NOW}),
            "GET market-observations/current(other account)",
        )
        reads["market_observations__current_track_mismatch"] = _ok(
            c.get("/workspaces/%s/market-observations/current" % wid, headers=H,
                  params={"applicable_track": "不存在的赛道", "at": NOW}),
            "GET market-observations/current(track mismatch)",
        )
        reads["publish_instance_feedback"] = _ok(
            c.get("/workspaces/%s/publish-instances/%s/feedback" % (wid, publish["id"]), headers=H),
            "GET publish-instance feedback",
        )
        captured["reads"] = reads

        # 权限不足的真实响应：换一个不是本 workspace 成员的 actor
        outsider = _ok(
            c.post(
                "/users",
                json={"external_ref": "%s-outsider" % SLUG, "display_name": "非成员"},
            ),
            "create outsider user",
        )
        captured["permission_denied"] = _expect_rejected(
            c.get(
                "/workspaces/%s/accounts/%s/cycles/current" % (wid, acc_full["id"]),
                headers={"X-Actor-Ref": outsider["external_ref"]},
            ),
            "非成员读取周期",
            403,
        )
        captured["missing_actor_header"] = _expect_rejected(
            c.get("/workspaces/%s/accounts/%s/cycles/current" % (wid, acc_full["id"])),
            "缺 X-Actor-Ref 读取周期",
            401,
        )

    json.dump(captured, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
