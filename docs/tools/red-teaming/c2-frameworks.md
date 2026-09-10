---
title: C2 Frameworks
description: Practical overview of command-and-control frameworks for authorised red team and adversary simulation work, including architecture, operator workflow, framework selection, infrastructure design, session management, telemetry, evidence, cleanup, and defensive validation.
---

# C2 Frameworks

Command-and-control frameworks, commonly abbreviated as **C2 frameworks**, provide authorised red team operators with a structured way to manage remote test agents, issue tasks, maintain operator workflows, and collect evidence during adversary simulation.

A C2 framework may provide capabilities such as:

- agent or implant management;
- operator tasking;
- remote command execution;
- file transfer;
- session management;
- transport configuration;
- operator collaboration;
- SOCKS or pivot support;
- task logging;
- payload generation;
- infrastructure management;
- post-exploitation modules.

The framework itself is not the objective.

A better model is:

```text
Assessment Objective
      |
      v
Adversary Behaviour
      |
      v
C2 Framework
      |
      v
Controlled Action
      |
      v
Endpoint / Network Telemetry
      |
      v
Detection and Response
      |
      v
Evidence
```

!!! warning "Authorised testing only"
    C2 frameworks provide powerful remote administration and post-exploitation capabilities. Use them only in explicitly authorised engagements and only within agreed rules of engagement. Payload deployment, persistence, credential access, lateral movement, tunnelling, and security-control testing should be separately authorised where relevant.

---

# Where C2 Fits

C2 typically appears after a controlled foothold or as part of an assumed-breach exercise.

```text
Rules of Engagement
      |
      v
Initial Access / Assumed Breach
      |
      v
Agent Execution
      |
      v
C2 Session
      |
      v
Approved Technique
      |
      v
Telemetry
      |
      v
Detection / Response Measurement
```

Related notes:

[Red Teaming Tools](index.md)

[Red Teaming](../../red-teaming/index.md)

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

---

# Basic C2 Architecture

A simplified C2 architecture contains:

```text
Operator
   |
   v
Team Server
   |
   v
Listener
   |
   v
Network
   |
   v
Agent
   |
   v
Target Host
```

Depending on the framework, there may also be:

```text
Redirector
Proxy
Database
Web UI
Multiple Operators
Payload Server
```

---

# Core Components

Most modern C2 platforms contain some variation of the following components.

| Component | Purpose |
|---|---|
| Team server | Coordinates sessions, listeners, tasks, and operators |
| Operator client | Interface used by the red team operator |
| Listener | Receives agent communications |
| Agent / implant | Runs on the authorised endpoint |
| Transport | Defines how communication occurs |
| Payload builder | Produces agent artefacts |
| Tasking system | Sends operator actions to an agent |
| Logging | Records operator and agent activity |
| Collaboration layer | Supports multiple operators |
| Pivot / proxy layer | Provides access through an established foothold |

Framework terminology varies.

---

# C2 Is Remote Tasking

At the most basic level:

```text
Operator
   |
   | Task
   v
Agent
   |
   | Result
   v
Operator
```

Examples of legitimate red-team tasks may include:

- identity discovery;
- host information collection;
- controlled process execution;
- checking network configuration;
- testing visibility of approved techniques.

The task should always exist because it supports an agreed objective.

---

# C2 Is Not Automatically Persistence

A C2 agent may run only for the lifetime of a process.

```text
Agent Starts
     |
     v
C2 Session
     |
     v
Process Ends
     |
     v
Session Ends
```

Persistence is a separate technique.

Do not automatically configure persistence merely because the C2 framework supports it.

---

# C2 Is Not Automatically Evasion

C2 tools often provide features associated with stealth, obfuscation, or transport customisation.

The existence of those capabilities does not mean they should be used.

A red team should distinguish:

```text
Normal authorised C2 operation
```

from:

```text
Explicit evasion testing
```

Evasion activity should only be performed when specifically permitted.

---

# Rules of Engagement First

Before deploying a C2 framework, confirm:

```text
Which systems are in scope?

Which users are in scope?

Which payload types are allowed?

Which transports are allowed?

Can agents persist?

Can credentials be accessed?

Can tunnelling occur?

Can security controls be tested?

Which actions are prohibited?
```

The answers determine framework configuration.

---

# Framework Selection

A framework should be chosen based on the engagement rather than popularity.

Useful selection questions include:

```text
Which operating systems are in scope?

Do multiple operators need access?

Which network transports are permitted?

Is browser-based management preferred?

Is cross-platform support required?

How important are audit logs?

Will detection engineering be part of the exercise?

Is commercial support required?
```

---

# Common C2 Frameworks

Commonly encountered frameworks include:

- Sliver;
- Mythic;
- Havoc;
- commercial red team platforms;
- organisation-developed internal C2.

Each has different architecture and operational characteristics.

---

# Sliver

Sliver is an open-source adversary emulation and red team framework maintained by Bishop Fox.

It supports multi-platform red team operations and provides capabilities associated with:

- agent management;
- listener management;
- operator tasking;
- remote execution;
- networking;
- session management;
- multi-operator workflows.

Official resources:

[Sliver - GitHub](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }

[Sliver Documentation](https://sliver.sh/){ target="_blank" rel="noopener noreferrer" }

---

# Sliver Architecture

Conceptually:

```text
Operator
   |
   v
Sliver Server
   |
   v
Listener
   |
   v
Agent
```

The server coordinates:

- listeners;
- sessions;
- operators;
- tasking;
- results.

Use the official Sliver documentation for current installation and operational syntax.

---

# Sliver Use Cases

Sliver may be suitable when:

- cross-platform support is required;
- an open-source C2 is desired;
- multiple operators need access;
- structured red team workflows are required;
- adversary emulation is being performed in a controlled lab or engagement.

---

# Mythic

Mythic is a modular collaborative C2 platform.

It provides a framework into which different agents and communication components can be integrated.

Official project:

[Mythic - GitHub](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }

Official documentation:

[Mythic Documentation](https://docs.mythic-c2.net/){ target="_blank" rel="noopener noreferrer" }

---

# Mythic Architecture

A simplified model is:

```text
Operators
    |
    v
Mythic Platform
    |
    +-- Agents
    +-- C2 Profiles
    +-- Tasks
    +-- Results
    +-- Web Interface
```

Its modular approach can be useful where an engagement requires different agents or communication patterns.

---

# Mythic Use Cases

Mythic may be useful where:

- operator collaboration is important;
- a web-based interface is preferred;
- modular agent development is useful;
- multiple communication profiles are needed;
- detailed task tracking is valuable.

---

# Havoc

Havoc is another command-and-control framework used in red team and adversary simulation environments.

Official project:

[Havoc - GitHub](https://github.com/HavocFramework/Havoc){ target="_blank" rel="noopener noreferrer" }

Its use should follow the same operational controls applied to other C2 frameworks.

---

# Havoc Use Cases

Havoc may be encountered in:

- red team labs;
- adversary emulation;
- training environments;
- controlled security assessments.

Framework capability should never be interpreted as permission to use every available feature.

---

# Commercial C2 Platforms

Commercial red team platforms may provide:

- vendor support;
- enterprise collaboration;
- documentation;
- maintained payloads;
- reporting;
- team management.

The organisation may select a commercial platform because of:

- support requirements;
- procurement policy;
- assurance;
- operational maturity;
- established internal procedures.

The same rules of engagement apply regardless of licensing model.

---

# Internal C2 Platforms

Some organisations build or maintain their own C2 tooling.

Advantages can include:

- predictable behaviour;
- controlled source code;
- custom telemetry;
- reduced dependency on public frameworks;
- tailored workflows.

Disadvantages can include:

- maintenance burden;
- security risk;
- incomplete testing;
- operator training requirements.

Internal tooling should be treated like production security software.

---

# C2 Server

The team server is the central component.

It may store:

- session information;
- task history;
- payload configuration;
- credentials;
- operator activity;
- target metadata.

Compromise of the team server could expose the entire exercise.

Therefore, it should be strongly protected.

---

# C2 Server Security

Recommended principles include:

```text
Dedicated Infrastructure
Restricted Management Access
Strong Authentication
Minimal Services
Firewalling
Patch Management
Operator Logging
Secure Backups Where Needed
```

Do not expose C2 management interfaces broadly to the internet.

---

# Dedicated Infrastructure

Prefer separate infrastructure for red team operations.

For example:

```text
Operator Workstation
      |
      v
Dedicated C2 Server
      |
      v
Authorised Target Network
```

Avoid mixing:

- personal workloads;
- unrelated client data;
- production corporate services;
- C2 infrastructure.

---

# VPS-Based C2

A VPS is commonly used for red team infrastructure.

Typical security considerations include:

- SSH hardening;
- firewall rules;
- key-based authentication;
- minimal exposed services;
- timely updates;
- logging.

The VPS itself becomes part of the trusted assessment environment.

---

# Firewalling

A C2 server should expose only the services required for the engagement.

Conceptually:

```text
Internet
   |
   v
Firewall
   |
   +-- Operator Management
   +-- Approved Listener
   |
   X
Unnecessary Services
```

Management access should be more restrictive than agent communication where possible.

---

# Management Interface

The operator interface may be:

- command line;
- desktop GUI;
- web interface.

Protect management access separately from C2 listener traffic.

Do not expose administrative interfaces unnecessarily.

---

# Operator Authentication

Where supported, use:

- individual operator accounts;
- unique credentials;
- strong authentication;
- audit logging.

Avoid shared operator accounts when multi-user support exists.

---

# Multi-Operator Environments

Multiple operators require coordination.

Without coordination:

```text
Operator A
    |
    +--> changes system

Operator B
    |
    +--> tests same system
```

may lead to:

- confusing results;
- duplicated actions;
- broken application state;
- inaccurate evidence.

Use shared operation logs or the framework's collaboration features.

---

# Listener

A listener accepts incoming agent communication.

Listener configuration may define:

- network interface;
- transport;
- port;
- certificates;
- communication profile.

Only listeners required for the exercise should be active.

---

# Listener Inventory

Record active listeners.

Example:

| Listener | Purpose | Exposure | Required |
|---|---|---|---|
| HTTPS test listener | Endpoint C2 | Internet-facing | Yes |
| Internal listener | Lab-only testing | Internal | Yes |
| Legacy listener | None | Disabled | No |

Remove or disable listeners that are no longer required.

---

# C2 Transport

The transport determines how an agent communicates with the server.

Possible categories include:

```text
HTTPS
DNS
Other framework-supported transports
```

The transport chosen should support the exercise objective.

---

# HTTPS Transport

HTTPS is frequently used because it provides normal TLS-protected network communication.

From a defensive perspective, HTTPS traffic can still be analysed through:

- endpoint process telemetry;
- destination;
- DNS;
- TLS characteristics;
- connection timing;
- proxy logs.

Encrypted does not mean invisible.

---

# DNS Transport

Some C2 systems support DNS-based communication.

DNS transport can create:

- unusual query patterns;
- encoded subdomains;
- high query volume;
- distinctive timing.

It should be used only where DNS-based command and control is part of the approved simulation.

---

# Agent

The agent is the target-side component.

It may receive tasks and return results.

A red team should know:

```text
Where is it running?

Which user context?

Which process?

Which architecture?

When did it start?

When should it stop?
```

This information is essential for evidence and cleanup.

---

# Session Context

When a session appears, first establish:

```text
Hostname
Current user
Integrity / privilege
Operating system
Process identity
Time
```

Do not assume a session has administrative privilege.

---

# Example Session Baseline

Conceptually:

```text
Host:
WS01

User:
EXAMPLE\tester

Privilege:
Standard user

Objective:
Validate local discovery telemetry
```

This baseline makes later privilege changes measurable.

---

# Agent Lifecycle

A well-managed agent has a clear lifecycle.

```text
Create
  |
  v
Deploy
  |
  v
Execute
  |
  v
Use
  |
  v
Terminate
  |
  v
Remove
```

Do not leave unused agents running.

---

# Payload Generation

Many C2 frameworks can generate target-specific agents.

Payload generation should be controlled because different builds may have different:

- hashes;
- transports;
- configuration;
- architectures;
- telemetry.

Every assessment artefact should be traceable.

---

# Payload Inventory

Record:

```text
Filename
Framework
Framework version
Architecture
Configuration
Hash
Target
Purpose
Creation date
Cleanup status
```

Example:

```text
Framework:
Approved C2

Artifact:
agent-ws01.exe

Architecture:
x64

Purpose:
Controlled C2 validation

SHA256:
Recorded internally
```

---

# Hashing Payloads

On Windows:

```powershell
Get-FileHash .\agent.exe -Algorithm SHA256
```

On Linux:

```bash
sha256sum agent.exe
```

Hashes help correlate:

- endpoint detections;
- EDR telemetry;
- operator logs;
- evidence.

---

# Payload Storage

Store payloads in dedicated assessment directories.

For example:

```text
engagement/
└── payloads/
    ├── windows/
    ├── linux/
    └── hashes.txt
```

Do not leave offensive artefacts mixed with unrelated files.

---

# Payload Delivery

Delivery is a separate assessment stage.

Possible approved mechanisms may include:

- administrative pre-placement;
- controlled web hosting;
- approved file transfer;
- exercise-specific delivery workflows.

The choice should match the engagement objective.

---

# Administrative Pre-Placement

In many purple-team exercises, administrators can place the agent on the endpoint before testing.

This reduces unnecessary complexity.

```text
Administrator
     |
     v
Approved Agent Placement
     |
     v
Red Team Executes Agreed Technique
```

This is often preferable when the exercise is focused on post-compromise visibility rather than initial access.

---

# Assumed Breach

An assumed-breach exercise may begin with:

```text
Valid Domain User
       +
Controlled Endpoint
       +
Pre-Positioned Agent
```

This allows the assessment to focus on:

- discovery;
- identity controls;
- lateral movement;
- privilege escalation;
- detection;
- response.

---

# Session Management

A C2 server may manage many sessions.

Useful metadata includes:

```text
Hostname
User
Operating system
Agent
Last seen
Privilege
IP
```

Avoid tasking a session unless the target has been confirmed as in scope.

---

# Session Naming

Where supported, use meaningful labels.

Example:

```text
WS01-standard-user
SRV02-test-account
LAB-DC01
```

This reduces accidental tasking of the wrong endpoint.

---

# Session Scope

A newly connected endpoint must still be checked against the engagement scope.

```text
New Session
    |
    v
Confirm Host
    |
    v
Check Scope
    |
    +-- In scope -> continue
    |
    +-- Unknown -> stop and verify
```

---

# Operator Tasking

Every task should support an objective.

Bad workflow:

```text
Session Connected
      |
      v
Run Every Available Command
```

Better:

```text
Objective:
Validate process discovery detection

Task:
Perform approved process discovery

Evidence:
Record operator and EDR timestamps
```

---

# Discovery Tasks

Common low-impact discovery categories include:

- current user;
- hostname;
- network configuration;
- processes;
- services;
- domain context.

These often provide useful starting telemetry.

---

# Privilege Awareness

Before using privileged functionality, confirm the current context.

```text
Standard User
      |
      v
Different capabilities
```

versus:

```text
Administrator / SYSTEM / root
      |
      v
Much broader capabilities
```

Do not infer privilege from the existence of a C2 session.

---

# Native Command Execution

Many C2 platforms can launch operating-system commands.

Native utilities may be appropriate for:

- identity checks;
- process review;
- network review;
- service inspection.

Use commands aligned with the objective.

---

# C2 File Transfer

Frameworks may support uploading and downloading files.

File transfer can create operational risks.

Before downloading:

```text
Is the file needed?

Does it contain sensitive data?

Can synthetic data be used instead?

Where will it be stored?

When will it be deleted?
```

---

# Data Minimisation

A red team should collect the minimum data necessary to demonstrate the objective.

Avoid:

```text
Download entire file share
```

when:

```text
Proof of access to controlled file
```

is sufficient.

---

# SOCKS and Pivoting

Some C2 frameworks provide SOCKS or proxy functionality.

Conceptually:

```text
Operator Tool
      |
      v
SOCKS
      |
      v
Agent
      |
      v
Internal Network
```

This can alter network reachability significantly.

Use pivoting only where explicitly authorised.

---

# Pivot Scope

Before using a pivot:

- identify reachable network ranges;
- confirm authorised subnets;
- define target list;
- limit tooling to those targets.

Do not assume that every reachable system is in scope.

---

# Tunnelling Risk

Tunnels can:

- bypass normal network paths;
- increase bandwidth;
- create unexpected routing;
- affect monitoring.

Document active tunnels and terminate them during cleanup.

---

# Beaconing

Many agents periodically contact the server.

A simplified pattern is:

```text
Agent
  |
  +---- callback
  |
  +---- callback
  |
  +---- callback
```

This periodic behaviour may create a detectable pattern.

---

# Sleep Interval

A callback interval affects:

- responsiveness;
- network traffic;
- detectability;
- server load.

Short intervals generate more traffic.

Long intervals make operator actions slower.

Choose values according to the exercise.

---

# Jitter

Jitter introduces variation in callback timing.

Conceptually:

```text
10 seconds
13 seconds
8 seconds
12 seconds
```

instead of:

```text
10
10
10
10
```

Changing timing characteristics should support an authorised simulation objective.

---

# Network Telemetry

Defensive teams may observe:

- destination IP;
- destination domain;
- port;
- TLS;
- DNS;
- periodic connections;
- unusual processes initiating traffic.

A C2 exercise can therefore validate several detection layers simultaneously.

---

# Endpoint Telemetry

Endpoint telemetry may include:

- agent process creation;
- parent process;
- child processes;
- file writes;
- network connections;
- modules;
- command lines;
- PowerShell activity.

This is often more useful than signature-based detection alone.

---

# Parent-Child Relationships

An EDR may observe:

```text
Parent Process
      |
      v
Agent
      |
      v
Child Process
```

Detection logic should consider whether the process chain is expected in the environment.

---

# Operator Logs

Operator logs should include:

```text
Timestamp
Operator
Target
Current user
Task
Framework
Result
```

These are essential when correlating with defensive telemetry.

---

# Time Synchronisation

Ensure that:

```text
Operator
C2 server
Endpoints
EDR
SIEM
```

use sufficiently aligned time.

Otherwise correlation becomes difficult.

---

# Timezone

Use one agreed timezone for evidence.

Example:

```text
UTC
```

or:

```text
Europe/Amsterdam
```

Document it in the report.

---

# C2 and MITRE ATT&CK

C2 tasks should be mapped to behaviour, not merely framework features.

Example:

```text
Framework:
Sliver

Task:
Process discovery

ATT&CK mapping:
Process Discovery
```

The technique is the behaviour.

The framework is the delivery mechanism.

Official reference:

[MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }

---

# Technique-Level Logging

A useful record might contain:

```text
Technique:
Process Discovery

Target:
WS01

User:
EXAMPLE\tester

Framework:
Approved C2

Timestamp:
20:15:42

Expected telemetry:
Process query and agent child activity
```

This makes purple-team analysis easier.

---

# Detection Validation

C2 frameworks can reproduce attacker behaviours while blue teams observe.

```text
Red Team
   |
   v
C2 Task
   |
   v
Endpoint Behaviour
   |
   v
Telemetry
   |
   v
SIEM / EDR
   |
   v
Analyst
```

Measure each stage separately.

---

# Prevention vs Detection

A useful model is:

```text
Technique Attempted
       |
       +--> Prevented?
       |
       +--> Telemetry generated?
       |
       +--> Detection generated?
       |
       +--> Alert investigated?
       |
       +--> Response performed?
```

A blocked technique may still reveal a monitoring gap.

---

# C2 Detection Does Not Equal Agent Detection

A defensive control might detect:

```text
Known agent signature
```

without detecting:

```text
Underlying behaviour
```

For mature detection engineering, measure both:

```text
Tool-Specific Detection
```

and:

```text
Technique-Level Detection
```

---

# Tool-Specific Detection

Tool-specific detection may include:

- executable hashes;
- known strings;
- known network indicators;
- framework-specific metadata.

These can be useful but fragile.

---

# Behavioural Detection

Behavioural detection focuses on:

- unusual process relationships;
- suspicious network behaviour;
- identity context;
- discovery patterns;
- privilege changes;
- unusual remote administration.

Behavioural coverage is generally more resilient to tooling changes.

---

# Framework Switching

If the blue team detects one C2 family, switching frameworks solely to obtain an undetected payload should not automatically become the next objective.

Instead ask:

```text
Are we testing signature resistance?
```

or:

```text
Are we testing behavioural detection?
```

The answer determines whether framework variation is justified.

---

# Security Control Interaction

C2 execution may be affected by:

- Defender;
- EDR;
- AppLocker;
- WDAC;
- firewall;
- proxy;
- DNS filtering;
- network segmentation.

These controls are part of the assessment environment.

---

# Blocked Payload

If an approved payload is blocked:

```text
Attempt
  |
  v
Security Control Blocks
  |
  v
Record Exact Result
```

This can be a successful control outcome.

Do not immediately try to bypass the control unless evasion testing is explicitly in scope.

---

# Application Control

Windows application control may restrict:

- executables;
- DLLs;
- scripts;
- installers;
- packaged applications.

Related note:

[Windows Application Control](../../windows/application-control.md)

A blocked C2 artefact may provide valuable evidence about application-control effectiveness.

---

# Defender and EDR

Endpoint products may:

- quarantine payloads;
- block processes;
- alert on child process behaviour;
- detect network activity;
- terminate sessions.

Record what happened rather than focusing only on whether the agent survived.

---

# Firewall Controls

Network controls may prevent C2 callbacks.

Potential control points include:

```text
Host firewall
Network firewall
Proxy
DNS filtering
Egress filtering
```

A failed callback can therefore be a useful network-control result.

---

# Proxy Environments

Some enterprise environments require HTTP traffic through a proxy.

This may affect C2 connectivity.

Do not reconfigure enterprise proxy policy without authorisation.

Record the environmental restriction.

---

# Egress Filtering

C2 testing is a useful way to evaluate outbound network controls.

For example:

```text
Endpoint
   |
   v
Unknown external destination
   |
   X
Egress filter
```

A blocked connection may demonstrate effective control.

---

# DNS Controls

DNS filtering may:

- block newly created domains;
- log suspicious requests;
- prevent certain resolutions.

Include DNS telemetry when evaluating C2 behaviour.

---

# Redirectors

Some red team architectures place a redirector between the target and primary C2 server.

```text
Agent
  |
  v
Redirector
  |
  v
Team Server
```

Possible reasons include:

- architecture separation;
- routing;
- traffic control;
- telemetry.

Redirectors introduce additional infrastructure that must be secured and monitored.

---

# Redirector Logging

A redirector can provide useful evidence such as:

```text
Source
Timestamp
Request
Destination
```

Do not store unnecessary target data.

---

# C2 Infrastructure Domains

If dedicated domains are used for authorised exercises:

- document ownership;
- restrict use to the assessment;
- secure DNS administration;
- remove records when no longer required.

Infrastructure should not remain active indefinitely.

---

# Certificates

TLS certificates used by C2 infrastructure should be tracked.

Record:

```text
Domain
Certificate source
Validity
Listener
Cleanup / expiry
```

Do not reuse unrelated production private keys.

---

# Framework Updates

C2 frameworks evolve quickly.

Before an engagement:

```text
Review release
Test in lab
Validate payload generation
Validate listener
Validate logging
```

Do not upgrade the production assessment infrastructure mid-engagement without reason.

---

# Lab Validation

Before deployment, test the framework in a controlled lab.

Validate:

- server stability;
- listener connectivity;
- logging;
- payload lifecycle;
- cleanup;
- operator access.

A lab is the correct place to discover configuration problems.

---

# Framework Version

Record the version.

For example:

```text
Framework:
Sliver

Version:
Recorded from installed build
```

Do not rely on memory or external documentation alone.

---

# Build Provenance

If built from source, record:

```text
Repository
Commit
Build date
Build environment
Hash
```

This helps correlate detections.

---

# Supply-Chain Risk

A C2 framework has access to extremely sensitive information.

Potential compromise of the framework itself could expose:

- operator credentials;
- target sessions;
- payloads;
- collected data;
- infrastructure credentials.

Use trusted sources.

---

# Dependencies

C2 servers may depend on:

- databases;
- containers;
- language runtimes;
- web components.

Secure the entire platform rather than only the main executable.

---

# Containerised Deployment

Some frameworks use Docker or container orchestration.

Security considerations include:

- exposed ports;
- mounted secrets;
- container privileges;
- volumes;
- update lifecycle.

Do not expose management containers publicly without need.

---

# Backup Strategy

C2 backups may contain highly sensitive information.

Ask whether backup is actually required.

If so:

- encrypt appropriately;
- restrict access;
- define retention;
- delete according to policy.

---

# Session Data Retention

Do not retain operational session data indefinitely.

Define:

```text
Retention period
Evidence requirements
Deletion process
```

This should align with engagement policy.

---

# Credentials in C2

A C2 framework may encounter:

- passwords;
- tokens;
- hashes;
- tickets;
- private keys.

These should be treated as high-sensitivity secrets.

Do not store them in normal notes.

---

# Do Not Paste Secrets into Reports

Instead of:

```text
Password:
P@ssw0rd123
```

write:

```text
A reusable credential was exposed. The value has been redacted.
```

Store the actual evidence separately if retention is required.

---

# Screenshots

Screenshots can show:

- agent connection;
- task execution;
- session context;
- defensive alert.

However, screenshots should not be the only evidence.

Combine with:

- operator logs;
- endpoint logs;
- SIEM/EDR events;
- timestamped outputs.

---

# C2 Evidence Model

A useful evidence chain is:

```text
Operator Task
     |
     v
C2 Timestamp
     |
     v
Endpoint Result
     |
     v
EDR Event
     |
     v
SIEM Alert
     |
     v
Analyst Action
```

This is particularly useful for purple-team exercises.

---

# Cleanup

Cleanup should be planned before deployment.

Potential C2 artefacts include:

- agent binary;
- script;
- service;
- task;
- startup entry;
- configuration file;
- tunnel;
- certificate;
- temporary download;
- listener;
- DNS record.

---

# Cleanup Ledger

Maintain a table such as:

| Target | Artefact | Purpose | Removal Required | Removed |
|---|---|---|---|---|
| WS01 | Test agent | C2 validation | Yes | Yes |
| VPS01 | HTTPS listener | Engagement C2 | Yes | Yes |
| DNS | Test record | Listener routing | Yes | Yes |

This reduces cleanup mistakes.

---

# Terminate Sessions

Before dismantling infrastructure:

```text
Stop Tasking
      |
      v
Terminate Agents
      |
      v
Remove Target Artefacts
      |
      v
Disable Listeners
      |
      v
Retire Infrastructure
```

Follow the engagement cleanup procedure.

---

# Do Not Delete Security Logs

Normal cleanup should not delete:

- event logs;
- EDR telemetry;
- SIEM events;
- firewall logs;
- DNS logs.

These are defensive evidence.

Log deletion is a separate adversary technique and should only be tested if explicitly approved.

---

# Persistence Cleanup

If persistence was separately authorised, every persistence artefact should be tracked.

Examples include:

```text
Scheduled task
Service
Registry startup value
Systemd unit
Cron entry
```

Verify removal independently.

---

# Validate Cleanup

Do not assume cleanup succeeded.

Check:

```text
File absent?
Process terminated?
Task absent?
Service removed?
Listener disabled?
DNS record removed?
```

Document completion.

---

# Incident Handling

If unexpected behaviour occurs:

```text
Unexpected Production Impact
      |
      v
Stop Activity
      |
      v
Contact Engagement Lead
      |
      v
Preserve Evidence
      |
      v
Support Recovery
```

Do not continue testing while an unplanned incident is unresolved.

---

# Stop Conditions

Potential stop conditions include:

- production outage;
- unstable endpoint;
- unexpected sensitive data access;
- third-party impact;
- real compromise discovered;
- account lockout;
- defensive team emergency request.

Operators should know these before starting.

---

# Purple Team Workflow

A C2 framework is especially useful when the goal is repeatable behaviour.

```text
Technique Selected
      |
      v
Task Executed
      |
      v
Timestamp Recorded
      |
      v
Blue Team Searches
      |
      v
Detection Result
      |
      v
Rule Improved
      |
      v
Technique Replayed
```

This supports continuous validation.

Related note:

[Continuous Validation](../../purple-teaming/continuous-validation.md)

---

# After-Action Review

C2 logs can help reconstruct:

```text
What happened?

When?

On which host?

Under which identity?

What did security controls observe?

What was missed?
```

Related note:

[After-Action Review](../../purple-teaming/after-action-review.md)

---

# Metrics

Potential C2-related purple-team metrics include:

```text
Time to telemetry
Time to alert
Time to analyst triage
Time to containment
Technique detection rate
Technique prevention rate
```

Related note:

[Metrics and Measurement](../../purple-teaming/metrics-and-measurement.md)

---

# Framework Comparison

A high-level comparison can help with selection.

| Area | Sliver | Mythic | Havoc |
|---|---|---|---|
| Open source | Yes | Yes | Yes |
| Multi-operator | Yes | Yes | Yes |
| Modular architecture | Yes | Strong focus | Yes |
| Cross-platform focus | Strong | Depends on agent | Framework-dependent |
| Web interface | Not primary operator model | Strong | GUI-focused |
| Suitable for lab/adversary simulation | Yes | Yes | Yes |

Capabilities change over time.

Verify current official documentation before making deployment decisions.

---

# Choosing Sliver

Sliver may fit when:

- cross-platform operations matter;
- open-source infrastructure is preferred;
- CLI workflows are comfortable;
- multi-operator support is needed.

---

# Choosing Mythic

Mythic may fit when:

- collaborative web workflows matter;
- modular agents are desirable;
- several operators need structured task visibility;
- extensibility is important.

---

# Choosing Havoc

Havoc may fit where:

- the team is already trained on it;
- the engagement has approved it;
- its operational model matches the objective.

Tool familiarity matters because operator error can be more dangerous than framework limitations.

---

# Do Not Constantly Switch Frameworks

Every additional framework increases:

- infrastructure complexity;
- training burden;
- artefact management;
- cleanup requirements;
- evidence complexity.

Use the minimum tooling needed to meet the objective.

---

# C2 and Native Tools

C2 can act as transport for normal operating-system actions.

Example:

```text
C2
 |
 v
Native Host Command
 |
 v
Endpoint Telemetry
```

The detection should focus on meaningful behaviour.

---

# C2 and Active Directory

C2 sessions may provide a foothold from which authorised AD analysis is performed.

Related section:

[Active Directory Tools](../active-directory/index.md)

Tools such as BloodHound, NetExec, Certipy, Impacket, or native utilities may then support specific directory objectives.

---

# C2 and Privilege Escalation

After establishing a standard-user foothold, privilege escalation enumeration may be performed using approved techniques.

Related section:

[Privilege Escalation Tools](../privilege-escalation/index.md)

The C2 framework does not itself establish that privilege escalation is possible.

---

# C2 and Web Testing

A red team may identify internal web applications reachable only from an established position.

The same scope rules still apply.

Related section:

[Web Application Testing Tools](../web-testing/index.md)

Do not test internal applications merely because a pivot makes them reachable.

---

# Operational Workflow

A mature C2 workflow can be:

```text
1. Define objective
      |
      v
2. Confirm rules of engagement
      |
      v
3. Select approved framework
      |
      v
4. Build isolated infrastructure
      |
      v
5. Secure management access
      |
      v
6. Configure only required listeners
      |
      v
7. Create controlled artefact
      |
      v
8. Record hash and configuration
      |
      v
9. Deploy to approved target
      |
      v
10. Confirm session identity
      |
      v
11. Execute agreed technique
      |
      v
12. Record timestamps and results
      |
      v
13. Correlate defensive telemetry
      |
      v
14. Stop unnecessary sessions
      |
      v
15. Remove artefacts
      |
      v
16. Disable infrastructure
      |
      v
17. Complete after-action review
```

---

# C2 Pre-Deployment Checklist

## Engagement

- [ ] Engagement authorised.
- [ ] Targets defined.
- [ ] Exclusions defined.
- [ ] Techniques agreed.
- [ ] Prohibited actions documented.
- [ ] Stop conditions documented.
- [ ] Emergency contact identified.
- [ ] Cleanup requirements documented.

## Framework

- [ ] Framework approved.
- [ ] Official source used.
- [ ] Version recorded.
- [ ] Lab tested.
- [ ] Operator team trained.
- [ ] Only required functionality enabled.

## Infrastructure

- [ ] Dedicated server used.
- [ ] Management access restricted.
- [ ] Firewall configured.
- [ ] Unnecessary ports closed.
- [ ] Operator authentication configured.
- [ ] TLS configured where required.
- [ ] Logging enabled.
- [ ] Time synchronised.

## Listener

- [ ] Listener purpose documented.
- [ ] Exposure understood.
- [ ] Network port approved.
- [ ] Transport approved.
- [ ] Unused listeners disabled.

## Payload

- [ ] Target architecture known.
- [ ] Payload configuration recorded.
- [ ] SHA256 recorded.
- [ ] Delivery method approved.
- [ ] Target identified.
- [ ] Cleanup procedure defined.

---

# Session Checklist

When a new agent connects:

- [ ] Hostname confirmed.
- [ ] IP confirmed.
- [ ] Current user confirmed.
- [ ] Privilege level confirmed.
- [ ] Operating system confirmed.
- [ ] Target checked against scope.
- [ ] Session labelled clearly.
- [ ] Objective confirmed before tasking.

---

# Tasking Checklist

Before issuing a task:

- [ ] Security objective known.
- [ ] Technique approved.
- [ ] Expected target impact understood.
- [ ] State-changing effect understood.
- [ ] Expected telemetry identified.
- [ ] Exact timestamp recorded.
- [ ] Sensitive data collection minimised.

---

# Detection Checklist

- [ ] Endpoint telemetry checked.
- [ ] Network telemetry checked.
- [ ] DNS telemetry checked.
- [ ] Proxy telemetry checked where relevant.
- [ ] SIEM ingestion checked.
- [ ] Alert generation checked.
- [ ] Analyst visibility checked.
- [ ] Response measured separately from prevention.

---

# Evidence Checklist

- [ ] Framework recorded.
- [ ] Framework version recorded.
- [ ] Agent hash recorded.
- [ ] Target recorded.
- [ ] User context recorded.
- [ ] Task timestamp recorded.
- [ ] Result recorded.
- [ ] Defensive event IDs or alert references retained.
- [ ] Screenshots contain no unnecessary secrets.
- [ ] Operator log retained.

---

# Cleanup Checklist

- [ ] Agent terminated.
- [ ] Payload removed.
- [ ] Temporary files removed.
- [ ] Tunnels closed.
- [ ] Persistence removed if used.
- [ ] Listeners disabled.
- [ ] Temporary DNS removed.
- [ ] Certificates handled appropriately.
- [ ] VPS/infrastructure retired where required.
- [ ] Cleanup independently confirmed.
- [ ] Defensive logs preserved.

---

# Reporting

Do not write:

```text
Sliver bypassed the environment.
```

unless the evidence actually supports a specific defensive-control failure.

Prefer:

```text
The approved red team agent successfully established outbound
communication from the tested workstation to the assessment
infrastructure. The connection generated endpoint network telemetry but
did not result in an alert during the agreed observation window.
```

This states:

- what happened;
- where;
- what telemetry existed;
- what detection outcome occurred.

---

# Reporting a Blocked Agent

Example:

```text
Execution of the approved red team agent was prevented by application
control on the tested workstation. The attempt generated corresponding
endpoint telemetry and was visible to the defensive team.
```

This is a positive control result.

---

# Reporting a Network Block

Example:

```text
The test agent executed locally but was unable to establish outbound
communication to the authorised assessment server. Network telemetry
showed the connection attempt was blocked by the organisation's egress
controls.
```

This separates execution from communication.

---

# Reporting a Detection Gap

Example:

```text
The test agent successfully established the authorised C2 channel and
performed the agreed host-discovery action. Endpoint telemetry was
available, but no alert was generated during the exercise. This
indicates a detection-logic gap rather than a telemetry-collection gap.
```

This makes the conclusion actionable.

---

# Reporting a Telemetry Gap

Example:

```text
The agreed technique executed successfully, but the expected endpoint
event was not present in the available telemetry. The result should be
investigated as a collection or logging coverage gap before additional
detection logic is developed.
```

---

# Prevention, Telemetry, Detection, Response

A useful final result model is:

| Stage | Result |
|---|---|
| Execution | Allowed / blocked |
| Communication | Allowed / blocked |
| Telemetry | Present / absent |
| Detection | Alert / no alert |
| Triage | Correct / missed |
| Response | Effective / ineffective |

This prevents overly simplistic conclusions.

---

# Related Tool Notes

[Red Teaming Tools](index.md)

[Active Directory Tools](../active-directory/index.md)

[Privilege Escalation Tools](../privilege-escalation/index.md)

[Web Enumeration Tools](../web-enumeration/index.md)

[Web Application Testing Tools](../web-testing/index.md)

---

# Related Red Team Notes

[Red Teaming](../../red-teaming/index.md)

Use the Red Teaming section as the canonical home for:

- adversary simulation methodology;
- operational planning;
- rules of engagement;
- technique-specific guidance;
- cleanup;
- reporting.

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

# External References

## Sliver

[Sliver - GitHub](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }

[Sliver Documentation](https://sliver.sh/){ target="_blank" rel="noopener noreferrer" }

## Mythic

[Mythic - GitHub](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }

[Mythic Documentation](https://docs.mythic-c2.net/){ target="_blank" rel="noopener noreferrer" }

## Havoc

[Havoc - GitHub](https://github.com/HavocFramework/Havoc){ target="_blank" rel="noopener noreferrer" }

## Adversary Behaviour

[MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }

## Practical References

[HackTricks - Red Team Methodology](https://book.hacktricks.wiki/en/generic-methodologies-and-resources/red-team-methodology/index.html){ target="_blank" rel="noopener noreferrer" }

[The Hacker Recipes](https://www.thehacker.recipes/){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use a C2 framework like this:

```text
Generate Agent
      |
      v
Get Session
      |
      v
Run Everything
      |
      v
Try to Remain Undetected
```

Use it like this:

```text
Define Security Objective
        |
        v
Approve Rules of Engagement
        |
        v
Select Appropriate Framework
        |
        v
Secure Infrastructure
        |
        v
Create Controlled Test Artefact
        |
        v
Record Hash and Configuration
        |
        v
Deploy to Authorised Target
        |
        v
Confirm Host and User Context
        |
        v
Execute One Agreed Behaviour
        |
        v
Record Timestamp
        |
        v
Observe Endpoint and Network Telemetry
        |
        v
Measure Prevention
        |
        v
Measure Detection
        |
        v
Measure Analyst Response
        |
        v
Capture Evidence
        |
        v
Terminate Agent
        |
        v
Clean Up Infrastructure
        |
        v
Feed Results Back Into Defences
```

A C2 framework is valuable because it provides a repeatable and controlled mechanism for reproducing adversary behaviour.

The quality of the assessment comes from the objectives, rules of engagement, validation, evidence, defensive correlation, and cleanup - not from the framework itself.
