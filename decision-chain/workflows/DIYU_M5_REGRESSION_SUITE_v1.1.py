#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 不退化与受影响回归 · REG-M1/M2/M3/M4/SKILLS。

判据：**不退化**。每一条都跑既有的、模块自己带来的测试，不另造一套判据——
另造一套等于换判据，换判据就不是回归了。

REG-SKILLS-01 的判据特别写清楚：合同要的是「六份专业 Skill 的任务适用专业价值，
**不要求六份全部调用**」。因此这一条既要证「用到的那几份确实产生了专业价值」，
也要证「没用到的那几份是合法跳过、且跳过被如实登记」——两头都要，只证一头是漏判。

v1.1 相对 v1.0：**只修参数解析与退出码，判定逻辑一行未动。**
v1.0 在 RB2 正式运行中跑出 0/0 PASS，原因是命令行过滤写成「丢掉所有 -- 开头的」，
于是 --full-story 的**路径值**留了下来被当成用例过滤器，一个用例都没匹配上。
按 A2「判据在看到结果后改必须版本化」，v1.0 原样保留不动，修复出这一版。
本文件与 v1.0 的差异必须为零行触及 def reg_* / verdict / fails.append。
"""
import glob, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")


def run(cmd, cwd=ROOT, timeout=900, in_container=None):
    if in_container:
        cmd = ["docker", "exec", "-i", in_container, "sh", "-lc", cmd]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    else:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, shell=isinstance(cmd, str))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def reg_m1():
    rc, out = run(["python3", "decision-chain/workflows/test_m1_context_compiler_v0.1.py"])
    m = re.search(r"Ran (\d+) tests", out)
    ok = "OK" in out and rc == 0
    return {"verdict": "PASS" if ok else "FAIL", "tests": int(m.group(1)) if m else 0,
            "target": "自然语言理解、任务上下文、用户可选择与不强迫术语",
            "source": "decision-chain/workflows/test_m1_context_compiler_v0.1.py",
            "tail": out.strip().splitlines()[-3:]}


def reg_m2():
    # 在**候选镜像内**跑 M2 自己的测试。跑在别处不算数——回归要回归的是候选。
    rc, out = run("cd /srv/app && python3 -m pytest tests -q", in_container="diyu-m2-app")
    m = re.search(r"(\d+) passed", out)
    fail = re.search(r"(\d+) failed", out)
    return {"verdict": "PASS" if (rc == 0 and m and not fail) else "FAIL",
            "passed": int(m.group(1)) if m else 0,
            "failed": int(fail.group(1)) if fail else 0,
            "target": "最小投影、版本、幂等反馈和当前状态；保留历史 waiver 的真实身份",
            "ran_inside_candidate_image": "diyu-m2-app:m5-candidate",
            "tail": out.strip().splitlines()[-2:]}


def reg_m3():
    files = sorted(glob.glob(os.path.join(ROOT, "account-operations", "tests", "test_*.py")))
    detail = {}
    ok_all = True
    for f in files:
        rc, out = run(["python3", f], timeout=400)
        m = re.search(r"Ran (\d+) tests", out)
        m2 = re.search(r"(\d+) passed, (\d+) failed", out)
        bad = ("FAILED" in out or "Traceback" in out or rc != 0)
        detail[os.path.basename(f)] = {
            "rc": rc, "unittest_ran": int(m.group(1)) if m else None,
            "passed": int(m2.group(1)) if m2 else None,
            "failed": int(m2.group(2)) if m2 else None,
            "ok": not bad}
        ok_all = ok_all and not bad
    return {"verdict": "PASS" if ok_all else "FAIL",
            "target": "运营判断职责、阶段/组合/产能/实验/反馈与可用 Brief",
            "files": detail}


def reg_m4():
    ev = os.path.join(ROOT, "decision-chain", "evidence", "m4", "rebase_ac31")
    gates = sorted(glob.glob(os.path.join(ev, "*")))
    env = dict(os.environ)
    env["DIYU_M4_DIFY_ENV"] = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
    p = subprocess.run(["python3", "decision-chain/workflows/DIYU_M4_AC31_REGRESSION_v0.1.py", "run"],
                       cwd=ROOT, capture_output=True, text=True, timeout=1800, env=env)
    out = (p.stdout or "") + (p.stderr or "")
    hits = re.findall(r"\[RB31-G(\d+)\].*?(succeeded|failed)", out)
    ok = bool(hits) and all(h[1] == "succeeded" for h in hits)
    return {"verdict": "PASS" if ok else "FAIL",
            "target": "非固定入口、局部 Return、PRE/MIXED/FINAL、条件附件、业务结果与平台状态分离",
            "gates": ["G%s:%s" % h for h in hits],
            "evidence_dir": "decision-chain/evidence/m4/rebase_ac31",
            "note": "走真实 Dify，用的是 M4 已发布的那八个应用，未做任何改动"}


# 六个能力各自加载**两份**：原专业 Skill（v0.1 系列）+ M4 后继补充（_M4）。
# 校验对象以**运行时实际加载的**为准，不以我以为的为准——这份清单是从真实运行的
# binding_json 里 source_skill_path / successor_skill_path 读出来的。
SKILL_FILES = [
    "decision-chain/skills/Matrix_Architect_v0.1.2.md",
    "decision-chain/skills/Matrix_Architect_v0.2_M4.md",
    "decision-chain/skills/Campaign_Orchestrator_v0.1.md",
    "decision-chain/skills/Campaign_Orchestrator_v0.2_M4.md",
    "decision-chain/skills/Content_Brief_Architect_v0.1.md",
    "decision-chain/skills/Content_Brief_Architect_v0.2_M4.md",
    "content-production/skills/writing-creative-scripts/SKILL.md",
    "content-production/skills/writing-creative-scripts-m4/SKILL.md",
    "content-production/skills/directing-content-production/SKILL.md",
    "content-production/skills/directing-content-production-m4/SKILL.md",
    "content-production/skills/packaging-content-for-release/SKILL.md",
    "content-production/skills/packaging-content-for-release-m4/SKILL.md",
]


def runtime_skill_hashes(since="2026-08-28 00:00"):
    """把**运行中的应用自报的** Skill 哈希收上来。

    这比 git diff 强一档：git diff 只能证明「候选树里的文件没变」，
    而这个能证明「跑起来的应用读的就是候选树里那一份，且字节一致」。
    两者对不上，说明应用读的不是这棵树——那才是真正要抓的情况。
    """
    q = ("SELECT DISTINCT outputs::jsonb->>'binding_json' FROM workflow_runs "
         "WHERE status='succeeded' AND created_at > '%s' "
         "AND outputs::jsonb ? 'binding_json';" % since)
    rc, out = run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                   "-d", "dify", "-t", "-A", "-c", q], timeout=120)
    seen = {}
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            b = json.loads(line)
        except Exception:
            continue
        for pk, hk in (("source_skill_path", "source_skill_sha256"),
                       ("successor_skill_path", "successor_skill_sha256")):
            if b.get(pk):
                seen[b[pk]] = b.get(hk)
    return seen


def reg_skills():
    """两头都要证：用到的那几份产生了专业价值；没用到的是合法跳过且如实登记。"""
    out = {"target": "六份专业 Skill 的任务适用专业价值，不要求六份全部调用"}

    # (a) 六份源文件相对 main 零改动
    rc, d = run(["git", "diff", "--name-status", "main", "--diff-filter=MD", "--"] + SKILL_FILES)
    out["skill_sources_modified_or_deleted_vs_main"] = d.strip() or "（空：零修改零删除）"
    out["sources_untouched"] = not d.strip()
    out["skill_sha256_on_disk"] = {}
    missing_files = []
    for f in SKILL_FILES:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            rc2, h = run(["sha256sum", p])
            out["skill_sha256_on_disk"][f] = h.split()[0]
        else:
            missing_files.append(f)
    out["skill_files_missing"] = missing_files

    # (a2) 运行时自报哈希 vs 候选树里文件哈希，逐条比对
    rt_hashes = runtime_skill_hashes()
    cmp_rows, mismatched, unseen = {}, [], []
    for f, disk in out["skill_sha256_on_disk"].items():
        got = rt_hashes.get(f)
        cmp_rows[f] = {"on_disk": disk[:16], "runtime_reported": (got or "")[:16],
                       "match": (got == disk) if got else None}
        if got and got != disk:
            mismatched.append(f)
        if not got:
            unseen.append(f)
    out["runtime_vs_disk"] = cmp_rows
    out["runtime_hash_mismatch"] = mismatched
    out["not_observed_in_any_run"] = unseen

    # (b) 从**显式指定**的那一次完整主故事里取「用到的」与「合法跳过的」。
    # 以前这里是 sorted(glob(...))[-1]：正式产物叫 full01F1，大写排在小写前面，
    # 于是永远取到 full01i 这种冻结前的诊断跑。改成只认 --full-story / 环境变量。
    src = _full_story_path()
    used, skipped, skip_reasons = [], [], []
    if src:
        runs = [src]
        D = json.load(open(src, encoding="utf-8"))
        d0 = D.get("full01") or {}
        used = [s["step"].split(":", 1)[1] for s in d0.get("steps", [])
                if s.get("step", "").startswith(("seam:", "reentry_seam:")) and s.get("delivered")]
        skipped = [x["capability"] for x in d0.get("skipped", [])]
        skip_reasons = [x.get("reason") for x in d0.get("skipped", [])]
        out["source_run"] = os.path.basename(runs[-1])
    out["capabilities_delivered"] = used
    out["capabilities_legally_skipped"] = skipped
    out["skip_reasons_recorded"] = skip_reasons
    out["not_all_six_forced"] = len(used) < 6
    out["skips_are_declared"] = bool(skipped) and all(bool(r) for r in skip_reasons)

    fails = []
    if not out["sources_untouched"]:
        fails.append("Skill 源文件相对 main 出现修改或删除")
    if out.get("skill_files_missing"):
        fails.append("清单里的 Skill 文件在候选树里不存在：%s" % out["skill_files_missing"])
    if out.get("runtime_hash_mismatch"):
        fails.append("运行中的应用自报的 Skill 哈希与候选树里的文件不一致：%s"
                     % out["runtime_hash_mismatch"])
    if not used:
        fails.append("没有任何能力真正交付，无法证明专业价值")
    if not out["not_all_six_forced"]:
        fails.append("六份被强制全调用，与「不要求六份全部调用」相悖")
    if skipped and not out["skips_are_declared"]:
        fails.append("存在未登记理由的跳过")
    out["failures"] = fails
    out["verdict"] = "PASS" if not fails else "FAIL"
    return out


def _full_story_path():
    """完整主故事证据的路径。必须显式给：--full-story <path> 或环境变量
    M5_FULL_STORY_PATH。给不出就返回 None 并让相关判据显式落空，**不猜**。"""
    for i, a in enumerate(sys.argv):
        if a == "--full-story" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith("--full-story="):
            return a.split("=", 1)[1]
    return os.environ.get("M5_FULL_STORY_PATH")


def main():
    # 只吃**位置参数**。上一版写成「丢掉所有 -- 开头的」，于是 --full-story 的
    # 那个路径值留了下来被当成用例过滤器，结果一个用例都没匹配上，跑出 0/0 PASS。
    # 0/0 不是通过，是什么都没跑。
    FLAGS_WITH_VALUE = ("--full-story",)
    argv, skip = [], False
    for a in sys.argv[1:]:
        if skip:
            skip = False
            continue
        if a in FLAGS_WITH_VALUE:
            skip = True
            continue
        if a.startswith("--"):
            continue
        argv.append(a)
    only = set((argv[0] if argv else "").split(",")) - {""}
    todo = [("REG-M1-01", reg_m1), ("REG-M2-01", reg_m2), ("REG-M3-01", reg_m3),
            ("REG-M4-01", reg_m4), ("REG-SKILLS-01", reg_skills)]
    # 输出带标签且**不合并历史**。以前是读旧文件再覆盖写回：跑一次子集，
    # 旧的条目原样留在结果里，看起来像本轮全跑过。那是把过期结论算进当前证据。
    tag = os.environ.get("REGRESSION_TAG") or "adhoc"
    res = {}
    existing = os.path.join(EV, "REGRESSION_RESULTS_%s.json" % tag)
    for cid, fn in todo:
        if only and cid not in only:
            continue
        print("\n>>> %s" % cid, flush=True)
        try:
            r = fn()
        except Exception as e:
            import traceback; traceback.print_exc()
            r = {"verdict": "FAIL", "exception": "%s: %s" % (type(e).__name__, e)}
        r["source"] = r.get("source") or "DIYU_M5_REGRESSION_SUITE_v1.0.py"
        res[cid] = r
        print("    %s  %s" % (r["verdict"],
                              json.dumps({k: v for k, v in r.items()
                                          if k in ("tests", "passed", "failed", "gates",
                                                   "capabilities_delivered",
                                                   "capabilities_legally_skipped")},
                                         ensure_ascii=False)[:220]), flush=True)
    with open(existing, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("SAVED", existing)
    if not res:
        # 0/0 不是通过，是什么都没跑。必须以非零退出，否则正式运行器
        # 会把「没跑」记成「跑过且没有失败」。
        print("\n=== 回归 0/0 —— 一个用例都没跑，这不是通过 ===")
        return 2
    npass = sum(1 for v in res.values() if v.get("verdict") == "PASS")
    print("\n=== 回归 %d/%d PASS ===" % (npass, len(res)))
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    # 上一版是裸 main()，返回值被丢掉，退出码永远是 0——
    # 上面那个 0/0 守卫等于没装。
    sys.exit(main())
