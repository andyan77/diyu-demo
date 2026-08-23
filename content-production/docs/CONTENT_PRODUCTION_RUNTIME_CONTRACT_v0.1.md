# 内容生产运行合同 v0.1

适用：内容生产链三份 Skill v0.6（基线提交 `2ec2ba1`）的真实运行。
本文件只定三件事：九个输入槽位、人工回改、plan 与 manifest。

---

## 4.1 九个输入槽位

### 槽位定义与缺失处置

| 槽位 | 主要提供方 | 缺失时 |
|---|---|---|
| `production_profile` | Production Profile | 询问 |
| `expression_subject` | Content Brief／账号责任 | 询问 |
| `content_origin_mode` | Production Profile | 询问，不默认现拍 |
| `subject_domain` | 品牌事实／Content Brief | 无法确定才询问 |
| `duration_band` | Content Brief／制作要求 | 询问 |
| `platform` | 用户本轮选择 | 询问，不自行选择 |
| `cta_contract` | Campaign／Content Brief | 缺失时不生成 CTA |
| `account_positioning` | Matrix／Content Brief | 询问 |
| `constraints[]` | Brief ＋ 品牌事实 ＋ Production Profile | 合并；阻塞项询问 |

### 实际覆盖表

核查对象：仓库现有正式 Content Brief
`decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md`
第 2 节第一份独立 Brief `BRF-SUHE-001`（苏禾｜真实使用验证）。

| 槽位 | 实际来源字段 | 状态 |
|---|---|---|
| `production_profile` | 无对应字段。`制作要求` 只给「一次 3 小时集中拍摄＋30 分钟补录」；`0. 运行结论 · 人员产能条件` 只给逐人工时。**均未给班底规模**（单人手机／1–2 人／小团队／商业制作） | `RUNTIME_REQUIRED` |
| `expression_subject` | `出镜人与事实确认人`：「出镜人为内部演示试穿人员，明确不是现实顾客；苏禾作为账号持续表达者可以出镜说明或旁白解释」→ 映射到五类中的 `NATURAL_PERSON` | `DETERMINISTIC_DERIVATION` |
| `content_origin_mode` | `必须使用的素材`：「VID-C01 中试穿记录一原始片段」（已有素材）＋ `制作要求`：「一次 3 小时集中拍摄＋30 分钟补录」（现拍）→ 按 CS-6 混合来源规则填多值：**现拍 ＋ 已有素材剪辑** | `DETERMINISTIC_DERIVATION` |
| `subject_domain` | `适用 Campaign`：序里集「初秋通勤衣橱」第一阶段；证据地图全部为商品事实、试穿记录与陈列 → 对应 `industry-conditions.md` 的「服装 / 门店零售」 | `DETERMINISTIC_DERIVATION` |
| `duration_band` | `制作要求` 明写「最终发布平台未确认前，**不进入平台规格的逐镜头、秒数与格式设计**」——秒数被显式推迟，Brief 不承载该值 | `RUNTIME_REQUIRED` |
| `platform` | `0. 运行结论 · 当前未成立条件`：「最终发布平台未确认」；`发布条件`：「最终发布平台由 Founder 锁定」 | `RUNTIME_REQUIRED` |
| `cta_contract` | `CTA 或无 CTA 的决定`：「本条无 CTA……更推荐本条不加」——是明确的「无 CTA」裁决，不是缺失 | `DIRECT` |
| `account_positioning` | `账号与本轮责任`：「苏禾，独立参战账号，零售搭配负责人；本轮负责……」＋ `账号关系姿态` | `DIRECT` |
| `constraints[]` | `明确不得表达`（10 条）＋ `发布条件` ＋ `降级条件` ＋ `取消或不发条件` ＋ `事实、观察、专业判断与待验证变量的区分` | `DIRECT` |

状态取值只使用：`DIRECT` / `DETERMINISTIC_DERIVATION` / `RUNTIME_REQUIRED` / `NOT_APPLICABLE` / `MISSING_BLOCKING`。

本次核查结果：`DIRECT` 3 项、`DETERMINISTIC_DERIVATION` 3 项、`RUNTIME_REQUIRED` 3 项、
`NOT_APPLICABLE` 0 项、`MISSING_BLOCKING` 0 项。

### 第一次真实生产运行的硬要求

九项必须**各有明确值或显式 `NOT_APPLICABLE`**。

不允许依靠隐藏默认值伪装完成。三份 Skill 自身带的默认值（如 Creative Script 输入表里的
「默认单人手机」「默认现拍」「默认短档」「默认平台中立母版」）在**工作流无人可问**时才允许使用，
且必须写进输出的 `assumptions[]`。生产运行不得把这些默认值当成上游已确认输入。

上表三项 `RUNTIME_REQUIRED`（`production_profile` / `duration_band` / `platform`）
在真实生产运行开始前必须由人给出。其中 `platform` 不得由任何 Skill 或工作流自行选择。

---

## 4.2 人工回改

### 下游可能发回什么

Production Director 可能输出：

```text
return_to_script[]
```

Publishing & Packaging 可能输出：

```text
return_to_script[]
return_to_production[]
```

**第一版只汇总建议，不自动回环。** 系统不得因为收到建议就重跑任何一段。

### 人的四个选项

- 全部拒绝；
- 接受部分；
- 全部接受；
- 暂停。

### 接受之后发生什么

接受 `return_to_script[]` 后：Creative Script 重新运行。

接受 `return_to_production[]`（且未接受 `return_to_script[]`）后：Production Director 重新运行。

### STALE 的触发点

**STALE 的触发点是「上游重跑后实际改了内容」，不是「人接受了建议」。**

依据：v0.6 的 Creative Script 输入表里，`return_from_downstream[]` 的处置写明
「**收到时必须逐条回应：接受并改写、或说明为什么不改。不得沉默**」——
也就是说，Creative Script 重跑后完全可能逐条回应「不改」，并给出理由。
这时下游产物仍然有效。若按「人接受建议」就置 STALE，会把两段仍然有效的产物白白作废。

因此：

| 上游重跑后的实际结果 | 下游产物状态 |
|---|---|
| Creative Script 改写了脚本内容 | 原 Production Director 与 Publishing & Packaging 产物转 `STALE` |
| Creative Script 逐条回应「不改」，脚本内容未变 | 下游产物**不转** `STALE`，保持原状态 |
| Production Director 改写了 `realization_plan` 或 `capture_plan` | 原 Publishing & Packaging 产物转 `STALE` |
| Production Director 回应「不改」，产物内容未变 | Publishing & Packaging 产物**不转** `STALE` |

「实际改了内容」以重跑前后产物正文的哈希比对为准，不以模型自述为准。
哈希相同即判定未改；哈希不同即判定已改。

### 被接受的建议写到哪里

写入：

```text
return_from_downstream[]
```

每条至少包含：

| 字段 | 内容 |
|---|---|
| `source_skill` | 建议来自哪一段（Production Director／Publishing & Packaging） |
| `target_location` | 要改的具体位置（哪一个 beat、哪一句） |
| `requested_change` | 要求改成什么 |
| `reason` | 为什么要改 |

### 重跑的发起

**每一次重跑必须再次由人发起。** 系统不得自动连跑，不得因为上一次接受而预授权下一次。

---

## 4.3 plan 与 manifest

### 拍摄前

拍摄前只有：

```text
realization_plan
```

`realization_plan` 是计划，不是兑现记录。它不得被当作 manifest 使用，
也不得据此声称任何 beat 已被覆盖。

### 素材回来之后

由 Production Director 按 beat 对位生成：

```text
realization_manifest
```

固定字段：

| 字段 | 内容 |
|---|---|
| `beat_id` | 脚本段落 ID |
| `covered_by_units[]` | 覆盖该 beat 的素材单元 |
| `asset_locator` | 时间码、图片序号或文件位置 |
| `fact_visual_support` | 有／没有／有，但不够 |
| `uncovered_part` | 未兑现部分 |
| `resolution` | 补拍／降级／删除／保留未完成 |

### 什么不是 manifest

**「拍了 42 分钟」「有 36 张图」不是 manifest。**

素材总量、素材清单、拍摄日志都不是 manifest。manifest 的最小单位是 **beat**：
没有逐 beat 的对位关系，就没有 manifest。

### 模式判断

| 条件 | 模式 |
|---|---|
| 全部 beat 都有对位覆盖 | `FINAL` |
| 部分 beat 有对位覆盖 | `MIXED` |
| 没有 beat 级 manifest | `PRE` |

Publishing & Packaging 在 `PRE` 模式下不得声称已验证 `realized_payoff`，
不得伪造 `realization_manifest`，不得把 PRE 包装写成正式成片已经完成。
