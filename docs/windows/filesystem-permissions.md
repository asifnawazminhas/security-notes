---
title: Windows Filesystem Permissions
description: Practical Windows filesystem permission enumeration and security assessment covering NTFS ACLs, writable files and directories, privilege escalation paths, service and task dependencies, evidence collection, remediation and retesting.
---

# Windows Filesystem Permissions

Windows filesystem permissions determine which users and groups can read, create, modify, delete or otherwise control files and directories.

During a Windows security assessment, insecure NTFS permissions are particularly important because privileged services, scheduled tasks and applications frequently execute code or consume configuration from the filesystem.

A common privilege escalation pattern is:

```text
Low-Privilege User
        |
        v
Writable File or Directory
        |
        v
Privileged Process Dependency
        |
        v
SYSTEM / Administrator Execution
```

The important question is not simply:

```text
Can I write to this directory?
```

Instead ask:

```text
Can a lower-privileged user modify something
that a higher-privileged process trusts?
```

!!! warning "Authorised Security Testing"

    Perform filesystem permission testing only on systems included in the authorised assessment scope. Prefer ACL inspection and harmless probe files. Do not replace legitimate executables, scripts, DLLs or configuration files merely to demonstrate write access.


# Security Model

A useful model is:

```text
Security Principal
       |
       v
NTFS ACL
       |
       v
File / Directory
       |
       v
Privileged Consumer
       |
       v
Security Impact
```

A writable file or directory alone is not necessarily vulnerable.

A meaningful privilege escalation path normally requires:

```text
Lower-privileged write capability
+
Security-sensitive resource
+
Privileged consumer
+
Reachable execution or processing path
```


# NTFS Security Components

NTFS permissions involve:

```text
Owner

Discretionary ACL - DACL

Access Control Entries - ACEs

Allow entries

Deny entries

Inheritance

User and group membership

Effective permissions
```


# Current Security Context

Always establish the current identity before interpreting permissions.

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


# Why Group Membership Matters

A file may not explicitly grant permission to your username.

Instead, access may come from:

```text
BUILTIN\Users

Authenticated Users

Everyone

Domain Users

A local group

A domain group

A custom application group
```


# Basic Permission Enumeration

The primary built-in command-line tool is:

```text
icacls.exe
```


# Inspect a File

```cmd
icacls "C:\ProgramData\Example\worker.exe"
```


# Inspect a Directory

```cmd
icacls "C:\ProgramData\Example"
```


# PowerShell

```powershell
Get-Acl -LiteralPath 'C:\ProgramData\Example'
```


# Detailed PowerShell View

```powershell
Get-Acl -LiteralPath 'C:\ProgramData\Example' | Format-List *
```


# Access Entries

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Example').Access
```


# Compact ACL View

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Example').Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited,InheritanceFlags,PropagationFlags
```


# Common icacls Permissions

Common abbreviations include:

| Permission | Meaning |
|---|---|
| `F` | Full control |
| `M` | Modify |
| `RX` | Read and execute |
| `R` | Read |
| `W` | Write |


# Common Advanced Permissions

PowerShell may display more granular rights such as:

```text
FullControl

Modify

ReadAndExecute

Read

Write

CreateFiles

CreateDirectories

AppendData

WriteData

Delete

DeleteSubdirectoriesAndFiles

WriteAttributes

WriteExtendedAttributes

ChangePermissions

TakeOwnership
```


# High-Value Permissions

During privilege escalation analysis, pay particular attention to:

```text
FullControl

Modify

Write

WriteData

CreateFiles

CreateDirectories

Delete

DeleteSubdirectoriesAndFiles

ChangePermissions

TakeOwnership
```


# File vs Directory Permissions

This distinction is extremely important.

A file may be protected:

```text
C:\ProgramData\Company\service.exe
```

while its parent directory is writable:

```text
C:\ProgramData\Company
```


# Analysis Model

```text
Target File
    |
    +--> File ACL
    |
    +--> Parent Directory ACL
```

Always review both.


# Example

```cmd
icacls "C:\ProgramData\Company\service.exe"
```

Then:

```cmd
icacls "C:\ProgramData\Company"
```


# Why Parent Permissions Matter

Depending on the exact permissions and application behaviour, directory access may allow:

```text
Creating new files

Creating subdirectories

Deleting files

Replacing files

Renaming files

Introducing supporting dependencies
```


# Do Not Infer Replacement Automatically

Being able to create:

```text
test.txt
```

in a directory does not necessarily prove the user can overwrite:

```text
service.exe
```

The target file's ACL and directory permissions must be evaluated together.


# File Owner

PowerShell:

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Company\service.exe').Owner
```


# Directory Owner

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Company').Owner
```


# Ownership

Ownership can matter because an owner may have the ability to alter the object's security descriptor under applicable Windows security semantics.

However:

```text
Ownership != automatic exploitability
```

Evaluate actual effective control.


# Inheritance

NTFS permissions are commonly inherited from parent directories.

PowerShell:

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Company').Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited
```


# Example

```text
IdentityReference : BUILTIN\Users
FileSystemRights  : ReadAndExecute
AccessControlType : Allow
IsInherited       : True
```


# Why Inheritance Matters

Weak permissions applied to:

```text
C:\ProgramData\Vendor
```

may affect:

```text
C:\ProgramData\Vendor\App1

C:\ProgramData\Vendor\App2

C:\ProgramData\Vendor\Scripts

C:\ProgramData\Vendor\Plugins
```


# Variant Analysis

When one insecure directory is identified, inspect related child directories and files rather than treating the problem as a single isolated object.


# Inheritance Flags

PowerShell may display:

```text
ContainerInherit

ObjectInherit
```


# Conceptually

```text
ContainerInherit
    |
    v
Child directories

ObjectInherit
    |
    v
Child files
```


# Deny ACEs

Explicit deny entries can affect effective permissions.

Example:

```text
BUILTIN\Users:
Allow Modify

DOMAIN\User:
Deny Write
```

Do not interpret a single Allow ACE without considering the complete ACL.


# Effective Access

Effective access depends on:

```text
User SID

Group SIDs

Allow ACEs

Deny ACEs

Inheritance

Ownership

Token privileges
```


# Read Permissions

Read access may expose:

```text
Configuration files

Credentials

API keys

Connection strings

Scripts

Source code

Backups

Logs

Command history
```

Read access should therefore be assessed independently from write access.


# Write Permissions

Write access becomes especially important when the resource is trusted by:

```text
SYSTEM services

Administrator processes

Scheduled tasks

Backup agents

Monitoring agents

Deployment agents

Software updaters

Web services
```


# Writable Directory Discovery

A practical assessment frequently involves identifying directories writable by the current user.


# Safe Manual Check

For a known directory:

```powershell
Get-Acl -LiteralPath 'C:\ProgramData\Example' | Format-List Owner,AccessToString
```


# Harmless Write Probe

Where the engagement permits it:

```powershell
$folder = 'C:\ProgramData\Example'
$probe = Join-Path $folder "write-test-$PID.tmp"

try {
    'permission-test' | Set-Content -LiteralPath $probe -ErrorAction Stop
    Write-Host "[+] Writable: $folder"
    Remove-Item -LiteralPath $probe -Force -ErrorAction SilentlyContinue
}
catch {
    Write-Host "[-] Not writable: $folder"
}
```


# What This Proves

Successful creation proves:

```text
The current security context can create this test file
in this directory.
```

It does not automatically prove:

```text
Existing executable overwrite

Existing script overwrite

File deletion

Privileged code execution
```


# Test the Exact Capability Required

Security conclusions should correspond to the permission actually needed by the attack path.


# Example

Suppose a SYSTEM service executes:

```text
C:\ProgramData\Vendor\agent.exe
```

You identify:

```text
Directory creation:
Allowed
```

but:

```text
agent.exe modification:
Denied
```

This does not automatically prove executable replacement.

Further analysis is required.


# Writable Files

A direct writable executable or script is generally a stronger candidate than merely having limited write access somewhere in its parent tree.


# Check File ACL

```cmd
icacls "C:\ProgramData\Vendor\agent.exe"
```


# PowerShell

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Vendor\agent.exe').Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited
```


# Strong Candidate

Example:

```text
BUILTIN\Users:(M)
```

on:

```text
agent.exe
```

when the file is executed by a SYSTEM service.


# Privilege Escalation Model

```text
Standard User
      |
      v
Modify agent.exe
      |
      v
SYSTEM Service
      |
      v
Executes agent.exe
      |
      v
SYSTEM Context
```


# Important

Do not replace the executable during discovery.

First establish:

```text
Service identity

Executable path

ACL

Trigger

Application control

Operational impact
```


# Services

Services are one of the highest-value consumers of filesystem content.


# Enumerate Services

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```


# Find Non-Windows Paths

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -and
        $_.PathName -notmatch '^"?C:\\Windows\\'
    } |
    Select-Object Name,StartName,State,PathName
```


# Example

```text
Name      : VendorAgent
StartName : LocalSystem
State     : Running
PathName  : "C:\ProgramData\Vendor\agent.exe"
```


# Next Steps

Review:

```cmd
icacls "C:\ProgramData\Vendor\agent.exe"
```

and:

```cmd
icacls "C:\ProgramData\Vendor"
```


# Service Security

Filesystem permissions are only one component.

Also review:

```text
Service object permissions

Service configuration

Registry configuration
```


# Related Notes

See:

[Windows Services](services.md)

and:

[Windows Registry Security](registry.md)


# Scheduled Tasks

Scheduled tasks frequently execute:

```text
EXE files

PowerShell scripts

Batch files

VBScript

JavaScript

Administrative scripts
```


# Enumerate Actions

```powershell
Get-ScheduledTask | ForEach-Object {
    $task = $_

    foreach ($action in $task.Actions) {
        [PSCustomObject]@{
            TaskPath         = $task.TaskPath
            TaskName         = $task.TaskName
            User             = $task.Principal.UserId
            Execute          = $action.Execute
            Arguments        = $action.Arguments
            WorkingDirectory = $action.WorkingDirectory
        }
    }
}
```


# Example

```text
TaskName  : BackupJob
User      : SYSTEM
Execute   : powershell.exe
Arguments : -File C:\ProgramData\Backup\backup.ps1
```


# Check Script

```cmd
icacls "C:\ProgramData\Backup\backup.ps1"
```


# Check Directory

```cmd
icacls "C:\ProgramData\Backup"
```


# Related Note

See:

[Windows Scheduled Tasks](scheduled-tasks.md)


# Script Files

High-value extensions include:

```text
.ps1
.bat
.cmd
.vbs
.js
.py
```


# Search ProgramData for Scripts

```powershell
Get-ChildItem 'C:\ProgramData' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Extension -in '.ps1','.bat','.cmd','.vbs','.js','.py' |
    Select-Object FullName
```


# Do Not Assume Vulnerability

A script's existence under:

```text
C:\ProgramData
```

does not imply insecure permissions.

Check the ACL.


# Script Consumer

Also determine:

```text
Who executes it?

When?

Under which privilege?
```


# Configuration Files

Privileged applications may consume configuration files such as:

```text
.ini

.conf

.config

.xml

.json

.yaml

.yml

.properties
```


# Security Question

Can modifying the configuration influence:

```text
Executable path

Command

Script

Plugin

Module

Service endpoint

Update source

Authentication behaviour

File location
```


# Example

```text
C:\ProgramData\Vendor\agent.ini
```

Check:

```cmd
icacls "C:\ProgramData\Vendor\agent.ini"
```


# Writable Config != Automatic Code Execution

Suppose the user can change:

```text
LogLevel=Debug
```

That may not cross a privilege boundary.

But:

```text
PluginPath=C:\Somewhere\plugin.dll
```

may deserve deeper investigation.


# Establish the Sink

Ask:

```text
How does the privileged application use this value?
```


# Plugin Directories

Applications may load extensions from directories such as:

```text
plugins

modules

extensions

providers

drivers

addons
```


# Example

```text
C:\ProgramData\Vendor\Plugins
```


# Check ACL

```cmd
icacls "C:\ProgramData\Vendor\Plugins"
```


# Security Model

```text
Writable Plugin Directory
        |
        v
Privileged Application
        |
        v
Loads Plugins
        |
        v
Potential Privileged Execution
```


# Important

You must confirm that the privileged process actually loads content from the writable directory.


# DLL Dependencies

A protected executable may load DLLs from other directories.

A possible security path is:

```text
Privileged EXE
     |
     v
Loads DLL
     |
     v
Writable Search Location
     |
     v
Potential DLL Hijacking
```


# Do Not Infer DLL Hijacking from Writability Alone

DLL loading depends on:

```text
Application behaviour

DLL name

Load method

Search order

Known DLL handling

Safe DLL search mode

Application directory

PATH

Explicit paths
```


# Required Validation

Establish:

```text
Which DLL is requested?

Where Windows searches?

Whether the legitimate DLL exists?

Which location is selected?

Whether the attacker can control that location?

Which privilege loads it?
```


# Program Files

Typical application locations include:

```text
C:\Program Files

C:\Program Files (x86)
```


# Expected Security Posture

Standard users should generally have:

```text
Read

ReadAndExecute
```

rather than:

```text
Modify

FullControl
```

over installed application executables.


# Check Application Directory

```cmd
icacls "C:\Program Files\Example"
```


# ProgramData

`C:\ProgramData` is widely used for application data.

Some subdirectories legitimately require user write access.

Therefore:

```text
Writable ProgramData directory
```

is not automatically a finding.


# Security Question

Determine whether the directory contains or controls:

```text
Privileged executable content

Scripts

Plugins

Modules

Security-sensitive configuration
```


# Users Public Directory

Review privileged dependencies referencing:

```text
C:\Users\Public
```

because it may contain locations intentionally shared between users.


# Important

Again:

```text
Location != vulnerability
```

The ACL and privileged consumer determine the security impact.


# Temporary Directories

Common temporary locations include:

```text
C:\Windows\Temp

%TEMP%

%TMP%

User profile Temp directories
```


# Security Concern

Privileged applications should not blindly execute code from broadly writable temporary directories.


# Environment Variables

Check:

```powershell
$env:TEMP
$env:TMP
```


# System Temp

Often:

```text
C:\Windows\Temp
```


# Important

A writable temporary directory alone is expected in many environments.

The vulnerability requires a privileged process that unsafely trusts content from it.


# Missing Files

An interesting case occurs when a privileged process expects a file that does not exist.


# Example

```text
Privileged task expects:

C:\ProgramData\OldVendor\update.exe
```

Check:

```powershell
Test-Path -LiteralPath 'C:\ProgramData\OldVendor\update.exe'
```


# If Missing

```text
False
```


# Next Check

```cmd
icacls "C:\ProgramData\OldVendor"
```


# Security Pattern

```text
Privileged Consumer
       |
       v
Missing Dependency
       |
       v
Writable Parent
       |
       v
Potential File Planting
```


# Required Conditions

You still need to establish:

```text
Exact expected filename

Writable location

Consumer privilege

Consumer execution

Trigger
```


# Existing File vs Missing File

These are different permission problems.

```text
Existing File
    |
    v
Can user modify / replace it?

Missing File
    |
    v
Can user create it?
```


# CreateFiles Permission

Directory permissions that allow file creation may become relevant when a privileged application expects a missing file.


# Delete Permissions

Delete rights can be security-sensitive even when direct write access is absent.


# Why

In some configurations, a user may be able to:

```text
Delete existing object
+
Create replacement
```

depending on parent and target permissions.


# Do Not Simplify ACL Analysis

Windows delete semantics can involve rights on both:

```text
File

Parent directory
```

Inspect the actual permissions before reaching a conclusion.


# Rename Behaviour

Similarly, directory permissions may permit operations that are not obvious from a simple:

```text
Write = Yes/No
```

classification.


# Use Granular ACL Analysis

PowerShell:

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Example').Access |
    Format-Table IdentityReference,FileSystemRights,AccessControlType,IsInherited -AutoSize
```


# Network Shares

Files may also be consumed from UNC paths:

```text
\\server\share\script.ps1
```

A complete review requires both:

```text
Share permissions

NTFS permissions
```


# Share Permissions vs NTFS

Conceptually:

```text
Network Access
     |
     v
Share Permissions
     |
     v
NTFS Permissions
     |
     v
Effective Access
```


# Important

The most restrictive applicable access usually determines what the remote user can actually do.


# Privileged UNC Dependency

Example:

```text
SYSTEM scheduled task
        |
        v
\\fileserver\automation\backup.ps1
```

Ask:

```text
Who can modify the share?

Who can modify the file?

Which identity accesses the share?

Does the task successfully authenticate?
```


# Local vs Remote Context

A local SYSTEM account accessing a remote resource may authenticate differently from an interactive user.

Do not assume your own network access proves the task's access behaviour.


# Sensitive Files

Filesystem permissions also affect confidentiality.


# Common Sensitive Locations

Examples include:

```text
Application configuration

Backup files

Database configuration

Web configuration

Deployment scripts

Automation scripts

Logs

Exported Registry files

Credential files

Private keys

API configuration
```


# Search by Filename

Targeted examples:

```powershell
Get-ChildItem 'C:\ProgramData' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'password|credential|secret|token|backup|config'
    } |
    Select-Object FullName
```


# Important

Filename matching is only candidate discovery.

A file called:

```text
password-policy.txt
```

does not necessarily contain a password.


# Configuration File Search

Examples:

```powershell
Get-ChildItem 'C:\ProgramData' -Recurse -File -Include *.ini,*.config,*.xml,*.json,*.yml,*.yaml -ErrorAction SilentlyContinue |
    Select-Object FullName
```


# Avoid Excessive Collection

Do not indiscriminately read every configuration file.

Prioritize:

```text
Assessment-relevant applications

Privileged services

Known deployment tooling

Backup software

Web applications

Management agents
```


# Credential Search

When specifically authorised, targeted searches may look for terms such as:

```text
password

passwd

secret

token

apikey

connectionstring
```


# PowerShell Example

```powershell
Get-ChildItem 'C:\ProgramData\ExampleVendor' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password|passwd|secret|token|api.?key|connectionstring' -CaseSensitive:$false -ErrorAction SilentlyContinue
```


# Protect Evidence

If credentials are discovered:

```text
Do not expose them unnecessarily

Do not paste full secrets into reports

Redact screenshots

Follow evidence-handling requirements
```


# Backup Files

Common backup patterns include:

```text
*.bak

*.old

*.backup

*.save

*.copy

*.orig
```


# Search

```powershell
Get-ChildItem 'C:\ProgramData' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in '.bak','.old','.backup','.save','.orig'
    } |
    Select-Object FullName
```


# Security Relevance

Backups may contain:

```text
Old credentials

Previous configuration

Database strings

API keys

Source code

Historical secrets
```


# Log Files

Logs may expose:

```text
Tokens

URLs containing secrets

Usernames

Internal paths

Application errors

Authentication details
```


# Log Access

Readable logs are not automatically a vulnerability.

Determine whether they expose information that the user should not be able to access.


# Web Applications

Windows-hosted web applications may contain:

```text
web.config

appsettings.json

connection strings

deployment configuration

application secrets
```


# Example

```powershell
Get-ChildItem 'C:\inetpub' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -in 'web.config','appsettings.json','appsettings.Production.json'
    } |
    Select-Object FullName
```


# Important

Access should be evaluated relative to the expected trust boundary.

An administrator being able to read application configuration is different from a standard user being able to read a privileged service account credential.


# IIS

Typical IIS content may exist under:

```text
C:\inetpub\wwwroot
```

Review:

```text
Application pool identity

Directory ACLs

Upload directories

Configuration files

Writable web roots
```


# Writable Web Root

A writable web root may create security impact when:

```text
User can introduce server-executable content

and

The web server processes that content
```

This depends on:

```text
IIS configuration

Handler mappings

Application framework

Application pool identity

Application control
```


# Do Not Assume Execution

Being able to write:

```text
test.txt
```

to a web root does not prove server-side code execution.


# Application Control

Filesystem write access may be constrained by:

```text
AppLocker

Windows Defender Application Control

Antivirus

EDR

PowerShell policy
```


# Security Layers

```text
User Writable File
       |
       v
Privileged Consumer
       |
       v
Execution Control
       |
   +---+---+
   |       |
 Allow    Block
   |       |
   v       v
Impact   Reduced
```


# Important Reporting Distinction

If application control prevents execution, distinguish between:

```text
Underlying insecure ACL
```

and:

```text
Demonstrated privilege escalation
```

Do not claim successful privileged code execution when an effective control prevents it.


# AppLocker

Where accessible:

```powershell
Get-AppLockerPolicy -Effective
```


# Application Control Does Not Replace ACL Security

A privileged executable directory should not become user-writable merely because AppLocker currently blocks unsigned executables.

Controls can:

```text
Change

Be misconfigured

Have allowed execution paths

Apply differently to scripts, DLLs, MSI or packaged applications
```


# Reparse Points

Windows filesystems can contain reparse points such as:

```text
Symbolic links

Junctions

Mount points
```


# Enumerate Reparse Points

```powershell
Get-ChildItem 'C:\ProgramData\Example' -Force -ErrorAction SilentlyContinue |
    Where-Object Attributes -match 'ReparsePoint' |
    Select-Object FullName,Attributes,LinkType,Target
```


# Security Relevance

Reparse points can affect path resolution.

They become security-sensitive when a privileged application performs filesystem operations on paths that a lower-privileged user can redirect.


# Do Not Infer Vulnerability

The presence of a junction or symbolic link alone is not a security finding.

You need a privileged filesystem operation that follows or otherwise mishandles the redirected path.


# Hard Links

Hard-link behaviour may also matter in specific privileged file-operation scenarios.

Again, this requires application-specific validation rather than assuming exploitability from filesystem capabilities alone.


# TOCTOU

Time-of-check to time-of-use issues can occur when a privileged application:

```text
Checks a file
      |
      v
Time passes
      |
      v
Uses the file
```

and an attacker can change the relevant filesystem object between those operations.


# Security Model

```text
Check Trusted Path
      |
      v
Attacker Changes Object
      |
      v
Privileged Use
```


# Important

TOCTOU testing can be timing-sensitive and potentially disruptive.

Perform only when relevant to the application and explicitly permitted.


# Installer Directories

Installers and update agents may use:

```text
C:\ProgramData\Vendor\Updates

C:\Windows\Temp

Application cache directories

Package staging directories
```


# Security Questions

Ask:

```text
Who can write packages?

Who verifies package integrity?

Which account installs them?

Are filenames predictable?

Are signatures validated?

Can configuration redirect package sources?
```


# Update Security

A writable update directory is not automatically exploitable if the updater cryptographically validates packages before execution.


# Validate the Complete Trust Model

```text
Writable Package
      |
      v
Signature Validation?
      |
  +---+---+
  |       |
 Yes      No
  |       |
  v       v
Reduced   Investigate
```


# Backup Agents

Backup software often operates with significant privileges.

Review directories containing:

```text
Scripts

Hooks

Plugins

Pre-backup commands

Post-backup commands

Configuration
```


# Monitoring Agents

Monitoring software may execute:

```text
Custom checks

Plugins

Scripts

Health checks
```

Review whether lower-privileged users can modify these dependencies.


# Deployment Agents

CI/CD and deployment software on Windows can be high-value because it may run with elevated rights.

Review:

```text
Agent directory

Workspace permissions

Script directories

Package cache

Service identity

Credential files
```


# Workspace Writability

A writable workspace may be intentional.

The key question is whether:

```text
Privileged agent executes untrusted workspace content
```

without an appropriate trust boundary.


# Software Installation Directories

Enumerate potentially interesting non-standard directories:

```powershell
Get-ChildItem 'C:\' -Directory -Force -ErrorAction SilentlyContinue |
    Select-Object FullName
```


# Do Not Recursively Scan Everything Blindly

Recursive ACL enumeration across an entire system can be:

```text
Slow

Noisy

Difficult to interpret

Operationally expensive
```

Prioritize likely privileged dependency locations.


# Recommended Priority

```text
1. Privileged service executables

2. Scheduled task scripts

3. ProgramData application directories

4. Privileged application configuration

5. Plugin/module directories

6. Update directories

7. Backup/monitoring/deployment agents

8. Sensitive configuration files
```


# ACL Candidate Function

For assessment assistance, a PowerShell helper can summarize explicit ACL entries for a known path.

```powershell
function Get-PathAclSummary {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Warning "Path does not exist: $Path"
        return
    }

    $acl = Get-Acl -LiteralPath $Path

    [PSCustomObject]@{
        Path  = $Path
        Owner = $acl.Owner
    }

    $acl.Access |
        Select-Object IdentityReference,
                      FileSystemRights,
                      AccessControlType,
                      IsInherited,
                      InheritanceFlags,
                      PropagationFlags
}
```


# Usage

```powershell
Get-PathAclSummary -Path 'C:\ProgramData\Example'
```


# Why This Is Better Than "Writable = True"

Security assessment benefits from retaining:

```text
Identity

Exact rights

Allow/Deny

Inheritance
```

rather than reducing complex ACLs to a single Boolean value.


# Broadly Privileged Groups

Potentially interesting ACL principals include:

```text
Everyone

BUILTIN\Users

Authenticated Users

Domain Users
```

but their presence is not automatically insecure.


# Example Safe Permission

```text
BUILTIN\Users:(RX)
```

This generally provides:

```text
Read and execute
```

without modification.


# Example Candidate

```text
BUILTIN\Users:(M)
```

on a privileged executable directory deserves investigation.


# Everyone

Modern Windows permissions involving:

```text
Everyone
```

should be evaluated carefully.

The security impact depends on the exact rights and object.


# Authenticated Users

Likewise:

```text
Authenticated Users:(RX)
```

may be expected.

But:

```text
Authenticated Users:(M)
```

on privileged executable content is more concerning.


# Users

Do not report:

```text
Users has access
```

without specifying the exact access.

The difference between:

```text
ReadAndExecute
```

and:

```text
Modify
```

is fundamental.


# Full Control

`FullControl` is especially significant because it can include:

```text
Read

Write

Modify

Delete

Change permissions

Take ownership
```


# Modify

`Modify` generally permits substantial control over file content and deletion.

For privileged executable content, this is a strong candidate.


# Write

`Write` requires more careful interpretation.

Determine which granular rights are present and whether they permit the operation required by the attack path.


# CreateFiles

`CreateFiles` can be security-sensitive when a privileged application expects a missing predictable file.


# CreateDirectories

This can matter when a privileged application expects a missing directory or searches recursively through user-controlled paths.


# Delete

Delete rights may enable replacement patterns depending on parent directory and target permissions.


# ChangePermissions

A lower-privileged user able to change permissions on a privileged dependency may be able to grant themselves additional control.


# TakeOwnership

Similarly, ownership control may enable further ACL modification.

Treat it as a high-value permission requiring careful validation.


# Integrity Levels

Windows also uses mandatory integrity control.

Processes can operate at integrity levels such as:

```text
Low

Medium

High

System
```


# Current Integrity Context

One useful view is:

```cmd
whoami /groups
```

and inspect the mandatory label entry.


# Example

```text
Mandatory Label\Medium Mandatory Level
```


# Security Boundary

Filesystem ACLs and integrity controls are related but distinct.

A user may appear to have discretionary permissions while another Windows security mechanism affects the actual operation.


# UAC

An administrator running with a filtered token may operate at medium integrity until elevation.

Do not assume:

```text
Member of Administrators
```

means every process is currently executing with unrestricted administrative rights.


# Planned Related Note

```text
docs/windows/uac.md
```


# Safe Validation Workflow

Use this sequence:

```text
1. Identify privileged consumer

2. Identify exact dependency

3. Inspect file ACL

4. Inspect directory ACL

5. Determine current identity/group rights

6. Determine exact required filesystem operation

7. Use harmless write test where appropriate

8. Confirm consumer privilege

9. Confirm execution/processing path

10. Evaluate application control

11. Establish security impact

12. Capture evidence
```


# Why Start With the Consumer?

Starting from random writable directories often produces large numbers of irrelevant results.

A stronger approach is:

```text
Privileged Process
      |
      v
What does it trust?
      |
      v
Can I control any of those resources?
```


# Consumer-First Methodology

```text
SYSTEM Service
      |
      +--> EXE
      |
      +--> DLL
      |
      +--> Config
      |
      +--> Plugin
      |
      +--> Script
              |
              v
          Check ACL
```


# Scheduled-Task-First Methodology

```text
SYSTEM Task
     |
     v
PowerShell
     |
     v
backup.ps1
     |
     v
helper.exe
     |
     v
config.json
```

Review each security-sensitive dependency.


# Filesystem-First Methodology

Sometimes a writable directory is discovered first.

Then reverse the analysis:

```text
Writable Directory
       |
       v
What uses this?
       |
       +--> Service?
       |
       +--> Scheduled Task?
       |
       +--> Privileged Application?
       |
       +--> Updater?
       |
       +--> Backup Agent?
```


# Process Enumeration

Running processes can help identify applications of interest.

```powershell
Get-Process | Select-Object ProcessName,Id,Path -ErrorAction SilentlyContinue
```


# Important

Access to process paths may vary depending on privilege and process protection.


# Service Correlation

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```


# Installed Software Correlation

Registry inventory can identify applications associated with unusual writable directories.

See:

[Windows Registry Security](registry.md)


# Evidence Collection

For a filesystem privilege escalation finding, capture the complete chain.


# 1. Current User

```cmd
whoami
```


# 2. Group Membership

```cmd
whoami /groups
```


# 3. Privileged Consumer

Example:

```powershell
Get-CimInstance Win32_Service -Filter "Name='VendorAgent'" |
    Select-Object Name,StartName,State,PathName
```


# 4. File ACL

```cmd
icacls "C:\ProgramData\Vendor\agent.exe"
```


# 5. Directory ACL

```cmd
icacls "C:\ProgramData\Vendor"
```


# 6. PowerShell ACL

```powershell
(Get-Acl -LiteralPath 'C:\ProgramData\Vendor\agent.exe').Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited
```


# 7. Runtime Evidence

Establish that the privileged consumer actually uses the dependency.


# 8. Safe Write Validation

If required and permitted, create a separate harmless test file rather than altering the dependency.


# 9. Application Control

Document relevant execution restrictions where they affect exploitability.


# Evidence Chain

```text
Standard User
      |
      v
Group Membership
      |
      v
Modify Permission
      |
      v
Privileged Dependency
      |
      v
SYSTEM Consumer
      |
      v
Execution / Processing
      |
      v
Privilege Boundary
```


# Strong Finding

A strong finding establishes:

```text
1. Current user is lower privileged.

2. The user or one of their groups has relevant write rights.

3. The affected file is security-sensitive.

4. A higher-privileged process consumes it.

5. The dependency is reachable.

6. Relevant controls do not invalidate the path.

7. Security impact follows from the user-controlled dependency.
```


# Weak Finding

This is insufficient:

> `C:\ProgramData\Vendor` is writable.

It does not establish:

```text
What is writable?

Which exact permission exists?

What uses the directory?

Which privilege is involved?

What security boundary is crossed?
```


# Better Finding

> The `BUILTIN\Users` group has `Modify` permission over `C:\ProgramData\Vendor\agent.exe`. The executable is launched by the `VendorAgent` Windows service running as `LocalSystem`. A standard local user can therefore modify executable content trusted by a SYSTEM-level service.


# Finding Titles

Suitable titles include:

```text
Insecure Filesystem Permissions Allow Local Privilege Escalation
```

or:

```text
Standard Users Can Modify a SYSTEM Service Executable
```

or:

```text
Writable Privileged Application Directory Allows Local Privilege Escalation
```


# Sensitive File Finding

For confidentiality issues:

```text
Sensitive Application Configuration Accessible to Standard Users
```


# Severity Factors

Severity depends on:

```text
Required local access

Current privilege

Exact filesystem rights

Consumer privilege

Execution frequency

Trigger requirements

User interaction

Application control

Reliability

Operational conditions
```


# High-Risk Pattern

```text
Standard User
+
Modify on EXE
+
SYSTEM Service
+
Automatic Start
+
No Effective Execution Restriction
```


# Lower-Risk Pattern

```text
Writable Directory
+
No Privileged Consumer
+
No Security-Sensitive Content
```

This may not represent a vulnerability at all.


# False Positive - Writable ProgramData

Observation:

```text
C:\ProgramData\Vendor\Data
```

is writable.

If it contains only user-generated data and no privileged process interprets that data as code or trusted configuration, privilege escalation is not established.


# False Positive - Writable Log

A privileged process writing to a log that users can also write does not automatically provide code execution.


# False Positive - Same User Consumer

```text
Current user:
UserA

Consumer:
UserA
```

A writable script executed by the same security context normally does not cross a privilege boundary.


# False Positive - Read and Execute

```text
Users:(RX)
```

does not provide modification capability.


# False Positive - Writable Config with Harmless Setting

If the only user-controlled setting is:

```text
WindowSize=Large
```

there may be no security impact.


# False Positive - Writable Temp

A writable temporary directory is common.

You need a privileged application that unsafely trusts predictable content from it.


# False Positive - Missing File

A missing file alone is not exploitable.

The user must be able to create it at the exact expected location, and the privileged consumer must use it.


# False Positive - Application Control Blocks Execution

If modified code cannot execute because of an effective application-control policy, do not claim successful code execution.

Still assess whether the insecure ACL itself should be remediated.


# Alternative Explanations

Unexpected permissions may result from:

```text
Vendor application requirements

Shared application data

Legacy software

Installer behaviour

Multi-user workstation requirements

Development tooling

Update staging

Backup software
```

Determine whether the permission is genuinely required.


# Reporting Principle

Do not report:

```text
Permission is unusual
```

as equivalent to:

```text
Permission crosses a security boundary
```


# Remediation

The primary remediation is to remove unnecessary write access from files and directories trusted by privileged processes.


# Protect Executables

Privileged executables should generally be writable only by trusted administrative identities.


# Protect Scripts

Scripts executed by privileged services or scheduled tasks should not be modifiable by standard users.


# Protect Configuration

Security-sensitive configuration should be protected according to the privilege of the consuming application.


# Protect Plugin Directories

Only trusted administrators or designated service identities should be able to modify privileged application plugins or modules.


# Protect Parent Directories

Do not correct only the target file while leaving a replacement path through its parent directory.


# Least Privilege

Grant only the permissions required for normal operation.


# Avoid Broad Permissions

Avoid unnecessary:

```text
Everyone:(F)

Users:(F)

Authenticated Users:(M)
```

on privileged application content.


# Separate Data and Executable Content

Where an application requires user-writable data, separate it from:

```text
Executables

Scripts

Plugins

Security-sensitive configuration
```


# Example Design

```text
C:\Program Files\Vendor\
    binaries
    administrators write only

C:\ProgramData\Vendor\Data\
    application data
    limited user write where required
```


# Secure Update Mechanisms

Privileged updaters should:

```text
Validate package integrity

Use protected staging locations

Validate signatures where appropriate

Avoid predictable unsafe file replacement
```


# Secure Temporary Operations

Privileged applications should:

```text
Use secure temporary-file creation

Avoid predictable filenames

Validate ownership and permissions

Avoid trusting user-controlled paths
```


# Application Control

Use:

```text
WDAC

AppLocker
```

as defense in depth.

Do not use application control as justification for insecure NTFS permissions.


# Monitoring

Monitor changes to:

```text
Service executables

Scheduled task scripts

Privileged configuration

Plugin directories

Security tooling

Deployment agents
```


# Remove Obsolete Content

Remove:

```text
Old scripts

Unused binaries

Legacy backups

Orphaned updater files

Deprecated configuration
```

when no longer required.


# Retesting

Retesting should reproduce the original permission and consumer analysis.


# Step 1 - Same User

Use the same low-privileged identity.

```cmd
whoami
```


# Step 2 - File ACL

```cmd
icacls "C:\ProgramData\Vendor\agent.exe"
```


# Step 3 - Directory ACL

```cmd
icacls "C:\ProgramData\Vendor"
```


# Step 4 - Effective Capability

Where permitted, repeat the harmless write test.


# Expected

If write access is no longer required:

```text
Access denied
```


# Step 5 - Consumer

Confirm the legitimate service, task or application still works.


# Step 6 - Related Dependencies

Review:

```text
Scripts

Plugins

Configuration

Helper executables

Sibling directories
```


# Step 7 - Inheritance

Ensure insecure permissions are not still inherited from a parent.


# Step 8 - Variant Analysis

Search for equivalent permissions created by the same installer or product.


# Retest Matrix

| Test | Expected After Fix |
|---|---|
| Standard user modifies privileged EXE | Denied |
| Standard user modifies privileged script | Denied |
| Standard user modifies privileged config | Denied unless explicitly required |
| Standard user creates executable in protected directory | Denied |
| Standard user deletes privileged dependency | Denied |
| Legitimate service executes | Success |
| Legitimate scheduled task executes | Success |
| Application functionality | Preserved |
| Parent ACL | Secure |
| Related directories | Secure |


# Assessment Checklist

## Identity

- [ ] Current user identified
- [ ] Group membership identified
- [ ] Token privileges reviewed
- [ ] Integrity context understood

## Filesystem

- [ ] File ACL reviewed
- [ ] Directory ACL reviewed
- [ ] Owner reviewed
- [ ] Inheritance reviewed
- [ ] Allow ACEs reviewed
- [ ] Deny ACEs reviewed
- [ ] Effective permissions considered

## Write Rights

- [ ] FullControl identified
- [ ] Modify identified
- [ ] Write identified
- [ ] CreateFiles identified
- [ ] CreateDirectories identified
- [ ] Delete rights considered
- [ ] ChangePermissions considered
- [ ] TakeOwnership considered

## Services

- [ ] Service executable paths reviewed
- [ ] Service account identified
- [ ] Executable ACL reviewed
- [ ] Parent directory ACL reviewed
- [ ] Service configuration correlated

## Scheduled Tasks

- [ ] Task actions reviewed
- [ ] Task principal identified
- [ ] Scripts reviewed
- [ ] Executables reviewed
- [ ] Working directories reviewed
- [ ] Parent ACLs reviewed

## Applications

- [ ] ProgramData reviewed
- [ ] Non-standard application directories reviewed
- [ ] Configuration files reviewed
- [ ] Plugin directories reviewed
- [ ] Module directories reviewed
- [ ] Update directories reviewed
- [ ] Backup agents reviewed
- [ ] Monitoring agents reviewed
- [ ] Deployment agents reviewed

## Dependencies

- [ ] Helper executables reviewed
- [ ] DLL dependencies considered
- [ ] Missing files considered
- [ ] Relative paths considered
- [ ] Environment paths considered
- [ ] UNC dependencies considered
- [ ] Share permissions considered
- [ ] NTFS permissions considered

## Sensitive Data

- [ ] Configuration files reviewed where relevant
- [ ] Backup files reviewed
- [ ] Logs reviewed where relevant
- [ ] Credential exposure considered
- [ ] Secrets redacted
- [ ] Unnecessary sensitive data not collected

## Advanced Filesystem Behaviour

- [ ] Reparse points considered where relevant
- [ ] Junctions considered
- [ ] Symbolic links considered
- [ ] TOCTOU considered where relevant
- [ ] Temporary file handling considered

## Application Control

- [ ] AppLocker considered
- [ ] WDAC considered
- [ ] Antivirus/EDR context considered
- [ ] ACL weakness distinguished from executable impact

## Validation

- [ ] Privileged consumer identified
- [ ] Consumer privilege established
- [ ] Exact dependency identified
- [ ] Exact user-controlled permission identified
- [ ] Trigger understood
- [ ] Harmless validation preferred
- [ ] Security boundary established
- [ ] Alternative explanations excluded

## Evidence

- [ ] Current identity captured
- [ ] Group membership captured
- [ ] Consumer captured
- [ ] File ACL captured
- [ ] Directory ACL captured
- [ ] Runtime evidence captured
- [ ] Safe write test captured where required
- [ ] Application-control context captured

## Reporting

- [ ] Exact path reported
- [ ] Exact ACL reported
- [ ] Affected group reported
- [ ] Privileged consumer reported
- [ ] Execution context reported
- [ ] Impact supported by evidence
- [ ] Root cause described
- [ ] Remediation addresses file and directory ACLs

## Retesting

- [ ] Same low-privileged account used
- [ ] Original write capability retested
- [ ] File ACL corrected
- [ ] Directory ACL corrected
- [ ] Inheritance corrected
- [ ] Legitimate functionality preserved
- [ ] Equivalent paths reviewed


# Quick Reference

| Goal | Command |
|---|---|
| Current user | `whoami` |
| Groups | `whoami /groups` |
| Privileges | `whoami /priv` |
| File ACL | `icacls "C:\Path\File"` |
| Directory ACL | `icacls "C:\Path"` |
| PowerShell ACL | `Get-Acl -LiteralPath 'C:\Path'` |
| ACL entries | `(Get-Acl -LiteralPath 'C:\Path').Access` |
| Owner | `(Get-Acl -LiteralPath 'C:\Path').Owner` |
| Test existence | `Test-Path -LiteralPath 'C:\Path\File'` |
| Services | `Get-CimInstance Win32_Service` |
| Scheduled tasks | `Get-ScheduledTask` |


# Permission Interpretation Matrix

| Permission | Security Relevance |
|---|---|
| Read | Confidentiality review |
| ReadAndExecute | Usually expected for installed programs |
| Write | Investigate exact granular rights |
| Modify | Strong candidate for trusted content |
| FullControl | High-value candidate |
| CreateFiles | Relevant to missing-file planting |
| CreateDirectories | Relevant to directory creation paths |
| Delete | May enable replacement scenarios |
| ChangePermissions | Can enable further control |
| TakeOwnership | Can enable ACL modification paths |


# Candidate Matrix

| Resource | Privileged Consumer | User Right | Priority |
|---|---|---|---|
| Service EXE | SYSTEM | Modify | Critical review |
| Task script | SYSTEM | Modify | Critical review |
| Plugin directory | SYSTEM service | CreateFiles | High review |
| Config file controlling command | SYSTEM | Modify | Critical review |
| Missing task EXE directory | SYSTEM | CreateFiles | Critical review |
| Application data | SYSTEM | Write | Context dependent |
| User script | Same user | Modify | Usually no PrivEsc |
| Log directory | Privileged app | Write | Usually low unless interpreted |
| Temp directory | Privileged app | Write | Requires unsafe consumer |


# Consumer Matrix

| Consumer | Files to Review |
|---|---|
| Windows service | EXE, DLL, config, plugins |
| Scheduled task | EXE, script, config, working directory |
| Backup agent | Scripts, hooks, plugins, config |
| Monitoring agent | Plugins, scripts, checks |
| Updater | Packages, staging directory, config |
| Web server | Web root, config, upload directories |
| Deployment agent | Workspace, scripts, packages |
| Privileged desktop app | Plugins, config, helper executables |


# Evidence Matrix

| Evidence | Purpose |
|---|---|
| `whoami` | Establish current identity |
| `whoami /groups` | Establish inherited access |
| `icacls` file | Establish file rights |
| `icacls` directory | Establish parent rights |
| `Get-Acl` | Detailed ACL analysis |
| Service configuration | Establish privileged consumer |
| Scheduled task action | Establish dependency |
| Safe probe | Establish actual directory creation capability |
| Application-control policy | Establish execution constraints |
| Runtime evidence | Establish dependency is actually consumed |


# Remediation Matrix

| Weakness | Remediation |
|---|---|
| Writable service executable | Remove standard-user write rights |
| Writable task script | Restrict script ACL |
| Writable application directory | Separate writable data and protected code |
| Writable plugin directory | Restrict plugin installation |
| Writable privileged config | Restrict configuration ACL |
| Missing dependency in writable path | Remove reference or secure directory |
| Weak inherited ACL | Correct parent ACL |
| Sensitive readable config | Restrict read access and protect secrets |
| Unsafe update staging | Protect staging and validate packages |
| Broad FullControl | Apply least privilege |


# Practical Validation Model

```text
WHEN THIS APPLIES
      |
      v
Privileged process trusts filesystem resource
      |
      v
IDENTIFY RESOURCE
      |
      v
INSPECT ACL
      |
      v
IDENTIFY USER RIGHTS
      |
      v
CONFIRM PRIVILEGED CONSUMER
      |
      v
CONFIRM RESOURCE IS USED
      |
      v
SAFE VALIDATION
      |
      v
INTERPRET RESULT
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


# Positive Result

A positive result supporting privilege escalation could be:

```text
Current identity:
DOMAIN\StandardUser

Group:
BUILTIN\Users

File:
C:\ProgramData\Vendor\agent.exe

Permission:
BUILTIN\Users = Modify

Consumer:
VendorAgent service

Service account:
LocalSystem

Service state:
Running
```

This establishes a strong security chain requiring final validation of execution conditions and applicable mitigations.


# Negative Result

Example:

```text
File:
Administrators = FullControl
SYSTEM = FullControl
Users = ReadAndExecute

Parent:
Administrators = FullControl
SYSTEM = FullControl
Users = ReadAndExecute
```

If no other controllable dependency exists, the filesystem path does not support the suspected privilege escalation.


# Further Validation

When a candidate is identified:

```text
Confirm exact consumer

Confirm security context

Confirm trigger

Review related files

Review application control

Review Registry configuration

Review service/task permissions

Validate effective write capability where necessary
```


# Reporting Conclusion Model

A defensible conclusion should answer:

```text
WHO can modify WHAT?

WHO trusts it?

AT WHAT privilege?

WHEN is it consumed?

WHAT security boundary is crossed?
```


# Final Testing Principle

Filesystem permission testing is not:

```text
Find writable folder
      |
      v
Report privilege escalation
```

It is:

```text
IDENTIFY TRUSTED RESOURCE
        |
        v
IDENTIFY PRIVILEGED CONSUMER
        |
        v
INSPECT FILE ACL
        |
        v
INSPECT DIRECTORY ACL
        |
        v
ESTABLISH USER CONTROL
        |
        v
ESTABLISH EXECUTION / PROCESSING
        |
        v
ESTABLISH PRIVILEGE BOUNDARY
```


# Final Questions

For every interesting file or directory ask:

```text
Who owns this object?

Which users can read it?

Which users can modify it?

Which users can create files here?

Which users can delete content?

Which permissions are inherited?

Are there explicit deny entries?

Which group gives the current user access?

Is the target itself writable?

Is the parent directory writable?

Can the current user create a harmless file?

Can the current user modify the existing dependency?

Can the current user delete it?

Can the current user replace it?

Is the expected dependency currently missing?

Can the current user create the missing dependency?

Which process uses this file?

Which service uses it?

Which scheduled task uses it?

Which account does the consumer run as?

Is that account more privileged?

When is the dependency consumed?

Can the current user trigger the consumer?

Does the application load plugins?

Does it load DLLs?

Does it execute scripts?

Does it consume writable configuration?

Does the configuration influence execution?

Does it use relative paths?

Does it use a writable working directory?

Does it use temporary files?

Does it use a network share?

What are the share permissions?

What are the NTFS permissions?

Does application control prevent execution?

Does the observed condition actually cross a privilege boundary?

Can the issue be demonstrated without modifying production content?

What evidence proves the complete chain?

Are sibling files or directories affected?

Is the weak permission inherited from a parent?

What is the correct root-cause remediation?

Does legitimate functionality still work after the ACL is corrected?
```


# Related Windows Notes

- [Windows Overview](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [Windows PowerShell](powershell.md)
- [Windows Services](services.md)
- [Windows Scheduled Tasks](scheduled-tasks.md)
- [Windows Registry Security](registry.md)
- [Windows Credentials](credentials.md)


# References

- [Microsoft Learn - File Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Access Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Access Control Lists](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-lists){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Access Control Entries](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-entries){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Get-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - FileSystemAccessRule](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.filesystemaccessrule){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - File and Directory Permissions Modification](https://attack.mitre.org/techniques/T1222/001/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Start from privileged consumers"

    Instead of scanning every writable directory on the system, begin with SYSTEM services, privileged scheduled tasks, update agents, backup software and other high-privilege applications. Trace the files they trust and then inspect those ACLs.


!!! tip "Check both the file and its parent"

    A secure file ACL does not automatically mean the dependency is safe. Parent directory permissions may permit creation, deletion or replacement operations that affect the trusted resource.


!!! tip "Record the exact permission"

    Avoid reducing NTFS permissions to a generic "writable" label. Record whether the user has Modify, Write, CreateFiles, Delete, FullControl or another specific right because the security impact depends on the operation actually permitted.


!!! tip "Separate code from writable data"

    Applications often need writable data directories. That is safer when executable files, scripts, plugins and security-sensitive configuration are stored separately in administrator-controlled locations.


!!! warning "Writable does not mean exploitable"

    Writable ProgramData, temporary and application-data directories are common. A privilege escalation finding requires a privileged consumer that trusts attacker-controlled content in a security-sensitive way.


!!! warning "Prefer non-destructive validation"

    Do not replace legitimate executables, scripts, DLLs or configuration files simply to prove filesystem write access. Use ACL analysis and harmless temporary probe files whenever they provide sufficient evidence.
