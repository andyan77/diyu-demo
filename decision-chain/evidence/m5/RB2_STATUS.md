# RB2 正式运行产物的效力 —— EXPLORATORY

`*_FRB2.json` / `*_abFRB2.json` / `FULL_STORY_RUN_full01FR.json` /
`FORMAL_EVIDENCE_MANIFEST_RB2.json` / `FORMAL_RUN_LOG_RB2.json`
是在 Candidate Run Manifest **v1.1.2** 上跑出来的。

这批产物**只读留存，不作为正式验收证据**，理由是判据在看到它们之后被修改了：

- `DIYU_M5_REGRESSION_SUITE_v1.0.py` 跑出 0/0 并被当成通过（返回码还被丢弃）；
- `DIYU_M5_BUILD_BLIND_PACKAGE_v1.0.py` 尾部 NameError。

按 A2「判据在看到结果后才定或改，本次运行只算探索」，这两份 v1.0 原样保留、
不再被正式运行调用，修复版另出 v1.1，清单重新冻结为 v1.1.3，正式结论改由
**RB3** 整轮重跑产生。

**候选运行时在 v1.1.2 → v1.1.3 之间零改动**（`git diff` 对 CANDIDATE_RUNTIME
路径集为空）。因此 RB2 的观察在技术上仍然可信，只是不占正式判据位；
它们的价值是诊断，不是验收。

不删除、不覆盖：这批文件连同它们暴露的三个脚手架缺陷一起留在账上。
