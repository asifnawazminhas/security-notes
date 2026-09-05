---
title: Red Team Reporting
description: Practical reporting methodology for authorised red team assessments, covering executive reporting, attack paths, findings, evidence, MITRE ATT&CK mapping, detection and response results, severity, remediation, timelines, metrics, cleanup, retesting, and technical appendices.
---

# Red Team Reporting

Red team reporting converts assessment activity into information that an organisation can use to reduce risk.

A useful red team report should explain:

```text
What happened?

How did access begin?

Which security boundaries were crossed?

Which systems and identities were affected?

What attack paths were demonstrated?

Which controls prevented activity?

Which controls detected activity?

Which activity remained undetected?

How did the SOC respond?

What was the realistic impact?

What should be fixed first?

How can the organisation verify the improvements?
```

The objective is not to produce the largest possible collection of screenshots or commands.

The objective is to communicate the security story clearly.

!!! warning "Authorised assessments only"
    Reports should contain only information obtained during the authorised assessment. Protect credentials, customer data, internal architecture, screenshots, payload information, and other sensitive evidence according to the Rules of Engagement and applicable data-handling requirements.


---

# Reporting Model

A red team report normally serves several audiences.

```text
                    RED TEAM REPORT
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      MANAGEMENT       SECURITY TEAM     TECHNICAL TEAM
          |                |                |
          v                v                v
     Business Risk     Attack Paths       Evidence
     Key Outcomes      Detection Gaps     Technical Detail
     Priorities        SOC Response       Remediation
```

Each audience needs different information.


---

# Core Reporting Principle

Do not make the reader reconstruct the engagement from raw evidence.

Instead:

```text
Evidence
   |
   v
Observation
   |
   v
Attack Path
   |
   v
Security Impact
   |
   v
Root Cause
   |
   v
Recommendation
```


---

# Suggested Report Structure

A practical structure is:

```text
1. Executive Summary

2. Engagement Overview

3. Scope

4. Objectives

5. Rules of Engagement

6. Assessment Methodology

7. Attack Narrative

8. Attack Path Summary

9. Key Findings

10. Detection and Response Assessment

11. MITRE ATT&CK Mapping

12. Recommendations

13. Strategic Improvement Roadmap

14. Retest Results

15. Cleanup Confirmation

16. Technical Findings

17. Evidence Appendix

18. Technical Appendix
```


---

# Executive Summary

The executive summary should be understandable without requiring deep technical knowledge.

Focus on:

```text
Overall security outcome
Business impact
Attack path
Critical weaknesses
Detection effectiveness
Response effectiveness
Priority improvements
```

Avoid filling the executive summary with:

```text
Tool names
Long commands
Payload details
Raw logs
Excessive ATT&CK identifiers
Low-level technical terminology
```


---

# Executive Summary Example

```text
The assessment demonstrated that an attacker with access to a
standard user account could progress through multiple security
boundaries and obtain access to systems containing elevated
administrative privileges.

The attack path was primarily enabled by excessive credential
reuse, insufficient network segmentation, and weaknesses in
administrative access controls.

Endpoint security controls detected several stages of the
assessment, including suspicious process execution and remote
administration activity. However, some authentication and lateral
movement activity did not generate actionable alerts.

The highest-priority improvements are to reduce privileged
credential exposure, strengthen administrative tiering, restrict
east-west administrative protocols, and improve correlation of
authentication and endpoint telemetry.
```


---

# Management Summary

A shorter management summary can follow:

```text
Initial Access
     |
     v
Standard User
     |
     v
Credential Exposure
     |
     v
Internal Movement
     |
     v
Privileged System
     |
     v
Business Impact
```

Management should understand the security boundaries that failed, not every command used to cross them.


---

# Engagement Overview

Document:

```text
Customer
Engagement type
Assessment dates
Testing team
Primary contact
Assessment model
Scope
Objectives
Assumptions
Limitations
```


---

# Engagement Type

Clearly identify whether the work was:

```text
Red Team Assessment
Purple Team Assessment
Assumed Breach
Internal Red Team
External Red Team
Adversary Simulation
Detection Validation
Penetration Test
```

Do not use these terms interchangeably.


---

# Assessment Dates

Record:

```text
Testing start
Testing end
Reporting period
Retest date
```

Use a consistent timezone.


---

# Objectives

Examples:

```text
Determine whether an external attacker could obtain internal access.

Determine whether a compromised standard user could reach
privileged systems.

Evaluate whether security controls detect credential access and
lateral movement.

Evaluate whether the SOC can reconstruct the attack path.

Identify opportunities to improve prevention, detection, and
response.
```


---

# Scope

Document the authorised scope.

Examples:

```text
Domains
IP ranges
Applications
Cloud tenants
User accounts
Workstations
Servers
Active Directory
Email
Physical locations
Wireless networks
```


---

# Exclusions

Also document exclusions.

Example:

```text
Production denial-of-service testing

Third-party infrastructure

Destructive testing

Unapproved social engineering

Unapproved credential collection

Data modification

Persistence beyond the agreed period
```


---

# Rules of Engagement

Summarise relevant operational restrictions.

Examples:

```text
Testing window
Permitted techniques
Prohibited techniques
Authentication limits
Social-engineering rules
Data-access limits
Persistence limits
Stop conditions
Emergency contacts
```


---

# Limitations

Be explicit about limitations.

Examples:

```text
Certain production systems were excluded.

Testing was limited to standard-user privileges.

Password spraying was not performed.

Social engineering was excluded.

No destructive actions were performed.

Some detection validation was performed collaboratively with the
SOC and therefore should not be interpreted as blind-response
testing.
```


---

# Assumptions

Examples:

```text
Customer-provided credentials were assumed to represent a
compromised standard user.

Assessment infrastructure was assumed to be external to the
customer network.

Customer-provided asset lists were assumed to be accurate.
```


---

# Methodology

Explain the assessment process.

Example:

```text
Planning
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
Discovery
   |
   v
Privilege Escalation
   |
   v
Credential Access
   |
   v
Lateral Movement
   |
   v
Objective
   |
   v
Detection Validation
   |
   v
Cleanup
```


---

# Methodology Should Match the Engagement

Do not claim:

```text
Full red team simulation
```

if the engagement actually consisted of:

```text
Known credentials
Limited internal testing
Predefined systems
Collaborative detection validation
```

Describe what was actually tested.


---

# Attack Narrative

The attack narrative is one of the most important parts of a red team report.

It explains the assessment as a connected sequence.

Example:

```text
External Exposure
       |
       v
Initial Access
       |
       v
Standard User
       |
       v
Credential Discovery
       |
       v
Internal Server
       |
       v
Administrative Context
       |
       v
Sensitive Resource
```


---

# Narrative vs Findings

Individual findings may look like:

```text
F01 - Credential Exposure

F02 - Weak Network Segmentation

F03 - Excessive Administrative Rights

F04 - Missing Lateral Movement Detection
```

But the attack narrative explains:

```text
F01
 |
 v
enabled
 |
 v
F02
 |
 v
enabled
 |
 v
F03
 |
 v
resulting in
 |
 v
Objective
```

This relationship is critical.


---

# Attack Path Summary

A concise attack-path table is useful.

| Stage | Source | Target | Security Boundary | Result |
|---|---|---|---|---|
| Initial Access | External | WS01 | Perimeter | Access obtained |
| Credential Access | WS01 | Local secrets | Credential boundary | Credential identified |
| Lateral Movement | WS01 | SRV01 | Network boundary | Remote access obtained |
| Privilege Escalation | SRV01 | Admin context | Privilege boundary | Elevated access |
| Objective | SRV01 | Sensitive service | Business boundary | Access demonstrated |


---

# Attack Path Diagram

Example:

```text
                      INTERNET
                          |
                          v
                    Initial Access
                          |
                          v
                    +-----------+
                    |   WS01    |
                    | User: A   |
                    +-----------+
                          |
                    Credential
                      Exposure
                          |
                          v
                    +-----------+
                    |   SRV01   |
                    | Service   |
                    +-----------+
                          |
                   Privilege Path
                          |
                          v
                    +-----------+
                    |   ADM01   |
                    | Elevated  |
                    +-----------+
                          |
                          v
                     OBJECTIVE
```


---

# Security Boundary Model

A useful report should identify the boundaries crossed.

Examples:

```text
Internet -> Internal Network

Standard User -> Local Administrator

Workstation -> Server

User Network -> Management Network

Application User -> Database

On-Premises -> Cloud

Standard Account -> Privileged Account
```


---

# Why Security Boundaries Matter

A remote service being reachable is not necessarily a vulnerability.

The meaningful question is:

```text
Did the attacker cross a security boundary that should have
prevented or restricted the attack path?
```


---

# Attack Path Evidence

For each major transition record:

```text
Source
Target
Identity
Privilege
Technique
Timestamp
Evidence
Security control
Result
```


---

# Attack Path Record

Example:

```text
Transition:
WS01 -> SRV01

Identity:
CORP\test-user

Technique:
Approved remote administration

Expected Control:
Network segmentation and access control

Observed:
TCP/445 reachable and authentication accepted.

Result:
Security boundary crossed.
```


---

# Findings

Each finding should describe a specific weakness or control gap.

Recommended structure:

```text
Title

Severity

Description

Observation

Evidence

Attack Path

Impact

Likelihood

Root Cause

MITRE ATT&CK

Detection

Recommendation

Validation

References
```


---

# Finding Title

A title should describe the weakness.

Good:

```text
Privileged Credentials Accessible to Standard Users
```

Better than:

```text
Mimikatz
```

Good:

```text
Workstation-to-Server Administrative Traffic Is Insufficiently Restricted
```

Better than:

```text
SMB Lateral Movement
```


---

# Avoid Tool-Based Finding Titles

Avoid titles such as:

```text
BloodHound Finding

NetExec Vulnerability

PowerShell Issue

Impacket Exploit
```

The tool is not the vulnerability.


---

# Finding Description

Explain the security condition.

Example:

```text
Standard-user systems were able to initiate administrative
protocol connections directly to server systems.

This increases the ability of an attacker who compromises a
workstation to attempt credential reuse and lateral movement
against internal servers.
```


---

# Observation

Describe what happened during the assessment.

Example:

```text
From workstation WS01, the assessment team confirmed TCP
connectivity to the SMB service on SRV01.

The customer-provided assessment identity was accepted by the
remote system and provided access beyond the original workstation.
```


---

# Evidence

Evidence should demonstrate the observation.

Possible evidence:

```text
Command output
Screenshot
Event log
SIEM event
EDR process tree
Authentication record
HTTP request/response
Configuration
Network capture
Cloud audit event
```


---

# Evidence Should Be Minimal

Do not include ten screenshots when one demonstrates the issue.

Prefer:

```text
Evidence
   |
   v
Clear Proof
```

instead of:

```text
Evidence
   |
   v
Large Raw Data Dump
```


---

# Evidence Identifier

Use identifiers:

```text
EVID-001
EVID-002
EVID-003
```

Example:

```text
EVID-014 - Successful authentication from WS01 to SRV01
```


---

# Evidence Metadata

Record:

```text
Evidence ID
Finding ID
Timestamp
Host
User
Operator
Source
Target
Description
File
Hash where required
```


---

# Evidence Naming

Example:

```text
20260905-1042-F03-WS01-SRV01-authentication.png
```


---

# Screenshot Caption

Example:

```text
Figure 4 - Successful authorised authentication from WS01 to SRV01
using the assessment identity.
```

Captions should explain what the reader should notice.


---

# Sensitive Evidence

Do not expose reusable secrets in the report.

Redact:

```text
Passwords
API tokens
Session cookies
Private keys
Reusable hashes
Authentication tokens
Personal data
```

Retain original evidence securely if required.


---

# Command Evidence

Commands can be useful when they explain reproducibility.

Example:

```powershell
Test-NetConnection SRV01 -Port 445
```

Do not turn the main report into a command transcript.


---

# Output Evidence

Show only relevant output.

Example:

```text
ComputerName     : SRV01
RemotePort       : 445
TcpTestSucceeded : True
```

This demonstrates reachability without unnecessary output.


---

# Impact

Explain what the weakness enables.

Weak:

```text
An attacker could use this.
```

Better:

```text
An attacker who compromises a standard workstation may be able to
reuse valid credentials against internal server systems, increasing
the likelihood that a single endpoint compromise progresses into a
broader internal compromise.
```


---

# Impact Categories

Consider:

```text
Confidentiality
Integrity
Availability
Privilege
Identity
Network reach
Business process
Detection capability
Recovery capability
```


---

# Do Not Overstate Impact

If testing demonstrated:

```text
Remote service reachable
```

do not automatically report:

```text
Full domain compromise possible.
```

Use evidence-based language.


---

# Evidence Strength

Useful classifications:

```text
Candidate

Likely

Confirmed
```


---

# Candidate

Example:

```text
A potentially exploitable configuration was identified but was not
validated.
```


---

# Likely

Example:

```text
The prerequisite conditions appear to be present, but exploitation
was not performed because of engagement restrictions.
```


---

# Confirmed

Example:

```text
The assessment team successfully crossed the security boundary
using the authorised validation procedure.
```


---

# Root Cause

Root cause describes why the weakness exists.

Examples:

```text
Credential reuse

Excessive privilege

Missing segmentation

Weak application control

Inadequate secret management

Insufficient authentication policy

Legacy protocol dependency

Missing logging

Missing detection logic

Configuration drift

Inadequate administrative tiering
```


---

# Root Cause vs Symptom

Example symptom:

```text
Remote administration succeeded.
```

Potential root cause:

```text
Administrative access from user workstations is not restricted.
```

Fixing the root cause is more valuable.


---

# Severity

Severity should represent demonstrated risk.

Consider:

```text
Impact

Likelihood

Privilege obtained

Asset criticality

Attack complexity

Prerequisites

User interaction

Security boundary crossed

Detection capability

Compensating controls
```


---

# Example Severity Model

```text
Critical
Direct path to highly privileged or business-critical compromise
with limited prerequisites.

High
Significant security boundary can be crossed and meaningful
privilege or sensitive access obtained.

Medium
Useful attacker capability exists but meaningful prerequisites,
limitations, or compensating controls apply.

Low
Limited security impact or significant constraints.

Informational
Observation or improvement opportunity without demonstrated
security impact.
```


---

# Severity Is Not Technique Severity

Do not assign severity because:

```text
Pass-the-Hash = High
```

or:

```text
PowerShell = Medium
```

Severity depends on the actual environment and impact.


---

# Attack Path Severity

An individual weakness may be moderate alone but important in a chain.

Example:

```text
Weakness A - Medium
       |
       v
Weakness B - Medium
       |
       v
Weakness C - Medium
       |
       v
Domain-Level Impact
```

The report should highlight this chain.


---

# Likelihood

Consider:

```text
Required access
Required privilege
Required credentials
Network reachability
User interaction
Exploit reliability
Existing security controls
Attacker knowledge
Repeatability
```


---

# Recommendation

Recommendations should address the root cause.

Weak:

```text
Block PowerShell.
```

Better:

```text
Restrict unnecessary PowerShell capabilities for standard users,
enforce application-control policy, enable appropriate PowerShell
logging, and ensure endpoint detections cover suspicious
interpreter behaviour.
```


---

# Recommendation Layers

Useful structure:

```text
Immediate
   |
   v
Tactical
   |
   v
Strategic
```


---

# Immediate Recommendation

Example:

```text
Rotate the exposed credential and terminate active sessions.
```


---

# Tactical Recommendation

Example:

```text
Remove the credential from the affected configuration and migrate
the application to an approved secret-management mechanism.
```


---

# Strategic Recommendation

Example:

```text
Implement centralised secret management and automated secret
scanning across repositories and deployment pipelines.
```


---

# Recommendation Ownership

Where practical, associate recommendations with responsible teams.

Example:

| Recommendation | Owner |
|---|---|
| Restrict SMB between workstation and server networks | Network Security |
| Deploy LAPS | Endpoint Engineering |
| Improve 4624/4648 correlation | Detection Engineering |
| Rotate service account | Identity Team |


---

# Recommendation Priority

Example:

```text
P0 - Emergency

P1 - Immediate

P2 - Near Term

P3 - Planned Improvement
```


---

# Remediation Roadmap

Example:

| Priority | Improvement | Target |
|---|---|---|
| P1 | Rotate exposed credentials | Immediate |
| P1 | Restrict workstation-to-server admin protocols | 30 days |
| P2 | Deploy LAPS broadly | 60 days |
| P2 | Improve lateral movement detections | 60 days |
| P3 | Implement privileged access workstations | Strategic |


---

# Prevention, Detection, Response

For each important attack path, consider all three.

```text
                     Attack Technique
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Prevention       Detection         Response
```


---

# Prevention Reporting

Document:

```text
Control expected
Control observed
Whether activity was prevented
Control weakness
Recommendation
```


---

# Detection Reporting

Document:

```text
Telemetry expected
Telemetry observed
EDR event
SIEM event
Detection rule
Alert
Severity
Time to detect
```


---

# Response Reporting

Document:

```text
Alert received
Analyst acknowledgement
Investigation
Escalation
Containment
Recovery
```


---

# Detection Result Table

| Technique | Prevented | Telemetry | Alert | SOC Response | Result |
|---|---:|---:|---:|---:|---|
| Controlled PowerShell | No | Yes | Yes | Yes | Effective |
| Scheduled Task | No | Yes | No | No | Detection gap |
| Lateral Movement | No | Yes | Yes | Yes | Effective |
| HTTPS C2 Simulation | No | Partial | No | No | Visibility gap |


---

# Positive Security Results

A red team report should also document controls that worked.

Examples:

```text
Microsoft Defender blocked the EICAR test artifact.

AppLocker prevented execution from the tested user-writable path.

The SOC detected remote authentication within two minutes.

Network segmentation prevented direct RDP access.

MFA prevented authentication using the compromised password.
```

This gives a balanced assessment.


---

# Detection Gap Categories

Useful categories:

```text
Telemetry Gap

Collection Gap

Parsing Gap

Detection Gap

Correlation Gap

Alerting Gap

Triage Gap

Response Gap
```


---

# Detection Gap Example

```text
The endpoint generated the expected process telemetry and the event
was successfully forwarded to the SIEM.

No detection rule generated an alert.

This represents a detection-logic gap rather than a telemetry gap.
```


---

# Telemetry Gap Example

```text
The controlled activity was successfully executed, but the
required endpoint telemetry was not available locally or in the
central security platform.
```


---

# Collection Gap Example

```text
The expected event was present on the endpoint but was not present
in the SIEM during the assessment window.
```


---

# SOC Response

Record:

```text
Detection time
Acknowledgement time
Triage time
Investigation time
Containment time
Escalation path
Correctness of conclusion
```


---

# Timeline

Maintain a timeline of important events.

Example:

| Time | Stage | Source | Target | Result |
|---|---|---|---|---|
| 09:05 | Initial Access | External | WS01 | Access |
| 09:32 | Discovery | WS01 | AD | Successful |
| 10:04 | Credential Access | WS01 | Local | Credential identified |
| 10:42 | Lateral Movement | WS01 | SRV01 | Successful |
| 10:44 | Detection | EDR | SOC | Alert |
| 10:47 | SOC | Analyst | Alert | Investigating |
| 11:02 | Objective | SRV01 | Resource | Demonstrated |


---

# Attack Timeline Diagram

```text
09:05              10:04              10:42              11:02
  |                   |                  |                  |
  v                   v                  v                  v
Initial            Credential          Lateral          Objective
Access              Access             Movement
  |                   |                  |
  +-------------------+------------------+
                      |
                      v
                 SOC Detection
                    10:44
```


---

# Time to Detect

```text
TTD = Detection Time - Activity Time
```


---

# Time to Respond

Define the response point clearly.

Example:

```text
TTR = Containment Time - Detection Time
```


---

# Metrics

Useful metrics may include:

```text
Objectives achieved
Security boundaries crossed
Critical attack paths
Findings by severity
Techniques tested
Techniques prevented
Techniques detected
Techniques not detected
SOC investigations
Mean time to detect
Mean time to respond
Retests passed
```


---

# Example Metrics

```text
Assessment objectives:        5

Objectives achieved:          4

Security boundaries crossed:  3

Techniques validated:         18

Prevented:                    5

Detected:                    11

Logged but not alerted:       4

No useful visibility:         3

SOC investigations:           9
```


---

# Metrics Need Context

Avoid:

```text
EDR detected 75 percent of attacks.
```

unless the methodology supports that conclusion.

Prefer:

```text
Nine of the twelve selected techniques for which an EDR alert was
expected generated the anticipated alert during the assessment.
```


---

# MITRE ATT&CK Mapping

Map observed behaviour to ATT&CK where useful.

Example:

| Stage | ATT&CK Tactic | Technique |
|---|---|---|
| Execution | Execution | PowerShell |
| Credential Access | Credential Access | Unsecured Credentials |
| Lateral Movement | Lateral Movement | Remote Services |
| Persistence | Persistence | Scheduled Task/Job |
| C2 | Command and Control | Application Layer Protocol |


---

# ATT&CK Mapping Purpose

ATT&CK can help:

```text
Standardise terminology

Map attack paths

Map detections

Identify coverage gaps

Compare exercises

Plan retesting
```

ATT&CK should support the report, not dominate it.


---

# Do Not Over-Map

One command may theoretically map to several techniques.

Only include mappings that meaningfully describe the tested behaviour.


---

# ATT&CK Coverage

A useful model:

```text
Technique Tested
      |
      v
Telemetry?
 /        \
No         Yes
|           |
Gap         v
        Detection?
         /      \
       No        Yes
       |          |
      Gap         v
              Response?
               /     \
             No       Yes
             |         |
            Gap      Validated
```


---

# ATT&CK Coverage Table

| Technique | Tested | Telemetry | Detection | Response |
|---|---:|---:|---:|---:|
| T1059.001 | Yes | Yes | Yes | Yes |
| T1021.002 | Yes | Yes | No | No |
| T1053 | Yes | Yes | Yes | No |


---

# ATT&CK Heatmaps

If an ATT&CK heatmap is included, explain what the colours represent.

Example:

```text
Green  = Tested and detected

Yellow = Tested with partial visibility

Red    = Tested without expected detection

Grey   = Not tested
```

Do not present untested techniques as validated coverage.


---

# Technical Findings

Technical findings should contain enough detail for remediation and retesting.

Recommended format:

```text
Finding ID

Title

Severity

Affected Systems

Description

Prerequisites

Observation

Evidence

Impact

Attack Path

Detection

Root Cause

Recommendation

Validation Procedure

References
```


---

# Finding ID

Use consistent identifiers.

Example:

```text
RT-01
RT-02
RT-03
```

or:

```text
FIND-001
FIND-002
```


---

# Affected Systems

List:

```text
Hostname
IP
Application
Domain
Cloud resource
Identity
```

Do not write:

```text
All systems
```

unless that was actually established.


---

# Prerequisites

Document what an attacker needs.

Examples:

```text
Internal network access

Standard domain account

Local workstation access

Compromised service account

Access to specific subnet
```


---

# Reproduction

For findings where reproduction is useful, document a minimal validation procedure.

Prefer:

```text
1. Authenticate using an authorised test identity.

2. Confirm the target service is reachable.

3. Perform the minimum action required to demonstrate the boundary.

4. Record the result.

5. Stop.

6. Cleanup.
```

Avoid unnecessary destructive or intrusive reproduction steps.


---

# Validation Procedure

The recommendation should be testable.

Example:

```text
After implementing network restrictions, repeat the TCP
connectivity test from a standard workstation.

Administrative SMB and WinRM access to server networks should no
longer be available unless explicitly authorised.
```


---

# Retesting

A retest should answer:

```text
Was the original weakness fixed?

Can the original attack path still be completed?

Did the remediation introduce another path?

Does detection now work?

Is the control consistently enforced?
```


---

# Retest Status

Use:

```text
Resolved

Partially Resolved

Not Resolved

Not Retested

Risk Accepted
```


---

# Retest Table

| Finding | Original | Retest | Status |
|---|---|---|---|
| RT-01 | High | Blocked | Resolved |
| RT-02 | High | Partial restriction | Partially Resolved |
| RT-03 | Medium | Alert generated | Resolved |


---

# Retest Evidence

Preserve:

```text
Original evidence

Remediation description

Retest date

Retest action

Retest evidence

Final result
```


---

# Attack Path Retesting

Do not only retest individual findings.

Retest the complete path where appropriate.

```text
Original:

A -> B -> C -> D


After remediation:

A -> B -> X
```

This demonstrates whether the attack chain was actually broken.


---

# Strategic Recommendations

Individual findings often share root causes.

Group them into themes.

Examples:

```text
Identity Security

Privileged Access

Network Segmentation

Endpoint Hardening

Application Control

Credential Management

Detection Engineering

Security Monitoring

SOC Response

Cloud Security
```


---

# Strategic Roadmap

Example:

```text
0-30 Days
    |
    +--> Rotate exposed credentials
    +--> Restrict high-risk remote administration
    +--> Fix critical detection gaps

30-90 Days
    |
    +--> Deploy LAPS
    +--> Improve segmentation
    +--> Improve central logging
    +--> Expand identity detections

90+ Days
    |
    +--> Administrative tiering
    +--> Privileged access workstations
    +--> Continuous ATT&CK validation
    +--> Purple team programme
```


---

# Prioritise Attack-Path Breakers

A useful question is:

```text
Which remediation breaks the largest number of demonstrated
attack paths?
```

Example:

```text
                 Credential Reuse
                       |
          +------------+------------+
          |            |            |
          v            v            v
        SRV01        SRV02        SRV03
```

Eliminating credential reuse may remove multiple paths at once.


---

# Compensating Controls

If immediate remediation is difficult, document compensating controls.

Examples:

```text
Network restriction
Additional monitoring
MFA
Temporary account restrictions
Increased alerting
Manual review
EDR policy
Firewall rule
```


---

# Risk Acceptance

If a risk is accepted, record:

```text
Finding
Risk owner
Reason
Compensating controls
Review date
Approval
```


---

# Cleanup Reporting

The report should confirm introduced artifacts were addressed.

Possible artifacts:

```text
Payloads
Scripts
Accounts
Services
Scheduled tasks
Registry modifications
SSH keys
Certificates
Routes
Tunnels
C2 sessions
Cloud resources
DNS records
Firewall rules
Temporary files
```


---

# Cleanup Statement

Example:

```text
All known assessment artifacts introduced by the red team were
removed at the conclusion of testing.

Temporary infrastructure and assessment credentials were revoked
or decommissioned according to the engagement cleanup inventory.
```


---

# Cleanup Exceptions

If something remains:

```text
Artifact:
RT monitoring account

Reason:
Customer requested retention for retesting.

Owner:
Customer Security Team

Action:
Customer assumes ownership.
```


---

# Evidence Appendix

A technical evidence appendix can contain:

```text
Evidence ID

Finding

Timestamp

Host

User

Description

Screenshot/File

Hash

Notes
```


---

# Evidence Manifest

Example:

| ID | Finding | File | SHA-256 |
|---|---|---|---|
| EVID-001 | RT-01 | `rt01-auth.png` | `...` |
| EVID-002 | RT-02 | `rt02-policy.txt` | `...` |


---

# Technical Appendix

Potential contents:

```text
Assessment IP addresses

Assessment domains

Test accounts

Payload hashes

ATT&CK mappings

Timeline

Tool versions

Infrastructure inventory

Detection test IDs

Evidence manifest

Cleanup inventory
```


---

# Tool Inventory

Document tools when relevant for reproducibility.

Example:

| Tool | Purpose |
|---|---|
| BloodHound | Attack-path analysis |
| NetExec | Authorised remote administration validation |
| Impacket | Protocol testing |
| Ligolo-ng | Approved network pivoting |
| Chisel | Approved tunnelling |
| Nmap | Network discovery |


---

# Tool Versions

Versions may matter when:

```text
Behaviour differs between releases

Output format changes

A vulnerability is version-specific

Reproduction requires the same environment
```


---

# Infrastructure Indicators

At the end of an engagement, defenders may benefit from receiving:

```text
Assessment source IPs
Assessment domains
Payload hashes
Test accounts
Test hostnames
Known timestamps
```


---

# Deconfliction Appendix

Example:

```text
Assessment IPs:

203.0.113.10
203.0.113.20


Assessment Domains:

edge.example.test
files.example.test


Assessment Identities:

CORP\rt-user01
CORP\rt-user02
```

Use the actual authorised indicators in the customer report.


---

# Detection Appendix

For each detection test:

```text
Test ID
ATT&CK Technique
Host
User
Time
Expected Telemetry
Observed Telemetry
Alert
SOC Action
Result
```


---

# Detection Test Example

```text
Test ID:
DV-004

Technique:
Remote Services

Source:
WS01

Target:
SRV01

Expected:
Authentication + endpoint + network telemetry

Observed:
Authentication and endpoint telemetry

Alert:
Yes

SOC:
Investigated

Result:
Pass
```


---

# Finding Summary Table

Example:

| ID | Finding | Severity | Attack Path | Status |
|---|---|---|---|---|
| RT-01 | Privileged credential exposure | High | AP-01 | Open |
| RT-02 | Weak east-west segmentation | High | AP-01 | Open |
| RT-03 | Missing lateral movement alert | Medium | AP-01 | Open |
| RT-04 | Excessive service-account privilege | High | AP-02 | Open |


---

# Attack Path IDs

Assign identifiers:

```text
AP-01
AP-02
AP-03
```

This makes it easier to connect:

```text
Finding
   |
   v
Attack Path
   |
   v
Objective
```


---

# Attack Path Record

Example:

```text
AP-01

Objective:
Reach privileged server environment.

Entry:
Compromised standard user workstation.

Path:
WS01 -> Credential -> SRV01 -> Administrative Context

Findings:
RT-01
RT-02
RT-03

Detection:
Partial

Outcome:
Objective achieved.
```


---

# Objective Status

Use clear statuses.

```text
Achieved

Partially Achieved

Not Achieved

Not Tested
```


---

# Objective Table

| Objective | Result | Detection | Notes |
|---|---|---|---|
| Obtain internal foothold | Achieved | Yes | Detected after execution |
| Reach server environment | Achieved | Partial | Authentication detected |
| Obtain privileged access | Achieved | No | Detection gap |
| Access critical data | Not Tested | N/A | Proof stopped before data access |


---

# Proof Without Data Collection

Sometimes the objective can be demonstrated without accessing real sensitive data.

Example:

```text
Instead of downloading sensitive records:

Demonstrate access to the containing system or directory.

Record permissions.

Use a customer-provided synthetic marker.

Stop.
```

This reduces customer risk.


---

# Synthetic Proof

Example:

```text
C:\RedTeamValidation\objective.txt
```

or:

```text
/opt/redteam-validation/objective.txt
```

The customer can pre-position a harmless marker specifically for the assessment.


---

# Report Language

Use evidence-based language.

Prefer:

```text
The assessment demonstrated...
```

```text
The tested configuration allowed...
```

```text
The assessment team confirmed...
```

```text
The available evidence indicates...
```

```text
The technique was not validated because...
```


---

# Avoid Absolute Claims

Avoid:

```text
This can never be detected.
```

```text
The organisation has no security.
```

```text
All servers are vulnerable.
```

```text
EDR can be bypassed.
```

unless the evidence genuinely supports the precise claim, which is uncommon.


---

# Accurate Control Language

Distinguish:

```text
Allowed

Blocked

Logged

Detected

Alerted

Investigated

Contained
```

These are not equivalent.


---

# Example

Do not write:

```text
Defender failed.
```

when the evidence shows:

```text
The activity was allowed, but Defender generated a behavioural
alert that was visible in the security platform.
```

That is a detection success, not a complete failure.


---

# Another Example

Do not write:

```text
AppLocker bypassed.
```

when:

```text
The tested binary was allowed because the applicable AppLocker
collection did not contain an enforced rule restricting that path.
```

Report the actual policy condition.


---

# Screenshots

Screenshots should:

```text
Show relevant evidence

Be readable

Have captions

Avoid unnecessary customer data

Avoid exposed credentials

Show sufficient context

Match the narrative
```


---

# Screenshot Naming

Example:

```text
Figure 1 - Initial access validation

Figure 2 - Credential exposure

Figure 3 - Lateral movement to SRV01

Figure 4 - EDR detection

Figure 5 - SOC investigation
```


---

# Figure References

Reference figures from the text.

Example:

```text
As shown in Figure 3, the assessment identity successfully
authenticated to SRV01 from WS01.
```


---

# Tables

Tables are useful for:

```text
Findings
Attack paths
Objectives
Detection results
ATT&CK coverage
Affected assets
Recommendations
Retests
Timelines
```


---

# Avoid Giant Raw Tables

A table with hundreds of rows rarely helps management.

Put large technical inventories in an appendix or separate evidence package.


---

# Redaction

When redacting:

```text
Preserve enough information to understand the evidence.

Remove only information that does not need to be distributed.
```

Examples:

```text
Password: [REDACTED]

Token: [REDACTED]

User: CORP\test-user

Internal IP: 10.10.x.x
```

Whether IP addresses or hostnames require redaction depends on report handling requirements.


---

# Report Versioning

Example:

```text
v0.1 - Internal Draft

v0.2 - Technical Review

v0.9 - Customer Draft

v1.0 - Final

v1.1 - Retest
```


---

# Version Table

| Version | Date | Author | Description |
|---|---|---|---|
| 0.1 | 2026-09-05 | Red Team | Initial draft |
| 0.9 | 2026-09-10 | Red Team | Customer draft |
| 1.0 | 2026-09-15 | Red Team | Final |
| 1.1 | 2026-10-20 | Red Team | Retest |


---

# Peer Review

Before delivery, another reviewer should verify:

```text
Evidence supports claims

Severity is justified

Commands are accurate

Affected systems are correct

Attack paths are understandable

Credentials are redacted

Screenshots are safe

Recommendations address root causes

ATT&CK mappings are reasonable

Scope statements are correct
```


---

# Technical Quality Review

Check:

```text
Can another tester understand what happened?

Can the customer reproduce the finding safely?

Can the customer verify remediation?

Are prerequisites clear?

Are limitations documented?
```


---

# Management Quality Review

Check:

```text
Can a non-technical reader understand the risk?

Are priorities clear?

Is the attack path understandable?

Is business impact explained?

Are strategic improvements clear?
```


---

# Security Review

Before sending:

```text
Search report for passwords

Search for API tokens

Search for private keys

Review screenshots

Review document metadata

Review hidden comments

Review revision history

Verify recipient list
```


---

# Report Delivery

Use the approved delivery mechanism.

Examples:

```text
Customer secure portal

Encrypted file transfer

Approved document platform

Encrypted email where authorised
```

Avoid uncontrolled public file-sharing services.


---

# Report Retention

Document:

```text
Storage location

Access permissions

Retention period

Deletion date

Backup policy
```


---

# Report Template

A reusable finding template:

```markdown
## RT-XX - Finding Title

**Severity:** High

**Affected systems:**

- HOST01
- HOST02

### Description

Describe the security weakness.

### Observation

Describe what was observed during the authorised assessment.

### Prerequisites

Describe the access required.

### Evidence

Provide minimal evidence demonstrating the issue.

### Attack Path

Explain how this weakness contributes to the demonstrated attack
path.

### Impact

Explain the realistic security impact.

### Detection

Describe whether the activity was logged, detected, alerted on, and
investigated.

### Root Cause

Explain the underlying security condition.

### Recommendation

Provide immediate, tactical, and strategic improvements where
appropriate.

### Validation

Explain how the organisation can safely confirm the remediation.

### MITRE ATT&CK

Map relevant observed behaviour.

### References

Provide authoritative references.
```


---

# Attack Path Template

```markdown
## AP-XX - Attack Path Name

### Objective

Describe the attacker objective.

### Starting Position

Describe the initial access or assumed-breach condition.

### Path

START
  |
  v
STEP 1
  |
  v
STEP 2
  |
  v
OBJECTIVE

### Findings

- RT-01
- RT-02
- RT-03

### Security Boundaries Crossed

Describe the boundaries.

### Detection

Describe which stages were detected.

### Outcome

Achieved / Partially Achieved / Not Achieved

### Recommendations

Describe the controls that would break the path.
```


---

# Detection Finding Template

```markdown
## DV-XX - Detection Gap

### Technique

ATT&CK technique or tested behaviour.

### Expected Telemetry

Describe what should have been generated.

### Observed Telemetry

Describe what was actually available.

### Detection

Describe whether detection logic matched.

### Alert

Describe whether an alert was generated.

### SOC Response

Describe the analyst response.

### Gap

Telemetry / Collection / Parsing / Detection / Correlation /
Alerting / Triage / Response.

### Recommendation

Describe the required improvement.

### Retest

Repeat the controlled test after remediation.
```


---

# Retest Template

```markdown
## Retest - RT-XX

### Original Finding

Finding title.

### Original Severity

High

### Remediation

Describe the customer's remediation.

### Retest Date

YYYY-MM-DD

### Validation

Describe the controlled retest.

### Result

Resolved / Partially Resolved / Not Resolved.

### Evidence

Reference the retest evidence.

### Final Status

Closed / Open / Risk Accepted.
```


---

# Reporting Checklist

## Engagement

- [ ] Engagement type documented
- [ ] Dates documented
- [ ] Scope documented
- [ ] Exclusions documented
- [ ] Objectives documented
- [ ] Rules of Engagement summarised
- [ ] Limitations documented
- [ ] Assumptions documented

## Executive Summary

- [ ] Overall outcome explained
- [ ] Business impact explained
- [ ] Attack path summarised
- [ ] Key findings prioritised
- [ ] Detection effectiveness discussed
- [ ] Response effectiveness discussed
- [ ] Strategic recommendations included
- [ ] Excessive technical detail removed

## Attack Narrative

- [ ] Initial position identified
- [ ] Major attack stages documented
- [ ] Security boundaries identified
- [ ] Findings connected
- [ ] Objective documented
- [ ] Detection points included
- [ ] Attack-path diagram included where useful

## Findings

- [ ] Finding ID
- [ ] Clear title
- [ ] Severity
- [ ] Affected systems
- [ ] Description
- [ ] Observation
- [ ] Prerequisites
- [ ] Evidence
- [ ] Impact
- [ ] Root cause
- [ ] Detection
- [ ] Recommendation
- [ ] Validation
- [ ] ATT&CK mapping where useful

## Evidence

- [ ] Evidence supports claim
- [ ] Evidence ID assigned
- [ ] Timestamp recorded
- [ ] Host recorded
- [ ] User recorded
- [ ] Screenshots readable
- [ ] Captions included
- [ ] Credentials redacted
- [ ] Personal data minimised
- [ ] Hash recorded where required

## Detection

- [ ] Prevention distinguished from detection
- [ ] Telemetry documented
- [ ] SIEM visibility documented
- [ ] Alert documented
- [ ] SOC response documented
- [ ] Detection gaps categorised
- [ ] Positive controls documented
- [ ] Timing recorded

## ATT&CK

- [ ] Techniques actually tested
- [ ] Mappings reviewed
- [ ] Coverage definition explained
- [ ] Untested techniques distinguished
- [ ] Detection coverage represented accurately

## Recommendations

- [ ] Root cause addressed
- [ ] Immediate actions identified
- [ ] Tactical actions identified
- [ ] Strategic actions identified
- [ ] Priority assigned
- [ ] Ownership suggested where appropriate
- [ ] Validation procedure provided

## Retest

- [ ] Original weakness repeated where safe
- [ ] Original attack path considered
- [ ] Remediation verified
- [ ] Detection improvements verified
- [ ] Retest evidence captured
- [ ] Final status assigned

## Cleanup

- [ ] Payloads removed
- [ ] Scripts removed
- [ ] Accounts reviewed
- [ ] Persistence removed
- [ ] Tunnels stopped
- [ ] Routes removed
- [ ] C2 sessions stopped
- [ ] Credentials revoked
- [ ] Infrastructure decommissioned
- [ ] DNS reviewed
- [ ] Cleanup exceptions documented
- [ ] Cleanup verified

## Delivery

- [ ] Peer review completed
- [ ] Technical review completed
- [ ] Management review completed
- [ ] Secret search completed
- [ ] Screenshot review completed
- [ ] Metadata reviewed
- [ ] Version assigned
- [ ] Recipient list verified
- [ ] Approved delivery channel used
- [ ] Retention requirements recorded


---

# Reporting Decision Model

```text
                     Observation
                         |
                         v
                  Evidence Available?
                    /          \
                  No            Yes
                  |              |
                  v              v
             Gather Evidence   Security
                              Impact?
                              /     \
                            No       Yes
                            |         |
                            v         v
                      Informational  Root Cause
                                      |
                                      v
                                 Attack Path?
                                  /       \
                                No         Yes
                                |           |
                                v           v
                           Standalone     Link to
                            Finding      Attack Path
                                |           |
                                +-----+-----+
                                      |
                                      v
                                Recommendation
                                      |
                                      v
                                  Validation
```


---

# Finding Prioritisation Model

```text
                      Finding
                         |
                         v
                 Security Boundary?
                    /         \
                  No           Yes
                  |             |
                  v             v
              Low Impact    Privilege?
                              /     \
                            No       Yes
                            |         |
                            v         v
                         Exposure   High Impact
                            |         |
                            +----+----+
                                 |
                                 v
                          Attack Path Role
                                 |
                   +-------------+-------------+
                   |                           |
                   v                           v
               Isolated                    Enables
                Issue                    Multiple Paths
                   |                           |
                   v                           v
             Normal Priority             Higher Priority
```


---

# Final Reporting Model

```text
                       ASSESSMENT
                           |
                           v
                        EVIDENCE
                           |
                           v
                    ATTACK TIMELINE
                           |
                           v
                     ATTACK PATHS
                           |
              +------------+------------+
              |                         |
              v                         v
          FINDINGS                 DETECTIONS
              |                         |
              v                         v
          ROOT CAUSE                SOC RESPONSE
              |                         |
              +------------+------------+
                           |
                           v
                        IMPACT
                           |
                           v
                    RECOMMENDATIONS
                           |
                           v
                       PRIORITIES
                           |
                           v
                        RETEST
                           |
                           v
                    RISK REDUCTION
```


---

# Core Principle

A red team report can be reduced to:

```text
Do not report only what commands worked.

Explain the attack path.

Explain which security boundaries were crossed.

Explain why those boundaries could be crossed.

Show enough evidence to prove the result.

Separate prevention from detection.

Explain what defenders saw.

Explain what defenders missed.

Describe the realistic business impact.

Recommend controls that break the attack path.

Provide a way to validate those controls.

Retest the complete path where appropriate.
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
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Active Directory](../active-directory/)
- [Windows](../windows/)
- [Linux](../linux/)
- [PrivEsc Explorer](../privesc/)


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Lateral Movement](https://attack.mitre.org/tactics/TA0008/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credential Access](https://attack.mitre.org/tactics/TA0006/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Defense Evasion](https://attack.mitre.org/tactics/TA0005/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Detection Strategies](https://attack.mitre.org/detectionstrategies/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [FIRST CVSS](https://www.first.org/cvss/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Report attack paths, not just vulnerabilities"
    The most useful red team report explains how multiple weaknesses interacted. A credential exposure issue, permissive network path, excessive privilege, and missing detection may each appear manageable in isolation but together form a path to a critical objective. Prioritising controls that break these paths usually provides more value than treating every observation as an independent vulnerability.


!!! warning "Protect the report"
    A red team report may provide a detailed map of an organisation's security weaknesses, identities, internal architecture, detection gaps, and attack paths. Treat the report and its evidence as sensitive security information, distribute it only through approved channels, remove reusable credentials from distributed copies, and apply the agreed retention and deletion requirements.
