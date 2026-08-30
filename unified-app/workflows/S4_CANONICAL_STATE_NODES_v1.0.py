#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一候选画布的规范任务状态载体｜两个确定性节点的源码。

规划侧 CONTINUE EXECUTION PROMPT v1.0 第五节授权的**唯一一次根修复**。
只改状态载体与直接相关的持久化/接受闸门；不碰 Hop Prompt、不碰六能力专业规则、
不建通用状态服务或数据库。

- `uapp_fields`（接缝之前）：规范字段载体 ＋ 上游 artifact 接受闸门
- `uapp_state`（接缝之后）：artifact 血缘账本的唯一写入者

判据真源：`unified-app/stages/S4_CANONICAL_TASK_STATE_GATE_v1.0.json`
（B1 规范字段表、B2 权威与缺失语义、B3 纠正与失效传播、B4 接受与血缘）

为什么不是"把正则放宽去抓 goal_family"：`goal_family` 在外壳里一直是裸键写法，
放宽正则会把 `provenance:` 块里的元数据一起抓进来，是同一个错误换个方向犯。
本版从 M1 快照的 `business_goal_categories` 结构化真源取值——那才是它的来源。
"""

FIELDS_SRC = r'''
import json
import re

# ============ B1 规范字段表 ============
# 字段身份**显式登记**。外壳里出现但本表未登记的键只披露、不入载体、不回填。
#   k    外壳键          st  BT=反引号 / PL=裸键
#   nest 写回时的嵌套块   only/notfor 按目标能力决定同名键解析到哪个规范身份
#   src  结构化真源（M1 快照路径），等级 D
SPEC = {
    "objective.primary_goal": {"k": "primary_goal", "st": "BT", "nest": "objective",
                               "sc": "CONTENT_TASK", "src": "goal_structure.primary_goal"},
    "objective.goal_family": {"k": "goal_family", "st": "PL", "nest": "objective",
                              "sc": "CONTENT_TASK", "src": "business_goal_categories"},
    "audience.problem": {"k": "audience_problem", "st": "BT", "sc": "CONTENT_TASK"},
    "audience.expected_change": {"k": "expected_change", "st": "BT", "sc": "CONTENT_TASK"},
    "content.promise": {"k": "content_promise", "st": "BT", "sc": "CONTENT_TASK"},
    "content.explicit_non_promise": {"k": "explicit_non_promise", "st": "BT", "sc": "CONTENT_TASK"},
    "content.origin_mode": {"k": "content_origin_mode", "st": "BT", "sc": "CONTENT_TASK"},
    "production.profile": {"k": "production_profile", "st": "BT", "sc": "PRODUCTION"},
    "production.time_window": {"k": "time_window", "st": "BT", "sc": "PRODUCTION",
                               "only": ["PRODUCTION_DIRECTOR"]},
    "operation.time_window": {"k": "time_window", "st": "BT", "sc": "OPERATION",
                              "notfor": ["PRODUCTION_DIRECTOR"]},
    "production.capacity_or_owner": {"k": "capacity_or_owner", "st": "BT", "sc": "PRODUCTION"},
    "cta.contract": {"k": "cta_contract", "st": "BT", "sc": "CONTENT_TASK"},
    "cta.level": {"k": "cta_level", "st": "PL", "sc": "CONTENT_TASK"},
    "delivery.platform": {"k": "platform", "st": "PL", "sc": "DELIVERY"},
    "expression.subject": {"k": "expression_subject", "st": "BT", "sc": "CONTENT_TASK"},
    "expression.subject_and_boundary": {"k": "expression_subject_and_boundary", "st": "BT",
                                        "sc": "CONTENT_TASK"},
    "expression.boundary": {"k": "expression_boundary", "st": "BT", "sc": "CONTENT_TASK"},
    "facts.registered": {"k": "facts_registered", "st": "BT", "sc": "CONTENT_TASK"},
    "facts.publish_permission": {"k": "asset_publish_permission", "st": "BT", "sc": "CONTENT_TASK"},
}
# 整篇 artifact 不是决策字段：走 B4 的接受与血缘账本，永不进字段载体。
ARTIFACT_SLOTS = ["script_or_equivalent_beats", "content_body_or_beats"]
PLAIN_KEYS = set(s["k"] for s in SPEC.values() if s["st"] == "PL")

LEVELS = ["A", "B", "C", "D", "E"]
MISS = ["未明确写出", "未明确说明", "未明确", "未声明", "未提供", "未给出", "未确认", "未指定",
        "未锁定", "无法确定", "尚未确定", "尚未给出", "待确定", "待确认", "待补充", "暂无", "不详",
        "UNDECLARED", "UNKNOWN", "UNSPECIFIED", "NOT_GIVEN", "N/A", "TBD"]
LEGAL_ENUM = ["NO_CTA", "NOT_LOCKED", "NOT_APPLICABLE", "NONE_REQUIRED"]
ACCEPT = ["可以", "行", "没问题", "通过", "认可", "就按这个", "照这个", "就这个", "定了", "OK", "ok"]
NEGATE = "不别未没无"
LCS_K = 8
WRAP_MAX = 24

BT_LINE = re.compile(r"^(\s*)`([A-Za-z_][A-Za-z0-9_]*)`\s*:\s*(.*)$")
PL_LINE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
PUNCT = re.compile(r"[\s，。；、：？！,.;:?!（）()\[\]「」『』“”\"'’‘…—–\-]")
TAIL_PAREN = re.compile(r"[（(【\[].*?[)）】\]]\s*$")


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _np(s):
    return PUNCT.sub("", s or "")


def _fp(s):
    """纯 Python FNV-1a 64。沙箱里不依赖 hashlib；离线判定器可逐位复算。"""
    h = 0xcbf29ce484222325
    for b in (s or "").encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def _missing(v):
    """缺失语义**整值匹配**。子串搜索会把正文里提到 UNDECLARED 的合法长文本误判为缺失。"""
    s = _norm(v).strip(" \t（）()【】[]「」\"'“”‘’")
    if not s:
        return True
    if s.upper() in LEGAL_ENUM:
        return False
    s2 = TAIL_PAREN.sub("", s).strip(" \t（）()【】[]「」\"'“”‘’") or s
    if s2.upper() in LEGAL_ENUM:
        return False
    if s2 in ("无", "-", "—", "–", "NA"):
        return True
    up = s2.upper()
    for tok in MISS:
        i = up.find(tok.upper())
        if i < 0:
            continue
        pre, post = s2[:i], s2[i + len(tok):]
        if len(pre) <= WRAP_MAX and len(post) <= WRAP_MAX \
                and not re.search(r"[，。；;,\n]", pre + post):
            return True
    return False


def _supported(v, uq):
    """本轮用户原话是否支持这个值：存在 >=8 字的公共连续片段。不依赖模型，不针对具体字符串。"""
    a, b = _np(v), _np(uq)
    if not a or not b:
        return False
    if len(a) < LCS_K:
        return a in b
    for i in range(len(a) - LCS_K + 1):
        if a[i:i + LCS_K] in b:
            return True
    return False


def _accepts(uq):
    """接受事件：『这版可以，接着……』。接受词紧邻否定词时不算。"""
    s = _norm(uq)
    bound = "，。；！？,.;!? \u3001\uff1a:"
    for t in ACCEPT:
        i = 0
        while True:
            i = s.find(t, i)
            if i < 0:
                break
            pre_ok = (i == 0) or (s[i - 1] not in NEGATE)
            if len(t) == 1:
                # 单字接受词只在句读边界成立，否则"执行""进行""银行"都会误命中
                pre_ok = pre_ok and (i == 0 or s[i - 1] in bound)
                nxt = s[i + 1:i + 2]
                pre_ok = pre_ok and (nxt == "" or nxt in bound)
            if pre_ok:
                return t
            i += 1
    return ""


def _resolve_key(k, cap):
    cands = [c for c in SPEC if SPEC[c]["k"] == k]
    for c in cands:
        if cap and cap in (SPEC[c].get("only") or []):
            return c
    for c in cands:
        if SPEC[c].get("only"):
            continue
        if cap and cap in (SPEC[c].get("notfor") or []):
            continue
        return c
    return None


def _resolve_gap(g, cap):
    g = re.split(r"[（(]", (g or "").strip())[0].strip()
    if not g or g == "无":
        return None, None
    if g in SPEC:
        return g, g
    cid = _resolve_key(g, cap)
    if cid:
        return cid, g
    if "." in g:
        cid = _resolve_key(g.rsplit(".", 1)[-1], cap)
        if cid:
            return cid, g
    return None, g


def _parse(env):
    lines = (env or "").split("\n")
    found = {}
    for i, ln in enumerate(lines):
        m = BT_LINE.match(ln)
        if m:
            found[m.group(2)] = {"i": i, "ind": m.group(1), "v": m.group(3).strip(), "st": "BT"}
            continue
        m = PL_LINE.match(ln)
        if m and m.group(2) in PLAIN_KEYS:
            found[m.group(2)] = {"i": i, "ind": m.group(1), "v": m.group(3).strip(), "st": "PL"}
    return lines, found


def _render(cid, ind, value):
    s = SPEC[cid]
    return "%s`%s`: %s" % (ind, s["k"], value) if s["st"] == "BT" \
        else "%s%s: %s" % (ind, s["k"], value)


def _shift(found, at, d=1):
    for e in found.values():
        if e["i"] >= at:
            e["i"] += d


def _set(lines, found, cid, value):
    """有行原地替换；无行按登记的样式与嵌套插入。不动其它任何一行。"""
    s = SPEC[cid]
    e = found.get(s["k"])
    if e is not None:
        lines[e["i"]] = _render(cid, e["ind"], value)
        e["v"] = value
        return
    nest = s.get("nest")
    if nest:
        at = None
        for i, ln in enumerate(lines):
            if ln.strip() == nest + ":":
                at = i + 1
                break
        if at is None:
            top = -1
            for x in found.values():
                if x["ind"] == "" and x["i"] > top:
                    top = x["i"]
            at = top + 1 if top >= 0 else len(lines)
            lines.insert(at, nest + ":")
            _shift(found, at)
            at += 1
        lines.insert(at, _render(cid, "  ", value))
        _shift(found, at)
        found[s["k"]] = {"i": at, "ind": "  ", "v": value, "st": s["st"]}
        return
    top = -1
    for x in found.values():
        if x["ind"] == "" and x["i"] > top:
            top = x["i"]
    at = top + 1 if top >= 0 else len(lines)
    lines.insert(at, _render(cid, "", value))
    _shift(found, at)
    found[s["k"]] = {"i": at, "ind": "", "v": value, "st": s["st"]}


def _drop(lines, found, key):
    e = found.get(key)
    if e is None:
        return
    lines.pop(e["i"])
    at = e["i"]
    found.pop(key, None)
    for x in found.values():
        if x["i"] > at:
            x["i"] -= 1


def _fresh(tk):
    return {"task_key": tk, "rev": 0, "fields": {}, "asked": [], "artifacts": [], "events": []}


def main(prev_state_json, task_key, capability_call, gaps_text, target_capability,
         user_request, snapshot_json):
    tk = (task_key or "").strip()
    cap = (target_capability or "").strip()
    uq = user_request or ""
    try:
        st = json.loads(prev_state_json) if (prev_state_json or "").strip() else {}
    except Exception:
        st = {}
    reset = ""
    if not isinstance(st, dict) or st.get("task_key") != tk or not tk:
        st = _fresh(tk)
        reset = "TASK_KEY_CHANGE"
    for key in ("fields", "artifacts", "events", "asked"):
        st.setdefault(key, {} if key == "fields" else [])
    rev = int(st.get("rev") or 0) + 1
    F = st["fields"]
    # 本轮开始前：上一轮的 A 级降为 B（用户更早说过的），本轮的 A 才是"用户本轮说的"
    for e in F.values():
        if e.get("lvl") == "A":
            e["lvl"] = "B"
    asked_prev = [c for c in (st.get("asked") or []) if c in SPEC]

    lines, found = _parse(capability_call)
    gaps, unresolved, gap_raw = [], [], {}
    for g in re.split(r"[；;]", gaps_text or ""):
        cid, raw = _resolve_gap(g, cap)
        if cid:
            if cid not in gaps:
                gaps.append(cid)
            gap_raw[cid] = raw
        elif raw:
            unresolved.append(raw)

    env_vals, env_missing, unspecified = {}, [], []
    for k, e in found.items():
        if k in ARTIFACT_SLOTS:
            continue
        cid = _resolve_key(k, cap)
        if not cid:
            unspecified.append(k)
            continue
        if not e["v"]:
            continue
        if _missing(e["v"]):
            env_missing.append(cid)
        else:
            env_vals[cid] = e["v"]

    # P-08 fail-closed：同一规范身份不能同时非空又出现在缺口里
    contradictions = [c for c in list(env_vals) if c in gaps]
    for c in contradictions:
        env_vals.pop(c, None)

    held, answered, updated, newly, deferred, restated, refined = ([], [], [], [],
                                                                  [], [], [])

    def offer(cid, val, lvl, kind, ref):
        if _missing(val):
            return "MISSING"
        old = F.get(cid)
        rec = {"v": val, "lvl": lvl, "kind": kind, "ref": ref,
               "sc": SPEC[cid]["sc"], "frev": 1, "origin_turn": rev}
        if not old:
            F[cid] = rec
            newly.append(cid)
            return "NEW"
        if _norm(old["v"]) == _norm(val):
            if LEVELS.index(lvl) < LEVELS.index(old.get("lvl", "E")):
                old.setdefault("ref0", old.get("ref"))
                old.setdefault("kind0", old.get("kind"))
                old["lvl"], old["kind"], old["ref"] = lvl, kind, ref
            restated.append(cid)
            return "SAME"
        lo, ln = LEVELS.index(old.get("lvl", "E")), LEVELS.index(lvl)
        if ln > lo or (ln == lo and lvl == "E"):
            held.append(cid)
            return "HELD"
        if lvl == "A" and old.get("lvl") in ("A", "B") and asked_prev and cid not in asked_prev:
            # 本轮存在未决提问时，用户回答不外溢成对其它已确认字段的纠正。
            # 无未决提问时，主动纠正照常成立——B3 不以"系统刚好问过"为前提。
            deferred.append(cid)
            held.append(cid)
            return "DEFERRED_CONFLICT"
        rec["frev"] = int(old.get("frev") or 1) + 1
        if int(old.get("origin_turn") or 0) >= rev:
            # 本轮首次登记的值在本轮被更高权威细化：是首次确认的一部分，
            # 不是对"已确认值"的纠正，不触发依赖产物 STALE。
            rec["frev"] = int(old.get("frev") or 1)
            rec["ref0"] = old.get("ref")
            F[cid] = rec
            refined.append(cid)
            return "REFINED"
        F[cid] = rec
        updated.append(cid)
        return "UPDATED"

    # 1. D 级：M1 结构化真源
    try:
        snap = json.loads(snapshot_json) if (snapshot_json or "").strip() else {}
    except Exception:
        snap = {}
    srev = snap.get("revision")
    for cid, s in SPEC.items():
        p = s.get("src")
        if not p or not isinstance(snap, dict):
            continue
        cur = snap
        for seg in p.split("."):
            cur = cur.get(seg) if isinstance(cur, dict) else None
        if isinstance(cur, list):
            cur = ",".join(str(x).strip() for x in cur if str(x).strip())
        if not isinstance(cur, str) or not cur.strip():
            continue
        offer(cid, cur.strip(), "D", "M1_SNAPSHOT", "M1_SNAPSHOT.rev%s.%s" % (srev, p))

    # 2. A/E 级：本轮外壳抽取
    for cid in sorted(env_vals):
        val = env_vals[cid]
        if cid in asked_prev or _supported(val, uq):
            r = offer(cid, val, "A", "USER_UTTERANCE", "TURN%d.user_request" % rev)
            if r in ("NEW", "UPDATED", "SAME"):
                answered.append(cid)
        else:
            offer(cid, val, "E", "MODEL_EXTRACTION",
                  "TURN%d.uapp_hop.%s" % (rev, cap or "-"))

    # 3. 撤回：系统问过的那一项，本轮解析出的是缺失语义
    withdrawn = []
    for cid in asked_prev:
        if cid in env_missing and cid in F:
            F.pop(cid, None)
            withdrawn.append(cid)

    # 4. 接受事件：标记最近一份未接受的产物
    tok = _accepts(uq)
    accepted_now = None
    if tok:
        for a in reversed(st["artifacts"]):
            if not a.get("accepted"):
                a["accepted"] = True
                a["accepted_turn"] = rev
                a["accepted_rev"] = rev
                accepted_now = a
                break

    # 5. 失效传播：被纠正或撤回的字段，使依赖它的产物 STALE
    changed = sorted(set(updated + withdrawn))
    staled = []
    for a in st["artifacts"]:
        if a.get("stale"):
            continue
        dep = a.get("dep") or {}
        hit = [c for c in changed if c in dep]
        if hit:
            a["stale"] = True
            a["stale_reason"] = "FIELD_CHANGED:" + ",".join(hit)
            staled.append("%s@t%s" % (a.get("cap"), a.get("turn")))

    # 6. 上游 artifact 接受闸门：未接受或已 STALE 的不得进入下一能力
    binding, rejected = [], []
    for slot in ARTIFACT_SLOTS:
        e = found.get(slot)
        if e is None or not e["v"]:
            continue
        fp = _fp(_norm(e["v"])[:256])
        rec = None
        for a in st["artifacts"]:
            if a.get("fp") == fp:
                rec = a
                break
        if rec and rec.get("accepted") and not rec.get("stale"):
            binding.append({"slot": slot, "upstream_capability": rec.get("cap"),
                            "fp": fp, "artifact_norm_len": rec.get("nlen"),
                            "produced_turn": rec.get("turn"),
                            "accepted_turn": rec.get("accepted_turn"),
                            "accepted_revision": rec.get("accepted_rev"),
                            "lineage": "BOUND"})
        else:
            why = "NO_LEDGER_MATCH" if not rec else (
                "STALE" if rec.get("stale") else "NOT_ACCEPTED")
            _drop(lines, found, slot)
            rejected.append(slot)
            binding.append({"slot": slot, "fp": fp, "lineage": "REJECTED", "reason": why})

    # 7. 用载体补本轮缺口。只补同一规范身份，且值必须有 source_ref。
    carried, remaining = [], []
    for cid in gaps:
        e = F.get(cid)
        if e and e.get("v") and e.get("ref") and not _missing(e["v"]):
            _set(lines, found, cid, e["v"])
            carried.append(cid)
        else:
            remaining.append(cid)
    # 被维持的字段：外壳里写回已确认值，保证外壳与载体一致
    for cid in sorted(set(held)):
        e = F.get(cid)
        if e:
            _set(lines, found, cid, e["v"])
    remaining_names = [gap_raw.get(c, c) for c in remaining] + unresolved + rejected
    merged_gaps = "；".join(remaining_names) if remaining_names else "无"

    env_fields = {}
    for cid, s in SPEC.items():
        e = found.get(s["k"])
        if e and e["v"] and not _missing(e["v"]) and cid in F:
            env_fields[cid] = F[cid].get("frev", 1)

    st["rev"] = rev
    st["asked"] = remaining
    ev = {"t": rev, "cap": cap, "new": newly, "upd": updated, "ref": refined,
          "held": sorted(set(held)),
          "wd": withdrawn, "carried": carried, "contra": contradictions,
          "accept_token": tok, "staled": staled, "reset": reset}
    st["events"] = (st.get("events") or [])[-59:] + [ev]

    note = ("任务=%s rev=%d 目标=%s｜补齐=%s｜维持=%s｜用户本轮确认=%s｜新登记=%s｜"
            "纠正=%s｜撤回=%s｜矛盾=%s｜上游=%s｜置STALE=%s｜本轮仍缺=%s") % (
        (tk[:8] or "(空)"), rev, cap or "-",
        ",".join(carried) or "无", ",".join(sorted(set(held))) or "无",
        ",".join(sorted(set(answered))) or "无", ",".join(newly) or "无",
        ",".join(updated) or "无", ",".join(withdrawn) or "无",
        ",".join(contradictions) or "无",
        ",".join("%s:%s" % (b["slot"], b["lineage"]) for b in binding) or "无",
        ",".join(staled) or "无", ",".join(remaining_names) or "无")

    return {"capability_call": "\n".join(lines),
            "gaps_text": merged_gaps,
            "pending_state_json": json.dumps(st, ensure_ascii=False),
            "envelope_fields_json": json.dumps(env_fields, ensure_ascii=False),
            "upstream_binding_json": json.dumps(binding, ensure_ascii=False),
            "carried_fields": ",".join(carried),
            "held_fields": ",".join(sorted(set(held))),
            "user_answered_fields": ",".join(sorted(set(answered))),
            "corrected_fields": ",".join(updated),
            "withdrawn_fields": ",".join(withdrawn),
            "contradiction_fields": ",".join(contradictions),
            "deferred_conflict_fields": ",".join(deferred),
            "refined_fields": ",".join(refined),
            "unspecified_keys": ",".join(sorted(unspecified)),
            "stale_artifacts": ",".join(staled),
            "merge_note": note}
'''


STATE_SRC = r'''
import json
import re


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _fp(s):
    h = 0xcbf29ce484222325
    for b in (s or "").encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def main(pending_state_json, envelope_fields_json, new_artifact, new_capability):
    """artifact 血缘账本的唯一写入者。字段侧的判断已在 uapp_fields 做完，这里只登记产物。

    为什么写在接缝之后：接受信号来自本轮用户原话（接缝之前就知道），
    但本轮产物要到接缝之后才存在。两者写同一个会话变量会造成双写入者，
    所以字段侧只产出 pending 状态，产物侧在这里合并成最终状态，由 uapp_save 单点赋值。
    """
    try:
        st = json.loads(pending_state_json) if (pending_state_json or "").strip() else {}
    except Exception:
        st = {}
    if not isinstance(st, dict):
        st = {}
    st.setdefault("artifacts", [])
    st.setdefault("fields", {})
    rev = int(st.get("rev") or 0)
    try:
        dep = json.loads(envelope_fields_json) if (envelope_fields_json or "").strip() else {}
    except Exception:
        dep = {}

    a = (new_artifact or "").strip()
    cap = (new_capability or "").strip()
    action = "NO_NEW_ARTIFACT"
    conflict = ""
    if a and cap:
        n = _norm(a)
        fp = _fp(n[:256])
        prev = None
        for r in st["artifacts"]:
            if r.get("fp") == fp:
                prev = r
                break
        if prev is None:
            st["artifacts"].append({
                "fp": fp, "nlen": len(n), "len": len(a), "cap": cap,
                "task_key": st.get("task_key"), "turn": rev,
                "accepted": False, "accepted_turn": None, "accepted_rev": None,
                "dep": dep, "stale": False, "stale_reason": None})
            action = "APPENDED"
        elif prev.get("cap") != cap:
            # B4：同一 hash 不得挂两个能力身份。冲突登记，不合并、不改写。
            conflict = "%s!=%s" % (prev.get("cap"), cap)
            action = "IDENTITY_CONFLICT"
        else:
            action = "ALREADY_PRESENT"
    st["artifacts"] = st["artifacts"][-24:]
    note = "账本 rev=%d 动作=%s 能力=%s 长度=%d 依赖字段=%d 冲突=%s 累计=%d" % (
        rev, action, cap or "-", len(a), len(dep), conflict or "无", len(st["artifacts"]))
    return {"task_state_json": json.dumps(st, ensure_ascii=False),
            "ledger_action": action,
            "ledger_conflict": conflict,
            "ledger_note": note}
'''
