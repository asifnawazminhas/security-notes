---
title: Red Team Collection
description: Collection methodology for authorised red team assessments, covering objective-driven data identification, data minimisation, Windows, Linux, Active Directory, file shares, databases, email, source code, cloud and container environments, staging, evidence handling, detection validation, cleanup and reporting.
---

# Red Team Collection

Collection is the process of identifying and gathering information required to satisfy an authorised red team objective.

Collection normally occurs after discovery has identified systems, applications, repositories, shares or other locations containing potentially relevant information.

A useful distinction is:

```text
Discovery:
Where might useful information exist?

Collection:
Which specific information should be gathered?

Exfiltration:
Can authorised test information leave the controlled environment?
```

Collection should not mean:

```text
Copy everything that is accessible.
```

Instead:

```text
Objective
   |
   v
Identify Required Evidence
   |
   v
Locate Data
   |
   v
Confirm Scope
   |
   v
Minimise Collection
   |
   v
Collect
   |
   v
Protect
   |
   v
Validate Detection
   |
   v
Cleanup
```

!!! warning "Authorised testing only"
    Collection can expose confidential, personal, regulated or otherwise sensitive information. Collect only information required by the Rules of Engagement and engagement objectives. Prefer synthetic data, customer-provided marker files, metadata, counts, hashes or screenshots over copying real sensitive datasets.


---

# Collection Objectives

Typical collection objectives include:

```text
Demonstrate access to objective data

Validate access-control boundaries

Identify objective-relevant files

Demonstrate access to a business system

Validate access to selected records

Prepare synthetic data for exfiltration testing

Capture evidence of compromise

Validate DLP and monitoring controls

Measure defensive visibility
```


---

# Collection in the Attack Chain

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
Objective System
      |
      v
Collection
      |
      v
Exfiltration Validation
```

Not every engagement requires exfiltration.

Sometimes demonstrating controlled access to the target information is sufficient to prove the objective.


---

# Collection vs Discovery

Discovery might reveal:

```text
Finance share exists

Database server exists

Source repository exists

Email platform exists

Backup system exists
```

Collection asks:

```text
Which authorised information from that system is necessary to
prove the objective?
```


---

# Collection vs Credential Access

Credential Access focuses primarily on authentication material.

Examples:

```text
Passwords

Hashes

Tokens

API keys

SSH keys

Certificates
```

Collection focuses primarily on objective-relevant information.

Examples:

```text
Documents

Database records

Source code

Email

Application data

Business information
```

See:

[Credential Access](credential-access.md)


---

# Collection vs Exfiltration

Collection:

```text
Objective Data
      |
      v
Controlled Collection
      |
      v
Internal Staging
```

Exfiltration:

```text
Synthetic / Approved Data
          |
          v
     Egress Channel
          |
          v
 External Controlled System
```

Keep these as separate validation decisions.

See:

`red-teaming/exfiltration.md`


---

# Collection Planning

Before collecting anything, answer:

```text
What is the engagement objective?

What information would prove it?

Where is that information expected?

Is the source in scope?

Is the data itself in scope?

How sensitive is it?

Can synthetic data be used instead?

What is the minimum amount required?

Where will collected material be stored?

How will it be protected?

When will it be deleted?
```


---

# Collection Decision Model

```text
Potential Data
     |
     v
Objective Relevant?
   /            \
 No              Yes
 |                |
STOP              v
              In Scope?
             /        \
           No          Yes
           |            |
          STOP          v
                    Sensitive?
                    /       \
                  No         Yes
                  |           |
                  |           v
                  |      Can Metadata /
                  |      Synthetic Data
                  |      Prove Objective?
                  |        /       \
                  |      Yes        No
                  |       |          |
                  |       v          v
                  |    Minimise    Approval /
                  |                ROE Check
                  +--------+---------+
                           |
                           v
                       Collect
```


---

# Data Minimisation

Data minimisation should be the default.

Prefer:

```text
One file instead of a directory

One record instead of a table

Metadata instead of content

A count instead of records

A hash instead of a copy

A screenshot instead of a dataset

A synthetic marker instead of production information
```


---

# Minimum Necessary Evidence

Suppose the objective is:

```text
Determine whether a compromised application server can access
the finance share.
```

You may not need:

```text
All finance documents
```

A safer proof might be:

```text
Share accessible

Target directory accessible

Customer-provided marker file readable
```

That may be sufficient to prove the attack path.


---

# Synthetic Data

Synthetic data is one of the safest approaches for collection testing.

Examples:

```text
Customer-provided marker file

Dummy database record

Synthetic customer account

Test email

Non-sensitive document

Generated CSV

Random binary file
```


---

# Example Marker

A customer might create:

```text
\\fileserver\finance\redteam-objective.txt
```

with:

```text
RED TEAM OBJECTIVE - FINANCE SHARE ACCESS CONFIRMED
```

The engagement objective becomes:

```text
Demonstrate authorised read access to the marker.
```

No real finance documents need to be copied.


---

# Data Classification

Understand the organisation's classification model where available.

Possible categories include:

```text
Public

Internal

Confidential

Restricted

Highly Restricted
```

Collection handling should reflect the highest classification encountered.


---

# Sensitive Data

Potentially sensitive information includes:

```text
Personal data

Health information

Financial records

Customer information

Employee information

Authentication material

Private keys

Source code

Legal documents

Security configurations

Incident records

Business strategy

Intellectual property
```


---

# Stop Conditions

Collection should stop if unexpected high-risk information appears.

Examples:

```text
Large amounts of personal data

Medical records

Payment-card information

Production private keys

Unrelated customer information

Third-party confidential information

Out-of-scope tenant data

Unexpected regulated information
```

Record the minimum necessary evidence and follow the engagement escalation procedure.


---

# Collection Sources

Potential collection sources include:

```text
Local filesystem

Network shares

Databases

Email

Source repositories

Application storage

Cloud storage

Document platforms

Backup systems

Containers

Kubernetes

Collaboration platforms

Internal APIs
```


---

# Local System Collection

Local systems may contain objective-relevant information in:

```text
User directories

Application directories

Configuration directories

Logs

Temporary directories

Export directories

Backup directories

Mounted volumes
```


---

# Windows Filesystem Discovery

Current directory:

```powershell
Get-Location
```

Drives:

```powershell
Get-PSDrive -PSProvider FileSystem
```

Directory listing:

```powershell
Get-ChildItem -LiteralPath "C:\Path"
```

Recursive enumeration should be limited to a known authorised location:

```powershell
Get-ChildItem -LiteralPath "C:\Authorised\TestData" -File -Recurse -ErrorAction SilentlyContinue |
    Select-Object FullName,Length,LastWriteTime
```


---

# Windows Metadata Collection

Metadata may be sufficient:

```powershell
Get-Item -LiteralPath "C:\Authorised\TestData\objective.txt" |
    Select-Object FullName,Length,CreationTime,LastWriteTime
```


---

# Windows File Hash

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "C:\Authorised\TestData\objective.txt"
```

A hash can prove exactly which test artifact was accessed without repeatedly preserving duplicate copies.


---

# Windows Controlled Copy

When copying an explicitly approved test file:

```powershell
Copy-Item -LiteralPath "C:\Authorised\TestData\objective.txt" -Destination "C:\RedTeamStaging\objective.txt"
```

Verify:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "C:\RedTeamStaging\objective.txt"
```


---

# Windows File Size

```powershell
(Get-Item -LiteralPath "C:\RedTeamStaging\objective.txt").Length
```


---

# Linux Filesystem Discovery

Current directory:

```bash
pwd
```

Directory listing:

```bash
ls -la
```

Known authorised location:

```bash
find /opt/redteam-testdata -maxdepth 2 -type f -printf '%p %s bytes\n' 2>/dev/null
```

Avoid broad filesystem searches for sensitive filenames unless required by the objective.


---

# Linux Metadata

```bash
stat /opt/redteam-testdata/objective.txt
```


---

# Linux Hash

```bash
sha256sum /opt/redteam-testdata/objective.txt
```


---

# Linux Controlled Copy

```bash
mkdir -p /tmp/redteam-staging
cp /opt/redteam-testdata/objective.txt /tmp/redteam-staging/objective.txt
```

Verify:

```bash
sha256sum /tmp/redteam-staging/objective.txt
```


---

# File Content Validation

Before displaying a file's contents, consider whether metadata is sufficient.

A good progression is:

```text
File Exists
    |
    v
Metadata
    |
    v
Hash
    |
    v
Small Approved Content Sample
    |
    v
Full Copy Only If Necessary
```


---

# Network Share Collection

Network shares are common sources of business information.

Potential platforms include:

```text
Windows SMB

NFS

NAS

Distributed file services

Cloud-backed enterprise shares
```


---

# Windows SMB Shares

Local shares:

```powershell
Get-SmbShare
```

For a known authorised server:

```cmd
net view \\SERVER
```


---

# Share Access Validation

For a known authorised path:

```powershell
Test-Path "\\SERVER\Share\RedTeamObjective"
```

List only the relevant directory:

```powershell
Get-ChildItem "\\SERVER\Share\RedTeamObjective"
```


---

# Remote Marker Validation

```powershell
Get-Item "\\SERVER\Share\RedTeamObjective\marker.txt" |
    Select-Object FullName,Length,LastWriteTime
```

If reading the marker is required:

```powershell
Get-Content "\\SERVER\Share\RedTeamObjective\marker.txt"
```


---

# SMB Collection Model

```text
Share Discovered
      |
      v
In Scope?
      |
      v
Access Available?
      |
      v
Objective Directory
      |
      v
Marker / Metadata
      |
      v
Enough Evidence?
   /            \
 Yes             No
 |                |
STOP              v
             Controlled Copy
```


---

# Linux NFS

Mounted NFS resources can be identified with:

```bash
findmnt -t nfs,nfs4
```

Review only authorised mount points.


---

# Share Collection Risks

Network shares can contain:

```text
Personal information

Credentials

Backups

Deployment scripts

Financial data

Source code

HR information
```

Avoid recursively copying shares.


---

# Active Directory Collection

Active Directory itself contains valuable organisational information.

Examples:

```text
Users

Groups

Computers

Organisational Units

Trust relationships

Group Policy

Certificate infrastructure

Service accounts
```

Most of this belongs to Discovery rather than Collection.

See:

[Active Directory Enumeration](../active-directory/enumeration.md)


---

# Directory Data Minimisation

Avoid exporting the entire directory unless required.

Prefer targeted queries related to:

```text
Objective users

Objective groups

Objective computers

Relevant administrative relationships

Relevant certificate infrastructure
```


---

# BloodHound Data

BloodHound collection can generate substantial directory information.

Use collection modes appropriate to:

```text
Scope

Objective

Environment size

ROE

Detection-validation goals
```

See:

[BloodHound](../active-directory/bloodhound.md)


---

# Database Collection

Databases can contain some of the most sensitive information in an environment.

Possible data includes:

```text
Customer records

Financial information

Authentication information

Orders

Business transactions

Application configuration

Audit information
```


---

# Database Collection Principle

Prefer:

```text
Schema information

Table names

Record counts

Synthetic records

Customer-provided test records
```

over:

```text
Full production tables
```


---

# Database Validation Model

```text
Database Access
      |
      v
Objective Database?
      |
      v
Identify Relevant Table
      |
      v
Metadata / Count
      |
      v
Synthetic Record Available?
   /             \
 Yes              No
 |                 |
 v                 v
Use Test Record   Minimum Approved Sample
      |
      v
Capture Evidence
```


---

# SQL Metadata Example

A read-only query against an explicitly authorised test table might be:

```sql
SELECT COUNT(*)
FROM redteam_test_records;
```

Or:

```sql
SELECT id, test_marker
FROM redteam_test_records
WHERE id = 1;
```

Prefer customer-created test data.


---

# Avoid Full Table Exports

Avoid:

```sql
SELECT *
FROM customers;
```

when a synthetic or narrowly scoped record proves the same objective.


---

# Database Evidence

Capture:

```text
Database server

Database name

Identity

Table/object

Query purpose

Record count or test marker

Timestamp

Result

Sensitivity
```


---

# Email Collection

Email collection can expose highly sensitive communications.

Possible platforms include:

```text
Microsoft Exchange

Microsoft 365

Google Workspace

IMAP-based services

Application mailboxes
```


---

# Email Collection Objectives

Examples:

```text
Demonstrate mailbox access

Validate access to a customer-provided test message

Validate delegated mailbox permissions

Test email security monitoring
```

Avoid collecting unrelated mail.


---

# Synthetic Email

A customer can send:

```text
Subject:
RED TEAM OBJECTIVE 2026

Body:
This is an authorised red team validation message.
```

The objective can then be:

```text
Demonstrate access to this specific message.
```


---

# Email Collection Model

```text
Mailbox Access
      |
      v
Authorised Mailbox?
      |
      v
Test Message Available?
   /             \
 Yes              No
 |                 |
 v                 v
Use Test Message  Approval Required
      |
      v
Capture Minimal Evidence
```


---

# Source Code Collection

Source repositories may be high-value engagement objectives.

Possible systems include:

```text
GitHub

GitLab

Azure DevOps

Bitbucket

Internal Git servers
```


---

# Source Repository Validation

A red team objective may only require proving:

```text
Repository readable

Specific project accessible

Protected branch visible

Customer-created marker file readable
```

A complete repository clone may not be necessary.


---

# Local Git Repository

Repository status:

```bash
git status
```

Remote configuration:

```bash
git remote -v
```

Recent commits:

```bash
git log --oneline -n 10
```

Do not expose repository credentials in evidence.


---

# Repository Evidence

Prefer:

```text
Repository name

Access level

Relevant path

Marker filename

Commit identifier

Timestamp
```

instead of copying proprietary source code into the report.


---

# Application Data

Applications may expose information through:

```text
Web interfaces

APIs

Local storage

Exports

Reports

Configuration

Administrative functions
```

Collection should use the least invasive authorised interface.


---

# Application Export Functions

Applications may provide:

```text
CSV export

PDF export

Report generation

Backup export

Administrative download
```

These features can create collection paths.

Test using:

```text
Synthetic account

Synthetic records

Small result sets
```

where possible.


---

# API Collection

An API may expose objective-relevant information.

A safe approach is:

```text
Authenticate

Identify approved endpoint

Request one known test object

Record response metadata

Avoid bulk pagination
```


---

# API Evidence

Capture:

```text
Endpoint

Method

Identity

Object requested

Status code

Response size

Relevant test marker

Timestamp
```

Redact authentication tokens.


---

# Browser-Based Collection

Browsers can contain:

```text
Application sessions

Downloads

Cached documents

Bookmarks

History

Cookies
```

Browser data can be highly personal.

Only inspect browser information when explicitly relevant to the objective.


---

# Screenshots

Screen capture may sometimes be sufficient to prove access.

For example:

```text
Administrative dashboard

Objective record

Restricted application area

Test message

Test document
```

Ensure screenshots do not unintentionally capture unrelated personal information.


---

# Clipboard

Clipboard contents may contain:

```text
Text

Credentials

Commands

Business information
```

Do not routinely collect clipboard contents.

Only test clipboard collection when specifically required by the engagement scenario.


---

# Audio and Video

ATT&CK includes audio and video capture techniques.

These techniques carry significant privacy risk.

They should normally require explicit approval and a specific objective.

Prefer synthetic or controlled test environments.


---

# Keylogging and Input Capture

Input capture can expose:

```text
Passwords

Personal messages

Financial information

Sensitive business data
```

Do not deploy keylogging or similar input-capture mechanisms as routine collection.

If the scenario specifically requires validation, establish:

```text
Explicit approval

Test user

Test credentials

Limited duration

Defined application

Immediate cleanup
```


---

# Cloud Collection

Cloud environments may contain:

```text
Object storage

Databases

Secrets

Source repositories

Documents

Backups

Logs

Virtual disks

Application data
```


---

# Cloud Collection Scope

Cloud authorisation may differ by:

```text
Tenant

Account

Subscription

Project

Resource group

Bucket

Storage account

Individual object
```

Confirm the exact boundary before collection.


---

# Cloud Storage

Potential services include:

```text
Amazon S3

Azure Blob Storage

Google Cloud Storage
```

Prefer:

```text
Bucket/container metadata

Object names

Customer-provided test objects

Small synthetic files
```

over bulk downloads.


---

# Cloud Object Validation

A safe objective might be:

```text
Demonstrate that the compromised identity can read
redteam-validation.txt from the authorised storage location.
```

This avoids accessing real customer data.


---

# Cloud Database Collection

Use the same principle as on-premises databases:

```text
Metadata

Counts

Synthetic records

Minimal samples
```

Avoid database exports unless specifically required.


---

# SaaS Collection

Potential SaaS platforms include:

```text
Microsoft 365

Google Workspace

Salesforce

ServiceNow

Atlassian

GitHub

GitLab
```

SaaS environments can contain extensive organisational information.

Use:

```text
Dedicated test objects

Test users

Test projects

Test documents
```

where possible.


---

# Container Collection

Containers may contain:

```text
Application configuration

Mounted secrets

Logs

Temporary data

Application files

Mounted volumes
```

First determine whether the container itself is in scope.


---

# Container Filesystem

Basic context:

```bash
pwd
```

```bash
mount
```

```bash
findmnt
```

Mounted volumes can indicate where persistent application data resides.


---

# Kubernetes Collection

Kubernetes workloads may expose:

```text
ConfigMaps

Secrets

Volumes

Application logs

Service-account information

Application data
```

Treat Kubernetes Secrets as credential material and handle them under the appropriate credential-access controls.

Do not enumerate cluster-wide resources unless authorised.


---

# Collaboration Platforms

Potential information repositories include:

```text
SharePoint

OneDrive

Confluence

Teams

Internal wikis

Document-management systems
```

These can contain large volumes of confidential information.

Use search terms only when objective-driven and authorised.


---

# Backup Systems

Backup infrastructure may contain copies of:

```text
Servers

Databases

Documents

Configuration

Directory services

Cloud workloads
```

Backups can significantly increase the sensitivity of collection activity.

Demonstrating administrative access to the backup platform may be sufficient without restoring or downloading production backups.


---

# Security Systems

Security platforms may contain:

```text
Alerts

Incident records

Endpoint inventories

Vulnerability data

Network architecture

Credentials

Investigation notes
```

Access to security systems can itself be a high-value objective.

Avoid altering or deleting security information.


---

# Collection Through Existing Access

Prefer existing authorised access paths.

For example:

```text
Application UI

Existing share

Existing database session

Approved API

Current filesystem permissions
```

before introducing additional tooling.


---

# Automated Collection

Automation can increase both efficiency and risk.

Potential problems include:

```text
Excessive volume

Sensitive-data exposure

Performance impact

Unexpected scope expansion

Large telemetry footprint

Difficult cleanup
```


---

# Automation Decision

```text
Collection Task
      |
      v
Small / Targeted?
   /            \
 Yes             No
 |                |
 v                v
Manual        Automation Needed?
                 /       \
               No         Yes
               |           |
               v           v
             Manual      Scope Check
                            |
                            v
                       Rate / Volume Limit
                            |
                            v
                          Collect
```


---

# Collection Inventory

Maintain an inventory of collected artifacts.

Example:

| ID | Source | Artifact | Size | Classification | Purpose |
|---|---|---|---:|---|---|
| COL-001 | APP01 | `objective.txt` | 128 B | Test | Objective proof |
| COL-002 | FILE01 | Marker metadata | N/A | Test | Share validation |
| COL-003 | DB01 | Test record | 1 row | Test | Database validation |


---

# Collection Metadata

For each artifact record:

```text
Collection ID

Source host/system

Source path/object

Source identity

Timestamp

Size

Hash

Classification

Reason collected

Storage location

Retention requirement

Cleanup status
```


---

# Staging

Staging is the temporary organisation of collected material before further validation.

Example:

```text
Source
   |
   v
Collection
   |
   v
Controlled Staging
   |
   +--> Hash
   |
   +--> Inventory
   |
   +--> Evidence
   |
   v
Exfiltration Test or Cleanup
```


---

# Staging Principles

A staging location should be:

```text
Authorised

Access controlled

Temporary

Documented

Encrypted where appropriate

Easy to clean up
```


---

# Windows Staging Example

Create a dedicated test directory:

```powershell
New-Item -ItemType Directory -Path "C:\RedTeamStaging" -Force
```

Inventory:

```powershell
Get-ChildItem "C:\RedTeamStaging" -File |
    Select-Object Name,Length,LastWriteTime
```

Hash:

```powershell
Get-ChildItem "C:\RedTeamStaging" -File |
    Get-FileHash -Algorithm SHA256
```


---

# Linux Staging Example

```bash
mkdir -p /tmp/redteam-staging
chmod 700 /tmp/redteam-staging
```

Inventory:

```bash
find /tmp/redteam-staging -maxdepth 1 -type f -printf '%f %s bytes\n'
```

Hashes:

```bash
sha256sum /tmp/redteam-staging/*
```

Use a more appropriate protected location if `/tmp` does not satisfy the engagement's data-handling requirements.


---

# Archive Collected Data

ATT&CK includes:

```text
Archive Collected Data
```

as a technique because adversaries may combine data before moving it.

In an authorised assessment, archiving should only be used when required by the test plan.

For synthetic test data on Linux:

```bash
tar -czf redteam-testdata.tar.gz redteam-testdata/
```

On Windows:

```powershell
Compress-Archive -Path "C:\RedTeamStaging\TestData\*" -DestinationPath "C:\RedTeamStaging\redteam-testdata.zip"
```

Use synthetic or explicitly approved test data.


---

# Archive Hashing

Windows:

```powershell
Get-FileHash -Algorithm SHA256 "C:\RedTeamStaging\redteam-testdata.zip"
```

Linux:

```bash
sha256sum redteam-testdata.tar.gz
```


---

# Compression Ratio and Size

Record archive size because it helps correlate later network telemetry.

Windows:

```powershell
Get-Item "C:\RedTeamStaging\redteam-testdata.zip" |
    Select-Object Name,Length
```

Linux:

```bash
stat -c '%n %s bytes' redteam-testdata.tar.gz
```


---

# Encryption

Collected sensitive data may require encryption at rest.

The exact encryption method should follow:

```text
Customer policy

Engagement policy

Organisation standards

Approved tooling
```

Do not invent ad-hoc encryption procedures for customer-sensitive data.


---

# Evidence vs Collected Data

Keep these conceptually separate.

```text
Collected Data:
Material obtained during objective validation.

Evidence:
Material required to demonstrate what happened.
```

The report usually needs much less information than was technically accessible.


---

# Evidence Minimisation

Instead of embedding a sensitive document:

```text
Screenshot:
Full confidential document
```

prefer:

```text
Filename

Path

Classification

Hash

Small redacted screenshot

Access context
```


---

# Hashing Evidence

Hashing helps establish integrity.

Windows:

```powershell
Get-FileHash -Algorithm SHA256 "C:\RedTeamStaging\objective.txt"
```

Linux:

```bash
sha256sum /tmp/redteam-staging/objective.txt
```


---

# Evidence Naming

Use predictable names.

Example:

```text
COL-001-WS01-objective-file.png

COL-002-FILE01-share-access.txt

COL-003-DB01-test-record.png
```

Avoid putting customer secrets directly into filenames.


---

# Timestamps

Use consistent timestamps.

Prefer:

```text
UTC
```

Example:

```text
2026-09-05T18:42:11Z
```

Consistent time improves correlation with:

```text
EDR

SIEM

Firewall

Proxy

Cloud audit

SOC investigation
```


---

# Collection Timeline

Example:

```text
14:02 - Objective share identified
14:05 - Scope confirmed
14:08 - Marker file metadata recorded
14:10 - Marker file read
14:12 - SHA-256 recorded
14:15 - Defender/SIEM telemetry reviewed
14:20 - Temporary local copy removed
```


---

# Detection Opportunities

Collection can generate telemetry from:

```text
File access

Share access

Database queries

Process creation

PowerShell

Archive creation

Cloud object access

Email access

API activity

Large read operations

DLP
```


---

# Windows File Access Auditing

Where auditing is configured, Windows may generate object-access events.

Potential examples include:

```text
4656 - Handle to an object requested

4663 - Attempt to access an object
```

These events depend on auditing configuration and object SACLs.


---

# SMB Telemetry

Potential Windows events include:

```text
5140 - Network share accessed

5145 - Network share object checked
```

Availability depends on audit policy.


---

# Process Creation

Archive or collection utilities may appear in:

```text
4688 - New process created
```

when process creation auditing is configured.


---

# PowerShell Collection Telemetry

Potential sources include:

```text
4688

PowerShell Operational log

Script Block Logging

Module Logging

AMSI

EDR
```


---

# Linux Collection Telemetry

Potential sources include:

```text
auditd

journald

Shell telemetry

EDR

Filesystem monitoring

Network monitoring
```


---

# Database Telemetry

Databases may record:

```text
Authentication

Query history

Audit events

Export activity

Large result sets

Administrative operations
```

Detection depends on database auditing configuration.


---

# Cloud Storage Telemetry

Cloud providers can record:

```text
Authentication

Object reads

Object downloads

API operations

Role use

Source address

User agent

Timestamp
```

Ensure appropriate data-access logging is enabled where detection is an objective.


---

# Email Telemetry

Email platforms may provide:

```text
Mailbox audit

Message access

Search operations

Authentication

API activity

Administrative actions
```


---

# DLP

Data Loss Prevention controls may inspect:

```text
Sensitive content

File classification

Email

Cloud storage

Endpoint transfers

Web uploads

Removable media
```

Collection testing can help determine whether sensitive-data access is visible before exfiltration is attempted.


---

# Collection Detection Hypothesis

Example:

```text
Hypothesis:
A compromised workstation reading an unusual finance-share test
artifact should generate SMB and endpoint telemetry sufficient
for investigation.

Test:
Read a customer-provided marker from the authorised finance share.

Expected:
Share-access telemetry and endpoint activity are recorded.

Result:
Record whether telemetry, detection and analyst response occur.
```


---

# Archive Detection Hypothesis

```text
Hypothesis:
Creation of an archive containing objective-relevant test files
should be observable through endpoint telemetry.

Test:
Archive a small synthetic dataset in the approved staging location.

Expected:
Process and file-creation telemetry are generated.

Result:
Record whether the behaviour is logged or alerted.
```


---

# Detection Outcome

Classify collection tests as:

```text
Prevented

Allowed and Detected

Allowed and Logged

Allowed without Alert

No Useful Visibility
```


---

# Collection Volume

Volume matters.

Record:

```text
Number of files

Total bytes

Number of database records

Number of API requests

Number of objects

Collection duration
```

This helps compare behaviour with monitoring thresholds.


---

# Example

```text
Files:
5

Total size:
4.2 MB

Duration:
47 seconds

Endpoint telemetry:
Present

DLP alert:
Triggered

SOC alert:
Triggered after 2 minutes
```


---

# Rate and Volume Control

Do not create large collection loads merely to make detection easier.

Start small.

```text
Single Object
    |
    v
Small Dataset
    |
    v
Controlled Batch
    |
    v
Larger Simulation Only If Required
```


---

# Objective-Based Collection

Every collected artifact should answer:

```text
Why do we need this?
```

Good:

```text
This marker proves access to the finance share.
```

Poor:

```text
It looked interesting.
```


---

# Collection and OPSEC

Collection creates operational risk because collected data may become a second copy of sensitive customer information.

Controls include:

```text
Dedicated staging

Restricted access

Encryption

Inventory

Hashes

Minimal retention

Controlled transfer

Verified deletion
```

See:

[Red Team OPSEC](opsec.md)


---

# Collection and Detection Validation

Collection should also answer:

```text
Did endpoint telemetry record access?

Did file auditing record access?

Did DLP detect the activity?

Did the SIEM receive the event?

Was an alert generated?

Did the SOC investigate?

Could defenders identify the source identity?
```

See:

[Detection Validation](detection-validation.md)


---

# Collection and Reporting

A red team report should explain:

```text
What was accessible

Why it mattered

What was actually collected

How much was collected

Whether synthetic data was used

How it was protected

Whether defenders detected it

Whether it was removed
```

See:

[Red Team Reporting](reporting.md)


---

# Candidate vs Confirmed

Collection findings should use precise evidence states.

## Candidate

```text
A finance share was discovered.
```


## Likely

```text
The current identity appears to have read permission to the
finance objective directory.
```


## Confirmed

```text
The assessment identity successfully read the customer-provided
finance objective marker.
```


---

# Do Not Overstate Access

Avoid:

```text
All finance information was compromised.
```

when only:

```text
One authorised test file was accessed.
```

Instead:

```text
The assessment confirmed that the compromised identity had read
access to the tested finance share location. The assessment did
not perform bulk collection of production finance data.
```


---

# Example Finding - Sensitive Share Access

```text
Title:
Standard User Context Provides Access to Restricted Finance Share

Observation:
Following compromise of a standard workstation account, the
assessment identified a network share used by the finance
department.

The assessment account successfully accessed the authorised
red team marker within the restricted finance directory.

No production finance documents were copied.

Impact:
An attacker who compromises the same class of user account may
be able to access information stored within the affected share,
potentially exposing confidential business information.

Recommendation:
Review share and NTFS permissions, remove unnecessary group
access, implement least privilege and monitor unusual access to
sensitive file repositories.
```


---

# Example Finding - Excessive Database Access

```text
Title:
Application Identity Has Unnecessary Read Access to Restricted Database Data

Observation:
The compromised application identity could query a database
outside the data required for its normal application function.

Validation was limited to a customer-provided test record.

Impact:
Compromise of the application identity could provide an attacker
with access beyond the application's intended data boundary.

Recommendation:
Restrict database permissions to the schemas, tables and
operations required by the application. Use separate identities
for workloads with different privilege requirements.
```


---

# Example Finding - Source Repository Access

```text
Title:
Compromised Service Account Can Access Restricted Source Repository

Observation:
The assessment demonstrated that the compromised service account
could access a restricted source-code repository.

Validation was limited to repository metadata and a
customer-provided marker file.

Impact:
Compromise of the service account could expose proprietary source
code and potentially provide additional information useful for
attacking internal applications.

Recommendation:
Review repository membership, service-account permissions and
token scope. Apply least privilege and monitor unusual repository
access by non-human identities.
```


---

# Example Positive Security Result

Not every collection test should produce a vulnerability.

Example:

```text
Control:
Data Loss Prevention

Test:
A synthetic document containing customer-approved test data was
placed in the collection staging directory.

Result:
The endpoint DLP control generated an alert and the SOC correctly
identified the host, user and file involved.

Conclusion:
The tested collection activity was successfully detected.
```


---

# Root Causes

Collection-related weaknesses commonly originate from:

```text
Excessive file permissions

Excessive share permissions

Overprivileged service accounts

Weak database authorisation

Excessive API permissions

Overly broad cloud IAM

Weak repository access controls

Poor data segmentation

Insufficient DLP

Insufficient auditing

Credential reuse
```


---

# Remediation - Files and Shares

Consider:

```text
Least-privilege ACLs

Role-based access

Separate sensitive shares

Remove broad groups

Review inherited permissions

Enable appropriate auditing

Classify sensitive information

Monitor unusual access
```


---

# Remediation - Databases

Consider:

```text
Separate application identities

Least-privilege roles

Restrict schemas

Restrict tables

Restrict export functionality

Enable database auditing

Protect backups

Monitor unusual queries
```


---

# Remediation - Cloud

Consider:

```text
Least-privilege IAM

Restrict object access

Separate workloads

Use managed identities

Use short-lived credentials

Enable data-access logging

Apply DLP/classification

Monitor unusual downloads
```


---

# Remediation - Repositories

Consider:

```text
Least-privilege repository access

Short-lived tokens

Scoped automation credentials

Protected branches

Secret scanning

Audit logging

Regular membership reviews
```


---

# Cleanup

All temporary collection artifacts should be tracked and removed according to the engagement plan.

Possible artifacts include:

```text
Copied files

Archives

Temporary exports

Database exports

Screenshots

Temporary directories

Synthetic data

Cloud test objects

Temporary reports
```


---

# Windows Cleanup

Review:

```powershell
Get-ChildItem "C:\RedTeamStaging" -Force -ErrorAction SilentlyContinue
```

Remove an approved temporary staging directory after evidence requirements are satisfied:

```powershell
Remove-Item "C:\RedTeamStaging" -Recurse -Force
```

Verify:

```powershell
Test-Path "C:\RedTeamStaging"
```


---

# Linux Cleanup

Review:

```bash
find /tmp/redteam-staging -maxdepth 2 -ls 2>/dev/null
```

Remove:

```bash
rm -rf /tmp/redteam-staging
```

Verify:

```bash
test ! -e /tmp/redteam-staging && echo "Staging directory removed"
```


---

# Cleanup Verification

Record:

```text
Artifact

Original location

Staging location

Deletion performed

Deletion verified

Operator

Timestamp
```


---

# Retention

Some evidence may need to remain after technical cleanup.

Define:

```text
What evidence is retained?

Where is it stored?

Who can access it?

Is it encrypted?

When is it deleted?

Who approves deletion?
```

Follow contractual and organisational requirements.


---

# Collection Checklist

## Planning

- [ ] Collection objective defined
- [ ] Rules of Engagement reviewed
- [ ] Source system confirmed in scope
- [ ] Data itself confirmed in scope
- [ ] Data sensitivity considered
- [ ] Minimum necessary evidence identified
- [ ] Synthetic data considered
- [ ] Stop conditions understood

## Local Systems

- [ ] Relevant directories identified
- [ ] Metadata considered before content
- [ ] File hashes recorded where useful
- [ ] Broad recursive collection avoided
- [ ] Sensitive files handled appropriately

## Shares

- [ ] Share confirmed in scope
- [ ] Relevant directory identified
- [ ] Access validated minimally
- [ ] Marker file preferred
- [ ] Bulk share copy avoided
- [ ] SMB telemetry considered

## Databases

- [ ] Database confirmed in scope
- [ ] Identity recorded
- [ ] Relevant schema/table identified
- [ ] Metadata/count considered
- [ ] Synthetic record preferred
- [ ] Full-table export avoided
- [ ] Database auditing considered

## Email

- [ ] Mailbox confirmed in scope
- [ ] Test message preferred
- [ ] Unrelated email avoided
- [ ] Mailbox auditing considered
- [ ] Personal information minimised

## Source Code

- [ ] Repository confirmed in scope
- [ ] Access level recorded
- [ ] Metadata considered sufficient where possible
- [ ] Marker file preferred
- [ ] Full repository clone avoided unless required
- [ ] Proprietary code excluded from report evidence where possible

## Cloud

- [ ] Tenant/account/project scope confirmed
- [ ] Storage location confirmed
- [ ] Test object preferred
- [ ] Bulk downloads avoided
- [ ] Cloud audit logging considered
- [ ] Cross-tenant boundaries respected

## Containers

- [ ] Container confirmed in scope
- [ ] Mounted volumes identified
- [ ] Container/host boundary understood
- [ ] Kubernetes scope confirmed where relevant
- [ ] Secrets treated as credential material

## Staging

- [ ] Dedicated staging location used
- [ ] Access restricted
- [ ] Inventory maintained
- [ ] Sizes recorded
- [ ] Hashes recorded
- [ ] Encryption used where required
- [ ] Temporary archives tracked

## Detection

- [ ] Endpoint telemetry considered
- [ ] File-access telemetry considered
- [ ] SMB telemetry considered
- [ ] Database auditing considered
- [ ] Cloud audit considered
- [ ] DLP considered
- [ ] SIEM ingestion checked
- [ ] Alert status recorded
- [ ] SOC response recorded

## Evidence

- [ ] Collection IDs assigned
- [ ] Source recorded
- [ ] Identity recorded
- [ ] Timestamp recorded
- [ ] Purpose recorded
- [ ] Sensitivity recorded
- [ ] Sensitive content redacted
- [ ] Evidence integrity preserved

## Cleanup

- [ ] Temporary files removed
- [ ] Archives removed
- [ ] Temporary exports removed
- [ ] Staging directories removed
- [ ] Synthetic artifacts removed where required
- [ ] Cleanup verified
- [ ] Retained evidence documented


---

# Quick Reference - Windows

## Drives

```powershell
Get-PSDrive -PSProvider FileSystem
```


## Directory Metadata

```powershell
Get-ChildItem -LiteralPath "C:\Authorised\TestData" -File |
    Select-Object FullName,Length,LastWriteTime
```


## File Metadata

```powershell
Get-Item -LiteralPath "C:\Authorised\TestData\objective.txt" |
    Select-Object FullName,Length,CreationTime,LastWriteTime
```


## Hash

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath "C:\Authorised\TestData\objective.txt"
```


## Share Validation

```powershell
Test-Path "\\SERVER\Share\RedTeamObjective"
```


## Remote Marker

```powershell
Get-Item "\\SERVER\Share\RedTeamObjective\marker.txt" |
    Select-Object FullName,Length,LastWriteTime
```


## Create Staging

```powershell
New-Item -ItemType Directory -Path "C:\RedTeamStaging" -Force
```


## Inventory Staging

```powershell
Get-ChildItem "C:\RedTeamStaging" -File |
    Select-Object Name,Length,LastWriteTime
```


## Archive Synthetic Data

```powershell
Compress-Archive -Path "C:\RedTeamStaging\TestData\*" -DestinationPath "C:\RedTeamStaging\redteam-testdata.zip"
```


## Archive Hash

```powershell
Get-FileHash -Algorithm SHA256 "C:\RedTeamStaging\redteam-testdata.zip"
```


---

# Quick Reference - Linux

## Files

```bash
find /opt/redteam-testdata -maxdepth 2 -type f -printf '%p %s bytes\n' 2>/dev/null
```


## Metadata

```bash
stat /opt/redteam-testdata/objective.txt
```


## Hash

```bash
sha256sum /opt/redteam-testdata/objective.txt
```


## NFS Mounts

```bash
findmnt -t nfs,nfs4
```


## Create Staging

```bash
mkdir -p /tmp/redteam-staging
chmod 700 /tmp/redteam-staging
```


## Staging Inventory

```bash
find /tmp/redteam-staging -maxdepth 1 -type f -printf '%f %s bytes\n'
```


## Archive Synthetic Data

```bash
tar -czf redteam-testdata.tar.gz redteam-testdata/
```


## Archive Hash

```bash
sha256sum redteam-testdata.tar.gz
```


---

# Collection Decision Tree

```text
                     OBJECTIVE
                         |
                         v
                  DATA REQUIRED?
                    /        \
                  No          Yes
                  |            |
                 STOP          v
                         SOURCE IN SCOPE?
                           /        \
                         No          Yes
                         |            |
                        STOP          v
                             DATA IN SCOPE?
                               /        \
                             No          Yes
                             |            |
                            STOP          v
                                 SYNTHETIC DATA?
                                  /          \
                                Yes           No
                                |              |
                                v              v
                            USE SYNTHETIC   METADATA
                                             ENOUGH?
                                            /     \
                                          Yes      No
                                          |         |
                                          v         v
                                       RECORD   MINIMUM
                                       EVIDENCE COLLECTION
                                             \     /
                                              \   /
                                                v
                                             STAGING
                                                |
                                                v
                                             HASH /
                                            INVENTORY
                                                |
                                                v
                                            DETECTION
                                                |
                                                v
                                             CLEANUP
```


---

# Collection Maturity Model

```text
Level 1
Ad-hoc collection

Level 2
Objective-driven collection

Level 3
Data minimisation and inventory

Level 4
Integrated DLP and detection validation

Level 5
Synthetic-data-first adversary simulation with measurable
collection and response controls
```


---

# Defensive Collection Model

```text
                    DATA ACCESS
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
     Endpoint          Server         Cloud
        |               |               |
        v               v               v
   File Access       Database        Object Read
   Process           SMB             API
   Archive           Audit           SaaS Audit
        |               |               |
        +---------------+---------------+
                        |
                        v
                       SIEM
                        |
                        v
                  Detection / DLP
                        |
                        v
                    SOC Response
```


---

# Collection Evidence Model

```text
                  Objective
                      |
                      v
                 Data Source
                      |
                      v
                 Scope Check
                      |
                      v
                 Minimal Data
                      |
                      v
              Controlled Staging
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
        Hash       Metadata     Evidence
          |           |           |
          +-----------+-----------+
                      |
                      v
                 Detection Test
                      |
                      v
                    Cleanup
```


---

# Final Collection Model

```text
                      OBJECTIVE
                          |
                          v
                       DISCOVERY
                          |
                          v
                    DATA LOCATION
                          |
                          v
                       IN SCOPE
                          |
                          v
                   DATA MINIMISATION
                          |
             +------------+------------+
             |                         |
             v                         v
        SYNTHETIC DATA             REAL DATA
             |                         |
             |                         v
             |                  MINIMUM NECESSARY
             |                         |
             +------------+------------+
                          |
                          v
                       COLLECT
                          |
                          v
                       STAGING
                          |
             +------------+------------+
             |            |            |
             v            v            v
           HASH       INVENTORY     PROTECT
             |            |            |
             +------------+------------+
                          |
                          v
                     TELEMETRY
                          |
                          v
                      DETECTION
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

Collection can be reduced to:

```text
Know the objective.

Identify only the data required to prove it.

Confirm both the system and data are in scope.

Prefer synthetic data.

Prefer metadata before content.

Prefer one record before a dataset.

Avoid bulk collection.

Protect anything collected.

Inventory every artifact.

Hash important evidence.

Use consistent timestamps.

Validate endpoint, server, cloud and DLP visibility.

Do not confuse accessibility with permission to collect.

Stop when sufficient evidence exists.

Remove temporary artifacts.

Retain only the evidence required for reporting.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Discovery](discovery.md)
- [Credential Access](credential-access.md)
- [Privilege Escalation](privilege-escalation.md)
- [Lateral Movement](lateral-movement.md)
- [Command and Control](command-and-control.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)
- [Active Directory](../active-directory/)
- [Active Directory Shares](../active-directory/shares.md)
- [BloodHound](../active-directory/bloodhound.md)


---

# References

- [MITRE ATT&CK - Collection](https://attack.mitre.org/tactics/TA0009/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Archive Collected Data](https://attack.mitre.org/techniques/T1560/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Automated Collection](https://attack.mitre.org/techniques/T1119/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Data from Information Repositories](https://attack.mitre.org/techniques/T1213/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Data from Local System](https://attack.mitre.org/techniques/T1005/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Data from Network Shared Drive](https://attack.mitre.org/techniques/T1039/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Email Collection](https://attack.mitre.org/techniques/T1114/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Screen Capture](https://attack.mitre.org/techniques/T1113/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Clipboard Data](https://attack.mitre.org/techniques/T1115/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Input Capture](https://attack.mitre.org/techniques/T1056/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Audio Capture](https://attack.mitre.org/techniques/T1123/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Audit File System](https://learn.microsoft.com/windows/security/threat-protection/auditing/audit-file-system){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Audit File Share](https://learn.microsoft.com/windows/security/threat-protection/auditing/audit-file-share){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Advanced Security Audit Policy Settings](https://learn.microsoft.com/windows/security/threat-protection/auditing/advanced-security-audit-policy-settings){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Proof is more important than volume"
    If one synthetic record, marker file, hash or screenshot proves that the security boundary has been crossed, collecting thousands of production records usually adds risk without materially improving the finding.


!!! warning "Access does not equal permission to collect"
    A compromised identity may technically be able to access large amounts of sensitive information. That does not mean the red team should copy it. Follow the Rules of Engagement, minimise collection and stop once sufficient evidence has been obtained.
