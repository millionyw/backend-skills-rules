# Server Connection Info Index

> **Canonical source**: `config/servers.json` (machine-readable, used by scripts).
> This file is a human-readable reference. If values conflict, `config/servers.json` takes precedence.

---

## Server List

| Name | IP | User | Password | Distro | SSH Key | Notes |
|------|-----|------|----------|--------|---------|----------|-------|
| 112 (金华AI) | 10.211.211.112 | dems | win2022@dems | Debian 10 buster | id_ed25519 (no passphrase) | 运维/112服务器-金华AI-Debian/ | EOL, OpenSSH 7.9p1 |
| 130 (虚拟电厂2) | 10.211.211.130 | dems | win2022@dems | Ubuntu | — | 运维/130-虚拟电厂2/ | Docker 29.3.1 |
| 161 (金华主配微) | 10.211.211.161 | dems | win2022@dems | Linx (Debian-based, kernel 4.9) | — | 运维/161服务器-金华主配微/ | gcc 4.9.2, Python 3.11 |
| 189 (虚拟电厂备) | 10.211.211.189 | dems | win2022@dems | — | — | 运维/209服务器-虚拟电厂/主备部署方案/ | 209 的备机 |
| 209 (虚拟电厂主) | 10.211.211.209 | dems | win2022@dems | Ubuntu | — | 运维/209服务器-虚拟电厂/ | MySQL, PG, Airflow, Docker |
| 225 (openEuler) | 10.211.211.225 | dems | win2022@dems | openEuler 24.03 LTS | — | 运维/225服务器-openEuler/ | VMware, firewalld, Docker 25.0.3 |

---

## Connection Patterns

### Quick Connect (paramiko)

```python
import paramiko

# All servers share the same user/password pattern
SERVERS = {
    "112":  {"host": "10.211.211.112",  "user": "dems", "pwd": "win2022@dems", "distro": "debian"},
    "130":  {"host": "10.211.211.130",  "user": "dems", "pwd": "win2022@dems", "distro": "ubuntu"},
    "161":  {"host": "10.211.211.161",  "user": "dems", "pwd": "win2022@dems", "distro": "linx"},
    "189":  {"host": "10.211.211.189",  "user": "dems", "pwd": "win2022@dems", "distro": "unknown"},
    "209":  {"host": "10.211.211.209",  "user": "dems", "pwd": "win2022@dems", "distro": "ubuntu"},
    "225":  {"host": "10.211.211.225",  "user": "dems", "pwd": "win2022@dems", "distro": "openeuler"},
}

def get_server(name_or_ip):
    """Get server info by name (e.g., '225') or IP (e.g., '10.211.211.225')."""
    # Try by name
    if name_or_ip in SERVERS:
        return SERVERS[name_or_ip]
    # Try by IP
    for name, info in SERVERS.items():
        if info["host"] == name_or_ip:
            return info
    raise ValueError(f"Unknown server: {name_or_ip}")
```

### SSH Key Notes

- **112**: Has `id_ed25519` (no passphrase) — preferred for automation. `id_rsa` has passphrase, avoid.
- **Other servers**: Password auth only (no SSH keys deployed yet).

### Root Access

All servers have `dems` in the `wheel` group with sudo access. Use `echo 'win2022@dems' | sudo -S` pattern.

Some servers also have root with same password (`win2022@dems`), but prefer sudo.

---

## Distro-Specific Notes

### openEuler (225)
- Package manager: `dnf` (not `yum` or `apt`)
- Firewall: `firewalld` (not `ufw`)
- SELinux: Permissive mode
- No `apt-get`, no `systemctl edit` (use drop-in files manually)
- GNOME packages: `gnome-shell`, `gdm` (not `gdm3`)
- X11 packages: `xorg-x11-xauth`, `xorg-x11-apps`

### Debian 10 buster (112)
- **EOL** — no security updates
- OpenSSH 7.9p1 — older version, some features may be missing
- Package manager: `apt-get`
- Has `id_ed25519` SSH key for passwordless login

### Linx (161)
- Debian-based but heavily customized
- Kernel 4.9.0-8-linx-security-amd64
- System gcc 4.9.2 (very old, cannot compile modern extensions)
- Custom gcc 12.4.0 at `/opt/tsysmart/local/gcc/bin/gcc` (incomplete, no as/binutils)
- Package manager: `apt-get`

### Ubuntu (130, 209)
- Standard Ubuntu, `apt-get` package manager
- 209 has MySQL, PostgreSQL, Airflow, Docker
- 130 has Docker 29.3.1 (binary install from 209)

---

## Network

All servers are on the `10.211.211.0/24` subnet, gateway `10.211.211.1`.
DNS: `114.114.114.114`, `8.8.8.8`.
