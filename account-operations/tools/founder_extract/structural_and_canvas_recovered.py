#!/usr/bin/env python3
"""恢复后的非模型取证：图结构、系统提示词绑定、浏览器渲染画布。零模型调用。

三个脚本原本写进历史证据目录（ep24 / ep25 / ep31 / ep36）。**历史证据不覆盖**，
这里把 `OUT` 改道到 ep43，判据一个字没动。
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

OUT = os.path.join(WT, "account-operations/evidence/ep43-dify-live-candidate-binding")


def run(label, modname):
    os.makedirs(OUT, exist_ok=True)
    m = __import__(modname)
    setattr(m, "OUT", OUT)
    print(f"\n=== {label} ({modname}) ===", flush=True)
    try:
        rc = m.main()
        return {"step": label, "module": modname, "rc": (0 if rc is None else rc),
                "ok": rc in (0, None)}
    except SystemExit as e:
        return {"step": label, "module": modname, "rc": e.code, "ok": e.code in (0, None)}
    except Exception as e:  # noqa: BLE001
        return {"step": label, "module": modname, "rc": -1, "ok": False,
                "error": f"{type(e).__name__}: {e}"}


def main():
    rows = [run("S-1 图结构检查", "graph_structural_check_v14"),
            run("S-2 系统提示词绑定", "capture_system_prompt"),
            run("S-3 浏览器画布实证", "canvas_evidence")]
    rep = {"what": "宿主挂载恢复后的活体候选非模型取证", "zero_model_calls": True,
           "out_dir": os.path.relpath(OUT, WT), "steps": rows,
           "all_pass": all(r["ok"] for r in rows)}
    json.dump(rep, io.open(os.path.join(OUT, "STRUCTURAL_AND_CANVAS_RECOVERED.json"),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n" + json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
