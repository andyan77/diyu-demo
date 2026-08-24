# -*- coding: utf-8 -*-
"""按文件名解析仓库内路径。

仓库在 2026-08 做过目录重组（`docs/` `skills/` `workflows/` `fixtures/` `evidence/`），
而 `tools/` 下的脚本仍按重组前的扁平布局用 `os.path.join(REPO, "<裸文件名>")` 取文件，
重组后全部 `FileNotFoundError`。

本模块只做一件事：**把裸文件名解析成它在当前布局下的真实路径**。
不改变任何脚本的验证逻辑，也不放宽任何判据——找不到就返回仓库根下的原路径，让调用方照旧报错。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_INDEX = {}
for _dirpath, _dirnames, _filenames in os.walk(ROOT):
    _dirnames[:] = [d for d in _dirnames if not d.startswith(".")]
    for _f in _filenames:
        _INDEX.setdefault(_f, os.path.join(_dirpath, _f))


def rpath(*parts):
    """解析仓库内文件路径。

    单段且是已知裸文件名 -> 返回它的真实位置；
    其余情况 -> 按 ROOT 拼接，行为与原来的 os.path.join(REPO, ...) 一致。
    """
    if len(parts) == 1 and parts[0] in _INDEX:
        return _INDEX[parts[0]]
    return os.path.join(ROOT, *parts)
