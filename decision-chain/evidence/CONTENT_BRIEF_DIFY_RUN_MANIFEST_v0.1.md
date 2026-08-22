# CONTENT_BRIEF_DIFY_RUN_MANIFEST_v0.1

本文件是 Content Brief Architect v0.1 在本机自托管 Dify 上全部运行的索引。
只登记后台原值，不含模型排名、业务评分或推荐意见。
本轮登记全部运行，无基础设施失败、无重放、无 Run 002。

| 归档文件 | 精确模型 | Run ID | started_at | 运行状态 | finish_reason | final_present | 原始输出 SHA-256 | 输入 SHA-256 | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| `CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_RAW.md` | `deepseek-v4-flash` | `25c4fb99-f933-4bfa-a7e3-18b59ff26caf` | `2026-08-21 05:10:46.82004` | `succeeded` | `stop` | `true` | `c1a502813e7202330fc28db6fbd5a0450ab5ba01d69e4f0085ca169fc3569a95` | `8aec6d8d280fa2634800676438850c16170644b6debdabf927495c577633ae9c` | 正向 Run 001 |
| `CONTENT_BRIEF_NEGATIVE_PROBES_RUN_001_RAW.md` | `deepseek-v4-flash` | `0bef8853-a153-4b40-9edc-79b44cd91048` | `2026-08-21 05:13:53.319882` | `succeeded` | `stop` | `true` | `17a9b89e8a5169696def7bf7683462a64bb4121078e7881e0f6f50104fc8b148` | `8495ba190fe1418d25aa1393729d003d5951d6b653fa92c26501d9259aba8221` | Negative Probe A｜缺少上游决策 |
| `CONTENT_BRIEF_NEGATIVE_PROBES_RUN_001_RAW.md` | `deepseek-v4-flash` | `96c3ff77-2aea-4afd-a1b9-ec9f38ac8be2` | `2026-08-21 05:14:02.042568` | `succeeded` | `stop` | `true` | `7f1ac40b4d0707c8d2f156bd6b5e0eca8f23f130768d240ead84079d1e7cf7a8` | `07c3492fe49f3e8f9d4dc23d7f3ecab0da75e6b54c6aacf069c9fb9a6a263a6a` | Negative Probe B｜同优先级正式决定冲突 |

## 运行环境与冻结件

| 项 | 值 |
|---|---|
| app_id | `e84f4f7a-2db7-4a25-a880-81a29ef24a92` |
| app_name | `DIYU Demo Content Brief DeepSeek V4 Flash v0.1` |
| workflow_id | `2f7a3f08-2864-4280-a755-f5c0a599c0aa` |
| provider / model / mode | `langgenius/deepseek/deepseek` / `deepseek-v4-flash` / `chat` |
| 插件依赖 | `langgenius/deepseek:0.0.20@850efe73fb62bbe7ab2229116086596596297a77174fb86f73e1363b99a24116` |
| completion_params（后台原值，三次运行一致） | `{"max_tokens": 384000, "top_p": 0.8}` |
| DSL SHA-256 | `c165e1dc395293087ca9985a542bed1ca8cca377ac03ff9a0f42d208dd05bae7` |
| Skill SHA-256 | `a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f` |
| 正向输入 SHA-256 | `8aec6d8d280fa2634800676438850c16170644b6debdabf927495c577633ae9c` |
| 负向探针文件 SHA-256 | `6a59345f33a434caf0ef67b0da0f88183ab800bdd76ea0f775d79f85e3b6ea0c` |
| Contract SHA-256 | `89d2a7836703189bf17dadd442d0c24987e35ec37f06321a8c6f91d78e5cb3a6` |
| Golden SHA-256 | `3b6cbcd7c79d49815ec1de8db472950ab84ac04a754b3342355285d706fe04bd` |

`started_at` 为数据库存储值，Dify 面板按账号时区 `Asia/Shanghai` 显示，比此处晚 8 小时。
`原始输出 SHA-256` 为后台 LLM 节点 `outputs.text` 原值的哈希。
`输入 SHA-256` 为后台 `workflow_runs.inputs.content_brief_input` 原值的哈希。

正向运行另有一份仅含业务输出、不含推理块的提取件：`CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md`。
两个负向探针的完整原始记录见 `CONTENT_BRIEF_NEGATIVE_PROBES_RUN_001_RAW.md`。
