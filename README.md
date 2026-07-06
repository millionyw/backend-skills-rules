# 🛠️ Backend Skills & Rules

> AI 编程助手的技能与规则知识库。每个技能和规则都解决特定的开发、运维或知识管理问题，可直接部署到 Claude Code 或 Trae IDE 使用。

English | **[中文](README_zh.md)**

## Skills

### 🖥️ Server Operations

| Skill | Description |
|-------|-------------|
| [linux-ssh-ops](skills/linux-ssh-ops/SKILL.md) | **Cross-distro SSH operations via paramiko** — Prevents heredoc file corruption, sudo hangs, ghost processes (D-state), and wrong package manager across Ubuntu/Debian/openEuler/CentOS/Linx. Includes ready-to-use code templates and server connection index. |
| [sync-to-209](skills/sync-to-209/SKILL.md) | **One-click file sync to remote server** — Uploads files/directories via paramiko, auto-creates remote dirs, verifies file sizes, and optionally runs post-sync commands. |

<details>
<summary>📁 linux-ssh-ops references</summary>

- [paramiko-patterns.md](skills/linux-ssh-ops/references/paramiko-patterns.md) — Copy-paste code templates (connect, run, SFTP write, distro detect, cross-platform install)
- [servers.md](skills/linux-ssh-ops/references/servers.md) — Server connection index (IP / user / password / distro)
- [ssh_run.py](skills/linux-ssh-ops/scripts/ssh_run.py) — Ready-to-use SSH operation script template

</details>

<details>
<summary>📁 sync-to-209 references</summary>

- [sync.py](skills/sync-to-209/scripts/sync.py) — Ready-to-use remote sync script (edit top config for different servers)

</details>

### 🔀 Git Workflow

| Skill | Description |
|-------|-------------|
| [git-add-message](skills/git-add-message/SKILL.md) | **Keep staged files in sync with change log** — Auto-collects modified files in session, asks to stage, groups by feature, and appends commit message entries to a change document. |
| [git-commit](skills/git-commit/SKILL.md) | **Full commit workflow** — ruff fix → per-file staging (excludes LOCAL_ONLY_FILES) → reads commit message doc → commit → fetch/rebase, preserving local rule files on conflict. |

### 📋 Project & Work Management

| Skill | Description |
|-------|-------------|
| [managing-tasks](skills/managing-tasks/SKILL.md) | **Structured task creation** — Decomposes goals by deliverables (not implementation steps), ensures unique file/ID per task, stores in `tasks/` directory. |
| [tracking-progress](skills/tracking-progress/SKILL.md) | **Keep progress in sync with reality** — Compares daily logs against planned tasks, updates completion rates, flags overdue/blocked items, auto-archives done tasks. |
| [generating-reports](skills/generating-reports/SKILL.md) | **Context-aware daily/weekly reports** — Generates reports from actual logs and task data; Fridays auto-switch to "next week plan" mode. |
| [recording-ideas](skills/recording-ideas/SKILL.md) | **Structured idea & experience capture** — Records with category tags (tech / product / ops / AI agent experience) and optional task linking. |
| [work-log-prompt](skills/work-log-prompt/SKILL.md) | **Never miss a work log** — Prompts to log after each substantial task; uses "purpose-driven" format (why + what), organizes by project/ops category instead of appending. |

---

## Rules

### 📐 Global Behavior

| Rule | Description |
|------|-------------|
| [global-behavior-rules](rules/global-behavior-rules.md) | Auto-prompt to record work log after completing substantial tasks. |

### 🖥️ Server Operations Compliance

| Rule | Description |
|------|-------------|
| [AGENTS_OPS_RULES](rules/AGENTS_OPS_RULES.md) | **Mandatory 7-rule ops standard** — Directory structure, ghost process prevention (D-state), file naming, startup checklist, violation handling, script execution logging, documentation back-feed. |

---

## Quick Reference

| Problem | Use |
|---------|-----|
| SSH to server, install software, change config | `linux-ssh-ops` + `AGENTS_OPS_RULES` |
| Sync code to remote server | `sync-to-209` |
| Stage code and record changes | `git-add-message` |
| Full commit workflow (ruff → stage → commit → rebase) | `git-commit` |
| Create a new task | `managing-tasks` |
| Sync task progress with logs | `tracking-progress` |
| Generate daily/weekly report | `generating-reports` |
| Record an idea or experience | `recording-ideas` |
| Forgot to write work log | `work-log-prompt` + `global-behavior-rules` |
| Ops not following standards | `AGENTS_OPS_RULES` |

---

## Repository Structure

```
backend-skills-rules/
├── skills/
│   ├── linux-ssh-ops/          # Cross-distro SSH operations
│   │   ├── references/         # Code templates & server info
│   │   └── scripts/            # Executable script templates
│   ├── sync-to-209/            # Remote server file sync
│   │   └── scripts/
│   ├── git-add-message/        # Stage code & update commit message doc
│   ├── git-commit/             # Full commit workflow
│   ├── managing-tasks/         # Task creation
│   ├── tracking-progress/      # Progress alignment
│   ├── generating-reports/     # Report generation
│   ├── recording-ideas/        # Idea & experience capture
│   └── work-log-prompt/        # Work log prompt
└── rules/
    ├── global-behavior-rules.md
    └── AGENTS_OPS_RULES.md
```
