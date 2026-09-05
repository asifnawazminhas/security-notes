# Linux Privilege Escalation

Linux privilege escalation is the process of identifying weaknesses that allow a user, service account, or application context to obtain permissions beyond those originally assigned.

During an authorised assessment, the objective is not simply to become `root`.

The objective is to understand the security boundary that failed:

```text
Initial User
     |
     v
Enumeration
     |
     v
Privilege Boundary
     |
     v
Misconfiguration / Vulnerability
     |
     v
Controlled Validation
     |
     v
Higher Privilege
     |
     v
Root Cause
     |
     v
Remediation
```

Privilege escalation should be approached as a structured analysis of:

```text
Identity
Permissions
Sudo
SUID / SGID
Capabilities
Services
Scheduled Tasks
Filesystem
Credentials
Groups
Containers
Kernel
Security Controls
```

---

# 1. Assessment Workflow

A practical Linux privilege escalation workflow is:

```text
Establish Current Context
        |
        v
Enumerate Host
        |
        v
Review Sudo
        |
        v
Review Groups
        |
        v
Review SUID / SGID
        |
        v
Review Capabilities
        |
        v
Review Services
        |
        v
Review Scheduled Tasks
        |
        v
Review Writable Files / Paths
        |
        v
Review Credentials
        |
        v
Review Containers
        |
        v
Review Kernel / Software
        |
        v
Prioritise Candidates
        |
        v
Validate Safely
        |
        v
Document Root Cause
```

Start with configuration weaknesses before considering software or kernel exploitation.

---

# 2. Current Identity

Always establish the starting identity.

```bash
whoami
```

```bash
id
```

Example:

```text
uid=1001 analyst
gid=1001 analyst
groups=1001 analyst,27 sudo,998 docker
```

Record:

```text
Username
UID
Primary group
Supplementary groups
```

Group membership can significantly change the effective security context.

---

# 3. Current Groups

```bash
groups
```

or:

```bash
id -nG
```

Interesting groups can include:

```text
sudo
wheel
docker
lxd
libvirt
disk
adm
systemd-journal
shadow
backup
www-data
```

A group name alone does not prove privilege escalation.

Determine what resources the group can actually access.

---

# 4. Root

The Linux superuser normally has:

```text
UID 0
```

Check:

```bash
getent passwd | awk -F: '$3 == 0 {print $1 ":" $3 ":" $6 ":" $7}'
```

Normally this should identify:

```text
root
```

Unexpected additional UID 0 accounts deserve investigation.

---

# 5. OS Information

```bash
cat /etc/os-release
```

Kernel:

```bash
uname -a
```

Architecture:

```bash
uname -m
```

Kernel release:

```bash
uname -r
```

This information becomes important when evaluating:

```text
Kernel vulnerabilities
Distribution-specific configuration
Installed package versions
Security features
```

---

# 6. Host Context

```bash
hostname
```

```bash
hostnamectl 2>/dev/null
```

Current time:

```bash
date
```

Uptime:

```bash
uptime
```

Virtualisation:

```bash
systemd-detect-virt 2>/dev/null
```

Understanding whether the system is:

```text
Physical
Virtual machine
Container
Cloud workload
```

can change the privilege escalation model.

---

# 7. Environment

```bash
env | sort
```

Important variables can include:

```text
PATH
HOME
SHELL
USER
LOGNAME
LD_LIBRARY_PATH
PYTHONPATH
PERL5LIB
SUDO_USER
SUDO_COMMAND
```

Environment variables can influence privileged programs when improperly trusted.

---

# 8. PATH

```bash
echo "$PATH"
```

Split into individual entries:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Check each directory:

```bash
printf '%s\n' "$PATH" | tr ':' '\n' | while read -r d; do [ -n "$d" ] && ls -ld "$d" 2>/dev/null; done
```

A writable directory in a privileged execution path can become significant when a privileged script or service invokes a program without an absolute path.

---

# 9. Empty PATH Entries

An empty PATH entry can represent the current working directory in some execution contexts.

Inspect:

```bash
printf '%s\n' "$PATH" | tr ':' '\n' | nl -ba
```

Security-sensitive scripts should use controlled PATH values and absolute command paths.

---

# 10. Sudo

One of the first checks should be:

```bash
sudo -l
```

This displays commands the current user may execute through `sudo`.

Possible output:

```text
User analyst may run the following commands:
    (root) /usr/bin/systemctl status *
```

Review:

```text
Command
Run-as user
Arguments
Wildcards
Environment
NOPASSWD
SETENV
```

---

# 11. Sudo Without Password

Example:

```text
(root) NOPASSWD: /usr/bin/example
```

`NOPASSWD` means sudo does not require the user's password for the specified rule.

It does not automatically mean the command is exploitable.

The security question is:

```text
Can the permitted command perform actions beyond the intended administrative task?
```

---

# 12. Sudo Rule Components

A sudo rule can contain:

```text
User
Host
RunAs
Command
Arguments
Tags
```

Example:

```text
analyst ALL=(root) NOPASSWD: /usr/bin/systemctl status nginx
```

This is much narrower than:

```text
analyst ALL=(ALL) NOPASSWD: ALL
```

---

# 13. Sudoers Files

Main configuration:

```text
/etc/sudoers
```

Additional configuration:

```text
/etc/sudoers.d/
```

Where readable:

```bash
ls -la /etc/sudoers.d 2>/dev/null
```

Do not modify sudo configuration during routine testing.

---

# 14. Sudo Version

```bash
sudo --version
```

Do not conclude vulnerability based solely on a version number.

Distribution packages frequently contain backported security patches.

Confirm:

```text
Distribution
Package version
Vendor advisory
Patch status
Configuration
```

---

# 15. Sudo Wildcards

Rules containing wildcards deserve careful review.

Example concept:

```text
/usr/bin/example *
```

Wildcards can sometimes allow additional arguments or unexpected file selection.

Whether this is dangerous depends entirely on how the allowed program processes those arguments.

---

# 16. Sudo Environment

Inspect:

```bash
sudo -V
```

Relevant sudo configuration can control:

```text
env_reset
env_keep
secure_path
setenv
```

Environment preservation can matter when privileged programs trust attacker-controlled environment variables.

---

# 17. `SETENV`

A sudo rule using:

```text
SETENV
```

may permit environment variables to be supplied to the permitted command.

This becomes important when the target program interprets security-sensitive variables.

Do not assume `SETENV` alone provides escalation.

---

# 18. Sudo Program Behaviour

When evaluating an allowed command, determine whether it can:

```text
Launch another program
Load a configuration file
Write arbitrary files
Read arbitrary files
Invoke an editor
Execute plugins
Execute scripts
Load libraries
Run shell commands
Control a service
Change permissions
```

This behavioural analysis is more important than the command name.

---

# 19. GTFOBins

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

GTFOBins documents Unix binaries whose legitimate functionality can sometimes be abused when combined with security-sensitive configurations such as:

```text
Sudo
SUID
Capabilities
```

Treat GTFOBins as a reference.

Always verify that:

```text
The exact binary exists
The relevant feature exists
The security context matches
The behaviour is authorised to test
```

---

# 20. SUID

SUID allows an executable to run with the effective user ID of its owner.

Find SUID files:

```bash
find / -xdev -perm -4000 -type f -print 2>/dev/null
```

Common legitimate examples may include:

```text
/usr/bin/passwd
/usr/bin/su
/usr/bin/mount
```

depending on the distribution.

---

# 21. SUID Permission

Example:

```text
-rwsr-xr-x
```

The:

```text
s
```

in the owner execute position indicates SUID.

Check:

```bash
stat /path/to/binary
```

---

# 22. SUID Ownership

For privilege escalation to root, a particularly interesting case is:

```text
root-owned SUID executable
```

Check:

```bash
find / -xdev -uid 0 -perm -4000 -type f -ls 2>/dev/null
```

Not every root-owned SUID binary is vulnerable.

---

# 23. Unusual SUID Files

Prioritise:

```text
Custom binaries
Files under /opt
Files under /usr/local
Unexpected copies of interpreters
Unexpected administrative utilities
Recently modified binaries
```

Example:

```bash
find / -xdev -perm -4000 -type f -printf '%TY-%Tm-%Td %TH:%TM %u %g %m %p\n' 2>/dev/null | sort
```

---

# 24. SUID Analysis

For an unfamiliar SUID program:

```bash
file /path/to/binary
```

```bash
stat /path/to/binary
```

```bash
ldd /path/to/binary 2>/dev/null
```

```bash
strings /path/to/binary | less
```

Static analysis can reveal:

```text
Referenced commands
Configuration paths
Library names
Temporary files
Error messages
Environment variables
```

Do not modify the binary.

---

# 25. SUID PATH Risk

Consider a privileged program that internally performs:

```text
backup
```

instead of:

```text
/usr/local/bin/backup
```

If the execution environment searches a user-writable directory first, command resolution can become unsafe.

The root cause is:

```text
Privileged Program
       +
Untrusted PATH
       +
Relative Command Execution
```

---

# 26. SUID Environment Risk

Privileged binaries should not trust unvalidated user-controlled input such as:

```text
Environment variables
Configuration paths
File paths
Temporary filenames
Plugin paths
```

Modern runtime loaders intentionally restrict many dangerous variables for privileged execution.

Do not assume historical environment-variable techniques still apply.

---

# 27. SGID

Find SGID files:

```bash
find / -xdev -perm -2000 -type f -print 2>/dev/null
```

SGID executables run with the effective group ID of their owning group.

This can expose:

```text
Restricted files
Administrative resources
Service data
Sensitive sockets
```

---

# 28. SUID and SGID Combined Search

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

Use manual review to separate expected system binaries from unusual files.

---

# 29. File Capabilities

Linux capabilities divide traditional root privileges into individual units.

Enumerate:

```bash
getcap -r / 2>/dev/null
```

Example:

```text
/usr/bin/example cap_net_raw=ep
```

---

# 30. Capabilities

Interesting capabilities can include:

```text
CAP_SETUID
CAP_SETGID
CAP_DAC_OVERRIDE
CAP_DAC_READ_SEARCH
CAP_SYS_ADMIN
CAP_SYS_PTRACE
CAP_SYS_CHROOT
CAP_NET_ADMIN
CAP_NET_RAW
```

Impact depends on:

```text
Binary
Capability
Execution context
Kernel
Namespaces
Application behaviour
```

---

# 31. Capability Documentation

Capabilities are documented in:

```bash
man 7 capabilities
```

Online reference:

[capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }

---

# 32. Capability Evidence

```bash
getcap /path/to/binary
```

Then:

```bash
stat /path/to/binary
```

```bash
file /path/to/binary
```

Record the exact capability set rather than merely stating that the binary has capabilities.

---

# 33. `CAP_SETUID`

`CAP_SETUID` can permit manipulation of process user IDs.

A program possessing this capability deserves careful review.

However:

```text
CAP_SETUID
```

does not mean every binary automatically provides a path to UID 0.

The program's behaviour matters.

---

# 34. `CAP_DAC_OVERRIDE`

This capability can bypass discretionary file read, write, and execute permission checks in many circumstances.

A custom executable possessing it may expose sensitive files or allow modification of protected resources.

Validate actual program functionality.

---

# 35. `CAP_DAC_READ_SEARCH`

This capability can bypass certain file read and directory search permission checks.

It can create credential exposure risk when assigned to inappropriate programs.

---

# 36. `CAP_SYS_ADMIN`

`CAP_SYS_ADMIN` covers a broad range of privileged operations.

Its presence should receive significant scrutiny.

Linux documentation describes it as an overloaded capability with extensive privilege.

---

# 37. `CAP_SYS_PTRACE`

This capability can allow tracing of processes under relevant security conditions.

Potential impact includes access to sensitive process state.

Do not dump process memory or credentials unless explicitly authorised.

---

# 38. Running Processes

```bash
ps aux
```

More detail:

```bash
ps -eo user,pid,ppid,etimes,comm,args
```

Look for:

```text
Root processes
Custom applications
Backup tools
Monitoring agents
Container runtimes
Databases
Management software
Scripts
```

---

# 39. Process Tree

```bash
ps -ef --forest
```

or:

```bash
pstree -ap 2>/dev/null
```

This helps identify relationships between:

```text
Privileged daemon
Worker
Script
Child process
```

---

# 40. Root Processes

```bash
ps -U root -u root -o user,pid,ppid,comm,args
```

Prioritise unusual or organisation-specific software rather than standard operating-system daemons.

---

# 41. Services

List running services:

```bash
systemctl --type=service --state=running --no-pager
```

List service files:

```bash
systemctl list-unit-files --type=service --no-pager
```

Detailed service assessment is covered in [Linux Services](services.md).

---

# 42. Custom Services

Prioritise:

```text
/etc/systemd/system/
/usr/local/lib/systemd/system/
/opt/
/usr/local/bin/
```

List custom unit files:

```bash
find /etc/systemd/system -type f -maxdepth 3 -print 2>/dev/null
```

---

# 43. Service Configuration

```bash
systemctl cat example.service
```

Review:

```ini
User=
Group=
ExecStart=
ExecStartPre=
ExecStartPost=
Environment=
EnvironmentFile=
WorkingDirectory=
```

Determine which files and directories are writable by the current user.

---

# 44. Service Executable

If a root service executes:

```text
/opt/application/bin/service
```

inspect:

```bash
stat -c '%A %a %U %G %n' /opt/application/bin/service
```

and:

```bash
namei -l /opt/application/bin/service
```

---

# 45. Writable Root Service Binary

A high-risk pattern is:

```text
Root Service
     |
     v
Executes Binary
     |
     v
Binary Writable by Standard User
```

This represents a broken privilege boundary.

Do not overwrite the production binary merely to demonstrate impact.

Permission evidence plus service configuration may be sufficient.

---

# 46. Writable Service Script

The same applies to:

```text
Shell scripts
Python scripts
Perl scripts
Ruby scripts
Node.js files
Configuration-generated scripts
```

If a privileged service executes a user-writable script, the script becomes part of the privileged trust boundary.

---

# 47. Parent Directory

Even if the executable itself is not writable:

```bash
namei -l /opt/application/bin/service
```

A writable parent directory may allow:

```text
Replacement
Rename
Path manipulation
```

depending on ownership and filesystem semantics.

---

# 48. Service Environment Files

Example:

```ini
EnvironmentFile=/etc/example/example.env
```

Check:

```bash
stat -c '%A %a %U %G %n' /etc/example/example.env
```

Writable configuration can sometimes influence privileged service behaviour.

---

# 49. Service Restart Requirement

A service weakness may require:

```text
Restart
Reload
Reboot
Crash
Scheduled restart
```

Determine whether the current user can trigger the required action.

A writable service file with no realistic activation path may have lower immediate exploitability.

---

# 50. Scheduled Tasks

Linux scheduling mechanisms include:

```text
cron
systemd timers
at
Application schedulers
```

Scheduled privileged execution is a common trust boundary.

---

# 51. System Cron

```bash
cat /etc/crontab 2>/dev/null
```

```bash
ls -la /etc/cron.d 2>/dev/null
```

```bash
ls -la /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly 2>/dev/null
```

---

# 52. User Crontab

```bash
crontab -l 2>/dev/null
```

Root's crontab may not be readable without privilege.

Do not attempt to bypass permissions.

---

# 53. Cron Trust Boundary

Example:

```text
root cron
    |
    v
/opt/backup/backup.sh
    |
    v
Writable by analyst
```

This can represent privilege escalation because the lower-privileged user controls code executed by root.

---

# 54. Cron Script Permissions

```bash
stat -c '%A %a %U %G %n' /opt/backup/backup.sh
```

Parent path:

```bash
namei -l /opt/backup/backup.sh
```

ACL:

```bash
getfacl /opt/backup/backup.sh
```

---

# 55. Cron PATH

System cron configuration may define:

```text
PATH=
```

Review:

```bash
grep -n '^PATH=' /etc/crontab /etc/cron.d/* 2>/dev/null
```

A privileged scheduled task using relative command names with a writable PATH directory can create risk.

---

# 56. Cron Wildcards

Scheduled commands containing wildcards deserve manual review.

Example concept:

```text
archive *
```

Some command-line utilities interpret specially named files as options.

Whether this is exploitable depends on:

```text
Exact utility
Working directory
File ownership
Command syntax
Privilege context
```

Do not assume every wildcard is vulnerable.

---

# 57. systemd Timers

List:

```bash
systemctl list-timers --all --no-pager
```

Inspect a timer:

```bash
systemctl cat example.timer
```

Then inspect the associated service:

```bash
systemctl cat example.service
```

---

# 58. Timer Analysis

Determine:

```text
Timer schedule
Associated service
Service user
Executed binary
Executed scripts
Writable dependencies
```

A timer itself may be secure while the associated service executes a writable file.

---

# 59. `at`

Where available:

```bash
atq 2>/dev/null
```

Scheduled `at` jobs are another potential execution source.

Do not remove or alter jobs.

---

# 60. Writable Files

A broad writable-file search can generate huge output.

Prefer targeted locations:

```bash
find /etc /opt /usr/local /srv -writable -ls 2>/dev/null
```

Review carefully.

---

# 61. Writable Directories

```bash
find /etc /opt /usr/local /srv -type d -writable -ls 2>/dev/null
```

A writable directory matters when a privileged process:

```text
Executes files from it
Loads configuration from it
Loads libraries from it
Processes attacker-controlled files from it
```

Writable alone is not necessarily a vulnerability.

---

# 62. World-Writable Directories

```bash
find / -xdev -type d -perm -0002 -ls 2>/dev/null
```

Common legitimate examples include:

```text
/tmp
/var/tmp
```

These usually rely on the sticky bit.

---

# 63. Sticky Bit

Example:

```text
drwxrwxrwt
```

The final:

```text
t
```

is the sticky bit.

Check:

```bash
stat -c '%A %a %U %G %n' /tmp
```

---

# 64. World-Writable Without Sticky Bit

Search:

```bash
find / -xdev -type d -perm -0002 ! -perm -1000 -ls 2>/dev/null
```

These directories deserve additional review.

Impact depends on what privileged processes use them.

---

# 65. ACLs

Traditional mode bits do not show the complete access model.

Use:

```bash
getfacl /path/to/file
```

Example:

```text
user:analyst:rw-
```

An ACL can grant access that is not obvious from the basic owner/group mode.

---

# 66. Path Permissions

Use:

```bash
namei -l /path/to/file
```

This displays permissions for every component of the path.

It is particularly useful for:

```text
Service executables
Cron scripts
Configuration files
Libraries
Credential files
```

---

# 67. `/etc/passwd`

Check:

```bash
ls -l /etc/passwd
```

Normally it is world-readable but should not be writable by standard users.

Test:

```bash
test -w /etc/passwd && echo "Writable" || echo "Not writable"
```

Do not modify it.

---

# 68. `/etc/shadow`

```bash
ls -l /etc/shadow
```

Standard users should not normally be able to read or write the shadow password database.

Test without displaying contents:

```bash
test -r /etc/shadow && echo "Readable" || echo "Not readable"
```

```bash
test -w /etc/shadow && echo "Writable" || echo "Not writable"
```

---

# 69. Sensitive System Files

Other high-value paths include:

```text
/etc/sudoers
/etc/sudoers.d/
/etc/ssh/sshd_config
/root/
/etc/systemd/system/
/etc/cron.d/
```

Unexpected write access can have significant impact.

---

# 70. Credentials

Credential exposure can provide:

```text
Another local account
Service account
Sudo-capable user
Root-equivalent identity
Remote administrative access
```

Detailed discovery is covered in [Linux Credentials](credentials.md).

---

# 71. Shell History

Check:

```bash
grep -Ei 'sudo|su |ssh|pass|password|secret|token' ~/.bash_history 2>/dev/null
```

Do not reproduce discovered credentials in reports.

---

# 72. SSH Keys

```bash
ls -la ~/.ssh 2>/dev/null
```

Potential impact depends on:

```text
Key owner
Authorised destinations
Passphrase protection
Agent availability
Remote account privileges
```

Do not assume a private key provides root access.

---

# 73. Application Credentials

Target:

```text
.env
Database configuration
Service EnvironmentFile
Deployment scripts
Backup scripts
Cloud configuration
```

If a credential belongs to a more privileged local identity, carefully determine whether legitimate authentication is possible and authorised.

---

# 74. Groups

Certain groups may provide significant privileges.

Always enumerate:

```bash
id
```

Then investigate the actual resources controlled by each group.

---

# 75. `docker` Group

Check:

```bash
getent group docker
```

Socket:

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

Docker documentation warns that the `docker` group grants root-level privileges.

[Docker daemon attack surface](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }

Membership should therefore be treated as a highly privileged assignment.

---

# 76. Docker Context

Where authorised:

```bash
docker info 2>/dev/null
```

```bash
docker ps 2>/dev/null
```

If these work as a standard user, document the Docker access.

Do not launch privileged containers merely to prove root-equivalent impact unless explicit validation is required.

---

# 77. `lxd` Group

Check:

```bash
getent group lxd 2>/dev/null
```

LXD management access can be highly privileged because containers can be configured with host resources.

Review membership and daemon access.

---

# 78. `disk` Group

```bash
getent group disk 2>/dev/null
```

Members may have access to raw block devices depending on device permissions.

Raw disk access can bypass normal filesystem protections.

Do not read raw disks merely to demonstrate impact.

---

# 79. `shadow` Group

```bash
getent group shadow 2>/dev/null
```

Membership may grant access to password-hash material depending on distribution configuration.

Validate permissions rather than assuming access.

---

# 80. `adm` Group

```bash
getent group adm 2>/dev/null
```

This commonly provides access to logs on Debian-derived systems.

Logs can contain sensitive information but `adm` membership does not inherently equal root.

---

# 81. `systemd-journal` Group

```bash
getent group systemd-journal 2>/dev/null
```

This may provide broad journal access.

Potential exposure can include:

```text
Application errors
Command output
Authentication events
Environment information
```

---

# 82. `libvirt` Group

```bash
getent group libvirt 2>/dev/null
```

Virtualisation management permissions deserve careful analysis.

Actual privilege depends on:

```text
libvirt configuration
Polkit
Socket permissions
Hypervisor
Available storage
```

---

# 83. Sockets

List Unix sockets:

```bash
ss -lxnp 2>/dev/null
```

Interesting sockets may belong to:

```text
Docker
Containerd
Podman
Libvirt
Databases
Management agents
Custom root services
```

Socket permissions can create privileged interfaces.

---

# 84. Socket Permissions

Find Unix sockets:

```bash
find /run /var/run -type s -ls 2>/dev/null
```

For a candidate:

```bash
stat -c '%A %a %U %G %n' /run/example.sock
```

Determine what operations the service exposes.

---

# 85. Privileged Local APIs

A root daemon may expose a local socket to a lower-privileged group.

This is not automatically insecure.

The service may implement its own authorisation.

Assess:

```text
Filesystem access
Protocol authentication
Available operations
Privilege of daemon
```

---

# 86. D-Bus

Linux systems may expose privileged operations over D-Bus.

List system bus names:

```bash
busctl list 2>/dev/null
```

or:

```bash
gdbus introspect --system --dest org.freedesktop.systemd1 --object-path /org/freedesktop/systemd1 2>/dev/null
```

Do not invoke privileged methods unless needed and authorised.

---

# 87. Polkit

Polkit controls authorisation for many system services.

Installed version:

```bash
pkaction --version 2>/dev/null
```

Available actions:

```bash
pkaction 2>/dev/null
```

Local policies and rules deserve review when unusual administrative actions are available to standard users.

---

# 88. Polkit Rules

Common locations include:

```text
/etc/polkit-1/rules.d/
/usr/share/polkit-1/rules.d/
/usr/share/polkit-1/actions/
```

List:

```bash
find /etc/polkit-1 /usr/share/polkit-1 -maxdepth 3 -type f -print 2>/dev/null
```

Prioritise custom organisation-specific rules.

---

# 89. NFS

Mounted filesystems:

```bash
findmnt
```

NFS mounts:

```bash
findmnt -t nfs,nfs4
```

NFS configuration can affect privilege boundaries.

---

# 90. NFS Exports

Where readable:

```bash
cat /etc/exports 2>/dev/null
```

Relevant options can include:

```text
root_squash
no_root_squash
rw
ro
```

Do not assume a local export configuration is reachable externally.

---

# 91. `root_squash`

NFS normally uses `root_squash` to prevent remote root from automatically retaining root identity on the exported filesystem.

A `no_root_squash` export deserves review when:

```text
Untrusted client can mount export
+
Client root can create privileged files
+
Those files are later trusted by the server
```

---

# 92. Mount Options

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

Security-relevant options include:

```text
nosuid
nodev
noexec
ro
rw
```

These options can reduce certain filesystem-based attack paths.

---

# 93. SUID on Mounted Filesystems

The:

```text
nosuid
```

mount option prevents SUID and SGID bits from taking effect on that filesystem.

Always consider mount options before assuming a SUID file is effective.

---

# 94. `noexec`

`noexec` restricts direct execution from a filesystem.

It is a hardening control, not a complete security boundary against every interpreter or execution mechanism.

Do not describe it as preventing all code execution.

---

# 95. Shared Filesystems

Check:

```bash
df -hT
```

and:

```bash
findmnt
```

Shared storage can introduce:

```text
Cross-user write access
NFS trust
Container mounts
Application data manipulation
Backup interactions
```

---

# 96. Temporary Files

Privileged applications should create temporary files securely.

Review custom applications for use of predictable files under:

```text
/tmp
/var/tmp
```

Potential issues include:

```text
Symlink attacks
Race conditions
File replacement
Insecure permissions
```

Do not create disruptive race conditions on production systems.

---

# 97. Temporary File Evidence

If a root process creates a predictable temporary file:

```bash
ls -la /tmp
```

Document:

```text
Filename
Owner
Permissions
Creation pattern
Privileged consumer
```

Avoid replacing the file merely to prove exploitability.

---

# 98. Symlinks

Inspect:

```bash
readlink -f /path/to/file
```

and:

```bash
ls -l /path/to/file
```

Privileged programs should safely handle attacker-controlled symbolic links when writing files.

---

# 99. Backup Processes

Search processes:

```bash
ps -ef | grep -Ei '[b]ackup|[r]sync|[t]ar|[b]org|[r]estic'
```

Scheduled backup scripts often run with high privileges and interact with writable directories.

---

# 100. Backup Configuration

Potential locations:

```text
/etc/
/opt/
/usr/local/
/srv/
/root/
```

Determine:

```text
Who runs backup?
What files are processed?
Where is output written?
Which scripts are executed?
Which credentials are used?
```

---

# 101. Tar and Archive Jobs

Privileged archive jobs deserve review when they process attacker-controlled directories.

The important elements are:

```text
Archive utility
Arguments
Wildcard use
Working directory
File ownership
Privilege
```

Do not assume every tar wildcard creates an escalation path.

---

# 102. Log Rotation

Configuration:

```bash
ls -la /etc/logrotate.d 2>/dev/null
```

Inspect custom entries:

```bash
grep -RniE 'postrotate|prerotate|firstaction|lastaction' /etc/logrotate.conf /etc/logrotate.d 2>/dev/null
```

Privileged scripts referenced by logrotate should not be writable by untrusted users.

---

# 103. Writable Logrotate Scripts

For a referenced script:

```bash
stat -c '%A %a %U %G %n' /path/to/script
```

and:

```bash
namei -l /path/to/script
```

Activation timing should also be established.

---

# 104. Package Managers

Package management is normally privileged.

Check whether the user has sudo access to:

```text
apt
apt-get
dpkg
dnf
yum
rpm
pacman
```

Package managers can perform installation scripts and modify trusted system paths.

Broad sudo access to package-management tooling should be carefully reviewed.

---

# 105. Editors

Sudo access to editors can be dangerous because many editors support:

```text
Shell commands
Plugins
External filters
File writes
Configuration loading
```

Examples include:

```text
vim
vi
nano
less
```

Capabilities vary.

Review the exact binary and sudo rule.

---

# 106. Interpreters

Sudo or SUID access to interpreters deserves particular attention:

```text
python
python3
perl
ruby
php
node
bash
sh
```

General-purpose interpreters can execute arbitrary code by design.

A root sudo rule granting unrestricted interpreter execution is effectively broad privileged code execution.

---

# 107. Compilers

Compilers and build systems can also execute helper programs or build-time commands.

Examples:

```text
gcc
make
cmake
```

Assess unrestricted privileged execution carefully.

---

# 108. File Utilities

Some utilities can:

```text
Read arbitrary files
Write arbitrary files
Invoke editors
Invoke shell commands
Load plugins
```

Do not judge sudo safety solely by whether a binary appears harmless.

Review its full functionality.

---

# 109. Dynamic Libraries

Inspect executable dependencies:

```bash
ldd /path/to/binary
```

This can reveal dynamically loaded libraries.

A privileged custom program loading libraries from a user-writable location may create a security issue.

---

# 110. Library Path Permissions

For a library:

```bash
stat -c '%A %a %U %G %n' /path/to/library.so
```

Parent path:

```bash
namei -l /path/to/library.so
```

Do not replace shared libraries during routine validation.

---

# 111. `ldconfig`

Configuration:

```bash
cat /etc/ld.so.conf 2>/dev/null
```

Additional paths:

```bash
grep -RhvE '^\s*(#|$)' /etc/ld.so.conf.d 2>/dev/null
```

Cache:

```bash
ldconfig -p 2>/dev/null | head
```

Trusted library directories should not be writable by standard users.

---

# 112. `LD_LIBRARY_PATH`

```bash
echo "$LD_LIBRARY_PATH"
```

The dynamic loader applies restrictions to security-sensitive execution contexts.

Do not assume user-controlled `LD_LIBRARY_PATH` affects SUID programs.

It can still matter for incorrectly configured sudo or custom privileged execution.

---

# 113. `LD_PRELOAD`

```bash
echo "$LD_PRELOAD"
```

System configuration:

```bash
cat /etc/ld.so.preload 2>/dev/null
```

`/etc/ld.so.preload` is security-sensitive because listed libraries can be loaded broadly.

Unexpected write access is high risk.

---

# 114. Python Import Paths

```bash
python3 - <<'PY'
import sys
for path in sys.path:
    print(path)
PY
```

A privileged Python script importing modules from a user-writable location can create module-hijacking risk.

---

# 115. Python Script Analysis

For a privileged script, inspect imports:

```bash
grep -nE '^(import|from) ' /path/to/script.py
```

Then determine module resolution and permissions.

Do not create malicious replacement modules on production systems unless explicit validation requires it.

---

# 116. Python Module Location

Example:

```bash
python3 -c 'import module_name; print(module_name.__file__)'
```

Replace `module_name` with the actual module.

The interpreter used by the privileged process must match the interpreter used for testing.

---

# 117. Custom Scripts

Search common administrative locations:

```bash
find /opt /usr/local /srv -type f \( -name '*.sh' -o -name '*.py' -o -name '*.pl' -o -name '*.rb' \) -ls 2>/dev/null
```

Prioritise scripts referenced by:

```text
Root services
Cron
Sudo
Backups
Monitoring
Deployment
```

---

# 118. Script Permissions

For each high-value script:

```bash
stat -c '%A %a %U %G %n' /path/to/script
```

```bash
getfacl /path/to/script
```

```bash
namei -l /path/to/script
```

---

# 119. Script Command Resolution

Search shell scripts for command execution:

```bash
grep -nE '(^|[;&|[:space:]])(cp|mv|tar|rsync|curl|wget|python|python3|bash|sh|find|awk|sed)([[:space:]]|$)' /path/to/script.sh
```

Manual review is still required.

---

# 120. Script Input

Determine whether privileged scripts consume:

```text
User-controlled filenames
Environment variables
Configuration
Arguments
Directory contents
Network input
Database values
```

Input reaching command execution or filesystem operations can become security-sensitive.

---

# 121. Shell Injection

A privileged shell script that incorporates untrusted input into shell commands can create command-injection risk.

The correct remediation is generally:

```text
Avoid unsafe shell evaluation
Quote variables correctly
Validate input
Use safer APIs
Reduce privilege
```

Do not execute destructive payloads to prove the issue.

---

# 122. `eval`

Search custom shell scripts:

```bash
grep -RniE '(^|[[:space:]])eval([[:space:]]|$)' /opt /usr/local /srv 2>/dev/null
```

`eval` is not automatically vulnerable.

Its safety depends on whether untrusted data reaches it.

---

# 123. Writable Configuration

Privileged applications may load:

```text
YAML
JSON
INI
XML
Environment files
Shell fragments
Plugin configuration
```

Writable configuration can influence privileged behaviour even when the executable itself is protected.

---

# 124. Plugin Directories

Search application configuration for terms such as:

```bash
grep -RniE 'plugin|module|extension|include|load' /opt/application 2>/dev/null
```

A root application loading plugins from a user-writable directory can create a privilege boundary failure.

---

# 125. `/etc/profile`

Inspect permissions:

```bash
stat -c '%A %a %U %G %n' /etc/profile
```

Additional shell configuration:

```bash
ls -la /etc/profile.d 2>/dev/null
```

Unexpected write access deserves review.

---

# 126. User Shell Startup Files

Examples:

```text
~/.bashrc
~/.profile
~/.bash_profile
~/.zshrc
```

These normally affect only the user's own sessions.

They become more important if a privileged automation process incorrectly sources a lower-privileged user's shell configuration.

---

# 127. Root Shell Configuration

Paths under:

```text
/root/
```

should not be accessible to ordinary users beyond intended permissions.

Do not attempt to access `/root` through bypass techniques during routine enumeration.

---

# 128. SSH Configuration

System SSH configuration:

```bash
sshd -T 2>/dev/null | head
```

or:

```bash
grep -RniE '^(PermitRootLogin|PasswordAuthentication|AuthorizedKeysFile|AllowUsers|AllowGroups)' /etc/ssh/sshd_config /etc/ssh/sshd_config.d 2>/dev/null
```

SSH hardening weaknesses are not necessarily local privilege escalation paths.

Keep remote access and local escalation findings distinct.

---

# 129. Writable `authorized_keys`

If a lower-privileged user can write another account's:

```text
authorized_keys
```

this may allow authentication as that account where SSH is enabled and configuration permits it.

Check permissions without modifying the file.

---

# 130. PAM

PAM configuration:

```bash
ls -la /etc/pam.d
```

PAM modules and configuration participate in authentication.

Unexpected write access to PAM configuration or loaded modules can have severe impact.

Do not modify authentication configuration during routine testing.

---

# 131. PAM Modules

Common module locations vary by architecture and distribution.

Find configured modules:

```bash
grep -RhE 'pam_[A-Za-z0-9_-]+\.so' /etc/pam.d 2>/dev/null | sort -u
```

Custom PAM modules deserve scrutiny.

---

# 132. Kernel

Kernel vulnerabilities should generally be evaluated after configuration-based paths.

Collect:

```bash
uname -r
```

```bash
uname -a
```

Distribution:

```bash
cat /etc/os-release
```

---

# 133. Kernel Exploit Assessment

Do not use:

```text
Kernel version
      |
      v
Search exploit
      |
      v
Immediately execute
```

Use:

```text
Kernel / Distribution
       |
       v
Vendor Patch Status
       |
       v
Vulnerability Preconditions
       |
       v
Mitigations
       |
       v
Exploit Reliability
       |
       v
Operational Risk
       |
       v
Controlled Decision
```

---

# 134. Distribution Backports

A kernel version may appear vulnerable based on upstream version comparisons while the distribution has backported the fix.

Always check vendor security advisories.

Examples:

- [Debian Security](https://www.debian.org/security/){ target="_blank" rel="noopener noreferrer" }
- [Ubuntu Security](https://ubuntu.com/security){ target="_blank" rel="noopener noreferrer" }
- [Red Hat Security](https://access.redhat.com/security/){ target="_blank" rel="noopener noreferrer" }

---

# 135. Installed Kernel Package

Debian-based:

```bash
dpkg-query -W 'linux-image*' 2>/dev/null
```

RPM-based:

```bash
rpm -qa | grep '^kernel' 2>/dev/null
```

Compare the actual package with vendor advisories.

---

# 136. Kernel Exploit Risk

Kernel exploitation can cause:

```text
Kernel panic
System crash
Filesystem corruption
Service interruption
Unpredictable state
```

Avoid kernel exploitation on production systems unless specifically authorised and necessary.

---

# 137. Kernel Hardening

Useful indicators include:

```text
ASLR
Yama
SELinux
AppArmor
seccomp
Capabilities
Namespaces
Lockdown
```

These controls can influence exploitability.

---

# 138. ASLR

Check:

```bash
sysctl kernel.randomize_va_space
```

Typical values:

```text
0 - disabled
1 - partial
2 - full
```

ASLR is exploit mitigation, not a substitute for fixing vulnerabilities.

---

# 139. Yama

Where available:

```bash
sysctl kernel.yama.ptrace_scope 2>/dev/null
```

This can restrict process tracing.

Do not weaken it for testing.

---

# 140. AppArmor

Status:

```bash
aa-status 2>/dev/null
```

Alternative:

```bash
cat /sys/module/apparmor/parameters/enabled 2>/dev/null
```

AppArmor can restrict applications even when traditional Unix permissions would allow an action.

---

# 141. SELinux

Status:

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

---

# 142. Mandatory Access Control

Privilege assessment should account for:

```text
Traditional UID/GID permissions
+
Capabilities
+
SELinux/AppArmor
+
Namespaces
+
seccomp
```

Obtaining UID 0 inside a constrained environment does not necessarily equal unrestricted host root.

---

# 143. seccomp

For the current shell:

```bash
grep '^Seccomp:' /proc/$$/status
```

Possible values include:

```text
0 - disabled
1 - strict
2 - filter
```

seccomp restricts system calls.

---

# 144. `NoNewPrivileges`

Check:

```bash
grep '^NoNewPrivs:' /proc/$$/status
```

The `no_new_privs` process attribute prevents gaining additional privileges through mechanisms such as SUID or file capabilities after it is set.

---

# 145. systemd Hardening

Inspect:

```bash
systemctl show example.service \
    -p NoNewPrivileges \
    -p PrivateTmp \
    -p ProtectSystem \
    -p ProtectHome \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities
```

These controls can significantly reduce service attack surface.

---

# 146. `systemd-analyze security`

Where available:

```bash
systemd-analyze security example.service
```

This provides a security exposure assessment of systemd sandboxing options.

It is a hardening aid, not proof of vulnerability.

---

# 147. Containers

Determine context:

```bash
systemd-detect-virt
```

Inspect cgroups:

```bash
cat /proc/1/cgroup
```

Container detection can vary by runtime and operating system.

---

# 148. Container Identity

Inside a container, UID 0 may represent:

```text
Container root
```

rather than:

```text
Host root
```

Namespaces can isolate:

```text
Processes
Mounts
Users
Network
IPC
UTS
Cgroups
```

---

# 149. Container Mounts

```bash
findmnt
```

or:

```bash
mount
```

Look for host resources mounted into the container.

Examples:

```text
Docker socket
Host filesystem directories
Device nodes
Configuration
Secrets
```

---

# 150. Container Capabilities

Current process:

```bash
grep '^Cap' /proc/$$/status
```

Where `capsh` exists:

```bash
capsh --print
```

Excessive capabilities can weaken container isolation.

---

# 151. Privileged Containers

A privileged container can have substantially broader host access.

Do not attempt container escape simply because a container appears privileged.

Document:

```text
Capabilities
Devices
Mounts
Runtime configuration
Host interfaces
```

and determine whether controlled validation is necessary.

---

# 152. Docker Socket in Container

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

A host Docker socket mounted inside a container can expose highly privileged daemon control.

This is often sufficient evidence without launching additional containers.

---

# 153. Kubernetes

Potential indicators:

```bash
env | grep '^KUBERNETES_'
```

Service account:

```bash
ls -la /var/run/secrets/kubernetes.io/serviceaccount 2>/dev/null
```

Kubernetes privilege is governed by:

```text
Service account
RBAC
Pod security
Capabilities
Host mounts
Node access
```

---

# 154. Kubernetes Service Account

A pod may legitimately receive a service-account token.

The presence of the token is not itself a vulnerability.

Assess:

```text
Token accessibility
RBAC permissions
Workload need
Token lifetime
Audience
Pod security context
```

---

# 155. Host Mounts

Container workloads with host filesystem mounts deserve review.

Example risk model:

```text
Container User
      |
      v
Writable Host Mount
      |
      v
Host-Trusted File
      |
      v
Host Privilege Boundary
```

Do not modify host files simply to demonstrate impact.

---

# 156. Device Access

List:

```bash
ls -la /dev | head -n 50
```

Container or group access to sensitive block devices can undermine filesystem isolation.

Avoid raw device access unless explicitly authorised.

---

# 157. Namespaces

Current namespaces:

```bash
ls -l /proc/$$/ns
```

PID 1:

```bash
ls -l /proc/1/ns
```

Differences can help establish containerisation or namespace isolation.

---

# 158. User Namespaces

Check:

```bash
sysctl kernel.unprivileged_userns_clone 2>/dev/null
```

Availability varies by distribution.

User namespaces are legitimate functionality and should not automatically be reported as a weakness.

---

# 159. Network Services

Listen sockets:

```bash
ss -lntup
```

Local-only root services may expose privileged functionality.

Prioritise:

```text
127.0.0.1
::1
Unix sockets
High-privilege custom daemons
Management APIs
```

---

# 160. Localhost Services

Example:

```text
127.0.0.1:8080
```

A localhost-only service is not automatically safe.

Determine:

```text
Authentication
Privilege
Available actions
Input validation
```

---

# 161. Databases

Root-owned database services may still implement their own lower-privileged database identities.

Database administrator access does not necessarily equal operating-system root.

Assess boundaries separately.

---

# 162. Management Agents

Potential examples:

```text
Monitoring agents
Backup agents
Configuration management
Cloud agents
Endpoint security
Deployment agents
```

These often run with elevated privileges.

Prioritise custom plugins, scripts, writable configuration, and local control interfaces.

---

# 163. Installed Software

Debian-based:

```bash
dpkg -l
```

RPM-based:

```bash
rpm -qa
```

Look for:

```text
Custom packages
Management software
Backup software
Old third-party applications
Privileged agents
```

---

# 164. Software Version Assessment

Do not automatically report:

```text
Package version is old
```

Instead verify:

```text
Exact package build
Vendor patches
Vulnerability applicability
Configuration
Exposure
Privileges
```

---

# 165. Custom Software

Search:

```bash
find /opt /usr/local -maxdepth 3 -type f -executable -ls 2>/dev/null
```

Custom privileged software deserves greater attention because it may not receive the same security scrutiny as standard distribution packages.

---

# 166. Recently Modified Files

Target privileged locations:

```bash
find /etc /opt /usr/local -type f -mtime -30 -ls 2>/dev/null
```

This can identify recently deployed:

```text
Scripts
Services
Configuration
Custom tools
```

Modification date alone does not indicate malicious or insecure content.

---

# 167. World-Writable Executables

Target trusted locations:

```bash
find /usr/local /opt /srv -type f -executable -perm -0002 -ls 2>/dev/null
```

Then determine whether privileged processes execute them.

---

# 168. Group-Writable Executables

```bash
find /usr/local /opt /srv -type f -executable -perm -0020 -ls 2>/dev/null
```

Compare file group with current user's groups:

```bash
id -nG
```

---

# 169. Ownership

Find files owned by the current user in administrative locations:

```bash
find /etc /opt /usr/local /srv -user "$(id -un)" -ls 2>/dev/null
```

A standard user owning a file executed by root can create a trust problem.

---

# 170. Group Ownership

Determine current groups:

```bash
id -nG
```

Then review group-writable privileged resources.

Do not assume every group-writable file is exploitable.

---

# 171. Open Files

Where available:

```bash
lsof 2>/dev/null | head
```

For a specific root process:

```bash
lsof -p PID 2>/dev/null
```

This can identify:

```text
Configuration
Logs
Libraries
Sockets
Working directories
```

Replace `PID` with the actual process ID.

---

# 172. Deleted Files

```bash
lsof +L1 2>/dev/null
```

Deleted but open files can contain sensitive information.

Do not extract them unless required.

---

# 173. Process Executable

For a process:

```bash
readlink -f /proc/PID/exe
```

Working directory:

```bash
readlink -f /proc/PID/cwd
```

Command line:

```bash
tr '\0' ' ' < /proc/PID/cmdline
```

Access depends on process permissions and security controls.

---

# 174. Process Credentials

```bash
grep -E '^(Uid|Gid|Groups|Cap|NoNewPrivs|Seccomp):' /proc/PID/status
```

This provides useful privilege information without interacting with the process.

---

# 175. `/proc` Restrictions

Security controls may restrict process information.

Examples include:

```text
hidepid
Yama
Namespaces
LSM policies
```

Do not weaken `/proc` protections for enumeration.

---

# 176. Filesystem Attributes

Inspect:

```bash
lsattr /path/to/file 2>/dev/null
```

Attributes such as immutable can influence whether a file can be changed even when traditional permissions suggest otherwise.

---

# 177. Immutable Files

An immutable file may display:

```text
i
```

in `lsattr`.

Changing immutable state generally requires privilege.

Do not treat a writable mode bit as the entire modification model.

---

# 178. Extended Attributes

```bash
getfattr -d /path/to/file 2>/dev/null
```

Extended attributes can store additional metadata.

Use targeted inspection only.

---

# 179. File Ownership vs Effective Control

A file may be root-owned but still effectively controlled by a standard user through:

```text
ACL
Writable parent directory
Writable symlink target
Group membership
Service interface
Configuration generator
```

Assess effective control, not just ownership.

---

# 180. Automated Enumeration

Automation can improve coverage.

Common tools include:

```text
LinPEAS
LinEnum
Linux Smart Enumeration
pspy
```

Automated results should always be manually validated.

---

# 181. LinPEAS

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

LinPEAS can enumerate:

```text
Sudo
SUID
Capabilities
Credentials
Services
Cron
Containers
Writable paths
Kernel information
Interesting files
```

Use only on systems where execution of third-party enumeration tools is authorised.

---

# 182. LinEnum

[LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }

LinEnum provides broad Linux host enumeration.

Treat output as candidate discovery rather than confirmed findings.

---

# 183. Linux Smart Enumeration

[Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

LSE attempts to present Linux privilege escalation information with different verbosity levels.

Manual verification remains necessary.

---

# 184. pspy

[pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }

pspy can help observe processes without requiring root.

It can be useful for discovering:

```text
Cron jobs
Periodic scripts
Backup jobs
Administrative commands
Short-lived processes
```

---

# 185. pspy Use

Use pspy only where introducing third-party binaries is allowed.

Prefer native observation first when possible.

Potentially sensitive command-line arguments may appear in output, so handle logs carefully.

---

# 186. Native Enumeration First

A strong assessment can begin entirely with native commands:

```bash
whoami
id
sudo -l
uname -a
cat /etc/os-release
env
ps -ef
systemctl --type=service --state=running --no-pager
systemctl list-timers --all --no-pager
cat /etc/crontab 2>/dev/null
find / -xdev -perm -4000 -type f -print 2>/dev/null
find / -xdev -perm -2000 -type f -print 2>/dev/null
getcap -r / 2>/dev/null
findmnt
ss -lntup
```

Then investigate specific candidates.

---

# 187. Candidate Prioritisation

A useful priority model is:

```text
Direct Privileged Configuration
        |
        v
Privileged Writable File
        |
        v
Sudo / SUID / Capability
        |
        v
Credential Exposure
        |
        v
Privileged Service Interface
        |
        v
Container / Group Privilege
        |
        v
Application Vulnerability
        |
        v
Kernel Exploit
```

This prioritises lower-risk and more deterministic paths.

---

# 188. Privilege Escalation Candidate Table

| Candidate | What to Verify |
|---|---|
| Sudo | Exact rule and program behaviour |
| SUID | Owner, binary behaviour, environment |
| SGID | Group privilege and accessible resources |
| Capabilities | Exact capability and program behaviour |
| Service | Privilege, executable, config, writable dependencies |
| Cron | User, command, script permissions, activation |
| systemd timer | Associated service and writable dependencies |
| Writable file | Whether privileged process trusts it |
| Writable directory | Whether trusted files can be replaced |
| Credential | Identity, validity, privilege, scope |
| Docker | Daemon access and group membership |
| LXD | Daemon access and configuration |
| Socket | Service privilege and exposed operations |
| Kernel | Patch status, preconditions, risk |

---

# 189. Exploitability Model

A candidate becomes meaningful when:

```text
Lower-Privileged User
        |
        v
Controls Input / File / Interface
        |
        v
Privileged Component Trusts It
        |
        v
Privileged Action Occurs
```

Without the privileged consumer, writable resources may have little security impact.

---

# 190. Validation Strategy

Prefer:

```text
Configuration Evidence
        |
        v
Permission Evidence
        |
        v
Execution Relationship
        |
        v
Minimal Proof
```

rather than:

```text
Modify Production Resource
        |
        v
Wait for Root Execution
```

---

# 191. Non-Destructive Validation

Examples include:

```text
Showing current user membership
Showing sudo rule
Showing writable permission
Showing root service configuration
Showing cron execution relationship
Showing SUID bit
Showing capability
Showing socket permissions
```

These often establish impact without altering the host.

---

# 192. Controlled Proof File

When explicit execution validation is required, use a harmless proof action such as creating a uniquely named file in an approved temporary directory.

Example evidence concept:

```text
/tmp/privilege-validation-<unique-id>
```

The validation should:

```text
Avoid persistent changes
Avoid shell access where unnecessary
Avoid credential modification
Avoid service disruption
Be removed after testing
```

---

# 193. Avoid Unnecessary Root Shells

If the finding can be proven without obtaining an interactive root shell, prefer the less invasive proof.

The assessment objective is:

```text
Demonstrate Security Impact
```

not:

```text
Maximise Control of the Host
```

---

# 194. Do Not Modify Critical Files

Avoid modifying:

```text
/etc/passwd
/etc/shadow
/etc/sudoers
PAM configuration
SSH configuration
System libraries
Production service binaries
Boot configuration
```

unless the engagement explicitly requires such validation and rollback has been agreed.

---

# 195. Service Restart Risk

Restarting production services can cause:

```text
Downtime
Connection loss
Data corruption
Failed transactions
State changes
```

If a weakness requires a service restart, permission and configuration evidence may be enough.

---

# 196. Reboot Risk

Do not reboot systems to activate a privilege escalation path unless explicitly authorised.

Reboot-dependent issues can usually be documented using configuration evidence.

---

# 197. Kernel Exploit Validation

Kernel exploit execution should be treated as a high-risk activity.

Before running one, establish:

```text
Explicit authorisation
Known vulnerable build
Reliable exploit
Rollback plan
System owner approval
Production impact
Crash risk
```

Often the vulnerability can be reported without exploitation.

---

# 198. Credential Validation Risk

Do not broadly reuse discovered credentials.

Use the workflow from [Linux Credentials](credentials.md).

Potential concerns include:

```text
Lockout
MFA
Audit alerts
Cross-system scope
Production access
Sensitive data exposure
```

---

# 199. Root Cause

A strong finding identifies why escalation is possible.

Examples:

```text
Excessive sudo rule
User-writable root service executable
User-writable root cron script
Dangerous file capability
Excessive group membership
Exposed privileged credential
Unpatched local privilege escalation vulnerability
Insecure custom SUID application
Writable privileged configuration
```

---

# 200. Finding Example - Sudo

## Title

```text
Overly Permissive Sudo Rule Allows Privileged Command Execution
```

## Description

```text
The affected user is permitted to execute a utility as root through sudo.
The utility exposes functionality that allows actions outside the intended
administrative purpose of the sudo rule.
```

## Evidence

```text
Current user
sudo -l output
Exact permitted command
Relevant utility functionality
```

## Recommendation

```text
Restrict sudo rules to the minimum commands and arguments required.

Avoid granting privileged access to general-purpose interpreters, editors,
package managers, or utilities capable of executing arbitrary commands.

Use explicit command paths and argument restrictions where appropriate.
```

---

# 201. Finding Example - Service

## Title

```text
Root Service Executes User-Writable File
```

## Description

```text
A systemd service running as root executes a file that can be modified by a
lower-privileged local user.
```

## Evidence

```text
systemctl cat <service>
stat <file>
getfacl <file>
namei -l <file>
id
```

## Impact

```text
A user capable of modifying the trusted file may influence code executed
within the root service context when the service starts.
```

## Recommendation

```text
Ensure service executables, scripts, configuration, libraries, and parent
directories are writable only by trusted administrative identities.

Run the service using a dedicated least-privileged account where root is not
required.
```

---

# 202. Finding Example - Cron

## Title

```text
Privileged Scheduled Task Executes User-Writable Script
```

## Description

```text
A scheduled task executed by root references a script that can be modified by
a lower-privileged user.
```

## Recommendation

```text
Restrict modification of scheduled scripts and their parent directories to
trusted administrators.

Use absolute paths, controlled environments, and dedicated service identities
where possible.
```

---

# 203. Finding Example - Capability

## Title

```text
Excessive Linux Capability Assigned to User-Accessible Executable
```

## Description

```text
A user-accessible executable has been assigned a Linux capability that allows
operations beyond those required by the application's intended function.
```

## Recommendation

```text
Remove unnecessary capabilities and assign only the minimum capabilities
required.

Where possible, redesign the application to avoid privileged capabilities or
isolate the privileged operation behind a narrowly scoped service.
```

---

# 204. Finding Example - SUID

## Title

```text
Custom Root-Owned SUID Application Exposes Privileged Functionality
```

## Description

```text
A custom application executes with the effective UID of root through the SUID
permission and exposes functionality that can be influenced by
lower-privileged users.
```

## Recommendation

```text
Remove SUID where it is not strictly required.

Where privileged functionality is necessary, separate it into a narrowly
scoped component with strict input validation and least privilege.
```

---

# 205. Finding Example - Docker

## Title

```text
Standard User Granted Root-Equivalent Docker Daemon Access
```

## Description

```text
The affected standard user can communicate with the Docker daemon through
membership of the docker group or equivalent socket permissions.
```

## Impact

Docker's own documentation warns that the `docker` group grants root-level privileges.

## Recommendation

```text
Restrict Docker daemon access to trusted administrative users.

Review docker group membership and remove accounts that do not require
container administration.
```

---

# 206. Finding Example - Credentials

## Title

```text
Privileged Service Credentials Accessible to Standard User
```

## Description

```text
A credential used by a higher-privileged service identity is stored in a file
readable by a standard local user.
```

## Recommendation

```text
Restrict credential access to the intended service identity and trusted
administrators.

Rotate the exposed credential and review other locations where it may have
been copied.
```

---

# 207. Finding Example - Kernel

## Title

```text
Linux Kernel Missing Security Update for Local Privilege Escalation Vulnerability
```

## Description

```text
The installed kernel package is affected by a vendor-confirmed local privilege
escalation vulnerability and the relevant security update has not been
installed.
```

Use vendor evidence rather than generic version matching.

## Recommendation

```text
Install the vendor-supported security update and reboot into the corrected
kernel according to the organisation's patch-management process.
```

---

# 208. Remediation Priorities

Common remediation priorities are:

```text
1. Remove unnecessary administrative permissions.

2. Correct ownership and filesystem permissions.

3. Restrict sudo.

4. Remove unnecessary SUID / SGID.

5. Remove excessive capabilities.

6. Protect privileged services and scripts.

7. Protect scheduled tasks.

8. Restrict privileged groups.

9. Protect credentials.

10. Harden containers and daemon sockets.

11. Patch vulnerable software and kernels.

12. Apply defence-in-depth controls.
```

---

# 209. Least Privilege

Services should run as dedicated accounts wherever possible.

Instead of:

```text
root -> web application
```

prefer:

```text
Dedicated Service User
        |
        v
Only Required Files
        |
        v
Only Required Network Access
        |
        v
Only Required Capabilities
```

---

# 210. Filesystem Hardening

Protect:

```text
Service binaries
Scripts
Configuration
Libraries
Cron files
systemd units
Environment files
Credentials
Administrative directories
```

Review both:

```text
File permissions
+
Parent directory permissions
```

---

# 211. Sudo Hardening

Prefer:

```text
Specific command
Specific run-as identity
Specific arguments where practical
Controlled environment
Logging
```

Avoid:

```text
ALL commands
General-purpose shell
General-purpose interpreter
Unrestricted editor
Broad package manager access
```

unless full administrative access is intentional.

---

# 212. SUID Hardening

Review SUID inventory regularly.

Remove SUID from binaries that do not require it.

Where possible consider:

```text
Capabilities
Dedicated services
Polkit
Privilege separation
```

depending on the use case.

---

# 213. Capability Hardening

Use:

```text
Minimum required capability
```

instead of broad privilege.

Avoid unnecessary:

```text
CAP_SYS_ADMIN
CAP_DAC_OVERRIDE
CAP_SETUID
CAP_SYS_PTRACE
```

where application design permits.

---

# 214. Service Hardening

systemd provides controls such as:

```ini
User=
Group=
NoNewPrivileges=
PrivateTmp=
ProtectSystem=
ProtectHome=
CapabilityBoundingSet=
RestrictAddressFamilies=
PrivateDevices=
```

Exact controls depend on application requirements.

---

# 215. Scheduled Task Hardening

Scheduled tasks should:

```text
Use absolute paths
Use protected scripts
Use protected configuration
Use controlled PATH
Run with minimum privilege
Avoid processing attacker-controlled directories unsafely
```

---

# 216. Credential Hardening

Prefer:

```text
Secret manager
Short-lived credential
Dedicated identity
Restricted file permissions
Rotation
Audit logging
```

Avoid:

```text
World-readable configuration
Hardcoded passwords
Credentials in shell history
Credentials in command-line arguments
Shared administrative passwords
```

---

# 217. Container Hardening

Review:

```text
Privileged mode
Capabilities
Host mounts
Device mounts
Docker socket
Host namespaces
Service account
Container user
Read-only filesystem
seccomp
AppArmor / SELinux
```

Avoid unnecessary host-level privileges.

---

# 218. Detection Opportunities

Potential monitoring targets include:

```text
Sudo use
SUID execution
Privilege-changing syscalls
Unexpected root process creation
Sensitive file changes
systemd unit changes
Cron changes
Capability changes
Docker administration
Authentication changes
Kernel exploit indicators
```

---

# 219. Auditd

Where installed:

```bash
systemctl status auditd 2>/dev/null
```

Rules:

```bash
auditctl -l 2>/dev/null
```

Audit configuration can provide visibility into privilege-sensitive activity.

---

# 220. Journal

Recent sudo events may be visible through:

```bash
journalctl _COMM=sudo 2>/dev/null
```

Availability depends on:

```text
Distribution
Logging configuration
Permissions
Retention
```

---

# 221. Authentication Logs

Debian-derived systems may use:

```text
/var/log/auth.log
```

RHEL-derived systems may use:

```text
/var/log/secure
```

Access depends on permissions.

Do not treat absence of one path as absence of authentication logging.

---

# 222. File Integrity Monitoring

High-value files for monitoring can include:

```text
/etc/sudoers
/etc/sudoers.d/
/etc/passwd
/etc/shadow
/etc/systemd/system/
/etc/cron.d/
/usr/local/bin/
/opt/
```

Monitoring should focus on unexpected changes.

---

# 223. Privilege Escalation Evidence

For each candidate record:

```text
Hostname
Current user
UID
Groups
Candidate type
Affected privileged component
File or resource
Owner
Group
Permissions
ACL
Privilege level
Activation mechanism
Validation performed
Result
Root cause
```

---

# 224. Evidence Commands

Identity:

```bash
id
```

Permissions:

```bash
stat -c '%A %a %U %G %n' /path/to/file
```

ACL:

```bash
getfacl /path/to/file
```

Path:

```bash
namei -l /path/to/file
```

Service:

```bash
systemctl cat example.service
```

Capability:

```bash
getcap /path/to/binary
```

Sudo:

```bash
sudo -l
```

---

# 225. Evidence Without Exploitation

Example:

```text
1. id proves analyst is a standard user.

2. systemctl cat proves root executes /opt/app/start.sh.

3. stat proves analyst can write /opt/app/start.sh.

4. namei proves the path is reachable.

5. Service status proves the service is active.
```

This can be enough to demonstrate the privilege boundary failure.

---

# 226. Severity

Severity depends on:

```text
Starting privilege
Reliability
Required interaction
Activation conditions
Resulting privilege
System criticality
Persistence
Detection
Scope
```

A direct deterministic path from a standard user to root will usually be more severe than a theoretical or unreliable candidate.

---

# 227. False Positives

Common false positives include:

```text
SUID binary with no dangerous functionality
Capability on a purpose-built restricted binary
Writable file never consumed by root
Root service with protected dependencies
Old package version with backported patch
Cron script not writable by current user
Docker installed but user cannot access daemon
Credential that is expired
Container root mistaken for host root
```

Validate before reporting.

---

# 228. Chaining

Privilege escalation frequently involves multiple individually weak conditions.

Example:

```text
Standard User
      |
      v
Readable Config
      |
      v
Service Credential
      |
      v
Membership in Administrative Application
      |
      v
Writable Deployment Script
      |
      v
Root Scheduled Execution
```

Document the complete chain and each contributing control failure.

---

# 229. Attack Path Documentation

A useful representation is:

```text
[analyst]
    |
    | write
    v
[/opt/backup/backup.sh]
    |
    | executed by
    v
[root cron]
    |
    | results in
    v
[root-level code execution]
```

This makes the trust relationship clear.

---

# 230. Root Verification

If controlled validation legitimately results in a higher-privileged shell, verify minimally:

```bash
id
```

Expected root context:

```text
uid=0(root)
```

Do not immediately enumerate unrelated root-only data.

Stop once sufficient proof has been obtained.

---

# 231. Post-Validation Cleanup

After validation:

```text
Remove test files
Restore approved temporary changes
Stop test processes
Remove temporary binaries
Remove temporary scripts
Document cleanup
Verify service state
```

Never leave privileged persistence behind.

---

# 232. Do Not Create Persistence

Privilege escalation validation should not normally create:

```text
New root users
SSH authorised keys
SUID shells
Cron persistence
systemd persistence
Backdoors
Startup scripts
```

These are unnecessary for proving most local privilege escalation findings.

---

# 233. Do Not Disable Security Controls

Avoid disabling:

```text
SELinux
AppArmor
auditd
EDR
Firewall
Kernel protections
Logging
```

to make an escalation technique work.

If a security control blocks the path, that is relevant assessment evidence.

---

# 234. Low-Noise Workflow

Start:

```bash
whoami
id
sudo -l
```

Then:

```bash
find / -xdev -perm -4000 -type f -print 2>/dev/null
```

Then:

```bash
getcap -r / 2>/dev/null
```

Then:

```bash
systemctl --type=service --state=running --no-pager
```

Then:

```bash
systemctl list-timers --all --no-pager
```

Then:

```bash
cat /etc/crontab 2>/dev/null
```

Then investigate only high-value candidates.

---

# 235. Fast Triage

```bash
id
sudo -l
uname -a
cat /etc/os-release
find / -xdev -perm -4000 -type f -print 2>/dev/null
getcap -r / 2>/dev/null
systemctl --type=service --state=running --no-pager
systemctl list-timers --all --no-pager
cat /etc/crontab 2>/dev/null
findmnt
ss -lntup
```

This provides a useful initial privilege escalation picture.

---

# 236. Detailed Checklist

## Identity

- [ ] Current username
- [ ] UID
- [ ] GID
- [ ] Supplementary groups
- [ ] Other UID 0 accounts
- [ ] Environment
- [ ] PATH

## Sudo

- [ ] `sudo -l`
- [ ] NOPASSWD
- [ ] SETENV
- [ ] Wildcards
- [ ] Argument restrictions
- [ ] Interpreters
- [ ] Editors
- [ ] Package managers
- [ ] Service management
- [ ] File utilities
- [ ] Custom binaries

## SUID / SGID

- [ ] SUID inventory
- [ ] SGID inventory
- [ ] Root ownership
- [ ] Custom binaries
- [ ] Unusual paths
- [ ] Program behaviour
- [ ] Dependencies
- [ ] Environment
- [ ] PATH handling

## Capabilities

- [ ] `getcap -r /`
- [ ] `CAP_SETUID`
- [ ] `CAP_SETGID`
- [ ] `CAP_DAC_OVERRIDE`
- [ ] `CAP_DAC_READ_SEARCH`
- [ ] `CAP_SYS_ADMIN`
- [ ] `CAP_SYS_PTRACE`
- [ ] Custom capable binaries

## Processes

- [ ] Root processes
- [ ] Process tree
- [ ] Custom applications
- [ ] Short-lived processes
- [ ] Process credentials
- [ ] Open files
- [ ] Local sockets

## Services

- [ ] Running services
- [ ] Custom services
- [ ] Service user
- [ ] Executable
- [ ] Scripts
- [ ] Configuration
- [ ] Environment files
- [ ] Parent directories
- [ ] Writable dependencies
- [ ] Restart mechanism

## Scheduled Execution

- [ ] `/etc/crontab`
- [ ] `/etc/cron.d`
- [ ] Periodic cron directories
- [ ] User crontab
- [ ] systemd timers
- [ ] Associated services
- [ ] `at`
- [ ] Writable scripts
- [ ] PATH
- [ ] Wildcards

## Filesystem

- [ ] Writable administrative files
- [ ] Writable administrative directories
- [ ] World-writable directories
- [ ] Sticky bit
- [ ] ACLs
- [ ] Parent permissions
- [ ] Sensitive files
- [ ] Mount options
- [ ] Shared filesystems
- [ ] Temporary files

## Credentials

- [ ] Shell history
- [ ] SSH keys
- [ ] Application configuration
- [ ] Service credentials
- [ ] Database credentials
- [ ] Cloud credentials
- [ ] Backup credentials
- [ ] Credential reuse within scope

## Groups

- [ ] sudo
- [ ] wheel
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
- [ ] Current capabilities
- [ ] Privileged mode indicators
- [ ] Host mounts
- [ ] Docker socket
- [ ] Devices
- [ ] Namespaces
- [ ] Kubernetes service account
- [ ] RBAC scope

## Software

- [ ] Distribution
- [ ] Kernel
- [ ] Installed packages
- [ ] Custom software
- [ ] Vendor advisories
- [ ] Patch status
- [ ] Kernel exploit preconditions

## Security Controls

- [ ] ASLR
- [ ] AppArmor
- [ ] SELinux
- [ ] seccomp
- [ ] Yama
- [ ] NoNewPrivileges
- [ ] systemd hardening
- [ ] Audit logging

## Validation

- [ ] Candidate confirmed
- [ ] Scope confirmed
- [ ] Lowest-risk proof selected
- [ ] Production impact considered
- [ ] No unnecessary root shell
- [ ] No persistence
- [ ] Cleanup completed
- [ ] Evidence retained securely

---

# 237. Quick Reference

Identity:

```bash
whoami
id
groups
```

Sudo:

```bash
sudo -l
```

OS:

```bash
cat /etc/os-release
uname -a
```

SUID:

```bash
find / -xdev -perm -4000 -type f -print 2>/dev/null
```

SGID:

```bash
find / -xdev -perm -2000 -type f -print 2>/dev/null
```

Capabilities:

```bash
getcap -r / 2>/dev/null
```

Processes:

```bash
ps -eo user,pid,ppid,comm,args
```

Services:

```bash
systemctl --type=service --state=running --no-pager
```

Timers:

```bash
systemctl list-timers --all --no-pager
```

Cron:

```bash
cat /etc/crontab 2>/dev/null
```

Writable administrative paths:

```bash
find /etc /opt /usr/local /srv -writable -ls 2>/dev/null
```

Mounts:

```bash
findmnt
```

Network:

```bash
ss -lntup
```

ACL:

```bash
getfacl /path/to/file
```

Path permissions:

```bash
namei -l /path/to/file
```

File metadata:

```bash
stat -c '%A %a %U %G %n' /path/to/file
```

---

# 238. Privilege Escalation Decision Tree

```text
Start
 |
 v
Who Am I?
 |
 v
sudo -l
 |
 +---- Dangerous Rule? ---- Yes ---> Validate
 |
 No
 |
 v
Privileged Groups?
 |
 +---- High-Privilege Access? ---- Yes ---> Validate
 |
 No
 |
 v
SUID / SGID
 |
 +---- Unsafe Binary? ---- Yes ---> Validate
 |
 No
 |
 v
Capabilities
 |
 +---- Excessive Capability? ---- Yes ---> Validate
 |
 No
 |
 v
Root Services
 |
 +---- Writable Dependency? ---- Yes ---> Validate
 |
 No
 |
 v
Scheduled Tasks
 |
 +---- Writable Dependency? ---- Yes ---> Validate
 |
 No
 |
 v
Credentials
 |
 +---- Higher Privileged Identity? ---- Yes ---> Validate
 |
 No
 |
 v
Containers / Sockets
 |
 +---- Privileged Interface? ---- Yes ---> Validate
 |
 No
 |
 v
Custom Applications
 |
 +---- Local Security Issue? ---- Yes ---> Validate
 |
 No
 |
 v
Kernel / Packages
 |
 +---- Confirmed Vulnerability? ---- Yes ---> Risk Assessment
 |
 No
 |
 v
No Confirmed Escalation Path
```

---

# 239. Privilege Boundary Model

```text
                  ROOT
                    ^
                    |
        +-----------+-----------+
        |           |           |
      Sudo        Service      Cron
        |           |           |
        +-----------+-----------+
                    |
              Trusted Inputs
                    ^
                    |
      +-------------+-------------+
      |             |             |
    Files         Config        Scripts
      |             |             |
      +-------------+-------------+
                    ^
                    |
              Standard User
```

Privilege escalation occurs when a lower-privileged identity can control something trusted by the higher-privileged component.

---

# 240. Final Testing Model

A reliable Linux privilege escalation assessment follows:

```text
1. Establish the current identity.

2. Record UID, GID, and supplementary groups.

3. Identify the operating system and kernel.

4. Review environment variables and PATH.

5. Review sudo permissions.

6. Analyse permitted sudo programs and arguments.

7. Enumerate SUID executables.

8. Enumerate SGID executables.

9. Enumerate Linux file capabilities.

10. Review unusual privileged binaries.

11. Enumerate root processes.

12. Identify custom privileged services.

13. Review service executables and scripts.

14. Review service configuration and environment files.

15. Review parent-directory permissions.

16. Enumerate cron jobs.

17. Enumerate systemd timers.

18. Identify privileged scheduled scripts.

19. Review writable files and directories used by privileged processes.

20. Review ACLs and path permissions.

21. Review sensitive system-file permissions.

22. Review exposed credentials.

23. Review privileged group membership.

24. Review privileged local sockets.

25. Review Docker, LXD, and virtualisation access.

26. Determine whether execution occurs inside a container.

27. Review container capabilities and host mounts.

28. Review Kubernetes identity where applicable.

29. Review custom software.

30. Review installed software and kernel patch status.

31. Account for SELinux, AppArmor, seccomp, and other controls.

32. Prioritise deterministic configuration weaknesses.

33. Prefer configuration and permission evidence over destructive exploitation.

34. Validate only the minimum required impact.

35. Avoid unnecessary root shells.

36. Avoid modifying critical system files.

37. Avoid persistence.

38. Avoid service interruption.

39. Avoid kernel exploitation unless explicitly required.

40. Record the complete privilege escalation chain.

41. Identify the root cause.

42. Remove temporary test artifacts.

43. Recommend least-privilege remediation.

44. Verify remediation where possible.
```

The objective is not:

```text
Run Every Privilege Escalation Technique
```

The preferred approach is:

```text
Enumerate
    |
    v
Understand Trust
    |
    v
Identify Boundary Failure
    |
    v
Prioritise
    |
    v
Validate Minimally
    |
    v
Document Impact
    |
    v
Fix Root Cause
```

---

# Related Notes

- [Linux](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)

---

# References

- [Linux man-pages](https://man7.org/linux/man-pages/){ target="_blank" rel="noopener noreferrer" }
- [Linux capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [systemd Documentation](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [LinEnum](https://github.com/rebootuser/LinEnum){ target="_blank" rel="noopener noreferrer" }
- [Linux Smart Enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }
- [pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/){ target="_blank" rel="noopener noreferrer" }
- [AppArmor](https://apparmor.net/){ target="_blank" rel="noopener noreferrer" }
- [SELinux Project](https://selinuxproject.org/){ target="_blank" rel="noopener noreferrer" }
- [Debian Security](https://www.debian.org/security/){ target="_blank" rel="noopener noreferrer" }
- [Ubuntu Security](https://ubuntu.com/security){ target="_blank" rel="noopener noreferrer" }
- [Red Hat Security](https://access.redhat.com/security/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Abuse Elevation Control Mechanism](https://attack.mitre.org/techniques/T1548/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Sudo and Sudo Caching](https://attack.mitre.org/techniques/T1548/003/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Setuid and Setgid](https://attack.mitre.org/techniques/T1548/001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }

---

> Use Linux privilege escalation techniques only on systems you own or have explicit permission to assess. Prefer configuration analysis, permission evidence, and minimal controlled validation over destructive exploitation. Avoid unnecessary root shells, persistence, credential modification, service interruption, security-control disabling, or kernel exploitation when the privilege boundary can be demonstrated safely.
