#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 运行器 v1.1｜只发起、只记录，不判定。

v1.0 的单点后继：只把冻结规格与层间硬门的判定书指向 v1.1，发起逻辑一行未改
（加载 v1.0 后覆盖三个模块常量，"逻辑未改"因此是结构事实，不是文档声明）。
v1.0 文件与 S4_PHASE_C_RESULT_v1.0.json 原样保留。

    python3 S4_PHASE_C_RUN_v1.1.py --layer C2
    python3 S4_PHASE_C_RUN_v1.1.py --layer C3
"""
import argparse
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("pcrun10", os.path.join(HERE, "S4_PHASE_C_RUN_v1.0.py"))
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)

R.FREEZE = os.path.join(R.STAGES, "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json")
R.RESULT = os.path.join(R.STAGES, "S4_PHASE_C_RESULT_v1.1.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", required=True, choices=["C1", "C2", "C3"])
    a = ap.parse_args()
    fz = json.load(io.open(R.FREEZE, encoding="utf-8"))
    os.makedirs(R.EV, exist_ok=True)
    R.preflight(fz, a.layer)
    if a.layer == "C1":
        R.run_c1(fz)
    elif a.layer == "C2":
        R.run_turns(fz, "C2", [1, 2])
    else:
        R.run_turns(fz, "C3", [3, 4, 5, 6])


if __name__ == "__main__":
    sys.exit(main())
