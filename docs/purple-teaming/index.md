---
title: Purple Teaming
description: Practical purple teaming methodology for collaborative offensive and defensive security testing, detection validation, knowledge transfer, MITRE ATT&CK mapping, security exercises and continuous improvement.
---

# Purple Teaming

Purple teaming is a structured, collaborative security approach in which offensive and defensive security teams work together to improve an organisation's ability to prevent, detect, investigate and respond to cyber attacks.

Rather than treating red and blue teams as isolated functions, purple teaming creates a feedback loop between them.

```text
                PURPLE TEAMING

       Offensive              Defensive
       Perspective            Perspective
            |                      |
            v                      v
        Red Team               Blue Team
            |                      |
            +----------+-----------+
                       |
                       v
                  Collaboration
                       |
                       v
                Security Testing
                       |
                       v
                   Telemetry
                       |
                       v
                   Detection
                       |
                       v
                   Response
                       |
                       v
                    Improve
                       |
                       v
                    Retest
```

The goal is not simply to determine whether an attack succeeds.

The goal is to understand:

```text
What happened?

Why did it happen?

What did the attacker observe?

What did the defender observe?

Was the behaviour prevented?

Was telemetry generated?

Was the telemetry collected?

Was the behaviour detected?

Was an alert generated?

Did the security team respond?

What can be improved?

Did the improvement work when retested?
```

!!! note "Purple is a function, not necessarily a separate team"
    Purple teaming does not require a permanent organisational team called the Purple Team. The purple function can be created through structured collaboration between red teams, blue teams, SOC analysts, detection engineers, incident responders, security engineers and other relevant stakeholders.


---

# Core Objective

A useful purple team model is:

```text
Attack
   |
   v
Observe
   |
   v
Understand
   |
   v
Detect
   |
   v
Improve
   |
   v
Retest
   |
   v
Learn
```

The cycle should produce measurable security improvement rather than only a list of vulnerabilities.


---

# Red, Blue and Purple

## Red Team

The red team provides the offensive perspective.

Typical responsibilities include:

```text
Threat modelling

Attack-path analysis

Technique selection

Adversary emulation

Execution

Privilege escalation

Credential access

Lateral movement

Persistence

Command and control

Objective execution
```


---

# Blue Team

The blue team provides the defensive perspective.

Typical responsibilities include:

```text
Security monitoring

Endpoint protection

Network monitoring

Identity monitoring

SIEM

Detection engineering

Threat hunting

Incident investigation

Containment

Response

Recovery
```


---

# Purple Team

Purple teaming connects both perspectives.

```text
Red Team
   |
   | "This is what I did."
   |
   v
Purple Collaboration
   ^
   |
   | "This is what we observed."
   |
Blue Team
```

The resulting conversation should answer:

```text
Did the technique work?

What telemetry was generated?

Which security controls observed it?

Was the activity detected?

Could analysts understand what happened?

What should be changed?

Can the improvement be validated?
```


---

# Purple Teaming Is Not

Purple teaming should not simply become:

```text
Red Team
   |
   v
Runs Attack
   |
   v
Blue Team
   |
   v
Watches
```

It should instead become:

```text
Red
 |
 v
Execute
 |
 v
Blue
 |
 v
Observe
 |
 v
Discuss
 |
 v
Understand
 |
 v
Improve
 |
 v
Retest
 |
 v
Shared Learning
```


---

# Purple Teaming vs Penetration Testing

Penetration testing typically focuses on identifying and validating vulnerabilities.

```text
Question:

What vulnerabilities can be exploited?
```

Purple teaming focuses more heavily on collaborative defensive improvement.

```text
Question:

Can the organisation prevent, detect and respond to realistic
attacker behaviour, and can those capabilities be improved?
```


---

# Purple Teaming vs Red Teaming

Red teaming commonly evaluates whether an attacker can achieve an objective.

```text
Initial Access
      |
      v
Execution
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
```

Purple teaming focuses on what happens defensively at each stage.

```text
Attack Step
    |
    v
Security Control
    |
    v
Telemetry
    |
    v
Detection
    |
    v
Response
    |
    v
Improvement
```


---

# Purple Teaming vs Vulnerability Assessment

A vulnerability assessment may identify:

```text
Missing patch

Weak configuration

Exposed service

Excessive permission
```

Purple teaming may ask:

```text
If this weakness were used during an attack, what would the
organisation observe and how would defenders respond?
```


---

# Purple Teaming vs Adversary Emulation

Adversary emulation attempts to reproduce behaviours associated with realistic threats.

Purple teaming can use adversary emulation as the testing mechanism.

```text
Threat Intelligence
       |
       v
Adversary Behaviour
       |
       v
ATT&CK Technique
       |
       v
Purple Team Exercise
       |
       v
Detection Validation
```


---

# Why Purple Teaming Matters

Security controls are often deployed independently.

For example:

```text
EDR

SIEM

Firewall

IDS / IPS

Email Security

Identity Protection

Application Control

Cloud Monitoring

DLP
```

Having these technologies does not automatically mean the organisation can detect realistic attacks.

Purple teaming validates whether they work together.


---

# Security Control Reality

A control may be:

```text
Installed

Enabled

Configured

Generating telemetry

Sending telemetry

Parsed correctly

Monitored

Detected

Investigated

Responded to
```

These are different levels of capability.


---

# Prevention, Detection and Response

Purple team exercises should distinguish between three outcomes.

## Prevention

```text
Was the activity blocked?
```


## Detection

```text
Was the activity identified?
```


## Response

```text
Did defenders take appropriate action?
```


---

# Possible Outcomes

A test may result in:

```text
Prevented and Detected

Prevented but Not Detected

Allowed and Detected

Allowed and Logged

Allowed without Useful Visibility
```

Each outcome provides different information.


---

# Purple Team Lifecycle

A practical purple team lifecycle is:

```text
                 PLAN
                   |
                   v
             DEFINE OBJECTIVES
                   |
                   v
             SELECT TECHNIQUES
                   |
                   v
             DEFINE EXPECTATIONS
                   |
                   v
                EXECUTE
                   |
                   v
                OBSERVE
                   |
                   v
                ANALYSE
                   |
                   v
                 IMPROVE
                   |
                   v
                 RETEST
                   |
                   v
                 MEASURE
                   |
                   v
                 REPORT
                   |
                   v
                  LEARN
                   |
                   +--------+
                            |
                            v
                       NEXT CYCLE
```


---

# Planning

Before testing, define:

```text
Business objective

Security objective

Learning objective

Scope

Systems

Identities

Techniques

Expected telemetry

Expected detections

Participants

Communication

Stop conditions

Evidence requirements
```


---

# Business Objectives

Purple teaming should support meaningful organisational goals.

Examples:

```text
Improve ransomware detection.

Validate Active Directory monitoring.

Test lateral movement visibility.

Evaluate endpoint detection coverage.

Improve cloud identity monitoring.

Validate SOC response to credential misuse.

Improve detection of attacker discovery activity.
```


---

# Security Objectives

A business objective should be converted into technical security objectives.

Example:

```text
Business Objective:

Improve resilience against ransomware.

Security Objectives:

Detect credential access.

Detect privilege escalation.

Detect lateral movement.

Detect unusual remote administration.

Detect mass file modification.

Validate containment procedures.
```


---

# Learning Objectives

Purple team exercises should also define what participants are expected to learn.

Examples:

```text
Understand attacker decision making.

Understand endpoint telemetry.

Understand authentication telemetry.

Understand how SIEM detections are constructed.

Understand which events are required for investigation.

Understand how red and blue teams interpret the same activity.
```


---

# Objective Hierarchy

```text
Business Objective
        |
        v
Security Objective
        |
        v
Technical Objective
        |
        v
Learning Objective
        |
        v
Exercise Activity
```


---

# Roles

Purple teaming can involve more than red and blue teams.

Potential participants include:

```text
Red Team

Blue Team

SOC Analysts

Detection Engineers

Threat Hunters

Incident Responders

Security Engineers

Identity Engineers

Network Engineers

Cloud Security

Application Security

Threat Intelligence

Security Architects
```


---

# Red Team Role

The red team should explain:

```text
What technique is being executed?

Why would an attacker use it?

What prerequisites exist?

What is the expected result?

What alternative techniques exist?

What indicators may be generated?
```


---

# Blue Team Role

The blue team should determine:

```text
What telemetry exists?

Where is it collected?

What fields are useful?

Does a detection exist?

Does an alert exist?

Can the activity be investigated?

Can related activity be correlated?
```


---

# SOC Role

SOC analysts validate operational effectiveness.

Questions include:

```text
Did the alert reach the SOC?

Was it prioritised correctly?

Was the alert understandable?

Could the analyst identify the affected host?

Could the analyst identify the account?

Could the analyst reconstruct the attack?

Was escalation appropriate?

Was containment appropriate?
```


---

# Detection Engineering Role

Detection engineers help translate attacker behaviour into detection logic.

```text
Technique
    |
    v
Behaviour
    |
    v
Telemetry
    |
    v
Detection Hypothesis
    |
    v
Detection Rule
    |
    v
Test
    |
    v
Tune
    |
    v
Retest
```


---

# Threat Intelligence Role

Threat intelligence can help determine:

```text
Which adversaries matter?

Which behaviours are relevant?

Which ATT&CK techniques should be prioritised?

Which attack paths are realistic?
```


---

# Security Engineering Role

Security engineers may improve:

```text
Logging

EDR policy

Firewall rules

Identity controls

Application control

Network segmentation

Cloud monitoring

Hardening
```


---

# Exercise Types

Purple team exercises can take several forms.

```text
Technique Validation

Detection Validation

Attack-Path Exercise

Threat-Informed Exercise

Adversary Emulation

Tabletop Exercise

Detection Engineering Workshop

Continuous Security Validation
```


---

# Technique Validation

A single technique is tested.

```text
Technique
    |
    v
Execute
    |
    v
Observe
    |
    v
Detect
```

Useful for focused detection engineering.


---

# Attack-Path Exercise

Multiple techniques are chained.

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
Objective
```

This tests whether defenders can correlate activity across the complete attack path.


---

# Threat-Informed Exercise

Threat intelligence determines which techniques are selected.

```text
Threat Intelligence
       |
       v
Relevant Adversary
       |
       v
Observed Behaviours
       |
       v
ATT&CK Mapping
       |
       v
Exercise
```


---

# Collaborative Exercise

Red and blue teams communicate throughout the exercise.

```text
Execute
   |
   v
Observe
   |
   v
Discuss
   |
   v
Tune
   |
   v
Retest
```

This is particularly effective for rapid learning.


---

# Blind Phase

A purple team exercise can include a blind phase.

```text
Red Team Executes
       |
       v
Blue Team Responds Normally
       |
       v
Results Recorded
```

This provides a baseline.


---

# Collaborative Phase

After the baseline:

```text
Red Explains
     |
     v
Blue Reviews
     |
     v
Detection Tuned
     |
     v
Technique Repeated
```

This allows direct improvement.


---

# Two-Phase Model

A useful model is:

```text
PHASE 1
Baseline

Red executes.
Blue operates normally.
Interaction is limited.

        |
        v

PHASE 2
Collaboration

Red explains.
Blue investigates.
Detection is improved.
Technique is repeated.
```


---

# Exercise Scenario

An exercise should have a scenario.

Example:

```text
Scenario:

An attacker has obtained access to a standard employee
workstation.

Objective:

Determine whether the organisation can detect the attacker's
progression toward a sensitive internal application.
```


---

# Starting Position

Possible starting points include:

```text
External attacker

Compromised employee account

Assumed-breach workstation

Compromised server

Cloud test identity

Insider scenario
```

Document the starting position clearly.


---

# Scope

Define:

```text
Hosts

Networks

Domains

Applications

Cloud environments

Accounts

Techniques

Testing windows
```


---

# Out of Scope

Explicitly define:

```text
Production disruption

Destructive testing

Unapproved social engineering

Unapproved credential access

Third-party systems

Sensitive production data

Unavailable systems
```


---

# Rules of Engagement

Rules of engagement should define:

```text
Authorised techniques

Prohibited techniques

Testing hours

Communication

Escalation

Stop conditions

Emergency contacts

Data handling

Cleanup
```


---

# Stop Conditions

Examples:

```text
Unexpected service disruption

Real security incident discovered

Unintended production data access

Testing reaches an out-of-scope system

Customer requests immediate stop

Unexpected security-control instability
```


---

# Technique Selection

Select techniques based on:

```text
Threat relevance

Business risk

Detection uncertainty

Attack-path importance

Previous incidents

Control maturity

Exercise objectives
```


---

# MITRE ATT&CK

MITRE ATT&CK provides a common language for purple team exercises.

```text
Tactic
  |
  v
Technique
  |
  v
Sub-Technique
  |
  v
Procedure
```

For example:

```text
Discovery
   |
   v
Account Discovery
   |
   v
Controlled Procedure
```


---

# ATT&CK Exercise Matrix

Example:

| Phase | Technique | Objective | Expected Detection |
|---|---|---|---|
| Execution | Command Interpreter | Validate process telemetry | Endpoint alert |
| Discovery | Account Discovery | Validate discovery visibility | Behaviour detection |
| Credential Access | Credential behaviour | Validate endpoint visibility | Credential alert |
| Lateral Movement | Remote Services | Validate authentication monitoring | Lateral movement alert |


---

# ATT&CK Is Not the Objective

Avoid:

```text
We tested 50 ATT&CK techniques.
```

without context.

Prefer:

```text
We tested the techniques required to evaluate the selected
attack path and defensive capabilities.
```


---

# Procedure Design

Each procedure should define:

```text
Technique

Purpose

Preconditions

Target

Identity

Procedure

Expected system result

Expected telemetry

Expected detection

Expected response

Cleanup
```


---

# Procedure Record

Example:

```text
Test ID:
PT-001

Technique:
Account Discovery

Host:
WS01

Identity:
CORP\purple-test

Objective:
Validate visibility of account enumeration.

Expected Telemetry:
Process creation
Directory-service telemetry

Expected Detection:
Discovery activity visible to analysts

Cleanup:
None
```


---

# Test IDs

Use unique identifiers.

Example:

```text
PT-001

PT-002

PT-003
```

or:

```text
PT-T1087-001
```


---

# Time Synchronisation

Use consistent timestamps.

Prefer:

```text
UTC
```

Record:

```text
Start time

End time

Operator

Host

Identity

Technique
```


---

# Execution

During execution, the red team performs the approved procedure.

The goal should be:

```text
Minimum activity required to produce meaningful evidence.
```

Avoid unnecessary actions once the test objective has been proven.


---

# Observation

The blue team observes:

```text
Endpoint telemetry

Windows Event Logs

Linux logs

Authentication logs

Network traffic

DNS

Firewall events

Proxy events

Cloud audit logs

SIEM events

EDR alerts
```


---

# Expected Telemetry

Before executing a technique, define what should be visible.

Example:

```text
Technique:
Remote Services

Expected:

Authentication event

Source IP

Destination host

Account

Remote-service process activity

Network connection
```


---

# Telemetry Pipeline

```text
Activity
   |
   v
Event Generated
   |
   v
Collected
   |
   v
Forwarded
   |
   v
Parsed
   |
   v
Stored
   |
   v
Detection
   |
   v
Alert
```


---

# Telemetry Gap

A missing alert does not automatically mean the detection rule failed.

The event may never have reached the SIEM.

```text
No Alert
   |
   v
Telemetry Exists?
 /          \
No           Yes
|             |
v             v
Telemetry    Detection
Problem      Review
```


---

# Detection Validation

For each technique ask:

```text
Was telemetry generated?

Was it collected?

Was it parsed correctly?

Was it searchable?

Was a detection rule triggered?

Was an alert created?

Did an analyst investigate?

Was the activity correctly understood?
```


---

# Detection Result Categories

Use consistent categories.

```text
Prevented

Detected

Telemetry Only

Partially Detected

Not Detected

Not Tested
```


---

# Prevention

Example:

```text
The security control prevented the approved procedure from
executing.
```


---

# Detected

Example:

```text
The procedure completed and generated the expected high-fidelity
alert.
```


---

# Telemetry Only

Example:

```text
The activity was visible in endpoint telemetry but no dedicated
alert was generated.
```


---

# Partial Detection

Example:

```text
An alert was generated, but it did not identify the relevant
user or destination system.
```


---

# Not Detected

Example:

```text
The procedure completed without generating useful telemetry or
an actionable detection.
```


---

# Detection Hypothesis

Before testing, define a hypothesis.

Example:

```text
Account discovery performed by a standard employee workstation
should generate endpoint telemetry that can be correlated with
other discovery behaviour.
```


---

# Detection Engineering Cycle

```text
Hypothesis
    |
    v
Technique
    |
    v
Telemetry
    |
    v
Detection Rule
    |
    v
Execute
    |
    v
Evaluate
    |
    v
Tune
    |
    v
Retest
```


---

# Detection Tuning

Tuning may involve:

```text
New fields

Additional data sources

Threshold changes

Context enrichment

Asset criticality

Identity context

Parent-child relationships

Sequence correlation
```


---

# Avoid Over-Tuning

Do not create a detection that only identifies the exact test command.

For example:

```text
Detect:

whoami.exe
```

may be less useful than understanding:

```text
Why is identity discovery occurring?

Which user executed it?

Which parent process launched it?

What happened immediately before and after?
```


---

# Behaviour-Based Detection

A stronger model is:

```text
Behaviour
   |
   v
Context
   |
   v
Sequence
   |
   v
Correlation
   |
   v
Detection
```


---

# Attack-Chain Correlation

Individual events may appear legitimate.

```text
Account Discovery
      +
Network Discovery
      +
Remote Authentication
      +
Credential Access
      |
      v
Suspicious Attack Path
```

Purple teaming can help defenders identify these relationships.


---

# SOC Validation

Detection is not complete when an alert exists.

The SOC must be able to use it.

Validate:

```text
Alert received

Alert prioritised

Host identified

User identified

Technique understood

Related events found

Attack path reconstructed

Escalation performed

Response initiated
```


---

# Response Validation

Potential response actions include:

```text
Investigate host

Investigate identity

Block account

Isolate endpoint

Block network communication

Revoke token

Reset credential

Escalate incident
```

Exercise response actions should be coordinated to avoid unintended production impact.


---

# Detection Maturity

A useful maturity progression is:

```text
No Visibility
     |
     v
Raw Telemetry
     |
     v
Searchable Telemetry
     |
     v
Detection
     |
     v
Alert
     |
     v
Investigation
     |
     v
Response
     |
     v
Automated Response
```


---

# Knowledge Transfer

Purple teaming should transfer knowledge between participants.

Red team knowledge may include:

```text
Attacker objectives

Technique prerequisites

Attack-path reasoning

Alternative techniques

Privilege relationships

Credential opportunities
```

Blue team knowledge may include:

```text
Telemetry sources

SIEM architecture

Detection logic

Environmental baselines

Alert triage

Incident response
```

The goal is shared understanding.


---

# Knowledge Transfer Cycle

```text
Red Knowledge
      |
      v
Exercise
      |
      v
Blue Observation
      |
      v
Discussion
      |
      v
Shared Understanding
      |
      v
Improvement
      |
      v
Retest
```


---

# Explain the Why

A useful purple team discussion should not stop at:

```text
Run this command.
```

Instead explain:

```text
Why would an attacker perform this action?

What information does it provide?

What does the defender see?

Which data source records it?

Why is the behaviour suspicious?

How could legitimate activity look similar?
```


---

# Shared Mental Model

The objective is to move from separate perspectives:

```text
Red:

Technique -> Objective
```

and:

```text
Blue:

Event -> Alert
```

toward:

```text
Technique
   |
   v
Attacker Objective
   |
   v
System Behaviour
   |
   v
Telemetry
   |
   v
Detection
   |
   v
Response
```


---

# Learning During Exercises

Learning can occur through:

```text
Observation

Discussion

Demonstration

Hands-on practice

Detection tuning

Retesting

Reflection
```


---

# Pre-Exercise Measurement

Before an exercise, measure baseline knowledge where useful.

Possible topics:

```text
ATT&CK

Offensive techniques

Endpoint telemetry

Network telemetry

Identity monitoring

Detection engineering

Incident response
```


---

# Post-Exercise Measurement

After the exercise, repeat comparable questions.

Compare:

```text
Pre-Exercise
     |
     v
Exercise
     |
     v
Post-Exercise
```


---

# Knowledge Improvement

A simple model is:

```text
Knowledge Improvement =
Post-Exercise Result - Pre-Exercise Result
```

This should be interpreted carefully and combined with other evidence.


---

# Observation

Observers can record:

```text
Participant interaction

Questions asked

Information exchanged

Detection improvements

Decision making

Communication

Areas of confusion

Successful collaboration
```


---

# Qualitative Evidence

Useful qualitative evidence may include:

```text
Participant comments

Observer notes

After-action discussion

Detection-engineering decisions

Lessons learned

Examples of changed understanding
```


---

# Quantitative Evidence

Possible quantitative measures include:

```text
Detection rate

Telemetry coverage

Time to detect

Time to triage

Time to respond

Number of techniques validated

Number of detection gaps identified

Number of detections improved

Pre/post knowledge scores
```


---

# Detection Rate

A simple metric is:

```text
Detected Tested Techniques
--------------------------  * 100
Tested Techniques
```

This should not be treated as a complete measure of defensive capability.


---

# Telemetry Coverage

```text
Techniques With Useful Telemetry
--------------------------------  * 100
Techniques Tested
```


---

# Time to Detect

```text
TTD = Detection Time - Technique Start Time
```


---

# Time to Triage

```text
TTT = Analyst Triage Time - Detection Time
```


---

# Time to Respond

```text
TTR = Response Time - Detection Time
```


---

# Baseline vs Retest

One of the strongest purple team measurements is:

```text
Baseline
   |
   v
Gap Identified
   |
   v
Improvement
   |
   v
Retest
   |
   v
Result
```


---

# Example

Before:

```text
Technique:
Account Discovery

Telemetry:
Available

Detection:
None
```

After tuning:

```text
Technique:
Account Discovery

Telemetry:
Available

Detection:
Behaviour correlated with additional discovery activity

Alert:
Generated

SOC:
Successfully investigated
```


---

# Improvement Categories

Purple team findings may lead to improvements in:

```text
Prevention

Logging

Telemetry collection

Parsing

Detection

Alerting

Triage

Response

Architecture

Process

Training
```


---

# Gap Classification

Classify gaps precisely.

```text
Control Gap

Telemetry Gap

Collection Gap

Parsing Gap

Detection Gap

Alerting Gap

Triage Gap

Response Gap

Knowledge Gap

Process Gap
```


---

# Control Gap

```text
A preventive security control did not stop the behaviour as
expected.
```


---

# Telemetry Gap

```text
The required security event was not generated.
```


---

# Collection Gap

```text
The event existed locally but was not collected centrally.
```


---

# Parsing Gap

```text
The event reached the security platform but important fields
were not parsed correctly.
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

# Triage Gap

```text
An alert existed but analysts could not efficiently determine
what happened.
```


---

# Response Gap

```text
The activity was detected but the operational response was
insufficient or delayed.
```


---

# Knowledge Gap

```text
Participants lacked the knowledge required to understand or
investigate the behaviour.
```


---

# Process Gap

```text
Technology worked, but organisational procedures prevented an
effective response.
```


---

# Evidence

For every test record:

```text
Test ID

Technique

Host

Identity

Timestamp

Procedure

Expected result

Actual result

Expected telemetry

Observed telemetry

Expected detection

Observed detection

SOC response

Improvement

Retest result
```


---

# Example Evidence Record

```text
Test ID:
PT-007

Technique:
Remote Services

Source:
WS01

Destination:
SRV01

Identity:
CORP\purple-test

Expected:
Authentication telemetry and lateral movement alert

Observed:
Authentication telemetry available

Detection:
No alert

Improvement:
Detection rule updated to include remote authentication from
standard workstation segments

Retest:
Alert generated successfully
```


---

# Exercise Timeline

Maintain a timeline.

Example:

```text
09:00 - Exercise begins

09:10 - Execution technique tested

09:13 - Endpoint telemetry confirmed

09:20 - Discovery technique tested

09:25 - Detection gap identified

09:40 - Detection rule updated

09:50 - Technique repeated

09:51 - Alert generated

09:55 - SOC begins investigation

10:05 - Investigation completed
```


---

# Communication

Purple teaming depends heavily on communication.

Useful communication channels include:

```text
Dedicated Teams channel

Slack channel

Conference call

Exercise room

Shared timeline

Shared test tracker
```


---

# Exercise Controller

For larger exercises, designate an exercise controller.

Responsibilities may include:

```text
Maintain scope

Track exercise progress

Record timestamps

Coordinate red and blue teams

Manage stop conditions

Resolve deconfliction

Track evidence
```


---

# Observer

An observer can record:

```text
Participant interaction

Knowledge exchange

Decision making

Communication quality

Confusion

Detection changes

Learning outcomes
```

The observer should avoid unnecessarily influencing the exercise.


---

# Facilitator

A facilitator can help maintain productive collaboration.

```text
Red
 |
 +--------+
          |
      Facilitator
          |
 +--------+
 |
Blue
```

The facilitator may help translate offensive and defensive terminology.


---

# Exercise Cadence

A collaborative exercise may use short cycles.

For example:

```text
Technique
   |
   v
Execute
   |
   v
Observe
   |
   v
Discuss
   |
   v
Improve
   |
   v
Retest
```

Then move to the next technique.


---

# Technique Cards

A useful exercise artefact is a technique card.

Example:

```text
Technique:
Account Discovery

ATT&CK:
T1087

Objective:
Validate account discovery visibility.

Preconditions:
Standard employee workstation.

Expected Telemetry:
Process creation
Directory-service activity

Expected Detection:
Discovery activity visible to SOC.

Red Team:
Execute approved procedure.

Blue Team:
Locate and analyse telemetry.

Learning Objective:
Understand which data sources reveal account discovery.

Cleanup:
None.
```


---

# Purple Team Matrix

| Technique | Prevented | Telemetry | Detection | SOC Response | Retest |
|---|---:|---:|---:|---:|---:|
| Execution | No | Yes | Yes | Yes | Pass |
| Account Discovery | No | Yes | No | No | Pass |
| Credential Access | Yes | Yes | Yes | Yes | Pass |
| Remote Services | No | Yes | Partial | Partial | Pending |


---

# ATT&CK Coverage

Purple team coverage should distinguish:

```text
Mapped

Planned

Executed

Telemetry Confirmed

Detected

Responded

Retested
```

Do not mark a technique as covered merely because a detection rule references its ATT&CK ID.


---

# Coverage Model

```text
Mapped
  |
  v
Planned
  |
  v
Tested
  |
  v
Observed
  |
  v
Detected
  |
  v
Responded
  |
  v
Retested
```


---

# Coverage Colours

If using an ATT&CK heatmap, define the meaning.

Example:

```text
Green:
Tested and expected detection confirmed.

Yellow:
Telemetry available but detection incomplete.

Red:
Tested without useful detection.

Grey:
Not tested.
```


---

# Avoid Vanity Metrics

Metrics such as:

```text
500 ATT&CK techniques mapped
```

may look impressive but provide little evidence of operational effectiveness.

Prefer:

```text
12 high-priority techniques tested.

10 produced useful telemetry.

8 generated actionable detections.

6 resulted in successful SOC investigation.

4 detection gaps were remediated and successfully retested.
```


---

# Purple Team Reporting

Reporting should focus on improvement.

A useful structure is:

```text
Executive Summary

Exercise Objectives

Scope

Scenario

Participants

Techniques Tested

Attack Path

Prevention Results

Telemetry Results

Detection Results

Response Results

Knowledge Transfer

Improvements

Retest Results

Remaining Gaps

Recommendations
```


---

# Positive Findings

Document successful controls.

Examples:

```text
EDR prevented execution.

Application control blocked the procedure.

Network segmentation prevented lateral movement.

Authentication telemetry identified the source account.

SOC correctly correlated multiple attack stages.

Containment occurred before the objective was reached.
```


---

# Finding Example

```text
Title:
Account Discovery Activity Is Logged but Not Detected

Technique:
T1087 - Account Discovery

Observation:
The approved account-discovery procedure generated process
creation telemetry on the test workstation.

The events were successfully forwarded to the SIEM.

No detection rule generated an alert during the baseline phase.

Improvement:
Detection logic was introduced to correlate unusual account
discovery with additional host discovery activity.

Retest:
The same approved procedure generated the expected alert.

Result:
Detection improved from Telemetry Only to Detected.
```


---

# Knowledge Transfer Finding

Example:

```text
Observation:

During the baseline phase, analysts initially identified the
individual process events but did not associate them with an
attacker discovery sequence.

During the collaborative phase, the red team explained the
purpose and sequence of the discovery actions.

Following discussion and detection tuning, the blue team
successfully identified the repeated activity as a related
discovery sequence during retesting.
```


---

# After-Action Review

After the exercise, review:

```text
What worked?

What failed?

What surprised participants?

What was learned?

Which controls improved?

Which detections improved?

Which gaps remain?

What should be tested next?
```


---

# Lessons Learned

Convert observations into reusable knowledge.

```text
Exercise Observation
       |
       v
Lesson Learned
       |
       v
Document
       |
       v
Control Improvement
       |
       v
Future Exercise
```


---

# Continuous Improvement

Purple teaming should not be a one-time event.

```text
Exercise
   |
   v
Find Gap
   |
   v
Improve
   |
   v
Retest
   |
   v
Monitor
   |
   v
New Threat
   |
   v
Next Exercise
```


---

# Continuous Validation

High-value tests can become repeatable validation procedures.

Examples:

```text
Critical identity attacks

Lateral movement

Privilege escalation

Cloud privilege changes

Suspicious PowerShell

Credential access

Ransomware precursors
```


---

# Detection Regression Testing

When detections change:

```text
Known Procedure
      |
      v
Execute
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

This helps identify detection regressions.


---

# Purple Team Test Library

Maintain a reusable library.

Example:

| Test ID | ATT&CK | Platform | Detection | Last Result |
|---|---|---|---|---|
| PT-001 | T1087 | Windows | Account Discovery | Pass |
| PT-002 | T1016 | Windows | Network Discovery | Pass |
| PT-003 | T1021 | Windows | Remote Services | Partial |


---

# Test Library Fields

Useful fields include:

```text
Test ID

Technique

Sub-Technique

Platform

Objective

Preconditions

Procedure

Expected Telemetry

Expected Detection

Cleanup

Last Test

Last Result

Owner
```


---

# Tooling

Purple team exercises may use:

```text
Native operating system commands

PowerShell

Atomic Red Team

MITRE CALDERA

BloodHound

NetExec

Impacket

Nmap

SIEM

EDR

Sigma
```

Tool selection should follow the exercise objective.


---

# Atomic Red Team

Atomic Red Team provides small ATT&CK-mapped tests.

A useful workflow is:

```text
Select Technique
      |
      v
Review Atomic Test
      |
      v
Review Dependencies
      |
      v
Review Cleanup
      |
      v
Execute Approved Test
      |
      v
Validate Telemetry
      |
      v
Validate Detection
```

Do not bulk-execute tests against production systems without review.


---

# MITRE CALDERA

CALDERA can support repeatable adversary emulation.

It can model:

```text
Adversaries

Abilities

Operations

Agents

Objectives
```

Automation should remain tightly scoped.


---

# Sigma

Sigma can help express detection logic in a platform-independent format.

Example concept:

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

This is only an illustrative example.

Production detection should consider environment, context, sequence and false positives.


---

# Purple Team Data Sources

Common sources include:

```text
Windows Event Logs

Sysmon

PowerShell Operational Logs

Microsoft Defender

EDR

Linux audit logs

systemd journal

Authentication logs

Active Directory

DNS

Firewall

Proxy

IDS / IPS

Cloud audit logs

Email security

Application logs
```


---

# Windows Detection Validation

Potential areas include:

```text
Process creation

PowerShell

Authentication

Scheduled tasks

Services

Account changes

Group membership

Remote access

Defender events

AppLocker

WDAC

Sysmon
```


---

# Linux Detection Validation

Potential areas include:

```text
Process execution

sudo

SSH

Authentication

Cron

systemd

User creation

Group changes

Network connections

File modifications

auditd
```


---

# Active Directory Detection Validation

Potential areas include:

```text
Authentication

Kerberos

NTLM

Group membership

Directory changes

Delegation

ACL changes

Certificate Services

Remote administration

Replication activity
```


---

# Cloud Detection Validation

Potential areas include:

```text
Authentication

MFA

Role assignments

Privilege changes

API activity

Application consent

Service principals

Storage access

Network changes

Audit logging
```


---

# Purple Team and Security Architecture

Purple teaming can reveal architectural issues such as:

```text
Flat networks

Weak administrative boundaries

Shared credentials

Excessive privilege

Missing telemetry

Poor identity separation

Weak application control
```

These may require architectural rather than detection-only remediation.


---

# Purple Team and Threat Hunting

Exercise telemetry can become hunting hypotheses.

```text
Technique
   |
   v
Observed Behaviour
   |
   v
Detection Logic
   |
   v
Historical Search
   |
   v
Threat Hunt
```

This helps determine whether similar activity has previously occurred.


---

# Purple Team and Incident Response

Purple team exercises can validate whether incident responders can:

```text
Identify affected systems

Identify affected identities

Determine attack progression

Contain compromised hosts

Disable accounts

Revoke sessions

Preserve evidence

Coordinate escalation
```


---

# Purple Team and Red Teaming

Red team findings can become purple team validation scenarios.

```text
Red Team Finding
      |
      v
Attack Path
      |
      v
Purple Team Exercise
      |
      v
Detection Improvement
      |
      v
Retest
```


---

# Purple Team and Penetration Testing

A penetration testing finding can also become a detection exercise.

Example:

```text
Weak Service Permission
       |
       v
Privilege Escalation Path
       |
       v
Remediation
       |
       v
Purple Team Validation
       |
       v
Can Similar Behaviour Be Detected?
```


---

# Purple Team and Vulnerability Management

Purple teaming helps prioritise vulnerabilities based on attack-path relevance.

```text
Vulnerability
    |
    v
Exploitable?
    |
    v
Attack Path?
    |
    v
Detection?
    |
    v
Business Impact?
```

This provides more context than severity scores alone.


---

# Common Purple Team Failure Modes

## No Clear Objective

```text
Let's run some attacks.
```

This produces activity without meaningful measurement.


---

## No Baseline

If the detection is changed before the original capability is measured, improvement cannot be demonstrated.


---

## Red Dominates the Exercise

Purple teaming should not become a red team demonstration with passive blue-team observers.


---

## Blue Dominates the Exercise

Purple teaming should not become only a detection workshop without realistic attacker behaviour.


---

## Too Many Techniques

Testing too many techniques can reduce learning quality.

Prefer:

```text
Fewer Techniques

More Observation

More Discussion

More Improvement

More Retesting
```


---

## No Retesting

Without retesting:

```text
Gap
 |
 v
Fix
 |
 v
Assumed Success
```

With retesting:

```text
Gap
 |
 v
Fix
 |
 v
Retest
 |
 v
Evidence
```


---

## Tool-Focused Testing

Avoid designing the exercise around:

```text
Can we detect Tool X?
```

Prefer:

```text
Can we detect Behaviour X?
```


---

## No Knowledge Capture

If knowledge remains only with participants:

```text
Exercise
   |
   v
People Learn
   |
   v
People Leave
   |
   v
Knowledge Lost
```

Document reusable lessons.


---

# Purple Team Checklist

## Planning

- [ ] Business objective defined
- [ ] Security objective defined
- [ ] Learning objectives defined
- [ ] Scenario defined
- [ ] Scope approved
- [ ] Out-of-scope systems documented
- [ ] Starting position defined
- [ ] Participants identified
- [ ] Roles assigned
- [ ] Rules of engagement approved
- [ ] Stop conditions defined
- [ ] Communication channel defined

## Threat Modelling

- [ ] Relevant threats reviewed
- [ ] Attack paths identified
- [ ] ATT&CK techniques selected
- [ ] Technique relevance documented
- [ ] High-risk behaviours prioritised

## Test Design

- [ ] Test IDs assigned
- [ ] Preconditions documented
- [ ] Procedures reviewed
- [ ] Expected results documented
- [ ] Expected telemetry documented
- [ ] Expected detections documented
- [ ] Expected responses documented
- [ ] Cleanup requirements documented

## Baseline

- [ ] Current detection capability recorded
- [ ] Existing telemetry confirmed
- [ ] Existing rules reviewed
- [ ] Baseline measurements captured
- [ ] Pre-exercise knowledge measurement completed where relevant

## Execution

- [ ] Correct host confirmed
- [ ] Correct identity confirmed
- [ ] Scope revalidated
- [ ] Timestamp recorded
- [ ] Approved procedure executed
- [ ] Result recorded
- [ ] Unexpected impact checked

## Telemetry

- [ ] Endpoint telemetry reviewed
- [ ] Identity telemetry reviewed
- [ ] Network telemetry reviewed
- [ ] Cloud telemetry reviewed
- [ ] SIEM ingestion confirmed
- [ ] Parsing validated

## Detection

- [ ] Prevention result recorded
- [ ] Detection result recorded
- [ ] Alert result recorded
- [ ] Detection quality assessed
- [ ] False-positive considerations reviewed
- [ ] Attack-chain correlation reviewed

## Response

- [ ] SOC received relevant alerts
- [ ] Analyst triage recorded
- [ ] Source identified
- [ ] Destination identified
- [ ] Identity identified
- [ ] Related activity correlated
- [ ] Escalation assessed
- [ ] Response assessed

## Collaboration

- [ ] Red team explained attacker objective
- [ ] Blue team explained observed telemetry
- [ ] Detection engineers participated where needed
- [ ] Questions recorded
- [ ] Knowledge gaps recorded
- [ ] Shared understanding developed

## Improvement

- [ ] Gap classified
- [ ] Root cause identified
- [ ] Improvement implemented
- [ ] Detection tuned
- [ ] Logging improved where required
- [ ] Process changes recorded

## Retesting

- [ ] Original procedure repeated
- [ ] Preconditions reproduced
- [ ] New telemetry confirmed
- [ ] Detection confirmed
- [ ] Response confirmed
- [ ] Result documented

## Learning

- [ ] Lessons learned captured
- [ ] Participant feedback captured
- [ ] Post-exercise knowledge measured where relevant
- [ ] Knowledge improvement reviewed
- [ ] Documentation updated

## Reporting

- [ ] Objectives documented
- [ ] Techniques documented
- [ ] Attack path documented
- [ ] Positive controls documented
- [ ] Gaps documented
- [ ] Improvements documented
- [ ] Retest results documented
- [ ] Remaining risks documented

## Continuous Improvement

- [ ] High-value tests added to test library
- [ ] Detection regression tests identified
- [ ] Owners assigned
- [ ] Future exercises planned
- [ ] Outstanding gaps tracked


---

# Exercise Decision Model

```text
                  BUSINESS OBJECTIVE
                         |
                         v
                  SECURITY OBJECTIVE
                         |
                         v
                    THREAT MODEL
                         |
                         v
                  SELECT TECHNIQUE
                         |
                         v
                    IN SCOPE?
                    /      \
                  No        Yes
                  |          |
                 Skip        v
                       SAFE TO TEST?
                         /      \
                       No        Yes
                       |          |
                    Simulate      v
                              BASELINE
                                 |
                                 v
                              EXECUTE
                                 |
                                 v
                              OBSERVE
                                 |
                                 v
                              DETECT
                                 |
                                 v
                              RESPOND
                                 |
                                 v
                              IMPROVE
                                 |
                                 v
                               RETEST
```


---

# Detection Decision Model

```text
                     TEST ACTIVITY
                          |
                          v
                     PREVENTED?
                      /       \
                    Yes        No
                    |           |
                    v           v
                Document    TELEMETRY?
                              /      \
                            No        Yes
                            |          |
                            v          v
                     Telemetry Gap   COLLECTED?
                                      /      \
                                    No        Yes
                                    |          |
                                    v          v
                             Collection Gap  PARSED?
                                             /     \
                                           No       Yes
                                           |         |
                                           v         v
                                      Parsing Gap  DETECTED?
                                                  /        \
                                                No          Yes
                                                |            |
                                                v            v
                                         Detection Gap    ALERT?
                                                         /      \
                                                       No        Yes
                                                       |          |
                                                       v          v
                                                Alerting Gap   RESPONSE?
                                                               /       \
                                                             No         Yes
                                                             |           |
                                                             v           v
                                                      Response Gap    Success
```


---

# Knowledge Transfer Model

```text
                 OFFENSIVE KNOWLEDGE
                         |
                         v
                      EXERCISE
                         |
                         v
                 DEFENSIVE OBSERVATION
                         |
                         v
                     DISCUSSION
                         |
             +-----------+-----------+
             |                       |
             v                       v
       RED EXPLAINS              BLUE EXPLAINS
       ATTACK LOGIC              TELEMETRY
             |                       |
             +-----------+-----------+
                         |
                         v
                  SHARED UNDERSTANDING
                         |
                         v
                     IMPROVEMENT
                         |
                         v
                       RETEST
                         |
                         v
                 ORGANISATIONAL LEARNING
```


---

# Purple Team Maturity Model

```text
Level 1
Ad-hoc collaboration between red and blue teams

Level 2
Structured exercises with ATT&CK mapping and documented
objectives

Level 3
Repeatable exercises with telemetry and detection validation

Level 4
Measured knowledge transfer, attack-path validation and
continuous detection improvement

Level 5
Threat-informed continuous security validation integrated with
detection engineering, incident response and organisational
learning
```


---

# Final Purple Team Model

```text
                       THREAT
                         |
                         v
                  BUSINESS OBJECTIVE
                         |
                         v
                  SECURITY OBJECTIVE
                         |
                         v
                  LEARNING OBJECTIVE
                         |
                         v
                    ATT&CK MAP
                         |
                         v
                    TEST DESIGN
                         |
             +-----------+-----------+
             |                       |
             v                       v
          RED TEAM                BLUE TEAM
             |                       |
             v                       v
          EXECUTE                  OBSERVE
             |                       |
             +-----------+-----------+
                         |
                         v
                      TELEMETRY
                         |
                         v
                      DETECTION
                         |
                         v
                       ALERT
                         |
                         v
                      RESPONSE
                         |
                         v
                    COLLABORATE
                         |
                         v
                     UNDERSTAND
                         |
                         v
                      IMPROVE
                         |
                         v
                       RETEST
                         |
                         v
                       MEASURE
                         |
                         v
                       LEARN
                         |
                         v
                      DOCUMENT
                         |
                         v
                 CONTINUOUS VALIDATION
```


---

# Core Principle

Purple teaming can be reduced to:

```text
Define the business objective.

Define what participants should learn.

Select relevant attacker behaviour.

Map behaviour to ATT&CK where useful.

Establish a baseline.

Execute the minimum required test.

Observe the defender's view.

Validate telemetry before judging detection.

Separate prevention from detection.

Separate detection from response.

Explain attacker decision making.

Explain defensive telemetry.

Encourage direct red-blue collaboration.

Identify the actual gap.

Improve the control.

Repeat the same test.

Measure whether capability improved.

Capture knowledge.

Convert useful tests into repeatable validation.

Repeat the cycle.
```


---

# Related Notes

## Purple Teaming

Planned detailed pages:

```text
purple-teaming/methodology.md

purple-teaming/exercises.md

purple-teaming/detection-engineering.md

purple-teaming/mitre-attack.md

purple-teaming/knowledge-transfer.md

purple-teaming/metrics-and-measurement.md

purple-teaming/after-action-review.md

purple-teaming/continuous-validation.md
```


## Red Teaming

- [Red Teaming](../red-teaming/)
- [Red Team Methodology](../red-teaming/methodology.md)
- [Adversary Emulation](../red-teaming/adversary-emulation.md)
- [Detection Validation](../red-teaming/detection-validation.md)
- [Red Team Reporting](../red-teaming/reporting.md)


## Operating Systems

- [Windows](../windows/)
- [Linux](../linux/)


## Active Directory

- [Active Directory](../active-directory/)
- [BloodHound](../active-directory/bloodhound.md)


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [MITRE Center for Threat-Informed Defense](https://ctid.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Red Canary - Atomic Red Team](https://redcanary.com/atomic-red-team/){ target="_blank" rel="noopener noreferrer" }
- [Sigma](https://sigmahq.io/){ target="_blank" rel="noopener noreferrer" }
- [SigmaHQ](https://github.com/SigmaHQ/sigma){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Retesting is what turns testing into improvement"
    Identifying a detection gap is useful, but repeating the same controlled procedure after the control has been improved provides evidence that the change actually works.


!!! tip "Share reasoning, not only commands"
    One of the most valuable parts of purple teaming is explaining why an attacker performs an action and why a defender interprets the resulting telemetry in a particular way. This helps transfer knowledge that cannot be captured by tool output alone.


!!! warning "Do not measure purple teaming only by ATT&CK coverage"
    A large number of mapped techniques does not prove defensive capability. Prioritise meaningful threat scenarios and distinguish techniques that are mapped, executed, observed, detected, responded to and successfully retested.
