#!/usr/bin/env python3
"""Source fragments for the bounded GAP-01 decisive-question successor."""

from __future__ import annotations

ACTION_PROMPT_APPEND = r'''

────────── 模糊内容请求的决定性分叉 ──────────

5. 用户只说想在本周或近期“发点东西／做些内容”，并把决定交给系统，但没有明确要求整段时间的
   排期、节奏或阶段计划，也没有给出具体商品、题目或内容方向时，不得仅凭时间词猜成 CAMPAIGN。
   这时“先做整体安排”与“先围绕具体商品或内容方向做一条内容”会产生不同结果，应判
   `AMBIGUOUS`，并只问这一个路线分叉。不得追问用户已经表达的本周范围，也不得替用户选择方向。
6. 上一轮若问的是上述路线分叉，本轮用户给出具体商品、受众、问题、期望改变或表达边界，视为
   对“具体内容/主推方向”的有效回答。应沿用同一任务，进入最匹配的内容能力；不得重复上一问，
   不得要求用户重述“本周想发内容”。
7. 用户明确要求整周排期、发布节奏、阶段计划或一波战役时，照常判 `CAMPAIGN`；用户已经给出
   具体商品或题目时，照常判对应内容能力。不能把本规则扩大成所有短输入都要反问。
'''


ROUTE_HELPER = r'''

def _scope_question(user_query, task_text, picked, action):
    """Return one route-changing question for an underspecified content request.

    This is a semantic class guard, not a frozen-sentence matcher.  It requires a
    content-production wish plus delegated choice, while excluding explicit
    campaign planning and concrete content anchors.
    """
    if picked or action != "NONE":
        return ""
    text = re.sub(r"\s+", "", "%s%s" % (user_query or "", task_text or ""))
    wants_content = bool(re.search(r"(?:发|做|弄|准备|想要).{0,6}(?:内容|东西|帖子|视频|图文)", text))
    delegates_choice = bool(re.search(
        r"(?:你看着办|你来定|交给你|帮我定|帮我想|随便安排|不知道(?:发|做)什么)", text
    ))
    explicit_campaign = bool(re.search(
        r"(?:整周|全周|一周).{0,8}(?:排期|节奏|计划|安排)|"
        r"(?:排期|发布节奏|阶段计划|战役|哪天发|每天发|发几条)", text
    ))
    concrete_direction = bool(re.search(
        r"(?:主推|商品|产品|款式|题目|主题|内容方向|围绕.{1,16}(?:做|拍|讲)|"
        r"说给.{1,20}(?:听|看)|希望.{1,20}(?:明白|知道)|做一条)", text
    ))
    if wants_content and delegates_choice and not explicit_campaign and not concrete_direction:
        return "你这次是想先安排一周的整体发布节奏，还是先围绕一个具体商品或内容方向做一条内容？"
    return ""
'''


ROUTE_OVERRIDE = r'''
    scope_q = _scope_question(user_query, task_text, picked, action)
    if scope_q:
        intent = "AMBIGUOUS"
        decisive_q = scope_q
'''
