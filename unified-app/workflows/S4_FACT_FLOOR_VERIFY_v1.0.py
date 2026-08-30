# -*- coding: utf-8 -*-
"""Phase B 机器验证（离线，零模型调用，零 Dify 写入）。

把 hop 的 m5_compose 与画布的 PERSIST_SRC 当纯函数跑，用**保存的真实载荷**重放。
"""
import hashlib, io, json, os, re, sys, types, glob

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/faye/diyu-demo-worktrees/v1-uapp-progressive-canvas"
EVID = os.path.join(REPO, "unified-app/evidence/stages")

ANCHOR = "    # ---- 组装扁平外壳：只写目标能力真正需要的键 + 不放松边界的附加键 ----"
PATCH = '''    # ---- 第三条允许的合成规则：事实在不在场是确定性事实，不由模型裁决 ----
    # registered_facts 由画布 uapp_ctx 代码节点从「用户本轮上传资料原文」与
    # 「M1 已登记证据条目（带 nature/scope 标签）」确定性拼装，全程不经模型。
    # 它非空 ⇒「本轮有可用的已登记事实」在结构上成立，这是来源绑定的事实，
    # 不是需要专业判断的结论。本函数下面已经把**同一份字节**原样写进 professional_input；
    # 这里据实标为在场，没有引入任何新事实，只是不让抽取器把已在场的来源随机抹成不在场。
    #
    # 实测依据：同一条会话六轮，registered_facts 恒非空（2367/2459/2459/2541/2541/2541），
    # 外壳 facts_registered 却四轮在场、两轮为空（S4-CO-T2/T3）。
    #
    # 边界：来源本身为空时一律不合成，照旧计入缺口——充分性闸门不因此放松。
    # 事实**如何组织成专业输入**仍归抽取器，本规则只兜「在不在场」这一层。
    if "facts_registered" in required and not f["facts_registered"]:
        _reg = _clean(registered_facts)
        if _reg:
            f["facts_registered"] = _reg[:6000]
            smap["facts_registered"] = "DERIVED(registered_facts)"

'''
MARKER = 'smap["facts_registered"] = "DERIVED(registered_facts)"'


def sha(s): return hashlib.sha256(s.encode()).hexdigest()


def load_mod(src, name):
    m = types.ModuleType(name)
    exec(compile(src, name, "exec"), m.__dict__)
    return m


def hop_versions():
    g = json.load(io.open(os.path.join(SCR, "hop_graph.json"), encoding="utf-8"))
    N = {n["id"]: n for n in g["nodes"]}
    before = N["m5_compose"]["data"]["code"]
    assert MARKER not in before, "现场已含补丁，验证前提不成立"
    assert ANCHOR in before, "锚点缺失"
    after = before.replace(ANCHOR, PATCH + ANCHOR, 1)
    return before, after


def turn_docs():
    out = []
    for p in sorted(glob.glob(os.path.join(EVID, "s4_continuation01", "S4-CO-T*.json"))):
        out.append(("continuation/" + os.path.basename(p), json.load(io.open(p, encoding="utf-8"))))
    for p in sorted(glob.glob(os.path.join(EVID, "S4-CAP-*-POS.json"))):
        d = json.load(io.open(p, encoding="utf-8"))
        if d.get("attempt") == "attempt03_chain":
            out.append(("attempt03_chain/" + os.path.basename(p), d))
    return out


def hop_payload(doc):
    N = {n["node_id"]: n for n in doc["node_detail"]}
    hi = json.loads(N["uapp_hop"]["inputs"])
    ho = json.loads(N["uapp_hop"]["outputs"])
    # 抽取器原始输出：证据里保存的是 compose 之后的 extracted_json；
    # 用它作为 extract_raw 等价重放输入（compose 的 _parse 接受扁平 JSON）。
    raw = json.dumps({"fields": json.loads(ho["extracted_json"]),
                      "_sources": json.loads(ho["source_map_json"])}, ensure_ascii=False)
    return hi, ho, raw


def call(mod, hi, raw):
    return mod.main(raw, hi["target_capability"], hi["m3_judgment"], hi["upstream_delivery"],
                    hi["upstream_capability"], hi["registered_facts"], hi["account_context"],
                    hi["user_request"], hi["focus_fields"])


def gaps(r): return [x for x in re.split(r"[；;]", r["extraction_gaps_text"] or "") if x.strip() and x.strip() != "无"]


results, ok = [], True
def chk(name, cond, detail=""):
    global ok
    ok = ok and bool(cond)
    results.append({"check": name, "result": "PASS" if cond else "FAIL", "detail": str(detail)[:400]})


before_src, after_src = hop_versions()
MB, MA = load_mod(before_src, "compose_before"), load_mod(after_src, "compose_after")


# U-01 补丁只增不改：差异必须是**唯一一处连续插入**，且内容逐字等于 PATCH
import difflib as _dl
bl, al = before_src.split("\n"), after_src.split("\n")
_ops = [o for o in _dl.SequenceMatcher(None, bl, al).get_opcodes() if o[0] != "equal"]
_ins = PATCH.split("\n")[:-1]
chk("U-01 唯一一处连续插入，内容逐字等于补丁",
    len(_ops) == 1 and _ops[0][0] == "insert" and al[_ops[0][3]:_ops[0][4]] == _ins,
    "ops=%s 插入行数=%d 期望=%d" % ([o[0] for o in _ops],
                                 (_ops[0][4] - _ops[0][3]) if _ops else -1, len(_ins)))
chk("U-01b 原有每一行都还在",
    _dl.SequenceMatcher(None, bl, al).get_matching_blocks() and
    sum(b.size for b in _dl.SequenceMatcher(None, bl, al).get_matching_blocks()) == len(bl))

# U-02 零案例专用字符串（不得为本场景硬填经营事实）
BAD = ["序里集", "苏禾", "周宁", "初秋", "衣橱", "熟客", "通勤", "XULI"]
hit = [w for w in BAD if w in PATCH]
chk("U-02 无案例专用字符串/经营事实", hit == [], hit)

# U-03 不复制专业语义：补丁只搬运来源，不生成任何字面内容
chk("U-03 补丁不产生新文本内容",
    'f["facts_registered"] = _reg[:6000]' in PATCH and
    not re.search(r'f\["facts_registered"\]\s*=\s*"[^"]', PATCH))

# U-04/05 真实载荷重放
replay = []
for name, doc in turn_docs():
    hi, ho, raw = hop_payload(doc)
    rb, ra = call(MB, hi, raw), call(MA, hi, raw)
    replay.append({
        "case": name, "capability": hi["target_capability"],
        "registered_facts_len": len(hi["registered_facts"] or ""),
        "gaps_before": gaps(rb), "gaps_after": gaps(ra),
        "facts_in_envelope_before": "`facts_registered`" in rb["capability_call"],
        "facts_in_envelope_after": "`facts_registered`" in ra["capability_call"],
        "other_gaps_unchanged": sorted(set(gaps(rb)) - {"facts_registered"}) ==
                                sorted(set(gaps(ra)) - {"facts_registered"}),
    })
chk("U-04 重放：before 复现历史缺口（诊断一致）",
    all(r["gaps_before"] == r["gaps_after"] or "facts_registered" in r["gaps_before"]
        for r in replay))
chk("U-05 修复只影响 facts_registered，其余缺口逐例不变",
    all(r["other_gaps_unchanged"] for r in replay),
    [r["case"] for r in replay if not r["other_gaps_unchanged"]])

erased = [r for r in replay if "facts_registered" in r["gaps_before"]]
chk("U-06 历史抹除案例全部被修复", erased and all(
    "facts_registered" not in r["gaps_after"] and r["facts_in_envelope_after"] for r in erased),
    [(r["case"], r["gaps_after"]) for r in erased])

# U-07 负控制：来源真空时仍精确停止（闸门不放松）
neg = []
for name, doc in turn_docs():
    hi, ho, raw = hop_payload(doc)
    if "facts_registered" not in json.loads(
            json.dumps({"x": 1})) and False:
        pass
    hi2 = dict(hi); hi2["registered_facts"] = ""
    fields = json.loads(ho["extracted_json"]); fields["facts_registered"] = ""
    raw2 = json.dumps({"fields": fields, "_sources": {}}, ensure_ascii=False)
    ra = call(MA, hi2, raw2)
    req = MA.REQUIRED_BY_CAPABILITY.get((hi["target_capability"] or "").upper(), [])
    if "facts_registered" in req:
        neg.append({"case": name, "gaps": gaps(ra),
                    "stops": "facts_registered" in gaps(ra),
                    "envelope_has": "`facts_registered`" in ra["capability_call"]})
chk("U-07 负控制：registered_facts 为空仍精确停在 facts_registered",
    neg and all(n["stops"] and not n["envelope_has"] for n in neg),
    [n for n in neg if not n["stops"] or n["envelope_has"]])

# U-08 幂等：抽取器已填时不覆盖、不重复写
name, doc = [t for t in turn_docs() if t[0].endswith("S4-CO-T4.json")][0]
hi, ho, raw = hop_payload(doc)
rb, ra = call(MB, hi, raw), call(MA, hi, raw)
chk("U-08 抽取器已填时输出逐字节不变",
    json.dumps(rb, sort_keys=True, ensure_ascii=False) ==
    json.dumps(ra, sort_keys=True, ensure_ascii=False))

# U-09 来源绑定可审计
name, doc = [t for t in turn_docs() if t[0].endswith("S4-CO-T2.json")][0]
hi, _ho, raw = hop_payload(doc)
ra = call(MA, hi, raw)
smap = json.loads(ra["source_map_json"])
chk("U-09 合成来源标记为 DERIVED(registered_facts)",
    smap.get("facts_registered") == "DERIVED(registered_facts)", smap.get("facts_registered"))
chk("U-10 外壳里的事实与来源逐字对应（不改写）",
    re.sub(r"\s+", " ", hi["registered_facts"].strip())[:400] in ra["capability_call"])
chk("U-11 professional_input 仍原样照带来源",
    hi["registered_facts"] in ra["professional_input"])

# ---- 画布写回闸门 ----
sys.path.insert(0, os.path.join(REPO, "unified-app/workflows"))
import importlib.util
sp = importlib.util.spec_from_file_location("s4b", os.path.join(REPO, "unified-app/workflows/S4_BUILD_v1.0.py"))
S4B = importlib.util.module_from_spec(sp); sp.loader.exec_module(S4B)
PG = load_mod(S4B.PERSIST_SRC, "persist")

chk("P-01 有真产出时写新值",
    PG.main("BRIEF", "CONTENT_BRIEF", "OLD", "MATRIX") ==
    {"artifact_to_persist": "BRIEF", "capability_to_persist": "CONTENT_BRIEF",
     "persist_action": "WRITE_NEW"})
chk("P-02 空产出时保留上一轮产物与能力（成对保留）",
    PG.main("", "CREATIVE_SCRIPT", "BRIEF_5593", "CONTENT_BRIEF") ==
    {"artifact_to_persist": "BRIEF_5593", "capability_to_persist": "CONTENT_BRIEF",
     "persist_action": "KEEP_PREVIOUS"})
chk("P-03 纯空白产出等同空",
    PG.main("   \n ", "X", "PREV", "PREVCAP")["persist_action"] == "KEEP_PREVIOUS")
chk("P-04 首轮空产出不造值",
    PG.main("", "CONTENT_BRIEF", "", "") ==
    {"artifact_to_persist": "", "capability_to_persist": "", "persist_action": "KEEP_PREVIOUS"})
chk("P-05 不会出现产物与能力身份错配",
    all(PG.main(a, c, pa, pc)["capability_to_persist"] ==
        (c if (a or "").strip() else pc)
        for a, c, pa, pc in [("A", "C1", "P", "C0"), ("", "C1", "P", "C0"), ("", "C1", "", "")]))

# 用真实链重放：conv 637ac1a6 turn2..turn5
seq = [("CONTENT_BRIEF", 5593), ("CREATIVE_SCRIPT", 0), ("PRODUCTION_DIRECTOR", 0),
       ("PUBLISHING_PACKAGING", 0)]
pa, pc, hist = "", "", []
for cap, alen in seq:
    r = PG.main("A" * alen, cap, pa, pc)
    pa, pc = r["artifact_to_persist"], r["capability_to_persist"]
    hist.append({"cap": cap, "artifact_len_in": alen, "persist": r["persist_action"],
                 "upstream_delivery_len_next": len(pa), "upstream_capability_next": pc})
chk("P-06 真实链重放：5593 字 Brief 不再被抹掉",
    all(h["upstream_delivery_len_next"] == 5593 for h in hist[1:]) and
    all(h["upstream_capability_next"] == "CONTENT_BRIEF" for h in hist[1:]), hist)

print(json.dumps({"phase_b_offline": "PASS" if ok else "FAIL",
                  "checks": results, "hop_replay": replay,
                  "persist_chain_replay": hist,
                  "model_calls": 0, "dify_writes": 0},
                 ensure_ascii=False, indent=1))
sys.exit(0 if ok else 1)
