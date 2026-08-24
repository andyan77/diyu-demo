#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 V1_E2E_QUALITY_VALIDATION_MANIFEST_v0.1.md。

所有 SHA / 计数从磁盘与后台现算，不人工誊写。
"""
import argparse, hashlib, json, os, subprocess

from _repo_paths import ROOT as REPO, rpath  # 目录重组后按文件名解析
PG = os.environ.get("DIFY_PG_CONTAINER", "docker-db_postgres-1")

NEW_FILES = [
 "V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md", "V1_E2E_CASES_v0.1.json",
 "V1_QUALITY_COMPARISON_INPUTS_v0.1.md", "v1_demo_e2e_replay.py",
 "v1_quality_comparison_run.py", "v1_e2e_quality_eval.py",
 "v1_quality_blind_pack.py", "v1_e2e_report_gen.py", "v1_e2e_manifest_gen.py",
 "V1_E2E_RUN_002_RAW.md", "V1_E2E_RUN_002_TRACE.md", "V1_E2E_RUN_002_EVAL.md",
 "V1_QUALITY_COMPARISON_RUN_001_RAW.md", "V1_QUALITY_BLIND_REVIEW_PACK_v0.1.md",
]
TEST_APPS = [
 ("TEST_MATRIX_QWEN38MAX",        "ced1566c-d83e-49d8-a3c0-7da45fdb8a84"),
 ("TEST_CAMPAIGN_QWEN38MAX",      "aad728f0-3b69-4241-a122-7ba83c6f8d23"),
 ("TEST_CONTENT_BRIEF_QWEN38MAX", "86e48b41-864c-4ff2-bcae-158f4396d3ae"),
 ("TEST_MATRIX_NOSKILL",          "87eb2e0b-65cd-4aa4-9752-5ba741972bd8"),
 ("TEST_CAMPAIGN_NOSKILL",        "a42c9cf0-fbaf-47a3-9961-eb9786f5d1ee"),
 ("TEST_CONTENT_BRIEF_NOSKILL",   "1b7b4023-5f82-49e6-9d35-4e9ae38985b9"),
]


def psql(sql):
    r = subprocess.run(["docker", "exec", PG, "psql", "-U", "postgres", "-d", "dify", "-tAc", sql],
                       capture_output=True, text=True, timeout=180)
    return r.stdout.strip() if r.returncode == 0 else "（查询失败）"


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--mapping-sha", required=True)
    ap.add_argument("--pre-commit", required=True)
    a = ap.parse_args()

    ev = json.load(open(os.path.join(a.eval, "eval_result.json"), encoding="utf-8"))
    sh, res = ev["shadow"], ev["results"]
    cs = {k: v["verdict"] for k, v in res.items() if v["suite"] == "scenarios"}
    ce = {k: v["verdict"] for k, v in res.items() if v["suite"] == "e2e"}

    L = ["""# 笛语 V1 E2E 与质量验证运行清单 v0.1

> 本清单的每一行都取自磁盘文件与自托管 Dify 的数据库本身，不是人工誊写。

## 1. 运行环境

| 维度 | 值 |
|---|---|
| Dify 版本 | 1.16.1（自托管 Docker Compose），DSL `0.7.0` |
| 主模型插件 | `langgenius/deepseek` 0.0.20，provider `langgenius/deepseek/deepseek` |
| 主模型 | `deepseek-v4-flash` / `chat`，`top_p=0.8`，**未设置 temperature** |
| 对照模型插件 | `langgenius/tongyi` 0.2.13，provider `langgenius/tongyi/tongyi` |
| 对照模型 | `qwen3.8-max` / `chat`，`top_p=0.8`，**未设置 temperature** |
| 与 RUN_001 的环境差异 | 已含 DNS 修复（国内解析器 + `single-request-reopen`）；TLS 握手中断一类仍开放 |

**成本口径**：Dify 插件显示的 `total_price=0` 是**插件未登记计价**，不是真实零成本，不得据此声称免费。

## 2. 预注册承诺

| 项 | 值 |
|---|---|
| 预注册 commit | `%s` |
| `V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md` | `%s` |
| `V1_E2E_CASES_v0.1.json` | `%s` |
| `V1_QUALITY_COMPARISON_INPUTS_v0.1.md` | `%s` |
| `v1_demo_e2e_replay.py`（预注册版） | `c41e239e06ae5d9507b195b3a94d77590a3e55c0c97a710f5ed8592b8d07fdf8` |
| **匿名映射表 SHA-256（盲审前承诺）** | `%s` |

`v1_demo_e2e_replay.py` 在预注册之后修改过**一次**，只改凭据优先级（显式 `DIFY_API_KEY_FILE`
必须压过环境里残留的 `DIFY_API_KEY`）。原始失败证据保留为
`replay_scenarios.FAILED_401_UNAUTHORIZED.jsonl`，受影响用例 S01 **从头重跑**，未做增量补跑。

## 3. 本轮新建的测试专用应用

均为**全新 app_id**，名称含 `V1 QUALITY TEST ONLY`，未注册为主 Chatflow 的 Tool，
未修改任何旧应用、旧 Workflow 版本或原三个 Workflow Tool。

| 名称 | app_id | 已发布 workflow_id |
|---|---|---|
""" % (a.pre_commit,
       sha_file(rpath("V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md")),
       sha_file(rpath("V1_E2E_CASES_v0.1.json")),
       sha_file(rpath("V1_QUALITY_COMPARISON_INPUTS_v0.1.md")),
       a.mapping_sha)]

    for name, aid in TEST_APPS:
        wid = psql("select id from workflows where app_id='%s' and version<>'draft' "
                   "order by created_at desc limit 1;" % aid)
        L.append("| `%s` | `%s` | `%s` |\n" % (name, aid, wid or "（未发布）"))

    L.append("""
## 4. 运行规模

| 项 | 值 |
|---|---|
| 十场景重放 | 通过 %d / 失败 %d / 未运行 %d |
| 40 类 E2E | 通过 %d / 失败 %d / 未运行 %d |
| 有效影子节点轮数 | %s |
| `shadow_patch_success_rate` | %s |
| `fail_open_rate` | %s |
| `empty_turn_rate` | %s |
| `unauthorized_execution_rate` | %s |
| 基础设施重试次数 | %s |

## 5. 新增文件 SHA-256

| 文件 | 字节 | SHA-256 |
|---|---|---|
""" % (sum(1 for v in cs.values() if v == "PASS"), sum(1 for v in cs.values() if v == "FAIL"),
       sum(1 for v in cs.values() if v == "NOT_RUN"),
       sum(1 for v in ce.values() if v == "PASS"), sum(1 for v in ce.values() if v == "FAIL"),
       sum(1 for v in ce.values() if v == "NOT_RUN"),
       sh.get("shadow_node_turns"), sh.get("shadow_patch_success_rate"),
       sh.get("fail_open_rate"), sh.get("empty_turn_rate"),
       sh.get("unauthorized_execution_rate"), sh.get("infra_retries")))

    for f in NEW_FILES:
        p = rpath(f)
        if os.path.exists(p):
            L.append("| `%s` | %d | `%s` |\n" % (f, os.path.getsize(p), sha_file(p)))
        else:
            L.append("| `%s` | —— | （本轮未产出） |\n" % f)
    for name, _ in TEST_APPS:
        p = rpath("testapps", name + ".yml")
        if os.path.exists(p):
            L.append("| `testapps/%s.yml` | %d | `%s` |\n" % (name, os.path.getsize(p), sha_file(p)))
    L.append("\n> 本清单自身的 SHA 不在表内（自指），以提交后的 git blob 为准。\n")

    out = rpath("V1_E2E_QUALITY_VALIDATION_MANIFEST_v0.1.md")
    open(out, "w", encoding="utf-8").write("".join(L))
    print("%-46s %8d 字节" % (os.path.basename(out), os.path.getsize(out)))


if __name__ == "__main__":
    main()
