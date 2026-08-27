#!/usr/bin/env python3
"""AC-16 缺口一：系统提示词**全文**进证据，并与仓库里那份逐字节绑死。

第 2–7 轮一直只有「SKILL.md 的 sha256 == 冻结记录」这一句。它证明的是仓库里那份没被改，
**没有**证明 Dify 里跑的就是它——中间隔着一次部署，而部署脚本是执行侧自己写的。
这里改成从**已发布**的工作流里把系统提示词整段读回来，落盘全文，然后做三件比对：

  1. 读回来的系统提示词 == `SKILL.md` 全文 + 图里那一行参考文件占位符，逐字节；
  2. `SKILL.md` 的工作区哈希 == `git show HEAD` 里那一份（部署的和提交的是同一份）；
  3. 已发布版本名与图哈希落盘，作为其余证据的绑定锚。

读的是 publish 端点，不是 draft——draft 是我刚写进去的，拿它自证等于没证。
"""
import hashlib
import json
import os
import subprocess
import sys

SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRATCH)
from dify_client import Console, read, WORKTREE   # noqa: E402

APP = "b7fb5b1a-9278-426c-bb8a-f9f288639548"
SKILL_PATH = os.path.join(WORKTREE, "account-operations/skills/operating-one-account/SKILL.md")
OUT = os.path.join(WORKTREE, "account-operations/evidence/ep24-ac16-canvas-and-prompt")


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def main():
    c = Console()
    os.makedirs(OUT, exist_ok=True)

    st, pub = c.call("GET", f"/console/api/apps/{APP}/workflows/publish")
    assert st == 200, (st, pub)
    graph = pub["graph"]
    llm = [n for n in graph["nodes"]
           if n["data"].get("type") == "llm" and n["id"] == "operating_one_account_llm"][0]
    sys_msgs = [m for m in llm["data"]["prompt_template"] if m["role"] == "system"]
    assert len(sys_msgs) == 1, f"系统提示词不是恰好一条：{len(sys_msgs)}"
    live = sys_msgs[0]["text"]

    with open(os.path.join(OUT, "published_system_prompt_full.txt"), "w", encoding="utf-8") as f:
        f.write(live)

    skill_disk = read(SKILL_PATH)
    expected = skill_disk + "\n\n---\n{{#start.loaded_references#}}"
    git_skill = subprocess.run(
        ["git", "-C", WORKTREE, "show",
         "HEAD:account-operations/skills/operating-one-account/SKILL.md"],
        capture_output=True, text=True).stdout

    st, vers = c.call("GET", f"/console/api/apps/{APP}/workflows?page=1&limit=10")
    versions = [{"version": v.get("version"), "marked_name": v.get("marked_name"),
                 "created_at": v.get("created_at")} for v in (vers.get("items") or [])] \
        if st == 200 else [{"error": st}]

    rep = {
        "what": "AC-16 缺口一 · 系统提示词全文绑定证据",
        "read_from": f"GET /console/api/apps/{APP}/workflows/publish（已发布，不是草稿）",
        "app_id": APP,
        "published_graph_hash": pub.get("hash"),
        "published_version": pub.get("version"),
        "published_versions_seen": versions,
        "system_prompt": {
            "chars": len(live), "sha256": sha(live),
            "saved_to": "published_system_prompt_full.txt（全文，未截断）",
            "first_120": live[:120], "last_120": live[-120:],
        },
        "checks": {
            "线上系统提示词 == SKILL.md 全文 + 参考占位符（逐字节）": live == expected,
            "SKILL.md 工作区哈希": sha(skill_disk),
            "SKILL.md git HEAD 哈希": sha(git_skill) if git_skill else "（尚未提交）",
            "工作区与 git HEAD 一致": bool(git_skill) and sha(skill_disk) == sha(git_skill),
            "系统提示词恰好一条": len(sys_msgs) == 1,
            "占位符尾巴逐字对上": live.endswith("\n\n---\n{{#start.loaded_references#}}"),
        },
        "note": "「工作区与 git HEAD 一致」在本次提交之前必然为 false —— 提交后由 "
                "recheck_after_commit.sh 零参数重跑一次，结果一并落盘。",
    }
    with open(os.path.join(OUT, "SYSTEM_PROMPT_BINDING.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: rep[k] for k in ("published_graph_hash", "published_versions_seen",
                                          "system_prompt", "checks")},
                     ensure_ascii=False, indent=2))
    return 0 if rep["checks"]["线上系统提示词 == SKILL.md 全文 + 参考占位符（逐字节）"] else 1


if __name__ == "__main__":
    sys.exit(main())
