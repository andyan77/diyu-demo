#!/usr/bin/env python3
"""最终候选 v1.5.2：部署后的非模型取证。零模型调用。

三件事，全部读回**已发布的实物**，不是读本地副本：
  S-1 图结构检查      `graph_structural_check_v14`
  S-2 系统提示词绑定   `ac16/capture_system_prompt`
  S-3 浏览器画布实证   `ac16/canvas_evidence`

三个脚本原本都写进历史证据目录（ep24 / ep25 / ep31）。**那是历史证据，不能覆盖**，
所以这里把它们的 `OUT` 改道到 ep36，再跑。改的只有落盘位置，判据一个字没动。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "ac16"))

OUT = os.path.join(WT, "account-operations/evidence/ep36-structural-and-ac16-v152")


def run(label, modname, outattr="OUT"):
    os.makedirs(OUT, exist_ok=True)
    m = __import__(modname)
    setattr(m, outattr, OUT)
    print(f"\n=== {label} ({modname}) ===", flush=True)
    try:
        rc = m.main()
        return {"step": label, "module": modname, "rc": (0 if rc is None else rc),
                "ok": rc in (0, None)}
    except SystemExit as e:
        return {"step": label, "module": modname, "rc": e.code, "ok": e.code in (0, None)}
    except Exception as e:  # noqa: BLE001 - 失败如实记，不隐藏
        return {"step": label, "module": modname, "rc": -1, "ok": False,
                "error": f"{type(e).__name__}: {e}"}


def main():
    rows = [run("S-1 图结构检查", "graph_structural_check_v14"),
            run("S-2 系统提示词绑定", "capture_system_prompt"),
            run("S-3 浏览器画布实证", "canvas_evidence")]
    rep = {"what": "最终候选 v1.5.2 部署后非模型取证", "zero_model_calls": True,
           "out_dir": OUT, "steps": rows, "all_pass": all(r["ok"] for r in rows)}
    json.dump(rep, io.open(os.path.join(OUT, "STRUCTURAL_AC16_V152.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n" + json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
