---
name: sync-to-209
description: "同步文件到远程服务器。当用户要求同步代码、部署、上传文件到远程服务器时使用此技能。触发词：同步到服务器、推送到服务器、部署、上传到服务器、sync to server。按实际环境修改 scripts/sync.py 顶部配置即可适配不同服务器。"
---

# 同步文件到远程服务器

## 服务器信息

> 服务器配置从 `config/servers.json` 自动读取。首次使用请运行 `python install.py --config-only` 生成配置文件。

| 项 | 来源 |
|----|------|
| IP | `config/servers.json` → `servers[SERVER_NAME].host` |
| 用户 | `config/servers.json` → `servers[SERVER_NAME].user` |
| 密码 | `config/servers.json` → `servers[SERVER_NAME].password` |
| 远程根目录 | `scripts/sync.py` 顶部 `REMOTE_BASE` 常量 |

## 使用方式

运行技能目录下 `scripts/sync.py`，支持文件和目录，自动验证：

```bash
python .claude/skills/sync-to-209/scripts/sync.py <路径1> [路径2] [路径3] ...
```

路径可以是：
- **单个文件**：`projects/vpp/shandong/services/foo.py`
- **目录**：`projects/vpp/shandong/conf/`（递归同步目录下所有文件）
- **混合**：同时传文件和目录

路径相对于项目根目录（`rtdbpy_04/`）。

## 工作流程

1. 用户指定要同步的文件或目录
2. 运行 `sync.py`，脚本自动：
   - 使用 paramiko 密码登录（无需手动输入密码）
   - 递归创建远程目录
   - 上传文件
   - 对比本地与远程文件大小，验证一致性
3. 输出每个文件的同步状态（OK / MISMATCH / SKIP）

## 示例

```bash
# 同步单个文件
python .claude/skills/sync-to-209/scripts/sync.py projects/vpp/shandong/services/mgems_vpp_energy_settlement.py

# 同步多个文件
python .claude/skills/sync-to-209/scripts/sync.py projects/vpp/shandong/services/foo.py projects/vpp/shandong/conf/task_registry.py

# 同步整个目录
python .claude/skills/sync-to-209/scripts/sync.py projects/vpp/shandong/services/

# 混合
python .claude/skills/sync-to-209/scripts/sync.py projects/vpp/shandong/services/ projects/vpp/shandong/conf/task_registry.py
```

## 远程执行命令（可选）

同步后如需在 209 上执行命令，可用 `-e` 参数：

```bash
python .claude/skills/sync-to-209/scripts/sync.py -e "cd /home/dems/tsysmart/rtdbpy && git status" projects/vpp/shandong/services/foo.py
```

## 依赖

- `paramiko`（`pip install paramiko`）

## 注意

- 文件路径使用正斜杠 `/`（与远程路径一致）
- 远程目录不存在时自动创建
- 验证仅比对文件大小；如需比对内容，可用 `-e "diff ..."` 手动检查
