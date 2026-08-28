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
SEAM_APP = "de0cb1e9-2af8-415a-9762-31b6cf348c22"
CANVAS_APP = "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"
M3_APP = "b7fb5b1a-9278-426c-bb8a-f9f288639548"
CAPABILITY_APPS = {
    "MATRIX":               "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3",
    "CAMPAIGN":             "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b",
    "CONTENT_BRIEF":        "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1",
    "CREATIVE_SCRIPT":      "8d518554-bfbc-4be0-8a57-3b1f04983edf",
    "PRODUCTION_DIRECTOR":  "57ebc138-ed9e-4202-bce2-38e44da0ec1d",
    "PUBLISHING_PACKAGING": "10056fcf-9237-4889-a3e3-81e3a695cae0",
}
CAPABILITIES = tuple(CAPABILITY_APPS)

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
        """M3 周期判断与内容任务。account_context = M2→M3 最小当前投影。"""
        r = DC.run_workflow(self.key(M3_APP), {
            "account_context": account_context,
            "user_request": user_request,
            "loaded_references": loaded_references,
        }, user=user)
        return _wf_result(r)

    # ------------------------------------------------------------ M4 接缝
    def seam(self, capability, capability_call, professional_input,
             entry="", example_reference_requested="NO", user="m5-runtime"):
        """一次调用只进入一个专业能力。capability 必须是六项之一。

        返回 dict 含 business_delivery_outcome / user_delivery / returns_json /
        seam_trace_json 等；**平台 status 与业务交付分开报**。
        """
        if capability not in CAPABILITIES:
            raise ValueError("capability 必须是六项之一，收到：%r" % (capability,))
        r = DC.run_workflow(self.key(SEAM_APP), {
            "capability": capability,
            "entry": entry,
            "capability_call": capability_call,
            "professional_input": professional_input,
            "example_reference_requested": example_reference_requested,
        }, user=user)
        return _wf_result(r)


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
        "user_delivery": outputs.get("user_delivery"),
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


def current_projection(ws, actor, account_id):
    """M2 最小当前投影 —— M3 的 account_context 由此而来，不靠人手抄。"""
    st, cyc = m2("GET", "/workspaces/%s/accounts/%s/cycles/current" % (ws, account_id),
                 actor=actor)
    st2, dec = m2("GET", "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (ws, account_id),
                  actor=actor)
    return {"cycle_current": {"status": st, "body": cyc},
            "decision_latest": {"status": st2, "body": dec}}


if __name__ == "__main__":
    # 只做连通性自检，不产生任何正式 PASS。
    print("M2 healthz:", m2("GET", "/healthz"))
    print("capabilities:", CAPABILITIES)
