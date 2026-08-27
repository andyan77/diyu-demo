# `M3-ECC-REBIND-003` · 附录修订 001：缺陷 G-1 的修复与影响面

> 修订对象：`M3_ECC_REBIND_003_FROZEN_v1.0.md` §1 的绑定表
> 触发事件：**本轮正式取证过程中，v1.2 闸门自己造成了一次事故**——
> 纵向 `E07` 里它把模型一句**正确**的话判成"与输入矛盾"，补齐节点据此把它改成了一句**假话**。
> 完整现场见 `account-operations/evidence/ep14-gate-v12-defect/DEFECT_G1_GATE_INDUCED_FALSEHOOD.md`。
> 原文不覆盖、不删除，本文件作为后继版本追加。

## 1. 改了什么

`shared_checks.check_input_contradiction` 的否定短语判据：

- 删掉 `没有任何` 这类**只描述内容**的泛化否定；
- 否定短语后 12 字内出现 `提到|涉及|包含|说到|谈到|写到|支持|指向|要求|表明|显示` 的，整个命中作废
  —— 那说明否定的对象是**话题**，不是槽位本身。

两条新夹具双向锁死（`POS-P7-topic-absent-not-slot-absent` / `NEG-P8-slot-absent-still-caught`），
夹具总数 26 → **28，28/28 通过**。

## 2. 新绑定

| 绑定 | 值 |
|---|---|
| Dify 草稿图 hash | `2f317ab9d8a04f7b…` |
| `shared_checks.py` | `bc895e8baf344eab…` |
| `gate_main.py` | `ad99abf35ed8f085…` |
| `assemble_main.py` | `2d1a5fd4e1ba91e5…` |
| `post_gate_main.py` | `02a842c84eb8589a…` |
| `projection_v12.py` | `60d05b69549c2916…` |
| `SKILL.md` | **未改动**，仍为 `343758f3c2da5694…` |

`SKILL.md` 一个字节没动——这次改的只是载体侧的一条检查，不是产品语义。

## 3. 影响面（A3，机械证明，不靠声明）

对**每一次**已完成的运行，用改后的闸门重放同一份 `draft_raw`，与记录里改前的判定
逐项比对 13 个决定量（`gate_status`、`missing_items`、`unanchored_items`、`hollow_items`、`decorative_items`、`overlapping_anchors` 等）：

```text
重放 73 次运行
  不受影响 72 次  —— 改后闸门的判定与改前**逐项相同**，
                        即这些运行的处理过程未被本次改动触及
  受影响    1 次  —— ep07-longitudinal-v12/E07
                        差异字段：['gate_status', 'input_contradiction']
```

结果落盘在 `account-operations/evidence/ep14-gate-v12-defect/unaffected_proof.json`，可独立重算。

### 3.1 因此，谁失效、谁不失效

```text
不失效（已机械证明不受影响，A3 明写"已证明不受影响的证据继续复用"）
  ECC-M3-RUNTIME-FIDELITY-001    9 例
  ECC-M3-RUNTIME-BEHAVIOR-002    49 例
  ECC-M3-MODULE-AB-001/002       12 次（候选臂 3 次逐项相同，其余三臂不过闸门）

失效（必须整条重跑）
  ECC-M3-LONGITUDINAL-001        12 步
    —— E07 判定不同，且其最终正文含一句由补齐节点写出的假话；
       E08 起的 standing_cycle_baseline 由它派生；
       冻结件 v1.1 §5 写死"序列不可局部重跑"
```

**不整轮作废**，因为 A3 明写「不使有证据不受影响的项失效」；
**不口头保证**，因为上面那条重放比对是机械的、逐项的、可重算的。

### 3.2 影响关系无法判断的项

**无。** 改动只落在一个函数的一个正则上，其调用点在 `gate_main` 与 `post_gate_main` 各一处，
依赖边可枚举完毕。

## 4. 这一轮已经产出、且不因本修订失效的判定

- 保真 ECC 独立判定（9/9「成功」）：其绑定的 9 次运行在 §3 中被证明不受影响，判定继续有效；
- A/B 36 名单臂盲评者的判定：候选臂 3 次运行不受影响，判定继续有效；
- 纵向 ECC 的判定：**它判的是失效的那一轮**。其结论不用于 `M3-AC-17`，
  但作为"缺陷 G-1 造成了什么后果"的证据保留，并单独标注。

```text
END_MARKER = M3-ECC-REBIND-003-FROZEN-v1.0-ADDENDUM-001-END
```
