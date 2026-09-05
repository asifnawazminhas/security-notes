---
title: Windows PrivEsc Explorer
description: Interactive Windows privilege escalation technique explorer for authorised security assessments.
---

# Windows PrivEsc Explorer

<div class="privesc-hero" data-platform="windows">

## Windows PrivEsc Explorer

Search Windows privilege escalation techniques based on the permissions, privileges, services, credentials, binaries, and configuration discovered during an authorised assessment.

<div class="privesc-hero-badges">
<span class="privesc-badge">WINDOWS</span>
<span class="privesc-badge">PRIVESC</span>
<span class="privesc-badge">INTERACTIVE</span>
</div>

</div>

---

# Explorer

<div id="privesc-explorer" data-platform="windows">

<div class="privesc-toolbar">

<div class="privesc-search-wrapper">
<label for="privesc-search">Search techniques</label>
<input
    id="privesc-search"
    class="privesc-search"
    type="search"
    placeholder="Try: SeImpersonate, service, scheduled task, DLL, credential..."
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

The explorer is designed around findings made during Windows enumeration.

Examples:

```text
SeImpersonatePrivilege
```

```text
SeBackupPrivilege
```

```text
SeRestorePrivilege
```

```text
SeTakeOwnershipPrivilege
```

```text
service
```

```text
unquoted service path
```

```text
scheduled task
```

```text
AlwaysInstallElevated
```

```text
PATH
```

```text
DLL
```

```text
AutoLogon
```

```text
credential
```

```text
AppLocker
```

```text
driver
```

---

# Windows Privilege Escalation Model

Windows privilege escalation commonly involves a lower-privileged identity gaining influence over a resource trusted by a more privileged security context.

```text
Standard User
     |
     v
Discovery
     |
     v
Interesting Permission / Privilege / Configuration
     |
     v
Privileged Consumer
     |
     v
Security Boundary
     |
     v
Controlled Validation
     |
     v
Elevated Impact
```

The important question is not:

```text
Can I modify this?
```

It is:

```text
Can I modify something that a more privileged component trusts?
```

---

# Categories

The explorer groups techniques into the following areas.

| Category | Focus |
|---|---|
| Services | Privileged Windows services and their dependencies |
| Scheduled Tasks | Tasks executing with elevated identities |
| Privileges | Windows user rights such as SeImpersonatePrivilege |
| Tokens | Access-token and impersonation conditions |
| Filesystem | Weak file and directory permissions |
| Registry | Security-sensitive registry permissions and configuration |
| DLL | DLL loading and search-order conditions |
| PATH | Unsafe executable search paths |
| Credentials | Credentials accessible to lower-privileged users |
| MSI | Windows Installer policy and deployment configuration |
| UAC | Elevation boundary and UAC configuration |
| Application Control | AppLocker and WDAC assessment conditions |
| Software | Privileged third-party or custom applications |
| Drivers | Kernel drivers and privileged driver interfaces |
| Configuration | Other security-sensitive Windows configuration |

---

# Services

Windows services are one of the most important privilege escalation surfaces.

The security relationship is commonly:

```text
Standard User
      |
      | controls
      v
Service Resource
      |
      | trusted by
      v
Privileged Service
      |
      v
SYSTEM / Administrator
```

Relevant resources can include:

```text
Service executable
Service directory
Service configuration
Registry configuration
Arguments
DLLs
Configuration files
Environment
Service account
```

---

## Enumerate Services

PowerShell:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, StartMode, PathName
```

Compact:

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,StartMode,PathName
```

Native:

```cmd
sc.exe query state= all
```

Specific service:

```cmd
sc.exe qc ServiceName
```

---

## Service Identity

Important service identities include:

```text
LocalSystem
NT AUTHORITY\SYSTEM

LocalService
NT AUTHORITY\LOCAL SERVICE

NetworkService
NT AUTHORITY\NETWORK SERVICE

Domain service accounts
Managed service accounts
Custom local accounts
```

A weakness affecting a service running as `SYSTEM` generally has greater local impact than one affecting an already low-privileged service.

---

## Writable Service Executable

Suppose:

```text
Service:
ExampleService

Account:
LocalSystem

Executable:
C:\Program Files\Example\service.exe
```

Check:

```cmd
icacls "C:\Program Files\Example\service.exe"
```

PowerShell:

```powershell
Get-Acl -LiteralPath "C:\Program Files\Example\service.exe" | Format-List Owner,AccessToString
```

The relevant condition is:

```text
Privileged Service
       |
       v
Executable
       ^
       |
Standard User Can Modify
```

Do not overwrite a production service binary merely to prove the issue.

---

## Writable Service Directory

Check the directory:

```cmd
icacls "C:\Program Files\Example"
```

PowerShell:

```powershell
Get-Acl -LiteralPath "C:\Program Files\Example" | Format-List Owner,AccessToString
```

A protected executable can still be exposed when its parent directory permits inappropriate:

```text
Create
Delete
Rename
Replace
```

operations.

Evaluate effective control rather than only the executable's ACL.

---

## Weak Service Permissions

Service-object permissions are different from filesystem permissions.

Relevant service rights can include the ability to:

```text
Change configuration
Start service
Stop service
Delete service
Change security descriptor
```

Inspect configuration:

```cmd
sc.exe qc ServiceName
```

Security descriptor:

```cmd
sc.exe sdshow ServiceName
```

Do not change the service configuration during routine enumeration.

---

## Unquoted Service Paths

Enumerate service paths containing spaces:

```powershell
Get-CimInstance Win32_Service | Where-Object { $_.PathName -match ' ' } | Select-Object Name,StartName,State,PathName
```

An unquoted path is not automatically exploitable.

The full condition requires analysis of:

```text
Unquoted executable path
+
Spaces in path
+
Windows path parsing
+
Writable candidate location
+
Privileged service
+
Execution opportunity
```

Do not report an unquoted service path without confirming the writable path condition.

---

# Scheduled Tasks

Scheduled tasks can execute:

```text
Programs
Scripts
PowerShell
Batch files
Maintenance actions
Administrative tooling
```

under privileged identities.

---

## Enumerate Scheduled Tasks

PowerShell:

```powershell
Get-ScheduledTask | Select-Object TaskPath,TaskName,State
```

Detailed:

```powershell
Get-ScheduledTask | ForEach-Object {
    $task = $_

    foreach ($action in $task.Actions) {
        [PSCustomObject]@{
            TaskPath  = $task.TaskPath
            TaskName  = $task.TaskName
            Execute   = $action.Execute
            Arguments = $action.Arguments
        }
    }
}
```

Native:

```cmd
schtasks.exe /query /fo LIST /v
```

---

## Scheduled Task Identity

Inspect:

```powershell
Get-ScheduledTask -TaskName "TaskName" | Select-Object -ExpandProperty Principal
```

Important properties include:

```text
UserId
LogonType
RunLevel
```

---

## Writable Scheduled Task Action

Suppose an elevated task executes:

```text
C:\ProgramData\Company\maintenance.ps1
```

Check:

```cmd
icacls "C:\ProgramData\Company\maintenance.ps1"
```

Parent directory:

```cmd
icacls "C:\ProgramData\Company"
```

The relationship becomes:

```text
Standard User
      |
      | writes
      v
Task Action
      |
      | executed by
      v
Privileged Scheduled Task
```

Permission evidence may be enough without modifying the task action.

---

# Windows Privileges

Enumerate the current token:

```cmd
whoami /priv
```

Example privileges can include:

```text
SeChangeNotifyPrivilege
SeImpersonatePrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeDebugPrivilege
SeLoadDriverPrivilege
SeCreateTokenPrivilege
SeAssignPrimaryTokenPrivilege
```

A privilege being listed does not automatically mean a practical escalation path exists.

Record its state:

```text
Enabled
Disabled
Removed / absent
```

and evaluate the surrounding security context.

---

# SeImpersonatePrivilege

Check:

```cmd
whoami /priv
```

Search for:

```text
SeImpersonatePrivilege
```

This privilege permits a process to impersonate security contexts under defined Windows conditions.

Potential relevance depends on whether the current context can obtain or interact with a suitable privileged token or authentication flow.

Do not report the privilege alone as a confirmed SYSTEM escalation.

---

# SeAssignPrimaryTokenPrivilege

Check:

```cmd
whoami /priv
```

This privilege can permit assignment of primary tokens under applicable Windows security rules.

Its practical impact depends on:

```text
Token availability
Process rights
Privilege state
Operating-system protections
Execution context
```

---

# SeBackupPrivilege

Check:

```cmd
whoami /priv
```

`SeBackupPrivilege` allows authorised backup operations to bypass certain normal file read restrictions.

It can expose sensitive operating-system data when assigned to an inappropriate identity.

Do not collect password databases or unrelated sensitive files unless explicitly required.

---

# SeRestorePrivilege

`SeRestorePrivilege` supports restoration operations that can bypass certain normal write restrictions.

Review whether the account legitimately requires this privilege.

The presence of the privilege should be assessed alongside accessible security-sensitive resources.

---

# SeTakeOwnershipPrivilege

`SeTakeOwnershipPrivilege` allows an identity to take ownership of securable objects under applicable conditions.

Ownership can subsequently influence discretionary access-control management.

Do not alter ownership of production resources merely to demonstrate the privilege.

---

# SeDebugPrivilege

`SeDebugPrivilege` provides extensive process inspection capabilities.

It is normally associated with highly trusted administrative contexts.

Potential impact includes access to sensitive process state.

Do not dump credential material from protected processes unless explicitly authorised.

---

# SeLoadDriverPrivilege

`SeLoadDriverPrivilege` is security-sensitive because kernel drivers execute within the Windows kernel security boundary.

Assess:

```text
Privilege assignment
Driver loading policy
Application control
Driver signing
Available driver configuration
```

Do not load arbitrary or vulnerable drivers merely to demonstrate impact.

---

# Access Tokens

Windows uses access tokens to represent a process or thread security context.

A token can contain:

```text
User SID
Group SIDs
Privileges
Integrity level
Restrictions
Session
Authentication information
```

Current identity:

```cmd
whoami /all
```

This provides:

```text
User
Groups
Privileges
Integrity information
```

---

# Integrity Levels

Common integrity levels include:

```text
Low
Medium
High
System
```

A standard desktop user normally operates at medium integrity.

An elevated administrator commonly operates at high integrity.

SYSTEM processes operate within a highly privileged system context.

---

# Filesystem Permissions

Filesystem weaknesses become relevant when privileged software trusts lower-privileged writable resources.

Check a file:

```cmd
icacls "C:\Path\file.exe"
```

Check a directory:

```cmd
icacls "C:\Path"
```

PowerShell:

```powershell
Get-Acl -LiteralPath "C:\Path\file.exe" | Format-List Owner,AccessToString
```

---

# Interesting ACL Principals

Pay attention to permissions granted to:

```text
Everyone
BUILTIN\Users
Authenticated Users
Current user
Current user's groups
Unexpected custom groups
```

Interesting rights can include:

```text
FullControl
Modify
Write
WriteData
CreateFiles
Delete
ChangePermissions
TakeOwnership
```

Interpret permissions in context.

---

# Writable Administrative Locations

Potentially interesting locations include:

```text
C:\Program Files\
C:\Program Files (x86)\
C:\ProgramData\
C:\Windows\
Application directories
Service directories
Deployment directories
Custom tool directories
```

Do not recursively probe the entire filesystem with aggressive write tests.

Use ACL inspection first.

---

# ProgramData

`C:\ProgramData` commonly contains application data.

Some subdirectories are intentionally writable by standard users.

A writable ProgramData directory becomes security-sensitive when:

```text
Privileged Service
        |
        v
Reads / Executes Resource
        ^
        |
Writable by Standard User
```

Writable ProgramData alone is not a vulnerability.

---

# PATH

Display PATH:

```cmd
echo %PATH%
```

PowerShell:

```powershell
$env:PATH -split ';'
```

Inspect permissions for individual directories:

```cmd
icacls "C:\Example\Bin"
```

---

# Writable PATH Directory

A writable PATH directory becomes interesting when privileged software executes a command without specifying a secure absolute path.

Required relationship:

```text
Writable PATH Directory
        +
Relative Command Execution
        +
Privileged Process
```

Do not report a writable PATH directory without identifying a privileged consumer.

---

# DLL Loading

Windows applications can load DLLs from multiple locations depending on:

```text
Application configuration
LoadLibrary usage
Known DLLs
Safe DLL search mode
Application directory
System directories
PATH
Explicit DLL paths
```

DLL findings require application-specific analysis.

---

# DLL Search Order Candidate

A potential condition may exist when:

```text
Privileged Process
       |
       v
Loads DLL by Name
       |
       v
Searches Writable Location
       |
       v
Lower-Privileged User Controls Candidate
```

The existence of a writable directory alone does not prove DLL hijacking.

---

# DLL Evidence

Useful evidence includes:

```text
Privileged process identity
Requested DLL name
Actual DLL path
Search path
Writable candidate directory
Application configuration
```

Where authorised, process-monitoring tools can help establish actual DLL resolution.

Avoid placing arbitrary DLLs into production application directories during initial validation.

---

# Registry

Registry permissions can influence:

```text
Services
Startup configuration
Applications
File associations
COM configuration
Environment
Installer settings
Security controls
```

---

# Registry ACL

PowerShell:

```powershell
Get-Acl -Path "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Example" | Format-List Owner,AccessToString
```

Do not modify registry values during initial enumeration.

---

# Service Registry

Service configuration is represented beneath:

```text
HKLM\SYSTEM\CurrentControlSet\Services
```

Example:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\ServiceName"
```

Relevant values can include:

```text
ImagePath
ObjectName
Start
Type
```

Use `sc.exe qc` as another source of service configuration evidence.

---

# AlwaysInstallElevated

Check both policy locations:

```cmd
reg.exe query HKCU\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```cmd
reg.exe query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

The security-sensitive condition historically requires the policy to be enabled in both the user and machine policy locations.

Do not report the condition based on only one value.

---

# PowerShell Check

```powershell
$hkcu = Get-ItemPropertyValue -Path "HKCU:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
$hklm = Get-ItemPropertyValue -Path "HKLM:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue

[PSCustomObject]@{
    HKCU = $hkcu
    HKLM = $hklm
}
```

A value of:

```text
1
```

in both relevant locations deserves investigation.

---

# Credentials

Potential credential sources include:

```text
Credential Manager
Application configuration
Service configuration
PowerShell history
Environment variables
Deployment files
Backup files
Unattended installation files
AutoLogon
SSH keys
Certificates
Developer tooling
Cloud configuration
```

Detailed handling is covered in [Windows Credentials](../windows/credentials.md).

---

# Credential Manager

List stored credentials:

```cmd
cmdkey.exe /list
```

The output can identify stored credential targets.

Do not assume every stored credential can be extracted or reused.

---

# AutoLogon

Relevant registry location:

```text
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```

Inspect selected values:

```cmd
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon
```

```cmd
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName
```

```cmd
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultDomainName
```

Do not print or collect `DefaultPassword` unnecessarily.

If AutoLogon is configured insecurely, record the configuration and protect any credential evidence.

---

# PowerShell History

Common PSReadLine history path:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Targeted review:

```powershell
$history = (Get-PSReadLineOption).HistorySavePath

if (Test-Path $history) {
    Select-String -Path $history -Pattern 'password|passwd|secret|token|credential|apikey|api_key' -CaseSensitive:$false
}
```

Do not include discovered secrets verbatim in reporting evidence.

---

# Environment Variables

```powershell
Get-ChildItem Env:
```

Targeted:

```powershell
Get-ChildItem Env: | Where-Object {
    $_.Name -match 'PASS|SECRET|TOKEN|KEY|CRED'
}
```

Environment-variable names may indicate credential storage.

Handle values carefully.

---

# Unattended Installation Files

Potential historical or deployment-related locations can include:

```text
C:\Windows\Panther\
C:\Windows\System32\Sysprep\
C:\Windows\System32\Sysprep\Panther\
```

Search targeted configuration files only where authorised.

Do not assume an unattended installation file contains usable credentials.

---

# Saved RDP and Administrative Credentials

Useful discovery sources can include:

```text
cmdkey.exe
Credential Manager
RDP configuration
Deployment scripts
Administrative scripts
```

The presence of a target in Credential Manager does not automatically mean privilege escalation is possible.

Determine:

```text
Stored identity
Target
Scope
Authentication behaviour
Privilege of destination identity
```

---

# UAC

User Account Control helps separate normal and elevated administrative execution.

Check whether the current identity belongs to the local Administrators group:

```cmd
whoami /groups
```

UAC is primarily relevant when the current user is already an administrator operating with a filtered token.

It should not be treated as a generic standard-user-to-administrator privilege escalation mechanism.

---

# UAC Configuration

Selected values are located under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
```

Inspect:

```cmd
reg.exe query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
```

Relevant values can include:

```text
EnableLUA
ConsentPromptBehaviorAdmin
PromptOnSecureDesktop
FilterAdministratorToken
```

Do not modify UAC settings during assessment.

---

# Application Control

Relevant technologies include:

```text
AppLocker
Windows Defender Application Control
Software Restriction Policies
Attack Surface Reduction
PowerShell language controls
```

Application-control assessment should distinguish:

```text
Executable allowed
```

from:

```text
Security boundary bypass confirmed
```

---

# AppLocker

Where accessible:

```powershell
Get-AppLockerPolicy -Effective
```

Summary:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections | Select-Object CollectionType,EnforcementMode
```

Test a specific file:

```powershell
Get-AppLockerPolicy -Effective | Test-AppLockerPolicy -Path "C:\Path\program.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

This tests the effective AppLocker decision for the specified path and user.

---

# AppLocker Rule Collections

Collections include:

```text
Exe
Msi
Script
Dll
Appx
```

Possible enforcement modes include:

```text
Enabled
AuditOnly
NotConfigured
```

Evaluate each relevant collection independently.

---

# PowerShell Language Mode

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible modes include:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

`FullLanguage` alone is not a vulnerability.

Language mode should be interpreted within the endpoint's intended security model.

---

# WDAC

Windows Defender Application Control can enforce code integrity policies.

Potential indicators include:

```text
Code Integrity operational logs
Configured policies
Application Control policy files
Enterprise management configuration
```

Do not infer WDAC state solely from whether one binary executes.

---

# LOLBins

Windows contains legitimate signed binaries that can provide functionality useful to administrators and applications.

Reference:

[LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }

Examples documented by LOLBAS can involve functionality such as:

```text
Execution
Download
File operations
Compilation
Script execution
```

A LOLBin being present or allowed is not automatically a vulnerability.

The security question is whether application-control policy allows functionality inconsistent with the organisation's intended trust model.

---

# Installed Software

PowerShell:

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

32-bit software on 64-bit Windows:

```powershell
Get-ItemProperty HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

---

# Software Assessment

For interesting software determine:

```text
Exact product
Exact version
Architecture
Install path
Service context
Update status
Vendor advisory
Local attack surface
Privileges
Configuration
```

Do not report a vulnerability based only on a product version from a generic vulnerability database.

Vendor backports and build-specific fixes must be considered.

---

# Custom Applications

Prioritise organisation-specific software under locations such as:

```text
C:\Program Files\
C:\Program Files (x86)\
C:\ProgramData\
Custom application directories
```

Review:

```text
Service identity
Executable ACL
Directory ACL
Configuration ACL
DLL dependencies
Plugins
Update mechanisms
Local IPC
Named pipes
Registry configuration
```

---

# Named Pipes

Named pipes can expose local inter-process communication.

Enumeration can be performed with PowerShell:

```powershell
Get-ChildItem \\.\pipe\
```

A named pipe is not automatically insecure.

Determine:

```text
Server process
Server privilege
Pipe ACL
Authentication
Impersonation behaviour
Available operations
```

---

# Drivers

Drivers operate in kernel mode and therefore represent a highly privileged trust boundary.

Enumerate:

```cmd
driverquery.exe
```

Verbose:

```cmd
driverquery.exe /v
```

PowerShell:

```powershell
Get-CimInstance Win32_SystemDriver | Select-Object Name,State,StartMode,PathName
```

---

# Driver Assessment

For interesting third-party drivers determine:

```text
Driver name
Vendor
Version
File path
Signature
Service configuration
Device interface
User accessibility
Known vendor advisory
```

Do not load or interact with vulnerable drivers beyond the authorised validation scope.

---

# Driver Signature

PowerShell:

```powershell
Get-AuthenticodeSignature "C:\Path\driver.sys"
```

Record:

```text
Status
SignerCertificate
Path
```

A valid signature does not prove that a driver is secure.

---

# Local Groups

Enumerate:

```cmd
whoami /groups
```

Local groups:

```cmd
net.exe localgroup
```

PowerShell:

```powershell
Get-LocalGroup
```

Membership:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

Availability of the LocalAccounts module depends on the host and PowerShell environment.

---

# Interesting Groups

Examples can include:

```text
Administrators
Backup Operators
Remote Desktop Users
Remote Management Users
Hyper-V Administrators
Event Log Readers
Custom application administration groups
```

Group membership must be mapped to actual permissions.

---

# Backup Operators

Membership can provide backup and restore-related rights.

Verify effective privileges:

```cmd
whoami /priv
```

Do not assume group membership alone means the relevant privileges are active in the current token.

---

# Hyper-V Administrators

Virtualisation administration can represent a highly privileged role.

Assess:

```text
VM management rights
Virtual disk access
Host resource access
Management interfaces
Operational need
```

Do not manipulate production virtual machines merely to demonstrate privilege.

---

# COM and DCOM

Windows applications can expose privileged functionality through COM and DCOM.

A useful assessment should identify:

```text
Component
Server process
Privilege
Launch permissions
Access permissions
Registry configuration
User-controlled inputs
```

Do not treat the existence of COM registration as a privilege escalation finding.

---

# WMI

WMI exposes extensive system-management functionality.

Current user access depends on:

```text
Namespace permissions
DCOM permissions
Local groups
UAC
Remote configuration
```

Local WMI availability alone is not a privilege escalation vulnerability.

---

# Registry Autoruns

Common startup locations include:

```text
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

Inspect:

```cmd
reg.exe query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

```cmd
reg.exe query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
```

A per-user autorun normally executes only as that user.

For privilege escalation, identify a higher-privileged consumer.

---

# Startup Directories

Current user:

```powershell
[Environment]::GetFolderPath("Startup")
```

All users:

```powershell
[Environment]::GetFolderPath("CommonStartup")
```

Inspect ACLs before making conclusions.

---

# Security Products

Security tooling can influence privilege escalation feasibility and detection.

Potential products include:

```text
Microsoft Defender Antivirus
Microsoft Defender for Endpoint
Third-party EDR
Application control
Host firewall
Exploit protection
Credential Guard
LSA protection
```

Do not disable these controls for testing.

---

# Microsoft Defender

Where accessible:

```powershell
Get-MpComputerStatus
```

Selected properties:

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,BehaviorMonitorEnabled,AntispywareEnabled
```

The absence or configuration of one protection feature should be interpreted within the overall endpoint security architecture.

---

# Attack Surface Reduction

Where accessible:

```powershell
Get-MpPreference | Select-Object AttackSurfaceReductionRules_Ids,AttackSurfaceReductionRules_Actions
```

ASR rules can block or audit behaviours relevant to privilege escalation and post-exploitation.

Do not modify ASR configuration during assessment.

---

# Credential Guard

Credential Guard protects selected credential material using virtualization-based security.

Its presence can affect credential-access techniques.

Credential Guard should not be treated as a general privilege escalation prevention mechanism.

---

# LSA Protection

LSA protection can reduce unauthorised interaction with LSASS.

Its state should be documented when credential-access paths are part of the assessment.

Do not disable it to facilitate testing.

---

# Candidate Validation

The explorer should treat every result as a candidate.

Use:

```text
Candidate
   |
   v
Confirm Current User
   |
   v
Confirm Permission
   |
   v
Confirm Privileged Consumer
   |
   v
Confirm Activation
   |
   v
Assess Existing Controls
   |
   v
Minimal Validation
```

---

# Example - Writable Service Binary

Discovery:

```text
C:\Program Files\Example\service.exe

BUILTIN\Users:(M)
```

Service:

```text
SERVICE_START_NAME : LocalSystem
```

Model:

```text
Standard User
     |
     | Modify
     v
service.exe
     |
     | Executed by
     v
LocalSystem Service
```

This is significantly stronger evidence than simply identifying a writable executable.

---

# Example - Scheduled Task

Discovery:

```text
Task:
\Company\Maintenance

Run As:
SYSTEM

Action:
C:\ProgramData\Company\maintenance.ps1
```

ACL:

```text
BUILTIN\Users:(M)
```

Model:

```text
Standard User
     |
     | Modify
     v
maintenance.ps1
     |
     | Scheduled execution
     v
SYSTEM
```

---

# Example - Privilege

Discovery:

```text
SeBackupPrivilege
```

Do not immediately conclude:

```text
SYSTEM compromise
```

Instead determine:

```text
Why does the user have it?
Is it enabled?
What resources can it access?
Is the access required?
Can impact be demonstrated without extracting secrets?
```

---

# Example - Application Control

Discovery:

```text
Executable allowed by AppLocker
```

Do not automatically report:

```text
AppLocker bypass
```

Determine whether the allowed executable exposes functionality that meaningfully violates the intended application-control policy.

---

# Evidence Collection

For each candidate collect:

| Field | Example |
|---|---|
| Host | `WS-01` |
| Current user | `DOMAIN\analyst` |
| Integrity | Medium |
| Technique | Writable Service Executable |
| Resource | `C:\Program Files\Example\service.exe` |
| Privileged consumer | `ExampleService` |
| Consumer identity | `LocalSystem` |
| Permission | Modify |
| Activation | Service start |
| Validation | ACL and configuration |
| Result | Privilege boundary confirmed |
| MITRE | T1574.010 |

---

# Safe Validation

Prefer evidence such as:

```text
whoami /all
```

```text
sc.exe qc ServiceName
```

```text
icacls "C:\Path\file.exe"
```

over modifying production resources.

A finding can often be proven using:

```text
Identity Evidence
       +
Permission Evidence
       +
Privileged Execution Evidence
```

---

# Do Not Automatically Report

Do not automatically report:

```text
Unquoted service path
```

without a writable candidate path.

Do not automatically report:

```text
SeImpersonatePrivilege
```

without evaluating usable conditions.

Do not automatically report:

```text
Writable directory
```

without identifying a privileged consumer.

Do not automatically report:

```text
Old software
```

without confirming vulnerability applicability.

Do not automatically report:

```text
AppLocker allowed
```

without showing why the allowed functionality breaks the intended control.

Do not automatically report:

```text
DLL missing
```

without confirming the privileged application's actual DLL search behaviour.

---

# Detection Opportunities

Windows privilege escalation monitoring can include:

```text
Service configuration changes
Service executable modification
Scheduled task modification
Security-sensitive registry changes
New privileged processes
Token manipulation
Privilege use
Driver installation
Driver loading
Application-control events
PowerShell activity
Sensitive file access
Credential access
Local group changes
```

---

# Windows Event Logs

Potentially relevant logs include:

```text
Security
System
Microsoft-Windows-PowerShell/Operational
Microsoft-Windows-AppLocker/*
Microsoft-Windows-CodeIntegrity/Operational
Microsoft-Windows-Windows Defender/Operational
TaskScheduler Operational logs
```

Actual logging depends on configuration.

---

# Service Changes

Service creation can generate security and system telemetry depending on audit configuration.

Defenders should monitor unexpected:

```text
Service creation
Service binary changes
Service account changes
Service configuration changes
```

especially when the resulting service runs as `SYSTEM`.

---

# Scheduled Task Changes

Monitor:

```text
Task creation
Task modification
Task deletion
Action changes
Principal changes
Unexpected SYSTEM tasks
```

Baseline legitimate administrative tooling to reduce noise.

---

# Privileged File Changes

Monitor modifications to:

```text
Service executables
Scheduled task scripts
Program Files
Sensitive ProgramData applications
Security configuration
Administrative scripts
```

File integrity monitoring can help identify unexpected changes.

---

# Remediation Model

Privilege escalation remediation should remove the underlying trust failure.

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
Add Monitoring
   |
   v
Retest
```

---

# Service Remediation

Recommended controls include:

```text
Protect service executables
Protect service directories
Restrict service-object permissions
Quote executable paths
Use dedicated service accounts
Use least privilege
Protect configuration and DLLs
```

---

# Scheduled Task Remediation

```text
Protect task action files
Protect parent directories
Restrict task modification
Use dedicated identities
Use minimum required privilege
Use absolute paths
Protect scripts and configuration
```

---

# Privilege Remediation

Review assignment of security-sensitive privileges.

Remove privileges that are not operationally required.

Pay particular attention to:

```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeDebugPrivilege
SeLoadDriverPrivilege
```

The appropriate assignment depends on the account's role.

---

# Filesystem Remediation

Avoid broad write access such as:

```text
Everyone - Full Control
Users - Modify
Authenticated Users - Modify
```

on resources consumed by privileged software unless explicitly required.

Apply least privilege to:

```text
Files
Directories
Scripts
Configuration
DLLs
Executables
```

---

# Credential Remediation

```text
Remove plaintext credentials
Use dedicated identities
Use managed identities where possible
Restrict file ACLs
Rotate exposed credentials
Avoid secrets in command lines
Avoid secrets in scripts
Use approved secret-management systems
```

---

# Application Control Remediation

Application control should be designed around:

```text
Trusted publishers
Trusted applications
Approved paths
Script controls
DLL controls where appropriate
User privilege
Operational requirements
```

Avoid relying solely on broad writable path rules.

---

# Driver Remediation

```text
Remove unnecessary drivers
Update vulnerable drivers
Restrict driver installation
Use driver block policies
Monitor driver loading
Use application control
Maintain supported software
```

---

# Technique Confidence

Use three practical confidence levels.

## Candidate

```text
Interesting configuration discovered.
```

Example:

```text
Service path contains spaces.
```

## Likely

```text
Most important prerequisites are present.
```

Example:

```text
Unquoted privileged service path with a writable candidate directory.
```

## Confirmed

```text
The privilege boundary has been demonstrated using sufficient evidence.
```

Example:

```text
Standard user has Modify access to the executable used by a LocalSystem service.
```

---

# Severity Considerations

Severity depends on:

```text
Starting identity
Resulting identity
Required interaction
Reliability
Activation conditions
Scope
Existing controls
System criticality
Persistence potential
Detection
```

A deterministic:

```text
Standard User -> SYSTEM
```

path normally carries more impact than a theoretical configuration weakness requiring unrealistic conditions.

---

# Windows Explorer Checklist

## Context

- [ ] Current user
- [ ] Groups
- [ ] Privileges
- [ ] Integrity level
- [ ] Hostname
- [ ] OS
- [ ] Architecture
- [ ] Security products

## Services

- [ ] Privileged services
- [ ] Executable paths
- [ ] Executable ACLs
- [ ] Directory ACLs
- [ ] Service-object permissions
- [ ] Unquoted paths
- [ ] Writable configuration
- [ ] DLL dependencies
- [ ] Service account
- [ ] Restart opportunity

## Scheduled Tasks

- [ ] Task inventory
- [ ] Task identity
- [ ] Run level
- [ ] Action executable
- [ ] Action arguments
- [ ] Script ACL
- [ ] Directory ACL
- [ ] Task modification rights
- [ ] Trigger

## Privileges

- [ ] SeImpersonatePrivilege
- [ ] SeAssignPrimaryTokenPrivilege
- [ ] SeBackupPrivilege
- [ ] SeRestorePrivilege
- [ ] SeTakeOwnershipPrivilege
- [ ] SeDebugPrivilege
- [ ] SeLoadDriverPrivilege

## Filesystem

- [ ] Program Files
- [ ] ProgramData
- [ ] Custom applications
- [ ] Writable executables
- [ ] Writable scripts
- [ ] Writable configuration
- [ ] Writable DLL locations
- [ ] Parent-directory ACLs

## Registry

- [ ] Service registry configuration
- [ ] Security-sensitive writable keys
- [ ] Installer policy
- [ ] Autoruns
- [ ] Application configuration

## Credentials

- [ ] Credential Manager
- [ ] AutoLogon
- [ ] PowerShell history
- [ ] Environment
- [ ] Application configuration
- [ ] Deployment files
- [ ] SSH keys
- [ ] Certificates

## Application Control

- [ ] AppLocker
- [ ] WDAC
- [ ] PowerShell language mode
- [ ] ASR
- [ ] Allowed administrative binaries
- [ ] Intended policy boundary

## Software

- [ ] Installed applications
- [ ] Third-party services
- [ ] Custom applications
- [ ] Drivers
- [ ] Vendor advisories
- [ ] Patch status

## Validation

- [ ] Candidate prerequisites confirmed
- [ ] Privileged consumer identified
- [ ] Lower-privileged control identified
- [ ] Minimal validation selected
- [ ] Evidence collected
- [ ] Production modification avoided
- [ ] Cleanup completed where required

---

# Quick Enumeration

Identity:

```cmd
whoami
```

Full token:

```cmd
whoami /all
```

Privileges:

```cmd
whoami /priv
```

Groups:

```cmd
whoami /groups
```

Services:

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,StartMode,PathName
```

Scheduled tasks:

```powershell
Get-ScheduledTask | Select-Object TaskPath,TaskName,State
```

PATH:

```powershell
$env:PATH -split ';'
```

Stored credential targets:

```cmd
cmdkey.exe /list
```

AppLocker:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections | Select-Object CollectionType,EnforcementMode
```

PowerShell language mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Drivers:

```powershell
Get-CimInstance Win32_SystemDriver | Select-Object Name,State,StartMode,PathName
```

Installed software:

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

---

# Explorer Decision Tree

```text
Start
 |
 v
whoami /all
 |
 v
Interesting Privileges?
 |
 +---- Yes ---> Search Privilege
 |
 v
Enumerate Services
 |
 +---- Writable Dependency? ---> Search Service
 |
 v
Enumerate Scheduled Tasks
 |
 +---- Writable Action? ------> Search Scheduled Task
 |
 v
Review Filesystem
 |
 +---- Privileged Consumer? --> Search Filesystem
 |
 v
Review Registry
 |
 +---- Privileged Setting? ---> Search Registry
 |
 v
Review Credentials
 |
 +---- Higher Privilege? -----> Search Credentials
 |
 v
Review PATH / DLL Loading
 |
 +---- Privileged Consumer? --> Search PATH / DLL
 |
 v
Review Application Control
 |
 +---- Unexpected Capability? -> Search App Control
 |
 v
Review Software / Drivers
 |
 +---- Confirmed Candidate? --> Validate
 |
 v
No Confirmed Local PrivEsc Path
```

---

# Final Testing Model

```text
1. Establish the current Windows identity.

2. Record groups, privileges, and integrity level.

3. Enumerate privileged services.

4. Review service executable paths.

5. Review service executable and directory ACLs.

6. Review service-object permissions.

7. Validate unquoted service paths correctly.

8. Enumerate scheduled tasks.

9. Identify tasks running under privileged identities.

10. Review task actions and their ACLs.

11. Enumerate security-sensitive token privileges.

12. Determine whether the required privilege conditions exist.

13. Review filesystem permissions.

14. Identify privileged consumers of writable resources.

15. Review security-sensitive registry permissions.

16. Review Windows Installer policy.

17. Review PATH configuration.

18. Identify privileged relative command execution.

19. Review DLL loading only in application context.

20. Identify credential exposure.

21. Determine whether exposed identities increase privilege.

22. Review local group membership.

23. Review UAC in the correct administrative context.

24. Review AppLocker and WDAC where applicable.

25. Distinguish allowed execution from policy bypass.

26. Review installed third-party software.

27. Review custom privileged applications.

28. Review drivers and kernel interfaces.

29. Consider endpoint security controls.

30. Prioritise deterministic configuration weaknesses.

31. Validate with configuration and permission evidence first.

32. Avoid modifying production binaries.

33. Avoid changing services or scheduled tasks unnecessarily.

34. Avoid credential extraction where configuration evidence is sufficient.

35. Avoid disabling security controls.

36. Avoid unnecessary SYSTEM shells.

37. Record the complete privilege relationship.

38. Identify the actual root cause.

39. Recommend least-privilege remediation.

40. Retest the corrected boundary.
```

The Windows explorer should therefore answer:

```text
What did I discover?
        |
        v
What privileged component trusts it?
        |
        v
Do I actually control it?
        |
        v
What conditions are required?
        |
        v
How can I validate it safely?
        |
        v
How should it be detected and fixed?
```

rather than simply:

```text
Which exploit should I run?
```

---

# Related Notes

- [PrivEsc Explorer](index.md)
- [Linux PrivEsc Explorer](linux.md)
- [Windows](../windows/index.md)
- [Windows Enumeration](../windows/enumeration.md)
- [Windows Services](../windows/services.md)
- [Windows Credentials](../windows/credentials.md)
- [Windows Privilege Escalation](../windows/privilege-escalation.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [Microsoft - Windows Security](https://learn.microsoft.com/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Access Control](https://learn.microsoft.com/windows/win32/secauthz/access-control){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Access Tokens](https://learn.microsoft.com/windows/win32/secauthz/access-tokens){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Privilege Constants](https://learn.microsoft.com/windows/win32/secauthz/privilege-constants){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Service Security and Access Rights](https://learn.microsoft.com/windows/win32/services/service-security-and-access-rights){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Task Scheduler](https://learn.microsoft.com/windows/win32/taskschd/task-scheduler-start-page){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - User Account Control](https://learn.microsoft.com/windows/security/application-security/application-control/user-account-control/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - App Control for Business](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Attack Surface Reduction](https://learn.microsoft.com/defender-endpoint/attack-surface-reduction){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Driver Security](https://learn.microsoft.com/windows-hardware/drivers/driversecurity/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Hijack Execution Flow](https://attack.mitre.org/techniques/T1574/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Services File Permissions Weakness](https://attack.mitre.org/techniques/T1574/010/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [WADComs](https://wadcoms.github.io/){ target="_blank" rel="noopener noreferrer" }
- [LOLAD](https://lolad-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [Command Manager](https://commandmgr.com/){ target="_blank" rel="noopener noreferrer" }

---

> Use Windows privilege escalation techniques only on systems you own or have explicit permission to assess. Explorer results represent assessment candidates rather than automatically confirmed vulnerabilities. Prefer identity, configuration, ACL, and privileged-consumer evidence before modifying services, binaries, scheduled tasks, registry settings, credentials, drivers, or security controls.
