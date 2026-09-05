# Windows Privilege Escalation

Windows privilege escalation is the process of identifying security weaknesses that allow a lower-privileged user or process to gain additional permissions on a Windows system.

During an authorised assessment, the objective is not simply to obtain administrative privileges. The objective is to identify the underlying trust or permission relationship that makes the escalation possible, validate the security impact safely, and provide evidence that allows the weakness to be remediated.

Typical escalation paths involve:

- Windows services
- Weak filesystem permissions
- Weak registry permissions
- Scheduled tasks
- Service configuration permissions
- Unquoted service paths
- DLL search behaviour
- Stored credentials
- User privileges
- Application configuration
- Installer policies
- AutoRun locations
- Vulnerable software
- Credential reuse
- Security-control misconfiguration

The central question is:

```text
Can the current user influence something
that executes or operates with greater privileges?
```

---

# 1. Privilege Escalation Model

A useful model is:

```text
Low-Privileged User
        |
        v
Enumeration
        |
        v
Identify Privileged Resource
        |
        v
Identify Controllable Component
        |
        v
Validate Permissions
        |
        v
Determine Execution Context
        |
        v
Confirm Security Boundary
        |
        v
Controlled Validation
        |
        v
Evidence
        |
        v
Remediation
```

Most meaningful privilege escalation findings contain three components:

```text
Privileged Context
        +
Attacker-Controlled Resource
        +
Execution / Consumption Relationship
        =
Potential Privilege Escalation
```

For example:

```text
SYSTEM Service
      +
User-Writable Executable
      =
Potential SYSTEM Execution
```

---

# 2. Initial Enumeration

Start by understanding the current security context.

```cmd
whoami
whoami /user
whoami /groups
whoami /priv
```

Complete information:

```cmd
whoami /all
```

PowerShell:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:COMPUTERNAME
```

Check integrity level:

```cmd
whoami /groups
```

Look for:

```text
Mandatory Label\Medium Mandatory Level
Mandatory Label\High Mandatory Level
Mandatory Label\System Mandatory Level
```

For broader host enumeration, see [Windows Enumeration](enumeration.md).

---

# 3. Determine Administrative Context

PowerShell:

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

Possible output:

```text
True
```

or:

```text
False
```

Remember that local Administrators group membership does not necessarily mean the current process is elevated because User Account Control can provide a filtered token.

---

# 4. User Privileges

Enumerate privileges:

```cmd
whoami /priv
```

Privileges worth investigating include:

| Privilege | Security Relevance |
|---|---|
| SeBackupPrivilege | Can permit reading protected files through backup semantics |
| SeRestorePrivilege | Can permit restoring or replacing protected resources |
| SeTakeOwnershipPrivilege | Can permit taking ownership of securable objects |
| SeDebugPrivilege | Provides powerful access to processes |
| SeImpersonatePrivilege | Allows impersonation in appropriate authentication contexts |
| SeAssignPrimaryTokenPrivilege | Allows assignment of primary tokens in specific circumstances |
| SeLoadDriverPrivilege | Allows loading kernel drivers under applicable conditions |
| SeManageVolumePrivilege | Provides powerful volume-management capabilities |
| SeTcbPrivilege | Highly privileged operating-system capability |

A listed privilege is not automatically exploitable.

Determine:

```text
Privilege Present?
      |
      v
Enabled?
      |
      v
Relevant Resource Available?
      |
      v
Current Integrity Context?
      |
      v
Security Boundary Crossed?
```

---

# 5. Local Groups

Enumerate groups:

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

```powershell
Get-LocalGroupMember -Group "Administrators"
```

Other potentially important groups include:

```text
Backup Operators
Remote Desktop Users
Remote Management Users
Hyper-V Administrators
Event Log Readers
Performance Log Users
```

Membership should be interpreted according to the capabilities granted on the particular host.

---

# 6. Operating System Information

```cmd
systeminfo
```

PowerShell:

```powershell
Get-ComputerInfo
```

Focused:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
```

CIM:

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture
```

Version information helps determine whether known vulnerabilities or configuration behaviours may be relevant.

Do not infer vulnerability solely from an operating-system build number.

---

# 7. Services

Windows services are one of the most important privilege escalation areas.

Enumerate services:

```powershell
Get-CimInstance Win32_Service
```

Useful fields:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, State, StartMode, StartName, PathName
```

Running services:

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq "Running" |
    Select-Object Name, StartName, PathName
```

Services running as LocalSystem:

```powershell
Get-CimInstance Win32_Service |
    Where-Object StartName -eq "LocalSystem" |
    Select-Object Name, State, StartMode, PathName
```

Other privileged identities may include:

```text
NT AUTHORITY\SYSTEM
LocalSystem
NetworkService
LocalService
Privileged domain service accounts
```

A service running as SYSTEM is normal.

The important question is whether a lower-privileged user can influence something used by that service.

See [Windows Services](services.md).

---

# 8. Service Executable Permissions

Suppose a service uses:

```text
C:\Program Files\Vendor\Service\service.exe
```

Inspect the executable:

```cmd
icacls "C:\Program Files\Vendor\Service\service.exe"
```

PowerShell:

```powershell
Get-Acl "C:\Program Files\Vendor\Service\service.exe" | Format-List Owner, AccessToString
```

Inspect the parent directory:

```cmd
icacls "C:\Program Files\Vendor\Service"
```

PowerShell:

```powershell
Get-Acl "C:\Program Files\Vendor\Service" | Format-List Owner, AccessToString
```

Potentially dangerous permissions for broad principals include:

```text
Write
Modify
FullControl
```

Potentially broad principals include:

```text
Everyone
BUILTIN\Users
Authenticated Users
Domain Users
```

The combination matters:

```text
Service runs as SYSTEM
        +
Standard user can modify service executable
        =
Potential privilege escalation
```

---

# 9. Writable Service Directories

Sometimes the executable itself is protected while its parent directory is writable.

Check:

```cmd
icacls "C:\Program Files\Vendor\Service"
```

or:

```powershell
(Get-Acl "C:\Program Files\Vendor\Service").Access
```

A controlled write test can validate permissions:

```powershell
$folder = "C:\ProgramData\CandidateFolder"
$file = Join-Path $folder "write-test-$PID.tmp"

try {
    New-Item -ItemType File -Path $file -ErrorAction Stop | Out-Null
    Write-Host "[+] Write succeeded: $file"
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}
catch {
    Write-Host "[-] Write failed: $($_.Exception.Message)"
}
```

This proves only that the user can write to the directory.

It does not prove privilege escalation.

---

# 10. Correlating Writable Directories with Services

If a writable directory is identified, determine whether a service references it.

Example:

```powershell
$folder = "C:\ProgramData\CandidateFolder"

Get-CimInstance Win32_Service |
    Where-Object PathName -Match ([regex]::Escape($folder)) |
    Select-Object Name, StartName, State, PathName
```

This is significantly stronger than simply reporting a writable folder.

Assessment logic:

```text
Writable Folder
      |
      v
Used by Service?
      |
      +--> No --> Record only if otherwise relevant
      |
      +--> Yes
             |
             v
       Service Privileged?
             |
             +--> No --> Lower priority
             |
             +--> Yes
                    |
                    v
             Controllable Resource?
                    |
                    v
               Validate Impact
```

---

# 11. Service Configuration

Inspect a service:

```cmd
sc qc ServiceName
```

Example:

```cmd
sc qc Spooler
```

PowerShell:

```powershell
Get-CimInstance Win32_Service -Filter "Name='Spooler'"
```

Important properties include:

```text
BINARY_PATH_NAME
SERVICE_START_NAME
START_TYPE
DEPENDENCIES
```

CIM equivalents:

```text
PathName
StartName
StartMode
```

---

# 12. Service Security Descriptors

Query the service security descriptor:

```cmd
sc sdshow ServiceName
```

Example:

```cmd
sc sdshow Spooler
```

The output uses Security Descriptor Definition Language.

Security-sensitive service rights can include the ability to:

```text
Change service configuration
Start service
Stop service
Delete service
Modify service permissions
```

A lower-privileged user with service configuration rights may be able to alter how a privileged service operates.

Validate the exact access granted before reporting.

---

# 13. AccessChk for Services

Microsoft Sysinternals AccessChk can simplify permission analysis.

[AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }

AccessChk can inspect:

```text
Services
Files
Directories
Registry keys
Processes
Named pipes
```

Always interpret AccessChk output in the context of the current user and the actual resource.

---

# 14. Unquoted Service Paths

A service path containing spaces may require further review if the executable path is not quoted.

Example:

```text
C:\Program Files\Vendor Application\Service.exe
```

The important conditions are not simply:

```text
Path contains spaces
```

A meaningful issue generally requires:

```text
Unquoted service path
        +
Path parsing ambiguity
        +
Attacker-writable candidate location
        +
Privileged service
        =
Potential privilege escalation
```

Enumerate service paths:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -and
        $_.PathName -notmatch '^"' -and
        $_.PathName -match '\s'
    } |
    Select-Object Name, StartName, PathName
```

This is a candidate-generation technique only.

Each result requires manual validation.

---

# 15. Scheduled Tasks

Enumerate scheduled tasks:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Useful summary:

```powershell
Get-ScheduledTask | ForEach-Object {
    [PSCustomObject]@{
        TaskName = $_.TaskName
        TaskPath = $_.TaskPath
        User = $_.Principal.UserId
        RunLevel = $_.Principal.RunLevel
        Actions = ($_.Actions | ForEach-Object {
            "$($_.Execute) $($_.Arguments)"
        }) -join "; "
    }
}
```

Look for tasks that:

```text
Run as SYSTEM / Administrator
        +
Execute modifiable file
        =
Potential privilege escalation
```

---

# 16. Scheduled Task File Permissions

Suppose a task executes:

```text
C:\ProgramData\Vendor\maintenance.ps1
```

Inspect:

```cmd
icacls "C:\ProgramData\Vendor\maintenance.ps1"
```

PowerShell:

```powershell
Get-Acl "C:\ProgramData\Vendor\maintenance.ps1" | Format-List Owner, AccessToString
```

Also inspect the directory:

```cmd
icacls "C:\ProgramData\Vendor"
```

Do not modify production scripts simply to demonstrate the issue.

Permission evidence combined with task configuration may already provide sufficient proof.

---

# 17. Startup Applications

Enumerate startup commands:

```powershell
Get-CimInstance Win32_StartupCommand |
    Select-Object Name, Command, Location, User
```

Registry locations include:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

PowerShell:

```powershell
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

```powershell
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

A startup entry becomes security-relevant when a lower-privileged user can influence content that executes in a higher-privileged context.

---

# 18. Registry Permissions

Inspect a registry key:

```powershell
Get-Acl "HKLM:\SOFTWARE\Vendor"
```

Access entries:

```powershell
(Get-Acl "HKLM:\SOFTWARE\Vendor").Access
```

Look for broad write access such as:

```text
SetValue
CreateSubKey
WriteKey
FullControl
```

Again, the permission alone is not enough.

Determine whether the registry value influences:

```text
Privileged service
Privileged application
Startup mechanism
Security configuration
Executable path
DLL path
```

---

# 19. Autoruns

Microsoft Sysinternals Autoruns provides broad visibility into automatic execution locations.

[Autoruns](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns){ target="_blank" rel="noopener noreferrer" }

It can enumerate areas such as:

```text
Logon entries
Services
Drivers
Scheduled tasks
Explorer extensions
AppInit entries
Winlogon entries
Known DLLs
Boot execution
```

During privilege escalation analysis, investigate whether privileged automatic execution references lower-privileged writable resources.

---

# 20. Installed Applications

Enumerate installed applications through the registry.

64-bit applications:

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation
```

32-bit applications:

```powershell
Get-ItemProperty HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation
```

Investigate:

```text
Unsupported applications
Old management software
Backup agents
Deployment clients
Custom enterprise applications
Privileged helper services
```

Do not associate a version with a CVE without verifying the affected version range and applicable configuration.

---

# 21. Application Directory Permissions

Custom software is often installed outside the standard protected directories.

Common locations include:

```text
C:\ProgramData
C:\Vendor
C:\Apps
C:\Tools
C:\Company
```

Inspect:

```cmd
icacls "C:\ProgramData\Vendor"
```

PowerShell:

```powershell
Get-Acl "C:\ProgramData\Vendor" | Format-List Owner, AccessToString
```

If writable, determine what uses the directory.

Search services:

```powershell
$folder = "C:\ProgramData\Vendor"

Get-CimInstance Win32_Service |
    Where-Object PathName -Match ([regex]::Escape($folder)) |
    Select-Object Name, StartName, PathName
```

Search scheduled tasks manually or through their actions.

The directory's consumers determine the actual impact.

---

# 22. DLL Search Behaviour

Applications may load DLLs from multiple locations.

Privilege escalation risk can arise when:

```text
Privileged Process
       |
       v
Attempts DLL Load
       |
       v
Searches Attacker-Writable Location
       |
       v
Attacker Controls DLL Resolution
```

Do not assume that the absence of a DLL automatically means a hijack is possible.

Validate:

- Actual DLL load attempt
- Search order
- Writable location
- Process privilege
- Architecture
- Application behaviour
- Existing mitigations

Process Monitor is useful for analysing runtime file and DLL activity.

[Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon){ target="_blank" rel="noopener noreferrer" }

---

# 23. PATH Environment Variable

Inspect PATH:

```cmd
echo %PATH%
```

PowerShell:

```powershell
$env:PATH
```

Split entries:

```powershell
$env:PATH -split ';'
```

Potential security concerns arise when:

```text
Privileged application
        +
Searches PATH for executable or library
        +
PATH contains user-writable directory
        =
Potential execution-control issue
```

A writable PATH entry alone does not prove privilege escalation.

---

# 24. Environment Variables

Enumerate:

```cmd
set
```

PowerShell:

```powershell
Get-ChildItem Env:
```

Environment variables may reveal:

```text
Custom application paths
Temporary directories
Development tools
Deployment configuration
Proxy configuration
Runtime paths
```

These can provide clues to applications and resources worth investigating.

---

# 25. Stored Credentials

List Windows Credential Manager entries:

```cmd
cmdkey /list
```

This can reveal credential targets.

The presence of a credential entry does not necessarily mean the underlying credential can be extracted or reused.

Assess:

```text
Target
Type
Current user
Associated service/application
Potential reuse context
```

See [Windows Credentials](credentials.md).

---

# 26. PowerShell History

History location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Read:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

History may reveal:

```text
Administrative commands
Network shares
Deployment commands
Application configuration
Operational paths
Authentication-related commands
```

Handle any discovered secrets as sensitive assessment evidence.

---

# 27. Configuration Files

Applications may store sensitive configuration in:

```text
*.config
*.ini
*.xml
*.json
*.yml
*.yaml
*.conf
```

Search should be scoped to relevant application directories.

Example:

```powershell
Get-ChildItem "C:\ProgramData\Vendor" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Extension -Match '\.(config|ini|xml|json|yml|yaml|conf)$'
```

Inspect configuration for:

```text
Service accounts
Connection strings
API endpoints
Database configuration
Network shares
Credential references
Certificate locations
```

Avoid unnecessarily collecting sensitive content.

---

# 28. User Profiles

Enumerate:

```powershell
Get-ChildItem C:\Users
```

Profiles:

```powershell
Get-CimInstance Win32_UserProfile |
    Select-Object LocalPath, Loaded, Special
```

Interesting areas may include:

```text
Documents
Desktop
Downloads
AppData
PowerShell history
SSH configuration
Cloud CLI configuration
Development configuration
Application configuration
```

Only access data permitted by the assessment scope and current account permissions.

---

# 29. AlwaysInstallElevated

Windows Installer policies should be reviewed carefully.

Relevant registry values are traditionally associated with:

```text
HKCU\Software\Policies\Microsoft\Windows\Installer
HKLM\Software\Policies\Microsoft\Windows\Installer
```

Inspect:

```powershell
Get-ItemProperty "HKCU:\Software\Policies\Microsoft\Windows\Installer" -ErrorAction SilentlyContinue
```

```powershell
Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\Installer" -ErrorAction SilentlyContinue
```

Focused query:

```powershell
Get-ItemPropertyValue "HKCU:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```

```powershell
Get-ItemPropertyValue "HKLM:\Software\Policies\Microsoft\Windows\Installer" -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```

A meaningful AlwaysInstallElevated condition historically requires the relevant policy to be enabled in both user and machine context.

Do not change the policy during routine testing.

---

# 30. UAC

User Account Control influences administrative token behaviour.

Basic information about the current token can be gathered through:

```cmd
whoami /groups
```

and:

```cmd
whoami /priv
```

Relevant registry configuration exists under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -ErrorAction SilentlyContinue
```

Important values can include:

```text
EnableLUA
ConsentPromptBehaviorAdmin
ConsentPromptBehaviorUser
PromptOnSecureDesktop
FilterAdministratorToken
```

UAC configuration should be interpreted in the context of administrative membership and endpoint security requirements.

---

# 31. Application Control

Application control can significantly affect privilege escalation opportunities.

Relevant technologies include:

```text
AppLocker
Windows Defender Application Control
Microsoft Defender
Attack Surface Reduction
PowerShell Constrained Language Mode
```

AppLocker effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

Collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType, EnforcementMode
```

PowerShell Language Mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Defender:

```powershell
Get-MpComputerStatus -ErrorAction SilentlyContinue
```

Application-control testing should focus on effective policy rather than the mere existence of individual Windows utilities.

---

# 32. AppLocker Allowed Paths

Path-based rules require particular attention.

Retrieve effective rules:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections | ForEach-Object {
    $_.Rules
}
```

The important relationship is:

```text
AppLocker Allows Directory
          +
Standard User Can Write There
          =
Potential Application-Control Weakness
```

For example, an allowed `%WINDIR%\*` path does not automatically create a weakness because standard users normally cannot modify most protected Windows directories.

The correct next question is:

```text
Can the assessed user write to any location covered by the allow rule?
```

---

# 33. Test Effective AppLocker Decisions

Test a file:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "C:\Path\file.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

Detailed output:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "C:\Path\file.exe" -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath, PolicyDecision, MatchingRule
```

This is preferable to assuming that a file is allowed because its parent directory appears in a rule.

---

# 34. PowerShell Language Mode

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible modes:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

`FullLanguage` is normal on many Windows systems.

It should not be reported as a vulnerability by itself.

In hardened environments, determine whether the expected design requires Constrained Language Mode through application control.

---

# 35. Security Products

Microsoft Defender:

```powershell
Get-MpComputerStatus -ErrorAction SilentlyContinue
```

Preferences:

```powershell
Get-MpPreference -ErrorAction SilentlyContinue
```

Running services:

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq "Running" |
    Select-Object Name, DisplayName, StartName
```

Do not disable or tamper with endpoint security during ordinary privilege escalation enumeration.

The goal is to understand the defensive environment.

---

# 36. Network Services

Listening ports:

```cmd
netstat -ano | findstr LISTENING
```

PowerShell:

```powershell
Get-NetTCPConnection -State Listen
```

Map to processes:

```powershell
Get-NetTCPConnection -State Listen | ForEach-Object {
    [PSCustomObject]@{
        Address = $_.LocalAddress
        Port = $_.LocalPort
        PID = $_.OwningProcess
        Process = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName
    }
}
```

Local-only administrative applications may expose functionality that becomes security-relevant when accessible from a lower-privileged context.

---

# 37. Named Pipes

Enumerate:

```powershell
Get-ChildItem \\.\pipe\
```

Named pipes can expose inter-process communication used by:

```text
Services
Databases
Browsers
Management software
Security software
Custom applications
```

A named pipe is not inherently vulnerable.

Further analysis requires understanding its permissions and protocol behaviour.

---

# 38. Network Shares

```cmd
net share
```

PowerShell:

```powershell
Get-SmbShare
```

Permissions:

```powershell
Get-SmbShareAccess -Name "ShareName"
```

Local shares may expose:

```text
Scripts
Backups
Deployment packages
Configuration files
Application data
```

Evaluate both share permissions and NTFS permissions.

---

# 39. Process Enumeration

```cmd
tasklist /v
```

PowerShell:

```powershell
Get-Process
```

Command lines:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId, Name, CommandLine
```

Processes may reveal:

```text
Privileged applications
Management agents
Backup software
Database services
Deployment agents
Custom applications
```

Correlate interesting processes with:

```text
Executable path
Service
User context
Filesystem permissions
Network listeners
Configuration
```

---

# 40. Process Ownership

CIM can help correlate processes and services, but access to owner information may depend on permissions.

For service-backed processes, start with:

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq "Running" |
    Select-Object Name, ProcessId, StartName, PathName
```

This provides:

```text
Service
PID
Service account
Executable path
```

which can then be correlated with filesystem permissions.

---

# 41. Hotfix and Patch Analysis

Enumerate:

```powershell
Get-HotFix
```

or:

```powershell
Get-CimInstance Win32_QuickFixEngineering
```

Patch analysis should not rely solely on the absence of a particular KB.

Modern Windows servicing uses cumulative updates, supersedence, and servicing-stack behaviour that can make simple KB checks misleading.

Validate:

```text
Windows version
Build
Revision
Installed updates
Affected product
Vulnerability prerequisites
```

before reporting a missing patch.

---

# 42. Automated Privilege Escalation Enumeration

Automated enumeration can improve coverage.

Useful tools include:

```text
WinPEAS
PrivescCheck
SharpUp
Seatbelt
AccessChk
Autoruns
Process Monitor
```

Automated results are candidate findings, not final findings.

Every meaningful result should be manually validated.

---

# 43. WinPEAS

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

WinPEAS can identify:

```text
System information
Users
Privileges
Services
Scheduled tasks
Applications
Credentials
Interesting files
Registry settings
Permissions
Security controls
```

Its output can be extensive.

Use it to identify areas for manual validation rather than treating every highlighted result as a vulnerability.

---

# 44. PrivescCheck

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

PrivescCheck provides PowerShell-based checks for common Windows privilege escalation conditions.

Potential areas include:

```text
Services
Scheduled tasks
Registry
Credentials
Applications
Permissions
Security configuration
```

Manual verification remains necessary.

---

# 45. SharpUp

[SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }

SharpUp focuses on identifying Windows privilege escalation opportunities.

Use tool findings as leads for deeper inspection.

---

# 46. Seatbelt

[Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

Seatbelt performs broad Windows host reconnaissance and can help identify:

```text
Security controls
Users
Processes
Services
Interesting configuration
Credentials
System information
```

It is particularly useful when privilege escalation analysis requires broader environmental context.

---

# 47. AccessChk

[AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }

AccessChk is useful for identifying permissions on:

```text
Files
Directories
Services
Registry keys
Processes
Named pipes
```

Permission output should always be correlated with resource usage.

---

# 48. Process Monitor

[Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon){ target="_blank" rel="noopener noreferrer" }

Process Monitor can help investigate:

```text
Filesystem access
Registry access
Process activity
DLL loading
Configuration access
Missing files
```

It is particularly useful when determining what resources a privileged application actually consumes.

---

# 49. Autoruns

[Autoruns](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns){ target="_blank" rel="noopener noreferrer" }

Autoruns can help identify privileged automatic execution paths that reference modifiable resources.

This is often more useful than manually checking a small number of startup registry keys.

---

# 50. Manual Validation

Automated tools may report:

```text
Writable directory
Unquoted service path
Interesting privilege
Weak registry ACL
Scheduled task
Stored credential
```

The next step should always be manual validation.

Example:

```text
Tool reports writable service directory
             |
             v
Identify service
             |
             v
Determine service account
             |
             v
Inspect exact ACL
             |
             v
Confirm current user has write access
             |
             v
Determine what service consumes
             |
             v
Establish practical impact
```

---

# 51. Safe Validation

Privilege escalation testing can alter privileged resources.

Where possible, demonstrate the condition without modifying production executables or configurations.

Preferred evidence can include:

```text
ACL showing write permission
        +
Service configuration showing privileged execution
        +
Current user identity
        +
Controlled write test using temporary file
        =
Strong evidence
```

A destructive or persistent payload is usually unnecessary.

---

# 52. Controlled Write Test

For a candidate directory:

```powershell
$folder = "C:\ProgramData\CandidateFolder"
$file = Join-Path $folder "write-test-$PID-$(Get-Random).tmp"

try {
    New-Item -ItemType File -Path $file -ErrorAction Stop | Out-Null
    Write-Host "[+] Write access confirmed: $file"
}
catch {
    Write-Host "[-] Write access denied: $($_.Exception.Message)"
}
finally {
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}
```

This demonstrates write capability without replacing an application file.

---

# 53. Permission Analysis

When a candidate resource is discovered, document:

```text
Owner
ACL
Inherited permissions
Current user's effective group membership
Resource type
Privileged consumer
```

PowerShell:

```powershell
Get-Acl "C:\Path" | Format-List Owner, AccessToString
```

Detailed:

```powershell
(Get-Acl "C:\Path").Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited
```

Command Prompt:

```cmd
icacls "C:\Path"
```

---

# 54. Important Permission Relationships

Common relationships worth investigating include:

| Privileged Resource | Controllable Component |
|---|---|
| SYSTEM service | Executable |
| SYSTEM service | Executable directory |
| SYSTEM service | Configuration file |
| SYSTEM service | Registry key |
| Elevated scheduled task | Script |
| Elevated scheduled task | Executable |
| Privileged application | DLL search directory |
| Startup mechanism | Referenced executable |
| Deployment agent | Package or script directory |

The presence of the relationship is more important than either component individually.

---

# 55. Common False Positives

## Writable directory without privileged consumer

```text
User can write to:
C:\ProgramData\Example
```

but nothing privileged uses the directory.

Result:

```text
Not sufficient for privilege escalation.
```

---

## SYSTEM service with protected executable

```text
Service runs as SYSTEM.
```

but:

```text
Executable protected
Directory protected
Configuration protected
Service configuration protected
```

Result:

```text
Normal privileged service configuration.
```

---

## Unquoted service path without writable location

```text
C:\Program Files\Vendor App\Service.exe
```

but the current user cannot write to any relevant candidate location.

Result:

```text
No demonstrated privilege escalation path.
```

---

## FullLanguage PowerShell

```text
LanguageMode = FullLanguage
```

Result:

```text
Not inherently a vulnerability.
```

Evaluate against the intended hardening model.

---

## Allowed Windows utility

```text
rundll32.exe = Allowed
```

Result:

```text
Not inherently a vulnerability.
```

The practical security impact depends on what content can be executed, application-control objectives, writable paths, and other controls.

---

# 56. Evidence Collection

For a privilege escalation finding, capture:

```text
Host
Current user
SID
Groups
Privileges
Integrity level
Affected resource
Resource owner
Resource permissions
Privileged consumer
Consumer identity
Configuration
Controlled validation
Security impact
```

Example:

```text
Host:
WS01

Current user:
CORP\standarduser

Integrity:
Medium

Affected directory:
C:\ProgramData\Vendor\Service

Permission:
BUILTIN\Users - Modify

Service:
VendorService

Service account:
LocalSystem

Service executable:
C:\ProgramData\Vendor\Service\service.exe

Validation:
The current standard user successfully created and removed a temporary
file in the service directory.

Impact:
A lower-privileged user can modify resources within the directory used by
a LocalSystem service. The exact executable and service behaviour should
be validated to determine whether privileged code execution is possible.
```

---

# 57. Severity Assessment

Severity depends on practical impact.

A useful model:

```text
Exploitability
     +
Privileges Gained
     +
User Interaction
     +
Reliability
     +
Scope
     =
Severity
```

Examples:

| Condition | Typical Importance |
|---|---|
| Writable unused directory | Informational / no finding |
| Writable privileged application config | Potentially significant |
| Writable SYSTEM service executable | High impact |
| Weak task file permissions with SYSTEM execution | High impact |
| Stored privileged credential | Potentially critical depending on reuse |
| Broad AppLocker rule without writable allowed location | Usually not sufficient alone |

Use the organisation's agreed severity methodology for final ratings.

---

# 58. Remediation Principles

Privilege escalation remediation usually focuses on removing the trust relationship.

Common approaches include:

```text
Restrict filesystem permissions
Restrict registry permissions
Protect service configuration
Protect scheduled task resources
Remove unnecessary local privileges
Remove unnecessary local administrators
Secure application directories
Quote service paths
Protect secrets
Patch vulnerable software
Harden application control
Monitor privileged execution
```

Remediation should target the root cause rather than only the demonstrated technique.

---

# 59. Service Remediation

For vulnerable services:

```text
Protect executable
Protect executable directory
Protect configuration
Restrict service permissions
Use least-privileged service account where practical
Quote executable paths
Remove unnecessary user write access
```

A typical secure relationship is:

```text
SYSTEM Service
      |
      v
Executable
      |
      v
Administrators / SYSTEM Modify
      |
      v
Standard Users Read and Execute Only
```

---

# 60. Scheduled Task Remediation

For privileged tasks:

```text
Protect task definition
Protect executable
Protect script
Protect parent directory
Review task principal
Use least privilege
Remove obsolete tasks
```

Privileged scheduled tasks should not execute content writable by ordinary users.

---

# 61. Credential Remediation

If credentials are exposed:

```text
Remove plaintext secrets
Rotate affected credentials
Use managed identities where possible
Use Windows Credential Manager appropriately
Use gMSA for applicable domain services
Restrict configuration-file permissions
Avoid credentials in command lines
Review credential reuse
```

For Active Directory service accounts, see [gMSA](../active-directory/gmsa.md).

---

# 62. Application Control Remediation

Where application control is part of the security design:

```text
Review AppLocker / WDAC policy
Review broad path rules
Identify user-writable allowed locations
Restrict script execution where appropriate
Apply PowerShell controls
Enable relevant logging
Review ASR configuration
```

Application control should be designed as a complete policy rather than as isolated executable blocks.

---

# 63. Privilege Escalation Checklist

## Current Context

- [ ] Current user
- [ ] SID
- [ ] Groups
- [ ] Privileges
- [ ] Integrity level
- [ ] Administrative membership
- [ ] Elevation state

## System

- [ ] Windows version
- [ ] Build
- [ ] Architecture
- [ ] Hotfixes
- [ ] Domain membership

## Services

- [ ] Enumerate services
- [ ] Identify privileged services
- [ ] Inspect service paths
- [ ] Inspect executable permissions
- [ ] Inspect directory permissions
- [ ] Inspect configuration permissions
- [ ] Inspect service permissions
- [ ] Review unquoted paths
- [ ] Validate writable resources

## Scheduled Tasks

- [ ] Enumerate tasks
- [ ] Identify privileged tasks
- [ ] Inspect actions
- [ ] Inspect scripts
- [ ] Inspect executables
- [ ] Inspect directories
- [ ] Validate permissions

## Applications

- [ ] Enumerate installed software
- [ ] Identify custom applications
- [ ] Review application directories
- [ ] Review privileged helper services
- [ ] Review configuration files
- [ ] Review DLL loading where relevant
- [ ] Validate versions

## Registry

- [ ] Startup locations
- [ ] Service configuration
- [ ] Application configuration
- [ ] Weak registry ACLs
- [ ] Installer policies

## Credentials

- [ ] Credential Manager
- [ ] PowerShell history
- [ ] Configuration files
- [ ] Scripts
- [ ] Deployment files
- [ ] User profiles

## Security Controls

- [ ] Defender
- [ ] ASR
- [ ] AppLocker
- [ ] WDAC indicators
- [ ] PowerShell Language Mode
- [ ] PowerShell logging
- [ ] Firewall

## Validation

- [ ] Confirm current user's effective access
- [ ] Identify privileged consumer
- [ ] Confirm execution relationship
- [ ] Avoid destructive modification
- [ ] Collect evidence
- [ ] Determine practical impact
- [ ] Recommend root-cause remediation

---

# 64. Quick Manual Workflow

```cmd
whoami /all
systeminfo
net localgroup Administrators
tasklist /v
schtasks /query /fo LIST /v
cmdkey /list
netstat -ano
net share
```

PowerShell:

```powershell
Get-CimInstance Win32_Service | Select-Object Name, State, StartMode, StartName, PathName
Get-ScheduledTask
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User
Get-LocalGroupMember -Group "Administrators"
Get-PSDrive -PSProvider FileSystem
Get-NetTCPConnection -State Listen
Get-MpComputerStatus -ErrorAction SilentlyContinue
Get-AppLockerPolicy -Effective -ErrorAction SilentlyContinue
$ExecutionContext.SessionState.LanguageMode
```

Then focus on the relationships identified by the initial enumeration.

---

# 65. Privilege Escalation Decision Tree

```text
Current User
     |
     v
Privileged Already?
     |
     +--> Yes --> Confirm actual integrity/elevation
     |
     +--> No
           |
           v
     Interesting Privileges?
           |
           +--> Yes --> Validate practical capability
           |
           v
        Services
           |
           +--> Privileged?
           |
           +--> Modifiable executable/config/path?
           |
           v
     Scheduled Tasks
           |
           +--> Privileged?
           |
           +--> Modifiable action?
           |
           v
       Applications
           |
           +--> Privileged helper?
           |
           +--> Writable resources?
           |
           v
        Registry
           |
           +--> Privileged configuration?
           |
           +--> Writable?
           |
           v
       Credentials
           |
           +--> Exposed?
           |
           +--> Reusable?
           |
           v
    Application Control
           |
           +--> Relevant weakness?
           |
           v
        Validate
           |
           v
         Report
```

---

# 66. Testing Model

The strongest privilege escalation findings follow this model:

```text
1. Identify current security context

2. Identify a more privileged process or execution mechanism

3. Identify a resource consumed by that mechanism

4. Confirm the lower-privileged user controls the resource

5. Confirm the relationship crosses a security boundary

6. Validate safely

7. Collect reproducible evidence

8. Recommend removal of the underlying trust relationship
```

Avoid:

```text
Observation
    |
    v
Immediate vulnerability conclusion
```

Prefer:

```text
Observation
    |
    v
Correlation
    |
    v
Permission validation
    |
    v
Execution-context validation
    |
    v
Practical impact
    |
    v
Finding
```

---

# 67. Reporting Example

## Title

```text
Standard Users Can Modify Resources Used by a LocalSystem Service
```

## Description

```text
A Windows service running as LocalSystem references resources stored in a
directory where standard users have Modify permissions.

This permission relationship allows a lower-privileged user to influence
content consumed by a privileged service and may result in privilege
escalation depending on the affected resource and service behaviour.
```

## Evidence

```text
Current user:
CORP\standarduser

Service:
VendorService

Service account:
LocalSystem

Service path:
C:\ProgramData\Vendor\Service\service.exe

Directory permissions:
BUILTIN\Users:(M)

Controlled write test:
Successful
```

## Impact

```text
A standard user may be able to influence execution performed by a service
running with LocalSystem privileges, potentially resulting in elevation of
privileges.
```

## Recommendation

```text
Remove unnecessary write and modify permissions for standard users from
directories and files consumed by privileged services.

Restrict modification rights to trusted administrative and service
identities, and review similar application directories for equivalent
permission relationships.
```

---

# 68. Related Notes

- [Windows](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Services](services.md)
- [Windows Credentials](credentials.md)
- [PowerShell](powershell.md)
- [Active Directory](../active-directory/index.md)
- [Active Directory Privilege Escalation](../active-directory/privilege-escalation.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [Microsoft Windows Security](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Windows application control](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/){ target="_blank" rel="noopener noreferrer" }
- [AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }
- [AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }
- [Autoruns](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns){ target="_blank" rel="noopener noreferrer" }
- [Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon){ target="_blank" rel="noopener noreferrer" }
- [Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }
- [SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }
- [PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on systems you own or have explicit permission to assess.
