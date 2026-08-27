# M3 最终候选 v1.5.2 · 证据索引与回滚入口 v1.0

- `task_id`：`DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`｜进入模式 `REBASE_TASK`
- 合同：`M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml`（`49021e60…`，已现场核验）
- Execution Prompt：`M3_ENGINEERING_EXECUTION_PROMPT_v1.2_FOUNDER_SINGLE_SET_REBASE.md`（`4b456c70…`，已现场核验）
- **执行侧模型调用：0 次**

---

## 1 候选绑定（全部读自实物，不是部署前声明）

| 项 | 值 |
|---|---|
| 候选 | `v1.5.2` |
| Dify App | `b7fb5b1a-9278-426c-bb8a-f9f288639548`（任务专用候选／测试 App） |
| 已发布版本名 | `m3-cand-v1.5.2` |
| 发布时间 | `2026-08-27 19:46:47.281053` |
| 已发布图哈希 | `91980f1aae8c988f8c61e72e6444ce30fd7bd03fbd50ed09b3df5662f6eccfac` |
| 图形状 | 7 节点 6 边（与 v1.5.1 相同） |
| 已发布系统提示词哈希 | `3a3c657d82d45e96dfbf9abdcb88adf66c58bb74f69f1e1e0412591242898028` |
| `SKILL.md` 哈希 | `90596da5170730b90bfa87089d456e7a2f4d670c46f98ea6ae60138e1f4d3c41`（v1.5.1 时 `245ee2ab…`） |
| 模型 / 温度 | `deepseek-v4-flash` / `0.4` |
| 冻结提交 | `3cc25c7c95b3cddae57847582bf56d26a4530e3d`（见 `founder-pack-v152/FREEZE_COMMIT.json`） |

**三处逐字节相等已核**：线上已发布系统提示词 == `SKILL.md` 全文 + 参考占位符；
`SKILL.md` 工作区哈希 == `git HEAD` 哈希；草稿图 == 已发布图。

---

## 2 证据索引

| 路径 | 内容 |
|---|---|
| `account-operations/evidence/ep34-candidate-v152-closure/` | 零模型技术闭合六项（Z1 Skill 静态一致性、Z2/Z5/Z6 全量重放、Z3 审计块不得单独构成交付、Z4 E07/E08 穷举不变性、Z7 四层分离、Z8 凭据扫描） |
| `account-operations/evidence/ep35-candidate-v152-freeze/` | 部署后读回的候选冻结绑定 + 草稿图全文 |
| `account-operations/evidence/ep36-structural-and-ac16-v152/` | 图结构检查、已发布系统提示词全文、浏览器渲染画布与 LLM 面板截图 |
| `account-operations/evidence/ep37-rollback-drill-v152/` | 导出与恢复演练 + DSL 全量导出件 + 草稿快照 |
| `account-operations/evidence/ep38-founder-pack-verify-v152/` | 实测包独立复算七项（含对线上实物的绑定核验与 A5 两两消融） |
| `account-operations/founder-pack-v152/` | **Founder 七场景实测包**（先看 `README_FOUNDER_FIRST.md`） |
| `account-operations/evidence/ep33-rebind007-v151/` | v1.5.1 的 DD-5 重放、预检、调用账与 DD-1 真运行结论（历史，未覆盖） |
| `account-operations/evidence/ep06*-v15/`、`ep07-longitudinal-v15/`、`ep32-formal-v15/` | v1.5 那 70 次真实运行的原始记录（历史，未覆盖，只作诊断输入） |

**历史证据一份没删、没覆盖、没改写**；`ep28`（第 9 轮）在本轮两次复算后与 `git HEAD` 逐字节相同。

---

## 3 回滚入口

按影响面从小到大，三级：

**① 只回滚 Dify 草稿**
`account-operations/evidence/ep37-rollback-drill-v152/draft_snapshot_v152.json` 里的 `graph`
直接 `POST /console/api/apps/b7fb5b1a…/workflows/draft`。演练已证明可逐字节还原。

**② 回滚整个候选 App**
`account-operations/evidence/ep37-rollback-drill-v152/m3_candidate_app_v152.dsl.yaml`
（198,091 字符，`sha256 bd676f29…`）走 `POST /console/api/apps/imports` 重建。

**③ 回滚到上一个候选**
Dify 版本记录里 `m3-cand-v1.5`（`2026-08-27 16:56:46.979840`）仍在，可直接切回；
仓库侧 `git checkout 5e1b6ee -- account-operations/skills/operating-one-account/SKILL.md`
即回到 v1.5.1 的 `SKILL.md`（`245ee2ab…`），再重新部署。

三级都只作用于**任务专用候选 App**，不触及生产、其他 App、凭据或数据库。

---

## 4 声明上限

即使 Founder 最终判 `PASS`，只能声明：

> 绑定 v1.5.2 的 M3 候选通过了适用确定性技术门，并在一组事前冻结的七个 Dify 输入上获得 Founder 产品接受。

**不得声明**：已盲评证明优于一份好提示词｜已完成 M5 成品集成增益｜已生产上线｜
已产生真实 GMV／线索／到店／增长或经营提升｜测试结果证明真实因果增益。

v1.5.2 那两句审计块输出形状硬规则对 `B09-5` 零正文的效果，
当前等级是**推断**，不是已观察、不是已修复、不是 PASS。
零模型验证证得到确定性组件的行为，证不到模型有没有照做。

---

`END_MARKER: M3-V152-EVIDENCE-INDEX-AND-ROLLBACK-v1.0-END`
