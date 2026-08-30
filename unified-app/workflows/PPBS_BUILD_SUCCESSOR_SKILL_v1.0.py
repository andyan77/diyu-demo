#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继｜Phase B 构建后继 Skill。**零模型调用、零 Dify 写入。**

从 M4 后继版逐字继承，只做**确定性插入**：三个新增块 ＋ 两条自检 ＋ 头部版本块。
一条既有判据都不删、不弱化。插入点用唯一锚点定位，锚点不唯一即拒绝构建。

规则层修复对应 Founder 三项裁决：
  裁决 2 → 新增「事实来源必须蕴含该主张」；
  裁决 3 → 新增「CTA 权威顺序」＋ 给「无 CTA 时评论区」小节加前置条件句；
  两条裁决各配一条自检（无自检的规则只是提醒，不是关卡）。

    python3 PPBS_BUILD_SUCCESSOR_SKILL_v1.0.py
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
SRC = os.path.join(REPO, "content-production/skills/"
                         "packaging-content-for-release-m4/SKILL.md")
DSTDIR = os.path.join(REPO, "content-production/skills/packaging-content-for-release-m4-b1")
DST = os.path.join(DSTDIR, "SKILL.md")
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")

# ---------------------------------------------------------------- 插入块

FACT_SECTION = """
## 事实来源必须蕴含该主张

> 本节是 b1 新增。它是 `used_fact_refs[]` 「找不到对应 `fact_id` 时，只有一条路：不生成它」
> 那一条的**判定细则**，不替代它，也不放宽它。

**什么算「真实行为主张」。** 产出里任何断言**具体人物、组织或品牌在过去或现在实际做过某件事**
的句子，都是真实行为主张。它包括但不限于：某人做过什么、说过什么、一直／长期／向来怎么做、
团队内部怎么决定的、店里／公司里历来的做法。
它**读起来像叙述**，不像"事实陈述"——这正是它最容易被漏掉的原因。

**回指必须是蕴含关系，不是相关关系。** 挂上一个 `fact_id` 不等于有来源。
判定只问一句：**这条来源自己有没有说这件事发生过？**

| 来源里写的 | 能不能推出「他实际长期用过这个方法」 |
|---|---|
| 他的职务、岗位、头衔 | **不能** |
| 他长期接触某类工作、某类人群、某类场景 | **不能** |
| 行业里一般都这么做 | **不能** |
| 这个方法本身是合理的、专业的 | **不能** |
| 来源逐字写了「他用这个方法」「他一直这么做」 | 能 |

**职责不蕴含行为。** 一个人负责某件事，不等于他用过某个具体方法；
接触过某类场景，不等于他形成过某套做法。**从职责推行为，是编造，不是推断。**

**任何限定语都不把无来源变成有来源。** 「这是推断」「基于职责的合理推断」「可能」「据说」
「印象中」「大概」「应该是」，以及正文之外的脚注、括注、说明行、免责句——
**一条都不改变这句话的性质**。读到它的人读到的仍然是一条关于真人的既成事实；
加一句说明不产生任何新证据，只是把问题连同一张便条一起交了出去。

> 这与「用户交付块的事实纪律」是同一条原理的两个面：
> 那一节讲的是**淘汰内容不许带着便条留下**，这一节讲的是**无来源主张不许带着推断标注留下**。
> 两种写法交出去的都是那句错的话。

**没有直接来源时，只有两个出口：**

1. **删除**该真实行为主张——依赖它的那一句、那一段、那一条预埋回答，一起拿掉；
2. **改为不主张真实历史的当前内容表达**——把方法、判断、框架写成**这条内容自己提出的**，
   不挂到任何真人的既往行为上。

这两个出口都不需要任何来源，因此**永远存在**，不构成阻塞。

**局部失效不升级为整任务拒绝。** 一处行为主张没有来源，只删除或改写**依赖它的那个局部分支**：
不依赖它的标题、封面、文案、平台适配、评论区设计**照常完成**；
其余部分的创意深度与成品质量**不降低**。
阻止的是**无依据的具体主张**，不是这项包装任务本身。
**因为一处事实缺口就交白卷、只交一句"资料不足"、或整体拒绝，都是错的。**
"""

CTA_SECTION = """
### CTA 权威顺序

> 本节是 b1 新增。它规定上面那张三级表**什么时候适用**，不改表里任何一行的内容。

**权威顺序（高在前，低者不得放宽高者）：**

```
cta_contract 的用户／上游自然语言原文
  >
已确认的 Content Brief 与任务边界
  >
cta_level
  >
本 Skill 的默认互动方法
```

**1. 上游闭合表达一旦出现，整份包装闭合。**
上游 `cta_contract` 里出现「只保留内容本身」「不做任何引导」「不做关注、评论、收藏」
或**其它等价的明确闭合表达**时，**整份产出**——标题、封面、首帧、发布文案、评论区置顶、
预埋问答、作者转发语、平台变体，一处不漏——**不得要求受众**：

```
购买 · 下单 · 到店 · 预约 · 咨询 · 私信 · 领取
关注 · 评论 · 回复 · 收藏 · 转发 · 分享 · 点赞 · 参与话题
```

**2. 不得用「低风险互动」放宽上游更严格的边界。**
三级表里的「低风险互动」是**上游没有给出更严格边界时**的默认裁量空间。
上游已经闭合时，它**不再适用**——低风险不是豁免。

**同样不得自造豁免类目。** 给某一处表达安一个新名目，说它属于某种"轻的""温和的"
"不算转化的"类别，因此不受边界约束——**这个类别不在任何冻结判据里，叫什么都一样。**
自造类目不产生豁免，只是把越界写成了合规。
边界只能由有权者改版，**执行方不得在产出里把它改写成更宽的一条**。
把上游原文压缩、改述、只挑其中一半来做合规自检——同样是改写。
**自检的对照物必须是 `cta_contract` 的原文本身，不是你对它的复述。**

**3. 内容内部的问题不是 CTA。**
用来表达主题的自问、反问、判断问题——「这件到底该不该买」「我该怎么判断」——
写在口播、文案正文或文字卡里，是**内容本身**，不构成 CTA。

界线只有一条：**这句话是不是在要求受众去做一个动作**（回答、留言、互动、点击、到店……）。

| | 是不是 CTA |
|---|---|
| 「这件到底该不该买？」（正文里的设问，随后自己给出判断） | 不是 |
| 「你会怎么选？」「你先问自己哪个问题？」（句末指向受众，等一个回答） | **是** |
| 「评论区设计：置顶一条能被追问的」（为引出留言而设计的整段） | **是** |

**4. 本节不删除低风险互动能力。**
上游**未明确禁止**，且目标、事实、权限允许时，仍按上面的三级表照常处理——
评论区照常设计，置顶照常写。**收紧只发生在上游已经闭合的那些条上。**
"""

NOCTA_PREFIX = """**先看上游闭合了没有。** 本小节的「可以做」是 `cta_contract` **只禁止业务动作、
未给出闭合表达**时的空间。上游出现「只保留内容本身」「不做任何引导」这类闭合表达时，
按「CTA 权威顺序」第 1 条，评论区**同样不得**要求受众回答、留言或互动——
此时评论区只能写不指向受众动作的内容，或者不写。

"""

SELFCHECK = """15. **（b1）** 产出里每一处「某人／某组织过去或现在实际做过某事」的主张，
    把它和它挂的来源**原文并排读一遍**——**这条来源自己说过这件事发生过吗？**
    只写了职务、岗位、长期接触某类工作，那就是**没有来源**。
    有没有哪一处是靠「这是推断」「基于职责」「可能」这类限定语留下来的？——**限定语不是来源。**
    没有来源的那几处，删掉了还是改成了不主张真实历史的表达？
    删改之后，不依赖它的部分是照常完成的，还是被一起做浅了？
16. **（b1）** 把 `cta_contract` 的**原文**抄到眼前，不看自己的复述——
    它有没有给出闭合表达（只保留内容本身／不做任何引导／不做关注评论收藏）？
    给出了的话，整份产出里还有没有任何一句在**要求受众做动作**：
    句末指向受众等一个回答、评论区设计、引导关注收藏转发点赞、参与话题？
    合规自检的每一行，对照的是原文全部，还是只挑了「不做购买引导」这半句？
    有没有自造一个「低风险互动」「温和引导」之类的类目把某一处放行？
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

    # 1. CTA 权威顺序：插在「CTA 三级接缝」小节之后、「母版制」之前
    a = "\n---\n\n## 母版制\n"
    _b = CTA_SECTION + "\n"
    out = insert_before(out, a, _b, "CTA 权威顺序")
    ins.append(("CTA_SECTION", _b))

    # 2. 无 CTA 评论区小节加前置条件句
    a2 = "评论区是最容易破口的地方 —— 它看起来只是\"互动\"，不像\"转化\"。\n\n"
    out = insert_after(out, a2, NOCTA_PREFIX, "无 CTA 评论区前置条件")
    ins.append(("NOCTA_PREFIX", NOCTA_PREFIX))

    # 3. 事实来源蕴含：插在「局部失效与不反向传播」之前
    a3 = "\n---\n\n## 局部失效与不反向传播\n"
    _b3 = FACT_SECTION + "\n"
    out = insert_before(out, a3, _b3, "事实来源必须蕴含该主张")
    ins.append(("FACT_SECTION", _b3))

    # 4. 自检 15 / 16：插在自检 14 之后、参考文件之前
    a4 = "\n---\n\n## 参考文件\n"
    out = insert_before(out, a4, SELFCHECK, "自检 15/16")
    ins.append(("SELFCHECK", SELFCHECK))

    # 5. 头部：name / 版本块 / 本版改了什么
    out = out.replace("name: packaging-content-for-release-m4\n",
                      "name: packaging-content-for-release-m4-b1\n", 1)
    old_yaml = ('skill_id: "packaging-content-for-release"\n'
                'successor_version: "m4"\n')
    new_yaml = ('skill_id: "packaging-content-for-release"\n'
                'successor_version: "m4-b1"\n'
                'source_skill_m4: "content-production/skills/'
                'packaging-content-for-release-m4/SKILL.md"\n'
                'source_skill_m4_sha256: "%s"\n'
                'boundary_task_id: "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001"\n'
                'founder_adjudication: "unified-app/stages/PPBS_FOUNDER_ADJUDICATION_v1.0.md"\n'
                'increment_only: true\n' % src_sha)
    if out.count(old_yaml) != 1:
        raise SystemExit("版本块锚点不唯一，拒绝构建")
    out = out.replace(old_yaml, new_yaml, 1)

    changed = """
## b1 版改了什么

> b1 只处理**交付边界**，一条包装专业判据都不碰。授权：Founder 裁决 2（事实边界）与裁决 3（CTA 权威顺序）。

| # | 改动点 | 位置 | 为什么 | 删了既有判据吗 |
|---|---|---|---|---|
| 1 | 新增「CTA 权威顺序」整节：`cta_contract` 原文 > Content Brief/任务边界 > `cta_level` > 默认互动方法；上游闭合表达出现时整份产出不得要求受众做任何动作；不得用「低风险互动」或自造类目放宽；内容内部设问不构成 CTA | 插在「CTA 三级接缝」之后 | 三级表把「低风险互动」写成默认可裁量项，没有让上游自然语言原文压过它 | 否，三级表逐字保留 |
| 2 | 「无 CTA 时，评论区能做什么、不能做什么」小节加一句前置条件：其「可以做」只在上游未闭合时适用 | 该小节开头 | 原文「可以做：提一个能一句话回答的具体问题」在上游闭合时会成为破口 | 否，原「可以做／不得出现」两张清单逐字保留 |
| 3 | 新增「事实来源必须蕴含该主张」整节：真实行为主张的定义、蕴含 vs 相关对照表、职责不蕴含行为、限定语不构成来源、两个永远存在的出口、局部失效不升级为整任务拒绝 | 插在「局部失效与不反向传播」之前 | `used_fact_refs[]` 已要求「挂不上号就不生成」，但没有规定**挂上的号必须自己陈述过该行为**；也没有说明推断标注不能替代来源 | 否，`used_fact_refs[]` 三格结构与六处覆盖逐字保留 |
| 4 | 自检新增第 15、16 条 | 自检 14 之后 | 无自检的规则只是提醒，不是关卡 | 否，原 1–14 条全部原样保留 |

> **删除审计结论**：b1 对 M4 后继版是**纯增量**。三级 mode 判据、输入槽位表、CTA 三级表、母版制、
> PP-1 至 PP-5、无 CTA 评论区两张清单、作者转发语、发布前五条检查、非视频形态映射表、关于数据、
> 默认失败模式表、`used_fact_refs[]` 三格结构与六处覆盖、用户交付块事实纪律、局部失效与不反向传播、
> 发布实例纪律、自检 1–14、参考文件处置，**逐字保留，一条未删、一条未弱化**。
> 本版只**收紧**，不放宽；收紧只发生在上游已经给出更严格边界、或事实主张挂不上蕴含来源的那些点上。
"""
    a5 = "\n---\n\n# Publishing & Packaging（M4 后继版）\n"
    out = insert_before(out, a5, changed, "b1 版改了什么")
    ins.append(("CHANGED", changed))

    os.makedirs(DSTDIR, exist_ok=True)
    io.open(DST, "w", encoding="utf-8").write(out)

    # 继承体核验：把插入块逐一移除后，必须逐字等于源（仅头部 name/yaml 两处替换除外）
    back = out
    for _, b in ins:
        back = back.replace(b, "", 1)
    back = back.replace("name: packaging-content-for-release-m4-b1\n",
                        "name: packaging-content-for-release-m4\n", 1)
    back = back.replace(new_yaml, old_yaml, 1)
    inherited_ok = back == src

    inserted_text = "".join(b for _, b in ins)
    rep = {"document": {"id": "PPBS_BUILD_SUCCESSOR_SKILL_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "model_calls": 0, "dify_writes": 0},
           "source": {"file": os.path.relpath(SRC, REPO), "sha256": src_sha, "chars": len(src)},
           "successor": {"file": os.path.relpath(DST, REPO), "sha256": sha(out), "chars": len(out)},
           "inserted_blocks": [{"id": k, "chars": len(b), "sha256": sha(b)} for k, b in ins],
           "inserted_text_chars": len(inserted_text),
           "inserted_text_sha256": sha(inserted_text),
           "inherited_body_byte_identical_to_source": inherited_ok,
           "header_replacements": ["frontmatter name", "yaml 版本块"],
           "deleted_or_weakened": []}
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_BUILD_SUCCESSOR_SKILL.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    io.open(os.path.join(EVDIR, "PPBS_INSERTED_TEXT.txt"), "w",
            encoding="utf-8").write(inserted_text)
    print("源 %d 字 → 后继 %d 字，新增 %d 字（4 块）" % (len(src), len(out), len(inserted_text)))
    print("继承体逐字节等同源：", inherited_ok)
    print("后继 SKILL.md sha256:", sha(out))
    return 0 if inherited_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
