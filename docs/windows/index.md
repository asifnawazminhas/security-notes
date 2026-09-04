# Windows

Windows systems are a major part of enterprise environments and are frequently encountered during authorised penetration tests, red team assessments, security reviews, and Active Directory engagements.

This section provides a structured reference for assessing Windows hosts from the perspective of an authorised security tester.

The objective is not simply to collect commands. The objective is to understand the system, identify meaningful attack paths, evaluate security controls, validate observations, and document evidence in a repeatable way.

---

## Scope

The Windows section focuses primarily on host-level assessment.

It covers:

- Windows system enumeration
- Local users and groups
- Network configuration
- Processes and services
- Installed software
- File and directory permissions
- Registry configuration
- Scheduled tasks
- Windows privileges
- PowerShell
- Credential exposure
- Local privilege escalation
- Windows security controls
- Application control
- Logging and defensive controls

Active Directory-specific techniques are documented separately in the [Active Directory](../active-directory/index.md) section.

---

# Windows Assessment Flow

A Windows assessment should follow a structured process.

```text
Initial Access / User Context
        |
        v
Identify Current Context
        |
        v
System Enumeration
        |
        +---- OS / architecture
        +---- hostname / domain
        +---- users / groups
        +---- privileges
        +---- network configuration
        |
        v
Security Control Enumeration
        |
        +---- Microsoft Defender
        +---- AppLocker
        +---- WDAC
        +---- PowerShell Language Mode
        +---- AMSI
        +---- ASR rules
        +---- Windows Firewall
        |
        v
Process / Service Enumeration
        |
        +---- running processes
        +---- services
        +---- service accounts
        +---- permissions
        |
        v
Application / Software Enumeration
        |
        +---- installed software
        +---- versions
        +---- development tools
        +---- management agents
        |
        v
Filesystem / Registry Review
        |
        +---- writable directories
        +---- configuration files
        +---- registry permissions
        +---- sensitive files
        |
        v
Credential Exposure Review
        |
        +---- configuration files
        +---- PowerShell history
        +---- Credential Manager
        +---- registry
        +---- application secrets
        |
        v
Privilege Escalation Analysis
        |
        +---- services
        +---- scheduled tasks
        +---- permissions
        +---- privileges
        +---- software
        +---- credential material
        |
        v
Validate Findings
        |
        v
Collect Evidence
        |
        v
Report and Remediate
```

---

# 1. Establish the Current Context

Before testing anything, determine the security context in which commands are executing.

Questions to answer include:

- Which user am I?
- Is the account local or domain-based?
- Which groups does the user belong to?
- Is the process elevated?
- Which Windows privileges are assigned?
- Is the host domain joined?
- What integrity level is being used?

Basic commands:

```cmd
whoami
whoami /user
whoami /groups
whoami /priv
hostname
```

PowerShell:

```powershell
whoami
$env:USERNAME
$env:USERDOMAIN
$env:COMPUTERNAME
```

Check group membership:

```powershell
whoami /groups
```

Look for membership in groups such as:

```text
BUILTIN\Administrators
```

Do not assume that membership automatically means the current process is elevated. User Account Control can result in different access tokens being used.

---

# 2. Identify the Operating System

Determine the Windows version, architecture, build number, and patch level.

```cmd
systeminfo
```

PowerShell:

```powershell
Get-ComputerInfo
```

Useful properties:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
```

Alternative:

```cmd
ver
```

Architecture:

```cmd
echo %PROCESSOR_ARCHITECTURE%
```

PowerShell:

```powershell
[Environment]::Is64BitOperatingSystem
```

The operating system version matters because security features, configuration options, and potential weaknesses vary between Windows releases and builds.

Do not report a vulnerability solely from an operating system or software version. Confirm that the relevant condition actually applies.

---

# 3. Determine Domain Membership

Determine whether the system is standalone, workgroup joined, or joined to Active Directory.

```cmd
systeminfo | findstr /B /C:"Domain"
```

PowerShell:

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Name, Domain, PartOfDomain
```

Environment variables can provide additional context:

```powershell
$env:USERDOMAIN
$env:LOGONSERVER
```

Current computer:

```powershell
$env:COMPUTERNAME
```

If the machine is domain joined, continue domain-specific investigation using the [Active Directory](../active-directory/index.md) section.

---

# 4. Enumerate Users

Local users:

```cmd
net user
```

PowerShell:

```powershell
Get-LocalUser
```

Inspect a particular account:

```powershell
Get-LocalUser -Name "username"
```

Useful properties include:

```text
Enabled
LastLogon
PasswordExpires
PasswordRequired
UserMayChangePassword
```

Current user:

```cmd
whoami
```

Detailed identity information:

```cmd
whoami /all
```

Testing should focus on identifying accounts that materially affect the security posture rather than simply producing a list of usernames.

---

# 5. Enumerate Local Groups

List local groups:

```cmd
net localgroup
```

Administrators:

```cmd
net localgroup Administrators
```

PowerShell:

```powershell
Get-LocalGroup
```

Members of the local Administrators group:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

Pay attention to:

- Local administrator accounts
- Domain groups
- Service accounts
- Support accounts
- Deployment accounts
- Unexpected users
- Nested administrative membership

Group membership should always be interpreted together with the current access token and integrity level.

---

# 6. Enumerate Windows Privileges

Windows privileges can significantly affect the security impact of an account.

```cmd
whoami /priv
```

Examples worth reviewing include:

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

The presence of a privilege does not automatically prove that privilege escalation is possible.

Record:

```text
Privilege
State
Current integrity level
Execution context
Relevant system configuration
```

The practical impact should be validated separately.

---

# 7. Network Enumeration

Display network configuration:

```cmd
ipconfig /all
```

PowerShell:

```powershell
Get-NetIPConfiguration
```

Interfaces:

```powershell
Get-NetAdapter
```

IP addresses:

```powershell
Get-NetIPAddress
```

Routes:

```cmd
route print
```

PowerShell:

```powershell
Get-NetRoute
```

ARP cache:

```cmd
arp -a
```

DNS cache:

```cmd
ipconfig /displaydns
```

PowerShell:

```powershell
Get-DnsClientCache
```

Listening ports and network connections:

```cmd
netstat -ano
```

PowerShell:

```powershell
Get-NetTCPConnection
```

Map a PID to a process:

```powershell
Get-Process -Id 1234
```

Network enumeration can reveal:

- Internal networks
- Management networks
- Listening services
- Locally bound services
- Remote connections
- DNS infrastructure
- Domain infrastructure
- Proxy configuration
- Potential pivoting opportunities

Network findings should be correlated with processes and services.

---

# 8. Process Enumeration

List running processes:

```cmd
tasklist
```

PowerShell:

```powershell
Get-Process
```

Detailed process information can help identify:

- Security software
- Management agents
- Backup software
- Monitoring agents
- Database software
- Web servers
- Development tools
- Administrative utilities
- User applications

Process enumeration should be correlated with:

```text
Services
Installed applications
Network listeners
Filesystem permissions
Execution context
Security products
```

A process name alone should not be treated as evidence of a vulnerability.

---

# 9. Service Enumeration

Services are one of the most important Windows assessment areas.

Basic enumeration:

```cmd
sc query
```

PowerShell:

```powershell
Get-Service
```

Detailed service information:

```powershell
Get-CimInstance Win32_Service | Select-Object Name, DisplayName, State, StartMode, StartName, PathName
```

Important properties include:

```text
Name
Display name
State
Start mode
Service account
Executable path
Arguments
Permissions
```

Potentially important relationships include:

```text
Low-privileged user
        |
        v
Writable service resource
        |
        v
Privileged service
        |
        v
Potential privilege boundary
```

A service running as `LocalSystem` is not itself a vulnerability.

The security question is whether a lower-privileged user can influence the service configuration, executable, DLLs, configuration files, or another resource consumed by that service.

Continue with [Windows Services](services.md).

---

# 10. Installed Software

Enumerate installed applications using the registry.

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Select-Object DisplayName, DisplayVersion, Publisher
```

Check 32-bit applications on 64-bit systems:

```powershell
Get-ItemProperty HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Select-Object DisplayName, DisplayVersion, Publisher
```

Review software for:

- Unsupported versions
- Privileged applications
- Management agents
- Backup clients
- Development environments
- Database clients
- Remote management software
- Security products
- Deployment software
- Custom enterprise applications

Do not conclude that software is vulnerable based only on a version string.

Confirm applicability before reporting a vulnerability.

---

# 11. Scheduled Tasks

List scheduled tasks:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Useful properties include:

```text
Task name
Principal
Trigger
Action
Executable
Arguments
Run level
```

When assessing scheduled tasks, review both configuration and filesystem permissions.

A task running with elevated privileges is not itself a vulnerability.

The security issue arises when an untrusted user can influence something the privileged task executes or consumes.

Assessment logic:

```text
Scheduled Task
      |
      v
Execution Context
      |
      v
Action / Executable
      |
      v
File Permissions
      |
      v
Directory Permissions
      |
      v
Can Lower-Privileged User Influence It?
```

---

# 12. Filesystem Permissions

Windows filesystem permissions are critical during privilege escalation analysis.

Inspect permissions:

```powershell
Get-Acl "C:\Path"
```

Example:

```powershell
Get-Acl "C:\ProgramData" | Format-List
```

Using `icacls`:

```cmd
icacls C:\Path
```

Look for inappropriate permissions granted to groups such as:

```text
Everyone
Users
Authenticated Users
BUILTIN\Users
```

Permissions of interest include:

```text
Write
Modify
FullControl
```

However, a writable directory alone is not necessarily a vulnerability.

The important question is:

> Can a lower-privileged user modify content that will later be consumed or executed by a more privileged security context?

This distinction is important when reporting findings.

---

# 13. Writable Locations

A writable location can become security relevant when privileged software relies on files stored there.

Example permission inspection:

```powershell
Get-Acl "C:\ProgramData\Example"
```

Using `icacls`:

```cmd
icacls "C:\ProgramData\Example"
```

Assessment logic:

```text
Can the user write?
        |
        v
What can be modified?
        |
        v
Does another process consume it?
        |
        v
Which account runs that process?
        |
        v
Can execution or configuration be influenced?
        |
        v
Validate practical security impact
```

This prevents reporting writable folders without demonstrating why they matter.

---

# 14. Registry Enumeration

The Windows Registry contains extensive system and application configuration.

PowerShell provides registry drives:

```powershell
Get-PSDrive -PSProvider Registry
```

Common locations include:

```text
HKLM:\SOFTWARE
HKLM:\SYSTEM
HKCU:\Software
```

Registry analysis can reveal:

- Application configuration
- Service configuration
- Startup entries
- Security settings
- Stored paths
- User-specific configuration
- Potential credential material

Example:

```powershell
Get-ChildItem HKLM:\SOFTWARE
```

Registry findings should always be evaluated in context.

A writable registry key only becomes security relevant when it can influence a security-sensitive or privileged operation.

---

# 15. PowerShell

PowerShell is both an administrative platform and an important Windows security assessment interface.

Determine the PowerShell version:

```powershell
$PSVersionTable
```

Check Language Mode:

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

Language Mode should be considered together with the broader application-control architecture.

`FullLanguage` by itself is not automatically a vulnerability.

PowerShell can also be used for:

- System enumeration
- Registry inspection
- File permission analysis
- Network enumeration
- Service inspection
- Event log inspection
- Security-control assessment
- Evidence collection

Continue with [PowerShell](powershell.md).

---

# 16. Microsoft Defender

Where permitted, inspect Microsoft Defender configuration.

```powershell
Get-MpComputerStatus
```

Selected information:

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled, AntispywareEnabled, RealTimeProtectionEnabled, BehaviorMonitorEnabled, IoavProtectionEnabled
```

Preferences:

```powershell
Get-MpPreference
```

Potential assessment areas include:

```text
Antivirus status
Real-time protection
Behaviour monitoring
Signature state
Exclusions
Cloud protection
Attack Surface Reduction
Tamper protection
```

During an assessment, security controls should primarily be documented and evaluated rather than disabled.

---

# 17. Attack Surface Reduction

Microsoft Defender Attack Surface Reduction rules can restrict commonly abused behaviours.

Where available:

```powershell
Get-MpPreference | Select-Object AttackSurfaceReductionRules_Ids, AttackSurfaceReductionRules_Actions
```

When analysing ASR configuration, determine whether relevant rules are:

```text
Disabled
Block
Audit
Warn
```

The exact representation can vary depending on Windows version and management configuration.

ASR configuration should be assessed together with:

```text
Microsoft Defender
Application control
PowerShell restrictions
Office security controls
Endpoint management
```

---

# 18. Windows Firewall

Basic status:

```cmd
netsh advfirewall show allprofiles
```

PowerShell:

```powershell
Get-NetFirewallProfile
```

Review enabled rules:

```powershell
Get-NetFirewallRule -Enabled True
```

Firewall analysis should consider:

```text
Profile
Direction
Action
Protocol
Local port
Remote address
Application
Service
```

The existence of an allow rule does not automatically represent a weakness.

Consider:

```text
Who can reach the service?
What service is listening?
Which account runs it?
Is authentication required?
Is the exposure necessary?
```

---

# 19. AppLocker

AppLocker can restrict executable, script, installer, packaged application, and DLL execution depending on policy configuration.

Inspect the effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

Rule collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections
```

Test a specific file against the effective policy:

```powershell
Get-AppLockerPolicy -Effective | Test-AppLockerPolicy -Path "C:\Path\test.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

Possible policy decisions can include:

```text
Allowed
Denied
DeniedByDefault
```

The effective policy matters more than simply determining that AppLocker components exist.

Review the relationship between:

```text
Rule collection
        |
        v
Enforcement mode
        |
        v
Path / publisher / hash rules
        |
        v
User or group scope
        |
        v
Effective execution decision
```

---

# 20. Windows Defender Application Control

Windows Defender Application Control, or WDAC, provides application-control capabilities based on Windows Code Integrity.

Assessment should determine:

```text
Is application control deployed?
Which policies are active?
Which files are trusted?
Which users or contexts are affected?
Is audit or enforcement mode being used?
```

Application-control assessment should focus on the effective security boundary rather than testing isolated executables without context.

WDAC and AppLocker are related areas of Windows application control, but they should not automatically be treated as equivalent controls.

---

# 21. AMSI

The Antimalware Scan Interface, commonly referred to as AMSI, provides an interface through which applications and services can integrate with antimalware products.

During an assessment, AMSI should be considered as part of the broader Windows security-control architecture.

Relevant context includes:

```text
PowerShell
Script execution
Microsoft Defender
Third-party endpoint protection
Application control
Logging
Execution policy
Language Mode
```

The presence of AMSI does not guarantee that every script or execution path will be blocked.

Likewise, the ability to execute PowerShell does not demonstrate that AMSI is ineffective.

Security controls should be evaluated based on observed behaviour and effective policy.

---

# 22. Credential Exposure

Potential credential material may exist in:

```text
Configuration files
Application settings
PowerShell history
Scripts
Scheduled tasks
Service configuration
Deployment files
Backup files
Registry entries
Credential Manager
User profiles
```

Credential searches should be targeted and authorised.

Sensitive material discovered during an assessment should be handled carefully and should not be unnecessarily copied into reports, screenshots, shell history, or shared storage.

Continue with [Windows Credentials](credentials.md).

---

# 23. PowerShell History

PowerShell command history can sometimes expose operational information or sensitive values.

Common PSReadLine history location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Display the history file where accessible:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

Potentially interesting content includes:

```text
Administrative commands
Network locations
Application configuration
Authentication commands
Deployment operations
Hard-coded secrets
```

Treat any discovered credentials, tokens, or secrets as sensitive assessment evidence.

---

# 24. Environment Variables

List environment variables:

```cmd
set
```

PowerShell:

```powershell
Get-ChildItem Env:
```

Interesting variables can include:

```text
USERNAME
USERDOMAIN
COMPUTERNAME
USERPROFILE
APPDATA
LOCALAPPDATA
TEMP
TMP
PATH
PSModulePath
```

Application-specific environment variables can also expose useful configuration.

Do not assume that an interesting value is sensitive simply because it appears in an environment variable. Determine what the value represents and whether it provides meaningful access.

---

# 25. PATH Analysis

Inspect the executable search path:

```powershell
$env:PATH -split ";"
```

Check permissions on relevant directories rather than assuming a PATH entry is dangerous.

The important relationship is:

```text
Search order
        +
Writable directory
        +
Privileged execution
        =
Potential security impact
```

All conditions must be investigated.

---

# 26. Interesting Directories

Common locations worth understanding include:

```text
C:\Users
C:\ProgramData
C:\Program Files
C:\Program Files (x86)
C:\Windows
C:\Windows\Temp
C:\Temp
```

User-specific locations include:

```text
%USERPROFILE%
%APPDATA%
%LOCALAPPDATA%
%TEMP%
```

These locations can contain:

- Application configuration
- User configuration
- Logs
- Temporary files
- Scripts
- Deployment artifacts
- Service resources
- Cached information

Do not recursively search an entire filesystem without considering scope, performance, privacy, and operational impact.

---

# 27. Startup and Persistence Locations

Windows contains several mechanisms that can cause software to execute automatically.

Assessment areas can include:

```text
Services
Scheduled tasks
Startup folders
Registry Run keys
Logon scripts
Application-specific startup mechanisms
```

Examples of common Run key locations include:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

These locations are not inherently vulnerable.

The important questions are:

```text
What executes?
Who configured it?
Which account executes it?
Who can modify the referenced resource?
Is the behaviour expected?
```

---

# 28. Security Tooling

Several tools can assist with authorised Windows security assessment.

## Sysinternals

Microsoft Sysinternals contains utilities for Windows troubleshooting, administration, and security analysis.

Useful tools include:

```text
Autoruns
Process Explorer
Process Monitor
AccessChk
TCPView
Sigcheck
Strings
PsExec
```

[Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }

---

## Seatbelt

Seatbelt performs Windows host security enumeration.

Typical areas include:

```text
System information
Security products
Processes
Services
Users
Interesting files
Windows configuration
```

[Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

Use automated enumeration as a supplement to manual validation rather than treating every result as a finding.

---

## SharpUp

SharpUp assists with identifying potential Windows privilege escalation conditions.

[SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }

Findings should still be manually verified.

---

## PrivescCheck

PrivescCheck is a PowerShell-based Windows privilege escalation enumeration project.

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

---

## WinPEAS

WinPEAS provides extensive Windows privilege escalation enumeration.

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Large automated enumeration tools can generate substantial output.

Use targeted execution where possible and manually validate significant findings.

---

# 29. Manual and Automated Enumeration

A strong assessment combines both approaches.

```text
Manual Enumeration
        |
        +---- Understand environment
        +---- Establish security context
        +---- Form hypotheses
        |
        v
Automated Enumeration
        |
        +---- Increase coverage
        +---- Identify overlooked configuration
        +---- Prioritise candidates
        |
        v
Manual Validation
        |
        +---- Confirm permissions
        +---- Confirm execution context
        +---- Confirm relationships
        +---- Confirm practical impact
        |
        v
Evidence
        |
        v
Reporting
```

Automated tool output should not be copied directly into a penetration test report without validation.

---

# 30. Privilege Escalation Mindset

Privilege escalation should be treated as relationship analysis.

For example:

```text
Low-privileged user
        |
        v
Writable resource
        |
        v
Privileged process uses resource
        |
        v
User can influence behaviour
        |
        v
Privilege boundary crossed
```

The existence of only one component does not necessarily create a vulnerability.

A better assessment asks:

```text
What can I control?
        |
        v
Who consumes it?
        |
        v
Under which security context?
        |
        v
Can my control influence privileged behaviour?
        |
        v
Can the condition be safely validated?
```

Continue with [Windows Privilege Escalation](privilege-escalation.md).

---

# 31. Evidence Collection

For each potentially significant finding, record:

```text
Host
User
Integrity level
Relevant groups
Relevant privileges
Object or resource
Permissions
Security control state
Command used
Observed result
Security impact
```

Prefer reproducible evidence.

Example:

```text
Observation:
A standard user has Modify permission on a directory.

Context:
The directory contains an executable used by a privileged Windows service.

Validation:
The service account and executable path were independently confirmed.

Impact:
The writable resource may allow the lower-privileged user to influence
execution performed by a higher-privileged service.

Recommendation:
Restrict write permissions and ensure privileged service resources can only
be modified by trusted administrative principals.
```

---

# 32. Reporting

A useful Windows finding should explain the relationship between configuration and security impact.

Avoid reporting only:

```text
C:\Example is writable.
```

Prefer:

```text
A standard user has Modify permission on C:\Example. The directory contains
a binary executed by a service running under a privileged account. This
creates a trust-boundary issue because an unprivileged user can influence a
resource consumed by a higher-privileged process.
```

The second statement explains why the configuration matters.

A good finding generally contains:

```text
Observation
        |
        v
Affected Resource
        |
        v
Security Context
        |
        v
Attack Preconditions
        |
        v
Validated Impact
        |
        v
Recommendation
```

---

# 33. Remediation Principles

Common Windows hardening principles include:

- Apply least privilege.
- Restrict administrative membership.
- Protect privileged service resources.
- Harden filesystem ACLs.
- Harden registry ACLs.
- Protect credential material.
- Remove unnecessary software.
- Patch supported software.
- Restrict unnecessary services.
- Configure host firewall rules.
- Deploy endpoint protection.
- Apply application control where appropriate.
- Enable appropriate PowerShell logging.
- Monitor privileged execution.
- Review scheduled tasks.
- Protect administrative interfaces.
- Centralise security telemetry.

Remediation should be proportional to the demonstrated risk.

---

# 34. Windows Testing Checklist

## Context

- [ ] Identify current user
- [ ] Identify user SID
- [ ] Identify groups
- [ ] Identify privileges
- [ ] Determine integrity level
- [ ] Determine domain membership

## System

- [ ] Identify Windows version
- [ ] Identify architecture
- [ ] Identify build
- [ ] Review patch state
- [ ] Identify installed software

## Network

- [ ] Enumerate interfaces
- [ ] Enumerate IP addresses
- [ ] Enumerate routes
- [ ] Review DNS configuration
- [ ] Review ARP cache where relevant
- [ ] Enumerate listeners
- [ ] Review active connections
- [ ] Review firewall configuration

## Users and Groups

- [ ] Enumerate local users
- [ ] Enumerate local groups
- [ ] Review Administrators membership
- [ ] Identify service accounts
- [ ] Identify unexpected privileged accounts

## Processes

- [ ] Enumerate processes
- [ ] Identify privileged processes
- [ ] Identify security products
- [ ] Identify management software
- [ ] Correlate processes with network listeners

## Services

- [ ] Enumerate services
- [ ] Review service accounts
- [ ] Review executable paths
- [ ] Review service permissions
- [ ] Review associated filesystem permissions
- [ ] Identify privileged service relationships

## Filesystem

- [ ] Identify interesting directories
- [ ] Review writable locations
- [ ] Review sensitive files
- [ ] Review application configuration
- [ ] Validate ACL findings

## Registry

- [ ] Review relevant application keys
- [ ] Review startup configuration
- [ ] Review service configuration
- [ ] Review permissions where relevant
- [ ] Identify sensitive configuration

## Scheduled Tasks

- [ ] Enumerate scheduled tasks
- [ ] Review principals
- [ ] Review actions
- [ ] Review referenced files
- [ ] Review permissions
- [ ] Determine execution context

## Credentials

- [ ] Review configuration files
- [ ] Review PowerShell history
- [ ] Review Credential Manager where authorised
- [ ] Review application configuration
- [ ] Review scripts
- [ ] Review deployment artifacts
- [ ] Protect collected evidence

## Security Controls

- [ ] Review Microsoft Defender
- [ ] Review ASR configuration
- [ ] Review Windows Firewall
- [ ] Review AppLocker
- [ ] Review WDAC where deployed
- [ ] Review PowerShell Language Mode
- [ ] Consider AMSI context
- [ ] Review relevant logging controls

## Validation

- [ ] Manually verify automated findings
- [ ] Determine affected security boundary
- [ ] Confirm practical impact
- [ ] Collect reproducible evidence
- [ ] Avoid unnecessary system modification
- [ ] Document remediation

---

# 35. Windows Documentation Flow

Use the Windows pages in approximately this order during an assessment:

```text
Windows Overview
        |
        v
Windows Enumeration
        |
        +-----------------------+
        |                       |
        v                       v
   PowerShell                Services
        |                       |
        +-----------+-----------+
                    |
                    v
               Credentials
                    |
                    v
          Privilege Escalation
                    |
                    v
             Validate Findings
                    |
                    v
                Reporting
```

The pages are intentionally connected.

**Enumeration** establishes what exists and the current security context.

**PowerShell** provides an important administrative and assessment interface.

**Services** focuses on privileged service relationships, permissions, executable paths, and service accounts.

**Credentials** focuses on sensitive authentication material and secret exposure.

**Privilege Escalation** brings evidence from the other areas together to determine whether a security boundary can actually be crossed.

---

# Recommended Reading Order

1. [Windows Enumeration](enumeration.md)
2. [PowerShell](powershell.md)
3. [Windows Services](services.md)
4. [Windows Credentials](credentials.md)
5. [Windows Privilege Escalation](privilege-escalation.md)

For domain-joined systems, also use:

- [Active Directory](../active-directory/index.md)
- [Active Directory Enumeration](../active-directory/enumeration.md)

---

# Related Notes

- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [PowerShell](powershell.md)
- [Windows Services](services.md)
- [Windows Credentials](credentials.md)
- [Active Directory](../active-directory/index.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [Microsoft Windows documentation](https://learn.microsoft.com/en-us/windows/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Windows security documentation](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Defender for Endpoint documentation](https://learn.microsoft.com/en-us/defender-endpoint/){ target="_blank" rel="noopener noreferrer" }
- [AppLocker documentation](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Windows application control documentation](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }
- [SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }
- [PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

---

> Use these notes only on systems you own or have explicit permission to assess.
