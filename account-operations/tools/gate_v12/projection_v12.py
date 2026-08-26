"""M2→M3 周期状态投影（纵向 harness 侧）。

v1.1 的投影是无条件全量覆盖：`standing = 本轮输出`。E07 一份 523 字的零实质输出
把上一基线里的 P1/P2/P3 与四周节奏整体挤掉，E08 起再未出现，**无任何机制察觉**。

冻结件 §3 把链接规则写成"逐字回填"，但同一节也写明它模拟的是
「经相应权限和接受规则后，由 M2 保存当前有效判断」——**接受规则这一步当时没实现**。
v1.2 把它补上，三条规则全部机械可复算：

  1. 交付不够格成为当前有效判断（cycle_state_carry=REJECTED） ⇒ 保持上一有效值，不覆盖；
  2. 够格但有关键对象未被点名处置 ⇒ 逐字保留上一基线中提到这些对象的原句，不静默丢；
  3. 全部对象要么继续、要么被点名处置 ⇒ 整体替换。

三条都**显式记录**在每步的 projection 段里，没有静默分支。
"""
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared_checks import extract_baseline_objects, check_continuity, _parse_slots  # noqa: E402

CARRY_HEADER = "———— 以下来自上一有效周期基线，本轮判断未涉及、也未点名处置，按连续性义务逐字保留 ————"


def _sentences(t):
    return [s.strip() for s in re.split(r"(?<=[。！？\n])", t or "") if s.strip()]


def project(prev_standing, output_text, carry, prev_account_context):
    """返回 (新的 standing_cycle_baseline, 一份可核查的投影记录)。"""
    slots = _parse_slots(prev_account_context)
    base_obj = extract_baseline_objects(slots)
    before = sorted(set(base_obj.get("tasks", [])) | set(base_obj.get("rhythm", [])))
    cont = check_continuity(base_obj, output_text or "")
    not_restated = cont.get("not_restated") or cont.get("dropped_without_notice") or []
    rec = {"objects_before": before,
           "objects_after_carried": cont["carried"], "objects_disposed": cont["disposed"],
           "objects_not_restated": not_restated,
           "objects_covered_by_blanket": cont.get("dropped_covered_by_blanket", []),
           "continuity_status": cont["status"], "cycle_state_carry": carry}

    if carry != "ACCEPTABLE_AS_NEW_BASELINE":
        rec["mode"] = "KEPT_PREVIOUS"
        rec["explicit_failure"] = "本轮交付不够格成为当前有效判断，上一有效基线原样保留"
        rec["chars_before"], rec["chars_after"] = len(prev_standing or ""), len(prev_standing or "")
        return prev_standing, rec

    at_risk = list(not_restated) + list(cont.get("dropped_covered_by_blanket", []))
    if at_risk:
        prev_text = slots.get("standing_cycle_baseline", "") or ""
        keep = []
        for s in _sentences(prev_text):
            for o in at_risk:
                is_rhythm = bool(re.search(r"条\s*/?\s*周|每周", o))
                pat = (r"每周\s*\d+\s*条|\d+\s*条\s*/\s*周" if is_rhythm
                       else r"(?<![A-Za-z0-9])" + re.escape(o) + r"(?![A-Za-z0-9])")
                if re.search(pat, s):
                    keep.append(s)
                    break
        merged = (output_text or "").rstrip()
        if keep:
            merged += "\n\n" + CARRY_HEADER + "\n" + "\n".join(keep)
        rec["mode"] = "MERGED_KEEP_PRIOR"
        rec["preserved_sentences"] = keep
        rec["chars_before"], rec["chars_after"] = len(prev_standing or ""), len(merged)
        return merged, rec

    rec["mode"] = "REPLACED"
    rec["chars_before"], rec["chars_after"] = len(prev_standing or ""), len(output_text or "")
    return output_text, rec
