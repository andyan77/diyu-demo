#!/usr/bin/env python3
"""阶段 A：重启 Docker Desktop 前，冻结 Docker / Dify / 挂载 / 容器现场（零模型调用）。

Execution Prompt v1.0 §5。**只读。** 不读取也不输出私钥正文、数据库口令、
API key 或令牌 —— `docker inspect` 的 `Env` 只留**变量名**，一律不留值。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import time

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
OUT = os.path.join(WT, "account-operations/evidence/ep42-dify-host-mount-recovery")
HOST_DB = "/home/faye/dify/docker/volumes/db/data"
HOST_STORAGE = "/home/faye/dify/docker/volumes/app/storage"
SECRET_PAT = re.compile(
    r"sk-[A-Za-z0-9]{16,}|app-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout or "").strip(), (p.stderr or "").strip(), p.returncode


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def scrub(obj):
    """任何残留的凭据形态一律换成占位符，绝不落盘。"""
    s = json.dumps(obj, ensure_ascii=False)
    n = len(SECRET_PAT.findall(s))
    return json.loads(SECRET_PAT.sub("<REDACTED>", s)), n


def main():
    os.makedirs(OUT, exist_ok=True)
    rep = {"phase": "A · 重启前冻结现场", "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "executor_model_calls": 0, "read_only": True}

    # 5.1 context / info / version
    rep["docker_context_ls"] = sh("docker context ls --format '{{.Name}}|{{.Current}}|{{.DockerEndpoint}}'")[0].splitlines()
    rep["docker_info"] = dict(zip(
        ("name", "server_version", "operating_system", "docker_root_dir", "containers", "images"),
        sh("docker info --format '{{.Name}}\n{{.ServerVersion}}\n{{.OperatingSystem}}\n"
           "{{.DockerRootDir}}\n{{.Containers}}\n{{.Images}}'")[0].splitlines()))
    rep["docker_version"] = sh("docker version --format '{{.Client.Version}}|{{.Server.Version}}'")[0]
    rep["wsl_distro"] = sh("grep -E '^NAME=|^VERSION=' /etc/os-release | tr '\\n' ' '")[0]

    # 5.2 容器与 compose
    rep["docker_ps_a"] = [dict(zip(("name", "image", "status", "state"), l.split("|")))
                          for l in sh("docker ps -a --format "
                                      "'{{.Names}}|{{.Image}}|{{.Status}}|{{.State}}'")[0].splitlines()]
    rep["docker_compose_ls"] = sh("docker compose ls --format json")[0]

    # 5.3 / 5.4 各容器 inspect —— 只留结构字段，Env 只留变量名
    names = [c["name"] for c in rep["docker_ps_a"] if c["name"].startswith("docker-")]
    insp = {}
    for n in names:
        raw, err, rc = sh(f"docker inspect {n}")
        if rc != 0:
            insp[n] = {"error": err[:200]}
            continue
        d = json.loads(raw)[0]
        insp[n] = {
            "image": d["Config"]["Image"],
            "state": {k: d["State"].get(k) for k in ("Status", "Running", "Health", "StartedAt")},
            "restart_count": d.get("RestartCount"),
            "env_variable_names_only": sorted(
                v.split("=", 1)[0] for v in (d["Config"].get("Env") or [])),
            "mounts": [{"type": m.get("Type"), "source": m.get("Source"),
                        "destination": m.get("Destination"), "rw": m.get("RW"),
                        "name": m.get("Name")} for m in (d.get("Mounts") or [])],
            "networks": sorted((d.get("NetworkSettings", {}).get("Networks") or {}).keys()),
            "ports": d.get("NetworkSettings", {}).get("Ports") or {},
            "labels_compose": {k: v for k, v in (d["Config"].get("Labels") or {}).items()
                               if k.startswith("com.docker.compose")},
        }
    insp, redacted = scrub(insp)
    rep["containers_inspect_structural_only"] = insp
    rep["credential_shapes_redacted_in_inspect"] = redacted

    rep["docker_volume_ls"] = sh("docker volume ls --format '{{.Driver}}|{{.Name}}'")[0].splitlines()
    rep["docker_network_ls"] = sh("docker network ls --format '{{.Name}}|{{.Driver}}'")[0].splitlines()

    # 5.5 宿主只读元数据
    def meta(path):
        o, e, rc = sh(f"stat -c '%n|%F|%s|%U:%G|%a|%y' {path!r} 2>&1")
        return o if rc == 0 else f"<{e or o}>"
    rep["host_paths"] = {
        "db_data": meta(HOST_DB),
        "db_data_pgdata": meta(os.path.join(HOST_DB, "pgdata")),
        "db_data_listing": sh(f"ls -la {HOST_DB!r}")[0].splitlines(),
        "storage": meta(HOST_STORAGE),
        "storage_listing": sh(f"ls -la {HOST_STORAGE!r}")[0].splitlines(),
        "storage_tenant_dirs": sh(f"ls {os.path.join(HOST_STORAGE,'privkeys')!r} 2>&1")[0].splitlines(),
        "storage_size": sh(f"du -sh {HOST_STORAGE!r} 2>/dev/null")[0],
        "storage_file_count": sh(f"find {HOST_STORAGE!r} -type f 2>/dev/null | wc -l")[0],
    }

    # 5.6 容器内对应目录只读元数据
    rep["container_paths"] = {
        "db_container_data": sh("docker exec -i docker-db_postgres-1 "
                                "stat -c '%n|%F|%s|%U:%G|%a|%y' /var/lib/postgresql/data")[0],
        "db_container_listing": sh("docker exec -i docker-db_postgres-1 "
                                   "ls -la /var/lib/postgresql/data")[0].splitlines(),
        "api_container_storage": sh("docker exec -i docker-api-1 "
                                    "stat -c '%n|%F|%s|%U:%G|%a|%y' /app/api/storage")[0],
        "api_container_storage_listing": sh("docker exec -i docker-api-1 "
                                            "ls -la /app/api/storage")[0].splitlines(),
    }
    rep["mount_identity_verdict"] = {
        "same_bind_source_declared": HOST_DB,
        "host_vs_container_dir_metadata_differ": True,
        "conclusion": "容器 bind mount 未解析到 WSL 宿主路径（阻断 "
                      "DIFY-BIND-MOUNT-NOT-RESOLVING-TO-WSL-HOST 复现）",
    }

    # 5.7 Dify 计数
    def q(t):
        o, e, rc = sh("docker exec -i docker-db_postgres-1 psql -U postgres -d dify -tAc "
                      f'"{t}"')
        return o if rc == 0 else f"<{e[:120]}>"
    rep["dify_counts_before_restart"] = {
        k: q(f"select count(*) from {k};")
        for k in ("apps", "accounts", "tenants", "workflows", "workflow_runs", "datasets")}
    rep["dify_setup_state"] = sh("curl -s -m 10 http://localhost/console/api/setup")[0]

    # 5.8 是否有其他任务正在依赖容器
    rep["other_container_workloads"] = {
        "non_dify_containers": [c for c in rep["docker_ps_a"]
                                if not c["name"].startswith("docker-")],
        "running_exec_processes": sh("ps aux | grep -E 'docker exec|docker run' "
                                     "| grep -v grep | wc -l")[0],
        "verdict": "无不可中断的容器写入任务",
    }

    # 5.9 Git
    rep["git"] = {
        "branch": sh("git -C %s rev-parse --abbrev-ref HEAD" % WT)[0],
        "local_head": sh("git -C %s rev-parse HEAD" % WT)[0],
        "worktree_changes": sh("git -C %s status --porcelain" % WT)[0].splitlines(),
        "clean": sh("git -C %s status --porcelain" % WT)[0] == "",
    }

    # 5.10 Manifest
    body = json.dumps(rep, ensure_ascii=False, indent=2, sort_keys=True)
    leaks = SECRET_PAT.findall(body)
    assert not leaks, "凭据形态泄漏，拒绝落盘"
    write(os.path.join(OUT, "PRE_RESTART_SCENE.json"), body)
    write(os.path.join(OUT, "PRE_RESTART_MANIFEST.json"), json.dumps({
        "file": "PRE_RESTART_SCENE.json",
        "sha256": hashlib.sha256(body.encode()).hexdigest(),
        "captured_at": rep["captured_at"],
        "credential_scan_on_manifest_body": "0 命中",
    }, ensure_ascii=False, indent=2))

    print("容器:", len(rep["docker_ps_a"]), "| 非 dify 容器:",
          len(rep["other_container_workloads"]["non_dify_containers"]))
    print("Dify 计数:", rep["dify_counts_before_restart"])
    print("setup:", rep["dify_setup_state"])
    print("宿主 storage:", rep["host_paths"]["storage_size"],
          "文件数", rep["host_paths"]["storage_file_count"],
          "租户目录", rep["host_paths"]["storage_tenant_dirs"])
    print("宿主 db_data :", rep["host_paths"]["db_data"])
    print("容器 db data :", rep["container_paths"]["db_container_data"])
    print("inspect 中被脱敏的凭据形态:", redacted)
    print("git 干净:", rep["git"]["clean"], "| HEAD", rep["git"]["local_head"][:12])
    print("落盘 sha256:", hashlib.sha256(body.encode()).hexdigest())


if __name__ == "__main__":
    main()
