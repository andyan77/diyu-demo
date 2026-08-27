"""M2→M3 周期状态投影（纵向 harness 侧）· v1.3

v1.1 无条件全量覆盖：一份 523 字的零实质输出把上一基线整体挤掉，无人察觉。
v1.2 加了三分支与"逐字保留"，但**基线对象仍然是从散文里正则抠出来的**——
第 5 轮实测的代价：`P1/P2/P3` 这个编号在产品语义里根本没有依据，保护分支 12 步 0 次生效；
`dropped_without_notice` 全程为 `[]` 的同时，8 个被独立追踪的对象真丢了 7 个。
判定者那句话必须留在代码里：

    在抽取器覆盖面被独立验证之前，`dropped_without_notice: []`
    **不构成**「没有内容被丢掉」的证据。

v1.3 换掉的是方法，不是参数：**持续位是结构化对象，端到端不经过散文。**
上一步投影写出 `standing_positions[]`，本步模型在审计块里对**每一个** id 逐条声明，
闸门做集合比对。少一个就阻断——因此"字段为空"这次真的等于"没有东西没交代"。

三条链接规则仍然全部显式，没有静默分支：

  1. 交付不够格成为当前有效判断（carry=REJECTED）⇒ 散文与持续位一并保持上一有效值；
  2. 够格 ⇒ 散文替换为本轮输出；持续位按声明逐条演进（继续／处置／替换／新增）；
  3. 处置掉的位不删除，进 `disposed_log`，可回指。
"""
import json


def _index(positions):
    return {p["id"]: dict(p) for p in (positions or []) if p.get("id")}


def project(prev_standing, prev_positions, output_text, carry, positions_report, step_id):
    """返回 (新的 standing_cycle_baseline 散文, 新的 standing_positions[], 可核查的投影记录)。"""
    if isinstance(positions_report, str):
        try:
            pr = json.loads(positions_report or "{}")
        except Exception:                                  # noqa: BLE001
            pr = {}
    else:
        pr = positions_report or {}

    prev_idx = _index(prev_positions)
    rec = {
        "projection_version": "v1.3",
        "step_id": step_id,
        "cycle_state_carry": carry,
        "positions_before": sorted(prev_idx),
        "declared_continued": pr.get("continued", []),
        "declared_disposed": pr.get("disposed", []),
        "declared_new": pr.get("new_positions", []),
        "positions_unaccounted": pr.get("positions_unaccounted", []),
        "positions_fabricated": pr.get("positions_fabricated", []),
        "input_parse_error": pr.get("input_parse_error"),
    }

    if carry != "ACCEPTABLE_AS_NEW_BASELINE":
        rec["mode"] = "KEPT_PREVIOUS"
        rec["explicit_failure"] = "本轮交付不够格成为当前有效判断，上一有效基线与持续位原样保留"
        rec["positions_after"] = sorted(prev_idx)
        rec["chars_before"] = len(prev_standing or "")
        rec["chars_after"] = len(prev_standing or "")
        return prev_standing, list(prev_positions or []), rec

    # ---- 够格：持续位按声明逐条演进 ----
    new_positions, disposed_log = [], list(rec.get("disposed_log") or [])
    for pid, p in prev_idx.items():
        if pid in (pr.get("disposed") or []):
            p["disposed_at"] = step_id
            disposed_log.append(p)
            continue
        p["last_restated"] = step_id
        new_positions.append(p)
    for np in (pr.get("new_positions") or []):
        new_positions.append({"id": np.get("id"), "kind": np.get("kind"),
                              "title": np.get("id"), "since": step_id,
                              "last_restated": step_id})

    rec["mode"] = "ADVANCED"
    rec["positions_after"] = sorted(p["id"] for p in new_positions)
    rec["disposed_log_added"] = [p["id"] for p in disposed_log]
    rec["chars_before"] = len(prev_standing or "")
    rec["chars_after"] = len(output_text or "")
    # 散文可以变短，**持续位不会因此丢**——这正是 v1.3 与 v1.2 的分界。
    rec["prose_shrank"] = rec["chars_after"] < rec["chars_before"]
    return output_text, new_positions, rec


def serialize_positions(positions):
    """写进下一步 account_context 的 standing_positions 槽位。
    一行 JSON，闸门用 json.loads 读——不需要任何正则。"""
    return json.dumps(positions or [], ensure_ascii=False)
