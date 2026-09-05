---
title: Red Team Cleanup
description: Red team cleanup and decommissioning methodology for authorised security assessments, covering host artifacts, accounts, credentials, persistence, C2, pivoting, cloud resources, phishing infrastructure, evidence retention, verification and handover.
---

# Red Team Cleanup

Cleanup is the controlled removal, reversal or handover of artifacts created during an authorised red team engagement.

A red team operation should not be considered complete when the final objective is reached.

It is complete when:

```text
Testing Stops
     |
     v
Artifacts Identified
     |
     v
Changes Reversed
     |
     v
Access Removed
     |
     v
Infrastructure Decommissioned
     |
     v
Credentials Revoked
     |
     v
Cleanup Verified
     |
     v
Exceptions Documented
     |
     v
Customer Handover
```

Cleanup should be planned before testing begins rather than reconstructed from memory at the end of the engagement.

!!! warning "Do not remove evidence of a real incident"
    If activity discovered during cleanup may belong to an actual attacker rather than the authorised assessment, stop and follow the engagement's deconfliction and incident-response procedures. Do not delete unknown artifacts merely because they resemble red team activity.


---

# Cleanup Objectives

Cleanup should ensure that:

```text
Temporary files are removed

Test accounts are removed or disabled

Temporary privileges are revoked

Persistence is removed

Credentials are revoked or rotated

Sessions and tokens are invalidated

Temporary routes and tunnels are removed

C2 infrastructure is disabled

Cloud resources are removed

Phishing infrastructure is retired

Test data is removed

Customer configuration is restored

Residual access is eliminated

Exceptions are documented

Cleanup is independently verified
```


---

# Cleanup Is Part of the Engagement

The operational lifecycle should be:

```text
Plan
  |
  v
Deploy
  |
  v
Test
  |
  v
Track Changes
  |
  v
Achieve Objective
  |
  v
Cleanup
  |
  v
Verify
  |
  v
Report
```

Not:

```text
Test
  |
  v
Finish
  |
  v
Try to Remember What Changed
```


---

# Plan Cleanup Before Execution

Before creating an artifact, know:

```text
What will be created?

Where will it exist?

Who owns it?

How will it be removed?

How will removal be verified?
```

A useful rule is:

```text
No deployment without a cleanup plan.
```


---

# Cleanup Inventory

Maintain a live inventory throughout the engagement.

Example:

| ID | Artifact | Location | Created By | Cleanup | Status |
|---|---|---|---|---|---|
| CLN-001 | Test file | WS01 | Operator A | Delete | Pending |
| CLN-002 | Test account | AD | Operator B | Disable/remove | Pending |
| CLN-003 | Scheduled task | WS02 | Operator A | Remove | Complete |
| CLN-004 | Cloud VM | Azure | Operator C | Delete | Pending |
| CLN-005 | Route | Operator host | Operator A | Remove | Complete |


---

# Artifact Categories

Track at least:

```text
Files

Directories

Accounts

Groups

Privileges

Services

Scheduled tasks

Registry changes

Startup entries

SSH keys

Cron jobs

Systemd units

Routes

Tunnels

Firewall rules

DNS records

Certificates

Tokens

API keys

OAuth applications

Cloud resources

Containers

Kubernetes resources

C2 agents

Payloads

Phishing infrastructure

Synthetic data

Logs and evidence
```


---

# Cleanup Status

Use consistent states:

```text
Pending

In Progress

Removed

Verified

Customer Owned

Unable to Remove

Retained by Agreement

Not Applicable
```


---

# Cleanup Responsibility

Every artifact should have an owner.

```text
Artifact
   |
   v
Operator
   |
   v
Cleanup Action
   |
   v
Verification
```

Avoid:

```text
Someone probably removed it.
```


---

# Original State

Before modifying a system, capture enough information to restore it.

For example:

```text
Original value

Original permissions

Original membership

Original configuration

Original service state

Original firewall state
```

Without the original state, "cleanup" may accidentally introduce a new configuration.


---

# Change Log

Maintain:

```text
Timestamp

Operator

System

Action

Original state

New state

Reason

Cleanup procedure

Cleanup status
```


---

# Example Change Log

```text
Time:
2026-09-05 10:14 UTC

Host:
WS01

Change:
Created scheduled task RT-Test-01

Purpose:
Persistence detection validation

Original State:
Task did not exist

Cleanup:
Remove RT-Test-01

Status:
Verified removed
```


---

# Cleanup Order

A practical cleanup order is:

```text
1. Stop active testing

2. Stop active sessions

3. Remove persistence

4. Remove temporary privileges

5. Remove temporary accounts

6. Remove host artifacts

7. Remove tunnels and routes

8. Revoke credentials and tokens

9. Disable C2

10. Remove cloud resources

11. Retire phishing infrastructure

12. Remove synthetic test data

13. Verify systems

14. Document exceptions

15. Decommission operator infrastructure
```


---

# Stop Active Operations

Before cleanup begins:

```text
Stop new tasking

Stop new payload deployment

Stop new phishing messages

Stop automated emulation

Stop scheduled testing

Stop active scanning
```

Otherwise new artifacts may appear while cleanup is being performed.


---

# Freeze the Inventory

At cleanup start:

```text
Active Inventory
      |
      v
Final Operational Review
      |
      v
Cleanup Baseline
```

Operators should report any undocumented artifacts before cleanup proceeds.


---

# Host Cleanup

Host cleanup may involve:

```text
Windows endpoints

Windows servers

Linux systems

Jump hosts

Containers

Cloud instances
```


---

# Windows Artifact Review

Review engagement-created artifacts such as:

```text
Files

Directories

Services

Scheduled tasks

Registry values

Startup entries

PowerShell profiles

Temporary users

Group memberships

Certificates

Firewall rules

Environment variables

Test scripts
```


---

# Windows Files

Maintain the exact paths of files deployed during testing.

Example inventory:

```text
C:\Windows\Temp\rt-test.txt

C:\ProgramData\RedTeam\marker.txt

C:\Temp\test.dll
```

Remove only files confirmed to belong to the engagement.


---

# Verify Before Deleting

Before removing a file:

```powershell
Get-Item -LiteralPath 'C:\Windows\Temp\rt-test.txt' -ErrorAction SilentlyContinue
```

If the file is part of the engagement and cleanup is authorised:

```powershell
Remove-Item -LiteralPath 'C:\Windows\Temp\rt-test.txt' -Force
```

Verify:

```powershell
Test-Path -LiteralPath 'C:\Windows\Temp\rt-test.txt'
```

Expected:

```text
False
```


---

# Hash Before Cleanup

For important artifacts, retain a hash in the evidence inventory before deletion.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Windows\Temp\rt-test.txt'
```

This allows the report to identify the artifact without retaining it on the customer system.


---

# Windows Scheduled Tasks

Review only tasks associated with the engagement.

```powershell
Get-ScheduledTask | Select-Object TaskName,TaskPath,State
```

For a known test task:

```powershell
Get-ScheduledTask -TaskName 'RT-Test-01' -ErrorAction SilentlyContinue
```

Remove the known test task:

```powershell
Unregister-ScheduledTask -TaskName 'RT-Test-01' -Confirm:$false
```

Verify:

```powershell
Get-ScheduledTask -TaskName 'RT-Test-01' -ErrorAction SilentlyContinue
```


---

# Windows Services

Review known engagement-created services.

```powershell
Get-Service | Sort-Object Name
```

For a known test service:

```powershell
Get-Service -Name 'RTTestService' -ErrorAction SilentlyContinue
```

If the engagement created the service, remove it using the documented cleanup procedure and verify that it no longer exists.

Do not delete an unfamiliar service simply because its name looks suspicious.


---

# Windows Registry

Record exact keys and values changed during testing.

Example inspection:

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
```

Cleanup should restore the original state rather than blindly deleting entire keys.


---

# Registry Cleanup Model

```text
Original:
Value absent

Test:
Value created

Cleanup:
Remove test value
```

or:

```text
Original:
Value = A

Test:
Value = B

Cleanup:
Restore A
```

The distinction matters.


---

# Windows Accounts

Review accounts created specifically for testing.

```powershell
Get-LocalUser
```

For domain environments, use approved administrative tooling to identify the exact test identity.

Do not remove accounts based only on naming assumptions.


---

# Group Membership

If temporary membership was added:

```text
Original:
Test user not member

Test:
Test user added to group

Cleanup:
Remove test user

Verify:
Membership matches original state
```


---

# Windows Firewall

If temporary firewall rules were created, record their exact names.

Inspect:

```powershell
Get-NetFirewallRule | Select-Object DisplayName,Enabled,Direction,Action
```

Remove only engagement-created rules using their recorded identifiers.


---

# Windows Certificates

Testing may create:

```text
Client certificates

TLS certificates

Test CA certificates

Authentication certificates
```

Record:

```text
Thumbprint

Store

Subject

Issuer

Purpose
```

before deployment.

Cleanup should remove only the certificates created for the engagement.


---

# PowerShell Artifacts

Review:

```text
Scripts

Profiles

Modules

Transcript files

Temporary output

Downloaded tools

History implications
```

Do not delete security logs or PowerShell operational logs as part of red team cleanup.


---

# Do Not Clear Logs

Cleanup does not mean destroying telemetry.

Do not clear:

```text
Windows Event Logs

PowerShell logs

Defender logs

Sysmon logs

EDR telemetry

Authentication logs

Firewall logs
```

These may be required for detection validation, incident response or evidence.


---

# Linux Artifact Review

Review:

```text
Files

Directories

Users

Groups

sudo configuration

SSH keys

Cron jobs

Systemd units

Services

Shell profiles

Environment files

Routes

Firewall rules

Containers
```


---

# Linux Files

Check exact engagement paths.

```bash
ls -la /tmp/rt-test.txt
```

Remove a confirmed test artifact:

```bash
rm -- /tmp/rt-test.txt
```

Verify:

```bash
test ! -e /tmp/rt-test.txt && echo "removed"
```


---

# Linux Hashing

Before removal:

```bash
sha256sum /tmp/rt-test.txt
```

Record the hash in the evidence inventory where useful.


---

# Linux Users

Review:

```bash
getent passwd
```

If a dedicated engagement account was created, verify:

```bash
id redteam-test
```

Remove it only according to the agreed cleanup procedure.


---

# Linux Groups

Check temporary group membership:

```bash
id redteam-test
```

Review changes against the original state.


---

# sudo Cleanup

If testing changed sudo configuration, validate syntax before and after restoration.

```bash
sudo visudo -c
```

Do not remove unrelated entries.


---

# SSH Keys

Review only keys added during the engagement.

Common location:

```text
~/.ssh/authorized_keys
```

Before editing:

```bash
cat ~/.ssh/authorized_keys
```

Remove only the exact engagement key.

Do not replace the entire file.


---

# SSH Key Fingerprints

Record the fingerprint of a test public key.

```bash
ssh-keygen -lf redteam_test.pub
```

This helps distinguish the engagement key from legitimate keys.


---

# Cron

Review:

```bash
crontab -l
```

and, where authorised:

```bash
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
```

Remove only engagement-created jobs.


---

# systemd

Review known test units:

```bash
systemctl list-unit-files --type=service
```

If a temporary unit was created, restore the system according to the documented cleanup procedure.

Verify that:

```text
Unit removed

Service stopped

Reload completed

Associated files removed
```


---

# Shell Startup Files

Review engagement changes to:

```text
.bashrc

.profile

.bash_profile

.zshrc

/etc/profile
```

Restore only the exact modifications made during testing.


---

# Linux Firewall

Depending on the system, review:

```bash
sudo nft list ruleset
```

or:

```bash
sudo ufw status numbered
```

Remove only temporary engagement rules.


---

# Routes

Temporary routes are common during pivoting.

Linux:

```bash
ip route
```

Windows:

```powershell
Get-NetRoute | Sort-Object DestinationPrefix
```

Compare against the route inventory maintained during testing.


---

# Pivot Cleanup

Pivoting can leave:

```text
TUN interfaces

Routes

SOCKS proxies

Port forwards

SSH tunnels

Ligolo sessions

Chisel processes

Framework routes
```


---

# Pivot Inventory

Maintain:

| ID | Type | Source | Destination | Port/Route | Status |
|---|---|---|---|---|---|
| PIV-01 | Ligolo | Operator | Internal | 10.10.20.0/24 | Active |
| PIV-02 | SSH Forward | Jump01 | App01 | 443 | Active |


---

# Ligolo Cleanup

For Ligolo-ng testing, cleanup may involve:

```text
Stop active proxy sessions

Stop agents

Remove temporary routes

Remove temporary TUN interfaces if created solely for the engagement

Remove agent binaries from customer systems

Verify no processes remain
```

Check routes:

```bash
ip route
```

Check interfaces:

```bash
ip addr
```


---

# Chisel Cleanup

Review:

```text
Client process

Server process

Downloaded binary

Listening ports

Temporary firewall rules
```

Verify no engagement-created listener remains.


---

# SSH Tunnel Cleanup

Review active SSH sessions and port forwards.

Linux examples:

```bash
ps aux | grep '[s]sh'
```

Review listeners:

```bash
ss -lntup
```

Do not terminate unrelated administrative SSH sessions.


---

# SOCKS Proxy Cleanup

Check:

```text
Proxy process

Listening port

proxychains configuration changes

Temporary DNS settings
```

Restore modified configuration files to their original state.


---

# C2 Cleanup

Command-and-control infrastructure can leave artifacts on both customer and operator systems.

Track:

```text
Agents

Payloads

Listeners

Redirectors

Team servers

Certificates

Domains

DNS

Logs

Credentials

Firewall rules
```


---

# C2 Agent Inventory

Maintain:

| Agent | Host | User | First Seen | Last Seen | Cleanup |
|---|---|---|---|---|---|
| A-01 | WS01 | test-user | 10:14 | 13:22 | Verified |
| A-02 | SRV01 | test-admin | 11:07 | 12:41 | Verified |


---

# Stop C2 Tasking

Before endpoint cleanup:

```text
Disable automation

Stop new tasking

Record final session inventory

Terminate engagement sessions
```

This prevents agents from recreating artifacts.


---

# Payload Cleanup

Track every deployed payload using:

```text
Filename

Path

SHA-256

Host

Deployment time

Purpose

Cleanup status
```


---

# Listener Cleanup

Review:

```text
Listener ports

Bind addresses

Certificates

Firewall rules

Redirectors

DNS records
```

Disable listeners after customer-side cleanup is complete.


---

# Why C2 Should Not Be Disabled First

If operator access is required for authorised cleanup:

```text
Customer Cleanup
       |
       v
Verify Artifacts Removed
       |
       v
Terminate Sessions
       |
       v
Disable C2 Infrastructure
```

Destroying infrastructure too early may make controlled cleanup harder.


---

# Redirector Cleanup

Review:

```text
Reverse proxy configuration

TLS certificates

Firewall rules

DNS records

Cloud instances

Logs
```

Retain only what the engagement agreement requires.


---

# Domain Cleanup

Domains may require a different lifecycle than temporary servers.

Options include:

```text
Retain registration

Remove DNS

Park domain

Redirect to neutral page

Continue monitoring

Retire after defined period
```

Do not allow a previously used engagement domain to expire carelessly if another party could register it and inherit trust or references associated with the campaign.


---

# DNS Cleanup

Review:

```text
A

AAAA

CNAME

MX

TXT

NS

CAA
```

Remove records that are no longer required.


---

# TLS Certificates

Track:

```text
Certificate

Private key

Domain

Provider

Expiration

Storage location
```

Remove private keys from temporary infrastructure when no longer required.


---

# Credentials

Credentials used during the engagement may include:

```text
Test passwords

API keys

SSH keys

Cloud access keys

Service credentials

Certificates

OAuth secrets

Tokens
```


---

# Credential Cleanup Model

```text
Credential Used?
      |
      v
Still Required?
   /       \
 Yes        No
 |           |
 v           v
Handover   Revoke
             |
             v
         Verify Failure
```


---

# Test Passwords

Dedicated test passwords should not be reused after the engagement.

For persistent customer test accounts, rotate them before handover.


---

# SSH Key Cleanup

Remove engagement public keys from customer systems.

Then securely remove unnecessary private keys from operator systems according to the retention policy.


---

# API Keys

Revoke temporary API keys.

Verify:

```text
Key disabled

Key deleted where appropriate

Associated sessions invalidated

No automation still depends on key
```


---

# Tokens

Review:

```text
Access tokens

Refresh tokens

Personal access tokens

Session tokens

Temporary access passes
```

Revocation is preferable to merely deleting the local copy.


---

# Certificates as Credentials

Certificates may provide authentication even after passwords are changed.

Review:

```text
Client certificates

Authentication certificates

Certificate private keys

Temporary CA material
```

Revoke or remove engagement-specific certificates where appropriate.


---

# Active Directory Cleanup

AD cleanup may involve:

```text
Users

Groups

Group memberships

ACL changes

Machine accounts

SPNs

Delegation

Certificates

GPO changes

Scheduled tasks

Services

Persistence
```


---

# AD Test Accounts

Track:

```text
SamAccountName

Distinguished Name

Creation time

Purpose

Group membership

Cleanup action
```


---

# AD Group Membership

If temporary membership was used:

```text
Original Membership
        |
        v
Temporary Addition
        |
        v
Testing
        |
        v
Remove Addition
        |
        v
Verify Original Membership
```


---

# AD ACL Changes

ACL modifications require particular care.

Record before testing:

```text
Object

Principal

Right

Inheritance

Original ACL
```

Cleanup should restore the original security descriptor or remove only the ACE introduced by the engagement.


---

# Machine Accounts

If a machine account was created for authorised testing, record:

```text
Name

Distinguished Name

Creator

Purpose

Password ownership

Associated SPNs
```

Remove it after the test unless the customer explicitly wants it retained.


---

# SPNs

If SPNs were added or changed, restore their original configuration.

Incorrect SPN cleanup can affect Kerberos authentication.


---

# Delegation

Review any engagement changes involving:

```text
Constrained delegation

Resource-based constrained delegation

Unconstrained delegation configuration
```

Restore the exact original configuration.


---

# Shadow Credentials

If an authorised test modifies key credential information, cleanup must restore the original state and verify the test material no longer provides authentication.

Avoid leaving authentication material in the directory after testing.


---

# AD CS

Certificate-based testing may leave:

```text
Issued certificates

Private keys

Template changes

CA configuration changes

Enrollment permissions
```

Track each artifact individually.


---

# Issued Certificates

Where test certificates remain valid after the engagement, determine whether they should be:

```text
Revoked

Allowed to expire

Retained as customer-owned test artifacts
```

The decision should be documented.


---

# GPO Cleanup

For any GPO modified during testing:

```text
Record original settings

Record test changes

Restore original settings

Confirm replication

Validate affected systems
```

Avoid deleting a production GPO merely because it was modified during the assessment.


---

# Cloud Cleanup

Cloud testing may create:

```text
Virtual machines

Storage

IAM identities

Roles

Policies

Security groups

Firewall rules

API keys

Service principals

Applications

Secrets

Snapshots

Functions

Containers

DNS records
```


---

# Cloud Inventory

Record:

| Resource | Provider | Region | Purpose | Owner | Cleanup |
|---|---|---|---|---|---|
| rt-vm-01 | Cloud | EU region | Redirector | Red Team | Pending |
| rt-storage | Cloud | EU region | Synthetic data | Red Team | Pending |


---

# Cloud Tags

Use engagement tags where possible.

Example concept:

```text
engagement = RT-2026-04

owner = red-team

temporary = true
```

This simplifies cleanup.


---

# Cloud Identity

Review:

```text
Users

Roles

Service principals

Managed identities

API keys

Access policies

Temporary role assignments
```

Remove temporary privileges before deleting supporting infrastructure.


---

# Cloud Sessions

Revoking credentials does not always terminate every existing session immediately.

Where supported, invalidate:

```text
Sessions

Refresh tokens

Access tokens

Temporary credentials
```


---

# Cloud Storage

Before deletion, confirm that storage contains only:

```text
Synthetic data

Engagement artifacts

Approved evidence
```

Do not delete customer data merely because the red team accessed the storage location.


---

# Cloud Snapshots

Temporary snapshots can persist after the associated VM is removed.

Review:

```text
Snapshots

Images

Backups

Disks

Volumes
```

for engagement-created resources.


---

# Security Groups

Review temporary:

```text
Inbound rules

Outbound rules

Source IP allowances

Administrative access rules
```

Remove only rules created for the engagement.


---

# Cloud Cost Cleanup

Residual infrastructure can continue generating cost.

Review:

```text
VMs

Disks

Public IPs

Load balancers

Gateways

Snapshots

Storage

Databases

DNS zones
```

after decommissioning.


---

# Containers

Container testing may leave:

```text
Containers

Images

Volumes

Networks

Secrets

Bind mounts
```


---

# Docker Review

Examples:

```bash
docker ps -a
docker images
docker volume ls
docker network ls
```

Remove only resources created for the engagement.


---

# Kubernetes Cleanup

Potential artifacts include:

```text
Pods

Deployments

Jobs

CronJobs

Services

ConfigMaps

Secrets

ServiceAccounts

RoleBindings

ClusterRoleBindings
```


---

# Kubernetes Inventory

Read-only review:

```bash
kubectl get pods -A
kubectl get deployments -A
kubectl get jobs -A
kubectl get cronjobs -A
```

Use exact recorded names and namespaces for cleanup.


---

# Kubernetes RBAC

If temporary permissions were created, verify:

```text
Role

ClusterRole

RoleBinding

ClusterRoleBinding

ServiceAccount
```

and restore the original RBAC state.


---

# Phishing Cleanup

Phishing campaigns may leave:

```text
Domains

Mailboxes

Mail server configuration

DNS

Landing pages

Campaign databases

Target lists

Tracking identifiers

Test accounts

OAuth applications

TLS certificates
```


---

# Stop Campaign Delivery

Before cleanup:

```text
Stop scheduled messages

Stop campaign automation

Disable landing-page submissions

Stop tracking where appropriate
```


---

# Landing Pages

Disable test forms before deleting campaign data.

A temporary page may display:

```text
Campaign Closed
```

until infrastructure is fully retired.


---

# Phishing Credentials

If synthetic credentials were used:

```text
Disable or remove test account

Rotate retained test account password

Revoke sessions

Remove stored test values
```


---

# Unexpected Real Credentials

If real credentials were unexpectedly submitted:

```text
Stop collection

Notify authorised customer contact

Rotate affected credential

Revoke relevant sessions

Remove retained sensitive value

Document the event
```


---

# OAuth Applications

For test OAuth applications:

```text
Revoke consent

Revoke tokens

Remove secrets

Remove certificates

Delete application where appropriate

Verify audit trail
```


---

# Target Lists

Target lists may contain personal information.

Apply the agreed:

```text
Retention period

Access control

Encryption

Deletion procedure
```


---

# Social Engineering Cleanup

Review:

```text
Synthetic identities

Test phone numbers

Test mailboxes

Visitor badges

USB devices

QR codes

Printed materials

Test documents
```


---

# Physical Artifacts

Recover:

```text
USB devices

Badges

Printed pretexts

Test access cards

Temporary equipment
```

where applicable.


---

# Collection Cleanup

Collection testing should normally use synthetic data.

Review:

```text
Staging directories

Archives

Temporary copies

Screenshots

Exports

Database extracts
```


---

# Synthetic Data

Delete temporary synthetic datasets from customer systems when they are no longer required.


---

# Production Data

If production data was accessed during the engagement, do not automatically delete the source data.

Only remove:

```text
Red team copies

Temporary exports

Temporary archives
```

created by the engagement.


---

# Exfiltration Cleanup

Review:

```text
Destination storage

Transferred synthetic files

Temporary archives

Cloud buckets

Upload endpoints

Transfer logs
```


---

# Exfiltration Destination

After evidence requirements are satisfied:

```text
Disable upload endpoint

Remove synthetic data

Remove temporary credentials

Remove temporary storage

Retain only approved evidence
```


---

# Persistence Cleanup

Persistence deserves a dedicated review because forgotten persistence can create continuing access.

Review:

```text
Scheduled tasks

Services

Registry autoruns

Startup folders

PowerShell profiles

WMI subscriptions

Cron

systemd

SSH keys

Accounts

Group memberships

AD ACLs

Certificates

Cloud identities

OAuth applications
```

See:

[Persistence](persistence.md)


---

# Persistence Verification

Do not rely solely on:

```text
I removed the one mechanism I remember.
```

Compare against the persistence inventory maintained during testing.


---

# Privilege Escalation Cleanup

Review changes involving:

```text
Group membership

sudo configuration

File permissions

Service configuration

ACLs

Tokens

Temporary privileges

Cloud roles

AD rights
```

See:

[Privilege Escalation](privilege-escalation.md)


---

# Temporary Administrative Access

If a test identity received administrative access:

```text
Remove privilege

Verify membership

Revoke sessions where necessary

Retest access
```


---

# Credential Access Cleanup

Credential-access testing may produce sensitive artifacts.

Review:

```text
Credential files

Hashes

Tickets

Tokens

Certificates

SSH keys

API keys

Tool output

Screenshots
```

See:

[Credential Access](credential-access.md)


---

# Sensitive Tool Output

Tools may produce output files containing:

```text
Credentials

Hashes

Hostnames

Usernames

Tokens

Directory data
```

Protect and remove them according to the engagement's evidence-retention policy.


---

# Kerberos Artifacts

If test tickets or credential caches were created on operator systems, remove them when no longer required.

If account secrets were exposed, follow the agreed credential rotation procedure.


---

# Browser Sessions

If testing used dedicated browser profiles:

```text
Sign out

Revoke test sessions

Remove test profile

Remove cookies

Remove downloaded artifacts
```

Do not retain customer sessions for convenience after the engagement.


---

# VPN Access

Review engagement VPN access.

```text
Test account

Certificate

VPN profile

MFA registration

Device registration
```

Remove or hand over according to the agreed lifecycle.


---

# Remote Access

Review:

```text
RDP access

WinRM access

SSH access

VPN access

Jump-host access

Cloud console access
```

Temporary access should not remain simply because it may be useful for future retesting.


---

# Tool Cleanup

Tools copied to customer systems should be inventoried.

Examples:

```text
Enumeration tools

Network utilities

Test scripts

Framework agents

Portable binaries

Configuration files
```

Remove engagement copies unless the customer requests otherwise.


---

# Tool Hashes

Maintain SHA-256 hashes for deployed tooling.

This assists:

```text
Cleanup

SOC deconfliction

Threat hunting

Reporting
```


---

# Temporary Web Servers

If temporary web servers were used:

```text
Stop server

Verify port closed

Remove hosted files

Remove firewall rule

Remove service if created
```


---

# Listener Verification

Linux:

```bash
ss -lntup
```

Windows:

```powershell
Get-NetTCPConnection -State Listen
```

Compare against the engagement listener inventory.


---

# Network Cleanup

Review:

```text
Routes

Firewall rules

Port forwards

Proxy settings

DNS changes

VPN configuration

Temporary listeners
```


---

# Proxy Settings

If system proxy settings were changed, restore the original values.

Do not assume that "no proxy" was the original configuration.


---

# DNS Changes

If local DNS configuration was modified:

```text
Hosts file

Resolver configuration

DNS server

Search suffix
```

restore the recorded original state.


---

# Hosts Files

Common locations:

Windows:

```text
C:\Windows\System32\drivers\etc\hosts
```

Linux:

```text
/etc/hosts
```

Remove only engagement-created entries.


---

# Evidence Is Not the Same as an Artifact

Distinguish:

```text
Customer-System Artifact
```

from:

```text
Red-Team Evidence
```

For example:

```text
C:\Temp\rt-test.txt
```

may need removal.

A screenshot proving it existed may need retention.


---

# Evidence Retention

Retain only what is required by:

```text
Statement of Work

Rules of Engagement

Customer policy

Legal requirements

Reporting requirements
```


---

# Evidence Classification

Classify evidence such as:

```text
Public

Internal

Confidential

Restricted
```

according to the engagement's data-handling requirements.


---

# Evidence Storage

Protect evidence using:

```text
Encryption

Access control

Dedicated storage

Backup policy

Retention schedule
```


---

# Evidence Minimisation

Avoid retaining unnecessary:

```text
Passwords

Tokens

Private keys

Personal data

Large production datasets

Complete mailbox contents
```


---

# Evidence Sanitisation

Reports may use:

```text
Redacted screenshots

Partial usernames

Masked tokens

Synthetic data

Hashes
```

instead of raw sensitive material.


---

# Retention Schedule

Example:

| Data | Retention | Action |
|---|---|---|
| Final report | Contract defined | Retain |
| Screenshots | Contract defined | Retain/delete |
| Raw tool output | Short term | Delete |
| Production credentials | None | Rotate/delete |
| Synthetic data | Engagement only | Delete |


---

# Do Not Delete Defensive Telemetry

Red team cleanup should preserve evidence useful to defenders.

Do not delete:

```text
SIEM events

EDR events

Firewall logs

Authentication logs

Cloud audit logs

Email security events

SOC tickets
```

unless the customer explicitly owns a separate retention decision.


---

# Detection Validation During Cleanup

Cleanup itself may generate useful telemetry.

Examples:

```text
Account deletion

Privilege removal

Task deletion

Service removal

Token revocation

Cloud resource deletion
```

Defenders may use this to validate administrative monitoring.


---

# Cleanup Verification

Cleanup should be verified rather than assumed.

```text
Cleanup Action
      |
      v
Artifact Query
      |
      v
Still Present?
   /        \
 Yes         No
 |            |
 v            v
Retry      Mark Verified
```


---

# Independent Verification

For high-risk artifacts, consider:

```text
Operator A removes artifact

Operator B verifies removal
```

This reduces errors.


---

# Verification Methods

Use:

```text
File existence check

Account query

Group membership query

Service query

Task query

Port scan

Route table review

Cloud inventory

DNS query

Authentication test

Token validation
```


---

# Authentication Verification

For a revoked test credential:

```text
Credential Revoked
      |
      v
Controlled Authentication Test
      |
      v
Authentication Fails
      |
      v
Verified
```

Avoid repeated authentication attempts that could trigger lockouts.


---

# Network Verification

Confirm temporary services are no longer exposed.

Examples:

```bash
ss -lntup
```

and, from an authorised validation host:

```bash
nmap -sT -Pn -p 443,8000,8080 <approved-test-host>
```

Use only against approved engagement infrastructure or in-scope hosts.


---

# DNS Verification

Use:

```bash
dig example.test
```

or:

```bash
nslookup example.test
```

to confirm retired records behave as expected.


---

# Cloud Verification

After cleanup, review the engagement tag or naming convention.

The desired result is:

```text
No unexpected temporary resources remain.
```


---

# Residual Artifact Hunt

Perform a final search using known engagement identifiers.

Examples:

```text
Campaign ID

Test username

Payload filename

Tool hash

Domain

Service name

Task name

Directory name
```

This is more reliable than relying on memory.


---

# Engagement Naming Convention

Consistent names make cleanup easier.

Example:

```text
RT-2026-04

RT-Test-User

RT-Test-Task

rt-2026-04-vm
```

Do not use predictable red team naming when it would invalidate an explicitly authorised detection objective, but still maintain an internal artifact inventory.


---

# Threat Hunting After Cleanup

Provide defenders with relevant engagement indicators where agreed.

Examples:

```text
Domains

IPs

File hashes

Account names

Process names

Tool hashes

Certificate fingerprints
```

This allows the blue team to verify whether residual activity remains.


---

# Indicator Handover

Example:

| Type | Value | Purpose |
|---|---|---|
| Domain | test.example | C2 |
| SHA-256 | `<hash>` | Test binary |
| Account | RT-Test-01 | Synthetic identity |
| IP | 192.0.2.10 | Test infrastructure |


---

# False Attribution Risk

After the engagement, defenders may later encounter a historical artifact.

Without documentation, they may interpret it as a real compromise.

Maintain sufficient records to answer:

```text
Was this ours?

When was it deployed?

Where?

Why?

Was it removed?
```


---

# Unexpected Artifacts

During cleanup, you may find an artifact that was not created by the red team.

Examples:

```text
Unknown account

Unknown scheduled task

Unknown SSH key

Unknown service

Unknown web shell

Unknown cloud identity
```

Do not remove it automatically.


---

# Unexpected Artifact Decision Model

```text
Unknown Artifact
      |
      v
Created by Red Team?
   /          \
 Yes           Unknown / No
 |                |
 v                v
Cleanup       Preserve Evidence
                  |
                  v
              Notify Contact
                  |
                  v
             Incident Process
```


---

# Real Compromise

If cleanup reveals indicators of a real compromise:

```text
Stop normal cleanup where necessary

Preserve evidence

Notify authorised contacts

Separate red team activity from unknown activity

Support deconfliction

Follow incident-response procedures
```


---

# Do Not Contaminate Evidence

Avoid modifying unknown artifacts merely to investigate them.

The incident-response team may need:

```text
Timestamps

Metadata

Logs

File hashes

Memory state

Cloud audit history
```


---

# Customer-Owned Artifacts

Some artifacts may intentionally remain.

Examples:

```text
Detection rules

Synthetic test accounts

Dedicated lab systems

Test certificates

Automation

Purple team infrastructure
```

Mark these:

```text
Customer Owned
```

rather than "not cleaned."


---

# Handover

If an artifact remains, document:

```text
Artifact

Location

Owner

Reason retained

Credentials

Security considerations

Expiration

Required future action
```


---

# Cleanup Exceptions

Not every artifact can always be removed immediately.

Examples:

```text
Customer requests retention

System unavailable

Change freeze

Production risk

Third-party dependency

Evidence preservation requirement
```


---

# Exception Record

Example:

```text
Artifact:
RT-Test-Account

Location:
Active Directory

Status:
Retained by Agreement

Reason:
Customer detection engineering team requires account for
retesting.

Owner:
Security Engineering

Expiration:
2026-10-01

Required Action:
Disable and remove after validation programme.
```


---

# Cleanup Failure

If cleanup fails:

```text
Do not silently mark complete.
```

Record:

```text
What remains

Why it remains

Risk

Owner

Required action

Deadline
```


---

# High-Risk Residuals

Prioritise residual artifacts that provide continuing access.

Examples:

```text
Privileged accounts

SSH keys

API keys

Cloud roles

OAuth applications

Certificates

C2 agents

Persistence

Open firewall rules

Exposed listeners
```


---

# Residual Risk

A cleanup exception should have a risk assessment.

Example:

```text
Residual:
Temporary cloud API key remains active.

Risk:
Key retains read access to test subscription.

Immediate Action:
Customer cloud administrator to revoke key.

Compensating Control:
Associated identity disabled.

Status:
Open.
```


---

# Operator Infrastructure

After customer cleanup, decommission engagement infrastructure.

Review:

```text
VPS instances

Team servers

Redirectors

Domains

DNS

Object storage

VPN servers

Mail servers

Landing pages

Databases

Backups
```


---

# VPS Decommissioning

Before deleting a VPS:

```text
Export required logs

Remove customer data

Remove credentials

Remove private keys

Remove payloads

Verify no dependency remains

Destroy instance
```


---

# Cloud Provider Review

After deleting the instance, check for:

```text
Detached disks

Snapshots

Public IPs

Security groups

Backups

Images

Load balancers

DNS records
```

Deleting a VM alone may not remove all resources.


---

# Operator Workstations

Review:

```text
Downloads

Payload builds

Target lists

Credentials

Screenshots

Browser profiles

SSH keys

VPN profiles

Terminal logs

Clipboard managers

Temporary directories
```


---

# Engagement Workspace

A typical workspace might contain:

```text
engagement/
├── evidence/
├── infrastructure/
├── logs/
├── payloads/
├── reports/
├── screenshots/
└── targets/
```

Apply retention requirements separately to each category.


---

# Build Artifacts

Payload development may leave:

```text
Source

Compiled binaries

Debug builds

Symbols

Temporary files

Configuration

Secrets
```

Remove unnecessary build artifacts after evidence requirements are satisfied.


---

# Git Repositories

Review:

```bash
git status
git diff
```

Ensure customer secrets were not accidentally committed.


---

# Secret Scanning

Where appropriate, review engagement repositories for:

```text
Passwords

Tokens

API keys

Private keys

Certificates

Connection strings
```

If a secret was committed, deleting the current file may not remove it from Git history.

Rotate exposed secrets.


---

# Backups

Check whether sensitive engagement data exists in:

```text
Cloud backups

VM snapshots

Filesystem backups

Sync folders

External drives
```

Deletion from the primary workspace may not remove backups.


---

# Browser Cleanup

Dedicated engagement browser profiles should be reviewed for:

```text
Cookies

Sessions

Downloads

Saved passwords

Client certificates

Cached documents
```

Revoke server-side sessions before deleting local browser data.


---

# Password Managers

Temporary credentials stored in an engagement vault should be:

```text
Removed

Archived only if required

Rotated where necessary
```

Do not retain production credentials merely for future convenience.


---

# Communication Platforms

Review sensitive material in:

```text
Email

Teams

Slack

Ticketing systems

Shared documents
```

Follow the agreed retention policy rather than deleting organisational records without approval.


---

# Cleanup Evidence

Cleanup itself should produce evidence.

Examples:

```text
Before state

Cleanup action

After state

Verification result

Timestamp

Operator
```


---

# Cleanup Evidence Example

```text
Artifact:
RT-Test-Task

Host:
WS01

Before:
Scheduled task present

Action:
Task removed

After:
Task query returned no matching task

Verified:
Yes

Operator:
A

Time:
2026-09-05 16:22 UTC
```


---

# Screenshot Strategy

Screenshots can show:

```text
Artifact before removal

Cleanup command

Verification result
```

But avoid generating excessive screenshots for low-risk artifacts.


---

# Cleanup Report

A cleanup appendix may include:

| Artifact Type | Created | Removed | Verified | Exceptions |
|---|---:|---:|---:|---:|
| Files | 14 | 14 | 14 | 0 |
| Accounts | 3 | 2 | 2 | 1 |
| Tasks | 2 | 2 | 2 | 0 |
| Cloud Resources | 5 | 5 | 5 | 0 |
| C2 Agents | 4 | 4 | 4 | 0 |


---

# Cleanup Statement

Example:

```text
All red team artifacts recorded in the engagement inventory were
reviewed during cleanup.

Temporary payloads, scheduled tasks, routes, C2 sessions and
cloud resources were removed and their removal was verified.

One synthetic Active Directory account was retained at the
customer's request for subsequent detection-engineering
validation. Ownership and expiration are documented in the
cleanup exceptions register.
```


---

# Avoid Absolute Claims

Avoid:

```text
There are absolutely no red team artifacts anywhere.
```

Prefer:

```text
All artifacts recorded in the engagement inventory were
reviewed and either removed, verified or documented as approved
exceptions.
```

This is more defensible.


---

# Cleanup Metrics

Useful metrics include:

```text
Artifacts created

Artifacts removed

Artifacts verified

Exceptions

High-risk residuals

Time to cleanup

Cleanup failures
```


---

# Cleanup Completion Rate

```text
Verified Removed Artifacts
--------------------------  * 100
Artifacts Requiring Removal
```


---

# Exception Rate

```text
Approved Exceptions
-------------------  * 100
Tracked Artifacts
```


---

# High-Risk Residual Count

Track separately:

```text
Privileged accounts

Credentials

Persistence

Cloud access

C2 access

Network exposure
```

The desired final value is normally:

```text
0
```

unless explicitly retained by agreement.


---

# Cleanup Retest

After cleanup, test whether engagement access still works.

Examples:

```text
Test account authentication fails

SSH key authentication fails

API key rejected

C2 callback absent

Temporary port closed

Route removed

Landing page disabled
```

Use minimal verification.


---

# Do Not Recreate the Artifact During Verification

For example:

```text
Remove persistence
      |
      v
Verify persistence absent
```

not:

```text
Remove persistence
      |
      v
Recreate persistence to test cleanup
```


---

# Cleanup and Detection Validation

Cleanup can also test whether defenders observe:

```text
Account deletion

Privilege removal

Service deletion

Task removal

Cloud resource deletion
```

However, cleanup quality takes priority over creating additional detection scenarios.


---

# Cleanup and OPSEC

Cleanup reduces exposure of:

```text
Customer data

Red team infrastructure

Credentials

Payloads

Evidence

Target information
```

See:

[Red Team OPSEC](opsec.md)


---

# Cleanup and Reporting

The final report should state:

```text
Cleanup completed

Cleanup date

Scope of cleanup

Verification performed

Exceptions

Residual risk

Customer-owned artifacts
```

See:

[Red Team Reporting](reporting.md)


---

# Cleanup and Persistence

Persistence should receive dedicated cleanup verification.

See:

[Persistence](persistence.md)


---

# Cleanup and C2

C2 cleanup should include both:

```text
Customer endpoint artifacts

Operator infrastructure
```

See:

[Command and Control](command-and-control.md)


---

# Cleanup and Lateral Movement

Review:

```text
Routes

Tunnels

Temporary remote access

Pivot agents

Proxy configuration
```

See:

[Lateral Movement](lateral-movement.md)


---

# Cleanup and Phishing

Review:

```text
Mail infrastructure

Landing pages

Target lists

Synthetic accounts

OAuth applications

Campaign databases
```

See:

[Phishing](phishing.md)


---

# Cleanup and Adversary Emulation

Automated emulation platforms may leave artifacts across multiple hosts.

Use the operation log as an additional cleanup source.

See:

[Adversary Emulation](adversary-emulation.md)


---

# Cleanup Checklist

## Engagement Control

- [ ] Active testing stopped
- [ ] Automation stopped
- [ ] Final artifact inventory collected
- [ ] Operators confirmed their artifacts
- [ ] Cleanup owners assigned
- [ ] Customer contact informed
- [ ] Stop conditions still understood

## Windows

- [ ] Temporary files reviewed
- [ ] Temporary directories reviewed
- [ ] Scheduled tasks reviewed
- [ ] Services reviewed
- [ ] Registry changes reviewed
- [ ] Startup entries reviewed
- [ ] PowerShell artifacts reviewed
- [ ] Test accounts reviewed
- [ ] Group memberships reviewed
- [ ] Firewall rules reviewed
- [ ] Certificates reviewed
- [ ] Listener ports reviewed

## Linux

- [ ] Temporary files reviewed
- [ ] Temporary directories reviewed
- [ ] Users reviewed
- [ ] Groups reviewed
- [ ] sudo changes reviewed
- [ ] SSH keys reviewed
- [ ] Cron reviewed
- [ ] systemd reviewed
- [ ] Shell profiles reviewed
- [ ] Firewall rules reviewed
- [ ] Routes reviewed
- [ ] Listener ports reviewed

## Active Directory

- [ ] Test users reviewed
- [ ] Test groups reviewed
- [ ] Group memberships restored
- [ ] ACL changes restored
- [ ] Machine accounts reviewed
- [ ] SPNs reviewed
- [ ] Delegation reviewed
- [ ] GPO changes restored
- [ ] Certificates reviewed
- [ ] AD CS changes reviewed
- [ ] Authentication material revoked

## Pivoting

- [ ] Ligolo sessions stopped
- [ ] Chisel sessions stopped
- [ ] SSH tunnels stopped
- [ ] SOCKS proxies stopped
- [ ] TUN interfaces reviewed
- [ ] Routes removed
- [ ] Pivot binaries removed
- [ ] Temporary firewall rules removed

## C2

- [ ] Final agent inventory captured
- [ ] New tasking stopped
- [ ] Agents terminated
- [ ] Payloads removed
- [ ] Listeners disabled
- [ ] Redirectors reviewed
- [ ] C2 firewall rules removed
- [ ] C2 credentials revoked
- [ ] C2 certificates reviewed
- [ ] Team server data handled according to retention policy

## Credentials

- [ ] Test passwords rotated
- [ ] SSH keys removed
- [ ] API keys revoked
- [ ] Tokens revoked
- [ ] Sessions invalidated
- [ ] Certificates revoked or removed
- [ ] OAuth secrets removed
- [ ] Credential files removed
- [ ] Sensitive tool output reviewed

## Cloud

- [ ] VMs reviewed
- [ ] Disks reviewed
- [ ] Snapshots reviewed
- [ ] Storage reviewed
- [ ] Public IPs reviewed
- [ ] Security groups reviewed
- [ ] IAM users reviewed
- [ ] Roles reviewed
- [ ] Service principals reviewed
- [ ] Applications reviewed
- [ ] API keys reviewed
- [ ] Tokens reviewed
- [ ] DNS reviewed
- [ ] Remaining cost-generating resources reviewed

## Containers

- [ ] Containers reviewed
- [ ] Images reviewed
- [ ] Volumes reviewed
- [ ] Networks reviewed
- [ ] Secrets reviewed
- [ ] Temporary Docker resources removed

## Kubernetes

- [ ] Pods reviewed
- [ ] Deployments reviewed
- [ ] Jobs reviewed
- [ ] CronJobs reviewed
- [ ] Services reviewed
- [ ] ConfigMaps reviewed
- [ ] Secrets reviewed
- [ ] ServiceAccounts reviewed
- [ ] RoleBindings reviewed
- [ ] ClusterRoleBindings reviewed

## Phishing

- [ ] Campaign delivery stopped
- [ ] Landing pages disabled
- [ ] Campaign forms disabled
- [ ] Mailboxes reviewed
- [ ] Target lists reviewed
- [ ] Synthetic accounts removed
- [ ] OAuth applications removed
- [ ] Tokens revoked
- [ ] DNS reviewed
- [ ] Campaign databases reviewed
- [ ] Unexpected credentials handled

## Social Engineering

- [ ] Test identities retired
- [ ] Visitor badges returned
- [ ] USB devices recovered
- [ ] Printed materials recovered
- [ ] QR content disabled
- [ ] Test phone infrastructure reviewed

## Collection and Exfiltration

- [ ] Staging directories removed
- [ ] Temporary archives removed
- [ ] Synthetic datasets removed
- [ ] Red team copies of production data reviewed
- [ ] Exfiltration destination disabled
- [ ] Temporary storage removed
- [ ] Transfer credentials revoked

## Operator Infrastructure

- [ ] VPS instances reviewed
- [ ] Team servers reviewed
- [ ] Redirectors reviewed
- [ ] Mail servers reviewed
- [ ] Landing servers reviewed
- [ ] Object storage reviewed
- [ ] VPN infrastructure reviewed
- [ ] Domains reviewed
- [ ] DNS reviewed
- [ ] Certificates reviewed
- [ ] Detached disks reviewed
- [ ] Snapshots reviewed
- [ ] Backups reviewed

## Operator Workstations

- [ ] Customer credentials reviewed
- [ ] Browser sessions reviewed
- [ ] Downloads reviewed
- [ ] Payloads reviewed
- [ ] Build artifacts reviewed
- [ ] SSH keys reviewed
- [ ] VPN profiles reviewed
- [ ] Repository secrets reviewed
- [ ] Temporary data reviewed

## Evidence

- [ ] Required evidence retained
- [ ] Unnecessary raw data removed
- [ ] Credentials removed from evidence
- [ ] Tokens redacted
- [ ] Personal data minimised
- [ ] Evidence encrypted
- [ ] Retention date recorded

## Verification

- [ ] Files verified absent
- [ ] Accounts verified removed/disabled
- [ ] Privileges verified removed
- [ ] Persistence verified removed
- [ ] Credentials verified revoked
- [ ] Sessions verified invalid
- [ ] Routes verified removed
- [ ] Listeners verified closed
- [ ] Cloud resources verified removed
- [ ] Phishing infrastructure verified disabled
- [ ] Residual artifact search completed

## Handover

- [ ] Customer-owned artifacts documented
- [ ] Exceptions documented
- [ ] Exception owners assigned
- [ ] Expiration dates assigned
- [ ] Residual risks documented
- [ ] Indicators handed over where agreed
- [ ] Cleanup statement prepared


---

# Host Cleanup Decision Model

```text
                    ARTIFACT
                       |
                       v
              CREATED BY RED TEAM?
                /             \
              No               Yes
              |                 |
              v                 v
         DO NOT REMOVE      ORIGINAL STATE
                                 |
                                 v
                          CLEANUP DEFINED?
                            /         \
                          No           Yes
                          |             |
                          v             v
                       REVIEW        REMOVE /
                                     RESTORE
                                        |
                                        v
                                     VERIFY
                                        |
                                  +-----+-----+
                                  |           |
                                  v           v
                               Present      Absent
                                  |           |
                                  v           v
                                Retry       Complete
```


---

# Credential Cleanup Decision Model

```text
                    CREDENTIAL
                        |
                        v
                  ENGAGEMENT USE?
                    /        \
                  No          Yes
                  |            |
                  v            v
             DO NOT ALTER   STILL REQUIRED?
                             /         \
                           Yes          No
                           |             |
                           v             v
                        HANDOVER       REVOKE
                           |             |
                           v             v
                        OWNER         INVALIDATE
                                         |
                                         v
                                      VERIFY
```


---

# Unknown Artifact Decision Model

```text
                   UNKNOWN ARTIFACT
                          |
                          v
                   RED TEAM RECORD?
                     /          \
                   Yes           No
                   |              |
                   v              v
                CLEANUP        PRESERVE
                                  |
                                  v
                              DECONFLICT
                                  |
                         +--------+--------+
                         |                 |
                         v                 v
                    LEGITIMATE         SUSPICIOUS
                         |                 |
                         v                 v
                       LEAVE         INCIDENT PROCESS
```


---

# Infrastructure Cleanup Decision Model

```text
                   INFRASTRUCTURE
                         |
                         v
                  STILL REQUIRED?
                    /          \
                  Yes           No
                  |              |
                  v              v
              DOCUMENT        EXPORT
                              REQUIRED
                                DATA
                                  |
                                  v
                            REMOVE SECRETS
                                  |
                                  v
                           REMOVE CUSTOMER
                                DATA
                                  |
                                  v
                              DESTROY
                                  |
                                  v
                           CHECK RESIDUALS
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
                 Found                        None
                    |                           |
                    v                           v
                 Remove                      Complete
```


---

# Cleanup Verification Model

```text
                   INVENTORY
                       |
                       v
                 CLEANUP ACTION
                       |
                       v
                   VALIDATION
                       |
             +---------+---------+
             |                   |
             v                   v
         Artifact             Artifact
         Present              Absent
             |                   |
             v                   v
          Retry               Verify
             |                   |
             v                   v
          Escalate             Close
          if Needed
```


---

# Cleanup Maturity Model

```text
Level 1
Cleanup performed from operator memory

Level 2
Artifacts documented during engagement

Level 3
Cleanup procedures and verification recorded

Level 4
Central artifact inventory with independent verification

Level 5
Lifecycle-controlled infrastructure, automated expiration,
credential revocation and continuous residual validation
```


---

# Final Cleanup Model

```text
                     ENGAGEMENT
                         |
                         v
                  CHANGE INVENTORY
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
        HOSTS        IDENTITIES    INFRASTRUCTURE
          |              |              |
          v              v              v
        FILES         ACCOUNTS          C2
        TASKS         GROUPS          CLOUD
       SERVICES      CREDENTIALS       DNS
       CONFIG          TOKENS         MAIL
          |              |              |
          +--------------+--------------+
                         |
                         v
                       STOP
                    ACTIVE TESTING
                         |
                         v
                       REMOVE
                         |
                         v
                       RESTORE
                         |
                         v
                       REVOKE
                         |
                         v
                       VERIFY
                         |
              +----------+----------+
              |                     |
              v                     v
           COMPLETE              EXCEPTION
              |                     |
              v                     v
          DOCUMENT              OWNER / DATE
              |                     |
              +----------+----------+
                         |
                         v
                      HANDOVER
                         |
                         v
                  RETENTION REVIEW
                         |
                         v
                ENGAGEMENT CLOSED
```


---

# Core Principle

Red team cleanup can be reduced to:

```text
Plan cleanup before deployment.

Track every meaningful change.

Record the original state.

Assign every artifact an owner.

Stop active operations before cleanup.

Remove only confirmed engagement artifacts.

Restore configuration instead of blindly deleting it.

Remove persistence.

Remove temporary privileges.

Remove temporary accounts.

Revoke credentials and tokens.

Terminate sessions.

Remove tunnels and routes.

Remove payloads and tools.

Decommission C2 infrastructure.

Review cloud residuals.

Retire phishing infrastructure.

Remove unnecessary customer data.

Preserve defensive telemetry.

Do not clear logs.

Do not delete unknown artifacts.

Escalate possible real compromise.

Verify every high-risk cleanup action.

Document customer-owned artifacts.

Document every exception.

Retain only required evidence.

Verify residual access is gone.

Close the engagement only after cleanup is verified.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Red Team Infrastructure](infrastructure.md)
- [Reconnaissance](reconnaissance.md)
- [Initial Access](initial-access.md)
- [Execution](execution.md)
- [Discovery](discovery.md)
- [Privilege Escalation](privilege-escalation.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Collection](collection.md)
- [Exfiltration](exfiltration.md)
- [Command and Control](command-and-control.md)
- [Social Engineering](social-engineering.md)
- [Phishing](phishing.md)
- [Adversary Emulation](adversary-emulation.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-61 - Incident Response Recommendations and Considerations for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }
- [Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - App Control for Business](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Microsoft Defender for Endpoint](https://learn.microsoft.com/defender-endpoint/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Microsoft Entra Audit Logs](https://learn.microsoft.com/entra/identity/monitoring-health/concept-audit-logs){ target="_blank" rel="noopener noreferrer" }
- [Kubernetes - RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/){ target="_blank" rel="noopener noreferrer" }
- [Docker Documentation](https://docs.docker.com/){ target="_blank" rel="noopener noreferrer" }
- [OWASP - Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "The artifact inventory is the cleanup plan"
    If every account, file, route, service, task, credential, cloud resource, payload and infrastructure change is recorded when it is created, cleanup becomes a controlled verification exercise instead of a memory exercise.


!!! warning "Cleanup is not anti-forensics"
    Never clear logs, destroy defensive telemetry or remove unknown suspicious artifacts under the label of cleanup. Red team artifacts should be removed, but evidence needed for detection validation, incident response and customer investigation should remain available according to the engagement agreement.
