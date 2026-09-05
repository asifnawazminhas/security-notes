# Windows Enumeration

Windows enumeration is the process of systematically identifying the configuration, security context, software, services, network exposure, permissions, security controls, and other characteristics of a Windows host during an authorised security assessment.

The objective is not to execute every available command. The objective is to understand the system well enough to identify meaningful security relationships and determine which areas require deeper investigation.

A useful Windows enumeration process should answer questions such as:

- Which user context am I operating under?
- Is the process elevated?
- Which groups and privileges are assigned?
- Which Windows version and architecture are running?
- Is the host joined to Active Directory?
- Which users and groups exist?
- Which processes and services are running?
- Which ports are listening?
- Which software is installed?
- Which scheduled tasks exist?
- Which directories and files are writable?
- Which security controls are active?
- Are credentials or secrets exposed?
- Can a lower-privileged user influence resources used by privileged processes?

---

# Enumeration Methodology

A structured approach reduces missed attack surface.

```text
Current Security Context
        |
        v
Operating System
        |
        v
Domain Membership
        |
        v
Users and Groups
        |
        v
Privileges
        |
        v
Network Configuration
        |
        v
Processes
        |
        v
Services
        |
        v
Installed Software
        |
        v
Scheduled Tasks
        |
        v
Filesystem and Registry
        |
        v
Security Controls
        |
        v
Credential Exposure
        |
        v
Privilege Escalation Analysis
```

Enumeration should progressively build a model of the host rather than produce disconnected command output.

---

# 1. Current User

Start by determining the current identity.

```cmd
whoami
```

Example:

```text
corp\asif
```

Display the SID:

```cmd
whoami /user
```

Display group membership:

```cmd
whoami /groups
```

Display assigned privileges:

```cmd
whoami /priv
```

Display everything:

```cmd
whoami /all
```

PowerShell alternatives:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:COMPUTERNAME
```

Windows identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent()
```

Current Windows principal:

```powershell
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($identity)
$principal
```

---

# 2. Determine Administrative Context

Do not assume that membership in the local Administrators group means the current process is elevated.

Check group membership:

```cmd
whoami /groups
```

Look for:

```text
BUILTIN\Administrators
```

PowerShell:

```powershell
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
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

Administrative membership and process elevation are related but not identical because User Account Control can result in filtered access tokens.

---

# 3. Integrity Level

The integrity level helps determine the security context of the current process.

```cmd
whoami /groups
```

Look for entries such as:

```text
Mandatory Label\Low Mandatory Level
Mandatory Label\Medium Mandatory Level
Mandatory Label\High Mandatory Level
Mandatory Label\System Mandatory Level
```

Typical interpretation:

| Integrity Level | Typical Context |
|---|---|
| Low | Restricted or sandboxed process |
| Medium | Standard interactive user |
| High | Elevated administrator |
| System | SYSTEM-level process |

Integrity level should be recorded when validating privilege escalation findings.

---

# 4. Operating System Information

Basic system information:

```cmd
systeminfo
```

Useful information includes:

```text
OS Name
OS Version
System Type
Hotfixes
Domain
Logon Server
Boot Time
```

PowerShell:

```powershell
Get-ComputerInfo
```

Focused output:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture
```

CIM:

```powershell
Get-CimInstance Win32_OperatingSystem
```

Focused CIM output:

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture
```

Simple version check:

```cmd
ver
```

---

# 5. Architecture

Command Prompt:

```cmd
echo %PROCESSOR_ARCHITECTURE%
```

PowerShell:

```powershell
$env:PROCESSOR_ARCHITECTURE
```

Check whether the operating system is 64-bit:

```powershell
[Environment]::Is64BitOperatingSystem
```

Check whether the current process is 64-bit:

```powershell
[Environment]::Is64BitProcess
```

The distinction can matter when interacting with registry redirection, filesystem redirection, and architecture-specific applications.

---

# 6. Hostname

```cmd
hostname
```

PowerShell:

```powershell
$env:COMPUTERNAME
```

Alternative:

```powershell
[System.Net.Dns]::GetHostName()
```

---

# 7. Domain Membership

Determine whether the computer is domain joined.

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Name, Domain, PartOfDomain
```

Useful environment variables:

```powershell
$env:USERDOMAIN
$env:LOGONSERVER
```

Command Prompt:

```cmd
echo %USERDOMAIN%
echo %LOGONSERVER%
```

System information:

```cmd
systeminfo | findstr /B /C:"Domain"
```

If `PartOfDomain` is `True`, continue domain-specific enumeration using the [Active Directory Enumeration](../active-directory/enumeration.md) notes.

---

# 8. Local Users

Command Prompt:

```cmd
net user
```

PowerShell:

```powershell
Get-LocalUser
```

Detailed output:

```powershell
Get-LocalUser | Format-Table Name, Enabled, LastLogon, PasswordRequired, PasswordExpires
```

Specific user:

```powershell
Get-LocalUser -Name "Administrator"
```

Useful properties include:

```text
Enabled
LastLogon
PasswordRequired
PasswordExpires
UserMayChangePassword
SID
```

Look for:

- Unexpected local accounts
- Enabled built-in Administrator accounts
- Support accounts
- Deployment accounts
- Service-related accounts
- Accounts with unusual password configuration

The presence of an account alone does not constitute a vulnerability.

---

# 9. Local Groups

Command Prompt:

```cmd
net localgroup
```

PowerShell:

```powershell
Get-LocalGroup
```

Enumerate administrators:

```cmd
net localgroup Administrators
```

PowerShell:

```powershell
Get-LocalGroupMember -Group "Administrators"
```

Other groups that may be relevant include:

```text
Remote Desktop Users
Remote Management Users
Backup Operators
Hyper-V Administrators
Event Log Readers
Performance Log Users
```

Enumerate a particular group:

```powershell
Get-LocalGroupMember -Group "Remote Desktop Users"
```

---

# 10. Windows Privileges

Enumerate privileges:

```cmd
whoami /priv
```

Privileges worth understanding include:

```text
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeCreateTokenPrivilege
SeDebugPrivilege
SeImpersonatePrivilege
SeLoadDriverPrivilege
SeManageVolumePrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeTcbPrivilege
```

Example output:

```text
Privilege Name                Description                          State
============================= ==================================== ========
SeChangeNotifyPrivilege       Bypass traverse checking             Enabled
SeImpersonatePrivilege        Impersonate a client after auth      Enabled
```

A privilege being listed does not automatically mean that exploitation is possible.

Consider:

```text
Privilege
    |
    v
Enabled or Disabled?
    |
    v
Current Account
    |
    v
Current Integrity Level
    |
    v
Relevant Service / Resource
    |
    v
Practical Security Impact
```

---

# 11. Environment Variables

Command Prompt:

```cmd
set
```

PowerShell:

```powershell
Get-ChildItem Env:
```

Useful individual values:

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

Environment variables can expose application configuration, custom paths, deployment details, and occasionally sensitive values.

Any discovered secret should be handled as sensitive assessment evidence.

---

# 12. Network Interfaces

Command Prompt:

```cmd
ipconfig
```

Detailed information:

```cmd
ipconfig /all
```

PowerShell:

```powershell
Get-NetIPConfiguration
```

Network adapters:

```powershell
Get-NetAdapter
```

IP addresses:

```powershell
Get-NetIPAddress
```

IPv4 only:

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

Look for:

- Multiple interfaces
- VPN adapters
- Management networks
- Virtual interfaces
- Internal-only networks
- DNS servers
- DHCP configuration
- Default gateways

---

# 13. Routing Table

Command Prompt:

```cmd
route print
```

PowerShell:

```powershell
Get-NetRoute
```

IPv4 routes:

```powershell
Get-NetRoute -AddressFamily IPv4
```

The routing table can reveal networks reachable from the compromised or assessed host that may not be reachable directly from the tester's original network position.

---

# 14. ARP Cache

```cmd
arp -a
```

PowerShell:

```powershell
Get-NetNeighbor
```

IPv4:

```powershell
Get-NetNeighbor -AddressFamily IPv4
```

The ARP or neighbour cache can help identify recently contacted systems on directly connected networks.

---

# 15. DNS Configuration

```cmd
ipconfig /all
```

PowerShell:

```powershell
Get-DnsClientServerAddress
```

DNS cache:

```cmd
ipconfig /displaydns
```

PowerShell:

```powershell
Get-DnsClientCache
```

DNS suffix information:

```powershell
Get-DnsClient
```

Domain environments often expose useful infrastructure relationships through DNS.

---

# 16. Proxy Configuration

WinHTTP proxy:

```cmd
netsh winhttp show proxy
```

User-level proxy configuration can also be reviewed through Windows settings and relevant registry locations where authorised.

PowerShell environment variables:

```powershell
Get-ChildItem Env: | Where-Object Name -Match 'proxy'
```

Proxy configuration can affect:

- Outbound connectivity
- Tool behaviour
- Application traffic
- Update mechanisms
- Security monitoring

---

# 17. Listening Ports

Command Prompt:

```cmd
netstat -ano
```

Listening ports only:

```cmd
netstat -ano | findstr LISTENING
```

PowerShell:

```powershell
Get-NetTCPConnection -State Listen
```

Display useful fields:

```powershell
Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess
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

This helps answer:

```text
What is listening?
        |
        v
Which process owns it?
        |
        v
Which service owns the process?
        |
        v
Which account runs the service?
        |
        v
Who can reach the port?
```

---

# 18. Active Network Connections

```cmd
netstat -ano
```

PowerShell:

```powershell
Get-NetTCPConnection
```

Established connections:

```powershell
Get-NetTCPConnection -State Established
```

Useful output:

```powershell
Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess
```

Active connections can reveal:

- Management servers
- Database servers
- Proxy infrastructure
- Internal applications
- Monitoring systems
- Domain controllers
- Backup infrastructure

---

# 19. Windows Firewall

Command Prompt:

```cmd
netsh advfirewall show allprofiles
```

PowerShell:

```powershell
Get-NetFirewallProfile
```

Enabled firewall rules:

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

Firewall rules should be interpreted together with actual listeners and network reachability.

An allow rule without a listening service may have little immediate security impact.

---

# 20. Running Processes

Command Prompt:

```cmd
tasklist
```

Verbose output:

```cmd
tasklist /v
```

PowerShell:

```powershell
Get-Process
```

Selected properties:

```powershell
Get-Process | Select-Object Id, ProcessName, Path
```

Some process paths may require elevated permissions.

Process enumeration can identify:

```text
Endpoint security software
Backup agents
Management agents
Web servers
Database software
Development tools
Remote access software
Custom applications
Administrative tools
```

Correlate processes with services and network listeners.

---

# 21. Process Command Lines

CIM can provide process command lines:

```powershell
Get-CimInstance Win32_Process | Select-Object ProcessId, Name, CommandLine
```

Search for a particular process:

```powershell
Get-CimInstance Win32_Process | Where-Object Name -Like "*java*" | Select-Object ProcessId, Name, CommandLine
```

Command lines can expose:

- Configuration file locations
- Service arguments
- Application paths
- Network endpoints
- Operational parameters

Treat credentials or tokens exposed in command lines as sensitive information.

---

# 22. Services

PowerShell:

```powershell
Get-Service
```

CIM provides more useful security information:

```powershell
Get-CimInstance Win32_Service
```

Focused output:

```powershell
Get-CimInstance Win32_Service | Select-Object Name, State, StartMode, StartName, PathName
```

Running services:

```powershell
Get-CimInstance Win32_Service | Where-Object State -eq "Running" | Select-Object Name, StartName, PathName
```

Services running as LocalSystem:

```powershell
Get-CimInstance Win32_Service | Where-Object StartName -eq "LocalSystem" | Select-Object Name, State, PathName
```

Other highly privileged contexts can include:

```text
LocalSystem
NT AUTHORITY\SYSTEM
LocalService
NetworkService
Privileged domain service accounts
```

A privileged service is not automatically vulnerable.

The key question is whether a lower-privileged user can influence:

```text
Service configuration
Executable
Executable directory
DLL
Configuration file
Script
Registry key
Other consumed resource
```

See [Windows Services](services.md).

---

# 23. Service Paths

Display service paths:

```powershell
Get-CimInstance Win32_Service | Select-Object Name, StartName, PathName
```

Filter for non-empty paths:

```powershell
Get-CimInstance Win32_Service | Where-Object PathName | Select-Object Name, StartName, PathName
```

When reviewing service paths, investigate:

- Executable permissions
- Parent directory permissions
- Service configuration permissions
- Quoting
- Arguments
- Referenced configuration files

Do not report a suspicious-looking service path without confirming the required conditions and practical impact.

---

# 24. Service Permissions

Windows service security descriptors can be queried with:

```cmd
sc sdshow ServiceName
```

Example:

```cmd
sc sdshow Spooler
```

The output uses Security Descriptor Definition Language.

For assessment purposes, determine whether untrusted principals have permissions capable of modifying the service or influencing its execution.

Potentially sensitive service rights include the ability to:

```text
Change configuration
Start service
Stop service
Delete service
Modify security
```

Use tools such as Sysinternals AccessChk where permitted for easier interpretation.

---

# 25. Installed Software

Registry-based enumeration is usually preferable to `Win32_Product`.

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

Current-user applications:

```powershell
Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation
```

Review software for:

- Unsupported applications
- Old management clients
- Backup software
- Database software
- Development tools
- Remote management utilities
- Deployment software
- Custom enterprise applications

Version information should be validated before associating software with a vulnerability.

---

# 26. Hotfixes

PowerShell:

```powershell
Get-HotFix
```

CIM:

```powershell
Get-CimInstance Win32_QuickFixEngineering
```

Basic system information also displays hotfix information:

```cmd
systeminfo
```

Patch enumeration can help prioritise investigation, but missing individual KB identifiers should not automatically be treated as proof of vulnerability because Windows servicing and cumulative updates can complicate direct KB comparisons.

---

# 27. Scheduled Tasks

Command Prompt:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Display task names and paths:

```powershell
Get-ScheduledTask | Select-Object TaskPath, TaskName, State
```

Actions:

```powershell
Get-ScheduledTask | ForEach-Object {
    [PSCustomObject]@{
        TaskName = $_.TaskName
        TaskPath = $_.TaskPath
        User = $_.Principal.UserId
        RunLevel = $_.Principal.RunLevel
        Actions = ($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join "; "
    }
}
```

Investigate tasks that:

```text
Run with elevated privileges
        +
Reference modifiable files
        =
Potential privilege boundary
```

Confirm filesystem permissions before reporting.

---

# 28. Startup Programs

CIM:

```powershell
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User
```

Common registry locations:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
```

PowerShell:

```powershell
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

```powershell
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
```

Also consider Sysinternals Autoruns for comprehensive startup analysis.

---

# 29. Filesystem Drives

PowerShell:

```powershell
Get-PSDrive -PSProvider FileSystem
```

Command Prompt:

```cmd
fsutil fsinfo drives
```

`fsutil` functionality may depend on the current privileges and Windows configuration.

CIM:

```powershell
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, DriveType, FileSystem, Size, FreeSpace
```

Additional drives may contain:

- Application data
- Backups
- Deployment files
- Configuration
- User data
- Logs
- Sensitive operational information

---

# 30. Directory Permissions

PowerShell:

```powershell
Get-Acl "C:\Path"
```

Readable format:

```powershell
(Get-Acl "C:\Path").Access
```

Example:

```powershell
Get-Acl "C:\ProgramData\Example" | Format-List Owner, AccessToString
```

Command Prompt:

```cmd
icacls "C:\ProgramData\Example"
```

Look for permissions assigned to broad principals such as:

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

The presence of write access should lead to additional analysis rather than an immediate vulnerability conclusion.

---

# 31. Writable Directory Validation

A controlled write test can confirm whether the current user can actually create files.

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

This test only validates write access.

It does **not** prove privilege escalation.

Continue by determining whether a privileged process consumes resources from the writable location.

---

# 32. Search for Writable Service Locations

Enumerate service paths first:

```powershell
Get-CimInstance Win32_Service | Select-Object Name, StartName, PathName
```

For a candidate service, inspect the executable and its parent directory:

```powershell
Get-Acl "C:\Program Files\Example"
```

or:

```cmd
icacls "C:\Program Files\Example"
```

Assessment logic:

```text
Writable directory?
      |
      v
Privileged service resource?
      |
      v
Can current user modify relevant content?
      |
      v
Does service actually consume that content?
      |
      v
Can impact be safely demonstrated?
```

---

# 33. Interesting Files

Potentially relevant file types include:

```text
*.config
*.ini
*.xml
*.json
*.yml
*.yaml
*.ps1
*.bat
*.cmd
*.vbs
*.txt
```

Search should be targeted rather than indiscriminately scanning an entire host.

Example:

```powershell
Get-ChildItem "C:\ProgramData\Example" -Recurse -File -ErrorAction SilentlyContinue
```

Search filenames within an authorised application directory:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Name -Match 'password|credential|secret|token|config'
```

Avoid unnecessarily exposing sensitive data during broad searches.

---

# 34. PowerShell History

Determine the PSReadLine history location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Read the history:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

Common history location:

```text
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Potentially interesting history entries include:

```text
Administrative commands
Deployment commands
Network paths
Authentication operations
Configuration changes
Application administration
```

Any credentials or secrets discovered should be handled carefully.

---

# 35. User Profiles

List profiles:

```powershell
Get-ChildItem C:\Users
```

Profile information:

```powershell
Get-CimInstance Win32_UserProfile | Select-Object LocalPath, Loaded, Special
```

User profiles can contain:

```text
PowerShell history
Application configuration
SSH configuration
Browser data
Scripts
Logs
Development configuration
Cloud CLI configuration
```

Access should remain within the authorised assessment scope.

---

# 36. Credential Manager

List stored credentials:

```cmd
cmdkey /list
```

This can reveal the existence and target of stored credentials.

Do not assume that listed credentials are directly recoverable.

Assess:

```text
Credential target
Credential type
Current user context
Associated application
Potential security relevance
```

See [Windows Credentials](credentials.md).

---

# 37. Registry

List registry drives:

```powershell
Get-PSDrive -PSProvider Registry
```

Common locations:

```text
HKLM:\SOFTWARE
HKLM:\SYSTEM
HKCU:\Software
```

Example:

```powershell
Get-ChildItem HKLM:\SOFTWARE
```

Specific key:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion"
```

Registry enumeration can identify:

```text
Application configuration
Startup configuration
Service configuration
Security settings
Installed software
Paths
User preferences
```

---

# 38. Registry Permissions

PowerShell:

```powershell
Get-Acl "HKLM:\SOFTWARE\Example"
```

Readable access entries:

```powershell
(Get-Acl "HKLM:\SOFTWARE\Example").Access
```

The relevant question is whether an untrusted principal can modify configuration that influences a more privileged security context.

---

# 39. PowerShell Version

```powershell
$PSVersionTable
```

Important fields include:

```text
PSVersion
PSEdition
BuildVersion
CLRVersion
WSManStackVersion
```

PowerShell version can affect available features, logging capabilities, and compatibility with assessment commands.

---

# 40. PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible values:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

`FullLanguage` should not automatically be reported as a vulnerability.

Language Mode should be assessed together with:

```text
WDAC
AppLocker
PowerShell policy
Endpoint security
User privilege level
System purpose
```

In hardened environments, Constrained Language Mode may form part of a broader application-control strategy.

---

# 41. PowerShell Execution Policy

```powershell
Get-ExecutionPolicy
```

All scopes:

```powershell
Get-ExecutionPolicy -List
```

Execution Policy is primarily a script-execution safety feature and should not be treated as a strong security boundary by itself.

Do not report `RemoteSigned`, `Unrestricted`, or another execution policy as a standalone vulnerability without relevant security context.

---

# 42. Microsoft Defender Status

Where available:

```powershell
Get-MpComputerStatus
```

Focused output:

```powershell
Get-MpComputerStatus | Select-Object AntivirusEnabled, AntispywareEnabled, RealTimeProtectionEnabled, BehaviorMonitorEnabled, IoavProtectionEnabled
```

Additional useful properties:

```powershell
Get-MpComputerStatus | Select-Object AMServiceEnabled, AntivirusEnabled, RealTimeProtectionEnabled, NISEnabled
```

Defender preferences:

```powershell
Get-MpPreference
```

During normal assessment, prefer inspection over modification of defensive controls.

---

# 43. Microsoft Defender Version Information

Where supported:

```powershell
Get-MpComputerStatus | Select-Object AMProductVersion, AMEngineVersion, AntivirusSignatureVersion, AntivirusSignatureLastUpdated
```

This can help document:

```text
Platform version
Engine version
Signature version
Signature age
```

Version information alone does not demonstrate a vulnerability.

---

# 44. Defender Exclusions

Where permissions allow:

```powershell
Get-MpPreference | Select-Object ExclusionPath, ExclusionProcess, ExclusionExtension
```

Exclusions should be assessed carefully.

An exclusion may be legitimate, but overly broad exclusions can reduce endpoint protection coverage.

Do not alter exclusions during routine enumeration.

---

# 45. Attack Surface Reduction Rules

Where Microsoft Defender cmdlets are available:

```powershell
Get-MpPreference | Select-Object AttackSurfaceReductionRules_Ids, AttackSurfaceReductionRules_Actions
```

For easier inspection:

```powershell
$p = Get-MpPreference

for ($i = 0; $i -lt $p.AttackSurfaceReductionRules_Ids.Count; $i++) {
    [PSCustomObject]@{
        RuleId = $p.AttackSurfaceReductionRules_Ids[$i]
        Action = $p.AttackSurfaceReductionRules_Actions[$i]
    }
}
```

Interpret the returned actions in the context of the Windows version and management platform being used.

ASR should be considered together with endpoint protection and application control.

---

# 46. AppLocker Effective Policy

Retrieve the effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

Rule collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections
```

Summary:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections | Select-Object CollectionType, EnforcementMode
```

Possible collection types include:

```text
Exe
Msi
Script
Dll
Appx
```

A collection being present does not necessarily mean it is effectively restricting the file being tested.

---

# 47. AppLocker File Testing

Test a specific executable:

```powershell
Get-AppLockerPolicy -Effective | Test-AppLockerPolicy -Path "$env:WINDIR\System32\wscript.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

Test a script:

```powershell
Get-AppLockerPolicy -Effective | Test-AppLockerPolicy -Path "$env:TEMP\test.ps1" -User "$env:USERDOMAIN\$env:USERNAME"
```

Detailed result:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:TEMP\test.ps1" -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath, PolicyDecision, MatchingRule
```

Possible results may include:

```text
Allowed
Denied
DeniedByDefault
```

Always evaluate the effective decision for the current user and exact path.

---

# 48. AppLocker Path Rules

Inspect effective rules:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections | ForEach-Object {
    $_.Rules
}
```

Path-based allow rules deserve particular attention.

For example, an administrator may intentionally allow:

```text
%WINDIR%\*
%PROGRAMFILES%\*
```

The presence of a broad path rule does not automatically represent a bypass.

Determine whether lower-privileged users can write into locations covered by the rule.

The important relationship is:

```text
Allowed path
      +
User-writable location
      +
Executable content
      =
Potential application-control weakness
```

All conditions should be validated.

---

# 49. Windows Defender Application Control

WDAC configuration can vary significantly by Windows release and enterprise management configuration.

Potential indicators can be inspected through Windows security and Code Integrity configuration.

Useful areas include:

```text
Code Integrity policies
Event logs
Application Control policies
Enterprise management configuration
```

Do not assume that the absence of one PowerShell class or utility means WDAC is not deployed.

Evaluate multiple sources of evidence.

---

# 50. Code Integrity Event Logs

List relevant logs:

```powershell
Get-WinEvent -ListLog *CodeIntegrity* -ErrorAction SilentlyContinue
```

A commonly relevant log is:

```text
Microsoft-Windows-CodeIntegrity/Operational
```

Inspect recent events:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 50 -ErrorAction SilentlyContinue
```

Code Integrity events can provide useful evidence regarding application-control enforcement and blocked execution.

---

# 51. AppLocker Event Logs

List AppLocker logs:

```powershell
Get-WinEvent -ListLog *AppLocker* -ErrorAction SilentlyContinue
```

Relevant channels can include:

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

Event logs can help confirm whether application-control decisions are actually being enforced.

---

# 52. AMSI Context

AMSI should be evaluated as one component of the Windows defensive architecture.

Relevant areas include:

```text
PowerShell
Microsoft Defender
Third-party endpoint security
Script hosts
Application control
Logging
```

Avoid interpreting AMSI as a binary "enabled" or "disabled" control solely from whether a particular command executes.

Observed behaviour should be correlated with endpoint-security configuration and telemetry.

---

# 53. Windows Event Logs

List logs:

```powershell
Get-WinEvent -ListLog *
```

Security log:

```powershell
Get-WinEvent -LogName Security -MaxEvents 20
```

System log:

```powershell
Get-WinEvent -LogName System -MaxEvents 20
```

PowerShell operational log:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 20 -ErrorAction SilentlyContinue
```

Relevant logging areas can include:

```text
Authentication
Process creation
PowerShell
Service creation
Scheduled tasks
Application control
Code Integrity
Endpoint security
```

Access to some event logs may require additional privileges.

---

# 54. PowerShell Logging

PowerShell logging configuration may include:

```text
Script Block Logging
Module Logging
Transcription
Operational event logging
```

Relevant registry locations can include:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell
HKCU\SOFTWARE\Policies\Microsoft\Windows\PowerShell
```

Inspect where accessible:

```powershell
Get-ChildItem "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell" -Recurse -ErrorAction SilentlyContinue
```

Do not conclude that PowerShell is unmonitored solely because one logging mechanism is absent.

Enterprise EDR products may provide additional telemetry.

---

# 55. SMB Configuration

Server SMB configuration:

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

Command Prompt:

```cmd
net share
```

Relevant security properties can include:

```text
SMB signing
Encryption
Protocol versions
Share permissions
Filesystem permissions
Guest access
```

For domain-specific SMB testing, see [SMB](../active-directory/smb.md).

---

# 56. Local Shares

```cmd
net share
```

PowerShell:

```powershell
Get-SmbShare
```

Share access:

```powershell
Get-SmbShareAccess -Name "ShareName"
```

Share permissions must be considered together with NTFS permissions.

Effective access is influenced by both layers.

---

# 57. Remote Desktop Configuration

Determine whether Remote Desktop services are present:

```powershell
Get-Service TermService
```

Listening port:

```powershell
Get-NetTCPConnection -LocalPort 3389 -ErrorAction SilentlyContinue
```

Relevant group:

```powershell
Get-LocalGroupMember -Group "Remote Desktop Users" -ErrorAction SilentlyContinue
```

RDP exposure should be assessed in the context of:

```text
Network reachability
Authentication requirements
NLA configuration
User permissions
Firewall rules
MFA or gateway controls
```

---

# 58. WinRM

Service status:

```powershell
Get-Service WinRM
```

Configuration:

```cmd
winrm get winrm/config
```

Listeners:

```cmd
winrm enumerate winrm/config/listener
```

PowerShell:

```powershell
Get-ChildItem WSMan:\localhost\Listener -ErrorAction SilentlyContinue
```

WinRM is commonly used for legitimate remote administration and is not inherently a vulnerability.

Assess access controls and network exposure.

For domain use, see [WinRM](../active-directory/winrm.md).

---

# 59. WMI and CIM

Operating system:

```powershell
Get-CimInstance Win32_OperatingSystem
```

Computer system:

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

CIM is generally preferable to older WMI cmdlets for modern PowerShell usage.

---

# 60. Named Pipes

Named pipes can expose useful information about applications and services.

PowerShell:

```powershell
Get-ChildItem \\.\pipe\
```

Named pipes may reveal:

```text
Database software
Browser components
Remote administration tools
Security software
Application IPC
```

A named pipe being present does not imply that it is exploitable.

Permissions and application behaviour must be investigated separately.

---

# 61. Current Sessions

Command Prompt:

```cmd
query user
```

Alternative:

```cmd
qwinsta
```

These commands can reveal currently logged-on interactive or remote users where permissions permit.

Session information may help identify:

- Administrative activity
- RDP usage
- Multi-user systems
- Operational context

Avoid disrupting active user sessions during testing.

---

# 62. Logged-On User

```cmd
whoami
```

Console user information may also be available through:

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object UserName
```

The current process identity and console user may differ.

This distinction can matter on servers and systems accessed through remote administration mechanisms.

---

# 63. Time and Time Zone

```cmd
time /t
date /t
```

PowerShell:

```powershell
Get-Date
```

Time zone:

```powershell
Get-TimeZone
```

Accurate host time is important when correlating:

```text
Assessment actions
Event logs
EDR telemetry
Network logs
Authentication events
Screenshots
```

Record time-zone differences during evidence collection.

---

# 64. Security Products

Microsoft Defender:

```powershell
Get-MpComputerStatus -ErrorAction SilentlyContinue
```

Running services can provide additional indicators:

```powershell
Get-CimInstance Win32_Service | Where-Object State -eq "Running" | Select-Object Name, DisplayName, StartName
```

Running processes:

```powershell
Get-Process | Select-Object ProcessName, Id
```

Do not attempt to terminate, disable, or tamper with security software unless the assessment scope explicitly authorises that activity.

---

# 65. Automated Enumeration

Automated tools can improve coverage.

Useful tools include:

```text
Seatbelt
SharpUp
PrivescCheck
WinPEAS
Sysinternals
```

## Seatbelt

[Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

Seatbelt can collect information about:

```text
Operating system
Users
Processes
Services
Security controls
Interesting files
Windows configuration
```

---

## SharpUp

[SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }

SharpUp focuses on Windows privilege escalation enumeration.

---

## PrivescCheck

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

PrivescCheck performs extensive PowerShell-based privilege escalation checks.

---

## WinPEAS

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

WinPEAS provides broad Windows enumeration.

Automated results should always be manually validated.

---

# 66. Sysinternals

Microsoft Sysinternals provides several useful assessment and troubleshooting utilities.

[Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }

Useful utilities include:

| Tool | Purpose |
|---|---|
| Autoruns | Startup and persistence enumeration |
| AccessChk | Permission analysis |
| Process Explorer | Process investigation |
| Process Monitor | Runtime filesystem, registry, and process monitoring |
| TCPView | Network connection analysis |
| Sigcheck | File signature and metadata inspection |
| Strings | String extraction |
| PsExec | Administrative remote/process execution utility |

Use tools only where authorised and appropriate to the assessment.

---

# 67. AccessChk

AccessChk can assist with permission analysis.

Examples of resources that may be reviewed include:

```text
Files
Directories
Registry keys
Services
Named pipes
Processes
```

[AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }

Automated permission output should be correlated with the actual security context and resource usage.

---

# 68. Correlating Enumeration Results

The most important part of enumeration is correlation.

Example:

```text
Service Enumeration
        |
        v
Service runs as SYSTEM
        |
        v
Executable located in custom directory
        |
        v
Directory ACL inspected
        |
        v
Standard user has Modify
        |
        v
Service consumes modifiable resource
        |
        v
Potential privilege escalation
```

Another example:

```text
Listening Port
        |
        v
Owning PID
        |
        v
Process
        |
        v
Service
        |
        v
Service Account
        |
        v
Configuration / Permissions
```

Individual observations become meaningful when relationships are established.

---

# 69. What Not to Report Automatically

Avoid automatically reporting observations such as:

```text
PowerShell FullLanguage is enabled
rundll32.exe exists
wscript.exe exists
A directory is writable
A service runs as SYSTEM
An application is installed
A firewall allow rule exists
A scheduled task runs elevated
An AppLocker path rule is broad
```

These observations may be useful starting points, but they require additional security context.

For example:

```text
Writable directory
```

becomes significantly more important when:

```text
Writable directory
        +
Privileged process
        +
Privileged process consumes modifiable resource
        =
Potential privilege escalation
```

---

# 70. Evidence Collection

For each relevant observation, record:

```text
Host
Timestamp
Current user
Integrity level
Relevant groups
Relevant privileges
Resource
Permissions
Process/service context
Security control state
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

Observation:
The user has Modify permission on C:\ProgramData\Vendor\App.

Related service:
VendorService

Service account:
LocalSystem

Service executable:
C:\ProgramData\Vendor\App\service.exe

Validation:
The service configuration references the executable located inside the
user-writable directory.

Security relevance:
A lower-privileged user can influence a resource consumed by a
higher-privileged service.
```

This is substantially stronger evidence than simply reporting that a folder is writable.

---

# 71. Enumeration Checklist

## Identity

- [ ] Current username
- [ ] SID
- [ ] Domain
- [ ] Groups
- [ ] Privileges
- [ ] Integrity level
- [ ] Administrative context

## Operating System

- [ ] Hostname
- [ ] Windows edition
- [ ] Version
- [ ] Build
- [ ] Architecture
- [ ] Hotfix information
- [ ] Boot time

## Domain

- [ ] Domain membership
- [ ] User domain
- [ ] Logon server
- [ ] Domain-specific enumeration required

## Users and Groups

- [ ] Local users
- [ ] Local groups
- [ ] Administrators
- [ ] Remote Desktop Users
- [ ] Remote Management Users
- [ ] Special operator groups

## Network

- [ ] Interfaces
- [ ] IP addresses
- [ ] DNS servers
- [ ] Routes
- [ ] ARP/neighbour cache
- [ ] Proxy configuration
- [ ] Listening ports
- [ ] Established connections
- [ ] Firewall profiles
- [ ] Firewall rules

## Processes

- [ ] Running processes
- [ ] Process paths
- [ ] Command lines
- [ ] Network listeners
- [ ] Security software
- [ ] Management agents

## Services

- [ ] Services
- [ ] Service accounts
- [ ] Service paths
- [ ] Service permissions
- [ ] Executable permissions
- [ ] Parent directory permissions
- [ ] Referenced configuration files

## Software

- [ ] Installed applications
- [ ] Versions
- [ ] Publishers
- [ ] Install locations
- [ ] Unsupported software
- [ ] Management software

## Scheduled Tasks

- [ ] Task names
- [ ] Principals
- [ ] Run levels
- [ ] Actions
- [ ] Referenced files
- [ ] File permissions

## Filesystem

- [ ] Drives
- [ ] Interesting directories
- [ ] Writable directories
- [ ] Application directories
- [ ] Configuration files
- [ ] Scripts
- [ ] Backup files

## Registry

- [ ] Startup keys
- [ ] Application configuration
- [ ] Service configuration
- [ ] Interesting permissions
- [ ] Security configuration

## Credentials

- [ ] PowerShell history
- [ ] Credential Manager entries
- [ ] Application configuration
- [ ] Scripts
- [ ] Deployment artifacts
- [ ] User profile configuration

## Security Controls

- [ ] Microsoft Defender
- [ ] Defender exclusions
- [ ] ASR
- [ ] Windows Firewall
- [ ] AppLocker
- [ ] WDAC indicators
- [ ] Code Integrity logs
- [ ] PowerShell Language Mode
- [ ] PowerShell logging
- [ ] AMSI context

## Remote Management

- [ ] SMB
- [ ] RDP
- [ ] WinRM
- [ ] WMI/CIM
- [ ] Local shares

## Validation

- [ ] Correlate findings
- [ ] Validate permissions
- [ ] Validate execution context
- [ ] Validate security boundary
- [ ] Confirm practical impact
- [ ] Collect reproducible evidence

---

# 72. Quick Enumeration Commands

A compact first-pass collection:

```cmd
whoami
whoami /all
hostname
systeminfo
ipconfig /all
route print
arp -a
netstat -ano
net user
net localgroup
net localgroup Administrators
tasklist
sc query
schtasks /query /fo LIST /v
net share
netsh advfirewall show allprofiles
cmdkey /list
```

PowerShell first pass:

```powershell
$env:COMPUTERNAME
$env:USERNAME
$env:USERDOMAIN
$ExecutionContext.SessionState.LanguageMode
$PSVersionTable
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

These commands establish an initial picture of the system.

Deeper testing should then be targeted based on the results.

---

# 73. Enumeration Decision Tree

```text
Start
 |
 +--> Who am I?
 |      |
 |      +--> Groups
 |      +--> Privileges
 |      +--> Integrity level
 |
 +--> What system is this?
 |      |
 |      +--> OS
 |      +--> Build
 |      +--> Architecture
 |      +--> Domain
 |
 +--> What is running?
 |      |
 |      +--> Processes
 |      +--> Services
 |      +--> Scheduled tasks
 |
 +--> What is exposed?
 |      |
 |      +--> Listening ports
 |      +--> Shares
 |      +--> RDP
 |      +--> WinRM
 |
 +--> What can I modify?
 |      |
 |      +--> Files
 |      +--> Directories
 |      +--> Registry
 |      +--> Service resources
 |
 +--> What credentials exist?
 |      |
 |      +--> History
 |      +--> Configuration
 |      +--> Credential Manager
 |
 +--> What security controls exist?
 |      |
 |      +--> Defender
 |      +--> ASR
 |      +--> Firewall
 |      +--> AppLocker
 |      +--> WDAC
 |      +--> PowerShell controls
 |
 +--> Can observations be correlated?
        |
        +--> Privileged process
        +--> Controllable resource
        +--> Security boundary
        |
        v
     Validate
        |
        v
      Report
```

---

# 74. Reporting Enumeration Findings

Enumeration results should be converted into evidence-based findings.

Weak finding:

```text
PowerShell is installed.
```

Better observation:

```text
PowerShell is available to standard users and operates in FullLanguage mode.
Application-control configuration should be evaluated to determine whether
this behaviour is consistent with the intended endpoint-hardening model.
```

Weak finding:

```text
C:\ProgramData\Example is writable.
```

Better finding:

```text
Standard users have Modify permission on C:\ProgramData\Example. A service
running as LocalSystem loads its executable from this directory. The
permission relationship therefore allows a lower-privileged user to
influence a resource consumed by a privileged process.
```

Weak finding:

```text
rundll32.exe is allowed.
```

Better observation:

```text
The effective application-control policy permits rundll32.exe for the tested
user context. This should be evaluated together with application-control
objectives, writable locations, permitted content, and monitoring controls
before determining whether the configuration creates a practical security
weakness.
```

---

# 75. Recommended Workflow

Use enumeration as the foundation for subsequent Windows testing.

```text
Windows Enumeration
        |
        +----------------------+
        |                      |
        v                      v
Security Controls       Services / Tasks
        |                      |
        +----------+-----------+
                   |
                   v
          Filesystem / Registry
                   |
                   v
             Credentials
                   |
                   v
        Privilege Escalation
                   |
                   v
              Validation
                   |
                   v
               Reporting
```

Continue with:

1. [PowerShell](powershell.md)
2. [Windows Services](services.md)
3. [Windows Credentials](credentials.md)
4. [Windows Privilege Escalation](privilege-escalation.md)

For domain-joined hosts:

- [Active Directory Enumeration](../active-directory/enumeration.md)
- [Active Directory](../active-directory/index.md)

---

# Related Notes

- [Windows](index.md)
- [PowerShell](powershell.md)
- [Windows Services](services.md)
- [Windows Credentials](credentials.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [Active Directory](../active-directory/index.md)
- [Active Directory Enumeration](../active-directory/enumeration.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [Microsoft Windows documentation](https://learn.microsoft.com/en-us/windows/){ target="_blank" rel="noopener noreferrer" }
- [Windows security documentation](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/){ target="_blank" rel="noopener noreferrer" }
- [AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Defender for Endpoint](https://learn.microsoft.com/en-us/defender-endpoint/){ target="_blank" rel="noopener noreferrer" }
- [AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Application Control for Windows](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/){ target="_blank" rel="noopener noreferrer" }
- [PowerShell documentation](https://learn.microsoft.com/en-us/powershell/){ target="_blank" rel="noopener noreferrer" }
- [Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }
- [SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }
- [PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on systems you own or have explicit permission to assess.
