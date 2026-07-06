# Paramiko SSH Operation Patterns (Multi-Distro)

Ready-to-use code patterns for Linux remote operations via paramiko. Supports Ubuntu, Debian, openEuler, CentOS/RHEL, and Linx.

---

## 1. Standard Connection (Key + Password Fallback)

```python
import paramiko
import os

def connect(host, port=22, user="dems", password=None):
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
                log(f"Connected with key: {fname}")
                return ssh
            except Exception:
                pass

    # Fall back to password
    if password:
        try:
            ssh.connect(host, port, user, password=password, timeout=10)
            log(f"Connected with password auth")
            return ssh
        except Exception as e:
            log(f"FATAL: password auth failed — {e}")
            raise ConnectionError(f"Cannot connect to {host}: {e}")

    raise ConnectionError("All authentication methods failed")
```

---

## 2. run() — Execute Remote Command with sudo Support

```python
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
```

---

## 3. run_with_sudo_pipe() — Commands with Inner Quotes

```python
def run_with_sudo_pipe(ssh, subcmd, desc="", timeout=30):
    """
    Execute a command that needs sudo but also contains inner quotes.
    Uses 'echo pwd | sudo -S subcmd' WITHOUT bash -c wrapper.
    Example: run_with_sudo_pipe(ssh, "-u postgres psql -c \"ALTER USER ...;\"")
    → executes: echo 'pwd' | sudo -S -u postgres psql -c "ALTER USER ...;"
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
```

---

## 4. write_remote_file() — Safe Remote File Write via SFTP

```python
def write_remote_file(ssh, content, target_path, owner="root", group="root", mode="644"):
    """
    Write content to a remote file safely via SFTP.
    Never use heredoc in exec_command — it truncates files silently.
    """
    tmp_path = f"/tmp/_wb_{os.path.basename(target_path)}"
    log(f"\n[Write remote file → {target_path}]")

    # Upload via SFTP
    sftp = ssh.open_sftp()
    with sftp.file(tmp_path, "w") as f:
        f.write(content)
    sftp.close()
    log(f"Uploaded to {tmp_path}")

    # Move to target
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
```

---

## 5. log() — File-Based Logging (Required for Windows Host)

```python
import os

LOG = "C:/path/to/operation.log"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

# At script start:
open(LOG, "w").close()
log("=== Operation Start ===")
```

---

## 6. detect_distro() — Distro Detection

```python
def detect_distro(ssh):
    """Detect Linux distribution and return (distro, pkg_manager, init_system)."""
    out, _ = run(ssh, "cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null")
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
        # Fallback: check which package manager exists
        if run(ssh, "which apt-get")[1] == 0:
            return "unknown-debian-like", "apt", "systemd"
        elif run(ssh, "which dnf")[1] == 0:
            return "unknown-rhel-like", "dnf", "systemd"
        elif run(ssh, "which yum")[1] == 0:
            return "unknown-rhel-like", "yum", "systemd"
        return "unknown", "unknown", "systemd"
```

---

## 7. install_packages() — Cross-Distro Package Install

```python
def install_packages(ssh, packages, desc=""):
    """
    Install packages using the correct package manager for the distro.
    packages: dict with keys 'apt' and 'dnf', values are list of package names.
    Example: install_packages(ssh, {'apt': ['xorg-x11-xauth'], 'dnf': ['xorg-x11-xauth']})
    """
    distro, pkg_mgr, _ = detect_distro(ssh)

    if pkg_mgr == "apt":
        pkg_list = packages.get("apt", packages.get("dnf", []))
        if not pkg_list:
            return "", 0
        run(ssh, "apt-get update", sudo=True, desc=f"apt update ({desc})")
        pkg_str = " ".join(pkg_list)
        return run(ssh, f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg_str}",
                   sudo=True, desc=f"Install {pkg_str}")
    elif pkg_mgr in ("dnf", "yum"):
        pkg_list = packages.get("dnf", packages.get("apt", []))
        if not pkg_list:
            return "", 0
        pkg_str = " ".join(pkg_list)
        return run(ssh, f"{pkg_mgr} install -y {pkg_str}",
                   sudo=True, desc=f"Install {pkg_str}")
    else:
        raise RuntimeError(f"Unsupported package manager: {pkg_mgr}")
```

---

## 8. Node.js Binary Install Pattern (Cross-Distro)

```python
NODE_VERSION = "22.13.1"
NODE_ARCH = "linux-x64"
NODE_TARBALL = f"node-v{NODE_VERSION}-{NODE_ARCH}.tar.xz"
NODE_URL = f"https://nodejs.org/dist/v{NODE_VERSION}/{NODE_TARBALL}"
NODE_INSTALL_DIR = "/usr/local/lib/nodejs"

steps = [
    f"wget -q {NODE_URL} -O /tmp/{NODE_TARBALL}",
    f"mkdir -p {NODE_INSTALL_DIR}",
    f"tar -xJf /tmp/{NODE_TARBALL} -C {NODE_INSTALL_DIR} --strip-components=1",
    f"rm /tmp/{NODE_TARBALL}",
    f"ln -sf {NODE_INSTALL_DIR}/bin/node /usr/local/bin/node",
    f"ln -sf {NODE_INSTALL_DIR}/bin/npm /usr/local/bin/npm",
    f"ln -sf {NODE_INSTALL_DIR}/bin/npx /usr/local/bin/npx",
    "node --version",
    "npm --version",
]
for step in steps:
    out, code = run(ssh, step, sudo=True)
    assert code == 0, f"FAILED: {step}"
```

---

## 9. X11 Forwarding Diagnostic Pattern

```python
def diagnose_x11(ssh):
    """Check X11 forwarding prerequisites on a remote server."""
    results = []

    # 1. Check xauth
    out, code = run(ssh, "which xauth", desc="Check xauth")
    if code != 0:
        results.append("MISSING: xauth not installed")
    else:
        results.append(f"OK: xauth at {out}")

    # 2. Check xorg-x11-xauth package
    out, code = run(ssh, "rpm -qa xorg-x11-xauth 2>/dev/null || dpkg -l xorg-x11-xauth 2>/dev/null", desc="Check xauth package")
    if code != 0 and not out:
        results.append("MISSING: xorg-x11-xauth package not installed")
    else:
        results.append(f"OK: xauth package installed ({out.strip()})")

    # 3. Check sshd_config X11Forwarding
    out, _ = run(ssh, "grep -i X11Forwarding /etc/ssh/sshd_config", sudo=True, desc="Check sshd X11 config")
    if "yes" in out.lower():
        results.append("OK: X11Forwarding yes in sshd_config")
    else:
        results.append("MISSING: X11Forwarding not set to yes in sshd_config")

    # 4. Check X11UseLocalhost
    out, _ = run(ssh, "grep -i X11UseLocalhost /etc/ssh/sshd_config", sudo=True, desc="Check X11UseLocalhost")
    if out and "no" in out.lower():
        results.append("NOTE: X11UseLocalhost no (may be needed for some setups)")

    # 5. Check DISPLAY (only meaningful in real SSH session, not paramiko)
    out, _ = run(ssh, "echo $DISPLAY", desc="Check DISPLAY env")
    if out:
        results.append(f"OK: DISPLAY={out}")
    else:
        results.append("WARNING: DISPLAY is empty (expected for paramiko — needs real SSH with -X)")

    return results
```

---

## 10. Standard pg_hba.conf Content

Always use this as the base — never omit the `local` and `127.0.0.1` rules:

```python
PG_HBA_CONTENT = """\
# PostgreSQL Client Authentication Configuration
# TYPE  DATABASE  USER      ADDRESS               METHOD

# Unix socket - postgres system user (peer, no password)
local   all       postgres                        peer

# Unix socket - all other users
local   all       all                             md5

# TCP loopback IPv4
host    all       all       127.0.0.1/32          md5

# TCP loopback IPv6
host    all       all       ::1/128               md5

# Internal network remote access (adjust subnet from config/servers.json → network.subnet)
host    all       all       YOUR_SUBNET_HERE      md5
"""
```

---

## 11. Firewall Management (Cross-Distro)

```python
def open_port(ssh, port, proto="tcp", permanent=True):
    """Open a firewall port. Works with firewalld (openEuler/CentOS) or ufw (Ubuntu)."""
    distro, _, _ = detect_distro(ssh)

    if distro in ("openeuler", "centos", "rhel"):
        # firewalld
        perm_flag = " --permanent" if permanent else ""
        run(ssh, f"firewall-cmd --add-port={port}/{proto}{perm_flag}",
            sudo=True, desc=f"Open port {port}/{proto}")
        if permanent:
            run(ssh, "firewall-cmd --reload", sudo=True, desc="Reload firewalld")
    elif distro in ("ubuntu", "debian", "linx"):
        # ufw
        run(ssh, f"ufw allow {port}/{proto}", sudo=True, desc=f"Open port {port}/{proto}")
    else:
        log(f"WARNING: Unknown distro, skipping firewall config for port {port}")
```
