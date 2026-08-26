# `ECC-M3-MODULE-AB-001` 冻结件 · 附录修订 001（**收紧**，非放宽）

> 修订对象：`M3_ECC_MODULE_AB_001_FROZEN_v1.0.md` §4「盲评协议」
> 触发事件：独立收口审查 `M3_INDEPENDENT_CLOSEOUT_REVIEW_v1.0.md` 阻断项 B-2 的附带发现
> 时序合法性：**A/B 盲评尚未开跑**（12 次运行只跑完 6 次，判定一次都没做）。本修订发生在
> 任何判定结果产生之前，且方向是**收紧**，不触及 §5 硬门、§6 增益门、§7 结果空间的任何一个字。
> 原文不覆盖、不删除，本文件作为后继版本追加。

## 1. 原协议的漏洞（实测，不是推测）

`v1.0` §4 的事后核验只写了：

> 判定完成后，逐一 grep 判定者的执行记录，确认其未访问过 sealed mapping 文件或 arms 文件。

**漏了同目录下按臂命名的原始记录。** 收口审查者实测证明该盲评包可以被**平凡去盲**：

```text
blind/FX-M3-HOLD-01/{甲,乙,丙,丁}.md 的正文
  与父目录 account-operations/evidence/ep08-module-ab/FX-M3-HOLD-01__{Aplus,B,A,Bprime}.json
  的 answer_text 逐段对应
⇒ 只需读一层兄弟文件即可还原映射
⇒ SALT 在不在仓库里都不影响
```

也就是说：`v1.0` 的盲评是**名义上的盲评**。没有人利用这个漏洞（判定还没跑），但如果按原协议跑完再发现，整轮判定按其自身条款作废。

## 2. 修订内容

### 2.1 判定者拿到的东西改为仓库外的独立包

判定者**只被给到一个仓库之外的目录路径**，该目录只含：

```text
<out-of-repo>/ab-blind/<case_id>/_scenario.md
<out-of-repo>/ab-blind/<case_id>/{甲,乙,丙,丁}.md
<out-of-repo>/rubric.md              # M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md §5.2 / §5.3 原文摘录
```

判定者被明确禁止进入 `diyu-demo` 仓库与 `diyu-demo-worktrees` 下的任何路径。

### 2.2 事后核验范围扩到"任何可去盲的载体"

核验必须确认判定者**未访问过**下列任意一项：

```text
account-operations/evidence/ep08-module-ab/            （整个目录，不只是两个文件）
  ├─ *__A.json / *__Aplus.json / *__B.json / *__Bprime.json   ← 原协议漏掉的就是这一族
  ├─ _arms_and_holdouts.json
  ├─ A_baseline_prompt.md / A_baseline_competence_review.md
  └─ _incomplete_blind/
account-operations/skills/operating-one-account/       （B 臂的系统提示词就是它）
scratch 下的 _SEALED_AB_MAPPING.json
任何 M3_ECC_MODULE_AB_001_FROZEN_*.md
```

核验方法与 `account-operations/evidence/ep10-closeout/judge_isolation_verification.json` 相同：
解析判定者自己的执行记录，只扫**会造成文件访问**的参数（`Read.file_path` / `Bash.command` /
`Grep`/`Glob` 的 pattern 与 path），**不扫 `Write`/`Edit` 的正文**——判定者在自己文件里
提到某个文件名是"提及"，不是"读取"。

### 2.3 核验结果必须落成仓库内产物

不得只写在 commit message 里。比照
`account-operations/evidence/ep10-closeout/judge_isolation_verification.json` 的形式，
逐名判定者给出 `isolation_verdict: CLEAN | VIOLATION` 与其 allow-list 外的全部路径引用。

任一名判定者被证实访问过 §2.2 任一项 ⇒ **其判定作废，重新招募判定者**，不做"打个折继续用"。

## 3. 不变的部分（逐条确认，防止本修订被读成放宽）

- §1 四臂身份与系统提示词哈希：**不变**；
- §2 公平条件：**不变**；
- §3 留出集与其强度上限的如实记录：**不变**；
- §5 五项非补偿硬门：**不变**；
- §6 七维增益门与"整体增益成立"的定义：**不变**；
- §7 结果空间（含"未跑完 → `NOT_VERIFIED`，不得用部分场景宣称通过"）：**不变**；
- §8 四项已知混杂：**不变**；
- 已跑完的 6 次运行：**不重跑、不作废、不择优**，原始记录逐条保留。

## 4. 对当前状态的影响

`M3-AC-18` 与 `M3-AC-01③` 本轮仍是 `NOT_VERIFIED`——原因是 12 次运行只跑完 6 次（余额耗尽），
**不是**因为本修订。本修订解决的是"等余额恢复、补齐 12 次之后，那一轮盲评算不算数"。

```text
END_MARKER
= ECC-M3-MODULE-AB-001-FROZEN-v1.0-ADDENDUM-001-END
```
