---
title: Red Team Methodology
description: End-to-end red team methodology for authorised security assessments, covering planning, reconnaissance, infrastructure, initial access, command and control, situational awareness, privilege escalation, credential access, lateral movement, persistence, defence evasion, objectives, detection validation, evidence, cleanup, and reporting.
---

# Red Team Methodology

A red team assessment evaluates how an organisation withstands a realistic attack against defined objectives.

Unlike isolated vulnerability testing, red teaming focuses on complete attack paths.

```text
Reconnaissance
      |
      v
Initial Access
      |
      v
Foothold
      |
      v
Situational Awareness
      |
      v
Privilege Escalation
      |
      v
Credential Access
      |
      v
Internal Discovery
      |
      v
Lateral Movement
      |
      v
Objective
```

Supporting activities may include:

```text
Infrastructure
Command and Control
Persistence
Defence Evasion
Pivoting
Detection Validation
Evidence Collection
```

The objective is not to execute every possible technique.

The objective is to determine whether realistic attacker behaviour can achieve the agreed goals and whether the organisation can prevent, detect, investigate, and respond to that behaviour.


---

# Authorisation

Red team activity must operate within explicit written authorisation.

Before testing begins, establish:

```text
Customer
Authorising authority
Assessment dates
In-scope organisations
In-scope systems
In-scope identities
In-scope networks
Permitted techniques
Prohibited techniques
Testing windows
Emergency contacts
Stop conditions
Data-handling requirements
Cleanup requirements
```

When an action falls outside the Rules of Engagement, do not perform it simply because it is technically possible.


---

# Red Team Engagement Model

```text
                  Authorisation
                       |
                       v
                    Planning
                       |
                       v
                 Threat Modelling
                       |
                       v
                Reconnaissance
                       |
                       v
                 Initial Access
                       |
                       v
                    Foothold
                       |
                       v
             Situational Awareness
                       |
             +---------+---------+
             |                   |
             v                   v
      Privilege Escalation   Credential Access
             |                   |
             +---------+---------+
                       |
                       v
               Internal Discovery
                       |
                       v
                Lateral Movement
                       |
                       v
                Target Objective
                       |
                       v
               Detection Review
                       |
                       v
                    Cleanup
                       |
                       v
                   Reporting
```


---

# Red Teaming vs Penetration Testing

The two disciplines overlap but normally have different emphasis.

| Area | Penetration Testing | Red Teaming |
|---|---|---|
| Primary focus | Vulnerabilities | Attack paths |
| Scope | Systems/applications | Organisational objective |
| Techniques | Broad testing | Selected realistic techniques |
| Detection | Useful | Core measurement |
| Stealth | Usually secondary | Scenario dependent |
| Duration | Often shorter | Often longer |
| Findings | Individual weaknesses | Attack chains and control gaps |
| SOC evaluation | Optional | Frequently important |
| Threat model | Useful | Usually central |


---

# Phase 0 - Engagement Preparation

Do not begin technical activity until the engagement is operationally ready.

Confirm:

- [ ] Rules of Engagement approved
- [ ] Scope approved
- [ ] Testing window approved
- [ ] Emergency contacts confirmed
- [ ] Stop conditions defined
- [ ] Infrastructure prepared
- [ ] Evidence handling agreed
- [ ] Data restrictions understood
- [ ] Cleanup responsibilities agreed
- [ ] Detection coordination model agreed


---

# Rules of Engagement

The Rules of Engagement should define what is allowed.

Typical categories include:

```text
External reconnaissance
Active scanning
Password spraying
Social engineering
Payload execution
C2
Privilege escalation
Credential access
Lateral movement
Persistence
Defence evasion
Cloud testing
Physical testing
Data access
Exfiltration simulation
Denial of service
Production modifications
```

Never assume permission for a high-impact activity because another activity was authorised.


---

# Stop Conditions

Examples include:

```text
Production instability
Unexpected customer impact
Access to excluded systems
Access to highly sensitive excluded data
Unexpected privileged access
Security incident unrelated to testing
Loss of control over assessment infrastructure
Customer request
Safety concern
```

Operators should know exactly who can stop the engagement.


---

# Phase 1 - Define Objectives

Red team objectives should describe outcomes rather than tools.

Weak objective:

```text
Get Domain Admin.
```

Better objective:

```text
Determine whether an external attacker can obtain administrative
control over systems supporting the defined business service.
```

Another example:

```text
Determine whether a compromised standard-user workstation can be
used to access the defined sensitive application and whether the
SOC detects the attack path.
```


---

# Objective Model

```text
Threat Actor
     |
     v
Starting Position
     |
     v
Attack Path
     |
     v
Target Asset
     |
     v
Business Objective
```


---

# Crown Jewels

Identify assets that matter to the scenario.

Examples:

```text
Domain controllers
Identity providers
Certificate authorities
Cloud administration
Critical applications
Source-code repositories
CI/CD infrastructure
Sensitive databases
Backup systems
Virtualisation platforms
Management networks
Privileged workstations
```


---

# Phase 2 - Threat Modelling

Threat modelling determines which attacker behaviours are relevant.

Consider:

```text
Attacker capability
Attacker motivation
Initial access opportunities
Target industry
Technology stack
Identity architecture
Cloud architecture
Security controls
Likely objectives
```

MITRE ATT&CK can help map expected behaviours.


---

# Threat-Informed Testing

A threat-informed assessment may select techniques based on:

```text
Known threat groups
Industry targeting
Recent incidents
Technology used by the organisation
Previous security findings
Threat intelligence
Business risks
```

Do not mechanically execute every ATT&CK technique.


---

# ATT&CK Mapping

A simplified attack chain might map to:

```text
Reconnaissance
      |
      v
Initial Access
      |
      v
Execution
      |
      v
Persistence
      |
      v
Privilege Escalation
      |
      v
Defense Evasion
      |
      v
Credential Access
      |
      v
Discovery
      |
      v
Lateral Movement
      |
      v
Command and Control
      |
      v
Collection
      |
      v
Objective
```


---

# Phase 3 - Infrastructure

Assessment infrastructure should be prepared before operational testing.

Typical components:

```text
Operator Workstation
        |
        v
Management Network
        |
        v
Assessment Infrastructure
        |
        +--> C2
        |
        +--> DNS
        |
        +--> Web
        |
        +--> File Hosting
        |
        +--> Redirector / Edge
        |
        v
Authorised Targets
```

Use:

[Red Team Infrastructure](infrastructure.md)


---

# Infrastructure Checklist

Confirm:

- [ ] Administrative interfaces restricted
- [ ] Strong authentication configured
- [ ] MFA enabled where supported
- [ ] SSH keys protected
- [ ] Firewall configured
- [ ] Required ports documented
- [ ] DNS configured
- [ ] TLS configured
- [ ] Logging enabled
- [ ] Time synchronised
- [ ] Payload hashes recorded
- [ ] Engagement resources isolated
- [ ] Emergency shutdown available
- [ ] Decommission plan documented


---

# Phase 4 - Reconnaissance

Reconnaissance builds understanding of the target.

Start with passive sources where practical.

Potential information includes:

```text
Domains
Subdomains
IP ranges
ASN information
Cloud services
Email infrastructure
VPN portals
Identity providers
Technology stacks
Public applications
Source-code repositories
Employee information
Third-party services
```


---

# Passive Reconnaissance

Examples include:

```text
DNS
Certificate Transparency
Search engines
Public repositories
Public documents
WHOIS/RDAP
Internet exposure databases
Job advertisements
Technology fingerprinting
```


---

# Active Reconnaissance

Where authorised:

```text
DNS resolution
HTTP probing
Port scanning
Service identification
Web crawling
Application enumeration
Authentication portal identification
```

Active reconnaissance generates target telemetry and should remain within scope.


---

# Reconnaissance Pipeline

```text
Root Domain
    |
    v
Subdomain Discovery
    |
    v
DNS Resolution
    |
    v
Alive Hosts
    |
    v
Port / Service Discovery
    |
    v
Technology Identification
    |
    v
Attack Surface
```


---

# Maintain an Attack Surface Inventory

Example:

| Asset | Type | Technology | Authentication | Exposure | Notes |
|---|---|---|---|---|---|
| `portal.example.test` | Web | IIS | SSO | Internet | Primary portal |
| `vpn.example.test` | VPN | VPN gateway | MFA | Internet | Remote access |
| `api.example.test` | API | HTTPS | Token | Internet | API endpoint |


---

# Phase 5 - Initial Access

Initial access establishes the first authorised foothold.

Potential assessment vectors depend on the Rules of Engagement.

Examples include:

```text
Web application vulnerability
Exposed service
Credential weakness
Password spraying
Customer-provided assumed breach
Social engineering
VPN weakness
Cloud identity weakness
Supply-chain simulation
```

Use:

[Initial Access](initial-access.md)


---

# Assume Breach

An assumed-breach engagement may intentionally skip external compromise.

Example starting position:

```text
Standard domain user
        +
Corporate workstation
        +
Internal network access
```

This allows more time to evaluate:

```text
Internal segmentation
Identity controls
Credential protection
Privilege escalation
Lateral movement
Detection
Response
```


---

# Phase 6 - Establish Foothold

Once initial access succeeds, avoid immediately executing large amounts of tooling.

First determine:

```text
Where am I?
Who am I?
What privilege do I have?
What security controls exist?
What network am I connected to?
What is the assessment objective?
```


---

# Windows Situational Awareness

Identity:

```powershell
whoami
```

Detailed token:

```powershell
whoami /all
```

Hostname:

```powershell
hostname
```

Network:

```powershell
ipconfig /all
```

Routes:

```powershell
route print
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

# Linux Situational Awareness

Identity:

```bash
id
```

Hostname:

```bash
hostname
```

Operating system:

```bash
cat /etc/os-release
```

Network:

```bash
ip addr
```

Routes:

```bash
ip route
```

Processes:

```bash
ps aux
```


---

# Phase 7 - Security Control Discovery

Determine which controls influence the next steps.

Examples:

```text
EDR
Antivirus
Application control
Firewall
Proxy
PowerShell restrictions
AMSI
ASR
Credential Guard
LSA protection
Network segmentation
MFA
PAM
Logging
SIEM
```


---

# Microsoft Defender

Where available:

```powershell
Get-MpComputerStatus
```

Record the control state before performing tests.


---

# PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible output may include:

```text
FullLanguage
ConstrainedLanguage
```


---

# AppLocker

```powershell
Get-AppLockerPolicy -Effective
```

Summarise:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType, EnforcementMode
```


---

# Phase 8 - Host Enumeration

Host enumeration should identify potential paths rather than collect everything indiscriminately.

Windows areas include:

```text
Users
Groups
Privileges
Services
Scheduled tasks
Installed applications
Processes
Network connections
Credentials
Shares
Security controls
Writable directories
Configuration files
```


---

# Linux Areas

```text
Users
Groups
sudo
SUID/SGID
Capabilities
Cron
systemd
Credentials
SSH
Containers
Mounted filesystems
NFS
Writable paths
Processes
Network services
```


---

# Enumeration Principle

```text
Observation
    |
    v
Potential Path
    |
    v
Prerequisites
    |
    v
Safe Validation
    |
    v
Confirmed?
```

Do not confuse enumeration output with confirmed vulnerabilities.


---

# Phase 9 - Privilege Escalation

Privilege escalation attempts to obtain greater permissions.

Typical progression:

```text
Standard User
     |
     v
Local Administrator / root
     |
     v
Privileged Credentials
     |
     v
Broader Environment Access
```

Use:

- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)


---

# Windows Privilege Escalation Areas

Review:

```text
Services
Scheduled tasks
Registry
Privileges
Writable paths
Application configuration
Stored credentials
Installer policy
Application control
Local groups
```


---

# Linux Privilege Escalation Areas

Review:

```text
sudo
SUID
SGID
Capabilities
Cron
systemd
Writable scripts
PATH
Credentials
Containers
NFS
Kernel context
```


---

# Minimum Necessary Validation

Do not execute every possible escalation.

Prefer:

```text
Candidate
   |
   v
Validate Permissions
   |
   v
Confirm Execution Context
   |
   v
Objective Proven
   |
   v
STOP
```

This reduces unnecessary system modification.


---

# Phase 10 - Credential Access

Credentials can enable movement across systems and security boundaries.

Potential credential material includes:

```text
Passwords
NTLM hashes
Kerberos tickets
SSH keys
API keys
Tokens
Certificates
Browser credentials
Cloud credentials
Service-account secrets
Configuration secrets
```


---

# Credential Access Questions

Ask:

```text
Which credentials are available?
Why are they available?
Which identity owns them?
Where can they be used?
Are they privileged?
Are they reusable?
Are they protected?
Was access detected?
```


---

# Credential Handling

Treat obtained credentials as sensitive assessment data.

Never place credentials in:

```text
Public repositories
Screenshots unnecessarily
Chat systems
Unencrypted notes
Shared terminals
Shell scripts committed to Git
```


---

# Credential Chain

```text
Compromised Host
      |
      v
Credential Material
      |
      v
Identity
      |
      v
Accessible Systems
      |
      v
Higher-Value Asset
```

Use:

[Credential Access](credential-access.md)


---

# Phase 11 - Active Directory Discovery

When the environment uses Active Directory, build an understanding of:

```text
Domain
Forest
Users
Groups
Computers
Sessions
SPNs
Delegation
ACLs
GPOs
Trusts
Certificate Services
Privileged identities
```


---

# Active Directory

Use the dedicated section:

[Active Directory](../active-directory/)


---

# BloodHound

BloodHound can help model relationships between:

```text
Users
Groups
Computers
Sessions
ACLs
Delegation
Certificate Services
Trusts
```

Use:

[BloodHound](../active-directory/bloodhound.md)


---

# Attack Path Analysis

Do not simply search for Domain Admin.

Analyse paths such as:

```text
Current User
     |
     v
Writable Group
     |
     v
Service Account
     |
     v
Server Admin
     |
     v
Privileged Session
     |
     v
Critical Asset
```


---

# Phase 12 - Lateral Movement

Lateral movement uses existing access or credentials to reach another authorised system.

Use:

[Lateral Movement](lateral-movement.md)


---

# Common Windows Remote Management Paths

Depending on configuration:

```text
SMB
WinRM
WMI
RDP
DCOM
Remote services
Scheduled tasks
```

These are legitimate administration mechanisms.

Their existence alone is not a vulnerability.


---

# Linux Remote Administration

Common mechanisms include:

```text
SSH
Configuration-management systems
Administrative APIs
Container management
Orchestration platforms
```


---

# Credential Reuse

A common movement path is:

```text
Host A
  |
  v
Credential
  |
  v
Host B
  |
  v
Additional Credential
  |
  v
Host C
```

This demonstrates why credential isolation is important.


---

# Network Segmentation

Before moving to another host, determine whether the connection should be permitted.

```text
Source
   |
   v
Network Control
   |
   +--> Allowed
   |
   +--> Blocked
```

A blocked path is useful assessment evidence.


---

# Pivoting

Sometimes an operator cannot directly reach the next target.

```text
Operator
    |
    v
Foothold
    |
    v
Internal Network
    |
    v
Target
```

A controlled tunnel or proxy may be used when authorised.


---

# Ligolo-ng

Ligolo-ng can provide a tunnel between an operator and an authorised pivot host.

Conceptually:

```text
Operator
    |
    v
Ligolo Proxy
    |
    v
Ligolo Agent
    |
    v
Internal Network
```

Use it only for networks explicitly included in the assessment scope.


---

# Chisel

Chisel provides TCP tunnelling over HTTP/WebSocket transport.

Conceptually:

```text
Operator
    |
    v
Chisel Server
    |
    v
Chisel Client
    |
    v
Internal Service
```

Tunnelling should be documented because it changes the apparent network source of subsequent assessment activity.


---

# SSH Tunnelling

SSH can provide native forwarding where SSH access already exists.

Types include:

```text
Local forwarding
Remote forwarding
Dynamic SOCKS forwarding
```

SSH tunnelling may be preferable when it uses an existing approved administrative channel.


---

# SOCKS Proxy

A SOCKS proxy can allow compatible assessment tools to reach systems through a pivot.

```text
Assessment Tool
      |
      v
SOCKS
      |
      v
Pivot
      |
      v
Internal Target
```

Ensure tools do not accidentally reach excluded networks through the proxy.


---

# Phase 13 - Command and Control

C2 provides an operator communication channel to an authorised assessment component.

Use:

[Command and Control](command-and-control.md)


---

# C2 Questions

Record:

```text
Which host?
Which user?
Which protocol?
Which destination?
Which port?
Which process?
Which security controls observed it?
Was the connection blocked?
Was it detected?
```


---

# C2 Architecture

```text
Operator
   |
   v
Management Plane
   |
   v
Team Server
   |
   v
Edge / Redirector
   |
   v
Assessment Host
```

Administrative interfaces should not be unnecessarily exposed to target networks or the public Internet.


---

# Phase 14 - Persistence

Persistence is only necessary when required by the scenario.

Use:

[Persistence](persistence.md)

Possible categories include:

```text
Scheduled tasks
Services
Startup mechanisms
SSH keys
Accounts
Directory permissions
Certificates
Cloud identities
```


---

# Persistence Rule

Before creating persistence:

```text
Is it necessary?
      |
     / \
   No   Yes
   |     |
 STOP    v
      Explicitly
      Authorised?
       /      \
      No       Yes
      |         |
     STOP       v
            Deploy Minimum
            Necessary Test
```


---

# Phase 15 - Defence Evasion

Defence evasion testing determines whether defensive controls provide the intended protection.

Use:

[Defence Evasion](defence-evasion.md)


---

# Defence Evasion Test Progression

```text
Configuration Review
        |
        v
Harmless Test
        |
        v
Vendor Test Artifact
        |
        v
Controlled Simulation
        |
        v
Technique Validation
        |
        v
Stop When Objective Proven
```


---

# Security Controls

Relevant controls can include:

```text
Microsoft Defender
EDR
AMSI
PowerShell CLM
AppLocker
WDAC
ASR
Firewall
Proxy
Network Protection
Credential Guard
LSA protection
Logging
SIEM
```


---

# EICAR

EICAR can safely validate antivirus detection.

```text
Test Artifact
     |
     v
Antivirus
     |
     v
Detection / Quarantine
     |
     v
EDR / SIEM
```

EICAR does not replace behavioural EDR testing.


---

# Phase 16 - Objective Execution

The assessment should eventually answer the business objective.

Example:

```text
Can an external attacker access the finance reporting system?
```

Attack chain:

```text
External Exposure
      |
      v
Initial Access
      |
      v
Workstation
      |
      v
Credential Access
      |
      v
Server Access
      |
      v
Application Access
      |
      v
Finance Reporting System
```


---

# Proof of Access

Use the least invasive proof possible.

Examples:

```text
Directory listing
Hostname
Database name
Synthetic record
Application role
File metadata
Screenshot
Authorised marker file
```

Avoid unnecessary access to real sensitive data.


---

# Synthetic Data

Where data access or exfiltration must be demonstrated, use synthetic test data whenever possible.

Example:

```text
red-team-proof.txt
```

containing:

```text
Authorised red team assessment test file.
No production data.
```

This can prove the path without exposing customer information.


---

# Phase 17 - Detection Validation

A red team engagement should evaluate the defensive chain.

```text
Activity
   |
   v
Telemetry
   |
   v
Detection
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
Containment
   |
   v
Response
```


---

# Prevention vs Detection

Track both.

| Technique | Prevented | Logged | Alerted | Investigated |
|---|---|---|---|---|
| Initial access test | No | Yes | Yes | Yes |
| PrivEsc test | Yes | Yes | Yes | Yes |
| Credential access | No | Yes | No | No |
| Lateral movement | No | Yes | Yes | Yes |
| Persistence test | No | Yes | No | No |


---

# Detection Gap

A useful detection finding describes:

```text
Activity
Expected Telemetry
Observed Telemetry
Alert
SOC Visibility
Investigation
Response
```

Avoid simply writing:

```text
EDR bypassed.
```


---

# Detection Quality

A detection may exist but still be ineffective.

Consider:

```text
Was the alert timely?
Was severity appropriate?
Was context useful?
Was the correct host identified?
Was the correct user identified?
Was the attack chain visible?
Was it investigated?
Was containment possible?
```


---

# Phase 18 - Evidence Collection

Evidence should be collected continuously.

For every important action record:

```text
Timestamp
Operator
Source
Target
Identity
Command or technique
Result
Security control
Detection result
Evidence location
Cleanup requirement
```


---

# Timestamp Standard

Prefer a consistent timezone such as UTC.

Example:

```text
2026-09-05 18:42:11 UTC
```

Infrastructure and target clocks should be synchronised where possible.


---

# Operator Log

Example:

| Time | Operator | Source | Target | Action | Result |
|---|---|---|---|---|---|
| 10:12 | OP01 | RT01 | WS01 | Initial access validation | Success |
| 10:24 | OP01 | WS01 | WS01 | PrivEsc validation | Blocked |
| 10:41 | OP02 | WS01 | SRV01 | WinRM authentication | Success |


---

# Evidence Quality

Good evidence demonstrates:

```text
Who
What
Where
When
How
Impact
```

Avoid screenshots without context.


---

# Screenshot Naming

A useful convention:

```text
YYYYMMDD-HHMM-host-technique-description.png
```

Example:

```text
20260905-1420-WS01-applocker-policy.png
```


---

# Command Logging

Record commands that materially support findings.

Do not flood reports with every enumeration command.

Keep detailed operator logs separately from the executive report.


---

# Phase 19 - Attack Path Documentation

Individual findings often make more sense when combined into an attack path.

Example:

```text
External Application
       |
       | Initial Access
       v
Standard User
       |
       | Writable Service
       v
Local Administrator
       |
       | Credential Exposure
       v
Server Administrator
       |
       | Credential Reuse
       v
Critical Server
```


---

# Attack Path Table

| Step | Technique | Security Weakness | Result |
|---|---|---|---|
| 1 | Initial access | Application weakness | User foothold |
| 2 | PrivEsc | Writable privileged component | Local admin |
| 3 | Credential access | Credential exposure | Server credential |
| 4 | Lateral movement | Credential reuse | Server access |
| 5 | Objective | Excessive application privilege | Sensitive system access |


---

# Root Cause

Do not report only the final technique.

For example:

```text
Domain Admin compromised
```

is an outcome.

The useful analysis is:

```text
Why could the attack path reach Domain Admin?
```

Potential root causes include:

```text
Credential reuse
Excessive delegation
Weak segmentation
Misconfigured ACL
Legacy authentication
Excessive local administration
Insufficient application control
Missing detection
```


---

# Phase 20 - Cleanup

Every assessment should maintain a cleanup inventory.

Potential artifacts include:

```text
Files
Processes
Services
Scheduled tasks
Accounts
SSH keys
Registry values
Certificates
Cloud identities
Role assignments
DNS records
Firewall changes
Test data
C2 components
Tunnels
Temporary credentials
```


---

# Cleanup Workflow

```text
Operator Logs
     |
     v
Artifact Inventory
     |
     v
Stop Active Sessions
     |
     v
Remove Persistence
     |
     v
Remove Files
     |
     v
Restore Configuration
     |
     v
Revoke Credentials
     |
     v
Verify
     |
     v
Customer Confirmation
```


---

# Tunnel Cleanup

For pivoting tools such as:

```text
Ligolo-ng
Chisel
SSH forwarding
SOCKS proxies
```

verify:

```text
Processes terminated
Interfaces removed
Routes removed
Listeners stopped
Temporary binaries removed
Firewall changes restored
Credentials removed
```


---

# Infrastructure Cleanup

At the end of the engagement:

```text
Stop assessment services
Revoke API tokens
Revoke temporary credentials
Remove DNS records
Destroy temporary servers
Delete temporary storage
Archive required logs
Remove payloads
Check cloud billing resources
Verify no infrastructure remains unintentionally active
```


---

# Phase 21 - Reporting

A red team report should explain the attack story.

Typical structure:

```text
Executive Summary

Objectives

Scope

Rules of Engagement

Methodology

Attack Narrative

Attack Paths

Technical Findings

Detection Analysis

Positive Security Controls

Recommendations

Cleanup Confirmation

Appendices
```


---

# Executive Summary

The executive summary should answer:

```text
Did the red team achieve the objective?

How?

What were the major control failures?

What worked well?

What is the business impact?

What should be fixed first?
```


---

# Attack Narrative

A useful attack narrative follows chronology.

```text
The assessment began from an external attacker position.

An exposed application provided the initial foothold.

The compromised identity had standard-user privileges.

A local configuration weakness enabled privilege escalation.

Credential material recovered from the system enabled access to
an internal server.

The internal connection was permitted by network segmentation.

The resulting access provided a path to the defined assessment
objective.
```

The narrative should connect individual technical findings.


---

# Finding Structure

A technical finding should contain:

```text
Title
Severity
Affected Assets
Description
Prerequisites
Attack Path
Validation
Evidence
Impact
Detection
Remediation
References
```


---

# Positive Findings

Red team reports should also identify controls that worked.

Examples:

```text
MFA prevented account compromise

ASR blocked the test technique

AppLocker denied execution

Network segmentation prevented lateral movement

EDR generated a high-confidence alert

SOC investigated within five minutes

Credential Guard prevented expected credential exposure
```

This helps organisations understand which investments are effective.


---

# Recommendations

Recommendations should address root causes.

Weak:

```text
Block attacker tool.
```

Better:

```text
Reduce administrative credential exposure by separating
administrative identities from workstation logons and enforcing
privileged-access workstations for tier-0 administration.
```

Tool-specific blocking alone rarely resolves the underlying attack path.


---

# Retesting

Retesting should reproduce the original attack path.

```text
Original Technique
       |
       v
Original Control Gap
       |
       v
Remediation
       |
       v
Repeat Same Validation
       |
       v
Prevented / Detected?
```


---

# Red Team Metrics

Useful measurements include:

```text
Time to initial access
Time to detection
Time to triage
Time to investigation
Time to containment
Number of attack steps detected
Number of attack steps prevented
Number of attack steps invisible
Objective achieved
Privilege obtained
Systems reached
Credential exposure
```


---

# Detection Coverage

Example:

```text
Total meaningful attack actions: 20

Prevented:       4
Detected:        8
Logged only:     5
No visibility:   3
```

This is often more informative than simply counting vulnerabilities.


---

# Operational Decision Model

For every significant action:

```text
                     Proposed Action
                           |
                           v
                      In Scope?
                     /        \
                   No          Yes
                   |            |
                  STOP          v
                         Explicitly Allowed?
                           /         \
                         No           Yes
                         |             |
                        STOP           v
                               Required for
                                Objective?
                                /      \
                              No        Yes
                              |          |
                            Avoid        v
                                   Safe Enough?
                                    /      \
                                  No        Yes
                                  |          |
                              Alternative    v
                                       Execute Minimum
                                          Necessary
                                            |
                                            v
                                      Record Evidence
                                            |
                                            v
                                       Objective Proven?
                                         /        \
                                       Yes         No
                                       |            |
                                      STOP      Reassess
```


---

# Red Team Attack Path Decision Model

```text
                     Current Access
                          |
                          v
                   Objective Reached?
                    /          \
                  Yes           No
                  |              |
                 STOP            v
                          Identify Paths
                                |
                +---------------+---------------+
                |               |               |
                v               v               v
             PrivEsc        Credentials      Discovery
                |               |               |
                +---------------+---------------+
                                |
                                v
                        Select Lowest-Risk
                          Useful Path
                                |
                                v
                            Validate
                                |
                                v
                        New Access Gained?
                           /        \
                         No          Yes
                         |            |
                         v            v
                      Reassess    Record State
                                      |
                                      v
                              Objective Reached?
```


---

# Full Red Team Checklist

## Planning

- [ ] Written authorisation obtained
- [ ] Scope confirmed
- [ ] Objectives defined
- [ ] Rules of Engagement approved
- [ ] Stop conditions defined
- [ ] Emergency contacts confirmed
- [ ] Data-handling rules confirmed
- [ ] Testing windows confirmed
- [ ] Cleanup responsibilities confirmed

## Infrastructure

- [ ] Infrastructure isolated
- [ ] Administrative access restricted
- [ ] Strong authentication configured
- [ ] MFA configured where possible
- [ ] Firewall configured
- [ ] DNS configured
- [ ] TLS configured
- [ ] Logging configured
- [ ] Time synchronised
- [ ] Infrastructure inventory maintained
- [ ] Decommission plan ready

## Reconnaissance

- [ ] Domains enumerated
- [ ] Subdomains enumerated
- [ ] DNS resolved
- [ ] Alive services identified
- [ ] Technologies identified
- [ ] Authentication portals identified
- [ ] Cloud exposure considered
- [ ] Attack surface documented

## Initial Access

- [ ] Initial access vectors prioritised
- [ ] Scope checked before exploitation
- [ ] Minimum-impact technique selected
- [ ] Foothold documented
- [ ] Detection result recorded

## Foothold

- [ ] Identity recorded
- [ ] Privilege recorded
- [ ] Host recorded
- [ ] Network configuration recorded
- [ ] Security controls identified
- [ ] Objective reviewed before proceeding

## Privilege Escalation

- [ ] Services reviewed
- [ ] Scheduled tasks or cron reviewed
- [ ] Permissions reviewed
- [ ] Credentials reviewed
- [ ] Application configuration reviewed
- [ ] Minimum necessary validation performed
- [ ] Detection result recorded

## Credential Access

- [ ] Credential access explicitly permitted
- [ ] Credential material minimised
- [ ] Credentials securely stored
- [ ] Credential scope determined
- [ ] Reuse considered
- [ ] Detection result recorded

## Active Directory

- [ ] Domain understood
- [ ] Privileged groups reviewed
- [ ] Sessions considered
- [ ] ACLs reviewed
- [ ] Delegation reviewed
- [ ] Kerberos exposure considered
- [ ] AD CS considered
- [ ] Trusts considered
- [ ] Attack paths mapped

## Lateral Movement

- [ ] Target in scope
- [ ] Credential authorised for use
- [ ] Network path understood
- [ ] Protocol selected
- [ ] Segmentation result recorded
- [ ] New host context recorded
- [ ] Detection result recorded

## Pivoting

- [ ] Pivoting permitted
- [ ] Reachable networks identified
- [ ] Excluded networks protected
- [ ] Ligolo-ng/Chisel/SSH tunnel documented if used
- [ ] Routes recorded
- [ ] Proxy configuration recorded
- [ ] Tunnel cleanup recorded

## C2

- [ ] C2 permitted
- [ ] Infrastructure documented
- [ ] Protocol documented
- [ ] Destination documented
- [ ] Administrative interface protected
- [ ] Detection result recorded

## Persistence

- [ ] Persistence required
- [ ] Persistence explicitly permitted
- [ ] Original state recorded
- [ ] Minimum-impact mechanism selected
- [ ] Persistence inventory updated
- [ ] Cleanup prepared
- [ ] Detection result recorded

## Defence Evasion

- [ ] Defender status recorded
- [ ] EICAR considered
- [ ] AMSI considered
- [ ] PowerShell language mode recorded
- [ ] AppLocker considered
- [ ] WDAC considered
- [ ] ASR considered
- [ ] LOLBins considered
- [ ] EDR visibility recorded
- [ ] Security controls left operational

## Objective

- [ ] Objective reached or blocked
- [ ] Minimum proof collected
- [ ] Sensitive data exposure minimised
- [ ] Synthetic data used where possible
- [ ] Business impact established

## Detection

- [ ] Prevented actions recorded
- [ ] Logged actions recorded
- [ ] Alerts recorded
- [ ] SOC investigations recorded
- [ ] Response times recorded
- [ ] Visibility gaps documented
- [ ] Successful controls documented

## Evidence

- [ ] Timestamps consistent
- [ ] Operator log maintained
- [ ] Commands recorded where important
- [ ] Screenshots labelled
- [ ] Attack path documented
- [ ] Credentials protected
- [ ] Evidence securely stored

## Cleanup

- [ ] Sessions stopped
- [ ] Tunnels stopped
- [ ] Routes restored
- [ ] Files removed
- [ ] Services removed
- [ ] Scheduled tasks removed
- [ ] Accounts removed
- [ ] SSH keys removed
- [ ] Persistence removed
- [ ] Cloud resources removed
- [ ] Credentials revoked
- [ ] Infrastructure decommissioned
- [ ] Cleanup independently verified

## Reporting

- [ ] Executive summary completed
- [ ] Objectives answered
- [ ] Attack narrative completed
- [ ] Attack paths documented
- [ ] Findings written
- [ ] Detection analysis included
- [ ] Positive controls included
- [ ] Root causes identified
- [ ] Recommendations prioritised
- [ ] Cleanup confirmed


---

# End-to-End Testing Model

```text
                           AUTHORISATION
                                |
                                v
                             PLANNING
                                |
                                v
                         THREAT MODELLING
                                |
                                v
                        INFRASTRUCTURE
                                |
                                v
                         RECONNAISSANCE
                                |
                                v
                          INITIAL ACCESS
                                |
                                v
                             FOOTHOLD
                                |
                                v
                     SITUATIONAL AWARENESS
                                |
                +---------------+---------------+
                |                               |
                v                               v
       PRIVILEGE ESCALATION             CREDENTIAL ACCESS
                |                               |
                +---------------+---------------+
                                |
                                v
                       INTERNAL DISCOVERY
                                |
                                v
                       LATERAL MOVEMENT
                                |
                                v
                             PIVOTING
                           IF REQUIRED
                                |
                                v
                      HIGHER-VALUE ACCESS
                                |
                +---------------+---------------+
                |               |               |
                v               v               v
          PERSISTENCE          C2        DEFENCE EVASION
          IF REQUIRED      IF REQUIRED      TESTING
                |               |               |
                +---------------+---------------+
                                |
                                v
                         TARGET OBJECTIVE
                                |
                                v
                      DETECTION VALIDATION
                                |
                                v
                        ATTACK PATH REVIEW
                                |
                                v
                             CLEANUP
                                |
                                v
                            REPORTING
                                |
                                v
                             RETEST
```


---

# Core Principle

The methodology can ultimately be reduced to:

```text
Know the objective.

Understand the current access.

Identify the shortest meaningful attack path.

Validate one security boundary at a time.

Collect evidence.

Measure defensive visibility.

Stop when the objective is proven.

Remove everything introduced during testing.

Explain the attack path and its root causes.
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
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)
- [Active Directory](../active-directory/)
- [BloodHound](../active-directory/bloodhound.md)
- [NetExec](../active-directory/netexec.md)
- [Impacket](../active-directory/impacket.md)


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [BloodHound](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }
- [Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    This methodology is intended for authorised red team, penetration testing, purple team, and security validation engagements. Every action must remain within the agreed scope and Rules of Engagement. Use the minimum-impact technique necessary to demonstrate each security boundary, protect credentials and customer data, stop when an objective has been sufficiently demonstrated, maintain an artifact inventory throughout the engagement, and verify complete cleanup before closing the assessment.
