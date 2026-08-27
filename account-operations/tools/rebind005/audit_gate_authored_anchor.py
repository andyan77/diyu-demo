#!/usr/bin/env python3
"""D-3 的残留缺口：**同一个 id 的锚点句**被补齐节点写出来。

`D-3` 的修法按 **id** 剥离补齐节点代写的 `POS` 行。它挡得住「凭空多出一位」，
挡不住另一条更细的路：补齐节点保留原来的 id，却把 `::` 右边那句锚点改写成
**它自己刚写进正文的一句话**。id 没变，剥离逻辑就放行了。

为什么不在本批次里把它做进闸门：那要改 `post_gate` 的输入（需要草稿正文），
等于改代码 → 重新部署 → 整批重跑。Founder 第 9 段只授权一个正式取证批次。
所以这一条**在闸门之外离线计量**，结果如实进证据：发生了几次、在哪几例。

判法（只用已落盘字段，不需要改任何节点）：
  对 `gate_path == "gate_repaired"` 的每一次运行，
  取最终复检认下的每个 `POS` id，回到 `draft_raw` 找同 id 的那一行，
  看它的锚点是否**逐字出现在草稿正文里**。
    在   ⇒ 这句话是模型写的，补齐只是搬运
    不在 ⇒ 锚点句在草稿里不存在，却在最终里成立 ⇒ 补齐节点写的，记一笔
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
import shared_checks as sc                                              # noqa: E402


def audit(dirs):
    rows, repaired, suspect = [], 0, []
    for pat in dirs:
        for p in sorted(glob.glob(os.path.join(WT, pat))):
            if "/_" in p:
                continue
            d = json.load(open(p, encoding="utf-8"))
            o = ((d.get("raw_response_body") or {}).get("data") or {}).get("outputs") or {}
            if not o or o.get("gate_path") != "gate_repaired":
                continue
            repaired += 1
            name = os.path.basename(p)[:-5]
            draft_raw = o.get("draft_raw") or ""
            draft_body, _ = sc.split_audit(draft_raw)
            draft_body, _r, _s = sc.render_body(draft_body)
            nb = sc._norm(draft_body)
            pg = json.loads(o["post_gate_report"])
            final_ids = pg["positions"].get("declared_position_ids") or []
            draft_anchor = {}
            for raw in re.findall(r"^\s*POS\s*::\s*(.+)$", draft_raw, flags=re.M):
                parts = [x.strip() for x in re.split(r"\s*::\s*", raw) if x.strip()]
                if len(parts) >= 3:
                    draft_anchor[parts[0]] = " :: ".join(parts[2:])
            for pid in final_ids:
                a = draft_anchor.get(pid)
                ok = bool(a) and sc._norm(a) in nb
                if not ok:
                    suspect.append({"case": name, "position_id": pid,
                                    "draft_had_line": bool(a),
                                    "draft_anchor_in_draft_body": ok})
                rows.append({"case": name, "position_id": pid, "anchor_from_model": ok})
    return rows, repaired, suspect


def main():
    dirs = sys.argv[1:] or ["account-operations/evidence/ep06b-runtime-behavior-v14/*.json",
                            "account-operations/evidence/ep07-longitudinal-v14/E*.json"]
    rows, repaired, suspect = audit(dirs)
    out = {
        "what": "D-3 残留缺口离线计量：补齐节点是否替模型写出了同 id 的锚点句",
        "scope": dirs,
        "runs_that_entered_repair": repaired,
        "positions_checked_in_repaired_runs": len(rows),
        "anchor_traced_back_to_model_draft": sum(1 for r in rows if r["anchor_from_model"]),
        "suspect": suspect,
        "suspect_count": len(suspect),
        "note": "本项不阻断运行，只计量。为零说明这条残留路径本批次没有被走到；"
                "非零则说明 D-3 的 id 级剥离不够，需要在下一版把草稿正文送进复检。",
    }
    ev = os.path.join(WT, "account-operations/evidence/ep22-rebind005-g4")
    os.makedirs(ev, exist_ok=True)
    with open(os.path.join(ev, "D3_RESIDUAL_ANCHOR_AUDIT.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("runs_that_entered_repair", "positions_checked_in_repaired_runs",
                       "anchor_traced_back_to_model_draft", "suspect_count", "suspect")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
