---
title: Detection Validation
description: Practical detection validation methodology for authorised red team and purple team assessments, covering telemetry, Microsoft Defender, EDR, SIEM, Sysmon, Windows Event Logs, PowerShell, AMSI, AppLocker, WDAC, ASR, EICAR, Atomic Red Team, ATT&CK coverage, detection gaps, SOC response, evidence, metrics, retesting, and detection engineering.
---

# Detection Validation

Detection validation determines whether security controls can observe, identify, alert on, and support investigation of attacker behaviour.

A successful red team assessment should not only answer:

```text
Could the attacker perform the action?
```

It should also answer:

```text
Was the action prevented?

Was telemetry generated?

Was the activity detected?

Was an alert created?

Did the SIEM receive it?

Did the SOC investigate it?

Could the organisation respond?
```

A useful model is:

```text
Red Team Activity
       |
       v
Endpoint / Network / Identity
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
SIEM / Security Platform
       |
       v
SOC Analyst
       |
       v
Investigation
       |
       v
Response
```

A failure anywhere in this chain can create a detection gap.

!!! warning "Authorised testing only"
    Detection validation should be performed only against systems and identities included in the assessment scope. Use harmless vendor test artifacts and controlled simulations before progressing to more intrusive techniques. Coordinate disruptive tests through the Rules of Engagement and stop once the required security objective has been demonstrated.


---

# Detection Validation Objectives

Common objectives include:

```text
Validate endpoint telemetry
Validate EDR detections
Validate antivirus
Validate Microsoft Defender
Validate AMSI
Validate PowerShell visibility
Validate application-control telemetry
Validate ASR
Validate Sysmon
Validate Windows auditing
Validate identity detections
Validate network detections
Validate SIEM ingestion
Validate correlation rules
Validate SOC triage
Validate incident investigation
Validate containment procedures
Validate ATT&CK coverage
Identify detection gaps
Measure time to detect
Measure time to respond
Retest detection improvements
```


---

# Detection Is a Pipeline

A detection should not be considered only as an alert rule.

```text
Activity
   |
   v
Sensor
   |
   v
Telemetry
   |
   v
Collection
   |
   v
Normalisation
   |
   v
Detection Rule
   |
   v
Alert
   |
   v
Triage
   |
   v
Investigation
   |
   v
Response
```

For example, an excellent SIEM rule cannot detect an event that never reaches the SIEM.


---

# Prevention, Detection, and Response

These should be measured separately.

```text
                    Technique
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Prevention    Detection     Response
          |            |            |
          v            v            v
        Block        Alert       Contain
```

Possible outcomes include:

| Prevention | Detection | Interpretation |
|---|---|---|
| Blocked | Alerted | Strong control |
| Blocked | No alert | Prevention works, visibility may be weak |
| Allowed | Alerted | Detective control worked |
| Allowed | Logged only | Telemetry exists but detection may be missing |
| Allowed | No telemetry | Major visibility gap |


---

# Detection Validation Lifecycle

```text
Define Technique
      |
      v
Identify Expected Telemetry
      |
      v
Confirm Logging
      |
      v
Run Safe Test
      |
      v
Collect Evidence
      |
      v
Check Endpoint
      |
      v
Check SIEM
      |
      v
Check Alert
      |
      v
Check SOC Response
      |
      v
Identify Gap
      |
      v
Improve Detection
      |
      v
Retest
```


---

# Start with the Detection Objective

Do not execute a technique simply because a test exists.

Define what should be validated.

Example:

```text
Objective:

Determine whether the SOC detects suspicious PowerShell execution
from a standard-user workstation.
```

Then determine:

```text
Expected process telemetry
Expected PowerShell telemetry
Expected Defender telemetry
Expected EDR telemetry
Expected SIEM events
Expected alert
Expected analyst response
```


---

# Establish a Baseline

Before executing tests, record the environment.

Useful information includes:

```text
Hostname
Operating system
Username
Privilege
PowerShell version
EDR product
Antivirus product
Defender state
Sysmon state
Application-control state
PowerShell logging
Audit policy
Time
Timezone
SIEM platform
```


---

# Windows Baseline

Identity:

```powershell
whoami
```

Detailed security context:

```powershell
whoami /all
```

Hostname:

```powershell
hostname
```

Operating system:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber
```

PowerShell:

```powershell
$PSVersionTable
```

Language mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```


---

# Time Synchronisation

Accurate timestamps are essential for detection validation.

Check:

```powershell
Get-Date
```

Windows time service:

```powershell
w32tm /query /status
```

Linux:

```bash
timedatectl status
```

Prefer a consistent timezone such as UTC in operator notes.


---

# Build a Test Identifier

Assign each test a unique identifier.

Example:

```text
RT-DV-001
RT-DV-002
RT-DV-003
```

Use the identifier in:

```text
Operator notes
Screenshots
SOC communication
Detection queries
Evidence
Retest records
```

This makes correlation easier.


---

# Detection Validation Record

Example:

```text
Test ID:
RT-DV-001

Technique:
PowerShell execution

Host:
WS01

User:
CORP\test-user

Start:
2026-09-05 18:42:11 UTC

End:
2026-09-05 18:43:02 UTC

Expected:
Process creation + PowerShell telemetry + EDR alert

Observed:
Process creation and PowerShell telemetry

Alert:
None

Result:
Detection gap
```


---

# Telemetry Sources

Detection engineering should combine multiple telemetry sources.

```text
Endpoint
Identity
Network
DNS
Proxy
Firewall
Email
Cloud
Application
Authentication
Application Control
EDR
Antivirus
```


---

# Endpoint Telemetry

Useful endpoint telemetry may include:

```text
Process creation
Process termination
Parent-child relationships
Command lines
PowerShell
Script execution
Network connections
DNS queries
File creation
File deletion
Registry modification
Service creation
Scheduled tasks
Authentication
Process access
DLL loading
Driver loading
Application control
Antivirus detections
```


---

# Windows Event Logs

Windows provides many useful event sources.

Examples include:

```text
Security
System
PowerShell
Windows Defender
AppLocker
Code Integrity
Task Scheduler
Windows Firewall
WMI
WinRM
```


---

# List Event Logs

PowerShell:

```powershell
Get-WinEvent -ListLog * |
    Select-Object LogName,RecordCount,IsEnabled
```

This can generate substantial output.

Filter when possible.


---

# Security Audit Policy

Review:

```powershell
auditpol /get /category:*
```

This provides the effective Windows audit configuration.


---

# Important Windows Event IDs

Event IDs should be interpreted in context because logging depends on audit configuration and platform components.

| Event ID | Source | Common Security Use |
|---|---|---|
| 4624 | Security | Successful logon |
| 4625 | Security | Failed logon |
| 4648 | Security | Explicit credentials |
| 4672 | Security | Special privileges assigned |
| 4688 | Security | Process creation |
| 4697 | Security | Service installation |
| 4698 | Security | Scheduled task created |
| 4702 | Security | Scheduled task updated |
| 4720 | Security | User account created |
| 4728 | Security | Member added to global security group |
| 4732 | Security | Member added to local security group |
| 4756 | Security | Member added to universal security group |
| 4768 | Security | Kerberos TGT requested |
| 4769 | Security | Kerberos service ticket requested |
| 4771 | Security | Kerberos pre-authentication failure |
| 4776 | Security | NTLM credential validation |
| 5140 | Security | Network share accessed |
| 5145 | Security | Detailed network share access |


---

# Event ID 4688 - Process Creation

Process creation is one of the most useful telemetry sources.

When configured appropriately, Event ID:

```text
4688
```

can provide:

```text
Process name
Creator process
User
Process ID
Command line
Timestamp
```

Query recent events:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    Id=4688
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

Access may require appropriate permissions.


---

# Command-Line Auditing

Process creation becomes significantly more useful when command-line information is available.

Detection logic should avoid relying only on:

```text
powershell.exe
```

and instead consider:

```text
Parent process
Command line
User
Integrity level
Network activity
File activity
Host role
Subsequent processes
```


---

# Process Tree Analysis

Process ancestry can provide strong context.

Example:

```text
explorer.exe
     |
     v
powershell.exe
```

may be common.

Whereas an unusual chain such as:

```text
Office Application
       |
       v
Script Interpreter
       |
       v
Unexpected Child Process
```

may warrant investigation depending on the environment.

Context matters.


---

# Microsoft Defender

Microsoft Defender Antivirus provides useful prevention and telemetry.

Check:

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
                  AMEngineVersion,
                  AMProductVersion,
                  AntivirusSignatureVersion,
                  AntivirusSignatureLastUpdated
```


---

# Defender Operational Log

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 100
```

Use timestamps to correlate events with the test.


---

# Defender Threat Detection

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


---

# EICAR Validation

EICAR is a standard harmless antivirus test artifact.

Canonical test string:

```text
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

Create an authorised temporary test file:

```powershell
$eicar = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
Set-Content -Path "$env:TEMP\eicar.com.txt" -Value $eicar -NoNewline
```

Expected flow:

```text
Create File
    |
    v
Antivirus Inspection
    |
    v
Detection
    |
    v
Block / Quarantine
    |
    v
Endpoint Alert
    |
    v
Central Security Platform
```


---

# EICAR Validation Questions

Record:

```text
Was creation prevented?

Was the file immediately removed?

Was it quarantined?

Was a local notification generated?

Was a Defender event generated?

Did the EDR receive the event?

Was a central alert generated?

Did the SOC see the alert?

How long did this take?
```


---

# EICAR Is Only a Baseline

EICAR demonstrates basic antivirus handling.

It does not validate detection of:

```text
Credential access
Persistence
Lateral movement
PowerShell abuse
Identity attacks
C2
Privilege escalation
Cloud attacks
```

Use behaviour-specific simulations for these.


---

# AMSI

The Antimalware Scan Interface allows compatible applications to submit content to antimalware providers.

Simplified model:

```text
Script Content
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

AMSI should be evaluated together with:

```text
PowerShell
Defender
EDR
Application Control
Logging
```


---

# AMSI Detection Validation

The objective is not automatically to bypass AMSI.

First establish:

```text
Does the application use AMSI?

Does the security provider inspect the content?

Is suspicious content detected?

Does the endpoint generate telemetry?

Does the central platform receive the result?
```

Use vendor-provided test content where available.


---

# AMSI Bypass Detection

If bypass simulation is explicitly part of the assessment, defenders should look for behaviour associated with interference with security interfaces rather than relying solely on one known bypass implementation.

Potential detection dimensions include:

```text
Suspicious memory modification
Unexpected reflection behaviour
Security-interface tampering
Unusual PowerShell host behaviour
Process ancestry
Script telemetry
EDR behavioural detections
```

A red team assessment should stop once the security boundary and detection outcome are sufficiently demonstrated.


---

# PowerShell Telemetry

PowerShell can provide several useful logging sources:

```text
Script Block Logging
Module Logging
Transcription
PowerShell Operational events
Process creation
AMSI
EDR telemetry
```


---

# PowerShell Operational Log

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 100
```


---

# Script Block Logging

Potential policy location:

```text
HKLM\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging
```

Query:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' -ErrorAction SilentlyContinue
```


---

# Event ID 4104

PowerShell Script Block Logging commonly uses:

```text
4104
```

Query:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-PowerShell/Operational'
    Id=4104
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```


---

# PowerShell Module Logging

Potential policy location:

```text
HKLM\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging
```

Query:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ModuleLogging' -ErrorAction SilentlyContinue
```


---

# PowerShell Transcription

Potential policy location:

```text
HKLM\Software\Policies\Microsoft\Windows\PowerShell\Transcription
```

Query:

```powershell
Get-ItemProperty 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\Transcription' -ErrorAction SilentlyContinue
```

Transcripts may contain sensitive information.

Protect their storage appropriately.


---

# PowerShell Language Mode

Check:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Detection validation should distinguish:

```text
Control prevented activity

from

Control allowed activity but EDR detected it
```

For example, Constrained Language Mode is primarily a restriction mechanism, while PowerShell logging provides visibility.


---

# AppLocker Telemetry

AppLocker logs can provide useful application-control events.

Relevant logs include:

```text
Microsoft-Windows-AppLocker/EXE and DLL
Microsoft-Windows-AppLocker/MSI and Script
```


---

# AppLocker EXE and DLL

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 100
```


---

# AppLocker MSI and Script

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/MSI and Script' -MaxEvents 100
```


---

# AppLocker Effective Policy

```powershell
Get-AppLockerPolicy -Effective
```

Summarise collections:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```


---

# AppLocker Detection Test

For a harmless existing binary:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy -Path "$env:WINDIR\System32\rundll32.exe" -User "$env:USERDOMAIN\$env:USERNAME"
```

The result helps establish expected policy behaviour before execution.


---

# Application Control Validation

```text
Policy Says Deny
      |
      v
Safe Execution Attempt
      |
      +--> Blocked
      |       |
      |       v
      |    Event Generated?
      |
      +--> Allowed
              |
              v
          Policy Gap?
```


---

# WDAC and Code Integrity

Windows Defender Application Control is closely associated with Code Integrity telemetry.

Useful log:

```text
Microsoft-Windows-CodeIntegrity/Operational
```

Query:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 100
```


---

# WDAC Validation Questions

Determine:

```text
Is policy present?

Is it enforced?

Is it audit-only?

Was execution allowed?

Was execution blocked?

Was a Code Integrity event generated?

Did the EDR receive the event?

Did the SIEM receive the event?
```


---

# Attack Surface Reduction

Attack Surface Reduction rules can operate as both prevention and detection controls.

Query:

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```


---

# ASR Validation Model

```text
ASR Rule
   |
   v
Configured?
   |
   v
Mode?
   |
   +--> Block
   |
   +--> Audit
   |
   +--> Warn
   |
   +--> Disabled
```

Then perform an approved safe test appropriate to that specific rule.


---

# ASR Detection Questions

Record:

```text
Rule ID
Rule name
Configured action
Test
Expected result
Observed result
Defender event
EDR event
SIEM alert
SOC response
```


---

# Sysmon

Sysmon provides detailed Windows telemetry when installed and configured.

Check whether the service exists:

```powershell
Get-Service Sysmon* -ErrorAction SilentlyContinue
```

Common log:

```text
Microsoft-Windows-Sysmon/Operational
```


---

# Query Sysmon

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 100
```


---

# Common Sysmon Event IDs

Exact visibility depends heavily on the deployed Sysmon configuration.

| Event ID | Common Meaning |
|---|---|
| 1 | Process creation |
| 2 | File creation time changed |
| 3 | Network connection |
| 5 | Process terminated |
| 6 | Driver loaded |
| 7 | Image loaded |
| 8 | CreateRemoteThread |
| 10 | Process access |
| 11 | File created |
| 12 | Registry object create/delete |
| 13 | Registry value set |
| 14 | Registry object renamed |
| 15 | FileCreateStreamHash |
| 17 | Pipe created |
| 18 | Pipe connected |
| 22 | DNS query |
| 23 | File delete |
| 25 | Process tampering |
| 26 | File delete detected |


---

# Sysmon Event ID 1

Process creation:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    Id=1
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```


---

# Sysmon Event ID 3

Network connections:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    Id=3
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

Network connection logging depends on the Sysmon configuration.


---

# Sysmon Event ID 22

DNS queries:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    Id=22
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```


---

# Sysmon Configuration Matters

Do not write:

```text
Sysmon installed, therefore detection coverage is good.
```

A weak configuration may exclude the exact behaviour defenders need.

Validate:

```text
Which event types are enabled?

Which processes are excluded?

Which paths are excluded?

Which network connections are captured?

Are events forwarded?

Are they used by detection rules?
```


---

# Windows Event Forwarding

Windows Event Forwarding can centralise Windows events.

Conceptually:

```text
Windows Endpoint
      |
      v
Event Log
      |
      v
Windows Event Forwarding
      |
      v
Collector
      |
      v
SIEM
```

Validation should confirm the event reaches the final security platform, not merely the local endpoint.


---

# EDR Validation

An EDR platform typically provides more than antivirus.

Capabilities may include:

```text
Process telemetry
File telemetry
Network telemetry
Identity context
Behavioural detection
Threat intelligence
Alerting
Investigation
Response
Isolation
Live response
```


---

# EDR Detection Lifecycle

```text
Technique
   |
   v
Sensor Observes
   |
   v
Telemetry Uploaded
   |
   v
Analytics
   |
   v
Detection
   |
   v
Alert
   |
   v
Analyst
```


---

# EDR Test Questions

For every significant test:

```text
Did the EDR record the process?

Did it record the command line?

Did it record the parent process?

Did it record the user?

Did it record network activity?

Did it identify the technique?

Did it generate an alert?

Was the alert severity appropriate?

Did it correlate related activity?

Did the SOC investigate it?
```


---

# Antivirus vs EDR

Do not treat them as identical.

```text
Antivirus
   |
   +--> File/content detection
   +--> Malware prevention
   +--> Behaviour protection

EDR
   |
   +--> Endpoint telemetry
   +--> Behaviour analytics
   +--> Investigation
   +--> Detection
   +--> Response
```

Products may integrate both capabilities, but the assessment questions remain different.


---

# Network Telemetry

Host telemetry should be correlated with network visibility.

Sources may include:

```text
Firewall
Proxy
DNS
IDS
IPS
NDR
VPN
Load balancer
Web proxy
Secure web gateway
Cloud firewall
```


---

# Network Detection Model

```text
Process
   |
   v
Connection
   |
   v
Endpoint Telemetry
   |
   +----------------+
   |                |
   v                v
Firewall          Proxy
   |                |
   +-------+--------+
           |
           v
          SIEM
```


---

# DNS Detection

DNS can reveal activity that process-only monitoring misses.

Useful context includes:

```text
Host
User
Query
Timestamp
Resolver
Domain age
Frequency
Response
Associated process
```


---

# DNS Test

Resolve an assessment-controlled domain:

```powershell
Resolve-DnsName test.example.com
```

or:

```powershell
nslookup test.example.com
```

Use a domain that is authorised for the assessment.


---

# Network Connectivity

Test TCP reachability:

```powershell
Test-NetConnection HOST -Port 443
```

Record:

```text
Source host
Destination
Port
Timestamp
Result
Firewall event
EDR event
SIEM event
```


---

# HTTP Visibility

A controlled HTTP request can validate:

```text
Proxy telemetry
Firewall telemetry
Endpoint network telemetry
DNS
TLS inspection
URL filtering
```

Example:

```powershell
Invoke-WebRequest -Uri 'https://example.com/' -UseBasicParsing
```

Use an approved destination for actual validation.


---

# Command and Control Detection

C2 validation should focus on observable behaviour rather than only specific framework signatures.

Relevant dimensions include:

```text
Process initiating connection
Destination
Port
Protocol
Connection frequency
DNS
TLS
Proxy metadata
User context
Host role
Connection duration
```


---

# C2 Detection Model

```text
Assessment Process
       |
       v
Outbound Connection
       |
       +--> Endpoint Telemetry
       |
       +--> DNS
       |
       +--> Firewall
       |
       +--> Proxy
       |
       +--> NDR
       |
       v
      SIEM
       |
       v
Detection / Correlation
```

See:

[Command and Control](command-and-control.md)


---

# Lateral Movement Detection

Lateral movement may produce telemetry across multiple systems.

```text
Source Host
    |
    | Authentication
    v
Target Host
    |
    v
Remote Activity
```

Potential evidence includes:

```text
Source endpoint process
Authentication event
Target logon
Network connection
Remote service activity
EDR event
SIEM correlation
```


---

# Windows Authentication Events

Useful events can include:

```text
4624 - Successful logon
4625 - Failed logon
4648 - Explicit credentials
4768 - Kerberos TGT
4769 - Kerberos service ticket
4771 - Kerberos pre-authentication failure
4776 - NTLM validation
```


---

# Logon Types

Windows logon events include a logon type.

Common examples include:

```text
2  - Interactive
3  - Network
4  - Batch
5  - Service
7  - Unlock
8  - NetworkCleartext
9  - NewCredentials
10 - RemoteInteractive
11 - CachedInteractive
```

The logon type can help explain how authentication occurred.


---

# Lateral Movement Correlation

Example:

```text
WS01
 |
 | Remote authentication
 v
SRV01
```

Detection should attempt to correlate:

```text
WS01 process
      +
WS01 network connection
      +
SRV01 logon
      +
SRV01 process creation
```


---

# Privilege Escalation Detection

Privilege escalation tests may generate:

```text
Process creation
Service events
Scheduled-task events
File modifications
Registry changes
Privilege assignment
Application-control events
EDR alerts
```


---

# Service Detection

Relevant Windows telemetry may include:

```text
Service installation
Service start
Service configuration change
Process creation
```

Security Event ID:

```text
4697
```

may record service installation when appropriate auditing is enabled.

System logs may also provide service-control events.


---

# Scheduled Task Detection

Relevant Security events can include:

```text
4698 - Scheduled task created
4702 - Scheduled task updated
```

Task Scheduler also maintains operational telemetry.


---

# Persistence Detection

Persistence detection should focus on changes that survive normal process termination or logon cycles.

Potential areas include:

```text
Services
Scheduled tasks
Startup locations
Registry
Accounts
SSH keys
Cloud identities
Certificates
Application configuration
```


---

# Credential Access Detection

Credential-access testing can be high impact.

Use controlled simulations and explicit authorisation.

Detection dimensions may include:

```text
Sensitive process access
Credential store access
Suspicious authentication
Directory replication behaviour
Browser credential access
Security-account database access
Unusual ticket activity
EDR behavioural alerts
```


---

# Credential Access Correlation

```text
Process
   |
   v
Sensitive Resource Access
   |
   v
Credential Material
   |
   v
Subsequent Authentication
```

A mature detection strategy should attempt to correlate credential access with later use.


---

# Identity Detection

Identity telemetry is increasingly important.

Potential sources include:

```text
Active Directory
Microsoft Entra ID
VPN
SSO
MFA
PAM
Cloud IAM
Application authentication
```


---

# Identity Detection Questions

Consider:

```text
Was the login expected?

Was the source expected?

Was MFA used?

Was the device trusted?

Was privilege unusual?

Was authentication followed by unusual activity?

Was the identity recently compromised?

Was there impossible or abnormal access?
```


---

# Active Directory Detection

Potential AD detection areas include:

```text
Password spraying
Kerberos abuse
NTLM activity
Privilege-group changes
ACL changes
Account creation
Delegation changes
AD CS activity
Directory replication
Trust changes
GPO changes
```


---

# Password Spray Validation

If explicitly authorised, detection validation should focus on controlled authentication patterns and avoid unnecessary account lockouts.

Measure:

```text
Authentication failures
Source
Target accounts
Lockout behaviour
Identity alerts
SIEM correlation
SOC response
```

Do not exceed agreed authentication thresholds.


---

# Kerberos Visibility

Useful events include:

```text
4768
4769
4771
```

Detection should consider:

```text
Account
Service
Encryption type
Source address
Failure code
Volume
Timing
```


---

# NTLM Visibility

Event:

```text
4776
```

can provide NTLM credential validation information in relevant circumstances.

NTLM should be evaluated alongside:

```text
Source
Target
Account
Protocol
Host role
Expected authentication behaviour
```


---

# Cloud Detection

Modern attack paths may move between endpoint and cloud environments.

Potential telemetry includes:

```text
Interactive sign-ins
Non-interactive sign-ins
Service principals
Role changes
Application consent
Token activity
Mailbox activity
Cloud audit logs
Conditional Access
Resource changes
```


---

# SIEM Validation

The SIEM should receive the telemetry required for detection.

Validate:

```text
Source generates event
        |
        v
Collector receives event
        |
        v
SIEM ingests event
        |
        v
Fields parsed
        |
        v
Detection rule evaluates
        |
        v
Alert generated
```


---

# SIEM Ingestion Gap

A common problem is:

```text
Endpoint Event Exists
       |
       v
SIEM Event Missing
```

Potential causes include:

```text
Forwarder failure
Collector failure
Filtering
Licensing
Retention policy
Parsing issue
Connector issue
Network problem
Misconfiguration
```


---

# Parsing Validation

An event reaching the SIEM is not enough.

Important fields should be usable.

Examples:

```text
Hostname
Username
Process
Parent process
Command line
Source IP
Destination IP
Destination port
Event ID
Timestamp
Hash
Domain
```


---

# Detection Rule Validation

A rule should be tested against known expected behaviour.

```text
Known Test
    |
    v
Expected Telemetry
    |
    v
Detection Query
    |
    v
Expected Match
    |
   / \
 No   Yes
 |     |
 v     v
Fix   Alert
```


---

# Detection Rule Quality

Review:

```text
Coverage
Precision
False positives
False negatives
Context
Severity
Suppression
Thresholds
Dependencies
Data sources
Response guidance
```


---

# Detection Rule Documentation

A useful rule record contains:

```text
Rule name
Description
ATT&CK technique
Data source
Required fields
Detection logic
Known false positives
Severity
Triage guidance
Response guidance
Test procedure
Last validation date
```


---

# Atomic Red Team

Atomic Red Team provides small tests mapped to ATT&CK techniques.

It is useful for controlled detection validation when each test is reviewed before execution.

Workflow:

```text
Select ATT&CK Technique
        |
        v
Select Atomic Test
        |
        v
Read Test
        |
        v
Review Prerequisites
        |
        v
Review Impact
        |
        v
Review Cleanup
        |
        v
Approve
        |
        v
Run One Test
        |
        v
Collect Telemetry
        |
        v
Cleanup
        |
        v
Verify
```


---

# Atomic Test Selection

Do not select tests only because they are easy to execute.

Select tests based on:

```text
Threat model
Attack path
Missing detection
Business risk
Security-control objective
Previous incident
Known ATT&CK gap
```


---

# Atomic Test Record

Example:

```text
Test ID:
RT-DV-014

ATT&CK:
T1059.001

Atomic:
Reviewed and approved test

Host:
WS01

Expected telemetry:
Process creation
PowerShell Operational
EDR process event

Expected alert:
Suspicious PowerShell activity

Cleanup:
Reviewed before execution
```


---

# Do Not Bulk Execute Tests

Avoid:

```text
Run every atomic
        |
        v
Generate thousands of events
        |
        v
Unknown system impact
        |
        v
Poor diagnostic value
```

Prefer:

```text
One hypothesis
      |
      v
One controlled test
      |
      v
Review
      |
      v
Improve
      |
      v
Retest
```


---

# MITRE ATT&CK Coverage

ATT&CK can help structure detection validation.

Example:

| ATT&CK Tactic | Technique | Test | Telemetry | Detection | Status |
|---|---|---|---|---|---|
| Execution | PowerShell | RT-DV-001 | Yes | Yes | Covered |
| Persistence | Scheduled Task | RT-DV-002 | Yes | No | Gap |
| Credential Access | Test simulation | RT-DV-003 | Yes | Yes | Covered |
| Lateral Movement | Remote service | RT-DV-004 | Yes | No | Gap |
| C2 | Controlled HTTPS | RT-DV-005 | Partial | No | Gap |


---

# ATT&CK Coverage Is Not Binary

Do not simply write:

```text
T1059.001 = Covered
```

Coverage depends on:

```text
Technique variation
Operating system
User context
Execution method
Data source
Detection rule
Security product
Environment
```


---

# Coverage Levels

A useful model is:

```text
0 - No telemetry

1 - Telemetry available

2 - Detection exists

3 - Alert enriched

4 - Analyst can investigate

5 - Response procedure validated
```


---

# Detection Coverage Matrix

Example:

| Technique | Telemetry | Detection | Alert | Investigation | Response |
|---|---:|---:|---:|---:|---:|
| PowerShell | Yes | Yes | Yes | Yes | Yes |
| Scheduled Task | Yes | No | No | No | No |
| Service Creation | Yes | Yes | Yes | Yes | No |
| C2 HTTPS | Partial | No | No | No | No |
| Lateral Movement | Yes | Yes | Yes | Yes | Yes |


---

# ATT&CK Heatmap Interpretation

A heatmap should represent tested coverage, not assumed coverage.

Avoid marking a technique green simply because:

```text
EDR vendor says it supports the technique.
```

Prefer:

```text
Technique actually tested
        |
        v
Telemetry confirmed
        |
        v
Detection confirmed
        |
        v
SOC response confirmed
```


---

# Detection Hypothesis

Detection engineering works well when expressed as a hypothesis.

Example:

```text
If a standard workstation launches an unusual script interpreter
that subsequently establishes an outbound connection, the endpoint
and network telemetry should allow the SOC to identify and
investigate the behaviour.
```

Then design a safe test around that hypothesis.


---

# Behaviour-Based Detection

Avoid relying entirely on:

```text
Tool name
File name
Known hash
Exact command
Exact string
```

Consider behaviour:

```text
Process ancestry
Identity
Privilege
Destination
Authentication
Resource access
Sequence
Timing
Host role
```


---

# Detection Chain

Individual low-confidence events can become meaningful when correlated.

```text
Unusual Process
      |
      v
Credential Access
      |
      v
Remote Authentication
      |
      v
New Host Process
      |
      v
Outbound Connection
```

Each event alone may be ambiguous.

Together they describe an attack path.


---

# Correlation

Useful correlation dimensions include:

```text
Same user
Same source host
Same destination
Same process tree
Short time window
Credential use
Network connection
Privilege change
```


---

# Detection Timing

Record at least:

```text
T0 - Test begins

T1 - Endpoint event generated

T2 - Event reaches SIEM

T3 - Alert generated

T4 - Analyst acknowledges

T5 - Investigation begins

T6 - Containment begins
```


---

# Time to Detect

```text
TTD = Alert Time - Activity Start Time
```


---

# Mean Time to Detect

Across multiple tests:

```text
MTTD = Sum of Detection Times / Number of Detected Tests
```

Be careful with small sample sizes.

A few controlled tests should not be presented as statistically representative of all incidents.


---

# Time to Triage

```text
TTT = Analyst Triage Time - Alert Time
```


---

# Time to Respond

A practical measurement may be:

```text
TTR = Response Action Time - Detection Time
```

Define the organisation's metric before comparing results.


---

# Example Timeline

```text
10:00:00 - Test starts

10:00:04 - Endpoint telemetry generated

10:00:19 - SIEM receives event

10:00:31 - Detection rule triggers

10:02:10 - Analyst acknowledges alert

10:05:22 - Investigation begins

10:09:40 - Host containment initiated
```


---

# Detection Gap Categories

Not all failures are the same.

Useful categories include:

```text
Telemetry Gap
Collection Gap
Parsing Gap
Detection Gap
Correlation Gap
Alerting Gap
Triage Gap
Investigation Gap
Response Gap
```


---

# Telemetry Gap

```text
Activity occurred
      |
      v
No relevant event generated
```

Potential remediation:

```text
Enable audit source
Deploy endpoint telemetry
Improve Sysmon configuration
Enable PowerShell logging
Enable identity auditing
Add network visibility
```


---

# Collection Gap

```text
Local Event Exists
      |
      v
Central Platform Missing Event
```

Potential remediation:

```text
Fix forwarding
Fix connector
Review filters
Review ingestion
Review licensing
Review network path
```


---

# Parsing Gap

```text
Event Ingested
      |
      v
Important Fields Missing
```

Potential remediation:

```text
Fix parser
Fix normalisation
Preserve raw event
Map identity fields
Map process fields
Map network fields
```


---

# Detection Gap

```text
Telemetry Exists
      |
      v
No Rule Detects Behaviour
```

Potential remediation:

```text
Create detection
Improve analytics
Add correlation
Tune threshold
Add context
```


---

# Alerting Gap

```text
Rule Matches
    |
    v
Alert Not Reaching Analyst
```

Review:

```text
Routing
Severity
Suppression
Notification
Queue
Case creation
Integration
```


---

# Triage Gap

```text
Alert Exists
    |
    v
Incorrectly Closed
```

Potential causes:

```text
Insufficient context
Weak playbook
Analyst training
Alert fatigue
Poor enrichment
Incorrect severity
```


---

# Response Gap

```text
Attack Detected
      |
      v
Organisation Cannot Contain
```

Review:

```text
Authority
Processes
EDR response capability
Identity suspension
Network isolation
Communication
Escalation
```


---

# Detection Gap Severity

Severity should consider:

```text
Technique impact
Attack-path position
Privilege
Asset criticality
Telemetry availability
Ease of detection engineering
Existing compensating controls
Repeatability
Threat relevance
```


---

# Example Detection Finding

## Title

```text
PowerShell Script Execution Was Logged but Did Not Generate an Alert
```

## Observation

```text
PowerShell Script Block Logging recorded the controlled assessment
activity on the workstation.

The corresponding events were successfully forwarded to the SIEM.

No detection rule generated an alert for the tested behaviour.
```

## Impact

```text
An attacker may be able to perform similar script-based activity
without generating an actionable SOC alert, despite the required
telemetry being available.
```

## Root Cause

```text
Telemetry was present but detection logic did not identify the
tested behaviour.
```

## Recommendation

```text
Develop and validate behaviour-focused PowerShell analytics using
process ancestry, script telemetry, user context, and related
network activity rather than relying solely on static strings.
```


---

# Example Collection Finding

## Title

```text
Endpoint Security Events Were Not Forwarded to the SIEM
```

## Observation

```text
The controlled test generated the expected event locally.

The event could not be located in the central SIEM during the
assessment window.
```

## Root Cause

Investigate:

```text
Forwarder
Collector
Filtering
Connector
Network
Ingestion
```


---

# Positive Detection Finding

Not every result should describe a weakness.

Example:

```text
The controlled lateral-movement simulation generated endpoint,
authentication, and network telemetry.

The SIEM correlated the events and generated a high-confidence
alert within 42 seconds.

The SOC acknowledged the alert within three minutes and correctly
identified both the source and target systems.
```

This is valuable evidence of effective security controls.


---

# SOC Validation

Detection engineering is incomplete without analyst validation.

Questions include:

```text
Did the analyst receive the alert?

Did they understand it?

Did they identify the user?

Did they identify the source?

Did they identify the target?

Did they reconstruct the attack path?

Did they escalate appropriately?

Did they contain the activity?

Did they preserve evidence?
```


---

# Blind Red Team

In a blind assessment, the SOC may not know the exact timing or techniques.

This can measure realistic detection and response.

However, the assessment still requires:

```text
Authorisation
Emergency communication
Stop conditions
Safety monitoring
```


---

# Purple Team Validation

Purple teaming enables direct collaboration.

```text
Red Team Executes
       |
       v
Blue Team Observes
       |
       v
Compare Telemetry
       |
       v
Identify Gap
       |
       v
Improve Detection
       |
       v
Red Team Repeats
       |
       v
Confirm Improvement
```

This is especially useful for detection engineering.


---

# Purple Team Test Cycle

A practical cycle:

```text
1. Select technique

2. Define expected telemetry

3. Execute controlled test

4. Blue team searches telemetry

5. Compare expected vs observed

6. Identify missing data

7. Create or improve detection

8. Repeat test

9. Validate alert

10. Document result
```


---

# Retesting

Every detection improvement should be retested.

```text
Original Test
      |
      v
Detection Failed
      |
      v
Rule Improved
      |
      v
Same Test Repeated
      |
      v
Detection Succeeds
```


---

# Use the Same Test

Changing the test during retesting makes comparison harder.

Record:

```text
Same host class
Same user privilege
Same technique
Same test parameters
Same expected telemetry
```

where practical.


---

# Regression Testing

A detection that works today may stop working after:

```text
EDR update
SIEM migration
Parser change
Operating-system update
Logging change
Rule modification
Infrastructure change
Agent failure
```

Important detections should therefore be validated periodically.


---

# Detection-as-Code

Where supported, detection rules should be version controlled.

Benefits include:

```text
Change history
Peer review
Testing
Rollback
Documentation
Automation
Consistency
```


---

# Sigma

Sigma provides a generic format for expressing log-based detection logic.

Conceptually:

```yaml
title: Example Detection
logsource:
  category: process_creation
  product: windows

detection:
  selection:
    Image|endswith: '\example.exe'

  condition: selection
```

This is only an illustrative structure.

Production detections require environment-specific context, exclusions, validation, and tuning.


---

# Sigma Workflow

```text
Detection Hypothesis
      |
      v
Sigma / Native Rule
      |
      v
Test Dataset
      |
      v
Controlled Validation
      |
      v
Tune
      |
      v
Deploy
      |
      v
Monitor
      |
      v
Retest
```


---

# False Positives

A detection that alerts constantly may become operationally ineffective.

During testing record:

```text
Expected legitimate behaviour
Alert frequency
Affected user groups
Affected systems
Known administrative tools
Developer workflows
Automation
Service accounts
```


---

# False Negatives

A false negative occurs when behaviour that should have been detected is missed.

Potential causes include:

```text
Missing telemetry
Incorrect query
Overly strict conditions
Unexpected technique variation
Parser failure
Suppression
Incorrect field mapping
Sensor failure
```


---

# Detection Tuning

Avoid tuning exclusively around the exact red team command.

Weak:

```text
Alert when command line contains exact-test-string.
```

Better:

```text
Detect unusual behaviour based on process relationships,
identity, execution context, and related activity.
```


---

# Detection Resilience

A resilient detection should survive minor variations.

Consider whether the detection still works when:

```text
Filename changes
Path changes
Whitespace changes
Parent process changes
User changes
Destination changes
Command syntax changes
```

Testing such variations should remain controlled and aligned with the threat model.


---

# Detection Enrichment

Useful alert enrichment includes:

```text
Hostname
User
Department
Asset criticality
Process
Parent process
Command line
Hash
Signature
Source IP
Destination IP
Domain
Threat intelligence
Recent authentication
Related alerts
```


---

# Asset Context

The same activity may have different importance on:

```text
Developer workstation
Standard workstation
Domain controller
Certificate authority
Jump server
Backup server
Privileged workstation
Production database
```

Detection severity should consider host role.


---

# Identity Context

Likewise:

```text
Standard user
Service account
Administrator
Domain administrator
Break-glass account
Application identity
```

should influence detection priority.


---

# Detection Evidence

For each validation collect:

```text
Test ID
Technique
ATT&CK mapping
Timestamp
Host
User
Privilege
Command or action
Expected telemetry
Observed telemetry
Endpoint event
SIEM event
Detection rule
Alert
SOC response
Result
Cleanup
```


---

# Screenshot Evidence

Useful screenshots may include:

```text
Local event
EDR process tree
SIEM query
Detection alert
SOC case
Timeline
Response action
```

Use a consistent naming convention:

```text
YYYYMMDD-HHMM-testid-host-description.png
```


---

# Detection Validation Table

Example:

| Test ID | Technique | Prevented | Telemetry | Alert | SOC | Result |
|---|---|---:|---:|---:|---:|---|
| DV-001 | EICAR | Yes | Yes | Yes | Yes | Pass |
| DV-002 | PowerShell | No | Yes | Yes | Yes | Pass |
| DV-003 | Scheduled Task | No | Yes | No | No | Gap |
| DV-004 | Lateral Movement | No | Yes | Yes | Yes | Pass |
| DV-005 | HTTPS C2 simulation | No | Partial | No | No | Gap |


---

# Result Classification

A useful classification:

```text
PASS
Expected prevention/detection/response occurred.

PARTIAL
Some expected controls worked but important gaps remain.

FAIL
Expected control did not function.

NOT TESTED
Technique was not executed.

NOT APPLICABLE
Technique does not apply to the environment.
```


---

# Detection Maturity Model

```text
Level 0
No telemetry

Level 1
Telemetry available locally

Level 2
Telemetry centralised

Level 3
Detection exists

Level 4
Alert enriched and actionable

Level 5
SOC response validated

Level 6
Detection continuously tested
```


---

# Detection Validation Dashboard

Useful summary metrics:

```text
Tests executed
Tests prevented
Tests detected
Tests logged only
Tests invisible
Alerts generated
Alerts investigated
Mean time to detect
Mean time to triage
ATT&CK techniques tested
Detection gaps
Retests passed
```


---

# Example Metrics

```text
Tests executed:              24

Prevented:                    6

Allowed but detected:        11

Logged but not detected:      5

No useful visibility:         2

SOC investigated:            13

Retests passed:               7 / 8
```


---

# Prevention Rate

```text
Prevention Rate =
Prevented Tests / Total Applicable Tests
```


---

# Detection Rate

For tests that were actually observable and expected to generate detection:

```text
Detection Rate =
Detected Tests / Detection-Expected Tests
```

Define the denominator clearly in reports.


---

# Visibility Rate

```text
Visibility Rate =
Tests with Useful Telemetry / Tests Executed
```


---

# Investigation Rate

```text
Investigation Rate =
Alerts Investigated / Alerts Generated
```


---

# Metrics Need Context

Do not write:

```text
EDR detected 80 percent of attacks.
```

when only five selected tests were performed.

Prefer:

```text
Eight of the ten controlled techniques selected for this
assessment generated the expected EDR alert.
```

This accurately describes the tested sample.


---

# Detection Validation Checklist

## Preparation

- [ ] Written authorisation confirmed
- [ ] Scope confirmed
- [ ] Detection-validation objective defined
- [ ] SOC coordination model defined
- [ ] Stop conditions defined
- [ ] Emergency contact confirmed
- [ ] Test IDs assigned
- [ ] Time synchronisation checked
- [ ] Evidence location prepared

## Baseline

- [ ] Host recorded
- [ ] User recorded
- [ ] Privilege recorded
- [ ] OS recorded
- [ ] EDR identified
- [ ] Antivirus identified
- [ ] Defender status recorded where relevant
- [ ] PowerShell version recorded
- [ ] Language mode recorded
- [ ] Audit policy reviewed
- [ ] Sysmon checked
- [ ] Application control checked

## Endpoint

- [ ] Process telemetry validated
- [ ] Command-line telemetry validated
- [ ] Parent-child telemetry validated
- [ ] File telemetry considered
- [ ] Registry telemetry considered
- [ ] Network telemetry considered
- [ ] DNS telemetry considered
- [ ] Authentication telemetry considered

## Defender

- [ ] Defender status recorded
- [ ] Real-time protection recorded
- [ ] Behaviour monitoring recorded
- [ ] Signature version recorded
- [ ] EICAR tested where appropriate
- [ ] Defender Operational log checked
- [ ] Threat detection checked
- [ ] Central alert checked

## PowerShell

- [ ] Operational logging checked
- [ ] Script Block Logging checked
- [ ] Module Logging checked
- [ ] Transcription considered
- [ ] AMSI considered
- [ ] Language Mode recorded
- [ ] EDR visibility checked

## Application Control

- [ ] AppLocker policy checked
- [ ] AppLocker logs checked
- [ ] WDAC considered
- [ ] Code Integrity logs checked
- [ ] Block events validated
- [ ] Audit events validated where applicable

## ASR

- [ ] Rules enumerated
- [ ] Actions recorded
- [ ] Relevant rules selected
- [ ] Safe tests performed
- [ ] Defender events checked
- [ ] EDR alerts checked
- [ ] SIEM alerts checked

## Sysmon

- [ ] Sysmon presence checked
- [ ] Configuration considered
- [ ] Process creation checked
- [ ] Network events checked
- [ ] DNS events checked
- [ ] File events considered
- [ ] Registry events considered
- [ ] Forwarding checked

## Identity

- [ ] Successful logons considered
- [ ] Failed logons considered
- [ ] Explicit credentials considered
- [ ] Kerberos telemetry considered
- [ ] NTLM telemetry considered
- [ ] Privileged group changes considered
- [ ] Cloud identity telemetry considered where applicable

## Network

- [ ] Firewall visibility checked
- [ ] Proxy visibility checked
- [ ] DNS visibility checked
- [ ] IDS/NDR considered
- [ ] VPN telemetry considered
- [ ] Endpoint network telemetry correlated

## SIEM

- [ ] Event generated locally
- [ ] Event received centrally
- [ ] Required fields parsed
- [ ] Detection rule evaluated
- [ ] Alert generated
- [ ] Severity appropriate
- [ ] Enrichment available
- [ ] Case created where expected

## SOC

- [ ] Alert received
- [ ] Alert acknowledged
- [ ] User identified
- [ ] Source identified
- [ ] Target identified
- [ ] Attack path understood
- [ ] Escalation performed
- [ ] Response performed where expected
- [ ] Timestamps recorded

## ATT&CK

- [ ] Technique mapped
- [ ] Expected data source documented
- [ ] Test actually executed
- [ ] Telemetry confirmed
- [ ] Detection confirmed
- [ ] Investigation confirmed
- [ ] Coverage status recorded

## Retesting

- [ ] Original test preserved
- [ ] Root cause identified
- [ ] Detection improved
- [ ] Same test repeated
- [ ] Alert confirmed
- [ ] SOC visibility confirmed
- [ ] Regression test considered

## Cleanup

- [ ] Test artifacts removed
- [ ] EICAR artifacts removed or quarantined
- [ ] Temporary scripts removed
- [ ] Temporary executables removed
- [ ] Scheduled tests removed
- [ ] Services removed if created
- [ ] Tunnels stopped
- [ ] Security configuration unchanged
- [ ] Cleanup verified


---

# Quick Reference

## Identity

```powershell
whoami /all
```

## PowerShell

```powershell
$PSVersionTable
```

## Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

## Defender

```powershell
Get-MpComputerStatus
```

## Defender Detection History

```powershell
Get-MpThreatDetection
```

## Defender Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 100
```

## EICAR

```powershell
$eicar = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
Set-Content -Path "$env:TEMP\eicar.com.txt" -Value $eicar -NoNewline
```

## PowerShell Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 100
```

## Script Block Logging

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-PowerShell/Operational'
    Id=4104
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

## Audit Policy

```powershell
auditpol /get /category:*
```

## Process Creation

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    Id=4688
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

## AppLocker

```powershell
Get-AppLockerPolicy -Effective
```

## AppLocker EXE/DLL Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/EXE and DLL' -MaxEvents 100
```

## AppLocker Script Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-AppLocker/MSI and Script' -MaxEvents 100
```

## Code Integrity

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 100
```

## ASR

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```

## Sysmon

```powershell
Get-Service Sysmon* -ErrorAction SilentlyContinue
```

## Sysmon Events

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 100
```

## Sysmon Process Creation

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    Id=1
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

## Sysmon Network Connections

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    Id=3
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

## Sysmon DNS

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-Sysmon/Operational'
    Id=22
    StartTime=(Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue
```

## TCP Connectivity

```powershell
Test-NetConnection HOST -Port 443
```

## DNS

```powershell
Resolve-DnsName HOST
```


---

# Detection Validation Decision Model

```text
                    Select Technique
                           |
                           v
                    Define Expected
                       Telemetry
                           |
                           v
                    Execute Safe Test
                           |
                           v
                    Was Prevented?
                      /        \
                    Yes         No
                    |            |
                    v            v
              Telemetry?      Telemetry?
                /   \          /    \
              No     Yes     No      Yes
              |       |       |        |
              v       v       v        v
           Visibility Record  Major   Detection?
             Gap    Control    Gap      /    \
                                      No     Yes
                                      |       |
                                      v       v
                                  Detection  Alert
                                     Gap       |
                                               v
                                          SOC Action?
                                           /      \
                                         No        Yes
                                         |          |
                                         v          v
                                     Response     PASS
                                        Gap
```


---

# Purple Team Improvement Loop

```text
                      ATT&CK Technique
                             |
                             v
                       Detection Goal
                             |
                             v
                       Controlled Test
                             |
                             v
                    Expected Telemetry?
                        /          \
                      No            Yes
                      |              |
                      v              v
                 Enable Data      Detection?
                    Source         /      \
                                No         Yes
                                |           |
                                v           v
                           Build Rule      Alert?
                                |          /   \
                                |        No     Yes
                                |        |       |
                                |        v       v
                                |      Fix    Analyst
                                |              |
                                +------+-------+
                                       |
                                       v
                                     Retest
                                       |
                                       v
                              Objective Achieved?
                                  /         \
                                No           Yes
                                |             |
                                +--> Improve  v
                                             PASS
```


---

# Final Detection Model

```text
                     RED TEAM ACTIVITY
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
       ENDPOINT           IDENTITY          NETWORK
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                        TELEMETRY
                            |
                            v
                        COLLECTION
                            |
                            v
                       NORMALISATION
                            |
                            v
                         ANALYTICS
                            |
                            v
                         DETECTION
                            |
                            v
                           ALERT
                            |
                            v
                            SOC
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
            TRIAGE     INVESTIGATION    RESPONSE
              |             |             |
              +-------------+-------------+
                            |
                            v
                         LESSONS
                            |
                            v
                       IMPROVEMENT
                            |
                            v
                          RETEST
```


---

# Core Principle

Detection validation can be reduced to:

```text
Do not ask only:

"Did the EDR alert?"

Ask:

Did the activity happen?

Was it prevented?

What telemetry was generated?

Did the telemetry reach the security platform?

Could defenders find it?

Did a detection identify it?

Was the alert actionable?

Did the SOC investigate it?

Could the organisation respond?

Did the improvement survive retesting?
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [PowerShell](../windows/powershell.md)
- [Active Directory](../active-directory/)
- [BloodHound](../active-directory/bloodhound.md)


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Data Sources](https://attack.mitre.org/datasources/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Detection Strategies](https://attack.mitre.org/detectionstrategies/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Security Auditing](https://learn.microsoft.com/windows/security/threat-protection/auditing/advanced-security-auditing){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Audit Process Creation](https://learn.microsoft.com/windows/security/threat-protection/auditing/audit-process-creation){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Logging](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_logging_windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Microsoft Defender Antivirus](https://learn.microsoft.com/defender-endpoint/microsoft-defender-antivirus-windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Antimalware Scan Interface](https://learn.microsoft.com/windows/win32/amsi/antimalware-scan-interface-portal){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - App Control for Business](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Attack Surface Reduction](https://learn.microsoft.com/defender-endpoint/attack-surface-reduction){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals - Sysmon](https://learn.microsoft.com/sysinternals/downloads/sysmon){ target="_blank" rel="noopener noreferrer" }
- [EICAR - Anti-Malware Test File](https://www.eicar.org/download-anti-malware-testfile/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Sigma](https://sigmahq.io/){ target="_blank" rel="noopener noreferrer" }
- [SigmaHQ GitHub](https://github.com/SigmaHQ/sigma){ target="_blank" rel="noopener noreferrer" }
- [MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "What good detection validation looks like"
    The strongest result is not a screenshot showing that an EDR generated an alert. A mature validation demonstrates the complete path from controlled attacker behaviour to endpoint or identity telemetry, central collection, detection, analyst investigation, and response. When a gap is identified, improve the relevant layer and repeat the same test to demonstrate that the gap has actually been closed.


!!! warning "Authorised testing only"
    Detection validation may intentionally generate security alerts and can involve authentication, endpoint execution, network connections, application-control events, and other behaviours normally associated with attacks. Coordinate tests through the Rules of Engagement, avoid uncontrolled bulk execution, protect any credentials or customer data encountered, use vendor test artifacts and controlled simulations where possible, and remove all introduced artifacts after testing.
