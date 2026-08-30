# UAPP S5 场景—能力合同审计 v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`model_calls: 0`
`authority: PRD v1.1 §9.3 + UAPP Task Contract UAPP-AC-01..11`

## 结论

v1.0 的 CAP-01～06 都不是“前置条件完整的能力正例”。CAP-01～04 真实调用了目标应用，但仅返回缺口且没有 artifact；CAP-05～06 缺合法上游。因此六项旧 PASS/FAIL 都保留为历史证据，但对 AC-04/05 置 STALE，不得结转。其余 13 个业务输入和 1 个恢复输入与其冻结目的一致。

| 场景 | 会话 | 目标/前置 | 预期 | Seam/目标 app | v1.0 充分性 | 后继处置 |
|---|---|---|---|---|---|---|
| CAP-01 | 独立 | Matrix；长期定位/分工的适用理由与表达边界 | EXECUTE | 1/1 | 不足 | 补齐四账号事实、长期目标与边界；复验 |
| CAP-02 | 独立 | Campaign；时间边界、受众问题、产能/责任人 | EXECUTE | 1/1 | 不足 | 补齐后复验 |
| CAP-03 | 独立 | Brief；受众问题、期望改变、内容承诺、表达主体/边界 | EXECUTE | 1/1 | 不足 | 使用完整自然语言 Brief 前提；复验 |
| CAP-04 | 独立 | Script；期望改变、承诺、表达主体、内容来源 | EXECUTE | 1/1 | 不足 | 补齐后复验 |
| CAP-05 | 独立 | PD；合法脚本/等价节拍 + 制作条件 | EXECUTE | 1/1 | 不足 | 在原话中附已确认脚本和制作条件；复验 |
| CAP-06 | 独立 | PP；已兑现内容/成片/素材说明 + 平台/包装请求 | EXECUTE | 1/1 | 不足 | 在原话中附已实现素材与平台；复验 |
| GAP G1/G2 | 连续 | G1 故意缺商品/方向；G2 只补该缺口 | ASK_ONE → EXECUTE | 0/0 → 1/1 | 充分 | 保持 |
| EQUIV a/b/c/n | 各独立 | 三种等价充分表达 + 缺 expected change 负例 | EXECUTE / LOCAL_RETURN | 1/1 / 0/0 | 充分 | 保持 |
| WITHDRAW W0/W1 | 连续 | W0 真实上传测试素材；W1 撤回同份素材 | EXECUTE / LOCAL_RETURN | 按节点 | 充分 | 保持 |
| FULL T1～T4 | 连续 | 完整 Brief → 测试发布 → 反馈 → 新周期 | EXECUTE | 按轮 | 充分 | 保持 |
| RECOVERY R1 | 延续 FULL | 重复同一反馈，验证幂等 | LOCAL_RETURN | 按轮 | 充分 | 保持 |

Checker v1.0 的 CAP 判据只检查“目标 app 运行”，未检查正例是否形成非空 artifact。v1.1 必须增加真实 artifact/content version 硬门，并为该谓词增加单变量负控制。

## CAP-05 历史归因后继裁决

`UAPP_S5_SUCCESSOR_FAILURE_TRIAGE_001_CAP05_SHORT_ENTRY_BLOCKED.md` 在 v1.0 Oracle 下的观察与 RAW 继续有效，但“confirmed_origin=SYSTEM_UNDER_TEST”不能上推到当前产品缺陷：PRD 要求独立 PD 正例已有合法脚本，v1.0 输入不满足该前提。当前归因投影为 `ORACLE_OR_CRITERION`，`CAP05_SUT_FAILURE=NOT_PROVEN`。
