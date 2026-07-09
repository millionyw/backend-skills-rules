---
name: sync-skills-to-repo
description: "将新增或修改的技能/规则同步到 backend-skills-rules 仓库，自动更新 install.py 注册表、中英文 README，脱敏检查后提交并推送到 GitHub。触发词：同步技能、sync skills、更新技能库、推送技能、sync to repo。当用户创建或修改了 SKILL.md / 规则文件后说'同步'时也应触发。"
---

# 同步技能/规则到 backend-skills-rules 仓库

## 概述

将用户在 `~/.claude/skills/` 或项目 `.trae/skills/` 等目录中新增或修改的技能/规则，同步到 backend-skills-rules 仓库（路径见下方"仓库位置"），确保 install.py 注册表、中英文 README 保持一致，然后提交并推送到 GitHub。

## 触发条件

### 正向触发

- 用户说"同步技能到仓库"、"sync skills"、"更新技能库"、"推送技能到 GitHub"
- 用户创建或修改了 SKILL.md / 规则文件后说"同步"
- 用户要求将某个技能/规则添加到 backend-skills-rules 仓库

### 负向触发

- 用户只是在查看或阅读技能内容，不涉及文件同步
- 用户要求安装技能（应使用 install.py）
- 用户要求修改技能内容本身（应直接编辑 SKILL.md）

## 仓库位置

> 通过 `git config --global backend-skills-repo.path` 或环境变量 `BACKEND_SKILLS_REPO` 指定仓库路径。
> 若两者均未设置，默认为 `~/backend-skills-rules`。

当前配置：

```
# 优先级：环境变量 > git config > 默认值
BACKEND_SKILLS_REPO=D:\my_homework\backend-skills-rules
```

远程：`git@github.com:millionyw/backend-skills-rules.git`

## 工作流程

### 步骤一：识别变更源

确定要同步的技能或规则：

1. **用户指定**：用户在对话中指明技能名（如 "同步 linux-ssh-ops"）或文件路径
2. **自动检测**：扫描当前会话中用 Edit/Write 工具修改过的 SKILL.md 或规则文件
3. **交互选择**：列出最近修改的技能/规则文件，让用户选择

**输出**：确认要同步的技能名或规则名列表。

### 步骤二：复制文件到仓库

将技能目录或规则文件复制到仓库对应位置：

| 类型 | 源 | 目标 |
|------|----|------|
| 技能 | 技能所在目录（含 SKILL.md、references/、scripts/ 等） | `$REPO/skills/<name>/` |
| 规则 | 规则 .md 文件 | `$REPO/rules/<name>.md` |

- 如果目标已存在，**覆盖更新**（用新版本替换旧版本）
- 如果目标不存在，**新建目录/文件**

复制方式：使用 Bash 的 `cp -r`（技能目录）或 `cp`（规则文件），确保所有子目录和文件都被复制。

### 步骤三：脱敏检查

扫描复制后的文件内容，检测不应入库的敏感信息：

| 检测项 | 正则模式 | 处理方式 |
|--------|---------|---------|
| 真实 IP 地址 | `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`（排除 127.0.0.1、0.0.0.0、255.255.255.255 等保留地址） | 提示用户替换为 `<IP address>` |
| 密码/凭据 | `password\s*[:=]\s*["'][^"']+["']` 或 `PWD\s*=\s*["'][^"']+["']` | 提示用户替换为占位符 |
| Windows 绝对路径 | `[A-Z]:[\\/]` 开头的路径 | 提示用户替换为 `config/servers.json` 引用或相对路径 |
| 内网域名/主机名 | `10\.211\.\d+\.\d+` 等明显内网地址 | 提示用户脱敏 |

**执行方式**：用 Grep 工具扫描刚复制的文件。发现敏感信息时：
1. 列出所有命中项（文件名 + 行号 + 命中内容）
2. 询问用户是否自动替换为占位符
3. 用户确认后，用 Edit 工具替换

### 步骤四：更新 install.py 注册表

读取 `$REPO/install.py` 中的 `REGISTRY` 列表：

1. **读取 SKILL.md frontmatter**：提取 `name` 和 `description` 字段
2. **检查是否已存在**：在 REGISTRY 中搜索同名条目
   - **已存在**：更新 `desc` 字段为最新 description
   - **不存在**：追加新条目，自动分配下一个序号（当前最大 id + 1）
3. **确定 config_steps**：根据技能性质选择配置步骤，可选项：
   - `[]` — 无需配置（大多数技能）
   - `["servers"]` — 需要服务器信息
   - `["servers", "sync_remote_base"]` — 需要服务器信息 + 远程路径
   - `["project_dirs"]` — 需要项目目录约定
   - `["ops_dir"]` — 需要运维目录
   - `["log_path"]` — 需要日志路径
   - 如不确定，**询问用户**
4. **确定 deploy_rules**：是否关联 AGENTS_OPS_RULES（默认 `False`，仅运维类技能为 `True`）
5. **确定 type**：`"skill"` 或 `"rule"`

用 Edit 工具在 REGISTRY 列表末尾添加新条目，或更新已有条目。

### 步骤五：更新 README.md

读取 `$REPO/README.md`，在对应分区添加技能/规则行：

1. **确定分区**：根据技能性质归入以下分区之一
   - 🖥️ Server Operations — 涉及 SSH、服务器、运维
   - 🔀 Git Workflow — 涉及 git 操作
   - 📋 Project & Work Management — 涉及任务管理、日志、报告
   - 如不确定，**询问用户**或新增分区
2. **添加技能/规则行**：在分区表格末尾添加一行，格式：
   - 技能：`| [name](skills/name/SKILL.md) | **简短描述** — 详细说明 |`
   - 规则：`| [name](rules/name.md) | 描述 |`
3. **更新 Quick Reference 表**：添加一行问题→技能映射
4. **更新 Repository Structure 树**：在 `skills/` 或 `rules/` 下添加新条目

### 步骤六：更新 README_zh.md

读取 `$REPO/README_zh.md`，同步 README.md 的变更：

1. **保持与 README.md 相同的分区和位置**
2. **使用中文描述**：
   - 如果 SKILL.md 的 description 是中文，直接使用
   - 如果是英文，翻译为中文
3. **同步 Quick Reference 和目录结构**

### 步骤七：验证一致性

检查以下一致性条件，如有不一致则列出差异并提示用户确认：

1. **install.py REGISTRY 条目** vs **README.md 表格行**：数量和名称应匹配
2. **skills/ 目录下的子目录名** vs **REGISTRY 中 type=skill 的 name**：应一一对应
3. **rules/ 目录下的 .md 文件名** vs **REGISTRY 中 type=rule 的 name + ".md"**：应一一对应
4. **README.md 与 README_zh.md**：分区、技能/规则条目数应相同

验证方式：用 Glob 扫描 skills/ 和 rules/ 目录，与 install.py REGISTRY 比对。

### 步骤八：Git 提交并推送到 GitHub

在仓库目录执行以下操作：

```bash
cd $REPO    # $REPO = 仓库根目录（见"仓库位置"）

# 1. 查看变更
git status
git diff --stat

# 2. 暂存所有变更
git add -A

# 3. 提交（commit message 列出新增/修改的技能和规则）
git commit -m "Add/update <skill-name>: <简短描述>

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"

# 4. 推送到 GitHub
git push origin master
```

**关键**：
- commit message 必须列出具体新增/修改的技能和规则名称
- 推送前确认 `git status` 显示的变更符合预期
- 推送后告知用户 GitHub 仓库已更新，附上仓库链接：https://github.com/millionyw/backend-skills-rules

## 约束

- 所有文件操作必须基于实际对话，不能编造技能内容
- 脱敏检查不能跳过，即使文件是从仓库自身复制的
- 更新 install.py 时不能破坏已有的 REGISTRY 条目（只能新增或更新 desc 字段）
- 更新 README 时不能删除已有条目，只能在末尾添加或在已有行上更新
- git push 前必须执行验证步骤（步骤七）
- 如果 git push 失败，报告错误信息，不自动重试

## 示例

### 示例1：同步新技能

**输入**：
> "我刚创建了一个新技能 sync-skills-to-repo，帮我同步到仓库"

**执行流程**：
1. 读取 `~/.claude/skills/sync-skills-to-repo/SKILL.md`，提取 name 和 description
2. 复制整个目录到 `$REPO/skills/sync-skills-to-repo/`
3. 扫描文件，检测敏感信息（如有的话提示替换）
4. 在 install.py REGISTRY 末尾添加条目（id=12, name=sync-skills-to-repo, type=skill, desc=...）
5. 在 README.md 的合适分区添加技能行
6. 在 README_zh.md 的相同分区添加中文技能行
7. 验证一致性
8. git commit + git push

### 示例2：同步已有技能的更新

**输入**：
> "linux-ssh-ops 的 SKILL.md 更新了，同步一下"

**执行流程**：
1. 复制更新后的文件覆盖仓库中的旧版本
2. 扫描脱敏
3. 更新 install.py REGISTRY 中 id=1 的 desc 字段
4. 更新 README.md 中 linux-ssh-ops 行的 Description
5. 更新 README_zh.md
6. 验证 → git commit + git push
