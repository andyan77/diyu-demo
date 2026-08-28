#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AC-15 · 隔离等参对照（规划侧裁决 T-04）

裁决要求：保持「同输入 / 同模型 / 同参数 / 同预算」判据不变，
用**隔离的临时对照对象**对齐参数重跑，不改保护应用、不改生产候选参数。

做法：用同一个生成器、同一个 MODEL 常量构建两侧 —— 因此参数**由构造保证逐项相同**：
  A 侧 = 源 Skill v0.1 正文
  B 侧 = M4 后继 Skill 正文
名称统一含 "M4 v1.3 TEST · AC15 EVAL"，evaluation-only，可回滚，结束后保留不删。

副作用纪律：只创建名称含该标记的对象；写前记录九个保护应用锚点，写后复算零变化。
"""
import copy, hashlib, importlib.util, io, json, os, time, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
OUT = os.path.join(EVID, "ac15_eval")


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


B = _mod("dsl", "decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py")
PUB = _mod("pub", "decision-chain/workflows/DIYU_M4_PUBLISH_AND_REBIND_v0.1.py")
FA = _mod("fa", "decision-chain/workflows/DIYU_M4_FORMAL_ATTEMPT_v0.1.py")

TAG = "M4 v1.3 TEST · AC15 EVAL"


def variants():
    """每能力两侧；除 system prompt 的来源 Skill 不同外，其余逐项相同。"""
    for cap in B.CAPABILITIES:
        for side, key in (("A_source", "source_skill"), ("B_m4", "skill_path")):
            c = copy.deepcopy(cap)
            c["skill_path"] = cap[key]
            c["app_name"] = "DIYU %s · %s · %s" % (TAG, cap["capability"], side)
            yield side, cap["capability"], c


def cmd_build():
    os.makedirs(OUT, exist_ok=True)
    man = {"tag": TAG, "kind": "EVALUATION_ONLY_ISOLATED_COMPARISON",
           "oracle_ref": "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md §2 AC-15（判据未改）",
           "ruling": "M4_TECHNICAL_ADJUDICATION_RESPONSE_v0.1 · T-04",
           "param_equality_by_construction": B.MODEL["completion_params"],
           "variants": []}
    for side, capname, c in variants():
        dsl, _bind = B.build_capability_app(c)
        txt = yaml.safe_dump(dsl, allow_unicode=True, sort_keys=True,
                             default_flow_style=False, width=120)
        fn = "AC15_EVAL_%s_%s.yml" % (capname, side)
        io.open(os.path.join(OUT, fn), "w", encoding="utf-8").write(txt)
        # 从生成的 DSL 里直接读回实际 prompt 与参数，不用自报值
        llm = [n for n in dsl["workflow"]["graph"]["nodes"]
               if n.get("data", {}).get("type") == "llm"][0]["data"]
        sysp = [p["text"] for p in llm["prompt_template"] if p["role"] == "system"][0]
        usrp = [p["text"] for p in llm["prompt_template"] if p["role"] == "user"][0]
        man["variants"].append({
            "side": side, "capability": capname, "app_name": c["app_name"], "file": fn,
            "skill_used": c["skill_path"],
            "skill_sha256": hashlib.sha256(io.open(os.path.join(ROOT, c["skill_path"]),
                                                   encoding="utf-8").read().encode()).hexdigest(),
            "system_prompt_sha256": hashlib.sha256(sysp.encode()).hexdigest(),
            "user_prompt_sha256": hashlib.sha256(usrp.encode()).hexdigest(),
            "completion_params": llm["model"]["completion_params"],
            "model": llm["model"]["name"], "dsl_sha256": hashlib.sha256(txt.encode()).hexdigest(),
        })
    # 公平性现场复算：两侧参数、模型、user prompt 必须逐项相同；只允许 system prompt 不同
    ok, diffs = True, []
    for capname in {v["capability"] for v in man["variants"]}:
        a = [v for v in man["variants"] if v["capability"] == capname and v["side"] == "A_source"][0]
        b = [v for v in man["variants"] if v["capability"] == capname and v["side"] == "B_m4"][0]
        for f in ("completion_params", "model", "user_prompt_sha256"):
            if a[f] != b[f]:
                ok = False; diffs.append("%s.%s: %s != %s" % (capname, f, a[f], b[f]))
        if a["system_prompt_sha256"] == b["system_prompt_sha256"]:
            ok = False; diffs.append("%s: 两侧 system prompt 相同，对照无意义" % capname)
    man["fairness_recomputed_ok"] = ok
    man["fairness_diffs"] = diffs
    json.dump(man, io.open(os.path.join(OUT, "AC15_EVAL_MANIFEST.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("构建 %d 个对照对象（6 能力 × 2 侧）" % len(man["variants"]))
    print("等参现场复算: %s%s" % ("PASS" if ok else "FAIL", ("  " + "; ".join(diffs)) if diffs else ""))
    print("-> %s" % os.path.relpath(os.path.join(OUT, "AC15_EVAL_MANIFEST.json"), ROOT))
    return 0 if ok else 1


def cmd_publish():
    c = PUB.Console(); c.login()
    before = PUB.protected_integrity()
    if before:
        print("保护应用写前已有差异，中止：%s" % before); return 1
    man = json.load(io.open(os.path.join(OUT, "AC15_EVAL_MANIFEST.json"), encoding="utf-8"))
    existing = {a["name"]: a["id"] for a in PUB.existing_m4_apps()}
    for v in man["variants"]:
        txt = io.open(os.path.join(OUT, v["file"]), encoding="utf-8").read()
        prior = existing.get(v["app_name"])
        res = c.import_dsl(txt, prior)
        app_id = res.get("app_id") or res.get("app", {}).get("id") or prior
        c.publish(app_id)
        v["app_id"] = app_id
        v["rollback_anchor"] = {"prior_app_id": prior, "dsl_sha256": v["dsl_sha256"]}
        print("[publish] %-46s app_id=%s" % (v["app_name"][-46:], app_id))
    after = PUB.protected_integrity()
    man["protected_integrity_after"] = after
    man["protected_zero_change"] = not after
    json.dump(man, io.open(os.path.join(OUT, "AC15_EVAL_MANIFEST.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("受保护应用写后完整性：%s" % ("零变化" if not after else after))
    return 0


# 冻结对照输入：每能力一份，取自 0dcd66f 候选下已落盘的正式运行 input_text，逐字复用
FROZEN_INPUT = {
    "MATRIX": "FA-05", "CAMPAIGN": "FA-46", "CONTENT_BRIEF": "FA-01",
    "CREATIVE_SCRIPT": "FA-08", "PRODUCTION_DIRECTOR": "FA-06",
    "PUBLISHING_PACKAGING": "FA-07",
}


def _payload(aid):
    for base in (os.path.join(EVID, "runs"), os.path.join(EVID, "candidate_0dcd66f", "runs")):
        p = os.path.join(base, "%s.json" % aid)
        if os.path.exists(p):
            d = json.load(io.open(p, encoding="utf-8"))
            t = d.get("input_text")
            if t:
                return t, hashlib.sha256(t.encode()).hexdigest()
            # FORMAL_ATTEMPT 的记录把输入放在 node_trace[0].inputs
            for nt in (d.get("node_trace") or []):
                ins = (nt or {}).get("inputs") or {}
                t = ins.get("professional_input") or ins.get("capability_call")
                if t:
                    got = hashlib.sha256(t.encode()).hexdigest()
                    dec = d.get("input_sha256")
                    if dec and dec != got:
                        raise SystemExit("%s 输入 sha256 与记录声明不符：%s != %s" % (aid, got, dec))
                    return t, got
    raise SystemExit("找不到 %s 的冻结输入" % aid)


def cmd_run():
    c = PUB.Console(); c.login()
    man = json.load(io.open(os.path.join(OUT, "AC15_EVAL_MANIFEST.json"), encoding="utf-8"))
    if not man.get("fairness_recomputed_ok"):
        print("等参复算未通过，拒绝运行"); return 1
    results = []
    for v in man["variants"]:
        aid = FROZEN_INPUT[v["capability"]]
        payload, ish = _payload(aid)
        token = FA.ensure_api_key(c, v["app_id"])
        t0 = time.time()
        try:
            r = FA.service_call(c.base, token, "/v1/workflows/run",
                                {"inputs": {"capability_call": payload,
                                            "professional_input": payload,
                                            "entry": "", "example_reference_requested": ""},
                                 "response_mode": "blocking", "user": "m4-ac15-eval"})
            err = None
        except Exception as e:
            r, err = {}, str(e)[:500]
        d = r.get("data", {}); o = d.get("outputs") or {}
        rec = {"capability": v["capability"], "side": v["side"], "app_id": v["app_id"],
               "app_name": v["app_name"], "frozen_input_from": aid, "input_sha256": ish,
               "input_text": payload, "completion_params": v["completion_params"],
               "model": v["model"], "system_prompt_sha256": v["system_prompt_sha256"],
               "user_prompt_sha256": v["user_prompt_sha256"], "skill_used": v["skill_used"],
               "run_id": d.get("id"), "status": d.get("status"), "error": err,
               "elapsed_s": round(time.time() - t0, 2),
               "artifact": o.get("artifact"), "user_delivery": o.get("user_delivery"),
               "returns_json": o.get("returns_json"),
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "raw_response": r}
        fn = "AC15_%s_%s.json" % (v["capability"], v["side"])
        json.dump(rec, io.open(os.path.join(OUT, fn), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        results.append({k: rec[k] for k in ("capability", "side", "run_id", "status", "elapsed_s")}
                       | {"artifact_len": len(rec["artifact"] or ""),
                          "delivery_len": len(rec["user_delivery"] or ""), "file": fn})
        print("[%s %-20s] status=%s artifact=%d delivery=%d%s"
              % (v["side"], v["capability"], d.get("status"),
                 len(rec["artifact"] or ""), len(rec["user_delivery"] or ""),
                 "  ERR:" + err[:120] if err else ""))
    man["runs"] = results
    man["all_preserved"] = True
    man["n30_note"] = "12 次全部保留，含失败与残缺产出；不重抽、不挑结果"
    json.dump(man, io.open(os.path.join(OUT, "AC15_EVAL_MANIFEST.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("12 次等参运行完成 -> %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    raise SystemExit({"build": cmd_build, "publish": cmd_publish, "run": cmd_run}[cmd]())
