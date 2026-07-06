# 服务器运维强制规范（所有智能体必读）

> **⚠️ 智能体启动规则：在开始任何 209/112/130/161 服务器运维工作之前，必须先阅读本文件！**
>
> 违反以下规则导致的服务器问题（幽灵进程、文件混乱、误操作），视为智能体责任。

---

## 一、目录结构强制规范

所有服务器运维目录**必须**遵循以下统一结构，不得违反：

```
服务器目录名/
├── README.md                # 入口文档（服务器基本信息）
├── 01_基本信息.md           # 系统版本、IP、网络
├── 02_用户与权限.md         # 用户、SSH、目录权限
├── 03_xxx.md               # 各类配置文档
├── ...
├── scripts/                # 【强制】所有 .py/.sh 脚本必须放在这里
│   └── README.md          # 脚本索引（按功能分类）
├── reports/               # 【强制】所有分析报告必须输出到这里
│   └── *.md              # 命名规范：disk_io_analysis_YYYYMMDD_HHMM.md
└── logs/                  # 【强制】所有 .log 文件必须放在这里
    └── *.log
```

### ❌ 禁止行为

| 禁止 | 原因 |
|------|------|
| 在服务器目录根目录下直接放 `.py`/`.sh` 脚本 | 与文档混在一起，难以维护 |
| 在服务器目录根目录下直接放 `.log` 文件 | 与文档混在一起，难以维护 |
| 在服务器目录根目录下直接放分析报告 `.md` | 与配置文档混在一起，难以查找 |
| 创建报告时不指定 `reports/` 路径 | 报告散落，无法统一管理 |

### ✅ 正确做法

```python
# 脚本中指定报告输出路径（示例）
REPORT_DIR = os.path.join(SCRIPT_DIR, '..', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)
filepath = os.path.join(REPORT_DIR, f'report_{timestamp}.md')
```

---

## 二、防止幽灵进程（D 状态）强制规范

### 问题回顾

2026-06-05，因 `collect_io_metrics.py` 中的 `find /home/dems ...` 命令在磁盘 I/O 饱和时没有超时保护，导致多个 `find` 进程卡死在 `D`（不可中断睡眠）状态，无法被 `kill` 杀死，直接造成 209 服务器 15 分钟负载飙升至 **63.79**（16 核正常满载 = 16.0）。

### ❌ 禁止行为

| 禁止 | 原因 |
|------|------|
| 对大型目录（如 `/home/dems`、`/var`）执行无超时 `find` | 磁盘 I/O 饱和时会卡死成 `D` 状态 |
| 在 SSH 远程命令中执行可能长时间阻塞的命令（无 `timeout` 包裹） | 进程卡死，只能等 I/O 完成或重启服务器 |
| 使用 `os.system()` 或 `subprocess.run()` 且不设 `timeout` 参数 | 脚本卡死，无法自动恢复 |
| 在服务器上后台执行 `find`/`rsync`/`tar` 等 I/O 密集型命令（无 timeout） | 同上的幽灵进程问题 |

### ✅ 强制规范（所有 SSH 远程命令必须遵循）

#### 1. 所有 SSH 执行的命令必须加 `timeout` 包裹

```python
# ❌ 错误示例（会导致卡死）
stdin, stdout, stderr = client.exec_command('find /home/dems -name "*.py"')

# ✅ 正确示例
stdin, stdout, stderr = client.exec_command(
    'timeout 30 find /home/dems -name "*.py" 2>/dev/null || true',
    timeout=40   # paramiko timeout 要大于命令 timeout
)
```

#### 2. 禁止对大型目录执行深度 `find`

```python
# ❌ 错误：遍历整个 /home/dems（可能数十万文件）
cmd = 'find /home/dems -name "clickhouse*"'

# ✅ 正确：限制深度，或换用 locate/which/直接指定路径
cmd = 'timeout 10 find /home/dems -maxdepth 4 -name "clickhouse*" 2>/dev/null || true'
# 更好：用 which 或直接检查已知路径
cmd = 'ls /home/dems/tsysmart/clickhouse_data 2>/dev/null && echo "found"'
```

#### 3. `collect_io_metrics.py` 等数据采集脚本的强制要求

```python
def ssh_run(client, cmd, timeout=30):
    """远程执行命令，强制加 timeout 包裹，防止卡死"""
    # 用 timeout 命令包裹原命令
    wrapped = f"timeout {timeout} bash -c '{_escape(cmd)}'"
    stdin, stdout, stderr = client.exec_command(wrapped, timeout=timeout+10)
    return stdout.read().decode('utf-8', errors='replace'), stderr.read().decode('utf-8', errors='replace')

def _escape(cmd):
    """对命令中的单引号进行转义，用于 bash -c '...' 包裹"""
    return cmd.replace("'", "'\\''")
```

#### 4. 本地执行耗时命令必须设 timeout

```python
# ✅ 正确
result = subprocess.run(
    ['ssh', 'dems@10.211.211.209', 'find /home/dems -name "*.log"'],
    capture_output=True, text=True, timeout=30
)

# ❌ 错误（可能永久卡死）
result = subprocess.run(['ssh', '...', 'find ...'], capture_output=True, text=True)
```

---

## 三、文件命名规范

> 📒 **幽灵进程清理工具**：`scripts/kill_ghost_processes.py`
> 用法：`python scripts/kill_ghost_processes.py`
> 功能：检测 209 服务器 D 状态进程，分析阻塞原因，生成处置报告到 `reports/`

### 脚本文件

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 检查类 | `check_xxx.py` | `check_airflow.py`、`check_docker.py` |
| 修复类 | `fix_xxx.py` | `fix_stuck_tasks.py`、`fix_docker_permission.py` |
| 重启类 | `restart_xxx.py` | `restart_airflow_final.py` |
| 报告采集 | `collect_xxx.py` | `collect_io_metrics.py` |
| Shell 脚本 | `xxx.sh` | `restart_airflow.sh` |

### 报告文件

| 类型 | 命名规范 | 输出路径 |
|------|----------|----------|
| 磁盘 IO 分析 | `disk_io_analysis_YYYYMMDD_HHMM.md` | `reports/` |
| 其他分析报告 | `xxx_analysis_YYYYMMDD_HHMM.md` | `reports/` |

### 日志文件

| 类型 | 命名规范 | 输出路径 |
|------|----------|----------|
| 脚本执行日志 | `脚本名.log` | `logs/` |
| 手动操作记录 | `操作描述_YYYYMMDD.log` | `logs/` |

---

## 四、智能体启动检查清单

> 每个智能体在开始运维工作前，**必须**确认以下事项：

- [ ] 已阅读本规范文件（`运维/AGENTS_OPS_RULES.md`）
- [ ] 所有 `.py`/`.sh` 脚本在 `scripts/` 目录中，根目录无散落脚本
- [ ] 所有 `.log` 文件在 `logs/` 目录中，根目录无散落日志
- [ ] 所有报告输出到 `reports/` 目录（脚本中已正确指定路径）
- [ ] 所有 SSH 远程命令已加 `timeout` 包裹（参考第二节）
- [ ] 不对大型目录执行无 `-maxdepth` 限制的 `find` 命令
- [ ] 本地 `subprocess` 调用已设 `timeout` 参数
- [ ] 脚本执行已添加 `scripts/script_logs.log` 日志记录（参考第六节）
- [ ] 运维操作产生的变更已反哺到对应配置文档（参考第七节）
- [ ] 如果需要创建新脚本，确认已同步更新 `scripts/README.md`

---

## 五、违规处理

| 违规行为 | 处理方式 |
|----------|----------|
| 在根目录创建脚本/日志/报告文件 | 立即移动到正确目录，更新 `scripts/README.md` |
| SSH 命令无 timeout 保护 | 立即停止脚本，修复后重新执行 |
| 产生 `D` 状态幽灵进程 | 记录到 `logs/`，并在 `06_运维操作记录.md` 中说明 |

---

## 六、脚本执行日志强制规范

所有在 `scripts/` 目录中创建和执行的脚本，**必须**维护统一的执行日志文件。

### 日志文件位置

```
scripts/script_logs.log
```

### 日志格式

每条日志记录一行，严格遵循以下格式：

```
[YYYY-MM-DD HH:MM:SS] - [目的描述] - [脚本名称] - [执行结果]
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| 时间 | 脚本开始执行的时间 | `[2026-07-01 17:30:00]` |
| 目的 | 本次执行的目标/用途 | `[磁盘IO性能采集]` |
| 脚本名称 | 执行的脚本文件名 | `[collect_io_metrics.py]` |
| 执行结果 | 成功/失败 + 简要说明 | `[成功]` 或 `[失败: 磁盘已满]` |

### 示例日志

```
[2026-07-01 09:15:00] - [209服务器磁盘IO性能采集] - [collect_io_metrics.py] - [成功]
[2026-07-01 10:30:00] - [清理Airflow僵尸任务] - [fix_stuck_tasks.py] - [成功]
[2026-07-01 14:00:00] - [检测D状态进程] - [check_ghost_processes.py] - [失败: SSH连接超时]
```

### ✅ 强制要求

1. **脚本入口处记录**：在脚本的入口处（或主逻辑开始时）立即写入 `script_logs.log`，记录时间、目的和脚本名称
2. **执行完成后补全结果**：脚本执行完成后，在 `script_logs.log` 中追加（或更新）执行结果
3. **手动执行也要记录**：即使在终端中手动执行脚本，也**必须**手动追加一条日志记录
4. **日志文件由所有脚本共享**：`scripts/script_logs.log` 是所有运维脚本的**共享日志文件**，不按脚本拆分

### Python 示例代码

```python
import os
from datetime import datetime

SCRIPT_LOG = os.path.join(os.path.dirname(__file__), 'script_logs.log')

def log_script_start(purpose: str, script_name: str = None):
    """记录脚本开始执行"""
    if script_name is None:
        script_name = os.path.basename(__file__)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(SCRIPT_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{ts}] - [{purpose}] - [{script_name}] - [开始]\n')

def log_script_result(purpose: str, result: str, script_name: str = None):
    """记录脚本执行结果"""
    if script_name is None:
        script_name = os.path.basename(__file__)
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(SCRIPT_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{ts}] - [{purpose}] - [{script_name}] - [{result}]\n')
```

### Shell 示例

```bash
SCRIPT_LOG="$(dirname "$0")/script_logs.log"
SCRIPT_NAME=$(basename "$0")

echo "[$(date '+%Y-%m-%d %H:%M:%S')] - [目的描述] - [$SCRIPT_NAME] - [开始]" >> "$SCRIPT_LOG"

# ... 执行逻辑 ...

echo "[$(date '+%Y-%m-%d %H:%M:%S')] - [目的描述] - [$SCRIPT_NAME] - [成功]" >> "$SCRIPT_LOG"
```

---

## 七、运维文档反哺强制规范

> **核心原则**：每次运维操作产生的变化，都必须同步回运维文档。
> 这是**智能体自身的责任**，不需要用户提醒或要求。

### 触发条件

以下任一情况发生时，**必须**在**同一会话内**完成文档反哺：

| 触发场景 | 举例 |
|----------|------|
| 修改了运维方式 | 端口配置变更、服务启动方式改变、认证方式切换等 |
| 新增了运维内容 | 创建了新的脚本、工具、检查方案等 |
| 发现了文档错误 | 端口映射写错、配置参数不对、路径不正确等 |
| 解决了历史问题 | 排查了故障并找到根因、发现了文档与实际情况不符 |

### 反哺要求

#### 1. 运维文档更新

| 文档 | 必须更新的内容 |
|------|---------------|
| 服务器目录下的 `*.md` 配置文档 | 新增/变更的服务配置、参数、路径、注意事项 |
| `07_常见问题FAQ.md`（如存在） | 新发现的问题根因、排查步骤、解决方案 |
| `scripts/README.md` | 新增脚本的用途、用法、参数说明 |
| `README.md` | 服务器基本信息的变更（端口、服务等） |

#### 2. 更新格式

```markdown
## 2026-07-02 更新

- 变更内容：xxxx
- 变更原因：xxxx
- 涉及文件：xxxx
```

或直接修改原文中错误的部分（如端口映射写错了，直接修正）。

#### 3. 不需要反哺的场景

- 临时测试（如 `SELECT 1` 之类的验证查询）
- 仅查看信息而未产生任何变更
- 用户明确要求不记录的操作

### 违规后果

| 违规行为 | 处理 |
|----------|------|
| 修改了配置但未更新文档 | 被视为主观失误，下次启动时需补全所有遗漏 |
| 新增脚本但未更新 `scripts/README.md` | 脚本索引不完整，视为智能体责任 |

---

*最后更新：2026-07-02*
*更新原因：新增运维文档反哺规范（第七条），新增脚本执行日志规范（第六条）*
