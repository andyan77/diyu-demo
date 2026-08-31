# UAPP S5 双阻断 · 全新环境恢复收口 v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

## 结论

Founder 已授权“全新环境重建并建立新基线，继续”。因此环境失效不再等待旧 volume 恢复，
而是建立新的 Dify/M2 身份。旧环境的失败和 14/19 结果全部保留，但不冒充当前证据。

## FAILURE TRIAGE 后继

- `observed_failure`：Dify 初始化时 API 容器无法写入 storage 私钥目录；首次 setup 返回
  `PermissionDenied`。
- `confirmed_origin`：`INPUT_ENVIRONMENT_OR_TOOL`。绑定目录属于 root，而 API 进程 uid 为 1001。
- `evidence`：失败时 tenant/app/workflow/model run 均为 0；修正 storage 所有者后，使用相同官方
  setup 路径成功完成。
- `mutation_target`：仅 `/app/api/storage` 的运行权限；没有改 UAPP、专业能力、Gate 或输入。
- `next_reverification`：Dify setup、登录、插件、provider、app/provider 图回读均已通过。

## 新基线

- M2 从迁移头 `17368b750d3b` 建立，schema md5 仍为
  `25192c11562827efedfc3b2c22c3b4fd`；新环境非测试保护计数为 `0/0`。
- 历史 `1568/117` 没有恢复，明确标为 `HISTORICAL_NOT_RECOVERED`，没有写占位数据。
- PP 由 M4 DSL、已接受 b2 正文和 CAP06 充分性外壳重建；provider 钉到同一新发布版本。
- Hop 由保留的发布图和已接受 facts floor 修复重建；Seam 只替换为新 provider 身份。
- UAPP 先逐层重放旧修复链，再加入本轮格式归一与测试写回接缝。正式模型调用仍为 0。

## 影响面

新应用、provider、workflow 和 M2 数据身份均不同，旧 14 项证据不能保持 `CURRENT`。历史 RAW、
PASS 和 FAIL 不删除、不改写；它们的时效统一降为 `STALE_NEW_ENVIRONMENT_IDENTITY`。

本轮候选只在 UAPP 内新增：结构化表达原值归一，以及测试发布、反馈、周期和恢复幂等写回。
M1、M2 服务与 schema、M3、Hop、Seam、六项专业能力和 PP 专业规则均未修改。
