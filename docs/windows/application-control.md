---
title: Windows Application Control
description: Practical Windows application control assessment covering AppLocker, Windows Defender Application Control, Software Restriction Policies, PowerShell language modes, effective policy validation, execution rules, evidence collection, remediation and retesting.
---

# Windows Application Control

Windows application control determines which executables, scripts, installers, DLLs and packaged applications are permitted to run.

The two primary modern Windows technologies are:

```text
AppLocker

Windows Defender Application Control - WDAC
```

Other controls can include:

```text
Software Restriction Policies - SRP

PowerShell execution policy

PowerShell language mode

Microsoft Defender Attack Surface Reduction rules

Endpoint security products
```

These technologies overlap in some areas but are not equivalent.

During a Windows security assessment, the objective is to determine:

```text
Which application-control technology is active?

Which file types are controlled?

Which users are affected?

Which paths, publishers or hashes are trusted?

Which rules deny execution?

Which rules are audit-only?

Are writable locations trusted?

Are interpreters or script hosts unnecessarily permitted?

Does the effective behaviour match the intended security policy?
```

!!! warning "Authorised Security Testing"

    Perform application-control testing only on systems included in the authorised assessment scope. Prefer policy inspection and harmless test files. Do not disable application control, security products or enterprise policy simply to demonstrate that a restriction exists.


# Application Control Security Model

A simplified model is:

```text
User
  |
  v
Attempts Execution
  |
  v
Application Control
  |
  +------------------+
  |                  |
  v                  v
Allowed             Denied
  |                  |
  v                  v
Execution          Blocked
```

The security value depends heavily on what is actually trusted.


# Application Control Is Not Just "On" or "Off"

A system may enforce:

```text
EXE rules
```

while leaving:

```text
DLL rules
```

unconfigured.

Or it may enforce:

```text
EXE
MSI
Script
AppX
```

with different rule sets.

Therefore:

```text
Application control enabled
```

is not a sufficiently precise conclusion.


# Assessment Model

Use:

```text
IDENTIFY CONTROL
      |
      v
IDENTIFY ENFORCEMENT MODE
      |
      v
ENUMERATE RULE COLLECTIONS
      |
      v
ENUMERATE ALLOW / DENY RULES
      |
      v
IDENTIFY TRUST BOUNDARIES
      |
      v
CORRELATE WITH FILESYSTEM ACLs
      |
      v
VALIDATE EFFECTIVE BEHAVIOUR
      |
      v
ASSESS COVERAGE
      |
      v
REPORT
```


# Start With the Current User

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


# PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```


# Common Results

```text
FullLanguage

ConstrainedLanguage

RestrictedLanguage

NoLanguage
```


# Interpretation

## FullLanguage

```text
FullLanguage
```

provides the normal PowerShell language capabilities available to the current process.

This does not automatically mean:

```text
Application control is absent
```

or:

```text
The host is vulnerable
```


# ConstrainedLanguage

```text
ConstrainedLanguage
```

restricts various PowerShell language capabilities.

It is commonly encountered when PowerShell is operating under an application-control security boundary.


# Important

Do not treat:

```text
ConstrainedLanguage
```

as equivalent to:

```text
PowerShell cannot execute commands
```

Many ordinary PowerShell operations remain available.


# PowerShell Execution Policy

Check:

```powershell
Get-ExecutionPolicy
```


# All Scopes

```powershell
Get-ExecutionPolicy -List
```


# Example

```text
        Scope ExecutionPolicy
        ----- ---------------
MachinePolicy       Undefined
   UserPolicy       Undefined
      Process       Undefined
  CurrentUser       Undefined
 LocalMachine    RemoteSigned
```


# Execution Policy Is Not Application Control

PowerShell execution policy primarily helps control script-loading behaviour.

It should not be treated as a strong security boundary equivalent to:

```text
AppLocker

WDAC
```


# AppLocker

AppLocker can define rules for:

```text
Executables

Windows Installer files

Scripts

DLLs

Packaged applications and installers
```


# Rule Collections

Common AppLocker collection types are:

```text
Exe

Msi

Script

Dll

Appx
```


# Get Effective AppLocker Policy

```powershell
Get-AppLockerPolicy -Effective
```


# XML View

```powershell
Get-AppLockerPolicy -Effective -Xml
```


# Save Effective Policy

```powershell
Get-AppLockerPolicy -Effective -Xml | Out-File -FilePath "$env:TEMP\AppLocker-Effective.xml" -Encoding utf8
```


# Why Effective Policy Matters

Do not rely only on local configuration.

The effective policy may combine:

```text
Local policy

Domain Group Policy

Enterprise configuration
```


# Local AppLocker Policy

```powershell
Get-AppLockerPolicy -Local
```


# Compare Local and Effective

```powershell
$local = Get-AppLockerPolicy -Local
$effective = Get-AppLockerPolicy -Effective
```


# Assessment Principle

Prefer:

```text
Effective policy
```

when determining what actually applies to the endpoint.


# Basic AppLocker Summary

```powershell
$policy = Get-AppLockerPolicy -Effective

$policy.RuleCollections |
    Select-Object CollectionType,EnforcementMode
```


# Alternative XML Inspection

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    Select-Object Type,EnforcementMode
```


# Expected Collection Types

```text
Exe

Msi

Script

Dll

Appx
```


# Enforcement Modes

AppLocker collections can operate in modes such as:

```text
Enabled

AuditOnly

NotConfigured
```


# Enabled

```text
Enabled
```

means applicable policy decisions are enforced.


# AuditOnly

```text
AuditOnly
```

records policy decisions but does not block execution.


# NotConfigured

```text
NotConfigured
```

means that collection does not provide an active AppLocker enforcement boundary by itself.


# Important Reporting Distinction

Do not report:

```text
AppLocker protects DLL execution
```

when:

```text
Dll = NotConfigured
```


# Full Collection Summary

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    ForEach-Object {
        [PSCustomObject]@{
            Type            = $_.Type
            EnforcementMode = $_.EnforcementMode
        }
    } |
    Format-Table -AutoSize
```


# Example

```text
Type    EnforcementMode
----    ---------------
Exe     Enabled
Msi     Enabled
Script  Enabled
Dll     NotConfigured
Appx    Enabled
```


# Interpretation

This means AppLocker enforcement covers:

```text
EXE

MSI

Scripts

Packaged applications
```

but the AppLocker DLL rule collection is not configured.


# AppLocker Rule Types

Rules can generally be based on:

```text
Path

Publisher

File hash
```


# Path Rules

Example concept:

```text
%WINDIR%\*
```

or:

```text
%PROGRAMFILES%\*
```


# Publisher Rules

Publisher rules can use signed-file metadata such as:

```text
Publisher

Product

Filename

Version
```


# Hash Rules

Hash rules identify specific file content using a cryptographic file hash.


# Allow and Deny

Rules may have actions such as:

```text
Allow

Deny
```


# Enumerate Rules

```powershell
$policy = Get-AppLockerPolicy -Effective

$policy.RuleCollections |
    ForEach-Object {
        $_.Rules
    }
```


# XML Rule Enumeration

For detailed analysis:

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    ForEach-Object {
        $collection = $_

        foreach ($ruleType in 'FilePathRule','FilePublisherRule','FileHashRule') {
            foreach ($rule in $collection.$ruleType) {
                [PSCustomObject]@{
                    Collection  = $collection.Type
                    Enforcement = $collection.EnforcementMode
                    RuleType    = $ruleType
                    Name        = $rule.Name
                    Action      = $rule.Action
                    UserOrGroup = $rule.UserOrGroupSid
                }
            }
        }
    } |
    Format-Table -AutoSize
```


# Path Rule Enumeration

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    ForEach-Object {
        $collection = $_

        foreach ($rule in $collection.FilePathRule) {
            [PSCustomObject]@{
                Collection  = $collection.Type
                Enforcement = $collection.EnforcementMode
                Name        = $rule.Name
                Action      = $rule.Action
                UserOrGroup = $rule.UserOrGroupSid
                Path        = $rule.Conditions.FilePathCondition.Path
            }
        }
    } |
    Format-Table -AutoSize
```


# Publisher Rule Enumeration

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    ForEach-Object {
        $collection = $_

        foreach ($rule in $collection.FilePublisherRule) {
            $condition = $rule.Conditions.FilePublisherCondition

            [PSCustomObject]@{
                Collection  = $collection.Type
                Enforcement = $collection.EnforcementMode
                Name        = $rule.Name
                Action      = $rule.Action
                UserOrGroup = $rule.UserOrGroupSid
                Publisher   = $condition.PublisherName
                Product     = $condition.ProductName
                Binary      = $condition.BinaryName
            }
        }
    } |
    Format-Table -AutoSize
```


# Hash Rule Enumeration

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    ForEach-Object {
        $collection = $_

        foreach ($rule in $collection.FileHashRule) {
            foreach ($hash in $rule.Conditions.FileHashCondition.FileHash) {
                [PSCustomObject]@{
                    Collection  = $collection.Type
                    Enforcement = $collection.EnforcementMode
                    Name        = $rule.Name
                    Action      = $rule.Action
                    UserOrGroup = $rule.UserOrGroupSid
                    FileName    = $hash.SourceFileName
                    Hash        = $hash.Data
                }
            }
        }
    } |
    Format-Table -AutoSize
```


# Path Rules and Filesystem Permissions

This is one of the most important AppLocker assessment concepts.

Suppose policy allows:

```text
%WINDIR%\*
```

This assumes the allowed location is appropriately protected.


# Security Model

```text
ALLOW PATH
    |
    v
Trusted Directory
    |
    v
Can Standard User Write?
    |
 +--+--+
 |     |
 No   Yes
 |     |
 v     v
Good  Investigate
```


# Why Writable Allowed Paths Matter

A path-based allow rule can become weaker when a lower-privileged user can introduce executable content into that trusted path.

Therefore always correlate:

```text
AppLocker path rules
```

with:

```text
NTFS permissions
```


# Example

Policy:

```text
Allow:
C:\TrustedApps\*
```

Filesystem:

```text
BUILTIN\Users = Modify
```

This deserves investigation.


# Check ACL

```cmd
icacls "C:\TrustedApps"
```


# PowerShell

```powershell
(Get-Acl -LiteralPath 'C:\TrustedApps').Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited
```


# Important

Do not report a bypass merely because an allowed directory is writable.

Establish:

```text
Applicable collection

Applicable user

Rule precedence

Effective policy

File type

Actual policy decision
```


# Default Windows Path Rules

AppLocker deployments commonly trust locations associated with:

```text
Windows

Program Files
```

These locations are generally protected from modification by standard users.


# Security Assumption

```text
Trusted path
+
Protected ACL
=
Stronger path-based trust
```


# Weak Trust Pattern

```text
Trusted path
+
User-writable ACL
=
Potential policy weakness
```


# Environment Variables

AppLocker paths may use variables such as:

```text
%WINDIR%

%PROGRAMFILES%
```


# Expand Environment Variables

```powershell
[Environment]::ExpandEnvironmentVariables('%WINDIR%')
```


# Program Files

```powershell
$env:ProgramFiles
```


# Program Files x86

```powershell
${env:ProgramFiles(x86)}
```


# Important

Do not assume that every directory underneath an allowed root has identical ACLs.

Applications may create subdirectories with weaker permissions.


# Writable Subdirectory Review

For interesting application directories:

```powershell
Get-Acl -LiteralPath 'C:\Program Files\Example' | Format-List Owner,AccessToString
```


# Related Note

See:

[Windows Filesystem Permissions](filesystem-permissions.md)


# Testing AppLocker Policy Decisions

AppLocker provides:

```powershell
Test-AppLockerPolicy
```


# Test a Known File

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\notepad.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```


# Format Result

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\notepad.exe" -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Possible Decisions

Results can indicate outcomes such as:

```text
Allowed

Denied

DeniedByDefault

AllowedByDefault
```

depending on policy and collection behaviour.


# Why Test-AppLockerPolicy Is Valuable

It helps answer:

```text
What does the effective AppLocker policy say about this exact file for this exact user?
```


# Important Limitation

Policy simulation is not always equivalent to every runtime enforcement layer.

A system may also use:

```text
WDAC

ASR

Antivirus

EDR

Other endpoint controls
```

Therefore combine policy inspection with harmless runtime validation where necessary.


# Test an EXE

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\Example.exe' -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Test a Script

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\Test.ps1' -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Test MSI

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\Test.msi' -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Test DLL

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\Test.dll' -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Test the Correct User

Do not accidentally evaluate policy against a different account.

Confirm:

```cmd
whoami
```

Then test using the applicable identity.


# Test Multiple Files

```powershell
$policy = Get-AppLockerPolicy -Effective
$user = "$env:USERDOMAIN\$env:USERNAME"

$files = @(
    "$env:WINDIR\System32\notepad.exe",
    "$env:WINDIR\System32\whoami.exe"
)

foreach ($file in $files) {
    $policy |
        Test-AppLockerPolicy -Path $file -User $user |
        Select-Object FilePath,PolicyDecision,MatchingRule
}
```


# Runtime Validation

When appropriate, use harmless Windows binaries or harmless test content.

For example:

```powershell
& "$env:WINDIR\System32\whoami.exe"
```


# Interpretation

Successful execution establishes:

```text
This executable was permitted to run in the current runtime context.
```

It does not establish:

```text
All executables are permitted.
```


# Controlled Test File

For a script rule test:

```powershell
'Write-Output "Application control test"' |
    Set-Content -LiteralPath "$env:TEMP\application-control-test.ps1"
```


# Test Policy

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:TEMP\application-control-test.ps1" -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Cleanup

```powershell
Remove-Item -LiteralPath "$env:TEMP\application-control-test.ps1" -Force -ErrorAction SilentlyContinue
```


# EXE Collection

The EXE collection controls executable files.

Typical security questions:

```text
Is EXE enforcement enabled?

Which paths are trusted?

Which publishers are trusted?

Are unsigned executables allowed?

Are user-writable paths trusted?

Are deny rules present?

Which users are affected?
```


# MSI Collection

The MSI collection applies to Windows Installer files.

Review:

```text
MSI enforcement mode

Publisher rules

Path rules

Hash rules

User-writable trusted paths
```


# Script Collection

Script rules can apply to script types handled by AppLocker.

Security analysis should include:

```text
PowerShell

Batch

Command scripts

VBScript

JScript
```

where applicable.


# Important

Do not assume:

```text
Script collection enabled
```

means:

```text
No scripting is possible.
```

The actual behaviour depends on the rules and execution environment.


# DLL Collection

DLL enforcement deserves special attention.


# Why DLL Rules Matter

Applications can load:

```text
DLLs

Libraries

Modules

Plugins
```

during normal operation.


# Performance Consideration

DLL enforcement can require evaluation of loaded libraries, which is one reason deployments may treat DLL rules differently from EXE rules.


# Assessment Question

Check whether:

```text
Dll = Enabled
```

or:

```text
Dll = NotConfigured
```


# Important Conclusion

If DLL rules are not configured, report exactly that:

> The effective AppLocker policy does not configure the DLL rule collection.

Do not automatically report:

> Arbitrary DLL execution is possible.

Those are different statements.


# AppX Collection

The AppX collection applies to packaged applications and installers.

Review:

```text
Enforcement mode

Publisher rules

Applicable users/groups
```


# Default-Deny Behaviour

AppLocker enforcement commonly relies on the presence of rules in an enforced collection.

The exact effective behaviour should be validated using:

```powershell
Test-AppLockerPolicy
```

rather than inferred solely from a partial policy listing.


# Deny Rules

Explicit deny rules deserve attention because they may intentionally restrict:

```text
Specific applications

Specific publishers

Specific versions

Specific users
```


# Rule Exceptions

AppLocker rules can contain exceptions.

Exceptions are important because an apparently broad allow rule may exclude specific paths or publishers.


# Path Rule Exceptions

When inspecting XML, review:

```text
Exceptions
```

as well as:

```text
Conditions
```


# Rule Review Principle

For each rule record:

```text
Collection

Enforcement

Action

Identity

Condition

Exceptions
```


# Rule Identity

Rules can target:

```text
Everyone

Specific users

Specific groups
```


# SID Resolution

Rules may contain SIDs.

PowerShell can resolve many account SIDs:

```powershell
$sid = New-Object System.Security.Principal.SecurityIdentifier('S-1-1-0')
$sid.Translate([System.Security.Principal.NTAccount]).Value
```


# Example

```text
Everyone
```


# Publisher Trust

Publisher rules can be useful because they allow software based on signing identity rather than only path.


# Security Questions

Ask:

```text
Which publisher is trusted?

Which product is trusted?

Which binary names are trusted?

Which versions are trusted?

Is the rule broader than necessary?
```


# Signed Does Not Automatically Mean Safe

A digital signature establishes publisher and integrity properties.

It does not automatically mean:

```text
Every signed application should be trusted for every user.
```


# Hash Rules

Hash rules provide precise control over specific file content.


# Operational Consideration

When the file changes:

```text
Hash changes
```

so policy maintenance may be required.


# Application Control Coverage

Build a matrix:

| Collection | Mode | Covered? | Review |
|---|---|---:|---|
| EXE | Enabled | Yes | Rules |
| MSI | Enabled | Yes | Rules |
| Script | Enabled | Yes | Rules |
| DLL | NotConfigured | No AppLocker collection | Additional controls |
| AppX | Enabled | Yes | Rules |


# Do Not Stop at AppLocker

A Windows endpoint may also use WDAC.


# Windows Defender Application Control

Windows Defender Application Control provides code integrity policy enforcement.

WDAC can apply more broadly than AppLocker and operates as part of the Windows code integrity architecture.


# Terminology

You may encounter:

```text
WDAC

Windows Defender Application Control

Application Control for Business

Code Integrity policy
```


# Assessment Questions

Determine:

```text
Are WDAC policies present?

Are they active?

Are they enforced or audit-only?

Are multiple policies deployed?

Which signing scenarios are trusted?

Are scripts affected indirectly?

How does PowerShell behave?

Are policy events recorded?
```


# Important

Do not assume that AppLocker output describes the complete application-control posture when WDAC is also present.


# Code Integrity Events

Code integrity logging can provide evidence about application-control decisions.


# Relevant Event Log

A useful log is:

```text
Microsoft-Windows-CodeIntegrity/Operational
```


# Query Recent Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message
```


# AppLocker Event Logs

Relevant AppLocker logs exist under:

```text
Microsoft-Windows-AppLocker
```


# List AppLocker Logs

```powershell
Get-WinEvent -ListLog 'Microsoft-Windows-AppLocker*' -ErrorAction SilentlyContinue |
    Select-Object LogName,RecordCount,IsEnabled
```


# Common Logs

Depending on Windows version and configuration, useful logs can include collections for:

```text
EXE and DLL

MSI and Script

Packaged applications
```


# Recent AppLocker Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message
```


# MSI and Script

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/MSI and Script' -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message
```


# Why Logs Matter

Logs can help distinguish:

```text
Allowed

Blocked

Audit-only

Policy not applicable

Different security control
```


# Runtime Block Attribution

If execution fails, do not immediately conclude:

```text
AppLocker blocked it.
```

Potential causes include:

```text
AppLocker

WDAC

ASR

Defender Antivirus

EDR

Filesystem ACL

PowerShell policy

Missing dependency

Application error
```


# Evidence Should Identify the Control

Use:

```text
Policy output

Event logs

Runtime message

Effective rule
```

to determine what actually blocked the action.


# Software Restriction Policies

Older environments may use Software Restriction Policies.

SRP can apply rules based on concepts such as:

```text
Path

Hash

Certificate

Internet zone
```


# Registry Locations

Policy information may exist under:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers
```

and potentially user policy locations.


# Query

```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers" /s
```


# Important

The absence of AppLocker does not prove:

```text
No application-control policy exists.
```


# AppLocker Service

The Application Identity service is associated with AppLocker functionality.


# Check

```powershell
Get-Service AppIDSvc -ErrorAction SilentlyContinue
```


# Example

```text
Status   Name      DisplayName
------   ----      -----------
Running  AppIDSvc  Application Identity
```


# Important

Service state alone does not describe the effective AppLocker policy.

Always inspect the policy itself.


# PowerShell and Application Control

PowerShell behaviour can provide useful supporting evidence.


# Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```


# Example

```text
ConstrainedLanguage
```


# Security Interpretation

Constrained Language Mode can reduce access to language features that enable broad interaction with .NET and other capabilities.

But assess the effective security architecture rather than treating the string itself as the entire control.


# New PowerShell Process

A child PowerShell process may inherit or independently determine its language mode based on the system's application-control state.


# Check Current Version

```powershell
$PSVersionTable
```


# PowerShell Executables

Potential installations can include:

```text
Windows PowerShell

PowerShell 7+
```

depending on the endpoint.


# Discover PowerShell

```powershell
Get-Command powershell.exe -ErrorAction SilentlyContinue
```

```powershell
Get-Command pwsh.exe -ErrorAction SilentlyContinue
```


# Important

Different PowerShell versions should be evaluated within the actual endpoint policy rather than assuming identical behaviour.


# Script Hosts

Windows contains multiple components capable of processing scripts or application content.

Examples include legitimate administrative technologies such as:

```text
PowerShell

Windows Script Host

Windows Installer
```

The assessment objective should be:

```text
Determine whether the application-control policy covers
the intended execution surfaces.
```

It should not become an indiscriminate attempt to defeat endpoint protections.


# Interpreter Assessment

For each relevant interpreter ask:

```text
Is the executable allowed?

Are scripts controlled?

Which users can invoke it?

Does application control apply to its content?

Does the business require it?
```


# Application Control and Services

A service executable may be permitted because it resides in:

```text
Program Files
```

or another trusted location.

Correlate this with:

```text
Service configuration

Filesystem permissions

Application-control rule
```


# Security Chain

```text
Service
  |
  v
Executable Path
  |
  v
Filesystem ACL
  |
  v
Application-Control Decision
  |
  v
Execution
```


# Application Control and Scheduled Tasks

Similarly:

```text
Scheduled Task
     |
     v
Script / EXE
     |
     v
ACL
     |
     v
App Control
     |
     v
Execution
```


# Application Control and Registry

Registry configuration may point privileged processes toward executable content.

Review:

[Windows Registry Security](registry.md)


# Application Control and Filesystem Permissions

Application-control path rules depend on filesystem trust.

Review:

[Windows Filesystem Permissions](filesystem-permissions.md)


# Application Control and Privilege Escalation

Application control should be treated as one layer in the complete privilege escalation analysis.


# Example

Suppose:

```text
Users can modify:
C:\ProgramData\Vendor\agent.exe
```

and:

```text
Service:
LocalSystem
```

but application control blocks the modified executable.


# Interpretation

There may still be:

```text
Insecure filesystem permissions
```

but:

```text
Successful privileged execution
```

has not been established through that path.


# Report Precisely

Possible conclusion:

> Standard users can modify executable content used by a SYSTEM service. However, runtime validation indicated that the modified execution path is subject to application-control enforcement. The underlying filesystem trust issue should still be corrected because the service relies on user-modifiable content.


# Application Control Does Not Fix Permissions

Do not recommend:

```text
Keep weak ACLs because AppLocker blocks execution.
```

Instead:

```text
Fix the ACL
+
Maintain application control
```


# Defense in Depth

```text
Secure ACL
   +
AppLocker / WDAC
   +
Defender
   +
Least Privilege
   =
Stronger Endpoint
```


# Policy Testing Workflow

Use:

```text
1. Identify current identity

2. Check PowerShell language mode

3. Inspect effective AppLocker policy

4. Enumerate collection enforcement

5. Enumerate rules

6. Identify path rules

7. Correlate path rules with NTFS ACLs

8. Test representative policy decisions

9. Review AppLocker logs

10. Review Code Integrity logs

11. Identify additional endpoint controls

12. Validate harmless runtime behaviour

13. Document gaps and mitigations
```


# Representative Test Matrix

Use harmless representative files where appropriate.

| Type | Question |
|---|---|
| EXE | Is executable enforcement active? |
| DLL | Is DLL enforcement configured? |
| PS1 | Is script enforcement active? |
| BAT/CMD | Is script execution controlled? |
| VBS/JS | Is Windows Script Host content controlled? |
| MSI | Is installer execution controlled? |
| AppX | Are packaged applications controlled? |


# Important

The matrix is intended to measure coverage.

It is not necessary to create malicious payloads to determine whether a policy collection is configured correctly.


# Policy Decision Evidence

For each tested file capture:

```text
File path

File type

Current user

Policy collection

Enforcement mode

Policy decision

Matching rule

Runtime result where relevant
```


# Example Evidence

```text
File:
C:\Users\User\AppData\Local\Temp\application-control-test.ps1

Collection:
Script

Enforcement:
Enabled

Decision:
DeniedByDefault

User:
DOMAIN\User
```


# Strong Evidence Chain

```text
Effective Policy
      |
      v
Script Collection Enabled
      |
      v
Test-AppLockerPolicy
      |
      v
DeniedByDefault
      |
      v
Runtime Block
      |
      v
Event Log
```

Multiple independent observations support a stronger conclusion.


# Allowed File Inventory

During an authorised assessment, it can be useful to identify known files that the effective policy allows.


# Example

For a controlled set of paths:

```powershell
$policy = Get-AppLockerPolicy -Effective
$user = "$env:USERDOMAIN\$env:USERNAME"

$files = Get-ChildItem "$env:WINDIR\System32" -Filter *.exe -File -ErrorAction SilentlyContinue |
    Select-Object -First 25

foreach ($file in $files) {
    $result = $policy |
        Test-AppLockerPolicy -Path $file.FullName -User $user

    [PSCustomObject]@{
        File     = $file.Name
        Path     = $file.FullName
        Decision = $result.PolicyDecision
        Rule     = $result.MatchingRule
    }
}
```


# Why Limit Enumeration?

Testing every executable on a system can generate large, difficult-to-review output.

Prefer targeted testing based on:

```text
Assessment objective

User-accessible applications

Privileged dependencies

Known business requirements
```


# Denied Files

Similarly, record representative denied content rather than attempting to generate an exhaustive bypass catalogue.


# Policy Coverage Summary

A useful final summary can look like:

```text
Application Control Summary

AppLocker:
Present

EXE:
Enabled

MSI:
Enabled

Script:
Enabled

DLL:
NotConfigured

AppX:
Enabled

PowerShell Language Mode:
ConstrainedLanguage

WDAC:
Requires separate Code Integrity validation

Primary Review:
DLL coverage and writable allowed paths
```


# Needs Review

When reporting a gap, identify exactly what needs review.

Weak:

```text
DLL needs review
```

Better:

```text
Rule collection:
Dll

Status:
NotConfigured

Impact to review:
DLL loading by privileged applications is not governed by an AppLocker DLL rule collection.

Additional validation:
Determine whether WDAC or another code integrity control provides equivalent DLL enforcement.
```


# Writable Allowed Path Review

For each broad path allow rule:

```text
1. Resolve path

2. Identify relevant directories

3. Inspect ACL

4. Identify standard-user write rights

5. Identify applicable file types

6. Test representative policy decision

7. Determine whether another control applies
```


# Example Review Table

| Allowed Path | Writable by Standard User? | Collection | Action |
|---|---:|---|---|
| `%WINDIR%\*` | Review subdirectories | EXE | Validate ACLs |
| `%PROGRAMFILES%\*` | Normally protected | EXE | Validate exceptions |
| Custom application path | Unknown | EXE | Inspect ACL |
| Custom script directory | Unknown | Script | Inspect ACL |


# Audit-Only Policies

Audit mode is valuable for deployment preparation but should not be described as active blocking.


# Example

```text
Collection:
Script

Mode:
AuditOnly
```


# Correct Conclusion

> Script policy rules are configured in audit-only mode and therefore provide visibility rather than blocking for the affected collection.


# Incorrect Conclusion

> Scripts are blocked by AppLocker.


# Application-Control Events

Audit events can help administrators understand what would be blocked before moving to enforcement.


# Policy Exceptions

Review exceptions carefully.

Example concept:

```text
Allow:
C:\Program Files\*

Except:
C:\Program Files\Vendor\Untrusted\
```


# Security Interpretation

The exception can materially change the effective trust boundary.


# Policy Scope

A rule targeted at:

```text
Administrators
```

does not necessarily apply to:

```text
Standard Users
```

and vice versa.


# Group Membership Correlation

Always correlate rule SIDs with:

```cmd
whoami /groups
```


# Domain Policy

Enterprise environments may deploy application control through:

```text
Group Policy

MDM

Endpoint management

Security baselines
```


# Local Modification

A local Registry or policy observation may not represent the management source of truth.

Determine whether configuration is centrally managed before recommending local changes.


# Policy Persistence

Enterprise management may automatically restore configuration.

Therefore remediation should generally occur at the authoritative policy source.


# AppLocker and Administrators

Do not assume administrators are always exempt from every policy.

Inspect the actual rule targets and effective policy.


# Application-Control Misconfiguration Patterns

Potential assessment findings include:

```text
Critical rule collection not enforced

Audit-only policy mistaken for enforcement

Broad user-writable path allowed

Overly broad publisher trust

Unexpected user/group exclusion

Privileged application loads uncontrolled dependencies

Policy differs from documented security baseline

Legacy execution surface not covered

Conflicting application-control technologies

Application-control logging unavailable
```


# Not Automatically Vulnerabilities

These observations require context:

```text
PowerShell is installed

cmd.exe is present

rundll32.exe exists

Windows Script Host exists

MSI support exists

DLL rules are not configured
```

The security impact depends on the endpoint threat model and complete control architecture.


# Application Inventory

Understanding what software must run helps determine whether rules are appropriately scoped.


# Installed Applications

```powershell
$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

Get-ItemProperty $paths -ErrorAction SilentlyContinue |
    Where-Object DisplayName |
    Select-Object DisplayName,DisplayVersion,Publisher
```


# Business Context

Application-control rules should balance:

```text
Security

Operational requirements

Administrative tooling

Software updates

Business applications
```


# Overly Restrictive Policy

A policy that blocks required software can lead administrators to introduce broad exceptions.

Therefore remediation should avoid:

```text
Allow C:\*
```

style solutions merely to restore functionality.


# Prefer Narrow Trust

Where practical:

```text
Publisher-specific rules

Protected path rules

Appropriate version restrictions

Specific exceptions
```

are preferable to unnecessarily broad trust.


# Policy Maintenance

Application control requires ongoing maintenance.

Changes such as:

```text
Software updates

New applications

Certificate changes

New administrative tooling

Operating system upgrades
```

may require policy review.


# Logging

Operational monitoring should include application-control events so unexpected blocks and audit findings can be investigated.


# Evidence Collection

A comprehensive assessment should capture:

```text
Current user

Group membership

PowerShell language mode

Execution policy

Effective AppLocker policy

Collection enforcement modes

Relevant rules

Relevant exceptions

Filesystem ACLs for trusted paths

Representative policy decisions

Runtime result

AppLocker events

Code Integrity events

Additional endpoint controls
```


# Evidence Commands

## Identity

```cmd
whoami
```

```cmd
whoami /groups
```


## PowerShell

```powershell
$ExecutionContext.SessionState.LanguageMode
```

```powershell
Get-ExecutionPolicy -List
```


## Effective AppLocker

```powershell
Get-AppLockerPolicy -Effective
```


## XML

```powershell
Get-AppLockerPolicy -Effective -Xml
```


## Collection Summary

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    Select-Object Type,EnforcementMode
```


## Test Exact File

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\Test.exe' -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


## Filesystem

```cmd
icacls "C:\Path"
```


## AppLocker Logs

```powershell
Get-WinEvent -ListLog 'Microsoft-Windows-AppLocker*' -ErrorAction SilentlyContinue |
    Select-Object LogName,RecordCount,IsEnabled
```


## Code Integrity

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message
```


# Finding Example - Writable Allowed Path

## Observation

```text
AppLocker EXE collection:
Enabled

Allow rule:
C:\CompanyApps\*

Filesystem:
BUILTIN\Users = Modify
```


## Further Validation

Determine:

```text
Does the rule apply to the current user?

Does the rule actually allow representative executable content?

Is WDAC also enforcing?

Does the directory legitimately require standard-user write access?
```


## Possible Finding Title

```text
AppLocker Trusts a Standard-User-Writable Application Directory
```


# Finding Example - Audit-Only Collection

Observation:

```text
Script:
AuditOnly
```


# Possible Finding Title

```text
AppLocker Script Rules Are Configured in Audit-Only Mode
```


# Context

Severity depends on whether script enforcement is required by the organisation's intended application-control baseline.


# Finding Example - Missing DLL Coverage

Observation:

```text
EXE:
Enabled

Script:
Enabled

DLL:
NotConfigured
```


# Correct Assessment

Investigate whether:

```text
WDAC provides DLL enforcement

Privileged applications load user-controlled libraries

The security baseline requires DLL control
```


# Possible Finding Title

If the complete assessment supports it:

```text
Application-Control Policy Does Not Enforce DLL Rules
```


# Do Not Overstate

Do not call this:

```text
AppLocker Bypass Allows SYSTEM Compromise
```

without evidence demonstrating such an impact.


# Finding Example - Policy vs Runtime Mismatch

Suppose:

```text
Test-AppLockerPolicy:
Denied
```

but runtime execution succeeds.


# Investigation

Determine whether:

```text
Collection is AuditOnly

Wrong user was tested

Wrong policy was inspected

Another file was executed

Rule conditions differ

Policy deployment is incomplete
```


# Conversely

If:

```text
Test-AppLockerPolicy:
Allowed
```

but execution fails, investigate:

```text
WDAC

ASR

Defender Antivirus

EDR

Filesystem permissions

Application errors
```


# Reporting

A strong application-control finding should describe:

```text
Control

Collection

Enforcement mode

Rule

Affected user/group

Trusted resource

Observed behaviour

Security consequence

Compensating controls

Recommended correction
```


# Weak Reporting

Avoid:

> AppLocker can be bypassed.

This does not identify:

```text
What rule is weak?

Which user is affected?

Which file type is involved?

Which trusted location is involved?

Which policy decision was observed?

What impact was demonstrated?
```


# Better Reporting

> The effective AppLocker EXE policy contains an allow rule for `C:\CompanyApps\*` that applies to standard users. NTFS permissions grant `BUILTIN\Users` Modify access to this directory. The path-based trust rule therefore relies on a location that standard users can modify, weakening the intended application-control boundary.


# Remediation

Application-control remediation should focus on the trust model rather than simply adding more deny rules.


# Secure Trusted Paths

Path-based allow rules should reference directories protected against modification by untrusted users.


# Correct NTFS Permissions

If a trusted path is writable:

```text
Remove unnecessary standard-user write access
```

where operationally possible.


# Narrow Broad Rules

Avoid unnecessarily broad path rules.


# Publisher Rules

Use appropriately scoped publisher rules where they better match software lifecycle requirements.


# Hash Rules

Use hashes for narrowly controlled files where appropriate, understanding the maintenance implications.


# Enforce Required Collections

Where organisational policy requires coverage, configure appropriate enforcement for:

```text
EXE

MSI

Script

DLL

AppX
```

based on the environment's security and compatibility requirements.


# Evaluate DLL Enforcement Carefully

DLL enforcement can have operational implications.

Test compatibility before broad deployment.


# Move From Audit to Enforcement

Use audit mode to understand impact before enforcement.

A controlled lifecycle is:

```text
Design
  |
  v
Audit
  |
  v
Review Events
  |
  v
Refine Rules
  |
  v
Pilot
  |
  v
Enforce
  |
  v
Monitor
```


# Central Management

Apply enterprise remediation through the authoritative management platform where applicable.


# Monitor Events

Ensure application-control event logs are available to security monitoring where appropriate.


# Maintain Policy

Review application-control rules after:

```text
Major software deployments

Operating system upgrades

Application upgrades

Certificate changes

Security incidents

Penetration tests
```


# Defense in Depth

Combine application control with:

```text
Secure filesystem ACLs

Least privilege

Credential protection

Defender

ASR

EDR

Patch management

Security monitoring
```


# Retesting

Retesting should reproduce the original weakness.


# Step 1 - Same User

```cmd
whoami
```


# Step 2 - Effective Policy

```powershell
Get-AppLockerPolicy -Effective
```


# Step 3 - Collection Mode

```powershell
[xml]$policy = Get-AppLockerPolicy -Effective -Xml

$policy.AppLockerPolicy.RuleCollection |
    Select-Object Type,EnforcementMode
```


# Step 4 - Rule

Confirm that the insecure rule has been:

```text
Removed

Narrowed

Replaced

or otherwise secured
```


# Step 5 - Filesystem

```cmd
icacls "C:\AffectedPath"
```


# Step 6 - Policy Decision

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\AffectedPath\Test.exe' -User "$env:USERDOMAIN\$env:USERNAME" |
    Format-List FilePath,PolicyDecision,MatchingRule
```


# Step 7 - Runtime

Where required, perform harmless runtime validation.


# Step 8 - Event Logs

Confirm expected application-control events are generated.


# Step 9 - Legitimate Software

Verify authorised applications still operate correctly.


# Retest Matrix

| Test | Expected After Fix |
|---|---|
| Trusted path writable by standard user | No |
| Unapproved EXE from user path | Blocked where policy requires |
| Unapproved script | Blocked where policy requires |
| Approved enterprise application | Allowed |
| Required installer | Allowed |
| Rule collection | Correct enforcement mode |
| AppLocker logging | Operational |
| Code Integrity logging | Operational |
| Business application functionality | Preserved |


# Application Control Checklist

## Identity

- [ ] Current user identified
- [ ] Groups identified
- [ ] Privileges reviewed
- [ ] Administrative status understood

## PowerShell

- [ ] Language mode checked
- [ ] Execution policy checked
- [ ] All execution-policy scopes reviewed
- [ ] PowerShell versions considered where relevant

## AppLocker

- [ ] Effective policy retrieved
- [ ] Local policy distinguished from effective policy
- [ ] EXE collection reviewed
- [ ] MSI collection reviewed
- [ ] Script collection reviewed
- [ ] DLL collection reviewed
- [ ] AppX collection reviewed

## Enforcement

- [ ] Enabled collections identified
- [ ] AuditOnly collections identified
- [ ] NotConfigured collections identified
- [ ] Intended baseline compared with effective state

## Rules

- [ ] Path rules reviewed
- [ ] Publisher rules reviewed
- [ ] Hash rules reviewed
- [ ] Allow rules reviewed
- [ ] Deny rules reviewed
- [ ] Exceptions reviewed
- [ ] User/group scope reviewed

## Filesystem Trust

- [ ] Allowed paths resolved
- [ ] NTFS ACLs checked
- [ ] User-writable trusted directories identified
- [ ] Writable subdirectories considered
- [ ] Parent ACL inheritance considered

## Policy Validation

- [ ] Representative EXE tested
- [ ] Representative script tested
- [ ] MSI coverage considered
- [ ] DLL coverage considered
- [ ] AppX coverage considered
- [ ] Correct user used for tests
- [ ] Matching rules captured

## WDAC

- [ ] WDAC considered
- [ ] Code Integrity logs reviewed
- [ ] AppLocker not assumed to be the only control
- [ ] Audit vs enforcement distinguished

## Legacy Controls

- [ ] SRP considered where relevant
- [ ] Execution policy not mistaken for strong application control

## Runtime

- [ ] Harmless runtime test performed where required
- [ ] Block attributed to correct security control
- [ ] Filesystem errors distinguished from policy blocks
- [ ] Application errors distinguished from policy blocks

## Logging

- [ ] AppLocker logs identified
- [ ] Code Integrity logs identified
- [ ] Audit events reviewed
- [ ] Block events reviewed

## Privilege Escalation Correlation

- [ ] Service dependencies reviewed
- [ ] Scheduled task dependencies reviewed
- [ ] Registry paths reviewed
- [ ] Filesystem permissions reviewed
- [ ] Application-control effect documented

## Reporting

- [ ] Exact collection reported
- [ ] Exact enforcement mode reported
- [ ] Exact rule reported
- [ ] Affected identity reported
- [ ] Matching path/publisher/hash reported
- [ ] Runtime result reported
- [ ] Compensating controls reported
- [ ] Impact not overstated

## Retesting

- [ ] Effective policy rechecked
- [ ] Weak rule rechecked
- [ ] Filesystem ACL rechecked
- [ ] Policy decision retested
- [ ] Runtime retested
- [ ] Event logging confirmed
- [ ] Legitimate applications tested


# Quick Reference

| Goal | Command |
|---|---|
| Current user | `whoami` |
| Groups | `whoami /groups` |
| Privileges | `whoami /priv` |
| PowerShell language mode | `$ExecutionContext.SessionState.LanguageMode` |
| Execution policy | `Get-ExecutionPolicy -List` |
| Effective AppLocker | `Get-AppLockerPolicy -Effective` |
| Effective AppLocker XML | `Get-AppLockerPolicy -Effective -Xml` |
| Local AppLocker | `Get-AppLockerPolicy -Local` |
| Test file | `Test-AppLockerPolicy` |
| ACL | `icacls "C:\Path"` |
| PowerShell ACL | `Get-Acl -LiteralPath 'C:\Path'` |
| AppLocker service | `Get-Service AppIDSvc` |
| AppLocker logs | `Get-WinEvent -ListLog 'Microsoft-Windows-AppLocker*'` |
| Code Integrity events | `Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational'` |


# Coverage Matrix

| Surface | Primary Question |
|---|---|
| EXE | Which executables can run? |
| MSI | Which installers can run? |
| Script | Which scripts are controlled? |
| DLL | Are libraries controlled? |
| AppX | Which packaged apps are trusted? |
| PowerShell | What language mode applies? |
| Filesystem | Are trusted paths protected? |
| WDAC | Is Code Integrity also enforcing? |
| Logging | Are allow/block events visible? |


# Interpretation Matrix

| Observation | Interpretation |
|---|---|
| EXE Enabled | EXE AppLocker rules are enforced |
| EXE AuditOnly | EXE rules are not blocking |
| DLL NotConfigured | No configured AppLocker DLL collection |
| FullLanguage | PowerShell is currently operating in FullLanguage |
| ConstrainedLanguage | PowerShell language capabilities are restricted |
| Allowed path writable | Investigate trust boundary |
| Test-AppLockerPolicy Allowed | AppLocker policy permits that file/user combination |
| Test-AppLockerPolicy Denied | AppLocker policy rejects that file/user combination |
| Policy allows but runtime blocks | Investigate additional controls |
| Policy denies but runtime succeeds | Investigate mode, identity and policy deployment |


# Finding Priority Matrix

| Observation | Priority |
|---|---|
| Enforced broad allow path with standard-user Modify | High review |
| Audit-only collection expected to enforce | High review |
| Missing required collection | Medium to high depending on threat model |
| Broad publisher rule | Review |
| Protected Windows path allowed | Usually expected |
| Protected Program Files path allowed | Usually expected |
| PowerShell installed | Informational |
| FullLanguage alone | Context required |
| DLL collection absent but WDAC enforces equivalent control | May be acceptable |
| Weak ACL mitigated only by app control | Underlying ACL should still be fixed |


# Defensible Assessment Model

```text
APPLICATION CONTROL PRESENT?
          |
      +---+---+
      |       |
     No      Yes
      |       |
      v       v
Review      Which Control?
Other          |
Controls       +--> AppLocker
               |
               +--> WDAC
               |
               +--> SRP
               |
               +--> Other
                       |
                       v
              Enforcement Mode?
                       |
                       v
                  Rule Scope?
                       |
                       v
                Trusted Resource
                       |
                       v
                 Protected ACL?
                       |
                  +----+----+
                  |         |
                 Yes        No
                  |         |
                  v         v
             Validate     Investigate
               Rule       Trust Gap
                  |
                  v
            Runtime Result
                  |
                  v
              Conclusion
```


# Final Testing Principle

Application-control assessment is not:

```text
Find an allowed executable
       |
       v
Report bypass
```

It is:

```text
IDENTIFY SECURITY POLICY
        |
        v
UNDERSTAND ENFORCEMENT
        |
        v
UNDERSTAND RULE
        |
        v
UNDERSTAND TRUSTED RESOURCE
        |
        v
CHECK FILESYSTEM SECURITY
        |
        v
TEST EFFECTIVE DECISION
        |
        v
CORRELATE RUNTIME BEHAVIOUR
        |
        v
IDENTIFY ACTUAL SECURITY GAP
```


# Final Questions

For every application-control assessment ask:

```text
Which control is active?

Is AppLocker present?

Is WDAC present?

Is SRP present?

What is the effective policy?

What is the local policy?

Are they different?

Which rule collections exist?

Which collections are enabled?

Which are audit-only?

Which are not configured?

Which users do the rules apply to?

Which groups do the rules apply to?

Which rules allow execution?

Which rules deny execution?

Are there rule exceptions?

Are path rules used?

Are publisher rules used?

Are hash rules used?

Which paths are trusted?

Can standard users modify those paths?

Can standard users modify any subdirectory?

Are the path ACLs inherited?

Does the rule apply to EXE files?

Does it apply to scripts?

Does it apply to MSI files?

Does it apply to DLL files?

Does it apply to packaged applications?

What does Test-AppLockerPolicy report?

Which rule matches the file?

Does runtime behaviour agree?

If runtime differs, which other control is responsible?

What does PowerShell language mode report?

Does PowerShell execution policy matter to this test?

Are AppLocker events recorded?

Are Code Integrity events recorded?

Is the collection enforced or only audited?

Does WDAC provide coverage absent from AppLocker?

Does a privileged service trust user-modifiable content?

Does a scheduled task trust user-modifiable content?

Does Registry configuration redirect execution?

Do filesystem ACLs undermine path-based trust?

Is an apparent application-control gap mitigated elsewhere?

Does the organisation's documented baseline require stronger coverage?

Can the issue be demonstrated using harmless files?

What evidence proves the effective security behaviour?

What is the root cause?

Should remediation occur in AppLocker, WDAC, filesystem ACLs or multiple layers?

Does remediation preserve required business applications?

Does the corrected policy produce the expected audit/block events?
```


# Effective Policy and Execution Validation

## Assessment Model

Application-control testing should distinguish each stage:

```text
Observation: policy exists
    -> Candidate: rule may apply to this user and file
    -> Validation: policy decision is allow, deny, or audit
    -> Actual execution behavior
    -> Evidence and security conclusion
```

An allowed binary is not automatically a finding. The question is whether the effective policy creates an unintended trust relationship, permits an unauthorised user to execute or modify a security-relevant resource, or fails to enforce a documented security requirement.

## AppLocker Coverage

Review the effective AppLocker policy and its collections:

```text
Executable
DLL
Script
Windows Installer
Packaged app / AppX
```

For each collection record enforcement mode, default rules, rule exceptions, user/group scope, and conditions based on path, publisher, or file hash. A default allow rule for protected Windows locations is materially different from a path rule covering a directory writable by standard users. Environment variables, wildcards, rule exceptions, and inherited policy should be resolved to the actual path and effective identity.

Use `Get-AppLockerPolicy -Effective`, `Test-AppLockerPolicy`, event logs, and approved harmless artifacts. Test the exact file as the relevant user rather than inferring behavior from a rule listing. Audit events establish that a decision was evaluated; an enforced block or controlled execution establishes runtime behavior.

## WDAC / App Control for Business

Determine whether Windows Defender Application Control or App Control for Business is active, which policy is effective, whether it is audit or enforced, and whether supplemental policies apply. Review signer, publisher, file-attribute, hash, managed-installer, policy rule, and user-mode code-integrity considerations where relevant. Do not treat the presence of a policy file or a policy identifier as proof that the expected policy is enforced.

Check Code Integrity and AppLocker event channels with the approved test artifact. A policy decision can be affected by signing state, catalog membership, path, reputation, policy version, reboot state, service state, and whether the tested component is actually covered by the policy type.

## Safe Controlled Test

Use a benign, uniquely named test executable or script built for the assessment and placed in an approved test directory. Test a protected path and a user-writable path only where explicitly authorised. Record the file hash, signer, path, user, collection, expected result, observed decision, event identifier, and whether the file actually ran. Do not use a trusted system binary to claim a bypass, and do not introduce unsigned code into production merely to create a denial.

Interpret results as follows:

| Result | Establishes | Does not establish |
|---|---|---|
| Policy is present | A policy is configured or discoverable | That it is effective or enforced |
| Rule matches | The tested rule condition applies | That execution occurred |
| Audit event appears | The policy evaluated the artifact | That execution was blocked |
| Execution is blocked | This tested path and identity were denied | That all equivalent file types are blocked |
| File executes | This specific request was allowed | That the policy is bypassed or insecure |

## Troubleshooting and False Positives

For conflicting results, check effective rather than local policy, collection enforcement, user/group scope, rule priority and exceptions, environment-variable expansion, wildcard matching, signer and hash changes, policy refresh, reboot requirements, AppLocker versus WDAC precedence, Defender or EDR interference, and whether the process was launched through another component. Repeat with the same hash and identity, then compare event logs with actual process creation.

## Evidence, Remediation, and Retesting

Capture the effective policy export or relevant redacted rule, collection and mode, user/group, artifact hash and signer, resolved path, command line, expected and observed decision, event records, and actual execution result. State clearly whether the evidence demonstrates policy coverage, a policy decision, runtime behavior, or a security boundary impact.

Remediation may include moving from audit to enforcement after compatibility testing, removing unsafe writable path rules, narrowing user/group scope, replacing broad wildcard or environment-variable rules, requiring trusted publishers or hashes, protecting default-rule locations, and aligning AppLocker, WDAC, Defender, and filesystem permissions. Retest all affected collections and identities with known-good applications, approved blocked artifacts, policy refresh, reboot-dependent behavior, and business-critical workflows.

# Related Windows Notes

- [Windows Overview](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [Windows PowerShell](powershell.md)
- [Windows Services](services.md)
- [Windows Scheduled Tasks](scheduled-tasks.md)
- [Windows Registry Security](registry.md)
- [Windows Filesystem Permissions](filesystem-permissions.md)
- [Windows Credentials](credentials.md)


# References

- [Microsoft Learn - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - AppLocker Policy](https://learn.microsoft.com/en-us/powershell/module/applocker/get-applockerpolicy){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Test-AppLockerPolicy](https://learn.microsoft.com/en-us/powershell/module/applocker/test-applockerpolicy){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - AppLocker Rule Condition Types](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/understanding-applocker-rule-condition-types){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - AppLocker Rules](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/working-with-applocker-rules){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Application Control for Business](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - PowerShell Language Modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - PowerShell Execution Policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - icacls](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Software Discovery](https://attack.mitre.org/techniques/T1518/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Always inspect the effective policy"

    Local AppLocker configuration may not represent the policy actually applied to the endpoint. Use the effective policy when determining rule collections, enforcement modes and policy decisions.


!!! tip "Correlate path rules with NTFS permissions"

    Path-based application control relies on filesystem trust. An allow rule for a protected Windows directory is very different from an allow rule covering a directory that standard users can modify.


!!! tip "Test exact files for exact users"

    Use `Test-AppLockerPolicy` with the relevant file and user rather than inferring the result from a broad rule listing. Capture the policy decision and matching rule as assessment evidence.


!!! tip "Check more than AppLocker"

    AppLocker may be only one part of the endpoint control architecture. WDAC, Code Integrity, Defender, ASR and endpoint security software can materially change runtime behaviour.


!!! warning "Audit mode is not enforcement"

    A configured AppLocker collection operating in `AuditOnly` mode provides telemetry but does not provide the same blocking boundary as an enforced collection.


!!! warning "Do not call every allowed Windows binary a bypass"

    Application-control policies intentionally permit legitimate applications. A meaningful security finding requires a weakness in the trust model, such as an unsafe writable trusted path, inappropriate rule scope or missing enforcement required by the security baseline.
