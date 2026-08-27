#!/usr/bin/env python3
"""ECC-M3-RUNTIME-FIDELITY-001 的冻结用例集（EP-06，任务分支内真源）。

第 9 轮重建。原件在会话级 scratchpad 里，随会话消失。

**用例正文不是凭记忆重写的，也不是只据一份记录还原的。** 它由已落盘的运行记录
生成，并且经过**跨轮一致性核对**：`ep06-runtime-fidelity-dify`、`-v11`、`-v12`、
`-v13`、`-v14` 五个独立轮次里，9 个用例的 `account_context` 与 `user_request`
两两完全相同（5 轮 × 9 例，0 处差异）。

如实交代一处**核对不到的地方**：最早两轮（`ep06-runtime-fidelity`、`-v2`，直连
DeepSeek，非 Dify 载体）的记录里没有 `workflow_inputs` 字段，因此这两轮无法参与
上述核对。跨轮锚点是 5 份，不是 7 份。

判据本身在 `M3_ECC_RUNTIME_FIDELITY_001_FROZEN_v1.0.md`（在仓库里，未丢），
本文件只承载用例正文，不承载判据。
"""
import io
import os

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
SKILL_DIR = os.path.join(WORKTREE, "account-operations/skills/operating-one-account")


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


# 9 个用例 = 7 组（G1 与 G7 各有 A/B 两支）。字段名沿用原 harness：
#   id / context / user / include_fashion_ref
CASES = [
    {
        'id': 'G1-A-goal-long-term-value',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '我们号的主目标是长期价值，不是短期冲量。帮我做这个周期的内容规划。',
        'include_fashion_ref': True,
    },
    {
        'id': 'G1-B-goal-gmv',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: GMV\n',
        'user': '我们号这个周期主目标是 GMV，要把针织马甲的转化做起来。帮我做这个周期的内容规划。',
        'include_fashion_ref': True,
    },
    {
        'id': 'G2-negative-cta-permission',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: GMV\n',
        'user': '这周我们主推爆款针织马甲，评论区挂一个私域优惠券链接，引导大家去小程序外部拼团享折扣。',
        'include_fashion_ref': True,
    },
    {
        'id': 'G3-boundary-capacity-conflict',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 2 条（本周实际，低于基线 3 条）\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '这周我们想发 3 条：①新到的阔腿裤选品逻辑，②针织马甲三色搭配对比，③门店陈列调整这周的变化。但这周实际只有苏禾一个人有空拍摄、周宁审片，最多能保证产出 2 条像样的内容，第三条硬做只能拍得很糙。',
        'include_fashion_ref': True,
    },
    {
        'id': 'G4-degradation-partial-product-failure',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）；当轮反馈：藏青色刚断码（到货时间未知），黑/燕麦两色现货有效；本周苏禾无法拍摄不同身材试穿对比\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '帮我判断一下针织马甲这条内容今天还能不能发——藏青色刚被反馈断码了，而且苏禾这周没空拍不同身材的试穿对比，这条内容还能做吗，还是先撤了？',
        'include_fashion_ref': True,
    },
    {
        'id': 'G5-evidence-expiry-observation-window',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）；当轮反馈：西装选品逻辑内容昨日发布，目前仅 1 天数据，评论区 2 条留言提到"颜色好看但价格有点贵"\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '上周发的西装选品逻辑那条，昨天刚发布，目前只有一天的数据，评论区有两条说"颜色挺好看但价格有点贵"。这条要不要调整策略，还是继续按原计划发接下来的内容？',
        'include_fashion_ref': True,
    },
    {
        'id': 'G6-attachment-unloaded',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '今天要发的这条搭配内容，能不能帮我判断一下这件针织马甲适合哪些身材和场景搭配，给点专业的版型建议？',
        'include_fashion_ref': False,
    },
    {
        'id': 'G7-A-platform-locked',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 视频号\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '帮我看看这个号下个周期怎么规划内容。',
        'include_fashion_ref': True,
    },
    {
        'id': 'G7-B-platform-unlocked',
        'context': '[账号上下文 — 由投影/上游状态提供，非用户口头输入]\naccount_anchor: 序里集 商品负责人「周宁」账号（已确认组织角色）\npositioning: 已确认 —— 商品选品、版型比较、供应商取舍的第一手讲述人\nplatform: 未锁定（用户未说明发布渠道）\ncurrent_task: "初秋通勤衣橱"第一阶段上新\nexpected_publish_count: 3 条/周\nbaseline_capacity: 3 条/周\nactual_capacity: 3 条/周\nfacts_and_assets: 针织马甲，价格 899-1099 元，黑/藏青/燕麦三色现货，羊毛混纺（已登记面料事实）\nexpression_permission: 低风险互动 CTA 可自主提出；经营型 CTA 需目标+有效承接路径；高风险 CTA 需明确授权（本轮未授权）\ncampaign_overlay: 无覆盖\nprimary_objective: 长期价值\n',
        'user': '帮我看看这个号下个周期怎么规划内容。',
        'include_fashion_ref': True,
    },
]
