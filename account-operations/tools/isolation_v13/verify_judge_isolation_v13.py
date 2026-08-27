#!/usr/bin/env python3
"""机械核验第 7 轮全部独立判定者是否真的只读了被允许读的东西。

方法沿用第 3–6 轮：解析判定者**自己的执行记录**，只扫会造成文件访问的参数
（Read.file_path / Bash.command / Grep|Glob 的 pattern 与 path），
不扫 Write/Edit 的正文，也不扫 Bash heredoc 的载荷 ——
判定者在自己写的文件里提到某个文件名是"提及"，不是"读取"。
这两个形态各在第 3、4 轮造成过一次假阳性，都已修掉并留在这里作回归。

本轮与上一轮的两处差别：
  1. 盲评者除自己那个单元目录外，还要读**属于自己的那份冻结提示词文件**
     （prompts/unit_NN_jK.txt）—— 这是本轮把提示词落盘冻结带来的，
     必须进白名单，否则 36 名全部会被误判越界。
  2. 行为判定者有两份执行记录：第一次在写判定书时 API 连接中断，
     第二次重新做了一遍。**两份都扫**，不只扫成功那一份 ——
     只扫成功那份等于让中断掩盖越界。

**本核验能证明什么、不能证明什么**：它能证明判定者没有读过去盲文件；
它**不能**证明盲评有效 —— 第 4 轮的盲评正是被输出自身的结构指纹去盲的，
那条通道不需要读任何文件。指纹本身由 _leak_scan_v3.json 单独机械扫描。
"""
import json, os, re, sys

SESSION = "/tmp/claude-1000/-home-faye-diyu-demo/2c670698-40ad-483e-b793-56ac12fb6aea"
PROJ = "/home/faye/.claude/projects/-home-faye-diyu-demo/2c670698-40ad-483e-b793-56ac12fb6aea"
TASKS = os.path.join(SESSION, "tasks")
WF = os.path.join(PROJ, "subagents/workflows/wf_7f3bd855-29e")
BLIND_ROOT = os.path.join(SESSION, "scratchpad/m3-ab-blind-v4")
WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
OUT = os.path.join(WT, "account-operations/evidence/ep20-judge-isolation-v13/"
                       "judge_isolation_verification_v13.json")

HEREDOC_RE = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?.*?^\1", re.S | re.M)
# 只扫会造成文件访问的参数。作者性工具（Write / Edit / StructuredOutput）扫**文件名**、
# 不扫正文 —— 判定者在自己的判定书里提到某个文件名是"提及"，不是"读取"。
# StructuredOutput 是本轮新增的假阳性源：它整份载荷就是判定者自己写的判定内容，
# 其中一名的自检句「未执行 git 命令」被旧版当成了执行 git 的证据 —— 把否认读成了违规。
ACCESS_FIELDS = {"Read": ["file_path"], "Grep": ["pattern", "path", "glob"],
                 "Glob": ["pattern", "path"], "Bash": ["command"],
                 "Write": ["file_path"], "Edit": ["file_path"], "NotebookEdit": ["file_path"],
                 "StructuredOutput": []}
PATH_RE = re.compile(
    r"[\w./~-]*(?:m3-account-content-operator-v1|diyu-demo|account-operations|"
    r"M3_[A-Z0-9_]+|_SEALED[\w.]*|_arms_and_holdouts[\w.]*|SKILL\.md|collab-ledger)[\w./-]*")

REPO_FORBIDDEN = ["M3_CHECKPOINT_", "M3_ACCEPTANCE_CRITERIA_FROZEN", "M3_ECC_REBIND_",
                  "M3_ECC_MODULE_AB_", "M3_FOUNDER_", "M3_INDEPENDENT_CLOSEOUT_REVIEW",
                  "GATE_DEFECTS_", "_VERDICT_", "collab-ledger",
                  "account-operations/tools", "account-operations/tests",
                  "account-operations/fixtures",
                  "ep08-", "ep10-", "ep11-", "ep12-", "ep13-", "ep15-", "ep16-",
                  "ep19-", "ep20-",
                  "git log", "git show", "git diff", "git reflog"]
# 仓库标记必须打在**真实仓库根**上，不能打在子串上：
# 本会话目录名里就含 `-home-faye-diyu-demo`，判定者读自己的 tool-results 落盘文件
# （合法、且完全在仓库之外）会命中子串。这是本轮第二个假阳性源。
BLIND_FORBIDDEN = ["/home/faye/diyu-demo", "_SEALED", "_arms_and_holdouts",
                   "SKILL.md", "M3_", "git log", "git show", "git reflog",
                   "scratchpad/m3/", "ep08-module-ab"]


def strip_payload(name, text):
    return HEREDOC_RE.sub("<<HEREDOC_PAYLOAD_STRIPPED>>", text) if name == "Bash" else text


def tool_calls(path):
    if not os.path.exists(path):
        return None
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") != "assistant":
            continue
        for b in o.get("message", {}).get("content", []):
            if b.get("type") != "tool_use":
                continue
            inp = b.get("input", {}) or {}
            fields = ACCESS_FIELDS.get(b.get("name"), list(inp.keys()))
            out.append((b.get("name"), " ".join(str(inp.get(k, "")) for k in fields)))
    return out


def scan_repo_judge(path, verdict_file, allowed):
    calls = tool_calls(path)
    if calls is None:
        return {"transcript_found": False, "transcript": path}
    touched = set()
    for name, scanned in calls:
        touched.update(PATH_RE.findall(strip_payload(name, scanned)))
    outside = sorted(r for r in touched
                     if verdict_file not in r and not any(a in r for a in allowed))
    forbidden = sorted(r for r in outside if any(f in r for f in REPO_FORBIDDEN))
    return {"transcript_found": True, "transcript": os.path.basename(path),
            "tool_use_count": len(calls), "distinct_path_refs": len(touched),
            "refs_outside_allowlist": outside, "forbidden_hits": forbidden,
            "isolation_verdict": "CLEAN" if not forbidden else "VIOLATION"}


def scan_blind_judge(path, own_unit, own_prompt):
    """盲评者只许待在自己那个单元目录 + 自己那份提示词 + 仓库外的 rubric。"""
    calls = tool_calls(path)
    if calls is None:
        return {"transcript_found": False, "transcript": path}
    allowed_prefixes = [os.path.join(BLIND_ROOT, "units", own_unit),
                        os.path.join(BLIND_ROOT, "prompts", own_prompt),
                        os.path.join(BLIND_ROOT, "rubric.md")]
    hits, other_units = [], set()
    for name, scanned in calls:
        s2 = strip_payload(name, scanned)
        for p in allowed_prefixes:
            s2 = s2.replace(p, "<ALLOWED>")
        for m in re.finditer(r"unit_\d{2}", s2):
            if m.group(0) != own_unit:
                other_units.add(m.group(0))
        if BLIND_ROOT in s2:
            hits.append({"tool": name, "marker": "盲评包根目录", "arg_head": s2[:160]})
        for f in BLIND_FORBIDDEN:
            if f in s2:
                hits.append({"tool": name, "marker": f, "arg_head": s2[:160]})
    if other_units:
        hits.append({"tool": "-", "marker": "看了别的单元", "arg_head": ",".join(sorted(other_units))})
    return {"transcript_found": True, "transcript": os.path.basename(path),
            "tool_use_count": len(calls), "own_unit": own_unit,
            "forbidden_hits": hits,
            "isolation_verdict": "CLEAN" if not hits else "VIOLATION"}


def blind_own_unit(path):
    """从盲评者自己的记录里读出他被派到哪个单元 —— 不从别处推。"""
    calls = tool_calls(path) or []
    for name, scanned in calls:
        m = re.search(r"(unit_\d{2})_j(\d)\.txt", scanned)
        if m:
            return m.group(1), f"{m.group(1)}_j{m.group(2)}.txt"
    for name, scanned in calls:
        m = re.search(r"units/(unit_\d{2})", scanned)
        if m:
            return m.group(1), None
    return None, None


ECC = [
    {"name": "fidelity-v13", "transcript": "ae4d11f678b0086ac.output",
     "verdict_file": "M3_ECC_RUNTIME_FIDELITY_001_VERDICT_V13_v1.0.md",
     "allowed": ["ep06-runtime-fidelity-dify-v13", "M3_ECC_RUNTIME_FIDELITY_001_FROZEN",
                 "skills/operating-one-account", "m3-account-content-operator-semantic-v1.0"]},
    {"name": "behavior-002-v13-attempt1-interrupted", "transcript": "aa18e2e951d57cc42.output",
     "verdict_file": "M3_ECC_RUNTIME_BEHAVIOR_002_VERDICT_V13_v1.0.md",
     "allowed": ["ep06b-runtime-behavior-v13", "M3_ECC_RUNTIME_BEHAVIOR_002_FROZEN",
                 "_oracle/BEHAVIOR_CASES_v2.json", "evidence/_oracle",
                 "skills/operating-one-account", "m3-account-content-operator-semantic-v1.0"]},
    {"name": "behavior-002-v13", "transcript": "af1e4b170c74ad77f.output",
     "verdict_file": "M3_ECC_RUNTIME_BEHAVIOR_002_VERDICT_V13_v1.0.md",
     "allowed": ["ep06b-runtime-behavior-v13", "M3_ECC_RUNTIME_BEHAVIOR_002_FROZEN",
                 "_oracle/BEHAVIOR_CASES_v2.json", "evidence/_oracle",
                 "skills/operating-one-account", "m3-account-content-operator-semantic-v1.0"]},
    {"name": "longitudinal-v13", "transcript": "acd6bec767266a891.output",
     "verdict_file": "M3_ECC_LONGITUDINAL_001_VERDICT_V13_v1.0.md",
     "allowed": ["ep07-longitudinal-v13", "M3_ECC_LONGITUDINAL_001_FROZEN",
                 "skills/operating-one-account", "m3-account-content-operator-semantic-v1.0"]},
]


def main():
    report = {
        "round": "v1.3 / 第 7 轮",
        "method": __doc__.strip(),
        "repo_judge_forbidden_markers": REPO_FORBIDDEN,
        "blind_judge_forbidden_markers": BLIND_FORBIDDEN,
        "checker_false_positive_families_fixed": [
            "StructuredOutput 的整份载荷是判定者自己写的判定内容，被当成文件访问参数扫描 —— "
            "其中一名的自检句「未执行 git 命令」被读成执行了 git，把否认当成了违规",
            "仓库标记 `diyu-demo` 打在子串上，而本会话目录名 `-home-faye-diyu-demo` 天然含它 —— "
            "判定者读自己的 tool-results 落盘文件（在仓库之外、完全合法）会命中",
        ],
        "checker_note": "本核验器与前几轮一样，是被假阳性逐次打磨出来的。上面两类已写死为判据。"
                        "它**只能**证明判定者没读过禁读的东西，不能证明判定内容正确。",
        "blind_judge_note": "本核验只能证明盲评者没读过去盲文件；它**不能**证明盲评有效。"
                            "输出自身的结构指纹是另一条通道，由 _leak_scan_v3.json 单独机械扫描。",
        "judges": {},
    }
    for j in ECC:
        report["judges"][j["name"]] = scan_repo_judge(
            os.path.join(TASKS, j["transcript"]), j["verdict_file"], j["allowed"])

    for f in sorted(os.listdir(WF)):
        if not (f.startswith("agent-") and f.endswith(".jsonl")):
            continue
        p = os.path.join(WF, f)
        unit, prompt = blind_own_unit(p)
        if unit is None:
            report["judges"][f"ab-blind-UNKNOWN-{f[6:12]}"] = {
                "transcript_found": True, "transcript": f,
                "forbidden_hits": [{"tool": "-", "marker": "无法从记录判定所属单元",
                                    "arg_head": ""}],
                "isolation_verdict": "VIOLATION"}
            continue
        report["judges"][f"ab-blind-{unit}-{f[6:12]}"] = scan_blind_judge(
            p, unit, prompt or "")

    bad = [k for k, v in report["judges"].items() if v.get("isolation_verdict") != "CLEAN"]
    miss = [k for k, v in report["judges"].items() if not v.get("transcript_found")]
    report["summary"] = {"total": len(report["judges"]), "violations": bad,
                         "transcript_missing": miss}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for k, v in report["judges"].items():
        if v.get("isolation_verdict") != "CLEAN" or not v.get("transcript_found"):
            print(f"  {k:42s} {v.get('isolation_verdict')} hits={len(v.get('forbidden_hits', []))}")
    print(f"\n{len(report['judges'])} judges | violations={len(bad)} | missing={len(miss)}")
    print("written:", OUT)
    return 1 if (bad or miss) else 0


if __name__ == "__main__":
    sys.exit(main())
