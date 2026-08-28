#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合同派生 · 否定语义感知的判定原语（规划侧裁决：一次判定器修复）

失效根因（M4-FND-016）：原判定器对 LLM 产出做**逐字字面量匹配**，
匹配串照着 0dcd66f 那一批具体产出调出来，换一批产出即失效；
且不区分「主张 X」与「禁止 X」——把禁令清单里的词当成搬运。

本模块只提供原语，不含任何判据。判据同义词族由**冻结 AC 正文**派生，
写在调用处并逐条标注来源子句，不从观察到的产出反推。

三个原语：
  asserted(text, terms)      —— X 是否被**主张**（否定语境内的出现不算）
  negated(text, terms)       —— X 是否被**否定/拦截**（只认否定语境内的出现）
  absent_as_claim(text, terms) —— X 是否未被主张（= not asserted），用于「不得出现」类子句
"""
import re

# 否定语境标记：出现在命中点邻域即认定该处为「否定/拦截」而非「主张」
NEGATION_MARKERS = [
    "不采用", "不得", "不能", "禁止", "不可", "不应", "不再", "不予", "不作",
    "不沿用", "不引用", "不使用", "不写", "不出现", "不提", "不做",
    "剔除", "淘汰", "排除", "去掉", "移除", "删去",
    "拒绝", "驳回", "未获", "未经", "未登记", "未确认", "未采用", "未采纳",
    "无依据", "无来源", "无授权", "缺乏", "不成立", "超出", "越界",
    "避免", "规避", "不属于", "不构成", "并非", "而非", "不是",
]
# 否定标记的搜索窗口（字符）。取双侧，因中文否定可前置也可后置。
WINDOW = 120


def _spans(text, terms):
    out = []
    for t in terms:
        for m in re.finditer(t if _is_regex(t) else re.escape(t), text or ""):
            lo = max(0, m.start() - WINDOW)
            hi = min(len(text), m.end() + WINDOW)
            ctx = text[lo:hi]
            out.append({
                "term": t, "at": m.start(), "context": ctx,
                "negated": any(n in ctx for n in NEGATION_MARKERS),
            })
    return out


def _is_regex(t):
    return any(c in t for c in r"\[](){}|+*?^$")


def asserted(text, terms):
    """X 被主张：存在至少一处**非否定语境**的出现。"""
    sp = _spans(text, terms)
    pos = [s for s in sp if not s["negated"]]
    return bool(pos), {"total": len(sp), "asserted": len(pos),
                       "negated": len(sp) - len(pos),
                       "sample": (pos or sp)[:2]}


def negated(text, terms):
    """X 被否定/拦截：有出现，且**全部**落在否定语境内。"""
    sp = _spans(text, terms)
    if not sp:
        return False, {"total": 0, "note": "零出现——既非主张也非显式拦截"}
    neg = [s for s in sp if s["negated"]]
    return len(neg) == len(sp), {"total": len(sp), "negated": len(neg),
                                 "asserted": len(sp) - len(neg),
                                 "sample": sp[:2]}


def absent_as_claim(text, terms):
    """X 未被主张：零出现，或全部出现都在否定语境内。"""
    ok, d = asserted(text, terms)
    return (not ok), d


def any_of(text, families):
    """同义词族任一命中（被主张）即成立。families = {名: [terms]}"""
    hit = {}
    for name, terms in families.items():
        ok, d = asserted(text, terms)
        hit[name] = {"ok": ok, **d}
        if ok:
            return True, {"matched_family": name, "detail": hit}
    return False, {"matched_family": None, "detail": hit}
