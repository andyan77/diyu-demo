# Codex 路径问题交接记录（2026-08-19）

## 用户明确要求

- 正确项目目录是 `/home/faye/diyu-demo`。
- `笛语demo` 是曾经误用的文件夹名，后来已改为 `diyu-demo`；不要改回中文名。
- 不要因为本问题删除 WSL 迁移备份、再次迁移 VHD，或修改项目文件。
- 当前旧对话上下文已接近上限，新窗口应读取本文件后继续处理。

## 已确认的当前事实

- 当前 WSL 发行版：`ubuntu-22.04`（WSL2）。
- 当前活跃 WSL 磁盘注册位置：`D:\\wsl\\Ubuntu\\ext4.vhdx`。
- 真实目录存在：`/home/faye/diyu-demo`。
- 错误目录不存在：`/home/faye/笛语demo`。
- Windows 可正常读取：`\\\\wsl$\\ubuntu-22.04\\home\\faye\\diyu-demo`。
- W 盘映射指向：`\\\\wsl$\\Ubuntu-22.04`，但 WSL 内并没有 `/mnt/w` 挂载点。
- 因此旧路径 `/mnt/w/home/faye/笛语demo` 是失效记录，不是当前真实目录。
- `/home/faye/diyu-demo` 当前是普通项目目录，没有目录内 `.git`；不要擅自执行 `git init`。

## Codex 当前状态

- 原始问题线程：`01a01a66-ec14-7d62-8299-18dd53e055ed`
  - 标题：`排查项目文件夹路径限制`
  - 旧工作目录：`/mnt/w/home/faye/笛语demo`
  - 该线程不可原地改绑工作目录。
- 已创建的正确目录 fork 线程：`01a01b68-8880-76f3-916f-b71016250c94`
  - 显示标题：`diyu-demo（正确目录）`
  - 工作目录：`/home/faye/diyu-demo`
  - 它目前是独立任务，不是已登记的侧边栏本地项目。
- Codex 项目列表仍含两个错误项目记录，均指向 `/home/faye/笛语demo`；正确的 `/home/faye/diyu-demo` 尚未登记为本地项目。
- 外部 CLI 需要同时设置：
  - `CODEX_HOME=/mnt/c/Users/Administrator/.codex`
  - `CODEX_SQLITE_HOME=/home/faye/.codex/sqlite`
- Windows 根目录下的旧库 `/mnt/c/Users/Administrator/.codex/state_5.sqlite` 有迁移版本冲突；不要删除或修复它。
- 桌面端实际使用的 WSL 状态库 `/home/faye/.codex/sqlite/state_5.sqlite` 完整性正常。

## 已排除的问题

- 当前 WSL 主 VHD 没有继续指向迁移前的其他盘。
- `\\\\wsl$` 能访问正确目录，因此不是 WSL 文件系统或 UNC 入口失效。
- 删除 E/F 盘迁移备份不会修复 Codex 项目登记。
- `searxng` MCP 启动警告与本地项目路径无关。
- `build-chatgpt-app` 技能适用于 Apps SDK/MCP 应用开发，不适用于 Codex 本地项目登记。

## 尚未解决的问题

Codex 桌面端仍未把 `/home/faye/diyu-demo` 登记为侧边栏本地项目。当前最可能的阻塞是 Codex 保存了迁移前/误命名时期的本地项目元数据，而不是 WSL 磁盘故障。

后续应优先：

1. 保持 `/home/faye/diyu-demo` 和 D 盘 VHD 不变。
2. 不删除迁移备份，除非另做备份完整性与未注册状态审计。
3. 只处理 Codex 中指向 `/home/faye/笛语demo` 和 `/mnt/w/...` 的陈旧项目记录。
4. 验证新建本地项目最终登记路径必须精确为 `/home/faye/diyu-demo`。
5. 不要再尝试把原始旧线程原地改绑；在 `diyu-demo（正确目录）` 任务或新建的正确项目任务中继续。

## 完整原始交互记录

原始 JSONL 会话记录仍保存在：

`/mnt/c/Users/Administrator/.codex/sessions/2026/08/19/rollout-2026-08-19T07-22-27-01a01a66-ec14-7d62-8299-18dd53e055ed.jsonl`

## 新窗口首条指令

在新窗口中发送：

> 请先读取 `/home/faye/diyu-demo/CODEX_HANDOFF_2026-08-19.md`，继续解决 Codex 桌面端无法把 `/home/faye/diyu-demo` 登记为本地项目的问题。不得改名项目文件夹，不得删除或迁移 WSL VHD/备份；先核对当前项目记录，再处理陈旧的 Codex 项目元数据。

