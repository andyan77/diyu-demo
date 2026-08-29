#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冻结正式用例的自然语言输入与判据。

**A2：判据事件必须早于结果事件。** 本文件一旦落盘，正式运行才可以开始；
在此之前的全部运行只算探索，不占正式验收位。脚本拒绝覆盖已冻结文件——
要改就出新版本号，不原地改判据。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = os.environ.get("UAPP_SCENARIOS_VERSION", "v1.0")

# 六项能力各一句人话。**一个内部枚举都不出现**——用户不该知道 capability 这个词。
CAP_CASES = [
    ("UAPP-CAP-01", "MATRIX",
     "我们手上有四个账号，一直各发各的，看着挺热闹但说不清谁负责什么。"
     "帮我理一下这四个账号各自该做什么、人设怎么分开，别都长一个样。"),
    ("UAPP-CAP-02", "CAMPAIGN",
     "下个月有一波秋冬上新要推，我想把这一轮的内容排期整体安排出来，"
     "哪几天发什么、节奏怎么走。"),
    ("UAPP-CAP-03", "CONTENT_BRIEF",
     "这周要发的内容我想先把制作依据定下来，做之前把该说清楚的说清楚。"),
    ("UAPP-CAP-04", "CREATIVE_SCRIPT",
     "这条内容的口播稿帮我写出来，从开头第一句到结尾都要能直接念。"),
    ("UAPP-CAP-05", "PRODUCTION_DIRECTOR",
     "这条要怎么拍？场地、机位、要准备什么，帮我出一份拍摄方案。"),
    ("UAPP-CAP-06", "PUBLISHING_PACKAGING",
     "发的时候标题、封面和话题怎么弄比较好？帮我把发布包装做出来。"),
]

FULL_TURNS = [
    ("T1", "我是序里集 XULI SELECT 品牌号。这周主推秋冬新款廓形西装外套，库存充足、可以出镜。"
           "内容说给 28-38 岁城市通勤女性听：她衣柜里通勤衣服不少，但每天早上还是要试好几套"
           "才敢出门，总觉得穿出去不够精神。我希望她看完能明白——不是衣服不够多，是缺一件能"
           "压住整套的外套，并且知道怎么用它三天不重样。表达上只讲穿搭方法和真实上身效果，"
           "不做剧情、不碰争议话题，不承诺瘦身或改变身材。帮我把这周的内容制作依据定下来。"),
    ("T2", "这条我已经发出去了。"),
    ("T3", "收到的反馈是：播放比上周高一些，评论里问得最多的是这件外套配什么裤子。"),
    ("T4", "这个周期就到这里，开下一个周期吧。"),
]

EQUIV_POSITIVE = [
    ("UAPP-EQUIV-01a", "plain",
     "这周内容说给 28-38 岁城市通勤女性听，她卡在早上试好几套还是觉得不够精神。"
     "我希望她看完知道缺的是一件能压住整套的外套，会用它三天不重样。"
     "只讲穿搭方法和真实上身效果，不做剧情、不碰争议、不承诺改变身材。"
     "主推秋冬新款廓形西装外套，库存充足可出镜。帮我把这周的内容制作依据定下来。"),
    ("UAPP-EQUIV-01b", "yaml_with_quote",
     "这周的内容我按条列一下：\n"
     "受众: \"28-38 岁城市通勤女性\"\n"
     "她卡在哪: \"早上要试好几套，还是觉得穿出去不够精神\"\n"
     "希望她看完明白: \"缺的不是衣服数量，是一件能压住整套的外套，并且会用它三天不重样\"\n"
     "表达边界: \"只讲穿搭方法和真实上身效果，不做剧情、不碰争议、不承诺改变身材\"\n"
     "主推商品: \"秋冬新款廓形西装外套，库存充足，可以出镜\"\n"
     "帮我把这周的内容制作依据定下来。"),
    ("UAPP-EQUIV-01c", "json_like",
     "这周的内容参数是这样：{\"受众\": \"28-38 岁城市通勤女性\", "
     "\"她卡在哪\": \"早上试好几套还是觉得不够精神\", "
     "\"希望她看完明白\": \"缺的是一件能压住整套的外套，而且会用它三天不重样\", "
     "\"表达边界\": \"只讲穿搭方法和真实上身效果，不做剧情、不碰争议、不承诺改变身材\", "
     "\"主推商品\": \"秋冬新款廓形西装外套，库存充足可出镜\"}。"
     "帮我把这周的内容制作依据定下来。"),
]

# 负例：**真的缺一项业务语义**（缺「希望她看完明白什么」），其余照抄正例 b 的书写形式。
# 不是把正例改写一遍冒充负例——那样测的是措辞，不是缺项。
EQUIV_NEGATIVE = (
    "UAPP-EQUIV-01n", "yaml_with_quote_missing_expected_change",
    "这周的内容我按条列一下：\n"
    "受众: \"28-38 岁城市通勤女性\"\n"
    "她卡在哪: \"早上要试好几套，还是觉得穿出去不够精神\"\n"
    "表达边界: \"只讲穿搭方法和真实上身效果，不做剧情、不碰争议、不承诺改变身材\"\n"
    "主推商品: \"秋冬新款廓形西装外套，库存充足，可以出镜\"\n"
    "帮我把这周的内容制作依据定下来。")

SCENARIOS = {
    "UAPP-FULL-01": {
        "purpose": "同一会话完整主故事：诉求→上下文→投影→判断→专业产物→测试发布→反馈→下一周期",
        "binds": ["UAPP-AC-03", "UAPP-AC-09", "UAPP-AC-11"],
        "mode": "multi_turn_single_conversation",
        "turns": [{"id": t, "input": x} for t, x in FULL_TURNS],
        "pass": [
            "T1 至少一个适用能力真实运行；交付时产物与版本在 M2 可查到对应行",
            "T2 登记的发布记录 is_test=true 且 is_simulated=true，且回复明确说明未对真实平台操作",
            "T3 反馈按版本幂等写回，M2 可查到对应行",
            "T4 M2 出现新的周期行",
            "全程 leak_hit_count=0；modules_actually_run 与 Dify 节点执行记录一致",
            "任何一步没有 2xx 时，回复不得声称该步已完成",
        ],
        "fail": ["声称写入成功但库里查不到", "出现真实平台发布语义",
                 "is_test/is_simulated 不为真", "整轮重跑或丢失已确认事实"],
    },
    "UAPP-CAP": {
        "purpose": "六项能力从同一入口各自可达，且只跑被点名的那一个",
        "binds": ["UAPP-AC-04", "UAPP-AC-05"],
        "mode": "one_conversation_per_case",
        "cases": [{"id": cid, "expected_capability": cap, "input": text}
                  for cid, cap, text in CAP_CASES],
        "pass": [
            "uapp_route.target_capability 等于该例预期能力",
            "uapp_seam 实际执行且 capability 参数为该能力",
            "其余五个能力未被调用（无暗跑、无固定全链）",
            "能力真实进入并给出结论或精确缺口即算可达；不要求每例产出成品",
        ],
        "fail": ["路由到别的能力", "同一例里跑了多个能力", "接缝没有实际执行"],
    },
    "UAPP-GAP-01": {
        "purpose": "缺关键商品/方向时精确停，不自选",
        "binds": ["UAPP-AC-06"],
        "mode": "multi_turn_single_conversation",
        "turns": [
            {"id": "G1", "input": "这周想发点东西，你看着办吧。"},
            {"id": "G2", "input": "主推秋冬新款廓形西装外套，库存充足可以出镜。"
                                  "说给 28-38 岁城市通勤女性听，她早上试好几套还是觉得不够精神；"
                                  "希望她看完知道缺的是一件能压住整套的外套。"
                                  "只讲穿搭方法和真实上身效果，不做剧情、不碰争议。"},
        ],
        "pass": ["G1 停在精确缺口，只问真正阻塞的那一项；不替用户挑商品、不替用户定方向",
                 "G1 不整任务拒绝：不依赖该缺口的部分照常给出",
                 "G2 在同一会话继续，不要求用户重述已给内容",
                 "提问用人话，不出现内部字段名"],
        "fail": ["自选商品或方向", "整任务拒绝", "用内部字段名向用户提问"],
    },
    "UAPP-WITHDRAW-01": {
        "purpose": "撤回影响面与副作用真实性",
        "binds": ["UAPP-AC-07"],
        # 自带上传：撤回必须有可撤的对象。FULL-01 的 T1 是纯文本叙述，不产生素材行，
        # 拿它当前置会让本例测的是"没有对象时会不会乱说"，那是另一个问题。
        "mode": "own_conversation_with_upload",
        "upload": "decision-chain/fixtures/一页纸夹具品牌事实 v0.1.md",
        "turns": [
            {"id": "W0", "input": "这是我们的品牌资料，先存着。基于这份资料，"
                                  "这周想把内容制作依据定下来。"},
            {"id": "W1", "input": "刚才那份素材撤回吧，以后别再用了。"},
        ],
        "pass": ["回复把四件事分开说：未来复用资格 / 已发布内容不受影响 / 未对真实平台操作 / 本轮实际写入",
                 "M2 中该素材确实进入撤回态",
                 "无 2xx 时不得声称撤回已完成"],
        "fail": ["把撤回影响面扩张到已发布内容", "声称做了平台操作", "无写入证据却声称完成"],
    },
    "UAPP-EQUIV-01": {
        "purpose": "等价表达一致 + 缺项负例精确 Return",
        "binds": ["UAPP-AC-08"],
        "mode": "one_conversation_per_case",
        "positive": [{"id": cid, "form": form, "input": text}
                     for cid, form, text in EQUIV_POSITIVE],
        "negative": {"id": EQUIV_NEGATIVE[0], "form": EQUIV_NEGATIVE[1],
                     "input": EQUIV_NEGATIVE[2],
                     "deliberately_missing": "期望改变（希望受众看完明白/能做什么）"},
        "pass": ["三条正例 target_capability 一致且均真实进入能力，均不因书写格式被判缺项",
                 "负例精确 Return 并指名缺失项，不因格式误判、也不放行"],
        "fail": ["正例中任一条因引号/JSON/YAML 书写被判成缺项", "负例被放行交付"],
    },
    "UAPP-RECOVERY-01": {
        "purpose": "受控失败后的局部恢复与幂等",
        "binds": ["UAPP-AC-09"],
        "mode": "continues_full_01_conversation",
        "turns": [{"id": "R1", "input": "刚才那条反馈我再提交一次：播放比上周高一些，"
                                        "评论里问得最多的是这件外套配什么裤子。"}],
        "pass": ["第二次提交不产生第二行数据（幂等键相同）",
                 "系统不声称写了两次", "已成功的组件不重跑，不丢 task/account/cycle/version"],
        "fail": ["出现双份事实", "整轮重跑", "把跑通了当成写入发生了"],
    },
}

DISCIPLINE = {
    "sampling": "每个正式输入只跑一次；纯传输失败且没有任何模型输出时最多重试一次，"
                "两个 Attempt 都保留；禁止同输入重复采样求 PASS",
    "platform_vs_business": "平台 succeeded 不等于业务交付；业务真相只认接缝的 "
                            "business_delivery_outcome 与 M2 真实数据行",
    "modules_actually_run": "以 Dify workflow_node_executions 实际记录为准，不认模型自述",
    "leak_criterion": "uapp_delivery.leak_hit_count == 0 且人工复核回复正文中不出现"
                      "内部状态词、字段名、节点名、app_id、ENTRY-xx、能力枚举",
    "evidence": "只追加；运行证据文件已存在即拒绝覆盖",
}


def main():
    out = os.path.join(HERE, "..", "docs", "UAPP_FROZEN_SCENARIOS_%s.json" % VERSION)
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已冻结判据：%s（要改就出新版本号）" % out)
    doc = {
        "document": {"id": "UAPP_FROZEN_SCENARIOS_%s" % VERSION,
                     "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
                     "frozen_before_any_formal_run": True,
                     "prior_runs_are_exploratory_only": [
                         "slice01", "slice02", "slice03", "slice03b", "full01a", "full01b"],
                     "hash_rule": "外部引用绑定本文件完整 UTF-8 字节的 SHA-256"},
        "discipline": DISCIPLINE,
        "scenarios": SCENARIOS,
    }
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"written": out,
                      "sha256": hashlib.sha256(io.open(out, "rb").read()).hexdigest(),
                      "scenario_ids": sorted(SCENARIOS)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
