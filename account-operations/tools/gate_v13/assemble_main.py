import re

from shared_checks import render_body  # noqa: F401


def main(body: str, fixed: str, needs_fix: str, gate_status: str,
         draft_audit: str) -> dict:
    """确定性选稿。

    v1.1 已经把"闸门没发现问题就逐字返回原稿"从'让模型照抄'改成'由代码返回'。
    v1.2 再加一条：**硬失败绝不进补齐**——补齐节点的职责是补锚点、去泄漏、说清处置，
    不是无中生有写交付物。G6 那次就是补齐节点写了一句话，复检据此宣布"缺口已闭合"。
    """
    b = body or ""
    raw_fixed = fixed or ""
    m = re.search(r"<<AUDIT>>(.*?)<<END_AUDIT>>", raw_fixed, flags=re.S)
    fixed_audit = m.group(1) if m else ""
    f = re.sub(r"<think>.*?</think>", "", raw_fixed, flags=re.S)
    f = re.sub(r"<<AUDIT>>.*?<<END_AUDIT>>", "", f, flags=re.S)
    f = re.sub(r"<<AUDIT>>.*$", "", f, flags=re.S).strip()

    if str(gate_status or "").startswith("HARD_FAIL"):
        return {"final_text": b, "final_audit": draft_audit or "",
                "path": "hard_fail_no_repair"}
    if needs_fix != "yes" or f == "" or f.strip() == "NO_CHANGE":
        return {"final_text": b, "final_audit": draft_audit or "",
                "path": "draft_verbatim"}
    # 补齐改了正文，配套的审计块必须由补齐节点重发；没重发就交空串，
    # 复检会据此判 audit_missing_after_repair，不会拿旧引用去对新正文（那会误伤）。
    f, _, _ = render_body(f)
    return {"final_text": f, "final_audit": fixed_audit, "path": "gate_repaired"}
