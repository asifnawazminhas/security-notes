# Impacket Cheatsheet

Quick-reference commands and workflows for using Impacket during authorised Windows and Active Directory security assessments.

Impacket is a collection of Python classes and example tools for interacting with Microsoft network protocols.

It is particularly useful for:

```text
Active Directory Enumeration
SMB
MSRPC
Kerberos
NTLM
LDAP
WMI
DCOM
MSSQL / TDS
Remote Registry
Service Control
Task Scheduler
Credential Assessment
Delegation
ACL Analysis
NTLM Relay
```

!!! warning "Authorised testing only"
    Some Impacket tools can access credentials, modify Active Directory objects, perform remote administration, create services or scheduled tasks, manipulate delegation, or interact with domain replication functionality. Use these capabilities only when explicitly permitted by the assessment scope and rules of engagement.

For detailed explanations of the underlying techniques see:

[Impacket](../active-directory/impacket.md)

[Active Directory Cheatsheet](active-directory.md)

[NetExec Cheatsheet](netexec.md)

[BloodHound Cheatsheet](bloodhound.md)

---

# Quick Tool Map

| Goal | Impacket Tool |
|---|---|
| Enumerate AD users | `GetADUsers` |
| Enumerate AD computers | `GetADComputers` |
| Find AS-REP candidates | `GetNPUsers` |
| Enumerate SPNs | `GetUserSPNs` |
| Enumerate SIDs / RIDs | `lookupsid` |
| Enumerate delegation | `findDelegation` |
| Read LAPS passwords where authorised | `GetLAPSPassword` |
| Review legacy GPP passwords | `Get-GPPPassword` |
| Enumerate RPC endpoints | `rpcdump` |
| Map RPC interfaces | `rpcmap` |
| Enumerate SAMR information | `samrdump` |
| Query WMI | `wmiquery` |
| Access SMB shares | `smbclient` |
| Host an SMB share | `smbserver` |
| Enumerate MSSQL instances | `mssqlinstance` |
| Access MSSQL | `mssqlclient` |
| Validate RDP authentication | `rdp_check` |
| Request a TGT | `getTGT` |
| Request a service ticket | `getST` |
| Inspect delegation | `findDelegation` |
| Convert Kerberos tickets | `ticketConverter` |
| Describe Kerberos tickets | `describeTicket` |
| Create Kerberos tickets | `ticketer` |
| Inspect PAC information | `getPac` |
| Access Windows secrets | `secretsdump` |
| Service-based remote administration | `psexec` |
| WMI remote administration | `wmiexec` |
| SMB/service remote administration | `smbexec` |
| DCOM remote administration | `dcomexec` |
| Task Scheduler remote administration | `atexec` |
| Change an authorised password | `changepasswd` |
| Read/edit AD ACLs | `dacledit` |
| Read/edit AD object ownership | `owneredit` |
| Review/manage RBCD | `rbcd` |
| NTLM relay testing | `ntlmrelayx` |

---

# Current Version

Check the installed version:

```bash
python3 -c "from importlib.metadata import version; print(version('impacket'))"
```

At the time this cheatsheet was updated:

```text
Stable:      Impacket 0.13.1
Development: Impacket 0.14.0-dev
```

Do not assume commands from `master` are available in the stable release.

---

# Installation

The upstream project recommends `pipx` for system-wide installations.

```bash
sudo apt update
sudo apt install pipx
```

```bash
pipx ensurepath
```

Install:

```bash
python3 -m pipx install impacket
```

Check:

```bash
pipx list
```

---

# Kali Linux

Kali may provide Impacket through its repositories:

```bash
sudo apt update
sudo apt install python3-impacket
```

Check:

```bash
apt policy python3-impacket
```

Find a command:

```bash
which impacket-GetADUsers
```

The Kali package version may differ from upstream.

---

# Command Naming

Packaged commands commonly use:

```text
impacket-GetADUsers
impacket-GetADComputers
impacket-GetNPUsers
impacket-GetUserSPNs
impacket-lookupsid
impacket-findDelegation
impacket-smbclient
impacket-getTGT
impacket-getST
impacket-secretsdump
```

Source installations may instead use:

```text
GetADUsers.py
GetADComputers.py
GetNPUsers.py
GetUserSPNs.py
lookupsid.py
findDelegation.py
smbclient.py
getTGT.py
getST.py
secretsdump.py
```

List installed packaged tools:

```bash
compgen -c | grep '^impacket-' | sort -u
```

---

# Help First

Always check the installed version:

```bash
impacket-GetADUsers -h
```

```bash
impacket-GetADComputers -h
```

```bash
impacket-GetUserSPNs -h
```

```bash
impacket-getTGT -h
```

```bash
impacket-getST -h
```

```bash
impacket-secretsdump -h
```

This is especially important for development-version features.

---

# Assessment Variables

A convenient shell setup:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DC_IP="10.10.20.10"
export USER="alice"
```

Check:

```bash
printf 'DOMAIN=%s\nDC=%s\nDC_IP=%s\nUSER=%s\n' "$DOMAIN" "$DC" "$DC_IP" "$USER"
```

---

# Before Impacket - DNS

Resolve the Domain Controller:

```bash
dig "$DC"
```

LDAP:

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

Kerberos:

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

Resolver:

```bash
cat /etc/resolv.conf
```

Kerberos and LDAP operations frequently fail because of DNS rather than credentials.

---

# Before Impacket - Time

```bash
date
```

```bash
timedatectl
```

Kerberos is time-sensitive.

Think:

```text
Kerberos Failure
      |
      +--> DNS?
      |
      +--> Time?
      |
      +--> Realm?
      |
      +--> FQDN?
      |
      +--> SPN?
      |
      +--> KDC?
      |
      +--> Ticket?
      |
      +--> Credential?
```

---

# Authentication Quick Reference

Impacket commonly supports:

```text
Password
NTLM Hash
Kerberos Ticket
AES Key
Kerberos Credential Cache
```

The exact authentication options vary by tool.

---

# Password Authentication

Common target form:

```text
domain/user:password@target
```

Example:

```bash
impacket-smbclient 'example.local/alice:Password@file01.example.local'
```

Prefer interactive prompting where supported:

```bash
impacket-smbclient 'example.local/alice@file01.example.local'
```

!!! warning
    Passwords supplied directly on the command line can appear in shell history, process listings, screenshots and terminal logs.

---

# NTLM Hash Authentication

Common option:

```text
-hashes LMHASH:NTHASH
```

When only the NT hash is available:

```text
-hashes :NTHASH
```

Example structure:

```bash
impacket-smbclient \
    'example.local/alice@file01.example.local' \
    -hashes ':<NT-HASH>'
```

Treat hashes as credentials.

---

# Kerberos Authentication

Many Impacket examples support:

```text
-k
-no-pass
-aesKey
-dc-ip
-target-ip
```

Exact support depends on the tool.

Check:

```bash
<tool> -h
```

---

# Kerberos Credential Cache

Set:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Check:

```bash
echo "$KRB5CCNAME"
```

Inspect:

```bash
klist
```

Protect `.ccache` files like passwords.

---

# Kerberos Checklist

```text
[ ] Correct domain
[ ] Correct username
[ ] Correct DC
[ ] FQDN resolves
[ ] Internal DNS works
[ ] KDC reachable
[ ] Time synchronised
[ ] Correct ticket loaded
[ ] Correct SPN used
[ ] Correct realm used
```

---

# AES Authentication

Where supported:

```text
-aesKey <AES_KEY>
```

Check:

```bash
impacket-getTGT -h
```

AES keys are authentication material and should receive the same protection as passwords and hashes.

---

# AD User Enumeration

## GetADUsers

Help:

```bash
impacket-GetADUsers -h
```

Enumerate users:

```bash
impacket-GetADUsers \
    "$DOMAIN/$USER" \
    -dc-ip "$DC_IP" \
    -all
```

Enter the password interactively when prompted.

Useful fields may include:

```text
Username
Email
Password Last Set
Last Logon
Description
```

---

# Specific AD User

Current versions support querying specific user information.

Check:

```bash
impacket-GetADUsers -h
```

Use targeted enumeration where possible rather than collecting unnecessary directory information.

---

# AD Computer Enumeration

## GetADComputers

Help:

```bash
impacket-GetADComputers -h
```

Enumerate computer objects:

```bash
impacket-GetADComputers \
    "$DOMAIN/$USER" \
    -dc-ip "$DC_IP"
```

Resolve discovered computer addresses where supported:

```bash
impacket-GetADComputers \
    "$DOMAIN/$USER" \
    -dc-ip "$DC_IP" \
    -resolveIP
```

Useful information can include:

```text
Computer Account
DNS Hostname
Operating System
Operating System Version
Last Logon
IP Address
```

---

# Computer Enumeration Workflow

```text
GetADComputers
       |
       v
Computer Objects
       |
       +--> Workstations
       +--> Servers
       +--> Domain Controllers
       +--> Legacy Systems
       +--> Stale Objects
       |
       v
Network Validation
```

Remember:

```text
AD computer object
        !=
currently reachable host
```

---

# AS-REP Candidates

## GetNPUsers

Help:

```bash
impacket-GetNPUsers -h
```

This tool is relevant to accounts configured without Kerberos pre-authentication.

Think:

```text
Domain User
    |
    v
Preauthentication Required?
    |
 +--+--+
 |     |
Yes    No
 |     |
 v     v
Normal Candidate
```

Do not assume an account is exploitable merely because pre-authentication is disabled.

Consider:

```text
Password Strength
Account Privilege
Account Purpose
Monitoring
Compensating Controls
```

See:

```text
active-directory/asrep-roasting.md
```

---

# SPN Enumeration

## GetUserSPNs

Help:

```bash
impacket-GetUserSPNs -h
```

Enumerate SPN accounts:

```bash
impacket-GetUserSPNs \
    "$DOMAIN/$USER" \
    -dc-ip "$DC_IP"
```

Useful output can include:

```text
ServicePrincipalName
Account
Group Membership
Password Last Set
Last Logon
Delegation
```

---

# SPN Analysis

Do not report:

```text
SPN exists
```

as a vulnerability.

Use:

```text
SPN
 |
 v
Account
 |
 v
Service Account?
 |
 v
Password Age
 |
 v
Password Strength
 |
 v
Privileges
 |
 v
Security Impact
```

---

# Cross-Domain SPN Enumeration

Current versions may support:

```text
-target-domain
```

Check:

```bash
impacket-GetUserSPNs -h
```

This is useful where trusted domains are explicitly in scope.

---

# SID and RID Enumeration

## lookupsid

Help:

```bash
impacket-lookupsid -h
```

Example:

```bash
impacket-lookupsid \
    "$DOMAIN/$USER@$DC"
```

---

# SID Structure

Example:

```text
S-1-5-21-111111111-222222222-333333333-1105
```

Domain SID:

```text
S-1-5-21-111111111-222222222-333333333
```

RID:

```text
1105
```

---

# Delegation Enumeration

## findDelegation

Help:

```bash
impacket-findDelegation -h
```

Enumerate:

```bash
impacket-findDelegation \
    "$DOMAIN/$USER" \
    -dc-ip "$DC_IP"
```

Review:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

---

# Delegation Analysis

```text
Principal
    |
    v
Delegation Type
    |
    v
Target Service
    |
    v
Who Controls Principal?
    |
    v
Prerequisites
    |
    v
Security Boundary
    |
    v
Potential Path
```

Do not equate:

```text
Delegation configured
```

with:

```text
Exploitable privilege escalation
```

---

# LAPS

## GetLAPSPassword

Modern Impacket includes LAPS-related functionality.

Check:

```bash
impacket-GetLAPSPassword -h
```

Use only with an identity that is explicitly authorised for the assessment.

The important security question is:

```text
Who can read the managed local administrator password?
```

not merely:

```text
Does LAPS exist?
```

---

# LAPS Assessment Model

```text
Computer
   |
   v
LAPS Enabled?
   |
   v
Password Attribute
   |
   v
Who Can Read?
   |
   v
Expected?
   |
   v
Privilege Boundary
```

See:

```text
active-directory/laps.md
```

---

# Group Policy Preferences Passwords

## Get-GPPPassword

Check:

```bash
impacket-Get-GPPPassword -h
```

This tool is relevant to legacy Group Policy Preferences credentials stored in SYSVOL.

The assessment question is:

```text
Does SYSVOL contain legacy GPP credential material?
```

rather than indiscriminately searching every domain file.

See:

```text
active-directory/gpp-passwords.md
```

---

# RPC Endpoint Enumeration

## rpcdump

Help:

```bash
impacket-rpcdump -h
```

Typical form:

```bash
impacket-rpcdump \
    "$DOMAIN/$USER@$DC"
```

Useful for identifying:

```text
RPC Interfaces
Endpoints
Protocol Sequences
Exposed Windows Services
```

---

# RPC Mapping

## rpcmap

Help:

```bash
impacket-rpcmap -h
```

Use it when a specific RPC interface or transport needs investigation.

RPC exposure itself is not automatically a vulnerability.

---

# SAMR Enumeration

## samrdump

Help:

```bash
impacket-samrdump -h
```

Typical structure:

```bash
impacket-samrdump \
    "$DOMAIN/$USER@$DC"
```

Depending on permissions, SAMR may expose:

```text
Users
Groups
Account Information
Domain Information
```

---

# SMB Client

## smbclient

Connect:

```bash
impacket-smbclient \
    "$DOMAIN/$USER@file01.$DOMAIN"
```

Use:

```text
help
```

inside the interactive client.

---

# SMB Workflow

```text
NetExec --shares
       |
       v
Interesting Share
       |
       v
impacket-smbclient
       |
       v
Focused Inspection
       |
       v
Evidence
```

Avoid recursively downloading entire corporate file shares.

---

# Interesting Share Content

Depending on scope, review:

```text
Configuration Files
Deployment Scripts
PowerShell Scripts
Batch Files
Backup Files
Connection Strings
Certificates
Keys
Administrative Documentation
Software Deployment Content
```

Validate whether discovered information is actually sensitive before reporting.

---

# SMB Server

## smbserver

Help:

```bash
impacket-smbserver -h
```

Create a controlled share directory:

```bash
mkdir -p /tmp/assessment-share
```

Start:

```bash
impacket-smbserver ASSESSMENT /tmp/assessment-share
```

Bind/expose the server only as required by the engagement.

---

# SMB Server Checklist

```text
[ ] Correct interface
[ ] Firewall understood
[ ] Share contents reviewed
[ ] Authentication considered
[ ] No customer secrets exposed
[ ] Server stopped after testing
```

---

# SMB Information

Impacket also contains tools useful for obtaining SMB/NTLM information.

List your installation:

```bash
compgen -c | grep '^impacket-' | grep -Ei 'smb|ntlm'
```

Use tool-specific help before testing.

---

# WMI Querying

## wmiquery

Help:

```bash
impacket-wmiquery -h
```

Connect:

```bash
impacket-wmiquery \
    "$DOMAIN/$USER@server01.$DOMAIN"
```

This provides a WQL-oriented shell.

Safe inventory-style examples include:

```text
select Caption,Version from Win32_OperatingSystem
```

```text
select Name,State,StartMode from Win32_Service
```

```text
select Name,ProcessId from Win32_Process
```

Use:

```text
describe Win32_Process
```

to inspect a class.

---

# WMI Security Model

WMI access depends on more than successful SMB authentication.

Think:

```text
Identity
   |
   v
DCOM Connectivity
   |
   v
WMI Namespace
   |
   v
Namespace Permissions
   |
   v
RPC Authentication Level
   |
   v
Query / Management Access
```

---

# MSSQL Instance Discovery

## mssqlinstance

Help:

```bash
impacket-mssqlinstance -h
```

This can assist with identifying Microsoft SQL Server instances where the relevant discovery service is reachable.

Confirm results with normal network/service enumeration.

---

# MSSQL Client

## mssqlclient

Help:

```bash
impacket-mssqlclient -h
```

Connect using an authorised account:

```bash
impacket-mssqlclient \
    "$DOMAIN/$USER@sql01.$DOMAIN"
```

Authentication may involve:

```text
SQL Authentication
Windows Authentication
NTLM
Kerberos
```

depending on configuration and command options.

---

# MSSQL Assessment Questions

Determine:

```text
Authentication Method
Database User
Database Roles
Server Roles
Accessible Databases
Linked Servers
Service Account
Domain Context
Impersonation Rights
Network Reachability
```

Do not enable command-execution functionality merely because the account can connect.

---

# RDP Authentication Check

## rdp_check

Help:

```bash
impacket-rdp_check -h
```

Use it for targeted authentication validation where RDP is in scope.

Successful authentication means:

```text
Credential accepted by RDP
```

It does not automatically mean:

```text
Local administrator
```

or:

```text
Unrestricted interactive access
```

---

# Requesting a TGT

## getTGT

Help:

```bash
impacket-getTGT -h
```

Concept:

```text
Credential
    |
    v
getTGT
    |
    v
KDC
    |
    v
TGT
    |
    v
ccache
```

Typical password-based structure:

```bash
impacket-getTGT \
    "$DOMAIN/$USER"
```

Enter the password when prompted.

After obtaining a ticket:

```bash
export KRB5CCNAME="$PWD/$USER.ccache"
```

Check:

```bash
klist
```

---

# TGT with NTLM Hash

Where explicitly authorised:

```bash
impacket-getTGT \
    "$DOMAIN/$USER" \
    -hashes ':<NT-HASH>'
```

Check your installed version's syntax first:

```bash
impacket-getTGT -h
```

---

# TGT with AES Key

Where authorised:

```bash
impacket-getTGT \
    "$DOMAIN/$USER" \
    -aesKey '<AES-KEY>'
```

Protect the resulting ticket and key material.

---

# Requesting a Service Ticket

## getST

Help:

```bash
impacket-getST -h
```

`getST` is relevant to:

```text
Service-Specific Kerberos Access
Constrained Delegation
S4U2Self
S4U2Proxy
RBCD
Impersonation Workflows
```

The exact command depends heavily on the delegation relationship.

Use the dedicated notes:

```text
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
```

---

# S4U Model

```text
Controlled Principal
       |
       v
Delegation Configuration
       |
       v
S4U2Self
       |
       v
S4U2Proxy
       |
       v
Service Ticket
       |
       v
Target Service
```

Do not run an impersonation workflow simply because `findDelegation` returned an entry.

Validate the relationship first.

---

# Kerberos Ticket Conversion

## ticketConverter

Help:

```bash
impacket-ticketConverter -h
```

Concept:

```text
kirbi
  |
  v
ticketConverter
  |
  v
ccache
```

or:

```text
ccache
  |
  v
ticketConverter
  |
  v
kirbi
```

Conversion changes the storage format.

It does not change:

```text
Identity
Privileges
Lifetime
Service
Cryptographic Validity
```

---

# Ticket Inspection

## describeTicket

Where present in your installed version:

```bash
impacket-describeTicket -h
```

Use ticket inspection to understand:

```text
Client Principal
Service Principal
Realm
Flags
Validity
Encryption Type
PAC-related Information
```

without immediately attempting to use the ticket.

---

# PAC Inspection

## getPac

Check:

```bash
impacket-getPac -h
```

PAC-related tooling is useful when investigating Kerberos authorisation information and advanced Kerberos behaviour.

Use it only when relevant to the assessment objective.

---

# Ticket Creation

## ticketer

Help:

```bash
impacket-ticketer -h
```

This is advanced Kerberos functionality associated with:

```text
Golden Tickets
Silver Tickets
Trust Tickets
Kerberos Persistence
```

!!! danger
    Ticket creation can materially alter the security context of an assessment and should only be used where explicitly authorised.

Use the dedicated Kerberos and persistence notes rather than treating `ticketer` as a routine enumeration tool.

---

# Password Changes

## changepasswd

Help:

```bash
impacket-changepasswd -h
```

Password modification is a state-changing operation.

Use it only where:

```text
The account is approved
The password change is approved
Impact is understood
Rollback is defined
```

For most assessments, password-change capability can be documented without actually changing a production user's password.

---

# AD ACLs

## dacledit

Check:

```bash
impacket-dacledit -h
```

This tool can inspect or modify Active Directory DACL information.

Prefer read-only inspection first.

Think:

```text
Principal
   |
   v
ACE
   |
   v
Object
   |
   v
Right
   |
   v
Security Impact
```

Examples of rights worth understanding include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
Extended Rights
Property-Specific Rights
```

Do not modify ACLs merely to prove that an ACE exists.

---

# Object Ownership

## owneredit

Check:

```bash
impacket-owneredit -h
```

Ownership can influence an identity's ability to modify an object's DACL.

Assess:

```text
Current Owner
Who Can Change Owner?
What Object?
What Security Boundary?
What Additional Rights Become Possible?
```

Prefer read-only validation unless modification is explicitly authorised.

---

# Resource-Based Constrained Delegation

## rbcd

Check:

```bash
impacket-rbcd -h
```

Current Impacket supports operations around:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Read-only assessment should come first.

Concept:

```text
Controlled Principal
        |
        v
RBCD Attribute
        |
        v
Target Computer
        |
        v
S4U
        |
        v
Target Service
```

See:

```text
active-directory/rbcd.md
```

---

# Machine Accounts

Some Impacket tooling can interact with computer accounts.

Before any state-changing machine-account operation, understand:

```text
MachineAccountQuota
Existing Computer Objects
Delegated Create/Delete Rights
Target OU
RBCD Relationship
Cleanup Requirements
```

See:

```text
active-directory/machine-account-quota.md
```

---

# Credential Access

## secretsdump

Help:

```bash
impacket-secretsdump -h
```

Potential credential sources include:

```text
SAM
LSA Secrets
Cached Domain Credentials
NTDS
Domain Replication
```

!!! danger
    Credential dumping is highly sensitive. Only perform it when credential-access testing is explicitly authorised.

---

# secretsdump Security Model

Do not think:

```text
Admin Credential
      =
Dump Everything
```

Use:

```text
Assessment Objective
       |
       v
Credential Access Required?
       |
    +--+--+
    |     |
   No    Yes
    |     |
    v     v
   Stop  Minimum
         Required
         Collection
```

---

# Local Secrets vs Domain Replication

These are different security boundaries.

```text
Remote Windows Host
       |
       +--> SAM
       +--> LSA Secrets
       +--> Cached Credentials
```

versus:

```text
Domain Controller
       |
       v
Directory Replication
       |
       v
Domain Credential Material
```

Domain replication access has substantially greater impact.

---

# DRSUAPI

`secretsdump` can use directory replication mechanisms when the identity has the necessary rights.

This should be treated as a high-impact capability.

The important finding may be:

```text
Unexpected Identity
       |
       v
Directory Replication Rights
       |
       v
Domain Credential Exposure
```

rather than the volume of credentials that can be collected.

---

# Targeted Replication Validation

Current `secretsdump` versions provide options for narrowing domain-controller collection.

Check:

```bash
impacket-secretsdump -h
```

Prefer targeted validation over full-domain extraction whenever the assessment objective can be proven with less sensitive data.

---

# Offline Secrets Assessment

`secretsdump` can also work with authorised offline registry/database material.

This can be preferable in a controlled lab or forensic assessment because it avoids interacting with a live production host.

Check:

```bash
impacket-secretsdump -h
```

for the exact offline-input options supported by the installed version.

---

# Credential Evidence Handling

Credential-related evidence may contain:

```text
NTLM Hashes
AES Keys
Passwords
Cached Credentials
Service Secrets
Machine Secrets
Kerberos Keys
```

Store it separately from normal screenshots and notes where possible.

Apply the engagement's data-retention requirements.

---

# Remote Administration

Common tools:

```text
psexec
smbexec
wmiexec
dcomexec
atexec
```

They use different Windows mechanisms.

---

# Remote Administration Comparison

| Tool | Primary Mechanism | Typical Dependencies | Operational Consideration |
|---|---|---|---|
| `psexec` | SMB + SCM | SMB, Service Control Manager | Creates/uses a service |
| `smbexec` | SMB + SCM | SMB, Service Control Manager | Service-based activity |
| `wmiexec` | WMI/DCOM | RPC, DCOM, WMI | WMI/DCOM telemetry |
| `dcomexec` | DCOM | RPC/DCOM | DCOM-specific activity |
| `atexec` | Task Scheduler | RPC/Task Scheduler | Scheduled-task activity |

The exact telemetry depends on Windows version, configuration, security products and tool version.

---

# Remote Administration Decision

```text
Need Remote Administration?
          |
          v
Is It Explicitly Authorised?
          |
       +--+--+
       |     |
      No    Yes
       |     |
       v     v
      Stop  Which
            Protocol?
              |
       +------+------+------+
       |      |      |      |
       v      v      v      v
      SCM    WMI    DCOM   TSCH
       |      |      |      |
       v      v      v      v
    psexec wmiexec dcomexec atexec
    smbexec
```

---

# psexec

Help:

```bash
impacket-psexec -h
```

This uses SMB and service-management functionality.

Consider it intrusive because service creation or service-control activity may occur.

---

# smbexec

Help:

```bash
impacket-smbexec -h
```

Also relies on SMB/service-management mechanisms.

Do not treat it as "stealthy" simply because it behaves differently from `psexec`.

---

# wmiexec

Help:

```bash
impacket-wmiexec -h
```

Typical dependencies include:

```text
RPC Endpoint Mapper
DCOM
WMI
Dynamic RPC Ports
Appropriate Permissions
```

---

# dcomexec

Help:

```bash
impacket-dcomexec -h
```

Use only when DCOM remote administration is explicitly within scope.

---

# atexec

Help:

```bash
impacket-atexec -h
```

Uses Task Scheduler interfaces.

Scheduled-task creation is state-changing and can generate security telemetry.

---

# Authentication Before Execution

Prefer:

```text
Credential
    |
    v
Authentication Test
    |
    v
Privilege Determination
    |
    v
Remote Management Exposure
    |
    v
Authorisation Check
    |
    v
Controlled Execution
```

Do not use remote execution merely to establish whether a password is valid.

---

# NTLM Relay

## ntlmrelayx

Help:

```bash
impacket-ntlmrelayx -h
```

Concept:

```text
Authentication Source
        |
        v
      Relay
        |
        v
 Target Protocol
        |
        v
 Target Identity Context
        |
        v
 Authorised Action
```

---

# Capture vs Relay

```text
Capture

Client
  |
  v
Assessment Host
  |
  v
Authentication Material
```

versus:

```text
Relay

Client
  |
  v
Assessment Host
  |
  v
Target Service
```

Therefore:

```text
Capture != Relay
```

---

# Relay Preconditions

Assess:

```text
Authentication Source
Target Protocol
SMB Signing
LDAP Signing
LDAP Channel Binding
Extended Protection
Target Authentication
Identity Privileges
Network Reachability
```

Do not report:

```text
SMB signing not required
```

as:

```text
NTLM relay confirmed
```

without validating the complete path.

---

# Relay Safety

Relay testing can cause real authentication and state changes.

Before testing:

```text
[ ] Relay explicitly in scope
[ ] Source understood
[ ] Target approved
[ ] Protocol approved
[ ] Expected identity understood
[ ] Security controls reviewed
[ ] State-changing action understood
[ ] Rollback defined where relevant
```

---

# NetExec + Impacket

A useful model:

```text
Nmap
  |
  v
NetExec
  |
  v
Broad Network Enumeration
  |
  v
Interesting Host / Identity
  |
  v
Impacket
  |
  v
Targeted Protocol Investigation
```

NetExec answers:

```text
Where should I look?
```

Impacket often answers:

```text
What exactly can this identity do through this protocol?
```

---

# BloodHound + Impacket

```text
BloodHound
    |
    v
Potential Relationship
    |
    v
Understand Edge
    |
    v
Check Preconditions
    |
    v
Impacket
    |
    v
Controlled Validation
```

BloodHound paths are hypotheses until their prerequisites are understood.

---

# Protocol and Port Reference

| Function | Common Ports |
|---|---|
| SMB | TCP 445 |
| RPC Endpoint Mapper | TCP 135 |
| Dynamic RPC | High TCP ports |
| LDAP | TCP 389 |
| LDAPS | TCP 636 |
| Kerberos | TCP/UDP 88 |
| Global Catalog | TCP 3268 |
| Global Catalog TLS | TCP 3269 |
| MSSQL | TCP 1433 |
| SQL Browser | UDP 1434 |
| RDP | TCP/UDP 3389 |

Actual environments may use non-default ports or firewall restrictions.

---

# Tool Connectivity Model

## SMB Tools

Commonly require:

```text
TCP 445
```

Examples:

```text
smbclient
smbserver
psexec
smbexec
secretsdump - some workflows
```

---

# RPC Tools

May require:

```text
TCP 135
Dynamic RPC Ports
TCP 445 depending on transport
```

Examples:

```text
rpcdump
rpcmap
wmiexec
dcomexec
atexec
```

---

# LDAP Tools

Commonly require:

```text
389/tcp
```

or:

```text
636/tcp
```

depending on LDAP/LDAPS.

Examples include directory-enumeration and AD-object management tools.

---

# Kerberos Tools

Commonly require:

```text
88/tcp
88/udp
```

plus:

```text
DNS
Correct Time
Correct Hostnames
```

---

# MSSQL

Usually:

```text
1433/tcp
```

but named instances can use other ports.

Do not assume every SQL Server listens on 1433.

---

# Troubleshooting - STATUS_LOGON_FAILURE

Usually investigate:

```text
Username
Password
Domain
Local vs Domain Account
Authentication Method
Account State
```

Do not repeatedly retry a credential without understanding lockout policy.

---

# Troubleshooting - STATUS_ACCESS_DENIED

This often means:

```text
Authentication succeeded
        |
        v
Requested operation not authorised
```

Distinguish:

```text
Authentication
```

from:

```text
Authorisation
```

---

# Troubleshooting - KDC_ERR_PREAUTH_FAILED

Investigate:

```text
Credential
AES Key
NT Hash
Account
Realm
Encryption Type
```

Do not assume the KDC itself is unavailable.

---

# Troubleshooting - KDC_ERR_S_PRINCIPAL_UNKNOWN

Investigate:

```text
SPN
Hostname
FQDN
Service Name
DNS
Realm
```

Kerberos is service-principal oriented.

---

# Troubleshooting - KRB_AP_ERR_SKEW

Check:

```bash
date
```

Compare against the domain environment.

This error commonly indicates clock skew.

---

# Troubleshooting - Kerberos Uses IP

Prefer:

```text
server01.example.local
```

over:

```text
10.10.20.25
```

for Kerberos-oriented operations where possible.

SPNs are normally hostname/service based.

---

# Troubleshooting - SMB Works, WMI Fails

Think:

```text
SMB Authentication
        |
        v
Credential Valid
```

but WMI additionally needs:

```text
RPC
DCOM
WMI Namespace Access
Firewall
Dynamic RPC
Appropriate Permissions
```

Therefore:

```text
SMB success != WMI success
```

---

# Troubleshooting - SMB Works, psexec Fails

Investigate:

```text
Administrative Rights
Service Control Manager Access
ADMIN$ Access
SMB Configuration
UAC Remote Restrictions
Endpoint Security
```

---

# Troubleshooting - DNS

```bash
dig "$DC"
```

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

---

# Troubleshooting - Ticket Cache

```bash
echo "$KRB5CCNAME"
```

```bash
klist
```

Check:

```text
Principal
Realm
Service
Start Time
Expiry
Renewal
```

---

# Authentication != Authorisation

Always remember:

```text
SMB Authentication
        !=
Local Administrator

Local Administrator
        !=
Domain Administrator

SMB Authentication
        !=
WMI Access

SMB Authentication
        !=
SCM Access

SMB Authentication
        !=
Remote Registry Access

LDAP Authentication
        !=
Write Access

Kerberos Ticket
        !=
Access to Every Service
```

---

# Domain vs Local Accounts

Always distinguish:

```text
EXAMPLE\alice
```

from:

```text
FILE01\alice
```

Same username does not mean same security principal.

---

# Credential Type Model

```text
Password
   |
NTLM Hash
   |
AES Key
   |
Kerberos Ticket
   |
Certificate
```

All can represent authentication capability.

Protect them accordingly.

---

# Evidence Directory

Create:

```bash
mkdir -p evidence/impacket/{ldap,kerberos,smb,rpc,mssql,delegation,credentials,remote-access,relay}
```

Result:

```text
evidence/
└── impacket/
    ├── ldap/
    ├── kerberos/
    ├── smb/
    ├── rpc/
    ├── mssql/
    ├── delegation/
    ├── credentials/
    ├── remote-access/
    └── relay/
```

---

# Save Output

Example:

```bash
impacket-GetADUsers \
    "$DOMAIN/$USER" \
    -dc-ip "$DC_IP" \
    -all |
    tee evidence/impacket/ldap/users.txt
```

Avoid putting credentials directly in screenshots or evidence filenames.

---

# Evidence Record

For an important result record:

```text
Timestamp:
Source:
Target:
Target IP:
Domain:
Identity:
Authentication Type:
Protocol:
Tool:
Operation:
Observed Result:
Privileges Required:
State Changed:
Security Impact:
```

---

# Timestamp

```bash
date -Is
```

This helps correlate testing with:

```text
Windows Event Logs
EDR
SIEM
Firewall Logs
Domain Controller Logs
SOC Alerts
```

---

# New Credential Workflow

```text
NEW CREDENTIAL
      |
      v
Password / Hash / Ticket / Key?
      |
      v
Domain or Local?
      |
      v
Validate Carefully
      |
      +--> SMB
      +--> LDAP
      +--> Kerberos
      +--> MSSQL
      |
      v
Enumerate Identity
      |
      v
Enumerate SPNs
      |
      v
Enumerate Delegation
      |
      v
Check Shares
      |
      v
Update BloodHound
      |
      v
Map Administrative Access
```

---

# New Host Workflow

```text
NEW HOST
   |
   v
Resolve Hostname
   |
   v
SMB?
   |
   +--> Shares
   +--> Signing
   |
   v
RPC?
   |
   +--> WMI
   +--> DCOM
   +--> SCM
   |
   v
MSSQL?
   |
   v
Credentials Valid?
   |
   v
Administrative?
   |
   v
New Relationships?
```

---

# New Domain Workflow

```text
NEW DOMAIN
    |
    v
DNS
    |
    v
Find DCs
    |
    v
Understand Trust
    |
    v
Users
    |
    v
Computers
    |
    v
SPNs
    |
    v
Delegation
    |
    v
BloodHound
    |
    v
Cross-Domain Relationships
```

---

# Unauthenticated Internal Workflow

From an internal network with no domain credentials:

```text
Network Position
      |
      v
Nmap / NetExec
      |
      v
Identify Windows Hosts
      |
      v
Identify Domain
      |
      v
Identify DC
      |
      v
DNS
      |
      v
SMB / RPC Exposure
      |
      v
Determine Whether Anonymous
Enumeration Is Available
      |
      v
Obtain Approved Credential
```

Impacket is most useful once a specific protocol, identity or target relationship has been identified.

---

# Authenticated Domain User Workflow

```text
Domain User
    |
    v
GetADUsers
    |
    v
GetADComputers
    |
    v
GetUserSPNs
    |
    v
findDelegation
    |
    v
LAPS / GPP Review
where authorised
    |
    v
Shares
    |
    v
BloodHound
    |
    v
Candidate Paths
    |
    v
Focused Impacket Validation
```

---

# Local Administrator Workflow

```text
Local Administrator
       |
       v
Which Host?
       |
       v
Credential Reused?
       |
       v
Remote Management Available?
       |
       v
Expected?
       |
       v
Controlled Validation
```

Do not automatically perform credential dumping or remote execution.

---

# Domain Privileged Identity Workflow

Highly privileged credentials should be used sparingly.

```text
Privileged Identity
       |
       v
What Must Be Proven?
       |
       v
Can a Lower Privileged
Account Prove It?
       |
   +---+---+
   |       |
  Yes      No
   |       |
   v       v
Use Low   Targeted
Privilege Validation
```

Avoid unnecessarily authenticating Domain Admin-equivalent identities to workstations.

---

# What Do I Have?

## I Have a Username

Consider:

```text
GetADUsers
GetNPUsers
lookupsid
```

depending on authentication availability and scope.

---

# I Have a Domain User

Start with:

```text
GetADUsers
GetADComputers
GetUserSPNs
findDelegation
smbclient
BloodHound
```

Then investigate only the relationships that matter.

---

# I Have an NTLM Hash

Ask:

```text
Which account?
Local or domain?
Which hosts?
Is hash authentication permitted?
Is Kerberos preferable?
```

Do not spray the hash across the entire environment by default.

---

# I Have a Kerberos Ticket

Check:

```bash
klist
```

Determine:

```text
TGT or TGS?
Which principal?
Which service?
Which realm?
Expiry?
```

Then choose a tool that supports:

```text
-k -no-pass
```

where appropriate.

---

# I Have Local Admin

Ask:

```text
What needs to be validated?
```

Possible protocol areas:

```text
SMB
SCM
WMI
DCOM
Task Scheduler
Remote Registry
```

Credential dumping should remain a separate explicit decision.

---

# I Have an Interesting BloodHound Edge

Use:

```text
BloodHound Edge
      |
      v
Read Edge Documentation
      |
      v
Understand Required Right
      |
      v
Check Identity
      |
      v
Check Target
      |
      v
Choose Relevant Impacket Tool
      |
      v
Read-Only Validation First
```

---

# I Have WriteDACL

Investigate:

```text
Which object?
Which identity?
Inherited?
Explicit?
Which rights can be delegated?
Is modification authorised?
```

`dacledit` may be relevant for inspection.

Do not alter a production ACL simply to prove the permission exists.

---

# I Have WriteOwner

Investigate ownership and DACL implications.

`owneredit` may be relevant.

Again, read-only confirmation is preferable where sufficient.

---

# I Have RBCD-Related Rights

Investigate:

```text
Controlled Principal
Target Computer
MachineAccountQuota
Existing Computer Accounts
msDS-AllowedToActOnBehalfOfOtherIdentity
S4U Prerequisites
```

Use the dedicated RBCD note.

---

# I Have MSSQL Credentials

Use:

```text
mssqlclient
```

to determine:

```text
Authentication
Database Access
Roles
Linked Servers
Server Context
```

Do not immediately enable OS-level command execution.

---

# I Have a Service Account

Investigate:

```text
SPNs
Privileges
Delegation
Password Age
Group Membership
Logon Rights
Where Account Is Used
```

Use BloodHound and directory enumeration before attempting further operations.

---

# Fast Enumeration Workflow

Assume:

```text
Domain: example.local
DC: dc01.example.local
DC IP: 10.10.20.10
User: alice
```

Users:

```bash
impacket-GetADUsers \
    example.local/alice \
    -dc-ip 10.10.20.10 \
    -all
```

Computers:

```bash
impacket-GetADComputers \
    example.local/alice \
    -dc-ip 10.10.20.10
```

SPNs:

```bash
impacket-GetUserSPNs \
    example.local/alice \
    -dc-ip 10.10.20.10
```

Delegation:

```bash
impacket-findDelegation \
    example.local/alice \
    -dc-ip 10.10.20.10
```

SIDs:

```bash
impacket-lookupsid \
    example.local/alice@dc01.example.local
```

Then:

```text
Review
  |
  v
BloodHound
  |
  v
Candidate Relationships
  |
  v
Focused Validation
```

---

# Operational Noise

Do not use simplistic labels such as:

```text
Tool X = stealthy
Tool Y = noisy
```

Detection depends on:

```text
Windows Version
Security Configuration
EDR
SIEM
Audit Policy
Network Monitoring
Identity
Command
Target
Tool Version
```

Instead document the mechanism.

---

# Common Telemetry Areas

Depending on the operation, defenders may observe:

```text
Authentication Events
Kerberos Events
SMB Connections
Service Creation
Scheduled Task Creation
WMI Activity
DCOM Activity
LDAP Queries
Directory Changes
Directory Replication
Remote Registry
Process Creation
Network Connections
```

---

# Read Before Write

For tools that support modification, prefer:

```text
Read
 |
 v
Understand
 |
 v
Document
 |
 v
Determine Whether Modification
Is Necessary
 |
 +---+---+
 |       |
No      Yes
 |       |
 v       v
Stop   Obtain
       Approval
         |
         v
      Minimal
      Change
         |
         v
      Validate
         |
         v
      Restore
```

---

# State-Changing Operations

Treat these especially carefully:

```text
Password Changes
ACL Changes
Owner Changes
RBCD Changes
Machine Account Creation
Service Creation
Scheduled Tasks
Ticket Creation
Relay Actions
Remote Execution
```

Document rollback before making the change.

---

# Cleanup Checklist

After state-changing tests:

```text
[ ] Temporary services removed
[ ] Scheduled tasks removed
[ ] Temporary accounts removed
[ ] ACL changes restored
[ ] Ownership restored
[ ] RBCD changes restored
[ ] Temporary files removed
[ ] SMB server stopped
[ ] Sensitive ticket files protected/deleted
[ ] Credential dumps handled per retention policy
[ ] Evidence retained securely
```

---

# Do Not Overreport

Do not automatically report:

```text
SMB Is Open
RPC Is Open
LDAP Is Open
An SPN Exists
Delegation Exists
A User Can Authenticate
A Computer Object Exists
LAPS Is Enabled
MSSQL Is Reachable
RDP Authentication Works
A Kerberos Ticket Can Be Requested
Impacket Can Connect
```

Instead determine:

```text
Configuration
     +
Identity
     +
Permission
     +
Reachability
     +
Security Boundary
     +
Impact
     =
Finding
```

---

# Examples of Better Interpretation

## SPN

Weak:

```text
Kerberoasting possible because an SPN exists.
```

Better:

```text
A service account has an SPN. Assess the account's password
strength, age and privileges before determining whether the
configuration creates meaningful offline password-guessing risk.
```

---

## Delegation

Weak:

```text
Constrained delegation found.
```

Better:

```text
The account is configured for constrained delegation to the
identified service. Determine who controls the account and whether
the relationship permits an unintended privilege boundary to be crossed.
```

---

## SMB Authentication

Weak:

```text
User can access SMB.
```

Better:

```text
The domain user successfully authenticated to SMB. Review accessible
shares and permissions to determine whether the access exceeds the
user's intended role.
```

---

## LAPS

Weak:

```text
LAPS password accessible.
```

Better:

```text
The tested identity can read the managed local administrator
credential for the specified computer. Determine whether this
permission is expected for the identity and whether it creates an
unintended administrative path.
```

---

## Replication Rights

Weak:

```text
DCSync possible.
```

Better:

```text
The identity possesses directory replication rights capable of
accessing domain credential material. This represents a domain-level
security boundary and should be validated using the minimum evidence
necessary.
```

---

# What Tool Do I Need?

```text
                         IMPACKET
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
   DIRECTORY             KERBEROS              SMB
       |                    |                    |
       +--> Users            +--> TGT             +--> Client
       |    GetADUsers       |    getTGT           |    smbclient
       |                    |                    |
       +--> Computers        +--> Service          +--> Server
       |    GetADComputers   |    Ticket           |    smbserver
       |                    |    getST             |
       +--> AS-REP           |                    |
       |    GetNPUsers       +--> Convert          |
       |                    |    ticketConverter  |
       +--> SPNs             |                    |
       |    GetUserSPNs      +--> Inspect          |
       |                    |    describeTicket   |
       +--> Delegation       |                    |
       |    findDelegation   +--> PAC              |
       |                    |    getPac            |
       +--> LAPS                                  |
       |    GetLAPSPassword                       |
       |                                         |
       +--> GPP                                   |
            Get-GPPPassword                       |
                                                  |
       +--------------------+---------------------+
                            |
                            v
                     REMOTE WINDOWS
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
        Service            WMI                DCOM
     psexec/smbexec      wmiexec            dcomexec
          |
          v
     Task Scheduler
        atexec


                     ACTIVE DIRECTORY
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
         ACL              Owner               RBCD
       dacledit          owneredit             rbcd


                        DATABASE
                            |
                            v
                       MSSQL / TDS
                            |
                     +------+------+
                     |             |
                     v             v
                Discovery       Client
               mssqlinstance  mssqlclient


                    CREDENTIAL ACCESS
                            |
                            v
                       secretsdump


                          RELAY
                            |
                            v
                       ntlmrelayx
```

---

# One-Minute Reference

```text
Users
    -> GetADUsers

Computers
    -> GetADComputers

AS-REP
    -> GetNPUsers

SPNs
    -> GetUserSPNs

SIDs
    -> lookupsid

Delegation
    -> findDelegation

LAPS
    -> GetLAPSPassword

GPP
    -> Get-GPPPassword

RPC
    -> rpcdump / rpcmap

WMI query
    -> wmiquery

SMB files
    -> smbclient

SMB server
    -> smbserver

MSSQL
    -> mssqlinstance / mssqlclient

RDP auth
    -> rdp_check

TGT
    -> getTGT

Service ticket
    -> getST

Ticket conversion
    -> ticketConverter

Ticket inspection
    -> describeTicket

PAC
    -> getPac

ACL
    -> dacledit

Owner
    -> owneredit

RBCD
    -> rbcd

Credential access
    -> secretsdump

Service administration
    -> psexec / smbexec

WMI administration
    -> wmiexec

DCOM
    -> dcomexec

Task Scheduler
    -> atexec

NTLM relay
    -> ntlmrelayx
```

---

# Assessment Checklist

## Environment

```text
[ ] Impacket version
[ ] Domain
[ ] DC hostname
[ ] DC IP
[ ] DNS
[ ] Time
[ ] Routes
[ ] Required ports
```

## Credentials

```text
[ ] Username
[ ] Domain/local context
[ ] Password or approved authentication material
[ ] Hash format understood
[ ] AES key protected
[ ] Kerberos cache checked
```

## Enumeration

```text
[ ] Users
[ ] Computers
[ ] SPNs
[ ] AS-REP configuration
[ ] SIDs where relevant
[ ] Delegation
[ ] LAPS permissions
[ ] Legacy GPP exposure
[ ] SMB shares
[ ] RPC where relevant
[ ] MSSQL where relevant
```

## Kerberos

```text
[ ] DNS correct
[ ] FQDN correct
[ ] Time correct
[ ] KDC reachable
[ ] Ticket type understood
[ ] KRB5CCNAME correct
[ ] SPN correct
[ ] Realm correct
```

## Active Directory Rights

```text
[ ] ACLs reviewed
[ ] Ownership reviewed
[ ] RBCD relationships reviewed
[ ] Machine account rights reviewed
[ ] Replication rights reviewed
[ ] BloodHound relationships correlated
```

## Remote Administration

```text
[ ] Administrative rights confirmed
[ ] Remote execution authorised
[ ] Protocol chosen deliberately
[ ] Operational impact understood
[ ] State changes documented
[ ] Cleanup defined
```

## Credential Access

```text
[ ] Explicitly authorised
[ ] Target approved
[ ] Sensitive-data handling defined
[ ] Minimum evidence collected
[ ] Storage protected
[ ] Retention policy followed
```

## Relay

```text
[ ] Explicitly authorised
[ ] Source understood
[ ] Target understood
[ ] Signing/protection reviewed
[ ] Identity privilege understood
[ ] State-changing action understood
[ ] Impact validated
```

---

# Core Mental Model

```text
                       IMPACKET
                          |
                          v
                       CONTEXT
                          |
             +------------+------------+
             |                         |
             v                         v
          IDENTITY                   TARGET
             |                         |
             v                         v
       AUTHENTICATION               PROTOCOL
             |                         |
    +--------+--------+       +--------+--------+
    |        |        |       |        |        |
    v        v        v       v        v        v
 Password   Hash   Kerberos   SMB     LDAP     RPC
                      |                  |
                      v                  |
                    Ticket               |
                      |                  |
             +--------+--------+         |
             |                 |         |
             v                 v         |
        ENUMERATION          ACCESS <----+
             |                 |
             v                 v
       Relationships       Privilege
             |                 |
             +--------+--------+
                      |
                      v
                   ANALYSE
                      |
                      v
              READ-ONLY VALIDATION
                      |
                      v
             STATE CHANGE NEEDED?
                      |
                 +----+----+
                 |         |
                No        Yes
                 |         |
                 v         v
              Evidence   Approval
                           |
                           v
                        Minimal
                         Change
                           |
                           v
                        Cleanup
                           |
                           v
                        Evidence
```

---

# Rules to Remember

```text
Tool output != vulnerability

SPN != weak password

Delegation != exploitable path

SMB signing not required != successful relay

Authentication != administration

Local administrator != Domain Admin

Ticket != access to every service

Credential found != permission to dump more credentials

Administrative access != permission to execute remotely

Write permission != permission to modify production

BloodHound edge != automatically exploitable path

Successful Impacket command != security finding
```

---

# Related Cheatsheets

[Active Directory Cheatsheet](active-directory.md)

[NetExec Cheatsheet](netexec.md)

[BloodHound Cheatsheet](bloodhound.md)

[Networking Cheatsheet](networking.md)

[Windows Cheatsheet](windows.md)

[PowerShell Cheatsheet](powershell.md)

---

# Detailed Notes

Relevant detailed notes include:

```text
active-directory/impacket.md
active-directory/enumeration.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/asrep-roasting.md
active-directory/kerberoasting.md
active-directory/ntlm-relay.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
active-directory/laps.md
active-directory/gpp-passwords.md
active-directory/machine-account-quota.md
active-directory/lateral-movement.md
active-directory/pivoting.md
active-directory/credential-access.md
active-directory/ntds.md
```

---

# References

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Primary upstream project.

---

## Impacket Examples

[Impacket Examples](https://github.com/fortra/impacket/tree/master/examples){ target="_blank" rel="noopener noreferrer" }

The current example scripts are one of the best references for version-specific options.

---

## Impacket Releases

[Impacket Releases](https://github.com/fortra/impacket/releases){ target="_blank" rel="noopener noreferrer" }

Check stable releases and release notes before relying on development-version functionality.

---

## GetADUsers

[GetADUsers](https://github.com/fortra/impacket/blob/master/examples/GetADUsers.py){ target="_blank" rel="noopener noreferrer" }

---

## GetADComputers

[GetADComputers](https://github.com/fortra/impacket/blob/master/examples/GetADComputers.py){ target="_blank" rel="noopener noreferrer" }

---

## GetNPUsers

[GetNPUsers](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py){ target="_blank" rel="noopener noreferrer" }

---

## GetUserSPNs

[GetUserSPNs](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py){ target="_blank" rel="noopener noreferrer" }

---

## findDelegation

[findDelegation](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py){ target="_blank" rel="noopener noreferrer" }

---

## lookupsid

[lookupsid](https://github.com/fortra/impacket/blob/master/examples/lookupsid.py){ target="_blank" rel="noopener noreferrer" }

---

## GetLAPSPassword

[GetLAPSPassword](https://github.com/fortra/impacket/blob/master/examples/GetLAPSPassword.py){ target="_blank" rel="noopener noreferrer" }

---

## Get-GPPPassword

[Get-GPPPassword](https://github.com/fortra/impacket/blob/master/examples/Get-GPPPassword.py){ target="_blank" rel="noopener noreferrer" }

---

## getTGT

[getTGT](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

---

## getST

[getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

---

## smbclient

[smbclient](https://github.com/fortra/impacket/blob/master/examples/smbclient.py){ target="_blank" rel="noopener noreferrer" }

---

## smbserver

[smbserver](https://github.com/fortra/impacket/blob/master/examples/smbserver.py){ target="_blank" rel="noopener noreferrer" }

---

## rpcdump

[rpcdump](https://github.com/fortra/impacket/blob/master/examples/rpcdump.py){ target="_blank" rel="noopener noreferrer" }

---

## rpcmap

[rpcmap](https://github.com/fortra/impacket/blob/master/examples/rpcmap.py){ target="_blank" rel="noopener noreferrer" }

---

## wmiquery

[wmiquery](https://github.com/fortra/impacket/blob/master/examples/wmiquery.py){ target="_blank" rel="noopener noreferrer" }

---

## mssqlclient

[mssqlclient](https://github.com/fortra/impacket/blob/master/examples/mssqlclient.py){ target="_blank" rel="noopener noreferrer" }

---

## secretsdump

[secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py){ target="_blank" rel="noopener noreferrer" }

---

## psexec

[psexec](https://github.com/fortra/impacket/blob/master/examples/psexec.py){ target="_blank" rel="noopener noreferrer" }

---

## wmiexec

[wmiexec](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py){ target="_blank" rel="noopener noreferrer" }

---

## smbexec

[smbexec](https://github.com/fortra/impacket/blob/master/examples/smbexec.py){ target="_blank" rel="noopener noreferrer" }

---

## dcomexec

[dcomexec](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py){ target="_blank" rel="noopener noreferrer" }

---

## atexec

[atexec](https://github.com/fortra/impacket/blob/master/examples/atexec.py){ target="_blank" rel="noopener noreferrer" }

---

## dacledit

[dacledit](https://github.com/fortra/impacket/blob/master/examples/dacledit.py){ target="_blank" rel="noopener noreferrer" }

---

## owneredit

[owneredit](https://github.com/fortra/impacket/blob/master/examples/owneredit.py){ target="_blank" rel="noopener noreferrer" }

---

## rbcd

[rbcd](https://github.com/fortra/impacket/blob/master/examples/rbcd.py){ target="_blank" rel="noopener noreferrer" }

---

## changepasswd

[changepasswd](https://github.com/fortra/impacket/blob/master/examples/changepasswd.py){ target="_blank" rel="noopener noreferrer" }

---

## ntlmrelayx

[ntlmrelayx](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py){ target="_blank" rel="noopener noreferrer" }

---

## ticketer

[ticketer](https://github.com/fortra/impacket/blob/master/examples/ticketer.py){ target="_blank" rel="noopener noreferrer" }

---

## ticketConverter

[ticketConverter](https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py){ target="_blank" rel="noopener noreferrer" }

---

## Exploit Notes - Active Directory

[Exploit Notes - Active Directory](https://exploitnotes.org/exploit/windows/active-directory/){ target="_blank" rel="noopener noreferrer" }

Additional Active Directory enumeration and assessment reference.

---

## InternalAllTheThings - Active Directory

[InternalAllTheThings - Active Directory](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/){ target="_blank" rel="noopener noreferrer" }

Additional Active Directory technique reference.

---

## HackTricks - Active Directory

[HackTricks - Active Directory Methodology](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html){ target="_blank" rel="noopener noreferrer" }

Additional methodology and testing reference.

---

## Microsoft Kerberos Documentation

[Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

Useful when interpreting Kerberos behaviour rather than relying solely on tool output.

---

# Final Impacket Model

Do not use Impacket as:

```text
Credential
    |
    v
Run Every Tool
    |
    v
Dump Everything
    |
    v
Execute Everywhere
```

Use:

```text
Understand Scope
      |
      v
Understand Network
      |
      v
Understand Identity
      |
      v
Identify Protocol
      |
      v
Choose Specific Tool
      |
      v
Read-Only Enumeration
      |
      v
Understand Relationship
      |
      v
Manual Validation
      |
      v
Need State Change?
      |
   +--+--+
   |     |
  No    Yes
   |     |
   v     v
Evidence Approval
          |
          v
       Minimal
       Change
          |
          v
       Cleanup
          |
          v
       Evidence
```

The goal is not:

```text
How many Impacket commands can I run?
```

The goal is:

```text
Which protocol, identity, permission or Active Directory
relationship explains the observed security boundary?
```

Impacket is most valuable when it turns:

```text
Potential Relationship
```

into:

```text
Protocol-Level Understanding
        +
Permission Validation
        +
Minimal Evidence
        =
Defensible Security Finding
```
