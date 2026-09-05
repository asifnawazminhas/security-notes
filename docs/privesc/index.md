---
title: PrivEsc Explorer
description: Interactive Windows and Linux privilege escalation reference for authorised security assessments.
---

# PrivEsc Explorer

<div class="privesc-hero">

# PrivEsc Explorer

**Windows and Linux privilege escalation assessment reference**

Search privilege escalation techniques based on the permissions, binaries, services, groups, credentials, and configuration discovered during an authorised security assessment.

<div class="privesc-platform-buttons">
  <a href="windows/" class="privesc-platform-button">Windows Explorer</a>
  <a href="linux/" class="privesc-platform-button">Linux Explorer</a>
</div>

</div>

---

## Choose a Platform

<div class="privesc-platform-grid">

<a href="windows/" class="privesc-platform-card">

### Windows PrivEsc Explorer

Explore Windows privilege escalation opportunities involving:

- Services
- Scheduled tasks
- Registry permissions
- Filesystem permissions
- Windows privileges
- Access tokens
- DLL loading
- PATH configuration
- Credentials
- Application control
- UAC
- Installed software
- Drivers

**Open Windows Explorer ->**

</a>

<a href="linux/" class="privesc-platform-card">

### Linux PrivEsc Explorer

Explore Linux privilege escalation opportunities involving:

- sudo
- SUID
- SGID
- Linux capabilities
- systemd
- cron
- Writable files
- Writable directories
- Credentials
- Docker
- LXD
- NFS
- Privileged sockets
- Custom applications
- Kernel vulnerabilities

**Open Linux Explorer ->**

</a>

</div>

---

# What Is PrivEsc Explorer?

PrivEsc Explorer is designed as a fast operational companion to the detailed Windows and Linux documentation in this knowledge base.

The normal documentation workflow is:

```text
Topic
  |
  v
Read Documentation
  |
  v
Understand Technique
  |
  v
Perform Assessment
```

PrivEsc Explorer supports the reverse workflow commonly encountered during an assessment:

```text
Discovery
   |
   v
"What did I find?"
   |
   v
Search PrivEsc Explorer
   |
   v
Identify Relevant Technique
   |
   v
Check Preconditions
   |
   v
Validate Safely
   |
   v
Open Detailed Notes
```

For example:

```text
Discovery:

SeImpersonatePrivilege
        |
        v
Search:
"SeImpersonate"
        |
        v
Windows PrivEsc Explorer
        |
        v
Token / Privilege Technique
        |
        v
Prerequisites
        |
        v
Enumeration
        |
        v
Safe Validation
        |
        v
Detection
        |
        v
Remediation
```

Or on Linux:

```text
Discovery:

/usr/bin/python3 cap_setuid=ep
        |
        v
Search:
"python3" or "cap_setuid"
        |
        v
Linux PrivEsc Explorer
        |
        v
Linux Capabilities
        |
        v
Prerequisites
        |
        v
Validation
        |
        v
Remediation
```

---

# Explorer Model

Every technique follows the same structure:

```text
Technique
    |
    +-- Platform
    |
    +-- Category
    |
    +-- Description
    |
    +-- What You Found
    |
    +-- Preconditions
    |
    +-- Enumeration
    |
    +-- Validation
    |
    +-- Detection
    |
    +-- Remediation
    |
    +-- MITRE ATT&CK
    |
    +-- References
    |
    +-- Related Notes
```

This allows Windows and Linux techniques to use the same interface.

---

# Search by Discovery

The explorer is intended to support searches such as:

```text
SeImpersonatePrivilege
```

```text
AlwaysInstallElevated
```

```text
unquoted service path
```

```text
writable service
```

```text
scheduled task
```

```text
docker
```

```text
sudo
```

```text
SUID
```

```text
cap_setuid
```

```text
systemd
```

```text
cron
```

```text
NFS
```

The search engine can match:

```text
Technique names
Categories
Tags
Commands
Privileges
Binaries
Configuration
MITRE ATT&CK IDs
Descriptions
```

---

# Windows Categories

The Windows explorer is organised around the major privilege escalation surfaces.

```text
Windows
|
+-- Services
|
+-- Scheduled Tasks
|
+-- Filesystem
|
+-- Registry
|
+-- Windows Privileges
|
+-- Access Tokens
|
+-- DLL Loading
|
+-- PATH
|
+-- Credentials
|
+-- UAC
|
+-- Application Control
|
+-- Installed Software
|
+-- Drivers
|
+-- Configuration
```

Examples include:

```text
Writable Service Executable
Writable Service Directory
Weak Service Permissions
Unquoted Service Path
Writable Scheduled Task Action
AlwaysInstallElevated
SeImpersonatePrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
Writable PATH Directory
DLL Search Order Candidate
Stored Credentials
AutoLogon Credentials
Vulnerable Driver
```

---

# Linux Categories

The Linux explorer is organised around:

```text
Linux
|
+-- sudo
|
+-- SUID
|
+-- SGID
|
+-- Capabilities
|
+-- Services
|
+-- systemd
|
+-- Cron
|
+-- Filesystem
|
+-- Credentials
|
+-- Groups
|
+-- Docker
|
+-- LXD
|
+-- NFS
|
+-- Sockets
|
+-- Applications
|
+-- Kernel
```

Examples include:

```text
sudo Command
sudo NOPASSWD
sudo SETENV
SUID Binary
SGID Binary
CAP_SETUID
CAP_DAC_OVERRIDE
CAP_SYS_ADMIN
Writable systemd Executable
Writable systemd EnvironmentFile
Writable Cron Script
Writable PATH Directory
Docker Group Membership
Docker Socket Access
LXD Group Membership
NFS no_root_squash
Privileged Local Socket
Kernel LPE Candidate
```

---

# Technique Cards

Explorer results are displayed as technique cards.

A Windows example:

```text
+--------------------------------------------------+
| Writable Service Executable                     |
| WINDOWS | SERVICES | PRIVESC                    |
+--------------------------------------------------+
|                                                  |
| A service running with elevated privileges      |
| executes a binary writable by a lower-privileged|
| user.                                            |
|                                                  |
| WHAT YOU FOUND                                   |
|                                                  |
| Writable executable used by privileged service. |
|                                                  |
| CHECK                                            |
|                                                  |
| sc.exe qc ServiceName                            |
| icacls "C:\Path\service.exe"                     |
|                                                  |
| REQUIRES                                         |
|                                                  |
| [x] Elevated service context                     |
| [x] Writable executable                         |
| [ ] Execution/restart opportunity                |
|                                                  |
| MITRE                                            |
|                                                  |
| T1574.010                                        |
|                                                  |
| [View Technique]                                 |
+--------------------------------------------------+
```

A Linux example:

```text
+--------------------------------------------------+
| Dangerous File Capability                       |
| LINUX | CAPABILITIES | PRIVESC                  |
+--------------------------------------------------+
|                                                  |
| A user-accessible executable has a capability   |
| that may permit privileged operations.           |
|                                                  |
| WHAT YOU FOUND                                   |
|                                                  |
| /usr/bin/example cap_setuid=ep                   |
|                                                  |
| CHECK                                            |
|                                                  |
| getcap /usr/bin/example                          |
|                                                  |
| REQUIRES                                         |
|                                                  |
| [x] Executable accessible                        |
| [x] Security-sensitive capability               |
| [ ] Binary functionality supports abuse          |
|                                                  |
| MITRE                                            |
|                                                  |
| T1548                                            |
|                                                  |
| [View Technique]                                 |
+--------------------------------------------------+
```

---

# Technique Information

Opening a technique should provide enough information to understand and validate the finding without requiring immediate exploitation.

## What It Means

A short explanation of the security condition.

## What You Found

Examples of discoveries that should lead to the technique.

## Preconditions

Conditions required before the technique becomes relevant.

Example:

```text
[x] Service executes with elevated privileges

[x] Current user can modify the executable

[ ] Service can be restarted or otherwise executed
```

## Enumeration

Commands used to confirm the configuration.

## Validation

The minimum testing required to demonstrate the security impact.

## Detection

Relevant defensive telemetry and monitoring opportunities.

## Remediation

The configuration changes required to remove the privilege escalation path.

## MITRE ATT&CK

Where appropriate, techniques are mapped to MITRE ATT&CK.

## Related Notes

Links to the detailed knowledge-base pages provide deeper explanations.

---

# Safe Validation

PrivEsc Explorer is not intended to encourage unnecessary destructive exploitation.

The preferred validation model is:

```text
Discovery
    |
    v
Configuration Evidence
    |
    v
Permission Evidence
    |
    v
Privilege Relationship
    |
    v
Minimal Validation
    |
    v
Finding
```

For example:

```text
Standard User
      |
      | can write
      v
Service Executable
      |
      | executed by
      v
SYSTEM / root
```

If the privilege boundary can already be demonstrated from configuration and permission evidence, replacing the production executable may be unnecessary.

---

# Confidence Levels

Techniques can eventually expose a confidence indicator.

```text
CANDIDATE
```

A potentially interesting configuration has been identified.

```text
LIKELY
```

The important prerequisites appear to exist.

```text
CONFIRMED
```

The privilege boundary has been safely demonstrated.

This helps distinguish:

```text
Interesting Configuration
```

from:

```text
Confirmed Privilege Escalation
```

---

# Technique Metadata

The explorer uses structured data rather than hardcoding every technique into the interface.

Conceptually, a technique contains:

```yaml
id: windows-writable-service-binary

name: Writable Service Binary

platform: windows

category: services

severity: high

tags:
  - service
  - permissions
  - filesystem
  - system

requires:
  - Privileged service
  - Writable service executable
  - Service execution opportunity

mitre:
  - T1574.010

related:
  - /windows/services/
  - /windows/privilege-escalation/
```

The interface renders this information dynamically.

---

# Why Structured Data?

Separating technique data from presentation means:

```text
Technique Database
        |
        v
JSON
        |
        v
Explorer Engine
        |
        +----------------+
        |                |
        v                v
     Windows           Linux
        |                |
        v                v
 Technique Cards    Technique Cards
```

Adding another technique should not require rewriting the explorer.

Instead:

```text
Add JSON Object
       |
       v
Technique Automatically Appears
```

---

# Future Expansion

The same framework can later support:

```text
AD Explorer
```

```text
Command Explorer
```

```text
Web Technique Explorer
```

```text
Cloud Explorer
```

```text
LOLBIN Explorer
```

The architecture therefore becomes:

```text
                    Explorer Engine
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       PrivEsc         Active          Command
       Explorer        Directory       Explorer
          |            Explorer
      +---+---+
      |       |
      v       v
   Windows   Linux
```

---

# Operational Use

During an assessment:

```text
1. Enumerate the host.

2. Record interesting permissions and configuration.

3. Search the relevant term in PrivEsc Explorer.

4. Review prerequisites.

5. Confirm the privilege relationship.

6. Perform minimum necessary validation.

7. Collect evidence.

8. Open the detailed documentation where deeper analysis is required.

9. Report the root cause.

10. Recommend remediation.
```

---

# What Not to Report Automatically

PrivEsc Explorer results are candidates.

Do not automatically report:

```text
SUID binary exists
```

```text
Docker is installed
```

```text
User has a capability
```

```text
Service path contains spaces
```

```text
Old kernel version
```

```text
Writable directory exists
```

Each candidate must be evaluated in context.

For example:

```text
Writable Directory
       |
       v
Does privileged software trust it?
       |
   +---+---+
   |       |
   No      Yes
   |       |
   v       v
Low      Investigate
Value
```

---

# Evidence Model

For each confirmed technique, collect:

```text
Host
Current identity
Technique
Affected resource
Privilege level
Permissions
Configuration
Required conditions
Validation performed
Observed result
Security impact
MITRE ATT&CK mapping
Remediation
```

---

# Explorer Principles

PrivEsc Explorer follows several principles.

```text
Fast Search
```

Find techniques from discoveries made during enumeration.

```text
Context First
```

A configuration is not automatically a vulnerability.

```text
Minimal Validation
```

Demonstrate the privilege boundary without unnecessary system modification.

```text
Defender Visibility
```

Include detection opportunities alongside offensive assessment information.

```text
Remediation First-Class
```

Every technique should explain how the root cause can be removed.

```text
Documentation Integration
```

Explorer cards should link directly into the detailed notes.

---

# Windows Explorer

Use the Windows explorer when assessing:

```text
Windows Workstations
Windows Servers
Application Servers
Jump Hosts
Management Servers
Developer Workstations
VDI Systems
```

Open:

[Windows PrivEsc Explorer](windows.md)

Detailed documentation:

[Windows Privilege Escalation](../windows/privilege-escalation.md)

---

# Linux Explorer

Use the Linux explorer when assessing:

```text
Linux Servers
Web Servers
Application Servers
Developer Systems
Containers
Cloud Workloads
Infrastructure Servers
```

Open:

[Linux PrivEsc Explorer](linux.md)

Detailed documentation:

[Linux Privilege Escalation](../linux/privilege-escalation.md)

---

# Related Notes

- [Windows](../windows/index.md)
- [Windows Enumeration](../windows/enumeration.md)
- [Windows Services](../windows/services.md)
- [Windows Credentials](../windows/credentials.md)
- [Windows Privilege Escalation](../windows/privilege-escalation.md)
- [Linux](../linux/index.md)
- [Linux Enumeration](../linux/enumeration.md)
- [Linux Services](../linux/services.md)
- [Linux Credentials](../linux/credentials.md)
- [Linux Privilege Escalation](../linux/privilege-escalation.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.org/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [LOLAD](https://lolad-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [WADComs](https://wadcoms.github.io/){ target="_blank" rel="noopener noreferrer" }
- [Command Manager](https://commandmgr.com/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Windows Documentation](https://learn.microsoft.com/windows/){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages](https://man7.org/linux/man-pages/){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [systemd](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }

---

> PrivEsc Explorer is intended for authorised security assessments, security research, defensive validation, and controlled lab environments. A technique appearing in the explorer represents an assessment candidate, not automatically a confirmed vulnerability. Validate the actual privilege boundary and use the minimum testing necessary to demonstrate security impact.
