# 载体 v1.2 必填项闸门 —— 源码

这四个文件是**部署进 Dify 候选 App 三个代码节点的同一份源**。
部署脚本（`scratch:/m3/v12/update_m3_app_v12.py`）用
`shared_checks.py + <node>_main.py` 拼出每个节点的代码，
因此"三个节点的检查逻辑一致"由构造保证，不靠人工同步。

| 文件 | 落在哪个节点 |
|---|---|
| `shared_checks.py` | 三个代码节点共用的检查块（拼接进每个节点） |
| `gate_main.py` | `required_item_gate` |
| `assemble_main.py` | `assemble` |
| `post_gate_main.py` | `post_gate` |
| `projection_v12.py` | 不进 Dify —— 纵向 harness 侧的周期状态投影，见 `M3_ECC_LONGITUDINAL_001_FROZEN_v1.1.md` §3 |

测试在 `account-operations/tests/`，夹具在 `account-operations/fixtures/gate_fixtures_v12.json`。
