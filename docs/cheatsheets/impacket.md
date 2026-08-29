# Impacket Cheatsheet

Quick-reference commands and workflows for using Impacket during authorised Windows and Active Directory security assessments.

For explanations of the protocols, authentication models, prerequisites, interpretation, detection, and reporting, see:

[Impacket](../active-directory/impacket.md)

---

# Quick Tool Map

| Goal | Impacket Tool |
|---|---|
| Enumerate AD users | `GetADUsers` |
| Find AS-REP candidates | `GetNPUsers` |
| Enumerate SPNs | `GetUserSPNs` |
| Enumerate SIDs / RIDs | `lookupsid` |
| Enumerate delegation | `findDelegation` |
| Enumerate RPC endpoints | `rpcdump` |
| Enumerate SAMR information | `samrdump` |
| Access SMB shares | `smbclient` |
| Host an SMB share | `smbserver` |
| Request a TGT | `getTGT` |
| Request a service ticket | `getST` |
| Convert Kerberos tickets | `ticketConverter` |
| Create Kerberos tickets | `ticketer` |
| Access Windows secrets | `secretsdump` |
| Service-based remote administration | `psexec` |
| WMI remote administration | `wmiexec` |
| SMB/service remote administration | `smbexec` |
| DCOM remote administration | `dcomexec` |
| Task Scheduler remote administration | `atexec` |
| NTLM relay testing | `ntlmrelayx` |

---

# Command Naming

Depending on how Impacket was installed, commands may appear as:

```text
impacket-GetADUsers
impacket-GetNPUsers
impacket-GetUserSPNs
impacket-lookupsid
impacket-findDelegation
```

or when running directly from the source repository:

```text
GetADUsers.py
GetNPUsers.py
GetUserSPNs.py
lookupsid.py
findDelegation.py
```

This cheatsheet primarily uses the packaged form:

```text
impacket-<tool>
```

Check what is installed:

```bash
compgen -c | grep '^impacket-' | sort -u
```

---

# Version

Check the installed version:

```bash
python3 -c "from importlib.metadata import version; print(version('impacket'))"
```

List pipx packages:

```bash
pipx list
```

Always check tool-specific help:

```bash
impacket-GetADUsers -h
```

---

# Installation

## pipx

```bash
sudo apt update
sudo apt install pipx
```

```bash
pipx ensurepath
```

```bash
python3 -m pipx install impacket
```

---

# Kali Linux

```bash
sudo apt update
sudo apt install python3-impacket
```

Check:

```bash
which impacket-GetADUsers
```

---

# Environment Variables

A useful assessment setup:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DC_IP="10.10.20.10"
export USER="alice"
```

Check:

```bash
echo "$DOMAIN"
echo "$DC"
echo "$DC_IP"
echo "$USER"
```

---

# DNS

Resolve the Domain Controller:

```bash
dig "$DC"
```

LDAP SRV:

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

Kerberos SRV:

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

Check resolver configuration:

```bash
cat /etc/resolv.conf
```

---

# Time

Kerberos is time sensitive.

```bash
date
```

If Kerberos fails unexpectedly, check clock synchronisation before assuming the credential or ticket is invalid.

---

# Authentication Quick Reference

Impacket commonly supports several authentication models:

```text
Password
NTLM hash
Kerberos
AES key
Kerberos ccache
```

---

# Password Authentication

Common target format:

```text
domain/user:password@target
```

Example:

```bash
impacket-smbclient \
    example.local/alice:'Password'@file01.example.local
```

!!! warning
    Plaintext passwords supplied on the command line may appear in shell history, process listings, terminal logs, screenshots, or assessment evidence.

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
    example.local/alice@file01.example.local \
    -hashes :<NT-HASH>
```

---

# Kerberos Authentication

Common Kerberos option:

```text
-k
```

Many tools also support:

```text
-no-pass
```

when authentication material is available through another mechanism such as the Kerberos credential cache.

Always check:

```bash
<tool> -h
```

---

# Kerberos Credential Cache

Set the credential cache:

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

---

# Kerberos Checklist

Before troubleshooting Impacket:

```text
[ ] Domain correct
[ ] Username correct
[ ] DC correct
[ ] DC FQDN resolves
[ ] Internal DNS works
[ ] KDC reachable
[ ] Time synchronised
[ ] Correct ticket loaded
[ ] Correct SPN used
```

---

# AES Key Authentication

Where supported:

```text
-aesKey <AES_KEY>
```

Check the individual tool:

```bash
<tool> -h
```

before assuming AES-key support or syntax.

---

# AD User Enumeration

## GetADUsers

Enumerate domain users:

```bash
impacket-GetADUsers \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10 \
    -all
```

Using variables:

```bash
impacket-GetADUsers \
    "$DOMAIN/$USER":'Password' \
    -dc-ip "$DC_IP" \
    -all
```

---

# GetADUsers with NTLM Hash

```bash
impacket-GetADUsers \
    example.local/alice \
    -hashes :<NT-HASH> \
    -dc-ip 10.10.20.10 \
    -all
```

---

# GetADUsers with Kerberos

```bash
impacket-GetADUsers \
    example.local/alice \
    -k \
    -no-pass \
    -dc-host dc01.example.local \
    -all
```

Use the correct Kerberos context first:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

---

# User Enumeration Workflow

```text
GetADUsers
     |
     v
Users
     |
     +--> Service accounts
     +--> Privileged accounts
     +--> Stale accounts
     +--> Password age
     +--> Interesting naming
     |
     v
Further Enumeration
```

---

# AS-REP Candidates

## GetNPUsers

Help:

```bash
impacket-GetNPUsers -h
```

Use it to investigate accounts configured without Kerberos pre-authentication.

Workflow:

```text
User Enumeration
       |
       v
Pre-Authentication Disabled?
       |
   +---+---+
   |       |
  No      Yes
   |       |
   |       v
   |   Candidate
   |       |
   |       v
   |   Controlled Validation
   |
   v
Continue
```

See the dedicated AS-REP Roasting note before moving from enumeration to ticket/hash collection.

---

# SPN Enumeration

## GetUserSPNs

Enumerate accounts with SPNs:

```bash
impacket-GetUserSPNs \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

Using variables:

```bash
impacket-GetUserSPNs \
    "$DOMAIN/$USER":'Password' \
    -dc-ip "$DC_IP"
```

---

# GetUserSPNs with NTLM Hash

General structure:

```bash
impacket-GetUserSPNs \
    example.local/alice \
    -hashes :<NT-HASH> \
    -dc-ip 10.10.20.10
```

---

# Cross-Domain SPN Enumeration

Current Impacket versions provide:

```text
-target-domain
```

Check:

```bash
impacket-GetUserSPNs -h
```

before using it.

---

# SPN Workflow

```text
GetUserSPNs
     |
     v
SPN Accounts
     |
     v
Service Account?
     |
     v
Privilege?
     |
     v
Password Age?
     |
     v
Kerberoasting Candidate?
```

Do not assume:

```text
SPN = vulnerability
```

---

# SID Enumeration

## lookupsid

Basic syntax:

```bash
impacket-lookupsid \
    example.local/alice:'Password'@dc01.example.local
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

```bash
impacket-findDelegation \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

Current Impacket supports discovery of relationships involving:

```text
Unconstrained delegation
Constrained delegation
Resource-Based Constrained Delegation
```

---

# Delegation Workflow

```text
findDelegation
      |
      v
Principal
      |
      v
Delegation Type
      |
      v
Target Service
      |
      v
Prerequisites
      |
      v
Potential Path
```

Do not treat:

```text
Delegation configured
```

as equivalent to:

```text
Exploitable attack path
```

---

# RPC Endpoint Enumeration

## rpcdump

Help:

```bash
impacket-rpcdump -h
```

Typical use:

```bash
impacket-rpcdump \
    example.local/alice:'Password'@dc01.example.local
```

Useful for investigating:

```text
RPC endpoints
RPC interfaces
Protocol sequences
Exposed Windows services
```

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
    example.local/alice:'Password'@dc01.example.local
```

Depending on access, SAMR may expose information about:

```text
Users
Groups
Account information
Domain information
```

---

# SMB Client

## smbclient

Connect:

```bash
impacket-smbclient \
    example.local/alice:'Password'@file01.example.local
```

---

# SMB Client with NTLM Hash

```bash
impacket-smbclient \
    example.local/alice@file01.example.local \
    -hashes :<NT-HASH>
```

---

# SMB Client Help

After connecting:

```text
help
```

Use interactive help to verify supported operations.

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
Focused Review
```

Review relevant files rather than recursively downloading entire file servers.

---

# Interesting Share Content

Look for:

```text
Configuration files
Deployment scripts
Backup files
PowerShell scripts
Batch files
Connection strings
Certificates
Keys
Administrative documentation
Service configuration
```

---

# SMB Server

## smbserver

Create a directory:

```bash
mkdir -p /tmp/share
```

Start an SMB server:

```bash
impacket-smbserver SHARE /tmp/share
```

Check available options first:

```bash
impacket-smbserver -h
```

---

# SMB Server Checklist

```text
[ ] Correct interface exposure
[ ] Firewall understood
[ ] Share contents reviewed
[ ] Authentication considered
[ ] Client-sensitive files excluded
[ ] Server stopped after use
```

---

# Kerberos TGT

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
.ccache
```

After obtaining an authorised ticket:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Then:

```bash
klist
```

---

# Kerberos Service Ticket

## getST

Help:

```bash
impacket-getST -h
```

Relevant to:

```text
S4U
Constrained delegation
RBCD
Service-specific Kerberos access
```

Use the dedicated delegation notes for technique-specific command sequences.

---

# Kerberos Ticket Conversion

## ticketConverter

Help:

```bash
impacket-ticketConverter -h
```

Concept:

```text
.kirbi
   |
   v
ticketConverter
   |
   v
.ccache
```

or:

```text
.ccache
   |
   v
ticketConverter
   |
   v
.kirbi
```

---

# Ticket Formats

Commonly:

```text
Linux
  |
  +--> ccache

Windows tooling
  |
  +--> kirbi
```

Conversion changes the ticket format, not the identity or privileges represented by the ticket.

---

# Ticket Creation

## ticketer

Help:

```bash
impacket-ticketer -h
```

This is advanced Kerberos functionality associated with techniques such as:

```text
Golden Tickets
Silver Tickets
Trust Tickets
Kerberos persistence
```

Use the dedicated Kerberos notes before using ticket-creation functionality.

---

# Credential Access

## secretsdump

Help:

```bash
impacket-secretsdump -h
```

Potential sources include:

```text
SAM
LSA Secrets
Cached domain credentials
NTDS
```

!!! danger
    Credential dumping is highly sensitive and should only be performed when explicitly permitted by the rules of engagement.

---

# secretsdump Checklist

Before use:

```text
[ ] Credential dumping explicitly permitted
[ ] Target approved
[ ] Account approved
[ ] Required privilege understood
[ ] Sensitive-data handling defined
[ ] Evidence location protected
[ ] Cleanup requirements understood
```

---

# Credential Access Workflow

```text
Administrative Access
        |
        v
Credential Dumping Permitted?
        |
    +---+---+
    |       |
   No      Yes
    |       |
    v       v
  Stop    Select
          Target
            |
            v
        Collect Minimum
        Required Evidence
            |
            v
          Protect
           Data
```

---

# Remote Administration

Common Impacket tools:

```text
psexec
wmiexec
smbexec
dcomexec
atexec
```

---

# Remote Administration Tool Map

| Tool | Primary Mechanism |
|---|---|
| `psexec` | SMB + Service Control Manager |
| `smbexec` | SMB + service-based execution |
| `wmiexec` | WMI / DCOM |
| `dcomexec` | DCOM |
| `atexec` | Task Scheduler |

---

# Remote Administration Rule

Do not jump from:

```text
Credential found
```

directly to:

```text
Remote execution
```

Use:

```text
Credential
    |
    v
Authentication
    |
    v
Privilege
    |
    v
Remote Management Exposure
    |
    v
Authorisation
    |
    v
Controlled Remote Administration
```

---

# psexec

Help:

```bash
impacket-psexec -h
```

Typical target syntax:

```text
domain/user:password@target
```

It uses service-management mechanisms and should be considered intrusive.

---

# wmiexec

Help:

```bash
impacket-wmiexec -h
```

Requirements may include:

```text
Administrative access
RPC Endpoint Mapper
DCOM
Dynamic RPC connectivity
Firewall allowance
```

---

# smbexec

Help:

```bash
impacket-smbexec -h
```

Uses SMB and service-management functionality.

Treat service-based execution as intrusive.

---

# dcomexec

Help:

```bash
impacket-dcomexec -h
```

Useful for testing authorised remote administration through DCOM.

---

# atexec

Help:

```bash
impacket-atexec -h
```

Uses Windows Task Scheduler interfaces.

This may create different telemetry from service-based or WMI execution.

---

# Selecting Remote Administration

```text
Need Remote Administration?
          |
          v
SMB + SCM Available?
          |
       +--+--+
       |     |
      Yes    No
       |     |
       v     v
 psexec /   WMI?
 smbexec     |
          +--+--+
          |     |
         Yes    No
          |     |
          v     v
       wmiexec DCOM?
                  |
               +--+--+
               |     |
              Yes    No
               |     |
               v     v
           dcomexec  Task
                     Scheduler?
                         |
                         v
                       atexec
```

Selection should also consider:

```text
Rules of engagement
Operational impact
Detection
Firewall
Privileges
Cleanup
```

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
     Attacker
        |
        v
    ntlmrelayx
        |
        v
 Target Service
```

---

# Capture vs Relay

```text
Capture

Client
  |
  v
Attacker
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
Attacker
  |
  v
Target
```

Remember:

```text
Capture != Relay
```

---

# Relay Checklist

Before testing:

```text
[ ] Relay explicitly permitted
[ ] Authentication source understood
[ ] Target identified
[ ] Target protocol identified
[ ] SMB signing checked
[ ] LDAP signing checked where relevant
[ ] LDAP channel binding checked where relevant
[ ] EPA considered where relevant
[ ] Identity privileges understood
[ ] Expected impact defined
```

---

# SMB Signing

A host where SMB signing is not required may be relevant to relay analysis.

But:

```text
Signing Not Required
        |
        v
Potential Prerequisite
        |
        v
Other Conditions?
        |
        v
Controlled Validation
```

Therefore:

```text
SMB signing not required
```

does not automatically mean:

```text
NTLM relay successful
```

---

# NetExec + Impacket Workflow

A common workflow:

```text
NetExec
   |
   v
Discover Hosts
   |
   v
Validate Credential
   |
   v
Enumerate Shares
   |
   v
Identify Interesting Relationship
   |
   v
Impacket
   |
   v
Focused Protocol Investigation
```

---

# BloodHound + Impacket Workflow

```text
BloodHound
    |
    v
Potential Attack Path
    |
    v
Understand Edge
    |
    v
Check Prerequisites
    |
    v
Impacket
    |
    v
Controlled Validation
```

---

# Responder + Impacket Workflow

For authorised authentication relay testing:

```text
Responder
    |
    v
Name Resolution /
Authentication
    |
    v
Authentication Attempt
    |
    v
ntlmrelayx
    |
    v
Target
```

Again:

```text
Captured authentication
        !=
Successful relay
```

---

# Pivoting

Before using Impacket through a pivot, verify:

```text
Routing
DNS
SMB
LDAP
Kerberos
RPC
Dynamic RPC ports
```

---

# Pivot Checklist

```bash
ip addr
```

```bash
ip route
```

```bash
cat /etc/resolv.conf
```

```bash
dig "$DC"
```

Then check required ports for the specific operation.

---

# Kerberos Through a Pivot

Remember:

```text
Route Works
    |
    v
DNS Works?
    |
    v
Time Correct?
    |
    v
FQDN Correct?
    |
    v
KDC Reachable?
    |
    v
Kerberos Works
```

---

# Common Troubleshooting

## Check Tool

```bash
which impacket-GetADUsers
```

---

## Check Version

```bash
python3 -c "from importlib.metadata import version; print(version('impacket'))"
```

---

## Check Help

```bash
impacket-GetADUsers -h
```

---

## Check DNS

```bash
dig dc01.example.local
```

---

## Check LDAP SRV

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

## Check Kerberos SRV

```bash
dig SRV _kerberos._tcp.example.local
```

---

## Check Time

```bash
date
```

---

## Check Kerberos Cache

```bash
echo "$KRB5CCNAME"
```

```bash
klist
```

---

# NTLM Hash Format

Common format:

```text
LMHASH:NTHASH
```

When only the NT hash is available:

```text
:NTHASH
```

---

# Domain vs Local Account

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

# IP vs FQDN

For Kerberos, prefer:

```text
dc01.example.local
```

over:

```text
10.10.20.10
```

where appropriate.

Kerberos depends on service identities and SPNs.

---

# RPC Troubleshooting

Relevant connectivity can include:

```text
135/tcp
445/tcp
Dynamic RPC ports
```

depending on the tool.

If:

```text
SMB works
```

but:

```text
wmiexec fails
```

do not automatically assume the credential is wrong.

Investigate RPC/DCOM connectivity and authorisation.

---

# Authentication != Authorisation

Remember:

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
Service Control Manager Access

SMB Authentication
        !=
Remote Registry Access
```

---

# Evidence Directory

Create:

```bash
mkdir -p evidence/impacket/{ldap,kerberos,smb,rpc,delegation,credentials,remote-access,relay}
```

Example:

```text
evidence/
└── impacket/
    ├── ldap/
    ├── kerberos/
    ├── smb/
    ├── rpc/
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
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10 \
    -all |
    tee evidence/impacket/ldap/users.txt
```

Be careful not to expose credentials in command history or screenshots.

---

# New Credential Workflow

Whenever a new credential is obtained:

```text
NEW CREDENTIAL
      |
      v
Domain or Local?
      |
      v
Validate Carefully
      |
      +--> SMB
      |
      +--> LDAP
      |
      +--> Kerberos
      |
      v
Enumerate User
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
SMB?
   |
   v
RPC?
   |
   v
LDAP?
   |
   v
WinRM?
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
Find DNS
    |
    v
Find DCs
    |
    v
Understand Trust
    |
    v
Enumerate Users
    |
    v
Enumerate SPNs
    |
    v
Enumerate Delegation
    |
    v
BloodHound
    |
    v
Cross-Domain Paths
```

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
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10 \
    -all
```

SPNs:

```bash
impacket-GetUserSPNs \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

Delegation:

```bash
impacket-findDelegation \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

SID enumeration:

```bash
impacket-lookupsid \
    example.local/alice:'Password'@dc01.example.local
```

Then:

```text
Review
  |
  v
BloodHound
  |
  v
Potential Relationships
  |
  v
Focused Validation
```

---

# What Tool Do I Need?

```text
                    WHAT DO I NEED?
                           |
       +-------------------+-------------------+
       |                   |                   |
       v                   v                   v
      AD                 Kerberos             SMB
       |                   |                   |
       |                   |                   |
       +--> Users           +--> TGT            +--> Client
       |    GetADUsers      |    getTGT          |    smbclient
       |                   |                   |
       +--> SPNs            +--> Service         +--> Server
       |    GetUserSPNs     |    Ticket          |    smbserver
       |                   |    getST            |
       +--> AS-REP          |                   |
       |    GetNPUsers      +--> Convert         |
       |                        Ticket           |
       +--> Delegation          ticketConverter  |
       |    findDelegation                      |
       |                                       |
       +--> SID / RID                           |
            lookupsid                           |
                                               |
       +-------------------+-------------------+
                           |
                           v
                    ADMINISTRATION
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
        Service           WMI              DCOM
        psexec          wmiexec          dcomexec
        smbexec
                           |
                           v
                     Task Scheduler
                           |
                           v
                         atexec


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

# One-Minute Impacket Reference

```text
Users
    -> GetADUsers

AS-REP
    -> GetNPUsers

SPNs
    -> GetUserSPNs

SIDs
    -> lookupsid

Delegation
    -> findDelegation

SMB files
    -> smbclient

SMB server
    -> smbserver

TGT
    -> getTGT

Service ticket
    -> getST

Ticket conversion
    -> ticketConverter

Credential access
    -> secretsdump

Service execution
    -> psexec / smbexec

WMI
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

## Context

```text
[ ] Domain
[ ] DC hostname
[ ] DC IP
[ ] DNS
[ ] Time
[ ] Routes
```

## Credentials

```text
[ ] Username
[ ] Domain/local context
[ ] Password or approved authentication material
[ ] Hash format understood
[ ] Kerberos cache checked
```

## Enumeration

```text
[ ] Users
[ ] SPNs
[ ] AS-REP configuration
[ ] SIDs where relevant
[ ] Delegation
[ ] SMB shares
[ ] RPC where relevant
```

## Kerberos

```text
[ ] DNS correct
[ ] FQDN correct
[ ] Time correct
[ ] KDC reachable
[ ] Ticket type understood
[ ] KRB5CCNAME correct
```

## Remote Administration

```text
[ ] Administrative rights confirmed
[ ] Remote execution authorised
[ ] Protocol chosen deliberately
[ ] Operational impact understood
[ ] Evidence collected
```

## Credential Access

```text
[ ] Explicitly authorised
[ ] Target approved
[ ] Sensitive-data handling defined
[ ] Minimum evidence collected
```

## Relay

```text
[ ] Explicitly authorised
[ ] Source understood
[ ] Target understood
[ ] Signing/protection reviewed
[ ] Identity privilege understood
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
             +----------+----------+
             |                     |
             v                     v
          IDENTITY               TARGET
             |                     |
             v                     v
        AUTHENTICATION          PROTOCOL
             |                     |
      +------+------+       +------+------+
      |      |      |       |      |      |
      v      v      v       v      v      v
   Password Hash Kerberos   SMB   LDAP   RPC
                    |
                    v
                  Ticket
                    |
             +------+------+
             |             |
             v             v
        ENUMERATION       ACCESS
             |             |
             v             v
        Relationships   Privilege
             |             |
             +------+------+
                    |
                    v
                 ANALYSE
                    |
                    v
               VALIDATE
                    |
                    v
                 EVIDENCE
```

---

# Rules to Remember

```text
Tool output != vulnerability

SPN != weak password

Delegation != exploitable path

SMB signing disabled != successful relay

Authentication != administration

Local admin != Domain Admin

Ticket != access to every service

Credential found != permission to dump more credentials

Admin access != permission to execute remotely
```

---

# Related Cheatsheets

```text
cheatsheets/active-directory.md
cheatsheets/netexec.md
cheatsheets/networking.md
cheatsheets/windows.md
cheatsheets/powershell.md
```

---

# Detailed Notes

```text
active-directory/impacket.md
active-directory/enumeration.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/asrep-roasting.md
active-directory/kerberoasting.md
active-directory/ntlm-relay.md
active-directory/lateral-movement.md
active-directory/pivoting.md
```

---

# References

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

## Impacket Examples

[Impacket Examples](https://github.com/fortra/impacket/tree/master/examples){ target="_blank" rel="noopener noreferrer" }

## GetADUsers

[GetADUsers](https://github.com/fortra/impacket/blob/master/examples/GetADUsers.py){ target="_blank" rel="noopener noreferrer" }

## GetNPUsers

[GetNPUsers](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py){ target="_blank" rel="noopener noreferrer" }

## GetUserSPNs

[GetUserSPNs](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py){ target="_blank" rel="noopener noreferrer" }

## findDelegation

[findDelegation](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py){ target="_blank" rel="noopener noreferrer" }

## lookupsid

[lookupsid](https://github.com/fortra/impacket/blob/master/examples/lookupsid.py){ target="_blank" rel="noopener noreferrer" }

## getTGT

[getTGT](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

## getST

[getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

## smbclient

[smbclient](https://github.com/fortra/impacket/blob/master/examples/smbclient.py){ target="_blank" rel="noopener noreferrer" }

## smbserver

[smbserver](https://github.com/fortra/impacket/blob/master/examples/smbserver.py){ target="_blank" rel="noopener noreferrer" }

## secretsdump

[secretsdump](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py){ target="_blank" rel="noopener noreferrer" }

## psexec

[psexec](https://github.com/fortra/impacket/blob/master/examples/psexec.py){ target="_blank" rel="noopener noreferrer" }

## wmiexec

[wmiexec](https://github.com/fortra/impacket/blob/master/examples/wmiexec.py){ target="_blank" rel="noopener noreferrer" }

## smbexec

[smbexec](https://github.com/fortra/impacket/blob/master/examples/smbexec.py){ target="_blank" rel="noopener noreferrer" }

## dcomexec

[dcomexec](https://github.com/fortra/impacket/blob/master/examples/dcomexec.py){ target="_blank" rel="noopener noreferrer" }

## atexec

[atexec](https://github.com/fortra/impacket/blob/master/examples/atexec.py){ target="_blank" rel="noopener noreferrer" }

## ntlmrelayx

[ntlmrelayx](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py){ target="_blank" rel="noopener noreferrer" }

## ticketer

[ticketer](https://github.com/fortra/impacket/blob/master/examples/ticketer.py){ target="_blank" rel="noopener noreferrer" }

## ticketConverter

[ticketConverter](https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py){ target="_blank" rel="noopener noreferrer" }

---

# Final Quick Reference

```text
DISCOVER
   |
   v
NetExec
   |
   v
IMPACKET
   |
   +--> GetADUsers ------> Users
   |
   +--> GetNPUsers ------> AS-REP
   |
   +--> GetUserSPNs -----> SPNs
   |
   +--> lookupsid -------> SIDs
   |
   +--> findDelegation --> Delegation
   |
   +--> smbclient -------> Shares
   |
   +--> getTGT ----------> TGT
   |
   +--> getST -----------> Service Ticket
   |
   +--> ticketConverter -> Ticket Format
   |
   +--> secretsdump -----> Credential Access
   |
   +--> psexec ----------> Service Administration
   |
   +--> wmiexec ---------> WMI
   |
   +--> smbexec ---------> SMB / Service
   |
   +--> dcomexec --------> DCOM
   |
   +--> atexec ----------> Task Scheduler
   |
   +--> ntlmrelayx ------> Relay
   |
   v
ANALYSE
   |
   v
VALIDATE
   |
   v
EVIDENCE
```
