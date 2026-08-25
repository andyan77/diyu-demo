# M2 Founder 实测包

`task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`

## 候选应用/工作流身份

- 应用名称：`M2 候选 - 业务持久化六步验收 (DO NOT USE FOR PRODUCTION)`
- Dify app_id：`8f34e8a3-fb49-4d3e-a222-3d666e767adf`
- 类型：`workflow`（不是 chat，不含任何 LLM 节点）
- 所在 workspace：你现有 Founder 账号的 `diyu 's Workspace`（未新建租户，未触碰其他任何应用）
- 入口：Dify Studio 里搜索上面的应用名称直接打开

## 测试身份说明

- 测试用户/workspace/account 由一次性引导脚本创建，**不是**你的真实经营账号：
  - workspace_id: `64f56e9b-c530-49cf-b670-1b1746de265a`
  - account_id: `49f6d2b8-488e-4543-8a4d-fad8bd2157b8`
- 这两个 ID 要粘贴进工作流「运行」时的 Start 表单前两个字段。

## 六步场景怎么跑

打开应用 -> 点「运行」-> 在表单里填：

| 字段 | 填什么 |
|---|---|
| Workspace ID | `64f56e9b-c530-49cf-b670-1b1746de265a` |
| Account ID | `49f6d2b8-488e-4543-8a4d-fad8bd2157b8` |
| 本次运行标识 | 任意字符串，比如 `founder-test-01`；**每次重新完整跑一遍请换一个新值**（它是幂等键前缀，同一个值第二次运行会直接返回上次的结果而不是真的重新创建） |
| 首次任务原始诉求 | 随便写一句真实一点的话，比如"帮我看看这周三条内容能不能按时发" |
| 候选内容引用 | 随便写一个占位引用，比如 `s3://demo/content-001.mp4` |
| 发布平台标识 | 比如 `douyin` |
| 发布时间 | ISO8601 格式，比如 `2026-08-26T10:00:00Z` |
| 反馈原始观测 | 随便写一句，比如"完播率比上周高，评论区在问价格" |

点运行，等它跑完（一条链路，没有分支，几秒钟内会结束）。

## 该看什么、怎么判断"接得住"

结果面板的 End 节点会给出这些输出：

1. `task_id` —— 应该是一个真实 UUID，不是空的
2. `snapshot_status` —— 应该是 `200`
3. `cycle_created_body` —— 应该能看到 `is_current: true`
4. `projection_body` —— **这是"再次进入"的核心验证**：里面应该能看到刚才存的
   `latest_snapshot.payload.note` 就是你填的"首次任务原始诉求"原文，说明状态真的被存住、
   读回来了，不是每次都是空白
5. `version_id` —— 真实 UUID
6. `promote_body` —— `is_current: true`，`promoted_by` 是 `dify-m2-candidate-reviewer`
7. `publish_instance_id` —— 真实 UUID
8. `feedback_body` —— 里面 `is_test: true`、`is_manual_entry: true`，`payload.note`
   就是你填的反馈原文
9. `current_cycle_body` —— **这是"下一周期读取"的核心验证**：应该能看到第 4 步建的
   那个周期，`label` 里带着你填的"本次运行标识"

**判断标准只有一条**：第 4 项（`projection_body`）里能看到你自己刚才写的话被原样存住、
读回来了；第 9 项（`current_cycle_body`）能读到之前建立的周期状态。如果这两处能看到你自己
输入的内容被系统"记住"了，就说明持久化这条链路是接得住的。

## 明确不要求你判断什么

- 不需要看 JSON 里的字段名是否好看、Schema 设计是否优雅
- 不需要判断迁移脚本、数据库权限、Git 提交是否规范——这些已经过独立审查
- 不需要判断这条工作流本身的"产品体验"——它是纯技术验证管线，不代表未来 M1 接入后
  用户实际会看到的自然语言交互界面

## 已知限制（不是 bug，是本轮范围之外）

- 没有自然语言理解——所有字段都要手填，M1 接入后这一层会被自然语言对话取代
- 没有真实社交平台发布——`publish-instances` 只是"登记"一条记录，不会真的发到抖音/小红书
- 没有旧 Demo 会话态（3 槽/5 槣）兼容读取——这部分还没做，不在本次验收范围
- 没有市场观察、打法版本化的端到端演示——底层能力已实现（见独立审查报告），但本次六步
  场景没有覆盖，需要的话可以另起一次工作流运行验证

## 如果哪一步失败了怎么办

把 End 节点里对应字段显示的 HTTP 状态码/错误信息截图给我，不用猜是什么原因——这是我需要
定向修复的证据，不需要你判断根因。
