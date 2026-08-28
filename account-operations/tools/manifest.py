#!/usr/bin/env python3
"""参考文件清单的构造（任务分支内真源）。

第 9 轮重建。原件在会话级 scratchpad 里，随会话消失。

**重建保真度是证出来的，不是声明的**：把本文件的输出与第 8 轮 71 次真实运行里
已落盘的 `workflow_inputs.loaded_references` 逐一比对，71/71 逐字节相同
（两种取值：含服装参考 70 例、不含 1 例）。校验脚本
`account-operations/tools/verify_rebuilt_modules.py`，可随时复算。
"""

HEADER = ("<<REFERENCE_MANIFEST>>\n"
          "references/fashion-and-market.md: {fashion}\n"
          "references/six-skill-methods.md: NOT_LOADED\n"
          "<<END_REFERENCE_MANIFEST>>")

BODY_SEP = "\n\n# references/fashion-and-market.md\n\n"


def build_refs(include_fashion_ref, fashion_text):
    """条件加载：清单头永远给，正文只在本轮确实加载时附上。

    `six-skill-methods.md` 在本任务的全部取证里一直是 NOT_LOADED——
    这是冻结用例集的设定，不是本文件的判断。
    """
    if not include_fashion_ref:
        return HEADER.format(fashion="NOT_LOADED")
    return HEADER.format(fashion="LOADED") + BODY_SEP + fashion_text
