# FAILURE TRIAGE · GAP-01 successor publisher module reference

observed_failure: `GAP01_SUCCESSOR_PUBLISH_v1.0.py` 在构造 Console 客户端前抛出
`AttributeError: module 'gap01_build_base' has no attribute 'DC'`。

frozen_target: 发布 canonical sha256
`65f46389f8f1a1334050427acee5788769f9032342e4423ec03878af4b59bcf2` 的 UAPP 候选，随后逐字回读。

candidate_sources: `INPUT_ENVIRONMENT_OR_TOOL`。

confirmed_origin: `INPUT_ENVIRONMENT_OR_TOOL`。发布器加载的是 GAP build 模块；Dify client 位于
其父模块的 `BASE` 成员，发布器少取了一层。异常发生在任何 Console 请求之前。

evidence: Python traceback 指向 `console = BUILD.BASE.DC.Console(...)`；publication evidence 文件
不存在；线上 UAPP 仍为 `7932502949d91ad366a4fa70d39a8a56`；活动 workflow 0。

mutation_target: `GAP01_SUCCESSOR_PUBLISH_v1.0.py` 的模块引用。

protected_targets: 候选图、Gate、输入、Checker、UAPP/PP/Seam/Hop/专业应用、数据库和 main。

next_reverification: py_compile + ruff 后运行同一零模型发布器，回读 canonical sha256 与完整保护面。

model_calls_before_failure: `0`。

side_effects: `0`；没有 draft、publish、workflow run、模型、M2 或 Git 远端写入。
