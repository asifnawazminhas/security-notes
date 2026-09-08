---
title: Microsoft Defender Security Assessment
description: Practical Microsoft Defender Antivirus and endpoint security assessment covering protection status, configuration, exclusions, cloud protection, tamper protection, Attack Surface Reduction rules, event logging, evidence collection, remediation and retesting.
---

# Microsoft Defender Security Assessment

Microsoft Defender Antivirus is the built-in antimalware component of modern Windows and forms part of the broader Microsoft endpoint security architecture.

A Windows security assessment should determine more than whether Defender is simply:

```text
Running
```

The objective is to understand the effective protection posture:

```text
Is Defender active?

Is real-time protection enabled?

Is behavior monitoring enabled?

Is cloud-delivered protection enabled?

Is tamper protection enabled?

Are exclusions configured?

Are Attack Surface Reduction rules configured?

Are protections enforced or only audited?

Are security events generated?

Can standard users alter important settings?

Are application-control and Defender controls working together?
```

!!! warning "Authorised Security Testing"

    Perform endpoint security assessment only on systems included in the authorised scope. Prefer configuration inspection, harmless validation files and event-log analysis. Do not disable Defender, tamper protection, EDR, cloud protection or other endpoint controls simply to demonstrate that they can be changed.


# Defender Security Model

A simplified endpoint security model is:

```text
File / Process / Script
          |
          v
Microsoft Defender
          |
          +--> Antivirus
          |
          +--> Real-Time Protection
          |
          +--> Behavior Monitoring
          |
          +--> Cloud Protection
          |
          +--> Network Protection
          |
          +--> Attack Surface Reduction
          |
          +--> Controlled Folder Access
          |
          +--> Endpoint Detection
          |
          v
Allow / Audit / Block / Quarantine
```


# Defense in Depth

Defender should be considered alongside:

```text
Windows Defender Application Control

AppLocker

Attack Surface Reduction

Windows Firewall

Credential Guard

Exploit Protection

SmartScreen

EDR

Secure NTFS permissions

Least privilege
```


# Assessment Model

Use the following approach:

```text
IDENTIFY SECURITY PRODUCT
        |
        v
CHECK DEFENDER STATUS
        |
        v
CHECK ANTIVIRUS CONFIGURATION
        |
        v
CHECK EXCLUSIONS
        |
        v
CHECK CLOUD PROTECTION
        |
        v
CHECK ASR
        |
        v
CHECK NETWORK PROTECTION
        |
        v
CHECK TAMPER PROTECTION
        |
        v
CHECK LOGGING
        |
        v
VALIDATE SAFELY
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


# Establish Current Context

Start with:

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


# Why User Context Matters

Some Defender information can be queried by standard users while other configuration details or changes require administrative privileges.

Record the context under which every test was performed.


# PowerShell Version

```powershell
$PSVersionTable
```


# Defender PowerShell Module

List available Defender commands:

```powershell
Get-Command -Module Defender -ErrorAction SilentlyContinue
```


# Common Defender Cmdlets

Typical cmdlets include:

```text
Get-MpComputerStatus

Get-MpPreference

Get-MpThreat

Get-MpThreatDetection

Start-MpScan

Update-MpSignature
```


# Defender Computer Status

The primary status command is:

```powershell
Get-MpComputerStatus
```


# Selected Status

```powershell
Get-MpComputerStatus |
    Select-Object AMServiceEnabled,
                  AntispywareEnabled,
                  AntivirusEnabled,
                  BehaviorMonitorEnabled,
                  IoavProtectionEnabled,
                  NISEnabled,
                  OnAccessProtectionEnabled,
                  RealTimeProtectionEnabled,
                  IsTamperProtected,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```


# Example

```text
AMServiceEnabled              : True
AntispywareEnabled            : True
AntivirusEnabled              : True
BehaviorMonitorEnabled        : True
IoavProtectionEnabled         : True
NISEnabled                    : True
OnAccessProtectionEnabled     : True
RealTimeProtectionEnabled     : True
IsTamperProtected             : True
AntivirusSignatureVersion     : ...
AntivirusSignatureLastUpdated : ...
```


# Interpretation

A healthy configuration will generally show the expected protection components enabled according to the organisation's endpoint security baseline.

Do not rely on a single property.


# AMServiceEnabled

```text
AMServiceEnabled
```

indicates whether the Microsoft antimalware service is enabled.


# AntivirusEnabled

```text
AntivirusEnabled
```

indicates Defender Antivirus status.


# RealTimeProtectionEnabled

```text
RealTimeProtectionEnabled
```

is particularly important because it indicates whether real-time protection is active.


# BehaviorMonitorEnabled

```text
BehaviorMonitorEnabled
```

indicates whether behavior monitoring is enabled.


# IoavProtectionEnabled

This relates to scanning files obtained through Internet-aware applications and attachment-related mechanisms.


# NISEnabled

```text
NISEnabled
```

relates to Network Inspection System functionality.


# Tamper Protection

Check:

```powershell
(Get-MpComputerStatus).IsTamperProtected
```


# Example

```text
True
```


# Security Purpose

Tamper protection helps prevent unauthorised changes to important Microsoft Defender security settings.


# Important

Do not attempt to disable tamper protection during ordinary assessment validation.

Instead document:

```text
Enabled

Disabled

Unavailable / unable to determine
```


# Defender Preferences

Retrieve Defender configuration:

```powershell
Get-MpPreference
```


# Important Properties

A focused view:

```powershell
Get-MpPreference |
    Select-Object DisableRealtimeMonitoring,
                  DisableBehaviorMonitoring,
                  DisableIOAVProtection,
                  DisableScriptScanning,
                  MAPSReporting,
                  SubmitSamplesConsent,
                  DisableBlockAtFirstSeen,
                  DisableArchiveScanning,
                  DisableEmailScanning,
                  DisableRemovableDriveScanning,
                  PUAProtection,
                  EnableNetworkProtection
```


# Negative Boolean Names

Many Defender properties use names such as:

```text
DisableRealtimeMonitoring
```

This can be confusing.

For example:

```text
DisableRealtimeMonitoring = False
```

means real-time monitoring is not disabled.


# Interpretation Model

```text
DisableRealtimeMonitoring = False
             |
             v
Real-Time Monitoring Enabled
```


# Real-Time Protection

Check both status and preference information:

```powershell
Get-MpComputerStatus |
    Select-Object RealTimeProtectionEnabled
```

and:

```powershell
Get-MpPreference |
    Select-Object DisableRealtimeMonitoring
```


# Why Use Both?

One represents observed status while the other represents configuration.

This helps identify situations where:

```text
Configured state
```

and:

```text
Runtime state
```

do not align.


# Behavior Monitoring

```powershell
Get-MpComputerStatus |
    Select-Object BehaviorMonitorEnabled
```


# Preference

```powershell
Get-MpPreference |
    Select-Object DisableBehaviorMonitoring
```


# Script Scanning

```powershell
Get-MpPreference |
    Select-Object DisableScriptScanning
```


# Interpretation

```text
False
```

normally means script scanning has not been disabled through that preference.


# Archive Scanning

```powershell
Get-MpPreference |
    Select-Object DisableArchiveScanning
```


# Removable Drive Scanning

```powershell
Get-MpPreference |
    Select-Object DisableRemovableDriveScanning
```


# Potentially Unwanted Application Protection

Check:

```powershell
Get-MpPreference |
    Select-Object PUAProtection
```


# Cloud-Delivered Protection

Microsoft Defender can use cloud-delivered protection to improve detection and response against emerging threats.


# MAPS Reporting

```powershell
Get-MpPreference |
    Select-Object MAPSReporting
```


# Sample Submission

```powershell
Get-MpPreference |
    Select-Object SubmitSamplesConsent
```


# Block at First Sight

```powershell
Get-MpPreference |
    Select-Object DisableBlockAtFirstSeen
```


# Important

Interpret these values against Microsoft's current documentation and the organisation's intended security baseline rather than assuming that every numeric value has the same meaning across all versions.


# Signature Information

Check:

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated,
                  AntispywareSignatureVersion,
                  AntispywareSignatureLastUpdated
```


# Signature Age

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusSignatureAge,
                  AntispywareSignatureAge
```


# Why Signature Freshness Matters

Outdated security intelligence may reduce the endpoint's ability to detect known threats.

However, modern Defender protection also incorporates cloud and behavior-based capabilities, so signature age should not be treated as the entire protection model.


# Defender Version Information

```powershell
Get-MpComputerStatus |
    Select-Object AMProductVersion,
                  AMEngineVersion,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```


# Example Evidence

Capture:

```text
Product version

Engine version

Security intelligence version

Last update time
```


# Defender Service

Check:

```powershell
Get-Service WinDefend -ErrorAction SilentlyContinue
```


# Example

```text
Status   Name       DisplayName
------   ----       -----------
Running  WinDefend  Microsoft Defender Antivirus Service
```


# Important

A running service alone does not prove all security features are correctly configured.


# Security Center

On supported client systems, Windows Security Center can provide information about registered security products.


# Query Antivirus Products

```powershell
Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -ErrorAction SilentlyContinue |
    Select-Object displayName,pathToSignedProductExe,pathToSignedReportingExe,productState
```


# Important

`root/SecurityCenter2` is not available or meaningful in every Windows environment, particularly some server configurations.

Failure to query this namespace does not prove that no antivirus product exists.


# Third-Party Antivirus

A third-party antivirus product may change Defender's operating mode.

Therefore establish whether another security product is registered before interpreting Defender status.


# Defender Operating Mode

Depending on the endpoint configuration, Defender may operate differently when another antivirus product is installed.

Do not automatically report reduced Defender status as a vulnerability without establishing:

```text
Whether another AV is active

Whether Defender for Endpoint is deployed

Whether passive mode is intentional

What the enterprise baseline requires
```


# Defender Exclusions

Exclusions are one of the highest-value configuration areas to review.


# Why Exclusions Matter

Defender can exclude:

```text
Paths

Processes

File extensions

IP addresses
```

depending on configuration and platform capabilities.


# Security Model

```text
Defender Protection
       |
       v
Exclusion
       |
       v
Reduced Inspection
       |
       v
Security-Sensitive Location?
       |
    +--+--+
    |     |
   No    Yes
    |     |
    v     v
Context  Investigate
```


# Path Exclusions

```powershell
(Get-MpPreference).ExclusionPath
```


# Process Exclusions

```powershell
(Get-MpPreference).ExclusionProcess
```


# Extension Exclusions

```powershell
(Get-MpPreference).ExclusionExtension
```


# IP Exclusions

Where available:

```powershell
(Get-MpPreference).ExclusionIpAddress
```


# Combined Exclusion Summary

```powershell
$pref = Get-MpPreference

[PSCustomObject]@{
    ExclusionPath      = ($pref.ExclusionPath -join '; ')
    ExclusionProcess   = ($pref.ExclusionProcess -join '; ')
    ExclusionExtension = ($pref.ExclusionExtension -join '; ')
    ExclusionIPAddress = ($pref.ExclusionIpAddress -join '; ')
}
```


# Important

Access to exclusion information can be restricted by Defender configuration.

An empty or unavailable result does not always prove:

```text
No exclusions exist
```


# Path Exclusion Assessment

For each path exclusion ask:

```text
Why is it excluded?

Who can write there?

What files are stored there?

Do privileged applications execute from there?

Can standard users introduce content?

Is the exclusion broader than necessary?
```


# Example

```text
C:\ProgramData\Vendor\Cache
```

If this path is excluded, inspect:

```cmd
icacls "C:\ProgramData\Vendor\Cache"
```


# Security Correlation

```text
Defender Exclusion
       +
Standard-User Write Access
       +
Privileged Execution
       =
High-Value Review
```


# Do Not Report Every Exclusion

Some applications require documented exclusions for compatibility or performance.

The finding should be based on:

```text
Unnecessary scope

Unsafe filesystem permissions

Security-sensitive use

Missing business justification
```


# Process Exclusions

A process exclusion should be reviewed carefully.

Ask:

```text
Which executable is excluded?

Where is it installed?

Who can modify it?

Why is exclusion required?

Does it process untrusted content?
```


# Extension Exclusions

Broad exclusions such as an entire executable or script extension can materially reduce scanning coverage.

Review whether the exclusion is:

```text
Necessary

Narrowly scoped

Centrally managed

Documented
```


# Wildcards and Broad Paths

Broad exclusions deserve additional scrutiny.

Conceptually:

```text
C:\*
```

would be far more significant than a narrowly defined application cache directory.


# Filesystem Correlation

Always correlate security-sensitive exclusions with:

[Windows Filesystem Permissions](filesystem-permissions.md)


# Attack Surface Reduction

Attack Surface Reduction - ASR - rules are designed to reduce common behaviors associated with malware and intrusion activity.


# ASR Configuration

Check:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```


# Display Rules

```powershell
$pref = Get-MpPreference

for ($i = 0; $i -lt $pref.AttackSurfaceReductionRules_Ids.Count; $i++) {
    [PSCustomObject]@{
        RuleId = $pref.AttackSurfaceReductionRules_Ids[$i]
        Action = $pref.AttackSurfaceReductionRules_Actions[$i]
    }
}
```


# Why Pair IDs and Actions?

The arrays correspond by index:

```text
Rule ID 1 -> Action 1

Rule ID 2 -> Action 2

Rule ID 3 -> Action 3
```


# ASR Actions

ASR rules can support operating modes such as:

```text
Disabled

Block

Audit

Warn
```

with exact supported behavior depending on the rule and platform.


# Important

Do not treat:

```text
Audit
```

as equivalent to:

```text
Block
```


# ASR Assessment Questions

For each rule determine:

```text
Is it configured?

Which action applies?

Is it centrally managed?

Does the endpoint support it?

Is the rule producing events?

Does the organisation expect enforcement?
```


# ASR Exclusions

Check:

```powershell
(Get-MpPreference).AttackSurfaceReductionOnlyExclusions
```


# Review Exclusions

ASR exclusions should be evaluated similarly to antivirus exclusions:

```text
Business justification

Scope

Filesystem permissions

Privileged use

User-controlled content
```


# ASR Policy Matrix

A useful assessment table is:

| Rule ID | Configured Action | Intended Action | Result |
|---|---|---|---|
| `<GUID>` | Block | Block | Match |
| `<GUID>` | Audit | Block | Review |
| `<GUID>` | Not configured | Block | Review |


# Avoid Memorising GUIDs in Reports

Where possible, map each rule GUID to its documented Microsoft rule name.

This makes findings easier to understand and maintain.


# Network Protection

Check:

```powershell
Get-MpPreference |
    Select-Object EnableNetworkProtection
```


# Security Purpose

Network Protection extends Microsoft Defender SmartScreen-style reputation and network protection capabilities to supported applications and processes.


# Assessment

Determine whether the configured state matches the organisation's intended endpoint baseline.


# Controlled Folder Access

Controlled Folder Access can help protect designated folders against unauthorized modifications by untrusted applications.


# Check Configuration

```powershell
Get-MpPreference |
    Select-Object EnableControlledFolderAccess
```


# Protected Folders

```powershell
(Get-MpPreference).ControlledFolderAccessProtectedFolders
```


# Allowed Applications

```powershell
(Get-MpPreference).ControlledFolderAccessAllowedApplications
```


# Assessment Questions

Ask:

```text
Is Controlled Folder Access enabled?

Which folders are protected?

Which applications are allowed?

Are exceptions broader than necessary?

Does the organisation require this feature?
```


# Important

Controlled Folder Access being disabled is not automatically a vulnerability.

It must be evaluated against:

```text
Threat model

Security baseline

Endpoint role

Other ransomware controls
```


# Defender Firewall

Microsoft Defender Firewall is separate from Defender Antivirus but is part of the Windows security posture.


# Profiles

```powershell
Get-NetFirewallProfile |
    Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction
```


# Example

```text
Name    Enabled
----    -------
Domain  True
Private True
Public  True
```


# Detailed Rules

```powershell
Get-NetFirewallRule -Enabled True -ErrorAction SilentlyContinue |
    Select-Object DisplayName,Direction,Action,Profile
```


# Important

A complete firewall assessment deserves its own methodology.

For Defender assessment, record whether host firewall protection is active and whether obvious policy gaps affect the endpoint threat model.


# Defender Event Logs

The primary Defender operational log is:

```text
Microsoft-Windows-Windows Defender/Operational
```


# Recent Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 50 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message
```


# List Defender Logs

```powershell
Get-WinEvent -ListLog '*Defender*' -ErrorAction SilentlyContinue |
    Select-Object LogName,RecordCount,IsEnabled
```


# Why Event Logs Matter

Events can provide evidence of:

```text
Threat detection

Configuration changes

ASR actions

Protection changes

Scan activity

Security intelligence updates
```


# Event IDs

Microsoft documents specific event IDs for Defender Antivirus and ASR activity.

When reporting an event:

```text
Record event ID

Timestamp

Message

Affected resource

Relevant policy
```

Do not rely on memorised event numbers without validating their meaning for the relevant Windows/Defender version.


# Defender Threat History

Query known threats:

```powershell
Get-MpThreat -ErrorAction SilentlyContinue
```


# Detection History

```powershell
Get-MpThreatDetection -ErrorAction SilentlyContinue
```


# Selected Fields

```powershell
Get-MpThreatDetection -ErrorAction SilentlyContinue |
    Select-Object InitialDetectionTime,
                  LastThreatStatusChangeTime,
                  ThreatID,
                  ActionSuccess,
                  Resources
```


# Sensitive Evidence

Detection history may contain:

```text
Usernames

File paths

Network locations

Sensitive filenames
```

Handle assessment evidence appropriately.


# Scan Configuration

Review:

```powershell
Get-MpPreference |
    Select-Object ScanParameters,
                  ScanScheduleDay,
                  ScanScheduleTime,
                  RandomizeScheduleTaskTimes
```


# Scan Status

```powershell
Get-MpComputerStatus |
    Select-Object QuickScanAge,
                  QuickScanStartTime,
                  QuickScanEndTime,
                  FullScanAge,
                  FullScanStartTime,
                  FullScanEndTime
```


# Interpretation

Scheduled scanning is one part of protection.

Real-time and behavior-based controls remain important even when periodic scans are configured.


# Safe Detection Validation

A standard harmless validation mechanism for antivirus products is the EICAR anti-malware test file.


# EICAR

The EICAR test file is specifically designed for antivirus testing and contains no malicious executable code.


# Recommended Approach

Use the official EICAR test mechanism only when:

```text
The assessment scope permits antivirus validation

Operational teams understand the test

Alerting impact is acceptable

Evidence handling is agreed
```


# Important

A successful EICAR detection demonstrates:

```text
The antivirus detection pipeline responded to the standard test pattern.
```

It does not prove:

```text
Every real-world threat will be detected.
```


# Prefer Official Source

Use the official EICAR test file documentation rather than copying untrusted variants from random websites.

See the references at the end of this page.


# Detection Validation Model

```text
Approved Test
     |
     v
Defender Inspection
     |
  +--+--+
  |     |
Detect No Detect
  |     |
  v     v
Capture Investigate
Event   Configuration
```


# Validation Evidence

Capture:

```text
Test timestamp

Test location

Defender status

Detection event

Action taken

Relevant policy

Cleanup state
```


# Do Not Use Live Malware

There is no need to deploy real malware merely to validate that Defender is operating.


# Defender and PowerShell

Defender can inspect PowerShell-related activity through multiple security mechanisms.

The endpoint may also use:

```text
AMSI

Script scanning

ASR

PowerShell logging

Application control

EDR
```


# AMSI

The Antimalware Scan Interface allows applications and services to integrate with antimalware products.


# Security Model

```text
Script / Content
      |
      v
AMSI-Aware Application
      |
      v
AMSI
      |
      v
Antimalware Provider
      |
      v
Allow / Detect
```


# Assessment Principle

Determine whether the endpoint's protection architecture is operating as intended.

Do not disable or patch AMSI as part of routine control validation.


# PowerShell Logging

PowerShell security monitoring can include:

```text
Script Block Logging

Module Logging

Transcription
```

depending on enterprise policy.


# Registry Policy Review

Relevant PowerShell policy locations can be inspected where permitted.

Example:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -ErrorAction SilentlyContinue
```


# Module Logging

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging' -ErrorAction SilentlyContinue
```


# Transcription

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue
```


# Important

PowerShell logging is not Defender Antivirus itself.

It is included here because endpoint detection quality frequently depends on several complementary Windows controls.


# Defender and Application Control

Defender and application control provide different security layers.

```text
Application Control
       |
       v
Should this code run?
```

while antivirus/EDR asks questions more like:

```text
Is this content or behavior malicious or suspicious?
```


# Combined Model

```text
Executable
    |
    v
AppLocker / WDAC
    |
Allowed?
    |
    v
Defender / EDR
    |
Malicious?
    |
    v
Execution / Block / Alert
```


# Related Note

See:

[Windows Application Control](application-control.md)


# Defender and Filesystem Permissions

A Defender exclusion becomes much more important if:

```text
The excluded directory is writable by standard users.
```

Check:

```cmd
icacls "C:\ExcludedPath"
```


# Related Note

See:

[Windows Filesystem Permissions](filesystem-permissions.md)


# Defender and Services

Security products operate through privileged services and drivers.

Do not modify Defender service permissions or service configuration during routine testing.


# Check Service

```powershell
Get-Service WinDefend -ErrorAction SilentlyContinue
```


# Related Note

See:

[Windows Services](services.md)


# Defender and Registry

Defender configuration can be influenced by:

```text
Local policy

Group Policy

MDM

Microsoft security management platforms

Defender configuration
```

Avoid treating a single Registry key as the complete source of truth.


# Related Note

See:

[Windows Registry Security](registry.md)


# Enterprise Management

Defender settings may be centrally controlled through technologies such as:

```text
Group Policy

Microsoft Intune

Microsoft Defender for Endpoint

Configuration Manager

Security management for Defender for Endpoint
```


# Assessment Principle

Determine the authoritative management source before recommending configuration changes.


# Local vs Effective Configuration

A Registry value may exist locally but be overridden or protected by enterprise policy.

Prefer observed effective configuration where possible.


# Standard User Modification

An important security question is:

```text
Can a standard user weaken Defender?
```


# Safe Assessment

Do not attempt to turn protections off.

Instead review:

```text
ACLs

Policy ownership

Tamper protection

Command authorization

Observed configuration
```


# Expected Security Boundary

Standard users should not be able to arbitrarily disable enterprise endpoint protection.


# Administrative Access

An administrator naturally has significantly greater system control.

The existence of administrator-accessible configuration is not by itself a vulnerability.


# Security Boundary

Focus on:

```text
Unexpected lower-privileged control
```

rather than:

```text
Administrator can administer the machine
```


# Defender Configuration Summary

A useful assessment summary:

```powershell
$status = Get-MpComputerStatus
$pref = Get-MpPreference

[PSCustomObject]@{
    AMServiceEnabled              = $status.AMServiceEnabled
    AntivirusEnabled              = $status.AntivirusEnabled
    RealTimeProtectionEnabled     = $status.RealTimeProtectionEnabled
    BehaviorMonitorEnabled        = $status.BehaviorMonitorEnabled
    IoavProtectionEnabled         = $status.IoavProtectionEnabled
    NISEnabled                    = $status.NISEnabled
    TamperProtected               = $status.IsTamperProtected
    SignatureVersion              = $status.AntivirusSignatureVersion
    SignatureLastUpdated          = $status.AntivirusSignatureLastUpdated
    DisableRealtimeMonitoring     = $pref.DisableRealtimeMonitoring
    DisableBehaviorMonitoring     = $pref.DisableBehaviorMonitoring
    DisableScriptScanning         = $pref.DisableScriptScanning
    PUAProtection                 = $pref.PUAProtection
    NetworkProtection             = $pref.EnableNetworkProtection
    ControlledFolderAccess        = $pref.EnableControlledFolderAccess
}
```


# Exclusion Summary

```powershell
$pref = Get-MpPreference

Write-Host "`n=== PATH EXCLUSIONS ==="
$pref.ExclusionPath

Write-Host "`n=== PROCESS EXCLUSIONS ==="
$pref.ExclusionProcess

Write-Host "`n=== EXTENSION EXCLUSIONS ==="
$pref.ExclusionExtension

Write-Host "`n=== ASR EXCLUSIONS ==="
$pref.AttackSurfaceReductionOnlyExclusions
```


# ASR Summary

```powershell
$pref = Get-MpPreference

Write-Host "=== ATTACK SURFACE REDUCTION RULES ==="

if ($pref.AttackSurfaceReductionRules_Ids) {
    for ($i = 0; $i -lt $pref.AttackSurfaceReductionRules_Ids.Count; $i++) {
        [PSCustomObject]@{
            RuleId = $pref.AttackSurfaceReductionRules_Ids[$i]
            Action = $pref.AttackSurfaceReductionRules_Actions[$i]
        }
    }
}
else {
    Write-Host "No ASR rules returned by Get-MpPreference."
}
```


# Comprehensive Read-Only Assessment

The following script collects useful Defender posture information without modifying Defender configuration.

```powershell
Write-Host "========================================"
Write-Host " MICROSOFT DEFENDER SECURITY ASSESSMENT "
Write-Host "========================================"

Write-Host "`n=== CURRENT USER ==="
whoami

Write-Host "`n=== GROUPS ==="
whoami /groups

Write-Host "`n=== DEFENDER SERVICE ==="
Get-Service WinDefend -ErrorAction SilentlyContinue |
    Format-Table Status,Name,DisplayName -AutoSize

Write-Host "`n=== DEFENDER STATUS ==="

$status = Get-MpComputerStatus -ErrorAction SilentlyContinue

if ($status) {
    $status |
        Select-Object AMServiceEnabled,
                      AntivirusEnabled,
                      AntispywareEnabled,
                      RealTimeProtectionEnabled,
                      BehaviorMonitorEnabled,
                      IoavProtectionEnabled,
                      NISEnabled,
                      OnAccessProtectionEnabled,
                      IsTamperProtected,
                      AMProductVersion,
                      AMEngineVersion,
                      AntivirusSignatureVersion,
                      AntivirusSignatureLastUpdated |
        Format-List
}
else {
    Write-Host "Get-MpComputerStatus did not return Defender status."
}

Write-Host "`n=== DEFENDER PREFERENCES ==="

$pref = Get-MpPreference -ErrorAction SilentlyContinue

if ($pref) {
    $pref |
        Select-Object DisableRealtimeMonitoring,
                      DisableBehaviorMonitoring,
                      DisableIOAVProtection,
                      DisableScriptScanning,
                      DisableBlockAtFirstSeen,
                      MAPSReporting,
                      SubmitSamplesConsent,
                      PUAProtection,
                      EnableNetworkProtection,
                      EnableControlledFolderAccess |
        Format-List

    Write-Host "`n=== PATH EXCLUSIONS ==="
    $pref.ExclusionPath

    Write-Host "`n=== PROCESS EXCLUSIONS ==="
    $pref.ExclusionProcess

    Write-Host "`n=== EXTENSION EXCLUSIONS ==="
    $pref.ExclusionExtension

    Write-Host "`n=== ASR EXCLUSIONS ==="
    $pref.AttackSurfaceReductionOnlyExclusions

    Write-Host "`n=== ASR RULES ==="

    if ($pref.AttackSurfaceReductionRules_Ids) {
        for ($i = 0; $i -lt $pref.AttackSurfaceReductionRules_Ids.Count; $i++) {
            [PSCustomObject]@{
                RuleId = $pref.AttackSurfaceReductionRules_Ids[$i]
                Action = $pref.AttackSurfaceReductionRules_Actions[$i]
            }
        }
    }
    else {
        Write-Host "No ASR rules returned."
    }
}
else {
    Write-Host "Get-MpPreference did not return Defender preferences."
}

Write-Host "`n=== DEFENDER EVENT LOG ==="

Get-WinEvent -ListLog 'Microsoft-Windows-Windows Defender/Operational' -ErrorAction SilentlyContinue |
    Select-Object LogName,RecordCount,IsEnabled |
    Format-Table -AutoSize

Write-Host "`n=== RECENT DEFENDER EVENTS ==="

Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 20 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message |
    Format-List

Write-Host "`n=== APPLICATION CONTROL CONTEXT ==="

Write-Host "PowerShell Language Mode:"
$ExecutionContext.SessionState.LanguageMode

Write-Host "`nAppLocker Collections:"

try {
    [xml]$appLocker = Get-AppLockerPolicy -Effective -Xml -ErrorAction Stop

    $appLocker.AppLockerPolicy.RuleCollection |
        Select-Object Type,EnforcementMode |
        Format-Table -AutoSize
}
catch {
    Write-Host "Unable to retrieve effective AppLocker policy."
}

Write-Host "`n=== COMPLETE ==="
```


# What the Script Does

The script performs read-only collection of:

```text
Identity

Groups

Defender service status

Antivirus status

Real-time protection

Behavior monitoring

Tamper protection

Engine/version information

Security intelligence information

Defender preferences

Exclusions

ASR configuration

Defender logging

PowerShell language mode

AppLocker context
```


# What the Script Does Not Do

It does not:

```text
Disable Defender

Modify exclusions

Change ASR rules

Disable tamper protection

Change application-control policy

Create persistence

Modify security settings
```


# Evidence Collection Model

For every relevant Defender observation capture:

```text
Configuration
      |
      v
Runtime Status
      |
      v
Relevant Policy
      |
      v
Validation Result
      |
      v
Event Log
      |
      v
Security Conclusion
```


# Finding - Real-Time Protection Disabled

Possible evidence:

```text
RealTimeProtectionEnabled : False
```

Further validate:

```text
Is another AV active?

Is Defender in passive mode?

Is this temporary?

Is the setting centrally managed?

What does the enterprise baseline require?
```


# Possible Finding Title

```text
Real-Time Antivirus Protection Is Not Active
```


# Do Not Overstate

Do not report:

> The endpoint has no antivirus protection.

unless you have established that no alternative protection exists.


# Finding - Tamper Protection Disabled

Possible observation:

```text
IsTamperProtected : False
```


# Further Validation

Determine:

```text
Is Defender for Endpoint deployed?

Is tamper protection required by policy?

Can a standard user alter security settings?

Are settings protected through another management mechanism?
```


# Possible Finding Title

```text
Microsoft Defender Tamper Protection Is Not Enabled
```


# Finding - Broad Defender Exclusion

Example:

```text
ExclusionPath:
C:\CompanyData
```

and:

```text
BUILTIN\Users:
Modify
```


# Further Validation

Determine:

```text
What is stored there?

Why is it excluded?

Does executable content exist there?

Do privileged processes consume content there?

Can the exclusion be narrowed?
```


# Possible Finding Title

```text
Microsoft Defender Exclusion Covers a Standard-User-Writable Directory
```


# Finding - ASR Audit Instead of Block

Observation:

```text
Required ASR rule:
Audit
```

Enterprise baseline:

```text
Block
```


# Possible Finding Title

```text
Attack Surface Reduction Rule Is Configured in Audit Mode Instead of Block Mode
```


# Finding - Outdated Security Intelligence

Observation:

```text
AntivirusSignatureLastUpdated:
Significantly older than expected baseline
```


# Further Validation

Check:

```text
Internet/connectivity status

Update infrastructure

Management policy

Platform update status

Cloud protection
```


# Possible Finding Title

```text
Microsoft Defender Security Intelligence Is Outdated
```


# Finding - Defender Logging Disabled

If the operational log required by the organisation is unavailable or disabled, this can reduce detection and investigation capability.


# Possible Finding Title

```text
Microsoft Defender Operational Logging Is Not Available
```


# Finding - Weak Exclusion and Privileged Consumer

Strong chain:

```text
Standard User
      |
      v
Writable Directory
      |
      v
Defender Exclusion
      |
      v
Privileged Service Dependency
      |
      v
Reduced Security Inspection
```


# Important

The exclusion itself does not automatically prove privilege escalation.

You must still establish the privileged execution or processing path.


# False Positive - Defender Disabled Because Another AV Is Active

If enterprise-approved third-party antivirus is providing primary protection, Defender Antivirus may intentionally operate differently.


# False Positive - Controlled Folder Access Disabled

Controlled Folder Access is not mandatory in every endpoint architecture.


# False Positive - No ASR Rules Returned

This requires investigation.

Possible explanations include:

```text
No ASR policy configured

Insufficient visibility

Different management architecture

Unsupported configuration

Policy not applied
```


# False Positive - Empty Exclusions

An empty result does not always guarantee there are no exclusions.

Access and management architecture can affect visibility.


# False Positive - FullLanguage PowerShell

```text
FullLanguage
```

does not mean:

```text
Defender is disabled
```

PowerShell language mode and antivirus protection are separate security controls.


# False Positive - Defender Service Running

Likewise:

```text
WinDefend = Running
```

does not prove:

```text
All protections are enabled
```


# False Positive - One Detection Test Succeeds

A successful standard antivirus test proves that specific detection path worked.

It does not establish comprehensive endpoint security effectiveness.


# Alternative Explanations

Unexpected Defender configuration may result from:

```text
Third-party antivirus

Passive mode

Troubleshooting

Legacy compatibility

Application vendor exclusions

VDI configuration

Server workload requirements

Performance requirements

Central security policy
```


# Reporting Principle

Do not report:

```text
Configuration differs from personal preference
```

as:

```text
Security vulnerability
```

Compare observations against:

```text
Vendor guidance

Organisational baseline

Threat model

Compensating controls

Actual security impact
```


# Remediation - Real-Time Protection

Where Defender is the intended primary antivirus, ensure real-time protection is enabled and centrally managed.


# Remediation - Tamper Protection

Enable tamper protection where supported and appropriate to the organisation's endpoint security architecture.


# Remediation - Exclusions

Remove unnecessary exclusions.

Where exclusions are required:

```text
Keep them narrow

Document the business justification

Protect excluded paths with strong ACLs

Avoid excluding broad executable locations

Review them periodically
```


# Remediation - ASR

Deploy appropriate ASR rules based on:

```text
Microsoft guidance

Application compatibility

Enterprise risk

Pilot testing

Audit telemetry
```


# ASR Deployment Model

```text
Identify Rule
     |
     v
Audit
     |
     v
Collect Events
     |
     v
Assess Compatibility
     |
     v
Warn / Block
     |
     v
Monitor
```


# Remediation - Cloud Protection

Where supported by organisational requirements, configure cloud-delivered protection and related security intelligence capabilities according to Microsoft's security baseline guidance.


# Remediation - Security Intelligence

Ensure Defender security intelligence updates occur through the approved enterprise update mechanism.


# Remediation - Logging

Forward relevant Defender events to central monitoring where appropriate.


# Remediation - Least Privilege

Standard users should not be able to weaken endpoint security controls.


# Remediation - Filesystem

Secure directories covered by Defender exclusions.

Review:

[Windows Filesystem Permissions](filesystem-permissions.md)


# Remediation - Application Control

Use application control as a complementary control.

Review:

[Windows Application Control](application-control.md)


# Remediation - Central Management

Manage Defender through the organisation's authoritative security-management platform where applicable.


# Retesting

Retesting should reproduce the original observation under the same security context.


# Step 1 - Identity

```cmd
whoami
```


# Step 2 - Defender Status

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusEnabled,
                  RealTimeProtectionEnabled,
                  BehaviorMonitorEnabled,
                  IsTamperProtected
```


# Step 3 - Preferences

```powershell
Get-MpPreference
```


# Step 4 - Exclusions

```powershell
$pref = Get-MpPreference

$pref.ExclusionPath
$pref.ExclusionProcess
$pref.ExclusionExtension
```


# Step 5 - ASR

```powershell
$pref = Get-MpPreference

for ($i = 0; $i -lt $pref.AttackSurfaceReductionRules_Ids.Count; $i++) {
    [PSCustomObject]@{
        RuleId = $pref.AttackSurfaceReductionRules_Ids[$i]
        Action = $pref.AttackSurfaceReductionRules_Actions[$i]
    }
}
```


# Step 6 - Network Protection

```powershell
(Get-MpPreference).EnableNetworkProtection
```


# Step 7 - Controlled Folder Access

```powershell
(Get-MpPreference).EnableControlledFolderAccess
```


# Step 8 - Event Logging

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 20 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated,Id,LevelDisplayName,Message
```


# Step 9 - Safe Detection Validation

Where explicitly approved, repeat the standard harmless antivirus validation used during the original assessment.


# Step 10 - Business Functionality

Confirm that required applications continue to function after Defender hardening.


# Retest Matrix

| Test | Expected After Fix |
|---|---|
| Defender service | Operational |
| Antivirus protection | Enabled where Defender is primary |
| Real-time protection | Enabled |
| Behavior monitoring | Enabled |
| Tamper protection | Enabled where required |
| Security intelligence | Current |
| Broad unnecessary exclusion | Removed |
| Required exclusion | Narrowly scoped |
| Writable excluded directory | Corrected or justified |
| Required ASR rules | Expected action |
| Network Protection | Expected state |
| Defender event logging | Operational |
| Approved applications | Functional |


# Defender Assessment Checklist

## Context

- [ ] Current user identified
- [ ] Group membership identified
- [ ] Privileges reviewed
- [ ] Windows role understood
- [ ] Third-party antivirus considered
- [ ] Defender for Endpoint deployment considered

## Defender Status

- [ ] `Get-MpComputerStatus` collected
- [ ] Antimalware service checked
- [ ] Antivirus status checked
- [ ] Real-time protection checked
- [ ] Behavior monitoring checked
- [ ] IOAV protection checked
- [ ] Network inspection checked
- [ ] Tamper protection checked

## Versions

- [ ] Product version collected
- [ ] Engine version collected
- [ ] Security intelligence version collected
- [ ] Last security intelligence update checked

## Preferences

- [ ] `Get-MpPreference` collected
- [ ] Real-time monitoring preference checked
- [ ] Behavior monitoring preference checked
- [ ] Script scanning checked
- [ ] Block at First Sight checked
- [ ] PUA protection checked
- [ ] Cloud protection configuration reviewed

## Exclusions

- [ ] Path exclusions reviewed
- [ ] Process exclusions reviewed
- [ ] Extension exclusions reviewed
- [ ] IP exclusions reviewed where applicable
- [ ] ASR exclusions reviewed
- [ ] Business justification considered
- [ ] ACLs of excluded paths reviewed
- [ ] Privileged consumers correlated

## ASR

- [ ] ASR rule IDs collected
- [ ] Actions collected
- [ ] Rule IDs mapped to names
- [ ] Audit distinguished from block
- [ ] Required enterprise baseline compared
- [ ] ASR exclusions reviewed
- [ ] ASR events reviewed

## Network Protection

- [ ] Network Protection state checked
- [ ] Intended baseline established

## Controlled Folder Access

- [ ] CFA state checked
- [ ] Protected folders reviewed
- [ ] Allowed applications reviewed
- [ ] Business requirement considered

## Firewall

- [ ] Firewall profiles checked
- [ ] Enabled state recorded
- [ ] Obvious policy gaps considered

## Logging

- [ ] Defender Operational log checked
- [ ] Recent events reviewed
- [ ] Detection events reviewed
- [ ] Configuration-change events considered
- [ ] Central monitoring considered

## Threat History

- [ ] Existing threats reviewed where appropriate
- [ ] Detection history reviewed where appropriate
- [ ] Sensitive evidence protected

## PowerShell Context

- [ ] PowerShell version checked
- [ ] Language mode checked
- [ ] Script scanning considered
- [ ] AMSI architecture considered
- [ ] Script Block Logging considered
- [ ] Module Logging considered
- [ ] Transcription considered

## Application Control

- [ ] AppLocker considered
- [ ] WDAC considered
- [ ] Defender not treated as application control
- [ ] Application control not treated as antivirus

## Privilege Escalation

- [ ] Defender exclusions correlated with writable paths
- [ ] Service dependencies considered
- [ ] Scheduled task dependencies considered
- [ ] Privileged execution paths considered
- [ ] Security impact not overstated

## Validation

- [ ] Non-destructive validation preferred
- [ ] Standard harmless antivirus test used only if approved
- [ ] Runtime result captured
- [ ] Defender event captured
- [ ] No live malware required

## Reporting

- [ ] Exact setting reported
- [ ] Runtime status reported
- [ ] Management context reported
- [ ] Compensating controls considered
- [ ] Alternative antivirus considered
- [ ] Organisational baseline considered
- [ ] Impact supported by evidence
- [ ] Remediation addresses root cause

## Retesting

- [ ] Same user context used
- [ ] Defender status rechecked
- [ ] Preferences rechecked
- [ ] Exclusions rechecked
- [ ] ASR rechecked
- [ ] Logging rechecked
- [ ] Safe validation repeated where required
- [ ] Business functionality preserved


# Quick Reference

| Goal | Command |
|---|---|
| Current user | `whoami` |
| Groups | `whoami /groups` |
| Privileges | `whoami /priv` |
| Defender status | `Get-MpComputerStatus` |
| Defender preferences | `Get-MpPreference` |
| Defender service | `Get-Service WinDefend` |
| Path exclusions | `(Get-MpPreference).ExclusionPath` |
| Process exclusions | `(Get-MpPreference).ExclusionProcess` |
| Extension exclusions | `(Get-MpPreference).ExclusionExtension` |
| ASR rules | `(Get-MpPreference).AttackSurfaceReductionRules_Ids` |
| ASR actions | `(Get-MpPreference).AttackSurfaceReductionRules_Actions` |
| ASR exclusions | `(Get-MpPreference).AttackSurfaceReductionOnlyExclusions` |
| Network Protection | `(Get-MpPreference).EnableNetworkProtection` |
| Controlled Folder Access | `(Get-MpPreference).EnableControlledFolderAccess` |
| Threats | `Get-MpThreat` |
| Detections | `Get-MpThreatDetection` |
| Defender logs | `Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational'` |
| Firewall profiles | `Get-NetFirewallProfile` |


# Status Interpretation Matrix

| Property | Desired Question |
|---|---|
| `AMServiceEnabled` | Is antimalware service functionality enabled? |
| `AntivirusEnabled` | Is Defender Antivirus enabled? |
| `RealTimeProtectionEnabled` | Is real-time protection active? |
| `BehaviorMonitorEnabled` | Is behavior monitoring active? |
| `IoavProtectionEnabled` | Is IOAV protection active? |
| `NISEnabled` | Is network inspection enabled? |
| `IsTamperProtected` | Is tamper protection active? |
| `AntivirusSignatureVersion` | Which security intelligence is installed? |
| `AntivirusSignatureLastUpdated` | When was it updated? |


# Exclusion Risk Matrix

| Exclusion | Example Risk | Priority |
|---|---|---|
| Narrow protected application cache | Compatibility requirement | Review |
| User-writable application directory | Reduced inspection of user content | High review |
| Privileged executable directory | Reduced inspection of privileged code | High |
| Broad drive/path exclusion | Large reduction in inspection | High |
| Process exclusion | Depends on process trust | High review |
| Broad executable extension exclusion | Large reduction in scanning | High |


# ASR Assessment Matrix

| State | Meaning |
|---|---|
| Block | Rule actively prevents applicable behavior |
| Audit | Activity is observed but not blocked |
| Warn | User-facing warning behavior where supported |
| Disabled | Rule is disabled |
| Not configured | No explicit configured action observed |


# Security Layers Matrix

| Layer | Purpose |
|---|---|
| Defender Antivirus | Malware detection and prevention |
| Behavior Monitoring | Detect suspicious runtime behavior |
| Cloud Protection | Cloud-assisted detection |
| ASR | Reduce common attack surfaces |
| Network Protection | Protect against malicious network destinations |
| Controlled Folder Access | Protect selected data from unauthorized modification |
| AppLocker | Application allow/deny control |
| WDAC | Code integrity/application control |
| Windows Firewall | Host network filtering |
| PowerShell Logging | Script visibility |
| EDR | Endpoint detection and response |


# Evidence Matrix

| Evidence | Purpose |
|---|---|
| `whoami` | Establish test identity |
| `Get-MpComputerStatus` | Runtime protection status |
| `Get-MpPreference` | Effective Defender preferences visible to tester |
| Exclusion output | Identify reduced inspection areas |
| `icacls` | Correlate exclusions with filesystem trust |
| ASR output | Establish rule configuration |
| Defender event log | Establish actual security events |
| AppLocker/WDAC status | Establish application-control context |
| Approved detection test | Validate antivirus pipeline |


# Practical Validation Model

```text
WHEN THIS APPLIES
       |
       v
Windows Endpoint
       |
       v
IDENTIFY SECURITY PRODUCT
       |
       v
GET RUNTIME STATUS
       |
       v
GET CONFIGURATION
       |
       v
CHECK EXCLUSIONS
       |
       v
CHECK ASR / NETWORK CONTROLS
       |
       v
CHECK TAMPER PROTECTION
       |
       v
CHECK LOGGING
       |
       v
SAFE VALIDATION
       |
       v
INTERPRET
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

A healthy representative result could include:

```text
AntivirusEnabled:
True

RealTimeProtectionEnabled:
True

BehaviorMonitorEnabled:
True

IsTamperProtected:
True

Security Intelligence:
Current according to organisational baseline

Broad Unsafe Exclusions:
None identified

Required ASR Rules:
Configured according to baseline

Defender Operational Logging:
Enabled
```


# Negative Result

A result requiring further review could include:

```text
RealTimeProtectionEnabled:
False

TamperProtection:
False

ExclusionPath:
C:\ProgramData\Company

Filesystem:
Users = Modify

ASR:
No required rules configured

Defender Operational Log:
Unavailable
```


# Further Validation

Before reporting, determine:

```text
Is another antivirus product active?

Is Defender intentionally passive?

Is the configuration centrally managed?

Does the organisation require these controls?

Are exclusions documented?

Are excluded paths writable?

Are privileged applications using excluded locations?

Are ASR rules intentionally in audit mode?

Are events forwarded elsewhere?

Are compensating controls present?
```


# Reporting Conclusion Model

A defensible Defender conclusion should answer:

```text
WHAT protection is missing or weakened?

WHERE does the condition apply?

WHO can influence the affected resource?

WHY does it matter?

WHICH compensating controls exist?

WHAT evidence confirms the effective state?
```


# Final Testing Principle

Defender assessment is not:

```text
Get-MpComputerStatus
       |
       v
Find False
       |
       v
Report Vulnerability
```

It is:

```text
IDENTIFY ENDPOINT ARCHITECTURE
        |
        v
UNDERSTAND DEFENDER ROLE
        |
        v
CHECK EFFECTIVE STATUS
        |
        v
CHECK CONFIGURATION
        |
        v
CHECK EXCLUSIONS
        |
        v
CHECK ASR
        |
        v
CHECK APPLICATION CONTROL
        |
        v
CHECK LOGGING
        |
        v
VALIDATE SAFELY
        |
        v
COMPARE WITH BASELINE
        |
        v
ESTABLISH SECURITY IMPACT
```


# Final Questions

For every Defender assessment ask:

```text
Is Microsoft Defender Antivirus installed?

Is another antivirus product installed?

Is Defender active or passive?

Is the antimalware service enabled?

Is antivirus protection enabled?

Is real-time protection enabled?

Is behavior monitoring enabled?

Is IOAV protection enabled?

Is network inspection enabled?

Is script scanning enabled?

Is tamper protection enabled?

Which Defender product version is installed?

Which engine version is installed?

Which security intelligence version is installed?

When was security intelligence last updated?

Is cloud-delivered protection configured?

Is automatic sample submission configured?

Is Block at First Sight configured?

Is PUA protection configured?

Which paths are excluded?

Which processes are excluded?

Which extensions are excluded?

Are any exclusions unnecessarily broad?

Are excluded paths writable by standard users?

Do privileged processes execute from excluded paths?

Are ASR rules configured?

Which ASR rules are in Block mode?

Which are in Audit mode?

Which are in Warn mode?

Which are disabled?

Are there ASR exclusions?

Are those exclusions necessary?

Is Network Protection configured?

Is Controlled Folder Access configured?

Which folders are protected?

Which applications are allowed?

Are Defender Firewall profiles enabled?

Are Defender operational events available?

Are detection events generated?

Are configuration changes visible?

Are events forwarded centrally?

Can standard users weaken Defender settings?

Is configuration protected by tamper protection?

Is Defender centrally managed?

Which platform owns the authoritative policy?

Is AppLocker configured?

Is WDAC configured?

Does application control compensate for any observed gap?

Are filesystem permissions secure?

Are Defender exclusions combined with writable privileged paths?

Does PowerShell use FullLanguage or ConstrainedLanguage?

Is PowerShell security logging enabled?

Is AMSI part of the endpoint protection architecture?

Was a harmless detection validation approved?

Did Defender detect the approved test?

Was an event generated?

Did the expected remediation action occur?

Is the observation actually a security issue?

Could another antivirus explain the Defender state?

Could passive mode explain the Defender state?

Does the organisation's security baseline require the missing feature?

What is the actual security consequence?

What evidence supports the conclusion?

What remediation addresses the root cause?

Can exclusions be narrowed instead of removed?

Can ASR move from audit to enforcement after compatibility testing?

Does the endpoint remain functional after hardening?

Does retesting demonstrate the expected protection?
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
- [Windows Credentials](credentials.md)


# References

- [Microsoft Learn - Microsoft Defender Antivirus](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-antivirus-windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Microsoft Defender Antivirus PowerShell Cmdlets](https://learn.microsoft.com/en-us/powershell/module/defender/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Get-MpComputerStatus](https://learn.microsoft.com/en-us/powershell/module/defender/get-mpcomputerstatus){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Get-MpPreference](https://learn.microsoft.com/en-us/powershell/module/defender/get-mppreference){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Configure Microsoft Defender Antivirus Exclusions](https://learn.microsoft.com/en-us/defender-endpoint/configure-exclusions-microsoft-defender-antivirus){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Attack Surface Reduction Rules](https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction-rules-reference){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Enable Attack Surface Reduction Rules](https://learn.microsoft.com/en-us/defender-endpoint/enable-attack-surface-reduction){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Network Protection](https://learn.microsoft.com/en-us/defender-endpoint/network-protection){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Controlled Folder Access](https://learn.microsoft.com/en-us/defender-endpoint/controlled-folders){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Microsoft Defender Antivirus Event IDs](https://learn.microsoft.com/en-us/defender-endpoint/troubleshoot-microsoft-defender-antivirus){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Microsoft Defender Antivirus Cloud Protection](https://learn.microsoft.com/en-us/defender-endpoint/cloud-protection-microsoft-defender-antivirus){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Tamper Protection](https://learn.microsoft.com/en-us/defender-endpoint/prevent-changes-to-security-settings-with-tamper-protection){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Antimalware Scan Interface](https://learn.microsoft.com/en-us/windows/win32/amsi/antimalware-scan-interface-portal){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Microsoft Defender Firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/){ target="_blank" rel="noopener noreferrer" }
- [EICAR - Anti-Malware Test File](https://www.eicar.org/download-anti-malware-testfile/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Check status and configuration"

    `Get-MpComputerStatus` and `Get-MpPreference` answer different questions. Review both so that configured preferences can be compared with the endpoint's observed protection state.


!!! tip "Prioritise exclusions"

    Defender exclusions deserve careful review, particularly when an excluded path is writable by standard users or contains content consumed by privileged applications.


!!! tip "Correlate Defender with application control"

    Defender Antivirus, AppLocker and WDAC provide different security functions. Evaluate them together rather than assuming that one control replaces the others.


!!! tip "Distinguish audit from enforcement"

    ASR rules operating in audit mode provide useful telemetry but should not be described as actively blocking the associated behaviour.


!!! warning "Do not disable protection to test protection"

    A normal endpoint assessment does not require disabling Defender, tamper protection, AMSI or EDR. Configuration inspection, event analysis and approved harmless validation provide stronger and safer evidence.


!!! warning "Defender status requires context"

    Defender Antivirus may intentionally operate differently when another enterprise antivirus product is active or when Defender is deployed in a different operating mode. Establish the complete endpoint protection architecture before reporting a configuration as vulnerable.
