#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 后继 Dify 对象发布与 provider 重绑 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001

副作用纪律（Prompt §13 / 统一合同 §10.2 / N-20 / N-24）：
  1. **写前**：导出并登记九个受保护应用的 published workflow 绑定与 graph md5，
     以及本任务已创建对象的当前状态；任一保护应用发生变化即中止，不写入。
  2. **幂等键**：应用名唯一含 "M4 v1.3 TEST"；同名对象存在即更新，不重复创建。
  3. **回滚锚点**：每次写前记录对象 id + 内容 hash + 上一版本 id。
  4. **写后**：由目标系统确认（重新读取并比对），不以 HTTP 200 当成功。
  5. `STARTED/UNKNOWN`：先查目标系统副作用，**不盲重放**。
  6. 只碰名称含 "M4 v1.3 TEST" 的对象。**绝不**修改九个保护应用、M1/M2/M3 资产，
     **绝不**直接 SQL 改 Dify，**绝不**删远端分支或连真实平台。

阶段：
  preflight   只读：核对保护应用完整性 + 列出将要创建/更新的对象
  publish     导入/更新六个能力应用与父接缝应用，并发布
  rebind      把已发布子应用注册为 workflow tool，回填 provider_id，重生成父接缝并重新发布
  confirm     由目标系统确认全部写入结果，并复算保护应用完整性

凭据：
  从环境变量读取，或从 `DIYU_M4_DIFY_ENV` 指向的 .env 文件读取：
    DIFY_CONSOLE_BASE_URL / DIFY_CONSOLE_EMAIL / DIFY_CONSOLE_PASSWORD
  凭据只在内存中使用，不写入任何文件、commit 或账本。
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import http.cookiejar
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
CP_WF = os.path.join(ROOT, "content-production", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
BINDINGS = os.path.join(DC_WF, "DIYU_M4_PROVIDER_BINDINGS.json")

APP_TAG = "M4 v1.3 TEST"

# Run Manifest §2.5 写前锚点：任一行变化即中止写入
PROTECTED = {
    "310ddfcf-e0fb-4211-af98-3d101725e07a": ("DIYU Demo V1 Main Chatflow v0.1",
                                             "055b7bbe-172f-4456-8459-951ae3e14ce7",
                                             "8def6c4f436ad989557992c59d029958"),
    "f8d2be15-2f71-4765-a482-fb62c0e1f3a0": ("Tool Matrix Architect v0.1",
                                             "612c8080-a952-4925-b17b-73205f89cdd8",
                                             "698882cb607c4e9a5837a1f7fbeee6d9"),
    "a0d92232-0afe-4b77-abb4-5356fd04bc7b": ("Tool Campaign Orchestrator v0.1",
                                             "1f5505a6-c9e9-480a-9979-0435fa4af229",
                                             "d58979e4e03cdb4e966510cfa73d78f7"),
    "eadf8867-6e00-48b8-b3b9-2cb8b89d8834": ("Tool Content Brief Architect v0.1",
                                             "8248fc80-08ff-4852-9812-598b263ef728",
                                             "3899602de5df3821fe1efc64016fd038"),
    "13ba9e70-2193-4217-9ac8-32bfda2a7822": ("Creative Script v0.1",
                                             "18668db6-8faa-4151-8cbd-aab74e4ed15c",
                                             "7aedc2221e83b7e8cc24b1e42de3811d"),
    "4433b747-4216-44d6-b8bb-e6664d3cf4fb": ("Production Director v0.1",
                                             "9342e31b-c342-466a-8604-ec076cd6e6d5",
                                             "f10feb365a209196f20ca8adb7b68907"),
    "fa71a06d-2b0d-4d09-b580-ca8e2db5f0a6": ("Publishing Packaging v0.1",
                                             "dcf428ee-8469-4e45-adf6-2016a1824fab",
                                             "053a5e4ed6a9c9b1970d7c206ce65dd7"),
    "4eac6ab7-9d81-4af0-accf-740e3157f5ea": ("PRE Chain Stage 1 v0.1",
                                             "762c23cd-226d-45f2-8126-009132565010",
                                             "cf8b4de9e33036d24059c8bfa8515b7b"),
    "2c188608-0559-4ef4-8c76-18b4f48c3cd9": ("Publishing Stage 2 v0.1",
                                             "993afbd8-e5f7-418d-827c-394389a13efd",
                                             "263efc104513463a1988c0698dd995ed"),
}

DSL_FILES = [
    ("matrix", os.path.join(DC_WF, "DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml")),
    ("campaign", os.path.join(DC_WF, "DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml")),
    ("content_brief", os.path.join(DC_WF, "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml")),
    ("creative_script", os.path.join(CP_WF, "DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml")),
    ("production_director", os.path.join(CP_WF, "DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml")),
    ("publishing_packaging", os.path.join(CP_WF, "DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml")),
]
SEAM_FILE = os.path.join(DC_WF, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")
CANVAS_FILE = os.path.join(DC_WF, "DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml")


# ---------------------------------------------------------------- 只读侦察
def psql(sql):
    """只读 SELECT。本脚本绝不通过 SQL 修改 Dify。"""
    assert sql.strip().upper().startswith("SELECT"), "只允许只读 SELECT"
    out = subprocess.run(
        ["docker", "exec", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify", "-tAc", sql],
        capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError("psql failed: %s" % out.stderr.strip())
    return [l for l in out.stdout.strip().split("\n") if l.strip()]


def protected_integrity():
    rows = psql(
        "SELECT a.id, a.workflow_id, md5(w.graph) FROM apps a "
        "LEFT JOIN workflows w ON w.id=a.workflow_id WHERE a.id IN (%s);"
        % ",".join("'%s'" % k for k in PROTECTED))
    got = {}
    for r in rows:
        parts = r.split("|")
        got[parts[0]] = (parts[1], parts[2])
    diffs = []
    for app_id, (name, wf_id, md5) in PROTECTED.items():
        if app_id not in got:
            diffs.append("%s (%s): 应用消失" % (name, app_id))
            continue
        if got[app_id][0] != wf_id:
            diffs.append("%s: published workflow_id %s -> %s" % (name, wf_id, got[app_id][0]))
        if got[app_id][1] != md5:
            diffs.append("%s: graph md5 %s -> %s" % (name, md5, got[app_id][1]))
    return diffs


def existing_m4_apps():
    rows = psql("SELECT id, name, mode FROM apps WHERE name LIKE '%%%s%%' ORDER BY created_at;" % APP_TAG)
    return [dict(zip(("id", "name", "mode"), r.split("|"))) for r in rows]


# ---------------------------------------------------------------- Console API
class Console(object):
    def __init__(self):
        cfg = {}
        env_file = os.environ.get("DIYU_M4_DIFY_ENV", "")
        if env_file and os.path.exists(env_file):
            for line in open(env_file, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip().strip('"').strip("'")
        self.base = (os.environ.get("DIFY_CONSOLE_BASE_URL")
                     or cfg.get("DIFY_CONSOLE_BASE_URL", "http://127.0.0.1")).rstrip("/")
        self.email = os.environ.get("DIFY_CONSOLE_EMAIL") or cfg.get("DIFY_CONSOLE_EMAIL")
        self.pw = os.environ.get("DIFY_CONSOLE_PASSWORD") or cfg.get("DIFY_CONSOLE_PASSWORD")
        self.token = None
        self.csrf = None
        # Dify 1.16.1 现场实测：/console/api/login 的响应体只有 {"result":"success"}，
        # access_token / refresh_token / csrf_token 全部走 Set-Cookie；且此后每一个
        # 已认证请求都必须带 X-CSRF-Token 头，否则一律 401 "CSRF token is missing or invalid"。
        # 因此必须用 cookie jar 打开器，并从 cookie 里取 token。
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj))

    def login(self):
        if not (self.email and self.pw):
            raise RuntimeError(
                "缺少 Dify Console 凭据。设置 DIFY_CONSOLE_EMAIL / DIFY_CONSOLE_PASSWORD，"
                "或用 DIYU_M4_DIFY_ENV 指向包含它们的 .env。凭据只在内存中使用。")
        body = self._req("POST", "/console/api/login", {
            "email": self.email,
            "password": base64.b64encode(self.pw.encode()).decode(),
            "language": "zh-Hans", "remember_me": True}, auth=False)
        ck = {c.name: c.value for c in self.cj}
        # 先按「token 在响应体里」取（其它 Dify 版本的形状），取不到再走 cookie。
        self.token = (body.get("data") or {}).get("access_token") or ck.get("access_token")
        self.csrf = ck.get("csrf_token")
        if not self.token:
            raise RuntimeError("登录失败：响应体 %s；cookie 名 %s"
                               % (json.dumps(body)[:120], sorted(ck)))
        if not self.csrf:
            raise RuntimeError("登录成功但没拿到 csrf_token cookie；后续写入必然 401。cookie 名 %s"
                               % sorted(ck))
        return True

    def _req(self, method, path, payload=None, auth=True, raw_files=None):
        url = self.base + path
        data = None
        headers = {}
        if raw_files is not None:
            boundary = "----M4Boundary" + hashlib.md5(path.encode()).hexdigest()[:12]
            parts = []
            for k, v in (payload or {}).items():
                parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v))
            for k, (fn, content) in raw_files.items():
                parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
                             "Content-Type: application/octet-stream\r\n\r\n%s\r\n" % (boundary, k, fn, content))
            parts.append("--%s--\r\n" % boundary)
            data = "".join(parts).encode("utf-8")
            headers["Content-Type"] = "multipart/form-data; boundary=%s" % boundary
        elif payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method)
        for k, v in headers.items():
            req.add_header(k, v)
        if auth and self.token:
            req.add_header("Authorization", "Bearer " + self.token)
        if auth and self.csrf:
            req.add_header("X-CSRF-Token", self.csrf)
        try:
            with self.opener.open(req, timeout=120) as resp:
                txt = resp.read().decode()
                return json.loads(txt) if txt.strip() else {}
        except urllib.error.HTTPError as e:
            txt = e.read().decode()
            raise RuntimeError("HTTP %s %s -> %s" % (e.code, path, txt[:300]))

    def import_dsl(self, yaml_text, app_id=None):
        payload = {"mode": "yaml-content", "yaml_content": yaml_text}
        if app_id:
            payload["app_id"] = app_id
        return self._req("POST", "/console/api/apps/imports", payload)

    def publish(self, app_id):
        return self._req("POST", "/console/api/apps/%s/workflows/publish" % app_id, {})

    def list_apps(self):
        return self._req("GET", "/console/api/apps?page=1&limit=100")

    def create_workflow_tool(self, workflow_app_id, name, label, params):
        return self._req("POST", "/console/api/workspaces/current/tool-provider/workflow/create", {
            "workflow_app_id": workflow_app_id, "name": name, "label": label,
            "icon": {"content": "🧩", "background": "#E4FBCC"},
            "description": "M4 v1.3 TEST 能力后继应用", "parameters": params, "privacy_policy": "",
        })

    def list_workflow_tools(self):
        return self._req("GET", "/console/api/workspaces/current/tools/workflow")


# ---------------------------------------------------------------- 阶段
def record(name, obj):
    os.makedirs(EVID, exist_ok=True)
    p = os.path.join(EVID, name)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("evidence -> %s" % os.path.relpath(p, ROOT))


def cmd_preflight():
    diffs = protected_integrity()
    existing = existing_m4_apps()
    print("受保护应用完整性：%s" % ("零变化" if not diffs else "**发生变化，禁止写入**"))
    for d in diffs:
        print("   [DIFF]", d)
    print("已存在的 M4 v1.3 TEST 对象：%d" % len(existing))
    for a in existing:
        print("   -", a["id"], a["name"])
    print("将要写入的对象：")
    for key, path in DSL_FILES:
        print("   - %-22s %s" % (key, os.path.relpath(path, ROOT)))
    print("   - %-22s %s" % ("capability_seam", os.path.relpath(SEAM_FILE, ROOT)))
    print("   - %-22s %s" % ("founder_canvas", os.path.relpath(CANVAS_FILE, ROOT)))
    record("M4_DIFY_PREFLIGHT.json", {
        "protected_integrity_diffs": diffs,
        "protected_integrity_ok": not diffs,
        "existing_m4_objects": existing,
        "planned_writes": [k for k, _ in DSL_FILES] + ["capability_seam", "founder_canvas"],
        "write_allowed": not diffs,
    })
    return 0 if not diffs else 1


def cmd_publish():
    diffs = protected_integrity()
    if diffs:
        print("中止：受保护应用已发生变化，禁止写入。")
        for d in diffs:
            print("   [DIFF]", d)
        return 1

    c = Console()
    c.login()
    before = {a["name"]: a["id"] for a in existing_m4_apps()}

    results = {}
    for key, path in DSL_FILES + [("capability_seam", SEAM_FILE), ("founder_canvas", CANVAS_FILE)]:
        yaml_text = open(path, encoding="utf-8").read()
        content_hash = hashlib.sha256(yaml_text.encode()).hexdigest()
        import yaml as _y
        app_name = _y.safe_load(yaml_text)["app"]["name"]
        prior_id = before.get(app_name)

        rollback = {"app_name": app_name, "prior_app_id": prior_id,
                    "prior_published_workflow": None}
        if prior_id:
            rows = psql("SELECT workflow_id, (SELECT md5(graph) FROM workflows w WHERE w.id=a.workflow_id) "
                        "FROM apps a WHERE a.id='%s';" % prior_id)
            if rows:
                rollback["prior_published_workflow"] = rows[0]

        print("[write] %-22s idempotency_key=%s prior=%s" % (key, app_name, prior_id or "NEW"))
        try:
            resp = c.import_dsl(yaml_text, app_id=prior_id)
            status = "STARTED"
            app_id = (resp.get("app_id") or resp.get("id")
                      or (resp.get("data") or {}).get("app_id"))
        except Exception as exc:                      # noqa: BLE001
            print("   写入返回异常：%s" % exc)
            print("   按 N-24：先查目标系统副作用，不盲重放。")
            after = {a["name"]: a["id"] for a in existing_m4_apps()}
            app_id = after.get(app_name)
            status = "UNKNOWN_THEN_CONFIRMED" if app_id else "FAILED"
            resp = {"error": str(exc)}

        if app_id:
            c.publish(app_id)
            rows = psql("SELECT a.workflow_id, md5(w.graph) FROM apps a "
                        "JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % app_id)
            confirmed = rows[0] if rows else None
            status = "EXECUTED_CONFIRMED_BY_TARGET" if confirmed else "PUBLISHED_UNCONFIRMED"
        else:
            confirmed = None

        results[key] = {"app_name": app_name, "app_id": app_id, "status": status,
                        "dsl_sha256": content_hash, "rollback_anchor": rollback,
                        "target_confirmation": confirmed, "raw": resp if isinstance(resp, dict) else {}}

    post = protected_integrity()
    record("M4_DIFY_PUBLISH.json", {
        "results": results,
        "protected_integrity_after": post,
        "protected_integrity_ok_after": not post,
    })
    print("受保护应用写后完整性：%s" % ("零变化" if not post else "**变化，需立即上报**"))
    return 0 if not post else 1


TOOL_PARAMS = [
    {"name": "capability_call", "form": "llm", "required": True,
     "description": "统一业务能力外壳", "type": "string"},
    {"name": "professional_input", "form": "llm", "required": True,
     "description": "本能力专业输入", "type": "string"},
    {"name": "entry", "form": "llm", "required": False,
     "description": "能力调用意图给出的入口", "type": "string"},
    {"name": "run_mode", "form": "llm", "required": False,
     "description": "运行模式", "type": "string"},
    {"name": "example_reference_requested", "form": "llm", "required": False,
     "description": "是否请求案例参考 YES/NO", "type": "string"},
]


def params_from_start(dsl_path):
    """工具参数直接从该应用 start 节点的变量派生，不用硬编码清单。

    现场教训（2026-08-26）：硬编码的 TOOL_PARAMS 里有 `run_mode`，
    统一接缝应用的 start 节点没有这个变量，Dify 直接 400 `variable not found`。
    参数清单只有一个真源——应用自己的 start 节点，从那里派生就不会漂移。"""
    import yaml as _y
    with open(dsl_path, encoding="utf-8") as fh:
        d = _y.safe_load(fh)
    for n in d["workflow"]["graph"]["nodes"]:
        if n["data"].get("type") == "start":
            return [{"name": v["variable"], "form": "llm",
                     "required": bool(v.get("required")), "type": "string",
                     "description": v.get("label") or v["variable"]}
                    for v in n["data"].get("variables", [])]
    raise RuntimeError("找不到 start 节点：%s" % dsl_path)


def resolve_provider(c, app_id):
    """provider_id 由目标系统重新读取确认，不从 create 的返回体里猜。

    现场教训（2026-08-26）：Dify 1.16.1 的 workflow tool create 返回体里
    既没有 `workflow_tool_id` 也没有顶层 `id`，照返回体取会得到 PENDING_PUBLISH，
    而工具其实已经建好了——那会把「已成功」误判成「未绑定」。
    写后由目标系统确认（Prompt §13 第 4 条）。"""
    t = c.list_workflow_tools()
    items = t if isinstance(t, list) else (t.get("data") or [])
    for it in items:
        if it.get("workflow_app_id") == app_id:
            return it.get("id") or "PENDING_PUBLISH"
    return "PENDING_PUBLISH"


def cmd_rebind():
    """N-20：子应用发布后，父接缝的 provider 必须重绑到后继版本；未重绑不得 PASS。"""
    pub_path = os.path.join(EVID, "M4_DIFY_PUBLISH.json")
    if not os.path.exists(pub_path):
        print("缺少 M4_DIFY_PUBLISH.json，先跑 publish。")
        return 1
    pub = json.load(open(pub_path, encoding="utf-8"))["results"]

    c = Console()
    c.login()
    existing_tools = c.list_workflow_tools()
    by_app = {}
    for t in (existing_tools if isinstance(existing_tools, list) else existing_tools.get("data", [])):
        if t.get("workflow_app_id"):
            by_app[t["workflow_app_id"]] = t

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "m4build", os.path.join(DC_WF, "DIYU_M4_DSL_BUILD_v0.1.py"))
    m4build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m4build)

    bindings = {}
    for cap in m4build.CAPABILITIES:
        key = cap["key"]
        app_id = pub.get(key, {}).get("app_id")
        if not app_id:
            print("[skip] %s 未发布成功，provider 保持 PENDING_PUBLISH" % key)
            bindings[key] = {"provider_id": "PENDING_PUBLISH", "app_id": "PENDING_PUBLISH",
                             "published_workflow_id": "PENDING_PUBLISH", "tool_name": cap["tool_name"]}
            continue
        if app_id not in by_app:
            c.create_workflow_tool(
                app_id, cap["tool_name"], cap["app_name"],
                params_from_start(os.path.join(cap["out_dir"], cap["out_file"])))
        provider_id = resolve_provider(c, app_id)      # 写后由目标系统确认
        rows = psql("SELECT workflow_id FROM apps WHERE id='%s';" % app_id)
        bindings[key] = {"provider_id": provider_id, "app_id": app_id,
                         "published_workflow_id": rows[0] if rows else "UNKNOWN",
                         "tool_name": cap["tool_name"]}
        print("[bind] %-22s provider_id=%s" % (key, provider_id))

    with open(BINDINGS, "w", encoding="utf-8") as fh:
        json.dump(bindings, fh, ensure_ascii=False, indent=2, sort_keys=True)

    # 用真实 provider_id 重生成父接缝并重新发布
    seam = m4build.build_seam_app()
    m4build._dump(SEAM_FILE, seam)
    seam_text = open(SEAM_FILE, encoding="utf-8").read()
    seam_app_id = pub.get("capability_seam", {}).get("app_id")
    c.import_dsl(seam_text, app_id=seam_app_id)
    if seam_app_id:
        c.publish(seam_app_id)

    # 接缝本身也要注册成 workflow tool，供 Founder 画布调用
    if seam_app_id:
        if seam_app_id not in by_app:
            c.create_workflow_tool(seam_app_id, "diyu_m4_capability_seam",
                                   "DIYU %s · Capability Seam" % APP_TAG,
                                   params_from_start(SEAM_FILE))
        bindings["_seam"] = {
            "provider_id": resolve_provider(c, seam_app_id),   # 写后由目标系统确认
            "app_id": seam_app_id, "tool_name": "diyu_m4_capability_seam",
        }
        with open(BINDINGS, "w", encoding="utf-8") as fh:
            json.dump(bindings, fh, ensure_ascii=False, indent=2, sort_keys=True)

        canvas = m4build.build_founder_canvas()
        canvas_path = os.path.join(DC_WF, "DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml")
        m4build._dump(canvas_path, canvas)
        canvas_app_id = pub.get("founder_canvas", {}).get("app_id")
        c.import_dsl(open(canvas_path, encoding="utf-8").read(), app_id=canvas_app_id)
        if canvas_app_id:
            c.publish(canvas_app_id)

    # 重绑后必须复验：父 provider 指向后继而不是旧版
    stale = [k for k, v in bindings.items() if v["provider_id"] == "PENDING_PUBLISH"]
    record("M4_DIFY_REBIND.json", {
        "bindings": bindings,
        "seam_app_id": seam_app_id,
        "unresolved_providers": stale,
        "rebind_complete": not stale,
        "note": "未重绑的 provider 一律不得据以宣称入口可达或 Runtime 保真成立（N-20）。",
    })
    return 0 if not stale else 1


def cmd_confirm():
    diffs = protected_integrity()
    apps = existing_m4_apps()
    print("受保护应用完整性：%s" % ("零变化" if not diffs else "**变化**"))
    for d in diffs:
        print("   [DIFF]", d)
    print("M4 v1.3 TEST 对象：%d" % len(apps))
    for a in apps:
        rows = psql("SELECT a.workflow_id, md5(w.graph), w.updated_at FROM apps a "
                    "LEFT JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % a["id"])
        print("   - %s | %s | %s" % (a["id"], a["name"], rows[0] if rows else "UNPUBLISHED"))
    record("M4_DIFY_CONFIRM.json", {"protected_integrity_diffs": diffs,
                                    "protected_integrity_ok": not diffs,
                                    "m4_objects": apps})
    return 0 if not diffs else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "preflight"
    fn = {"preflight": cmd_preflight, "publish": cmd_publish,
          "rebind": cmd_rebind, "confirm": cmd_confirm}.get(cmd)
    if not fn:
        print(__doc__)
        sys.exit(2)
    sys.exit(fn())
