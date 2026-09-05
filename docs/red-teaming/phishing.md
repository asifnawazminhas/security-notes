---
title: Red Team Phishing
description: Phishing methodology for authorised red team assessments, covering campaign planning, email security controls, safe landing pages, synthetic credentials, attachment and link scenarios, QR phishing, MFA-resistant testing principles, telemetry, detection validation, metrics, cleanup and reporting.
---

# Red Team Phishing

Phishing is a social engineering technique that uses electronic communication to influence a target into performing an action.

Typical attacker objectives include:

```text
Open a link

Open an attachment

Submit credentials

Approve authentication

Execute content

Provide information

Initiate a business process
```

In an authorised red team assessment, phishing should instead be treated as a controlled test of:

```text
Email Security

User Awareness

Identity Controls

Endpoint Controls

Reporting

SOC Detection

Incident Response
```

A safe phishing model is:

```text
Authorised Objective
        |
        v
Approved Target Group
        |
        v
Controlled Message
        |
        v
Safe Landing Page / Test Artifact
        |
        v
User Action
        |
        v
Security Controls
        |
        v
Detection / Reporting
        |
        v
Evidence
        |
        v
Debrief / Cleanup
```

!!! warning "Explicit authorisation required"
    Phishing directly targets people and may interact with production email, identity and endpoint controls. Campaign scope, recipients, sending infrastructure, domains, landing pages, credential handling, attachments, QR codes, MFA interactions, data retention and stop conditions should be explicitly approved before testing.


---

# Phishing Objectives

Typical objectives include:

```text
Validate secure email gateway controls

Validate anti-phishing controls

Validate domain authentication

Validate malicious-link protection

Validate attachment controls

Validate browser protections

Validate endpoint protections

Validate identity controls

Validate user reporting

Validate SOC visibility

Measure incident-response performance
```


---

# Phishing Is More Than Click Rate

A phishing assessment should not be reduced to:

```text
How many people clicked?
```

A better model is:

```text
Message Delivery
      |
      v
Email Security
      |
      v
User Decision
      |
      v
Identity / Endpoint Control
      |
      v
User Reporting
      |
      v
SOC Detection
      |
      v
Response
```

A user clicking a test link does not automatically mean the organisation has suffered a serious control failure.

For example:

```text
User Clicks
    |
    v
Browser Blocks
    |
    v
Security Alert
    |
    v
SOC Responds
```

may demonstrate successful defence in depth.


---

# Phishing in the Attack Chain

```text
Reconnaissance
      |
      v
Target Selection
      |
      v
Phishing
      |
      v
User Interaction
      |
      +--------------------+
      |                    |
      v                    v
Credential Scenario    Execution Scenario
      |                    |
      v                    v
Identity Controls      Endpoint Controls
      |                    |
      +---------+----------+
                |
                v
           Initial Access
```

See:

[Initial Access](initial-access.md)


---

# Phishing vs Social Engineering

Phishing is a subset of social engineering.

```text
Social Engineering
      |
      +--> Telephone
      |
      +--> Physical
      |
      +--> Help Desk
      |
      +--> Information Elicitation
      |
      +--> Phishing
             |
             +--> Email
             |
             +--> SMS
             |
             +--> QR
```

See:

[Social Engineering](social-engineering.md)


---

# Phishing Campaign Lifecycle

```text
Authorisation
      |
      v
Objective
      |
      v
Target Population
      |
      v
Scenario
      |
      v
Infrastructure
      |
      v
Pre-Test Validation
      |
      v
Campaign
      |
      v
Telemetry
      |
      v
Response
      |
      v
Debrief
      |
      v
Reporting
      |
      v
Cleanup
```


---

# Rules of Engagement

Before the campaign, define:

```text
Campaign dates

Sending windows

Target groups

Excluded users

Approved sender identities

Approved domains

Approved landing pages

Allowed attachment types

Allowed link types

Credential handling

MFA interaction

Maximum messages

Reminder messages

Data retention

Debrief process

Emergency contacts

Stop conditions
```


---

# Target Population

Potential populations include:

```text
Representative employee sample

Specific department

Privileged administrators

Help desk

Finance

Executives

Remote workers

New employees
```

Target selection should follow the engagement objective rather than simply maximising the number of recipients.


---

# Exclusions

Potential exclusions may include:

```text
Employees on leave

Employees involved in critical incidents

Emergency personnel

Sensitive HR cases

External contractors

Third parties

Shared public mailboxes
```

Actual exclusions should be agreed with the organisation.


---

# Target Minimisation

A campaign does not necessarily require the entire organisation.

```text
Organisation
     |
     v
Relevant Population
     |
     v
Representative Sample
     |
     v
Controlled Campaign
```

Smaller campaigns can provide useful evidence while reducing disruption.


---

# Scenario Design

A phishing scenario should be:

```text
Relevant

Plausible

Non-threatening

Measurable

Reversible

Aligned to the objective
```

Avoid unnecessary psychological pressure.


---

# Safe Scenario Categories

Examples include:

```text
Internal survey

Training notification

Document-sharing notification

Test meeting invitation

Synthetic IT notification

Benefits portal test

Policy acknowledgement

Test collaboration request
```

Use only scenarios approved for the engagement.


---

# Sensitive Scenarios

Avoid or explicitly review scenarios involving:

```text
Termination

Salary changes

Bonuses

Medical information

Family emergencies

Death

Disciplinary action

Legal threats

Criminal allegations

Romantic relationships

Urgent personal financial problems
```

These scenarios can create unnecessary distress.


---

# Campaign Record

Maintain a campaign record.

Example:

| Field | Example |
|---|---|
| Campaign ID | PHISH-2026-004 |
| Objective | Validate link-based phishing controls |
| Targets | 25 test users |
| Channel | Email |
| Sender | Approved synthetic identity |
| Domain | Approved test domain |
| Landing page | Controlled training page |
| Credential collection | Synthetic only |
| Attachment | None |
| Start | 09:00 |
| End | 15:00 |


---

# Sending Infrastructure

Phishing infrastructure may include:

```text
Domain

DNS

Mail server

Sending platform

Landing page

TLS certificate

Logging

Test mailbox
```

All infrastructure should be:

```text
Approved

Controlled

Inventoried

Logged

Temporary where appropriate
```

See:

[Red Team Infrastructure](infrastructure.md)


---

# Domain Selection

Use:

```text
Customer-owned test domain

Red-team-owned approved domain

Dedicated engagement subdomain
```

Avoid impersonating unrelated organisations.


---

# Domain Inventory

Record:

```text
Domain

Registrar

Owner

Purpose

DNS provider

Mail provider

TLS status

Start date

Retirement date
```


---

# DNS Records

Email infrastructure may require:

```text
A

AAAA

MX

TXT

SPF

DKIM

DMARC
```

The exact configuration depends on the approved sending platform.


---

# SPF

SPF allows a domain to define which mail systems are authorised to send mail on its behalf.

Example structure:

```text
v=spf1 include:approved-mail-provider.example -all
```

Use the correct values for the actual authorised provider.


---

# DKIM

DKIM cryptographically signs email so receiving systems can verify that an authorised system signed the message.

Validate that the campaign platform supports appropriate DKIM configuration.


---

# DMARC

DMARC builds on SPF and DKIM and allows domain owners to specify handling and reporting policy.

A phishing assessment can also evaluate whether the organisation's own domains are protected against spoofing.


---

# Domain Authentication Model

```text
Sender
  |
  v
SPF
  |
  v
DKIM
  |
  v
DMARC
  |
  v
Receiving Mail System
```


---

# Defensive Domain Review

During reconnaissance, review whether organisational domains have:

```text
SPF

DKIM

DMARC
```

Misconfiguration may increase spoofing risk.

Do not spoof a production domain unless that scenario is explicitly authorised.


---

# Pre-Test Infrastructure Validation

Before sending to employees, test with:

```text
Red team mailbox

Customer security mailbox

Customer test account
```

Validate:

```text
Message delivery

Formatting

Links

TLS

Landing page

Logging

Redirect behaviour

Tracking

Cleanup
```


---

# Test Accounts First

Use a progression:

```text
Red Team Mailbox
      |
      v
Customer Test Mailbox
      |
      v
Small Pilot Group
      |
      v
Approved Campaign
```

This reduces accidental production impact.


---

# Email Message Structure

A campaign message typically contains:

```text
Sender

Recipient

Subject

Body

Link or attachment

Scenario context
```

Avoid unnecessary tracking or personal data.


---

# Sender Identity

Prefer:

```text
Synthetic internal identity

Synthetic vendor

Dedicated test identity
```

over impersonating a real employee.


---

# Display Name

Email clients may display:

```text
Display Name <address@example.com>
```

Employees should be trained to consider the actual sender identity rather than relying solely on the display name.


---

# Reply-To

The `Reply-To` address may differ from the sender.

Security controls and users should consider unexpected mismatches.

Campaigns should not route replies to unrelated third parties.


---

# Link-Based Phishing

A link-based scenario generally tests:

```text
Email filtering

URL rewriting

Safe Links

Browser controls

DNS filtering

Proxy controls

User awareness

Reporting
```


---

# Link Test Model

```text
Email
  |
  v
Secure Email Gateway
  |
  v
Inbox
  |
  v
User Click
  |
  v
URL Protection
  |
  v
Browser / Proxy
  |
  v
Safe Landing Page
  |
  v
Telemetry
```


---

# Safe Landing Pages

A phishing landing page should be designed for controlled testing.

It may record:

```text
Campaign ID

Timestamp

Anonymous or pseudonymous target identifier

Page visit

Approved test action
```

Avoid collecting unnecessary:

```text
Browser fingerprints

Personal information

Production passwords

Session tokens
```


---

# Landing Page Content

A safe landing page might display:

```text
Authorised Security Exercise

This page is part of an approved security awareness test.

No production credentials are required.
```

Whether this message appears immediately or after the measured action depends on the approved exercise design.


---

# Credential Submission Scenarios

Credential phishing requires additional safeguards.

The preferred approach is:

```text
Synthetic Account
      |
      v
Synthetic Password
      |
      v
Controlled Form
      |
      v
Record Event
      |
      v
Discard Password
```

Do not store real employee passwords.


---

# Synthetic Credential Example

Customer-created account:

```text
Username:
phishing.test01

Password:
Dedicated test password
```

The campaign can measure whether the test credentials are submitted without handling production authentication material.


---

# Production Credential Handling

If the landing page receives a real password unexpectedly:

```text
Do Not Display It

Do Not Reuse It

Do Not Store It in Plaintext

Stop Collection

Follow the ROE

Notify the Designated Contact

Trigger Credential Rotation if Required
```


---

# Password Logging

A safer landing page records:

```text
Credential submission attempted:
Yes
```

rather than:

```text
Password:
ActualPassword123!
```


---

# Credential Capture Model

```text
Form Submitted
      |
      v
Record Event Only
      |
      v
Discard Sensitive Value
      |
      v
Redirect / Debrief
```


---

# MFA

Modern identity environments often use MFA.

Phishing assessments should evaluate:

```text
Does MFA prevent account compromise?

Is phishing-resistant MFA deployed?

Are risky sign-ins detected?

Are users trained not to approve unexpected prompts?

Are recovery processes secure?
```


---

# MFA Safety Boundary

Do not attempt to capture or relay live MFA sessions unless that specific high-risk scenario has been explicitly approved.

Safer validation can use:

```text
Synthetic identity

Test tenant

Test authenticator

Controlled login environment
```


---

# Phishing-Resistant MFA

Examples of stronger authentication approaches include:

```text
FIDO2 security keys

Passkeys

Certificate-based authentication

Device-bound authentication
```

These can significantly reduce traditional credential-phishing risk.


---

# MFA Push Fatigue

Repeatedly generating MFA prompts can disrupt users and may cause account or security incidents.

Do not conduct MFA fatigue testing unless explicitly approved.

A tabletop or synthetic-account exercise is usually safer.


---

# Attachment-Based Phishing

Attachments can test:

```text
Secure email gateway

File-type controls

Malware scanning

Sandboxing

Mark of the Web

Office protections

Application control

EDR
```

Use harmless test artifacts whenever possible.


---

# Safe Attachment Strategy

Prefer:

```text
Plain text

PDF with test content

Benign Office document

Customer-provided test file

EICAR only for explicit antivirus validation
```

Do not send weaponised documents merely to measure attachment delivery.


---

# Attachment Test Model

```text
Test Attachment
      |
      v
Mail Gateway
      |
      v
Sandbox / AV
      |
      v
Mailbox
      |
      v
User Opens
      |
      v
Endpoint Controls
      |
      v
Telemetry
```


---

# EICAR

When antivirus validation is specifically part of the exercise, the EICAR test file can provide a standard non-malicious antivirus test.

Canonical EICAR string:

```text
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

!!! warning "Coordinate EICAR testing"
    EICAR is intentionally detected by security products. Sending it through production email can trigger gateways, antivirus, EDR and SOC workflows. Use it only when the defensive team has approved that test.


---

# Office Documents

Office-document scenarios can evaluate:

```text
Macro restrictions

Protected View

Mark of the Web

ASR

Application control

User awareness
```

Prefer harmless documents that demonstrate whether the security control is applied.

Do not embed malicious payloads simply to increase campaign success.


---

# PDF Scenarios

PDF files can be useful for safe attachment testing.

A test PDF might contain:

```text
Campaign identifier

Synthetic document content

Controlled hyperlink
```

No exploit content is required to test whether users open the document or follow the approved link.


---

# HTML Attachments

HTML attachments can redirect users to web content and may be treated differently by email security products.

If included in scope, use a harmless HTML page pointing only to the approved test environment.


---

# Archive Attachments

Security products may inspect:

```text
ZIP

7z

RAR
```

Archive testing should use benign content.

Do not use encrypted archives merely to bypass security inspection unless the specific control behaviour is the approved test objective.


---

# QR Phishing

QR phishing, sometimes called quishing, uses a QR code to direct a user to a web destination.

Potential controls include:

```text
Email image analysis

URL analysis

Mobile browser protection

DNS filtering

User awareness
```


---

# QR Test Model

```text
Email
  |
  v
QR Code
  |
  v
Mobile Device
  |
  v
Approved Landing Page
  |
  v
Telemetry
```


---

# Safe QR Testing

The QR code should resolve only to:

```text
Customer-controlled test page

Approved red team test page
```

Do not collect production credentials.


---

# QR Metrics

Possible metrics include:

```text
Messages delivered

QR scans

Landing-page visits

Reports

Time to report
```


---

# SMS Phishing

SMS phishing is commonly called smishing.

Testing may evaluate:

```text
Mobile-device awareness

URL protection

Identity controls

Reporting
```

Phone-number handling introduces additional privacy concerns.


---

# SMS Scope

Define:

```text
Approved phone numbers

Sender identity

Message volume

Sending window

Landing page

Data retention
```

Do not obtain personal phone numbers from unrelated sources simply to expand campaign reach.


---

# Collaboration Platform Phishing

Organisations may communicate through:

```text
Microsoft Teams

Slack

Google Chat

Other collaboration platforms
```

Phishing-like scenarios may test:

```text
External user indicators

Link handling

Application permissions

Reporting

Identity verification
```

Use dedicated test identities.


---

# OAuth Consent Scenarios

Some attacks attempt to convince users to authorise an application rather than submit a password.

This can bypass the traditional concept of password phishing.

Testing should use:

```text
Customer-approved test application

Minimal permissions

Synthetic or test accounts

Immediate consent revocation
```

Do not request broad production permissions merely to prove the scenario.


---

# OAuth Test Model

```text
Message
   |
   v
User Opens Link
   |
   v
Identity Provider
   |
   v
Consent Screen
   |
   v
Test Application
   |
   v
Minimal Permission
   |
   v
Audit / Detection
```


---

# OAuth Security Questions

Determine:

```text
Can users consent to arbitrary applications?

Are risky permissions restricted?

Is admin consent required?

Are publisher controls used?

Are consent events logged?

Does the SOC monitor unusual applications?
```


---

# Business Email Compromise

BEC-style scenarios focus on business processes rather than malware.

Examples include:

```text
Payment request

Supplier change

Invoice request

Sensitive document request

Executive request
```

No real payment or production financial change should occur.


---

# Safe BEC Scenario

Use:

```text
Synthetic supplier

Dummy invoice

Test payment details

Non-production workflow
```

Stop before any real transaction occurs.


---

# Finance Control Model

```text
Email Request
     |
     v
Finance Employee
     |
     v
Independent Verification
     |
     v
Secondary Approval
     |
     v
Transaction
```

The exercise should stop before the final production transaction.


---

# Email Security Gateway

A secure email gateway may inspect:

```text
Sender reputation

SPF

DKIM

DMARC

URLs

Attachments

Malware

Impersonation

Message content
```


---

# Gateway Outcome

Record:

```text
Delivered

Quarantined

Rejected

Rewritten

Attachment Removed

Warning Added
```


---

# Microsoft 365 Environments

Potential controls include:

```text
Exchange Online Protection

Microsoft Defender for Office 365

Safe Links

Safe Attachments

Anti-phishing policies

Impersonation protection

Mailbox auditing
```

Record which controls were expected to apply to the campaign.


---

# Google Workspace Environments

Potential controls include:

```text
Spam and phishing protection

Attachment scanning

Link protection

Domain authentication

Security investigation tooling

User reporting
```

Evaluate according to the customer's deployed configuration.


---

# URL Rewriting

Some email security platforms rewrite links.

Record:

```text
Original URL

Delivered URL

Security redirect

Final destination
```

Do not attempt to defeat link rewriting merely to improve campaign success.


---

# Time-of-Click Protection

Some platforms evaluate a URL when the user clicks it rather than only when the email is delivered.

This can provide protection even if the URL was initially considered safe.


---

# Browser Controls

Potential controls include:

```text
Safe Browsing

SmartScreen

Enterprise browser policy

DNS filtering

Proxy filtering

Endpoint web protection
```


---

# Endpoint Controls

Attachment and link scenarios may interact with:

```text
Microsoft Defender

EDR

ASR

AppLocker

WDAC

Office security

Browser isolation
```

See:

[Defence Evasion](defence-evasion.md)


---

# Identity Controls

Credential scenarios may interact with:

```text
MFA

Conditional Access

Risk-based authentication

Device compliance

Impossible-travel detection

Phishing-resistant authentication

Session controls
```


---

# User Reporting

A phishing campaign should measure whether employees report suspicious messages.

Possible mechanisms include:

```text
Report Phishing button

Security mailbox

Help desk

SOC hotline

Ticketing system
```


---

# Reporting Is a Positive Outcome

If a user reports the campaign:

```text
That is a successful security behaviour.
```

Do not attempt to persuade the same user again simply to produce a click.


---

# Report Button Telemetry

Where available, determine whether the report action provides:

```text
Original message

Headers

URLs

Attachments

Reporter

Timestamp
```

to the security team.


---

# Detection Validation

Phishing generates telemetry across multiple layers.

```text
Sender
  |
  v
Mail Gateway
  |
  v
Mailbox
  |
  v
User
  |
  +----------+
  |          |
  v          v
Click      Report
  |          |
  v          v
Proxy      SOC
  |
  v
Endpoint
  |
  v
Identity
  |
  v
SIEM
```


---

# Email Telemetry

Potential telemetry includes:

```text
Message trace

Sender

Recipient

Subject

Authentication results

Delivery status

URL verdict

Attachment verdict

User report
```


---

# Web Telemetry

Landing-page interactions may appear in:

```text
Proxy logs

DNS logs

Browser telemetry

Firewall logs

EDR

Web server logs
```


---

# Identity Telemetry

Credential or OAuth scenarios may generate:

```text
Authentication attempts

Risk detections

MFA events

Conditional Access decisions

Consent events

Application audit events
```


---

# Endpoint Telemetry

Attachment scenarios may generate:

```text
File creation

File open

Child processes

Defender detections

ASR events

EDR telemetry
```

Use benign content where possible.


---

# Detection Hypothesis - Link

```text
Hypothesis:
A user visiting the approved phishing simulation domain should
generate email, proxy, DNS and endpoint telemetry sufficient for
the security team to identify the event.

Test:
Send the approved link-based scenario to the pilot group.

Expected:
The email platform records delivery, web controls record the
click and the SIEM receives relevant telemetry.

Result:
Record prevention, telemetry, alerting and user reporting.
```


---

# Detection Hypothesis - Attachment

```text
Hypothesis:
Opening the approved test attachment should generate endpoint
telemetry and allow the SOC to correlate the activity with the
original phishing message.

Test:
Deliver the benign attachment scenario to approved test users.

Expected:
Email and endpoint telemetry are available for investigation.

Result:
Record visibility and response.
```


---

# Detection Hypothesis - Identity

```text
Hypothesis:
A credential-submission event involving the synthetic test
identity should be visible through identity monitoring.

Test:
Use only the dedicated synthetic account and approved landing
page.

Expected:
Relevant identity telemetry is generated without exposing
production credentials.

Result:
Record detection and response.
```


---

# Detection Outcomes

Use:

```text
Prevented

Delivered and Detected

Delivered and Logged

User Reported

User Interacted

Identity Control Prevented

Endpoint Control Prevented

No Useful Visibility
```


---

# Campaign Metrics

Possible metrics include:

```text
Messages sent

Messages delivered

Messages blocked

Messages quarantined

Messages reported

Links clicked

Landing pages visited

Synthetic submissions

Attachments opened

Identity controls triggered

Endpoint controls triggered

SOC alerts

Incident tickets
```


---

# Delivery Rate

```text
Delivered Messages / Messages Sent * 100
```


---

# Reporting Rate

```text
Users Reporting / Delivered Messages * 100
```


---

# Interaction Rate

```text
Users Interacting / Delivered Messages * 100
```

Do not interpret interaction rate alone as organisational security maturity.


---

# Time to First Report

```text
TTFR = First User Report - Campaign Start
```


---

# Time to Detection

```text
TTD = Security Alert Time - Campaign Start
```


---

# Time to Response

```text
TTR = Response Time - Detection Time
```


---

# Better Metrics

Prefer:

```text
Gateway prevention rate

User reporting rate

Median time to report

Identity-control prevention rate

Endpoint-control prevention rate

SOC detection rate

Time to triage

Time to containment
```

over click rate alone.


---

# Example Campaign Metrics

```text
Messages sent:
50

Delivered:
41

Blocked/quarantined:
9

Reported:
17

Clicked:
8

Synthetic submissions:
2

Identity control prevented:
2

SOC alerts:
3

Median time to user report:
6 minutes
```


---

# Interpret the Funnel

```text
50 Sent
   |
   v
41 Delivered
   |
   +--> 17 Reported
   |
   +--> 8 Clicked
          |
          +--> 2 Synthetic Submissions
                 |
                 v
            Identity Control
                 |
                 v
               Blocked
```

This provides much more context than:

```text
16% clicked.
```


---

# Individual Results

Avoid publishing employee leaderboards.

Do not produce:

```text
Top 10 Employees Who Failed
```

Prefer:

```text
Department-level trends

Control-level trends

Aggregate reporting rates

Process findings
```


---

# Evidence

Capture:

```text
Campaign ID

Message template

Sending time

Target population

Infrastructure

Delivery result

Gateway result

User interaction

User report

Identity result

Endpoint result

SIEM result

SOC response
```


---

# Evidence Minimisation

Avoid retaining unnecessary:

```text
Production passwords

Session tokens

Personal phone numbers

Private messages

Personal browser information
```

Store only what is necessary to support the assessment.


---

# Campaign Timeline

Example:

```text
09:00 - Campaign started
09:01 - First messages delivered
09:04 - First user report
09:07 - First click
09:08 - Proxy telemetry observed
09:09 - SOC alert generated
09:14 - Analyst triage started
09:20 - Campaign identified
09:25 - Security communication issued
10:00 - Campaign stopped
```


---

# Candidate vs Confirmed

## Candidate

```text
The organisation may permit messages from lookalike external
domains.
```


## Likely

```text
The test message reached the secure email gateway without being
rejected.
```


## Confirmed

```text
The approved phishing simulation message was delivered to 41 of
50 targeted mailboxes.
```


---

# Accurate Reporting

Avoid:

```text
Eight employees were compromised.
```

when:

```text
Eight users clicked a safe test link.
```

Prefer:

```text
Eight of 41 recipients who received the simulation visited the
approved landing page. No production credentials were collected,
and subsequent identity controls were not bypassed.
```


---

# Example Finding - Email Impersonation

```text
Title:
External Email Impersonation Controls Do Not Reliably Identify Synthetic Executive Display Names

Observation:
The authorised campaign used a customer-approved external test
domain and a synthetic executive-style display name.

The test messages were delivered without a prominent
impersonation warning to the tested recipients.

No production executive mailbox or domain was spoofed.

Impact:
An attacker may be able to create messages that appear familiar
to recipients and increase the likelihood of successful social
engineering.

Recommendation:
Review anti-phishing and impersonation-protection policies,
particularly for high-risk identities. Combine technical
controls with clear external-sender indicators and user
reporting mechanisms.
```


---

# Example Finding - Weak User Reporting

```text
Title:
Phishing Reporting Mechanism Is Not Consistently Used

Observation:
The campaign delivered 41 authorised simulation messages.

Eight recipients visited the controlled landing page, while only
three messages were reported through the organisation's
designated phishing-report mechanism during the agreed
observation period.

Impact:
Low reporting rates may delay security-team awareness of
phishing campaigns and reduce the organisation's ability to
protect other recipients.

Recommendation:
Reinforce the phishing-reporting process, ensure the reporting
mechanism is easily accessible and provide periodic scenario-
based awareness exercises.
```


---

# Example Finding - Missing SOC Correlation

```text
Title:
Phishing Link Interaction Is Logged but Does Not Generate Actionable SOC Detection

Observation:
The approved campaign generated email delivery, DNS and proxy
telemetry when users visited the controlled phishing simulation
domain.

The events were successfully ingested by the SIEM, but no
correlated alert was generated.

Impact:
An attacker may be able to interact with users through phishing
infrastructure without producing an actionable alert despite
relevant telemetry being available.

Recommendation:
Develop correlation logic combining email delivery, web
navigation, domain reputation and endpoint or identity events.
Validate the resulting detection using repeatable phishing
simulation scenarios.
```


---

# Example Positive Security Result

```text
Control:
Secure Email Gateway

Scenario:
Approved link-based phishing simulation

Result:
The gateway quarantined the message before delivery.

Telemetry:
The event was forwarded to the SIEM.

SOC:
An analyst reviewed the event and correctly identified the
campaign domain.

Conclusion:
The tested phishing message was successfully prevented and
detected.
```


---

# Root Causes

Common phishing-related weaknesses include:

```text
Weak domain authentication

Insufficient impersonation protection

Insufficient URL inspection

Weak attachment controls

Missing browser protection

Weak identity controls

Weak MFA

Weak user reporting

Missing SIEM correlation

Insufficient awareness

Weak business processes
```


---

# Remediation - Email

Consider:

```text
SPF

DKIM

DMARC

Anti-phishing policies

Impersonation protection

External sender indicators

URL protection

Attachment sandboxing

Message authentication
```


---

# Remediation - Identity

Consider:

```text
Phishing-resistant MFA

Conditional Access

Device compliance

Risk-based authentication

Restricted OAuth consent

Secure account recovery

Identity monitoring
```


---

# Remediation - Endpoint

Consider:

```text
EDR

Browser protection

Office hardening

ASR

Application control

Mark of the Web enforcement

Endpoint DLP
```


---

# Remediation - Users

Focus training on:

```text
Check sender identity

Be cautious with unexpected requests

Do not approve unexpected MFA prompts

Verify sensitive business requests independently

Report suspicious messages

Use approved reporting mechanisms
```


---

# Remediation - SOC

Consider:

```text
Mail telemetry ingestion

User-report ingestion

URL telemetry

DNS telemetry

Proxy telemetry

Endpoint telemetry

Identity telemetry

Cross-source correlation

Automated enrichment
```


---

# Campaign Debrief

After the campaign:

```text
Explain the exercise

Recognise positive reporting

Explain observed techniques

Provide practical guidance

Explain process weaknesses

Provide reporting instructions
```

Avoid humiliating participants.


---

# Immediate Training Pages

Some organisations redirect users who interact with a simulation to an awareness page.

This can provide:

```text
Immediate feedback

Recognition of warning signs

Reporting guidance
```

Whether immediate disclosure is appropriate depends on the exercise design.


---

# Delayed Debrief

A delayed debrief may be preferable when:

```text
SOC response is still being measured

Campaign remains active

Multiple waves are planned
```

The engagement plan should define when participants are informed.


---

# Cleanup

Phishing campaigns can leave substantial infrastructure and data.

Potential artifacts include:

```text
Domains

DNS records

Mailboxes

Mail server configuration

Landing pages

TLS certificates

Campaign databases

Target lists

Tracking identifiers

Test accounts

OAuth applications

Synthetic credentials
```


---

# Cleanup Inventory

Record:

| Artifact | Action |
|---|---|
| Campaign landing page | Disable/remove |
| Test mailbox | Remove or archive |
| Synthetic account | Disable/remove |
| OAuth test application | Remove |
| Test tokens | Revoke |
| Target list | Delete according to retention policy |
| Campaign database | Sanitize/delete |
| DNS records | Remove where appropriate |


---

# Domain Retirement

A red team domain should not simply be forgotten after the engagement.

Consider:

```text
Remove unnecessary DNS records

Disable campaign services

Remove mail configuration

Preserve registration if required to prevent takeover

Monitor until formally retired
```

Domain retention depends on the team's infrastructure policy.


---

# Landing Page Cleanup

Verify that campaign pages no longer accept submissions.

For example:

```text
Campaign Closed
```

may be preferable temporarily before complete removal.


---

# Credential Data Cleanup

If any sensitive authentication material was unexpectedly received:

```text
Notify authorised contact

Rotate affected credential

Revoke sessions where required

Remove retained value

Document incident

Verify deletion
```


---

# OAuth Cleanup

For test applications:

```text
Revoke consent

Remove application

Revoke tokens

Remove secrets/certificates

Verify audit trail
```


---

# Target Data Cleanup

Target lists may contain personal information.

Define:

```text
Retention period

Storage location

Encryption

Access

Deletion date
```


---

# Phishing Checklist

## Planning

- [ ] Objective defined
- [ ] Phishing explicitly authorised
- [ ] Campaign dates defined
- [ ] Target population defined
- [ ] Exclusions defined
- [ ] Sending window defined
- [ ] Scenario approved
- [ ] Sensitive pretexts excluded
- [ ] Emergency contacts defined
- [ ] Stop conditions defined
- [ ] Debrief process defined

## Infrastructure

- [ ] Domain approved
- [ ] Domain ownership recorded
- [ ] DNS configured
- [ ] SPF reviewed
- [ ] DKIM reviewed
- [ ] DMARC reviewed
- [ ] Mail infrastructure approved
- [ ] TLS configured
- [ ] Landing page approved
- [ ] Logging configured
- [ ] Infrastructure inventory maintained

## Message

- [ ] Sender identity approved
- [ ] Display name approved
- [ ] Subject approved
- [ ] Message body approved
- [ ] Link approved
- [ ] Attachment approved where applicable
- [ ] No unrelated third-party impersonation
- [ ] No harmful psychological pretext

## Landing Page

- [ ] Controlled destination used
- [ ] TLS enabled
- [ ] Production passwords not required
- [ ] Sensitive values not logged
- [ ] Tracking minimised
- [ ] Test identifiers used
- [ ] Debrief behaviour defined

## Credentials

- [ ] Synthetic account preferred
- [ ] Synthetic password used
- [ ] Real passwords not stored
- [ ] Unexpected credential procedure defined
- [ ] MFA interaction explicitly scoped
- [ ] Session tokens not collected
- [ ] Account cleanup planned

## Attachments

- [ ] Benign attachment preferred
- [ ] File type approved
- [ ] No unnecessary exploit content
- [ ] EICAR coordinated if used
- [ ] Archive testing approved
- [ ] Endpoint telemetry expected
- [ ] Attachment cleanup planned

## QR/SMS

- [ ] QR destination approved
- [ ] Phone numbers approved
- [ ] Personal numbers minimised
- [ ] Synthetic data only
- [ ] Mobile telemetry considered

## OAuth

- [ ] Test application approved
- [ ] Permissions minimised
- [ ] Test identity preferred
- [ ] Consent events monitored
- [ ] Token cleanup planned
- [ ] Application cleanup planned

## Detection

- [ ] Message trace reviewed
- [ ] Gateway result recorded
- [ ] URL telemetry reviewed
- [ ] DNS telemetry reviewed
- [ ] Proxy telemetry reviewed
- [ ] Endpoint telemetry reviewed
- [ ] Identity telemetry reviewed
- [ ] User reports reviewed
- [ ] SIEM ingestion confirmed
- [ ] SOC response recorded

## Metrics

- [ ] Messages sent recorded
- [ ] Delivery recorded
- [ ] Blocking recorded
- [ ] Reporting recorded
- [ ] Interaction recorded
- [ ] Synthetic submissions recorded
- [ ] Control prevention recorded
- [ ] Time to report recorded
- [ ] Time to detection recorded
- [ ] Time to response recorded

## Evidence

- [ ] Campaign ID recorded
- [ ] Template retained
- [ ] Infrastructure recorded
- [ ] Timestamps recorded
- [ ] Personal data minimised
- [ ] Production credentials excluded
- [ ] Evidence protected

## Cleanup

- [ ] Landing page disabled
- [ ] Test accounts removed
- [ ] Test mailboxes reviewed
- [ ] OAuth applications removed
- [ ] Tokens revoked
- [ ] Campaign data removed
- [ ] Target lists handled according to retention policy
- [ ] DNS records reviewed
- [ ] Infrastructure decommissioned
- [ ] Cleanup verified


---

# Campaign Decision Model

```text
                     OBJECTIVE
                         |
                         v
                 PHISHING REQUIRED?
                   /          \
                 No            Yes
                 |              |
                STOP            v
                        EXPLICITLY APPROVED?
                           /          \
                         No            Yes
                         |              |
                        STOP            v
                               TARGET POPULATION
                                      |
                                      v
                               APPROVED SCENARIO
                                      |
                                      v
                                TEST ACCOUNT?
                                  /       \
                                Yes        No
                                |           |
                                v           v
                              USE IT     CREDENTIAL
                                         COLLECTION
                                         REQUIRED?
                                          /     \
                                        No       Yes
                                        |         |
                                        v         v
                                     SAFE PAGE   EXPLICIT
                                                 APPROVAL
                                                    |
                                                    v
                                               SYNTHETIC
                                               CREDENTIALS
                                                    |
                         +--------------------------+
                         |
                         v
                     PILOT TEST
                         |
                         v
                      CAMPAIGN
                         |
            +------------+------------+
            |            |            |
            v            v            v
          EMAIL         USER        SECURITY
          CONTROL     REPORTING      CONTROL
            |            |            |
            +------------+------------+
                         |
                         v
                        SIEM
                         |
                         v
                     SOC RESPONSE
                         |
                         v
                       DEBRIEF
                         |
                         v
                      CLEANUP
```


---

# Defence-in-Depth Model

```text
                       PHISH
                         |
                         v
                  DOMAIN CONTROLS
                         |
                         v
                   MAIL GATEWAY
                         |
                         v
                      MAILBOX
                         |
                         v
                        USER
                         |
             +-----------+-----------+
             |                       |
             v                       v
           REPORT                   CLICK
             |                       |
             v                       v
            SOC                  WEB CONTROL
                                     |
                                     v
                                  BROWSER
                                     |
                                     v
                                  IDENTITY
                                     |
                                     v
                                  ENDPOINT
                                     |
                                     v
                                    SOC
```


---

# Phishing Maturity Model

```text
Level 1
Basic spam filtering and annual awareness

Level 2
Domain authentication and user reporting

Level 3
Advanced email, browser and identity protections

Level 4
Cross-source SIEM correlation and measured SOC response

Level 5
Phishing-resistant identity controls with continuous,
scenario-based validation
```


---

# Final Phishing Model

```text
                 AUTHORISED OBJECTIVE
                         |
                         v
                    CAMPAIGN PLAN
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       TARGETS        SCENARIO     INFRASTRUCTURE
          |              |              |
          +--------------+--------------+
                         |
                         v
                      PILOT
                         |
                         v
                     CAMPAIGN
                         |
             +-----------+-----------+
             |                       |
             v                       v
          DELIVERY                 BLOCKED
             |
             v
            USER
             |
      +------+------+----------------+
      |             |                |
      v             v                v
    REPORT         CLICK          ATTACHMENT
      |             |                |
      |             v                v
      |          BROWSER          ENDPOINT
      |             |                |
      |             v                |
      |          IDENTITY            |
      |             |                |
      +------+------+----------------+
             |
             v
          TELEMETRY
             |
             v
            SIEM
             |
             v
          DETECTION
             |
             v
          RESPONSE
             |
             v
           DEBRIEF
             |
             v
           CLEANUP
             |
             v
          REPORTING
```


---

# Core Principle

Phishing testing can be reduced to:

```text
Define the objective.

Obtain explicit authorisation.

Target only the approved population.

Use controlled infrastructure.

Use safe scenarios.

Avoid harmful pretexts.

Prefer synthetic identities.

Prefer synthetic credentials.

Do not store production passwords.

Do not capture live sessions unless explicitly approved.

Use harmless attachments where possible.

Treat user reporting as success.

Measure the entire defensive chain.

Validate email security.

Validate browser and endpoint controls.

Validate identity controls.

Validate SIEM visibility.

Measure SOC response.

Report aggregate control behaviour.

Do not shame employees.

Debrief appropriately.

Remove campaign infrastructure and sensitive data.

Retest after improvements.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Red Team Infrastructure](infrastructure.md)
- [Reconnaissance](reconnaissance.md)
- [Initial Access](initial-access.md)
- [Social Engineering](social-engineering.md)
- [Execution](execution.md)
- [Credential Access](credential-access.md)
- [Command and Control](command-and-control.md)
- [Collection](collection.md)
- [Exfiltration](exfiltration.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)

Planned:

```text
red-teaming/adversary-emulation.md
red-teaming/cleanup.md
```


---

# References

- [MITRE ATT&CK - Phishing](https://attack.mitre.org/techniques/T1566/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Spearphishing Attachment](https://attack.mitre.org/techniques/T1566/001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Spearphishing Link](https://attack.mitre.org/techniques/T1566/002/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Spearphishing via Service](https://attack.mitre.org/techniques/T1566/003/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Spearphishing Voice](https://attack.mitre.org/techniques/T1566/004/){ target="_blank" rel="noopener noreferrer" }
- [CISA - Avoiding Social Engineering and Phishing Attacks](https://www.cisa.gov/news-events/news/avoiding-social-engineering-and-phishing-attacks){ target="_blank" rel="noopener noreferrer" }
- [CISA - Implementing Phishing-Resistant MFA](https://www.cisa.gov/resources-tools/resources/implementing-phishing-resistant-mfa){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-63B - Authentication and Authenticator Management](https://pages.nist.gov/800-63-4/sp800-63b.html){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [OWASP - Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP - Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Anti-phishing Policies](https://learn.microsoft.com/defender-office-365/anti-phishing-policies-about){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Safe Links](https://learn.microsoft.com/defender-office-365/safe-links-about){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Safe Attachments](https://learn.microsoft.com/defender-office-365/safe-attachments-about){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Email Authentication](https://learn.microsoft.com/defender-office-365/email-authentication-about){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Attack Simulation Training](https://learn.microsoft.com/defender-office-365/attack-simulation-training-get-started){ target="_blank" rel="noopener noreferrer" }
- [Google Workspace - Prevent Phishing and Spoofing](https://support.google.com/a/answer/9157861){ target="_blank" rel="noopener noreferrer" }
- [DMARC](https://dmarc.org/){ target="_blank" rel="noopener noreferrer" }
- [EICAR Anti-Malware Test File](https://www.eicar.org/download-anti-malware-testfile/){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Measure the defensive chain, not just the employee"
    A useful phishing exercise evaluates message delivery, gateway controls, user reporting, browser protection, identity controls, endpoint visibility, SIEM correlation and SOC response. Click rate is only one small part of that picture.


!!! warning "Never make real credentials the objective"
    If the campaign can prove that a user attempted to submit credentials, that is normally sufficient. Production passwords, session tokens and live authentication sessions introduce unnecessary risk and should not be collected unless an exceptional scenario has been explicitly authorised and controlled.
