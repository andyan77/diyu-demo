# EP-08 A/B 模块消融与专业增益 · 载体 v1.2 轮

## 读这个目录之前必须知道的一件事

`_unblinded_results_v3.json` 里的 `"M3-AC-01③": "PASS"` 是**推导脚本的输出**，
**不是该 AC 的正式状态**。

本轮的盲评协议（`ADDENDUM_002` §2.3）在**判定冻结、揭盲之后**被原地改写过。
按通用内核 A2「判据在看到结果后才定或改，本次运行只算探索，不产生正式 `PASS`」，
`AC-01③` 的正式等级已下调为 **`NOT_VERIFIED`（探索级结论）**。

- 完整事实与两条出路：`M3_ECC_MODULE_AB_001_FROZEN_v1.0_ADDENDUM_003.md` §1、§4
- 发现者：`M3_INDEPENDENT_CLOSEOUT_REVIEW_V12_v1.0.md` 阻断项 `B-1`
- `AC-18 = FAIL(INSUFFICIENT)` **不受影响**——降级不救回任何东西，它两种记法下都不是 `PASS`

## 目录内容

```text
FX-M3-HOLD-0N__{A,Aplus,B,Bprime}.json   12 次运行原始记录（3 场景 × 4 臂）
verdicts_raw/verdict_unit_NN_jN.json     36 份盲评判定原文（12 单元 × 3 名判定者）
derivation/_SEALED_AB_MAPPING_v3.json    单元 → (场景, 臂) 封存映射（已揭盲，落盘不再泄露）
derivation/assignments.json              单元 → 判定者分配表
derivation/blind_rubric.md               判定者拿到的判据（唯一一份，36 人相同）
derivation/unblind_v3.py                 当轮实际使用的揭盲与推导脚本（含时序断言）
derivation/recompute_from_repo.py        只用本目录材料重算推导并与落盘结果比对
_unblinded_results_v3.json               当轮揭盲与推导结果
recompute_check.json                     重算比对结果
_arms_and_holdouts_v3.json               四臂定义与三个留出场景
_leak_scan_v3.json                       四臂输出的内部字段泄漏扫描
```

## 独立重算

```bash
python3 derivation/recompute_from_repo.py
```

零参数，路径全部相对脚本自身，**只读本目录**。当前结果：

```text
36 份判定 → 12 个单元格 → grades 84 格、hard gates 60 格、三组推导
与 _unblinded_results_v3.json 比对：mismatches = 0（IDENTICAL）
```

推导规则（等第映射、三名取中位、硬门取多数、`B优`／`A优且实质`／`相当` 的阈值）
冻结在 `ADDENDUM_002` §2.4／§2.5，判定开始之前提交，此后一字节未动——
这一点由第 6 轮独立收口 Reviewer 独立核实（该次 diff 只有一个 hunk，落在 §2.3）。
