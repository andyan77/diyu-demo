#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R6 · 被修改节点的确定性测试与保护面回归。零模型调用，只读 Dify。

每条都要能区分：负控制必须复现旧缺陷，正控制必须拦住，干净输入必须不误报。
只有正控制通过、负控制也通过，才说明改动真的起作用而不是判据变松了。
"""
import importlib.util, json, os, subprocess, sys, types
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "decision-chain", "evidence", "m5-final-p0",
                   "FINAL_P0_DETERMINISTIC_TESTS.json")
CAND = os.path.join(ROOT, "decision-chain", "docs",
                    "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.4_FINAL_P0.yaml")

# M5-05 实际产出的用户交付开头，逐字。这是「原失败回归」的被测输入。
FAIL_UD = ("status: READY\n\n从头跑完了。先把你说的两个情况直接对齐：\n\n"
           "**关于账号那块**：按你的要求整轮重跑了。")
CLEAN_UD = ("苏禾号这周的内容简报已经编好了，可以往下走。\n\n"
            "核心判断一句话：穿法能调整一部分，版型适配需要试穿判断。\n\n"
            "需要你定一件事：最终发布平台还没锁定。")
TEMPLATE_LINE = "status: READY | NEEDS_DECISION | BLOCKED_LOCAL"
FIDELITY = "不得把用户的原话当成已执行的事实回述"
M3_MARKS = ["素材撤回的影响面止于依赖它的未发布产出",
            "没有发生的写入不能说成已经发生",
            "关键业务输入缺席时，停在缺口，不替用户选",
            "不得从已登记商品表、上一周期、历史上下文或素材库里挑一个或几个具体商品来顶替"]


def psql(q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", q], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:300])
    return p.stdout.strip()


def node_code(app, node):
    return psql("select n->'data'->>'code' from workflows w join apps a on a.workflow_id=w.id, "
                "jsonb_array_elements(w.graph::jsonb->'nodes') n where a.id='%s' and n->>'id'='%s' "
                "and w.version<>'draft' order by w.created_at desc limit 1;" % (app, node))


def prompts(app):
    g = json.loads(psql("SELECT graph FROM workflows WHERE app_id='%s' AND version<>'draft' "
                        "ORDER BY created_at DESC LIMIT 1;" % app))
    return "\n".join(pt.get("text") or "" for n in g["nodes"]
                     if (n.get("data") or {}).get("type") == "llm"
                     for pt in (n["data"].get("prompt_template") or []))


def load(src, name):
    m = types.ModuleType(name)
    exec(compile(src, name, "exec"), m.__dict__)
    return m


def leaks_of(mod, t):
    base = [p for p in mod.LEAK_PATTERNS if t and p in t]
    if not hasattr(mod, "_STATE_TOKEN"):
        return sorted(set(base))
    ex = sorted({"STATE_WORD:" + m.group(0) for m in mod._STATE_TOKEN.finditer(t)})
    if mod._STATE_LINE.search(t):
        ex.append("STATE_FIELD_LINE")
    return sorted(set(base) | set(ex))


def main():
    rt = importlib.util.spec_from_file_location(
        "rt", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_INTEGRATION_RUNTIME_v0.1.py"))
    RT = importlib.util.module_from_spec(rt); rt.loader.exec_module(RT)
    cand = yaml.safe_load(open(CAND, encoding="utf-8"))
    res, fails = {}, []

    def check(name, ok, detail):
        res[name] = {"pass": bool(ok), "detail": detail}
        if not ok:
            fails.append(name)
        print("  %-46s %s  %s" % (name, "PASS" if ok else "**FAIL**", detail), flush=True)

    # ---------------- T1 泄漏检查器：负控制 / 正控制 / 假阳性
    old = load(node_code(RT.RB_BIND["CONTENT_BRIEF"], "returns_adapter"), "old_ra")
    new = load(node_code(RT.FP_BIND["CONTENT_BRIEF"], "returns_adapter"), "new_ra")
    o = leaks_of(old, FAIL_UD)
    n = leaks_of(new, FAIL_UD)
    c = leaks_of(new, CLEAN_UD)
    check("T1a 负控制：旧检查器对原失败正文漏检", o == [], "旧 leaks=%s" % o)
    check("T1b 正控制：新检查器拦下原失败正文", bool(n), "新 leaks=%s" % n)
    check("T1c 正控制：命中状态词与结构行两类", 
          any(x.startswith("STATE_WORD:READY") for x in n) and "STATE_FIELD_LINE" in n, str(n))
    check("T1d 假阳性：干净中文交付正文零命中", c == [], "leaks=%s" % c)
    check("T1e 旧检查器没有状态词检查", not hasattr(old, "_STATE_TOKEN"), "旧代码无 _STATE_TOKEN")

    # ---------------- T2 六能力共享节点全部改到
    tpl, fid, df = {}, {}, {}
    for capname, app in sorted(RT.FP_BIND.items()):
        if capname in ("SEAM", "M3"):
            continue
        t = prompts(app)
        tpl[capname] = t.count(TEMPLATE_LINE)
        fid[capname] = t.count(FIDELITY)
        df[capname] = ("STATE_WORDS" in (node_code(app, "delivery_finalize") or ""))
    check("T2a 六能力模板 status 行已全部移除", set(tpl.values()) == {0}, str(tpl))
    check("T2b 六能力保真条款各存在一次", set(fid.values()) == {1}, str(fid))
    check("T2c 六能力 delivery_finalize 已补状态词全集", all(df.values()), str(df))

    # ---------------- T3 M3 successor 两段都在
    m3 = prompts(RT.FP_BIND["M3"])
    hit = {k: m3.count(k) for k in M3_MARKS}
    check("T3 M3 successor 两段四条各存在一次", set(hit.values()) == {1}, str(hit))

    # ---------------- T4 保护面：rb 与 legacy 源应用 graph 未变
    drift = {}
    for role, app in sorted(RT.RB_BIND.items()):
        cur = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                   "ORDER BY created_at DESC LIMIT 1;" % app)
        want = cand["protected_source_apps"]["rb_" + role]["graph_md5"]
        if cur != want:
            drift["rb_" + role] = {"frozen": want, "now": cur}
    for role, app in sorted(RT.LEGACY_BIND.items()):
        cur = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                   "ORDER BY created_at DESC LIMIT 1;" % app)
        want = cand["protected_source_apps"]["legacy_" + role]["graph_md5"]
        if cur != want:
            drift["legacy_" + role] = {"frozen": want, "now": cur}
    check("T4 rb 与 legacy 源应用 graph 与冻结值一致", not drift, "漂移=%s" % (drift or "无"))

    # ---------------- T5 候选运行时 graph 与冻结清单一致
    cdrift = {}
    for role, app in sorted(RT.FP_BIND.items()):
        cur = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                   "ORDER BY created_at DESC LIMIT 1;" % app)
        want = cand["modified_successors"][role]["graph_md5"]
        if cur != want:
            cdrift[role] = {"frozen": want, "now": cur}
    check("T5 fp 候选 graph 与冻结清单一致", not cdrift, "漂移=%s" % (cdrift or "无"))

    out = {"suite": "FINAL_P0_DETERMINISTIC_TESTS_v1.0", "model_calls": 0,
           "candidate_commit": cand["git"]["candidate_commit"],
           "bind": RT.BIND_NAME, "results": res,
           "verdict": "PASS" if not fails else "FAIL", "failed": fails}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== %d/%d PASS === SAVED %s" % (len(res) - len(fails), len(res), OUT))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
