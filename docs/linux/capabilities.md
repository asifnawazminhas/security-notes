---
title: Linux Capabilities Security
description: Practical Linux capabilities security assessment covering capability enumeration, file and process capabilities, effective and permitted sets, dangerous capability combinations, privileged binaries, containers, systemd, GTFOBins and privilege escalation analysis.
---

# Linux Capabilities Security

Linux capabilities divide traditional root privileges into smaller units that can be granted independently to processes and executable files.

Instead of giving a process unrestricted UID 0 privileges, Linux can grant only the specific privileged operations that the application requires.

Examples include:

```text
CAP_NET_BIND_SERVICE

CAP_NET_RAW

CAP_CHOWN

CAP_DAC_OVERRIDE

CAP_SETUID

CAP_SETGID

CAP_SYS_PTRACE

CAP_SYS_ADMIN
```

Capabilities are therefore an important least-privilege mechanism.

They are also important during security assessments because an incorrectly assigned capability can provide a lower-privileged user with access far beyond what was intended.

The key question is not:

> Does this binary have a Linux capability?

The key question is:

> What security-sensitive operation does the capability permit, and can the current user use the executable or process to cross an intended security boundary?

A useful assessment model is:

```text
Current User
     |
     v
Executable / Process
     |
     v
Linux Capability
     |
     v
Privileged Operation
     |
     +---- File access
     +---- UID / GID manipulation
     +---- Process interaction
     +---- Network operations
     +---- Kernel administration
     +---- Namespace operations
     |
     v
Can User Control the Operation?
     |
  +--+--+
  |     |
 No    Yes
  |     |
  v     v
Record  Validate Security Boundary
```

!!! warning "Authorised Security Testing"

    Perform capability testing only on systems you own or have explicit permission to assess. Prefer enumeration and controlled validation. Do not modify privileged files, process credentials, namespaces, kernel configuration or production capabilities merely to demonstrate impact.

---

# 1. Why Linux Capabilities Exist

Traditional Unix privilege historically centered heavily around:

```text
UID 0
```

A root process could perform a broad range of privileged operations.

Linux capabilities divide many of those operations into individual privilege units.

Conceptually:

```text
Traditional Root
      |
      +---- Change UID
      +---- Change GID
      +---- Bypass file permissions
      +---- Bind privileged ports
      +---- Raw networking
      +---- Trace processes
      +---- Change ownership
      +---- System administration
```

Capabilities allow selected operations to be delegated without necessarily granting unrestricted root authority.

The security goal is:

```text
Only the privilege actually required
```

rather than:

```text
All root privileges
```

---

# 2. Capabilities Are Not Automatically Vulnerabilities

Finding:

```text
/usr/bin/example cap_net_raw=ep
```

does not automatically mean the host is vulnerable.

The capability may be:

```text
Required by the application

Intentionally assigned

Narrowly scoped

Protected by application logic

Restricted by namespaces

Constrained by SELinux or AppArmor
```

A security finding requires understanding what the executable allows the current user to do with the granted capability.

---

# 3. Capability Sets

Linux maintains multiple capability sets associated with threads and executable transitions.

Important sets include:

```text
Permitted

Effective

Inheritable

Bounding

Ambient
```

These sets serve different purposes.

A simplified model is:

```text
             Capability Model
                    |
       +------------+------------+
       |            |            |
       v            v            v
   Permitted     Effective    Inheritable
       |            |
       |            +---- Capabilities currently used
       |
       +---- Capabilities the thread may make effective

       +------------+------------+
       |                         |
       v                         v
    Bounding                   Ambient
       |                         |
       +---- Limits              +---- Can survive certain
            capabilities              exec transitions
```

Capability behavior during `execve()` is more detailed than this simplified representation.

For precise behavior, consult `capabilities(7)`.

---

# 4. Permitted Set

The permitted set defines capabilities that a thread may potentially make effective.

Conceptually:

```text
Permitted
    |
    v
Maximum capabilities available
to the thread under the current
credential state
```

A capability outside the permitted set generally cannot simply be enabled by the process.

---

# 5. Effective Set

The effective set contains capabilities currently used by the kernel when performing capability checks.

Conceptually:

```text
Operation Requested
       |
       v
Kernel Capability Check
       |
       v
Capability in Effective Set?
```

The effective set is therefore especially important when examining a running process.

---

# 6. Inheritable Set

The inheritable set participates in capability handling across program execution.

Its exact behavior depends on:

```text
Process capability state

Executable capability metadata

execve() rules

Other capability sets
```

Do not interpret the inheritable set in isolation.

---

# 7. Bounding Set

The capability bounding set limits capabilities that can be acquired through executable file capability mechanisms.

It acts as an important upper boundary.

A capability outside the bounding set cannot generally be gained through normal file capability transitions.

Inspecting the bounding set can therefore help explain why a capability does or does not become available.

---

# 8. Ambient Capabilities

Ambient capabilities provide a mechanism for retaining selected capabilities across execution of non-privileged programs under specific conditions.

They are particularly relevant to:

```text
Services

Containers

Application launchers

systemd units
```

Ambient capabilities should be reviewed when investigating a process that appears to retain privileges after executing another program.

---

# 9. File Capabilities

Capabilities can be associated with executable files.

Example:

```text
/usr/bin/ping cap_net_raw=ep
```

This allows selected privileged functionality without necessarily using SUID root.

File capabilities are stored as extended attributes.

They can be enumerated with:

```bash
getcap
```

---

# 10. Enumerate File Capabilities

A common enumeration command is:

```bash
getcap -r / 2>/dev/null
```

Representative output might resemble:

```text
/usr/bin/example cap_net_raw=ep
/usr/local/bin/helper cap_setuid=ep
```

Do not treat every result as vulnerable.

The next step is to determine:

```text
Which capability is assigned?

Which executable receives it?

Who can execute the binary?

Who can modify the binary?

What functionality does the binary expose?

What privilege does the capability actually provide?
```

---

# 11. Targeted Capability Enumeration

Searching the complete filesystem can be noisy.

Target common executable locations:

```bash
getcap -r /usr /usr/local /opt 2>/dev/null
```

Application-specific locations can also be checked:

```bash
getcap -r /srv 2>/dev/null
```

Targeted enumeration is often preferable on production systems.

---

# 12. Inspect One File

For a specific executable:

```bash
getcap /path/to/binary
```

Example:

```bash
getcap /usr/local/bin/helper
```

Then collect metadata:

```bash
stat /usr/local/bin/helper
```

```bash
getfacl /usr/local/bin/helper
```

```bash
namei -l /usr/local/bin/helper
```

This correlates capability assignment with filesystem trust.

---

# 13. Capability Notation

Capability output may contain forms such as:

```text
cap_net_raw=ep
```

The letters describe file capability flags.

Commonly encountered indicators include:

```text
e - Effective
p - Permitted
i - Inheritable
```

Interpret the capability together with the executable and runtime behavior rather than relying only on the letters.

---

# 14. Process Capabilities

Capabilities also exist on running processes.

A useful source is:

```text
/proc/<PID>/status
```

Relevant fields include:

```text
CapInh

CapPrm

CapEff

CapBnd

CapAmb
```

For the current shell:

```bash
grep '^Cap' /proc/$$/status
```

Representative structure:

```text
CapInh: 0000000000000000
CapPrm: 0000000000000000
CapEff: 0000000000000000
CapBnd: 000001ffffffffff
CapAmb: 0000000000000000
```

These values are hexadecimal bitmasks.

---

# 15. capsh

If available, `capsh` can help decode capability information.

Check:

```bash
command -v capsh
```

Display current capability information:

```bash
capsh --print
```

Decode a hexadecimal mask:

```bash
capsh --decode=0000000000000000
```

Replace the mask with the relevant value from `/proc/<PID>/status`.

---

# 16. getpcaps

If available:

```bash
command -v getpcaps
```

Inspect a process:

```bash
getpcaps <PID>
```

For the current shell:

```bash
getpcaps $$
```

This can provide a more readable view of process capabilities.

---

# 17. Establish the Current Identity

Before interpreting capabilities:

```bash
whoami
id
groups
```

Record:

```text
Username

UID

GID

Supplementary groups

Current capabilities
```

This is necessary because the same capability may have very different security significance depending on the existing privileges of the user.

---

# 18. Enumerate Current Process Capabilities

Use:

```bash
grep '^Cap' /proc/$$/status
```

and where available:

```bash
capsh --print
```

This helps answer:

```text
Does my current shell already possess capabilities?

Which capabilities are effective?

Which capabilities are permitted?

Which capabilities are bounded?

Are ambient capabilities present?
```

---

# 19. Inspect Other Processes

Where `/proc` permissions allow:

```bash
grep '^Cap' /proc/<PID>/status
```

Also inspect process identity:

```bash
ps -o pid,user,group,comm,args -p <PID>
```

Do not attempt to bypass `/proc` restrictions.

Process capability analysis can be useful when reviewing:

```text
Services

Containers

Agents

Network daemons

Custom applications
```

---

# 20. CAP_CHOWN

`CAP_CHOWN` permits bypassing restrictions associated with changing file ownership.

Security relevance depends on which files the process can operate on and what functionality the application exposes.

Assessment questions include:

```text
Can the user choose the target file?

Can ownership of protected resources be changed?

Are paths restricted?

Does the program validate ownership transitions?
```

Do not report the capability alone.

---

# 21. CAP_DAC_OVERRIDE

`CAP_DAC_OVERRIDE` can bypass discretionary access-control permission checks for certain file access operations.

This capability is highly security sensitive.

Conceptually:

```text
Normal User
    |
    v
Unix Permission Check
    |
   Denied

Process with CAP_DAC_OVERRIDE
    |
    v
May bypass relevant DAC checks
```

If an interpreter, file-management utility or highly flexible custom program receives this capability, the impact can be substantial.

---

# 22. CAP_DAC_READ_SEARCH

`CAP_DAC_READ_SEARCH` can bypass selected discretionary access checks related to reading files and traversing directories.

This can create confidentiality impact even where arbitrary file modification is not possible.

Potentially sensitive resources include:

```text
Credential stores

Private keys

Application secrets

Configuration files

Backups
```

The actual impact depends on the executable's functionality.

---

# 23. CAP_FOWNER

`CAP_FOWNER` permits bypassing certain permission checks that normally require the filesystem UID of the process to match the file owner.

This can affect operations such as selected permission and metadata changes.

Assess what operations the application exposes rather than equating the capability directly with root access.

---

# 24. CAP_FSETID

`CAP_FSETID` affects preservation and handling of SUID and SGID bits during certain file modifications.

It is generally less directly useful than some broader capabilities but can become relevant in combination with writable privileged files or other delegated operations.

Capability combinations should therefore be reviewed together.

---

# 25. CAP_SETUID

`CAP_SETUID` is particularly security sensitive.

It permits selected manipulation of process user IDs.

A flexible executable with:

```text
cap_setuid=ep
```

deserves immediate investigation.

The core question is:

> Can the current user use the application's intended or unintended functionality to select a more privileged UID?

Do not modify system identities merely to demonstrate the condition.

---

# 26. CAP_SETGID

`CAP_SETGID` permits selected manipulation of process group IDs and supplementary groups.

This can provide access to resources controlled by privileged groups.

Potential impact includes:

```text
Protected files

Administrative sockets

Application data

Device access

Credential stores
```

The resulting privilege may be significant even without UID 0.

---

# 27. CAP_NET_BIND_SERVICE

`CAP_NET_BIND_SERVICE` permits binding Internet-domain sockets to privileged ports.

This is commonly and legitimately assigned to network services.

Example use:

```text
Web service binding to TCP 80 or 443
```

This capability alone usually does not imply local privilege escalation.

Assess whether the assignment matches the application's intended role.

---

# 28. CAP_NET_RAW

`CAP_NET_RAW` allows operations involving raw and packet sockets.

It may be legitimately used by networking utilities.

Security implications can include expanded ability to perform certain network operations.

Do not automatically equate:

```text
CAP_NET_RAW
```

with:

```text
Root compromise
```

The impact depends on environment and exposed functionality.

---

# 29. CAP_NET_ADMIN

`CAP_NET_ADMIN` permits numerous network-administration operations.

Potential functionality includes management of:

```text
Interfaces

Routing

Firewall-related configuration

Traffic control

Network namespaces
```

This is a broad and security-sensitive capability.

Its significance can be particularly important inside containers.

---

# 30. CAP_SYS_PTRACE

`CAP_SYS_PTRACE` allows selected process tracing operations beyond ordinary same-user restrictions.

Potential impact can include interaction with processes containing:

```text
Credentials

Tokens

Secrets

Sensitive application state
```

The practical boundary depends on:

```text
Target process

Namespaces

LSM policy

Kernel ptrace restrictions

Application functionality
```

---

# 31. CAP_SYS_CHROOT

`CAP_SYS_CHROOT` permits use of `chroot()`.

By itself, this should not simply be described as "root access."

Its security significance depends on:

```text
Other capabilities

Filesystem control

Namespace context

Application functionality
```

Capabilities often become more important in combination.

---

# 32. CAP_SYS_ADMIN

`CAP_SYS_ADMIN` is one of the broadest Linux capabilities.

It covers many administrative operations.

It is frequently described as capability-heavy because a large number of kernel operations historically depend on it.

A process with `CAP_SYS_ADMIN` deserves careful investigation.

Potentially relevant areas include:

```text
Mount-related operations

Namespaces

Filesystem administration

Kernel interfaces

Various system-management operations
```

Do not assume every process with this capability can automatically compromise the host.

Namespaces and other controls can materially restrict its scope.

---

# 33. CAP_SYS_MODULE

`CAP_SYS_MODULE` permits loading and unloading kernel modules.

On a host where the capability is effective in the relevant namespace and kernel configuration, this is extremely security sensitive.

A lower-privileged user should not normally have arbitrary access to functionality exposing this capability.

---

# 34. CAP_SYS_RAWIO

`CAP_SYS_RAWIO` permits selected raw I/O operations.

It is highly privileged and unusual for ordinary applications.

If discovered on a custom or user-accessible executable, investigate:

```text
Why is it required?

Which operations are exposed?

Can arbitrary addresses or devices be selected?

What additional controls exist?
```

---

# 35. CAP_MKNOD

`CAP_MKNOD` permits creation of special files using `mknod()` under applicable conditions.

This can be particularly important in container security when combined with:

```text
Device access

Mounts

Other capabilities
```

Do not assess it in isolation from the surrounding namespace and device policy.

---

# 36. CAP_SETFCAP

`CAP_SETFCAP` permits setting file capabilities.

This capability is security sensitive because file capabilities can alter the privilege obtained when an executable runs.

Assessment questions include:

```text
Which files can the process modify?

Can it set capabilities on executable files?

Which filesystem is involved?

Are namespace restrictions present?

Can another user execute the resulting file?
```

---

# 37. CAP_KILL

`CAP_KILL` permits bypassing certain permission checks for sending signals to processes.

This can affect availability and process control.

The practical impact depends on:

```text
Which processes are reachable?

Which signals can be selected?

Does the application expose arbitrary targets?
```

It does not automatically provide arbitrary code execution.

---

# 38. CAP_AUDIT_WRITE

`CAP_AUDIT_WRITE` allows writing records to the kernel auditing log.

It is commonly present in container configurations and some service contexts.

Do not classify it as host compromise by itself.

Determine whether the application has additional capabilities or security-sensitive functionality.

---

# 39. Prioritising Capabilities

During privilege escalation review, capabilities that often deserve higher priority include:

```text
CAP_DAC_OVERRIDE

CAP_DAC_READ_SEARCH

CAP_SETUID

CAP_SETGID

CAP_SYS_ADMIN

CAP_SYS_PTRACE

CAP_SYS_MODULE

CAP_SYS_RAWIO

CAP_SETFCAP
```

This is not a complete vulnerability ranking.

Impact depends on:

```text
Executable

Functionality

Namespace

Filesystem

Configuration

Other capability sets

Security controls
```

---

# 40. Capability Combinations

Capabilities should not always be assessed individually.

Example:

```text
CAP_SETUID
+
Flexible interpreter
```

may be much more significant than:

```text
CAP_SETUID
+
Narrow custom helper
```

Similarly:

```text
CAP_SYS_ADMIN
+
Container mount access
```

requires different analysis from:

```text
CAP_SYS_ADMIN
+
Strongly restricted namespace
```

Assess the complete privilege combination.

---

# 41. Interpreters with Capabilities

Interpreters and general-purpose runtime environments deserve additional scrutiny when assigned capabilities.

Examples can include:

```text
Python

Perl

Ruby

Node.js

Shells
```

The reason is their flexibility.

A narrow application may expose only one privileged operation.

A general-purpose interpreter can potentially expose many operations available through its language runtime.

Do not execute privilege-escalation snippets simply because an interpreter appears in capability enumeration.

First establish:

```text
Capability

Executable path

File ownership

Runtime version

Mount context

Actual capability behavior

Authorised validation method
```

---

# 42. Editors and File Utilities

General-purpose tools capable of reading or writing arbitrary files can also become security sensitive when assigned filesystem-related capabilities.

Examples include tools that can:

```text
Read arbitrary paths

Write arbitrary paths

Change ownership

Change permissions

Execute commands
```

The combination of capability and exposed functionality determines the impact.

---

# 43. GTFOBins

GTFOBins documents legitimate Unix binaries whose functionality can become security relevant when used with mechanisms such as:

```text
sudo

SUID

capabilities
```

Use:

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

A useful workflow is:

```text
Capability Found
      |
      v
Identify Binary
      |
      v
Check GTFOBins
      |
      v
Review Capability-Specific Entry
      |
      v
Confirm Local Preconditions
      |
      v
Validate Safely
```

A GTFOBins match is not automatic proof of exploitability.

---

# 44. Writable Capability-Enabled Binary

A capability-enabled executable writable by an untrusted user is highly security sensitive.

Inspect:

```bash
stat /path/to/binary
```

```bash
getfacl /path/to/binary
```

```bash
namei -l /path/to/binary
```

Check effective write access:

```bash
if test -w /path/to/binary; then
    echo "[+] Current context reports write access"
else
    echo "[-] Current context does not report write access"
fi
```

Do not replace the executable.

The combination of:

```text
Privileged capability
+
Untrusted modification
```

can itself establish a serious trust-boundary problem.

---

# 45. Parent Directory Permissions

As with SUID binaries, inspect the complete path.

```bash
namei -l /path/to/binary
```

A protected file can exist inside a directory where another principal has unexpected control over directory entries.

See [Linux Filesystem Permissions](filesystem-permissions.md).

---

# 46. POSIX ACLs

Inspect:

```bash
getfacl /path/to/binary
```

Traditional mode bits do not show every effective permission.

Named users or groups may have unexpected write access through ACLs.

---

# 47. File Capability Extended Attributes

File capabilities are implemented using extended attributes.

Inspect extended attributes where useful:

```bash
getfattr -d -m - /path/to/binary 2>/dev/null
```

The exact representation should normally be interpreted using capability-aware tools such as:

```bash
getcap
```

rather than manually decoding raw extended attribute data.

---

# 48. Copying Capability-Enabled Files

Do not assume that copying a file automatically preserves its capability metadata.

Whether extended attributes are preserved depends on:

```text
Copy mechanism

Filesystem

Command options

Privileges

Destination support
```

This matters during:

```text
Deployment

Backups

Restoration

Container image construction
```

A capability can disappear or unexpectedly persist depending on operational procedures.

---

# 49. Filesystem Support

File capabilities depend on filesystem and kernel support.

When capability behavior is unexpected, inspect:

```bash
findmnt -T /path/to/binary
```

and filesystem characteristics.

Do not infer effective privilege solely from metadata without considering the execution environment.

---

# 50. nosuid and File Capabilities

The `nosuid` mount option is relevant not only to SUID/SGID execution but also to file capabilities.

Inspect:

```bash
findmnt -T /path/to/binary
```

If:

```text
nosuid
```

is present, capability behavior may be affected.

Therefore:

```text
getcap shows capability
```

does not by itself prove that the capability becomes effective during execution.

---

# 51. systemd Capabilities

systemd can configure capabilities for services.

Relevant directives include:

```text
CapabilityBoundingSet=

AmbientCapabilities=

NoNewPrivileges=
```

Inspect a service:

```bash
systemctl cat example.service
```

Also inspect effective properties:

```bash
systemctl show example.service \
    -p User \
    -p Group \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p NoNewPrivileges
```

These settings can materially affect service privilege.

---

# 52. CapabilityBoundingSet

A systemd service can restrict capabilities with:

```text
CapabilityBoundingSet=
```

Conceptually:

```text
Potential Service Privileges
          |
          v
CapabilityBoundingSet
          |
          v
Reduced Capability Boundary
```

A restrictive bounding set can reduce the impact of application compromise.

---

# 53. AmbientCapabilities

systemd can grant ambient capabilities to a service:

```text
AmbientCapabilities=
```

This allows selected capabilities to remain available through certain executable transitions.

If a service launches helper processes, ambient capabilities can be particularly relevant.

---

# 54. NoNewPrivileges

systemd can configure:

```text
NoNewPrivileges=yes
```

This prevents the service and its descendants from gaining additional privileges through `execve()` mechanisms such as SUID, SGID and file capabilities.

It is an important hardening control.

However:

```text
NoNewPrivileges=no
```

is not automatically a vulnerability.

Determine whether the application actually has a dangerous privilege transition available.

---

# 55. systemd Security Analysis

For an interesting service:

```bash
systemctl cat example.service
```

Then inspect:

```bash
systemctl show example.service \
    -p User \
    -p Group \
    -p ExecStart \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p NoNewPrivileges
```

Correlate this with:

```text
Executable permissions

File capabilities

Service identity

Writable configuration

Writable dependencies
```

---

# 56. systemd-analyze security

On compatible systemd systems:

```bash
systemd-analyze security example.service
```

This can provide useful service-hardening information.

Treat the score as guidance rather than a vulnerability verdict.

A service with a poor exposure score is not automatically exploitable.

A service with a good score is not automatically secure.

---

# 57. Containers

Capabilities are particularly important in container security.

Containers commonly operate with a reduced capability set rather than unrestricted host root privilege.

Inspect the current process:

```bash
grep '^Cap' /proc/$$/status
```

Where available:

```bash
capsh --print
```

Determine:

```text
Which capabilities are present?

Which namespace applies?

Which host resources are mounted?

Which devices are available?

Is the process container root?

Is a user namespace used?
```

---

# 58. Container Root Is Not Automatically Host Root

A process can have:

```text
uid=0(root)
```

inside a container while remaining isolated from the host.

Similarly, capabilities may apply within a namespace rather than globally.

Assessment must distinguish:

```text
Container Privilege
```

from:

```text
Host Privilege
```

Do not report host compromise without demonstrating the actual boundary.

---

# 59. Dangerous Container Capability Combinations

Some capabilities deserve particular attention in containers.

Examples include:

```text
CAP_SYS_ADMIN

CAP_SYS_PTRACE

CAP_SYS_MODULE

CAP_NET_ADMIN

CAP_MKNOD

CAP_DAC_OVERRIDE
```

Their significance depends on:

```text
Namespace configuration

Device access

Host mounts

Kernel configuration

Seccomp

AppArmor

SELinux

Container runtime configuration
```

Do not evaluate container capabilities in isolation.

---

# 60. Seccomp

Container environments may use seccomp to restrict system calls.

Even where a process possesses a capability, a required system call may be blocked.

Therefore the practical security model can involve:

```text
UID / GID
   |
   v
Capabilities
   |
   v
Namespaces
   |
   v
seccomp
   |
   v
SELinux / AppArmor
   |
   v
Effective Operation
```

---

# 61. SELinux

Check:

```bash
getenforce 2>/dev/null
```

SELinux can restrict processes even when Unix permissions and capabilities would otherwise permit an operation.

Capability analysis should therefore include mandatory access-control context where relevant.

---

# 62. AppArmor

Check:

```bash
aa-status 2>/dev/null
```

AppArmor can constrain:

```text
Filesystem access

Network operations

Capabilities

Process execution
```

A capability-enabled process may still be limited by its profile.

---

# 63. Capability Logging

Kernel or audit logs may provide evidence of denied capability operations.

Where Linux Audit is configured, relevant events may include capability-related denials.

Search carefully according to system configuration.

For example:

```bash
journalctl --no-pager | grep -i capability
```

SELinux systems may also expose AVC denials.

Do not rely on absence of log entries as proof that a capability is unused.

---

# 64. Practical Validation - Capability-Enabled Binary

## Scenario

Enumeration identifies:

```text
/usr/local/bin/report-helper cap_dac_read_search=ep
```

## Step 1 - Establish Identity

```bash
id
```

## Step 2 - Confirm Capability

```bash
getcap /usr/local/bin/report-helper
```

## Step 3 - Inspect Metadata

```bash
stat /usr/local/bin/report-helper
```

```bash
getfacl /usr/local/bin/report-helper
```

## Step 4 - Inspect Complete Path

```bash
namei -l /usr/local/bin/report-helper
```

## Step 5 - Determine File Type

```bash
file /usr/local/bin/report-helper
```

## Step 6 - Inspect Mount Context

```bash
findmnt -T /usr/local/bin/report-helper
```

## Step 7 - Understand Functionality

Determine whether the program allows the user to select arbitrary files or only a narrowly defined resource.

The capability itself is not yet the complete finding.

---

# 65. Representative Positive Result

Suppose the assessment establishes:

```text
Current user:
analyst

Binary:
/usr/local/bin/report-reader

Capability:
cap_dac_read_search=ep

Functionality:
User can supply an arbitrary local path

Security boundary:
Normally unreadable files can be returned through the program
```

The relationship is:

```text
analyst
   |
   v
report-reader
   |
   v
CAP_DAC_READ_SEARCH
   |
   v
DAC Read Restrictions Bypassed
   |
   v
Protected File Accessible
```

This can support a confidentiality finding.

The impact should be described according to what was actually demonstrated.

---

# 66. Practical Validation - CAP_SETUID Candidate

## Scenario

Enumeration identifies:

```text
/usr/local/bin/vendor-helper cap_setuid=ep
```

Do not immediately attempt to obtain UID 0.

First establish:

```text
What does vendor-helper do?

Can the caller select a UID?

Does the program call setuid-family functions?

Does it drop privileges?

Is the binary an interpreter or general-purpose utility?

Is the capability actually effective?
```

Collect:

```bash
getcap /usr/local/bin/vendor-helper
stat /usr/local/bin/vendor-helper
file /usr/local/bin/vendor-helper
findmnt -T /usr/local/bin/vendor-helper
```

Where static analysis is appropriate:

```bash
readelf -Ws /usr/local/bin/vendor-helper | grep -E 'setuid|seteuid|setreuid|setresuid'
```

The presence of a symbol is a clue, not proof that the caller can control the operation.

---

# 67. Practical Validation - systemd Service

## Scenario

A service runs as:

```text
User=appsvc
```

and contains:

```text
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

This may be completely appropriate for a web service that needs to bind a privileged port.

Review:

```bash
systemctl cat application.service
```

```bash
systemctl show application.service \
    -p User \
    -p Group \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p NoNewPrivileges
```

Then determine whether the capability matches the service requirement.

This is an example where a capability is a security control rather than a vulnerability.

---

# 68. Practical Validation - Writable Binary

## Scenario

A binary has:

```text
cap_setuid=ep
```

and is writable by the:

```text
developers
```

group.

The assessed user belongs to that group.

Collect:

```bash
id
getcap /path/to/binary
stat /path/to/binary
getfacl /path/to/binary
namei -l /path/to/binary
findmnt -T /path/to/binary
```

If the capability is effective and the binary can be modified by an untrusted user, this establishes a serious privileged-code integrity problem.

Do not replace the executable.

---

# 69. Representative Negative Result

Suppose:

```text
/usr/bin/network-helper cap_net_bind_service=ep
```

is identified.

Further assessment shows:

```text
Distribution-managed binary

Expected capability

Root-owned

Not writable

Protected parent directories

Capability limited to binding privileged ports

Application exposes no broader privileged functionality

No unexpected dependency control identified
```

A reasonable conclusion is:

```text
The file capability was reviewed and appears consistent with the
application's intended least-privilege design. No unintended privilege
boundary was identified under the assessed configuration.
```

Do not report the capability simply because it exists.

---

# 70. False Positives

Common false positives include:

```text
Expected application capability

CAP_NET_BIND_SERVICE on a web service

CAP_NET_RAW on a networking utility where operationally required

Capability metadata on a nosuid filesystem

Capability restricted to a container namespace

Capability constrained by SELinux or AppArmor

Capability present in permitted set but not effective

GTFOBins technique that does not apply locally

Capability-enabled binary with narrowly restricted functionality

systemd capability intentionally replacing SUID root
```

Always validate actual behavior.

---

# 71. Automated Enumeration

Tools such as:

```text
LinPEAS

LinEnum

linux-smart-enumeration
```

can identify capability-enabled files and interesting process configurations.

Use automated results as leads.

```text
Automated Enumeration
        |
        v
Capability Candidate
        |
        v
Manual getcap Validation
        |
        v
Executable Analysis
        |
        v
Capability Semantics
        |
        v
Runtime Context
        |
        v
Security Boundary
```

---

# 72. Capability Collection Script

A concise read-only collection can include:

```bash
echo '=== IDENTITY ==='
id

echo
echo '=== FILE CAPABILITIES ==='
getcap -r /usr /usr/local /opt 2>/dev/null || true

echo
echo '=== CURRENT PROCESS CAPABILITIES ==='
grep '^Cap' /proc/$$/status 2>/dev/null || true

echo
echo '=== CAPSH ==='
capsh --print 2>/dev/null || true

echo
echo '=== SELINUX ==='
getenforce 2>/dev/null || true

echo
echo '=== APPARMOR ==='
aa-status 2>/dev/null || true
```

This provides useful initial context without modifying system state.

---

# 73. Evidence Collection

For each significant capability finding, record:

```text
Hostname

Distribution

Kernel

Current user

UID

GID

Groups

Executable path

File type

Owner

Group

Mode

ACL

Capability

Capability flags

Parent directory permissions

Mount point

Mount options

Package ownership

Program purpose

Relevant arguments

Process capability sets

Namespace context

systemd capability configuration

SELinux / AppArmor context

Validation procedure

Observed security impact
```

---

# 74. Evidence Chain

A strong capability finding normally establishes:

```text
1. The capability exists.

2. The capability is effective in the assessed context.

3. The lower-privileged user can invoke or influence the privileged operation.

4. The executable exposes functionality that uses the capability.

5. The functionality crosses an intended security boundary.

6. Other controls do not prevent the demonstrated impact.
```

This is stronger than simply presenting `getcap` output.

---

# 75. Reporting

Avoid:

> The binary has `CAP_SETUID`.

Avoid:

> Dangerous Linux capabilities were found.

Prefer:

> The executable `/usr/local/bin/vendor-helper` is accessible to non-administrative users and is assigned `CAP_SETUID`. The application's functionality allows the caller to influence the UID selected during a privileged operation, allowing the assessed user to obtain an identity beyond the intended application security boundary.

Only use this wording if the behavior has actually been validated.

---

# 76. Example Finding

## Observation

A user-accessible application exposes functionality beyond the intended scope of its assigned Linux capability.

## Current User

```text
analyst
```

## Executable

```text
/usr/local/bin/report-reader
```

## Capability

```text
cap_dac_read_search=ep
```

## Security Relationship

```text
analyst
   |
   v
report-reader
   |
   v
CAP_DAC_READ_SEARCH
   |
   v
Bypass Selected DAC Read Checks
   |
   v
Protected Data
```

## Impact

The capability permits the application to perform file reads that the invoking user could not normally perform. Because the application exposes insufficiently restricted path selection, the user can access protected information outside the intended application scope.

## Recommendation

Restrict the application to explicitly approved resources and remove the capability if it is not required.

---

# 77. Remediation

Capability remediation should focus on least privilege.

Potential actions include:

```text
Remove unnecessary file capabilities

Reduce broad capabilities

Replace broad capabilities with narrower ones

Restrict application functionality

Protect capability-enabled binaries

Protect parent directories

Protect configuration

Protect dependencies

Restrict service capability bounding sets

Use NoNewPrivileges where appropriate

Apply SELinux or AppArmor

Reduce container capabilities
```

Do not remove capabilities blindly if they are required for legitimate functionality.

---

# 78. Removing a File Capability

Administrators can remove file capabilities with:

```bash
setcap -r /path/to/binary
```

This should only be performed after confirming the capability is unnecessary.

During an assessment, normally recommend remediation rather than changing production capability assignments yourself.

---

# 79. Assign Only Required Capabilities

Avoid unnecessarily broad capability assignments.

Conceptually:

```text
Application Requirement
        |
        v
Identify Required Privileged Operation
        |
        v
Assign Minimum Capability
        |
        v
Restrict Application Interface
```

For example, a service requiring only a privileged network port should not automatically receive broad system-administration capabilities.

---

# 80. Restrict systemd Services

Where appropriate, consider service hardening such as:

```text
CapabilityBoundingSet=

AmbientCapabilities=

NoNewPrivileges=yes
```

along with other systemd sandboxing options.

The exact configuration must be tested against application requirements.

---

# 81. Container Hardening

Containers should normally receive only the capabilities required for their workload.

Review runtime configuration and remove unnecessary capabilities.

The security objective is:

```text
Default Reduced Capability Set
        |
        v
Drop Unnecessary Capabilities
        |
        v
Add Only Explicit Requirements
```

Avoid broad privilege such as:

```text
--privileged
```

unless there is a justified operational requirement and the resulting risk is understood.

---

# 82. Retesting

After remediation:

```bash
getcap /path/to/binary
```

or:

```bash
getcap -r /relevant/path 2>/dev/null
```

Inspect:

```bash
stat /path/to/binary
getfacl /path/to/binary
namei -l /path/to/binary
findmnt -T /path/to/binary
```

For services:

```bash
systemctl cat example.service
```

```bash
systemctl show example.service \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p NoNewPrivileges
```

Confirm:

```text
Unnecessary capability removed

Required capability narrowed

Application still functions

Writable dependency corrected

Security boundary no longer exists

Container or namespace restrictions remain effective
```

---

# Linux Capabilities Assessment Checklist

## Identity

- [ ] Identify current user
- [ ] Record UID
- [ ] Record GID
- [ ] Review supplementary groups
- [ ] Inspect current process capabilities

## File Capability Enumeration

- [ ] Run targeted `getcap`
- [ ] Review `/usr`
- [ ] Review `/usr/local`
- [ ] Review `/opt`
- [ ] Review application-specific locations
- [ ] Identify custom binaries
- [ ] Identify unusual interpreters or utilities

## File Metadata

- [ ] Inspect owner
- [ ] Inspect group
- [ ] Inspect mode
- [ ] Inspect ACL
- [ ] Inspect parent directories
- [ ] Identify file type
- [ ] Identify package ownership
- [ ] Inspect mount context

## Capability Analysis

- [ ] Identify capability
- [ ] Understand capability semantics
- [ ] Determine whether capability is effective
- [ ] Determine capability scope
- [ ] Review capability combinations
- [ ] Review bounding set
- [ ] Review ambient capabilities where relevant

## Program Functionality

- [ ] Determine intended purpose
- [ ] Review accepted arguments
- [ ] Review file access
- [ ] Review process interaction
- [ ] Review UID/GID manipulation
- [ ] Review network operations
- [ ] Review external command execution
- [ ] Review configuration
- [ ] Review dependencies

## Processes

- [ ] Review `/proc/<PID>/status`
- [ ] Decode capability masks where useful
- [ ] Review process identity
- [ ] Review namespace context
- [ ] Review service configuration

## systemd

- [ ] Review `CapabilityBoundingSet=`
- [ ] Review `AmbientCapabilities=`
- [ ] Review `NoNewPrivileges=`
- [ ] Review service user and group
- [ ] Review executable permissions
- [ ] Review writable dependencies

## Containers

- [ ] Determine whether inside a container
- [ ] Review effective capabilities
- [ ] Review namespace context
- [ ] Review host mounts
- [ ] Review device access
- [ ] Review seccomp
- [ ] Review SELinux/AppArmor
- [ ] Distinguish container root from host root

## Security Controls

- [ ] Review SELinux
- [ ] Review AppArmor
- [ ] Review mount options
- [ ] Review `nosuid`
- [ ] Review namespaces
- [ ] Review seccomp where relevant

## GTFOBins

- [ ] Check capability-enabled binaries
- [ ] Review capability-specific technique
- [ ] Confirm local prerequisites
- [ ] Confirm configuration
- [ ] Avoid unnecessary destructive validation

## Validation

- [ ] Confirm capability exists
- [ ] Confirm capability is effective
- [ ] Confirm user can invoke the operation
- [ ] Confirm privileged functionality
- [ ] Confirm security boundary
- [ ] Identify false positives
- [ ] Validate safely

## Evidence

- [ ] Capture identity
- [ ] Capture `getcap`
- [ ] Capture metadata
- [ ] Capture ACL
- [ ] Capture complete path
- [ ] Capture mount context
- [ ] Capture process capability sets
- [ ] Capture service configuration
- [ ] Capture namespace context
- [ ] Capture security controls

## Reporting

- [ ] Identify affected principal
- [ ] Identify executable or process
- [ ] Identify capability
- [ ] Explain capability functionality
- [ ] Explain controllable operation
- [ ] Explain security boundary
- [ ] Explain impact
- [ ] Recommend least-privilege remediation
- [ ] Define retest procedure

---

# Quick Capability Assessment Workflow

```text
Enumerate Capabilities
        |
        +---- File capabilities
        |
        +---- Process capabilities
        |
        +---- systemd capabilities
        |
        +---- Container capabilities
        |
        v
Identify Interesting Capability
        |
        v
Identify Executable / Process
        |
        v
Understand Capability Semantics
        |
        v
Determine Runtime Scope
        |
        +---- Host
        +---- Namespace
        +---- Container
        |
        v
Inspect Program Functionality
        |
        v
Can Current User Control
Capability-Backed Operation?
        |
     +--+--+
     |     |
    No    Yes
     |     |
     v     v
  Record   Does It Cross an
           Intended Boundary?
               |
            +--+--+
            |     |
           No    Yes
            |     |
            v     v
         Record  Validate
                    |
                    v
                 Evidence
                    |
                    v
                  Report
```

---

# Command Reference

## Identity

```bash
whoami
id
groups
```

## Enumerate File Capabilities

```bash
getcap -r / 2>/dev/null
```

## Targeted Enumeration

```bash
getcap -r /usr /usr/local /opt 2>/dev/null
```

## Inspect One File

```bash
getcap /path/to/binary
```

## File Metadata

```bash
stat /path/to/binary
```

## ACL

```bash
getfacl /path/to/binary
```

## Complete Path

```bash
namei -l /path/to/binary
```

## File Type

```bash
file /path/to/binary
```

## Extended Attributes

```bash
getfattr -d -m - /path/to/binary 2>/dev/null
```

## Current Process Capabilities

```bash
grep '^Cap' /proc/$$/status
```

## capsh

```bash
capsh --print
```

## Decode Capability Mask

```bash
capsh --decode=<hexadecimal-mask>
```

## Process Capabilities

```bash
getpcaps <PID>
```

## Mount Context

```bash
findmnt -T /path/to/binary
```

## systemd Service Capabilities

```bash
systemctl show example.service \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities \
    -p NoNewPrivileges
```

## systemd Security Review

```bash
systemd-analyze security example.service
```

## SELinux

```bash
getenforce 2>/dev/null
```

## AppArmor

```bash
aa-status 2>/dev/null
```

---

# Capability Testing Mindset

Do not think:

```text
Capability = Vulnerability

CAP_SETUID = Automatic Root

CAP_SYS_ADMIN = Guaranteed Host Escape

CAP_NET_RAW = Root

GTFOBins Match = Exploitable

Container Root = Host Root

Capability Present = Capability Effective

NoNewPrivileges Disabled = Vulnerability
```

Instead think:

```text
Which Capability Exists?
        |
        v
Where Does It Apply?
        |
        v
Is It Effective?
        |
        v
Which Operation Does It Permit?
        |
        v
Which Program Exposes That Operation?
        |
        v
What Can the User Control?
        |
        v
Which Namespace Applies?
        |
        v
What Other Security Controls Apply?
        |
        v
Does the Capability Cross an
Intended Security Boundary?
        |
        v
Can the Impact Be Validated Safely?
```

Capabilities are privilege building blocks.

The security conclusion comes from how those building blocks are exposed to the user.

---

# Related Notes

- [Linux Overview](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Filesystem Permissions](filesystem-permissions.md)
- [sudo Security](sudo.md)
- [Linux Scheduled Jobs](scheduled-jobs.md)
- [Linux SUID and SGID Security](suid-sgid.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

The remaining dedicated Linux expansion page is:

[Linux Security Controls](security-controls.md)

---

# References

- [Linux capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux prctl(2)](https://man7.org/linux/man-pages/man2/prctl.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux setuid(2)](https://man7.org/linux/man-pages/man2/setuid.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux setgid(2)](https://man7.org/linux/man-pages/man2/setgid.2.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.resource-control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

!!! tip "Capabilities can be safer than SUID root"

    A narrowly assigned capability can be a strong least-privilege control. The goal of an assessment is not to eliminate capabilities, but to determine whether the application receives more authority than it requires or exposes that authority unsafely.

!!! tip "Prioritise flexible executables"

    General-purpose interpreters, editors, file-management tools and highly configurable custom programs deserve additional attention when assigned powerful capabilities because their functionality may expose more of the delegated privilege.

!!! tip "Check runtime scope"

    A capability observed inside a container or namespace may not apply to the host. Determine the namespace, mounts, devices and surrounding security controls before drawing conclusions about impact.

!!! tip "Correlate file and process capabilities"

    `getcap` shows file capability assignments, while `/proc/<PID>/status`, `getpcaps` and `capsh` help explain capabilities associated with running processes. Both views can be necessary to understand actual privilege.

!!! warning "Capability metadata is only the starting point"

    A defensible finding requires evidence that the capability is effective and that user-controlled functionality can use it to cross an intended security boundary.
