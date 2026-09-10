---
title: WinPEAS
description: Practical WinPEAS reference for authorised Windows privilege escalation enumeration, interpretation, validation, evidence collection, false-positive analysis, and integration with manual Windows security review.
---

# WinPEAS

WinPEAS is part of the PEASS-ng project and is designed to enumerate Windows systems for conditions that may be relevant to local privilege escalation.

It can inspect a broad range of areas, including:

- users and groups;
- token privileges;
- services;
- scheduled tasks;
- registry configuration;
- filesystem permissions;
- installed applications;
- credentials;
- environment variables;
- network configuration;
- security products;
- potentially sensitive files;
- interesting execution paths.

WinPEAS is most useful as an **enumeration accelerator**.

It is not a vulnerability scanner that can automatically determine whether every highlighted condition is exploitable.

```text
Windows Host
    |
    v
WinPEAS
    |
    +-- Identity
    +-- Privileges
    +-- Services
    +-- Scheduled Tasks
    +-- Registry
    +-- Filesystem
    +-- Credentials
    +-- Applications
    +-- Security Controls
    |
    v
Candidate Conditions
    |
    v
Manual Validation
    |
    v
Privilege Escalation Conclusion
```

!!! warning "Authorised testing only"
    Run WinPEAS only on Windows systems where local security enumeration is explicitly authorised. It performs a large number of checks and may generate endpoint-security telemetry. Review the rules of engagement before transferring or executing third-party enumeration tooling.

---

# Where WinPEAS Fits

WinPEAS normally follows initial access to a Windows system.

A useful workflow is:

```text
Initial Local Access
        |
        v
Identify Current User
        |
        v
Manual Baseline
        |
        v
Run WinPEAS
        |
        v
Review Interesting Results
        |
        v
Validate With Native Tools
        |
        v
Confirm or Reject Candidate
```

Related notes:

[Privilege Escalation Tools](index.md)

[Windows Privilege Escalation](../../windows/privilege-escalation.md)

[Windows Enumeration](../../windows/enumeration.md)

[Privilege Escalation Explorer](../../privesc/windows.md)

---

# What WinPEAS Does

WinPEAS automates many checks that could otherwise be performed manually.

Conceptually:

```text
System State
    |
    +-- Users
    +-- Groups
    +-- Privileges
    +-- Services
    +-- Tasks
    +-- ACLs
    +-- Registry
    +-- Credentials
    +-- Software
    +-- Security Controls
    |
    v
WinPEAS Checks
    |
    v
Prioritised Output
```

The tool attempts to highlight items that may deserve further investigation.

The important word is:

> **may**

A highlighted result is a lead, not a confirmed finding.

---

# Official Project

WinPEAS is maintained as part of PEASS-ng.

Official project:

[PEASS-ng - GitHub](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Use official releases or the official repository when obtaining the tool.

Avoid modified copies from untrusted sources.

---

# Before Running WinPEAS

First understand the current user context.

Run:

```powershell
whoami
```

Then:

```powershell
whoami /groups
```

And:

```powershell
whoami /priv
```

Useful questions include:

```text
Which user am I?

Am I a local administrator?

Which groups do I belong to?

Which token privileges are available?

What integrity level am I running at?
```

Without this context, tool output is harder to interpret.

---

# Record System Context

Before running a large enumeration tool, record basic host information.

Useful native commands include:

```powershell
hostname
```

```powershell
whoami
```

```powershell
systeminfo
```

PowerShell:

```powershell
Get-ComputerInfo
```

where available and permitted.

This creates a baseline for later evidence.

---

# Obtaining WinPEAS

Prefer the official PEASS-ng releases or repository.

Verify:

- repository source;
- release provenance;
- filename;
- hash where appropriate;
- internal malware-scanning requirements;
- engagement approval.

Third-party security tools may be detected by endpoint protection even when they are being used legitimately during an authorised assessment.

---

# Common WinPEAS Formats

PEASS-ng may provide different WinPEAS builds or forms depending on the release.

Examples can include:

```text
winPEAS.exe
winPEASx64.exe
winPEASx86.exe
winPEAS.bat
```

The exact filenames available can change between releases.

Always inspect the official release being used rather than assuming a specific filename exists.

---

# Architecture

Determine whether the host is 32-bit or 64-bit where this matters.

Useful command:

```powershell
$env:PROCESSOR_ARCHITECTURE
```

Another option:

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object OSArchitecture
```

Choose the appropriate binary for the environment.

---

# Basic Execution

A common usage pattern is:

```powershell
.\winPEAS.exe
```

The exact binary name depends on the downloaded release.

If using another official build:

```powershell
.\winPEASx64.exe
```

Do not assume all PEASS-ng releases use the same naming convention.

---

# Save Output

For assessment work, saving output is often more useful than relying entirely on the terminal.

For example:

```powershell
.\winPEAS.exe | Tee-Object -FilePath .\winpeas-output.txt
```

This allows the tester to:

- search results later;
- compare findings;
- retain evidence;
- avoid losing information during long runs.

Be aware that output may contain sensitive information.

Protect the file appropriately.

---

# Output May Contain Secrets

WinPEAS can surface information such as:

- passwords;
- API keys;
- connection strings;
- tokens;
- usernames;
- application secrets;
- sensitive paths.

Do not casually:

- upload raw output;
- paste it into public tickets;
- attach it to reports;
- commit it to Git;
- share it outside the authorised assessment team.

Sanitise evidence where necessary.

---

# Colour Coding

WinPEAS uses colour to draw attention to potentially interesting items.

A common mistake is:

```text
Red output
    |
    v
Confirmed vulnerability
```

This is wrong.

The correct interpretation is:

```text
Highlighted output
    |
    v
Worth investigating
```

Then validate the result manually.

---

# WinPEAS Is a Triage Tool

A useful mental model is:

```text
WinPEAS
   |
   v
Triage
   |
   v
Investigation
   |
   v
Validation
```

Not:

```text
WinPEAS
   |
   v
Automatic Finding Generator
```

---

# Major Enumeration Areas

WinPEAS may inspect areas such as:

```text
System Information
Users and Groups
Token Privileges
Services
Scheduled Tasks
Registry
Filesystem
Installed Software
Credentials
Network
Security Products
Interesting Files
Environment
```

Each category requires a different validation approach.

---

# System Information

System information provides context.

Useful details may include:

- Windows edition;
- build;
- architecture;
- hostname;
- domain membership;
- current user;
- patch information.

The purpose is to understand the environment, not simply collect version numbers.

---

# Patch Information

Operating system version and patch information can provide useful context.

Do not automatically conclude:

```text
Old-looking build
    =
Vulnerable
```

Instead determine:

- current patch state;
- vendor advisory applicability;
- configuration;
- exploit preconditions;
- whether the relevant component is present.

Version-based conclusions require care.

---

# Users

WinPEAS can enumerate local or domain-related user information visible from the system.

Manual validation may include:

```powershell
Get-LocalUser
```

where available.

Or:

```powershell
net user
```

Useful questions:

```text
Which users exist?

Which accounts are administrative?

Are service accounts present?

Are disabled accounts still relevant?

Are unusual local accounts configured?
```

---

# Groups

Review local group membership.

For example:

```powershell
Get-LocalGroup
```

and:

```powershell
Get-LocalGroupMember Administrators
```

where available.

Or:

```powershell
net localgroup
```

Group membership can significantly change the interpretation of a privilege escalation condition.

---

# Token Privileges

Check:

```powershell
whoami /priv
```

WinPEAS may highlight potentially interesting privileges.

Do not assume a privilege is exploitable simply because it appears in the token.

Consider:

```text
Privilege present?
Privilege enabled?
Current process context?
Operating-system restrictions?
Required preconditions?
```

Related note:

[Windows Privilege Escalation](../../windows/privilege-escalation.md)

---

# Services

Windows services are one of the most important areas to review.

WinPEAS may identify:

- service names;
- service accounts;
- executable paths;
- startup modes;
- unquoted paths;
- writable service binaries;
- potentially writable service directories;
- modifiable service configurations.

The validation model is:

```text
Service
  |
  +-- Runs privileged?
  |
  +-- Binary/path modifiable?
  |
  +-- Configuration modifiable?
  |
  +-- Trigger available?
  |
  v
Potential PrivEsc
```

Related note:

[Windows Services](../../windows/services.md)

---

# Validate Service Configuration

Use native tooling.

For example:

```powershell
sc.exe qc ExampleService
```

This can show information such as:

```text
SERVICE_START_NAME
BINARY_PATH_NAME
START_TYPE
```

PowerShell can also be useful:

```powershell
Get-CimInstance Win32_Service | Where-Object Name -eq 'ExampleService'
```

The objective is to confirm what the service actually executes and under which identity.

---

# Service Accounts

A service may run as:

```text
LocalSystem
LocalService
NetworkService
Domain account
Custom local account
```

The potential security impact depends heavily on this execution identity.

A writable binary used by a low-privileged service is not equivalent to one used by `LocalSystem`.

---

# Service Binary Permissions

If WinPEAS highlights a service executable, validate the ACL.

Example:

```powershell
icacls "C:\Program Files\Example\Service.exe"
```

Review whether the current user or one of their groups has rights such as:

```text
F
M
W
```

which may correspond to:

```text
Full control
Modify
Write
```

Do not infer permissions from the directory name alone.

---

# Directory Permissions

Even when a binary itself is protected, the containing directory may matter.

Check:

```powershell
icacls "C:\Program Files\Example"
```

Review:

- inherited permissions;
- group permissions;
- write/modify rights;
- creator-owner behaviour.

The complete path may matter.

---

# Effective Permissions Matter

A tool may flag a path because one ACL entry appears writable.

You still need to understand:

- inherited ACEs;
- group membership;
- deny ACEs;
- owner;
- integrity level;
- application control.

The real question is:

> Can the current security context actually modify the object?

---

# Service Restartability

A service-related condition may require a restart before changed content executes.

Check whether the current user can control the service.

Example information gathering:

```powershell
sc.exe query ExampleService
```

Do not assume the user can stop or start the service.

Possible execution triggers include:

```text
Immediate restart
Automatic recovery
Scheduled restart
System reboot
Administrator action
```

Document the actual trigger.

---

# Unquoted Service Paths

WinPEAS may highlight unquoted service paths.

Example:

```text
C:\Program Files\Example App\Service.exe
```

An unquoted path alone is not enough for exploitation.

Also determine whether:

- an earlier path component can be influenced;
- relevant directories are writable;
- the service runs privileged;
- the service can be triggered.

Related note:

[Windows Services](../../windows/services.md)

---

# Service Configuration Permissions

The service executable might be protected while the service object itself is modifiable.

Relevant properties include:

- executable path;
- service identity;
- startup configuration.

A service configuration weakness can be more significant than a file-permission weakness.

Manual validation is required.

---

# Scheduled Tasks

Scheduled tasks can create privileged execution paths.

WinPEAS may identify:

- task name;
- user context;
- trigger;
- executable;
- script;
- argument;
- potentially writable referenced files.

Related note:

[Windows Scheduled Tasks](../../windows/scheduled-tasks.md)

---

# Validate Scheduled Tasks

Native command:

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

Then inspect the action:

```powershell
(Get-ScheduledTask -TaskName "ExampleTask").Actions
```

---

# Task Execution Identity

Important questions include:

```text
Who runs the task?

SYSTEM?

Administrator?

Service account?

Current user?
```

A writable task script has much greater impact if executed in a privileged context.

---

# Task Trigger

Also determine:

```text
When does it execute?

At startup?

At logon?

On a schedule?

On an event?
```

A condition that executes every minute has different practical characteristics from one requiring a reboot or administrator logon.

---

# Task File Permissions

If a task invokes:

```text
C:\ProgramData\Scripts\backup.ps1
```

validate:

```powershell
icacls "C:\ProgramData\Scripts\backup.ps1"
```

Also check its parent directory:

```powershell
icacls "C:\ProgramData\Scripts"
```

---

# Registry

WinPEAS can highlight registry locations relevant to privilege escalation.

Potentially important categories include:

- service configuration;
- application startup;
- installer settings;
- application configuration;
- credentials;
- execution-related registry values.

Related note:

[Windows Registry](../../windows/registry.md)

---

# Registry Permissions

Validate potentially writable keys.

PowerShell can inspect registry objects, while native tools can query values.

Example:

```powershell
reg.exe query "HKLM\Software\Example"
```

For permissions, use an appropriate ACL inspection method.

The key question is:

```text
Can the current user modify a value that a privileged process trusts?
```

---

# AlwaysInstallElevated

Some enumeration tools check Windows Installer policy related to elevated MSI installation.

If such a condition is reported, validate both relevant policy locations and the actual environment before drawing a conclusion.

The security significance depends on whether the configuration permits a lower-privileged user to influence elevated installer execution.

Do not report merely because one registry value exists.

---

# Filesystem Enumeration

WinPEAS inspects many filesystem locations.

Potentially interesting findings include:

- writable privileged executables;
- writable scripts;
- configuration files;
- credential files;
- weakly protected directories;
- startup resources.

Related note:

[Windows Filesystem Permissions](../../windows/filesystem-permissions.md)

---

# Validate Files with icacls

Use:

```powershell
icacls "C:\Path\To\File"
```

and:

```powershell
icacls "C:\Path\To\Directory"
```

Interpret:

- explicit ACEs;
- inherited ACEs;
- user/group rights;
- deny entries.

The result should support a specific conclusion.

---

# Parent Directory Analysis

A protected file may still be replaceable depending on parent-directory permissions.

Example structure:

```text
C:\
  ProgramData\
    Example\
      service.exe
```

Check each relevant level where needed.

The question is not only:

```text
Can I write the file?
```

but also:

```text
Can I rename/delete/replace it through directory permissions?
```

---

# Installed Applications

WinPEAS may identify installed software.

This can help find:

- privileged services;
- custom applications;
- management tools;
- legacy products;
- local agents.

Do not convert every old version into a vulnerability.

Validate:

- exact build;
- vendor patch status;
- exposed functionality;
- configuration;
- exploit preconditions.

---

# Application Directories

Third-party applications are often installed under:

```text
C:\Program Files\
C:\Program Files (x86)\
C:\ProgramData\
```

Review whether application-specific subdirectories have unusual permissions.

Do not assume the whole top-level directory is writable simply because one application directory is.

---

# Credentials

WinPEAS may identify potentially sensitive credential material.

Examples can include:

- configuration files;
- scripts;
- saved credentials;
- environment variables;
- deployment artefacts;
- connection strings;
- unattended installation files.

Related note:

[Windows Credentials](../../windows/credentials.md)

Treat discovered credentials as high-sensitivity assessment data.

---

# Credential Findings Require Validation

A string that looks like a password may be:

- example data;
- expired;
- unused;
- encrypted;
- placeholder content;
- test data.

Before describing credential exposure as exploitable, determine whether it is genuine and relevant.

Avoid unnecessary authentication attempts.

---

# Environment Variables

Environment variables can expose:

- application paths;
- credentials;
- tokens;
- configuration;
- execution paths.

Inspect manually:

```powershell
Get-ChildItem Env:
```

Security relevance depends on whether sensitive information is actually exposed or whether a privileged process trusts modifiable environment data.

---

# PATH

Windows PATH configuration can sometimes matter when privileged software resolves commands without explicit paths.

Inspect:

```powershell
$env:Path -split ';'
```

Then assess:

```text
Which directories appear first?

Are any writable?

Does a privileged application actually resolve a command through PATH?
```

A writable PATH directory without a privileged consumer is not automatically exploitable.

---

# DLL Search Paths

WinPEAS may highlight DLL-related conditions.

DLL loading security depends on:

- application load behaviour;
- DLL search order;
- writable locations;
- application-control policy;
- execution context.

A writable directory alone does not prove a DLL hijacking path.

Related note:

[Windows Privilege Escalation](../../windows/privilege-escalation.md)

---

# Autoruns and Startup Locations

Startup mechanisms may include:

- Run keys;
- Startup directories;
- services;
- scheduled tasks;
- application-specific autostart mechanisms.

The key questions are:

```text
What executes?

Who can modify it?

Who executes it?

When does it execute?
```

---

# Network Information

WinPEAS can provide network context.

This may include:

- interfaces;
- listening services;
- connections;
- domain information;
- DNS.

Network data can help identify local services or management components relevant to privilege escalation analysis.

---

# Listening Services

A locally bound administrative service may be relevant.

Check:

```powershell
Get-NetTCPConnection -State Listen
```

where available.

Or:

```powershell
netstat -ano
```

Then map the process ID to an application.

Do not interact with services outside assessment scope.

---

# Security Products

WinPEAS may identify endpoint-security products and security controls.

Examples can include:

- Microsoft Defender;
- EDR;
- AppLocker;
- WDAC;
- PowerShell restrictions.

These controls influence how practical a privilege escalation path may be.

Related notes:

[Microsoft Defender](../../windows/defender.md)

[Windows Application Control](../../windows/application-control.md)

---

# AppLocker

An execution path may be writable but restricted by AppLocker.

This can affect practical execution.

However, application control does not automatically remove the underlying weak permission.

Separate:

```text
Configuration weakness
```

from:

```text
Exploitability under current controls
```

Related note:

[Windows Application Control](../../windows/application-control.md)

---

# WDAC

Windows Defender Application Control can also restrict execution.

Where applicable, review whether:

- executable;
- script;
- DLL;

execution is constrained.

Again, document the distinction between:

```text
weak permission
```

and:

```text
execution prevented by defence-in-depth
```

---

# PowerShell Restrictions

WinPEAS execution or PowerShell-based follow-up tooling can be affected by:

- execution policy;
- AppLocker;
- WDAC;
- language mode;
- endpoint security.

A blocked script does not mean no privilege escalation condition exists.

Use native commands for validation where necessary.

---

# Native Validation Is Important

Useful native Windows tools include:

```text
whoami.exe
sc.exe
schtasks.exe
icacls.exe
reg.exe
net.exe
wmic.exe where available
PowerShell cmdlets
```

WinPEAS should guide you toward which native checks matter.

---

# WinPEAS and PowerUp

WinPEAS and PowerUp overlap in several areas.

A useful workflow is:

```text
WinPEAS
   |
   v
Candidate Service
   |
   v
PowerUp
   |
   v
Second Perspective
   |
   v
Native Validation
```

Related tool:

[PowerUp](powerup.md)

---

# WinPEAS and PrivescCheck

PrivescCheck can provide another structured perspective on Windows privilege escalation conditions.

```text
WinPEAS
     |
     +--> Candidate

PrivescCheck
     |
     +--> Related candidate

Native tools
     |
     +--> Confirm effective configuration
```

Related tool:

[PrivescCheck](privesccheck.md)

---

# WinPEAS and Manual Enumeration

Automated and manual enumeration should complement each other.

```text
WinPEAS
   |
   +-- breadth

Manual Checks
   |
   +-- precision
   +-- context
   +-- interpretation
```

This combination produces stronger assessment conclusions.

---

# Searching WinPEAS Output

Large output can be difficult to review.

If saved:

```text
winpeas-output.txt
```

search for relevant areas with PowerShell:

```powershell
Select-String -Path .\winpeas-output.txt -Pattern "service"
```

or:

```powershell
Select-String -Path .\winpeas-output.txt -Pattern "writable"
```

Do not rely only on keyword searching; preserve enough surrounding context to interpret the result.

---

# Review by Category

A practical review order is:

```text
1. Current user and groups
2. Privileges
3. Services
4. Scheduled tasks
5. Filesystem permissions
6. Registry
7. Credentials
8. Installed applications
9. Security controls
10. Miscellaneous findings
```

This helps prevent long output from becoming unmanageable.

---

# Prioritising WinPEAS Findings

High-value candidates often share three characteristics:

```text
Current user can influence something
        |
        +
Privileged component trusts it
        |
        +
Execution can be triggered
```

This is more useful than prioritising based solely on colour.

---

# Candidate Scoring Model

A simple mental model can be:

| Question | Yes/No |
|---|---|
| Can current user modify the resource? | |
| Is the resource consumed by a privileged process? | |
| Can execution be triggered? | |
| Is the path currently active? | |
| Are security controls likely to block it? | |
| Is additional user interaction required? | |

More "yes" answers generally mean the candidate deserves deeper investigation.

---

# Representative Service Scenario

WinPEAS reports:

```text
Service:
ExampleService

Runs as:
LocalSystem

Binary:
C:\Program Files\Example\Service.exe

Potential issue:
Writable binary
```

Manual validation:

```powershell
sc.exe qc ExampleService
```

Then:

```powershell
icacls "C:\Program Files\Example\Service.exe"
```

Suppose the ACL shows no write or modify rights for the current user.

Conclusion:

```text
The WinPEAS candidate was reviewed, but effective filesystem
permissions did not allow the tested user to modify the service
executable. The suspected privilege escalation path was therefore not
confirmed.
```

---

# Representative Confirmed Permission Scenario

Suppose:

```text
Service:
ExampleService

Account:
LocalSystem

Binary:
C:\ProgramData\Example\Service.exe
```

Manual validation confirms:

```text
Current standard user:
Modify
```

The next steps are to determine:

```text
Is the service active?

Can it restart?

Will it execute this exact file?

Do application-control policies affect execution?
```

Only after the full path is validated should the security condition be reported.

---

# Representative Scheduled Task Scenario

WinPEAS reports:

```text
Task:
ExampleBackup

Runs as:
SYSTEM

Action:
C:\ProgramData\Scripts\backup.ps1
```

Check:

```powershell
icacls "C:\ProgramData\Scripts\backup.ps1"
```

Then check the directory:

```powershell
icacls "C:\ProgramData\Scripts"
```

Inspect task details:

```powershell
schtasks.exe /query /tn "\ExampleBackup" /fo LIST /v
```

The security question is:

> Can the tested user influence content that the SYSTEM task executes?

---

# Representative Credential Scenario

WinPEAS identifies:

```text
Potential password in configuration file
```

Validate carefully:

```text
Is it an actual credential?

Is it still valid?

Which account does it belong to?

Is use of that account in scope?

Is validation necessary?
```

Do not perform unnecessary authentication tests merely to prove a credential exists.

The exposure itself may already be the relevant issue depending on the engagement.

---

# Representative Application Control Scenario

WinPEAS identifies a writable privileged execution path.

AppLocker analysis shows execution from that location is denied.

The correct conclusion may be:

```text
A weak filesystem permission exists, but the tested execution path is
currently constrained by application-control policy. The underlying
permission weakness should still be corrected because the application
control acts as a separate defence-in-depth layer.
```

This is more accurate than either:

```text
No issue because AppLocker exists
```

or:

```text
Immediate SYSTEM compromise
```

---

# False Positives

WinPEAS results can be misleading because of:

- heuristic assumptions;
- inherited ACLs;
- group membership interpretation;
- disabled services;
- inactive tasks;
- stale files;
- false credential patterns;
- protected execution paths;
- security-control interference.

Manual verification is mandatory for high-confidence conclusions.

---

# False Negatives

WinPEAS can also miss real issues.

Possible reasons include:

- custom applications;
- unusual service logic;
- non-standard directories;
- transient files;
- proprietary software;
- custom IPC;
- unusual ACL arrangements;
- application-specific privileged workflows.

A clean WinPEAS output does not prove the system has no privilege escalation path.

---

# Do Not Rely on One Tool

Strong local review might combine:

```text
WinPEAS
    |
    +--> broad enumeration

PowerUp
    |
    +--> Windows-specific checks

PrivescCheck
    |
    +--> additional structured checks

Manual Native Tools
    |
    +--> actual validation
```

The objective is not tool quantity.

The objective is evidence quality.

---

# Endpoint Security and Telemetry

Running WinPEAS can produce observable behaviour through:

- process execution;
- registry enumeration;
- WMI/CIM access;
- filesystem access;
- security-product interaction.

In purple-team exercises, this can be useful for measuring detection coverage.

Related notes:

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

---

# WinPEAS in Purple Team Exercises

A purple-team use case may look like:

```text
WinPEAS Execution
      |
      v
Host Enumeration
      |
      v
EDR / Windows Telemetry
      |
      v
Detection Review
      |
      v
Rule Improvement
```

The exercise objective should be agreed in advance.

---

# Tool Transfer

Where transfer is authorised, retain records such as:

```text
Tool:
WinPEAS

Source:
Official PEASS-ng release

Destination:
Approved temporary test directory

Timestamp:
Recorded

Cleanup:
Completed after testing
```

Do not leave unnecessary assessment tools behind.

---

# Cleanup

After the assessment, remove transferred tool artefacts where required.

For example:

```text
winPEAS executable
output files
temporary working files
```

Do not remove legitimate operating-system or security logs.

Evidence retention should follow the engagement's rules.

---

# Logging the Run

A useful record is:

```text
Host:
User:
WinPEAS release:
Binary:
Command:
Start time:
End time:
Output file:
Relevant findings:
Manual validation:
```

This improves reproducibility.

---

# Evidence Quality

Weak evidence:

```text
Screenshot of highlighted WinPEAS line
```

Better evidence:

```text
WinPEAS output
      |
      v
Native configuration query
      |
      v
ACL output
      |
      v
Execution identity
      |
      v
Trigger
      |
      v
Conclusion
```

The report should explain the chain.

---

# Reporting a Validated Service Weakness

Avoid:

```text
WinPEAS identified an insecure service.
```

Prefer:

```text
The tested standard user had Modify permissions over an executable
configured to run as part of a LocalSystem service. This allowed the
user to influence a privileged execution path. The condition was
validated through the effective filesystem permissions and service
configuration.
```

---

# Reporting a Negative Result

Example:

```text
WinPEAS highlighted a service executable as potentially writable.
Manual validation with icacls showed that the current user and its
groups did not have write or modify permissions. The suspected
privilege escalation path was therefore not confirmed.
```

Negative validation prevents scanner-style overreporting.

---

# Severity Assessment

Privilege escalation severity depends on:

- starting privilege;
- resulting privilege;
- interaction required;
- trigger requirements;
- reliability;
- security controls;
- environment importance.

Example:

```text
Standard user
    |
    v
SYSTEM
```

with an immediate and reliable trigger may represent a high-impact issue.

A path requiring rare administrator action may have different practical risk.

---

# Remediation Principles

WinPEAS findings commonly lead to remediation in areas such as:

- ACLs;
- service configuration;
- scheduled tasks;
- registry permissions;
- credentials;
- startup paths;
- installer policy.

The general principle is:

> Low-privileged users should not be able to influence resources that are executed or trusted by higher-privileged processes.

---

# Service Remediation

Typical measures include:

- remove unnecessary write permissions;
- restrict service configuration rights;
- protect service executable directories;
- quote service paths where relevant;
- use least-privileged service identities.

---

# Scheduled Task Remediation

Typical measures include:

- protect scripts and binaries;
- protect parent directories;
- restrict task modification;
- use least privilege;
- review unnecessary tasks.

---

# Credential Remediation

Typical measures include:

- remove plaintext secrets;
- rotate exposed credentials;
- use secure secret storage;
- limit file permissions;
- remove obsolete deployment artefacts.

---

# Retesting

Do not retest only by rerunning WinPEAS.

For example, after fixing an ACL:

```powershell
icacls "C:\ProgramData\Example\Service.exe"
```

Verify that the tested low-privileged identity no longer has inappropriate modification rights.

Then confirm the application or service still operates correctly.

Optionally rerun WinPEAS as a secondary regression check.

---

# WinPEAS Review Workflow

A strong workflow is:

```text
1. Confirm scope
      |
      v
2. Record current identity
      |
      v
3. Record host context
      |
      v
4. Obtain official WinPEAS build
      |
      v
5. Run approved enumeration
      |
      v
6. Save output securely
      |
      v
7. Prioritise interesting findings
      |
      v
8. Validate with native tools
      |
      v
9. Identify privileged consumer
      |
      v
10. Confirm trigger
      |
      v
11. Consider application controls
      |
      v
12. Confirm or reject candidate
      |
      v
13. Capture evidence
      |
      v
14. Clean up assessment artefacts
```

---

# Quick Command Reference

## Current User

```powershell
whoami
```

## Groups

```powershell
whoami /groups
```

## Privileges

```powershell
whoami /priv
```

## Basic Execution

```powershell
.\winPEAS.exe
```

Use the actual filename from the official release.

## Save Output

```powershell
.\winPEAS.exe | Tee-Object -FilePath .\winpeas-output.txt
```

## Service Configuration

```powershell
sc.exe qc ExampleService
```

## Service Status

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

## Environment Variables

```powershell
Get-ChildItem Env:
```

## PATH

```powershell
$env:Path -split ';'
```

## Listening Ports

```powershell
Get-NetTCPConnection -State Listen
```

Fallback:

```powershell
netstat -ano
```

---

# WinPEAS Checklist

## Preparation

- [ ] Host explicitly authorised.
- [ ] Current identity recorded.
- [ ] Current groups recorded.
- [ ] Current privileges recorded.
- [ ] System architecture known.
- [ ] Official PEASS-ng source used.
- [ ] Tool transfer approved where necessary.
- [ ] Endpoint-security implications understood.

## Execution

- [ ] Correct WinPEAS build selected.
- [ ] Output retained securely.
- [ ] Sensitive output protected.
- [ ] Excessive or unnecessary execution avoided.
- [ ] Tool version or release recorded where useful.

## Service Review

- [ ] Privileged services identified.
- [ ] Service account confirmed.
- [ ] Binary path confirmed.
- [ ] Binary ACL checked.
- [ ] Parent directory ACL checked.
- [ ] Service configuration permissions considered.
- [ ] Restart/trigger conditions confirmed.
- [ ] Unquoted paths validated rather than assumed exploitable.

## Scheduled Tasks

- [ ] Privileged tasks identified.
- [ ] Task identity confirmed.
- [ ] Action path confirmed.
- [ ] Script/binary permissions checked.
- [ ] Parent directories checked.
- [ ] Trigger confirmed.

## Registry

- [ ] Interesting keys reviewed.
- [ ] Effective permissions validated.
- [ ] Privileged consumer identified.
- [ ] Installer-related policy interpreted carefully.

## Filesystem

- [ ] Interesting writable files validated.
- [ ] Interesting writable directories validated.
- [ ] Parent directories reviewed.
- [ ] Actual privileged consumer confirmed.

## Credentials

- [ ] Potential secrets reviewed carefully.
- [ ] Sensitive values protected.
- [ ] Stale/example credentials distinguished from active secrets.
- [ ] Unnecessary authentication attempts avoided.

## Security Controls

- [ ] Defender considered.
- [ ] AppLocker considered.
- [ ] WDAC considered.
- [ ] PowerShell restrictions considered.
- [ ] EDR impact considered.

## Validation

- [ ] WinPEAS result treated as candidate.
- [ ] Native validation performed.
- [ ] Effective permissions confirmed.
- [ ] Privileged execution context confirmed.
- [ ] Trigger confirmed.
- [ ] False-positive explanations considered.
- [ ] Security impact demonstrated appropriately.

## Evidence

- [ ] Current identity retained.
- [ ] Relevant WinPEAS excerpt retained.
- [ ] Native ACL/configuration evidence retained.
- [ ] Execution context documented.
- [ ] Trigger documented.
- [ ] Sensitive values redacted where appropriate.
- [ ] Finding describes underlying weakness, not WinPEAS output.

## Cleanup

- [ ] WinPEAS binary removed if required.
- [ ] Temporary output removed if required.
- [ ] Evidence retained according to engagement policy.
- [ ] Legitimate logs left intact.

---

# Related Tool Notes

[Privilege Escalation Tools](index.md)

[PowerUp](powerup.md)

[PrivescCheck](privesccheck.md)

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

## Official PEASS-ng Resources

[PEASS-ng - GitHub](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

[PEASS-ng Releases](https://github.com/peass-ng/PEASS-ng/releases){ target="_blank" rel="noopener noreferrer" }

---

## Supporting Windows Privilege Escalation References

[HackTricks - Windows Local Privilege Escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html){ target="_blank" rel="noopener noreferrer" }

[Microsoft - icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls){ target="_blank" rel="noopener noreferrer" }

[Microsoft - sc.exe query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query){ target="_blank" rel="noopener noreferrer" }

[Microsoft - schtasks query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use WinPEAS like this:

```text
Run WinPEAS
    |
    v
Find Red Text
    |
    v
Call It PrivEsc
```

Use it like this:

```text
Understand Current Identity
        |
        v
Run WinPEAS
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
        +-- registry inspection
        |
        v
Confirm Effective Permissions
        |
        v
Identify Privileged Consumer
        |
        v
Confirm Trigger
        |
        v
Consider Security Controls
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

WinPEAS is most valuable when it reduces the amount of Windows configuration that must be inspected manually.

It identifies where to look.

The tester still has to determine whether the highlighted condition forms a genuine privilege escalation path.
