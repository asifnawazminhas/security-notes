---
title: Impacket Cheatsheet
description: Detailed practical Impacket reference for authorised Active Directory and Windows security assessments covering SMB, LDAP, Kerberos, SPNs, authentication, NTLM hashes, tickets, MSSQL, remote administration, secrets, result interpretation, troubleshooting, evidence and retesting.
---

# Impacket Cheatsheet

Impacket is a collection of Python classes and command-line tools for working with network protocols commonly encountered in Windows and Active Directory environments.

It includes specialised utilities for:

```text
SMB

MSRPC

Kerberos

NTLM

LDAP-related workflows

MSSQL

WMI

Windows services

Remote administration

Credential and ticket analysis
```

This cheatsheet focuses on using Impacket as a **focused protocol toolkit** during authorised penetration tests, red team exercises and security labs.

The objective is not simply:

```text
Find Impacket command
        |
        v
Run command
```

Instead:

```text
Identify Objective
        |
        v
Choose Protocol
        |
        v
Choose Impacket Tool
        |
        v
Check Prerequisites
        |
        v
Run Focused Test
        |
        v
Interpret Result
        |
        v
Determine What It Proves
        |
        v
Validate Further If Required
        |
        v
Collect Evidence
```

For the broader workflow, see:

- [Active Directory Cheatsheet](active-directory.md)
- [NetExec Cheatsheet](netexec.md)

!!! warning "Authorised Security Testing"
    Only use these techniques against systems, accounts and environments you are explicitly authorised to test. Some Impacket utilities can perform remote administration, request authentication material, access sensitive credential stores or make changes to systems. Use the least intrusive method necessary to prove the assessment objective.


# Quick Start

A useful way to think about Impacket is:

```text
What do I have?
      |
      +--> Password
      |
      +--> NTLM Hash
      |
      +--> Kerberos Ticket
      |
      +--> Kerberos Key
      |
      +--> Administrative Access
      |
      +--> SQL Credentials
      |
      v
What am I trying to learn?
      |
      +--> Enumerate SPNs
      |
      +--> Check Preauthentication
      |
      +--> Access SMB
      |
      +--> Query MSSQL
      |
      +--> Validate Remote Administration
      |
      +--> Inspect Credential Stores
      |
      +--> Work with Kerberos Tickets
      |
      v
Select the smallest appropriate Impacket utility
```


# Common Impacket Tools

| Tool | Primary Purpose |
|---|---|
| `GetUserSPNs.py` | Enumerate accounts with SPNs and Kerberos service-ticket candidates |
| `GetNPUsers.py` | Identify/test accounts without Kerberos preauthentication |
| `getTGT.py` | Request a Kerberos Ticket Granting Ticket |
| `getST.py` | Request Kerberos service tickets in supported scenarios |
| `ticketConverter.py` | Convert between Kerberos ticket-cache formats |
| `secretsdump.py` | Access credential material where sufficient privilege exists |
| `smbclient.py` | SMB share interaction |
| `lookupsid.py` | SID/RPC-based domain enumeration |
| `rpcdump.py` | Enumerate RPC endpoints |
| `samrdump.py` | Query SAMR information |
| `mssqlclient.py` | Microsoft SQL Server client |
| `wmiexec.py` | WMI-based remote administration |
| `psexec.py` | Service-based remote administration |
| `smbexec.py` | SMB/service-based remote administration |
| `atexec.py` | Scheduled-task-based remote administration |
| `dcomexec.py` | DCOM-based remote administration |

Depending on the installation, command names may be prefixed with:

```text
impacket-
```

For example:

```bash
impacket-GetUserSPNs
```

instead of:

```bash
GetUserSPNs.py
```


# Installation

On Kali Linux, Impacket may already be installed.

Check:

```bash
python3 -m pip show impacket
```

Check installed command wrappers:

```bash
compgen -c | grep '^impacket-' | sort -u
```

Package version:

```bash
python3 -m pip show impacket | grep -E '^(Name|Version):'
```

Example:

```text
Name: impacket
Version: <installed-version>
```


# Help Before Execution

For any utility:

```bash
impacket-GetUserSPNs -h
```

```bash
impacket-GetNPUsers -h
```

```bash
impacket-secretsdump -h
```

```bash
impacket-wmiexec -h
```

```bash
impacket-mssqlclient -h
```

This matters because syntax and supported authentication options can change between releases.


# Example Environment

Examples throughout this cheatsheet use:

```text
Domain:     corp.local
DC:         dc01.corp.local
DC IP:      10.10.10.10

Server:     srv01.corp.local
Server IP:  10.10.10.20

SQL Server: sql01.corp.local
SQL IP:     10.10.10.30

Username:   asif
Password:   Password123!
```

Example NTLM hash:

```text
0123456789abcdef0123456789abcdef
```

These are placeholders only.


# Impacket Target Syntax

Many Impacket utilities use a target string resembling:

```text
domain/username:password@target
```

Example:

```text
corp.local/asif:Password123!@10.10.10.20
```

Some tools instead take:

```text
domain/username:password
```

and a separate:

```text
-dc-ip
```

option.

Always check:

```bash
impacket-<tool> -h
```

before assuming the target format.


# Passwords with Special Characters

Shell metacharacters can alter a command.

Prefer single quotes around target strings where possible:

```bash
impacket-smbclient 'corp.local/asif:Password123!@10.10.10.20'
```

For complex credentials, interactive prompting or other supported authentication options may be safer than placing the password directly on the command line.


# Command-Line Credential Exposure

Be aware that passwords supplied directly as command arguments may be exposed through:

```text
Shell history

Process listings

Terminal recordings

Screenshots

Assessment logs
```

Where supported, prefer prompting for the password.

In reports, always redact real credentials.


# Domain Controller Discovery

Before Kerberos-focused testing, identify the domain controller.

From Linux:

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```

or:

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.corp.local
```

Example:

```text
_ldap._tcp.dc._msdcs.corp.local. 600 IN SRV 0 100 389 dc01.corp.local.
```


# DNS Check

```bash
dig dc01.corp.local
```

```bash
getent hosts dc01.corp.local
```

Kerberos problems are frequently caused by DNS rather than by Impacket itself.


# Time Check

Kerberos depends on reasonably synchronised clocks.

Check:

```bash
date
```

If Kerberos errors indicate clock skew, compare the assessment host's time with the domain environment before changing authentication options.


# SMBClient

Impacket provides an SMB client for interacting with SMB shares.

Check:

```bash
impacket-smbclient -h
```

Connect:

```bash
impacket-smbclient 'corp.local/asif:Password123!@10.10.10.20'
```

## Representative Session

```text
Impacket v...

Type help for list of commands
# shares
ADMIN$
C$
IPC$
Public
Software
```

Useful interactive commands may include:

```text
help

shares

use

ls

cd

pwd

get

put

mkdir

exit
```

Check `help` inside the client for the installed version.


# SMBClient Workflow

```text
Credential
    |
    v
SMB Authentication
    |
    v
List Shares
    |
    v
Select Relevant Share
    |
    v
List Files
    |
    v
Review Business Purpose
    |
    v
Retrieve Only Relevant Evidence
```


# Interpreting Share Access

If you can list a share:

```text
Authentication
      |
      v
Share Access
```

has been demonstrated.

This does not automatically prove:

```text
Administrative access

Sensitive-data exposure

Remote code execution

Privilege escalation
```

The contents and intended permissions determine the security significance.


# Writable Share

A writable share should trigger questions such as:

```text
Who is expected to write?

Which systems consume files?

Are files executed?

Are configuration files loaded?

Does a privileged service read the directory?

Can application behaviour be changed?
```

Do not automatically conclude:

```text
WRITE = RCE
```


# LookUpSID

`lookupsid` uses Windows RPC mechanisms to enumerate SID information.

Help:

```bash
impacket-lookupsid -h
```

Authenticated example:

```bash
impacket-lookupsid 'corp.local/asif:Password123!@10.10.10.10'
```

## Representative Output

```text
[*] Brute forcing SIDs at 10.10.10.10
[*] StringBinding ncacn_np:10.10.10.10[\pipe\lsarpc]
[*] Domain SID is: S-1-5-21-...
...
500: CORP\Administrator
501: CORP\Guest
1104: CORP\asif
```

### Interpretation

Useful information may include:

```text
Domain SID

Usernames

Group names

Relative identifiers
```

The existence of a user or group is inventory information, not a vulnerability.


# RPCDump

Enumerate RPC endpoints:

```bash
impacket-rpcdump 10.10.10.20
```

or use the authentication syntax supported by the installed version.

RPC endpoints can reveal:

```text
Available RPC interfaces

Named pipes

Protocol sequences

Service exposure
```


# RPCDump Interpretation

RPC endpoint enumeration is mainly reconnaissance.

Do not report:

```text
RPC endpoint exists
```

as a vulnerability without identifying an actual insecure configuration or exploitable security consequence.


# SAMRDump

Check:

```bash
impacket-samrdump -h
```

Against an authorised target:

```bash
impacket-samrdump 'corp.local/asif:Password123!@10.10.10.20'
```

Depending on permissions and target configuration, SAMR information may include account-related information.

Interpret returned data according to the account's expected directory visibility and the environment's security model.


# Kerberos Overview

A simplified Kerberos workflow is:

```text
User
 |
 v
AS-REQ
 |
 v
KDC
 |
 v
TGT
 |
 v
TGS-REQ
 |
 v
Service Ticket
 |
 v
Service
```

Important concepts:

```text
KDC

TGT

TGS

SPN

Realm

Service Ticket

Ticket Cache
```


# GetUserSPNs

`GetUserSPNs` is commonly used to enumerate accounts associated with Service Principal Names.

Help:

```bash
impacket-GetUserSPNs -h
```

Authenticated enumeration:

```bash
impacket-GetUserSPNs 'corp.local/asif:Password123!' -dc-ip 10.10.10.10
```

## Representative Output

```text
ServicePrincipalName             Name       MemberOf
-------------------------------  ---------  ------------------------
MSSQLSvc/sql01.corp.local:1433   svc_sql
HTTP/web01.corp.local            svc_web
```

### What This Proves

It identifies directory accounts associated with SPNs visible to the current principal.

It does **not** prove:

```text
The account password is weak

The account is compromised

The account is privileged

Kerberoasting will recover a password
```


# Interpreting SPNs

Example:

```text
MSSQLSvc/sql01.corp.local:1433
```

This indicates a service principal associated with Microsoft SQL Server.

Investigate:

```text
Which account owns the SPN?

What service uses it?

Is the identity a managed service account?

What privileges does it hold?

Is the service still active?

Where can the account log on?
```


# Kerberoasting Assessment Model

```text
Domain Credential
      |
      v
Enumerate SPNs
      |
      v
Service Account Found
      |
      v
Determine Privilege
      |
      v
Determine Credential Management
      |
      v
Requesting Ticket Necessary?
      |
      v
Authorised Controlled Validation
      |
      v
Assess Password Resilience Offline
      |
      v
Document Impact
```

The most important security question is not simply whether a service ticket can be requested.

Service-ticket issuance is normal Kerberos behaviour.

The risk arises when a service account uses crackable credential material and that account provides meaningful access.


# Requesting Service Tickets

Where explicitly authorised, `GetUserSPNs` supports requesting service tickets.

Review the installed options:

```bash
impacket-GetUserSPNs -h
```

Use only the minimum number of accounts required for the assessment objective.

Avoid requesting tickets for every SPN merely because the tool supports it.


# Kerberoasting Evidence

Useful evidence includes:

```text
Service account

SPN

Associated service

Account privilege

Password-management model

Whether an authorised ticket request was performed

Whether offline password testing was in scope

Result of controlled validation
```

Avoid including reusable credential material in the final report.


# GetNPUsers

`GetNPUsers` is used when assessing Kerberos accounts configured without preauthentication.

Help:

```bash
impacket-GetNPUsers -h
```

Authenticated directory assessment example:

```bash
impacket-GetNPUsers 'corp.local/asif:Password123!' -dc-ip 10.10.10.10
```

Exact options for user lists and ticket requests should be confirmed with:

```bash
impacket-GetNPUsers -h
```


# AS-REP Roasting Prerequisite

The relevant account configuration is:

```text
Do not require Kerberos preauthentication
```

Conceptually:

```text
User
 |
 v
Preauthentication Required?
   |
 +---+---+
 |       |
Yes      No
 |       |
 v       v
Normal   AS-REP Assessment Candidate
```


# What an AS-REP Candidate Means

It does not automatically mean:

```text
Password recovered

Account compromised

Privilege escalation
```

It means the account has a security-relevant Kerberos configuration that may expose password-derived material to offline analysis.


# AS-REP Follow-Up

Determine:

```text
Why is preauthentication disabled?

Is the account enabled?

What privilege does it have?

Is it a service account?

Is the password strong?

Is the configuration still required?
```


# GetTGT

`getTGT` can request a Kerberos Ticket Granting Ticket when appropriate credential material is available.

Help:

```bash
impacket-getTGT -h
```

A password-based example in a controlled environment may resemble:

```bash
impacket-getTGT 'corp.local/asif:Password123!' -dc-ip 10.10.10.10
```

Successful execution typically creates a Kerberos credential cache file.


# Inspect the Ticket Cache

Set the cache:

```bash
export KRB5CCNAME=/path/to/asif.ccache
```

Inspect:

```bash
klist
```

Representative output:

```text
Ticket cache: FILE:/path/to/asif.ccache
Default principal: asif@CORP.LOCAL

Valid starting       Expires              Service principal
...
krbtgt/CORP.LOCAL@CORP.LOCAL
```


# What a TGT Proves

A valid TGT demonstrates that the represented principal has an authenticated Kerberos context.

It does not mean:

```text
Administrator

Domain Admin

Access to every service
```

Authorisation still depends on the target service and the principal's permissions.


# Ticket Cache Environment Variable

Check:

```bash
echo "$KRB5CCNAME"
```

Set:

```bash
export KRB5CCNAME=/tmp/asif.ccache
```

Then:

```bash
klist
```


# Kerberos Authentication with Impacket

Many Impacket utilities support Kerberos options such as:

```text
-k
```

and:

```text
-no-pass
```

depending on the utility.

Always check the relevant help output.

Example pattern:

```bash
impacket-<tool> -k -no-pass <target>
```

The exact target syntax depends on the utility.


# Kerberos Name Resolution

Kerberos usually works best when:

```text
DNS is correct

Hostnames match SPNs

Realm is correct

Clock is synchronised
```

If an IP-based command fails but a hostname-based command works, the difference may be Kerberos/SPN related rather than a network problem.


# GetST

`getST` handles Kerberos service-ticket operations used in several legitimate administration and delegation-related testing scenarios.

Help:

```bash
impacket-getST -h
```

Before using it, understand:

```text
Which principal you control

Which service is involved

Which delegation configuration exists

Which SPN is required

What the resulting ticket represents
```

For delegation concepts see:

- [Constrained Delegation](../active-directory/constrained-delegation.md)
- [RBCD](../active-directory/rbcd.md)
- [S4U](../active-directory/s4u.md)


# Do Not Treat getST as a Generic Command

The correct model is:

```text
Directory Relationship
        |
        v
Delegation Configuration
        |
        v
Controlled Principal
        |
        v
Target Service
        |
        v
Required Ticket
        |
        v
getST
```

not:

```text
Run getST
    |
    v
See What Happens
```


# TicketConverter

Impacket can convert between Kerberos ticket formats.

Help:

```bash
impacket-ticketConverter -h
```

Conceptually:

```text
Kirbi
  |
  v
ticketConverter
  |
  v
CCache
```

or the reverse where supported.


# Why Ticket Conversion Matters

Different tooling ecosystems may use different ticket formats.

For example:

```text
Windows-oriented tooling

Linux Kerberos tooling
```

may expect different representations.

Conversion changes the file format. It does not grant additional privilege.


# Kerberos Ticket Workflow

```text
Credential / Existing Ticket
          |
          v
Identify Principal
          |
          v
Identify Realm
          |
          v
Identify Ticket Type
          |
          v
Check Validity
          |
          v
Set KRB5CCNAME If Needed
          |
          v
klist
          |
          v
Use Against Authorised Service
          |
          v
Interpret Authorisation
```


# NTLM Hash Authentication

Several Impacket utilities support NTLM hash authentication.

Check the specific utility:

```bash
impacket-wmiexec -h
```

Common options may include:

```text
-hashes
```

A typical hash pair format is:

```text
LMHASH:NTHASH
```

When the LM hash is unavailable, tools commonly accept an empty LM component:

```text
:NTHASH
```

Example placeholder:

```text
:0123456789abcdef0123456789abcdef
```


# What Hash Authentication Proves

If the target accepts the NTLM credential material:

```text
Credential Material
        |
        v
Authentication
```

has been demonstrated.

It does not prove:

```text
Plaintext password known

Domain Admin

Credential works everywhere
```


# Pass-the-Hash Assessment Model

```text
NTLM Hash
    |
    v
Identify Account
    |
    v
Determine Expected Scope
    |
    v
Choose One Authorised Target
    |
    v
Validate Authentication
    |
    v
Determine Privilege
    |
    v
Expand Only If Required
```


# Remote Administration Tools

Impacket includes several utilities capable of remote administration when sufficient permissions exist.

Important examples:

```text
wmiexec

psexec

smbexec

atexec

dcomexec
```

These tools use different Windows mechanisms.

Do not treat them as interchangeable.


# Remote Administration Comparison

| Tool | General Mechanism | Important Consideration |
|---|---|---|
| `wmiexec` | WMI | Requires appropriate WMI/DCOM permissions |
| `psexec` | SMB + service creation | Creates/uses a service mechanism |
| `smbexec` | SMB/service-based execution | Service-related artefacts may be created |
| `atexec` | Task Scheduler | Scheduled-task artefacts and logs |
| `dcomexec` | DCOM | DCOM/RPC connectivity and permissions |

Operational footprint differs significantly between methods.


# Before Remote Execution

Confirm:

```text
Is remote execution explicitly authorised?

Do I already have enough evidence?

Is the target production-critical?

What artefacts will be created?

What logs will be generated?

Will a service be created?

Will a scheduled task be created?

Is cleanup required?

Can the same conclusion be proven more safely?
```


# WMIExec

Help:

```bash
impacket-wmiexec -h
```

Password-based authorised example:

```bash
impacket-wmiexec 'corp.local/asif:Password123!@10.10.10.20'
```

## What Success Proves

A successful remote administrative session demonstrates that:

```text
The supplied credential authenticates
+
The account has sufficient permissions for the WMI-based path
```

This is stronger evidence than simple SMB authentication.


# WMIExec with Hash Authentication

Where explicitly authorised, inspect:

```bash
impacket-wmiexec -h
```

for the current `-hashes` syntax.

Use a single authorised target first.


# WMIExec Interpretation

If WMI-based administration succeeds, investigate:

```text
Why does the account have remote WMI rights?

Is it local administrator?

Is access inherited from a domain group?

Is the access expected?

Which other systems share the same administrative model?
```


# PSExec

Help:

```bash
impacket-psexec -h
```

`psexec` uses a service-based remote administration mechanism.

Because this can create service-related artefacts, it generally has a different operational footprint from WMI-based approaches.


# PSExec Safety

Before using it, understand:

```text
Service creation

File/service artefacts

Windows event logging

EDR visibility

Cleanup requirements
```

Do not use it merely to prove credentials are valid.


# SMBExec

Help:

```bash
impacket-smbexec -h
```

This also uses SMB/service-related mechanisms.

The exact artefacts and behaviour should be understood before production use.


# ATExec

Help:

```bash
impacket-atexec -h
```

This uses Task Scheduler-related functionality.

Potential telemetry includes:

```text
Task creation

Task execution

Process creation

Authentication events
```

Use only where the engagement objective requires remote execution.


# DCOMExec

Help:

```bash
impacket-dcomexec -h
```

DCOM-based remote administration depends on:

```text
RPC connectivity

DCOM availability

Authentication

Relevant permissions
```

For deeper context see [DCOM](../active-directory/dcom.md).


# Choosing a Remote Administration Method

Do not choose based on:

```text
Which command is shortest?
```

Choose based on:

```text
Assessment objective

Permissions

Protocol availability

Operational impact

Telemetry

Cleanup

Rules of engagement
```


# Remote Administration Decision Tree

```text
Administrative Credential
         |
         v
Do I Need Remote Execution?
      /       \
    No         Yes
    |           |
    v           v
 Stop       What Protocols
            Are Available?
                 |
       +---------+---------+
       |         |         |
       v         v         v
      WMI       SMB       DCOM
       |         |         |
       v         v         v
   wmiexec   psexec/    dcomexec
             smbexec
                 |
                 v
          Minimal Validation
                 |
                 v
              Cleanup
```


# MSSQLClient

Impacket includes a Microsoft SQL Server client.

Help:

```bash
impacket-mssqlclient -h
```

A controlled Windows-authentication example may resemble:

```bash
impacket-mssqlclient 'corp.local/asif:Password123!@10.10.10.30' -windows-auth
```

Exact authentication options should be confirmed with:

```bash
impacket-mssqlclient -h
```


# Representative MSSQL Session

```text
[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
SQL>
```


# Initial SQL Questions

After authentication, determine:

```text
Who am I?

Which database am I using?

Which roles do I have?

Which databases are accessible?

Is the account sysadmin?

Are linked servers configured?
```


# Safe SQL Context Queries

Current login:

```sql
SELECT SYSTEM_USER;
```

Current database:

```sql
SELECT DB_NAME();
```

Server name:

```sql
SELECT @@SERVERNAME;
```

Version:

```sql
SELECT @@VERSION;
```

Check sysadmin membership:

```sql
SELECT IS_SRVROLEMEMBER('sysadmin');
```


# Interpret `IS_SRVROLEMEMBER`

Example:

```text
1
```

generally indicates membership in the requested server role.

Example:

```text
0
```

indicates the current login is not a member.

This provides much stronger evidence than simply assuming that successful SQL authentication means administrative database access.


# SQL Linked Servers

Linked servers can create trust relationships between SQL systems.

List them using an appropriate SQL query or client functionality supported in the environment.

Then determine:

```text
Which server is linked?

Which authentication context is used?

What permissions exist remotely?

Is the link bidirectional?

Does it cross a security boundary?
```


# MSSQL Attack-Path Thinking

```text
Domain User
    |
    v
SQL Login
    |
    v
Database Role
    |
    v
Linked Server
    |
    v
Different Security Context
    |
    v
Sensitive Database / Server
```

Do not assume the path exists until each relationship is validated.


# SecretsDump

`secretsdump` is one of the most sensitive Impacket utilities.

It can access credential material from Windows systems and Active Directory where sufficient privileges and conditions exist.

Help:

```bash
impacket-secretsdump -h
```

Potential data can include:

```text
Local SAM hashes

LSA secrets

Cached domain logons

Service-account secrets

Domain credential material
```

!!! danger "Sensitive Operation"
    Credential extraction should only be performed when it is explicitly authorised and necessary to meet the assessment objective. Domain-controller credential extraction can expose highly sensitive domain-wide authentication material.


# Before Using SecretsDump

Ask:

```text
Do I need credential material to prove the finding?

Is credential extraction explicitly in scope?

Can I demonstrate the privilege without collecting secrets?

Is the target a domain controller?

How will evidence be protected?

What data-retention requirements apply?

Will the command create temporary artefacts?
```


# Local Administrative Context

Against a specifically authorised test host where administrative access is already established, `secretsdump` can be used to validate whether that level of access exposes local credential stores.

Do not run it simply because an account receives `(Pwn3d!)` in NetExec.


# SecretsDump Result Interpretation

If credential material is retrieved:

```text
Administrative Access
        |
        v
Sensitive Credential Store Accessible
        |
        v
Credential Material Retrieved
```

has been demonstrated.

Next determine:

```text
Which accounts are represented?

Are they local or domain accounts?

Are any credentials reusable?

What privilege do they provide?

Is further validation necessary?
```


# Do Not Over-Collect

If the objective is:

> Determine whether local administrative compromise exposes reusable credentials.

you may only need enough evidence to demonstrate that sensitive credential material is accessible.

You do not necessarily need to validate every recovered credential against every system.


# Domain Controller Considerations

A domain controller represents a significantly different risk level.

Potential credential data may affect:

```text
Entire domain

Privileged users

Service accounts

Machine accounts

Trust relationships

Kerberos infrastructure
```

Treat any DC credential-access activity as a high-impact assessment step requiring explicit authorisation.


# Credential Handling

Never place real credential material in public notes or final reports.

Prefer:

```text
Administrator:500:<REDACTED>
```

instead of preserving a reusable hash.


# Credential Validation Workflow

```text
Credential Material
       |
       v
Identify Principal
       |
       v
Determine Type
       |
       +--> Password
       +--> NTLM
       +--> Kerberos
       |
       v
Determine Expected Scope
       |
       v
Select One Relevant Target
       |
       v
Minimal Validation
       |
       v
Determine Privilege
       |
       v
Stop When Proven
```


# Impacket and NetExec

These tools complement each other.

A practical workflow is:

```text
NetExec
   |
   v
Broad Access Mapping
   |
   v
Interesting Target
   |
   v
Impacket
   |
   v
Focused Protocol Validation
```


# Example

NetExec:

```bash
nxc smb 10.10.10.20 -d corp.local -u 'asif' -p 'Password123!'
```

Suppose the result shows administrative access.

Rather than running every Impacket remote-administration tool, determine what you need to prove.

If WMI access is specifically relevant, a focused WMI validation may be appropriate.

If SMB share access is the objective, use an SMB client instead.

Choose the tool according to the question.


# Impacket and BloodHound

BloodHound identifies relationships.

Impacket can help validate selected protocol-level paths.

```text
BloodHound
    |
    v
Interesting Relationship
    |
    v
Understand Preconditions
    |
    v
Choose Appropriate Impacket Tool
    |
    v
Minimal Validation
    |
    v
Evidence
```


# Impacket and Kerberos

Impacket's Kerberos utilities are particularly useful for:

```text
SPN enumeration

Preauthentication assessment

TGT handling

Service tickets

Delegation validation

Kerberos authentication
```

Use them after understanding the underlying Kerberos relationship.


# Impacket and AD CS

Impacket is not the primary toolkit for all AD CS assessment workflows.

For AD CS-specific enumeration and certificate analysis, specialised tools such as Certipy are often more appropriate.

See:

[Active Directory Certificate Services](../active-directory/ad-cs/index.md)


# "I Have a Domain Password - What Next?"

```text
Domain Password
      |
      v
Confirm Domain
      |
      v
Confirm DC
      |
      v
Validate Authentication
      |
      +--> SMB
      |
      +--> LDAP / Directory Context
      |
      v
Enumerate SPNs
      |
      v
Review Preauthentication
      |
      v
Review Shares
      |
      v
BloodHound
      |
      v
Select Specific Privilege Path
      |
      v
Focused Impacket Validation
```


# "I Have an NTLM Hash - What Next?"

```text
NTLM Hash
   |
   v
Identify Account
   |
   v
Determine Domain or Local Context
   |
   v
Identify One Relevant Target
   |
   v
Choose Protocol
   |
   v
Validate Authentication
   |
   v
Determine Privilege
   |
   v
Stop or Expand Based on Objective
```


# "I Have a Kerberos Ticket - What Next?"

First:

```bash
klist
```

Then determine:

```text
Who is the client?

What realm?

TGT or service ticket?

Which service?

When does it expire?

What target is relevant?
```

If required:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
```

Then use a compatible Impacket utility with the appropriate Kerberos options.


# "I Found an SPN - What Next?"

```text
SPN
 |
 v
Identify Account
 |
 v
Identify Service
 |
 v
Check Account Privilege
 |
 v
Check Credential Management
 |
 v
Is Ticket Request Required?
 |
 v
Controlled Validation
 |
 v
Assess Password Resilience If Authorised
```


# "I Found an Account Without Preauthentication"

```text
Account
   |
   v
Confirm Configuration
   |
   v
Determine Account Status
   |
   v
Determine Privilege
   |
   v
Understand Business Reason
   |
   v
Controlled AS-REP Assessment
   |
   v
Remediation
```


# "I Have Local Admin"

Do not automatically run:

```text
secretsdump

psexec

smbexec

wmiexec

atexec
```

Instead:

```text
Local Admin
    |
    v
What Is the Objective?
    |
    +--> Prove Admin Access?
    |       |
    |       v
    |    Already Proven
    |
    +--> Review Credential Exposure?
    |       |
    |       v
    |    Controlled Credential Assessment
    |
    +--> Validate Remote Management?
    |       |
    |       v
    |    Select One Method
    |
    +--> Collect Host Evidence?
            |
            v
         Minimal Queries
```


# "I Have SQL Credentials"

```text
SQL Credential
     |
     v
Authenticate
     |
     v
SYSTEM_USER
     |
     v
Server Role
     |
     v
Accessible Databases
     |
     v
Linked Servers
     |
     v
Determine Actual Privilege
```


# Candidate vs Confirmed

Impacket output should be interpreted in stages.

## Candidate

Examples:

```text
SPN identified

Account without preauthentication identified

RPC endpoint exposed

SQL server reachable

Administrative credential available
```

These indicate something worth investigating.


## Likely

Examples:

```text
Account has SPN and weak credential policy

Administrative credential authenticates to target

SQL login has elevated server role

Sensitive credential store is accessible
```


## Confirmed

A controlled test demonstrates the actual security consequence.

Examples:

```text
Authorised account successfully performs the relevant
administrative action.

Controlled credential analysis demonstrates that a service
account uses weak password-derived material.

SQL role query confirms sysadmin membership.
```


# Common Errors

# `KRB_AP_ERR_SKEW`

Meaning:

```text
Clock difference between client and Kerberos infrastructure
is too large.
```

Check:

```bash
date
```

Then compare against the domain environment.


# `KDC_ERR_PREAUTH_FAILED`

Possible causes:

```text
Incorrect password

Incorrect key

Wrong principal

Wrong realm

Authentication mismatch
```


# `KDC_ERR_C_PRINCIPAL_UNKNOWN`

Possible causes:

```text
Incorrect username

Incorrect realm

Principal does not exist

Naming issue
```


# `KDC_ERR_S_PRINCIPAL_UNKNOWN`

Often related to:

```text
Incorrect SPN

Wrong hostname

DNS issue

Service principal not registered
```


# `STATUS_LOGON_FAILURE`

Possible causes:

```text
Incorrect username

Incorrect password/hash

Wrong domain

Authentication restriction
```


# `STATUS_ACCOUNT_LOCKED_OUT`

Stop testing that account.

Do not repeatedly retry credentials.


# `STATUS_ACCESS_DENIED`

This often means:

```text
Authentication succeeded
```

but:

```text
Requested action is not authorised
```

Separate authentication from authorisation.


# `rpc_s_access_denied`

The account does not have sufficient permission for the requested RPC operation.

This is not necessarily an authentication failure.


# `Connection Refused`

Possible causes:

```text
Service not listening

Firewall

Wrong port

Wrong host

Service disabled
```


# `Name or Service Not Known`

Check:

```bash
getent hosts target.corp.local
```

```bash
dig target.corp.local
```

DNS problems are especially important with Kerberos.


# Kerberos Works by Hostname but Not IP

This can be expected.

Kerberos uses service principal names that are normally associated with hostnames.

Prefer correct DNS names for Kerberos workflows.


# Ticket Not Found

Check:

```bash
echo "$KRB5CCNAME"
```

Then:

```bash
ls -l "$KRB5CCNAME"
```

if the variable contains a direct file path.

Finally:

```bash
klist
```


# Expired Ticket

`klist` shows ticket validity.

Do not troubleshoot network connectivity when the actual problem is simply an expired credential cache.


# Special Characters Break Target String

Use quoting:

```bash
'impacket-target-string'
```

rather than leaving shell-sensitive characters unquoted.


# Old Impacket Writeup Does Not Work

Check:

```bash
python3 -m pip show impacket
```

Then:

```bash
impacket-<tool> -h
```

Old examples may use different:

```text
Executable names

Arguments

Authentication flags

Target formats
```


# Tool Selection Guide

| Objective | Consider |
|---|---|
| List SMB shares | `smbclient` |
| Enumerate SPNs | `GetUserSPNs` |
| Assess no-preauth users | `GetNPUsers` |
| Request TGT | `getTGT` |
| Work with service tickets | `getST` |
| Convert ticket format | `ticketConverter` |
| Enumerate SIDs | `lookupsid` |
| Enumerate RPC endpoints | `rpcdump` |
| Query SAMR information | `samrdump` |
| Connect to MSSQL | `mssqlclient` |
| Validate WMI administration | `wmiexec` |
| Validate service-based administration | `psexec` / `smbexec` |
| Validate scheduled-task administration | `atexec` |
| Validate DCOM administration | `dcomexec` |
| Assess sensitive credential stores | `secretsdump` |


# Do Not Default to the Most Powerful Tool

Example:

```text
Question:
Can this user read the Finance share?
```

Use:

```text
SMB client
```

not:

```text
secretsdump
```

Another example:

```text
Question:
Does this account have SQL sysadmin?
```

Use:

```text
mssqlclient
+
SELECT IS_SRVROLEMEMBER('sysadmin');
```

not:

```text
Remote OS execution
```

Match the validation to the question.


# Evidence Collection

For each important Impacket test record:

```text
Test ID

Timestamp

Tool

Impacket version

Source system

Target system

Domain

Account

Protocol

Objective

Command

Relevant output

Interpretation

Security consequence

Cleanup
```


# Example Evidence Record

```text
Test ID:
AD-IMP-003

Timestamp:
2026-09-06 15:20 UTC

Tool:
Impacket GetUserSPNs

Version:
<installed version>

Source:
Assessment workstation

Target:
DC01 / 10.10.10.10

Domain:
corp.local

Identity:
CORP\asif

Objective:
Identify domain accounts associated with Service Principal Names.

Command:
impacket-GetUserSPNs 'corp.local/asif:<REDACTED>' -dc-ip 10.10.10.10

Result:
svc_sql associated with MSSQLSvc/sql01.corp.local:1433.

Interpretation:
The account is associated with an MSSQL service principal and
is therefore relevant to the Kerberos service-account review.

Security Conclusion:
No password weakness or account compromise is established by
SPN enumeration alone.
```


# Evidence for Remote Administration

Record:

```text
Account

Target

Protocol/mechanism

Authentication result

Privilege demonstrated

Command used

Minimal output

Any artefacts created

Cleanup performed
```


# Evidence for Credential Access

Do not preserve unnecessary credential material.

Prefer:

```text
Credential store access confirmed.
2 local account hashes were accessible.
Values redacted.
```

rather than including the reusable secrets.


# Evidence for Kerberos

Useful fields:

```text
Principal

Realm

SPN

Ticket type

Target service

Timestamp

Relevant configuration

Result
```

Avoid publishing complete reusable tickets.


# Reporting Example - Service Account

Avoid:

> `GetUserSPNs` found `svc_sql`, therefore the account is vulnerable to Kerberoasting.

Prefer:

> The domain account `CORP\svc_sql` is associated with the MSSQL service principal `MSSQLSvc/sql01.corp.local:1433`. This makes the account eligible for normal Kerberos service-ticket issuance. The security impact depends on the strength and management of the account credential and the privileges assigned to the service account. Further controlled validation should therefore focus on password resilience and account privilege rather than treating the SPN itself as a vulnerability.


# Reporting Example - No Preauthentication

Prefer:

> The account `CORP\legacy_service` is configured so that Kerberos preauthentication is not required. This configuration permits an unauthenticated requester to obtain password-derived authentication material for offline analysis. Review whether the configuration remains necessary and ensure the account uses a sufficiently strong managed credential.


# Reporting Example - Administrative Access

Prefer:

> The supplied domain credential successfully established a WMI-based administrative session on `SRV01`. This confirms that the account has sufficient remote-management privileges on the server. Review identified that the privilege is inherited through the `Server-Admins` domain group.


# Reporting Example - SQL Privilege

Prefer:

> The tested domain account successfully authenticated to `SQL01` using Windows authentication. A direct server-role query returned `1` for `IS_SRVROLEMEMBER('sysadmin')`, confirming that the account is a member of the SQL Server `sysadmin` role.


# Reporting Example - Credential Store Access

Prefer:

> Controlled validation confirmed that local administrative access to `SRV01` permits access to sensitive local credential material. Reusable credential values were not included in the report. This increases the impact of compromise of accounts with local administrative privileges and reinforces the need for unique managed local credentials and protection of privileged logon sessions.


# Remediation - Kerberoasting

Focus on:

```text
Long, high-entropy service-account passwords

gMSA where appropriate

Least privilege

Remove unnecessary SPNs

Reduce service-account privileges

Monitor abnormal service-ticket activity

Review legacy service identities
```


# Remediation - AS-REP

Focus on:

```text
Require Kerberos preauthentication

Use strong managed credentials

Review why the setting was disabled

Remove stale accounts

Restrict service-account privilege
```


# Remediation - Administrative Access

Focus on:

```text
Least privilege

Separate administrative accounts

Tiered administration

Restrict remote administration

Review local administrator membership

Use Windows LAPS

Reduce credential reuse
```


# Remediation - Credential Exposure

Focus on:

```text
Windows LAPS

gMSA

Credential Guard

Privileged access workstations

Administrative tiering

Limit privileged sessions

Reduce local administrator access

Monitor credential-access behaviour
```


# Remediation - SQL

Focus on:

```text
Least privilege

Remove unnecessary sysadmin membership

Separate application and administrative identities

Review linked servers

Restrict remote SQL exposure

Use managed service identities where appropriate

Audit privileged SQL operations
```


# Retesting

A retest should verify the root cause.

## Kerberos Preauthentication

Original:

```text
legacy_service
    |
    v
Preauthentication disabled
```

Retest:

```text
1. Re-query account configuration.
2. Confirm preauthentication is required.
3. Confirm the previous AS-REP condition is no longer present.
```


# Service Account Password

Original:

```text
Service Account
     |
     v
Weak Password
```

Retest:

```text
1. Confirm credential rotation.
2. Confirm password-management mechanism.
3. Verify account privilege was reviewed.
4. Repeat only the minimum authorised password-resilience test if required.
```


# Administrative Access

Original:

```text
CORP\asif
    |
    v
Admin on SRV01
```

After remediation:

```text
1. Validate normal authentication if still expected.
2. Confirm administrative remote-management action is denied.
3. Confirm group/policy assignment has been removed.
```


# SQL Privilege

Original:

```sql
SELECT IS_SRVROLEMEMBER('sysadmin');
```

Result:

```text
1
```

After remediation, repeat the same query.

Expected:

```text
0
```

assuming sysadmin membership was the issue being remediated.


# Detection Perspective

Impacket activity can generate telemetry across:

```text
Domain controllers

Windows Security logs

SMB

Kerberos

RPC

WMI

Service Control Manager

Task Scheduler

MSSQL

EDR

Network monitoring

SIEM
```


# Useful Windows Events

| Event ID | General Area |
|---:|---|
| 4624 | Successful logon |
| 4625 | Failed logon |
| 4648 | Explicit credentials |
| 4672 | Special privileges assigned |
| 4688 | Process creation |
| 4697 | Service installation |
| 4698 | Scheduled task created |
| 4768 | Kerberos TGT request |
| 4769 | Kerberos service-ticket request |
| 4771 | Kerberos preauthentication failure |
| 4776 | NTLM credential validation |

Telemetry depends on:

```text
Audit policy

Operating system

Protocol

Tool

Target role

EDR configuration

SIEM collection
```


# Kerberoasting Detection Questions

During controlled purple-team validation ask:

```text
Was the service-ticket request logged?

Which account requested it?

Which service account was targeted?

Which encryption type was used?

Was the volume unusual?

Did a detection fire?

Could the SOC distinguish normal application traffic from suspicious enumeration?
```


# AS-REP Detection Questions

Ask:

```text
Was the Kerberos request visible?

Was the account identified?

Was preauthentication state visible?

Did the SOC detect unusual requests?

Could analysts identify the source?
```


# Remote Administration Detection Questions

For WMI/service/task/DCOM-based validation ask:

```text
Was authentication visible?

Was the source host visible?

Was the account visible?

Was remote process execution visible?

Was service creation visible?

Was task creation visible?

Did EDR alert?

Could analysts reconstruct the complete sequence?
```


# Credential Access Detection Questions

Ask:

```text
Was sensitive process access visible?

Were registry/service interactions visible?

Was credential-store access detected?

Was remote administrative activity correlated?

Did the SOC identify the affected account and host?
```


# Impacket Operational Safety Checklist

Before a test:

```text
[ ] Target is in scope
[ ] Account is authorised
[ ] Objective is clear
[ ] Tool version checked
[ ] Help reviewed
[ ] DNS verified
[ ] Time verified for Kerberos
[ ] Potential system changes understood
[ ] Sensitive-data handling understood
[ ] Cleanup understood
```


# Impacket Assessment Checklist

## Environment

- [ ] Domain identified
- [ ] Domain controller identified
- [ ] DNS functioning
- [ ] Time synchronisation checked
- [ ] Target hostnames known
- [ ] Scope confirmed

## Tooling

- [ ] Impacket version recorded
- [ ] Installed command names confirmed
- [ ] Relevant `-h` output reviewed
- [ ] Old writeup syntax not assumed

## SMB

- [ ] SMB target identified
- [ ] Authentication validated where required
- [ ] Shares reviewed
- [ ] Share permissions interpreted
- [ ] Writable shares investigated in context
- [ ] Sensitive files handled appropriately

## RPC

- [ ] SID enumeration considered where relevant
- [ ] RPC endpoints considered
- [ ] SAMR information considered
- [ ] Enumeration distinguished from vulnerability

## Kerberos

- [ ] SPNs reviewed
- [ ] Service accounts identified
- [ ] Account privilege reviewed
- [ ] Preauthentication configuration reviewed
- [ ] TGT context understood
- [ ] Ticket cache inspected
- [ ] Delegation relationships understood before service-ticket operations
- [ ] Hostnames used correctly
- [ ] Clock skew considered

## Credential Material

- [ ] Password use kept narrow
- [ ] NTLM hash use kept narrow
- [ ] Kerberos ticket context understood
- [ ] Real secrets excluded from reports
- [ ] Sensitive evidence protected

## Remote Administration

- [ ] Need for remote execution established
- [ ] Appropriate mechanism selected
- [ ] WMI considered
- [ ] Service-based execution considered carefully
- [ ] Task-based execution considered carefully
- [ ] DCOM considered
- [ ] Artefacts understood
- [ ] Cleanup completed

## MSSQL

- [ ] Authentication validated
- [ ] Current identity queried
- [ ] Current database identified
- [ ] SQL role checked
- [ ] Linked servers considered
- [ ] OS privilege not assumed
- [ ] Database privilege documented accurately

## Secrets

- [ ] Credential extraction explicitly authorised
- [ ] Need established
- [ ] Target sensitivity considered
- [ ] DC actions treated as high impact
- [ ] Collection minimised
- [ ] Secrets redacted
- [ ] Evidence protected

## Interpretation

- [ ] Candidate distinguished from confirmed issue
- [ ] Authentication distinguished from authorisation
- [ ] SPN not treated as vulnerability by itself
- [ ] Ticket issuance not treated as compromise
- [ ] Administrative privilege independently understood
- [ ] Root cause identified

## Evidence

- [ ] Timestamp recorded
- [ ] Tool recorded
- [ ] Version recorded
- [ ] Source recorded
- [ ] Target recorded
- [ ] Account recorded
- [ ] Command recorded
- [ ] Credentials redacted
- [ ] Relevant output captured
- [ ] Interpretation written
- [ ] Cleanup recorded

## Retest

- [ ] Original condition identified
- [ ] Remediation confirmed
- [ ] Same narrow validation repeated
- [ ] Security consequence no longer reproducible
- [ ] Evidence captured


# Quick Command Reference

## Version

```bash
python3 -m pip show impacket
```

## Installed Tools

```bash
compgen -c | grep '^impacket-' | sort -u
```

## SMB Client

```bash
impacket-smbclient 'corp.local/asif:Password123!@10.10.10.20'
```

## SID Enumeration

```bash
impacket-lookupsid 'corp.local/asif:Password123!@10.10.10.10'
```

## RPC Endpoints

```bash
impacket-rpcdump 10.10.10.20
```

## SAMR Query

```bash
impacket-samrdump 'corp.local/asif:Password123!@10.10.10.20'
```

## SPN Enumeration

```bash
impacket-GetUserSPNs 'corp.local/asif:Password123!' -dc-ip 10.10.10.10
```

## No-Preauthentication Review

```bash
impacket-GetNPUsers -h
```

## Request TGT

```bash
impacket-getTGT 'corp.local/asif:Password123!' -dc-ip 10.10.10.10
```

## Ticket Cache

```bash
export KRB5CCNAME=/path/to/asif.ccache
klist
```

## Service-Ticket Tool

```bash
impacket-getST -h
```

## Ticket Conversion

```bash
impacket-ticketConverter -h
```

## WMI Administration

```bash
impacket-wmiexec 'corp.local/asif:Password123!@10.10.10.20'
```

## PSExec Help

```bash
impacket-psexec -h
```

## SMBExec Help

```bash
impacket-smbexec -h
```

## ATExec Help

```bash
impacket-atexec -h
```

## DCOMExec Help

```bash
impacket-dcomexec -h
```

## MSSQL

```bash
impacket-mssqlclient 'corp.local/asif:Password123!@10.10.10.30' -windows-auth
```

## SecretsDump Help

```bash
impacket-secretsdump -h
```


# Quick SQL Queries

Current identity:

```sql
SELECT SYSTEM_USER;
```

Server:

```sql
SELECT @@SERVERNAME;
```

Version:

```sql
SELECT @@VERSION;
```

Current database:

```sql
SELECT DB_NAME();
```

Sysadmin:

```sql
SELECT IS_SRVROLEMEMBER('sysadmin');
```


# Quick Kerberos Troubleshooting

```bash
date
```

```bash
klist
```

```bash
echo "$KRB5CCNAME"
```

```bash
getent hosts dc01.corp.local
```

```bash
dig _kerberos._tcp.corp.local SRV
```

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```


# Quick Interpretation Table

| Observation | What It Proves | What It Does Not Prove |
|---|---|---|
| SPN returned | Account is associated with a service principal | Weak password |
| No-preauth account | Kerberos preauthentication is not required | Password recovered |
| TGT obtained | Kerberos authentication context obtained | Administrative privilege |
| SMB share listed | Account can enumerate/access that share as shown | Admin access |
| NTLM hash accepted | Hash material authenticates in tested context | Plaintext password known |
| WMI session succeeds | Remote WMI administration is permitted | Domain Admin |
| SQL login succeeds | SQL authentication succeeded | SQL sysadmin |
| `IS_SRVROLEMEMBER('sysadmin') = 1` | Current SQL identity is sysadmin | Windows/domain admin |
| Credential store accessible | Tested privilege exposes sensitive credentials | Every recovered credential is reusable |
| RPC endpoint exists | RPC interface is exposed | Vulnerability exists |


# Impacket Decision Tree

```text
                         START
                           |
                           v
                     WHAT DO I HAVE?
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
     PASSWORD          NTLM HASH        KERBEROS TICKET
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                   WHAT IS THE OBJECTIVE?
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
   ENUMERATION         AUTHENTICATION      ADMINISTRATION
       |                   |                   |
       v                   v                   v
 GetUserSPNs          SMB / Kerberos      WMI / SMB / DCOM
 GetNPUsers           MSSQL               Task / Service
 lookupsid                |                   |
 rpcdump                  |                   |
       |                   |                   |
       +-------------------+-------------------+
                           |
                           v
                     RUN NARROW TEST
                           |
                           v
                    INTERPRET RESULT
                           |
                           v
                    WHAT DOES IT PROVE?
                           |
                           v
                  MORE VALIDATION NEEDED?
                       /          \
                     No            Yes
                     |              |
                     v              v
                  EVIDENCE     NEXT NARROW TEST
                     |              |
                     +------+-------+
                            |
                            v
                          REPORT
                            |
                            v
                         REMEDIATE
                            |
                            v
                          RETEST
```


# Complete Active Directory Workflow with Impacket

```text
                    AUTHORISED DOMAIN ACCESS
                             |
                             v
                       IDENTIFY DOMAIN
                             |
                             v
                          FIND DC
                             |
                             v
                      DNS / TIME CHECK
                             |
                             v
                    VALIDATE CREDENTIAL
                             |
               +-------------+-------------+
               |                           |
               v                           v
              SMB                       KERBEROS
               |                           |
               v                           v
            SHARES                       SPNs
               |                           |
               v                           v
        FILE / CONFIG REVIEW         PREAUTH REVIEW
               |                           |
               +-------------+-------------+
                             |
                             v
                         BLOODHOUND
                             |
                             v
                    PRIVILEGE RELATIONSHIP
                             |
                             v
                    CHOOSE TARGET SERVICE
                             |
            +----------------+----------------+
            |                |                |
            v                v                v
           SMB              WMI             MSSQL
            |                |                |
            +----------------+----------------+
                             |
                             v
                      MINIMAL VALIDATION
                             |
                             v
                        NEW ACCESS?
                         /       \
                       No         Yes
                       |           |
                       v           v
                    EVIDENCE    RE-ENUMERATE
                                   |
                                   v
                                EVIDENCE
                                   |
                       +-----------+
                       |
                       v
                     REPORT
                       |
                       v
                    REMEDIATE
                       |
                       v
                     RETEST
```


# Final Testing Principle

Impacket should not become:

```text
Tool List
   |
   v
Copy Commands
   |
   v
Run Everything
```

The stronger methodology is:

```text
Question
   |
   v
Protocol
   |
   v
Prerequisites
   |
   v
Specific Impacket Utility
   |
   v
Focused Command
   |
   v
Representative Result
   |
   v
Interpretation
   |
   v
Alternative Explanation
   |
   v
Minimal Additional Validation
   |
   v
Defensible Conclusion
```

For every Impacket result, be able to answer:

```text
What exactly did I test?

Why did I use this tool?

What prerequisite did I already establish?

What did the result prove?

What did it not prove?

What is the security consequence?

What additional evidence is actually necessary?

Can I stop here?
```


# Related Cheatsheets

- [Active Directory Cheatsheet](active-directory.md)
- [NetExec Cheatsheet](netexec.md)
- [BloodHound Cheatsheet](bloodhound.md)
- [Windows Cheatsheet](windows.md)
- [PowerShell Cheatsheet](powershell.md)
- [Networking Cheatsheet](networking.md)


# Detailed Notes

## Core Active Directory

- [Active Directory Overview](../active-directory/index.md)
- [Methodology](../active-directory/methodology.md)
- [Enumeration](../active-directory/enumeration.md)
- [Impacket](../active-directory/impacket.md)
- [NetExec](../active-directory/netexec.md)
- [BloodHound](../active-directory/bloodhound.md)

## Authentication

- [Kerberos](../active-directory/kerberos.md)
- [NTLM](../active-directory/ntlm.md)
- [Kerberoasting](../active-directory/kerberoasting.md)
- [AS-REP Roasting](../active-directory/asrep-roasting.md)
- [Pass-the-Hash](../active-directory/pass-the-hash.md)
- [Pass-the-Ticket](../active-directory/pass-the-ticket.md)
- [Pass-the-Key](../active-directory/pass-the-key.md)
- [OverPass-the-Hash](../active-directory/overpass-the-hash.md)

## Delegation

- [Unconstrained Delegation](../active-directory/unconstrained-delegation.md)
- [Constrained Delegation](../active-directory/constrained-delegation.md)
- [Resource-Based Constrained Delegation](../active-directory/rbcd.md)
- [S4U](../active-directory/s4u.md)

## Credential Access

- [Credential Access](../active-directory/credential-access.md)
- [NTDS](../active-directory/ntds.md)
- [LAPS](../active-directory/laps.md)
- [gMSA](../active-directory/gmsa.md)

## Remote Access

- [SMB](../active-directory/smb.md)
- [WinRM](../active-directory/winrm.md)
- [WMI](../active-directory/wmi.md)
- [DCOM](../active-directory/dcom.md)
- [Lateral Movement](../active-directory/lateral-movement.md)

## Privilege Relationships

- [ACL and ACE](../active-directory/acl-ace.md)
- [Privilege Escalation](../active-directory/privilege-escalation.md)
- [Trusts](../active-directory/trusts.md)
- [Trust Relationships](../active-directory/trust-relationships.md)


# References

- [Impacket GitHub](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }
- [Impacket Examples](https://github.com/fortra/impacket/tree/master/examples){ target="_blank" rel="noopener noreferrer" }
- [Fortra Impacket Documentation](https://www.secureauth.com/labs/open-source-tools/impacket/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - NTLM Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - SMB Overview](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Windows Management Instrumentation](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - SQL Server](https://learn.microsoft.com/en-us/sql/sql-server/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Use the smallest tool that answers the question"
    If the objective is to determine whether an account can read a share, use an SMB client. If the objective is to determine whether a SQL login is sysadmin, query the SQL role. Do not use a more intrusive remote-administration or credential-access technique when a smaller test already provides sufficient evidence.


!!! tip "Read the output, not just the exit status"
    A successful Impacket connection may prove authentication while still showing that the requested operation is denied. Separate authentication, authorisation and security impact when interpreting results.


!!! warning "Credential access is not routine enumeration"
    Utilities capable of accessing password hashes, tickets, secrets or domain credential material should be treated as sensitive assessment actions. Establish the need, authorisation, evidence-handling requirements and stop condition before using them.


!!! warning "A successful technique is not the end of the analysis"
    After a technique succeeds, determine why it succeeded, which permission or configuration enabled it, what security boundary was crossed, whether the access was expected, how defenders could observe it, and what change would remove the root cause.
