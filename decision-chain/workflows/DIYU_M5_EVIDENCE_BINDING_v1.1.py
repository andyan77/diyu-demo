#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 正式证据绑定 v1.1 —— 正式产物只能按**显式路径 + SHA-256**取，不许猜。

为什么要有这个文件：

v1.0 的三个构建器都用 `sorted(glob.glob(...))[-1]` 选「最新」证据。正式产物的标签
是大写 `F`（`deF`/`riskF`/`m2pF`/`full01F1`/`abF`），而 ASCII 排序里大写排在小写前面，
于是 `[-1]` **永远选不到正式文件**，稳定地选到冻结前的诊断跑。这不是偶尔选错一个，
是系统性反选：正式证据索引里出现的 `dea`/`full01i`/`m2pb`/`riskd` 全是诊断件，
盲评包拿到的是 `AB_BLIND_aba` 而不是 `AB_BLIND_abF`。

「最新」「最好」「排最后」都是猜。冻结的正式运行知道自己写了哪些文件，
把它们连同哈希写进清单，构建器只按清单取——取不到、对不上就非零退出，
不许降级成猜一个。
"""
import hashlib
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# 正式证据的键。键是**语义位置**，不是文件名——文件名带 run tag，会变；语义位置不变。
KEYS = ("FULL_STORY", "DIRECT_ENTRY", "RISK_PROBE", "M2_PROBE",
        "REGRESSION", "AB_RAW", "AB_BLIND", "AB_SEALED")


class EvidenceBindingError(Exception):
    """绑定不成立。**只准抛，不准降级**——降级成猜就是本文件要消灭的那个缺陷。"""


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def build(manifest_path, candidate_commit, frozen_at, entries, run_tag=None, note=""):
    """把本次正式运行**实际写出**的文件连同哈希固定下来。

    entries: {KEY: 仓库相对路径}。文件必须已经在场——清单不预告未来，只记录已发生。
    """
    unknown = [k for k in entries if k not in KEYS]
    if unknown:
        raise EvidenceBindingError("未知证据键：%s；合法键：%s" % (unknown, list(KEYS)))
    out = {}
    for key, rel in entries.items():
        ab = os.path.join(ROOT, rel)
        if not os.path.exists(ab):
            raise EvidenceBindingError("清单要绑定的文件不在场：%s -> %s" % (key, rel))
        out[key] = {"path": rel, "sha256": sha256_file(ab),
                    "bytes": os.path.getsize(ab)}
    man = {"manifest_id": "M5-FORMAL-EVIDENCE-MANIFEST-v1.1",
           "task_id": "DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001",
           "candidate_commit": candidate_commit, "frozen_at": frozen_at,
           "run_tag": run_tag, "note": note,
           "selection_rule": "构建器只按本清单的显式路径与 sha256 取证据；"
                             "禁止 glob / 排序 / 「最新」「最好」推断",
           "entries": out}
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
    return man


def load(manifest_path):
    """读清单并**当场复算**每个文件的哈希。对不上就抛，不返回半份可用的绑定。"""
    if not manifest_path or not os.path.exists(manifest_path):
        raise EvidenceBindingError(
            "没有正式证据清单：%s。正式包必须由清单绑定，不接受由构建器自行挑文件。"
            % manifest_path)
    man = json.load(open(manifest_path, encoding="utf-8"))
    bad = []
    for key, e in (man.get("entries") or {}).items():
        ab = os.path.join(ROOT, e["path"])
        if not os.path.exists(ab):
            bad.append("%s 文件不在场：%s" % (key, e["path"]))
            continue
        got = sha256_file(ab)
        if got != e["sha256"]:
            bad.append("%s 哈希不一致：清单 %s，现场 %s（%s）"
                       % (key, e["sha256"][:16], got[:16], e["path"]))
    if bad:
        raise EvidenceBindingError("正式证据绑定不成立：\n  - " + "\n  - ".join(bad))
    return man


def path_of(man, key):
    e = (man.get("entries") or {}).get(key)
    if not e:
        raise EvidenceBindingError("清单里没有绑定 %s；本次正式运行没有产出它，就不能凭空引用。" % key)
    return os.path.join(ROOT, e["path"])


def load_json(man, key):
    return json.load(open(path_of(man, key), encoding="utf-8"))


def source_name(man, key):
    return os.path.basename((man["entries"][key])["path"])


def cli_manifest(argv, env_key="M5_FORMAL_EVIDENCE_MANIFEST"):
    """从 --manifest / 环境变量取清单路径。**取不到就是取不到**，不回退到 glob。"""
    for i, a in enumerate(argv):
        if a == "--manifest" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--manifest="):
            return a.split("=", 1)[1]
    return os.environ.get(env_key)
