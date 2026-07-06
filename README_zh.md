# 🛠️ Backend Skills & Rules

> AI 编程助手的技能与规则知识库。每个技能和规则都解决特定的开发、运维或知识管理问题，可直接部署到 Claude Code 或 Trae IDE 使用。

**[English](README.md)** | 中文

---

## 技能

### 🖥️ 服务器运维

| 技能 | 说明 |
|------|------|
| [linux-ssh-ops](skills/linux-ssh-ops/SKILL.md) | **跨发行版 SSH 运维** — 通过 paramiko 统一 Ubuntu/Debian/openEuler/CentOS/Linx 运维操作，防止 heredoc 写坏文件、sudo 卡死、幽灵进程（D 状态）、包管理器选错等常见陷阱。含即用型代码模板和服务器连接索引。 |
| [sync-to-209](skills/sync-to-209/SKILL.md) | **一键同步文件到远程服务器** — 通过 paramiko 密码登录上传文件/目录，自动递归创建远程目录，验证文件大小一致性，支持同步后远程执行命令。 |

<details>
<summary>📁 linux-ssh-ops 参考文件</summary>

- [paramiko-patterns.md](skills/linux-ssh-ops/references/paramiko-patterns.md) — 即用型代码模板（连接、run()、SFTP 写文件、发行版检测、跨平台装包）
- [servers.md](skills/linux-ssh-ops/references/servers.md) — 服务器连接信息索引（IP / 用户 / 密码 / 发行版）
- [ssh_run.py](skills/linux-ssh-ops/scripts/ssh_run.py) — 可直接使用的 SSH 操作脚本模板

</details>

<details>
<summary>📁 sync-to-209 参考文件</summary>

- [sync.py](skills/sync-to-209/scripts/sync.py) — 可直接使用的远程同步脚本（修改顶部配置适配不同服务器）

</details>

### 🔀 Git 工作流

| 技能 | 说明 |
|------|------|
| [git-add-message](skills/git-add-message/SKILL.md) | **暂存代码与变更记录脱节** — 自动收集会话改动文件、询问暂存、按功能分组生成 commit message 条目并追加到变更文档，确保每次改动都有据可查。 |
| [git-commit](skills/git-commit/SKILL.md) | **完整提交流程** — ruff 修复 → 逐文件暂存（排除 LOCAL_ONLY_FILES）→ 读取 commit message 文档 → 提交 → fetch/rebase，冲突时保留本地规则文件。 |

### 📋 项目管理与工作记录

| 技能 | 说明 |
|------|------|
| [managing-tasks](skills/managing-tasks/SKILL.md) | **任务创建混乱、子任务拆分不合理** — 按"交付成果"而非"实现步骤"拆分子任务，确保任务文件唯一、ID 唯一，存储在 `tasks/` 目录。 |
| [tracking-progress](skills/tracking-progress/SKILL.md) | **任务进度与实际脱节** — 自动比对日志执行情况与计划任务，更新完成度，识别过期/阻塞任务，完成时自动归档到 done/。 |
| [generating-reports](skills/generating-reports/SKILL.md) | **日报/周报编写费时** — 基于实际日志和任务数据上下文感知生成报告，周五自动切换为"下周计划"模式。 |
| [recording-ideas](skills/recording-ideas/SKILL.md) | **想法/经验无处记录** — 结构化记录想法和经验，支持分类（技术/产品/运维经验/AI Agent 经验）和任务关联。 |
| [work-log-prompt](skills/work-log-prompt/SKILL.md) | **工作日志容易遗漏** — 完成工作后主动提示记录日志，采用"目的导向"格式（为什么做 + 做了什么），按归属分类整理而非简单追加。 |

---

## 规则

### 📐 全局行为

| 规则 | 说明 |
|------|------|
| [global-behavior-rules](rules/global-behavior-rules.md) | 每次完成实质性工作后自动提示记录工作日志。 |

### 🖥️ 运维强制规范

| 规则 | 说明 |
|------|------|
| [AGENTS_OPS_RULES](rules/AGENTS_OPS_RULES.md) | **七条强制运维规范** — 目录结构、防止幽灵进程（D 状态）、文件命名、启动检查清单、违规处理、脚本执行日志、运维文档反哺。 |

---

## 快速参考

| 你遇到的问题 | 使用 |
|-------------|------|
| SSH 到服务器装软件/改配置 | `linux-ssh-ops` + `AGENTS_OPS_RULES` |
| 同步代码到远程服务器 | `sync-to-209` |
| 暂存代码并记录变更 | `git-add-message` |
| 提交代码（ruff → 暂存 → commit → rebase） | `git-commit` |
| 创建一个新任务 | `managing-tasks` |
| 同步任务进度和日志 | `tracking-progress` |
| 生成日报/周报 | `generating-reports` |
| 记录一个想法或经验 | `recording-ideas` |
| 忘了写工作日志 | `work-log-prompt` + `global-behavior-rules` |
| 运维操作不规范 | `AGENTS_OPS_RULES` |

---

## 仓库结构

```
backend-skills-rules/
├── skills/
│   ├── linux-ssh-ops/          # 跨发行版 SSH 运维
│   │   ├── references/         # 代码模板 & 服务器信息
│   │   └── scripts/            # 可执行脚本模板
│   ├── sync-to-209/            # 远程服务器文件同步
│   │   └── scripts/
│   ├── git-add-message/        # 暂存代码 & 更新 commit message 文档
│   ├── git-commit/             # 完整提交工作流
│   ├── managing-tasks/         # 任务创建
│   ├── tracking-progress/      # 进度对齐
│   ├── generating-reports/     # 报告生成
│   ├── recording-ideas/        # 想法 & 经验记录
│   └── work-log-prompt/        # 工作日志提示
└── rules/
    ├── global-behavior-rules.md
    └── AGENTS_OPS_RULES.md
```
