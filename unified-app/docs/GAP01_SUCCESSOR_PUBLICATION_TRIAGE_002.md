# FAILURE TRIAGE · GAP-01 successor publisher console-call reference

observed_failure: 修正 Console 类型后，发布器在首个 GET 调用前抛出
`AttributeError: module 'gap01_build_base' has no attribute 'console_call'`。

frozen_target: 与 Triage 001 相同的 UAPP canonical candidate。

confirmed_origin: `INPUT_ENVIRONMENT_OR_TOOL`。HTTP helper 与 Dify client 一样位于 GAP build 的
父模块 `BASE` 中；发布器仍少取一层。失败发生在 helper 解析时，未发出 HTTP 请求。

evidence: publication 文件仍不存在；线上 UAPP md5 仍为 predecessor；模型、workflow 与数据
副作用 0。

mutation_target: 发布器 `console_call` 引用；候选和全部正式冻结件不变。

next_reverification: py_compile、ruff、同一 canonical 候选发布与回读。

model_calls_before_failure: `0`。side_effects: `0`。
