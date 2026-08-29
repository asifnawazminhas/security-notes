# Impacket

Impacket is a collection of Python classes and command-line tools for working with network protocols commonly encountered during Windows and Active Directory security assessments.

It provides implementations and tooling for protocols including:

```text
SMB1 / SMB2 / SMB3
MS-RPC
LDAP
Kerberos
NTLM
DCOM
WMI
TDS / MSSQL
```

For an Active Directory assessment, Impacket is especially useful because it provides focused tools for:

```text
Directory enumeration
Kerberos enumeration
Kerberos ticket operations
SMB access
RPC enumeration
Delegation discovery
Credential access
Remote administration
NTLM relay testing
Ticket analysis
```

A useful way to think about Impacket is:

```text
                    Impacket
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
   Enumeration     Authentication     Protocols
       |               |               |
       v               v               v
      LDAP          Kerberos          SMB
      RPC             NTLM            RPC
      SMB            Password         WMI
                       Hash           DCOM
                       Ticket         MSSQL
                       Key
```

---

# Authorised Testing

The commands in this note are intended for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Training laboratories
CTFs
Security research
```

Some Impacket tools can:

```text
Request Kerberos tickets
Validate credentials
Access remote shares
Dump credentials
Create services
Create scheduled tasks
Execute commands remotely
Relay authentication
Modify remote systems
```

Confirm that the specific activity is permitted by the rules of engagement before using intrusive functionality.

---

# Impacket in the AD Workflow

Impacket is most useful after basic network and domain context has been established.

```text
Network Access
     |
     v
AD Discovery
     |
     v
Domain Controller
     |
     v
Credentials?
     |
 +---+---+
 |       |
No      Yes
 |       |
 v       v
Basic   Authenticated
Enum    Enumeration
         |
         +--> LDAP
         +--> SMB
         +--> RPC
         +--> Kerberos
         |
         v
   Relationships
         |
         v
   Focused Validation
```

NetExec is often useful for broad discovery and access mapping.

Impacket is often useful for focused protocol operations.

```text
NetExec
   |
   v
Broad Discovery
   |
   v
Interesting Relationship
   |
   v
Impacket
   |
   v
Focused Investigation
```

---

# Current Version

Check your installed version rather than assuming commands from an older write-up still apply.

```bash
python3 -c "from importlib.metadata import version; print(version('impacket'))"
```

The upstream repository should be checked when syntax differs from your installed package.

---

# Installation

The upstream Impacket project recommends `pipx` for system-wide command-line installation.

Install pipx:

```bash
sudo apt update
sudo apt install pipx
```

Ensure the pipx path is configured:

```bash
pipx ensurepath
```

Install the current stable Impacket package:

```bash
python3 -m pipx install impacket
```

Open a new shell if necessary.

---

# Kali Linux

Kali also packages Impacket.

Search:

```bash
apt search impacket
```

Install:

```bash
sudo apt update
sudo apt install python3-impacket
```

Depending on the package and distribution, command names can differ from upstream pipx installations.

Always check:

```bash
which impacket-smbclient
```

and:

```bash
which smbclient.py
```

---

# Installed Commands

List Impacket-related commands:

```bash
compgen -c | grep '^impacket-' | sort -u
```

Or inspect the pipx environment:

```bash
pipx list
```

Common packaged command names may look like:

```text
impacket-GetADUsers
impacket-GetNPUsers
impacket-GetUserSPNs
impacket-findDelegation
impacket-getTGT
impacket-getST
impacket-lookupsid
impacket-smbclient
impacket-secretsdump
impacket-psexec
impacket-wmiexec
impacket-smbexec
impacket-dcomexec
impacket-atexec
impacket-ntlmrelayx
impacket-ticketer
impacket-ticketConverter
```

When working directly from the source repository, the corresponding example files use names such as:

```text
GetADUsers.py
GetNPUsers.py
GetUserSPNs.py
findDelegation.py
getTGT.py
getST.py
lookupsid.py
smbclient.py
secretsdump.py
psexec.py
wmiexec.py
smbexec.py
dcomexec.py
atexec.py
ntlmrelayx.py
ticketer.py
ticketConverter.py
```

This note uses the `.py` names conceptually.

Adapt them to the command names installed on your system.

---

# Help

Every Impacket tool has its own options.

Always check:

```bash
impacket-GetADUsers -h
```

or, from the source tree:

```bash
python3 examples/GetADUsers.py -h
```

This is particularly important because Impacket evolves and command-line options can change.

---

# Target Syntax

Many Impacket tools use a target format similar to:

```text
domain/username:password@target
```

Example:

```text
example.local/alice:Password@dc01.example.local
```

Other tools use:

```text
domain/username
```

with the target or Domain Controller supplied separately.

Always check:

```bash
<tool> -h
```

---

# Authentication Models

Impacket supports several authentication models.

```text
                   Authentication
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
    Password            NTLM            Kerberos
                          |                 |
                          v                 |
                        Hash                |
                                            |
                             +--------------+-------------+
                             |              |             |
                             v              v             v
                          Password         TGT          AES Key
                                           |
                                           v
                                         ccache
```

---

# Password Authentication

Many tools accept:

```text
domain/user:password@target
```

Example:

```bash
impacket-smbclient \
    example.local/alice:'Password'@file01.example.local
```

Be careful with:

```text
Shell history
Process listings
Terminal logs
Screenshots
Evidence files
```

when supplying plaintext credentials.

---

# NTLM Hash Authentication

Many Impacket tools support:

```text
-hashes LMHASH:NTHASH
```

A commonly used format when only the NT hash is known is:

```text
-hashes :NTHASH
```

Example structure:

```bash
impacket-smbclient \
    example.local/alice@file01.example.local \
    -hashes :<NT-HASH>
```

This represents NTLM hash-based authentication.

The dedicated Pass-the-Hash note should cover the technique and its prerequisites in detail.

---

# Kerberos Authentication

Many Impacket tools support:

```text
-k
```

for Kerberos authentication.

Depending on the tool, Kerberos authentication may use:

```text
Password
NTLM hashes
AES key
Kerberos credential cache
```

Kerberos workflows depend heavily on:

```text
DNS
FQDNs
SPNs
Time synchronisation
Domain configuration
KDC reachability
```

---

# AES Keys

Where supported, Impacket tools commonly expose:

```text
-aesKey
```

for Kerberos authentication using an AES key.

Always verify the tool's help:

```bash
<tool> -h
```

before using key-based authentication.

---

# Kerberos Credential Cache

Kerberos tickets are commonly stored in a credential cache:

```text
.ccache
```

Set:

```bash
export KRB5CCNAME=/path/to/ticket.ccache
```

Verify:

```bash
echo "$KRB5CCNAME"
```

Then use a Kerberos-aware Impacket tool with its supported Kerberos options.

---

# Kerberos Ticket Inspection

If Kerberos utilities are installed:

```bash
klist
```

can be useful for reviewing the current credential cache.

The important relationship is:

```text
Ticket
  |
  v
Identity
  |
  v
Service
  |
  v
Validity
```

---

# Kerberos Requirements

Before troubleshooting Impacket itself, verify:

```text
DNS
Domain
FQDN
Domain Controller
KDC
Clock
SPN
Ticket
```

Check time:

```bash
date
```

Check the DC:

```bash
dig dc01.example.local
```

Check Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

Check LDAP:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# Core Impacket Tool Map

A useful operational map is:

```text
ENUMERATION

GetADUsers
GetNPUsers
GetUserSPNs
lookupsid
findDelegation
samrdump
rpcdump
net


KERBEROS

GetNPUsers
GetUserSPNs
getTGT
getST
ticketer
ticketConverter


SMB

smbclient
smbserver


CREDENTIAL ACCESS

secretsdump


REMOTE ADMINISTRATION

psexec
wmiexec
smbexec
dcomexec
atexec


RELAY

ntlmrelayx
```

---

# GetADUsers

`GetADUsers.py` queries Active Directory through LDAP and retrieves information about domain users.

It is useful during authenticated enumeration.

Typical information can include:

```text
Username
Email
Last logon
Password last set
```

---

# GetADUsers - Basic Usage

Current upstream syntax uses a target of:

```text
domain[/username[:password]]
```

Example:

```bash
impacket-GetADUsers \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10 \
    -all
```

---

# GetADUsers with NTLM Hash

Check the current help:

```bash
impacket-GetADUsers -h
```

The tool supports hash-based authentication.

General pattern:

```bash
impacket-GetADUsers \
    example.local/alice \
    -hashes :<NT-HASH> \
    -dc-ip 10.10.20.10 \
    -all
```

---

# GetADUsers with Kerberos

General pattern:

```bash
impacket-GetADUsers \
    example.local/alice \
    -k \
    -no-pass \
    -dc-host dc01.example.local \
    -all
```

This assumes an appropriate Kerberos authentication context exists.

---

# GetADUsers Workflow

```text
Domain Credential
       |
       v
GetADUsers
       |
       v
User Inventory
       |
       +--> Active users
       +--> Service identities
       +--> Stale users
       +--> Password age
       |
       v
Further Analysis
```

---

# GetNPUsers

`GetNPUsers.py` is used to identify accounts that do not require Kerberos pre-authentication and can support AS-REP roasting analysis.

Conceptually:

```text
Domain Users
     |
     v
Kerberos Pre-Authentication?
     |
 +---+---+
 |       |
Yes      No
 |       |
 |       v
 |   AS-REP Candidate
 |
 v
Normal Kerberos Flow
```

---

# AS-REP Candidate Enumeration

A common authorised assessment workflow is:

```text
Enumerate Users
      |
      v
Identify Accounts
Without Pre-Authentication
      |
      v
Determine Whether
Configuration Is Intended
      |
      v
Controlled Validation
```

The detailed technique belongs in:

```text
active-directory/asrep-roasting.md
```

---

# GetNPUsers Help

Always inspect:

```bash
impacket-GetNPUsers -h
```

because output and request options should be selected deliberately.

---

# GetUserSPNs

`GetUserSPNs.py` queries the domain for Service Principal Names associated with user accounts.

This makes it useful for Kerberoasting analysis.

Conceptually:

```text
Active Directory
       |
       v
Accounts with SPNs
       |
       v
Service Accounts
       |
       v
Privilege / Password Analysis
```

---

# Enumerate SPNs

Example:

```bash
impacket-GetUserSPNs \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

Enumeration alone can reveal:

```text
Service account
SPN
Service
Password age
Delegation-related information
```

depending on the directory data returned.

---

# Cross-Domain SPN Queries

Current versions support:

```text
-target-domain
```

for querying a domain different from the authenticating user's domain.

Check:

```bash
impacket-GetUserSPNs -h
```

before using cross-domain options.

---

# Kerberoasting

`GetUserSPNs.py` can also request service tickets.

That moves beyond simple SPN enumeration into Kerberoasting validation.

The workflow should therefore be separated:

```text
SPN Enumeration
      |
      v
Identify Candidate
      |
      v
Assess Account Context
      |
      v
Authorised Ticket Request
      |
      v
Offline Password Strength Assessment
```

See:

```text
active-directory/kerberoasting.md
```

---

# lookupsid

`lookupsid.py` performs SID lookup/enumeration through MS-RPC.

It can help enumerate:

```text
Users
Groups
Domain SID
RID relationships
```

---

# lookupsid Syntax

Current upstream target syntax is similar to:

```text
[[domain/]username[:password]@]<target>
```

Example:

```bash
impacket-lookupsid \
    example.local/alice:'Password'@dc01.example.local
```

---

# Why the Domain SID Matters

A SID looks conceptually like:

```text
S-1-5-21-111111111-222222222-333333333-1105
```

The domain portion is:

```text
S-1-5-21-111111111-222222222-333333333
```

The final value:

```text
1105
```

is the RID.

Understanding this helps with:

```text
Identity mapping
Trust analysis
SID history
Group analysis
Kerberos research
```

---

# findDelegation

`findDelegation.py` enumerates delegation relationships in Active Directory.

Current upstream functionality covers:

```text
Unconstrained delegation
Constrained delegation
Resource-Based Constrained Delegation
```

---

# Basic Delegation Enumeration

Example:

```bash
impacket-findDelegation \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

---

# Delegation Analysis

The result should be interpreted as:

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
Prerequisites
    |
    v
Potential Security Path
```

Do not treat every delegation relationship as automatically exploitable.

See:

```text
active-directory/unconstrained-delegation.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
```

---

# rpcdump

`rpcdump.py` enumerates RPC endpoints.

This can help identify:

```text
RPC services
Interfaces
Protocol sequences
Endpoints
```

It is useful when investigating Windows services exposed through RPC.

Check:

```bash
impacket-rpcdump -h
```

---

# samrdump

`samrdump.py` queries the Security Account Manager Remote Protocol.

Depending on access, it can provide information about:

```text
Users
Groups
Account properties
Domain information
```

Check:

```bash
impacket-samrdump -h
```

---

# net.py

Impacket also includes a remote alternative to portions of the Windows `net.exe` functionality.

It uses RPC and can interact with:

```text
Users
Groups
Local groups
Computers
```

Some operations can modify remote state.

Enumeration and modification should therefore be clearly separated.

---

# smbclient

`smbclient.py` provides an interactive SMB client.

It is useful when a share has already been identified and needs focused review.

Example:

```bash
impacket-smbclient \
    example.local/alice:'Password'@file01.example.local
```

---

# SMB Client Workflow

```text
NetExec
   |
   v
Interesting Share
   |
   v
Impacket smbclient
   |
   v
Focused Review
```

This avoids manually reviewing every share on every system.

---

# SMB Client Commands

Once connected, use:

```text
help
```

to review commands supported by the installed version.

Common operations include:

```text
List shares
Change share
List directories
Change directories
Download files
Upload files
```

Only write or upload files when explicitly required and authorised.

---

# SMB Share Analysis

Review shares for:

```text
Configuration
Scripts
Deployment files
Backups
Credentials
Certificates
Keys
Connection strings
Service configuration
Administrative documentation
```

Do not indiscriminately download entire shares.

---

# smbserver

`smbserver.py` creates an SMB server from the assessment system.

General syntax:

```bash
impacket-smbserver SHARE /path/to/directory
```

Example:

```bash
mkdir -p /tmp/share
```

```bash
impacket-smbserver SHARE /tmp/share
```

Modern environments should use appropriate SMB versions and authentication where required.

Review:

```bash
impacket-smbserver -h
```

before use.

---

# SMB Server Security

An assessment SMB server can expose files to the network.

Consider:

```text
Interface binding
Firewall rules
Authentication
Share contents
Network exposure
Cleanup
```

Never expose sensitive client material unnecessarily.

---

# getTGT

`getTGT.py` requests a Kerberos Ticket Granting Ticket for a supplied identity.

Conceptually:

```text
Credential
    |
    v
KDC
    |
    v
TGT
    |
    v
Credential Cache
```

---

# getTGT Workflow

Use:

```bash
impacket-getTGT -h
```

to confirm the syntax for your installed release.

A resulting ticket may be stored as:

```text
user.ccache
```

Set:

```bash
export KRB5CCNAME="$PWD/user.ccache"
```

Then inspect:

```bash
klist
```

---

# Why getTGT Is Useful

It allows a workflow based around Kerberos tickets rather than repeatedly supplying credentials.

```text
Credential
   |
   v
getTGT
   |
   v
.ccache
   |
   v
KRB5CCNAME
   |
   v
Kerberos-Aware Tools
```

---

# getST

`getST.py` is used for obtaining Kerberos service tickets in supported Kerberos workflows.

It is particularly relevant to topics such as:

```text
Constrained delegation
RBCD
S4U
Service-specific Kerberos access
```

Because the options depend heavily on the technique, detailed commands belong in the relevant delegation notes.

Always begin with:

```bash
impacket-getST -h
```

---

# S4U

Service-for-User Kerberos extensions are important in delegation attack paths.

Conceptually:

```text
Service Account
      |
      v
S4U2Self
      |
      v
User-to-Service Ticket
      |
      v
S4U2Proxy
      |
      v
Delegated Service
```

See:

```text
active-directory/s4u.md
```

for the detailed security model.

---

# ticketConverter

`ticketConverter.py` converts between common Kerberos ticket formats.

Common formats include:

```text
ccache
kirbi
```

Conceptually:

```text
Windows Tool
   |
   v
.kirbi
   |
   v
ticketConverter
   |
   v
.ccache
   |
   v
Linux Kerberos Tooling
```

and the reverse direction when required.

---

# Ticket Format Matters

Linux tooling commonly works with:

```text
ccache
```

while Windows Kerberos tooling frequently uses:

```text
kirbi
```

Ticket conversion does not change the identity or privileges represented by the ticket.

It changes the storage format.

---

# ticketer

`ticketer.py` can create Kerberos tickets from appropriate cryptographic key material.

This is advanced functionality associated with topics such as:

```text
Golden Tickets
Silver Tickets
Trust Tickets
Kerberos persistence
```

It should not be treated as routine enumeration.

See the dedicated Kerberos persistence notes before using it.

---

# Credential Access Tools

Impacket includes tools capable of accessing credential material.

The primary example is:

```text
secretsdump.py
```

This functionality is substantially more intrusive than normal enumeration.

---

# secretsdump

`secretsdump.py` can retrieve credential-related secrets from Windows systems and Active Directory under appropriate privilege conditions.

Depending on the target and access, this may involve sources such as:

```text
SAM
LSA Secrets
Cached domain credentials
NTDS
```

---

# secretsdump Security Model

Think in terms of:

```text
Administrative Access
        |
        v
Credential Material Accessible?
        |
        v
Collection Method
        |
        v
Sensitive Secrets
        |
        v
New Identities
```

This is a major security boundary.

---

# Authorisation Before secretsdump

Before using it, confirm:

```text
[ ] Credential dumping is in scope
[ ] Target is approved
[ ] Account is approved
[ ] Sensitive-data handling is defined
[ ] Evidence storage is protected
[ ] Cleanup requirements are understood
```

Do not run credential dumping simply because administrative access exists.

---

# NTDS

Domain Controller credential extraction represents particularly high-impact testing.

Conceptually:

```text
Domain Controller
       |
       v
NTDS
       |
       v
Domain Credential Material
       |
       v
Potential Domain-Wide Impact
```

See:

```text
active-directory/ntds.md
```

for detailed methodology.

---

# Remote Administration

Impacket includes several remote command-execution examples.

Common tools include:

```text
psexec
wmiexec
smbexec
dcomexec
atexec
```

These tools use different Windows mechanisms.

---

# Remote Execution Comparison

```text
psexec
   |
   +--> SMB
   +--> Service Control Manager

smbexec
   |
   +--> SMB
   +--> Service-based execution

wmiexec
   |
   +--> DCOM
   +--> WMI

dcomexec
   |
   +--> DCOM

atexec
   |
   +--> Task Scheduler
```

The correct tool depends on:

```text
Privileges
Firewall
Available services
Operational impact
Detection considerations
Rules of engagement
```

---

# psexec

`psexec.py` implements remote execution using SMB and Windows service-management mechanisms.

Because it can create and interact with a service, it should be considered intrusive.

Check:

```bash
impacket-psexec -h
```

before use.

---

# psexec Workflow

```text
Administrative Credential
          |
          v
SMB Reachability
          |
          v
Service Control Access
          |
          v
Remote Execution
```

Use only after administrative access has been established and remote execution is authorised.

---

# wmiexec

`wmiexec.py` executes commands through WMI/DCOM.

Current upstream documentation notes that the account must have appropriate administrative access and that DCOM connectivity is required.

Conceptually:

```text
Administrative Identity
        |
        v
DCOM
        |
        v
WMI
        |
        v
Remote Process
```

---

# WMI Requirements

Typical considerations include:

```text
RPC Endpoint Mapper
Dynamic RPC ports
DCOM
Firewall
Administrative rights
```

A successful SMB authentication does not guarantee WMI access.

---

# smbexec

`smbexec.py` uses SMB and service-management mechanisms for remote command execution.

It should be treated as intrusive because service-based execution creates observable host activity.

Check:

```bash
impacket-smbexec -h
```

---

# dcomexec

`dcomexec.py` performs remote execution using DCOM.

This can be relevant when:

```text
SMB-based execution is unavailable
DCOM is reachable
The identity has sufficient rights
```

Check:

```bash
impacket-dcomexec -h
```

---

# atexec

`atexec.py` uses the Windows Task Scheduler interfaces to execute a command remotely.

Conceptually:

```text
Administrative Identity
        |
        v
Task Scheduler RPC
        |
        v
Scheduled Task
        |
        v
Command
```

This creates different telemetry from WMI or service-based execution.

---

# Choose Remote Administration Deliberately

Do not randomly cycle through:

```text
psexec
wmiexec
smbexec
dcomexec
atexec
```

Instead:

```text
What access do I have?
        |
        v
What protocol is reachable?
        |
        v
What mechanism is permitted?
        |
        v
What operational impact is acceptable?
        |
        v
Choose One Technique
```

---

# Remote Execution Is Not Enumeration

Keep these phases separate:

```text
ENUMERATION
     |
     v
ACCESS VALIDATION
     |
     v
PRIVILEGE CONFIRMATION
     |
     v
REMOTE EXECUTION
```

Do not jump directly from discovering a credential to remote execution.

---

# ntlmrelayx

`ntlmrelayx.py` is Impacket's major NTLM relay framework.

It is used for controlled testing of authentication relay scenarios.

Conceptually:

```text
Victim Authentication
        |
        v
Attacker
        |
        v
ntlmrelayx
        |
        v
Target Service
        |
        v
Target Validates
Authentication
```

---

# Capture vs Relay

These are different concepts.

```text
CAPTURE

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
RELAY

Client
  |
  v
Attacker
  |
  v
Target Service
```

Therefore:

```text
Capture != Relay
```

---

# Relay Prerequisites

Relay depends on the protocol and target configuration.

Potential factors include:

```text
SMB signing
LDAP signing
LDAP channel binding
Authentication protocol
Target service
Identity privileges
EPA
Network reachability
```

A single missing hardening control does not prove a successful relay path.

---

# Relay Methodology

Use:

```text
Identify Potential Target
        |
        v
Review Security Controls
        |
        v
Identify Authentication Source
        |
        v
Confirm Rules of Engagement
        |
        v
Controlled Relay Validation
        |
        v
Record Exact Impact
```

See:

```text
active-directory/ntlm-relay.md
```

for the full technique.

---

# Responder and ntlmrelayx

Responder and Impacket are commonly used together in authorised relay testing.

Conceptually:

```text
Responder
    |
    v
Name Resolution / Authentication
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

But remember:

```text
Responder Capture
       !=
Successful Relay
```

---

# BloodHound and Impacket

BloodHound helps identify relationships.

Impacket can help validate selected relationships.

```text
BloodHound
    |
    v
Potential Path
    |
    v
Understand Edge
    |
    v
Impacket
    |
    v
Controlled Validation
```

Do not automatically exercise every BloodHound edge.

---

# NetExec and Impacket

The tools complement each other.

```text
NetExec
   |
   +--> Broad host discovery
   +--> Credential validation
   +--> Share enumeration
   +--> Access mapping
   |
   v
Interesting Target
   |
   v
Impacket
   |
   +--> Focused LDAP
   +--> Focused RPC
   +--> Kerberos
   +--> SMB
   +--> Delegation
   +--> Remote administration
```

---

# PowerView and Impacket

PowerView provides directory-oriented enumeration from Windows.

Impacket provides protocol-oriented operations from Linux.

```text
Windows
   |
   v
PowerView
   |
   v
Directory Relationships

Linux
   |
   v
Impacket
   |
   v
Protocol Relationships
```

Using both can provide different perspectives on the same environment.

---

# Impacket Through a Pivot

Impacket is commonly used after gaining access to another network segment.

```text
Kali
 |
 v
Pivot
 |
 v
Internal Network
 |
 v
Domain Controller
 |
 v
Impacket
```

Before assuming a tool is broken, verify:

```text
Routing
DNS
Kerberos
RPC
SMB
LDAP
Dynamic RPC ports
```

---

# SOCKS vs Routed Pivoting

Some Impacket operations are straightforward through SOCKS.

Others become more complicated because Windows protocols may use:

```text
Multiple connections
Dynamic RPC ports
Hostname resolution
Kerberos
```

A routed/TUN-based pivot can therefore be more convenient for broad AD testing.

See:

```text
active-directory/pivoting.md
```

---

# DNS During Pivoting

Check:

```bash
cat /etc/resolv.conf
```

Resolve the DC:

```bash
dig dc01.example.local
```

Check LDAP:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Check Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

---

# Common Error - Clock Skew

Kerberos is time sensitive.

Check:

```bash
date
```

If Kerberos authentication fails unexpectedly, compare the assessment system's time with the Domain Controller.

Do not immediately assume the credential or ticket is invalid.

---

# Common Error - DNS

A common failure pattern is:

```text
IP connectivity works
        |
        v
Hostname resolution fails
        |
        v
Kerberos fails
```

Correct DNS rather than permanently replacing hostnames with IP addresses.

---

# Common Error - SPN Mismatch

Kerberos authenticates services through SPNs.

Using:

```text
10.10.20.10
```

where the ticket expects:

```text
dc01.example.local
```

can cause unexpected authentication problems.

Prefer correct FQDNs for Kerberos workflows.

---

# Common Error - Wrong Domain

Always distinguish:

```text
EXAMPLE\alice
```

from:

```text
FILE01\alice
```

A local account and a domain account with the same username are different security principals.

---

# Common Error - NTLM Hash Format

Impacket frequently expects:

```text
LMHASH:NTHASH
```

When only an NT hash is available, the format commonly becomes:

```text
:NTHASH
```

Always check the individual tool's help.

---

# Common Error - Wrong Ticket

A valid Kerberos ticket does not mean it is valid for every service.

Understand:

```text
TGT
```

versus:

```text
TGS
```

and the service principal represented by a ticket.

---

# Common Error - KRB5CCNAME

Check:

```bash
echo "$KRB5CCNAME"
```

Then:

```bash
klist
```

Make sure the expected cache is actually being used.

---

# Common Error - RPC Blocked

Tools such as:

```text
lookupsid
samrdump
wmiexec
dcomexec
atexec
```

may rely on RPC-related connectivity.

Check:

```text
135/tcp
445/tcp
Dynamic RPC ports
Firewall rules
```

depending on the technique.

---

# Common Error - Authentication Works but Tool Fails

This can occur because:

```text
Authentication succeeded
        |
        v
Required Authorisation Missing
```

For example:

```text
SMB authentication
        !=
Remote Registry access

SMB authentication
        !=
Service Control Manager access

SMB authentication
        !=
WMI access

SMB authentication
        !=
Domain Admin
```

---

# Common Error - Using Old Blog Syntax

Impacket changes over time.

When an old command fails:

```bash
<tool> -h
```

Then verify:

```bash
python3 -c "from importlib.metadata import version; print(version('impacket'))"
```

Compare the installed version against the matching upstream release.

---

# Operational Security

Impacket tools can create very different levels of telemetry.

Low-impact examples may include:

```text
LDAP enumeration
RPC enumeration
SMB browsing
```

More intrusive operations may include:

```text
Kerberos ticket requests
Credential dumping
Remote service creation
Remote task creation
WMI execution
DCOM execution
NTLM relay
```

Use the least intrusive operation that answers the assessment question.

---

# Evidence Collection

Create a structured evidence directory:

```bash
mkdir -p evidence/impacket
```

Suggested structure:

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

# Save Enumeration Output

Example:

```bash
impacket-GetADUsers \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10 \
    -all |
    tee evidence/impacket/ldap/users.txt
```

Be careful that commands containing passwords may themselves be captured by:

```text
Terminal logging
Shell history
Screenshots
```

---

# Evidence Naming

Useful names include:

```text
users.txt
spns.txt
delegation.txt
sid-enumeration.txt
shares.txt
kerberos-tickets.txt
remote-access.txt
relay-validation.txt
```

---

# Credential Evidence

Avoid putting actual:

```text
Passwords
NTLM hashes
AES keys
Kerberos tickets
Private keys
```

into reports unless strictly required.

Prefer evidence that demonstrates the security condition without unnecessarily reproducing sensitive secrets.

---

# Reporting

Report the security condition rather than the tool.

Avoid:

```text
secretsdump worked.
```

Prefer:

```text
The tested administrative account was able to access credential
material stored by the target Windows system.
```

Avoid:

```text
GetUserSPNs found an account.
```

Prefer:

```text
A domain service account was configured with a Service Principal
Name and was therefore eligible for Kerberos service-ticket
requests.
```

---

# Reporting Delegation

Avoid:

```text
findDelegation says constrained.
```

Prefer:

```text
The service account was configured for constrained delegation to
the identified service.
```

Then explain:

```text
Principal
Delegation type
Target service
Prerequisites
Potential impact
```

---

# Reporting Remote Administration

Avoid:

```text
wmiexec worked.
```

Prefer:

```text
The tested account possessed sufficient administrative privileges
to execute commands remotely on APP01 through WMI.
```

---

# Detection Perspective

Impacket activity may create telemetry across:

```text
Windows Security logs
Kerberos logs
SMB logs
LDAP logs
RPC telemetry
Service creation
Task Scheduler
WMI
DCOM
Network monitoring
EDR
Domain Controller logs
```

Different tools produce different indicators.

---

# Purple Team Use

Impacket is useful for controlled purple team exercises because individual protocols and behaviours can be tested separately.

Example:

```text
Technique
   |
   v
Execute Controlled Action
   |
   v
Observe Host Telemetry
   |
   v
Observe Network Telemetry
   |
   v
Detection?
   |
 +---+---+
 |       |
Yes      No
 |       |
 v       v
Tune    Create
Rule    Detection
```

---

# Tool Selection

A practical decision tree:

```text
What do I need?
      |
      +--> Domain users
      |       |
      |       +--> GetADUsers
      |
      +--> SPNs
      |       |
      |       +--> GetUserSPNs
      |
      +--> AS-REP candidates
      |       |
      |       +--> GetNPUsers
      |
      +--> SID / RID information
      |       |
      |       +--> lookupsid
      |
      +--> Delegation
      |       |
      |       +--> findDelegation
      |
      +--> SMB files
      |       |
      |       +--> smbclient
      |
      +--> Kerberos TGT
      |       |
      |       +--> getTGT
      |
      +--> Kerberos service ticket
      |       |
      |       +--> getST
      |
      +--> Ticket conversion
      |       |
      |       +--> ticketConverter
      |
      +--> Credential material
      |       |
      |       +--> secretsdump
      |
      +--> WMI administration
      |       |
      |       +--> wmiexec
      |
      +--> Service-based administration
      |       |
      |       +--> psexec / smbexec
      |
      +--> DCOM
      |       |
      |       +--> dcomexec
      |
      +--> Task Scheduler
      |       |
      |       +--> atexec
      |
      +--> NTLM relay
              |
              +--> ntlmrelayx
```

---

# Fast Authenticated Enumeration Workflow

Assume:

```text
Domain: example.local
DC: dc01.example.local
DC IP: 10.10.20.10
User: alice
```

Start with domain users:

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

SID information where appropriate:

```bash
impacket-lookupsid \
    example.local/alice:'Password'@dc01.example.local
```

Then:

```text
Review Results
      |
      v
BloodHound
      |
      v
Identify Relationships
      |
      v
Select Focused Technique
```

---

# New Credential Workflow

Whenever a new credential is obtained:

```text
New Credential
      |
      v
Identify Principal
      |
      v
Determine Domain / Local
      |
      v
Validate Carefully
      |
      v
LDAP Enumeration
      |
      v
SMB Access
      |
      v
Kerberos Relationships
      |
      v
Delegation
      |
      v
BloodHound
      |
      v
New Attack Paths
```

---

# New Host Workflow

When a new Windows host becomes reachable:

```text
New Host
   |
   v
SMB?
   |
   v
RPC?
   |
   v
WMI?
   |
   v
Remote Management?
   |
   v
Credentials Valid?
   |
   v
Privilege?
   |
   v
Relationships?
```

Use NetExec for broad validation and Impacket for focused follow-up.

---

# New Domain Workflow

When a new domain is discovered:

```text
New Domain
    |
    v
DNS
    |
    v
Domain Controllers
    |
    v
Trust Relationship
    |
    v
Users / Groups
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
Cross-Domain Paths
```

---

# Impacket Assessment Checklist

## Installation

```text
[ ] Impacket installed
[ ] Version identified
[ ] Installed command naming understood
[ ] Current tool help checked
```

## Environment

```text
[ ] Domain known
[ ] DC known
[ ] DC FQDN known
[ ] DC IP known
[ ] DNS configured
[ ] Time synchronised
[ ] Routes understood
```

## Authentication

```text
[ ] Account type understood
[ ] Domain/local context understood
[ ] Password handling protected
[ ] Hash format understood
[ ] Kerberos context understood
[ ] KRB5CCNAME checked where relevant
[ ] Ticket validity checked
```

## Enumeration

```text
[ ] Users reviewed
[ ] SPNs reviewed
[ ] AS-REP configuration reviewed
[ ] SIDs reviewed where useful
[ ] Delegation reviewed
[ ] RPC services reviewed where useful
[ ] SMB shares reviewed
```

## Kerberos

```text
[ ] DNS correct
[ ] Time correct
[ ] KDC reachable
[ ] FQDN used where appropriate
[ ] TGT/TGS distinction understood
[ ] Ticket cache understood
[ ] Delegation relationships analysed
```

## Remote Administration

```text
[ ] Administrative access confirmed first
[ ] Remote execution explicitly authorised
[ ] Appropriate protocol selected
[ ] Operational impact considered
[ ] Host artefacts considered
[ ] Detection telemetry considered
```

## Credential Access

```text
[ ] Credential dumping explicitly authorised
[ ] Target approved
[ ] Sensitive evidence protected
[ ] Scope limits understood
[ ] Cleanup requirements understood
```

## Relay

```text
[ ] Relay explicitly authorised
[ ] Authentication source understood
[ ] Target identified
[ ] SMB signing checked
[ ] LDAP protections checked
[ ] Identity privileges understood
[ ] Impact validated carefully
```

## Evidence

```text
[ ] Commands recorded
[ ] Targets recorded
[ ] Identities recorded
[ ] Relevant output saved
[ ] Passwords excluded where possible
[ ] Hashes protected
[ ] Tickets protected
[ ] Client data stored securely
```

---

# Impacket Mental Model

Do not memorise Impacket as a random collection of scripts.

Use this model:

```text
                         IMPACKET
                            |
                            v
                         PROTOCOL
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
             SMB           LDAP          RPC
              |             |             |
              +-------------+-------------+
                            |
                            v
                       AUTHENTICATION
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
       Password            NTLM            Kerberos
                            |                 |
                            v                 v
                           Hash        Ticket / Key
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                         IDENTITY
                            |
                            v
                      AUTHORISATION
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
          Enumerate       Access       Administer
              |             |             |
              v             v             v
          AD / RPC         SMB       WMI / DCOM
          Kerberos        Shares     Services / Tasks
              |             |             |
              +-------------+-------------+
                            |
                            v
                         ANALYSIS
                            |
                            v
                       ATTACK PATH
                            |
                            v
                   CONTROLLED VALIDATION
```

---

# Impacket vs NetExec vs BloodHound vs Responder

```text
NetExec
   |
   v
Broad Network and Access Validation


Impacket
   |
   v
Focused Protocol Operations


BloodHound
   |
   v
Identity and Attack-Path Analysis


Responder
   |
   v
Name-Resolution and Authentication Testing
```

Together:

```text
Discovery
    |
    v
NetExec
    |
    v
Enumeration
    |
    +--> Impacket
    |
    +--> BloodHound
    |
    v
Potential Path
    |
    v
Focused Validation
    |
    +--> Impacket
    |
    +--> Responder / Relay where appropriate
    |
    v
Evidence
```

---

# Related Notes

```text
active-directory/index.md
active-directory/methodology.md
active-directory/enumeration.md
active-directory/netexec.md
active-directory/bloodhound.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/asrep-roasting.md
active-directory/kerberoasting.md
active-directory/pass-the-hash.md
active-directory/unconstrained-delegation.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
active-directory/ntlm-relay.md
active-directory/ntds.md
active-directory/lateral-movement.md
active-directory/pivoting.md
```

---

# References

## Official Impacket Repository

[Official Impacket Repository](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

## Impacket README

[Impacket README](https://github.com/fortra/impacket/blob/master/README.md){ target="_blank" rel="noopener noreferrer" }

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

## smbclient

[smbclient](https://github.com/fortra/impacket/blob/master/examples/smbclient.py){ target="_blank" rel="noopener noreferrer" }

## smbserver

[smbserver](https://github.com/fortra/impacket/blob/master/examples/smbserver.py){ target="_blank" rel="noopener noreferrer" }

## getTGT

[getTGT](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

## getST

[getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

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

# Final Impacket Model

```text
                         IMPACKET
                            |
                            v
                     Understand Context
                            |
              +-------------+-------------+
              |                           |
              v                           v
          Identity                     Network
              |                           |
              v                           v
     Password / Hash / Ticket       SMB / LDAP / RPC
              |                           |
              +-------------+-------------+
                            |
                            v
                        ENUMERATE
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
      Users                SPNs             Delegation
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                         ANALYSE
                            |
                            v
                      BloodHound / AD
                            |
                            v
                    Potential Relationship
                            |
                            v
                   Confirm Prerequisites
                            |
                            v
                  Controlled Validation
                            |
              +-------------+-------------+
              |                           |
              v                           v
        No Security Impact          Security Impact
              |                           |
              v                           v
          Document                     Evidence
                                          |
                                          v
                                        Report
```

The key principle is:

```text
Impacket is not an attack sequence.

It is a protocol toolkit.
```

Choose the tool because you understand:

```text
The protocol
The identity
The authentication method
The required privilege
The target relationship
The expected result
```

and not simply because a command appears in a penetration-testing checklist.
