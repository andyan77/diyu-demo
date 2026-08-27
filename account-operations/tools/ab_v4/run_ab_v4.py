#!/usr/bin/env python3
"""EP-08 v1.2：12 次运行 + **逐场景、单臂、独立随机分配**的盲评包生成。

与 v1.1 的两处实质差别：
  1. B 臂走 v1.3 镜像（`v13/gate_pipeline_v13.py`），与 Dify 图导入同一份源文件；
  2. 盲评包不再是"每场景四份并排"，而是 12 个**不透明单元**，每个单元只含一个场景的一份输出。
     判定者只拿到一个单元，看不到任何其他臂或场景，跨场景观察臂轮换的通道在构造上不存在。

冻结件 §7「禁止重抽」不变：12 次全部保留，失败、超时、空结果一并保留。
判定包生成前逐份机械扫描内部字段泄漏，任一份命中即整轮作废重出（ADDENDUM_002 §2.1）。
"""
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
sys.path.insert(0, os.path.join(SCRATCH, "v13"))
from gate_pipeline_v13 import run_gated            # noqa: E402
from shared_checks import check_leaks, LABEL_SHELL, REF_DISPLAY  # noqa: E402

EVID = os.path.join(WORKTREE, "account-operations/evidence/ep08-module-ab-v13")
OUT_OF_REPO = ("/tmp/claude-1000/-home-faye-diyu-demo/"
               "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3-ab-blind-v4")
UNITS_DIR = os.path.join(OUT_OF_REPO, "units")
SEALED = os.path.join(HERE, "_SEALED_AB_MAPPING_v4.json")
RUBRIC_SRC = os.path.join(WORKTREE, "M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md")

API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"
TEMPERATURE = 0.4
SEED = "m3-ep08-v13-single-arm-blind-2026-08-27-4c71e0ab"
JUDGES_PER_UNIT = 3
MANIFEST = ("<<REFERENCE_MANIFEST>>\n"
            "references/fashion-and-market.md: LOADED\n"
            "references/six-skill-methods.md: LOADED\n"
            "<<END_REFERENCE_MANIFEST>>")


def load_key():
    with open(os.path.join(WORKTREE, ".env"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("no key")


def call(key, system_prompt, user_message):
    payload = {"model": MODEL, "temperature": TEMPERATURE,
               "messages": [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            return {"status": r.status, "body": json.loads(r.read().decode("utf-8")),
                    "elapsed_seconds": round(time.time() - start, 2)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": {"error": e.read().decode("utf-8")},
                "elapsed_seconds": round(time.time() - start, 2)}
    except Exception as e:  # noqa: BLE001
        return {"status": -1, "body": {"error": f"{type(e).__name__}: {e}"},
                "elapsed_seconds": round(time.time() - start, 2)}


def unit_order(n):
    """由冻结种子派生的 (场景,臂) → 不透明单元号 的置换。"""
    h = hashlib.sha256(SEED.encode()).hexdigest()
    idx = sorted(range(n), key=lambda i: h[(i * 5) % 60:(i * 5) % 60 + 5] + f"{i:02d}")
    return idx


def write_rubric():
    src = open(RUBRIC_SRC, encoding="utf-8").read()
    a = src.index("### 5.2 硬门")
    b = src.index("## 6. 验收充分性反查")
    body = ("# 判定 Rubric（摘自已冻结的验收判据，原文，未增删）\n\n" + src[a:b].strip()
            + "\n\n---\n\n> 本文件是给判定者的唯一评分依据。它冻结于本任务全部工程结果之前。\n")
    os.makedirs(OUT_OF_REPO, exist_ok=True)
    with open(os.path.join(OUT_OF_REPO, "rubric.md"), "w", encoding="utf-8") as f:
        f.write(body)


def main():
    key = load_key()
    spec = json.load(open(os.path.join(EVID, "_arms_and_holdouts_v4.json"), encoding="utf-8"))
    arms, holdouts = spec["arms"], spec["holdouts"]
    os.makedirs(EVID, exist_ok=True)

    jobs = [(h["fixture_id"], a) for h in holdouts for a in ("A", "Aplus", "B", "Bprime")]

    def one(job):
        cid, arm = job
        h = [x for x in holdouts if x["fixture_id"] == cid][0]
        um = h["account_context"] + "\n" + h["user_request"]
        sysp = arms[arm]["system_prompt"]
        if arms[arm]["runtime"] == "gated_pipeline":
            text, trace, draft_res, repair_res = run_gated(
                call, key, sysp, um, MANIFEST, h["account_context"])
            rec = {"case_id": cid, "arm": arm, "runtime": "gated_pipeline",
                   "answer_text": text, "gate_trace": trace,
                   "draft_response": draft_res, "repair_response": repair_res,
                   "http_status": draft_res["status"],
                   "elapsed_seconds": draft_res["elapsed_seconds"]
                   + (repair_res["elapsed_seconds"] if repair_res else 0)}
        else:
            res = call(key, sysp, um)
            b = res["body"]
            ch = (b.get("choices") or [{}])[0] if isinstance(b, dict) else {}
            text = (ch.get("message", {}) or {}).get("content", "") if isinstance(ch, dict) else ""
            rec = {"case_id": cid, "arm": arm, "runtime": "single_call",
                   "answer_text": text, "response": res,
                   "http_status": res["status"], "elapsed_seconds": res["elapsed_seconds"]}
        rec.update({"model": MODEL, "provider": "deepseek-direct-api",
                    "temperature": TEMPERATURE, "system_prompt_sha256": arms[arm]["system_prompt_sha256"],
                    "user_message": um, "manifest": MANIFEST,
                    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        with open(os.path.join(EVID, f"{cid}__{arm}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        print(f"  done {cid} {arm} {rec['http_status']} {len(rec['answer_text'])} chars "
              f"{rec['elapsed_seconds']}s", file=sys.stderr, flush=True)
        return rec

    with ThreadPoolExecutor(max_workers=2) as ex:
        recs = list(ex.map(one, jobs))

    bad = [r for r in recs if r["http_status"] != 200 or not r["answer_text"].strip()]
    if bad:
        print(f"\n{len(bad)} run(s) failed — 全部保留，不重抽；本轮不生成判定包。",
              file=sys.stderr)
        for r in bad:
            print("   ", r["case_id"], r["arm"], r["http_status"], file=sys.stderr)
        return

    # ---- ADDENDUM_002 §2.1：判定包生成前逐份扫描内部字段泄漏 ----
    scan = {}
    for r in recs:
        t = r["answer_text"]
        hits = check_leaks(t)
        hits += [f"方括号标签壳: {m.group(0)[:30]}" for m in LABEL_SHELL.finditer(t)]
        hits += [f"参考文件路径: {p}" for p in REF_DISPLAY if p in t]
        scan[f"{r['case_id']}__{r['arm']}"] = hits
    with open(os.path.join(EVID, "_leak_scan_v3.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "四臂输出的内部字段泄漏机械扫描；任一份命中即整轮作废重出。",
                   "scan": scan}, f, ensure_ascii=False, indent=2)
    leaking = {k: v for k, v in scan.items() if v}
    if leaking:
        print("\n内部字段泄漏，判定包不生成（ADDENDUM_002 §2.1）：", file=sys.stderr)
        for k, v in leaking.items():
            print("   ", k, v[:3], file=sys.stderr)
        return

    # ---- 12 个不透明单元 ----
    write_rubric()
    if os.path.exists(UNITS_DIR):
        shutil.rmtree(UNITS_DIR)
    os.makedirs(UNITS_DIR)
    order = unit_order(len(recs))
    mapping, assignments = {}, []
    for slot, ridx in enumerate(order):
        r = recs[ridx]
        uid = f"unit_{slot + 1:02d}"
        d = os.path.join(UNITS_DIR, uid)
        os.makedirs(d)
        h = [x for x in holdouts if x["fixture_id"] == r["case_id"]][0]
        with open(os.path.join(d, "_scenario.md"), "w", encoding="utf-8") as f:
            f.write("# 场景输入（判定者可见）\n\n## 账号上下文\n\n```text\n"
                    + h["account_context"] + "\n```\n\n## 用户本轮请求\n\n```text\n"
                    + h["user_request"] + "\n```\n")
        with open(os.path.join(d, "output.md"), "w", encoding="utf-8") as f:
            f.write(r["answer_text"])
        mapping[uid] = {"case_id": r["case_id"], "arm": r["arm"]}
        for j in range(1, JUDGES_PER_UNIT + 1):
            assignments.append({"unit": uid, "judge": j, "verdict_file": f"verdict_{uid}_j{j}.json"})

    with open(SEALED, "w", encoding="utf-8") as f:
        json.dump({"SEED": SEED, "judges_per_unit": JUDGES_PER_UNIT,
                   "mapping": mapping,
                   "note": "封存映射。执行侧在全部判定文件写定并记录哈希/mtime 之前不读它；"
                           "揭盲由 unblind_v3.py 执行，脚本先断言时序再输出。"},
                  f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_OF_REPO, "assignments.json"), "w", encoding="utf-8") as f:
        json.dump({"units": sorted(mapping), "assignments": assignments},
                  f, ensure_ascii=False, indent=2)

    print(f"\nblind units (OUT OF REPO): {UNITS_DIR}  共 {len(mapping)} 个单元，"
          f"{len(assignments)} 份判定待产出", file=sys.stderr)
    print("sealed mapping:", SEALED, file=sys.stderr)
    print(f"done. {len(recs)} runs, 0 failed, 0 leaking", file=sys.stderr)


if __name__ == "__main__":
    main()
