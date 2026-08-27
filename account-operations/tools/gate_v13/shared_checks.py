"""载体 v1.2 · 必填项闸门（确定性）。

v1.1 的设计根基错误：整个闸门跑在"模型自报四个触发标志"上，而这正是缺陷一
（`missing[]` 自述不可靠）已经否定的前提。v1.2 把这条原则贯穿到底——

    凡是能从输入里确定性算出来的事实，就不要问模型。

四条修复面：
  A 最低实质产出硬门：零交付不得被盖合规章，且**不得进补齐节点**（补齐不许无中生有）。
  B 触发条件：能从 account_context 算的直接算；算不出的自报缺失或与输入冲突时 fail-closed。
  D 内部字段不得进入用户可见正文：标签整族移出正文，进只给机器看的审计块。
  E 裸标签/空洞标签/装饰性填空：改为"锚定行必须逐字指回正文里一段互不重叠的实质文字"。
"""
import json
import re

__all__ = ['ABSENCE_NEAR', 'ACTION_MARKER', 'ADVISORY_SLOT_SUBJECTS', 'ALWAYS_ITEMS', 'BLANKET_CARRY', 'BODY_KEYWORDS', 'CONDITIONAL_VOID', 'EMPTY_SLOT_VALUES', 'HOLLOW_EXACT', 'LABEL_SHELL', 'LEAK_PATTERNS', 'MIN_ANCHOR_CHARS', 'MIN_BODY_CHARS', 'MIN_NON_REFERENCE_CHARS', 'MIN_SENTENCES', 'NEGATION_BEFORE', 'NOW_MARKER', 'PAST_MARKER', 'POS_NEW_KINDS', 'POS_STATUS', 'PROPOSAL_THESIS', 'PROPOSAL_WINDOW', 'QTY_SUBJECTS', 'REF_ALIASES', 'REF_DISPLAY', 'REF_NEGATION', 'REF_NOUN', 'REF_SENTENCE', 'SHELL_FAMILY', 'SLOT_ABSENCE_VALUE', 'SLOT_NAMES', 'SLOT_SUBJECTS', 'TRIGGER_ITEMS', '_CN_NUM', '_PUNCT', '_SLOT_HEAD', '_negated_at', '_norm', '_nows', '_parse_slots', '_per_week', '_fmt_q', '_qty', '_qty_scan', '_segments', '_slot_filled', 'check_input_contradiction', 'check_items', 'check_leaks', 'check_manifest', 'check_min_output', 'check_positions', 'check_stale_value_override', 'compute_triggers_from_input', 'has_blanket_carry', 'parse_audit', 'parse_positions_declaration', 'parse_standing_positions', 'positive_hit', 'proposal_shape_hit', 'render_body', 'resolve_triggers', 'split_audit']

# ---------------------------------------------------------------- 常量（冻结）

MIN_BODY_CHARS = 200          # 第 4 轮 70 次实测：最低非零正文 523，中位 1781，唯一 <160 的是 G6(=0)
MIN_SENTENCES = 3
MIN_NON_REFERENCE_CHARS = 120  # G6 的全部交付就是一句"参考文件未加载"
MIN_ANCHOR_CHARS = 12

TRIGGER_ITEMS = {
    "explore": ("探索提案", ["探索·不确定性", "探索·最小可逆动作", "探索·支持继续的观察",
                             "探索·推翻信号", "探索·到期或复验", "探索·让位的稳定义务"]),
    "anchor": ("暂定锚点", ["暂定锚点·来源", "暂定锚点·范围", "暂定锚点·不确定性",
                            "暂定锚点·复验触发"]),
    "conflict": ("冲突反馈", ["冲突反馈·冲突在哪", "冲突反馈·各自证据身份",
                              "冲突反馈·为什么保持或改变", "冲突反馈·还需要什么观察"]),
    "notask": ("无内容任务", ["无任务·缺什么", "无任务·谁能补", "无任务·补上后会变成什么",
                              "无任务·现在能做的替代动作"]),
}
ALWAYS_ITEMS = ["参考文件加载状态"]

# 只有这两个触发能从输入确定性算出来；另两个是输出侧选择，只能自报 + fail-closed。
# 措辞 crosscheck 必须带否定极性。SKILL 的 O-5 **要求**模型在不探索时写清
# 「本轮不安排探索」，O-9 要求写清"有依据地保持不变"——不带极性的关键词匹配
# 会把这两句正确表述判成"你其实在探索/其实是无任务"。第 4 轮 70 次实测里，
# 不带极性的版本在 explore 一项上就误报 20 次，真阳 0 次。
BODY_KEYWORDS = {
    "explore": r"探索|试一下|试试|小范围测试|小范围试|验证一下|新方向|新机制|做个实验",
    "notask": r"NO_CONTENT_TASK|不产出内容任务|没有可派发的内容任务",
}
# 出现在同一句段里、且位于关键词**之前**的否定/零量词，使该命中作废
NEGATION_BEFORE = (r"(?:不|无|没有|未|零|不再|不安排|不设|不做|不引入|不需要|不进行|"
                   r"不新增|不提出|不启动|暂不|先不|=\s*0|为 ?0|为零)")
# 命中要算数，还必须有动作性措辞——"提出一个探索"和"说明本轮不探索"是两回事
# 动作性措辞要写得准。实测反例：「删任务 2 → 失去『合身要试』这一到店理由」——
# 「要试」说的是顾客试穿，不是做实验；「我建议不改方向」里的「我建议」也不是探索。
# 因此动作词必须**带上试验对象或试验动词**，不能只匹配一个意图词。
ACTION_MARKER = (r"(?:我(?:想|打算|建议)[^，。；；\n]{0,8}(?:试|跑|做个|做一)|"
                 r"试一(?:次|条|轮|把)|跑一(?:次|条|轮)|先试一|先跑一|"
                 r"安排一(?:次|条)(?:[^，。；\n]{0,6})?(?:试|实验|验证)|"
                 r"小范围(?:跑|试|测)|做一(?:个|次)实验|设一个假设|提出一个假设|"
                 r"先做一条|先上一条)")


# 条件式/未来式的"要不要试"不是本轮的探索提案，是复验触发条款——
# SKILL O-5 恰恰要求写这一句。实测 B07-3「复验触发：出现任一反馈后，重新评估是否要试新方向」。
CONDITIONAL_VOID = (r"是否|要不要|再评估|重新评估|复验触发|下周期|下一轮|后续|将来|以后|"
                    r"届时|之后再|等[^，。]{0,8}再|如果|若|一旦|视情况")


# ---- G-2 第二层：提案形态 --------------------------------------------------
# 第 5 轮的漏检现场：「核心命题是……观察窗口至少一周」——一个动作词都没有，
# 却是一次不折不扣的受控探索提案。ACTION_MARKER 那一版为压误报收紧成"动作性措辞"，
# **收紧后只量了误报（0/70），没量漏检**。这是方法漏，不是运气差。
#
# 改判据：一次探索提案在结构上总要说清两件事——**要验证什么**，以及**验证多久/多少**。
# 两件事出现在同一句段里，才算命中；只有其中一件不算。
# 判据不是我想出来的，是从**逃逸现场原文**反推的。第 5 轮 G-2 的两行逐字是：
#
#   L10  核心命题是：在数据回来之前，用不承诺换取可信，用试穿实拍让观众看到真实上身效果。
#   L13  这条内容发布后要盯的：门店和企业微信预约是否增加、私信里面料疑问是否被接住；观察窗口至少一周。
#
# 关键在于：**产品自己的词汇不是「试一次」，是「核心命题是……；观察窗口……」**，
# 而且这两半落在**不同的行**上。上一版按"同一句段内动作词"去认，认不出来；
# 第一次改判据时按"同一句段内主语 + 度量"去认，同样认不出来——它们本来就不在同一段。
#
# 因此判据是**篇章级共现**：命题标记（在一个未被否定的句段里）+ 观察窗标记。
# 泛化的「假设」「验证」「N 条」不进判据——实测它们在六份完全正常的正向夹具里都出现，
# 拿它们当判据就是造一台误报机（第一版实测：6/6 正向夹具全部误报）。
PROPOSAL_THESIS = (r"核心命题(?:是|为|：|:)|主要假设(?:是|为|：|:)|要验证的是|"
                   r"想验证的是|待验证的命题|本轮的假设是")
PROPOSAL_WINDOW = r"观察窗口|观察窗|观察期(?:为|是|至少)|窗口(?:期|长度)?(?:为|是|至少)"


def proposal_shape_hit(body):
    """篇章级共现：命题 + 观察窗 ⇒ 探索提案。否定极性与条件式否决继续有效（G-1 不回退）。"""
    t = body or ""
    if not re.search(PROPOSAL_WINDOW, t):
        return None
    for seg in _segments(t):
        m = re.search(PROPOSAL_THESIS, seg)
        if not m:
            continue
        if re.search(NEGATION_BEFORE, seg[:m.start()]):
            continue
        if re.search(CONDITIONAL_VOID, seg):
            continue
        return seg.strip()[:60]
    return None


def positive_hit(pattern, body):
    """句段级：命中 = 出现**动作性**措辞（要试/先做/小范围跑…）或主题词，且

      · 该措辞之前 14 字内没有否定或零量词；
      · 整段不是条件式/未来式（是否、要不要、复验触发、下周期…）。

    只匹配主题词（"探索""新方向"）是不够的——SKILL O-5 **要求**模型在不探索时
    写清"本轮不安排探索"，主题词必然出现。真正区分"提出探索"和"声明不探索"的
    是动作性措辞。第 4 轮 70 例实测：只看主题词命中 67/70（全是误报），
    加上极性与条件式之后 0/70 误报，而真实提案仍然命中。
    """
    for seg in _segments(body or ""):
        if re.search(CONDITIONAL_VOID, seg):
            continue
        for m in re.finditer(ACTION_MARKER, seg):
            head = seg[max(0, m.start() - 14):m.start()]
            if re.search(NEGATION_BEFORE, head):
                continue
            return seg.strip()[:60]
        for m in re.finditer(pattern, seg):
            head = seg[max(0, m.start() - 14):m.start()]
            if re.search(NEGATION_BEFORE, head):
                continue
            if re.search(ACTION_MARKER, seg):
                return seg.strip()[:60]
    return None

HOLLOW_EXACT = {"已列明", "已按规则处理", "不适用", "无", "暂无", "同上", "见上",
                "待补充", "略", "N/A", "NA", "未知", "已完成", "符合要求", "已说明"}

# 渲染之后仍然存在的，就是模型在正文里谈自己的内部结构——代码不能替它改。
LEAK_PATTERNS = [
    (r"\[[^\]\n]{0,24}·[^\]\n]{0,24}\]", "方括号内部标签"),
    (r"<<[^>\n]{0,40}>>", "控制标记"),
    (r"</?think>", "推理标记"),
    (r"missing\[\]|assumptions\[\]|primary_job|candidate_status|is_current|"
     r"needs_fix|gate_report|cycle_state_carry|REFERENCE_MANIFEST", "内部字段名"),
    (r"[\w./-]*[\w-]\.md(?![A-Za-z])", "文件路径"),
    (r"(?<![A-Za-z0-9])O-(?:[1-9]|1[01])(?![0-9])", "内部规则号"),
    (r"§\s*\d", "内部章节号"),
    (r"(?<![A-Za-z])AC-\d{2}|ECC-M3|M3-AC-", "治理标识"),
]

# 渲染层与内容层要分开。
#   外观泄漏（方括号标签壳、清单机器值、参考文件路径）——**代码能确定性还原**，
#   那就由代码还原，别退给模型重写；这正是本轮那条原则的应用。
#   内容层泄漏（内部字段名、内部规则号、章节号、验收编号）——模型在谈自己的内部结构，
#   代码替它改就是替它写交付物，只能退回去让它自己说人话。
REF_DISPLAY = {
    "references/fashion-and-market.md": "服装经营与市场参考资料",
    "references/six-skill-methods.md": "既有能力方法参考资料",
    "fashion-and-market.md": "服装经营与市场参考资料",
    "six-skill-methods.md": "既有能力方法参考资料",
}
LABEL_SHELL = re.compile(
    r"`?\[(?:探索|暂定锚点|冲突反馈|无任务|无内容任务|参考文件加载状态)(?:·[^\]\n]{0,24})?\]`?"
    r"\s*[：:]?\s*|(?<![0-9A-Za-z_])`?\[\s*\]`?\s*")


SHELL_FAMILY = {"探索": "explore", "暂定锚点": "anchor", "冲突反馈": "conflict",
                "无任务": "notask", "无内容任务": "notask"}


def render_body(body):
    """把外观层的机器痕迹确定性地还原成人话。只动外观，不动任何一句判断的内容。

    顺带返回它剥掉了哪几族标签——审计块整体缺失时，这是关于"模型自己认为哪些触发命中"
    的**结构性**证据，比正文措辞可靠。
    """
    t = body or ""
    applied, fams = [], set()
    hits = LABEL_SHELL.findall(t)
    n = len(hits)
    if n:
        for m in re.finditer(r"\[(探索|暂定锚点|冲突反馈|无任务|无内容任务)", t):
            fams.add(SHELL_FAMILY[m.group(1)])
        t = LABEL_SHELL.sub("", t)
        applied.append(f"剥掉方括号标签壳 {n} 处（内容保留）")
    for path in sorted(REF_DISPLAY, key=len, reverse=True):
        if path in t:
            t = t.replace(path, REF_DISPLAY[path])
            applied.append(f"参考文件路径改写为自然语言：{path}")
    for a, b in (("NOT_LOADED", "未加载"), ("LOADED", "已加载")):
        t2 = re.sub(r"(?<![A-Za-z_])" + a + r"(?![A-Za-z_])", b, t)
        if t2 != t:
            t = t2
            applied.append(f"清单机器值改写为自然语言：{a}")
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip(), applied, sorted(fams)


# 输入槽位里"这一项确实给了"是机器已知的事实，模型不许说它没给。
# 主语必须紧邻否定短语（≤8 字、不跨逗号/冒号/括号），否则会误伤——第 4 轮 70 例实测里，
# 宽口径版本在 B02-1 / B02-3 / B10-1 / E06 上开了 4 枪，四枪全错：
#   「账号锚点未提供正式 Matrix 产物」说的是 Matrix，不是锚点槽位为空；
#   「三条真实反馈一致指向同一个缺口：…内容缺少上身效果」说的是内容缺口，不是反馈没进来。
SLOT_SUBJECTS = {
    "feedback": r"(?:新?反馈(?:的(?:本体|内容|正文))?|反馈内容|反馈本体)",
    "market_observations": r"(?:市场观察|外部市场证据|市场证据|市场数据)",
    "campaign_overlay": r"(?:Campaign|活动覆盖|覆盖层|活动信息)",
}
# 这两个槽位的自然语言指代太容易和别的东西重名，只记录不阻断；
# 暂定锚点的触发本来就由输入侧算出，不依赖这条检查兜底。
ADVISORY_SLOT_SUBJECTS = {
    "account_anchor": r"(?:账号锚点|锚点信息)",
    "stage_evidence": r"(?:阶段证据|阶段依据)",
}
# 否定短语必须是**"这一项本身没送到"**，不能是**"这一项的内容里没有某个话题"**。
# 实测事故（E07，v1.2 自己造成的）：正文写「三条反馈里没有任何一条提到上身效果或试穿」——
# 这是**真话**（L5 是三色对比互动、L6 是门店顾客变少、L7 是价格有点贵，确实没有一条谈上身效果）。
# 旧口径把 `反馈` + `没有任何` 判成"说槽位缺失"，补齐节点据此把这句真话改成了
# 「反馈里确实有内容提到上身效果或试穿」——**闸门逼出了一句假话**。
# 这正是这道闸门存在的理由的反面，必须写死区分。
ABSENCE_NEAR = (
    r"[^。；;，,：:「」（）()\n]{0,8}?"
    r"(?:还没有(?:进来|给|提供|到)|没有进来|未进来|没有收到|未收到|没给我?|没有给我?|"
    r"未给出|尚未提供|没有提供|未提供|缺了|缺失|为空|不可得)"
    r"(?![^。；;，,\n]{0,12}(?:提到|涉及|包含|说到|谈到|写到|支持|指向|要求|表明|显示))"
)

EMPTY_SLOT_VALUES = {"", "未提供", "无", "无覆盖", "不适用", "尚无", "-", "—", "N/A"}

REF_SENTENCE = r"参考|附件|资料|清单|加载"


# ---------------------------------------------------------------- 小工具

def _nows(s):
    return re.sub(r"\s+", "", s or "")


# 锚定比对用：连标点一起去掉。模型复述自己那句话时经常把「，」写成「,」或多吞一个「的」，
# 那不是"没写"，是抄写噪声。去掉标点之后仍然要求**逐字**，实质要求没有放松。
_PUNCT = re.compile(r"[\s、，。；：！？「」『』（）【】《》〈〉…—–\-·"
                    r",.;:!?()\[\]{}\"'`*_#>~/\\|+=]+")


def _norm(s):
    return _PUNCT.sub("", s or "")


def _segments(text):
    """按句子切分。v1.1 第一版用 ±120 字符窗口，会溢进下一句，误伤过一次。"""
    return [s for s in re.split(r"[。；;！!？?\n]", text or "") if s.strip()]


# M2→M3 最小投影的槽位名（冻结接口）。多行值必须整段归属——
# standing_cycle_baseline 装的是上一轮完整答复，本身就带换行；
# 只取首行会把基线截断成一句话，连续性检查随之整体失效。
SLOT_NAMES = ("account_anchor", "positioning", "platform", "current_task", "stage_evidence",
              "expected_publish_count", "baseline_capacity", "actual_capacity",
              "facts_and_assets", "market_observations", "feedback", "campaign_overlay",
              "expression_permission", "primary_objective", "secondary_objectives",
              "standing_cycle_baseline", "standing_positions")
_SLOT_HEAD = re.compile(r"^\s*(" + "|".join(SLOT_NAMES) + r")\s*:\s?(.*)$")


def _parse_slots(account_context):
    slots, cur = {}, None
    for line in (account_context or "").splitlines():
        m = _SLOT_HEAD.match(line)
        if m:
            cur = m.group(1)
            slots[cur] = m.group(2)
        elif cur is not None:
            slots[cur] += "\n" + line
    return {k: v.strip() for k, v in slots.items()}


SLOT_ABSENCE_VALUE = re.compile(
    r"^\s*(?:未提供|无|空|尚无|缺失|不适用|不详|未知|NOT_APPLICABLE|N/A|-|—|"
    r"无覆盖|无任何|没有任何|尚未|未建立|未登记|暂无)")


def _slot_filled(v):
    """字面白名单不够：`无覆盖`、`无任何外部市场资料`、`缺失：不知道这个号是…`
    这些值本身说的就是"没有"，把它们算成"有内容"会让模型逐字回抄输入反而被判自相矛盾。"""
    t = (v or "").strip()
    if _nows(t) in {_nows(x) for x in EMPTY_SLOT_VALUES}:
        return False
    return not SLOT_ABSENCE_VALUE.match(t)


# ---------------------------------------------------------------- 触发计算

def compute_triggers_from_input(slots):
    """只返回能从输入确定性算出来的；算不出的返回 None（= 不可判）。"""
    out = {"explore": None, "anchor": None, "conflict": None, "notask": None}

    fb = slots.get("feedback", "")
    if "feedback" not in slots:
        out["conflict"] = None                     # 槽位不存在 ⇒ 不可判
    elif not _slot_filled(fb):
        out["conflict"] = False                    # 定死：本轮根本没有反馈，谈不上冲突
    else:
        kinds = set(re.findall(r"kind\s*=\s*([^，,；;\s]+)", fb))
        n_items = len(re.findall(r"反馈[A-Za-z0-9]+\s*[：:]", fb)) or (1 if fb.strip() else 0)
        window_open = bool(re.search(r"尚未结束|未结束|窗口未结束|window_end\s*=\s*[^（(]*（?尚未", fb))
        if (len(kinds) >= 2 or window_open or
                (n_items >= 2 and re.search(r"反而|相反|不一致|冲突|矛盾", fb))):
            out["conflict"] = True
        else:
            # 有反馈但机械特征没命中：内容层面的冲突是语义判断，不装作算得出
            out["conflict"] = None

    anc = slots.get("account_anchor", None)
    if anc is None:
        out["anchor"] = None                      # 槽位根本不存在 ⇒ 不可判，走 fail-closed
    elif not _slot_filled(anc):
        out["anchor"] = True                      # 缺失 ⇒ 必然用暂定锚点
    else:
        pos_line = slots.get("positioning", "")
        blob = anc + " " + pos_line
        if re.search(r"暂定|待确认|未确认|不完整|不明确|新号|空白|尚未建立|缺失|不知道|不清楚|r未建档|没有.*Matrix|无 ?Matrix", blob):
            out["anchor"] = True
        elif re.search(r"已确认", blob):
            out["anchor"] = False                 # 定死：锚点已确认，不存在暂定锚点
        else:
            out["anchor"] = None
    return out


def resolve_triggers(computed, self_reported, body, shell_families=()):
    """输入算出来的压过自报；算不出的 fail-closed。"""
    eff, blocks, notes = {}, [], []
    for k, (cn, _) in TRIGGER_ITEMS.items():
        c, s = computed.get(k), self_reported.get(k)
        if c is True:
            eff[k] = True
            if s is False:
                notes.append(f"{cn}: 输入算出=是，模型自报=否 —— 以输入为准（自报压不下去）")
        elif c is False:
            if s is True:
                eff[k] = False
                notes.append(f"{cn}: 输入定死=否，模型自报=是 —— 以输入为准，该族标注属装饰性填空")
            elif s is False:
                eff[k] = False
            else:
                eff[k] = False
                notes.append(f"{cn}: 自报缺失，但输入可算出=否，按否处理")
        else:                                     # 不可判：只能靠自报 + 正文结构证据
            if s is None:
                # 自报缺失时**不能**一律按触发处理：那会让模型为一个根本不存在的探索提案
                # 编六条内容，正好撞上〈判断主链〉禁止的装饰性填空，也和"补齐不许无中生有"冲突。
                # 改用两条结构性证据：模型自己写了该族标签（渲染层剥掉时记下来的），
                # 或正文里有**肯定式**的动作性提案（该判据在 70 例实测上误报 0）。
                struct = k in (shell_families or ())
                hit = positive_hit(BODY_KEYWORDS.get(k), body) if BODY_KEYWORDS.get(k) else None
                if k == "explore" and not hit:
                    hit = proposal_shape_hit(body)
                eff[k] = bool(struct or hit)
                blocks.append(f"{cn}: 自报缺失 ⇒ 按结构证据判定为"
                              f"{'是' if eff[k] else '否'}"
                              + (f"（正文标签族命中）" if struct else
                                 (f"（正文肯定式措辞：「{hit}」）" if hit else "（无结构证据）"))) 
            elif s is True:
                eff[k] = True
            else:
                pat = BODY_KEYWORDS.get(k)
                hit = positive_hit(pat, body) if pat else None
                if k == "explore" and not hit:
                    hit = proposal_shape_hit(body)
                if hit:
                    eff[k] = True
                    blocks.append(f"{cn}: 自报=否，但正文出现该类**肯定式**措辞 ⇒ fail-closed —— 「{hit}」")
                else:
                    eff[k] = False
    return eff, blocks, notes


# ---------------------------------------------------------------- 审计块

def split_audit(src):
    body = re.sub(r"<think>.*?</think>", "", src or "", flags=re.S)
    body = re.sub(r"<think>.*$", "", body, flags=re.S)          # 未闭合的推理块
    m = re.search(r"<<AUDIT>>(.*?)<<END_AUDIT>>", body, flags=re.S)
    audit = m.group(1) if m else None
    body = re.sub(r"<<AUDIT>>.*?<<END_AUDIT>>", "", body, flags=re.S)
    body = re.sub(r"<<AUDIT>>.*$", "", body, flags=re.S)        # 未闭合的审计块也剥掉
    return body.strip(), audit


def parse_audit(audit):
    self_rep, anchors, machine, positions = {}, {}, {}, []
    if audit is None:
        return None, anchors, machine, positions
    for name in ("探索提案", "暂定锚点", "冲突反馈", "无内容任务"):
        mm = re.search(name + r"\s*=\s*(是|否)", audit)
        key = {"探索提案": "explore", "暂定锚点": "anchor",
               "冲突反馈": "conflict", "无内容任务": "notask"}[name]
        self_rep[key] = (mm.group(1) == "是") if mm else None
    for line in audit.splitlines():
        m = re.match(r"^\s*([^\s:：][^:：]*?)\s*::\s*(.+?)\s*$", line)
        if not m:
            continue
        k, v = m.group(1).strip(), m.group(2).strip()
        if k in ("未加载参考文件", "已加载参考文件"):
            machine[k] = v
        elif k == "POS":
            positions.append(v)
        else:
            anchors[k] = v
    return self_rep, anchors, machine, positions


# ---------------------------------------------------------------- 必填项实质检查

def check_items(eff, anchors, body):
    nb = _norm(body)
    missing, unanchored, hollow, decorative, inapplicable, spans = [], [], [], [], [], {}

    required = list(ALWAYS_ITEMS)
    for k, (_, items) in TRIGGER_ITEMS.items():
        if eff.get(k):
            required += items
        else:
            for it in items:
                if it in anchors:
                    decorative.append(it)

    for it in required:
        q = anchors.get(it)
        if q is None:
            missing.append(it)
            continue
        nq = _norm(q)
        # 先判空洞（引用内容本身够不够实质），再判锚定（它在不在正文里）
        bad = None
        mm = re.match(r"^(不适用|未知)\s*[：:，,]?\s*(.*)$", q.strip())
        if mm:
            if len(_norm(mm.group(2))) < 10:
                hollow.append(f"{it}: 不适用/未知 后面没有实质原因（{q[:40]}）")
            else:
                inapplicable.append(it)      # 合法：本项确实不适用，不要求它在正文里有对应句
            continue
        if nq in {_norm(x) for x in HOLLOW_EXACT}:
            bad = "纯空洞短语"
        elif len(nq) < MIN_ANCHOR_CHARS:
            bad = f"少于 {MIN_ANCHOR_CHARS} 字"
        if bad:
            hollow.append(f"{it}: {bad}（{q[:40]}）")
            continue
        pos = nb.find(nq)
        if pos < 0:
            unanchored.append(it)
            continue
        spans[it] = (pos, pos + len(nq))

    # 一族里过半都写"不适用"，多半是这个触发本来就不该命中——如实记下来，
    # 而不是逼模型为一个不存在的提案编六条内容。
    mostly = []
    for k, (cn, items) in TRIGGER_ITEMS.items():
        if not eff.get(k):
            continue
        n = sum(1 for it in items if it in inapplicable)
        if n * 2 > len(items):
            mostly.append(f"{cn}: {n}/{len(items)} 项写了不适用 —— 该触发可能本就不该命中")

    overlap = []
    keys = sorted(spans)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = spans[keys[i]], spans[keys[j]]
            if a[0] < b[1] and b[0] < a[1]:
                overlap.append(f"{keys[i]} 与 {keys[j]} 引用了正文同一段文字")
    # spans 一并返回：持续位锚点要与必填项锚点**跨族**互不重叠，
    # 否则同一句话可以既顶一项探索、又顶一个持续位。
    return (missing, unanchored, hollow, decorative, overlap,
            inapplicable, mostly, list(spans.values()))


# ---------------------------------------------------------------- 其余确定性检查

def check_min_output(body):
    fails = []
    n = len(_nows(body))
    if n < MIN_BODY_CHARS:
        fails.append(f"正文仅 {n} 字，低于最低实质产出门 {MIN_BODY_CHARS}")
    segs = [s for s in _segments(body) if len(_nows(s)) >= 10]
    if len(segs) < MIN_SENTENCES:
        fails.append(f"实质句段仅 {len(segs)} 句，低于 {MIN_SENTENCES}")
    rest = "".join(_nows(s) for s in segs if not re.search(REF_SENTENCE, s))
    if len(rest) < MIN_NON_REFERENCE_CHARS:
        fails.append(f"去掉谈参考文件加载状态的句段后只剩 {len(rest)} 字，"
                     f"低于 {MIN_NON_REFERENCE_CHARS} —— 交付实质等于没有")
    return fails


def check_leaks(body):
    hits = []
    for pat, why in LEAK_PATTERNS:
        for m in re.finditer(pat, body or ""):
            hits.append(f"{why}: {m.group(0)[:40]}")
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def check_input_contradiction(slots, body):
    """返回 (阻断项, 仅记录项)。"""
    segs = [x for x in re.split(r"[。；;！!？?\n]", body or "") if x.strip()]
    def scan(table):
        out = []
        for slot, subj in table.items():
            if slot not in slots or not _slot_filled(slots[slot]):
                continue
            for seg in segs:
                if re.search(subj + ABSENCE_NEAR, seg):
                    out.append(f"{slot}: 输入槽位有内容，正文却说它缺失/没进来 —— 「{seg.strip()[:60]}」")
                    break
        return out
    return scan(SLOT_SUBJECTS), scan(ADVISORY_SLOT_SUBJECTS)


# 别名只用于**散文层**的附加核对。实测反例：「市场观察未提供」被旧别名里的「市场」命中，
# 判成"服装参考资料被说成未加载"——那句话说的是 market_observations 槽，不是参考文件。
# 因此散文核对必须同时满足三件事：出现参考类名词、出现该文件的别名、出现否定。
REF_ALIASES = {
    "fashion-and-market": r"服装|服饰|面料|陈列|季节|穿搭|版型",
    "six-skill-methods": r"六份|方法参考|能力方法|既有能力|方法继承",
}
REF_NOUN = r"参考|资料|附件|清单|文件"
REF_NEGATION = r"未加载|不可得|未读到|没有加载|未提供|不可用|没附|未附|没有附|拿不到|缺失"
# ---- DD-4：否定必须落在**参考文件**上，不是落在账号事实上（REBIND-006 §2.4）----
# 「对照服装经营参考资料判断了试穿证据的缺失边界——本周期没有试穿素材」：
# 缺的是试穿素材（账号事实缺口），不是参考文件。v1.2 起的检查只要求同一分句里
# 同时出现「参考类名词」与「否定类词」，于是把 SKILL.md O-6 **要求**分开写两类缺口
# 的那句话判成了与清单矛盾（第 8 轮 B07-1）。
# 修法：否定必须**紧贴**参考类名词——前后 4 字内、中间不跨标点，才算说的是参考文件本身。
REF_NEG_ATTACHED = re.compile(
    r"(?:参考|资料|附件|清单|文件)[^，。；、,\n]{0,4}"
    r"(?:未加载|不可得|未读到|没有加载|没加载|未提供|不可用|没附|未附|没有附|拿不到|缺失)"
    r"|"
    r"(?:未加载|没有加载|没加载|未读到|未提供|不可用|没附|未附|没有附|拿不到|缺少|缺失|没有|无)"
    r"[^，。；、,\n]{0,4}(?:参考|资料|附件|清单|文件)")


def check_manifest(manifest, body, machine_lines=None):
    man = manifest or ""
    loaded = re.findall(r"([\w./-]+\.md)\s*:\s*LOADED", man)
    notloaded = re.findall(r"([\w./-]+\.md)\s*:\s*NOT_LOADED", man)
    bad = []

    # (a) 主检查：审计机器行必须与清单逐条相等。这是"只许回抄"的机械化，
    #     不依赖任何自然语言措辞——v1.2 正文里已经不许出现文件路径了。
    # (a) 机器行是**可有可无的**：清单本来就在代码手里，让模型再抄一遍是纯重复
    #     （A5：拿掉它结果不变）。抄了就核对一下当记录，没抄不算错、更不阻断。
    ml = machine_lines or {}
    echo_note = []
    if man.strip() and ml:
        truth = {p: "LOADED" for p in loaded}
        truth.update({p: "NOT_LOADED" for p in notloaded})
        blob = " ".join(f"{k} :: {v}" for k, v in ml.items())
        pairs = dict(re.findall(r"([\w./-]*[\w-]\.md)\s*[:：]?\s*(NOT_LOADED|LOADED)", blob))
        line = {}
        for p in re.findall(r"[\w./-]*[\w-]\.md", ml.get("已加载参考文件", "")):
            line[p] = "LOADED"
        for p in re.findall(r"[\w./-]*[\w-]\.md", ml.get("未加载参考文件", "")):
            line[p] = "NOT_LOADED"
        got = pairs if pairs else line
        if got and got != truth:
            echo_note.append(f"审计块机器行与清单不一致（仅记录，不阻断）：自报 {got}，清单 {truth}")

    # (b) 附加网：正文散文层面的否定。按逗号级切分，避免"附了 A，没附 B"被整句误判。
    csegs = [x for x in re.split(r"[。；;！!？?，,、\n]", body or "") if x.strip()]
    for f in loaded:
        stem = f.split("/")[-1].rsplit(".", 1)[0]
        alias = REF_ALIASES.get(stem)
        for seg in csegs:
            hit_name = (stem in seg) or (alias and re.search(alias, seg))
            if hit_name and REF_NEG_ATTACHED.search(seg):
                bad.append(f"{stem}: 清单为 LOADED，正文同一分句出现未加载类措辞 —— 「{seg.strip()[:40]}」")
                break
    return loaded, notloaded, bad, ("<<REFERENCE_MANIFEST>>" in man), echo_note


# v1.2 的 extract_baseline_objects / check_continuity / CONT_DISPOSED 在 v1.3 整段删除。
# 不是重构，是这一轮修复的实质：它们用正则从散文里认产品语义，
# 词面收紧就漏检、放宽就误报，认不出的对象整批丢。替代品在下面——结构对结构。
# 原文在 gate_v12/shared_checks.py 里逐字保留，可回指。

# ================================================================ 持续位（G-3）
# 第 5 轮的根因不是正则写得不好，是**根本不该用正则**：`P1/P2/P3` 这个编号在产品语义里
# 没有任何依据，是执行侧从某一次输出里看到就当成通例。判定者的原话必须留在代码里：
#   「在抽取器覆盖面被独立验证之前，dropped_without_notice: [] 不构成『没有内容被丢掉』的证据。」
# v1.3 因此把持续位做成端到端结构化对象——输入侧 JSON、输出侧审计块机器行、闸门做集合比对，
# 任何一环都不经过散文。

POS_STATUS = {"继续": "continued", "处置": "disposed", "替换": "superseded"}
POS_NEW_KINDS = {"探索": "exploration", "常规": "regular"}


def parse_standing_positions(slots):
    """输入侧持续位。槽位值是 JSON 数组；解析失败**不当作空**，明确回报解析错误——
    静默当空正是上一轮那种「字段为空 = 没丢东西」的假象来源。"""
    raw = (slots.get("standing_positions") or "").strip()
    if not raw:
        return {"present": "standing_positions" in slots, "positions": [], "parse_error": None}
    try:
        v = json.loads(raw)
    except Exception as e:                                    # noqa: BLE001
        return {"present": True, "positions": [], "parse_error": f"{type(e).__name__}: {e}"}
    if not isinstance(v, list):
        return {"present": True, "positions": [], "parse_error": "不是 JSON 数组"}
    out = []
    for it in v:
        if isinstance(it, dict) and it.get("id"):
            out.append({"id": str(it["id"]), "kind": it.get("kind"),
                        "title": it.get("title"), "since": it.get("since"),
                        "last_restated": it.get("last_restated")})
    return {"present": True, "positions": out, "parse_error": None}


def parse_positions_declaration(pos_lines):
    """审计块机器行：`POS :: <id> :: <状态> :: <正文原句锚点>`
    新建位：`POS :: NEW:<slug> :: 新增·探索|新增·常规 :: <锚点>`"""
    decls, bad = [], []
    for raw in pos_lines or []:
        parts = [x.strip() for x in re.split(r"\s*::\s*", raw) if x.strip()]
        if len(parts) < 3:
            bad.append(f"字段不足（需 id::状态::锚点）：{raw[:60]}")
            continue
        pid, st, anchor = parts[0], parts[1], " :: ".join(parts[2:])
        if st in POS_STATUS:
            decls.append({"id": pid, "status": POS_STATUS[st], "kind": None,
                          "anchor": anchor, "is_new": False})
        elif st.startswith("新增"):
            kind_cn = st.split("·", 1)[1].strip() if "·" in st else ""
            if kind_cn not in POS_NEW_KINDS:
                bad.append(f"新增位的类别只能是「探索」或「常规」：{raw[:60]}")
                continue
            decls.append({"id": pid, "status": "new", "kind": POS_NEW_KINDS[kind_cn],
                          "anchor": anchor, "is_new": True})
        else:
            bad.append(f"状态只能是 继续/处置/替换/新增·探索/新增·常规：{raw[:60]}")
    return decls, bad


def check_positions(input_pos, decls, bad_lines, body, used_spans=()):
    """确定性集合比对 + 锚点核对。这里**没有一处**去猜产品语义。"""
    nb = _norm(body or "")
    in_ids = [p["id"] for p in input_pos.get("positions", [])]
    dec_ids = [d["id"] for d in decls]

    unaccounted = [i for i in in_ids if i not in dec_ids]
    fabricated = [d["id"] for d in decls if not d["is_new"] and d["id"] not in in_ids]
    dup = sorted({i for i in dec_ids if dec_ids.count(i) > 1})

    bad_anchor, spans = [], list(used_spans)
    for d in decls:
        a = (d.get("anchor") or "").strip()
        na = _norm(a)
        if len(na) < MIN_ANCHOR_CHARS:
            bad_anchor.append(f"{d['id']}: 锚点不足 {MIN_ANCHOR_CHARS} 字")
            continue
        if _nows(a) in {_nows(x) for x in HOLLOW_EXACT}:
            bad_anchor.append(f"{d['id']}: 锚点是空话")
            continue
        i = nb.find(na)
        if i < 0:
            bad_anchor.append(f"{d['id']}: 锚点指不回正文")
            continue
        seg = (i, i + len(na))
        if any(not (seg[1] <= a0 or seg[0] >= b0) for a0, b0 in spans):
            bad_anchor.append(f"{d['id']}: 锚点与其他引用重叠（同一句不能顶两项）")
            continue
        spans.append(seg)

    new_exploration = [d["id"] for d in decls if d["is_new"] and d["kind"] == "exploration"]
    blocking = bool(unaccounted or fabricated or dup or bad_anchor or bad_lines
                    or input_pos.get("parse_error"))
    return {
        "baseline_present": bool(in_ids),
        "input_position_ids": in_ids,
        "declared_position_ids": dec_ids,
        "positions_unaccounted": unaccounted,
        "positions_fabricated": fabricated,
        "positions_duplicated": dup,
        "positions_bad_anchor": bad_anchor,
        "positions_bad_lines": list(bad_lines or []),
        "input_parse_error": input_pos.get("parse_error"),
        "new_exploration_positions": new_exploration,
        "continued": [d["id"] for d in decls if d["status"] == "continued"],
        "disposed": [d["id"] for d in decls if d["status"] in ("disposed", "superseded")],
        "new_positions": [{"id": d["id"], "kind": d["kind"]} for d in decls if d["is_new"]],
        "blocking": blocking,
        "anchor_spans": spans,
    }


# ================================================================ 旧值压过输入（G-4 v2）
# REBIND_005 §2：v1 的判据在 61 例真实运行上命中 12 次、误报 11 次，6 次拒收了合格交付。
# 根因只有一句：**没有周期的数字不是速率主张**。「用一条内容同时覆盖四个目标」里的
# 「一条」是量词，不是发布量；v1 把它和槽位里的「3 条/周」直接比，于是几乎只在
# 冻结判据**要求**的行为（三值分离、等价换算、拒绝合并）上开火。
#
# v2 把「数字」和「速率」分开：
#   带周期的数字   → 正式判据，可阻断；
#   不带周期的数字 → 只记 advisory，不阻断（宁可少挡，不可挡掉对的）。
# 两个方向的数字（误报、漏检）都必须在真实语料上量出来并写进证据——这条方法义务
# REBIND_004 §2.2 只给了 G-2，REBIND_005 §3 补给 G-4。
_CN_NUM = {"零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5,
           "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

QTY_SUBJECTS = {
    "actual_capacity": r"实际产能|当前产能|本周产能|这周产能|真实产能|实际能做|实际只能",
    "baseline_capacity": r"基线产能|常态产能|正常产能|平时产能|基准产能",
    "expected_publish_count": r"目标|期望发布|计划发布|想发|要发",
}
NOW_MARKER = r"当前|本周|这周|现在|目前|眼下|如今|此刻"
PAST_MARKER = r"上周|上一轮|上个?周期|之前|原来|原本|曾|此前|过去|历史上|当初"

# 序数与指代前缀：「第一条」「下一条」「另一条」——数的是内容的第几条，不是一周几条。
# 不排掉它们，一个「本周三条内容：第一条讲价格…」就会被读成「本周 1 条」。
ORDINAL_PREFIX = "第下上这那另某每前后同各"
# 周期词回看窗口。「本周实际产能只有一条」从「一」往回 8 个字就能看到「本周」。
PERIOD_LOOKBACK = 12
# ---- DD-5：「本周期」不是「本周」（REBIND-007 §2.1）------------------------
# 第 10 轮真实运行 B15-DIR-02 的原句：「这是长期价值目标下，本周期最重要的一条」。
# 「本周」在「本周期」里被整个匹配掉，于是「一条」被绑上了周期，一个**选择性量词**
# 被读成 1 条/周，去压输入里的 3 条/周 —— 这正是 REBIND-005 要修掉的 G-4 v1 病理
# 换了个形状复发。同族还有「本日期」。修法是一个负向前瞻，不新增词表。
PERIOD_WORD = re.compile(r"(每|本|这|一|该)\s*(天|日|周)(?!期)")
PERIOD_PREFIX = re.compile(r"每\s*(天|日|周)\s*(?:约|大约|差不多|近|上下|将近)?\s*$")
# advisory：无周期的数字要离主语足够近才值得记一笔，否则整段里任何一个「一条」都会响。
ADVISORY_NEAR = 12
# 谓语式：主语**后面**紧跟系动词/量度词再接数字 —— 「当前实际产能只有一条」。
# 这一支专门捞「没写周期但确实在给主语赋值」的真覆盖（S1、E04 都是这个形状）。
# 它和量词式的区别是位置和结构，不是措辞：量词式里数字在主语**前面**（「用一条内容
# 同时覆盖四个目标」），或者中间隔着标点（「长期价值目标下，两条反馈…」）。
PREDICATE_COPULA = re.compile(r"是|为|只有|仅有|只剩|剩下|只能|仅能|能做|可做|做得了|"
                              r"排得下|可投入|支撑|上限|降到|降为|不足|实际是|实为")
PREDICATE_GAP_MAX = 14
PREDICATE_NO_PUNCT = re.compile(r"^[^，。；、,:：!！?？\n]*$")
# 否定语境：「不为凑三条把本周压缩成一条内容」说的是**不这么做**，不是「当前是一条」。
# 用的是本文件已有的 `NEGATION_BEFORE`（G-2 探索位那一层同款回看），不另造一套词表。
# `NEG_CANCEL` 挡住「不是每周 3 条，而是每周 1 条」——转折之后那个数仍然是主张。
NEG_LOOKBACK = 16
NEG_CANCEL = re.compile(r"而是|实际是|其实是|应为|应该是|改为|调整为|降到|降为|提到|提为")

# ---- DD-2：槽位权威值只认主句（REBIND-006 §2.1）----------------------------
# 「1 条（本周实际，低于基线 3 条）」的权威值是 1 条；括注里的 3 条是解释性对照。
# v2 直接扫全串、只留带周期的数字，于是把括注里的对照值当成了权威值，正文里
# 正确的「本周实际产能只有 1 条」反被判成用旧值压输入（第 8 轮 B04-1P）。
# 修法就一句：**槽位里第一个数量是权威值，它后面的都是解释性对照**；周期允许
# 从后半段借（借的是周期，不是值），这样「1 条（本周实际…）」才能认成 1 条/周。
# 说明一句作用域：这条规则认不出反序写法（「陈晚 2 条 + 导购 1 条，合计每周 3 条」）。
# 真实语料 14 个不同槽位取值里没有这种形状；出现了就是漏检，不是误报。
# 曾经写过一版「先剥掉括注再取值」的 SLOT_ASIDE，在真实语料上消融无差别
# （删掉它 64 例 ×2 份正文的命中集完全不变），按 A5 删除，不为对称保留。

# ---- DD-3a：被拿掉的那部分不是速率主张（REBIND-006 §2.2）-------------------
# 「本周必须让掉另外 2 条」说的是**被让掉的那 2 条**，不是「目标变成 2 条/周」。
# SKILL.md O-3 恰恰**要求**写清让掉了哪几条，检查却对着这句话开火。
#
# 一个族，一次消融：句中这个数前面挂着「部分量限定词」或「移除类动词」时，
# 它指的是整体里被拿走的那一块，不是整体的新值。
# 移除类动词一律带结果补语（掉／出／走）或本身就是移交义，这是和**赋值类动词**的
# 分界线：`砍到／减到／降到／压到 2 条` 说的是「现在变成 2 条」，是真覆盖，
# 必须留在判据里能被抓到——所以这几个词**不进**这张表。
# （曾经把「部分量限定词」与「移除类动词」写成两个独立守卫，二者在真实语料上互相
#   遮蔽、单独关掉都无差别，按 A5 合并成这一个。）
PARTITIVE_PREFIX = re.compile(
    r"(另外|其余|其中|剩下|余下|多出|"
    r"让掉|让出|让渡|去掉|减掉|删掉|压掉|省掉|挪走|推迟|延后|牺牲|留给)"
    r"[^，。；、\n]{0,4}$")
TRADEOFF_LOOKBACK = 14

# ---- DD-3b：后置否定（REBIND-006 §2.3）------------------------------------
# 「一周五条这周做不到，不是安排问题，是真实产能只剩两条」——「五条」是被否掉的
# 那个方案，不是当前值；真正的赋值在后半句「只剩两条」，和输入一致。
# 已有的 `_negated_at` 只往**前**看（「不为凑三条…」），这一支是同一个现象的另一侧。
NEG_AFTER_LOOKAHEAD = 10
NEG_AFTER = re.compile(r"做不到|做不了|做不完|办不到|排不下|排不开|达不到|完不成|"
                       r"不可能|不现实|撑不住|顶不住|做不出|来不及")


# 回看窗口不许跨小句：第 9 轮实测到一次——「一周五条这周做不到，**不是**安排问题，
# 是真实产能只剩两条」里，前一小句的「不是」把后一小句「只剩两条」这个真赋值否掉了，
# 于是把权威值改成必然冲突的值之后判据也不再开火（漏检）。否定只管自己那一小句。
NEG_CLAUSE_CUT = re.compile(r"[，,、：:]")


def _negated_at(seg, at):
    pre = NEG_CLAUSE_CUT.split(seg[max(0, at - NEG_LOOKBACK):at])[-1]
    last = None
    for last in re.finditer(NEGATION_BEFORE, pre):
        pass
    if last is None:
        return False
    return not NEG_CANCEL.search(pre[last.end():])


def _negated_after(seg, end):
    """数字**后面**紧跟「做不到／排不下」这类可行性否定 ⇒ 这个数是被否掉的方案，
    不是当前值。中间不许跨标点，否则「本周 5 条，这我做不到」也会被吞掉。"""
    win = seg[end:end + NEG_AFTER_LOOKAHEAD]
    m = NEG_AFTER.search(win)
    if not m:
        return False
    return PREDICATE_NO_PUNCT.match(win[:m.start()]) is not None


def _slot_authority(raw):
    """槽位的权威速率，最多一项：`[{n, unit, period_source}]`；取不到周期就返回 `[]`
    （= 这个槽位没有速率主张，G-4 对它整槽豁免，宁可少挡也不挡掉对的）。"""
    qs = _qty_scan(raw or "")
    if not qs:
        return []
    head = dict(qs[0])                       # 第一个数量就是权威值，其后都是解释性对照
    if head["unit"]:
        return [head]
    mw = PERIOD_WORD.search(raw or "")       # 主句没写周期：只借周期，不借值
    if mw:
        head["unit"] = {"日": "天"}.get(mw.group(2), mw.group(2))
        head["period_source"] = "aside_word"
        return [head]
    return []


def _qty_scan(text):
    """抽出全部「N 条」，并逐个判断它**有没有绑定周期**。

    绑定来源三种，优先级从强到弱：
      suffix  `3 条/周`
      prefix  `每周约 3 条`
      word    同一句里数字前 12 字内出现「本周／这周／一周／每天」等周期词
    三种都没有 ⇒ `unit=None`，这个数字**不是速率主张**，不进正式判据。
    """
    out = []
    t = text or ""
    # 已知漏检，本轮**不修**，如实记在 REBIND-006 §4：`／` 是全角斜杠，语料里
    # `4 条／周` 这种写法有 5 个不同槽位取值，这条正则只认半角，于是它们整槽落进
    # "没有周期"，G-4 对它们从来没生效过。改成 `[/／]` 只是一个字符，但在真实语料上
    # 两个轴（误报集、漏检探针捕获数）都量不出差别——按 A5 不为"看起来更完整"而留，
    # 留下来的是这条披露。哪天有样本能把它量出来，再按同一套程序收口。
    for m in re.finditer(r"(\d+|[零一两二三四五六七八九十])\s*条(?:\s*/\s*(天|日|周))?", t):
        raw = m.group(1)
        n = int(raw) if raw.isdigit() else _CN_NUM.get(raw)
        if n is None:
            continue
        if m.start() > 0 and t[m.start() - 1] in ORDINAL_PREFIX:
            continue                      # 第一条／下一条／另一条：序数，不是速率
        unit, src = m.group(2), ("suffix" if m.group(2) else None)
        if not unit:
            pre = t[max(0, m.start() - PERIOD_LOOKBACK):m.start()]
            mp = PERIOD_PREFIX.search(pre)
            if mp:
                unit, src = mp.group(1), "prefix"
            else:
                mw = PERIOD_WORD.search(pre)
                if mw:
                    unit, src = mw.group(2), "word"
        tpre = t[max(0, m.start() - TRADEOFF_LOOKBACK):m.start()]
        partitive = bool(PARTITIVE_PREFIX.search(tpre))
        out.append({"n": n, "unit": {"日": "天"}.get(unit, unit),
                    "period_source": src, "partitive": partitive,
                    "start": m.start(), "end": m.end()})
    return out


def _qty(text):
    """兼容旧签名：只返回 (数量, 单位)。判据本身已改用 `_qty_scan`。"""
    return [(q["n"], q["unit"]) for q in _qty_scan(text)]


def _per_week(n, unit):
    """§3 的等价换算：每天 N 条 ⇒ 每周 7N 条。换算本身**不是**矛盾，
    缩小目标量才是。单位缺失时不归一，返回 None。"""
    if unit == "天":
        return n * 7
    if unit == "周":
        return n
    return None


def _fmt_q(qs):
    return "、".join(f"{q['n']}条/{q['unit'] or '?'}" for q in qs)


def check_stale_value_override(slots, body):
    """只挡一个方向：正文用一个**现时性、带周期**的速率断言，压过当轮输入里该槽位的权威值。

    不挡量词（「用一条内容同时覆盖四个目标」）——那不是速率。
    不挡等价换算（每天 3 条 ⇒ 每周 21 条）——Founder 第 3 条逐字授权。
    不挡三值分离的原句——三个数与槽位一致时整段豁免。
    不挡历史对比，不挡逐字引用输入原值后的比较。

    返回 (blocking_hits, advisory)。advisory 记的是「数字对不上但没有周期」的情形：
    看得见、不阻断。漏检就漏在这里，所以它必须被记出来，而不是消失。
    """
    hits, advisory = [], []
    for slot, subj in QTY_SUBJECTS.items():
        raw = slots.get(slot)
        if raw is None or not _slot_filled(raw):
            continue
        slot_q = _slot_authority(raw)          # DD-2：权威值只认主句
        if not slot_q:
            continue
        slot_pw = {_per_week(q["n"], q["unit"]) for q in slot_q}
        slot_n = {q["n"] for q in slot_q}
        for seg in _segments(body or ""):
            ms = re.search(subj, seg)
            if not ms:
                continue
            if not re.search(NOW_MARKER, seg):
                continue
            if re.search(PAST_MARKER, seg):
                continue
            qs = [q for q in _qty_scan(seg) if not q["partitive"]]   # DD-3a
            periodic = [q for q in qs if q["unit"]
                        and not _negated_at(seg, q["start"])
                        and not _negated_after(seg, q["end"])]        # DD-3b
            if periodic:
                # 任一带周期的数与槽位归一后相等 ⇒ 在复述或换算，不是覆盖。
                if any(_per_week(q["n"], q["unit"]) in slot_pw for q in periodic):
                    continue
                hits.append(f"{slot}: 输入权威值 {_fmt_q(slot_q)}，正文却断言当前是 "
                            f"{_fmt_q(periodic)} —— 「{seg.strip()[:60]}」")
                break
            # 谓语式：主语后面 14 字内、中间不跨标点、且夹着系动词/量度词的那个数字，
            # 是在给主语赋值。数值与槽位一致 ⇒ 复述，整段豁免；对不上 ⇒ 覆盖，阻断。
            pred = [q for q in qs
                    if q["start"] >= ms.end()
                    and q["start"] - ms.end() <= PREDICATE_GAP_MAX
                    and PREDICATE_NO_PUNCT.match(seg[ms.end():q["start"]])
                    and PREDICATE_COPULA.search(seg[ms.end():q["start"]])
                    and not _negated_at(seg, q["start"])]
            if pred:
                if any(q["n"] in slot_n for q in pred):
                    continue
                hits.append(f"{slot}: 输入权威值 {_fmt_q(slot_q)}，正文却把当前值说成 "
                            f"{_fmt_q(pred)} —— 「{seg.strip()[:60]}」")
                break
            # 没有周期的数字：只有紧挨着主语、且数值也对不上时才记 advisory。
            near = [q for q in qs
                    if abs(q["start"] - ms.start()) <= ADVISORY_NEAR and q["n"] not in slot_n]
            if near:
                advisory.append(f"{slot}: 输入权威值 {_fmt_q(slot_q)}，正文里紧邻主语出现无周期的 "
                                f"{_fmt_q(near)} —— 「{seg.strip()[:60]}」（无周期，不阻断）")
            # DD-3 排掉的量必须留痕：漏检要看得见，不能因为被排掉就消失。
            excl = [q for q in _qty_scan(seg)
                    if q["unit"] and (q["partitive"] or _negated_after(seg, q["end"]))]
            if excl:
                advisory.append(f"{slot}: 已按取舍量／后置否定排除 {_fmt_q(excl)} —— "
                                f"「{seg.strip()[:60]}」（不阻断，留痕备查）")
    return hits, advisory


BLANKET_CARRY = (r"(其余|其他|未涉及|未受影响|不受影响|没有涉及|以外)[^。；;\n]{0,24}"
                 r"(判断|任务|安排|计划|部分|内容|组合|节奏|基线)?[^。；;\n]{0,24}"
                 r"(保持不变|保持|不变|沿用|继续有效|仍然有效|维持|照常)")


def has_blanket_carry(text):
    """概括性延续声明。判据只写一份，闸门与复检共用——两份判据迟早会分叉。"""
    return bool(re.search(BLANKET_CARRY, text or ""))
