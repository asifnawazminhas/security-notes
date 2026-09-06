---
title: Active Directory Cheatsheet
description: Practical Active Directory penetration testing and red team reference covering enumeration, SMB, LDAP, Kerberos, NTLM, BloodHound, AD CS, delegation, ACLs, credentials, lateral movement, privilege paths and result interpretation.
---

# Active Directory Cheatsheet

This cheatsheet is a practical reference for assessing Microsoft Active Directory environments during authorised penetration tests, red team exercises and security labs.

It is designed around a simple question:

> **I have access to an Active Directory environment. What should I check next, what does the result mean, and where should I investigate further?**

For detailed explanations of individual techniques, use the [Active Directory Notes](../active-directory/index.md).

!!! warning "Authorised Security Testing"
    Only use these techniques against systems and environments you are explicitly authorised to test. Credential attacks, authentication testing and remote administration can lock accounts, trigger security controls or affect production systems.


# Quick Start

A typical Active Directory assessment progresses through:

```text
Identify Domain
      |
      v
Identify Domain Controllers
      |
      v
DNS
      |
      v
SMB / LDAP / Kerberos
      |
      v
Validate Credentials
      |
      v
Enumerate Users and Groups
      |
      v
Enumerate Computers
      |
      v
Enumerate Shares
      |
      v
BloodHound
      |
      v
Kerberos
      |
      +--> AS-REP Roasting
      |
      +--> Kerberoasting
      |
      +--> Delegation
      |
      v
AD CS
      |
      v
ACLs / Privilege Relationships
      |
      v
Credential Access
      |
      v
Lateral Movement
      |
      v
Privilege Paths
      |
      v
Validate
      |
      v
Evidence
      |
      v
Report
```


# Quick Reference Variables

Throughout this cheatsheet, examples use:

```bash
DOMAIN="corp.local"
DC="dc01.corp.local"
DC_IP="10.10.10.10"
USER="asif"
PASSWORD='Password123!'
TARGET="10.10.10.20"
```

For NTLM authentication examples:

```bash
NT_HASH="0123456789abcdef0123456789abcdef"
```

Replace all values with the authorised test environment.


# Know Your Starting Position

Before running tools, determine what you already have.

| Starting Position | Useful First Actions |
|---|---|
| Network access only | DNS, DC discovery, SMB, LDAP, Kerberos |
| Username only | Validate username carefully, review Kerberos opportunities |
| Domain credentials | NetExec, LDAP, BloodHound, shares, Kerberos |
| NTLM hash | Determine which approved tools/protocols accept hash authentication |
| Kerberos ticket | Confirm ticket cache and service/domain context |
| Local foothold | Host enumeration, domain context, identity, routes |
| Domain user shell | BloodHound, Kerberos, shares, ACLs, privilege paths |
| Local administrator | Determine whether privilege is local only or reusable elsewhere |
| Domain privilege | Identify why the privilege exists and affected trust boundaries |


# Environment Identification

## Current Windows Identity

```powershell
whoami
```

More detail:

```powershell
whoami /all
```

Domain information:

```powershell
whoami /fqdn
```

Environment variables:

```powershell
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:LOGONSERVER
```

### Interpretation

Example:

```text
CORP\asif
```

This indicates the current security context is associated with the `CORP` domain.

`whoami /all` is particularly useful because it shows:

```text
User SID

Group memberships

Privileges

Integrity level
```

Do not assume membership in a group automatically provides an exploitable privilege. Determine whether the membership actually grants access to a relevant resource.


# Discover the Domain

From Windows:

```powershell
systeminfo | findstr /B /C:"Domain"
```

PowerShell:

```powershell
[System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
```

Using `nltest`:

```cmd
nltest /dsgetdc:corp.local
```

### Representative Output

```text
DC: \\DC01.corp.local
Address: \\10.10.10.10
Dom Guid: ...
Dom Name: corp.local
Forest Name: corp.local
Dc Site Name: HQ
```

### Interpretation

This can identify:

```text
Domain controller

Domain

Forest

AD site
```

The domain controller is often the starting point for DNS, LDAP and Kerberos enumeration.


# Discover Domain Controllers

## DNS SRV Records

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```

Alternative:

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.corp.local
```

### Representative Output

```text
_ldap._tcp.dc._msdcs.corp.local. 600 IN SRV 0 100 389 dc01.corp.local.
```

### Interpretation

This indicates that:

```text
dc01.corp.local
```

advertises the LDAP domain-controller service for the domain.


# Resolve the Domain Controller

```bash
dig dc01.corp.local
```

or:

```bash
nslookup dc01.corp.local
```

Confirm:

```bash
ping -c 1 dc01.corp.local
```

Remember that ICMP may be blocked even when the host is reachable.


# Common Active Directory Ports

| Port | Protocol | Purpose |
|---:|---|---|
| 53 | DNS | Name resolution |
| 88 | Kerberos | Authentication |
| 135 | RPC | RPC endpoint mapper |
| 139 | NetBIOS | Legacy SMB |
| 389 | LDAP | Directory services |
| 445 | SMB | File sharing and remote administration |
| 464 | Kerberos | Password changes |
| 636 | LDAPS | LDAP over TLS |
| 3268 | Global Catalog | Forest-wide LDAP |
| 3269 | Global Catalog TLS | Forest-wide LDAP over TLS |
| 5985 | WinRM | HTTP |
| 5986 | WinRM | HTTPS |


# Initial Port Check

A focused scan against an authorised domain controller:

```bash
nmap -Pn -sT -p 53,88,135,139,389,445,464,636,3268,3269 "$DC_IP"
```

### Interpretation

A typical domain controller commonly exposes several of:

```text
53
88
135
389
445
464
3268
```

Port exposure alone does not constitute a vulnerability. It identifies services available for subsequent assessment.


# Time Synchronisation

Kerberos is sensitive to clock differences.

Check local time:

```bash
date
```

Check the DC's time information through SMB:

```bash
nxc smb "$DC_IP"
```

If Kerberos tools return clock-skew errors, compare your test system's time with the domain controller before troubleshooting credentials.


# DNS

Check the configured resolver:

```bash
cat /etc/resolv.conf
```

Query the domain:

```bash
dig "$DOMAIN"
```

Query the DC:

```bash
dig "$DC"
```

Reverse lookup:

```bash
dig -x "$DC_IP"
```

### Why DNS Matters

Active Directory depends heavily on DNS.

Incorrect DNS can cause apparently unrelated failures involving:

```text
Kerberos

LDAP

BloodHound

SMB hostnames

SPNs

Domain discovery
```

When a tool works by IP but fails by hostname, DNS should be one of the first things checked.


# `/etc/hosts` for Lab Environments

When appropriate for a controlled lab:

```text
10.10.10.10 dc01.corp.local dc01 corp.local
```

Check:

```bash
getent hosts dc01.corp.local
```

Prefer functioning DNS in real environments rather than relying extensively on static host entries.


# SMB Enumeration

## Basic NetExec SMB Enumeration

```bash
nxc smb "$DC_IP"
```

### Representative Output

```text
SMB  10.10.10.10  445  DC01  [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:corp.local) (signing:True) (SMBv1:False)
```

### Interpretation

Useful fields include:

```text
Hostname

Domain

Operating system

SMB signing

SMBv1
```

For example:

```text
signing:True
```

means SMB signing is enabled/required according to the tool's reported state.

Do not treat every SMB configuration value as a vulnerability without understanding the exact server configuration and attack prerequisites.


# Validate Domain Credentials

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASSWORD"
```

### Representative Output

```text
SMB  10.10.10.10  445  DC01  [+] corp.local\asif:Password123!
```

### Interpretation

`[+]` indicates authentication succeeded.

This proves that the supplied credential was accepted for the tested SMB authentication path.

It does **not** prove:

```text
Domain administrator access

Local administrator access

Access to every domain host

Access to every SMB share
```

Those require separate validation.


# Administrative SMB Access

Against an authorised member server:

```bash
nxc smb "$TARGET" -u "$USER" -p "$PASSWORD"
```

You may see output similar to:

```text
SMB  10.10.10.20  445  SRV01  [+] corp.local\asif:Password123! (Pwn3d!)
```

### Interpretation

`(Pwn3d!)` is NetExec's indication that the tested account has administrative-level access relevant to the SMB assessment on that host.

This should be investigated further:

```text
Why does the account have administrative access?

Is the privilege expected?

Is it local or domain-derived?

Which group or policy grants it?

Is the same privilege present on other systems?
```


# Avoid Unnecessary Credential Spray

Do not immediately run credentials against an entire subnet.

Start narrowly:

```bash
nxc smb "$DC_IP" -u "$USER" -p "$PASSWORD"
```

Then expand only when the engagement scope and objective justify it.

This reduces:

```text
Account lockout risk

Unnecessary authentication noise

Production impact

Scope mistakes
```


# Enumerate SMB Shares

```bash
nxc smb "$TARGET" -u "$USER" -p "$PASSWORD" --shares
```

### Representative Output

```text
SMB  10.10.10.20  445  SRV01  Share       Permissions
SMB  10.10.10.20  445  SRV01  -----       -----------
SMB  10.10.10.20  445  SRV01  ADMIN$      READ
SMB  10.10.10.20  445  SRV01  Public      READ,WRITE
```

### Interpretation

A writable share such as:

```text
Public READ,WRITE
```

is a candidate for further review.

It does not automatically constitute a vulnerability.

Determine:

```text
What data is stored there?

Who should have access?

Can files be modified?

Are files consumed by privileged processes?

Does the share contain credentials or configuration?

Is write access operationally expected?
```


# SMBClient

List shares:

```bash
smbclient -L "//$TARGET" -U "$DOMAIN/$USER"
```

Connect:

```bash
smbclient "//$TARGET/Public" -U "$DOMAIN/$USER"
```

Useful interactive commands:

```text
ls
cd
pwd
get
put
mkdir
help
exit
```

Only modify or upload files where authorised.


# Enumerate Domain Users with NetExec

Check the version-specific options first:

```bash
nxc ldap "$DC_IP" --help
```

NetExec syntax changes over time, so confirm the available LDAP enumeration options for the installed version rather than assuming an old flag remains valid.


# LDAP

LDAP provides structured access to Active Directory objects.

Useful object types include:

```text
Users

Groups

Computers

Organisational Units

Group Policies

Service accounts

Trusts

Certificate-related objects
```


# LDAP RootDSE

A useful initial LDAP query:

```bash
ldapsearch -x -H "ldap://$DC_IP" -s base namingContexts
```

### Representative Output

```text
namingContexts: DC=corp,DC=local
namingContexts: CN=Configuration,DC=corp,DC=local
namingContexts: CN=Schema,CN=Configuration,DC=corp,DC=local
```

### Interpretation

The domain naming context is:

```text
DC=corp,DC=local
```

This becomes the base DN for many LDAP queries.


# Authenticated LDAP Query

```bash
ldapsearch -x \
  -H "ldap://$DC_IP" \
  -D "$USER@$DOMAIN" \
  -w "$PASSWORD" \
  -b "DC=corp,DC=local" \
  "(objectClass=user)" \
  sAMAccountName
```

### Interpretation

Look for:

```text
sAMAccountName
```

which represents the traditional Active Directory logon name.

Large environments can return substantial output. Use narrow filters where possible.


# Query Computers

```bash
ldapsearch -x \
  -H "ldap://$DC_IP" \
  -D "$USER@$DOMAIN" \
  -w "$PASSWORD" \
  -b "DC=corp,DC=local" \
  "(objectClass=computer)" \
  dNSHostName
```

### Representative Result

```text
dNSHostName: DC01.corp.local
dNSHostName: SRV01.corp.local
dNSHostName: WS01.corp.local
```

This helps build an authorised host inventory.


# Query Groups

```bash
ldapsearch -x \
  -H "ldap://$DC_IP" \
  -D "$USER@$DOMAIN" \
  -w "$PASSWORD" \
  -b "DC=corp,DC=local" \
  "(objectClass=group)" \
  cn
```

Prioritise groups such as:

```text
Domain Admins

Enterprise Admins

Administrators

Server administration groups

Helpdesk groups

Application administration groups

Backup groups
```

Do not limit analysis to built-in privileged groups. Custom groups frequently provide important access.


# Native Windows Domain Enumeration

Current domain:

```cmd
net user /domain
```

Domain groups:

```cmd
net group /domain
```

Domain Admins:

```cmd
net group "Domain Admins" /domain
```

Specific user:

```cmd
net user asif /domain
```

### Why Native Commands Matter

They can provide useful context when:

```text
Third-party tooling is unavailable

Application control restricts tooling

You need a quick local check

You want to compare tool results
```


# PowerShell AD Module

If the Active Directory PowerShell module is available:

```powershell
Get-Module -ListAvailable ActiveDirectory
```

Import:

```powershell
Import-Module ActiveDirectory
```

Domain:

```powershell
Get-ADDomain
```

Forest:

```powershell
Get-ADForest
```

Users:

```powershell
Get-ADUser -Filter *
```

Computers:

```powershell
Get-ADComputer -Filter *
```

Groups:

```powershell
Get-ADGroup -Filter *
```

Group members:

```powershell
Get-ADGroupMember "Domain Admins"
```


# BloodHound

BloodHound helps model relationships between:

```text
Users

Groups

Computers

Sessions

ACLs

Delegation

Local administration

Remote access

Certificate Services
```

Its main value is not simply enumeration.

It helps answer:

> **How can the access I currently have lead to more privileged access?**


# BloodHound Collection Strategy

Start with the least disruptive collection appropriate for the engagement.

Before collection, confirm the collector's supported options:

```bash
bloodhound-python --help
```

or for SharpHound:

```powershell
.\SharpHound.exe --help
```

Collector syntax and available methods can change between versions.


# BloodHound Python

A common authenticated collection pattern is:

```bash
bloodhound-python \
  -u "$USER" \
  -p "$PASSWORD" \
  -d "$DOMAIN" \
  -ns "$DC_IP" \
  -c All
```

!!! caution
    `-c All` can perform substantially more collection than a narrow query. Review the collection methods and engagement requirements before using broad collection in production environments.


# BloodHound Output

Typical collection produces JSON files representing objects such as:

```text
users

groups

computers

domains

ous

gpos
```

Depending on collector and collection methods, additional relationship information may also be present.


# BloodHound Import

After collection:

```text
Collector
   |
   v
JSON / ZIP
   |
   v
BloodHound
   |
   v
Import
   |
   v
Graph Analysis
```

Verify that the imported dataset actually contains expected objects.


# Incomplete BloodHound Data

If BloodHound contains:

```text
Users: 0
Computers: 0
Groups: 0
```

or unexpectedly limited data, investigate:

```text
DNS resolution

Domain name

Domain controller selection

Credentials

LDAP connectivity

Collector errors

Collection method

Import errors
```

Do not interpret an empty graph as proof that no attack paths exist.


# BloodHound Analysis Priorities

Useful questions include:

```text
What can my current user control?

Which systems can my user administer?

Which groups can my user modify?

Which ACLs are interesting?

Which users have paths to privileged groups?

Which computers expose useful privilege relationships?

Which delegation relationships exist?

Which AD CS relationships exist?
```


# BloodHound Path Thinking

Avoid:

```text
Find Domain Admin.
```

Think instead:

```text
Current Principal
      |
      v
Relationship
      |
      v
Intermediate Principal
      |
      v
Computer / Group / ACL
      |
      v
Privilege Boundary
      |
      v
Target
```


# BloodHound Result Interpretation

A graph edge is a **relationship**, not automatically a confirmed exploit.

For every interesting edge ask:

```text
What does the relationship mean?

Which permissions create it?

Does it still exist?

Can my current principal exercise it?

Would exercising it modify the environment?

Is the action authorised?

What evidence can prove the risk safely?
```

See the [BloodHound Notes](../active-directory/bloodhound.md) for deeper analysis.


# Kerberos

Kerberos commonly involves:

```text
Client

KDC

TGT

TGS

SPN

Service
```

Simplified flow:

```text
User
 |
 v
AS-REQ
 |
 v
Domain Controller
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
Target Service
```


# Check Kerberos Tickets on Windows

```cmd
klist
```

### Representative Output

```text
Cached Tickets: (2)

#0> Client: asif @ CORP.LOCAL
    Server: krbtgt/CORP.LOCAL @ CORP.LOCAL
```

### Interpretation

A `krbtgt` ticket indicates a Ticket Granting Ticket is present in the current cache.

Other tickets may identify services the current security context has accessed.


# Kerberos from Linux

Impacket tools commonly support Kerberos authentication with options such as:

```text
-k
```

and ticket-cache usage.

Always inspect the specific tool:

```bash
impacket-GetUserSPNs -h
```

because authentication options differ between utilities.


# Kerberos Credential Cache

Check:

```bash
echo "$KRB5CCNAME"
```

List tickets:

```bash
klist
```

A cache path may resemble:

```text
FILE:/tmp/krb5cc_1000
```


# Kerberoasting

Kerberoasting targets accounts associated with Service Principal Names.

The important prerequisite is:

```text
Account has an SPN
```

Enumeration is therefore the first step.


# Enumerate SPNs

Using Impacket:

```bash
impacket-GetUserSPNs \
  "$DOMAIN/$USER:$PASSWORD" \
  -dc-ip "$DC_IP"
```

### Representative Output

```text
ServicePrincipalName          Name       MemberOf
----------------------------  ---------  ----------------
MSSQLSvc/sql01.corp.local     svc_sql
HTTP/web01.corp.local         svc_web
```

### Interpretation

This identifies accounts with SPNs.

An SPN does **not** itself mean:

```text
Weak password

Compromised account

Privilege escalation
```

It means the account is a candidate for Kerberos service-ticket analysis.


# Request Service Tickets

Where explicitly authorised, Impacket supports requesting service tickets for identified SPN accounts.

Check the installed syntax:

```bash
impacket-GetUserSPNs -h
```

The assessment should focus on:

```text
Which accounts have SPNs?

What privileges do they hold?

Are they human or service identities?

Are strong managed credentials used?

Would compromise create a meaningful attack path?
```

See [Kerberoasting](../active-directory/kerberoasting.md).


# AS-REP Roasting

AS-REP roasting applies when an account does not require Kerberos preauthentication.

The important condition is:

```text
DONT_REQ_PREAUTH
```

This is a specific account configuration, not a general property of Active Directory users.


# Identify AS-REP Candidates

With valid domain credentials, directory enumeration can identify accounts configured without Kerberos preauthentication.

For Impacket capabilities:

```bash
impacket-GetNPUsers -h
```

### Interpretation

A returned account should be investigated for:

```text
Why preauthentication is disabled

Account privilege

Account usage

Credential policy

Whether the configuration is still required
```

See [AS-REP Roasting](../active-directory/asrep-roasting.md).


# Password Spraying

Password spraying can cause:

```text
Account lockouts

Security alerts

Operational impact

Incident-response escalation
```

Before any spraying activity, determine:

```text
Is password spraying explicitly authorised?

What is the lockout threshold?

What is the observation window?

Which accounts are excluded?

What rate is approved?

Who must be notified?
```

See [Password Spraying](../active-directory/password-spraying.md).

Do not begin spraying merely because usernames have been enumerated.


# Account Lockout Policy

From a domain-connected Windows system:

```cmd
net accounts /domain
```

Review:

```text
Lockout threshold

Lockout duration

Lockout observation window

Minimum password age

Maximum password age
```

### Interpretation

The policy helps determine whether authentication testing could lock accounts.

It does not automatically account for:

```text
Fine-grained password policies

Identity-provider controls

Third-party authentication

Conditional access

Application-specific lockouts
```


# NTLM

NTLM remains relevant in many Active Directory environments.

During assessment, determine:

```text
Where NTLM is still used

Which systems accept it

Whether SMB signing is enforced

Whether LDAP signing is required

Whether Extended Protection is configured where applicable

Whether legacy authentication remains necessary
```

See [NTLM](../active-directory/ntlm.md).


# SMB Signing

Check with NetExec:

```bash
nxc smb "$DC_IP"
```

Example:

```text
(signing:True)
```

### Interpretation

SMB signing configuration affects the feasibility of some relay scenarios.

Do not conclude:

```text
SMB signing disabled = domain compromised
```

Relay feasibility depends on multiple conditions, including:

```text
Source authentication

Target protocol

Target signing requirements

Authentication method

Channel protections

Identity privilege

Network reachability
```


# NTLM Relay Assessment

Treat relay as a prerequisite chain:

```text
Can Authentication Be Induced?
           |
           v
Is NTLM Used?
           |
           v
Can Attacker Receive It?
           |
           v
Does Target Accept Relay?
           |
           v
Are Required Protections Missing?
           |
           v
What Privilege Does the Identity Have?
```

See:

- [NTLM Relay](../active-directory/ntlm-relay.md)
- [Authentication Coercion](../active-directory/authentication-coercion.md)


# LDAP Signing and Channel Binding

These controls can materially affect LDAP relay opportunities.

Assessment should determine:

```text
Is LDAP signing required?

Is LDAPS available?

Is channel binding enforced where relevant?

Which clients still depend on insecure compatibility settings?
```

Avoid reporting a generic relay vulnerability without validating the relevant protocol protections.


# Delegation

Important delegation categories include:

```text
Unconstrained Delegation

Constrained Delegation

Resource-Based Constrained Delegation
```


# Unconstrained Delegation

Look for computers or accounts configured for unconstrained delegation.

Questions:

```text
Which principal is trusted for delegation?

Is it a workstation or server?

Which users authenticate to it?

Are privileged identities protected?

Is the configuration still required?
```

See [Unconstrained Delegation](../active-directory/unconstrained-delegation.md).


# Constrained Delegation

Constrained delegation restricts which services may be delegated to.

Review:

```text
Principal

Allowed service

Target host

Protocol transition

Privilege of delegated identity
```

See [Constrained Delegation](../active-directory/constrained-delegation.md).


# Resource-Based Constrained Delegation

RBCD places delegation configuration on the target resource.

The important relationship is:

```text
Principal
    |
    v
Can Modify Relevant Target Attribute
    |
    v
Target Computer
```

A BloodHound relationship or writable attribute is a candidate requiring validation.

See [Resource-Based Constrained Delegation](../active-directory/rbcd.md).


# S4U

Service-for-User Kerberos extensions are relevant to several delegation scenarios.

Understand:

```text
S4U2Self

S4U2Proxy
```

before interpreting delegation paths.

See [S4U](../active-directory/s4u.md).


# ACLs and ACEs

Active Directory permissions can create indirect privilege paths.

Important rights may include:

```text
GenericAll

GenericWrite

WriteDACL

WriteOwner

AddMember

ForceChangePassword

WriteProperty
```

The exact security impact depends on the target object.


# ACL Analysis Model

```text
Principal
    |
    v
Permission
    |
    v
Target Object
    |
    v
Permitted Modification
    |
    v
Security Consequence
```

Example:

```text
Helpdesk Group
      |
      v
Can Modify
      |
      v
Server Admin Group
```

This may represent a privilege path, but the actual ACE and effective permissions should be verified before reporting.


# GenericAll

`GenericAll` generally represents extensive control over the target object.

But interpretation depends on whether the target is:

```text
User

Group

Computer

OU

GPO

Domain object
```

Do not describe all `GenericAll` relationships with the same impact.


# GenericWrite

`GenericWrite` permits writing a set of properties.

The practical impact depends on:

```text
Target object

Writable attributes

Inheritance

Security-sensitive properties
```


# WriteDACL

`WriteDACL` allows modification of the target object's discretionary ACL.

This can be highly significant because it may allow the principal to grant additional rights.

Validation should establish:

```text
Effective permission

Target importance

Inheritance

Safe proof

Potential privilege path
```


# WriteOwner

Ownership can affect the ability to modify an object's permissions.

Again:

```text
Ownership Relationship
        !=
Immediate Domain Compromise
```

Follow the complete path.


# Group Membership

Enumerate important groups:

```cmd
net group "Domain Admins" /domain
```

PowerShell:

```powershell
Get-ADGroupMember "Domain Admins" -Recursive
```

### Why Recursive Membership Matters

Privilege may be inherited through nested groups.

Example:

```text
asif
 |
 v
IT-Support
 |
 v
Server-Admins
 |
 v
Administrators
```

Looking only at direct membership may miss this relationship.


# Local Administrators

A domain user may have local administrative access without being a Domain Admin.

This distinction is critical:

```text
Local Administrator
       !=
Domain Administrator
```

Local administrative access may still create a wider attack path if:

```text
Credentials are reused

Privileged sessions exist

Management systems are reachable

Service accounts are present

Administrative tiers are weak
```


# LAPS

LAPS helps manage unique local administrator passwords.

Assessment questions include:

```text
Is LAPS deployed?

Which systems are covered?

Who can read the managed password?

Who can modify LAPS-related permissions?

Are legacy and Windows LAPS configurations understood?

Are privileged readers appropriately restricted?
```

See [LAPS](../active-directory/laps.md).


# gMSA

Group Managed Service Accounts provide automatically managed service-account passwords.

Assessment should determine:

```text
Which gMSAs exist?

Which systems use them?

Which principals can retrieve their managed passwords?

What privileges does the gMSA hold?
```

See [gMSA](../active-directory/gmsa.md).


# Machine Account Quota

Review the domain's machine-account creation policy.

The important question is not simply:

```text
Is MachineAccountQuota non-zero?
```

but:

```text
Can the current user create a computer?

Does that capability combine with another relationship?

Is the default behaviour required?

Does it enable a meaningful privilege path?
```

See [Machine Account Quota](../active-directory/machine-account-quota.md).


# Active Directory Certificate Services

AD CS can introduce privilege paths through:

```text
Certificate templates

Enrollment rights

Template permissions

CA configuration

Web enrollment

Certificate mapping

Authentication settings
```


# Find Certificate Services

With appropriate tooling, determine whether an enterprise CA exists.

Useful tools may include:

```text
Certipy

Certify

Native certificate utilities
```

Confirm your installed Certipy version:

```bash
certipy -h
```

or, depending on packaging:

```bash
certipy-ad -h
```


# Certipy Enumeration

Review the installed syntax:

```bash
certipy find -h
```

A typical authenticated assessment collects information about:

```text
Certificate authorities

Templates

Enrollment rights

Template settings

Potentially risky configurations
```

### Important

Do not report an `ESC` classification solely because a tool labels something as vulnerable.

Manually validate:

```text
Template settings

Enrollment rights

Effective permissions

CA configuration

Authentication capability

Current principal

Required prerequisites
```


# AD CS Review Model

```text
Certificate Authority
        |
        v
Certificate Template
        |
        v
Who Can Enroll?
        |
        v
Template Configuration
        |
        v
Certificate Purpose
        |
        v
Authentication Capability
        |
        v
Privilege Consequence
```


# ESC1

At a high level, ESC1 involves a certificate template configuration where an enrollee can influence identity information under conditions that can make authentication as another principal possible.

Review:

```text
Enrollment rights

Subject/SAN control

Authentication EKUs

Manager approval

Authorised signatures

Target identity
```

See [ESC1](../active-directory/ad-cs/esc1.md).


# ESC2 - ESC17

The detailed AD CS section contains separate notes for each currently documented ESC category:

```text
ESC1
ESC2
ESC3
ESC4
ESC5
ESC6
ESC7
ESC8
ESC9
ESC10
ESC11
ESC12
ESC13
ESC14
ESC15
ESC16
ESC17
```

Start with:

[Active Directory Certificate Services](../active-directory/ad-cs/index.md)


# AD CS Enumeration Results

When tooling reports something similar to:

```text
Template: ExampleTemplate
Enabled: True
Client Authentication: True
Enrollment Rights: CORP\Domain Users
```

do not stop at the output.

Ask:

```text
Can my principal actually enroll?

What identity can the certificate represent?

Can it be used for authentication?

Does the CA issue the template?

Are approvals required?

Are signatures required?

Which account would be affected?
```


# Certificate Evidence

Useful evidence includes:

```text
CA name

Template name

Template configuration

Enrollment rights

Relevant permissions

Authentication EKUs

Approval requirements

Target principal

Observed result
```

Avoid including unnecessary private-key material in reports.


# Shares

Shares often expose valuable operational context.

Prioritise:

```text
SYSVOL

NETLOGON

Application shares

Deployment shares

Backup shares

User shares

IT administration shares
```


# SYSVOL

Connect:

```bash
smbclient "//$DC/SYSVOL" -U "$DOMAIN/$USER"
```

Review:

```text
Group Policy files

Scripts

Configuration files

Deployment information
```

Do not modify SYSVOL during routine enumeration.


# NETLOGON

```bash
smbclient "//$DC/NETLOGON" -U "$DOMAIN/$USER"
```

Look for:

```text
Logon scripts

Configuration

Mapped-drive scripts

Legacy administrative scripts
```


# Search Downloaded Files

If files have been legitimately copied into an assessment workspace:

```bash
rg -n -i 'password|passwd|secret|token|apikey|api_key|connectionstring' .
```

Treat matches as candidates.

Example:

```text
config.xml:18:<Password>Example123!</Password>
```

This may indicate a credential, but verify:

```text
Is it active?

Which system uses it?

Is it a placeholder?

Is it encrypted?

What privilege does it provide?

Is validation authorised?
```


# Group Policy

Group Policy can affect:

```text
Security configuration

Local groups

Scripts

Software deployment

Firewall

PowerShell

Application control

Scheduled tasks

Registry settings
```

See [Group Policy](../active-directory/group-policy.md).


# Group Policy Result Interpretation

A GPO linked to an OU does not automatically mean every setting applies to every object in that OU.

Consider:

```text
Link status

Inheritance

Security filtering

WMI filtering

Enforced links

Block inheritance

Object type

Resultant policy
```


# Credential Access

Potential Active Directory credential sources include:

```text
Service accounts

Configuration files

Scripts

Deployment systems

Shares

Scheduled tasks

Application pools

Backup systems

CI/CD

Management platforms

Privileged sessions
```

Credential discovery should be driven by the engagement objective and data-handling rules.


# Credential Validation

If a credential is discovered:

```text
Credential
    |
    v
Identify Owner
    |
    v
Identify Intended Use
    |
    v
Determine Scope
    |
    v
Validate Minimally
    |
    v
Determine Privilege
    |
    v
Stop When Proven
```

Avoid unnecessary authentication attempts across the environment.


# Credential Reuse

A credential valid on one host should not automatically be tested against every system.

Instead determine:

```text
Account type

Expected administrative scope

Target systems

Authorised test boundaries

Lockout implications
```


# Pass-the-Hash

NTLM hashes may be accepted by some tools and protocols in circumstances where NTLM authentication is supported.

The important assessment question is:

```text
Does possession of this credential material permit authentication
to a security-relevant target?
```

See [Pass-the-Hash](../active-directory/pass-the-hash.md).


# Pass-the-Ticket

Kerberos tickets can represent existing authenticated security contexts.

Before analysing a ticket, identify:

```text
Client principal

Service principal

Ticket type

Validity

Domain

Encryption type
```

See [Pass-the-Ticket](../active-directory/pass-the-ticket.md).


# OverPass-the-Hash

OverPass-the-Hash concerns using credential material in a Kerberos authentication context rather than treating the technique as simply another SMB authentication method.

See [OverPass-the-Hash](../active-directory/overpass-the-hash.md).


# Pass-the-Key

Kerberos keys may also be relevant to authentication depending on the account and available key material.

See [Pass-the-Key](../active-directory/pass-the-key.md).


# Lateral Movement

Common Active Directory remote-management surfaces include:

```text
SMB

WinRM

WMI

DCOM

RDP

SSH

Management platforms
```

The presence of a protocol does not prove the current account can use it.


# WinRM Reachability

```bash
nmap -Pn -sT -p 5985,5986 "$TARGET"
```

### Interpretation

Open `5985` or `5986` indicates WinRM may be available.

It does not prove:

```text
Authentication succeeds

The current user has remote-management rights

The host is exploitable
```


# NetExec WinRM Validation

Check available syntax:

```bash
nxc winrm --help
```

A credential can be tested against a specifically authorised target using the installed version's authentication syntax.

Start with a single target rather than a large range.


# Evil-WinRM

For authorised remote administration:

```bash
evil-winrm -i "$TARGET" -u "$USER" -p "$PASSWORD"
```

### Interpretation

A successful session demonstrates that the account has sufficient access for the tested WinRM path.

Record:

```text
Target

Account

Privilege level

Group-derived access

Why access exists
```


# SMB Remote Administration

Administrative SMB access can indicate a lateral movement path.

The important chain is:

```text
Credential
    |
    v
Target Accepts Authentication
    |
    v
Administrative Rights
    |
    v
Remote Management Capability
```

Each step should be demonstrated separately.


# WMI

WMI may provide remote-management capabilities where:

```text
RPC is reachable

Authentication succeeds

The account has sufficient permissions
```

See [WMI](../active-directory/wmi.md).


# DCOM

DCOM is another Windows remote-management surface.

See [DCOM](../active-directory/dcom.md).

Treat DCOM access as a protocol and permission question rather than assuming its availability automatically enables lateral movement.


# RDP

Check:

```bash
nmap -Pn -sT -p 3389 "$TARGET"
```

An open port only demonstrates network reachability.

Determine separately:

```text
Can the user authenticate?

Does the user have RDP logon rights?

Is NLA required?

Is MFA involved?

Would an interactive logon be appropriate for the engagement?
```


# Pivoting

When internal systems are not directly reachable:

```text
Operator
    |
    v
Compromised / Test Host
    |
    v
Internal Network
```

Common authorised assessment options include:

```text
Ligolo-ng

Chisel

SSH forwarding

SOCKS proxying
```

See [Active Directory Pivoting](../active-directory/pivoting.md) and [Red Team Lateral Movement](../red-teaming/lateral-movement.md).


# Trusts

Active Directory environments may contain:

```text
Parent-child trusts

Forest trusts

External trusts

Shortcut trusts
```

See:

- [Trusts](../active-directory/trusts.md)
- [Trust Relationships](../active-directory/trust-relationships.md)


# Trust Analysis

For every trust determine:

```text
Source domain

Target domain

Direction

Transitivity

Trust type

SID filtering

Authentication scope

Privilege relationships
```

Do not assume:

```text
Trust Exists
    =
Privilege Escalation
```

The trust establishes a relationship. Additional permissions determine practical security impact.


# SID History

SID History can preserve access during migrations.

Review:

```text
Which accounts contain SIDHistory?

Which historical SID is present?

What access does that SID grant?

Is the configuration legitimate?

Is SID filtering relevant across the trust?
```

See [SID History](../active-directory/sid-history.md).


# Trust Tickets

Kerberos trust relationships involve inter-realm authentication material.

See [Trust Tickets](../active-directory/trust-tickets.md) for the detailed trust-ticket model.


# Domain Infrastructure

Do not limit AD assessment to users and domain controllers.

Important infrastructure may include:

```text
SCCM

WSUS

MDT

SCOM

ADFS

AD CS

DNS

Backup infrastructure

Virtualisation

Identity management

Privileged access systems
```


# SCCM

SCCM can represent an important administrative trust boundary because it manages large numbers of endpoints.

Questions:

```text
Who administers SCCM?

Which systems are managed?

Which accounts are used?

Where are distribution points?

What privileges do site servers hold?

Can low-privileged users interact with sensitive components?
```

See [SCCM](../active-directory/sccm.md).


# WSUS

Review:

```text
WSUS topology

Administrative permissions

Update approval model

Transport protections

Managed systems
```

See [WSUS](../active-directory/wsus.md).


# MDT

Deployment infrastructure may contain:

```text
Deployment credentials

Scripts

Configuration

Images

Domain join information
```

See [MDT](../active-directory/mdt.md).


# ADFS

Federation infrastructure can represent a critical identity boundary.

Review:

```text
Federation servers

Service accounts

Certificates

Trust relationships

Authentication methods

Administrative access
```

See [ADFS](../active-directory/adfs.md).


# Active Directory DNS

AD-integrated DNS can expose important infrastructure information.

See [ADIDNS](../active-directory/adidns.md).


# Privilege Escalation Decision Tree

```text
Current Domain User
        |
        v
Any Interesting Group Membership?
        |
    +---+---+
    |       |
   Yes      No
    |       |
    v       v
Analyse   BloodHound
Rights       |
             v
        Interesting ACL?
             |
         +---+---+
         |       |
        Yes      No
         |       |
         v       v
      Validate  Kerberos
                  |
             +----+----+
             |         |
          SPNs?     No-Preauth?
             |         |
             v         v
          Review     Review
             |
             v
          AD CS
             |
             v
        Delegation
             |
             v
          Shares
             |
             v
        Credentials
             |
             v
      Local Admin Rights
             |
             v
       Lateral Movement
             |
             v
      New Security Context
             |
             +--------> Repeat
```


# "I Have Credentials - What Next?"

```text
Valid Domain Credentials
          |
          +--> Confirm domain and DC
          |
          +--> SMB authentication
          |
          +--> LDAP enumeration
          |
          +--> Users
          |
          +--> Groups
          |
          +--> Computers
          |
          +--> Shares
          |
          +--> BloodHound
          |
          +--> SPNs
          |
          +--> No-preauth accounts
          |
          +--> Delegation
          |
          +--> AD CS
          |
          +--> ACL relationships
          |
          +--> Local admin relationships
          |
          +--> Trusts
          |
          +--> Privilege paths
```


# "I Have a Hash - What Next?"

```text
NTLM Hash
   |
   v
Identify Account
   |
   v
Determine Domain
   |
   v
Determine Intended Scope
   |
   v
Select One Authorised Target
   |
   v
Validate Authentication
   |
   v
Determine Privilege
   |
   v
Investigate Why Access Exists
```

Avoid immediately testing the hash against the entire environment.


# "I Have a Kerberos Ticket - What Next?"

```text
Ticket
  |
  v
klist
  |
  v
Identify Principal
  |
  v
Identify Service
  |
  v
Check Validity
  |
  v
Determine Target
  |
  v
Use Only for Authorised Validation
```


# "I Found a Service Account - What Next?"

```text
Service Account
      |
      +--> SPN?
      |
      +--> Group memberships?
      |
      +--> Local admin anywhere?
      |
      +--> Delegation?
      |
      +--> gMSA?
      |
      +--> Interactive logon?
      |
      +--> Password management?
      |
      +--> Application dependencies?
      |
      +--> Privilege path?
```


# "I Found an Interesting BloodHound Edge - What Next?"

```text
BloodHound Edge
      |
      v
Read Edge Meaning
      |
      v
Identify Source Principal
      |
      v
Identify Target
      |
      v
Verify Actual Permission
      |
      v
Determine Preconditions
      |
      v
Can It Be Safely Validated?
      |
    +-+--+
    |    |
   No   Yes
    |    |
    v    v
Document Minimal
Candidate Proof
         |
         v
      Evidence
```


# "I Found an AD CS Issue - What Next?"

```text
Tool Reports ESC Condition
          |
          v
Identify CA
          |
          v
Identify Template
          |
          v
Verify Enrollment Rights
          |
          v
Verify Template Settings
          |
          v
Verify Authentication Purpose
          |
          v
Verify Approval Requirements
          |
          v
Verify Effective Principal
          |
          v
Determine Security Impact
```


# Candidate vs Confirmed

This distinction is important throughout Active Directory testing.

## Candidate

Examples:

```text
SPN exists

Writable share exists

Interesting BloodHound edge exists

Template is flagged by tooling

Remote service is exposed

User belongs to an interesting group
```

These require further investigation.


## Likely

Examples:

```text
Current principal has a relevant ACL

Writable location is consumed by a privileged service

Certificate enrollment rights and risky settings coexist

Account has administrative group-derived rights
```

Multiple prerequisites are present.


## Confirmed

A controlled validation demonstrates the security consequence.

For example:

```text
Approved test account successfully performs the relevant
privileged action against the authorised test object.
```

Stop once sufficient evidence exists.


# Evidence Collection

For each important observation record:

```text
Timestamp

Source system

Target system

Domain

Account

Tool

Tool version

Command

Relevant output

Interpretation

Validation performed

Security impact

Cleanup
```


# Record Tool Versions

NetExec:

```bash
nxc --version
```

Impacket package information:

```bash
python3 -m pip show impacket
```

BloodHound Python:

```bash
bloodhound-python --help
```

Certipy:

```bash
certipy -h
```

Recording versions makes procedures easier to reproduce when syntax changes.


# Screenshot Guidance

A useful screenshot should show:

```text
Target

Relevant command

Relevant output

Security-relevant field
```

Avoid screenshots containing unnecessary:

```text
Passwords

Hashes

Private keys

Tokens

Personal information
```

Redact sensitive information where appropriate.


# Reporting an Attack Path

Avoid reporting every intermediate observation as an isolated high-severity finding.

Where appropriate, describe the complete path.

Example:

```text
Standard Domain User
        |
        v
Writable Group Membership
        |
        v
Server Administration Group
        |
        v
Local Administrator on APP01
        |
        v
Privileged Service Credential
        |
        v
Sensitive Application Access
```

This explains why the individual relationships matter.


# Example Attack-Path Evidence Table

| Step | Observation | Evidence | Result |
|---|---|---|---|
| 1 | User belongs to Helpdesk | LDAP | Confirmed |
| 2 | Helpdesk can modify Server-Admins | ACL | Confirmed |
| 3 | Server-Admins administer APP01 | BloodHound + validation | Confirmed |
| 4 | APP01 contains privileged application context | Host review | Confirmed |


# Reporting Language

Prefer:

> The `CORP\Helpdesk` group has effective permissions that allow modification of the `Server-Admins` group. The tested account is a member of `Helpdesk`. Controlled validation using an authorised test object confirmed that the delegated permission can be exercised.

Avoid:

> BloodHound says GenericAll, therefore Domain Admin.


# Common Errors

## `KRB_AP_ERR_SKEW`

Usually indicates a significant time difference between the client and KDC.

Check:

```bash
date
```

and compare with the domain environment.


## `KDC_ERR_PREAUTH_FAILED`

Possible causes include:

```text
Incorrect password

Incorrect key

Wrong principal

Domain mismatch

Authentication configuration
```

Do not assume the account does not exist.


## `STATUS_LOGON_FAILURE`

Possible causes:

```text
Incorrect username

Incorrect password

Wrong domain

Account restrictions

Authentication method mismatch
```


## `STATUS_ACCOUNT_LOCKED_OUT`

Stop authentication testing for that account.

Do not continue retrying credentials.


## LDAP Connection Works but Query Fails

Check:

```text
Base DN

Bind identity

LDAP vs LDAPS

Permissions

LDAP signing requirements

DNS

Query syntax
```


## BloodHound Collection Is Empty

Check:

```text
DNS

Domain

DC

Credentials

LDAP

Collection method

Collector errors

Import status
```


## Tool Command from an Old Writeup Does Not Work

Check:

```bash
tool --help
```

and:

```bash
tool --version
```

Security tooling changes frequently.

Prefer the syntax supported by the installed version over copying commands blindly from older writeups.


# Defensive Perspective

Active Directory assessment should also identify the defensive controls protecting each attack path.

Important controls include:

```text
Tiered administration

Privileged access workstations

Unique local administrator passwords

Windows LAPS

gMSA

Credential Guard

Protected Users

Authentication policies

SMB signing

LDAP signing

Extended Protection

Network segmentation

AD CS hardening

Kerberos configuration

NTLM restrictions

EDR

Identity monitoring

Directory auditing
```


# Useful Windows Events

Examples of security events frequently relevant to AD assessments include:

| Event ID | General Area |
|---:|---|
| 4624 | Successful logon |
| 4625 | Failed logon |
| 4648 | Explicit credentials |
| 4672 | Special privileges |
| 4688 | Process creation |
| 4720 | User created |
| 4728 | Member added to global group |
| 4732 | Member added to local group |
| 4756 | Member added to universal group |
| 4768 | Kerberos TGT request |
| 4769 | Kerberos service ticket request |
| 4771 | Kerberos preauthentication failure |
| 4776 | NTLM credential validation |

Event interpretation depends on:

```text
Audit policy

Log source

Domain-controller role

Operating-system version

Collection configuration
```


# Detection Questions

For every validated technique ask:

```text
Was authentication logged?

Was process execution visible?

Was directory modification logged?

Was an alert generated?

Could the SOC identify the account?

Could the SOC identify the source host?

Could the SOC identify the target?

Could analysts reconstruct the attack path?
```


# Remediation Themes

Common Active Directory remediation themes include:

```text
Least privilege

Remove unnecessary group memberships

Remove stale accounts

Restrict delegated permissions

Protect privileged identities

Use managed service accounts

Deploy LAPS

Reduce credential reuse

Harden Kerberos configuration

Reduce NTLM dependency

Require protocol protections

Segment administrative access

Harden AD CS

Monitor directory changes

Improve authentication monitoring

Separate administrative tiers
```


# Retesting

A good retest verifies the underlying privilege relationship rather than simply checking whether a tool stops reporting it.

Example:

```text
Original:

Helpdesk
   |
   v
Can Modify Server-Admins


Remediation:

Delegated permission removed


Retest:

1. Re-enumerate ACL.
2. Confirm permission no longer exists.
3. Confirm effective access is removed.
4. Confirm authorised test principal cannot perform the
   previously demonstrated modification.
```


# Active Directory Assessment Checklist

## Environment

- [ ] Current identity established
- [ ] Domain identified
- [ ] Forest identified
- [ ] Domain controller identified
- [ ] DNS working
- [ ] Time synchronisation checked
- [ ] Scope confirmed

## Services

- [ ] DNS reviewed
- [ ] Kerberos reviewed
- [ ] LDAP reviewed
- [ ] SMB reviewed
- [ ] RPC exposure understood
- [ ] Global Catalog identified
- [ ] WinRM reviewed where relevant
- [ ] RDP reviewed where relevant

## Accounts

- [ ] Users enumerated
- [ ] Privileged users identified
- [ ] Service accounts identified
- [ ] Disabled/stale accounts considered
- [ ] Group memberships reviewed
- [ ] Nested memberships reviewed

## Computers

- [ ] Domain controllers identified
- [ ] Servers identified
- [ ] Workstations identified
- [ ] Administrative systems identified
- [ ] Management infrastructure identified

## SMB

- [ ] SMB signing reviewed
- [ ] SMBv1 state reviewed
- [ ] Shares enumerated
- [ ] Read access reviewed
- [ ] Write access reviewed
- [ ] Sensitive share contents reviewed

## LDAP

- [ ] Base DN identified
- [ ] Authenticated LDAP validated
- [ ] Users queried
- [ ] Groups queried
- [ ] Computers queried
- [ ] Relevant attributes reviewed

## Kerberos

- [ ] SPNs reviewed
- [ ] Kerberoasting candidates reviewed
- [ ] Preauthentication configuration reviewed
- [ ] Delegation reviewed
- [ ] Ticket context understood
- [ ] Kerberos errors interpreted correctly

## BloodHound

- [ ] Collection method selected
- [ ] Data imported
- [ ] Dataset completeness checked
- [ ] Current-user paths reviewed
- [ ] ACL edges reviewed
- [ ] Local admin relationships reviewed
- [ ] Delegation reviewed
- [ ] AD CS relationships reviewed
- [ ] Interesting edges manually validated

## ACLs

- [ ] GenericAll reviewed
- [ ] GenericWrite reviewed
- [ ] WriteDACL reviewed
- [ ] WriteOwner reviewed
- [ ] Group modification rights reviewed
- [ ] User modification rights reviewed
- [ ] Computer modification rights reviewed
- [ ] OU/GPO rights reviewed

## Credentials

- [ ] Service-account exposure reviewed
- [ ] Share contents reviewed
- [ ] Scripts reviewed
- [ ] Configuration files reviewed
- [ ] Deployment infrastructure reviewed
- [ ] Credential reuse assessed carefully
- [ ] Validation kept minimal

## AD CS

- [ ] Enterprise CA identified
- [ ] Templates enumerated
- [ ] Enrollment rights reviewed
- [ ] Template permissions reviewed
- [ ] Authentication EKUs reviewed
- [ ] Approval requirements reviewed
- [ ] Tool findings manually validated
- [ ] Relevant ESC conditions reviewed

## Delegation

- [ ] Unconstrained delegation reviewed
- [ ] Constrained delegation reviewed
- [ ] RBCD reviewed
- [ ] S4U relationships understood

## Trusts

- [ ] Trusts enumerated
- [ ] Direction identified
- [ ] Transitivity identified
- [ ] Trust type identified
- [ ] SID filtering considered
- [ ] SID History reviewed
- [ ] Cross-domain privilege paths reviewed

## Infrastructure

- [ ] SCCM considered
- [ ] WSUS considered
- [ ] MDT considered
- [ ] SCOM considered
- [ ] ADFS considered
- [ ] AD-integrated DNS considered
- [ ] Backup infrastructure considered

## Lateral Movement

- [ ] Local administrator relationships reviewed
- [ ] SMB access reviewed
- [ ] WinRM access reviewed
- [ ] WMI access reviewed
- [ ] DCOM access reviewed
- [ ] RDP access reviewed
- [ ] Pivot requirements reviewed

## Evidence

- [ ] Commands recorded
- [ ] Tool versions recorded
- [ ] Relevant output captured
- [ ] Sensitive data minimised
- [ ] Candidate vs confirmed distinguished
- [ ] Attack paths documented
- [ ] Cleanup completed

## Defensive Validation

- [ ] Authentication telemetry reviewed
- [ ] Kerberos telemetry reviewed
- [ ] Directory-change telemetry reviewed
- [ ] Endpoint telemetry reviewed
- [ ] Relevant detections reviewed
- [ ] SOC visibility considered

## Reporting

- [ ] Root cause identified
- [ ] Security impact established
- [ ] Alternative explanations considered
- [ ] Attack-path context included
- [ ] Remediation addresses root cause
- [ ] Retest procedure documented


# Quick Commands

## Domain

```powershell
whoami
whoami /all
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:LOGONSERVER
```

## Domain Controller

```cmd
nltest /dsgetdc:corp.local
```

## DNS

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```

## SMB

```bash
nxc smb 10.10.10.10
```

## Validate Credentials

```bash
nxc smb 10.10.10.10 -u 'asif' -p 'Password123!'
```

## Shares

```bash
nxc smb 10.10.10.20 -u 'asif' -p 'Password123!' --shares
```

## SMBClient

```bash
smbclient -L //10.10.10.20 -U 'corp.local/asif'
```

## LDAP RootDSE

```bash
ldapsearch -x -H ldap://10.10.10.10 -s base namingContexts
```

## Domain Users from Windows

```cmd
net user /domain
```

## Domain Groups

```cmd
net group /domain
```

## Domain Admins

```cmd
net group "Domain Admins" /domain
```

## Kerberos Tickets

```cmd
klist
```

## SPNs

```bash
impacket-GetUserSPNs 'corp.local/asif:Password123!' -dc-ip 10.10.10.10
```

## BloodHound

```bash
bloodhound-python -u 'asif' -p 'Password123!' -d corp.local -ns 10.10.10.10 -c All
```

## WinRM

```bash
evil-winrm -i 10.10.10.20 -u 'asif' -p 'Password123!'
```

## Search Assessment Files

```bash
rg -n -i 'password|passwd|secret|token|apikey|api_key|connectionstring' .
```


# Practical Assessment Model

```text
                    DOMAIN ACCESS
                         |
                         v
                  IDENTIFY CONTEXT
                         |
             +-----------+-----------+
             |                       |
             v                       v
            DNS                     DC
             |                       |
             +-----------+-----------+
                         |
                         v
                  ENUMERATE SERVICES
                         |
                         v
                 VALIDATE CREDENTIAL
                         |
                         v
                DIRECTORY ENUMERATION
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
           USERS       GROUPS     COMPUTERS
             |           |           |
             +-----------+-----------+
                         |
                         v
                      SHARES
                         |
                         v
                    BLOODHOUND
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          KERBEROS      ACLs      DELEGATION
             |           |           |
             +-----------+-----------+
                         |
                         v
                       AD CS
                         |
                         v
                    CREDENTIALS
                         |
                         v
                  PRIVILEGE PATHS
                         |
                         v
                 LATERAL MOVEMENT
                         |
                         v
                  NEW ACCESS LEVEL
                         |
                         v
                  RE-ENUMERATE
                         |
                         v
                     VALIDATE
                         |
                         v
                      EVIDENCE
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

Do not use Active Directory tooling as:

```text
Run Tool
   |
   v
Copy Output
   |
   v
Report Vulnerability
```

Use it as:

```text
Enumerate
    |
    v
Identify Candidate
    |
    v
Understand Relationship
    |
    v
Check Preconditions
    |
    v
Validate Safely
    |
    v
Interpret Result
    |
    v
Determine Attack Path
    |
    v
Collect Evidence
    |
    v
Report Root Cause
    |
    v
Remediate
    |
    v
Retest
```

The command is only the beginning.

The important part is understanding what the result actually proves.


# Detailed Active Directory Notes

Use the full notes when you need deeper explanations.

## Core

- [Active Directory Overview](../active-directory/index.md)
- [Methodology](../active-directory/methodology.md)
- [Enumeration](../active-directory/enumeration.md)

## Tooling

- [NetExec](../active-directory/netexec.md)
- [Impacket](../active-directory/impacket.md)
- [BloodHound](../active-directory/bloodhound.md)

## Authentication

- [Kerberos](../active-directory/kerberos.md)
- [NTLM](../active-directory/ntlm.md)
- [Password Spraying](../active-directory/password-spraying.md)
- [AS-REP Roasting](../active-directory/asrep-roasting.md)
- [Kerberoasting](../active-directory/kerberoasting.md)
- [Pass-the-Hash](../active-directory/pass-the-hash.md)
- [OverPass-the-Hash](../active-directory/overpass-the-hash.md)
- [Pass-the-Key](../active-directory/pass-the-key.md)
- [Pass-the-Ticket](../active-directory/pass-the-ticket.md)

## Access Control

- [ACL and ACE](../active-directory/acl-ace.md)
- [Groups](../active-directory/groups.md)
- [Group Policy](../active-directory/group-policy.md)
- [Machine Account Quota](../active-directory/machine-account-quota.md)

## Delegation

- [Unconstrained Delegation](../active-directory/unconstrained-delegation.md)
- [Constrained Delegation](../active-directory/constrained-delegation.md)
- [Resource-Based Constrained Delegation](../active-directory/rbcd.md)
- [S4U](../active-directory/s4u.md)

## Credential Access

- [Credential Access](../active-directory/credential-access.md)
- [LAPS](../active-directory/laps.md)
- [gMSA](../active-directory/gmsa.md)
- [Shadow Credentials](../active-directory/shadow-credentials.md)
- [NTDS](../active-directory/ntds.md)

## Relay and Coercion

- [NTLM Relay](../active-directory/ntlm-relay.md)
- [Kerberos Relay](../active-directory/kerberos-relay.md)
- [Authentication Coercion](../active-directory/authentication-coercion.md)

## AD CS

- [Active Directory Certificate Services](../active-directory/ad-cs/index.md)
- [AD CS Enumeration](../active-directory/ad-cs/enumeration.md)
- [ESC1](../active-directory/ad-cs/esc1.md)
- [ESC2](../active-directory/ad-cs/esc2.md)
- [ESC3](../active-directory/ad-cs/esc3.md)
- [ESC4](../active-directory/ad-cs/esc4.md)
- [ESC5](../active-directory/ad-cs/esc5.md)
- [ESC6](../active-directory/ad-cs/esc6.md)
- [ESC7](../active-directory/ad-cs/esc7.md)
- [ESC8](../active-directory/ad-cs/esc8.md)
- [ESC9](../active-directory/ad-cs/esc9.md)
- [ESC10](../active-directory/ad-cs/esc10.md)
- [ESC11](../active-directory/ad-cs/esc11.md)
- [ESC12](../active-directory/ad-cs/esc12.md)
- [ESC13](../active-directory/ad-cs/esc13.md)
- [ESC14](../active-directory/ad-cs/esc14.md)
- [ESC15](../active-directory/ad-cs/esc15.md)
- [ESC16](../active-directory/ad-cs/esc16.md)
- [ESC17](../active-directory/ad-cs/esc17.md)
- [Golden Certificate](../active-directory/ad-cs/golden-certificate.md)

## Lateral Movement

- [Lateral Movement](../active-directory/lateral-movement.md)
- [SMB](../active-directory/smb.md)
- [WinRM](../active-directory/winrm.md)
- [WMI](../active-directory/wmi.md)
- [DCOM](../active-directory/dcom.md)
- [Pivoting](../active-directory/pivoting.md)

## Trusts

- [Trusts](../active-directory/trusts.md)
- [Trust Relationships](../active-directory/trust-relationships.md)
- [SID History](../active-directory/sid-history.md)
- [Trust Tickets](../active-directory/trust-tickets.md)

## Infrastructure

- [AD Integrated DNS](../active-directory/adidns.md)
- [Shares](../active-directory/shares.md)
- [SCCM](../active-directory/sccm.md)
- [WSUS](../active-directory/wsus.md)
- [MDT](../active-directory/mdt.md)
- [SCOM](../active-directory/scom.md)
- [ADFS](../active-directory/adfs.md)
- [RODC](../active-directory/rodc.md)

## Privilege and Persistence

- [Privilege Escalation](../active-directory/privilege-escalation.md)
- [Persistence](../active-directory/persistence.md)


# Related Cheatsheets

- [NetExec](netexec.md)
- [Impacket](impacket.md)
- [BloodHound](bloodhound.md)
- [Windows](windows.md)
- [PowerShell](powershell.md)
- [Networking](networking.md)


# References

- [Microsoft Learn - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - NTLM Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Windows LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Group Managed Service Accounts](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }
- [NetExec](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }
- [Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }
- [BloodHound](https://github.com/SpecterOps/BloodHound){ target="_blank" rel="noopener noreferrer" }
- [BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }
- [Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }
- [The Hacker Recipes - Active Directory](https://www.thehacker.recipes/ad/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Use the detailed notes when the cheatsheet stops being enough"
    The purpose of this page is to help you move quickly from an observation to the correct next question. The detailed Active Directory pages contain the deeper explanation for individual protocols, techniques and privilege relationships.


!!! tip "Re-enumerate after privilege changes"
    Active Directory assessment is iterative. New credentials, group membership, host access or delegated rights may reveal relationships that were not relevant from the previous security context.


!!! warning "A tool finding is not automatically a vulnerability"
    NetExec, BloodHound, Certipy, Impacket and other tools provide evidence and identify candidates. Confirm prerequisites, effective permissions, security context and practical impact before reporting a vulnerability.
