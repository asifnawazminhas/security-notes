---
title: Red Team Social Engineering
description: Social engineering methodology for authorised red team assessments, covering engagement planning, pretexting, identity verification, phone and physical scenarios, information elicitation, help desk testing, synthetic data, detection validation, safety, evidence, cleanup and reporting.
---

# Red Team Social Engineering

Social engineering tests whether an attacker can influence people or abuse organisational processes to gain access, obtain information or advance an attack path.

Technical security controls may be strong while human and procedural controls remain vulnerable.

Examples include:

```text
Help desk verification

Telephone requests

Impersonation scenarios

Physical access requests

Information elicitation

Account recovery

Password reset processes

MFA recovery

Visitor procedures

Third-party verification

Business process manipulation
```

Social engineering should be treated as a controlled security exercise rather than an unrestricted attempt to deceive employees.

```text
Authorised Scenario
       |
       v
Defined Target Group
       |
       v
Approved Pretext
       |
       v
Controlled Interaction
       |
       v
Security Decision
       |
       v
Detection / Escalation
       |
       v
Evidence
       |
       v
Debrief / Cleanup
```

!!! warning "Explicit authorisation required"
    Social engineering directly involves people and may expose personal information, cause distress or disrupt business processes. The exact techniques, target groups, communication channels, prohibited actions, escalation procedures and stop conditions should be explicitly defined in the Rules of Engagement.


---

# Social Engineering Objectives

Typical objectives include:

```text
Validate employee security awareness

Validate help desk identity verification

Validate password reset procedures

Validate MFA recovery procedures

Validate visitor management

Validate physical security processes

Validate sensitive-information handling

Validate escalation procedures

Validate reporting mechanisms

Measure SOC or security-team visibility
```


---

# Social Engineering Is a Process Test

A successful social engineering interaction does not necessarily mean:

```text
Employee failed.
```

The underlying problem may instead involve:

```text
Weak verification procedures

Ambiguous policy

Insufficient training

Poor escalation paths

Excessive help desk authority

Weak visitor controls

Missing technical enforcement

Unsafe recovery procedures
```

Focus reporting on the security process rather than blaming individuals.


---

# Human Layer of Security

Security controls can be represented as:

```text
Technology
    |
    v
Process
    |
    v
People
```

An attacker may target whichever layer provides the easiest path.

For example:

```text
Strong MFA
   |
   v
Account Recovery
   |
   v
Help Desk
   |
   v
Weak Verification
   |
   v
Account Access
```

The technical control may be strong while the recovery process undermines it.


---

# Social Engineering Attack Surface

Potential interaction points include:

```text
Help desk

Reception

Security desk

Employees

Contractors

Suppliers

HR

Finance

IT administrators

Service desk

Facilities

Call centre

Executive assistants

Remote support teams
```


---

# Engagement Planning

Before testing, define:

```text
Objective

Target population

Allowed communication methods

Allowed identities

Approved pretexts

Prohibited scenarios

Working hours

Emergency contacts

Evidence requirements

Stop conditions

Debrief procedure
```


---

# Rules of Engagement

The ROE should explicitly state whether the following are permitted:

```text
Email

Telephone

SMS

Video calls

Physical visits

USB drops

QR codes

Credential submission

MFA interactions

Help desk calls

Password resets

Account recovery

Visitor impersonation

Third-party impersonation
```


---

# Prohibited Actions

Depending on the engagement, prohibited activities may include:

```text
Threats

Harassment

Intimidation

Blackmail

Romantic manipulation

Medical emergencies

Family emergencies

Law-enforcement impersonation

Emergency-service impersonation

Financial extortion

Requests for real payment

Requests for personal passwords

Collection of unnecessary personal data
```

These boundaries should be established before testing begins.


---

# Sensitive Pretexts

Avoid pretexts involving:

```text
Employee termination

Serious illness

Death

Family emergencies

Criminal accusations

Personal relationships

Salary disputes

Disciplinary action
```

A red team exercise should not create unnecessary psychological harm.


---

# Approved Pretext Design

A pretext is the scenario used to explain the tester's request.

A good authorised pretext should be:

```text
Relevant to the objective

Plausible

Limited in scope

Non-threatening

Easy to terminate

Easy to explain during debrief
```


---

# Example Pretext Categories

Possible controlled scenarios include:

```text
New employee support

Internal IT support

Meeting-room assistance

Visitor access

Vendor support

Account recovery

Temporary access request

Document-sharing request

Help desk validation
```

Use only scenarios approved by the organisation.


---

# Pretext Record

Maintain a record such as:

| Field | Example |
|---|---|
| Scenario ID | SE-004 |
| Objective | Test help desk verification |
| Channel | Telephone |
| Target | Service desk |
| Approved identity | Synthetic employee |
| Requested action | Test account recovery |
| Real credentials allowed | No |
| MFA interaction | No |
| Stop condition | Unexpected personal data requested |


---

# Synthetic Identities

Where possible, use customer-created synthetic identities.

Example:

```text
Name:
Alex Test

Department:
Red Team Validation

Employee ID:
RT-2026-004

Account:
alex.test
```

The organisation can configure the test identity so that:

```text
No production access exists

No real employee is impersonated

Recovery actions are reversible

SOC telemetry can be correlated
```


---

# Real Employee Impersonation

Impersonating a real employee increases risk.

Potential issues include:

```text
Reputational impact

Personal-data exposure

Confusion

Account lockout

Incorrect escalation

Damage to working relationships
```

Prefer synthetic identities unless the engagement specifically requires real-user impersonation.


---

# Target Selection

Targets should be selected according to the engagement objective.

Possible groups include:

```text
Random employee sample

Help desk personnel

Reception personnel

Privileged administrators

Finance staff

Remote workers

Specific business unit
```

Avoid unnecessary targeting of individuals.


---

# Sampling

Instead of testing everyone:

```text
Organisation
     |
     v
Defined Population
     |
     v
Representative Sample
     |
     v
Controlled Testing
```

This can provide useful evidence while reducing disruption.


---

# Communication Channels

Social engineering may occur through:

```text
Telephone

Email

SMS

Chat

Video conferencing

Physical interaction
```

Email-focused scenarios are covered separately in:

`red-teaming/phishing.md`


---

# Telephone Social Engineering

Telephone testing can validate:

```text
Identity verification

Help desk processes

Information disclosure

Account recovery

Escalation

Security awareness
```


---

# Telephone Test Model

```text
Call Initiated
     |
     v
Request Made
     |
     v
Verification Requested?
   /                \
 Yes                 No
 |                    |
 v                    v
Can Requester       Process
Satisfy Approved    Weakness
Test Verification?
     |
     v
Security Decision
     |
     v
Record Outcome
```


---

# Telephone Safety

Before calling, define:

```text
Approved caller identity

Approved target group

Permitted request

Maximum interaction duration

Information that may be provided

Information that must not be collected

Stop phrase

Escalation contact
```


---

# Help Desk Testing

Help desks are important because they often control:

```text
Password resets

Account unlocks

MFA resets

Device enrolment

Access requests

Remote support
```

These processes can become alternative authentication paths.


---

# Help Desk Security Model

```text
Requester
    |
    v
Help Desk
    |
    v
Identity Verification
    |
    +--> Knowledge
    |
    +--> Trusted Device
    |
    +--> Manager Approval
    |
    +--> Existing Authenticator
    |
    +--> Identity Platform
    |
    v
Sensitive Action
```


---

# Help Desk Validation Questions

Determine:

```text
How is identity verified?

Which information is considered proof?

Can public information satisfy verification?

Is manager approval required?

Are high-risk actions treated differently?

Are MFA resets audited?

Are password resets audited?

Does the user receive notification?

Does the SOC receive telemetry?
```


---

# Knowledge-Based Verification

Weak verification may rely on information such as:

```text
Employee name

Job title

Department

Manager name

Office location

Email address
```

Much of this information may be publicly available.

These attributes should generally not be treated as strong authentication factors.


---

# Stronger Verification

More robust processes may involve:

```text
Existing authenticated session

Known managed device

Existing MFA factor

Manager approval

Identity verification platform

In-person verification

Multiple independent checks
```


---

# Account Recovery

Account recovery deserves particular attention.

```text
Primary Authentication
        |
        v
      Strong MFA
        |
        v
   Recovery Process
        |
        v
Weak Verification?
        |
        v
Control Undermined
```

The recovery process should not be significantly weaker than normal authentication.


---

# Password Reset Testing

If password reset testing is authorised, prefer a dedicated test account.

Example:

```text
Synthetic account:
alex.test

Objective:
Determine whether the help desk follows the documented
verification process before initiating password recovery.
```

Do not reset a real employee's password merely to prove the process weakness.


---

# MFA Recovery

MFA recovery may include:

```text
Authenticator replacement

Phone-number change

Temporary access pass

Hardware-token replacement

MFA reset

New-device enrolment
```

These are high-impact actions and should be specifically addressed in the ROE.


---

# MFA Recovery Test Model

```text
Recovery Request
      |
      v
Identity Verification
      |
      v
Approval Required?
      |
      v
Recovery Action
      |
      v
User Notification
      |
      v
Audit / SIEM
```


---

# Information Elicitation

Information elicitation tests whether personnel disclose information that should be protected.

Potential categories include:

```text
Internal processes

System names

Employee information

Technology details

Support procedures

Vendor information

Office procedures
```

Avoid requesting real credentials or unnecessary personal information.


---

# Information Classification

Before testing, define which information is:

```text
Public

Internal

Confidential

Restricted
```

A useful finding requires demonstrating disclosure of information that actually should have been protected.


---

# Public Information Is Not a Finding

For example:

```text
Employee reveals company headquarters address.
```

If the address is public, this is not meaningful information disclosure.

Instead test whether restricted information can be obtained.


---

# Minimal Information Collection

If an employee begins disclosing more information than required:

```text
Objective Proven
      |
      v
Stop Collection
      |
      v
Record Minimum Evidence
```

Do not continue gathering sensitive information unnecessarily.


---

# Physical Social Engineering

Physical scenarios may test:

```text
Reception procedures

Visitor badges

Tailgating controls

Restricted areas

Security guards

Door controls

Escort requirements

Visitor logging
```

Physical testing requires particularly clear authorisation.


---

# Physical Scope

Define:

```text
Buildings

Floors

Rooms

Restricted areas

Working hours

Allowed entrances

Prohibited areas

Safety-critical areas
```


---

# Areas Commonly Excluded

Possible exclusions include:

```text
Data centres

Medical areas

Industrial control areas

Safety-critical facilities

Executive residences

Childcare areas

Emergency facilities
```

The actual exclusions depend on the engagement.


---

# Visitor Management

A mature visitor process may require:

```text
Identity verification

Host confirmation

Visitor registration

Temporary badge

Escort

Badge return

Entry/exit logging
```


---

# Visitor Test Model

```text
Arrival
   |
   v
Reception
   |
   v
Identity Checked?
   |
   v
Host Confirmed?
   |
   v
Badge Issued?
   |
   v
Escort Required?
   |
   v
Access Decision
```


---

# Tailgating

Tailgating occurs when an unauthorised person follows an authorised person through a controlled entry point.

In testing, define:

```text
Which doors may be tested?

Can employees be approached?

Can testers follow employees?

What happens if challenged?

When must the test stop?
```

Do not force doors or physically pressure employees.


---

# Piggybacking

Piggybacking generally involves an authorised person knowingly allowing another person to enter.

The assessment should record whether:

```text
Badge verification occurred

Visitor status was checked

Escort policy was followed

Security was contacted
```


---

# Restricted Area Validation

Once access to a controlled area is achieved:

```text
Stop when the objective is proven.
```

Do not continue deeper into the building merely because additional access appears possible.


---

# Physical Proof

Possible proof includes:

```text
Timestamp

Approved photograph

Location identifier

Access log

Tester notes

Customer-provided marker
```

Avoid photographing employees or sensitive material unnecessarily.


---

# Clean Desk Testing

If explicitly authorised, physical testing may evaluate whether sensitive material is exposed.

Potential examples:

```text
Printed confidential documents

Unlocked workstations

Visible credentials

Sensitive whiteboards

Unattended access cards
```

Do not collect or remove real employee property.


---

# USB Drop Exercises

USB-drop exercises may test whether employees connect unknown removable media.

A safe exercise should use:

```text
Customer-approved devices

Clearly inventoried media

Non-malicious content

Unique identifiers

Controlled telemetry
```

Avoid deploying executable payloads unless separately authorised and necessary.


---

# Safe USB Marker

A test device could contain:

```text
README.txt
```

with an engagement identifier.

The goal might be to measure:

```text
Device insertion

Security alert

Employee reporting

SOC response
```

rather than executing code.


---

# QR Code Exercises

QR codes can be used in awareness exercises.

A controlled QR code should lead only to:

```text
Customer-controlled test page

Red-team-controlled approved test page
```

Do not collect real credentials.


---

# QR Test Metrics

Possible metrics include:

```text
Scans

Unique test sessions

Reporting

Time to report

Security-team response
```


---

# Third-Party Impersonation

Vendor or supplier impersonation can create legal and reputational risks.

Only use an actual third-party identity if explicitly approved.

Prefer:

```text
Synthetic vendor

Customer-created test supplier

Generic support scenario
```


---

# Executive Impersonation

Executive impersonation may be particularly persuasive.

It may also create:

```text
Reputational risk

Employee stress

Financial risk

Escalation risk
```

Use only when explicitly authorised and necessary.


---

# Finance Scenarios

Finance-related social engineering may test:

```text
Payment-change procedures

Supplier verification

Invoice handling

Bank-detail changes

Approval workflows
```

Do not request or cause real financial transfers.


---

# Safe Finance Test

Use:

```text
Synthetic supplier

Test invoice

Dummy account information

Non-production workflow
```

The objective should be to test the process without creating financial impact.


---

# Business Email Compromise Simulation

BEC-style exercises may test whether:

```text
Payment requests are independently verified

Supplier changes require secondary approval

Executive requests bypass normal process

Employees report suspicious messages
```

No real payment should occur.


---

# HR Scenarios

HR processes may expose:

```text
Employee information

Account onboarding

Account termination

Identity information

Payroll processes
```

Avoid collecting real HR data unless explicitly necessary.


---

# Onboarding

Potential test questions include:

```text
Can an unverified person obtain account details?

Can equipment be collected without sufficient identity verification?

Can access be provisioned before approval?
```


---

# Offboarding

Potential security questions include:

```text
Are accounts disabled promptly?

Are badges revoked?

Are sessions terminated?

Are devices recovered?

Are tokens revoked?
```

These are usually better tested with synthetic or controlled accounts.


---

# Remote Work

Remote working introduces additional verification challenges.

Examples:

```text
Employees cannot physically verify colleagues

Help desk interactions occur remotely

Personal phone numbers may be used

Courier delivery may be involved

Video meetings may substitute in-person contact
```


---

# Video Conferencing

Video calls should not automatically be considered strong identity proof.

Consider:

```text
Known corporate account

Meeting invitation origin

Existing authenticated identity

Secondary verification
```

Do not design exercises around deceptive synthetic media unless explicitly authorised.


---

# Deepfake and Synthetic Media

AI-generated voice or video introduces new social engineering risks.

Testing with synthetic media requires explicit approval because it can create significant:

```text
Reputational risk

Privacy risk

Psychological impact

Legal concerns
```

A safer initial exercise is tabletop validation:

```text
Would the help desk accept a video call as identity proof?

Would finance accept voice approval?

What secondary controls exist?
```


---

# Reporting Mechanisms

Employees need a clear way to report suspicious activity.

Possible channels include:

```text
Phishing-report button

Security mailbox

Help desk

SOC hotline

Teams/Slack security channel

Incident portal
```


---

# Reporting Validation

Measure whether employees:

```text
Recognise suspicious behaviour

Know where to report it

Report quickly

Provide useful context
```


---

# Positive Security Behaviour

Examples include:

```text
Employee refuses the request

Employee follows verification procedure

Employee contacts manager

Employee reports the interaction

Reception challenges the visitor

Help desk escalates the request
```

These should be reported as positive security outcomes.


---

# Do Not Punish Employees for Reporting

If an employee becomes suspicious and reports the exercise:

```text
That is success.
```

The red team should not continue manipulating the person merely to achieve a technical objective.


---

# Security Awareness

Awareness should focus on behaviours such as:

```text
Verify unusual requests

Use approved communication channels

Do not share authentication factors

Challenge unknown visitors

Report suspicious interactions

Follow payment verification procedures

Escalate uncertainty
```


---

# Detection Validation

Social engineering can also test organisational detection and response.

Potential telemetry includes:

```text
Help desk tickets

Password reset logs

MFA reset logs

Identity audit logs

Visitor management logs

Physical access logs

Email telemetry

Endpoint telemetry

Security reports
```


---

# Identity Telemetry

Account recovery may generate:

```text
Password reset events

MFA changes

Authentication events

New-device registration

Temporary access credentials

Administrative actions
```

Validate whether these events reach the SIEM where appropriate.


---

# Help Desk Audit

Help desk platforms may record:

```text
Ticket creation

Requester identity

Agent identity

Actions taken

Approval

Notes

Timestamps
```

These records can provide valuable evidence.


---

# Physical Access Telemetry

Possible sources include:

```text
Badge access

Visitor-management platform

Reception logs

CCTV

Door alarms

Security reports
```

Use CCTV only according to organisational policy and engagement authorisation.


---

# Detection Hypothesis

Example:

```text
Hypothesis:
An unusual MFA recovery request for the synthetic red team
account should require enhanced verification and generate
identity audit telemetry.

Test:
Request MFA recovery through the authorised help desk scenario.

Expected:
The help desk performs the documented verification process and
the recovery request is logged.

Result:
Record verification, approval, telemetry and escalation.
```


---

# Physical Detection Hypothesis

```text
Hypothesis:
An unknown visitor attempting to enter a restricted office area
without an escort should be challenged and reported.

Test:
Use the approved visitor scenario at the agreed location.

Expected:
Reception or staff challenge the tester and follow the visitor
management procedure.

Result:
Record whether the procedure was followed.
```


---

# Detection Outcomes

Classify outcomes as:

```text
Prevented and Reported

Prevented but Not Reported

Allowed and Detected

Allowed and Logged

Allowed without Detection
```


---

# Human Outcome Classification

For social engineering, another useful classification is:

```text
Request Refused

Verification Performed

Request Escalated

Information Disclosed

Sensitive Action Initiated

Sensitive Action Completed
```


---

# Example Outcome

```text
Scenario:
SE-006

Objective:
Help desk account recovery

Account:
Synthetic test user

Result:
Agent requested employee ID and manager name.

Both values were part of the approved pretext and were publicly
available within the test scenario.

No secondary verification was performed.

Password recovery was initiated.

Classification:
Sensitive Action Initiated

Security Team Alert:
None
```


---

# Candidate vs Confirmed

## Candidate

```text
The help desk appears to rely on knowledge-based verification.
```


## Likely

```text
The requested verification information can be obtained from
public or organisational sources.
```


## Confirmed

```text
The help desk initiated account recovery for the synthetic test
account using only the approved knowledge-based information.
```


---

# Evidence

Social engineering evidence may include:

```text
Scenario ID

Date and time

Channel

Target function

Tester identity

Approved pretext

Request

Verification performed

Information disclosed

Action performed

Escalation

Security report

Detection result

Outcome
```


---

# Personal Data in Evidence

Avoid recording unnecessary:

```text
Employee names

Personal phone numbers

Private conversations

Personal email addresses

Photographs

Voice recordings
```

Use role-based descriptions where possible.

For example:

```text
Service Desk Agent 1
```

instead of a full employee name.


---

# Recording Calls

Do not record telephone or video interactions unless explicitly approved and legally reviewed.

Tester notes may provide sufficient evidence.


---

# Evidence Example

```text
Scenario ID:
SE-003

Channel:
Telephone

Target:
Service Desk

Objective:
Validate identity verification for test account recovery

Identity:
Synthetic employee

Request:
Password recovery

Verification:
Employee ID and manager name requested

Result:
Recovery initiated

Additional Verification:
None

Security Report:
None observed

Production Credentials Collected:
No

Impact:
The tested recovery process relied on information available to
the approved test scenario.
```


---

# Evidence Strength

Use:

```text
Observed

Likely

Confirmed
```

Do not convert assumptions into confirmed findings.


---

# Reporting

A social engineering finding should explain:

```text
Which process was tested?

What was requested?

Which verification occurred?

Which security decision was made?

What technical or procedural control was missing?

What was the potential impact?

How should the process improve?
```


---

# Avoid Employee-Blaming Language

Avoid:

```text
The employee was careless and gave the attacker access.
```

Prefer:

```text
The tested visitor process allowed access without requiring the
documented host verification step.
```

Focus on systemic improvement.


---

# Example Finding - Help Desk Verification

```text
Title:
Help Desk Account Recovery Relies on Publicly Obtainable Information

Observation:
During an authorised telephone social engineering scenario, the
assessment requested account recovery for a customer-provided
synthetic user.

The service desk requested the employee identifier, department
and manager name before initiating the recovery process.

No existing authenticator, trusted device or independent
approval was required.

The information used during the test was part of the approved
scenario and did not include production credentials.

Impact:
An attacker who obtains basic employee information may be able
to abuse the tested recovery process to weaken or bypass normal
authentication controls.

Recommendation:
Strengthen account-recovery verification using independent
factors such as existing authenticators, managed devices,
verified manager approval or dedicated identity-verification
workflows. Do not rely solely on publicly obtainable employee
attributes.
```


---

# Example Finding - Visitor Management

```text
Title:
Visitors Can Enter Restricted Office Area Without Host Verification

Observation:
During the approved physical security scenario, the tester
requested access to the office using the agreed synthetic vendor
pretext.

A visitor badge was issued without contacting the stated host.

The tester stopped after entering the authorised test area.

No restricted rooms or employee systems were accessed.

Impact:
An unauthorised individual may be able to gain physical access
to office areas without confirmation from an employee sponsor.

Recommendation:
Require host verification before issuing visitor credentials,
enforce escort requirements and periodically review visitor
management procedures with reception and security personnel.
```


---

# Example Finding - Information Disclosure

```text
Title:
Internal Support Information Disclosed Without Requester Verification

Observation:
During the authorised telephone scenario, the tester requested
internal support information while using the approved synthetic
employee identity.

The requested information was provided without verifying the
requester's identity.

Impact:
Disclosure of internal operational information may assist an
attacker in developing more convincing social engineering
scenarios or identifying additional attack paths.

Recommendation:
Define which support information requires requester verification
and provide staff with clear escalation procedures for unusual
requests.
```


---

# Example Positive Security Result

```text
Control:
Service Desk Identity Verification

Scenario:
The tester requested MFA recovery for a synthetic employee.

Result:
The service desk refused to perform the recovery because the
tester could not complete verification using the existing
registered authenticator.

The agent also created a security ticket and escalated the
interaction.

Conclusion:
The tested recovery process successfully resisted the social
engineering scenario.
```


---

# Root Causes

Common root causes include:

```text
Weak identity verification

Knowledge-based authentication

Unclear procedures

Inconsistent processes

Insufficient staff training

Missing escalation paths

Excessive help desk authority

Weak visitor management

Lack of secondary approval

Insufficient audit logging

Weak recovery controls
```


---

# Remediation - Help Desk

Consider:

```text
Documented verification workflows

Existing-authenticator verification

Managed-device verification

Independent manager approval

Risk-based recovery

High-risk action escalation

User notifications

Audit logging

Regular process testing
```


---

# Remediation - Identity Recovery

Consider:

```text
Recovery controls equivalent to primary authentication strength

Multiple independent verification signals

Temporary recovery credentials

Short validity periods

Immediate user notification

Administrative audit

SIEM integration
```


---

# Remediation - Physical Security

Consider:

```text
Visitor registration

Identity checks

Host confirmation

Visitor badges

Escort requirements

Badge expiration

Badge return

Restricted-area controls

Security awareness
```


---

# Remediation - Employees

Provide practical guidance:

```text
Verify unusual requests

Use official directories

Do not trust caller ID alone

Do not disclose authentication factors

Do not bypass procedures because a request appears urgent

Report suspicious interactions

Challenge unknown visitors according to policy
```


---

# Remediation - Finance

Consider:

```text
Independent payment verification

Known contact details

Dual approval

Supplier-change verification

Out-of-band confirmation

Transaction limits

Fraud monitoring
```


---

# Debriefing

Social engineering exercises should include a controlled debrief.

Possible objectives:

```text
Explain the exercise

Reduce employee uncertainty

Reinforce positive behaviour

Explain observed weaknesses

Provide practical guidance

Collect participant feedback
```


---

# Individual vs Group Debrief

Depending on the exercise:

```text
Immediate individual debrief

Delayed individual debrief

Team debrief

Organisation-wide awareness session
```

may be appropriate.

The engagement plan should define the approach.


---

# Protect Participants

Reports should normally avoid creating a public list of:

```text
Employees who clicked

Employees who answered calls

Employees who disclosed information
```

Aggregate metrics and process-level findings are often more useful.


---

# Metrics

Useful metrics may include:

```text
Interactions attempted

Interactions completed

Requests refused

Verification performed

Requests escalated

Security reports submitted

Sensitive actions initiated

Sensitive actions completed

Time to report

Time to security response
```


---

# Example Metrics

```text
Telephone scenarios:
10

Requests refused:
6

Requests escalated:
3

Sensitive action initiated:
1

Sensitive action completed:
0

Security reports:
4

Median time to report:
7 minutes
```


---

# Success Rate

A simple scenario success rate can be calculated as:

```text
Successful Scenarios / Completed Scenarios * 100
```

But do not use this metric without context.

For example:

```text
2 of 10 interactions resulted in information disclosure
```

does not explain:

```text
What information?

How sensitive?

Which process?

What verification was expected?
```


---

# Better Metrics

Prefer metrics linked to control behaviour:

```text
Percentage performing required verification

Percentage escalating unusual requests

Percentage reporting suspicious interactions

Percentage of high-risk actions requiring secondary approval
```


---

# Time to Report

```text
TTR = Security Report Time - Interaction Time
```

This can measure awareness and reporting effectiveness.


---

# Scenario Inventory

Maintain:

| ID | Channel | Target Function | Objective | Status |
|---|---|---|---|---|
| SE-001 | Phone | Help Desk | Password recovery | Complete |
| SE-002 | Physical | Reception | Visitor control | Complete |
| SE-003 | Phone | Finance | Process verification | Stopped |
| SE-004 | QR | General Staff | Reporting | Planned |


---

# Stop Conditions

Stop immediately if:

```text
Employee becomes distressed

Emergency services are contacted

Real financial action begins

Unexpected sensitive data is disclosed

A production account may be disrupted

A third party becomes involved unexpectedly

Physical safety is affected

Tester enters an excluded area

The scenario leaves the approved scope
```


---

# Emergency Contact

The red team should have:

```text
Primary engagement contact

Backup contact

Security contact

Physical security contact

Emergency stop phrase
```

available during testing.


---

# Deconfliction

Security teams may encounter activity that appears malicious.

A deconfliction process should allow authorised personnel to determine:

```text
Is this part of the exercise?

Is this a real attack?

Should the exercise continue?

Should the test be stopped?
```

without unnecessarily revealing the exercise to all participants.


---

# Social Engineering and OPSEC

Protect:

```text
Target lists

Employee information

Pretexts

Synthetic identities

Scenario documents

Call notes

Physical access information

Evidence
```

See:

[Red Team OPSEC](opsec.md)


---

# Social Engineering and Detection Validation

The exercise should evaluate:

```text
Human detection

Technical telemetry

Reporting

Escalation

SOC correlation

Response
```

See:

[Detection Validation](detection-validation.md)


---

# Social Engineering and Reporting

Report:

```text
Process weaknesses

Control strengths

Observed verification

Observed escalation

Detection

Response

Business impact

Remediation
```

Avoid unnecessary personal attribution.

See:

[Red Team Reporting](reporting.md)


---

# Retesting

After remediation:

```text
Original Scenario
       |
       v
Same Process
       |
       v
Equivalent Synthetic Identity
       |
       v
Repeat Test
       |
       v
Compare Verification
```

Do not necessarily retest the same employee.

The control is usually the process.


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

# Social Engineering Checklist

## Planning

- [ ] Objective defined
- [ ] Social engineering explicitly authorised
- [ ] Target group defined
- [ ] Channels defined
- [ ] Pretexts approved
- [ ] Synthetic identities considered
- [ ] Working hours defined
- [ ] Prohibited actions documented
- [ ] Stop conditions documented
- [ ] Emergency contacts available
- [ ] Debrief process defined

## Identity

- [ ] Real employee impersonation avoided where possible
- [ ] Synthetic identity documented
- [ ] Test account created where required
- [ ] No production credentials required
- [ ] Recovery actions reversible
- [ ] Test identity cleanup planned

## Telephone

- [ ] Caller identity approved
- [ ] Target function approved
- [ ] Request approved
- [ ] Maximum interaction duration defined
- [ ] Verification steps recorded
- [ ] Disclosure minimised
- [ ] Escalation recorded
- [ ] Call recording avoided unless approved

## Help Desk

- [ ] Password reset scope defined
- [ ] MFA reset scope defined
- [ ] Account unlock scope defined
- [ ] Synthetic account preferred
- [ ] Verification procedure documented
- [ ] High-risk approval requirements reviewed
- [ ] User notification reviewed
- [ ] Audit telemetry reviewed

## Physical

- [ ] Building in scope
- [ ] Floors in scope
- [ ] Restricted areas defined
- [ ] Prohibited areas defined
- [ ] Visitor scenario approved
- [ ] Tailgating rules defined
- [ ] Safety requirements understood
- [ ] Stop point defined
- [ ] Evidence method approved

## Information

- [ ] Requested information classified
- [ ] Public information distinguished from sensitive information
- [ ] Minimum necessary disclosure recorded
- [ ] Unexpected sensitive data not collected
- [ ] Personal data minimised

## Finance

- [ ] Synthetic transaction only
- [ ] No real payment requested
- [ ] Approval workflow defined
- [ ] Secondary verification evaluated
- [ ] Test stopped before financial impact

## Detection

- [ ] Help desk ticket reviewed
- [ ] Identity audit reviewed
- [ ] MFA audit reviewed
- [ ] Physical access logs reviewed
- [ ] Security reports reviewed
- [ ] SIEM ingestion reviewed
- [ ] SOC response recorded

## Evidence

- [ ] Scenario ID recorded
- [ ] Timestamp recorded
- [ ] Channel recorded
- [ ] Target function recorded
- [ ] Pretext recorded
- [ ] Request recorded
- [ ] Verification recorded
- [ ] Outcome recorded
- [ ] Personal data minimised
- [ ] Evidence protected

## Debrief

- [ ] Debrief method defined
- [ ] Participants treated respectfully
- [ ] Positive behaviour recognised
- [ ] Process improvements explained
- [ ] Employee blame avoided

## Cleanup

- [ ] Synthetic accounts removed
- [ ] Temporary access removed
- [ ] Temporary badges returned
- [ ] Test documents removed
- [ ] Test devices recovered
- [ ] Temporary identities retired
- [ ] Evidence retention reviewed


---

# Social Engineering Decision Model

```text
                     OBJECTIVE
                         |
                         v
               HUMAN PROCESS REQUIRED?
                   /            \
                 No              Yes
                 |                |
                STOP              v
                           AUTHORISED?
                           /       \
                         No         Yes
                         |           |
                        STOP         v
                            TARGET GROUP
                                 |
                                 v
                          APPROVED PRETEXT
                                 |
                                 v
                         SYNTHETIC IDENTITY?
                           /            \
                         Yes             No
                         |                |
                         v                v
                     USE TEST ID     REAL IDENTITY
                                    EXPLICITLY
                                    APPROVED?
                                     /     \
                                   No       Yes
                                   |         |
                                  STOP       v
                                         INTERACT
                                            |
                                            v
                                      VERIFICATION
                                            |
                          +-----------------+-----------------+
                          |                 |                 |
                          v                 v                 v
                        REFUSE           ESCALATE           ALLOW
                          |                 |                 |
                          +-----------------+-----------------+
                                            |
                                            v
                                         REPORT
                                            |
                                            v
                                        DETECTION
                                            |
                                            v
                                         DEBRIEF
```


---

# Help Desk Decision Model

```text
                 RECOVERY REQUEST
                        |
                        v
                 REQUESTER IDENTITY
                        |
                        v
                 STRONG VERIFICATION?
                   /             \
                 No               Yes
                 |                 |
                 v                 v
             DO NOT ACT        RISK CHECK
                 |                 |
                 v                 v
              ESCALATE       HIGH-RISK ACTION?
                               /          \
                             Yes           No
                             |              |
                             v              v
                         SECONDARY        PROCESS
                         APPROVAL
                             |
                             v
                           PROCESS
                             |
                             v
                         USER NOTICE
                             |
                             v
                          AUDIT LOG
```


---

# Physical Security Decision Model

```text
                    VISITOR
                       |
                       v
                IDENTITY CHECK
                       |
                       v
                HOST CONFIRMATION
                       |
                       v
                 BADGE ISSUED
                       |
                       v
                ESCORT REQUIRED?
                  /          \
                Yes           No
                |              |
                v              v
              ESCORT       ACCESS POLICY
                |              |
                +------+-------+
                       |
                       v
                  AUTHORISED AREA
                       |
                       v
                   EXIT / LOG
```


---

# Social Engineering Maturity Model

```text
Level 1
Ad-hoc employee awareness

Level 2
Documented verification and reporting procedures

Level 3
Consistent identity, visitor and escalation controls

Level 4
Technical telemetry integrated with human reporting

Level 5
Regular scenario-based validation with measurable improvement
```


---

# Final Social Engineering Model

```text
                 AUTHORISED OBJECTIVE
                         |
                         v
                    TARGET PROCESS
                         |
                         v
                    RISK REVIEW
                         |
                         v
                   APPROVED PRETEXT
                         |
                         v
                  SYNTHETIC IDENTITY
                         |
                         v
                    INTERACTION
                         |
              +----------+----------+
              |          |          |
              v          v          v
           VERIFY      REFUSE     ESCALATE
              |          |          |
              +----------+----------+
                         |
                         v
                    HUMAN SIGNAL
                         |
                         v
                 TECHNICAL TELEMETRY
                         |
                         v
                     REPORTING
                         |
                         v
                    SOC / SECURITY
                         |
                         v
                      RESPONSE
                         |
                         v
                      EVIDENCE
                         |
                         v
                      DEBRIEF
                         |
                         v
                   PROCESS CHANGE
                         |
                         v
                      RETEST
```


---

# Core Principle

Social engineering testing can be reduced to:

```text
Test the process, not the person.

Obtain explicit authorisation.

Define target groups.

Use approved pretexts.

Prefer synthetic identities.

Avoid unnecessary personal data.

Never request real payments.

Avoid psychologically harmful scenarios.

Use dedicated test accounts for recovery testing.

Stop when the objective is proven.

Recognise employees who challenge or report the scenario.

Validate help desk and identity telemetry.

Validate physical security procedures.

Measure reporting and escalation.

Protect participant information.

Report systemic weaknesses rather than blaming individuals.

Debrief appropriately.

Retest the process after remediation.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Discovery](discovery.md)
- [Credential Access](credential-access.md)
- [Collection](collection.md)
- [Exfiltration](exfiltration.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)

Planned:

```text
red-teaming/phishing.md
red-teaming/adversary-emulation.md
red-teaming/cleanup.md
```


---

# References

- [MITRE ATT&CK - Phishing](https://attack.mitre.org/techniques/T1566/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Trusted Relationship](https://attack.mitre.org/techniques/T1199/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Account Access Removal](https://attack.mitre.org/techniques/T1531/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-63B - Authentication and Authenticator Management](https://pages.nist.gov/800-63-4/sp800-63b.html){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [CISA - Avoiding Social Engineering and Phishing Attacks](https://www.cisa.gov/news-events/news/avoiding-social-engineering-and-phishing-attacks){ target="_blank" rel="noopener noreferrer" }
- [CISA - Implementing Phishing-Resistant MFA](https://www.cisa.gov/resources-tools/resources/implementing-phishing-resistant-mfa){ target="_blank" rel="noopener noreferrer" }
- [OWASP - Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP - Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "A refusal is a successful control"
    When an employee refuses an unusual request, performs the required verification or reports the interaction, record it as a positive security result. The purpose of the assessment is to identify where organisational controls succeed and where they need improvement.


!!! warning "Do not turn the exercise into a contest"
    The goal is not to manipulate an employee until they eventually make a mistake. Once the tested control has succeeded or failed and sufficient evidence exists, end the interaction and follow the agreed debrief procedure.
