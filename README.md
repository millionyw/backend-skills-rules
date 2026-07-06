# Backend Skills & Rules

AI 编程助手的技能与规则知识库，整理自 Claude Code / Trae IDE 的自定义配置。每个技能和规则都解决特定的开发、运维或知识管理问题。

---

## 技能目录

### 🔍 代码理解与导航

| 技能 | 文件 | 解决的问题 |
|------|------|-----------|
| gitnexus-exploring | [SKILL.md](skills/gitnexus-exploring/SKILL.md) | **不熟悉代码库时无从下手** — 通过 GitNexus 知识图谱发现执行流、追踪调用链、理解架构，避免大海捞针式阅读源码 |
| gitnexus-debugging | [SKILL.md](skills/gitnexus-debugging/SKILL.md) | **Bug 追踪效率低** — 利用知识图谱快速定位错误来源、追踪调用链、识别外部依赖故障点，而非逐文件搜索 |
| gitnexus-impact-analysis | [SKILL.md](skills/gitnexus-impact-analysis/SKILL.md) | **改代码怕"炸"** — 在修改函数/模块前评估影响范围（blast radius），按 d=1/2/3 分级风险，避免盲目修改导致级联故障 |
| gitnexus-refactoring | [SKILL.md](skills/gitnexus-refactoring/SKILL.md) | **重命名/重构风险高** — 自动化多文件重命名（gitnexus_rename），追踪所有引用点，重构后验证影响范围 |
| gitnexus-guide | [SKILL.md](skills/gitnexus-guide/SKILL.md) | **不知道 GitNexus 能做什么** — 工具/资源/图谱 Schema 的快速参考手册，帮助选择合适的 GitNexus 技能 |
| gitnexus-cli | [SKILL.md](skills/gitnexus-cli/SKILL.md) | **索引过时/需要重建** — GitNexus CLI 命令参考（analyze/status/clean/wiki），管理代码知识图谱的生命周期 |

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

### 🛠️ 技能开发

| 技能 | 文件 | 解决的问题 |
|------|------|-----------|
| learn-skills | [SKILL.md](skills/learn-skills/SKILL.md) | **不知道如何编写/优化 AI 技能** — 将 Skill 设计标准（边界、结构化 I/O、指令化步骤、失败策略、单一职责）转化为可执行的开发流程 |

<details>
<summary>learn-skills 模板</summary>

- [SKILL-template.md](skills/learn-skills/templates/SKILL-template.md) — 标准技能模板（含 frontmatter、触发条件、I/O 定义、步骤、失败策略）

</details>

### 📝 Obsidian 知识管理

| 技能 | 文件 | 解决的问题 |
|------|------|-----------|
| obsidian-markdown | [SKILL.md](skills/obsidian-markdown/SKILL.md) | **Obsidian 特有语法记不住** — Wikilinks、嵌入、Callouts、YAML frontmatter、高亮/脚注/数学公式等 Obsidian 专属语法的完整参考 |
| obsidian-cli | [SKILL.md](skills/obsidian-cli/SKILL.md) | **Obsidian 插件开发缺乏参考** — 插件结构、API 概览（命令/事件/Modal/设置面板）、文件读写、编辑器操作的代码模板 |
| obsidian-bases | [SKILL.md](skills/obsidian-bases/SKILL.md) | **Obsidian Bases 数据库不会配置** — .base 文件的 YAML 格式、列类型、视图（Table/Board/Gallery/Calendar）、过滤器、公式、汇总的完整参考 |
| json-canvas | [SKILL.md](skills/json-canvas/SKILL.md) | **JSON Canvas 画布文件格式不清** — 节点类型（text/file/link/image/group）、边连接、分组、属性定义的完整规范 |
| defuddle | [SKILL.md](skills/defuddle/SKILL.md) | **网页内容提取噪音太多** — 从网页中提取干净的 Markdown 内容，去除导航/广告/页脚等非正文元素，节省 token |

---

## 规则目录

### 📐 项目管理规则

| 规则 | 文件 | 解决的问题 |
|------|------|-----------|
| project-manager | [project-manager.md](rules/project-manager.md) | **AI 输出格式不统一** — 强制结构化输出（Markdown 表格、清单、分点列表），要求上下文感知（先读文件再操作），确保数据一致性和可操作性 |
| global-behavior-rules | [global-behavior-rules.md](rules/global-behavior-rules.md) | **工作日志容易忘记** — 全局指令：每次完成实质性工作后主动询问是否记入日志 |

### 🖥️ 运维强制规范

| 规则 | 文件 | 解决的问题 |
|------|------|-----------|
| AGENTS_RULES | [AGENTS_RULES.md](rules/AGENTS_RULES.md) | **运维操作不规范导致服务器问题** — 七条强制规范：目录结构、防止幽灵进程（D 状态）、文件命名、启动检查清单、违规处理、脚本执行日志、运维文档反哺 |

---

## 技能分类总览

```
backend-skills-rules/
├── README.md                              ← 本文件
├── skills/                                ← 技能库
│   ├── gitnexus-exploring/                # 代码探索
│   ├── gitnexus-debugging/                # Bug 追踪
│   ├── gitnexus-impact-analysis/          # 影响分析
│   ├── gitnexus-refactoring/              # 安全重构
│   ├── gitnexus-guide/                    # GitNexus 参考手册
│   ├── gitnexus-cli/                      # 索引管理
│   ├── linux-ssh-ops/                     # 跨发行版 SSH 运维
│   │   ├── references/                    # 代码模板 & 服务器信息
│   │   └── scripts/                       # 可执行脚本模板
│   ├── managing-tasks/                    # 任务创建
│   ├── tracking-progress/                 # 进度对齐
│   ├── generating-reports/                # 报告生成
│   ├── recording-ideas/                   # 想法/经验记录
│   ├── work-log-prompt/                   # 工作日志提示
│   ├── learn-skills/                      # 技能开发指南
│   │   └── templates/                     # 技能模板
│   ├── obsidian-markdown/                 # Obsidian Markdown 语法
│   ├── obsidian-cli/                      # Obsidian 插件开发
│   ├── obsidian-bases/                    # Obsidian Bases 数据库
│   ├── json-canvas/                       # JSON Canvas 画布
│   └── defuddle/                          # 网页内容清洗
└── rules/                                 ← 规则库
    ├── project-manager.md                 # 项目管理输出规范
    ├── global-behavior-rules.md           # 全局行为指令
    └── AGENTS_RULES.md                    # 服务器运维强制规范
```

---

## 核心问题 → 技能/规则 映射

| 你遇到的问题 | 应使用的技能/规则 |
|-------------|-----------------|
| "这段代码怎么工作的？" | gitnexus-exploring |
| "为什么这个接口报 500？" | gitnexus-debugging |
| "改这个函数会影响到谁？" | gitnexus-impact-analysis |
| "安全地重命名这个函数" | gitnexus-refactoring |
| "GitNexus 怎么用？" | gitnexus-guide |
| "索引需要更新" | gitnexus-cli |
| "SSH 到服务器装软件/改配置" | linux-ssh-ops + AGENTS_RULES |
| "创建一个新任务" | managing-tasks |
| "同步任务进度和日志" | tracking-progress |
| "生成日报/周报" | generating-reports |
| "记录一个想法或经验" | recording-ideas |
| "忘了写工作日志" | work-log-prompt + global-behavior-rules |
| "写一个新的 AI 技能" | learn-skills |
| "写 Obsidian 笔记" | obsidian-markdown |
| "开发 Obsidian 插件" | obsidian-cli |
| "配置 Obsidian Bases 数据库" | obsidian-bases |
| "创建 Obsidian 画布" | json-canvas |
| "从网页提取干净内容" | defuddle |
| "AI 输出格式不统一" | project-manager |
| "运维操作不规范" | AGENTS_RULES |

---

## 来源说明

| 来源 | 路径 | 说明 |
|------|------|------|
| Claude Code 自定义技能 | `~/.claude/skills/` | gitnexus 系列、linux-ssh-ops、work-log-prompt |
| Trae IDE 自定义技能 | 项目 `.trae/skills/` | managing-tasks、learn-skills、recording-ideas、defuddle、generating-reports、tracking-progress、obsidian 系列、json-canvas |
| Claude Code 全局规则 | `~/.claude/CLAUDE.md` | global-behavior-rules |
| Trae IDE 项目规则 | 项目 `.trae/rules/` | project-manager |
| 运维强制规范 | 项目 `运维/AGENTS_RULES.md` | 服务器运维七条强制规范 |

---

*最后更新：2026-07-06*
