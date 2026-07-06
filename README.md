# Backend Skills & Rules

AI 编程助手的技能与规则知识库，整理自 Claude Code / Trae IDE 的自定义配置。每个技能和规则都解决特定的开发、运维或知识管理问题。

---

## 技能目录

### 🖥️ 服务器运维

| 技能 | 文件 | 解决的问题 |
|------|------|-----------|
| linux-ssh-ops | [SKILL.md](skills/linux-ssh-ops/SKILL.md) | **跨发行版 SSH 运维踩坑** — 统一 Ubuntu/Debian/openEuler/CentOS/Linx 的运维操作，防止 heredoc 写坏文件、sudo 卡死、幽灵进程、包管理器选错等常见陷阱 |

<details>
<summary>linux-ssh-ops 参考文件</summary>

- [paramiko-patterns.md](skills/linux-ssh-ops/references/paramiko-patterns.md) — 即用型 paramiko 代码模板（连接、run()、SFTP 写文件、发行版检测、跨平台装包）
- [servers.md](skills/linux-ssh-ops/references/servers.md) — 服务器连接信息索引（IP/用户/密码/发行版）
- [ssh_run.py](skills/linux-ssh-ops/scripts/ssh_run.py) — 可直接使用的 SSH 操作脚本模板

</details>

### 📋 项目管理与工作记录

| 技能 | 文件 | 解决的问题 |
|------|------|-----------|
| managing-tasks | [SKILL.md](skills/managing-tasks/SKILL.md) | **任务创建混乱、子任务拆分不合理** — 规范化任务创建流程，按"交付成果"而非"实现步骤"拆分子任务，确保任务文件唯一、ID 唯一 |
| tracking-progress | [SKILL.md](skills/tracking-progress/SKILL.md) | **任务进度与实际脱节** — 自动比对日志执行情况与计划任务，更新完成度，识别过期/阻塞任务，完成时自动归档到 done/ |
| generating-reports | [SKILL.md](skills/generating-reports/SKILL.md) | **日报/周报编写费时** — 基于实际日志和任务数据上下文感知生成报告，周五自动切换为"下周计划"模式 |
| recording-ideas | [SKILL.md](skills/recording-ideas/SKILL.md) | **想法/经验无处记录** — 结构化记录想法和经验，支持分类（技术/产品/运维经验/AI Agent 经验）和任务关联 |
| work-log-prompt | [SKILL.md](skills/work-log-prompt/SKILL.md) | **工作日志容易遗漏** — 完成工作后主动提示记录日志，采用"目的导向"格式（为什么做 + 做了什么），按归属分类整理而非简单追加 |

---

## 规则目录

### 📐 全局行为规则

| 规则 | 文件 | 解决的问题 |
|------|------|-----------|
| global-behavior-rules | [global-behavior-rules.md](rules/global-behavior-rules.md) | **工作日志容易忘记** — 全局指令：每次完成实质性工作后主动询问是否记入日志 |

### 🖥️ 运维强制规范

| 规则 | 文件 | 解决的问题 |
|------|------|-----------|
| AGENTS_RULES | [AGENTS_RULES.md](rules/AGENTS_RULES.md) | **运维操作不规范导致服务器问题** — 七条强制规范：目录结构、防止幽灵进程（D 状态）、文件命名、启动检查清单、违规处理、脚本执行日志、运维文档反哺 |

---

## 目录结构

```
backend-skills-rules/
├── README.md                              ← 本文件
├── skills/                                ← 技能库
│   ├── linux-ssh-ops/                     # 跨发行版 SSH 运维
│   │   ├── references/                    # 代码模板 & 服务器信息
│   │   └── scripts/                       # 可执行脚本模板
│   ├── managing-tasks/                    # 任务创建
│   ├── tracking-progress/                 # 进度对齐
│   ├── generating-reports/                # 报告生成
│   ├── recording-ideas/                   # 想法/经验记录
│   └── work-log-prompt/                   # 工作日志提示
└── rules/                                 ← 规则库
    ├── global-behavior-rules.md           # 全局行为指令
    └── AGENTS_RULES.md                    # 服务器运维强制规范
```

---

## 核心问题 → 技能/规则 映射

| 你遇到的问题 | 应使用的技能/规则 |
|-------------|-----------------|
| "SSH 到服务器装软件/改配置" | linux-ssh-ops + AGENTS_RULES |
| "创建一个新任务" | managing-tasks |
| "同步任务进度和日志" | tracking-progress |
| "生成日报/周报" | generating-reports |
| "记录一个想法或经验" | recording-ideas |
| "忘了写工作日志" | work-log-prompt + global-behavior-rules |
| "运维操作不规范" | AGENTS_RULES |

---

## 来源说明

| 来源 | 路径 | 说明 |
|------|------|------|
| Claude Code 自定义技能 | `~/.claude/skills/` | linux-ssh-ops、work-log-prompt |
| Trae IDE 自定义技能 | 项目 `.trae/skills/` | managing-tasks、recording-ideas、generating-reports、tracking-progress |
| Claude Code 全局规则 | `~/.claude/CLAUDE.md` | global-behavior-rules |
| 运维强制规范 | 项目 `运维/AGENTS_RULES.md` | 服务器运维七条强制规范 |

---

*最后更新：2026-07-06*
