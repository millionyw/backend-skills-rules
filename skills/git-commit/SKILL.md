---
name: git-commit
description: "项目代码提交工作流：ruff 修复 → 暂存（排除规则文件）→ 生成 commit message → 提交 → fetch/rebase。触发词：'提交', 'commit', 'git commit', 'push代码', '提交代码', '暂存并提交'。当用户要求提交代码、暂存代码、或执行 git commit/push 时使用此技能，即使只说'提交一下'也应触发。"
---

# Git Commit — 项目代码提交工作流

## 核心原则：规则文件"只入不出"

以下文件属于**本地规则/工具文件**，只从远程拉取更新，**绝不提交到远程**：

| 文件 | 性质 |
|------|------|
| `CLAUDE.md` | 本地 AI 行为规则 |
| `AGENTS.md` | 本地 AI 代理配置 |
| `.gitignore` | 本地忽略规则 |
| `docs/虚拟电厂后端更新-commit-message.md` | 本地 commit message 管理工具 |

统称为 **LOCAL_ONLY_FILES**。

**操作规则：**
- `git add` 时**逐文件添加**，跳过 LOCAL_ONLY_FILES
- `git pull --rebase` 冲突时对 LOCAL_ONLY_FILES **始终选择本地版本**
- **不修改 `.gitignore`** 来实现排除——全靠本技能在 `git add` 阶段显式排除
- **不执行 `git rm --cached`**——这会产生待提交变更，改变远程仓库历史

---

## 执行流程

```
┌─────────────────────────────────────────────────────┐
│  Step 1: ruff 修复 + 格式化                           │
│  ruff check --fix + ruff format                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Step 2: git add 暂存                                │
│  逐文件添加，跳过 LOCAL_ONLY_FILES                    │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Step 3: 生成/读取 commit message                     │
│  从 docs/虚拟电厂后端更新-commit-message.md 读取       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Step 4: git commit                                  │
│  使用 commit message 提交，处理 pre-commit hook 报错   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Step 5: fetch + pull --rebase                       │
│  拉取远程更新并 rebase，冲突时保留本地规则文件          │
└─────────────────────────────────────────────────────┘
```

---

## Step 1: ruff 修复 + 格式化

### 1.1 收集待处理文件

从 `git diff --name-only` 和 `git diff --cached --name-only` 获取所有变更的 Python 文件（`*.py`），**排除 LOCAL_ONLY_FILES 中的 .py 文件**。

### 1.2 ruff check

```bash
ruff check --fix <file1.py> <file2.py> ...
```

### 1.3 手动处理不可自动修复的问题

常见不可自动修复的 ruff 错误：

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| F841 | 变量赋值后未使用 | 去掉赋值（如 `run_id = func()` → `func()`） |
| F811 | 重复定义 | 删除重复项 |

检查修复后是否还有报错：

```bash
ruff check <file1.py> <file2.py> ...
```

必须输出 `All checks passed!` 才继续。

### 1.4 ruff format

```bash
ruff format <file1.py> <file2.py> ...
```

---

## Step 2: git add 暂存（核心步骤）

**绝不使用 `git add -A` 或 `git add .`**，这会把 LOCAL_ONLY_FILES 也加入暂存区。

### 2.1 收集待暂存文件

```bash
# 获取所有已修改/新增/删除的文件
git diff --name-only          # 工作区修改
git diff --cached --name-only # 已暂存
git ls-files --deleted        # 已删除
```

### 2.2 过滤掉 LOCAL_ONLY_FILES

从上述文件列表中**移除**以下文件：

```
CLAUDE.md
AGENTS.md
.gitignore
docs/虚拟电厂后端更新-commit-message.md
```

### 2.3 逐文件 git add

```bash
git add <file1> <file2> <file3> ...   # 仅添加过滤后的文件
```

对于已删除的文件，`git add <deleted_file>` 会正确处理删除。

### 2.4 确认暂存区

```bash
git diff --cached --name-only
```

确认暂存区中**不包含**任何 LOCAL_ONLY_FILES。如果发现误添加，立即移除：

```bash
git reset HEAD -- <误添加的文件>
```

---

## Step 3: 生成/读取 commit message

### 读取本地 commit message 文档

```bash
cat docs/虚拟电厂后端更新-commit-message.md
```

该文档由用户或 `git-add-message` 技能维护，包含本次提交的完整 message。

### 如果文档不存在或为空

根据 `git diff --cached` 内容自动生成简洁的 commit message，格式参照文档中的条目风格：

```
<标题>

<功能分组条目>
```

---

## Step 4: git commit

### 4.1 执行提交

```bash
git commit -m "$(cat <<'EOF'
<commit message 内容>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 4.2 处理 pre-commit hook 报错

如果 pre-commit hook 修改了文件（如 ruff-format 再次格式化）：

1. 检查 hook 修改的文件列表
2. 过滤掉 LOCAL_ONLY_FILES
3. 将剩余文件重新 `git add`
4. 重新 `git commit`（使用相同的 message）

如果 hook 报错且无法自动修复，向用户报告错误内容，等待指示。

### 4.3 确认提交成功

```bash
git log -1 --oneline
```

---

## Step 5: fetch + pull --rebase

### 5.1 stash 本地修改

rebase 前先保存工作区未提交的修改（包括 LOCAL_ONLY_FILES 的修改）：

```bash
git stash push -m "rebase前暂存"
```

### 5.2 fetch + rebase

```bash
git fetch origin
git pull --rebase origin master
```

### 5.3 处理冲突

如果 rebase 产生冲突：

1. 查看冲突文件：`git status`
2. 对于 **LOCAL_ONLY_FILES** 的冲突：**始终选择本地版本**
   ```bash
   git checkout --ours <冲突的规则文件>
   git add <冲突的规则文件>
   ```
   逻辑：本地规则文件优先级高于远程，远程更新需要人工审阅后手动合并。
3. 对于**代码文件**的冲突：逐文件分析，向用户报告冲突内容，等待指示
4. 继续 rebase：`git rebase --continue`

### 5.4 恢复 stash

```bash
git stash pop
```

如果 stash pop 产生冲突（通常在 LOCAL_ONLY_FILES 上）：

1. 对 LOCAL_ONLY_FILES 冲突：选择本地版本（stash 中的版本）
2. 对代码文件冲突：报告给用户
3. 冲突解决后：`git stash drop`

### 5.5 合并远程规则文件更新

rebase 后，远程的 LOCAL_ONLY_FILES 可能有新内容。此时：

1. 用 `git diff HEAD@{1}..HEAD -- CLAUDE.md AGENTS.md .gitignore` 查看远程变更
2. 如果有变更，提示用户："远程规则文件有更新，是否手动审阅合并？"
3. 用户确认后，展示 diff 内容，由用户决定如何合并到本地版本
4. **不自动合并**——规则文件的变更需要人工判断

### 5.6 最终状态确认

```bash
git status
git log --oneline -3
```

---

## 快捷操作

### 仅暂存不提交

用户说"暂存"或"git add"时，执行 Step 2 后停止。

### 仅 rebase 不提交

用户说"rebase"或"pull"时，执行 Step 5。

### 仅 ruff 修复

用户说"ruff"或"lint"时，执行 Step 1。

---

## 注意事项

- **绝不使用 `git add -A` / `git add .`**——必须逐文件添加，跳过 LOCAL_ONLY_FILES
- **绝不修改 `.gitignore`**——排除逻辑全靠本技能在 git add 阶段实现
- **绝不执行 `git rm --cached`**——这会产生改变远程仓库的待提交变更
- `docs/虚拟电厂后端更新-commit-message.md` 是本地管理工具，**绝不提交**
- 规则文件冲突时**始终保留本地版本**，远程更新需人工审阅后手动合并
- pre-commit hook 中的 ruff 版本以 `.pre-commit-config.yaml` 为准
- commit message 末尾添加 `Co-Authored-By: Claude <noreply@anthropic.com>`
