# PowerShell Cheatsheet

Quick-reference PowerShell commands for Windows administration, enumeration, troubleshooting and authorised security assessments.

This cheatsheet covers:

```text
PowerShell
   |
   +--> Environment
   +--> Files / Directories
   +--> Processes
   +--> Services
   +--> Networking
   +--> Registry
   +--> ACLs
   +--> Users / Groups
   +--> Scheduled Tasks
   +--> Event Logs
   +--> Defender
   +--> AppLocker
   +--> PowerShell Security
   +--> Active Directory
   +--> Data Processing
   +--> Downloads
   +--> Encoding
   +--> Evidence Collection
```

!!! warning "Authorised testing only"
    Use these commands only on systems you own or are explicitly authorised to assess. Prefer read-only enumeration and minimal-impact validation. Do not disable security controls, alter policies, extract unnecessary credentials or execute untrusted code merely to demonstrate a finding.

---

# Quick Start

```powershell
whoami
whoami /all

$PSVersionTable
$ExecutionContext.SessionState.LanguageMode
Get-ExecutionPolicy -List

hostname
Get-ComputerInfo

Get-LocalUser
Get-LocalGroup
Get-Process
Get-Service

Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection

Get-ScheduledTask
Get-MpComputerStatus
Get-NetFirewallProfile
```

Useful assessment flow:

```text
Identity
   |
   v
PowerShell Environment
   |
   v
System
   |
   v
Users / Groups
   |
   v
Processes / Services
   |
   v
Network
   |
   v
Files / Registry / ACLs
   |
   v
Scheduled Tasks
   |
   v
Security Controls
```

---

# PowerShell Version

```powershell
$PSVersionTable
```

Version only:

```powershell
$PSVersionTable.PSVersion
```

Edition:

```powershell
$PSVersionTable.PSEdition
```

Useful distinction:

```text
Windows PowerShell
        |
        +--> Windows PowerShell 5.1
        |
PowerShell
        |
        +--> Modern cross-platform PowerShell
```

Do not assume syntax, modules or security behaviour is identical across versions.

---

# PowerShell Executable

Current process:

```powershell
Get-Process -Id $PID
```

Executable path:

```powershell
(Get-Process -Id $PID).Path
```

Command discovery:

```powershell
Get-Command powershell.exe -ErrorAction SilentlyContinue
Get-Command pwsh.exe -ErrorAction SilentlyContinue
```

---

# Current Identity

```powershell
whoami
```

Detailed:

```powershell
whoami /all
```

Groups:

```powershell
whoami /groups
```

Privileges:

```powershell
whoami /priv
```

.NET identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent()
```

Username:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

SID:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
```

---

# Administrator Check

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)

$principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)
```

This checks membership in the Administrators role for the current token context.

UAC can affect the effective privileges available to the process.

---

# Environment Variables

```powershell
Get-ChildItem Env:
```

Specific:

```powershell
$env:USERNAME
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:COMPUTERNAME
$env:USERPROFILE
$env:APPDATA
$env:LOCALAPPDATA
$env:TEMP
$env:WINDIR
$env:PATH
```

PATH one entry per line:

```powershell
$env:PATH -split ';'
```

---

# Current Directory

```powershell
Get-Location
```

Alias:

```powershell
pwd
```

Change:

```powershell
Set-Location C:\Temp
```

Alias:

```powershell
cd C:\Temp
```

---

# Command Discovery

Find command:

```powershell
Get-Command Get-Service
```

Executable:

```powershell
Get-Command cmd.exe
```

All matching commands:

```powershell
Get-Command *service*
```

Command type:

```powershell
Get-Command Get-Service |
    Select-Object Name,CommandType,Source
```

---

# Help

```powershell
Get-Help Get-Service
```

Examples:

```powershell
Get-Help Get-Service -Examples
```

Full:

```powershell
Get-Help Get-Service -Full
```

Online:

```powershell
Get-Help Get-Service -Online
```

---

# Aliases

List:

```powershell
Get-Alias
```

Specific:

```powershell
Get-Alias ls
```

Resolve alias:

```powershell
Get-Command ls
```

For documentation and reusable scripts, prefer full cmdlet names over aliases.

---

# Variables

```powershell
$name = 'example'
```

Display:

```powershell
$name
```

List variables:

```powershell
Get-Variable
```

Remove:

```powershell
Remove-Variable name
```

---

# Objects

PowerShell passes objects through the pipeline rather than plain text wherever possible.

Example:

```powershell
Get-Service |
    Get-Member
```

Properties:

```powershell
Get-Service |
    Select-Object Name,Status
```

---

# Pipeline

```powershell
Get-Service |
    Where-Object Status -eq 'Running' |
    Select-Object Name,Status
```

Conceptually:

```text
Command
   |
   v
Objects
   |
   v
Filter
   |
   v
Select
   |
   v
Output
```

---

# Filtering

```powershell
Get-Service |
    Where-Object Status -eq 'Running'
```

Using script block:

```powershell
Get-Process |
    Where-Object {
        $_.CPU -gt 10
    }
```

---

# Selecting Properties

```powershell
Get-Process |
    Select-Object Name,Id,CPU
```

First five:

```powershell
Get-Process |
    Select-Object -First 5
```

Unique:

```powershell
Get-Process |
    Select-Object ProcessName -Unique
```

---

# Sorting

```powershell
Get-Process |
    Sort-Object CPU -Descending
```

---

# Grouping

```powershell
Get-Service |
    Group-Object Status
```

---

# Measuring

```powershell
Get-Process |
    Measure-Object
```

CPU:

```powershell
Get-Process |
    Measure-Object CPU -Sum -Average
```

---

# Formatting

Table:

```powershell
Get-Service |
    Format-Table Name,Status
```

List:

```powershell
Get-Service WinRM |
    Format-List *
```

Use formatting cmdlets primarily at the end of interactive pipelines.

Avoid inserting `Format-Table` or `Format-List` in the middle of data-processing pipelines.

---

# Files

List:

```powershell
Get-ChildItem
```

Hidden:

```powershell
Get-ChildItem -Force
```

Specific path:

```powershell
Get-ChildItem C:\Temp
```

Recursive:

```powershell
Get-ChildItem C:\Temp -Recurse
```

Files only:

```powershell
Get-ChildItem C:\Temp -File
```

Directories:

```powershell
Get-ChildItem C:\Temp -Directory
```

---

# Create Directory

```powershell
New-Item -ItemType Directory -Path C:\Temp\Test
```

---

# Create File

```powershell
New-Item -ItemType File -Path C:\Temp\test.txt
```

---

# Write File

```powershell
Set-Content -Path C:\Temp\test.txt -Value 'test'
```

Append:

```powershell
Add-Content -Path C:\Temp\test.txt -Value 'another line'
```

---

# Read File

```powershell
Get-Content C:\Temp\test.txt
```

First ten lines:

```powershell
Get-Content C:\Temp\test.txt -TotalCount 10
```

Last ten:

```powershell
Get-Content C:\Temp\test.txt -Tail 10
```

Follow:

```powershell
Get-Content C:\Temp\log.txt -Wait
```

---

# Copy File

```powershell
Copy-Item C:\Temp\source.txt C:\Temp\destination.txt
```

Recursive:

```powershell
Copy-Item C:\Source C:\Destination -Recurse
```

---

# Move File

```powershell
Move-Item C:\Temp\old.txt C:\Temp\new.txt
```

---

# Delete File

```powershell
Remove-Item C:\Temp\test.txt
```

Recursive directory:

```powershell
Remove-Item C:\Temp\Test -Recurse
```

Be cautious with:

```powershell
-Recurse
-Force
```

especially on production systems.

---

# Test Path

```powershell
Test-Path C:\Temp\test.txt
```

Directory:

```powershell
Test-Path C:\Temp -PathType Container
```

File:

```powershell
Test-Path C:\Temp\test.txt -PathType Leaf
```

---

# Resolve Path

```powershell
Resolve-Path C:\Temp
```

---

# File Metadata

```powershell
Get-Item C:\Temp\test.txt |
    Format-List *
```

Useful:

```powershell
Get-Item C:\Temp\test.txt |
    Select-Object FullName,Length,CreationTime,LastWriteTime
```

---

# File Hash

```powershell
Get-FileHash C:\Temp\file.exe
```

SHA-256 explicitly:

```powershell
Get-FileHash C:\Temp\file.exe -Algorithm SHA256
```

---

# File Version

```powershell
(Get-Item C:\Path\application.exe).VersionInfo
```

Useful:

```powershell
(Get-Item C:\Path\application.exe).VersionInfo |
    Select-Object FileVersion,ProductVersion,CompanyName,FileDescription
```

---

# Authenticode Signature

```powershell
Get-AuthenticodeSignature C:\Path\application.exe
```

Useful:

```powershell
Get-AuthenticodeSignature C:\Path\application.exe |
    Select-Object Status,StatusMessage,SignerCertificate
```

---

# Search Files

By name:

```powershell
Get-ChildItem C:\Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Name -like '*config*'
```

Using filter:

```powershell
Get-ChildItem C:\Path -Recurse -Filter '*.config' -ErrorAction SilentlyContinue
```

---

# Search File Contents

```powershell
Select-String -Path C:\Path\file.txt -Pattern 'text'
```

Recursive:

```powershell
Get-ChildItem C:\Path -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','secret','token'
```

Prefer targeted paths to avoid unnecessary access to sensitive data.

---

# Recently Modified Files

Last 24 hours:

```powershell
$since = (Get-Date).AddDays(-1)

Get-ChildItem C:\Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object LastWriteTime -gt $since
```

---

# Large Files

Files larger than 100 MB:

```powershell
Get-ChildItem C:\Path -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Length -gt 100MB |
    Select-Object FullName,Length
```

---

# ACLs

File:

```powershell
Get-Acl C:\Path\file.exe
```

Detailed:

```powershell
Get-Acl C:\Path\file.exe |
    Format-List
```

Access entries:

```powershell
(Get-Acl C:\Path\file.exe).Access
```

Directory:

```powershell
Get-Acl C:\Path
```

---

# ACL Review

```powershell
(Get-Acl C:\Path).Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited
```

Look for identities such as:

```text
Everyone
BUILTIN\Users
Authenticated Users
Current User
Current User's Groups
```

and rights such as:

```text
Write
Modify
FullControl
WriteData
CreateFiles
```

Interpret inherited and explicit permissions together.

---

# Writable Location Validation

First inspect permissions:

```powershell
Get-Acl C:\Path |
    Format-List
```

A writable directory is not automatically a vulnerability.

The important relationship is:

```text
Low-Privilege Write Access
          +
Privileged Consumer
          =
Potential Security Boundary
```

If a real write test is necessary, create a uniquely named temporary file and remove it immediately.

---

# Registry

List:

```powershell
Get-ChildItem HKLM:\
```

Specific:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft'
```

---

# Read Registry Value

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
```

Specific value:

```powershell
Get-ItemPropertyValue `
    -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' `
    -Name 'ProductName'
```

---

# Registry ACL

```powershell
Get-Acl 'HKLM:\SOFTWARE\Vendor\Product'
```

Detailed:

```powershell
(Get-Acl 'HKLM:\SOFTWARE\Vendor\Product').Access
```

---

# Registry Search

Prefer targeted application keys.

Example:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Vendor' -Recurse -ErrorAction SilentlyContinue
```

Do not blindly search the entire registry for secrets unless the assessment requires it.

---

# Host Information

```powershell
hostname
```

Detailed:

```powershell
Get-ComputerInfo
```

OS:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber,OSArchitecture
```

Computer:

```powershell
Get-CimInstance Win32_ComputerSystem
```

---

# Windows Build

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' |
    Select-Object ProductName,DisplayVersion,CurrentBuild,UBR
```

---

# Installed Hotfixes

```powershell
Get-HotFix
```

Newest first:

```powershell
Get-HotFix |
    Sort-Object InstalledOn -Descending
```

Do not determine vulnerability status from a KB list alone.

Modern Windows uses cumulative servicing.

---

# Last Boot

```powershell
(Get-CimInstance Win32_OperatingSystem).LastBootUpTime
```

---

# Local Users

```powershell
Get-LocalUser
```

Detailed:

```powershell
Get-LocalUser |
    Select-Object Name,Enabled,LastLogon,PasswordRequired,PasswordExpires
```

Specific:

```powershell
Get-LocalUser -Name Administrator
```

---

# Local Groups

```powershell
Get-LocalGroup
```

Members:

```powershell
Get-LocalGroupMember -Group Administrators
```

Group names may be localised.

For cross-language automation, SID-based approaches can be more reliable.

---

# Current Groups

```powershell
whoami /groups
```

---

# Current Privileges

```powershell
whoami /priv
```

Security-sensitive privileges can include:

```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeRestorePrivilege
SeTakeOwnershipPrivilege
SeDebugPrivilege
SeLoadDriverPrivilege
SeManageVolumePrivilege
```

Presence alone is not proof of exploitability.

---

# Processes

```powershell
Get-Process
```

Specific:

```powershell
Get-Process -Id 1234
```

By name:

```powershell
Get-Process -Name explorer
```

Useful:

```powershell
Get-Process |
    Select-Object Name,Id,Path
```

Some process properties require additional permissions.

---

# Process Command Lines

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,CommandLine
```

Specific:

```powershell
Get-CimInstance Win32_Process -Filter 'ProcessId=1234' |
    Select-Object *
```

---

# Process Owner

```powershell
Get-CimInstance Win32_Process |
    ForEach-Object {
        $owner = Invoke-CimMethod -InputObject $_ -MethodName GetOwner -ErrorAction SilentlyContinue

        [PSCustomObject]@{
            PID     = $_.ProcessId
            Process = $_.Name
            User    = if ($owner.User) {
                "$($owner.Domain)\$($owner.User)"
            } else {
                $null
            }
        }
    }
```

Permissions can limit owner information.

---

# Services

```powershell
Get-Service
```

Running:

```powershell
Get-Service |
    Where-Object Status -eq 'Running'
```

Specific:

```powershell
Get-Service WinRM
```

---

# Service Configuration

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,StartMode,PathName
```

Specific:

```powershell
Get-CimInstance Win32_Service -Filter "Name='WinRM'"
```

---

# Service Analysis

```text
Service
   |
   +--> Account
   +--> Executable
   +--> Directory
   +--> Configuration
   +--> ACL
```

A useful review:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```

Then inspect relevant ACLs:

```powershell
Get-Acl 'C:\Path\service.exe'
Get-Acl 'C:\Path'
```

---

# Unquoted Service Paths

Candidate enumeration:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -match ' ' -and
        $_.PathName -notmatch '^"'
    } |
    Select-Object Name,StartName,State,PathName
```

This identifies candidates only.

A classic security issue additionally requires a writable candidate path and a higher-privileged service context.

---

# Scheduled Tasks

```powershell
Get-ScheduledTask
```

Useful:

```powershell
Get-ScheduledTask |
    Select-Object TaskPath,TaskName,State
```

Actions:

```powershell
Get-ScheduledTask |
    ForEach-Object {
        [PSCustomObject]@{
            TaskPath  = $_.TaskPath
            TaskName  = $_.TaskName
            Executable = ($_.Actions.Execute -join '; ')
            Arguments  = ($_.Actions.Arguments -join '; ')
        }
    }
```

---

# Scheduled Task Information

```powershell
Get-ScheduledTaskInfo -TaskName 'TaskName'
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
ACL
```

The important condition is:

```text
Privileged Task
      +
Low-Privilege Writable Dependency
```

---

# Network Configuration

```powershell
Get-NetIPConfiguration
```

Addresses:

```powershell
Get-NetIPAddress
```

IPv4:

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

---

# Routes

```powershell
Get-NetRoute
```

IPv4:

```powershell
Get-NetRoute -AddressFamily IPv4 |
    Sort-Object RouteMetric
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

```powershell
Resolve-DnsName example.com
```

A record:

```powershell
Resolve-DnsName example.com -Type A
```

MX:

```powershell
Resolve-DnsName example.com -Type MX
```

TXT:

```powershell
Resolve-DnsName example.com -Type TXT
```

---

# TCP Connections

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

---

# UDP

```powershell
Get-NetUDPEndpoint
```

---

# Map Network Connection to Process

```powershell
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Then:

```powershell
Get-Process -Id 1234
```

Combined:

```powershell
Get-NetTCPConnection -State Listen |
    ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue

        [PSCustomObject]@{
            Address = $_.LocalAddress
            Port    = $_.LocalPort
            PID     = $_.OwningProcess
            Process = $process.ProcessName
        }
    }
```

---

# Test Connectivity

```powershell
Test-NetConnection example.com
```

TCP:

```powershell
Test-NetConnection example.com -Port 443
```

Boolean:

```powershell
Test-NetConnection example.com -Port 443 -InformationLevel Quiet
```

---

# Common Port Tests

SMB:

```powershell
Test-NetConnection server.example.local -Port 445
```

RDP:

```powershell
Test-NetConnection server.example.local -Port 3389
```

WinRM HTTP:

```powershell
Test-NetConnection server.example.local -Port 5985
```

WinRM HTTPS:

```powershell
Test-NetConnection server.example.local -Port 5986
```

HTTPS:

```powershell
Test-NetConnection example.com -Port 443
```

---

# SMB Shares

Local:

```powershell
Get-SmbShare
```

Mappings:

```powershell
Get-SmbMapping
```

Server configuration:

```powershell
Get-SmbServerConfiguration
```

Client:

```powershell
Get-SmbClientConfiguration
```

---

# Firewall

Profiles:

```powershell
Get-NetFirewallProfile
```

Rules:

```powershell
Get-NetFirewallRule
```

Enabled:

```powershell
Get-NetFirewallRule |
    Where-Object Enabled -eq 'True'
```

Allow rules:

```powershell
Get-NetFirewallRule |
    Where-Object {
        $_.Enabled -eq 'True' -and
        $_.Action -eq 'Allow'
    }
```

---

# HTTP Requests

GET:

```powershell
Invoke-WebRequest -Uri 'https://example.com/'
```

Store response:

```powershell
$response = Invoke-WebRequest -Uri 'https://example.com/'
```

Status:

```powershell
$response.StatusCode
```

Headers:

```powershell
$response.Headers
```

Content:

```powershell
$response.Content
```

---

# Download File

```powershell
Invoke-WebRequest `
    -Uri 'https://example.com/file.txt' `
    -OutFile 'C:\Temp\file.txt'
```

Alias:

```powershell
iwr 'https://example.com/file.txt' -OutFile 'C:\Temp\file.txt'
```

Use only trusted sources and authorised destinations.

---

# REST APIs

GET:

```powershell
Invoke-RestMethod -Uri 'https://example.com/api'
```

JSON response objects can often be used directly:

```powershell
$response = Invoke-RestMethod -Uri 'https://example.com/api'
$response
```

---

# POST JSON

```powershell
$body = @{
    name = 'example'
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri 'https://example.com/api' `
    -Method Post `
    -ContentType 'application/json' `
    -Body $body
```

Use only against authorised APIs.

---

# Headers

```powershell
$headers = @{
    'X-Test' = 'value'
}

Invoke-WebRequest `
    -Uri 'https://example.com/' `
    -Headers $headers
```

---

# Proxy

WinHTTP configuration:

```powershell
netsh winhttp show proxy
```

Environment:

```powershell
Get-ChildItem Env: |
    Where-Object Name -match 'proxy'
```

---

# Base64

Encode UTF-8:

```powershell
$text = 'test'

$bytes = [Text.Encoding]::UTF8.GetBytes($text)

[Convert]::ToBase64String($bytes)
```

Decode:

```powershell
$encoded = 'dGVzdA=='

$bytes = [Convert]::FromBase64String($encoded)

[Text.Encoding]::UTF8.GetString($bytes)
```

---

# PowerShell EncodedCommand

PowerShell's `-EncodedCommand` expects Base64 representing UTF-16LE command text.

Create an encoded command:

```powershell
$command = 'Get-Date'

$bytes = [Text.Encoding]::Unicode.GetBytes($command)

$encoded = [Convert]::ToBase64String($bytes)

$encoded
```

Decode for analysis:

```powershell
$bytes = [Convert]::FromBase64String($encoded)

[Text.Encoding]::Unicode.GetString($bytes)
```

Encoded commands are not encryption.

They are frequently used for legitimate automation as well as malicious activity.

InternalAllTheThings also highlights the UTF-16LE requirement for PowerShell encoded commands.

---

# JSON

Object to JSON:

```powershell
Get-Process -Id $PID |
    Select-Object Name,Id |
    ConvertTo-Json
```

JSON to object:

```powershell
'{"name":"test","id":1}' |
    ConvertFrom-Json
```

---

# CSV

Export:

```powershell
Get-Service |
    Select-Object Name,Status |
    Export-Csv C:\Temp\services.csv -NoTypeInformation
```

Import:

```powershell
Import-Csv C:\Temp\services.csv
```

---

# XML

```powershell
[xml]$xml = Get-Content C:\Temp\file.xml
```

Then:

```powershell
$xml
```

---

# Convert Output to Text

```powershell
Get-Service |
    Out-String
```

Useful when capturing command output programmatically.

---

# Clipboard

Copy:

```powershell
'text' | Set-Clipboard
```

Read:

```powershell
Get-Clipboard
```

Avoid copying sensitive credentials to the clipboard during assessments.

---

# PowerShell Modules

List available:

```powershell
Get-Module -ListAvailable
```

Loaded:

```powershell
Get-Module
```

Import:

```powershell
Import-Module ModuleName
```

Remove:

```powershell
Remove-Module ModuleName
```

---

# Module Commands

```powershell
Get-Command -Module Microsoft.PowerShell.Management
```

---

# PowerShell Profiles

Profile path:

```powershell
$PROFILE
```

All profile paths:

```powershell
$PROFILE |
    Format-List *
```

Existence:

```powershell
Test-Path $PROFILE
```

Read:

```powershell
Get-Content $PROFILE -ErrorAction SilentlyContinue
```

Profiles can execute PowerShell code automatically when specific PowerShell hosts start.

Unexpected write permissions on another user's or a privileged execution context's profile should be investigated.

---

# Execution Policy

View:

```powershell
Get-ExecutionPolicy
```

All scopes:

```powershell
Get-ExecutionPolicy -List
```

Common values:

```text
Restricted
AllSigned
RemoteSigned
Unrestricted
Bypass
Undefined
```

Important:

```text
Execution Policy
       !=
Security Boundary
```

Execution Policy is intended primarily as a safety feature controlling script execution behaviour.

Do not treat it as equivalent to AppLocker or WDAC.

---

# Language Mode

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

---

# FullLanguage

`FullLanguage` provides the normal PowerShell language capabilities.

It is common on ordinary Windows systems.

Do not automatically report:

```text
LanguageMode = FullLanguage
```

as a vulnerability.

Instead determine whether the endpoint's intended security architecture requires application control and PowerShell restrictions for untrusted users.

---

# Constrained Language Mode

Constrained Language Mode restricts access to certain PowerShell language features and .NET capabilities.

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

A result such as:

```text
ConstrainedLanguage
```

should be evaluated together with:

```text
AppLocker
WDAC / App Control
PowerShell Version
Security Product
Policy Scope
```

Do not attempt to bypass Constrained Language Mode merely to test whether it can be bypassed unless explicitly authorised.

---

# InternalAllTheThings and Constrained Mode

InternalAllTheThings includes historical PowerShell constrained-mode techniques.

Treat historical techniques carefully.

For modern Windows environments, validate:

```text
Windows Version
PowerShell Version
WDAC/AppLocker
Patch State
Current Microsoft Behaviour
```

before drawing conclusions.

---

# AppLocker

Effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

Collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```

XML:

```powershell
Get-AppLockerPolicy -Effective -Xml
```

---

# Test AppLocker Policy

Executable:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy `
        -Path 'C:\Path\candidate.exe' `
        -User "$env:USERDOMAIN\$env:USERNAME"
```

Script:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy `
        -Path 'C:\Path\candidate.ps1' `
        -User "$env:USERDOMAIN\$env:USERNAME"
```

This is preferable to executing a candidate merely to discover whether policy allows it.

---

# AppLocker Collections

Common collections:

```text
Exe
Msi
Script
Dll
Appx
```

Interpret:

```text
NotConfigured
```

carefully.

Another application-control layer such as WDAC may still enforce restrictions.

---

# AppLocker Events

EXE and DLL:

```powershell
Get-WinEvent `
    -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' `
    -MaxEvents 50
```

MSI and Script:

```powershell
Get-WinEvent `
    -LogName 'Microsoft-Windows-AppLocker/MSI and Script' `
    -MaxEvents 50
```

---

# Code Integrity Events

```powershell
Get-WinEvent `
    -LogName 'Microsoft-Windows-CodeIntegrity/Operational' `
    -MaxEvents 50
```

Useful when analysing application-control decisions.

---

# Defender Status

```powershell
Get-MpComputerStatus
```

Useful:

```powershell
Get-MpComputerStatus |
    Select-Object `
        AntivirusEnabled,
        RealTimeProtectionEnabled,
        BehaviorMonitorEnabled,
        IoavProtectionEnabled,
        AMProductVersion,
        AMEngineVersion,
        AntivirusSignatureVersion,
        AntivirusSignatureLastUpdated
```

---

# Defender Preferences

```powershell
Get-MpPreference
```

---

# Defender Exclusions

```powershell
Get-MpPreference |
    Select-Object ExclusionPath,ExclusionProcess,ExclusionExtension
```

Do not modify exclusions during routine enumeration.

An exclusion requires context before it should be reported as a security issue.

---

# Attack Surface Reduction

```powershell
Get-MpPreference |
    Select-Object `
        AttackSurfaceReductionRules_Ids,
        AttackSurfaceReductionRules_Actions
```

---

# PowerShell Logging

PowerShell security visibility can include:

```text
Script Block Logging
Module Logging
Transcription
Process Creation Logging
AMSI Integration
```

---

# Script Block Logging

Policy:

```powershell
Get-ItemProperty `
    'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' `
    -ErrorAction SilentlyContinue
```

Events are commonly found in:

```text
Microsoft-Windows-PowerShell/Operational
```

Query:

```powershell
Get-WinEvent `
    -LogName 'Microsoft-Windows-PowerShell/Operational' `
    -MaxEvents 50
```

---

# Module Logging

```powershell
Get-ItemProperty `
    'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging' `
    -ErrorAction SilentlyContinue
```

---

# Transcription

```powershell
Get-ItemProperty `
    'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription' `
    -ErrorAction SilentlyContinue
```

Transcripts can contain sensitive command output and should be protected appropriately.

---

# PSReadLine History

Path:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Read:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

Search:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath |
    Select-String -Pattern 'password','secret','token'
```

Treat discovered secrets as sensitive evidence.

History is not a complete audit trail.

---

# Event Logs

List:

```powershell
Get-WinEvent -ListLog *
```

System:

```powershell
Get-WinEvent -LogName System -MaxEvents 50
```

Application:

```powershell
Get-WinEvent -LogName Application -MaxEvents 50
```

Security:

```powershell
Get-WinEvent -LogName Security -MaxEvents 50
```

Security-log access can require elevated rights.

---

# Filter Event ID

Example:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id      = 4624
} -MaxEvents 20
```

---

# Filter by Time

```powershell
$start = (Get-Date).AddHours(-1)

Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = $start
}
```

---

# Common Windows Security Events

| Event ID | Description |
|---:|---|
| 4624 | Successful logon |
| 4625 | Failed logon |
| 4648 | Logon using explicit credentials |
| 4672 | Special privileges assigned to a new logon |
| 4688 | New process created |
| 4697 | Service installed |
| 4698 | Scheduled task created |
| 4702 | Scheduled task updated |
| 4720 | User account created |
| 4728 | Member added to global security group |
| 4732 | Member added to local security group |

Event availability depends on audit policy.

---

# Services from Event Logs

System service installation events can include Event ID:

```text
7045
```

Query:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    Id      = 7045
} -MaxEvents 20
```

---

# Remoting

WinRM service:

```powershell
Get-Service WinRM
```

Configuration:

```powershell
winrm get winrm/config
```

Listeners:

```powershell
winrm enumerate winrm/config/listener
```

PowerShell remoting configuration:

```powershell
Get-PSSessionConfiguration
```

---

# Test WinRM

HTTP:

```powershell
Test-NetConnection server.example.local -Port 5985
```

HTTPS:

```powershell
Test-NetConnection server.example.local -Port 5986
```

---

# Remote Command

For authorised administration:

```powershell
Invoke-Command `
    -ComputerName server.example.local `
    -ScriptBlock {
        hostname
    }
```

PowerShell remoting requires appropriate authentication, authorisation and WinRM configuration.

---

# Interactive Remote Session

```powershell
Enter-PSSession -ComputerName server.example.local
```

Exit:

```powershell
Exit-PSSession
```

---

# Sessions

```powershell
Get-PSSession
```

Remove:

```powershell
Remove-PSSession -Id 1
```

---

# CIM

Local OS:

```powershell
Get-CimInstance Win32_OperatingSystem
```

Services:

```powershell
Get-CimInstance Win32_Service
```

Processes:

```powershell
Get-CimInstance Win32_Process
```

---

# Remote CIM

Where authorised and configured:

```powershell
Get-CimInstance `
    -ClassName Win32_OperatingSystem `
    -ComputerName server.example.local
```

Modern environments may require explicit CIM sessions depending on authentication and transport configuration.

---

# Installed Software

Avoid `Win32_Product` for routine inventory because querying it can have undesirable side effects on MSI-installed applications.

Prefer uninstall registry keys:

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

---

# Windows Features

On supported Windows clients:

```powershell
Get-WindowsOptionalFeature -Online
```

Enabled:

```powershell
Get-WindowsOptionalFeature -Online |
    Where-Object State -eq 'Enabled'
```

Windows Server:

```powershell
Get-WindowsFeature
```

when the ServerManager module is available.

---

# Domain Membership

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```

---

# Logon Server

```powershell
$env:LOGONSERVER
```

---

# Domain Information

If the ActiveDirectory module is installed:

```powershell
Get-ADDomain
```

Forest:

```powershell
Get-ADForest
```

---

# Active Directory Module

Check:

```powershell
Get-Module -ListAvailable ActiveDirectory
```

Import:

```powershell
Import-Module ActiveDirectory
```

---

# Current Domain

```powershell
Get-ADDomain
```

---

# Domain Controllers

```powershell
Get-ADDomainController -Filter *
```

Useful:

```powershell
Get-ADDomainController -Filter * |
    Select-Object HostName,IPv4Address,Site,IsGlobalCatalog
```

---

# AD Users

```powershell
Get-ADUser -Filter *
```

Specific:

```powershell
Get-ADUser username
```

Useful properties:

```powershell
Get-ADUser username -Properties * |
    Select-Object `
        SamAccountName,
        Enabled,
        DistinguishedName,
        MemberOf,
        LastLogonDate,
        PasswordLastSet
```

---

# AD Groups

```powershell
Get-ADGroup -Filter *
```

Members:

```powershell
Get-ADGroupMember 'Domain Admins'
```

---

# AD Computers

```powershell
Get-ADComputer -Filter *
```

Useful:

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem |
    Select-Object Name,DNSHostName,OperatingSystem
```

---

# Group Membership

```powershell
Get-ADPrincipalGroupMembership username
```

---

# Search AD

Example:

```powershell
Get-ADUser -Filter "Name -like '*admin*'"
```

Use targeted searches to reduce unnecessary directory queries.

For comprehensive AD testing, use the dedicated Active Directory notes and cheatsheet rather than treating this PowerShell page as a replacement.

---

# SecureString

Prompt:

```powershell
$secure = Read-Host 'Password' -AsSecureString
```

Credential:

```powershell
$credential = Get-Credential
```

Username:

```powershell
$credential.UserName
```

---

# SecureString Security Note

`SecureString` should not be treated as a universal encrypted-secret storage solution.

Its behaviour and security properties depend on the platform and how it is persisted.

Do not convert protected secrets to plaintext merely for convenience during an assessment.

InternalAllTheThings includes SecureString-to-plaintext handling, but credential disclosure should only be performed where explicitly required and authorised.

---

# PSCredential

Interactive:

```powershell
$credential = Get-Credential
```

Use with supported cmdlets:

```powershell
Invoke-Command `
    -ComputerName server.example.local `
    -Credential $credential `
    -ScriptBlock {
        hostname
    }
```

Avoid embedding plaintext passwords directly in scripts.

---

# Date and Time

```powershell
Get-Date
```

Custom:

```powershell
Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
```

Add time:

```powershell
(Get-Date).AddDays(-7)
```

---

# Random Values

```powershell
Get-Random
```

Range:

```powershell
Get-Random -Minimum 1 -Maximum 100
```

GUID:

```powershell
[guid]::NewGuid()
```

Useful temporary filename:

```powershell
$testFile = Join-Path $env:TEMP "test-$([guid]::NewGuid()).tmp"
```

---

# Strings

Length:

```powershell
'example'.Length
```

Uppercase:

```powershell
'example'.ToUpper()
```

Lowercase:

```powershell
'EXAMPLE'.ToLower()
```

Replace:

```powershell
'hello world' -replace 'world','PowerShell'
```

Split:

```powershell
'a,b,c' -split ','
```

Join:

```powershell
'a','b','c' -join ','
```

---

# Regex

Match:

```powershell
'server01.example.local' -match '^server'
```

Extract:

```powershell
'User: alice' -match 'User:\s+(.+)'

$Matches[1]
```

---

# Arrays

```powershell
$items = @(
    'one'
    'two'
    'three'
)
```

Loop:

```powershell
foreach ($item in $items) {
    $item
}
```

---

# Hashtables

```powershell
$data = @{
    Host = 'server01'
    Port = 443
}
```

Read:

```powershell
$data.Host
```

---

# Custom Objects

```powershell
[PSCustomObject]@{
    Host = $env:COMPUTERNAME
    User = $env:USERNAME
    Time = Get-Date
}
```

---

# Functions

```powershell
function Get-Test {
    param(
        [string]$Name
    )

    "Hello $Name"
}
```

Use:

```powershell
Get-Test -Name 'Asif'
```

---

# Error Handling

```powershell
try {
    Get-Item 'C:\does-not-exist' -ErrorAction Stop
}
catch {
    Write-Warning $_.Exception.Message
}
```

---

# ErrorAction

Silently continue:

```powershell
Get-Item 'C:\does-not-exist' -ErrorAction SilentlyContinue
```

Stop:

```powershell
Get-Item 'C:\does-not-exist' -ErrorAction Stop
```

---

# Last Error

```powershell
$Error[0]
```

Clear:

```powershell
$Error.Clear()
```

---

# Background Jobs

```powershell
Start-Job -ScriptBlock {
    Get-Date
}
```

List:

```powershell
Get-Job
```

Receive:

```powershell
Receive-Job -Id 1
```

Remove:

```powershell
Remove-Job -Id 1
```

---

# Output Redirection

To file:

```powershell
Get-Service > C:\Temp\services.txt
```

Append:

```powershell
Get-Service >> C:\Temp\services.txt
```

Better structured output:

```powershell
Get-Service |
    Export-Csv C:\Temp\services.csv -NoTypeInformation
```

---

# Tee

```powershell
Get-Service |
    Tee-Object -FilePath C:\Temp\services.txt
```

---

# Null Output

```powershell
Get-Service | Out-Null
```

or:

```powershell
$null = Get-Service
```

---

# Transcript

Start:

```powershell
Start-Transcript -Path C:\Temp\session.txt
```

Stop:

```powershell
Stop-Transcript
```

Only record assessment sessions where doing so is permitted, because transcripts may capture sensitive data.

---

# Evidence Collection

A useful object:

```powershell
[PSCustomObject]@{
    Timestamp = Get-Date
    Computer  = $env:COMPUTERNAME
    User      = "$env:USERDOMAIN\$env:USERNAME"
}
```

Export:

```powershell
$evidence = [PSCustomObject]@{
    Timestamp = Get-Date
    Computer  = $env:COMPUTERNAME
    User      = "$env:USERDOMAIN\$env:USERNAME"
}

$evidence |
    Export-Csv C:\Temp\evidence.csv -NoTypeInformation
```

---

# Redact Secrets

Avoid including:

```text
Passwords
Private Keys
Access Tokens
Session Tokens
API Keys
Credential Hashes
Recovery Keys
```

in screenshots or reports unless strictly necessary.

Prefer:

```text
Secret Present
Value Redacted
Current User Has Read Access
```

---

# PowerShell Security Assessment Flow

```text
PowerShell Version
       |
       v
Execution Policy
       |
       v
Language Mode
       |
       v
Logging
       |
       v
AMSI / Defender Context
       |
       v
AppLocker / WDAC
       |
       v
Effective Restrictions
```

No single item provides the full security picture.

---

# Execution Policy vs Application Control

```text
Execution Policy
       |
       +--> Script Safety / User Intent

AppLocker / WDAC
       |
       +--> Application Control

Language Mode
       |
       +--> PowerShell Language Restrictions

Defender / AMSI
       |
       +--> Content Inspection / Detection
```

Do not treat these as interchangeable controls.

---

# Encoded Commands

InternalAllTheThings highlights PowerShell encoded-command handling.

For assessment and incident response, decoding an observed command is often more useful than executing it.

Decode:

```powershell
$encoded = 'RwBlAHQALQBEAGEAdABlAA=='

[Text.Encoding]::Unicode.GetString(
    [Convert]::FromBase64String($encoded)
)
```

Use:

```text
Decode
  |
  v
Inspect
  |
  v
Understand
```

rather than executing unknown encoded content.

---

# Script Loading

Import a trusted local script:

```powershell
. C:\Path\script.ps1
```

This is dot-sourcing and places functions/variables from the script into the current scope.

Module:

```powershell
Import-Module C:\Path\module.psm1
```

Before loading third-party scripts:

```powershell
Get-FileHash C:\Path\script.ps1
Get-AuthenticodeSignature C:\Path\script.ps1
```

Only execute assessment tooling where explicitly permitted.

---

# Reflection and .NET

PowerShell can access .NET directly.

Example:

```powershell
[Environment]::MachineName
```

Loaded assemblies:

```powershell
[AppDomain]::CurrentDomain.GetAssemblies() |
    Select-Object FullName,Location
```

This capability is legitimate and widely used by administration and development tooling.

It is also one reason application-control and PowerShell security architecture should be assessed as a whole.

This cheatsheet intentionally does not include shellcode runners or memory-execution examples.

---

# CIM vs WMI

Prefer modern CIM cmdlets where practical:

```powershell
Get-CimInstance Win32_OperatingSystem
```

rather than older:

```text
Get-WmiObject
```

`Get-WmiObject` belongs to Windows PowerShell and is not available in the same way in modern cross-platform PowerShell.

---

# Quick Enumeration

```powershell
whoami
whoami /all

$PSVersionTable
$ExecutionContext.SessionState.LanguageMode
Get-ExecutionPolicy -List

Get-ComputerInfo

Get-LocalUser
Get-LocalGroup

Get-Process

Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName

Get-ScheduledTask

Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection -State Listen

Get-NetFirewallProfile

Get-MpComputerStatus
```

---

# Security Quick Check

```powershell
$PSVersionTable
$ExecutionContext.SessionState.LanguageMode
Get-ExecutionPolicy -List

Get-MpComputerStatus
Get-MpPreference

Get-NetFirewallProfile

Get-AppLockerPolicy -Effective

Get-WinEvent `
    -LogName 'Microsoft-Windows-PowerShell/Operational' `
    -MaxEvents 20

Get-WinEvent `
    -LogName 'Microsoft-Windows-CodeIntegrity/Operational' `
    -MaxEvents 20
```

---

# Privilege Quick Check

```powershell
whoami /all
whoami /priv

Get-LocalGroupMember -Group Administrators

Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName

Get-ScheduledTask

Get-ChildItem Env:
```

Then investigate permissions only where a more-privileged component creates a meaningful trust relationship.

---

# PowerShell Checklist

## Environment

- [ ] Identify PowerShell version
- [ ] Identify PowerShell edition
- [ ] Identify executable
- [ ] Review environment variables
- [ ] Review PATH
- [ ] Review profiles
- [ ] Review loaded modules

## Identity

- [ ] Current user
- [ ] SID
- [ ] Groups
- [ ] Privileges
- [ ] Administrator context
- [ ] Domain membership

## System

- [ ] Windows version
- [ ] Build
- [ ] Architecture
- [ ] Hotfixes
- [ ] Installed software
- [ ] Windows features

## Processes

- [ ] Enumerate processes
- [ ] Review command lines
- [ ] Review parent PIDs
- [ ] Review process owners where relevant
- [ ] Identify security software

## Services

- [ ] Enumerate services
- [ ] Review service accounts
- [ ] Review executable paths
- [ ] Review unquoted path candidates
- [ ] Review relevant ACLs
- [ ] Review writable dependencies

## Scheduled Tasks

- [ ] Enumerate tasks
- [ ] Review actions
- [ ] Review execution identities
- [ ] Review executable/script ACLs
- [ ] Review writable dependencies

## Network

- [ ] IP configuration
- [ ] Routes
- [ ] DNS
- [ ] TCP listeners
- [ ] UDP listeners
- [ ] Established connections
- [ ] Firewall
- [ ] Proxy

## Files

- [ ] Review relevant application directories
- [ ] Review configuration
- [ ] Review ACLs
- [ ] Search targeted files
- [ ] Review hashes/signatures where relevant
- [ ] Review PowerShell history where authorised

## Registry

- [ ] Review relevant application keys
- [ ] Review autoruns where applicable
- [ ] Review ACLs
- [ ] Avoid unnecessary broad secret searches

## PowerShell Security

- [ ] Execution Policy
- [ ] Language Mode
- [ ] Script Block Logging
- [ ] Module Logging
- [ ] Transcription
- [ ] PowerShell Operational log
- [ ] Defender
- [ ] ASR
- [ ] AppLocker
- [ ] Code Integrity / WDAC context

## Active Directory

- [ ] Check domain membership
- [ ] Check AD module
- [ ] Enumerate domain where relevant
- [ ] Enumerate DCs
- [ ] Use dedicated AD notes for deeper testing

## Evidence

- [ ] Record exact command
- [ ] Record timestamp
- [ ] Record hostname
- [ ] Record user
- [ ] Capture only relevant output
- [ ] Redact credentials
- [ ] Record any state changes
- [ ] Remove temporary files

---

# Do Not Overreport

Do not automatically report:

```text
PowerShell Installed
PowerShell 5.1 Present
FullLanguage Mode
ExecutionPolicy Bypass at Process Scope
Encoded PowerShell Exists
Invoke-WebRequest Available
.NET Accessible
AppLocker Collection NotConfigured
PSRemoting Installed
PowerShell History Exists
```

Instead ask:

```text
What Security Boundary
Was Supposed to Exist?
        |
        v
Can This User Cross It?
```

---

# Safe Validation Model

Prefer:

```text
Read Configuration
       |
       v
Read ACL
       |
       v
Read Effective Policy
       |
       v
Test Policy Decision
       |
       v
Document Result
```

before:

```text
Change Policy
Execute Untrusted Binary
Disable Defender
Modify AppLocker
Modify Registry
Change Service
Create Persistence
```

---

# Common Mistakes

Avoid:

```powershell
Get-CimInstance Win32_Product
```

for routine software inventory when registry-based inventory is sufficient.

Avoid broad recursive searches such as:

```text
Search every file on C: for "password"
```

without a clear reason.

Avoid assuming:

```text
FullLanguage = Vulnerable
```

or:

```text
ExecutionPolicy Restricted = Secure
```

or:

```text
EncodedCommand = Malicious
```

or:

```text
AppLocker Rule Allows Binary = Exploitable
```

Context matters.

---

# Quick Reference

```powershell
# Identity
whoami
whoami /all
whoami /priv
whoami /groups

# PowerShell
$PSVersionTable
Get-ExecutionPolicy -List
$ExecutionContext.SessionState.LanguageMode

# Environment
Get-ChildItem Env:
$env:PATH -split ';'

# Host
Get-ComputerInfo
Get-CimInstance Win32_OperatingSystem
Get-HotFix

# Users
Get-LocalUser
Get-LocalGroup
Get-LocalGroupMember -Group Administrators

# Processes
Get-Process
Get-CimInstance Win32_Process

# Services
Get-Service
Get-CimInstance Win32_Service

# Tasks
Get-ScheduledTask

# Network
Get-NetIPConfiguration
Get-NetRoute
Get-NetTCPConnection
Get-NetUDPEndpoint
Resolve-DnsName example.com
Test-NetConnection example.com -Port 443

# SMB
Get-SmbShare
Get-SmbMapping
Get-SmbServerConfiguration
Get-SmbClientConfiguration

# Firewall
Get-NetFirewallProfile
Get-NetFirewallRule

# Files
Get-ChildItem
Get-Content
Get-FileHash
Get-AuthenticodeSignature

# ACL
Get-Acl C:\Path

# Registry
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'

# HTTP
Invoke-WebRequest -Uri 'https://example.com/'
Invoke-RestMethod -Uri 'https://example.com/api'

# Defender
Get-MpComputerStatus
Get-MpPreference

# AppLocker
Get-AppLockerPolicy -Effective

# Events
Get-WinEvent -LogName System -MaxEvents 50

# AD
Get-ADDomain
Get-ADForest
Get-ADDomainController -Filter *
```

---

# Testing Model

PowerShell should be assessed as part of the wider Windows security model:

```text
User
 |
 v
PowerShell
 |
 +--> Language Mode
 |
 +--> Execution Policy
 |
 +--> Modules / .NET
 |
 +--> Logging
 |
 +--> AMSI
 |
 +--> Defender
 |
 +--> AppLocker / WDAC
 |
 v
Effective Security Boundary
```

The key distinction is:

```text
PowerShell Capability
        !=
Vulnerability
```

For example:

```text
Invoke-WebRequest Available
```

does not itself mean:

```text
Security Control Bypass
```

and:

```text
FullLanguage
```

does not itself mean:

```text
Privilege Escalation
```

A finding should demonstrate:

```text
Principal
   |
   v
PowerShell Capability
   |
   v
Expected Restriction
   |
   v
Restriction Ineffective
   |
   v
Security Impact
```

---

# References

## InternalAllTheThings

[InternalAllTheThings - PowerShell Cheatsheet](https://swisskyrepo.github.io/InternalAllTheThings/cheatsheets/powershell-cheatsheet/){ target="_blank" rel="noopener noreferrer" }

Useful coverage reference for:

```text
Execution Policy
Language Mode
Encoded Commands
Downloads
PowerShell Script Loading
.NET / Reflection
SecureString Handling
```

Some material is offensive-security focused or historical. Validate techniques against the Windows version, PowerShell version and current security controls before using them.

---

## Microsoft PowerShell

[Microsoft Learn - PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/){ target="_blank" rel="noopener noreferrer" }

---

## about_Execution_Policies

[Microsoft Learn - about_Execution_Policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies){ target="_blank" rel="noopener noreferrer" }

---

## about_Language_Modes

[Microsoft Learn - about_Language_Modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }

---

## about_PowerShell_exe

[Microsoft Learn - powershell.exe](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe){ target="_blank" rel="noopener noreferrer" }

---

## PowerShell Security

[Microsoft Learn - PowerShell Security Features](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features){ target="_blank" rel="noopener noreferrer" }

---

## PowerShell Logging

[Microsoft Learn - about_Logging_Windows](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows){ target="_blank" rel="noopener noreferrer" }

---

## AppLocker

[Microsoft Learn - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }

---

## App Control for Business

[Microsoft Learn - App Control for Business](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Defender Antivirus

[Microsoft Learn - Microsoft Defender Antivirus](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-antivirus-windows){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

For everyday PowerShell use:

```text
Get
 |
 v
Filter
 |
 v
Select
 |
 v
Export
```

For security assessment:

```text
Identity
   |
   v
Environment
   |
   v
System
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
Security Controls
```

The most useful initial commands are often:

```powershell
whoami /all
$PSVersionTable
$ExecutionContext.SessionState.LanguageMode
Get-ExecutionPolicy -List
Get-ComputerInfo
Get-Process
Get-CimInstance Win32_Service
Get-ScheduledTask
Get-NetIPConfiguration
Get-NetTCPConnection -State Listen
Get-MpComputerStatus
Get-AppLockerPolicy -Effective
```

When analysing PowerShell security, do not focus on a single setting.

Use:

```text
Execution Policy
      +
Language Mode
      +
Logging
      +
AMSI
      +
Defender
      +
Application Control
      =
Effective PowerShell Security Posture
```

When encountering encoded or unfamiliar PowerShell:

```text
Capture
   |
   v
Decode
   |
   v
Read
   |
   v
Understand
   |
   v
Decide Whether Execution Is Necessary
```

Do not execute unknown content merely to understand what it does.

For authorised assessments, the preferred workflow remains:

```text
Enumerate
   |
   v
Analyse
   |
   v
Validate Safely
   |
   v
Collect Evidence
   |
   v
Report
```
