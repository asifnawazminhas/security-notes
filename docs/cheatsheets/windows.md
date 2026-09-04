# Windows Cheatsheet

Quick-reference commands for Windows enumeration, local privilege analysis, services, processes, networking, permissions, credentials, security controls and common administrative tasks during authorised security assessments.

This cheatsheet focuses primarily on:

```text
Windows Host
    |
    v
Identity
    |
    v
System
    |
    v
Users / Groups
    |
    v
Privileges
    |
    v
Processes / Services
    |
    v
Network
    |
    v
Files / Registry
    |
    v
Scheduled Execution
    |
    v
Credentials
    |
    v
Security Controls
    |
    v
Privilege Analysis
```

!!! warning "Authorised testing only"
    Use these commands only on systems you own or are explicitly authorised to assess. Prefer read-only enumeration and minimal validation. Do not change services, registry values, scheduled tasks, security policies, ACLs, Defender settings or application-control policies merely to prove a finding unless the rules of engagement explicitly permit it.

---

# Quick Start

CMD:

```cmd
whoami
whoami /all
whoami /priv
whoami /groups
hostname
systeminfo
ipconfig /all
route print
arp -a
netstat -ano
tasklist
sc query
net user
net localgroup
```

PowerShell:

```powershell
Get-ComputerInfo
Get-LocalUser
Get-LocalGroup
Get-Process
Get-Service
Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection
Get-ScheduledTask
Get-ChildItem Env:
```

A useful first-pass workflow:

```text
whoami
   |
   v
Privileges
   |
   v
Groups
   |
   v
OS / Patches
   |
   v
Processes
   |
   v
Services
   |
   v
Network
   |
   v
Scheduled Tasks
   |
   v
Files / Registry
   |
   v
Security Controls
```

---

# Current Identity

```cmd
whoami
```

Fully qualified:

```cmd
whoami /fqdn
```

SID:

```cmd
whoami /user
```

Groups:

```cmd
whoami /groups
```

Privileges:

```cmd
whoami /priv
```

Everything:

```cmd
whoami /all
```

---

# PowerShell Identity

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

Current SID:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
```

Current identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent()
```

---

# Current User Environment

CMD:

```cmd
echo %USERNAME%
echo %USERDOMAIN%
echo %USERDNSDOMAIN%
echo %COMPUTERNAME%
```

PowerShell:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:COMPUTERNAME
```

---

# Hostname

```cmd
hostname
```

PowerShell:

```powershell
$env:COMPUTERNAME
```

---

# System Information

```cmd
systeminfo
```

PowerShell:

```powershell
Get-ComputerInfo
```

Operating system:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber,OSArchitecture
```

---

# Windows Version

```cmd
ver
```

PowerShell:

```powershell
[Environment]::OSVersion
```

Registry:

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
```

Useful fields include:

```text
ProductName
DisplayVersion
CurrentBuild
CurrentBuildNumber
UBR
InstallationType
```

---

# Architecture

CMD:

```cmd
echo %PROCESSOR_ARCHITECTURE%
```

PowerShell:

```powershell
$env:PROCESSOR_ARCHITECTURE
```

OS architecture:

```powershell
(Get-CimInstance Win32_OperatingSystem).OSArchitecture
```

---

# Installed Hotfixes

PowerShell:

```powershell
Get-HotFix
```

Sorted:

```powershell
Get-HotFix |
    Sort-Object InstalledOn -Descending
```

CIM:

```powershell
Get-CimInstance Win32_QuickFixEngineering
```

Do not conclude that a host is vulnerable based only on a missing-looking KB number.

Modern Windows servicing uses cumulative updates and supersedence.

---

# Reboot Information

Last boot:

```powershell
(Get-CimInstance Win32_OperatingSystem).LastBootUpTime
```

---

# Environment Variables

CMD:

```cmd
set
```

PowerShell:

```powershell
Get-ChildItem Env:
```

PATH:

```cmd
echo %PATH%
```

PowerShell:

```powershell
$env:PATH -split ';'
```

---

# Drives

CMD:

```cmd
fsutil fsinfo drives
```

PowerShell:

```powershell
Get-PSDrive -PSProvider FileSystem
```

Volumes:

```powershell
Get-Volume
```

Disks:

```powershell
Get-Disk
```

---

# Local Users

CMD:

```cmd
net user
```

PowerShell:

```powershell
Get-LocalUser
```

Useful view:

```powershell
Get-LocalUser |
    Select-Object Name,Enabled,LastLogon,PasswordRequired,PasswordExpires
```

Specific user:

```cmd
net user Administrator
```

PowerShell:

```powershell
Get-LocalUser -Name Administrator
```

---

# User Profiles

```cmd
dir C:\Users
```

PowerShell:

```powershell
Get-ChildItem C:\Users -Force
```

Profile information:

```powershell
Get-CimInstance Win32_UserProfile |
    Select-Object LocalPath,Loaded,Special
```

---

# Local Groups

CMD:

```cmd
net localgroup
```

PowerShell:

```powershell
Get-LocalGroup
```

---

# Local Administrators

```cmd
net localgroup Administrators
```

PowerShell:

```powershell
Get-LocalGroupMember -Group Administrators
```

On non-English Windows installations the built-in group name may be localised.

SID-based identification can be more reliable when scripting across languages.

---

# Current Groups

```cmd
whoami /groups
```

Look for security-sensitive membership such as:

```text
Administrators
Remote Desktop Users
Remote Management Users
Backup Operators
Server Operators
Print Operators
Hyper-V Administrators
```

Exact security impact depends on the system and assigned rights.

---

# Token Privileges

```cmd
whoami /priv
```

Important privileges can include:

```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeDebugPrivilege
SeLoadDriverPrivilege
SeManageVolumePrivilege
SeCreateTokenPrivilege
SeTcbPrivilege
```

A privilege being listed does not automatically mean it is enabled or practically exploitable.

Record:

```text
Privilege
State
Process Context
OS Version
Security Boundary
```

---

# Privilege Analysis

Conceptually:

```text
User Token
   |
   v
Privilege
   |
   v
Windows Security Capability
   |
   v
Can It Cross a Boundary?
```

Do not report:

```text
SeImpersonatePrivilege Present
```

alone.

Determine whether the privilege is expected for the account and whether it creates an unintended escalation path in the actual environment.

---

# UAC

Current token elevation information can be inspected through:

```cmd
whoami /groups
```

Look for:

```text
Mandatory Label\High Mandatory Level
Mandatory Label\Medium Mandatory Level
```

PowerShell:

```powershell
whoami /groups
```

---

# UAC Registry Configuration

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
```

Relevant values can include:

```text
EnableLUA
ConsentPromptBehaviorAdmin
PromptOnSecureDesktop
FilterAdministratorToken
```

Do not disable UAC during an assessment.

---

# Domain Membership

```cmd
systeminfo | findstr /B /C:"Domain"
```

PowerShell:

```powershell
(Get-CimInstance Win32_ComputerSystem).Domain
```

Domain joined:

```powershell
(Get-CimInstance Win32_ComputerSystem).PartOfDomain
```

---

# Domain Controller Discovery

```cmd
nltest /dsgetdc:%USERDNSDOMAIN%
```

List DCs:

```cmd
nltest /dclist:%USERDNSDOMAIN%
```

---

# Logon Server

```cmd
echo %LOGONSERVER%
```

PowerShell:

```powershell
$env:LOGONSERVER
```

---

# Network Configuration

```cmd
ipconfig /all
```

PowerShell:

```powershell
Get-NetIPConfiguration
```

IP addresses:

```powershell
Get-NetIPAddress
```

---

# Routes

```cmd
route print
```

PowerShell:

```powershell
Get-NetRoute
```

IPv4:

```powershell
Get-NetRoute -AddressFamily IPv4 |
    Sort-Object RouteMetric
```

---

# ARP / Neighbours

```cmd
arp -a
```

PowerShell:

```powershell
Get-NetNeighbor
```

---

# DNS Servers

```powershell
Get-DnsClientServerAddress
```

IPv4:

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
```

---

# DNS Resolution

```cmd
nslookup example.com
```

PowerShell:

```powershell
Resolve-DnsName example.com
```

---

# Listening Ports

CMD:

```cmd
netstat -ano
```

Listening:

```cmd
netstat -ano | findstr LISTENING
```

PowerShell:

```powershell
Get-NetTCPConnection -State Listen
```

UDP:

```powershell
Get-NetUDPEndpoint
```

---

# Map Port to Process

For PID 1234:

```cmd
tasklist /FI "PID eq 1234"
```

PowerShell:

```powershell
Get-Process -Id 1234
```

---

# TCP Connectivity

PowerShell:

```powershell
Test-NetConnection example.com -Port 443
```

Short result:

```powershell
Test-NetConnection example.com -Port 443 -InformationLevel Quiet
```

---

# SMB Connectivity

```powershell
Test-NetConnection server.example.local -Port 445
```

---

# WinRM Connectivity

HTTP:

```powershell
Test-NetConnection server.example.local -Port 5985
```

HTTPS:

```powershell
Test-NetConnection server.example.local -Port 5986
```

---

# RDP Connectivity

```powershell
Test-NetConnection server.example.local -Port 3389
```

---

# Proxy Configuration

WinHTTP:

```cmd
netsh winhttp show proxy
```

PowerShell:

```powershell
netsh winhttp show proxy
```

User Internet settings:

```cmd
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
```

---

# Network Shares

```cmd
net share
```

PowerShell:

```powershell
Get-SmbShare
```

This normally shows locally hosted SMB shares where access permits.

---

# Connected SMB Resources

```cmd
net use
```

PowerShell:

```powershell
Get-SmbMapping
```

---

# SMB Server Configuration

Where permitted:

```powershell
Get-SmbServerConfiguration
```

Useful properties include:

```text
EnableSMB1Protocol
EnableSMB2Protocol
RequireSecuritySignature
EnableSecuritySignature
EncryptData
```

---

# SMB Client Configuration

```powershell
Get-SmbClientConfiguration
```

---

# Windows Firewall

Profiles:

```powershell
Get-NetFirewallProfile
```

Rules:

```powershell
Get-NetFirewallRule
```

Enabled rules:

```powershell
Get-NetFirewallRule |
    Where-Object Enabled -eq 'True'
```

CMD:

```cmd
netsh advfirewall show allprofiles
```

---

# Processes

```cmd
tasklist
```

Services associated with processes:

```cmd
tasklist /svc
```

Verbose:

```cmd
tasklist /v
```

PowerShell:

```powershell
Get-Process
```

---

# Process Command Lines

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,CommandLine
```

Specific process:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId=1234" |
    Select-Object *
```

---

# Parent Processes

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,CommandLine
```

Useful for understanding:

```text
Service Processes
Scheduled Tasks
Application Launchers
Management Agents
```

---

# Services

CMD:

```cmd
sc query
```

PowerShell:

```powershell
Get-Service
```

Running:

```powershell
Get-Service |
    Where-Object Status -eq 'Running'
```

---

# Service Details

```cmd
sc qc SERVICE_NAME
```

PowerShell/CIM:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,StartMode,PathName
```

Specific service:

```powershell
Get-CimInstance Win32_Service -Filter "Name='SERVICE_NAME'"
```

---

# Service Accounts

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```

Interesting identities can include:

```text
LocalSystem
NT AUTHORITY\LocalService
NT AUTHORITY\NetworkService
Domain Service Accounts
gMSA Accounts
```

---

# Service Security Review

For each privileged service:

```text
Service
   |
   v
Service Account
   |
   v
Executable
   |
   v
Directory
   |
   v
Configuration
   |
   v
Permissions
```

Questions:

```text
Can the current user modify the service?
Can the current user modify its executable?
Can the current user modify its directory?
Can the current user modify loaded configuration?
Does the service run with higher privilege?
```

---

# Service ACL

Built-in representation:

```cmd
sc sdshow SERVICE_NAME
```

This returns SDDL.

Do not modify the service ACL merely to validate a finding.

---

# Service Executable Permissions

Get path:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,PathName
```

Then inspect the relevant file:

```powershell
Get-Acl 'C:\Path\service.exe' |
    Format-List
```

Directory:

```powershell
Get-Acl 'C:\Path' |
    Format-List
```

---

# Unquoted Service Paths

Enumerate service paths:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -match ' ' -and
        $_.PathName -notmatch '^"'
    } |
    Select-Object Name,StartName,State,PathName
```

This produces candidates, not confirmed vulnerabilities.

A meaningful finding requires conditions such as:

```text
Unquoted Path
    +
Space in Path
    +
Current User Can Write a Candidate Location
    +
Service Runs More Privileged
```

---

# Service Path Analysis

Example path:

```text
C:\Program Files\Example Service\service.exe
```

Do not assume this is exploitable merely because it contains spaces.

Validate permissions on relevant path components.

---

# Scheduled Tasks

CMD:

```cmd
schtasks /query
```

Verbose:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

---

# Scheduled Task Details

```powershell
Get-ScheduledTask |
    Select-Object TaskPath,TaskName,State
```

Actions:

```powershell
Get-ScheduledTask |
    ForEach-Object {
        [PSCustomObject]@{
            TaskPath = $_.TaskPath
            TaskName = $_.TaskName
            Actions  = ($_.Actions.Execute -join '; ')
        }
    }
```

---

# Scheduled Task Security Model

```text
Task
 |
 v
Execution Identity
 |
 v
Action
 |
 v
Executable / Script
 |
 v
Permissions
```

Look for:

```text
High-Privilege Task
        +
Low-Privilege Writable Dependency
```

---

# Task Scheduler Service

```powershell
Get-Service Schedule
```

---

# Startup Programs

Current user:

```cmd
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
```

All users:

```cmd
dir "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
```

PowerShell:

```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
```

---

# Autorun Registry Locations

Current user:

```cmd
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
```

Machine:

```cmd
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```

RunOnce:

```cmd
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce"
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce"
```

---

# Registry

Query key:

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
```

Recursive:

```cmd
reg query "HKLM\SOFTWARE\Vendor" /s
```

PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
```

---

# Registry Permissions

```powershell
Get-Acl 'HKLM:\SOFTWARE\Vendor\Product' |
    Format-List
```

---

# Search Registry

Use targeted searches.

Example:

```cmd
reg query HKCU /f "password" /t REG_SZ /s
```

Machine scope can be very noisy:

```cmd
reg query HKLM /f "password" /t REG_SZ /s
```

Prefer known application paths rather than blindly searching the entire registry.

---

# Files

List:

```cmd
dir
```

Hidden:

```cmd
dir /a
```

Recursive:

```cmd
dir /s
```

PowerShell:

```powershell
Get-ChildItem
```

Hidden:

```powershell
Get-ChildItem -Force
```

Recursive:

```powershell
Get-ChildItem -Recurse
```

---

# File Permissions

CMD:

```cmd
icacls "C:\Path\file.exe"
```

Directory:

```cmd
icacls "C:\Path"
```

PowerShell:

```powershell
Get-Acl 'C:\Path\file.exe' |
    Format-List
```

---

# icacls Permission Reference

Common rights include:

```text
F   Full control
M   Modify
RX  Read and execute
R   Read
W   Write
```

Inheritance indicators can include:

```text
OI  Object inherit
CI  Container inherit
IO  Inherit only
I   Inherited
```

---

# Writable Location Test

First inspect:

```powershell
Get-Acl 'C:\Path' |
    Format-List
```

If an actual write test is necessary and authorised, use a temporary uniquely named file and remove it immediately.

Do not leave test artifacts behind.

---

# Common Writable Locations

Examples often writable by standard users include:

```text
%TEMP%
%LOCALAPPDATA%\Temp
C:\Users\<user>\
```

Other writable locations depend on ACL configuration.

A writable directory is not itself a privilege-escalation finding.

The important question is:

```text
Does a More-Privileged Process Trust It?
```

---

# Search Files by Name

CMD:

```cmd
dir C:\ /s /b *config* 2>nul
```

PowerShell:

```powershell
Get-ChildItem C:\ -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Name -like '*config*'
```

Targeted searches are strongly preferred.

---

# Search File Contents

PowerShell:

```powershell
Get-ChildItem 'C:\Path' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','secret','token'
```

Avoid broad searches across large production volumes unless necessary.

---

# Interesting Configuration Files

Common examples:

```text
web.config
appsettings.json
*.config
*.xml
*.ini
*.yml
*.yaml
*.json
unattend.xml
unattended.xml
sysprep.inf
sysprep.xml
```

The presence of a file does not mean it contains credentials.

---

# Unattended Installation Files

Potential historical locations include:

```text
C:\Windows\Panther\
C:\Windows\Panther\Unattend\
C:\Windows\System32\Sysprep\
```

Search:

```powershell
Get-ChildItem C:\Windows -Recurse -Include unattend.xml,unattended.xml,sysprep.xml -ErrorAction SilentlyContinue
```

Handle discovered credentials as sensitive evidence.

---

# IIS Configuration

Common location:

```text
C:\inetpub\
```

Application configuration commonly uses:

```text
web.config
```

Search targeted IIS directories:

```powershell
Get-ChildItem C:\inetpub -Recurse -Filter web.config -ErrorAction SilentlyContinue
```

---

# PowerShell History

Current user:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Read:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

Common default path:

```text
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

History may contain sensitive commands but is not a complete audit trail.

---

# PowerShell Transcription

Potential policy settings:

```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription"
```

PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue
```

Transcripts may contain sensitive command output and credentials.

---

# PowerShell Logging

Script block logging:

```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
```

Module logging:

```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
```

---

# PowerShell Language Mode

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

`FullLanguage` is normal on many Windows systems and is not automatically a vulnerability.

Interpret it in the context of the organisation's application-control and endpoint-hardening requirements.

---

# PowerShell Version

```powershell
$PSVersionTable
```

---

# Credential Manager

List stored credential metadata:

```cmd
cmdkey /list
```

Do not attempt to extract stored credential secrets merely because entries exist.

---

# Windows Vault / Stored Credentials

Credential metadata can also be inspected through normal Windows interfaces and authorised management tooling.

The security question is:

```text
Can the Current Security Context
Access Reusable Authentication Material?
```

---

# Wi-Fi Profiles

List profiles:

```cmd
netsh wlan show profiles
```

Do not extract stored wireless keys unless the assessment scope specifically includes credential recovery.

---

# DPAPI

Windows uses DPAPI to protect many user and machine secrets.

Common DPAPI-backed data includes:

```text
Browser Credentials
Credential Manager
Certificates
Application Secrets
Wireless Credentials
```

The existence of DPAPI-protected data is normal.

Report only unintended access to protected secrets.

---

# SAM and SYSTEM

Registry hives include:

```text
SAM
SYSTEM
SECURITY
```

These contain security-sensitive system data.

Do not save, copy or dump these hives during routine enumeration unless credential extraction is explicitly authorised.

---

# LSA Protection

Check RunAsPPL configuration:

```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v RunAsPPL
```

Interpret alongside the actual Windows version and security configuration.

---

# Credential Guard

Useful system information:

```powershell
Get-ComputerInfo |
    Select-Object DeviceGuard*
```

On supported environments, additional Device Guard/Credential Guard state can be obtained through appropriate Windows management interfaces.

Do not assume absence from one query means the control is disabled.

---

# Windows Defender

Status:

```powershell
Get-MpComputerStatus
```

Selected fields:

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusEnabled,RealTimeProtectionEnabled,BehaviorMonitorEnabled,IoavProtectionEnabled,AntispywareEnabled
```

---

# Defender Preferences

```powershell
Get-MpPreference
```

Review relevant configuration such as:

```text
Exclusions
Cloud Protection
Network Protection
ASR
Controlled Folder Access
```

Do not change Defender configuration during routine testing.

---

# Defender Exclusions

```powershell
Get-MpPreference |
    Select-Object ExclusionPath,ExclusionProcess,ExclusionExtension
```

Access may be restricted.

An exclusion is not automatically a vulnerability; assess whether it creates an exploitable trust boundary.

---

# Attack Surface Reduction

Rules:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,AttackSurfaceReductionRules_Actions
```

---

# Firewall

```powershell
Get-NetFirewallProfile
```

Enabled rules:

```powershell
Get-NetFirewallRule |
    Where-Object Enabled -eq 'True'
```

---

# AppLocker

Effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

XML:

```powershell
Get-AppLockerPolicy -Effective -Xml
```

Collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```

---

# Test AppLocker Policy

For a specific file:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\test.exe' -User "$env:USERDOMAIN\$env:USERNAME"
```

For a script:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\test.ps1' -User "$env:USERDOMAIN\$env:USERNAME"
```

This tests policy evaluation without executing the target.

---

# AppLocker Collections

Common collections include:

```text
Exe
Msi
Script
Dll
Appx
```

Important distinction:

```text
Collection Not Configured
```

does not necessarily mean:

```text
No Application Control Exists
```

WDAC or another security product may also enforce policy.

---

# WDAC / Application Control

Windows Defender Application Control is now commonly documented under App Control for Business.

Useful checks depend on the Windows version and available management interfaces.

Potential indicators include:

```text
Code Integrity Policies
Device Guard Configuration
Code Integrity Event Logs
```

Do not rely on one command alone to declare WDAC enabled or disabled.

---

# Code Integrity Logs

Useful logs include:

```text
Microsoft-Windows-CodeIntegrity/Operational
```

Query recent events:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 50
```

---

# AppLocker Logs

Examples:

```text
Microsoft-Windows-AppLocker/EXE and DLL
Microsoft-Windows-AppLocker/MSI and Script
```

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 50
```

---

# Security Products

Installed security products should be identified carefully.

Processes:

```powershell
Get-Process
```

Services:

```powershell
Get-Service
```

Defender:

```powershell
Get-MpComputerStatus
```

Do not terminate or disable endpoint security controls during routine enumeration.

---

# Installed Software

Registry:

```powershell
$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

Get-ItemProperty $paths -ErrorAction SilentlyContinue |
    Where-Object DisplayName |
    Select-Object DisplayName,DisplayVersion,Publisher |
    Sort-Object DisplayName
```

Current user applications may also appear under HKCU.

---

# MSI - AlwaysInstallElevated

Check machine policy:

```cmd
reg query "HKLM\Software\Policies\Microsoft\Windows\Installer" /v AlwaysInstallElevated
```

Check user policy:

```cmd
reg query "HKCU\Software\Policies\Microsoft\Windows\Installer" /v AlwaysInstallElevated
```

PowerShell:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\Installer' -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```

```powershell
Get-ItemProperty 'HKCU:\Software\Policies\Microsoft\Windows\Installer' -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```

The classic unsafe condition requires the relevant policy configuration in both machine and user contexts.

Do not install a test MSI merely to prove the risk unless explicitly authorised.

---

# WSL

Check:

```cmd
wsl --status
```

Distributions:

```cmd
wsl --list --verbose
```

WSL presence is not itself a vulnerability.

Review its relevance to:

```text
Credential Boundaries
Filesystem Access
Development Tooling
Network Exposure
```

---

# Named Pipes

List:

```powershell
Get-ChildItem \\.\pipe\
```

Named pipes are normal Windows IPC mechanisms.

Investigate only where:

```text
Pipe Security
   +
Privileged Service
   +
Unsafe Client/Server Trust
```

creates an actual boundary issue.

---

# Drivers

List:

```cmd
driverquery
```

Verbose:

```cmd
driverquery /v
```

PowerShell:

```powershell
Get-CimInstance Win32_SystemDriver |
    Select-Object Name,State,StartMode,PathName
```

---

# Driver Security

A driver should not be labelled vulnerable solely because it is old.

Validate:

```text
Exact Driver Version
Vendor
Known Vulnerability
Affected Version Range
Exploit Preconditions
Microsoft Driver Blocklist
Security Controls
```

---

# Printers

```powershell
Get-Printer
```

Spooler:

```powershell
Get-Service Spooler
```

Printer-related services have historically been security-sensitive, but an enabled Print Spooler is not automatically a vulnerability.

Assess role and exposure.

---

# Windows Features

```powershell
Get-WindowsOptionalFeature -Online |
    Where-Object State -eq 'Enabled'
```

On Windows Server:

```powershell
Get-WindowsFeature
```

if the ServerManager module is available.

---

# IIS

Server feature:

```powershell
Get-Service W3SVC -ErrorAction SilentlyContinue
```

Common root:

```text
C:\inetpub\
```

Configuration:

```text
C:\Windows\System32\inetsrv\config\
```

Handle IIS configuration carefully because it can contain sensitive application settings.

---

# Remote Desktop

Service:

```powershell
Get-Service TermService
```

Port:

```powershell
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

RDP configuration:

```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server"
```

---

# WinRM

Service:

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
Get-WSManInstance -ResourceURI winrm/config/listener -Enumerate
```

---

# SMB

Service:

```powershell
Get-Service LanmanServer
```

Configuration:

```powershell
Get-SmbServerConfiguration
```

Shares:

```powershell
Get-SmbShare
```

---

# Event Logs

List logs:

```powershell
Get-WinEvent -ListLog *
```

Recent System events:

```powershell
Get-WinEvent -LogName System -MaxEvents 50
```

Security:

```powershell
Get-WinEvent -LogName Security -MaxEvents 50
```

Access to the Security log may be restricted.

---

# Useful Security Event IDs

Common examples include:

| Event ID | Description |
|---:|---|
| 4624 | Successful logon |
| 4625 | Failed logon |
| 4648 | Logon using explicit credentials |
| 4672 | Special privileges assigned to new logon |
| 4688 | New process created |
| 4697 | Service installed |
| 4698 | Scheduled task created |
| 4702 | Scheduled task updated |
| 4720 | User account created |
| 4728 | Member added to global security group |
| 4732 | Member added to local security group |
| 7045 | Service installed - System log |

Audit policy determines whether many Security events are available.

---

# Audit Policy

```cmd
auditpol /get /category:*
```

---

# Local Security Policy

Useful effective policy information:

```cmd
net accounts
```

For broader security-policy review, use authorised policy-management or export mechanisms rather than changing settings.

---

# Password Policy

Local:

```cmd
net accounts
```

Domain context where applicable:

```cmd
net accounts /domain
```

---

# Local Administrators Security Model

```text
User
 |
 v
Local Group Membership
 |
 v
Administrators
 |
 v
UAC / Token
 |
 v
Administrative Capability
```

Being a member of Administrators and currently running with a high-integrity token are related but not identical concepts.

---

# Privileged Group Review

```powershell
Get-LocalGroup |
    ForEach-Object {
        $group = $_
        try {
            Get-LocalGroupMember -Group $group.Name -ErrorAction Stop |
                Select-Object @{N='Group';E={$group.Name}},Name,PrincipalSource
        } catch {}
    }
```

---

# Privilege Escalation - Core Model

Most local Windows privilege escalation can be reduced to:

```text
Low-Privilege User
        |
        v
Privileged Resource
        |
        v
Unsafe Permission / Trust
        |
        v
Higher-Privilege Execution
```

Common categories:

```text
Services
Scheduled Tasks
File ACLs
Registry ACLs
Credentials
Token Privileges
Installers
Drivers
Applications
Operating System Vulnerabilities
```

---

# Service Escalation Checklist

```text
Service Runs as SYSTEM/Admin?
          |
          v
Can User Reconfigure Service?
          |
          +--> Yes --> Finding Candidate
          |
          v
Can User Modify Executable?
          |
          +--> Yes --> Finding Candidate
          |
          v
Can User Modify Dependency?
          |
          +--> Yes --> Finding Candidate
          |
          v
Unquoted Path?
          |
          +--> Yes --> Check Candidate Directory ACLs
```

---

# Scheduled Task Escalation Checklist

```text
Task Runs Privileged?
       |
       v
Action Identified?
       |
       v
Can User Modify Script/Binary?
       |
       v
Can User Modify Parent Directory?
       |
       v
Can User Modify Configuration?
```

---

# File ACL Escalation Checklist

```text
Writable File
    |
    v
Who Uses It?
    |
    v
When?
    |
    v
Under Which Identity?
    |
    v
Does Modification Influence Execution?
```

---

# Registry ACL Escalation Checklist

```text
Writable Registry Key
       |
       v
What Component Reads It?
       |
       v
Does Component Run Privileged?
       |
       v
Can Value Influence Code / Path / Configuration?
```

---

# Credential Escalation Checklist

```text
Readable Secret
    |
    v
Which Identity?
    |
    v
More Privileged?
    |
    v
Reusable?
    |
    v
Within Scope?
```

Avoid authenticating with discovered credentials unless explicitly permitted.

---

# Impersonation Privileges

Review:

```cmd
whoami /priv
```

Particularly:

```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
```

These privileges are common for some service identities.

Their presence should trigger context analysis rather than automatic exploitation.

---

# Backup Operators

Check groups:

```cmd
whoami /groups
```

Backup-related privileges:

```text
SeBackupPrivilege
SeRestorePrivilege
```

These can provide broad access that bypasses ordinary file permissions when used through appropriate backup semantics.

Do not use them to extract credential stores unless explicitly authorised.

---

# Take Ownership

Relevant privilege:

```text
SeTakeOwnershipPrivilege
```

Check:

```cmd
whoami /priv
```

Do not change ownership merely to prove the privilege exists.

---

# Debug Privilege

```text
SeDebugPrivilege
```

Check:

```cmd
whoami /priv
```

This privilege can grant powerful process access.

Do not access sensitive processes unnecessarily.

---

# Driver Loading

Relevant privilege:

```text
SeLoadDriverPrivilege
```

Review:

```cmd
whoami /priv
```

Do not load a driver as part of routine validation.

---

# Automated Enumeration

Useful authorised host-enumeration tools include:

```text
winPEAS
PrivescCheck
Seatbelt
PowerUp
WES-NG
```

Tool execution can trigger endpoint security controls and produce extensive telemetry.

Obtain authorisation before using them.

---

# winPEAS

Project:

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Use the current project documentation for execution syntax.

Treat output as:

```text
Candidate Findings
```

not confirmed vulnerabilities.

---

# PrivescCheck

Project:

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

Useful for structured Windows privilege-escalation enumeration.

---

# Seatbelt

Project:

[Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

Seatbelt performs security-oriented host survey checks.

Use only where execution of third-party assessment tooling is permitted.

---

# PowerUp

PowerUp is part of the PowerSploit project.

Project:

[PowerSploit](https://github.com/PowerShellMafia/PowerSploit){ target="_blank" rel="noopener noreferrer" }

PowerSploit is an older project and should be treated accordingly when comparing its checks with modern Windows versions and controls.

---

# WES-NG

Project:

[Windows Exploit Suggester - Next Generation](https://github.com/bitsadmin/wesng){ target="_blank" rel="noopener noreferrer" }

Typical workflow:

```text
systeminfo
   |
   v
WES-NG
   |
   v
Candidate CVEs
   |
   v
Verify Patch State
   |
   v
Verify Preconditions
```

Do not report WES-NG suggestions without manual validation.

---

# Automated Enumeration Model

```text
Tool
 |
 v
Candidate
 |
 v
Manual Verification
 |
 v
Permissions / Version / Context
 |
 v
Security Boundary
 |
 v
Finding
```

Never use:

```text
winPEAS highlighted it
```

as the sole evidence for a finding.

---

# Kernel / OS Vulnerabilities

Collect:

```cmd
systeminfo
```

and:

```powershell
Get-HotFix
```

Then determine:

```text
Exact Windows Version
Build
Revision
Architecture
Installed Cumulative Update
Vulnerability
Affected Build Range
Exploit Preconditions
```

Do not run public local privilege-escalation exploits solely to verify patch state.

---

# Software Vulnerabilities

Installed software:

```powershell
$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

Get-ItemProperty $paths -ErrorAction SilentlyContinue |
    Where-Object DisplayName |
    Select-Object DisplayName,DisplayVersion,Publisher
```

Then verify versions against vendor advisories.

---

# LOLBins

Windows contains many legitimate binaries and scripts that can perform security-sensitive operations.

The presence of such a binary is not a vulnerability.

The security question is:

```text
Is a Legitimate Administrative Capability
Exposed in a Way That Violates
the Intended Security Boundary?
```

Application-control testing should focus on effective policy rather than merely listing installed binaries.

---

# Application Control Test Model

```text
Candidate Binary / Script
          |
          v
Effective AppLocker / WDAC Policy
          |
          v
Test Policy Decision
          |
          v
Execution Needed?
          |
          +--> No --> Record Read-Only Result
          |
          +--> Yes --> Only If Authorised
```

---

# AppLocker Example

Check executable policy without execution:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\wscript.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

Interpret:

```text
Allowed
Denied
DeniedByDefault
```

alongside the matching rule and other application-control layers.

---

# PowerShell Execution Policy

```powershell
Get-ExecutionPolicy -List
```

Execution Policy is not a security boundary.

Do not equate:

```text
Restricted
```

with comprehensive PowerShell application control.

---

# AMSI

AMSI is an antimalware scanning interface used by supported applications and scripting engines.

Do not attempt to patch or disable AMSI during routine enumeration.

Assess endpoint protection through supported status, configuration and test mechanisms.

---

# Windows Defender Version

```powershell
Get-MpComputerStatus |
    Select-Object AMProductVersion,AMEngineVersion,AntivirusSignatureVersion,AntivirusSignatureLastUpdated
```

---

# HTTP Requests

PowerShell:

```powershell
Invoke-WebRequest -Uri 'https://example.com/' -UseBasicParsing
```

Save response:

```powershell
Invoke-WebRequest -Uri 'https://example.com/file.txt' -OutFile 'C:\Temp\file.txt'
```

Only download assessment tooling where authorised.

---

# curl

Modern Windows versions commonly include `curl.exe`.

```cmd
curl.exe https://example.com/
```

Headers:

```cmd
curl.exe -I https://example.com/
```

Save:

```cmd
curl.exe -o file.txt https://example.com/file.txt
```

---

# File Hash

```powershell
Get-FileHash 'C:\Path\file.exe' -Algorithm SHA256
```

---

# Base64

Encode text:

```powershell
[Convert]::ToBase64String(
    [Text.Encoding]::UTF8.GetBytes('test')
)
```

Decode:

```powershell
[Text.Encoding]::UTF8.GetString(
    [Convert]::FromBase64String('dGVzdA==')
)
```

---

# Search Text

```powershell
Select-String -Path '.\file.txt' -Pattern 'text'
```

Recursive:

```powershell
Get-ChildItem C:\Path -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'text'
```

---

# Find Executable

CMD:

```cmd
where powershell.exe
```

PowerShell:

```powershell
Get-Command powershell.exe
```

---

# File Version

```powershell
(Get-Item 'C:\Path\application.exe').VersionInfo
```

Useful fields:

```powershell
(Get-Item 'C:\Path\application.exe').VersionInfo |
    Select-Object FileVersion,ProductVersion,CompanyName,FileDescription
```

---

# Authenticode Signature

```powershell
Get-AuthenticodeSignature 'C:\Path\application.exe'
```

---

# Alternate Data Streams

List streams:

```powershell
Get-Item 'C:\Path\file.txt' -Stream *
```

ADS are a normal NTFS feature and are not inherently malicious.

---

# Recycle Bin

Do not search user recycle bins for sensitive information unless relevant and authorised.

If required for forensic or configuration review, preserve privacy and minimise data collection.

---

# Shadow Copies

List:

```cmd
vssadmin list shadows
```

PowerShell/CIM:

```powershell
Get-CimInstance Win32_ShadowCopy
```

Shadow copies are normal backup functionality.

Do not use them to extract protected credential stores unless explicitly authorised.

---

# BitLocker

```cmd
manage-bde -status
```

PowerShell:

```powershell
Get-BitLockerVolume
```

Availability depends on Windows edition and PowerShell modules.

---

# Secure Boot

```powershell
Confirm-SecureBootUEFI
```

This may fail on unsupported firmware or non-UEFI systems.

---

# TPM

```powershell
Get-Tpm
```

---

# Local Security Quick Check

```cmd
whoami /all
systeminfo
net user
net localgroup administrators
ipconfig /all
route print
netstat -ano
tasklist /svc
sc query
schtasks /query /fo LIST /v
netsh advfirewall show allprofiles
auditpol /get /category:*
```

---

# PowerShell Security Quick Check

```powershell
Get-ComputerInfo
Get-LocalUser
Get-LocalGroup
Get-Process
Get-Service
Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection -State Listen
Get-ScheduledTask
Get-MpComputerStatus
Get-NetFirewallProfile
Get-AppLockerPolicy -Effective
$ExecutionContext.SessionState.LanguageMode
Get-ExecutionPolicy -List
```

---

# Windows Privilege Escalation Quick Flow

```text
Identity
   |
   v
Groups
   |
   v
Privileges
   |
   v
OS / Patches
   |
   v
Processes
   |
   v
Services
   |
   v
Scheduled Tasks
   |
   v
Files / ACLs
   |
   v
Registry / ACLs
   |
   v
Credentials
   |
   v
Installer Policy
   |
   v
Drivers
   |
   v
Security Controls
```

---

# High-Value Initial Commands

```cmd
whoami /all
systeminfo
ipconfig /all
route print
netstat -ano
tasklist /svc
sc query
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ComputerInfo
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
Get-ScheduledTask
Get-MpComputerStatus
Get-NetFirewallProfile
```

---

# Manual Privilege Escalation Checklist

## Identity

- [ ] Current username
- [ ] SID
- [ ] Groups
- [ ] Token privileges
- [ ] Integrity level
- [ ] Domain membership
- [ ] Local administrator membership

## System

- [ ] Windows edition
- [ ] Version
- [ ] Build
- [ ] Architecture
- [ ] Installed updates
- [ ] Last boot
- [ ] Installed applications

## Network

- [ ] Interfaces
- [ ] Routes
- [ ] DNS
- [ ] ARP / neighbours
- [ ] Listening ports
- [ ] Established connections
- [ ] Proxy configuration
- [ ] Firewall

## Processes

- [ ] Running processes
- [ ] Parent processes
- [ ] Command lines
- [ ] Process owners where available
- [ ] Security software
- [ ] Management agents

## Services

- [ ] Service accounts
- [ ] Executable paths
- [ ] Service ACLs
- [ ] Executable ACLs
- [ ] Directory ACLs
- [ ] Configuration ACLs
- [ ] Unquoted paths
- [ ] Writable dependencies

## Scheduled Tasks

- [ ] Task identity
- [ ] Task action
- [ ] Executable
- [ ] Script
- [ ] File permissions
- [ ] Directory permissions
- [ ] Configuration dependencies

## Files

- [ ] Writable application directories
- [ ] Writable privileged executables
- [ ] Configuration files
- [ ] Backup files
- [ ] Unattended installation files
- [ ] IIS configuration
- [ ] PowerShell history

## Registry

- [ ] Autoruns
- [ ] Service configuration
- [ ] Application configuration
- [ ] Installer policy
- [ ] Writable privileged keys

## Credentials

- [ ] Credential Manager metadata
- [ ] PowerShell history
- [ ] PowerShell transcripts
- [ ] Application configuration
- [ ] Service configuration
- [ ] Deployment files
- [ ] Cloud/application credentials where relevant
- [ ] Redact discovered secrets

## Privileges

- [ ] SeImpersonatePrivilege
- [ ] SeAssignPrimaryTokenPrivilege
- [ ] SeBackupPrivilege
- [ ] SeRestorePrivilege
- [ ] SeTakeOwnershipPrivilege
- [ ] SeDebugPrivilege
- [ ] SeLoadDriverPrivilege
- [ ] Other unusual rights

## Security Controls

- [ ] Defender status
- [ ] Defender exclusions
- [ ] ASR
- [ ] Firewall
- [ ] AppLocker
- [ ] WDAC / App Control
- [ ] PowerShell language mode
- [ ] PowerShell logging
- [ ] Credential Guard
- [ ] LSA protection
- [ ] BitLocker
- [ ] Secure Boot

## Software / Kernel

- [ ] Installed software versions
- [ ] Drivers
- [ ] OS build
- [ ] Patch state
- [ ] Candidate CVEs manually validated
- [ ] Vendor advisories checked

## Evidence

- [ ] Record hostname
- [ ] Record username
- [ ] Record groups
- [ ] Record privileges
- [ ] Record exact command
- [ ] Capture relevant output
- [ ] Record ACLs
- [ ] Record service/task identity
- [ ] Explain privilege boundary
- [ ] Redact credentials
- [ ] Clean up temporary test artifacts

---

# Do Not Overreport

Do not automatically report:

```text
PowerShell FullLanguage
Defender Exclusion Exists
Writable Temp Directory
Unquoted Service Path
Scheduled Task Exists
SeImpersonatePrivilege Exists
AppLocker DLL Collection Not Configured
Old Application Installed
Driver Installed
SMB Enabled
RDP Enabled
WinRM Enabled
```

Instead determine:

```text
Who Can Reach It?
       |
       v
What Can They Control?
       |
       v
Which Security Context Uses It?
       |
       v
Can a Boundary Be Crossed?
```

---

# Example - Unquoted Service Path

Weak evidence:

```text
Service path contains spaces and is not quoted.
```

Better analysis:

```text
Service runs as LocalSystem
        |
        v
Path is unquoted
        |
        v
Candidate path exists
        |
        v
Standard user can write candidate location
        |
        v
Service execution could cross
user -> SYSTEM boundary
```

If the writable condition is absent, the classic escalation path may not exist.

---

# Example - Writable Directory

Weak finding:

```text
C:\ProgramData\Example is writable.
```

Better question:

```text
What privileged component trusts files
inside C:\ProgramData\Example?
```

If nothing privileged consumes the writable content, the security impact may be limited.

---

# Example - FullLanguage

Observation:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Output:

```text
FullLanguage
```

Do not automatically classify this as a vulnerability.

A defensible hardening observation may instead be:

```text
PowerShell is available in FullLanguage mode to the assessed
standard-user context. Where the endpoint security model relies
on application control to restrict script-based administrative
capabilities, consider enforcing an appropriate WDAC/AppLocker
policy that results in Constrained Language Mode for untrusted
PowerShell code.
```

---

# Example - AppLocker

Read-only policy test:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\candidate.exe' -User "$env:USERDOMAIN\$env:USERNAME"
```

A useful finding needs more than:

```text
PolicyDecision = Allowed
```

Determine:

```text
Why is it allowed?
Is that intentional?
Can the user control content consumed by it?
Does WDAC provide another enforcement layer?
Does the allowed capability create an actual security boundary bypass?
```

---

# Evidence Model

```text
Principal
   |
   v
Permission
   |
   v
Object
   |
   v
Privileged Consumer
   |
   v
Impact
```

For example:

```text
Standard User
    |
    v
Modify
    |
    v
Service Executable
    |
    v
LocalSystem Service
    |
    v
Potential Local Privilege Escalation
```

---

# Safe Validation

Prefer:

```text
Read Policy
Read ACL
Read Configuration
Inspect Service
Inspect Task
Inspect Token
Test Policy Decision
```

before:

```text
Modify File
Restart Service
Create Task
Change Registry
Disable Security Control
Execute Exploit
```

A good assessment proves the vulnerability with the least possible system modification.

---

# Cleanup

If a write test was explicitly necessary:

```text
Create Unique Temporary Artifact
          |
          v
Record Result
          |
          v
Delete Artifact
          |
          v
Verify Removal
```

Document all state changes.

---

# Quick Command Reference

```cmd
:: Identity
whoami
whoami /all
whoami /groups
whoami /priv

:: System
hostname
systeminfo
ver

:: Users
net user
net localgroup
net localgroup administrators

:: Network
ipconfig /all
route print
arp -a
netstat -ano

:: Processes
tasklist
tasklist /svc

:: Services
sc query
sc qc SERVICE_NAME

:: Tasks
schtasks /query /fo LIST /v

:: Shares
net share
net use

:: Firewall
netsh advfirewall show allprofiles

:: Domain
echo %USERDOMAIN%
echo %USERDNSDOMAIN%
echo %LOGONSERVER%
nltest /dsgetdc:%USERDNSDOMAIN%

:: Audit
auditpol /get /category:*

:: Credential metadata
cmdkey /list
```

PowerShell:

```powershell
Get-ComputerInfo
Get-LocalUser
Get-LocalGroup
Get-Process
Get-Service
Get-CimInstance Win32_Service
Get-ScheduledTask
Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection
Get-NetFirewallProfile
Get-MpComputerStatus
Get-MpPreference
Get-AppLockerPolicy -Effective
Get-ExecutionPolicy -List
$ExecutionContext.SessionState.LanguageMode
```

---

# Testing Model

The Windows privilege model can be simplified as:

```text
Identity
   |
   v
Token
   |
   v
Groups + Privileges
   |
   v
Access Control
   |
   v
Windows Object
```

Privilege escalation usually introduces a relationship such as:

```text
Low-Privilege Identity
          |
          v
Control Over Resource
          |
          v
Resource Trusted by Privileged Identity
          |
          v
Higher Privilege
```

For services:

```text
User
 |
 v
Writable Service Component
 |
 v
SYSTEM Service
 |
 v
Privilege Boundary
```

For scheduled tasks:

```text
User
 |
 v
Writable Task Dependency
 |
 v
Privileged Task
 |
 v
Privilege Boundary
```

For credentials:

```text
User
 |
 v
Readable Authentication Material
 |
 v
Privileged Identity
 |
 v
Privilege Boundary
```

For token privileges:

```text
Process Token
 |
 v
Assigned Privilege
 |
 v
Security-Sensitive Windows Operation
 |
 v
Potential Boundary Crossing
```

For vulnerable software:

```text
Software Version
 |
 v
Known Vulnerability
 |
 v
Preconditions Satisfied
 |
 v
Affected Security Boundary
```

---

# References

## HackTricks

[HackTricks - Windows Local Privilege Escalation Checklist](https://hacktricks.wiki/en/windows-hardening/checklist-windows-privilege-escalation.html){ target="_blank" rel="noopener noreferrer" }

Useful as a broad Windows privilege-escalation checklist and research reference.

Validate individual techniques against the Windows version and configuration being assessed.

---

## InternalAllTheThings

[InternalAllTheThings - Windows Privilege Escalation](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/){ target="_blank" rel="noopener noreferrer" }

Useful coverage reference for areas including:

```text
Windows Enumeration
Users
Network
Security Products
Writable Locations
Credentials
Processes
Services
Scheduled Tasks
Unquoted Service Paths
Windows Installer
Drivers
Impersonation Privileges
Privileged File Operations
Windows Vulnerabilities
```

---

## Microsoft Learn

[Microsoft Learn - Windows Security](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }

Use Microsoft documentation as the authoritative reference for Windows security-control behaviour.

---

## Windows Defender

[Microsoft Defender Antivirus](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-antivirus-windows){ target="_blank" rel="noopener noreferrer" }

---

## AppLocker

[Microsoft Learn - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }

---

## App Control for Business

[Microsoft Learn - App Control for Business](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }

---

## PowerShell

[Microsoft Learn - PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/){ target="_blank" rel="noopener noreferrer" }

---

## PEASS-ng

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

---

## PrivescCheck

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

---

## Seatbelt

[Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

---

## WES-NG

[Windows Exploit Suggester - Next Generation](https://github.com/bitsadmin/wesng){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

The most useful first questions on a Windows endpoint are:

```text
Who am I?
What groups am I in?
What privileges do I have?
What version of Windows is this?
What runs with more privilege than me?
What can I modify?
What security controls restrict me?
```

Start with:

```cmd
whoami /all
systeminfo
tasklist /svc
sc query
schtasks /query /fo LIST /v
ipconfig /all
netstat -ano
```

Then investigate the relationships between:

```text
Permissions
    +
Privileged Execution
```

rather than simply searching for unusual files or binaries.

The important distinction is:

```text
Interesting Configuration
        !=
Confirmed Privilege Escalation
```

A service path, scheduled task, token privilege, writable directory or installed driver becomes security-relevant when the complete privilege path can be demonstrated.

Use:

```text
Enumeration
    |
    v
Candidate
    |
    v
Manual Validation
    |
    v
Minimal Proof
    |
    v
Evidence
    |
    v
Cleanup
```

Automated tools such as winPEAS, PrivescCheck, Seatbelt and WES-NG are useful accelerators, but the final finding should always explain the actual Windows security boundary that can be crossed.
