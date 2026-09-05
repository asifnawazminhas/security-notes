---
title: Command and Control
description: Command-and-control architecture, team servers, listeners, agents, transports, redirectors, sleep and jitter, operational security, infrastructure hardening, detection, logging, and cleanup for authorised red team assessments.
---

# Command and Control

Command and Control (C2) is the communication layer used by an authorised red team to manage controlled agents, issue tasks, receive results, and coordinate activity during an assessment.

A basic C2 architecture can be represented as:

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
Redirector
   |
   v
Internet
   |
   v
Authorised Test Host
```

C2 should not be considered only from the offensive perspective.

A mature assessment should also evaluate:

```text
Endpoint visibility
Network visibility
DNS visibility
Proxy visibility
Firewall visibility
Authentication controls
Application control
EDR telemetry
SIEM correlation
Incident response
```

The objective is to determine whether authorised adversary-like communication can operate in the environment and how effectively defensive controls identify and respond to it.


---

# C2 Terminology

Common C2 terminology includes:

| Term | Description |
|---|---|
| Team server | Backend system coordinating C2 activity |
| Operator | Authorised tester interacting with the framework |
| Listener | Service waiting for agent communication |
| Agent | Controlled software component running on an authorised test system |
| Beacon | Common term for an agent that periodically checks in |
| Implant | Another term commonly used for an agent |
| Session | Active communication context with an agent |
| Callback | Communication initiated by an agent toward C2 infrastructure |
| Check-in | Periodic agent communication |
| Tasking | Instructions provided to an agent |
| Redirector | Internet-facing system forwarding permitted traffic to the backend |
| Transport | Communication mechanism used by the C2 channel |
| Sleep | Delay between periodic check-ins |
| Jitter | Variation applied to timing |
| Profile | Configuration controlling communication behaviour in frameworks that support it |


---

# High-Level C2 Architecture

A simple architecture:

```text
+----------------+
|    Operator    |
+-------+--------+
        |
        v
+----------------+
|  Team Server   |
+-------+--------+
        |
        v
+----------------+
|    Listener    |
+-------+--------+
        |
        v
+----------------+
|   Redirector   |
+-------+--------+
        |
        v
     Internet
        |
        v
+----------------+
| Authorised Host|
+----------------+
```

For a small lab, several components may exist on the same system.

For a larger engagement, separating them provides better security and operational control.


---

# C2 Communication Model

A common communication model is agent initiated.

```text
Authorised Host
      |
      | 1. Check in
      v
Redirector
      |
      v
Team Server
      |
      | 2. Retrieve task
      v
Authorised Host
      |
      | 3. Execute authorised task
      |
      | 4. Return result
      v
Redirector
      |
      v
Team Server
      |
      v
Operator
```

This communication creates opportunities for defensive monitoring at multiple layers.


---

# C2 Components

A C2 environment commonly contains:

```text
Operator Client
Team Server
Listener
Agent
Redirector
Domain
DNS
TLS Certificate
Firewall
Logging
Management Network
```

Each component should have a clearly defined purpose.


---

# Operator

The operator is the authorised tester interacting with the C2 platform.

Operators may:

```text
Review active sessions
Issue approved tasks
Collect command results
Coordinate operations
Review logs
Manage listeners
Track objectives
Record evidence
```

Operator access should be tightly controlled.


---

# Operator Security

Protect operator systems using controls such as:

```text
Strong authentication
Dedicated engagement accounts
Encrypted storage
Screen locking
Minimal local secrets
Separate engagement workspaces
Restricted administrative access
Logging
VPN access
```

Avoid sharing a single administrative account between operators where individual accounts are supported.


---

# Team Server

The team server is the backend of the C2 architecture.

It may contain:

```text
Agent state
Operator accounts
Listener configuration
Task history
Results
Infrastructure configuration
Logs
Assessment metadata
Cryptographic material
```

Compromise of the team server can expose significant engagement information.

It should therefore normally receive stronger protection than an internet-facing redirector.


---

# Team Server Exposure

Prefer:

```text
Internet
   |
   X
Team Server
```

with operational communication routed through controlled infrastructure:

```text
Internet
   |
   v
Redirector
   |
   v
Team Server
```

Administrative access should preferably follow a separate path:

```text
Operator
   |
   v
Management VPN
   |
   v
Team Server
```


---

# Management Plane vs C2 Plane

Separating management traffic from operational C2 traffic is useful.

```text
MANAGEMENT PLANE

Operator
   |
   v
VPN
   |
   v
Team Server


C2 PLANE

Authorised Host
   |
   v
Internet
   |
   v
Redirector
   |
   v
Listener
   |
   v
Team Server
```

This reduces unnecessary exposure of administrative services.


---

# Listener

A listener receives communication associated with authorised agents.

Conceptually:

```text
Agent
  |
  v
Transport
  |
  v
Listener
  |
  v
Team Server
```

Listeners may use different communication mechanisms depending on the framework and assessment design.


---

# Listener Inventory

Track active listeners.

Example:

| Listener | Purpose | Transport | Exposure | Redirected |
|---|---|---|---|---|
| `web-01` | Workstation testing | HTTPS | Public redirector | Yes |
| `lab-01` | Internal lab | HTTPS | Internal | No |

Do not create unnecessary listeners.


---

# Agents

An agent is the controlled component communicating with the C2 infrastructure.

Depending on the framework, agents may support:

```text
Command execution
Process information
Filesystem operations
Network discovery
Task execution
Session management
Data collection
Framework-specific extensions
```

Agent capabilities vary significantly between frameworks.

Only functionality permitted by the Rules of Engagement should be used.


---

# Agent Lifecycle

A useful operational model is:

```text
Generate
   |
   v
Record
   |
   v
Deploy
   |
   v
Execute
   |
   v
Operate
   |
   v
Collect Required Evidence
   |
   v
Terminate
   |
   v
Remove
   |
   v
Verify Cleanup
```

Every deployed assessment artifact should have a cleanup plan.


---

# C2 Transport

C2 communication requires a transport mechanism.

Common concepts include:

```text
HTTP
HTTPS
DNS
TCP
Named pipes
Framework-specific peer-to-peer channels
```

Availability depends on the framework.


---

# HTTP

A simplified HTTP C2 model:

```text
Agent
   |
   | HTTP
   v
Redirector
   |
   v
Listener
```

HTTP communication can be observed by:

```text
Endpoint telemetry
Network monitoring
Proxy logs
Firewall logs
Web server logs
DNS logs
```

Plain HTTP also exposes network content and should generally not be preferred for internet-facing assessment infrastructure.


---

# HTTPS

HTTPS adds TLS protection around the HTTP communication.

```text
Agent
   |
   | TLS
   v
Redirector
   |
   v
Listener
```

HTTPS does not make communication invisible.

Defenders can still observe metadata such as:

```text
Destination domain
Destination IP
Connection timing
Connection frequency
TLS characteristics
DNS lookups
Proxy metadata
Certificate information
Process responsible for connection
```


---

# DNS-Based Communication

Some C2 frameworks can use DNS-related communication.

Conceptually:

```text
Agent
   |
   v
DNS Query
   |
   v
Recursive Resolver
   |
   v
Authoritative Infrastructure
   |
   v
C2 Backend
```

DNS communication can produce distinctive telemetry.

Defensive monitoring can examine:

```text
Query volume
Query length
Subdomain entropy
Unusual record types
Rare domains
Newly observed domains
Repeated periodic queries
Endpoint process relationships
```

DNS-based communication should only be used where explicitly permitted because it can generate substantial infrastructure and monitoring activity.


---

# Direct TCP Communication

Some tools support direct TCP-based communication.

```text
Agent
   |
   v
TCP Connection
   |
   v
Listener
```

Direct connections can be simple operationally but may provide fewer infrastructure layers between the test host and backend.


---

# Peer-to-Peer Communication

Some frameworks support peer-to-peer communication between controlled systems.

Conceptually:

```text
Agent A
   |
   v
Agent B
   |
   v
Agent C
   |
   v
External C2
```

This may reduce the number of systems communicating directly with external infrastructure.

However, it also introduces additional complexity and should only be used when relevant to the engagement.


---

# Redirectors

A redirector sits between the authorised target environment and the C2 backend.

```text
Target
   |
   v
Redirector
   |
   v
Team Server
```

Potential benefits include:

```text
Backend isolation
TLS termination
Traffic filtering
Logging
Service separation
Simpler backend firewalling
Replaceable internet-facing infrastructure
```


---

# Redirector Architecture

A recommended conceptual separation is:

```text
                     Internet
                        |
                        v
                 +-------------+
                 | Redirector  |
                 +------+------+
                        |
                  Allowed Route
                        |
                        v
                 +-------------+
                 | Team Server |
                 +------+------+
                        |
                        v
                 Management VPN
                        |
                        v
                    Operator
```

The backend should preferably only accept the required operational traffic from known redirectors.


---

# Multiple Redirectors

Larger engagements may use multiple redirectors.

```text
                 Internet
                    |
         +----------+----------+
         |                     |
         v                     v
   Redirector A          Redirector B
         |                     |
         +----------+----------+
                    |
                    v
               Team Server
```

Potential reasons include:

```text
Separation of roles
Availability
Different engagement phases
Different network paths
Infrastructure replacement
Testing different control points
```


---

# Reverse Proxy

A reverse proxy is commonly used as part of redirector infrastructure.

Examples include:

```text
Nginx
Apache
Caddy
HAProxy
Traefik
Cloud load balancers
```

A reverse proxy can provide:

```text
TLS termination
Access logging
Backend routing
Request filtering
Rate limiting
Health checks
```


---

# Backend Firewalling

The backend should accept only necessary traffic.

Conceptually:

```text
Internet ----------X----------> Team Server

Redirector --------ALLOW------> Team Server

Operator VPN ------ALLOW------> Management Interface
```

Verify firewall rules from both the host and provider layers.


---

# Domains

C2 infrastructure may use dedicated assessment domains.

Example structure:

```text
assessment-example.net
        |
        +--> c2.assessment-example.net
        |
        +--> files.assessment-example.net
        |
        +--> vpn.assessment-example.net
```

Domains should be tracked as engagement resources.


---

# DNS Records

A typical HTTPS endpoint may use:

```text
c2.assessment-example.net
            |
            v
         A Record
            |
            v
       Redirector IP
```

Verify:

```bash
dig +short c2.assessment-example.net
```

or:

```bash
nslookup c2.assessment-example.net
```


---

# TLS Certificates

HTTPS infrastructure should use appropriately configured TLS.

Check a certificate:

```bash
openssl s_client -connect c2.assessment-example.net:443 -servername c2.assessment-example.net
```

Review:

```text
Subject
Issuer
Validity
SANs
Certificate chain
```

Certificate lifecycle should be included in infrastructure cleanup planning.


---

# Sleep

Periodic C2 agents commonly wait between check-ins.

Conceptually:

```text
Check In
   |
   v
Wait
   |
   v
Check In
   |
   v
Wait
```

The configured interval influences:

```text
Responsiveness
Network frequency
Infrastructure load
Operational tempo
Defensive visibility
```


---

# Jitter

Jitter introduces variation into a periodic interval.

Without variation:

```text
60
60
60
60
60
```

With variation:

```text
54
67
58
63
51
```

From a defensive perspective, periodic or near-periodic outbound communication remains an important behavioural signal.

The exact implementation varies by framework.


---

# C2 Timing

Timing should reflect the engagement objective.

Factors include:

```text
Testing window
Operational responsiveness
Network monitoring objectives
Endpoint monitoring objectives
Infrastructure capacity
Engagement duration
Rules of Engagement
```

Do not optimise solely for stealth.

For purple-team-oriented work, predictable activity may actually make telemetry correlation easier.


---

# Communication Profiles

Some frameworks allow communication behaviour to be configured through profiles.

Profiles may influence concepts such as:

```text
Request paths
Headers
Timing
Transport
Connection behaviour
Framework-specific metadata
```

Profiles should be treated as controlled engagement configuration.

Avoid attempting to impersonate unrelated organisations or abuse third-party infrastructure.


---

# C2 Framework Selection

Framework selection should be based on engagement requirements.

Consider:

```text
Operating systems
Agent support
Transport support
Team collaboration
Authentication
Logging
Extensibility
Infrastructure requirements
Detection objectives
Maintenance
Community activity
Rules of Engagement
```


---

# Cobalt Strike

Cobalt Strike is a commercial adversary simulation platform widely used in authorised red team operations.

Relevant concepts include:

```text
Team server
Client
Listeners
Beacon
Profiles
Post-exploitation capabilities
Collaborative operations
```

Official documentation should be used for framework-specific configuration.

[Cobalt Strike](https://www.cobaltstrike.com/){ target="_blank" rel="noopener noreferrer" }


---

# Sliver

Sliver is an open-source adversary emulation framework maintained by Bishop Fox.

Its architecture includes concepts such as:

```text
Server
Operators
Listeners
Implants
Sessions
Beacons
Extensions
```

[Sliver](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }


---

# Mythic

Mythic is a collaborative command-and-control platform designed around modular agents and communication components.

Concepts include:

```text
Mythic server
Operators
Payload types
Agents
C2 profiles
Tasks
Callbacks
```

[Mythic](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }


---

# Havoc

Havoc is an open-source command-and-control framework used for security research and authorised red team operations.

Framework capabilities and security characteristics can change over time, so use the project's current documentation when deploying it.

[Havoc](https://github.com/HavocFramework/Havoc){ target="_blank" rel="noopener noreferrer" }


---

# Metasploit Framework

Metasploit provides exploitation and post-exploitation capabilities and can also manage controlled sessions.

Common concepts include:

```text
Exploit modules
Payloads
Handlers
Sessions
Meterpreter
Post modules
```

[Metasploit Framework](https://github.com/rapid7/metasploit-framework){ target="_blank" rel="noopener noreferrer" }


---

# MITRE CALDERA

MITRE CALDERA focuses on automated adversary emulation.

It can be useful when the objective is repeatable security-control validation rather than traditional operator-driven red teaming.

[MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }


---

# Framework Comparison

A conceptual comparison:

| Framework | Model | Typical Use |
|---|---|---|
| Cobalt Strike | Commercial C2 | Red teaming |
| Sliver | Open-source C2 | Red teaming and research |
| Mythic | Modular C2 platform | Collaborative red teaming |
| Havoc | Open-source C2 | Red teaming and research |
| Metasploit | Exploitation framework | Penetration testing and controlled sessions |
| CALDERA | Adversary emulation | Automated security validation |

Capabilities evolve, so verify current framework documentation before relying on a particular feature.


---

# C2 Authentication

Operator authentication should be protected.

Consider:

```text
Individual operator accounts
Strong passwords
MFA where supported
VPN restrictions
Source restrictions
Credential rotation
Account removal after engagement
```

Do not expose administrative interfaces unnecessarily.


---

# C2 Secrets

Potentially sensitive C2 material includes:

```text
Operator credentials
TLS private keys
Framework secrets
Agent configuration
Listener secrets
API tokens
Infrastructure credentials
VPN keys
SSH keys
```

These should not be committed to public repositories.


---

# C2 Configuration Storage

A controlled directory structure may resemble:

```text
redteam/
├── infrastructure/
├── c2/
├── redirectors/
├── logs/
└── inventory/
```

Secrets should be stored separately from normal configuration where practical.


---

# Git Exclusions

Example:

```gitignore
.env
*.key
*.pem
*.pfx
*.p12
secrets/
credentials/
logs/
engagement-data/
```

Always review staged files before committing:

```bash
git status
```

and:

```bash
git diff --cached
```


---

# Agent Tracking

Maintain an inventory of controlled agents.

Example:

| Agent | Host | User | First Seen | Purpose | Cleanup |
|---|---|---|---|---|---|
| `A01` | `TEST-WKS01` | `testuser` | 10:15 UTC | Detection test | Required |
| `A02` | `TEST-SRV01` | `svc-test` | 11:04 UTC | Lateral movement validation | Required |

This is particularly important when multiple operators are active.


---

# Task Tracking

Important actions should be traceable.

Record:

```text
Timestamp
Operator
Agent
Host
Identity
Task
Result
Objective
Evidence
```

Example:

```text
2026-09-05 11:12 UTC
Operator: A
Agent: A01
Host: TEST-WKS01
Task: Identity enumeration
Result: Successful
Objective: Establish security context
```


---

# C2 Logging

Preserve enough C2 logs to reconstruct assessment activity.

Potential logs include:

```text
Operator login
Listener creation
Agent registration
Task execution
Task results
Agent termination
Infrastructure errors
Framework events
```

Log retention should follow the engagement agreement.


---

# Network Logging

Infrastructure-side telemetry can include:

```text
Reverse-proxy access logs
Firewall logs
DNS logs
VPN logs
TLS logs
Cloud flow logs
Provider firewall logs
```

These logs help reconstruct communication independently from the C2 framework.


---

# Time Synchronisation

Synchronise infrastructure clocks.

Check:

```bash
timedatectl
```

Prefer a consistent timeline such as UTC.

```text
Operator activity: UTC
C2 logs: UTC
Redirector logs: UTC
Evidence: UTC
Blue-team comparison: converted consistently
```


---

# Defensive Visibility

C2 activity can produce evidence at several layers.

```text
+----------------------+
|       Endpoint       |
+----------------------+
           |
           v
+----------------------+
|       Network        |
+----------------------+
           |
           v
+----------------------+
|         DNS          |
+----------------------+
           |
           v
+----------------------+
|        Proxy         |
+----------------------+
           |
           v
+----------------------+
|      Firewall        |
+----------------------+
           |
           v
+----------------------+
|         SIEM         |
+----------------------+
```


---

# Endpoint Detection

Endpoint telemetry may reveal:

```text
Process creation
Parent-child relationships
Network connections
Module loads
Script execution
File creation
Service activity
Scheduled tasks
Authentication activity
Memory-related telemetry
Security-control alerts
```

Exact visibility depends on the endpoint security stack.


---

# Network Detection

Network monitoring may identify:

```text
Unusual destinations
Rare domains
Periodic connections
Long-lived sessions
Unexpected ports
DNS anomalies
Proxy anomalies
TLS metadata
Unusual connection volume
```

Encrypted traffic still exposes useful metadata.


---

# DNS Detection

Useful DNS signals can include:

```text
Newly observed domains
Rare domains
High-entropy labels
Repeated queries
Unusual record types
Long labels
Unexpected query volume
Endpoint-to-domain relationships
```


---

# Proxy Detection

Proxy telemetry can reveal:

```text
Destination
HTTP method
Request frequency
Response size
User identity
Endpoint identity
TLS information
Category
Policy result
```

Where TLS inspection is used, additional visibility may exist depending on organisational policy and architecture.


---

# Firewall Detection

Firewall logs can provide:

```text
Source IP
Destination IP
Destination port
Protocol
Connection duration
Bytes transferred
Allow or deny decision
```


---

# C2 Behaviour Analytics

One useful defensive concept is beaconing analysis.

Conceptually:

```text
Connection
   |
   v
Wait
   |
   v
Connection
   |
   v
Wait
   |
   v
Connection
```

Analysts can examine:

```text
Periodicity
Destination rarity
Connection duration
Byte patterns
Domain age
Endpoint process
Time of day
Peer population
```

No single signal should automatically be treated as proof of C2.


---

# Baseline vs Anomaly

Detection works better when behaviour is compared with a baseline.

```text
Normal Endpoint
     |
     +--> Microsoft services
     +--> Corporate applications
     +--> Known SaaS

Test Endpoint
     |
     +--> Normal traffic
     +--> Rare assessment domain
```

The rare destination may provide useful investigative context.


---

# Detection Validation

During an authorised assessment, record whether each C2 stage is visible.

Example:

| Stage | Telemetry | Alert | Investigated |
|---|---|---|---|
| DNS lookup | Yes | No | No |
| HTTPS connection | Yes | No | No |
| Agent execution | Yes | Yes | Yes |
| Task execution | Yes | Yes | Yes |

This makes the exercise useful beyond simply demonstrating connectivity.


---

# Purple Team C2 Testing

C2 behaviours are particularly suitable for purple teaming.

```text
Red Team
   |
   v
Execute Controlled Behaviour
   |
   v
Blue Team
   |
   v
Observe Telemetry
   |
   v
Create / Tune Detection
   |
   v
Repeat
```

This allows individual behaviours to be tested without requiring a complete attack chain.


---

# C2 Infrastructure Hardening

Protect C2 infrastructure using multiple layers.

```text
Provider Firewall
       |
       v
Host Firewall
       |
       v
Management VPN
       |
       v
Strong Authentication
       |
       v
Restricted Team Server
       |
       v
Redirector
       |
       v
TLS
```


---

# Server Baseline

Before deployment:

```bash
sudo apt update
```

```bash
sudo apt full-upgrade -y
```

Review listening services:

```bash
sudo ss -lntup
```

Review firewall:

```bash
sudo nft list ruleset
```

or, where UFW is used:

```bash
sudo ufw status numbered
```


---

# SSH

Prefer key-based administration.

Example connection:

```bash
ssh -i ~/.ssh/redteam-engagement operator@SERVER
```

Review effective SSH settings:

```bash
sudo sshd -T
```

Validate configuration before reload:

```bash
sudo sshd -t
```


---

# Provider Firewall

A layered architecture:

```text
Internet
   |
   v
Cloud / Provider Firewall
   |
   v
Host Firewall
   |
   v
C2 Infrastructure
```

Management ports should normally be restricted to authorised source addresses or a management network.


---

# C2 Availability

Operational infrastructure may fail.

Possible causes include:

```text
Server failure
Network failure
DNS failure
Certificate expiry
Firewall error
Provider issue
Configuration error
Disk exhaustion
Process crash
```

Monitor infrastructure during active engagements.


---

# Health Checks

Examples:

```bash
uptime
```

```bash
df -h
```

```bash
free -h
```

```bash
ss -lntup
```

```bash
systemctl --failed
```


---

# Redirector Health

For HTTPS infrastructure:

```bash
curl -I https://c2.assessment-example.net/
```

TLS validation:

```bash
openssl s_client -connect c2.assessment-example.net:443 -servername c2.assessment-example.net
```

The expected HTTP response depends on the infrastructure design.


---

# Kill Switch

A C2 architecture should have a rapid shutdown mechanism.

Possible actions include:

```text
Disable listener
Stop redirector
Block operational port
Remove DNS record
Revoke operator access
Terminate controlled agents
Disable infrastructure
```

The procedure should be known before testing begins.


---

# Emergency Model

```text
Unexpected Event
       |
       v
Stop Tasking
       |
       v
Disable Listener
       |
       v
Restrict Infrastructure
       |
       v
Preserve Required Logs
       |
       v
Contact Engagement Lead
       |
       v
Investigate
```


---

# Agent Cleanup

When an agent is no longer required:

```text
Stop Tasking
    |
    v
Terminate Session
    |
    v
Remove Assessment Artifact
    |
    v
Remove Persistence if Used
    |
    v
Verify Process Stopped
    |
    v
Verify File Removed
    |
    v
Record Cleanup
```

Do not assume closing a session removes the deployed artifact.


---

# Infrastructure Cleanup

At engagement completion:

```text
Stop listeners
       |
       v
Terminate agents
       |
       v
Collect required logs
       |
       v
Remove payloads
       |
       v
Revoke temporary credentials
       |
       v
Remove DNS
       |
       v
Remove firewall exceptions
       |
       v
Destroy temporary servers
       |
       v
Verify cleanup
```


---

# C2 Evidence

For each meaningful C2 event, record:

```text
Timestamp
Operator
Agent
Host
Identity
Listener
Transport
Action
Result
Detection result
Evidence reference
```

This enables later correlation with defensive telemetry.


---

# C2 Reporting

The final report should not simply state:

```text
C2 established successfully.
```

Instead explain:

```text
How communication was established
Which system communicated externally
Which transport was used
Which controls observed it
Which controls alerted
How long detection took
Whether the activity was investigated
What defensive gaps were identified
```


---

# Example Detection Narrative

```text
The authorised test workstation established HTTPS communication
with the assessment redirector.

Endpoint telemetry recorded the originating process and outbound
connection.

The DNS lookup and HTTPS connection were present in network telemetry.

No alert was generated for the initial communication.

Subsequent controlled task execution generated an endpoint alert,
which was investigated by the defensive team.
```

This provides substantially more value than merely documenting successful connectivity.


---

# MITRE ATT&CK

Command and Control is represented by the MITRE ATT&CK Command and Control tactic.

Relevant technique families can include communication through:

```text
Application-layer protocols
Non-application-layer protocols
Proxy infrastructure
Encrypted channels
Web services
```

Map only techniques actually demonstrated during the engagement.

[MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }


---

# C2 Operational Checklist

## Planning

- [ ] Written authorisation confirmed
- [ ] C2 use permitted
- [ ] Infrastructure documented
- [ ] Framework selected
- [ ] Required transports identified
- [ ] Domains prepared
- [ ] Redirectors prepared
- [ ] Logging requirements defined
- [ ] Cleanup requirements defined
- [ ] Kill switch documented

## Team Server

- [ ] Operating system updated
- [ ] Management access restricted
- [ ] Strong authentication configured
- [ ] Operator accounts reviewed
- [ ] Firewall configured
- [ ] Logging enabled
- [ ] Time synchronised
- [ ] Backups considered

## Redirector

- [ ] Internet exposure limited
- [ ] TLS configured
- [ ] Backend restricted
- [ ] Access logging enabled
- [ ] Firewall configured
- [ ] DNS verified
- [ ] Replacement procedure documented

## Listeners

- [ ] Listener purpose documented
- [ ] Exposure understood
- [ ] Transport approved
- [ ] Listener inventory maintained
- [ ] Unused listeners disabled

## Agents

- [ ] Agent purpose documented
- [ ] Host recorded
- [ ] Identity recorded
- [ ] Deployment time recorded
- [ ] Tasks remained in scope
- [ ] Cleanup required flag recorded

## Detection

- [ ] Endpoint telemetry reviewed
- [ ] Network telemetry reviewed
- [ ] DNS telemetry reviewed
- [ ] Proxy telemetry reviewed
- [ ] Firewall telemetry reviewed
- [ ] Alerts recorded
- [ ] Investigation response recorded

## Cleanup

- [ ] Tasking stopped
- [ ] Agents terminated
- [ ] Assessment files removed
- [ ] Persistence removed if applicable
- [ ] Listeners disabled
- [ ] Required logs collected
- [ ] DNS removed where required
- [ ] Temporary credentials revoked
- [ ] Infrastructure destroyed where appropriate
- [ ] Cleanup verified


---

# C2 Decision Model

```text
                  Need C2?
                  /     \
                No       Yes
                |         |
                |         v
                |    Select Framework
                |         |
                |         v
                |    Select Transport
                |         |
                |         v
                |   Public Listener?
                |      /       \
                |    No         Yes
                |    |           |
                |    |           v
                |    |      Redirector
                |    |           |
                |    +-----+-----+
                |          |
                |          v
                |      Firewall
                |          |
                |          v
                |       TLS / DNS
                |          |
                |          v
                |        Logging
                |          |
                |          v
                |       Validate
                |          |
                +----------+
                           |
                           v
                       Operation
                           |
                           v
                     Detection Review
                           |
                           v
                        Cleanup
```


---

# Final C2 Model

```text
                         Operator
                            |
                            v
                     Management VPN
                            |
                            v
                     +-------------+
                     | Team Server |
                     +------+------+
                            |
                            v
                       Listener
                            |
                            v
                     +-------------+
                     | Redirector  |
                     +------+------+
                            |
                          HTTPS
                            |
                            v
                         Internet
                            |
                            v
                    Authorised Agent


Defensive Visibility
--------------------

Agent
 |
 +--> Process telemetry
 |
 +--> Network telemetry
 |
 +--> DNS telemetry
 |
 +--> Proxy telemetry
 |
 +--> Firewall telemetry
 |
 +--> EDR
 |
 +--> SIEM
 |
 +--> Incident Response


Operational Lifecycle
---------------------

Plan
 |
 v
Build
 |
 v
Harden
 |
 v
Validate
 |
 v
Operate
 |
 v
Measure Detection
 |
 v
Collect Evidence
 |
 v
Terminate Agents
 |
 v
Remove Infrastructure
 |
 v
Verify Cleanup
```


---

# Related Notes

- [Red Teaming](./)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Active Directory](../active-directory/)
- [PrivEsc Explorer](../privesc/)


---

# References

- [MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }
- [Cobalt Strike](https://www.cobaltstrike.com/){ target="_blank" rel="noopener noreferrer" }
- [Sliver](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }
- [Mythic](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }
- [Havoc](https://github.com/HavocFramework/Havoc){ target="_blank" rel="noopener noreferrer" }
- [Metasploit Framework](https://github.com/rapid7/metasploit-framework){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Nginx Documentation](https://nginx.org/en/docs/){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [WireGuard](https://www.wireguard.com/){ target="_blank" rel="noopener noreferrer" }
- [Let's Encrypt](https://letsencrypt.org/){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Command-and-control infrastructure should only be deployed for explicitly authorised security assessments and controlled security research. Restrict C2 activity to approved systems, identities, networks, and objectives. Protect operator credentials and customer information, maintain an inventory of deployed agents, and verify that assessment artifacts and temporary infrastructure are removed when testing is complete.
