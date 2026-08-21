# 笛语 V1 Demo Dify 运行清单 v0.1

> 本清单的每一行都取自自托管 Dify 的数据库与仓库文件本身，不是人工誊写。

## 1. 运行环境

| 维度 | 值 |
|---|---|
| Dify 版本 | 1.16.1（自托管 Docker Compose） |
| API 镜像 | `langgenius/dify-api:1.16.1` |
| Web 镜像 | `langgenius/dify-web:1.16.1` |
| 插件守护镜像 | `langgenius/dify-plugin-daemon:0.6.3-local` |
| DSL 版本 | `0.7.0`（`constants/dsl_version.py :: CURRENT_APP_DSL_VERSION`） |
| 模型插件 | `langgenius/deepseek` 0.0.20 |
| provider | `langgenius/deepseek/deepseek` |
| model / mode | `deepseek-v4-flash` / `chat` |
| 上下文窗口 | 1000000 |
| 模型能力声明 | `agent-thought`、`tool-call`、`multi-tool-call`、`stream-tool-call`；**未声明原生 structured output**，因此走 Dify 的 prompt-based 结构化输出回退（`core/llm_generator/output_parser/structured_output.py`） |
| 代码沙箱 | `worker_timeout=5s`；`CODE_MAX_STRING_LENGTH=400000`；`CODE_MAX_DEPTH=5` |
| 变量上限 | `MAX_VARIABLE_SIZE=200KB`；`TEMPLATE_TRANSFORM_MAX_LENGTH=400000` |

## 2. 模型参数（实际写入 DSL 的 completion_params）

| 节点 | max_tokens | top_p | temperature | reasoning_format | 结构化输出 |
|---|---|---|---|---|---|
| 三份 Skill 的 LLM 节点 | 384000 | 0.8 | **未设置** | separated | 否 |
| 影子状态节点 | 16000 | 0.8 | **未设置** | separated | 是 |
| 自然对话节点 | 12000 | 0.8 | **未设置** | separated | 否 |
| 轻量 Judge ×3 | 32000 | 0.8 | **未设置** | separated | 是 |

三份 Skill 的参数与已验证运行逐字一致。`temperature` 虽然被插件提供（默认 1），但历次已验证运行都没有设置它，因此本轮同样不设置。
影子、对话与 Judge 沿用同一插件、provider、model 与 mode，只调小 `max_tokens`——这是《任务书》第十二节要求的「小输出限制」。
**注意**：DeepSeek V4 Flash 默认开启思考模式，推理块也计入 completion tokens。首版把 Judge 的 `max_tokens` 设为 1200，推理直接把预算吃光、正文为空，导致 `JUDGE_VERDICT_MISSING`；本版已放大到 32000。

## 3. 应用与 Workflow Tool 标识

| 角色 | app_id | 已发布 workflow_id | tool_provider_id | tool name |
|---|---|---|---|---|
| Matrix Architect 适配 Workflow | `f8d2be15-2f71-4765-a482-fb62c0e1f3a0` | `612c8080-a952-4925-b17b-73205f89cdd8` | `909b1b0f-f45a-414b-953a-e502b9ea6a77` | `diyu_v1_matrix_architect` |
| Campaign Orchestrator 适配 Workflow | `a0d92232-0afe-4b77-abb4-5356fd04bc7b` | `1f5505a6-c9e9-480a-9979-0435fa4af229` | `47b156cb-215f-406d-b94d-1fb5c46183ed` | `diyu_v1_campaign_orchestrator` |
| Content Brief Architect 适配 Workflow | `eadf8867-6e00-48b8-b3b9-2cb8b89d8834` | `8248fc80-08ff-4852-9812-598b263ef728` | `4b505cb9-7afe-4376-ad65-9cc720ecc312` | `diyu_v1_content_brief_architect` |
| 主 Chatflow | `310ddfcf-e0fb-4211-af98-3d101725e07a` | `eb2c1ecd-4f71-43e8-957a-a71f020736f7` | —（不作为 Tool 发布） | — |

主 Chatflow 在本轮共发布 9 个版本（每次修复后重新发布）。所有历史版本均保留，未删除、未覆盖。

## 4. 冻结夹具 bundle

### Matrix Architect（bundle SHA `7f9f0730f02149133178b14917b9e7a197ba7947539a230dc75bc66a8e289c91`，共 2450 字符）

| 顺序 | 文件 | SHA-256 | 字符数 |
|---|---|---|---|
| 1 | `一页纸夹具品牌事实 v0.1.md` | `8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a` | 2344 |

Skill 正文：`Matrix_Architect_v0.1.2.md`，SHA-256 `7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838`，4617 字符。

### Campaign Orchestrator（bundle SHA `8b4dbab71e4ee19f912c4eb48c57f149b139ffb051cf9ecc5f3c80ce1fd5b3da`，共 42000 字符）

| 顺序 | 文件 | SHA-256 | 字符数 |
|---|---|---|---|
| 1 | `一页纸夹具品牌事实 v0.1.md` | `8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a` | 2344 |
| 2 | `序里集_Campaign当前素材与资源夹具_v0.1.md` | `53ea76e93c6529d211bcc41161e9771f7cc5818fe99caf54c4af5f7539ae0074` | 5323 |
| 3 | `序里集_Campaign最小承接条件夹具_v0.1.md` | `17b41d3ae37635fcd1e97f6af1136c71afa6310a9c51e1db12948b0b2e1e2b06` | 3275 |
| 4 | `C1_FOUNDER_CONFIRMED_v0.1.md` | `5aa0785515dc2875585b973581b89d3460a89e87512527f1b2499ea94c9138ec` | 4772 |
| 5 | `C2_FOUNDER_CONFIRMED_v0.1.md` | `9182614ec73db0e3149298e53d8b420696a85e206acbd81a1017cb56c7fd1dfd` | 4625 |
| 6 | `C3_FOUNDER_CONFIRMED_v0.1.md` | `91cdc43f697f0c469cb78dfcd44a6e4cd1a3d86bfd54fd370ca050c4f776ec45` | 6287 |
| 7 | `C4_FOUNDER_CONFIRMED_v0.1.md` | `340234393802d6442cc4f46a4b7845e476b2a6957fd7aed45ac3f8285435f50e` | 4249 |
| 8 | `C5_FOUNDER_CONFIRMED_v0.1.md` | `6a44a63625c75f05ca5d399c1ed55787da20a9f919330b09b9a92c64242c8eac` | 3738 |
| 9 | `C6_FOUNDER_CONFIRMED_v0.1.md` | `9555b86df379fb0546197fddf0329448c21e9ba5b79fa9b45934eabd3f9cbf34` | 6113 |

Skill 正文：`Campaign_Orchestrator_v0.1.md`，SHA-256 `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb`，7489 字符。

### Content Brief Architect（bundle SHA `8ad330625089bd04fce7186c7d497bf656f29ad5dcecb88269c7ad68aa6f6277`，共 11340 字符）

| 顺序 | 文件 | SHA-256 | 字符数 |
|---|---|---|---|
| 1 | `一页纸夹具品牌事实 v0.1.md` | `8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a` | 2344 |
| 2 | `序里集_Campaign当前素材与资源夹具_v0.1.md` | `53ea76e93c6529d211bcc41161e9771f7cc5818fe99caf54c4af5f7539ae0074` | 5323 |
| 3 | `序里集_Campaign最小承接条件夹具_v0.1.md` | `17b41d3ae37635fcd1e97f6af1136c71afa6310a9c51e1db12948b0b2e1e2b06` | 3275 |

Skill 正文：`Content_Brief_Architect_v0.1.md`，SHA-256 `a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f`，6469 字符。

拼接方式与已验证运行一致：每份文件用 `===== BEGIN SOURCE: <文件名>｜全文｜<标签> =====` / `===== END SOURCE: … =====` 包裹，段间空行分隔。
每次运行实际使用的 bundle SHA 由 Tool 回传，并被确定性合同检查逐字比对；不符即判 `FIXTURE_BUNDLE_SHA_MISMATCH`。

## 5. 十场景运行标识

| 场景 | conversation_id | 轮数 | Skill 调用 | workflow_run_id（逐轮） |
|---|---|---|---|---|
| S01 | `3c413b39-5b2f-4bdc-8fed-696607f42079` | 3 | 0 无 | `3db7389d` `e6355fae` `2e809d24` |
| S02 | `9dc28339-b07f-4c81-9e06-259eec5173fb` | 4 | 0 无 | `7f6912a4` `1f05875a` `61b43ba4` `b100bddd` |
| S03 | `1b017375-b8aa-433d-932a-0516441859da` | 2 | 1 matrix | `363fbce0` `dca57425` |
| S04 | `382c6684-5d44-40af-b833-9f5d003a1b59` | 5 | 0 无 | `40c0ed09` `bbfeab85` `a030a194` `8390a03c` `37183ead` |
| S05 | `7dbfd631-6bc2-4127-baa4-ab2efea599df` | 4 | 0 无 | `240fba71` `9a63750f` `3ea4f162` `f43d6d22` |
| S06 | `9e9d4275-465e-4de8-b689-eec88195dfba` | 4 | 0 无 | `33131732` `1877fda6` `b9f86bc7` `b3491ea4` |
| S07 | `371c1158-9707-473c-87a4-6c756601294b` | 3 | 1 matrix | `c04891eb` `cee84a9f` `864810be` |
| S08 | `a13098a0-3f9f-4d94-89c1-2593e1b10a9f` | 4 | 3 matrix、campaign、content_brief | `a81eeb35` `b8ecd414` `00e86904` `f5429ebf` |
| S09 | `adf10a68-299c-4cb8-a86e-f8096e176139` | 6 | 4 matrix、campaign、content_brief、matrix | `b4db857b` `d2ccb75c` `3a7183c0` `c01f3513` `e9270207` `fa8b57db` |
| S10 | `4d009a36-d4e5-42a3-8b3a-1ce61eb6f349` | 5 | 0 无 | `acba1833` `6a67c707` `8a692d9a` `49ef65a4` `0be4997d` |

完整 workflow_run_id 与逐节点执行记录见 [`V1_RUN_001_TRACE.md`](V1_RUN_001_TRACE.md) 与 [`V1_RUN_001_RAW.md`](V1_RUN_001_RAW.md)。

## 6. Golden 三 Skill 全链 Run ID（S08）

| 环节 | workflow_run_id | Artifact | content_hash | parent_hash |
|---|---|---|---|---|
| Matrix Architect | `b8ecd414-7bcc-4e39-8892-8ab69ad66680` | art_matrix_001 / USER_ACCEPTED | `sha256:86629c2c82c1490d06f99a1b259846844b97bfea51bd3d360db3fcd0cd6c0c77` | `None` |
| Campaign Orchestrator | `00e86904-8fc3-486d-b60d-38cfb32d06cf` | art_campaign_001 / USER_ACCEPTED | `sha256:bfe0e3dd8c849b32ea4ec313b240ee78b8ba728bf8bb182eec2f83e41785f153` | `sha256:86629c2c82c1490d06f99a1b259846844b97bfea51bd3d360db3fcd0cd6c0c77` |
| Content Brief Architect | `f5429ebf-adf9-4497-8f73-b82efb212b37` | art_content_brief_001 / VALIDATED | `sha256:7fbb0b578bf54f3c998cba6e3e2b612cf86009d07b0ab697bf9a07e45dbacd60` | `sha256:bfe0e3dd8c849b32ea4ec313b240ee78b8ba728bf8bb182eec2f83e41785f153` |

## 7. 运行期真实错误记录（主 Chatflow，未删除、未覆盖）

| 时间 | 节点 | 状态 | 错误 |
|---|---|---|---|
| 2026-08-21T07:43:51 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T07:47:50 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T07:48:56 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T07:49:20 | `v1_shadow` | exception | Failed to parse structured output: Failed to parse structured output: <think> <!--dify-deepseek-reasoning-->We need respond with JSON patch. Need analyze conversation. System prompt says we are shadow |
| 2026-08-21T07:54:55 | `judge_matrix` | succeeded | Failed to parse structured output: Failed to parse structured output: <think> <!--dify-deepseek-reasoning-->We need to produce JSON output for the judge. The task is to evaluate the product against th |
| 2026-08-21T08:12:39 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:17:50 | `judge_matrix` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T08:19:43 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:23:58 | `judge_matrix` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T08:24:47 | `v1_shadow` | succeeded | Failed to parse structured output: Failed to parse structured output: <think> <!--dify-deepseek-reasoning-->我们只需要按照要求输出JSON。用户说“等一下，我说错了。我真正要的是提高到店预约量，不是减少重复。”这是在纠正之前的目标，且提到“帮我把四个账号的分工理清楚，减少内容重复。”与之前一 |
| 2026-08-21T08:33:36 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:35:36 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:38:24 | `judge_matrix` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T08:48:18 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:49:43 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:50:06 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:57:35 | `judge_matrix` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T08:58:54 | `judge_campaign` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T09:01:40 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T09:03:27 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T09:09:27 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T09:09:35 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T09:09:47 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T09:10:40 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T09:16:49 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T09:17:40 | `tool_matrix` | exception | Failed to invoke tool 909b1b0f-f45a-414b-953a-e502b9ea6a77: req_id: df5e4392f8 PluginInvokeError: {"args":{"traceback":"Traceback (most recent call last):\n  File \"/app/storage/cwd/langgenius/deepsee |
| 2026-08-21T09:20:05 | `v1_shadow` | succeeded | req_id: 941b7f2074 PluginInvokeError: {"args":{"traceback":"Traceback (most recent call last):\n  File \"/app/storage/cwd/langgenius/deepseek-0.0.20@850efe73fb62bbe7ab2229116086596596297a77174fb86f73e |
| 2026-08-21T09:22:00 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:02:42 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:03:54 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:09:59 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:10:43 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T10:11:42 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:11:54 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:12:43 | `judge_matrix` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:18:41 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:27:47 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:38:58 | `v1_shadow` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |
| 2026-08-21T10:51:42 | `judge_campaign` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.de |
| 2026-08-21T11:02:49 | `v1_chat_llm` | succeeded | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHI |

### 7.1 错误分类与事后归因（2026-08-21 补记）

上表 40 条运行期错误按成因分为三类：

| 类别 | 条数 | 状态 |
|---|---|---|
| `SSLEOFError`（TLS 握手被中断） | 26 | **未定位，仍开放** |
| `NameResolutionError`（DNS 解析失败） | 9 | **已定位并修复** |
| `Failed to parse structured output` | 3 | 已在第 4—5 次构建中修复（见 EVAL 第 F 节） |

**DNS 一类的根因**：容器 DNS 链路为 `127.0.0.11`（Docker 内置解析器）→ `192.168.65.7`（Docker Desktop 虚拟机）→ Windows 网卡 `WLAN 2` 的 `1.1.1.1` / `8.8.8.8`。实测 `1.1.1.1` 30/30 全超时（完全不通），`8.8.8.8` 丢包 7%—30%、平均 183 ms。容器 `resolv.conf` 原未设 `timeout` / `attempts`，走 glibc 默认 5 秒 × 2 次，故失败节点耗时恒为约 10.0 秒。`api.deepseek.com` 经 CNAME 指向腾讯 EdgeOne，只有 A 记录无 AAAA；glibc 双栈查询时若 A 应答丢失而 AAAA 返回空，即报 `[Errno -5] No address associated with hostname`——与实际报文完全一致。

**处置**：本次运行**之后**，在 `dify/docker/docker-compose.override.yaml` 为 `plugin_daemon` / `api` / `worker` / `ssrf_proxy` 指定 `dns: [223.5.5.5, 119.29.29.29, 223.6.6.6]` 与 `dns_opt: [timeout:2, attempts:2, single-request-reopen]`，并重建这四个容器。修复后实测 60 次解析 0 失败、最慢 59 ms。**本节第 1 节所记录的运行环境是十场景实际运行时的状态，不含此项变更。**

**TLS 一类**：现仍可复现，实测握手失败率在 0%—10% 之间随时间波动。已用 240 次并发对照排除容器 MTU 因素——同一时间窗内 MTU 1420 为 120/120 全通，MTU 1400 为 117/120，中位耗时 492 ms 对 487 ms，无差异。宿主实测到 `43.242.198.77` 的路径 MTU 为 1420，与容器当前设置一致。根因未定位，按开放项处理。


## 8. 仓库新增文件 SHA-256

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `V1_DEMO_INTEGRATION_CONTRACT_v0.1.md` | 18851 | `cf670c61aef4fa57fff3fe62fc3c828d9f9f29bf3341d31224b48b06a177cce4` |
| `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` | 8091 | `6839b20546ff7d4b381a92293c992ac1b2007a8fddabec970e4ba1a0317171fa` |
| `V1_NATURAL_LANGUAGE_TEST_CATALOG_v0.1.md` | 14083 | `07f30d6ce919dfdc9d3d8debbbca4cb41d6d7ac679766f3cf623e99fca46aa73` |
| `V1_PRODUCTION_GAP_REGISTER_v0.1.md` | 10354 | `e3d971b9a5f3ef648a00fa1b4deac861d21c4f4487c7e175c29ef8bea6b7886e` |
| `V1_SCENARIO_INPUTS_v0.1.md` | 7931 | `cd7eb0ad78736e54045371b3d0cf8d4fcea9b97d0b0fc2252870de7403ccd460` |
| `DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml` | 312193 | `b667dc13cf0f8d92b1478b29b903756155afbc4d126924289376ce89f40115c2` |
| `DIYU_DEMO_V1_TOOL_MATRIX_v0.1.yml` | 32694 | `dbc6b400aa1d7d7d1f43a374ab9cc1e7cb00eb5b7834576c2e38639453e451cc` |
| `DIYU_DEMO_V1_TOOL_CAMPAIGN_v0.1.yml` | 159495 | `6468223b40c1d56f8c192e5f2548371715c1522d60ca3379eb0e7c6a443b7c89` |
| `DIYU_DEMO_V1_TOOL_CONTENT_BRIEF_v0.1.yml` | 66137 | `b703a0cb690855ae76bac9483208a70f06cf3d96b24171e8e274397b31749265` |
| `V1_RUN_001_RAW.md` | 133639 | `6ad9b71610c88e76c8e32bc0dfe8152053fed650da92da39ab1a22d1dcae1c9a` |
| `V1_RUN_001_FINAL.md` | 23124 | `8c13dff6c873d970054e9da1dd06588ec94784036f1af8a392fde6fce15ff312` |
| `V1_RUN_001_TRACE.md` | 63287 | `a7353e27444fc3d6600585a8d0a09423680351a7ce1e90049c7d9a8a2be8852f` |
| `V1_RUN_001_EVAL.md` | 21334 | `590916c3abc3abb7cb8a25a51583921e84a84c6079bbb0b58fed4238cc14f64e` |
| `V1_DIFY_RUN_MANIFEST_v0.1.md` | —— | ——（自指，见 git blob） |
| `v1_demo_verify.py` | 45254 | `02d6f5958289858bad3afa99b3c9d5ba8ac6efb76feb3bf21314dc2d798bbfa0` |

> `V1_DIFY_RUN_MANIFEST_v0.1.md` 自身的 SHA 不在表内（自指），以提交后的 git blob 为准。
