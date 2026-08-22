#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""笛语 V1 九组质量对照执行器。

按 `V1_QUALITY_COMPARISON_INPUTS_v0.1.md` 冻结的三段 `task_context`，
对以下三条臂各跑一次真实 Dify Workflow：

    deepseek   原三份 Tool 适配 Workflow（同时充当 A 轴独立侧、B 轴 DeepSeek 侧、C 轴 Skill 侧）
    qwen       仅供测试的 Qwen3.8 Max 副本（B 轴对照侧）
    noskill    仅供测试的 No-Skill 强基线副本（C 轴对照侧）

A 轴的集成侧不在此脚本内产生——它来自主 Chatflow 的 S08 真实重放，
由 `--collect-integrated` 从会话变量中原样取出。

凭据从受保护目录按 app_id 前缀读取（`.k_<8位>`），全程不回显。
"""
import argparse, hashlib, json, os, subprocess, sys, time
import urllib.error, urllib.request

BASE = os.environ.get("DIFY_BASE", "http://localhost/v1")
PG = os.environ.get("DIFY_PG_CONTAINER", "docker-db_postgres-1")
KEYDIR = os.environ.get("DIFY_KEY_DIR", "")
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

APPS = {
 "matrix":        {"deepseek": "f8d2be15-2f71-4765-a482-fb62c0e1f3a0",
                   "qwen":     "ced1566c-d83e-49d8-a3c0-7da45fdb8a84",
                   "noskill":  "87eb2e0b-65cd-4aa4-9752-5ba741972bd8"},
 "campaign":      {"deepseek": "a0d92232-0afe-4b77-abb4-5356fd04bc7b",
                   "qwen":     "aad728f0-3b69-4241-a122-7ba83c6f8d23",
                   "noskill":  "a42c9cf0-fbaf-47a3-9961-eb9786f5d1ee"},
 "content_brief": {"deepseek": "eadf8867-6e00-48b8-b3b9-2cb8b89d8834",
                   "qwen":     "86e48b41-864c-4ff2-bcae-158f4396d3ae",
                   "noskill":  "1b7b4023-5f82-49e6-9d35-4e9ae38985b9"},
}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def key_for(app_id):
    p = os.path.join(KEYDIR, ".k_" + app_id[:8])
    if not os.path.exists(p):
        sys.exit("缺少 %s 的 API Key 文件" % app_id[:8])
    return open(p, encoding="utf-8").read().strip()


def psql(sql):
    r = subprocess.run(["docker", "exec", PG, "psql", "-U", "postgres", "-d", "dify", "-tAc", sql],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def run_workflow(app_id, task_context, tag, timeout=1800):
    body = json.dumps({"inputs": {"task_context": task_context},
                       "response_mode": "streaming", "user": "v1-quality-" + tag},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + "/workflows/run", data=body,
                                 headers={"Authorization": "Bearer " + key_for(app_id),
                                          "Content-Type": "application/json"})
    wid, outputs, status, err, elapsed, tokens = None, {}, None, None, None, None
    t0 = time.time()
    try:
        with OPENER.open(req, timeout=timeout) as resp:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                try:
                    ev = json.loads(line[5:].strip())
                except Exception:
                    continue
                if ev.get("event") == "workflow_finished":
                    d = ev.get("data") or {}
                    wid = d.get("id") or d.get("workflow_run_id")
                    outputs = d.get("outputs") or {}
                    status = d.get("status")
                    err = d.get("error")
                    elapsed = d.get("elapsed_time")
                    tokens = d.get("total_tokens")
                elif ev.get("event") == "workflow_started":
                    wid = wid or ((ev.get("data") or {}).get("id"))
                elif ev.get("event") == "error":
                    err = json.dumps(ev, ensure_ascii=False)[:600]
    except urllib.error.HTTPError as e:
        err = "HTTP %s %s" % (e.code, e.read()[:400].decode("utf-8", "replace"))
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:400])
    fo = outputs.get("final_output") or ""
    return {"app_id": app_id, "workflow_run_id": wid, "run_status": status,
            "server_elapsed": elapsed, "total_tokens": tokens, "error": err,
            "wall_seconds": round(time.time() - t0, 2),
            "final_present": outputs.get("final_present"),
            "skill_name": outputs.get("skill_name"), "skill_sha": outputs.get("skill_sha"),
            "model_used": outputs.get("model_used"),
            "fixture_bundle_sha": outputs.get("fixture_bundle_sha"),
            "final_output": fo, "final_chars": len(fo), "final_sha256": sha(fo) if fo else None}


def collect_integrated(conversation_id, outdir):
    """从主 Chatflow 真实重放的会话变量中，原样取出三份集成侧 Artifact 正文。

    修复记录：首版把整张表一次查出、按行切分再按制表符拆列，Artifact 正文含换行，
    于是只截到第一行（matrix 只得 11 字符）。改为**逐个变量单独查**，
    单行单列时 psql 的整段 stdout 就是值本身，多行正文不会被切碎。
    """
    got = {}
    for slot in ("matrix", "campaign", "content_brief"):
        val = psql("select data::json->>'value' from workflow_conversation_variables "
                   "where conversation_id='%s' and data::json->>'name'='%s_artifact';"
                   % (conversation_id, slot))
        val = val[:-1] if val.endswith("\n") else val
        if val:
            got[slot] = {"final_output": val, "final_chars": len(val), "final_sha256": sha(val)}
    p = os.path.join(outdir, "integrated.json")
    json.dump({"conversation_id": conversation_id, "artifacts": got},
              open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("集成侧已收集：%s -> %s" % (sorted(got), p))
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help="frozen_inputs.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--arms", default="deepseek,qwen,noskill")
    ap.add_argument("--skills", default="matrix,campaign,content_brief")
    ap.add_argument("--collect-integrated", default="")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.collect_integrated:
        collect_integrated(a.collect_integrated, a.out)
        return

    frozen = json.load(open(a.inputs, encoding="utf-8"))
    path = os.path.join(a.out, "comparison_runs.jsonl")
    done = set()
    if a.resume and os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("run_status") == "succeeded":
                done.add(r["arm_id"])
        print("resume：已完成 %d 条" % len(done))

    with open(path, "a", encoding="utf-8") as f:
        for skill in [s for s in a.skills.split(",") if s]:
            tc = frozen[skill]["task_context"]
            assert sha(tc) == frozen[skill]["sha256"], "冻结输入 SHA 不符：" + skill
            for arm in [x for x in a.arms.split(",") if x]:
                arm_id = "%s|%s" % (skill, arm)
                if arm_id in done:
                    print("跳过(已完成) %s" % arm_id)
                    continue
                print("运行 %-26s ..." % arm_id, flush=True)
                r = run_workflow(APPS[skill][arm], tc, "%s-%s" % (skill, arm))
                r.update({"arm_id": arm_id, "skill": skill, "arm": arm,
                          "task_context_sha256": sha(tc), "task_context_chars": len(tc)})
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
                print("   status=%s chars=%s model=%s %.1fs %s" % (
                    r["run_status"], r["final_chars"], r["model_used"], r["wall_seconds"],
                    ("ERR " + str(r["error"])[:120]) if r["error"] else ""), flush=True)
    print("完成 →", path)


if __name__ == "__main__":
    main()
