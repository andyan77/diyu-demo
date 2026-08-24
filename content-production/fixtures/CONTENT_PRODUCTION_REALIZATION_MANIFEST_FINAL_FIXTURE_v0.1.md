# 拍后 realization_manifest 夹具 · 完整覆盖样本

`SIMULATION_ONLY — 本文件仅用于验证拍后覆盖记录分支，不代表真实拍摄、真实素材或真实发布。`

---

## 一、这份夹具是什么

| | |
|---|---|
| **是** | 一份**模拟的** beat 级拍后覆盖记录，按 P04 真实产出的 Creative Script Final（5 条 beat）与 Production Director `realization_plan`（9 个拍摄单元）逐条对位而成 |
| **不是** | 不是真实拍摄结果。没有任何一段素材真实存在，所有素材编号与时间码均为构造值 |
| **这一份的特点** | 五条 beat 的画面支撑全部为「有」，没有任何需要处置的缺口。 |
| **与原件的差异** | 本件以 `CONTENT_PRODUCTION_REALIZATION_MANIFEST_FIXTURE_v0.1.md` 为基础，**只改 S4 一节**：画面支撑从「有，但不够」改为「有」，补入足以支撑该比较的模拟素材时长与一张全身静帧，`uncovered_part` 置空，`resolution` 写明无需处理。其余四条 beat、全部事实、覆盖单元与时间码**逐字相同**。 |
| **上游基线** | Creative Script Final SHA-256 前 16 位 `d0ed0e4c0c389ab1`；Production Director Final `badb41c5cd94de16`。**两份均未被本夹具修改** |

**覆盖关系不是造出来迁就结论的。** beat 与单元的对应关系直接取自 PD 每个单元自己写的「对应 beat」一栏，
本夹具**没有**修改 Creative Script 或 `realization_plan` 中的任何一个字。

素材编号一律带 `SIM-` 前缀，时间码为构造值。**本文件不含任何真实文件路径**，也不指向任何真实存在的素材。
**本文件不声称任何真实拍摄已经完成。**

---

## 二、交付给运行的 manifest 正文

> 以下标记之间的内容，与实际传入 `realization_manifest` 槽位的文本**逐字相同**。
> 本节之外的文字**不进入模型输入** —— 它们含有对本轮预期结论的描述，
> 写进输入会污染「`mode` 由模型自行推导」这一验证项。

<!-- RUNTIME_PAYLOAD_BEGIN -->
SIMULATION_ONLY —— 以下为模拟的拍后覆盖记录，不代表真实拍摄、真实素材或真实发布。所有素材编号带 `SIM-` 前缀，时间码为构造值，不指向任何真实文件。

# realization_manifest（beat 级拍后覆盖记录）

对位基准：Creative Script Final 的 `script_beats[]`（S1—S5），与 Production Director `realization_plan` 的 `capture_plan.units[]`（U1a、U1b、U2、U3、U4a、U4b、U5、U6、U7）。单元与 beat 的对应关系取自 PD 每个单元自己登记的「对应 beat」。

## S1

| 字段 | 内容 |
|---|---|
| `beat_id` | S1 |
| `covered_by_units[]` | U1a、U1b |
| `asset_locator` | U1a → `SIM-SHOT-SUHE-01` 00:00:04–00:00:09（苏禾直对镜头开场，面前放试穿记录打印件，5 秒）<br>U1b → `SIM-VID-C01` 00:02:14–00:02:19（试穿者穿着完整组合的整身中景，三件商品在同一帧内可分辨，5 秒） |
| `fact_visual_support` | 有 —— 涉及 `BRF-SUHE-001-F01`（三件商品在画面中可辨识）、`BRF-SUHE-001-F06`（演示情境的身份标注可在画面内完成） |
| `uncovered_part` | 无 |
| `resolution` | 不适用 |

## S2

| 字段 | 内容 |
|---|---|
| `beat_id` | S2 |
| `covered_by_units[]` | U2、U3 |
| `asset_locator` | U2 → `SIM-VID-C01` 00:07:38–00:07:44（会议演示空间内整身，试穿者的点头动作发生在 00:07:41，6 秒）<br>U3 → `SIM-VID-C01` 00:12:03–00:12:10（连续生活场景内同一套穿着的整身，试穿者的停顿发生在 00:12:06，「太正式了」原声在 00:12:07–00:12:08，7 秒） |
| `fact_visual_support` | 有 —— 涉及 `BRF-SUHE-001-F02`、`BRF-SUHE-001-A01`（点头动作在画面内）、`BRF-SUHE-001-A02`（停顿与该句表达在画面与原声内）、`BRF-SUHE-001-A03`（该动作与表达已获授权用于 U2、U3） |
| `uncovered_part` | 无 |
| `resolution` | 不适用 |

## S3

| 字段 | 内容 |
|---|---|
| `beat_id` | S3 |
| `covered_by_units[]` | U4a、U4b |
| `asset_locator` | U4a → `SIM-VID-C01` 00:18:20–00:18:25（手部松开衬衫领口的特写，手与衣物均可辨析，5 秒）<br>U4b → `SIM-VID-C01` 00:18:25–00:18:29（袖口折起一层的特写，折起前后的层次变化可见，4 秒） |
| `fact_visual_support` | 有 —— 涉及 `BRF-SUHE-001-F03` 中「保留西装与阔腿裤、放松衬衫领口与袖口」这一部分；画面同时可见西装与阔腿裤未被更换 |
| `uncovered_part` | 无 |
| `resolution` | 不适用 |

## S4

| 字段 | 内容 |
|---|---|
| `beat_id` | S4 |
| `covered_by_units[]` | U5 |
| `asset_locator` | U5 → `SIM-VID-C01` 00:24:02–00:24:09（试穿者着西装外套，7 秒）→ 紧接 00:24:09–00:24:20（脱下西装外套后单穿衬衫与阔腿裤，11 秒，**全身完整入画，含裤脚与整体轮廓**）。两段时间码在同一 clip 内连续相邻<br>补充静帧 → `SIM-STILL-C01-SO` @ 00:24:16（单穿状态全身正面定格，肩线、衣长、裤脚同框可辨） |
| `fact_visual_support` | **有** —— 涉及 `BRF-SUHE-001-F03` 中「比较脱下西装后的单穿效果」这一部分，以及 `BRF-SUHE-001-A04`。脱前脱后同属一段连续记录，且单穿状态有完整全身画面 |
| `uncovered_part` | 无 |
| `resolution` | 无需处理。单穿画面时长与取景均足以支撑「脱下西装后单穿的整体效果」这一比较，不存在需要补拍、替换或降低承诺的缺口 |

## S5

| 字段 | 内容 |
|---|---|
| `beat_id` | S5 |
| `covered_by_units[]` | U6、U7 |
| `asset_locator` | U6 → 三张静帧，均截自 `SIM-VID-C01`：`SIM-STILL-C01-SH` @ 00:31:08（肩部）、`SIM-STILL-C01-SL` @ 00:31:12（袖口）、`SIM-STILL-C01-TR` @ 00:31:15（裤脚）。三张均未含脸部<br>U7 → `SIM-SHOT-SUHE-02` 00:00:11–00:00:19（苏禾真人直对镜头完成接力收束，8 秒） |
| `fact_visual_support` | 有 —— 涉及 `BRF-SUHE-001-F05`（肩部、袖长、裤长三个待验证位置各有独立可辨的画面）。三张静帧只呈现位置本身，画面内不含任何表情判断 |
| `uncovered_part` | 无 |
| `resolution` | 不适用 |

---

## 本记录的适用边界

**上表的覆盖结论只在模拟测试范围内成立。** 这份记录中没有任何一段素材真实存在：所有 `SIM-` 编号与时间码都是为验证流程而构造的。它可以用来判断「拿到这样一份覆盖记录之后应当怎么做」，**不能**用来判断任何真实素材的可用性，也**不能**作为任何内容可以真实发布的依据。
<!-- RUNTIME_PAYLOAD_END -->
