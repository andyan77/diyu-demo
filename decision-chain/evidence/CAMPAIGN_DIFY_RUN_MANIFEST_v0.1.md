# CAMPAIGN_DIFY_RUN_MANIFEST_v0.1

本文件是 Campaign Orchestrator v0.1 在本机自托管 Dify 上全部运行的索引。
只登记后台原值，不含模型排名、业务评分或推荐意见。

| 文件名 | 精确模型 | Run ID | started_at | 运行状态 | 是否有 Final | 是否含 think | 输出 SHA-256 | 输入 SHA-256 | DSL SHA-256 | Skill SHA-256 |
|---|---|---|---|---|---|---|---|---|---|---|
| `CAMPAIGN_QWEN_RUN_001_RAW.md` | `qwen-max` | `aa6184a7-a292-4c5f-8efa-056ce80a9379` | `2026-08-20T17:27:02.079857` | `succeeded` | 是 | 否 | `8650f87b38b902d46eca569bde348f9aeaf28037c08d7335b38ddd9f5fc4c96e` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_DEEPSEEK_V4_PRO_RUN_001_RAW.md` | `deepseek-v4-pro` | `98998f2c-46e2-4725-80f7-7b15e86577cf` | `2026-08-20T18:23:37.362918` | `succeeded` | 否 | 是 | `0fa9710f6a8f25b5167f5de55bb21abccb7c82fe9a8c31a8658a6c27c094d8ae` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_DEEPSEEK_V4_FLASH_RUN_001_RAW.md` | `deepseek-v4-flash` | `c676edf2-20ce-4110-9c7c-01598d83069d` | `2026-08-20T18:27:58.019814` | `succeeded` | 否 | 是 | `4fd369b48f3138e3be84546883be96a66954a1fcccc9a6d34b02d671f6276c99` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_QWEN38MAX_RUN_001_RAW.md` | `qwen3.8-max` | `54bdaeb1-fff0-4b0d-a91d-4e55b51f7954` | `2026-08-20T18:31:34.794795` | `succeeded` | 是 | 是 | `f5da10e871926de04a872328126ad9eaa880ba22ed9cf9560936bf7996462ba5` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_QWEN37PLUS_RUN_001_RAW.md` | `qwen3.7-plus` | `f76d24a0-58db-4823-9c55-151452e53701` | `2026-08-20T18:54:31.492826` | `succeeded` | 是 | 否 | `e21980cfbfccee332c69b7c510d1c42c6f1bf4ccc51955b56beb93ce464cfe7d` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_DEEPSEEK_V4_FLASH_RUN_002_RAW.md` | `deepseek-v4-flash` | `4d7d68d9-53be-4952-8359-87104ab9df45` | `2026-08-20T19:20:47.264649` | `succeeded` | 是 | 是 | `1fce9b5c113f4e8a57a8506a5a59424e7b49097feb7a673bbb49d42a64f985b0` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_DEEPSEEK_V4_PRO_RUN_002_RAW.md` | `deepseek-v4-pro` | `982ef857-9a74-4fbb-b668-b4f5617d2ec1` | `2026-08-20T19:24:16.171096` | `succeeded` | 是 | 是 | `fd96498b4540ed96760759a029032adb89a4dd0211f753262c78f2d46392a177` | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_RAW.md` | `deepseek-v4-flash` | `c484b072-da64-49cf-9808-18627732bf93` | `2026-08-21T01:50:22.984060` | `succeeded` | 是 | 是 | `84679bbebd22abfff12a67ff2bb51ee040ff5bb87f9a12a40bcb47a9201c7184` | `2f431c900a52b4715cfdeefdff4e149dad6d0e70c85a85a1d7bef21e05c41ab8` | `f590c29b27255353bf0c6f7e4bf1c4be8705d5537602c02cfa18899e9e99e36f` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |

`started_at` 为数据库存储值，Dify 面板按账号时区 `Asia/Shanghai` 显示，比此处晚 8 小时。
`输出 SHA-256` 为后台 `outputs.text` 原值的哈希。

Compile Mode 运行另有一份仅含业务输出、不含 think 的提取件：`CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_FINAL.md`。
`输出 SHA-256` 为后台 LLM 节点 `outputs.text` 原值的哈希；Compile Mode 运行的输入为 `CAMPAIGN_COMPILE_RUN_001_INPUT.md`，与其余运行的输入文件不同。
