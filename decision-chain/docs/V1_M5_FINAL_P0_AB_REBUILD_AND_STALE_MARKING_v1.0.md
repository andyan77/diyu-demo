# M5 A/B 受影响重建与旧包失效标记 v1.0

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 依据：冻结清单 `v1.1.4` 的 `ab_dependency_judgment`
  （`conclusion: AFFECTED_MUST_REBUILD`；`action:` 只重建受影响案例并出新 sealed mapping；
  旧包**原样保留并标 STALE / INVALID_FOR_FINAL_SCORING，不删除、不覆盖**）
- 候选：`5f84d94d…` / `M5_BIND=fp`

## 一、为什么必须重建

`AB-M3-01` 的 B 组直接调 M3_APP；`AB-FINAL-01` 的 B 组走完整链路，经过接缝与能力应用。
这三者本轮全部被替换为 fp successor，**评分文本因此受影响**。旧包评的是旧候选的文本，
拿它给新候选评分属于 A3 的失效面误用。

## 二、旧包：标失效，原样保留

| 文件 | sha256 | 本轮状态 |
|---|---|---|
| `AB_SUITE_RAW_abFRB3.json` | `2a37853c…f0e6598b` | `STALE` |
| `AB_BLIND_abFRB3.json` | `24ebaee8…2d99b7e174c` | `STALE / INVALID_FOR_FINAL_SCORING` |
| `AB_MAPPING_SEALED_abFRB3.json` | `546468f9…9f9457c7be` | `STALE`，**仍未打开** |

三份**均未删除、未覆盖、未移动**。它们对 RB3 候选继续是有效历史证据，只是不得用于本轮评分。

## 三、新包

| 文件 | sha256 | 字节 |
|---|---|---|
| `AB_SUITE_RAW_abFfp1.json` | `3ce9d7a1…5ab82ab12` | 53866 |
| `AB_BLIND_abFfp1.json` | `020f0c5e…95d2c17` | 50276 |
| `AB_MAPPING_SEALED_abFfp1.json` | `d55c43ab…79050e56` | 224 |

两个案例各两组，盲评包以 `甲` / `乙` 匿名：

```
AB-M3-01       A=4199字  B=1944字
AB-FINAL-01    A=5551字  B=8066字
```

**新映射同样封存，本轮未打开，评分完成前不得打开。**

## 四、必须披露的两件事

### 4.1 盲评在本仓库内不成立——盲评包必须隔离交付

`AB_SUITE_RAW_abFfp1.json` 里带着**显式的 `A` / `B` 键**，正文与盲评包 `甲` / `乙` 相同，
两份文件同目录并存。**任何拿到本仓库的人都可以用正文比对或字数比对还原映射**，
封存的 mapping 因此保护不了什么。

这不是本轮引入的：同一个 `DIYU_M5_AB_SUITE_v1.0.py` 在此前每一轮都这样产出。
本轮不改该脚本——它不在本次冻结的 N1／N2／N3 修改面内，改它属于扩面。

**对 `M5-AC-05` / `M5-AC-06` 的实际要求**：盲评包必须**脱离本仓库**单独交给独立评审人；
评审人不得同时拿到 RAW 文件或本仓库读权限。否则该盲评无效，不因为"有一个封存文件"而成立。

### 4.2 执行侧已对 `AB-M3-01` 丧失盲评资格

运行器把 A／B 的字数打进了控制台日志（`A=4199字 B=1944字`），
而盲评包里 `甲=1944` / `乙=4199`。**执行侧因此已经知道 `AB-M3-01` 的映射。**

这不影响判定，因为 `AC-05` / `AC-06` 本来就是 `human_only`、执行侧无权评分；
但按"实现者知道映射的评分无效"这条，必须记下来：
**执行侧对本案例的任何评分意见一律无效**，本文件不给任何 A/B 优劣判断。

## 五、结论

- 受影响案例已按冻结清单重建，新 sealed mapping 已生成且未打开；
- 旧包三份标 `STALE / INVALID_FOR_FINAL_SCORING`，原样保留；
- `M5-AC-05` / `M5-AC-06` 维持 `NOT_VERIFIED`，等待**隔离交付**的独立人类盲评。
