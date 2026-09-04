# Linux Cheatsheet

Quick-reference commands for Linux enumeration, networking, files, permissions, services, credentials, containers and privilege-escalation analysis during authorised security assessments.

This cheatsheet is designed for:

```text
Initial Access
     |
     v
System Enumeration
     |
     v
Privilege Analysis
     |
     v
Configuration Review
     |
     v
Minimal Validation
     |
     v
Evidence
```

!!! warning "Authorised testing only"
    Use these commands only on systems you own or are explicitly authorised to assess. Prefer read-only enumeration and the lowest-impact validation method. Do not modify privileged files, create SUID binaries, change sudoers, alter scheduled tasks, extract unnecessary credentials or establish persistence unless explicitly authorised.

---

# Quick Start

Start with:

```bash
whoami
id
hostname
uname -a
cat /etc/os-release
sudo -l
env
ip -br addr
ip route
cat /etc/resolv.conf
ss -tulpn
ps aux
systemctl --type=service --state=running
mount
df -h
```

Then investigate:

```text
Identity
   |
   v
OS / Kernel
   |
   v
Users / Groups
   |
   v
Sudo
   |
   v
Processes / Services
   |
   v
Network
   |
   v
Files / Permissions
   |
   v
SUID / SGID
   |
   v
Capabilities
   |
   v
Cron / Timers
   |
   v
Credentials / Configuration
   |
   v
Containers
   |
   v
Security Controls
```

---

# Identity

Current user:

```bash
whoami
```

UID, GID and groups:

```bash
id
```

Groups:

```bash
groups
```

Specific user:

```bash
id username
```

Effective username:

```bash
id -un
```

Effective group:

```bash
id -gn
```

Current UID:

```bash
id -u
```

Current GID:

```bash
id -g
```

---

# Logged-In Users

```bash
who
```

More detail:

```bash
w
```

Login history:

```bash
last
```

Last-login information:

```bash
lastlog
```

---

# Host Information

Hostname:

```bash
hostname
```

FQDN:

```bash
hostname -f
```

Detailed:

```bash
hostnamectl
```

---

# Operating System

Kernel:

```bash
uname -a
```

Kernel release:

```bash
uname -r
```

Architecture:

```bash
uname -m
```

Distribution:

```bash
cat /etc/os-release
```

Other useful locations:

```bash
cat /etc/*release 2>/dev/null
cat /proc/version
```

If available:

```bash
lsb_release -a
```

---

# CPU

```bash
lscpu
```

```bash
cat /proc/cpuinfo
```

---

# Memory

```bash
free -h
```

```bash
cat /proc/meminfo
```

---

# Uptime

```bash
uptime
```

Boot time:

```bash
who -b
```

---

# Environment

```bash
env
```

Alternative:

```bash
printenv
```

Important variables:

```bash
echo "$USER"
echo "$HOME"
echo "$SHELL"
echo "$PATH"
echo "$PWD"
```

---

# Shell

Configured shell:

```bash
echo "$SHELL"
```

Current shell process:

```bash
ps -p $$ -o comm=
```

Available shells:

```bash
cat /etc/shells
```

---

# PATH

```bash
echo "$PATH"
```

One directory per line:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Inspect permissions:

```bash
printf '%s\n' "$PATH" |
while read -r d; do
    [ -n "$d" ] && ls -ld "$d" 2>/dev/null
done
```

Writable PATH directories:

```bash
printf '%s\n' "$PATH" |
while read -r d; do
    [ -n "$d" ] && [ -d "$d" ] && [ -w "$d" ] && echo "$d"
done
```

A writable PATH directory is not automatically exploitable.

Investigate whether a privileged process:

```text
Executes an Unqualified Command
            +
Uses the Writable PATH Entry
```

---

# Users

Local account database:

```bash
cat /etc/passwd
```

Usernames only:

```bash
cut -d ':' -f 1 /etc/passwd
```

NSS-aware enumeration:

```bash
getent passwd
```

Specific user:

```bash
getent passwd username
```

---

# Interactive-Looking Users

```bash
awk -F: '$7 !~ /(nologin|false)$/ {print $1 ":" $3 ":" $7}' /etc/passwd
```

Treat this as an indicator, not definitive proof that an account is actively used interactively.

---

# UID 0 Accounts

```bash
awk -F: '$3 == 0 {print $1 ":" $3 ":" $7}' /etc/passwd
```

Unexpected additional UID 0 accounts require investigation.

---

# Groups

```bash
cat /etc/group
```

NSS-aware:

```bash
getent group
```

Specific group:

```bash
getent group sudo
```

Current membership:

```bash
id
```

---

# Interesting Groups

Depending on the distribution and installed software, security-sensitive groups can include:

```text
sudo
wheel
docker
lxd
libvirt
disk
adm
shadow
systemd-journal
```

Do not classify membership as a vulnerability without evaluating what the group can actually access.

---

# Sudo

One of the first privilege checks should be:

```bash
sudo -l
```

More detail where supported:

```bash
sudo -ll
```

Version:

```bash
sudo --version
```

Review:

```text
NOPASSWD
SETENV
Allowed Commands
Wildcards
Arguments
Run-As User
Run-As Group
Editors
Interpreters
Package Managers
File Utilities
Service Managers
```

---

# Sudo Security Model

```text
Current User
     |
     v
sudo Rule
     |
     v
Allowed Binary
     |
     v
Binary Capability
     |
     +--> Command Execution?
     +--> Shell Escape?
     +--> File Read?
     +--> File Write?
     +--> Library Load?
```

When a binary appears in `sudo -l`, check whether its permitted functionality can cross the intended privilege boundary.

GTFOBins is useful for this analysis.

---

# GTFOBins

GTFOBins is a curated reference for legitimate Unix-like executables whose normal functionality can become security-relevant when exposed through unsafe configurations.

Useful contexts include:

```text
Unprivileged
Sudo
SUID
Capabilities
```

Useful function categories include:

```text
Shell
Command
File Read
File Write
Upload
Download
Library Load
Privilege Escalation
```

Do not assume:

```text
Binary Listed in GTFOBins
=
Vulnerable System
```

The relevant model is:

```text
Binary
   +
Privileged Context
   +
Useful Functionality
   =
Potential Security Boundary Bypass
```

Example assessment workflow:

```text
sudo -l
   |
   v
Identify Binary
   |
   v
Check GTFOBins
   |
   v
Understand Required Conditions
   |
   v
Validate Configuration
   |
   v
Report
```

Reference:

[GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" }

---

# Sudoers

Where readable:

```bash
cat /etc/sudoers
```

Additional rules:

```bash
ls -la /etc/sudoers.d/
```

Search:

```bash
grep -Rni '' /etc/sudoers /etc/sudoers.d 2>/dev/null
```

Do not modify sudo configuration during routine assessment.

---

# Processes

```bash
ps aux
```

Alternative:

```bash
ps -ef
```

Process tree:

```bash
ps auxf
```

If available:

```bash
pstree -ap
```

---

# Root Processes

```bash
ps -U root -u root
```

Investigate:

```text
Executable
Arguments
Working Directory
Configuration
Environment
Loaded Libraries
Writable Dependencies
```

---

# Search Processes

```bash
pgrep -a nginx
```

or:

```bash
ps aux | grep nginx
```

---

# Process Details

```bash
ps -p PID -f
```

Executable:

```bash
readlink -f /proc/PID/exe
```

Command line:

```bash
tr '\0' ' ' < /proc/PID/cmdline
```

Working directory:

```bash
readlink -f /proc/PID/cwd
```

Permissions may restrict `/proc` access.

---

# Process Environment

Where permitted:

```bash
tr '\0' '\n' < /proc/PID/environ
```

Process environments may expose:

```text
Passwords
API Keys
Tokens
Database Credentials
Cloud Credentials
```

Do not unnecessarily collect or reproduce secrets.

---

# Services

Running:

```bash
systemctl --type=service --state=running
```

All:

```bash
systemctl --type=service
```

Specific:

```bash
systemctl status ssh
```

---

# Service Definition

```bash
systemctl cat SERVICE
```

Unit file:

```bash
systemctl show SERVICE -p FragmentPath
```

Properties:

```bash
systemctl show SERVICE
```

---

# Enabled Services

```bash
systemctl list-unit-files --type=service --state=enabled
```

---

# Failed Services

```bash
systemctl --failed
```

---

# Service Security Review

For privileged services investigate:

```text
Unit File
   |
   v
ExecStart
   |
   v
Executable
   |
   v
Configuration
   |
   v
Working Directory
   |
   v
EnvironmentFile
   |
   v
Dependencies
```

Check permissions on each relevant component.

---

# SysV Init

Older systems may use:

```bash
service --status-all
```

Scripts:

```bash
ls -la /etc/init.d/
```

---

# Networking

Interfaces:

```bash
ip addr
```

Compact:

```bash
ip -br addr
```

Links:

```bash
ip link
```

IPv4:

```bash
ip -4 addr
```

IPv6:

```bash
ip -6 addr
```

---

# Routes

```bash
ip route
```

IPv6:

```bash
ip -6 route
```

Default route:

```bash
ip route | grep '^default'
```

Route to target:

```bash
ip route get 192.0.2.10
```

---

# Neighbours

```bash
ip neigh
```

Legacy if installed:

```bash
arp -a
```

---

# Listening Ports

```bash
ss -tulpn
```

TCP:

```bash
ss -lntp
```

UDP:

```bash
ss -lnup
```

Without process information:

```bash
ss -lntu
```

---

# Network Connections

```bash
ss -tunap
```

Established TCP:

```bash
ss -tn state established
```

---

# DNS

Resolver configuration:

```bash
cat /etc/resolv.conf
```

systemd-resolved:

```bash
resolvectl status
```

---

# DNS Queries

```bash
dig example.com
```

A:

```bash
dig example.com A
```

AAAA:

```bash
dig example.com AAAA
```

MX:

```bash
dig example.com MX
```

NS:

```bash
dig example.com NS
```

TXT:

```bash
dig example.com TXT
```

Reverse:

```bash
dig -x 192.0.2.10
```

---

# Alternative DNS Tools

```bash
host example.com
```

```bash
nslookup example.com
```

---

# Connectivity

```bash
ping -c 4 example.com
```

TCP:

```bash
nc -vz example.com 443
```

HTTP:

```bash
curl -I https://example.com/
```

Verbose:

```bash
curl -v https://example.com/
```

---

# Route Discovery

```bash
traceroute example.com
```

Alternative:

```bash
tracepath example.com
```

---

# NetworkManager

```bash
nmcli device status
```

```bash
nmcli connection show
```

---

# Firewall

## nftables

Where authorised and permitted:

```bash
sudo nft list ruleset
```

## iptables

```bash
sudo iptables -L -n -v
```

NAT:

```bash
sudo iptables -t nat -L -n -v
```

## UFW

```bash
sudo ufw status verbose
```

## firewalld

```bash
firewall-cmd --state
```

```bash
firewall-cmd --list-all
```

---

# Filesystems

```bash
mount
```

Cleaner:

```bash
findmnt
```

Disk usage:

```bash
df -h
```

Devices:

```bash
lsblk
```

Filesystems:

```bash
lsblk -f
```

---

# fstab

```bash
cat /etc/fstab
```

Review:

```text
Network Mounts
Credentials
Mount Options
Sensitive Shares
Writable Mounts
```

---

# NFS

Mounted NFS:

```bash
findmnt -t nfs,nfs4
```

Exports configured locally:

```bash
cat /etc/exports 2>/dev/null
```

Exported filesystems where permitted:

```bash
exportfs -v 2>/dev/null
```

---

# SMB / CIFS Mounts

```bash
findmnt -t cifs
```

Search mount configuration:

```bash
grep -i cifs /etc/fstab 2>/dev/null
```

---

# File Listing

```bash
ls -la
```

Human readable:

```bash
ls -lah
```

---

# File Metadata

```bash
stat file.txt
```

Type:

```bash
file file.txt
```

Resolve symlink:

```bash
readlink -f file.txt
```

---

# Find Files

Name:

```bash
find / -type f -name 'filename' 2>/dev/null
```

Case insensitive:

```bash
find / -type f -iname '*config*' 2>/dev/null
```

Directories:

```bash
find / -type d -iname '*backup*' 2>/dev/null
```

---

# Recently Modified Files

Last day:

```bash
find / -type f -mtime -1 2>/dev/null
```

Last seven days:

```bash
find / -type f -mtime -7 2>/dev/null
```

Last hour:

```bash
find / -type f -mmin -60 2>/dev/null
```

Prefer targeted directories on production systems.

---

# Large Files

```bash
find / -type f -size +100M 2>/dev/null
```

---

# Permissions

```bash
ls -l file
```

Numeric:

```bash
stat -c '%a %U %G %n' file
```

---

# Permission Reference

```text
r = 4 = read
w = 2 = write
x = 1 = execute
```

Examples:

```text
700 = rwx------
750 = rwxr-x---
755 = rwxr-xr-x
600 = rw-------
640 = rw-r-----
644 = rw-r--r--
```

---

# ACLs

```bash
getfacl file
```

Directory:

```bash
getfacl directory
```

Remember:

```text
Traditional Mode Bits
        +
POSIX ACLs
        =
Effective Permissions
```

---

# World-Writable Files

Restrict to the current filesystem:

```bash
find / -xdev -type f -perm -0002 2>/dev/null
```

---

# World-Writable Directories

```bash
find / -xdev -type d -perm -0002 2>/dev/null
```

A writable object matters when a more privileged process trusts it.

---

# Writable Files

Targeted directory:

```bash
find /path -type f -writable 2>/dev/null
```

Directories:

```bash
find /path -type d -writable 2>/dev/null
```

---

# SUID

Find SUID executables:

```bash
find / -type f -perm -4000 2>/dev/null
```

Alternative:

```bash
find / -type f -perm -u=s 2>/dev/null
```

Detailed:

```bash
find / -user root -type f -perm -4000 -exec ls -ldb {} \; 2>/dev/null
```

---

# SGID

```bash
find / -type f -perm -2000 2>/dev/null
```

Alternative:

```bash
find / -type f -perm -g=s 2>/dev/null
```

---

# SUID and SGID Together

```bash
find / -type f \( -perm -4000 -o -perm -2000 \) -exec ls -la {} \; 2>/dev/null
```

---

# SUID Analysis

Use:

```text
SUID Binary
    |
    v
Expected?
    |
    +--> No --> Investigate Origin
    |
    +--> Yes
           |
           v
      Safe Functionality?
           |
           v
      GTFOBins / Vendor Research
```

Check unusual binaries against:

[GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" }

Do not assume every SUID binary is vulnerable.

---

# Capabilities

```bash
getcap -r / 2>/dev/null
```

Security-sensitive examples include:

```text
cap_setuid
cap_setgid
cap_dac_override
cap_dac_read_search
cap_sys_admin
cap_sys_ptrace
cap_net_admin
cap_net_raw
```

Interpret the capability together with the executable.

---

# Capability Analysis

```text
Executable
    |
    v
Linux Capability
    |
    v
What Kernel Privilege Is Granted?
    |
    v
Can Existing Program Functionality
Cross a Security Boundary?
```

Check relevant executables against GTFOBins.

---

# File Attributes

```bash
lsattr file
```

---

# Cron

System crontab:

```bash
cat /etc/crontab
```

Directories:

```bash
ls -la /etc/cron.d/
ls -la /etc/cron.hourly/
ls -la /etc/cron.daily/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/
```

Current user:

```bash
crontab -l
```

---

# Cron Analysis

Review:

```text
Schedule
   |
   v
Execution User
   |
   v
Command
   |
   v
Script
   |
   v
Dependencies
   |
   v
Permissions
```

Questions:

```text
Can I modify the script?
Can I modify its directory?
Can I modify a dependency?
Does it use wildcards?
Does it rely on PATH?
Does it load writable configuration?
```

---

# systemd Timers

```bash
systemctl list-timers --all
```

Timer:

```bash
systemctl cat example.timer
```

Service:

```bash
systemctl cat example.service
```

---

# at Jobs

Where available:

```bash
atq
```

---

# Shell Startup Files

Current user:

```bash
ls -la ~
```

Common files:

```text
~/.bashrc
~/.bash_profile
~/.profile
~/.zshrc
```

Inspect:

```bash
cat ~/.bashrc
cat ~/.profile
```

Writable startup files belonging to another security context may warrant investigation.

---

# MOTD

Dynamic MOTD configuration may exist under:

```bash
ls -la /etc/update-motd.d/ 2>/dev/null
```

Review permissions:

```bash
find /etc/update-motd.d -maxdepth 1 -type f -exec ls -l {} \; 2>/dev/null
```

Unexpected non-root write access to privileged login-time scripts can be security-sensitive.

Do not modify them during routine assessment.

---

# SSH

Directory:

```bash
ls -la ~/.ssh/
```

Configuration:

```bash
cat ~/.ssh/config 2>/dev/null
```

Authorised keys:

```bash
cat ~/.ssh/authorized_keys 2>/dev/null
```

Known hosts:

```bash
cat ~/.ssh/known_hosts 2>/dev/null
```

---

# SSH Keys

List:

```bash
find ~/.ssh -maxdepth 1 -type f -ls 2>/dev/null
```

Common names:

```text
id_rsa
id_ed25519
id_ecdsa
```

Treat private keys as credentials.

---

# SSH Public Key Fingerprint

```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

---

# SSH Server

```bash
systemctl status ssh
```

or:

```bash
systemctl status sshd
```

Effective configuration where permitted:

```bash
sshd -T
```

Review:

```text
permitrootlogin
passwordauthentication
pubkeyauthentication
allowusers
allowgroups
```

---

# SSH Connection

```bash
ssh user@example.com
```

Specific key:

```bash
ssh -i ~/.ssh/id_ed25519 user@example.com
```

Port:

```bash
ssh -p 2222 user@example.com
```

Verbose:

```bash
ssh -v user@example.com
```

---

# SSH Tunnelling

Only establish tunnels when explicitly within scope.

Local forwarding:

```bash
ssh -L 8080:internal.example:80 user@jump.example
```

Dynamic SOCKS:

```bash
ssh -D 1080 user@jump.example
```

Remote forwarding:

```bash
ssh -R 8080:127.0.0.1:8000 user@remote.example
```

---

# Configuration Files

Common locations:

```text
/etc/
/opt/
/srv/
/var/www/
/usr/local/etc/
/home/<user>/
```

Search common formats:

```bash
find /etc -type f \( \
    -name '*.conf' -o \
    -name '*.ini' -o \
    -name '*.yaml' -o \
    -name '*.yml' \
\) 2>/dev/null
```

---

# Sensitive Configuration Search

Use targeted locations:

```bash
grep -RniE 'password|passwd|secret|token|api[_-]?key' /opt /srv /var/www 2>/dev/null
```

Common interesting file types:

```text
.env
.conf
.ini
.yml
.yaml
.json
.xml
.properties
```

---

# Environment Files

```bash
find /var/www /opt /srv -type f -name '.env' 2>/dev/null
```

Do not expose discovered secrets in screenshots or reports.

---

# Shell History

```bash
history
```

Bash:

```bash
cat ~/.bash_history 2>/dev/null
```

Zsh:

```bash
cat ~/.zsh_history 2>/dev/null
```

Search:

```bash
grep -Ei 'password|passwd|token|secret|key' ~/.bash_history 2>/dev/null
```

History is not a complete audit trail.

---

# Credentials

Potential credential sources include:

```text
Shell History
Environment Variables
Application Configuration
Database Configuration
SSH Keys
Cloud CLI Configuration
Backup Files
Service Configuration
Mounted Shares
```

The objective is to determine:

```text
Does Sensitive Authentication Material
Exist Where the Current User Can Access It?
```

Do not collect more secret material than required to demonstrate the finding.

---

# Backup Files

Search common patterns:

```bash
find / -type f \( \
    -name '*.bak' -o \
    -name '*.backup' -o \
    -name '*.old' -o \
    -name '*.save' \
\) 2>/dev/null
```

Prefer targeted paths where possible.

---

# Archives

Search:

```bash
find / -type f \( \
    -name '*.zip' -o \
    -name '*.tar' -o \
    -name '*.tar.gz' -o \
    -name '*.tgz' -o \
    -name '*.7z' \
\) 2>/dev/null
```

---

# Web Servers

Common application locations:

```text
/var/www/
/srv/www/
/opt/
/srv/
```

---

# Apache

Processes:

```bash
pgrep -a apache2
```

or:

```bash
pgrep -a httpd
```

Common configuration:

```text
/etc/apache2/
/etc/httpd/
```

Debian-derived enabled sites:

```bash
ls -la /etc/apache2/sites-enabled/ 2>/dev/null
```

---

# Nginx

```bash
pgrep -a nginx
```

Configuration:

```bash
ls -la /etc/nginx/ 2>/dev/null
```

Where permitted:

```bash
nginx -T
```

This can expose the effective configuration and potentially sensitive values, so handle the output appropriately.

---

# Databases

Processes:

```bash
ps aux | grep -Ei 'mysql|mariadb|postgres|mongod|redis'
```

Listening:

```bash
ss -lntp
```

Common ports:

```text
3306   MySQL / MariaDB
5432   PostgreSQL
6379   Redis
27017  MongoDB
```

Port number alone does not prove the service.

---

# MySQL Configuration

Common locations:

```text
/etc/mysql/
/etc/my.cnf
~/.my.cnf
```

Search:

```bash
find /etc -iname '*mysql*' -o -iname '*mariadb*' 2>/dev/null
```

---

# PostgreSQL Configuration

Common locations vary by distribution and version.

Find:

```bash
find /etc -iname 'postgresql.conf' -o -iname 'pg_hba.conf' 2>/dev/null
```

---

# Docker

Version:

```bash
docker --version
```

Information:

```bash
docker info
```

Containers:

```bash
docker ps
```

All:

```bash
docker ps -a
```

Images:

```bash
docker images
```

Networks:

```bash
docker network ls
```

Volumes:

```bash
docker volume ls
```

---

# Docker Group

```bash
getent group docker
```

Current membership:

```bash
id
```

Docker socket:

```bash
ls -l /var/run/docker.sock
```

Control of a privileged Docker daemon can imply extensive control over the host.

Do not start a privileged container merely to prove the security impact unless explicitly authorised.

---

# Podman

```bash
podman info
```

```bash
podman ps
```

Rootless Podman should not automatically be treated as equivalent to access to a root-controlled Docker daemon.

---

# LXD / LXC

Groups:

```bash
getent group lxd
```

```bash
getent group lxc
```

Current user:

```bash
id
```

If available:

```bash
lxc list
```

Administrative control of privileged container infrastructure can have host-security implications.

Validate the actual configuration before reporting.

---

# Container Detection

```bash
systemd-detect-virt
```

Docker indicator:

```bash
test -f /.dockerenv && echo 'Docker environment indicator present'
```

Cgroups:

```bash
cat /proc/1/cgroup
```

No single method detects every container environment.

---

# Kubernetes

Current context:

```bash
kubectl config current-context
```

Contexts:

```bash
kubectl config get-contexts
```

Authorisation:

```bash
kubectl auth can-i --list
```

Configuration:

```bash
ls -la ~/.kube/
```

Kubeconfig may contain sensitive authentication information.

---

# Cloud Credentials

Common user configuration locations include:

```text
~/.aws/
~/.azure/
~/.config/gcloud/
```

List:

```bash
ls -la ~/.aws 2>/dev/null
ls -la ~/.azure 2>/dev/null
ls -la ~/.config/gcloud 2>/dev/null
```

Treat cloud tokens and credentials as sensitive and remain within the authorised cloud scope.

---

# NFS Privilege Analysis

Check mounts:

```bash
findmnt -t nfs,nfs4
```

Local exports:

```bash
cat /etc/exports 2>/dev/null
```

Review export options such as:

```text
root_squash
no_root_squash
rw
ro
```

Do not modify remote files merely to prove an unsafe export.

---

# Shared Libraries

Loaded libraries:

```bash
ldd /path/to/binary
```

Dynamic loader information:

```bash
ldconfig -p
```

Environment:

```bash
env | grep '^LD_'
```

Potentially relevant variables include:

```text
LD_LIBRARY_PATH
LD_PRELOAD
```

Privileged execution often applies additional loader restrictions, so evaluate the actual execution context.

---

# Writable Library Paths

For a specific privileged application:

```bash
ldd /path/to/binary
```

Then inspect relevant library and directory permissions:

```bash
ls -l /path/to/library.so
ls -ld /path/to/library-directory
```

Do not replace production libraries during routine testing.

---

# Kernel

```bash
uname -a
```

```bash
uname -r
```

```bash
cat /proc/version
```

Installed kernel packages on Debian-based systems:

```bash
dpkg -l 'linux-image*' 2>/dev/null
```

---

# Kernel Vulnerability Assessment

Do not assume:

```text
Old Kernel Version
=
Exploitable
```

Distribution vendors frequently backport security patches without changing the upstream version in the way a simple version comparison expects.

Validate:

```text
Distribution
Kernel Package
Vendor Patch Level
Architecture
Exploit Preconditions
Mitigations
```

before reporting a kernel vulnerability.

---

# Linux Privilege Escalation Automation

Common assessment tools include:

```text
LinPEAS
Linux Exploit Suggester
Linux Smart Enumeration
```

These tools can accelerate enumeration but should not replace manual validation.

Use them only when tooling execution is authorised.

---

# LinPEAS

Project:

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Use the current project documentation for installation and execution.

Review findings manually before reporting them.

---

# Linux Exploit Suggester

Project:

[Linux Exploit Suggester](https://github.com/The-Z-Labs/linux-exploit-suggester){ target="_blank" rel="noopener noreferrer" }

Treat suggestions as:

```text
Candidates for Investigation
```

not confirmed vulnerabilities.

---

# Linux Smart Enumeration

Project:

[Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

Use according to the rules of engagement.

---

# Automated Enumeration Model

```text
Enumeration Tool
       |
       v
Candidate Finding
       |
       v
Manual Verification
       |
       v
Context Analysis
       |
       v
Minimal Validation
       |
       v
Report
```

Never use:

```text
Scanner Says Vulnerable
```

as the entire evidence chain.

---

# Privilege Escalation Checklist

Start with:

```bash
id
sudo -l
uname -a
cat /etc/os-release
env
```

Then:

```bash
find / -type f -perm -4000 2>/dev/null
```

```bash
getcap -r / 2>/dev/null
```

```bash
cat /etc/crontab
```

```bash
systemctl list-timers --all
```

```bash
systemctl --type=service --state=running
```

```bash
ps aux
```

```bash
ss -tulpn
```

```bash
mount
```

---

# Privilege Escalation Decision Tree

```text
Current User
    |
    v
sudo -l
    |
    +--> Interesting Rule? --> Analyse Binary / GTFOBins
    |
    v
SUID / SGID
    |
    +--> Unusual Binary? --> GTFOBins / Vendor Research
    |
    v
Capabilities
    |
    +--> Sensitive Capability? --> Analyse Program
    |
    v
Cron / Timers
    |
    +--> Writable Dependency? --> Validate Path
    |
    v
Services
    |
    +--> Writable Component? --> Validate Path
    |
    v
Credentials
    |
    +--> Reusable Credential? --> Scope Check
    |
    v
Groups
    |
    +--> Docker / LXD / Other Privileged Group?
    |
    v
Kernel / Software
    |
    +--> Known Vulnerability? --> Verify Patch State
```

---

# GTFOBins Workflow

When you discover:

```text
sudo
SUID
Capability
```

use:

[GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" }

Search the binary.

Then determine:

```text
Does the Required Context Match?
Does the Binary Have the Required Permission?
Does the Technique Modify State?
Can Impact Be Proven Read-Only?
```

GTFOBins itself notes that listed programs are not necessarily vulnerable; the issue is how legitimate functionality can interact with unsafe security configuration.

---

# Exploit Notes Workflow

Exploit Notes provides a broad Linux privilege-escalation reference covering areas such as:

```text
OS / Kernel Information
Users
Shell Configuration
SUID / SGID
Writable Files
Capabilities
Sudo
Scheduled Execution
Containers
Software-Specific Privilege Escalation
```

Use it primarily as:

```text
Enumeration Reference
       +
Research Starting Point
```

and independently validate findings before reporting.

Reference:

[Exploit Notes - Linux Privilege Escalation](https://exploitnotes.org/exploit/linux/privilege-escalation/){ target="_blank" rel="noopener noreferrer" }

---

# File Transfers

Only transfer files where authorised.

## Python HTTP Server

```bash
python3 -m http.server 8000
```

Explicit bind:

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

---

# curl Download

```bash
curl -O https://example.com/file.txt
```

Custom name:

```bash
curl -o file.txt https://example.com/file.txt
```

---

# wget

```bash
wget https://example.com/file.txt
```

Custom name:

```bash
wget -O file.txt https://example.com/file.txt
```

---

# SCP

Local to remote:

```bash
scp file.txt user@example.com:/tmp/
```

Remote to local:

```bash
scp user@example.com:/tmp/file.txt .
```

---

# Base64

Encode:

```bash
printf '%s' 'test' | base64
```

Decode:

```bash
printf '%s' 'dGVzdA==' | base64 -d
```

File:

```bash
base64 file.bin > file.b64
```

Decode:

```bash
base64 -d file.b64 > file.bin
```

---

# Hashes

SHA-256:

```bash
sha256sum file.bin
```

SHA-1:

```bash
sha1sum file.bin
```

MD5:

```bash
md5sum file.bin
```

Prefer SHA-256 or stronger for integrity verification.

---

# OpenSSL

File SHA-256:

```bash
openssl dgst -sha256 file.bin
```

Random bytes:

```bash
openssl rand -hex 32
```

Certificate:

```bash
openssl x509 -in certificate.pem -text -noout
```

---

# TLS

Inspect:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

Certificate details:

```bash
openssl s_client \
    -connect example.com:443 \
    -servername example.com \
    </dev/null 2>/dev/null |
openssl x509 -noout -subject -issuer -dates
```

---

# Archives

Create tar.gz:

```bash
tar -czf archive.tar.gz directory/
```

Extract:

```bash
tar -xzf archive.tar.gz
```

List:

```bash
tar -tzf archive.tar.gz
```

ZIP:

```bash
zip -r archive.zip directory/
```

Unzip:

```bash
unzip archive.zip
```

---

# Text Processing

## grep

```bash
grep 'text' file.txt
```

Case insensitive:

```bash
grep -i 'text' file.txt
```

Recursive:

```bash
grep -Rni 'text' .
```

---

# ripgrep

```bash
rg 'text'
```

File type:

```bash
rg 'password' -g '*.conf'
```

---

# sort

```bash
sort file.txt
```

Unique:

```bash
sort -u file.txt
```

---

# uniq

```bash
sort file.txt | uniq
```

Count:

```bash
sort file.txt | uniq -c
```

---

# cut

```bash
cut -d ':' -f 1 /etc/passwd
```

---

# awk

```bash
awk '{print $1}' file.txt
```

```bash
awk -F: '{print $1}' /etc/passwd
```

---

# sed

```bash
sed 's/old/new/g' file.txt
```

---

# jq

Pretty JSON:

```bash
jq . file.json
```

Property:

```bash
jq '.name' file.json
```

HTTP pipeline:

```bash
curl -s https://example.com/api | jq .
```

---

# xargs

```bash
cat hosts.txt | xargs -n1 echo
```

Null-delimited:

```bash
find . -type f -print0 | xargs -0 ls -l
```

---

# tee

```bash
command | tee output.txt
```

Append:

```bash
command | tee -a output.txt
```

---

# Command Lookup

```bash
command -v python3
```

```bash
which python3
```

```bash
whereis python3
```

---

# Package Management

## Debian / Ubuntu / Kali

Installed:

```bash
dpkg -l
```

Specific:

```bash
dpkg -l | grep package
```

Policy:

```bash
apt-cache policy package
```

---

# RPM

```bash
rpm -qa
```

Specific:

```bash
rpm -q package
```

---

# Arch

```bash
pacman -Q
```

---

# Snap

```bash
snap list
```

---

# Flatpak

```bash
flatpak list
```

---

# Security Controls

## SELinux

```bash
getenforce
```

Detailed:

```bash
sestatus
```

Possible states include:

```text
Enforcing
Permissive
Disabled
```

---

# AppArmor

```bash
aa-status
```

or:

```bash
apparmor_status
```

---

# ASLR

```bash
cat /proc/sys/kernel/randomize_va_space
```

Common values:

```text
0 = disabled
1 = partial
2 = full randomisation
```

---

# ptrace

Where Yama is enabled:

```bash
cat /proc/sys/kernel/yama/ptrace_scope
```

---

# Seccomp

Current process:

```bash
grep '^Seccomp:' /proc/$$/status
```

Common values:

```text
0 = disabled
1 = strict
2 = filter
```

---

# Kernel Modules

```bash
lsmod
```

Specific:

```bash
modinfo module_name
```

---

# Open Files

Current shell:

```bash
lsof -p $$
```

Network:

```bash
lsof -i
```

Port:

```bash
lsof -i :443
```

Deleted but still open:

```bash
lsof +L1
```

---

# Logs

Common locations:

```text
/var/log/
/var/log/auth.log
/var/log/syslog
/var/log/messages
/var/log/secure
```

Availability depends on the distribution.

---

# journalctl

Recent:

```bash
journalctl -n 100
```

Current boot:

```bash
journalctl -b
```

Service:

```bash
journalctl -u ssh
```

Since today:

```bash
journalctl --since today
```

---

# Authentication Logs

Debian-derived:

```bash
grep -i 'sudo' /var/log/auth.log 2>/dev/null
```

RHEL-derived:

```bash
grep -i 'sudo' /var/log/secure 2>/dev/null
```

---

# Search for Errors

```bash
journalctl -p err
```

Current boot:

```bash
journalctl -b -p err
```

---

# Evidence Collection

Useful evidence model:

```text
Command
   |
   v
Relevant Output
   |
   v
Security Context
   |
   v
Affected Component
   |
   v
Impact
```

Record:

```text
Hostname
Username
UID / Groups
Timestamp
Command
Relevant Output
File / Service
Permissions
Expected State
Observed State
```

---

# Sensitive Evidence

Avoid unnecessarily storing:

```text
Passwords
Private Keys
Tokens
Cloud Credentials
Database Credentials
Session Cookies
API Keys
Hashes
```

Prefer evidence such as:

```text
File Exists
+
Current User Can Read It
+
Secret Value Redacted
```

rather than exposing the secret itself.

---

# Privilege Escalation Evidence

A strong finding should demonstrate:

```text
Low-Privilege Principal
        |
        v
Misconfiguration
        |
        v
Privileged Resource
        |
        v
Security Impact
```

Example:

```text
User
 |
 v
sudo Permission
 |
 v
Binary with Unsafe Functionality
 |
 v
Potential Root-Level Capability
```

The finding is the unsafe privilege relationship, not simply that a binary exists.

---

# Do Not Overreport

Do not automatically report:

```text
SUID Binary Exists
Docker Installed
Old Kernel String
Cron Exists
sudo Installed
Capability Exists
Writable /tmp
SSH Enabled
```

Instead determine:

```text
Can the Current User Cross
a Security Boundary?
```

---

# Manual Validation

For each candidate finding:

```text
What Is Misconfigured?
       |
       v
Who Can Reach It?
       |
       v
What Privilege Does It Provide?
       |
       v
Is That Privilege Intended?
       |
       v
Can It Be Demonstrated Safely?
```

---

# Linux Privilege Escalation Quick Flow

```text
whoami / id
     |
     v
sudo -l
     |
     v
SUID / SGID
     |
     v
Capabilities
     |
     v
Groups
     |
     v
Cron / Timers
     |
     v
Services
     |
     v
Processes
     |
     v
Writable Files
     |
     v
PATH / Libraries
     |
     v
Credentials
     |
     v
Docker / LXD
     |
     v
NFS
     |
     v
Kernel / Software
```

---

# Linux Assessment Checklist

## Identity

- [ ] Run `whoami`
- [ ] Run `id`
- [ ] Review groups
- [ ] Review logged-in users
- [ ] Review UID 0 accounts
- [ ] Review interactive users

## System

- [ ] Identify distribution
- [ ] Identify kernel
- [ ] Identify architecture
- [ ] Review environment variables
- [ ] Review PATH
- [ ] Review installed software where relevant

## Sudo

- [ ] Run `sudo -l`
- [ ] Review NOPASSWD
- [ ] Review SETENV
- [ ] Review allowed binaries
- [ ] Review wildcards
- [ ] Review arguments
- [ ] Check relevant binaries against GTFOBins
- [ ] Validate actual security boundary

## Processes

- [ ] Review processes
- [ ] Review root processes
- [ ] Review command lines
- [ ] Review writable dependencies
- [ ] Review sensitive process environments where authorised

## Services

- [ ] Review running services
- [ ] Review enabled services
- [ ] Review service unit files
- [ ] Review `ExecStart`
- [ ] Review executable permissions
- [ ] Review configuration permissions
- [ ] Review environment files

## Network

- [ ] Enumerate interfaces
- [ ] Enumerate routes
- [ ] Enumerate neighbours
- [ ] Enumerate DNS configuration
- [ ] Enumerate listening ports
- [ ] Enumerate established connections
- [ ] Review firewall configuration where permitted

## Files

- [ ] Review mounts
- [ ] Review fstab
- [ ] Review writable files
- [ ] Review writable directories
- [ ] Review ACLs
- [ ] Review configuration files
- [ ] Review backup files
- [ ] Review application directories

## SUID / SGID

- [ ] Enumerate SUID
- [ ] Enumerate SGID
- [ ] Identify unusual binaries
- [ ] Check relevant binaries against GTFOBins
- [ ] Validate owner and permissions
- [ ] Determine whether functionality crosses privilege boundary

## Capabilities

- [ ] Run `getcap -r /`
- [ ] Review unusual capabilities
- [ ] Identify executable
- [ ] Check GTFOBins where relevant
- [ ] Determine actual privilege exposed

## Scheduled Execution

- [ ] Review `/etc/crontab`
- [ ] Review `/etc/cron.d`
- [ ] Review user crontabs
- [ ] Review systemd timers
- [ ] Review executed scripts
- [ ] Review script permissions
- [ ] Review dependency permissions
- [ ] Review PATH and wildcard usage

## Credentials

- [ ] Review shell history
- [ ] Review environment variables
- [ ] Review application configuration
- [ ] Review `.env` files
- [ ] Review SSH configuration
- [ ] Review accessible private keys
- [ ] Review database configuration
- [ ] Review cloud CLI configuration
- [ ] Redact secrets in evidence

## Containers

- [ ] Check Docker
- [ ] Check Docker socket
- [ ] Check Docker group
- [ ] Check Podman
- [ ] Check LXD/LXC
- [ ] Determine rootless vs privileged model
- [ ] Review Kubernetes context where relevant

## Security Controls

- [ ] Review SELinux
- [ ] Review AppArmor
- [ ] Review ASLR
- [ ] Review ptrace restrictions
- [ ] Review seccomp where relevant
- [ ] Review firewall
- [ ] Review logging

## Privilege Escalation

- [ ] Review sudo
- [ ] Review SUID
- [ ] Review SGID
- [ ] Review capabilities
- [ ] Review cron
- [ ] Review timers
- [ ] Review services
- [ ] Review writable dependencies
- [ ] Review PATH
- [ ] Review libraries
- [ ] Review credentials
- [ ] Review privileged groups
- [ ] Review containers
- [ ] Review NFS
- [ ] Review kernel/software candidates
- [ ] Manually validate automated findings

## Evidence

- [ ] Record hostname
- [ ] Record current user
- [ ] Record groups
- [ ] Record command
- [ ] Capture relevant output
- [ ] Record affected object
- [ ] Record permissions
- [ ] Explain privilege boundary
- [ ] Redact secrets
- [ ] Document any state changes
- [ ] Perform cleanup where required

---

# Testing Model

The Linux privilege model can be simplified as:

```text
User
 |
 v
Permission
 |
 v
Resource
 |
 v
Privileged Execution
```

For sudo:

```text
User
 |
 v
sudo Rule
 |
 v
Binary
 |
 v
Privileged Functionality
```

For SUID:

```text
User
 |
 v
SUID Binary
 |
 v
Effective Owner
 |
 v
Privileged Functionality
```

For capabilities:

```text
User
 |
 v
Executable
 |
 v
Linux Capability
 |
 v
Kernel Privilege
```

For scheduled tasks:

```text
User-Writable Component
        |
        v
Scheduled Execution
        |
        v
Privileged User
```

For services:

```text
Writable Component
       |
       v
Privileged Service
       |
       v
Higher Privilege
```

For credentials:

```text
Readable Secret
     |
     v
More-Privileged Identity
     |
     v
Privilege Escalation
```

For containers:

```text
Container Management
        |
        v
Host Resource Access
        |
        v
Potential Host Control
```

The overall assessment model is:

```text
Enumerate
   |
   v
Identify Candidate
   |
   v
Research
   |
   +--> GTFOBins
   |
   +--> Exploit Notes
   |
   +--> Vendor Documentation
   |
   v
Validate Preconditions
   |
   v
Minimal Proof
   |
   v
Evidence
   |
   v
Remediation
```

---

# Quick Reference

```bash
# Identity
whoami
id
groups

# Host
hostname
uname -a
cat /etc/os-release

# Sudo
sudo -l

# Environment
env
echo "$PATH"

# Network
ip -br addr
ip route
ip neigh
cat /etc/resolv.conf
ss -tulpn

# Processes
ps aux
ps -U root -u root

# Services
systemctl --type=service --state=running
systemctl list-unit-files --type=service --state=enabled

# Filesystems
mount
findmnt
df -h
lsblk -f

# SUID
find / -type f -perm -4000 2>/dev/null

# SGID
find / -type f -perm -2000 2>/dev/null

# Capabilities
getcap -r / 2>/dev/null

# Cron
cat /etc/crontab
ls -la /etc/cron.d/
crontab -l

# Timers
systemctl list-timers --all

# Writable files
find /path -type f -writable 2>/dev/null

# Writable directories
find /path -type d -writable 2>/dev/null

# Shell history
history
cat ~/.bash_history 2>/dev/null

# SSH
ls -la ~/.ssh/
cat ~/.ssh/config 2>/dev/null

# Logs
journalctl -n 100

# Docker
docker info
docker ps
ls -l /var/run/docker.sock

# Security
getenforce
aa-status
cat /proc/sys/kernel/randomize_va_space
```

---

# References

## GTFOBins

[GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" }

Use GTFOBins when assessing security-sensitive Unix executables exposed through contexts such as:

```text
sudo
SUID
Capabilities
```

Remember that inclusion in GTFOBins does not mean the binary itself is vulnerable.

---

## Exploit Notes

[Exploit Notes - Linux Privilege Escalation](https://exploitnotes.org/exploit/linux/privilege-escalation/){ target="_blank" rel="noopener noreferrer" }

Useful as a practical reference for Linux privilege-escalation enumeration and technique research.

---

## PEASS-ng

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Includes LinPEAS for automated Linux privilege-escalation enumeration.

---

## Linux Exploit Suggester

[Linux Exploit Suggester](https://github.com/The-Z-Labs/linux-exploit-suggester){ target="_blank" rel="noopener noreferrer" }

Use suggestions as candidates requiring manual validation.

---

## Linux Smart Enumeration

[Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

---

## Linux man-pages

[Linux man-pages Project](https://www.kernel.org/doc/man-pages/){ target="_blank" rel="noopener noreferrer" }

---

## systemd

[systemd Documentation](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }

---

## OpenSSH

[OpenSSH Manual Pages](https://www.openssh.com/manual.html){ target="_blank" rel="noopener noreferrer" }

---

## Docker

[Docker Documentation](https://docs.docker.com/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

For Linux assessments, start simple:

```text
Who Am I?
   |
   v
What System Is This?
   |
   v
What Can I Run?
   |
   v
What Runs as Root?
   |
   v
What Can I Modify?
```

The highest-value initial commands are often:

```bash
id
sudo -l
uname -a
cat /etc/os-release
ps aux
ss -tulpn
find / -type f -perm -4000 2>/dev/null
getcap -r / 2>/dev/null
systemctl list-timers --all
```

When you discover an unusual privileged binary:

```text
Binary
   |
   v
Check Permission Context
   |
   v
GTFOBins
   |
   v
Exploit Notes
   |
   v
Vendor Documentation
   |
   v
Validate Preconditions
```

The important distinction is:

```text
Interesting Configuration
        !=
Confirmed Privilege Escalation
```

For example:

```text
SUID Binary
```

alone is not the finding.

The relevant question is:

```text
Can the Current User Use
That Binary's Functionality
to Cross a Security Boundary?
```

Similarly:

```text
Old Kernel
```

does not automatically mean:

```text
Kernel Privilege Escalation
```

and:

```text
Docker Installed
```

does not automatically mean:

```text
Root Access
```

Always validate the complete path:

```text
Low-Privilege User
        |
        v
Specific Misconfiguration
        |
        v
Reachable Privileged Capability
        |
        v
Security Boundary Crossed
```

For authorised penetration testing, prefer:

```text
Enumeration
    |
    v
Analysis
    |
    v
Minimal Validation
    |
    v
Evidence
    |
    v
Cleanup
```

over unnecessary system modification.

The Linux cheatsheet should therefore function as:

```text
Command Reference
      +
Privilege Checklist
      +
Research Map
```

with GTFOBins and Exploit Notes used as supporting references when a potentially dangerous Unix executable or privilege-escalation condition is discovered.
