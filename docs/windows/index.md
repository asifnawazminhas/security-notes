---
title: Windows Security Testing
description: Structured Windows security assessment methodology covering enumeration, services, scheduled tasks, permissions, registry security, credentials, application control, Microsoft Defender, UAC and privilege escalation.
---

# Windows

Windows systems are a major part of enterprise environments and are frequently encountered during authorised penetration tests, red team assessments, security reviews and Active Directory engagements.

This section provides a structured reference for assessing Windows hosts from the perspective of an authorised security tester.

The objective is not simply to collect commands. The objective is to:

- establish the current security context;
- understand the host and its role;
- identify meaningful attack paths;
- evaluate Windows security controls;
- determine whether lower-privileged users can influence privileged resources;
- validate observations safely;
- distinguish configuration weaknesses from exploitable conditions;
- collect reproducible evidence; and
- produce defensible findings and remediation advice.

!!! warning "Authorised Security Testing"

    Use these notes only on systems you own or have explicit permission to assess. Prefer read-only enumeration and controlled validation. Avoid unnecessary changes to services, tasks, registry values, security controls or production data.

---

# Windows Assessment Model

A Windows assessment should follow a structured process rather than executing unrelated enumeration commands.

```text
Initial Access / User Context
        |
        v
Identity and Token
        |
        +---- Current user
        +---- Local / domain account
        +---- Groups
        +---- Privileges
        +---- Integrity level
        +---- UAC state
        |
        v
System Enumeration
        |
        +---- OS / build / architecture
        +---- Hostname / domain
        +---- Users / groups
        +---- Network
        +---- Processes
        +---- Installed software
        |
        v
Security Control Enumeration
        |
        +---- Microsoft Defender
        +---- ASR
        +---- Windows Firewall
        +---- AppLocker
        +---- WDAC
        +---- PowerShell Language Mode
        +---- UAC
        |
        v
Privileged Execution Paths
        |
        +---- Services
        +---- Scheduled tasks
        +---- Startup mechanisms
        +---- Administrative applications
        |
        v
Permission Analysis
        |
        +---- Files
        +---- Directories
        +---- Registry
        +---- Service objects
        +---- Task resources
        |
        v
Credential Exposure Review
        |
        +---- Configuration
        +---- Scripts
        +---- PowerShell history
        +---- Application secrets
        +---- Credential stores
        |
        v
Privilege Escalation Analysis
        |
        +---- What can I control?
        +---- Who consumes it?
        +---- Under which identity?
        +---- Can privileged behaviour be influenced?
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

# Windows Notes

<div class="grid cards" markdown>

-   :material-magnify:{ .lg .middle } **Windows Enumeration**

    ---

    Establish the host, user, token, operating system, network, users, groups, processes, software and security context.

    [:octicons-arrow-right-24: Windows Enumeration](enumeration.md)

-   :material-console:{ .lg .middle } **PowerShell**

    ---

    PowerShell enumeration, execution context, language modes, logging, security controls and assessment workflows.

    [:octicons-arrow-right-24: PowerShell](powershell.md)

-   :material-cog:{ .lg .middle } **Windows Services**

    ---

    Service accounts, executable paths, permissions, service configuration and privileged service relationships.

    [:octicons-arrow-right-24: Windows Services](services.md)

-   :material-calendar-clock:{ .lg .middle } **Scheduled Tasks**

    ---

    Task principals, actions, triggers, run levels, referenced resources and privileged task relationships.

    [:octicons-arrow-right-24: Scheduled Tasks](scheduled-tasks.md)

-   :material-folder-lock:{ .lg .middle } **Filesystem Permissions**

    ---

    NTFS ACLs, inheritance, writable files and directories, ownership and privileged filesystem relationships.

    [:octicons-arrow-right-24: Filesystem Permissions](filesystem-permissions.md)

-   :material-database-cog:{ .lg .middle } **Registry Security**

    ---

    Registry enumeration, ACL analysis, startup configuration, service settings and security-sensitive registry relationships.

    [:octicons-arrow-right-24: Registry Security](registry.md)

-   :material-key:{ .lg .middle } **Windows Credentials**

    ---

    Credential exposure, PowerShell history, application configuration, scripts, deployment artifacts and sensitive authentication material.

    [:octicons-arrow-right-24: Windows Credentials](credentials.md)

-   :material-shield-lock:{ .lg .middle } **Application Control**

    ---

    AppLocker, WDAC, effective policy, rule collections, enforcement modes and execution-control validation.

    [:octicons-arrow-right-24: Application Control](application-control.md)

-   :material-shield-check:{ .lg .middle } **Microsoft Defender**

    ---

    Defender status, protection features, exclusions, ASR, tamper protection and endpoint security posture.

    [:octicons-arrow-right-24: Microsoft Defender](defender.md)

-   :material-account-lock:{ .lg .middle } **User Account Control**

    ---

    UAC configuration, integrity levels, split tokens, Admin Approval Mode, secure desktop and elevation behavior.

    [:octicons-arrow-right-24: User Account Control](uac.md)

-   :material-arrow-up-bold-circle:{ .lg .middle } **Privilege Escalation**

    ---

    Correlate services, tasks, permissions, credentials, privileges and software into validated privilege escalation paths.

    [:octicons-arrow-right-24: Windows Privilege Escalation](privilege-escalation.md)

</div>

---

# 1. Establish the Current Security Context

Before investigating potential vulnerabilities, determine exactly who you are and which token the current process is using.

Start with:

```cmd
whoami
whoami /user
whoami /groups
whoami /priv
whoami /all
hostname
```

PowerShell:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:COMPUTERNAME
$ExecutionContext.SessionState.LanguageMode
```

Important questions include:

```text
Who is the current user?

Is the account local or domain based?

Which groups does it belong to?

Is it a local administrator?

Which privileges are assigned?

Which privileges are enabled?

What integrity level is active?

Is the current process elevated?

Is the machine domain joined?
```

Do not assume that membership in:

```text
BUILTIN\Administrators
```

means the current process is elevated.

UAC can result in an administrator operating with a filtered medium-integrity token.

See:

- [Windows Enumeration](enumeration.md)
- [User Account Control](uac.md)

---

# 2. Identify the System

Determine the Windows edition, build, architecture and system role.

```cmd
systeminfo
```

PowerShell:

```powershell
Get-ComputerInfo
```

Focused output:

```powershell
Get-ComputerInfo |
    Select-Object WindowsProductName,
                  WindowsVersion,
                  OsBuildNumber,
                  OsArchitecture
```

Architecture:

```powershell
[Environment]::Is64BitOperatingSystem
```

Computer and domain information:

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```

The operating system version provides context, but version information alone is not sufficient evidence that a vulnerability exists.

Use:

```text
Version
    +
Configuration
    +
Exposure
    +
Applicable vulnerable condition
    +
Validation
```

before reaching a security conclusion.

---

# 3. Determine Domain Membership

Domain membership changes the scope of the assessment significantly.

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```

Additional context:

```powershell
$env:USERDOMAIN
$env:LOGONSERVER
$env:COMPUTERNAME
```

If the host is domain joined, host-level Windows assessment should normally be combined with the separate [Active Directory](../active-directory/index.md) methodology.

Keep the two scopes conceptually separate:

```text
Windows Host Assessment
        |
        +---- Local configuration
        +---- Local permissions
        +---- Services
        +---- Tasks
        +---- Credentials
        +---- Endpoint controls

Active Directory Assessment
        |
        +---- Domain identities
        +---- Kerberos
        +---- NTLM
        +---- Delegation
        +---- ACLs
        +---- AD CS
        +---- Trusts
```

---

# 4. Enumerate Users, Groups and Privileges

Local users:

```powershell
Get-LocalUser
```

Local groups:

```powershell
Get-LocalGroup
```

Administrators:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

Privileges:

```cmd
whoami /priv
```

Privileges commonly worth understanding include:

```text
SeBackupPrivilege
SeRestorePrivilege
SeDebugPrivilege
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeTakeOwnershipPrivilege
SeLoadDriverPrivilege
SeManageVolumePrivilege
```

The existence of a privilege does not automatically demonstrate privilege escalation.

Determine:

```text
Privilege
    |
    v
Assigned?
    |
    v
Enabled?
    |
    v
Usable from current token?
    |
    v
Relevant target/configuration exists?
    |
    v
Security boundary can be crossed?
```

---

# 5. Enumerate the Network

Basic network information:

```cmd
ipconfig /all
route print
arp -a
netstat -ano
```

PowerShell:

```powershell
Get-NetIPConfiguration
Get-NetAdapter
Get-NetIPAddress
Get-NetRoute
Get-NetTCPConnection
```

DNS:

```powershell
Get-DnsClientCache
```

Network enumeration can reveal:

- internal networks;
- management interfaces;
- DNS infrastructure;
- domain infrastructure;
- locally listening services;
- remote connections;
- administrative interfaces; and
- potential pivoting relationships.

Correlate network listeners with their owning processes.

For example:

```powershell
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Then:

```powershell
Get-Process -Id 1234
```

The existence of a listening port alone does not demonstrate a vulnerability.

---

# 6. Processes and Software

Processes:

```cmd
tasklist
```

PowerShell:

```powershell
Get-Process
```

Installed 64-bit software:

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher
```

Installed 32-bit software on 64-bit Windows:

```powershell
Get-ItemProperty 'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher
```

Look for software that changes the security model, including:

```text
Endpoint protection
Management agents
Backup software
Remote administration tools
Development environments
Database software
Web servers
Deployment agents
Custom enterprise applications
Privileged utilities
```

Version information is a starting point for research, not a finding by itself.

---

# 7. Services

Windows services are one of the most important privileged execution mechanisms on a Windows host.

Enumerate them with:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,
                  DisplayName,
                  State,
                  StartMode,
                  StartName,
                  PathName
```

The assessment should correlate:

```text
Service
    |
    v
Service Account
    |
    v
Executable / Arguments
    |
    v
Service Object Permissions
    |
    v
Executable Permissions
    |
    v
Directory Permissions
    |
    v
Configuration Dependencies
```

A service running as:

```text
LocalSystem
```

is not a vulnerability.

The relevant question is whether a lower-privileged principal can influence something that the privileged service executes or consumes.

Continue with [Windows Services](services.md).

---

# 8. Scheduled Tasks

Scheduled tasks represent another important privileged execution path.

Basic enumeration:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Review:

```text
Task name
Principal
Run level
Triggers
Actions
Executable
Arguments
Working directory
Referenced scripts
Referenced configuration
```

Assessment logic:

```text
Task Runs Privileged
        |
        v
What Does It Execute?
        |
        v
Can Current User Modify It?
        |
        +---- Executable
        +---- Script
        +---- Directory
        +---- Configuration
        +---- Arguments / dependencies
        |
        v
Can Privileged Behaviour Be Influenced?
```

A privileged scheduled task is not inherently vulnerable.

The security issue exists when an untrusted principal can influence a resource used by that privileged task.

Continue with [Scheduled Tasks](scheduled-tasks.md).

---

# 9. Filesystem Permissions

Windows filesystem security should be assessed as a relationship rather than as a list of writable directories.

PowerShell:

```powershell
Get-Acl 'C:\Path'
```

Native Windows tooling:

```cmd
icacls "C:\Path"
```

Pay particular attention to permissions granted to principals such as:

```text
Everyone
Users
Authenticated Users
BUILTIN\Users
```

and rights such as:

```text
Write
Modify
FullControl
```

However:

```text
Writable Directory
```

does not automatically mean:

```text
Privilege Escalation
```

Use:

```text
Writable Resource
        |
        v
What Can Be Modified?
        |
        v
Who Consumes It?
        |
        v
Under Which Security Context?
        |
        v
Can Behavior Be Influenced?
        |
        v
Can the Impact Be Safely Validated?
```

Continue with [Filesystem Permissions](filesystem-permissions.md).

---

# 10. Registry Security

The Registry contains operating system and application configuration that can become security relevant when permissions and privileged consumers interact.

Useful locations include:

```text
HKLM:\SOFTWARE
HKLM:\SYSTEM
HKCU:\Software
```

PowerShell:

```powershell
Get-PSDrive -PSProvider Registry
```

Example:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE'
```

Registry analysis can reveal:

- service configuration;
- startup mechanisms;
- application settings;
- security configuration;
- executable paths;
- user-specific configuration; and
- potentially sensitive values.

A writable registry key is not automatically a vulnerability.

Determine whether changing that key can influence a privileged or security-sensitive operation.

Continue with [Registry Security](registry.md).

---

# 11. Credential Exposure

Potential credential material may exist in:

```text
Application configuration
Scripts
PowerShell history
Deployment files
Scheduled tasks
Service configuration
Backup files
Registry values
Credential stores
User profiles
```

PowerShell history location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Where authorised:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

Credential discovery should be targeted and proportionate.

Sensitive material should not be unnecessarily:

```text
Copied

Displayed

Stored in shell history

Included unredacted in screenshots

Committed to repositories

Placed in reports
```

Continue with [Windows Credentials](credentials.md).

---

# 12. PowerShell Security Context

PowerShell is an important Windows administration and assessment interface.

Version:

```powershell
$PSVersionTable
```

Language Mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible values include:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

`FullLanguage` alone is not automatically a security weakness.

Language Mode should be interpreted together with:

```text
AppLocker
WDAC
PowerShell policy
Logging
Endpoint protection
User privilege
System role
```

Continue with [PowerShell](powershell.md).

---

# 13. Microsoft Defender and ASR

Where permitted:

```powershell
Get-MpComputerStatus
```

Focused status:

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusEnabled,
                  AntispywareEnabled,
                  RealTimeProtectionEnabled,
                  BehaviorMonitorEnabled,
                  IoavProtectionEnabled,
                  IsTamperProtected
```

Preferences:

```powershell
Get-MpPreference
```

Attack Surface Reduction:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```

Assess:

```text
Antivirus state
Real-time protection
Behaviour monitoring
Cloud protection
Tamper protection
Exclusions
ASR configuration
Signature state
```

Do not disable endpoint protection simply to demonstrate that it can be disabled.

The preferred model is:

```text
Inspect
   |
   v
Understand Effective Configuration
   |
   v
Perform Approved Validation
   |
   v
Observe Detection / Prevention
   |
   v
Collect Evidence
```

Continue with [Microsoft Defender](defender.md).

---

# 14. Application Control

Application control can significantly affect which binaries, scripts, installers, DLLs and packaged applications are permitted to execute.

The main Windows technologies covered in these notes are:

```text
AppLocker

Windows Defender Application Control
Application Control for Business
```

Effective AppLocker policy:

```powershell
Get-AppLockerPolicy -Effective
```

Rule collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections
```

A file can be evaluated against effective AppLocker policy using:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\test.exe' -User "$env:USERDOMAIN\$env:USERNAME"
```

Application-control assessment should answer:

```text
Which policy exists?

Which collections are configured?

Which collections are enforced?

Which identities are affected?

Which paths / publishers / hashes are trusted?

What does the effective policy permit?

Does runtime behavior match the policy?
```

Do not assume:

```text
AppLocker Installed = Application Control Enforced
```

or:

```text
One Allowed Executable = Application Control Bypass
```

Continue with [Application Control](application-control.md).

---

# 15. User Account Control

UAC affects administrative elevation and token behavior.

Important questions include:

```text
Is UAC enabled?

Is the user already an administrator?

What integrity level is active?

Is the current token filtered?

How are administrators prompted?

How are standard users handled?

Is secure desktop enabled?
```

Core configuration:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
```

Remember the distinction:

```text
Standard User
     |
     v
Administrator
```

is not equivalent to:

```text
Administrator
Medium Integrity
     |
     v
Administrator
High Integrity
```

The second is an elevation within an already administrative identity.

Continue with [User Account Control](uac.md).

---

# 16. Windows Firewall

Review firewall profiles:

```powershell
Get-NetFirewallProfile
```

Enabled rules:

```powershell
Get-NetFirewallRule -Enabled True
```

Native command:

```cmd
netsh advfirewall show allprofiles
```

Interpret firewall rules using:

```text
Profile
Direction
Action
Protocol
Port
Remote Address
Application
Service
```

An allow rule does not automatically constitute a vulnerability.

Determine:

```text
What is exposed?

Who can reach it?

What service receives the connection?

What authentication protects it?

Is the exposure required?
```

---

# 17. Startup and Automatic Execution

Windows supports multiple automatic execution mechanisms, including:

```text
Services
Scheduled tasks
Startup folders
Registry Run keys
Logon scripts
Application-specific mechanisms
```

Common Run keys include:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run

HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

For every startup mechanism determine:

```text
What executes?

Which identity executes it?

Who can modify the configuration?

Who can modify the referenced file?

Who can modify its parent directory?

Is the behavior expected?
```

Autorun presence alone is not a vulnerability.

---

# 18. Privilege Escalation Analysis

Privilege escalation should bring together evidence from all earlier phases.

The central question is:

```text
What can the current user control?
```

Then:

```text
Controlled Resource
        |
        v
Who Consumes It?
        |
        v
Under Which Identity?
        |
        v
When Is It Consumed?
        |
        v
Can Its Behaviour Be Influenced?
        |
        v
Does This Cross a Security Boundary?
```

Common relationships include:

```text
User
  |
  +----> Service configuration
  |
  +----> Service executable
  |
  +----> Scheduled task resource
  |
  +----> Writable privileged file
  |
  +----> Writable privileged directory
  |
  +----> Registry configuration
  |
  +----> Credential material
  |
  +----> Assigned Windows privilege
  |
  +----> Vulnerable privileged software
  |
  v
Higher-Privileged Execution
```

Continue with [Windows Privilege Escalation](privilege-escalation.md).

---

# 19. Manual and Automated Enumeration

A strong assessment combines manual understanding with automated coverage.

```text
Manual Enumeration
        |
        +---- Understand context
        +---- Identify controls
        +---- Form hypotheses
        |
        v
Automated Enumeration
        |
        +---- Increase coverage
        +---- Identify candidates
        +---- Highlight unusual configuration
        |
        v
Manual Validation
        |
        +---- Confirm permissions
        +---- Confirm identity
        +---- Confirm execution context
        +---- Confirm relationships
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

Automated tool output should be treated as:

```text
Candidate Evidence
```

rather than:

```text
Confirmed Finding
```

until manually validated.

---

# 20. Useful Windows Assessment Tools

## Microsoft Sysinternals

Useful Sysinternals tools include:

| Tool | Typical Use |
|---|---|
| Autoruns | Automatic execution and persistence review |
| Process Explorer | Process, token and integrity inspection |
| Process Monitor | Runtime filesystem, Registry and process activity |
| AccessChk | Windows object permission analysis |
| TCPView | Network connection inspection |
| Sigcheck | File signature and metadata inspection |
| Strings | Printable string extraction |
| PsExec | Approved remote/local administration scenarios |

[Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }

## Seatbelt

Seatbelt can assist with broad Windows host enumeration and security-context discovery.

[GhostPack Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

## SharpUp

SharpUp focuses on potential Windows privilege escalation conditions.

[GhostPack SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }

## PrivescCheck

PrivescCheck provides PowerShell-based Windows privilege escalation enumeration.

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

## WinPEAS

WinPEAS provides broad Windows privilege escalation enumeration.

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

!!! tip "Automation supports analysis"

    Automated tools are useful for coverage and prioritisation, but their output should be manually validated before being treated as assessment evidence.

---

# 21. Practical Validation Model

For potentially significant observations, use the same validation model throughout the Windows section.

```text
Observation
     |
     v
Applicability
     |
     v
Security Context
     |
     v
Permissions / Configuration
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

## Example

Suppose enumeration identifies:

```text
C:\ProgramData\Vendor\App\
```

as writable by a standard user.

Do not stop at:

```text
Directory is writable.
```

Determine:

```text
What files are stored there?

Which files can actually be modified?

Does a privileged service or task use them?

Under which account does that process execute?

Are permissions inherited?

Can the user replace or modify the relevant resource?

Will the privileged process actually consume the changed resource?
```

Only after establishing the relationship should the observation be classified.

---

# 22. False Positives and Alternative Explanations

Windows enumeration frequently produces observations that look more significant than they are.

Examples include:

```text
Writable directory with no privileged consumer

Privileged service with protected executable

Scheduled task running as SYSTEM with protected resources

Administrator account running at medium integrity

FullLanguage PowerShell without a requirement for CLM

AppLocker installed but not intended as the primary control

Allowed executable covered by a deliberate policy rule

Old software version where vulnerable functionality is absent

Interesting privilege that cannot affect a relevant resource
```

Before reporting, ask:

```text
Does the condition actually apply?

Can the current user reach it?

Can the relevant resource be influenced?

Does a higher-privileged component consume it?

Does another security control prevent the behavior?

Is the configuration intentional?

Can the impact be reproduced safely?
```

---

# 23. Evidence Collection

For each potentially significant Windows finding, capture:

```text
Hostname
Windows version
Current user
User SID
Group membership
Integrity level
Relevant privileges
Affected object
Object owner
Relevant ACL
Privileged consumer
Consumer identity
Security-control state
Command used
Observed result
Validation result
```

Evidence should show the complete relationship.

For example:

```text
Current User
    |
    v
Modify Permission
    |
    v
C:\ProgramData\Vendor\Service\
    |
    v
Service.exe
    |
    v
Windows Service
    |
    v
LocalSystem
```

That is considerably stronger than a screenshot showing only:

```text
BUILTIN\Users:(M)
```

---

# 24. Reporting

A Windows finding should explain why a configuration matters.

Avoid:

> `C:\Example` is writable.

Prefer:

> A standard user has Modify permission on `C:\Example`, which contains an executable used by a Windows service running as LocalSystem. This creates a privileged resource trust issue because a lower-privileged user can modify content consumed by a higher-privileged process.

A defensible finding generally contains:

```text
Observation
        |
        v
Affected Resource
        |
        v
Affected Principal
        |
        v
Privileged Consumer
        |
        v
Attack Preconditions
        |
        v
Validated Impact
        |
        v
Remediation
        |
        v
Retest
```

---

# 25. Remediation Principles

Common Windows hardening principles include:

- apply least privilege;
- restrict local administrator membership;
- protect privileged service resources;
- protect scheduled-task resources;
- harden NTFS ACLs;
- harden Registry ACLs;
- protect credential material;
- remove unnecessary software;
- maintain supported and patched software;
- restrict unnecessary services;
- configure host firewall rules;
- maintain endpoint protection;
- deploy application control where appropriate;
- configure appropriate PowerShell security controls;
- monitor privileged execution;
- protect administrative interfaces; and
- centralise security telemetry.

Remediation should address the root cause rather than only the proof-of-concept path.

---

# 26. Retesting

Retesting should demonstrate that the original security relationship no longer exists.

Example:

```text
Original Condition

Standard User
     |
     v
Modify Permission
     |
     v
Privileged Service Executable
```

After remediation:

```text
Standard User
     |
     v
No Modification Permission
     X
Privileged Service Executable
```

Retest:

```text
Original ACL

New ACL

Current effective user rights

Service configuration

Service identity

Referenced executable

Runtime functionality
```

Also confirm that remediation did not break legitimate application or administrative functionality.

---

# Windows Assessment Checklist

## Context

- [ ] Identify current user
- [ ] Record SID
- [ ] Review groups
- [ ] Review privileges
- [ ] Determine integrity level
- [ ] Determine elevation state
- [ ] Determine domain membership
- [ ] Review UAC context

## System

- [ ] Identify Windows version
- [ ] Identify architecture
- [ ] Identify build
- [ ] Review patch context
- [ ] Enumerate installed software

## Network

- [ ] Enumerate interfaces
- [ ] Enumerate addresses
- [ ] Enumerate routes
- [ ] Review DNS configuration
- [ ] Enumerate listeners
- [ ] Review active connections
- [ ] Review firewall profiles and relevant rules

## Users and Groups

- [ ] Enumerate local users
- [ ] Enumerate local groups
- [ ] Review local Administrators
- [ ] Identify service accounts
- [ ] Identify unexpected privileged identities

## Processes and Services

- [ ] Enumerate processes
- [ ] Correlate listeners with processes
- [ ] Identify security products
- [ ] Enumerate services
- [ ] Review service identities
- [ ] Review executable paths
- [ ] Review service permissions
- [ ] Review associated filesystem permissions

## Scheduled Tasks

- [ ] Enumerate tasks
- [ ] Review principals
- [ ] Review run levels
- [ ] Review triggers
- [ ] Review actions
- [ ] Review referenced files
- [ ] Review referenced directories
- [ ] Determine whether lower-privileged users can influence resources

## Filesystem

- [ ] Review security-sensitive directories
- [ ] Review privileged executable ACLs
- [ ] Review parent-directory ACLs
- [ ] Review configuration-file ACLs
- [ ] Review ownership
- [ ] Validate effective permissions

## Registry

- [ ] Review security-sensitive configuration
- [ ] Review service configuration
- [ ] Review startup configuration
- [ ] Review relevant Registry ACLs
- [ ] Identify privileged consumers

## Credentials

- [ ] Review relevant configuration files
- [ ] Review scripts
- [ ] Review PowerShell history where authorised
- [ ] Review deployment artifacts
- [ ] Review application configuration
- [ ] Protect collected secrets and evidence

## Security Controls

- [ ] Review Microsoft Defender
- [ ] Review Defender exclusions
- [ ] Review ASR
- [ ] Review Windows Firewall
- [ ] Review AppLocker
- [ ] Review WDAC/Application Control
- [ ] Review PowerShell Language Mode
- [ ] Review UAC
- [ ] Consider AMSI and logging context

## Privilege Escalation

- [ ] Identify controllable resources
- [ ] Identify privileged consumers
- [ ] Establish execution context
- [ ] Validate permissions
- [ ] Identify alternative explanations
- [ ] Safely validate meaningful relationships
- [ ] Determine the actual security boundary crossed

## Reporting

- [ ] Capture reproducible commands
- [ ] Record relevant output
- [ ] Record affected identity
- [ ] Record privileged identity
- [ ] Record permissions
- [ ] Explain preconditions
- [ ] Explain impact
- [ ] Provide root-cause remediation
- [ ] Define retest procedure

---

# Recommended Reading Order

For a complete host-level assessment, use the Windows notes in approximately this order:

```text
1. Windows Overview
        |
        v
2. Enumeration
        |
        v
3. PowerShell
        |
        +------------------+
        |                  |
        v                  v
4. Services       5. Scheduled Tasks
        |                  |
        +--------+---------+
                 |
                 v
6. Filesystem Permissions
                 |
                 v
7. Registry Security
                 |
                 v
8. Credentials
                 |
                 v
9. Application Control
                 |
                 v
10. Microsoft Defender
                 |
                 v
11. UAC
                 |
                 v
12. Privilege Escalation
                 |
                 v
Validation / Evidence / Reporting
```

Direct links:

1. [Windows Enumeration](enumeration.md)
2. [PowerShell](powershell.md)
3. [Windows Services](services.md)
4. [Scheduled Tasks](scheduled-tasks.md)
5. [Filesystem Permissions](filesystem-permissions.md)
6. [Registry Security](registry.md)
7. [Windows Credentials](credentials.md)
8. [Application Control](application-control.md)
9. [Microsoft Defender](defender.md)
10. [User Account Control](uac.md)
11. [Windows Privilege Escalation](privilege-escalation.md)

For domain-joined systems, also use:

- [Active Directory](../active-directory/index.md)
- [Active Directory Enumeration](../active-directory/enumeration.md)

---

# Related Notes

- [Active Directory](../active-directory/index.md)
- [Windows PrivEsc Explorer](../privesc/windows.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)

---

# Windows Security Testing Mindset

The most important principle in this section is correlation.

Do not think:

```text
Writable = Vulnerable

SYSTEM = Vulnerable

Old Version = Vulnerable

FullLanguage = Vulnerable

Allowed = Vulnerable

Administrator = Vulnerable
```

Instead think:

```text
Observation
      |
      v
What Does It Mean?
      |
      v
Who Can Influence It?
      |
      v
Who Consumes It?
      |
      v
Under Which Security Context?
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

This produces better testing and substantially stronger reporting.

---

# References

- [Microsoft Windows documentation](https://learn.microsoft.com/en-us/windows/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Windows security documentation](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Defender for Endpoint documentation](https://learn.microsoft.com/en-us/defender-endpoint/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - User Account Control](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Application Control for Business](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [GhostPack Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }
- [GhostPack SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }
- [PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

!!! tip "Correlate before reporting"

    The strongest Windows findings demonstrate a complete relationship between a lower-privileged principal, a controllable resource, a higher-privileged consumer and a realistic security impact.

!!! tip "Use dedicated pages for depth"

    This page is the Windows assessment map. Use the dedicated pages for detailed enumeration, validation, interpretation, remediation and retesting procedures.

!!! warning "Validate automated findings"

    Seatbelt, SharpUp, PrivescCheck, WinPEAS and similar tools identify candidate conditions. Their output should not be treated as a confirmed vulnerability until the relevant permissions, execution context and security impact have been manually verified.
