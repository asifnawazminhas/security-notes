# Linux Enumeration

Linux enumeration is the process of building an accurate picture of a host before attempting deeper security testing.

The objective is to identify:

- Current security context
- Operating system and kernel
- Users and groups
- Administrative privileges
- Network configuration
- Processes and services
- Installed software
- Scheduled execution
- Filesystem permissions
- SUID and SGID binaries
- Linux capabilities
- Credentials and secrets
- SSH configuration
- Containers and virtualisation
- Security controls
- Logging and monitoring
- Potential privilege escalation relationships

Enumeration should answer:

```text
Who am I?
    |
    v
What system am I on?
    |
    v
What is running?
    |
    v
What can I access?
    |
    v
What can I modify?
    |
    v
What executes with higher privilege?
    |
    v
Can I influence it?
```

Enumeration produces candidates.

Manual validation determines whether those candidates represent actual security weaknesses.

---

# 1. Enumeration Workflow

A structured Linux enumeration workflow is:

```text
Initial Context
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
Network
      |
      v
Processes
      |
      v
Services
      |
      v
Scheduled Execution
      |
      v
Filesystem
      |
      v
SUID / SGID
      |
      v
Capabilities
      |
      v
Credentials
      |
      v
Containers
      |
      v
Security Controls
      |
      v
Automated Enumeration
      |
      v
Manual Validation
      |
      v
Privilege Escalation Candidates
```

Start broad and progressively focus on interesting relationships.

---

# 2. Initial Security Context

Begin with:

```bash
whoami
```

Then:

```bash
id
```

Example:

```text
uid=1000(analyst) gid=1000(analyst) groups=1000(analyst),27(sudo)
```

Important information:

```text
Username
UID
Primary GID
Supplementary groups
```

---

# 3. Current UID and GID

UID:

```bash
id -u
```

Username:

```bash
id -un
```

Primary group:

```bash
id -gn
```

All groups:

```bash
id -Gn
```

Numeric group IDs:

```bash
id -G
```

---

# 4. Root Context

The root account normally uses:

```text
UID 0
```

Check for all UID 0 accounts:

```bash
awk -F: '$3 == 0 {print $1 ":" $3 ":" $6 ":" $7}' /etc/passwd
```

Expected output commonly includes:

```text
root:0:/root:/bin/bash
```

Additional UID 0 accounts should be investigated.

---

# 5. Current Shell

Configured shell:

```bash
echo "$SHELL"
```

Current process:

```bash
ps -p $$ -o pid,ppid,user,comm,args
```

Available shells:

```bash
cat /etc/shells
```

Common shells include:

```text
/bin/bash
/bin/sh
/bin/zsh
/bin/dash
/bin/fish
```

---

# 6. Environment

Display:

```bash
env
```

Alternative:

```bash
printenv
```

Sorted:

```bash
printenv | sort
```

Interesting variables include:

```text
USER
LOGNAME
HOME
SHELL
PATH
PWD
OLDPWD
HOSTNAME
SSH_CLIENT
SSH_CONNECTION
SSH_TTY
SUDO_USER
SUDO_COMMAND
SUDO_UID
SUDO_GID
```

---

# 7. Sensitive Environment Variables

Target variable names:

```bash
printenv | grep -Ei 'pass|passwd|pwd|secret|token|api[_-]?key|credential|auth'
```

Possible secrets include:

```text
API tokens
Database passwords
Cloud credentials
Application secrets
Build tokens
Authentication tokens
```

A keyword match is only a candidate.

Do not automatically report it as a credential exposure.

---

# 8. PATH

Display:

```bash
echo "$PATH"
```

One directory per line:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Check permissions:

```bash
printf '%s\n' "$PATH" | tr ':' '\n' | while read -r dir; do
    [ -n "$dir" ] && ls -ld "$dir" 2>/dev/null
done
```

Look for directories writable by the current user.

---

# 9. PATH Analysis

A potentially unsafe relationship looks like:

```text
Privileged Process
       |
       v
Runs Command Without Absolute Path
       |
       v
PATH Search
       |
       v
User-Writable Directory
       |
       v
Attacker-Controlled Executable
```

A writable PATH directory alone does not prove privilege escalation.

The privileged execution relationship must also exist.

---

# 10. Hostname

```bash
hostname
```

Fully qualified:

```bash
hostname -f
```

Where systemd is present:

```bash
hostnamectl
```

Potential clues include:

```text
Environment
Application role
Location
Cluster
Domain
Naming convention
```

---

# 11. Operating System

Primary source:

```bash
cat /etc/os-release
```

Example:

```text
NAME="Debian GNU/Linux"
VERSION="13"
ID=debian
```

Alternative where installed:

```bash
lsb_release -a
```

---

# 12. Distribution Files

Useful files may include:

```text
/etc/os-release
/etc/debian_version
/etc/redhat-release
/etc/alpine-release
```

Target them individually where relevant.

Avoid relying on one generic command that assumes every distribution uses the same files.

---

# 13. Kernel

Kernel release:

```bash
uname -r
```

Complete:

```bash
uname -a
```

Architecture:

```bash
uname -m
```

Kernel version:

```bash
cat /proc/version
```

---

# 14. Architecture

```bash
uname -m
```

Where available:

```bash
arch
```

Common values:

```text
x86_64
aarch64
armv7l
i686
```

Architecture matters when analysing:

```text
Packages
Binaries
Containers
Kernel vulnerabilities
Exploit compatibility
```

---

# 15. Kernel Security Assessment

Do not use:

```text
Old Kernel
    =
Vulnerable Kernel
```

Use:

```text
Kernel Release
      |
      v
Distribution
      |
      v
Package Build
      |
      v
Vendor Security Advisory
      |
      v
Backported Fix?
      |
      v
Required Configuration
      |
      v
Practical Exposure
```

Linux distributions frequently backport security fixes.

---

# 16. Uptime

```bash
uptime
```

Boot time:

```bash
who -b
```

Where supported:

```bash
uptime -s
```

A long uptime may provide useful context around patching and reboot requirements, but it does not itself establish that security updates are missing.

---

# 17. System Time

```bash
date
```

Where available:

```bash
timedatectl
```

Record system time before collecting evidence that will later be correlated with logs.

---

# 18. CPU Information

```bash
lscpu
```

Alternative:

```bash
cat /proc/cpuinfo
```

Useful information includes:

```text
Architecture
CPU model
Virtualisation support
Core count
```

---

# 19. Memory

```bash
free -h
```

Detailed:

```bash
cat /proc/meminfo
```

Memory information is generally operational context rather than a security finding.

---

# 20. Block Devices

```bash
lsblk
```

Detailed:

```bash
lsblk -f
```

Potential information:

```text
Disks
Partitions
Filesystems
Mount points
UUIDs
Encryption
```

---

# 21. Mounted Filesystems

```bash
findmnt
```

Alternative:

```bash
mount
```

Disk usage:

```bash
df -hT
```

---

# 22. Mount Options

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

Potentially relevant options include:

```text
rw
ro
nosuid
nodev
noexec
relatime
```

Security significance depends on the mount's purpose.

---

# 23. `/etc/fstab`

```bash
cat /etc/fstab
```

Review for:

```text
Local filesystems
NFS
CIFS
Credentials references
Mount options
Application storage
Backup storage
```

Do not assume a network filesystem entry exposes credentials.

---

# 24. Current Users

Logged-in users:

```bash
who
```

More context:

```bash
w
```

Current login:

```bash
who am i
```

---

# 25. Login History

```bash
last
```

Failed login history may be available through:

```bash
lastb
```

`lastb` commonly requires elevated privileges.

Use login history only where relevant to the assessment.

---

# 26. Local User Accounts

```bash
cat /etc/passwd
```

Usernames:

```bash
cut -d: -f1 /etc/passwd
```

Structured:

```bash
awk -F: '{printf "%-20s UID=%-6s GID=%-6s HOME=%-30s SHELL=%s\n",$1,$3,$4,$6,$7}' /etc/passwd
```

---

# 27. Login-Capable Accounts

A useful candidate view:

```bash
awk -F: '$7 !~ /(nologin|false)$/ {print $1, $3, $6, $7}' /etc/passwd
```

This identifies accounts whose configured shell is not an obvious non-login shell.

It does not prove that every listed account can authenticate remotely.

---

# 28. Human User Candidates

On many distributions:

```bash
awk -F: '$3 >= 1000 && $3 < 65534 {print $1, $3, $6, $7}' /etc/passwd
```

UID allocation policies differ.

Treat this as a heuristic.

---

# 29. Groups

```bash
cat /etc/group
```

Current groups:

```bash
groups
```

or:

```bash
id
```

Specific group:

```bash
getent group sudo
```

---

# 30. Interesting Groups

Potentially high-value groups include:

```text
sudo
wheel
docker
lxd
lxc
disk
adm
shadow
systemd-journal
libvirt
```

Actual privilege varies by distribution and configuration.

Group membership should be analysed as delegated authority.

---

# 31. Sudo Group

Debian-family systems commonly use:

```bash
getent group sudo
```

RHEL-family systems commonly use:

```bash
getent group wheel
```

Do not assume group membership alone determines effective sudo permissions.

Always check:

```bash
sudo -l
```

---

# 32. Sudo Enumeration

```bash
sudo -l
```

This may reveal:

```text
ALL
NOPASSWD
Specific binaries
Specific scripts
Run-as identities
Environment permissions
Argument restrictions
```

Example:

```text
(root) NOPASSWD: /usr/bin/systemctl restart application.service
```

---

# 33. Sudo Rule Analysis

For each delegated command determine:

```text
Which user can run it?
        |
        v
As which identity?
        |
        v
Which executable?
        |
        v
Which arguments?
        |
        v
Can configuration be controlled?
        |
        v
Can files be read/written?
        |
        v
Can child commands execute?
        |
        v
Can the privilege boundary be crossed?
```

---

# 34. Sudoers Files

Main file:

```text
/etc/sudoers
```

Drop-in directory:

```text
/etc/sudoers.d/
```

List where permitted:

```bash
ls -la /etc/sudoers.d/ 2>/dev/null
```

Do not edit these files during enumeration.

---

# 35. User Home Directories

```bash
ls -la /home
```

Detailed:

```bash
find /home -maxdepth 1 -mindepth 1 -type d -exec ls -ld {} \; 2>/dev/null
```

Check whether unrelated users can access sensitive content.

---

# 36. Current Home Directory

```bash
echo "$HOME"
```

List:

```bash
ls -la "$HOME"
```

Interesting content may include:

```text
Shell history
SSH
Application configuration
Cloud configuration
Source repositories
Scripts
Backups
Credentials
```

---

# 37. Shell History

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
grep -Ei 'pass|passwd|pwd|secret|token|api[_-]?key|ssh|mysql|psql|sudo' ~/.bash_history 2>/dev/null
```

Review results manually.

---

# 38. History Files

Search current home:

```bash
find "$HOME" -maxdepth 3 -type f \( \
    -name '*history*' -o \
    -name '.bash_history' -o \
    -name '.zsh_history' \
\) -ls 2>/dev/null
```

Potential history files include:

```text
.bash_history
.zsh_history
.mysql_history
.psql_history
.python_history
.sqlite_history
```

---

# 39. SSH Directory

```bash
ls -la ~/.ssh 2>/dev/null
```

Common files:

```text
authorized_keys
known_hosts
config
id_rsa
id_ed25519
```

---

# 40. SSH Configuration

User configuration:

```bash
cat ~/.ssh/config 2>/dev/null
```

System configuration:

```bash
cat /etc/ssh/sshd_config 2>/dev/null
```

Drop-ins:

```bash
ls -la /etc/ssh/sshd_config.d/ 2>/dev/null
```

---

# 41. Effective SSH Server Configuration

Where supported:

```bash
sshd -T
```

Interesting settings:

```bash
sshd -T 2>/dev/null | grep -Ei 'permitrootlogin|passwordauthentication|pubkeyauthentication|allowusers|allowgroups|maxauthtries'
```

Context-dependent `Match` blocks may require additional parameters to evaluate accurately.

---

# 42. SSH Keys

Candidate files:

```bash
find ~/.ssh -maxdepth 1 -type f -ls 2>/dev/null
```

Check permissions:

```bash
stat -c '%A %a %U %G %n' ~/.ssh/* 2>/dev/null
```

Private keys should be handled as sensitive credential material.

---

# 43. Network Interfaces

```bash
ip addr
```

Compact:

```bash
ip -br addr
```

IPv4 only:

```bash
ip -4 addr
```

IPv6:

```bash
ip -6 addr
```

---

# 44. Routes

```bash
ip route
```

IPv6:

```bash
ip -6 route
```

Look for:

```text
Default gateway
Internal networks
VPN routes
Container networks
Management networks
```

---

# 45. Neighbours

```bash
ip neigh
```

This may reveal recently observed local network systems.

Do not treat the neighbour table as a complete network inventory.

---

# 46. DNS

```bash
cat /etc/resolv.conf
```

Where systemd-resolved is used:

```bash
resolvectl status
```

Search domains can provide useful environment context.

---

# 47. Hosts File

```bash
cat /etc/hosts
```

Potential information:

```text
Internal systems
Application aliases
Cluster nodes
Development endpoints
```

Entries may be stale.

Validate before relying on them.

---

# 48. Listening Sockets

```bash
ss -lntup
```

TCP:

```bash
ss -lntp
```

UDP:

```bash
ss -lnup
```

Process details may be restricted for sockets owned by other users.

---

# 49. Established Connections

```bash
ss -antp
```

Summary:

```bash
ss -s
```

Potential observations include:

```text
Internal dependencies
Database connections
Management connections
Unexpected external communication
```

---

# 50. Unix Domain Sockets

```bash
ss -lx
```

Unix sockets can expose local application interfaces.

Interesting examples may include:

```text
Docker
Databases
Application control sockets
System services
```

Permissions matter.

---

# 51. Network Namespace Context

```bash
ip netns list 2>/dev/null
```

Current network namespace:

```bash
readlink /proc/$$/ns/net
```

Containerised or specialised environments may use multiple network namespaces.

---

# 52. Firewall Identification

Look for available tools:

```bash
command -v nft
command -v iptables
command -v ufw
command -v firewall-cmd
```

This helps identify likely firewall management frameworks.

---

# 53. nftables

Where authorised and permitted:

```bash
sudo nft list ruleset
```

Without sufficient privileges, complete firewall configuration may not be available.

Do not modify rules during enumeration.

---

# 54. iptables

```bash
sudo iptables -L -n -v
```

IPv6:

```bash
sudo ip6tables -L -n -v
```

Modern distributions may provide iptables compatibility backed by nftables.

---

# 55. UFW

```bash
sudo ufw status verbose
```

Rules:

```bash
sudo ufw status numbered
```

Do not enable, disable, or alter UFW during enumeration.

---

# 56. firewalld

```bash
firewall-cmd --state
```

Current zone:

```bash
firewall-cmd --get-active-zones
```

Configuration:

```bash
firewall-cmd --list-all
```

Permissions and PolicyKit configuration may affect access.

---

# 57. Process Enumeration

```bash
ps aux
```

Alternative:

```bash
ps -ef
```

Useful structured view:

```bash
ps -eo user,pid,ppid,%cpu,%mem,comm,args --sort=user
```

---

# 58. Process Tree

```bash
ps -ef --forest
```

Where installed:

```bash
pstree -ap
```

Parent-child relationships can reveal:

```text
Service launchers
Shells
Scheduled jobs
Application workers
Container processes
```

---

# 59. Root Processes

```bash
ps -U root -u root u
```

Alternative:

```bash
ps -eo user,pid,ppid,comm,args | awk '$1 == "root"'
```

A large number of root processes is normal on many Linux systems.

Focus on custom or influenceable privileged processes.

---

# 60. Interesting Processes

```bash
ps -eo user,pid,ppid,comm,args |
    grep -Ei 'python|perl|ruby|java|node|nginx|apache|httpd|mysql|postgres|redis|docker|containerd'
```

Use this as a filter, not as proof of a weakness.

---

# 61. Process Executable

For a process:

```bash
readlink -f /proc/PID/exe
```

Replace `PID` with the process identifier.

Permissions may restrict access.

---

# 62. Process Working Directory

```bash
readlink -f /proc/PID/cwd
```

This can help identify application directories.

---

# 63. Process Command Line

```bash
tr '\0' ' ' < /proc/PID/cmdline
```

Visibility depends on process ownership and system configuration.

Command lines may contain sensitive information.

---

# 64. Process Environment

For your own shell:

```bash
tr '\0' '\n' < /proc/$$/environ
```

For another process:

```bash
tr '\0' '\n' < /proc/PID/environ
```

Access may be restricted.

Do not indiscriminately collect other users' environment data.

---

# 65. Process Credentials

```bash
grep -E '^(Uid|Gid|Groups):' /proc/PID/status
```

Capabilities:

```bash
grep '^Cap' /proc/PID/status
```

This can help establish the actual security context of a process.

---

# 66. systemd

Check:

```bash
systemctl --version
```

Running services:

```bash
systemctl list-units --type=service --state=running
```

All service units:

```bash
systemctl list-unit-files --type=service
```

---

# 67. Failed Services

```bash
systemctl --failed
```

Failed services can reveal:

```text
Broken deployments
Misconfiguration
Old software
Unused components
Operational issues
```

A failed service is not automatically a security finding.

---

# 68. Custom Services

List service files under common administrative locations:

```bash
find /etc/systemd/system -type f -name '*.service' -ls 2>/dev/null
```

Custom units deserve additional attention because they often contain organisation-specific scripts and configuration.

---

# 69. Service Details

```bash
systemctl status example.service
```

Effective unit:

```bash
systemctl cat example.service
```

Properties:

```bash
systemctl show example.service
```

---

# 70. Service Identity

```bash
systemctl show example.service -p User -p Group
```

An empty `User=` for a system service commonly means it runs as root unless another mechanism changes the execution context.

Validate the actual running process where possible.

---

# 71. Service Execution

```bash
systemctl show example.service -p ExecStart -p ExecStartPre -p ExecStartPost
```

Then inspect referenced:

```text
Executables
Scripts
Configuration
Environment files
Working directories
```

Detailed analysis belongs in [Linux Services](services.md).

---

# 72. Service Environment

```bash
systemctl show example.service -p Environment -p EnvironmentFiles
```

Where an environment file is referenced, inspect permissions before reading sensitive content.

---

# 73. Service Hardening

Where supported:

```bash
systemd-analyze security example.service
```

This provides a security-oriented review of systemd sandboxing settings.

It is not a vulnerability scanner and should not be used as the sole basis for a finding.

---

# 74. Legacy Services

SysV-style services may exist beneath:

```text
/etc/init.d/
```

Enumerate:

```bash
ls -la /etc/init.d/ 2>/dev/null
```

Some systems use compatibility layers around these scripts.

---

# 75. Cron

Current user's crontab:

```bash
crontab -l
```

System:

```bash
cat /etc/crontab
```

Cron directories:

```bash
ls -la /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly 2>/dev/null
```

---

# 76. Cron Files

Inspect metadata:

```bash
find /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly \
    -maxdepth 1 -type f -ls 2>/dev/null
```

Look for:

```text
Custom scripts
Weak permissions
Unexpected ownership
References to writable paths
```

---

# 77. Cron Execution Relationship

For each interesting cron entry determine:

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
Script / Binary
   |
   v
Dependencies
   |
   v
Permissions
```

The schedule alone is not a vulnerability.

---

# 78. systemd Timers

```bash
systemctl list-timers --all
```

Identify the associated service:

```bash
systemctl status example.timer
```

Then:

```bash
systemctl cat example.timer
systemctl cat example.service
```

---

# 79. `at`

Where installed:

```bash
atq
```

Package presence:

```bash
command -v at
```

Do not assume `at` is installed or enabled.

---

# 80. Installed Software - Debian

```bash
dpkg -l
```

Package names and versions:

```bash
dpkg-query -W -f='${Package}\t${Version}\n'
```

---

# 81. Installed Software - RPM

```bash
rpm -qa
```

Sorted:

```bash
rpm -qa | sort
```

---

# 82. Installed Software - DNF

```bash
dnf list installed
```

---

# 83. Installed Software - Alpine

```bash
apk info
```

Versions:

```bash
apk info -v
```

---

# 84. Package Managers

Identify:

```bash
command -v apt
command -v dpkg
command -v dnf
command -v yum
command -v rpm
command -v apk
command -v pacman
```

Use the distribution-native package database when validating versions.

---

# 85. Package Security

For a potentially vulnerable package, collect:

```text
Distribution
Package name
Package version
Repository
Vendor advisory
Security patch status
Runtime configuration
Reachability
```

Do not rely solely on upstream version comparison.

---

# 86. Filesystem Overview

Important locations include:

```text
/etc
/home
/root
/tmp
/var/tmp
/opt
/srv
/usr/local
/var/www
/var/lib
/var/log
```

Prioritise custom application directories.

---

# 87. File Permission Inspection

```bash
ls -l /path/to/file
```

Numeric:

```bash
stat -c '%A %a %U %G %n' /path/to/file
```

ACL:

```bash
getfacl /path/to/file
```

---

# 88. Directory Permission Inspection

```bash
ls -ld /path/to/directory
```

Numeric:

```bash
stat -c '%A %a %U %G %n' /path/to/directory
```

Remember:

```text
Directory read    -> list names
Directory write   -> modify entries
Directory execute -> traverse
```

---

# 89. Writable Application Files

```bash
find /opt /srv /usr/local /var/www -type f -writable -ls 2>/dev/null
```

Investigate files associated with privileged services or scheduled jobs first.

---

# 90. Writable Application Directories

```bash
find /opt /srv /usr/local /var/www -type d -writable -ls 2>/dev/null
```

A writable directory may allow creation, deletion, or replacement of files depending on permissions and sticky-bit behaviour.

---

# 91. Root-Owned Writable Files

```bash
find /etc /opt /srv /usr/local /var/www -xdev -user root -type f -writable -ls 2>/dev/null
```

This is a candidate search.

Manually verify the current user's effective access.

---

# 92. World-Writable Files

```bash
find /etc /opt /srv /usr/local /var -xdev -type f -perm -0002 -ls 2>/dev/null
```

World-writable files used by privileged components deserve investigation.

---

# 93. World-Writable Directories

```bash
find /etc /opt /srv /usr/local /var -xdev -type d -perm -0002 -ls 2>/dev/null
```

Expect legitimate results such as temporary directories.

Review purpose and sticky-bit protection.

---

# 94. `/tmp`

```bash
stat -c '%A %a %U %G %n' /tmp
```

Typical:

```text
drwxrwxrwt 1777 root root /tmp
```

The final `t` represents the sticky bit.

---

# 95. `/var/tmp`

```bash
stat -c '%A %a %U %G %n' /var/tmp
```

Like `/tmp`, it is commonly shared and writable.

The security issue is usually unsafe use by privileged applications rather than the directory's existence.

---

# 96. SUID Enumeration

```bash
find / -xdev -perm -4000 -type f -ls 2>/dev/null
```

Record:

```text
Path
Owner
Permissions
Package
Purpose
```

---

# 97. SGID Enumeration

```bash
find / -xdev -perm -2000 -type f -ls 2>/dev/null
```

Combined:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

---

# 98. SUID Package Ownership

Debian-based:

```bash
dpkg -S /path/to/binary 2>/dev/null
```

RPM-based:

```bash
rpm -qf /path/to/binary 2>/dev/null
```

This helps distinguish distribution-provided binaries from custom executables.

---

# 99. Custom SUID Binaries

Prioritise SUID files that are:

```text
Outside normal system paths
Not owned by a known package
Recently modified
Custom-developed
Unexpectedly writable
```

Example search after inventory:

```bash
find /opt /srv /usr/local -type f -perm -4000 -ls 2>/dev/null
```

---

# 100. Linux Capabilities

```bash
getcap -r / 2>/dev/null
```

Example:

```text
/usr/bin/example cap_net_raw=ep
```

Capabilities should be analysed according to what they permit.

---

# 101. Interesting Capabilities

Examples that may deserve closer review:

```text
cap_setuid
cap_setgid
cap_dac_override
cap_dac_read_search
cap_sys_admin
cap_sys_ptrace
cap_net_admin
cap_net_raw
cap_chown
cap_fowner
```

The binary's behaviour remains critical.

---

# 102. Current Process Capabilities

```bash
grep '^Cap' /proc/$$/status
```

Where available:

```bash
capsh --print
```

Containerised environments may expose a different capability set from the host.

---

# 103. File ACLs

Identify files with ACL indicators through targeted inspection.

Example:

```bash
getfacl /opt/application/config 2>/dev/null
```

ACLs can grant permissions not immediately obvious from standard mode bits.

---

# 104. Extended Attributes

Inspect:

```bash
getfattr -d /path/to/file 2>/dev/null
```

Extended attributes can contain metadata used by security mechanisms and applications.

Only investigate where relevant.

---

# 105. Immutable and Other File Attributes

Where supported:

```bash
lsattr /path/to/file
```

Example flags may include:

```text
i - immutable
a - append only
```

These are separate from traditional Unix permissions.

---

# 106. Interesting Application Directories

Start with:

```bash
ls -la /opt
ls -la /srv
ls -la /usr/local
ls -la /var/www 2>/dev/null
```

Then investigate only directories associated with installed or running applications.

---

# 107. Configuration Files

Targeted search:

```bash
find /opt /srv /var/www /usr/local -type f \( \
    -name '*.conf' -o \
    -name '*.config' -o \
    -name '*.ini' -o \
    -name '*.yaml' -o \
    -name '*.yml' -o \
    -name '*.json' -o \
    -name '*.xml' -o \
    -name '*.properties' -o \
    -name '.env' \
\) 2>/dev/null
```

---

# 108. Sensitive Configuration Search

For a known application:

```bash
grep -RniE 'password|passwd|secret|token|api[_-]?key|credential' /opt/application 2>/dev/null
```

Do not use this as a blanket search across unrelated user data.

---

# 109. Environment Files

Search likely application locations:

```bash
find /opt /srv /var/www /home -type f \( -name '.env' -o -name '.env.*' \) -ls 2>/dev/null
```

Potential contents:

```text
Database credentials
API tokens
Application secrets
Cloud configuration
```

Permissions determine exposure.

---

# 110. Backup Files

```bash
find /opt /srv /var/www /etc -type f \( \
    -name '*.bak' -o \
    -name '*.backup' -o \
    -name '*.old' -o \
    -name '*.orig' -o \
    -name '*.save' \
\) -ls 2>/dev/null
```

Historical configuration can expose credentials removed from active files.

---

# 111. Swap Files

Editor swap files can expose old content.

Target application directories:

```bash
find /opt /srv /var/www -type f \( -name '*.swp' -o -name '*.swo' \) -ls 2>/dev/null
```

Do not report editor files unless sensitive content is actually exposed.

---

# 112. Git Repositories

```bash
find /opt /srv /var/www /home -type d -name .git -print 2>/dev/null
```

Potential value:

```text
Source
Configuration
History
Secrets
Internal endpoints
Deployment logic
```

Review only repositories within scope.

---

# 113. Git Status

Inside an authorised repository:

```bash
git status
```

History:

```bash
git log --oneline --decorate -n 20
```

Remote configuration:

```bash
git remote -v
```

Remote URLs may themselves contain sensitive information in poorly configured environments.

---

# 114. Credential Candidates

Useful locations include:

```text
Shell history
SSH configuration
Application configuration
Environment files
Git repositories
Database clients
Backup files
Cloud configuration
Service environment files
```

Detailed handling belongs in [Linux Credentials](credentials.md).

---

# 115. `/etc/shadow` Permissions

Inspect metadata:

```bash
ls -l /etc/shadow
```

Numeric:

```bash
stat -c '%A %a %U %G %n' /etc/shadow
```

Do not read or copy password hashes unless explicitly required and authorised.

---

# 116. `/etc/gshadow`

```bash
ls -l /etc/gshadow
```

This is also security-sensitive and should normally have restrictive permissions.

---

# 117. SSH Private-Key Search

Start with the current user:

```bash
find "$HOME/.ssh" -maxdepth 1 -type f -ls 2>/dev/null
```

Avoid immediately searching every user's home directory.

Escalate only when scope and permissions justify it.

---

# 118. Cloud Configuration

Potential user directories include:

```text
~/.aws
~/.azure
~/.config/gcloud
```

Check existence:

```bash
ls -ld ~/.aws ~/.azure ~/.config/gcloud 2>/dev/null
```

Do not automatically read or export cloud credentials.

Cloud testing must be in scope.

---

# 119. Kubernetes Configuration

Potential configuration:

```text
~/.kube/config
```

Check:

```bash
ls -l ~/.kube/config 2>/dev/null
```

A Kubernetes configuration file can contain:

```text
Cluster endpoints
Certificates
Tokens
Authentication configuration
```

Treat it as sensitive.

---

# 120. Docker Enumeration

Version:

```bash
docker --version 2>/dev/null
```

Group:

```bash
id
```

Socket:

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

Daemon process:

```bash
ps -ef | grep '[d]ockerd'
```

---

# 121. Docker Access

Where authorised:

```bash
docker info
```

Containers:

```bash
docker ps
```

Do not create, modify, stop, or remove containers during routine enumeration.

---

# 122. Container Runtime

Identify common runtimes:

```bash
command -v docker
command -v podman
command -v containerd
command -v crictl
command -v nerdctl
```

Processes:

```bash
ps -ef | grep -Ei '[d]ocker|[c]ontainerd|[p]odman|[c]rio'
```

---

# 123. Container Detection

```bash
test -f /.dockerenv && echo "Docker environment indicator present"
```

PID 1:

```bash
ps -p 1 -o pid,user,comm,args
```

Control groups:

```bash
cat /proc/1/cgroup
```

Mounts:

```bash
findmnt
```

Use several indicators rather than relying on one file.

---

# 124. Container Mounts

```bash
findmnt
```

Inspect for:

```text
Host filesystem mounts
Docker socket
Configuration
Secrets
Device mounts
```

Container escape analysis should only be performed when explicitly within scope.

---

# 125. LXD

```bash
command -v lxc
```

Group:

```bash
getent group lxd
```

Current membership:

```bash
id
```

LXD administrative access can provide extensive host authority.

---

# 126. Virtualisation

```bash
systemd-detect-virt
```

Alternative indicators:

```bash
cat /sys/class/dmi/id/product_name 2>/dev/null
cat /sys/class/dmi/id/sys_vendor 2>/dev/null
```

Possible environments include:

```text
KVM
VMware
Hyper-V
VirtualBox
Cloud platforms
Containers
```

---

# 127. NFS

Mounted:

```bash
findmnt -t nfs,nfs4
```

Server exports where applicable:

```bash
cat /etc/exports 2>/dev/null
```

NFS security depends on configuration and filesystem permissions.

---

# 128. CIFS / SMB Mounts

```bash
findmnt -t cifs
```

Review:

```bash
grep -Ei 'cifs|smb' /etc/fstab 2>/dev/null
```

Be alert for references to credential files.

Do not automatically display those credentials.

---

# 129. Database Processes

```bash
ps -ef | grep -Ei '[m]ysql|[m]ariadb|[p]ostgres|[m]ongod|[r]edis'
```

Listeners:

```bash
ss -lntp
```

Potential configuration:

```text
/etc/mysql
/etc/postgresql
/etc/redis
```

---

# 130. Web Servers

```bash
ps -ef | grep -Ei '[n]ginx|[a]pache|[h]ttpd|[c]addy'
```

Common configuration directories:

```text
/etc/nginx
/etc/apache2
/etc/httpd
```

Actual paths vary.

---

# 131. Web Roots

Common candidates:

```text
/var/www
/srv/www
/opt/application
```

Determine actual paths from service configuration rather than assuming the default.

---

# 132. Application Service Accounts

Use:

```bash
ps -eo user,pid,ppid,comm,args
```

Identify service identities such as:

```text
www-data
nginx
apache
postgres
mysql
redis
Application-specific accounts
```

The account name itself is not a weakness.

---

# 133. Security Modules

Active LSMs where exposed:

```bash
cat /sys/kernel/security/lsm 2>/dev/null
```

Potential entries:

```text
selinux
apparmor
landlock
lockdown
yama
```

---

# 134. SELinux

```bash
getenforce 2>/dev/null
```

Detailed:

```bash
sestatus 2>/dev/null
```

Possible states:

```text
Enforcing
Permissive
Disabled
```

Interpret against the system's security baseline.

---

# 135. AppArmor

```bash
aa-status 2>/dev/null
```

Where additional privileges are required:

```bash
sudo aa-status
```

Profiles can be:

```text
Enforce
Complain
Unconfined
```

---

# 136. Yama

```bash
cat /proc/sys/kernel/yama/ptrace_scope 2>/dev/null
```

This affects process tracing restrictions.

Do not treat one value as a complete measure of process security.

---

# 137. ASLR

```bash
sysctl kernel.randomize_va_space
```

Alternative:

```bash
cat /proc/sys/kernel/randomize_va_space
```

ASLR is one exploit mitigation layer.

---

# 138. Kernel Pointer Restriction

```bash
sysctl kernel.kptr_restrict
```

Kernel log restriction:

```bash
sysctl kernel.dmesg_restrict
```

These reduce selected information exposures.

---

# 139. Protected Symlinks and Hardlinks

```bash
sysctl fs.protected_symlinks
```

```bash
sysctl fs.protected_hardlinks
```

These controls help mitigate certain unsafe temporary-file and link-based behaviours.

---

# 140. Core Dumps

Check shell limit:

```bash
ulimit -c
```

systemd configuration may also influence core dump handling.

Core dumps can contain sensitive process memory.

Do not generate dumps unnecessarily.

---

# 141. `/proc` Restrictions

```bash
findmnt /proc
```

Look for mount options such as:

```text
hidepid
```

Process visibility restrictions can reduce information exposure between users.

---

# 142. Secure Boot

Where available:

```bash
mokutil --sb-state 2>/dev/null
```

Absence of `mokutil` does not mean Secure Boot is disabled.

---

# 143. Auditd

Service:

```bash
systemctl status auditd 2>/dev/null
```

Where permitted:

```bash
auditctl -s
```

Rules:

```bash
auditctl -l
```

Complete audit configuration may require root.

---

# 144. Logging

Common location:

```bash
ls -lah /var/log
```

systemd journal:

```bash
journalctl -n 100
```

Current boot:

```bash
journalctl -b
```

Permissions may restrict access.

---

# 145. Authentication Logs

Debian-family:

```bash
grep -Ei 'sudo|sshd|authentication|session' /var/log/auth.log 2>/dev/null
```

RHEL-family:

```bash
grep -Ei 'sudo|sshd|authentication|session' /var/log/secure 2>/dev/null
```

Do not assume these files exist when journald-only logging is configured.

---

# 146. SSH Logs

Using journal:

```bash
journalctl -u ssh 2>/dev/null
```

or:

```bash
journalctl -u sshd 2>/dev/null
```

Service naming varies by distribution.

---

# 147. Sudo Logs

Depending on logging configuration:

```bash
journalctl _COMM=sudo 2>/dev/null
```

or:

```bash
grep -i sudo /var/log/auth.log 2>/dev/null
```

Logging behaviour depends on sudo and system configuration.

---

# 148. Security Software

Search process names broadly:

```bash
ps -ef
```

Then identify:

```text
EDR
Antivirus
Audit agents
SIEM forwarders
Configuration management
File integrity monitoring
Monitoring agents
```

Do not terminate, disable, or tamper with defensive software.

---

# 149. Configuration Management

Potential agents include:

```text
Ansible-related automation
Puppet
Chef
Salt
Cloud agents
Custom management agents
```

Processes:

```bash
ps -ef | grep -Ei '[p]uppet|[c]hef|[s]alt'
```

Configuration-management directories can contain sensitive deployment information.

---

# 150. Recently Modified Files

Target an application directory:

```bash
find /opt/application -type f -mtime -7 -ls 2>/dev/null
```

This can help identify recent deployment changes.

Do not search the entire filesystem unless necessary.

---

# 151. Recently Modified SUID Files

```bash
find / -xdev -type f -perm -4000 -mtime -30 -ls 2>/dev/null
```

A recently modified SUID file may warrant additional investigation.

Modification time alone does not establish malicious or insecure behaviour.

---

# 152. Recently Modified Configuration

```bash
find /etc -type f -mtime -7 -ls 2>/dev/null
```

This can produce substantial output.

Use only when change timing is relevant.

---

# 153. Executables Outside Standard Paths

Custom executable directories:

```bash
find /opt /srv /usr/local -type f -executable -ls 2>/dev/null
```

Prioritise executables referenced by:

```text
Root services
Cron
Sudo
Administrative scripts
```

---

# 154. Script Inventory

```bash
find /opt /srv /usr/local /var/www -type f \( \
    -name '*.sh' -o \
    -name '*.py' -o \
    -name '*.pl' -o \
    -name '*.rb' \
\) -ls 2>/dev/null
```

Then inspect permissions and privileged consumers.

---

# 155. Interpreter Inventory

```bash
command -v bash
command -v sh
command -v python3
command -v python
command -v perl
command -v ruby
command -v php
command -v node
```

Interpreter presence is normally informational.

It becomes relevant when privileged mechanisms delegate execution through them.

---

# 156. Compiler Availability

```bash
command -v gcc
command -v clang
command -v cc
command -v make
```

Compiler presence is not itself a security weakness.

It may be useful context for development systems and authorised testing.

---

# 157. Tool Availability

```bash
command -v curl
command -v wget
command -v nc
command -v ncat
command -v socat
command -v openssl
command -v ssh
command -v git
```

Treat installed tools as system capabilities, not vulnerabilities.

---

# 158. Writable Service Dependencies

When a privileged service is interesting:

```text
Service Unit
     |
     v
Executable
     |
     +---- Script
     +---- Config
     +---- Environment File
     +---- Working Directory
     +---- Libraries
     |
     v
Permission Analysis
```

Check each dependency individually.

---

# 159. Parent Directory Permissions

For a file:

```bash
namei -l /opt/application/bin/service
```

`namei -l` can reveal permissions across every component of the path.

This is useful when a file itself is protected but a parent directory may allow replacement or path manipulation.

---

# 160. `namei`

Example:

```bash
namei -l /opt/application/config/settings.conf
```

Possible output conceptually shows:

```text
/
opt
application
config
settings.conf
```

with ownership and permissions for each path component.

---

# 161. SUID Analysis Workflow

```text
Enumerate SUID
      |
      v
Identify Package
      |
      v
Standard or Custom?
      |
      v
Inspect Binary Behaviour
      |
      v
Inputs / Files / Commands
      |
      v
Can User Influence Behaviour?
      |
      v
Privilege Boundary?
```

Do not report every SUID binary.

---

# 162. Capability Analysis Workflow

```text
getcap
   |
   v
Binary
   |
   v
Capability
   |
   v
Binary Functionality
   |
   v
Current User Can Execute?
   |
   v
Can Capability Be Leveraged?
```

---

# 163. Cron Analysis Workflow

```text
Cron Entry
    |
    v
Execution User
    |
    v
Command
    |
    v
Script / Binary
    |
    v
Parent Directories
    |
    v
Dependencies
    |
    v
Current User Influence?
```

---

# 164. Service Analysis Workflow

```text
Service
   |
   v
Execution Identity
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
Environment
   |
   v
Permissions
   |
   v
User-Controlled Resource?
```

---

# 165. Credential Analysis Workflow

```text
Potential Secret
      |
      v
Actually Sensitive?
      |
      v
Who Can Read It?
      |
      v
Which Identity?
      |
      v
Which Resource?
      |
      v
Privilege?
      |
      v
Minimal Validation
```

See [Linux Credentials](credentials.md).

---

# 166. Kernel Analysis Workflow

```text
uname -r
   |
   v
Distribution
   |
   v
Exact Package
   |
   v
Vendor Advisory
   |
   v
Affected Build?
   |
   v
Mitigations
   |
   v
Exploit Preconditions
```

Kernel exploitation should generally be a later-stage validation method because of its operational risk.

---

# 167. Automated Enumeration Strategy

Recommended approach:

```text
Manual Baseline
      |
      v
Run One Enumeration Tool
      |
      v
Review Output
      |
      v
Select Candidates
      |
      v
Manual Validation
      |
      v
Additional Tool Only If Needed
```

Avoid running multiple large scripts without first reviewing the information already collected.

---

# 168. LinPEAS

Project:

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

LinPEAS can enumerate areas including:

```text
System information
Sudo
SUID
Capabilities
Processes
Services
Cron
Credentials
Containers
Interesting files
Permissions
```

Treat colour-highlighted results as investigation candidates.

---

# 169. LinEnum

Project:

[LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }

LinEnum performs broad Linux host enumeration.

It can be useful for validating manual coverage.

---

# 170. Linux Smart Enumeration

Project:

[linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

The tool focuses on identifying Linux privilege escalation information.

Use it to prioritise manual investigation.

---

# 171. pspy

Project:

[pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }

pspy can help observe processes executed by other users in environments where normal process enumeration does not provide sufficient timing visibility.

Potential use cases:

```text
Cron discovery
Periodic scripts
Administrative automation
Short-lived processes
```

Use only within the authorised scope.

---

# 172. Tool Transfer Considerations

Before transferring enumeration tools, consider:

```text
Is transfer allowed?
Is the host production?
Will EDR alert?
Can native commands answer the question?
Does the tool write files?
Does it require execution permission?
Does it collect sensitive information?
```

Native enumeration is often sufficient.

---

# 173. No-Tool Enumeration

A useful native-only sequence:

```bash
whoami
id
hostname
cat /etc/os-release
uname -a
sudo -l
ip -br addr
ip route
ss -lntup
ps -ef
findmnt
systemctl list-units --type=service --state=running
systemctl list-timers --all
crontab -l
getcap -r / 2>/dev/null
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

Then investigate interesting results individually.

---

# 174. Low-Noise Workflow

## Phase 1 - Identity

```bash
whoami
id
groups
```

## Phase 2 - System

```bash
hostname
cat /etc/os-release
uname -a
```

## Phase 3 - Privilege

```bash
sudo -l
```

## Phase 4 - Network

```bash
ip -br addr
ip route
ss -lntup
```

## Phase 5 - Processes

```bash
ps -ef
```

## Phase 6 - Services

```bash
systemctl list-units --type=service --state=running
```

## Phase 7 - Scheduled Execution

```bash
crontab -l
systemctl list-timers --all
```

## Phase 8 - Filesystem

```bash
findmnt
```

Then perform targeted permission searches.

---

# 175. High-Value Candidate Prioritisation

Prioritise relationships such as:

```text
sudo delegation
        |
        v
Potential privileged functionality
```

```text
Root service
        |
        v
User-writable executable/config
```

```text
Root cron
        |
        v
User-writable script
```

```text
SUID binary
        |
        v
Custom/influenceable behaviour
```

```text
Dangerous capability
        |
        v
User-controlled executable behaviour
```

```text
Accessible credential
        |
        v
Higher-privileged account
```

---

# 176. Permission Validation

Do not rely only on visual inspection.

For a candidate file:

```bash
stat -c '%A %a %U %G %n' /path/to/file
```

ACL:

```bash
getfacl /path/to/file
```

Path components:

```bash
namei -l /path/to/file
```

Current user:

```bash
id
```

Together these provide stronger evidence.

---

# 177. Non-Destructive Write Validation

Where required and authorised:

```bash
dir="/opt/application"
testfile="$dir/.write-test-$$"

if touch "$testfile" 2>/dev/null; then
    echo "[+] Writable: $dir"
    rm -f "$testfile"
else
    echo "[-] Not writable: $dir"
fi
```

This confirms directory write access without replacing application files.

---

# 178. Do Not Modify the Target File

Prefer:

```text
Check ACL
    |
    v
Check Effective Access
    |
    v
Create Separate Temporary Test File
```

instead of:

```text
Overwrite Production Script
```

Privilege escalation can often be demonstrated through permissions and execution relationships without actually changing privileged resources.

---

# 179. Evidence Collection

For each candidate record:

```text
Hostname
Timestamp
Current user
UID / groups
Affected path
Owner
Group
Permissions
ACL
Privileged process/service
Execution identity
Configuration
Relationship
Validation performed
Impact
```

---

# 180. Evidence Example

```text
Host:
linux-app-01

Current user:
analyst

Service:
backup-agent.service

Service identity:
root

Executable:
/opt/backup/bin/backup.sh

Owner:
root

Permissions:
775

Writable through:
backup group

Current user membership:
backup
```

This is stronger than merely reporting:

```text
Writable script found
```

---

# 181. Root Cause Analysis

Ask:

```text
Why can the user modify the resource?
```

Possible causes:

```text
Incorrect ownership
Excessive group permissions
World-writable mode
Unsafe ACL
Deployment process
Shared application directory
Misconfigured sudo
Overprivileged container group
Credential exposure
```

Report the underlying cause.

---

# 182. Enumeration Finding Model

Weak:

```text
LinPEAS highlighted file in red.
```

Strong:

```text
The standard user belongs to the application group.

That group has write permission to a script executed by a systemd service
running as root.

The service executes the affected script during startup.
```

Automated-tool output should not be the primary evidence.

---

# 183. What Not to Report Automatically

Do not automatically report:

```text
SUID binaries exist
SGID binaries exist
cron exists
systemd exists
root processes exist
Docker is installed
SSH is enabled
gcc is installed
Python is installed
/tmp is writable
Kernel appears old
SELinux is disabled
AppArmor is absent
Environment variables exist
Private keys exist
```

Determine whether an actual security boundary is weakened.

---

# 184. False Positive Reduction

For every candidate ask:

```text
Is the observation expected?
        |
        v
Can current user access it?
        |
        v
Can current user modify it?
        |
        v
Does a privileged process consume it?
        |
        v
Can the behaviour actually be influenced?
        |
        v
Is impact realistic?
```

If the chain breaks, reconsider the finding.

---

# 185. Enumeration Checklist

## Identity

- [ ] `whoami`
- [ ] `id`
- [ ] Groups
- [ ] UID / GID
- [ ] Shell
- [ ] Environment
- [ ] PATH

## System

- [ ] Hostname
- [ ] Distribution
- [ ] Kernel
- [ ] Architecture
- [ ] Uptime
- [ ] Time
- [ ] CPU
- [ ] Memory
- [ ] Block devices

## Users

- [ ] `/etc/passwd`
- [ ] UID 0 accounts
- [ ] Login-capable accounts
- [ ] Human user candidates
- [ ] Home directories
- [ ] Logged-in users
- [ ] Login history

## Privilege

- [ ] `sudo -l`
- [ ] Sudo groups
- [ ] Sudoers drop-ins
- [ ] SUID
- [ ] SGID
- [ ] Capabilities
- [ ] ACLs

## Network

- [ ] Interfaces
- [ ] Routes
- [ ] Neighbours
- [ ] DNS
- [ ] Hosts file
- [ ] Listening sockets
- [ ] Connections
- [ ] Unix sockets
- [ ] Firewall

## Processes

- [ ] Running processes
- [ ] Root processes
- [ ] Process tree
- [ ] Command lines
- [ ] Executable paths
- [ ] Process identity
- [ ] Capabilities

## Services

- [ ] Running systemd services
- [ ] Custom services
- [ ] Failed services
- [ ] Service identity
- [ ] ExecStart
- [ ] Environment files
- [ ] Executable permissions
- [ ] Configuration permissions

## Scheduled Execution

- [ ] User crontab
- [ ] `/etc/crontab`
- [ ] `/etc/cron.d`
- [ ] Periodic cron
- [ ] systemd timers
- [ ] `at`
- [ ] Scheduled script permissions

## Filesystem

- [ ] Mounts
- [ ] Mount options
- [ ] `/etc/fstab`
- [ ] Writable application files
- [ ] Writable application directories
- [ ] World-writable files
- [ ] World-writable directories
- [ ] Parent directory permissions
- [ ] Backups
- [ ] Custom scripts

## Credentials

- [ ] Shell history
- [ ] SSH
- [ ] Environment
- [ ] `.env`
- [ ] Application configuration
- [ ] Git repositories
- [ ] Cloud configuration
- [ ] Kubernetes configuration
- [ ] Sensitive backup files

## Containers

- [ ] Docker
- [ ] Docker socket
- [ ] Docker group
- [ ] Podman
- [ ] containerd
- [ ] LXD
- [ ] Container detection
- [ ] Capabilities
- [ ] Mounts

## Security Controls

- [ ] SELinux
- [ ] AppArmor
- [ ] Active LSMs
- [ ] Yama
- [ ] ASLR
- [ ] Kernel information restrictions
- [ ] Auditd
- [ ] Firewall
- [ ] Endpoint security
- [ ] Secure Boot where relevant

## Validation

- [ ] Identify candidate
- [ ] Check permissions
- [ ] Check ACL
- [ ] Check parent directories
- [ ] Identify privileged consumer
- [ ] Establish execution relationship
- [ ] Validate minimally
- [ ] Preserve evidence

---

# 186. Quick Reference

Identity:

```bash
whoami
id
groups
```

System:

```bash
hostname
cat /etc/os-release
uname -a
```

Sudo:

```bash
sudo -l
```

Network:

```bash
ip -br addr
ip route
ip neigh
ss -lntup
```

Processes:

```bash
ps -ef
```

Services:

```bash
systemctl list-units --type=service --state=running
```

Timers:

```bash
systemctl list-timers --all
```

Cron:

```bash
crontab -l
cat /etc/crontab
```

Mounts:

```bash
findmnt
```

SUID / SGID:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

Capabilities:

```bash
getcap -r / 2>/dev/null
```

Writable application files:

```bash
find /opt /srv /usr/local /var/www -type f -writable -ls 2>/dev/null
```

---

# 187. Enumeration Decision Tree

```text
Start
  |
  v
Who Am I?
  |
  v
What OS / Kernel?
  |
  v
What Groups?
  |
  v
sudo -l
  |
  v
What Is Listening?
  |
  v
What Is Running?
  |
  v
Which Services Are Privileged?
  |
  v
What Executes Periodically?
  |
  v
What Can I Write?
  |
  v
SUID / SGID?
  |
  v
Capabilities?
  |
  v
Credentials?
  |
  v
Containers?
  |
  v
Interesting Candidate
  |
  v
Who Owns It?
  |
  v
Who Can Modify It?
  |
  v
Who Consumes It?
  |
  v
Does It Cross a Privilege Boundary?
  |
  +---- No ----> Continue Enumeration
  |
  +---- Yes
          |
          v
    Minimal Validation
          |
          v
       Evidence
          |
          v
        Finding
```

---

# 188. Enumeration vs Exploitation

Keep these phases separate.

```text
Enumeration
     |
     v
Identify Relationship
```

```text
Validation
     |
     v
Confirm Security Impact
```

```text
Exploitation
     |
     v
Exercise the Security Weakness
```

A security assessment often does not require full exploitation when the relationship and impact can already be demonstrated safely.

---

# 189. Manual Validation Model

For every automated finding:

```text
Tool Output
    |
    v
Reproduce With Native Command
    |
    v
Verify Permissions
    |
    v
Verify Current Identity
    |
    v
Identify Privileged Consumer
    |
    v
Confirm Relationship
    |
    v
Determine Impact
```

This greatly reduces false positives.

---

# 190. Final Testing Model

Use this model for Linux enumeration:

```text
Establish Identity
      |
      v
Understand Host
      |
      v
Enumerate Users and Groups
      |
      v
Review Sudo
      |
      v
Map Network
      |
      v
Identify Processes
      |
      v
Identify Services
      |
      v
Identify Scheduled Execution
      |
      v
Review Filesystem Permissions
      |
      v
Enumerate SUID / SGID
      |
      v
Enumerate Capabilities
      |
      v
Review Credentials
      |
      v
Review Containers
      |
      v
Review Security Controls
      |
      v
Run Automated Enumeration
      |
      v
Correlate Candidates
      |
      v
Manually Validate
      |
      v
Establish Privileged Relationship
      |
      v
Collect Evidence
      |
      v
Report Root Cause
```

The objective is not to generate the largest possible amount of enumeration output.

The objective is to understand the Linux host well enough to identify security boundaries that can be crossed because of insecure permissions, configuration, credentials, software, or delegated privilege.

---

# Related Notes

- [Linux](index.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)
- [Active Directory](../active-directory/index.md)
- [Windows Enumeration](../windows/enumeration.md)

---

# References

- [Linux Kernel Documentation](https://docs.kernel.org/){ target="_blank" rel="noopener noreferrer" }
- [proc(5) - Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html){ target="_blank" rel="noopener noreferrer" }
- [capabilities(7) - Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [systemd](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [SELinux Project](https://selinuxproject.org/){ target="_blank" rel="noopener noreferrer" }
- [AppArmor](https://apparmor.net/){ target="_blank" rel="noopener noreferrer" }
- [Docker Engine Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }
- [Ubuntu Security](https://ubuntu.com/security){ target="_blank" rel="noopener noreferrer" }
- [Debian Security Information](https://www.debian.org/security/){ target="_blank" rel="noopener noreferrer" }
- [Red Hat Product Security](https://access.redhat.com/security/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }
- [Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }
- [pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Linux](https://attack.mitre.org/matrices/enterprise/linux/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Owner/User Discovery](https://attack.mitre.org/techniques/T1033/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Information Discovery](https://attack.mitre.org/techniques/T1082/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Process Discovery](https://attack.mitre.org/techniques/T1057/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Permission Groups Discovery](https://attack.mitre.org/techniques/T1069/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - File and Directory Discovery](https://attack.mitre.org/techniques/T1083/){ target="_blank" rel="noopener noreferrer" }

---

> Use these enumeration techniques only on Linux systems you own or have explicit permission to assess. Prefer low-noise native enumeration and targeted searches. Avoid unnecessary access to credentials, unrelated user data, production configuration, or privileged resources when metadata and permission evidence are sufficient.
