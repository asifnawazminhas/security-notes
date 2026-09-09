---
title: Purple Teaming Methodology
description: Practical methodology for planning, executing, measuring and continuously improving authorised purple team exercises through structured collaboration between offensive and defensive security teams.
---

# Purple Teaming Methodology

Purple teaming is a structured, collaborative process where offensive and defensive security teams work together to improve cyber resilience by sharing tactics, observations, telemetry, detection logic and response knowledge during controlled security exercises.

The objective is not simply to determine whether an attack technique works.

The objective is to understand the complete defensive chain:

```text
Adversary Behaviour
        |
        v
Security Control
        |
        v
Telemetry Generation
        |
        v
Telemetry Collection
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
Learning
        |
        v
Improvement
        |
        v
Retest
```

Purple teaming therefore combines:

```text
Offensive Security
       +
Defensive Security
       +
Detection Engineering
       +
Threat Intelligence
       +
Incident Response
       +
Knowledge Transfer
       +
Measurement
       +
Continuous Validation
```

The methodology on this page provides a practical framework for organising that process.

---

# 1. Core Principle

Purple teaming should not be reduced to:

```text
Red Team Attacks
      |
      v
Blue Team Watches
```

A stronger model is:

```text
Threat-Informed Objective
          |
          v
Controlled Adversary Behaviour
          |
          v
Observe Defensive Response
          |
          v
Exchange Knowledge
          |
          v
Identify Gaps
          |
          v
Improve Controls
          |
          v
Retest
          |
          v
Capture Learning
          |
          v
Convert Into Repeatable Validation
```

The value comes from the feedback loop.

---

# 2. Purple Teaming Is a Process

Purple teaming does not necessarily require a permanent team called the "Purple Team".

It can be implemented as a collaborative process involving existing functions such as:

```text
Red Team

Penetration Testing

SOC

Detection Engineering

Threat Intelligence

Incident Response

Security Engineering

Platform Engineering

Cloud Security

Identity Security

Application Security
```

The exact organisational structure can vary.

The important characteristic is structured collaboration between offensive and defensive capabilities.

---

# 3. Purple Teaming Versus Red Teaming

Red teaming and purple teaming can overlap, but their primary objectives are different.

| Red Teaming | Purple Teaming |
|---|---|
| Tests security objectives through adversary emulation | Improves defensive capability through collaboration |
| May intentionally limit defender knowledge | Usually involves deliberate information sharing |
| Often measures whether objectives can be achieved | Measures and improves control effectiveness |
| Detection may be evaluated after the operation | Detection can be analysed during the exercise |
| Operational realism may be prioritised | Learning and improvement are prioritised |
| Feedback may occur after the engagement | Feedback may occur throughout the exercise |

A red team operation can generate valuable input for a later purple team exercise.

---

# 4. Purple Teaming Versus Penetration Testing

Penetration testing commonly focuses on identifying and validating vulnerabilities.

Purple teaming focuses more broadly on whether security controls can:

```text
Prevent

Observe

Detect

Investigate

Respond

Recover

Learn
```

A penetration test finding may therefore become a purple team scenario.

Example:

```text
Penetration Test
      |
      v
Credential Exposure Identified
      |
      v
Purple Team Scenario
      |
      v
Test Credential Access Behaviour
      |
      v
Validate Telemetry
      |
      v
Validate Detection
      |
      v
Validate SOC Investigation
```

---

# 5. Purple Teaming Versus BAS

Breach and Attack Simulation, security control validation platforms and purple teaming are related but should not be treated as identical.

Automation can repeatedly execute security tests.

Purple teaming additionally includes:

```text
Human collaboration

Context

Reasoning

Threat prioritisation

Knowledge transfer

Detection engineering

Investigation analysis

Root cause analysis

Exercise adaptation
```

Automation can support the methodology.

It does not replace the collaborative process.

---

# 6. Methodology Overview

A practical purple teaming lifecycle is:

```text
AUTHORISATION
      |
      v
DEFINE OBJECTIVES
      |
      v
SELECT THREAT BEHAVIOURS
      |
      v
MAP CONTROLS AND TELEMETRY
      |
      v
DESIGN SCENARIOS
      |
      v
ESTABLISH BASELINE
      |
      v
EXECUTE
      |
      v
OBSERVE
      |
      v
COLLABORATE
      |
      v
IDENTIFY GAPS
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
AFTER-ACTION REVIEW
      |
      v
KNOWLEDGE TRANSFER
      |
      v
CONTINUOUS VALIDATION
```

The lifecycle is iterative.

A failure at one stage may require returning to an earlier stage.

---

# 7. Phase 1 - Authorisation and Governance

Every exercise begins with explicit authorisation.

Define:

```text
Who authorised the exercise?

Which systems are in scope?

Which techniques are permitted?

Which techniques are prohibited?

Which accounts may be used?

Which data may be accessed?

Which production systems may be touched?

What safety controls are required?

Who can stop the exercise?

How will incidents be distinguished from exercise activity?
```

Do not begin execution until these questions have clear answers.

---

# 8. Rules of Engagement

The Rules of Engagement should define operational boundaries.

A practical RoE may contain:

```text
Exercise name

Exercise owner

Business owner

Technical owner

Participants

Target systems

Excluded systems

Allowed techniques

Prohibited techniques

Testing window

Source infrastructure

Test accounts

Data restrictions

Communication channels

Emergency contacts

Stop conditions

Evidence handling

Cleanup requirements
```

The RoE should be available to the people responsible for exercise safety.

---

# 9. Stop Conditions

Define conditions that immediately suspend exercise activity.

Examples:

```text
Unexpected production outage

Unexpected access to sensitive data

Uncontrolled privilege escalation

Activity leaving the approved scope

Unexpected account lockouts

Unintended persistence

Security-control instability

Uncontrolled resource consumption

Business owner requests stop

Potential real incident detected
```

A clear stop process is part of good purple team governance.

---

# 10. Exercise Safety

Exercise design should minimise unnecessary operational risk.

Prefer:

```text
Dedicated test accounts

Synthetic data

Controlled hosts

Known source addresses

Bounded targets

Non-destructive techniques

Defined cleanup

Rate limits

Snapshots where practical

Maintenance windows where necessary
```

Do not assume that because an activity is part of a purple team exercise it is automatically safe for production.

---

# 11. Phase 2 - Define the Objective

Every scenario should begin with a clear objective.

Weak objective:

```text
Test PowerShell.
```

Better objective:

```text
Determine whether the endpoint and SIEM controls generate
sufficient telemetry to detect and investigate an authorised
PowerShell-based execution scenario on the selected Windows
test endpoint.
```

A good objective identifies what capability is being validated.

---

# 12. Objective Categories

Objectives may focus on:

```text
Prevention

Telemetry

Detection

Alerting

Investigation

Response

Containment

Recovery

Knowledge transfer

Control integration

Detection robustness

Response automation

Regression validation
```

A single scenario may evaluate several categories.

---

# 13. Define Success Before Execution

Do not decide whether a test succeeded after seeing the result.

Define expected outcomes first.

Example:

```text
Execution:
Technique executes on authorised test host.

Prevention:
Endpoint control blocks the prohibited variation.

Telemetry:
Process creation telemetry is generated.

Collection:
Relevant telemetry reaches the SIEM.

Detection:
Expected detection rule fires.

Alerting:
Alert reaches the intended queue.

Investigation:
Analyst can identify host, user, process and parent process.

Response:
Documented response workflow can be initiated.

Evidence:
Required artifacts can be collected.
```

This creates measurable expectations.

---

# 14. Success Is Layered

A scenario should not have only:

```text
PASS

FAIL
```

because different defensive layers may behave differently.

Example:

```text
Technique Execution: PASS

Prevention: FAIL

Telemetry Generation: PASS

Telemetry Collection: PASS

Detection: FAIL

Investigation: PARTIAL

Response: NOT TESTED
```

This is far more useful than a single overall score.

---

# 15. Phase 3 - Threat-Informed Prioritisation

Purple team exercises should be based on relevant threats and security objectives.

Potential inputs include:

```text
Threat intelligence

Previous incidents

Penetration test findings

Red team findings

Vulnerability assessments

Risk assessments

SOC observations

Detection gaps

Attack-path analysis

Business-critical systems

Cloud architecture

Identity architecture

Security-control changes
```

MITRE ATT&CK can then help organise adversary behaviours.

---

# 16. Threat Relevance Before ATT&CK Coverage

Do not begin with:

```text
How many ATT&CK techniques can we test?
```

Begin with:

```text
Which adversary behaviours matter to this organisation?
```

Then map those behaviours to ATT&CK where appropriate.

A large ATT&CK coverage percentage does not automatically mean strong security.

---

# 17. Scenario Prioritisation

Useful prioritisation factors include:

| Factor | Question |
|---|---|
| Threat relevance | Is the behaviour used by relevant adversaries? |
| Business criticality | Does it affect an important system? |
| Exposure | Is the attack path realistically reachable? |
| Detection uncertainty | Do we know whether the behaviour is detected? |
| Historical weakness | Has this control failed before? |
| Change frequency | Has the environment recently changed? |
| Impact | What happens if the control fails? |
| Learning value | Will the scenario improve team understanding? |

Prioritisation should be risk-informed rather than based only on technique count.

---

# 18. Phase 4 - Map the Defensive Chain

Before executing a technique, identify the expected defensive chain.

Example:

```text
Technique
   |
   v
Endpoint Activity
   |
   v
Operating System Event
   |
   v
EDR Sensor
   |
   v
Telemetry Pipeline
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
SOC Queue
   |
   v
Investigation
   |
   v
Response
```

This map helps identify exactly where a failure occurs.

---

# 19. Prevention Mapping

Identify controls expected to prevent the behaviour.

Examples:

```text
Endpoint protection

Application control

Attack surface reduction

Firewall

Web proxy

Email security

Identity policy

Conditional access

Network segmentation

Cloud policy

Privilege controls
```

Record whether prevention is:

```text
Expected

Optional

Not applicable
```

before testing.

---

# 20. Telemetry Mapping

Identify which telemetry should be generated.

Examples:

```text
Process creation

Authentication events

PowerShell logs

File creation

Registry modification

DNS queries

Network connections

Cloud audit events

Identity events

EDR telemetry

Proxy logs

Application logs
```

Then determine where that telemetry should be collected.

---

# 21. Telemetry Questions

For each data source, ask:

```text
Is the event generated?

Is the sensor enabled?

Is the event forwarded?

Does it reach the correct platform?

Is it parsed correctly?

Are important fields preserved?

Is enrichment applied?

Is the timestamp accurate?

Can analysts query it?
```

A missing alert does not necessarily mean the detection rule is wrong.

The problem may exist earlier in the telemetry pipeline.

---

# 22. Detection Mapping

For each scenario, document expected detections.

Example:

```text
Detection ID:
DET-WIN-001

Data Source:
Endpoint process telemetry

Expected Fields:
host.name
user.name
process.name
process.command_line
process.parent.name

Detection Objective:
Identify suspicious execution behaviour matching the
selected scenario.

Expected Alert:
Purple Team - Suspicious Execution Validation
```

The exact schema depends on the security platform.

---

# 23. Response Mapping

If response is in scope, document:

```text
Who receives the alert?

Who investigates it?

What information is required?

What escalation path applies?

What containment action is expected?

What evidence should be preserved?

What response automation may execute?
```

This allows the exercise to evaluate more than detection.

---

# 24. Phase 5 - Design the Scenario

A purple team scenario should contain enough information to reproduce the test.

Recommended fields:

```text
Scenario ID

Scenario name

Objective

Threat context

ATT&CK mapping

Scope

Target

Preconditions

Test account

Technique

Procedure

Expected prevention

Expected telemetry

Expected detection

Expected alert

Expected investigation

Expected response

Safety controls

Stop conditions

Evidence requirements

Cleanup

Owner
```

---

# 25. Scenario Template

```yaml
scenario_id: PT-001
name: Controlled Execution Validation

objective: >
  Validate whether the selected endpoint execution behaviour
  generates the expected telemetry and detection.

scope:
  environment: authorised-lab
  target: test-endpoint-01

preconditions:
  - test endpoint available
  - endpoint telemetry enabled
  - SIEM ingestion enabled
  - approved test account available

expected:
  prevention: not_expected
  telemetry: expected
  detection: expected
  alert: expected
  investigation: expected

safety:
  destructive_actions: prohibited
  persistence: prohibited
  scope_expansion: prohibited

evidence:
  - execution timestamp
  - endpoint telemetry
  - SIEM event
  - detection result
  - analyst observations

cleanup:
  - remove temporary test artifacts
```

This is illustrative.

Adapt the schema to the organisation.

---

# 26. Technique Selection

Choose the smallest safe procedure that represents the behaviour being tested.

The objective is usually not to reproduce every implementation used by a real adversary.

The objective is to validate the relevant defensive capability.

For example:

```text
Adversary Behaviour
       |
       v
Representative Procedure
       |
       v
Expected Telemetry
       |
       v
Detection
```

---

# 27. Procedure Versus Technique

A MITRE ATT&CK technique describes adversary behaviour.

A procedure is a specific implementation of that behaviour.

```text
Technique
   |
   +---- Procedure A
   |
   +---- Procedure B
   |
   +---- Procedure C
```

A detection that identifies one procedure may not detect every implementation of the technique.

This distinction is important during purple team testing.

---

# 28. Avoid Tool-Centric Validation

Weak approach:

```text
Does our detection detect Tool X?
```

Better approach:

```text
Does our detection identify the relevant adversary behaviour
across realistic implementations?
```

Tools change.

Behaviours and security objectives are more durable.

---

# 29. Phase 6 - Establish the Baseline

Before executing the adversary behaviour, confirm that the environment is working.

Check:

```text
Target reachable

Test account valid

Logging enabled

Sensor healthy

Telemetry forwarding healthy

SIEM ingestion healthy

Detection rule enabled

Alert route available

Time synchronised
```

Without a baseline, infrastructure problems may be incorrectly classified as defensive failures.

---

# 30. Baseline Telemetry

Generate a known-safe event when possible.

Example:

```text
Known Test Event
       |
       v
Endpoint Telemetry
       |
       v
Collector
       |
       v
SIEM
```

If the baseline event never reaches the SIEM, there is little value in immediately testing the detection rule.

---

# 31. Time Synchronisation

Record timestamps and timezone.

Example:

```text
Exercise Timezone:
Europe/Amsterdam

Execution:
2026-09-09 14:05:22 +02:00

SIEM Event:
2026-09-09 14:05:27 +02:00

Alert:
2026-09-09 14:05:31 +02:00
```

Time synchronisation is essential when measuring detection latency.

---

# 32. Unique Test Identifiers

Use unique markers where appropriate.

Example:

```text
PT-2026-001
```

A marker may be associated with:

```text
Scenario

Temporary file

Test account

Test hostname

Command argument

Log entry

Ticket
```

This makes evidence correlation easier.

Do not design the marker in a way that causes the detection to fire only because the marker exists.

---

# 33. Phase 7 - Execute the Scenario

Execution should follow the agreed procedure.

Record:

```text
Who executed the test?

When?

From where?

Against which target?

Which procedure?

Which variation?

What was the immediate result?
```

Avoid undocumented deviations.

If the procedure changes, record the change.

---

# 34. Execution Result

Separate:

```text
Test Execution

Security Control Result
```

Example:

```text
Test Execution:
Successful

Prevention Control:
Blocked
```

This is not contradictory.

The test successfully demonstrated that the prevention control blocked the behaviour.

---

# 35. Failed Test Execution

If the procedure itself fails:

```text
Technique not executed

No valid security conclusion
```

Do not classify:

```text
No alert = Detection failure
```

if the expected behaviour never occurred.

Instead classify the result as:

```text
Test Error

Inconclusive
```

depending on the situation.

---

# 36. Phase 8 - Observe the Defensive Response

Observe each layer separately.

```text
Execution
   |
   v
Prevented?
   |
   v
Telemetry Generated?
   |
   v
Telemetry Collected?
   |
   v
Fields Parsed?
   |
   v
Detection Fired?
   |
   v
Alert Routed?
   |
   v
Analyst Investigated?
   |
   v
Response Initiated?
```

This is one of the most important purple team analysis models.

---

# 37. Defensive Validation Matrix

Example:

| Layer | Expected | Observed | Result |
|---|---|---|---|
| Execution | Execute | Executed | Pass |
| Prevention | Not expected | Not blocked | Pass |
| Endpoint telemetry | Yes | Present | Pass |
| SIEM ingestion | Yes | Present | Pass |
| Parsing | Correct | `user.name` missing | Fail |
| Detection | Yes | No alert | Fail |
| Alert routing | Yes | Not reached | Not tested |
| Investigation | Yes | Not reached | Not tested |

This immediately identifies where deeper investigation should begin.

---

# 38. Phase 9 - Collaborative Feedback

Purple teaming should create deliberate interaction between participants.

A practical feedback loop is:

```text
Red:
"This is what we executed."

Blue:
"This is what we observed."

Red:
"This value or behaviour should have been visible."

Blue:
"This is what our telemetry contains."

Detection Engineer:
"This is why the rule did or did not match."

SOC:
"This is how the alert would be investigated."

All:
"What needs to change?"
```

The objective is shared understanding.

---

# 39. Feedback Cadence

Feedback can occur:

```text
Immediately after each test

After a group of related tests

At scheduled intervals

During a formal after-action review
```

The right cadence depends on the exercise objective.

Highly collaborative detection engineering exercises may use rapid cycles.

More realistic adversary emulation may delay feedback.

---

# 40. Exercise Modes

Purple team exercises can use different collaboration models.

## Fully Collaborative

```text
Red and Blue share activity in real time.
```

Useful for:

```text
Detection development

Telemetry troubleshooting

Knowledge transfer

Initial capability building
```

## Semi-Blind

```text
Defenders know an exercise is occurring but do not know every
procedure or exact execution time.
```

Useful for:

```text
Detection validation

SOC workflow validation

Investigation testing
```

## Blind or Low-Disclosure

```text
Defender awareness is intentionally limited.
```

Useful for selected objectives requiring more realistic observation.

This mode requires stronger governance and should not be treated as automatically superior.

---

# 41. Phase 10 - Gap Analysis

When expected behaviour does not occur, determine where the failure exists.

A useful model is:

```text
Technique Executed?
   |
   +---- No -> Test problem
   |
   v
Expected Prevention?
   |
   +---- Yes -> Was it blocked?
   |
   v
Telemetry Generated?
   |
   +---- No -> Sensor / logging gap
   |
   v
Telemetry Collected?
   |
   +---- No -> Pipeline gap
   |
   v
Fields Correct?
   |
   +---- No -> Parsing / schema gap
   |
   v
Detection Fired?
   |
   +---- No -> Detection logic gap
   |
   v
Alert Routed?
   |
   +---- No -> Alert workflow gap
   |
   v
Investigation Successful?
   |
   +---- No -> Analyst / context / process gap
   |
   v
Response Successful?
       |
       +---- No -> Response gap
```

This prevents every failure from being labelled a "detection gap".

---

# 42. Gap Categories

Useful categories include:

```text
Prevention gap

Logging gap

Sensor gap

Collection gap

Parsing gap

Schema gap

Enrichment gap

Detection gap

Alert routing gap

Investigation gap

Response gap

Documentation gap

Knowledge gap

Process gap

Configuration gap

Coverage gap

Exercise-design gap
```

A consistent taxonomy improves trend analysis.

---

# 43. Root Cause Analysis

Do not stop at:

```text
Detection did not fire.
```

Ask why.

Example:

```text
Detection did not fire
        |
        v
Required field missing
        |
        v
Parser did not populate field
        |
        v
Vendor schema changed after update
        |
        v
Detection still referenced old schema
```

Root cause:

```text
Detection dependency was not updated after the telemetry
schema changed.
```

That is much more actionable than:

```text
Detection failed.
```

---

# 44. Five Whys

The Five Whys technique can help identify systemic causes.

Example:

```text
Why did the alert not fire?
Because the rule could not find the user field.

Why?
Because the field was renamed.

Why?
Because the parser changed.

Why?
Because the platform was upgraded.

Why was the detection not updated?
Because detection regression testing was not part of the
upgrade process.
```

This can turn one exercise failure into a programme-level improvement.

---

# 45. Phase 11 - Detection Engineering

When a detection gap is confirmed:

```text
Observed Behaviour
       |
       v
Available Telemetry
       |
       v
Detection Hypothesis
       |
       v
Rule Development
       |
       v
Test
       |
       v
Tune
       |
       v
Retest
       |
       v
Document
```

Detection development should remain connected to the adversary behaviour being tested.

See [Detection Engineering](detection-engineering.md).

---

# 46. Detection Quality

Do not evaluate detection only on whether an alert exists.

Consider:

```text
Signal quality

Context

False positives

False negatives

Required fields

Alert severity

Investigation value

Robustness

Latency

Coverage across variants
```

A rule that fires but provides unusable information may still require improvement.

---

# 47. Detection Robustness

After a detection works for the initial procedure, test controlled variations.

Example:

```text
Procedure A
   |
   v
Detection Fires
   |
   v
Variation B
   |
   v
Detection Fires?
   |
   v
Variation C
   |
   v
Detection Fires?
```

The objective is to understand the detection boundary.

Do not assume one successful test proves full technique coverage.

---

# 48. Phase 12 - Retest

Every remediation should be retested.

```text
Gap
 |
 v
Improvement
 |
 v
Original Test
 |
 v
Expected Result?
 |
 +---- No -> Continue investigation
 |
 v
Controlled Variations
 |
 v
Expected Result?
 |
 +---- No -> Improve again
 |
 v
Validated
```

Without retesting, the action is implemented but not validated.

---

# 49. Original Test First

Begin the retest with the original scenario.

This answers:

```text
Did the specific failure get fixed?
```

Then test variants to answer:

```text
Did the improvement address the underlying problem?
```

---

# 50. Phase 13 - Measurement

Measurement should answer useful questions.

Examples:

```text
Did prevention work?

Was telemetry available?

Did detection fire?

How long did detection take?

Could analysts investigate?

Was the response effective?

Was the gap remediated?

Did the remediation survive retesting?

Did participant knowledge improve?

Does the control remain effective later?
```

See [Metrics and Measurement](metrics-and-measurement.md).

---

# 51. Useful Metrics

Possible metrics include:

```text
Scenario execution success rate

Prevention success rate

Telemetry availability rate

Detection success rate

Detection latency

Alert-routing success rate

Investigation success rate

Response success rate

Remediation completion rate

Validated remediation rate

Regression failure rate
```

Metrics require clear denominators.

Example:

```text
Detection Rate =
Successful Expected Detections
/
Successfully Executed Tests Where Detection Was Expected
```

Do not include tests that never executed in the denominator without explicitly defining why.

---

# 52. Time to Detect

For a single scenario:

```text
TTD =
Detection Time - Technique Execution Time
```

Example:

```text
Execution:
14:05:22

Detection:
14:05:31

TTD:
9 seconds
```

Always define the timestamps used.

---

# 53. Metrics Are Not the Goal

Avoid turning the programme into a score-generation exercise.

Weak:

```text
ATT&CK Coverage = 82%
```

without context.

Better:

```text
The programme validated 18 prioritised behaviours relevant
to the selected threat model. Fifteen generated the expected
telemetry and 12 produced the expected detections.
```

Context matters more than an impressive percentage.

---

# 54. Phase 14 - Knowledge Transfer

Purple teaming should improve what participants know and can reproduce.

Knowledge transfer may include:

```text
Red explaining adversary behaviour

Blue explaining telemetry

Detection engineers explaining rule logic

SOC analysts explaining investigation workflow

Incident responders explaining containment decisions

Threat intelligence explaining threat relevance
```

See [Knowledge Transfer](knowledge-transfer.md).

---

# 55. Teach-Back

A useful learning technique is teach-back.

Example:

```text
Red demonstrates behaviour
        |
        v
Blue observes
        |
        v
Blue explains what happened
        |
        v
Blue reproduces investigation
        |
        v
Red validates understanding
```

Knowledge is stronger when participants can independently reproduce and explain the process.

---

# 56. Knowledge Transfer Is Bidirectional

Purple teaming should not imply:

```text
Red teaches Blue.
```

A stronger model is:

```text
Red <------> Blue
 |             |
 v             v
Attack       Detection
Knowledge    Knowledge
 |             |
 +-------> Shared Understanding
```

Defenders often provide knowledge that changes how offensive participants understand the environment.

---

# 57. Phase 15 - After-Action Review

After the exercise, conduct a structured review.

Questions should include:

```text
What was expected?

What actually happened?

What worked?

What failed?

What was unexpected?

Why did the difference occur?

What did participants learn?

What needs to change?

Who owns each action?

How will improvements be validated?
```

See [After-Action Review](after-action-review.md).

---

# 58. Lessons Identified Versus Lessons Learned

A useful distinction is:

```text
Lesson Identified
       |
       v
Action Assigned
       |
       v
Improvement Implemented
       |
       v
Retested
       |
       v
Improvement Validated
       |
       v
Lesson Learned
```

A lesson is not fully learned merely because it appears in an AAR document.

---

# 59. Action Tracking

A practical action record may contain:

| Field | Example |
|---|---|
| Action ID | PT-ACT-017 |
| Scenario | PT-006 |
| Gap | Parser field missing |
| Root cause | Schema changed |
| Owner | Detection Engineering |
| Priority | High |
| Due date | 2026-09-30 |
| Status | In Progress |
| Retest required | Yes |
| Validation status | Pending |

Actions should remain visible until validated.

---

# 60. Phase 16 - Continuous Validation

Successful purple team tests can become repeatable validation cases.

```text
Purple Team Scenario
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
Validated
        |
        v
Regression Test
        |
        v
Recurring Validation
```

See [Continuous Validation](continuous-validation.md).

---

# 61. What to Convert Into Regression Tests

Good candidates include:

```text
Previously failed detections

Critical prevention controls

High-risk attack paths

Important identity controls

Critical cloud controls

Telemetry dependencies

Parser dependencies

Detection rules

Alert-routing workflows
```

Not every manual exercise needs to become an automated test.

---

# 62. Change-Triggered Validation

Some tests should run after important changes.

Examples:

```text
EDR upgrade

SIEM upgrade

Parser change

Detection-rule change

Logging-policy change

Identity-policy change

Cloud configuration change

Network segmentation change

Major application release
```

This helps detect regressions before they remain unnoticed for long periods.

---

# 63. Exercise Evidence Model

For each scenario, capture evidence across the defensive chain.

```text
Execution Evidence
       |
       v
Host Evidence
       |
       v
Telemetry Evidence
       |
       v
SIEM Evidence
       |
       v
Detection Evidence
       |
       v
Alert Evidence
       |
       v
Investigation Evidence
       |
       v
Response Evidence
```

The exact evidence required depends on the objective.

---

# 64. Evidence Quality

Evidence should answer:

```text
What happened?

When?

Where?

Who performed it?

Which system observed it?

What security control responded?

What conclusion does the evidence support?
```

Avoid collecting large volumes of screenshots that do not support a specific conclusion.

---

# 65. Evidence Record

Example:

```text
Scenario:
PT-006

Execution:
2026-09-09 14:05:22 +02:00

Target:
WIN-TEST-01

Test Account:
purple-test-01

Endpoint Event:
Observed

SIEM Event:
Observed

Detection:
Not observed

Root Cause:
Detection expected field user.name, but current parser
populated user.target.name.

Action:
Update detection schema mapping and add regression test.
```

---

# 66. Evidence Handling

Exercise evidence may contain:

```text
Hostnames

Usernames

Internal addresses

Security-control configuration

Detection logic

Threat intelligence

Incident-response procedures
```

Apply appropriate access controls and retention requirements.

Do not place sensitive operational evidence in public repositories.

---

# 67. Exercise Roles

A purple team exercise may involve several roles.

| Role | Responsibility |
|---|---|
| Exercise Lead | Coordinates exercise |
| Red / Offensive | Executes authorised adversary behaviours |
| Blue / SOC | Observes, investigates and responds |
| Detection Engineer | Analyses and improves detections |
| Threat Intelligence | Provides threat context |
| Incident Response | Validates response workflows |
| Security Engineering | Implements control improvements |
| Observer | Records evidence and observations |
| Business Owner | Supports scope and risk decisions |

One person may perform multiple roles in smaller organisations.

---

# 68. Exercise Lead

The exercise lead should help ensure:

```text
Objectives remain clear

Scope is respected

Safety controls remain active

Participants understand the current phase

Evidence is captured

Actions are recorded

Stop conditions are enforced

Retesting occurs
```

The role should facilitate collaboration rather than act as a scorekeeper.

---

# 69. Observer

An observer can record:

```text
Execution time

Detection time

Questions raised

Communication flow

Investigation steps

Unexpected events

Knowledge gaps

Decisions

Actions
```

Observer notes can provide useful qualitative evidence that technical logs do not capture.

---

# 70. Communication

Define exercise communication channels before execution.

Examples:

```text
Dedicated Teams channel

Slack channel

Bridge call

Exercise ticket

Shared document
```

Avoid mixing exercise coordination with unrelated operational communication where possible.

---

# 71. Communication Markers

Clearly identify exercise communication.

Example:

```text
[PURPLE-EXERCISE PT-006]
```

This reduces confusion during active testing.

---

# 72. Real Incident During Exercise

Define what happens if a real incident occurs.

A common principle is:

```text
Real Incident
     |
     v
Exercise Suspended
     |
     v
Operational Incident Process Takes Priority
```

The exact process should be defined before the exercise begins.

---

# 73. Exercise Cadence

Purple teaming can operate at several cadences.

Examples:

```text
Continuous small validation tests

Weekly detection-engineering sessions

Monthly focused exercises

Quarterly scenario-based exercises

Annual large-scale exercises

Change-triggered validation
```

Cadence should reflect:

```text
Risk

Threat change

Control change

Available resources

Business criticality

Learning needs
```

---

# 74. Small Iterations

Large annual exercises are not the only model.

Small cycles can be highly effective:

```text
One Behaviour
     |
     v
One Detection
     |
     v
One Gap
     |
     v
One Improvement
     |
     v
One Retest
```

Repeated frequently, these cycles can create substantial defensive improvement.

---

# 75. Exercise Planning Record

A planning record may contain:

```text
Exercise ID:

Objective:

Threat Context:

Business Context:

ATT&CK Techniques:

Targets:

Participants:

Exercise Mode:

Start Time:

End Time:

Expected Prevention:

Expected Telemetry:

Expected Detections:

Expected Response:

Safety Controls:

Stop Conditions:

Evidence Required:

Success Criteria:

AAR Date:

Owners:
```

---

# 76. Scenario Result Record

```text
Scenario ID:

Execution Status:

Execution Timestamp:

Prevention Result:

Telemetry Generated:

Telemetry Collected:

Parsing Result:

Detection Result:

Alert Result:

Investigation Result:

Response Result:

Knowledge Observations:

Gap Category:

Root Cause:

Action Required:

Owner:

Retest Required:

Retest Result:
```

---

# 77. Result States

Use consistent result states.

For example:

```text
PASS

FAIL

PARTIAL

INCONCLUSIVE

ERROR

NOT TESTED

NOT APPLICABLE
```

Define them centrally so participants interpret them consistently.

---

# 78. PASS

Use `PASS` when:

```text
The test executed correctly

and

The expected security outcome occurred
```

Example:

```text
Expected:
Detection should fire.

Observed:
Detection fired with required context.

Result:
PASS
```

---

# 79. FAIL

Use `FAIL` when:

```text
The test executed correctly

but

The expected security outcome did not occur
```

Example:

```text
Expected:
Detection should fire.

Observed:
Telemetry was present but no detection fired.

Result:
FAIL
```

---

# 80. INCONCLUSIVE

Use `INCONCLUSIVE` when the evidence cannot support a reliable security conclusion.

Example:

```text
Technique executed

but

Telemetry pipeline experienced an unrelated outage
```

The scenario should normally be repeated.

---

# 81. ERROR

Use `ERROR` when the test procedure itself did not execute correctly.

Example:

```text
Test harness failed before the intended behaviour occurred.
```

Do not classify this as a defensive failure.

---

# 82. Common Methodology Failure - Testing Without an Objective

Weak:

```text
Run a collection of attack tools and see what happens.
```

Better:

```text
Define the defensive capability to validate and select
representative behaviours that exercise it.
```

---

# 83. Common Methodology Failure - Counting Techniques

A high number of executed ATT&CK techniques does not prove strong purple team maturity.

Ask instead:

```text
Were the techniques relevant?

Were controls validated?

Were gaps understood?

Were improvements implemented?

Were improvements retested?

Was knowledge retained?
```

---

# 84. Common Methodology Failure - Alert Equals Success

An alert firing does not automatically mean the defensive capability is effective.

Evaluate:

```text
Was the correct activity detected?

Was context sufficient?

Was severity appropriate?

Could the analyst understand it?

Could related activity be found?

Was the alert timely?

Did it survive variations?
```

---

# 85. Common Methodology Failure - No Alert Equals Detection Failure

A missing alert can originate from:

```text
Test failure

Missing telemetry

Sensor failure

Collection failure

Parser failure

Schema mismatch

Detection logic

Rule disabled

Alert routing
```

Trace the full chain before assigning root cause.

---

# 86. Common Methodology Failure - No Retest

This process is incomplete:

```text
Exercise
   |
   v
Gap
   |
   v
Ticket
   |
   v
Closed
```

Prefer:

```text
Exercise
   |
   v
Gap
   |
   v
Root Cause
   |
   v
Improvement
   |
   v
Retest
   |
   v
Validated
```

---

# 87. Common Methodology Failure - Tool Focus

Purple teaming should not become a demonstration of offensive tools.

The tool is an implementation detail.

Focus on:

```text
Behaviour

Telemetry

Detection

Investigation

Response

Learning
```

---

# 88. Common Methodology Failure - Red Versus Blue Competition

Purple teaming is not primarily about determining which team "won".

A useful failure is often more valuable than an easy success.

```text
Failure
   |
   v
Understanding
   |
   v
Improvement
   |
   v
Retest
   |
   v
Capability Increase
```

---

# 89. Common Methodology Failure - Hiding Information

Secrecy can be appropriate for selected validation objectives.

It should not be the default simply because red team operations often use it.

If the objective is:

```text
Build a detection
```

real-time collaboration may be best.

If the objective is:

```text
Measure SOC discovery without prior knowledge
```

limited information may be appropriate.

Choose the exercise mode based on the objective.

---

# 90. Common Methodology Failure - No Ownership

A gap without an owner often remains unresolved.

Every improvement action should have:

```text
Owner

Priority

Due date

Validation requirement

Status
```

---

# 91. Common Methodology Failure - Closing on Implementation

Do not automatically close an action because:

```text
Rule updated

Policy changed

Logging enabled

Configuration modified
```

Close it when the expected outcome has been validated.

```text
Implemented
    !=
Validated
```

---

# 92. Maturity Model

A simple purple team maturity model can help assess programme development.

## Level 1 - Ad Hoc

```text
Occasional collaboration

Limited documentation

No consistent scenarios

Little measurement

Improvements not systematically retested
```

## Level 2 - Repeatable

```text
Defined exercise process

Documented scope

Reusable scenarios

Basic metrics

Actions tracked
```

## Level 3 - Integrated

```text
Threat-informed prioritisation

Detection engineering integrated

Structured knowledge transfer

AAR process

Validated remediation
```

## Level 4 - Measured

```text
Consistent metrics

Trend analysis

Detection latency measured

Gap categories analysed

Regression tracked
```

## Level 5 - Continuous

```text
High-value scenarios become regression tests

Change-triggered validation

Continuous control validation

Lessons influence engineering

Programme adapts to threat and environment changes
```

Maturity should reflect capability, not simply the number of tools or exercises.

---

# 93. Practical Scenario

Consider an authorised exercise designed to validate endpoint execution detection.

Objective:

```text
Determine whether the selected execution behaviour produces
the expected endpoint telemetry and SIEM detection and whether
the SOC can investigate the activity.
```

Expected chain:

```text
Execution
   |
   v
Endpoint Event
   |
   v
EDR
   |
   v
SIEM
   |
   v
Detection Rule
   |
   v
SOC Alert
```

---

## Step 1 - Baseline

The team confirms:

```text
Endpoint sensor:
Healthy

SIEM ingestion:
Healthy

Detection rule:
Enabled

Test account:
Available

Time synchronisation:
Confirmed
```

---

## Step 2 - Execute

The offensive participant performs the authorised representative procedure.

Record:

```text
Scenario:
PT-EXEC-001

Target:
WIN-TEST-01

Account:
purple-test-01

Execution:
14:05:22
```

---

## Step 3 - Observe Endpoint Telemetry

Endpoint telemetry appears.

Result:

```text
Telemetry Generation:
PASS
```

Relevant fields include:

```text
host

user

process

parent process

command line

timestamp
```

---

## Step 4 - Observe SIEM

The event reaches the SIEM.

Result:

```text
Collection:
PASS
```

However:

```text
user.name:
missing
```

The current parser places the value in:

```text
user.target.name
```

---

## Step 5 - Detection

The expected detection does not fire.

Initial result:

```text
Detection:
FAIL
```

Do not immediately conclude that the detection logic itself is conceptually wrong.

---

## Step 6 - Root Cause

The team reviews the rule.

It expects:

```text
user.name
```

but the current event schema contains:

```text
user.target.name
```

Root cause:

```text
The telemetry parser schema changed after a platform update,
but the dependent detection rule was not updated.
```

---

## Step 7 - Improve

The detection engineering team updates the field mapping and validates the query against the current telemetry.

---

## Step 8 - Retest

The original scenario is executed again.

Observed:

```text
Telemetry:
PASS

Collection:
PASS

Parsing:
PASS

Detection:
PASS

Alert Routing:
PASS
```

---

## Step 9 - Investigation

The SOC analyst can identify:

```text
Target host

Test account

Process

Parent process

Execution timestamp

Related activity
```

Result:

```text
Investigation:
PASS
```

---

## Step 10 - Programme Improvement

The AAR identifies a broader issue:

```text
Security platform upgrades can change telemetry schemas
without automatically triggering detection regression tests.
```

Improvement:

```text
Add detection validation to the platform upgrade process.
```

The scenario becomes a regression test.

The exercise therefore improved more than one detection.

It improved the engineering process around detection dependencies.

---

# 94. Purple Team Exercise Checklist

## Before the Exercise

- [ ] Confirm authorisation
- [ ] Define objective
- [ ] Define scope
- [ ] Define exclusions
- [ ] Define participants
- [ ] Define exercise mode
- [ ] Define Rules of Engagement
- [ ] Define stop conditions
- [ ] Identify threat context
- [ ] Select relevant behaviours
- [ ] Map ATT&CK where useful
- [ ] Map expected controls
- [ ] Map expected telemetry
- [ ] Map expected detections
- [ ] Define response expectations
- [ ] Define success criteria
- [ ] Define evidence requirements
- [ ] Confirm cleanup requirements
- [ ] Confirm communication channels
- [ ] Confirm real-incident process

## Baseline

- [ ] Target available
- [ ] Test account available
- [ ] Sensor healthy
- [ ] Logging enabled
- [ ] Telemetry forwarding healthy
- [ ] SIEM ingestion healthy
- [ ] Detection enabled
- [ ] Alert route available
- [ ] Time synchronised
- [ ] Test identifier assigned

## During Execution

- [ ] Record execution time
- [ ] Record target
- [ ] Record test identity
- [ ] Record procedure
- [ ] Confirm procedure executed
- [ ] Observe prevention
- [ ] Observe telemetry
- [ ] Observe collection
- [ ] Observe parsing
- [ ] Observe detection
- [ ] Observe alert routing
- [ ] Observe investigation
- [ ] Observe response
- [ ] Record unexpected behaviour
- [ ] Maintain scope
- [ ] Monitor stop conditions

## Gap Analysis

- [ ] Confirm test executed
- [ ] Identify failing layer
- [ ] Categorise gap
- [ ] Determine root cause
- [ ] Identify contributing factors
- [ ] Identify owner
- [ ] Define improvement
- [ ] Define retest requirement

## Retest

- [ ] Execute original scenario
- [ ] Confirm expected outcome
- [ ] Test relevant variations
- [ ] Confirm evidence
- [ ] Record result
- [ ] Close only after validation

## After the Exercise

- [ ] Conduct AAR
- [ ] Record lessons
- [ ] Assign actions
- [ ] Record owners
- [ ] Record due dates
- [ ] Measure outcomes
- [ ] Capture knowledge transfer
- [ ] Update documentation
- [ ] Identify regression-test candidates
- [ ] Schedule continuous validation where appropriate
- [ ] Complete cleanup

---

# 95. Purple Team Scenario Template

```text
Scenario ID:

Scenario Name:

Objective:

Threat Context:

Business Context:

ATT&CK Technique:

ATT&CK Sub-Technique:

Scope:

Target:

Test Identity:

Preconditions:

Procedure:

Expected Prevention:

Expected Telemetry:

Expected Collection:

Expected Parsing:

Expected Detection:

Expected Alert:

Expected Investigation:

Expected Response:

Exercise Mode:

Safety Controls:

Stop Conditions:

Execution Timestamp:

Observed Prevention:

Observed Telemetry:

Observed Collection:

Observed Parsing:

Observed Detection:

Observed Alert:

Observed Investigation:

Observed Response:

Gap Category:

Root Cause:

Improvement:

Owner:

Retest Required:

Retest Result:

Knowledge Transfer Notes:

Evidence Location:

Cleanup Status:
```

---

# 96. Quick Methodology

```text
AUTHORISE
    |
    v
DEFINE OBJECTIVE
    |
    v
PRIORITISE THREAT
    |
    v
SELECT BEHAVIOUR
    |
    v
MAP ATT&CK
    |
    v
MAP CONTROLS
    |
    v
MAP TELEMETRY
    |
    v
MAP DETECTION
    |
    v
DEFINE SUCCESS
    |
    v
BASELINE
    |
    v
EXECUTE
    |
    v
OBSERVE
    |
    v
COLLABORATE
    |
    v
IDENTIFY GAP
    |
    v
ROOT CAUSE
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
TRANSFER KNOWLEDGE
    |
    v
AAR
    |
    v
REGRESSION TEST
    |
    v
CONTINUOUS VALIDATION
```

---

# 97. Purple Teaming Mindset

Do not think:

```text
Red Team versus Blue Team

More ATT&CK techniques = better programme

Alert fired = complete success

No alert = detection-rule failure

Tool execution = adversary emulation

Ticket closed = issue fixed

Exercise completed = improvement achieved
```

Instead think:

```text
What behaviour matters?
        |
        v
What security outcome do we expect?
        |
        v
What should prevent it?
        |
        v
What telemetry should exist?
        |
        v
What should detect it?
        |
        v
Can analysts investigate it?
        |
        v
Can responders act?
        |
        v
Where did the chain fail?
        |
        v
Why?
        |
        v
What should change?
        |
        v
Did the change work?
        |
        v
Can we validate it again later?
```

Purple teaming is most valuable when it converts security testing into measurable defensive improvement.

---

# 98. Final Purple Teaming Model

A mature purple team methodology connects:

```text
THREAT RELEVANCE
       |
       v
BUSINESS RISK
       |
       v
AUTHORISED SCENARIO
       |
       v
ADVERSARY BEHAVIOUR
       |
       v
PREVENTION
       |
       v
TELEMETRY
       |
       v
COLLECTION
       |
       v
DETECTION
       |
       v
ALERT
       |
       v
INVESTIGATION
       |
       v
RESPONSE
       |
       v
GAP ANALYSIS
       |
       v
ROOT CAUSE
       |
       v
IMPROVEMENT
       |
       v
RETEST
       |
       v
MEASUREMENT
       |
       v
KNOWLEDGE TRANSFER
       |
       v
AFTER-ACTION REVIEW
       |
       v
CONTINUOUS VALIDATION
       |
       v
IMPROVED CYBER RESILIENCE
```

The success of a purple team programme should therefore not be judged only by:

```text
Number of exercises

Number of techniques

Number of alerts

Number of tools
```

It should be judged by whether the organisation can demonstrate:

```text
Relevant adversary behaviours are understood

Security controls are validated

Telemetry gaps are identified

Detections are improved

Analysts can investigate

Response processes are validated

Knowledge is transferred

Improvements are retested

Regressions are detected

Lessons influence future security engineering
```

That is the core purpose of a structured purple teaming methodology.

---

# Related Notes

- [Purple Teaming](index.md)
- [Purple Team Exercises](exercises.md)
- [MITRE ATT&CK for Purple Teaming](mitre-attack.md)
- [Detection Engineering](detection-engineering.md)
- [Knowledge Transfer](knowledge-transfer.md)
- [Metrics and Measurement](metrics-and-measurement.md)
- [After-Action Review](after-action-review.md)
- [Continuous Validation](continuous-validation.md)
- [Red Teaming](../red-teaming/index.md)

---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK Data Sources](https://attack.mitre.org/datasources/){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NICE Workforce Framework for Cybersecurity](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center){ target="_blank" rel="noopener noreferrer" }

!!! tip "Start with the objective"

    Select adversary behaviours because they help answer an important security question, not because they increase an ATT&CK coverage percentage.

!!! tip "Trace the entire defensive chain"

    When a detection does not fire, determine whether the failure occurred during execution, telemetry generation, collection, parsing, detection logic, alert routing or another layer before assigning the root cause.

!!! tip "Retest every meaningful improvement"

    Implementing a new rule or configuration does not prove that the original gap has been resolved. Repeat the original scenario and validate the expected security outcome.

!!! tip "Convert lessons into repeatable tests"

    High-value scenarios and previously failed controls are strong candidates for regression testing and continuous validation.

!!! warning "Purple teaming requires authorisation"

    Execute adversary behaviours only against approved targets and within documented Rules of Engagement. Define stop conditions and safety controls before testing begins.

!!! warning "ATT&CK is a knowledge base, not a score"

    ATT&CK is valuable for describing and organising adversary behaviour, but a large technique count does not by itself demonstrate effective defensive coverage.
