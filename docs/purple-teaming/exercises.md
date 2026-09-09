---
title: Purple Team Exercises
description: Practical guidance for designing, executing, observing, measuring and improving authorised purple team exercises using threat-informed scenarios and structured red-blue collaboration.
---

# Purple Team Exercises

Purple team exercises are controlled security activities in which offensive and defensive participants work together to validate and improve security controls.

The purpose is not simply to execute attack techniques.

A useful exercise connects:

```text
Threat-Relevant Behaviour
          |
          v
Controlled Execution
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
Learning
          |
          v
Improvement
          |
          v
Retest
```

A successful exercise should leave the organisation with stronger defensive capability than it had before the exercise.

---

# 1. Exercise Objectives

Every exercise should begin with a clearly defined objective.

Avoid objectives such as:

```text
Test the SOC.

Test EDR.

Run ATT&CK techniques.

See what gets detected.
```

These are too broad to produce defensible conclusions.

Prefer objectives such as:

```text
Validate whether endpoint controls generate sufficient
telemetry to detect and investigate the selected credential
access behaviour on authorised Windows test systems.
```

or:

```text
Determine whether the SOC can identify, investigate and
escalate the selected lateral movement behaviour using
currently deployed telemetry and detection rules.
```

The objective determines what should be executed, observed and measured.

---

# 2. Exercise Scope

Define scope before execution.

Document:

```text
Environment

Networks

Hosts

Applications

Cloud accounts

Identity systems

Test accounts

Source infrastructure

Permitted techniques

Excluded techniques

Permitted data

Testing window
```

Example:

```text
Environment:
Authorised corporate test environment

Targets:
WIN-TEST-01
WIN-TEST-02

Test Identity:
purple-test-user

Permitted:
Process execution
File creation
Authentication testing
Selected discovery

Prohibited:
Destructive actions
Production persistence
Real credential theft
Data exfiltration
Denial of service
```

The exact restrictions depend on the environment and authorisation.

---

# 3. Rules of Engagement

The Rules of Engagement should define how the exercise operates.

Recommended fields include:

```text
Exercise ID

Exercise owner

Authorising party

Business owner

Participants

Targets

Excluded assets

Allowed techniques

Prohibited techniques

Testing window

Source systems

Test identities

Communication channel

Emergency contacts

Stop conditions

Evidence requirements

Cleanup requirements
```

All participants should understand the applicable boundaries.

---

# 4. Exercise Safety

Purple teaming does not remove the operational risk associated with adversary simulation.

Prefer:

```text
Dedicated test accounts

Synthetic data

Non-destructive procedures

Bounded targets

Known source systems

Rate limits

Temporary artifacts

Explicit cleanup

Snapshots where appropriate

Controlled execution windows
```

Exercise safety should be designed before execution rather than added after something goes wrong.

---

# 5. Stop Conditions

Define explicit conditions that stop or suspend testing.

Examples include:

```text
Unexpected production outage

Unintended access to sensitive information

Activity reaches an excluded system

Unexpected account lockout

Uncontrolled resource consumption

Unintended persistence

Unexpected security-control instability

Potential real incident discovered

Business owner requests suspension
```

A stop condition should have:

```text
Trigger
   |
   v
Stop Execution
   |
   v
Notify Exercise Lead
   |
   v
Assess Situation
   |
   +-------------------+
   |                   |
   v                   v
Resume               Terminate
```

---

# 6. Threat-Informed Exercise Design

Exercise scenarios should be connected to relevant threat behaviour.

Potential inputs include:

```text
Threat intelligence

Incident history

Red team findings

Penetration test findings

Detection gaps

Vulnerability findings

Attack-path analysis

SOC observations

Business risks

Security-control changes
```

Then use ATT&CK where useful to describe the behaviour consistently.

Do not begin by selecting random ATT&CK techniques solely to increase coverage.

---

# 7. Prioritising Exercise Scenarios

A simple prioritisation model can consider:

| Factor | Question |
|---|---|
| Threat relevance | Is the behaviour relevant to realistic adversaries? |
| Business impact | Could the behaviour affect important assets? |
| Exposure | Is the path realistically reachable? |
| Detection confidence | Do we know whether it is detected? |
| Historical gaps | Has this control failed previously? |
| Change rate | Has the control or environment recently changed? |
| Learning value | Will testing improve team capability? |
| Regression risk | Could a previous improvement have broken? |

High-value exercises usually combine several of these factors.

---

# 8. Exercise Types

Purple team exercises can be organised in several ways.

## Technique-Focused Exercise

Validates one specific adversary behaviour.

Example:

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
Improve
   |
   v
Retest
```

Useful for:

```text
Detection development

Telemetry validation

Training

Regression testing
```

---

## Scenario-Based Exercise

Combines several behaviours into a realistic attack sequence.

Example:

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
```

Useful for evaluating interactions between multiple controls.

---

## Detection Engineering Exercise

Focused primarily on improving a specific detection.

```text
Behaviour
    |
    v
Generate Telemetry
    |
    v
Inspect Data
    |
    v
Develop Detection
    |
    v
Execute Again
    |
    v
Tune
    |
    v
Validate
```

---

## Control Validation Exercise

Focused on determining whether a security control behaves as expected.

Examples:

```text
Endpoint prevention

Application control

Identity policy

Network segmentation

Email filtering

Cloud controls

Logging controls
```

---

## SOC Validation Exercise

Focused on analyst workflows.

```text
Activity
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
Escalation
   |
   v
Response
```

---

## Regression Exercise

Repeats previously validated scenarios to determine whether defensive capability remains effective.

```text
Previous Gap
     |
     v
Improvement
     |
     v
Previously Passing Test
     |
     v
Execute Again
     |
     v
Still Passing?
```

---

# 9. Exercise Collaboration Models

Different objectives require different levels of information sharing.

## Fully Collaborative

Both offensive and defensive participants know:

```text
What will be executed

When it will be executed

Where it will be executed

What should be observed
```

Best suited to:

```text
Detection development

Telemetry troubleshooting

Knowledge transfer

Early programme maturity
```

---

## Semi-Blind

Defenders know that an exercise is occurring but do not know every detail.

They may not know:

```text
Exact execution time

Exact target

Exact technique variation
```

Useful for:

```text
SOC validation

Detection validation

Investigation testing
```

---

## Low-Disclosure

Defender knowledge is intentionally limited.

This can be appropriate when evaluating:

```text
Independent detection

Escalation

Investigation

Operational response
```

It requires stronger coordination and safety controls.

Low disclosure should be selected because it supports the objective, not because secrecy is assumed to be more realistic or mature.

---

# 10. Exercise Roles

Typical roles include:

| Role | Responsibility |
|---|---|
| Exercise Lead | Coordinates the exercise |
| Offensive Participant | Executes authorised behaviours |
| Defensive Participant | Observes and investigates |
| Detection Engineer | Analyses and improves detections |
| SOC Analyst | Performs triage and investigation |
| Threat Intelligence | Provides threat context |
| Incident Response | Evaluates response processes |
| Security Engineer | Implements control changes |
| Observer | Records events and observations |
| Business Owner | Supports risk and scope decisions |

Smaller organisations may combine several roles.

---

# 11. Exercise Lead

The exercise lead coordinates:

```text
Scope

Objectives

Safety

Communication

Execution sequence

Evidence

Stop conditions

Actions

Retesting
```

The exercise lead should ensure that the exercise remains focused on the agreed objective.

---

# 12. Offensive Participant

The offensive participant should understand:

```text
Threat behaviour

Procedure

Target

Expected security controls

Safety boundaries

Evidence requirements

Cleanup
```

The role is not simply:

```text
Run attack tool.
```

The participant should be able to explain:

```text
What behaviour occurred?

What should defenders have observed?

Which artifacts should exist?

What variations may matter?
```

---

# 13. Defensive Participant

The defensive participant should evaluate:

```text
Prevention

Telemetry

Detection

Alert context

Investigation

Response
```

The defensive role should also explain what is missing when an expected result does not occur.

---

# 14. Observer

An observer can record information that may not appear in technical logs.

Examples:

```text
Execution timestamps

Communication

Questions

Analyst decisions

Investigation steps

Confusion

Unexpected results

Knowledge gaps

Manual workarounds

Action items
```

Observer notes can provide valuable qualitative evidence.

---

# 15. Scenario Design

Each scenario should answer:

```text
Why are we testing this?

What behaviour are we testing?

Where will it execute?

What must exist before execution?

What should prevent it?

What telemetry should it generate?

What should detect it?

What should analysts see?

What response is expected?

What evidence will prove the result?

What are the safety controls?

How will cleanup occur?
```

---

# 16. Scenario Template

A practical scenario record may look like:

```yaml
scenario_id: PT-001

name: Controlled Execution Validation

objective: >
  Validate whether the selected execution behaviour generates
  the expected endpoint telemetry and SIEM detection.

threat_context:
  source: internal threat model

attack_mapping:
  framework: MITRE ATT&CK
  technique: selected technique

scope:
  environment: authorised-test-environment
  target: WIN-TEST-01
  account: purple-test-user

preconditions:
  - endpoint sensor healthy
  - SIEM ingestion healthy
  - detection enabled
  - test account available

expected:
  prevention: not_expected
  telemetry: expected
  collection: expected
  detection: expected
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
  - analyst notes

cleanup:
  - remove temporary artifacts
```

This schema is illustrative.

Adapt it to the organisation and security platforms.

---

# 17. Scenario IDs

Assign each scenario a unique identifier.

Example:

```text
PT-001

PT-002

PT-003
```

For larger programmes:

```text
PT-ENDPOINT-001

PT-IDENTITY-001

PT-CLOUD-001

PT-NETWORK-001
```

Scenario IDs simplify:

```text
Evidence correlation

Metrics

Tickets

Retesting

Reporting

Regression tracking
```

---

# 18. Preconditions

Document conditions that must exist before the scenario can be executed.

Examples:

```text
Target online

Required service running

Test account available

Sensor healthy

Logging enabled

Telemetry forwarding enabled

Detection rule enabled

Required feature enabled
```

If a precondition is not satisfied, the result may be invalid.

---

# 19. Expected Results

Define expectations before execution.

For example:

```text
Expected Execution:
Behaviour should execute.

Expected Prevention:
No prevention expected.

Expected Telemetry:
Process event should be generated.

Expected Collection:
Event should reach SIEM.

Expected Detection:
Detection should fire.

Expected Alert:
Alert should reach SOC queue.

Expected Investigation:
Analyst should identify host, user and process.

Expected Response:
Not tested.
```

This prevents post-test reinterpretation.

---

# 20. Defensive Layers

Evaluate the defensive chain separately.

```text
Attack Behaviour
      |
      v
Prevention
      |
      v
Telemetry Generation
      |
      v
Collection
      |
      v
Parsing
      |
      v
Enrichment
      |
      v
Detection
      |
      v
Alert Routing
      |
      v
Investigation
      |
      v
Response
```

A failure at one layer can prevent later layers from being evaluated.

---

# 21. Prevention

Determine whether prevention is expected.

Possible states:

```text
Expected

Not Expected

Not Applicable
```

Example:

```text
Expected:
Application control should prevent execution.

Observed:
Execution blocked.

Result:
PASS
```

The offensive procedure failing because the defensive control blocked it can represent a successful security result.

---

# 22. Telemetry Generation

Determine whether the endpoint, service or platform generated the expected telemetry.

Questions include:

```text
Was an event generated?

Did it contain the expected timestamp?

Was the correct user recorded?

Was the correct process recorded?

Was command-line information available?

Was the target resource recorded?

Was the source system recorded?
```

No telemetry at the source indicates a different problem than telemetry being lost later.

---

# 23. Telemetry Collection

Next determine whether the telemetry reached the intended security platform.

```text
Source Event
    |
    v
Collector
    |
    v
Forwarder
    |
    v
Processing
    |
    v
SIEM
```

Possible failures include:

```text
Collector unavailable

Forwarder misconfiguration

Filtering

Dropped events

Incorrect index

Incorrect data stream

Pipeline delay
```

---

# 24. Parsing

An event reaching the SIEM does not mean the data is usable.

Check:

```text
Field names

Field values

Data types

Timestamps

Source identity

Destination identity

User identity

Process information

Network information
```

Example:

```text
Expected:
user.name

Observed:
user.target.name
```

A parser or schema mismatch can break dependent detection logic.

---

# 25. Enrichment

Detection may depend on additional context.

Examples:

```text
Asset criticality

User privilege

Hostname mapping

Threat intelligence

Identity information

Network zone

Cloud account

Device ownership
```

Validate whether required enrichment exists when the detection depends on it.

---

# 26. Detection

A detection test should answer:

```text
Did the rule execute?

Did the relevant event match?

Did an alert or finding result?

Was the severity correct?

Was the detection timely?

Was the context useful?
```

Do not stop at:

```text
Alert = yes.
```

Detection quality matters.

---

# 27. Alert Routing

An alert may be generated but fail to reach the analyst.

Validate where appropriate:

```text
SIEM alert

SOC queue

Case management

Ticketing

SOAR

Notification channel
```

Example:

```text
Detection:
PASS

Alert Routing:
FAIL
```

This distinction matters.

---

# 28. Investigation

Where investigation is in scope, evaluate whether the analyst can answer:

```text
What happened?

Which host was involved?

Which account was involved?

What process or service was involved?

What occurred before the event?

What occurred afterwards?

Are other systems affected?

Does the behaviour require escalation?
```

A detection with insufficient context may slow or prevent investigation.

---

# 29. Response

Response validation may include:

```text
Escalation

Account containment

Endpoint isolation

Process termination

Credential reset

Network blocking

Incident creation

Evidence preservation
```

Only perform response actions that are explicitly authorised for the exercise.

---

# 30. Baseline Validation

Before the scenario, validate the environment.

Example:

```text
Target:
Reachable

Sensor:
Healthy

Telemetry:
Flowing

SIEM:
Receiving events

Detection:
Enabled

SOC queue:
Available

Clock:
Synchronised
```

This reduces false conclusions caused by unrelated infrastructure problems.

---

# 31. Baseline Event

Where practical, generate a known-safe event.

```text
Known Event
    |
    v
Telemetry Generated?
    |
    v
Collected?
    |
    v
Queryable?
```

If the baseline fails, resolve that issue before continuing with the main scenario.

---

# 32. Time Synchronisation

Record:

```text
Timezone

Execution timestamp

Telemetry timestamp

Detection timestamp

Alert timestamp

Investigation timestamp
```

Example:

```text
Timezone:
Europe/Amsterdam

Execution:
14:10:04.220

Telemetry:
14:10:05.103

Detection:
14:10:10.812

Alert:
14:10:12.001
```

This supports latency measurement.

---

# 33. Unique Test Markers

Unique identifiers can help correlate evidence.

Example:

```text
PT-2026-EXEC-001
```

Possible uses:

```text
Temporary filename

Command argument

Synthetic object

Test account

Ticket

Evidence directory
```

The marker should support correlation without becoming the sole reason a detection fires.

---

# 34. Exercise Execution

During execution, record:

```text
Scenario ID

Participant

Target

Source

Account

Start time

Procedure

Variation

Immediate result

Stop conditions encountered
```

Keep the record close to real time.

---

# 35. Execution Confirmation

Before evaluating the defensive response, confirm that the intended behaviour actually occurred.

```text
Procedure Started
       |
       v
Behaviour Occurred?
    /        \
  No          Yes
  |            |
  v            v
Test Error   Evaluate Controls
```

If the behaviour did not occur, a missing detection cannot reliably be classified as a detection failure.

---

# 36. Result States

Use consistent result states.

Recommended:

```text
PASS

FAIL

PARTIAL

INCONCLUSIVE

ERROR

NOT TESTED

NOT APPLICABLE
```

Document what each state means.

---

# 37. PASS

Use `PASS` when:

```text
The scenario executed correctly

and

The expected security outcome occurred.
```

Example:

```text
Expected:
Telemetry should reach the SIEM.

Observed:
Telemetry reached the SIEM with required fields.

Result:
PASS
```

---

# 38. FAIL

Use `FAIL` when:

```text
The scenario executed correctly

but

The expected security outcome did not occur.
```

Example:

```text
Expected:
Detection should fire.

Observed:
Relevant telemetry was present but the detection did not fire.

Result:
FAIL
```

---

# 39. PARTIAL

Use `PARTIAL` where some but not all defined expectations were satisfied.

Example:

```text
Expected:
Alert should contain host, user, process and parent process.

Observed:
Host, user and process were present.
Parent process was missing.

Result:
PARTIAL
```

Define partial-result criteria before using the state extensively in programme metrics.

---

# 40. INCONCLUSIVE

Use `INCONCLUSIVE` when available evidence does not support a reliable conclusion.

Example:

```text
The technique executed successfully, but an unrelated
telemetry outage occurred during the test window.
```

Repeat the test after the environment is stable.

---

# 41. ERROR

Use `ERROR` when the test procedure itself failed.

Example:

```text
The test harness terminated before the intended behaviour
was generated.
```

This is not a defensive-control failure.

---

# 42. Observation Matrix

Use a matrix to summarise results.

| Layer | Expected | Observed | Result |
|---|---|---|---|
| Execution | Execute | Executed | PASS |
| Prevention | Not expected | Not blocked | PASS |
| Telemetry | Present | Present | PASS |
| Collection | Present | Present | PASS |
| Parsing | Required fields | One field missing | PARTIAL |
| Detection | Alert | No alert | FAIL |
| Routing | SOC queue | Not reached | NOT TESTED |
| Investigation | Successful | Not reached | NOT TESTED |

This makes the failure point visible.

---

# 43. Collaborative Testing Cycle

A highly collaborative exercise can use short cycles.

```text
Red Executes
     |
     v
Blue Observes
     |
     v
Compare Results
     |
     v
Identify Gap
     |
     v
Modify Control
     |
     v
Execute Again
     |
     v
Validate
```

These cycles are useful for detection engineering and knowledge transfer.

---

# 44. Iteration Length

There is no universal correct cycle length.

Possible models include:

```text
Immediate feedback after each test

15-minute cycles

30-minute cycles

Technique-group review

End-of-day review
```

Choose the cadence based on:

```text
Objective

Complexity

Participant availability

Exercise mode

Learning goals
```

---

# 45. Phase-Based Exercise

A useful learning-oriented exercise can use two phases.

## Phase 1 - Limited Interaction

The offensive participant executes agreed scenarios while defenders work using their normal processes.

Measure:

```text
Detection

Investigation

Response

Time

Evidence quality
```

## Phase 2 - Collaborative Feedback

Participants then work together.

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
Improve
   |
   v
Retest
```

Comparing the phases can help evaluate the effect of structured knowledge transfer.

---

# 46. Example Phase Structure

```text
PHASE 1
Independent Observation
        |
        v
Baseline Performance
        |
        v
Initial Results
        |
        v
Feedback Session
        |
        v
PHASE 2
Collaborative Testing
        |
        v
Detection Improvement
        |
        v
Retest
        |
        v
Post-Exercise Results
```

Possible measurements include:

```text
Time to detect

Detection success

Investigation quality

Response quality

Knowledge assessment

Participant confidence

Ability to reproduce investigation
```

---

# 47. Exercise Timeline

Example one-day structure:

```text
09:00 - 09:30
Briefing and safety review

09:30 - 10:00
Environment and telemetry baseline

10:00 - 12:00
Phase 1 scenarios

12:00 - 12:30
Initial observations

13:00 - 15:00
Collaborative testing cycles

15:00 - 16:00
Retesting

16:00 - 16:30
Measurement and evidence review

16:30 - 17:00
After-action review
```

This is illustrative rather than mandatory.

---

# 48. Short Exercise Model

A focused exercise may require only:

```text
15 min - Scope and baseline

20 min - Initial execution

20 min - Evidence review

20 min - Improvement

20 min - Retest

15 min - Actions and lessons
```

Small exercises can be valuable when repeated consistently.

---

# 49. Exercise Evidence

Evidence should support the conclusion at each layer.

Possible evidence includes:

```text
Execution logs

Endpoint telemetry

SIEM events

Detection results

Alert screenshots

Case records

Query results

Analyst notes

Response records

Configuration changes

Retest results
```

Do not collect evidence merely to increase volume.

---

# 50. Evidence Directory

A simple structure is:

```text
PT-001/
├── 01-scope/
├── 02-baseline/
├── 03-execution/
├── 04-telemetry/
├── 05-detection/
├── 06-investigation/
├── 07-response/
├── 08-improvements/
├── 09-retest/
└── 10-aar/
```

Apply appropriate controls because evidence may contain sensitive security information.

---

# 51. Evidence Record

Example:

```text
Scenario:
PT-ENDPOINT-003

Execution Time:
2026-09-09 10:15:22 +02:00

Target:
WIN-TEST-01

Account:
purple-test-user

Execution:
Successful

Prevention:
Not expected

Endpoint Telemetry:
Present

SIEM:
Present

Detection:
Not observed

Investigation:
Not reached

Evidence:
endpoint-event.json
siem-event.json
scenario-notes.md
```

---

# 52. Gap Identification

When an expectation fails, classify the gap.

Possible categories:

```text
Execution gap

Prevention gap

Logging gap

Sensor gap

Collection gap

Parsing gap

Schema gap

Enrichment gap

Detection gap

Alert-routing gap

Investigation gap

Response gap

Knowledge gap

Process gap

Configuration gap

Exercise-design gap
```

Use a consistent taxonomy across exercises.

---

# 53. Failure Triage

A useful triage tree is:

```text
Did the intended behaviour occur?
        |
      No
        |
        v
Test Error / Procedure Issue

        Yes
        |
        v
Was prevention expected?
        |
        +---- Yes ----> Was it blocked?
        |                 |
        |               Yes -> Prevention PASS
        |                 |
        |               No  -> Prevention FAIL
        |
        v
Was telemetry generated?
        |
      No -> Logging / Sensor Gap
        |
       Yes
        |
        v
Was telemetry collected?
        |
      No -> Collection Gap
        |
       Yes
        |
        v
Was telemetry parsed correctly?
        |
      No -> Parsing / Schema Gap
        |
       Yes
        |
        v
Did detection fire?
        |
      No -> Detection Gap
        |
       Yes
        |
        v
Did alert reach analyst?
        |
      No -> Routing Gap
        |
       Yes
        |
        v
Could analyst investigate?
        |
      No -> Investigation Gap
        |
       Yes
        |
        v
Did expected response occur?
        |
      No -> Response Gap
        |
       Yes
        |
        v
Scenario Validated
```

---

# 54. Root Cause

After identifying the failing layer, determine why it failed.

Weak conclusion:

```text
SIEM did not detect the attack.
```

Better:

```text
The required endpoint event reached the SIEM, but the
detection rule referenced a field that was no longer
populated by the current parser.
```

The second statement identifies an actionable technical cause.

---

# 55. Improvement Actions

An improvement should contain:

```text
Gap

Root cause

Required change

Owner

Priority

Due date

Retest requirement
```

Example:

```text
Gap:
Detection did not fire.

Root Cause:
Rule uses obsolete schema field.

Action:
Update detection to current schema.

Owner:
Detection Engineering

Retest:
Required
```

---

# 56. Retesting

Retesting is part of the exercise lifecycle.

```text
Original Scenario
       |
       v
Failure
       |
       v
Improvement
       |
       v
Original Scenario Again
       |
       v
Expected Outcome?
```

Do not treat an implemented configuration change as proof that the issue is fixed.

---

# 57. Variant Retesting

After the original scenario passes, test relevant controlled variations.

```text
Original Procedure
       |
       v
PASS
       |
       v
Variation 1
       |
       v
Variation 2
       |
       v
Variation 3
```

This helps determine whether the detection or control is robust rather than narrowly tuned to one implementation.

---

# 58. Detection Engineering During Exercises

Purple exercises can directly support detection engineering.

```text
Execute Behaviour
       |
       v
Inspect Telemetry
       |
       v
Identify Useful Signals
       |
       v
Create Detection
       |
       v
Execute Again
       |
       v
Tune
       |
       v
Test Variations
       |
       v
Validate
```

See [Detection Engineering](detection-engineering.md).

---

# 59. Behaviour Over Tool

Avoid designing detections exclusively around one offensive tool.

For example:

```text
Tool Name
   |
   v
Static Indicator
```

may be fragile.

Prefer understanding:

```text
Adversary Behaviour
       |
       v
Underlying System Activity
       |
       v
Stable Telemetry
       |
       v
Detection Logic
```

Tool-specific detections can still be useful, but they should not be confused with complete behavioural coverage.

---

# 60. ATT&CK Mapping

ATT&CK can help describe:

```text
Tactic

Technique

Sub-technique

Relevant data sources

Adversary context
```

Example exercise record:

```text
Scenario:
PT-004

ATT&CK:
Technique mapped after scenario selection.

Reason:
The technique represents the behaviour being validated.

Expected Data:
Endpoint process telemetry
Authentication telemetry
```

See [MITRE ATT&CK for Purple Teaming](mitre-attack.md).

---

# 61. ATT&CK Is Not the Exercise Objective

Avoid:

```text
Objective:
Test T1059.
```

Prefer:

```text
Objective:
Validate whether command and scripting interpreter activity
on the selected endpoint generates sufficient telemetry and
detection context for the SOC to investigate the behaviour.
```

ATT&CK provides classification.

The security objective provides meaning.

---

# 62. Knowledge Transfer

Exercises should deliberately transfer knowledge.

Examples:

```text
Offensive participant explains the procedure.

Defender explains observed telemetry.

Detection engineer explains rule logic.

SOC analyst explains investigation workflow.

Threat intelligence explains relevance.

Incident response explains escalation requirements.
```

See [Knowledge Transfer](knowledge-transfer.md).

---

# 63. Teach-Back

After explanation, ask another participant to reproduce or explain the process.

```text
Demonstrate
    |
    v
Explain
    |
    v
Participant Reproduces
    |
    v
Participant Explains
    |
    v
Validate Understanding
```

This provides stronger evidence of knowledge transfer than attendance alone.

---

# 64. Measuring Exercises

Possible measurements include:

```text
Execution success

Prevention success

Telemetry availability

Detection success

Detection latency

Investigation success

Response success

Quality of alert context

Knowledge improvement

Remediation rate

Validated remediation rate

Regression rate
```

See [Metrics and Measurement](metrics-and-measurement.md).

---

# 65. Measurement Denominators

Metrics require explicit denominators.

Example:

```text
Detection Success Rate =
Successful Expected Detections
/
Successfully Executed Scenarios Where Detection Was Expected
```

Do not silently count:

```text
Test errors

Scenarios where detection was not expected

Scenarios that never executed
```

as detection failures.

---

# 66. Time to Detect

For one scenario:

```text
TTD =
Detection Timestamp - Execution Timestamp
```

Example:

```text
Execution:
10:15:22

Detection:
10:15:34

TTD:
12 seconds
```

Record exactly which timestamps are used.

---

# 67. Time to Investigate

Define the metric before measuring it.

For example:

```text
Investigation Start:
Analyst opens alert.

Investigation Complete:
Analyst identifies the scenario's required host, user,
process and related activity.

TTI =
Investigation Complete - Investigation Start
```

Different definitions produce different numbers.

---

# 68. Qualitative Observations

Not every useful result is numerical.

Record observations such as:

```text
Analyst could not find required telemetry.

Alert description was confusing.

Red and Blue used different terminology.

Investigation required undocumented knowledge.

SOC dashboard hid an important field.

Escalation ownership was unclear.

Detection logic was difficult to maintain.
```

These can reveal systemic problems that raw timing metrics miss.

---

# 69. Pre-Exercise Assessment

For learning-oriented exercises, a pre-exercise assessment can establish a baseline.

Possible questions:

```text
How confident are participants in identifying the behaviour?

Which telemetry would they expect?

Which tools would they use?

How would they investigate?

Which response would they consider?
```

Avoid using only self-reported confidence as evidence of learning.

---

# 70. Post-Exercise Assessment

After the exercise, evaluate whether participants can:

```text
Explain the behaviour

Identify relevant telemetry

Locate the events

Explain detection logic

Reproduce the investigation

Identify the response process
```

Comparing pre- and post-exercise results can provide evidence of learning.

---

# 71. Exercise AAR

After the exercise, conduct an After-Action Review.

Ask:

```text
What was expected?

What happened?

What worked?

What failed?

What surprised us?

Why?

What did we learn?

What should change?

Who owns the change?

How will we validate it?
```

See [After-Action Review](after-action-review.md).

---

# 72. Lessons Identified Versus Lessons Learned

A useful model is:

```text
Observation
    |
    v
Lesson Identified
    |
    v
Action
    |
    v
Implementation
    |
    v
Retest
    |
    v
Validated Improvement
    |
    v
Lesson Learned
```

An AAR document by itself does not prove improvement.

---

# 73. Continuous Validation

High-value scenarios should be considered for repeatable validation.

Candidates include:

```text
Previously failed detections

Critical identity controls

High-risk endpoint controls

Important telemetry pipelines

Critical cloud controls

Important network controls

Parser dependencies

Detection dependencies
```

See [Continuous Validation](continuous-validation.md).

---

# 74. Exercise to Regression Test

```text
Exercise
   |
   v
Gap
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
Standardised Test Case
   |
   v
Recurring Validation
```

This is how a one-time exercise can create long-term defensive value.

---

# 75. Change-Triggered Exercises

Repeat relevant tests after significant changes.

Examples:

```text
EDR upgrade

SIEM upgrade

Parser change

Detection rule change

Logging-policy change

Identity-policy change

Cloud configuration change

Network segmentation change

Major application release
```

A previously working control can regress after environmental changes.

---

# 76. Exercise Automation

Automation can support:

```text
Scenario execution

Test scheduling

Evidence collection

Telemetry queries

Detection assertions

Result comparison

Ticket creation

Regression testing
```

Automation should not remove the human reasoning required to understand failures.

---

# 77. Atomic Tests

Small, focused tests can be useful for validating one behaviour.

```text
Single Behaviour
      |
      v
Controlled Execution
      |
      v
Observe Telemetry
      |
      v
Validate Detection
```

Projects such as Atomic Red Team can provide reusable test definitions, but each test still requires:

```text
Scope review

Safety review

Environment review

Expected-result definition
```

before execution.

---

# 78. Adversary Emulation Platforms

Platforms such as MITRE CALDERA can help orchestrate authorised adversary emulation.

Potential uses include:

```text
Procedure orchestration

Repeatable execution

Scenario sequencing

Evidence generation

Regression validation
```

Tooling should be selected based on the exercise objective.

The platform is not the methodology.

---

# 79. Cloud Exercises

Cloud purple team exercises may evaluate:

```text
Identity activity

Role assumption

Privilege changes

Storage access

Control-plane activity

Logging

Network configuration

Security-group changes

Key usage

Service-account activity
```

Cloud testing requires particular attention to:

```text
Account boundaries

Region

Tenant

Subscription

Project

Role permissions

Audit logging

Cost impact
```

---

# 80. Identity Exercises

Identity-focused scenarios may evaluate:

```text
Authentication

Conditional access

Privilege assignment

Service accounts

Administrative roles

Credential use

Authentication anomalies

Identity telemetry
```

The exercise should distinguish:

```text
Authentication success

Authorisation success

Privilege obtained

Detection generated
```

These are separate events.

---

# 81. Endpoint Exercises

Endpoint-focused exercises may evaluate:

```text
Execution

Process creation

File activity

Registry changes

Persistence-related behaviour

Credential access indicators

Security-control response

Endpoint isolation
```

Use non-destructive representative procedures wherever possible.

---

# 82. Network Exercises

Network-focused scenarios may evaluate:

```text
Connection telemetry

DNS visibility

Firewall policy

Proxy visibility

Segmentation

Network detection

East-west traffic

Egress controls
```

The objective should specify whether the exercise is validating:

```text
Prevention

Visibility

Detection

Response
```

---

# 83. Application Exercises

Application-focused purple testing may validate:

```text
Authentication telemetry

Authorisation events

Application logs

WAF controls

API monitoring

Rate limiting

Security alerts

Fraud signals
```

Application teams may need to participate because useful security evidence can exist outside traditional SOC platforms.

---

# 84. Production Versus Lab

Lab environments provide:

```text
Safety

Repeatability

Debugging

Control
```

Production environments provide:

```text
Real configuration

Real telemetry pipelines

Real integrations

Real operational workflows
```

A useful model is:

```text
Develop in Lab
      |
      v
Validate Safely
      |
      v
Controlled Production Validation
      |
      v
Operational Evidence
```

Production testing requires explicit authorisation and stronger safeguards.

---

# 85. False Positives

An exercise may reveal that a detection generates excessive unrelated alerts.

Record:

```text
Expected Signal

Observed Signal

Background Events

Alert Volume

Distinguishing Fields
```

Detection tuning should preserve the intended detection objective.

Do not solve false positives by creating exclusions that also hide the behaviour being tested.

---

# 86. False Negatives

A detection may miss relevant variations.

Example:

```text
Procedure A -> Detected

Procedure B -> Detected

Procedure C -> Not Detected
```

Investigate whether the cause is:

```text
Missing telemetry

Different event type

Different field values

Overly specific rule logic

Different execution path

Environmental difference
```

This defines the actual detection boundary.

---

# 87. Exercise Repeatability

A repeatable exercise should document enough information for another authorised tester to reproduce it.

Include:

```text
Target type

Prerequisites

Procedure

Expected telemetry

Expected control behaviour

Expected detection

Evidence requirements

Cleanup

Success criteria
```

Avoid undocumented dependencies.

---

# 88. Exercise Versioning

Scenarios should be versioned when they change.

Example:

```text
Scenario:
PT-ENDPOINT-004

Version:
1.3

Change:
Updated expected telemetry after EDR schema migration.
```

Versioning helps explain why historical results differ.

---

# 89. Scenario Ownership

Each maintained scenario should have an owner.

The owner is responsible for reviewing:

```text
Threat relevance

Procedure validity

Safety

Telemetry expectations

Detection dependencies

Documentation

Retest results
```

Without ownership, scenario libraries become stale.

---

# 90. Scenario Review

Review scenarios when:

```text
Threat behaviour changes

Security controls change

Telemetry changes

Detection logic changes

Tooling changes

Architecture changes

Scenario repeatedly errors

Procedure becomes unsafe

Scenario no longer represents relevant risk
```

---

# 91. Scenario Retirement

Retire scenarios when they are no longer useful.

Possible reasons:

```text
Technology removed

Threat behaviour no longer relevant

Control replaced

Scenario duplicated

Procedure obsolete

Risk accepted

Better scenario available
```

Preserve historical records where appropriate.

---

# 92. Common Exercise Failure - No Baseline

Without baseline validation:

```text
No Alert
```

may actually mean:

```text
Sensor Offline

Collector Broken

SIEM Delay

Rule Disabled

Test Failed
```

Always confirm the environment first.

---

# 93. Common Exercise Failure - Undefined Expectations

If the team does not define expected behaviour before testing, results become subjective.

Avoid:

```text
We ran it and looked around.
```

Prefer:

```text
Expected:
Event X should be generated.
Rule Y should fire.
Alert Z should reach the SOC.
```

---

# 94. Common Exercise Failure - Too Many Techniques

Executing dozens of techniques with little analysis can produce less value than deeply testing a small number of important behaviours.

Prefer:

```text
Relevant Behaviour
      |
      v
Deep Validation
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

over:

```text
Large Technique Count
      |
      v
Shallow Results
```

---

# 95. Common Exercise Failure - No Root Cause

Do not stop with:

```text
FAIL
```

Determine:

```text
Where did it fail?

Why did it fail?

What dependency failed?

What should change?
```

---

# 96. Common Exercise Failure - No Retest

This is incomplete:

```text
Gap Found
   |
   v
Rule Changed
   |
   v
Ticket Closed
```

Prefer:

```text
Gap Found
   |
   v
Root Cause
   |
   v
Rule Changed
   |
   v
Original Test Repeated
   |
   v
Expected Outcome Confirmed
```

---

# 97. Common Exercise Failure - Treating ATT&CK as a Score

Do not conclude:

```text
80% ATT&CK coverage = strong security
```

without defining:

```text
Which techniques?

Which environments?

Which procedures?

Which telemetry?

Which detections?

Which variants?

Which threats?
```

Coverage needs context.

---

# 98. Common Exercise Failure - Competition

Purple team exercises should not encourage participants to hide useful information merely to "win".

A better outcome is:

```text
Gap Discovered
      |
      v
Shared Understanding
      |
      v
Improvement
      |
      v
Validated Control
```

A discovered weakness can represent a successful exercise.

---

# 99. Common Exercise Failure - Tool Demonstration

Avoid turning the exercise into:

```text
Tool A

Tool B

Tool C

Tool D
```

Instead organise around:

```text
Threat Behaviour

Security Objective

Telemetry

Detection

Investigation

Response
```

---

# 100. Practical Exercise Example

Consider an authorised exercise focused on execution visibility.

Objective:

```text
Validate whether representative command execution on an
authorised Windows endpoint generates sufficient telemetry
for detection and SOC investigation.
```

Scope:

```text
Target:
WIN-TEST-01

Account:
purple-test-user

Environment:
Dedicated authorised test system

Persistence:
Not permitted

Destructive actions:
Not permitted
```

---

## Baseline

Before execution:

```text
Endpoint sensor:
Healthy

SIEM ingestion:
Healthy

Detection:
Enabled

Alert queue:
Operational

Clock:
Synchronised
```

Result:

```text
Baseline:
PASS
```

---

## Initial Execution

The authorised representative procedure is executed.

Record:

```text
Scenario:
PT-ENDPOINT-001

Execution:
14:00:00

Target:
WIN-TEST-01

Account:
purple-test-user
```

The behaviour executes successfully.

```text
Execution:
PASS
```

---

## Prevention

Prevention was not expected for this particular test.

Observed:

```text
Not blocked
```

Result:

```text
Prevention:
PASS
```

because this matched the defined expectation.

---

## Endpoint Telemetry

The endpoint platform records:

```text
Timestamp

Host

User

Process

Parent process

Command line
```

Result:

```text
Telemetry Generation:
PASS
```

---

## SIEM Collection

The event appears in the SIEM.

Result:

```text
Collection:
PASS
```

---

## Detection

The expected rule does not fire.

Result:

```text
Detection:
FAIL
```

The team investigates rather than immediately modifying the rule.

---

## Root Cause Analysis

The detection expects:

```text
process.parent.name
```

but the current parser stores the relevant value under a different field.

The underlying event is present.

The failure is therefore traced to a schema dependency.

Classification:

```text
Primary:
Schema / Parsing Gap

Secondary:
Detection Dependency Gap
```

---

## Improvement

The detection engineering team updates the relevant mapping and validates the detection logic against current events.

---

## Retest

The original procedure is executed again.

Observed:

```text
Execution:
PASS

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

## Investigation

The SOC analyst receives the alert and identifies:

```text
Host

User

Process

Parent process

Timestamp

Related events
```

Result:

```text
Investigation:
PASS
```

---

## Learning

During the review, the team determines that platform upgrades can modify field mappings.

The lesson is converted into an engineering action:

```text
After telemetry or parser changes, execute representative
detection regression tests before considering the change
complete.
```

---

## Continuous Validation

The scenario becomes:

```text
PT-ENDPOINT-001
       |
       v
Regression Test
       |
       v
Run After Parser Changes
       |
       v
Validate Telemetry
       |
       v
Validate Detection
```

The exercise therefore improves both the detection and the process used to maintain it.

---

# 101. Exercise Planning Checklist

## Authorisation

- [ ] Authorisation confirmed
- [ ] Exercise owner identified
- [ ] Business owner identified
- [ ] Scope documented
- [ ] Exclusions documented
- [ ] Testing window documented
- [ ] Stop conditions documented
- [ ] Emergency contacts documented

## Objective

- [ ] Security objective defined
- [ ] Threat relevance documented
- [ ] Business relevance documented
- [ ] Success criteria defined
- [ ] Required measurements defined

## Scenario

- [ ] Scenario ID assigned
- [ ] ATT&CK mapping reviewed
- [ ] Preconditions documented
- [ ] Procedure documented
- [ ] Target documented
- [ ] Test identity documented
- [ ] Expected prevention documented
- [ ] Expected telemetry documented
- [ ] Expected collection documented
- [ ] Expected detection documented
- [ ] Expected investigation documented
- [ ] Expected response documented

## Safety

- [ ] Procedure reviewed for operational impact
- [ ] Destructive behaviour excluded unless explicitly authorised
- [ ] Data restrictions understood
- [ ] Rate limits defined where required
- [ ] Cleanup defined
- [ ] Stop process understood

## Baseline

- [ ] Target healthy
- [ ] Test identity valid
- [ ] Sensor healthy
- [ ] Logging enabled
- [ ] Collection healthy
- [ ] SIEM ingestion healthy
- [ ] Detection enabled
- [ ] Alert route healthy
- [ ] Time synchronised

---

# 102. Execution Checklist

- [ ] Confirm scenario ID
- [ ] Confirm target
- [ ] Confirm source
- [ ] Confirm test identity
- [ ] Record start time
- [ ] Execute approved procedure
- [ ] Confirm behaviour occurred
- [ ] Record immediate result
- [ ] Observe prevention
- [ ] Observe telemetry
- [ ] Observe collection
- [ ] Observe parsing
- [ ] Observe enrichment
- [ ] Observe detection
- [ ] Observe alert routing
- [ ] Observe investigation
- [ ] Observe response
- [ ] Record evidence
- [ ] Monitor stop conditions

---

# 103. Failure Checklist

When an expected outcome fails:

- [ ] Confirm the test actually executed
- [ ] Confirm the expected result was defined
- [ ] Identify the first failing layer
- [ ] Check source telemetry
- [ ] Check collection
- [ ] Check parsing
- [ ] Check enrichment
- [ ] Check detection logic
- [ ] Check rule state
- [ ] Check alert routing
- [ ] Check analyst workflow
- [ ] Determine root cause
- [ ] Record contributing factors
- [ ] Assign an owner
- [ ] Define remediation
- [ ] Define retest

---

# 104. Retest Checklist

- [ ] Confirm improvement implemented
- [ ] Confirm environment healthy
- [ ] Repeat original procedure
- [ ] Capture new evidence
- [ ] Compare against original result
- [ ] Confirm expected security outcome
- [ ] Test relevant variations
- [ ] Record residual limitations
- [ ] Update scenario documentation
- [ ] Determine whether regression testing is required

---

# 105. Exercise Record Template

```text
EXERCISE

Exercise ID:

Exercise Name:

Date:

Environment:

Authorisation:

Exercise Lead:

Participants:

Business Owner:


OBJECTIVE

Security Objective:

Threat Context:

Business Context:

Success Criteria:


SCOPE

Targets:

Excluded Targets:

Source Systems:

Test Accounts:

Testing Window:

Permitted Techniques:

Prohibited Techniques:


SAFETY

Stop Conditions:

Emergency Contact:

Data Restrictions:

Cleanup Requirements:


SCENARIO

Scenario ID:

Scenario Name:

ATT&CK Mapping:

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


RESULT

Execution Status:

Execution Timestamp:

Prevention:

Telemetry:

Collection:

Parsing:

Enrichment:

Detection:

Alert Routing:

Investigation:

Response:


ANALYSIS

Gap:

Gap Category:

Root Cause:

Contributing Factors:

Security Impact:


IMPROVEMENT

Action:

Owner:

Priority:

Due Date:

Retest Required:


RETEST

Retest Date:

Retest Result:

Variants Tested:

Residual Gap:


LEARNING

Knowledge Transferred:

Participant Observations:

Documentation Updated:

Regression Test Required:


EVIDENCE

Evidence Location:

Evidence Owner:

Retention Requirements:


CLEANUP

Artifacts Removed:

Test Accounts Reset:

Environment Restored:

Cleanup Confirmed:
```

---

# 106. Exercise Decision Model

```text
DEFINE OBJECTIVE
       |
       v
SELECT RELEVANT BEHAVIOUR
       |
       v
DEFINE EXPECTATIONS
       |
       v
BASELINE HEALTHY?
    /        \
  No          Yes
  |            |
  v            v
FIX BASELINE  EXECUTE
               |
               v
        BEHAVIOUR OCCURRED?
           /         \
         No           Yes
         |             |
         v             v
       ERROR       OBSERVE CONTROLS
                       |
                       v
                 EXPECTED RESULT?
                    /       \
                  Yes        No
                  |           |
                  v           v
                PASS       FIND FIRST
                           FAILING LAYER
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
                         VALIDATED?
                          /      \
                        No        Yes
                        |          |
                        v          v
                     IMPROVE     DOCUMENT
                       AGAIN        |
                                   v
                              REGRESSION?
                               /       \
                             No         Yes
                             |           |
                             v           v
                           CLOSE     CONTINUOUS
                                    VALIDATION
```

---

# 107. Final Exercise Model

A strong purple team exercise connects:

```text
AUTHORISATION
      |
      v
THREAT RELEVANCE
      |
      v
BUSINESS OBJECTIVE
      |
      v
SCENARIO
      |
      v
EXPECTED SECURITY OUTCOME
      |
      v
CONTROLLED EXECUTION
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
PARSING
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
KNOWLEDGE TRANSFER
      |
      v
AFTER-ACTION REVIEW
      |
      v
REGRESSION TEST
      |
      v
CONTINUOUS VALIDATION
```

The purpose is not to prove that the offensive participant can execute techniques.

The purpose is to generate evidence about how the defensive system behaves and use that evidence to improve security capability.

---

# Related Notes

- [Purple Teaming](index.md)
- [Purple Teaming Methodology](methodology.md)
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
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NICE Workforce Framework for Cybersecurity](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center){ target="_blank" rel="noopener noreferrer" }

!!! tip "Define expectations before testing"

    Document what prevention, telemetry, detection, investigation and response should occur before executing the scenario. This makes the final result much easier to defend.

!!! tip "Validate one layer at a time"

    When a scenario fails, identify the first layer where expected behaviour stopped. This is usually more useful than treating every missing alert as a detection-rule problem.

!!! tip "A failed control can still mean a successful exercise"

    Discovering a previously unknown gap, understanding its root cause, implementing an improvement and validating the fix is a valuable purple team outcome.

!!! tip "Keep exercises repeatable"

    Record prerequisites, procedures, expected results, evidence requirements and cleanup so that important scenarios can be executed again after security or infrastructure changes.

!!! warning "Only execute authorised scenarios"

    Purple team exercises must remain within approved scope and Rules of Engagement. Use controlled targets, test identities, safety controls and defined stop conditions.

!!! warning "Do not confuse ATT&CK coverage with security effectiveness"

    ATT&CK helps describe adversary behaviour. Exercise quality depends on relevance, evidence, defensive validation, improvement and retesting rather than the number of techniques executed.
