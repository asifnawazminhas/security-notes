---
title: Red Team Adversary Emulation
description: Adversary emulation methodology for authorised red team assessments, covering threat intelligence, ATT&CK mapping, emulation plans, objectives, procedures, atomic testing, CALDERA, detection validation, purple teaming, evidence, metrics, cleanup and reporting.
---

# Red Team Adversary Emulation

Adversary emulation is a threat-informed security assessment approach in which authorised testers reproduce selected behaviours associated with realistic threat actors or intrusion scenarios.

The objective is not to copy every technique ever attributed to an adversary.

The objective is to answer:

```text
If an attacker relevant to this organisation used these
behaviours, would our controls prevent, detect and respond?
```

A useful adversary emulation model is:

```text
Threat Intelligence
        |
        v
Relevant Adversary
        |
        v
ATT&CK Techniques
        |
        v
Emulation Plan
        |
        v
Controlled Procedures
        |
        v
Security Telemetry
        |
        v
Detection
        |
        v
Response
        |
        v
Lessons Learned
```

!!! warning "Authorised testing only"
    Adversary emulation can include behaviours that resemble real intrusions. Scope, systems, identities, techniques, infrastructure, payloads, test windows, prohibited actions, stop conditions and cleanup requirements should be explicitly defined before execution.


---

# Objectives

Adversary emulation can help answer:

```text
Can the organisation detect relevant attacker behaviour?

Which attack paths are realistic?

Which controls prevent progression?

Where are telemetry gaps?

Where are detection gaps?

Can the SOC correlate activity across multiple systems?

Can responders reconstruct the attack chain?

How quickly can the organisation respond?

Which ATT&CK techniques have actually been validated?
```


---

# Adversary Emulation vs Penetration Testing

Penetration testing often asks:

```text
What vulnerabilities exist?
```

Adversary emulation asks:

```text
How would a realistic attacker combine behaviours to pursue
an objective?
```

The two approaches overlap but have different emphasis.


---

# Adversary Emulation vs Red Teaming

Adversary emulation is often part of a broader red team engagement.

```text
Red Teaming
    |
    +--> Objective-based operations
    |
    +--> Attack-path testing
    |
    +--> Social engineering
    |
    +--> Physical testing
    |
    +--> Adversary emulation
```

A red team may use an adversary profile to guide the engagement without attempting to reproduce every historical behaviour of that actor.


---

# Adversary Emulation vs Purple Teaming

A useful distinction is:

```text
Red Team Emulation
        |
        v
Behaviour Executed
        |
        v
Blue Team Detects / Responds
```

Purple teaming adds direct collaboration:

```text
Red Team
   |
   v
Technique
   |
   v
Blue Team
   |
   v
Detection Review
   |
   v
Tune Control
   |
   v
Retest
```

Both approaches can use the same ATT&CK techniques.


---

# Threat-Informed Testing

Adversary emulation should begin with threat relevance.

Sources may include:

```text
Threat intelligence reports

Industry reporting

Internal incidents

SOC observations

Sector threats

MITRE ATT&CK

CISA advisories

Vendor research

ISAC information
```

The goal is to select behaviours relevant to:

```text
Organisation

Industry

Technology stack

Geography

Business model

Known threat landscape
```


---

# Threat Model

A simple model is:

```text
Threat Actor
     |
     v
Motivation
     |
     v
Target
     |
     v
Capabilities
     |
     v
Likely Techniques
     |
     v
Relevant Attack Paths
```


---

# Threat Relevance

Before selecting an adversary, ask:

```text
Does this actor target our sector?

Does the actor operate in our geography?

Does the actor target our technology?

Are the actor's objectives relevant?

Are the attributed techniques sufficiently documented?

Can the important behaviours be safely tested?
```


---

# Avoid Actor Name Chasing

Do not choose an adversary merely because the name is well known.

For example:

```text
Famous Threat Actor
        |
        v
Poor Relevance
        |
        v
Low-Value Exercise
```

A less famous intrusion set may provide a more realistic scenario.


---

# Behaviour Matters More Than Branding

Threat attribution can change.

Therefore, prioritise:

```text
Observed behaviours

ATT&CK techniques

Attack paths

Security-control implications
```

rather than treating an adversary label as absolute truth.


---

# ATT&CK

MITRE ATT&CK provides a common language for describing adversary behaviour.

Enterprise tactics include areas such as:

```text
Reconnaissance

Resource Development

Initial Access

Execution

Persistence

Privilege Escalation

Defence Evasion

Credential Access

Discovery

Lateral Movement

Collection

Command and Control

Exfiltration

Impact
```


---

# ATT&CK Hierarchy

```text
Tactic
  |
  v
Technique
  |
  v
Sub-technique
  |
  v
Procedure
```

Example concept:

```text
Credential Access
      |
      v
OS Credential Dumping
      |
      v
Specific Procedure
```


---

# Tactic

A tactic represents the adversary's objective.

Examples:

```text
Initial Access

Discovery

Credential Access

Lateral Movement
```


---

# Technique

A technique describes how an adversary may achieve that objective.

For example:

```text
Valid Accounts

Remote Services

Scheduled Task/Job
```


---

# Sub-Technique

A sub-technique provides more specific behaviour.

This allows detection coverage to be mapped more precisely.


---

# Procedure

A procedure is the concrete implementation of a technique.

Different adversaries may implement the same ATT&CK technique differently.

```text
Same Technique
     |
     +--> Native OS command
     |
     +--> PowerShell
     |
     +--> Custom tool
     |
     +--> Administrative utility
```


---

# ATT&CK Is Not a Checklist

Do not treat ATT&CK as:

```text
Execute every technique.
```

Instead:

```text
Threat Intelligence
       |
       v
Relevant Behaviours
       |
       v
Relevant ATT&CK Techniques
       |
       v
Safe Procedures
```


---

# Selecting an Adversary

Create an adversary profile containing:

```text
Name or scenario

Motivation

Typical targets

Initial access patterns

Credential behaviour

Discovery behaviour

Lateral movement

Persistence

Command and control

Collection

Exfiltration

Relevant ATT&CK techniques
```


---

# Generic Scenario Profiles

A named threat actor is not always required.

Useful profiles may include:

```text
Ransomware affiliate

Credential-focused intruder

Cloud identity attacker

Business email compromise actor

External espionage actor

Malicious insider

Compromised administrator
```

This can reduce dependence on uncertain attribution.


---

# Scenario Example

```text
Scenario:
Credential-Focused External Intruder

Objective:
Reach a sensitive internal application using compromised
employee access.

Initial Access:
Synthetic test account

Primary Behaviours:
Account discovery
Host discovery
Credential access
Remote services
Lateral movement
Collection

Final Objective:
Access customer-provided synthetic objective file
```


---

# Define the Objective

Every emulation should have a business-relevant objective.

Examples:

```text
Reach a sensitive application

Access a synthetic crown-jewel file

Reach a privileged identity

Access a controlled database record

Demonstrate movement between security tiers

Validate ransomware precursor detections
```


---

# Crown Jewels

Identify:

```text
Critical applications

Identity infrastructure

Sensitive databases

Administrative systems

Cloud control planes

Business-critical services
```

Use synthetic proof where possible.


---

# Emulation Plan

The emulation plan converts threat intelligence into a controlled test.

Example structure:

```text
1. Scenario

2. Threat rationale

3. Objective

4. Scope

5. Assumptions

6. ATT&CK techniques

7. Procedures

8. Expected telemetry

9. Expected detections

10. Stop conditions

11. Cleanup
```


---

# Technique Matrix

Example:

| Phase | Technique | Test Objective | Status |
|---|---|---|---|
| Initial Access | Valid Accounts | Test authentication controls | Planned |
| Discovery | System Information Discovery | Validate endpoint visibility | Planned |
| Credential Access | Credential-related behaviour | Validate detection | Planned |
| Lateral Movement | Remote Services | Validate segmentation | Planned |
| Collection | Data from Local System | Validate access controls | Planned |


---

# Procedure Matrix

A more useful matrix adds implementation context.

| Technique | Procedure | Host | Expected Telemetry | Expected Detection |
|---|---|---|---|---|
| System Discovery | Native system command | WS01 | Process creation | Discovery alert |
| Account Discovery | Native identity query | WS01 | Process/identity telemetry | Behaviour correlation |
| Remote Services | Approved remote administration | SRV01 | Authentication/network logs | Lateral movement alert |


---

# Preconditions

Every procedure should document prerequisites.

Example:

```text
Technique:
Remote Services

Preconditions:
Valid synthetic account
Network reachability
Approved destination
Required service enabled
```

This prevents failed tests from being misclassified as successful defensive controls.


---

# Expected Outcome

Document:

```text
What should happen?

Which control should prevent it?

Which telemetry should appear?

Which alert should trigger?

What should the SOC do?
```


---

# Procedure Safety

Procedures should be:

```text
Minimal

Reversible

Observable

Scoped

Repeatable

Non-destructive where possible
```


---

# Safe Validation Ladder

```text
1. Confirm scope

2. Confirm preconditions

3. Run minimal procedure

4. Verify expected system effect

5. Check telemetry

6. Check detection

7. Check response

8. Stop if objective is proven

9. Cleanup
```


---

# Atomic Testing

An atomic test validates one behaviour at a time.

```text
Technique
    |
    v
Small Procedure
    |
    v
Telemetry
    |
    v
Detection
```

Atomic testing is particularly useful during purple team exercises.


---

# Atomic vs Chained Emulation

Atomic:

```text
Technique A
   |
   v
Validate Detection
```

Chained:

```text
Technique A
   |
   v
Technique B
   |
   v
Technique C
   |
   v
Objective
```

Atomic testing helps identify individual control gaps.

Chained testing evaluates whether defenders can understand the overall attack path.


---

# Atomic Red Team

Atomic Red Team provides small tests mapped to ATT&CK techniques.

Before using an atomic test:

```text
Review the test

Review dependencies

Review cleanup

Confirm scope

Understand expected system changes

Confirm telemetry

Use only the required test
```

Do not bulk-execute an entire library against production systems.


---

# Atomic Red Team Repository

A typical local review workflow is:

```bash
git clone https://github.com/redcanaryco/atomic-red-team.git
```

Then review the relevant technique directory before running anything.

The repository contains tests that can alter systems, create files, modify configuration or execute tools.

Treat every test as code requiring review.


---

# Atomic Test Record

```text
Test ID:
EMU-T1059-001

Technique:
T1059

Host:
WS01

Procedure:
Approved benign command interpreter validation

Expected Telemetry:
Process creation
Command-line telemetry

Expected Detection:
Command interpreter activity available in EDR

Cleanup:
None required
```


---

# CALDERA

MITRE CALDERA is an automated adversary emulation platform.

It can model:

```text
Adversaries

Abilities

Operations

Agents

Objectives
```

Use automation carefully.


---

# CALDERA Model

```text
Adversary Profile
       |
       v
Abilities
       |
       v
Operation
       |
       v
Agent
       |
       v
Endpoint
       |
       v
Telemetry
```


---

# Automation Safety

Automated emulation introduces risks such as:

```text
Unexpected technique execution

Large numbers of commands

Scope expansion

Repeated actions

System changes

Cleanup complexity
```

Use:

```text
Small test groups

Reviewed abilities

Explicit hosts

Controlled operations

Defined stop conditions
```


---

# Manual vs Automated Emulation

Manual execution provides:

```text
Fine control

Immediate judgement

Easy stop decisions
```

Automation provides:

```text
Repeatability

Scale

Regression testing

Consistent procedure execution
```

A mature programme can use both.


---

# Emulation Execution Modes

Possible modes include:

```text
Blind

Semi-blind

Collaborative

Purple team

Detection engineering
```


---

# Blind Exercise

The defensive team is not informed of exact timing or procedures.

Useful for:

```text
Operational detection

SOC response

Escalation

Incident handling
```

It provides less opportunity for immediate tuning.


---

# Purple Team Mode

Red and blue teams collaborate during execution.

```text
Execute
   |
   v
Observe
   |
   v
Explain
   |
   v
Tune
   |
   v
Retest
```

Useful for rapidly improving detection coverage.


---

# Hybrid Model

A practical model is:

```text
Phase 1
Blind Validation

Phase 2
Collaborative Review

Phase 3
Detection Tuning

Phase 4
Retest
```

This provides both realistic measurement and learning.


---

# Deconfliction

Because adversary emulation resembles real attacker behaviour, establish a deconfliction process.

```text
Suspicious Activity
       |
       v
Security Team
       |
       v
Authorised Contact
       |
       v
Exercise or Real Attack?
       |
       +--> Exercise
       |
       +--> Real Incident
```

Never assume suspicious activity belongs to the exercise.


---

# Test Identifiers

Where practical, assign:

```text
Campaign ID

Operation ID

Technique ID

Procedure ID
```

Example:

```text
Campaign:
EMU-2026-01

Technique:
T1087

Procedure:
EMU-2026-01-T1087-01
```


---

# Time Synchronisation

Use consistent time.

Prefer:

```text
UTC
```

Record:

```text
Start

End

Host

Operator

Procedure
```


---

# Execution Log

Example:

| Time | Host | Technique | Procedure | Result |
|---|---|---|---|---|
| 10:02 | WS01 | Account Discovery | Native query | Success |
| 10:05 | WS01 | System Discovery | Native query | Success |
| 10:14 | WS01 | Remote Services | Approved connection | Blocked |


---

# Initial Access

An emulation may begin from:

```text
External attacker position

Synthetic compromised account

Assumed breach workstation

Existing foothold

Cloud test identity
```

The starting point should be explicit.


---

# Assumed Breach

An assumed-breach scenario skips initial access.

Example:

```text
Assumption:
The attacker already controls a standard employee workstation.

Start:
WS01

Identity:
CORP\redteam-user
```

This allows deeper controls to be tested without depending on phishing success.


---

# Execution

Execution testing asks:

```text
Can the relevant procedure run?

What process is created?

Which security controls observe it?

Is it prevented?

Is it detected?
```

See:

[Execution](execution.md)


---

# Discovery

Discovery is essential for realistic adversary emulation.

Relevant behaviours may include:

```text
System discovery

User discovery

Group discovery

Network discovery

Domain discovery

Trust discovery

Security software discovery
```

See:

[Discovery](discovery.md)


---

# Privilege Escalation

Where the threat scenario requires elevated privileges:

```text
Current Context
      |
      v
Relevant PrivEsc Path
      |
      v
Controlled Validation
      |
      v
Elevated Context
```

See:

[Privilege Escalation](privilege-escalation.md)


---

# Credential Access

Credential-related procedures should use the minimum level of access required to validate the objective.

Prefer:

```text
Synthetic credentials

Test accounts

Controlled secrets

Minimal validation
```

See:

[Credential Access](credential-access.md)


---

# Lateral Movement

Lateral movement procedures should document:

```text
Source

Destination

Identity

Protocol

Security boundary

Expected authentication telemetry
```

See:

[Lateral Movement](lateral-movement.md)


---

# Persistence

Persistence is not required in every emulation.

Only include it when relevant to the threat model.

See:

[Persistence](persistence.md)


---

# Defence Evasion

Threat intelligence may describe evasion behaviour.

For production testing, translate this into safe security-control validation.

For example:

```text
Threat intelligence:
Actor attempts to interfere with security controls.

Safe emulation objective:
Validate whether tamper protection, application control,
telemetry and alerting identify unauthorised control changes.
```

Do not disable security controls merely to make the scenario succeed.

See:

[Defence Evasion](defence-evasion.md)


---

# Command and Control

C2 may be represented through:

```text
Controlled framework

Synthetic callback

Approved HTTPS endpoint

DNS marker

Framework simulation
```

The exact mechanism should match the engagement objective.

See:

[Command and Control](command-and-control.md)


---

# Collection

Collection procedures should use:

```text
Synthetic data

Customer-provided markers

Minimum required proof
```

See:

[Collection](collection.md)


---

# Exfiltration

If exfiltration is relevant, transfer synthetic data to an approved destination.

See:

[Exfiltration](exfiltration.md)


---

# Impact

ATT&CK includes Impact behaviours.

Examples may relate to:

```text
Service interruption

Data destruction

Encryption

Account disruption
```

These behaviours can create substantial production risk.


---

# Safe Impact Simulation

Instead of performing destructive actions:

```text
Real Ransomware Encryption
        |
        X
        |
        v
Synthetic Test Directory
        |
        v
Controlled File Operation
        |
        v
Detection Validation
```

Use isolated or synthetic resources.


---

# Ransomware Emulation

A ransomware-focused exercise might validate:

```text
Initial access

Credential access

Privilege escalation

Discovery

Lateral movement

Backup discovery

Security control interaction

File-access patterns

Detection

Containment
```

The final destructive step can be simulated.


---

# Ransomware Safety Boundary

Do not encrypt production files.

Use:

```text
Synthetic directory

Dedicated test host

Disposable VM

Customer-provided test share
```


---

# Cloud Adversary Emulation

Cloud-focused scenarios may involve:

```text
Identity discovery

Role discovery

Resource discovery

Storage discovery

Application consent

Privilege paths

Audit telemetry
```

Use read-only queries wherever possible.


---

# Cloud Test Identity

Prefer:

```text
Dedicated account

Dedicated role

Temporary permissions

Controlled subscription/project/account
```

This makes cleanup and attribution easier.


---

# Identity-Focused Emulation

Identity attacks increasingly span:

```text
Endpoint

Active Directory

Entra ID

Cloud IAM

SaaS

OAuth
```

An identity-focused emulation should trace the complete authentication path.


---

# Identity Attack Path

```text
User Account
    |
    v
Authentication
    |
    v
MFA
    |
    v
Session
    |
    v
Application
    |
    v
Privilege
```

Validate controls at every boundary.


---

# Active Directory Emulation

AD scenarios may include:

```text
Domain discovery

Group discovery

Kerberos activity

NTLM activity

Delegation

ACL relationships

Certificate Services

Remote administration
```

Deep AD techniques should remain in the dedicated Active Directory notes rather than being duplicated here.


---

# BloodHound

BloodHound can help identify potential relationships and attack paths.

Use it to answer:

```text
Which privilege relationships exist?

Which path is relevant to the scenario?

Which security boundaries matter?

Which path should be validated?
```

See:

[BloodHound](../active-directory/bloodhound.md)


---

# Detection Engineering

Every emulated technique should ideally have a detection hypothesis.

Example:

```text
Technique:
Account Discovery

Hypothesis:
Account enumeration from an employee workstation should create
process or directory-service telemetry visible to the SOC.

Expected Sources:
Endpoint telemetry
Process creation
Directory-service telemetry

Expected Result:
Relevant activity is searchable and can be correlated with
other discovery behaviour.
```


---

# Detection Matrix

| Technique | Endpoint | Identity | Network | SIEM | Alert |
|---|---|---|---|---|---|
| Account Discovery | Yes | Yes | - | Yes | Partial |
| Remote Services | Yes | Yes | Yes | Yes | Yes |
| Collection | Yes | - | - | Yes | No |
| Exfiltration | Yes | - | Yes | Yes | Yes |


---

# Prevention vs Detection

Keep results separate.

```text
Prevented
```

means the action could not complete.

```text
Detected
```

means useful telemetry or alerting identified the behaviour.

Possible outcomes include:

```text
Prevented and Detected

Prevented but Not Detected

Allowed and Detected

Allowed and Logged

Allowed without Visibility
```


---

# Telemetry Validation

For each technique determine:

```text
Was telemetry generated?

Was it collected?

Was it parsed?

Was it searchable?

Was it correlated?

Was an alert generated?

Did the SOC investigate?
```


---

# Detection Pipeline

```text
Technique
   |
   v
Telemetry
   |
   v
Collector
   |
   v
SIEM
   |
   v
Detection Rule
   |
   v
Alert
   |
   v
Analyst
   |
   v
Response
```


---

# Detection Gap Categories

Classify gaps as:

```text
Telemetry Gap

Collection Gap

Parsing Gap

Detection Gap

Alerting Gap

Triage Gap

Response Gap
```


---

# Telemetry Gap

```text
Required event was not generated.
```


---

# Collection Gap

```text
Event existed locally but was not forwarded.
```


---

# Parsing Gap

```text
Event reached the platform but important fields were not parsed.
```


---

# Detection Gap

```text
Useful telemetry existed but no detection logic identified the
behaviour.
```


---

# Alerting Gap

```text
Detection logic matched but did not create an actionable alert.
```


---

# Response Gap

```text
An alert existed but the operational response was insufficient.
```


---

# Correlation

Individual techniques may appear benign.

For example:

```text
User Discovery

System Discovery

Network Discovery
```

may each have legitimate administrative uses.

Together:

```text
User Discovery
      +
System Discovery
      +
Network Discovery
      +
Remote Connection
      |
      v
Suspicious Sequence
```

Behavioural correlation can provide stronger detection.


---

# Attack Chain Detection

Evaluate whether defenders can connect:

```text
Initial Access
      |
      v
Execution
      |
      v
Discovery
      |
      v
Credential Access
      |
      v
Lateral Movement
      |
      v
Collection
```

rather than treating each event independently.


---

# SOC Validation

Record whether analysts:

```text
Received alert

Identified source host

Identified user

Identified destination

Mapped related events

Escalated incident

Contained activity

Documented findings
```


---

# Blue Team Visibility

Possible visibility levels:

```text
No Visibility

Raw Log Only

Searchable Telemetry

Detection

High-Fidelity Alert

Correlated Incident

Automated Response
```


---

# Purple Team Loop

```text
Select Technique
      |
      v
Execute
      |
      v
Observe Telemetry
      |
      v
Detection Works?
   /             \
 Yes              No
 |                 |
 v                 v
Document          Investigate Gap
                   |
                   v
                 Improve
                   |
                   v
                 Retest
```


---

# Detection as Code

Where detection rules are maintained as code:

```text
Technique
   |
   v
Detection Hypothesis
   |
   v
Rule
   |
   v
Test
   |
   v
Version Control
   |
   v
Regression Test
```

This supports repeatable validation.


---

# Sigma

Sigma provides a generic format for describing log-based detections.

A high-level example:

```yaml
title: Example Discovery Behaviour
status: experimental

logsource:
  category: process_creation
  product: windows

detection:
  selection:
    Image|endswith:
      - '\whoami.exe'
      - '\hostname.exe'
  condition: selection
```

This is only an illustrative detection example.

Production rules require environment-specific tuning.


---

# Regression Testing

Once a detection has been fixed:

```text
Original Technique
       |
       v
Same Procedure
       |
       v
Expected Telemetry
       |
       v
Expected Alert
       |
       v
Pass / Fail
```

Repeatability turns one-time exercises into continuous validation.


---

# Technique Coverage

ATT&CK coverage should distinguish:

```text
Mapped

Tested

Prevented

Detected

Responded
```

A mapped technique is not automatically a tested technique.


---

# Coverage Example

| Technique | Mapped | Tested | Telemetry | Detection | Response |
|---|---:|---:|---:|---:|---:|
| T1087 | Yes | Yes | Yes | Partial | No |
| T1016 | Yes | Yes | Yes | Yes | Yes |
| T1021 | Yes | Yes | Yes | Yes | Yes |
| T1005 | Yes | No | Unknown | Unknown | Unknown |


---

# Avoid Misleading Heatmaps

A green ATT&CK square should not automatically mean:

```text
We detect this technique.
```

Document what green actually means.

For example:

```text
Green:
Test executed and expected alert confirmed.

Yellow:
Telemetry available but alert incomplete.

Red:
Test executed without useful detection.

Grey:
Not tested.
```


---

# Technique Selection

Prioritise techniques based on:

```text
Threat relevance

Business impact

Attack-path importance

Current control uncertainty

Historical incidents

Detection gaps

Feasibility

Safety
```


---

# Prioritisation Matrix

```text
                   Threat Relevance
                 Low            High
              +-----------------------+
High Impact    | Review      | Priority |
              |             |          |
              +-----------------------+
Low Impact     | Low        | Consider |
              | Priority   |          |
              +-----------------------+
```


---

# Emulation Plan Example

```text
Campaign:
EMU-2026-02

Scenario:
Assumed-breach credential-focused intruder

Objective:
Reach the synthetic finance objective from a standard
workstation.

Starting Host:
WS01

Starting Identity:
CORP\redteam-user

Techniques:
System Discovery
Account Discovery
Domain Discovery
Credential Access
Remote Services
Collection

Excluded:
Destructive impact
Production credential dumping
Security-control disabling
Production data exfiltration

Final Proof:
Read customer-provided synthetic objective file.

Detection Goal:
SOC identifies and correlates the attack path before objective
completion.
```


---

# Execution Gates

Before progressing to the next phase, use gates.

```text
Phase Complete
     |
     v
Objective Met?
   /        \
 No          Yes
 |            |
 v            v
Review      Scope Still Valid?
               /       \
             No         Yes
             |           |
            STOP         v
                     Next Phase
```


---

# Gate Questions

Ask:

```text
Are we still in scope?

Is the next technique authorised?

Are preconditions satisfied?

Has unexpected production impact occurred?

Has the objective already been proven?

Would the next action add meaningful evidence?
```


---

# Stop When Proven

Do not continue simply because additional techniques are available.

```text
Objective Proven
      |
      v
Collect Evidence
      |
      v
Stop Progression
```

This is particularly important near sensitive systems.


---

# Evidence

For every procedure record:

```text
Campaign ID

Procedure ID

ATT&CK technique

Host

Identity

Timestamp

Command or procedure description

Expected result

Actual result

Telemetry

Detection

Response

Cleanup
```


---

# Evidence Example

```text
Campaign:
EMU-2026-02

Procedure:
EMU-2026-02-T1087-01

Technique:
Account Discovery

Host:
WS01

Identity:
CORP\redteam-user

Result:
Approved discovery procedure completed.

Endpoint Telemetry:
Present

SIEM:
Event ingested

Detection:
No dedicated alert

SOC:
No investigation observed

Cleanup:
None required
```


---

# Timeline

Example:

```text
10:00 - Emulation begins
10:04 - System discovery
10:07 - Account discovery
10:12 - Domain discovery
10:20 - Credential-related test
10:31 - Remote-service validation
10:33 - Authentication telemetry generated
10:35 - SIEM alert created
10:40 - Analyst begins triage
10:48 - Source account identified
10:54 - Source host isolated
10:56 - Exercise paused
```


---

# Metrics

Useful metrics include:

```text
Techniques planned

Techniques executed

Techniques prevented

Techniques detected

Techniques with telemetry only

Techniques without visibility

Time to detection

Time to triage

Time to containment

Attack-path stage reached
```


---

# Detection Rate

```text
Detected Tested Techniques / Tested Techniques * 100
```

Use carefully.

Not every ATT&CK technique should necessarily produce an individual alert.


---

# Telemetry Coverage

```text
Techniques With Useful Telemetry / Techniques Tested * 100
```


---

# Prevention Coverage

```text
Prevented Techniques / Techniques Tested * 100
```


---

# Response Coverage

```text
Techniques or Attack Paths With Appropriate Response
-----------------------------------------------------
Relevant Tested Techniques or Attack Paths
```


---

# Time to Detect

```text
TTD = Detection Time - Procedure Start
```


---

# Time to Triage

```text
TTT = Analyst Triage Time - Detection Time
```


---

# Time to Contain

```text
TTC = Containment Time - Detection Time
```


---

# Attack Path Depth

Another useful metric is how far the emulation progressed.

```text
Initial Access
      |
      v
Execution
      |
      v
Discovery
      |
      v
Credential Access
      |
      X
   Detected /
   Contained
```

This may be more meaningful than counting individual alerts.


---

# Positive Security Results

Document controls that succeed.

Examples:

```text
EDR prevented execution

Application control blocked procedure

Segmentation prevented movement

MFA prevented account use

DLP blocked synthetic transfer

SOC detected discovery

SOC contained source host
```


---

# Finding Structure

A useful adversary emulation finding includes:

```text
Title

Scenario

Threat relevance

ATT&CK mapping

Observation

Evidence

Attack-path role

Impact

Detection result

Root cause

Recommendation

Retest
```


---

# Example Finding - Discovery Visibility Gap

```text
Title:
Internal Discovery Activity Is Logged but Not Correlated

Scenario:
Assumed-breach credential-focused intruder

ATT&CK:
Account Discovery
System Information Discovery
System Network Configuration Discovery

Observation:
The emulation executed several approved discovery procedures
from the synthetic compromised workstation.

Endpoint telemetry for the individual processes was available in
the SIEM.

No detection correlated the sequence of discovery activity, and
no SOC investigation was observed during the agreed validation
window.

Impact:
An attacker operating from a compromised workstation may be
able to perform internal situational awareness without
generating an actionable alert.

Recommendation:
Develop behavioural correlation for unusual sequences of
account, host and network discovery, particularly when observed
from non-administrative endpoints. Validate the detection using
the same controlled procedures.
```


---

# Example Finding - Segmentation Success

```text
Title:
Network Segmentation Prevents Tested Lateral Movement Path

Scenario:
Assumed-breach employee workstation

ATT&CK:
Remote Services

Observation:
The assessment attempted the approved remote-service validation
from the compromised test workstation to the protected server
segment.

Network controls prevented the connection.

Firewall telemetry identified the source and destination and was
successfully ingested by the SIEM.

Conclusion:
The tested segmentation control successfully prevented the
emulated lateral movement path and provided useful defensive
telemetry.
```


---

# Example Finding - Detection Without Response

```text
Title:
High-Fidelity Lateral Movement Alert Does Not Result in Timely Investigation

Observation:
The approved remote-service procedure generated the expected
high-severity SIEM alert.

The alert correctly identified the source host, user and target
server.

No analyst investigation was observed during the 45-minute
validation window.

Impact:
Effective detection logic may not reduce attacker dwell time if
alerts are not triaged and escalated promptly.

Recommendation:
Review alert routing, ownership, severity and SOC procedures.
Retest the attack path after operational changes.
```


---

# Candidate vs Confirmed

## Candidate

```text
The environment may lack detection for account discovery.
```


## Likely

```text
The relevant endpoint telemetry is available but no corresponding
detection rule was identified.
```


## Confirmed

```text
The approved account-discovery procedure was executed and
recorded in endpoint telemetry, but no alert was generated during
the agreed validation window.
```


---

# Accurate Reporting

Avoid:

```text
The organisation cannot detect this threat actor.
```

A limited emulation cannot prove that.

Prefer:

```text
The assessment tested six behaviours associated with the
selected threat scenario. Four generated the expected alerts,
one generated telemetry without an alert and one lacked useful
visibility.
```


---

# Threat Intelligence Limitations

Document limitations such as:

```text
Public reporting may be incomplete

Attribution may change

Procedure details may be unavailable

Actor behaviour evolves

Tools may change

Not every reported technique was tested
```


---

# Reporting the Scenario

Describe:

```text
Why the scenario was selected

Which intelligence supported it

Which behaviours were chosen

Which behaviours were excluded

Which systems were tested

Which assumptions were made
```


---

# Attack Path Narrative

Example:

```text
The exercise began from an assumed-breach workstation using a
customer-provided standard user account.

The emulation performed host and domain discovery before
validating access to an approved credential source.

The resulting synthetic credential permitted authentication to
a server in the application segment.

Network authentication telemetry was generated, and the SOC
detected the remote access before the final collection objective
was attempted.
```


---

# Recommendations

Recommendations should address:

```text
Prevention

Telemetry

Detection

Alerting

Triage

Response

Architecture
```


---

# Prevention Recommendations

Potential improvements include:

```text
Least privilege

Application control

MFA

Network segmentation

Credential isolation

Privileged access management

Secure administrative tiers
```


---

# Telemetry Recommendations

Potential improvements include:

```text
Process creation

PowerShell logging

Authentication logs

Directory-service telemetry

DNS

Proxy

Firewall

Cloud audit

EDR

Sysmon
```


---

# Detection Recommendations

Potential improvements include:

```text
Behaviour correlation

Attack-chain analytics

Identity analytics

Rare remote-service use

Unusual discovery sequences

Credential access indicators

Cloud privilege changes
```


---

# Response Recommendations

Potential improvements include:

```text
Alert ownership

Escalation procedures

Host isolation

Account containment

Credential rotation

Investigation playbooks

Cross-team communication
```


---

# Retesting

After remediation:

```text
Original Procedure
      |
      v
Same Preconditions
      |
      v
Same Technique
      |
      v
Expected Detection
      |
      v
Pass / Fail
```

Use the same procedure where practical.


---

# Regression Programme

High-value emulation procedures can become recurring tests.

```text
Threat Intelligence
       |
       v
Stable Test Procedure
       |
       v
Detection Rule
       |
       v
Scheduled Validation
       |
       v
Regression Result
```


---

# Continuous Validation

A mature programme may periodically validate:

```text
Critical ATT&CK techniques

High-risk attack paths

Identity controls

Segmentation

Crown-jewel access

Detection rules
```


---

# Test Library

Maintain an internal library containing:

```text
Test ID

ATT&CK mapping

Description

Preconditions

Procedure

Expected telemetry

Expected detection

Cleanup

Last test date

Result
```


---

# Example Test Library Entry

```text
ID:
DET-WIN-ACCOUNT-001

ATT&CK:
Account Discovery

Platform:
Windows

Risk:
Low

Preconditions:
Standard user session

Expected Telemetry:
Process creation

Expected Detection:
Discovery behaviour visible in EDR

Cleanup:
None

Last Result:
Telemetry confirmed
```


---

# Emulation Plan Versioning

Version emulation plans.

Example:

```text
EMU-2026-01-v1.0
```

Record changes such as:

```text
Technique added

Procedure changed

Detection expectation changed

Cleanup changed
```


---

# Reproducibility

A good emulation procedure should allow another authorised tester to reproduce:

```text
Starting state

Technique

Expected system effect

Expected telemetry

Expected detection

Cleanup
```

without relying on undocumented assumptions.


---

# Tool Selection

Possible tools include:

```text
Native operating system utilities

PowerShell

Atomic Red Team

MITRE CALDERA

Cobalt Strike

Sliver

Metasploit

BloodHound

NetExec

Impacket

Nmap
```

Tool choice should follow the objective.

Do not use a complex offensive framework when a simple benign procedure can validate the same detection.


---

# Tool vs Behaviour

Defenders should avoid detecting only tool names.

```text
Tool Signature
     |
     v
Easy to Change
```

Prefer:

```text
Behaviour
   |
   v
Telemetry Pattern
   |
   v
Detection
```

where possible.


---

# Native Tools

Native tools can be valuable because they test whether defenders detect behaviour without depending on known malware signatures.

However, native administrative commands also create false-positive challenges.

Context matters.


---

# Custom Tooling

If custom tooling is used:

```text
Record version

Record hash

Record purpose

Review source where possible

Control distribution

Remove after engagement
```


---

# Payload Inventory

Maintain:

```text
Filename

SHA-256

Purpose

Host

Deployment time

Removal time
```


---

# OPSEC

Adversary emulation still requires operational security.

Protect:

```text
Infrastructure

Credentials

Threat profiles

Target lists

Payloads

Evidence

Customer data
```

See:

[Red Team OPSEC](opsec.md)


---

# Cleanup

Every procedure should define cleanup before execution.

```text
Procedure
   |
   v
System Change?
  /       \
No         Yes
|           |
v           v
None      Cleanup Action
            |
            v
         Verification
```


---

# Cleanup Examples

Track:

```text
Files

Directories

Tasks

Services

Accounts

Groups

Registry changes

Routes

Firewall rules

Cloud resources

Tokens

Certificates

Applications
```

The complete engagement cleanup process is covered in:

`red-teaming/cleanup.md`


---

# Emulation Checklist

## Planning

- [ ] Business objective defined
- [ ] Threat scenario selected
- [ ] Threat relevance documented
- [ ] Scope approved
- [ ] Starting position defined
- [ ] Crown-jewel objective defined
- [ ] Assumptions documented
- [ ] Exclusions documented
- [ ] Stop conditions defined
- [ ] Deconfliction process defined

## Threat Intelligence

- [ ] Intelligence sources reviewed
- [ ] Sector relevance considered
- [ ] Geographic relevance considered
- [ ] Technology relevance considered
- [ ] Attribution uncertainty documented
- [ ] Behaviours prioritised over actor branding

## ATT&CK

- [ ] Tactics mapped
- [ ] Techniques mapped
- [ ] Sub-techniques mapped where relevant
- [ ] Procedures documented
- [ ] ATT&CK not treated as a simple checklist
- [ ] Untested techniques clearly marked

## Procedures

- [ ] Procedure ID assigned
- [ ] Preconditions documented
- [ ] Expected result documented
- [ ] Expected telemetry documented
- [ ] Expected detection documented
- [ ] Safety reviewed
- [ ] Cleanup documented
- [ ] Procedure manually reviewed

## Execution

- [ ] Correct host confirmed
- [ ] Correct identity confirmed
- [ ] Time recorded
- [ ] Scope revalidated
- [ ] Minimal procedure used
- [ ] Result recorded
- [ ] Unexpected impact checked
- [ ] Next phase justified

## Automation

- [ ] Automated tests reviewed
- [ ] Dependencies reviewed
- [ ] Target hosts explicitly defined
- [ ] Bulk execution avoided
- [ ] Stop capability available
- [ ] Cleanup understood

## Detection

- [ ] Endpoint telemetry reviewed
- [ ] Identity telemetry reviewed
- [ ] Network telemetry reviewed
- [ ] Cloud telemetry reviewed
- [ ] SIEM ingestion confirmed
- [ ] Detection result recorded
- [ ] Alert result recorded
- [ ] SOC response recorded
- [ ] Detection gap classified

## Evidence

- [ ] Campaign ID recorded
- [ ] Procedure ID recorded
- [ ] ATT&CK mapping recorded
- [ ] Host recorded
- [ ] Identity recorded
- [ ] Timestamp recorded
- [ ] Result recorded
- [ ] Telemetry recorded
- [ ] Detection recorded
- [ ] Response recorded

## Reporting

- [ ] Threat rationale explained
- [ ] Attack path documented
- [ ] Tested techniques distinguished from mapped techniques
- [ ] Prevention distinguished from detection
- [ ] Positive controls documented
- [ ] Limitations documented
- [ ] Recommendations prioritised

## Retesting

- [ ] Original procedure retained
- [ ] Detection improvements documented
- [ ] Same preconditions reproduced where possible
- [ ] Retest result recorded
- [ ] Regression candidate identified

## Cleanup

- [ ] Files removed
- [ ] Services reviewed
- [ ] Tasks reviewed
- [ ] Accounts reviewed
- [ ] Credentials revoked
- [ ] Cloud resources removed
- [ ] Infrastructure reviewed
- [ ] Cleanup verified


---

# Adversary Selection Decision Model

```text
                   BUSINESS OBJECTIVE
                          |
                          v
                    THREAT RELEVANT?
                      /         \
                    No           Yes
                    |             |
                    v             v
             GENERIC SCENARIO   INTELLIGENCE
                                  |
                                  v
                          BEHAVIOURS KNOWN?
                            /          \
                          No            Yes
                          |              |
                          v              v
                    USE SCENARIO     ATT&CK MAP
                                         |
                                         v
                                  SAFE TO EMULATE?
                                    /          \
                                  No            Yes
                                  |              |
                                  v              v
                              SIMULATE        PROCEDURE
                                  |              |
                                  +------+-------+
                                         |
                                         v
                                      TEST PLAN
```


---

# Technique Decision Model

```text
                    TECHNIQUE
                        |
                        v
                 THREAT RELEVANT?
                   /         \
                 No           Yes
                 |             |
                SKIP           v
                         IN SCOPE?
                          /      \
                        No        Yes
                        |          |
                       SKIP        v
                            SAFE PROCEDURE?
                              /        \
                            No          Yes
                            |            |
                         SIMULATE        v
                                  PRECONDITIONS
                                       |
                                       v
                                     EXECUTE
                                       |
                                       v
                                    TELEMETRY
                                       |
                                       v
                                    DETECTION
                                       |
                                       v
                                     RESPONSE
```


---

# Detection Validation Model

```text
                   EMULATED BEHAVIOUR
                           |
                           v
                       TELEMETRY
                           |
               +-----------+-----------+
               |                       |
               v                       v
            Missing                  Present
               |                       |
               v                       v
         TELEMETRY GAP            COLLECTED?
                                  /        \
                                No          Yes
                                |            |
                                v            v
                         COLLECTION GAP     PARSED?
                                           /     \
                                         No       Yes
                                         |         |
                                         v         v
                                    PARSING GAP   DETECTED?
                                                /        \
                                              No          Yes
                                              |            |
                                              v            v
                                       DETECTION GAP    ALERTED?
                                                       /       \
                                                     No         Yes
                                                     |           |
                                                     v           v
                                              ALERTING GAP    RESPONSE
```


---

# Emulation Maturity Model

```text
Level 1
Ad-hoc technique testing

Level 2
ATT&CK-mapped procedures

Level 3
Threat-informed emulation plans with repeatable detection tests

Level 4
Red, blue and SOC validation with attack-path correlation

Level 5
Continuous threat-informed regression testing integrated with
detection engineering
```


---

# Final Adversary Emulation Model

```text
                     THREAT INTELLIGENCE
                            |
                            v
                       THREAT MODEL
                            |
                            v
                     BUSINESS OBJECTIVE
                            |
                            v
                       ATT&CK MAPPING
                            |
                            v
                       EMULATION PLAN
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        PRECONDITIONS    PROCEDURES      SAFETY
             |              |              |
             +--------------+--------------+
                            |
                            v
                         EXECUTION
                            |
                            v
                        TELEMETRY
                            |
                            v
                        DETECTION
                            |
                            v
                         RESPONSE
                            |
              +-------------+-------------+
              |                           |
              v                           v
          CONTROL WORKS                 GAP
              |                           |
              v                           v
           DOCUMENT                    IMPROVE
              |                           |
              +-------------+-------------+
                            |
                            v
                          RETEST
                            |
                            v
                     REGRESSION TEST
                            |
                            v
                       REPORTING
```


---

# Core Principle

Adversary emulation can be reduced to:

```text
Start with threat relevance.

Define a business objective.

Prioritise behaviour over actor branding.

Map relevant behaviour to ATT&CK.

Do not treat ATT&CK as a checklist.

Document preconditions.

Choose the safest procedure that validates the behaviour.

Use synthetic identities and data where possible.

Execute only authorised techniques.

Measure prevention separately from detection.

Validate telemetry before blaming detection logic.

Measure SOC response.

Correlate the complete attack path.

Document positive security outcomes.

Stop when the objective is proven.

Clean up every system change.

Retest failed controls.

Convert valuable procedures into repeatable regression tests.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Red Team Infrastructure](infrastructure.md)
- [Reconnaissance](reconnaissance.md)
- [Initial Access](initial-access.md)
- [Execution](execution.md)
- [Discovery](discovery.md)
- [Privilege Escalation](privilege-escalation.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Collection](collection.md)
- [Exfiltration](exfiltration.md)
- [Command and Control](command-and-control.md)
- [Social Engineering](social-engineering.md)
- [Phishing](phishing.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)
- [BloodHound](../active-directory/bloodhound.md)

Planned:

```text
red-teaming/cleanup.md
```


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Groups](https://attack.mitre.org/groups/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Software](https://attack.mitre.org/software/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Campaigns](https://attack.mitre.org/campaigns/){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA GitHub](https://github.com/mitre/caldera){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Red Canary - Atomic Red Team](https://redcanary.com/atomic-red-team/){ target="_blank" rel="noopener noreferrer" }
- [MITRE Center for Threat-Informed Defense](https://ctid.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [CISA Cybersecurity Advisories](https://www.cisa.gov/news-events/cybersecurity-advisories){ target="_blank" rel="noopener noreferrer" }
- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog){ target="_blank" rel="noopener noreferrer" }
- [Sigma](https://sigmahq.io/){ target="_blank" rel="noopener noreferrer" }
- [SigmaHQ GitHub](https://github.com/SigmaHQ/sigma){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Emulate behaviour, not malware"
    A useful emulation does not require reproducing an adversary's exact malware. If a safe native or synthetic procedure generates the relevant behaviour and telemetry, it may provide a better and more repeatable detection test.


!!! warning "ATT&CK coverage is not automatically security coverage"
    Mapping a control or detection to an ATT&CK technique does not prove that the organisation can detect that behaviour. Distinguish techniques that are mapped, tested, observed, detected and successfully responded to.
