#!/usr/bin/env python3
"""EP-08 v1.4（第 8 轮正式重跑）：12 次运行 + **逐场景、单臂、独立随机分配**的盲评包生成。

与 v1.1 的两处实质差别：
  1. B 臂走 v1.4 镜像（`v14/gate_pipeline_v14.py`），与 Dify 图导入同一份源文件；
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
sys.path.insert(0, os.path.join(SCRATCH, "v14"))
from gate_pipeline_v14 import run_gated            # noqa: E402
from shared_checks import check_leaks, LABEL_SHELL, REF_DISPLAY  # noqa: E402

EVID = os.path.join(WORKTREE, "account-operations/evidence/ep08-module-ab-v14")
# 臂与留出场景**沿用第 7 轮那一份，不重新生成**。Founder 第 7 条要的是
# 「同等基线、同模型、同输入」——重新生成一份等于换了输入，比较就不成立了。
# 臂规格取本轮那一份：留出场景与 A/A+/B′ 三臂**逐字沿用**第 7 轮（哈希相同即为证，
# 由 prepare_ab_v5.py 在生成时机械断言），B 臂重绑到 SKILL.md v1.4。
# 第一次启动时这里指的是第 7 轮那份 v4 —— B 臂因此还是 v1.3 的提示词，
# 等于拿旧候选重跑一遍。发现后立即中止，已产出的 7 份移进 -aborted 并记录。
ARMS_SPEC = os.path.join(WORKTREE,
                         "account-operations/evidence/ep08-module-ab-v14",
                         "_arms_and_holdouts_v5.json")
OUT_OF_REPO = ("/tmp/claude-1000/-home-faye-diyu-demo/"
               "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3-ab-blind-v5")
UNITS_DIR = os.path.join(OUT_OF_REPO, "units")
SEALED = os.path.join(HERE, "_SEALED_AB_MAPPING_v5.json")
RUBRIC_SRC = os.path.join(WORKTREE, "M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md")

API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"
TEMPERATURE = 0.4
SEED = "m3-ep08-v14-single-arm-blind-2026-08-27-9f31d6c2"
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


RESUME = "--resume" in sys.argv


def main():
    key = load_key()
    spec = json.load(open(ARMS_SPEC, encoding="utf-8"))
    arms, holdouts = spec["arms"], spec["holdouts"]
    os.makedirs(EVID, exist_ok=True)

    # ---- 开跑前的写盘契约：先证明每一个落盘目标都写得进去，再花一次 API ----
    # 第一次尝试跑完 12 次调用才在写盘那一行崩掉（沙箱下 worktree 只读），
    # 12 份模型产出未落盘即丢失。这类失败必须发生在花钱之前，不是花完之后。
    for probe_dir in (EVID, OUT_OF_REPO):
        os.makedirs(probe_dir, exist_ok=True)
        probe = os.path.join(probe_dir, ".write_probe")
        try:
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
        except OSError as e:
            raise SystemExit(f"落盘目标不可写，未发起任何调用：{probe_dir}\n  {e}")

    jobs = [(h["fixture_id"], a) for h in holdouts for a in ("A", "Aplus", "B", "Bprime")]

    # 只认传输故障签名，与已冻结的 rerun_transport_failures.py 同一份词表。
    # 模型产出的坏结果（空正文、被闸门判死、内容不好）一律**不**重跑。
    TRANSPORT_SIGNS = ("Server Unavailable", "SSLEOFError", "UNEXPECTED_EOF_WHILE_READING",
                       "Max retries exceeded", "Connection reset", "Read timed out",
                       "IncompleteRead", "Bad gateway", "502", "503", "504")
    MODEL_SIGNS = ("Not all output parameters are validated", "Insufficient Balance",
                   "content_filter", "invalid_param")

    def transport_failure_reason(rec):
        """返回传输故障原文；不是传输故障就返回 None。"""
        if rec.get("http_status") == 200 and (rec.get("answer_text") or "").strip():
            return None
        blob = json.dumps(rec.get("draft_response") or rec.get("response") or {},
                          ensure_ascii=False)
        if any(m in blob for m in MODEL_SIGNS):
            return None
        for sgn in TRANSPORT_SIGNS:
            if sgn in blob:
                return blob[:400]
        return None

    def one(job):
        cid, arm = job
        dst = os.path.join(EVID, f"{cid}__{arm}.json")
        if RESUME and os.path.exists(dst):
            prev = json.load(open(dst, encoding="utf-8"))
            if prev.get("http_status") == 200 and (prev.get("answer_text") or "").strip():
                print(f"  reuse {cid} {arm}（已成功，逐字节沿用，不重跑）",
                      file=sys.stderr, flush=True)
                return prev
            why = transport_failure_reason(prev)
            if why is None:
                raise SystemExit(f"{cid} {arm} 不是传输故障，拒绝重跑（模型产出坏结果属于证据）\n"
                                 f"  http_status={prev.get('http_status')}")
            n = 1
            while os.path.exists(os.path.join(EVID, f"{cid}__{arm}__transport_failure_{n}.json")):
                n += 1
            shutil.copy(dst, os.path.join(EVID, f"{cid}__{arm}__transport_failure_{n}.json"))
            print(f"  RETRY {cid} {arm}（传输故障 #{n}，失败那次已原样保留）：{why[:110]}",
                  file=sys.stderr, flush=True)
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
