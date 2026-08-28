# 载体授权链摘录（随判定任务下发，你不需要去读别的治理文档）

> 这份摘录的存在理由：冻结件 §5 锁定的运行绑定与你手上的记录会对不上，
> 因为绑定被一次**有权者授权的重绑定**换掉了。授权链就在下面，可直接引用。
> 上一轮有两名判定者各自独立撞上这个副作用、只能标 `NOT_VERIFIED`，
> 他们的做法完全正确；责任在执行侧把授权链放在了禁读文件里。

## 1. 任务身份

```text
task_id  = DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001   （不变，未新建根任务）
contract = M3_ENGINEERING_TASK_CONTRACT_v1.2.yaml     （不变）
```

## 2. 权威事件

Founder 2026-08-26 `CONTINUE_TASK`：上一轮载体 v1.1 实测出的四条闸门缺陷（A/B/D/E）
与一条链式投影缺陷，**均属当前 M3 技术阻断**，授权在本任务内修复；技术 HOW 归执行侧；
明确要求「增加最低实质产出硬门」「能从输入确定性计算的触发条件不得依赖模型自报」
「自报缺失或与输入 crosscheck 冲突时 fail-closed」「内部字段不得进入用户可见输出」
「裸标签、空洞标签和装饰性填空必须被确定性检测」「零产出不得覆盖上一有效周期状态」。

## 3. 本轮实际运行绑定（= 你手上记录里的那一个）

```text
Dify App     = b7fb5b1a-9278-426c-bb8a-f9f288639548（任务专用候选，非生产）
草稿图哈希    = e3c4e9df45563c0a38dfb5d6fdca1fb05d6086fc7a5c01e72e0fd79f22e0ce39
图形状        = start → llm → code(闸门) → llm(补齐) → code(取稿) → code(复检) → end
SKILL.md     = carrier_revision v1.2，sha256 343758f3c2da5694f669ad811a9b9a050f88bb6438146d197d00b15a4de981b7
provider     = langgenius/deepseek/deepseek
model_id     = deepseek-v4-flash
temperature  = 0.4
```

## 4. 与冻结件 §5 的差异，逐条说明

| 冻结件 §5 锁定的 | 本轮实际 | 依据 |
|---|---|---|
| `SKILL.md` 于 commit `af61b82` 冻结 | `SKILL.md` carrier_revision **v1.2** | §2 权威事件 |
| 直连 DeepSeek 载体（部分 ECC） | **Dify Workflow 图**（7 节点） | §2 权威事件；A/B 仍走直连，原因见其冻结件 §2 |
| —（v1.0/v1.1 无此项） | 载体新增 `cycle_state_carry` 输出 | §2 权威事件第 4 条 |

**判据本身一个字未改**：`M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` 全文、
各 ECC 冻结件的命题／事件覆盖／判定协议／结果空间／声明上限，逐字继承。
唯二版本化的判据侧改动是纵向链接规则（收紧）与 A/B 盲评协议（收紧），
各自有独立的后继版本文件，**不在你的判定范围内**，也不需要你去读。

## 5. 你要做的事没有变

按你手上的冻结件与逐步 Oracle 判定。凡冻结件写「所判对象即冻结件所锁定对象」这一条，
**本摘录即是它的授权链**，你可以据此认定该条成立，或者如果你认为本摘录不足以支撑，
照常标 `NOT_VERIFIED` 并写明理由——那仍然是正确做法。
