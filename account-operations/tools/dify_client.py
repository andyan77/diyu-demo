#!/usr/bin/env python3
"""Dify Console / Service API 客户端（任务分支内真源）。

第 9 轮重建。原件放在会话级 scratchpad 里，随会话消失，导致部署与取证整条链断掉。
**这一版落在仓库里**，不再依赖 scratchpad。

两件事值得写清楚：

1. **凭据只从 worktree 根的 `.env` 读**（已 gitignore）。本文件不含任何凭据，
   也不把凭据写进任何证据文件。

2. **传输路径会自动选择，并且如实上报走了哪条。**
   宿主（WSL2 发行版）只有 `lo` / `eth0`，容器跑在 Docker Desktop 自己的 VM 里，
   宿主要靠它的端口代理才能到 nginx。2026-08-27 该代理处于「TCP 接受连接、
   随即 RST」的故障态（nginx 访问日志里根本没有这些请求），宿主直连不可用。
   修它要重启 Docker Desktop —— 会停掉用户所有容器，不可逆、超出本任务授权。
   因此这里加了第二条路：**请求从容器内部发出**（`docker exec` 起一个短命
   python 进程去打 `http://nginx/...`）。
   Dify 侧收到的东西完全一样：同一个 nginx、同一个 app、同一张图、同一份 payload；
   变的只有客户端待在哪。`TRANSPORT` 会记录实际用的是哪条，取证记录里必须带上它。
"""
import base64
import io
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
RELAY_CONTAINER = "docker-api-1"
RELAY_HOST = "http://nginx"          # 容器内看到的 nginx
DIRECT_HOST = "http://localhost"     # 宿主看到的 nginx（端口代理正常时）

CSRF_HEADER = "X-CSRF-Token"

TRANSPORT = None                     # "direct" | "relay"，首次调用时定下来


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def load_env(path=None):
    """只解析 KEY=VALUE，忽略注释与空行。不打印、不外传。"""
    env = {}
    for line in io.open(path or os.path.join(WORKTREE, ".env"), encoding="utf-8"):
        m = re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$", line)
        if m and not line.lstrip().startswith("#"):
            env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return env


# ------------------------------------------------------------------ 传输层

_RELAY_PROG = (
    "import sys,json,urllib.request,urllib.error\n"
    "s=json.load(sys.stdin)\n"
    "op=urllib.request.build_opener(urllib.request.ProxyHandler({}))\n"
    "d=s['data'].encode('utf-8') if s.get('data') is not None else None\n"
    "rq=urllib.request.Request(s['url'],data=d,headers=s.get('headers') or {},"
    "method=s['method'])\n"
    "try:\n"
    "    r=op.open(rq,timeout=s.get('timeout',120))\n"
    "    print(json.dumps({'status':r.status,'headers':list(r.headers.items()),"
    "'body':r.read().decode('utf-8','replace')}))\n"
    "except urllib.error.HTTPError as e:\n"
    "    print(json.dumps({'status':e.code,'headers':list(e.headers.items()),"
    "'body':e.read().decode('utf-8','replace')}))\n"
    "except Exception as e:\n"
    "    print(json.dumps({'status':-1,'headers':[],"
    "'body':json.dumps({'error':type(e).__name__+': '+str(e)})}))\n"
)


def _direct(method, url, headers, data, timeout):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    rq = urllib.request.Request(url, data=(data.encode("utf-8") if data else None),
                                headers=headers or {}, method=method)
    try:
        r = op.open(rq, timeout=timeout)
        return {"status": r.status, "headers": list(r.headers.items()),
                "body": r.read().decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "headers": list(e.headers.items()),
                "body": e.read().decode("utf-8", "replace")}


def _relay(method, url, headers, data, timeout):
    spec = {"method": method, "url": url, "headers": headers or {},
            "data": data, "timeout": timeout}
    p = subprocess.run(["docker", "exec", "-i", RELAY_CONTAINER, "python3", "-c", _RELAY_PROG],
                       input=json.dumps(spec), capture_output=True, text=True,
                       timeout=timeout + 60)
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError(f"relay 失败 rc={p.returncode}: {(p.stderr or '')[:300]}")
    return json.loads(p.stdout)


def _probe():
    """先试宿主直连；不通就走容器中转。只探一次，结果记进 TRANSPORT。"""
    global TRANSPORT
    if TRANSPORT:
        return TRANSPORT
    try:
        r = _direct("GET", DIRECT_HOST + "/console/api/setup", {}, None, 5)
        if r["status"] == 200:
            TRANSPORT = "direct"
            return TRANSPORT
    except Exception:  # noqa: BLE001 - 探测失败就是探测失败，不藏
        pass
    _relay("GET", RELAY_HOST + "/console/api/setup", {}, None, 10)   # 不通就让它抛
    TRANSPORT = "relay"
    return TRANSPORT


def http_json(method, path, headers=None, body=None, timeout=120, raw_body=None):
    """path 以 `/` 开头；host 由当前传输路径决定。返回 dict(status, headers, body)。"""
    t = _probe()
    host = DIRECT_HOST if t == "direct" else RELAY_HOST
    h = dict(headers or {})
    data = raw_body
    if body is not None:
        data = json.dumps(body, ensure_ascii=False)
        h.setdefault("Content-Type", "application/json")
    fn = _direct if t == "direct" else _relay
    return fn(method, host + path, h, data, timeout)


# ------------------------------------------------------------------ Console

class Console:
    """真实登录后的 Console 会话。

    Dify 当前版本：登录 payload 里的 `password` 是 **base64**（不是 RSA，
    见 `libs/field_encryption.py::FieldEncryption.decrypt_field`）；
    鉴权走 cookie，且写操作要求请求头 `X-CSRF-Token` 与 `csrf_token` cookie 相等
    （`libs/token.py::check_csrf_token`）。
    """

    def __init__(self, env=None):
        self.env = env or load_env()
        self.jar = {}
        self.transport = None
        self._login()

    def _login(self):
        pw = base64.b64encode(self.env["DIFY_CONSOLE_PASSWORD"].encode()).decode()
        r = http_json("POST", "/console/api/login",
                      body={"email": self.env["DIFY_CONSOLE_EMAIL"], "password": pw,
                            "language": "zh-Hans", "remember_me": True}, timeout=30)
        if r["status"] != 200:
            raise RuntimeError(f"console 登录失败 {r['status']}: {r['body'][:200]}")
        for k, v in r["headers"]:
            if k.lower() == "set-cookie":
                nv = v.split(";")[0]
                name, _, val = nv.partition("=")
                if val:
                    self.jar[name.strip()] = val.strip()
        if "access_token" not in self.jar:
            raise RuntimeError("登录返回里没有 access_token cookie")
        self.transport = TRANSPORT

    def _headers(self):
        h = {"Cookie": "; ".join(f"{k}={v}" for k, v in self.jar.items())}
        if "csrf_token" in self.jar:
            h[CSRF_HEADER] = self.jar["csrf_token"]
        return h

    def call(self, method, path, body=None, timeout=180):
        r = http_json(method, path, headers=self._headers(), body=body, timeout=timeout)
        try:
            return r["status"], json.loads(r["body"])
        except Exception:  # noqa: BLE001
            return r["status"], {"raw": r["body"][:2000]}

    # -------------------------------------------------------------- 便利方法

    def find_app(self, name_contains):
        st, apps = self.call("GET", "/console/api/apps?page=1&limit=100")
        assert st == 200, (st, apps)
        hits = [a for a in apps["data"] if name_contains in (a.get("name") or "")]
        return hits

    def app_api_key(self, app_id, create_if_missing=True):
        """取应用的 Service API key。**只返回值，不落盘**；调用方决定写到哪，
        写也只能写进 gitignore 的路径。"""
        st, keys = self.call("GET", f"/console/api/apps/{app_id}/api-keys")
        assert st == 200, (st, keys)
        data = keys.get("data") or []
        if data:
            return data[0]["token"]
        if not create_if_missing:
            return None
        st, k = self.call("POST", f"/console/api/apps/{app_id}/api-keys", body={})
        assert st in (200, 201), (st, k)
        return k["token"]

    def import_dsl(self, yaml_content, name, description=None):
        """从 DSL 字节内容新建一个独立应用（`mode=yaml-content`，不传 `app_id`）。

        路由与 payload 字段核实自本机 `docker-api-1` 容器内
        `controllers/console/app/app_import.py`（Dify 1.16.1 实际源码，非文档推测）：
        `POST /console/api/apps/imports`，`AppImportPayload{mode, yaml_content, name, ...}`。
        `mode` 取值核实自 `services/entities/dsl_entities.py::ImportMode.YAML_CONTENT = "yaml-content"`。
        返回值含 `app_id` 与 `status`；`status == "pending"` 时需要再调
        `confirm_import` 才会真正建库，本方法在返回前自动做这一步，调用方拿到的
        始终是终态结果。**只建新应用，不接受 `app_id` 参数——不提供改动既有应用的能力。**
        """
        body = {"mode": "yaml-content", "yaml_content": yaml_content, "name": name}
        if description is not None:
            body["description"] = description
        st, result = self.call("POST", "/console/api/apps/imports", body=body, timeout=120)
        assert st in (200, 202), (st, result)
        if result.get("status") == "pending":
            import_id = result["id"]
            st2, result2 = self.call("POST", f"/console/api/apps/imports/{import_id}/confirm", body={})
            assert st2 == 200, (st2, result2)
            return result2
        return result

    def publish_workflow(self, app_id, marked_name="", marked_comment=""):
        """`POST /console/api/apps/{app_id}/workflows/publish`。核实自
        `controllers/console/app/workflow.py::PublishedWorkflowApi.post`——
        body 只接受 `marked_name`/`marked_comment`，均可为空，无需传 draft 内容
        （发布的是该应用当前已保存的草稿图，即刚导入 DSL 时写入的图）。"""
        st, result = self.call(
            "POST", f"/console/api/apps/{app_id}/workflows/publish",
            body={"marked_name": marked_name, "marked_comment": marked_comment}, timeout=60)
        assert st == 200, (st, result)
        return result


# ------------------------------------------------------------------ Service API

def run_workflow(key, inputs, user, timeout=1200):
    """`POST /v1/workflows/run`，blocking。返回 {status, body, elapsed_seconds}。

    三个 runner 原先各自内联了一份 urllib 调用，只能从宿主发出。宿主→容器的
    端口代理故障之后它们全都打不通，所以统一改成走这里的传输层——
    **payload 一个字节没变**，变的只有客户端待在哪。
    """
    start = time.time()
    try:
        r = http_json("POST", "/v1/workflows/run",
                      headers={"Authorization": f"Bearer {key}"},
                      body={"inputs": inputs, "response_mode": "blocking", "user": user},
                      timeout=timeout)
        try:
            body = json.loads(r["body"])
        except Exception:  # noqa: BLE001
            body = {"error": r["body"][:2000]}
        return {"status": r["status"], "body": body,
                "elapsed_seconds": round(time.time() - start, 2)}
    except Exception as e:  # noqa: BLE001 - 传输失败如实记为证据，不隐藏
        return {"status": -1, "body": {"error": f"{type(e).__name__}: {e}"},
                "elapsed_seconds": round(time.time() - start, 2)}


if __name__ == "__main__":
    c = Console()
    print("传输路径:", c.transport)
    print("cookie:", sorted(c.jar))
    hits = c.find_app("DIYU-V1-M3")
    for a in hits:
        print("app:", a["id"], a["name"][:70])
