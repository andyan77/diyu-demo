#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 统一集成运行时 · 把 M1/M2/M3/M4 接成一个可自然使用的系统。

**这不是第二套工作流引擎，也不是第二套路由。** 它只做两件 main 上原本缺失的事：

  接缝 A（M3 → M4）：把 M3 的运营判断/内容任务，按 M4 已冻结的统一业务能力外壳
                     （capability / capability_call / professional_input）送进
                     **已发布的** Capability Seam，一次只进一个专业能力。
  接缝 B（M4 → M2）：把测试发布结果与反馈按版本写回 **已运行的** M2 服务，
                     再由 M3 复盘进入 Cycle N+1。

其余全部复用既有真源：
  - M1  decision-chain/workflows/m1_context_compiler_v0.1.py
  - M2  business-persistence 服务（容器 diyu-m2-app，docker_default 网络）
  - M3  Dify 已发布应用 b7fb5b1a（m3-cand-v1.5.2-live）
  - M4  Dify 已发布 Capability Seam de0cb1e9 + 六个能力应用
  - 传输 account-operations/tools/dify_client.py（direct/relay 自动选路）

M4 语义在本文件中是**硬约束**，不是建议：
  1. 一次调用只进入一个专业能力；六个能力应用之间零调用边；不得拼成固定全链。
  2. 读业务结果一律看 business_delivery_outcome，**不拿平台 status 当交付成功**。
  3. user_delivery 是唯一可直接呈现给用户的字段；artifact 不整份透出。
  4. 组件级 Return 是**该分支结果**，不是整任务 terminal/hard stop，不触发全局硬停。
  5. 组件可按需调用、可合法跳过；调用哪些由任务决定，不由本文件写死。

凭据只在内存中使用，不打印、不落盘、不写进任何证据文件。
"""
import importlib.util
import json
import os
import subprocess
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# ---------------------------------------------------------------- 冻结绑定
# 全部来自 M4 → M5 交接映射 V1_M4_M5_HANDOFF_MAP_v0.1.yaml，并在 Node 2 现场复算一致。
# ---------------------------------------------------------------- 应用绑定
# 两套绑定并存，是为了能做**同一输入的新旧对照**，不是为了留后门。
#   legacy = M4 已接受的八个应用，**一个字节都不动**，只读、只用于对照；
#   rb     = M5 AC-07 Rebase 的 successor：只换 envelope_check 里那一份
#            _find_scalar，接缝只把 6 个 tool 节点改指新能力，其余节点照搬。
# 默认走 rb —— 它是本轮候选。要跑对照就 M5_BIND=legacy。
LEGACY_BIND = {
    "SEAM": "de0cb1e9-2af8-415a-9762-31b6cf348c22",
    "M3":   "b7fb5b1a-9278-426c-bb8a-f9f288639548",
    "MATRIX":               "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3",
    "CAMPAIGN":             "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b",
    "CONTENT_BRIEF":        "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1",
    "CREATIVE_SCRIPT":      "8d518554-bfbc-4be0-8a57-3b1f04983edf",
    "PRODUCTION_DIRECTOR":  "57ebc138-ed9e-4202-bce2-38e44da0ec1d",
    "PUBLISHING_PACKAGING": "10056fcf-9237-4889-a3e3-81e3a695cae0",
}
RB_BIND = {
    "SEAM": "9e1b1fd8-f696-436d-9d42-54700a29a4dd",
    "M3":   "ca4c28aa-e0fd-4c54-bde3-a0918dc4c884",
    "MATRIX":               "47e52165-f6cb-48ff-93be-6c6a8ea5cecf",
    "CAMPAIGN":             "7d10e28d-30e6-4c4a-950b-88dcbb5fd0fc",
    "CONTENT_BRIEF":        "cbbeab61-a4de-4a21-a6be-7dc2385dd6f3",
    "CREATIVE_SCRIPT":      "4fbcfea8-48a3-41b3-b2b5-cdb50276eeb2",
    "PRODUCTION_DIRECTOR":  "07e99f7b-71a3-40af-85f3-fc43b68e774a",
    "PUBLISHING_PACKAGING": "0fb7636a-55e8-49a9-92f7-3d11ad0a35fa",
}
BIND_NAME = os.environ.get("M5_BIND", "rb").lower()
if BIND_NAME not in ("rb", "legacy"):
    raise ValueError("M5_BIND 只接受 rb / legacy，实得 %r" % BIND_NAME)
_BIND = RB_BIND if BIND_NAME == "rb" else LEGACY_BIND

SEAM_APP = _BIND["SEAM"]
CANVAS_APP = "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"
M3_APP = _BIND["M3"]
CAPABILITY_APPS = {k: v for k, v in _BIND.items() if k not in ("SEAM", "M3")}
CAPABILITIES = tuple(CAPABILITY_APPS)

# M5 测试候选：M3 判断（散文）→ 能力外壳（扁平）的抽取适配器。
# 它是 M5 自己新建的应用，不改 M1-M4 任何已发布应用；只做抽取与格式化，不做业务判断。
ADAPTER_APP = "e1013ce2-69c5-44c1-ad83-26534f3c5e4c"   # m5-adapter-v0.1（只覆盖 CONTENT_BRIEF 一跳）
# v0.2 能力感知版：按目标能力各自的必填清单抽取，覆盖六个能力的全部跨能力接缝。
# 六个能力的必填清单实测互不相同，一份写死的清单接不完整条链——这是诊断出来的，不是设计假设。
HOP_ADAPTER_APP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"   # m5-hop-adapter-v0.2

M2_BASE = "http://diyu-m2-app:8000"
M2_RELAY_CONTAINER = "docker-api-1"   # 与 dify_client 同一条 relay 通道
DIFY_ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"

# 只有这些字段可以直接给用户看。其余一律内部字段。
USER_VISIBLE = ("user_delivery",)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DC = _load("m5_dify_client", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
M1 = _load("m5_m1_compiler", os.path.join(ROOT, "decision-chain", "workflows",
                                          "m1_context_compiler_v0.1.py"))


# ================================================================ M2 客户端
# 宿主没有到 diyu-m2-app 的端口映射（实测 172.18.0.15:8000 不可达），
# 因此复用 dify_client 已确立的 relay 形态：从 docker_default 网络内部发请求。
# Dify 侧看到的东西完全一样，变的只有客户端待在哪。
_M2_RELAY_PROG = r"""
import json, sys, urllib.request, urllib.error
m, u, h, b = json.load(sys.stdin)
req = urllib.request.Request(u, method=m,
                             data=(json.dumps(b).encode() if b is not None else None))
for k, v in h.items():
    req.add_header(k, v)
if b is not None:
    req.add_header("Content-Type", "application/json")
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print(json.dumps({"status": r.status, "body": r.read().decode()}))
except urllib.error.HTTPError as e:
    print(json.dumps({"status": e.code, "body": e.read().decode()}))
except Exception as e:
    print(json.dumps({"status": -1, "body": "%s: %s" % (type(e).__name__, e)}))
"""


def m2(method, path, body=None, actor=None, timeout=90):
    """打 M2 服务。返回 (status, parsed_body)。传输失败如实上报，不静默吞掉。"""
    headers = {}
    if actor:
        headers["X-Actor-Ref"] = actor
    payload = json.dumps([method, M2_BASE + path, headers, body])
    p = subprocess.run(
        ["docker", "exec", "-i", M2_RELAY_CONTAINER, "python3", "-c", _M2_RELAY_PROG],
        input=payload, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        return -1, {"error": "relay failed: " + (p.stderr or "")[:300]}
    try:
        r = json.loads(p.stdout.strip())
    except Exception:
        return -1, {"error": "unparsable relay output: " + p.stdout[:300]}
    try:
        return r["status"], json.loads(r["body"])
    except Exception:
        return r["status"], {"raw": r["body"][:2000]}


# ================================================================ Dify 会话
class Runtime(object):
    """一个 M5 运行会话：持有 console 登录与各应用的 service key（仅内存）。"""

    def __init__(self, env_path=DIFY_ENV):
        self.env = DC.load_env(env_path)
        self.console = DC.Console(env=self.env)
        self._keys = {}

    def key(self, app_id):
        if app_id not in self._keys:
            self._keys[app_id] = self.console.app_api_key(app_id)
        return self._keys[app_id]

    # ------------------------------------------------------------ M3
    def m3_operate(self, account_context, user_request, loaded_references="", user="m5-runtime"):
        """M3 周期判断与内容任务。account_context = M2→M3 最小当前投影。

        **参考资料信封闸门。** M3 的契约要求 `loaded_references` 带
        `<<REFERENCE_MANIFEST>>` 与逐项 LOADED/NOT_LOADED；没有清单时 M3 会照规范
        写「本轮输入没有附参考资料清单，所以我不判断专业参考文件是否加载」并拒绝
        引用参考内容——**它没做错，是调用方没给清单**。

        这个错法实际发生过：完整主故事走 `m3_loaded_references()` 组了合法清单，
        短入口和风险探针却把裸夹具正文直接塞进这个参数，于是同一套系统在两条路径上
        拿到的不是同一个 M3。裸正文不会报错，只会安静地少掉整个专业方法层，
        跑出来的证据看着正常但不成立。所以这里改成**结构性拒绝**：
        要么给合法清单，要么显式传空表示本轮不提供参考；不接受「有正文、无清单」。
        """
        refs = loaded_references or ""
        if refs.strip() and "<<REFERENCE_MANIFEST>>" not in refs:
            raise ValueError(
                "loaded_references 非空但没有 <<REFERENCE_MANIFEST>>：这会让 M3 拒绝"
                "引用参考资料，而调用方却以为已加载。请用 FULL_STORY.m3_loaded_references() "
                "组装，或显式传空字符串表示本轮不提供参考。")
        return _run_with_retry(self.key(M3_APP), {
            "account_context": account_context,
            "user_request": user_request,
            "loaded_references": loaded_references,
        }, user, "m3")

    # ------------------------------------------------------------ M3 -> M4 抽取适配
    def adapt(self, m3_judgment, account_context="", user_request="", user="m5-runtime"):
        """把 M3 的运营判断抽取成能力侧可解析的扁平外壳。

        **只抽取，不判断。** 抽不到就留空并计入 extraction_gaps，不推断、不补全、
        不跨源搬运——缺口如实上报比填满字段重要。
        """
        r = DC.run_workflow(self.key(ADAPTER_APP), {
            "m3_judgment": m3_judgment,
            "account_context": account_context,
            "user_request": user_request,
        }, user=user)
        return _wf_result(r)

    def hop(self, target_capability, m3_judgment="", upstream_delivery="",
            upstream_capability="", registered_facts="", account_context="",
            user_request="", focus_fields="", user="m5-runtime"):
        """跨能力接缝：按目标能力的必填清单，从四类已登记来源抽取扁平外壳。

        与 adapt() 的区别是它**知道自己要进哪个能力**。M4 冻结了六个能力各自的
        必填清单且能力之间零调用边，谁来接这一跳由 M5 负责——这就是那一跳。
        """
        return _run_with_retry(self.key(HOP_ADAPTER_APP), {
            "target_capability": target_capability,
            "m3_judgment": m3_judgment,
            "upstream_delivery": upstream_delivery,
            "upstream_capability": upstream_capability,
            "registered_facts": registered_facts,
            "account_context": account_context,
            "user_request": user_request,
            "focus_fields": focus_fields,
        }, user, "hop:%s" % target_capability)

    # ------------------------------------------------------------ M4 接缝
    def seam(self, capability, capability_call, professional_input,
             entry="", example_reference_requested="NO", user="m5-runtime"):
        """一次调用只进入一个专业能力。capability 必须是六项之一。

        返回 dict 含 business_delivery_outcome / user_delivery / returns_json /
        seam_trace_json 等；**平台 status 与业务交付分开报**。
        """
        if capability not in CAPABILITIES:
            raise ValueError("capability 必须是六项之一，收到：%r" % (capability,))
        return _run_with_retry(self.key(SEAM_APP), {
            "capability": capability,
            "entry": entry,
            "capability_call": capability_call,
            "professional_input": professional_input,
            "example_reference_requested": example_reference_requested,
        }, user, "seam:%s" % capability)


# 只有这些是**传输层/模型可用性**故障，可以重试。业务结果一律不重试——
# INPUT_INSUFFICIENT、组件级 Return、UNKNOWN 都是真实业务结论，重试就是掩盖。
TRANSIENT_MARKERS = (
    "Server Unavailable Error", "SSLEOFError", "UNEXPECTED_EOF_WHILE_READING",
    "Max retries exceeded", "Connection aborted", "Read timed out",
    "Remote end closed connection", "Bad gateway", "502", "503", "504",
)
MAX_TRANSIENT_ATTEMPTS = 3


def _is_transient(result):
    if (result or {}).get("platform_status") != "failed":
        return False
    err = str((result or {}).get("error") or "")
    return any(m in err for m in TRANSIENT_MARKERS)


def _run_with_retry(key, inputs, user, label):
    """有界重试。每次尝试都记进 attempts，失败原因原样保留，不吞。"""
    attempts = []
    for i in range(MAX_TRANSIENT_ATTEMPTS):
        r = _wf_result(DC.run_workflow(key, inputs, user=user))
        attempts.append({"attempt": i + 1, "platform_status": r["platform_status"],
                         "run_id": r["run_id"],
                         "error": (str(r.get("error"))[:200] if r.get("error") else None)})
        if not _is_transient(r):
            r["attempts"] = attempts
            return r
        if i + 1 < MAX_TRANSIENT_ATTEMPTS:
            time.sleep(5 * (i + 1))
    r["attempts"] = attempts
    r["transient_exhausted"] = True
    return r


def _wf_result(r):
    """把 Dify 运行结果规范成统一形状，**不把平台成功当业务交付成功**。"""
    body = r.get("body") or {}
    data = body.get("data") or {}
    outputs = data.get("outputs") or {}
    return {
        "platform_status": data.get("status") or ("http_%s" % r.get("status")),
        "http_status": r.get("status"),
        "run_id": data.get("id") or body.get("workflow_run_id"),
        "elapsed_seconds": r.get("elapsed_seconds"),
        "outputs": outputs,
        # 业务真相以此字段为准（M4 交接契约明写）
        "business_delivery_outcome": outputs.get("business_delivery_outcome"),
        # user_delivery 是唯一可**直接呈现给用户**的字段。
        # artifact 不整份透出给用户，但它是**给下一个专业能力用的产物本体**——
        # 「不给用户看」和「不给下一跳用」是两件事，不能混为一谈。
        "user_delivery": outputs.get("user_delivery"),
        "artifact": outputs.get("artifact"),
        "binding_json": outputs.get("binding_json"),
        "seam_trace_json": outputs.get("seam_trace_json"),
        "capabilities_skipped": outputs.get("capabilities_skipped"),
        "error": body.get("error") or (data.get("error") if isinstance(data, dict) else None),
    }


# ================================================================ 语义守卫
def user_facing(result):
    """只取可直接呈现给用户的部分。artifact / 内部状态一律不透出。"""
    return {k: result.get(k) for k in USER_VISIBLE}


def is_component_return(result):
    """组件级 Return：本分支结果，不是整任务终态。"""
    rj = (result.get("outputs") or {}).get("returns_json")
    if not rj:
        return False
    try:
        arr = json.loads(rj) if isinstance(rj, str) else rj
    except Exception:
        return False
    return bool(arr)


def component_return_gaps(result):
    """从组件级 Return 里取出**能力侧自己写的**精确缺口与那一个问题。
    不由本文件猜能力在缺什么——它已经说了。"""
    try:
        arr = json.loads((result.get("outputs") or {}).get("returns_json") or "[]")
    except Exception:
        return None
    if not arr:
        return None
    r0 = arr[0] or {}
    return {"precise_gap": r0.get("precise_gap"),
            "highest_damaged_layer": r0.get("highest_damaged_layer"),
            "affected_objects": r0.get("affected_objects"),
            "downstream_stale": r0.get("downstream_stale"),
            "needs_user_decision": r0.get("needs_user_decision"),
            "single_question": (result.get("outputs") or {}).get("single_question"),
            "missing": (result.get("outputs") or {}).get("missing")}


def delivered(result):
    """业务是否真的交付。只认 business_delivery_outcome，不认平台 status。"""
    return result.get("business_delivery_outcome") in ("DELIVERED", "DELIVERED_AFTER_RECOVERY")


# ================================================================ 接缝 B：写回 M2
def record_test_publish(ws, actor, content_version_id, account_id, platform,
                        external_ref, idempotency_key):
    """测试/模拟发布记录写入 M2。**不连接真实内容平台。**"""
    return m2("POST", "/workspaces/%s/publish-instances" % ws, {
        "content_version_id": content_version_id,
        "account_id": account_id,
        "platform": platform,
        "external_ref": external_ref,
        "idempotency_key": idempotency_key,
    }, actor=actor)


def record_feedback(ws, actor, publish_instance_id, payload, idempotency_key,
                    observed_at=None):
    """反馈按版本幂等写回 M2。重复写入不得制造双份事实。"""
    body = {
        "publish_instance_id": publish_instance_id,
        "payload": payload,
        "idempotency_key": idempotency_key,
    }
    if observed_at:
        body["observed_at"] = observed_at
    return m2("POST", "/workspaces/%s/feedback" % ws, body, actor=actor)


def current_projection(ws, actor, account_id, task_id=None, task_ids=None):
    """M2 最小当前投影 —— M3 的 account_context 由此而来，不靠人手抄。

    **补上运行状态。** 旧版只投影周期与最近决策，投出来实测 217 字符，里面
    没有一个字说明上一轮跑到哪、哪些写入已经发生过。于是恢复场景下用户问
    「昨天那条反馈到底提交成没成」，M3 手上根本没有可查的依据——而 M3 的契约
    明写它**不处理 M2 的并发、幂等、权限、版本晋升或恢复内部实现**，那是 M2 的事。
    该拿的东西 M2 一直有（`/tasks/{id}/run-state` 的 last_success_step、failed_step、
    resumable_from、side_effects），是这一侧没去拿。
    """
    st, cyc = m2("GET", "/workspaces/%s/accounts/%s/cycles/current" % (ws, account_id),
                 actor=actor)
    st2, dec = m2("GET", "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (ws, account_id),
                  actor=actor)
    out = {"cycle_current": {"status": st, "body": cyc},
           "decision_latest": {"status": st2, "body": dec}}
    # 一个账号上同时有多条在跑的事是常态：这周的内容安排、上周的发布登记、
    # 某一条的推进，各自有各自的运行状态。只投一个 task 等于让系统看不见其余的，
    # 而看不见就只能靠用户说——那正是本轮要修的毛病。M2 没有按账号列 task 的端点，
    # 所以由调用方交出它这次涉及哪些 task；它本来就知道，是它建的。
    ids = list(task_ids) if task_ids else ([task_id] if task_id else [])
    states = []
    for t in ids:
        tid = t["id"] if isinstance(t, dict) else t
        label = t.get("label") if isinstance(t, dict) else None
        st3, rs = m2("GET", "/workspaces/%s/tasks/%s/run-state" % (ws, tid), actor=actor)
        states.append({"task_id": tid, "label": label, "status": st3, "body": rs})
    if states:
        out["run_states"] = states
        out["run_state"] = states[0]          # 向后兼容：单 task 调用方行为不变
    return out


if __name__ == "__main__":
    # 只做连通性自检，不产生任何正式 PASS。
    print("M2 healthz:", m2("GET", "/healthz"))
    print("capabilities:", CAPABILITIES)
