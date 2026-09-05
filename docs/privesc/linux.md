---
title: Linux PrivEsc Explorer
description: Interactive Linux privilege escalation technique explorer for authorised security assessments.
---

# Linux PrivEsc Explorer

<div class="privesc-hero" data-platform="linux">

## Linux PrivEsc Explorer

Search Linux privilege escalation techniques based on sudo permissions, SUID and SGID binaries, capabilities, services, scheduled jobs, filesystem permissions, credentials, containers, groups, sockets, and system configuration discovered during an authorised assessment.

<div class="privesc-hero-badges">
<span class="privesc-badge">LINUX</span>
<span class="privesc-badge">PRIVESC</span>
<span class="privesc-badge">INTERACTIVE</span>
</div>

</div>

---

# Explorer

<div id="privesc-explorer" data-platform="linux">

<div class="privesc-toolbar">

<div class="privesc-search-wrapper">
<label for="privesc-search">Search techniques</label>
<input
    id="privesc-search"
    class="privesc-search"
    type="search"
    placeholder="Try: sudo, SUID, cap_setuid, systemd, cron, docker..."
    autocomplete="off"
>
</div>

<div class="privesc-filter-wrapper">

<label for="privesc-category">Category</label>

<select id="privesc-category" class="privesc-filter">
<option value="all">All categories</option>
</select>

</div>

<div class="privesc-filter-wrapper">

<label for="privesc-severity">Severity</label>

<select id="privesc-severity" class="privesc-filter">
<option value="all">All severities</option>
<option value="critical">Critical</option>
<option value="high">High</option>
<option value="medium">Medium</option>
<option value="low">Low</option>
<option value="informational">Informational</option>
</select>

</div>

<button id="privesc-reset" class="privesc-reset" type="button">
Reset
</button>

</div>

<div id="privesc-active-filters" class="privesc-active-filters"></div>

<div class="privesc-results-header">

<span id="privesc-result-count">
Loading techniques...
</span>

<select id="privesc-sort" class="privesc-sort" aria-label="Sort techniques">
<option value="name">Sort: Name</option>
<option value="severity">Sort: Severity</option>
<option value="category">Sort: Category</option>
</select>

</div>

<div id="privesc-results" class="privesc-results">

<noscript>
PrivEsc Explorer requires JavaScript. The reference material below remains available without JavaScript.
</noscript>

</div>

<div id="privesc-empty" class="privesc-empty" hidden>

## No techniques found

Try another search term or reset the filters.

</div>

</div>

---

# What Should I Search For?

The explorer is designed around discoveries made during Linux enumeration.

Examples:

```text
sudo
```

```text
NOPASSWD
```

```text
SETENV
```

```text
SUID
```

```text
SGID
```

```text
cap_setuid
```

```text
cap_dac_override
```

```text
cap_sys_admin
```

```text
systemd
```

```text
cron
```

```text
PATH
```

```text
docker
```

```text
docker.sock
```

```text
lxd
```

```text
disk
```

```text
shadow
```

```text
NFS
```

```text
no_root_squash
```

```text
writable service
```

```text
writable script
```

```text
socket
```

```text
credential
```

```text
kernel
```

---

# Linux Privilege Escalation Model

Linux privilege escalation usually involves identifying a resource or capability available to the current user that is trusted by a more privileged process, account, or security boundary.

```text
Unprivileged User
       |
       v
Enumeration
       |
       v
Permission / Binary / Group / Capability
       |
       v
Privileged Consumer or Kernel Boundary
       |
       v
Precondition Analysis
       |
       v
Controlled Validation
       |
       v
Privilege Impact
```

The important question is not simply:

```text
Is this writable?
```

or:

```text
Is this SUID?
```

The important question is:

```text
Can this capability influence a more privileged security context?
```

---

# Categories

The Linux explorer groups techniques into the following areas.

| Category | Focus |
|---|---|
| sudo | Delegated command execution through sudo |
| SUID | Executables running with the file owner's effective UID |
| SGID | Executables running with the file group's effective GID |
| Capabilities | Fine-grained Linux process capabilities |
| Services | Privileged daemons and service dependencies |
| systemd | Units, timers, environment files, and service resources |
| Cron | Scheduled privileged commands and scripts |
| Filesystem | Writable files, directories, and trusted resources |
| PATH | Unsafe command resolution |
| Credentials | Passwords, keys, tokens, and application secrets |
| Groups | Security-sensitive group memberships |
| Containers | Docker, LXD, container runtime, and host relationships |
| NFS | Network filesystem configuration |
| Sockets | Privileged Unix-domain sockets and local APIs |
| Applications | Custom or third-party privileged software |
| Libraries | Dynamic library and module loading |
| Kernel | Kernel-level privilege escalation candidates |

---

# Start With Context

Before analysing individual techniques, establish the current security context.

Identity:

```bash
id
```

Current user:

```bash
whoami
```

Groups:

```bash
groups
```

Detailed identity:

```bash
id -a
```

Kernel:

```bash
uname -a
```

Operating system:

```bash
cat /etc/os-release
```

Architecture:

```bash
uname -m
```

---

# UID and GID

Linux identity is represented primarily through:

```text
UID
GID
Supplementary groups
Effective UID
Effective GID
```

Typical root identity:

```text
uid=0(root)
```

A normal user might appear as:

```text
uid=1000(user)
gid=1000(user)
groups=1000(user)
```

Privilege escalation commonly aims to cross:

```text
UID != 0
   |
   v
UID = 0
```

or obtain equivalent privileged control without necessarily creating an interactive root shell.

---

# sudo

One of the highest-value checks is:

```bash
sudo -l
```

This lists commands the current user may execute through sudo.

Possible output can include:

```text
(ALL : ALL) ALL
```

```text
(root) NOPASSWD: /usr/bin/example
```

```text
(root) /usr/bin/systemctl restart example.service
```

```text
(root) SETENV: /usr/bin/example
```

Each rule must be evaluated in context.

---

# sudo Rule Model

```text
Current User
     |
     v
sudo Rule
     |
     v
Allowed Command
     |
     v
Target User
     |
     v
Command Behaviour
```

A sudo entry is security-sensitive when the delegated program exposes functionality beyond the intended administrative operation.

---

# sudo NOPASSWD

Example:

```text
(root) NOPASSWD: /usr/bin/example
```

This means the command may be executed as the specified target without re-entering the user's password.

`NOPASSWD` alone is not automatically a vulnerability.

The relevant question is:

```text
Can the delegated command perform unintended privileged operations?
```

---

# sudo Command Analysis

For each sudo rule determine:

```text
Target identity
Executable
Arguments
Wildcards
Environment handling
Working directory
Files consumed
Plugins
Editors
Shell escapes
Subcommands
External commands
Configuration
Writable dependencies
```

---

# sudo Wildcards

Rules containing wildcards deserve careful analysis.

Example concept:

```text
/usr/bin/example *
```

A wildcard may allow additional argument control beyond what the administrator intended.

Do not assume every wildcard is exploitable.

Understand how:

```text
sudo
```

and:

```text
the delegated program
```

interpret the resulting arguments.

---

# sudo SETENV

A rule containing:

```text
SETENV
```

may permit preservation or specification of environment variables for the delegated command.

Potentially security-sensitive variables can include those affecting:

```text
Library loading
Interpreter behaviour
Module loading
Application configuration
PATH resolution
```

The practical impact depends on the delegated executable and sudo configuration.

---

# GTFOBins

[GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" } documents Unix binaries that can provide security-sensitive functionality when exposed through configurations such as:

```text
sudo
SUID
Capabilities
```

The presence of a GTFOBins-listed binary is not automatically a vulnerability.

The relevant question is whether the binary is exposed through an unsafe privilege boundary.

---

# SUID

SUID executables can run with the effective UID of the file owner.

Enumerate:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Alternative:

```bash
find / -type f -perm -u=s 2>/dev/null
```

Typical legitimate SUID binaries may exist on standard Linux installations.

Do not report SUID merely because it exists.

---

# SUID Permissions

Inspect:

```bash
ls -l /path/to/binary
```

Example:

```text
-rwsr-xr-x 1 root root ...
```

The:

```text
s
```

in the owner's execute position indicates SUID.

---

# SUID Model

```text
User Executes Binary
        |
        v
SUID Program
        |
        v
Effective UID = File Owner
        |
        v
Program Functionality
```

Security depends heavily on what the program does while operating with the elevated effective UID.

---

# Interesting SUID Binaries

Prioritise:

```text
Custom binaries
Unusual binaries
Interpreters
Editors
File-management tools
Backup tools
Archive utilities
Legacy applications
Organisation-specific executables
Unexpected copies of common programs
```

Standard SUID binaries should still be checked against the expected package and system baseline.

---

# Custom SUID Programs

Custom SUID programs deserve detailed review.

Inspect:

```bash
ls -l /path/to/program
```

```bash
file /path/to/program
```

```bash
stat /path/to/program
```

```bash
ldd /path/to/program
```

where applicable.

Look for unsafe assumptions involving:

```text
PATH
Environment
Relative commands
Temporary files
Configuration
Dynamic libraries
User input
File ownership
Symlinks
```

---

# SGID

Enumerate SGID executables:

```bash
find / -perm -2000 -type f 2>/dev/null
```

SGID programs execute with the effective group identity of the file's group.

This may provide access to:

```text
Protected files
Administrative groups
Application resources
Sockets
Devices
Logs
Credentials
```

depending on the group.

---

# Linux Capabilities

Linux capabilities divide traditional root privileges into smaller units.

Enumerate file capabilities:

```bash
getcap -r / 2>/dev/null
```

Example:

```text
/usr/bin/example cap_setuid=ep
```

Capabilities should be analysed together with the functionality of the executable.

---

# Interesting Capabilities

Potentially security-sensitive capabilities include:

```text
CAP_SETUID
CAP_SETGID
CAP_DAC_OVERRIDE
CAP_DAC_READ_SEARCH
CAP_SYS_ADMIN
CAP_SYS_PTRACE
CAP_SYS_MODULE
CAP_SYS_CHROOT
CAP_NET_ADMIN
CAP_NET_RAW
CAP_CHOWN
CAP_FOWNER
CAP_SETFCAP
```

Their impact depends on the program receiving the capability.

---

# CAP_SETUID

`CAP_SETUID` can permit UID manipulation under applicable conditions.

A capable interpreter or flexible executable may therefore be particularly security-sensitive.

Check:

```bash
getcap /path/to/binary
```

Do not assume every `CAP_SETUID` binary provides a practical root path.

Review the program's functionality.

---

# CAP_SETGID

`CAP_SETGID` can permit manipulation of group identity.

Potential impact depends on which groups provide access to privileged resources.

---

# CAP_DAC_OVERRIDE

`CAP_DAC_OVERRIDE` can bypass selected discretionary access-control checks.

This can provide access to files otherwise protected by normal Unix permissions.

Avoid reading unrelated sensitive information merely because the capability permits it.

---

# CAP_DAC_READ_SEARCH

This capability can bypass selected file read and directory search permission checks.

Assess whether security-sensitive resources become accessible.

---

# CAP_SYS_ADMIN

`CAP_SYS_ADMIN` covers a broad set of privileged operations.

Its presence on a user-accessible executable or container can be highly security-sensitive.

Analyse the exact executable and namespace context before concluding impact.

---

# CAP_SYS_PTRACE

This capability can permit process tracing under applicable conditions.

Potential impact depends on:

```text
Target process
UID relationships
Yama configuration
Namespaces
LSM controls
Process protections
```

---

# CAP_SYS_MODULE

`CAP_SYS_MODULE` permits kernel module operations.

It represents a highly privileged capability and should normally be tightly restricted.

Do not load kernel modules merely to prove impact.

---

# Process Capabilities

For a process:

```bash
grep '^Cap' /proc/self/status
```

Where available:

```bash
capsh --print
```

Capabilities may differ between:

```text
Permitted
Effective
Inheritable
Bounding
Ambient
```

sets.

---

# Services

Linux systems commonly use privileged daemons for:

```text
Web applications
Databases
Monitoring
Backup
Networking
Updates
Management
Security tooling
Custom applications
```

Enumerate running processes:

```bash
ps aux
```

Process tree:

```bash
ps auxf
```

Alternative:

```bash
ps -ef
```

---

# Root Processes

```bash
ps -U root -u root u
```

A root process is not itself a vulnerability.

The assessment question is:

```text
What lower-privileged resources does this root process trust?
```

---

# systemd

List running services:

```bash
systemctl --type=service --state=running
```

List unit files:

```bash
systemctl list-unit-files --type=service
```

Inspect a service:

```bash
systemctl cat example.service
```

Properties:

```bash
systemctl show example.service
```

---

# systemd Unit Model

```text
systemd
   |
   v
Unit File
   |
   +-- ExecStart
   |
   +-- ExecStartPre
   |
   +-- ExecStartPost
   |
   +-- EnvironmentFile
   |
   +-- WorkingDirectory
   |
   +-- User
   |
   +-- Group
   |
   +-- PermissionsStartOnly
```

The exact available directives depend on the unit type and systemd version.

---

# Writable systemd Executable

Suppose:

```text
ExecStart=/opt/company/service.sh
```

and the unit executes as root.

Check:

```bash
ls -l /opt/company/service.sh
```

```bash
namei -l /opt/company/service.sh
```

The relationship becomes:

```text
User
 |
 | write
 v
service.sh
 |
 | executed by
 v
root systemd service
```

This can often be demonstrated without modifying the script.

---

# Writable systemd Unit

Locate:

```bash
systemctl cat example.service
```

Check the unit file:

```bash
ls -l /etc/systemd/system/example.service
```

A lower-privileged writable root service unit is highly security-sensitive.

Do not edit the unit merely to demonstrate the issue.

---

# EnvironmentFile

Example unit directive:

```text
EnvironmentFile=/etc/example/example.env
```

Check:

```bash
ls -l /etc/example/example.env
```

Determine whether the variables influence privileged command execution.

A writable environment file is not automatically exploitable.

---

# systemd Timers

Enumerate:

```bash
systemctl list-timers --all
```

Inspect:

```bash
systemctl cat example.timer
```

and the corresponding service.

A timer is analogous to other scheduled execution mechanisms:

```text
Timer
  |
  v
Service
  |
  v
Command
  |
  v
Execution Identity
```

---

# Cron

System cron configuration may exist in:

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

```bash
ls -la /etc/cron.d
```

---

# Cron Process Model

```text
cron
 |
 v
Schedule
 |
 v
User
 |
 v
Command / Script
 |
 v
Dependencies
```

A root cron job becomes security-sensitive when a lower-privileged user controls the executed resource or its trusted dependencies.

---

# Writable Cron Script

Example:

```text
root /opt/company/backup.sh
```

Check:

```bash
ls -l /opt/company/backup.sh
```

```bash
namei -l /opt/company/backup.sh
```

If a normal user can modify the script:

```text
User
 |
 | write
 v
backup.sh
 |
 | executed by cron
 v
root
```

The privilege relationship can be established without modifying the script.

---

# Cron PATH

Review PATH definitions in:

```text
/etc/crontab
/etc/cron.d/*
```

A privilege escalation candidate may exist when:

```text
Privileged Cron Job
        |
        v
Relative Command
        |
        v
PATH Search
        |
        v
Writable Earlier Directory
```

Do not report a writable PATH without identifying a privileged relative command.

---

# Wildcards in Scheduled Jobs

Backup and archive commands sometimes operate on wildcard-expanded file sets.

Review carefully when privileged jobs use:

```text
tar
rsync
cp
find
chown
chmod
```

or custom utilities against user-writable directories.

The impact depends on how the specific command interprets filenames and arguments.

---

# Filesystem Permissions

Find world-writable files:

```bash
find / -xdev -type f -perm -0002 2>/dev/null
```

World-writable directories:

```bash
find / -xdev -type d -perm -0002 2>/dev/null
```

These commands identify candidates, not vulnerabilities.

---

# Sticky Bit

A directory such as:

```text
/tmp
```

is commonly world-writable but protected by the sticky bit.

Example:

```text
drwxrwxrwt
```

The final:

```text
t
```

changes deletion and replacement semantics.

Do not treat standard `/tmp` permissions as a finding by themselves.

---

# ACLs

Traditional permission output may not show the complete access model.

Check:

```bash
getfacl /path/to/resource
```

ACL entries may grant access beyond standard:

```text
owner
group
other
```

permissions.

---

# Parent Directory Permissions

Use:

```bash
namei -l /path/to/file
```

This is useful because a protected file may still be exposed through unsafe parent-directory permissions.

Analyse the complete path.

---

# Writable Root-Owned Script

A file can be:

```text
root-owned
```

while still being writable by another identity through:

```text
Group permissions
ACL
Parent-directory replacement
```

Ownership alone is not enough.

---

# PATH

Display:

```bash
printf '%s\n' "$PATH"
```

One entry per line:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Check permissions:

```bash
ls -ld /path/from/PATH
```

---

# Writable PATH Directory

The required relationship is:

```text
Privileged Process
       |
       v
Executes Relative Command
       |
       v
PATH Resolution
       |
       v
Writable Directory
```

A writable PATH directory without a privileged consumer is usually not a privilege escalation finding.

---

# Relative Commands in Scripts

Inspect privileged scripts for commands such as:

```text
cp
mv
tar
python
bash
sh
awk
sed
find
```

without explicit absolute paths.

Then determine the PATH used by the privileged execution context.

---

# Credentials

Potential credential locations include:

```text
Shell history
Configuration files
Environment variables
SSH keys
Application configuration
Database configuration
Backup files
Deployment scripts
Cloud credentials
Container configuration
Git repositories
Service environment files
```

Detailed handling is covered in [Linux Credentials](../linux/credentials.md).

---

# Shell History

Potential history files include:

```text
~/.bash_history
~/.zsh_history
~/.python_history
```

Targeted search:

```bash
grep -Ei 'pass(word)?|secret|token|api[_-]?key|credential' ~/.bash_history 2>/dev/null
```

Avoid printing secrets unnecessarily.

---

# Environment

```bash
env
```

Targeted names:

```bash
env | cut -d= -f1 | grep -Ei 'pass|secret|token|key|cred'
```

Searching names first reduces unnecessary exposure of secret values.

---

# SSH Keys

Typical locations:

```text
~/.ssh/
```

Inspect metadata:

```bash
ls -la ~/.ssh
```

Possible files include:

```text
id_rsa
id_ed25519
authorized_keys
known_hosts
config
```

Private keys must be handled as sensitive credential material.

---

# Application Configuration

Potential locations include:

```text
/opt/
/srv/
/var/www/
/etc/
User home directories
Application deployment directories
```

Search narrowly around known applications rather than recursively dumping every configuration file.

---

# Group Membership

Current groups:

```bash
id
```

or:

```bash
groups
```

Some groups can provide security-sensitive access depending on the host.

Examples include:

```text
docker
lxd
disk
shadow
adm
systemd-journal
libvirt
```

Membership is a candidate requiring contextual analysis.

---

# docker Group

Check:

```bash
id
```

Docker socket:

```bash
ls -l /var/run/docker.sock
```

Docker access can represent a host-equivalent administrative boundary on many standard configurations because the daemon commonly operates with root privileges.

The exact impact depends on:

```text
Docker daemon configuration
Rootless Docker
Socket permissions
Authorization plugins
Container restrictions
Host configuration
```

---

# Docker Socket

Check:

```bash
stat /var/run/docker.sock
```

or:

```bash
ls -l /var/run/docker.sock
```

Determine:

```text
Owner
Group
Permissions
Daemon mode
Current group membership
```

Do not launch privileged containers on production hosts merely to demonstrate the relationship.

---

# Rootless Docker

Rootless Docker changes the security relationship.

Do not assume:

```text
docker group = root
```

without establishing whether the daemon itself operates with root privileges.

---

# LXD

Check groups:

```bash
id
```

Potential socket locations can be reviewed according to the installed LXD configuration.

LXD administration can provide significant control over containers and potentially host resources depending on configuration.

Confirm the actual daemon and storage model before concluding impact.

---

# disk Group

Membership in:

```text
disk
```

can provide direct access to block devices on many Linux systems.

Check:

```bash
id
```

Devices:

```bash
ls -l /dev/sd* /dev/nvme* 2>/dev/null
```

Direct block-device access can bypass normal filesystem permissions.

Do not read unrelated disk content merely to prove access.

---

# shadow Group

Membership in a group capable of reading:

```text
/etc/shadow
```

is security-sensitive.

Check metadata:

```bash
ls -l /etc/shadow
```

Do not copy password hashes unnecessarily.

Permission evidence may be sufficient.

---

# adm and systemd-journal

These groups can provide access to extensive system logs.

Logs may contain:

```text
Usernames
Application data
Tokens
URLs
Errors
Operational secrets
```

Their security impact depends on what is actually logged.

Do not classify log-reading groups as automatic root escalation.

---

# libvirt

Virtualisation management groups can provide extensive control over local virtual machines and storage.

Assess:

```text
Daemon privilege
Socket permissions
Storage access
VM configuration
Host filesystem exposure
```

before determining impact.

---

# Unix-Domain Sockets

Find Unix sockets:

```bash
find / -type s 2>/dev/null
```

Target common runtime locations first where possible:

```bash
find /run /var/run /tmp -type s 2>/dev/null
```

A socket is only interesting when its server exposes security-sensitive functionality.

---

# Socket Model

```text
User
 |
 | connect
 v
Unix Socket
 |
 v
Privileged Daemon
 |
 v
Administrative API
```

Determine:

```text
Server process
Server identity
Socket owner
Socket group
Socket permissions
Protocol
Authentication
Available operations
```

---

# D-Bus

D-Bus can expose privileged system services.

System bus:

```bash
busctl list
```

where available.

A service being present does not mean it exposes unsafe privileged methods.

Analyse:

```text
Service identity
Policy
Methods
Authentication
Polkit integration
```

---

# Polkit

Polkit mediates authorisation for many privileged desktop and system services.

Installed rules may exist under locations such as:

```text
/etc/polkit-1/rules.d/
/usr/share/polkit-1/rules.d/
```

Assess:

```text
Custom rules
Group-based authorisation
Authentication requirements
Service integration
```

Do not assume Polkit itself is a vulnerability.

---

# NFS

Review mounted filesystems:

```bash
mount
```

NFS mounts:

```bash
mount -t nfs,nfs4
```

Local export configuration, where accessible:

```bash
cat /etc/exports
```

---

# root_squash

NFS commonly uses:

```text
root_squash
```

to map remote root access to a less privileged identity.

An export configured with:

```text
no_root_squash
```

deserves careful review.

The actual impact depends on:

```text
Export permissions
Client restrictions
Filesystem content
Execution context
Mount options
Network accessibility
```

---

# Mount Options

Review:

```bash
mount
```

Security-relevant options can include:

```text
nosuid
noexec
nodev
ro
rw
```

These options affect exploitability and should be recorded when evaluating filesystem-based candidates.

---

# Dynamic Libraries

Inspect dependencies:

```bash
ldd /path/to/binary
```

where appropriate.

Potential issues can involve:

```text
Writable library files
Writable library directories
Unsafe custom search paths
Privileged programs loading user-controlled libraries
```

---

# ldconfig

Review:

```bash
ldconfig -p
```

Configuration commonly exists under:

```text
/etc/ld.so.conf
/etc/ld.so.conf.d/
```

A writable library configuration used by privileged system processes can be security-sensitive.

Do not modify dynamic linker configuration merely to prove the condition.

---

# LD_LIBRARY_PATH

Environment-controlled library paths can become security-sensitive when preserved into a privileged execution context.

Most normal privileged execution mechanisms deliberately restrict dangerous environment variables.

Confirm actual behaviour rather than assuming inheritance.

---

# Interpreters and Module Search Paths

Privileged scripts using:

```text
Python
Perl
Ruby
Node.js
PHP
Shell
```

may load modules, libraries, or configuration from search paths.

For example, review Python's effective import behaviour only when a privileged Python application is identified.

The presence of Python itself is not a privilege escalation issue.

---

# Writable Imported Module

Model:

```text
Root Python Script
       |
       v
Imports Module
       |
       v
Module Search
       |
       v
User-Writable Module
```

Confirm the actual imported path before reporting.

---

# Temporary Files

Privileged applications sometimes use:

```text
/tmp
/var/tmp
Custom temporary directories
```

Potential weaknesses can involve:

```text
Predictable filenames
Unsafe permissions
Symlink handling
Race conditions
Insecure replacement
```

These conditions require application-specific validation.

---

# Symlinks

Check:

```bash
ls -l /path/to/resource
```

Resolve:

```bash
readlink -f /path/to/resource
```

Do not report symlink presence alone.

Determine whether a privileged process follows a lower-privileged controlled link in a security-sensitive operation.

---

# Backup Jobs

Backup systems often execute with elevated privileges and interact with large filesystem areas.

Review:

```text
Backup scripts
Configuration
Archive commands
Destination permissions
Source permissions
Temporary files
Credentials
Scheduled execution
```

Custom backup scripts are particularly valuable review targets.

---

# tar

`tar` is a normal archive utility.

It becomes relevant when:

```text
Privileged automation
+
User-controlled files or arguments
+
Unsafe command construction
```

interact.

Do not report `tar` simply because root uses it.

---

# rsync

Review privileged `rsync` automation for:

```text
Source control
Destination control
Options
Remote identities
Scripts
Writable configuration
```

Again, the binary itself is not the weakness.

---

# logrotate

Configuration can exist under:

```text
/etc/logrotate.conf
/etc/logrotate.d/
```

Review custom entries where:

```text
Privileged logrotate
+
User-controlled file or directory
+
Unsafe configuration
```

may create a privilege boundary issue.

---

# Custom Scripts

Search known privileged execution paths for:

```text
Shell scripts
Python scripts
Perl scripts
Backup scripts
Deployment scripts
Maintenance scripts
Monitoring scripts
```

Review:

```text
Owner
Permissions
Parent directories
PATH
Environment
External commands
Input handling
Configuration
Imports
Temporary files
```

---

# Writable Configuration

A root-owned process may consume a configuration file writable by a lower-privileged user.

Check:

```bash
ls -l /path/to/config
```

```bash
namei -l /path/to/config
```

```bash
getfacl /path/to/config
```

Determine what configuration options actually influence.

---

# Plugins

Applications supporting plugins or extensions deserve additional review.

Model:

```text
Privileged Application
       |
       v
Plugin Directory
       |
       v
User-Writable Plugin
```

Confirm:

```text
Plugin discovery
Plugin loading
Directory permissions
Application identity
Activation condition
```

---

# Package Managers

Package-management access can represent administrative control.

Relevant tools include:

```text
apt
apt-get
dpkg
dnf
yum
rpm
pacman
zypper
```

If sudo permits unrestricted package-management operations, evaluate whether that delegation effectively provides administrative control.

---

# Editors

Privileged editor delegation can expose functionality beyond editing a single intended file.

Examples include:

```text
vim
vi
nano
less
```

depending on configuration and restrictions.

Evaluate the exact sudo rule and program functionality.

---

# Shells and Interpreters

Direct sudo access to:

```text
bash
sh
zsh
python
python3
perl
ruby
```

as root generally represents broad administrative capability.

Record the sudo rule itself as the root cause rather than treating the interpreter as vulnerable software.

---

# Compilers

Access to compilers such as:

```text
gcc
clang
```

is not itself a privilege escalation issue.

It becomes relevant only when combined with a privileged execution mechanism or writable trusted resource.

---

# Process Monitoring

Privilege escalation opportunities sometimes depend on short-lived root processes.

Native monitoring:

```bash
ps aux
```

Repeated process inspection can help identify recurring jobs.

Tools such as [pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" } can assist with observing process activity without requiring root on supported systems.

Use assessment tooling only where authorised.

---

# Recently Modified Files

Targeted review can identify deployment or maintenance resources.

Example:

```bash
find /opt /srv /usr/local -type f -mtime -7 2>/dev/null
```

Avoid indiscriminate searches across very large production filesystems.

---

# /usr/local

Custom administrative software commonly exists under:

```text
/usr/local/bin
/usr/local/sbin
/usr/local/lib
```

Review:

```bash
ls -ld /usr/local/bin /usr/local/sbin /usr/local/lib
```

and relevant custom files.

---

# /opt

Third-party and organisation-specific applications frequently use:

```text
/opt
```

Prioritise:

```text
Custom services
Scripts
Configuration
Plugins
Update mechanisms
Writable directories
Credentials
```

---

# /srv

Application and service data may exist under:

```text
/srv
```

Determine whether privileged services execute or import content from lower-privileged writable locations.

---

# Kernel

Kernel privilege escalation should normally be considered after deterministic configuration weaknesses.

Collect:

```bash
uname -a
```

```bash
cat /etc/os-release
```

Package information depends on distribution.

Debian-based:

```bash
dpkg-query -W 'linux-image*' 2>/dev/null
```

RPM-based:

```bash
rpm -qa | grep -i '^kernel'
```

---

# Kernel Version Is Not Enough

Do not conclude:

```text
Kernel version appears old
=
Kernel LPE confirmed
```

Consider:

```text
Distribution
Exact package build
Vendor backports
Architecture
Kernel configuration
Required namespace
Required capability
Mitigations
Patch status
Exploit prerequisites
```

Vendor security advisories are more authoritative than generic version matching.

---

# Kernel Exploit Validation

Kernel exploitation carries greater operational risk than most configuration validation.

Before attempting active validation determine:

```text
Is configuration evidence sufficient?
Is a safer privilege path already available?
Is the host production?
Could the test crash the kernel?
Could data be corrupted?
Is explicit approval present?
Is rollback available?
```

Avoid kernel exploit execution where unnecessary.

---

# ASLR

Check:

```bash
cat /proc/sys/kernel/randomize_va_space
```

Typical values:

```text
0
1
2
```

ASLR affects exploitability but does not determine whether a privilege escalation vulnerability exists.

---

# Yama

Where present:

```bash
cat /proc/sys/kernel/yama/ptrace_scope
```

Yama can restrict process tracing.

This is relevant when evaluating ptrace-based conditions.

---

# AppArmor

Check where available:

```bash
aa-status
```

AppArmor can restrict application behaviour even when traditional Unix permissions would otherwise permit it.

Do not assume root-equivalent behaviour without considering active mandatory access controls.

---

# SELinux

Check:

```bash
getenforce
```

Possible states include:

```text
Enforcing
Permissive
Disabled
```

Context:

```bash
id -Z
```

where supported.

SELinux policy can materially affect exploitability.

---

# seccomp

Process status may expose:

```bash
grep '^Seccomp' /proc/self/status
```

Seccomp filters can restrict available system calls.

This is particularly relevant in container and sandbox environments.

---

# NoNewPrivileges

Check:

```bash
grep '^NoNewPrivs' /proc/self/status
```

`NoNewPrivileges` can prevent certain privilege gains through executable transitions.

Consider it when evaluating SUID and capability-based behaviour.

---

# Containers

Determine whether the current environment is containerised.

Useful indicators can include:

```bash
cat /proc/1/cgroup
```

```bash
cat /proc/self/mountinfo
```

```bash
test -f /.dockerenv && echo "Docker environment indicator present"
```

Do not rely on a single indicator.

---

# Container Privilege Model

```text
Container Process
       |
       v
Namespaces
       |
       +-- User
       +-- Mount
       +-- PID
       +-- Network
       |
       v
Capabilities
       |
       v
Devices / Host Mounts / Runtime Socket
       |
       v
Host Boundary
```

A container root user is not necessarily host root.

---

# Privileged Containers

Review:

```text
Capabilities
Devices
Host mounts
Runtime sockets
Namespaces
Security profiles
User namespace
```

A highly privileged container may significantly weaken host isolation.

Do not attempt host escape solely because the container appears privileged.

---

# Host Filesystem Mounts

Inspect:

```bash
mount
```

and:

```bash
cat /proc/self/mountinfo
```

Host filesystem mounts can expose security-sensitive host resources.

Record:

```text
Source
Destination
Read/write state
Namespace
Permissions
```

---

# Excessive Container Capabilities

Check:

```bash
capsh --print
```

or:

```bash
grep '^Cap' /proc/self/status
```

Capabilities such as:

```text
CAP_SYS_ADMIN
CAP_SYS_PTRACE
CAP_SYS_MODULE
```

can materially weaken isolation depending on namespace and runtime configuration.

---

# Docker Socket in Container

Check:

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

A host Docker socket mounted into a container can expose extensive daemon control.

Confirm whether the socket points to a rootful or rootless daemon and whether authorisation controls are present.

---

# Local Network Services

Listening sockets:

```bash
ss -lntup
```

Without process information where permissions restrict it:

```bash
ss -lntu
```

Local-only administrative services may expose privileged functionality.

---

# Databases

Local databases can contain:

```text
Application credentials
Password hashes
Tokens
Session data
Administrative configuration
```

Access should be assessed against scope and data-handling requirements.

Do not dump entire databases unnecessarily.

---

# Management Agents

Prioritise privileged:

```text
Backup agents
Monitoring agents
Deployment agents
Configuration-management agents
Security agents
Update services
Custom management daemons
```

These often have:

```text
Root execution
Network interfaces
Local sockets
Configuration files
Plugins
Update mechanisms
Credentials
```

---

# Candidate Prioritisation

A useful prioritisation order is:

```text
1. sudo rules

2. Security-sensitive groups

3. SUID / SGID

4. File capabilities

5. Writable root service resources

6. Writable scheduled-job resources

7. Credentials

8. PATH and environment trust

9. Privileged local sockets and APIs

10. Container / runtime control

11. Custom privileged applications

12. Third-party software

13. Kernel vulnerabilities
```

This prioritises deterministic configuration issues before riskier exploit paths.

---

# Automated Enumeration

Tools can accelerate candidate discovery.

Examples include:

[PEASS-ng / LinPEAS](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

[Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

[LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }

[pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }

Automated results must still be manually validated.

---

# Native Enumeration First

Where possible, establish the important security relationships with native commands:

```bash
id
sudo -l
find
getcap
ps
systemctl
ls
stat
namei
getfacl
mount
ss
```

This provides transparent evidence and reduces dependence on scanner interpretation.

---

# Candidate Validation

Use:

```text
Candidate
   |
   v
Confirm Current Identity
   |
   v
Confirm Permission / Capability
   |
   v
Identify Privileged Consumer
   |
   v
Confirm Activation
   |
   v
Review Security Controls
   |
   v
Minimal Validation
```

---

# Example - Writable Root Service Script

Discovery:

```text
/opt/company/service.sh
```

Permissions:

```text
-rwxrwxr-x root developers
```

Current user:

```text
groups=user developers
```

Service:

```text
User=root
ExecStart=/opt/company/service.sh
```

Model:

```text
Normal User
    |
    | group write
    v
service.sh
    |
    | executed by
    v
root service
```

The configuration and ACL evidence establish the privilege relationship.

---

# Example - sudo Rule

Discovery:

```text
(root) NOPASSWD: /usr/bin/example
```

Do not immediately conclude:

```text
root compromise
```

Instead analyse:

```text
What does example do?
Can arguments be controlled?
Does it launch external programs?
Does it load configuration?
Does it invoke an editor?
Does it provide shell functionality?
Does it consume writable files?
Does it preserve dangerous environment variables?
```

---

# Example - Capability

Discovery:

```text
/usr/bin/example cap_setuid=ep
```

Analyse:

```text
What functionality does the binary expose?
Can it manipulate UID?
Is the capability effective?
Is the executable user-accessible?
Are additional security controls present?
```

---

# Example - Docker

Discovery:

```text
user belongs to docker group
```

Confirm:

```bash
ls -l /var/run/docker.sock
```

Then determine:

```text
Is the daemon rootful?
Can the user access the socket?
Are authorization controls present?
What host resources can the daemon manage?
```

Do not automatically launch a privileged container.

---

# Evidence Collection

For each candidate record:

| Field | Example |
|---|---|
| Host | `linux-app-01` |
| Current user | `analyst` |
| UID | `1001` |
| Groups | `analyst,developers` |
| Technique | Writable systemd Service Script |
| Resource | `/opt/company/service.sh` |
| Privileged consumer | `company.service` |
| Consumer identity | `root` |
| Permission | Group write |
| Activation | Service start |
| Validation | Permission and unit configuration |
| Result | Privilege boundary confirmed |
| MITRE | Applicable technique |

---

# Confidence Levels

## Candidate

An interesting configuration exists.

Example:

```text
SUID binary discovered.
```

## Likely

Important prerequisites appear to exist.

Example:

```text
Custom root-owned SUID binary performs unsafe relative command execution.
```

## Confirmed

The privilege relationship has been established with sufficient evidence.

Example:

```text
Normal user can modify a script executed by a root systemd service.
```

---

# Severity Considerations

Severity depends on:

```text
Starting privilege
Resulting privilege
Reliability
Interaction required
Execution frequency
System criticality
Existing controls
Scope of resulting access
Operational impact
```

A deterministic:

```text
Unprivileged User -> root
```

configuration path normally carries greater impact than a speculative kernel candidate requiring unsafe active exploitation.

---

# Detection Opportunities

Linux privilege escalation monitoring can include:

```text
sudo activity
SUID and SGID changes
Capability changes
systemd unit changes
Cron changes
Privileged script modification
Sensitive file access
Group membership changes
Docker socket access
Container creation
Kernel module loading
Unexpected root process execution
Security-policy changes
```

---

# Authentication Logs

Depending on distribution and configuration, sudo activity may appear in:

```text
/var/log/auth.log
```

or:

```text
/var/log/secure
```

systemd journal:

```bash
journalctl
```

sudo-specific review may be available through:

```bash
journalctl _COMM=sudo
```

depending on the logging environment.

---

# auditd

Where deployed, Linux Audit can provide detailed telemetry for:

```text
File changes
Privilege use
Process execution
Identity changes
Configuration changes
```

Actual coverage depends on configured audit rules.

---

# File Integrity Monitoring

Prioritise:

```text
/etc/
/usr/local/
/opt/
/etc/systemd/system/
/etc/cron.d/
/etc/sudoers
/etc/sudoers.d/
Privileged application directories
```

according to the host role.

---

# Remediation Model

```text
Finding
   |
   v
Identify Privileged Consumer
   |
   v
Identify Lower-Privilege Control
   |
   v
Remove Excess Permission
   |
   v
Reduce Consumer Privilege
   |
   v
Apply Hardening
   |
   v
Add Monitoring
   |
   v
Retest
```

---

# sudo Remediation

```text
Delegate only required commands
Avoid unrestricted interpreters and shells
Avoid unsafe wildcards
Restrict arguments where feasible
Avoid unnecessary SETENV
Protect delegated scripts and configuration
Use dedicated administrative roles
Review sudoers regularly
```

---

# SUID and SGID Remediation

```text
Remove unnecessary SUID / SGID bits
Use capabilities where narrowly appropriate
Remove obsolete binaries
Protect custom privileged executables
Review package ownership
Monitor SUID / SGID changes
```

---

# Capability Remediation

```text
Remove unnecessary file capabilities
Assign the minimum required capability
Avoid broad capabilities such as CAP_SYS_ADMIN
Review capable interpreters carefully
Monitor capability changes
```

Remove a file capability where appropriate:

```bash
setcap -r /path/to/binary
```

Only administrators should perform remediation changes.

---

# Service Remediation

```text
Protect unit files
Protect executables
Protect scripts
Protect configuration
Protect environment files
Use absolute command paths
Use dedicated service users
Use minimum required capabilities
Apply systemd hardening
```

---

# Cron Remediation

```text
Protect cron configuration
Protect scripts
Protect parent directories
Use absolute paths
Use controlled PATH values
Avoid unsafe wildcard processing
Use least privilege
```

---

# Filesystem Remediation

```text
Remove unnecessary world-write
Restrict group write
Review ACLs
Protect parent directories
Separate writable data from executable content
Use correct ownership
Use sticky bit where appropriate
```

---

# Credential Remediation

```text
Remove plaintext credentials
Rotate exposed secrets
Protect SSH private keys
Use dedicated service identities
Use secret-management systems
Avoid secrets in shell history
Avoid secrets in command lines
Restrict configuration files
```

---

# Container Remediation

```text
Restrict runtime socket access
Avoid unnecessary privileged containers
Drop unnecessary capabilities
Avoid host filesystem mounts
Use user namespaces where appropriate
Use rootless modes where appropriate
Apply seccomp
Apply AppArmor or SELinux
Restrict devices
Apply least privilege
```

---

# Kernel Remediation

```text
Use supported distributions
Apply vendor security updates
Track vendor advisories
Remove unsupported kernels
Reboot into updated kernels when required
Use exploit mitigations
Reduce unnecessary local access
```

---

# Linux Explorer Checklist

## Context

- [ ] Current user
- [ ] UID
- [ ] GID
- [ ] Groups
- [ ] Kernel
- [ ] Distribution
- [ ] Architecture
- [ ] Container context
- [ ] Security controls

## sudo

- [ ] `sudo -l`
- [ ] Target user
- [ ] NOPASSWD
- [ ] SETENV
- [ ] Wildcards
- [ ] Arguments
- [ ] Shell escapes
- [ ] External commands
- [ ] Writable dependencies
- [ ] GTFOBins applicability

## SUID / SGID

- [ ] SUID inventory
- [ ] SGID inventory
- [ ] Custom binaries
- [ ] Unexpected binaries
- [ ] Owner
- [ ] Group
- [ ] Permissions
- [ ] PATH usage
- [ ] Environment
- [ ] External commands

## Capabilities

- [ ] `getcap -r /`
- [ ] CAP_SETUID
- [ ] CAP_SETGID
- [ ] CAP_DAC_OVERRIDE
- [ ] CAP_DAC_READ_SEARCH
- [ ] CAP_SYS_ADMIN
- [ ] CAP_SYS_PTRACE
- [ ] CAP_SYS_MODULE
- [ ] Capable interpreters

## Services

- [ ] Root processes
- [ ] systemd services
- [ ] Unit files
- [ ] ExecStart
- [ ] Service user
- [ ] Executable ACL
- [ ] Script ACL
- [ ] Configuration ACL
- [ ] EnvironmentFile
- [ ] Parent directories

## Scheduled Execution

- [ ] Cron
- [ ] `/etc/crontab`
- [ ] `/etc/cron.d`
- [ ] systemd timers
- [ ] Root scripts
- [ ] PATH
- [ ] Wildcards
- [ ] Writable resources

## Filesystem

- [ ] World-writable files
- [ ] World-writable directories
- [ ] Group-writable privileged resources
- [ ] ACLs
- [ ] Parent directories
- [ ] `/opt`
- [ ] `/usr/local`
- [ ] `/srv`
- [ ] Temporary files
- [ ] Symlinks

## Credentials

- [ ] Shell history
- [ ] Environment
- [ ] SSH keys
- [ ] Application configuration
- [ ] Database configuration
- [ ] Backup files
- [ ] Deployment scripts
- [ ] Service environment files
- [ ] Cloud credentials

## Groups

- [ ] docker
- [ ] lxd
- [ ] disk
- [ ] shadow
- [ ] adm
- [ ] systemd-journal
- [ ] libvirt
- [ ] Custom privileged groups

## Containers

- [ ] Container detection
- [ ] Runtime socket
- [ ] Rootful / rootless
- [ ] Capabilities
- [ ] Host mounts
- [ ] Devices
- [ ] Namespaces
- [ ] seccomp
- [ ] AppArmor / SELinux

## Local Interfaces

- [ ] Unix sockets
- [ ] Local TCP services
- [ ] D-Bus
- [ ] Polkit
- [ ] Management agents
- [ ] Custom administrative APIs

## Kernel

- [ ] Exact kernel package
- [ ] Distribution
- [ ] Vendor advisory
- [ ] Backports
- [ ] Architecture
- [ ] Mitigations
- [ ] Exploit prerequisites
- [ ] Operational risk

## Validation

- [ ] Candidate confirmed
- [ ] Privileged consumer identified
- [ ] Lower-privileged control identified
- [ ] Security controls considered
- [ ] Minimal validation selected
- [ ] Evidence collected
- [ ] Destructive testing avoided
- [ ] Cleanup completed where required

---

# Quick Enumeration

Identity:

```bash
id
```

sudo:

```bash
sudo -l
```

SUID:

```bash
find / -perm -4000 -type f 2>/dev/null
```

SGID:

```bash
find / -perm -2000 -type f 2>/dev/null
```

Capabilities:

```bash
getcap -r / 2>/dev/null
```

Processes:

```bash
ps auxf
```

Root processes:

```bash
ps -U root -u root u
```

Services:

```bash
systemctl --type=service --state=running
```

Timers:

```bash
systemctl list-timers --all
```

Cron:

```bash
cat /etc/crontab
```

PATH:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Mounts:

```bash
mount
```

Sockets:

```bash
ss -lntu
```

Unix sockets:

```bash
find /run /var/run /tmp -type s 2>/dev/null
```

Kernel:

```bash
uname -a
```

OS:

```bash
cat /etc/os-release
```

---

# Explorer Decision Tree

```text
Start
 |
 v
id
 |
 v
sudo -l
 |
 +---- Interesting Rule? -----> Search sudo
 |
 v
Check Groups
 |
 +---- docker/lxd/disk/etc? --> Search Group
 |
 v
Enumerate SUID / SGID
 |
 +---- Interesting Binary? ---> Search SUID / SGID
 |
 v
Enumerate Capabilities
 |
 +---- Sensitive Capability? -> Search Capability
 |
 v
Enumerate Root Services
 |
 +---- Writable Resource? ----> Search Service
 |
 v
Enumerate Cron / Timers
 |
 +---- Writable Action? ------> Search Cron / systemd
 |
 v
Review Filesystem
 |
 +---- Privileged Consumer? --> Search Filesystem
 |
 v
Review Credentials
 |
 +---- Higher Privilege? -----> Search Credentials
 |
 v
Review PATH / Libraries
 |
 +---- Privileged Consumer? --> Search PATH / Libraries
 |
 v
Review Sockets / APIs
 |
 +---- Privileged Service? ---> Search Socket
 |
 v
Review Containers
 |
 +---- Host Control? ---------> Search Container
 |
 v
Review Custom Software
 |
 +---- Privileged Candidate? -> Search Application
 |
 v
Review Kernel
 |
 +---- Applicable Candidate? -> Risk Assessment
 |
 v
No Confirmed Local PrivEsc Path
```

---

# Final Testing Model

```text
1. Establish the current identity.

2. Record UID, GID, and supplementary groups.

3. Record kernel, distribution, and architecture.

4. Determine whether the environment is containerised.

5. Run sudo -l.

6. Analyse each delegated command.

7. Check NOPASSWD and SETENV.

8. Review wildcard and argument handling.

9. Compare relevant delegated binaries with GTFOBins where useful.

10. Enumerate SUID binaries.

11. Enumerate SGID binaries.

12. Prioritise custom and unusual privileged binaries.

13. Enumerate file capabilities.

14. Analyse sensitive capabilities in application context.

15. Enumerate root processes.

16. Enumerate systemd services.

17. Review privileged service unit files.

18. Review service executables and scripts.

19. Review service configuration and environment files.

20. Enumerate systemd timers.

21. Enumerate cron configuration.

22. Identify root scheduled jobs.

23. Review scheduled scripts and dependencies.

24. Review PATH handling.

25. Review filesystem permissions.

26. Review ACLs and parent-directory permissions.

27. Review credentials.

28. Review security-sensitive group membership.

29. Review Docker and container runtime access.

30. Review LXD where installed.

31. Review block-device access.

32. Review Unix-domain sockets.

33. Review local administrative services.

34. Review D-Bus and Polkit where relevant.

35. Review NFS and mount configuration.

36. Review dynamic library trust.

37. Review privileged interpreter module loading.

38. Review custom applications.

39. Review management agents.

40. Review installed third-party software.

41. Consider kernel vulnerabilities after deterministic paths.

42. Verify vendor patch status and backports.

43. Consider AppArmor, SELinux, seccomp, and NoNewPrivileges.

44. Prioritise reproducible configuration weaknesses.

45. Validate with permission and configuration evidence first.

46. Avoid modifying privileged production resources unnecessarily.

47. Avoid dumping credentials when access evidence is sufficient.

48. Avoid launching privileged containers merely to prove daemon access.

49. Avoid kernel exploitation where safer evidence exists.

50. Record the complete privilege relationship.

51. Identify the root cause.

52. Recommend least-privilege remediation.

53. Retest the corrected security boundary.
```

The Linux explorer should answer:

```text
What did I discover?
        |
        v
What privilege does it provide?
        |
        v
What privileged component trusts it?
        |
        v
Are the required conditions present?
        |
        v
How can I validate it safely?
        |
        v
How should it be detected and fixed?
```

rather than simply:

```text
Which root exploit should I run?
```

---

# Related Notes

- [PrivEsc Explorer](index.md)
- [Windows PrivEsc Explorer](windows.md)
- [Linux](../linux/index.md)
- [Linux Enumeration](../linux/enumeration.md)
- [Linux Services](../linux/services.md)
- [Linux Credentials](../linux/credentials.md)
- [Linux Privilege Escalation](../linux/privilege-escalation.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)

---

# References

- [GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }
- [LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }
- [pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages](https://man7.org/linux/man-pages/){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [systemd](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [Linux Kernel Documentation](https://docs.kernel.org/){ target="_blank" rel="noopener noreferrer" }
- [Linux Capabilities - capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }
- [Docker Rootless Mode](https://docs.docker.com/engine/security/rootless/){ target="_blank" rel="noopener noreferrer" }
- [AppArmor](https://apparmor.net/){ target="_blank" rel="noopener noreferrer" }
- [SELinux Project](https://github.com/SELinuxProject){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Abuse Elevation Control Mechanism](https://attack.mitre.org/techniques/T1548/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exploitation for Privilege Escalation](https://attack.mitre.org/techniques/T1068/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Hijack Execution Flow](https://attack.mitre.org/techniques/T1574/){ target="_blank" rel="noopener noreferrer" }

---

> Use Linux privilege escalation techniques only on systems you own or have explicit permission to assess. Explorer results represent assessment candidates rather than automatically confirmed vulnerabilities. Prefer identity, permission, configuration, and privileged-consumer evidence before modifying SUID binaries, services, scheduled jobs, credentials, container configuration, filesystem resources, or kernel state.
