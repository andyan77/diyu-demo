# 这一轮为什么中断，以及为什么整条重跑（保留，不用于任何判定）

## 事实

```text
E01   succeeded（一次上游传输故障后自动重试成功），tok=56447，303s
E02   从未发起
崩溃  run_longitudinal_v13.py:185  KeyError: 'objects_before'
```

原因是**执行侧的代码错误，与模型输出无关**：投影 v1.2 → v1.3 换掉了记录字段
（`objects_before` / `objects_not_restated` → `positions_before` / `positions_unaccounted`），
runner 里建索引那几行还在读旧键。任何一份输出都会在同一行崩。

## 必须自己说清楚的一件事

**执行侧在整条重跑之前已经看过这份 E01 的输出。** 这一点不隐瞒。

第 6 轮独立收口 Reviewer 判过完全同类的一次（`R-5`），结论是不构成择优，
理由不是动机声明，而是**择优所需的梯度不存在**：三份 E01 的输入逐字节相同、
闸门十三项判定全同，被丢弃的那份反而最长。本次同理——输入取自同一份冻结的
`_steps.json`，重跑不换任何输入。**这条仍然交给独立判定者复核，不由执行侧自己判。**

## 这是第二次栽在同一类错误上

第 5 轮也是字段改名后 runner 漏改一处（`objects_dropped_without_notice`），
同样跑到一半崩。两次都不是模型问题，都是执行侧的机械疏忽。

**因此这次不只是改一行**：`run_longitudinal_v13.py` 开跑前先用一份假记录跑一次投影，
把 runner 将要读的每一个键逐个断言存在——**没花任何 API 成本之前就会失败**。
判据写在 `_projection_record_contract` 里，字段再改一次也会立刻被挡住。

## 处置

- 本目录**保留不删**，`E01.json` 原样在此，**不进入任何判定**；
- 整条序列从第 1 步重跑到 `ep07-longitudinal-v13/`，依据是冻结件
  `M3_ECC_LONGITUDINAL_001_FROZEN_v1.1.md` §5「序列不可局部重跑」——
  这条规则冻结在结果之前，不是事后发明的。
