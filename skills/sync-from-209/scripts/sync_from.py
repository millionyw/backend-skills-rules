#!/usr/bin/env python3
"""
从 209 服务器同步文件/目录到本地（paramiko + 密码登录）

用法:
    python sync_from.py <路径1> [路径2] ...          # 拉取文件或目录
    python sync_from.py -e "命令" <路径1> ...         # 拉取前在远程执行命令

路径相对于项目根目录，支持正斜杠或反斜杠。
"""
import argparse
import json
import os
import sys

try:
    import paramiko
except ImportError:
    sys.exit("[ERROR] 缺少 paramiko，请执行: pip install paramiko")

# ── 服务器配置（自动从 config/servers.json 读取）─────────────────

def _load_server_config(server_name="209"):
    """从 config/servers.json 读取服务器配置"""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        candidate = os.path.join(current, "config", "servers.json")
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("servers", {})
            if server_name in servers:
                return servers[server_name]
            else:
                sys.exit(f"[ERROR] 服务器 '{server_name}' 未在 config/servers.json 中找到。可用: {list(servers.keys())}")
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None

# 默认读取 "209" 服务器配置；如需修改，改下方 SERVER_NAME
SERVER_NAME = "209"
_config = _load_server_config(SERVER_NAME) or {}

HOST = _config.get("host", "10.0.0.209")
USER = _config.get("user", "root")
PASSWORD = _config.get("password", "")
REMOTE_BASE = "/home/dems/tsysmart/rtdbpy"  # 按实际项目修改
# ─────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "venv"}
SKIP_EXTS = {".pyc", ".pyo"}


def list_remote_files(sftp, remote_dir):
    """递归列出远程目录下的文件，返回相对路径列表；目录不存在返回 None"""
    result = []
    try:
        entries = sftp.listdir_attr(remote_dir)
    except FileNotFoundError:
        return None

    for entry in entries:
        name = entry.filename
        if name in SKIP_DIRS:
            continue
        full_path = f"{remote_dir}/{name}"
        if entry.st_mode & 0o040000:  # 目录
            sub = list_remote_files(sftp, full_path)
            if sub is not None:
                result.extend(sub)
        else:
            ext = os.path.splitext(name)[1]
            if ext in SKIP_EXTS:
                continue
            rel = full_path[len(REMOTE_BASE) + 1:]
            result.append(rel)
    return result


def collect_remote_paths(sftp, paths):
    """将输入路径展开为远程相对路径列表，验证远程是否存在"""
    result = []
    for p in paths:
        p = p.replace("\\", "/")
        remote = f"{REMOTE_BASE}/{p}"

        try:
            attr = sftp.stat(remote)
        except FileNotFoundError:
            alt = remote.rstrip("/")
            if alt != remote:
                try:
                    attr = sftp.stat(alt)
                    remote = alt
                except FileNotFoundError:
                    print(f"[NOT_FOUND] 远程不存在: {p}")
                    continue
            else:
                print(f"[NOT_FOUND] 远程不存在: {p}")
                continue

        if attr.st_mode & 0o040000:  # 目录
            sub = list_remote_files(sftp, remote)
            if sub is None:
                print(f"[NOT_FOUND] 远程目录无法读取: {p}")
            elif not sub:
                print(f"[SKIP] 远程目录为空: {p}")
            else:
                result.extend(sub)
        else:
            rel = remote[len(REMOTE_BASE) + 1:]
            result.append(rel)
    return result


def ensure_local_dir(local_path):
    """确保本地目录存在"""
    d = os.path.dirname(local_path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def sync_files(sftp, rel_paths):
    """下载文件并验证大小，返回 (成功数, 失败列表)"""
    ok_count = 0
    failed = []
    for rel in rel_paths:
        remote = f"{REMOTE_BASE}/{rel}"
        local = os.path.join(PROJECT_ROOT, rel.replace("/", os.sep))

        ensure_local_dir(local)

        print(f"[<<] {rel}")
        try:
            sftp.get(remote, local)
        except Exception as e:
            print(f"    DOWNLOAD FAILED: {e}")
            failed.append(rel)
            continue

        remote_size = sftp.stat(remote).st_size
        local_size = os.path.getsize(local)
        if local_size == remote_size:
            print(f"    OK ({local_size} bytes)")
            ok_count += 1
        else:
            print(f"    MISMATCH remote={remote_size} local={local_size}")
            failed.append(rel)
    return ok_count, failed


def run_remote_command(client, cmd):
    """在远程执行命令并打印输出"""
    print(f"\n[EXEC] {cmd}")
    _, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    code = stdout.channel.recv_exit_status()
    if out:
        print(out)
    if err:
        print(f"[STDERR] {err}")
    print(f"[EXIT] {code}")
    return code


def main():
    parser = argparse.ArgumentParser(description="从 209 服务器同步文件到本地")
    parser.add_argument("paths", nargs="*", help="要拉取的文件或目录（相对项目根目录）")
    parser.add_argument("-e", "--exec", dest="remote_cmd", default=None,
                        help="拉取前在远程执行的命令")
    args = parser.parse_args()

    if not args.paths and not args.remote_cmd:
        parser.print_help()
        sys.exit(1)

    print(f"[来源] {USER}@{HOST}:{REMOTE_BASE}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=HOST, port=22, username=USER, password=PASSWORD,
            allow_agent=False, look_for_keys=False, timeout=15,
        )
    except Exception as e:
        sys.exit(f"[FAIL] 连接失败: {e}")
    print(f"[OK] 已连接 {USER}@{HOST}")

    sftp = client.open_sftp()
    try:
        if args.remote_cmd:
            run_remote_command(client, args.remote_cmd)

        if args.paths:
            rel_paths = collect_remote_paths(sftp, args.paths)
            if not rel_paths:
                print("[WARN] 没有需要拉取的文件（远程路径均不存在或目录为空）")
            else:
                print(f"[INFO] 共 {len(rel_paths)} 个文件待拉取")
                ok, failed = sync_files(sftp, rel_paths)
                print(f"\n[DONE] 成功={ok} 失败={len(failed)}")
                if failed:
                    print(f"[FAIL] 失败文件: {failed}")
    finally:
        sftp.close()
        client.close()
        print("[--] 连接已关闭")


if __name__ == "__main__":
    main()
