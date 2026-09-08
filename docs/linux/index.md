---
title: Linux Security Testing
description: Structured Linux security assessment methodology covering enumeration, services, permissions, scheduled jobs, credentials, sudo, SUID and SGID binaries, capabilities, security controls and privilege escalation.
---

# Linux

Linux systems are widely used across enterprise infrastructure, cloud environments, web hosting, development platforms, containers, appliances and security infrastructure.

This section provides a structured reference for assessing Linux hosts during authorised penetration tests, red team assessments and security reviews.

The objective is not simply to execute enumeration commands. A Linux assessment should establish the current security context, understand the host and its role, identify resources that can be influenced, determine which privileged processes consume those resources, evaluate security controls and validate meaningful attack paths.

The core methodology is:

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
Collect Evidence
    |
    v
Report
    |
    v
Remediate
    |
    v
Retest
```

!!! warning "Authorised Security Testing"

    Use these notes only on Linux systems you own or have explicit permission to assess. Prefer read-only enumeration and controlled validation. Avoid unnecessary changes to services, scheduled jobs, permissions, security controls or production data.

---

# Linux Assessment Model

A structured Linux host assessment can be represented as:

```text
Initial Access / User Context
        |
        v
Identity and Privileges
        |
        +---- UID / GID
        +---- Groups
        +---- sudo rights
        +---- Login context
        |
        v
System Enumeration
        |
        +---- Distribution
        +---- Kernel
        +---- Architecture
        +---- Hostname
        +---- Environment
        +---- Packages
        |
        v
Network Enumeration
        |
        +---- Interfaces
        +---- Routes
        +---- DNS
        +---- Listening services
        +---- Connections
        |
        v
Process / Service Enumeration
        |
        +---- Processes
        +---- systemd services
        +---- Legacy init services
        +---- Service identities
        +---- Executable paths
        |
        v
Privilege-Relevant Configuration
        |
        +---- sudo
        +---- SUID / SGID
        +---- Linux capabilities
        +---- cron / timers
        +---- Filesystem permissions
        |
        v
Credential Exposure Review
        |
        +---- Configuration files
        +---- Shell history
        +---- SSH material
        +---- Environment variables
        +---- Application secrets
        +---- Backup files
        |
        v
Security Control Review
        |
        +---- SELinux
        +---- AppArmor
        +---- Firewall
        +---- Audit
        +---- Kernel protections
        |
        v
Privilege Escalation Analysis
        |
        +---- What can I control?
        +---- Who consumes it?
        +---- Under which UID?
        +---- Can behaviour be influenced?
        |
        v
Safe Validation
        |
        v
Evidence
        |
        v
Reporting
        |
        v
Remediation
        |
        v
Retest
```

---

# Linux Notes

<div class="grid cards" markdown>

-   :material-magnify:{ .lg .middle } **Linux Enumeration**

    ---

    Establish the user, operating system, kernel, network, processes, users, groups, packages and overall host context.

    [:octicons-arrow-right-24: Linux Enumeration](enumeration.md)

-   :material-cog:{ .lg .middle } **Linux Services**

    ---

    Service enumeration, systemd, service identities, executables, configuration and privileged service relationships.

    [:octicons-arrow-right-24: Linux Services](services.md)

-   :material-key:{ .lg .middle } **Linux Credentials**

    ---

    Credential exposure, configuration files, shell history, SSH keys, application secrets and authentication material.

    [:octicons-arrow-right-24: Linux Credentials](credentials.md)

-   :material-folder-lock:{ .lg .middle } **Filesystem Permissions**

    ---

    Ownership, Unix permissions, ACLs, writable files and directories, sensitive resources and privileged filesystem relationships.

    [:octicons-arrow-right-24: Filesystem Permissions](filesystem-permissions.md)

-   :material-shield-account:{ .lg .middle } **sudo Security**

    ---

    sudo permissions, sudoers configuration, command restrictions, environment handling and privileged execution.

    [:octicons-arrow-right-24: sudo Security](sudo.md)

-   :material-calendar-clock:{ .lg .middle } **Scheduled Jobs**

    ---

    cron, systemd timers, scheduled scripts, execution identities, writable resources and privileged automation.

    [:octicons-arrow-right-24: Scheduled Jobs](scheduled-jobs.md)

-   :material-file-key:{ .lg .middle } **SUID and SGID**

    ---

    SUID and SGID binaries, ownership, permissions, expected system binaries and security-sensitive execution paths.

    [:octicons-arrow-right-24: SUID and SGID](suid-sgid.md)

-   :material-security:{ .lg .middle } **Linux Capabilities**

    ---

    File and process capabilities, privileged capability assignments and capability-related security analysis.

    [:octicons-arrow-right-24: Linux Capabilities](capabilities.md)

-   :material-shield-check:{ .lg .middle } **Linux Security Controls**

    ---

    SELinux, AppArmor, firewall configuration, audit controls, kernel protections and host hardening.

    [:octicons-arrow-right-24: Linux Security Controls](security-controls.md)

-   :material-arrow-up-bold-circle:{ .lg .middle } **Privilege Escalation**

    ---

    Correlate sudo, SUID, capabilities, services, scheduled jobs, permissions, credentials and software into validated privilege escalation paths.

    [:octicons-arrow-right-24: Linux Privilege Escalation](privilege-escalation.md)

</div>

---

# 1. Establish the Current Security Context

Always establish the current identity before analysing the system.

```bash
whoami
id
```

The `id` command provides:

```text
UID
GID
Primary group
Supplementary groups
```

Example:

```text
uid=1000"user" gid=1000"user" groups=1000"user",27"sudo"
```

Important questions include:

```text
Who am I?

What is my UID?

What is my primary GID?

Which supplementary groups am I in?

Is this an interactive shell?

How was the session established?

Do I have sudo rights?

Are there privileged group memberships?

What environment variables affect execution?
```

Current user information can also be retrieved with:

```bash
id -u
id -un
id -g
id -gn
groups
```

Do not assume that a group membership automatically creates a privilege escalation path.

Determine what the group can actually access or control.

---

# 2. Identify the Operating System

Start by identifying the distribution and release.

```bash
cat /etc/os-release
```

Alternative information may be available from:

```bash
hostnamectl
```

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

Hostname:

```bash
hostname
```

Additional distribution information may be available through:

```bash
lsb_release -a 2>/dev/null
```

The exact commands available depend on the distribution.

Important information includes:

```text
Distribution
Version
Kernel
Architecture
Hostname
Virtualisation
System role
```

Do not conclude that a system is vulnerable solely because a kernel or package version appears old.

Confirm:

```text
Affected version
      +
Relevant configuration
      +
Distribution backports
      +
Patch state
      +
Vulnerable condition
```

before reporting a vulnerability.

Linux distributions frequently backport security patches without changing the upstream version in the way a simple version comparison might suggest.

---

# 3. Understand the Host Role

Determine what the system appears to be used for.

Possible roles include:

```text
Web server

Database server

Application server

Development host

Jump host

Container host

Cloud workload

Monitoring server

Backup server

Security appliance

CI/CD worker

Administrative system
```

Useful clues include:

```bash
ps aux
```

```bash
ss -lntup
```

```bash
systemctl --type=service --state=running
```

Installed packages can also provide context.

Debian-based systems:

```bash
dpkg -l
```

RPM-based systems:

```bash
rpm -qa
```

The host role affects which findings are meaningful and which security controls should reasonably be expected.

---

# 4. Environment Enumeration

Environment variables can expose important system and application context.

```bash
env
```

or:

```bash
printenv
```

Important variables may include:

```text
USER
LOGNAME
HOME
SHELL
PATH
PWD
OLDPWD
LANG
TERM
SSH_CONNECTION
SSH_CLIENT
SUDO_USER
SUDO_COMMAND
```

Application-specific environment variables may also contain:

```text
Database locations

API endpoints

Cloud configuration

Application configuration

Authentication tokens

Credentials

Runtime options
```

Treat potentially sensitive values carefully.

Do not include secrets unnecessarily in screenshots or reports.

---

# 5. PATH Analysis

Inspect the current executable search path:

```bash
echo "$PATH"
```

Display each entry separately:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

A PATH entry is not inherently dangerous.

A security-relevant relationship normally requires something similar to:

```text
Privileged Process
       |
       v
Executes Command Without Absolute Path
       |
       v
PATH Search
       |
       v
Attacker-Writable Directory
       |
       v
Attacker-Controlled Executable
```

Therefore:

```text
Writable PATH Directory
```

alone does not demonstrate privilege escalation.

Determine whether a privileged process actually uses that search path.

---

# 6. User Enumeration

Local account information is typically stored in:

```text
/etc/passwd
```

Review:

```bash
cat /etc/passwd
```

Human users commonly have interactive shells and home directories, but exact UID conventions differ between distributions and environments.

Users with interactive shells can be identified approximately with:

```bash
awk -F: '$7 !~ /(nologin|false)$/ {print $1 ":" $3 ":" $6 ":" $7}' /etc/passwd
```

Do not assume every interactive account is security relevant.

Determine:

```text
Account purpose

Group membership

Home directory

Login capability

Privileged access

Service ownership
```

---

# 7. Group Enumeration

Current groups:

```bash
groups
```

Detailed identity:

```bash
id
```

System groups:

```bash
cat /etc/group
```

Group membership can materially affect Linux security.

Groups commonly worth understanding include environment-dependent examples such as:

```text
sudo
wheel
docker
lxd
libvirt
disk
adm
systemd-journal
```

Membership does not automatically equal a vulnerability.

For example:

```text
User
   |
   v
Group Membership
   |
   v
What Resource Does Group Control?
   |
   v
Can That Resource Affect a Security Boundary?
```

This relationship must be established before reporting.

---

# 8. sudo Enumeration

Check permitted sudo commands:

```bash
sudo -l
```

This is one of the most important Linux privilege-related checks.

Review:

```text
Which commands are allowed?

Which target users are permitted?

Is a password required?

Are command arguments restricted?

Which environment settings are preserved?

Are wildcards used?

Are scripts involved?

Can referenced files be modified?
```

Do not treat every sudo rule as vulnerable.

The security question is whether the permitted command or its dependencies allow behaviour beyond the administrator's intended boundary.

Continue with [sudo Security](sudo.md).

---

# 9. Network Enumeration

Interfaces:

```bash
ip addr
```

Short form:

```bash
ip a
```

Routes:

```bash
ip route
```

Neighbour cache:

```bash
ip neigh
```

DNS configuration may be available from:

```bash
cat /etc/resolv.conf
```

Listening TCP and UDP sockets:

```bash
ss -lntup
```

Current connections:

```bash
ss -antup
```

Older systems may provide:

```bash
netstat -lntup
```

if the relevant package is installed.

Network enumeration can reveal:

- internal networks;
- management interfaces;
- locally bound services;
- database listeners;
- administrative services;
- container networks;
- DNS infrastructure; and
- potential pivoting relationships.

A service bound only to:

```text
127.0.0.1
```

may still be security relevant from an existing local foothold even though it is not externally reachable.

---

# 10. Process Enumeration

Processes:

```bash
ps aux
```

Alternative:

```bash
ps -ef
```

Process trees:

```bash
ps auxf
```

or:

```bash
pstree -a
```

where available.

Look for:

```text
Root-owned processes

Service processes

Database servers

Web servers

Security agents

Backup agents

Monitoring software

Custom scripts

Interpreters

Container runtimes

Administrative tooling
```

A process running as root is not itself a vulnerability.

Ask:

```text
What executable is running?

Who owns it?

What configuration does it load?

Which files does it consume?

Can the current user modify any of them?

Can environment or search paths influence it?
```

---

# 11. Service Enumeration

Modern Linux systems frequently use systemd.

Running services:

```bash
systemctl --type=service --state=running
```

All service units:

```bash
systemctl list-units --type=service --all
```

Installed service unit files:

```bash
systemctl list-unit-files --type=service
```

Inspect a service:

```bash
systemctl status ssh.service
```

Display its unit definition:

```bash
systemctl cat ssh.service
```

Useful service properties can also be queried using:

```bash
systemctl show ssh.service
```

Assessment should correlate:

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
Unit File
    |
    v
Executable
    |
    v
Configuration
    |
    v
Filesystem Permissions
```

A root service is not inherently vulnerable.

The relevant condition is whether a lower-privileged user can influence something the root service executes or consumes.

Continue with [Linux Services](services.md).

---

# 12. Scheduled Jobs

Linux provides several scheduling mechanisms.

Common examples include:

```text
cron

anacron

systemd timers

Application-specific schedulers
```

System cron configuration may include:

```text
/etc/crontab
/etc/cron.d/
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/
```

Review system crontab:

```bash
cat /etc/crontab
```

List systemd timers:

```bash
systemctl list-timers --all
```

Assessment logic:

```text
Scheduled Job
      |
      v
Execution Identity
      |
      v
Command / Script
      |
      v
Referenced Resources
      |
      v
Permissions
      |
      v
Can Lower-Privileged User Influence Them?
```

A root cron job is not automatically vulnerable.

Continue with [Scheduled Jobs](scheduled-jobs.md).

---

# 13. Filesystem Permissions

Linux permission analysis should include:

```text
Owner

Group

Mode

ACLs

Parent directory permissions

Symlink relationships

Mount options
```

Basic inspection:

```bash
ls -la /path
```

Detailed metadata:

```bash
stat /path
```

ACLs where supported:

```bash
getfacl /path
```

Useful permission classes include:

```text
r - read
w - write
x - execute
```

Do not report a writable file or directory without establishing why it matters.

Use:

```text
Writable Resource
       |
       v
What Can Be Changed?
       |
       v
Who Uses It?
       |
       v
Under Which UID?
       |
       v
When Is It Used?
       |
       v
Can Privileged Behaviour Be Influenced?
```

Continue with [Filesystem Permissions](filesystem-permissions.md).

---

# 14. World-Writable Resources

World-writable files:

```bash
find / -xdev -type f -perm -0002 -print 2>/dev/null
```

World-writable directories:

```bash
find / -xdev -type d -perm -0002 -print 2>/dev/null
```

These commands can produce substantial output.

Prefer targeted searches where possible.

Expected writable locations such as:

```text
/tmp
/var/tmp
```

are not automatically vulnerabilities.

The important question is whether privileged processes trust attacker-controllable content stored in those locations.

---

# 15. SUID and SGID Files

SUID and SGID permissions can change the effective identity or group context of an executable.

Find SUID files:

```bash
find / -xdev -type f -perm -4000 -print 2>/dev/null
```

Find SGID files:

```bash
find / -xdev -type f -perm -2000 -print 2>/dev/null
```

Combined search:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null
```

For each interesting binary, record:

```text
Path

Owner

Group

Permissions

Package

Expected purpose

Version

Whether the binary is standard or custom
```

A SUID binary is not automatically vulnerable.

Many legitimate Linux utilities rely on SUID functionality.

The security question is whether the executable exposes functionality that allows the effective privilege boundary to be exceeded.

Continue with [SUID and SGID](suid-sgid.md).

---

# 16. Linux Capabilities

Linux capabilities divide traditional root privileges into more granular units.

Enumerate file capabilities:

```bash
getcap -r / 2>/dev/null
```

Example output may resemble:

```text
/usr/bin/example cap_net_raw=ep
```

Capabilities worth understanding depend on context and can include:

```text
CAP_CHOWN
CAP_DAC_OVERRIDE
CAP_DAC_READ_SEARCH
CAP_FOWNER
CAP_NET_ADMIN
CAP_NET_RAW
CAP_SETGID
CAP_SETUID
CAP_SYS_ADMIN
CAP_SYS_PTRACE
```

Do not treat the presence of a capability as a finding by itself.

Determine:

```text
Which binary has it?

Why does it require it?

Who can execute the binary?

Can the binary expose the capability in an unintended way?

Can the binary or its dependencies be modified?
```

Continue with [Linux Capabilities](capabilities.md).

---

# 17. Shell History

Shell history can contain useful operational information and sometimes sensitive material.

Common files include:

```text
~/.bash_history
~/.zsh_history
```

Current history:

```bash
history
```

Potentially sensitive content may include:

```text
Administrative commands

Database commands

SSH destinations

Deployment commands

Tokens

Passwords supplied as arguments

API credentials
```

Treat discovered secrets as sensitive evidence.

Avoid unnecessarily displaying or storing them.

Continue with [Linux Credentials](credentials.md).

---

# 18. SSH Configuration and Material

SSH is frequently central to Linux administration.

User SSH directory:

```bash
ls -la ~/.ssh
```

Possible files include:

```text
authorized_keys
config
id_rsa
id_ed25519
known_hosts
```

System configuration commonly includes:

```text
/etc/ssh/sshd_config
```

and potentially configuration fragments under:

```text
/etc/ssh/sshd_config.d/
```

When assessing SSH material, consider:

```text
Ownership

Permissions

Purpose

Passphrase protection

Scope

Reuse

Authorisation
```

Do not copy private keys unnecessarily.

If credential material must be collected as evidence, handle it according to the engagement's evidence-handling requirements.

---

# 19. Configuration Files

Applications commonly store security-sensitive information in configuration files.

Potential locations include:

```text
/etc

/opt

/var/www

/srv

Application directories

User home directories
```

Common file types include:

```text
.conf
.ini
.yaml
.yml
.json
.xml
.env
```

Target searches based on the identified application rather than recursively searching the entire filesystem without a reason.

For example:

```bash
find /var/www -type f \( -name '*.env' -o -name '*.conf' -o -name '*.yml' -o -name '*.yaml' \) -print 2>/dev/null
```

Potentially sensitive values include:

```text
Database credentials

API keys

Tokens

Service credentials

Cloud configuration

Private keys

Application secrets
```

---

# 20. Backup and Temporary Files

Operational mistakes can expose sensitive data through:

```text
Backup files

Editor swap files

Temporary files

Old configuration

Archived application directories

Deployment artifacts
```

Examples of naming patterns include:

```text
*.bak
*.old
*.backup
*.swp
*~
```

Search only relevant application locations rather than performing unnecessary full-filesystem scans.

A backup file is security relevant when it contains information or resources that should not be accessible to the current user.

---

# 21. Mounts and Filesystems

Mounted filesystems:

```bash
mount
```

More structured output:

```bash
findmnt
```

Disk usage:

```bash
df -h
```

Block devices:

```bash
lsblk
```

Review:

```text
Filesystem type

Mount location

Ownership

Permissions

Network mounts

Container mounts

Removable storage

Sensitive shares

Mount options
```

Security-relevant mount options may include:

```text
nosuid
nodev
noexec
ro
```

Their significance depends on the filesystem's purpose.

Do not treat absence of one option as a vulnerability without understanding the threat model and workload.

---

# 22. Network Filesystems

Linux hosts may mount remote filesystems such as:

```text
NFS

SMB/CIFS

Distributed storage

Cloud storage
```

Inspect:

```bash
findmnt
```

and where relevant:

```bash
mount
```

Review:

```text
Mount source

Mount point

Credentials

Permissions

Execution behavior

Trust relationship
```

Remote storage can introduce privilege relationships between multiple systems and should be analysed in context.

---

# 23. Containers

Linux hosts frequently run container workloads.

Indicators can include:

```text
Docker

Podman

containerd

Kubernetes components

LXC / LXD
```

Processes:

```bash
ps aux
```

Sockets and groups can provide additional context.

For example, determine whether Docker is present:

```bash
command -v docker
```

and whether the current user belongs to a relevant container-management group:

```bash
id
```

Container access should be treated as a distinct security relationship.

Do not assume:

```text
Docker Installed = Vulnerability
```

Instead determine:

```text
Can Current User Control Container Runtime?
        |
        v
What Runtime Permissions Exist?
        |
        v
What Host Resources Are Exposed?
        |
        v
Does This Affect the Host Security Boundary?
```

---

# 24. Kernel Information

Kernel:

```bash
uname -a
```

Release:

```bash
uname -r
```

Kernel command line:

```bash
cat /proc/cmdline
```

Kernel security assessment should consider:

```text
Distribution

Kernel release

Distribution patches

Architecture

Enabled features

Relevant configuration

Exploit prerequisites
```

Do not report a kernel vulnerability based solely on a version comparison.

Linux distributions frequently backport fixes.

---

# 25. Kernel Parameters

Runtime kernel parameters can be inspected with:

```bash
sysctl -a 2>/dev/null
```

Targeted queries are generally more useful.

Examples:

```bash
sysctl kernel.randomize_va_space
```

```bash
sysctl kernel.dmesg_restrict
```

```bash
sysctl kernel.kptr_restrict
```

```bash
sysctl kernel.yama.ptrace_scope 2>/dev/null
```

Configuration significance depends on:

```text
Distribution

Kernel

Workload

Security baseline

Threat model
```

Do not treat every deviation from a hardening recommendation as an exploitable vulnerability.

---

# 26. SELinux

Check whether SELinux tooling is available:

```bash
command -v getenforce
```

Where available:

```bash
getenforce
```

Possible states commonly include:

```text
Enforcing
Permissive
Disabled
```

Additional status:

```bash
sestatus
```

SELinux should be evaluated in context.

A system without SELinux is not automatically vulnerable if another security architecture is intentionally used.

Continue with [Linux Security Controls](security-controls.md).

---

# 27. AppArmor

AppArmor is commonly encountered on distributions such as Ubuntu.

Where available:

```bash
aa-status
```

Alternative system information may be available under:

```text
/sys/kernel/security/
```

Assess:

```text
Is AppArmor enabled?

Which profiles are loaded?

Which profiles are enforcing?

Which profiles are complain-only?

Which applications are covered?
```

The presence of AppArmor alone does not prove that the target application is confined.

---

# 28. Firewall Configuration

Firewall tooling varies by distribution and deployment.

Possible technologies include:

```text
nftables

iptables

ufw

firewalld
```

nftables:

```bash
nft list ruleset
```

iptables where available:

```bash
iptables -L -n -v
```

UFW:

```bash
ufw status verbose
```

firewalld:

```bash
firewall-cmd --list-all
```

Some commands may require elevated privileges.

Firewall analysis should consider:

```text
Interface

Direction

Protocol

Port

Source

Destination

Default policy

Application requirement
```

A firewall rule should be correlated with actual listening services and network reachability.

---

# 29. Logging and Audit

Linux logging architecture varies between systems.

systemd journal:

```bash
journalctl --no-pager -n 50
```

Traditional logs may exist under:

```text
/var/log
```

List:

```bash
ls -la /var/log
```

Audit subsystem:

```bash
command -v auditctl
```

Where permitted:

```bash
auditctl -s
```

Assessment should determine whether security-relevant activity is:

```text
Generated

Stored

Protected

Centralised

Monitored
```

Logging should be assessed as a defensive capability rather than simply checking whether log files exist.

---

# 30. Security Software

Security tooling may include:

```text
EDR

Antivirus

Audit agents

File-integrity monitoring

SIEM forwarders

Cloud security agents

Configuration management

Monitoring software
```

Identify running processes and services before assuming a particular product is installed or active.

```bash
ps aux
```

```bash
systemctl --type=service --state=running
```

Do not disable security tooling during normal assessment.

Document:

```text
Product

Service state

Observed configuration

Relevant protection

Testing interaction
```

---

# 31. Package Enumeration

Debian-based systems:

```bash
dpkg -l
```

RPM-based systems:

```bash
rpm -qa
```

Package managers may also provide information.

APT:

```bash
apt list --installed 2>/dev/null
```

DNF:

```bash
dnf list installed 2>/dev/null
```

YUM:

```bash
yum list installed 2>/dev/null
```

Do not identify vulnerabilities from package versions without considering distribution-specific security updates and backports.

---

# 32. Writable Executables and Scripts

A particularly important Linux relationship is:

```text
Privileged Process
       |
       v
Executable / Script
       |
       v
Writable by Lower-Privileged User
```

Inspect:

```bash
ls -l /path/to/file
```

Detailed:

```bash
stat /path/to/file
```

ACL:

```bash
getfacl /path/to/file
```

Also inspect the parent directories.

A protected file located inside a user-writable directory can require additional analysis depending on ownership, replacement possibilities and how the privileged process references the resource.

Continue with [Filesystem Permissions](filesystem-permissions.md).

---

# 33. Privilege Escalation Mindset

Linux privilege escalation should be approached as relationship analysis.

Avoid thinking:

```text
SUID = Vulnerable

sudo = Vulnerable

Root Process = Vulnerable

Writable = Vulnerable

Old Version = Vulnerable

Capability = Vulnerable

Cron = Vulnerable
```

Instead ask:

```text
What Can I Control?
        |
        v
Who Uses It?
        |
        v
Under Which UID / GID?
        |
        v
When Is It Used?
        |
        v
What Security Controls Apply?
        |
        v
Can I Influence Privileged Behaviour?
        |
        v
Does This Cross a Security Boundary?
```

Continue with [Linux Privilege Escalation](privilege-escalation.md).

---

# 34. Common Privilege Escalation Areas

A structured Linux assessment should review at least:

```text
sudo
 |
 +---- Command permissions
 +---- Environment
 +---- Arguments
 +---- Referenced resources

SUID / SGID
 |
 +---- Standard binaries
 +---- Custom binaries
 +---- Permissions
 +---- Functionality

Capabilities
 |
 +---- File capabilities
 +---- Process capabilities
 +---- Privileged capability exposure

Services
 |
 +---- Root services
 +---- Unit files
 +---- Executables
 +---- Configuration
 +---- Writable dependencies

Scheduled Jobs
 |
 +---- cron
 +---- systemd timers
 +---- Scripts
 +---- PATH
 +---- Writable resources

Filesystem
 |
 +---- Ownership
 +---- Permissions
 +---- ACLs
 +---- Writable directories
 +---- Sensitive files

Credentials
 |
 +---- Configuration
 +---- History
 +---- SSH
 +---- Environment
 +---- Backups

Software
 |
 +---- Version
 +---- Configuration
 +---- Local attack surface
 +---- Privileged components
```

---

# 35. Manual and Automated Enumeration

A strong Linux assessment combines both manual and automated methods.

```text
Manual Enumeration
        |
        +---- Understand environment
        +---- Establish context
        +---- Identify controls
        +---- Form hypotheses
        |
        v
Automated Enumeration
        |
        +---- Increase coverage
        +---- Identify candidates
        +---- Prioritise review
        |
        v
Manual Validation
        |
        +---- Verify permissions
        +---- Verify ownership
        +---- Verify execution identity
        +---- Verify dependencies
        |
        v
Safe Impact Validation
        |
        v
Evidence
        |
        v
Reporting
```

Automated output should be treated as candidate information until manually validated.

---

# 36. Useful Linux Assessment Tools

## LinPEAS

LinPEAS performs broad Linux privilege escalation enumeration.

Typical areas include:

```text
System information
Users
Groups
sudo
SUID
Capabilities
Processes
Services
Scheduled jobs
Credentials
Interesting files
Containers
Network configuration
```

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Large automated tools can produce substantial output. Use targeted execution where possible and manually verify significant observations.

---

## LinEnum

LinEnum provides Linux host enumeration focused on information useful during privilege escalation analysis.

[LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }

---

## linux-smart-enumeration

linux-smart-enumeration provides tiered Linux enumeration designed to highlight potentially interesting conditions.

[linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

---

## GTFOBins

GTFOBins documents legitimate Unix binaries that can have security-relevant functionality when exposed through particular privilege configurations.

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

!!! note "Interpret GTFOBins correctly"

    The presence of a binary listed by GTFOBins does not itself represent a vulnerability. The relevant question is whether that binary is exposed through a security-sensitive context such as sudo, SUID, capabilities or another privileged execution mechanism.

---

# 37. Practical Validation Model

Use the following model for potentially significant Linux observations:

```text
Observation
     |
     v
Applicability
     |
     v
Current User / UID
     |
     v
Affected Resource
     |
     v
Permissions / Ownership
     |
     v
Privileged Consumer
     |
     v
Influence
     |
     v
Safe Validation
     |
     v
Evidence
     |
     v
Conclusion
```

---

# 38. Example - Writable Script

Suppose enumeration identifies:

```text
/opt/vendor/backup.sh
```

as writable by the current user.

Do not report:

> `/opt/vendor/backup.sh` is writable.

First establish:

```bash
ls -l /opt/vendor/backup.sh
```

Then determine:

```text
Who owns the script?

Who can write to it?

What executes it?

When is it executed?

Which UID executes it?

Is it referenced by cron?

Is it referenced by a systemd timer?

Is it referenced by a service?

Is the path actually used?
```

The relevant relationship might become:

```text
Unprivileged User
       |
       v
Write Permission
       |
       v
/opt/vendor/backup.sh
       |
       v
Root Cron Job
       |
       v
Privileged Execution
```

Only after confirming the relationship should it be treated as a privilege escalation condition.

---

# 39. Example - SUID Binary

Suppose enumeration identifies:

```text
/usr/local/bin/custom-tool
```

with SUID root permissions.

Inspect:

```bash
ls -l /usr/local/bin/custom-tool
```

Then determine:

```text
Is SUID expected?

Who owns it?

Is it part of a package?

Is it custom software?

What functionality does it expose?

Can its configuration be modified?

Does it invoke other programs?

Does it use environment-controlled paths?

Does it drop privileges?

Can privileged functionality be reached by the current user?
```

Do not report:

> SUID binary found.

Report the actual insecure behavior if one exists.

---

# 40. Example - sudo Rule

Suppose:

```bash
sudo -l
```

shows a permitted command.

Do not immediately conclude that root access is possible.

Determine:

```text
Exact command

Target user

Password requirement

Allowed arguments

Environment restrictions

Binary functionality

Configuration dependencies

Writable files

Wildcard behavior

Whether shell execution is possible
```

The rule is security relevant only when the granted functionality exceeds the intended administrative boundary.

---

# 41. False Positives and Alternative Explanations

Linux enumeration frequently produces observations that require additional interpretation.

Examples include:

```text
Root process with protected configuration

Root cron job with protected script

SUID binary that is expected and safely implemented

Capability required for legitimate functionality

Writable temporary directory with no privileged consumer

sudo rule intentionally restricted to safe functionality

Old package version with distribution security patches

SELinux disabled because AppArmor is the chosen MAC framework

Listening service bound only to localhost

Container software installed but inaccessible to current user
```

Before reporting, ask:

```text
Does the condition apply?

Can the current user influence it?

Does a privileged consumer exist?

Is the resource actually consumed?

Do security controls prevent the behavior?

Is the configuration intentional?

Can the impact be safely demonstrated?
```

---

# 42. Evidence Collection

For each potentially significant finding, capture:

```text
Hostname

Distribution

Kernel

Current user

UID / GID

Groups

Relevant sudo permissions

Affected resource

Owner

Group

Permissions

ACL

Privileged consumer

Consumer UID

Command used

Observed output

Security-control context

Validation result
```

Evidence should demonstrate the complete security relationship.

For example:

```text
User
 |
 v
Write Permission
 |
 v
/opt/application/task.sh
 |
 v
systemd Timer
 |
 v
Root-Owned Service
 |
 v
UID 0
```

This is considerably stronger than evidence showing only:

```text
-rwxrwxrwx
```

without demonstrating what uses the file.

---

# 43. Reporting

A useful Linux finding explains the security relationship.

Avoid:

> `/opt/example` is writable.

Prefer:

> The current unprivileged user has write permission to `/opt/example/task.sh`. The script is executed by a systemd service running as root. This allows a lower-privileged user to influence a resource consumed in a privileged execution context.

A strong finding should normally contain:

```text
Observation
        |
        v
Affected Resource
        |
        v
Current Principal
        |
        v
Privileged Consumer
        |
        v
Preconditions
        |
        v
Validated Impact
        |
        v
Recommendation
        |
        v
Retest
```

---

# 44. Remediation Principles

Common Linux hardening principles include:

- apply least privilege;
- restrict sudo permissions;
- remove unnecessary privileged group membership;
- minimise SUID and SGID exposure;
- restrict unnecessary capabilities;
- protect privileged service resources;
- protect scheduled-job resources;
- harden filesystem permissions;
- protect credential material;
- remove unnecessary software;
- maintain supported and patched packages;
- restrict unnecessary services;
- configure host firewall rules;
- use SELinux or AppArmor where appropriate;
- enable appropriate audit and logging controls;
- protect SSH configuration and keys;
- review container-runtime access; and
- centralise security telemetry.

Remediation should address the root cause rather than only the demonstrated proof path.

---

# 45. Retesting

Retesting should verify that the original security relationship no longer exists.

Example original condition:

```text
Unprivileged User
       |
       v
Write
       |
       v
Root-Executed Script
```

After remediation:

```text
Unprivileged User
       |
       v
No Write Permission
       X
Root-Executed Script
```

Retest:

```bash
ls -l /path/to/script
```

Where ACLs are used:

```bash
getfacl /path/to/script
```

Also verify:

```text
Parent directory permissions

Execution identity

Scheduled job or service configuration

Application functionality
```

Remediation should remove the unwanted privilege relationship without breaking legitimate operations.

---

# Linux Assessment Checklist

## Context

- [ ] Identify current user
- [ ] Record UID
- [ ] Record GID
- [ ] Review supplementary groups
- [ ] Review sudo permissions
- [ ] Determine shell
- [ ] Review environment
- [ ] Identify session context

## System

- [ ] Identify distribution
- [ ] Identify release
- [ ] Identify kernel
- [ ] Identify architecture
- [ ] Identify hostname
- [ ] Determine system role
- [ ] Enumerate relevant packages
- [ ] Consider distribution security backports

## Network

- [ ] Enumerate interfaces
- [ ] Enumerate IP addresses
- [ ] Enumerate routes
- [ ] Review DNS configuration
- [ ] Enumerate listeners
- [ ] Review established connections
- [ ] Identify locally bound services
- [ ] Review firewall configuration where authorised

## Users and Groups

- [ ] Enumerate users
- [ ] Identify interactive users
- [ ] Enumerate groups
- [ ] Review privileged groups
- [ ] Review service identities
- [ ] Review unexpected accounts

## Processes

- [ ] Enumerate processes
- [ ] Identify root processes
- [ ] Identify security software
- [ ] Identify management agents
- [ ] Identify custom applications
- [ ] Correlate processes with listeners

## Services

- [ ] Enumerate running services
- [ ] Review service identities
- [ ] Review unit files
- [ ] Review `ExecStart`
- [ ] Review executable permissions
- [ ] Review configuration permissions
- [ ] Review parent directories
- [ ] Identify privileged service relationships

## Scheduled Jobs

- [ ] Review `/etc/crontab`
- [ ] Review `/etc/cron.d`
- [ ] Review periodic cron directories
- [ ] Review systemd timers
- [ ] Review execution identities
- [ ] Review scripts
- [ ] Review referenced resources
- [ ] Review permissions

## Filesystem

- [ ] Review sensitive directories
- [ ] Review writable resources
- [ ] Review ownership
- [ ] Review Unix permissions
- [ ] Review ACLs
- [ ] Review parent directories
- [ ] Review temporary locations
- [ ] Review mount options where relevant

## sudo

- [ ] Run `sudo -l`
- [ ] Identify allowed commands
- [ ] Identify target users
- [ ] Identify password requirements
- [ ] Review command arguments
- [ ] Review environment handling
- [ ] Review referenced files
- [ ] Validate actual security impact

## SUID / SGID

- [ ] Enumerate SUID files
- [ ] Enumerate SGID files
- [ ] Identify unusual binaries
- [ ] Identify custom binaries
- [ ] Review ownership
- [ ] Review package origin
- [ ] Review functionality
- [ ] Validate significant candidates

## Capabilities

- [ ] Enumerate file capabilities
- [ ] Identify unusual capability assignments
- [ ] Review binary ownership
- [ ] Review executable functionality
- [ ] Determine actual capability exposure
- [ ] Validate significant candidates

## Credentials

- [ ] Review relevant configuration files
- [ ] Review shell history where authorised
- [ ] Review SSH material
- [ ] Review application configuration
- [ ] Review environment variables
- [ ] Review backup files
- [ ] Review deployment artifacts
- [ ] Protect collected secrets

## Security Controls

- [ ] Review SELinux where applicable
- [ ] Review AppArmor where applicable
- [ ] Review firewall configuration
- [ ] Review audit configuration
- [ ] Review kernel hardening where relevant
- [ ] Identify endpoint security tooling
- [ ] Review logging architecture

## Containers

- [ ] Identify container runtimes
- [ ] Review current user's runtime access
- [ ] Review privileged groups
- [ ] Consider host/container boundaries
- [ ] Review exposed host resources where relevant

## Validation

- [ ] Manually verify automated findings
- [ ] Confirm ownership
- [ ] Confirm permissions
- [ ] Confirm privileged consumer
- [ ] Confirm execution identity
- [ ] Identify alternative explanations
- [ ] Validate security impact safely
- [ ] Avoid unnecessary system changes

## Reporting

- [ ] Capture reproducible commands
- [ ] Record current identity
- [ ] Record affected resource
- [ ] Record ownership
- [ ] Record permissions
- [ ] Record privileged consumer
- [ ] Explain preconditions
- [ ] Explain validated impact
- [ ] Provide root-cause remediation
- [ ] Define retest procedure

---

# Recommended Reading Order

For a complete Linux host assessment, use these notes approximately in this order:

```text
1. Linux Overview
       |
       v
2. Enumeration
       |
       +----------------+
       |                |
       v                v
3. Services      4. Filesystem Permissions
       |                |
       +--------+-------+
                |
                v
5. sudo Security
                |
                v
6. Scheduled Jobs
                |
                v
7. SUID / SGID
                |
                v
8. Capabilities
                |
                v
9. Credentials
                |
                v
10. Security Controls
                |
                v
11. Privilege Escalation
                |
                v
Validation / Evidence / Reporting
```

Direct links:

1. [Linux Enumeration](enumeration.md)
2. [Linux Services](services.md)
3. [Filesystem Permissions](filesystem-permissions.md)
4. [sudo Security](sudo.md)
5. [Scheduled Jobs](scheduled-jobs.md)
6. [SUID and SGID](suid-sgid.md)
7. [Linux Capabilities](capabilities.md)
8. [Linux Credentials](credentials.md)
9. [Linux Security Controls](security-controls.md)
10. [Linux Privilege Escalation](privilege-escalation.md)

---

# Related Notes

- [Linux Enumeration](enumeration.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Filesystem Permissions](filesystem-permissions.md)
- [sudo Security](sudo.md)
- [Scheduled Jobs](scheduled-jobs.md)
- [SUID and SGID](suid-sgid.md)
- [Linux Capabilities](capabilities.md)
- [Linux Security Controls](security-controls.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)

---

# Linux Security Testing Mindset

The central principle throughout this section is correlation.

Do not think:

```text
Writable = Vulnerable

Root = Vulnerable

SUID = Vulnerable

SGID = Vulnerable

sudo = Vulnerable

Capability = Vulnerable

Cron = Vulnerable

Old Version = Vulnerable

Docker = Vulnerable
```

Instead think:

```text
Observation
      |
      v
What Does It Mean?
      |
      v
Can I Influence It?
      |
      v
Who Consumes It?
      |
      v
Under Which UID / GID?
      |
      v
What Controls Apply?
      |
      v
Can a Security Boundary Be Crossed?
      |
      v
Can That Be Safely Demonstrated?
```

This approach produces better testing, reduces false positives and results in substantially stronger findings.

---

# References

- [Linux Kernel Documentation](https://docs.kernel.org/){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages Project](https://www.kernel.org/doc/man-pages/){ target="_blank" rel="noopener noreferrer" }
- [systemd Documentation](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [Red Hat - SELinux](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/){ target="_blank" rel="noopener noreferrer" }
- [Ubuntu - AppArmor](https://documentation.ubuntu.com/server/how-to/security/apparmor/){ target="_blank" rel="noopener noreferrer" }
- [nftables Wiki](https://wiki.nftables.org/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }
- [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Linux](https://attack.mitre.org/matrices/enterprise/linux/){ target="_blank" rel="noopener noreferrer" }

!!! tip "Start with identity"

    Always establish the current UID, GID, groups and sudo permissions before interpreting privilege-related observations. The same filesystem or service configuration can have completely different security implications depending on the current principal.

!!! tip "Correlate before reporting"

    The strongest Linux findings demonstrate a complete relationship between a lower-privileged principal, a controllable resource, a higher-privileged consumer and a realistic security impact.

!!! tip "Account for distribution backports"

    Do not determine Linux vulnerability exposure from upstream version numbers alone. Distribution vendors frequently backport security fixes while retaining package version structures that can make simple version comparisons misleading.

!!! warning "Validate automated findings"

    LinPEAS, LinEnum, linux-smart-enumeration and similar tools identify candidate conditions. Their output should not be treated as a confirmed vulnerability until ownership, permissions, execution context and practical impact have been manually verified.
