---
title: Purple Teaming Continuous Validation
description: Practical guidance for turning purple team exercises into repeatable continuous security validation through regression testing, detection-as-code, telemetry monitoring, automation and threat-informed testing.
---

# Purple Teaming Continuous Validation

Purple teaming should not end when an exercise finishes.

Security environments continuously change:

```text
Operating systems are updated

Applications change

Detection rules are modified

EDR agents are upgraded

SIEM schemas change

Parsers are updated

Cloud services evolve

Identity configurations change

Adversary techniques evolve

Infrastructure is replaced
```

A control that worked during one purple team exercise may not continue working indefinitely.

Continuous validation addresses this problem by converting important purple team tests into repeatable validation activities.

```text
Purple Team Exercise
        |
        v
Observation
        |
        v
Improvement
        |
        v
Retest
        |
        v
Validated Test
        |
        v
Reusable Test
        |
        v
Continuous Validation
        |
        v
Regression Detection
        |
        v
Improvement
```

The objective is not to continuously attack production systems.

The objective is to continuously maintain evidence that important security controls, telemetry, detections and response processes continue to operate as expected.

---

## 1. Why Continuous Validation Matters

A successful purple team exercise provides evidence about a specific point in time.

For example:

```text
Technique executed:
Yes

Telemetry generated:
Yes

Detection triggered:
Yes

SOC investigation:
Successful
```

This proves that the tested capability worked under the tested conditions.

It does not prove that it will still work:

```text
Tomorrow

Next month

After an EDR upgrade

After a SIEM migration

After a parser change

After a detection modification

After infrastructure changes
```

Continuous validation helps detect these regressions.

---

## 2. Point-in-Time Assurance

Traditional validation often looks like:

```text
Test
 |
 v
Pass
 |
 v
Report
 |
 v
Done
```

This creates point-in-time assurance.

The problem is:

```text
Environment
    |
    +---- Changes
    |
    +---- Changes
    |
    +---- Changes
    |
    v
Original Test Result
May No Longer Be Valid
```

Continuous validation changes the model to:

```text
Test
 |
 v
Pass
 |
 v
Retain Test
 |
 v
Repeat
 |
 v
Compare
 |
 v
Investigate Regression
```

---

## 3. Continuous Validation Objectives

A continuous validation programme may aim to verify:

```text
Preventive controls still work

Telemetry is still generated

Telemetry still reaches the required platform

Parsers still populate required fields

Detection rules still match

Alerts still reach analysts

Investigation guidance remains accurate

Response workflows remain usable

Remediation remains effective

Knowledge remains current
```

Not every objective requires the same validation frequency.

---

## 4. Continuous Validation Is Not Continuous Exploitation

Continuous validation does not mean repeatedly running dangerous exploitation against production systems.

Validation can include:

```text
Safe simulations

Controlled emulation

Synthetic events

Replay testing

Detection unit tests

Telemetry health checks

Configuration checks

Lab testing

Staging validation

Approved production tests
```

Choose the least disruptive method that provides sufficient evidence.

---

## 5. Authorisation

Every validation activity must remain within approved scope.

Define:

```text
Systems

Accounts

Techniques

Tools

Test windows

Data handling

Safety controls

Cleanup requirements

Notification requirements
```

Automation does not remove the requirement for authorisation.

An automated security test is still a security test.

---

# 6. From Exercise to Regression Test

Not every purple team action needs to become a recurring test.

Prioritise tests that validate:

```text
Critical detections

High-risk techniques

Previously failed controls

Important telemetry sources

Critical attack paths

High-value assets

Frequently changing infrastructure

Regulatory requirements

Threat-relevant behavior
```

A useful lifecycle is:

```text
Exercise Test
     |
     v
Was It Valuable?
     |
   +-+--+
   |    |
  No   Yes
   |    |
   v    v
Archive Convert to
        Reusable Test
             |
             v
       Define Expected
           Result
             |
             v
       Add Validation
             |
             v
       Run Repeatedly
```

---

# 7. What Makes a Good Regression Test?

A good security regression test should be:

```text
Repeatable

Scoped

Safe

Observable

Deterministic where practical

Documented

Owned

Versioned

Measurable

Easy to investigate when it fails
```

The test should have a clearly defined expected result.

---

# 8. Test Definition

A reusable test should document:

```text
Test ID

Objective

Technique

ATT&CK mapping

Threat relevance

Environment

Prerequisites

Procedure

Expected telemetry

Expected prevention

Expected detection

Expected alert

Cleanup

Success criteria

Failure criteria

Owner

Last validation date
```

---

# 9. Example Test Definition

```text
Test ID:
PT-CV-001

Objective:
Validate detection of the selected execution behavior.

ATT&CK:
Relevant technique and sub-technique.

Environment:
Approved Windows validation endpoint.

Prerequisites:
Endpoint online.
EDR active.
Required logging enabled.
SIEM ingestion operational.

Expected Telemetry:
Process telemetry.
Relevant Windows telemetry.

Expected Detection:
Purple team validation analytic.

Expected Alert:
Alert visible in SOC platform.

Success:
Technique executes as designed and the expected alert is generated.

Failure:
Technique executes successfully but expected telemetry or detection is absent.

Owner:
Detection Engineering.

Validation:
Purple Team.
```

---

# 10. Expected Results

A continuous test requires an expected result.

Avoid:

```text
Run test and see what happens.
```

Prefer:

```text
Expected:
Technique executes.

Expected:
Event generated within defined test window.

Expected:
Required fields populated.

Expected:
Detection matches.

Expected:
Alert appears.

Expected:
Test marker allows activity to be identified.
```

This makes automated comparison possible.

---

# 11. Success States

Possible states include:

```text
Pass

Partial Pass

Fail

Blocked

Test Error

Environment Error

Not Applicable

Not Run
```

These states should have consistent definitions.

---

# 12. Separate Test Failure From Control Failure

A failed test does not automatically indicate a security regression.

Example:

```text
Validation script failed to execute.
```

This may be:

```text
Test Failure
```

rather than:

```text
Detection Failure
```

Similarly:

```text
Target endpoint offline
```

is an environmental issue.

Use explicit classifications.

---

# 13. Validation Chain

For detection-focused tests, validate the complete chain:

```text
Test Action
    |
    v
Endpoint Behavior
    |
    v
Telemetry Generated
    |
    v
Telemetry Collected
    |
    v
Telemetry Forwarded
    |
    v
Telemetry Parsed
    |
    v
Detection Evaluated
    |
    v
Alert Generated
    |
    v
Alert Delivered
```

This makes failures easier to diagnose.

---

# 14. Prevention Validation

Some tests focus on preventive controls.

Example:

```text
Technique Attempted
       |
       v
Preventive Control
       |
       v
Blocked
```

Validate:

```text
Was execution actually blocked?

Which control blocked it?

Was telemetry generated?

Was an alert generated?

Was the block expected?
```

Do not confuse:

```text
Technique failed
```

with:

```text
Technique prevented
```

without evidence.

---

# 15. Detection Validation

A detection validation should answer:

```text
Did the behavior occur?

Was telemetry available?

Did detection logic evaluate it?

Did the analytic match?

Was an alert created?

Was the alert routed correctly?
```

A simple:

```text
Alert exists
```

check may not be enough for complex detections.

---

# 16. Telemetry Validation

Telemetry is a dependency for many detections.

Continuous telemetry validation can verify:

```text
Data source present

Recent events available

Required fields populated

Timestamp valid

Parser functioning

Expected host coverage

Expected retention

Acceptable ingestion delay
```

A healthy detection rule cannot compensate for missing telemetry.

---

# 17. Telemetry Health Checks

Examples of telemetry health questions:

```text
Has this source produced events recently?

Are all expected endpoints reporting?

Are critical fields populated?

Did event volume suddenly drop?

Did schema change?

Did ingestion latency increase?
```

These checks can identify failures before an attack test is performed.

---

# 18. Parser Validation

Parser changes can silently break detections.

Example:

```text
Original Field:
process.command_line

New Field:
process.commandline
```

A detection depending on the original field may stop working even though telemetry is still being ingested.

Continuous validation should consider:

```text
Schema

Field names

Field types

Normalization

Mappings

Parser versions
```

---

# 19. Detection-as-Code

Detection-as-code treats detection logic similarly to software.

A detection repository may contain:

```text
Rule

Metadata

ATT&CK mapping

Required data sources

Test cases

Expected matches

Expected non-matches

Documentation

Version history
```

Changes can then be reviewed and tested before deployment.

---

# 20. Detection Development Lifecycle

A useful model is:

```text
Detection Requirement
        |
        v
Rule Development
        |
        v
Static Validation
        |
        v
Test Data
        |
        v
Purple Team Validation
        |
        v
Peer Review
        |
        v
Deployment
        |
        v
Continuous Validation
```

This creates stronger assurance than manually editing production rules without testing.

---

# 21. Positive Tests

A positive test verifies that known suspicious behavior matches the detection.

Conceptually:

```text
Known Test Behavior
       |
       v
Detection
       |
       v
Expected Match
```

If the detection does not match:

```text
Regression
```

may have occurred.

---

# 22. Negative Tests

A negative test verifies that expected legitimate behavior does not incorrectly trigger the rule.

```text
Known Legitimate Behavior
        |
        v
Detection
        |
        v
Expected No Match
```

Both positive and negative tests can improve detection quality.

---

# 23. Test Data

Detection tests may use:

```text
Synthetic events

Sanitised historical events

Exercise telemetry

Replay datasets

Controlled live telemetry
```

Test data should accurately represent the fields required by the analytic.

---

# 24. Replay Testing

Previously captured exercise telemetry can sometimes be replayed or evaluated against updated detection logic.

This can help answer:

```text
Would the new rule detect the previous attack?

Did a rule change break an existing detection?

Does a parser change alter the result?
```

Replay testing can reduce the need to execute the original technique every time.

---

# 25. Live Validation

Some controls require live execution to validate the complete chain.

For example:

```text
Endpoint
   |
   v
Sensor
   |
   v
Collector
   |
   v
SIEM
   |
   v
Detection
   |
   v
SOC
```

Replay testing may validate the analytic but not necessarily the endpoint sensor or collection pipeline.

Use live validation when end-to-end assurance is required and authorised.

---

# 26. Lab Validation

A lab can provide a safer environment for:

```text
New techniques

Potentially disruptive tests

Detection development

Technique variations

Tool testing

Parser validation
```

Lab results should not automatically be treated as proof that production behaves identically.

---

# 27. Staging Validation

Where a representative staging environment exists:

```text
Develop
   |
   v
Lab Test
   |
   v
Staging Test
   |
   v
Approved Production Validation
```

This can reduce operational risk.

---

# 28. Production Validation

Some organisations perform carefully controlled validation in production.

Requirements may include:

```text
Explicit authorisation

Defined test accounts

Dedicated test endpoints

Change window

SOC coordination

Test identifiers

Safety controls

Cleanup

Rollback plan
```

Production testing should be proportionate to the assurance required.

---

# 29. Test Markers

Controlled tests should be distinguishable from real malicious activity where appropriate.

Possible markers include:

```text
Dedicated test account

Known test hostname

Exercise identifier

Unique benign filename

Unique event marker

Defined test window
```

Markers help analysts and automation correlate test activity.

They should not undermine the behavior being validated.

---

# 30. Scheduling Validation

Not every test needs the same frequency.

Possible schedules include:

```text
On every detection change

Daily

Weekly

Monthly

Quarterly

After platform upgrades

After parser changes

After major architecture changes

After incidents
```

Frequency should reflect risk and change rate.

---

# 31. Event-Driven Validation

Some of the most useful validation is triggered by change.

Examples:

```text
EDR upgrade
      |
      v
Run endpoint detection tests

SIEM parser update
      |
      v
Run parser and detection tests

Detection rule modification
      |
      v
Run positive and negative tests

Operating system upgrade
      |
      v
Run platform-specific validation
```

This connects security testing with change management.

---

# 32. Change Management Integration

Security validation can be included in technical change processes.

Example:

```text
Change Requested
      |
      v
Security Impact Identified
      |
      v
Relevant Validation Tests Selected
      |
      v
Change Implemented
      |
      v
Tests Executed
      |
      v
Results Reviewed
      |
      v
Change Closed
```

This can reduce silent detection regressions.

---

# 33. Critical Change Triggers

Consider validation after changes to:

```text
EDR

SIEM

SOAR

Identity platform

Firewall

Proxy

DNS logging

Cloud platform

Endpoint logging

Windows policies

Linux audit configuration

Detection content

Parsers

Log collectors
```

These components can affect defensive visibility.

---

# 34. Regression

A regression occurs when previously validated capability stops meeting its expected result.

Example:

```text
January:
Test passes.

February:
Test passes.

March:
EDR upgraded.

April:
Test fails.
```

The April failure may indicate a regression.

---

# 35. Regression Investigation

Use:

```text
Test Failed
    |
    v
Did Test Execute?
    |
    +---- No -> Test Problem
    |
    v
Was Telemetry Generated?
    |
    +---- No -> Sensor / Platform
    |
    v
Was Telemetry Collected?
    |
    +---- No -> Collection
    |
    v
Was Telemetry Parsed?
    |
    +---- No -> Parser
    |
    v
Did Detection Match?
    |
    +---- No -> Detection
    |
    v
Was Alert Delivered?
    |
    +---- No -> Alert Pipeline
    |
    v
Operational Workflow
```

This is similar to the analysis performed during a purple team exercise.

---

# 36. Regression Severity

Not all regressions are equally important.

Consider:

```text
Threat relevance

Control criticality

Asset exposure

Number of affected systems

Availability of compensating controls

Attack-chain position

Business impact
```

A failed high-risk credential-access detection may require faster response than a low-priority informational analytic.

---

# 37. Regression Ownership

Every recurring test should have ownership.

Example:

| Component | Owner |
|---|---|
| Attack Test | Purple Team |
| Telemetry | Security Engineering |
| Detection | Detection Engineering |
| Alert Routing | SOC Engineering |
| Investigation | SOC |
| Platform | Platform Team |

A failed test can then be routed appropriately.

---

# 38. Regression Workflow

A useful workflow is:

```text
Test Failure
    |
    v
Automatic Triage
    |
    v
Confirm Failure
    |
    v
Identify Layer
    |
    v
Assign Owner
    |
    v
Investigate
    |
    v
Fix
    |
    v
Retest
    |
    v
Close
```

Avoid automatically creating high-priority incidents for every test failure without validation.

---

# 39. Continuous Validation Metrics

Useful metrics include:

```text
Tests executed

Tests passed

Tests failed

Tests not run

Regression rate

Time to identify regression

Time to restore validation

Telemetry availability

Detection availability

Repeated failures

Test coverage
```

See [Metrics and Measurement](metrics-and-measurement.md).

---

# 40. Validation Pass Rate

A basic metric is:

```text
Validation Pass Rate =
Passed Tests
------------
Executed Tests
```

Example:

```text
Executed:
100

Passed:
94

Pass rate:
94%
```

The remaining six tests require classification.

---

# 41. Regression Rate

A useful distinction is between new failures and regressions.

```text
Regression Rate =
Previously Passing Tests Now Failing
------------------------------------
Previously Passing Tests Executed
```

This helps measure stability.

---

# 42. Mean Time to Restore Validation

For failed controls:

```text
MTTRV =
Sum of Time From Confirmed Failure to Successful Retest
-------------------------------------------------------
Number of Restored Tests
```

The acronym is less important than defining the measurement consistently.

---

# 43. Validation Coverage

Coverage can be measured across:

```text
Relevant ATT&CK techniques

Critical detections

Critical telemetry sources

Platforms

Business units

Attack paths

Security controls
```

Do not present one percentage without explaining what it represents.

---

# 44. Threat-Informed Prioritisation

Continuous validation should focus on behavior relevant to the organisation.

Prioritisation inputs may include:

```text
Threat intelligence

Incident history

Red team findings

Purple team findings

Technology stack

Industry threats

Business-critical assets

External exposure
```

This helps avoid testing techniques merely because they are easy to automate.

---

# 45. ATT&CK Mapping

MITRE ATT&CK can help organise the validation library.

Example:

| Test | Technique | Platform | Detection | Status |
|---|---|---|---|---|
| CV-001 | Txxxx | Windows | DET-001 | Pass |
| CV-002 | Tyyyy | Linux | DET-014 | Pass |
| CV-003 | Tzzzz | Cloud | DET-031 | Fail |

See [MITRE ATT&CK](mitre-attack.md).

---

# 46. ATT&CK Is an Index, Not Proof

A test library containing:

```text
100 ATT&CK techniques
```

does not automatically provide strong defensive assurance.

Ask:

```text
Are they relevant?

Are realistic procedures tested?

Is telemetry validated?

Are detections validated?

Are important variants tested?

Are failures investigated?
```

Coverage quality matters.

---

# 47. Attack Path Validation

Continuous validation should include complete attack paths where useful.

Example:

```text
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
```

Individual detections may work while correlation or operational response across the complete chain fails.

---

# 48. Atomic Versus Scenario Tests

Atomic tests focus on one behavior:

```text
Technique
   |
   v
Expected Detection
```

Scenario tests combine multiple behaviors:

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
Detection and Response
```

Both are useful.

---

# 49. Atomic Tests

Advantages:

```text
Fast

Focused

Easy to troubleshoot

Easy to automate

Useful for regression
```

Limitations:

```text
Limited adversary context

May not test correlation

May not test realistic sequencing
```

---

# 50. Scenario Tests

Advantages:

```text
More realistic

Tests multiple controls

Tests correlation

Tests analyst reasoning

Tests operational workflow
```

Limitations:

```text
More complex

Harder to automate

Harder to diagnose

Potentially more disruptive
```

Use both appropriately.

---

# 51. Validation Pyramid

A practical model is:

```text
              Full Scenario
                  /\
                 /  \
                /    \
               /      \
          Technique Tests
             /          \
            /            \
           /              \
      Detection Unit Tests
         /                  \
        /                    \
       /                      \
Telemetry and Configuration Checks
```

Lower layers can run frequently.

Higher layers may run less frequently.

---

# 52. Layer 1 - Configuration Validation

Examples:

```text
Logging enabled

EDR running

Required audit policy enabled

Collector configured

Detection enabled

Alert routing configured
```

These checks are fast but do not prove end-to-end effectiveness.

---

# 53. Layer 2 - Telemetry Validation

Verify:

```text
Events generated

Events received

Required fields populated

Latency acceptable
```

This validates the data pipeline.

---

# 54. Layer 3 - Detection Unit Tests

Verify:

```text
Known positive data matches

Known negative data does not match

Rule syntax valid

Required fields available
```

This validates detection logic.

---

# 55. Layer 4 - Technique Tests

Execute controlled behavior.

Validate:

```text
Real telemetry

Real detection

Real alert
```

This provides stronger end-to-end evidence.

---

# 56. Layer 5 - Scenario Tests

Validate:

```text
Multiple techniques

Correlation

Investigation

Escalation

Response

Cross-team coordination
```

These are closer to full purple team exercises.

---

# 57. Automation

Automation can improve:

```text
Frequency

Repeatability

Consistency

Coverage

Evidence collection

Regression detection
```

But automation should not replace analysis.

A failed automated test still requires interpretation.

---

# 58. Automation Pipeline

A conceptual pipeline is:

```text
Scheduler / Trigger
        |
        v
Test Runner
        |
        v
Controlled Action
        |
        v
Telemetry
        |
        v
Detection
        |
        v
Result Collector
        |
        v
Expected vs Observed
        |
        v
Pass / Fail
        |
        v
Ticket / Dashboard
```

---

# 59. Safety Controls for Automation

Automated tests should include controls such as:

```text
Explicit allowlist

Approved targets

Rate limits

Execution timeout

Test account

Defined cleanup

Maximum concurrency

Kill switch

Logging

Failure handling
```

Automation should fail safely.

---

# 60. Allowlisting Targets

Never allow validation automation to run against arbitrary systems.

Prefer:

```text
Approved Endpoint List

Approved Lab

Approved Staging Environment

Dedicated Validation Hosts
```

The test runner should enforce scope.

---

# 61. Rate Limiting

Recurring tests can generate:

```text
Alerts

Logs

Network traffic

Endpoint activity
```

Control frequency and concurrency.

The objective is validation, not unnecessary operational load.

---

# 62. Cleanup

Automated tests should define cleanup.

Examples:

```text
Remove test files

Remove temporary configuration

Remove test accounts where applicable

Remove temporary scheduled activity

Restore changed settings

Terminate test processes
```

Cleanup should itself be validated where relevant.

---

# 63. Test Isolation

Where practical, use:

```text
Dedicated validation endpoints

Dedicated test accounts

Dedicated network segments

Dedicated cloud resources
```

This reduces operational risk and improves result interpretation.

---

# 64. Validation Tool Categories

Continuous validation may use several categories of tooling.

Examples include:

```text
Adversary emulation frameworks

Breach and attack simulation platforms

Atomic testing frameworks

Detection-as-code pipelines

SIEM test frameworks

Custom validation scripts

Configuration validation

Telemetry health monitoring
```

No single tool validates every layer.

---

# 65. Atomic Red Team

Atomic Red Team provides small tests mapped to MITRE ATT&CK techniques.

It can be useful for:

```text
Technique validation

Detection testing

Controlled emulation

Repeatable regression testing
```

Tests should still be reviewed before execution.

Project:

[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }

---

# 66. MITRE Caldera

MITRE Caldera provides an automated adversary emulation platform.

It can support:

```text
Adversary emulation

Technique sequencing

Automated operations

Scenario validation
```

Project:

[MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }

---

# 67. Detection Testing Frameworks

Detection testing can also be implemented using:

```text
Custom unit tests

Saved telemetry

Rule-specific test data

CI/CD pipelines

Detection repositories
```

The important requirement is repeatability.

---

# 68. Sigma

Sigma can provide a portable format for expressing log detection logic.

A detection engineering workflow may use:

```text
Exercise Behavior
       |
       v
Telemetry
       |
       v
Detection Requirement
       |
       v
Sigma Rule
       |
       v
Backend Conversion
       |
       v
Validation
```

Documentation:

[Sigma Documentation](https://sigmahq.io/docs/){ target="_blank" rel="noopener noreferrer" }

---

# 69. Version Control

Store validation artifacts in version control where appropriate.

Examples:

```text
Attack tests

Detection rules

Test data

Expected results

Configuration checks

Documentation
```

Version control provides:

```text
History

Peer review

Rollback

Change attribution

Reproducibility
```

---

# 70. Test Versioning

A test should have a version or revision history.

Example:

```text
CV-001 v1
Initial test.

CV-001 v2
Updated for new telemetry schema.

CV-001 v3
Added negative test.
```

Record which version produced each validation result.

---

# 71. Detection Versioning

When a test fails, identify the detection version.

Example:

```text
Test:
CV-001 v3

Detection:
DET-014 v8

Result:
Fail
```

This helps reproduce and investigate the regression.

---

# 72. Environment Versioning

Also capture relevant environment context:

```text
Operating system version

EDR version

Parser version

SIEM content version

Application version
```

This can explain why a test behaves differently over time.

---

# 73. CI/CD Integration

Detection validation can be integrated into CI/CD.

Conceptually:

```text
Detection Change
      |
      v
Pull Request
      |
      v
Syntax Check
      |
      v
Unit Tests
      |
      v
Positive Test
      |
      v
Negative Test
      |
      v
Review
      |
      v
Merge
      |
      v
Deployment
```

This reduces the chance of deploying broken detection content.

---

# 74. Pre-Deployment Validation

Before deploying a changed detection:

```text
Does syntax validate?

Do known positives match?

Do known negatives remain clean?

Are required fields available?

Does ATT&CK mapping remain accurate?

Is documentation updated?
```

These checks can be automated where possible.

---

# 75. Post-Deployment Validation

Deployment success does not prove operational success.

After deployment:

```text
Confirm rule enabled

Confirm correct environment

Execute or replay test

Confirm alert

Confirm routing

Confirm analyst visibility
```

This validates the production chain.

---

# 76. Monitoring Test Health

Tests themselves can break.

Monitor:

```text
Test runner availability

Credential validity

Target availability

Dependency versions

Test syntax

API availability

Network access
```

A broken test should not be confused with a broken control.

---

# 77. Test Reliability

If a test frequently fails for unrelated reasons, teams may stop trusting it.

Track:

```text
False test failures

Environmental failures

Flaky tests

Timeouts

Dependency failures
```

Improve unreliable tests.

---

# 78. Test Confidence

A useful classification may be:

```text
High Confidence

Medium Confidence

Low Confidence
```

based on factors such as:

```text
Test reliability

Environment fidelity

Evidence quality

Procedure realism

Coverage depth
```

Document the reasoning.

---

# 79. Evidence Collection

Each recurring validation should retain enough evidence to support its result.

Examples:

```text
Test ID

Timestamp

Target

Test version

Detection version

Execution result

Telemetry result

Detection result

Alert identifier

Relevant logs

Failure reason
```

Avoid retaining unnecessary sensitive data.

---

# 80. Machine-Readable Results

Automation benefits from structured results.

Example:

```json
{
  "test_id": "PT-CV-001",
  "technique": "TXXXX",
  "execution": "pass",
  "telemetry": "pass",
  "detection": "pass",
  "alert": "pass",
  "result": "pass"
}
```

Structured output can feed:

```text
Dashboards

Tickets

Trend analysis

Reporting
```

---

# 81. Human-Readable Results

Machine-readable results should still support human interpretation.

Example:

```text
Test:
PT-CV-001

Result:
FAIL

Execution:
Successful

Telemetry:
Available

Detection:
No match

Likely Failure Layer:
Detection logic

Next Step:
Review DET-014 against current telemetry schema.
```

This helps analysts investigate quickly.

---

# 82. Alerting on Validation Failures

Not every failed test needs the same notification.

Possible routing:

```text
Critical detection regression
        |
        v
Immediate notification

Low-priority validation failure
        |
        v
Ticket

Test infrastructure failure
        |
        v
Test platform owner
```

Use severity and ownership.

---

# 83. Avoid Alert Fatigue

If continuous validation generates excessive alerts:

```text
SOC may ignore test alerts

Real alerts may be obscured

Metrics become distorted
```

Use:

```text
Test markers

Dedicated queues

Controlled schedules

Appropriate suppression

Clear labelling
```

without bypassing the control being validated.

---

# 84. SOC Awareness

The SOC should understand how recurring validation is handled.

Possible models include:

```text
Announced tests

Partially announced tests

Dedicated test alerts

Blind validation windows
```

The choice depends on the objective.

---

# 85. Announced Validation

Useful when testing:

```text
Telemetry

Detection logic

Alert routing

Technical integration
```

Analysts know that testing is occurring.

This reduces confusion.

---

# 86. Blind Validation

Blind or limited-notice testing may be appropriate when evaluating:

```text
Analyst recognition

Triage

Escalation

Operational response
```

This requires stronger governance and authorisation.

---

# 87. Do Not Mix Objectives

If the SOC knows exactly when and how a test will occur, the exercise may not provide meaningful evidence of analyst detection performance.

Conversely, if the objective is only to validate telemetry, secrecy may add unnecessary complexity.

Define the objective first.

---

# 88. Knowledge Validation

Continuous validation can also test knowledge.

Examples:

```text
Can analysts still explain the alert?

Can another analyst reproduce the investigation?

Is the runbook still accurate?

Does the escalation path still work?
```

Technical controls and human capability both change over time.

---

# 89. Runbook Validation

A runbook may become outdated because:

```text
SIEM interface changed

Query syntax changed

Alert fields changed

Team responsibilities changed

Escalation contacts changed
```

Periodic exercises can validate the runbook.

---

# 90. Documentation Validation

Check:

```text
Links work

Queries work

Screenshots remain relevant

Owners remain correct

Procedures match current tooling

Referenced detections still exist
```

Documentation is part of operational capability.

---

# 91. Knowledge Retention

A later exercise can test whether knowledge from an earlier exercise was retained.

Example:

```text
Exercise 1:
Analyst learns investigation workflow.

30 Days Later:
Similar scenario repeated.

Question:
Can analyst perform investigation independently?
```

See [Knowledge Transfer](knowledge-transfer.md).

---

# 92. Continuous Validation and AAR

A failed recurring test should create a smaller feedback cycle.

```text
Regression
   |
   v
Review
   |
   v
Root Cause
   |
   v
Improvement
   |
   v
Retest
```

The same principles used in an after-action review remain useful.

See [After-Action Review](after-action-review.md).

---

# 93. Lessons Feed Validation

The relationship should be:

```text
Exercise
   |
   v
AAR
   |
   v
Important Lesson
   |
   v
Reusable Test
   |
   v
Continuous Validation
```

This prevents important lessons from being forgotten.

---

# 94. Continuous Validation Feeds Exercises

The relationship also works in reverse:

```text
Recurring Test Failure
       |
       v
Interesting Regression
       |
       v
Purple Team Exercise
       |
       v
Deeper Investigation
```

Recurring validation can identify areas requiring human-led testing.

---

# 95. Continuous Validation Backlog

Maintain a backlog containing:

```text
Candidate test

Threat relevance

Technique

Control

Platform

Expected result

Automation feasibility

Risk

Priority

Owner
```

Not every candidate must be automated immediately.

---

# 96. Prioritisation Matrix

Example:

| Test | Threat Relevance | Control Criticality | Change Frequency | Priority |
|---|---|---|---|---|
| Credential Access A | High | High | Medium | High |
| Discovery B | Medium | Medium | Low | Medium |
| Persistence C | High | High | High | Critical |

Use organisational context rather than generic ranking.

---

# 97. Automation Suitability

A test is a stronger automation candidate when it is:

```text
Repeatable

Safe

Deterministic

Fast

Easy to clean up

Easy to observe

High value
```

Tests requiring complex human reasoning may remain manual.

---

# 98. Manual Validation Still Matters

Automation cannot fully replace:

```text
Creative adversary emulation

Novel technique testing

Complex attack chains

Analyst decision-making

Human collaboration

Threat-driven hypothesis testing
```

A mature programme combines automated and human-led validation.

---

# 99. Validation Portfolio

A balanced programme may contain:

```text
Automated telemetry checks

Detection unit tests

Automated atomic tests

Manual technique validation

Scenario-based exercises

Full purple team exercises
```

Each provides a different level of assurance.

---

# 100. Validation Frequency

A conceptual model is:

| Validation Type | Example Frequency |
|---|---|
| Configuration checks | Frequent |
| Telemetry health | Frequent |
| Detection unit tests | On change |
| Atomic validation | Regular |
| Scenario validation | Periodic |
| Full purple team exercise | Risk-based |

These are examples, not mandatory schedules.

---

# 101. Risk-Based Frequency

Increase validation frequency when:

```text
Threat relevance is high

Control is critical

Environment changes frequently

Previous regressions occurred

Detection is fragile

Asset is highly critical
```

Decrease frequency where evidence shows stable, low-risk capability.

---

# 102. Continuous Validation Dashboard

A useful dashboard might show:

```text
Total Active Tests

Passing Tests

Failed Tests

Regressions

Tests Not Run

Telemetry Health

Detection Health

High-Risk Failures

Average Time to Restore

Coverage by Platform

Coverage by ATT&CK
```

Every dashboard result should link to underlying evidence.

---

# 103. Example Dashboard

```text
PURPLE TEAM CONTINUOUS VALIDATION

Active Tests:                120

Executed This Period:        116

Passed:                      109

Failed:                        7

Confirmed Regressions:         4

Test Infrastructure Issues:    3

High-Risk Regressions:         1

Telemetry Health:            96%

Detection Validation:        94%
```

Do not interpret these numbers without scope and denominator definitions.

---

# 104. Trend Analysis

Track performance over time.

Example:

| Month | Tests | Pass | Regression |
|---|---:|---:|---:|
| January | 80 | 76 | 4 |
| February | 85 | 82 | 3 |
| March | 90 | 88 | 2 |

Trend analysis can show whether defensive capability is becoming more stable.

---

# 105. Recurring Failure Analysis

If the same test repeatedly fails:

```text
Test Failure
    |
    v
Fix
    |
    v
Pass
    |
    v
Fails Again
```

investigate whether the real problem is:

```text
Change management

Architecture

Ownership

Test design

Platform instability

Detection fragility
```

Repeated remediation may indicate a systemic issue.

---

# 106. Stale Tests

A test can become obsolete.

Reasons include:

```text
Technique no longer relevant

System retired

Detection replaced

Telemetry source changed

Threat model changed

Platform migrated
```

Validation libraries require maintenance.

---

# 107. Test Review

Periodically ask:

```text
Is this test still relevant?

Does it represent realistic behavior?

Does it validate an important control?

Is the expected result still correct?

Is the owner still correct?

Should the test be retired?
```

Remove tests that no longer provide useful assurance.

---

# 108. Test Retirement

A retirement record may contain:

```text
Test ID

Retirement date

Reason

Replacement test

Affected detection

Owner
```

Do not simply delete historical tests without context where auditability matters.

---

# 109. Validation Maturity Model

A practical maturity model is:

```text
Level 1 - Manual

Security controls are tested occasionally.

Level 2 - Repeatable

Important tests are documented and reusable.

Level 3 - Regression

Previously successful tests are repeated.

Level 4 - Automated

Suitable tests run automatically.

Level 5 - Integrated

Validation is connected to detection and change workflows.

Level 6 - Threat-Informed

Testing is continuously prioritised using threat and risk context.

Level 7 - Adaptive

Validation evolves based on regressions, incidents and environmental change.
```

---

# 110. Level 1 - Manual

Typical state:

```text
Purple team exercises occur.

Results are recorded.

Retesting is mostly manual.
```

Useful but dependent on individual effort.

---

# 111. Level 2 - Repeatable

The organisation maintains:

```text
Documented procedures

Expected results

Reusable scenarios

Clear ownership
```

Tests can be repeated consistently.

---

# 112. Level 3 - Regression

Previously successful tests are intentionally repeated.

The organisation can identify:

```text
Capability worked before.

Capability no longer works.
```

This is a major improvement in assurance.

---

# 113. Level 4 - Automated

Suitable tests are integrated into automation.

Benefits include:

```text
Higher frequency

Consistent execution

Faster regression discovery

Reduced manual effort
```

Human investigation remains necessary for failures.

---

# 114. Level 5 - Integrated

Validation connects with:

```text
Detection engineering

Change management

SIEM engineering

Endpoint engineering

SOC operations

Ticketing

CI/CD
```

Security validation becomes part of normal engineering.

---

# 115. Level 6 - Threat-Informed

Testing priorities adapt to:

```text
Threat intelligence

New adversary behavior

Incident trends

External exposure

Business risk
```

The validation library reflects the current threat environment.

---

# 116. Level 7 - Adaptive

The programme continuously learns from:

```text
Purple team exercises

Red team findings

Incidents

Threat intelligence

Detection regressions

Platform changes

Operational feedback
```

These inputs influence:

```text
What gets tested

How often it is tested

Which variants are added

Which controls receive priority
```

---

# Practical Continuous Validation Scenario

## Scenario

A purple team previously identified a detection gap involving a selected execution technique.

The original lifecycle was:

```text
Technique Executed
       |
       v
Telemetry Available
       |
       v
Detection Failed
       |
       v
Rule Improved
       |
       v
Retest Passed
```

The organisation wants to ensure that the improvement remains effective.

---

## Step 1 - Convert the Test

Create a reusable test containing:

```text
Technique

Procedure

Expected telemetry

Expected detection

Expected alert

Success criteria

Cleanup
```

---

## Step 2 - Establish Baseline

The first reusable test produces:

```text
Execution:
Pass

Telemetry:
Pass

Detection:
Pass

Alert:
Pass

Overall:
Pass
```

This becomes the validated baseline.

---

## Step 3 - Repeat After Change

Several weeks later, the SIEM parser is updated.

The test runs again.

Result:

```text
Execution:
Pass

Telemetry:
Pass

Detection:
Fail

Alert:
Fail
```

This indicates a likely regression.

---

## Step 4 - Investigate

The team compares:

```text
Previous telemetry

Current telemetry

Detection logic

Parser configuration
```

A field used by the detection has changed.

---

## Step 5 - Root Cause

```text
SIEM Parser Update
       |
       v
Field Mapping Changed
       |
       v
Detection Dependency Broken
       |
       v
Rule No Longer Matches
```

---

## Step 6 - Correct

Detection Engineering updates the rule.

---

## Step 7 - Retest

```text
Execution:
Pass

Telemetry:
Pass

Detection:
Pass

Alert:
Pass
```

The capability is restored.

---

## Step 8 - Improve the Process

The organisation adds:

```text
Parser Change
     |
     v
Automatic Detection Regression Tests
```

The original purple team lesson has now influenced the engineering lifecycle.

---

# Continuous Validation Checklist

## Governance

- [ ] Define validation scope
- [ ] Obtain required authorisation
- [ ] Define approved targets
- [ ] Define safety constraints
- [ ] Define ownership
- [ ] Define failure escalation
- [ ] Define data handling

## Test Design

- [ ] Assign test ID
- [ ] Define objective
- [ ] Define threat relevance
- [ ] Define ATT&CK mapping
- [ ] Define prerequisites
- [ ] Define procedure
- [ ] Define cleanup
- [ ] Define success criteria
- [ ] Define failure criteria

## Prevention

- [ ] Confirm technique attempted
- [ ] Confirm whether control blocked activity
- [ ] Identify blocking control
- [ ] Capture relevant evidence
- [ ] Separate prevention from execution failure

## Telemetry

- [ ] Confirm event generation
- [ ] Confirm collection
- [ ] Confirm forwarding
- [ ] Confirm parsing
- [ ] Confirm required fields
- [ ] Confirm acceptable latency
- [ ] Confirm expected host coverage

## Detection

- [ ] Confirm rule enabled
- [ ] Confirm rule version
- [ ] Confirm positive test
- [ ] Confirm negative test where applicable
- [ ] Confirm alert creation
- [ ] Confirm alert routing
- [ ] Confirm expected context

## Automation

- [ ] Enforce target allowlist
- [ ] Use safe test procedures
- [ ] Define timeout
- [ ] Define rate limits
- [ ] Define maximum concurrency
- [ ] Implement cleanup
- [ ] Implement failure handling
- [ ] Maintain test logs

## Regression

- [ ] Identify previously passing test
- [ ] Confirm current failure
- [ ] Separate test failure from control failure
- [ ] Identify failure layer
- [ ] Assign owner
- [ ] Identify root cause
- [ ] Implement improvement
- [ ] Retest
- [ ] Record validation result

## Change Management

- [ ] Identify security-relevant changes
- [ ] Map changes to validation tests
- [ ] Run tests after relevant changes
- [ ] Review results before closure
- [ ] Record unresolved regressions

## Knowledge

- [ ] Update documentation
- [ ] Update runbooks
- [ ] Update detection dependencies
- [ ] Update test procedure
- [ ] Confirm owners
- [ ] Validate analyst knowledge where relevant

## Maintenance

- [ ] Review test relevance
- [ ] Review test reliability
- [ ] Review threat relevance
- [ ] Review owners
- [ ] Review environment dependencies
- [ ] Retire obsolete tests
- [ ] Add new tests from exercises and incidents

---

# Quick Continuous Validation Workflow

```text
Purple Team Exercise
        |
        v
Important Finding
        |
        v
Remediation
        |
        v
Successful Retest
        |
        v
Reusable Test
        |
        v
Version Control
        |
        v
Schedule / Change Trigger
        |
        v
Execute
        |
        v
Collect Evidence
        |
        v
Compare With Expected Result
        |
      +-+--+
      |    |
     Pass Fail
      |    |
      |    v
      | Confirm Regression
      |    |
      |    v
      | Root Cause
      |    |
      |    v
      | Remediate
      |    |
      |    v
      | Retest
      |    |
      +----+
        |
        v
Update Baseline
        |
        v
Continue Validation
```

---

# Validation Decision Model

For each candidate test, ask:

```text
Is the behavior threat-relevant?
        |
        v
Does it validate an important control?
        |
        v
Can it be executed safely?
        |
        v
Can the result be observed?
        |
        v
Can success be clearly defined?
        |
        v
Is repetition valuable?
        |
        v
Can it be automated safely?
```

If automation is inappropriate:

```text
Retain as Manual Validation
```

If automation is appropriate:

```text
Add to Continuous Validation
```

---

# Failure Interpretation Model

When a test fails:

```text
Did the test execute correctly?
        |
      +-+--+
      |    |
     No   Yes
      |    |
      v    v
 Test Issue Was behavior prevented?
             |
           +-+--+
           |    |
          Yes   No
           |    |
           v    v
       Validate Was telemetry generated?
       Prevention       |
                     +--+--+
                     |     |
                    No    Yes
                     |     |
                     v     v
                  Sensor   Was telemetry collected?
                  Issue          |
                              +--+--+
                              |     |
                             No    Yes
                              |     |
                              v     v
                          Collection Was telemetry parsed?
                          Issue           |
                                       +--+--+
                                       |     |
                                      No    Yes
                                       |     |
                                       v     v
                                    Parser   Did detection match?
                                    Issue          |
                                                +-+--+
                                                |    |
                                               No   Yes
                                                |    |
                                                v    v
                                           Detection Alert Pipeline
                                           Issue
```

This prevents premature conclusions.

---

# Reporting Continuous Validation

A useful result should explain:

```text
What was tested?

Why was it tested?

What was expected?

What occurred?

Did the result change from the baseline?

Where did the failure occur?

What was done?

Did the retest pass?
```

Example:

> The recurring validation test for the selected execution behavior failed following a SIEM parser update. The test action executed successfully and the expected telemetry reached the SIEM, but the detection no longer matched because a required field mapping had changed. Detection Engineering updated the analytic and the same test was repeated successfully. The regression is considered resolved, and parser changes will now trigger the relevant detection regression suite.

This is stronger than:

> Detection failed but was fixed.

---

# Continuous Validation Testing Mindset

Do not think:

```text
Detection Passed Once = Detection Works Forever

Rule Enabled = Rule Works

Telemetry Exists = Telemetry Is Usable

Automated Test Passed = Complete Security

ATT&CK Coverage = Defensive Effectiveness

More Tests = Better Validation
```

Instead think:

```text
What Capability Matters?
       |
       v
How Can We Validate It?
       |
       v
What Evidence Should Exist?
       |
       v
Can the Test Be Repeated?
       |
       v
Can It Be Performed Safely?
       |
       v
What Changes Could Break It?
       |
       v
When Should It Run Again?
       |
       v
How Will We Detect Regression?
       |
       v
Who Owns the Failure?
       |
       v
How Will We Restore and Retest?
```

Continuous validation should preserve confidence in security capability as the environment changes.

---

# Purple Team Continuous Improvement Loop

The complete purple team cycle becomes:

```text
Threat Intelligence
        |
        v
Prioritisation
        |
        v
Purple Team Exercise
        |
        v
Telemetry Validation
        |
        v
Detection Validation
        |
        v
Investigation
        |
        v
After-Action Review
        |
        v
Knowledge Transfer
        |
        v
Improvement
        |
        v
Retest
        |
        v
Continuous Validation
        |
        v
Regression Monitoring
        |
        +--------------------------+
        |                          |
        v                          |
New Threat Intelligence            |
        |                          |
        +--------------------------+
```

This turns purple teaming from a periodic exercise into a repeatable security-improvement capability.

---

# Related Notes

- [Purple Teaming Overview](index.md)
- [Purple Teaming Methodology](methodology.md)
- [Purple Team Exercises](exercises.md)
- [Detection Engineering](detection-engineering.md)
- [MITRE ATT&CK](mitre-attack.md)
- [Knowledge Transfer](knowledge-transfer.md)
- [Metrics and Measurement](metrics-and-measurement.md)
- [After-Action Review](after-action-review.md)

---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Sigma Documentation](https://sigmahq.io/docs/){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-61 - Incident Response Recommendations and Considerations for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final){ target="_blank" rel="noopener noreferrer" }

!!! tip "Preserve successful purple team tests"

    When an exercise identifies an important gap and the remediation is successfully validated, consider preserving that procedure as a regression test. This prevents the organisation from repeatedly rediscovering the same weakness.

!!! tip "Validate dependencies, not only rules"

    Detection effectiveness depends on sensors, telemetry collection, parsers, field mappings, detection logic and alert delivery. Continuous validation should identify which layer failed.

!!! tip "Trigger tests after change"

    Platform upgrades, parser modifications, logging changes and detection updates are valuable triggers for regression testing because they can silently invalidate previously successful controls.

!!! tip "Combine automation with human-led exercises"

    Automated validation provides frequency and consistency. Human-led purple team exercises provide creativity, contextual reasoning and collaboration. A mature programme benefits from both.

!!! warning "Automation does not change scope"

    Recurring or automated security validation must remain within explicitly authorised systems, accounts, techniques and safety constraints. Automation should enforce scope rather than assume it.
