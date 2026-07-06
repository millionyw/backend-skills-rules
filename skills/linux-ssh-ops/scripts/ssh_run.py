#!/usr/bin/env python3
"""
ssh_run.py — Base template for Linux remote operation scripts (multi-distro).

Usage:
  1. Copy this file to your workspace (e.g., fix_x11_225.py)
  2. Fill in SERVER (name from servers.md, e.g., "225") or HOST/PORT/USER/PWD directly
  3. Replace the "--- Operations ---" section with your commands
  4. Run: python fix_x11_225.py
  5. Check the .log file for results
  6. Delete the script and log after confirming success

Rules enforced by this template:
  - All output written to LOG file (avoids Windows GBK encoding issues)
  - recv_exit_status() always called before reading stdout (avoids output truncation)
  - File writes go via SFTP → /tmp → sudo mv (never heredoc)
  - sudo uses echo pwd | sudo -S pattern
  - All remote commands wrapped with timeout (prevents ghost D-state processes)
  - Distro detection for cross-platform compatibility
"""

import paramiko
import json
import os
import sys

# ─── Configuration ────────────────────────────────────────────────────────────
# Option A: Use server name from config/servers.json
SERVER = "225"  # Change this: use a key from your servers.json

# Option B: Override with direct connection info (takes precedence)
HOST = None     # e.g., "10.211.211.225"
PORT = 22
USER = None     # e.g., "dems"
PWD  = None     # e.g., "your-password"

LOG  = os.path.join(os.path.dirname(__file__) or ".", "operation.log")
# ──────────────────────────────────────────────────────────────────────────────

# Load server registry from config
def _load_servers():
    """Load servers from config/servers.json (searches upward to repo root)."""
    # Walk upward to find config/servers.json
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        candidate = os.path.join(current, "config", "servers.json")
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("servers", {})
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return {}

SERVERS = _load_servers()


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")


def connect():
    # Resolve server info
    if HOST:
        host, port, user, pwd = HOST, PORT, USER or "root", PWD or ""
    elif SERVER in SERVERS:
        info = SERVERS[SERVER]
        host = info["host"]
        port = 22
        user = info.get("user", "root")
        pwd = info.get("password", "")
    else:
        log(f"FATAL: Unknown server '{SERVER}'. Available: {list(SERVERS.keys())}")
        sys.exit(1)

    global PWD
    PWD = pwd  # Update global for run() sudo pattern

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Try key-based auth first
    ssh_dir = os.path.expanduser("~/.ssh")
    if os.path.isdir(ssh_dir):
        for fname in sorted(os.listdir(ssh_dir)):
            fpath = os.path.join(ssh_dir, fname)
            if (fname.endswith(".pub") or fname.endswith(".ppk")
                or fname in ("known_hosts", "known_hosts.old", "config")
                or not os.path.isfile(fpath)):
                continue
            try:
                ssh.connect(host, port, user, key_filename=fpath, timeout=10)
                log(f"Connected to {host} with key: {fname}")
                return ssh
            except Exception:
                pass

    # Fall back to password
    try:
        ssh.connect(host, port, user, password=pwd, timeout=10)
        log(f"Connected to {host} with password auth")
        return ssh
    except Exception as e:
        log(f"FATAL: cannot connect to {host} — {e}")
        sys.exit(1)


def run(ssh, cmd, sudo=False, desc="", timeout=120):
    """
    Execute a remote command.
    - sudo=True: wraps in 'echo pwd | sudo -S bash -c'
    - ALWAYS blocks until command completes via recv_exit_status()
    - Use for simple commands without nested quotes
    """
    if desc:
        log(f"\n[{desc}]")
    log(f"$ {cmd}")

    full_cmd = f"echo '{PWD}' | sudo -S bash -c '{cmd}'" if sudo else cmd
    _, stdout, stderr = ssh.exec_command(full_cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()  # CRITICAL: block-wait

    out = stdout.read().decode(errors="replace").strip()
    err = "\n".join(
        l for l in stderr.read().decode(errors="replace").splitlines()
        if "[sudo]" not in l and "password for" not in l.lower()
    ).strip()

    log(f"exit={exit_code}")
    if out:
        log(f"OUT: {out}")
    if err:
        log(f"ERR: {err}")
    return out, exit_code


def run_with_sudo_pipe(ssh, subcmd, desc="", timeout=30):
    """
    Execute a command that needs sudo but also contains inner quotes.
    Uses 'echo pwd | sudo -S subcmd' WITHOUT bash -c wrapper.
    """
    if desc:
        log(f"\n[{desc}]")
    full_cmd = f"echo '{PWD}' | sudo -S {subcmd}"
    log(f"$ {full_cmd}")

    _, stdout, stderr = ssh.exec_command(full_cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()

    out = stdout.read().decode(errors="replace").strip()
    err = "\n".join(
        l for l in stderr.read().decode(errors="replace").splitlines()
        if "[sudo]" not in l and "password for" not in l.lower()
    ).strip()

    log(f"exit={exit_code}")
    if out:
        log(f"OUT: {out}")
    if err:
        log(f"ERR: {err}")
    return out, exit_code


def write_remote_file(ssh, content, target_path, owner="root", group="root", mode="644"):
    """
    Write content to a remote file safely via SFTP.
    Never use heredoc in exec_command — it truncates files silently.
    """
    tmp_path = f"/tmp/_wb_{os.path.basename(target_path)}"
    log(f"\n[Write remote file → {target_path}]")

    sftp = ssh.open_sftp()
    with sftp.file(tmp_path, "w") as f:
        f.write(content)
    sftp.close()
    log(f"Uploaded to {tmp_path}")

    run(ssh, f"cp {tmp_path} {target_path}", sudo=True, desc="Move to target")
    run(ssh, f"chown {owner}:{group} {target_path}", sudo=True, desc="Chown")
    run(ssh, f"chmod {mode} {target_path}", sudo=True, desc="Chmod")
    run(ssh, f"rm -f {tmp_path}", sudo=False, desc="Clean tmp")

    # Verify — never skip this
    out, _ = run(ssh, f"wc -l {target_path}", sudo=True, desc="Verify line count")
    lines = int(out.split()[0]) if out else 0
    if lines == 0:
        raise RuntimeError(f"FATAL: {target_path} has 0 lines after write — aborting!")
    log(f"Verified: {lines} lines in {target_path}")
    return lines


def detect_distro(ssh):
    """Detect Linux distribution and return (distro, pkg_manager, init_system)."""
    out, _ = run(ssh, "cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null",
                 desc="Detect distro")
    out_lower = out.lower()

    if "ubuntu" in out_lower:
        return "ubuntu", "apt", "systemd"
    elif "openeuler" in out_lower:
        return "openeuler", "dnf", "systemd"
    elif "debian" in out_lower:
        return "debian", "apt", "systemd"
    elif "centos" in out_lower:
        return "centos", "yum", "systemd"
    elif "rhel" in out_lower or "red hat" in out_lower:
        return "rhel", "dnf", "systemd"
    elif "linx" in out_lower:
        return "linx", "apt", "systemd"
    else:
        if run(ssh, "which apt-get")[1] == 0:
            return "unknown-debian-like", "apt", "systemd"
        elif run(ssh, "which dnf")[1] == 0:
            return "unknown-rhel-like", "dnf", "systemd"
        elif run(ssh, "which yum")[1] == 0:
            return "unknown-rhel-like", "yum", "systemd"
        return "unknown", "unknown", "systemd"


def install_packages(ssh, apt_pkgs=None, dnf_pkgs=None, desc=""):
    """Install packages using the correct package manager for the distro."""
    distro, pkg_mgr, _ = detect_distro(ssh)

    if pkg_mgr == "apt":
        pkg_list = apt_pkgs or dnf_pkgs or []
        if not pkg_list:
            return "", 0
        run(ssh, "apt-get update", sudo=True, desc=f"apt update ({desc})")
        pkg_str = " ".join(pkg_list)
        return run(ssh, f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg_str}",
                   sudo=True, desc=f"Install {pkg_str}")
    elif pkg_mgr in ("dnf", "yum"):
        pkg_list = dnf_pkgs or apt_pkgs or []
        if not pkg_list:
            return "", 0
        pkg_str = " ".join(pkg_list)
        return run(ssh, f"{pkg_mgr} install -y {pkg_str}",
                   sudo=True, desc=f"Install {pkg_str}")
    else:
        raise RuntimeError(f"Unsupported package manager: {pkg_mgr}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    open(LOG, "w").close()
    log("=== Operation Start ===")

    ssh = connect()

    try:
        # ─── Distro Detection ───────────────────────────────────────────────
        distro, pkg_mgr, init_sys = detect_distro(ssh)
        log(f"\nDetected: distro={distro}, pkg_manager={pkg_mgr}, init={init_sys}")

        # ─── Operations ────────────────────────────────────────────────────
        # Replace this section with your actual commands.
        # Examples:

        # Simple command:
        # run(ssh, "apt-get update", sudo=True, desc="apt update")

        # Cross-distro install:
        # install_packages(ssh, apt_pkgs=["curl", "wget"], dnf_pkgs=["curl", "wget"],
        #                  desc="Install basic tools")

        # Write a config file:
        # write_remote_file(ssh, CONFIG_CONTENT, "/etc/myapp/config.conf",
        #                   owner="myapp", group="myapp", mode="640")

        # psql command (contains inner quotes — use run_with_sudo_pipe):
        # run_with_sudo_pipe(ssh, "-u postgres psql -c \"SELECT version();\"", desc="PG version")

        # Verify service:
        # run(ssh, "systemctl is-active myservice", sudo=True, desc="Service status")

        out, code = run(ssh, "echo 'hello from $(hostname)'", desc="Sanity check")
        assert code == 0

        # ─── End Operations ────────────────────────────────────────────────

        log("\n=== Operation Complete ===")

    except Exception as e:
        log(f"\nFATAL ERROR: {e}")
        raise
    finally:
        ssh.close()

    print(f"Done. Check log: {LOG}")


if __name__ == "__main__":
    main()
