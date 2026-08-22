# 笛语 V1 E2E 与质量验证运行清单 v0.1

> 本清单的每一行都取自磁盘文件与自托管 Dify 的数据库本身，不是人工誊写。

## 1. 运行环境

| 维度 | 值 |
|---|---|
| Dify 版本 | 1.16.1（自托管 Docker Compose），DSL `0.7.0` |
| 主模型插件 | `langgenius/deepseek` 0.0.20，provider `langgenius/deepseek/deepseek` |
| 主模型 | `deepseek-v4-flash` / `chat`，`top_p=0.8`，**未设置 temperature** |
| 对照模型插件 | `langgenius/tongyi` 0.2.13，provider `langgenius/tongyi/tongyi` |
| 对照模型 | `qwen3.8-max` / `chat`，`top_p=0.8`，**未设置 temperature** |
| 与 RUN_001 的环境差异 | 已含 DNS 修复（国内解析器 + `single-request-reopen`）；TLS 握手中断一类仍开放 |

**成本口径**：Dify 插件显示的 `total_price=0` 是**插件未登记计价**，不是真实零成本，不得据此声称免费。

## 2. 预注册承诺

| 项 | 值 |
|---|---|
| 预注册 commit | `00fc94e6c39bc161d33a3df7df260abb7d37b9ec` |
| `V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md` | `7a3f2e4b7a480bfa31ad20be56b63f9973a9db2296be2a364258e7b5f15e478b` |
| `V1_E2E_CASES_v0.1.json` | `dae6399cec4afeec66a693868df80200859a88025eda8bdab3fbac50afc7e132` |
| `V1_QUALITY_COMPARISON_INPUTS_v0.1.md` | `3838606f364642dee27a44ab34ff67654c8d20d8d6736abd2113cfcf27d0d35d` |
| `v1_demo_e2e_replay.py`（预注册版） | `c41e239e06ae5d9507b195b3a94d77590a3e55c0c97a710f5ed8592b8d07fdf8` |
| **匿名映射表 SHA-256（盲审前承诺）** | `39df1008a8b88bac781e4fe3fc46487397d7c9a42673f9da1bf95bdee07f3a59` |

`v1_demo_e2e_replay.py` 在预注册之后修改过**一次**，只改凭据优先级（显式 `DIFY_API_KEY_FILE`
必须压过环境里残留的 `DIFY_API_KEY`）。原始失败证据保留为
`replay_scenarios.FAILED_401_UNAUTHORIZED.jsonl`，受影响用例 S01 **从头重跑**，未做增量补跑。

## 3. 本轮新建的测试专用应用

均为**全新 app_id**，名称含 `V1 QUALITY TEST ONLY`，未注册为主 Chatflow 的 Tool，
未修改任何旧应用、旧 Workflow 版本或原三个 Workflow Tool。

| 名称 | app_id | 已发布 workflow_id |
|---|---|---|
| `TEST_MATRIX_QWEN38MAX` | `ced1566c-d83e-49d8-a3c0-7da45fdb8a84` | `c4001ddc-e702-44f1-af71-4ef40f81a06a` |
| `TEST_CAMPAIGN_QWEN38MAX` | `aad728f0-3b69-4241-a122-7ba83c6f8d23` | `dcdd0da7-c59f-4d9d-8887-99a72df5ed86` |
| `TEST_CONTENT_BRIEF_QWEN38MAX` | `86e48b41-864c-4ff2-bcae-158f4396d3ae` | `eb13e331-5de7-4b5e-b180-ca673a58c597` |
| `TEST_MATRIX_NOSKILL` | `87eb2e0b-65cd-4aa4-9752-5ba741972bd8` | `39853546-275a-41a5-940e-e864bf003fa2` |
| `TEST_CAMPAIGN_NOSKILL` | `a42c9cf0-fbaf-47a3-9961-eb9786f5d1ee` | `21a140ba-c544-40a8-af5b-438453a99ba1` |
| `TEST_CONTENT_BRIEF_NOSKILL` | `1b7b4023-5f82-49e6-9d35-4e9ae38985b9` | `9bbd5baf-b4ef-4506-9ec2-3a9db8346fce` |

## 4. 运行规模

| 项 | 值 |
|---|---|
| 十场景重放 | 通过 7 / 失败 3 / 未运行 0 |
| 40 类 E2E | 通过 25 / 失败 9 / 未运行 6 |
| 有效影子节点轮数 | 165 |
| `shadow_patch_success_rate` | 0.9091 |
| `fail_open_rate` | 1.0 |
| `empty_turn_rate` | 0.0 |
| `unauthorized_execution_rate` | 0.0 |
| 基础设施重试次数 | 0 |

## 5. 新增文件 SHA-256

| 文件 | 字节 | SHA-256 |
|---|---|---|
| `V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md` | 18745 | `7a3f2e4b7a480bfa31ad20be56b63f9973a9db2296be2a364258e7b5f15e478b` |
| `V1_E2E_CASES_v0.1.json` | 50621 | `dae6399cec4afeec66a693868df80200859a88025eda8bdab3fbac50afc7e132` |
| `V1_QUALITY_COMPARISON_INPUTS_v0.1.md` | 67453 | `3838606f364642dee27a44ab34ff67654c8d20d8d6736abd2113cfcf27d0d35d` |
| `v1_demo_e2e_replay.py` | 15072 | `66cdf50473f422b4f22877d94642186831a9285b4cd796be782fb9e67fd0bbcd` |
| `v1_quality_comparison_run.py` | 8185 | `fe951e5331c1cf902e8c9bf59d753e9e6fd8a9e9939ec7a84137e0a0e069a5d4` |
| `v1_e2e_quality_eval.py` | 16268 | `00d56bbe36743cb70cd898c75423c8ee49f52df6969bd1eb9bb7ef9a9fc1797b` |
| `v1_quality_blind_pack.py` | 13924 | `471a94079736cad26b5843cb98affcb3b31b204a281b4d885851462d4c3869d5` |
| `v1_e2e_report_gen.py` | 9321 | `40377aa3b0cb71833f4d9db36c7e30778204cff87ce01a2b83594653c6276fe6` |
| `v1_e2e_manifest_gen.py` | 6336 | `8ab6a81b9bb765b8cbc4df7b98ebaa400f19a1094e9d500ac00bb20ce0037260` |
| `V1_E2E_RUN_002_RAW.md` | 130240 | `b1fb39084682ef3c469135bfea0f16741e2f73417937e1344d402c76ac27fdf3` |
| `V1_E2E_RUN_002_TRACE.md` | 39957 | `e41c7a1699a5d12a99292ce456109dcbaa725893df2e3bd6faab2fed3ac445ba` |
| `V1_E2E_RUN_002_EVAL.md` | 15182 | `9d2c8ddb64801aa3c66396c258dc9125a089658e06b630b36d30ea40c76ede84` |
| `V1_QUALITY_COMPARISON_RUN_001_RAW.md` | 149510 | `12a1ffd65d953ae26a25ecb8ba75b0077de1be43f72debaedeebf04b060effe8` |
| `V1_QUALITY_BLIND_REVIEW_PACK_v0.1.md` | 135556 | `7ec87de9f76ef60c8d77df118a3a18fa8a806890b52f295b580805dc71d1d1af` |
| `testapps/TEST_MATRIX_QWEN38MAX.yml` | 32732 | `1c18b45bc1795a7497965b3703d97f2d59fd27a03fca7cdbd0788174a0f58963` |
| `testapps/TEST_CAMPAIGN_QWEN38MAX.yml` | 159846 | `a51b229802265891fba1b7b0862fa8381823b730627994a3bc7cba71d02899e6` |
| `testapps/TEST_CONTENT_BRIEF_QWEN38MAX.yml` | 66251 | `40558a738a5b4e35f99d9a1a54d57fe9558a2cffb75c0cbbfa730edbe16b3cca` |
| `testapps/TEST_MATRIX_NOSKILL.yml` | 20206 | `1cf99a75dd8d99d6fc01593915411bcc162ca814707ee18873f8318080d3e926` |
| `testapps/TEST_CAMPAIGN_NOSKILL.yml` | 138105 | `eea48e105aa5458c68c781c8be72161caffcda667e85f2aa94969375befbbcab` |
| `testapps/TEST_CONTENT_BRIEF_NOSKILL.yml` | 48188 | `02ebb042088812c0584e6749b484e2082e1eaea80da0a6bca785d5857b29d8a0` |

> 本清单自身的 SHA 不在表内（自指），以提交后的 git blob 为准。
