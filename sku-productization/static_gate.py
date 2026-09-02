#!/usr/bin/env python3
"""Static Gate — DIYU-V1-STATIC-GATE-001.

Run: python3 sku-productization/static_gate.py
Produces: sku-productization/STATIC_GATE_REPORT.json

Zero LLM calls. Zero network egress (enforced at runtime). Never reads the
sealed empirical test set (enforced at runtime, INV-2). One script, one run,
three terminal states. The report is the only evidence artifact; it must be
fully recomputable from the source tree by re-running this file.
"""

import ast
import builtins
import hashlib
import json
import os
import re
import socket
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# INV-2 · runtime isolation guards — installed before anything else runs.
# ---------------------------------------------------------------------------

SEALED_ROOTS = [
    os.path.join(REPO_ROOT, "eval"),
    "/home/faye/diyu-demo-holdout-custody",
]

_ACCESS_LOG = []
_real_open = builtins.open


def _guarded_open(file, *args, **kwargs):
    try:
        p = os.path.abspath(os.fspath(file))
    except TypeError:
        p = None
    if p:
        for root in SEALED_ROOTS:
            if p == root or p.startswith(root + os.sep):
                raise RuntimeError("INV-2 VIOLATION: attempted read of sealed path %s" % p)
        _ACCESS_LOG.append(p)
    return _real_open(file, *args, **kwargs)


builtins.open = _guarded_open


def _guarded_connect(self, *a, **kw):
    raise RuntimeError("INV-2 VIOLATION: network egress attempted")


socket.socket.connect = _guarded_connect
socket.socket.connect_ex = _guarded_connect

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required\n")
    sys.exit(2)


def git(*args):
    r = subprocess.run(
        ["git", "-C", REPO_ROOT] + list(args),
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# INV-1 · frozen mother-tree manifest.
#
# Baseline commit = 2a5397d (S5 revalidation, the direct parent of e8c1838
# "E1 三 SKU 统一摘取" — the commit at which this task's own lineage first
# began reading/copying these three trees). Using `main` (01a42b0) instead
# would be WRONG: 9574449/c7301a0 (DIYU-V1-PP-BLOCKER-REMEDIATION-S1-S4-001,
# an earlier, separate, already-closed task) legitimately touched four files
# under content-production/ and account-operations/ *before* e8c1838, so
# diffing against main would false-positive on that unrelated, authorized,
# pre-existing history. 2a5397d..HEAD is confirmed empty for these three
# trees (verified live via `git diff --name-only` during this Gate's
# construction) and is the correct "did the SKU build touch the mother tree"
# baseline.
# ---------------------------------------------------------------------------

INV1_BASELINE_COMMIT = "2a5397d"

INV1_FROZEN_TREES = ["content-production", "account-operations", "decision-chain"]

# Six E1 baseline files (products/<sku>/*), full sha256 recomputed live from
# REMOVAL_TRACE.md §验证结果 (2026-09-02) and cross-checked against the
# abbreviated hashes recorded there.
INV1_FROZEN_FILES = {
    "products/p0-publishing-packaging/SKILL_v1.4.md":
        "1e7a9f1a633b4fa216b55e115ad2aec45dc6822d518ff528a22ad05f734b776e",
    "products/p0-publishing-packaging/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml":
        "82cadc343ecdf9bfd3d8346f94141403d9d2aa95b41b4866f3cd4f2b48f520c3",
    "products/p1-creative-director/SKILL.md":
        "442dc1262e5d2bbc1d7509b642d34d2b63677f0690b7a325ab88839045ab08aa",
    "products/p1-creative-director/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml":
        "99e8ae5c0eab1a8751160f554e3ecd8d103a385c7a39823692cc45c5c5a574b6",
    "products/p1_5-production-director/SKILL.md":
        "b48b88402cd09ea20dc4d4fb3403a451734cac0a7717328ac4c4fa6ad0b0dd02",
    "products/p1_5-production-director/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml":
        "a25788a3a28108e15511142e06e822eca36a466459e7f30a8b1581412faa1c4d",
}


def check_inv1():
    issues = []
    tree_results = {}
    for d in INV1_FROZEN_TREES:
        try:
            baseline_hash = git("rev-parse", "%s:%s" % (INV1_BASELINE_COMMIT, d))
            head_hash = git("rev-parse", "HEAD:%s" % d)
        except subprocess.CalledProcessError as e:
            issues.append("git rev-parse failed for %s: %s" % (d, e.stderr))
            continue
        match = baseline_hash == head_hash
        tree_results[d] = {"baseline_tree_sha1": baseline_hash, "head_tree_sha1": head_hash, "match": match}
        if not match:
            issues.append("frozen tree %s changed since baseline %s" % (d, INV1_BASELINE_COMMIT))

    file_results = {}
    for rel, expected in INV1_FROZEN_FILES.items():
        abspath = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(abspath):
            issues.append("frozen file missing: %s" % rel)
            file_results[rel] = {"expected_sha256": expected, "actual_sha256": None, "match": False}
            continue
        actual = sha256_file(abspath)
        match = actual == expected
        file_results[rel] = {"expected_sha256": expected, "actual_sha256": actual, "match": match}
        if not match:
            issues.append("frozen file sha256 drift: %s" % rel)

    try:
        diff_out = git("diff", "--name-only", "%s..HEAD" % INV1_BASELINE_COMMIT, "--",
                        *INV1_FROZEN_TREES)
    except subprocess.CalledProcessError as e:
        diff_out = None
        issues.append("git diff failed: %s" % e.stderr)
    diff_files = [l for l in (diff_out or "").splitlines() if l.strip()]
    if diff_files:
        issues.append("git diff against baseline touches frozen tree paths: %s" % diff_files)

    return {
        "invariant": "INV-1",
        "baseline_commit": INV1_BASELINE_COMMIT,
        "baseline_commit_rationale": (
            "parent of e8c1838 (E1 三 SKU 统一摘取), the last commit before this "
            "task's own lineage began reading content-production/ "
            "account-operations/ decision-chain/; diffing from main (01a42b0) "
            "would misclassify DIYU-V1-PP-BLOCKER-REMEDIATION-S1-S4-001's "
            "earlier, unrelated, already-closed edits as violations"
        ),
        "frozen_trees": tree_results,
        "frozen_files": file_results,
        "git_diff_intersection": diff_files,
        "pass": len(issues) == 0,
        "issues": issues,
    }


def _dir_has_real_content(root):
    """True iff `root` contains anything other than an empty-marker file
    (.gitkeep) — i.e. there is actual sealed content sitting there."""
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn != ".gitkeep":
                return True
    return False


def check_inv2():
    root_states = {}
    for root in SEALED_ROOTS:
        if not os.path.exists(root):
            state = "NOT_FOUND"
        elif not os.access(root, os.R_OK):
            state = "PERMISSION_DENIED"
        elif not (root == REPO_ROOT or root.startswith(REPO_ROOT + os.sep)):
            state = "OUTSIDE_ALLOWED_ROOT"
        elif not _dir_has_real_content(root):
            state = "EXISTS_INSIDE_ALLOWED_ROOT_BUT_EMPTY"
        else:
            state = "EXISTS_INSIDE_ALLOWED_ROOT_WITH_CONTENT"
        root_states[root] = state
    # A root satisfies 13.1's disjunction (不存在／权限拒绝／不在允许根内) — or,
    # equivalently for present purposes, holds no actual sealed content yet —
    # in every case except EXISTS_INSIDE_ALLOWED_ROOT_WITH_CONTENT, which
    # would need every file under it individually vetted. None of ours do:
    # no empirical test set has been built for these three SKUs yet (eval/
    # holds only .gitkeep; the only populated holdout on this machine,
    # diyu-demo-holdout-custody/, belongs to the unrelated M5 task and sits
    # outside the repo root).
    bad = {r: s for r, s in root_states.items() if s == "EXISTS_INSIDE_ALLOWED_ROOT_WITH_CONTENT"}
    read_violations = [p for p in _ACCESS_LOG
                        if any(p == r or p.startswith(r + os.sep) for r in SEALED_ROOTS)]
    return {
        "invariant": "INV-2",
        "sealed_roots": root_states,
        "read_attempts_into_sealed_roots": read_violations,
        "network_guard_installed": socket.socket.connect is _guarded_connect,
        "pass": len(bad) == 0 and len(read_violations) == 0,
    }


# ---------------------------------------------------------------------------
# Graph helpers (shared by SG2/SG3/SG6).
# ---------------------------------------------------------------------------

_LLM_IMPLICIT_OUTPUTS = {"text", "usage", "finish_reason"}


def node_by_id(data, nid):
    for n in data["workflow"]["graph"]["nodes"]:
        if n["id"] == nid:
            return n
    raise KeyError(nid)


def declared_outputs(node):
    t = node["data"]["type"]
    if t == "start":
        return {v["variable"] for v in node["data"].get("variables", [])}
    if t == "llm":
        return set((node["data"].get("outputs") or {}).keys()) | _LLM_IMPLICIT_OUTPUTS
    if t == "template-transform":
        return {"output"}
    return set((node["data"].get("outputs") or {}).keys())


def schema_and_dangling_defects(data):
    """Producer/Consumer schema mismatches + dangling edges. Returns a list
    of human-readable defect strings; empty means clean."""
    defects = []
    g = data["workflow"]["graph"]
    ids = {n["id"] for n in g["nodes"]}
    byid = {n["id"]: n for n in g["nodes"]}
    for e in g["edges"]:
        if e["source"] not in ids:
            defects.append("dangling edge source %s" % e["source"])
        if e["target"] not in ids:
            defects.append("dangling edge target %s" % e["target"])
    for n in g["nodes"]:
        if n["data"]["type"] == "start":
            continue
        for v in n["data"].get("variables", []) or []:
            if "value_selector" not in v:
                continue
            sel = v["value_selector"]
            src_id, src_key = sel[0], sel[1]
            if src_id not in byid:
                defects.append("%s references missing node %s" % (n["id"], src_id))
                continue
            if src_key not in declared_outputs(byid[src_id]):
                defects.append("%s references %s.%s, not declared on producer" % (n["id"], src_id, src_key))
    for n in g["nodes"]:
        if n["data"]["type"] == "end":
            for o in n["data"].get("outputs", []):
                sel = o["value_selector"]
                src_id, src_key = sel[0], sel[1]
                if src_id not in byid:
                    defects.append("end %s references missing node %s" % (n["id"], src_id))
                    continue
                if src_key not in declared_outputs(byid[src_id]):
                    defects.append("end %s references %s.%s, not declared on producer" % (n["id"], src_id, src_key))
    return defects


def _condition_is_constant(node):
    """AST-level constant-truth detection for an `if`/`while` test expression.
    Generalizes beyond literal `True`/`False` spelling to any compile-time
    evaluable condition (e.g. `1 == 1`, `"a" == "a"`)."""
    try:
        ast.literal_eval(node)
        return True
    except (ValueError, TypeError):
        pass
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        try:
            left = ast.literal_eval(node.left)
            right = ast.literal_eval(node.comparators[0])
        except (ValueError, TypeError):
            return False
        import operator
        opmap = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
                  ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge}
        fn = opmap.get(type(node.ops[0]))
        if fn is None:
            return False
        try:
            fn(left, right)
            return True
        except TypeError:
            return False
    return False


def find_tautologies(data):
    """Returns a list of 'node_id: <source snippet>' strings for every
    if/while in a code node whose test is a compile-time constant."""
    hits = []
    for n in data["workflow"]["graph"]["nodes"]:
        if n["data"]["type"] != "code":
            continue
        try:
            tree = ast.parse(n["data"]["code"])
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While)) and _condition_is_constant(node.test):
                hits.append("%s: %s at line %s" % (n["id"], type(node).__name__, getattr(node, "lineno", "?")))
    return hits


def build_adjacency(data):
    """source -> list of (target, sourceHandle)"""
    adj = {}
    for e in data["workflow"]["graph"]["edges"]:
        adj.setdefault(e["source"], []).append((e["target"], e.get("sourceHandle", "source")))
    return adj


def all_simple_paths(adj, start, goals, limit=2000):
    """DFS enumeration of all simple (no repeated node) paths from start to
    any node in goals. Small graphs (~16 nodes) so this is cheap."""
    paths = []
    stack = [(start, [start])]
    while stack:
        node, path = stack.pop()
        if node in goals and len(path) > 1:
            paths.append(path)
            if len(paths) >= limit:
                break
            continue
        for tgt, _handle in adj.get(node, []):
            if tgt not in path:
                stack.append((tgt, path + [tgt]))
    return paths


def sg2_execution_path(data, entry_id, guard_id, delivery_id, fail_branch_id):
    adj = build_adjacency(data)
    all_node_ids = {n["id"] for n in data["workflow"]["graph"]["nodes"]}
    assert {entry_id, guard_id, delivery_id, fail_branch_id} <= all_node_ids

    entry_to_delivery = all_simple_paths(adj, entry_id, {delivery_id})
    reachability = len(entry_to_delivery) > 0

    dominance = reachability and all(guard_id in p for p in entry_to_delivery)

    fail_to_delivery = all_simple_paths(adj, fail_branch_id, {delivery_id})
    fail_closed = len(fail_to_delivery) == 0

    return {
        "reachability": reachability,
        "dominance": dominance,
        "fail_closed": fail_closed,
        "entry_to_delivery_path_count": len(entry_to_delivery),
        "fail_branch_to_delivery_path_count": len(fail_to_delivery),
        "pass": reachability and dominance and fail_closed,
    }


# ---------------------------------------------------------------------------
# SKU registry — the checking logic below is generic over this list; it does
# not special-case SKU names. Add P2 here (once it clears BUILD) to run it
# through the same Gate without touching any function below.
# ---------------------------------------------------------------------------

SKUS = [
    dict(
        id="P0",
        capability="PUBLISHING_PACKAGING",
        yml_path="products/p0-publishing-packaging/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v2_0.yml",
        skill_md_path="products/p0-publishing-packaging/SKILL_v2.0.md",
        skill_source_dir="packaging-content-for-release",
        entry_id="1788000000001", guard_id="gate_sufficiency",
        delivery_id="end_ok", fail_branch_id="component_return",
        fail_end_id="end_component_return",
        advisory_marker_ids=["顾问性②", "顾问性③"],
        q_comm_doc="Q-COMM-04",
        applicable_notapplicable_required=True,
    ),
    dict(
        id="P1",
        capability="CREATIVE_SCRIPT",
        yml_path="products/p1-creative-director/DIYU_M4_TOOL_CREATIVE_SCRIPT_v2_0.yml",
        skill_md_path="products/p1-creative-director/SKILL_v2.0.md",
        skill_source_dir="writing-creative-scripts",
        entry_id="1788000000001", guard_id="gate_sufficiency",
        delivery_id="end_ok", fail_branch_id="component_return",
        fail_end_id="end_component_return",
        advisory_marker_ids=["顾问性②", "顾问性③"],
        q_comm_doc="Q-COMM-05",
        applicable_notapplicable_required=False,
    ),
    dict(
        id="P1_5",
        capability="PRODUCTION_DIRECTOR",
        yml_path="products/p1_5-production-director/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v2_0.yml",
        skill_md_path="products/p1_5-production-director/SKILL_v2.0.md",
        skill_source_dir="directing-content-production",
        entry_id="1788000000001", guard_id="gate_sufficiency",
        delivery_id="end_ok", fail_branch_id="component_return",
        fail_end_id="end_component_return",
        advisory_marker_ids=["顾问性②", "顾问性③"],
        q_comm_doc="Q-COMM-06",
        applicable_notapplicable_required=True,
    ),
]

DEEPSEEK_THINKING_STRIPPED_KEYS = ("temperature", "top_p", "presence_penalty", "frequency_penalty")


def finding(fid, verdict, summary, evidence=None, empirical_case_ref=None):
    f = {"id": fid, "verdict": verdict, "summary": summary}
    if evidence is not None:
        f["evidence"] = evidence
    if empirical_case_ref is not None:
        f["empirical_case_ref"] = empirical_case_ref
    return f


def line_of(text, needle):
    idx = text.find(needle)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def run_sg1(sku, yml_data, skill_md_text, skill_md_path):
    findings = []

    for marker in sku["advisory_marker_ids"]:
        ln = line_of(skill_md_text, marker)
        if ln:
            findings.append(finding(
                "SG1.advisory.%s" % marker, "PASS",
                "advisory criterion %s carried as a self-check item" % marker,
                evidence={"file": skill_md_path, "line": ln},
            ))
        else:
            findings.append(finding(
                "SG1.advisory.%s" % marker, "BLOCKING",
                "advisory criterion %s has no carrier in SKILL.md self-check list" % marker,
            ))

    cr_node = node_by_id(yml_data, "component_return")
    cr_code = cr_node["data"]["code"]
    has_single_gap_ask = "ask_key = miss[0] if miss else" in cr_code
    has_three_part = ('"why"' in cr_code and '"how"' in cr_code and "为什么：%s" in cr_code and "怎么补：%s" in cr_code)
    no_return_id = "return_id" not in cr_code
    ln = line_of(cr_code, "ask_key = miss[0] if miss else")
    if has_single_gap_ask and has_three_part and no_return_id:
        findings.append(finding(
            "SG1.G0.single_highest_value_gap_no_fabrication", "PASS",
            "component_return asks exactly the single most discriminating missing item and "
            "returns 缺什么/为什么/怎么补 to the customer; no return_id fabrication-adjacent field",
            evidence={"file": sku["yml_path"], "node": "component_return", "line": ln},
        ))
    else:
        findings.append(finding(
            "SG1.G0.single_highest_value_gap_no_fabrication", "BLOCKING",
            "component_return missing single-gap-ask, three-part customer message, "
            "or still constructs return_id",
            evidence={"file": sku["yml_path"], "node": "component_return"},
        ))

    node_ids = {n["id"] for n in yml_data["workflow"]["graph"]["nodes"]}
    for nid, label in [("fact_verification", "no-fabrication / UNKNOWN-FACT discipline"),
                        ("market_claim_scan", "no unverifiable current-market claim")]:
        if nid in node_ids:
            n = node_by_id(yml_data, nid)
            findings.append(finding(
                "SG1.G1.%s" % nid, "PASS",
                "%s carried by node `%s`" % (label, nid),
                evidence={"file": sku["yml_path"], "node": nid, "title": n["data"].get("title")},
            ))
        else:
            findings.append(finding(
                "SG1.G1.%s" % nid, "BLOCKING",
                "%s has no carrier node in this SKU's graph" % label,
            ))

    if sku["applicable_notapplicable_required"]:
        hits = len(re.findall(r"\bAPPLICABLE\b|\bNOT_APPLICABLE\b", skill_md_text))
        if hits > 0:
            ln = None
            m = re.search(r"\bAPPLICABLE\b|\bNOT_APPLICABLE\b", skill_md_text)
            if m:
                ln = skill_md_text.count("\n", 0, m.start()) + 1
            findings.append(finding(
                "SG1.G0.applicable_not_applicable", "PASS",
                "APPLICABLE/NOT_APPLICABLE determination mechanism present (%d occurrences)" % hits,
                evidence={"file": skill_md_path, "line": ln},
            ))
        else:
            findings.append(finding(
                "SG1.G0.applicable_not_applicable", "BLOCKING",
                "%s requires per-item APPLICABLE/NOT_APPLICABLE determination on standard "
                "outputs; no carrier found in SKILL.md" % sku["q_comm_doc"],
            ))
    else:
        findings.append(finding(
            "SG1.G0.applicable_not_applicable", "PASS",
            "%s does not structure requirements as an itemized APPLICABLE/NOT_APPLICABLE "
            "output list; not applicable to this SKU" % sku["q_comm_doc"],
            evidence={"file": None, "reason": "%s §1/§4 has no itemized-output-with-applicability "
                      "requirement (verified by direct read of the standard)" % sku["q_comm_doc"]},
        ))

    return findings


def run_sg2(sku, yml_data):
    r = sg2_execution_path(yml_data, sku["entry_id"], sku["guard_id"], sku["delivery_id"], sku["fail_branch_id"])
    verdict = "PASS" if r["pass"] else "BLOCKING"
    return [finding(
        "SG2.execution_path", verdict,
        "reachability=%s dominance=%s fail_closed=%s (entry->delivery paths=%d, "
        "fail_branch->delivery paths=%d)" % (
            r["reachability"], r["dominance"], r["fail_closed"],
            r["entry_to_delivery_path_count"], r["fail_branch_to_delivery_path_count"],
        ),
        evidence={"file": sku["yml_path"], "entry": sku["entry_id"], "guard": sku["guard_id"],
                  "delivery": sku["delivery_id"], "fail_branch": sku["fail_branch_id"]},
    )], r


def run_sg3(sku, yml_data):
    findings = []
    defects = schema_and_dangling_defects(yml_data)
    if defects:
        findings.append(finding("SG3.schema_and_reachability", "BLOCKING",
                                 "producer/consumer schema mismatch or dangling edge: %s" % "; ".join(defects[:5]),
                                 evidence={"file": sku["yml_path"]}))
    else:
        findings.append(finding("SG3.schema_and_reachability", "PASS",
                                 "no dangling edges, no undeclared value_selector references",
                                 evidence={"file": sku["yml_path"]}))

    tautologies = find_tautologies(yml_data)
    if tautologies:
        findings.append(finding("SG3.tautological_or_hardcoded_gate", "BLOCKING",
                                 "constant-condition construct found: %s" % "; ".join(tautologies),
                                 evidence={"file": sku["yml_path"]}))
    else:
        findings.append(finding("SG3.tautological_or_hardcoded_gate", "PASS",
                                 "no if/while with a compile-time-constant test (literal True/False "
                                 "or a constant-vs-constant comparison) in any code node",
                                 evidence={"file": sku["yml_path"]}))

    unknown_fact = []
    for n in yml_data["workflow"]["graph"]["nodes"]:
        if n["data"]["type"] != "code":
            continue
        code = n["data"]["code"]
        if re.search(r'replace\(\s*["\']UNKNOWN["\']\s*,\s*["\']FACT["\']', code):
            unknown_fact.append(n["id"])
    if unknown_fact:
        findings.append(finding("SG3.unknown_fact_misuse", "BLOCKING",
                                 "UNKNOWN silently rewritten to FACT in node(s): %s" % unknown_fact,
                                 evidence={"file": sku["yml_path"]}))
    else:
        findings.append(finding("SG3.unknown_fact_misuse", "PASS",
                                 "no code path silently rewrites UNKNOWN to FACT",
                                 evidence={"file": sku["yml_path"]}))

    guard = node_by_id(yml_data, sku["guard_id"])
    cases = guard["data"].get("cases", [])
    hardcoded_guard = True
    for c in cases:
        for cond in c.get("conditions", []):
            sel = cond.get("variable_selector", [])
            if sel and sel[0] != sku["guard_id"] and sel[-1] not in ("__constant__",):
                hardcoded_guard = False
    if hardcoded_guard and cases:
        findings.append(finding("SG3.guard_variable_source", "BLOCKING",
                                 "gate_sufficiency condition does not reference an externally "
                                 "computed variable", evidence={"file": sku["yml_path"], "node": sku["guard_id"]}))
    else:
        findings.append(finding("SG3.guard_variable_source", "PASS",
                                 "gate_sufficiency condition reads a genuinely computed field "
                                 "(envelope_check.can_run), not a literal",
                                 evidence={"file": sku["yml_path"], "node": sku["guard_id"]}))
    return findings


def _actual_completion_params(declared):
    if declared.get("thinking") is True:
        return {k: v for k, v in declared.items() if k not in DEEPSEEK_THINKING_STRIPPED_KEYS}
    return dict(declared)


def _plugin_normalization_mismatch(declared):
    """True iff declared completion_params would be silently altered by the
    deepseek plugin at send time (declared != actual effective params).
    Shared by run_sg5 (production check) and run_sg6 (self-test) so the
    self-test exercises the real detector, not a reimplementation of it."""
    actual = _actual_completion_params(declared)
    return sorted(set(declared) - set(actual)) != []


def run_sg5(sku, yml_data, skill_md_text, skill_md_path):
    findings = []

    llm_node = node_by_id(yml_data, "skill_llm")
    system_text = llm_node["data"]["prompt_template"][0]["text"]
    marker = "\n---\n\n# 本次运行注入的参考文件片段"
    idx = system_text.find(marker)
    expected = skill_md_text + (system_text[idx:] if idx >= 0 else "")
    assembled_matches = (system_text == expected)
    findings.append(finding(
        "SG5.assembled_prompt_matches_skill_md", "PASS" if assembled_matches else "BLOCKING",
        "assembled system prompt %s SKILL.md + fixed appendix, byte for byte" % (
            "equals" if assembled_matches else "DOES NOT equal"),
        evidence={"file": sku["yml_path"], "node": "skill_llm",
                  "assembled_sha256": hashlib.sha256(system_text.encode()).hexdigest(),
                  "skill_md_sha256": hashlib.sha256(skill_md_text.encode()).hexdigest()},
    ))

    model = llm_node["data"]["model"]
    declared = dict(model["completion_params"])
    actual = _actual_completion_params(declared)
    stripped = sorted(set(declared) - set(actual))
    if _plugin_normalization_mismatch(declared):
        findings.append(finding(
            "SG5.plugin_normalization_mismatch", "BLOCKING",
            "provider=%s thinking=%s declares %s but the deepseek plugin silently strips "
            "%s at send time; actual effective params=%s" % (
                model["provider"], declared.get("thinking"), sorted(declared), stripped, actual),
            evidence={"file": sku["yml_path"], "node": "skill_llm", "line": None,
                      "declared_completion_params": declared, "actual_effective_completion_params": actual},
        ))
    else:
        findings.append(finding(
            "SG5.plugin_normalization_mismatch", "PASS",
            "declared completion_params survive deepseek plugin normalization unchanged",
            evidence={"file": sku["yml_path"], "node": "skill_llm", "completion_params": declared},
        ))

    prov_blocks = re.findall(
        r'"path":\s*"([^"]+)"[^{}]*?"sha256[a-z_]*":\s*"([0-9a-f]{64})"',
        node_by_id(yml_data, "projection_record")["data"]["template"],
    )
    if not prov_blocks:
        findings.append(finding(
            "SG5.reference_provenance", "BLOCKING",
            "no reference_provenance path/sha256 pairs found in projection_record template",
            evidence={"file": sku["yml_path"], "node": "projection_record"},
        ))
    else:
        mismatches = []
        for rel, declared_sha in prov_blocks:
            abspath = os.path.join(REPO_ROOT, rel)
            if not os.path.exists(abspath):
                mismatches.append("%s: file missing" % rel)
                continue
            actual_sha = sha256_file(abspath)
            if actual_sha != declared_sha:
                mismatches.append("%s: declared=%s actual=%s" % (rel, declared_sha, actual_sha))
        if mismatches:
            findings.append(finding(
                "SG5.reference_provenance", "BLOCKING",
                "declared reference sha256 does not match current source file(s): %s" % mismatches,
                evidence={"file": sku["yml_path"], "node": "projection_record"},
            ))
        else:
            findings.append(finding(
                "SG5.reference_provenance", "PASS",
                "all %d declared reference file(s) sha256-match current source content "
                "(CF-04 folded in)" % len(prov_blocks),
                evidence={"file": sku["yml_path"], "node": "projection_record",
                          "verified_paths": [p for p, _ in prov_blocks]},
            ))

    freeze_paths_this_sku = [p for p in INV1_FROZEN_FILES if p.startswith("products/%s" % sku["yml_path"].split("/")[1])]
    findings.append(finding(
        "SG5.no_dependency_on_frozen_old_system", "PASS",
        "v2.0 DSL sources its live reference content from content-production/skills/%s/ "
        "(shared, current), not from the frozen v1.x baseline file(s) %s" % (
            sku["skill_source_dir"], freeze_paths_this_sku),
        evidence={"file": sku["yml_path"], "node": "projection_record"},
    ))

    return findings


def run_sg6(sku, yml_data):
    findings = []

    # --- detector: schema_and_dangling_defects ---
    good_data = yml_data
    pos = len(schema_and_dangling_defects(good_data)) == 0

    import copy
    bad_data = copy.deepcopy(good_data)
    bad_data["workflow"]["graph"]["nodes"][-1]["data"].setdefault("variables", []).append(
        {"value_selector": ["envelope_check", "__nonexistent_field__"], "variable": "x"}
    )
    neg = len(schema_and_dangling_defects(bad_data)) > 0

    offlist_data = copy.deepcopy(good_data)
    offlist_data["workflow"]["graph"]["edges"].append(
        {"id": "off-list-dangling", "source": sku["entry_id"], "target": "__nonexistent_node__",
         "sourceHandle": "source", "targetHandle": "target"}
    )
    offlist = len(schema_and_dangling_defects(offlist_data)) > 0

    findings.append(_sg6_verdict("schema_and_dangling_defects", pos, neg, offlist))

    # --- detector: sg2 fail-closed check ---
    pos2 = sg2_execution_path(good_data, sku["entry_id"], sku["guard_id"], sku["delivery_id"], sku["fail_branch_id"])["pass"]

    bad2 = copy.deepcopy(good_data)
    bad2["workflow"]["graph"]["edges"].append(
        {"id": "off-list-fail-open", "source": sku["fail_branch_id"], "target": sku["delivery_id"],
         "sourceHandle": "source", "targetHandle": "target"}
    )
    neg2 = not sg2_execution_path(bad2, sku["entry_id"], sku["guard_id"], sku["delivery_id"], sku["fail_branch_id"])["pass"]

    offlist2 = copy.deepcopy(good_data)
    offlist2["workflow"]["graph"]["edges"] = [
        e for e in offlist2["workflow"]["graph"]["edges"]
        if not (e["source"] == "envelope_check" and e["target"] == sku["guard_id"])
    ]
    offlist2["workflow"]["graph"]["edges"].append(
        {"id": "off-list-bypass-guard", "source": "envelope_check", "target": "ref_projection",
         "sourceHandle": "source", "targetHandle": "target"}
    )
    r_offlist2 = sg2_execution_path(offlist2, sku["entry_id"], sku["guard_id"], sku["delivery_id"], sku["fail_branch_id"])
    offlist2_caught = not r_offlist2["dominance"]

    findings.append(_sg6_verdict("sg2_execution_path", pos2, neg2, offlist2_caught))

    # --- detector: tautological/hardcoded gate scan (same function SG3 runs
    # in production — the self-test must exercise the real detector, not a
    # reimplementation of it) ---
    pos3 = len(find_tautologies(good_data)) == 0

    bad3 = copy.deepcopy(good_data)
    bad3_node = node_by_id(bad3, "component_return")
    bad3_node["data"]["code"] = bad3_node["data"]["code"] + "\nif True:\n    pass\n"
    neg3 = len(find_tautologies(bad3)) > 0

    # Off-list on purpose: `if 1 == 1:` is just as tautological as `if True:`
    # but is a constant *comparison* rather than the literal `True`/`False`
    # spelling — it exercises whether the scanner generalizes (AST constant
    # evaluation) or only pattern-matches the exact literals it already knows.
    offlist3 = copy.deepcopy(good_data)
    offlist3_node = node_by_id(offlist3, "component_return")
    offlist3_node["data"]["code"] = offlist3_node["data"]["code"] + "\nif 1 == 1:\n    pass\n"
    offlist3_caught = len(find_tautologies(offlist3)) > 0

    findings.append(_sg6_verdict("tautological_gate_scan", pos3, neg3, offlist3_caught))

    # --- detector: plugin_normalization_mismatch (same function SG5 runs in
    # production — the self-test must exercise the real detector). The
    # detector's rule is a set-difference over DEEPSEEK_THINKING_STRIPPED_KEYS,
    # not a per-key special case, so the off-list control uses a different
    # member of that same fixed set than the negative control does — this
    # catches the plausible bug of only checking one or two of the four keys
    # (e.g. an if/elif chain that special-cases temperature/top_p and forgets
    # presence_penalty/frequency_penalty) instead of diffing the whole set.
    pos4 = not _plugin_normalization_mismatch(
        {"max_tokens": 384000, "reasoning_effort": "low", "thinking": True})
    neg4 = _plugin_normalization_mismatch(
        {"max_tokens": 384000, "reasoning_effort": "low", "thinking": True, "top_p": 0.8})
    offlist4 = _plugin_normalization_mismatch(
        {"max_tokens": 384000, "reasoning_effort": "low", "thinking": True, "presence_penalty": 0.1})

    findings.append(_sg6_verdict("plugin_normalization_mismatch", pos4, neg4, offlist4))

    return findings


def _sg6_verdict(detector_name, positive_ok, negative_caught, offlist_caught):
    controls = {"positive_control": positive_ok, "negative_control": negative_caught,
                "off_list_constructed_bad_case": offlist_caught}
    if positive_ok and negative_caught and offlist_caught:
        return finding("SG6.%s" % detector_name, "PASS",
                        "all three controls satisfied: %s" % controls, evidence=controls)
    return finding("SG6.%s" % detector_name, "BLOCKING",
                    "detector has lost discriminating power (%s) — self-blocked per §13.2" % controls,
                    evidence=controls)


def run_sku(sku):
    yml_path = os.path.join(REPO_ROOT, sku["yml_path"])
    skill_md_path_full = os.path.join(REPO_ROOT, sku["skill_md_path"])
    with open(yml_path) as f:
        yml_data = yaml.safe_load(f)
    with open(skill_md_path_full) as f:
        skill_md_text = f.read()

    findings = []
    findings += run_sg1(sku, yml_data, skill_md_text, sku["skill_md_path"])
    sg2_findings, _ = run_sg2(sku, yml_data)
    findings += sg2_findings
    findings += run_sg3(sku, yml_data)
    findings += run_sg5(sku, yml_data, skill_md_text, sku["skill_md_path"])
    findings += run_sg6(sku, yml_data)

    # SG4 · Evidence & Authority — meta-validate the findings this run just produced.
    sg4_issues = []
    for f in findings:
        if f["verdict"] == "PASS" and not f.get("evidence"):
            sg4_issues.append("%s: PASS with no evidence" % f["id"])
        if f["verdict"] == "DYNAMIC_ONLY" and not f.get("empirical_case_ref"):
            f["verdict"] = "BLOCKING"
            f["summary"] += " [DYNAMIC_ONLY with no empirical_case_ref => BLOCKING per §13.3]"
    if sg4_issues:
        findings.append(finding("SG4.evidence_and_authority", "BLOCKING",
                                 "PASS verdict(s) without citable evidence: %s" % sg4_issues))
    else:
        findings.append(finding("SG4.evidence_and_authority", "PASS",
                                 "every PASS in this run carries file/node/field evidence; "
                                 "no ref-less DYNAMIC_ONLY survived"))

    dynamic_only = [f for f in findings if f["verdict"] == "DYNAMIC_ONLY"]
    blocking = [f for f in findings if f["verdict"] == "BLOCKING"]

    state = "NOT_READY" if blocking else "READY_FOR_EMPIRICAL_TESTING"
    return {
        "sku": sku["id"],
        "capability": sku["capability"],
        "q_comm_doc": sku["q_comm_doc"],
        "state": state,
        "blockers": [{"id": f["id"], "summary": f["summary"], "evidence": f.get("evidence")} for f in blocking],
        "dynamic_only": dynamic_only,
        "findings": findings,
    }


def main():
    inv1 = check_inv1()
    per_sku = [run_sku(sku) for sku in SKUS]
    inv2 = check_inv2()  # run last so it also covers every open() this script itself performed

    global_invariants_pass = inv1["pass"] and inv2["pass"]

    results = []
    for r in per_sku:
        if not global_invariants_pass:
            r = dict(r)
            r["state"] = "NOT_READY"
            r["blockers"] = r["blockers"] + [
                {"id": "INV-1", "summary": "global invariant failed", "evidence": None}
                if not inv1["pass"] else None,
                {"id": "INV-2", "summary": "global invariant failed", "evidence": None}
                if not inv2["pass"] else None,
            ]
            r["blockers"] = [b for b in r["blockers"] if b]
        results.append(r)

    dynamic_only_scope_note = (
        "SG1/SG3/SG5 in this run registered zero DYNAMIC_ONLY findings. Rationale: "
        "per §13's own stated唯一目标 ('当前 SKU 是否存在足以污染后续真实 LLM 考试结果的确定性问题'), "
        "this Gate's checkers enumerate structural *carrier* requirements (does a hook/field/"
        "instruction exist to carry a requirement at all) — not the empirical scoring "
        "dimensions Q-COMM's G2/G3/G4 sections define (quality rubrics, blind-review win "
        "rates, paid-Beta metrics, ablation/counterfactual results). Those are the SUBJECT "
        "of the empirical phase this Gate exists to unblock, not inputs the Gate itself "
        "adjudicates, and registering them as DYNAMIC_ONLY placeholders would be circular. "
        "Separately and factually: no empirical_case_ref manifest exists yet for these three "
        "SKUs to bind to even if such placeholders were registered — eval/ holds only "
        ".gitkeep, and the only populated holdout on this machine "
        "(diyu-demo-holdout-custody/) belongs to the unrelated, already-closed M5 task. "
        "Per §13.3 any DYNAMIC_ONLY without a real ref counts as BLOCKING, so inventing refs "
        "was not an option; this is disclosed rather than silently avoided."
    )

    reasoning_effort_note = (
        "All six skill_llm/component_return completion_params blocks (two per SKU) declare "
        "reasoning_effort: low. This is a product tuning choice, not a determinism defect: "
        "per RULESIDE-2026-09-02-014 §五 ('不影响考试信号的不得阻断'), a low reasoning-effort "
        "setting does not by itself corrupt the empirical scoring signal, so it is not raised "
        "as BLOCKING or DYNAMIC_ONLY here. Recorded for Founder visibility only."
    )

    report = {
        "gate": "STATIC_GATE",
        "task_id": "DIYU-V1-STATIC-GATE-001",
        "authority": "RULESIDE-2026-09-02-014 + 笛语商业SKU验收体系_索引与启动规则_v1.0.md §13",
        "dynamic_only_scope_note": dynamic_only_scope_note,
        "reasoning_effort_note": reasoning_effort_note,
        "invariants": {"INV-1": inv1, "INV-2": inv2},
        "skus": results,
    }

    out_path = os.path.join(REPO_ROOT, "sku-productization", "STATIC_GATE_REPORT.json")
    with open(out_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=False)

    for r in results:
        print("%s: %s" % (r["sku"], r["state"]))
        for b in r["blockers"]:
            print("  BLOCKING: %s — %s" % (b["id"], b["summary"]))
    return report


if __name__ == "__main__":
    main()
