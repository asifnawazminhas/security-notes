---
title: PrivescCheck
description: Practical PrivescCheck reference for authorised Windows privilege escalation enumeration, interpretation, native validation, evidence collection, false-positive analysis, and integration with manual Windows security review.
---

# PrivescCheck

PrivescCheck is a PowerShell-based Windows privilege escalation enumeration tool designed to identify local security conditions that may allow a lower-privileged user to influence privileged execution or access sensitive local resources.

It can help review areas such as:

- users and groups;
- token privileges;
- Windows services;
- scheduled tasks;
- filesystem permissions;
- registry permissions;
- installed applications;
- credentials;
- environment configuration;
- startup locations;
- security controls;
- potentially sensitive files.

PrivescCheck should be treated as an **enumeration and triage tool**.

Its output identifies conditions that deserve investigation.

It does not automatically prove that a privilege escalation path exists.

```text
Windows Host
    |
    v
PrivescCheck
    |
    +-- Identity
    +-- Privileges
    +-- Services
    +-- Tasks
    +-- Files
    +-- Registry
    +-- Credentials
    +-- Applications
    +-- Security Controls
    |
    v
Candidate Conditions
    |
    v
Native Validation
    |
    v
Privilege Escalation Conclusion
```

!!! warning "Authorised testing only"
    Run PrivescCheck only on Windows systems where local security assessment is explicitly authorised. PowerShell-based enumeration can generate endpoint-security telemetry and may inspect sensitive local configuration. Review the rules of engagement before execution.

---

# Where PrivescCheck Fits

PrivescCheck normally follows initial local access and a basic understanding of the current security context.

```text
Initial Access
      |
      v
Current User
      |
      v
Manual Baseline
      |
      v
PrivescCheck
      |
      v
Candidate Conditions
      |
      v
Native Validation
      |
      v
Confirm or Reject
```

Related notes:

[Privilege Escalation Tools](index.md)

[Windows Privilege Escalation](../../windows/privilege-escalation.md)

[Windows Enumeration](../../windows/enumeration.md)

[Windows Privilege Escalation Explorer](../../privesc/windows.md)

---

# Official Project

PrivescCheck is maintained by itm4n.

Official project:

[PrivescCheck - GitHub](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

Use the official repository or a trusted internal mirror.

Avoid modified copies from unknown sources.

---

# What PrivescCheck Does

PrivescCheck automates local Windows checks that would otherwise require many individual commands.

Conceptually:

```text
Windows Configuration
       |
       +-- Services
       +-- Scheduled Tasks
       +-- Registry
       +-- Filesystem
       +-- Credentials
       +-- Users
       +-- Privileges
       +-- Applications
       |
       v
PrivescCheck
       |
       v
Potential Security Conditions
```

The purpose is to answer:

> Which areas should I investigate further?

not:

> Which findings are definitely exploitable?

---

# Before Running PrivescCheck

Start by recording the current security context.

```powershell
whoami
```

```powershell
whoami /groups
```

```powershell
whoami /priv
```

Also consider:

```powershell
whoami /all
```

This helps answer:

```text
Who am I?

Which groups apply?

Which token privileges exist?

Am I already an administrator?

Which security identifiers influence ACL evaluation?
```

---

# Record Host Context

Useful commands include:

```powershell
hostname
```

```powershell
systeminfo
```

and, where available:

```powershell
Get-ComputerInfo
```

This establishes:

- hostname;
- Windows version;
- architecture;
- domain context;
- patch context.

---

# PowerShell Environment

Check the PowerShell version:

```powershell
$PSVersionTable
```

Check the current language mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

This matters because PowerShell restrictions can affect tool execution.

---

# Execution Policy

Review:

```powershell
Get-ExecutionPolicy -List
```

Execution policy can affect script loading but should not be confused with a strong security boundary.

Do not change enterprise policy merely to run the tool unless that change is specifically authorised.

---

# Application Control

PrivescCheck may be affected by:

- AppLocker;
- Windows Defender Application Control;
- Constrained Language Mode;
- Microsoft Defender;
- EDR controls.

Related notes:

[Windows Application Control](../../windows/application-control.md)

[Microsoft Defender](../../windows/defender.md)

If the script cannot execute, the underlying checks can still be performed manually.

---

# Obtaining PrivescCheck

Prefer the official repository.

Useful information to retain includes:

```text
Tool:
PrivescCheck

Source:
Official GitHub repository

Revision:
Recorded where useful

Hash:
Recorded where required
```

This improves reproducibility.

---

# Basic Execution

The exact invocation should always be confirmed against the version being used.

A typical workflow is:

```powershell
. .\PrivescCheck.ps1
```

Then invoke the main PrivescCheck function exposed by that version.

Before running:

```powershell
Get-Content .\PrivescCheck.ps1 -Head 40
```

and inspect the documentation in the repository.

Do not assume all historical versions expose identical function names or parameters.

---

# Inspect Available Functions

After loading the script, inspect functions related to the tool.

For example:

```powershell
Get-Command | Where-Object Name -like '*Privesc*'
```

or use:

```powershell
Get-Help
```

for the main function exposed by the installed version.

The exact script remains the best reference for exact syntax.

---

# Save Output

For longer assessments, save results.

A common PowerShell pattern is:

```powershell
<PrivescCheckCommand> | Tee-Object -FilePath .\privesccheck-output.txt
```

Replace:

```text
<PrivescCheckCommand>
```

with the main command from the version being used.

The output may contain sensitive information.

Protect it accordingly.

---

# Output Can Be Sensitive

PrivescCheck may surface:

- usernames;
- service accounts;
- filesystem paths;
- weak permissions;
- credentials;
- registry values;
- potentially sensitive configuration.

Do not:

- commit raw output to Git;
- paste full output into public tickets;
- upload it to third-party services;
- attach unnecessary sensitive data to reports.

Extract only relevant evidence.

---

# Result Interpretation

A useful model is:

```text
PrivescCheck Result
        |
        v
Candidate
        |
        v
Native Validation
        |
        v
Execution Context
        |
        v
Reachability
        |
        v
Impact
```

The tool result alone is not enough.

---

# Services

Windows services are one of the most important local privilege escalation areas.

PrivescCheck may identify conditions involving:

- weak service permissions;
- weak executable permissions;
- weak directory permissions;
- unquoted service paths;
- privileged service identities.

Related note:

[Windows Services](../../windows/services.md)

---

# Service Configuration

Validate a service with:

```powershell
sc.exe qc ExampleService
```

Review:

```text
BINARY_PATH_NAME
SERVICE_START_NAME
START_TYPE
```

You can also use:

```powershell
Get-CimInstance Win32_Service | Where-Object Name -eq 'ExampleService'
```

This confirms the actual service configuration.

---

# Service Identity

Common service identities include:

```text
LocalSystem
LocalService
NetworkService
Domain service account
Custom local account
```

A service running as LocalSystem generally represents a highly privileged execution context.

The service identity is critical to impact assessment.

---

# Service Executable Permissions

If PrivescCheck identifies a potentially writable service binary, validate:

```powershell
icacls "C:\Program Files\Example\Service.exe"
```

Review:

```text
Current user
Current groups
Explicit ACEs
Inherited ACEs
Allow permissions
Deny permissions
```

The security question is:

> Can the current user actually modify or replace this executable?

---

# Service Directory Permissions

The executable may be protected while the parent directory is writable.

Check:

```powershell
icacls "C:\Program Files\Example"
```

This may reveal rights allowing:

- file creation;
- deletion;
- replacement;
- rename operations.

Parent directory permissions can matter as much as the file ACL.

---

# Weak Service Object Permissions

Filesystem ACLs and service-object ACLs are different.

A user may have no write access to the binary but still have permission to modify the service itself.

Possible security-relevant controls include the ability to change:

- service binary path;
- startup configuration;
- service identity.

The underlying weakness in that case is the service object security descriptor.

---

# Restartability

A service-related condition may require execution to be triggered.

Questions include:

```text
Can the current user stop the service?

Can the current user start it?

Does it restart automatically?

Will it execute at reboot?

Does an administrator action trigger it?
```

Check state:

```powershell
sc.exe query ExampleService
```

Do not assume immediate exploitability without a reachable trigger.

---

# Unquoted Service Paths

PrivescCheck may identify unquoted service paths.

Example:

```text
C:\Program Files\Vendor Application\Service.exe
```

The presence of spaces alone is not sufficient.

Also determine:

```text
Is the path unquoted?

Which candidate path components are evaluated?

Can current user write to one?

Does the service run privileged?

Can the service be triggered?
```

An unquoted path with protected directories may not provide a practical escalation path.

---

# Scheduled Tasks

Scheduled tasks can execute in privileged contexts.

PrivescCheck may identify:

- task name;
- action;
- execution identity;
- potentially writable referenced files.

Related note:

[Windows Scheduled Tasks](../../windows/scheduled-tasks.md)

---

# Scheduled Task Enumeration

Use native tooling:

```powershell
schtasks.exe /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

For a specific task:

```powershell
Get-ScheduledTask -TaskName "ExampleTask"
```

Inspect actions:

```powershell
(Get-ScheduledTask -TaskName "ExampleTask").Actions
```

---

# Task Execution Identity

Determine whether the task runs as:

```text
SYSTEM
Administrator
Service account
Normal user
```

The privilege of the task determines the importance of writable resources it consumes.

---

# Task Actions

Suppose the task runs:

```text
C:\ProgramData\Scripts\backup.ps1
```

Validate:

```powershell
icacls "C:\ProgramData\Scripts\backup.ps1"
```

and:

```powershell
icacls "C:\ProgramData\Scripts"
```

The complete execution chain matters.

---

# Task Trigger

Determine whether the task runs:

```text
At startup
At logon
On schedule
On event
Manually
```

Document the actual trigger.

A condition that executes every few minutes is different from one requiring an administrator reboot.

---

# Filesystem Permissions

Filesystem permissions are one of the most important areas in local privilege escalation.

PrivescCheck may identify:

- writable files;
- writable directories;
- privileged executables;
- configuration files;
- scripts.

Related note:

[Windows Filesystem Permissions](../../windows/filesystem-permissions.md)

---

# Validate Files with icacls

Use:

```powershell
icacls "C:\Path\To\File"
```

For a directory:

```powershell
icacls "C:\Path\To\Directory"
```

Common permission abbreviations include:

```text
F  -> Full control
M  -> Modify
RX -> Read and execute
R  -> Read
W  -> Write
```

Always interpret permissions in combination with current group membership.

---

# Inheritance

Windows ACLs often contain inherited permissions.

A child object may inherit rights from a parent.

Therefore review:

```text
Explicit ACE
Inherited ACE
Parent ACL
```

Do not assume the permission originates directly on the file.

---

# Deny ACEs

Explicit deny entries can affect effective permission evaluation.

A simple match for:

```text
Users:(M)
```

is not always sufficient to determine effective access.

Review the complete ACL and security token.

---

# Ownership

Ownership may grant the ability to modify an object's security descriptor depending on the current security context.

Therefore:

```text
Owner
```

can be relevant even when direct write permission is absent.

Do not assume ownership automatically results in exploitability.

---

# Registry Permissions

The Windows registry can influence privileged execution.

PrivescCheck may identify writable registry locations associated with:

- services;
- applications;
- startup;
- policy;
- installer behaviour.

Related note:

[Windows Registry](../../windows/registry.md)

---

# Registry Query

Read configuration with:

```powershell
reg.exe query "HKLM\Software\Example"
```

The interesting condition is not simply that a key exists.

It is whether:

```text
Current user can modify it
        +
Privileged process trusts it
```

---

# Service Registry Keys

Windows services are represented in the registry under system service configuration.

However, do not infer service configuration permissions solely from registry visibility.

Use appropriate service and ACL inspection methods to determine effective rights.

---

# Installer Policy

PrivescCheck may inspect Windows Installer policy related to elevated installations.

If an elevated installer policy is identified, verify the complete configuration rather than relying on one registry value.

The underlying security issue is an unsafe installer policy allowing lower-privileged influence over elevated installation.

---

# Startup Locations

Windows startup mechanisms may include:

```text
Run keys
Startup folders
Services
Scheduled tasks
Application-specific autostart
```

The relevant questions are:

```text
What runs?

Who can modify it?

Who runs it?

When is it executed?
```

---

# PATH

PrivescCheck may identify writable PATH directories.

Inspect:

```powershell
$env:Path -split ';'
```

Then validate relevant paths:

```powershell
icacls "C:\Path"
```

A writable PATH directory is only relevant if a privileged process performs unqualified executable resolution through it.

---

# PATH Privilege Escalation Model

```text
Privileged Process
      |
      v
Calls Binary Without Full Path
      |
      v
Searches PATH
      |
      v
Writable Directory Appears First
      |
      v
User Can Influence Resolution
```

Every step must be demonstrated.

---

# DLL Search Conditions

PrivescCheck may identify conditions relevant to DLL loading.

A real DLL hijacking path requires understanding:

```text
Which process loads the DLL?

Which name is requested?

Which search order applies?

Which locations are writable?

What privilege runs the process?

Can the process be triggered?
```

A writable directory by itself is not enough.

---

# Installed Applications

PrivescCheck can identify software and configuration relevant to local privilege escalation.

Custom or third-party applications deserve particular attention because they may introduce:

- services;
- scheduled jobs;
- writable configuration;
- weak installation directories;
- insecure update mechanisms.

Do not report old-looking versions without validating patch status and actual applicability.

---

# Credentials

PrivescCheck may identify possible credential exposure.

Potential sources include:

- configuration files;
- unattended deployment files;
- registry values;
- scripts;
- application files;
- environment variables.

Related note:

[Windows Credentials](../../windows/credentials.md)

Treat any credential-like material as sensitive.

---

# Credential Validation

A candidate credential may be:

```text
Current
Expired
Unused
Placeholder
Example data
Encrypted
```

Do not automatically authenticate with it.

Determine whether validation is:

- necessary;
- within scope;
- low risk.

The exposure itself may already be the relevant finding.

---

# Autologon

Windows autologon configuration can expose sensitive credential-related information in some configurations.

If PrivescCheck highlights autologon data, verify what is actually present.

Do not assume a password exists simply because autologon-related keys are configured.

---

# Environment Variables

Environment variables may expose:

- secrets;
- application settings;
- PATH;
- internal locations.

Inspect:

```powershell
Get-ChildItem Env:
```

Security relevance depends on content and privilege context.

---

# Token Privileges

PrivescCheck may highlight token privileges.

Confirm manually:

```powershell
whoami /priv
```

Potentially interesting privileges must be interpreted according to:

- current state;
- process context;
- Windows protections;
- privilege preconditions.

The presence of a privilege is not the same as successful privilege escalation.

---

# User and Group Membership

PrivescCheck output should always be interpreted alongside:

```powershell
whoami /groups
```

Group membership may explain:

- filesystem access;
- registry access;
- service rights;
- local administrative rights.

Without group context, ACL findings can be misleading.

---

# UAC Context

If the current user belongs to the local Administrators group, User Account Control may affect the current token.

Check the broader context before describing the situation as ordinary privilege escalation.

Related note:

[Windows User Account Control](../../windows/uac.md)

UAC should not be confused with a normal privilege boundary between unrelated users.

---

# Security Controls

PrivescCheck output should be interpreted in the context of security controls such as:

- AppLocker;
- WDAC;
- Microsoft Defender;
- EDR;
- PowerShell controls.

A candidate may be technically present but practically constrained.

---

# AppLocker

A writable privileged resource may not allow arbitrary executable or script execution if AppLocker blocks the relevant file type or path.

This changes practical exploitability.

It does not necessarily correct the underlying permission issue.

Related note:

[Windows Application Control](../../windows/application-control.md)

---

# WDAC

WDAC can enforce stronger code-integrity restrictions.

The assessment should distinguish:

```text
Weak ACL
```

from:

```text
Ability to execute modified code under current policy
```

These are separate security questions.

---

# Constrained Language Mode

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

If the result is:

```text
ConstrainedLanguage
```

some PowerShell functionality may be unavailable.

A failed PrivescCheck execution does not mean the endpoint has no local privilege escalation weaknesses.

Use native tools where necessary.

---

# Microsoft Defender

PowerShell privilege escalation enumeration tools may be inspected or blocked by Defender or another endpoint product.

Do not disable security controls merely to make the tool run unless specifically authorised.

Related note:

[Microsoft Defender](../../windows/defender.md)

---

# Native Validation

PrivescCheck should lead to native validation.

Useful native tools include:

```text
whoami.exe
sc.exe
schtasks.exe
icacls.exe
reg.exe
net.exe
PowerShell cmdlets
```

The goal is to make each conclusion understandable without depending on PrivescCheck output alone.

---

# PrivescCheck vs WinPEAS

WinPEAS provides broad Windows enumeration.

PrivescCheck provides another structured Windows privilege escalation perspective.

```text
WinPEAS
   |
   +-- broad local enumeration

PrivescCheck
   |
   +-- structured PowerShell-based checks
```

A useful workflow is:

```text
WinPEAS
    |
    v
Candidate
    |
    v
PrivescCheck
    |
    v
Native Validation
```

Related note:

[WinPEAS](winpeas.md)

---

# PrivescCheck vs PowerUp

PowerUp and PrivescCheck overlap in several areas.

PowerUp is historically associated with PowerSploit.

PrivescCheck is a separate project with its own implementation and checks.

```text
PowerUp
    |
    +--> Candidate A

PrivescCheck
    |
    +--> Candidate A

Native Windows Tools
    |
    v
Confirm Actual Condition
```

Related note:

[PowerUp](powerup.md)

---

# Running Multiple Tools

Multiple tools can improve coverage.

However:

```text
Three tools report same service
```

does not mean:

```text
Three vulnerabilities
```

Consolidate duplicate results around the actual underlying weakness.

---

# Candidate Correlation

Example:

```text
WinPEAS:
Writable service candidate

PowerUp:
Service permission candidate

PrivescCheck:
Same service highlighted

icacls:
Modify confirmed

sc.exe:
Runs as LocalSystem
```

This provides strong evidence that the service deserves further investigation.

---

# Representative Service Scenario

Suppose PrivescCheck reports:

```text
Service:
ExampleService

Binary:
C:\ProgramData\Vendor\Service.exe

Potential issue:
Writable executable
```

Validate:

```powershell
sc.exe qc ExampleService
```

Then:

```powershell
icacls "C:\ProgramData\Vendor\Service.exe"
```

And:

```powershell
icacls "C:\ProgramData\Vendor"
```

Questions:

```text
Does current user have Modify or Write?

Which group grants access?

Does the service run as LocalSystem?

Can execution be triggered?

Does AppLocker or WDAC affect execution?
```

Only the complete chain determines risk.

---

# Representative Negative Service Scenario

PrivescCheck highlights:

```text
C:\Program Files\Example\Service.exe
```

Manual validation:

```powershell
icacls "C:\Program Files\Example\Service.exe"
```

shows only:

```text
SYSTEM
Administrators
TrustedInstaller
```

with modification rights.

Conclusion:

```text
The service executable was highlighted during automated enumeration,
but manual ACL validation did not show write or modify permissions for
the tested low-privileged user or its groups. The suspected privilege
escalation path was not confirmed.
```

---

# Representative Scheduled Task Scenario

PrivescCheck identifies:

```text
Task:
BackupTask

Runs as:
SYSTEM

Action:
C:\ProgramData\Backup\backup.ps1
```

Validate:

```powershell
schtasks.exe /query /tn "\BackupTask" /fo LIST /v
```

Then:

```powershell
icacls "C:\ProgramData\Backup\backup.ps1"
```

and:

```powershell
icacls "C:\ProgramData\Backup"
```

The key question is:

> Can the current user influence a resource executed by the SYSTEM task?

---

# Representative PATH Scenario

PrivescCheck identifies:

```text
C:\Tools
```

as writable and present in PATH.

Validate:

```powershell
icacls "C:\Tools"
```

Then investigate whether any privileged service or scheduled task invokes a command without a fully qualified path.

Without that privileged consumer:

```text
Writable PATH
```

may remain only a hardening observation.

---

# Representative Registry Scenario

PrivescCheck highlights a writable registry value.

Do not immediately call it privilege escalation.

Determine:

```text
Which process reads this value?

What privilege does that process run with?

Can the current user modify it?

Can the change affect execution?
```

The privileged consumer is essential.

---

# Representative Credential Scenario

PrivescCheck reports a potential password in a configuration file.

Validate:

```text
Is it plaintext?

Is the current user allowed to read the file?

Which account is referenced?

Does the credential provide more privilege?

Is testing the credential necessary?
```

Do not over-validate sensitive secrets.

---

# False Positives

PrivescCheck results can be misleading because of:

- inherited ACL interpretation;
- disabled services;
- inactive scheduled tasks;
- writable resources without privileged consumers;
- stale credentials;
- security-control restrictions;
- assumptions about execution triggers;
- generic weak-permission heuristics.

Manual validation is essential.

---

# False Negatives

PrivescCheck can miss real privilege escalation paths.

Possible reasons include:

- proprietary applications;
- non-standard directories;
- custom IPC;
- transient resources;
- newer Windows features;
- unusual service architectures;
- application-specific logic.

A clean result does not prove the host is free of local privilege escalation weaknesses.

---

# Tool Coverage Is Not Complete Coverage

A good assessment does not end with:

```text
PrivescCheck:
No findings
```

Continue with manual analysis of:

```text
Identity
Privileges
Services
Scheduled Tasks
Filesystem
Registry
Credentials
Applications
Security Controls
```

Automation improves coverage but cannot guarantee completeness.

---

# Review Output by Category

For large output, review systematically:

```text
1. Identity
2. Privileges
3. Services
4. Scheduled tasks
5. Filesystem permissions
6. Registry
7. Credentials
8. Applications
9. Security controls
10. Miscellaneous findings
```

This is more effective than looking only for highlighted strings.

---

# Search Saved Output

If output was saved:

```text
privesccheck-output.txt
```

search with:

```powershell
Select-String -Path .\privesccheck-output.txt -Pattern "service"
```

or:

```powershell
Select-String -Path .\privesccheck-output.txt -Pattern "writ"
```

or:

```powershell
Select-String -Path .\privesccheck-output.txt -Pattern "credential"
```

Preserve surrounding context.

---

# Candidate Evaluation Model

For each candidate, answer:

| Question | Answer |
|---|---|
| What did PrivescCheck identify? | |
| Can the current user influence it? | |
| Which ACL or permission proves this? | |
| Which privileged process consumes it? | |
| Which identity runs that process? | |
| Can it be triggered? | |
| Which security controls apply? | |
| What privilege would result? | |

This turns automated output into structured analysis.

---

# User Influence

The first major question is:

```text
Can the current user actually influence the resource?
```

This may mean:

- write;
- modify;
- delete;
- replace;
- reconfigure;
- control service object;
- change registry value.

A result without user influence is rarely a privilege escalation condition.

---

# Privileged Consumer

The second major question is:

```text
What privileged process trusts or executes the resource?
```

Examples include:

```text
LocalSystem service
SYSTEM scheduled task
Administrator-started application
Privileged installer
```

Without a privileged consumer, a writable resource may have little privilege escalation relevance.

---

# Reachable Trigger

The third question is:

```text
Can execution occur?
```

Possible triggers include:

- service restart;
- reboot;
- scheduled execution;
- logon;
- administrator action;
- application launch.

Document this clearly.

---

# Security Control Context

The fourth question is:

```text
Will another security control constrain the path?
```

Examples include:

- AppLocker;
- WDAC;
- Defender;
- EDR.

Do not ignore defence-in-depth controls when assessing practical exploitability.

---

# Evidence Model

Weak evidence:

```text
Screenshot of PrivescCheck output
```

Better:

```text
PrivescCheck candidate
      |
      v
Native configuration query
      |
      v
ACL evidence
      |
      v
Privileged identity
      |
      v
Trigger
      |
      v
Impact
```

The evidence should tell the story without requiring the reader to trust the tool.

---

# Evidence Collection

For a validated condition, retain:

```text
Current user:
Current groups:
PrivescCheck result:
Affected object:
Native configuration:
ACL:
Privileged consumer:
Execution identity:
Trigger:
Security controls:
Observed impact:
```

---

# Reporting

Avoid:

```text
PrivescCheck found privilege escalation.
```

Prefer:

```text
The tested standard user had Modify rights over a script executed by a
scheduled task running as SYSTEM. Native ACL and task configuration
checks confirmed that the low-privileged user could influence content
executed by a privileged process.
```

The finding is the weak privilege boundary, not the tool result.

---

# Reporting an Unconfirmed Candidate

Example:

```text
PrivescCheck identified a potentially writable service resource.
Manual validation showed that the tested user did not have effective
write or modify rights over the file or its parent directory. The
suspected privilege escalation path was therefore not confirmed.
```

This avoids false-positive reporting.

---

# Reporting Security Control Impact

Example:

```text
The tested user had write access to a file referenced by a privileged
service. However, application-control policy prevented execution of
unapproved code from the affected path during testing. The filesystem
permission remains weaker than necessary and should be corrected, while
the application-control policy currently provides an additional
defence-in-depth layer.
```

This describes both conditions accurately.

---

# Remediation Principles

The general remediation principle is:

> A low-privileged user should not be able to modify configuration or resources that determine how a higher-privileged process executes.

Typical remediation areas include:

- service permissions;
- service executable ACLs;
- scheduled-task resources;
- filesystem permissions;
- registry permissions;
- PATH;
- installer policy;
- credentials.

---

# Service Remediation

Typical measures include:

- remove unnecessary Modify/Write access;
- restrict service-object permissions;
- protect executable directories;
- use least-privileged service accounts;
- quote service executable paths where relevant.

---

# Scheduled Task Remediation

Typical measures include:

- protect task scripts and binaries;
- protect parent directories;
- restrict task modification;
- use least privilege;
- remove obsolete privileged tasks.

---

# Filesystem Remediation

Typical measures include:

- remove unnecessary writable ACLs;
- avoid broad permissions such as excessive `Users` or `Everyone` access;
- secure parent directories;
- use inheritance carefully.

---

# Registry Remediation

Typical measures include:

- restrict write access;
- protect privileged application configuration;
- remove insecure installer policies;
- review startup-related keys.

---

# Credential Remediation

Typical measures include:

- remove plaintext credentials;
- rotate exposed secrets;
- use secure credential storage;
- restrict file access;
- remove obsolete configuration.

---

# PATH Remediation

Typical measures include:

- remove writable directories from privileged PATH contexts;
- use explicit executable paths;
- correct directory ACLs.

---

# Retesting

Do not retest only by rerunning PrivescCheck.

For a file ACL fix:

```powershell
icacls "C:\Path\To\File"
```

For service configuration:

```powershell
sc.exe qc ExampleService
```

For a scheduled task:

```powershell
schtasks.exe /query /tn "\ExampleTask" /fo LIST /v
```

For registry configuration:

```powershell
reg.exe query "HKLM\Software\Example"
```

Then optionally rerun PrivescCheck as a secondary regression check.

---

# PrivescCheck in Purple Teaming

PrivescCheck can also be useful in purple-team exercises where the objective includes understanding defensive visibility.

```text
PrivescCheck
     |
     v
Local Enumeration
     |
     v
PowerShell / EDR Telemetry
     |
     v
Detection Review
```

Related notes:

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

The activity should be coordinated in advance.

---

# Detection Considerations

Potential telemetry may include:

- PowerShell script execution;
- service queries;
- registry access;
- filesystem enumeration;
- process creation.

Do not attempt to bypass defensive monitoring unless that activity is explicitly part of the approved test objective.

---

# Tool Transfer

Document transfer where appropriate:

```text
Tool:
PrivescCheck.ps1

Source:
Official repository

Destination:
Approved temporary assessment folder

Execution:
Authorised

Output:
Protected assessment evidence

Cleanup:
Completed after testing
```

---

# Cleanup

Where required, remove:

```text
PrivescCheck.ps1
privesccheck-output.txt
temporary assessment files
```

Do not remove legitimate event logs or security telemetry.

---

# Practical PrivescCheck Workflow

A strong workflow is:

```text
1. Confirm scope
      |
      v
2. Record current identity
      |
      v
3. Record groups and privileges
      |
      v
4. Record host context
      |
      v
5. Check PowerShell restrictions
      |
      v
6. Obtain trusted PrivescCheck copy
      |
      v
7. Review tool documentation
      |
      v
8. Run approved enumeration
      |
      v
9. Save output securely
      |
      v
10. Review by category
      |
      v
11. Prioritise privileged execution paths
      |
      v
12. Validate with native Windows tools
      |
      v
13. Confirm effective permissions
      |
      v
14. Identify privileged consumer
      |
      v
15. Confirm trigger
      |
      v
16. Consider application controls
      |
      v
17. Confirm or reject candidate
      |
      v
18. Capture evidence
      |
      v
19. Clean up assessment artefacts
```

---

# Quick Command Reference

## Current User

```powershell
whoami
```

## Full Security Context

```powershell
whoami /all
```

## Groups

```powershell
whoami /groups
```

## Privileges

```powershell
whoami /priv
```

## PowerShell Version

```powershell
$PSVersionTable
```

## Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

## Execution Policies

```powershell
Get-ExecutionPolicy -List
```

## Load Local Script

```powershell
. .\PrivescCheck.ps1
```

## Find Related Functions

```powershell
Get-Command | Where-Object Name -like '*Privesc*'
```

## Service Configuration

```powershell
sc.exe qc ExampleService
```

## Service State

```powershell
sc.exe query ExampleService
```

## File ACL

```powershell
icacls "C:\Path\To\File"
```

## Directory ACL

```powershell
icacls "C:\Path\To\Directory"
```

## Scheduled Tasks

```powershell
schtasks.exe /query /fo LIST /v
```

## Specific Scheduled Task

```powershell
schtasks.exe /query /tn "\ExampleTask" /fo LIST /v
```

## Registry Query

```powershell
reg.exe query "HKLM\Software\Example"
```

## Environment

```powershell
Get-ChildItem Env:
```

## PATH

```powershell
$env:Path -split ';'
```

---

# PrivescCheck Checklist

## Preparation

- [ ] Host explicitly authorised.
- [ ] Current user recorded.
- [ ] Current groups recorded.
- [ ] Current privileges recorded.
- [ ] Host information recorded.
- [ ] PowerShell version known.
- [ ] Language mode checked.
- [ ] Execution policy understood.
- [ ] Application-control context considered.
- [ ] Official PrivescCheck source used.

## Execution

- [ ] Script reviewed before use.
- [ ] Exact version/revision recorded where useful.
- [ ] Output retained securely.
- [ ] Sensitive information protected.
- [ ] Endpoint-security impact considered.

## Services

- [ ] Privileged services identified.
- [ ] Service identity confirmed.
- [ ] Binary path confirmed.
- [ ] File ACL validated.
- [ ] Directory ACL validated.
- [ ] Service-object permissions considered.
- [ ] Restart/trigger conditions confirmed.
- [ ] Unquoted paths manually validated.

## Scheduled Tasks

- [ ] Privileged tasks identified.
- [ ] Task action identified.
- [ ] Execution identity confirmed.
- [ ] Referenced file permissions checked.
- [ ] Parent directories checked.
- [ ] Trigger confirmed.

## Filesystem

- [ ] Interesting files validated.
- [ ] Interesting directories validated.
- [ ] Effective permissions understood.
- [ ] Inherited permissions considered.
- [ ] Deny entries considered.
- [ ] Privileged consumer confirmed.

## Registry

- [ ] Interesting registry locations confirmed.
- [ ] Effective permissions evaluated.
- [ ] Privileged consumer identified.
- [ ] Installer-related policy reviewed carefully.

## Credentials

- [ ] Potential credentials treated as sensitive.
- [ ] Stale/example data distinguished from live secrets.
- [ ] Unnecessary authentication attempts avoided.
- [ ] Finding describes actual exposure.

## PATH and DLL

- [ ] Writable PATH entries treated as candidates only.
- [ ] Privileged command resolution confirmed.
- [ ] DLL loading context understood.
- [ ] Writable search location validated.
- [ ] Security controls considered.

## Security Controls

- [ ] AppLocker considered.
- [ ] WDAC considered.
- [ ] Defender considered.
- [ ] EDR considered.
- [ ] Constrained Language Mode considered.

## Validation

- [ ] Tool result treated as candidate evidence.
- [ ] Native validation performed.
- [ ] Effective user influence confirmed.
- [ ] Privileged consumer confirmed.
- [ ] Trigger confirmed.
- [ ] Security-control context considered.
- [ ] False positives considered.
- [ ] Actual impact established.

## Evidence

- [ ] Current identity retained.
- [ ] Relevant PrivescCheck result retained.
- [ ] Native ACL/configuration evidence retained.
- [ ] Privileged execution context documented.
- [ ] Trigger documented.
- [ ] Sensitive data redacted where appropriate.
- [ ] Finding describes underlying weakness.

## Cleanup

- [ ] Tool removed where required.
- [ ] Temporary output removed where required.
- [ ] Evidence retained according to policy.
- [ ] Legitimate Windows/security logs preserved.

---

# Related Tool Notes

[Privilege Escalation Tools](index.md)

[WinPEAS](winpeas.md)

[PowerUp](powerup.md)

Linux equivalents:

[LinPEAS](linpeas.md)

[linux-smart-enumeration](linux-smart-enumeration.md)

---

# Related Windows Notes

[Windows](../../windows/index.md)

[Windows Enumeration](../../windows/enumeration.md)

[Windows Privilege Escalation](../../windows/privilege-escalation.md)

[Windows Services](../../windows/services.md)

[Windows Scheduled Tasks](../../windows/scheduled-tasks.md)

[Windows Registry](../../windows/registry.md)

[Windows Filesystem Permissions](../../windows/filesystem-permissions.md)

[Windows Credentials](../../windows/credentials.md)

[Windows Application Control](../../windows/application-control.md)

[Microsoft Defender](../../windows/defender.md)

[Windows User Account Control](../../windows/uac.md)

[Windows Privilege Escalation Explorer](../../privesc/windows.md)

---

# External References

## Official PrivescCheck Resources

[PrivescCheck - GitHub](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

## Supporting Windows References

[Microsoft - icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls){ target="_blank" rel="noopener noreferrer" }

[Microsoft - sc.exe query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query){ target="_blank" rel="noopener noreferrer" }

[Microsoft - schtasks query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query){ target="_blank" rel="noopener noreferrer" }

[Microsoft - about_Language_Modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }

## Practical Reference

[HackTricks - Windows Local Privilege Escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use PrivescCheck like this:

```text
Run PrivescCheck
      |
      v
Find Warning
      |
      v
Report PrivEsc
```

Use it like this:

```text
Understand Current Identity
        |
        v
Run PrivescCheck
        |
        v
Identify Candidate
        |
        v
Understand Why It Was Flagged
        |
        v
Validate With Native Tools
        |
        +-- icacls
        +-- sc.exe
        +-- schtasks.exe
        +-- reg.exe
        |
        v
Confirm Effective User Influence
        |
        v
Identify Privileged Consumer
        |
        v
Confirm Trigger
        |
        v
Consider AppLocker / WDAC / Defender
        |
        v
Determine Actual Impact
        |
        v
Capture Evidence
        |
        v
Report the Underlying Weakness
```

PrivescCheck is valuable because it provides structured Windows privilege escalation enumeration without replacing the need to understand Windows security boundaries.

The tool highlights where to investigate.

The tester determines whether the condition can actually cross a privilege boundary.
