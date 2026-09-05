---
title: Red Team OPSEC
description: Operational security for authorised red team assessments, covering engagement separation, operator workstations, identities, infrastructure, credentials, secrets, metadata, communications, evidence, browser isolation, repositories, logging, cloud resources, data handling, cleanup, and incident response.
---

# Red Team OPSEC

Operational security, or OPSEC, is the discipline of preventing information about an assessment from being accidentally exposed, mixed between engagements, lost, or disclosed to unauthorised parties.

In an authorised red team engagement, OPSEC is primarily about protecting:

```text
Customer information
Assessment credentials
Operator identities
Assessment infrastructure
Payloads and test artifacts
Evidence
Reports
Attack-path information
Internal network information
Cloud resources
Communication channels
```

A useful model is:

```text
                 RED TEAM OPSEC
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
     PEOPLE         SYSTEMS          DATA
        |              |              |
        +--------------+--------------+
                       |
                       v
                   PROCESS
                       |
                       v
                  ENGAGEMENT
                    SAFETY
```

Good OPSEC should make the engagement easier to control, investigate, reproduce, and clean up.

!!! warning "Authorised testing only"
    OPSEC does not expand the authorised scope of an assessment. It should protect customer information and assessment operations, not be used to conceal unauthorised activity. Rules of Engagement, legal authorisation, customer safety, and stop conditions always take priority.


---

# OPSEC Objectives

The primary objectives are:

```text
Prevent cross-client data exposure

Prevent credential leakage

Protect assessment infrastructure

Protect evidence

Separate operator identities

Prevent accidental out-of-scope activity

Maintain reliable attribution of assessment actions

Prevent uncontrolled payload distribution

Maintain an accurate infrastructure inventory

Support incident investigation

Support complete cleanup
```


---

# OPSEC Threat Model

Before an engagement, consider what could go wrong.

```text
                     Engagement
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
  Data Leakage     Infrastructure      Human Error
                       Exposure
       |                 |                 |
       v                 v                 v
Credentials        Admin Interface     Wrong Target
Evidence           Public Storage      Wrong Client
Reports            Weak Access         Wrong Account
Client Data        Stale Services      Wrong Payload
```


---

# OPSEC Is More Than Stealth

Red team OPSEC should not be reduced to:

```text
Avoid detection.
```

A broader model is:

```text
Operational Security
        |
        +--> Customer confidentiality
        |
        +--> Engagement isolation
        |
        +--> Infrastructure security
        |
        +--> Credential protection
        |
        +--> Evidence integrity
        |
        +--> Operator accountability
        |
        +--> Scope enforcement
        |
        +--> Cleanup
```

Detection by the customer's security team may actually be a desired assessment outcome.


---

# OPSEC Lifecycle

```text
Preparation
    |
    v
Environment Isolation
    |
    v
Infrastructure Deployment
    |
    v
Operational Testing
    |
    v
Continuous Logging
    |
    v
Evidence Handling
    |
    v
Cleanup
    |
    v
Infrastructure Destruction
    |
    v
Credential Revocation
    |
    v
Archive / Retention
```


---

# Engagement Separation

One of the most important OPSEC controls is strict separation between engagements.

Avoid:

```text
Client A files
      +
Client B credentials
      +
Client C infrastructure
      +
Personal projects
```

inside the same uncontrolled environment.

Prefer:

```text
Operator Device
     |
     +--> Engagement A Workspace
     |
     +--> Engagement B Workspace
     |
     +--> Training / Lab Workspace
```

Each workspace should have clearly separated:

```text
Credentials
Notes
Evidence
Infrastructure
Browser state
SSH configuration
VPN configuration
Payloads
Reports
Cloud resources
```


---

# Engagement Identifier

Assign each engagement a unique identifier.

Example:

```text
RT-2026-001
RT-2026-002
PT-2026-001
```

Use the identifier consistently for:

```text
Directories
Infrastructure
Evidence
Screenshots
Cloud tags
Operator logs
DNS records
Reports
Tickets
Cleanup records
```


---

# Directory Structure

Example:

```text
engagements/
└── RT-2026-001/
    ├── scope/
    ├── notes/
    ├── recon/
    ├── evidence/
    ├── screenshots/
    ├── hashes/
    ├── infrastructure/
    ├── payloads/
    ├── logs/
    ├── reports/
    └── cleanup/
```

Do not store unnecessary customer data simply because a directory exists for it.


---

# File Naming

Use predictable names.

Example:

```text
YYYYMMDD-HHMM-host-technique-description.ext
```

Example:

```text
20260905-1430-WS01-applocker-policy.txt
```

Screenshot:

```text
20260905-1435-WS01-defender-status.png
```

Network evidence:

```text
20260905-1440-WS01-SRV01-connectivity.txt
```


---

# Operator Workstation

The operator workstation should be treated as security-sensitive infrastructure.

Protect it with:

```text
Full-disk encryption
Strong authentication
Automatic screen locking
Current security updates
Minimal unnecessary software
Secure browser configuration
Protected SSH keys
Protected VPN credentials
Encrypted evidence
Backups where appropriate
Endpoint security
```


---

# Dedicated Assessment Environment

Where practical, use a dedicated environment for assessment work.

Options include:

```text
Dedicated workstation
Virtual machine
Cloud workstation
Disposable VM
Separate user profile
Container for selected tooling
```

The choice depends on:

```text
Engagement sensitivity
Customer requirements
Tool compatibility
Data-handling policy
Isolation requirements
```


---

# Virtual Machine Separation

A simple model:

```text
Host Workstation
      |
      +--> Client-A VM
      |
      +--> Client-B VM
      |
      +--> Lab VM
```

Avoid sharing unnecessary:

```text
Clipboard
Folders
Browser profiles
SSH agents
Credentials
Cloud sessions
VPN connections
```

between environments.


---

# VM Snapshots

Snapshots can provide useful rollback points.

Example:

```text
Clean OS
   |
   v
Tools Installed
   |
   v
Pre-Engagement Snapshot
   |
   v
Assessment
   |
   v
Archive Required Evidence
   |
   v
Destroy / Revert
```

Be careful: snapshots can contain credentials and customer information.


---

# Operator Identity

Separate:

```text
Personal identity
Corporate identity
Customer-provided identity
Assessment identity
Infrastructure identity
```

Do not use personal accounts for customer assessment infrastructure unless specifically required and approved.


---

# Customer-Provided Accounts

Customer-provided identities should be documented.

Example:

| Account | Purpose | Privilege | Owner | Expiry |
|---|---|---|---|---|
| `rt-user01` | Assumed breach | Standard user | Customer | Engagement end |
| `rt-admin01` | Recovery only | Admin | Customer | Engagement end |

Track:

```text
Account
Purpose
Privilege
Systems
Credential owner
MFA
Creation time
Expiration
Revocation
```


---

# Least Privilege

Assessment infrastructure should also follow least privilege.

Do not give every operator:

```text
Root
Cloud Owner
DNS Administrator
Repository Administrator
Billing Administrator
```

unless required.

Prefer:

```text
Operator
    |
    v
Required Role
    |
    v
Required Resource
```


---

# Privileged Infrastructure Access

Administrative interfaces should be reachable only through controlled management paths.

Example:

```text
Operator
   |
   v
VPN / Bastion
   |
   v
Management Network
   |
   v
Team Server
```

Avoid:

```text
Internet
   |
   v
Public Administrative Interface
```


---

# Infrastructure Inventory

Maintain an inventory from the beginning.

Example:

| ID | Type | Address | Provider | Purpose | Owner | Status |
|---|---|---|---|---|---|---|
| RT01 | VPS | `203.0.113.10` | Provider | Edge | OP01 | Active |
| RT02 | VPS | Private | Provider | Management | OP01 | Active |
| RTDNS01 | Domain | `example.test` | Registrar | Assessment | OP02 | Active |


---

# Infrastructure Lifecycle

Every resource should move through a lifecycle.

```text
Requested
    |
    v
Created
    |
    v
Configured
    |
    v
Validated
    |
    v
Active
    |
    v
Retired
    |
    v
Destroyed
    |
    v
Verified
```


---

# Cloud Resource Tags

Use provider tagging where supported.

Example:

```text
Engagement=RT-2026-001
Owner=RedTeam
Purpose=Assessment
Expiry=2026-09-30
```

This helps identify forgotten resources.


---

# Resource Expiration

Every temporary resource should have an expected expiration.

Track:

```text
VPS
Domains
Certificates
API tokens
Storage
DNS
VPN users
Temporary accounts
Cloud roles
```

An engagement should not leave forgotten infrastructure running indefinitely.


---

# Infrastructure Hardening

Assessment servers should be hardened like other Internet-facing systems.

Typical controls:

```text
Patch operating system
Restrict administrative access
Use SSH keys
Disable unnecessary services
Use host firewall
Use MFA at provider
Protect API tokens
Monitor authentication
Enable logging
Synchronise time
Back up required configuration
```


---

# Linux Baseline

For Debian/Ubuntu-based infrastructure:

```bash
sudo apt update
```

Apply approved updates according to the engagement environment:

```bash
sudo apt upgrade
```

Review listening services:

```bash
sudo ss -lntup
```

Review firewall:

```bash
sudo ufw status verbose
```

Review failed services:

```bash
systemctl --failed
```


---

# Remote Administration Safety

Before modifying a remote firewall:

```text
1. Confirm the current SSH connection.

2. Confirm the management source address.

3. Permit the required administrative path.

4. Validate the rule.

5. Only then enable restrictive firewall policy.

6. Keep a second administrative session available during validation.
```

This reduces the chance of locking yourself out.


---

# SSH Key Generation

Generate a dedicated key where appropriate:

```bash
ssh-keygen -t ed25519 -a 100
```

Use meaningful filenames:

```text
~/.ssh/rt-2026-001-management
```

Never share the private key.


---

# SSH Key Permissions

Linux:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/rt-2026-001-management
```

Public key:

```bash
chmod 644 ~/.ssh/rt-2026-001-management.pub
```


---

# SSH Configuration

A local SSH configuration can help prevent using the wrong identity.

Example:

```text
Host rt-2026-001-edge
    HostName 203.0.113.10
    User operator
    IdentityFile ~/.ssh/rt-2026-001-management
    IdentitiesOnly yes
```

This reduces accidental key selection.


---

# Verify SSH Server Configuration

Before reloading configuration:

```bash
sudo sshd -t
```

If validation succeeds, reload the appropriate service for the distribution.

On many Debian/Ubuntu systems:

```bash
sudo systemctl reload ssh
```

Maintain an existing session until the new connection has been tested.


---

# SSH Hardening

Typical settings may include:

```text
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
```

Do not disable password authentication until key-based access has been successfully tested.


---

# Firewall Principles

Expose only required services.

Example:

```text
Internet
   |
   +--> HTTPS
   |
   X--> SSH
   |
   X--> Administrative UI
```

Management traffic:

```text
Approved Operator IP / VPN
           |
           +--> SSH
           |
           +--> Administrative UI
```


---

# UFW Baseline

Example:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

Allow SSH before enabling the firewall:

```bash
sudo ufw allow OpenSSH
```

Then:

```bash
sudo ufw enable
```

Review:

```bash
sudo ufw status verbose
```

Use more restrictive source-based rules where practical.


---

# Management Plane Separation

Separate operator management traffic from assessment traffic.

```text
                   Operator
                      |
                      v
               Management Plane
                      |
                      v
                  Backend
                      |
                      v
                Assessment Edge
                      |
                      v
                    Target
```

This improves:

```text
Access control
Logging
Troubleshooting
Cleanup
Infrastructure security
```


---

# DNS OPSEC

Domains used for assessments should be managed carefully.

Track:

```text
Registrar
Account
MFA
Nameservers
DNS provider
Records
Purpose
Expiration
Engagement
```


---

# DNS Inventory

Example:

| Name | Type | Value | Purpose |
|---|---|---|---|
| `edge.example.test` | A | `203.0.113.10` | Assessment edge |
| `files.example.test` | A | `203.0.113.20` | Controlled hosting |
| `www.example.test` | CNAME | `edge.example.test` | Web endpoint |


---

# DNS Record Types

Common records:

| Record | Purpose |
|---|---|
| A | IPv4 address |
| AAAA | IPv6 address |
| CNAME | Alias |
| MX | Mail |
| TXT | Text/policy data |
| NS | Nameserver |


---

# DNS Validation

```bash
dig example.test
```

Specific record:

```bash
dig A example.test
```

Nameservers:

```bash
dig NS example.test
```

TXT:

```bash
dig TXT example.test
```


---

# DNS Cleanup

At engagement completion:

```text
Remove temporary records
Remove stale subdomains
Remove mail records if temporary
Remove verification records
Remove unused nameserver delegations
Document retained records
Verify resolution
```


---

# Domain Safety

Avoid unnecessary brand impersonation.

Domain naming and social-engineering infrastructure should follow explicit customer approval.

Consider:

```text
Customer trademark
Third-party trademark
Registrar policy
Provider terms
Engagement scope
Social-engineering authorisation
```


---

# TLS

Use TLS for administrative and assessment services where appropriate.

Benefits include:

```text
Transport confidentiality
Server authentication
Integrity
Reduced accidental credential exposure
```


---

# TLS Validation

Inspect:

```bash
openssl s_client -connect example.test:443 -servername example.test
```

Basic HTTPS validation:

```bash
curl -I https://example.test/
```


---

# Certificate Inventory

Track:

```text
Certificate
Hostname
Issuer
Private-key location
Creation
Expiration
Renewal
Revocation
```


---

# Private Keys

Private keys should never be stored in:

```text
Public Git repositories
Shared chat
Public storage
Unencrypted evidence
Screenshots
Issue trackers
Documentation repositories
```

Protect file permissions and access.


---

# Secrets Management

Assessment secrets may include:

```text
SSH keys
VPN credentials
API tokens
Cloud credentials
DNS tokens
C2 credentials
Customer accounts
Certificates
Repository tokens
Passwords
```


---

# Secret Storage

Prefer:

```text
Password manager
Secret vault
Protected environment
Encrypted credential store
```

Avoid:

```text
notes.txt
passwords.txt
Desktop files
Public repositories
Shell scripts
Chat history
Screenshots
```


---

# Environment Variables

Environment variables may be useful for temporary automation but are not automatically secure.

They may be exposed through:

```text
Process inspection
Debug output
Shell history
Crash information
CI/CD logs
Child processes
```

Do not treat environment variables as a replacement for proper secret management.


---

# Shell History

Be aware that commands may be stored in shell history.

Linux:

```bash
history
```

PowerShell:

```powershell
Get-History
```

PSReadLine history may also persist separately.

Do not type sensitive credentials directly into commands where avoidable.


---

# Git Repository OPSEC

Repositories can accidentally expose:

```text
Credentials
API keys
Internal domains
Customer IP addresses
Screenshots
Payloads
Reports
Private keys
Environment files
```


---

# Repository Separation

Prefer:

```text
Public Notes Repository
        |
        X
        |
Customer Engagement Repository
```

Never use the public notes repository as an engagement evidence store.


---

# .gitignore

Common exclusions may include:

```gitignore
.env
.env.*
*.key
*.pem
*.pfx
*.p12
credentials/
secrets/
evidence/
screenshots/
customer-data/
```

A `.gitignore` prevents new accidental additions but does not remove secrets already committed.


---

# Check Git Status

Before committing:

```bash
git status
```

Review the actual diff:

```bash
git diff
```

Review staged content:

```bash
git diff --cached
```


---

# Secret Scanning

Where available, use repository secret-scanning capabilities.

The goal is to detect:

```text
API tokens
Cloud keys
Private keys
Passwords
Authentication tokens
```

before they leave the controlled environment.


---

# Committed Secret Response

If a secret is committed:

```text
Do not assume deleting the file fixes the issue.
```

Treat the secret as potentially compromised.

Response:

```text
Revoke
    |
    v
Rotate
    |
    v
Remove from active repository
    |
    v
Assess history exposure
    |
    v
Clean history where required
    |
    v
Verify
```


---

# Browser OPSEC

Browsers can mix identities through:

```text
Cookies
Saved passwords
Autofill
History
Extensions
Cloud sync
SSO sessions
Downloads
Certificates
```


---

# Browser Profiles

Use separate browser profiles where appropriate.

Example:

```text
Browser
   |
   +--> Corporate
   |
   +--> Engagement RT-2026-001
   |
   +--> Engagement RT-2026-002
   |
   +--> Research
```

Do not enable personal browser synchronisation inside an assessment profile.


---

# Browser Extensions

Review extensions before using a browser for sensitive assessment work.

Extensions may have permission to read:

```text
Page content
URLs
Clipboard
Downloads
Authentication data
```

Use the minimum required set.


---

# Cookies and Sessions

Customer authentication sessions are sensitive.

After an engagement:

```text
Log out
Revoke test sessions where possible
Clear engagement browser data
Remove customer certificates
Remove saved credentials
Destroy disposable profiles
```


---

# VPN Separation

Before connecting to a customer VPN, understand:

```text
Routes
DNS changes
Split tunnelling
Default gateway
Accessible networks
Excluded networks
Local network behaviour
```

A VPN may alter the operator's routing unexpectedly.


---

# Route Validation

Linux:

```bash
ip route
```

Windows:

```powershell
route print
```

Record routes before and after connecting to a customer network if network isolation is important.


---

# DNS After VPN Connection

Linux:

```bash
resolvectl status
```

Windows:

```powershell
ipconfig /all
```

This helps identify DNS changes introduced by the VPN.


---

# Scope Enforcement

Do not rely on memory to determine which targets are authorised.

Maintain machine-readable scope where possible.

Example:

```text
scope/
├── domains.txt
├── ips.txt
├── excluded-ips.txt
├── urls.txt
└── notes.md
```


---

# Scope Before Action

Use the mental model:

```text
Target
  |
  v
In Scope?
 /     \
No     Yes
|       |
STOP    v
     Technique
       Allowed?
      /      \
     No      Yes
     |        |
    STOP      v
           Execute
```


---

# Out-of-Scope Discovery

If an apparently related system is discovered but is not explicitly in scope:

```text
Discover
   |
   v
Record
   |
   v
Do Not Test
   |
   v
Request Clarification
```

Do not infer authorisation from ownership or naming.


---

# Third-Party Services

Modern organisations rely heavily on third parties.

Examples:

```text
CDN
SaaS
Cloud provider
Email provider
Payment processor
Identity provider
Managed service
Hosting provider
```

Customer authorisation does not automatically provide permission to test third-party infrastructure.


---

# Payload Management

Assessment payloads and binaries should be controlled.

Track:

```text
Filename
Purpose
Hash
Source
Build date
Target
Deployment location
Cleanup status
```


---

# Payload Hashing

Linux:

```bash
sha256sum file
```

Windows:

```powershell
Get-FileHash .\file.exe -Algorithm SHA256
```

Record the hash in operator notes.


---

# Payload Inventory

Example:

| File | SHA-256 | Purpose | Host | Status |
|---|---|---|---|---|
| `assessment-test.exe` | `...` | Controlled validation | WS01 | Removed |
| `test-script.ps1` | `...` | Detection test | WS02 | Removed |


---

# Controlled File Hosting

Assessment file hosting should avoid accidental public exposure.

Prefer:

```text
Authentication
Source restrictions
Non-indexed locations
Minimal retention
Logging
Explicit file inventory
```

Avoid open directory listing unless there is a specific reason.


---

# Temporary Hosting

Concept:

```text
Operator
    |
    v
Controlled File Server
    |
    v
Authorised Target
```

After the test:

```text
Remove artifact
Stop server if unnecessary
Archive required logs
Verify no unrelated downloads occurred
```


---

# Cloud Storage

Do not use public storage buckets for sensitive assessment artifacts.

Prefer:

```text
Private storage
Restricted identities
Encryption
Short retention
Access logging
Lifecycle rules
```


---

# Signed URLs

Temporary signed URLs may reduce the need for permanently public files.

However:

```text
Signed URL = Temporary Credential
```

Protect it accordingly.


---

# Payload Cleanup

After a test:

```text
Target file
Assessment server copy
Temporary web copy
Cloud storage copy
Operator working copy
```

should each have an intentional retention or deletion decision.


---

# C2 OPSEC

Command-and-control infrastructure is security-sensitive.

Administrative access should be separated from target-facing communication.

```text
Operator
   |
   v
Management Channel
   |
   v
C2 Server
   |
   v
Assessment Channel
   |
   v
Authorised Endpoint
```

See:

[Command and Control](command-and-control.md)


---

# C2 Administrative Interfaces

Do not expose administrative interfaces unnecessarily.

Protect with:

```text
VPN
IP allowlisting
Strong authentication
TLS
Firewall
Separate management interface
```


---

# C2 Credentials

Treat C2 credentials as privileged infrastructure secrets.

Use:

```text
Unique credentials
Strong authentication
Per-engagement access
Credential rotation
Access removal after engagement
```


---

# C2 Logging

Where supported, retain useful operational records such as:

```text
Operator
Session
Host
Timestamp
Action
Result
```

This helps answer:

```text
Who performed the action?

When?

Against which system?

Why?
```


---

# Pivoting OPSEC

Pivoting changes network reachability.

Examples include:

```text
Ligolo-ng
Chisel
SSH forwarding
SOCKS
VPN
```

Every pivot should have:

```text
Purpose
Operator
Pivot host
Reachable network
Routes
Start time
Stop time
Cleanup
```


---

# Pivot Scope Risk

A pivot may expose networks that were not previously reachable.

```text
Operator
    |
    v
Pivot
    |
    +--> In-Scope Network
    |
    +--> Out-of-Scope Network
```

Do not assume every network reachable through a compromised host is authorised.


---

# Route Inventory

Before pivoting:

```text
Known Scope
    |
    v
Required Network
    |
    v
Route Added
    |
    v
Validation
```

After testing:

```text
Remove Route
    |
    v
Stop Tunnel
    |
    v
Remove Agent
    |
    v
Verify
```


---

# Ligolo-ng Cleanup

When Ligolo-ng has been used, verify:

```text
Agent process terminated
Proxy stopped
Tunnel interface removed
Routes removed
Temporary files removed
Firewall changes restored
```


---

# Chisel Cleanup

Verify:

```text
Client stopped
Server stopped
Listeners removed
Temporary binaries removed
Service definitions removed if created
Logs handled according to policy
```


---

# SSH Tunnel Cleanup

Confirm no unexpected forwarding remains.

Linux:

```bash
ps aux | grep '[s]sh'
```

Review listening sockets:

```bash
ss -lntp
```


---

# Evidence OPSEC

Evidence can be more sensitive than the tools used to collect it.

Evidence may contain:

```text
Credentials
Hostnames
IP addresses
Usernames
Internal URLs
Source code
Configuration
Customer data
Screenshots
Attack paths
Security-control details
```


---

# Evidence Minimisation

Collect only what is necessary to demonstrate the finding.

Prefer:

```text
Relevant lines
       |
       v
Context
       |
       v
Proof
```

instead of:

```text
Entire database
Entire mailbox
Entire filesystem
```


---

# Screenshot Review

Before including a screenshot, check for:

```text
Passwords
Tokens
Personal data
Other customer tabs
Personal bookmarks
Notifications
Chat windows
Internal URLs
Unrelated terminals
Browser account details
```


---

# Screenshot Cropping

Cropping can reduce unnecessary disclosure, but preserve enough context to make the evidence meaningful.

Do not manipulate evidence in a way that changes its meaning.


---

# Evidence Integrity

For important files, calculate a hash.

Linux:

```bash
sha256sum evidence.bin
```

Windows:

```powershell
Get-FileHash .\evidence.bin -Algorithm SHA256
```


---

# Evidence Manifest

Example:

```text
evidence/
├── 001-defender-status.txt
├── 002-applocker-policy.txt
├── 003-network-test.txt
└── SHA256SUMS
```

Generate on Linux:

```bash
sha256sum evidence/* > SHA256SUMS
```

Ensure the output file itself is not unintentionally included in a recursive hashing workflow.


---

# Encryption

Sensitive evidence should be encrypted at rest and in transit according to customer and organisational requirements.

Protect:

```text
Operator laptop
External storage
Cloud storage
Backups
Report drafts
Evidence archives
```


---

# Data Classification

A useful assessment classification may include:

```text
Public
Internal
Confidential
Highly Sensitive
Credential Material
```

Follow the customer's classification requirements when provided.


---

# Personal Data

Avoid collecting personal data unless required for the assessment.

If encountered:

```text
Minimise access
Do not copy unnecessarily
Do not include unnecessarily in screenshots
Follow retention policy
Follow legal requirements
```


---

# Credential Evidence

A finding normally does not require publishing the full credential.

Instead of:

```text
Password: SuperSecretPassword123!
```

use:

```text
A valid credential for the affected account was obtained during
the authorised assessment. The credential has been omitted from
the report.
```


---

# Hash Evidence

Similarly, avoid placing reusable authentication material directly in reports.

Use:

```text
Credential material was successfully accessed and validated
against the authorised target.
```

Store the sensitive artifact separately only when required.


---

# Report OPSEC

Reports often contain:

```text
Attack paths
Credentials
Network architecture
Security weaknesses
Screenshots
Internal hostnames
Sensitive recommendations
```

Treat draft reports as confidential assessment data.


---

# Report Distribution

Maintain an approved recipient list.

Example:

```text
Customer Engagement Lead
Security Lead
Authorised Technical Contacts
```

Avoid forwarding reports through uncontrolled channels.


---

# Communications

Define approved communication channels before testing.

Examples:

```text
Corporate email
Customer ticketing system
Approved secure chat
Emergency telephone
Project platform
```

Do not use personal messaging accounts for sensitive engagement data unless explicitly approved.


---

# Emergency Communication

Operators should know:

```text
Who to contact

How to contact them

When to stop

How to identify the engagement

How to describe the affected system

How to preserve evidence
```


---

# Emergency Message Structure

```text
Engagement:
RT-2026-001

Time:
2026-09-05 18:42 UTC

System:
WS01

Observation:
Unexpected production instability following authorised test.

Action:
Testing stopped.

Current State:
No further activity being performed.

Contact:
OP01
```


---

# Operational Logging

Maintain an operator timeline.

Example:

| Time | Operator | Source | Target | Action | Result |
|---|---|---|---|---|---|
| 10:00 | OP01 | RT01 | WS01 | Connectivity test | Success |
| 10:12 | OP01 | WS01 | WS01 | Enumeration | Success |
| 10:31 | OP02 | WS01 | SRV01 | Authentication validation | Blocked |


---

# Operator Accountability

Shared accounts make investigation difficult.

Prefer:

```text
OP01
OP02
OP03
```

over:

```text
redteam
```

for management access where practical.


---

# Command Logging

Important assessment commands should be recorded.

The objective is:

```text
Reproducibility
Accountability
Evidence
Cleanup
Troubleshooting
```

not indiscriminate collection of every terminal keystroke.


---

# Terminal Separation

A common source of mistakes is using the wrong terminal.

Use obvious visual or naming separation.

Example:

```text
[CLIENT-A]
[CLIENT-B]
[LAB]
[INFRA]
```

Terminal titles, tmux sessions, or dedicated workspaces can help.


---

# tmux Sessions

Example:

```bash
tmux new -s rt-2026-001
```

List:

```bash
tmux ls
```

Attach:

```bash
tmux attach -t rt-2026-001
```

Avoid placing secrets in session names.


---

# Working Directory Check

Before running an engagement command:

```bash
pwd
```

Repository:

```bash
git status
```

VPN:

```bash
ip route
```

These simple checks can prevent mistakes.


---

# Clipboard Risk

The clipboard may contain:

```text
Passwords
Hashes
Tokens
Commands
Customer data
Internal URLs
```

Be careful when switching between:

```text
Customer environment
Personal browser
Chat
Documentation
Other engagement
```


---

# Copy/Paste Verification

Before pressing Enter:

```text
Correct terminal?

Correct host?

Correct client?

Correct command?

Correct target?

Correct scope?
```

This is one of the simplest OPSEC controls.


---

# Command History Review

At the end of an engagement, review whether local histories contain sensitive material.

Do not automatically destroy logs that are required for evidence or accountability.

Retention should follow the engagement policy.


---

# Metadata

Files may contain hidden metadata.

Examples:

```text
Author name
Username
Hostname
Software version
Creation path
GPS coordinates
Document revision history
Organisation
Email address
```


---

# Document Metadata

Review report metadata before external distribution.

Office and PDF documents may contain properties not visible in the main document.


---

# Image Metadata

Images may contain EXIF metadata.

Inspect on Linux where appropriate:

```bash
exiftool image.jpg
```

Do not remove metadata from original evidence if it is required for integrity.

Instead, prepare a sanitised report copy while retaining the original according to evidence policy.


---

# Public Notes vs Engagement Notes

Maintain a hard boundary:

```text
Public Security Notes
        |
        X
        |
Customer Engagement Data
```

When turning assessment lessons into public documentation:

```text
Generalise
Anonymise
Remove customer identifiers
Remove real infrastructure
Remove credentials
Remove sensitive screenshots
Verify permission
```


---

# Tool Output

Tool output can contain sensitive information.

Examples:

```text
BloodHound data
NetExec output
Nmap results
HTTP responses
Cloud enumeration
Credential files
Directory listings
Configuration files
```

Do not upload raw output to public services without approval.


---

# AI and External Services

Before placing engagement data into an external service, determine whether organisational and customer policy permits it.

Consider:

```text
Customer confidentiality
Data retention
Provider terms
Training/data-use policy
Geographic storage
Personal data
Credential material
Source code
Contractual restrictions
```


---

# Do Not Paste Secrets

Never intentionally submit:

```text
Passwords
Private keys
Session cookies
API tokens
Cloud secrets
Reusable hashes
Customer confidential data
```

to an unapproved external service.


---

# Social Engineering OPSEC

If social engineering is explicitly authorised, protect:

```text
Recipient lists
Email addresses
Scenario details
Domains
Landing-page data
Results
Submitted information
```

Do not collect real credentials unless the Rules of Engagement explicitly permit it and appropriate safeguards exist.


---

# Social Engineering Data Minimisation

Prefer proving:

```text
User reached simulation page
User clicked link
User attempted submission
```

without retaining the actual password.


---

# Email Infrastructure

Where email simulation is authorised, track:

```text
Domain
Mailbox
Provider
SPF
DKIM
DMARC
Recipient list
Sending window
Scenario
Stop condition
Cleanup
```


---

# Physical OPSEC

If physical testing is authorised, operators may require:

```text
Authorisation letter
Emergency contact
Identification procedure
Escalation procedure
Safety instructions
Defined buildings
Defined hours
Prohibited areas
```

Physical safety takes priority over assessment objectives.


---

# Lost Device Procedure

If an operator device containing customer data is lost:

```text
Report immediately
      |
      v
Revoke credentials
      |
      v
Revoke sessions
      |
      v
Assess data exposure
      |
      v
Follow incident process
      |
      v
Notify required stakeholders
```


---

# Infrastructure Compromise

Assessment infrastructure itself can be attacked.

Indicators may include:

```text
Unexpected login
Unknown process
Unknown SSH key
Unexpected firewall rule
Unknown cloud API call
Modified binary
Unexpected outbound connection
Unexpected DNS change
```


---

# Infrastructure Incident Response

If compromise is suspected:

```text
Stop using affected infrastructure
        |
        v
Preserve relevant evidence
        |
        v
Notify engagement lead
        |
        v
Revoke credentials
        |
        v
Isolate resource
        |
        v
Determine customer impact
        |
        v
Rebuild from trusted state
```

Do not continue normal assessment operations from infrastructure whose integrity is uncertain.


---

# Authentication Logs

Linux SSH authentication can often be reviewed through the system journal:

```bash
sudo journalctl -u ssh
```

On some systems, authentication records may also be available in:

```text
/var/log/auth.log
```

Exact logging depends on the distribution and configuration.


---

# Successful SSH Sessions

Useful commands include:

```bash
last
```

Currently logged-in users:

```bash
who
```

Detailed current sessions:

```bash
w
```


---

# Cloud Audit Logs

Enable provider audit logging where practical.

Audit records should help answer:

```text
Who created the resource?

Who modified the firewall?

Who changed DNS?

Who created a token?

Who deleted the server?

When?
```


---

# Monitoring Infrastructure

Monitor:

```text
CPU
Memory
Disk
Network
Authentication
Service status
Certificate expiry
Unexpected processes
Cloud billing
```


---

# Disk Usage

Linux:

```bash
df -h
```

Directory usage:

```bash
du -sh ./*
```


---

# Listening Services

Linux:

```bash
ss -lntup
```

Unexpected listeners should be investigated.


---

# Running Services

```bash
systemctl --type=service --state=running
```


---

# Process Review

```bash
ps aux
```

Process tree:

```bash
ps auxf
```


---

# Network Connections

```bash
ss -antp
```

Use appropriate privileges where required for process information.


---

# Time Synchronisation

Check:

```bash
timedatectl status
```

Accurate timestamps are important for correlating red team and blue team evidence.


---

# Backups

Backups may be appropriate for:

```text
Configuration
Operator notes
Evidence
Reports
Infrastructure-as-code
```

But backups also create additional copies of sensitive information.

Apply:

```text
Encryption
Access control
Retention
Deletion
```


---

# Infrastructure as Code

Where practical, infrastructure definitions can improve reproducibility.

Benefits:

```text
Repeatable deployment
Peer review
Known configuration
Faster cleanup
Change history
Reduced manual error
```

Never commit secrets directly into infrastructure definitions.


---

# Configuration Drift

Infrastructure can change during a long assessment.

Track important changes:

```text
Firewall
DNS
TLS
Users
SSH keys
Packages
Services
Cloud roles
Routes
```


---

# Change Log

Example:

| Time | Resource | Change | Operator | Reason |
|---|---|---|---|---|
| 09:00 | RT01 | Created | OP01 | Engagement |
| 09:20 | RT01 | Firewall configured | OP01 | Hardening |
| 10:00 | DNS | Added A record | OP02 | Assessment |
| 17:30 | RT01 | Rule removed | OP01 | Cleanup |


---

# Dependency Management

Assessment tools and infrastructure may depend on:

```text
Python
Go
Java
.NET
Node.js
System packages
Containers
Third-party libraries
```

Avoid uncontrolled updates in the middle of an engagement unless required.

Record important versions when reproducibility matters.


---

# Tool Provenance

Prefer obtaining tools from:

```text
Official project
Official release
Trusted package repository
Verified source
```

Avoid random binary mirrors.


---

# Hash Downloaded Tools

Where practical:

```bash
sha256sum tool
```

Compare with an official checksum when the project publishes one.


---

# Containers

Containers can improve separation for some tools but are not a complete security boundary.

Consider:

```text
Mounted directories
Environment variables
Host networking
Privileged containers
Docker socket
Secrets
Persistent volumes
```


---

# Docker Socket

Access to:

```text
/var/run/docker.sock
```

is highly privileged on many Linux systems.

Do not expose it unnecessarily to assessment containers.


---

# Temporary Accounts

Temporary infrastructure accounts should have:

```text
Owner
Purpose
Privilege
Creation
Expiration
Cleanup
```

At engagement end:

```text
Disable
Delete
Revoke tokens
Remove SSH keys
Verify
```


---

# Temporary Firewall Rules

Document temporary rules.

Example:

```text
Purpose:
Allow management from approved operator address.

Created:
2026-09-05 10:00 UTC

Remove:
End of engagement.
```

Do not rely on memory.


---

# Temporary Routes

Likewise:

```text
Route
Purpose
Pivot
Operator
Creation
Cleanup
```

Routes are especially important when using:

```text
Ligolo-ng
VPN
SSH tunnels
SOCKS
```


---

# Persistence Inventory

If persistence testing is explicitly authorised, every artifact should immediately enter the cleanup inventory.

Example:

| Host | Artifact | Purpose | Created | Removed |
|---|---|---|---|---|
| WS01 | Scheduled task | Persistence validation | 10:30 | 10:45 |
| SRV01 | Test service | Persistence validation | 11:00 | 11:08 |

See:

[Persistence](persistence.md)


---

# Defence Evasion and OPSEC

Defence evasion testing should not involve disabling security controls simply to make testing easier.

Prefer:

```text
Observe Control
      |
      v
Test Safely
      |
      v
Record Prevention
      |
      v
Record Detection
      |
      v
Stop When Proven
```

See:

[Defence Evasion](defence-evasion.md)


---

# Detection Collaboration

When appropriate to the engagement model, provide defenders with assessment infrastructure indicators after testing.

Examples:

```text
Source IP addresses
Assessment domains
Test accounts
Hostnames
Time windows
Payload hashes
ATT&CK techniques
```

This can help validate telemetry and reconstruct the attack path.


---

# Deconfliction

The organisation may experience a real incident during the red team assessment.

Maintain enough information to distinguish:

```text
Red Team Activity
        |
        vs
        |
Real Attacker Activity
```

Useful deconfliction data includes:

```text
Operator logs
Infrastructure IPs
Domains
Payload hashes
Test identities
Timestamps
Target systems
```


---

# Do Not Claim Unknown Activity

If an event cannot be confidently attributed to the assessment:

```text
Do not claim it.
```

Escalate it through the agreed incident procedure.


---

# Kill Switch

Assessment infrastructure should have a rapid shutdown procedure.

Example:

```text
STOP ORDER
    |
    v
Stop Active Operations
    |
    v
Terminate Sessions
    |
    v
Stop C2
    |
    v
Stop Tunnels
    |
    v
Disable Hosting
    |
    v
Revoke Temporary Access
    |
    v
Notify Engagement Lead
```


---

# Emergency Shutdown Checklist

- [ ] Stop operator activity
- [ ] Stop C2 sessions
- [ ] Stop tunnels
- [ ] Stop payload hosting
- [ ] Disable temporary accounts if required
- [ ] Revoke exposed credentials
- [ ] Preserve relevant logs
- [ ] Record timestamps
- [ ] Notify engagement contact
- [ ] Await further instruction


---

# Cleanup Inventory

Maintain cleanup information throughout the engagement.

Potential artifacts:

```text
Files
Processes
Services
Scheduled tasks
Accounts
Group memberships
SSH keys
Certificates
Registry values
Cloud identities
API tokens
Firewall rules
Routes
Tunnels
DNS records
Storage
Email accounts
Payloads
Test data
```


---

# Cleanup Workflow

```text
Operator Logs
      |
      v
Artifact Inventory
      |
      v
Stop Sessions
      |
      v
Remove Persistence
      |
      v
Remove Payloads
      |
      v
Remove Tunnels
      |
      v
Restore Configuration
      |
      v
Revoke Credentials
      |
      v
Destroy Infrastructure
      |
      v
Verify
```


---

# Infrastructure Decommissioning

For each resource:

```text
Still required?
    |
   / \
 Yes  No
 |     |
Retain v
     Archive Required Logs
            |
            v
       Revoke Secrets
            |
            v
        Remove DNS
            |
            v
      Destroy Resource
            |
            v
       Verify Billing
            |
            v
         Complete
```


---

# DNS Decommissioning

Review:

```text
A
AAAA
CNAME
MX
TXT
NS
```

Remove records that are no longer required.


---

# Cloud Decommissioning

Check for:

```text
Instances
Disks
Snapshots
Object storage
Load balancers
Public IPs
DNS zones
Secrets
API tokens
IAM users
Service accounts
Firewall rules
Backups
```


---

# Billing Verification

Forgotten resources may continue generating costs.

After cleanup, review the provider resource inventory and billing dashboard.


---

# Credential Rotation

Rotate or revoke:

```text
Cloud API keys
DNS tokens
SSH keys
C2 credentials
VPN credentials
Temporary customer credentials
Repository tokens
Email credentials
Certificates where appropriate
```


---

# Retention

Not all data should be deleted immediately.

Retention may be required for:

```text
Contract
Quality assurance
Legal requirements
Evidence
Retesting
Customer policy
```

Document:

```text
What is retained
Why
Where
Who can access it
Retention period
Deletion date
```


---

# Secure Deletion

Follow organisational and customer policy for deleting sensitive assessment data.

Modern storage, cloud systems, snapshots, backups, and SSDs make simple assumptions about physical overwriting unreliable.

Focus on:

```text
Approved deletion mechanism
Encryption
Key destruction where applicable
Cloud lifecycle controls
Backup retention
Verification
```


---

# End-of-Engagement Review

Before closing:

```text
Are all customer credentials handled?

Are all temporary accounts removed?

Are all payloads removed?

Are all tunnels stopped?

Are all routes removed?

Are all persistence mechanisms removed?

Are all DNS records reviewed?

Are all cloud resources reviewed?

Are all API tokens revoked?

Are reports in approved storage?

Are evidence-retention rules applied?

Has cleanup been verified?
```


---

# OPSEC Failure Examples

## Cross-Client Data Mixing

```text
Client A evidence copied into Client B report.
```

Control:

```text
Dedicated engagement workspace
Separate report directories
Peer review
```


---

## Private Key Committed to Git

```text
SSH private key committed to repository.
```

Response:

```text
Revoke key
Generate replacement
Remove active exposure
Review repository history
Review access logs
```


---

## Public Storage Bucket

```text
Assessment artifacts stored in publicly accessible cloud storage.
```

Response:

```text
Restrict access
Review access logs
Rotate exposed credentials
Assess customer-data exposure
Notify according to incident procedure
```


---

## Forgotten VPS

```text
Assessment server remains online months after completion.
```

Control:

```text
Expiry tags
Infrastructure inventory
Decommission checklist
Billing review
```


---

## Wrong VPN

```text
Operator performs activity while connected to another customer's VPN.
```

Control:

```text
Dedicated VM
Route check
Terminal labels
Pre-action checklist
```


---

## Wrong Terminal

```text
Command intended for a lab is executed against a customer host.
```

Control:

```text
Distinct terminal sessions
Host prompts
Workspace separation
Scope verification
```


---

## Forgotten Tunnel

```text
Pivot tunnel remains active after testing.
```

Control:

```text
Tunnel inventory
Cleanup checklist
Process review
Route review
```


---

## Credential in Screenshot

```text
Screenshot used in report contains reusable password or token.
```

Control:

```text
Screenshot review
Evidence minimisation
Redaction of report copy
Secure original evidence
```


---

# OPSEC Review Before Every Major Action

```text
                    Proposed Action
                          |
                          v
                    Correct Client?
                     /        \
                   No          Yes
                   |            |
                  STOP          v
                         Correct Target?
                          /        \
                        No          Yes
                        |            |
                       STOP          v
                              In Scope?
                               /     \
                             No       Yes
                             |         |
                            STOP       v
                               Technique Allowed?
                                  /       \
                                No         Yes
                                |           |
                               STOP         v
                                   Correct Identity?
                                      /      \
                                    No        Yes
                                    |          |
                                   STOP        v
                                       Evidence Ready?
                                          /     \
                                        No       Yes
                                        |         |
                                      Prepare     v
                                             Execute
```


---

# Daily OPSEC Checklist

## Start of Day

- [ ] Correct engagement workspace open
- [ ] Correct VM selected
- [ ] Correct VPN selected
- [ ] Routes reviewed
- [ ] Infrastructure status reviewed
- [ ] Scope available
- [ ] Rules of Engagement available
- [ ] Emergency contact available
- [ ] Operator log started
- [ ] Time synchronised

## During Testing

- [ ] Correct target verified
- [ ] Scope checked
- [ ] Technique permitted
- [ ] Credentials protected
- [ ] Evidence labelled
- [ ] Payloads inventoried
- [ ] Tunnels inventoried
- [ ] Routes inventoried
- [ ] Persistence inventoried
- [ ] Infrastructure changes logged
- [ ] Unexpected behaviour escalated

## End of Day

- [ ] Operator notes saved
- [ ] Evidence stored securely
- [ ] Credentials secured
- [ ] Temporary payloads reviewed
- [ ] Active tunnels reviewed
- [ ] Active sessions reviewed
- [ ] Infrastructure reviewed
- [ ] Unexpected resources investigated
- [ ] Sensitive clipboard contents considered
- [ ] Customer sessions secured


---

# Infrastructure OPSEC Checklist

- [ ] Infrastructure inventory maintained
- [ ] Unique engagement identifier used
- [ ] Administrative interfaces restricted
- [ ] SSH keys used where appropriate
- [ ] Root remote login restricted where appropriate
- [ ] Password authentication reviewed
- [ ] Firewall configured
- [ ] Unnecessary services disabled
- [ ] OS patched
- [ ] Cloud MFA enabled
- [ ] Provider API tokens protected
- [ ] DNS inventory maintained
- [ ] TLS certificates tracked
- [ ] Private keys protected
- [ ] Authentication logging enabled
- [ ] Time synchronised
- [ ] Expiration date recorded
- [ ] Decommission procedure prepared


---

# Identity OPSEC Checklist

- [ ] Personal and assessment identities separated
- [ ] Customer accounts documented
- [ ] Privilege documented
- [ ] MFA documented
- [ ] Temporary identities expire
- [ ] Shared accounts avoided where practical
- [ ] Infrastructure roles use least privilege
- [ ] Credentials stored securely
- [ ] Credential revocation planned


---

# Data OPSEC Checklist

- [ ] Customer data minimised
- [ ] Evidence encrypted
- [ ] Sensitive screenshots reviewed
- [ ] Credential material separated
- [ ] Reports stored securely
- [ ] Approved communication channel used
- [ ] Cloud storage private
- [ ] Backups protected
- [ ] Retention documented
- [ ] Deletion requirements documented


---

# Browser OPSEC Checklist

- [ ] Dedicated profile used where appropriate
- [ ] Personal sync disabled
- [ ] Unnecessary extensions removed
- [ ] Saved passwords disabled where appropriate
- [ ] Customer sessions separated
- [ ] Downloads reviewed
- [ ] Cookies removed after engagement
- [ ] Customer certificates removed after engagement


---

# Git OPSEC Checklist

- [ ] Engagement data not stored in public repository
- [ ] `.gitignore` reviewed
- [ ] `git status` reviewed before commit
- [ ] Staged diff reviewed
- [ ] Secrets not committed
- [ ] Private keys excluded
- [ ] Customer screenshots excluded
- [ ] Environment files excluded
- [ ] Secret scanning enabled where available


---

# Payload OPSEC Checklist

- [ ] Payload purpose documented
- [ ] Hash recorded
- [ ] Source recorded
- [ ] Deployment location recorded
- [ ] Hosting controlled
- [ ] Public directory listing disabled where appropriate
- [ ] Target cleanup recorded
- [ ] Hosting cleanup recorded
- [ ] Operator copy retention decided


---

# Pivoting OPSEC Checklist

- [ ] Pivoting explicitly permitted
- [ ] Pivot host documented
- [ ] Reachable networks understood
- [ ] Out-of-scope networks identified
- [ ] Routes documented
- [ ] Tunnel documented
- [ ] Ligolo-ng/Chisel/SSH session documented if used
- [ ] Start time recorded
- [ ] Stop time recorded
- [ ] Tunnel removed
- [ ] Route removed
- [ ] Agent removed
- [ ] Cleanup verified


---

# Evidence OPSEC Checklist

- [ ] Evidence ID assigned
- [ ] Timestamp recorded
- [ ] Host recorded
- [ ] User recorded
- [ ] Technique recorded
- [ ] Sensitive content minimised
- [ ] Screenshots reviewed
- [ ] Hash calculated where required
- [ ] Secure storage used
- [ ] Retention classification applied


---

# Decommission Checklist

- [ ] Operator sessions stopped
- [ ] C2 stopped
- [ ] Tunnels stopped
- [ ] Temporary routes removed
- [ ] Payload hosting stopped
- [ ] Temporary files removed
- [ ] Persistence removed
- [ ] Temporary accounts removed
- [ ] SSH keys removed
- [ ] API tokens revoked
- [ ] VPN credentials revoked
- [ ] DNS reviewed
- [ ] Certificates reviewed
- [ ] Cloud storage reviewed
- [ ] VPS instances destroyed where appropriate
- [ ] Snapshots reviewed
- [ ] Public IP resources released
- [ ] Firewall resources removed
- [ ] Billing checked
- [ ] Evidence archived
- [ ] Cleanup independently verified


---

# OPSEC Incident Decision Model

```text
                 Unexpected Event
                       |
                       v
             Could Customer Be Affected?
                  /             \
                No               Yes
                |                 |
                v                 v
             Record            STOP
                                  |
                                  v
                         Preserve Evidence
                                  |
                                  v
                       Notify Engagement Lead
                                  |
                                  v
                         Customer Contact
                                  |
                                  v
                        Assess Situation
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
               Safe to Resume             Do Not Resume
                    |                           |
                    v                           v
             Approved Resume              Incident Process
```


---

# OPSEC Maturity Model

```text
Level 0 - Ad Hoc

Shared environments
No inventory
No formal cleanup


Level 1 - Basic

Dedicated folders
Basic credential protection
Manual cleanup


Level 2 - Managed

Dedicated workspaces
Infrastructure inventory
Evidence controls
Operator logging


Level 3 - Standardised

Repeatable deployment
Defined identities
Formal retention
Peer-reviewed cleanup


Level 4 - Measured

Infrastructure monitoring
Secret scanning
Cleanup verification
OPSEC metrics


Level 5 - Automated

Infrastructure lifecycle automation
Automatic expiration
Automated secret detection
Policy enforcement
Continuous validation
```


---

# Useful OPSEC Metrics

Potential measurements:

```text
Untracked infrastructure resources
Expired resources still active
Unrevoked credentials
Cleanup exceptions
Cross-engagement data incidents
Secret-scanning findings
Infrastructure security incidents
Unapproved public resources
Missing evidence hashes
Unverified cleanup items
```


---

# Final OPSEC Model

```text
                         AUTHORISATION
                              |
                              v
                       ENGAGEMENT ID
                              |
                              v
                    ISOLATED WORKSPACE
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          IDENTITY       INFRASTRUCTURE       DATA
              |               |               |
              +---------------+---------------+
                              |
                              v
                         OPERATIONS
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
           LOGGING         EVIDENCE        INVENTORY
              |               |               |
              +---------------+---------------+
                              |
                              v
                         MONITORING
                              |
                              v
                           CLEANUP
                              |
                              v
                        REVOCATION
                              |
                              v
                       DECOMMISSION
                              |
                              v
                         VERIFY
```


---

# Core Principle

Red team OPSEC can be reduced to:

```text
Know which engagement you are working on.

Know which identity you are using.

Know which infrastructure belongs to the engagement.

Know exactly which targets are authorised.

Protect credentials and customer data.

Keep assessment resources isolated.

Record important actions.

Track everything introduced into the environment.

Treat unexpected activity seriously.

Remove everything that should not remain.

Verify cleanup rather than assuming it succeeded.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Detection Validation](detection-validation.md)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Active Directory](../active-directory/)


---

# References

- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH Manual Pages](https://www.openssh.com/manual.html){ target="_blank" rel="noopener noreferrer" }
- [GitHub - Removing Sensitive Data from a Repository](https://docs.github.com/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository){ target="_blank" rel="noopener noreferrer" }
- [GitHub - About Secret Scanning](https://docs.github.com/code-security/secret-scanning/introduction/about-secret-scanning){ target="_blank" rel="noopener noreferrer" }
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [WireGuard](https://www.wireguard.com/){ target="_blank" rel="noopener noreferrer" }
- [Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }
- [Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "OPSEC should make testing safer"
    Good red team OPSEC is not measured by how difficult the assessment is to attribute to the authorised testers. It is measured by whether customer data, credentials, infrastructure, evidence, and operator activity remain controlled throughout the engagement and whether every introduced artifact can be accounted for and removed.


!!! warning "Authorised testing only"
    Operational security does not override scope, customer safety, provider terms, or the Rules of Engagement. Do not use OPSEC practices to conceal unauthorised activity. Maintain sufficient logs for deconfliction and accountability, immediately escalate unexpected production impact or suspected third-party activity, and verify complete cleanup at the end of every assessment.
