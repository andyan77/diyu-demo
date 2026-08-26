# M3 独立收口审查（EP-09 / AC-19）

> Reviewer 身份声明：未参与实现、未参与任何判据撰写、未参与任何一次模型运行；无写权限，本次会话只写本文件一份。
> 本次审查被明确授权读取全部内容（Checkpoint、各份判定、验收判据、git log），因此**不存在"被禁读且确实未读"的文件**——本 Reviewer 的角色不是盲评者，是查"声明有没有超过证据"的审计者。
> 审查基线：`task/m3-account-content-operator-v1` @ `b1a1d35`（审查开始时为 `a715687`，进行中另一条工作线追加了 `b1a1d35` 的纵向判定，已一并纳入）。
> 唯一问题：**这份交付里，有没有任何一条声明的等级高于它的证据？**

## 汇总

| 项 | 结论 | 一句话 |
|---|---|---|
| R-1 · 判据先于结果 | `PASS` | 四份 ECC 冻结件全部早于其结果运行，且冻结后一次未被改动；唯一一处结果后编辑只动了 `本轮状态` 行，判据行逐字节未变 |
| R-2 · 声明等级不越级 | `PASS` | 全交付只有一条 AC 被标 `PASS`（AC-16 的直连半），其 7 组冻结输入全部实测；未见"有但不够"被填成 `PASS`，两处失败被如实记为 `不足`/`FAIL(INSUFFICIENT)` |
| R-3 · 失效传播不多算不少算 | `FAIL` | `M3_CHECKPOINT_ROUND_3.md` §4 在 `main` 已前进 9 分钟后仍写"本轮未变"，§8 以"复核"名义给出在该时点不可复现的 console 输出；漂移影响面核算把该缺陷的载体少算了一份 |
| R-4 · 边界与受保护资产 | `PASS` | 受保护目录对入场基线零改动，175 处变更全部是新增，六份既有 Skill 一个字节未动，全仓只出现一个 Dify App id，无 merge/push/force/amend/reset/squash |
| R-5 · 失败路径只追加不删除 | `PASS` | 第 1 轮组 6 失败证据与其 `FAIL` 判定仍在；14 例行为 402 失败、6 次 A/B 402 失败逐条保留；三套同用例结果分属三个不同绑定且各有判定，无择优 |
| R-6 · 声明上限反搜 | `PASS` | 11 条措辞在本分支新增的 59 份 md/yaml/py 中全部为禁止性用法（判据失败行、ECC 声明上限、Rubric 自身、Skill 禁令），零处肯定性使用 |
| R-7 · 留出与探索/正式分轨 | `NOT_CHECKED` | 留出顺序与真实上限如实成立；但"判定者工具调用记录"这项核验只对 4 名判定者中的 1 名做过，承载交付唯一 `PASS` 的 3 名保真判定者从未被核验，且其隔离性在三处被写成既成事实 |

---

## 逐项

### R-1 · 判据先于结果（A2 §时序）

**查了什么**

```console
$ git log --format="%h %ad %s" --date=format:"%H:%M:%S" df2c595..HEAD -- M3_ECC_*_FROZEN_*.md M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md
$ git show a8f7504 -- M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md
$ sha256sum account-operations/evidence/ep06b-runtime-behavior/_cases.json
$ sha256sum account-operations/evidence/ep08-module-ab/_arms_and_holdouts.json
$ python3 -c "…读每份 transcript 的 timestamp_utc…"
```

**发现**

逐份比对"判据冻结 commit 时刻"与"该批结果的最早一次运行时刻"（transcript 内的 `timestamp_utc`，UTC＝本地 +7）：

| 判据文件 | 冻结 commit / 时刻 | 该批最早运行 | 先后 |
|---|---|---|---|
| `RUNTIME_FIDELITY_001_FROZEN_v1.0` | `c64d762` 08:19:37 | 轮 1 `874bea1` 08:37 提交 | ✔ |
| 同上（轮 3 Dify 载体） | 同上 | `17:18:46Z` = 10:18:46 | ✔ |
| `RUNTIME_BEHAVIOR_002_FROZEN_v1.0` | `4bcaaa0` 10:23:58 | `17:28:12Z` = 10:28:12 | ✔ |
| `LONGITUDINAL_001_FROZEN_v1.0` | `4bcaaa0` 10:23:58 | `17:29:50Z` = 10:29:50 | ✔ |
| `MODULE_AB_001_FROZEN_v1.0` | `7564896` 10:33:32 | `17:38:53Z` = 10:38:53 | ✔ |

四份 ECC 冻结件**每一份都只有一个 commit 触碰过**（即创建它的那一个），冻结之后零改动。冻结件内声明的绑定哈希与今天的文件逐字节相符：`_cases.json` = `1da81ea6…9eb75`（冻结件 §头声明值），`_arms_and_holdouts.json` = `961e74f6…56b5`（冻结件 §头声明值），两处均实测一致。

唯一一处"结果之后修改判据文件"的痕迹在 `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`（`a8f7504`，09:18:10，晚于轮 1/轮 2 结果）。逐行核 diff：改动只有一行——AC-16 卡的 `本轮状态` 行，加上其后追加的一段实测记录。该卡的十项判据字段（命题／冻结输入／候选／锁定变量／Oracle／成功／不足／无结果／失败／反证探针）**一个字节都没变**。`本轮状态` 是结果登记位，不是判据位。

另核 `BEHAVIOR-002` §0 主动声明了它为什么另起一份 ECC 而不是扩写 `FIDELITY-001`——"在它上面追加判据等于看到结果之后改判据"。这条纪律在该处被正确执行。

**结论**：`PASS`。无任何一条判据在其结果产出后被修改。

---

### R-2 · 声明等级不越级（A2 §可信度阶梯）

**查了什么**

```console
$ grep -n "本轮状态" M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md          # 21 张卡逐条
$ sed -n '560,594p' M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md            # §7 状态矩阵
$ grep -rn "PASS" --include="M3_*.md" .                              # 全部 PASS 声明位
$ python3 …/_run_index.json                                          # 逐批实测覆盖率
```

**发现**

全交付**只有一条 AC 被标 `PASS`**：`M3-AC-16`，且状态行自带范围限定——`PASS`（Skill → 条件引用 → 直连 DeepSeek 链路）；`NOT_VERIFIED`（Dify Workflow/画布链路）。其余 20 条全部 `NOT_VERIFIED`。

逐条核 AC-16 的冻结输入是否**真的都被实测过**：冻结输入 = `ECC-M3-RUNTIME-FIDELITY-001` 的七组（正向／负向／边界／来源降级／动态证据过期／附件加载未加载／平台差异）。实测：`ep06-runtime-fidelity-v2/` 9 份 transcript，全部 `http_status=200`、`finish_reason=stop`、`model=deepseek-v4-flash`、`temperature=0.4`，覆盖全部 7 组 9 例，无一组缺跑。`成功` 条件是"全部 ≥7 组保真"，判定文件 `VERDICT_v1.1` 逐组给出可核查引用，7/7。**没有出现"某项冻结输入从未被实测却标 PASS"。**

三条反向测试：

1. **"有但不够"有没有被填成 `PASS`？** 没有，而且是反过来的。轮 1 组 6 被判 `不足`，`VERDICT_v1.0` 末行直接写"未达成全部 7 组成功，因此 `M3-AC-16` 不得判 `PASS`"，`PASS` 被卡住直到实现被修正并整轮重跑。刚落地的 `LONGITUDINAL_001_VERDICT_v1.0` 同样把 E04、E07 判 `不足`，整体 `FAIL(INSUFFICIENT)`，并明写"判据没有被放宽，也没有被部分满足即通过地读"。
2. **"尚未取证"有没有被写成 `FAIL`？** 没有。EP-08 只跑完 6/12，`_incomplete_blind/README.md` 按冻结件 §7 记 `NOT_VERIFIED` 而不是 `FAIL`，并明写"不得用部分场景宣称通过"。
3. **"计划"有没有被写成"已验证"？** 没有。Checkpoint 1、2 均以"本轮无任何一条 AC 被判 `PASS`"收尾；Checkpoint 3 §11 在 Dify Console 凭据打通后明写"**这不等于这些工作已经完成**——只是前置阻塞解除，尚未执行"。

**结论**：`PASS`。无任一 AC 的声明状态高于其可指认的证据。

---

### R-3 · 失效传播不多算不少算（A3）

**查了什么**

```console
$ git reflog show main --date=iso
$ git log --format="%h %ad" --date=iso df2c595..HEAD
$ git merge-base --is-ancestor 17ca3f7 HEAD          # → NO
$ git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence collab-ledger   # → 空
$ docker inspect -f '{{.State.StartedAt}}' diyu-m2-app
$ docker exec diyu-m2-app sha256sum /srv/app/api/knowledge.py  ↔  git show main:business-persistence/…
$ grep -rn "M3_CHECKPOINT_ROUND_3\|前两轮" --include=*.md .
```

**发现（先说做对的部分）**

`BASELINE_DRIFT_IMPACT_v1.0.md` 的核心影响面核算**是正确的，且不多算不少算**：

- 不多算——没有因为 `main` 动了就把全部证据置 `STALE`。逐条核对，`df2c595 → a7b8101` 只动了 `business-persistence/**` 与 M1 落地内容，与 Skill／四份 ECC／Dify 图/证据的绑定无交集，这些项**不失效**是正确处置。
- 不少算——它把 AC-12／AC-09 的 M2 接口版本绑定单独拎出来做定向复验，这确实是唯一真实受影响的依赖边。
- 那次 `STALE → CURRENT` 的上行**有事件支撑，不是"应该没变"**。我独立重跑了它的比对：

```console
$ docker inspect -f '{{.State.StartedAt}}' diyu-m2-app
2026-08-26T11:44:24.831195331Z  running=true
$ app/api/knowledge.py     容器 = 69f12b79f72c…  vs main(a7b8101) IDENTICAL   vs df2c595 DIFFERENT
$ app/models/knowledge.py  容器 = c39df6296727…  vs main(a7b8101) IDENTICAL   vs df2c595 DIFFERENT
$ stat -c '%y' account-operations/fixtures/m2_live_capture_v1.json
2026-08-26 05:04:08 -0700  (= 12:04:08Z，晚于容器启动 11:44:24Z，同一实例未重建)
```

三条结论逐条复现，该文件 §3 的实测记录属实。

**发现（缺陷）**

`M3_CHECKPOINT_ROUND_3.md`（commit `a8f7504`，作者与提交时刻同为 **09:18:10**）：

- **§4 抬头**：「`main` HEAD 入场时 `df2c595`，**本轮未变**。」
- **§8 抬头**：「受保护模块与回滚（**复核**，同前两轮结论不变）」，其下给出两条 console 输出：

```console
$ git diff --stat main -- content-production decision-chain business-persistence collab-ledger
（无输出）
$ git merge-base --is-ancestor main task/m3-account-content-operator-v1 && echo OK
OK
```

实测 `main` 的 reflog：

```console
17ca3f7 main@{2026-08-26 09:08:51 -0700}: merge origin/task/m2-…: Merge made by the 'ort' strategy.
```

即 `main` 在该 Checkpoint 提交前 **9 分 19 秒**就已经离开 `df2c595`。而该文件 §2 列出的 commit 清单最后一条是 `de13ec1`（09:14:41），证明正文是在 09:14 之后写的——写下"本轮未变"时，`main` 已经变了。

进一步实测 `git merge-base --is-ancestor 17ca3f7 HEAD` → **NO**，`git diff --stat 17ca3f7 HEAD -- <四个受保护目录>` → **1535 行删除**。也就是说 §8 那两条输出在它自称的时点**都不可能产出**——它们是前一轮的值被以"复核"名义原样带下来的。

这正落在 R-3 的 FAIL 条款上：**把"应该没变"当成"已核验没变"**。

第二处是 **少算**。`BASELINE_DRIFT_IMPACT_v1.0.md` §4 更正这条口径时写的是「**前两轮** Checkpoint 用过这条自证」。实测：Round 1／Round 2／Round 3 **三轮都用过**（`grep -n "diff --stat main" M3_CHECKPOINT_ROUND_*.md` 命中 Round 2 §9 与 Round 3 §8，Round 3 且额外带一句"本轮未变"的事实性错误）。失效集遗漏了已知依赖中的一份，且 Round 3 那句事实性错误在全仓**没有任何一处被更正**（`grep -rn "M3_CHECKPOINT_ROUND_3" --include=*.md .` 只命中该文件自身）。

**必须说清的边界**：这条缺陷**不影响受保护目录的实质结论**。我用正确口径独立重测，`git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence collab-ledger` = 空。**受保护目录确实零改动**——错的是自证方法与那句"本轮未变"，不是被自证的事实。

**结论**：`FAIL`。见阻断项 B-1。

---

### R-4 · 边界与受保护资产（A4）

**查了什么**

```console
$ git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence collab-ledger
$ git diff --name-status df2c595 HEAD | sort | uniq -c -w1
$ git diff --name-status df2c595 HEAD | grep -v "^A"
$ grep -rhoE "app_id[\":= ]+[0-9a-f-]{36}" $(git diff --name-only df2c595 HEAD) | sort | uniq -c
$ git log --format="%h|%p" df2c595..HEAD | awk -F'|' '{if(split($2,p," ")>1) print "MERGE"}'
$ git log --format="ad=%ad cd=%cd" --date=iso df2c595..HEAD
$ git ls-remote origin | grep -i m3
```

**发现**

| 检查 | 实测 |
|---|---|
| 受保护目录 vs 入场基线 `df2c595` | `git diff --stat` **空输出** |
| 全分支变更性质 | **175 项全部是 `A`（新增）**；`grep -v "^A"` 零命中，即无一处修改、删除或重命名 |
| 六份既有 Skill | 位于 `content-production/skills/**`（3 份）与 `decision-chain/skills/**`（Matrix/Campaign/Content Brief），**全部落在零改动的受保护目录内，一个字节未动** |
| Dify App | 全部 175 份新增文件中 app_id 只出现 **一个**：`b7fb5b1a-9278-426c-bb8a-f9f288639548`，共 76 次；无第二个 app id |
| Dify 运行记录 | 回滚演练 step 7 复查 `published_version` 与 `published_graph_sha256` 未变；演练在 draft 上做，发布版本未被触碰 |
| merge / 直推 main | 20 个 commit **全部单父**，无 merge commit；`main` 反而不是本分支祖先（本分支从未把 `main` 并进来） |
| force / amend / rebase / squash | 20 个 commit 的 `author date` 与 `committer date` **逐条相等**，无改写痕迹；reflog 只有 `commit:` 条目 |
| 远端 | `git ls-remote origin` 无任何 m3 相关 ref——**未推送**（与 AC-20 记 `NOT_VERIFIED` 一致） |

**结论**：`PASS`。无任一越界。

---

### R-5 · 失败路径只追加不删除

**查了什么**

```console
$ ls account-operations/evidence/*/            # 七个证据目录逐个点数
$ python3 …  ep06b/_run_index.json  → failed[14]，逐份打开核 raw_response_body
$ python3 …  ep08/_run_index.json   → failed[6]，逐份打开核 402
$ git log --stat df2c595..HEAD                 # 有无删除或覆盖
```

**发现**

1. **第 1 轮 EP-06 的失败证据仍在**：`account-operations/evidence/ep06-runtime-fidelity/`（10 份，含被判 `不足` 的 `G6-attachment-unloaded.json`）完整存在，与修复后的 `ep06-runtime-fidelity-v2/` **并存而非被覆盖**；记录该失败的 `M3_ECC_RUNTIME_FIDELITY_001_VERDICT_v1.0.md`（"7 组中 6 组成功，组 6 为不足…因此不得判 `PASS`"）**没有被 v1.1 删除或替换**，两份并列在仓库里。全分支 175 项变更零删除，从 git 层面也不可能存在覆盖。

2. **本轮余额耗尽的失败逐条保留**：
   - `ep06b-runtime-behavior`：49 例中 14 例 `workflow_status=failed`，14 份独立 JSON 全部存在，各带 `raw_response_body`、`workflow_run_id`、`timestamp_utc`，无一份被删；
   - `ep08-module-ab`：12 次运行中 6 次 `http_status=402`，`raw_response_body` 逐字保留 `{"error":{"message":"Insufficient Balance",…}}`，`answer_text` 为空串而不是被删除的字段；
   - `_incomplete_blind/README.md` 写明为什么把 HOLD-02／HOLD-03 移出盲评包（避免判定者拿到空白对照臂），并明写"已跑完的 6 次运行原始记录逐条保留在上级目录，未删除、未重跑、未择优"，还预先禁止了"只补跑失败的那几次再与本轮混判"。

3. **有没有"看到结果后重抽"？** 同一批 9 个用例确实存在三套结果（`ep06-runtime-fidelity` / `-v2` / `-dify`）。逐条核绑定：轮 1 = Skill@`874bea1` 之前 + 直连；轮 2 = Skill@`af61b82` + 直连；轮 3 = Skill@`af61b82` + Dify 载体。**三者是三个不同绑定，不是同一绑定下的重抽**，且**三套各自都有独立判定文件**（v1.0 / v1.1 / DIFY v1.0），没有出现"跑了几套只用其中一套"。轮 1→轮 2 之间改的是被测实现（`SKILL.md` O-6），不是判据，且 AC 卡记录里按 A3 把**全部 9 组**前序证据置 `STALE`（而不是只置组 6），这是不少算的正确处置。

4. 刚落地的 `LONGITUDINAL_001_VERDICT_v1.0` 在判出 `FAIL(INSUFFICIENT)` 后**明确拒绝当场改 `SKILL.md`**，理由是"Skill 是四份 ECC 的共同锁定变量，改一个字四份证据全部作废"，把缺陷登记下来等整轮重跑——这是不用修复动作掩盖失败的正确做法。

**结论**：`PASS`。无任一失败 Attempt 被删除、覆盖或择优丢弃。

---

### R-6 · 声明上限（AC-20 反证探针）

**查了什么**

```console
$ FILES=$(git diff --name-only df2c595 HEAD | grep -E '\.(md|yaml|py)$')   # 59 份
$ for pat in 生产就绪 真实经营提升 因果 纵向切片完成 平台唯一 已经避开同质化 \
             REAL_OPERATION_LOOP_VERIFIED OPERATIONAL_UPLIFT_PROVEN CAUSAL_BUSINESS_LIFT_PROVEN \
             UNIVERSAL_SUPERIORITY "M5 集成增益" ; do grep -n -F "$pat" $FILES ; done
```

**发现**

11 条措辞在本分支新增的 59 份治理／代码文件中的**每一处命中**，逐条核其用法：

| 命中类型 | 例 |
|---|---|
| 判据的**失败**条款 | AC-20 「失败｜出现"生产就绪""真实经营提升""单账号纵向切片完成"等超出证据的声明」 |
| ECC 的**声明上限**章节（禁止性） | `MODULE_AB` §9「**不能**建立：M5 集成增益／真实经营提升或因果提升／生产就绪…」；`BEHAVIOR_002` §7 同形 |
| Rubric 自身的反搜清单 | 本次 Rubric §R-6 第 65–67 行 |
| Skill 正文的**禁令** | `SKILL.md`「**不做**：…声称真实经营提升」「**不得声称**"平台稀缺""平台唯一""已经避开同质化"」 |
| 夹具的**负向探针**标签 | `M3_ACCEPTANCE_FIXTURES_v1.0.md` 把这些 token 列为要反搜的对象 |

**零处肯定性使用。** 反向检查也成立：`DONE` 在全交付中只出现在"不把等待写成 `DONE`""不得写 DONE"这类禁止语境，两份 Checkpoint 抬头均写 `terminal_state = 不是终态`。

另核一处最容易越级的地方——Checkpoint 3 §11 记录 Founder 排除 Qwen 时的措辞：它没有把跳过 Qwen 写成"该项通过"，而是如实写"按契约原文，跳过 Qwen 意味着依赖 Qwen 独立核验的验收项无法达到契约 v1.2 定义的完整 `PASS`/`DONE`……按 Founder 指示以 `NOT_APPLICABLE` 处理，而不是自行回填为 `PASS`"，并把是否 REBASE 契约交回 Founder。这是正确的跨域处置。

**结论**：`PASS`。无任一措辞在无对应证据时被肯定性使用。

---

### R-7 · 留出与探索/正式分轨（AC-19 本体）

**查了什么**

```console
$ git log --format="%h %ad %s" --date=format:"%H:%M:%S" df2c595..HEAD -- account-operations/skills/operating-one-account/SKILL.md
$ git log --format="%h %ad" --date=format:"%H:%M:%S" -1 -- account-operations/evidence/ep08-module-ab/_arms_and_holdouts.json
$ python3 … 比对 blind/FX-M3-HOLD-01/{甲乙丙丁}.md 与 FX-M3-HOLD-01__{A,Aplus,B,Bprime}.json
$ grep -rli "SALT\|sealed" account-operations/evidence/ep08-module-ab/
$ grep -rn "工具调用\|未读\|隔离" --include=*.md .   # 找核验记录
```

**逐条发现**

**① 留出夹具是否在 `SKILL.md` 冻结之后才存在（git 可证）？——成立。**
`SKILL.md` 最后一次改动 = `af61b82` @ 08:48:10。三个留出场景的内容随 `_arms_and_holdouts.json` 提交于 `7564896` @ 10:33:32，晚 1 小时 45 分。该文件的 `frozen_before_execution: true` 与最早一次 A/B 运行（`17:38:53Z` = 10:38:53）也顺序正确。**不存在"用留出集反向优化实现"的路径。**

**② 交付文档有没有如实记录留出强度的真实上限？——成立，而且是主动降级。**
`MODULE_AB` §3 逐字写：「但执行侧（= 实现侧）在 EP-08 运行时看得到夹具内容。因此留出强度**低于**"实现者全程不可见"的理想情形……**如实降级记录，不因此自动判 FAIL，也不假装留出是完美的**」，并规定三个夹具本轮后即退出留出集。§8「已知混杂」还预先声明了提示词长度不对称、单次采样、"判定者也是大模型，这不等于人类专家盲评"三条上限。**没有"完美留出"式表述。**

**③ 独立判定者有没有实际读过被禁止的文件？其工具调用记录是否被核验过？——这一项没有答案。**

仓库里现有四名判定者的产物。逐条核其访问核验记录：

| 判定者 | 隔离声明的措辞 | 工具调用记录被核验过吗 |
|---|---|---|
| `VERDICT_v1.0`（保真轮 1） | 「判定者**未读取**执行侧的 CHECKPOINT／ROLLBACK／MANIFEST／collab-ledger 任何文件」 | **无任何核验记录** |
| `VERDICT_v1.1`（保真轮 2） | 「未被提供执行侧判断或摘要、**未被提供任何前轮判定**」 | **无任何核验记录** |
| `VERDICT_DIFY_v1.0`（保真轮 3） | 「**未读任何** Checkpoint 或既有判定」 | **无任何核验记录** |
| `LONGITUDINAL_001_VERDICT_v1.0` | 「未读任何 Checkpoint / 其他 VERDICT / `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` / `ep07-longitudinal` 以外证据目录 / git 历史」 | **做过** —— commit `b1a1d35` 的 message：「判定者工具调用记录已逐条核验：未读任何 Checkpoint、其他 VERDICT、验收判据或其他证据目录。」但只写在 commit message 里，**不在任何仓库文件内** |

前三条全部是**平铺直叙的既成事实句**，其唯一来源是判定者对自己的自述与执行侧对自己实验装置的自述。按 A2，自述不是能把可信度往上抬的事件；这三句现在站在"已确认"位置，来源却在"未验证"位置。

这不是抽象顾虑：**AC-16 是全交付唯一的 `PASS`，而它的冻结 Oracle 原文就是"由未参与实现者按冻结清单判定"**——判定者的独立性是这条 `PASS` 的承重前提。Checkpoint 3 §4 做的独立复核是**对判定结论的复核**（读原始 transcript 确认组 6 的判定属实），不是对访问行为的核验，两者不能互相替代。

值得指出的是：本仓库对这类不可复核性**已有既定先例**。`collab-ledger/L1_TASK_MANIFESTS.md` 第 250 行对同一问题的处置是「如实标注，**不辩解**……是否接受这一层不可复核性，**报 Founder 裁决**」。M3 的三份保真判定没有走这条先例，而是直接写成了事实。`MODULE_AB` §4.6 反倒把这项核验写成了硬要求（"逐一检查每名判定者的执行记录……任一名判定者被证实访问过上述文件，其判定作废"）——纪律在设计上是有的，只是没有回头适用到已经产出的三份判定上。

**④ 探索性运行与正式取证是不是分开的？——成立。**
四份 ECC 各自带 §0 时序声明，冻结→运行的顺序 git 可证（见 R-1 表）。七个证据目录中没有任何一份"探索性"运行被混进正式证据集；`BEHAVIOR_002` §0 还预先写死了"判据晚于结果的本轮只算探索，不产生正式 `PASS`"。

**结论**：`NOT_CHECKED`。R-7 的两条 FAIL 条款我都无法证成——留出泄露**已被记录**（①②成立），而"判定者读过禁读文件"我无法证实也无法证伪，因为对 4 名判定者中的 3 名，这项核验**从来没有人做过**。我不会把一条没做过的核验判成 `PASS`，也不会在 FAIL 条款未被证成时伪造 `FAIL`。见阻断项 B-2。

---

## 阻断项（必须修复才能收口）

### B-1 · `M3_CHECKPOINT_ROUND_3.md` 里有一句与事实不符的自证，且更正范围少算一份（R-3 FAIL）

**事实**：该文件提交于 09:18:10，`main` 已于 09:08:51 从 `df2c595` 前进到 `17ca3f7`。文件 §4 仍写「`main` HEAD 入场时 `df2c595`，**本轮未变**」；§8 以「**复核**」为题给出的两条 console 输出（`git diff --stat main -- <受保护目录>` → 无输出；`git merge-base --is-ancestor main task/…` → `OK`），在该时点实测均不成立（我复测：`--is-ancestor 17ca3f7 HEAD` → `NO`；`diff --stat 17ca3f7 HEAD -- <受保护目录>` → 1535 行删除）。

**且**：`BASELINE_DRIFT_IMPACT_v1.0.md` §4 更正此口径时写「**前两轮** Checkpoint 用过这条自证」，实测是**三轮**（Round 2 §9 与 Round 3 §8 均命中）；Round 3 那句"本轮未变"在全仓无任何一处被更正。

**为什么阻断**：R-3 的 FAIL 条款逐字包含"把'应该没变'当成'已核验没变'"与"少算"，两者同时命中；且一份交付文档里现在留着一句可被 `git reflog` 一行推翻的事实性错误声明。

**修复口径（不需要重跑任何模型调用）**：在 `BASELINE_DRIFT_IMPACT_v1.0.md` 追加更正，把载体范围从"前两轮"改为**三轮全部**，并点名 Round 3 §4 的"本轮未变"与 §8 的"复核"抬头为过时且与事实不符；正确口径统一为对共同祖先 `df2c595` 比对。**账本只追加不改写**——不要回去修改 Round 3 的原文。

**必须一并保留的事实**：受保护目录的**实质结论没有错**。我用正确口径独立复测，`git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence collab-ledger` 为空。错的是自证方法与那一句话，不是被自证的事实。修复时不要把这条写成"边界被突破"。

---

### B-2 · 三名保真判定者的隔离性被写成既成事实，但其工具调用记录从未被核验（R-7 `NOT_CHECKED`）

**事实**：`VERDICT_v1.0` / `VERDICT_v1.1` / `VERDICT_DIFY_v1.0` 三份判定的抬头分别以"未读取执行侧的 CHECKPOINT／…任何文件""未被提供任何前轮判定""未读任何 Checkpoint 或既有判定"的**事实句**声明隔离性，同样的表述又被复制进 `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` 第 362 行与 `M3_CHECKPOINT_ROUND_3.md` §1。仓库内**不存在**任何一份核验这三名判定者访问行为的记录。第四名判定者（纵向）做了这项核验，但结果只写在 commit `b1a1d35` 的 message 里，没有落成仓库内的可核查产物。

**为什么阻断**：本次 Rubric R-7 把"其工具调用记录是否被核验过"列为必答项；`ECC-M3-MODULE-AB-001` §4.6 自己也把这项定为硬要求。更关键的是 **AC-16 是全交付唯一的 `PASS`，其冻结 Oracle 明文要求"由未参与实现者判定"**——判定者独立性是这条 `PASS` 的承重前提，该前提目前只有自述支撑。Checkpoint 3 §4 复核的是**判定结论**，不是访问行为，替代不了。

**修复口径（二选一，都不需要重跑模型调用）**：

- **(a) 补做核验**：若三名保真判定者的工具调用记录仍可取，逐条 grep 其是否访问过 Checkpoint／其他 VERDICT／`M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`／`ep06-runtime-fidelity*` 以外的证据目录，结果落成仓库内产物（比照纵向判定的做法，但要写进文件而不是只写进 commit message）；或
- **(b) 如实降级措辞**：若记录已不可取，把三处"未读…"从事实句改为**自述且未核验**，并按本仓库既有先例（`collab-ledger/L1_TASK_MANIFESTS.md` 第 250 行）把"是否接受这一层不可复核性"**报 Founder 裁决**；同时在 AC-16 的 `PASS` 旁标注该 `PASS` 依赖一项未核验的前提。

**顺带必须一起处理的一条**（同属 B-2 的修复面，因为它决定尚未进行的 A/B 盲评是否有效）：`_arms_and_holdouts.json` 的 `post_hoc_check` 只要求核验判定者"未访问过 sealed mapping 文件或 arms 文件"，**漏了同目录下按臂命名的原始记录**。我实测该盲评包可被平凡去盲——`blind/FX-M3-HOLD-01/{甲,乙,丙,丁}.md` 的正文与父目录 `FX-M3-HOLD-01__{Aplus,B,A,Bprime}.json` 的 `answer_text` 逐段对应（甲=Aplus、乙=B、丙=A、丁=Bprime），只需读一层兄弟文件即可还原映射，`SALT` 在不在仓库里都不影响。A/B 盲评尚未开跑，此刻扩充 `post_hoc_check` 的覆盖范围即可，成本为零；若等跑完再发现，整轮判定按 §4.6 作废。

---

## 非阻断观察（登记为新任务候选，不在本任务内处理）

**O-1 · `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` §7 状态矩阵已过时，与 §3 自相矛盾。**
§3 的 AC-16 卡写 `PASS`（直连半），§7 矩阵仍写 `NOT_VERIFIED`，并以「**本轮没有任何一条 AC 被判定为 `PASS`**」收尾。方向是保守的（低报而非高报），不构成 R-2 越级；但同一文件内两处对同一条 AC 的状态互相矛盾，属 A3 意义上的"主本变化未同步副本"。

**O-2 · 同一份 v1.0 文件同时承载冻结判据与可变状态登记位。**
`本轮状态` 行按设计要随取证更新，但它与十项冻结判据字段同处一张卡、同一个 v1.0 版本号。结果是"这次改动到底动没动判据"只能靠 diff git 回答（我这次就是这么答的）。判据与状态分文件，或状态更新时带版本后缀，能让 R-1 这类检查不依赖 git 考古。

**O-3 · AC-16 的 `锁定变量` 含"Workflow 图"，但拿到 `PASS` 的那两轮里它并不在场。**
AC-16 的命题原文是"经 Skill → 条件引用 → **Workflow → Dify** → 准确 DeepSeek 运行"，`锁定变量` 也列了"Workflow 图"。判 `PASS` 的第 2 轮走的是直连 API，无 Workflow 图。交付把单一状态位拆成"直连半 `PASS` ／ 画布半 `NOT_VERIFIED`"，这个二分**是看到结果之后才引入的**，冻结卡本身没有定义可分别通过的两半。按本次 Rubric R-2 的三条判别（冻结输入是否都实测／有但不够是否填成 PASS／未取证是否写成 FAIL）它都不命中，故不阻断；但若将来要把 AC-16 整条收口，应版本化一份把"分载体判定"写进判据的修订，而不是继续沿用这个事后二分。

**O-4 · Dify 画布链路的保真证据已经存在，AC-16 的画布半却仍记 `NOT_VERIFIED`。**
`VERDICT_DIFY_v1.0` 判出 7/7 成功（9 次 Dify Workflow 运行，全部 `workflow_status=succeeded`），但 AC 卡最后一次更新在 09:18，早于该批 10:18 的运行，因此画布半的状态没跟上。这是**低报**，不是越级。同时需要注意 `FIDELITY_001_FROZEN_v1.0` §5 明文写过"**不建立** Dify 画布级/Workflow 图级证据"——该冻结件从未被版本化修订，第 3 轮却在同一 ECC id 下换了载体重跑。判定者本人在其附录 A1 里主动指出了这处载体不一致并声明"本判定不回答这批运行能否落在冻结件 §5 的声明上限之内——那是合同范围问题，不属判定者职权"，处置是克制且正确的。要把这批证据用于收口 AC-16，需要一份版本化的 ECC 修订说明载体扩展，不能靠沿用。

**O-5 · 共用 Dify 实例的 Console 口令被轮换，该副作用只登记在本任务分支内。**
Checkpoint 3 §11 完整记录了：执行侧核验出 `INIT_PASSWORD` 路线不通、拒绝执行、改提 `flask reset-password`、该命令被权限分类器拦截、最终由 **Founder 本人在宿主机执行**。披露是充分的，授权域也正确（A1：有权者决定）。但该 Dify 实例与 M2 共用，而这条跨任务副作用没有进 `collab-ledger/L5_SIDE_EFFECTS.md`——这是**正确行为**（collab-ledger 是本任务的受保护目录，不得触碰），代价是其他工作线看不到它。登记为新任务候选：收口时由有权触碰 collab-ledger 的任务补登 L5。

**O-6 · `ep06b-runtime-behavior/_run_index.json` 的 `case_file_sha256_at_run` 为 `null`。**
运行时绑定哈希这个字段留了位但没填。实质影响很小——`_cases.json` 早于运行提交、此后零改动、且今日实测哈希与冻结件声明值一致，绑定仍可由 git 证成。但字段留空会让"运行时用的到底是不是这份"必须绕道 git 才能回答。

**O-7 · 判定者与 A 臂撰写者同为大模型代理，且共享同一份账户级协作宪法。**
`MODULE_AB` §8 已把这条作为已知混杂预先声明，并指出其方向对 B 不利、不构成偏袒，还写明"这不等于人类专家盲评，如实记录为证据强度上限"。处置得当，此处只作登记：任何基于该 A/B 的模块增益结论，其证据强度上限就停在这里。

---

---

## 附录 · 审查基线之外出现的产物（披露，不构成第二轮 Review）

本次 Review 预算为**一轮**，七项结论全部锚定在 `b1a1d35`。在我写结论的过程中，工作树里又出现了一份**未跟踪**的新文件 `M3_FOUNDER_ACCEPTANCE_PACKAGE_v1.0.md`（245 行）。它**不在**我的审查基线内，我**没有**对它执行七项审查。

按 A4"披露会改变原结论或合同前提的异常"，只登记两点：

1. **对它做的最低限度扫描是干净的**：R-6 的 11 条措辞在其中全部为否定性用法（如"❌ 真实经营提升——全部反馈都是构造输入，与真实经营无关"）；终态登记为 `M3_FOUNDER_DIFY_ACCEPTANCE = AWAITING_FOUNDER`、`M3_ENGINEERING_TASK = IN_PROGRESS（不是 DONE，也不是 FAILED）`，未把等待写成 `DONE`；`AC-17` 的 `FAIL(INSUFFICIENT)` 与 `AC-18` 的 `NOT_VERIFIED` 都如实上报。

2. **有一条声明直接落在本审查 O-4 的口子上，请在收口前一并处置**：该文件 §13 证据分层写「✅ 语义经工程化后没有丢失 —— AC-16，**两条链路各 7/7 组保真**」。这把 AC-16 的**画布半**从 `NOT_VERIFIED` 提到了 ✅。该提升的**运行证据是存在的**（`VERDICT_DIFY_v1.0`，9 次 Dify Workflow 运行 7/7），但按 O-4：`FIDELITY_001_FROZEN_v1.0` §5 原文写着"**不建立** Dify 画布级/Workflow 图级证据"，该冻结件至今未被版本化修订；判定者本人在附录 A1 里也明确"**本判定不回答**这批运行能否落在冻结件 §5 的声明上限之内"。同时 `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` 的 AC-16 卡仍记画布半为 `NOT_VERIFIED`。

   **处置口径**：要么补一份版本化的 ECC 修订，把"分载体判定"写进判据并说明触发事件，然后同步更新 AC-16 卡与 §7 矩阵；要么把 Founder 包 §13 那一行降回"直连链路 7/7 已判定；画布链路 7/7 已运行但其判据载体扩展尚未版本化"。**不要**在两处状态不一致的情况下把 ✅ 交给 Founder。

```text
END_MARKER
= M3-INDEPENDENT-CLOSEOUT-REVIEW-v1.0-END
```
