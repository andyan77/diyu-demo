#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase B 发布后确定性集成验证（零模型调用）。

与 S4_FACT_FLOOR_VERIFY_v1.0.py 的区别：那一份验的是**本地算出来的补丁**，
这一份验的是**线上 provider 实际钉住的那一版代码**——两者相符才叫修复真的到位。

取图口径全部走 provider 的钉：
    tool_workflow_providers.version → workflows.version → graph
因为 Dify 的 workflow-as-tool 是按版本钉死取图的（tool.py:_get_workflow）。

用保存的真实载荷重放 M1/M2 → M3 → Hop → Seam 入口这一段，证明：
  1. 已登记事实在目标节点按来源保留；
  2. 来源真空时仍精确停止；
  3. 其余字段判定逐例不变；
  4. 空产出不再覆盖已确认上游。
Seam → Content Brief 那一跳需要真实调用，属 Phase C，不在本脚本内冒充已验证。
"""
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.abspath(os.path.join(HERE, "..", "evidence", "stages"))
OUT_DIR = os.path.join(EVID, "s4_fact_chain_root_cause")
HOP_APP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"
CANVAS_APP = "85c01f85-a081-43e9-ab09-9993289cc200"

PROTECTED = {
    "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
    "M3": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
    "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
    "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
    "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
    "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df",
    "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
    "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
    "OLD_CANVAS": "2448e4f9-818f-4b88-9311-d18546e97da9",
}
# R0 基线（本轮修复前实测，与更早的 C11 基线一致）
PROTECTED_BASELINE_MD5 = {
    "SEAM": "db49a3da8973d4fdcbe9ecf63bdf7e2a",
    "M3": "cd93757bcf8ad322f3b32fc43b2da3ff",
    "CONTENT_BRIEF": "0c841642a71feedfb327ffb76aec0ddd",
    "CREATIVE_SCRIPT": "a1cd859d5b88d0d025f336665ca94e51",
    "PRODUCTION_DIRECTOR": "964e9a947dc9790d1de82496469689ad",
    "PUBLISHING_PACKAGING": "788c8555aca09e6fa6d979f237f70157",
    "MATRIX": "6cdaeac9cacf69fbeea4bd25e1536ace",
    "CAMPAIGN": "4876dacc43a73741b41c5a3083796347",
    "OLD_CANVAS": "e67147abde10a3fdd0c2043c10cbe266",
}
EXPECT_PINNED_COMPOSE = "6474b902c81c7d91fe8f6143c0a3ece9bbde55dc58b64a822e595b088f2ee855"
EXPECT_CANVAS_GRAPH = "8c9788f293fa7750bea451bd2195ddfb4df7c2647ca00c383ec7c096a4cdc2d1"


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def load_mod(src, name):
    m = types.ModuleType(name)
    exec(compile(src, name, "exec"), m.__dict__)
    return m


results, ok = [], True


def chk(name, cond, detail=""):
    global ok
    ok = ok and bool(cond)
    results.append({"check": name, "result": "PASS" if cond else "FAIL",
                    "detail": str(detail)[:400]})


# ---- 0. 取「provider 实际钉住」的 hop 图 ----
pin = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
pub = psql("select w.version from apps a join workflows w on w.id=a.workflow_id "
           "where a.id='%s';" % HOP_APP)
chk("I-01 hop provider 的钉与应用已发布版一致", pin == pub, "pin=%s published=%s" % (pin, pub))

hop_graph = json.loads(psql("select w.graph from workflows w "
                            "where w.app_id='%s' and w.version='%s';" % (HOP_APP, pin)))
HN = {n["id"]: n for n in hop_graph["nodes"]}
pinned_compose = HN["m5_compose"]["data"]["code"]
chk("I-02 钉住那一版的 m5_compose 就是修复版", sha(pinned_compose) == EXPECT_PINNED_COMPOSE,
    sha(pinned_compose))
chk("I-03 抽取器 prompt/模型/参数未被本轮改动",
    sha(json.dumps(HN["m5_extract"]["data"], ensure_ascii=False, sort_keys=True)) ==
    sha(json.dumps(json.load(io.open(os.path.join(OUT_DIR, "HOP_GRAPH_BEFORE.json"),
                                     encoding="utf-8"))["nodes"][
        [n["id"] for n in json.load(io.open(os.path.join(OUT_DIR, "HOP_GRAPH_BEFORE.json"),
                                            encoding="utf-8"))["nodes"]].index("m5_extract")
    ]["data"], ensure_ascii=False, sort_keys=True)))

before_graph = json.load(io.open(os.path.join(OUT_DIR, "HOP_GRAPH_BEFORE.json"),
                                 encoding="utf-8"))
BN = {n["id"]: n for n in before_graph["nodes"]}
touched = sorted(k for k in HN
                 if json.dumps(HN[k], sort_keys=True, ensure_ascii=False)
                 != json.dumps(BN.get(k), sort_keys=True, ensure_ascii=False))
chk("I-04 hop 图只有 m5_compose 一个节点变化", touched == ["m5_compose"], touched)

MB = load_mod(BN["m5_compose"]["data"]["code"], "compose_before")
MA = load_mod(pinned_compose, "compose_pinned")

# ---- 1. 画布已发布图 ----
canvas = json.loads(psql("select w.graph from apps a join workflows w on w.id=a.workflow_id "
                         "where a.id='%s';" % CANVAS_APP))
csha = sha(json.dumps(canvas, ensure_ascii=False, sort_keys=True))
chk("I-05 画布已发布图 == 干跑构建图", csha == EXPECT_CANVAS_GRAPH, csha)
chk("I-06 画布节点/边 = 47/49", len(canvas["nodes"]) == 47 and len(canvas["edges"]) == 49,
    "%d/%d" % (len(canvas["nodes"]), len(canvas["edges"])))
CN = {n["id"]: n for n in canvas["nodes"]}
chk("I-07 uapp_save 现在读 uapp_persist，不再直读 seam_merge",
    all((it.get("value") or [None])[0] == "uapp_persist"
        for it in CN["uapp_save"]["data"].get("items", [])),
    json.dumps(CN["uapp_save"]["data"].get("items"), ensure_ascii=False)[:300])
PG = load_mod(CN["uapp_persist"]["data"]["code"], "persist_live")

# ---- 2. 保护面零漂移 ----
drift = {}
for k, aid in PROTECTED.items():
    m = psql("select md5(w.graph) from apps a join workflows w on w.id=a.workflow_id "
             "where a.id='%s';" % aid)
    if m != PROTECTED_BASELINE_MD5[k]:
        drift[k] = {"now": m, "baseline": PROTECTED_BASELINE_MD5[k]}
chk("I-08 九个受保护对象零漂移", drift == {}, drift)

# ---- 3. 真实载荷重放（线上钉住的代码） ----
def docs():
    out = []
    for p in sorted(glob.glob(os.path.join(EVID, "s4_continuation01", "S4-CO-T*.json"))):
        out.append(("continuation/" + os.path.basename(p),
                    json.load(io.open(p, encoding="utf-8"))))
    for p in sorted(glob.glob(os.path.join(EVID, "S4-CAP-*-POS.json"))):
        d = json.load(io.open(p, encoding="utf-8"))
        if d.get("attempt") == "attempt03_chain":
            out.append(("attempt03_chain/" + os.path.basename(p), d))
    return out


def payload(doc):
    N = {n["node_id"]: n for n in doc["node_detail"]}
    hi = json.loads(N["uapp_hop"]["inputs"])
    ho = json.loads(N["uapp_hop"]["outputs"])
    raw = json.dumps({"fields": json.loads(ho["extracted_json"]),
                      "_sources": json.loads(ho["source_map_json"])}, ensure_ascii=False)
    return hi, ho, raw


def call(mod, hi, raw):
    return mod.main(raw, hi["target_capability"], hi["m3_judgment"], hi["upstream_delivery"],
                    hi["upstream_capability"], hi["registered_facts"], hi["account_context"],
                    hi["user_request"], hi["focus_fields"])


def gaps(r):
    return [x.strip() for x in re.split(r"[；;]", r["extraction_gaps_text"] or "")
            if x.strip() and x.strip() != "无"]


replay = []
for name, d in docs():
    hi, ho, raw = payload(d)
    rb, ra = call(MB, hi, raw), call(MA, hi, raw)
    replay.append({"case": name, "capability": hi["target_capability"],
                   "registered_facts_len": len(hi["registered_facts"] or ""),
                   "gaps_before": gaps(rb), "gaps_after": gaps(ra),
                   "facts_in_envelope_after": "`facts_registered`" in ra["capability_call"],
                   "others_unchanged": sorted(set(gaps(rb)) - {"facts_registered"}) ==
                                       sorted(set(gaps(ra)) - {"facts_registered"})})

erased = [r for r in replay if "facts_registered" in r["gaps_before"]]
chk("I-09 历史抹除案例（T2/T3）在线上代码下全部消失",
    len(erased) == 2 and all("facts_registered" not in r["gaps_after"]
                             and r["facts_in_envelope_after"] for r in erased),
    [(r["case"], r["gaps_after"]) for r in erased])
chk("I-10 其余字段判定逐例不变", all(r["others_unchanged"] for r in replay),
    [r["case"] for r in replay if not r["others_unchanged"]])

neg = []
for name, d in docs():
    hi, ho, raw = payload(d)
    cap = (hi["target_capability"] or "").upper()
    if "facts_registered" not in MA.REQUIRED_BY_CAPABILITY.get(cap, []):
        continue
    hi2 = dict(hi); hi2["registered_facts"] = ""
    fl = json.loads(ho["extracted_json"]); fl["facts_registered"] = ""
    ra = call(MA, hi2, json.dumps({"fields": fl, "_sources": {}}, ensure_ascii=False))
    neg.append({"case": name, "stops": "facts_registered" in gaps(ra),
                "envelope_has": "`facts_registered`" in ra["capability_call"]})
chk("I-11 负控制：来源真空仍精确停在 facts_registered，且外壳不写该键",
    neg and all(n["stops"] and not n["envelope_has"] for n in neg),
    [n for n in neg if not n["stops"] or n["envelope_has"]])

t2 = [d for n, d in docs() if n.endswith("S4-CO-T2.json")][0]
hi, _ho, raw = payload(t2)
ra = call(MA, hi, raw)
chk("I-12 合成来源可审计：DERIVED(registered_facts)",
    json.loads(ra["source_map_json"]).get("facts_registered") == "DERIVED(registered_facts)")
chk("I-13 外壳中的事实与来源逐字对应，未改写",
    re.sub(r"\s+", " ", hi["registered_facts"].strip())[:500] in ra["capability_call"])
chk("I-14 professional_input 仍原样照带来源",
    hi["registered_facts"] in ra["professional_input"])

# ---- 4. 写回闸门：真实链重放 ----
seq = [("CONTENT_BRIEF", 5593), ("CREATIVE_SCRIPT", 0),
       ("PRODUCTION_DIRECTOR", 0), ("PUBLISHING_PACKAGING", 0)]
pa, pc, hist = "", "", []
for cap, alen in seq:
    r = PG.main("A" * alen, cap, pa, pc)
    pa, pc = r["artifact_to_persist"], r["capability_to_persist"]
    hist.append({"cap": cap, "artifact_len_in": alen, "persist": r["persist_action"],
                 "next_upstream_delivery_len": len(pa), "next_upstream_capability": pc})
chk("I-15 线上写回闸门：5593 字 Brief 不再被空产出抹掉",
    all(h["next_upstream_delivery_len"] == 5593 and
        h["next_upstream_capability"] == "CONTENT_BRIEF" for h in hist[1:]), hist)
chk("I-16 有真产出时正常覆盖",
    PG.main("NEW", "CREATIVE_SCRIPT", "OLD", "CONTENT_BRIEF") ==
    {"artifact_to_persist": "NEW", "capability_to_persist": "CREATIVE_SCRIPT",
     "persist_action": "WRITE_NEW"})
chk("I-17 首轮空产出不造值",
    PG.main("", "CONTENT_BRIEF", "", "")["artifact_to_persist"] == "")

rep = {"phase_b_post_repair_integration": "PASS" if ok else "FAIL",
       "hop_provider_pinned_version": pin,
       "pinned_m5_compose_sha256": sha(pinned_compose),
       "canvas_graph_sha256": csha,
       "checks": results, "hop_replay": replay,
       "persist_chain_replay": hist,
       "model_calls": 0, "dify_writes": 0,
       "not_covered_here": "Seam → Content Brief 那一跳需要真实调用，属 Phase C"}
os.makedirs(OUT_DIR, exist_ok=True)
io.open(os.path.join(OUT_DIR, "PHASE_B_POST_REPAIR_INTEGRATION.json"), "w",
        encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({k: rep[k] for k in
                  ("phase_b_post_repair_integration", "hop_provider_pinned_version",
                   "pinned_m5_compose_sha256", "canvas_graph_sha256", "checks")},
                 ensure_ascii=False, indent=1))
sys.exit(0 if ok else 1)
