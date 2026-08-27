"""EP-07 纵向序列（载体 v1.3）。

v1.1 无条件全量覆盖：E07 一份 523 字的零实质输出把上一基线整体挤掉，无人察觉。
v1.2 加了三分支与逐字保留，但基线对象仍然是**从散文里正则抠**出来的——
第 5 轮实测代价：保护分支 12 步 0 次生效，8 个被独立追踪的对象丢了 7 个，
而 `dropped_without_notice` 全程为 `[]`。

v1.3 换掉的是方法：**持续位是结构化对象，端到端不经过散文**。
上一步的投影写出 `standing_positions[]`（JSON），本步模型在审计块里逐条声明，
闸门做集合比对，复检独立复算，投影按声明演进。
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
V12 = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(V12)          # 脚本搬到 v12/ 之后，共用模块仍在上一层
EVID = os.path.join(WORKTREE, "account-operations/evidence/ep07-longitudinal-v13")
SPEC_DIR = os.path.join(WORKTREE, "account-operations/evidence/ep07-longitudinal-v11")
SKILL_DIR = os.path.join(WORKTREE, "account-operations/skills/operating-one-account")
SERVICE_URL = "http://localhost/v1/workflows/run"
APP_ID = "b7fb5b1a-9278-426c-bb8a-f9f288639548"

sys.path.insert(0, SCRATCH)
sys.path.insert(0, V12)
from manifest import build_refs  # noqa: E402
from projection_v13 import project, serialize_positions  # noqa: E402

THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_reasoning(text: str) -> str:
    """Frozen chaining rule: remove the first <think>…</think> block, keep the rest."""
    return THINK.sub("", text, count=1).strip()


def run_workflow(key, inputs, user):
    payload = {"inputs": inputs, "response_mode": "blocking", "user": user}
    req = urllib.request.Request(
        SERVICE_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=1200) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode("utf-8")),
                    "elapsed_seconds": round(time.time() - start, 2)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": {"error": e.read().decode("utf-8")},
                "elapsed_seconds": round(time.time() - start, 2)}
    except Exception as e:  # noqa: BLE001
        return {"status": -1, "body": {"error": f"{type(e).__name__}: {e}"},
                "elapsed_seconds": round(time.time() - start, 2)}


TRANSPORT_RETRY_MAX = 2          # 只对"没有产出"的传输/上游断连重试，不对内容重试
TRANSPORT_RETRY_SLEEP = 20


def _is_transport_failure(res):
    """True 仅当这一次调用根本没产出模型正文（传输层或上游断连），
    而不是'产出了但内容不好'。后者绝不重试——那是择优。"""
    if res["status"] != 200:
        return True
    d = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
    if d.get("status") == "succeeded":
        return False
    err = str(d.get("error") or "")
    return bool(re.search(r"SSLEOFError|UNEXPECTED_EOF|Server Unavailable|"
                          r"Max retries exceeded|Connection|Timeout|timed out", err, re.I))


def run_workflow_with_retry(key, inputs, user):
    attempts = []
    for i in range(TRANSPORT_RETRY_MAX + 1):
        res = run_workflow(key, inputs, f"{user}-a{i}" if i else user)
        d = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
        attempts.append({"attempt": i + 1, "http_status": res["status"],
                         "workflow_status": d.get("status"),
                         "error": d.get("error"), "elapsed_seconds": res["elapsed_seconds"]})
        if not _is_transport_failure(res):
            res["attempts"] = attempts
            return res
        if i < TRANSPORT_RETRY_MAX:
            print(f"    transport failure, retry {i+1}/{TRANSPORT_RETRY_MAX} in "
                  f"{TRANSPORT_RETRY_SLEEP}s: {str(d.get('error'))[:90]}",
                  file=sys.stderr, flush=True)
            time.sleep(TRANSPORT_RETRY_SLEEP)
    res["attempts"] = attempts
    return res


def main():
    key = read(os.path.join(SCRATCH, "m3_app_key.txt")).strip()
    # 输出目录必须存在且为空：非空说明有上一次残留，混进来会造成产地不明
    os.makedirs(EVID, exist_ok=True)
    leftover = [f for f in os.listdir(EVID) if not f.startswith('.')]
    if leftover:
        raise SystemExit(f"REFUSE: {EVID} 非空（{len(leftover)} 项），先清空或换目录，不混跑")

    fashion = read(os.path.join(SKILL_DIR, "references/fashion-and-market.md"))
    spec = json.load(open(os.path.join(SPEC_DIR, "_steps.json"), encoding="utf-8"))
    order = spec["context_slot_order"]
    base = spec["base_context"]

    standing = base["standing_cycle_baseline"]
    positions = list(spec.get("initial_standing_positions") or [])
    if "standing_positions" not in order:
        order = list(order) + ["standing_positions"]
    index = []

    for st in spec["steps"]:
        d = dict(base)
        d.update(st["context_overrides"])
        if st["carry_previous_output_as_standing_baseline"]:
            d["standing_cycle_baseline"] = standing
        d["standing_positions"] = serialize_positions(positions)
        lines = ["[账号上下文 — 由 M2→M3 最小投影提供，非用户口头输入]"]
        lines += [f"{k}: {d[k]}" for k in order]
        account_context = "\n".join(lines) + "\n"

        refs = build_refs(st["include_fashion_ref"], fashion)
        inputs = {"account_context": account_context,
                  "user_request": st["user_request"],
                  "loaded_references": refs}

        print(f"start {st['step_id']} ({st['event_kind']})", file=sys.stderr, flush=True)
        res = run_workflow_with_retry(key, inputs, f"m3-ep07-{st['step_id']}")
        data = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
        raw_out = (data.get("outputs") or {}).get("operating_judgment", "") or ""
        final_only = strip_reasoning(raw_out)

        rec = {"step_id": st["step_id"], "label": st["label"], "event_kind": st["event_kind"],
               "carrier": "dify_workflow", "dify_app_id": APP_ID,
               "model": "deepseek-v4-flash", "provider": "langgenius/deepseek/deepseek",
               "temperature": 0.4,
               "standing_cycle_baseline_in": d["standing_cycle_baseline"],
               "standing_positions_in": positions,
               "workflow_inputs": inputs,
               "http_status": res["status"], "elapsed_seconds": res["elapsed_seconds"],
               "raw_response_body": res["body"],
               "transport_attempts": res.get("attempts"),
               "final_answer_only_after_reasoning_strip": final_only,
               "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(os.path.join(EVID, f"{st['step_id']}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)

        print(f"  done {st['step_id']} {res['status']} {data.get('status')} "
              f"tok={data.get('total_tokens')} {res['elapsed_seconds']}s "
              f"carry_len={len(final_only)}", file=sys.stderr, flush=True)

        index.append({"step_id": st["step_id"], "event_kind": st["event_kind"],
                      "http_status": res["status"], "workflow_status": data.get("status"),
                      "error": data.get("error"), "total_tokens": data.get("total_tokens"),
                      "workflow_run_id": res["body"].get("workflow_run_id") if isinstance(res["body"], dict) else None,
                      "elapsed_seconds": res["elapsed_seconds"],
                      "carried_forward_chars": len(final_only)})

        # 载体给出的承载决定 + 执行侧独立复算，两者不一致就如实记下，不静默采信任何一边
        carry_reported = (data.get("outputs") or {}).get("cycle_state_carry") or "UNKNOWN"
        positions_final = (data.get("outputs") or {}).get("positions_final", "{}")
        new_standing, new_positions, prec = project(
            standing, positions, final_only, carry_reported, positions_final, st["step_id"])
        prec["carry_reported_by_workflow"] = carry_reported
        rec["projection"] = prec
        rec["standing_positions_out"] = new_positions
        with open(os.path.join(EVID, f"{st['step_id']}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        index[-1]["projection_mode"] = prec["mode"]
        index[-1]["cycle_state_carry"] = carry_reported
        index[-1]["objects_before"] = prec["objects_before"]
        index[-1]["objects_not_restated"] = prec["objects_not_restated"]
        print(f"    projection: {prec['mode']} carry={carry_reported} "
              f"before={prec['objects_before']} not_restated={prec['objects_not_restated']}",
              file=sys.stderr, flush=True)

        # 只有传输/上游层面的失败才中断序列；内容层面的失败按新投影规则继续，
        # 因为"一步没产出，序列还能不能诚实地走下去"正是本轮要证明的东西。
        if data.get("status") != "succeeded":
            print(f"ABORT: step {st['step_id']} did not complete at transport level; "
                  f"sequence cannot continue honestly.", file=sys.stderr)
            break
        standing = new_standing
        positions = new_positions

    with open(os.path.join(EVID, "_run_index.json"), "w", encoding="utf-8") as f:
        json.dump({"ecc_id": spec["ecc_id"], "carrier": "dify_workflow", "dify_app_id": APP_ID,
                   "planned_steps": spec["total_steps"], "executed_steps": len(index),
                   "total_tokens": sum((r.get("total_tokens") or 0) for r in index),
                   "steps": index}, f, ensure_ascii=False, indent=2)
    print(f"\ndone. executed {len(index)}/{spec['total_steps']} steps", file=sys.stderr)


if __name__ == "__main__":
    main()
