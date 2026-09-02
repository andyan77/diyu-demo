---
task_id: DIYU-V1-PP-BLOCKER-REMEDIATION-S1-S4-001
blocker: B-01
model_calls_budget: 3
model_calls_used: 0
status: CONFIG_DONE_EMPIRICAL_SMOKE_NOT_EXECUTED
---

# S1 确定性冒烟 · 结果记录

## 配置层（已完成）

`skill_llm` / `recovery_llm` 共用的 `completion_params`（YAML 锚点 `&id001`）：

| 参数 | v1.3 值 | v1.4 值 | provider 是否支持 |
|---|---|---|---|
| `temperature` | 未设置（落到平台默认 `1`） | `0` | 支持（`parameter_rules` 声明 `min:0.0 max:2.0 default:1`） |
| `top_p` | `0.8` | `1` | 支持（`parameter_rules` 声明 `min:0.01 max:1.00 default:1`） |
| `frequency_penalty` | 未设置 | **未加入**（不支持） | **不支持**——`langgenius/deepseek:0.0.20` 的 `deepseek-v4-flash.yaml` `parameter_rules` 未声明此参数 |
| `presence_penalty` | 未设置 | **未加入**（不支持） | **不支持**，同上 |
| `seed` | 未设置 | **未加入**（不支持） | **不支持**，同上 |
| `thinking` | `true` | `true`（不变，本已显式设值） | 支持 |
| `reasoning_effort` | `low` | `low`（不变，本已显式设值） | 支持 |
| `max_tokens` | `384000` | `384000`（不变） | 支持 |

**核实方法**：直接读取本机真实运行的 Docker Dify 实例（`docker-plugin_daemon-1`，`langgenius/dify-plugin-daemon:0.6.3-local`）挂载的插件包文件
`.../langgenius/deepseek-0.0.20@850efe73.../models/llm/deepseek-v4-flash.yaml`，其 `parameter_rules` 字段只列出六项：`temperature`/`max_tokens`/`top_p`/`thinking`/`reasoning_effort`/`response_format`。不是猜测、不是查文档，是这台机器上实际部署的插件包字节本身。

**可复现性的真实边界（如实登记，不假装钉死了）**：`frequency_penalty`/`presence_penalty`/`seed` 在这个 provider/model 组合下**根本不是合法的 Dify 节点配置项**——不是"钉了但可能不生效"，是"写进去 Dify 大概率会在校验层拒绝或静默丢弃"。可复现性因此只能靠 `temperature=0`（贪心解码）+ `top_p=1`（消除额外核采样带来的截断不确定性）实现，且这本身依赖 provider 推理栈在贪心解码下具有确定性——这一点不是本任务能从配置层单方面保证的（大批量 GPU 推理的浮点非结合性是行业内已知的、贪心解码仍可能非严格逐字节确定的成因，与本次改动无关，是外部约束）。S1 的三次同输入连跑冒烟，就是用来实测这层边界在实践中够不够稳，不是走个形式。

## 确定性冒烟（S1 唯一允许的模型调用）—— 未执行

**model_calls_used: 0 / model_calls_budget: 3**

尝试的执行路径与结果：

1. `docker exec docker-api-1 curl ... /console/api/setup`（只读 GET，探测当前 Dify 控制台状态）
   → 被本次会话的 auto-mode 权限分类器拒绝："Blocked by classifier"，未给出可绕过的替代工具。
2. `python3 account-operations/tools/dify_client.py`（仓库既有、此前任务已验证可用的 Console 登录 + Service API 客户端，只读探测 + 列出应用）
   → 同样被 auto-mode 权限分类器拒绝，理由相同。

两条路径均指向同一个判断：**触达本机真实 Docker Dify 实例（哪怕是只读探测）在当前会话权限模式下需要人工显式批准，不是"重试几次就能绕过"的技术性故障**。按分类器自身的提示："如果你确信这个能力对完成用户请求是必需的，应当停下来向用户说明你想做什么、为什么需要这个权限，让用户决定如何处理"——因此这里停下，未强行寻找绕过方式（包括未尝试改用其它 shell 技巧掩饰同一操作）。

**未执行的后果**：无法给出"同一输入连跑 3 次、逐字节比对"的实测结果。**B-01 因此只能记为 `PARTIALLY_CLOSED`**——配置层已经按 provider 真实支持范围做到了能做的最大值，但"配置钉死了" ≠ "实测过确实稳定"，这两件事不能互相顶替，本文件不假装后者已经发生。

## 复验所需的最小动作（供 Founder 授权后执行）

1. 任取一组合法输入（不含商业敏感信息即可）。
2. 用同一输入、同一份 `DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`（可通过 `account-operations/tools/dify_client.py` 的 `import_dsl` 能力发布为一个新的、独立于 v1.3 已发布应用的测试应用）连跑 3 次，`response_mode=blocking`。
3. 比较三次 `outputs`（或至少 `---M4_ARTIFACT---` 块）是否逐字节相同。
4. 完全相同 → 把比较结果（**只贴哈希或字节数是否一致，不贴输出正文**）补进本文件，`status` 改为 `CLOSED`，`model_calls_used` 改为 `3`。
5. 不完全相同 → 定位剩余随机源，如实登记为新的阻断项，不得回改 `status` 为 `CLOSED`。
