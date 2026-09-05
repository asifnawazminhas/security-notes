---
title: PrivEsc Explorer
description: Interactive Windows and Linux privilege escalation reference for authorised security testing.
---

# PrivEsc Explorer

PrivEsc Explorer is an interactive privilege escalation reference for **Windows** and **Linux** systems.

Instead of starting with a technique name, the explorer is designed around a practical question:

> **What did I find?**

Search for an observation such as `SeImpersonatePrivilege`, `writable service`, `sudo`, `SUID`, `CAP_SETUID`, `Docker`, `cron`, or `PATH` and use the results to identify relevant privilege escalation candidates, validation steps, detection opportunities, and remediation guidance.

!!! warning "Authorised testing only"
    The techniques and commands in PrivEsc Explorer are intended for authorised penetration testing, security assessments, labs, CTF environments, and defensive research. Always remain within the agreed scope and rules of engagement.


---

## Choose a Platform

<div class="privesc-platform-grid">

<div class="privesc-platform-card privesc-platform-windows">

<h3>Windows PrivEsc Explorer</h3>

<p>
Explore Windows privilege escalation opportunities involving services,
scheduled tasks, registry permissions, filesystem permissions, Windows
privileges, access tokens, DLL loading, PATH configuration, credentials,
application control, UAC, installed software, and drivers.
</p>

<a class="md-button md-button--primary" href="windows/">
Open Windows Explorer
</a>

</div>

<div class="privesc-platform-card privesc-platform-linux">

<h3>Linux PrivEsc Explorer</h3>

<p>
Explore Linux privilege escalation opportunities involving sudo, SUID,
SGID, Linux capabilities, systemd, cron, writable files, writable
directories, credentials, Docker, LXD, NFS, privileged sockets, custom
applications, and kernel vulnerabilities.
</p>

<a class="md-button md-button--primary" href="linux/">
Open Linux Explorer
</a>

</div>

</div>


---

## What Is PrivEsc Explorer?

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
Perform Enumeration
  |
  v
Identify Candidate
  |
  v
Validate Candidate
```

PrivEsc Explorer also supports the reverse workflow commonly encountered during an assessment:

```text
Enumeration Finding
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
Review Preconditions
        |
        v
Perform Safe Validation
        |
        v
Determine Impact
        |
        v
Collect Evidence
        |
        v
Report and Remediate
```

This makes the explorer useful when enumeration has already produced something interesting but the security significance is not immediately clear.


---

## Search by What You Found

You do not need to know the exact technique name.

Search using the evidence you already have.

Examples include:

```text
SeImpersonate
SeBackup
SeDebug
service
scheduled task
writable
DLL
PATH
AlwaysInstallElevated
AppLocker
PowerShell
credential
driver
sudo
NOPASSWD
SETENV
SUID
SGID
CAP_SETUID
CAP_SYS_ADMIN
systemd
cron
Docker
docker.sock
LXD
NFS
no_root_squash
socket
kernel
```

The explorer searches across technique names, categories, summaries, prerequisites, enumeration commands, validation guidance, tags, and MITRE ATT&CK information.


---

## Explorer Workflow

A useful privilege escalation assessment can be represented as:

```text
Enumeration
    |
    v
Candidate
    |
    v
Context
    |
    v
Preconditions
    |
    v
Safe Validation
    |
    v
Exploitability
    |
    v
Impact
    |
    v
Evidence
    |
    v
Remediation
```

The important distinction is between **finding something interesting** and **confirming a privilege escalation path**.

For example:

```text
Writable File
```

does not automatically mean:

```text
Privilege Escalation
```

The real question is:

```text
Writable File
    |
    v
Who Uses It?
    |
    +--> Current User Only
    |       |
    |       v
    |     Low Interest
    |
    +--> Privileged Process
            |
            v
       Can It Be Modified?
            |
            v
       Is It Consumed?
            |
            v
       PrivEsc Candidate
```

PrivEsc Explorer is designed to preserve this distinction.


---

## Windows Privilege Escalation Model

Windows privilege escalation commonly involves relationships between:

```text
User
 |
 +--> Services
 |
 +--> Scheduled Tasks
 |
 +--> Filesystem Permissions
 |
 +--> Registry Permissions
 |
 +--> Windows Privileges
 |
 +--> Access Tokens
 |
 +--> DLL Loading
 |
 +--> PATH Resolution
 |
 +--> Credentials
 |
 +--> Application Control
 |
 +--> UAC
 |
 +--> Installed Applications
 |
 +--> Drivers
 |
 +--> Local Administrative Interfaces
 |
 +--> Security Configuration
```

The Windows explorer groups techniques into categories such as:

| Category | Examples |
|---|---|
| Services | Writable service executable, weak service permissions, unquoted service paths |
| Scheduled Tasks | Writable task actions and privileged scheduled execution |
| Privileges | SeImpersonate, SeBackup, SeRestore, SeDebug, SeLoadDriver |
| Filesystem | Writable privileged files and directories |
| Registry | Writable security-sensitive registry configuration |
| PATH | Writable PATH directories and unsafe executable resolution |
| DLL | DLL search-order and writable dependency candidates |
| Credentials | AutoLogon, PowerShell history, environment secrets, stored credentials |
| Application Control | AppLocker and PowerShell execution-control context |
| Drivers | Vulnerable or overly privileged driver candidates |
| Applications | Custom privileged applications and writable application resources |

Open the [Windows PrivEsc Explorer](windows/).


---

## Linux Privilege Escalation Model

Linux privilege escalation commonly involves relationships between:

```text
User
 |
 +--> sudo
 |
 +--> SUID / SGID
 |
 +--> Linux Capabilities
 |
 +--> systemd
 |
 +--> Cron
 |
 +--> Filesystem Permissions
 |
 +--> PATH Resolution
 |
 +--> Libraries
 |
 +--> Credentials
 |
 +--> Groups
 |
 +--> Containers
 |
 +--> Unix Sockets
 |
 +--> NFS
 |
 +--> Custom Applications
 |
 +--> Kernel
 |
 +--> Security Controls
```

The Linux explorer groups techniques into categories such as:

| Category | Examples |
|---|---|
| sudo | NOPASSWD, SETENV, wildcards, interpreters, editors |
| SUID / SGID | SUID binaries, custom SUID applications, SGID binaries |
| Capabilities | CAP_SETUID, CAP_DAC_OVERRIDE, CAP_SYS_ADMIN, CAP_SYS_PTRACE |
| systemd | Writable units, service scripts, binaries, environment files, timers |
| Cron | Writable scripts, unsafe PATH usage, privileged scheduled jobs |
| Filesystem | Writable files, directories, ACLs, parent-directory replacement |
| Credentials | Shell history, environment variables, SSH keys, application secrets |
| Groups | docker, disk, shadow, LXD, libvirt and administrative groups |
| Containers | Docker socket, privileged containers, sensitive host mounts |
| NFS | Export configuration and no_root_squash candidates |
| Libraries | Writable libraries, linker configuration and Python imports |
| Applications | Writable configuration, plugins and privileged management agents |
| Kernel | Kernel LPE candidates and exploitability controls |

Open the [Linux PrivEsc Explorer](linux/).


---

## Technique Cards

Explorer results are presented as technique cards.

A card can contain:

```text
Technique
 |
 +--> Platform
 |
 +--> Category
 |
 +--> Severity
 |
 +--> Confidence
 |
 +--> Summary
 |
 +--> What You Found
 |
 +--> Preconditions
 |
 +--> Enumeration Commands
 |
 +--> Validation
 |
 +--> Detection
 |
 +--> Remediation
 |
 +--> MITRE ATT&CK
 |
 +--> Tags
 |
 +--> Related Notes
```

The goal is to provide enough context to move from an enumeration result to a defensible security conclusion.


---

## Candidate Does Not Mean Vulnerable

One of the most important principles of the explorer is:

> **A candidate is not automatically a vulnerability.**

For example, finding:

```text
SeImpersonatePrivilege
```

does not by itself prove privilege escalation.

Likewise:

```text
SUID binary
```

does not automatically mean the binary can be abused.

And:

```text
docker group membership
```

must still be interpreted in the context of the Docker daemon, rootless operation, authorisation controls, and the intended administrative model.

The explorer therefore separates discovery from validation.


---

## Confidence Levels

Explorer entries use confidence levels to help communicate how strongly the discovered condition supports a privilege escalation conclusion.

### Candidate

A potentially relevant condition has been discovered, but additional context is required.

```text
Interesting Condition
        |
        v
Candidate
```

Examples:

```text
SUID binary discovered
CAP_SYS_PTRACE discovered
custom privileged service discovered
writable configuration discovered
```

These require further investigation.


### Likely

The important privilege relationship appears to exist, but practical impact may still depend on additional context.

```text
Condition
    +
Privilege Relationship
    |
    v
Likely
```

Examples might include:

```text
CAP_SETUID on a flexible executable
docker group access to a rootful daemon
writable privileged library
```

Further validation should still be performed.


### Confirmed

The privilege boundary itself has been established with sufficient evidence.

```text
Lower-Privileged User
        |
        v
Controls Resource
        |
        v
Privileged Consumer
        |
        v
Confirmed Boundary
```

For example:

```text
Root Service
    |
    v
Executes Script
    |
    v
Script Writable by Normal User
```

The relationship can often be confirmed without modifying the script or triggering privileged execution.


---

## Severity Is Contextual

Severity is provided as an assessment aid rather than an automatic final rating.

A technique may appear as:

```text
Critical
High
Medium
Low
Informational
```

but the final severity should consider:

```text
Required Access
      +
Exploit Preconditions
      +
Privilege Obtained
      +
Reliability
      +
Business Context
      +
Security Controls
      =
Final Risk
```

For example, a root-owned writable service executable is generally much more significant than an ordinary writable temporary file with no privileged consumer.


---

## Safe Validation

Privilege escalation testing can affect operating-system stability, services, scheduled jobs, authentication, and security controls.

Prefer the least invasive evidence that establishes the privilege relationship.

### Preferred

```text
Inspect permissions
Inspect ownership
Inspect ACLs
Inspect service configuration
Inspect sudo rules
Inspect capabilities
Inspect execution identity
Inspect PATH
Inspect task definitions
Inspect mount configuration
Inspect application configuration
```

### Avoid When Not Required

```text
Replacing production binaries
Modifying privileged scripts
Restarting critical services
Changing scheduled tasks
Loading kernel modules
Exploiting kernel vulnerabilities
Creating persistent privileged users
Disabling security controls
Modifying production configuration
```

A strong assessment demonstrates the security boundary with the minimum necessary system modification.


---

## Evidence Model

Useful evidence usually contains four elements:

```text
1. Identity
2. Controlled Resource
3. Privileged Consumer
4. Security Impact
```

For example:

```text
Identity
--------
CORP\user

Controlled Resource
-------------------
C:\Program Files\Example\Service.exe

Privileged Consumer
-------------------
ExampleService

Execution Identity
------------------
LocalSystem
```

or:

```text
Identity
--------
www-data

Controlled Resource
-------------------
/opt/example/backup.sh

Privileged Consumer
-------------------
root cron job

Execution Identity
------------------
root
```

This is considerably stronger than reporting only:

```text
File is writable
```

because the evidence establishes the complete privilege relationship.


---

## Validation Questions

When a candidate is discovered, ask:

```text
Who owns the resource?

Who can modify it?

Who consumes it?

What identity does the consumer run as?

When is it consumed?

Can the current user influence execution?

Are there additional security controls?

Is the behaviour intentional?

What privilege would actually be obtained?
```

Only then determine whether the condition represents a security finding.


---

## Detection

Privilege escalation paths frequently produce observable behaviour.

Useful defensive telemetry may include:

```text
Process creation
Service changes
Scheduled-task changes
sudo execution
File permission changes
ACL changes
SUID changes
Capability changes
systemd unit changes
Cron changes
Registry changes
DLL loading
Driver loading
Container creation
Docker API activity
Authentication events
Sensitive file access
```

Explorer cards include detection guidance where relevant so the same technique can support both offensive testing and defensive validation.


---

## Remediation

Most privilege escalation findings ultimately involve one or more trust-boundary problems.

Common remediation themes include:

```text
Least privilege
        |
        +--> Remove unnecessary administrative rights
        |
        +--> Restrict sudo delegation
        |
        +--> Remove unnecessary SUID / SGID
        |
        +--> Remove unnecessary capabilities
        |
        +--> Restrict privileged groups

Trusted resources
        |
        +--> Protect executables
        |
        +--> Protect scripts
        |
        +--> Protect configuration
        |
        +--> Protect libraries
        |
        +--> Protect registry keys
        |
        +--> Protect service definitions

Execution controls
        |
        +--> Use absolute paths
        |
        +--> Control PATH
        |
        +--> Harden application control
        |
        +--> Restrict privileged interpreters
        |
        +--> Harden service identities

Credential protection
        |
        +--> Remove plaintext secrets
        |
        +--> Rotate exposed credentials
        |
        +--> Protect private keys
        |
        +--> Use secret-management systems
```

The objective is not simply to block one command. It is to remove the underlying unsafe privilege relationship.


---

## Structured Data

The explorer interface is backed by structured JSON rather than hard-coded technique cards.

The current data files are:

```text
docs/data/privesc/windows.json
docs/data/privesc/linux.json
```

Each technique can contain fields such as:

```json
{
  "id": "example-technique",
  "name": "Example Technique",
  "platform": "windows",
  "category": "Services",
  "severity": "high",
  "confidence": "candidate",
  "summary": "Short description of the condition.",
  "found": [
    "What the tester discovered."
  ],
  "requires": [
    "Conditions required for practical impact."
  ],
  "commands": [
    "enumeration command"
  ],
  "validation": [
    "Safe validation guidance."
  ],
  "detection": [
    "Defensive detection guidance."
  ],
  "remediation": [
    "Recommended remediation."
  ],
  "mitre": [],
  "tags": [
    "example"
  ],
  "related": []
}
```

Keeping the data separate from the interface makes it easier to expand and maintain the explorer.


---

## Search Architecture

The explorer uses the following model:

```text
User Query
    |
    v
Tokenise Search
    |
    v
Search Technique Data
    |
    +--> Name
    +--> ID
    +--> Platform
    +--> Category
    +--> Severity
    +--> Confidence
    +--> Summary
    +--> Findings
    +--> Preconditions
    +--> Commands
    +--> Validation
    +--> Detection
    +--> Remediation
    +--> MITRE ATT&CK
    +--> Tags
    |
    v
Apply Filters
    |
    v
Sort Results
    |
    v
Render Technique Cards
```

This allows searches such as:

```text
writable service
```

or:

```text
docker root
```

or:

```text
SeBackup
```

without requiring the tester to know the internal technique ID.


---

## Recommended Assessment Workflow

Use the explorer as part of a broader privilege escalation methodology.

```text
1. Establish current identity
          |
          v
2. Enumerate privileges and groups
          |
          v
3. Enumerate privileged execution
          |
          v
4. Identify writable resources
          |
          v
5. Search PrivEsc Explorer
          |
          v
6. Review candidate prerequisites
          |
          v
7. Validate safely
          |
          v
8. Determine actual privilege impact
          |
          v
9. Collect evidence
          |
          v
10. Review detection opportunities
          |
          v
11. Recommend remediation
```

Do not rely exclusively on automated enumeration.

Automated tools are useful for finding candidates, but the tester still needs to understand the privilege relationship.


---

## Useful Enumeration Tools

PrivEsc Explorer is designed to complement manual enumeration and established assessment tools.

Examples include:

### Windows

```text
WinPEAS
PowerUp
Seatbelt
AccessChk
Process Monitor
Process Explorer
PowerShell
sc.exe
schtasks.exe
whoami.exe
icacls.exe
Get-Acl
Get-AppLockerPolicy
```

### Linux

```text
LinPEAS
LinEnum
pspy
sudo
find
getcap
getfacl
namei
systemctl
journalctl
ss
findmnt
capsh
```

Tool output should be treated as a starting point for investigation rather than automatic proof of a vulnerability.


---

## GTFOBins and Related References

For Linux, [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" } is an important reference for understanding security-sensitive functionality exposed by Unix binaries.

For Windows, [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" } documents Windows binaries, scripts, and libraries that can provide security-relevant functionality.

For Active Directory, [LOlAD](https://lolad-project.github.io/){ target="_blank" rel="noopener noreferrer" } provides a useful reference for Active Directory attack techniques and commands.

PrivEsc Explorer does not attempt to duplicate these projects.

Instead, it focuses on the question:

```text
What privilege escalation condition did I discover,
what must be true for it to matter,
and how should I validate and report it?
```


---

## MITRE ATT&CK

Where applicable, explorer techniques include mappings to [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }.

Common privilege escalation and execution-related areas include:

```text
T1548 - Abuse Elevation Control Mechanism
T1548.001 - Setuid and Setgid
T1548.003 - Sudo and Sudo Caching
T1068 - Exploitation for Privilege Escalation
T1574 - Hijack Execution Flow
T1543 - Create or Modify System Process
T1053 - Scheduled Task/Job
T1552 - Unsecured Credentials
```

ATT&CK mappings provide useful context, but the presence of an ATT&CK technique does not determine exploitability or severity by itself.


---

## Explorer Principles

PrivEsc Explorer follows several core principles.

### Evidence Before Exploitation

Prefer configuration and permission evidence before modifying privileged resources.

### Context Before Severity

A dangerous-looking permission is only meaningful when connected to a privileged consumer.

### Candidates Before Conclusions

Enumeration produces candidates. Validation produces findings.

### Minimal Impact

Use the least invasive technique necessary to establish the security boundary.

### Offensive and Defensive Context

Where practical, each technique includes both testing and defensive guidance.

### Structured Knowledge

Technique data is maintained separately from presentation logic so the explorer can grow without turning into an unmaintainable collection of hard-coded pages.


---

## Future Expansion

The explorer architecture can be expanded without changing the overall workflow.

Possible future areas include:

```text
Active Directory Explorer
        |
        +--> Kerberos
        +--> Delegation
        +--> ACL / ACE
        +--> AD CS
        +--> NTLM Relay
        +--> Trusts

Command Explorer
        |
        +--> Windows
        +--> Linux
        +--> PowerShell
        +--> Active Directory
        +--> Networking

Detection Explorer
        |
        +--> ATT&CK Technique
        +--> Data Source
        +--> Event ID
        +--> Sigma
        +--> Detection Logic

Web Testing Explorer
        |
        +--> Observation
        +--> Vulnerability Class
        +--> Validation
        +--> Burp Workflow
        +--> Remediation
```

The same structured-data approach can therefore support other operational areas of the knowledge base.


---

## Related Notes

### Windows

- [Windows Overview](../windows/)
- [Windows Enumeration](../windows/enumeration/)
- [Windows Privilege Escalation](../windows/privilege-escalation/)
- [Windows Services](../windows/services/)
- [Windows Credentials](../windows/credentials/)
- [PowerShell](../windows/powershell/)

### Linux

- [Linux Overview](../linux/)
- [Linux Enumeration](../linux/enumeration/)
- [Linux Privilege Escalation](../linux/privilege-escalation/)
- [Linux Services](../linux/services/)
- [Linux Credentials](../linux/credentials/)


---

## References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [LOlAD](https://lolad-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [WADComs](https://wadcoms.github.io/){ target="_blank" rel="noopener noreferrer" }
- [Command Manager](https://commandmgr.com/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Windows Documentation](https://learn.microsoft.com/windows/){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [systemd Documentation](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Privilege escalation testing can modify services, scheduled tasks, files, registry settings, processes, containers, authentication material, and operating-system security controls. Perform active validation only where explicitly authorised and use the least invasive method necessary to demonstrate the security impact.
