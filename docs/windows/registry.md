---
title: Windows Registry Security
description: Practical Windows Registry enumeration and security assessment covering permissions, privilege escalation paths, autoruns, services, application configuration, credentials, evidence collection, remediation and retesting.
---

# Windows Registry Security

The Windows Registry is a hierarchical configuration database used by Windows, applications, services and users.

It stores information related to:

```text
Operating system configuration
Services
Drivers
Applications
User profiles
Authentication
Security policies
Startup behaviour
File associations
Environment variables
Installed software
Application settings
```

During a Windows security assessment, Registry permissions and configuration can reveal privilege escalation opportunities, sensitive information and insecure application behaviour.

The key security question is not simply:

```text
Can the user write to the Registry?
```

Instead ask:

```text
Can a lower-privileged user modify a Registry value
that influences a higher-privileged security context?
```

!!! warning "Authorised Security Testing"

    Perform Registry testing only on systems included in the authorised assessment scope. Prefer permission inspection and non-destructive validation. Do not modify production service configuration, startup entries, security controls or other operational Registry values unless explicitly permitted.


# Registry Security Model

A typical privilege escalation path looks like:

```text
Low-Privilege User
        |
        v
Writable Registry Key
        |
        v
Privileged Configuration
        |
        v
SYSTEM / Administrator Process
        |
        v
Attacker-Controlled Behaviour
```

A writable Registry key alone is not necessarily a vulnerability.

A meaningful security issue normally requires:

```text
Lower-privileged write access
+
Security-sensitive Registry value
+
Higher-privileged consumer
+
Demonstrable security impact
```


# Registry Hives

The primary Registry hives include:

| Hive | Abbreviation | Purpose |
|---|---|---|
| `HKEY_LOCAL_MACHINE` | `HKLM` | System-wide configuration |
| `HKEY_CURRENT_USER` | `HKCU` | Current user's configuration |
| `HKEY_CLASSES_ROOT` | `HKCR` | File associations and COM registration view |
| `HKEY_USERS` | `HKU` | Loaded user profiles |
| `HKEY_CURRENT_CONFIG` | `HKCC` | Current hardware configuration |


# PowerShell Registry Drives

PowerShell exposes common Registry hives as drives:

```powershell
Get-PSDrive -PSProvider Registry
```

Typical output:

```text
Name Used (GB) Free (GB) Provider Root
---- --------- --------- -------- ----
HKCU                     Registry HKEY_CURRENT_USER
HKLM                     Registry HKEY_LOCAL_MACHINE
```


# Registry Paths

PowerShell example:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE'
```

Traditional Registry path:

```text
HKEY_LOCAL_MACHINE\SOFTWARE
```

`reg.exe` representation:

```text
HKLM\SOFTWARE
```


# Core Registry Tools

Useful built-in tools include:

```text
reg.exe
regedit.exe
PowerShell Registry provider
Get-Item
Get-ItemProperty
Get-Acl
```


# reg.exe

Query a key:

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion"
```


# Query a Value

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion" /v ProgramFilesDir
```


# Recursive Query

```cmd
reg query "HKLM\SOFTWARE\Example" /s
```


# PowerShell Query

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion'
```


# List Subkeys

```powershell
Get-ChildItem 'HKLM:\SOFTWARE'
```


# Specific Property

```powershell
Get-ItemPropertyValue -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion' -Name 'ProgramFilesDir'
```


# Current Identity

Before analysing Registry permissions, identify the current security context.

```cmd
whoami
```


# Group Membership

```cmd
whoami /groups
```


# Privileges

```cmd
whoami /priv
```


# PowerShell Identity

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```


# Why Identity Matters

An ACL may grant access to:

```text
Users

Authenticated Users

Everyone

A local group

A domain group
```

You need to determine whether the current user belongs to the relevant security principal.


# Registry ACLs

Registry keys have security descriptors similar to filesystem objects.

Use:

```powershell
Get-Acl 'HKLM:\SOFTWARE\Example'
```


# Detailed ACL

```powershell
Get-Acl 'HKLM:\SOFTWARE\Example' | Format-List *
```


# Access Entries

```powershell
(Get-Acl 'HKLM:\SOFTWARE\Example').Access
```


# Compact View

```powershell
(Get-Acl 'HKLM:\SOFTWARE\Example').Access | Select-Object IdentityReference,RegistryRights,AccessControlType,IsInherited
```


# Important Registry Rights

Common rights include:

| Right | Meaning |
|---|---|
| `QueryValues` | Read values |
| `SetValue` | Modify values |
| `CreateSubKey` | Create child keys |
| `EnumerateSubKeys` | Enumerate child keys |
| `Delete` | Delete key |
| `ChangePermissions` | Modify ACL |
| `TakeOwnership` | Change ownership |
| `ReadKey` | Read access |
| `WriteKey` | Write-related access |
| `FullControl` | Full access |


# High-Value Write Rights

Pay particular attention to:

```text
SetValue
CreateSubKey
WriteKey
FullControl
ChangePermissions
TakeOwnership
```


# ACL Example

```text
RegistryRights    : SetValue, CreateSubKey, ReadKey
AccessControlType : Allow
IdentityReference : BUILTIN\Users
IsInherited       : False
```


# Interpretation

This establishes that:

```text
BUILTIN\Users
```

has meaningful write access.

It does not yet establish a vulnerability.

Next determine:

```text
What consumes this key?

Which privilege does that process use?

Can modification influence execution or security behaviour?
```


# Registry Privilege Escalation Workflow

```text
ENUMERATE
    |
    v
IDENTIFY WRITABLE KEY
    |
    v
IDENTIFY SECURITY-SENSITIVE VALUE
    |
    v
IDENTIFY CONSUMING PROCESS
    |
    v
DETERMINE PROCESS PRIVILEGE
    |
    v
VERIFY USER CONTROL
    |
    v
VALIDATE IMPACT
```


# High-Value Registry Areas

Useful areas to review include:

```text
Services

Startup configuration

Application configuration

Installer policy

Environment configuration

COM registration

Protocol handlers

File associations

Security product configuration

Stored application secrets
```


# Services

Windows service configuration is represented under:

```text
HKLM\SYSTEM\CurrentControlSet\Services
```

Enumerate:

```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Services"
```


# PowerShell

```powershell
Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services'
```


# Specific Service

```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Services\ExampleService"
```


# Important Service Values

Common values include:

```text
ImagePath
DisplayName
ObjectName
Start
Type
DependOnService
```


# ImagePath

Query:

```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Services\ExampleService" /v ImagePath
```


# Representative Output

```text
ImagePath    REG_EXPAND_SZ    C:\Program Files\Example\Service.exe
```


# Security Analysis

Determine:

```text
Who can modify the service key?

Who can modify ImagePath?

Who can modify the referenced executable?

Who can modify the executable's parent directory?

Which account runs the service?
```


# Service Registry ACL

```powershell
Get-Acl 'HKLM:\SYSTEM\CurrentControlSet\Services\ExampleService' | Format-List Owner,AccessToString
```


# Access Entries

```powershell
(Get-Acl 'HKLM:\SYSTEM\CurrentControlSet\Services\ExampleService').Access | Select-Object IdentityReference,RegistryRights,AccessControlType,IsInherited
```


# Potential Pattern

```text
Standard User
      |
      v
Writable Service Registry Key
      |
      v
ImagePath
      |
      v
Privileged Service
      |
      v
Potential Privilege Escalation
```


# Important

Registry ACLs are only one part of service security.

Also review the service object's permissions.

See:

[Windows Services](services.md)


# Service Security Context

Check:

```powershell
Get-CimInstance Win32_Service -Filter "Name='ExampleService'" | Select-Object Name,StartName,State,PathName
```


# Representative Output

```text
Name      : ExampleService
StartName : LocalSystem
State     : Running
PathName  : C:\Program Files\Example\Service.exe
```


# Interpretation

If:

```text
Service account:
LocalSystem
```

and:

```text
Standard user can modify ImagePath
```

this is a strong privilege escalation candidate.

However, establish whether the user can actually change the value and whether the service can subsequently execute the modified configuration.


# Safe Validation

Prefer:

```text
ACL inspection

Current-user access analysis

Service configuration review
```

before attempting any Registry modification.


# Autorun Registry Keys

Windows and applications may use Registry values to start programs during user logon.


# Common Run Keys

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run

HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce

HKLM\Software\Microsoft\Windows\CurrentVersion\Run

HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
```


# Query HKCU Run

```cmd
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
```


# Query HKLM Run

```cmd
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
```


# PowerShell

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue
```


# Machine-Wide Run

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue
```


# Security Context Matters

An HKCU autorun normally executes as:

```text
That user
```

It does not automatically provide privilege escalation.


# Machine-Wide Configuration

An insecure machine-wide startup configuration can be more significant when:

```text
Standard user can modify it

and

A higher-privileged user or process consumes it
```


# Startup Command Dependencies

Example:

```text
Updater    REG_SZ    C:\ProgramData\Vendor\update.exe
```

Review:

```text
Registry ACL

Executable ACL

Parent directory ACL

Execution context
```


# Startup Folder Relationship

Registry autoruns are not the only startup mechanism.

Also consider:

```text
Startup folders

Scheduled tasks

Services
```

when reviewing Windows persistence and privilege escalation.


# Winlogon

Security-sensitive configuration exists under:

```text
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```


# Query

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```


# Common Values

Examples include:

```text
Shell
Userinit
```


# Typical Values

Common legitimate values may resemble:

```text
Shell:
explorer.exe

Userinit:
C:\Windows\system32\userinit.exe,
```


# Security Assessment

Review unexpected modifications and ACLs.

Do not modify Winlogon configuration during routine assessment validation.

Incorrect values can prevent normal user logon.


# Safe Check

```powershell
Get-Acl 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' | Format-List Owner,AccessToString
```


# Installer Policies

Windows Installer policy deserves attention during privilege escalation reviews.


# AlwaysInstallElevated

Two Registry values are relevant:

```text
HKCU\Software\Policies\Microsoft\Windows\Installer

HKLM\Software\Policies\Microsoft\Windows\Installer
```


# Query Current User

```cmd
reg query "HKCU\Software\Policies\Microsoft\Windows\Installer" /v AlwaysInstallElevated
```


# Query Local Machine

```cmd
reg query "HKLM\Software\Policies\Microsoft\Windows\Installer" /v AlwaysInstallElevated
```


# PowerShell

```powershell
Get-ItemPropertyValue -Path 'HKCU:\Software\Policies\Microsoft\Windows\Installer' -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```

```powershell
Get-ItemPropertyValue -Path 'HKLM:\Software\Policies\Microsoft\Windows\Installer' -Name AlwaysInstallElevated -ErrorAction SilentlyContinue
```


# Interpretation

The security-relevant configuration is when the policy is enabled in both applicable locations.

Example:

```text
HKCU:
AlwaysInstallElevated = 1

HKLM:
AlwaysInstallElevated = 1
```


# Important

Do not report the condition based on only one value without understanding the effective Windows Installer policy.

The finding should be based on effective behaviour and the applicable policy configuration.


# Safe Reporting

For an authorised assessment, configuration evidence is often sufficient to report the unsafe policy without executing an installer package.


# Environment Variables

Machine and user environment configuration can be stored in the Registry.


# Machine Environment

```text
HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
```


# Query

```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
```


# User Environment

```text
HKCU\Environment
```


# Query

```cmd
reg query "HKCU\Environment"
```


# PATH

Pay attention to:

```text
Path
```

but do not automatically treat writable PATH directories as exploitable.


# PATH Security Model

```text
Privileged Process
       |
       v
Executes Relative Command
       |
       v
PATH Search
       |
       v
Writable Directory
       |
       v
Potential Hijack
```


# Required Conditions

A meaningful PATH-based privilege escalation generally requires:

```text
Privileged process
+
Relative executable invocation
+
Attacker-controlled search location
+
Predictable execution
```


# Machine PATH

PowerShell:

```powershell
[Environment]::GetEnvironmentVariable('Path','Machine')
```


# User PATH

```powershell
[Environment]::GetEnvironmentVariable('Path','User')
```


# Split PATH

```powershell
[Environment]::GetEnvironmentVariable('Path','Machine') -split ';'
```


# Review Directory ACLs

For each relevant directory:

```powershell
Get-Acl -LiteralPath 'C:\Example\bin' | Format-List Owner,AccessToString
```


# Important

A writable PATH entry is not sufficient by itself.

You still need a privileged application that resolves an executable through that path.


# Application Configuration

Third-party software frequently stores configuration under:

```text
HKLM\SOFTWARE\Vendor

HKLM\SOFTWARE\WOW6432Node\Vendor

HKCU\Software\Vendor
```


# Enumerate Installed Vendor Keys

```powershell
Get-ChildItem 'HKLM:\SOFTWARE' | Select-Object PSChildName
```


# 32-bit Software

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\WOW6432Node' -ErrorAction SilentlyContinue | Select-Object PSChildName
```


# Security Questions

For interesting application keys ask:

```text
Who can modify the key?

Which process reads it?

Which account runs that process?

Does it contain executable paths?

Does it contain script paths?

Does it contain plugin paths?

Does it contain command-line arguments?

Does it contain credentials?

Does it contain network locations?
```


# Application Command Configuration

Example:

```text
ExecutablePath = C:\ProgramData\Vendor\worker.exe
```

If a privileged service consumes this value, inspect both:

```text
Registry permissions

Filesystem permissions
```


# Registry-to-Filesystem Relationship

```text
Registry Value
     |
     v
Executable Path
     |
     v
Filesystem Object
     |
     v
Filesystem ACL
```

Both layers matter.


# Credentials in the Registry

Applications sometimes store sensitive information in Registry values.

Search should be targeted and authorised.


# Common Keywords

Potential indicators include:

```text
password
passwd
pwd
credential
secret
token
apikey
api_key
connectionstring
username
user
```


# Targeted PowerShell Search

For a known application subtree:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\ExampleVendor' -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $item = Get-ItemProperty $_.PSPath -ErrorAction Stop
        $item.PSObject.Properties | Where-Object {
            $_.Name -match 'password|passwd|pwd|secret|token|api.?key|credential|connection'
        } | ForEach-Object {
            [PSCustomObject]@{
                Path  = $_.PSParentPath
                Name  = $_.Name
                Value = $_.Value
            }
        }
    } catch {}
}
```


# Important

Avoid indiscriminately dumping the entire Registry.

Large-scale searches can:

```text
Generate unnecessary data

Expose unrelated secrets

Create evidence-handling issues

Consume significant time
```


# Scope Searches

Prefer:

```text
Known application keys

Assessment-relevant vendor keys

Specific configuration paths
```


# Credential Interpretation

Finding a value named:

```text
Password
```

does not prove it contains plaintext credentials.

Determine whether it contains:

```text
Plaintext

Encrypted data

Hash

Reference

Placeholder

Empty value
```


# DPAPI

Some Registry values may contain data protected using Windows Data Protection API.

Encrypted data should not be described as plaintext credentials.


# Reporting Sensitive Data

Do not place full passwords, API keys or tokens in screenshots or reports.

Use redaction such as:

```text
Password = Sup***********
```


# Uninstall Information

Installed application information is commonly stored under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall

HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall
```


# Query

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s
```


# PowerShell Inventory

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue | ForEach-Object {
    Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
} | Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```


# Include 32-bit Applications

```powershell
$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

Get-ItemProperty $paths -ErrorAction SilentlyContinue |
    Where-Object DisplayName |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```


# Security Use

Application inventory can support:

```text
Patch review

Attack-surface identification

Service correlation

Vendor configuration discovery
```

Do not assume a version is vulnerable without verifying the applicable advisory and product configuration.


# Current User Software

Also consider:

```text
HKCU\Software
```

for per-user application configuration.


# File Associations

Windows file associations may involve:

```text
HKCR
```

and underlying user/machine class registration.


# Example Query

```cmd
reg query "HKCR\.txt"
```


# Handler

```cmd
reg query "HKCR\txtfile\shell\open\command"
```


# Security Relevance

File association hijacking can matter when:

```text
A privileged process opens a registered file type

and

A lower-privileged user controls the applicable handler
```

Do not infer privilege escalation from a user-controlled association alone.


# HKEY_CLASSES_ROOT

`HKCR` is a merged view involving machine and user class registration.

This distinction matters during security analysis.

Conceptually:

```text
Machine classes
+
User classes
     |
     v
Merged HKCR view
```


# COM Registration

COM configuration can be security-sensitive.

Relevant locations include class registration under:

```text
HKLM\SOFTWARE\Classes

HKCU\Software\Classes
```


# CLSID

Example structure:

```text
Software\Classes\CLSID\{GUID}
```


# InprocServer32

COM servers may reference:

```text
InprocServer32
```

or other server registration.


# Example Query

```cmd
reg query "HKLM\SOFTWARE\Classes\CLSID\{GUID}\InprocServer32"
```


# Security Model

A COM-related privilege escalation requires much more than discovering a writable registration.

You need to establish:

```text
Which component instantiates the COM object?

Which registration view applies?

Which user context is involved?

Which process privilege is involved?

Can the lower-privileged user influence the effective registration?

Does the behaviour cross a privilege boundary?
```


# Do Not Overstate COM Findings

COM registration is complex.

Avoid reporting:

```text
Writable HKCU COM key = SYSTEM privilege escalation
```

without demonstrating the relevant privileged consumer and registration behaviour.


# Protocol Handlers

Applications may register URI schemes such as:

```text
example://
```

Registry configuration can determine which application handles the scheme.


# Security Questions

Review:

```text
Command path

Arguments

Quoting

User control

Privilege of invoking application

Input handling
```


# Shell Commands

Registry locations may contain command strings such as:

```text
shell\open\command
```

Analyse:

```text
Executable path

Arguments

User-controlled substitutions

Execution context
```


# Safe Inspection

Query only:

```cmd
reg query "HKCR\Example\shell\open\command"
```

Avoid changing handlers on production systems during routine validation.


# Registry AutoRun Review

A consolidated PowerShell view:

```powershell
$runKeys = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce'
)

foreach ($key in $runKeys) {
    if (Test-Path $key) {
        Write-Host "`n[$key]"
        Get-ItemProperty $key
    }
}
```


# ACL Review for Run Keys

```powershell
$runKeys = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run'
)

foreach ($key in $runKeys) {
    if (Test-Path $key) {
        Write-Host "`n[$key]"
        (Get-Acl $key).Access |
            Select-Object IdentityReference,RegistryRights,AccessControlType,IsInherited
    }
}
```


# Important HKCU Distinction

The current user is expected to control much of:

```text
HKCU
```

That alone is not a security weakness.

Look for situations where per-user configuration unexpectedly influences a more privileged security context.


# HKLM Distinction

Write access to security-sensitive:

```text
HKLM
```

locations is generally more interesting because HKLM contains machine-wide configuration.

Still, validate the actual consumer and impact.


# Registry Inheritance

Registry permissions may be inherited from parent keys.

Inspect:

```powershell
(Get-Acl 'HKLM:\SOFTWARE\Example').Access | Select-Object IdentityReference,RegistryRights,AccessControlType,IsInherited
```


# Why Inheritance Matters

An insecure permission may originate from:

```text
HKLM\SOFTWARE\Vendor
```

and propagate to many application subkeys.


# Variant Analysis

After finding one insecure key, inspect sibling keys.

Example:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Vendor'
```


# Root Cause

If several keys inherit the same weak ACL, fixing one child key may not resolve the root cause.


# Registry Ownership

Inspect owner:

```powershell
(Get-Acl 'HKLM:\SOFTWARE\Example').Owner
```


# Ownership Security

Unexpected ownership can be relevant when it permits a lower-privileged identity to change permissions.

Do not equate ownership alone with immediate write access without examining effective rights.


# Deny ACEs

Explicit deny entries can override or constrain allow entries.

Example:

```text
Users:
Allow SetValue

SpecificUser:
Deny SetValue
```

Effective access must account for the complete security descriptor and token membership.


# Effective Access

Registry ACL interpretation should consider:

```text
Direct ACEs

Inherited ACEs

Allow entries

Deny entries

Group membership

Ownership

Privilege
```


# Safe Write Validation

When the engagement permits validation, avoid altering operational values.

If you control a dedicated test key, a harmless value can be used to validate effective write access.


# Example Test Key

Only use this against a location explicitly approved for testing:

```powershell
$path = 'HKCU:\Software\SecurityAssessmentTest'

New-Item -Path $path -Force | Out-Null
New-ItemProperty -Path $path -Name 'WriteTest' -Value 'test' -PropertyType String -Force | Out-Null
Get-ItemProperty -Path $path -Name 'WriteTest'
Remove-Item -Path $path -Recurse -Force
```


# Important

Testing write access to:

```text
HKCU:\Software\SecurityAssessmentTest
```

does not prove write access to an unrelated target key.

For actual target keys, use ACL analysis or a specifically authorised non-operational value where appropriate.


# Do Not Modify Production Values Just to Test ACLs

Avoid changing:

```text
Service ImagePath

Winlogon Shell

Security product settings

Authentication settings

Startup commands

Installer policies
```

unless explicit validation requires it.


# Remote Registry

Registry access can also occur remotely when:

```text
Remote Registry service is available

Network access permits it

Authentication succeeds

Registry ACL permits access
```


# Security Relevance

Remote Registry exposure is not automatically a vulnerability.

Evaluate:

```text
Network segmentation

Authentication

Authorization

Administrative requirements

Firewall policy
```


# Remote Registry Service

Check locally:

```powershell
Get-Service RemoteRegistry -ErrorAction SilentlyContinue
```


# Representative Output

```text
Status   Name            DisplayName
------   ----            -----------
Stopped  RemoteRegistry  Remote Registry
```


# Interpretation

A stopped Remote Registry service is common.

Do not report it merely because the service exists.


# Registry Backups

Registry hives and exported `.reg` files can contain sensitive configuration.


# Search Relevant Filesystem Locations

During an authorised assessment, look for files such as:

```text
*.reg
*.hiv
*.save
registry-backup*
```

in assessment-relevant directories.


# Important

Do not indiscriminately copy Registry hives.

Credential-bearing system hives are sensitive evidence and should only be collected when required by the assessment scope.


# Registry and UAC

Some UAC-related configuration is represented in the Registry.

Relevant policy configuration can exist under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
```


# Query

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
```


# Important

Do not interpret individual UAC Registry values in isolation.

UAC behaviour depends on:

```text
Account type

Token state

Integrity level

Policy combination

Executable behaviour
```

UAC deserves separate analysis.

See the planned note:

```text
docs/windows/uac.md
```


# Registry and Application Control

Security controls may also expose configuration through Registry-backed policy.

Examples include:

```text
AppLocker

Windows Defender

Windows Defender Application Control related policy/configuration

PowerShell policy
```


# Important

Registry configuration visibility does not necessarily mean the current user can change the effective security policy.

Policies may be:

```text
GPO-managed

MDM-managed

Locally enforced

Protected by security software
```


# Group Policy

Values under policy-related Registry locations may be applied by Group Policy.

A local modification, even if technically possible, may be:

```text
Reverted

Overwritten

Ignored

Protected
```


# Determine Source of Truth

When analysing security policy, distinguish:

```text
Observed Registry value

Effective policy

Policy management source
```


# WOW64 Registry Redirection

On 64-bit Windows, 32-bit and 64-bit applications can observe different Registry views.

Relevant paths may include:

```text
HKLM\SOFTWARE

HKLM\SOFTWARE\WOW6432Node
```


# Security Relevance

When investigating a third-party application, determine whether it is:

```text
32-bit

64-bit
```

and inspect the applicable Registry view.


# PowerShell Architecture

Check:

```powershell
[Environment]::Is64BitProcess
```

and:

```powershell
[Environment]::Is64BitOperatingSystem
```


# Registry Value Types

Common Registry data types include:

| Type | Purpose |
|---|---|
| `REG_SZ` | String |
| `REG_EXPAND_SZ` | Expandable string |
| `REG_DWORD` | 32-bit number |
| `REG_QWORD` | 64-bit number |
| `REG_MULTI_SZ` | Multiple strings |
| `REG_BINARY` | Binary data |


# Expandable Values

Example:

```text
%SystemRoot%\System32\example.exe
```

may be stored as:

```text
REG_EXPAND_SZ
```


# Expand Environment Variables

```powershell
[Environment]::ExpandEnvironmentVariables('%SystemRoot%\System32\example.exe')
```


# Do Not Assume Current User Expansion

A privileged service may execute with a different environment.

Consider the consuming process's security context.


# Interesting Registry Value Patterns

During targeted review, values containing these concepts may deserve attention:

```text
Path

Executable

Command

Script

Plugin

Module

Handler

Service

Update

Backup

Temp

Config

Password

Secret

Token

Key
```


# Targeted Value Search

For a known vendor key:

```powershell
$root = 'HKLM:\SOFTWARE\ExampleVendor'

Get-ChildItem $root -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $item = Get-ItemProperty $_.PSPath -ErrorAction Stop

        foreach ($property in $item.PSObject.Properties) {
            if ($property.Name -match 'path|exe|command|script|plugin|module|handler|password|secret|token') {
                [PSCustomObject]@{
                    Key   = $_.Name
                    Name  = $property.Name
                    Value = $property.Value
                }
            }
        }
    } catch {}
}
```


# Interpretation

Treat keyword searches as:

```text
Candidate discovery
```

not:

```text
Vulnerability confirmation
```


# Registry-to-Execution Analysis

Suppose you find:

```text
HKLM\SOFTWARE\ExampleVendor

WorkerPath =
C:\ProgramData\ExampleVendor\worker.exe
```


# Step 1 - Registry ACL

```powershell
Get-Acl 'HKLM:\SOFTWARE\ExampleVendor' | Format-List Owner,AccessToString
```


# Step 2 - File ACL

```powershell
Get-Acl 'C:\ProgramData\ExampleVendor\worker.exe' | Format-List Owner,AccessToString
```


# Step 3 - Directory ACL

```powershell
Get-Acl 'C:\ProgramData\ExampleVendor' | Format-List Owner,AccessToString
```


# Step 4 - Consumer

Determine which process uses:

```text
WorkerPath
```


# Step 5 - Security Context

Determine whether that process runs as:

```text
Current user

Administrator

SYSTEM

Service account
```


# Step 6 - Trigger

Determine:

```text
When is WorkerPath consumed?
```


# Step 7 - Security Boundary

Only then determine whether a privilege escalation exists.


# Complete Analysis Model

```text
Registry Key
    |
    v
Registry Value
    |
    v
Consumer
    |
    v
Security Context
    |
    v
Referenced Resource
    |
    v
Filesystem / Network ACL
    |
    v
Trigger
    |
    v
Security Impact
```


# Application Update Configuration

Update mechanisms deserve particular attention.

Registry configuration may contain:

```text
Update URL

Updater path

Package directory

Command

Installation path
```


# Security Questions

Ask:

```text
Does updater run privileged?

Can user modify updater path?

Can user modify package directory?

Can user influence update source?

Is package integrity verified?
```


# Important

A writable update-related Registry value is only one part of the update trust model.


# Backup Configuration

Backup agents may store:

```text
Executable paths

Script paths

Credential references

Network shares

Destination directories
```

in the Registry.


# Security Context

Backup software frequently runs with elevated privileges.

Therefore, writable configuration can be high-value.


# Monitoring Agents

Monitoring and management agents may use Registry configuration for:

```text
Plugins

Scripts

Commands

Configuration directories
```

Review whether standard users can influence these values.


# Development Software

Developer tooling may create machine-wide Registry configuration.

Examples include:

```text
Build tools

Package managers

IDE integrations

Local web servers

Automation agents
```

Do not assume development software is low risk when services run privileged.


# Registry and Scheduled Tasks

Scheduled tasks may execute applications whose configuration is stored in the Registry.

Analysis can therefore become:

```text
Scheduled Task
      |
      v
Privileged Application
      |
      v
Registry Configuration
      |
      v
User-Writable Value
      |
      v
Controlled Dependency
```


# Related Note

See:

[Windows Scheduled Tasks](scheduled-tasks.md)


# Registry and Services

Similarly:

```text
Service
   |
   v
Application
   |
   v
Registry Configuration
   |
   v
Executable / Plugin / Script
```


# Related Note

See:

[Windows Services](services.md)


# Registry and Filesystem Permissions

Registry write access may redirect a privileged process to a filesystem location.

Always evaluate both security descriptors.


# Example

```text
Registry:
Executable = C:\ProgramData\App\worker.exe

Registry ACL:
Users = SetValue

Filesystem:
C:\ProgramData\App = Administrators only
```

Even though the current executable is protected, changing the Registry path may still allow redirection if the privileged application trusts that value.


# Conversely

```text
Registry:
Administrators only

Filesystem executable:
Users = Modify
```

The privilege escalation may exist through the filesystem even though Registry permissions are secure.


# Multiple Control Points

```text
              PRIVILEGED PROCESS
                     |
          +----------+----------+
          |                     |
          v                     v
     Registry Path          Fixed Path
          |                     |
          v                     v
   Registry ACL          Filesystem ACL
          |                     |
          +----------+----------+
                     |
                     v
               User Control?
```


# Registry Enumeration Checklist

## Identity

- [ ] Current user identified
- [ ] Group memberships identified
- [ ] Token privileges reviewed
- [ ] Administrative status understood

## Registry Structure

- [ ] Relevant HKLM keys reviewed
- [ ] Relevant HKCU keys reviewed
- [ ] 32-bit Registry view considered
- [ ] 64-bit Registry view considered
- [ ] Inheritance considered

## Permissions

- [ ] Key owner reviewed
- [ ] ACL entries reviewed
- [ ] `SetValue` identified
- [ ] `CreateSubKey` identified
- [ ] `WriteKey` identified
- [ ] `FullControl` identified
- [ ] `ChangePermissions` identified
- [ ] `TakeOwnership` identified
- [ ] Deny ACEs considered
- [ ] Group membership correlated

## Services

- [ ] Service Registry keys reviewed
- [ ] `ImagePath` reviewed
- [ ] Service account identified
- [ ] Service object permissions considered
- [ ] Executable ACL reviewed
- [ ] Parent directory ACL reviewed

## Startup

- [ ] HKCU Run reviewed
- [ ] HKLM Run reviewed
- [ ] RunOnce reviewed
- [ ] Winlogon configuration reviewed where relevant
- [ ] Startup execution context established
- [ ] Referenced files reviewed

## Installer Policy

- [ ] HKCU AlwaysInstallElevated checked
- [ ] HKLM AlwaysInstallElevated checked
- [ ] Effective policy interpreted correctly

## Applications

- [ ] Vendor keys reviewed
- [ ] Executable paths reviewed
- [ ] Script paths reviewed
- [ ] Plugin paths reviewed
- [ ] Configuration paths reviewed
- [ ] Update configuration reviewed
- [ ] Backup configuration reviewed
- [ ] Referenced filesystem ACLs reviewed

## Sensitive Information

- [ ] Relevant application keys searched
- [ ] Plaintext distinguished from encrypted data
- [ ] Tokens handled as sensitive evidence
- [ ] Credentials redacted in reports
- [ ] Unrelated secrets not collected unnecessarily

## Advanced Areas

- [ ] File associations considered where relevant
- [ ] Protocol handlers considered
- [ ] COM registration considered where relevant
- [ ] Environment configuration considered
- [ ] PATH-based behaviour validated rather than assumed
- [ ] WOW64 view differences considered

## Validation

- [ ] Consumer identified
- [ ] Consumer privilege identified
- [ ] Trigger identified
- [ ] User write access established
- [ ] Security boundary established
- [ ] Alternative explanations excluded
- [ ] Non-destructive validation preferred

## Reporting

- [ ] Exact Registry path recorded
- [ ] Exact value recorded
- [ ] ACL evidence recorded
- [ ] Consumer identified
- [ ] Privileged context identified
- [ ] Security impact explained
- [ ] Sensitive values redacted
- [ ] Root cause identified

## Retesting

- [ ] Registry ACL retested
- [ ] Referenced filesystem ACL retested
- [ ] Original modification path closed
- [ ] Legitimate application still operates
- [ ] Parent-key inheritance reviewed
- [ ] Equivalent vulnerable keys reviewed


# Quick Reference

| Goal | Command |
|---|---|
| Query key | `reg query "HKLM\SOFTWARE\Example"` |
| Recursive query | `reg query "HKLM\SOFTWARE\Example" /s` |
| Query value | `reg query "HKLM\SOFTWARE\Example" /v ValueName` |
| PowerShell properties | `Get-ItemProperty 'HKLM:\SOFTWARE\Example'` |
| List subkeys | `Get-ChildItem 'HKLM:\SOFTWARE\Example'` |
| Registry ACL | `Get-Acl 'HKLM:\SOFTWARE\Example'` |
| ACL entries | `(Get-Acl 'HKLM:\SOFTWARE\Example').Access` |
| Current identity | `whoami` |
| Groups | `whoami /groups` |
| Privileges | `whoami /priv` |
| Services | `Get-CimInstance Win32_Service` |
| Machine PATH | `[Environment]::GetEnvironmentVariable('Path','Machine')` |
| User PATH | `[Environment]::GetEnvironmentVariable('Path','User')` |


# High-Value Registry Paths

| Purpose | Path |
|---|---|
| Services | `HKLM\SYSTEM\CurrentControlSet\Services` |
| Machine Run | `HKLM\Software\Microsoft\Windows\CurrentVersion\Run` |
| User Run | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| Machine RunOnce | `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce` |
| User RunOnce | `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce` |
| Winlogon | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` |
| Machine environment | `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment` |
| User environment | `HKCU\Environment` |
| Installed software | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` |
| 32-bit installed software | `HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall` |
| Machine classes | `HKLM\SOFTWARE\Classes` |
| User classes | `HKCU\Software\Classes` |
| UAC policy | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System` |


# Candidate Prioritization Matrix

| Registry Condition | Consumer | Priority |
|---|---|---|
| Writable service `ImagePath` | SYSTEM service | Critical review |
| Writable privileged application path | SYSTEM process | Critical review |
| Writable privileged script path | Administrator/SYSTEM | Critical review |
| Writable plugin path | Privileged application | High review |
| Writable updater configuration | Privileged updater | High review |
| Writable backup configuration | Privileged backup agent | High review |
| Writable HKCU autorun | Same user | Usually no privilege escalation |
| Writable user application preference | Same user | Low |
| Readable plaintext privileged credential | Applicable privileged account | Critical review |
| Writable unused vendor key | No consumer | Low |


# Interpretation Matrix

| Observation | Interpretation |
|---|---|
| User can write HKCU | Usually expected |
| User can write arbitrary sensitive HKLM key | Investigate |
| Users have `SetValue` on service key | Strong candidate |
| `ImagePath` references protected EXE | Registry redirection may still matter |
| Registry protected but EXE writable | Filesystem path may remain vulnerable |
| AlwaysInstallElevated only in one location | Do not assume exploitable configuration |
| Both relevant AlwaysInstallElevated policies enabled | Significant insecure policy |
| Plaintext password found | Sensitive information exposure |
| Encrypted Registry blob found | Requires correct classification |
| Writable PATH directory | Requires privileged relative execution |
| Writable COM registration | Requires privileged consumer validation |
| Writable autorun executes as same user | Persistence, not necessarily privilege escalation |


# False Positives

## Writable HKCU

A user being able to modify their own:

```text
HKCU
```

is expected.

Do not report this without a cross-privilege impact.


## Writable Application Preference

A user may control:

```text
Theme

Window size

Recent files

UI preferences
```

These are normally not security-sensitive.


## Registry Value Contains "Password"

A property name alone does not prove credential exposure.


## Writable PATH Entry

A writable PATH directory does not prove privilege escalation unless a privileged process resolves a predictable executable through it.


## Writable COM Key

COM behaviour is contextual.

A writable registration does not prove privileged COM hijacking without a relevant privileged consumer.


## Service Key Exists

The existence of:

```text
HKLM\SYSTEM\CurrentControlSet\Services\ServiceName
```

is normal.

The security issue requires inappropriate control.


# Alternative Explanations

When an unusual Registry permission is discovered, consider:

```text
Application installer requirement

Legacy software compatibility

Per-user customization

Group Policy management

Vendor update mechanism

Development environment

Temporary migration configuration
```

These explanations do not automatically make the permission safe, but they help establish why it exists and whether it is security-sensitive.


# Evidence Collection

A strong Registry finding should capture:

```text
Current user

Group membership

Exact Registry path

Exact value

Registry ACL

Relevant filesystem ACL

Consuming process

Process security context

Trigger

Observed impact
```


# Example Evidence Sequence

```cmd
whoami
```

```powershell
(Get-Acl 'HKLM:\SOFTWARE\ExampleVendor').Access | Select-Object IdentityReference,RegistryRights,AccessControlType,IsInherited
```

```cmd
reg query "HKLM\SOFTWARE\ExampleVendor"
```

```powershell
Get-CimInstance Win32_Service | Where-Object PathName -match 'ExampleVendor' | Select-Object Name,StartName,State,PathName
```

```cmd
icacls "C:\ProgramData\ExampleVendor"
```


# Evidence Chain

```text
Standard User
     |
     v
Registry SetValue
     |
     v
Security-Sensitive Configuration
     |
     v
SYSTEM Process
     |
     v
Controlled Execution
```


# Strong Finding

A strong finding might establish:

```text
1. Current user is a standard user.

2. BUILTIN\Users has SetValue on a vendor Registry key.

3. The key controls an executable path.

4. A SYSTEM service reads that value.

5. The user can redirect the path to a controlled location.

6. The service subsequently uses that configuration.

7. The result crosses the local privilege boundary.
```


# Weak Finding

This is insufficient:

> Users have write access to a Registry key.

It does not explain:

```text
Which key?

Which value?

Which consumer?

Which privilege?

Which impact?
```


# Better Reporting

> The `BUILTIN\Users` group has `SetValue` permission on `HKLM\SOFTWARE\ExampleVendor\Service`, which contains the executable path used by a service running as `LocalSystem`. A standard local user can therefore modify security-sensitive service configuration that is consumed in a higher-privileged context.


# Finding Titles

Possible titles include:

```text
Insecure Registry Permissions Allow Local Privilege Escalation
```

or:

```text
Standard Users Can Modify Privileged Application Configuration
```

or, when service-specific:

```text
Writable Service Registry Configuration Allows Privileged Execution
```


# Severity

Severity depends on:

```text
Current user requirements

Registry rights

Consumer privilege

Trigger reliability

Application behaviour

Filesystem permissions

Application-control policy

User interaction

Operational conditions
```


# Do Not Inflate Severity

If the Registry key is writable but:

```text
No privileged consumer exists

or

The value cannot influence security-sensitive behaviour
```

then privilege escalation has not been established.


# Remediation

## Correct Registry ACLs

Remove unnecessary write permissions from standard users on security-sensitive machine-wide configuration.


# Principle

Privileged configuration should generally be writable only by:

```text
SYSTEM

Administrators

Explicitly required trusted service identities
```


# Least Privilege

Do not grant:

```text
FullControl
```

when only:

```text
Read
```

is required.


# Protect Parent Keys

If insecure permissions are inherited, correct the appropriate parent key rather than only individual children.


# Protect Referenced Files

Registry ACL remediation alone is insufficient when the referenced:

```text
Executable

Script

Plugin

Configuration file
```

remains user-writable.


# Secure Application Design

Applications running with elevated privileges should not trust mutable per-user Registry configuration for security-sensitive decisions.


# Validate Paths

Privileged applications should use:

```text
Explicit paths

Protected locations

Secure ACLs
```

for executable content.


# Avoid Secrets

Do not store plaintext:

```text
Passwords

API keys

Tokens

Connection credentials
```

in broadly readable Registry values.


# Use Appropriate Secret Storage

Where secrets must be stored locally, use platform-appropriate protected storage and restrict access according to the application security model.


# Group Policy

Where appropriate, enforce machine security settings centrally using managed policy.


# Application Control

Use:

```text
WDAC

AppLocker
```

as additional execution-control layers where appropriate.

They should complement secure Registry and filesystem permissions.


# Monitoring

Monitor changes to security-sensitive keys such as:

```text
Service configuration

Machine startup configuration

Security tooling configuration

Privileged application settings
```


# Remove Legacy Configuration

Delete obsolete:

```text
Vendor keys

Service keys

Startup entries

Update configuration

Application remnants
```

when no longer required.


# Retesting

Retesting should reproduce the original security chain.


# 1. Confirm Identity

Use the same privilege level as the original finding.

```cmd
whoami
```


# 2. Recheck Registry ACL

```powershell
(Get-Acl 'HKLM:\SOFTWARE\ExampleVendor').Access | Select-Object IdentityReference,RegistryRights,AccessControlType,IsInherited
```


# Expected

The affected standard user or group should no longer possess inappropriate:

```text
SetValue

CreateSubKey

WriteKey

FullControl
```


# 3. Recheck Configuration

```cmd
reg query "HKLM\SOFTWARE\ExampleVendor"
```


# 4. Recheck Filesystem

```cmd
icacls "C:\ProgramData\ExampleVendor"
```


# 5. Confirm Application Operation

Ensure the legitimate application or service continues to function.


# 6. Review Inheritance

Check whether weak permissions remain on:

```text
Parent keys

Sibling keys

Related vendor keys
```


# 7. Variant Analysis

Search for equivalent configurations created by the same product or installer.


# Retest Matrix

| Test | Expected After Fix |
|---|---|
| Standard user modifies sensitive key | Denied |
| Standard user creates sensitive subkey | Denied |
| Standard user redirects privileged executable | Denied |
| Referenced executable modification | Denied |
| Legitimate application operation | Success |
| Parent key inheritance | Secure |
| Equivalent vendor keys | Secure |


# Registry Assessment Workflow

```text
IDENTIFY CURRENT USER
        |
        v
ENUMERATE RELEVANT KEYS
        |
        v
REVIEW ACLs
        |
        v
IDENTIFY WRITABLE VALUES
        |
        v
CLASSIFY VALUE
        |
        +----------------+
        |                |
        v                v
   SECURITY-SENSITIVE   NORMAL DATA
        |                |
        v                v
IDENTIFY CONSUMER      LOW PRIORITY
        |
        v
IDENTIFY PRIVILEGE
        |
        v
TRACE REFERENCED RESOURCES
        |
        v
CHECK FILESYSTEM ACLs
        |
        v
IDENTIFY TRIGGER
        |
        v
VALIDATE IMPACT
        |
        v
REPORT
        |
        v
REMEDIATE
        |
        v
RETEST
```


# Defensible Conclusion Model

```text
Writable Registry Key
        |
        v
Not Enough
        |
        v
Security-Sensitive Value?
        |
        +------ No ------> No PrivEsc Finding
        |
       Yes
        |
        v
Privileged Consumer?
        |
        +------ No ------> Reclassify
        |
       Yes
        |
        v
User Can Influence Behaviour?
        |
        +------ No ------> No Demonstrated Path
        |
       Yes
        |
        v
Security Boundary Crossed
        |
        v
Defensible Finding
```


# Final Testing Principle

Registry testing is not:

```text
Find writable Registry key
        |
        v
Report privilege escalation
```

It is:

```text
FIND WRITABLE KEY
        |
        v
UNDERSTAND VALUE
        |
        v
IDENTIFY CONSUMER
        |
        v
IDENTIFY CONSUMER PRIVILEGE
        |
        v
TRACE DEPENDENCIES
        |
        v
VERIFY USER CONTROL
        |
        v
ESTABLISH SECURITY IMPACT
```


# Final Questions

For every interesting Registry key ask:

```text
Who owns this key?

Who can read it?

Who can modify values?

Who can create subkeys?

Are permissions inherited?

Does the current user belong to a permitted group?

What values exist?

Which values are security-sensitive?

Does a value contain an executable path?

Does it contain a script path?

Does it contain a plugin path?

Does it contain a command?

Does it contain credentials?

Does it contain a network location?

Which application reads the value?

Which service reads the value?

Which account runs that process?

Is that account more privileged than the current user?

When is the value consumed?

Can the user trigger the consumer?

Does the Registry value reference a file?

Who can modify that file?

Who can modify the parent directory?

Does application control affect execution?

Is the value machine-wide or per-user?

Does WOW64 Registry redirection matter?

Is the configuration managed by Group Policy?

Could the value be automatically restored?

Does the observed permission represent intended functionality?

Does modification actually cross a privilege boundary?

Can the issue be validated non-destructively?

What evidence proves the complete chain?

What is the root cause?

Does remediation need to occur at a parent key?

Are sibling keys affected by the same ACL?

Does the legitimate application still function after remediation?
```


# Related Windows Notes

- [Windows Overview](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [Windows PowerShell](powershell.md)
- [Windows Services](services.md)
- [Windows Scheduled Tasks](scheduled-tasks.md)
- [Windows Credentials](credentials.md)


# References

- [Microsoft Learn - Windows Registry](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Registry Hives](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-hives){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Registry Key Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-key-security-and-access-rights){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - reg query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg-query){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Get-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Registry Provider](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_registry_provider){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Modify Registry](https://attack.mitre.org/techniques/T1112/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Follow the consumer"

    A writable Registry key becomes security-relevant when you understand which process consumes it. Identify the process, its privilege level, the trigger and any referenced files before deciding whether the configuration creates a security boundary violation.


!!! tip "Correlate Registry and filesystem permissions"

    Registry configuration frequently points to executables, scripts, plugins and configuration files. Review both Registry ACLs and filesystem ACLs because either layer may provide the actual control point.


!!! tip "Use variant analysis"

    When one vendor key has insecure permissions, inspect related keys created by the same installer. Weak Registry ACLs frequently originate from a shared parent key or installation process.


!!! warning "Writable does not automatically mean vulnerable"

    Standard users are expected to control many HKCU settings. Even writable HKLM configuration does not automatically prove privilege escalation. Establish the privileged consumer and resulting security impact.


!!! warning "Do not modify operational Registry values unnecessarily"

    Changes to services, Winlogon, security controls and startup configuration can cause system instability or outages. Prefer ACL analysis and non-destructive validation during authorised assessments.
