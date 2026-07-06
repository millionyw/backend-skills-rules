---
name: linux-ssh-ops
description: This skill should be used when performing remote operations on ANY Linux server via SSH using Python paramiko. It generalizes the proven patterns from ubuntu-ssh-ops to support multiple distros (Ubuntu, Debian, openEuler, CentOS/RHEL, Linx) and multiple servers. Triggers include connecting to servers mentioned in 运维/ directory READMEs, running diagnostic commands, installing software, writing config files, managing services, and any task requiring SSH remote execution. Always use this skill when the user mentions a server IP or asks to do something on a remote Linux server.
---

# Linux SSH Remote Operations (Multi-Distro)

## Overview

This skill encodes hard-won operational experience for remote Linux server management via Python paramiko, generalized from Ubuntu-specific patterns to support **all distros** in the current environment. It prevents common pitfalls: output being swallowed, heredoc file corruption, sudo authentication failures, distro-specific package manager differences, and ghost processes.

**Read `references/paramiko-patterns.md`** for ready-to-use code templates.
**Read `references/servers.md`** for server connection info (IPs, users, passwords, distros).
**Use `scripts/ssh_run.py`** as a base for new operation scripts.

---

## Distro Detection & Package Manager Mapping

**Always detect the distro first** before running any package install command:

```python
def detect_distro(ssh):
    """Detect Linux distribution and return (distro, pkg_manager, init_system)."""
    out, _ = run(ssh, "cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null")
    out_lower = out.lower()

    if "ubuntu" in out_lower:
        return "ubuntu", "apt", "systemd"
    elif "debian" in out_lower:
        return "debian", "apt", "systemd"
    elif "openeuler" in out_lower:
        return "openeuler", "dnf", "systemd"
    elif "centos" in out_lower:
        return "centos", "yum", "systemd"
    elif "rhel" in out_lower or "red hat" in out_lower:
        return "rhel", "dnf", "systemd"
    elif "linx" in out_lower:
        return "linx", "apt", "systemd"  # Linx is Debian-based
    else:
        # Fallback: check which package manager exists
        if run(ssh, "which apt-get")[1] == 0:
            return "unknown", "apt", "systemd"
        elif run(ssh, "which dnf")[1] == 0:
            return "unknown", "dnf", "systemd"
        elif run(ssh, "which yum")[1] == 0:
            return "unknown", "yum", "systemd"
        return "unknown", "unknown", "systemd"
```

### Package Install Commands by Distro

| Distro | Install | Update | Service Enable | Service Start |
|--------|---------|--------|----------------|---------------|
| Ubuntu/Debian/Linx | `apt-get install -y` | `apt-get update` | `systemctl enable` | `systemctl start` |
| openEuler/CentOS/RHEL | `dnf install -y` | `dnf makecache` | `systemctl enable` | `systemctl start` |

---

## Rule 1: Always Load Server Info from `references/servers.md`

**Problem:** Hardcoding IP/password in scripts is fragile and insecure. Server info may change.

**Mandatory approach:**
1. Read `references/servers.md` to get the server's IP, user, password, and distro
2. If the server is not listed, ask the user for connection details
3. If the user mentions a server by name (e.g., "225 服务器"), look up its info in `references/servers.md`
4. Also check the server's dedicated README under `运维/` directory for special notes

```python
# Example: connect to 225 server
from references.servers import get_server  # conceptually
HOST = "10.211.211.225"
USER = "dems"
PWD  = "win2022@dems"
```

---

## Rule 2: Install Software with the Right Package Manager

**Problem:** Ubuntu uses `apt`, openEuler/CentOS uses `dnf/yum`. Package names differ across distros.

**Cross-distro install pattern:**

```python
def install_package(ssh, pkg_name_apt, pkg_name_dnf=None, desc=""):
    """Install a package using the correct package manager for the distro."""
    distro, pkg_mgr, _ = detect_distro(ssh)

    if pkg_mgr == "apt":
        run(ssh, "apt-get update", sudo=True, desc=f"apt update ({desc})")
        run(ssh, f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pkg_name_apt}",
            sudo=True, desc=f"Install {pkg_name_apt}")
    elif pkg_mgr in ("dnf", "yum"):
        cmd = pkg_mgr  # dnf or yum
        dnf_pkg = pkg_name_dnf or pkg_name_apt  # fallback to apt name if no dnf name given
        run(ssh, f"{cmd} install -y {dnf_pkg}", sudo=True, desc=f"Install {dnf_pkg}")
    else:
        raise RuntimeError(f"Unsupported package manager: {pkg_mgr}")
```

**Common package name mapping:**

| Function | apt (Ubuntu/Debian) | dnf (openEuler/CentOS) |
|----------|---------------------|------------------------|
| SSH server | `openssh-server` | `openssh-server` |
| X11 auth | `xorg-x11-xauth` | `xorg-x11-xauth` |
| X11 apps | `xorg-x11-apps` | `xorg-x11-apps` |
| curl/wget | `curl`, `wget` | `curl`, `wget` |
| Docker | See Docker docs | See Docker docs |
| PostgreSQL | `postgresql-17` (pgdg) | `postgresql-server` |
| Node.js | Binary install (see Rule 8) | Binary install (see Rule 8) |
| GDM | `gdm3` | `gdm` |
| GNOME | `gnome-shell` | `gnome-shell` |

---

## Rule 3: Never Write Remote Files via Shell Heredoc in exec_command

**Problem:** `paramiko.exec_command()` does not provide a real interactive shell. Heredoc (`cat > file << 'EOF'`) behaves unpredictably — the file may be truncated to 0 bytes or contain only partial content, silently destroying existing configuration.

**This will corrupt files — never do this:**
```python
ssh.exec_command("cat > /etc/postgresql/16/main/postgresql.conf << 'EOF'\n...\nEOF")
```

**Correct approach — always use SFTP for file writes:**
```python
sftp = ssh.open_sftp()
with sftp.file("/tmp/myconfig.conf", "w") as f:
    f.write(config_content)
sftp.close()
# Then move with sudo
run(f"echo '{PWD}' | sudo -S cp /tmp/myconfig.conf /etc/target/config.conf")
run(f"echo '{PWD}' | sudo -S chown root:root /etc/target/config.conf")
run(f"echo '{PWD}' | sudo -S chmod 644 /etc/target/config.conf")
```

**After every file write, verify immediately:**
```python
result = run("sudo wc -l /etc/target/config.conf")
# Ensure line count is non-zero
```

---

## Rule 4: Correct sudo Usage in paramiko

**Problem:** `exec_command("sudo cmd")` hangs or fails because sudo requires a terminal for password input. Double-quoting in `sudo bash -c "cmd with 'quotes'"` causes bash to misparse the inner command.

**Pattern A — simple commands (no nested quotes):**
```python
def run(ssh, cmd, sudo=False, desc="", timeout=120):
    if sudo:
        full_cmd = f"echo '{PWD}' | sudo -S bash -c '{cmd}'"
    else:
        full_cmd = cmd
    _, stdout, stderr = ssh.exec_command(full_cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()  # always block-wait
    # ... (see paramiko-patterns.md for full implementation)
```

**Pattern B — commands with inner quotes (e.g., psql -c "SQL"):**
```python
# Pass directly to the target binary, not via bash -c
run_direct(ssh, f"sudo -S -u postgres psql -c \"{sql}\"", stdin_data=f"{PWD}\n")
```

**Pattern C — complex multi-line commands:**
- Write the logic as a temporary shell script
- Upload via SFTP to `/tmp/op_script.sh`
- Execute: `sudo bash /tmp/op_script.sh`
- Remove after use

**Always use `recv_exit_status()` to block until command completes — never read stdout before the command finishes.**

---

## Rule 5: Always Write Diagnostic Output to Log Files

**Problem:** On Windows hosts, PowerShell pipes and terminal encoding (GBK vs UTF-8) silently swallow `print()` output. stdout may appear empty even when the remote command ran and produced output.

**Mandatory logging pattern:**
```python
LOG = "C:/path/to/operation.log"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# In run():
log(f"[{desc}] exit={exit_code}")
if out: log(f"OUT: {out}")
if err: log(f"ERR: {err}")
```

---

## Rule 6: Prevent Ghost Processes (D-state)

**Problem:** Commands without timeout can hang in D (uninterruptible sleep) state on I/O-saturated servers, making them unkillable and driving load averages through the roof.

**Mandatory: all SSH remote commands must use timeout:**
```python
# Always wrap with `timeout` command
stdin, stdout, stderr = ssh.exec_command(
    'timeout 30 find /home/dems -name "*.py" 2>/dev/null || true',
    timeout=40   # paramiko timeout > command timeout
)
```

**Never run deep `find` on large directories without `-maxdepth`.**

---

## Rule 7: Service Management is Distro-Agnostic (systemd)

All target servers use systemd. Service management commands are the same across distros:

```python
# Check status
run(ssh, "systemctl is-active servicename", sudo=True)
run(ssh, "systemctl status servicename --no-pager", sudo=True)

# Enable and start
run(ssh, "systemctl enable servicename", sudo=True)
run(ssh, "systemctl start servicename", sudo=True)

# Restart and reload
run(ssh, "systemctl restart servicename", sudo=True)
run(ssh, "systemctl reload servicename", sudo=True)

# Check listening ports
run(ssh, "ss -tlnp", sudo=True)
```

---

## Rule 8: Node.js Binary Install (Cross-Distro)

**Problem:** System package managers lag behind. NodeSource is unreliable. Binary install works everywhere.

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

## Rule 9: SSH X11 Forwarding Debugging

**Problem:** Qt/GUI applications fail with `could not connect to display` over SSH.

**Diagnostic checklist:**
1. Check `xorg-x11-xauth` is installed
2. Check `/etc/ssh/sshd_config` has `X11Forwarding yes`
3. Restart sshd after config change
4. Reconnect SSH (X11 forwarding is established at connect time)
5. Verify `echo $DISPLAY` shows a value (e.g., `localhost:10.0`)

```python
# Diagnose X11 forwarding
def diagnose_x11(ssh):
    """Check X11 forwarding prerequisites on a remote server."""
    distro, pkg_mgr, _ = detect_distro(ssh)

    # Check xauth
    out, code = run(ssh, "which xauth")
    if code != 0:
        return "MISSING: xauth not installed. Install with: {apt|dnf} install xorg-x11-xauth"

    # Check sshd_config
    out, _ = run(ssh, "grep -i X11Forwarding /etc/ssh/sshd_config", sudo=True)
    if "yes" not in out:
        return "MISSING: X11Forwarding not enabled in sshd_config"

    # Check DISPLAY (only meaningful in current SSH session, not from paramiko)
    out, _ = run(ssh, "echo $DISPLAY")
    if not out:
        return "WARNING: DISPLAY is empty (expected for paramiko — needs real SSH with -X)"

    return "X11 forwarding prerequisites OK"
```

---

## Rule 10: Follow AGENTS_OPS_RULES.md for All Operations

**Before any server operation**, read `E:/2026_work_schedule/运维/AGENTS_OPS_RULES.md` for:
- Directory structure rules (scripts/, reports/, logs/)
- Ghost process prevention (timeout on all commands)
- Script execution logging (scripts/script_logs.log)
- Documentation back-feed requirements

---

## Workflow: Connecting to a Server

When the user asks to do something on a server:

1. **Identify the server** — look up `references/servers.md` for IP/user/password/distro
2. **Read server-specific notes** — check `运维/<server-dir>/README.md` for special config
3. **Connect** — use `connect()` from `references/paramiko-patterns.md`
4. **Detect distro** — call `detect_distro()` to determine package manager
5. **Execute operations** — use `run()` / `write_remote_file()` with appropriate sudo
6. **Verify** — always verify after each operation
7. **Log** — write to log file, follow AGENTS_OPS_RULES.md
8. **Update docs** — back-feed changes to server README

---

## Resources

- `references/paramiko-patterns.md` — Copy-paste code patterns for common operations
- `references/servers.md` — Server connection info index
- `scripts/ssh_run.py` — Ready-to-use base template for new operation scripts
- `E:/2026_work_schedule/运维/AGENTS_OPS_RULES.md` — Mandatory operational rules
