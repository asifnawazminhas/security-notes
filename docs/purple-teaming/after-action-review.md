---
title: Purple Teaming After-Action Review
description: Practical guidance for conducting purple team after-action reviews, analysing exercise outcomes, identifying root causes, capturing lessons, assigning improvements and validating remediation.
---

# Purple Teaming After-Action Review

An after-action review (AAR) converts purple team exercise activity into structured learning and measurable improvement.

The technical exercise may have finished, but the improvement process has not.

A useful lifecycle is:

```text
Exercise
   |
   v
Evidence Collection
   |
   v
After-Action Review
   |
   v
Root Cause Analysis
   |
   v
Lessons Identified
   |
   v
Actions Assigned
   |
   v
Improvements Implemented
   |
   v
Retest
   |
   v
Lessons Validated
   |
   v
Continuous Validation
```

The purpose of the AAR is not simply to document what happened.

It should determine:

```text
What was expected?

What actually happened?

Why did it happen?

What worked?

What failed?

What did participants learn?

What should change?

Who owns the change?

How will the change be validated?

How will the improvement be sustained?
```

---

## 1. Why After-Action Reviews Matter

Purple team exercises generate observations across offensive, defensive and operational workflows.

Without a structured review:

```text
Exercise
   |
   v
Interesting Findings
   |
   v
Informal Discussion
   |
   v
People Return to Normal Work
   |
   v
Knowledge Fades
```

With an AAR:

```text
Exercise
   |
   v
Evidence
   |
   v
Shared Analysis
   |
   v
Root Cause
   |
   v
Action
   |
   v
Owner
   |
   v
Improvement
   |
   v
Retest
```

The review helps turn observations into organisational change.

---

## 2. The AAR Is Part of the Exercise

The AAR should not be treated as an optional administrative meeting after the technical work.

It is part of the exercise lifecycle:

```text
Plan
  |
  v
Prepare
  |
  v
Execute
  |
  v
Observe
  |
  v
Review
  |
  v
Improve
  |
  v
Retest
```

Time for the review should therefore be included in exercise planning.

---

## 3. Core AAR Questions

A practical AAR can be organised around five questions:

```text
1. What was supposed to happen?

2. What actually happened?

3. Why was there a difference?

4. What did we learn?

5. What will we change?
```

Purple teaming adds a sixth:

```text
6. How will we prove the change worked?
```

That final question connects the AAR directly to retesting.

---

## 4. Expected Versus Observed

The starting point should be the difference between expectation and reality.

Example:

```text
Expected:
Credential-access activity generates telemetry and triggers an alert.

Observed:
Technique executed successfully.
Endpoint telemetry was generated.
No SIEM alert was created.
```

This creates the investigation question:

```text
Why?
```

---

## 5. AAR Assessment Model

A useful review model is:

```text
Objective
   |
   v
Expected Behavior
   |
   v
Observed Behavior
   |
   v
Evidence
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

This prevents the review from stopping at symptoms.

---

# 6. AAR Inputs

Before the review, collect the relevant evidence.

Potential inputs include:

```text
Exercise plan

Scenario description

Attack procedures

ATT&CK mappings

Red team notes

Blue team notes

Facilitator observations

SIEM events

EDR telemetry

Detection alerts

Detection queries

Screenshots

System logs

Exercise timestamps

Response actions

Tickets

Participant feedback

Pre/post measurements
```

The exact evidence depends on exercise scope.

---

# 7. Exercise Timeline

A shared timeline is one of the most useful AAR artifacts.

Example:

```text
14:00:00 Exercise started

14:05:12 Technique executed

14:05:15 Endpoint telemetry generated

14:05:27 Telemetry reached SIEM

14:05:41 Detection rule evaluated

14:05:44 Alert generated

14:06:10 Analyst opened alert

14:08:32 Analyst identified technique

14:10:15 Escalation completed

14:20:00 Detection improvement discussed

14:35:00 Detection updated

14:42:00 Technique repeated

14:42:37 Updated detection triggered
```

A timeline helps participants reconstruct what actually occurred.

---

# 8. Timestamp Quality

Before drawing timing conclusions, verify:

```text
Time zones

Clock synchronisation

Endpoint timestamps

SIEM timestamps

EDR timestamps

Red team timestamps

Analyst timestamps
```

Incorrect clock assumptions can produce misleading conclusions.

---

# 9. Exercise Objectives

Review the original objectives first.

Example:

```text
Objective 1:
Validate telemetry for the selected technique.

Objective 2:
Determine whether the existing detection identifies the behavior.

Objective 3:
Evaluate SOC investigation.

Objective 4:
Identify opportunities for detection improvement.

Objective 5:
Transfer technique and telemetry knowledge between teams.
```

The AAR should evaluate outcomes against these objectives.

---

# 10. Success Criteria

Review the predefined success criteria.

Example:

| Objective | Success Criterion |
|---|---|
| Telemetry | Required events available |
| Detection | Alert generated |
| Investigation | Analyst identifies host and user |
| Response | Correct escalation performed |
| Learning | Analyst explains detection dependency |
| Improvement | Failed scenario successfully retested |

This prevents success from being redefined after the exercise.

---

# 11. Participants

The review should include the roles required to explain the exercise.

Potential participants include:

```text
Red team operators

SOC analysts

Detection engineers

Incident responders

Threat intelligence

Security engineers

Platform owners

Purple team facilitator

Exercise coordinator
```

Not every exercise requires every role.

---

# 12. Independent Facilitation

Where practical, a facilitator can help keep the review:

```text
Structured

Evidence-based

Objective-focused

Time-bounded

Non-punitive

Action-oriented
```

The facilitator should encourage explanation rather than competition.

---

# 13. Psychological Safety

Participants should be able to say:

```text
I missed the alert.

I misunderstood the technique.

The rule was configured incorrectly.

Our assumption was wrong.

The documentation was unclear.

I do not know why this happened.
```

without the review becoming a blame session.

Purple teaming depends on exposing weaknesses so they can be improved.

---

# 14. Blameless Does Not Mean Unaccountable

A non-punitive review does not mean ignoring responsibility.

Distinguish:

```text
Blame:
Who caused this?

Accountability:
Who owns the improvement?
```

The AAR should focus on systems, processes, controls and decisions while still assigning clear action ownership.

---

# 15. Red Team Perspective

The offensive team should explain:

```text
What technique was executed?

Why was it selected?

What prerequisites existed?

Which procedure was used?

Did execution behave as expected?

Which controls were encountered?

Were variations attempted?

What artifacts were expected?
```

This gives defenders technical context.

---

# 16. Blue Team Perspective

The defensive team should explain:

```text
What telemetry was expected?

What telemetry was observed?

Did a rule match?

Was an alert generated?

Was the alert actionable?

How was it investigated?

What was missed?

What worked well?
```

This provides the defensive view of the same activity.

---

# 17. Compare Perspectives

The AAR should combine both views.

```text
Red View
   |
   +---- Technique succeeded
   |
   +---- Expected process telemetry
   |
   v
Shared Timeline
   ^
   |
   +---- Process telemetry received
   |
   +---- Detection did not trigger
   |
Blue View
```

The shared view helps identify where assumptions differ.

---

# 18. Separate Facts From Assumptions

During the review, distinguish:

```text
Fact

Observation

Interpretation

Assumption

Hypothesis
```

Example:

```text
Fact:
The technique executed at 14:05.

Observation:
The expected process event exists in EDR.

Observation:
No corresponding SIEM event was found.

Hypothesis:
The event was not forwarded.

Validation Required:
Review forwarding configuration.
```

This improves the quality of conclusions.

---

# 19. Evidence-Based Discussion

Prefer:

> The endpoint generated Event X at 14:05:15, but the SIEM search contains no corresponding event during the test window.

over:

> Logging did not work.

The first statement can be investigated.

The second is too broad.

---

# 20. Positive Outcomes

The AAR should capture what worked, not only failures.

Examples:

```text
Technique correctly blocked

Expected telemetry generated

Detection triggered

Alert reached SOC

Analyst identified attack

Escalation followed correctly

Detection documentation was useful

Red-blue communication was effective
```

Understanding successful behavior helps preserve it.

---

# 21. Why Did It Work?

Successful controls should also be analysed.

Ask:

```text
Which control worked?

Which configuration enabled success?

Which telemetry supported detection?

Which detection logic matched?

Which analyst action was effective?

Would the result survive a technique variation?
```

This identifies defensive strengths.

---

# 22. Negative Outcomes

Examples include:

```text
Technique unexpectedly succeeded

Telemetry missing

Telemetry incomplete

Detection failed

Alert delayed

Alert lacked context

Analyst missed alert

Investigation incorrect

Escalation failed

Response procedure unclear

Remediation ineffective
```

Each should be investigated rather than simply recorded.

---

# 23. Unexpected Outcomes

Some of the most valuable exercise results are unexpected.

Examples:

```text
Unexpected control prevented technique

Different telemetry appeared

Existing detection triggered for another reason

Attack caused unrelated alert

Technique behaved differently on another host

Response process worked better than expected
```

Capture these observations.

They may reveal both strengths and hidden dependencies.

---

# 24. Root Cause Analysis

The AAR should move from:

```text
What failed?
```

to:

```text
Why did it fail?
```

A useful model is:

```text
Observed Failure
      |
      v
Immediate Cause
      |
      v
Contributing Factors
      |
      v
Underlying Cause
      |
      v
Corrective Action
```

---

# 25. Detection Failure Analysis

For a missed detection:

```text
Technique Executed
       |
       v
Telemetry Generated?
       |
   +---+---+
   |       |
  No      Yes
   |       |
   v       v
Sensor    Telemetry Collected?
Gap           |
           +--+--+
           |     |
          No    Yes
           |     |
           v     v
       Collection Detection Logic
       Gap        Available?
                     |
                  +--+--+
                  |     |
                 No    Yes
                  |     |
                  v     v
              Detection Rule
              Gap       Matched?
                           |
                        +--+--+
                        |     |
                       No    Yes
                        |     |
                        v     v
                    Logic    Alert Generated?
                    Gap          |
                              +--+--+
                              |     |
                             No    Yes
                              |     |
                              v     v
                           Alert   Analyst
                           Pipeline Response
```

This helps locate the failure accurately.

---

# 26. Common Root Cause Categories

Useful categories include:

```text
Test design

Technique execution

Preventive control

Sensor configuration

Telemetry generation

Telemetry collection

Telemetry forwarding

Parsing

Data quality

Detection logic

Detection deployment

Alert routing

Triage

Investigation

Escalation

Response

Documentation

Training

Ownership

Process
```

Consistent categories make programme-level analysis easier.

---

# 27. Five Whys

The Five Whys technique can help explore underlying causes.

Example:

```text
Problem:
The alert did not trigger.

Why?
The detection query did not match.

Why?
The required field was empty.

Why?
The parser did not populate the field.

Why?
The log format changed after a platform upgrade.

Why?
Parser compatibility was not included in post-upgrade validation.
```

Potential underlying issue:

```text
No detection regression validation after platform changes.
```

The appropriate action may therefore be broader than modifying one query.

---

# 28. Do Not Force Five Whys

Not every problem has exactly five causal layers.

The technique is a prompt for deeper analysis, not a rigid formula.

Stop when the evidence supports a meaningful underlying cause.

---

# 29. Contributing Factors

A failure may have multiple causes.

Example:

```text
Primary Cause:
Detection query expected wrong field.

Contributing Factor:
Detection documentation did not identify required schema.

Contributing Factor:
No automated regression test existed.

Contributing Factor:
Platform change was not communicated to Detection Engineering.
```

Capture relevant contributing factors.

---

# 30. Human Error as a Starting Point

Avoid ending root cause analysis with:

```text
Analyst error
```

Ask:

```text
Was the alert understandable?

Was the procedure documented?

Was training sufficient?

Was workload realistic?

Was required context available?

Was escalation clear?

Did tooling support the task?
```

Human actions often occur within system conditions that can be improved.

---

# 31. Lessons Identified

An exercise observation becomes a lesson identified when its significance is understood.

Example:

```text
Observation:
The SOC did not receive the expected alert.

Lesson Identified:
Detection depends on a telemetry field that is not consistently
populated across endpoint versions.
```

This is more useful than the observation alone.

---

# 32. Lessons Identified Versus Lessons Learned

Use the distinction:

```text
Observation
     |
     v
Lesson Identified
     |
     v
Action Defined
     |
     v
Action Implemented
     |
     v
Action Retested
     |
     v
Improvement Sustained
     |
     v
Lesson Learned
```

A lesson is not fully learned merely because it appears in an AAR document.

---

# 33. Good Lesson Statements

A useful lesson explains:

```text
What happened

Why it matters

What caused it

What should change
```

Example:

> The detection depended on command-line telemetry that was available in EDR but not forwarded to the SIEM. As a result, the SIEM analytic could not evaluate the behavior. The collection policy should be updated and the scenario repeated to validate the change.

---

# 34. Weak Lesson Statements

Avoid:

```text
Logging needs improvement.

SOC needs more training.

Detection failed.

Red team succeeded.

Communication could be better.
```

These statements do not explain enough to support action.

---

# 35. Improvement Actions

Each actionable lesson should produce a clear task where appropriate.

Example:

```text
Lesson:
Required endpoint telemetry is not forwarded.

Action:
Add the required event source to the SIEM forwarding policy.

Owner:
Security Engineering.

Priority:
High.

Due Date:
Agreed programme date.

Validation:
Repeat technique and confirm event ingestion and alert generation.
```

---

# 36. SMART Actions

Actions are more useful when they are:

```text
Specific

Measurable

Achievable

Relevant

Time-bound
```

Weak:

```text
Improve logging.
```

Stronger:

```text
Enable forwarding of the required PowerShell event channel
for the agreed Windows endpoint scope and validate ingestion
using the original purple team test.
```

---

# 37. Action Ownership

Every action should have an owner.

Avoid:

```text
Owner:
Security Team
```

where possible.

Prefer a specific accountable role or team:

```text
Detection Engineering

SOC Engineering

Endpoint Security

Identity Team

Platform Engineering
```

Ownership should match the organisation's operating model.

---

# 38. Action Priority

Prioritisation can consider:

```text
Threat relevance

Business impact

Exploitability

Asset criticality

Detection dependency

Attack-chain position

Frequency

Existing compensating controls

Remediation complexity
```

Do not prioritise solely by how interesting the technique was.

---

# 39. Action Status

A useful lifecycle is:

```text
Open
  |
  v
Assigned
  |
  v
In Progress
  |
  v
Implemented
  |
  v
Retest Required
  |
  v
Validated
  |
  v
Closed
```

Keep:

```text
Implemented
```

and:

```text
Validated
```

separate.

---

# 40. Accepted Risk

Some actions may not be implemented.

Possible reasons include:

```text
Business constraint

Technical limitation

Low threat relevance

Compensating control

Cost

Planned platform replacement
```

If risk is accepted:

```text
Document rationale

Identify decision owner

Record compensating controls

Define review date
```

Do not silently close the action.

---

# 41. Retesting

Retesting should answer:

> Did the implemented change address the original gap?

Use the original scenario where possible.

```text
Original Technique
       |
       v
Original Failure
       |
       v
Improvement
       |
       v
Same Technique Repeated
       |
       v
Expected Result?
```

---

# 42. Retest Evidence

Capture:

```text
Retest timestamp

Technique

Environment

Configuration state

Telemetry

Detection

Alert

Investigation

Response

Result
```

This supports a defensible closure decision.

---

# 43. Positive Retest

Example:

```text
Original:
Technique executed without alert.

Improvement:
Detection logic corrected.

Retest:
Technique repeated.

Observed:
Alert generated after 34 seconds.

Analyst:
Correctly identified host, user and technique.

Result:
Validated.
```

---

# 44. Failed Retest

A failed retest should reopen analysis.

```text
Change Implemented
       |
       v
Retest Failed
       |
       v
Why?
       |
       v
New Evidence
       |
       v
Root Cause Revisited
```

Do not repeatedly modify controls without understanding why previous changes failed.

---

# 45. Partial Retest

Sometimes an improvement addresses only part of the gap.

Example:

```text
Telemetry now forwarded:
Yes

Detection:
Yes

Alert context:
Incomplete

Investigation:
Still difficult
```

Result:

```text
Partial improvement
```

rather than:

```text
Fully resolved
```

---

# 46. Knowledge Transfer Review

The AAR should evaluate what participants learned.

Ask:

```text
What did Red learn?

What did Blue learn?

What did Detection Engineering learn?

What did the SOC learn?

What assumptions changed?

What knowledge should be shared?
```

See [Knowledge Transfer](knowledge-transfer.md).

---

# 47. Knowledge Transfer Evidence

Potential evidence includes:

```text
Participant can explain technique

Participant can identify telemetry

Participant can explain detection

Participant can reproduce query

Participant can investigate alert

Documentation created

Playbook updated

Knowledge shared with another team
```

---

# 48. Teach-Back During the AAR

Ask participants to explain the result in their own words.

For example:

```text
Blue explains:
Why the technique was initially missed.

Red explains:
Which telemetry exposed the technique.

Detection engineer explains:
Why the corrected analytic now works.
```

Teach-back can reveal misunderstandings before the review closes.

---

# 49. Review Collaboration

Discuss the collaboration itself.

Questions include:

```text
Was information shared quickly enough?

Were roles clear?

Could teams ask questions?

Did participants understand objectives?

Were feedback cycles effective?

Were there unnecessary delays?

Did any process discourage collaboration?
```

This helps improve future exercises.

---

# 50. Review Exercise Design

Not every problem belongs to the defensive environment.

The exercise itself may have issues.

Examples:

```text
Unclear objective

Unrealistic scenario

Incorrect prerequisite

Wrong target

Insufficient preparation

Technique not relevant

Poor timing

Missing participant

Test procedure error
```

Capture these separately from security-control gaps.

---

# 51. Test Failure Versus Security Failure

Distinguish:

```text
Test Failure
```

from:

```text
Security Failure
```

Example:

```text
Technique did not execute because the test script contained an error.
```

This is not evidence that the defensive control prevented the technique.

Similarly:

```text
Alert did not trigger because the technique never executed.
```

This is not evidence of a detection gap.

---

# 52. Prevention Versus Detection

If a preventive control blocks the technique:

```text
Technique Attempted
       |
       v
Preventive Control
       |
       v
Blocked
```

record:

```text
Prevention:
Successful
```

Then determine whether:

```text
Telemetry existed

Alert existed

SOC visibility existed
```

Prevention and detection are separate outcomes.

---

# 53. Detection Versus Investigation

An alert does not prove successful defence.

Review:

```text
Alert generated?
       |
       v
Alert seen?
       |
       v
Alert understood?
       |
       v
Scope identified?
       |
       v
Escalation correct?
       |
       v
Response correct?
```

This helps identify operational gaps after detection.

---

# 54. Review Timing Metrics

Where timing is measured, review:

```text
Time to telemetry

Time to detection

Time to alert

Time to triage

Time to investigation

Time to escalation

Time to response
```

See [Metrics and Measurement](metrics-and-measurement.md).

---

# 55. Explain Timing Outliers

Do not record only averages.

Investigate unusual results.

Example:

```text
Median TTD:
42 seconds

One test:
11 minutes
```

Ask why.

Possible causes:

```text
Ingestion delay

Rule schedule

Queue backlog

Analyst workload

Sensor connectivity
```

Outliers can reveal hidden weaknesses.

---

# 56. Review Detection Quality

For successful detections, ask:

```text
Was the alert specific enough?

Did it identify the relevant host?

Did it identify the user?

Did it provide useful process context?

Was severity appropriate?

Was the ATT&CK mapping correct?

Were false positives understood?

Could the analyst act on it?
```

A technically triggered alert may still require improvement.

---

# 57. Review False Positives

If detection tuning occurred, evaluate whether the change creates unnecessary alerts.

Ask:

```text
What legitimate behavior also matches?

What exclusions exist?

Are exclusions too broad?

Can contextual fields improve precision?

Could the change hide malicious variants?
```

Do not improve detection rate by creating unusably broad rules.

---

# 58. Review Technique Variations

If only one implementation was tested, record that limitation.

Example:

```text
Validated:
Technique using Procedure A.

Not validated:
Alternative tools.
Alternative parent processes.
Alternative protocols.
Alternative privilege levels.
```

Avoid claiming complete coverage from one procedure.

---

# 59. Review ATT&CK Mapping

Check whether the exercise mapping accurately represents the behavior.

Ask:

```text
Was the correct technique selected?

Is a sub-technique more appropriate?

Did the scenario contain multiple techniques?

Does the detection map to behavior or merely the tool?
```

See [MITRE ATT&CK](mitre-attack.md).

---

# 60. Review Detection Engineering

For detections created or modified during the exercise, confirm:

```text
Detection objective

Required telemetry

Relevant fields

Query logic

Known false positives

Known blind spots

ATT&CK mapping

Investigation guidance

Owner

Test procedure
```

See [Detection Engineering](detection-engineering.md).

---

# 61. Review Documentation

Ask:

```text
Could someone who missed the exercise understand the result?

Can another analyst reproduce the investigation?

Can another operator reproduce the test?

Does the detection explain its dependencies?

Does the playbook explain what to do?
```

Documentation should preserve the knowledge created during the exercise.

---

# 62. Review Existing Runbooks

Exercise results may reveal outdated runbooks.

Check:

```text
Queries

Screenshots

Hostnames

Tool names

Escalation contacts

Detection names

Response procedures

Data-source assumptions
```

Update them where required.

---

# 63. Review Communication

Purple team exercises depend on communication.

Evaluate:

```text
Pre-exercise briefing

Real-time communication

Technical terminology

Escalation communication

Decision communication

Post-exercise communication
```

Communication gaps may be operational security gaps.

---

# 64. Review Roles and Responsibilities

Ask whether everyone understood:

```text
Who executes?

Who observes?

Who investigates?

Who approves changes?

Who records evidence?

Who facilitates?

Who owns remediation?

Who performs retest?
```

Unclear roles can delay both exercises and real incidents.

---

# 65. Review Tooling

Tooling may affect exercise performance.

Examples:

```text
SIEM search limitations

EDR access

Missing dashboards

Slow queries

Attack automation failure

Ticketing workflow

Communication tooling
```

Record tooling problems separately from detection logic where appropriate.

---

# 66. Review Environment Differences

A test may behave differently across:

```text
Operating systems

Endpoint versions

Cloud environments

Business units

Network segments

Security-control versions
```

Document environmental limitations.

Do not assume one validated environment represents all environments.

---

# 67. Review Scope Limitations

Every AAR should identify relevant limitations.

Examples:

```text
Only one endpoint tested

Only one technique variation tested

No containment performed

No production systems tested

Small participant group

Limited exercise duration

Some telemetry unavailable
```

This makes conclusions more defensible.

---

# 68. Review Safety

Confirm whether the exercise stayed within:

```text
Authorised scope

Agreed techniques

Agreed targets

Agreed time window

Agreed safety constraints
```

Record unexpected operational impact if any occurred.

---

# 69. Safety Lessons

Examples include:

```text
Test caused excessive alert volume

Test affected application performance

Cleanup was incomplete

Technique created unexpected persistence

Test data reached unintended monitoring system
```

Safety lessons should influence future exercise design.

---

# 70. Cleanup Review

Confirm required cleanup.

Examples:

```text
Test accounts removed

Test files removed

Temporary rules removed

Temporary exclusions removed

Test services removed

Test scheduled jobs removed

Temporary infrastructure removed

Credentials rotated where required
```

Do not assume cleanup occurred simply because the exercise ended.

---

# 71. Preserve Required Evidence

Cleanup should not destroy required assessment evidence.

Before removing artifacts:

```text
Capture timestamps

Capture logs

Capture configuration

Capture screenshots where required

Record hashes where relevant

Preserve exercise notes
```

Follow organisational evidence-handling requirements.

---

# 72. AAR Meeting Structure

A practical meeting can follow:

```text
1. Reconfirm objectives

2. Review timeline

3. Review successful outcomes

4. Review failed outcomes

5. Analyse root causes

6. Identify lessons

7. Define actions

8. Assign owners

9. Define retests

10. Confirm follow-up
```

This keeps the review focused.

---

# 73. Example 60-Minute AAR

```text
00-05 min
Objectives and scope

05-15 min
Exercise timeline

15-25 min
What worked

25-40 min
What failed and root causes

40-50 min
Lessons and improvements

50-55 min
Owners and priorities

55-60 min
Retest and follow-up
```

Complex exercises may require longer sessions.

---

# 74. Immediate Hotwash

A short review immediately after the exercise can capture fresh observations.

Example:

```text
15-30 minutes

What worked?

What failed?

What surprised us?

What needs immediate attention?
```

This is sometimes called a hotwash.

It should not necessarily replace a more structured AAR.

---

# 75. Formal AAR

A formal review can occur after evidence has been consolidated.

It can include:

```text
Complete timeline

Technical evidence

Root cause analysis

Metrics

Participant feedback

Lessons

Actions

Owners

Retest plan
```

This produces a more defensible record.

---

# 76. Hotwash Versus Formal Review

A useful model is:

```text
Exercise Ends
     |
     v
Immediate Hotwash
     |
     v
Evidence Consolidation
     |
     v
Formal AAR
     |
     v
Action Tracking
```

The hotwash captures immediate observations.

The formal AAR validates them against evidence.

---

# 77. AAR Record

A structured record might contain:

```text
Exercise ID

Date

Scope

Participants

Objectives

Techniques

Expected outcomes

Observed outcomes

Timeline

Positive observations

Gaps

Root causes

Lessons identified

Actions

Owners

Priorities

Due dates

Retest criteria

Status
```

---

# 78. Example AAR Record

```text
Exercise ID:
PT-2026-021

Objective:
Validate detection of the selected execution technique.

Expected:
Endpoint telemetry reaches SIEM and triggers detection.

Observed:
Endpoint telemetry generated.
SIEM received event.
Detection did not match.

Root Cause:
Detection rule referenced legacy field name.

Contributing Factor:
Parser schema changed during previous platform upgrade.

Lesson Identified:
Detection dependencies are not currently regression-tested after
schema changes.

Immediate Action:
Update detection to use current field.

Programme Action:
Add detection regression testing to platform-change validation.

Owner:
Detection Engineering.

Retest:
Repeat original technique after rule update.

Success Criterion:
Expected alert generated and correctly investigated.

Status:
Retest Required.
```

---

# 79. Action Tracker

A practical action table is:

| ID | Action | Owner | Priority | Status | Validation |
|---|---|---|---|---|---|
| AAR-01 | Correct detection field | Detection Engineering | High | Implemented | Retest |
| AAR-02 | Update forwarding policy | Security Engineering | High | In Progress | Telemetry test |
| AAR-03 | Update SOC playbook | SOC | Medium | Open | Analyst review |
| AAR-04 | Add regression test | Purple Team | Medium | Open | Automated test |

The tracker should remain active after the meeting.

---

# 80. Action Dependencies

Some actions depend on others.

Example:

```text
Enable Telemetry
      |
      v
Update Parser
      |
      v
Update Detection
      |
      v
Update Playbook
      |
      v
Retest
```

Record dependencies to avoid premature validation.

---

# 81. Action Aging

Track how long actions remain unresolved.

Example:

```text
0-30 days

31-60 days

61-90 days

90+ days
```

Long-lived actions may indicate:

```text
Ownership problem

Priority problem

Resource constraint

Technical complexity

Risk acceptance
```

---

# 82. Repeated Findings

Repeated lessons are important.

If multiple exercises identify:

```text
Missing telemetry
```

the issue may not be individual detection rules.

It may indicate a broader:

```text
Telemetry governance problem
```

Programme-level trend analysis can identify systemic causes.

---

# 83. Recurring Root Causes

Track recurring categories such as:

```text
Telemetry gaps

Parser issues

Detection logic

Alert routing

Documentation

Training

Ownership

Platform changes
```

Repeated root causes should influence programme priorities.

---

# 84. Escalating Systemic Issues

A systemic issue may require broader action.

Example:

```text
Exercise 1 -> Parser failure

Exercise 2 -> Parser failure

Exercise 3 -> Parser failure
```

Instead of fixing three detections independently:

```text
Review parser lifecycle and change-management process.
```

The AAR should help reveal this pattern.

---

# 85. Metrics in the AAR

Useful metrics may include:

```text
Technique execution success

Prevention result

Telemetry availability

Detection result

Detection depth

Time to detect

Investigation result

Response result

Remediation status

Retest result

Knowledge improvement
```

See [Metrics and Measurement](metrics-and-measurement.md).

---

# 86. Do Not Let Metrics Replace Discussion

A dashboard may show:

```text
Detection Rate: 80%
```

but the AAR should ask:

```text
Why were 20% missed?

Were misses concentrated in one tactic?

Were they caused by telemetry?

Were alerts actionable?

Did technique difficulty vary?
```

Metrics should guide investigation.

---

# 87. Participant Feedback

Participant feedback can help evaluate:

```text
Exercise realism

Learning value

Communication

Role clarity

Technical difficulty

Tooling

Facilitation

Time allocation
```

Use feedback to improve future exercises.

---

# 88. Example Feedback Questions

```text
Did the exercise objectives remain clear?

Did you understand your role?

Did collaboration help you understand the tested technique?

Did you learn something you can apply in your normal role?

Was the exercise technically realistic?

Was sufficient time available for investigation?

What should change in the next exercise?
```

---

# 89. Open-Ended Feedback

Open questions often reveal issues not captured by metrics.

Examples:

```text
What was the most useful part of the exercise?

What surprised you?

What was unclear?

What would you change?

What should we test next?
```

---

# 90. AAR Reporting

A concise AAR report should communicate:

```text
Scope

Objectives

What happened

What worked

What failed

Why

What was learned

What will change

Who owns the change

How it will be validated
```

Avoid overwhelming stakeholders with raw exercise logs unless they are required.

---

# 91. Executive Summary

Leadership may need:

```text
Exercise objective

Major strengths

Major gaps

Risk significance

Improvement actions

Outstanding risks

Validation status
```

Keep the technical evidence available separately.

---

# 92. Technical Detail

Technical stakeholders may require:

```text
Commands

Techniques

ATT&CK mappings

Telemetry

Queries

Detection logic

Timestamps

Root cause

Configuration changes

Retest evidence
```

Use appropriate detail for the audience.

---

# 93. Example Executive Finding

> The exercise demonstrated that endpoint telemetry for the selected technique was generated successfully but was not available to the SIEM detection layer because of a forwarding configuration gap. Security Engineering updated the collection policy and the original scenario was repeated successfully. The improvement has been validated, and the test will be retained for future regression testing.

This communicates:

```text
Gap

Cause

Action

Validation

Sustainability
```

---

# 94. Example Technical Finding

```text
Technique:
Selected ATT&CK technique

Execution:
Successful

Endpoint Telemetry:
Available

SIEM Telemetry:
Missing

Detection:
Not evaluated

Root Cause:
Required event source absent from forwarding policy

Remediation:
Forwarding policy updated

Retest:
Event successfully ingested

Detection:
Expected alert generated

Investigation:
SOC correctly identified test host and user

Status:
Validated
```

---

# 95. AAR Distribution

Distribute relevant outcomes to appropriate stakeholders.

Possible recipients include:

```text
SOC

Detection Engineering

Incident Response

Security Engineering

Platform Owners

Threat Intelligence

Security Leadership
```

Do not distribute sensitive offensive detail more broadly than necessary.

---

# 96. Sensitive Exercise Information

AAR artifacts may contain:

```text
Attack procedures

Credentials

Internal architecture

Detection gaps

Security-control weaknesses

Hostnames

IP addresses

Screenshots

Logs
```

Handle them according to organisational classification and access-control requirements.

---

# 97. Knowledge Repository

Store reusable outputs in approved locations.

Examples:

```text
Detection repository

Internal wiki

Exercise repository

Ticketing platform

Runbook repository

Threat emulation repository
```

Avoid leaving important knowledge only in meeting notes.

---

# 98. Version Control

Where appropriate, version:

```text
Detection rules

Attack procedures

Exercise scenarios

Queries

Runbooks

Configuration-as-code

Regression tests
```

This provides history and supports repeatability.

---

# 99. AAR Follow-Up

The review process should continue after the meeting.

Example:

```text
AAR
 |
 v
Actions
 |
 v
Weekly/Periodic Review
 |
 v
Implementation
 |
 v
Retest
 |
 v
Closure
```

Without follow-up, the AAR can become documentation without improvement.

---

# 100. Closure Criteria

An action should have explicit closure criteria.

Example:

```text
Configuration changed:
Not sufficient.

Telemetry visible:
Partial evidence.

Detection triggered:
Better.

Analyst successfully investigated:
Operational validation.

Regression test created:
Sustainability improvement.
```

Closure depends on the original objective.

---

# 101. Validation Ownership

The team implementing a change does not always need to be the only team validating it.

Example:

```text
Detection Engineering
        |
        v
Implements Rule
        |
        v
Purple Team
        |
        v
Repeats Technique
        |
        v
SOC
        |
        v
Confirms Investigation
```

This provides stronger end-to-end validation.

---

# 102. Reopen Criteria

An action may need to be reopened if:

```text
Retest fails

Detection regresses

Telemetry disappears

False positives become unacceptable

Platform change invalidates control

New technique variation exposes same gap
```

Closure should not make the issue invisible forever.

---

# 103. Continuous Improvement

The AAR should feed the next exercise.

```text
Exercise 1
   |
   v
AAR
   |
   v
Lessons
   |
   v
Improvement
   |
   v
Exercise 2
   |
   v
AAR
   |
   v
Further Improvement
```

This creates an iterative purple team programme.

---

# 104. Exercise Backlog

AAR findings can generate future tests.

Examples:

```text
Test another technique variation

Test same technique on Linux

Test same detection in cloud environment

Test response workflow

Test control after platform upgrade

Test alternative telemetry source
```

Add these to an exercise backlog.

---

# 105. Detection Backlog

Not every detection improvement can be completed during the exercise.

Record:

```text
Detection requirement

Threat relevance

Required telemetry

Owner

Priority

Validation procedure
```

This allows detection engineering to continue after the exercise.

---

# 106. Telemetry Backlog

Similarly, track:

```text
Missing data sources

Missing fields

Parser problems

Forwarding gaps

Retention issues

Latency issues
```

Telemetry engineering may be a prerequisite for future detections.

---

# 107. Knowledge Backlog

Some learning gaps may require:

```text
Training

Documentation

Workshop

Playbook update

Pairing

Future exercise
```

Track these alongside technical actions where appropriate.

---

# 108. What Not to Do

Avoid AARs that become:

```text
A presentation by one team

A blame session

A list of screenshots

A list of alerts

A scorecard without explanation

A report with no owners

A report with no retesting

A meeting with no follow-up
```

These approaches weaken the improvement cycle.

---

# 109. Common AAR Failure Modes

Common problems include:

```text
AAR occurs too late

Evidence is incomplete

Participants forget details

Only failures are discussed

Root cause analysis stops too early

Actions are vague

Owners are missing

Deadlines are unrealistic

Retesting is not planned

Lessons remain in meeting notes

Same findings recur
```

Recognising these patterns can improve the process.

---

# 110. Practical AAR Scenario

## Scenario

A purple team tests a persistence technique.

Expected result:

```text
Technique executes
      |
      v
Endpoint telemetry generated
      |
      v
SIEM receives telemetry
      |
      v
Detection triggers
      |
      v
SOC investigates
```

Observed result:

```text
Technique executes
      |
      v
Endpoint telemetry generated
      |
      v
SIEM receives telemetry
      |
      v
No alert
```

---

# 111. Evidence Review

The team confirms:

```text
Technique execution:
Successful

Endpoint event:
Present

SIEM event:
Present

Required fields:
Present

Detection rule:
Enabled

Rule match:
Failed
```

This narrows the investigation.

---

# 112. Root Cause

The detection contains a condition matching:

```text
process_name = example-old-name
```

The current platform records:

```text
process_name = example-current-name
```

Root cause:

```text
Detection logic no longer reflects current telemetry.
```

---

# 113. Contributing Cause

The team discovers:

```text
The endpoint platform was upgraded three months earlier.

No detection regression test was performed after the upgrade.
```

This creates a broader lesson.

---

# 114. Lesson Identified

```text
Individual Lesson:
Detection logic requires updating.

Programme Lesson:
Security-platform changes can invalidate detection assumptions,
and current change-management processes do not automatically
trigger detection regression testing.
```

The second lesson is more strategically important.

---

# 115. Corrective Actions

```text
Action 1:
Update detection logic.

Owner:
Detection Engineering.

Action 2:
Create regression test for the technique.

Owner:
Purple Team.

Action 3:
Add detection validation to endpoint platform change process.

Owner:
Security Engineering.
```

---

# 116. Retest

After the rule is updated:

```text
Technique repeated

Telemetry generated

SIEM event available

Detection triggered

Alert generated

SOC investigated correctly
```

Result:

```text
Technical remediation validated.
```

---

# 117. Follow-Up

The regression test is then added to recurring validation.

The result becomes:

```text
Exercise Finding
       |
       v
Root Cause
       |
       v
Detection Fix
       |
       v
Process Improvement
       |
       v
Regression Test
       |
       v
Continuous Validation
```

This demonstrates how an AAR can produce improvement beyond one detection rule.

---

# 118. AAR Maturity Model

A simple maturity model is:

```text
Level 1 - Informal

Teams discuss what happened.

Level 2 - Documented

Observations and findings are recorded.

Level 3 - Actionable

Lessons have owners and actions.

Level 4 - Validated

Actions require retesting before closure.

Level 5 - Measured

AAR trends and recurring root causes are analysed.

Level 6 - Integrated

Lessons influence engineering, training and future exercises.

Level 7 - Continuous

Validated improvements become recurring regression tests.
```

---

# 119. Level 1 - Informal

Typical state:

```text
Exercise finishes.

Teams discuss results.

Little documentation remains.
```

Knowledge is highly dependent on individuals.

---

# 120. Level 2 - Documented

The organisation records:

```text
Findings

Screenshots

Exercise notes

Basic lessons
```

This improves retention but may not create change.

---

# 121. Level 3 - Actionable

The organisation adds:

```text
Owners

Priorities

Actions

Due dates
```

The review begins driving operational improvement.

---

# 122. Level 4 - Validated

Actions cannot close solely because someone changed a configuration.

They require:

```text
Retest

Evidence

Expected outcome
```

This strengthens assurance.

---

# 123. Level 5 - Measured

The organisation analyses:

```text
Recurring root causes

Action completion

Retest success

Time to remediate

Repeated findings
```

AAR data begins informing programme decisions.

---

# 124. Level 6 - Integrated

Lessons influence:

```text
Detection engineering

SOC playbooks

Security architecture

Training

Threat emulation

Platform engineering

Change management
```

Purple teaming becomes integrated with normal security operations.

---

# 125. Level 7 - Continuous

Validated tests become recurring controls.

```text
Exercise
   |
   v
AAR
   |
   v
Improvement
   |
   v
Automated Test
   |
   v
Continuous Validation
   |
   v
Regression Detected
   |
   v
New Review
```

The feedback loop becomes continuous.

---

# After-Action Review Checklist

## Before the Review

- [ ] Collect exercise objectives
- [ ] Collect success criteria
- [ ] Collect red team notes
- [ ] Collect blue team notes
- [ ] Collect facilitator observations
- [ ] Collect telemetry
- [ ] Collect alerts
- [ ] Collect relevant queries
- [ ] Consolidate timestamps
- [ ] Build exercise timeline
- [ ] Identify required participants

## Exercise Reconstruction

- [ ] Confirm technique execution
- [ ] Confirm target
- [ ] Confirm timestamp
- [ ] Confirm prerequisites
- [ ] Confirm expected behavior
- [ ] Confirm observed behavior
- [ ] Separate facts from assumptions

## Positive Outcomes

- [ ] Identify successful controls
- [ ] Identify useful telemetry
- [ ] Identify successful detections
- [ ] Identify effective investigations
- [ ] Identify effective collaboration
- [ ] Determine why success occurred

## Gaps

- [ ] Identify prevention gaps
- [ ] Identify telemetry gaps
- [ ] Identify parsing gaps
- [ ] Identify detection gaps
- [ ] Identify alert-routing gaps
- [ ] Identify investigation gaps
- [ ] Identify response gaps
- [ ] Identify documentation gaps
- [ ] Identify exercise-design gaps

## Root Cause

- [ ] Identify immediate cause
- [ ] Identify contributing factors
- [ ] Identify underlying cause
- [ ] Validate assumptions with evidence
- [ ] Avoid stopping at "human error"
- [ ] Identify systemic patterns

## Lessons

- [ ] Document what happened
- [ ] Explain why it matters
- [ ] Explain root cause
- [ ] Identify transferable knowledge
- [ ] Distinguish lesson identified from lesson learned

## Actions

- [ ] Define specific action
- [ ] Assign owner
- [ ] Assign priority
- [ ] Define due date where appropriate
- [ ] Record dependencies
- [ ] Define validation criteria
- [ ] Record accepted risks explicitly

## Retesting

- [ ] Define retest procedure
- [ ] Use original scenario where practical
- [ ] Capture retest evidence
- [ ] Verify telemetry
- [ ] Verify detection
- [ ] Verify investigation where applicable
- [ ] Keep implemented and validated statuses separate

## Knowledge Transfer

- [ ] Capture what Red learned
- [ ] Capture what Blue learned
- [ ] Capture what engineering learned
- [ ] Update documentation
- [ ] Update runbooks
- [ ] Update detection guidance
- [ ] Share relevant knowledge
- [ ] Validate understanding where useful

## Exercise Improvement

- [ ] Review objectives
- [ ] Review scenario realism
- [ ] Review timing
- [ ] Review roles
- [ ] Review communication
- [ ] Review tooling
- [ ] Review safety
- [ ] Review cleanup

## Follow-Up

- [ ] Track open actions
- [ ] Review action aging
- [ ] Identify repeated findings
- [ ] Identify recurring root causes
- [ ] Add future tests to backlog
- [ ] Convert suitable tests into regression tests
- [ ] Feed lessons into the next exercise

---

# Quick AAR Workflow

```text
Exercise Ends
      |
      v
Immediate Hotwash
      |
      v
Collect Evidence
      |
      v
Build Timeline
      |
      v
Compare Expected vs Observed
      |
      v
Identify Strengths
      |
      v
Identify Gaps
      |
      v
Root Cause Analysis
      |
      v
Lessons Identified
      |
      v
Define Actions
      |
      v
Assign Owners
      |
      v
Implement
      |
      v
Retest
      |
      +--------------------+
      |                    |
      v                    v
    Pass                  Fail
      |                    |
      v                    v
  Validate            Reanalyse
      |                    |
      +---------+----------+
                |
                v
        Capture Knowledge
                |
                v
       Regression Testing
                |
                v
         Next Exercise
```

---

# AAR Question Set

A compact facilitator question set is:

```text
OBJECTIVE

What were we trying to validate?


EXPECTATION

What did we expect to happen?


OBSERVATION

What actually happened?


EVIDENCE

What evidence proves that?


DIFFERENCE

Where did observed behavior differ from expectation?


CAUSE

Why did the difference occur?


CONTRIBUTING FACTORS

What else contributed?


STRENGTH

What worked and why?


LESSON

What should we learn from this?


ACTION

What should change?


OWNER

Who is responsible?


VALIDATION

How will we prove the change worked?


SUSTAINABILITY

How will we make sure it keeps working?
```

---

# Reporting Model

A defensible AAR conclusion follows:

```text
Expected
   +
Observed
   +
Evidence
   +
Root Cause
   +
Impact
   +
Action
   +
Retest
```

Example:

> The exercise expected the existing analytic to identify the selected technique. The technique executed successfully and the required telemetry was available in the SIEM, but the analytic did not match because it referenced a legacy field name. Detection Engineering updated the analytic and the original procedure was repeated. The updated detection generated the expected alert and the SOC successfully completed the investigation. The remediation is therefore considered validated for the tested procedure. A regression test will be retained to identify future schema-related failures.

This statement explains both the problem and the evidence supporting closure.

---

# AAR Testing Mindset

Do not think:

```text
Exercise Finished = Work Finished

Finding Documented = Lesson Learned

Configuration Changed = Problem Fixed

Alert Generated = Defence Validated

Meeting Held = Knowledge Transferred

Action Closed = Improvement Sustained
```

Instead think:

```text
What Was Expected?
       |
       v
What Happened?
       |
       v
What Evidence Proves It?
       |
       v
Why Did It Happen?
       |
       v
What Did We Learn?
       |
       v
What Must Change?
       |
       v
Who Owns It?
       |
       v
How Will We Retest It?
       |
       v
Did the Retest Pass?
       |
       v
Can the Improvement Be Reused?
       |
       v
Can We Detect Future Regression?
```

The AAR is complete only when its important lessons have a path from observation to validated improvement.

---

# Related Notes

- [Purple Teaming Overview](index.md)
- [Purple Teaming Methodology](methodology.md)
- [Purple Team Exercises](exercises.md)
- [Detection Engineering](detection-engineering.md)
- [MITRE ATT&CK](mitre-attack.md)
- [Knowledge Transfer](knowledge-transfer.md)
- [Metrics and Measurement](metrics-and-measurement.md)

The next planned Purple Teaming page is:

```text
continuous-validation.md
```

---

# References

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-61 - Incident Response Recommendations and Considerations for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Detection Strategies](https://attack.mitre.org/detectionstrategies/){ target="_blank" rel="noopener noreferrer" }
- [NICE Workforce Framework for Cybersecurity](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center){ target="_blank" rel="noopener noreferrer" }

!!! tip "Review strengths as well as failures"

    Understanding why a control, detection or investigation worked helps the organisation preserve successful behavior and determine whether it will remain effective under future variations.

!!! tip "Separate implementation from validation"

    A configuration change should not automatically close an AAR action. Repeat the relevant test and confirm that the expected outcome now occurs.

!!! tip "Look for systemic causes"

    Repeated telemetry, parsing or detection failures may indicate a broader engineering or change-management problem rather than several unrelated technical findings.

!!! tip "Feed the next exercise"

    Useful AAR findings should influence future scenarios, detection tests, training, engineering priorities and regression testing.

!!! warning "Do not turn the AAR into a blame session"

    Purple teaming depends on participants openly discussing missed alerts, incorrect assumptions and failed controls. Focus on evidence, root causes, ownership and improvement rather than individual blame.
