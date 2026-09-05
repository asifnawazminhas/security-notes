---
title: Windows PrivEsc Explorer
description: Interactive Windows privilege escalation reference for authorised security assessments.
---

# Windows PrivEsc Explorer

<div class="privesc-hero">

<h2>Windows PrivEsc Explorer</h2>

<p>
Search Windows privilege escalation techniques based on the permissions,
privileges, services, credentials, binaries, and configuration discovered
during an authorised assessment.
</p>

<div class="privesc-card-badges">
<span class="privesc-badge privesc-badge-platform">Windows</span>
<span class="privesc-badge privesc-badge-category">PrivEsc</span>
<span class="privesc-badge privesc-badge-category">Interactive</span>
</div>

</div>


---

## Explorer

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
No techniques found. Try another search term or reset the filters.
</div>

</div>


---

## Search Examples

Try searching for:

```text
SeImpersonate
SeBackup
SeRestore
SeDebug
SeLoadDriver
service
scheduled task
writable
DLL
PATH
registry
credential
AutoLogon
PowerShell
AppLocker
UAC
driver
named pipe
autorun
```

The search engine evaluates multiple fields in each technique entry rather than only matching the technique name.


---

## Windows Privilege Escalation Model

Windows privilege escalation usually involves a lower-privileged user being able to influence something that is later consumed by a more privileged security context.

```text
Current User
    |
    v
Enumeration
    |
    +--> Services
    +--> Scheduled Tasks
    +--> Privileges
    +--> Access Tokens
    +--> Filesystem ACLs
    +--> Registry ACLs
    +--> PATH
    +--> DLL Loading
    +--> Credentials
    +--> Application Control
    +--> UAC
    +--> Installed Software
    +--> Drivers
    +--> Named Pipes
    +--> Autoruns
    |
    v
Candidate
    |
    v
Validate Privilege Relationship
    |
    v
Determine Impact
```

The presence of an interesting condition does not automatically prove privilege escalation.


---

## Establish the Current Security Context

Start by understanding the current identity.

```powershell
whoami
```

```powershell
whoami /user
```

```powershell
whoami /groups
```

```powershell
whoami /priv
```

```powershell
whoami /all
```

Useful PowerShell context:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

```powershell
$ExecutionContext.SessionState.LanguageMode
```

The current user, group memberships, privileges, integrity level, and execution restrictions determine which privilege escalation paths are relevant.


---

## Services

Windows services are an important privilege escalation surface because many services execute as privileged identities such as:

```text
LocalSystem
LocalService
NetworkService
Domain service accounts
Custom privileged accounts
```

Enumerate services:

```powershell
Get-Service
```

```cmd
sc query
```

Inspect service configuration:

```cmd
sc qc <SERVICE_NAME>
```

PowerShell:

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName
```

Useful fields include:

```text
Name
StartName
State
PathName
StartMode
```

The central question is:

```text
Can the current user influence something executed by a privileged service?
```


---

## Writable Service Executable

A service executable may represent a privilege escalation candidate when:

```text
Service
    |
    v
Runs as Privileged Identity
    |
    v
Executes Binary
    |
    v
Binary Writable by Lower-Privileged User
```

Inspect permissions:

```cmd
icacls "C:\Path\service.exe"
```

PowerShell:

```powershell
Get-Acl "C:\Path\service.exe" | Format-List
```

Do not replace the executable merely to prove the condition.

The combination of privileged execution identity and writable executable permissions may already provide sufficient evidence.


---

## Writable Service Directory

Even if the service executable itself is protected, inspect its parent directory.

```cmd
icacls "C:\Path"
```

A writable parent directory can be security relevant because it may permit:

```text
File replacement
Dependency placement
Configuration modification
Application resource modification
```

Always determine whether the privileged service actually consumes the controlled resource.


---

## Weak Service Object Permissions

Service Control Manager permissions can allow users to modify service configuration independently of filesystem permissions.

Inspect service configuration:

```cmd
sc qc <SERVICE_NAME>
```

Where authorised tooling is available, inspect the service security descriptor.

The important permissions may include the ability to:

```text
Change service configuration
Change binary path
Change service account
Start service
Stop service
Modify service security
```

A writable service object running as `LocalSystem` can represent a significant privilege boundary.


---

## Unquoted Service Paths

An unquoted service path may be interesting when:

```text
Service path contains spaces
        +
Path is not quoted
        +
Earlier interpreted location is writable
        +
Service runs privileged
```

Example:

```text
C:\Program Files\Example Service\service.exe
```

The issue is not simply that the path is unquoted.

You must also establish whether a lower-privileged user can control a path Windows could resolve before the intended executable.


---

## Scheduled Tasks

Enumerate scheduled tasks:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Inspect task actions:

```powershell
Get-ScheduledTask | Select-Object TaskName,TaskPath,State
```

Useful questions include:

```text
What executes?
Who executes it?
When does it execute?
Is the executable writable?
Is the script writable?
Is the working directory writable?
Can the task definition be modified?
```


---

## Writable Scheduled Task Action

A common relationship is:

```text
Scheduled Task
      |
      v
Privileged Identity
      |
      v
Executes Script or Binary
      |
      v
Resource Writable by Current User
```

Inspect the target resource:

```cmd
icacls "C:\Path\task-script.ps1"
```

or:

```powershell
Get-Acl "C:\Path\task-script.ps1" | Format-List
```

Prefer demonstrating the permission relationship without modifying or triggering production tasks.


---

## Windows Privileges

Enumerate privileges:

```cmd
whoami /priv
```

Security-sensitive privileges include:

```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeDebugPrivilege
SeLoadDriverPrivilege
```

A privilege being present does not automatically mean practical privilege escalation is possible.


---

## SeImpersonatePrivilege

`SeImpersonatePrivilege` allows a process to impersonate certain security tokens.

It is commonly associated with service identities and application pools.

Relevant contexts can include:

```text
IIS application pools
SQL Server services
Service accounts
LocalService
NetworkService
Other service processes
```

Validation should focus on:

```text
Current process identity
Privilege state
Available token context
Operating-system protections
Security boundaries involved
```


---

## SeAssignPrimaryTokenPrivilege

This privilege can permit assignment of primary tokens under specific circumstances.

Enumerate with:

```cmd
whoami /priv
```

The privilege should be treated as a candidate requiring contextual validation rather than automatic proof of escalation.


---

## SeBackupPrivilege

`SeBackupPrivilege` can permit security-sensitive read operations that bypass normal filesystem access checks in applicable contexts.

Potentially sensitive targets include:

```text
Registry hives
Configuration files
Credential material
Protected system data
```

The security significance depends on whether access can expose material that enables further privilege escalation.


---

## SeRestorePrivilege

`SeRestorePrivilege` can permit security-sensitive write operations that bypass normal filesystem restrictions in applicable contexts.

The impact depends on which privileged resources can actually be modified.


---

## SeTakeOwnershipPrivilege

This privilege may allow ownership of securable objects to be changed.

The important chain is:

```text
Take Ownership
      |
      v
Change Permissions
      |
      v
Control Privileged Resource
```

Do not change ownership of production resources unless explicitly required and authorised.


---

## SeDebugPrivilege

`SeDebugPrivilege` provides powerful access to processes and can cross important process-security boundaries.

Determine:

```text
Is the privilege enabled?
What processes are accessible?
What protection mechanisms are present?
Does the current context already have administrative authority?
```


---

## SeLoadDriverPrivilege

This privilege may permit driver loading in applicable contexts.

Driver-based privilege escalation is high impact and potentially destabilising.

Prefer configuration-based validation rather than loading arbitrary drivers on production systems.


---

## Access Tokens

Windows access tokens define the security context associated with processes and threads.

Useful concepts include:

```text
User SID
Group SIDs
Privileges
Integrity level
Restricted SIDs
Token type
Impersonation level
```

Enumerate:

```cmd
whoami /all
```

Understanding token context is especially important when investigating service accounts and impersonation-related privilege escalation.


---

## Integrity Levels

Windows integrity levels commonly include:

```text
Low
Medium
High
System
```

An administrator running a medium-integrity process is different from a standard user with no administrative membership.

Do not report UAC-related observations without establishing the actual token and administrative context.


---

## Filesystem Permissions

Inspect permissions with:

```cmd
icacls "C:\Path"
```

PowerShell:

```powershell
Get-Acl "C:\Path" | Format-List
```

Interesting permissions may include:

```text
FullControl
Modify
Write
WriteData
CreateFiles
CreateDirectories
Delete
ChangePermissions
TakeOwnership
```

Interesting principals may include:

```text
Everyone
Users
Authenticated Users
Domain Users
Current user
Current user's groups
```


---

## Program Files and ProgramData

Useful locations include:

```text
C:\Program Files
C:\Program Files (x86)
C:\ProgramData
```

Do not assume a writable directory under `ProgramData` is automatically vulnerable.

Determine whether a privileged application, service, task, or other security-sensitive process consumes the writable content.


---

## PATH Configuration

Inspect PATH:

```cmd
echo %PATH%
```

PowerShell:

```powershell
$env:PATH -split ';'
```

For each directory, consider:

```text
Who can write there?
Does a privileged process use PATH resolution?
Does the privileged process execute a relative command?
Is the intended executable found later in PATH?
```

A writable PATH directory without a privileged consumer is not automatically a privilege escalation vulnerability.


---

## DLL Loading

DLL-related candidates can involve:

```text
Missing DLLs
Writable application directories
Writable dependency directories
Unsafe DLL search order
User-controlled working directories
Custom privileged applications
```

Useful investigation tools include:

```text
Process Monitor
Process Explorer
AccessChk
Filesystem ACL inspection
Application configuration review
```

Avoid placing arbitrary DLLs into production application directories unless active exploitation is explicitly authorised.


---

## Registry Permissions

Inspect a registry key:

```powershell
Get-Acl "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Example" | Format-List
```

Service registry configuration can be inspected under:

```text
HKLM\SYSTEM\CurrentControlSet\Services
```

Potentially sensitive writable values include those controlling:

```text
Service executable paths
Application configuration
Autoruns
Security configuration
Environment values
Privileged application settings
```


---

## AlwaysInstallElevated

Check:

```cmd
reg query HKCU\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```cmd
reg query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Both policy locations and the actual operating context should be considered before reaching a conclusion.


---

## Credential Exposure

Potential credential locations include:

```text
Credential Manager
PowerShell history
Environment variables
Configuration files
Unattended installation files
Application configuration
Deployment scripts
Saved administrative credentials
RDP configuration
Backup files
```

Credential discovery should remain within the agreed assessment scope.


---

## Credential Manager

Enumerate stored credential targets:

```cmd
cmdkey /list
```

The existence of a target does not necessarily mean credential material can be extracted or reused.

Determine the actual security impact.


---

## PowerShell History

Common history path:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Review only where authorised.

History may contain:

```text
Credentials
Tokens
Administrative commands
Internal hosts
API keys
Deployment commands
```


---

## Environment Variables

Enumerate:

```cmd
set
```

PowerShell:

```powershell
Get-ChildItem Env:
```

Look for secrets only within authorised scope.


---

## Unattended Files

Potential locations can include:

```text
C:\Windows\Panther
C:\Windows\Panther\Unattend
C:\Windows\System32\Sysprep
```

Search carefully and avoid indiscriminate collection of unrelated sensitive information.


---

## UAC Context

Useful questions include:

```text
Is the user a local administrator?
What integrity level is the current process?
Is UAC enabled?
What is the configured elevation behaviour?
Is the scenario a real privilege escalation or an elevation boundary?
```

UAC observations should be reported with accurate context.


---

## AppLocker

Where available:

```powershell
Get-AppLockerPolicy -Effective
```

Inspect rule collections:

```text
Executable
Windows Installer
Script
Packaged app
DLL
```

An application-control gap can be security relevant, but the ability to execute a particular signed binary does not automatically prove a privilege escalation vulnerability.


---

## PowerShell Language Mode

Check:

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

`FullLanguage` is normal on many Windows systems.

It becomes more interesting where the endpoint is intended to enforce restrictive application-control boundaries for lower-privileged users.


---

## Drivers

Enumerate installed drivers using appropriate system tooling.

Driver assessment should consider:

```text
Driver version
Signature
Vendor
Known vulnerability
Loaded state
Accessible device objects
Required privileges
Exploitability mitigations
```

Do not assume an old driver version is exploitable without confirming the exact affected version and conditions.


---

## Named Pipes

Named pipes may expose privileged local interfaces.

Assess:

```text
Pipe ACL
Server identity
Client authentication
Impersonation behaviour
Protocol
Authorisation
```

A named pipe being present is not automatically a vulnerability.


---

## Autoruns and Startup Resources

Potential persistence and privilege escalation surfaces can include:

```text
Run keys
Startup folders
Services
Scheduled tasks
Application-specific startup mechanisms
```

The important relationship remains:

```text
Lower-Privileged Write Access
        +
Privileged Execution
        =
Candidate
```


---

## Custom Applications

Custom privileged software deserves particular attention because application-specific trust relationships may not be covered by generic operating-system hardening.

Investigate:

```text
Installation directory
Configuration
Plugins
Libraries
Update mechanisms
Service integration
Named pipes
Local sockets
Temporary files
Log directories
PATH usage
Credential storage
```


---

## Security Products

Understand the defensive context before interpreting findings.

Relevant controls can include:

```text
Microsoft Defender Antivirus
Attack Surface Reduction
AppLocker
Windows Defender Application Control
Credential Guard
LSA protection
EDR
Privilege-management products
```

The objective is not to disable these controls.

Their presence may materially affect whether a candidate is exploitable.


---

## Candidate Validation

A useful validation model is:

```text
Finding
   |
   v
Who Controls It?
   |
   v
Who Consumes It?
   |
   v
What Identity Is Used?
   |
   v
Can the Resource Be Influenced?
   |
   v
Are Security Controls Present?
   |
   v
What Privilege Would Be Obtained?
```

Example:

```text
Writable service.exe
        |
        v
Writable by normal user?
        |
       Yes
        |
        v
Service runs as SYSTEM?
        |
       Yes
        |
        v
Service executes that exact binary?
        |
       Yes
        |
        v
Strong PrivEsc Candidate
```


---

## Evidence

Strong evidence should identify:

```text
Current user
Affected object
Relevant permissions
Privileged consumer
Execution identity
Security impact
```

For example:

```text
Current user:
CORP\user

Affected resource:
C:\Program Files\Example\Service.exe

Permission:
BUILTIN\Users:(M)

Privileged consumer:
ExampleService

Execution identity:
LocalSystem
```

This demonstrates the security relationship without replacing the executable.


---

## What Not to Report Automatically

Do not automatically report:

```text
Writable temporary directory
Old software version
FullLanguage PowerShell
Allowed Windows binary
Unquoted service path
SUID-like application behaviour
Interesting privilege
Writable ProgramData directory
Stored credential target
Named pipe
Driver
```

Each requires context.


---

## Detection Opportunities

Useful telemetry may include:

```text
Process creation
Service configuration changes
Service creation
Scheduled-task changes
Registry changes
File permission changes
Sensitive file writes
DLL loading
Driver loading
PowerShell activity
Credential access
Application-control events
```

Where available, correlate activity with:

```text
User
Process
Parent process
Integrity level
Target resource
Timestamp
Host
```


---

## Remediation Model

Privilege escalation remediation commonly involves:

```text
Remove unnecessary privileges
        |
        v
Correct filesystem ACLs
        |
        v
Correct registry ACLs
        |
        v
Protect service configuration
        |
        v
Protect scheduled-task resources
        |
        v
Use explicit executable paths
        |
        v
Protect PATH directories
        |
        v
Protect DLL dependencies
        |
        v
Remove exposed credentials
        |
        v
Harden application control
        |
        v
Patch vulnerable software and drivers
        |
        v
Monitor privileged configuration changes
```


---

## Quick Enumeration

```cmd
whoami /all
```

```cmd
whoami /priv
```

```cmd
whoami /groups
```

```cmd
systeminfo
```

```cmd
sc query
```

```cmd
schtasks /query /fo LIST /v
```

```cmd
cmdkey /list
```

```cmd
echo %PATH%
```

PowerShell:

```powershell
Get-CimInstance Win32_Service | Select-Object Name,StartName,State,PathName
```

```powershell
Get-ScheduledTask
```

```powershell
$ExecutionContext.SessionState.LanguageMode
```

```powershell
Get-ChildItem Env:
```


---

## Checklist

### Identity

- [ ] Current user identified
- [ ] User SID recorded
- [ ] Group memberships reviewed
- [ ] Privileges reviewed
- [ ] Integrity level understood

### Services

- [ ] Privileged services enumerated
- [ ] Service executable paths reviewed
- [ ] Service executable ACLs reviewed
- [ ] Service directory ACLs reviewed
- [ ] Service object permissions considered
- [ ] Unquoted paths reviewed contextually

### Scheduled Tasks

- [ ] Tasks enumerated
- [ ] Execution identities reviewed
- [ ] Task actions reviewed
- [ ] Scripts and binaries checked
- [ ] Writable task resources investigated

### Filesystem

- [ ] Privileged writable files investigated
- [ ] Privileged writable directories investigated
- [ ] Program Files reviewed where relevant
- [ ] ProgramData reviewed where relevant
- [ ] ACL inheritance considered

### Registry

- [ ] Sensitive registry ACLs reviewed
- [ ] Service registry configuration reviewed
- [ ] Autorun locations considered
- [ ] Installer policy reviewed where relevant

### Privileges

- [ ] SeImpersonate reviewed
- [ ] SeAssignPrimaryToken reviewed
- [ ] SeBackup reviewed
- [ ] SeRestore reviewed
- [ ] SeTakeOwnership reviewed
- [ ] SeDebug reviewed
- [ ] SeLoadDriver reviewed

### Credentials

- [ ] Credential Manager reviewed
- [ ] PowerShell history considered
- [ ] Environment variables reviewed
- [ ] Configuration files reviewed
- [ ] Unattended files considered

### Execution

- [ ] PATH reviewed
- [ ] DLL loading considered
- [ ] Application control understood
- [ ] PowerShell language mode understood
- [ ] UAC context understood

### Applications

- [ ] Custom privileged applications reviewed
- [ ] Installed software reviewed
- [ ] Drivers reviewed
- [ ] Named pipes considered
- [ ] Autorun resources considered

### Reporting

- [ ] Candidate distinguished from confirmed finding
- [ ] Privileged consumer identified
- [ ] Evidence collected
- [ ] Impact established
- [ ] Detection opportunities considered
- [ ] Remediation provided


---

## Related Notes

- [PrivEsc Explorer](./)
- [Linux PrivEsc Explorer](../linux/)
- [Windows Overview](../../windows/)
- [Windows Enumeration](../../windows/enumeration/)
- [Windows Privilege Escalation](../../windows/privilege-escalation/)
- [Windows Services](../../windows/services/)
- [Windows Credentials](../../windows/credentials/)
- [PowerShell](../../windows/powershell/)


---

## References

- [Microsoft Windows Documentation](https://learn.microsoft.com/windows/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Access Control](https://learn.microsoft.com/windows/win32/secauthz/access-control){ target="_blank" rel="noopener noreferrer" }
- [Microsoft User Rights Assignment](https://learn.microsoft.com/windows/security/threat-protection/security-policy-settings/user-rights-assignment){ target="_blank" rel="noopener noreferrer" }
- [Microsoft AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Windows privilege escalation testing can affect services, scheduled tasks, processes, drivers, files, registry configuration, credentials, and security controls. Perform active validation only where explicitly authorised and prefer non-destructive evidence whenever possible.
