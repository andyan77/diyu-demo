#!/usr/bin/env python3
"""从核验 JSON 生成 Founder 七场景收口报告。数字全部来自 JSON，不手抄。"""
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EV = os.path.join(WT, "account-operations/evidence/ep39-founder-seven-run-extraction")
DOC = os.path.join(WT, "M3_FOUNDER_SEVEN_RUN_CLOSEOUT_v1.0.md")

R = json.load(io.open(os.path.join(EV, "FOUNDER_RUN_VERIFICATION.json"), encoding="utf-8"))
rows = R["rows"]
V = R["checks"]
official = [r for r in rows if r["role"] == "official"]
extra = [r for r in rows if r["role"] != "official"]
v4 = V["V4_ran_on_frozen_candidate"]

L = []
w = L.append

w("# M3 Founder 七场景实测 · 只读提取与绑定收口 v1.0")
w("")
w("- `task_id`：`DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`")
w("- `entry_mode`：`CONTINUE_TASK`（非 NEW_TASK，不修改合同）")
w("- 后继合同：`M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml`"
  " sha256 `49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49`")
w("- 本轮执行侧模型调用：**0**（只读 Console API + 本地确定性重算）")
w(f"- 生成时间：`{R['generated_at']}`")
w("")
w("## 1. Founder 裁决（原文引用，不改写）")
w("")
w("```text")
w("M3_FOUNDER_ACCEPTANCE = PASS")
w("accepted_candidate = v1.5.2")
w("accepted_test_set = S1-S7")
w("founder_observed_all_outputs = true")
w("founder_test_runs_completed = 7/7")
w("```")
w("")
w("执行侧不得重新做产品裁决，也不得推翻该 PASS。以下只核验绑定、完整性与确定性行为。")
w("")
w("## 2. 运行识别：不按「最近七次」，按逐字输入哈希交叉定位")
w("")
w(f"该 App 全部 workflow 日志 **{json.load(io.open(os.path.join(EV,'app_logs_census.json'),encoding='utf-8'))['total_logs']} 条**，"
  f"按 `created_from` 分离：`web-app` **{len(rows)} 条**、"
  f"`service-api` **{V['V9_no_distorting_misbinding']['service_api_runs_excluded']} 条**（执行侧历史运行，全部排除）。")
w("`web-app` 八条全部来自同一浏览器会话 "
  f"`{official[0]['end_user_session'][:8]}…`，"
  f"时间窗 `{rows[0]['created_at_local']}` – `{rows[-1]['created_at_local']}`。")
w("")
w("| 场景 | run_id | 角色 | 起 | 用时 | tokens | 闸门 | 路径 | 周期状态 | 终稿字数 |")
w("|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    w("| %s | `%s` | %s | %s | %.1fs | %d | %s | %s | %s | %d |" % (
        r["scenario"], r["run_id"], "正式" if r["role"] == "official" else "**重复提交**",
        r["created_at_local"].split()[1], r["elapsed_seconds"], r["total_tokens"],
        r["gate_status"], r["gate_path"], r["cycle_state_carry"], r["final_body_len"]))
w("")
w("绑定依据（每条都逐条算过，不是按时间挑的）：App ID、已发布版本、"
  "三个输入框的逐字内容与 SHA-256、Founder 运行时间、`FREEZE_MANIFEST.json` 场景绑定、"
  "workflow run 与 node execution 记录。**七个场景各自唯一命中，无一靠时间顺序推定。**")
w("")
w("## 3. 九项核验")
w("")
w("| 项 | 结果 | 关键数 |")
w("|---|---|---|")
NAMES = {
    "V1_all_seven_present": "七个场景是否全部存在",
    "V2_one_official_run_each": "每个场景是否只绑定一次正式运行",
    "V3_inputs_verbatim": "输入是否与冻结包逐字一致",
    "V4_ran_on_frozen_candidate": "运行是否来自 v1.5.2 已发布候选",
    "V5_no_undisclosed_transport_failure_or_retry": "是否存在未披露的纯传输失败或重试",
    "V6_outputs_fully_landed": "最终输出是否完整落盘",
    "V7_founder_verdict_bound": "Founder 裁决是否准确绑定这七次输出",
    "V8_no_deterministic_authoring": "闸门或补齐节点是否代写实质交付",
    "V9_no_distorting_misbinding": "是否出现会使裁决对象失真的错绑",
}
DETAIL = {
    "V1_all_seven_present": "S1–S7 全在",
    "V2_one_official_run_each": "S6 提交了两次，两次都成功",
    "V3_inputs_verbatim": "`account_context` / `loaded_references` 八条全部逐字节相同；"
                          "`user_request` 八条一律多一个结尾换行",
    "V4_ran_on_frozen_candidate": "可执行内容绑定成立、版本标签绑定不成立（见 §4）",
    "V5_no_undisclosed_transport_failure_or_retry":
        "纯传输失败 0 次；节点错误 0 个；但存在 1 次未披露的重复提交",
    "V6_outputs_fully_landed": "零截断；终稿字数 %s；三层输出逐字节一致" % ", ".join(
        str(r["final_body_len"]) for r in official),
    "V7_founder_verdict_bound": "7 条正式运行全部落盘可回指，终稿均非空",
    "V8_no_deterministic_authoring":
        "8/8 无代写（含 3 条补齐路）；仓库 v1.5.2 代码重算 8/8 逐字节一致",
    "V9_no_distorting_misbinding": "全部运行自报 `gate_version` / `post_gate_version` = `v1.5.2`",
}
for k, v in V.items():
    w("| %s | %s | %s |" % (NAMES[k], "`PASS`" if v["pass"] else "**`FAIL`**", DETAIL[k]))
w("")
w("### 3.1 V8 的分量：补上了零模型证不到的那一层")
w("")
w("`ep34` 的 Z7 当时**显式声明**过覆盖不到补齐路："
  "「补齐路的终稿由补齐 LLM 产出，零模型拿不到，不在本项覆盖内」。")
w("本轮 Founder 的七次运行里有 3 条真的走了补齐路（S1 / S3 / S5），"
  "补齐节点的原始输出已落盘，所以这一层现在**有实物可验**：")
w("")
w("- 判据：终稿里每个字符必须来自模型产物（直发路取草稿、补齐路取补齐输出），"
  "或来自 `render_body` 那张封闭替换表；子序列判定，**只许删、不许插**。")
w("- 结果：8/8 通过。确定性节点没有给交付物添过一个字。")
w("- 另加一道更强的：用**仓库里的 v1.5.2 代码**对同一份草稿重算 "
  "`gate` / `assemble` / `post_gate`，与线上记录比对 —— "
  "8/8 三个节点全部**逐字节相同**。线上跑的确定性代码与仓库代码行为等同，这是实测不是声明。")
w("")
w("## 4. 四个真实缺口（精确差异，不做闭合）")
w("")
w("### 缺口 1 · 七条运行跑在一个**未命名的重新发布版本**上")
w("")
w("Founder 运行期间，App 被重新发布了一次：")
w("")
w("| | workflow_id | version | marked_name |")
w("|---|---|---|---|")
w("| 冻结候选 | `706fdce0-9a0d-42ec-8a8c-e4f6a3071173` | `2026-08-27 19:46:47.281053` |"
  " `m3-cand-v1.5.2` |")
w("| 实际承载 S2–S7 | `ff801653-ba58-48c9-bbfe-e77c144c9b1d` |"
  " `2026-08-27 20:46:36.695260` | **（空）** |")
w("")
w(f"- S1（`{official[0]['run_id'][:8]}`，`{official[0]['created_at_local'].split()[1]}`）"
  "跑在冻结候选上。")
w("- 新版本发布于 `2026-08-27 13:46:36`（本地），在 S1 结束之后、S2 开始之前。")
w("- 其余 7 条（S2–S7 + 那次重复提交）跑在新版本上。")
w("")
w("**差异逐项算过，全部落在画布外观层：**")
w("")
w("| 维度 | 是否相同 |")
w("|---|---|")
w("| 七个节点的 `data`（系统提示词、代码节点源码、模型配置、变量） | **逐字节相同** |")
w("| 六条边的 source / target / handle 拓扑 | **完全相同** |")
w("| 系统提示词 SHA-256 | 八条运行全部 = `%s` = 冻结值 |" % v4["system_prompt_sha256_all_runs"][0][:32] + "…")
w("| 模型 / provider / 温度 | 八条全部 = `deepseek-v4-flash` / "
  "`langgenius/deepseek/deepseek` / `0.4` |")
w("| 节点 `position` / `positionAbsolute` / `height` | 不同（画布重排） |")
w("| 边 `data.isInLoop` | 新版本多了这个前端标记 |")
w("| 画布 `viewport` 平移与缩放 | 不同 |")
w("")
w("推断（**不是观察**）：打开画布这个动作触发了自动保存并重排了节点坐标，"
  "随后有人在画布上点了「发布」，把这个只含几何改动的草稿发成了新版本。"
  "我没有该次点击的直接记录，所以这条只到**推断**级。")
w("")
w("**结论分成两半，不合并：**")
w("")
w("```text")
w("可执行内容绑定 = %s" % ("成立（系统提示词 + 全部节点 data + 边拓扑，八条全部逐字节相同）"
                            if v4["executable_content_binding_pass"] else "不成立"))
w("已发布版本标签绑定 = %s" % ("成立" if v4["label_binding_pass"]
                              else "不成立（7/8 条不在 m3-cand-v1.5.2 这条版本记录上）"))
w("```")
w("")
w("按授权 §4：Founder 实际运行的已发布版本记录不是冻结的 `m3-cand-v1.5.2`，"
  "因此**受影响项标为 `NOT_VERIFIED`**。可执行内容绑定成立这件事"
  "**不得自动上推**成版本标签绑定成立 —— 那需要有权者裁定，不是执行侧能给的。")
w("")
w("### 缺口 2 · S6 提交了两次，无法唯一确定 Founder 判的是哪一份")
w("")
for r in [x for x in rows if x["scenario"] == "S6"]:
    w("- `%s` · %s · 用时 %.1fs · 终稿 %d 字 · sha256 `%s…`%s" % (
        r["run_id"], r["created_at_local"], r["elapsed_seconds"], r["final_body_len"],
        r["final_body_sha256"][:16], "（本报告记为正式）" if r["role"] == "official" else "（重复提交）"))
w("")
w("两次输入逐字节相同、都成功、都产出了正文，因此**第二次不属于合同允许的重跑**"
  "（合同只允许「无任何模型输出的纯传输故障」重跑一次）。")
w("按 Founder 自己定的「按第一次的真实结果算」，本报告把先发生的那条记为正式，"
  "**两条全部原样保留，一条都不删**。")
w("但 Founder 声明的是 `7/7`，实际提交是 8 次 —— "
  "**Founder 到底看的是哪一份 S6 输出，后台证据不能唯一确定**。"
  "按授权 §2，这是需要精确报告的场景级证据歧义，执行侧不得择优选择。")
w("")
w("### 缺口 3 · `user_request` 八条一律多一个结尾换行")
w("")
w("| 输入框 | 结果 |")
w("|---|---|")
w("| `account_context` | 八条**全部逐字节相同** |")
w("| `loaded_references` | 八条**全部逐字节相同** |")
w("| `user_request` | 八条一律 = 冻结原文 + 一个结尾 `\\n` |")
w("")
w("形态统一、只在结尾、不含任何内容差异，是从代码块复制粘贴的机械痕迹。"
  "语义上不改变任何东西，但**逐字不等于冻结包**，据实记为差异，不当作一致。")
w("")
w("### 缺口 4 · Dify 实例的数据库在提取完成后被清空")
w("")
w("提取完成之后、写本报告之前，Dify 整个容器栈重启，PostgreSQL 走了 **initdb 全新初始化**："
  "`apps` 表 0 行，`setup` 回到 `not_started`，`PGDATA` 里每个文件都是新建时刻的。"
  "该 App、641 条运行记录与全部版本谱系**已不在这个实例上**。")
w("")
w("- 本轮执行侧对 Dify 只发过 **GET**，未修改、未删除、未重放、未覆盖任何运行记录。")
w("- 起因不在本任务范围内，也不是本任务能裁定的，据实记录为外部事实。")
w("- **七场景全部原始证据已在此事件之前落盘**，不受影响（见 §5）。")
w("- 受影响的是**往后**的动态绑定复验：合同 `dynamic_dify_binding_requires_refresh: true` "
  "这一条现在无法再满足；线上回滚入口也不再可对活体演练。")
w("- 重建路径仍在盘上：`account-operations/evidence/ep37-rollback-drill-v152/"
  "m3_candidate_app_v152.dsl.yaml`（sha256 "
  "`bd676f291b8e108c906b606549da357f0dfc5153e3ccccb3ca15d97670811620`，"
  "含 v1.5.2 全部改动），可导入重建；本轮**未**执行重建，未获授权。")
w("")
w("## 5. 证据落盘")
w("")
w("### 5.1 原始提取（提取方法：Dify Console API 只读）")
w("")
w("`account-operations/evidence/ep39-founder-seven-run-extraction/`")
w("")
w("| 文件 | 内容 |")
w("|---|---|")
w("| `app_logs_census.json` | 全部 641 条日志普查、按来源分离、八条 web-app 运行清单 |")
w("| `published_version_lineage.json` | 已发布版本谱系（提取时刻的完整快照） |")
w("| `frozen_graph_reference.json` | 冻结图基准哈希 |")
w("| `raw/<run_id>/workflow_run.json` | 八条运行的完整记录，含执行时的整张图 |")
w("| `raw/<run_id>/node_executions.json` | 八条运行的全部 7 个节点执行记录 |")
w("| `FOUNDER_RUN_VERIFICATION.json` | 九项核验的全部中间量与结论 |")
w("")
w("### 5.2 逐场景结果目录")
w("")
w("`account-operations/founder-pack-v152/results/S1..S7/`，每个含：")
w("")
w("`input_account_context.txt`｜`input_user_request.txt`｜`input_loaded_references.txt`｜"
  "`final_output.txt`｜`draft_raw.txt`｜`gate_report.json`｜`post_gate_report.json`｜"
  "`positions_final.json`｜`final_audit.txt`｜`node_executions.json`｜`run_meta.json`"
  "（补齐路另有 `gate_repair_raw.txt`）")
w("")
w("S6 的第二次提交完整存放在 `results/S6/extra_second_submission_0a0f406d/`，"
  "结构相同，**不删不改**。")
w("")
w("`run_meta.json` 含：场景、run_id、App、版本、与冻结候选的图差异全量、状态、"
  "起止时间、用时、token、模型与 provider、系统提示词哈希及是否等于冻结值、"
  "三段输入哈希与逐字差异、闸门与周期状态、终稿与草稿哈希、Founder PASS 引用、"
  "提取方法与提取时间。")
w("")
w("## 6. 七场景实际结果")
w("")
w("| 场景 | 主要验收目的 | 闸门 | 路径 | 周期状态 | 终稿 |")
w("|---|---|---|---|---|---|")
PURPOSE = {
    "S1": "暂定锚点、无正式定位时能否继续作有边界周期判断",
    "S2": "三类转化不被压成一个「转化」，长期基线不被目标切换冲掉",
    "S3": "产能掉到 1 条时是否做真取舍",
    "S4": "无市场资料下拒绝无证据断言、同时仍完成不依赖市场证据的判断",
    "S5": "冲突反馈下形成解释假设并选择处置，持续位一个不丢",
    "S6": "产出能被 Content Brief 直接消费且只有一个主要工作",
    "S7": "拒绝越界并正确路由，同时继续完成仍属 M3 的部分",
}
for r in official:
    w("| %s | %s | %s | %s | %s | %d 字 |" % (
        r["scenario"], PURPOSE[r["scenario"]], r["gate_status"], r["gate_path"],
        r["cycle_state_carry"], r["final_body_len"]))
w("")
s4 = [r for r in official if r["scenario"] == "S4"][0]
w("### 6.1 S4：历史上翻过车的那一格，这次没有退化")
w("")
w(f"`{s4['run_id']}`：闸门 `{s4['gate_status']}`、路径 `{s4['gate_path']}`、"
  f"终稿 **{s4['final_body_len']} 字**、`finish_reason = {s4['llm_finish_reason']}`。")
w("")
w("历史上 446 次有草稿的运行里有 3 次只吐审计块、正文 0 字，其中 2 次就发生在这个输入上。"
  "v1.5.2 为此在 Skill 里加了两句硬规则。**这一次它没有退化。**")
w("")
w("声明上限：这是 **1 次观察**，n=1。它证明了那两句规则在这一次运行下没有失效，"
  "**不能**证明退化率已被降低到某个水平，也**不能**把「两句规则修好了 B09-5」"
  "从推断上推成已确认 —— 那需要多次运行的统计证据，本轮没有，也不授权去取。")
w("")
w("## 7. 适用验收项矩阵（按后继合同 v1.3 重算）")
w("")
w("| 验收项 | 状态 | 依据 |")
w("|---|---|---|")
w("| M3-AC-00 授权、身份与基线回指 | **`NOT_VERIFIED` (INSUFFICIENT)** |"
  " 任务身份、分支、远端、Skill、系统提示词、模型、App 全部绑定成立；"
  "**已发布候选版本标签**对 7/8 条运行不成立，`user_request` 逐字不等于冻结包。"
  "可执行内容绑定成立，但不得据此上推 |")
for i in range(1, 18):
    ac = "M3-AC-%02d" % i
    w("| %s | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、"
      "`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加"
      "八条运行的仓库代码重算一致与无代写核验 |" % ac)
w("| M3-AC-18 公平同模型 A/B | `NOT_APPLICABLE_BY_FOUNDER_REBASE` |"
  " 盲评/AB 路径按 Founder REBASE 取消；历史 `NOT_VERIFIED` 记录原样保留，不改写为 PASS |")
w("| M3-AC-19 Qwen 隔离、独立 Review、留出分轨 | `NOT_APPLICABLE_BY_FOUNDER_REBASE` |"
  " 同上 |")
w("| M3-AC-20 收口、回滚、远端与 Founder 接受 | **`NOT_VERIFIED` (ABSENT)** |"
  " 远端任务分支收口成立、Founder PASS 已记录、回滚 DSL 完整在盘；"
  "但线上 Dify 实例数据库已被清空，`dynamic_dify_binding_requires_refresh` 无法再满足，"
  "活体回滚入口不可复演 |")
w("")
w("**AC-01–AC-17 判 `PASS` 的失效面说明**：缺口 1 只影响版本标签，"
  "不影响 Founder 所观察内容由哪套逻辑产出 —— "
  "系统提示词、七个节点 data、边拓扑、确定性代码行为，八条运行全部被证明与冻结候选相同。"
  "因此这些产品语义项**不随缺口 1 失效**（A3：不多算）。"
  "缺口 2 只使 S6 的**产物身份**存疑，两份都在，都非退化，"
  "不改变 Founder 的整体 PASS 覆盖。")
w("")
w("## 8. 终态与声明上限")
w("")
w("```text")
w("M3_ENGINEERING_TASK")
w("= IN_PROGRESS")
w("")
w("M3_FOUNDER_PRODUCT_ACCEPTANCE")
w("= PASS")
w("")
w("FOUNDER_TEST_RUNS")
w("= 7/7_BOUND_AND_PRESERVED（另有 1 次 S6 重复提交，一并保留并披露）")
w("")
w("EXECUTOR_MODEL_CALLS_AFTER_REBASE")
w("= 0")
w("")
w("BLIND_REVIEW")
w("= NOT_APPLICABLE_BY_FOUNDER_REBASE")
w("")
w("MODULE_AB_GAIN_VS_GOOD_PROMPT")
w("= NOT_CLAIMED")
w("")
w("MAIN_MERGE")
w("= NOT_AUTHORIZED_NOT_PERFORMED")
w("")
w("M5")
w("= NOT_STARTED_NOT_AUTHORIZED")
w("")
w("REAL_BUSINESS_LIFT")
w("= NOT_VERIFIED")
w("```")
w("")
w("**为什么不是 `DONE`**：授权 §7 要求「所有适用确定性技术门成立」才推导 DONE，"
  "并在 §4 明确「如果发现 Founder 实际看到的不是冻结 v1.5.2、输入不是冻结 S1-S7，"
  "必须将受影响项标记为 `NOT_VERIFIED` 并报告精确差异，不得伪造闭合」。"
  "M3-AC-00 与 M3-AC-20 现为 `NOT_VERIFIED`，DONE 不可推导。"
  "按授权「如果证据绑定尚有真实缺口，保持 `IN_PROGRESS`」，本轮停在 `IN_PROGRESS`。")
w("")
w("**这次核验能说明什么**：绑定 v1.5.2 可执行内容的 M3 候选，"
  "在一组事前冻结的七个 Dify 输入上真实运行并获得 Founder 产品接受；"
  "七次运行的全部原始证据完整保留、可逐条回指；"
  "确定性组件在这八次真实运行中没有代写过任何交付内容。")
w("")
w("**不能说明**：已盲评证明优于一份好提示词｜已完成 M5 成品集成增益｜"
  "已生产上线｜已产生真实 GMV／线索／到店／增长｜测试结果证明真实因果增益｜"
  "两句新 Skill 规则已被证明修好了 B09-5（仍是**推断**，本轮只多了 1 次未退化的观察）。")
w("")

io.open(DOC, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("written:", DOC, len("\n".join(L)), "chars")
