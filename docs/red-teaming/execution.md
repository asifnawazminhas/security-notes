---
title: Red Team Execution
description: Execution methodology for authorised red team assessments, covering execution context, interpreters, native binaries, scripts, application control, PowerShell, Windows and Linux execution, remote execution, LOLBins, payload handling, telemetry, detection validation, evidence, cleanup, and reporting.
---

# Red Team Execution

Execution is the stage where an attacker causes code, commands, scripts, or applications to run on a target system.

Within an authorised red team assessment, execution testing should answer:

```text
What can execute?

Under which identity?

With which privileges?

From which locations?

Which interpreters are available?

Which application-control policies apply?

Which endpoint controls inspect execution?

What telemetry is generated?

Is suspicious execution detected?

Can defenders reconstruct what happened?
```

Execution should not be treated as:

```text
Payload runs = security control bypassed
```

Instead, evaluate the complete control path:

```text
Execution Attempt
      |
      v
Application Control
      |
      v
Endpoint Prevention
      |
      v
Execution
      |
      v
Telemetry
      |
      v
Detection
      |
      v
Response
```

!!! warning "Authorised testing only"
    Execute commands, scripts, binaries, and remote administration activity only on explicitly authorised systems. Prefer harmless validation artifacts and minimal-impact techniques when determining whether an execution boundary exists.


---

# Execution Objectives

Common objectives include:

```text
Determine available execution mechanisms

Determine execution context

Identify interpreters

Identify application-control boundaries

Identify writable execution locations

Validate script-control policies

Validate endpoint prevention

Validate execution telemetry

Validate detection logic

Understand remote execution boundaries

Determine whether execution enables the next attack phase
```


---

# Execution in the Attack Chain

```text
Initial Access
      |
      v
Execution
      |
      v
Foothold
      |
      v
Discovery
      |
      v
Privilege Escalation
      |
      v
Credential Access
      |
      v
Lateral Movement
```


---

# Execution Is a Security Boundary

The important question is not merely:

```text
Can I run a command?
```

Ask:

```text
What should this identity be allowed to execute?

What should be blocked?

Which locations are trusted?

Which binaries are permitted?

Which scripts are permitted?

Which interpreters are available?

Which controls enforce those decisions?
```


---

# Execution Context

Always determine the current execution context first.

Record:

```text
Hostname

Username

Domain

Groups

Integrity level

Privileges

Architecture

Operating system

Shell

Working directory

Environment

Security controls
```


---

# Windows Context

Current user:

```powershell
whoami
```

Detailed identity information:

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

Hostname:

```powershell
hostname
```

Environment:

```powershell
Get-ChildItem Env:
```


---

# Windows Architecture

```powershell
$env:PROCESSOR_ARCHITECTURE
```

Operating-system architecture:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,OSArchitecture
```


---

# PowerShell Version

```powershell
$PSVersionTable
```

Useful fields include:

```text
PSVersion

PSEdition

OS

Platform

CLRVersion
```


---

# PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Common values include:

```text
FullLanguage

ConstrainedLanguage

RestrictedLanguage

NoLanguage
```


---

# FullLanguage

`FullLanguage` provides the normal PowerShell language capabilities.

Its presence is not automatically a vulnerability.

Evaluate:

```text
User privilege

Application control

Script controls

AMSI

Endpoint security

Logging

Allowed operations
```


---

# Constrained Language Mode

PowerShell Constrained Language Mode, or CLM, restricts certain PowerShell capabilities.

Typical restrictions affect:

```text
Arbitrary .NET type access

COM interaction

Type creation

Some method invocation

Advanced scripting functionality
```

CLM is most useful when enforced as part of a broader application-control architecture.


---

# Safe CLM Validation

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

A harmless restricted-operation test can help determine whether language restrictions are actually enforced.

For example:

```powershell
Add-Type -TypeDefinition 'public class ExecutionControlTest { public static string Value = "test"; }'
```

Under a restricted language environment, this may be prevented.

The goal is to validate the boundary, not to bypass it.


---

# Execution Policy

Check:

```powershell
Get-ExecutionPolicy -List
```

Possible scopes include:

```text
MachinePolicy

UserPolicy

Process

CurrentUser

LocalMachine
```


---

# Execution Policy Is Not Application Control

PowerShell Execution Policy should not be treated as a strong security boundary by itself.

It primarily helps control script execution behaviour.

Stronger controls include:

```text
AppLocker

Windows Defender Application Control

Endpoint security

Privilege management

Script logging

AMSI
```


---

# Windows Shells and Interpreters

Common execution environments include:

```text
cmd.exe

powershell.exe

pwsh.exe

wscript.exe

cscript.exe

mshta.exe

python.exe

java.exe
```

Their presence does not mean they are unrestricted.


---

# Check Command Availability

PowerShell:

```powershell
Get-Command powershell.exe -ErrorAction SilentlyContinue
Get-Command cmd.exe -ErrorAction SilentlyContinue
Get-Command wscript.exe -ErrorAction SilentlyContinue
Get-Command cscript.exe -ErrorAction SilentlyContinue
Get-Command mshta.exe -ErrorAction SilentlyContinue
```

This confirms discovery, not successful execution.


---

# Execution States

Distinguish:

```text
Binary Exists

Binary Launches

Command Executes

Child Process Executes

Payload Executes

Control Blocks

Control Detects

SOC Responds
```

These are different observations.


---

# Simple Windows Execution Test

A minimal command:

```powershell
cmd.exe /c echo Execution test
```

PowerShell:

```powershell
Write-Output "Execution test"
```

These establish basic command execution without introducing a payload.


---

# Process Creation

List processes:

```powershell
Get-Process
```

Detailed process information:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
```


---

# Parent-Child Relationships

Execution often creates a process tree.

Example:

```text
explorer.exe
    |
    v
powershell.exe
    |
    v
cmd.exe
```

Defenders frequently analyse parent-child relationships rather than individual process names alone.


---

# Process Tree Questions

Ask:

```text
Who started the process?

What started it?

Which command line was used?

Which user executed it?

Was elevation involved?

Was the process signed?

Did it access the network?

Did it create additional processes?
```


---

# Windows Event 4688

If process creation auditing is enabled, Windows Security Event ID `4688` can record process creation.

Defenders may observe:

```text
New process name

Creator process

Account

Process ID

Command line
```

Command-line availability depends on auditing configuration.


---

# Process Creation Audit Policy

Review relevant audit configuration:

```powershell
auditpol /get /subcategory:"Process Creation"
```

This helps determine whether process execution should be visible in the Security log.


---

# Sysmon

Sysmon can provide additional process telemetry when deployed.

Common useful telemetry includes:

```text
Process creation

Network connections

Image loading

File creation

Registry modification

DNS activity
```

Sysmon Event ID `1` represents process creation.


---

# Windows Defender

Check Microsoft Defender status:

```powershell
Get-MpComputerStatus
```

Useful fields:

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusEnabled,
                  RealTimeProtectionEnabled,
                  BehaviorMonitorEnabled,
                  IoavProtectionEnabled,
                  AntispywareEnabled
```


---

# Defender Version

```powershell
Get-MpComputerStatus |
    Select-Object AMEngineVersion,
                  AMProductVersion,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```


---

# EICAR Validation

The EICAR test file is designed to validate antivirus detection without using real malware.

Canonical EICAR test string:

```text
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

Create the test artifact:

```powershell
$eicar = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
Set-Content -Path "$env:TEMP\eicar.com.txt" -Value $eicar -NoNewline
```

Expected behaviour depends on endpoint configuration.

Possible outcomes:

```text
Creation blocked

File quarantined

Detection generated

Alert generated

File remains but detection recorded
```


---

# Review Defender Detection

```powershell
Get-MpThreatDetection
```

Also review:

```text
Applications and Services Logs
    |
    Microsoft
        |
        Windows
            |
            Windows Defender
                |
                Operational
```


---

# Defender Event Log

PowerShell:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-Windows Defender/Operational" -MaxEvents 30
```

Review events around the test timestamp.


---

# EICAR Interpretation

If EICAR is blocked:

```text
Antivirus signature validation succeeded.
```

It does not prove:

```text
Every malicious technique will be blocked.
```

Likewise, if a behavioural simulation executes, that does not automatically prove the endpoint product has been bypassed.


---

# AMSI

The Antimalware Scan Interface provides an interface through which applications can submit content to antimalware products for inspection.

AMSI commonly applies to environments such as:

```text
PowerShell

Windows Script Host

JavaScript

VBScript

Other integrated applications
```


---

# AMSI Model

```text
Script Content
      |
      v
Script Host
      |
      v
AMSI
      |
      v
Antimalware Provider
      |
      v
Allow / Detect / Block
```


---

# AMSI Validation

The objective should be to determine:

```text
Is AMSI-integrated inspection present?

Does suspicious test content generate telemetry?

Does endpoint security respond?

Are detections forwarded centrally?
```

A red team report should distinguish an AMSI control observation from a claim that AMSI itself was defeated.


---

# AMSI Bypass Assessment

During an authorised assessment, bypass resistance may be evaluated conceptually across areas such as:

```text
AMSI integration

Script content inspection

Runtime protections

Application control

Behaviour monitoring

EDR telemetry

Detection engineering
```

Avoid treating one execution result as proof of a universal AMSI bypass.


---

# Application Control

Execution may be governed by:

```text
AppLocker

Windows Defender Application Control

Software Restriction Policies

Endpoint security

Privilege-management products
```


---

# AppLocker

Check the effective AppLocker policy:

```powershell
Get-AppLockerPolicy -Effective
```

Review collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```

Possible collections include:

```text
Exe

Msi

Script

Dll

Appx
```


---

# AppLocker Enforcement

Possible enforcement modes include:

```text
Enabled

AuditOnly

NotConfigured
```

An enabled collection does not necessarily mean every execution path is restricted.


---

# AppLocker Policy Details

```powershell
Get-AppLockerPolicy -Effective -Xml
```

Review:

```text
Path rules

Publisher rules

Hash rules

Exceptions

User/group scope
```


---

# Test-AppLockerPolicy

A useful safe validation mechanism is:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\wscript.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

Possible result:

```text
Allowed
```

or:

```text
Denied
```


---

# Test a Specific File

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "C:\Path\To\Test.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

This checks the effective policy decision without requiring execution.


---

# AppLocker Path Rules

A rule such as:

```text
%WINDIR%\*
```

allows files matching that path according to the rule's scope and collection.

The security question becomes:

```text
Can a lower-privileged user modify locations covered by an
allow rule?
```


---

# Writable Trusted Locations

A potentially important control condition is:

```text
Writable by Standard User
          +
Allowed by Application Control
          =
Potential Execution-Control Weakness
```

Both conditions should be validated.


---

# Test Directory Permissions

Example:

```powershell
Get-Acl -LiteralPath "C:\ProgramData\CandidateFolder" |
    Format-List Owner,AccessToString
```

Do not assume a directory is writable solely because of its location.


---

# Safe Write Test

```powershell
$folder = "C:\ProgramData\CandidateFolder"
$file = Join-Path $folder "write-test-$PID.tmp"

try {
    New-Item -ItemType File -Path $file -ErrorAction Stop | Out-Null
    Write-Output "Write succeeded"
}
finally {
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}
```

This validates write access without introducing an executable payload.


---

# Application-Control Assessment

```text
Candidate Path
      |
      v
User Writable?
   /      \
 No        Yes
 |          |
Stop        v
        Policy Allows?
         /       \
       No         Yes
       |           |
      Stop         v
             Safe Execution
               Validation
                   |
                   v
              Confirmed Gap?
```


---

# WDAC

Windows Defender Application Control is now generally described by Microsoft as App Control for Business.

It can control which:

```text
Executables

DLLs

Scripts

Installers

Applications
```

are trusted to execute.


---

# Code Integrity Logs

Important logs include:

```text
Microsoft-Windows-CodeIntegrity/Operational
```

Query:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 50
```


---

# Application Control Interpretation

Distinguish:

```text
No policy exists

Policy exists in audit mode

Policy exists and allowed the file

Policy exists and blocked the file

Different rule collection applies

File was outside policy scope
```


---

# LOLBins

Living-off-the-land binaries are legitimate system utilities that can sometimes perform functionality useful during an attack.

Common Windows examples include:

```text
PowerShell

cmd

rundll32

regsvr32

mshta

wscript

cscript

certutil

bitsadmin

msbuild

InstallUtil

schtasks

sc
```

Their presence alone is not a vulnerability.


---

# LOLBin Assessment Model

```text
Binary Present
      |
      v
Allowed to Launch?
      |
      v
Relevant Functionality Available?
      |
      v
Security Boundary Crossed?
      |
      v
Telemetry Generated?
      |
      v
Detection?
```


---

# rundll32

Locate:

```powershell
Get-Command rundll32.exe
```

A harmless functional validation:

```powershell
& "$env:WINDIR\System32\rundll32.exe" "shell32.dll,Control_RunDLL" "main.cpl"
```

This demonstrates that `rundll32.exe` can invoke an expected Windows Control Panel function.

It does not prove arbitrary DLL execution or application-control bypass.


---

# Windows Script Host

Check:

```powershell
Get-Command wscript.exe
Get-Command cscript.exe
```

Create a harmless test script:

```powershell
'WScript.Echo "Execution test"' | Set-Content "$env:TEMP\wscript-test.vbs"
```

Evaluate policy:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:TEMP\wscript-test.vbs" -User "$env:USERDOMAIN\$env:USERNAME"
```

Cleanup:

```powershell
Remove-Item "$env:TEMP\wscript-test.vbs" -Force -ErrorAction SilentlyContinue
```


---

# mshta

Check availability:

```powershell
Get-Command mshta.exe -ErrorAction SilentlyContinue
```

Evaluate whether application-control policy restricts it.

Do not equate:

```text
Binary exists
```

with:

```text
HTA execution is unrestricted.
```


---

# MSBuild

Check common framework locations:

```powershell
Get-ChildItem "$env:WINDIR\Microsoft.NET\Framework*\*\MSBuild.exe" -ErrorAction SilentlyContinue
```

Modern installations may also provide MSBuild through Visual Studio or the .NET toolchain.

Assess:

```text
Presence

Policy

User context

Logging

Endpoint visibility
```


---

# InstallUtil

Search:

```powershell
Get-ChildItem "$env:WINDIR\Microsoft.NET\Framework*\*\InstallUtil.exe" -ErrorAction SilentlyContinue
```

Again:

```text
Present != unrestricted execution
```


---

# certutil

Check:

```powershell
Get-Command certutil.exe -ErrorAction SilentlyContinue
```

Legitimate certificate functionality makes `certutil.exe` a common administrative utility.

Defenders should focus on unusual behaviour and context rather than the filename alone.


---

# BITS

Check:

```powershell
Get-Command bitsadmin.exe -ErrorAction SilentlyContinue
```

PowerShell BITS functionality may also exist:

```powershell
Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue
```


---

# curl

Modern Windows installations may include:

```powershell
Get-Command curl.exe -ErrorAction SilentlyContinue
```

Its availability means HTTP transfer functionality exists, not that a vulnerability exists.


---

# Script Execution

Script execution commonly involves:

```text
PowerShell

Batch

VBScript

JavaScript

Python

Shell scripts
```

Evaluate each relevant interpreter separately.


---

# PowerShell Script Logging

Important PowerShell telemetry includes:

```text
Script Block Logging

Module Logging

Transcription

Process Creation

AMSI

EDR telemetry
```


---

# Script Block Logging

Relevant policy location:

```text
HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -ErrorAction SilentlyContinue
```


---

# Module Logging

```powershell
Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -ErrorAction SilentlyContinue
```


---

# Transcription

```powershell
Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue
```


---

# PowerShell Operational Log

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 50
```

Important events can include script execution and engine activity depending on configuration.


---

# ASR Rules

Microsoft Defender Attack Surface Reduction rules can restrict behaviours frequently associated with attacks.

Review:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```

Interpret the configured rule IDs using Microsoft's current ASR documentation.


---

# ASR States

Rules may operate in modes such as:

```text
Disabled

Block

Audit

Warn
```

The exact numeric configuration should be interpreted using current Microsoft documentation.


---

# Execution Validation Matrix

Maintain a matrix:

| Mechanism | Present | Policy | Executes | Telemetry | Alert |
|---|---:|---:|---:|---:|---:|
| PowerShell | Yes | Allowed | Yes | Yes | Yes |
| cmd | Yes | Allowed | Yes | Yes | No |
| wscript | Yes | Restricted | No | Yes | No |
| mshta | Yes | Blocked | No | Yes | Yes |
| rundll32 | Yes | Allowed | Yes | Yes | No |


---

# Remote Execution

Execution may also occur remotely through authorised administration protocols.

Common Windows mechanisms include:

```text
WinRM

SMB services

WMI

DCOM

RDP

Scheduled tasks

Remote service management
```

See:

[Lateral Movement](lateral-movement.md)


---

# Remote Execution Model

```text
Source Host
     |
     v
Authentication
     |
     v
Remote Protocol
     |
     v
Target Host
     |
     v
Process Execution
```


---

# Remote Execution Preconditions

Validate:

```text
Network reachability

Authentication

Authorisation

Administrative rights

Firewall policy

Service availability

Application control
```


---

# WinRM

Check reachability from Windows:

```powershell
Test-NetConnection TARGET -Port 5985
```

HTTPS WinRM:

```powershell
Test-NetConnection TARGET -Port 5986
```

Reachability alone does not prove authentication or execution rights.


---

# SMB

```powershell
Test-NetConnection TARGET -Port 445
```

Again:

```text
TCP reachable != remote execution possible
```


---

# RDP

```powershell
Test-NetConnection TARGET -Port 3389
```


---

# WMI

Local WMI functionality:

```powershell
Get-CimInstance Win32_OperatingSystem
```

Remote WMI execution requires additional authentication, authorisation, and network conditions.


---

# Scheduled Tasks

Enumerate:

```powershell
Get-ScheduledTask
```

Detailed task information:

```powershell
Get-ScheduledTask |
    Select-Object TaskName,TaskPath,State
```

Scheduled tasks can represent:

```text
Legitimate automation

Execution mechanism

Persistence mechanism
```

Context determines the security significance.


---

# Services

Enumerate:

```powershell
Get-Service
```

Service configuration:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```

Services may be relevant to:

```text
Execution

Privilege escalation

Persistence

Lateral movement
```


---

# Linux Execution

On Linux, begin with execution context.

```bash
id
```

```bash
whoami
```

```bash
hostname
```

```bash
uname -a
```


---

# Current Shell

```bash
echo "$SHELL"
```

Current process:

```bash
ps -p $$ -o pid,ppid,user,comm,args
```


---

# Available Shells

```bash
cat /etc/shells
```

Possible shells include:

```text
/bin/sh

/bin/bash

/bin/zsh

/usr/bin/fish
```


---

# Command Availability

Use:

```bash
command -v bash
command -v sh
command -v python3
command -v perl
command -v ruby
command -v php
command -v gcc
```

Presence should be recorded separately from privilege and security impact.


---

# Simple Linux Execution

```bash
printf '%s\n' 'Execution test'
```

Create a harmless shell script:

```bash
cat > /tmp/execution-test.sh <<'EOF'
#!/bin/sh
printf '%s\n' 'Execution test'
EOF
```

Make executable:

```bash
chmod +x /tmp/execution-test.sh
```

Execute:

```bash
/tmp/execution-test.sh
```

Cleanup:

```bash
rm -f /tmp/execution-test.sh
```


---

# Linux Mount Options

Execution may be restricted by filesystem mount options.

Review:

```bash
findmnt
```

Look for:

```text
noexec

nosuid

nodev
```


---

# noexec

A filesystem mounted with:

```text
noexec
```

restricts direct execution of binaries from that filesystem.

Do not interpret `noexec` as a universal code-execution prevention mechanism.

It is one layer of filesystem policy.


---

# Linux Permissions

Review file permissions:

```bash
ls -la /path/to/file
```

Directory permissions:

```bash
namei -l /path/to/file
```

The ability to write a file and the ability to execute it are separate conditions.


---

# Linux Sudo

Review authorised sudo permissions:

```bash
sudo -l
```

This is important because execution through privileged commands may cross a privilege boundary.

See:

[Linux Privilege Escalation](../linux/privilege-escalation.md)


---

# Linux Capabilities

Review file capabilities:

```bash
getcap -r / 2>/dev/null
```

Capabilities may permit specific privileged operations without full root access.


---

# Linux SUID and SGID

Find SUID files:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Find SGID files:

```bash
find / -perm -2000 -type f 2>/dev/null
```

The presence of SUID/SGID files is normal.

The question is whether a specific configuration creates an unintended privilege path.


---

# Linux Services

List running services:

```bash
systemctl --type=service --state=running
```

Inspect a service:

```bash
systemctl status SERVICE
```

Service execution context may matter for:

```text
Privilege

Persistence

Writable configuration

Environment variables

Executable paths
```


---

# Linux Cron

Review:

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d/
```

User cron:

```bash
crontab -l
```

Scheduled execution should be analysed together with file ownership and permissions.


---

# Linux Audit Telemetry

Linux execution visibility may come from:

```text
auditd

systemd journal

EDR

Shell logging

Process accounting

Container telemetry

SIEM agents
```


---

# systemd Journal

Example:

```bash
journalctl --since "10 minutes ago"
```

Service-specific:

```bash
journalctl -u SERVICE
```


---

# auditd

Check status where available:

```bash
systemctl status auditd
```

Rules:

```bash
auditctl -l
```

Read-only inspection is preferred during initial validation.


---

# Containers

Execution may occur inside:

```text
Docker

Podman

Kubernetes containers
```

Always determine whether the shell is:

```text
Host

Container

Virtual machine
```


---

# Container Identification

Useful indicators:

```bash
cat /proc/1/cgroup
```

```bash
test -f /.dockerenv && echo "Docker indicator present"
```

Container execution does not automatically imply host execution.


---

# Docker

Check:

```bash
docker version
```

Current containers:

```bash
docker ps
```

Only where the current user is authorised to access the Docker daemon.


---

# Execution Boundaries

Track boundaries explicitly.

Examples:

```text
Browser -> Shell

User -> Interpreter

Interpreter -> Child Process

User-Writable Path -> Executable

Standard User -> Administrative Process

Workstation -> Remote Server

Container -> Host
```


---

# Execution and Privilege Escalation

Execution becomes privilege escalation when:

```text
Current Context
      |
      v
Execution Mechanism
      |
      v
Higher Privilege Context
```

See:

[Windows Privilege Escalation](../windows/privilege-escalation.md)

[Linux Privilege Escalation](../linux/privilege-escalation.md)

[PrivEsc Explorer](../privesc/)


---

# Execution and Credential Access

Successful execution may provide access to:

```text
Configuration files

Environment variables

Credential stores

Application secrets

Authentication material
```

See:

[Credential Access](credential-access.md)


---

# Execution and Persistence

Execution mechanisms such as:

```text
Scheduled tasks

Services

Startup items

Cron

systemd
```

may also become persistence mechanisms.

See:

[Persistence](persistence.md)


---

# Execution and Defence Evasion

Application control, AMSI, ASR, endpoint prevention, and interpreter restrictions overlap strongly with defence-evasion testing.

See:

[Defence Evasion](defence-evasion.md)


---

# Execution and C2

A foothold may eventually establish authorised command-and-control communication.

Execution should be evaluated independently from C2.

```text
Execution Works
      |
      v
Network Communication?
      |
      v
C2 Established?
```

See:

[Command and Control](command-and-control.md)


---

# Payload Management

Every assessment artifact should be controlled.

Record:

```text
Payload ID

Filename

Hash

Purpose

Target

Operator

Creation time

Deployment time

Cleanup status
```


---

# Hashing an Artifact

Windows:

```powershell
Get-FileHash .\test-file.bin -Algorithm SHA256
```

Linux:

```bash
sha256sum test-file.bin
```


---

# Payload Inventory Example

| ID | Artifact | Host | Purpose | SHA-256 | Cleanup |
|---|---|---|---|---|---|
| EX-001 | `execution-test.ps1` | WS01 | Script validation | `...` | Removed |
| EX-002 | `execution-test.sh` | LNX01 | Shell validation | `...` | Removed |


---

# Prefer Harmless Validation

When the question is:

```text
Can this location execute a file?
```

you usually do not need:

```text
Reverse shell

Credential dumper

Persistence payload

Exploit
```

A marker program or harmless command can establish the boundary with significantly less risk.


---

# Validation Ladder

Use the least intrusive test that answers the question.

```text
1. Configuration Review

2. Policy Query

3. File Presence

4. Write Test

5. Harmless Script

6. Harmless Binary

7. Controlled Security Test

8. More Intrusive Technique Only If Required
```


---

# Detection Validation

Execution testing should consider both prevention and detection.

```text
Execution Attempt
      |
      +--------------------+
      |                    |
      v                    v
   Prevented             Allowed
      |                    |
      v                    v
 Telemetry?             Telemetry?
      |                    |
      v                    v
   Alert?                Alert?
      |                    |
      v                    v
 Response?              Response?
```


---

# Detection Outcomes

Useful classifications:

```text
Prevented and Alerted

Prevented but Not Alerted

Allowed and Detected

Allowed and Logged

Allowed with No Useful Visibility
```


---

# Prevention vs Detection

Do not confuse:

```text
Process executed
```

with:

```text
Security control failed.
```

A detection-focused control may intentionally allow the action while generating telemetry and an alert.


---

# Detection Evidence

Capture:

```text
Test timestamp

Hostname

Username

Process

Parent process

Command line

EDR event

SIEM event

Alert

SOC action
```


---

# Example Detection Record

```text
Test ID:
EXEC-007

Host:
WS01

User:
CORP\test-user

Action:
Harmless PowerShell child-process execution

Expected:
Process creation and PowerShell telemetry

Observed:
Process telemetry received

Alert:
Yes

SOC Response:
Analyst investigation initiated

Result:
Detected
```


---

# Process Telemetry

Useful fields:

```text
Image

Command line

Parent image

Parent command line

User

Integrity level

Hash

Signer

Timestamp

Network activity
```


---

# Behaviour Matters More Than Filename

A legitimate executable may participate in suspicious activity.

Likewise, a custom executable is not automatically malicious.

Detection should consider:

```text
Parent

Child

Command line

User

Location

Network

Frequency

Sequence

Target
```


---

# Execution Sequence

Example:

```text
Office Application
      |
      v
Script Interpreter
      |
      v
Command Shell
      |
      v
Network Utility
```

The sequence may be more meaningful than any single process.


---

# Evidence

For each important execution test, record:

```text
Execution mechanism

Source

Target

User

Privilege

Timestamp

Command

Result

Security control

Telemetry

Alert

Cleanup
```


---

# Evidence Example

```text
Evidence ID:
EXEC-014

Host:
WS01

User:
CORP\test-user

Mechanism:
Windows Script Host

Policy:
AppLocker Script collection enforced

Test:
Harmless VBS file in user temporary directory

Result:
Denied by policy

Impact:
Script execution from the tested location was prevented.

Detection:
Policy event generated.
```


---

# Candidate vs Confirmed

Use:

```text
Candidate

Likely

Confirmed
```

Example:

```text
Writable Allowed Path
      |
      v
Candidate
      |
      v
Policy Review
      |
      v
Likely
      |
      v
Harmless Validation
      |
      v
Confirmed
```


---

# Reporting Execution Findings

Good finding titles:

```text
Application Control Permits Execution from User-Writable Directory

PowerShell Language Restrictions Are Not Enforced for Standard Users

Script Execution Is Allowed Without Central Security Telemetry

Remote Administrative Execution Is Insufficiently Restricted
```

Avoid:

```text
PowerShell Bypass

rundll32 Vulnerability

MSBuild Exploit
```

unless those phrases precisely describe the validated condition.


---

# Example Finding

```text
Title:
Application Control Permits Execution from User-Writable Directory

Severity:
High

Observation:
A standard user was able to create an executable artifact in a
directory writable by non-administrative users.

The effective application-control policy allowed execution from
the same location.

A harmless validation executable was successfully launched under
the standard-user context.

Impact:
An attacker who obtains code execution as a standard user may be
able to execute arbitrary tooling from a location trusted by the
application-control policy, reducing the effectiveness of the
execution-control boundary.

Recommendation:
Remove write access for standard users from trusted application
paths or replace broad path-based allow rules with appropriately
scoped publisher, signer, or managed application-control rules.
```


---

# Example CLM Observation

```text
Title:
PowerShell Full Language Mode Available to Standard Users

Observation:
The assessment account operated in PowerShell FullLanguage mode.

Impact:
FullLanguage provides access to PowerShell capabilities that may
increase the functionality available to an attacker following
initial code execution.

The observation should be evaluated together with application
control, AMSI, endpoint protection, PowerShell logging, and user
privilege.

Recommendation:
Where appropriate for the environment, consider enforcing
PowerShell Constrained Language Mode through a supported
application-control architecture for non-administrative users,
while ensuring administrative workflows remain functional.
```


---

# Example Detection Finding

```text
Title:
PowerShell Execution Generates Telemetry but No Actionable Alert

Observation:
The controlled execution test generated PowerShell and endpoint
process telemetry.

The telemetry was successfully forwarded to the central security
platform.

No detection rule generated an alert during the assessment
window.

Classification:
Detection logic gap.

Recommendation:
Develop and tune detection logic around suspicious PowerShell
execution patterns while maintaining sufficient context to avoid
alerting on normal administrative use.
```


---

# Remediation

Execution-control improvements may include:

```text
Application control

Least privilege

Removal of unnecessary interpreters

Restricting writable trusted paths

PowerShell language restrictions

Script signing

ASR rules

AMSI integration

Endpoint protection

Process telemetry

Central logging

Detection engineering

Administrative tiering
```


---

# Layered Execution Security

```text
                  EXECUTION ATTEMPT
                         |
                         v
                   Least Privilege
                         |
                         v
                Application Control
                         |
                         v
                   Script Control
                         |
                         v
                       AMSI
                         |
                         v
                Endpoint Prevention
                         |
                         v
                 Process Telemetry
                         |
                         v
                    Detection
                         |
                         v
                     Response
```


---

# Execution Testing Checklist

## Context

- [ ] Hostname recorded
- [ ] User recorded
- [ ] Groups recorded
- [ ] Privileges recorded
- [ ] Operating system recorded
- [ ] Architecture recorded
- [ ] Shell recorded
- [ ] Current working directory recorded

## Windows

- [ ] PowerShell version reviewed
- [ ] Language mode reviewed
- [ ] Execution policy reviewed
- [ ] Defender status reviewed
- [ ] Defender version reviewed
- [ ] AMSI considerations reviewed
- [ ] ASR configuration reviewed
- [ ] AppLocker reviewed
- [ ] WDAC/App Control reviewed where applicable
- [ ] Code Integrity logs reviewed
- [ ] PowerShell logging reviewed
- [ ] Process creation auditing reviewed

## Interpreters

- [ ] PowerShell reviewed
- [ ] cmd reviewed
- [ ] Windows Script Host reviewed
- [ ] mshta reviewed where relevant
- [ ] .NET tooling reviewed where relevant
- [ ] Python reviewed where relevant
- [ ] Other installed interpreters reviewed

## LOLBins

- [ ] Presence distinguished from execution
- [ ] Policy decision validated
- [ ] Harmless functional tests used where appropriate
- [ ] Telemetry reviewed
- [ ] Findings based on security boundaries rather than tool names

## Linux

- [ ] User context reviewed
- [ ] Shell identified
- [ ] Available interpreters reviewed
- [ ] Mount options reviewed
- [ ] File permissions reviewed
- [ ] sudo permissions reviewed
- [ ] Capabilities reviewed
- [ ] SUID/SGID reviewed
- [ ] Services reviewed
- [ ] Cron reviewed
- [ ] Logging reviewed

## Remote Execution

- [ ] Network reachability validated
- [ ] Authentication requirements understood
- [ ] Authorisation requirements understood
- [ ] Remote service identified
- [ ] Execution context recorded
- [ ] Telemetry reviewed

## Detection

- [ ] Test timestamp recorded
- [ ] Process telemetry reviewed
- [ ] Parent-child relationship reviewed
- [ ] EDR telemetry reviewed
- [ ] SIEM telemetry reviewed
- [ ] Alert status recorded
- [ ] SOC response recorded
- [ ] Prevention distinguished from detection

## Evidence

- [ ] Test ID assigned
- [ ] Host recorded
- [ ] User recorded
- [ ] Command recorded
- [ ] Result recorded
- [ ] Policy recorded
- [ ] Security telemetry recorded
- [ ] Cleanup recorded


---

# Quick Reference - Windows

## Context

```powershell
whoami /all
```

```powershell
hostname
```

```powershell
$PSVersionTable
```

```powershell
$ExecutionContext.SessionState.LanguageMode
```


## Execution Policy

```powershell
Get-ExecutionPolicy -List
```


## Defender

```powershell
Get-MpComputerStatus
```


## Defender Version

```powershell
Get-MpComputerStatus |
    Select-Object AMEngineVersion,
                  AMProductVersion,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```


## ASR

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```


## AppLocker

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```


## Code Integrity

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 50
```


## PowerShell Logging

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 50
```


## Defender Logging

```powershell
Get-WinEvent -LogName "Microsoft-Windows-Windows Defender/Operational" -MaxEvents 30
```


## Processes

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
```


## Services

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```


## Scheduled Tasks

```powershell
Get-ScheduledTask |
    Select-Object TaskName,TaskPath,State
```


---

# Quick Reference - Linux

## Identity

```bash
id
```


## System

```bash
uname -a
```


## Shell

```bash
echo "$SHELL"
```


## Current Process

```bash
ps -p $$ -o pid,ppid,user,comm,args
```


## Mounts

```bash
findmnt
```


## Sudo

```bash
sudo -l
```


## Capabilities

```bash
getcap -r / 2>/dev/null
```


## SUID

```bash
find / -perm -4000 -type f 2>/dev/null
```


## Running Services

```bash
systemctl --type=service --state=running
```


## Cron

```bash
cat /etc/crontab
```


## Journal

```bash
journalctl --since "10 minutes ago"
```


---

# Execution Decision Model

```text
                    Execution Candidate
                            |
                            v
                       In Scope?
                       /      \
                     No        Yes
                     |          |
                    STOP        v
                         Current Context
                              |
                              v
                       Mechanism Present?
                         /          \
                       No            Yes
                       |              |
                    Record            v
                              Policy Allows?
                               /       \
                             No         Yes
                             |           |
                             v           v
                          Record    Safe Validation
                                         |
                                         v
                                   Executes?
                                    /     \
                                  No       Yes
                                  |         |
                                  v         v
                               Record    Telemetry?
                                         /      \
                                       No        Yes
                                       |          |
                                       v          v
                                  Visibility     Alert?
                                     Gap        /    \
                                              No      Yes
                                              |        |
                                              v        v
                                          Detection  Response
                                             Gap
```


---

# Execution Control Model

```text
                     USER CONTEXT
                          |
                          v
                     FILE / SCRIPT
                          |
                          v
                   EXECUTION ENGINE
                          |
           +--------------+--------------+
           |              |              |
           v              v              v
       AppLocker         WDAC           ASR
           |              |              |
           +--------------+--------------+
                          |
                          v
                         AMSI
                          |
                          v
                Endpoint Protection
                          |
                          v
                      PROCESS
                          |
                          v
                     TELEMETRY
                          |
                          v
                      DETECTION
                          |
                          v
                       RESPONSE
```


---

# Final Execution Model

```text
                     AUTHORISED TEST
                           |
                           v
                     USER CONTEXT
                           |
                           v
                 EXECUTION HYPOTHESIS
                           |
                           v
                    POLICY REVIEW
                           |
                           v
                  HARMLESS VALIDATION
                           |
                           v
                      EXECUTION
                           |
              +------------+------------+
              |                         |
              v                         v
           BLOCKED                    ALLOWED
              |                         |
              v                         v
          TELEMETRY                 TELEMETRY
              |                         |
              +------------+------------+
                           |
                           v
                       DETECTION
                           |
                           v
                        RESPONSE
                           |
                           v
                        EVIDENCE
                           |
                           v
                       REPORTING
                           |
                           v
                        CLEANUP
```


---

# Core Principle

Execution testing can be reduced to:

```text
Determine the current identity.

Determine the current privilege.

Identify available execution mechanisms.

Understand application-control policy.

Check script restrictions.

Check endpoint security.

Use the least intrusive validation.

Separate presence from permission.

Separate execution from privilege escalation.

Separate execution from control bypass.

Determine what telemetry was generated.

Determine whether an alert was generated.

Determine whether defenders responded.

Preserve evidence.

Cleanup test artifacts.

Report the actual security boundary that was validated.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Reconnaissance](reconnaissance.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)
- [Windows](../windows/)
- [Windows PowerShell](../windows/powershell.md)
- [Windows Privilege Escalation](../windows/privilege-escalation.md)
- [Linux](../linux/)
- [Linux Privilege Escalation](../linux/privilege-escalation.md)
- [PrivEsc Explorer](../privesc/)


---

# References

- [MITRE ATT&CK - Execution](https://attack.mitre.org/tactics/TA0002/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Command and Scripting Interpreter](https://attack.mitre.org/techniques/T1059/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - PowerShell](https://attack.mitre.org/techniques/T1059/001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Windows Command Shell](https://attack.mitre.org/techniques/T1059/003/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Unix Shell](https://attack.mitre.org/techniques/T1059/004/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Windows Management Instrumentation](https://attack.mitre.org/techniques/T1047/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Services](https://attack.mitre.org/techniques/T1569/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Constrained Language Mode](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - App Control for Business](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Antimalware Scan Interface](https://learn.microsoft.com/windows/win32/amsi/antimalware-scan-interface-portal){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Attack Surface Reduction Rules](https://learn.microsoft.com/defender-endpoint/attack-surface-reduction-rules-reference){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Logging](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_logging_windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysmon](https://learn.microsoft.com/sysinternals/downloads/sysmon){ target="_blank" rel="noopener noreferrer" }
- [EICAR Anti-Malware Test File](https://www.eicar.org/download-anti-malware-testfile/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Validate the boundary, not the payload"
    If a harmless executable, script, or built-in command can demonstrate that an execution boundary is missing, there is usually no need to introduce a more intrusive payload. The security finding is the failed control boundary, not the sophistication of the code used to demonstrate it.


!!! warning "Execution does not automatically mean bypass"
    A command or process successfully executing does not prove that Defender, AMSI, AppLocker, WDAC, ASR, or an EDR product was bypassed. Determine which control was expected to prevent the action, whether that control was actually configured and applicable, what telemetry was produced, and whether detection or response occurred before describing the result as a security-control failure.
