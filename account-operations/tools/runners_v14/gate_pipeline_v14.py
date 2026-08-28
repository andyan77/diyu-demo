"""A/B 的 B 臂用的直连镜像（载体 v1.4）。

它**导入部署进 Dify 图的同一份源文件**（`shared_checks.py` + 三个 `*_main.py` +
`update_m3_app_v14.FINALIZE_SYS`），所以"镜像等于产品"是由同一性证明的，不是靠声明。

B 臂为什么需要它：SKILL.md v1.4 让模型在正文之后输出一段 `<<AUDIT>>` 审计块。
在 Dify 载体里这段由闸门剥掉。没有镜像，B 臂的盲评稿会带着一段别的臂都没有的审计块——
既不是产品的真实形态，又当场把盲评拆穿。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
# 三个 *_main.py 与 shared_checks.py 的唯一真源是仓库里的 gate_v13/，
# 与部署进 Dify 图的**同一份文件**——"镜像等于产品"由同一性证明，不靠声明。
sys.path.insert(0, os.path.join(WORKTREE, "account-operations/tools/gate_v13"))
sys.path.insert(0, HERE)
from gate_main import main as gate_main                 # noqa: E402
from assemble_main import main as assemble_main         # noqa: E402
from post_gate_main import main as post_gate_main       # noqa: E402
from update_m3_app_v14 import FINALIZE_SYS              # noqa: E402


def repair_user_message(gate_report, needs_fix, gate_status, body, draft_audit):
    """与 Dify gate_repair_llm 的 user 模板同内容，变量已解析。"""
    return (f"<gate_report>\nneeds_fix = {needs_fix}\ngate_status = {gate_status}\n"
            f"{gate_report}\n</gate_report>\n\n<draft>\n{body}\n</draft>\n\n"
            f"<draft_audit>\n{draft_audit}\n</draft_audit>")


def _text(res):
    b = res["body"]
    ch = (b.get("choices") or [{}])[0] if isinstance(b, dict) else {}
    return (ch.get("message", {}) or {}).get("content", "") if isinstance(ch, dict) else ""


def run_gated(call_fn, key, system_prompt, user_message, manifest, account_context):
    draft_res = call_fn(key, system_prompt, user_message)
    draft_text = _text(draft_res)

    g = gate_main(draft_text, manifest, account_context)
    trace = {"gate_report": g["gate_report"], "needs_fix": g["needs_fix"],
             "gate_status": g["gate_status"], "draft_raw": draft_text,
             "repair_called": False, "repair_raw": ""}

    fixed_text, repair_res = "", None
    if g["needs_fix"] == "yes":
        repair_res = call_fn(key, FINALIZE_SYS,
                             repair_user_message(g["gate_report"], g["needs_fix"],
                                                 g["gate_status"], g["body"], g["draft_audit"]))
        fixed_text = _text(repair_res)
        trace["repair_called"] = True
        trace["repair_raw"] = fixed_text

    a = assemble_main(g["body"], fixed_text, g["needs_fix"], g["gate_status"], g["draft_audit"])
    pg = post_gate_main(a["final_text"], manifest, g["gate_report"],
                        account_context, a["final_audit"], a["path"])
    trace["gate_path"] = a["path"]
    trace["post_gate_report"] = pg["post_gate_report"]
    trace["gaps_closed"] = pg["gaps_closed"]
    trace["cycle_state_carry"] = pg["cycle_state_carry"]
    return pg["operating_judgment_final"], trace, draft_res, repair_res
