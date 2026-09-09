---
title: MITRE ATT&CK for Purple Teaming
description: Practical guidance for using MITRE ATT&CK to design threat-informed purple team scenarios, map adversary behaviour, validate telemetry and detections, measure defensive capability and build repeatable security validation.
---

# MITRE ATT&CK for Purple Teaming

MITRE ATT&CK provides a common language for describing adversary behaviour.

Within purple teaming, ATT&CK can help connect:

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
Purple Team Scenario
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
Investigation
        |
        v
Response
        |
        v
Improvement
```

ATT&CK is extremely useful for organising purple team activity, but it should not become the objective of the programme.

The objective is not:

```text
Execute as many ATT&CK techniques as possible.
```

The objective is:

```text
Use relevant adversary behaviours to determine whether
important defensive capabilities work as expected and improve
them when they do not.
```

---

# 1. What Is MITRE ATT&CK?

MITRE ATT&CK is a knowledge base of adversary tactics and techniques based on real-world observations.

ATT&CK can help security teams describe:

```text
Why an adversary performs an action

What behaviour the adversary performs

How the behaviour may be implemented

Which platforms may be affected

How behaviour relates to other adversary activity
```

ATT&CK provides a shared vocabulary that can be used across:

```text
Threat Intelligence

Red Teaming

Purple Teaming

Detection Engineering

SOC Operations

Incident Response

Security Engineering

Security Validation
```

---

# 2. ATT&CK Structure

A simplified ATT&CK hierarchy is:

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

These levels should not be treated as interchangeable.

---

# 3. Tactics

A tactic represents the adversary's tactical objective.

Enterprise ATT&CK includes tactics such as:

```text
Reconnaissance

Resource Development

Initial Access

Execution

Persistence

Privilege Escalation

Defense Evasion

Credential Access

Discovery

Lateral Movement

Collection

Command and Control

Exfiltration

Impact
```

A tactic answers:

```text
Why is the adversary performing this behaviour?
```

For example:

```text
Credential Access
```

describes the adversary objective of obtaining credentials.

It does not describe one specific implementation.

---

# 4. Techniques

A technique describes a way an adversary may achieve a tactical objective.

Example structure:

```text
Tactic:
Execution

Technique:
Command and Scripting Interpreter

Technique ID:
T1059
```

A technique provides a useful abstraction for describing behaviour without depending entirely on one specific offensive tool.

---

# 5. Sub-Techniques

Some ATT&CK techniques contain sub-techniques that describe more specific forms of behaviour.

For example:

```text
T1059
Command and Scripting Interpreter

        |
        +-- T1059.001 PowerShell
        |
        +-- T1059.003 Windows Command Shell
        |
        +-- T1059.004 Unix Shell
        |
        +-- T1059.005 Visual Basic
        |
        +-- T1059.006 Python
        |
        +-- T1059.007 JavaScript/JScript
```

Always verify the current ATT&CK entry before relying on technique or sub-technique mappings because ATT&CK evolves over time.

---

# 6. Procedures

A procedure is a specific implementation of adversary behaviour.

Consider:

```text
T1059.001
PowerShell
```

Many different procedures could implement behaviour associated with that sub-technique.

Therefore:

```text
Technique
   |
   +---- Procedure A
   |
   +---- Procedure B
   |
   +---- Procedure C
```

A detection that identifies Procedure A does not automatically detect every possible implementation associated with the technique.

This distinction is critical during purple team validation.

---

# 7. ATT&CK as a Common Language

Different security teams may initially describe the same activity differently.

For example:

```text
Red Team:
"We executed PowerShell."

SOC:
"We observed powershell.exe."

Detection Engineer:
"We matched a suspicious command-line rule."

Threat Intelligence:
"The behaviour is associated with command and scripting
interpreter activity."
```

ATT&CK provides a shared reference:

```text
T1059.001 - PowerShell
```

This improves communication without replacing the technical detail required by each team.

---

# 8. ATT&CK in Purple Teaming

A useful purple team flow is:

```text
Relevant Threat
      |
      v
Observed Adversary Behaviour
      |
      v
ATT&CK Mapping
      |
      v
Security Objective
      |
      v
Scenario
      |
      v
Representative Procedure
      |
      v
Expected Security Controls
      |
      v
Expected Telemetry
      |
      v
Expected Detection
      |
      v
Exercise
      |
      v
Evidence
      |
      v
Improvement
```

ATT&CK helps organise the behaviour.

It does not replace the security objective or the exercise methodology.

---

# 9. Start With Threat Relevance

Do not begin purple team planning with:

```text
Which ATT&CK technique should we test today?
```

A stronger process begins with:

```text
Which threats matter to us?

Which behaviours do those threats use?

Which assets would those behaviours affect?

Which controls should prevent or detect them?

Which capabilities have not been validated?
```

Then map the selected behaviour to ATT&CK.

---

# 10. Threat-Informed Selection

Potential inputs include:

```text
Threat intelligence

Previous incidents

Red team findings

Penetration test findings

Vulnerability research

Attack-path analysis

SOC observations

Detection gaps

Business risk assessments

Control changes

Architecture changes
```

These inputs can be mapped to ATT&CK to create a consistent threat-informed exercise backlog.

---

# 11. Example Threat-Informed Flow

Suppose threat intelligence indicates that relevant adversaries commonly use PowerShell during post-compromise activity.

The purple team process might be:

```text
Threat Intelligence
       |
       v
PowerShell Behaviour Relevant
       |
       v
ATT&CK T1059.001
       |
       v
Identify Relevant Systems
       |
       v
Identify Expected Telemetry
       |
       v
Identify Existing Detection
       |
       v
Design Safe Scenario
       |
       v
Execute
       |
       v
Validate
```

ATT&CK provides classification.

Threat relevance provides prioritisation.

---

# 12. Business Context

ATT&CK mappings should be connected to business context.

For example:

```text
Technique:
T1059.001

Environment:
Windows administrative workstations

Business Context:
Systems used by privileged administrators

Security Objective:
Determine whether suspicious PowerShell execution involving
privileged identities can be identified and investigated.
```

This provides more value than recording only:

```text
T1059.001 - Tested
```

---

# 13. ATT&CK Mapping Does Not Equal Validation

A technique being listed in a detection platform does not prove that the technique has been validated.

These are different:

```text
Technique Mapped
      |
      v
Detection Exists
      |
      v
Telemetry Exists
      |
      v
Detection Tested
      |
      v
Detection Works
      |
      v
Investigation Works
```

A programme should distinguish these states.

---

# 14. Useful ATT&CK Validation States

A purple team programme may track:

```text
NOT ASSESSED

PLANNED

MAPPED

TESTED

PARTIALLY DETECTED

DETECTED

PREVENTED

VALIDATED

REGRESSION TESTED
```

The organisation should define what each state means.

Avoid using ambiguous labels such as:

```text
Covered
```

without defining the evidence required.

---

# 15. Technique Selection

Prioritise techniques based on factors such as:

| Factor | Question |
|---|---|
| Threat relevance | Do relevant adversaries use this behaviour? |
| Asset relevance | Does it apply to important systems? |
| Exposure | Can the behaviour realistically occur? |
| Impact | What happens if the control fails? |
| Detection uncertainty | Has the capability actually been tested? |
| Historical gaps | Has it failed previously? |
| Change rate | Has the environment recently changed? |
| Learning value | Will testing improve understanding? |

Do not select techniques solely because they are easy to automate.

---

# 16. ATT&CK Technique Record

A useful record may include:

```text
Technique ID:

Technique Name:

Sub-Technique:

Tactic:

Threat Relevance:

Relevant Assets:

Relevant Platforms:

Scenario ID:

Procedure:

Expected Prevention:

Expected Telemetry:

Expected Detection:

Expected Investigation:

Last Tested:

Result:

Evidence:

Owner:
```

This creates traceability between ATT&CK and actual security validation.

---

# 17. ATT&CK Mapping Granularity

Map at the level that accurately represents the behaviour.

Do not use a broad parent technique when a specific sub-technique better describes the scenario.

At the same time, do not force overly specific mappings that the evidence does not support.

The mapping should answer:

```text
What behaviour did the scenario actually represent?
```

---

# 18. Avoid Mapping by Tool Name

Do not assume a tool automatically maps to one ATT&CK technique.

A single tool may perform behaviours associated with many techniques.

Example:

```text
Tool
 |
 +---- Discovery
 |
 +---- Credential Access
 |
 +---- Execution
 |
 +---- Lateral Movement
```

Map the behaviour actually performed by the scenario.

---

# 19. One Scenario Can Map to Multiple Techniques

A scenario may contain multiple adversary behaviours.

Example:

```text
Scenario
   |
   +---- Execution
   |
   +---- Discovery
   |
   +---- Credential Access
   |
   +---- Lateral Movement
```

However, avoid mapping every remotely related technique.

Only map behaviours actually represented by the scenario.

---

# 20. One Technique Can Have Multiple Scenarios

A single ATT&CK technique may require several scenarios.

```text
Technique
   |
   +---- Windows Scenario
   |
   +---- Linux Scenario
   |
   +---- Cloud Scenario
   |
   +---- Procedure Variant
```

This is one reason technique-level coverage percentages can be misleading.

---

# 21. Platform Context

The same technique may behave differently across:

```text
Windows

Linux

macOS

Cloud

Containers

Identity platforms

Network devices

Applications
```

Record environment context with validation results.

For example:

```text
T1059.001

Windows Workstations:
Validated

Windows Servers:
Not Assessed

Privileged Admin Workstations:
Validated

Other Environments:
Not Applicable
```

This is more useful than:

```text
T1059.001:
Covered
```

---

# 22. ATT&CK and Exercise Design

ATT&CK can help structure scenario design.

A scenario may contain:

```text
ATT&CK ID

ATT&CK Name

Tactic

Threat Context

Business Context

Procedure

Expected Prevention

Expected Telemetry

Expected Detection

Expected Investigation

Expected Response
```

See [Purple Team Exercises](exercises.md).

---

# 23. Example Scenario Mapping

```text
Scenario ID:
PT-EXEC-001

Objective:
Validate visibility and detection of selected PowerShell
execution behaviour on the authorised Windows test endpoint.

ATT&CK:
T1059.001 - PowerShell

Tactic:
Execution

Target:
WIN-TEST-01

Expected Telemetry:
Process telemetry
PowerShell telemetry

Expected Detection:
Suspicious PowerShell behaviour detection

Expected Investigation:
Analyst identifies host, account, process and relevant
command context.
```

This connects ATT&CK to an actual defensive objective.

---

# 24. ATT&CK and Procedures

The procedure should represent the behaviour safely and clearly.

A useful model is:

```text
ATT&CK Technique
       |
       v
Representative Procedure
       |
       v
Observable Behaviour
       |
       v
Telemetry
       |
       v
Detection
```

The procedure should not be selected merely because a public tool provides it.

---

# 25. Safe Representative Procedures

Purple team testing often does not require reproducing every harmful effect associated with real adversary activity.

A representative procedure may be designed to generate:

```text
Equivalent process behaviour

Equivalent authentication behaviour

Equivalent file activity

Equivalent network behaviour

Equivalent cloud control-plane activity
```

while avoiding unnecessary operational impact.

The test must still accurately exercise the security capability being validated.

---

# 26. ATT&CK and Telemetry

An ATT&CK mapping becomes much more useful when connected to expected telemetry.

For each scenario ask:

```text
Which event should exist?

Which system generates it?

Which sensor collects it?

Where is it stored?

Which fields matter?

Which detection consumes it?
```

This creates:

```text
Technique
    |
    v
Behaviour
    |
    v
Data
    |
    v
Detection
```

---

# 27. Telemetry Dependency Map

Example:

```text
T1059.001
PowerShell
     |
     v
Process Execution
     |
     +---- Endpoint Process Telemetry
     |
     +---- PowerShell Logging
     |
     +---- EDR Telemetry
     |
     v
Collection Pipeline
     |
     v
SIEM
     |
     v
Detection
```

The exact telemetry depends on the environment and detection objective.

---

# 28. Validate Telemetry Before Detection

When a detection fails:

```text
Detection Failed
      |
      v
Was Behaviour Executed?
      |
      v
Was Telemetry Generated?
      |
      v
Was Telemetry Collected?
      |
      v
Was It Parsed Correctly?
      |
      v
Was Detection Logic Correct?
```

Do not assume the rule itself is the first failure.

---

# 29. ATT&CK and Detection Engineering

ATT&CK can help organise detection engineering around behaviours.

A useful flow is:

```text
ATT&CK Behaviour
       |
       v
Detection Hypothesis
       |
       v
Required Telemetry
       |
       v
Available Telemetry
       |
       v
Detection Logic
       |
       v
Purple Team Test
       |
       v
Tune
       |
       v
Retest
```

See [Detection Engineering](detection-engineering.md).

---

# 30. Detection Hypothesis

Instead of beginning with a query, begin with a hypothesis.

Example:

```text
If suspicious PowerShell execution occurs on a monitored
endpoint, endpoint telemetry should contain process and
PowerShell activity that allows the behaviour to be
distinguished from expected administrative activity.
```

Then determine:

```text
Required Data

Available Data

Detection Logic

Expected Context

Test Procedure
```

---

# 31. Detection Coverage Is Not Binary

A detection may cover:

```text
One procedure

Several procedures

One platform

Several platforms

One command pattern

One behaviour variant
```

Therefore:

```text
Detected Technique = Yes
```

may hide important limitations.

Prefer documenting detection depth.

---

# 32. Detection Depth

Example:

```text
Technique:
T1059.001

Procedure A:
Detected

Procedure B:
Detected

Procedure C:
Not Detected

Windows 11:
Validated

Windows Server:
Not Tested

Detection Context:
Good

False Positive Rate:
Requires further assessment
```

This communicates much more than a single coverage marker.

---

# 33. Detection Robustness

After validating the initial procedure, test controlled variations.

```text
Procedure A
    |
    v
Detected
    |
    v
Variation B
    |
    v
Detected?
    |
    v
Variation C
    |
    v
Detected?
```

The goal is to understand the detection boundary.

---

# 34. Detection Boundary

A useful conclusion may be:

```text
The detection reliably identified the tested PowerShell
execution variants where process command-line telemetry was
available, but did not detect the tested variation when the
required command-line field was absent.
```

This is more defensible than:

```text
PowerShell is detected.
```

---

# 35. ATT&CK and Prevention

ATT&CK can also organise prevention validation.

For each technique ask:

```text
Should this behaviour be prevented?

Which control should prevent it?

Under which conditions?

On which assets?

What happens if prevention fails?
```

Example:

```text
Technique:
Selected execution technique

Expected Control:
Application control

Expected Result:
Execution blocked on managed workstation

Observed:
Blocked

Result:
Prevention validated for tested scenario
```

Do not generalise beyond the tested conditions.

---

# 36. Prevention Versus Detection

Different scenarios may expect different security outcomes.

```text
Scenario A:
Prevention expected

Scenario B:
Execution allowed but detection expected

Scenario C:
Prevention and detection both expected
```

Document the expected outcome before execution.

---

# 37. ATT&CK and Investigation

Detection is not the end of the defensive chain.

For each relevant technique, determine whether analysts can answer:

```text
What happened?

Which system was affected?

Which account was involved?

What occurred before?

What occurred afterwards?

What related behaviours occurred?

Does the activity require escalation?
```

A technically correct alert may still provide insufficient investigation context.

---

# 38. ATT&CK and Response

Where response is in scope, connect ATT&CK behaviours to response decisions.

Examples:

```text
Credential Access
       |
       v
Credential Compromise Suspected
       |
       v
Identity Investigation
       |
       v
Credential Reset / Session Revocation
```

or:

```text
Lateral Movement
       |
       v
Compromised Host Identified
       |
       v
Containment Decision
```

Only execute response actions that are authorised for the exercise.

---

# 39. ATT&CK and Threat Intelligence

Threat intelligence can provide prioritisation context.

A useful flow is:

```text
Threat Actor / Campaign
        |
        v
Observed Behaviours
        |
        v
ATT&CK Mapping
        |
        v
Relevant Techniques
        |
        v
Organisation Exposure
        |
        v
Purple Team Priority
```

The presence of a technique in ATT&CK alone does not make it a priority.

---

# 40. Threat Profile

A simple threat profile may include:

```text
Threat:

Motivation:

Targeted Assets:

Relevant Platforms:

Observed ATT&CK Techniques:

Organisation Exposure:

Existing Controls:

Validation Status:

Priority:
```

This creates traceability from threat intelligence to exercise selection.

---

# 41. ATT&CK and Adversary Emulation

ATT&CK can help build adversary emulation plans.

Example:

```text
Threat Profile
      |
      v
Relevant ATT&CK Behaviours
      |
      v
Ordered Scenario
      |
      v
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

Not every purple team exercise needs to emulate an entire adversary lifecycle.

Focused technique validation may be more appropriate for specific objectives.

---

# 42. Atomic Versus Chained Testing

## Atomic Testing

Tests one behaviour independently.

```text
Technique
   |
   v
Procedure
   |
   v
Telemetry
   |
   v
Detection
```

Advantages:

```text
Easy troubleshooting

Repeatability

Clear root cause

Fast retesting
```

## Chained Testing

Combines several behaviours.

```text
Technique A
    |
    v
Technique B
    |
    v
Technique C
```

Advantages:

```text
Context

Sequence validation

Cross-control validation

Investigation realism
```

Both models are useful.

---

# 43. Atomic Tests Before Complex Chains

A practical progression is:

```text
Atomic Validation
       |
       v
Technique Works?
       |
       v
Telemetry Works?
       |
       v
Detection Works?
       |
       v
Combine Into Chain
       |
       v
Validate Sequence
```

This makes failures in complex scenarios easier to diagnose.

---

# 44. Atomic Red Team

Atomic Red Team provides small tests mapped to ATT&CK techniques.

It can be useful for:

```text
Generating representative behaviour

Validating telemetry

Testing detections

Creating repeatable scenarios

Regression testing
```

However, a public test definition should never be executed automatically without reviewing:

```text
Prerequisites

Commands

Cleanup

Target impact

Privileges

Network activity

Artifacts

Environment suitability
```

The organisation's Rules of Engagement remain authoritative.

---

# 45. MITRE CALDERA

MITRE CALDERA is an adversary emulation platform that can help automate and orchestrate authorised security testing.

Potential purple team uses include:

```text
Procedure orchestration

Scenario sequencing

Repeatability

Adversary emulation

Security validation
```

CALDERA can support the methodology.

It does not replace:

```text
Threat prioritisation

Safety review

Detection analysis

Root cause analysis

Knowledge transfer

Retesting
```

---

# 46. ATT&CK Navigator

ATT&CK Navigator can help visualise ATT&CK information.

Possible purple team uses include:

```text
Threat profiles

Exercise planning

Technique prioritisation

Validation status

Detection status

Gap visualisation

Retest planning
```

Use visualisations carefully.

A coloured ATT&CK matrix is a summary, not proof of security effectiveness.

---

# 47. Example Navigator Status Model

An organisation might use a defined internal status model such as:

```text
Grey:
Not assessed

Blue:
Planned

Yellow:
Tested with gap

Green:
Validated

Orange:
Retest required
```

The colours are less important than the definitions.

Every status should trace back to evidence.

---

# 48. ATT&CK Coverage

The term "ATT&CK coverage" can mean many different things.

Possible meanings include:

```text
Technique has a detection rule

Technique has telemetry

Technique has been tested

Technique has been prevented

Technique has been detected

Technique has been investigated

Technique has a validated response
```

Never report "coverage" without defining what it means.

---

# 49. Coverage Layers

A better model is:

```text
Technique
   |
   +---- Threat Relevant?
   |
   +---- Applicable?
   |
   +---- Telemetry Available?
   |
   +---- Prevention Exists?
   |
   +---- Detection Exists?
   |
   +---- Detection Tested?
   |
   +---- Investigation Tested?
   |
   +---- Response Tested?
   |
   +---- Regression Tested?
```

This creates multidimensional coverage.

---

# 50. Example Coverage Record

| Capability | Status |
|---|---|
| Threat relevant | Yes |
| Applicable | Yes |
| Telemetry identified | Yes |
| Telemetry validated | Yes |
| Prevention expected | No |
| Detection exists | Yes |
| Detection tested | Yes |
| Detection successful | Partial |
| Investigation tested | Yes |
| Response tested | No |
| Regression test | Planned |

This is more informative than a single green square.

---

# 51. Coverage Denominator

If calculating coverage percentages, define the denominator.

For example:

```text
Validated Detection Coverage =
Threat-Relevant Applicable Techniques With Validated Detection
/
Threat-Relevant Applicable Techniques Selected for Validation
```

This is different from:

```text
Validated Techniques
/
Every Technique in Enterprise ATT&CK
```

The first may support a meaningful programme question.

The second may produce a misleading vanity metric.

---

# 52. Risk-Weighted Coverage

Not all techniques have equal relevance.

A programme may assign priority based on:

```text
Threat relevance

Asset criticality

Likelihood

Exposure

Impact

Historical failures
```

Then focus validation effort on the highest-value behaviours.

This is usually more useful than trying to make the entire matrix green.

---

# 53. ATT&CK Coverage Depth

Coverage should also consider depth.

Example:

```text
Technique A:
1 procedure tested

Technique B:
4 procedures tested across 3 endpoint classes

Technique C:
2 procedures tested plus SOC investigation

Technique D:
Prevention, detection, investigation and response validated
```

All four could otherwise appear as:

```text
Tested
```

despite very different evidence.

---

# 54. ATT&CK Coverage Quality

A useful maturity model is:

```text
Mapped
  |
  v
Telemetry Identified
  |
  v
Detection Exists
  |
  v
Tested
  |
  v
Validated
  |
  v
Variants Tested
  |
  v
Investigation Validated
  |
  v
Response Validated
  |
  v
Regression Tested
```

Higher levels require stronger evidence.

---

# 55. Technique Status Should Expire

A validation result should not remain green forever.

Changes may invalidate previous evidence.

Examples:

```text
EDR upgrade

SIEM migration

Parser change

Detection rule update

Operating system upgrade

Identity architecture change

Cloud configuration change

Network architecture change
```

Record:

```text
Last Validated

Validation Version

Environment

Next Review
```

---

# 56. Change-Triggered ATT&CK Validation

Relevant scenarios can be rerun after changes.

Example:

```text
Detection Rule Change
        |
        v
Identify ATT&CK Mapping
        |
        v
Identify Associated Tests
        |
        v
Execute Tests
        |
        v
Validate Result
```

This connects ATT&CK mapping with continuous validation.

---

# 57. ATT&CK and Regression Testing

Previously successful ATT&CK-mapped scenarios can become regression tests.

```text
Technique
    |
    v
Validated Scenario
    |
    v
Stored Test Case
    |
    v
Environment Changes
    |
    v
Execute Again
    |
    v
Still Validated?
```

See [Continuous Validation](continuous-validation.md).

---

# 58. ATT&CK and Knowledge Transfer

ATT&CK can help participants communicate using consistent terminology.

Example:

```text
Red:
Explains procedure.

Blue:
Explains observed telemetry.

Detection Engineer:
Explains detection.

Threat Intelligence:
Explains adversary relevance.

ATT&CK:
Provides common behavioural reference.
```

ATT&CK should support knowledge transfer rather than replace technical explanation.

See [Knowledge Transfer](knowledge-transfer.md).

---

# 59. ATT&CK and After-Action Review

ATT&CK mappings can help organise AAR observations.

Example:

```text
Scenario:
PT-004

ATT&CK:
T1059.001

Expected:
Detection

Observed:
Telemetry available but detection failed

Root Cause:
Detection depended on obsolete schema

Action:
Update rule and create regression test
```

See [After-Action Review](after-action-review.md).

---

# 60. ATT&CK and Metrics

Useful ATT&CK-related metrics may include:

```text
Threat-relevant techniques selected

Applicable techniques validated

Validation success rate

Telemetry validation rate

Detection validation rate

Techniques requiring retest

Techniques with repeated failures

Average validation age
```

Avoid metrics that reward quantity without quality.

See [Metrics and Measurement](metrics-and-measurement.md).

---

# 61. Technique Validation Age

Track when a capability was last validated.

Example:

| Technique | Environment | Last Validated | Status |
|---|---|---|---|
| T1059.001 | Windows endpoints | 2026-09-01 | Validated |
| T1021 | Server environment | 2026-04-12 | Review |
| T1003 | Test environment | 2025-12-15 | Retest required |

The appropriate validation interval depends on risk and environmental change.

---

# 62. ATT&CK Version Awareness

ATT&CK evolves.

Techniques may be:

```text
Added

Modified

Renamed

Reorganised

Deprecated

Revoked
```

Record ATT&CK mappings in a maintainable way.

Do not assume an old technique name or structure remains current indefinitely.

---

# 63. Mapping Review

Review mappings when:

```text
ATT&CK changes

Scenario changes

Procedure changes

Threat intelligence changes

Detection objective changes

Environment changes
```

The mapping should describe the current scenario accurately.

---

# 64. Deprecated Techniques

If ATT&CK deprecates or changes a technique:

```text
Review Scenario
      |
      v
Review Current ATT&CK
      |
      v
Update Mapping
      |
      v
Preserve Historical Context
```

Do not delete historical evidence merely because the taxonomy changed.

---

# 65. ATT&CK Is Not a Vulnerability Database

ATT&CK describes adversary behaviour.

It is not primarily a catalogue of:

```text
CVEs

Software vulnerabilities

Configuration weaknesses

Security findings
```

A vulnerability may enable a behaviour, but the concepts are different.

Example:

```text
Vulnerability
     |
     v
Exploitation
     |
     v
Adversary Behaviour
     |
     v
ATT&CK Mapping
```

---

# 66. ATT&CK Is Not a Control Framework

ATT&CK does not by itself define an organisation's complete security-control programme.

It can inform:

```text
Detection

Testing

Threat modelling

Adversary emulation

Security validation
```

but it should be combined with:

```text
Risk management

Security architecture

Control frameworks

Incident response

Governance
```

where appropriate.

---

# 67. ATT&CK Is Not a Checklist

Avoid:

```text
Technique 1 - Done
Technique 2 - Done
Technique 3 - Done
```

Security behaviour is not permanently "done".

A better model is:

```text
Relevant?
   |
   v
Applicable?
   |
   v
Validated?
   |
   v
Evidence?
   |
   v
Last Tested?
   |
   v
Retest Required?
```

---

# 68. ATT&CK Is Not a Score

Avoid statements such as:

```text
We detect 90% of ATT&CK.
```

unless the organisation can precisely explain:

```text
Which ATT&CK domain?

Which version?

Which techniques?

Which sub-techniques?

Which environments?

Which procedures?

Which telemetry?

Which detection criteria?

Which evidence?

Which validation date?
```

Without this context, the percentage may be misleading.

---

# 69. Avoid False Precision

A dashboard showing:

```text
82.7% ATT&CK coverage
```

may look precise while hiding uncertainty.

Questions to ask:

```text
What is the denominator?

What qualifies as covered?

Was it tested?

How recently?

Which environments?

How many procedures?

Was detection or only telemetry validated?
```

Precision in the number does not guarantee precision in the underlying evidence.

---

# 70. Avoid Green Matrix Syndrome

A common programme failure is attempting to make every ATT&CK cell green.

This can incentivise:

```text
Weak mappings

Untested detections

Irrelevant techniques

Duplicate controls

Shallow validation
```

A smaller set of high-priority behaviours with strong evidence may provide more defensive value.

---

# 71. Avoid Procedure Overfitting

Suppose a detection identifies:

```text
Exact Tool Name

Exact Command

Exact Filename
```

and the test passes.

That does not necessarily demonstrate behavioural detection.

Test controlled variations.

Ask:

```text
What stable signal does the detection rely on?

Would a different implementation still produce it?

Which variations are expected to remain detectable?
```

---

# 72. Avoid ATT&CK Mapping Inflation

Do not map a scenario to every possible related technique.

Weak:

```text
One simple scenario
    |
    +---- 12 ATT&CK techniques
```

Better:

```text
Scenario
    |
    +---- Techniques actually represented by observed behaviour
```

Mappings should be defensible.

---

# 73. Avoid Unverified Mapping

Before publishing or reporting a mapping:

```text
Check current ATT&CK entry

Read technique description

Review sub-techniques

Compare actual behaviour

Document mapping rationale
```

Do not map based solely on technique name similarity.

---

# 74. ATT&CK Mapping Rationale

For important scenarios, document why the mapping applies.

Example:

```text
Mapping:
T1059.001 - PowerShell

Rationale:
The scenario intentionally executed PowerShell as the command
and scripting interpreter on the authorised Windows endpoint.

Evidence:
Process telemetry and PowerShell telemetry confirmed the
behaviour.
```

This makes mappings auditable.

---

# 75. Mapping Confidence

Where useful, record confidence:

```text
High

Medium

Low
```

Example:

```text
Mapping:
Txxxx

Confidence:
High

Reason:
Observed behaviour directly matches the technique description.
```

Low-confidence mappings should be reviewed rather than silently treated as authoritative.

---

# 76. Data and Detection Traceability

A mature record connects:

```text
Threat
   |
   v
ATT&CK Technique
   |
   v
Scenario
   |
   v
Procedure
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
Evidence
   |
   v
Improvement
```

This traceability allows teams to answer:

```text
Why does this detection exist?

Which threat does it address?

Which scenario validates it?

When was it last tested?

What evidence supports the result?
```

---

# 77. Detection Catalogue Integration

A detection catalogue may include:

```text
Detection ID

Detection Name

ATT&CK Mapping

Data Sources

Required Fields

Platforms

Scenario IDs

Owner

Status

Last Tested

Known Limitations
```

Example:

```text
Detection ID:
DET-WIN-014

ATT&CK:
T1059.001

Scenario:
PT-EXEC-001

Required Data:
Endpoint process telemetry
PowerShell telemetry

Status:
Validated

Last Tested:
2026-09-09
```

---

# 78. Scenario Catalogue Integration

A scenario catalogue may include:

| Scenario | ATT&CK | Platform | Objective | Last Result |
|---|---|---|---|---|
| PT-001 | T1059.001 | Windows | Execution visibility | Pass |
| PT-002 | T1021 | Windows | Lateral movement detection | Partial |
| PT-003 | Selected technique | Cloud | Identity validation | Retest |

This helps connect ATT&CK to actual testing rather than theoretical mappings.

---

# 79. Evidence Integration

Each validated mapping should ideally trace to evidence.

Example:

```text
Technique:
T1059.001

Scenario:
PT-EXEC-001

Evidence:
evidence/PT-EXEC-001/

Execution:
Confirmed

Telemetry:
Confirmed

Detection:
Confirmed

Investigation:
Confirmed

Validation Date:
2026-09-09
```

The evidence repository may be restricted depending on sensitivity.

---

# 80. ATT&CK and Detection-as-Code

Where detections are maintained as code, ATT&CK metadata can be included with the detection.

Illustrative example:

```yaml
id: DET-WIN-014
name: Suspicious PowerShell Behaviour

attack:
  technique:
    - T1059.001

platform:
  - windows

required_data:
  - endpoint_process
  - powershell

validation:
  scenario:
    - PT-EXEC-001
```

This is an illustrative schema rather than a universal standard.

---

# 81. ATT&CK and Test-as-Code

Purple team scenarios can also be maintained in version control.

Illustrative structure:

```text
purple-tests/
├── endpoint/
│   ├── PT-EXEC-001/
│   │   ├── scenario.yml
│   │   ├── expected.yml
│   │   └── cleanup.md
│   └── PT-DISC-001/
├── identity/
├── network/
└── cloud/
```

This can improve:

```text
Versioning

Peer review

Repeatability

Change tracking

Regression testing
```

---

# 82. Example Test Metadata

```yaml
scenario_id: PT-EXEC-001
version: 1.2

attack:
  technique: T1059.001
  name: PowerShell

platform:
  - windows

objective: >
  Validate visibility and detection of the selected
  PowerShell execution behaviour.

expected:
  telemetry: true
  detection: true
  investigation: true

owner: detection-engineering

last_validated: 2026-09-09
```

Keep metadata synchronised with the actual test implementation.

---

# 83. ATT&CK and CI/CD

Where appropriate, controlled ATT&CK-mapped validation can be integrated into security engineering workflows.

Example:

```text
Detection Rule Change
       |
       v
Pull Request
       |
       v
Peer Review
       |
       v
Safe Test Environment
       |
       v
Relevant Purple Tests
       |
       v
Assertions
       |
       v
Result
```

Do not execute attack simulations automatically against production simply because they are integrated into CI/CD.

---

# 84. Detection Change Example

Suppose:

```text
DET-WIN-014
```

maps to:

```text
T1059.001
```

and is validated by:

```text
PT-EXEC-001
PT-EXEC-002
```

A detection-rule change could trigger those representative tests in an authorised validation environment.

This provides stronger assurance than syntax checking alone.

---

# 85. ATT&CK and Continuous Validation

ATT&CK metadata can help determine which regression tests are affected by changes.

```text
Control Change
      |
      v
Affected Detections
      |
      v
ATT&CK Mapping
      |
      v
Associated Scenarios
      |
      v
Execute
      |
      v
Validate
```

See [Continuous Validation](continuous-validation.md).

---

# 86. Practical ATT&CK Workflow

A complete workflow can be:

```text
1. Identify relevant threat.

2. Identify relevant adversary behaviour.

3. Verify current ATT&CK mapping.

4. Determine business and platform relevance.

5. Define security objective.

6. Identify expected prevention.

7. Identify required telemetry.

8. Identify existing detections.

9. Create representative safe procedure.

10. Establish baseline.

11. Execute procedure.

12. Confirm behaviour occurred.

13. Validate prevention.

14. Validate telemetry generation.

15. Validate collection and parsing.

16. Validate detection.

17. Validate alert routing.

18. Validate investigation.

19. Validate response where applicable.

20. Identify gaps.

21. Determine root cause.

22. Improve.

23. Retest.

24. Record evidence.

25. Update ATT&CK status.

26. Consider regression testing.
```

---

# 87. Practical Example - PowerShell

Consider an authorised exercise involving:

```text
T1059.001 - PowerShell
```

The objective is not:

```text
Can we run PowerShell?
```

The objective is:

```text
Determine whether the selected PowerShell behaviour on the
authorised Windows endpoint produces sufficient telemetry for
the expected detection and SOC investigation.
```

---

## Threat Context

The organisation has determined that command and scripting interpreter activity is relevant to its threat model.

ATT&CK provides a common mapping:

```text
Technique:
T1059

Sub-Technique:
T1059.001

Name:
PowerShell
```

---

## Scope

```text
Environment:
Authorised test environment

Target:
WIN-TEST-01

Account:
purple-test-user

Destructive Actions:
Prohibited

Persistence:
Prohibited

Scope Expansion:
Prohibited
```

---

## Expected Defensive Chain

```text
PowerShell Activity
        |
        v
Endpoint Telemetry
        |
        v
PowerShell Telemetry
        |
        v
EDR / Collector
        |
        v
SIEM
        |
        v
Detection
        |
        v
SOC Alert
        |
        v
Investigation
```

---

## Baseline

Before execution:

```text
Endpoint Sensor:
Healthy

PowerShell Logging:
Configured as required by the scenario

SIEM Ingestion:
Healthy

Detection Rule:
Enabled

Alert Queue:
Available

Clock:
Synchronised
```

---

## Execution

The approved representative procedure is executed.

Record:

```text
Scenario:
PT-EXEC-001

Technique:
T1059.001

Execution Time:
14:05:22

Target:
WIN-TEST-01

Account:
purple-test-user
```

The intended behaviour occurs.

Result:

```text
Execution:
PASS
```

---

## Telemetry

Endpoint telemetry is generated.

Observed fields include:

```text
Host

User

Process

Parent Process

Command Line

Timestamp
```

Result:

```text
Telemetry Generation:
PASS
```

---

## Collection

The event reaches the SIEM.

Result:

```text
Collection:
PASS
```

---

## Detection

The expected detection fires.

Result:

```text
Detection:
PASS
```

But the exercise does not stop here.

---

## Alert Quality

The team examines the alert.

Observed:

```text
Hostname:
Present

Username:
Present

Process:
Present

Parent Process:
Present

Command Context:
Present

Related Events:
Queryable
```

Result:

```text
Alert Context:
PASS
```

---

## Investigation

The analyst is asked to identify:

```text
Affected host

Executing identity

Process

Parent process

Relevant command context

Related activity
```

The analyst successfully retrieves the information.

Result:

```text
Investigation:
PASS
```

---

## Variation

A second authorised procedure representing the same sub-technique is executed.

Observed:

```text
Telemetry:
PASS

Detection:
FAIL
```

This changes the conclusion.

The organisation should not report:

```text
T1059.001 fully covered.
```

A more accurate conclusion is:

```text
The detection successfully identified the initial tested
PowerShell procedure but did not identify the second tested
variation. Additional detection engineering and validation
are required before broader coverage can be claimed.
```

---

## Improvement

The detection engineer identifies that the rule relied on an overly specific command pattern.

The rule is redesigned around more durable behavioural signals.

---

## Retest

Both procedures are repeated.

```text
Procedure A:
Detected

Procedure B:
Detected
```

A third controlled variation is then tested.

```text
Procedure C:
Detected
```

The result now provides stronger evidence of detection robustness.

It still does not prove universal coverage of every possible PowerShell behaviour.

---

# 88. Practical Example - Lateral Movement

Suppose a relevant scenario maps to a lateral movement technique.

The purple team should not simply record:

```text
Lateral Movement:
Detected
```

Instead evaluate:

```text
Was authentication visible?

Was source host visible?

Was destination host visible?

Was account visible?

Was remote execution visible?

Did the detection correlate the activity?

Could the analyst identify the movement path?

Could the affected systems be identified?
```

This tests the defensive capability behind the ATT&CK mapping.

---

# 89. Practical Example - Cloud

ATT&CK can also help organise cloud-focused purple testing.

Example model:

```text
Cloud Identity Behaviour
       |
       v
ATT&CK Mapping
       |
       v
Cloud Audit Event
       |
       v
Collection
       |
       v
SIEM
       |
       v
Detection
       |
       v
Cloud Investigation
```

Important context includes:

```text
Cloud provider

Tenant / organisation

Account / subscription / project

Identity

Role

Region where relevant

Control-plane service

Audit-log source
```

---

# 90. Practical Example - Identity

Identity-focused ATT&CK validation may examine:

```text
Authentication Behaviour

Privilege Assignment

Credential Use

Service Accounts

Administrative Roles

Remote Authentication
```

Distinguish:

```text
Authentication occurred

Authentication succeeded

Authorisation succeeded

Privilege was obtained

Detection occurred

Investigation succeeded
```

These are separate observations.

---

# 91. Failure Triage

When an ATT&CK-mapped test does not produce the expected result:

```text
Was the intended ATT&CK behaviour generated?
              |
            No
              |
              v
        Test / Mapping Issue

             Yes
              |
              v
       Prevention Expected?
              |
              v
       Telemetry Generated?
          /          \
        No            Yes
        |              |
        v              v
 Logging/Sensor    Collected?
      Gap          /       \
                  No       Yes
                  |         |
                  v         v
             Pipeline     Parsed?
               Gap       /      \
                        No       Yes
                        |         |
                        v         v
                    Schema     Detection?
                      Gap      /       \
                              No       Yes
                              |         |
                              v         v
                         Detection    Alert
                            Gap       Routing?
```

This prevents ATT&CK status from hiding the actual failure.

---

# 92. Mapping Failure Versus Security Failure

Sometimes the ATT&CK mapping itself is wrong.

Example:

```text
Scenario executed successfully.

Telemetry exists.

Detection works.

But the scenario was mapped to the wrong ATT&CK technique.
```

This is:

```text
Mapping Quality Failure
```

not:

```text
Security Control Failure
```

Keep taxonomy and security outcomes separate.

---

# 93. ATT&CK Validation Record

A complete record might look like:

```text
ATT&CK VALIDATION RECORD

Technique ID:
T1059.001

Technique:
PowerShell

Tactic:
Execution

Threat Relevant:
Yes

Platform:
Windows

Environment:
Authorised test environment

Scenario:
PT-EXEC-001

Procedure Version:
1.2

Expected Prevention:
No

Expected Telemetry:
Yes

Expected Detection:
Yes

Expected Investigation:
Yes

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

Investigation:
PASS

Response:
NOT TESTED

Variations Tested:
3

Known Limitations:
Not validated against all PowerShell execution patterns.

Last Validated:
2026-09-09

Owner:
Detection Engineering

Evidence:
Restricted exercise evidence repository
```

---

# 94. ATT&CK Validation Matrix

A programme-level matrix may contain:

| ATT&CK | Threat Relevant | Telemetry | Detection | Investigation | Last Tested |
|---|---:|---:|---:|---:|---|
| T1059.001 | Yes | Validated | Validated | Validated | 2026-09-09 |
| T1021 | Yes | Validated | Partial | Tested | 2026-08-20 |
| T1003 | Yes | Planned | Planned | Not Tested | - |

The table should link to detailed evidence internally where possible.

---

# 95. Programme Questions

ATT&CK should help the programme answer questions such as:

```text
Which relevant adversary behaviours have we validated?

Which relevant behaviours lack telemetry?

Which behaviours have detections but no test evidence?

Which detections repeatedly fail?

Which techniques depend on fragile telemetry?

Which behaviours have not been tested recently?

Which environments have weak validation?

Which scenarios should become regression tests?

Which gaps matter most to business risk?
```

These questions are more useful than:

```text
What percentage of ATT&CK are we green?
```

---

# 96. ATT&CK Validation Checklist

## Selection

- [ ] Threat relevance established
- [ ] Business relevance established
- [ ] Platform applicability confirmed
- [ ] Current ATT&CK entry reviewed
- [ ] Technique mapping verified
- [ ] Sub-technique mapping reviewed
- [ ] Mapping rationale documented

## Scenario

- [ ] Scenario ID assigned
- [ ] Security objective defined
- [ ] Representative procedure selected
- [ ] Scope documented
- [ ] Preconditions documented
- [ ] Safety controls documented
- [ ] Cleanup documented

## Defensive Mapping

- [ ] Expected prevention identified
- [ ] Expected telemetry identified
- [ ] Collection path identified
- [ ] Required fields identified
- [ ] Detection identified
- [ ] Alert route identified
- [ ] Investigation objective defined
- [ ] Response objective defined where applicable

## Execution

- [ ] Baseline validated
- [ ] Time synchronised
- [ ] Test executed
- [ ] Intended behaviour confirmed
- [ ] Evidence captured

## Validation

- [ ] Prevention evaluated
- [ ] Telemetry generation evaluated
- [ ] Collection evaluated
- [ ] Parsing evaluated
- [ ] Detection evaluated
- [ ] Alert routing evaluated
- [ ] Investigation evaluated
- [ ] Response evaluated where applicable

## Improvement

- [ ] Gaps categorised
- [ ] Root cause identified
- [ ] Action assigned
- [ ] Improvement implemented
- [ ] Original test repeated
- [ ] Relevant variations tested
- [ ] Result documented

## Maintenance

- [ ] Last validation date recorded
- [ ] ATT&CK version changes considered
- [ ] Scenario owner assigned
- [ ] Retest criteria defined
- [ ] Regression-test suitability reviewed

---

# 97. ATT&CK Mapping Checklist

Before assigning a mapping:

```text
Does the behaviour actually match the technique description?

Is a sub-technique more accurate?

Did the behaviour really occur?

Is the mapping based on behaviour rather than tool name?

Can the mapping be supported with evidence?

Has the current ATT&CK entry been reviewed?
```

If the answer to these questions is unclear, review the mapping.

---

# 98. ATT&CK Coverage Checklist

Before claiming coverage:

```text
What does coverage mean?

What is the denominator?

Which environment was tested?

Which procedures were tested?

Was telemetry validated?

Was detection validated?

Was investigation validated?

Were variations tested?

When was it last validated?

What limitations remain?
```

If these questions cannot be answered, the coverage claim probably needs more context.

---

# 99. Recommended ATT&CK Mindset

Do not think:

```text
ATT&CK = Checklist

Green Cell = Secure

Detection Rule = Coverage

One Procedure = Technique Coverage

Tool = Technique

Mapped = Validated

High Percentage = High Maturity
```

Think:

```text
Threat
   |
   v
Relevant Behaviour
   |
   v
ATT&CK Classification
   |
   v
Security Objective
   |
   v
Representative Scenario
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
Evidence
   |
   v
Improvement
   |
   v
Retest
```

---

# 100. Final ATT&CK Purple Team Model

A mature ATT&CK-driven purple team programme should connect:

```text
THREAT INTELLIGENCE
        |
        v
BUSINESS RISK
        |
        v
ADVERSARY BEHAVIOUR
        |
        v
MITRE ATT&CK
        |
        v
PRIORITISATION
        |
        v
PURPLE TEAM SCENARIO
        |
        v
REPRESENTATIVE PROCEDURE
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
EVIDENCE
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
VALIDATION
        |
        v
REGRESSION TESTING
        |
        v
CONTINUOUS VALIDATION
```

ATT&CK provides the behavioural language that connects many of these activities.

It should help the organisation answer:

```text
Which adversary behaviours matter?

Which of those behaviours can we observe?

Which can we prevent?

Which can we detect?

Which can we investigate?

Which can we respond to?

Which have actually been tested?

Which have failed?

Which have been improved?

Which improvements remain effective?
```

That is far more valuable than simply colouring an ATT&CK matrix.

---

# Related Notes

- [Purple Teaming](index.md)
- [Purple Teaming Methodology](methodology.md)
- [Purple Team Exercises](exercises.md)
- [Detection Engineering](detection-engineering.md)
- [Knowledge Transfer](knowledge-transfer.md)
- [Metrics and Measurement](metrics-and-measurement.md)
- [After-Action Review](after-action-review.md)
- [Continuous Validation](continuous-validation.md)
- [Red Teaming](../red-teaming/index.md)

---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Enterprise ATT&CK](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [ATT&CK Techniques](https://attack.mitre.org/techniques/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [ATT&CK Tactics](https://attack.mitre.org/tactics/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [ATT&CK Data Sources](https://attack.mitre.org/datasources/){ target="_blank" rel="noopener noreferrer" }
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }

!!! tip "Start with the threat, not the matrix"

    Determine which adversary behaviours matter to the organisation and then use ATT&CK to describe and organise those behaviours.

!!! tip "Map behaviour, not tools"

    A tool can implement many behaviours and a technique can be implemented by many tools. Base ATT&CK mappings on what actually occurred during the scenario.

!!! tip "Connect ATT&CK to evidence"

    A useful ATT&CK mapping should trace to a scenario, expected telemetry, detection, validation result, evidence and validation date.

!!! tip "Measure depth as well as breadth"

    One tested procedure does not demonstrate universal coverage of a technique. Record platforms, procedures, variations, defensive layers and known limitations.

!!! warning "ATT&CK is not a security score"

    A high percentage of coloured ATT&CK cells does not demonstrate effective security unless the organisation defines what the colours mean and can support them with relevant validation evidence.

!!! warning "Verify current ATT&CK mappings"

    ATT&CK evolves over time. Review the current MITRE ATT&CK knowledge base before relying on technique names, identifiers, sub-techniques or mappings in assessments and exercise plans.
