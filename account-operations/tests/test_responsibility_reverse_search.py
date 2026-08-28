"""责任与禁区反搜（宪法动作 1 与 5）。

覆盖的冻结判据：

- **M3-AC-01 ①**：Skill 树中不存在第二份状态存储、评分器、日历生成器；
- **M3-AC-01 ②**：`排期表`/`发布日历`/`打分`/`评分`/`score`/`rank` 等词的出现处
  **必须是禁止性表述**；
- **M3-AC-13 ①**：M3 侧不存在指向 M2 写接口的直接调用、凭据或 `is_current=true` 的设置；
- **M3-AC-13 ③**：不存在 M3 自有的持久化状态存储；
- **M3-AC-15 ①**：Skill 中不得出现钩子／叙事／台词／镜头／标题／封面／发布文案的
  **具体产出**。

这几条都是**期望为空**的负向检查。期望为空的检查最容易变成安慰剂——它天然全绿，
即使正则写错、路径写错、或者根本没扫到任何文件。所以每一条都配了自我校验：
先证明扫描器确实扫到了东西、确实能在注入的违规样本上失败，再报告"没搜到"。
"""

import os
import re
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_INTERFACES = os.path.join(_ROOT, "interfaces")
if _INTERFACES not in sys.path:
    sys.path.insert(0, _INTERFACES)

import projection as P  # noqa: E402

SKILL_DIR = os.path.join(_ROOT, "skills", "operating-one-account")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def _skill_files():
    out = []
    for base, _dirs, names in os.walk(SKILL_DIR):
        for name in sorted(names):
            if name.endswith(".md"):
                out.append(os.path.join(base, name))
    return out


def _interface_files():
    out = []
    for base, _dirs, names in os.walk(_INTERFACES):
        if "__pycache__" in base:
            continue
        for name in sorted(names):
            if name.endswith((".py", ".json", ".md")):
                out.append(os.path.join(base, name))
    return out


def _lines(paths):
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for number, text in enumerate(handle, 1):
                yield path, number, text.rstrip("\n")


# 禁止性标记。命中禁区词的那一行必须同时带有其中之一，否则就是在**教 M3 去做**
# 这件事，而不是在划边界。
PROHIBITION_MARKERS = (
    "不", "禁", "别", "停", "属于", "而是", "只", "无权", "越界", "不得",
    "NOT", "not", "Do NOT", "never", "instead",
)

# M3-AC-01 ② + AC-15 ① 的禁区词
RESPONSIBILITY_TERMS = (
    "排期表", "发布日历", "选题清单", "打分", "评分", "排名",
    "钩子", "叙事结构", "台词", "镜头", "分镜", "标题", "封面", "发布文案",
    "表演指导",
)


class ScannerSelfCheck(unittest.TestCase):
    """先证明扫描器不是安慰剂。"""

    def test_scanner_actually_reads_the_skill_tree(self):
        files = _skill_files()
        self.assertGreaterEqual(len(files), 3, "Skill 树至少应有 SKILL.md + 两份条件附件")
        self.assertIn(SKILL_MD, files)
        total = sum(1 for _ in _lines(files))
        self.assertGreater(total, 400, "扫到的行数远少于预期，扫描范围可能是错的")

    def test_prohibition_detector_rejects_an_injected_violation(self):
        """注入一条"教 M3 去做"的样本，检测器必须判它违规。"""

        offending = "为账号生成一张下个月的发布日历，并给每条内容打分排名。"
        self.assertFalse(
            any(marker in offending for marker in PROHIBITION_MARKERS),
            "检测器把一条明显的违规句判成了禁止性表述",
        )
        legit = "**不做**：排期表、发布日历、选题清单｜给内容打分排名。"
        self.assertTrue(any(marker in legit for marker in PROHIBITION_MARKERS))


class ResponsibilityBoundary(unittest.TestCase):
    """M3-AC-01 ② / M3-AC-15 ①：禁区词只能出现在禁止性表述里。"""

    def test_forbidden_terms_appear_only_in_prohibitive_statements(self):
        """禁止性可以来自本行，也可以来自它所在的块。

        第一版只看本行，报了 4 条"违规"，逐条查证后全部是误报：三条是
        `**不做**：` 标题下的列表项，一条是 `## 自检` 下的反问句
        （"有没有替下游写钩子、叙事、镜头、标题或封面？"）。**它们本身就是禁止性
        表述**，只是禁止性写在块首而不是每一行里。

        判据没有放宽——"出现处必须是禁止性表述"照旧。变的是检测器：它现在按人读
        文档的方式判断上下文，而不是按行孤立地判断。
        """

        block_leads = ("不做", "自检", "不得", "越界", "禁止", "永远不", "停止边界",
                       "非责任", "不负责")
        offenders = []
        hits = 0
        for path in _skill_files():
            with open(path, encoding="utf-8") as handle:
                lines = [line.rstrip("\n") for line in handle]
            for index, text in enumerate(lines):
                if not any(term in text for term in RESPONSIBILITY_TERMS):
                    continue
                hits += 1
                if any(marker in text for marker in PROHIBITION_MARKERS):
                    continue
                # 反问式自检（"有没有……？"）本身就是在找违规，不是在教做法。
                if text.strip().endswith("？"):
                    continue
                # 向上回溯至多 8 行找块级禁止性引导（如 `**不做**：`）。
                window = lines[max(0, index - 8):index]
                if any(lead in line for line in window for lead in block_leads):
                    continue
                offenders.append("%s:%d %s" % (os.path.basename(path), index + 1, text.strip()[:120]))

        self.assertGreater(hits, 5, "一个禁区词都没搜到——正则或路径有问题，不是真的干净")
        self.assertEqual([], offenders, "禁区词出现在非禁止性表述中：%s" % offenders)

    def test_block_level_exemption_has_a_known_blind_spot(self):
        """**登记这条检查的已知上限，不是证明它没有上限。**

        块级豁免的代价是真实的：一段以 `**不做**：` 开头、但列表项里确实在教
        M3 怎么排日历的文本，会被放过。这条测试把那个盲点钉成可见的事实。

        因此 AC-01 ② 的正式证据等级是 `static_verified`，**不是** `runtime_verified`：
        它证明的是"当前 Skill 文本里的禁区词都写在禁止性块中"，证明不了"模型运行时
        不会去排日历"。后者是 AC-01 ③ 的盲评消融门（EP-08），本轮 `NOT_VERIFIED`。
        """

        block_leads = ("不做", "自检", "不得")
        lines = ["**不做**：", "", "- 先按周一到周日铺满发布日历，再给每条打分排序；"]
        target = lines[2]
        self.assertTrue(any(t in target for t in RESPONSIBILITY_TERMS))
        # 该行本身不含禁止性标记，也不是反问句
        self.assertFalse(any(m in target for m in PROHIBITION_MARKERS))
        self.assertFalse(target.strip().endswith("？"))
        # 块级豁免会放过它——这正是本检查的已知上限，必须显式登记而不是假装不存在
        self.assertTrue(any(lead in line for line in lines[:2] for lead in block_leads))

    def test_skill_declares_the_boundary_explicitly_up_front(self):
        with open(SKILL_MD, encoding="utf-8") as handle:
            head = "".join(handle.readlines()[:20])
        for owed in ("不做", "Matrix", "打分"):
            with self.subTest(term=owed):
                self.assertIn(owed, head)


class NoSecondStateStore(unittest.TestCase):
    """M3-AC-01 ① / M3-AC-13 ③：不存在第二份状态真源。"""

    PERSISTENCE_SIGNS = (
        "sqlite", "psycopg", "sqlalchemy", "CREATE TABLE", "INSERT INTO", "UPDATE ",
        "DELETE FROM", "redis", "pickle.dump", "shelve", "os.makedirs",
    )

    def test_no_persistence_primitives_in_the_m3_tree(self):
        offenders = []
        for path, number, text in _lines(_skill_files() + _interface_files()):
            for sign in self.PERSISTENCE_SIGNS:
                if sign.lower() in text.lower():
                    offenders.append("%s:%d %s" % (os.path.basename(path), number, text.strip()[:120]))
        self.assertEqual([], offenders, "M3 侧出现持久化原语：%s" % offenders)

    def test_projection_module_writes_nothing(self):
        """投影编译器必须是纯函数：不开文件、不发网络请求、不起子进程。

        用 AST 而不是子串匹配。子串匹配在这里是错的工具——第一版按 `"requests" in
        source` 判，被 `requested.get("side_requests")` 这个**正常业务字段名**判成了
        网络调用。禁区检查一旦开始误报，真正的违规就会淹没在噪声里。
        """

        import ast

        with open(os.path.join(_INTERFACES, "projection.py"), encoding="utf-8") as handle:
            tree = ast.parse(handle.read())

        forbidden_modules = {"requests", "httpx", "urllib", "socket", "subprocess", "os",
                             "pathlib", "shutil", "sqlite3", "pickle"}
        forbidden_calls = {"open", "exec", "eval", "compile", "__import__"}

        imported, called = set(), set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called.add(node.func.id)

        self.assertEqual(set(), imported & forbidden_modules,
                         "投影编译器引入了 I/O 模块：%s" % (imported & forbidden_modules))
        self.assertEqual(set(), called & forbidden_calls,
                         "投影编译器调用了 I/O 原语：%s" % (called & forbidden_calls))
        # 自我校验：确实解析出了东西，不是空树假通过
        self.assertIn("datetime", imported, "AST 没解析到已知的 datetime import，扫描是空的")

    def test_no_scorer_or_calendar_generator(self):
        """评分器与日历生成器的实现形态，不只是词。"""

        for path, number, text in _lines(_interface_files()):
            lowered = text.lower()
            for sign in ("def score", "def rank", "def rate_", "def generate_calendar",
                         "def build_schedule", "weight *", "* weight"):
                with self.subTest(path=os.path.basename(path), sign=sign):
                    self.assertNotIn(sign, lowered, "%s:%d" % (path, number))


class NoDirectM2Write(unittest.TestCase):
    """M3-AC-13 ①：M3 侧不存在指向 M2 写接口的直接调用或凭据。"""

    def test_no_write_endpoint_calls_or_credentials(self):
        offenders = []
        for path, number, text in _lines(_skill_files() + _interface_files()):
            lowered = text.lower()
            if any(t in lowered for t in ("api_key", "apikey", "authorization:", "bearer ",
                                          "x-actor-ref", "password", "secret")):
                offenders.append("cred %s:%d" % (os.path.basename(path), number))
            if any(t in lowered for t in (".post(", ".put(", ".patch(", ".delete(",
                                          "client.post", "httpx.post")):
                offenders.append("write-call %s:%d" % (os.path.basename(path), number))
        self.assertEqual([], offenders, "M3 侧出现写调用或凭据：%s" % offenders)

    def test_candidate_envelope_cannot_express_acceptance(self):
        """AC-13 反证探针：用候选信封表达"把这条反馈改成正面"必须表达不出来。"""

        attempts = (
            {"payload": {"feedback_override": {"fb-1": "positive"}}},
            {"payload": {"is_current": True}},
            {"payload": {"nested": {"deep": {"promote": "cand-1"}}}},
            {"affects": {"invalidates": [], "explicitly_unchanged": [], "accepted": True}},
        )
        for i, overlay in enumerate(attempts):
            with self.subTest(i=i):
                candidate = {
                    "schema_version": "1.0",
                    "candidate_status": "proposed",
                    "candidate_kind": "review_update",
                    "based_on": [{"ref": "x", "evidence_identity": "confirmed_fact"}],
                    "affects": {"invalidates": [], "explicitly_unchanged": []},
                }
                candidate.update(overlay)
                self.assertTrue(
                    P.validate_writeback_candidate(candidate),
                    "候选信封表达出了「已接受／已晋升／覆盖反馈」：%r" % overlay,
                )

    def test_no_write_endpoint_points_at_feedback_or_market_observations(self):
        import json

        schema_path = os.path.join(_INTERFACES, "M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json")
        with open(schema_path, encoding="utf-8") as handle:
            allowed = json.load(handle)["properties"]["suggested_m2_endpoint"]["enum"]
        self.assertTrue(allowed, "端点白名单为空，这条检查会假通过")
        for endpoint in allowed:
            with self.subTest(endpoint=endpoint):
                self.assertNotIn("feedback", endpoint.lower())
                self.assertNotIn("market-observation", endpoint.lower())
                self.assertNotIn("promote", endpoint.lower())


class SemanticBackReference(unittest.TestCase):
    """宪法动作 1（回指）：16 项不可改 WHAT 都要有承载小节。"""

    def test_skill_carries_a_semantic_backreference_table(self):
        with open(SKILL_MD, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("语义回指表", text)
        rows = re.findall(r"^\|\s*(\d+)\s*\|", text, flags=re.M)
        self.assertGreaterEqual(
            len(rows), 16, "回指表少于 16 行——ENGINEERING_HANDOFF §5 的 16 项没被逐项承载"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
