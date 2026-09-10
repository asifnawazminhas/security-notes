---
title: Red Teaming Tools
description: Practical red teaming tooling overview for authorised adversary simulation, including command-and-control frameworks, payload delivery, infrastructure, lateral movement support, credential access tooling, operational safety, evidence collection, and integration with red team methodology.
---

# Red Teaming Tools

Red teaming tools support authorised adversary simulation by helping operators reproduce realistic attacker behaviours across an environment.

They may be used for:

- command and control;
- payload delivery;
- operator tasking;
- credential access;
- lateral movement;
- persistence;
- collection;
- exfiltration simulation;
- infrastructure management;
- detection validation;
- reporting and replay.

A red team tool should never be treated as the objective itself.

The objective is to emulate a defined adversary behaviour safely and measure whether the organisation can prevent, detect, investigate, and respond to it.

```text
Red Team Objective
      |
      v
Adversary Behaviour
      |
      v
Choose Appropriate Tool
      |
      v
Controlled Execution
      |
      v
Telemetry
      |
      v
Detection / Response
      |
      v
Evidence
      |
      v
Assessment Conclusion
```

!!! warning "Authorised testing only"
    Use red team tooling only inside explicitly authorised engagements. Command-and-control frameworks and post-exploitation tools can provide powerful remote capabilities and may trigger or bypass security controls depending on configuration. Scope, target systems, persistence, credential access, and network communication must be agreed before use.

---

# Where Red Teaming Tools Fit

Red team tooling usually appears after objectives and rules of engagement have been defined.

```text
Threat / Objective
      |
      v
Rules of Engagement
      |
      v
Initial Access Simulation
      |
      v
Command and Control
      |
      v
Post-Exploitation
      |
      +-- Discovery
      +-- Credential Access
      +-- Lateral Movement
      +-- Persistence
      +-- Collection
      |
      v
Detection and Response Measurement
      |
      v
Cleanup
      |
      v
Reporting
```

Related methodology:

[Red Teaming](../../red-teaming/index.md)

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

---

# Core Tool Categories

A practical red team toolkit may include:

| Category | Example Tools / Technologies |
|---|---|
| Command and control | Sliver, Mythic, Havoc, commercial platforms where authorised |
| Payload hosting / delivery | HTTP servers, controlled staging infrastructure |
| Remote administration / movement | Native Windows tools, WinRM, SMB, RDP, SSH |
| AD analysis | NetExec, Impacket, BloodHound, Certipy, Rubeus |
| Credential access support | Platform-specific approved tooling |
| Network tunnelling / proxying | SOCKS, SSH, controlled tunnelling tools |
| Reconnaissance | Nmap, httpx, DNS tooling |
| Detection validation | Atomic-style controlled tests, custom test artefacts |
| Evidence | Operator logs, timestamps, screenshots, packet captures where needed |

The exact tools depend on:

- objective;
- scope;
- platform;
- detection goals;
- engagement restrictions.

---

# Command and Control

Command-and-control, commonly abbreviated C2, provides a way for an authorised operator to communicate with an implant or agent on a target system.

Conceptually:

```text
Operator
   |
   v
C2 Server
   |
   v
Network Channel
   |
   v
Agent / Implant
   |
   v
Target Host
```

A C2 framework may provide features such as:

- tasking;
- file transfer;
- process execution;
- tunnelling;
- session management;
- operator collaboration;
- logging;
- payload generation.

Detailed note:

[C2 Frameworks](c2-frameworks.md)

---

# C2 Is Not the Assessment

A common mistake is to think:

```text
C2 Session Established
      |
      v
Red Team Success
```

A better model is:

```text
C2 Session
      |
      v
Controlled Capability
      |
      v
Execute Agreed Technique
      |
      v
Observe Defensive Response
      |
      v
Measure Objective
```

A session is merely the mechanism used to conduct the authorised activity.

---

# C2 Framework Selection

Choose a framework based on the engagement.

Useful questions include:

```text
Which operating systems are in scope?

Which transports are permitted?

Which security controls are present?

Is multi-operator support needed?

Is payload generation required?

Is detailed task logging required?

Will the exercise include detection engineering?
```

Do not choose a framework solely because it is popular.

---

# Open-Source and Commercial C2

Red teams may use:

```text
Open-source frameworks
Commercial frameworks
Organisation-specific tooling
```

Each has different implications for:

- support;
- payload behaviour;
- observability;
- operator workflow;
- detection coverage;
- licensing.

The engagement should define which toolsets are acceptable.

---

# Sliver

Sliver is an open-source adversary emulation and red team framework maintained by Bishop Fox.

It supports multi-platform operations and provides capabilities associated with:

- session management;
- payload generation;
- command execution;
- network interaction;
- operator workflows.

Official project:

[Sliver - GitHub](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }

Official documentation:

[Sliver Documentation](https://sliver.sh/){ target="_blank" rel="noopener noreferrer" }

---

# Mythic

Mythic is a collaborative command-and-control platform designed around modular agents and operator workflows.

It is useful where teams need:

- multi-user operation;
- task tracking;
- agent modularity;
- browser-based management;
- collaborative adversary emulation.

Official project:

[Mythic - GitHub](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }

---

# Havoc

Havoc is another command-and-control framework used in adversary simulation and research.

As with any C2 framework, use it only within a controlled and authorised environment.

Official project:

[Havoc - GitHub](https://github.com/HavocFramework/Havoc){ target="_blank" rel="noopener noreferrer" }

---

# Framework Features vs Security Objective

The fact that a framework supports a capability does not mean it should be used.

For example:

```text
Framework supports persistence
```

does not mean:

```text
Persistence is automatically authorised
```

Similarly:

```text
Framework supports credential dumping
```

does not mean:

```text
Credential access is automatically in scope
```

The rules of engagement determine what is allowed.

---

# Rules of Engagement

Before red team tooling is deployed, document:

- target systems;
- excluded systems;
- permitted hours;
- permitted techniques;
- prohibited techniques;
- credential handling;
- persistence rules;
- data handling;
- payload storage;
- cleanup requirements;
- emergency stop procedure.

The tool should operate inside those constraints.

---

# Kill Switch

A red team engagement should define how activity can be stopped quickly.

A practical process may include:

```text
Authorised Contact
      |
      v
Stop Request
      |
      v
Operator Halts Tasks
      |
      v
Disable / Remove C2 Access
      |
      v
Confirm Cleanup
```

The exact mechanism depends on the engagement.

---

# Infrastructure

Red team infrastructure can include:

- C2 servers;
- redirectors;
- domain names;
- TLS certificates;
- cloud servers;
- DNS;
- payload hosting;
- logging infrastructure.

Infrastructure should be built specifically for the engagement or reused under a controlled internal process.

---

# Infrastructure Segmentation

Separate red team infrastructure from unrelated environments.

A practical model is:

```text
Operator Workstation
      |
      v
Red Team Infrastructure
      |
      v
Authorised Target Environment
```

Avoid routing unrelated personal or corporate traffic through engagement infrastructure.

---

# VPS Use

A VPS can provide:

- C2 hosting;
- payload hosting;
- redirectors;
- testing infrastructure.

Use:

- firewall restrictions;
- strong SSH authentication;
- minimal exposed services;
- logging;
- timely patching.

The VPS itself becomes part of the assessment infrastructure and must be secured.

---

# Firewalling Red Team Infrastructure

Restrict unnecessary inbound access.

Conceptually:

```text
Internet
   |
   v
Firewall
   |
   +-- Required management
   +-- Required C2 listener
   +-- Required web listener
   |
   X
Everything else
```

Avoid exposing management services to broad networks when not required.

---

# SSH Management

Prefer key-based authentication for management infrastructure.

Protect:

- private keys;
- operator accounts;
- sudo access;
- SSH configuration.

Do not place private keys in assessment reports or public repositories.

---

# TLS

Where HTTPS is used, TLS should provide normal transport protection.

Certificates may come from:

- public certificate authorities;
- controlled internal PKI;
- engagement-specific certificates.

TLS is not a substitute for authorisation or C2 operational security.

---

# Redirectors

A redirector can separate exposed infrastructure from the primary C2 server.

Conceptually:

```text
Agent
  |
  v
Redirector
  |
  v
C2 Server
```

Redirectors may also help:

- isolate infrastructure;
- enforce routing;
- collect network telemetry.

Use them only where the engagement architecture requires them.

---

# Payload Hosting

Red teams may need to deliver test artefacts.

Potential methods include:

- HTTP;
- HTTPS;
- SMB;
- approved software deployment mechanisms;
- removable media in physical exercises.

Hosting should be limited to authorised artefacts.

---

# Simple HTTP Hosting

For controlled lab or engagement delivery, a temporary web server may be appropriate.

Example:

```bash
python3 -m http.server 8000
```

This serves files from the current directory.

Before use:

- ensure only intended files are present;
- restrict network access where possible;
- stop the service after testing.

Do not expose sensitive assessment directories accidentally.

---

# Payload Inventory

Keep an inventory of delivered artefacts.

Example:

```text
Artifact:
test-agent.exe

Hash:
SHA256 recorded

Source:
Red team build

Target:
Authorised workstation

Purpose:
C2 connectivity validation

Cleanup:
Required
```

This makes cleanup and reporting easier.

---

# Hashing Artefacts

On Linux:

```bash
sha256sum test-agent.exe
```

On Windows:

```powershell
Get-FileHash .\test-agent.exe -Algorithm SHA256
```

Recording hashes helps prove exactly which artefact was used.

---

# Initial Access Simulation

Initial access should reproduce an agreed behaviour rather than attempt every available method.

Examples may include:

- controlled phishing simulation;
- approved file delivery;
- exposed application testing;
- assumed breach;
- pre-positioned agent;
- physical access exercise.

The chosen method should match the assessment objective.

---

# Assumed Breach

An assumed-breach engagement starts with a pre-defined foothold.

Example:

```text
Standard Domain User
      |
      +
Controlled Workstation Access
      |
      v
Internal Adversary Simulation
```

This avoids spending exercise time on initial-access techniques when internal detection and lateral movement are the real objectives.

---

# Pre-Positioned Agent

A controlled agent may be installed by administrators before the exercise.

This can reduce operational risk.

```text
Blue Team / Admin
      |
      v
Approved Test Agent
      |
      v
Red Team Begins From Agreed Position
```

This can be especially useful in purple-team exercises.

---

# Native Tools

Red team operations often benefit from native operating-system utilities.

Examples on Windows may include:

```text
whoami
hostname
ipconfig
net
nltest
sc.exe
schtasks.exe
PowerShell
```

Linux examples include:

```text
id
hostname
ip
ss
ps
systemctl
```

Native tooling can reduce the need for unnecessary third-party binaries.

---

# Native Does Not Mean Invisible

A common misconception is:

```text
Native Windows tool
      =
Undetectable
```

This is incorrect.

Native utilities can generate:

- process telemetry;
- command-line telemetry;
- network activity;
- authentication events;
- security logs.

Use them because they are appropriate, not because they are assumed to be invisible.

---

# Discovery

Discovery techniques help understand the compromised environment.

Potential areas include:

- hostname;
- current user;
- groups;
- network interfaces;
- processes;
- services;
- domain information;
- nearby systems.

The exercise should define how much discovery is necessary.

---

# Discovery Should Be Purposeful

Avoid:

```text
Run every discovery command
```

Prefer:

```text
What information do I need for the next objective?
```

For example:

```text
Need domain context
    |
    v
Query domain context only
```

This reduces unnecessary telemetry and operational impact.

---

# Active Directory Tooling

Active Directory-focused tooling may include:

- NetExec;
- Impacket;
- BloodHound;
- Certipy;
- Rubeus;
- PowerView.

Related section:

[Active Directory Tools](../active-directory/index.md)

Use these tools according to a specific AD objective.

---

# BloodHound in Red Teaming

BloodHound can help identify potential privilege paths.

Example:

```text
Current User
     |
     v
Group Relationship
     |
     v
Computer Control
     |
     v
Higher-Value Identity
```

A graph path should still be validated before operational use.

---

# NetExec in Red Teaming

NetExec can assist with:

- SMB enumeration;
- authentication validation;
- remote access mapping;
- LDAP analysis.

Avoid broad authentication attempts that could lock accounts.

---

# Impacket in Red Teaming

Impacket provides protocol tooling for authorised Windows and AD workflows.

Because many utilities can perform remote actions, use only the specific utility required for the exercise.

---

# Credential Access

Credential access is a high-impact part of red teaming.

It may involve:

- credential files;
- tokens;
- cached authentication;
- password stores;
- Kerberos material;
- application credentials.

Credential access should be explicitly covered by the rules of engagement.

---

# Use Test Credentials Where Possible

Where the exercise objective can be met without collecting real user credentials, prefer:

- synthetic accounts;
- pre-created test secrets;
- controlled canary credentials.

This reduces data-handling risk.

---

# Credential Minimisation

Do not collect more credential material than necessary.

For example:

```text
Objective:
Validate EDR detection of credential access

Required:
One controlled test identity

Not required:
Bulk collection of employee credentials
```

Align collection with the objective.

---

# Credential Storage

Any collected authentication material should be protected.

Do not place:

- passwords;
- hashes;
- tickets;
- tokens;
- private keys;

in public notes or screenshots.

---

# Lateral Movement

Lateral movement tests whether an adversary can move from one authorised host to another.

Potential mechanisms include legitimate remote administration technologies such as:

- WinRM;
- SMB;
- RDP;
- SSH;
- remote management systems.

The security question is:

```text
Why is this identity allowed to access the destination?
```

not:

```text
Which tool connected?
```

---

# Lateral Movement Scope

Every destination must be in scope.

A broad domain credential does not grant permission to access every system it can technically reach.

Maintain an explicit target list.

---

# Network Segmentation

Lateral movement testing can validate segmentation.

Example:

```text
Workstation Segment
      |
      X
Server Management Segment
```

If an authorised test identity unexpectedly reaches the protected segment, investigate the control failure.

---

# Remote Administration

Legitimate administration protocols may be used by attackers and administrators alike.

Defensive conclusions should therefore consider:

- user identity;
- source host;
- destination;
- timing;
- process lineage;
- command context.

Tool name alone is weak detection logic.

---

# Persistence

Persistence techniques cause access to survive:

- process termination;
- logout;
- reboot;
- service restart.

Persistence is often more operationally sensitive than normal execution.

Use persistence only where explicitly authorised.

---

# Persistence Validation

A lower-impact approach may be:

```text
Create controlled persistence artefact
      |
      v
Confirm detection
      |
      v
Remove immediately
```

rather than leaving it active for the remainder of the engagement.

---

# Persistence Inventory

If persistence is used, record:

```text
Host
Technique
File / registry / task / service
Creation time
Expected trigger
Cleanup time
```

No persistence mechanism should be forgotten during cleanup.

---

# Collection

Collection simulates an adversary identifying information of interest.

Prefer:

- synthetic documents;
- canary data;
- pre-approved datasets.

Avoid collecting real sensitive business information when the same objective can be demonstrated safely.

---

# Exfiltration Simulation

Exfiltration does not always require sending actual sensitive data externally.

A safer model may use:

```text
Synthetic Data
      |
      v
Controlled Transfer
      |
      v
Detection Validation
```

This proves the control objective without unnecessary data exposure.

---

# Network Tunnelling

Some operations require controlled tunnelling or proxying.

Examples include:

- SOCKS proxying;
- SSH tunnels;
- C2-supported proxying.

Tunnelling can change network reachability and should be specifically authorised.

---

# SOCKS

A SOCKS proxy can allow operator tools to reach services through an established session.

Conceptually:

```text
Operator Tool
     |
     v
SOCKS Proxy
     |
     v
Compromised Host
     |
     v
Internal Service
```

This can be useful for controlled internal testing.

---

# SSH Tunnelling

SSH can provide controlled port forwarding in Linux or mixed environments.

Use it only through authorised systems and accounts.

Document temporary forwarding so it can be removed after use.

---

# ProxyChains

ProxyChains can route compatible Linux tools through supported proxy services.

Its use should be deliberate because it can cause tools to interact with internal systems through a pivot.

Maintain scope discipline.

---

# Network Scanning Through a Pivot

Do not automatically run broad port scans through C2 or SOCKS infrastructure.

Consider:

- bandwidth;
- latency;
- target scope;
- IDS impact;
- stability.

Use focused discovery where possible.

---

# C2 Transport

C2 communications may use different transports depending on the framework.

Examples can include:

- HTTPS;
- DNS;
- other framework-supported channels.

The transport should match the exercise objective and rules.

---

# HTTPS C2

HTTPS may resemble normal encrypted web traffic at the network layer.

Detection can still use:

- destination reputation;
- process behaviour;
- TLS metadata;
- timing;
- endpoint telemetry.

Encryption does not make activity invisible.

---

# DNS-Based C2

DNS-based communication can generate distinctive query patterns.

It can also create operational load and dependencies on DNS infrastructure.

Use it only where specifically required for the exercise.

---

# Beaconing

Periodic agent check-ins may create regular network patterns.

Conceptually:

```text
Agent
 |
 +---- wait ----> callback
 |
 +---- wait ----> callback
```

Regularity can become a detection signal.

Some frameworks support configurable intervals.

Changes should remain within the exercise design.

---

# Jitter

Jitter changes timing between agent callbacks.

Its purpose in adversary simulation may be to reproduce less predictable timing.

Do not use traffic shaping solely to avoid detection unless evasion testing is specifically authorised.

---

# Detection Evasion

Red teaming may include testing whether security controls resist evasion.

This must be explicitly authorised.

There is an important distinction:

```text
Test Detection Robustness
```

versus:

```text
Disable or Destroy Security Controls
```

The latter carries substantially greater operational risk.

---

# Security Control Tampering

Avoid:

- disabling EDR;
- stopping antivirus;
- deleting logs;
- changing central security policy;

unless this is an explicit, approved objective.

Many detection objectives can be measured without tampering with defensive controls.

---

# Application Control

Windows environments may use:

- AppLocker;
- WDAC;
- Defender;
- Constrained Language Mode.

Related notes:

[Windows Application Control](../../windows/application-control.md)

[Microsoft Defender](../../windows/defender.md)

These controls are part of the environment being assessed.

---

# Red Team Response to Blocked Execution

If an artefact is blocked:

```text
Attempt
  |
  v
Control Blocks
  |
  v
Record Evidence
```

Do not automatically attempt every possible bypass.

Whether further evasion is appropriate depends on the exercise objective.

---

# Endpoint Telemetry

Red team activity may generate:

- process creation;
- parent-child process relationships;
- file writes;
- registry modification;
- module loading;
- script execution;
- network connections;
- authentication events.

This telemetry is often more valuable than whether one antivirus signature fired.

---

# Network Telemetry

Network controls may observe:

- DNS;
- proxy traffic;
- TLS connections;
- SMB;
- Kerberos;
- LDAP;
- RDP;
- SSH.

The exercise should map techniques to expected telemetry sources.

---

# Purple Team Integration

Red team tools can become controlled inputs to purple-team validation.

```text
Technique
   |
   v
Red Team Action
   |
   v
Telemetry
   |
   v
Blue Team Investigation
   |
   v
Feedback
   |
   v
Detection Improvement
```

Related section:

[Purple Teaming](../../purple-teaming/index.md)

---

# MITRE ATT&CK

MITRE ATT&CK provides a useful common language for describing adversary behaviours.

A red team test may map:

```text
Tool Action
      |
      v
Technique
      |
      v
ATT&CK ID
```

The tool itself should not be the primary mapping.

For example:

```text
PowerShell
```

can be used for many different techniques.

Map the behaviour, not merely the executable.

Official resource:

[MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }

---

# Technique Mapping

A useful test record might contain:

```text
Technique:
Service Discovery

ATT&CK:
Relevant technique identifier

Action:
Enumerated local services

Tool:
Native Windows command

Expected telemetry:
Process creation
Service enumeration
```

This is more useful than simply recording the tool name.

---

# Atomic Testing

Small, controlled tests can be useful for validating one technique at a time.

This is particularly effective for:

- purple teaming;
- detection engineering;
- regression testing.

A small test is often easier to measure than a long multi-stage C2 workflow.

---

# Operator Logs

Maintain operator logs.

Useful fields include:

```text
Timestamp
Operator
Host
User context
Technique
Command / action
Tool
Expected result
Observed result
Cleanup
```

These logs become essential during incident-response validation.

---

# Time Synchronisation

Operator, infrastructure, endpoint, SIEM, and EDR timestamps should be as aligned as practical.

Otherwise:

```text
Red Team:
14:02

EDR:
14:07

SIEM:
13:59
```

can make event correlation unnecessarily difficult.

---

# Timestamp Discipline

Use a consistent timezone for reporting.

For example:

```text
UTC
```

or the engagement's agreed local timezone.

Document the timezone explicitly.

---

# Evidence Collection

For each relevant red team activity, retain:

```text
Objective:
Technique:
ATT&CK mapping:
Target:
User context:
Tool:
Tool version:
Timestamp:
Command / task:
Observed target result:
Observed defensive response:
Cleanup status:
```

This supports both offensive and defensive conclusions.

---

# Screenshots

Screenshots can be useful for:

- C2 session evidence;
- defensive alerts;
- command execution;
- blocked actions.

However, screenshots alone are weak evidence.

Prefer combining them with:

- operator logs;
- raw command output;
- EDR event details;
- SIEM events.

---

# Tool Logs

Many C2 frameworks retain:

- operator activity;
- session metadata;
- task history.

Preserve relevant logs according to engagement requirements.

Do not retain them longer than necessary if they contain sensitive information.

---

# Red Team Data Sensitivity

Operational data may contain:

- usernames;
- hostnames;
- internal IPs;
- credentials;
- hashes;
- file contents;
- business information.

Treat red team project directories as sensitive.

---

# Separate Engagement Workspaces

Use separate directories per engagement.

Example:

```text
engagements/
└── example-client/
    ├── infrastructure/
    ├── payloads/
    ├── logs/
    ├── evidence/
    └── cleanup/
```

Avoid mixing client artefacts.

---

# Artefact Naming

Use descriptive filenames.

Example:

```text
2026-09-10_ws01_process-discovery.txt
```

rather than:

```text
output1.txt
```

This makes evidence easier to correlate.

---

# Payload Versioning

If multiple payload builds are used, record:

```text
Build
Hash
Configuration
Target
Date
```

This avoids uncertainty about which binary generated which telemetry.

---

# C2 Server Security

A C2 server may contain:

- active sessions;
- credentials;
- payloads;
- operational logs.

Protect it like sensitive security infrastructure.

Recommended principles include:

- restrict management access;
- strong authentication;
- patch operating system;
- minimal services;
- firewalling;
- encrypted storage where appropriate;
- backups only where necessary.

---

# Multi-Operator Access

If several operators share a framework:

- use individual accounts where supported;
- avoid credential sharing;
- maintain audit logs;
- coordinate tasking.

This improves accountability.

---

# Operator Coordination

Without coordination, two operators may:

- duplicate actions;
- interfere with application state;
- create unnecessary noise;
- damage cleanup accuracy.

Use an agreed operation log or team channel.

---

# Tool Provenance

Use official project sources.

Record:

```text
Repository
Version / commit
Build method
Hash
```

where practical.

Avoid unknown precompiled binaries.

---

# Build Integrity

If a framework is built from source, retain:

```text
Source revision
Build environment
Build date
Output hash
```

This improves reproducibility.

---

# Supply-Chain Risk

Red team tools themselves can be compromised.

Security tooling often receives broad access to:

- credentials;
- networks;
- endpoint sessions.

Therefore verify the source before execution.

---

# Cleanup

Cleanup is part of the assessment.

Potential artefacts include:

- agents;
- binaries;
- scripts;
- scheduled tasks;
- services;
- registry entries;
- user accounts;
- certificates;
- tunnels;
- temporary files;
- payload hosting.

Every state-changing action should have a cleanup plan.

---

# Cleanup Ledger

Maintain a table such as:

| Host | Artefact | Created | Removal Required | Removed |
|---|---|---|---|---|
| WS01 | Test agent | 14:05 | Yes | Yes |
| SRV01 | Temporary file | 14:27 | Yes | Yes |
| LAB01 | Test scheduled task | 15:01 | Yes | Yes |

This reduces the chance of leaving artefacts behind.

---

# Do Not Delete Defensive Evidence

Cleanup does not mean erasing security logs.

Do not delete:

- Windows event logs;
- EDR telemetry;
- SIEM data;
- firewall logs;

unless log-tampering itself is a specifically authorised technique.

Normal cleanup removes red team artefacts, not defensive evidence.

---

# Reporting

Red team findings should describe control outcomes.

Avoid:

```text
Sliver obtained SYSTEM.
```

Prefer:

```text
The tested standard-user context could influence a privileged service
execution path, resulting in code execution as LocalSystem. The
resulting activity did not generate a timely defensive alert during the
exercise.
```

This explains:

- initial privilege;
- weakness;
- impact;
- detection outcome.

---

# Detection Findings

A red team exercise may produce findings even when prevention works.

Example:

```text
Execution prevented by WDAC
```

This may be a positive control result.

But if the organisation did not detect the attempt despite expecting detection, there may still be a visibility gap.

---

# Prevention and Detection Are Separate

A useful model is:

```text
Technique
   |
   +--> Prevention?
   |
   +--> Detection?
   |
   +--> Investigation?
   |
   +--> Response?
```

A blocked technique can still generate valuable detection evidence.

---

# Measuring Outcome

For each test, record:

```text
Prevented?
Detected?
Alerted?
Investigated?
Escalated?
Contained?
```

This provides a richer result than simply:

```text
Success / Failure
```

---

# Red Team Tool Success Does Not Equal Control Failure

If a C2 agent connects successfully, that does not automatically mean the organisation failed.

The assessment may be testing:

- post-compromise detection;
- lateral movement;
- identity security;
- response speed.

Interpret results against the agreed objective.

---

# Failed Tool Execution Does Not Equal Strong Security

Similarly:

```text
Payload blocked
```

does not prove:

```text
Environment is secure
```

Another allowed execution path may still exist.

The test proves only the specific observed condition.

---

# False Conclusions

Avoid:

```text
EDR did not alert in five minutes
    =
Undetectable
```

Possible alternative explanations include:

- delayed ingestion;
- alert routing;
- suppression;
- analyst backlog;
- missing test correlation;
- wrong telemetry source.

Validate with the defensive team.

---

# Operational Safety

Before any red team action ask:

```text
Could this disrupt production?

Could this lock an account?

Could this restart a service?

Could this corrupt data?

Could this generate large traffic?

Could this affect a third party?
```

If the answer is yes, use a lower-impact validation approach where possible.

---

# High-Risk Actions

Examples that normally deserve explicit approval include:

- password spraying;
- persistence;
- security-control tampering;
- credential dumping;
- broad lateral movement;
- production service restart;
- destructive file modification;
- kernel exploitation;
- mass scanning;
- data exfiltration.

---

# Read-Only First

A good operating principle is:

```text
Enumerate
   |
   v
Understand
   |
   v
Validate Read-Only
   |
   v
Escalate Test Intensity Only If Needed
```

This reduces avoidable risk.

---

# Stop Conditions

Define stop conditions such as:

- production instability;
- unexpected outage;
- real malware discovery;
- unintended third-party impact;
- account lockout;
- sensitive data exposure beyond agreed limits.

Operators should know who to contact immediately.

---

# Red Team Tool Selection Guide

## Need Command and Control

Use an approved C2 framework.

Examples:

```text
Sliver
Mythic
Havoc
Approved commercial framework
```

---

## Need Active Directory Analysis

Use:

```text
NetExec
Impacket
BloodHound
Certipy
Rubeus
```

as appropriate.

---

## Need Web Reconnaissance

Use:

```text
httpx
WhatWeb
Wappalyzer
Nmap
```

Related section:

[Web Enumeration Tools](../web-enumeration/index.md)

---

## Need Web Application Testing

Use:

```text
Burp Suite
ffuf
Nuclei
Katana
```

Related section:

[Web Application Testing Tools](../web-testing/index.md)

---

## Need Windows Privilege Escalation Enumeration

Use:

```text
WinPEAS
PowerUp
PrivescCheck
```

Related section:

[Privilege Escalation Tools](../privilege-escalation/index.md)

---

## Need Linux Privilege Escalation Enumeration

Use:

```text
LinPEAS
linux-smart-enumeration
```

---

# Red Team Tool Checklist

## Engagement Preparation

- [ ] Objectives documented.
- [ ] Rules of engagement approved.
- [ ] In-scope systems defined.
- [ ] Excluded systems defined.
- [ ] Approved techniques defined.
- [ ] Prohibited techniques defined.
- [ ] Emergency contacts defined.
- [ ] Stop conditions defined.
- [ ] Cleanup requirements defined.

## Infrastructure

- [ ] C2 infrastructure secured.
- [ ] Management access restricted.
- [ ] SSH keys protected.
- [ ] Firewall configured.
- [ ] Unnecessary services disabled.
- [ ] TLS configured where required.
- [ ] Infrastructure logging enabled.
- [ ] Infrastructure ownership documented.

## Payloads

- [ ] Payload source trusted.
- [ ] Build/revision recorded.
- [ ] SHA256 recorded.
- [ ] Intended target recorded.
- [ ] Delivery method authorised.
- [ ] Cleanup plan documented.

## C2

- [ ] Framework approved.
- [ ] Version recorded.
- [ ] Listener configuration documented.
- [ ] Operator accounts controlled.
- [ ] Session scope monitored.
- [ ] Tasking logged.
- [ ] Unnecessary capabilities avoided.

## Discovery

- [ ] Commands aligned with objective.
- [ ] Broad enumeration avoided where unnecessary.
- [ ] Sensitive systems excluded.
- [ ] Output protected.

## Active Directory

- [ ] Domain scope confirmed.
- [ ] Credentials handled securely.
- [ ] Account lockout risk reviewed.
- [ ] NetExec/Impacket modules selected carefully.
- [ ] BloodHound collection scoped.
- [ ] Certipy actions reviewed.
- [ ] Kerberos actions controlled.

## Credential Access

- [ ] Explicitly authorised.
- [ ] Real credentials minimised.
- [ ] Synthetic credentials used where possible.
- [ ] Credential artefacts protected.
- [ ] Validation limited to objective.

## Lateral Movement

- [ ] Destination in scope.
- [ ] Protocol approved.
- [ ] Identity understood.
- [ ] Segmentation objectives documented.
- [ ] State-changing actions minimised.

## Persistence

- [ ] Explicitly authorised.
- [ ] Technique documented.
- [ ] Trigger understood.
- [ ] Artefact recorded.
- [ ] Removal procedure tested.
- [ ] Persistence removed after objective where appropriate.

## Collection / Exfiltration

- [ ] Synthetic data used where possible.
- [ ] Data volume minimised.
- [ ] Destination controlled.
- [ ] Sensitive information protected.
- [ ] Cleanup confirmed.

## Detection Validation

- [ ] ATT&CK technique mapped.
- [ ] Expected telemetry documented.
- [ ] Action timestamp recorded.
- [ ] EDR/SIEM evidence correlated.
- [ ] Prevention measured separately from detection.
- [ ] Analyst response measured where applicable.

## Evidence

- [ ] Operator logs retained.
- [ ] Tool versions retained.
- [ ] Commands/actions retained.
- [ ] Target/user context retained.
- [ ] Relevant screenshots retained.
- [ ] Sensitive secrets redacted.
- [ ] Timezone documented.

## Cleanup

- [ ] Agents removed.
- [ ] Payloads removed.
- [ ] Scripts removed.
- [ ] Temporary services removed.
- [ ] Scheduled tasks removed.
- [ ] Persistence removed.
- [ ] Tunnels closed.
- [ ] Certificates handled appropriately.
- [ ] Test accounts handled according to plan.
- [ ] Defensive logs preserved.
- [ ] Cleanup independently confirmed.

---

# Related Tool Notes

[Security Tools](../index.md)

[C2 Frameworks](c2-frameworks.md)

[Active Directory Tools](../active-directory/index.md)

[Privilege Escalation Tools](../privilege-escalation/index.md)

[Web Enumeration Tools](../web-enumeration/index.md)

[Web Application Testing Tools](../web-testing/index.md)

---

# Related Red Team Notes

[Red Teaming](../../red-teaming/index.md)

Use the Red Teaming section as the canonical home for methodology, planning, operational phases, detection objectives, and technique-specific guidance.

The Tools section should explain how tooling supports those workflows without replacing them.

---

# Related Purple Team Notes

[Purple Teaming](../../purple-teaming/index.md)

[Purple Team Methodology](../../purple-teaming/methodology.md)

[Purple Team Exercises](../../purple-teaming/exercises.md)

[MITRE ATT&CK](../../purple-teaming/mitre-attack.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

[Metrics and Measurement](../../purple-teaming/metrics-and-measurement.md)

[After-Action Review](../../purple-teaming/after-action-review.md)

[Continuous Validation](../../purple-teaming/continuous-validation.md)

---

# Related Platform Notes

[Windows](../../windows/index.md)

[Linux](../../linux/index.md)

[Active Directory](../../active-directory/index.md)

[Privilege Escalation Explorer](../../privesc/index.md)

---

# External References

## Command and Control

[Sliver - GitHub](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }

[Sliver Documentation](https://sliver.sh/){ target="_blank" rel="noopener noreferrer" }

[Mythic - GitHub](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }

[Havoc - GitHub](https://github.com/HavocFramework/Havoc){ target="_blank" rel="noopener noreferrer" }

## Adversary Behaviour

[MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }

## Active Directory Tooling

[NetExec](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

[Impacket - GitHub](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[BloodHound](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

[Certipy - GitHub](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

[Rubeus - GitHub](https://github.com/GhostPack/Rubeus){ target="_blank" rel="noopener noreferrer" }

## Practical References

[HackTricks - Red Teaming](https://book.hacktricks.wiki/en/generic-methodologies-and-resources/red-team-methodology/index.html){ target="_blank" rel="noopener noreferrer" }

[The Hacker Recipes](https://www.thehacker.recipes/){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use red team tools like this:

```text
Deploy C2
   |
   v
Run Techniques
   |
   v
Try to Avoid Detection
   |
   v
Declare Success
```

Use them like this:

```text
Define Objective
      |
      v
Define Rules of Engagement
      |
      v
Choose Adversary Behaviour
      |
      v
Choose Appropriate Tool
      |
      v
Execute Controlled Technique
      |
      v
Record Exact Timestamp
      |
      v
Observe Target Result
      |
      v
Observe Defensive Telemetry
      |
      +-- Prevention
      +-- Detection
      +-- Investigation
      +-- Response
      |
      v
Validate Security Conclusion
      |
      v
Clean Up
      |
      v
Feed Lessons Back Into Defences
```

Red team tools provide the technical capability to reproduce attacker behaviour.

Their value comes from using that capability in a controlled way to answer a defined security question, measure the effectiveness of defensive controls, and produce evidence that the organisation can act on.
