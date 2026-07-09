---
name: sync-from-209
description: "从 209 服务器同步代码到本地。当用户要求从远程服务器拉取代码、下载文件到本地时使用此技能。触发词：从 209 同步、从服务器拉取、下载到本地、sync from 209、pull from 209。"
---

# 从 209 服务器同步文件到本地

## 服务器信息

> 服务器配置从 `config/servers.json` 自动读取。首次使用请运行 `python install.py --config-only` 生成配置文件。

| 项 | 来源 |
|----|------|
| IP | `config/servers.json` → `servers[SERVER_NAME].host` |
| 用户 | `config/servers.json` → `servers[SERVER_NAME].user` |
| 密码 | `config/servers.json` → `servers[SERVER_NAME].password` |
| 远程根目录 | `scripts/sync_from.py` 顶部 `REMOTE_BASE` 常量 |

## 使用方式

运行技能目录下 `scripts/sync_from.py`，支持文件和目录，自动验证：

```bash
python .claude/skills/sync-from-209/scripts/sync_from.py <路径1> [路径2] [路径3] ...
```

路径可以是：
- **单个文件**：`projects/vpp/shandong/services/foo.py`
- **目录**：`projects/vpp/shandong/conf/`（递归同步目录下所有文件）
- **混合**：同时传文件和目录

路径相对于项目根目录（`rtdbpy_04/`），与远程路径对应。

## 工作流程

1. 用户指定要从 209 拉取的文件或目录
2. 运行 `sync_from.py`，脚本自动：
   - 使用 paramiko 密码登录（无需手动输入密码）
   - **验证远程文件/目录是否存在**（不存在的跳过并警告）
   - 递归创建本地目录
   - 下载文件
   - 对比远程与本地文件大小，验证一致性
3. 输出每个文件的同步状态（OK / MISMATCH / SKIP / NOT_FOUND）

## 示例

```bash
# 拉取单个文件
python .claude/skills/sync-from-209/scripts/sync_from.py projects/vpp/shandong/services/foo.py

# 拉取多个文件
python .claude/skills/sync-from-209/scripts/sync_from.py projects/vpp/shandong/services/foo.py projects/vpp/shandong/conf/task_registry.py

# 拉取整个目录
python .claude/skills/sync-from-209/scripts/sync_from.py projects/vpp/shandong/services/

# 混合
python .claude/skills/sync-from-209/scripts/sync_from.py projects/vpp/shandong/services/ projects/vpp/shandong/conf/task_registry.py
```

## 远程执行命令（可选）

拉取前如需在 209 上执行命令（如 `git log` 查看版本），可用 `-e` 参数：

```bash
python .claude/skills/sync-from-209/scripts/sync_from.py -e "cd /home/dems/tsysmart/rtdbpy && git log --oneline -5" projects/vpp/shandong/services/foo.py
```

## 依赖

- `paramiko`（`pip install paramiko`）

## 注意

- 文件路径使用正斜杠 `/`（与远程路径一致）
- 本地目录不存在时自动创建
- 验证仅比对文件大小；如需比对内容，可用 `-e "diff ..."` 手动检查
- 远程不存在的文件/目录会跳过并标记 `NOT_FOUND`
