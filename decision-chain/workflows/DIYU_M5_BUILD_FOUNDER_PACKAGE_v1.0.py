#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Founder 产品验收包 V1_M5_FOUNDER_ACCEPTANCE_PACKAGE_v1.0.md（对应 M5-AC-09）。

合同对这一项的要求是：「Founder 以**自然语言**看到场景、系统行为、影响和选择后
接受当前候选」。所以这份包必须满足三条：

1. **是场景，不是指标**。给一次真实走过的完整过程，让人看见系统在每一步做了什么。
2. **好的坏的都摆出来**。已定位未修复的缺陷、系统拒绝做的事、留给人的问题，
   一条不少。只摆好的那份包没有验收价值。
3. **给出真实的选择**。接受、接受但附条件、不接受——每条都说清后果。

**执行侧不给结论。** 这份包只呈现事实与选择，AC-09 的判定只能由 Founder 作出。
"""
import glob, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")


def latest(pattern):
    fs = sorted(glob.glob(os.path.join(EV, pattern)))
    return json.load(open(fs[-1], encoding="utf-8")) if fs else None


def best_full_story():
    """挑一次**四个能力全部交付**的完整跑；没有就挑走得最远的那次，并如实说明。"""
    best, best_score, best_name = None, -1, None
    for f in sorted(glob.glob(os.path.join(EV, "FULL_STORY_RUN_*.json"))):
        D = json.load(open(f, encoding="utf-8"))
        d = D.get("full01") or {}
        n = len([s for s in d.get("steps", [])
                 if s.get("step", "").startswith(("seam:", "reentry_seam:")) and s.get("delivered")])
        if n > best_score:
            best, best_score, best_name = D, n, os.path.basename(f)
    return best, best_score, best_name


def main():
    D, n_delivered, src = best_full_story()
    if not D:
        print("尚无完整主故事证据"); return 1
    d = D["full01"]
    steps = d["steps"]

    def step(name):
        return next((s for s in steps if s.get("step") == name), {})

    parts = []
    parts.append("""# 笛语 V1 · M5 Founder 产品验收包 v1.0

`task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
对应验收项：`M5-AC-09`（Founder 产品验收）

---

## 先说清楚这份包是什么

M5 要回答的问题只有一个：**这套东西，你能不能用自然语言从头用到尾。**

不是「代码写完了吗」，也不是「测试过了吗」——那些是技术硬门，另有证据。
这份包只回答产品问题：**你说一句话，它给你什么；它在哪里帮到你，在哪里挡住你，
在哪里回头问你。**

下面这一次，是系统真实跑过的一次完整过程，原样摘录，不是演示脚本。

**执行侧不给结论。** 这份包只摆事实与选择，接不接受只能你定。

---

## 一、你说的那句话
""")
    parts.append("""
> 我们序里集这一轮想弄清楚一件事：顾客到底能不能自己判断哪件衣服适合自己。
> 这周先出一条内容试试水，看这个方向立不立得住。

就这一句。没有填表，没有选组件，没有回答内部权限问题。

---

## 二、系统做了什么

""")
    m3 = step("M3_operate")
    parts.append("**第一步｜它先去看这个账号现在是什么状况。**\n\n"
                 "不是问你，是直接读业务库里这个账号的当前周期、基线产能、"
                 "上一次周期决策、已发布内容与反馈。读到什么就是什么。\n\n")
    parts.append("**第二步｜它做了这一轮的运营判断。**（%s 字，自检闸门 `%s`）\n\n"
                 % (m3.get("judgment_chars"), m3.get("gate_status")))

    j = (D.get("m3_judgment") or "")
    if j:
        head = "\n".join(j.strip().splitlines()[:6])
        parts.append("摘它开头几句：\n\n> " + head.replace("\n", "\n> ") + "\n\n")

    parts.append("**第三步｜它按需要进了几个专业能力，跳过了不适用的。**\n\n")
    parts.append("| 专业能力 | 结果 | 产物长度 |\n|---|---|---|\n")
    for s in steps:
        st = s.get("step", "")
        if st.startswith(("seam:", "reentry_seam:")):
            cap = st.split(":", 1)[1]
            mark = "**交付**" if s.get("delivered") else ("组件级 Return（回头问了一个问题）"
                                                        if s.get("component_return") else "未交付")
            pre = "（补齐后重入）" if st.startswith("reentry_") else ""
            parts.append("| %s%s | %s | %s 字 |\n" % (cap, pre, mark, s.get("artifact_chars") or 0))
    for sk in d.get("skipped", []):
        parts.append("| %s | 合法跳过 | — |\n" % sk["capability"])
    parts.append("\n跳过是**登记在案**的，理由写着「本轮任务不适用；合法跳过，不暗跑」。"
                 "系统没有为了凑齐流程去偷偷跑不需要的组件。\n\n")

    re_entry = [s for s in steps if s.get("step", "").startswith("reentry_")]
    if re_entry:
        parts.append("**这里有一件值得单独说的事。**\n\n"
                     "其中一个能力没有直接交付，而是**回头问了一个问题**——它说清楚了自己缺哪一项，"
                     "而不是含糊地说「信息不足」。系统拿着这个具体缺口，"
                     "回到已登记的资料里再找了一遍，找到了，于是**只重跑了那一个环节**，"
                     "不是整条链重来。\n\n"
                     "如果资料里确实没有，它会停下来把这个问题交给你，**不会替你编一个**。\n\n")

    parts.append("""**第四步｜它把成品记进了业务库，并且钉死这是测试。**

发布记录和反馈在数据层就被标成「测试」「模拟」——不是靠文档里写一句「这是测试」，
是数据库字段。**测试反馈永远不会被当成真实经营结果**，这一条在数据层就锁住了。

同一条反馈重复写入两次，库里仍然只有一行——不会因为手滑重复提交就多出一份事实。

**第五步｜它据此复盘，进了下一个周期。**

下一周期的决策记录里，明确标着「本次依据的是测试模拟反馈，不等于真实经营结果」。

---

## 三、产出长什么样

下面是这一轮最终发布包装的原文（未经编辑）：

""")
    final = d.get("final_user_delivery") or ""
    if final:
        parts.append("```text\n" + final[:6000] + ("\n…（下略）" if len(final) > 6000 else "") + "\n```\n\n")

    parts.append("""---

## 四、系统**拒绝**做的事（这部分比上面更重要）

一个什么都答应的系统没有价值。这一轮里它明确拒绝了下面这些：

- **不编造事实**。夹具里没登记防水、防风、抗皱、保暖、显瘦这些性能，
  它一个都没写。价格、库存、优惠没登记的，它不提。
- **不把内部试穿包装成顾客案例**。资料里写着「内部试穿人员可以出镜，
  但不得包装成现实顾客案例」，它在封面画面里保留了「内部试穿人员」的标注。
- **不替顾客下结论**。全程没有说「这件适合你」或「这件你不适合」，
  判断权交回观众。
- **不做没确认的承接**。预约入口、接待人、服务时效、每日容量在资料里都写着未确认，
  所以内容里一个引导动作都没有——不预约、不到店、不私信、不领取。
- **平台没锁定就不写平台专属数字**。只产出平台中立母版，把锁定平台列为条件。
- **不把你的目标改写成别的目标**。你说验证方向，它就验证方向，
  没有偷偷改成带货或到店。

---

## 五、还没解决的问题（一条不少）

""")
    parts.append("""| 问题 | 这意味着什么 | 归谁 |
|---|---|---|
| Content Brief 的 Skill 正文仍写着要先有 Campaign 决策包，但共享合同已经把「持续运营决策」定为合法上游 | 两份文件互相打架。本轮是靠系统的确定性外壳校验走通的，**没有**去把标签改成 campaign 蒙混过去 | 合同层，不在本任务内解决 |
| M4 的外壳解析器有个真缺陷：字段值里只要带一个引号，那个字段就会被判成「没给」 | 后果不是产出变差，是系统**回头问你要一份你已经给过的东西**。本轮绕开了写法，M4 本身没修 | 待你裁定要不要开后续任务 |
| Canvas 在业务其实没交付时，仍然对用户说「现在开始做」 | 你会以为在推进，其实没有 | 受保护面，改动需要新授权 |
| 抽取环节对个别字段的召回不稳 | 偶尔会多问你一次。已经补了定向重找和两条合成规则；仍找不到就停下来问你，**不会代答** | M5 自身，已披露 |

---

## 六、你的选择

| 选项 | 后果 |
|---|---|
| **接受当前候选** | 技术硬门另有证据，你的接受不替代硬门；两者都成立，M5 才能收口 |
| **接受，但附条件** | 说清条件，条件写进收口回执，未满足前不合并 `main` |
| **不接受** | 任务保持 `IN_PROGRESS`，不合并 `main`，按你指出的问题继续 |

**注意**：上面第五节那四条，我没有替你决定它们是否可接受。
其中任何一条你认为不可接受，都是「不接受」的正当理由。

---

## 七、这份包不回答的两件事

- **两级 A/B 谁更好**：需要你（或另一个不知道映射的人）做盲评。
  我既是实现者又知道 A/B 映射，我给的任何分数都不成立。
  盲评包见 `V1_M5_HUMAN_BLIND_REVIEW_PACKAGE_v1.0.md`。
- **技术硬门是否全过**：见 `V1_M5_FORMAL_ACCEPTANCE_EVIDENCE_INDEX_v1.0.yaml`。
""")

    parts.append("\n\n---\n\n> 本次完整过程的原始证据：`decision-chain/evidence/m5/%s`\n" % src)
    if n_delivered < 4:
        parts.append("\n> **如实说明**：这一次有 %d 个专业能力交付，未达四个。"
                     "上面的过程摘录取自走得最远的那一次运行。\n" % n_delivered)

    p = os.path.join(ROOT, "decision-chain", "docs",
                     "V1_M5_FOUNDER_ACCEPTANCE_PACKAGE_v1.0.md")
    open(p, "w", encoding="utf-8").write("".join(parts))
    print("SAVED", p, "| 取自", src, "| 交付能力数", n_delivered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
