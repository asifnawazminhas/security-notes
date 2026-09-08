---
title: Purple Teaming Metrics and Measurement
description: Practical guidance for measuring purple team effectiveness across attack execution, detection, response, knowledge transfer, control improvement, coverage and continuous validation.
---

# Purple Teaming Metrics and Measurement

Purple teaming should produce measurable security improvement.

Executing techniques, generating alerts and holding collaborative sessions are useful activities, but activity alone does not demonstrate effectiveness.

A mature purple team programme should be able to answer:

```text
What did we test?

What happened?

What was detected?

How quickly was it detected?

Could defenders investigate it?

Could defenders respond?

Which controls failed?

Why did they fail?

What improved?

Was the improvement validated?

What did participants learn?

Was knowledge transferred?

Did the improvement persist?
```

A useful measurement model is:

```text
Exercise Objective
       |
       v
Attack Execution
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
       |
       v
Retest
       |
       v
Knowledge Transfer
       |
       v
Continuous Validation
```

Metrics should help explain this chain rather than reduce purple teaming to a collection of numbers.

---

## 1. Why Measure Purple Teaming?

Measurement helps determine whether purple teaming produces meaningful improvement.

Without measurement:

```text
Exercise Completed
       |
       v
Findings Recorded
       |
       v
Changes Made
       |
       v
Unknown Effectiveness
```

With measurement:

```text
Baseline
   |
   v
Exercise
   |
   v
Observed Result
   |
   v
Improvement
   |
   v
Retest
   |
   v
Comparison
   |
   v
Evidence of Change
```

The second model provides stronger evidence that the programme is improving security capability.

---

## 2. What Should Be Measured?

Purple teaming can measure several dimensions:

```text
Attack execution

Telemetry availability

Detection effectiveness

Investigation effectiveness

Response effectiveness

Control effectiveness

ATT&CK coverage

Knowledge improvement

Knowledge transfer

Collaboration

Remediation

Retest success

Sustainability
```

No single metric represents the complete programme.

---

## 3. Measurement Layers

A useful model separates measurement into layers:

```text
Layer 1 - Activity

Layer 2 - Technical Results

Layer 3 - Operational Performance

Layer 4 - Learning

Layer 5 - Improvement

Layer 6 - Sustainability
```

Each layer answers a different question.

---

## 4. Activity Metrics

Activity metrics describe what occurred.

Examples:

```text
Number of exercises

Number of techniques tested

Number of systems tested

Number of participants

Number of detection rules reviewed

Number of scenarios completed
```

These metrics are easy to collect.

However:

```text
More Activity != Better Security
```

Running 100 techniques poorly may provide less value than deeply validating 10 important techniques.

---

## 5. Technical Result Metrics

Technical metrics describe what the security controls observed.

Examples:

```text
Telemetry generated

Telemetry collected

Telemetry forwarded

Detection triggered

Alert generated

Control blocked activity

Technique succeeded

Technique failed
```

These metrics help evaluate the technical control chain.

---

## 6. Operational Metrics

Operational metrics measure how defenders handled the activity.

Examples:

```text
Time to detect

Time to triage

Time to investigate

Time to escalate

Time to contain

Time to respond

Investigation accuracy

Escalation accuracy
```

These metrics connect technical controls with human and operational processes.

---

## 7. Learning Metrics

Purple teaming should also measure learning.

Examples:

```text
Pre/post knowledge change

Practical task performance

Technique understanding

Telemetry understanding

Detection understanding

Investigation confidence

Independent reproduction

Knowledge retention
```

This distinguishes purple teaming from purely technical control testing.

See [Knowledge Transfer](knowledge-transfer.md).

---

## 8. Improvement Metrics

Improvement metrics determine whether identified gaps were actually addressed.

Examples:

```text
Detection rules improved

Telemetry sources added

Logging configurations corrected

Playbooks updated

Controls hardened

False positives reduced

Investigation procedures improved

Actions completed
```

A change should ideally be followed by validation.

---

## 9. Sustainability Metrics

Sustainability asks whether improvements remain effective.

Examples:

```text
Regression test success

Detection still operational after 30 days

Telemetry still available

Documentation still current

Knowledge retained

Action owners still assigned

Control survives platform changes
```

This moves measurement beyond one-time exercise success.

---

# 10. Start With Objectives

Metrics should derive from objectives.

Avoid:

```text
We collect this metric because it is easy.
```

Prefer:

```text
Objective
   |
   v
Question
   |
   v
Metric
   |
   v
Evidence
```

Example:

```text
Objective:
Improve credential-access detection.

Question:
Can the SOC detect and investigate the selected credential-access technique?

Metrics:
- telemetry availability
- detection success
- time to detect
- investigation success
- retest result
```

---

# 11. Define Success Before Testing

Success criteria should be established before execution where practical.

Example:

```text
Technique:
Selected ATT&CK technique

Expected Telemetry:
Endpoint process and security telemetry

Detection Requirement:
Alert generated

Operational Requirement:
SOC identifies host and user

Response Requirement:
Analyst follows escalation procedure

Learning Requirement:
Analyst explains detection logic

Retest Requirement:
Improvement survives repeated execution
```

Without predefined criteria, teams may interpret results differently after the exercise.

---

# 12. Baseline Measurement

Before changing anything, establish the current state.

```text
Baseline
   |
   v
Exercise
   |
   v
Improvement
   |
   v
Retest
   |
   v
Compare
```

Baseline measurements may include:

```text
Detection status

Telemetry availability

Time to detect

Time to investigate

Knowledge level

ATT&CK coverage

Existing control configuration
```

---

# 13. Before-and-After Measurement

A simple improvement model is:

```text
Before
  |
  v
Exercise
  |
  v
Change
  |
  v
After
```

Example:

| Metric | Before | After |
|---|---:|---:|
| Detection | Failed | Successful |
| Telemetry | Partial | Complete |
| Time to Detect | Not detected | 45 seconds |
| Investigation | Incomplete | Complete |
| Knowledge Score | 60% | 85% |

The numbers should always be interpreted with context.

---

# 14. Attack Execution Metrics

Before evaluating detection, confirm whether the technique actually executed as intended.

Record:

```text
Technique attempted

Technique successfully executed

Technique blocked

Technique partially executed

Technique failed because of test error

Technique failed because of environmental condition
```

This distinction is critical.

---

# 15. Technique Execution Success Rate

A simple metric is:

```text
Technique Execution Success Rate =
Successfully Executed Techniques
---------------------------------
Attempted Techniques
```

Example:

```text
Attempted: 20

Successfully executed: 16

Execution success rate: 80%
```

However, this does not measure defensive effectiveness.

A failed technique may indicate:

```text
Preventive control

Incorrect test conditions

Missing prerequisite

Tool failure

Operator error
```

Investigate the reason.

---

# 16. Prevention Metrics

Some techniques may be blocked before telemetry or detection becomes the primary question.

Track:

```text
Prevented

Allowed

Partially prevented

Not applicable
```

Example:

| Technique | Prevention |
|---|---|
| Technique A | Blocked |
| Technique B | Allowed |
| Technique C | Partially blocked |
| Technique D | Not applicable |

Do not treat every prevented technique as proof of complete security.

Alternative implementations may behave differently.

---

# 17. Telemetry Availability

Detection depends on telemetry.

Measure the telemetry chain:

```text
Action
   |
   v
Event Generated
   |
   v
Event Collected
   |
   v
Event Forwarded
   |
   v
Event Parsed
   |
   v
Event Searchable
```

A useful result classification is:

```text
Complete

Partial

Missing

Unknown
```

---

# 18. Telemetry Coverage Rate

One possible metric is:

```text
Telemetry Coverage =
Required Telemetry Sources Available
------------------------------------
Required Telemetry Sources
```

Example:

```text
Required sources: 10

Available sources: 8

Telemetry coverage: 80%
```

This metric should not imply that every available data source is correctly configured.

---

# 19. Telemetry Quality

Availability alone is insufficient.

Evaluate:

```text
Required fields present

Timestamp quality

Hostname consistency

User identity

Process information

Command-line information

Network information

Parser correctness

Data latency

Retention
```

A source can exist while still being operationally unusable.

---

# 20. Detection Success

A basic detection classification is:

```text
Detected

Partially Detected

Not Detected

Not Applicable

Unable to Validate
```

Avoid forcing uncertain results into:

```text
Detected / Not Detected
```

when evidence does not support that conclusion.

---

# 21. Detection Rate

A simple metric is:

```text
Detection Rate =
Techniques Detected
-------------------
Techniques Successfully Executed
```

Example:

```text
Successfully executed techniques: 20

Detected techniques: 15

Detection rate: 75%
```

This can be useful, but only when the denominator is clearly defined.

---

# 22. Why the Denominator Matters

Consider:

```text
30 techniques planned

25 attempted

20 successfully executed

15 detected
```

Possible calculations:

```text
15 / 30 = 50%

15 / 25 = 60%

15 / 20 = 75%
```

All are mathematically valid but answer different questions.

Therefore always define the denominator.

---

# 23. Prevention Versus Detection

Keep these separate.

Example:

```text
Technique A
Prevented before execution.

Technique B
Executed and detected.

Technique C
Executed and not detected.
```

Do not classify Technique A as:

```text
Detected
```

unless detection actually occurred.

Use separate measures:

```text
Prevention

Detection

Response
```

---

# 24. Detection Depth

A detection can occur at different levels.

```text
Level 0 - No visibility

Level 1 - Telemetry available

Level 2 - Searchable activity

Level 3 - Detection logic matches

Level 4 - Alert generated

Level 5 - Analyst investigates correctly

Level 6 - Response initiated correctly
```

This provides more context than a binary detection rate.

---

# 25. Detection Quality

Detection quality may consider:

```text
Accuracy

Context

Actionability

False positives

False negatives

Timeliness

Coverage

Investigation value
```

An alert that triggers but provides no useful context may still require improvement.

---

# 26. Time to Detect

Time to Detect can be represented as:

```text
TTD = Detection Time - Technique Start Time
```

Example:

```text
Technique start:
14:10:00

Detection:
14:10:42

TTD:
42 seconds
```

Define timestamps consistently.

---

# 27. Time to Alert

Sometimes it is useful to separate:

```text
Telemetry Time

Detection Evaluation Time

Alert Creation Time

Analyst Visibility Time
```

For example:

```text
Technique
14:10:00

Telemetry
14:10:03

Rule Match
14:10:20

Alert Created
14:10:25

SOC Sees Alert
14:10:40
```

This helps identify pipeline latency.

---

# 28. Mean Time to Detect

Across multiple tests:

```text
MTTD =
Sum of Detection Times
----------------------
Number of Detected Tests
```

Be careful with averages.

A few extreme results can distort the mean.

Consider also:

```text
Median

Minimum

Maximum

Percentiles
```

when the dataset is large enough.

---

# 29. Time to Triage

Time to triage measures how quickly an analyst begins meaningful assessment.

Define the starting point explicitly.

For example:

```text
Alert visible to analyst
        |
        v
Analyst determines initial severity
```

Avoid comparing metrics collected with different definitions.

---

# 30. Time to Investigate

A possible definition is:

```text
Investigation Time =
Investigation Conclusion Time
-
Investigation Start Time
```

The conclusion might include:

```text
Technique identified

Affected host identified

User identified

Scope established

Escalation decision made
```

Define what constitutes completion.

---

# 31. Time to Respond

Response timing may measure:

```text
Time to escalation

Time to containment

Time to account disablement

Time to host isolation

Time to block indicator
```

Only simulate or perform disruptive response actions when explicitly authorised.

---

# 32. Response Success

A response can be classified as:

```text
Successful

Partially Successful

Unsuccessful

Not Tested

Not Applicable
```

A purple team exercise does not always need to perform full containment.

The exercise scope determines what should be measured.

---

# 33. Investigation Accuracy

Speed alone can create poor incentives.

A fast but incorrect investigation is not a successful outcome.

Measure whether analysts correctly identified:

```text
Technique

Host

User

Process

Parent process

Network destination

Scope

Severity

Required escalation
```

---

# 34. Detection-to-Response Funnel

A useful operational model is:

```text
100 Techniques
      |
      v
80 Generated Required Telemetry
      |
      v
65 Matched Detection Logic
      |
      v
60 Generated Alerts
      |
      v
55 Correctly Triaged
      |
      v
50 Correctly Investigated
      |
      v
45 Correctly Escalated
```

This can reveal where capability is lost.

---

# 35. Control Effectiveness

Purple teaming can evaluate controls such as:

```text
EDR

SIEM

Firewall

Identity protection

Application control

Email security

Network monitoring

Logging

Cloud security controls

DLP
```

For each control, ask:

```text
Was it expected to prevent?

Was it expected to detect?

Was it expected to provide telemetry?

Did it perform as expected?
```

---

# 36. Expected Versus Observed

Use:

| Control | Expected | Observed | Result |
|---|---|---|---|
| EDR | Detect | Alert generated | Pass |
| SIEM | Correlate | Rule did not match | Gap |
| Firewall | Allow test traffic | Allowed | Pass |
| Logging | Capture command | Partial | Gap |

This makes control assumptions visible.

---

# 37. Control Validation Rate

A possible programme metric is:

```text
Validated Controls
------------------
Controls Tested
```

But define:

```text
Validated
```

carefully.

A control should not be considered validated merely because it was present.

---

# 38. Detection Gap Classification

Classify detection gaps by root cause.

Example categories:

```text
Telemetry generation

Telemetry collection

Telemetry forwarding

Parsing

Detection logic

Rule configuration

Rule deployment

Alert routing

Analyst triage

Investigation procedure
```

This makes metrics actionable.

---

# 39. Gap Distribution

Example:

| Gap Type | Count |
|---|---:|
| Telemetry | 5 |
| Detection Logic | 8 |
| Alert Routing | 2 |
| Investigation | 4 |
| Response | 1 |

This can help identify systemic weaknesses.

Do not treat counts alone as risk severity.

---

# 40. Root Cause Metrics

Tracking root causes over time can reveal recurring problems.

Example:

```text
Quarter 1:
40% telemetry gaps

Quarter 2:
20% telemetry gaps

Quarter 3:
8% telemetry gaps
```

This may indicate improvement in collection architecture.

---

# 41. ATT&CK Coverage

MITRE ATT&CK can help structure coverage measurement.

Possible dimensions include:

```text
Tactics tested

Techniques tested

Sub-techniques tested

Techniques with telemetry

Techniques with detections

Techniques operationally validated
```

See [MITRE ATT&CK](mitre-attack.md).

---

# 42. ATT&CK Coverage Is Not One Number

Avoid:

```text
We have 80% ATT&CK coverage.
```

without defining what coverage means.

Possible meanings include:

```text
80% have a detection rule.

80% have telemetry.

80% were tested.

80% generated an alert.

80% were operationally investigated.
```

These are very different.

---

# 43. ATT&CK Coverage Model

A more useful matrix is:

| Technique | Relevant | Telemetry | Detection | Tested | Investigated |
|---|---|---|---|---|---|
| Txxxx | Yes | Yes | Yes | Yes | Yes |
| Tyyyy | Yes | Yes | No | Yes | No |
| Tzzzz | Yes | Partial | No | Yes | No |

This shows capability depth.

---

# 44. Relevant Coverage

Not every ATT&CK technique is equally relevant to every organisation.

Prioritise based on:

```text
Threat intelligence

Technology stack

Industry

Attack surface

Previous incidents

Red team findings

Business risk

Control architecture
```

A smaller amount of high-relevance coverage may be more useful than broad but shallow coverage.

---

# 45. Scenario Coverage

Measure complete attack paths in addition to individual techniques.

Example:

```text
Initial Access
     |
     v
Execution
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

A scenario can reveal gaps that isolated technique testing misses.

---

# 46. Coverage Depth

For each technique, consider:

```text
Variant 1

Variant 2

Different tool

Different parent process

Different protocol

Different privilege level

Different host type
```

One successful detection does not guarantee detection of every implementation.

---

# 47. Detection Robustness

A robust detection should ideally focus on meaningful behavior rather than one exact tool signature.

Test:

```text
Original procedure

Modified procedure

Alternative tool

Alternative command syntax

Different process ancestry
```

within the authorised exercise scope.

The objective is to determine whether detection logic generalises.

---

# 48. False Positive Measurement

A detection that generates excessive false positives may be operationally ineffective.

Potential measures include:

```text
Alert volume

True positive rate

False positive rate

Analyst disposition

Suppression rate
```

Be careful with terminology when ground truth is incomplete.

---

# 49. False Negative Measurement

Purple team testing is particularly useful for discovering false negatives.

A known test provides ground truth:

```text
Known Technique Executed
        |
        v
Expected Detection
        |
        v
No Detection
```

Investigate why the activity was missed.

---

# 50. Precision and Recall

Where reliable labelled data exists, detection evaluation may use:

```text
Precision =
True Positives
-----------------------------
True Positives + False Positives
```

and:

```text
Recall =
True Positives
-----------------------------
True Positives + False Negatives
```

These metrics require trustworthy ground truth.

Do not calculate them from incomplete datasets.

---

# 51. Knowledge Measurement

Purple teaming should measure whether participants learned.

Potential dimensions include:

```text
Conceptual understanding

Technique understanding

Telemetry understanding

Detection understanding

Investigation capability

Response understanding

Ability to reproduce
```

---

# 52. Pre-Exercise Knowledge Assessment

A pre-exercise assessment can establish baseline understanding.

Example scale:

```text
1 - No familiarity

2 - Basic awareness

3 - Working understanding

4 - Can apply independently

5 - Can explain and teach others
```

Self-assessment should ideally be combined with practical measurement.

---

# 53. Post-Exercise Knowledge Assessment

Repeat the same or equivalent assessment after the exercise.

Example:

| Area | Before | After |
|---|---:|---:|
| Technique understanding | 2 | 4 |
| Telemetry understanding | 2 | 4 |
| Detection knowledge | 3 | 4 |
| Investigation confidence | 2 | 4 |

This indicates perceived improvement.

It does not alone prove practical capability.

---

# 54. Knowledge Improvement

A simple calculation is:

```text
Knowledge Improvement =
Post-Exercise Score - Pre-Exercise Score
```

For example:

```text
Pre: 60

Post: 82

Improvement: +22
```

Interpret results carefully, particularly with small participant groups.

---

# 55. Practical Knowledge Measurement

Practical tasks provide stronger evidence.

Examples:

```text
Identify the relevant telemetry.

Explain why the rule triggered.

Modify the detection safely.

Investigate the alert.

Identify the affected host.

Identify a likely false positive.

Reproduce the query independently.
```

Record whether the participant can complete the task:

```text
Independently

With guidance

Unable
```

---

# 56. Independent Reproduction Rate

One possible metric is:

```text
Independent Reproduction Rate =
Participants Completing Task Independently
------------------------------------------
Participants Attempting Task
```

This can provide evidence of knowledge transfer.

---

# 57. Knowledge Retention

Measure knowledge again later.

Example:

```text
Pre-Exercise
     |
     v
Immediate Post-Exercise
     |
     v
30-Day Follow-Up
```

Example:

| Stage | Score |
|---|---:|
| Pre | 55 |
| Post | 85 |
| 30-Day | 78 |

This provides more information than immediate improvement alone.

---

# 58. Knowledge Transfer Coverage

Measure whether important exercise knowledge was converted into reusable artifacts.

Examples:

```text
Detection documented

Attack procedure documented

Playbook updated

Telemetry requirements documented

Lessons recorded

Owner assigned
```

A possible measure is:

```text
Documented Reusable Outputs
---------------------------
Expected Reusable Outputs
```

Again, quality matters more than quantity.

---

# 59. Collaboration Metrics

Collaboration is difficult to reduce to a single number.

Possible indicators include:

```text
Frequency of red-blue interaction

Number of joint investigations

Participant feedback

Cross-team participation

Number of jointly developed improvements

Time between observation and feedback
```

Use collaboration metrics carefully.

More messages or meetings do not automatically mean better collaboration.

---

# 60. Feedback Cycle Time

Purple teaming benefits from short feedback loops.

Measure:

```text
Technique Execution
       |
       v
Observation
       |
       v
Discussion
       |
       v
Improvement
       |
       v
Retest
```

The elapsed time can indicate how quickly the team can learn and adapt.

---

# 61. Remediation Metrics

Track actions created from exercises.

Possible statuses:

```text
Open

Assigned

In Progress

Implemented

Validated

Closed

Accepted Risk
```

Avoid marking an action complete when a configuration change has merely been deployed.

Prefer:

```text
Implemented
```

followed by:

```text
Validated
```

---

# 62. Remediation Completion Rate

A simple measure is:

```text
Completed Actions
-----------------
Total Actions
```

But distinguish:

```text
Implemented

Validated
```

A stronger metric is:

```text
Validated Remediation Rate =
Validated Actions
-----------------
Total Actions
```

---

# 63. Time to Remediate

Measure:

```text
TTR =
Validated Remediation Time
-
Finding Identification Time
```

The endpoint should ideally be validation, not merely implementation.

---

# 64. Remediation Priority

Not every gap has equal importance.

Prioritise using:

```text
Threat relevance

Technique impact

Exposure

Likelihood

Business criticality

Control dependency

Attack-chain position

Existing compensating controls
```

Avoid prioritising only by how easy the fix is.

---

# 65. Retest Success Rate

A useful metric is:

```text
Retest Success Rate =
Successful Retests
------------------
Completed Retests
```

A successful retest should verify the original objective.

Example:

```text
Original:
Technique executed without detection.

Change:
Detection created.

Retest:
Technique executed again.

Result:
Detection generated expected alert.

Status:
Validated.
```

---

# 66. Regression Testing

A one-time successful retest does not guarantee long-term effectiveness.

Important detections can become regression tests.

```text
Detection Created
       |
       v
Test Created
       |
       v
Scheduled Validation
       |
       v
Environment Changes
       |
       v
Test Repeated
```

This supports continuous validation.

---

# 67. Detection Regression Rate

Over time, track:

```text
Previously Validated Tests
       |
       v
Still Passing?
```

Example:

```text
100 previously validated detections

94 still pass

6 regressions
```

The six regressions should be investigated.

---

# 68. Programme Trend Metrics

Single exercise results provide limited context.

Trend data can show whether capability is improving.

Example:

| Quarter | Detection | Investigation | Validated Remediation |
|---|---:|---:|---:|
| Q1 | 61% | 54% | 48% |
| Q2 | 70% | 66% | 62% |
| Q3 | 79% | 75% | 73% |

Trends should use consistent definitions.

---

# 69. Compare Like With Like

Avoid comparing:

```text
Different technique sets

Different environments

Different data sources

Different exercise scopes

Different measurement definitions
```

without explaining the differences.

A detection rate increasing from:

```text
60% -> 80%
```

may not represent improvement if the second exercise tested easier techniques.

---

# 70. Segmentation

Segment metrics where useful.

Examples:

```text
By ATT&CK tactic

By platform

By business unit

By operating system

By data source

By control

By detection team

By scenario
```

This can reveal patterns hidden by aggregate numbers.

---

# 71. Example by ATT&CK Tactic

| Tactic | Tested | Detected | Detection Rate |
|---|---:|---:|---:|
| Execution | 10 | 9 | 90% |
| Persistence | 8 | 5 | 62.5% |
| Credential Access | 7 | 4 | 57.1% |
| Discovery | 12 | 10 | 83.3% |

This may suggest where deeper validation is required.

---

# 72. Example by Data Source

| Data Source | Required | Available | Quality |
|---|---:|---:|---|
| Process | 15 | 15 | Good |
| PowerShell | 6 | 4 | Partial |
| DNS | 5 | 2 | Weak |
| Authentication | 8 | 8 | Good |

This helps prioritise telemetry engineering.

---

# 73. Example by Platform

```text
Windows
Detection: 85%

Linux
Detection: 62%

Cloud
Detection: 58%
```

Do not assume the percentages are directly comparable unless technique selection and testing methodology are equivalent.

---

# 74. Risk-Weighted Coverage

Not all techniques have equal importance.

A programme may assign weights based on:

```text
Threat intelligence

Business impact

Likelihood

Asset criticality

Historical incidents
```

Conceptually:

```text
High-Risk Technique = Weight 3

Medium-Risk Technique = Weight 2

Low-Risk Technique = Weight 1
```

Weighted metrics can better reflect organisational priorities.

Document the weighting methodology.

---

# 75. Do Not Game the Metrics

Poor metrics can create undesirable behavior.

For example:

```text
Goal:
Increase detection rate.
```

Teams may respond by:

```text
Testing easier techniques

Avoiding difficult scenarios

Creating overly broad rules

Ignoring false positives
```

The metric improves while security quality decreases.

This is a measurement failure.

---

# 76. Balanced Metrics

Use multiple dimensions.

For example:

```text
Detection Rate
      +
False Positive Quality
      +
Investigation Success
      +
Time to Detect
      +
Retest Success
      +
Knowledge Transfer
```

A balanced view reduces metric gaming.

---

# 77. Leading Indicators

Leading indicators can suggest future improvement.

Examples:

```text
Percentage of high-risk techniques with tests

Percentage of detections with automated validation

Percentage of telemetry sources health-checked

Percentage of exercise actions assigned owners

Percentage of detections with investigation guidance
```

These measure capability-building activity.

---

# 78. Lagging Indicators

Lagging indicators measure results after activity occurs.

Examples:

```text
Detection success

Incident detection performance

Exercise response performance

Remediation completion

Regression rate
```

Use both leading and lagging indicators where appropriate.

---

# 79. Quantitative Metrics

Quantitative measurements include:

```text
Counts

Percentages

Time

Scores

Rates

Coverage
```

These are useful for trends and dashboards.

But numbers may not explain why something happened.

---

# 80. Qualitative Evidence

Qualitative evidence can include:

```text
Participant observations

Analyst feedback

Exercise notes

Interview responses

Investigation quality

Lessons learned

Observed collaboration
```

This provides context for quantitative results.

---

# 81. Mixed Measurement

A stronger approach combines:

```text
Quantitative
     +
Qualitative
```

Example:

```text
Detection Rate:
75%

Analyst Observation:
Most failures involved missing PowerShell telemetry.

Technical Evidence:
Forwarding configuration omitted the relevant event channel.
```

Together, these provide a stronger conclusion.

---

# 82. Measurement Validity

A metric should measure what it claims to measure.

Example:

```text
Number of alerts
```

does not necessarily measure:

```text
Detection effectiveness
```

because alerts may be:

```text
Duplicate

Low quality

False positive

Unactionable
```

Always ask:

> What does this metric actually tell us?

---

# 83. Measurement Reliability

A reliable metric should produce comparable results when applied consistently.

Define:

```text
Start timestamp

End timestamp

Success criteria

Failure criteria

Denominator

Scope

Data source
```

Without consistent definitions, trend analysis becomes unreliable.

---

# 84. Small Sample Sizes

Purple team exercises may involve small participant groups or a small number of techniques.

Avoid overstating results.

Instead of:

> The exercise proves that knowledge transfer improves analyst performance by 35%.

Prefer:

> Participants demonstrated higher post-exercise scores within this exercise. Given the limited sample size, the result should be interpreted as an indicator of improvement rather than a generalisable effect.

Measurement should remain defensible.

---

# 85. Participant Privacy

Knowledge and performance measurement can involve individuals.

Where appropriate:

```text
Avoid unnecessary personal identifiers

Aggregate results

Explain why data is collected

Restrict access

Define retention

Avoid punitive use
```

The objective should be capability improvement.

---

# 86. Team Versus Individual Measurement

Purple teaming often benefits from measuring team capability rather than ranking individuals.

Prefer:

```text
Can the SOC identify the technique?
```

over:

```text
Which analyst performed worst?
```

unless individual assessment is explicitly part of an agreed training programme.

---

# 87. Dashboard Design

A purple team dashboard might contain:

```text
Exercises Completed

Relevant Techniques Tested

Telemetry Coverage

Detection Rate

Investigation Success

Mean/Median Time to Detect

Open Gaps

Validated Remediations

Regression Failures

Knowledge Improvement
```

Keep the dashboard focused on decision-making.

---

# 88. Example Dashboard

```text
PURPLE TEAM PROGRAMME

Exercises Completed:           12

Relevant Techniques Tested:    84

Telemetry Coverage:            88%

Detection Rate:                76%

Investigation Success:         71%

Median Time to Detect:         52 sec

Open Detection Gaps:           14

Validated Remediations:        31

Regression Failures:           3

Knowledge Improvement:         +18%
```

Each metric should link back to underlying evidence.

---

# 89. Traffic-Light Status

Dashboards sometimes use:

```text
Green

Amber

Red
```

Define thresholds explicitly.

Example:

```text
Green:
Validated and operating as expected

Amber:
Partial capability or improvement in progress

Red:
Expected capability absent or failed
```

Avoid arbitrary thresholds without risk context.

---

# 90. Metric Ownership

Every important metric should have an owner.

Example:

| Metric | Owner |
|---|---|
| Telemetry Coverage | Security Engineering |
| Detection Coverage | Detection Engineering |
| Investigation Success | SOC |
| Remediation Status | Control Owner |
| Knowledge Measurement | Purple Team Lead |

Ownership improves data quality and follow-up.

---

# 91. Data Sources for Measurement

Potential sources include:

```text
Exercise platform

SIEM

EDR

SOAR

Ticketing system

Detection repository

Attack automation platform

Survey platform

Manual observer notes
```

Prefer reproducible evidence where possible.

---

# 92. Timestamp Synchronisation

Time-based metrics depend on consistent clocks.

Verify:

```text
Red team host time

Target time

SIEM time

EDR time

SOC platform time
```

Clock differences can invalidate timing metrics.

---

# 93. Exercise Timeline

Maintain a timeline:

```text
14:00:00 Exercise started

14:05:12 Technique executed

14:05:15 Endpoint event generated

14:05:29 SIEM event available

14:05:44 Alert generated

14:06:10 Analyst opened alert

14:08:32 Investigation completed
```

This allows multiple timing metrics to be calculated correctly.

---

# 94. Evidence Record

For each test, capture:

```text
Exercise ID

Scenario

Technique

ATT&CK mapping

Host

Test timestamp

Execution result

Expected telemetry

Observed telemetry

Detection result

Alert timestamp

Investigation result

Response result

Gap

Root cause

Remediation

Retest

Owner
```

---

# 95. Example Technique Measurement Record

```text
Exercise ID:
PT-2026-014

Technique:
Selected credential-access technique

Execution:
Successful

Telemetry:
Partial

Detection:
Failed

Root Cause:
Required event not forwarded to SIEM

Time to Detect:
N/A

Investigation:
Not initiated because no alert was generated

Remediation:
Forwarding policy updated

Retest:
Successful

Retest Detection Time:
38 seconds

Knowledge Outcome:
SOC analyst independently identified required telemetry after retest

Status:
Validated
```

---

# 96. Practical Measurement Scenario

## Scenario

A purple team tests a technique against a Windows endpoint.

The expected chain is:

```text
Technique
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
SOC
```

### Baseline

```text
Technique executed:
Yes

Telemetry generated:
Yes

Telemetry forwarded:
Yes

Detection:
No

Investigation:
No

Response:
No
```

### Root Cause

The detection rule expects:

```text
Field A
```

but the current parser stores the value in:

```text
Field B
```

### Improvement

The detection logic is corrected.

### Retest

```text
Technique executed:
Yes

Telemetry generated:
Yes

Telemetry forwarded:
Yes

Detection:
Yes

Alert generated:
Yes

Analyst investigation:
Successful
```

---

# 97. Measuring the Scenario

Possible results:

| Measure | Baseline | Retest |
|---|---|---|
| Technique Execution | Success | Success |
| Telemetry | Complete | Complete |
| Detection | Failed | Success |
| Alert | None | Generated |
| Investigation | Not Started | Successful |
| TTD | N/A | 41 sec |
| Root Cause | Field mismatch | Resolved |

This provides clear evidence of improvement.

---

# 98. Measuring Learning in the Same Scenario

Before:

```text
Analyst could identify:
- alert name

Analyst could not identify:
- required telemetry
- relevant fields
- root cause
```

After:

```text
Analyst independently identified:
- telemetry source
- relevant fields
- detection condition
- investigation path
```

This demonstrates both:

```text
Technical Improvement

Knowledge Improvement
```

---

# 99. Measuring Collaboration

Observer notes may record:

```text
Red explained technique behavior.

Blue identified expected telemetry.

Detection engineer explained rule logic.

SOC analyst investigated the retest alert.

Participants jointly identified parser mismatch.
```

This qualitative evidence can complement quantitative metrics.

---

# 100. Measuring Improvement Over Multiple Exercises

Example:

```text
Exercise 1
Detection: 55%

Exercise 2
Detection: 63%

Exercise 3
Detection: 72%

Exercise 4
Detection: 79%
```

Before concluding that capability improved, verify:

```text
Were technique sets comparable?

Was scope comparable?

Were measurement definitions unchanged?

Did difficulty change?

Did telemetry architecture change?
```

Trend interpretation requires context.

---

# 101. Programme-Level Questions

Metrics should help leadership answer:

```text
Are we detecting the threats that matter?

Where are our largest visibility gaps?

Which controls repeatedly fail?

How quickly are gaps corrected?

Are improvements validated?

Are detections regressing?

Are teams learning?

Is knowledge spreading?

Is purple teaming becoming repeatable?
```

These questions are more useful than:

```text
How many techniques did we run?
```

---

# 102. Technical-Level Questions

Engineers may need:

```text
Which telemetry source failed?

Which parser failed?

Which rule condition failed?

Which fields were missing?

Which variation bypassed detection?

Which service produced the event?

Which control blocked the technique?
```

Metrics should allow investigation beneath the dashboard.

---

# 103. Operational-Level Questions

SOC leadership may need:

```text
How quickly did analysts react?

Was the alert actionable?

Was severity correct?

Was escalation correct?

Was investigation complete?

Was containment appropriate?
```

This connects engineering validation to operational capability.

---

# 104. Learning-Level Questions

Purple team facilitators may ask:

```text
Did participants understand the technique?

Could they explain the telemetry?

Could they reproduce the investigation?

Did confidence improve?

Was knowledge retained?

Was knowledge shared beyond the session?
```

---

# 105. Avoid Vanity Metrics

Examples of potential vanity metrics include:

```text
Number of techniques executed

Number of alerts generated

Number of meetings

Number of rules created

Number of ATT&CK techniques mapped
```

These can be useful operational statistics.

They become vanity metrics when presented as evidence of effectiveness without additional context.

---

# 106. Avoid Percentage Without Context

Weak:

> Detection coverage is 92%.

Stronger:

> Of 50 threat-relevant techniques successfully executed during the assessment period, 46 generated the expected detection, producing a validated detection rate of 92% for the tested technique set.

The second statement defines:

```text
Scope

Denominator

Validation

Meaning
```

---

# 107. Avoid Combining Incompatible Results

Do not calculate:

```text
Overall Detection Rate
```

from unrelated environments without explaining differences.

For example:

```text
Windows endpoints

Linux servers

Cloud control plane

SaaS applications
```

may require different telemetry and detection models.

Segment first.

---

# 108. Avoid Punitive Metrics

If metrics are used primarily to blame teams:

```text
Red hides information

Blue avoids difficult tests

Participants hide mistakes

Metrics become manipulated
```

Purple teaming requires openness.

Metrics should encourage:

```text
Learning

Transparency

Improvement

Collaboration
```

---

# 109. Measurement Review

Metrics themselves should be reviewed periodically.

Ask:

```text
Is this metric still useful?

Does it influence a decision?

Can it be measured reliably?

Can teams game it?

Does it reflect security outcomes?

Should it be replaced?
```

Measurement should evolve with programme maturity.

---

# 110. Recommended Core Metric Set

A practical starting set is:

```text
1. Relevant techniques tested

2. Technique execution success

3. Prevention result

4. Telemetry availability

5. Detection success

6. Detection depth

7. Time to detect

8. Investigation success

9. Root cause category

10. Validated remediation rate

11. Retest success

12. Knowledge improvement

13. Independent reproduction

14. Regression status
```

This provides a balanced view without creating excessive measurement overhead.

---

# 111. Minimal Exercise Scorecard

For smaller exercises:

| Measure | Result |
|---|---|
| Technique Executed | Yes |
| Prevented | No |
| Telemetry Available | Partial |
| Detection | Failed |
| Investigation | Not Started |
| Root Cause | Telemetry Gap |
| Improvement | Implemented |
| Retest | Passed |
| Knowledge Transfer | Confirmed |
| Follow-Up | Regression Test |

This can be sufficient for practical tracking.

---

# 112. Advanced Scorecard

Larger programmes may track:

```text
Threat relevance

Technique coverage

Technique variants

Telemetry completeness

Telemetry quality

Detection success

Detection quality

False positives

Time to detect

Time to triage

Time to investigate

Response success

Remediation time

Retest success

Regression rate

Knowledge change

Knowledge retention

Cross-team transfer
```

Only collect metrics that support decisions.

---

# 113. Measurement Maturity Model

A simple maturity model is:

```text
Level 1 - Activity

Exercises and techniques are counted.

Level 2 - Results

Prevention and detection outcomes are measured.

Level 3 - Operations

Investigation and response performance are measured.

Level 4 - Improvement

Remediation and retesting are tracked.

Level 5 - Learning

Knowledge transfer and retention are measured.

Level 6 - Continuous Validation

Regression and recurring validation are measured.

Level 7 - Risk Alignment

Metrics are prioritised using threat and business context.
```

This can help organisations understand how their measurement capability evolves.

---

# 114. Level 1 - Activity

Typical questions:

```text
How many exercises did we run?

How many techniques did we test?
```

Useful for programme administration.

Limited for security effectiveness.

---

# 115. Level 2 - Results

Questions become:

```text
Which techniques were prevented?

Which were detected?

Which were missed?
```

This begins measuring defensive outcomes.

---

# 116. Level 3 - Operations

Questions include:

```text
Did analysts see the alert?

Could they investigate it?

How quickly?

Was escalation correct?
```

This measures operational readiness.

---

# 117. Level 4 - Improvement

Questions include:

```text
Was the gap fixed?

Who owns it?

Was the fix retested?

How long did remediation take?
```

This closes the improvement loop.

---

# 118. Level 5 - Learning

Questions include:

```text
What did participants learn?

Can they reproduce the task?

Was knowledge retained?

Was knowledge transferred to others?
```

This evaluates the human capability created by purple teaming.

---

# 119. Level 6 - Continuous Validation

Questions include:

```text
Does the detection still work?

Did a platform update break it?

Did telemetry change?

Did the control regress?
```

This moves from exercise-based assurance toward continuous validation.

---

# 120. Level 7 - Risk Alignment

Questions include:

```text
Are we testing the techniques most relevant to our threats?

Are critical business systems covered?

Are high-risk gaps remediated first?

Does the programme influence security investment?
```

Measurement becomes connected to organisational risk.

---

# Purple Team Metrics Checklist

## Objectives

- [ ] Define exercise objective
- [ ] Define learning objective
- [ ] Define expected controls
- [ ] Define success criteria
- [ ] Define measurement scope
- [ ] Define metric owners

## Baseline

- [ ] Record existing detection state
- [ ] Record telemetry availability
- [ ] Record relevant response capability
- [ ] Record knowledge baseline where appropriate
- [ ] Record existing ATT&CK coverage

## Execution

- [ ] Record attempted technique
- [ ] Record execution result
- [ ] Record prevention result
- [ ] Record timestamps
- [ ] Distinguish control failure from test failure

## Telemetry

- [ ] Confirm telemetry generation
- [ ] Confirm collection
- [ ] Confirm forwarding
- [ ] Confirm parsing
- [ ] Confirm required fields
- [ ] Measure latency where relevant
- [ ] Record missing data

## Detection

- [ ] Record detection result
- [ ] Record alert result
- [ ] Record detection depth
- [ ] Record relevant rule
- [ ] Record false positives where measurable
- [ ] Record false negatives
- [ ] Identify root cause for failures

## Investigation

- [ ] Record analyst visibility
- [ ] Record triage result
- [ ] Record investigation result
- [ ] Record investigation accuracy
- [ ] Record escalation result
- [ ] Record relevant timing

## Response

- [ ] Define whether response is in scope
- [ ] Record response result
- [ ] Record containment where authorised
- [ ] Record escalation
- [ ] Record response timing

## Improvement

- [ ] Create action
- [ ] Assign owner
- [ ] Identify root cause
- [ ] Record implementation
- [ ] Perform retest
- [ ] Mark validated only after successful retest

## Knowledge

- [ ] Establish baseline where appropriate
- [ ] Measure post-exercise understanding
- [ ] Include practical validation
- [ ] Measure independent reproduction
- [ ] Measure retention where useful
- [ ] Capture reusable knowledge

## Continuous Validation

- [ ] Convert important tests to regression tests
- [ ] Track regression status
- [ ] Review telemetry health
- [ ] Review detection health
- [ ] Revalidate after major changes

## Reporting

- [ ] Define denominators
- [ ] Explain percentages
- [ ] Include qualitative context
- [ ] Avoid vanity metrics
- [ ] Avoid unsupported conclusions
- [ ] Segment incompatible datasets
- [ ] Explain limitations
- [ ] Connect results to risk

---

# Quick Measurement Workflow

```text
Define Objective
       |
       v
Define Success Criteria
       |
       v
Establish Baseline
       |
       v
Execute Technique
       |
       v
Confirm Execution
       |
       +--------------------+
       |                    |
       v                    v
   Prevented             Executed
       |                    |
       |                    v
       |              Check Telemetry
       |                    |
       |                    v
       |              Check Detection
       |                    |
       |                    v
       |              Check Investigation
       |                    |
       |                    v
       |               Check Response
       |                    |
       +---------+----------+
                 |
                 v
            Identify Gaps
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
         Measure Knowledge
                 |
                 v
             Document
                 |
                 v
         Regression Testing
```

---

# Measurement Interpretation Model

For every metric, ask:

```text
What question does this metric answer?

What is the numerator?

What is the denominator?

What is the data source?

What is the time period?

What is the scope?

What counts as success?

What counts as failure?

What is excluded?

What assumptions exist?

Can the metric be gamed?

What decision will it support?
```

If these questions cannot be answered, the metric may not be reliable enough for decision-making.

---

# Reporting Model

A strong purple team measurement statement follows:

```text
Scope
  +
Method
  +
Result
  +
Interpretation
  +
Limitation
  +
Improvement
  +
Validation
```

Example:

> During the exercise, 20 threat-relevant techniques were successfully executed against the agreed endpoint scope. Fifteen generated the expected detection, resulting in a validated detection rate of 75% for the tested technique set. Three failures were caused by missing telemetry and two by detection-logic gaps. Following remediation, all five failed scenarios were repeated and four generated the expected alert. One telemetry gap remains open and has been assigned to Security Engineering.

This is considerably stronger than:

> Detection coverage was 75%.

---

# Metrics Should Tell a Story

The objective is not to create the largest possible dashboard.

The useful story is:

```text
We expected this.
       |
       v
We tested it.
       |
       v
This happened.
       |
       v
This control worked.
       |
       v
This control failed.
       |
       v
This is why.
       |
       v
We changed it.
       |
       v
We tested it again.
       |
       v
It now works.
       |
       v
The team understands why.
       |
       v
We will continue validating it.
```

That is meaningful purple team measurement.

---

# Related Notes

- [Purple Teaming Overview](index.md)
- [Purple Teaming Methodology](methodology.md)
- [Purple Team Exercises](exercises.md)
- [Detection Engineering](detection-engineering.md)
- [MITRE ATT&CK](mitre-attack.md)
- [Knowledge Transfer](knowledge-transfer.md)

The next planned Purple Teaming pages are:

```text
after-action-review.md
continuous-validation.md
```

---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Data Sources](https://attack.mitre.org/datasources/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Detection Strategies](https://attack.mitre.org/detectionstrategies/){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-61 - Incident Response Recommendations and Considerations for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final){ target="_blank" rel="noopener noreferrer" }
- [NICE Workforce Framework for Cybersecurity](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center){ target="_blank" rel="noopener noreferrer" }

!!! tip "Define the denominator"

    A percentage without a clearly defined denominator can be misleading. Always explain whether detection coverage refers to planned techniques, attempted techniques, successfully executed techniques or threat-relevant techniques.

!!! tip "Measure the complete chain"

    Detection is only one part of defensive capability. Where appropriate, measure telemetry, detection, analyst investigation, response, remediation and retesting.

!!! tip "Combine quantitative and qualitative evidence"

    Metrics show what changed. Exercise observations and technical investigation help explain why it changed.

!!! tip "Measure improvement, not activity"

    The number of exercises or techniques executed can describe programme activity, but stronger evidence comes from validated improvements in prevention, detection, investigation, response and knowledge.

!!! warning "Do not optimise for the metric"

    A metric can become harmful when teams change behavior primarily to improve the number. Use balanced measurements and regularly review whether each metric still represents the security outcome it was intended to measure.
