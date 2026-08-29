# FAILURE TRIAGE 002 · UAPP-FULL-01 首次正式运行

证据：`unified-app/evidence/formal_v1.0_stale/UAPP-FULL-01.json`（Attempt 1，原样保留）

```yaml
observed_failure:
  - "T2「这条我已经发出去了」整轮 HTTP 400：Run failed: Variable ['uapp_seam','artifact'] not found"
  - "T4「开下一个周期」同一报错"
  - "T3 uapp_action 结构化输出解析失败，动作退回 NONE，用户陈述的反馈被漏记"
frozen_target: "UAPP-FULL-01 的四步 M2 写入必须在库里查得到对应行（判据 c45c4668… 第 T2/T3/T4 条）"
candidate_sources:
  - SYSTEM_UNDER_TEST
  - INPUT_ENVIRONMENT_OR_TOOL
  - CHECKER_OR_FIXTURE
confirmed_origin: "SYSTEM_UNDER_TEST（两处，都是新画布自己的接线；M1-M5 既有资产与 M2 服务均无关）"
```

## 缺陷 A｜非能力轮引用了没执行的节点

`route_mode = WRITEBACK` 时不进专业能力，`uapp_seam` / `uapp_hop` **根本不执行**。
但 `uapp_save`（assigner）仍然直接引用 `uapp_seam.artifact`，于是整轮失败。

**为什么六个 CAP 例没打到它**：那六例全部走能力分支，接缝一定执行。
这条路径此前一次也没被跑过——**通过的用例覆盖不到的地方，不等于那里没问题**。

**为什么代码节点没炸而 assigner 炸了**：`uapp_side` 同样引用了本轮没跑的 `wb_p3..wb_p6`，
它成功了并拿到空值（CAP 例的实测记录可查）。代码节点容忍上游变量缺失，assigner 不容忍。

**修法**：新增 `uapp_noseam` 空占位节点与 `uapp_seam_merge` 变量汇合节点
（Dify 原生 `variable-aggregator`，就是干这件事的）。哪一支跑了取哪一支，两支都没跑取空。
`uapp_wb_prep` / `uapp_delivery` / `uapp_save` 一律改读汇合节点。
`uapp_m3` 在 `STATUS` 分支同样不执行，一并纳入汇合——**同一类错不要只修被打到的那一个**。

## 缺陷 B｜动作分类的载体被 `<think>` 污染

DeepSeek 在结构化输出前输出了一段 `<think>` 推理，Dify 的结构化输出解析因此失败。
`error_strategy: default-value` 生效，没有让整轮崩掉——**这一层设计是对的**。
但后果是 `action` 退回 `NONE`，用户说的「这条我已经发出去了」被安静地漏记，走了闲聊分支。

**判断本身没错，错的是载体。** 模型的推理正文里明确写着它判成了已发布。
所以修法是**把那一个 JSON 从原文里捞回来**（`_salvage_action`：跳过 `</think>`、
括号配对扫描、要求含 `action` 键），不是再做一次判断，更不是放宽判据。
捞不回来仍然按 `NONE` 处理，保持「宁可漏记，不可记下没发生的事」。

三向自测：`<think>` 包裹 → 捞回 `RECORD_PUBLISH`；结构化正常 → 直取；
纯垃圾文本 → 退回 `NONE` 且 `action_source=none`。

```yaml
mutation_target:
  - "新画布的分支汇合接线（新增 uapp_noseam / uapp_seam_merge，下游改读汇合节点）"
  - "新画布 uapp_route 的动作补捞逻辑与新增 action_text 输入"
protected_targets:
  - "M1 子图与 m1_context_compiler_v0.1.py（未证明有错，一个字节没动）"
  - "最终 FP M3 / hop / Seam 与六个能力应用"
  - "M2 服务（本轮行为正确）"
  - "冻结判据 UAPP_FROZEN_SCENARIOS_v1.0.json（变的是被测系统，不是判据）"
  - "旧 Canvas、旧 provider、main、非测试数据"
next_reverification:
  - "在新图（61 节点，sha256 e8819f5b…）上重跑 UAPP-CAP-01..06 与 UAPP-FULL-01"
  - "FULL-01 的 T2/T4 必须真正执行到写回节点并在 M2 查到对应行"
  - "T3 的 action_source 必须显示 structured_output 或 salvaged_from_text，不得为 none"
  - "确定性预检 19/19 保持 PASS"
```

**旧 Attempt 全部原样保留**在 `evidence/formal_v1.0_stale/`，不删除、不覆盖、不改写。
影响面与 STALE 判定见 `UAPP_STALENESS_RECORD_001.md`。
