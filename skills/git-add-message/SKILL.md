---
name: git-add-message
description: "暂存代码并更新 commit message 文档。执行 git add 暂存后，生成 commit message 并写入 docs/虚拟电厂后端更新-commit-message.md，智能合并到已有相关条目。禁止执行 git commit。触发词：'git add', '暂存', 'add到暂存区', 'add message'"
---

# Git Add Message - 暂存代码并更新 commit message 文档

## 核心规则

**禁止执行 `git commit`。** 本技能只负责 `git add` 暂存和写入 commit message 文档，绝不执行提交。

## 触发时机

每次完成代码修改/创建工作后，主动询问用户是否暂存。也可由用户主动调用 `/git-add-message`。

## 执行流程

```
┌─────────────────────────────────────────────────────┐
│  Step 1: 收集本轮会话改动                              │
│  读取会话中所有 Edit/Write 操作涉及的文件路径           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Step 2: 询问用户是否暂存                              │
│  展示改动文件列表，询问是否 git add                     │
└─────────────────────────────────────────────────────┘
          ↓                           ↓
      [用户确认]                   [用户拒绝]
          ↓                           ↓
┌──────────────────────────────┐   ┌──────────────┐
│  Step 3: git add             │   │  流程结束     │
│  将本轮改动文件添加到暂存区    │   └──────────────┘
└──────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│  Step 4: 生成 commit message                          │
│  分析 git diff --cached 内容，按功能分组               │
└─────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│  Step 5: 更新 commit message 文档                      │
│  智能合并到已有条目，或追加新条目                       │
└─────────────────────────────────────────────────────┘
```

## Step 1: 收集本轮会话改动

从会话上下文中提取本轮所有文件变更：

- 所有 `Edit` 工具调用的 `file_path`
- 所有 `Write` 工具调用的 `file_path`
- 去重，得到本轮修改/新增的文件列表

**排除规则：** 以下文件仅更新内容，不加入暂存区：

- `docs/虚拟电厂后端更新-commit-message.md`（commit message 文档本身不参与 commit）

输出格式：
```
本轮会话改动文件：
  M  projects/vpp/shandong/services/weather.py
  A  projects/vpp/shandong/services/new_service.py
```

## Step 2: 询问用户

使用 AskUserQuestion 工具询问：

- 问题：是否将以上文件 git add 到暂存区？
- 选项：是 / 否

## Step 3: git add

用户确认后，逐文件添加到暂存区：

**注意：** 排除规则中的文件（如 `docs/虚拟电厂后端更新-commit-message.md`）不执行 `git add`。

```bash
git add <file1> <file2> ...
```

如果文件已删除（从会话中判断），使用：
```bash
git add <deleted_file>  # git add 会自动处理删除
```

执行后用 `git diff --cached --stat` 确认暂存结果。

## Step 4: 生成 commit message

分析 `git diff --cached` 的内容，按功能分组生成条目。

### 格式规范

每条 commit message 条目格式：

```
 <序号>. <功能标题>：
    - <具体改动描述1>
    - <具体改动描述2>
      (<相对路径文件列表>)
```

### 标题行规则

- **一行标题**：概括功能，以冒号结尾
- 简洁，不超过 30 字
- 描述"做了什么"，而非"改了哪个文件"

### 子条目规则

- 每条 `-` 描述一个具体改动点
- 描述"改了什么"，包含关键变量名/函数名
- 避免模糊描述（如"优化代码"、"修复bug"）
- **只记录功能层面的变更**，排除以下过程性内容：
  - 从远程服务器同步/下载文件（如"从 209 同步"）
  - 修复 AI 工具自身产生的错误（如"修复多余导入"、"缺 import os"）
  - 清理/删除无关文件（如"清除无关文件"）
  - 其他不影响产品功能的操作过程

### 文件列表规则

- 最后一行用 `(<文件列表>)` 标注涉及的文件
- 使用**相对于 `projects/vpp/shandong/` 的短路径**
- 多个文件用中文顿号 `、` 分隔
- 示例：`(services/weather.py、conf/task_registry.py)`

### 完整示例

```
 1. task_registry 天气任务参数对齐：
    - params_schema 从旧版 provider+ak 改为 baidu_ak，与 weather.run() 参数名一致
    - weather.py 新增 baidu_ak 参数
      (conf/task_registry.py、services/weather.py)

 2. 电能量合规校验日志迁移：
    - validate_compliance 日志从 bid_log 迁移到 task_log
    - 新增 client_info 参数，role_user 写入 OPERATOR_NAME
      (services/energy_bid.py、subapi/energy_bid.py)
```

## Step 5: 更新 commit message 文档

目标文件：`docs/虚拟电厂后端更新-commit-message.md`

### 核心原则：合并优先，追加其次

**写入前必须先分析已有条目**，判断本轮新改动是否应合并到已有条目中，而非简单追加。目标是保持文档聚合度——同一功能/模块的改动应归入同一条目。

### 合并判定规则

对每个新生成的条目，按以下规则判定是否应合并到已有条目：

1. **文件重叠**：新条目的文件列表与已有条目的文件列表有交集 → 合并到已有条目
2. **模块相同**：新条目与已有条目属于同一模块/功能域（如都是"24小时测试脚本"、"调频申报"相关） → 合并到已有条目
3. **标题语义相同**：新条目标题与已有条目标题描述的是同一功能的延续或补充 → 合并到已有条目

**不合并的情况：** 新条目与已有条目无文件重叠、无模块关联、功能独立 → 作为新条目追加。

### 合并操作步骤

当判定应合并到已有条目时：

1. **保留已有条目的序号和标题**（标题可微调以涵盖新内容）
2. **追加子条目**：将新改动点追加到已有条目的子条目列表末尾
3. **合并文件列表**：将新条目的文件列表合并到已有条目的文件列表中，去重
4. **不改变已有子条目内容**：已有描述保持原样，只追加新的

### 合并示例

**文档已有条目：**
```
 3. 24小时测试脚本增强：
    - 新增 --vpp-name 必填命令行参数，TestRunner 传递 vpp_name
    - 运行开始时导出三个面板的 CSV 基准数据
      (test/24hour_test_flow.py)
```

**本轮新生成条目：**
```
 4. 24小时测试 check 定义重构为 dict 格式：
    - 所有 check 定义从元组改为 dict，显式声明 sql/params/desc/validator/export_sql/export_params
    - 删除 _build_export_sql 和 _parse_check_item
      (test/24hour_test_flow.py)
```

**合并结果（修改已有条目 3，不追加条目 4）：**
```
 3. 24小时测试脚本增强：
    - 新增 --vpp-name 必填命令行参数，TestRunner 传递 vpp_name
    - 运行开始时导出三个面板的 CSV 基准数据
    - check 定义从元组重构为 dict 格式，显式声明 sql/params/desc/validator/export_sql/export_params
    - 删除 _build_export_sql 和 _parse_check_item
      (test/24hour_test_flow.py)
```

### 追加逻辑（不合并时）

1. 确定条目所属章节（"新增功能："/"修改功能："/协作者章节）
2. 在该章节末尾追加新条目
3. 序号接续该章节现有的最大序号 +1
4. 不重新编号已有条目

### 写入后确认

确认文档已更新，输出摘要：

```
已暂存 N 个文件，commit message 已更新：
  [合并] <已有条目标题>（追加 N 条子条目）
  [新增] <新条目标题>
  ...
文档路径：docs/虚拟电厂后端更新-commit-message.md（仅本地更新，未加入暂存区）
```

## 禁止事项

- **禁止执行 `git commit`**：本技能只负责 `git add` 暂存和写入 commit message 文档，绝不执行 `git commit`。即使暂存完成，也不提交。
- **禁止执行 `git push`**：不执行任何推送操作。

## 注意事项

- 只处理**本轮会话**中 Edit/Write 操作涉及的文件，不包含用户手动修改的文件
- 如果暂存区已有文件，`git add` 会追加而非覆盖
- 文件路径统一使用正斜杠 `/`
- commit message 文档中的路径相对于 `projects/vpp/shandong/`，不含该前缀
- 如果本轮无文件改动，直接提示"本轮无代码改动"，不执行后续步骤
- **合并时必须重写整个已有条目**（因为需要修改子条目和文件列表），确保条目格式完整
