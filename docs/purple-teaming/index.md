---
title: Purple Teaming
description: Practical purple teaming methodology covering collaborative security testing, adversary emulation, detection engineering, MITRE ATT&CK, knowledge transfer, measurement, after-action reviews and continuous validation.
---

# Purple Teaming

Purple teaming is a collaborative security-testing approach in which offensive and defensive security teams work together to improve an organisation's ability to prevent, detect, investigate and respond to adversary behavior.

Rather than treating red and blue teams as isolated functions:

```text
Traditional Model

Red Team                         Blue Team
    |                                |
    v                                v
Attack                           Defend
    |                                |
    +------------ Limited -----------+
                 Feedback
```

purple teaming creates an active feedback loop:

```text
Purple Teaming

Red Team
   |
   v
Execute Technique
   |
   v
Blue Team Observes
   |
   v
Telemetry Reviewed
   |
   v
Detection Evaluated
   |
   v
Feedback Shared
   |
   v
Detection Improved
   |
   v
Technique Repeated
   |
   v
Improvement Validated
```

The objective is not simply to determine whether an attacker can succeed.

The objective is to understand:

```text
What happened?

What was visible?

What was detected?

What was missed?

Why was it missed?

What did participants learn?

What should change?

Did the change work?

Will it continue working?
```

---

# Purple Teaming Knowledge Base

This section is organised around nine core areas.

```text
Purple Teaming
│
├── Methodology
│
├── Exercises
│
├── Detection Engineering
│
├── MITRE ATT&CK
│
├── Knowledge Transfer
│
├── Metrics and Measurement
│
├── After-Action Review
│
└── Continuous Validation
```

Each area represents part of the purple team improvement lifecycle.

---

# 1. Methodology

[Purple Teaming Methodology](methodology.md)

The methodology defines how purple team activities are planned, executed, reviewed and improved.

Topics include:

```text
Objectives

Scope

Roles

Rules of engagement

Scenario selection

Technique selection

Exercise preparation

Execution

Observation

Feedback

Improvement

Retesting

Lessons learned
```

A structured methodology helps make exercises repeatable rather than dependent on individual operators.

---

# 2. Exercises

[Purple Team Exercises](exercises.md)

Exercises provide the practical environment in which offensive and defensive teams collaborate.

Topics include:

```text
Exercise objectives

Scenario design

Exercise preparation

Participants

Facilitation

Attack execution

Defensive observation

Feedback cycles

Evidence collection

Exercise safety

Retesting
```

The exercise should produce measurable security improvement rather than simply demonstrate offensive capability.

---

# 3. Detection Engineering

[Detection Engineering](detection-engineering.md)

Detection engineering connects adversary behavior to observable telemetry and actionable detection logic.

```text
Adversary Behavior
       |
       v
Telemetry
       |
       v
Data Collection
       |
       v
Detection Logic
       |
       v
Alert
       |
       v
Investigation
       |
       v
Response
```

Topics include:

```text
Detection requirements

Telemetry

Data sources

Detection logic

Rule development

Detection testing

False positives

Detection tuning

ATT&CK mapping

Validation

Regression testing
```

Purple teaming provides an effective environment for validating this complete chain.

---

# 4. MITRE ATT&CK

[MITRE ATT&CK](mitre-attack.md)

MITRE ATT&CK provides a shared vocabulary for describing adversary behavior.

It can help structure:

```text
Threat intelligence

Exercise planning

Technique selection

Adversary emulation

Detection engineering

Coverage analysis

Reporting

Validation
```

A simplified relationship is:

```text
Threat
  |
  v
ATT&CK Technique
  |
  v
Purple Team Test
  |
  v
Telemetry
  |
  v
Detection
  |
  v
Validation
```

ATT&CK should support the testing methodology rather than replace evidence-based validation.

---

# 5. Knowledge Transfer

[Knowledge Transfer](knowledge-transfer.md)

Purple teaming is fundamentally a learning activity.

Exercise findings should be converted into reusable organisational knowledge.

```text
Exercise
   |
   v
Observation
   |
   v
Explanation
   |
   v
Knowledge Transfer
   |
   v
Operational Knowledge
   |
   v
Application
```

Knowledge may need to move between:

```text
Red Team

Blue Team

SOC

Detection Engineering

Incident Response

Security Engineering

Platform Teams

Identity Teams

Cloud Teams

Application Teams
```

The objective is to reduce knowledge isolation and ensure that lessons survive beyond the exercise.

---

# 6. Metrics and Measurement

[Metrics and Measurement](metrics-and-measurement.md)

Purple team programmes need evidence that security capability is improving.

Useful measurements may include:

```text
Technique execution success

Prevention success

Telemetry availability

Detection success

Time to detect

Time to triage

Time to investigate

Response performance

Knowledge improvement

Action completion

Retest success

Regression rate
```

Metrics should explain capability rather than simply create impressive numbers.

---

# 7. After-Action Review

[After-Action Review](after-action-review.md)

The after-action review converts exercise observations into structured improvement.

```text
Exercise
   |
   v
Evidence
   |
   v
Review
   |
   v
Root Cause
   |
   v
Lesson
   |
   v
Action
   |
   v
Owner
   |
   v
Retest
```

The review should answer:

```text
What was expected?

What actually happened?

Why was there a difference?

What worked?

What failed?

What did we learn?

What should change?

Who owns the improvement?

How will the improvement be validated?
```

A lesson is not fully learned merely because it appears in an exercise report.

---

# 8. Continuous Validation

[Continuous Validation](continuous-validation.md)

Continuous validation converts important purple team tests into repeatable security checks.

```text
Exercise
   |
   v
Finding
   |
   v
Improvement
   |
   v
Retest
   |
   v
Reusable Test
   |
   v
Continuous Validation
   |
   v
Regression Detection
```

This helps organisations identify when previously successful controls stop working because of environmental changes.

Examples include:

```text
EDR upgrades

SIEM changes

Parser changes

Detection modifications

Logging changes

Operating system upgrades

Cloud configuration changes
```

---

# Purple Teaming Lifecycle

The complete lifecycle can be represented as:

```text
Threat Intelligence
        |
        v
Objectives
        |
        v
Scope
        |
        v
Scenario Selection
        |
        v
ATT&CK Mapping
        |
        v
Exercise Preparation
        |
        v
Technique Execution
        |
        v
Telemetry Observation
        |
        v
Detection Evaluation
        |
        v
Investigation
        |
        v
Feedback
        |
        v
Improvement
        |
        v
Retest
        |
        v
Knowledge Transfer
        |
        v
After-Action Review
        |
        v
Metrics
        |
        v
Continuous Validation
        |
        +-------------------------+
        |                         |
        v                         |
New Threat Intelligence           |
        |                         |
        +-------------------------+
```

Purple teaming should therefore be viewed as an improvement cycle rather than a single event.

---

# Red, Blue and Purple Teams

## Red Team

The red team represents the offensive perspective.

Typical responsibilities include:

```text
Adversary emulation

Technique execution

Attack-path testing

Security-control testing

Evidence collection

Explaining offensive behavior
```

---

## Blue Team

The blue team represents the defensive perspective.

Typical responsibilities include:

```text
Monitoring

Telemetry analysis

Detection

Investigation

Incident response

Security engineering

Control improvement
```

---

## Purple Team

Purple teaming connects these capabilities.

```text
              Purple Team
             /           \
            /             \
           v               v
      Red Team          Blue Team
           \               /
            \             /
             v           v
              Collaboration
                   |
                   v
               Feedback
                   |
                   v
              Improvement
```

Purple does not necessarily need to be a separate permanent team.

It may instead represent:

```text
A process

A working model

A facilitated exercise

A collaborative security programme
```

---

# Purple Teaming Versus Red Teaming

Red teaming and purple teaming have related but different objectives.

| Red Teaming | Purple Teaming |
|---|---|
| Tests security from an adversary perspective | Improves security through collaboration |
| Often limits defender knowledge during execution | Encourages controlled information sharing |
| Measures whether objectives can be achieved | Measures and improves defensive capability |
| May emphasise realistic attack paths | May repeat techniques for learning |
| Detection may be evaluated afterwards | Detection can be improved during the exercise |
| Feedback often occurs after operations | Feedback can occur continuously |

Purple teaming does not replace red teaming.

The approaches can support each other.

---

# Purple Teaming Versus Penetration Testing

Penetration testing commonly focuses on identifying and demonstrating vulnerabilities.

```text
Asset
  |
  v
Vulnerability
  |
  v
Validation
  |
  v
Impact
  |
  v
Remediation
```

Purple teaming focuses more directly on defensive capability.

```text
Adversary Behavior
       |
       v
Security Controls
       |
       v
Telemetry
       |
       v
Detection
       |
       v
Investigation
       |
       v
Response
       |
       v
Improvement
```

A penetration test finding can become input for a later purple team exercise.

---

# Purple Teaming Versus Breach and Attack Simulation

Breach and attack simulation platforms can automate security-control testing.

They can provide:

```text
Repeatability

Frequent testing

Technique coverage

Automated validation
```

Purple teaming additionally emphasises:

```text
Human collaboration

Context

Knowledge transfer

Investigation

Root cause analysis

Detection engineering

Organisational learning
```

Automation can support a purple team programme but should not be treated as a complete replacement for it.

---

# Threat-Informed Purple Teaming

Purple team exercises should ideally be informed by threats relevant to the organisation.

Potential inputs include:

```text
Threat intelligence

Incident history

Red team findings

Penetration-test findings

Vulnerability assessments

Industry threats

Business-critical assets

Technology stack

External exposure
```

The process can be:

```text
Threat Intelligence
        |
        v
Relevant Adversary Behavior
        |
        v
ATT&CK Mapping
        |
        v
Exercise Scenario
        |
        v
Security Validation
```

This helps prioritise realistic behavior rather than simply testing techniques because they are available.

---

# Exercise Objectives

Before testing begins, define what the exercise is intended to answer.

Examples:

```text
Can the selected technique execute?

Does the preventive control block it?

Is telemetry generated?

Does telemetry reach the SIEM?

Does the detection trigger?

Does the SOC investigate correctly?

Does the response process work?

Can the teams improve the control together?
```

Clear objectives make the result easier to interpret.

---

# Scope

Define:

```text
Systems

Applications

Networks

Cloud environments

Accounts

Techniques

Tools

Testing windows

Excluded systems
```

The scope should be understood by all relevant participants.

---

# Rules of Engagement

Rules of engagement may define:

```text
Authorised activities

Prohibited activities

Testing windows

Safety restrictions

Escalation contacts

Stop conditions

Data handling

Cleanup requirements
```

Purple team collaboration does not remove the need for formal authorisation.

---

# Exercise Safety

Purple team exercises should minimise unnecessary operational risk.

Potential controls include:

```text
Dedicated test accounts

Dedicated validation endpoints

Known test infrastructure

Rate limits

Approved payloads

Defined cleanup

Rollback procedures

Emergency stop process
```

The test should be proportionate to the objective.

---

# Technique Selection

Select techniques based on:

```text
Threat relevance

Business risk

Existing detection coverage

Previous findings

Critical assets

Known control gaps

Learning objectives
```

Avoid selecting techniques solely to maximise ATT&CK coverage.

---

# Technique Decomposition

A technique should be understood as behavior rather than only a tool.

```text
Technique
   |
   +---- Preconditions
   |
   +---- Procedure
   |
   +---- Observable Behavior
   |
   +---- Telemetry
   |
   +---- Detection
   |
   +---- Prevention
   |
   +---- Investigation
```

This makes the exercise more transferable.

---

# Exercise Execution

A simple purple team cycle is:

```text
Red Executes
     |
     v
Blue Observes
     |
     v
Result Discussed
     |
     v
Control Improved
     |
     v
Red Repeats
     |
     v
Blue Validates
```

This cycle may occur multiple times during the same exercise.

---

# Feedback Cycles

Short feedback cycles are one of the defining characteristics of purple teaming.

Example:

```text
Attempt 1

Technique succeeds
Detection fails
      |
      v
Teams investigate
      |
      v
Detection modified
      |
      v
Attempt 2

Technique succeeds
Detection succeeds
```

The improvement should then be documented and retained.

---

# Evidence Collection

Capture enough evidence to explain the result.

Potential evidence includes:

```text
Technique

Timestamp

Target

User context

Execution result

Preventive-control result

Endpoint telemetry

SIEM telemetry

Detection result

Alert

Investigation

Response

Configuration changes

Retest result
```

Evidence quality is essential for defensible conclusions.

---

# Testing the Complete Defensive Chain

A strong purple team exercise should determine where the defensive chain succeeds or fails.

```text
Adversary Behavior
       |
       v
Endpoint Activity
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
Parsing
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
Response
```

A failure at one layer should not automatically be attributed to another.

---

# Prevention

Ask:

```text
Was the technique attempted?

Did it execute?

Was it blocked?

Which control blocked it?

Was the block expected?

Was evidence generated?
```

A failed attack command is not automatically proof of effective prevention.

---

# Telemetry

Ask:

```text
Was relevant telemetry generated?

Was it collected?

Was it forwarded?

Was it parsed?

Were required fields populated?

Was latency acceptable?
```

Detection engineering depends on usable telemetry.

---

# Detection

Ask:

```text
Did the analytic evaluate the behavior?

Did it match?

Was an alert generated?

Was severity appropriate?

Was ATT&CK mapping accurate?

Did the alert contain useful context?
```

See [Detection Engineering](detection-engineering.md).

---

# Investigation

Detection alone is not the final objective.

Validate whether analysts can determine:

```text
What happened?

Which host was involved?

Which account was involved?

What process or activity occurred?

What happened before?

What happened afterwards?

Is the activity malicious?

What should happen next?
```

---

# Response

Where the exercise includes response validation, evaluate:

```text
Escalation

Containment

Evidence preservation

Communication

Decision-making

Recovery

Documentation
```

Response activities should follow agreed exercise safety constraints.

---

# Feedback

Purple teaming depends on useful feedback.

Weak feedback:

```text
The detection did not work.
```

Better feedback:

```text
The endpoint generated the expected process event, but the
SIEM parser did not populate the field required by the detection.
```

The second statement supports investigation and improvement.

---

# Improvement

Improvements may include:

```text
New telemetry

Parser correction

Detection rule

Detection tuning

Dashboard

SOC query

Runbook

Security configuration

Training

Architecture change

Process change
```

Not every exercise finding requires a new detection rule.

---

# Retesting

After an improvement:

```text
Repeat the original test.
```

Then compare:

```text
Before

vs

After
```

Example:

| Stage | Before | After |
|---|---|---|
| Technique | Successful | Successful |
| Telemetry | Available | Available |
| Detection | Failed | Successful |
| Alert | None | Generated |
| Investigation | Not possible | Successful |

Retesting provides evidence that the improvement worked.

---

# Knowledge Transfer

Exercise knowledge should not remain only with the participants.

```text
Exercise Knowledge
       |
       v
Document
       |
       v
Explain
       |
       v
Demonstrate
       |
       v
Practice
       |
       v
Apply
       |
       v
Retain
```

See [Knowledge Transfer](knowledge-transfer.md).

---

# Measurement

Measure outcomes that demonstrate capability.

Examples:

```text
Detection success

Telemetry availability

Time to detect

Time to investigate

Retest success

Knowledge improvement

Action completion

Regression rate
```

See [Metrics and Measurement](metrics-and-measurement.md).

---

# After-Action Review

After the exercise:

```text
Expected
   |
   v
Observed
   |
   v
Difference
   |
   v
Root Cause
   |
   v
Lesson
   |
   v
Action
   |
   v
Owner
   |
   v
Retest
```

See [After-Action Review](after-action-review.md).

---

# Continuous Validation

Important successfully retested scenarios should be considered for recurring validation.

```text
Exercise
   |
   v
Gap
   |
   v
Fix
   |
   v
Retest
   |
   v
Pass
   |
   v
Reusable Test
   |
   v
Continuous Validation
```

See [Continuous Validation](continuous-validation.md).

---

# Purple Team Exercise Record

A practical record may contain:

```text
Exercise ID:

Date:

Objective:

Scope:

Participants:

Technique:

ATT&CK Mapping:

Prerequisites:

Expected Result:

Observed Result:

Preventive Control:

Telemetry:

Detection:

Alert:

Investigation:

Response:

Root Cause:

Improvement:

Retest:

Knowledge Transfer:

Owner:

Status:
```

This creates a reusable record of the exercise.

---

# Practical Validation Model

Use the following model when documenting technical purple team tests:

```text
Prerequisites
     |
     v
Test Procedure
     |
     v
Representative Result
     |
     v
Interpretation
     |
     v
Positive Result
     |
     v
Negative Result
     |
     v
False Positives
     |
     v
Further Validation
     |
     v
Evidence
     |
     v
Conclusion
     |
     v
Remediation
     |
     v
Retest
```

This makes the conclusion traceable to evidence.

---

# Example Purple Team Scenario

## Objective

Validate whether the organisation can detect a selected execution technique.

---

## Expected Behavior

```text
Controlled Technique
       |
       v
Endpoint Telemetry
       |
       v
SIEM
       |
       v
Detection
       |
       v
SOC Alert
```

---

## Attempt 1

Observed:

```text
Technique:
Successful

Endpoint Telemetry:
Available

SIEM Telemetry:
Available

Detection:
No Match

Alert:
None
```

The result does not immediately explain why detection failed.

---

## Investigation

The teams review:

```text
Telemetry

Field mappings

Detection logic

Rule status

Rule scheduling

Alert pipeline
```

They identify that the detection expects a field value that differs from the current telemetry schema.

---

## Improvement

Detection Engineering updates the analytic.

The change is reviewed before deployment.

---

## Attempt 2

The same controlled procedure is repeated.

Observed:

```text
Technique:
Successful

Endpoint Telemetry:
Available

SIEM Telemetry:
Available

Detection:
Match

Alert:
Generated

SOC Investigation:
Successful
```

---

## Conclusion

A defensible conclusion is:

> The initial test demonstrated that the selected behavior generated the required endpoint and SIEM telemetry, but the existing analytic did not match because its logic depended on an outdated field value. Detection Engineering updated the analytic and the original procedure was repeated. The updated rule generated the expected alert and the SOC successfully investigated the activity. Detection is therefore considered validated for the tested procedure and environment.

This explains:

```text
What happened

Why it failed

What changed

What evidence supports improvement

What was actually validated
```

---

# Purple Teaming Metrics

A balanced measurement model can include:

```text
                 Purple Team Metrics
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
   Technical          Operational        Learning
       |                 |                 |
Telemetry Coverage   Time to Detect    Knowledge Gain
Detection Success    Investigation     Teach-Back
Prevention           Response          Retention
Retest Success       Escalation        Collaboration
       |
       v
Programme Improvement
       |
       +---- Action Completion
       +---- Regression Rate
       +---- Repeated Findings
```

Avoid relying on a single metric.

---

# Purple Team Maturity

A simple maturity progression is:

```text
Level 1 - Isolated

Red and Blue operate separately.


Level 2 - Cooperative

Teams occasionally share findings.


Level 3 - Collaborative

Structured purple team exercises occur.


Level 4 - Measured

Exercises use defined objectives and metrics.


Level 5 - Learning

Knowledge transfer and AARs are systematic.


Level 6 - Validated

Improvements require retesting.


Level 7 - Continuous

Important tests become recurring validation.
```

The exact maturity model can be adapted to organisational needs.

---

# Common Purple Teaming Mistakes

Avoid:

```text
Treating purple teaming as another penetration test

Measuring only whether Red succeeded

Testing without objectives

Testing techniques without threat relevance

Focusing only on detection rules

Ignoring telemetry dependencies

Ignoring investigation capability

Changing controls without retesting

Creating metrics without interpretation

Holding an AAR without assigning actions

Documenting lessons without transferring knowledge

Assuming one successful test proves permanent effectiveness
```

---

# Purple Teaming Checklist

## Planning

- [ ] Define objectives
- [ ] Define scope
- [ ] Define success criteria
- [ ] Define participants
- [ ] Define rules of engagement
- [ ] Define safety constraints
- [ ] Select threat-relevant techniques
- [ ] Map techniques to ATT&CK where useful
- [ ] Identify expected telemetry
- [ ] Identify expected detections

## Preparation

- [ ] Confirm authorisation
- [ ] Confirm targets
- [ ] Confirm test accounts
- [ ] Confirm logging
- [ ] Confirm SIEM access
- [ ] Confirm EDR access
- [ ] Confirm communication channel
- [ ] Confirm evidence collection
- [ ] Confirm stop procedure
- [ ] Confirm cleanup requirements

## Execution

- [ ] Record timestamp
- [ ] Execute agreed technique
- [ ] Confirm execution result
- [ ] Confirm preventive-control result
- [ ] Confirm telemetry
- [ ] Confirm collection
- [ ] Confirm parsing
- [ ] Confirm detection
- [ ] Confirm alert
- [ ] Confirm investigation

## Collaboration

- [ ] Share observations
- [ ] Explain attack behavior
- [ ] Explain telemetry
- [ ] Explain detection logic
- [ ] Identify assumptions
- [ ] Identify gaps
- [ ] Agree improvement

## Retesting

- [ ] Repeat original procedure
- [ ] Compare before and after
- [ ] Confirm telemetry
- [ ] Confirm detection
- [ ] Confirm investigation
- [ ] Capture evidence
- [ ] Record limitations

## Learning

- [ ] Identify lessons
- [ ] Transfer relevant knowledge
- [ ] Update documentation
- [ ] Update runbooks
- [ ] Validate understanding
- [ ] Record ownership

## After-Action Review

- [ ] Reconstruct timeline
- [ ] Compare expected and observed
- [ ] Identify strengths
- [ ] Identify failures
- [ ] Determine root causes
- [ ] Define actions
- [ ] Assign owners
- [ ] Define retests

## Continuous Improvement

- [ ] Track actions
- [ ] Close only after appropriate validation
- [ ] Identify repeated findings
- [ ] Identify systemic problems
- [ ] Add future exercise scenarios
- [ ] Convert suitable tests to regression tests
- [ ] Review metrics
- [ ] Review threat relevance

---

# Quick Purple Team Workflow

```text
DEFINE OBJECTIVE
      |
      v
DEFINE SCOPE
      |
      v
SELECT THREAT
      |
      v
MAP BEHAVIOR
      |
      v
DEFINE EXPECTED RESULT
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
TRANSFER KNOWLEDGE
      |
      v
MEASURE
      |
      v
AFTER-ACTION REVIEW
      |
      v
CONTINUOUS VALIDATION
      |
      +----------------+
      |                |
      v                |
NEW THREAT / CHANGE ---+
```

---

# Recommended Reading Order

For someone learning purple teaming from these notes:

```text
1. Purple Teaming Overview
          |
          v
2. Methodology
          |
          v
3. Exercises
          |
          v
4. MITRE ATT&CK
          |
          v
5. Detection Engineering
          |
          v
6. Knowledge Transfer
          |
          v
7. Metrics and Measurement
          |
          v
8. After-Action Review
          |
          v
9. Continuous Validation
```

Start with the process before focusing on individual tools.

---

# Related Notes

## Purple Teaming

- [Methodology](methodology.md)
- [Exercises](exercises.md)
- [Detection Engineering](detection-engineering.md)
- [MITRE ATT&CK](mitre-attack.md)
- [Knowledge Transfer](knowledge-transfer.md)
- [Metrics and Measurement](metrics-and-measurement.md)
- [After-Action Review](after-action-review.md)
- [Continuous Validation](continuous-validation.md)

## Related Security Areas

- [Red Teaming](../red-teaming/index.md)
- [Active Directory](../active-directory/index.md)
- [Windows Security](../windows/index.md)
- [Linux Security](../linux/index.md)
- [Web Application Security](../web/index.md)
- [Source Code Review](../source-code-review/index.md)
- [Privilege Escalation Explorer](../privesc/index.md)

---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE Center for Threat-Informed Defense](https://ctid.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Sigma Documentation](https://sigmahq.io/docs/){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NICE Workforce Framework for Cybersecurity](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center){ target="_blank" rel="noopener noreferrer" }

!!! tip "Purple teaming is an improvement process"

    The value of a purple team exercise is not determined by how many techniques the red team executes. Its value comes from what the organisation learns, improves and can subsequently validate.

!!! tip "Follow the complete chain"

    When a detection fails, determine whether the problem occurred during execution, telemetry generation, collection, parsing, detection logic, alert routing or investigation before deciding what needs to change.

!!! tip "Retest improvements"

    A configuration or detection change demonstrates implementation. Repeating the relevant scenario and observing the expected result provides validation.

!!! tip "Preserve important tests"

    Successful retests can become reusable regression tests so that future platform, telemetry or detection changes do not silently reintroduce previously resolved gaps.

!!! warning "Stay within authorised scope"

    Purple team exercises and recurring validation should operate only against approved systems, accounts and techniques under the organisation's agreed rules of engagement.
