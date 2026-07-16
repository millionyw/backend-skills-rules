#!/usr/bin/env python3
"""
install.py — Backend Skills & Rules 安装脚本

逐个技能/规则个性化安装：每个条目有独立的配置流程和部署逻辑。

用法：
  python install.py                          # 交互式安装（选择要安装的技能/规则）
  python install.py <序号或名称> [序号或名称]  # 安装指定技能/规则
  python install.py --list                   # 列出可用技能/规则及序号
  python install.py --all                    # 安装全部（逐个配置）

依赖：无（仅使用 Python 标准库）
"""

import argparse
import json
import os
import shutil
import sys

# ── 常量 ──────────────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
SKILLS_DIR = os.path.join(SCRIPT_DIR, "skills")
RULES_DIR = os.path.join(SCRIPT_DIR, "rules")

SUPPORTED_AGENTS = [
    {"key": "claude", "global_dir": "~/.claude/skills", "project_dir": ".claude/skills", "name": "Claude Code"},
    {"key": "trae",   "global_dir": "~/.trae/skills",   "project_dir": ".trae/skills",   "name": "Trae IDE"},
    {"key": "cursor", "global_dir": "~/.cursor/skills",  "project_dir": ".cursor/skills", "name": "Cursor"},
]

# ── 技能/规则注册表 ───────────────────────────────────────────────────────────
# 每个条目定义：序号、名称、类型、描述、配置步骤、部署目标

REGISTRY = [
    {
        "id": 1,
        "name": "linux-ssh-ops",
        "type": "skill",
        "desc": "跨发行版 SSH 运维 (paramiko, 多服务器)",
        "config_steps": ["servers"],
        "deploy_rules": True,   # 顺便部署 AGENTS_OPS_RULES
    },
    {
        "id": 2,
        "name": "sync-to-209",
        "type": "skill",
        "desc": "一键同步文件到远程服务器",
        "config_steps": ["servers", "sync_remote_base"],
        "deploy_rules": False,
    },
    {
        "id": 3,
        "name": "git-add-message",
        "type": "skill",
        "desc": "暂存代码并生成 commit message 条目（ruff 格式审查、智能合并已有条目、禁止 git commit）",
        "config_steps": [],
        "deploy_rules": False,
    },
    {
        "id": 4,
        "name": "git-commit",
        "type": "skill",
        "desc": "完整提交工作流 (ruff → stage → commit → rebase)",
        "config_steps": [],
        "deploy_rules": False,
    },
    {
        "id": 5,
        "name": "managing-tasks",
        "type": "skill",
        "desc": "任务创建与分解 (交付成果导向)",
        "config_steps": ["project_dirs"],
        "deploy_rules": False,
    },
    {
        "id": 6,
        "name": "tracking-progress",
        "type": "skill",
        "desc": "进度对齐与任务归档",
        "config_steps": ["project_dirs"],
        "deploy_rules": False,
    },
    {
        "id": 7,
        "name": "generating-reports",
        "type": "skill",
        "desc": "日报/周报生成 (上下文感知)",
        "config_steps": ["project_dirs"],
        "deploy_rules": False,
    },
    {
        "id": 8,
        "name": "recording-ideas",
        "type": "skill",
        "desc": "想法与经验结构化记录",
        "config_steps": ["project_dirs"],
        "deploy_rules": False,
    },
    {
        "id": 9,
        "name": "work-log-prompt",
        "type": "skill",
        "desc": "工作日志提示 (目的导向格式)",
        "config_steps": ["log_path"],
        "deploy_rules": False,
    },
    {
        "id": 10,
        "name": "global-behavior-rules",
        "type": "rule",
        "desc": "全局行为规则 (工作日志提示)",
        "config_steps": [],
        "deploy_rules": False,
    },
    {
        "id": 11,
        "name": "AGENTS_OPS_RULES",
        "type": "rule",
        "desc": "服务器运维强制规范 (七条规则)",
        "config_steps": ["ops_dir"],
        "deploy_rules": False,
    },
    {
        "id": 12,
        "name": "sync-skills-to-repo",
        "type": "skill",
        "desc": "同步技能/规则到仓库 (更新 install.py + README + 推送 GitHub)",
        "config_steps": [],
        "deploy_rules": False,
    },
    {
        "id": 13,
        "name": "sync-from-209",
        "type": "skill",
        "desc": "从远程服务器同步文件到本地 (dry-run 确认 + 远程验证 + 下载 + 大小校验)",
        "config_steps": ["servers", "sync_remote_base"],
        "deploy_rules": False,
    },
    {
        "id": 14,
        "name": "orm-diff",
        "type": "skill",
        "desc": "ORM 模型 vs 数据库表结构全属性对比 (列名、类型、nullable、default、primary_key)",
        "config_steps": [],
        "deploy_rules": False,
    },
]


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def prompt(prompt_text, default=None, required=False):
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"  {prompt_text}{suffix}: ").strip()
        if not value and default:
            return default
        if not value and required:
            print("    ⚠ 此项为必填")
            continue
        return value or None


def prompt_yes_no(prompt_text, default=True):
    hint = "Y/n" if default else "y/N"
    value = input(f"  {prompt_text} [{hint}]: ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes", "是")


def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def make_symlink(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    if os.path.islink(dst) and os.readlink(dst) == src:
        print(f"    ✓ 链接已存在: {dst}")
        return True
    if os.path.exists(dst) or os.path.islink(dst):
        if not prompt_yes_no(f"目标已存在: {dst}，是否覆盖?", default=False):
            print(f"    ✗ 跳过: {dst}")
            return False
        if os.path.islink(dst):
            os.unlink(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    try:
        os.symlink(src, dst, target_is_directory=True)
        print(f"    ✓ 链接: {dst} → {src}")
        return True
    except OSError as e:
        if getattr(e, "winerror", 0) == 1314:
            print(f"    ⚠ Windows 需要管理员权限创建符号链接，改用目录复制")
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"    ✓ 复制: {dst}")
            return True
        raise


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def resolve_deployment_dir():
    """交互式确定部署根目录"""
    print("\n  选择部署级别:")
    print("    1) 系统级 — ~/.agents/skills/")
    print("    2) 项目级 — <项目>/.agents/skills/")
    level = prompt("选择 (1/2)", default="1")

    if level == "2":
        project_root = prompt("项目根目录路径", required=True)
        project_root = expand_path(project_root)
        if not os.path.isdir(project_root):
            print(f"    ✗ 目录不存在: {project_root}")
            return None, None
        return os.path.join(project_root, ".agents"), project_root
    else:
        return expand_path("~/.agents"), None


def get_agents_target_dirs(agents_root, project_root):
    """获取用户的 AGENTS 技能目录"""
    targets = []
    for agent in SUPPORTED_AGENTS:
        if prompt_yes_no(f"    链接到 {agent['name']}?", default=True):
            if project_root:
                targets.append((agent["name"], os.path.join(project_root, agent["project_dir"])))
            else:
                targets.append((agent["name"], expand_path(agent["global_dir"])))
    return targets


# ── 个性化配置步骤 ─────────────────────────────────────────────────────────────

def config_servers():
    """配置服务器信息 → config/servers.json"""
    config_path = os.path.join(CONFIG_DIR, "servers.json")
    existing = load_json(config_path)

    print("\n    📡 服务器连接信息配置")
    print("    ─────────────────────────")

    if existing.get("servers"):
        print(f"    已有 {len(existing['servers'])} 台服务器配置")
        if prompt_yes_no("是否追加新服务器?", default=True):
            pass
        else:
            return existing

    servers = existing.get("servers", {})
    print("    输入服务器信息（留空结束）:\n")
    while True:
        name = prompt("服务器名称（如 prod1、db-server）")
        if not name:
            break
        if name in servers:
            if not prompt_yes_no(f"服务器 '{name}' 已存在，是否覆盖?", default=False):
                continue
        host = prompt("IP 地址", required=True)
        user = prompt("SSH 用户名", default="root")
        password = prompt("SSH 密码")
        distro = prompt("发行版", default="ubuntu")
        servers[name] = {
            "host": host,
            "user": user or "root",
            "distro": distro or "ubuntu",
        }
        if password:
            servers[name]["password"] = password
        print()

    config = existing
    config["servers"] = servers
    if "network" not in config:
        subnet = prompt("子网", default="192.168.1.0/24")
        config["network"] = {"subnet": subnet}
    if "paths" not in config:
        config["paths"] = {"ops_dir": "运维", "ops_rules": "运维/AGENTS_OPS_RULES.md"}

    save_json(config_path, config)
    print(f"    ✓ 配置已保存: {config_path}")
    return config


def config_sync_remote_base():
    """配置 sync 脚本的远程基础路径"""
    config_path = os.path.join(CONFIG_DIR, "servers.json")
    config = load_json(config_path)

    remote_base = prompt("远程项目根目录", default="/home/user/project")
    config.setdefault("sync", {})["remote_base"] = remote_base

    save_json(config_path, config)
    print(f"    ✓ 同步远程路径已保存: {remote_base}")
    return config


def config_project_dirs():
    """配置项目目录约定"""
    config_path = os.path.join(CONFIG_DIR, "servers.json")
    config = load_json(config_path)

    print("\n    📁 项目目录约定（留空使用默认值）")
    print("    ─────────────────────────")
    tasks_dir = prompt("任务目录", default="tasks")
    logs_dir = prompt("日志目录", default="logs")
    reports_dir = prompt("报告目录", default="reports")

    config["project_dirs"] = {
        "tasks": tasks_dir or "tasks",
        "logs": logs_dir or "logs",
        "reports": reports_dir or "reports",
    }

    save_json(config_path, config)
    print(f"    ✓ 项目目录约定已保存")
    return config


def config_ops_dir():
    """配置运维目录"""
    config_path = os.path.join(CONFIG_DIR, "servers.json")
    config = load_json(config_path)

    ops_dir = prompt("运维文档目录", default="运维")
    config.setdefault("paths", {})
    config["paths"]["ops_dir"] = ops_dir or "运维"
    config["paths"]["ops_rules"] = f"{ops_dir or '运维'}/AGENTS_OPS_RULES.md"

    save_json(config_path, config)
    print(f"    ✓ 运维目录已保存: {config['paths']['ops_dir']}")
    return config


def config_log_path():
    """配置工作日志路径"""
    config_path = os.path.join(CONFIG_DIR, "servers.json")
    config = load_json(config_path)

    log_base = prompt("日志存储根目录", default="logs")
    config["work_log"] = {"base_dir": log_base or "logs"}

    save_json(config_path, config)
    print(f"    ✓ 日志路径已保存: {config['work_log']['base_dir']}")
    return config


# 配置步骤分发
CONFIG_STEP_HANDLERS = {
    "servers": config_servers,
    "sync_remote_base": config_sync_remote_base,
    "project_dirs": config_project_dirs,
    "ops_dir": config_ops_dir,
    "log_path": config_log_path,
}


# ── 部署逻辑 ──────────────────────────────────────────────────────────────────

def deploy_one(entry, agents_root, agents_targets):
    """部署单个技能或规则"""
    name = entry["name"]
    entry_type = entry["type"]

    print(f"\n  {'─' * 50}")
    print(f"  📦 安装: [{entry['id']}] {name} — {entry['desc']}")
    print(f"  {'─' * 50}")

    # 1. 个性化配置
    if entry["config_steps"]:
        print("\n  ⚙️ 配置:")
        for step in entry["config_steps"]:
            handler = CONFIG_STEP_HANDLERS.get(step)
            if handler:
                handler()
            else:
                print(f"    ⚠ 未知配置步骤: {step}")

    # 2. 部署到 agents_root
    if entry_type == "skill":
        src = os.path.join(SKILLS_DIR, name)
        dst = os.path.join(agents_root, "skills", name)
    else:
        src = os.path.join(RULES_DIR, f"{name}.md")
        dst = os.path.join(agents_root, "rules", f"{name}.md")

    if not os.path.exists(src):
        print(f"    ✗ 源不存在: {src}")
        return False

    # 规则是单文件，技能是目录，链接方式不同
    if entry_type == "skill":
        make_symlink(src, dst)
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.islink(dst) and os.readlink(dst) == os.path.abspath(src):
            print(f"    ✓ 链接已存在: {dst}")
        elif os.path.exists(dst):
            if prompt_yes_no(f"目标已存在: {dst}，覆盖?", default=False):
                os.remove(dst) if os.path.islink(dst) else None
                if os.path.isfile(dst):
                    os.remove(dst)
                try:
                    os.symlink(os.path.abspath(src), dst)
                    print(f"    ✓ 链接: {dst}")
                except OSError as e:
                    if getattr(e, "winerror", 0) == 1314:
                        shutil.copy2(os.path.abspath(src), dst)
                        print(f"    ✓ 复制: {dst}")
            else:
                print(f"    ✗ 跳过: {dst}")
        else:
            try:
                os.symlink(os.path.abspath(src), dst)
                print(f"    ✓ 链接: {dst}")
            except OSError as e:
                if getattr(e, "winerror", 0) == 1314:
                    shutil.copy2(os.path.abspath(src), dst)
                    print(f"    ✓ 复制: {dst}")
                else:
                    raise

    # 3. 链接到 AGENTS 技能目录
    for agent_name, target_dir in agents_targets:
        agent_dst = os.path.join(target_dir, name)
        agent_src = os.path.join(agents_root, "skills" if entry_type == "skill" else "rules", name)
        make_symlink(agent_src, agent_dst)

    # 4. 关联规则（如 linux-ssh-ops 需要 AGENTS_OPS_RULES）
    if entry.get("deploy_rules"):
        print(f"\n  📐 关联规则: AGENTS_OPS_RULES")
        rule_entry = next((r for r in REGISTRY if r["name"] == "AGENTS_OPS_RULES"), None)
        if rule_entry and rule_entry not in [entry]:
            deploy_one(rule_entry, agents_root, agents_targets)

    # 5. 部署配置文件
    config_src = os.path.join(CONFIG_DIR, "servers.json")
    if os.path.exists(config_src):
        config_dst = os.path.join(agents_root, "config", "servers.json")
        if not os.path.exists(config_dst):
            os.makedirs(os.path.dirname(config_dst), exist_ok=True)
            shutil.copy2(config_src, config_dst)
            print(f"    ✓ 配置已复制: {config_dst}")

    print(f"\n  ✓ [{entry['id']}] {name} 安装完成")
    return True


# ── 列表 ──────────────────────────────────────────────────────────────────────

def list_all():
    print("\n  可安装的技能与规则:")
    print("  " + "─" * 60)
    print(f"  {'序号':>4s}  {'类型':6s}  {'名称':25s}  说明")
    print("  " + "─" * 60)
    for entry in REGISTRY:
        type_label = "技能" if entry["type"] == "skill" else "规则"
        print(f"  {entry['id']:>4d}  {type_label:6s}  {entry['name']:25s}  {entry['desc']}")
    print("  " + "─" * 60)
    print(f"\n  用法: python install.py 1 3 5    # 安装序号 1、3、5")
    print(f"        python install.py linux-ssh-ops git-commit  # 按名称安装")
    print()


# ── 主入口 ────────────────────────────────────────────────────────────────────

def resolve_entries(selections):
    """将用户输入（序号或名称）解析为注册表条目"""
    entries = []
    for sel in selections:
        # 尝试按序号
        try:
            idx = int(sel)
            entry = next((e for e in REGISTRY if e["id"] == idx), None)
            if entry:
                entries.append(entry)
                continue
        except ValueError:
            pass
        # 按名称
        entry = next((e for e in REGISTRY if e["name"] == sel), None)
        if entry:
            entries.append(entry)
        else:
            print(f"  ⚠ 未找到: {sel}")
    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Backend Skills & Rules 安装脚本（按技能/规则个性化安装）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python install.py                          # 交互式选择安装
  python install.py --list                   # 列出可用技能/规则及序号
  python install.py 1                        # 安装 linux-ssh-ops
  python install.py 1 2                      # 安装序号 1 和 2
  python install.py linux-ssh-ops git-commit # 按名称安装
  python install.py --all                    # 安装全部（逐个配置）
        """,
    )
    parser.add_argument("items", nargs="*", help="要安装的技能/规则序号或名称")
    parser.add_argument("--list", action="store_true", help="列出可用技能/规则及序号")
    parser.add_argument("--all", action="store_true", help="安装全部（逐个配置）")

    args = parser.parse_args()

    if args.list:
        list_all()
        return

    print()
    print("  🛠️  Backend Skills & Rules — 安装向导")
    print()

    # 确定要安装的条目
    if args.all:
        entries = list(REGISTRY)
    elif args.items:
        entries = resolve_entries(args.items)
        if not entries:
            print("  ⚠ 没有匹配的技能/规则，请使用 --list 查看")
            return
    else:
        # 交互式选择
        list_all()
        selection = prompt("输入要安装的序号或名称（空格分隔，如 1 3 5 或 linux-ssh-ops）")
        if not selection:
            print("  未选择任何技能/规则，退出")
            return
        entries = resolve_entries(selection.split())
        if not entries:
            print("  ⚠ 没有匹配的技能/规则")
            return

    # 确定部署目录
    agents_root, project_root = resolve_deployment_dir()
    if not agents_root:
        return

    os.makedirs(os.path.join(agents_root, "skills"), exist_ok=True)
    os.makedirs(os.path.join(agents_root, "rules"), exist_ok=True)
    os.makedirs(os.path.join(agents_root, "config"), exist_ok=True)

    # 获取 AGENTS 目标目录
    print("\n  🔗 链接到 AGENTS 技能目录:")
    agents_targets = get_agents_target_dirs(agents_root, project_root)

    # 逐个安装
    print("\n" + "=" * 60)
    print(f"  将安装 {len(entries)} 个项目")
    print("=" * 60)

    # 去重（linux-ssh-ops 会触发 AGENTS_OPS_RULES，避免重复）
    installed = set()
    for entry in entries:
        if entry["name"] in installed:
            continue
        deploy_one(entry, agents_root, agents_targets)
        installed.add(entry["name"])

    print("\n" + "=" * 60)
    print("  ✅ 全部安装完成!")
    print("=" * 60)
    print(f"\n  技能根目录: {agents_root}")
    print(f"  配置文件: {os.path.join(agents_root, 'config', 'servers.json')}")
    print(f"  已安装: {', '.join(installed)}")
    print()


if __name__ == "__main__":
    main()
