---
title: NetExec Cheatsheet
description: Detailed practical NetExec reference for authorised Active Directory and Windows security assessments covering SMB, LDAP, WinRM, MSSQL, SSH, authentication, enumeration, shares, users, groups, sessions, permissions, Kerberos, certificates, result interpretation and troubleshooting.
---

# NetExec Cheatsheet

NetExec is a network service enumeration and assessment framework commonly used during authorised Windows and Active Directory security testing.

It provides a consistent interface for interacting with protocols such as:

```text
SMB

LDAP

WinRM

MSSQL

SSH

FTP

RDP
```

This cheatsheet focuses on a practical workflow:

```text
What protocol is available?
        |
        v
Can I authenticate?
        |
        v
What does that access provide?
        |
        v
What can I enumerate?
        |
        v
Is anything security relevant?
        |
        v
What should I verify next?
```

For broader Active Directory methodology, see the [Active Directory Cheatsheet](active-directory.md).

!!! warning "Authorised Security Testing"
    Only use NetExec against systems and accounts that are explicitly within the authorised scope. Authentication testing, enumeration and remote actions can create logs, trigger detections, lock accounts or affect production systems.


# Quick Start

A common NetExec workflow is:

```text
Identify Targets
      |
      v
Identify Protocol
      |
      v
Collect Basic Host Information
      |
      v
Validate One Credential
      |
      v
Determine Privilege
      |
      v
Enumerate Relevant Resources
      |
      v
Investigate Interesting Results
      |
      v
Validate Minimally
      |
      v
Capture Evidence
```


# Installation

Follow the current NetExec installation documentation where possible.

Check whether NetExec is already available:

```bash
which nxc
```

Version:

```bash
nxc --version
```

General help:

```bash
nxc --help
```

### Why Version Matters

NetExec changes over time.

Options shown in:

```text
Old blog posts

Archived CrackMapExec guides

CTF writeups

Older pentest notes
```

may no longer match the installed version.

Before using a protocol-specific option, check:

```bash
nxc <protocol> --help
```

For example:

```bash
nxc smb --help
```

or:

```bash
nxc ldap --help
```


# Supported Protocols

List the protocols supported by the installed version:

```bash
nxc --help
```

Depending on the version, protocols may include:

```text
smb

ldap

winrm

mssql

ssh

ftp

rdp

wmi
```

Do not assume every installation exposes exactly the same protocol set.


# General Syntax

The basic structure is:

```bash
nxc <protocol> <target> [options]
```

Examples:

```bash
nxc smb 10.10.10.10
```

```bash
nxc ldap 10.10.10.10
```

```bash
nxc winrm 10.10.10.20
```


# Target Formats

NetExec can work with several target formats.

## Single IP

```bash
nxc smb 10.10.10.20
```

## Hostname

```bash
nxc smb srv01.corp.local
```

## Network Range

```bash
nxc smb 10.10.10.0/24
```

## Target File

Create:

```text
10.10.10.10
10.10.10.20
10.10.10.30
```

Then:

```bash
nxc smb targets.txt
```

!!! caution
    Do not move from a single-host test to an entire subnet merely because NetExec supports CIDR ranges. Confirm the engagement scope and authentication-testing constraints first.


# Example Environment

Examples throughout this page use:

```text
Domain:   corp.local
DC:       dc01.corp.local
DC IP:    10.10.10.10
Server:   srv01.corp.local
Server IP:10.10.10.20
User:     asif
```

Example password:

```text
Password123!
```

These are placeholders for a controlled environment.


# Protocol-First Methodology

Use NetExec as a protocol assessment tool rather than as a single "Active Directory attack command".

```text
Target
  |
  +--> SMB
  |
  +--> LDAP
  |
  +--> WinRM
  |
  +--> MSSQL
  |
  +--> SSH
  |
  +--> Other Supported Protocols
```

Each protocol answers different questions.


# SMB

SMB is one of the most useful NetExec protocols for Windows and Active Directory assessment.

It can provide information about:

```text
Hostname

Domain

Operating system

SMB signing

SMBv1

Authentication

Shares

Local access

Administrative access
```


# Basic SMB Enumeration

```bash
nxc smb 10.10.10.20
```

### Representative Output

```text
SMB  10.10.10.20  445  SRV01  [*] Windows Server 2022 Build 20348 x64 (name:SRV01) (domain:corp.local) (signing:True) (SMBv1:False)
```

### How to Read the Result

Important fields include:

```text
10.10.10.20

SRV01

Windows Server 2022

corp.local

signing:True

SMBv1:False
```

This provides environmental context before authentication is attempted.


# SMB Signing

Example:

```text
(signing:True)
```

SMB signing affects the integrity protection of SMB communications and is relevant when assessing certain authentication-relay scenarios.

Do not automatically report:

```text
signing:False
```

as a complete vulnerability.

Instead determine:

```text
Is signing optional or disabled?

Which system is affected?

Can authentication reach the target?

Is NTLM being used?

Are other relay prerequisites present?

What privilege would the relayed identity have?
```


# SMBv1

Example:

```text
(SMBv1:False)
```

This indicates NetExec did not identify SMBv1 as enabled for the tested service.

If SMBv1 is reported as enabled, investigate why the legacy protocol is still required and validate the actual configuration before reporting.


# Validate a Password

```bash
nxc smb 10.10.10.20 -u 'asif' -p 'Password123!'
```

### Representative Output

```text
SMB  10.10.10.20  445  SRV01  [+] corp.local\asif:Password123!
```

### Interpretation

`[+]` indicates that authentication succeeded for the tested SMB authentication path.

It demonstrates:

```text
The account was accepted by the target.
```

It does not demonstrate:

```text
Local administrator

Domain administrator

Remote code execution

Access to every share

Access to other systems
```


# Failed Authentication

Representative output may contain:

```text
[-] corp.local\asif:Password123! STATUS_LOGON_FAILURE
```

Possible explanations include:

```text
Incorrect password

Incorrect username

Wrong domain

Authentication restrictions

Account state

Authentication method mismatch
```

Do not immediately retry many passwords.


# Locked Account

If the result indicates:

```text
STATUS_ACCOUNT_LOCKED_OUT
```

stop authentication attempts for that account.

Record:

```text
Account

Target

Timestamp

Test performed
```

and follow the engagement's escalation procedure.


# Disabled or Restricted Accounts

Authentication errors can also reflect:

```text
Disabled account

Expired account

Logon restrictions

Password expiration

Workstation restrictions

Policy restrictions
```

A failed SMB login is therefore not always proof that the password itself is incorrect.


# Local vs Domain Authentication

This distinction is important.

A username may represent:

```text
CORP\asif
```

or:

```text
SRV01\administrator
```

Those are different security principals.


# Domain Authentication

Typical domain credential test:

```bash
nxc smb 10.10.10.20 -d corp.local -u 'asif' -p 'Password123!'
```

Alternatively, depending on the installed version and environment:

```bash
nxc smb 10.10.10.20 -u 'asif' -p 'Password123!' -d corp.local
```


# Local Authentication

For a specifically authorised local account, review:

```bash
nxc smb --help
```

for the installed version's local-authentication option.

Do not accidentally interpret a local account as a domain account or vice versa.


# Administrative Access

A successful administrative result may resemble:

```text
SMB  10.10.10.20  445  SRV01  [+] corp.local\asif:Password123! (Pwn3d!)
```

### What `Pwn3d!` Means

NetExec uses `(Pwn3d!)` to indicate administrative-level access relevant to the tested protocol/host.

This is substantially different from:

```text
[+]
```

alone.


# Compare Results

## Authentication Only

```text
[+] corp.local\asif:Password123!
```

Interpretation:

```text
Credential accepted.
```

## Administrative Access

```text
[+] corp.local\asif:Password123! (Pwn3d!)
```

Interpretation:

```text
Credential accepted and administrative-level access identified
for the tested SMB target.
```


# What to Do After `Pwn3d!`

Do not immediately execute commands.

First determine:

```text
Why is the account an administrator?

Is it directly assigned?

Is access inherited through a group?

Is the account supposed to administer this server?

Does the same relationship exist elsewhere?

Does the host contain sensitive administrative sessions?

Does this create an attack path?
```

Useful next steps may include:

```text
Review group membership

Review BloodHound relationships

Review local administrative design

Document affected host

Validate only the minimum required privilege
```


# Enumerate Shares

```bash
nxc smb 10.10.10.20 -u 'asif' -p 'Password123!' --shares
```

### Representative Output

```text
SMB  10.10.10.20  445  SRV01  Share       Permissions
SMB  10.10.10.20  445  SRV01  -----       -----------
SMB  10.10.10.20  445  SRV01  ADMIN$      READ
SMB  10.10.10.20  445  SRV01  C$          READ
SMB  10.10.10.20  445  SRV01  Public      READ,WRITE
SMB  10.10.10.20  445  SRV01  Software    READ
```

### Interpretation

Focus on:

```text
Share name

Read access

Write access

Administrative shares

Business purpose
```


# Writable Shares

Example:

```text
Public READ,WRITE
```

A writable share is a candidate, not automatically a vulnerability.

Investigate:

```text
Who is expected to write?

What files are stored there?

Are files executed?

Are files imported by applications?

Does a privileged process consume files?

Can configuration be changed?

Could business data be altered?
```


# Readable Shares

Readable shares may expose:

```text
Configuration

Scripts

Documentation

Deployment packages

Backups

Credentials

API keys

Connection strings
```

But ordinary read access to a public business share may be completely expected.


# Administrative Shares

Common administrative shares include:

```text
ADMIN$

C$

IPC$
```

Access to these shares should be interpreted in the context of the account's administrative rights.


# Enumerating Multiple Targets

```bash
nxc smb targets.txt -u 'asif' -p 'Password123!' --shares
```

This can be useful after the scope and credential-testing plan have been confirmed.

For large environments, prefer targeted enumeration rather than unnecessarily querying every host.


# Save Output

Shell redirection:

```bash
nxc smb targets.txt -u 'asif' -p 'Password123!' --shares | tee nxc-shares.txt
```

This provides a local assessment artefact.

Be aware that output files may contain:

```text
Usernames

Hostnames

Domains

Credential strings supplied on the command line
```

Store them according to the engagement's evidence-handling requirements.


# Target Inventory

Basic SMB enumeration across an authorised target list:

```bash
nxc smb targets.txt
```

This can quickly provide an inventory such as:

```text
DC01    Windows Server
SRV01   Windows Server
WS01    Windows 11
WS02    Windows 11
```


# Parse Interesting Hosts

Instead of immediately launching additional actions, first identify categories:

```text
Domain Controllers

Member Servers

Workstations

Legacy Hosts

Systems Without Expected Signing

Systems Accepting the Credential

Systems Where Administrative Access Exists
```


# SMB Workflow

```text
SMB Target
    |
    v
Basic Enumeration
    |
    v
Hostname / Domain / OS
    |
    v
Signing / SMB Version
    |
    v
Credential Available?
   / \
 No   Yes
 |     |
 v     v
Stop  Validate
       |
       v
Authentication Successful?
       |
   +---+---+
   |       |
  No      Yes
   |       |
   v       v
Review   Shares
Error      |
           v
      Admin Access?
       /       \
     No         Yes
     |           |
     v           v
 Document    Determine Why
```


# LDAP

LDAP is particularly valuable against Active Directory domain controllers.

It can help enumerate:

```text
Users

Groups

Computers

SPNs

Delegation

Directory relationships

Domain configuration
```


# Basic LDAP Connection

```bash
nxc ldap 10.10.10.10
```

### Representative Output

Depending on the environment/version, NetExec may identify information such as:

```text
Domain controller

Domain

Hostname

LDAP availability
```


# LDAP Authentication

```bash
nxc ldap 10.10.10.10 -u 'asif' -p 'Password123!'
```

### Interpretation

Successful LDAP authentication means the account can authenticate to the directory service through the tested path.

This commonly enables directory enumeration according to the permissions granted to that principal.


# LDAP Help First

Because LDAP enumeration flags can change between NetExec releases, check:

```bash
nxc ldap --help
```

Look for capabilities relevant to:

```text
Users

Groups

Computers

SPNs

Delegation

LDAP queries

BloodHound
```


# Why LDAP Is Valuable

SMB may tell you:

```text
Credential works.
```

LDAP can help answer:

```text
Who is the account?

Which groups is it in?

Which users exist?

Which computers exist?

Which service accounts exist?

Which directory relationships exist?
```


# LDAP Enumeration Workflow

```text
Domain Credentials
       |
       v
LDAP Authentication
       |
       v
Users
       |
       v
Groups
       |
       v
Computers
       |
       v
Service Accounts
       |
       v
Delegation
       |
       v
Interesting Relationships
       |
       v
BloodHound / Manual Validation
```


# LDAP Result Interpretation

Do not treat directory enumeration output as vulnerabilities by itself.

Examples:

```text
User exists
```

is inventory.

```text
User has SPN
```

is a Kerberos assessment candidate.

```text
Account has delegated control over privileged group
```

may represent a privilege path.

Context determines significance.


# Users

Use:

```bash
nxc ldap --help
```

to identify the current version's user-enumeration functionality.

When user information is returned, prioritise attributes such as:

```text
Username

Description

Enabled state

Group membership

Service-account indicators

Password-related configuration

Administrative purpose
```


# User Descriptions

Descriptions sometimes contain operational information.

Example:

```text
svc_backup - Backup service account
```

This is useful context.

If a description contains what appears to be a password or secret, treat it as sensitive evidence and validate carefully rather than immediately using it across the environment.


# Groups

Group enumeration helps identify:

```text
Administrative groups

Helpdesk groups

Server-management groups

Application administrators

Backup operators

Custom delegated groups
```

Custom groups can be as security-sensitive as built-in groups.


# Computers

Computer enumeration helps build:

```text
Domain controller inventory

Server inventory

Workstation inventory

Management infrastructure

Potential attack-path targets
```

Correlate directory data with actual network reachability rather than assuming every computer object is online.


# SPNs

Service Principal Names are important for identifying Kerberos service accounts.

Use the current LDAP help:

```bash
nxc ldap --help
```

to identify supported SPN enumeration capabilities.

Interpret SPN results as:

```text
Potential service-account relationship
```

not:

```text
Password compromised
```


# Delegation

NetExec LDAP capabilities may assist with identifying delegation configuration.

Relevant categories include:

```text
Unconstrained Delegation

Constrained Delegation

Resource-Based Constrained Delegation
```

For deeper analysis use:

- [Active Directory Cheatsheet](active-directory.md)
- [Unconstrained Delegation](../active-directory/unconstrained-delegation.md)
- [Constrained Delegation](../active-directory/constrained-delegation.md)
- [RBCD](../active-directory/rbcd.md)


# BloodHound Through NetExec

Some NetExec versions expose BloodHound-related LDAP functionality.

Check:

```bash
nxc ldap --help
```

before using it.

When available, consider:

```text
Collection method

DNS configuration

Domain controller

Scope

Operational impact

Output location
```

For full collection and graph interpretation, see the [BloodHound Cheatsheet](bloodhound.md).


# WinRM

WinRM provides remote Windows management.

Typical ports:

```text
5985 - HTTP

5986 - HTTPS
```


# Basic WinRM Check

```bash
nxc winrm 10.10.10.20
```

This can determine whether the service is available to NetExec.

Network exposure alone does not demonstrate access.


# WinRM Credential Validation

```bash
nxc winrm 10.10.10.20 -u 'asif' -p 'Password123!'
```

### Representative Outcome

A successful result indicates that the supplied account was accepted for the tested WinRM path.

Depending on version and permissions, NetExec may also identify elevated access.


# WinRM Interpretation

Separate:

```text
Port Open

Service Recognised

Authentication Successful

Remote Management Authorised

Administrative Privilege
```

These are different conclusions.


# What to Check After WinRM Authentication

Determine:

```text
Which group grants access?

Is the account a Remote Management Users member?

Is it an administrator?

Is access expected?

Which systems expose the same management path?
```


# WinRM Workflow

```text
Port 5985/5986
      |
      v
WinRM Available
      |
      v
Credential
      |
      v
Authentication
      |
   +--+--+
   |     |
 Fail  Success
   |     |
   v     v
Review  Determine
Error   Privilege
          |
          v
      Is Access Expected?
```


# MSSQL

NetExec can also interact with Microsoft SQL Server where supported.

Check:

```bash
nxc mssql --help
```

Basic target:

```bash
nxc mssql 10.10.10.30
```


# MSSQL Authentication

For an authorised account:

```bash
nxc mssql 10.10.10.30 -u 'asif' -p 'Password123!'
```

Review the installed version's options for:

```text
Windows authentication

Domain authentication

SQL authentication

Encryption

Port selection
```


# MSSQL Interpretation

Successful database authentication does not automatically mean:

```text
Database administrator

Operating-system administrator

Remote command execution
```

Determine:

```text
Database role

Server role

Database permissions

Linked servers

Authentication mode

Service-account context
```


# MSSQL Security Questions

After authentication, ask:

```text
Which SQL roles does the account hold?

Which databases are accessible?

Is the account sysadmin?

Are linked servers configured?

What identity runs SQL Server?

Are dangerous server features enabled?

Is the privilege expected?
```


# SSH

Where the installed NetExec version supports SSH:

```bash
nxc ssh --help
```

Basic service check:

```bash
nxc ssh 10.10.10.40
```

Credential validation:

```bash
nxc ssh 10.10.10.40 -u 'asif' -p 'Password123!'
```


# SSH Interpretation

Successful SSH authentication demonstrates access to the target under the supplied identity.

It does not automatically imply:

```text
root

sudo

administrator

privilege escalation
```

Follow with normal Linux privilege and configuration assessment.


# FTP

Where supported:

```bash
nxc ftp --help
```

Basic check:

```bash
nxc ftp 10.10.10.50
```

Authentication:

```bash
nxc ftp 10.10.10.50 -u 'asif' -p 'Password123!'
```

Assess:

```text
Authentication

Readable directories

Writable directories

Data sensitivity

Application relationships
```

Do not upload or modify files unless required and authorised.


# RDP

Where supported:

```bash
nxc rdp --help
```

Use RDP testing to distinguish:

```text
RDP reachable

Authentication accepted

Interactive logon permitted
```

These are not equivalent.


# NTLM Hash Authentication

NetExec supports NTLM hash-based authentication for relevant protocols.

First inspect:

```bash
nxc smb --help
```

for the installed version's hash option.

A common form for authorised SMB testing is:

```bash
nxc smb 10.10.10.20 -u 'asif' -H '0123456789abcdef0123456789abcdef'
```

### Interpretation

If authentication succeeds, the tested NTLM credential material was sufficient for authentication to that target through the selected protocol.

This does not mean:

```text
The plaintext password is known.

The account is Domain Admin.

Every host accepts the hash.
```


# Hash Validation Strategy

Avoid:

```text
Hash
 |
 v
Entire /16 Network
```

Prefer:

```text
Hash
 |
 v
Identify Account
 |
 v
Identify Expected Administrative Scope
 |
 v
Choose One Authorised Target
 |
 v
Validate
 |
 v
Determine Privilege
 |
 v
Expand Only If Necessary
```


# Kerberos Authentication

NetExec supports Kerberos authentication for relevant protocols.

Check:

```bash
nxc smb --help
```

and:

```bash
nxc ldap --help
```

for the installed version's Kerberos options.

Before troubleshooting NetExec, verify the ticket cache:

```bash
klist
```

Check:

```bash
echo "$KRB5CCNAME"
```


# Kerberos Troubleshooting

Common causes of failure include:

```text
DNS

Clock skew

Incorrect SPN

Incorrect hostname

Missing ticket

Expired ticket

Wrong realm

Ticket cache not exported
```

Kerberos frequently depends on correct hostnames, so avoid replacing hostnames with IP addresses without understanding the protocol consequences.


# Password Spraying

NetExec can authenticate many usernames and passwords efficiently.

That does not mean it should be used casually for password spraying.

Before any spray:

```text
Explicitly authorised?

Lockout threshold known?

Observation window known?

Excluded accounts known?

Approved password count known?

Approved rate known?

SOC informed if required?
```

If any of these are unresolved, do not begin the spray.


# Account Lockout Policy

From a domain-connected Windows system:

```cmd
net accounts /domain
```

Review:

```text
Lockout threshold

Lockout duration

Observation window
```

Remember that fine-grained password policies may differ from the domain default.


# Authentication Matrix

Maintain a controlled matrix rather than repeatedly guessing.

| Account | Target | Protocol | Result | Privilege |
|---|---|---|---|---|
| `CORP\asif` | DC01 | SMB | Success | User |
| `CORP\asif` | SRV01 | SMB | Success | Admin |
| `CORP\asif` | SRV01 | WinRM | Success | Remote access |
| `CORP\asif` | SQL01 | MSSQL | Fail | N/A |

This makes the emerging access model much easier to understand.


# "I Have Credentials - What Do I Do?"

```text
Credential
   |
   v
Identify Domain
   |
   v
Choose One Target
   |
   v
SMB Validation
   |
   v
LDAP Validation
   |
   v
Shares
   |
   v
Users / Groups / Computers
   |
   v
BloodHound
   |
   v
WinRM Where Relevant
   |
   v
Other Services
   |
   v
Privilege Relationships
```


# "I Got `[+]` - What Does It Mean?"

```text
[+]
 |
 v
Authentication succeeded
```

Next ask:

```text
What protocol?

What target?

What account?

What access was granted?

Is it expected?

What can be safely enumerated?
```


# "I Got `Pwn3d!` - What Next?"

```text
Pwn3d!
   |
   v
Administrative Access Candidate
   |
   v
Confirm Target
   |
   v
Confirm Account
   |
   v
Determine Why Access Exists
   |
   v
Group / Policy / Local Assignment?
   |
   v
Is Access Expected?
   |
   v
Document Attack-Path Relevance
```


# "I Found a Writable Share - What Next?"

```text
Writable Share
     |
     v
Identify Purpose
     |
     v
Review Contents
     |
     v
Who Writes?
     |
     v
Who Reads?
     |
     v
Does Privileged Software Consume Files?
     |
   +-+--+
   |    |
  No   Yes
   |    |
   v    v
Document Further
Context  Validation
```


# "I Found Lots of Hosts - What Next?"

Classify them.

```text
Hosts
 |
 +--> Domain Controllers
 |
 +--> Servers
 |
 +--> Workstations
 |
 +--> Database Servers
 |
 +--> Management Systems
 |
 +--> Legacy Systems
 |
 +--> Unknown Systems
```

Then prioritise based on the assessment objective.


# "My Credential Works Everywhere"

Do not immediately interpret this as a vulnerability.

Determine:

```text
Is the account expected to have broad access?

Is it an administrator?

Is it a service account?

Is it a management account?

Is the same password being reused?

Is access granted through domain groups?

Which systems represent sensitive boundaries?
```


# "My Credential Is Admin on Several Hosts"

Build the relationship:

```text
CORP\asif
    |
    +--> Admin on WS01
    |
    +--> Admin on WS02
    |
    +--> Admin on SRV01
```

Then investigate why.

BloodHound can help model this relationship.


# Target Selection

Good target selection reduces unnecessary activity.

Prioritise:

```text
Domain controllers

Management servers

Application servers

Database servers

Hosts related to the objective

Hosts indicated by BloodHound

Systems where current credentials have expected relevance
```


# Avoid Blind Network-Wide Execution

NetExec makes commands such as this technically easy:

```bash
nxc smb 10.10.10.0/24 ...
```

But assessment quality improves when the operator first understands:

```text
What am I trying to prove?

Why do I need every host?

What will the authentication traffic look like?

Could accounts lock?

Will the SOC interpret this as an incident?

Can I prove the same thing against fewer systems?
```


# Modules

NetExec provides modules that extend protocol functionality.

List or inspect module functionality using the options provided by the installed version:

```bash
nxc smb --help
```

and the NetExec documentation.

Modules can vary between versions.


# Module Safety

Before running a module, determine:

```text
What does it query?

Does it write anything?

Does it execute remotely?

Does it access credentials?

Does it modify configuration?

Does it create files?

Does it start services?

Does it generate significant authentication traffic?
```

Do not treat every enumeration module as passive.


# Remote Execution

Some NetExec functionality can perform remote command execution when sufficient administrative access exists.

During an assessment, remote execution should only be used when:

```text
It is explicitly within scope.

Administrative access has already been established.

The command is necessary to prove the objective.

The command is low impact.

The expected artefacts are understood.

Cleanup is possible.
```

Do not execute commands merely because `(Pwn3d!)` appears.


# Safer Validation Principle

Prefer:

```text
Enumerate
   |
   v
Establish Permission
   |
   v
Minimal Validation
   |
   v
Stop
```

over:

```text
Admin Access
   |
   v
Run Many Commands
   |
   v
Dump Everything
```


# Credential Access

NetExec may expose functionality related to credential material on systems where administrative rights are available.

Credential extraction is sensitive because it may expose:

```text
Password hashes

Cached credentials

Service secrets

LSA secrets

Domain credentials
```

Only perform credential-access actions when explicitly required by the assessment and covered by the rules of engagement.

Before doing so, determine whether the same security conclusion can be demonstrated with less sensitive evidence.


# Credential Evidence Handling

If sensitive credential material is collected:

```text
Minimise collection.

Do not place secrets in screenshots unnecessarily.

Encrypt evidence at rest.

Restrict access.

Follow retention requirements.

Remove temporary artefacts.

Do not publish secrets in reports.
```


# Domain Controller Caution

Domain controllers contain highly sensitive directory information.

Do not treat a DC like an ordinary member server.

Before performing any privileged action against a DC, confirm:

```text
Explicit scope

Business justification

Testing method

Potential impact

Data-handling requirements

Cleanup

Escalation contact
```


# NetExec and BloodHound

A useful division of responsibility is:

```text
NetExec
   |
   v
Validate Services and Access
   |
   v
BloodHound
   |
   v
Model Relationships
   |
   v
NetExec / Native Tools
   |
   v
Validate Specific Relationship
```


# NetExec and Impacket

NetExec is useful for:

```text
Broad protocol-oriented enumeration

Authentication validation

Host inventories

Access mapping
```

Impacket is useful when a more specialised protocol utility is required.

```text
NetExec
   |
   v
Find Interesting Relationship
   |
   v
Impacket
   |
   v
Perform Focused Protocol Validation
```

See the [Impacket Cheatsheet](impacket.md).


# NetExec and Active Directory

Use NetExec within the broader AD workflow:

```text
Network
   |
   v
NetExec
   |
   v
Access Mapping
   |
   v
LDAP
   |
   v
BloodHound
   |
   v
Kerberos / AD CS / ACL Analysis
   |
   v
Focused Validation
```


# NetExec and PrivEsc

NetExec can reveal:

```text
Administrative access

Remote-management access

Interesting shares

Host relationships
```

For host-level privilege escalation candidates use the [PrivEsc Explorer](../privesc/index.md).


# Output Interpretation

NetExec output is useful evidence, but it must be interpreted.

## Informational

Example:

```text
Windows Server 2022
```

This identifies platform information.

It is not a vulnerability.


## Security Configuration

Example:

```text
signing:False
```

This may affect a security scenario but requires prerequisite analysis.


## Authentication Evidence

Example:

```text
[+] CORP\asif:Password123!
```

This demonstrates successful authentication.


## Privilege Evidence

Example:

```text
(Pwn3d!)
```

This indicates administrative-level access identified by NetExec for the tested context.


## Resource Permission

Example:

```text
Public READ,WRITE
```

This demonstrates the tested identity's access to the share.

Impact depends on how the share is used.


# Evidence Template

For an important NetExec result record:

```text
Test ID:
AD-NXC-001

Timestamp:
2026-09-06 14:30 UTC

Tool:
NetExec

Version:
<record installed version>

Source:
Assessment workstation

Target:
SRV01 / 10.10.10.20

Protocol:
SMB

Identity:
CORP\asif

Objective:
Determine whether the standard domain account has administrative
access to SRV01.

Command:
nxc smb 10.10.10.20 -u asif -p <redacted>

Result:
Authentication successful.
Administrative access identified.

Interpretation:
The tested domain account has administrative-level access to the
target through the assessed SMB context.

Further Validation:
Determine which group or local assignment grants the privilege.

Evidence:
Relevant NetExec output captured.

Cleanup:
No modification performed.
```


# Report Passwords Safely

Do not include:

```bash
nxc smb 10.10.10.20 -u asif -p 'ActualProductionPassword'
```

in a report.

Prefer:

```bash
nxc smb 10.10.10.20 -u asif -p '<REDACTED>'
```


# Evidence Screenshot

A good screenshot should show:

```text
Tool

Target

Protocol

Account

Relevant result
```

Crop or redact unrelated sensitive information.


# Reporting Example - Excessive Administrative Access

## Observation

```text
The standard domain account CORP\asif successfully authenticated
to SRV01 over SMB. NetExec identified the account as having
administrative-level access on the server.
```

## Verification

```text
The access relationship was independently reviewed against the
account's group membership and the target's administrative
configuration.
```

## Impact

```text
If the account is compromised, the assigned administrative
privilege could provide an attacker with elevated control over
SRV01.
```

## Recommendation

```text
Review the administrative assignment and remove access that is
not required for the account's business function.
```


# Reporting Example - Writable Share

Avoid:

> The Public share is writable, therefore remote code execution is possible.

Prefer:

> The tested domain account has write access to the `Public` SMB share on `SRV01`. Review confirmed that the share is intended for collaborative file storage. No evidence was identified that files written to the share are automatically executed by a privileged process. The observation should therefore be evaluated primarily as an access-control and data-integrity issue rather than assumed to provide code execution.


# False Positives and Misinterpretation

## `[+]` Means Domain Admin

Incorrect.

It means authentication succeeded.


## `Pwn3d!` Means Domain Admin

Incorrect.

It indicates administrative-level access to the tested host/protocol context.

The account may only be a local administrator on one machine.


## Writable Share Means RCE

Incorrect.

A writable share only proves write access.

Execution requires additional conditions.


## SMB Signing Disabled Means Immediate Compromise

Incorrect.

It may satisfy one prerequisite for certain relay scenarios.

Other prerequisites must still exist.


## Open WinRM Means Remote Shell

Incorrect.

Authentication and authorisation must also succeed.


## LDAP Access Means Elevated Directory Rights

Incorrect.

Standard domain users commonly have substantial read access to directory information.


# Troubleshooting

# DNS Problems

Symptoms:

```text
Hostname cannot be resolved

Kerberos fails

LDAP behaves unexpectedly

Domain name incorrect
```

Check:

```bash
getent hosts dc01.corp.local
```

```bash
dig dc01.corp.local
```

```bash
cat /etc/resolv.conf
```


# Kerberos Clock Skew

Check:

```bash
date
```

Kerberos authentication can fail when the client and KDC clocks differ significantly.


# Wrong Domain

Symptoms may include:

```text
STATUS_LOGON_FAILURE

Unexpected local authentication

LDAP bind failure
```

Verify:

```text
Domain name

Username format

Target hostname

Domain controller
```


# SMB Works but LDAP Fails

Investigate:

```text
Are you targeting a domain controller?

Is LDAP reachable?

Are credentials supplied correctly?

Is the domain correct?

Does the environment require LDAP protections?

Is DNS correct?
```


# IP Works but Hostname Fails

Likely areas:

```text
DNS

/etc/hosts

Search domain

Resolver configuration
```

Kerberos especially benefits from correct hostname resolution.


# Hostname Works but IP Fails with Kerberos

This can be expected because Kerberos service identities are tied to SPNs and hostnames.

Use the correct DNS names when performing Kerberos-based testing.


# Old NetExec Command Fails

First:

```bash
nxc --version
```

Then:

```bash
nxc <protocol> --help
```

Do not assume old CrackMapExec syntax remains valid.


# NetExec vs CrackMapExec

NetExec evolved from the CrackMapExec ecosystem.

As a result, older resources may use:

```bash
crackmapexec
```

or:

```bash
cme
```

where modern workflows use:

```bash
nxc
```

Do not mechanically replace the executable name in old commands. Flags and functionality may also have changed.


# Common Status Codes

## `STATUS_LOGON_FAILURE`

Possible causes:

```text
Bad username

Bad password

Wrong domain

Authentication restriction
```


## `STATUS_ACCOUNT_LOCKED_OUT`

Meaning:

```text
Account is locked.
```

Action:

```text
Stop authentication attempts.
```


## `STATUS_ACCOUNT_DISABLED`

Meaning:

```text
Account is disabled.
```


## `STATUS_PASSWORD_EXPIRED`

Meaning:

```text
Password has expired.
```

Do not automatically attempt to change the password during an assessment.


## `STATUS_ACCESS_DENIED`

Authentication may have succeeded, but the requested operation is not permitted.

Separate:

```text
Authentication
```

from:

```text
Authorisation
```


# Authentication vs Authorisation

This distinction is central to NetExec.

```text
Authentication

"Who are you?"
       |
       v
Credential accepted


Authorisation

"What are you allowed to do?"
       |
       v
Shares / Admin / WinRM / SQL / etc.
```

A successful login does not imply permission to perform every operation.


# Operational Safety

Before running a NetExec command ask:

```text
How many targets?

How many accounts?

How many authentication attempts?

Does this query modify anything?

Could it trigger lockout?

Could it trigger EDR?

Could it create a service?

Could it access sensitive credentials?

Could it affect production?

Do I actually need this action?
```


# Rate and Scope Discipline

Prefer:

```text
One Account
    |
    v
One Target
    |
    v
One Protocol
    |
    v
Understand Result
    |
    v
Expand
```

rather than:

```text
Many Accounts
     x
Many Passwords
     x
Entire Network
```


# Detection Perspective

NetExec activity can generate telemetry across:

```text
Windows Security logs

Domain-controller authentication logs

SMB logs

PowerShell logs

WinRM logs

SQL logs

EDR

Network monitoring

SIEM
```


# Authentication Events

Useful Windows events may include:

| Event ID | General Meaning |
|---:|---|
| 4624 | Successful logon |
| 4625 | Failed logon |
| 4648 | Explicit credentials |
| 4672 | Special privileges |
| 4768 | Kerberos TGT request |
| 4769 | Kerberos service ticket |
| 4771 | Kerberos preauthentication failure |
| 4776 | NTLM credential validation |

Exact telemetry depends on:

```text
Protocol

Authentication method

Audit configuration

Target role

Collection configuration
```


# Purple Team Validation

NetExec can also be useful in controlled purple team exercises.

Example objective:

```text
Validate whether repeated SMB authentication attempts are visible
to the SOC.
```

Record:

```text
Source

Target

Account

Protocol

Timestamp

Number of attempts

Expected telemetry

Observed telemetry

Detection

SOC response
```


# Detection Questions

After a controlled NetExec test ask:

```text
Was authentication visible?

Was the source IP recorded?

Was the username recorded?

Was the target visible?

Was the authentication method visible?

Was administrative access visible?

Did an alert fire?

Could analysts reconstruct the activity?
```


# Retesting

If a privilege or access issue is remediated, repeat the same narrow validation.

Example:

```text
Before:

CORP\asif
   |
   v
SRV01
   |
   v
(Pwn3d!)


Remediation:

Unnecessary local administrator assignment removed.


Retest:

nxc smb 10.10.10.20 -u asif -p '<REDACTED>'


Expected:

Authentication may still succeed.

Administrative indicator should no longer be present.
```

This is stronger than merely checking that a configuration change was made.


# Practical Workflow - Domain Credentials

```text
                    DOMAIN CREDENTIALS
                           |
                           v
                      CONFIRM SCOPE
                           |
                           v
                      IDENTIFY DC
                           |
                           v
                       SMB BASIC
                           |
                           v
                 VALIDATE CREDENTIAL
                           |
                           v
                         LDAP
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
           USERS         GROUPS       COMPUTERS
             |             |             |
             +-------------+-------------+
                           |
                           v
                         SHARES
                           |
                           v
                       BLOODHOUND
                           |
                           v
                  PRIVILEGE RELATIONSHIPS
                           |
                           v
                  TARGETED HOST TESTING
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
            SMB          WINRM         MSSQL
             |             |             |
             +-------------+-------------+
                           |
                           v
                    INTERPRET ACCESS
                           |
                           v
                    MINIMAL VALIDATION
                           |
                           v
                        EVIDENCE
                           |
                           v
                         REPORT
```


# Practical Workflow - Host Assessment

```text
Host
 |
 v
nxc smb <target>
 |
 v
Identify:
 |
 +--> Hostname
 +--> Domain
 +--> OS
 +--> Signing
 +--> SMBv1
 |
 v
Credential Available?
 |
 +--> No -> Record information
 |
 +--> Yes
        |
        v
     Authenticate
        |
        +--> Failure -> Interpret error
        |
        +--> Success
               |
               +--> Shares
               |
               +--> Admin?
               |
               +--> Other authorised services
```


# Practical Workflow - Access Mapping

```text
                   AUTHORISED TARGET LIST
                           |
                           v
                    BASIC ENUMERATION
                           |
                           v
                     CREDENTIAL TEST
                           |
                           v
                   SUCCESSFUL TARGETS
                           |
             +-------------+-------------+
             |                           |
             v                           v
       USER-LEVEL ACCESS           ADMIN ACCESS
             |                           |
             v                           v
          SHARES                    WHY ADMIN?
             |                           |
             v                           v
       APPLICATION DATA          GROUP / POLICY
             |                           |
             +-------------+-------------+
                           |
                           v
                    BLOODHOUND CONTEXT
                           |
                           v
                       ATTACK PATH
```


# NetExec Assessment Checklist

## Preparation

- [ ] Scope confirmed
- [ ] Target list confirmed
- [ ] Accounts authorised for testing
- [ ] Lockout policy understood
- [ ] Tool version recorded
- [ ] Protocol help reviewed
- [ ] DNS configured
- [ ] Time synchronisation checked where Kerberos is used

## SMB

- [ ] Basic SMB information collected
- [ ] Hostname recorded
- [ ] Domain recorded
- [ ] OS information recorded
- [ ] SMB signing reviewed
- [ ] SMBv1 reviewed
- [ ] Authentication validated narrowly
- [ ] Shares enumerated where relevant
- [ ] Read/write permissions interpreted
- [ ] Administrative access distinguished from authentication

## LDAP

- [ ] Domain controller identified
- [ ] LDAP authentication validated
- [ ] Users reviewed
- [ ] Groups reviewed
- [ ] Computers reviewed
- [ ] SPNs considered
- [ ] Delegation considered
- [ ] BloodHound considered
- [ ] Results treated as relationships rather than automatic findings

## WinRM

- [ ] WinRM availability reviewed
- [ ] Authentication tested where relevant
- [ ] Remote-management privilege distinguished from port exposure
- [ ] Group-derived access understood

## MSSQL

- [ ] SQL service identified
- [ ] Authentication mode understood
- [ ] Account privilege reviewed
- [ ] SQL roles considered
- [ ] Linked servers considered where relevant
- [ ] OS privilege not assumed from database authentication

## Other Protocols

- [ ] SSH considered where applicable
- [ ] FTP considered where applicable
- [ ] RDP considered where applicable
- [ ] Installed NetExec protocol support confirmed

## Credentials

- [ ] Password testing kept narrow
- [ ] Hash testing kept narrow
- [ ] Kerberos context understood
- [ ] Password spraying separately authorised
- [ ] Lockout errors acted on immediately
- [ ] Sensitive credentials protected

## Privilege

- [ ] `[+]` interpreted as authentication only
- [ ] `(Pwn3d!)` interpreted in host context
- [ ] Administrative access independently understood
- [ ] Group/policy source investigated
- [ ] Attack-path relevance considered

## Shares

- [ ] Read access reviewed
- [ ] Write access reviewed
- [ ] Business purpose understood
- [ ] Sensitive content reviewed appropriately
- [ ] Writable share not automatically labelled RCE
- [ ] Privileged consumers considered

## Safety

- [ ] No unnecessary subnet-wide authentication
- [ ] No unnecessary remote execution
- [ ] No unnecessary credential extraction
- [ ] No unnecessary file modification
- [ ] Domain-controller actions treated carefully
- [ ] Stop conditions understood

## Evidence

- [ ] Timestamp recorded
- [ ] Source recorded
- [ ] Target recorded
- [ ] Protocol recorded
- [ ] Account recorded
- [ ] NetExec version recorded
- [ ] Command recorded
- [ ] Passwords redacted
- [ ] Relevant output captured
- [ ] Interpretation documented

## Reporting

- [ ] Authentication separated from authorisation
- [ ] Candidate separated from confirmed finding
- [ ] Root cause identified
- [ ] Business/security impact established
- [ ] Attack-path context included where relevant
- [ ] Remediation addresses privilege/access source
- [ ] Retest procedure documented


# Quick Command Reference

## Version

```bash
nxc --version
```

## General Help

```bash
nxc --help
```

## SMB Help

```bash
nxc smb --help
```

## LDAP Help

```bash
nxc ldap --help
```

## WinRM Help

```bash
nxc winrm --help
```

## MSSQL Help

```bash
nxc mssql --help
```

## Basic SMB

```bash
nxc smb 10.10.10.20
```

## SMB Against a Target File

```bash
nxc smb targets.txt
```

## Password Authentication

```bash
nxc smb 10.10.10.20 -d corp.local -u 'asif' -p 'Password123!'
```

## NTLM Hash Authentication

```bash
nxc smb 10.10.10.20 -d corp.local -u 'asif' -H '0123456789abcdef0123456789abcdef'
```

## Shares

```bash
nxc smb 10.10.10.20 -d corp.local -u 'asif' -p 'Password123!' --shares
```

## LDAP Authentication

```bash
nxc ldap 10.10.10.10 -d corp.local -u 'asif' -p 'Password123!'
```

## WinRM Authentication

```bash
nxc winrm 10.10.10.20 -d corp.local -u 'asif' -p 'Password123!'
```

## MSSQL Authentication

```bash
nxc mssql 10.10.10.30 -d corp.local -u 'asif' -p 'Password123!'
```

## SSH Authentication

```bash
nxc ssh 10.10.10.40 -u 'asif' -p 'Password123!'
```

## Save Output

```bash
nxc smb targets.txt -u 'asif' -p 'Password123!' | tee netexec-results.txt
```


# Quick Interpretation Reference

| Result | Interpretation | Next Question |
|---|---|---|
| SMB host information | Service/platform information | Is configuration security relevant? |
| `[+]` | Authentication succeeded | What is the account authorised to do? |
| `(Pwn3d!)` | Administrative-level access identified | Why does the account have admin rights? |
| `READ` | Share can be read | Is exposed data sensitive? |
| `WRITE` | Share can be modified | What consumes the files? |
| `STATUS_LOGON_FAILURE` | Authentication failed | Credential, domain or policy issue? |
| `STATUS_ACCOUNT_LOCKED_OUT` | Account locked | Stop testing and follow escalation process |
| WinRM success | Remote-management authentication/access | Which right grants it? |
| LDAP success | Directory authentication works | What relationships can be enumerated? |
| MSSQL success | Database authentication works | Which database/server roles exist? |


# Command-to-Conclusion Model

Do not use NetExec like this:

```text
Command
   |
   v
Interesting Colour
   |
   v
Screenshot
   |
   v
Finding
```

Use:

```text
Command
   |
   v
Result
   |
   v
What Does It Prove?
   |
   v
What Does It NOT Prove?
   |
   v
Additional Preconditions
   |
   v
Minimal Validation
   |
   v
Security Consequence
   |
   v
Evidence
   |
   v
Finding
```


# Final NetExec Workflow

```text
                         TARGET
                           |
                           v
                    SELECT PROTOCOL
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
         SMB              LDAP            WINRM
          |                |                |
          +----------------+----------------+
                           |
                           v
                   BASIC ENUMERATION
                           |
                           v
                    HAVE CREDENTIAL?
                      /          \
                    No            Yes
                    |              |
                    v              v
                 Record        VALIDATE
                                  |
                                  v
                           AUTHENTICATED?
                             /        \
                           No          Yes
                           |            |
                           v            v
                     Interpret Error  ENUMERATE
                                        |
                                        v
                                  WHAT ACCESS?
                                        |
                         +--------------+--------------+
                         |              |              |
                         v              v              v
                       Shares        Directory       Admin
                         |              |              |
                         +--------------+--------------+
                                        |
                                        v
                               SECURITY RELEVANT?
                                  /           \
                                No             Yes
                                |               |
                                v               v
                             Record       VERIFY CONTEXT
                                                |
                                                v
                                       MINIMAL VALIDATION
                                                |
                                                v
                                             EVIDENCE
                                                |
                                                v
                                             REPORT
                                                |
                                                v
                                             RETEST
```


# Related Cheatsheets

- [Active Directory Cheatsheet](active-directory.md)
- [Impacket Cheatsheet](impacket.md)
- [BloodHound Cheatsheet](bloodhound.md)
- [Windows Cheatsheet](windows.md)
- [PowerShell Cheatsheet](powershell.md)
- [Networking Cheatsheet](networking.md)


# Detailed Notes

- [Active Directory](../active-directory/index.md)
- [Active Directory Methodology](../active-directory/methodology.md)
- [Active Directory Enumeration](../active-directory/enumeration.md)
- [NetExec](../active-directory/netexec.md)
- [Impacket](../active-directory/impacket.md)
- [BloodHound](../active-directory/bloodhound.md)
- [SMB](../active-directory/smb.md)
- [NTLM](../active-directory/ntlm.md)
- [Kerberos](../active-directory/kerberos.md)
- [NTLM Relay](../active-directory/ntlm-relay.md)
- [Authentication Coercion](../active-directory/authentication-coercion.md)
- [Lateral Movement](../active-directory/lateral-movement.md)
- [WinRM](../active-directory/winrm.md)
- [WMI](../active-directory/wmi.md)
- [DCOM](../active-directory/dcom.md)
- [Pivoting](../active-directory/pivoting.md)


# References

- [NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }
- [NetExec GitHub](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - SMB Overview](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Windows Remote Management](https://learn.microsoft.com/en-us/windows/win32/winrm/portal){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Kerberos Authentication](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - NTLM Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Use NetExec to answer a question"
    Start with a specific objective such as "Does this credential authenticate to SRV01?", "Which shares can this account access?" or "Does this user have administrative access?". This produces cleaner evidence than running every available option against every target.


!!! tip "Authentication is not authorisation"
    `[+]` proves that authentication succeeded for the tested protocol. It does not by itself demonstrate administrative privilege. Interpret the access available after authentication before drawing a security conclusion.


!!! warning "Do not let automation replace analysis"
    NetExec can query many systems quickly, but the important part of an assessment is understanding why access exists, whether it is expected, what security boundary it crosses and what the evidence actually proves.
