#!/usr/bin/env python3
"""
install.py — Backend Skills & Rules 安装脚本

功能：
  1. 生成 config/servers.json（交互式输入服务器信息）
  2. 将技能部署到用户指定路径（系统级或项目级），并创建符号链接到 AGENTS 技能目录

用法：
  python install.py                    # 交互式安装（引导式）
  python install.py --config-only      # 仅生成配置文件
  python install.py --deploy-only      # 仅部署技能（配置已存在）
  python install.py --list             # 列出可用技能

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

SUPPORTED_AGENTS_DIRS = {
    "claude": {
        "global": "~/.claude/skills",
        "project": ".claude/skills",
        "name": "Claude Code",
    },
    "trae": {
        "global": "~/.trae/skills",
        "project": ".trae/skills",
        "name": "Trae IDE",
    },
    "cursor": {
        "global": "~/.cursor/skills",
        "project": ".cursor/skills",
        "name": "Cursor",
    },
}

# ── 工具函数 ──────────────────────────────────────────────────────────────────

def prompt(prompt_text, default=None, required=False):
    """交互式输入提示"""
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt_text}{suffix}: ").strip()
        if not value and default:
            return default
        if not value and required:
            print("  ⚠ 此项为必填")
            continue
        return value or None


def prompt_yes_no(prompt_text, default=True):
    """是/否提示"""
    hint = "Y/n" if default else "y/N"
    value = input(f"{prompt_text} [{hint}]: ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes", "是")


def expand_path(path):
    """展开 ~ 和环境变量"""
    return os.path.expanduser(os.path.expandvars(path))


def make_symlink(src, dst):
    """创建符号链接（跨平台兼容）"""
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    if os.path.exists(dst) or os.path.islink(dst):
        if os.path.islink(dst) and os.readlink(dst) == src:
            print(f"  ✓ 链接已存在且正确: {dst} → {src}")
            return True
        if prompt_yes_no(f"  目标已存在: {dst}\n  是否覆盖?", default=False):
            if os.path.islink(dst):
                os.unlink(dst)
            elif os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        else:
            print(f"  ✗ 跳过: {dst}")
            return False

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    try:
        os.symlink(src, dst, target_is_directory=True)
        print(f"  ✓ 链接: {dst} → {src}")
        return True
    except OSError as e:
        # Windows 可能需要管理员权限或开发者模式
        if getattr(e, "winerror", 0) == 1314:
            print(f"  ⚠ Windows 需要管理员权限创建符号链接，改用目录复制")
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✓ 复制: {dst} (来自 {src})")
            return True
        raise


# ── 配置生成 ──────────────────────────────────────────────────────────────────

def generate_config():
    """交互式生成 config/servers.json"""
    print("\n" + "=" * 60)
    print("📝 步骤 1/2: 生成服务器配置")
    print("=" * 60)

    example_path = os.path.join(CONFIG_DIR, "servers.example.json")
    config_path = os.path.join(CONFIG_DIR, "servers.json")

    # 如果已有配置，询问是否覆盖
    if os.path.exists(config_path):
        if not prompt_yes_no("config/servers.json 已存在，是否重新生成?", default=False):
            print("  保留现有配置")
            return True

    # 尝试从 example 复制
    if os.path.exists(example_path):
        if prompt_yes_no("是否基于 servers.example.json 修改?", default=True):
            shutil.copy2(example_path, config_path)
            print(f"\n  ✓ 已复制 example → config/servers.json")
            print(f"  请编辑该文件填入实际服务器信息:")
            print(f"    {config_path}")
            return True

    # 手动输入
    print("\n请输入服务器信息（留空结束添加）:\n")
    servers = {}
    while True:
        name = prompt("服务器名称（如 209、prod1）", required=False)
        if not name:
            break
        host = prompt("  IP 地址", required=True)
        user = prompt("  SSH 用户名", default="root")
        password = prompt("  SSH 密码")
        distro = prompt("  发行版 (ubuntu/debian/openeuler/centos/rhel/linx)", default="ubuntu")

        servers[name] = {
            "host": host,
            "user": user or "root",
            "distro": distro or "ubuntu",
        }
        if password:
            servers[name]["password"] = password
        print()

    subnet = prompt("子网 (如 10.0.0.0/24)", default="10.0.0.0/24")

    config = {
        "servers": servers,
        "network": {
            "subnet": subnet or "10.0.0.0/24",
        },
        "paths": {
            "ops_dir": "运维",
            "ops_rules": "运维/AGENTS_OPS_RULES.md",
        },
    }

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ 配置已写入: {config_path}")
    return True


# ── 技能部署 ──────────────────────────────────────────────────────────────────

def list_skills():
    """列出所有可用技能"""
    print("\n可用技能:")
    print("-" * 50)
    for skill_name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        if os.path.isdir(skill_path):
            skill_md = os.path.join(skill_path, "SKILL.md")
            desc = ""
            if os.path.exists(skill_md):
                with open(skill_md, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("description:"):
                            desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                            break
            print(f"  • {skill_name:25s} {desc[:60]}")
    print()

    print("可用规则:")
    print("-" * 50)
    for rule_name in sorted(os.listdir(RULES_DIR)):
        if rule_name.endswith(".md"):
            print(f"  • {rule_name}")
    print()


def deploy_skills():
    """交互式部署技能"""
    print("\n" + "=" * 60)
    print("🚀 步骤 2/2: 部署技能")
    print("=" * 60)

    # 选择部署级别
    print("\n选择部署级别:")
    print("  1) 系统级 — 所有项目可用，部署到 ~/.agents/skills/")
    print("  2) 项目级 — 仅当前项目可用，部署到 <项目>/.agents/skills/")
    level = prompt("选择 (1/2)", default="1")

    if level == "2":
        project_root = prompt("项目根目录路径", required=True)
        project_root = expand_path(project_root)
        if not os.path.isdir(project_root):
            print(f"  ✗ 目录不存在: {project_root}")
            return False
        agents_root = os.path.join(project_root, ".agents")
    else:
        agents_root = expand_path("~/.agents")

    agents_skills = os.path.join(agents_root, "skills")
    agents_rules = os.path.join(agents_root, "rules")
    agents_config = os.path.join(agents_root, "config")
    os.makedirs(agents_skills, exist_ok=True)
    os.makedirs(agents_rules, exist_ok=True)
    os.makedirs(agents_config, exist_ok=True)

    # 部署技能
    print("\n📦 部署技能:")
    deployed_skills = []
    for skill_name in sorted(os.listdir(SKILLS_DIR)):
        skill_src = os.path.join(SKILLS_DIR, skill_name)
        if not os.path.isdir(skill_src):
            continue

        skill_dst = os.path.join(agents_skills, skill_name)
        if make_symlink(skill_src, skill_dst):
            deployed_skills.append(skill_name)

    # 部署规则
    print("\n📐 部署规则:")
    for rule_name in sorted(os.listdir(RULES_DIR)):
        if not rule_name.endswith(".md"):
            continue
        rule_src = os.path.join(RULES_DIR, rule_name)
        rule_dst = os.path.join(agents_rules, rule_name)
        make_symlink(rule_src, rule_dst)

    # 部署配置
    config_src = os.path.join(CONFIG_DIR, "servers.json")
    config_example = os.path.join(CONFIG_DIR, "servers.example.json")
    config_dst = os.path.join(agents_config, "servers.json")

    if os.path.exists(config_src):
        shutil.copy2(config_src, config_dst)
        print(f"\n  ✓ 配置已复制: {config_dst}")
    elif os.path.exists(config_example):
        print(f"\n  ⚠ 未找到 servers.json，请先运行 --config-only 或手动创建:")
        print(f"    cp {config_example} {config_dst}")
        shutil.copy2(config_example, config_dst)
        print(f"  ✓ 示例配置已复制: {config_dst}")

    # 创建 AGENTS 目录符号链接
    print("\n🔗 链接到 AGENTS 技能目录:")
    for agent_key, agent_info in SUPPORTED_AGENTS_DIRS.items():
        if not prompt_yes_no(f"  链接到 {agent_info['name']}?", default=True):
            continue

        if level == "1":
            target_dir = expand_path(agent_info["global"])
        else:
            target_dir = os.path.join(project_root, agent_info["project"])

        # 为每个已部署的技能创建链接
        for skill_name in deployed_skills:
            src = os.path.join(agents_skills, skill_name)
            dst = os.path.join(target_dir, skill_name)
            make_symlink(src, dst)

    print("\n" + "=" * 60)
    print("✅ 安装完成!")
    print("=" * 60)
    print(f"\n  技能根目录: {agents_root}")
    print(f"  技能: {', '.join(deployed_skills)}")
    print(f"  配置: {agents_config}/servers.json")
    print()
    return True


# ── 主入口 ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Backend Skills & Rules 安装脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python install.py                  # 交互式安装
  python install.py --config-only    # 仅生成配置
  python install.py --deploy-only    # 仅部署技能
  python install.py --list           # 列出可用技能
        """,
    )
    parser.add_argument("--config-only", action="store_true", help="仅生成配置文件")
    parser.add_argument("--deploy-only", action="store_true", help="仅部署技能")
    parser.add_argument("--list", action="store_true", help="列出可用技能")

    args = parser.parse_args()

    if args.list:
        list_skills()
        return

    print()
    print("🛠️  Backend Skills & Rules — 安装向导")
    print()

    if args.config_only:
        generate_config()
    elif args.deploy_only:
        if not os.path.exists(os.path.join(CONFIG_DIR, "servers.json")):
            print("⚠ 未找到配置文件，建议先运行: python install.py --config-only")
            if not prompt_yes_no("是否跳过配置直接部署?", default=False):
                return
        deploy_skills()
    else:
        # 完整安装流程
        generate_config()
        deploy_skills()


if __name__ == "__main__":
    main()
