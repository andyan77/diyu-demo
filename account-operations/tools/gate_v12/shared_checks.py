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

__all__ = ['ABSENCE_NEAR', 'ACTION_MARKER', 'ADVISORY_SLOT_SUBJECTS', 'ALWAYS_ITEMS', 'BODY_KEYWORDS', 'CONDITIONAL_VOID', 'CONT_DISPOSED', 'EMPTY_SLOT_VALUES', 'HOLLOW_EXACT', 'LABEL_SHELL', 'LEAK_PATTERNS', 'MIN_ANCHOR_CHARS', 'MIN_BODY_CHARS', 'MIN_NON_REFERENCE_CHARS', 'MIN_SENTENCES', 'NEGATION_BEFORE', 'REF_ALIASES', 'REF_DISPLAY', 'REF_NEGATION', 'REF_NOUN', 'REF_SENTENCE', 'SHELL_FAMILY', 'SLOT_ABSENCE_VALUE', 'SLOT_NAMES', 'SLOT_SUBJECTS', 'TRIGGER_ITEMS', '_PUNCT', '_SLOT_HEAD', '_norm', '_nows', '_parse_slots', '_segments', '_slot_filled', 'check_continuity', 'check_input_contradiction', 'check_items', 'check_leaks', 'check_manifest', 'check_min_output', 'compute_triggers_from_input', 'extract_baseline_objects', 'parse_audit', 'positive_hit', 'render_body', 'resolve_triggers', 'split_audit']

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
ABSENCE_NEAR = (r"[^。；;，,：:「」（）()\n]{0,8}?"
                r"(?:还没有(?:进来|给|提供)|没有进来|未进来|没有收到|未收到|没给我?|没有给我?|"
                r"未给出|尚未提供|没有提供|未提供|缺了|缺失|为空|不可得|没有任何)")
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
              "standing_cycle_baseline")
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
    self_rep, anchors, machine = {}, {}, {}
    if audit is None:
        return None, anchors, machine
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
        else:
            anchors[k] = v
    return self_rep, anchors, machine


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
    return missing, unanchored, hollow, decorative, overlap, inapplicable, mostly


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
            if hit_name and re.search(REF_NOUN, seg) and re.search(REF_NEGATION, seg):
                bad.append(f"{stem}: 清单为 LOADED，正文同一分句出现未加载类措辞 —— 「{seg.strip()[:40]}」")
                break
    return loaded, notloaded, bad, ("<<REFERENCE_MANIFEST>>" in man), echo_note


def extract_baseline_objects(slots):
    """投影"前"的关键对象。阻断集只取歧义最低的两类：任务位号与节奏数量。"""
    b = slots.get("standing_cycle_baseline", "") or ""
    # 「本周不是把周频改成 1 条/周」里的 1 条/周 是被否定掉的量，不是必须延续的对象
    b = re.sub(r"[^。；;\n]*?(?:不是|并非|不会|不换算|不改成|不降到|不提到)[^。；;\n]*", "", b)
    tasks = sorted(set(re.findall(r"(?<![A-Za-z0-9])(P\d{1,2})(?![A-Za-z0-9])", b)))
    rhythm = sorted({re.sub(r"\s+", "", x) for x in
                     re.findall(r"每周\s*\d+\s*条|\d+\s*条\s*/\s*周", b)})
    named = sorted({x for x in re.findall(r"[「《]([^」》\n]{2,20})[」》]", b)})
    return {"tasks": tasks, "rhythm": rhythm, "named_advisory": named,
            "baseline_present": bool(_slot_filled(b) and not b.startswith("尚无"))}


CONT_DISPOSED = (r"退出|停(?:掉|了|更|止)?|暂停|收起|结束|下线|不再|取消|替换|并入|合并|"
                 r"覆盖|到期|让位|延后|延期|推迟|改期|后移|回到|不动|保持|不变|沿用|"
                 r"继续|维持|照常|仍然|复验|按原计划|无新任务")


def check_continuity(base_obj, text):
    """投影前后一致性：基线里的关键对象，本轮要么继续、要么被点名处置，不许静默消失。

    这不是新要求——SKILL 自检第 7 条（"未受影响的判断明确说保持了吗"）、O-7 连续性义务、
    O-11 限定影响面已经要求了。这里只是把它从"记得就写"改成"缺了能被机械检出"。
    """
    if not base_obj or not base_obj.get("baseline_present"):
        return {"status": "NO_BASELINE", "carried": [], "disposed": [],
                "dropped_without_notice": [], "advisory_named_dropped": []}
    t = text or ""
    segs = _segments(t)
    carried, disposed, dropped = [], [], []
    for obj in list(base_obj.get("tasks", [])) + list(base_obj.get("rhythm", [])):
        probe = obj if not re.search(r"条\s*/?\s*周|每周", obj) else None
        if probe is None:
            hit = bool(re.search(r"每周\s*\d+\s*条|\d+\s*条\s*/\s*周", t))
        else:
            hit = bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(obj) + r"(?![A-Za-z0-9])", t))
        if hit:
            named = [s for s in segs if (re.search(r"每周\s*\d+\s*条|\d+\s*条\s*/\s*周", s)
                                         if probe is None else
                                         re.search(r"(?<![A-Za-z0-9])" + re.escape(obj)
                                                   + r"(?![A-Za-z0-9])", s))]
            if any(re.search(CONT_DISPOSED, s) for s in named):
                disposed.append(obj)
            else:
                carried.append(obj)
        else:
            dropped.append(obj)
    adv = [n for n in base_obj.get("named_advisory", []) if n not in t]
    # 概括性延续声明（= SKILL 自检第 7 条"未受影响的判断明确说保持了吗"）。
    # 有它就不必逐个点名，但投影侧必须改为"逐字保留上一基线的相应原句"，不能整体覆盖。
    blanket = bool(re.search(
        r"(其余|其他|未涉及|未受影响|不受影响|没有涉及|以外)[^。；;\n]{0,24}"
        r"(判断|任务|安排|计划|部分|内容|组合|节奏|基线)?[^。；;\n]{0,24}"
        r"(保持不变|保持|不变|沿用|继续有效|仍然有效|维持|照常)", t))
    # 「本轮没重述」≠「内容丢了」。O-11 要求限定影响面，一份聚焦回答本来就不该
    # 把整份基线抄一遍；把"没重述"判成交付失败会逼出全量重写，和产品语义相反。
    # 真正要防的是**投影把它弄丢**——那由投影侧的逐字保留兜底，见 projection_v12.py。
    # 因此这里只分三态，且都不阻断交付本身：
    #   OK       全部对象要么被继续、要么被点名处置
    #   MERGED   有对象本轮未涉及 ⇒ 投影必须逐字保留它们的原句，不得整体覆盖
    #   （交付侧唯一的阻断来自最低产出硬门，不来自这里）
    status = "OK" if not dropped else ("BLANKET_CARRY" if blanket else "MERGED")
    return {"status": status, "carried": carried, "disposed": disposed,
            "blanket_carry_statement": blanket,
            "not_restated": dropped,
            "dropped_without_notice": [],
            "dropped_covered_by_blanket": dropped if (dropped and blanket) else [],
            "advisory_named_dropped": adv}
