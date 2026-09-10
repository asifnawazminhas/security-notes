---
title: PowerUp
description: Practical PowerUp reference for authorised Windows privilege escalation enumeration, service and filesystem checks, registry analysis, interpretation, manual validation, evidence collection, and integration with wider Windows security assessment workflows.
---

# PowerUp

PowerUp is a PowerShell-based collection of Windows privilege escalation checks from the PowerSploit project.

It is designed to identify local Windows configuration conditions that may deserve further investigation during an authorised security assessment.

Typical areas include:

- Windows services;
- service executable permissions;
- service configuration permissions;
- unquoted service paths;
- registry configuration;
- installer-related policy;
- writable application locations;
- potentially exposed credentials;
- autologon configuration;
- DLL-related conditions;
- other local privilege escalation candidates.

PowerUp should be treated as an **enumeration and triage tool**.

It does not automatically prove that a highlighted configuration can be used to gain additional privilege.

```text
Windows Host
    |
    v
PowerUp
    |
    +-- Services
    +-- Permissions
    +-- Registry
    +-- Installer Policy
    +-- Credentials
    +-- Execution Paths
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
    Use PowerUp only on Windows systems where local security testing is explicitly authorised. PowerShell-based security tooling can generate endpoint-security telemetry and may be blocked by application control or endpoint protection. Review the rules of engagement before loading or executing third-party scripts.

---

# Where PowerUp Fits

PowerUp normally sits between initial local enumeration and focused manual validation.

```text
Initial Access
    |
    v
Current User Context
    |
    v
Manual Baseline
    |
    v
PowerUp
    |
    v
Candidate Condition
    |
    v
Native Windows Validation
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

PowerUp is part of PowerSploit.

Project reference:

[PowerUp - PowerSploit](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc){ target="_blank" rel="noopener noreferrer" }

The PowerSploit repository should be treated as the canonical historical source for the original PowerUp implementation.

Because PowerSploit is an older project, always review:

- repository state;
- script provenance;
- last update;
- PowerShell compatibility;
- endpoint-security impact;
- environment restrictions;

before relying on a copy during an assessment.

---

# What PowerUp Does

PowerUp automates checks for local Windows configurations that may allow a lower-privileged user to influence privileged execution.

A useful model is:

```text
System Configuration
        |
        +-- Services
        +-- Registry
        +-- Files
        +-- Directories
        +-- Installer Policy
        +-- Credentials
        |
        v
PowerUp Checks
        |
        v
Potential PrivEsc Candidates
```

The tool tries to answer:

> Where should I investigate further?

It does not answer:

> Which findings are definitely exploitable?

---

# Before Running PowerUp

Start with the current security context.

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
Who am I?

Am I already a local administrator?

Which groups do I belong to?

Which token privileges are available?

Is the shell elevated?
```

This context is essential when interpreting PowerUp output.

---

# PowerShell Environment

PowerUp depends on PowerShell.

Check the PowerShell version:

```powershell
$PSVersionTable
```

Check the current language mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible language modes include:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

PowerUp may not function fully in restricted environments.

---

# Execution Policy

Execution policy can affect script loading.

Check:

```powershell
Get-ExecutionPolicy -List
```

Execution policy is not intended to be a hard security boundary.

However, it may affect how PowerUp can be loaded in a particular environment.

Do not change enterprise execution policy merely to run the script unless that change is explicitly authorised.

---

# Application Control

PowerUp may be affected by:

- AppLocker;
- Windows Defender Application Control;
- PowerShell Constrained Language Mode;
- Defender;
- EDR controls.

Related notes:

[Windows Application Control](../../windows/application-control.md)

[Microsoft Defender](../../windows/defender.md)

If PowerUp cannot run, use native Windows commands to perform the underlying checks manually.

---

# Obtaining PowerUp

Prefer the official PowerSploit repository.

Review the script before use.

Do not use random modified copies from paste sites or unknown repositories.

Record where the script came from when evidence provenance matters.

---

# Importing PowerUp

If an authorised local copy exists:

```powershell
Import-Module .\PowerUp.ps1
```

Another common approach is dot-sourcing:

```powershell
. .\PowerUp.ps1
```

The exact method depends on the script copy and PowerShell environment.

After loading, inspect available functions rather than assuming a particular function set.

For example:

```powershell
Get-Command -Module PowerUp
```

if imported as a module.

If dot-sourced, use:

```powershell
Get-Command *Service* | Where-Object Source -eq ''
```

or inspect the script help directly.

---

# Script Help

Use built-in PowerShell help where available.

For example:

```powershell
Get-Help Invoke-AllChecks
```

Detailed help:

```powershell
Get-Help Invoke-AllChecks -Full
```

The installed or downloaded script is the best source for exact function syntax.

---

# Invoke-AllChecks

A commonly used PowerUp entry point is:

```powershell
Invoke-AllChecks
```

This runs multiple local privilege escalation checks.

Conceptually:

```text
Invoke-AllChecks
      |
      +-- Service Checks
      +-- Permission Checks
      +-- Registry Checks
      +-- Installer Policy
      +-- Credential Checks
      |
      v
Candidate Findings
```

Do not treat the output as confirmed exploitation.

---

# Save Output

For assessment work, save output for later review.

Example:

```powershell
Invoke-AllChecks | Tee-Object -FilePath .\powerup-output.txt
```

PowerUp output may contain:

- usernames;
- service paths;
- permissions;
- registry values;
- potential credentials.

Protect the output appropriately.

---

# PowerUp and Services

Services are one of PowerUp's most important areas.

Potential findings may involve:

- writable service executable;
- writable service directory;
- weak service permissions;
- unquoted service path;
- modifiable service configuration.

A good service analysis model is:

```text
Service
  |
  +-- Runs privileged?
  |
  +-- User can influence binary?
  |
  +-- User can influence configuration?
  |
  +-- Execution can be triggered?
  |
  v
Potential PrivEsc
```

Related note:

[Windows Services](../../windows/services.md)

---

# Service Configuration

If PowerUp reports a service-related candidate, first confirm the service configuration.

Use:

```powershell
sc.exe qc ExampleService
```

Review:

```text
SERVICE_NAME
START_TYPE
BINARY_PATH_NAME
SERVICE_START_NAME
```

PowerShell can also help:

```powershell
Get-CimInstance Win32_Service | Where-Object Name -eq 'ExampleService'
```

This confirms what the service actually executes and which account it uses.

---

# Service Identity

A service may run as:

```text
LocalSystem
LocalService
NetworkService
Domain service account
Custom local account
```

Impact depends strongly on the execution identity.

A service running as LocalSystem generally represents a more privileged execution context than a low-privileged service account.

---

# Writable Service Executable

Suppose PowerUp reports:

```text
Service binary may be writable
```

Validate with:

```powershell
icacls "C:\Program Files\Example\Service.exe"
```

Review:

- current user;
- group memberships;
- explicit permissions;
- inherited permissions;
- deny entries.

Do not rely solely on PowerUp's interpretation.

---

# Writable Service Directory

The executable itself may be protected while its parent directory is modifiable.

Check:

```powershell
icacls "C:\Program Files\Example"
```

The relevant question is:

> Can the current user replace, rename, delete, or otherwise influence the service binary through directory permissions?

The exact answer depends on effective ACLs.

---

# Weak Service Permissions

Service objects themselves have security descriptors.

A user may lack file write access but still have permissions to modify the service configuration.

Possible security-relevant rights include the ability to alter:

- binary path;
- service configuration;
- service identity;
- startup configuration.

Do not infer these permissions from filesystem ACLs.

They are separate security objects.

---

# Service Permission Model

A service privilege escalation condition can arise through:

```text
Weak File ACL
```

or:

```text
Weak Directory ACL
```

or:

```text
Weak Service Object ACL
```

These are distinct.

A complete review should identify which trust boundary is weak.

---

# Unquoted Service Paths

PowerUp commonly checks for unquoted service paths.

Example:

```text
C:\Program Files\Example Application\Service.exe
```

The important distinction is:

```text
Unquoted Path
   !=
Exploitable Path
```

Also verify:

- service runs privileged;
- earlier path locations exist;
- user can write to a relevant location;
- service can be triggered;
- application-control policy.

---

# Unquoted Path Validation Model

```text
Unquoted Service Path
        |
        v
Contains Spaces?
        |
        v
Potential Earlier Executable Resolution
        |
        v
Relevant Directory Writable?
        |
        v
Privileged Service?
        |
        v
Reachable Trigger?
```

Only the full chain determines risk.

---

# Example Unquoted Service Path

Suppose:

```text
C:\Program Files\Example App\Service.exe
```

Potential path interpretation may involve earlier components depending on Windows executable resolution behaviour.

Do not create proof files on production systems without explicit authorisation.

First validate permissions and service configuration safely.

---

# Service Restart Conditions

Even when a service path can be influenced, execution may require a trigger.

Determine whether:

- current user can restart the service;
- service restarts automatically on failure;
- service starts at boot;
- an administrator action is required.

Check state:

```powershell
sc.exe query ExampleService
```

Document the actual trigger.

---

# PowerUp Service Findings and Native Validation

A strong workflow is:

```text
PowerUp
   |
   v
Candidate Service
   |
   v
sc.exe qc
   |
   v
icacls
   |
   v
Service Permission Review
   |
   v
Trigger Review
   |
   v
Conclusion
```

---

# Registry Checks

PowerUp may inspect registry configuration related to privilege escalation.

Potential areas can include:

- service configuration;
- installer settings;
- autologon;
- application settings;
- execution paths.

Related note:

[Windows Registry](../../windows/registry.md)

---

# AlwaysInstallElevated

PowerUp may check the Windows Installer policy commonly associated with `AlwaysInstallElevated`.

The condition is only security relevant when the required policy configuration is present in the relevant machine and user contexts.

Do not report based on one registry value alone.

A validation process should determine:

```text
Machine policy set?
User policy set?
Current user context?
Actual installer behaviour?
```

The underlying issue is an unsafe elevated installer policy.

---

# AlwaysInstallElevated Validation

Inspect the relevant policy configuration using native registry tools.

For example, query the configured Windows Installer policy locations rather than trusting tool output alone.

Document:

```text
Registry path
Value
Current user context
Machine context
```

Avoid creating or executing installer payloads merely to prove the policy unless explicit exploitation validation is required and authorised.

---

# Autologon Information

PowerUp may identify autologon-related registry information.

Possible values may include:

```text
DefaultUserName
DefaultDomainName
DefaultPassword
```

where configured.

If sensitive credentials are present, treat them carefully.

Related note:

[Windows Credentials](../../windows/credentials.md)

---

# Autologon Does Not Always Mean Plaintext Password

Do not assume every autologon configuration exposes a usable plaintext password.

Validate what values actually exist.

Possible outcomes include:

```text
Username only
```

or:

```text
Domain information only
```

or:

```text
Credential material present
```

Report only what the evidence supports.

---

# Credential Findings

PowerUp may identify possible credential material in local configuration.

A candidate credential could be:

- active;
- expired;
- unused;
- placeholder;
- test data.

Do not automatically attempt authentication with every discovered value.

First determine whether validation is necessary and authorised.

---

# Filesystem Checks

PowerUp may identify writable files or directories associated with privileged applications.

Validate with:

```powershell
icacls "C:\Path\To\File"
```

and:

```powershell
icacls "C:\Path\To\Directory"
```

Related note:

[Windows Filesystem Permissions](../../windows/filesystem-permissions.md)

---

# Effective Permissions

The security question is not:

```text
Does an ACL contain "Users"?
```

It is:

```text
Does the current user, through their effective security token,
actually have the permission required to influence the object?
```

Consider:

- direct user ACEs;
- group ACEs;
- inherited ACEs;
- deny ACEs;
- owner;
- integrity level.

---

# Parent Directory Permissions

Always consider the full path.

Example:

```text
C:\ProgramData\Vendor\App\Service.exe
```

Review:

```powershell
icacls "C:\ProgramData\Vendor\App\Service.exe"
```

and, where relevant:

```powershell
icacls "C:\ProgramData\Vendor\App"
```

The parent directory may allow operations that affect the child object.

---

# DLL-Related Conditions

PowerUp may identify potential DLL-related privilege escalation conditions.

DLL loading issues require careful validation.

Relevant factors include:

```text
Which process loads the DLL?

Which DLL name is requested?

Which search order applies?

Which directories are writable?

What account executes the process?

Do application-control policies apply?
```

A writable directory alone does not prove a DLL hijacking condition.

---

# DLL Search Order

Windows searches for DLLs according to a specific loading process influenced by:

- application path;
- system directories;
- current directory;
- PATH;
- SafeDllSearchMode;
- application-specific loading behaviour.

The exact mechanism depends on how the program loads the library.

Do not make broad conclusions from a generic writable PATH directory.

---

# PATH Checks

PowerUp may flag writable directories in PATH.

Inspect:

```powershell
$env:Path -split ';'
```

Then check individual paths with:

```powershell
icacls "C:\Path"
```

The key question is:

```text
Does a privileged process search this directory for a binary or DLL?
```

If not, the writable PATH entry may not create a privilege escalation path.

---

# Startup Locations

PowerUp may identify autostart-related configuration.

Potential areas include:

- Run keys;
- Startup folders;
- services;
- scheduled tasks.

The important questions are:

```text
What executes?

Who can modify it?

Who executes it?

When is it triggered?
```

---

# Scheduled Tasks

PowerUp historically focuses strongly on services and local configuration, but scheduled tasks should still be reviewed manually as part of the overall privilege escalation methodology.

Use:

```powershell
schtasks.exe /query /fo LIST /v
```

or:

```powershell
Get-ScheduledTask
```

Related note:

[Windows Scheduled Tasks](../../windows/scheduled-tasks.md)

Do not assume PowerUp provides complete coverage of every scheduled execution path.

---

# PowerUp vs WinPEAS

PowerUp and WinPEAS overlap, but they are not identical.

```text
WinPEAS
   |
   +-- very broad host enumeration

PowerUp
   |
   +-- focused Windows privilege escalation checks
   +-- PowerShell-based
```

A useful workflow is:

```text
WinPEAS
   |
   v
Broad Candidates
   |
   v
PowerUp
   |
   v
Focused Cross-Check
   |
   v
Native Validation
```

Related note:

[WinPEAS](winpeas.md)

---

# PowerUp vs PrivescCheck

PrivescCheck provides another PowerShell-based approach to local Windows privilege escalation enumeration.

```text
PowerUp
    |
    +--> Candidate

PrivescCheck
    |
    +--> Related candidate

Native Tools
    |
    v
Validation
```

Related note:

[PrivescCheck](privesccheck.md)

---

# PowerUp and Manual Enumeration

PowerUp should supplement native Windows analysis.

Useful native tools include:

```text
whoami.exe
sc.exe
icacls.exe
schtasks.exe
reg.exe
PowerShell cmdlets
```

The tool helps identify where to focus those checks.

---

# PowerUp and AppLocker

PowerUp may identify a technically interesting writable execution path.

AppLocker may restrict executable or script execution from that location.

This changes practical exploitability.

It does not automatically correct the weak ACL.

Separate:

```text
Underlying permission issue
```

from:

```text
Defence-in-depth control
```

Related note:

[Windows Application Control](../../windows/application-control.md)

---

# PowerUp and WDAC

WDAC may enforce code integrity beyond normal filesystem permissions.

A candidate path could be:

```text
Writable
```

but:

```text
Unapproved binary cannot execute
```

This may substantially reduce practical risk.

However, the configuration should still be evaluated according to the intended security boundary.

---

# PowerUp and Constrained Language Mode

Constrained Language Mode may limit PowerShell functionality.

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

If PowerUp cannot execute fully:

```text
PowerUp failure
    !=
No privilege escalation issues
```

Switch to native/manual enumeration.

---

# PowerUp and Defender

Microsoft Defender or EDR may detect or block PowerUp.

Do not disable endpoint protection simply to run the tool unless the engagement explicitly authorises such action.

Instead:

- coordinate testing;
- use allowed tooling;
- perform equivalent native checks.

Related note:

[Microsoft Defender](../../windows/defender.md)

---

# Script Provenance

Because PowerUp is frequently copied between repositories, preserve provenance.

Useful record:

```text
Tool:
PowerUp.ps1

Source:
PowerSploit repository

Commit/release:
Recorded where relevant

Hash:
Recorded where required
```

This makes results more reproducible.

---

# PowerUp Function Names

PowerUp contains multiple functions targeting different Windows privilege escalation conditions.

Function names can vary across forks and versions.

Do not build a permanent knowledge base around an assumed function list without checking the actual script.

Use:

```powershell
Get-Command
```

and:

```powershell
Get-Help
```

against the version being used.

---

# Reviewing PowerUp Source

PowerShell source is readable.

Before using a function:

1. locate it in `PowerUp.ps1`;
2. understand what it checks;
3. understand what constitutes a positive result;
4. determine whether the function performs only enumeration or also modifies state.

This is especially important for functions that include exploitation or write functionality.

---

# Enumeration vs Modification

A security tool may contain both:

```text
Check functions
```

and:

```text
Abuse / write functions
```

These should be treated differently.

For normal validation:

```text
Prefer read-only enumeration first
```

Then use separate controlled validation only where necessary and authorised.

---

# Do Not Automatically Run Exploitation Functions

PowerUp has historically included functionality beyond passive enumeration.

Do not automatically use functions that:

- modify services;
- create users;
- alter files;
- change registry values;
- modify system configuration.

A finding can often be validated through permissions and configuration evidence without modifying the host.

---

# Safe Validation Principle

Prefer:

```text
Read configuration
      |
      v
Check ACL
      |
      v
Confirm privileged consumer
      |
      v
Confirm trigger
```

before:

```text
Modify privileged resource
```

This reduces operational impact.

---

# Representative Service Scenario

Suppose:

```powershell
Invoke-AllChecks
```

reports a potentially writable service executable.

PowerUp output identifies:

```text
ServiceName:
ExampleService

Path:
C:\ProgramData\Example\Service.exe
```

Validate service configuration:

```powershell
sc.exe qc ExampleService
```

Then file permissions:

```powershell
icacls "C:\ProgramData\Example\Service.exe"
```

Then directory permissions:

```powershell
icacls "C:\ProgramData\Example"
```

Determine:

```text
Which account runs service?

Can current user modify file?

Can current user replace file?

Can current user trigger service?

Does application control restrict execution?
```

Only then reach a conclusion.

---

# Representative Weak Service Configuration Scenario

PowerUp identifies that the current user may have service configuration rights.

Validate the service's security permissions using an appropriate native or administrative inspection method available in the environment.

The relevant security question is:

> Can the low-privileged user alter how a higher-privileged service executes?

If yes, the weak service object permission is the finding.

---

# Representative Unquoted Service Path Scenario

PowerUp reports:

```text
C:\Program Files\Example App\Service.exe
```

Validate:

1. service account;
2. exact service path;
3. write permissions on candidate directories;
4. service trigger;
5. application-control restrictions.

If all candidate locations are protected:

```text
Unquoted path present
```

may represent hardening debt without a practical local privilege escalation path for the tested user.

Do not overstate it.

---

# Representative AlwaysInstallElevated Scenario

PowerUp reports that installer policy may allow elevated MSI installation.

Validate both policy contexts.

If only one required policy value is configured, the full privilege escalation condition may not exist.

The conclusion should state exactly what was verified.

---

# Representative Autologon Scenario

PowerUp identifies:

```text
DefaultUserName
DefaultPassword
```

If a plaintext password is exposed to the low-privileged user, assess:

- account privilege;
- password reuse scope where authorised;
- whether the account provides higher local privilege.

The primary finding may be insecure local credential storage.

---

# Representative Writable PATH Scenario

PowerUp highlights:

```text
C:\Tools
```

because the directory is writable and appears in PATH.

Do not conclude privilege escalation immediately.

Determine whether a privileged service or scheduled process executes an unqualified command that could resolve through this path.

Without a privileged consumer, there may be no escalation path.

---

# Representative DLL Scenario

PowerUp reports a possible DLL hijacking condition.

Validate:

```text
Target process
Requested DLL
Load method
Search order
Writable directory
Execution identity
Trigger
```

If no privileged process loads the DLL from the writable location, the candidate is not confirmed.

---

# False Positives

PowerUp can produce misleading candidates because of:

- broad ACL heuristics;
- inherited permissions;
- disabled services;
- protected candidate directories;
- incomplete service-trigger context;
- application-control restrictions;
- registry values without full policy conditions;
- stale credential configuration.

Manual validation is essential.

---

# False Negatives

PowerUp can also miss privilege escalation paths.

Possible reasons include:

- custom applications;
- scheduled-task logic;
- proprietary services;
- unusual registry usage;
- non-standard directories;
- application-specific IPC;
- newer Windows features;
- configurations added after the script's development.

Do not treat a clean PowerUp result as proof that the host has no local privilege escalation weaknesses.

---

# Why PowerUp Age Matters

PowerUp remains useful because many Windows privilege escalation fundamentals have not changed.

However, Windows platforms and defensive controls have evolved.

Modern environments may include:

- WDAC;
- AppLocker;
- stronger Defender protections;
- EDR;
- newer service and application configurations.

Therefore combine PowerUp with:

- WinPEAS;
- PrivescCheck;
- native commands;
- manual reasoning.

---

# Candidate Evaluation Model

For each PowerUp result, ask:

| Question | Answer |
|---|---|
| What exactly was identified? | |
| Can the current user influence it? | |
| What effective permission proves this? | |
| Which privileged process consumes it? | |
| What identity runs that process? | |
| Can execution be triggered? | |
| Which security controls apply? | |
| What additional privilege results? | |

If these questions cannot be answered, the result may not yet be a finding.

---

# Evidence Collection

For a PowerUp-supported finding, retain:

```text
Current user:
Current groups:
PowerUp function/check:
PowerUp result:
Affected object:
Native validation:
Effective ACL:
Privileged consumer:
Execution identity:
Trigger:
Security controls:
Impact:
```

For example:

```text
Current user:
CORP\tester

Candidate:
Service executable permission

Affected path:
C:\ProgramData\Vendor\Service.exe

Service:
VendorService

Service account:
LocalSystem

Validation:
icacls confirmed Modify permission through an assigned local group.
```

---

# Evidence Should Be Native Where Possible

PowerUp output is useful supporting evidence.

The strongest primary evidence is often:

- `sc.exe` output;
- `icacls.exe` output;
- registry configuration;
- scheduled-task configuration;
- effective user/group context.

This makes the finding independently understandable without requiring the reader to know PowerUp.

---

# Reporting

Avoid:

```text
PowerUp found privilege escalation.
```

Prefer:

```text
The tested standard user had Modify permission over an executable
configured to run as part of a LocalSystem service. Native service and
filesystem permission checks confirmed that the low-privileged user
could influence a privileged execution path.
```

PowerUp may have identified the candidate, but the finding describes the underlying condition.

---

# Reporting an Unconfirmed Candidate

Example:

```text
PowerUp identified an unquoted service path. Manual validation showed
that the service ran as LocalSystem, but all candidate path locations
were protected from modification by the tested user. A practical local
privilege escalation path was therefore not confirmed.
```

This is more accurate than reporting every PowerUp warning.

---

# Reporting a Defence-in-Depth Condition

Example:

```text
A privileged service referenced a file located in a directory with weak
write permissions. However, execution from the affected location was
restricted by application-control policy during testing. The underlying
filesystem permission should still be corrected because application
control represents a separate defence-in-depth layer.
```

This preserves both facts.

---

# Remediation Principles

PowerUp findings commonly map to a simple principle:

> Standard users should not be able to modify resources that determine how privileged processes execute.

Remediation areas include:

- service ACLs;
- service executable ACLs;
- directory ACLs;
- service paths;
- registry policy;
- autologon credentials;
- PATH;
- DLL loading locations.

---

# Service Remediation

Typical measures include:

- remove unnecessary Modify/Write access;
- restrict service configuration rights;
- use least-privileged service identities;
- protect service directories;
- quote executable paths where applicable.

---

# AlwaysInstallElevated Remediation

Disable unsafe installer policy where it is not specifically required.

Enterprise policy should be managed centrally through appropriate administrative controls.

---

# Autologon Remediation

Where plaintext credentials are exposed:

- remove unnecessary autologon;
- avoid storing reusable plaintext secrets;
- rotate exposed credentials;
- apply least privilege to the account.

---

# PATH Remediation

Typical measures include:

- remove insecure writable directories from privileged PATH contexts;
- use absolute executable paths in privileged automation;
- correct directory permissions.

---

# DLL Remediation

Typical measures include:

- use explicit library paths;
- secure application directories;
- remove writable search locations;
- use appropriate application-control and code-integrity protections.

---

# Retesting

Do not retest only by running:

```powershell
Invoke-AllChecks
```

again.

For a service ACL fix, confirm:

```powershell
icacls "C:\Path\To\Service.exe"
```

and:

```powershell
sc.exe qc ExampleService
```

For installer policy, confirm the relevant registry values.

For a PATH issue, confirm:

```powershell
$env:Path -split ';'
```

and directory ACLs.

Then optionally rerun PowerUp as a secondary regression check.

---

# PowerUp in Purple Teaming

PowerUp execution can also generate useful telemetry during purple-team exercises.

Conceptually:

```text
PowerUp
   |
   v
Privilege Escalation Enumeration
   |
   v
PowerShell / Process / EDR Telemetry
   |
   v
Detection Review
```

Related notes:

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

The exercise objective should be agreed before execution.

---

# Logging and Telemetry

PowerUp may generate observable activity through:

- PowerShell script loading;
- registry queries;
- service enumeration;
- filesystem ACL inspection;
- process activity.

This may be expected in an authorised assessment.

Do not attempt to evade logging merely to make the tool execute unless that is explicitly part of the engagement objective.

---

# Tool Transfer

Document transferred security tooling where appropriate.

Example:

```text
Tool:
PowerUp.ps1

Source:
Official PowerSploit repository

Destination:
Approved temporary working directory

Execution:
Authorised

Cleanup:
Completed after testing
```

---

# Cleanup

Where required, remove:

```text
PowerUp.ps1
powerup-output.txt
temporary assessment artefacts
```

Do not delete legitimate Windows event logs or security telemetry.

Retain assessment evidence according to policy.

---

# Practical PowerUp Workflow

A strong workflow is:

```text
1. Confirm scope
      |
      v
2. Record current user
      |
      v
3. Record groups and privileges
      |
      v
4. Check PowerShell environment
      |
      v
5. Obtain official PowerUp
      |
      v
6. Review script/version
      |
      v
7. Load PowerUp
      |
      v
8. Run enumeration checks
      |
      v
9. Save output securely
      |
      v
10. Prioritise service and permission findings
      |
      v
11. Validate with native Windows tools
      |
      v
12. Identify privileged consumer
      |
      v
13. Confirm trigger
      |
      v
14. Consider AppLocker/WDAC/EDR
      |
      v
15. Confirm or reject candidate
      |
      v
16. Capture evidence
      |
      v
17. Clean up assessment artefacts
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

## PowerShell Version

```powershell
$PSVersionTable
```

## Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

## Execution Policy

```powershell
Get-ExecutionPolicy -List
```

## Import Local PowerUp

```powershell
Import-Module .\PowerUp.ps1
```

## Dot-Source Local PowerUp

```powershell
. .\PowerUp.ps1
```

## Run Main Checks

```powershell
Invoke-AllChecks
```

## Save Results

```powershell
Invoke-AllChecks | Tee-Object -FilePath .\powerup-output.txt
```

## Help

```powershell
Get-Help Invoke-AllChecks -Full
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

## Registry Query

```powershell
reg.exe query "HKLM\Software\Example"
```

## PATH

```powershell
$env:Path -split ';'
```

---

# PowerUp Checklist

## Preparation

- [ ] Target system explicitly authorised.
- [ ] Current user recorded.
- [ ] Groups recorded.
- [ ] Privileges recorded.
- [ ] PowerShell version known.
- [ ] Language mode checked.
- [ ] Execution policy understood.
- [ ] AppLocker/WDAC context considered.
- [ ] Official PowerSploit source used.
- [ ] Script provenance recorded where useful.

## Execution

- [ ] Script reviewed before loading.
- [ ] Enumeration functions preferred first.
- [ ] State-changing functions not used automatically.
- [ ] Output retained securely.
- [ ] Sensitive data protected.

## Services

- [ ] Service account confirmed.
- [ ] Binary path confirmed.
- [ ] File ACL confirmed.
- [ ] Parent directory ACL confirmed.
- [ ] Service object permissions considered.
- [ ] Restart/trigger condition reviewed.
- [ ] Unquoted path candidates manually validated.

## Registry

- [ ] Interesting registry values confirmed manually.
- [ ] Installer policy evaluated in full context.
- [ ] Autologon findings validated.
- [ ] Sensitive registry data protected.

## Filesystem

- [ ] Writable files manually checked.
- [ ] Writable directories manually checked.
- [ ] Effective permissions understood.
- [ ] Privileged consumer identified.

## PATH / DLL

- [ ] Writable PATH entries treated as candidates only.
- [ ] Privileged PATH consumer confirmed.
- [ ] DLL loading behaviour understood.
- [ ] Search path and writable locations validated.
- [ ] Application-control restrictions considered.

## Security Controls

- [ ] Defender considered.
- [ ] EDR considered.
- [ ] AppLocker considered.
- [ ] WDAC considered.
- [ ] Constrained Language Mode considered.

## Validation

- [ ] PowerUp result treated as candidate evidence.
- [ ] Native commands used for confirmation.
- [ ] Effective user influence confirmed.
- [ ] Privileged execution context confirmed.
- [ ] Trigger confirmed.
- [ ] False positives considered.
- [ ] Security impact established.

## Evidence

- [ ] Current identity retained.
- [ ] Relevant PowerUp output retained.
- [ ] Native ACL/configuration evidence retained.
- [ ] Privileged consumer documented.
- [ ] Trigger documented.
- [ ] Security-control context documented.
- [ ] Sensitive values redacted where required.
- [ ] Finding describes underlying security weakness.

## Cleanup

- [ ] PowerUp script removed where required.
- [ ] Temporary output removed where required.
- [ ] Evidence retained according to policy.
- [ ] Legitimate Windows/security logs preserved.

---

# Related Tool Notes

[Privilege Escalation Tools](index.md)

[WinPEAS](winpeas.md)

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

## PowerUp

[PowerUp - PowerSploit](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc){ target="_blank" rel="noopener noreferrer" }

[PowerSploit - GitHub](https://github.com/PowerShellMafia/PowerSploit){ target="_blank" rel="noopener noreferrer" }

## Supporting Windows References

[Microsoft - icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls){ target="_blank" rel="noopener noreferrer" }

[Microsoft - sc.exe query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-query){ target="_blank" rel="noopener noreferrer" }

[Microsoft - schtasks query](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-query){ target="_blank" rel="noopener noreferrer" }

[Microsoft - about_Language_Modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }

## Practical Reference

[HackTricks - Windows Local Privilege Escalation](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use PowerUp like this:

```text
Load PowerUp
    |
    v
Invoke-AllChecks
    |
    v
Copy Findings
    |
    v
Report PrivEsc
```

Use it like this:

```text
Understand Current Identity
        |
        v
Load Trusted PowerUp Copy
        |
        v
Run Enumeration
        |
        v
Identify Candidate
        |
        v
Understand the Check
        |
        v
Validate With Native Tools
        |
        +-- sc.exe
        +-- icacls.exe
        +-- reg.exe
        +-- schtasks.exe
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
Consider AppLocker / WDAC / EDR
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

PowerUp remains useful because it automates a number of important Windows local privilege escalation checks in a readable PowerShell implementation.

Its greatest value is not automatically exploiting the host.

Its value is identifying configurations that deserve careful, native Windows validation.
