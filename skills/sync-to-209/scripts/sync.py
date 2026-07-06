#!/usr/bin/env python3
"""
同步文件/目录到 209 服务器（paramiko + 密码登录）

用法:
    python sync.py <路径1> [路径2] ...          # 同步文件或目录
    python sync.py -e "命令" <路径1> ...         # 同步后在远程执行命令

路径相对于项目根目录，支持正斜杠或反斜杠。
"""
import argparse
import os
import sys

try:
    import paramiko
except ImportError:
    sys.exit("[ERROR] 缺少 paramiko，请执行: pip install paramiko")

# ── 服务器配置（按实际环境修改）────────────────────────
HOST = "10.211.211.209"
USER = "dems"
PASSWORD = "win2022@dems"
REMOTE_BASE = "/home/dems/tsysmart/rtdbpy"
# ─────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))


def collect_files(paths):
    """将输入路径展开为相对路径列表（目录递归展开）"""
    skip_dirs = {"__pycache__", ".git", "node_modules", ".venv", "venv"}
    skip_exts = {".pyc", ".pyo"}
    result = []
    for p in paths:
        p = p.replace("\\", "/")
        full = os.path.join(PROJECT_ROOT, p.replace("/", os.sep))
        if os.path.isfile(full):
            result.append(p)
        elif os.path.isdir(full):
            for root, dirs, files in os.walk(full):
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                for f in files:
                    if os.path.splitext(f)[1] in skip_exts:
                        continue
                    abs_f = os.path.join(root, f)
                    rel = os.path.relpath(abs_f, PROJECT_ROOT).replace(os.sep, "/")
                    result.append(rel)
        else:
            print(f"[SKIP] 不存在: {p}")
    return result


def ensure_remote_dir(sftp, remote_dir):
    """递归创建远程目录"""
    if remote_dir in ("", "/"):
        return
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        parent = os.path.dirname(remote_dir).replace("\\", "/")
        ensure_remote_dir(sftp, parent)
        sftp.mkdir(remote_dir)


def sync_files(client, sftp, rel_paths):
    """上传文件并验证大小，返回 (成功数, 失败列表)"""
    ok_count = 0
    failed = []
    for rel in rel_paths:
        local = os.path.join(PROJECT_ROOT, rel.replace("/", os.sep))
        remote = f"{REMOTE_BASE}/{rel}"
        remote_dir = os.path.dirname(remote).replace("\\", "/")

        ensure_remote_dir(sftp, remote_dir)

        print(f"[>>] {rel}")
        sftp.put(local, remote)

        local_size = os.path.getsize(local)
        remote_size = sftp.stat(remote).st_size
        if local_size == remote_size:
            print(f"    OK ({local_size} bytes)")
            ok_count += 1
        else:
            print(f"    MISMATCH local={local_size} remote={remote_size}")
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
    parser = argparse.ArgumentParser(description="同步文件到 209 服务器")
    parser.add_argument("paths", nargs="*", help="要同步的文件或目录（相对项目根目录）")
    parser.add_argument("-e", "--exec", dest="remote_cmd", default=None,
                        help="同步后在远程执行的命令")
    args = parser.parse_args()

    if not args.paths and not args.remote_cmd:
        parser.print_help()
        sys.exit(1)

    print(f"[目标] {USER}@{HOST}:{REMOTE_BASE}")

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
        if args.paths:
            rel_paths = collect_files(args.paths)
            if not rel_paths:
                print("[WARN] 没有需要同步的文件")
            else:
                print(f"[INFO] 共 {len(rel_paths)} 个文件待同步")
                ok, failed = sync_files(client, sftp, rel_paths)
                print(f"\n[DONE] 成功={ok} 失败={len(failed)}")
                if failed:
                    print(f"[FAIL] 失败文件: {failed}")

        if args.remote_cmd:
            run_remote_command(client, args.remote_cmd)
    finally:
        sftp.close()
        client.close()
        print("[--] 连接已关闭")


if __name__ == "__main__":
    main()
