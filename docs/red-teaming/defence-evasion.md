---
title: Defence Evasion
description: Defence evasion testing methodology for authorised red team assessments, covering Microsoft Defender validation, EICAR, AMSI, PowerShell language modes, CLM, application control, AppLocker, WDAC, ASR, LOLBins, logging, telemetry, security-control validation, detection, evidence, cleanup, and remediation.
---

# Defence Evasion

Defence evasion describes techniques used to avoid, disable, bypass, or otherwise interfere with security controls.

During an authorised red team assessment, the objective should be to determine whether defensive controls:

```text
Prevent
Detect
Alert
Contain
Record
Respond
```

to relevant attacker behaviour.

A useful assessment model is:

```text
Security Control
      |
      v
Safe Validation
      |
      +--> Prevented
      |
      +--> Detected
      |
      +--> Allowed + Logged
      |
      +--> Allowed + Not Detected
```

The most important result is not whether a particular tool "bypasses Defender."

The important questions are:

```text
Which control was expected to stop the behaviour?
Was the control enabled?
Was the behaviour prevented?
Was telemetry generated?
Was an alert generated?
Did the SOC investigate?
What security boundary failed?
```

Defence evasion testing can affect endpoint protection, logging, application control, and other critical security controls.

Only perform testing explicitly permitted by the Rules of Engagement.


---

# Defence Evasion Objectives

Common assessment objectives include:

```text
Validate antivirus protection
Validate EDR prevention
Validate EDR detection
Validate Microsoft Defender
Validate AMSI integration
Validate PowerShell restrictions
Validate Constrained Language Mode
Validate application control
Validate AppLocker
Validate WDAC
Validate Attack Surface Reduction
Validate script controls
Validate LOLBin restrictions
Validate security logging
Validate tamper protection
Validate network protection
Validate cloud-delivered protection
Validate SOC visibility
```


---

# Defence Evasion Testing Model

```text
Identify Control
      |
      v
Determine Expected Behaviour
      |
      v
Select Safe Test
      |
      v
Execute
      |
      +------------------+
      |                  |
      v                  v
  Prevented            Allowed
      |                  |
      v                  v
 Was Alerted?        Was Logged?
      |                  |
      v                  v
Record Result       Was Alerted?
                         |
                         v
                    Record Result
```


---

# Test Controls Individually

Avoid immediately combining multiple techniques.

For example:

```text
PowerShell
   +
Obfuscation
   +
AMSI modification
   +
Application-control bypass
   +
Security-product tampering
```

may produce an interesting result but provides poor diagnostic information.

Prefer:

```text
Test 1 -> Antivirus

Test 2 -> AMSI

Test 3 -> PowerShell Language Mode

Test 4 -> AppLocker / WDAC

Test 5 -> ASR

Test 6 -> LOLBin policy

Test 7 -> Logging

Test 8 -> EDR visibility
```

This makes the root cause much easier to identify.


---

# Defence Evasion Control Stack

A Windows endpoint may contain several independent security layers.

```text
                     User Activity
                          |
                          v
                    PowerShell
                          |
                +---------+---------+
                |                   |
                v                   v
               AMSI            Language Mode
                |                   |
                +---------+---------+
                          |
                          v
                 Application Control
                          |
                  +-------+-------+
                  |               |
                  v               v
              AppLocker          WDAC
                  |
                  v
                ASR
                  |
                  v
        Microsoft Defender / EDR
                  |
                  v
               Logging
                  |
                  v
                 SIEM
                  |
                  v
                  SOC
```

One control allowing an action does not mean all other controls failed.


---

# Establish Security Context

Before testing, record:

```text
Hostname
Username
Privilege
PowerShell version
PowerShell language mode
Defender status
Defender versions
ASR configuration
AppLocker policy
WDAC status where available
Relevant EDR product
Network connectivity
```

Windows context:

```powershell
whoami /all
```

Hostname:

```powershell
hostname
```

PowerShell version:

```powershell
$PSVersionTable
```


---

# Microsoft Defender

Microsoft Defender Antivirus provides:

```text
Real-time protection
Signature-based detection
Behaviour monitoring
Cloud-delivered protection
AMSI integration
Network protection
Attack Surface Reduction
Tamper protection
EDR integration where licensed/configured
```


---

# Defender Status

Query:

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
                  NISEnabled,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```

The output should be recorded before testing.


---

# Defender Version

Useful version information:

```powershell
Get-MpComputerStatus |
    Select-Object AMEngineVersion,
                  AMProductVersion,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```

Version information can help reproduce results and determine whether signatures were current.


---

# Defender Preferences

Where permissions permit:

```powershell
Get-MpPreference
```

Relevant configuration may include:

```text
Exclusions
Cloud protection
Sample submission
Attack Surface Reduction
Network protection
Controlled folder access
PUA protection
```


---

# EICAR Antivirus Test

The EICAR Anti-Malware Test File is a standard harmless test file designed to verify antivirus detection.

It is not malware.

The canonical EICAR test string is:

```text
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

The complete test file should contain only that string.


---

# EICAR Test Purpose

EICAR can answer:

```text
Is antivirus active?
Does real-time protection inspect the file?
Is the file quarantined?
Is an alert generated?
Does the EDR record the event?
Does the SOC receive the alert?
```


---

# Create EICAR Test File with PowerShell

Use an authorised temporary directory.

```powershell
$eicar = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
Set-Content -Path "$env:TEMP\eicar.com.txt" -Value $eicar -NoNewline
```

If real-time protection is functioning, creation or subsequent access may be blocked or quarantined.


---

# Create EICAR with cmd.exe

The special characters in the EICAR string make shell quoting awkward.

PowerShell is generally easier for creating the test file accurately.

Verify only if the file remains present:

```powershell
Test-Path "$env:TEMP\eicar.com.txt"
```

If Defender immediately removes it, that is an expected successful prevention result.


---

# EICAR Expected Result

Typical successful control behaviour:

```text
EICAR Created
     |
     v
Antivirus Inspects File
     |
     v
Detection
     |
     v
Block / Quarantine
     |
     v
Security Alert
```


---

# EICAR Evidence

Record:

```text
Timestamp
Host
User
Defender state
Signature version
File path
Whether creation succeeded
Whether file remained present
Detection name
Defender alert
EDR alert
SOC response
```


---

# Defender Threat History

Where available:

```powershell
Get-MpThreatDetection
```

Useful fields:

```powershell
Get-MpThreatDetection |
    Select-Object InitialDetectionTime,
                  ThreatName,
                  Resources,
                  ActionSuccess
```

Depending on permissions and platform version, some information may not be available to a standard user.


---

# Defender Event Logs

Microsoft Defender Antivirus events can be reviewed under:

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

PowerShell:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 50
```

Filter around the assessment timestamp rather than exporting excessive logs.


---

# EICAR Is Not an EDR Test

EICAR primarily validates antivirus handling.

It does not demonstrate whether an EDR can detect:

```text
Credential access
Lateral movement
Persistence
PowerShell abuse
Process injection
C2
Identity attacks
Cloud attacks
```

Use behaviour-specific tests for those controls.


---

# AMSI

The Antimalware Scan Interface allows applications and scripting engines to submit content to registered antimalware products for inspection.

A simplified PowerShell model is:

```text
PowerShell Content
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

AMSI is an interface rather than an antivirus engine itself.


---

# AMSI Coverage

AMSI can be integrated into technologies including:

```text
PowerShell
Windows Script Host
JavaScript
VBScript
Office VBA
Applications implementing AMSI
```

Actual coverage depends on platform and application configuration.


---

# AMSI Validation

AMSI should be tested independently from an actual bypass.

A safe validation can use a known security-product test string designed for AMSI testing rather than deploying malicious code.

The goal is:

```text
Submit Known Test Content
        |
        v
Does AMSI Inspect It?
        |
        v
Does Defender Detect It?
```


---

# Microsoft AMSI Test String

Microsoft documents an AMSI sample test string for validating integration:

```text
AMSI Test Sample
```

Because vendor test strings and behaviour can change, use the test sample documented for the security product and platform being assessed rather than relying on copied offensive payloads.

The validation result should record:

```text
Content blocked
Content allowed
Defender event
EDR event
PowerShell event
SOC alert
```


---

# AMSI Bypass Assessment

AMSI bypass research evaluates whether a process can prevent or interfere with AMSI inspection.

Potential bypass categories historically include:

```text
Runtime state manipulation
Memory modification
Reflection-based manipulation
Provider interference
Content transformation
Host-specific weaknesses
Implementation weaknesses
```

A production assessment normally does not require deploying a working AMSI patch to demonstrate that AMSI is an important security boundary.

Prefer:

```text
AMSI test sample
        |
        v
Confirm Detection
        |
        v
Review Tamper / EDR Controls
        |
        v
Controlled Bypass Simulation if Explicitly Approved
```

Do not treat AMSI as the only defensive layer.


---

# AMSI Bypass Test Result Model

If bypass testing is explicitly authorised, record the control outcome rather than only stating "AMSI bypassed."

```text
AMSI Initially Detects Test
          |
          v
Controlled Bypass Attempt
          |
       +--+--+
       |     |
       v     v
    Blocked  Allowed
       |       |
       v       v
 EDR Alert?  AMSI Still
             Effective?
```

Useful findings include:

```text
AMSI bypass attempt prevented by EDR

AMSI modification allowed but generated high-confidence alert

AMSI inspection became ineffective without alert

AMSI bypass ineffective against current endpoint configuration
```


---

# AMSI Logging

Correlate AMSI-related tests with:

```text
PowerShell logs
Defender logs
EDR telemetry
Process creation
Script content
Security alerts
SOC investigation
```

Do not infer AMSI failure solely because a PowerShell command executed.


---

# PowerShell Security Controls

PowerShell security should be assessed as a collection of controls:

```text
Language Mode
AMSI
Script Block Logging
Module Logging
Transcription
Application Control
Execution Policy
Defender / EDR
ASR
Identity privilege
```


---

# PowerShell Language Mode

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Common results include:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```


---

# FullLanguage

`FullLanguage` provides normal PowerShell language capabilities.

Seeing:

```text
FullLanguage
```

is not automatically a vulnerability.

The security significance depends on:

```text
User privilege
Endpoint role
Application control
EDR
AMSI
Administrative model
Security requirements
```


---

# Constrained Language Mode

Constrained Language Mode restricts access to various PowerShell capabilities.

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Expected hardened endpoint result may be:

```text
ConstrainedLanguage
```

depending on the organisation's design.


---

# CLM Purpose

CLM is intended to reduce access to powerful PowerShell language capabilities in constrained environments.

Examples of affected capabilities can include:

```text
Arbitrary .NET type usage
COM access
Some reflection capabilities
Native API interaction through PowerShell
Custom type creation
```

Exact behaviour depends on PowerShell and platform version.


---

# CLM Validation

Test expected restrictions using harmless operations.

For example:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Then test whether creation of a harmless custom type is restricted:

```powershell
Add-Type -TypeDefinition 'public class CLMTest { public static string Value() { return "test"; } }'
```

Under an appropriately constrained environment, this type of operation may be restricted.

Record the actual result.


---

# CLM Bypass Assessment

CLM bypass testing asks whether a user constrained in one PowerShell environment can obtain an execution environment that provides capabilities outside the intended policy.

The assessment should distinguish:

```text
PowerShell process
        |
        v
ConstrainedLanguage

from

Different trusted execution path
        |
        v
Unexpected FullLanguage capability
```

The finding is not simply:

```text
PowerShell became FullLanguage.
```

The finding should explain which security boundary allowed that transition.


---

# CLM Bypass Categories

Historically relevant categories include:

```text
Alternative PowerShell hosts
Trusted binaries
Application-control policy gaps
Legacy PowerShell environments
Incorrect WDAC/AppLocker integration
Custom hosts
Misconfigured trusted paths
```

Do not assume a technique described in older research remains effective on a modern patched endpoint.


---

# Safe CLM Bypass Testing

A safe test methodology is:

```text
1. Confirm ConstrainedLanguage.

2. Confirm a harmless restricted operation fails.

3. Review application-control policy.

4. Identify approved execution hosts.

5. Test whether an approved host unexpectedly provides
   FullLanguage capabilities.

6. Repeat the harmless restricted operation.

7. Record EDR and PowerShell telemetry.

8. Stop when the control boundary is demonstrated.
```

There is no need to deploy a payload to prove a CLM control failure.


---

# CLM Finding Example

Weak:

```text
CLM bypass possible.
```

Better:

```text
PowerShell operated in ConstrainedLanguage mode for the standard
user. However, an application permitted by the endpoint
application-control policy launched a PowerShell runspace that
operated with FullLanguage capabilities.

A harmless custom-type test that was rejected in the constrained
session succeeded through the alternate execution path.
```


---

# CLM Remediation

Consider:

```text
WDAC
AppLocker
Removal of unnecessary script hosts
Removal of legacy PowerShell versions
Application allowlisting
EDR
Least privilege
PowerShell logging
Administrative tiering
```


---

# Execution Policy

PowerShell execution policy can be queried with:

```powershell
Get-ExecutionPolicy -List
```

Execution Policy is primarily a safety feature and should not be treated as a strong security boundary.

Do not report:

```text
ExecutionPolicy is Bypass
```

as a critical vulnerability without relevant context.


---

# PowerShell Script Block Logging

Check policy configuration where readable:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -ErrorAction SilentlyContinue
```

PowerShell Operational log:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 50
```

Script Block Logging can provide visibility into PowerShell activity.


---

# PowerShell Module Logging

Potential policy location:

```text
HKLM\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging
```

Check:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging' -ErrorAction SilentlyContinue
```


---

# PowerShell Transcription

Potential policy location:

```text
HKLM\Software\Policies\Microsoft\Windows\PowerShell\Transcription
```

Check:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue
```

Transcription can capture sensitive content, so storage permissions and retention should also be reviewed.


---

# Application Control

Application control restricts which software can execute.

Common Windows technologies include:

```text
AppLocker
Windows Defender Application Control
Software Restriction Policies
EDR application-control features
```


---

# AppLocker

AppLocker supports rule collections for:

```text
Executables
Windows Installer
Scripts
Packaged applications
DLLs
```

Retrieve the effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

Summarise collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType, EnforcementMode
```


---

# AppLocker Rule Collections

Possible results include:

```text
Exe
Msi
Script
Appx
Dll
```

Each collection can have its own enforcement state.

Do not assume DLL enforcement exists because EXE enforcement is enabled.


---

# AppLocker Test

AppLocker provides `Test-AppLockerPolicy`.

Example:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\wscript.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

The result can indicate whether the executable is expected to be allowed by policy.


---

# Test a File

For an existing harmless file:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path 'C:\Path\To\Test.exe' -User "$env:USERDOMAIN\$env:USERNAME"
```

Possible policy decisions can include:

```text
Allowed
Denied
DeniedByDefault
AllowedByDefault
```

Exact output depends on policy and platform.


---

# AppLocker Path Rules

Path rules deserve careful review.

Example:

```text
Allow:
%WINDIR%\*
```

The security question is not simply whether the wildcard exists.

Determine:

```text
Can a standard user write to a location covered by the allow rule?
```

The risky combination is:

```text
User-Writable Directory
        +
Allowed Path Rule
        =
Potential Application-Control Gap
```


---

# Writable Path Validation

Test directory permissions without placing an operational payload.

PowerShell:

```powershell
Get-Acl 'C:\Path\To\Directory' |
    Format-List Owner,AccessToString
```

A temporary write test can establish whether the current user can write there.

Use a unique temporary filename and remove it immediately after testing.


---

# AppLocker Policy Model

```text
Executable
    |
    v
Rule Collection Enabled?
    |
   / \
 No   Yes
 |     |
 v     v
No    Matching Rule?
Rule     |
       /   \
     No     Yes
     |       |
     v       v
 Default   Allow / Deny
 Action
```


---

# WDAC

Windows Defender Application Control provides stronger application-control capabilities based on Code Integrity policy.

Depending on configuration, WDAC can control:

```text
Executables
DLLs
Drivers
Scripts
Installers
Packaged applications
Managed code
```


---

# WDAC Assessment

Useful questions include:

```text
Is WDAC deployed?
Is policy enforced or audit-only?
Which signing policies are trusted?
Are user-writable paths trusted?
Are scripts covered?
Are DLLs covered?
Are managed applications covered?
Are supplemental policies present?
Is policy telemetry monitored?
```


---

# WDAC and CLM

PowerShell can integrate with application-control policy.

Conceptually:

```text
Application Control
       |
       v
PowerShell Trust Decision
       |
       v
Language Restrictions
```

This is why CLM should not be evaluated in isolation.


---

# Code Integrity Logs

Useful Windows logs include:

```text
Microsoft-Windows-CodeIntegrity/Operational
```

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 50
```

These events can help explain why execution was allowed or denied.


---

# AppLocker Logs

Relevant logs can include:

```text
Microsoft-Windows-AppLocker/EXE and DLL
Microsoft-Windows-AppLocker/MSI and Script
```

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 50
```

and:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/MSI and Script' -MaxEvents 50
```


---

# LOLBins

Living-off-the-land binaries are legitimate operating-system or signed applications that can expose functionality useful to attackers.

Examples often assessed include:

```text
PowerShell
cmd.exe
rundll32.exe
regsvr32.exe
mshta.exe
wscript.exe
cscript.exe
msbuild.exe
InstallUtil.exe
certutil.exe
bitsadmin.exe
curl.exe
schtasks.exe
sc.exe
wmic.exe
```

Availability varies by Windows version and installed components.


---

# LOLBin Testing

Do not treat:

```text
Binary Exists
```

as equivalent to:

```text
Security Control Bypass
```

A useful workflow is:

```text
Binary Exists
      |
      v
Can User Execute It?
      |
      v
Can It Perform Relevant Function?
      |
      v
Was Behaviour Allowed?
      |
      v
Was Behaviour Detected?
```


---

# Check Binary Presence

PowerShell:

```powershell
Get-Command rundll32.exe -ErrorAction SilentlyContinue
```

```powershell
Get-Command mshta.exe -ErrorAction SilentlyContinue
```

```powershell
Get-Command wscript.exe -ErrorAction SilentlyContinue
```

```powershell
Get-Command cscript.exe -ErrorAction SilentlyContinue
```


---

# Test AppLocker Decision for LOLBins

Example:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\rundll32.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

For `wscript.exe`:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\wscript.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

For `mshta.exe`:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\mshta.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```


---

# rundll32 Validation

`rundll32.exe` is a legitimate Windows component used to invoke exported functions from DLLs.

A harmless built-in validation can open a Control Panel component.

For example:

```powershell
& "$env:WINDIR\System32\rundll32.exe" "shell32.dll,Control_RunDLL" "main.cpl"
```

This demonstrates that `rundll32.exe` is executable without loading an assessment DLL.

Record:

```text
AppLocker decision
Process execution
EDR telemetry
Command-line telemetry
User context
```


---

# Windows Script Host

Windows Script Host includes:

```text
wscript.exe
cscript.exe
```

Application-control testing should distinguish:

```text
Executable allowed

from

Untrusted script allowed
```

For example, `wscript.exe` may be permitted while scripts from user-writable directories are denied.


---

# Harmless VBS Test

Create:

```powershell
'WScript.Echo "Assessment test"' | Set-Content "$env:TEMP\wscript-test.vbs"
```

Test policy:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:TEMP\wscript-test.vbs" -User "$env:USERDOMAIN\$env:USERNAME"
```

Cleanup:

```powershell
Remove-Item "$env:TEMP\wscript-test.vbs" -ErrorAction SilentlyContinue
```

This provides better evidence than assuming executable policy determines script policy.


---

# MSHTA

`mshta.exe` hosts HTML Applications.

Check:

```powershell
Get-Command mshta.exe -ErrorAction SilentlyContinue
```

Policy:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\mshta.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

For defence-evasion assessment, determine whether unnecessary script hosts are restricted and monitored.

There is no need to execute remote script content merely to establish the control state.


---

# MSBuild

MSBuild is a legitimate Microsoft build engine.

It may exist with Visual Studio, Build Tools, or .NET tooling.

Locate:

```powershell
Get-Command msbuild.exe -ErrorAction SilentlyContinue
```

If it exists, evaluate:

```text
Who can execute it?
Does application control permit it?
Is it required on the endpoint?
Is execution monitored?
```

Developer systems and build servers may legitimately require MSBuild.


---

# InstallUtil

`InstallUtil.exe` is associated with .NET Framework installer components.

Locate possible copies:

```powershell
Get-ChildItem "$env:WINDIR\Microsoft.NET\Framework*" -Filter InstallUtil.exe -Recurse -ErrorAction SilentlyContinue |
    Select-Object FullName
```

The existence of InstallUtil is not itself a vulnerability.

Evaluate policy and business requirement.


---

# certutil

`certutil.exe` is a legitimate certificate-management utility.

Check:

```powershell
Get-Command certutil.exe
```

It may be required for normal certificate administration.

Defensive monitoring should focus on unusual usage rather than simply blocking all execution without context.


---

# BITS

Background Intelligent Transfer Service supports asynchronous file transfers used by Windows and applications.

PowerShell exposes BITS functionality through commands such as:

```powershell
Get-Command *BitsTransfer*
```

BITS usage should be monitored in context.

Do not classify all BITS traffic as malicious.


---

# curl

Modern Windows systems may provide:

```powershell
curl.exe
```

Check:

```powershell
Get-Command curl.exe -ErrorAction SilentlyContinue
```

A download utility existing on a system does not itself constitute defence evasion.


---

# LOLBin Assessment Table

Maintain results such as:

| Binary | Present | Policy | Safe Test | Logged | Alerted |
|---|---|---|---|---|---|
| PowerShell | Yes | Allowed | Completed | Yes | No |
| rundll32 | Yes | Allowed | Completed | Yes | Yes |
| mshta | Yes | Denied | Not run | Yes | Yes |
| wscript | Yes | Allowed | Script denied | Yes | No |
| msbuild | No | N/A | N/A | N/A | N/A |


---

# Attack Surface Reduction

Microsoft Defender Attack Surface Reduction rules can restrict behaviours frequently associated with attacks.

Query configured rules:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```

The two arrays correspond by position.


---

# ASR Actions

Depending on configuration, ASR rules can operate in modes such as:

```text
Disabled
Block
Audit
Warn
```

Interpret results according to the current Microsoft documentation and endpoint configuration.


---

# ASR Validation

A useful workflow is:

```text
Enumerate Rules
      |
      v
Map Rule IDs to Names
      |
      v
Determine Mode
      |
      v
Select Safe Validation
      |
      v
Execute
      |
      v
Review Defender / EDR
```


---

# ASR Testing Principles

Do not test every ASR rule simply because it exists.

Focus on rules relevant to the endpoint role.

Examples:

```text
Office workstation
    |
    +--> Office child-process controls
    +--> Script controls
    +--> Credential protection

Developer workstation
    |
    +--> Script controls
    +--> Executable-content controls

Server
    |
    +--> Credential controls
    +--> Remote-management behaviour
```


---

# Network Protection

Microsoft Defender Network Protection can help restrict access to malicious or untrusted network destinations.

Query relevant Defender configuration through:

```powershell
Get-MpPreference
```

Network protection should be evaluated separately from host antivirus.


---

# Controlled Folder Access

Controlled Folder Access can protect designated directories against unauthorised modification by untrusted applications.

Relevant questions include:

```text
Is it enabled?
Which folders are protected?
Which applications are allowed?
Are block events visible?
Is it appropriate for the endpoint role?
```


---

# Tamper Protection

Tamper Protection helps protect security settings against unauthorised modification.

During a red team assessment, do not disable security products simply because the current account technically allows it.

Instead test:

```text
Can the current identity modify the security control?

Is the modification blocked?

Is an alert generated?
```

A safe validation should avoid leaving protection disabled.


---

# Defender Exclusions

Exclusions can significantly reduce antivirus visibility.

Where readable:

```powershell
(Get-MpPreference).ExclusionPath
```

Also review:

```powershell
(Get-MpPreference).ExclusionProcess
```

and:

```powershell
(Get-MpPreference).ExclusionExtension
```

Do not create an exclusion merely to demonstrate that administrators can configure Defender.


---

# Security Product Tampering

Potential tampering categories include:

```text
Stopping services
Changing configuration
Adding exclusions
Disabling protection
Modifying security components
Interfering with telemetry
Changing logging
```

These are high-impact actions.

Prefer testing whether the action is prevented or authorised without actually disabling protection.


---

# Safe Tamper Testing Model

```text
Security Setting
      |
      v
Current User Has Modification Permission?
      |
      +--> No
      |
      +--> Yes
              |
              v
        Tamper Protection?
              |
              v
        Modification Blocked?
```

Where possible, use policy inspection rather than changing the setting.


---

# Security Logging

Defence evasion is not only about prevention.

An action may be allowed but fully visible.

```text
Technique
   |
   +--> Prevented
   |
   +--> Detected
   |
   +--> Logged
   |
   +--> Invisible
```

The last case is generally the most concerning.


---

# Windows Process Creation

Security Event ID:

```text
4688
```

can record process creation when the relevant audit policy is enabled.

Useful fields can include:

```text
New process
Parent process
User
Command line
Timestamp
```


---

# Sysmon

Where deployed, Sysmon can provide telemetry such as:

```text
Process creation
Network connections
File creation
Registry changes
Process access
Image loading
DNS queries
```

Configuration quality is critical.

Installing Sysmon is not equivalent to monitoring all attacker behaviour.


---

# Event Log Validation

Review relevant logs around the assessment timestamp.

Example:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

Access to the Security log may require elevated privileges.


---

# EDR Validation

EDR testing should evaluate the complete detection lifecycle.

```text
Activity
   |
   v
Endpoint Sensor
   |
   v
Telemetry
   |
   v
Detection Logic
   |
   v
Alert
   |
   v
SOC
   |
   v
Investigation
   |
   v
Response
```

An endpoint alert that nobody investigates is not the same as an effective detection-and-response process.


---

# EDR Test Categories

Useful safe categories include:

```text
EICAR antivirus test
Known vendor simulation tests
PowerShell test activity
Scheduled-task test
Service-creation test
Harmless remote administration
Known test process trees
Controlled authentication activity
Atomic simulation tests approved by the organisation
```


---

# Atomic Red Team

Atomic Red Team provides small tests mapped to MITRE ATT&CK techniques.

It can be useful for controlled detection validation.

Before running an atomic test:

```text
Read the test
Understand prerequisites
Understand commands
Understand cleanup
Confirm scope
Confirm expected impact
Run one test
Review telemetry
Run cleanup
Verify cleanup
```

Never bulk-run a large set of tests against production endpoints without review.


---

# Obfuscation

Attackers may transform commands or scripts to make static analysis more difficult.

Examples conceptually include:

```text
Encoding
String construction
Variable substitution
Whitespace changes
Command aliases
Dynamic resolution
Nested interpreters
```

For defence validation, start with transparent test content.

Only introduce controlled transformations when the objective specifically requires testing detection resilience.


---

# Obfuscation Testing Model

```text
Plain Test
    |
    v
Detected?
    |
   Yes
    |
    v
Controlled Transformation
    |
    v
Still Detected?
```

This isolates whether detection relies only on a simple static signature.


---

# Behaviour vs Signature

A resilient defensive strategy should not depend entirely on one exact string.

```text
Signature Detection
       +
Behaviour Detection
       +
Identity Analytics
       +
Network Telemetry
       +
Application Control
       =
Layered Defence
```


---

# File Reputation

Some security products use:

```text
File hash
Digital signature
Prevalence
Cloud reputation
Download origin
Mark of the Web
Behaviour
```

A newly compiled harmless executable may therefore be treated differently from a common signed application.


---

# Mark of the Web

Files downloaded from external locations may receive zone information.

This can influence:

```text
SmartScreen
Office behaviour
Script execution
Security warnings
Application behaviour
```

Assessment results should record how the file reached the endpoint because delivery context can change security behaviour.


---

# SmartScreen

Microsoft Defender SmartScreen provides reputation-based protection for certain downloaded content and web activity.

Do not confuse:

```text
SmartScreen
Defender Antivirus
EDR
AMSI
ASR
Application Control
```

They are separate defensive components.


---

# Application Allowlisting Gap

A useful application-control assessment model is:

```text
Allowed Binary
      |
      v
Expected Business Use?
    /       \
  Yes        No
  |           |
  v           v
Required    Consider Restriction
  |
  v
Can It Execute
Untrusted Content?
  |
  v
Is Behaviour Controlled?
```

The presence of a dual-use binary alone is insufficient evidence.


---

# Trusted Path Assessment

A potentially dangerous configuration is:

```text
Trusted Path
    +
Standard User Write Access
```

Assessment:

```text
Trusted Directory
      |
      v
Check ACL
      |
      v
User Writable?
   /       \
 No         Yes
 |           |
 v           v
Good      Safe Write Test
              |
              v
       Application Control
       Allows Content?
```


---

# Safe Writable Directory Test

PowerShell:

```powershell
$folder = 'C:\Path\To\Candidate'
$file = Join-Path $folder "write-test-$PID.tmp"

try {
    New-Item -ItemType File -Path $file -ErrorAction Stop | Out-Null
    Write-Host '[+] Write succeeded'
}
catch {
    Write-Host '[-] Write failed'
}
finally {
    Remove-Item $file -ErrorAction SilentlyContinue
}
```

This demonstrates write access without leaving an executable.


---

# DLL Application Control

DLL rule enforcement should be reviewed separately from executable enforcement.

AppLocker may have:

```text
EXE: Enabled

DLL: NotConfigured
```

This is a policy observation.

Whether it represents a material security weakness depends on the intended application-control design and other controls such as WDAC and EDR.


---

# Script Application Control

Script controls should be tested independently.

Potential script types include:

```text
PowerShell
VBScript
JScript
Batch
Command files
```

A policy that blocks executables from a directory may not necessarily provide identical coverage for scripts.


---

# Office Security Controls

On endpoints with Microsoft Office, defence-evasion testing may include validation of:

```text
Macro policy
Mark of the Web
Protected View
ASR
Child-process restrictions
Application control
AMSI integration
EDR
```

Use harmless documents and vendor-supported simulations.


---

# Credential Protection

Defence evasion intersects with credential access when an attacker attempts to interfere with controls protecting authentication material.

Relevant defensive technologies include:

```text
Credential Guard
LSA protection
Defender
EDR
ASR
Application control
Administrative tiering
```


---

# Credential Guard

Credential Guard should be evaluated as part of a layered credential-protection strategy.

Do not report its absence as a vulnerability by itself.

The important question is whether sensitive credentials are sufficiently protected against the assessed threat model.


---

# LSA Protection

LSA protection can make unauthorised access to LSASS more difficult.

Assessment should focus on:

```text
Is protection configured?
Can inappropriate processes access LSASS?
Was access blocked?
Was access detected?
```


---

# Firewall Evasion vs Network Validation

Avoid treating every permitted outbound connection as "firewall bypass."

A more accurate model is:

```text
Destination
    |
    v
Protocol
    |
    v
Firewall Policy
    |
    +--> Explicitly Allowed
    |
    +--> Explicitly Blocked
    |
    +--> Unrestricted
```

If outbound HTTP is intentionally allowed, successfully reaching an HTTP server does not constitute bypassing the firewall.


---

# Connectivity Test

PowerShell:

```powershell
Test-NetConnection HOST -Port 443
```

This confirms TCP reachability only.


---

# HTTP Test

PowerShell:

```powershell
Invoke-WebRequest -Uri 'https://example.com/' -UseBasicParsing
```

Use an assessment-controlled or otherwise approved destination when validating egress controls.


---

# DNS Controls

DNS can provide useful defensive telemetry.

Review:

```text
DNS query logs
Resolver policy
Filtering
Unexpected domains
Newly registered domains
Dynamic DNS
Internal DNS activity
```


---

# Proxy Controls

Corporate proxies may provide:

```text
URL filtering
Authentication
TLS inspection
Category filtering
Logging
Malware scanning
DLP
```

Defence-evasion testing should determine whether alternative network paths undermine the intended proxy policy.


---

# Security Control Bypass Terminology

Use precise language.

Instead of:

```text
Defender bypassed
```

consider:

```text
The test file was not detected by Microsoft Defender Antivirus.
```

Instead of:

```text
AppLocker bypassed
```

consider:

```text
A standard user could execute the test application from a
user-writable path covered by an AppLocker allow rule.
```

Instead of:

```text
CLM bypassed
```

consider:

```text
An AppLocker-permitted execution path provided FullLanguage
PowerShell capabilities to a user whose interactive PowerShell
session was restricted to ConstrainedLanguage.
```


---

# Candidate vs Confirmed

## Candidate

A potential defensive gap is identified.

Examples:

```text
LOLBin allowed
DLL collection not configured
FullLanguage available
Writable allowed directory
Security logging appears incomplete
```


## Likely

The configuration appears capable of enabling behaviour outside the intended defensive model.


## Confirmed

A controlled, non-destructive test demonstrates that the intended security control can be circumvented or does not provide the expected protection.


---

# Severity

Severity depends on:

```text
User privilege
Control bypassed
Endpoint role
Attack path
Security layers remaining
Required prerequisites
Detection
Repeatability
Business impact
Ability to chain techniques
```

For example:

```text
FullLanguage PowerShell
```

on a developer workstation may be expected.

The same capability on a tightly controlled kiosk or privileged access workstation may be much more significant.


---

# Defence Evasion Evidence

For each test record:

```text
Timestamp
Hostname
Username
Privilege
Security control
Control configuration
Expected result
Test performed
Actual result
Prevention result
Detection result
EDR result
SOC result
Cleanup
```


---

# Example EICAR Evidence

```text
Test:
EICAR

Host:
TEST-WKS01

User:
CORP\test-user

Defender:
Real-time protection enabled

Result:
File creation detected and quarantined

EDR:
Alert generated

SOC:
Alert investigated

Assessment:
Control operating as expected
```


---

# Example CLM Evidence

```text
Initial Language Mode:
ConstrainedLanguage

Restricted Operation:
Harmless Add-Type test

Initial Result:
Blocked

Alternate Approved Host:
Tested

Result:
FullLanguage available

Restricted Operation:
Succeeded

EDR:
Process recorded but no alert

Assessment:
Application-control policy allowed an execution path that weakened
the intended PowerShell restriction
```


---

# Example AppLocker Evidence

```text
Collection:
Exe

Enforcement:
Enabled

Candidate Path:
C:\ProgramData\CandidateFolder

ACL:
Standard users had write access

Policy:
Path covered by allow rule

Safe Test:
Assessment executable allowed

Result:
Confirmed application-control gap
```


---

# Example LOLBin Evidence

```text
Binary:
rundll32.exe

User:
Standard domain user

AppLocker:
Allowed

Safe Action:
Opened built-in Control Panel component

Execution:
Successful

EDR:
Process and command line recorded

Alert:
None

Assessment:
Binary executable as expected. Additional business context required
before classifying this as a security finding.
```


---

# Defence Evasion Finding Structure

```text
Title
Severity
Affected Systems
Security Control
Expected Behaviour
Observed Configuration
Test Method
Result
Attack Path
Detection
Impact
Evidence
Remediation
References
```


---

# Remediation Model

```text
Confirmed Gap
     |
     v
Identify Root Cause
     |
     +--> Policy
     |
     +--> Permissions
     |
     +--> Missing Control
     |
     +--> Monitoring
     |
     +--> Legacy Component
     |
     +--> Excessive Trust
     |
     v
Apply Hardening
     |
     v
Repeat Same Test
     |
     v
Prevented / Detected?
     |
     v
Close Finding
```


---

# Application Control Recommendations

Depending on environment:

```text
Deploy WDAC where appropriate
Strengthen AppLocker policy
Avoid writable trusted paths
Configure relevant rule collections
Restrict unnecessary interpreters
Restrict unnecessary LOLBins
Use publisher/signing rules where appropriate
Monitor Code Integrity events
Use audit mode before enforcement rollout
```


---

# PowerShell Recommendations

Potential controls include:

```text
Application control
Constrained Language Mode where appropriate
AMSI
Script Block Logging
Module Logging
Protected event logging
Transcription where appropriate
PowerShell 7 lifecycle management
Removal of obsolete PowerShell versions
EDR
Least privilege
```


---

# Defender Recommendations

Potential improvements include:

```text
Real-time protection
Cloud-delivered protection
Behaviour monitoring
Tamper Protection
ASR
Network Protection
Controlled Folder Access where appropriate
EDR integration
Central alerting
Current security intelligence
Minimal exclusions
```


---

# LOLBin Recommendations

Do not blindly block every signed Windows utility.

Instead:

```text
Determine business requirement
Restrict where unnecessary
Apply application control
Monitor unusual command lines
Monitor parent-child relationships
Monitor network behaviour
Restrict standard-user execution where justified
Use ASR and EDR
```


---

# Detection Engineering

A mature defence should combine:

```text
Process
   +
Command Line
   +
Identity
   +
File
   +
Registry
   +
Network
   +
Authentication
   +
Application Control
   +
Threat Intelligence
```

rather than relying solely on executable names.


---

# Defence Evasion Testing Checklist

## Context

- [ ] Written authorisation confirmed
- [ ] Defence-evasion testing permitted
- [ ] Security-product tampering rules understood
- [ ] Endpoint role understood
- [ ] Current user known
- [ ] Current privilege known
- [ ] EDR product identified
- [ ] Emergency contact known

## Defender

- [ ] Antivirus state recorded
- [ ] Real-time protection recorded
- [ ] Behaviour monitoring recorded
- [ ] Engine version recorded
- [ ] Signature version recorded
- [ ] Signature age reviewed
- [ ] Exclusions reviewed where permitted
- [ ] EICAR tested
- [ ] Defender event recorded
- [ ] EDR alert recorded
- [ ] SOC response recorded

## AMSI

- [ ] AMSI integration considered
- [ ] Safe AMSI test considered
- [ ] Defender response recorded
- [ ] PowerShell response recorded
- [ ] EDR response recorded
- [ ] Bypass testing only if explicitly approved
- [ ] AMSI not treated as sole security boundary

## PowerShell

- [ ] PowerShell version recorded
- [ ] Language mode recorded
- [ ] Execution policy recorded
- [ ] CLM restrictions tested safely
- [ ] CLM boundary reviewed
- [ ] Script Block Logging considered
- [ ] Module Logging considered
- [ ] Transcription considered
- [ ] PowerShell Operational logs reviewed

## Application Control

- [ ] AppLocker effective policy reviewed
- [ ] Rule collections reviewed
- [ ] Enforcement modes reviewed
- [ ] DLL policy reviewed
- [ ] Script policy reviewed
- [ ] Writable allowed paths considered
- [ ] WDAC considered
- [ ] Code Integrity logs reviewed
- [ ] Safe test executable used where appropriate

## LOLBins

- [ ] PowerShell considered
- [ ] rundll32 considered
- [ ] regsvr32 considered
- [ ] mshta considered
- [ ] wscript considered
- [ ] cscript considered
- [ ] msbuild considered
- [ ] InstallUtil considered
- [ ] certutil considered
- [ ] BITS considered
- [ ] curl considered
- [ ] Business requirements considered
- [ ] Safe validation used

## ASR

- [ ] ASR rules enumerated
- [ ] IDs mapped to rules
- [ ] Modes recorded
- [ ] Relevant rules selected
- [ ] Safe tests used
- [ ] Defender events reviewed
- [ ] EDR alerts reviewed

## Logging

- [ ] Process creation considered
- [ ] PowerShell logs considered
- [ ] Defender logs considered
- [ ] AppLocker logs considered
- [ ] Code Integrity logs considered
- [ ] Sysmon considered
- [ ] Network telemetry considered
- [ ] SIEM visibility considered

## Evidence

- [ ] Timestamp recorded
- [ ] Host recorded
- [ ] User recorded
- [ ] Privilege recorded
- [ ] Control configuration recorded
- [ ] Expected result recorded
- [ ] Actual result recorded
- [ ] Prevention recorded
- [ ] Detection recorded
- [ ] SOC response recorded

## Cleanup

- [ ] EICAR artifacts removed or quarantined
- [ ] Test scripts removed
- [ ] Test executables removed
- [ ] Temporary files removed
- [ ] Configuration unchanged
- [ ] Security controls remain enabled
- [ ] No exclusions added
- [ ] No persistent artifacts remain
- [ ] Cleanup verified


---

# Defence Evasion Decision Model

```text
                    Security Control
                          |
                          v
                   Control Enabled?
                     /        \
                   No          Yes
                   |            |
                   v            v
              Document      Safe Test
                               |
                               v
                         Action Prevented?
                           /        \
                         Yes         No
                         |            |
                         v            v
                    Alerted?       Logged?
                    /    \          /   \
                  Yes     No      Yes    No
                   |       |       |      |
                   v       v       v      v
                Record   Record  Alert?  High
                                  |      Priority
                               +--+--+
                               |     |
                              Yes    No
                               |      |
                               v      v
                            Record  Detection
                                     Gap
```


---

# Layered Defence Model

```text
                     User / Process
                          |
                          v
                    Least Privilege
                          |
                          v
                  Application Control
                          |
                          v
                     PowerShell
                     Restrictions
                          |
                          v
                         AMSI
                          |
                          v
                    Defender / EDR
                          |
                          v
                         ASR
                          |
                          v
                  Network Controls
                          |
                          v
                       Logging
                          |
                          v
                        SIEM
                          |
                          v
                         SOC
                          |
                          v
                       Response
```

A mature environment does not depend on one layer being perfect.


---

# Safe Testing Progression

```text
Configuration Review
        |
        v
Harmless Built-in Test
        |
        v
Vendor Test Artifact
        |
        v
Known Simulation
        |
        v
Controlled Technique Test
        |
        v
Bypass Simulation
        |
        v
Stop When Objective Proven
```

Move down the progression only when required by the assessment objective.


---

# Quick Reference

## Security Context

```powershell
whoami /all
```

```powershell
$PSVersionTable
```

## PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

## Execution Policy

```powershell
Get-ExecutionPolicy -List
```

## Defender Status

```powershell
Get-MpComputerStatus
```

## Defender Versions

```powershell
Get-MpComputerStatus |
    Select-Object AMEngineVersion,
                  AMProductVersion,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```

## Defender Preferences

```powershell
Get-MpPreference
```

## Defender Threat Detections

```powershell
Get-MpThreatDetection
```

## EICAR

```powershell
$eicar = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
Set-Content -Path "$env:TEMP\eicar.com.txt" -Value $eicar -NoNewline
```

## Defender Operational Log

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 50
```

## AppLocker

```powershell
Get-AppLockerPolicy -Effective
```

## AppLocker Collections

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType, EnforcementMode
```

## AppLocker Test

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\rundll32.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

## Code Integrity

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 50
```

## AppLocker EXE/DLL Log

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 50
```

## AppLocker Script Log

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/MSI and Script' -MaxEvents 50
```

## ASR

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```

## PowerShell Operational Log

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 50
```

## Script Block Logging Policy

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -ErrorAction SilentlyContinue
```

## Module Logging Policy

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging' -ErrorAction SilentlyContinue
```

## Transcription Policy

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue
```

## LOLBin Presence

```powershell
Get-Command rundll32.exe,mshta.exe,wscript.exe,cscript.exe,certutil.exe,curl.exe -ErrorAction SilentlyContinue
```

## rundll32 Harmless Test

```powershell
& "$env:WINDIR\System32\rundll32.exe" "shell32.dll,Control_RunDLL" "main.cpl"
```

## Harmless VBS Test

```powershell
'WScript.Echo "Assessment test"' | Set-Content "$env:TEMP\wscript-test.vbs"
```

## VBS Policy Test

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:TEMP\wscript-test.vbs" -User "$env:USERDOMAIN\$env:USERNAME"
```

## Connectivity

```powershell
Test-NetConnection HOST -Port 443
```


---

# Final Testing Model

```text
                 Establish Context
                        |
                        v
                 Enumerate Controls
                        |
                        v
                Record Configuration
                        |
                        v
                 Safe Test Artifact
                        |
                        v
                  Was Prevented?
                   /          \
                 Yes           No
                 |              |
                 v              v
             Detection?      Telemetry?
                 |              |
                 v              v
               Record        Alert?
                                |
                                v
                         Control Objective
                              Met?
                           /       \
                         Yes        No
                         |           |
                         v           v
                       STOP      Controlled
                                 Additional
                                   Test
                                    |
                                    v
                             Objective Proven
                                    |
                                    v
                                  STOP
                                    |
                                    v
                                 Cleanup
```


---

# Related Notes

- [Red Teaming](./)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Windows](../windows/)
- [PowerShell](../windows/powershell.md)
- [Windows Privilege Escalation](../windows/privilege-escalation.md)
- [Windows PrivEsc Explorer](../privesc/windows/)
- [Active Directory](../active-directory/)
- [Credential Access - AD](../active-directory/credential-access.md)
- [Lateral Movement - AD](../active-directory/lateral-movement.md)


---

# References

- [MITRE ATT&CK - Defense Evasion](https://attack.mitre.org/tactics/TA0005/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Impair Defenses](https://attack.mitre.org/techniques/T1562/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Binary Proxy Execution](https://attack.mitre.org/techniques/T1218/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Obfuscated Files or Information](https://attack.mitre.org/techniques/T1027/){ target="_blank" rel="noopener noreferrer" }
- [EICAR - Anti-Malware Test File](https://www.eicar.org/download-anti-malware-testfile/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Microsoft Defender Antivirus](https://learn.microsoft.com/defender-endpoint/microsoft-defender-antivirus-windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Defender Antivirus event IDs](https://learn.microsoft.com/defender-endpoint/troubleshoot-microsoft-defender-antivirus){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Antimalware Scan Interface](https://learn.microsoft.com/windows/win32/amsi/antimalware-scan-interface-portal){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Constrained Language Mode](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Script Block Logging](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_logging_windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - App Control for Business / WDAC](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Attack Surface Reduction](https://learn.microsoft.com/defender-endpoint/attack-surface-reduction){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Attack Surface Reduction rules reference](https://learn.microsoft.com/defender-endpoint/attack-surface-reduction-rules-reference){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Defender Application Control and PowerShell](https://learn.microsoft.com/powershell/scripting/security/app-control/application-control){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Sysmon](https://learn.microsoft.com/sysinternals/downloads/sysmon){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Defence-evasion testing interacts directly with endpoint security controls. Start with configuration review, harmless built-in actions, EICAR, vendor-provided test artifacts, and controlled simulations. Do not disable antivirus, EDR, logging, application control, AMSI, or other security controls unless the Rules of Engagement explicitly require and permit that action. CLM and AMSI bypass testing should demonstrate the control boundary with the minimum necessary action rather than deploying an operational payload. Record the original security state, correlate every test with defensive telemetry, stop when the objective is proven, and verify that all security controls remain enabled after testing.
