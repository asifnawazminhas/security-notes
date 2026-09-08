---
title: Linux Security Controls
description: Practical Linux security control assessment covering SELinux, AppArmor, seccomp, namespaces, mount hardening, kernel protections, systemd hardening, authentication controls, auditing, firewalling and defensive validation.
---

# Linux Security Controls

Linux systems can use multiple overlapping security controls to reduce the impact of compromised accounts, vulnerable applications and configuration weaknesses.

Important controls include:

```text
Unix permissions and ACLs

SELinux

AppArmor

seccomp

Linux capabilities

Namespaces

Kernel hardening

Mount options

systemd sandboxing

PAM

Firewalling

Audit logging

Application-specific controls
```

These mechanisms should not be assessed independently.

A useful security model is:

```text
Application / User
        |
        v
Unix Permissions
        |
        v
Capabilities
        |
        v
Mandatory Access Control
        |
        +---- SELinux
        |
        +---- AppArmor
        |
        v
Namespaces / Containers
        |
        v
seccomp
        |
        v
Kernel Protections
        |
        v
Service Hardening
        |
        v
Network Controls
        |
        v
Logging / Detection
```

The objective of a Linux security assessment is not simply to determine whether each control exists.

The important questions are:

> Which controls apply to the assessed workload, how are they configured, and do they meaningfully restrict the security boundary being tested?

!!! warning "Authorised Security Testing"

    Perform security-control assessment only on systems you own or have explicit permission to assess. Prefer read-only inspection. Do not disable SELinux, AppArmor, firewalling, auditing, seccomp, kernel protections or production service hardening merely to demonstrate that a control is effective.

---

# 1. Defence in Depth

Linux security should use multiple independent controls.

For example:

```text
Internet
   |
   v
Firewall
   |
   v
Web Service
   |
   v
Unprivileged Service Account
   |
   v
Filesystem Permissions
   |
   v
AppArmor / SELinux
   |
   v
systemd Sandboxing
   |
   v
Kernel
```

If the web application is compromised, the attacker should still encounter additional restrictions.

This is defence in depth.

---

# 2. Establish the Assessment Context

Before reviewing individual controls, establish:

```bash
whoami
id
uname -a
cat /etc/os-release
```

Collect:

```text
Distribution

Distribution version

Kernel

Architecture

Current user

UID

GID

Groups
```

Security-control availability and configuration can differ significantly between Linux distributions.

---

# 3. Quick Security Control Discovery

A useful initial read-only review is:

```bash
echo '=== IDENTITY ==='
id

echo
echo '=== OPERATING SYSTEM ==='
cat /etc/os-release 2>/dev/null || true

echo
echo '=== KERNEL ==='
uname -a

echo
echo '=== SELINUX ==='
getenforce 2>/dev/null || true
sestatus 2>/dev/null || true

echo
echo '=== APPARMOR ==='
aa-status 2>/dev/null || true

echo
echo '=== PROCESS CAPABILITIES ==='
grep '^Cap' /proc/$$/status 2>/dev/null || true

echo
echo '=== NO NEW PRIVILEGES ==='
grep '^NoNewPrivs' /proc/$$/status 2>/dev/null || true

echo
echo '=== SECCOMP ==='
grep '^Seccomp' /proc/$$/status 2>/dev/null || true

echo
echo '=== MOUNTS ==='
findmnt 2>/dev/null || true

echo
echo '=== FIREWALL TOOLS ==='
command -v nft 2>/dev/null || true
command -v iptables 2>/dev/null || true
command -v ufw 2>/dev/null || true
command -v firewall-cmd 2>/dev/null || true
```

This does not establish that every control is secure.

It provides a starting point.

---

# 4. Mandatory Access Control

Traditional Linux discretionary access control is based primarily on:

```text
UID

GID

Mode bits

ACLs
```

Mandatory Access Control, or MAC, can impose additional policy.

Two common Linux MAC frameworks are:

```text
SELinux

AppArmor
```

Conceptually:

```text
Process Requests Access
        |
        v
Unix Permission Check
        |
      Allowed
        |
        v
MAC Policy Check
        |
     +--+--+
     |     |
   Allow  Deny
```

Passing ordinary Unix permission checks does not necessarily mean an operation will be permitted by the MAC policy.

---

# 5. SELinux

SELinux provides label-based mandatory access control.

Important concepts include:

```text
Subject

Object

Security context

Type

Domain

Policy

Allow rule
```

A simplified relationship is:

```text
Process Domain
      |
      v
SELinux Policy
      |
      v
Target Object Type
      |
   +--+--+
   |     |
 Allow  Deny
```

SELinux can restrict even privileged processes.

---

# 6. Check SELinux Status

Use:

```bash
getenforce
```

Possible output:

```text
Enforcing
Permissive
Disabled
```

For additional information:

```bash
sestatus
```

Representative output may contain:

```text
SELinux status:                 enabled
Current mode:                   enforcing
Mode from config file:          enforcing
Policy from config file:        targeted
```

---

# 7. SELinux Modes

## Enforcing

```text
Policy violations are blocked and can be logged.
```

## Permissive

```text
Policy violations are generally logged but not enforced.
```

## Disabled

```text
SELinux policy enforcement is not active.
```

Do not automatically report:

```text
SELinux disabled
```

as a vulnerability.

Whether SELinux is required depends on:

```text
System baseline

Threat model

Distribution

Application architecture

Alternative controls

Organisational policy
```

---

# 8. SELinux Contexts

Inspect a file:

```bash
ls -Z /path/to/file
```

Inspect a process:

```bash
ps -eZ
```

Representative file context:

```text
system_u:object_r:httpd_sys_content_t:s0
```

Representative process context might include a domain such as:

```text
httpd_t
```

The exact context depends on the distribution and policy.

---

# 9. SELinux Process Review

Find relevant processes:

```bash
ps -eZ | grep -i nginx
```

or:

```bash
ps -eZ | grep -i httpd
```

Determine:

```text
Which domain is the process running under?

Is the domain expected?

What resources should it access?

Are unexpected domains unconfined?
```

Do not conclude that a process is insecure solely because its domain name is unfamiliar.

---

# 10. SELinux Configuration

Common configuration location:

```text
/etc/selinux/config
```

Inspect:

```bash
cat /etc/selinux/config 2>/dev/null
```

Typical settings can include:

```text
SELINUX=enforcing
SELINUXTYPE=targeted
```

Runtime state should still be checked separately because configuration and current state can differ.

---

# 11. SELinux Booleans

SELinux booleans allow selected policy behavior to be changed without rewriting the complete policy.

Enumerate:

```bash
getsebool -a 2>/dev/null
```

Search relevant settings:

```bash
getsebool -a 2>/dev/null | grep -i http
```

A boolean set to:

```text
on
```

is not automatically insecure.

Determine what behavior it enables and whether that behavior is required.

---

# 12. SELinux Denials

SELinux denials can appear in audit logs.

Where available:

```bash
ausearch -m AVC,USER_AVC -ts recent 2>/dev/null
```

Alternative log inspection may include:

```bash
journalctl --no-pager | grep -i 'avc.*denied'
```

A denial can demonstrate that SELinux prevented an operation.

Do not disable SELinux simply to determine whether the denied operation would otherwise succeed.

---

# 13. SELinux Validation Model

Use:

```text
Process
   |
   v
Security Domain
   |
   v
Requested Operation
   |
   v
Target Object
   |
   v
SELinux Decision
   |
   +---- Allowed
   |
   +---- Denied
```

When SELinux blocks an assessment path, document the restriction as part of the effective security posture.

---

# 14. AppArmor

AppArmor provides path-oriented mandatory access control.

Applications can be associated with profiles defining permitted operations.

Potential restrictions include:

```text
File access

Executable access

Capabilities

Networking

Signals

Mount operations
```

---

# 15. Check AppArmor Status

Use:

```bash
aa-status
```

or:

```bash
apparmor_status
```

Depending on distribution and installed tools.

The output can identify:

```text
Loaded profiles

Enforcing profiles

Complain-mode profiles

Unconfined processes
```

---

# 16. AppArmor Modes

Common concepts include:

```text
Enforce

Complain
```

## Enforce

Policy restrictions are applied.

## Complain

Policy violations are generally logged rather than blocked.

A profile in complain mode may be useful during policy development but provides different protection from enforce mode.

---

# 17. AppArmor Profiles

Common profile locations include:

```text
/etc/apparmor.d/
```

List:

```bash
ls -la /etc/apparmor.d/ 2>/dev/null
```

Search for a specific application:

```bash
grep -R "nginx" /etc/apparmor.d/ 2>/dev/null
```

Do not modify profiles during ordinary assessment unless explicitly authorised.

---

# 18. AppArmor Process Review

Use:

```bash
aa-status
```

Then correlate profiles with running processes:

```bash
ps aux
```

Questions include:

```text
Is the security-sensitive service confined?

Which profile applies?

Is the profile enforcing?

Is the process unexpectedly unconfined?

Does policy allow more access than required?
```

---

# 19. AppArmor Denials

Relevant messages may appear in:

```bash
journalctl --no-pager | grep -i apparmor
```

or distribution-specific audit logs.

A denial may contain information about:

```text
Profile

Operation

Target

Requested permissions
```

Use denials as evidence of actual policy enforcement.

---

# 20. SELinux Versus AppArmor

A simplified comparison:

| Control | General Model |
|---|---|
| SELinux | Label and type based |
| AppArmor | Primarily path based |
| Both | Mandatory access control |

The security assessment should focus on effective policy rather than which framework is preferred.

---

# 21. seccomp

seccomp allows Linux processes to restrict the system calls they can make.

This can significantly reduce the kernel attack surface available to a compromised process.

A simplified model:

```text
Compromised Process
        |
        v
System Call
        |
        v
seccomp Filter
        |
     +--+--+
     |     |
   Allow  Block
```

seccomp is especially common in:

```text
Containers

Browsers

Sandboxes

Security-sensitive services
```

---

# 22. Check seccomp State

Inspect the current process:

```bash
grep '^Seccomp' /proc/$$/status
```

You may see:

```text
Seccomp: 0
```

or another value.

The values represent seccomp modes defined by the kernel interface.

Also inspect:

```bash
grep '^Seccomp_filters' /proc/$$/status 2>/dev/null
```

where supported.

---

# 23. seccomp Modes

At a high level, Linux supports:

```text
SECCOMP_MODE_DISABLED

SECCOMP_MODE_STRICT

SECCOMP_MODE_FILTER
```

Filter mode allows a BPF-based filter to determine how specific system calls are handled.

Do not infer policy quality solely from:

```text
Seccomp: 2
```

That indicates filtering is active but does not tell you whether the filter is appropriately restrictive.

---

# 24. seccomp and Containers

Container runtimes frequently apply seccomp profiles.

When assessing a container, determine:

```text
Is seccomp enabled?

Which profile is applied?

Is the container unconfined?

Which system calls are restricted?

Are dangerous capabilities also present?
```

The combination matters more than any one control.

---

# 25. No New Privileges

Linux supports the:

```text
no_new_privs
```

process attribute.

When set, `execve()` cannot grant privileges that the process did not already possess through mechanisms such as SUID, SGID and file capabilities.

Inspect:

```bash
grep '^NoNewPrivs' /proc/$$/status
```

Representative output:

```text
NoNewPrivs: 1
```

This is an important defence against privilege transitions.

---

# 26. systemd NoNewPrivileges

systemd can configure:

```text
NoNewPrivileges=yes
```

Inspect:

```bash
systemctl show example.service -p NoNewPrivileges
```

Do not report:

```text
NoNewPrivileges=no
```

as a standalone vulnerability.

Determine whether the service has an actual privilege transition that this control would mitigate.

---

# 27. Linux Namespaces

Namespaces isolate different aspects of the operating system.

Important namespace types include:

```text
Mount

PID

Network

User

IPC

UTS

Cgroup

Time
```

Namespaces are fundamental to container isolation.

---

# 28. Inspect Namespaces

For the current process:

```bash
ls -l /proc/$$/ns/
```

Representative entries include:

```text
cgroup

ipc

mnt

net

pid

user

uts
```

Compare another process where permitted:

```bash
ls -l /proc/<PID>/ns/
```

Processes referencing different namespace identifiers may operate in different isolation contexts.

---

# 29. User Namespaces

User namespaces can map identities between namespace and host contexts.

Therefore:

```text
UID 0 inside namespace
```

does not necessarily mean:

```text
UID 0 on host
```

Inspect mappings:

```bash
cat /proc/$$/uid_map
```

```bash
cat /proc/$$/gid_map
```

This is particularly important when analysing containers and sandboxed applications.

---

# 30. Container Detection

Potential indicators include:

```bash
cat /proc/1/cgroup 2>/dev/null
```

```bash
cat /proc/1/mountinfo 2>/dev/null
```

```bash
test -f /.dockerenv && echo "Docker environment marker present"
```

No single indicator should always be treated as definitive across every runtime.

Use multiple observations.

---

# 31. Container Security Context

If a container is identified, determine:

```text
Container UID

Host UID mapping

Capabilities

seccomp

AppArmor / SELinux

Mounted host paths

Device access

Network namespace

PID namespace

Container runtime
```

The security boundary is the combination of these controls.

---

# 32. Linux Capabilities

Capabilities divide many traditional root privileges into narrower units.

Enumerate file capabilities:

```bash
getcap -r /usr /usr/local /opt 2>/dev/null
```

Inspect process capabilities:

```bash
grep '^Cap' /proc/$$/status
```

See [Linux Capabilities Security](capabilities.md) for detailed assessment methodology.

---

# 33. SUID and SGID

SUID and SGID provide another privilege mechanism.

Enumerate:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null
```

See [Linux SUID and SGID Security](suid-sgid.md).

Do not assess SUID, SGID and capabilities independently from controls such as:

```text
nosuid

NoNewPrivileges

SELinux

AppArmor

Namespaces
```

---

# 34. Mount Security

Filesystem mount options can provide additional hardening.

Inspect:

```bash
findmnt
```

For a specific path:

```bash
findmnt -T /path/to/file
```

Potentially relevant options include:

```text
nosuid

nodev

noexec

ro
```

These controls require contextual interpretation.

---

# 35. nosuid

The:

```text
nosuid
```

mount option affects privilege transitions associated with SUID, SGID and file capabilities.

It can reduce the risk of privileged executables on filesystems where such functionality is not required.

Typical candidates for consideration may include:

```text
Temporary filesystems

User-controlled filesystems

Removable storage
```

Do not recommend `nosuid` blindly where legitimate privileged execution is required.

---

# 36. nodev

The:

```text
nodev
```

option prevents interpretation of device special files on the filesystem.

It can be useful on filesystems where device nodes are unnecessary.

Its absence is not automatically a vulnerability.

---

# 37. noexec

The:

```text
noexec
```

option restricts direct execution of binaries from the mounted filesystem.

This can provide useful hardening.

However:

```text
noexec
```

should not be described as a universal prevention mechanism for all forms of code execution.

Interpreters and other execution paths can change the practical result.

Treat it as defence in depth.

---

# 38. Read-Only Mounts

The:

```text
ro
```

option mounts a filesystem read-only.

This can strongly protect immutable application or system resources where writes are unnecessary.

Containers frequently use read-only mounts for sensitive host resources.

---

# 39. Review Important Mounts

Use:

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

Pay attention to filesystems associated with:

```text
/tmp

/var/tmp

/home

/dev/shm

Application data

Container mounts

Network shares
```

The correct options depend on system requirements.

---

# 40. /tmp Security

`/tmp` is intentionally writable on typical Linux systems.

Inspect:

```bash
ls -ld /tmp
```

A common secure mode is:

```text
drwxrwxrwt
```

The:

```text
t
```

represents the sticky bit.

World-writable `/tmp` is not automatically a vulnerability.

The security question is whether privileged applications trust attacker-controlled temporary resources unsafely.

---

# 41. /var/tmp Security

Inspect:

```bash
ls -ld /var/tmp
```

Like `/tmp`, `/var/tmp` may intentionally be writable.

Do not report it simply because multiple users can create files there.

Investigate privileged consumers of those files.

---

# 42. /dev/shm

Inspect:

```bash
findmnt -T /dev/shm
```

and:

```bash
ls -ld /dev/shm
```

`/dev/shm` is commonly a writable temporary shared-memory filesystem.

Review its use by security-sensitive applications rather than reporting expected writability.

---

# 43. Kernel Hardening

Linux exposes many security-relevant kernel settings through:

```text
sysctl
```

Potential areas include:

```text
Kernel pointer exposure

Process tracing

Core dumps

Symbol restrictions

Network behavior

User namespaces

BPF

Filesystem protections
```

Do not create a finding from one sysctl without understanding the system's baseline and threat model.

---

# 44. sysctl Enumeration

List all settings:

```bash
sysctl -a 2>/dev/null
```

This can produce substantial output.

For targeted assessment, query specific controls.

Example:

```bash
sysctl kernel.randomize_va_space
```

---

# 45. Address Space Layout Randomization

Check:

```bash
sysctl kernel.randomize_va_space
```

Common values include:

```text
0
1
2
```

The precise behavior is documented by the kernel.

On modern general-purpose Linux systems, full ASLR is commonly expected.

However, exploitability cannot be determined from this value alone.

---

# 46. Kernel Pointer Restrictions

Inspect:

```bash
sysctl kernel.kptr_restrict
```

This setting restricts exposure of kernel addresses through interfaces such as `/proc/kallsyms`.

Reducing kernel address exposure can increase the difficulty of exploiting certain kernel vulnerabilities.

---

# 47. dmesg Restrictions

Inspect:

```bash
sysctl kernel.dmesg_restrict
```

Restricting unprivileged access to kernel logs can reduce information exposure.

Validate actual access:

```bash
dmesg 2>&1 | head
```

Do not change the setting during routine assessment.

---

# 48. ptrace Restrictions

On systems using Yama:

```bash
sysctl kernel.yama.ptrace_scope 2>/dev/null
```

This can restrict process tracing.

The practical result also depends on:

```text
UID

Capabilities

Process relationships

Namespaces

LSM policy
```

---

# 49. Protected Symlinks

Check:

```bash
sysctl fs.protected_symlinks
```

This control helps mitigate classes of symlink attacks in sticky world-writable directories.

---

# 50. Protected Hard Links

Check:

```bash
sysctl fs.protected_hardlinks
```

This can reduce abuse of hard links involving files owned by other users.

---

# 51. Protected FIFOs and Regular Files

Where supported:

```bash
sysctl fs.protected_fifos
```

```bash
sysctl fs.protected_regular
```

These settings provide additional protection in sticky world-writable directories.

Availability can depend on kernel version and distribution.

---

# 52. Core Dumps

Core dumps can contain:

```text
Passwords

Tokens

Private keys

Application secrets

Memory-resident sensitive data
```

Inspect:

```bash
ulimit -c
```

For systemd-managed systems:

```bash
systemctl status systemd-coredump.socket 2>/dev/null
```

Also review application-specific core dump configuration where relevant.

Do not assume enabled core dumps are automatically vulnerable.

Consider:

```text
Storage permissions

Retention

Sensitivity

Access controls
```

---

# 53. Kernel Module Security

List modules:

```bash
lsmod
```

Check whether module loading is disabled:

```bash
sysctl kernel.modules_disabled
```

If:

```text
kernel.modules_disabled = 1
```

further module loading is disabled until reboot.

This can be a strong hardening measure for systems whose module requirements are already satisfied.

It may not be operationally appropriate for every host.

---

# 54. Kernel Lockdown

Some systems support kernel lockdown.

Check:

```bash
cat /sys/kernel/security/lockdown 2>/dev/null
```

Possible modes can include:

```text
none

integrity

confidentiality
```

Availability depends on kernel and boot configuration.

---

# 55. Secure Boot

On compatible UEFI systems, check using available tooling such as:

```bash
mokutil --sb-state 2>/dev/null
```

Representative output:

```text
SecureBoot enabled
```

Secure Boot helps protect the boot chain but should not be treated as a substitute for runtime security controls.

---

# 56. Kernel Version

Collect:

```bash
uname -r
```

and:

```bash
uname -a
```

Do not report a vulnerability based solely on kernel version.

Distribution vendors frequently backport security patches without changing the version in the same way as upstream releases.

Validate security advisories against:

```text
Distribution

Package release

Vendor advisory

Patch state
```

---

# 57. systemd Security

systemd provides numerous service-hardening controls.

Examples include:

```text
User=

Group=

NoNewPrivileges=

CapabilityBoundingSet=

AmbientCapabilities=

PrivateTmp=

PrivateDevices=

ProtectSystem=

ProtectHome=

ProtectKernelTunables=

ProtectKernelModules=

ProtectControlGroups=

RestrictNamespaces=

RestrictAddressFamilies=

SystemCallFilter=

ReadOnlyPaths=

InaccessiblePaths=
```

Not every directive is appropriate for every service.

---

# 58. Review a Service

Inspect the effective unit:

```bash
systemctl cat example.service
```

Useful properties:

```bash
systemctl show example.service \
    -p User \
    -p Group \
    -p ExecStart \
    -p NoNewPrivileges \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p PrivateTmp \
    -p PrivateDevices \
    -p ProtectSystem \
    -p ProtectHome
```

Correlate service hardening with actual application requirements.

---

# 59. systemd-analyze security

Where supported:

```bash
systemd-analyze security example.service
```

This provides an automated assessment of multiple sandboxing and hardening properties.

It can help identify improvement opportunities.

Do not use the exposure score as the sole basis for a vulnerability.

---

# 60. PrivateTmp

A service can use:

```text
PrivateTmp=yes
```

This provides a private `/tmp` and `/var/tmp` namespace for the service.

It can reduce temporary-file interaction between services and other users.

It does not automatically fix insecure temporary-file handling inside the service itself.

---

# 61. ProtectSystem

systemd supports:

```text
ProtectSystem=
```

Possible settings provide varying levels of read-only protection for portions of the filesystem.

This can reduce the impact of service compromise.

The application may still require explicit writable paths.

---

# 62. ProtectHome

systemd can restrict service access to:

```text
/home

/root

/run/user
```

through:

```text
ProtectHome=
```

This can reduce unnecessary access to user data.

Whether it is appropriate depends on service requirements.

---

# 63. PrivateDevices

```text
PrivateDevices=yes
```

can provide the service with a restricted `/dev`.

This reduces access to physical and kernel device interfaces.

It is particularly useful for services that do not require direct device access.

---

# 64. RestrictAddressFamilies

systemd can restrict which socket address families a service may use.

Example concept:

```text
RestrictAddressFamilies=AF_INET AF_INET6
```

A network service may not require:

```text
AF_PACKET

AF_NETLINK

AF_UNIX
```

depending on its functionality.

Use allowlists carefully to avoid breaking required behavior.

---

# 65. SystemCallFilter

systemd can restrict system calls using:

```text
SystemCallFilter=
```

This can reduce kernel attack surface.

The filter should be tested against legitimate service functionality.

---

# 66. Service Account Isolation

Services should generally avoid running as root unless necessary.

Inspect:

```bash
systemctl show example.service -p User -p Group
```

Also inspect the running process:

```bash
ps -o pid,user,group,comm,args -C example
```

Running as root is not automatically a vulnerability, but it increases potential impact if the service is compromised.

---

# 67. DynamicUser

systemd supports:

```text
DynamicUser=yes
```

for some services.

This can provide transient service identities and reduce persistent account-management requirements.

It is not appropriate for every application, particularly where persistent ownership is required.

---

# 68. PAM

Pluggable Authentication Modules provide authentication and session controls for many Linux services.

Common configuration locations include:

```text
/etc/pam.d/

/etc/security/
```

PAM may control:

```text
Authentication

Password policy

Account restrictions

Session handling

Resource limits

Login controls
```

---

# 69. Review PAM Configuration

List:

```bash
ls -la /etc/pam.d/
```

Review relevant services individually.

Examples might include:

```text
sshd

login

sudo

su
```

Do not modify PAM configuration during routine testing.

Incorrect PAM changes can lock users out of the system.

---

# 70. Password Policy

Password policy can be influenced by:

```text
PAM modules

/etc/login.defs

Identity providers

Directory services

Application-specific authentication
```

Inspect:

```bash
grep -Ev '^\s*(#|$)' /etc/login.defs 2>/dev/null
```

Do not assume `/etc/login.defs` alone defines the effective password policy.

---

# 71. Account Lockout

Depending on distribution, PAM may use mechanisms such as:

```text
pam_faillock
```

Search:

```bash
grep -R "pam_faillock" /etc/pam.d/ 2>/dev/null
```

Lockout testing can cause denial of service to real accounts.

Use designated test accounts and agreed thresholds.

---

# 72. SSH Security

OpenSSH is a major Linux administrative boundary.

Inspect effective server configuration where authorised:

```bash
sshd -T 2>/dev/null
```

Useful settings can include:

```text
permitrootlogin

passwordauthentication

pubkeyauthentication

permitemptypasswords

allowusers

allowgroups

maxauthtries
```

The effective configuration is preferable to reading only:

```text
/etc/ssh/sshd_config
```

because includes and defaults can alter behavior.

---

# 73. SSH Root Login

Check:

```bash
sshd -T 2>/dev/null | grep '^permitrootlogin'
```

The security impact depends on:

```text
Authentication method

Network exposure

MFA

Source restrictions

Monitoring

Operational requirements
```

Avoid treating one directive as the entire SSH security posture.

---

# 74. SSH Password Authentication

Check:

```bash
sshd -T 2>/dev/null | grep '^passwordauthentication'
```

Public-key authentication can reduce some password-related attack paths.

However, key management then becomes security critical.

---

# 75. SSH Private Keys

Review permissions on authorised in-scope keys:

```bash
find /home /root -type f -name 'id_*' 2>/dev/null
```

Do not copy or expose private key material unnecessarily.

Relevant security questions include:

```text
Who can read the key?

Is the key still required?

Is it protected by a passphrase?

Where is the public key authorised?

Is key rotation managed?
```

---

# 76. Firewalling

Linux firewalling may be implemented through:

```text
nftables

iptables

firewalld

UFW

Cloud firewall controls

Container runtime rules
```

Do not assume that the absence of one firewall utility means no firewall exists.

---

# 77. nftables

Inspect:

```bash
nft list ruleset
```

This may require elevated privileges depending on configuration.

Review:

```text
Input policy

Allowed ports

Source restrictions

Forwarding

NAT

Container rules
```

---

# 78. iptables

Where still applicable:

```bash
iptables -S
```

and:

```bash
iptables -L -n -v
```

The visible interface may use an nftables backend on modern distributions.

Interpret the actual system implementation.

---

# 79. UFW

Check:

```bash
ufw status verbose
```

Where permissions permit.

Review:

```text
Default policy

Allowed services

Source restrictions

IPv4

IPv6
```

---

# 80. firewalld

Check:

```bash
firewall-cmd --state
```

Then:

```bash
firewall-cmd --get-active-zones
```

and where authorised:

```bash
firewall-cmd --list-all
```

Zone context is important when interpreting rules.

---

# 81. Listening Services

Firewall review should be correlated with actual listeners.

Use:

```bash
ss -lntup
```

or without process information where permissions restrict it:

```bash
ss -lntu
```

The assessment relationship is:

```text
Listening Service
       |
       v
Bound Interface
       |
       v
Host Firewall
       |
       v
Upstream Firewall
       |
       v
Reachable Source
```

---

# 82. IPv6

Do not review only IPv4.

Check:

```bash
ip -6 addr
```

```bash
ip -6 route
```

and firewall configuration for IPv6.

A service may be restricted on IPv4 but unexpectedly reachable over IPv6.

---

# 83. Audit Framework

Linux Audit can provide detailed security events.

Check:

```bash
systemctl status auditd 2>/dev/null
```

Rules may be viewed with:

```bash
auditctl -l 2>/dev/null
```

where permissions permit.

---

# 84. Audit Rules

Audit rules can monitor:

```text
Authentication

Privilege use

Sensitive file changes

System calls

Identity changes

Policy changes
```

The presence of `auditd` alone does not prove that meaningful events are being collected.

Review rules and operational monitoring.

---

# 85. journald

Check:

```bash
systemctl status systemd-journald
```

Inspect configuration:

```bash
grep -Ev '^\s*(#|$)' /etc/systemd/journald.conf 2>/dev/null
```

Consider:

```text
Persistence

Retention

Storage

Forwarding

Permissions
```

---

# 86. Log Permissions

Inspect:

```bash
ls -ld /var/log
```

and selected security-sensitive logs:

```bash
find /var/log -maxdepth 2 -type f \
    -printf '%M %u %g %p\n' 2>/dev/null | head -100
```

Avoid reading sensitive log contents unless required by the assessment.

The key questions are:

```text
Can untrusted users modify logs?

Can sensitive logs be read unnecessarily?

Are logs retained appropriately?
```

---

# 87. Remote Logging

Centralised logging can protect evidence if the local system is compromised.

Potential architectures include:

```text
Host
 |
 v
Local Logging
 |
 v
Remote Collector
 |
 v
SIEM
```

Assess whether critical events leave the host and whether monitoring exists.

Do not assume remote logging from the presence of an agent alone.

---

# 88. Time Synchronisation

Accurate time is important for:

```text
Incident investigation

Authentication

Certificate validation

Log correlation

Detection
```

Check:

```bash
timedatectl status
```

Potential services include:

```text
systemd-timesyncd

chronyd

ntpd
```

---

# 89. Automatic Security Updates

Update strategy depends on distribution and organisational policy.

Potential mechanisms include:

```text
unattended-upgrades

dnf-automatic

yum-cron

Configuration management

Central patch orchestration
```

Do not assume automatic updates must always be enabled.

Production environments may use controlled patch deployment.

The relevant question is whether security updates are managed within an acceptable timeframe.

---

# 90. Debian and Ubuntu Package State

Useful commands include:

```bash
apt list --upgradable 2>/dev/null
```

and:

```bash
dpkg -l
```

Do not automatically report every available package update as a security vulnerability.

Determine whether the update addresses a relevant security issue.

---

# 91. RPM-Based Package State

Depending on distribution:

```bash
dnf check-update
```

or:

```bash
yum check-update
```

may identify available updates.

Again, correlate with vendor security advisories.

---

# 92. File Integrity Monitoring

Some environments use:

```text
AIDE

Wazuh

OSSEC

EDR

Configuration management

Custom integrity monitoring
```

The objective is to detect unauthorised changes to important resources.

Potential targets include:

```text
/etc

Privileged binaries

Service units

SSH configuration

Cron configuration

Application configuration
```

---

# 93. AIDE

If installed:

```bash
command -v aide
```

Configuration may exist under:

```text
/etc/aide/
```

or:

```text
/etc/aide.conf
```

Do not initiate a large integrity scan on a production system without considering performance impact.

---

# 94. Application Sandboxing

Security-sensitive applications may use additional sandboxing beyond operating-system defaults.

Examples include:

```text
chroot

Namespaces

seccomp

SELinux

AppArmor

systemd sandboxing

Application-specific privilege separation
```

Assess the effective combination.

---

# 95. chroot

A chroot changes the apparent filesystem root of a process.

It can reduce filesystem exposure but should not be treated as a complete security boundary by itself.

Additional controls are normally required for strong isolation.

---

# 96. Privilege Separation

A secure application architecture may split functionality.

Example:

```text
Network-Facing Process
        |
        | IPC
        v
Small Privileged Helper
        |
        v
Privileged Operation
```

This can reduce the amount of code running with elevated privileges.

During assessment, review the interface between the unprivileged process and privileged helper.

---

# 97. Compiler Availability

Some hardened environments remove development tooling from production hosts.

Check where relevant:

```bash
command -v gcc
command -v clang
command -v make
```

Compiler presence is not a vulnerability.

Compiler absence is not a complete code-execution mitigation.

Treat this as contextual information only.

---

# 98. Shell and Interpreter Availability

Inventory where relevant:

```bash
command -v bash
command -v sh
command -v python3
command -v perl
command -v ruby
command -v node
```

Do not report interpreter presence as a vulnerability.

Applications may legitimately require them.

Security depends on whether privileged mechanisms expose them unsafely.

---

# 99. Security Control Correlation

The most important part of the assessment is correlation.

Example:

```text
Root-Owned SUID Binary
        |
        v
nosuid Filesystem
        |
        v
SUID Transition Restricted
```

Another:

```text
Compromised Web Service
        |
        v
Unprivileged User
        |
        v
AppArmor Enforcing
        |
        v
Restricted Filesystem Access
        |
        v
NoNewPrivileges
        |
        v
Reduced PrivEsc Paths
```

Controls should be evaluated as a system.

---

# 100. Practical Validation - Service Hardening

## Scenario

A web application runs through:

```text
application.service
```

## Step 1 - Identify Service Identity

```bash
systemctl show application.service -p User -p Group
```

## Step 2 - Review Unit

```bash
systemctl cat application.service
```

## Step 3 - Review Security Properties

```bash
systemctl show application.service \
    -p User \
    -p Group \
    -p NoNewPrivileges \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p PrivateTmp \
    -p PrivateDevices \
    -p ProtectSystem \
    -p ProtectHome
```

## Step 4 - Automated Hardening Review

Where supported:

```bash
systemd-analyze security application.service
```

## Step 5 - Correlate

Determine:

```text
Does the service run as root?

Which capabilities are available?

Can it gain new privileges?

Can it access user home directories?

Can it modify system files?

Can it access devices?

Which MAC policy applies?
```

---

# 101. Representative Positive Result

Suppose:

```text
Service:
backup-web.service

User:
backupsvc

NoNewPrivileges:
no

ProtectSystem:
no

ProtectHome:
no

AppArmor:
No profile

SELinux:
Not active

Writable privileged helper:
Present
```

Do not create one finding for every disabled hardening directive.

Instead determine whether the missing controls enable an actual security boundary to be crossed.

If `backupsvc` can modify a privileged helper later executed by root, the writable privileged execution path is the primary finding.

Missing hardening controls can be described as contributing factors where appropriate.

---

# 102. Representative Defensive Result

Suppose:

```text
Service:
web.service

User:
websvc

NoNewPrivileges:
yes

PrivateTmp:
yes

ProtectSystem:
strict

ProtectHome:
yes

CapabilityBoundingSet:
CAP_NET_BIND_SERVICE

AppArmor:
Enforcing
```

This suggests a strong defence-in-depth design.

It does not prove that the application is vulnerability free.

The controls reduce the potential impact of application compromise.

---

# 103. Practical Validation - SELinux

## Scenario

A service appears unable to access a sensitive directory even though Unix permissions suggest access should be possible.

Check:

```bash
getenforce
```

Then:

```bash
ps -eZ | grep application
```

Inspect target context:

```bash
ls -Zd /sensitive/path
```

Search relevant denials:

```bash
ausearch -m AVC,USER_AVC -ts recent 2>/dev/null
```

The result may demonstrate that SELinux provides an additional effective boundary.

---

# 104. Practical Validation - AppArmor

## Scenario

An application appears restricted from accessing an unexpected file.

Check:

```bash
aa-status
```

Identify its profile.

Review relevant log events:

```bash
journalctl --no-pager | grep -i apparmor
```

If the operation is denied by an enforcing profile, record this as part of the effective control environment.

Do not place the profile into complain mode merely to continue testing unless explicitly authorised.

---

# 105. Practical Validation - Mount Hardening

## Scenario

An SUID binary is discovered under:

```text
/mnt/application/
```

Check:

```bash
getcap /mnt/application/example 2>/dev/null
```

```bash
stat /mnt/application/example
```

```bash
findmnt -T /mnt/application/example
```

If the filesystem is mounted:

```text
nosuid
```

the apparent privileged metadata may not produce the privilege transition initially assumed.

This is an important false-positive check.

---

# 106. Practical Validation - Kernel Controls

Collect selected controls:

```bash
sysctl kernel.randomize_va_space
sysctl kernel.kptr_restrict
sysctl kernel.dmesg_restrict
sysctl kernel.yama.ptrace_scope 2>/dev/null
sysctl fs.protected_symlinks
sysctl fs.protected_hardlinks
sysctl fs.protected_fifos 2>/dev/null
sysctl fs.protected_regular 2>/dev/null
```

Interpret them against:

```text
Distribution guidance

Organisational baseline

Threat model

Application requirements
```

Avoid treating a generic internet hardening checklist as authoritative for every Linux system.

---

# 107. False Positives and Weak Conclusions

Common weak conclusions include:

```text
SELinux disabled = vulnerable

AppArmor absent = vulnerable

Firewall inactive = vulnerable

noexec missing = vulnerable

nosuid missing = vulnerable

Compiler installed = vulnerable

Python installed = vulnerable

Root process = vulnerable

Old-looking kernel version = vulnerable

NoNewPrivileges=no = vulnerable

systemd-analyze score = vulnerability severity
```

Each may identify an area for investigation.

None automatically establishes a security vulnerability.

---

# 108. Security Baselines

Security-control assessment is stronger when compared against an explicit baseline.

Potential sources include:

```text
Organisational hardening standard

System build standard

Vendor security guidance

CIS Benchmark

DISA STIG

Application security requirements

Cloud provider recommendations
```

Do not combine multiple baselines without understanding their intended environment.

---

# 109. CIS Benchmarks

CIS publishes security configuration guidance for multiple Linux distributions.

Use the benchmark matching:

```text
Distribution

Version

System role

Profile
```

A benchmark deviation should initially be described as a configuration deviation unless actual security impact has been established.

---

# 110. Security Control Evidence

Capture evidence such as:

```text
Hostname

Distribution

Kernel

Current identity

SELinux state

SELinux context

AppArmor state

AppArmor profile

seccomp state

NoNewPrivileges

Capabilities

Namespaces

Mount options

Kernel hardening settings

systemd security properties

PAM configuration

SSH effective configuration

Firewall state

Listening services

Audit configuration

Logging configuration

Patch state
```

Only collect what is relevant to the assessment.

---

# 111. Evidence Quality

Good evidence answers:

```text
What control exists?

Where is it configured?

What workload does it protect?

Is it enforcing?

What behavior does it restrict?

How was enforcement verified?

What alternative controls exist?
```

A screenshot of:

```text
getenforce
```

alone is not a complete security assessment.

---

# 112. Reporting Missing Hardening

Avoid:

> SELinux is disabled and therefore the server is vulnerable.

Prefer, when relevant:

> SELinux is not enabled on the assessed host. The application therefore does not receive SELinux-based mandatory access-control isolation. No direct privilege escalation was demonstrated from this condition alone; however, enabling an appropriate mandatory access-control policy would provide additional defence in depth against application compromise.

This distinguishes:

```text
Hardening Opportunity
```

from:

```text
Exploitable Vulnerability
```

---

# 113. Reporting an Effective Control

Security assessments should also recognise controls that materially limit impact.

Example:

> The assessed application executes as the dedicated `websvc` account with `NoNewPrivileges=yes`, a restricted capability bounding set and an enforcing AppArmor profile. Testing confirmed that access outside the application's approved data paths was denied by the mandatory access-control policy. These controls materially reduce the post-compromise privileges available to the service.

This provides useful defensive feedback.

---

# 114. Reporting a Control Failure

If a control is expected but ineffective:

> The system baseline requires the application to execute under an enforcing AppArmor profile. Although the profile is installed, it is configured in complain mode. As a result, policy violations are logged but are not blocked, and the application does not receive the intended mandatory access-control enforcement.

This is stronger than simply saying:

```text
AppArmor misconfigured
```

---

# 115. Remediation Strategy

Prioritise remediation using:

```text
Remove unnecessary privilege
        |
        v
Separate privileged functionality
        |
        v
Apply least privilege
        |
        v
Protect filesystem trust
        |
        v
Apply MAC
        |
        v
Apply service sandboxing
        |
        v
Restrict kernel interface
        |
        v
Restrict network exposure
        |
        v
Enable logging and detection
```

Defence in depth should support the primary security design rather than compensate for fundamentally unsafe privilege relationships.

---

# 116. SELinux Remediation

Where SELinux is part of the required security baseline:

```text
Use enforcing mode

Use appropriate domains

Correct file labels

Use narrowly scoped policy

Review booleans

Monitor AVC denials

Avoid unnecessary unconfined services
```

Do not solve policy problems by permanently disabling SELinux.

---

# 117. AppArmor Remediation

Where AppArmor is used:

```text
Use enforce mode

Create application-specific profiles

Limit filesystem access

Limit capabilities

Limit execution paths

Review policy denials

Avoid unnecessarily broad rules
```

Profiles must be tested against legitimate application functionality.

---

# 118. seccomp Remediation

Where appropriate:

```text
Identify required system calls

Apply allowlist-oriented filters

Use runtime defaults

Avoid unconfined container profiles

Test application functionality

Monitor failures
```

Overly restrictive filters can break applications.

---

# 119. Mount Hardening Remediation

Where operationally appropriate, consider:

```text
nosuid

nodev

noexec

ro
```

for filesystems that do not require the corresponding functionality.

The correct configuration depends on workload requirements.

---

# 120. systemd Remediation

Potential hardening includes:

```text
Dedicated User=

Dedicated Group=

NoNewPrivileges=yes

CapabilityBoundingSet=

ProtectSystem=

ProtectHome=

PrivateTmp=yes

PrivateDevices=yes

RestrictNamespaces=

RestrictAddressFamilies=

SystemCallFilter=
```

Apply controls incrementally and test application functionality.

---

# 121. Kernel Hardening Remediation

Use distribution-supported settings and organisational baselines.

Avoid copying arbitrary sysctl collections from the internet into production.

A safer process is:

```text
Identify Threat
      |
      v
Identify Relevant Kernel Control
      |
      v
Check Vendor Guidance
      |
      v
Test Compatibility
      |
      v
Deploy Through Configuration Management
      |
      v
Monitor
```

---

# 122. Firewall Remediation

Use least-exposure principles:

```text
Required Service
      |
      v
Required Interface
      |
      v
Required Source
      |
      v
Required Port
      |
      v
Explicit Allow
```

Avoid exposing administrative services broadly when narrower access is possible.

---

# 123. Logging Remediation

Ensure security-relevant events are:

```text
Generated

Protected

Retained

Centralised where appropriate

Correlated

Monitored

Actionable
```

Logging without monitoring provides limited detection value.

---

# 124. Retesting

After remediation, repeat the relevant assessment.

Examples:

```bash
getenforce
```

```bash
aa-status
```

```bash
grep -E '^(Cap|NoNewPrivs|Seccomp)' /proc/$$/status
```

```bash
findmnt
```

```bash
systemctl show example.service \
    -p NoNewPrivileges \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p PrivateTmp \
    -p PrivateDevices \
    -p ProtectSystem \
    -p ProtectHome
```

```bash
ss -lntu
```

Confirm:

```text
Control is enabled

Control is enforcing

Expected application functionality remains available

Previously demonstrated access is blocked

Logging captures relevant denials

No new unintended exposure was introduced
```

---

# Linux Security Controls Assessment Checklist

## System Context

- [ ] Identify distribution
- [ ] Identify distribution version
- [ ] Identify kernel
- [ ] Identify architecture
- [ ] Identify current user
- [ ] Record groups
- [ ] Determine whether host, VM or container

## SELinux

- [ ] Check whether installed
- [ ] Check runtime state
- [ ] Check enforcing/permissive mode
- [ ] Review relevant process domains
- [ ] Review file contexts
- [ ] Review relevant booleans
- [ ] Review denials
- [ ] Identify unconfined security-sensitive services

## AppArmor

- [ ] Check whether installed
- [ ] Review loaded profiles
- [ ] Identify enforcing profiles
- [ ] Identify complain-mode profiles
- [ ] Identify unconfined relevant processes
- [ ] Review relevant policy
- [ ] Review denials

## seccomp

- [ ] Inspect current process state
- [ ] Review relevant service/container state
- [ ] Identify filter mode
- [ ] Determine whether container is unconfined
- [ ] Correlate with capabilities

## No New Privileges

- [ ] Inspect current process
- [ ] Review systemd services
- [ ] Review container configuration
- [ ] Correlate with SUID/SGID
- [ ] Correlate with file capabilities

## Namespaces

- [ ] Inspect current namespaces
- [ ] Review UID mapping
- [ ] Review GID mapping
- [ ] Identify container context
- [ ] Distinguish namespace root from host root
- [ ] Review host-mounted resources

## Capabilities

- [ ] Enumerate file capabilities
- [ ] Inspect process capabilities
- [ ] Review service capabilities
- [ ] Review container capabilities
- [ ] Identify broad capabilities
- [ ] Review capability bounding sets

## SUID and SGID

- [ ] Enumerate privileged executables
- [ ] Review mount context
- [ ] Check `nosuid`
- [ ] Review NoNewPrivileges
- [ ] Review MAC restrictions

## Filesystems

- [ ] Review mount points
- [ ] Review `nosuid`
- [ ] Review `nodev`
- [ ] Review `noexec`
- [ ] Review read-only mounts
- [ ] Review `/tmp`
- [ ] Review `/var/tmp`
- [ ] Review `/dev/shm`
- [ ] Review application-specific mounts

## Kernel

- [ ] Review ASLR
- [ ] Review kernel pointer restrictions
- [ ] Review dmesg restrictions
- [ ] Review ptrace restrictions
- [ ] Review protected symlinks
- [ ] Review protected hard links
- [ ] Review protected FIFOs where supported
- [ ] Review protected regular files where supported
- [ ] Review module policy
- [ ] Review kernel lockdown where supported
- [ ] Review Secure Boot where relevant

## systemd

- [ ] Review service user
- [ ] Review service group
- [ ] Review NoNewPrivileges
- [ ] Review capability restrictions
- [ ] Review PrivateTmp
- [ ] Review PrivateDevices
- [ ] Review ProtectSystem
- [ ] Review ProtectHome
- [ ] Review namespace restrictions
- [ ] Review address-family restrictions
- [ ] Review system-call filtering
- [ ] Use `systemd-analyze security` where appropriate

## Authentication

- [ ] Review PAM configuration
- [ ] Review password policy
- [ ] Review account lockout
- [ ] Review SSH effective configuration
- [ ] Review root login policy
- [ ] Review password authentication
- [ ] Review authorised key management

## Network

- [ ] Identify firewall implementation
- [ ] Review firewall state
- [ ] Review default policies
- [ ] Review allowed services
- [ ] Review source restrictions
- [ ] Review listening services
- [ ] Review IPv6 exposure

## Logging

- [ ] Review auditd
- [ ] Review audit rules
- [ ] Review journald
- [ ] Review log permissions
- [ ] Review retention
- [ ] Review central logging
- [ ] Review monitoring
- [ ] Review time synchronisation

## Updates

- [ ] Review package state
- [ ] Review security update process
- [ ] Validate against vendor advisories
- [ ] Avoid version-only vulnerability conclusions

## Validation

- [ ] Determine which control applies
- [ ] Determine whether it is enforcing
- [ ] Determine actual security boundary
- [ ] Identify overlapping controls
- [ ] Test safely
- [ ] Document defensive controls
- [ ] Identify false positives

## Reporting

- [ ] Separate vulnerability from hardening opportunity
- [ ] Identify expected baseline
- [ ] Explain actual configuration
- [ ] Explain security impact
- [ ] Identify compensating controls
- [ ] Recommend practical remediation
- [ ] Define retest procedure

---

# Quick Linux Security Control Workflow

```text
Identify Host
     |
     v
Establish Identity
     |
     v
Identify Workload
     |
     +-----------------------+
     |                       |
     v                       v
Unix Permissions       Privilege Mechanisms
     |                       |
     |                  +----+----+
     |                  |         |
     |                 SUID   Capabilities
     |                  |         |
     +--------+---------+---------+
              |
              v
     Mandatory Access Control
              |
         +----+----+
         |         |
      SELinux   AppArmor
         |         |
         +----+----+
              |
              v
           seccomp
              |
              v
          Namespaces
              |
              v
        Mount Hardening
              |
              v
        Kernel Hardening
              |
              v
       systemd Sandboxing
              |
              v
         Authentication
              |
              v
           Firewall
              |
              v
        Audit / Logging
              |
              v
      Correlate Controls
              |
              v
       Validate Boundary
              |
              v
           Evidence
              |
              v
           Report
```

---

# Read-Only Command Reference

## System

```bash
id
uname -a
cat /etc/os-release
```

## SELinux

```bash
getenforce 2>/dev/null
sestatus 2>/dev/null
```

## SELinux Contexts

```bash
ps -eZ
ls -Z /path/to/file
```

## SELinux Denials

```bash
ausearch -m AVC,USER_AVC -ts recent 2>/dev/null
```

## AppArmor

```bash
aa-status 2>/dev/null
```

## seccomp

```bash
grep '^Seccomp' /proc/$$/status
```

## No New Privileges

```bash
grep '^NoNewPrivs' /proc/$$/status
```

## Capabilities

```bash
getcap -r /usr /usr/local /opt 2>/dev/null
grep '^Cap' /proc/$$/status
```

## Namespaces

```bash
ls -l /proc/$$/ns/
cat /proc/$$/uid_map
cat /proc/$$/gid_map
```

## Mounts

```bash
findmnt
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

## ASLR

```bash
sysctl kernel.randomize_va_space
```

## Kernel Pointer Restriction

```bash
sysctl kernel.kptr_restrict
```

## dmesg Restriction

```bash
sysctl kernel.dmesg_restrict
```

## ptrace Restriction

```bash
sysctl kernel.yama.ptrace_scope 2>/dev/null
```

## Filesystem Protections

```bash
sysctl fs.protected_symlinks
sysctl fs.protected_hardlinks
sysctl fs.protected_fifos 2>/dev/null
sysctl fs.protected_regular 2>/dev/null
```

## Kernel Modules

```bash
lsmod
sysctl kernel.modules_disabled
```

## Kernel Lockdown

```bash
cat /sys/kernel/security/lockdown 2>/dev/null
```

## Secure Boot

```bash
mokutil --sb-state 2>/dev/null
```

## systemd Service

```bash
systemctl cat example.service
```

## systemd Security Properties

```bash
systemctl show example.service \
    -p User \
    -p Group \
    -p NoNewPrivileges \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p PrivateTmp \
    -p PrivateDevices \
    -p ProtectSystem \
    -p ProtectHome
```

## systemd Security Analysis

```bash
systemd-analyze security example.service
```

## SSH Effective Configuration

```bash
sshd -T 2>/dev/null
```

## Listening Services

```bash
ss -lntu
```

## nftables

```bash
nft list ruleset
```

## iptables

```bash
iptables -S
```

## UFW

```bash
ufw status verbose
```

## firewalld

```bash
firewall-cmd --state
firewall-cmd --get-active-zones
```

## Audit

```bash
systemctl status auditd 2>/dev/null
auditctl -l 2>/dev/null
```

## Time

```bash
timedatectl status
```

---

# Practical Testing Model

For every Linux security control, use:

```text
1. What asset or workload is being protected?

2. What control should protect it?

3. Is the control present?

4. Is the control enabled?

5. Is it enforcing?

6. What exactly does it restrict?

7. Can the restriction be demonstrated safely?

8. Which other controls overlap with it?

9. Is the observed gap an exploitable vulnerability,
   a configuration weakness or a hardening opportunity?

10. What evidence supports the conclusion?

11. What remediation addresses the root cause?

12. How will the remediation be retested?
```

---

# Security Control Testing Mindset

Do not think:

```text
SELinux Disabled = Compromised

AppArmor Missing = Vulnerable

Firewall Disabled = Exploitable

noexec Missing = Code Execution

nosuid Missing = PrivEsc

Root Service = Vulnerability

Compiler Installed = Vulnerability

Old Kernel String = Vulnerable

NoNewPrivileges Disabled = PrivEsc

High systemd Exposure Score = Exploitable

One Hardening Control = Secure
```

Instead think:

```text
What Asset Am I Protecting?
        |
        v
What Threat Am I Testing?
        |
        v
Which Security Control Applies?
        |
        v
Is It Actually Enforcing?
        |
        v
What Does It Restrict?
        |
        v
Can I Validate the Restriction?
        |
        v
What Other Controls Apply?
        |
        v
Does a Real Security Boundary Exist?
        |
        v
Can That Boundary Be Crossed?
        |
        +---- No -> Document Effective Controls
        |
        +---- Yes -> Establish Root Cause
                         |
                         v
                      Evidence
                         |
                         v
                       Report
```

The absence of a hardening feature is not automatically a vulnerability.

The presence of a hardening feature is not automatically proof of security.

The effective security posture comes from the complete control chain.

---

# Related Notes

- [Linux Overview](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Filesystem Permissions](filesystem-permissions.md)
- [sudo Security](sudo.md)
- [Linux Scheduled Jobs](scheduled-jobs.md)
- [Linux SUID and SGID Security](suid-sgid.md)
- [Linux Capabilities Security](capabilities.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

---

# References

- [Linux Kernel Security Documentation](https://docs.kernel.org/security/){ target="_blank" rel="noopener noreferrer" }
- [Linux Kernel sysctl Documentation](https://docs.kernel.org/admin-guide/sysctl/){ target="_blank" rel="noopener noreferrer" }
- [Linux capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux seccomp(2)](https://man7.org/linux/man-pages/man2/seccomp.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux PR_SET_NO_NEW_PRIVS](https://man7.org/linux/man-pages/man2/PR_SET_NO_NEW_PRIVS.2const.html){ target="_blank" rel="noopener noreferrer" }
- [SELinux Project](https://selinuxproject.org/){ target="_blank" rel="noopener noreferrer" }
- [Red Hat - Using SELinux](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/){ target="_blank" rel="noopener noreferrer" }
- [AppArmor Documentation](https://apparmor.net/){ target="_blank" rel="noopener noreferrer" }
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html){ target="_blank" rel="noopener noreferrer" }
- [systemd-analyze](https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH sshd_config](https://man.openbsd.org/sshd_config){ target="_blank" rel="noopener noreferrer" }
- [nftables Wiki](https://wiki.nftables.org/){ target="_blank" rel="noopener noreferrer" }
- [Linux Audit Documentation](https://github.com/linux-audit/audit-documentation){ target="_blank" rel="noopener noreferrer" }
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks){ target="_blank" rel="noopener noreferrer" }

!!! tip "Correlate controls"

    A security control rarely tells the complete story. For example, a service may run with a powerful capability but still be strongly restricted by namespaces, SELinux, seccomp and systemd sandboxing. Assess the effective combination.

!!! tip "Recognise defensive successes"

    A penetration test should not only identify failures. When SELinux, AppArmor, NoNewPrivileges, mount restrictions or service sandboxing materially prevent an attack path, record that result. It provides useful evidence that the defensive architecture is working.

!!! tip "Separate hardening from vulnerabilities"

    Missing defence-in-depth controls can be important recommendations without being directly exploitable vulnerabilities. Make this distinction explicit in reporting.

!!! tip "Prefer effective configuration"

    Where possible, inspect runtime or effective configuration rather than only configuration files. Examples include `sshd -T`, `systemctl show`, `getenforce`, `findmnt` and process status under `/proc`.

!!! warning "Do not disable controls to prove they work"

    If SELinux, AppArmor, seccomp, firewalling or another security control prevents an assessment path, that is valuable evidence. Disabling the control can change the system's security posture and should only occur when explicitly authorised as part of a controlled test.
