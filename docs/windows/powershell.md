# PowerShell

PowerShell is one of the most important administrative, automation, investigation, and security assessment interfaces available on Windows.

During an authorised security assessment, PowerShell can be used to inspect:

- System information
- Users and groups
- Processes
- Services
- Network configuration
- Filesystem permissions
- Registry configuration
- Scheduled tasks
- Event logs
- Microsoft Defender
- Attack Surface Reduction rules
- AppLocker
- PowerShell security controls
- Credential exposure
- Active Directory environments

PowerShell should not be viewed only as an execution mechanism. It is also an extremely capable native interface for understanding Windows security configuration.

---

# 1. PowerShell Assessment Flow

A useful PowerShell assessment workflow is:

```text
PowerShell
    |
    v
Version / Edition
    |
    v
Current Security Context
    |
    +---- User
    +---- Groups
    +---- Privileges
    +---- Integrity
    |
    v
PowerShell Security Context
    |
    +---- Language Mode
    +---- Execution Policy
    +---- Logging
    +---- AMSI context
    |
    v
Windows Security Controls
    |
    +---- Defender
    +---- ASR
    +---- AppLocker
    +---- WDAC
    |
    v
Host Enumeration
    |
    +---- System
    +---- Network
    +---- Processes
    +---- Services
    +---- Registry
    +---- Filesystem
    |
    v
Validate Findings
    |
    v
Evidence
    |
    v
Reporting
```

The objective is to determine the effective security configuration rather than drawing conclusions from individual settings.

---

# 2. PowerShell Version

Display PowerShell information:

```powershell
$PSVersionTable
```

Important properties can include:

```text
PSVersion
PSEdition
GitCommitId
OS
Platform
PSCompatibleVersions
WSManStackVersion
SerializationVersion
```

Focused output:

```powershell
$PSVersionTable.PSVersion
```

Edition:

```powershell
$PSVersionTable.PSEdition
```

PowerShell environments may include:

```text
Windows PowerShell 5.1
PowerShell 7+
```

PowerShell 7 is a separate modern product based on .NET, while Windows PowerShell 5.1 remains integrated into many supported Windows environments.

Do not assume that the presence of one version means another version is unavailable.

---

# 3. PowerShell Executables

Windows PowerShell is commonly located at:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

The `v1.0` directory name is historical and does not mean the installed PowerShell version is version 1.

PowerShell 7 commonly uses:

```text
C:\Program Files\PowerShell\7\pwsh.exe
```

Locate PowerShell:

```powershell
Get-Command powershell.exe
```

PowerShell 7:

```powershell
Get-Command pwsh.exe -ErrorAction SilentlyContinue
```

Executable path of the current process:

```powershell
(Get-Process -Id $PID).Path
```

---

# 4. Current User

Determine the current identity:

```powershell
whoami
```

Environment variables:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:COMPUTERNAME
```

Windows identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent()
```

Name only:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

SID:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
```

---

# 5. Groups

Command-line enumeration:

```powershell
whoami /groups
```

Windows identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Groups
```

Local groups:

```powershell
Get-LocalGroup
```

Administrators:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

Group membership should be interpreted together with the current token and integrity level.

---

# 6. Determine Whether the Process Is Administrative

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

Possible results:

```text
True
False
```

This is useful for distinguishing an administrative process from a standard-user process.

Local Administrators group membership alone does not necessarily mean the current process is elevated because User Account Control can provide filtered tokens.

---

# 7. Windows Privileges

```powershell
whoami /priv
```

Privileges worth understanding include:

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

A privilege being present does not automatically mean it can be used to cross a security boundary.

See [Windows Privilege Escalation](privilege-escalation.md).

---

# 8. Environment Variables

Enumerate all environment variables:

```powershell
Get-ChildItem Env:
```

Useful individual variables:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:COMPUTERNAME
$env:USERPROFILE
$env:APPDATA
$env:LOCALAPPDATA
$env:TEMP
$env:TMP
$env:PATH
$env:PSModulePath
```

PATH entries:

```powershell
$env:PATH -split ';'
```

Environment variables can reveal:

- Application paths
- Proxy configuration
- Development environments
- Temporary directories
- Management tooling
- Custom enterprise configuration

Treat secrets discovered in environment variables as sensitive evidence.

---

# 9. PowerShell Language Mode

Determine the current Language Mode:

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

## FullLanguage

`FullLanguage` provides access to the complete PowerShell language subject to the permissions of the current process and other security controls.

Example:

```text
FullLanguage
```

This is normal on many Windows systems.

It should not automatically be reported as a vulnerability.

## ConstrainedLanguage

`ConstrainedLanguage` restricts various PowerShell language capabilities.

Example:

```text
ConstrainedLanguage
```

Constrained Language Mode is particularly relevant when it is applied as part of a broader application-control architecture.

The assessment question should therefore be:

```text
What PowerShell restrictions are expected?
        |
        v
What application-control policy exists?
        |
        v
What Language Mode is effective?
        |
        v
Does observed behaviour match the security design?
```

---

# 10. Language Mode and Application Control

Language Mode should not be evaluated in isolation.

Consider:

```text
PowerShell Language Mode
        |
        +---- AppLocker
        |
        +---- WDAC
        |
        +---- Endpoint security
        |
        +---- User privileges
        |
        +---- Script policy
        |
        +---- Logging
```

For hardened endpoints, organisations may use application control to restrict scripting environments and executable content.

A finding should explain the intended control objective and the demonstrated security impact.

---

# 11. Execution Policy

Display the effective execution policy:

```powershell
Get-ExecutionPolicy
```

All scopes:

```powershell
Get-ExecutionPolicy -List
```

Possible policies include:

```text
Restricted
AllSigned
RemoteSigned
Unrestricted
Bypass
Undefined
```

Execution Policy is primarily intended to help control PowerShell script execution behaviour.

It should not be treated as a strong standalone security boundary.

For example:

```text
ExecutionPolicy = RemoteSigned
```

does not by itself establish a vulnerability.

---

# 12. PowerShell Profiles

PowerShell profiles can execute commands when PowerShell sessions start.

Display profile information:

```powershell
$PROFILE
```

All profile paths:

```powershell
$PROFILE | Format-List *
```

Common profile scopes include:

```text
CurrentUserCurrentHost
CurrentUserAllHosts
AllUsersCurrentHost
AllUsersAllHosts
```

Check whether the current profile exists:

```powershell
Test-Path $PROFILE
```

Display it:

```powershell
Get-Content $PROFILE -ErrorAction SilentlyContinue
```

Profile security depends heavily on permissions and execution context.

The important relationship is:

```text
Profile executes automatically
        +
Higher-privileged user/process uses profile
        +
Lower-privileged user can modify profile
        =
Potential security issue
```

Do not treat the existence of a profile as a vulnerability.

---

# 13. PowerShell Modules

List available modules:

```powershell
Get-Module -ListAvailable
```

Currently imported modules:

```powershell
Get-Module
```

Module paths:

```powershell
$env:PSModulePath -split ';'
```

Module information:

```powershell
Get-Module -ListAvailable |
    Select-Object Name, Version, ModuleBase
```

Modules can provide information about:

- Administrative tooling
- Cloud tooling
- Security software
- Enterprise management
- Active Directory management
- Custom applications

---

# 14. Commands

List commands:

```powershell
Get-Command
```

Search by name:

```powershell
Get-Command *Firewall*
```

Search for AppLocker commands:

```powershell
Get-Command *AppLocker*
```

Defender commands:

```powershell
Get-Command *Mp*
```

Determine where a command originates:

```powershell
Get-Command Get-MpComputerStatus | Format-List *
```

---

# 15. Command History

Session history:

```powershell
Get-History
```

Aliases:

```powershell
h
```

PSReadLine persistent history location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Read persistent history:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

Common location:

```text
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

History may reveal:

```text
Administrative operations
Application configuration
Network shares
Remote systems
Deployment commands
Authentication operations
```

Any discovered credentials or tokens should be treated as sensitive evidence.

---

# 16. Clear Distinction Between History Types

PowerShell has different history concepts.

`Get-History` normally displays history associated with the current session:

```powershell
Get-History
```

PSReadLine can persist command history to disk:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Therefore:

```text
Get-History
```

and:

```text
ConsoleHost_history.txt
```

should not be assumed to contain identical data.

---

# 17. System Information

PowerShell provides several ways to obtain system information.

```powershell
Get-ComputerInfo
```

Focused:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
```

CIM:

```powershell
Get-CimInstance Win32_OperatingSystem
```

Computer information:

```powershell
Get-CimInstance Win32_ComputerSystem
```

Useful focused output:

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name, Domain, PartOfDomain, Manufacturer, Model
```

---

# 18. Domain Membership

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name, Domain, PartOfDomain
```

Additional context:

```powershell
$env:USERDOMAIN
$env:LOGONSERVER
```

If the host is domain joined, continue with [Active Directory Enumeration](../active-directory/enumeration.md).

---

# 19. Local Users

```powershell
Get-LocalUser
```

Focused:

```powershell
Get-LocalUser |
    Select-Object Name, Enabled, LastLogon, PasswordRequired
```

Specific account:

```powershell
Get-LocalUser -Name "Administrator"
```

---

# 20. Local Groups

```powershell
Get-LocalGroup
```

Administrators:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

Remote Desktop users:

```powershell
Get-LocalGroupMember -Group "Remote Desktop Users" -ErrorAction SilentlyContinue
```

Remote Management users:

```powershell
Get-LocalGroupMember -Group "Remote Management Users" -ErrorAction SilentlyContinue
```

---

# 21. Processes

Enumerate:

```powershell
Get-Process
```

Focused:

```powershell
Get-Process |
    Select-Object Id, ProcessName, Path
```

A process path may not be accessible from every security context.

CIM command-line information:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId, Name, ExecutablePath, CommandLine
```

Search:

```powershell
Get-CimInstance Win32_Process |
    Where-Object Name -Like "*java*" |
    Select-Object ProcessId, Name, CommandLine
```

Process command lines can expose sensitive information. Handle output carefully.

---

# 22. Services

```powershell
Get-Service
```

CIM provides additional information:

```powershell
Get-CimInstance Win32_Service
```

Useful output:

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

LocalSystem services:

```powershell
Get-CimInstance Win32_Service |
    Where-Object StartName -eq "LocalSystem" |
    Select-Object Name, State, PathName
```

Continue with [Windows Services](services.md).

---

# 23. Service Path Correlation

Suppose a writable directory is identified:

```text
C:\ProgramData\CandidateFolder
```

Determine whether services reference it:

```powershell
$folder = "C:\ProgramData\CandidateFolder"

Get-CimInstance Win32_Service |
    Where-Object PathName -Match ([regex]::Escape($folder)) |
    Select-Object Name, StartName, State, PathName
```

This helps establish whether a writable location has a privileged consumer.

---

# 24. Network Configuration

```powershell
Get-NetIPConfiguration
```

Adapters:

```powershell
Get-NetAdapter
```

Addresses:

```powershell
Get-NetIPAddress
```

IPv4:

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

Routes:

```powershell
Get-NetRoute
```

IPv4 routes:

```powershell
Get-NetRoute -AddressFamily IPv4
```

DNS:

```powershell
Get-DnsClientServerAddress
```

DNS cache:

```powershell
Get-DnsClientCache
```

---

# 25. TCP Connections

All TCP connections:

```powershell
Get-NetTCPConnection
```

Listening:

```powershell
Get-NetTCPConnection -State Listen
```

Established:

```powershell
Get-NetTCPConnection -State Established
```

Useful fields:

```powershell
Get-NetTCPConnection |
    Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess
```

Map listeners to processes:

```powershell
Get-NetTCPConnection -State Listen | ForEach-Object {
    [PSCustomObject]@{
        LocalAddress = $_.LocalAddress
        LocalPort = $_.LocalPort
        PID = $_.OwningProcess
        Process = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName
    }
}
```

---

# 26. Test Network Connectivity

PowerShell provides `Test-NetConnection` for connectivity diagnostics.

Test a host:

```powershell
Test-NetConnection example.com
```

Test a TCP port:

```powershell
Test-NetConnection example.com -Port 443
```

Focused result:

```powershell
Test-NetConnection example.com -Port 443 |
    Select-Object ComputerName, RemoteAddress, RemotePort, TcpTestSucceeded
```

This is useful for validating whether a particular TCP destination is reachable.

---

# 27. DNS Resolution

```powershell
Resolve-DnsName example.com
```

Specific type:

```powershell
Resolve-DnsName example.com -Type A
```

Nameserver records:

```powershell
Resolve-DnsName example.com -Type NS
```

Use only domains and infrastructure within the authorised assessment scope.

---

# 28. Web Requests

PowerShell can make HTTP and HTTPS requests.

```powershell
Invoke-WebRequest -Uri "https://example.com"
```

Store the response:

```powershell
$response = Invoke-WebRequest -Uri "https://example.com"
$response.StatusCode
```

Headers:

```powershell
$response.Headers
```

PowerShell 7 also provides modern web-request behaviour through the same cmdlet family.

Web requests should only target systems permitted by the assessment scope.

---

# 29. Files

List files:

```powershell
Get-ChildItem
```

Recursive:

```powershell
Get-ChildItem -Recurse
```

Files only:

```powershell
Get-ChildItem -File
```

Directories only:

```powershell
Get-ChildItem -Directory
```

Hidden items:

```powershell
Get-ChildItem -Force
```

Avoid unnecessarily recursive enumeration of entire drives.

Target directories relevant to the assessment.

---

# 30. File Content

Read:

```powershell
Get-Content "C:\Path\file.txt"
```

First ten lines:

```powershell
Get-Content "C:\Path\file.txt" -TotalCount 10
```

Search:

```powershell
Select-String -Path "C:\Path\file.txt" -Pattern "example"
```

Recursive targeted search:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern "example" -ErrorAction SilentlyContinue
```

Be careful when searching potentially sensitive data.

---

# 31. File Metadata

```powershell
Get-Item "C:\Path\file.exe"
```

Useful properties:

```powershell
Get-Item "C:\Path\file.exe" |
    Select-Object Name, FullName, Length, CreationTime, LastWriteTime
```

File version:

```powershell
(Get-Item "C:\Path\file.exe").VersionInfo
```

Focused:

```powershell
(Get-Item "C:\Path\file.exe").VersionInfo |
    Select-Object FileVersion, ProductVersion, CompanyName, ProductName
```

---

# 32. File Hashes

Calculate a SHA-256 hash:

```powershell
Get-FileHash "C:\Path\file.exe" -Algorithm SHA256
```

Other supported algorithms can be specified where required.

Hashes are useful for:

- Evidence
- File comparison
- Integrity verification
- Malware triage
- Application-control analysis

---

# 33. Digital Signatures

PowerShell can inspect Authenticode signatures:

```powershell
Get-AuthenticodeSignature "C:\Path\file.exe"
```

Focused:

```powershell
Get-AuthenticodeSignature "C:\Path\file.exe" |
    Select-Object Status, StatusMessage, SignerCertificate
```

Signature status can help during application and binary assessment.

A valid signature does not automatically mean software is safe.

---

# 34. Filesystem Permissions

```powershell
Get-Acl "C:\Path"
```

Useful output:

```powershell
Get-Acl "C:\Path" |
    Format-List Owner, AccessToString
```

Detailed ACL:

```powershell
(Get-Acl "C:\Path").Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited
```

Potentially important broad principals include:

```text
Everyone
BUILTIN\Users
Authenticated Users
Domain Users
```

Potentially important rights include:

```text
Write
Modify
FullControl
```

A permission must be correlated with the resource's security relevance.

---

# 35. Controlled Write Test

A non-destructive temporary-file test can confirm whether the current user can write to a candidate directory.

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

This validates only write access.

It does not establish privilege escalation.

---

# 36. Registry

PowerShell exposes the Registry through providers.

Registry drives:

```powershell
Get-PSDrive -PSProvider Registry
```

Common locations:

```text
HKLM:\SOFTWARE
HKLM:\SYSTEM
HKCU:\Software
```

List:

```powershell
Get-ChildItem HKLM:\SOFTWARE
```

Read values:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"
```

Specific value:

```powershell
Get-ItemPropertyValue "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion" -Name "ProgramFilesDir"
```

---

# 37. Registry Permissions

```powershell
Get-Acl "HKLM:\SOFTWARE\Vendor"
```

Access:

```powershell
(Get-Acl "HKLM:\SOFTWARE\Vendor").Access
```

Registry permissions become especially important when a key controls:

```text
Service configuration
Startup behaviour
Privileged application settings
Executable paths
Security configuration
```

---

# 38. Scheduled Tasks

Enumerate:

```powershell
Get-ScheduledTask
```

Basic:

```powershell
Get-ScheduledTask |
    Select-Object TaskPath, TaskName, State
```

Useful security-oriented summary:

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

Investigate privileged tasks that reference user-modifiable resources.

---

# 39. Startup Configuration

CIM:

```powershell
Get-CimInstance Win32_StartupCommand |
    Select-Object Name, Command, Location, User
```

Current-user Run key:

```powershell
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

Machine Run key:

```powershell
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

Automatic execution is not inherently vulnerable.

Determine who controls the referenced resources and under which context they execute.

---

# 40. Installed Software

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

Current user:

```powershell
Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation
```

Avoid using `Win32_Product` as a routine software-enumeration method because querying it can have undesirable Windows Installer side effects on some systems.

---

# 41. Hotfixes

```powershell
Get-HotFix
```

Alternative:

```powershell
Get-CimInstance Win32_QuickFixEngineering
```

Patch analysis should consider cumulative updates and supersedence.

Do not treat a missing KB identifier as definitive evidence of vulnerability without verifying the actual Windows build and applicable security update.

---

# 42. Microsoft Defender Status

Where Defender cmdlets are available:

```powershell
Get-MpComputerStatus
```

Focused:

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusEnabled, AntispywareEnabled, RealTimeProtectionEnabled, BehaviorMonitorEnabled, IoavProtectionEnabled
```

Additional information:

```powershell
Get-MpComputerStatus |
    Select-Object AMServiceEnabled, AMProductVersion, AMEngineVersion, AntivirusSignatureVersion, AntivirusSignatureLastUpdated
```

Defender status should be documented rather than altered during normal enumeration.

---

# 43. Defender Preferences

```powershell
Get-MpPreference
```

Potentially relevant areas include:

```text
Exclusions
Cloud protection
Attack Surface Reduction
Controlled Folder Access
Network protection
Scan configuration
```

The exact settings available depend on Windows version and Defender configuration.

---

# 44. Defender Exclusions

Where permissions allow:

```powershell
Get-MpPreference |
    Select-Object ExclusionPath, ExclusionProcess, ExclusionExtension
```

Exclusions may be legitimate.

Potential security significance depends on:

```text
Scope of exclusion
        |
        v
Who can write there?
        |
        v
What executes there?
        |
        v
What protection is removed?
```

Do not modify exclusions during routine assessment.

---

# 45. Attack Surface Reduction Rules

Retrieve ASR configuration:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids, AttackSurfaceReductionRules_Actions
```

Display pairs:

```powershell
$p = Get-MpPreference

for ($i = 0; $i -lt $p.AttackSurfaceReductionRules_Ids.Count; $i++) {
    [PSCustomObject]@{
        RuleId = $p.AttackSurfaceReductionRules_Ids[$i]
        Action = $p.AttackSurfaceReductionRules_Actions[$i]
    }
}
```

Interpret action values according to Microsoft documentation and the management configuration used by the organisation.

ASR should be evaluated as part of the complete endpoint-security architecture.

---

# 46. Windows Firewall

Profiles:

```powershell
Get-NetFirewallProfile
```

Enabled rules:

```powershell
Get-NetFirewallRule -Enabled True
```

Allow rules:

```powershell
Get-NetFirewallRule -Enabled True -Action Allow
```

Block rules:

```powershell
Get-NetFirewallRule -Enabled True -Action Block
```

Useful summary:

```powershell
Get-NetFirewallProfile |
    Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
```

Firewall configuration should be correlated with actual listeners and network reachability.

---

# 47. AppLocker

Retrieve effective AppLocker policy:

```powershell
Get-AppLockerPolicy -Effective
```

Rule collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections
```

Summary:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType, EnforcementMode
```

Potential collections include:

```text
Exe
Msi
Script
Dll
Appx
```

Not every environment configures every collection.

---

# 48. Inspect AppLocker Rules

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    ForEach-Object {
        $_.Rules
    }
```

Rules can be based on:

```text
Path
Publisher
Hash
```

The existence of an allow rule does not automatically mean it creates a weakness.

For path rules, determine whether the current user can write into an allowed path.

---

# 49. Test AppLocker Policy

Test a particular file:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "C:\Path\test.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

Detailed output:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "C:\Path\test.exe" -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath, PolicyDecision, MatchingRule
```

Testing should use the exact:

```text
User
Path
File type
Effective policy
```

that applies to the assessment scenario.

---

# 50. AppLocker and Writable Paths

A useful assessment relationship is:

```text
AppLocker Allow Rule
        |
        v
Allowed Directory
        |
        v
Can Standard User Write?
        |
        +--> No
        |     |
        |     v
        |  Likely expected protection
        |
        +--> Yes
              |
              v
       What content is allowed?
              |
              v
       Can security boundary be crossed?
```

A broad allow rule should not automatically be labelled a bypass.

Validate the effective permissions and execution behaviour.

---

# 51. WDAC

Windows Defender Application Control uses Code Integrity policies to control trusted code.

Assessment questions include:

```text
Are policies deployed?
Are they enforced or audited?
Which trust mechanisms are used?
Which binaries or scripts are permitted?
Are supplemental policies present?
What do Code Integrity events show?
```

Do not conclude that WDAC is absent merely because one PowerShell query or WMI/CIM class is unavailable.

Different Windows versions and deployment methods can expose configuration differently.

---

# 52. Code Integrity Logs

List relevant logs:

```powershell
Get-WinEvent -ListLog *CodeIntegrity* -ErrorAction SilentlyContinue
```

Common operational log:

```text
Microsoft-Windows-CodeIntegrity/Operational
```

Recent events:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 50 -ErrorAction SilentlyContinue
```

Focused:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated, Id, LevelDisplayName, Message
```

These events can provide evidence of application-control enforcement.

---

# 53. AppLocker Logs

List AppLocker logs:

```powershell
Get-WinEvent -ListLog *AppLocker* -ErrorAction SilentlyContinue
```

Relevant channels may include:

```text
Microsoft-Windows-AppLocker/EXE and DLL
Microsoft-Windows-AppLocker/MSI and Script
Microsoft-Windows-AppLocker/Packaged app-Deployment
Microsoft-Windows-AppLocker/Packaged app-Execution
```

Example:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-AppLocker/EXE and DLL" -MaxEvents 50 -ErrorAction SilentlyContinue
```

---

# 54. AMSI

The Antimalware Scan Interface provides an integration point between applications and antimalware products.

AMSI is used by multiple Windows scripting and application environments.

For security assessment purposes, AMSI should be considered alongside:

```text
Microsoft Defender
Third-party endpoint protection
PowerShell
Script hosts
Application control
Logging
```

Avoid reducing AMSI assessment to:

```text
Command executed = AMSI disabled
```

or:

```text
Command blocked = AMSI enabled
```

Observed execution can be affected by several different controls.

---

# 55. PowerShell Logging

PowerShell can provide multiple logging mechanisms.

Important examples include:

```text
Script Block Logging
Module Logging
Transcription
PowerShell Operational logging
```

Relevant policy path:

```text
HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell
```

Inspect:

```powershell
Get-ChildItem "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell" -Recurse -ErrorAction SilentlyContinue
```

Current-user policy:

```powershell
Get-ChildItem "HKCU:\SOFTWARE\Policies\Microsoft\Windows\PowerShell" -Recurse -ErrorAction SilentlyContinue
```

---

# 56. Script Block Logging

A commonly relevant policy path is:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -ErrorAction SilentlyContinue
```

Relevant configuration can include:

```text
EnableScriptBlockLogging
```

Logging behaviour should be verified through effective configuration and event telemetry rather than relying only on a registry value.

---

# 57. Module Logging

Relevant policy path:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -ErrorAction SilentlyContinue
```

Module Logging can provide visibility into PowerShell module and command activity depending on configuration.

---

# 58. PowerShell Transcription

Relevant policy path:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue
```

Potential configuration can include:

```text
EnableTranscripting
EnableInvocationHeader
OutputDirectory
```

Transcripts may contain sensitive administrative information and should themselves be protected.

---

# 59. PowerShell Operational Event Log

Inspect recent PowerShell events:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 50 -ErrorAction SilentlyContinue
```

Focused:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated, Id, LevelDisplayName, Message
```

The amount of information available depends on logging configuration.

---

# 60. Event Log Discovery

List logs:

```powershell
Get-WinEvent -ListLog *
```

Search:

```powershell
Get-WinEvent -ListLog *PowerShell*
```

AppLocker:

```powershell
Get-WinEvent -ListLog *AppLocker*
```

Code Integrity:

```powershell
Get-WinEvent -ListLog *CodeIntegrity*
```

Defender:

```powershell
Get-WinEvent -ListLog *Defender*
```

---

# 61. Microsoft Defender Event Log

A commonly relevant channel is:

```text
Microsoft-Windows-Windows Defender/Operational
```

Inspect:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-Windows Defender/Operational" -MaxEvents 50 -ErrorAction SilentlyContinue
```

This can provide useful context about:

```text
Detections
Configuration
Protection events
Operational changes
```

Access depends on the current security context.

---

# 62. Security Event Log

Recent events:

```powershell
Get-WinEvent -LogName Security -MaxEvents 20
```

Specific event ID:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id = 4624
} -MaxEvents 20
```

Security log access may require elevated privileges depending on the environment.

Event logs can be useful for validating detection coverage during authorised purple team or security-control assessments.

---

# 63. System Event Log

```powershell
Get-WinEvent -LogName System -MaxEvents 50
```

Filter:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    Id = 7045
} -MaxEvents 20 -ErrorAction SilentlyContinue
```

Event interpretation should consider Windows version, provider, and environment.

---

# 64. Exporting Structured Results

PowerShell objects can be exported to CSV:

```powershell
Get-Process |
    Select-Object Id, ProcessName |
    Export-Csv "processes.csv" -NoTypeInformation
```

JSON:

```powershell
Get-Process |
    Select-Object Id, ProcessName |
    ConvertTo-Json
```

Save JSON:

```powershell
Get-Process |
    Select-Object Id, ProcessName |
    ConvertTo-Json |
    Set-Content "processes.json"
```

Structured output is useful for evidence collection and later analysis.

Do not export sensitive data to insecure locations.

---

# 65. Formatting Output

Table:

```powershell
Get-Service | Format-Table
```

List:

```powershell
Get-Service | Format-List
```

Select fields:

```powershell
Get-Service |
    Select-Object Name, Status, StartType
```

Sort:

```powershell
Get-Process |
    Sort-Object CPU -Descending
```

Filter:

```powershell
Get-Service |
    Where-Object Status -eq "Running"
```

Good filtering makes assessment output easier to interpret and report.

---

# 66. Searching Objects

Use `Where-Object`:

```powershell
Get-Service |
    Where-Object Name -Like "*Defender*"
```

Processes:

```powershell
Get-Process |
    Where-Object ProcessName -Like "*sql*"
```

Services using a particular path:

```powershell
Get-CimInstance Win32_Service |
    Where-Object PathName -Like "*ProgramData*"
```

---

# 67. Select-String

Search a file:

```powershell
Select-String -Path "C:\Path\file.txt" -Pattern "example"
```

Multiple patterns:

```powershell
Select-String -Path "C:\Path\file.txt" -Pattern "user","server","database"
```

Recursive targeted search:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern "password|secret|token" -ErrorAction SilentlyContinue
```

Use sensitive searches only where authorised and necessary.

---

# 68. CIM

CIM provides structured access to Windows management information.

Operating system:

```powershell
Get-CimInstance Win32_OperatingSystem
```

Computer:

```powershell
Get-CimInstance Win32_ComputerSystem
```

Processes:

```powershell
Get-CimInstance Win32_Process
```

Services:

```powershell
Get-CimInstance Win32_Service
```

Logical disks:

```powershell
Get-CimInstance Win32_LogicalDisk
```

Network adapters:

```powershell
Get-CimInstance Win32_NetworkAdapterConfiguration |
    Where-Object IPEnabled
```

CIM is generally preferable to older WMI cmdlets for modern PowerShell administration.

---

# 69. SMB

Server configuration:

```powershell
Get-SmbServerConfiguration
```

Client configuration:

```powershell
Get-SmbClientConfiguration
```

Shares:

```powershell
Get-SmbShare
```

Share permissions:

```powershell
Get-SmbShareAccess -Name "ShareName"
```

SMB configuration can be relevant to both local Windows security and Active Directory assessments.

See [SMB](../active-directory/smb.md).

---

# 70. WinRM

Service:

```powershell
Get-Service WinRM
```

WSMan configuration:

```powershell
Get-ChildItem WSMan:\localhost
```

Listeners:

```powershell
Get-ChildItem WSMan:\localhost\Listener -ErrorAction SilentlyContinue
```

WinRM is a legitimate administrative interface.

The security assessment should consider:

```text
Network exposure
Authentication
Authorised users
Firewall configuration
Transport configuration
Endpoint configuration
```

See [WinRM](../active-directory/winrm.md).

---

# 71. Remote Desktop

RDP service:

```powershell
Get-Service TermService
```

Check for a listener:

```powershell
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

Remote Desktop users:

```powershell
Get-LocalGroupMember -Group "Remote Desktop Users" -ErrorAction SilentlyContinue
```

RDP exposure should be evaluated together with authentication, firewall, network reachability, and access controls.

---

# 72. PowerShell Remoting

PowerShell remoting commonly uses WinRM.

Inspect WSMan:

```powershell
Get-ChildItem WSMan:\localhost
```

Session configurations:

```powershell
Get-PSSessionConfiguration -ErrorAction SilentlyContinue
```

Remote management capabilities should be evaluated as administrative functionality rather than automatically classified as weaknesses.

---

# 73. Constrained Endpoints

PowerShell can expose restricted remoting endpoints.

List session configurations:

```powershell
Get-PSSessionConfiguration
```

Restricted endpoints can be used to limit available commands and capabilities.

During assessment, review:

```text
Who can connect?
What commands are available?
What security context is used?
What language capabilities are available?
What resources can be accessed?
```

---

# 74. Active Directory PowerShell Module

Where the Active Directory module is installed:

```powershell
Get-Module -ListAvailable ActiveDirectory
```

Import:

```powershell
Import-Module ActiveDirectory
```

The module provides commands such as:

```text
Get-ADUser
Get-ADGroup
Get-ADComputer
Get-ADDomain
Get-ADForest
```

Detailed Active Directory enumeration belongs in the [Active Directory](../active-directory/index.md) section.

---

# 75. PowerShell and Credential Exposure

PowerShell itself does not automatically expose credentials, but administrative usage can leave sensitive information in:

```text
History
Scripts
Configuration
Environment variables
Transcripts
Command lines
Logs
```

Review only locations permitted by the assessment.

See [Windows Credentials](credentials.md).

---

# 76. Script Inspection

Display a script:

```powershell
Get-Content "C:\Path\script.ps1"
```

Search for potentially sensitive configuration:

```powershell
Select-String -Path "C:\Path\script.ps1" -Pattern "password|secret|token|credential"
```

Inspect metadata:

```powershell
Get-Item "C:\Path\script.ps1"
```

Permissions:

```powershell
Get-Acl "C:\Path\script.ps1" |
    Format-List Owner, AccessToString
```

A script used by a privileged process becomes particularly important when lower-privileged users can modify it.

---

# 77. Script Signatures

Check Authenticode signature:

```powershell
Get-AuthenticodeSignature "C:\Path\script.ps1"
```

Possible status values can include:

```text
Valid
NotSigned
HashMismatch
NotTrusted
UnknownError
```

Signature status should be interpreted together with the actual execution and application-control policy.

---

# 78. Execution Controls

PowerShell execution can be influenced by several independent controls.

```text
PowerShell
    |
    +---- User permissions
    |
    +---- Execution Policy
    |
    +---- Language Mode
    |
    +---- AppLocker
    |
    +---- WDAC
    |
    +---- Defender / EDR
    |
    +---- ASR
    |
    +---- AMSI
    |
    +---- Logging / monitoring
```

No single setting should automatically be treated as representing the complete PowerShell security posture.

---

# 79. What Not to Report Automatically

Avoid automatically reporting:

```text
PowerShell is installed
PowerShell can execute commands
LanguageMode is FullLanguage
ExecutionPolicy is RemoteSigned
rundll32.exe is allowed
wscript.exe exists
PowerShell history exists
AppLocker contains a broad rule
Defender has an exclusion
```

These may warrant investigation, but the security impact depends on context.

For example:

```text
FullLanguage
      |
      v
Expected on workstation?
      |
      +--> Yes --> likely normal
      |
      +--> No
            |
            v
      Hardened endpoint design?
            |
            v
      Application control expected?
            |
            v
      Demonstrated security impact?
```

---

# 80. Evidence Collection

For PowerShell-related observations, record:

```text
Host
Current user
PowerShell version
PowerShell edition
Language Mode
Execution Policy
AppLocker state
WDAC evidence
Defender state
ASR state
Relevant logging
Command
Output
Practical impact
```

Example:

```text
Host:
WS01

User:
CORP\standarduser

PowerShell:
Windows PowerShell 5.1

Language Mode:
FullLanguage

AppLocker:
Enabled for executable and script collections

Observation:
PowerShell operates in FullLanguage mode for the assessed standard user.

Assessment:
The result should be evaluated against the organisation's intended
application-control architecture. FullLanguage mode alone does not
demonstrate a security vulnerability.
```

---

# 81. Application-Control Validation Model

Use:

```text
Policy Exists
     |
     v
Effective Policy
     |
     v
Relevant Rule Collection
     |
     v
Current User
     |
     v
Exact File / Path
     |
     v
Policy Decision
     |
     v
Observed Execution
     |
     v
Security Impact
```

This is preferable to:

```text
Tool exists
     |
     v
Tool allowed
     |
     v
Vulnerability
```

---

# 82. PowerShell Security Checklist

## Environment

- [ ] Determine PowerShell version
- [ ] Determine edition
- [ ] Identify executable path
- [ ] Enumerate modules
- [ ] Review module paths
- [ ] Review environment variables

## Security Context

- [ ] Current user
- [ ] SID
- [ ] Groups
- [ ] Privileges
- [ ] Administrative context
- [ ] Integrity level

## PowerShell Controls

- [ ] Language Mode
- [ ] Execution Policy
- [ ] Profiles
- [ ] Script signatures where relevant
- [ ] PowerShell logging
- [ ] Transcription
- [ ] Module Logging
- [ ] Script Block Logging

## Endpoint Controls

- [ ] Defender
- [ ] Defender exclusions
- [ ] ASR
- [ ] AppLocker
- [ ] WDAC evidence
- [ ] Code Integrity logs
- [ ] AppLocker logs
- [ ] AMSI context

## Enumeration

- [ ] System
- [ ] Users
- [ ] Groups
- [ ] Processes
- [ ] Services
- [ ] Network
- [ ] Scheduled tasks
- [ ] Files
- [ ] Registry
- [ ] Installed software

## Credential Exposure

- [ ] Session history
- [ ] PSReadLine history
- [ ] Scripts
- [ ] Configuration
- [ ] Environment variables
- [ ] Transcripts where authorised
- [ ] Process command lines where relevant

## Validation

- [ ] Verify effective policy
- [ ] Verify current user context
- [ ] Correlate security controls
- [ ] Avoid standalone conclusions
- [ ] Validate practical impact
- [ ] Preserve evidence

---

# 83. Quick PowerShell Enumeration

A compact first pass:

```powershell
$PSVersionTable
$ExecutionContext.SessionState.LanguageMode
Get-ExecutionPolicy -List
whoami /all
Get-ComputerInfo
Get-CimInstance Win32_ComputerSystem
Get-LocalUser
Get-LocalGroup
Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection
Get-Process
Get-CimInstance Win32_Service
Get-ScheduledTask
Get-SmbShare
Get-NetFirewallProfile
Get-MpComputerStatus -ErrorAction SilentlyContinue
```

Application-control checks:

```powershell
Get-AppLockerPolicy -Effective -ErrorAction SilentlyContinue
```

PowerShell logging:

```powershell
Get-ChildItem "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell" -Recurse -ErrorAction SilentlyContinue
```

Relevant event logs:

```powershell
Get-WinEvent -ListLog *PowerShell* -ErrorAction SilentlyContinue
Get-WinEvent -ListLog *AppLocker* -ErrorAction SilentlyContinue
Get-WinEvent -ListLog *CodeIntegrity* -ErrorAction SilentlyContinue
```

---

# 84. PowerShell Assessment Decision Tree

```text
Start PowerShell
      |
      v
Version / Edition
      |
      v
Current User
      |
      +---- Groups
      +---- Privileges
      +---- Integrity
      |
      v
Language Mode
      |
      v
Execution Policy
      |
      v
Application Control
      |
      +---- AppLocker
      +---- WDAC
      |
      v
Endpoint Protection
      |
      +---- Defender
      +---- ASR
      +---- AMSI context
      |
      v
Logging
      |
      +---- Script Block
      +---- Module
      +---- Transcription
      +---- Event logs
      |
      v
Host Enumeration
      |
      +---- Services
      +---- Processes
      +---- Network
      +---- Files
      +---- Registry
      |
      v
Interesting Condition?
      |
      +---- No --> Continue enumeration
      |
      +---- Yes
              |
              v
       Validate Effective Context
              |
              v
        Demonstrate Impact
              |
              v
            Report
```

---

# 85. Reporting Example - PowerShell Hardening

## Observation

```text
PowerShell is available to the assessed standard user and operates in
FullLanguage mode.
```

## Analysis

```text
FullLanguage mode is the normal PowerShell language mode in many Windows
environments and should not be treated as a vulnerability by itself.

If the endpoint is intended to enforce a restrictive application-control
model, the effective PowerShell language mode should be evaluated together
with AppLocker or WDAC policy, script restrictions, endpoint protection,
and logging controls.
```

## Recommendation

Where a restrictive endpoint-hardening model is required:

```text
Consider enforcing appropriate application-control policies using WDAC or
AppLocker and validate whether PowerShell Constrained Language Mode forms
part of the intended design.

PowerShell logging, endpoint monitoring, least privilege, and Attack Surface
Reduction controls should be considered as complementary protections.
```

---

# 86. Reporting Example - PowerShell Logging

## Observation

```text
PowerShell Script Block Logging was not observed in the assessed policy
configuration.
```

## Validation

Before reporting, determine whether equivalent visibility is provided by:

```text
Endpoint Detection and Response
PowerShell Operational logging
Module Logging
Transcription
Centralised event collection
Other endpoint telemetry
```

## Recommendation

```text
Where PowerShell activity represents a meaningful threat scenario, enable
appropriate PowerShell logging and forward relevant telemetry to a
centralised monitoring platform.

Ensure logs are protected from unauthorised modification and that monitoring
rules are capable of identifying suspicious PowerShell activity.
```

---

# 87. Defensive Monitoring

PowerShell monitoring can combine:

```text
PowerShell Operational Events
        |
        +
Script Block Logging
        |
        +
Module Logging
        |
        +
Transcription
        |
        +
Process Creation
        |
        +
AMSI / Endpoint Telemetry
        |
        +
AppLocker / Code Integrity
        |
        v
Central Detection
```

No single telemetry source provides complete visibility.

Defenders should correlate PowerShell activity with:

- Parent processes
- User context
- Network activity
- File creation
- Registry changes
- Authentication activity
- Application-control events
- Endpoint detections

---

# 88. PowerShell in Purple Team Exercises

PowerShell is particularly useful during authorised purple team exercises because both execution and detection can be evaluated.

A simple validation model is:

```text
Authorised Test Action
        |
        v
PowerShell Execution
        |
        v
Host Telemetry
        |
        +---- Process events
        +---- PowerShell events
        +---- AMSI / EDR
        +---- Network events
        |
        v
SIEM / EDR
        |
        v
Detection
        |
        v
Analyst Investigation
        |
        v
Feedback
```

Record:

```text
Technique tested
Command or behaviour
Expected telemetry
Observed telemetry
Detection generated
Analyst response
Visibility gaps
Recommended improvement
```

---

# 89. Hardening Principles

PowerShell hardening should be layered.

Common principles include:

- Apply least privilege.
- Restrict unnecessary administrative access.
- Use application control where appropriate.
- Consider Constrained Language Mode as part of a managed application-control design.
- Configure PowerShell logging appropriate to the threat model.
- Centralise important telemetry.
- Protect PowerShell transcripts and logs.
- Monitor suspicious parent-child process relationships.
- Use endpoint protection.
- Configure ASR rules where appropriate.
- Protect privileged scripts.
- Protect module directories.
- Avoid hard-coded credentials.
- Protect administrative profiles.
- Keep PowerShell and Windows supported and maintained.

PowerShell itself should not automatically be disabled simply because it can be used by attackers. It is an important Windows administrative and defensive platform.

---

# 90. Final Testing Model

Use the following model when evaluating PowerShell security:

```text
PowerShell Available
        |
        v
Who Can Use It?
        |
        v
Which Security Context?
        |
        v
Which Language Mode?
        |
        v
Which Application-Control Policy?
        |
        v
Which Endpoint Controls?
        |
        v
Which Logging Exists?
        |
        v
What Behaviour Is Actually Allowed?
        |
        v
Can a Security Boundary Be Crossed?
        |
        v
Can Defenders Observe It?
        |
        v
Validated Finding
```

This avoids treating PowerShell capabilities as vulnerabilities without understanding the surrounding Windows security architecture.

---

# Related Notes

- [Windows](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [Windows Services](services.md)
- [Windows Credentials](credentials.md)
- [Active Directory](../active-directory/index.md)
- [Active Directory Enumeration](../active-directory/enumeration.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/){ target="_blank" rel="noopener noreferrer" }
- [About PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/overview){ target="_blank" rel="noopener noreferrer" }
- [PowerShell Security](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features){ target="_blank" rel="noopener noreferrer" }
- [About Language Modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }
- [About Execution Policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies){ target="_blank" rel="noopener noreferrer" }
- [About PowerShell Logging](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Windows Security](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Application Control for Windows](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Defender for Endpoint](https://learn.microsoft.com/en-us/defender-endpoint/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - PowerShell](https://attack.mitre.org/techniques/T1059/001/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on systems you own or have explicit permission to assess.
