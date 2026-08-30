#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜构建后继 Skill。**零模型调用、零 Dify 写入。**

从 **b1** 逐字继承（b1 的事实来源修复整块保留，不回退），只做确定性插入：
一个任务级状态判定块、两个条件化前置块（PP-5 / 作者转发语）、一条全表面自检。
一条既有判据都不删、不弱化。插入点用唯一锚点定位，锚点不唯一即拒绝构建。

b1 的失效原因是**覆盖面不足**：新 CTA 规则只装在「CTA 三级接缝」之后与
「无 CTA 评论区」小节前，而实际产生"要求受众动作"表达的是
PP-5 整节与「作者转发语」整节——两者都没有被约束到（A3「少算」）。
b2 只补这个缺口，不改任何包装专业判据。

    python3 PPBS_B2_BUILD_SUCCESSOR_SKILL_v1.0.py
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
SRC = os.path.join(REPO, "content-production/skills/"
                         "packaging-content-for-release-m4-b1/SKILL.md")
M4 = os.path.join(REPO, "content-production/skills/"
                        "packaging-content-for-release-m4/SKILL.md")
DSTDIR = os.path.join(REPO, "content-production/skills/packaging-content-for-release-m4-b2")
DST = os.path.join(DSTDIR, "SKILL.md")
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")

# ---------------------------------------------------------------- 插入块

CTA_STATE = """
### strict_cta_closed：一次判定，全面适用

> 本节是 b2 新增。它不改「CTA 权威顺序」任何一行，只规定那一节**落到哪些产出面上**。
> 上一版把权威顺序写清楚了，却没说清它作用在哪里，结果只有 `cta_surface` 那一格被约束到，
> 评论区与转发语照旧按默认互动方法生成。**规则不写清作用面，就等于没装。**

**第一步：从 `cta_contract` 原文推出一个任务级状态，整份产出只推一次。**

```
strict_cta_closed = true
    ⇔ 上游 cta_contract 原文明确要求：只保留内容本身 ／ 不做任何引导 ／
      不做互动 ／ 不要求受众做任何动作（或其它等价的明确闭合表达）

strict_cta_closed = false
    ⇔ 上游只禁止了若干具体业务动作，没有给出闭合表达
```

判定的对照物是 `cta_contract` 的**原文全文**，不是你对它的复述、摘要或改写。
原文里出现了闭合表达，就是 `true`——**不因为同一句里还列着几项业务动作，
就把它读成"只禁这几项"。一句话里的闭合表达不会被它前面的清单抵消。**

**第二步：`strict_cta_closed = true` 时，下面每一个对外输出面受同一条约束。**
这是一张**清单**，不是举例——逐行过，过一行划掉一行：

| # | 对外输出面 |
|---|---|
| 1 | 标题（全部候选，含未被推荐的那几个） |
| 2 | 封面文字（每一层级） |
| 3 | 首帧／开场 |
| 4 | 发布正文（含单列的开头三行） |
| 5 | `cta_surface` |
| 6 | `comment_design`（置顶首条、每一组预埋问答、每一条作者回复） |
| 7 | `author_share_line` |
| 8 | 各平台差异化版本 |
| 9 | 用户交付块的每一句（**包括你对边界本身的那句说明**） |

同一条约束是：**不得要求受众做动作。** 包括但不限于——

```
购买 · 下单 · 到店 · 预约 · 咨询 · 私信 · 领取
关注 · 评论 · 回复 · 收藏 · 转发 · 分享 · 点赞 · 参与话题
以及：句末指向受众、等一个回答的任何问句
```

最后一行是最容易漏的一种：它不属于任何业务动作类目，不带奖励，读起来像内容，
**但它在等一个回答**。只扫业务动作清单扫不到它。

**第三步：`strict_cta_closed = false` 时，什么都不变。**
CTA 三级表照常适用，PP-5 照常设计评论区，`author_share_line` 照常写，
低风险互动能力**一条没删**。**b2 只在 `true` 那一支收紧，另一支一个字都没动。**

### 自我声明不改变行为性质

在产出里加一句「这不算引导」「这只是内容的延伸」「这属于某种轻的互动」，
**不改变那句话本身有没有在要求受众做动作**。

判定只看一件事：**把那句话单独拿出来读，读的人会不会觉得自己该做点什么。**
会，它就是在要求受众动作——旁边写了什么说明都一样。
**自述不是证据；给一件东西加注释，不改变那件东西。**

同理，**把边界复述一遍不等于守住了边界**。在交付块里写一句"本次不做某几类引导"，
只是重复了原文的一部分；原文里的闭合表达如果没有进入你实际执行的约束面，
复述得再准确也没用。**自检的对照物是原文全文，不是你的复述。**

### 内容里的设问必须由内容自己接住

用设问组织表达是允许的，但有一条硬边界：**问出来的，内容自己要接。**

| | 判定 |
|---|---|
| 正文里问一句，**紧接着自己给出判断** | 是内容，不是 CTA |
| 问完就停，把答案留给受众 | **是 CTA** |
| 问句落在结尾、评论区或转发语的位置 | **是 CTA** |

`strict_cta_closed = true` 时，**不得存在任何一个由受众来回答的问题**——
不管它长得多像"内容"，也不管它有没有挂奖励。
"""

PP5_COND = """> **先判 `strict_cta_closed`，再决定本节适不适用。**（b2 新增）
>
> `strict_cta_closed = true` 时，本节下面三条要求**整体不适用**：
> 不主动设计置顶互动问题，不写为引出留言而准备的开场，不预埋等受众来问的问题，
> 不布置任何形式的评论区任务。此时 `comment_design` 的正确取值是 **`NOT_APPLICABLE`**，
> 或者只写**被动答复边界**——"有人问到 X 时，能答的是 Y、不能答的是 Z"——
> 这类内容不指向受众动作，只是预先准备好的边界说明。
>
> **换一种措辞继续要求互动，等于没有执行这一条。** 把"问一个问题"改写成
> "抛一个缺口""留一个可以接着聊的点""写一条能引出讨论的"——**都是同一件事**。
> 判定看的是这句话会不会让受众想去回答，不是它用了哪个词。
>
> `strict_cta_closed = false` 时，本节**照常全部适用**，一条都不减。

"""

SHARE_COND = """> **先判 `strict_cta_closed`。**（b2 新增）
>
> `true` 时，`author_share_line` 只能是**陈述句**，或者取 **`NOT_APPLICABLE`**；
> 不得是面向受众的疑问句、祈使句或邀请，也不得出现关注、评论、收藏、私信、咨询、
> 到店、预约、购买等任何动作。
> 一句"你有没有……？"即使不带奖励、不涉及任何业务动作，
> **句末指向受众、在等一个回答**，同样不成立。
>
> `false` 时，本节照常适用。

"""

SELFCHECK17 = """17. **（b2）** 先把 `cta_contract` 的**原文全文**抄到眼前，判出 `strict_cta_closed`。
    判成 `true` 的话，**把那张九行的对外输出面清单逐行走一遍**——
    标题（含未推荐的候选）、封面文字、首帧、发布正文、`cta_surface`、
    `comment_design` 的每一条、`author_share_line`、各平台变体、
    用户交付块的每一句：**有没有任何一处在要求受众做动作，或者留了一个等受众回答的问句？**
    只扫了购买／到店／私信／领取这几类业务动作，**就是没扫完**——
    句末指向受众的问句不在那几类里，它是本条最容易漏掉的一种。
    `comment_design` 取了 `NOT_APPLICABLE` 或只写了被动答复边界吗？
    `author_share_line` 是陈述句或 `NOT_APPLICABLE` 吗？
    有没有靠一句"这不算引导""这只是延伸"把某一处放行了——**自述不改变行为**。
    判成 `false` 的话，反过来查一遍：低风险互动能力有没有被无故删掉？
    该设计的评论区设计了吗？——**收紧只发生在 `true` 那一支。**
"""

CHANGED = """
## b2 版改了什么

> b2 只补 b1 的**覆盖面缺口**，一条包装专业判据都不碰，b1 的事实来源修复整块逐字保留。
> 授权：《PP Boundary Successor b2 最小修复与收口执行 Prompt》第四节。

**b1 为什么不够**：b1 把「CTA 权威顺序」装在「CTA 三级接缝」之后、
给「无 CTA 时评论区」小节加了前置条件句，但 **PP-5 整节与「作者转发语」整节没有被约束到**——
这两节恰恰是实际产生"要求受众动作"表达的地方。规则装了，作用面算漏了。

| # | 改动点 | 位置 | 为什么 | 删了既有判据吗 |
|---|---|---|---|---|
| 1 | 新增「`strict_cta_closed`：一次判定，全面适用」：从 `cta_contract` 原文推一次任务级状态；`true` 时九行对外输出面清单受同一条约束（含"句末指向受众等一个回答的问句"）；`false` 时一个字不变 | 「CTA 权威顺序」之后 | b1 写清了权威顺序，没写清作用面，于是只有 `cta_surface` 被约束到 | 否 |
| 2 | 新增「自我声明不改变行为性质」：加一句"这不算引导"不改变那句话在不在要求受众动作；把边界复述一遍不等于守住边界 | 同上 | 自述被当成了合规依据 | 否 |
| 3 | 新增「内容里的设问必须由内容自己接住」判定表 | 同上 | b1 说了"内容内部的设问不是 CTA"，但没说它必须被内容自己接住 | 否，b1 该节逐字保留 |
| 4 | PP-5 加条件化前置块：`true` 时本节三条整体不适用，`comment_design` 取 `NOT_APPLICABLE` 或只写被动答复边界；换措辞继续要求互动等于没执行 | PP-5 标题之后 | PP-5 无条件要求"第一条自己写、预埋两个问题" | 否，`false` 时本节全部照常适用 |
| 5 | 「作者转发语」加条件化前置块：`true` 时只能是陈述句或 `NOT_APPLICABLE` | 该节标题之后 | 该节原先只受 PP-1 约束，不受任何 CTA 边界约束 | 否，`false` 时照常适用 |
| 6 | 自检新增第 17 条：按九行清单逐面扫，对照 `cta_contract` 原文全文；并反查 `false` 分支没被误删 | 自检 16 之后 | b1 的自检 16 没有给出要扫哪些面 | 否，1–16 全部原样保留 |

> **删除审计结论**：b2 对 b1 是**纯增量**。b1 的「事实来源必须蕴含该主张」整节、
> 「CTA 权威顺序」整节、「无 CTA 评论区」前置条件句、自检 15／16，以及继承自 M4 的
> 三级 mode 判据、输入槽位表、CTA 三级表、母版制、PP-1 至 PP-5 正文、无 CTA 评论区两张清单、
> 作者转发语正文、发布前五条检查、非视频形态映射表、关于数据、默认失败模式表、
> `used_fact_refs[]` 三格结构与六处覆盖、用户交付块事实纪律、局部失效与不反向传播、
> 发布实例纪律、自检 1–14、参考文件处置，**逐字保留，一条未删、一条未弱化**。
> 本版只**收紧**，且收紧只发生在 `strict_cta_closed = true` 的那一支。
"""


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def insert_after(text, anchor, block, what):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit("锚点不唯一（%d 次），拒绝构建：%s" % (n, what))
    i = text.index(anchor) + len(anchor)
    return text[:i] + block + text[i:]


def insert_before(text, anchor, block, what):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit("锚点不唯一（%d 次），拒绝构建：%s" % (n, what))
    i = text.index(anchor)
    return text[:i] + block + text[i:]


def main():
    src = io.open(SRC, encoding="utf-8").read()
    src_sha = sha(src)
    out = src
    ins = []

    # 1. strict_cta_closed 状态判定：插在 b1「CTA 权威顺序」之后、「母版制」之前
    a1 = "\n---\n\n## 母版制\n"
    _b1 = CTA_STATE + "\n"
    out = insert_before(out, a1, _b1, "strict_cta_closed 状态判定")
    ins.append(("CTA_STATE", _b1))

    # 2. PP-5 条件化：插在 PP-5 标题之后
    a2 = "\n### PP-5 · 评论区是设计出来的，不是等来的\n\n"
    out = insert_after(out, a2, PP5_COND, "PP-5 条件化")
    ins.append(("PP5_COND", PP5_COND))

    # 3. 作者转发语条件化
    a3 = "\n### 作者转发语\n\n"
    out = insert_after(out, a3, SHARE_COND, "作者转发语条件化")
    ins.append(("SHARE_COND", SHARE_COND))

    # 4. 自检 17：插在自检 16 之后、参考文件之前
    a4 = "\n---\n\n## 参考文件\n"
    out = insert_before(out, a4, SELFCHECK17, "自检 17")
    ins.append(("SELFCHECK17", SELFCHECK17))

    # 5. 头部：name / 版本块
    out = out.replace("name: packaging-content-for-release-m4-b1\n",
                      "name: packaging-content-for-release-m4-b2\n", 1)
    old_yaml = 'successor_version: "m4-b1"\n'
    new_yaml = ('successor_version: "m4-b2"\n'
                'source_skill_b1: "content-production/skills/'
                'packaging-content-for-release-m4-b1/SKILL.md"\n'
                'source_skill_b1_sha256: "%s"\n'
                'b1_fact_fix_inherited_verbatim: true\n' % src_sha)
    if out.count(old_yaml) != 1:
        raise SystemExit("版本块锚点不唯一，拒绝构建")
    out = out.replace(old_yaml, new_yaml, 1)

    # 6. b2 版改了什么
    a5 = "\n---\n\n# Publishing & Packaging（M4 后继版）\n"
    out = insert_before(out, a5, CHANGED, "b2 版改了什么")
    ins.append(("CHANGED", CHANGED))

    os.makedirs(DSTDIR, exist_ok=True)
    io.open(DST, "w", encoding="utf-8").write(out)

    # 继承体核验：移除插入块后必须逐字等于 b1（仅头部两处替换除外）
    back = out
    for _, b in ins:
        back = back.replace(b, "", 1)
    back = back.replace("name: packaging-content-for-release-m4-b2\n",
                        "name: packaging-content-for-release-m4-b1\n", 1)
    back = back.replace(new_yaml, old_yaml, 1)
    inherited_ok = back == src

    # b1 事实修复整块必须逐字在场，不得回退
    b1_fact_start = src.find("\n## 事实来源必须蕴含该主张\n")
    b1_fact_end = src.find("\n---\n\n## 局部失效与不反向传播\n", b1_fact_start + 1)
    fact_block = src[b1_fact_start:b1_fact_end]
    fact_verbatim = bool(fact_block) and out.count(fact_block) == 1
    b1_cta_start = src.find("\n### CTA 权威顺序\n")
    b1_cta_end = src.find("\n---\n\n", b1_cta_start + 1)
    cta_block = src[b1_cta_start:b1_cta_end]
    cta_verbatim = bool(cta_block) and out.count(cta_block) == 1

    m4 = io.open(M4, encoding="utf-8").read()
    inserted_text = "".join(b for _, b in ins)
    rep = {"document": {"id": "PPBS_B2_BUILD_SUCCESSOR_SKILL_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "task_mode": "REBASE",
                        "model_calls": 0, "dify_writes": 0},
           "source_b1": {"file": os.path.relpath(SRC, REPO), "sha256": src_sha,
                         "chars": len(src)},
           "source_m4": {"file": os.path.relpath(M4, REPO), "sha256": sha(m4),
                         "chars": len(m4)},
           "successor_b2": {"file": os.path.relpath(DST, REPO), "sha256": sha(out),
                            "chars": len(out)},
           "inserted_blocks": [{"id": k, "chars": len(b), "sha256": sha(b)} for k, b in ins],
           "inserted_text_chars": len(inserted_text),
           "inserted_text_sha256": sha(inserted_text),
           "inherited_body_byte_identical_to_b1": inherited_ok,
           "b1_fact_section_verbatim_present": fact_verbatim,
           "b1_fact_section_chars": len(fact_block),
           "b1_cta_section_verbatim_present": cta_verbatim,
           "b1_cta_section_chars": len(cta_block),
           "header_replacements": ["frontmatter name", "yaml 版本块"],
           "deleted_or_weakened": []}
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_B2_BUILD_SUCCESSOR_SKILL.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    io.open(os.path.join(EVDIR, "PPBS_B2_INSERTED_TEXT.txt"), "w",
            encoding="utf-8").write(inserted_text)
    print("b1 %d 字 → b2 %d 字，新增 %d 字（%d 块）"
          % (len(src), len(out), len(inserted_text), len(ins)))
    print("继承体逐字节等同 b1：", inherited_ok)
    print("b1 事实修复整块逐字在场：%s（%d 字）" % (fact_verbatim, len(fact_block)))
    print("b1 CTA 权威顺序整块逐字在场：%s（%d 字）" % (cta_verbatim, len(cta_block)))
    print("b2 SKILL.md sha256:", sha(out))
    ok = inherited_ok and fact_verbatim and cta_verbatim
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
