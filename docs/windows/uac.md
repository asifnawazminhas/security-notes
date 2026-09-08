---
title: Windows User Account Control
description: Practical Windows User Account Control assessment covering integrity levels, elevation, consent behavior, token filtering, UAC configuration, auto-elevation exposure, privileged execution, evidence collection, remediation and retesting.
---

# Windows User Account Control

User Account Control - UAC - is a Windows security feature designed to reduce unnecessary administrative execution and make elevation to higher privileges explicit.

UAC is particularly relevant when assessing systems where the current account is:

```text
Member of the local Administrators group
```

but the current process is running with a filtered token.

A Windows security assessment should determine:

```text
Is UAC enabled?

What integrity level is the current process using?

Is the current user a local administrator?

Is the process elevated?

Which UAC level is configured?

How are administrator elevation prompts handled?

How are standard-user elevation prompts handled?

Is the secure desktop used?

Are installer detection and virtualization enabled?

Is the built-in Administrator treated differently?

Are remote administrative tokens filtered?

Does the observed runtime behavior match the intended policy?
```

!!! warning "Authorised Security Testing"

    Perform UAC testing only on Windows systems included in the authorised assessment scope. Prefer configuration inspection, token analysis and harmless elevation validation. Do not weaken UAC, alter enterprise policy or change consent behavior merely to demonstrate that the control can be modified.


# What UAC Does

A simplified model is:

```text
User Logs In
     |
     v
Administrative Account?
     |
  +--+--+
  |     |
 No    Yes
  |     |
  v     v
Standard   Split Token
Token       |
            +----------------+
            |                |
            v                v
      Filtered Token    Elevated Token
            |                |
            v                v
      Normal Desktop    Administrative
                         Operation
```

For many administrator accounts, Windows creates:

```text
Filtered token
+
Full administrator token
```

The normal desktop typically operates using the filtered token until elevation is approved.


# UAC Is Not a Privilege Boundary

This distinction is important.

Microsoft does not position UAC as a security boundary between processes belonging to the same interactive administrative user.

Therefore:

```text
UAC behavior
```

should not automatically be reported as:

```text
Privilege escalation vulnerability
```

without establishing the actual trust boundary and security impact.


# UAC Security Objectives

UAC helps:

```text
Reduce routine administrative execution

Make privileged actions visible

Separate normal and elevated process contexts

Encourage applications to operate without administrative rights

Reduce accidental system-wide modification
```


# UAC Does Not Replace

UAC does not replace:

```text
Least privilege

Application control

Endpoint protection

Secure filesystem permissions

Secure service permissions

Patch management

Credential protection
```


# Assessment Model

Use:

```text
IDENTIFY USER
      |
      v
CHECK ADMIN MEMBERSHIP
      |
      v
CHECK TOKEN
      |
      v
CHECK INTEGRITY LEVEL
      |
      v
CHECK UAC CONFIGURATION
      |
      v
CHECK CONSENT POLICY
      |
      v
CHECK SECURE DESKTOP
      |
      v
CHECK REMOTE TOKEN FILTERING
      |
      v
VALIDATE EXPECTED BEHAVIOUR
      |
      v
INTERPRET
      |
      v
REPORT
      |
      v
RETEST
```


# Establish Current Identity

Start with:

```cmd
whoami
```


# User SID

```cmd
whoami /user
```


# Group Membership

```cmd
whoami /groups
```


# Privileges

```cmd
whoami /priv
```


# Why This Matters

Before analysing UAC, establish whether the account is:

```text
Standard user

Local administrator

Domain administrator

Built-in Administrator

Another privileged identity
```


# Local Administrators Group

PowerShell:

```powershell
Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue
```


# Alternative

```cmd
net localgroup administrators
```


# Domain Considerations

A domain account may obtain local administrative privileges through:

```text
Direct local group membership

Nested domain groups

Group Policy

Endpoint management

Privileged workstation policy
```

Therefore do not rely solely on the username.


# Token vs Group Membership

Being a member of:

```text
BUILTIN\Administrators
```

does not necessarily mean the current process is elevated.


# Split Token Model

An administrator may have:

```text
Administrator account
       |
       +--> Filtered token
       |
       +--> Full administrator token
```


# Current Process Integrity Level

A convenient check is:

```cmd
whoami /groups
```

Look for a mandatory integrity label such as:

```text
Mandatory Label\Medium Mandatory Level
```

or:

```text
Mandatory Label\High Mandatory Level
```


# Common Integrity Levels

Windows integrity levels commonly include:

```text
Low

Medium

High

System
```


# Simplified Interpretation

| Integrity Level | Typical Context |
|---|---|
| Low | Restricted/sandboxed process |
| Medium | Normal interactive user process |
| High | Elevated administrator process |
| System | Highly privileged system service/process |


# Important

Integrity level and user identity are related but different security concepts.

A process can run as an account that belongs to Administrators while the process itself remains at:

```text
Medium Integrity
```


# Check Integrity Label

```powershell
whoami /groups | Select-String 'Mandatory'
```


# Example

```text
Mandatory Label\Medium Mandatory Level
```


# Interpretation

For a local administrator, this commonly indicates that the current process is using the filtered token rather than the elevated administrator token.


# Elevated PowerShell

An elevated administrative PowerShell session commonly shows:

```text
Mandatory Label\High Mandatory Level
```


# Administrative Token Check

A useful PowerShell test is:

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)

$principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)
```


# Example

```text
True
```

This evaluates whether the current token has the Administrator role enabled.


# Compact Token Summary

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)

[PSCustomObject]@{
    User          = $identity.Name
    IsAdminToken  = $principal.IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
}
```


# Determine UAC Configuration

Core UAC policy is stored under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
```


# Query All UAC Settings

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
```


# PowerShell

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
```


# Important Values

Common UAC-related values include:

```text
EnableLUA

ConsentPromptBehaviorAdmin

ConsentPromptBehaviorUser

PromptOnSecureDesktop

FilterAdministratorToken

EnableInstallerDetection

EnableVirtualization

ValidateAdminCodeSignatures

EnableSecureUIAPaths
```


# Focused UAC Summary

```powershell
$uac = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'

[PSCustomObject]@{
    EnableLUA                  = $uac.EnableLUA
    ConsentPromptBehaviorAdmin = $uac.ConsentPromptBehaviorAdmin
    ConsentPromptBehaviorUser  = $uac.ConsentPromptBehaviorUser
    PromptOnSecureDesktop      = $uac.PromptOnSecureDesktop
    FilterAdministratorToken   = $uac.FilterAdministratorToken
    EnableInstallerDetection   = $uac.EnableInstallerDetection
    EnableVirtualization       = $uac.EnableVirtualization
    ValidateAdminCodeSignatures = $uac.ValidateAdminCodeSignatures
    EnableSecureUIAPaths       = $uac.EnableSecureUIAPaths
}
```


# EnableLUA

One of the most important values is:

```text
EnableLUA
```


# Query

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').EnableLUA
```


# Typical Values

```text
1 = UAC enabled

0 = UAC disabled
```


# Important

Disabling `EnableLUA` affects more than the appearance of elevation prompts.

It changes important Windows security and application behavior.


# Assessment

If:

```text
EnableLUA = 0
```

determine:

```text
Why UAC is disabled

Whether enterprise policy requires UAC

Which users have local administrator rights

Whether compensating controls exist
```


# Administrator Consent Behavior

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').ConsentPromptBehaviorAdmin
```


# Why It Matters

This value controls how elevation requests are handled for administrators operating in Admin Approval Mode.


# Possible Behaviors

Depending on configuration and Windows version, policies can represent behaviors such as:

```text
Elevate without prompting

Prompt for credentials

Prompt for consent

Prompt for credentials on secure desktop

Prompt for consent on secure desktop

Prompt for consent for non-Windows binaries
```


# Important

When documenting the setting, record:

```text
Numeric value

Resolved policy meaning

Windows version

Observed runtime behavior
```

Do not rely solely on a memorised numeric value when producing formal evidence.


# Standard User Consent Behavior

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').ConsentPromptBehaviorUser
```


# Standard User Model

A standard user normally requires administrative credentials for operations requiring elevation.


# Security Question

Determine whether the endpoint:

```text
Prompts for credentials

Automatically denies elevation requests

Uses another enterprise workflow
```


# Secure Desktop

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').PromptOnSecureDesktop
```


# Typical Values

```text
1 = Elevation prompt uses secure desktop

0 = Prompt appears on interactive desktop
```


# Secure Desktop Model

```text
Normal Desktop
      |
      v
Elevation Requested
      |
      v
Secure Desktop
      |
      v
Consent / Credentials
      |
      v
Elevated Process
```


# Why Secure Desktop Matters

The secure desktop isolates the elevation prompt from ordinary user applications, reducing the ability of normal desktop processes to interact with the prompt.


# Admin Approval Mode for Built-In Administrator

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').FilterAdministratorToken
```


# Security Purpose

This setting controls Admin Approval Mode behavior for the built-in Administrator account.


# Built-In Administrator

The built-in Administrator account can behave differently from other accounts in the local Administrators group.

Therefore establish whether the tested account is actually the built-in Administrator.


# Current SID

```cmd
whoami /user
```


# Local Built-In Administrator SID

The built-in Administrator account has a SID ending in:

```text
-500
```


# Important

The account may have been renamed.

Therefore identify it by SID rather than assuming the account is literally named:

```text
Administrator
```


# Find Local Administrator Account

```powershell
Get-LocalUser |
    Where-Object { $_.SID.Value -match '-500$' } |
    Select-Object Name,Enabled,SID
```


# Installer Detection

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').EnableInstallerDetection
```


# Purpose

Installer detection helps Windows identify certain installer applications that may require elevation.


# Important

Installer detection is not an application-control boundary.

It should not be confused with:

```text
AppLocker

WDAC

MSI policy
```


# UAC Virtualization

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').EnableVirtualization
```


# Purpose

UAC virtualization can redirect certain legacy application writes from protected locations to per-user locations.


# Conceptual Example

A legacy application attempts to write to:

```text
C:\Program Files\LegacyApp\config.ini
```

Windows may redirect compatible writes to a user-specific virtualized location rather than granting administrative write access.


# Important

UAC virtualization is primarily an application compatibility mechanism.

Do not treat it as a substitute for correct filesystem permissions.


# Signed Elevation

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').ValidateAdminCodeSignatures
```


# Security Purpose

This policy can require executables requesting elevation to be signed by a trusted publisher.


# Important

The organisation must evaluate compatibility before enabling strict signed-elevation requirements.


# UIAccess Security

Check:

```powershell
(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').EnableSecureUIAPaths
```


# UIAccess

Windows includes special handling for accessibility applications that require interaction with higher-integrity user interfaces.


# Assessment Principle

UIAccess-related configuration should remain aligned with Microsoft security guidance and enterprise requirements.


# UAC Policy Through Local Security Policy

UAC settings are also represented through security policy interfaces such as:

```text
Local Security Policy
    |
    v
Local Policies
    |
    v
Security Options
```


# Common Policy Names

You may encounter policies beginning with:

```text
User Account Control:
```

Examples include:

```text
Run all administrators in Admin Approval Mode

Behavior of the elevation prompt for administrators

Behavior of the elevation prompt for standard users

Switch to the secure desktop when prompting for elevation

Detect application installations and prompt for elevation

Virtualize file and registry write failures

Admin Approval Mode for the Built-in Administrator account
```


# Group Policy

Enterprise environments may centrally configure UAC using Group Policy.


# Resultant Policy

Useful commands include:

```cmd
gpresult /r
```


# HTML Report

Where permitted:

```cmd
gpresult /h "%TEMP%\gpresult.html"
```


# PowerShell

```powershell
gpresult /r
```


# Important

Local Registry state may be the result of:

```text
Local policy

Domain Group Policy

MDM

Security baseline
```

Determine the authoritative management source before recommending local changes.


# UAC Notification Level

Windows exposes familiar Control Panel notification levels such as:

```text
Always notify

Notify only when apps try to make changes

Notify only when apps try to make changes without secure desktop

Never notify
```

These user-facing levels correspond to combinations of underlying policy settings.


# Important

For assessment reporting, prefer the underlying effective policy values rather than relying only on the slider position.


# Token Inspection

Understanding the token is central to UAC analysis.


# Full Identity Information

```cmd
whoami /all
```


# This Includes

```text
User information

Group membership

Privileges

Integrity label
```


# Privilege State

```cmd
whoami /priv
```


# Example Privileges

An elevated administrator token may expose additional privileges compared with a filtered medium-integrity token.


# Important

Do not determine elevation from one privilege alone.

Use multiple signals:

```text
Group membership

Integrity level

Administrator role

Process context
```


# Process Integrity

PowerShell can inspect the current process:

```powershell
Get-Process -Id $PID |
    Select-Object Id,ProcessName,Path
```


# Parent Process

Where available:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId=$PID" |
    Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine
```


# Why Parentage Matters

During testing, knowing whether PowerShell was started from:

```text
Explorer

Windows Terminal

cmd.exe

Another administrative console
```

can help explain the current token context.


# Harmless Elevation Validation

A simple manual validation is to launch a legitimate administrative Windows utility that requires elevation and observe the expected UAC behavior.

The objective is to establish:

```text
Was elevation requested?

Was consent required?

Were credentials required?

Was the secure desktop used?

Did the resulting process run elevated?
```


# Do Not Modify Security Settings

The validation does not require actually changing the protected setting.


# Start-Process RunAs

PowerShell provides the normal Windows elevation mechanism:

```powershell
Start-Process powershell.exe -Verb RunAs
```


# Expected Behavior

Depending on policy and user type:

```text
Consent prompt

Credential prompt

Automatic denial

Elevation according to configured policy
```


# Important

This is a normal Windows elevation request, not a UAC bypass.


# Elevated Validation

Inside the newly elevated PowerShell session:

```cmd
whoami /groups
```


# Expected

An administrator session will typically show:

```text
Mandatory Label\High Mandatory Level
```


# Compare Tokens

Before elevation:

```cmd
whoami /all
```

After elevation:

```cmd
whoami /all
```


# Evidence

Capture the differences in:

```text
Integrity level

Enabled groups

Privileges
```


# Standard User Test

For a standard user, an elevation request may result in:

```text
Credential prompt
```

or:

```text
Automatic denial
```

depending on policy.


# Do Not Supply Unauthorised Credentials

During an assessment, do not use administrative credentials unless explicitly provided and authorised for the test.


# UAC and Local Administrators

Local administrator membership is a high-value endpoint security consideration.


# Enumerate Administrators

```powershell
Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue
```


# Questions

Ask:

```text
Which users are local administrators?

Which domain groups are included?

Are privileges required?

Are administrative accounts separated from normal accounts?

Is UAC enforced for those accounts?
```


# Least Privilege

UAC should not be used as justification for giving ordinary users local administrator rights.


# Weak Model

```text
User is Local Administrator
        +
UAC Prompt
        =
Least Privilege
```

This is incorrect.


# Stronger Model

```text
Standard User
      +
Separate Administrative Identity
      +
UAC
      +
Application Control
      +
Endpoint Protection
```


# UAC and Application Control

Application control answers:

```text
Should this application be allowed to execute?
```

UAC answers:

```text
Should this operation execute with administrative privileges?
```


# Combined Model

```text
Application
    |
    v
AppLocker / WDAC
    |
Allowed?
    |
    v
Normal Execution
    |
Requires Admin?
    |
    v
UAC
    |
    v
Elevation Decision
```


# Related Note

See:

[Windows Application Control](application-control.md)


# UAC and Defender

Microsoft Defender provides another independent layer.

```text
Application
    |
    +--> Application Control
    |
    +--> Defender / EDR
    |
    +--> UAC
    |
    v
Runtime Security Decision
```


# Related Note

See:

[Microsoft Defender Security Assessment](defender.md)


# UAC and Filesystem Permissions

A high-integrity process can modify resources that a medium-integrity process normally cannot.

However, insecure filesystem ACLs may allow a medium-integrity user to modify sensitive resources without elevation.


# Security Question

If a standard user can modify:

```text
C:\Program Files\Vendor\Service.exe
```

the root problem is not:

```text
UAC
```

It is likely:

```text
Filesystem permissions
```

possibly combined with a privileged execution path.


# Related Note

See:

[Windows Filesystem Permissions](filesystem-permissions.md)


# UAC and Services

Windows services frequently execute with privileged identities such as:

```text
LocalSystem

LocalService

NetworkService

Service accounts
```

UAC does not protect insecure service configuration from a user who already has permission to modify the relevant service resource.


# Related Note

See:

[Windows Services](services.md)


# UAC and Scheduled Tasks

Scheduled tasks can be configured to run:

```text
Only when user is logged on

Whether user is logged on or not

With highest privileges
```

A task running with highest privileges represents a privileged execution path that must be protected independently of UAC.


# Related Note

See:

[Windows Scheduled Tasks](scheduled-tasks.md)


# UAC and Registry Permissions

Insecure Registry permissions can create privileged modification paths independently of UAC.

Review:

[Windows Registry Security](registry.md)


# Remote UAC Restrictions

Windows applies additional UAC-related behavior to some remote administrative connections.


# LocalAccountTokenFilterPolicy

A relevant Registry value is:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy
```


# Query

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v LocalAccountTokenFilterPolicy
```


# PowerShell

```powershell
Get-ItemPropertyValue `
    -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' `
    -Name 'LocalAccountTokenFilterPolicy' `
    -ErrorAction SilentlyContinue
```


# Security Purpose

Remote UAC restrictions can filter administrative tokens for local accounts connecting remotely.


# Important

Do not change this value during assessment merely to enable remote administrative behavior.


# Domain Accounts

Remote token filtering behavior differs depending on:

```text
Local account

Domain account

Group membership

Administrative share access

Remote management technology

Enterprise policy
```


# Assessment Principle

When remote administration behaves differently from local administration, investigate token filtering before assuming:

```text
Credentials are invalid
```

or:

```text
The service is broken
```


# Built-In Administrator and Remote Access

The built-in Administrator account can have special behavior depending on:

```text
Admin Approval Mode

Remote UAC restrictions

Local security policy
```


# UAC and Network Logons

UAC primarily concerns interactive administrative elevation.

Network logons and remote administrative access involve additional Windows authentication and token rules.


# Do Not Conflate

```text
UAC

NTLM

Kerberos

WinRM

SMB

Remote Desktop

Remote token filtering
```

are related in some scenarios but are distinct mechanisms.


# Auto-Elevation

Windows includes trusted components that can support elevation behavior as part of normal operating system functionality.


# Security Assessment

The useful questions are:

```text
Is UAC configured according to the security baseline?

Are users unnecessarily local administrators?

Are privileged execution paths protected?

Are trusted Windows components intact?

Is application control configured?

Are endpoint protections operational?
```


# Important

Do not build an assessment around collecting arbitrary UAC bypass techniques.

A more durable security assessment evaluates the underlying security architecture.


# UAC Bypass Classification

When a UAC-related technique is discussed during a penetration test, classify it correctly.

A typical UAC elevation scenario assumes:

```text
User already belongs to Administrators
        |
        v
Current process is Medium Integrity
        |
        v
Technique obtains High Integrity
```

This is different from:

```text
Standard User
        |
        v
Local Administrator
```

The second case crosses a stronger privilege boundary.


# Reporting Consequence

Do not report:

```text
Standard user privilege escalation
```

when the tested account was already a member of:

```text
Administrators
```


# Integrity Transition

The actual transition may be:

```text
Administrator
Medium Integrity
       |
       v
Administrator
High Integrity
```


# Why This Distinction Matters

It affects:

```text
Severity

Impact

Root cause

Remediation

Executive reporting
```


# UAC and Credential Theft

UAC elevation can expose administrative operations, but UAC should not be treated as the primary credential-protection mechanism.

Credential security should be evaluated separately.

See:

[Windows Credentials](credentials.md)


# UAC and Process Elevation

Processes started from an elevated parent can inherit an elevated context depending on how they are launched.


# Assessment Example

```text
Elevated PowerShell
       |
       v
Launch cmd.exe
       |
       v
High Integrity cmd.exe
```

Therefore always establish the current shell context before interpreting command results.


# Windows Terminal

A Windows Terminal session may contain shells running under different privilege contexts.

Do not assume:

```text
Windows Terminal
```

itself tells you whether the active shell is elevated.


# Check Every Relevant Shell

Use:

```cmd
whoami /groups
```

inside the actual shell being tested.


# Process Explorer

Administrative tools such as Microsoft Sysinternals Process Explorer can also help inspect:

```text
Integrity levels

Process tokens

Parent-child relationships

User identities
```

when GUI tooling is available and permitted.


# UAC Virtualization Status

For legacy application troubleshooting and assessment, virtualization state may be relevant.

A modern application with an appropriate manifest normally should not depend on UAC virtualization for secure operation.


# Application Manifests

Windows executables can declare requested execution levels such as:

```text
asInvoker

highestAvailable

requireAdministrator
```


# Security Meaning

## asInvoker

The application runs using the caller's current token.


## highestAvailable

The application requests the highest privilege level available to the user.


## requireAdministrator

The application requests administrative elevation.


# Important

An application requesting:

```text
requireAdministrator
```

is not automatically vulnerable.

Determine whether administrative privileges are genuinely required.


# Excessive Administrative Requirements

An application that unnecessarily requires administrative privileges can increase security risk.


# Assessment Questions

Ask:

```text
Why does the application require elevation?

Can it function as standard user?

Which protected resources does it need?

Can permissions be redesigned?

Does every user need the elevated functionality?
```


# Potential Finding

```text
Application Requires Unnecessary Administrative Privileges
```


# Security Impact

Unnecessary elevation increases the amount of code executing with administrative rights and can increase the impact of application vulnerabilities.


# UAC and Software Installation

Software installation frequently requires elevation because installers may modify:

```text
Program Files

HKLM

Windows services

Drivers

System-wide configuration
```


# Assessment Principle

Do not weaken UAC simply because an installer requires administrative access.

Use appropriate software deployment mechanisms.


# Enterprise Deployment

Managed environments may install applications through:

```text
Intune

Configuration Manager

Group Policy

Enterprise software deployment platforms
```

without granting permanent local administrator rights to end users.


# UAC Configuration Collection Script

The following read-only script collects useful UAC posture information.

```powershell
Write-Host "===================================="
Write-Host " WINDOWS UAC SECURITY ASSESSMENT"
Write-Host "===================================="

Write-Host "`n=== CURRENT USER ==="
whoami

Write-Host "`n=== USER SID ==="
whoami /user

Write-Host "`n=== GROUP MEMBERSHIP ==="
whoami /groups

Write-Host "`n=== PRIVILEGES ==="
whoami /priv

Write-Host "`n=== TOKEN ADMINISTRATOR STATUS ==="

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)

[PSCustomObject]@{
    User = $identity.Name
    IsAdministratorToken = $principal.IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
} | Format-List

Write-Host "`n=== UAC CONFIGURATION ==="

$policyPath = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
$uac = Get-ItemProperty $policyPath -ErrorAction SilentlyContinue

if ($uac) {
    [PSCustomObject]@{
        EnableLUA                   = $uac.EnableLUA
        ConsentPromptBehaviorAdmin  = $uac.ConsentPromptBehaviorAdmin
        ConsentPromptBehaviorUser   = $uac.ConsentPromptBehaviorUser
        PromptOnSecureDesktop       = $uac.PromptOnSecureDesktop
        FilterAdministratorToken    = $uac.FilterAdministratorToken
        EnableInstallerDetection    = $uac.EnableInstallerDetection
        EnableVirtualization        = $uac.EnableVirtualization
        ValidateAdminCodeSignatures = $uac.ValidateAdminCodeSignatures
        EnableSecureUIAPaths        = $uac.EnableSecureUIAPaths
        LocalAccountTokenFilterPolicy = $uac.LocalAccountTokenFilterPolicy
    } | Format-List
}
else {
    Write-Host "Unable to retrieve UAC policy configuration."
}

Write-Host "`n=== BUILT-IN ADMINISTRATOR ==="

Get-LocalUser -ErrorAction SilentlyContinue |
    Where-Object { $_.SID.Value -match '-500$' } |
    Select-Object Name,Enabled,SID |
    Format-Table -AutoSize

Write-Host "`n=== LOCAL ADMINISTRATORS ==="

Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue |
    Select-Object Name,ObjectClass,PrincipalSource |
    Format-Table -AutoSize

Write-Host "`n=== POWERHELL LANGUAGE MODE ==="
$ExecutionContext.SessionState.LanguageMode

Write-Host "`n=== APPLICATION CONTROL ==="

try {
    [xml]$appLocker = Get-AppLockerPolicy -Effective -Xml -ErrorAction Stop

    $appLocker.AppLockerPolicy.RuleCollection |
        Select-Object Type,EnforcementMode |
        Format-Table -AutoSize
}
catch {
    Write-Host "Unable to retrieve effective AppLocker policy."
}

Write-Host "`n=== DEFENDER STATUS ==="

Get-MpComputerStatus -ErrorAction SilentlyContinue |
    Select-Object AntivirusEnabled,
                  RealTimeProtectionEnabled,
                  BehaviorMonitorEnabled,
                  IsTamperProtected |
    Format-List

Write-Host "`n=== COMPLETE ==="
```


# Script Purpose

The script collects:

```text
Current identity

SID

Groups

Privileges

Administrator-token status

UAC policy

Built-in Administrator state

Local Administrators membership

Remote token-filtering configuration

PowerShell language mode

AppLocker context

Defender context
```


# Script Safety

The script does not:

```text
Change UAC

Trigger elevation

Modify Registry settings

Disable Defender

Modify AppLocker

Create persistence

Change local group membership
```


# Note

The heading in the script:

```text
POWERHELL LANGUAGE MODE
```

can be changed to:

```text
POWERSHELL LANGUAGE MODE
```

if you want the output heading perfectly spelled.

The functional PowerShell command itself is unaffected.


# Practical Validation

## When This Applies

Use this methodology when:

```text
Assessing Windows endpoints

Reviewing local administrator exposure

Testing workstation hardening

Reviewing Windows privilege boundaries

Validating security baselines

Investigating administrative execution
```


# Prerequisites

Record:

```text
Windows version

User identity

Local administrator membership

Domain membership

Management architecture

Assessment authorization
```


# Procedure

## Step 1 - Identify User

```cmd
whoami
```


## Step 2 - Identify Groups

```cmd
whoami /groups
```


## Step 3 - Identify Privileges

```cmd
whoami /priv
```


## Step 4 - Determine Integrity

```powershell
whoami /groups | Select-String 'Mandatory'
```


## Step 5 - Determine Administrator Token

```powershell
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)

$principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)
```


## Step 6 - Retrieve UAC Configuration

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
```


## Step 7 - Identify Local Administrators

```powershell
Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue
```


## Step 8 - Identify Built-In Administrator

```powershell
Get-LocalUser |
    Where-Object { $_.SID.Value -match '-500$' } |
    Select-Object Name,Enabled,SID
```


## Step 9 - Check Remote Token Filtering

```powershell
Get-ItemPropertyValue `
    -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' `
    -Name 'LocalAccountTokenFilterPolicy' `
    -ErrorAction SilentlyContinue
```


## Step 10 - Validate Normal Elevation

Where permitted:

```powershell
Start-Process powershell.exe -Verb RunAs
```

Observe the normal Windows elevation workflow.


# Representative Result

Example:

```text
Current account:
CORP\User1

Local Administrators:
Yes

Current integrity:
Medium

Administrator token enabled:
False

EnableLUA:
1

PromptOnSecureDesktop:
1
```


# Interpretation

This supports a conclusion similar to:

> The tested account belongs to the local Administrators group but the current interactive process is operating at medium integrity under a filtered token. UAC is enabled and elevation requests are configured to use the secure desktop.


# Positive Security Result

A hardened representative configuration may include:

```text
UAC enabled

Administrative accounts operate using Admin Approval Mode

Elevation requires appropriate consent or credentials

Secure desktop enabled

Standard users cannot silently elevate

Built-in Administrator appropriately controlled

Local administrator membership restricted

Remote token filtering configured appropriately
```


# Negative Security Result

Further review may be required where:

```text
UAC is disabled

Administrators elevate without prompting contrary to baseline

Secure desktop is disabled contrary to baseline

Users unnecessarily hold local administrator rights

Built-in Administrator configuration is weak

Remote administrative token filtering has been weakened without justification
```


# Alternative Explanations

Before reporting, consider:

```text
Kiosk endpoint

Server role

Dedicated administrative workstation

Application compatibility requirement

Enterprise management tooling

Legacy system requirement

Alternative privileged access controls
```


# Evidence to Capture

Capture:

```text
Hostname

Windows version

Current user

User SID

Local administrator membership

Current integrity level

Administrator-token state

EnableLUA

ConsentPromptBehaviorAdmin

ConsentPromptBehaviorUser

PromptOnSecureDesktop

FilterAdministratorToken

LocalAccountTokenFilterPolicy

Relevant Group Policy

Observed elevation behavior
```


# Evidence Table

| Evidence | Purpose |
|---|---|
| `whoami` | Current identity |
| `whoami /user` | User SID |
| `whoami /groups` | Groups and integrity level |
| `whoami /priv` | Token privileges |
| Administrator-role test | Current token elevation |
| `EnableLUA` | UAC status |
| `ConsentPromptBehaviorAdmin` | Administrator prompt behavior |
| `ConsentPromptBehaviorUser` | Standard-user behavior |
| `PromptOnSecureDesktop` | Secure desktop status |
| `FilterAdministratorToken` | Built-in Administrator behavior |
| `LocalAccountTokenFilterPolicy` | Remote token filtering |
| `gpresult` | Policy management context |


# Finding - UAC Disabled

## Observation

```text
EnableLUA:
0
```


# Further Validation

Determine:

```text
Is this required for a legacy workload?

Is the endpoint a workstation or server?

Which users have administrator rights?

Is the setting centrally managed?

Does the security baseline require UAC?
```


# Possible Finding Title

```text
User Account Control Is Disabled
```


# Reporting Conclusion

Example:

> User Account Control is disabled on the tested Windows endpoint. As a result, the normal Admin Approval Mode protections and elevation workflow are not applied to administrative users. The configuration should be reviewed against the organisation's Windows security baseline.


# Finding - Elevation Without Prompt

If effective policy permits administrator elevation without prompting and this conflicts with the intended baseline:

```text
Administrator Elevation Does Not Require User Consent
```


# Impact

This reduces the visibility and explicit user interaction normally associated with administrative elevation.


# Important

Do not describe this automatically as:

```text
Standard-user-to-SYSTEM privilege escalation
```

The tested user may already be an administrator.


# Finding - Secure Desktop Disabled

Observation:

```text
PromptOnSecureDesktop:
0
```


# Possible Finding Title

```text
UAC Elevation Prompts Do Not Use the Secure Desktop
```


# Further Validation

Determine whether:

```text
The organisation requires secure desktop

Another control compensates

The setting is intentionally disabled for accessibility or compatibility
```


# Finding - Excessive Local Administrator Rights

Observation:

```text
Ordinary user:
Member of BUILTIN\Administrators
```

Possible finding:

```text
Standard User Accounts Have Unnecessary Local Administrator Privileges
```


# Root Cause

This is primarily a:

```text
Least privilege
```

issue rather than a UAC configuration issue.


# Finding - Built-In Administrator Enabled

The built-in Administrator account being enabled is not automatically a vulnerability.

Review:

```text
Business need

Authentication controls

Password management

Remote access

Admin Approval Mode

Monitoring
```


# Finding - Remote Token Filtering Weakened

If configuration changes remote UAC restrictions, determine why.

Do not report the Registry value alone.

Establish:

```text
Affected accounts

Remote management exposure

Network access

Administrative privileges

Enterprise requirement
```


# Reporting

A strong UAC finding should contain:

```text
Affected endpoint

Affected identity

Administrator membership

Current integrity level

Relevant UAC policy

Observed behavior

Security consequence

Compensating controls

Recommended policy
```


# Weak Finding

Avoid:

> UAC can be bypassed.

This does not explain:

```text
Which user was tested?

Was the user already an administrator?

Which configuration was weak?

What boundary was crossed?

What actual impact was demonstrated?
```


# Better Finding

> The tested user account is a member of the local Administrators group and normally operates at medium integrity. The effective UAC configuration permits administrative elevation without a consent prompt, reducing the user interaction normally required before administrative operations execute at high integrity.


# Remediation

UAC remediation should be based on:

```text
Least privilege

Microsoft security guidance

Organisational security baseline

Application compatibility

Endpoint role
```


# Enable UAC

Where organisational policy requires UAC:

```text
EnableLUA
```

should remain enabled.


# Configure Admin Approval Mode

Administrative users should use appropriate Admin Approval Mode settings rather than operating continuously with unrestricted administrative execution.


# Secure Desktop

Use the secure desktop for elevation prompts where required by the security baseline.


# Standard Users

Prefer standard-user accounts for normal daily activity.


# Separate Administrative Accounts

Where appropriate:

```text
Normal Account
      |
      v
Daily Activity

Administrative Account
      |
      v
Privileged Administration
```


# Reduce Local Administrators

Remove unnecessary users and groups from:

```text
BUILTIN\Administrators
```


# Manage Local Administrator Passwords

Use appropriate enterprise mechanisms such as Windows LAPS where local administrative accounts are required.


# Application Compatibility

Applications that unnecessarily require administrative privileges should be redesigned or reconfigured where possible.


# Central Management

Apply UAC configuration through the organisation's authoritative management platform:

```text
Group Policy

MDM

Security baseline

Endpoint management
```


# Do Not Rely on UAC Alone

Combine UAC with:

```text
Application control

Defender

Secure ACLs

Least privilege

Credential protection

Patch management

Security monitoring
```


# Retesting

Retesting should verify both:

```text
Configuration

Observed behavior
```


# Step 1 - User

```cmd
whoami
```


# Step 2 - Membership

```cmd
whoami /groups
```


# Step 3 - Integrity

```powershell
whoami /groups | Select-String 'Mandatory'
```


# Step 4 - UAC

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' |
    Select-Object EnableLUA,
                  ConsentPromptBehaviorAdmin,
                  ConsentPromptBehaviorUser,
                  PromptOnSecureDesktop,
                  FilterAdministratorToken
```


# Step 5 - Local Administrators

```powershell
Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue
```


# Step 6 - Remote Filtering

```powershell
Get-ItemPropertyValue `
    -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' `
    -Name 'LocalAccountTokenFilterPolicy' `
    -ErrorAction SilentlyContinue
```


# Step 7 - Runtime Validation

Where approved:

```powershell
Start-Process powershell.exe -Verb RunAs
```

Confirm that the expected:

```text
Consent

Credential

Secure desktop

or denial behavior
```

occurs.


# Step 8 - Elevated Integrity

Inside an approved elevated session:

```powershell
whoami /groups | Select-String 'Mandatory'
```


# Step 9 - Business Applications

Confirm that required applications continue functioning after UAC hardening.


# Retest Matrix

| Test | Expected After Fix |
|---|---|
| `EnableLUA` | Enabled |
| Administrator consent | Matches baseline |
| Standard-user elevation | Matches baseline |
| Secure desktop | Enabled where required |
| Local administrators | Only authorised identities |
| Built-in Administrator | Controlled |
| Remote token filtering | Matches baseline |
| Daily user session | Standard/filtered context |
| Approved admin workflow | Functional |
| Business applications | Functional |


# UAC Assessment Checklist

## Identity

- [ ] Current user identified
- [ ] SID recorded
- [ ] Local administrator membership checked
- [ ] Domain group membership considered
- [ ] Built-in Administrator distinguished by SID

## Token

- [ ] Integrity level identified
- [ ] Administrator role checked
- [ ] Privileges reviewed
- [ ] Filtered vs elevated context understood

## UAC Core

- [ ] `EnableLUA` checked
- [ ] `ConsentPromptBehaviorAdmin` checked
- [ ] `ConsentPromptBehaviorUser` checked
- [ ] `PromptOnSecureDesktop` checked
- [ ] `FilterAdministratorToken` checked
- [ ] `EnableInstallerDetection` checked
- [ ] `EnableVirtualization` checked
- [ ] `ValidateAdminCodeSignatures` checked
- [ ] `EnableSecureUIAPaths` checked

## Local Administrators

- [ ] Administrators group enumerated
- [ ] Unnecessary users identified
- [ ] Unnecessary domain groups identified
- [ ] Separate administrative identities considered

## Built-In Administrator

- [ ] SID `-500` account identified
- [ ] Enabled state checked
- [ ] Admin Approval Mode considered
- [ ] Remote access considered

## Remote UAC

- [ ] `LocalAccountTokenFilterPolicy` checked
- [ ] Local vs domain accounts distinguished
- [ ] Remote management architecture understood
- [ ] Token filtering not weakened during testing

## Group Policy

- [ ] Domain policy considered
- [ ] `gpresult` reviewed where appropriate
- [ ] Authoritative management source identified
- [ ] Local configuration not assumed to be authoritative

## Application Security

- [ ] Application manifests considered
- [ ] Unnecessary `requireAdministrator` usage considered
- [ ] Installer behavior considered
- [ ] UAC virtualization considered
- [ ] Application compatibility considered

## Related Controls

- [ ] AppLocker considered
- [ ] WDAC considered
- [ ] Defender considered
- [ ] Filesystem permissions considered
- [ ] Service permissions considered
- [ ] Scheduled tasks considered
- [ ] Registry permissions considered

## Runtime Validation

- [ ] Normal shell integrity captured
- [ ] Normal elevation mechanism used where approved
- [ ] Prompt behavior observed
- [ ] Secure desktop behavior observed
- [ ] Elevated shell integrity captured
- [ ] No UAC settings modified for validation

## Reporting

- [ ] User context clearly stated
- [ ] Existing administrator membership stated
- [ ] Integrity transition clearly stated
- [ ] Exact policy value captured
- [ ] Policy meaning verified
- [ ] Runtime behavior captured
- [ ] UAC not incorrectly described as a security boundary
- [ ] Severity reflects actual privilege transition
- [ ] Least-privilege issues separated from UAC issues

## Retesting

- [ ] Same user context retested
- [ ] UAC policy rechecked
- [ ] Integrity level rechecked
- [ ] Administrator membership rechecked
- [ ] Elevation workflow rechecked
- [ ] Secure desktop rechecked
- [ ] Business functionality confirmed


# Quick Reference

| Goal | Command |
|---|---|
| Current user | `whoami` |
| User SID | `whoami /user` |
| Groups | `whoami /groups` |
| Privileges | `whoami /priv` |
| Full token information | `whoami /all` |
| Integrity level | `whoami /groups` |
| Local administrators | `Get-LocalGroupMember -Group 'Administrators'` |
| Built-in Administrator | `Get-LocalUser \| Where-Object { $_.SID.Value -match '-500$' }` |
| UAC policy | `Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'` |
| UAC enabled | `(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System').EnableLUA` |
| Admin prompt behavior | `ConsentPromptBehaviorAdmin` |
| User prompt behavior | `ConsentPromptBehaviorUser` |
| Secure desktop | `PromptOnSecureDesktop` |
| Built-in Admin Approval Mode | `FilterAdministratorToken` |
| Remote token filtering | `LocalAccountTokenFilterPolicy` |
| Request normal elevation | `Start-Process powershell.exe -Verb RunAs` |
| Resultant policy | `gpresult /r` |


# UAC Policy Matrix

| Setting | Security Question |
|---|---|
| `EnableLUA` | Is UAC enabled? |
| `ConsentPromptBehaviorAdmin` | How do administrators elevate? |
| `ConsentPromptBehaviorUser` | How do standard users request elevation? |
| `PromptOnSecureDesktop` | Are prompts isolated on secure desktop? |
| `FilterAdministratorToken` | Is Admin Approval Mode applied to built-in Administrator? |
| `EnableInstallerDetection` | Is installer detection enabled? |
| `EnableVirtualization` | Is legacy virtualization enabled? |
| `ValidateAdminCodeSignatures` | Are elevation signatures required? |
| `EnableSecureUIAPaths` | Are UIAccess applications restricted appropriately? |
| `LocalAccountTokenFilterPolicy` | How are remote local administrator tokens handled? |


# Token Interpretation Matrix

| User | Integrity | Typical Interpretation |
|---|---|---|
| Standard user | Medium | Normal standard-user session |
| Local administrator | Medium | Filtered administrator token |
| Local administrator | High | Elevated administrator process |
| SYSTEM | System | System service/process |
| Restricted process | Low | Sandboxed/restricted context |


# Finding Classification Matrix

| Observation | Likely Category |
|---|---|
| UAC disabled | Endpoint hardening |
| Admin elevation without prompt | UAC configuration |
| Secure desktop disabled | UAC hardening |
| Ordinary users are local admins | Least privilege |
| Weak service ACL | Service security |
| Writable Program Files application | Filesystem permissions |
| Unprotected privileged task | Scheduled task security |
| Weak Registry ACL | Registry security |
| Missing AppLocker rule | Application control |
| Defender disabled | Endpoint protection |


# UAC vs Privilege Escalation

```text
CASE 1

Standard User
     |
     v
Administrator

Actual privilege escalation
```

```text
CASE 2

Administrator
Medium Integrity
     |
     v
Administrator
High Integrity

UAC elevation
```

These should not be reported as equivalent security transitions.


# Defense-in-Depth Model

```text
Standard User
     |
     v
Least Privilege
     |
     v
Application Control
     |
     v
Defender / EDR
     |
     v
UAC
     |
     v
Secure Administrative Workflow
```


# Practical Reporting Model

```text
APPLICABILITY
     |
     v
USER CONTEXT
     |
     v
ADMIN MEMBERSHIP
     |
     v
TOKEN / INTEGRITY
     |
     v
UAC CONFIGURATION
     |
     v
OBSERVED ELEVATION
     |
     v
ALTERNATIVE EXPLANATIONS
     |
     v
SECURITY IMPACT
     |
     v
REMEDIATION
     |
     v
RETEST
```


# Final Testing Principle

UAC testing is not:

```text
Current Shell = Medium
       |
       v
Obtain High Integrity
       |
       v
Critical Privilege Escalation
```

Instead determine:

```text
WHO IS THE USER?
       |
       v
IS THE USER ALREADY AN ADMIN?
       |
       v
WHAT TOKEN IS ACTIVE?
       |
       v
WHAT UAC POLICY APPLIES?
       |
       v
WHAT ELEVATION BEHAVIOR OCCURS?
       |
       v
WHAT SECURITY BOUNDARY WAS ACTUALLY CROSSED?
       |
       v
WHAT IS THE REAL IMPACT?
```


# Final Questions

For every UAC assessment ask:

```text
Who is the current user?

What is the user's SID?

Is the user a local administrator?

Is the membership direct or inherited?

Is the account the built-in Administrator?

What integrity level is the current process?

Is the current token elevated?

Which privileges are enabled?

Is UAC enabled?

Is Admin Approval Mode active?

How are administrator elevation requests handled?

How are standard-user elevation requests handled?

Does elevation use the secure desktop?

Is installer detection enabled?

Is UAC virtualization enabled?

Is signed elevation required?

How is UIAccess restricted?

How is the built-in Administrator configured?

Is the built-in Administrator enabled?

Are ordinary users unnecessarily local administrators?

Is local administrator access centrally managed?

Does the organisation use separate administrative identities?

Does the organisation use Windows LAPS?

Is the UAC policy locally or centrally managed?

Does Group Policy configure UAC?

Does MDM configure UAC?

Does the observed runtime behavior match policy?

What happens during a normal RunAs elevation?

Is consent requested?

Are credentials requested?

Is the request denied?

Does the prompt use the secure desktop?

What integrity level does the elevated process receive?

Is remote UAC token filtering active?

Has LocalAccountTokenFilterPolicy been changed?

Does remote behavior differ for local and domain accounts?

Are applications unnecessarily requesting administrative rights?

Do applications rely on UAC virtualization?

Are privileged application files protected by ACLs?

Are privileged service files protected?

Are privileged scheduled tasks protected?

Are sensitive Registry paths protected?

Is AppLocker configured?

Is WDAC configured?

Is Defender operational?

Does application control reduce execution exposure?

Is the observed issue really UAC related?

Is it actually a least-privilege issue?

Is it actually a filesystem-permission issue?

Is it actually a service-permission issue?

Is it actually an application-control issue?

Was the tested account already an administrator?

What privilege transition actually occurred?

Does the observation cross a documented security boundary?

What compensating controls exist?

What evidence supports the finding?

Does remediation preserve administrative functionality?

Does retesting reproduce the expected elevation workflow?
```


# Related Windows Notes

- [Windows Overview](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [Windows PowerShell](powershell.md)
- [Windows Services](services.md)
- [Windows Scheduled Tasks](scheduled-tasks.md)
- [Windows Registry Security](registry.md)
- [Windows Filesystem Permissions](filesystem-permissions.md)
- [Windows Application Control](application-control.md)
- [Microsoft Defender Security Assessment](defender.md)
- [Windows Credentials](credentials.md)


# References

- [Microsoft Learn - User Account Control](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - How User Account Control Works](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - UAC Settings and Configuration](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/settings-and-configuration){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - UAC Security Policy Settings](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/user-account-control){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - User Account Control and Remote Restrictions](https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/user-account-control-and-remote-restriction){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Windows Security Baselines](https://learn.microsoft.com/en-us/windows/security/operating-system-security/device-management/windows-security-configuration-framework/windows-security-baselines){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Windows LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Application Control for Business](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Abuse Elevation Control Mechanism: Bypass User Account Control](https://attack.mitre.org/techniques/T1548/002/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Establish administrator membership first"

    Before interpreting a UAC elevation result, determine whether the tested account already belongs to the local Administrators group. Moving from a filtered medium-integrity administrator token to a high-integrity administrator token is not equivalent to a standard user becoming an administrator.


!!! tip "Record both policy and behavior"

    Registry and Group Policy values show configuration, while an approved normal elevation test shows runtime behavior. Strong assessment evidence uses both.


!!! tip "Treat least privilege separately"

    If ordinary users are unnecessarily members of the local Administrators group, report the underlying least-privilege problem rather than relying on UAC prompts as the primary mitigation.


!!! tip "Correlate with other Windows controls"

    UAC is only one layer. Application control, Defender, filesystem permissions, service security, scheduled tasks and credential protections determine the broader endpoint security posture.


!!! warning "UAC is not a security boundary"

    Do not automatically classify a medium-to-high integrity transition for an account already in the Administrators group as a standard-user privilege escalation. Document the actual identity, token and privilege transition.


!!! warning "Do not weaken UAC during validation"

    Normal assessment does not require changing `EnableLUA`, consent behavior, secure desktop configuration or remote token filtering. Inspect the effective configuration and use the standard Windows elevation workflow where runtime validation is authorised.
