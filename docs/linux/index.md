# Linux

Linux is widely used across servers, cloud infrastructure, containers, appliances, development environments, security platforms, and enterprise systems.

A Linux security assessment should not focus only on finding a single privilege escalation technique. The objective is to understand the host, its users, services, permissions, credentials, security controls, and trust relationships before determining whether those relationships can be abused.

A structured Linux assessment typically examines:

- Operating system and kernel
- Current user and groups
- Sudo configuration
- SUID and SGID binaries
- Linux capabilities
- Filesystem permissions
- Services and processes
- Scheduled jobs
- Credentials and secrets
- Network configuration
- Installed software
- Containers and virtualisation
- Security controls
- Logging and monitoring
- Privilege escalation paths

This section provides the foundation for Linux host assessment.

---

# 1. Linux Assessment Model

A practical workflow is:

```text
Linux Host
    |
    v
Current Context
    |
    +---- User
    +---- UID / GID
    +---- Groups
    +---- Shell
    +---- Environment
    |
    v
System Information
    |
    +---- Distribution
    +---- Kernel
    +---- Architecture
    +---- Hostname
    |
    v
Network
    |
    +---- Interfaces
    +---- Routes
    +---- DNS
    +---- Connections
    +---- Listeners
    |
    v
Processes and Services
    |
    +---- Running Processes
    +---- systemd
    +---- Init Scripts
    +---- Application Services
    |
    v
Filesystem
    |
    +---- Permissions
    +---- Mounts
    +---- Writable Locations
    +---- SUID / SGID
    +---- Capabilities
    |
    v
Credentials
    |
    +---- Configuration
    +---- Shell History
    +---- SSH
    +---- Environment
    +---- Application Secrets
    |
    v
Scheduled Execution
    |
    +---- cron
    +---- systemd Timers
    +---- at
    |
    v
Security Controls
    |
    +---- SELinux
    +---- AppArmor
    +---- Firewall
    +---- Audit
    +---- Endpoint Security
    |
    v
Privilege Escalation Analysis
```

---

# 2. Initial Context

Start by determining who you are.

```bash
whoami
```

User identity:

```bash
id
```

Example:

```text
uid=1000 user=analyst gid=1000 user groups=1000(user),27(sudo)
```

Important information includes:

```text
UID
Primary GID
Supplementary groups
Username
```

---

# 3. User ID

Display the current UID:

```bash
id -u
```

Username:

```bash
id -un
```

Group IDs:

```bash
id -G
```

Group names:

```bash
id -Gn
```

The root account normally has:

```text
UID 0
```

Do not assume that a username must literally be `root` to have UID 0.

---

# 4. Current Groups

```bash
groups
```

or:

```bash
id
```

Groups can significantly affect access.

Security-relevant examples may include:

```text
sudo
wheel
docker
lxd
disk
adm
shadow
systemd-journal
libvirt
```

Membership does not automatically mean a vulnerability exists.

Determine what access the group actually grants.

---

# 5. Current Shell

```bash
echo "$SHELL"
```

Current process shell:

```bash
ps -p $$ -o pid,ppid,user,comm,args
```

Available shells:

```bash
cat /etc/shells
```

Shell configuration can affect:

```text
Environment variables
PATH
Aliases
Startup scripts
Command history
Application behaviour
```

---

# 6. Environment Variables

```bash
env
```

or:

```bash
printenv
```

Sorted:

```bash
printenv | sort
```

Interesting variables can include:

```text
PATH
HOME
USER
LOGNAME
SHELL
PWD
SSH_CONNECTION
SSH_CLIENT
SSH_TTY
SUDO_USER
SUDO_COMMAND
SUDO_UID
SUDO_GID
```

Environment variables can also contain application secrets.

Avoid displaying or collecting sensitive values unnecessarily.

---

# 7. Hostname

```bash
hostname
```

Detailed where supported:

```bash
hostnamectl
```

Fully qualified hostname:

```bash
hostname -f
```

The hostname can reveal:

```text
Host role
Environment
Naming conventions
Domain
Application purpose
```

Do not rely solely on hostname naming conventions to determine the host's actual role.

---

# 8. Operating System

A common source of distribution information is:

```bash
cat /etc/os-release
```

Example:

```text
NAME="Ubuntu"
VERSION="24.04 LTS"
ID=ubuntu
```

Additional information:

```bash
uname -a
```

Distribution utilities may also exist:

```bash
lsb_release -a
```

Do not assume `lsb_release` is installed.

---

# 9. Kernel

```bash
uname -r
```

Full kernel information:

```bash
uname -a
```

Architecture:

```bash
uname -m
```

Example architectures:

```text
x86_64
aarch64
armv7l
```

Kernel version information can support vulnerability research, but version strings alone are not sufficient proof of vulnerability because distributions frequently backport security fixes.

---

# 10. Kernel Vulnerability Validation

Avoid:

```text
Kernel version looks old
        |
        v
Vulnerable
```

Prefer:

```text
Kernel Version
      |
      v
Distribution
      |
      v
Package Version
      |
      v
Vendor Security Advisory
      |
      v
Patch / Backport Status
      |
      v
Configuration / Preconditions
      |
      v
Affected?
```

Always verify against the distribution vendor's security information.

---

# 11. System Uptime

```bash
uptime
```

Boot time:

```bash
who -b
```

Where available:

```bash
uptime -s
```

Uptime can provide context around:

```text
Patch deployment
Recent reboots
Service restarts
Kernel updates
```

---

# 12. System Time

```bash
date
```

Timezone information where systemd is present:

```bash
timedatectl
```

Accurate system time matters when correlating:

```text
Logs
Authentication
Network captures
SIEM alerts
Incident timelines
```

---

# 13. Logged-In Users

```bash
who
```

More context:

```bash
w
```

Recent login information:

```bash
last
```

Current login:

```bash
who am i
```

Respect privacy and engagement scope when reviewing login history.

---

# 14. Local Users

User accounts are described in:

```text
/etc/passwd
```

View:

```bash
cat /etc/passwd
```

Username only:

```bash
cut -d: -f1 /etc/passwd
```

Structured:

```bash
awk -F: '{print $1, $3, $4, $6, $7}' /etc/passwd
```

Fields include:

```text
Username
UID
GID
Comment
Home directory
Login shell
```

---

# 15. Human Users

A quick candidate search:

```bash
awk -F: '$3 >= 1000 {print $1, $3, $6, $7}' /etc/passwd
```

UID allocation differs between distributions.

Do not treat `UID >= 1000` as a universal definition of a human user.

---

# 16. UID 0 Accounts

Search:

```bash
awk -F: '$3 == 0 {print $1}' /etc/passwd
```

Normally:

```text
root
```

Additional UID 0 accounts deserve investigation because UID 0 provides root-equivalent privileges.

---

# 17. Groups

Group information:

```bash
cat /etc/group
```

Group names:

```bash
cut -d: -f1 /etc/group
```

Current user:

```bash
id
```

Specific user:

```bash
id username
```

---

# 18. Sudo

Check permitted sudo commands:

```bash
sudo -l
```

This is one of the most important Linux privilege enumeration commands.

Possible results may include:

```text
Full sudo access
Specific binaries
Specific scripts
NOPASSWD rules
Environment restrictions
Run-as restrictions
```

Example:

```text
User analyst may run the following commands:
    (root) /usr/bin/systemctl restart example.service
```

Do not assume every sudo entry is exploitable.

Analyse the delegated command and its dependencies.

---

# 19. Sudo Configuration

Primary configuration:

```text
/etc/sudoers
```

Additional configuration commonly exists beneath:

```text
/etc/sudoers.d/
```

Where permissions allow:

```bash
ls -la /etc/sudoers.d/
```

The preferred administrative tool for editing sudo policy is:

```bash
visudo
```

Do not modify sudo configuration during routine enumeration.

---

# 20. Sudo Security Model

```text
User
  |
  v
sudo Rule
  |
  v
Allowed Command
  |
  +---- Arguments
  +---- Environment
  +---- File Inputs
  +---- Plugins
  +---- Scripts
  +---- Editors
  +---- Child Processes
  |
  v
Can User Influence Privileged Execution?
```

The existence of sudo delegation is not itself a vulnerability.

The issue is unsafe delegation.

---

# 21. Sudo Environment

Where permitted:

```bash
sudo -V
```

Review sudo policy carefully for environment-related behaviour.

Potentially relevant concepts include:

```text
env_reset
secure_path
env_keep
SETENV
```

Do not assume environment manipulation is possible without validating the effective sudo policy.

---

# 22. PATH

Display:

```bash
echo "$PATH"
```

Readable format:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

A PATH risk can occur when:

```text
Privileged Process
      |
      v
Executes Command Without Absolute Path
      |
      v
Searches PATH
      |
      v
User-Writable Directory Appears First
```

All conditions must be validated.

---

# 23. PATH Directory Permissions

Inspect each PATH component:

```bash
printf '%s\n' "$PATH" | tr ':' '\n' | while read -r dir; do
    [ -n "$dir" ] && ls -ld "$dir"
done
```

Check whether any component is writable by the assessed user.

A writable PATH directory is not automatically exploitable.

A privileged process must actually rely on it.

---

# 24. Processes

Enumerate:

```bash
ps aux
```

Alternative:

```bash
ps -ef
```

Useful process tree:

```bash
ps -ef --forest
```

Where available:

```bash
pstree -ap
```

Processes can reveal:

```text
Applications
Service accounts
Command-line arguments
Custom scripts
Security software
Container runtimes
Databases
Web servers
```

---

# 25. Process Command Lines

```bash
ps -eo user,pid,ppid,comm,args
```

Search carefully for interesting applications:

```bash
ps -eo user,pid,ppid,comm,args | grep -Ei 'python|java|node|nginx|apache|mysql|postgres|docker'
```

Do not assume a process command line is visible to all users on every Linux configuration.

---

# 26. Process Credentials

For a specific process:

```bash
ps -o user,group,euser,egroup,pid,ppid,comm,args -p PID
```

Replace `PID` with the actual process identifier.

The effective user is particularly important when analysing privileged applications.

---

# 27. systemd Services

On systemd systems:

```bash
systemctl list-units --type=service
```

Running services:

```bash
systemctl list-units --type=service --state=running
```

Installed service unit files:

```bash
systemctl list-unit-files --type=service
```

Specific service:

```bash
systemctl status example.service
```

---

# 28. Service Configuration

Display the effective unit:

```bash
systemctl cat example.service
```

Properties:

```bash
systemctl show example.service
```

Security-relevant directives can include:

```text
User
Group
ExecStart
ExecStartPre
ExecStartPost
Environment
EnvironmentFile
WorkingDirectory
RootDirectory
CapabilityBoundingSet
AmbientCapabilities
NoNewPrivileges
ProtectSystem
ProtectHome
PrivateTmp
```

Detailed service analysis belongs in [Linux Services](services.md).

---

# 29. Service Files

Common systemd locations include:

```text
/etc/systemd/system/
/run/systemd/system/
/usr/lib/systemd/system/
/lib/systemd/system/
```

Exact locations vary by distribution.

List:

```bash
find /etc/systemd/system -maxdepth 2 -type f -ls 2>/dev/null
```

Do not modify service units during enumeration.

---

# 30. Service Permissions

Inspect a unit:

```bash
ls -l /etc/systemd/system/example.service
```

Parent directory:

```bash
ls -ld /etc/systemd/system
```

Executable:

```bash
systemctl show example.service -p ExecStart
```

Then inspect the relevant executable or script.

A strong service finding usually requires:

```text
Privileged Service
      +
User-Controlled Resource
      +
Execution Relationship
```

---

# 31. Network Interfaces

Modern:

```bash
ip addr
```

Short:

```bash
ip -br addr
```

Legacy systems may have:

```bash
ifconfig
```

Do not assume `ifconfig` is installed.

---

# 32. Routes

```bash
ip route
```

IPv6:

```bash
ip -6 route
```

Routes can reveal:

```text
Default gateway
Internal networks
VPN networks
Container networks
Management networks
```

---

# 33. ARP and Neighbour Cache

```bash
ip neigh
```

Legacy:

```bash
arp -a
```

`ip neigh` is generally preferred on modern Linux systems.

---

# 34. DNS

Common resolver configuration:

```bash
cat /etc/resolv.conf
```

On systems using systemd-resolved:

```bash
resolvectl status
```

DNS configuration can reveal:

```text
Internal DNS servers
Search domains
Corporate domains
VPN configuration
```

---

# 35. Listening Ports

Preferred:

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

Depending on permissions, process information may be incomplete.

Legacy systems may use:

```bash
netstat -lntup
```

---

# 36. Established Connections

```bash
ss -antp
```

All sockets:

```bash
ss -a
```

Network connections can reveal:

```text
Databases
Internal services
Management interfaces
C2-like unexpected traffic
Application dependencies
Container communication
```

Interpret findings within the authorised assessment scope.

---

# 37. Firewall

Linux hosts may use several firewall frameworks.

Common examples:

```text
nftables
iptables
ufw
firewalld
```

nftables:

```bash
sudo nft list ruleset
```

iptables:

```bash
sudo iptables -L -n -v
```

UFW:

```bash
sudo ufw status verbose
```

firewalld:

```bash
firewall-cmd --list-all
```

Access may require elevated privileges.

Do not modify firewall rules during routine enumeration.

---

# 38. Open Ports vs Firewall

Keep these concepts separate.

```text
Listening Socket
      |
      v
Application Is Listening
```

does not automatically mean:

```text
Remote Network Can Reach It
```

Consider:

```text
Bind address
Host firewall
Network firewall
Routing
Security groups
Container networking
```

---

# 39. Mounted Filesystems

```bash
mount
```

More structured:

```bash
findmnt
```

Block devices:

```bash
lsblk
```

Filesystem information:

```bash
df -hT
```

Mounts can reveal:

```text
Network shares
External disks
Container mounts
Sensitive data volumes
Backup storage
Temporary filesystems
```

---

# 40. Mount Options

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

Security-relevant options can include:

```text
nosuid
nodev
noexec
ro
rw
```

Interpret mount options in context.

For example:

```text
noexec
```

does not prevent every possible form of code interpretation, but it changes normal executable behaviour on that filesystem.

---

# 41. Network Filesystems

Search:

```bash
findmnt -t nfs,nfs4,cifs
```

Potentially relevant files:

```text
/etc/fstab
/etc/auto.master
/etc/auto.*
```

Review:

```bash
cat /etc/fstab
```

Do not assume credentials are present simply because a network mount exists.

---

# 42. File Permissions

Linux permissions are central to host security.

Inspect:

```bash
ls -l file
```

Directory:

```bash
ls -ld directory
```

Numeric permissions:

```bash
stat -c '%A %a %U %G %n' file
```

Example:

```text
-rwxr-x--- 750 root administrators application
```

---

# 43. Permission Model

Traditional Unix permissions apply to:

```text
Owner
Group
Other
```

Rights:

```text
r = read
w = write
x = execute
```

Example:

```text
-rwxr-xr--
```

means:

```text
Owner: read, write, execute
Group: read, execute
Other: read
```

---

# 44. Directory Permissions

Directory permissions have different implications.

For directories:

```text
Read    -> list names
Write   -> create/delete entries
Execute -> traverse/access entries
```

Security analysis must consider combinations of these permissions.

---

# 45. ACLs

Linux can also use POSIX ACLs.

Inspect:

```bash
getfacl file
```

Directory:

```bash
getfacl directory
```

ACLs can grant permissions beyond what appears in the basic owner/group/other bits.

Do not rely only on `ls -l` when ACLs are present.

---

# 46. Writable Directories

Targeted writable directory search:

```bash
find /opt /srv /usr/local /var -type d -writable 2>/dev/null
```

Avoid immediately searching the entire filesystem.

Writable directories become interesting when privileged processes consume resources from them.

---

# 47. Writable Files

Target likely application locations:

```bash
find /opt /srv /usr/local /etc -type f -writable 2>/dev/null
```

A writable file is not automatically a vulnerability.

Determine:

```text
Who consumes it?
Under which identity?
When?
Can it affect execution?
```

---

# 48. SUID

SUID allows an executable to run with the effective UID of the file owner.

Search common local filesystems:

```bash
find / -xdev -perm -4000 -type f 2>/dev/null
```

Typical legitimate examples vary by distribution.

The existence of SUID binaries is normal.

Focus on:

```text
Custom SUID binaries
Unexpected locations
Unusual owners
Weak permissions
Known unsafe behaviour
```

---

# 49. SGID

Search:

```bash
find / -xdev -perm -2000 -type f 2>/dev/null
```

SGID can cause a program to run with the effective group ID of the file's group.

As with SUID, existence alone is not a vulnerability.

---

# 50. SUID and SGID Inventory

Combined:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

Use `-xdev` to avoid crossing into other mounted filesystems during the initial search.

Assess additional filesystems separately if relevant.

---

# 51. Linux Capabilities

Linux capabilities divide traditional root privileges into smaller units.

Enumerate file capabilities:

```bash
getcap -r / 2>/dev/null
```

Potentially security-relevant capabilities include:

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

Context determines actual risk.

---

# 52. Capability Model

Instead of:

```text
root / not root
```

Linux can delegate individual capabilities:

```text
Process
   |
   +---- CAP_NET_RAW
   +---- CAP_SETUID
   +---- CAP_SYS_ADMIN
   +---- ...
```

Some capabilities provide extensive control.

`CAP_SYS_ADMIN` in particular covers a broad set of privileged operations.

---

# 53. Process Capabilities

For the current shell:

```bash
grep '^Cap' /proc/$$/status
```

If `capsh` is installed:

```bash
capsh --print
```

Container environments often make capability analysis particularly important.

---

# 54. cron

System cron configuration can exist in:

```text
/etc/crontab
/etc/cron.d/
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/
```

Inspect:

```bash
cat /etc/crontab
```

List:

```bash
ls -la /etc/cron.d/
```

User cron:

```bash
crontab -l
```

---

# 55. Cron Security Model

```text
Privileged Cron Job
      |
      v
Command / Script
      |
      v
File Permissions
      |
      v
Directory Permissions
      |
      v
Dependencies / PATH
      |
      v
Can Lower-Privileged User Influence Execution?
```

Do not report a root cron job simply because it exists.

---

# 56. systemd Timers

Enumerate:

```bash
systemctl list-timers --all
```

Timers can provide scheduled execution similar to cron.

Determine:

```text
Timer
  |
  v
Associated Service
  |
  v
ExecStart
  |
  v
Executable / Script
  |
  v
Permissions
```

---

# 57. at Jobs

Where available:

```bash
atq
```

Access depends on configuration and user permissions.

Do not assume the `at` package is installed.

---

# 58. Installed Packages

Debian-based:

```bash
dpkg -l
```

Package query:

```bash
dpkg -l | grep -i package
```

APT:

```bash
apt list --installed 2>/dev/null
```

RPM-based:

```bash
rpm -qa
```

DNF:

```bash
dnf list installed
```

Package managers vary by distribution.

---

# 59. Package Vulnerability Analysis

Avoid:

```text
Package Version
      |
      v
Internet CVE Search
      |
      v
Vulnerable
```

Prefer:

```text
Package
   |
   v
Distribution
   |
   v
Exact Package Build
   |
   v
Vendor Advisory
   |
   v
Backported Fix?
   |
   v
Configuration
   |
   v
Reachability
   |
   v
Practical Impact
```

Distribution security trackers are important because Linux vendors frequently backport patches without changing to the upstream version expected by generic scanners.

---

# 60. Debian and Ubuntu Package Information

Package details:

```bash
apt-cache policy package-name
```

Installed version:

```bash
dpkg-query -W -f='${Package} ${Version}\n' package-name
```

Replace `package-name` with the actual package.

---

# 61. RPM Package Information

```bash
rpm -qi package-name
```

Exact version:

```bash
rpm -q package-name
```

Replace `package-name` with the relevant package.

---

# 62. Configuration Files

Important configuration commonly exists beneath:

```text
/etc
/opt
/srv
/usr/local
/var/lib
/var/www
```

Target the applications actually present on the host.

Avoid recursively reading every configuration file without a clear reason.

---

# 63. Interesting Configuration Types

Examples:

```text
*.conf
*.config
*.ini
*.yaml
*.yml
*.json
*.xml
*.properties
.env
```

Targeted search:

```bash
find /opt /srv /var/www -type f \( \
    -name '*.conf' -o \
    -name '*.ini' -o \
    -name '*.yaml' -o \
    -name '*.yml' -o \
    -name '*.json' -o \
    -name '*.properties' -o \
    -name '.env' \
\) 2>/dev/null
```

---

# 64. Credential Search

Search a specific application directory:

```bash
grep -RniE 'password|passwd|secret|token|api[_-]?key' /opt/application 2>/dev/null
```

This produces candidates only.

Review matches manually.

Do not perform broad secret searches across unrelated user data without a clear assessment requirement.

---

# 65. Shell History

Bash history commonly uses:

```text
~/.bash_history
```

Read where appropriate:

```bash
cat ~/.bash_history
```

Search:

```bash
grep -Ei 'password|passwd|secret|token|key|ssh|mysql|psql' ~/.bash_history 2>/dev/null
```

Other shells use different history mechanisms.

---

# 66. History Files

Potential examples:

```text
~/.bash_history
~/.zsh_history
~/.python_history
~/.mysql_history
~/.psql_history
~/.sqlite_history
```

Search current home directory:

```bash
find "$HOME" -maxdepth 2 -type f -name '*history*' -ls 2>/dev/null
```

History files may contain sensitive commands or data.

---

# 67. SSH

User SSH configuration:

```bash
ls -la ~/.ssh
```

Potential files:

```text
authorized_keys
config
known_hosts
id_rsa
id_ed25519
Other private keys
```

System SSH configuration:

```text
/etc/ssh/sshd_config
```

and potentially:

```text
/etc/ssh/sshd_config.d/
```

---

# 68. SSH Private Keys

Find private-key candidates in the current user's SSH directory:

```bash
find ~/.ssh -maxdepth 1 -type f -ls 2>/dev/null
```

Inspect permissions:

```bash
stat ~/.ssh/id_ed25519 2>/dev/null
```

A private key is sensitive authentication material.

Do not copy private keys unless required and authorised.

---

# 69. SSH Server Configuration

Effective configuration can often be queried with:

```bash
sshd -T
```

Depending on the system, elevated privileges or additional context may be required.

Interesting settings include:

```text
permitrootlogin
passwordauthentication
pubkeyauthentication
allowusers
allowgroups
maxauthtries
```

Do not modify SSH configuration during enumeration.

---

# 70. Root Home

The root home directory is commonly:

```text
/root
```

A standard user should normally not be able to browse sensitive root files.

Unexpected access should be investigated.

Do not treat an inaccessible `/root` directory as a testing problem - that is expected security behaviour.

---

# 71. `/etc/shadow`

Password hash information is normally stored in:

```text
/etc/shadow
```

Permissions should restrict access.

Check metadata:

```bash
ls -l /etc/shadow
```

Do not attempt to read or copy password hashes unless credential-access testing is explicitly authorised and necessary.

Detailed credential analysis belongs in [Linux Credentials](credentials.md).

---

# 72. Home Directories

List:

```bash
ls -la /home
```

Permissions:

```bash
find /home -maxdepth 1 -mindepth 1 -type d -exec ls -ld {} \; 2>/dev/null
```

Assess whether users can access unrelated users' sensitive files.

World-readable home directories are not automatically a vulnerability, but sensitive content should not be exposed.

---

# 73. `/tmp`

Inspect:

```bash
ls -ld /tmp
```

Typical permissions include the sticky bit:

```text
drwxrwxrwt
```

The sticky bit limits deletion or renaming of files belonging to other users.

Writable temporary directories are normal.

The security question is whether privileged applications insecurely trust files placed there.

---

# 74. Sticky Bit

Example:

```text
drwxrwxrwt
         ^
         sticky bit
```

Check numeric and symbolic permissions:

```bash
stat -c '%A %a %n' /tmp
```

A missing sticky bit on a shared world-writable directory may warrant investigation.

---

# 75. `/opt`

Third-party applications are frequently installed beneath:

```text
/opt
```

Enumerate:

```bash
ls -la /opt
```

Permissions:

```bash
find /opt -maxdepth 3 -type d -writable 2>/dev/null
```

Custom application deployments are often valuable enumeration targets.

---

# 76. `/usr/local`

Locally installed applications often use:

```text
/usr/local/bin
/usr/local/sbin
/usr/local/lib
```

Inspect:

```bash
ls -la /usr/local/bin /usr/local/sbin 2>/dev/null
```

Writable executable directories used by privileged processes deserve investigation.

---

# 77. `/var/www`

Web applications commonly use:

```text
/var/www
```

Enumerate:

```bash
find /var/www -maxdepth 3 -type f -ls 2>/dev/null
```

Potential sensitive information includes:

```text
Application configuration
Database credentials
API keys
Environment files
Deployment scripts
Source code
```

Remain within application scope.

---

# 78. Logs

Common logs exist beneath:

```text
/var/log
```

List:

```bash
ls -lah /var/log
```

systemd journal:

```bash
journalctl
```

Recent:

```bash
journalctl -n 100
```

User permissions may restrict log access.

---

# 79. Authentication Logs

Depending on distribution:

```text
/var/log/auth.log
/var/log/secure
```

Examples:

```bash
grep -i 'sudo' /var/log/auth.log 2>/dev/null
```

or:

```bash
grep -i 'sudo' /var/log/secure 2>/dev/null
```

Do not assume the same log location across all distributions.

---

# 80. Journal

Service logs:

```bash
journalctl -u ssh
```

or distribution-specific service name:

```bash
journalctl -u sshd
```

Current boot:

```bash
journalctl -b
```

Errors:

```bash
journalctl -p err
```

Log access may be restricted.

---

# 81. SELinux

Check:

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

SELinux being enabled is not a vulnerability.

Likewise, SELinux being disabled should be interpreted according to the host's security requirements and compensating controls.

---

# 82. AppArmor

Status:

```bash
aa-status
```

or:

```bash
sudo aa-status
```

Where AppArmor is installed, profiles may operate in:

```text
Enforce
Complain
```

Do not assume `aa-status` exists on every distribution.

---

# 83. Security Modules

Check active Linux Security Modules where exposed:

```bash
cat /sys/kernel/security/lsm 2>/dev/null
```

Possible entries may include:

```text
apparmor
selinux
landlock
lockdown
yama
```

Availability depends on kernel configuration and distribution.

---

# 84. Yama ptrace Scope

Where available:

```bash
cat /proc/sys/kernel/yama/ptrace_scope 2>/dev/null
```

Yama can restrict process tracing behaviour.

Interpret the value according to kernel documentation and the system's security requirements.

---

# 85. Kernel Hardening Parameters

Selected parameters:

```bash
sysctl kernel.randomize_va_space
```

```bash
sysctl kernel.kptr_restrict
```

```bash
sysctl kernel.dmesg_restrict
```

```bash
sysctl fs.protected_symlinks
```

```bash
sysctl fs.protected_hardlinks
```

Do not classify individual sysctl values without considering distribution defaults, workload requirements, and threat model.

---

# 86. ASLR

Check:

```bash
sysctl kernel.randomize_va_space
```

ASLR is one layer of exploit mitigation.

Its configuration should not be interpreted as a complete measure of host security.

---

# 87. Kernel Messages

Where permitted:

```bash
dmesg
```

Some systems restrict unprivileged access.

Check:

```bash
sysctl kernel.dmesg_restrict
```

Restricted kernel logs can reduce information exposure to unprivileged users.

---

# 88. Docker

Check:

```bash
docker --version
```

Current user groups:

```bash
id
```

Docker socket:

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

Docker group membership can provide extensive control over the Docker daemon and should be treated as highly privileged.

---

# 89. Docker Security Model

Typical architecture:

```text
User
  |
  v
Docker CLI
  |
  v
Docker Socket
  |
  v
Docker Daemon
  |
  v
Host Resources
```

If an unprivileged user can fully control a root-owned Docker daemon, the practical security boundary between that user and the host may be weak.

This may be intentional administrative delegation rather than a software vulnerability.

---

# 90. Container Detection

Potential indicators:

```bash
test -f /.dockerenv && echo "Docker environment indicator present"
```

Control groups:

```bash
cat /proc/1/cgroup
```

PID 1:

```bash
ps -p 1 -o pid,comm,args
```

No single detection method works for every container runtime.

---

# 91. Container Capabilities

Where available:

```bash
capsh --print
```

Inspect:

```bash
grep '^Cap' /proc/1/status
```

Important container security questions include:

```text
Is the container privileged?
Which capabilities exist?
Which host paths are mounted?
Is the container runtime socket exposed?
Which user runs the container?
Are namespaces restricted?
```

---

# 92. LXD and LXC

Check group membership:

```bash
id
```

Search:

```bash
getent group lxd
```

or:

```bash
getent group lxc
```

Membership in container-management groups can represent substantial administrative authority.

Interpret it as delegated privilege rather than automatically calling it a vulnerability.

---

# 93. Virtualisation

Potential indicators:

```bash
systemd-detect-virt
```

DMI information where accessible:

```bash
cat /sys/class/dmi/id/product_name 2>/dev/null
```

Virtualisation context can affect:

```text
Host role
Cloud metadata
Device exposure
Security boundaries
Snapshot behaviour
```

---

# 94. Cloud Systems

Linux hosts may run in:

```text
AWS
Azure
Google Cloud
Other cloud platforms
```

Cloud systems introduce additional trust relationships:

```text
Instance identity
Metadata services
Managed identities
Attached roles
Cloud-init
Agent configuration
Secrets
```

Do not query cloud metadata endpoints unless cloud testing is within scope.

---

# 95. Cloud-Init

Where present:

```bash
ls -la /var/lib/cloud 2>/dev/null
```

Configuration:

```bash
ls -la /etc/cloud 2>/dev/null
```

Cloud-init data can contain deployment information.

Treat user data and instance configuration as potentially sensitive.

---

# 96. NFS

NFS configuration:

```bash
cat /etc/exports 2>/dev/null
```

Mounted NFS:

```bash
findmnt -t nfs,nfs4
```

NFS security depends on:

```text
Export options
Network restrictions
UID mapping
Root squashing
Filesystem permissions
Authentication model
```

Do not classify an NFS export based on one option alone.

---

# 97. Samba

Configuration may exist at:

```text
/etc/samba/smb.conf
```

Where accessible:

```bash
testparm -s 2>/dev/null
```

Samba can expose:

```text
Shares
Authentication
Filesystem access
Domain integration
```

Validate both Samba configuration and underlying filesystem permissions.

---

# 98. Databases

Look for running database processes:

```bash
ps aux | grep -Ei 'mysql|mariadb|postgres|mongod|redis' | grep -v grep
```

Listening ports:

```bash
ss -lntp
```

Potential configuration directories include:

```text
/etc/mysql
/etc/postgresql
/etc/redis
```

Only inspect databases and configuration included in scope.

---

# 99. Web Servers

Common examples:

```text
Apache
Nginx
Caddy
Lighttpd
Application-specific servers
```

Processes:

```bash
ps aux | grep -Ei 'apache|httpd|nginx|caddy' | grep -v grep
```

Configuration locations vary.

For example:

```text
/etc/apache2
/etc/httpd
/etc/nginx
```

---

# 100. Web Application Identities

Determine which account runs the service.

```bash
ps -eo user,pid,ppid,comm,args | grep -Ei 'apache|httpd|nginx'
```

Common accounts may include:

```text
www-data
apache
nginx
```

Names vary by distribution.

Filesystem access should be analysed relative to the actual service identity.

---

# 101. Application Directories

Useful targets include:

```text
/opt
/srv
/var/www
/usr/local
/home
```

Look for:

```text
Custom binaries
Scripts
Configuration
Credentials
Backups
Logs
Repositories
Service files
```

Prioritise custom applications because they often define organisation-specific trust relationships.

---

# 102. Git Repositories

Targeted search:

```bash
find /opt /srv /var/www /home -type d -name .git 2>/dev/null
```

Repositories may expose:

```text
Source code
Configuration history
Deleted secrets
Deployment scripts
Internal endpoints
```

Source-code review must remain within scope.

---

# 103. Backup Files

Potential patterns:

```text
*.bak
*.backup
*.old
*.orig
*.save
*.swp
```

Targeted search:

```bash
find /opt /srv /var/www /etc -type f \( \
    -name '*.bak' -o \
    -name '*.backup' -o \
    -name '*.old' -o \
    -name '*.orig' \
\) 2>/dev/null
```

Backups can expose older secrets or insecure configurations.

---

# 104. World-Writable Files

Target common system and application locations:

```bash
find /etc /opt /srv /usr/local /var -xdev -type f -perm -0002 -ls 2>/dev/null
```

A world-writable file is particularly interesting when consumed by a privileged process.

---

# 105. World-Writable Directories

```bash
find /etc /opt /srv /usr/local /var -xdev -type d -perm -0002 -ls 2>/dev/null
```

Many legitimate shared directories may be writable.

Review:

```text
Sticky bit
Ownership
Purpose
Privileged consumers
```

---

# 106. Root-Owned Writable Files

A useful candidate search:

```bash
find /etc /opt /srv /usr/local /var -xdev -user root -type f -writable -ls 2>/dev/null
```

If a non-root user can modify a root-owned file, determine why.

Ownership alone does not determine effective permissions.

---

# 107. Root-Owned Writable Directories

```bash
find /etc /opt /srv /usr/local /var -xdev -user root -type d -writable -ls 2>/dev/null
```

High-value cases are directories used by privileged services, scheduled jobs, or administrative scripts.

---

# 108. Writable Scripts

Search:

```bash
find /opt /srv /usr/local /var -xdev -type f \( \
    -name '*.sh' -o \
    -name '*.py' -o \
    -name '*.pl' \
\) -writable -ls 2>/dev/null
```

Then determine whether a privileged process executes the script.

---

# 109. Shell Scripts Run by Root

Search service and scheduling configuration rather than guessing.

Useful sources:

```text
systemd units
cron
sudo rules
init scripts
administrative automation
```

The important relationship is:

```text
Root Execution
      |
      v
Script
      |
      v
User Can Modify Script?
```

---

# 110. Legacy Init Scripts

Some systems may still use:

```text
/etc/init.d/
```

List:

```bash
ls -la /etc/init.d/ 2>/dev/null
```

Inspect only relevant custom services.

---

# 111. Startup Files

Potential system-wide shell startup files include:

```text
/etc/profile
/etc/profile.d/
/etc/bash.bashrc
```

User-specific examples:

```text
~/.profile
~/.bashrc
~/.bash_profile
~/.zshrc
```

Exact files depend on shell and distribution.

---

# 112. Startup File Permissions

Example:

```bash
ls -l /etc/profile
```

```bash
find /etc/profile.d -maxdepth 1 -type f -ls 2>/dev/null
```

Unexpected user write access to system-wide startup scripts should be investigated.

---

# 113. Dynamic Linker Configuration

Important configuration can include:

```text
/etc/ld.so.conf
/etc/ld.so.conf.d/
```

Display:

```bash
cat /etc/ld.so.conf 2>/dev/null
```

```bash
find /etc/ld.so.conf.d -maxdepth 1 -type f -exec sh -c 'echo "### $1"; cat "$1"' _ {} \; 2>/dev/null
```

Dynamic linker configuration is security-sensitive because it influences library resolution.

---

# 114. `ldconfig`

Display linker cache:

```bash
ldconfig -p 2>/dev/null
```

Do not modify linker configuration or cache during enumeration.

---

# 115. Library Paths

Current environment:

```bash
echo "$LD_LIBRARY_PATH"
```

Environment-based library search behaviour may be security-relevant in specific execution contexts.

Privileged executables often apply additional restrictions.

Do not assume a set `LD_LIBRARY_PATH` can influence SUID execution.

---

# 116. `/etc/ld.so.preload`

Check:

```bash
ls -l /etc/ld.so.preload 2>/dev/null
```

If present:

```bash
cat /etc/ld.so.preload 2>/dev/null
```

This file is highly security-sensitive because it can influence dynamic library loading system-wide.

Unexpected write access should be treated seriously.

---

# 117. File Ownership

Inspect:

```bash
stat file
```

Compact:

```bash
stat -c '%U %G %A %a %n' file
```

Security analysis should consider:

```text
Owner
Group
Mode
ACL
Parent directories
Consumer identity
```

---

# 118. Symlinks

Identify:

```bash
find /opt/application -type l -ls 2>/dev/null
```

Resolve:

```bash
readlink -f /path/to/link
```

Symlinks become security-relevant when privileged processes follow attacker-controlled paths or when insecure file handling exists.

The presence of symlinks alone is normal.

---

# 119. Open Files

Where available:

```bash
lsof
```

Network:

```bash
lsof -i
```

Specific process:

```bash
lsof -p PID
```

`lsof` may not be installed and may expose limited information to unprivileged users.

---

# 120. Deleted but Open Files

Where permitted:

```bash
lsof +L1
```

This can identify deleted files still held open by processes.

Potential uses include:

```text
Operational troubleshooting
Unexpected temporary data
Application behaviour
Disk usage investigation
```

Do not assume deleted open files are security findings.

---

# 121. `/proc`

The proc filesystem provides extensive process and kernel information.

Examples:

```text
/proc/cpuinfo
/proc/meminfo
/proc/mounts
/proc/net
/proc/PID/
```

Permissions and mount options can restrict process visibility.

---

# 122. Process Environment

For your own process:

```bash
tr '\0' '\n' < /proc/$$/environ
```

Access to another process's environment depends on identity and system security settings.

Environment data can contain secrets and should be handled carefully.

---

# 123. `/proc` Mount Options

Inspect:

```bash
findmnt /proc
```

Some environments use options such as:

```text
hidepid
```

to reduce cross-user process visibility.

Interpret this as a defensive hardening control rather than an obstacle to bypass during routine enumeration.

---

# 124. Kernel Modules

List:

```bash
lsmod
```

Module information:

```bash
modinfo module_name
```

Kernel module analysis can help understand:

```text
Drivers
Security products
Filesystems
Networking
Virtualisation
```

Do not load or unload kernel modules during routine testing.

---

# 125. Secure Boot

Where supported:

```bash
mokutil --sb-state
```

`mokutil` may not be installed.

Secure Boot contributes to platform integrity but should be interpreted together with boot configuration, kernel policy, and organisational requirements.

---

# 126. Audit Framework

Linux Audit status where available:

```bash
auditctl -s
```

Rules:

```bash
auditctl -l
```

These commands may require elevated privileges.

Service status:

```bash
systemctl status auditd 2>/dev/null
```

---

# 127. Endpoint Security

Look for security and monitoring processes using normal process enumeration.

Examples can include:

```text
EDR agents
Antivirus
SIEM forwarders
Audit agents
File integrity monitoring
Configuration management
```

Do not stop or tamper with defensive tooling during enumeration.

---

# 128. Security Control Mindset

Avoid:

```text
Security Product Present
        |
        v
Host Secure
```

and:

```text
Security Product Absent
        |
        v
Host Vulnerable
```

Instead assess:

```text
Preventive Controls
       +
Permissions
       +
Hardening
       +
Logging
       +
Monitoring
       +
Identity Security
       =
Defence in Depth
```

---

# 129. Automated Enumeration

Automation can accelerate Linux host assessment.

Common tools include:

```text
LinPEAS
LinEnum
linux-smart-enumeration
pspy
```

Automated tools should be treated as coverage aids.

Manual validation remains essential.

---

# 130. LinPEAS

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

LinPEAS can identify candidates involving:

```text
Sudo
SUID
Capabilities
Credentials
Writable files
Cron
Services
Containers
Kernel information
Interesting configuration
```

Do not report every highlighted item.

---

# 131. LinEnum

[LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }

LinEnum provides broad Linux enumeration.

It can help identify:

```text
System information
Users
Sudo configuration
Processes
Networking
Interesting files
SUID / SGID
Cron
```

Some environments may consider the tool noisy.

---

# 132. Linux Smart Enumeration

[linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

Linux Smart Enumeration provides structured Linux privilege escalation enumeration.

Use it to generate investigation candidates rather than conclusions.

---

# 133. pspy

[pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }

pspy can help observe process execution without requiring root in many environments.

This can be useful for discovering:

```text
Cron execution
Administrative scripts
Periodic jobs
Service activity
```

Use only where authorised and operationally appropriate.

---

# 134. Automated Tool Workflow

```text
Manual Baseline
      |
      v
Automated Enumeration
      |
      v
Candidate Findings
      |
      v
Manual Validation
      |
      v
Permission Analysis
      |
      v
Execution Relationship
      |
      v
Practical Impact
      |
      v
Report
```

Automation should increase coverage, not replace reasoning.

---

# 135. Low-Noise Enumeration

A low-noise workflow can begin with:

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
```

Then move into targeted analysis.

This is usually preferable to immediately launching large recursive enumeration scripts.

---

# 136. Privilege Escalation Mindset

Linux privilege escalation usually depends on a trust relationship.

Examples:

```text
sudo
SUID
SGID
Capabilities
Writable service files
Writable scripts
Cron
PATH
Credentials
Containers
Kernel vulnerabilities
Misconfigured mounts
Application weaknesses
```

A useful model:

```text
Current User
      |
      v
Trusted Mechanism
      |
      v
User-Controlled Input
      |
      v
Privileged Execution
      |
      v
Privilege Escalation
```

---

# 137. Sudo Escalation Model

```text
sudo -l
   |
   v
Allowed Binary
   |
   v
Can It:
   |
   +---- Execute commands?
   +---- Load plugins?
   +---- Read/write files?
   +---- Launch editor?
   +---- Invoke shell?
   +---- Execute scripts?
   |
   v
Privilege Boundary?
```

Detailed analysis belongs in [Linux Privilege Escalation](privilege-escalation.md).

---

# 138. SUID Escalation Model

```text
SUID Binary
    |
    v
Owner
    |
    v
Effective UID
    |
    v
Binary Behaviour
    |
    +---- Commands
    +---- Files
    +---- Libraries
    +---- Environment
    +---- Inputs
    |
    v
Can User Influence Privileged Behaviour?
```

Custom SUID applications deserve particular scrutiny.

---

# 139. Capability Escalation Model

```text
Binary
   |
   v
Linux Capability
   |
   v
What Privileged Operation Is Allowed?
   |
   v
Can User Control Binary Behaviour?
   |
   v
Can Capability Cross Security Boundary?
```

Capabilities should be analysed individually.

---

# 140. Cron Escalation Model

```text
Root Cron
   |
   v
Script
   |
   v
User Writable?
   |
   +---- No
   |
   +---- Yes
          |
          v
   Privileged Execution Path
```

Also inspect:

```text
Parent directories
PATH
Referenced configuration
Wildcards
External commands
```

---

# 141. Service Escalation Model

```text
Root Service
    |
    v
Unit Configuration
    |
    v
ExecStart
    |
    v
Executable / Script
    |
    v
Configuration / Environment
    |
    v
User-Controlled Resource?
```

See [Linux Services](services.md).

---

# 142. Credential Escalation Model

```text
Current User
     |
     v
Accessible Secret
     |
     v
Other Account
     |
     v
Higher Privilege?
     |
     v
Authentication Allowed?
     |
     v
Privilege Escalation
```

See [Linux Credentials](credentials.md).

---

# 143. Container Escalation Model

```text
Current User
     |
     v
Container Management Access
     |
     v
Runtime / Socket
     |
     v
Host Resources
     |
     v
Security Boundary
```

Container-management privileges should be treated according to the authority they provide.

---

# 144. Kernel Escalation Model

Kernel vulnerabilities should generally be investigated after configuration and permission-based paths.

```text
Kernel
   |
   v
Exact Distribution Build
   |
   v
Vendor Advisory
   |
   v
Affected?
   |
   v
Required Configuration
   |
   v
Exploit Preconditions
   |
   v
Operational Risk
```

Kernel exploitation can destabilise systems and should only be attempted when explicitly authorised.

---

# 145. Evidence Collection

For Linux findings, collect enough information to reproduce the condition.

Useful fields:

```text
Hostname
Distribution
Kernel
Current user
UID / groups
Affected file
Owner
Group
Permissions
ACL
Affected service
Execution identity
Configuration
Validation performed
Security impact
```

---

# 146. File Permission Evidence

Example:

```bash
stat -c '%A %a %U %G %n' /opt/application/script.sh
```

ACL:

```bash
getfacl /opt/application/script.sh
```

Service:

```bash
systemctl cat application.service
```

This can establish:

```text
Root service
      |
      v
Executes script
      |
      v
Script writable by user
```

without modifying the script.

---

# 147. Controlled Write Test

Where safe and authorised, a temporary file can confirm directory write access.

```bash
dir="/opt/application"
file="$dir/write-test-$$"

if touch "$file" 2>/dev/null; then
    echo "[+] Write access confirmed: $file"
    rm -f "$file"
else
    echo "[-] Write access denied: $dir"
fi
```

This proves write access only.

It does not prove privilege escalation.

---

# 148. Evidence Chain

Strong Linux findings generally establish:

```text
Current Identity
       |
       v
Permission
       |
       v
Privileged Consumer
       |
       v
Execution Relationship
       |
       v
Practical Impact
```

Avoid jumping directly from a permission observation to maximum impact.

---

# 149. Reporting Example - Writable Root Service Script

## Title

```text
Standard User Can Modify a Script Executed by a Root Service
```

## Description

```text
A system service running as root executes a script that can be modified by
the assessed standard user.

Because the script is consumed by a privileged service, unauthorised
modification could allow the lower-privileged user to influence code
executed with root privileges.
```

## Evidence

```text
Current user:
analyst

Service:
application.service

Service user:
root

Script:
/opt/application/start.sh

Permissions:
[record actual permissions]
```

## Impact

```text
A local standard user may be able to cross the local privilege boundary and
obtain root-level code execution when the affected service executes the
modifiable script.
```

## Recommendation

```text
Remove write access for unprivileged users from the affected script and its
parent directories.

Restrict modification rights to trusted administrative or application
deployment identities.
```

---

# 150. Reporting Example - Excessive Sudo Delegation

## Title

```text
Sudo Policy Grants Excessive Privileged Command Execution
```

## Description

```text
The sudo policy permits a standard user to execute a privileged application
whose functionality can influence operations outside the intended
administrative task.

The delegated command therefore provides broader authority than required.
```

## Recommendation

```text
Restrict sudo rules to the minimum commands and arguments required for the
user's operational role.

Avoid delegating general-purpose interpreters, editors, or extensible
applications where their full functionality is not required.
```

---

# 151. Reporting Example - Exposed Credential

## Title

```text
Privileged Application Credential Accessible to Standard Users
```

## Description

```text
An application configuration file readable by standard users contains
authentication material for a more privileged account.

The file permissions expose the credential beyond the identities that
require access to it.
```

## Recommendation

```text
Remove plaintext reusable credentials where possible and use an appropriate
secret-management mechanism.

Restrict access to configuration containing sensitive authentication
material and rotate the exposed credential.
```

---

# 152. Remediation Principles

Linux host hardening should focus on root causes.

Common principles:

```text
Least privilege
Secure file ownership
Restrictive permissions
Safe sudo delegation
Service isolation
Credential protection
Patch management
Application hardening
Container isolation
Security monitoring
Strong authentication
```

---

# 153. Filesystem Remediation

Review:

```text
World-writable files
World-writable directories
Root-owned user-writable files
Service directories
Cron scripts
Application configuration
Private keys
Credential files
```

Do not blindly remove permissions.

Understand application requirements first.

---

# 154. Sudo Remediation

Prefer:

```text
Specific commands
Specific arguments where practical
Restricted environment
Least privilege
Auditable administrative actions
```

Avoid unnecessary delegation of:

```text
Shells
Interpreters
Editors
General-purpose file utilities
Extensible applications
```

when their full functionality is not operationally required.

---

# 155. Service Remediation

For privileged services:

```text
Protect unit files
Protect executables
Protect scripts
Protect configuration
Protect environment files
Use dedicated service users
Apply systemd sandboxing where appropriate
Remove unnecessary capabilities
```

Service hardening must be tested for application compatibility.

---

# 156. Credential Remediation

Prefer:

```text
Secret managers
Short-lived credentials
SSH keys with appropriate protection
Managed service identities where available
Restricted configuration permissions
Credential rotation
Least privilege
```

Avoid:

```text
Plaintext passwords in scripts
Secrets in shell history
Secrets in command-line arguments
Shared administrative passwords
World-readable private keys
```

---

# 157. Container Remediation

Review:

```text
Docker socket access
Privileged containers
Host mounts
Capabilities
Container users
Secrets
Network exposure
Image provenance
Runtime configuration
```

Treat container-management access as administrative authority where it provides equivalent host control.

---

# 158. Logging and Monitoring

Useful telemetry can include:

```text
Authentication
sudo
SSH
Service changes
cron
File modifications
Process execution
Audit events
Container activity
Package changes
Security-control events
```

Centralise security-relevant logs where appropriate.

---

# 159. Linux Host Checklist

## Context

- [ ] Current user
- [ ] UID and GID
- [ ] Groups
- [ ] Shell
- [ ] Environment
- [ ] Hostname
- [ ] Distribution
- [ ] Kernel
- [ ] Architecture
- [ ] Uptime
- [ ] System time

## Users

- [ ] Local users
- [ ] UID 0 accounts
- [ ] Groups
- [ ] Logged-in users
- [ ] Home directory permissions
- [ ] Administrative groups

## Privilege

- [ ] `sudo -l`
- [ ] Sudo configuration
- [ ] SUID binaries
- [ ] SGID binaries
- [ ] File capabilities
- [ ] Process capabilities
- [ ] Writable privileged files
- [ ] Writable privileged directories

## Processes and Services

- [ ] Running processes
- [ ] Process command lines
- [ ] systemd services
- [ ] Custom services
- [ ] Service users
- [ ] Service unit permissions
- [ ] Executable permissions
- [ ] Configuration permissions

## Scheduled Execution

- [ ] User crontab
- [ ] `/etc/crontab`
- [ ] `/etc/cron.d`
- [ ] Periodic cron directories
- [ ] systemd timers
- [ ] `at` jobs where available
- [ ] Writable scheduled scripts

## Network

- [ ] Interfaces
- [ ] Routes
- [ ] DNS
- [ ] Neighbours
- [ ] Listening ports
- [ ] Established connections
- [ ] Firewall
- [ ] Network filesystems

## Filesystem

- [ ] Mounts
- [ ] Mount options
- [ ] Block devices
- [ ] ACLs
- [ ] World-writable files
- [ ] World-writable directories
- [ ] `/opt`
- [ ] `/srv`
- [ ] `/usr/local`
- [ ] `/var/www`
- [ ] Backup files

## Credentials

- [ ] Shell history
- [ ] SSH configuration
- [ ] Private keys
- [ ] Application configuration
- [ ] Environment files
- [ ] Database configuration
- [ ] Backup configuration
- [ ] Sensitive logs
- [ ] `/etc/shadow` permissions

## Security Controls

- [ ] SELinux
- [ ] AppArmor
- [ ] Linux Security Modules
- [ ] Firewall
- [ ] Audit
- [ ] Kernel hardening
- [ ] Endpoint security
- [ ] Secure Boot where relevant

## Containers

- [ ] Docker
- [ ] Docker socket
- [ ] Docker group
- [ ] LXD / LXC
- [ ] Capabilities
- [ ] Host mounts
- [ ] Container identity
- [ ] Cloud context

## Validation

- [ ] Validate permissions manually
- [ ] Identify privileged consumer
- [ ] Establish execution relationship
- [ ] Avoid unnecessary modification
- [ ] Preserve evidence
- [ ] Determine practical impact

---

# 160. Quick Linux Enumeration

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
getcap -r / 2>/dev/null
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

This provides a useful baseline before deeper targeted enumeration.

---

# 161. Manual Enumeration Model

```text
Identity
   |
   v
Operating System
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
Scheduled Jobs
   |
   v
Filesystem
   |
   v
Sudo
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
Security Controls
   |
   v
Containers
   |
   v
Privilege Escalation Analysis
```

---

# 162. What Not to Report Automatically

Do not automatically report:

```text
Root account exists
SUID binaries exist
sudo is installed
cron is enabled
Docker is installed
SELinux is disabled
AppArmor is absent
SSH is running
Private keys exist
systemd services run as root
Kernel version appears old
World-writable /tmp exists
```

Each observation requires security context.

---

# 163. Strong Finding Model

Prefer:

```text
Security Boundary
      |
      v
Privileged Component
      |
      v
User-Controlled Resource
      |
      v
Validated Relationship
      |
      v
Practical Security Impact
```

Example:

```text
Root Service
     |
     v
Executes Script
     |
     v
Script Writable by Standard User
     |
     v
Privilege Boundary Crossed
```

---

# 164. Final Testing Model

A reliable Linux host assessment follows:

```text
1. Establish current identity.

2. Identify distribution, kernel, and architecture.

3. Enumerate users, groups, and administrative delegation.

4. Enumerate network configuration and listeners.

5. Identify running processes and services.

6. Review scheduled execution.

7. Analyse filesystem permissions.

8. Enumerate SUID, SGID, and capabilities.

9. Review credentials and sensitive configuration.

10. Identify container and cloud context.

11. Review host security controls.

12. Run automated enumeration where appropriate.

13. Manually validate interesting candidates.

14. Identify the privileged consumer.

15. Establish the user-controlled resource.

16. Determine whether the trust relationship crosses a security boundary.

17. Validate with the minimum necessary system modification.

18. Preserve reproducible evidence.

19. Determine practical impact.

20. Recommend remediation of the underlying trust failure.
```

The goal is not:

```text
Run enumeration script
       |
       v
Report everything highlighted
```

The preferred model is:

```text
Enumerate
    |
    v
Understand
    |
    v
Correlate
    |
    v
Validate
    |
    v
Demonstrate Impact
    |
    v
Remediate Root Cause
```

---

# Linux Documentation Flow

The Linux section is organised as:

```text
Linux
 |
 +-- Overview
 |
 +-- Enumeration
 |
 +-- Services
 |
 +-- Credentials
 |
 +-- Privilege Escalation
```

Recommended reading order:

```text
Linux Overview
      |
      v
Enumeration
      |
      v
Services
      |
      v
Credentials
      |
      v
Privilege Escalation
```

---

# Related Notes

- [Linux Enumeration](enumeration.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)
- [Active Directory](../active-directory/index.md)
- [Windows](../windows/index.md)

---

# References

- [Linux Kernel Documentation](https://docs.kernel.org/){ target="_blank" rel="noopener noreferrer" }
- [systemd Documentation](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [Ubuntu Security](https://ubuntu.com/security){ target="_blank" rel="noopener noreferrer" }
- [Debian Security Information](https://www.debian.org/security/){ target="_blank" rel="noopener noreferrer" }
- [Red Hat Security](https://access.redhat.com/security/){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }
- [AppArmor](https://apparmor.net/){ target="_blank" rel="noopener noreferrer" }
- [SELinux Project](https://selinuxproject.org/){ target="_blank" rel="noopener noreferrer" }
- [Linux Audit Documentation](https://github.com/linux-audit/audit-documentation){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }
- [Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }
- [pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Linux](https://attack.mitre.org/matrices/enterprise/linux/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on Linux systems you own or have explicit permission to assess. Avoid unnecessary modification, credential collection, service disruption, or kernel-level testing when configuration and permission evidence is sufficient to demonstrate the security issue.
