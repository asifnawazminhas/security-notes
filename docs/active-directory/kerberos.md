# Kerberos

Kerberos is the primary authentication protocol used in modern Active Directory environments.

Understanding Kerberos is fundamental to Active Directory security testing because many important authentication and privilege relationships depend on it, including:

```text
Domain authentication
Service authentication
Single sign-on
Service Principal Names
Delegation
Kerberoasting
AS-REP Roasting
Pass-the-Ticket
Pass-the-Key
OverPass-the-Hash
Golden Tickets
Silver Tickets
S4U
Cross-domain authentication
```

Kerberos should not be approached as a collection of attack commands.

A better model is:

```text
Identity
   |
   v
Authentication
   |
   v
TGT
   |
   v
Service Request
   |
   v
TGS
   |
   v
Service
```

The security assessment methodology is therefore:

```text
Understand Kerberos
        |
        v
Map Principals
        |
        v
Map SPNs
        |
        v
Map Encryption
        |
        v
Map Preauthentication
        |
        v
Map Delegation
        |
        v
Analyse Tickets
        |
        v
Identify Weak Relationships
        |
        v
Authorised Validation
        |
        v
Evidence
        |
        v
Detection / Remediation
```

---

# Authorised Use

Use the techniques and tools described here only for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Active Directory security reviews
Training environments
CTFs
Security research
```

Kerberos operations can generate authentication traffic and security events on Domain Controllers.

Some techniques may also:

```text
Request authentication tickets
Request service tickets
Interact with privileged services
Use existing authentication material
Access sensitive identity information
```

Remain within the agreed rules of engagement.

---

# Why Kerberos Matters

Kerberos is central to Active Directory authentication.

It provides:

```text
Authentication
Mutual authentication
Single sign-on
Delegation
Service authentication
Cross-domain authentication
```

A user normally authenticates once and then receives tickets that can be used to access authorised resources without repeatedly sending the user's password.

Conceptually:

```text
Password / Key
      |
      v
Domain Authentication
      |
      v
TGT
      |
      +------------------+
      |                  |
      v                  v
   CIFS Ticket        HTTP Ticket
      |                  |
      v                  v
 File Server          Web Service
```

---

# Kerberos Components

Important components include:

```text
Client
Principal
Realm
Domain Controller
KDC
Authentication Service
Ticket-Granting Service
TGT
TGS / Service Ticket
SPN
Session Key
PAC
KRBTGT
```

---

# Kerberos Terminology

| Term | Meaning |
|---|---|
| KDC | Key Distribution Center |
| AS | Authentication Service |
| TGS | Ticket-Granting Service |
| TGT | Ticket-Granting Ticket |
| ST | Service Ticket |
| SPN | Service Principal Name |
| PAC | Privilege Attribute Certificate |
| Realm | Kerberos administrative domain |
| Principal | Kerberos identity |
| KRBTGT | AD account used by the KDC for TGT protection |
| AS-REQ | Authentication Service Request |
| AS-REP | Authentication Service Response |
| TGS-REQ | Ticket-Granting Service Request |
| TGS-REP | Ticket-Granting Service Response |
| AP-REQ | Application Request containing service authentication material |

---

# Kerberos Architecture

```text
                  ACTIVE DIRECTORY
                         |
                         v
                 Domain Controller
                         |
                         v
                        KDC
                    /         \
                   /           \
                  v             v
       Authentication       Ticket-Granting
          Service              Service
             |                    |
             v                    v
            TGT              Service Ticket
```

The KDC runs as part of the domain services on Domain Controllers.

---

# Authentication Flow

A simplified Kerberos authentication flow:

```text
CLIENT                      KDC                     SERVICE
  |                          |                         |
  |------ AS-REQ ----------->|                         |
  |                          |                         |
  |<----- AS-REP ------------|                         |
  |       TGT                |                         |
  |                          |                         |
  |------ TGS-REQ ---------->|                         |
  |       TGT + SPN          |                         |
  |                          |                         |
  |<----- TGS-REP -----------|                         |
  |       Service Ticket     |                         |
  |                          |                         |
  |---------------- AP-REQ -------------------------->|
  |                                                  |
  |<--------------- Service Access ------------------|
```

The user's password is not normally sent directly to each network service.

---

# Phase 1 - AS Exchange

The first major exchange is:

```text
AS-REQ
   |
   v
KDC Authentication Service
   |
   v
AS-REP
   |
   v
TGT
```

The client requests authentication from the KDC.

With normal Kerberos preauthentication enabled, the client must demonstrate knowledge of its long-term credential before receiving the TGT.

---

# AS-REQ

Conceptually:

```text
Client
  |
  | AS-REQ
  v
KDC
```

The request identifies the principal requesting authentication.

With preauthentication, additional authentication material is supplied.

---

# Preauthentication

Kerberos preauthentication protects accounts against unauthenticated AS-REP retrieval.

Conceptually:

```text
User
 |
 | Proof derived from credential
 v
KDC
 |
 | Verify
 v
Issue AS-REP
```

Without preauthentication:

```text
Username
   |
   v
AS-REQ
   |
   v
AS-REP
```

may be possible for affected accounts without first proving knowledge of the password.

This condition enables:

```text
AS-REP Roasting
```

Detailed testing belongs in:

```text
active-directory/asrep-roasting.md
```

---

# AS-REP

After successful authentication, the KDC returns:

```text
AS-REP
```

which includes authentication material associated with the user's TGT.

Conceptually:

```text
AS-REP
 |
 +--> TGT
 |
 +--> Client-side encrypted data
```

---

# Ticket-Granting Ticket

The TGT proves that the principal has authenticated to the domain.

```text
User
 |
 v
TGT
 |
 v
Request Service Tickets
```

The TGT is not normally presented directly to the final application service.

Instead, it is presented to the KDC to obtain service tickets.

---

# KRBTGT

Active Directory contains a special account:

```text
KRBTGT
```

The KDC uses secrets associated with this account to protect TGTs.

Conceptually:

```text
KRBTGT Secret
      |
      v
Protect TGT
      |
      v
Domain Trusts Ticket
```

Compromise of KRBTGT authentication material is extremely serious because it can enable forged TGTs.

This is associated with:

```text
Golden Tickets
```

---

# Phase 2 - TGS Exchange

Once a client has a TGT:

```text
TGT
 |
 v
TGS-REQ
 |
 v
KDC
 |
 v
TGS-REP
 |
 v
Service Ticket
```

The client requests access to a specific service.

---

# TGS-REQ

The request contains information identifying the target service.

That service is represented using a:

```text
Service Principal Name
```

or:

```text
SPN
```

---

# TGS-REP

The KDC returns a service ticket.

```text
TGS-REP
   |
   v
Service Ticket
   |
   v
Target Service
```

Part of the ticket is protected using key material associated with the service account.

This characteristic is central to understanding Kerberoasting.

---

# Service Authentication

The client presents the service ticket to the target service.

```text
Client
   |
   | Service Ticket
   v
Server
```

The server can validate the ticket using its own key material.

This reduces the need for the application server to contact the Domain Controller for every authentication attempt.

---

# Mutual Authentication

Kerberos supports mutual authentication.

Conceptually:

```text
Client verifies Server
        +
Server verifies Client
```

This is an important difference from older challenge-response authentication mechanisms.

---

# Single Sign-On

After initial authentication:

```text
User Login
    |
    v
TGT
    |
    +--> CIFS Ticket
    |
    +--> LDAP Ticket
    |
    +--> HTTP Ticket
    |
    +--> MSSQL Ticket
```

The user does not normally need to re-enter credentials for every service.

---

# Kerberos Port

The primary Kerberos port is:

```text
TCP/UDP 88
```

Check:

```bash
nc -vz dc01.example.local 88
```

Kerberos may also depend on:

```text
53      DNS
88      Kerberos
389     LDAP
445     SMB
464     Kerberos password operations
3268    Global Catalog
```

depending on the operation being performed.

---

# DNS Is Critical

Kerberos depends heavily on correct name resolution.

Check:

```bash
dig dc01.example.local
```

Check Kerberos SRV records:

```bash
dig SRV _kerberos._tcp.example.local
```

Check LDAP:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# Time Is Critical

Kerberos authentication is time-sensitive.

Check:

```bash
date
```

On Windows:

```powershell
w32tm /query /status
```

Domain hierarchy:

```powershell
w32tm /query /source
```

Large clock differences may result in Kerberos errors.

---

# Kerberos Troubleshooting Model

When Kerberos fails, check:

```text
DNS
 |
 v
FQDN
 |
 v
Domain / Realm
 |
 v
Time
 |
 v
KDC
 |
 v
SPN
 |
 v
Credential
 |
 v
Ticket
 |
 v
Encryption Type
```

---

# Domain and Realm

Active Directory domain:

```text
example.local
```

Kerberos realm is commonly represented uppercase:

```text
EXAMPLE.LOCAL
```

This becomes important when configuring Linux Kerberos clients.

---

# Linux Kerberos Configuration

The primary Kerberos configuration file is:

```text
/etc/krb5.conf
```

Example:

```ini
[libdefaults]
    default_realm = EXAMPLE.LOCAL
    dns_lookup_realm = false
    dns_lookup_kdc = true

[realms]
    EXAMPLE.LOCAL = {
        kdc = dc01.example.local
    }

[domain_realm]
    .example.local = EXAMPLE.LOCAL
    example.local = EXAMPLE.LOCAL
```

Adapt this to the target environment.

---

# Verify Kerberos Configuration

Check:

```bash
cat /etc/krb5.conf
```

Then:

```bash
kinit alice@EXAMPLE.LOCAL
```

Inspect:

```bash
klist
```

---

# kinit

Request a Kerberos TGT using the system Kerberos client:

```bash
kinit alice@EXAMPLE.LOCAL
```

Then inspect:

```bash
klist
```

Destroy the cache when finished:

```bash
kdestroy
```

---

# Windows Ticket Inspection

Windows includes:

```text
klist
```

Display tickets:

```powershell
klist
```

---

# Purge Windows Tickets

```powershell
klist purge
```

!!! warning
    Purging tickets affects the current authentication context and can interrupt access to resources. Do not use casually on production systems.

---

# Request a Windows Service Ticket

Windows can request a ticket for a specific SPN using:

```powershell
klist get <SPN>
```

For example, in an authorised test:

```powershell
klist get cifs/server01.example.local
```

Then:

```powershell
klist
```

This is useful for understanding ticket acquisition without requiring third-party tooling.

---

# Service Principal Names

An SPN uniquely identifies a service instance for Kerberos authentication.

Examples:

```text
cifs/server01.example.local
HTTP/web01.example.local
MSSQLSvc/sql01.example.local:1433
HOST/server01.example.local
LDAP/dc01.example.local
```

Conceptually:

```text
Service
   |
   v
SPN
   |
   v
AD Account
   |
   v
Kerberos Key
```

---

# SPN Enumeration - Windows

Native Windows:

```powershell
setspn -Q */*
```

This may produce substantial output in large environments.

---

# Query Specific SPN

```powershell
setspn -Q MSSQLSvc/*
```

---

# SPNs Registered to an Account

```powershell
setspn -L EXAMPLE\svc_sql
```

---

# PowerShell SPN Enumeration

Using the ActiveDirectory module:

```powershell
Get-ADUser -LDAPFilter '(servicePrincipalName=*)' `
    -Properties servicePrincipalName |
    Select-Object SamAccountName,servicePrincipalName
```

---

# PowerView SPN Enumeration

Depending on the PowerView version:

```powershell
Get-DomainUser -SPN
```

This can help identify service accounts.

---

# Linux LDAP SPN Enumeration

Using ldapsearch:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.example.local \
    -D 'alice@example.local' \
    -W \
    -b 'DC=example,DC=local' \
    '(servicePrincipalName=*)' \
    sAMAccountName servicePrincipalName
```

This performs directory enumeration without requesting service tickets.

---

# Impacket SPN Enumeration

Impacket provides:

```text
GetUserSPNs.py
```

or on many modern installations:

```text
impacket-GetUserSPNs
```

Enumeration-only example:

```bash
impacket-GetUserSPNs \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

This identifies user accounts with SPNs.

Ticket-requesting functionality should be reserved for the dedicated Kerberoasting workflow.

---

# NetExec Kerberos Context

NetExec supports Kerberos authentication across supported protocols.

Always check the installed version:

```bash
nxc smb --help
```

and:

```bash
nxc ldap --help
```

Kerberos usage depends on:

```text
DNS
FQDN
KDC
Time
Credential
Ticket cache
```

---

# Kerberos vs NTLM

Conceptually:

```text
Kerberos
   |
   +--> Ticket based
   +--> Mutual authentication
   +--> SPNs
   +--> Delegation
   +--> KDC
   +--> Single sign-on

NTLM
   |
   +--> Challenge-response
   +--> No Kerberos tickets
   +--> No native Kerberos delegation model
```

Kerberos is normally preferred in modern AD environments.

---

# Determine Authentication Protocol

Windows logs and network telemetry can help determine whether Kerberos or NTLM is being used.

Kerberos authentication normally produces Kerberos-specific Domain Controller events.

NTLM authentication produces different authentication telemetry.

Do not assume:

```text
Domain joined
    =
Always Kerberos
```

Applications may fall back to NTLM under certain conditions.

---

# Why Kerberos Falls Back to NTLM

Common reasons include:

```text
IP address used instead of hostname
SPN missing
SPN incorrect
SPN duplicate
DNS problem
Application does not support Kerberos
Authentication configuration
Cross-domain configuration
```

---

# Hostnames Matter

Kerberos generally expects service identity through SPNs.

Using:

```text
\\server01.example.local\share
```

may allow normal Kerberos service resolution.

Using an IP address may result in different authentication behaviour depending on configuration.

During assessments, compare:

```text
Hostname
FQDN
IP
```

when diagnosing Kerberos vs NTLM behaviour.

---

# Duplicate SPNs

Duplicate SPNs can cause Kerberos authentication problems.

Check:

```powershell
setspn -X
```

This searches for duplicate SPNs.

---

# Validate SPN

```powershell
setspn -Q cifs/server01.example.local
```

---

# PAC

Windows Kerberos tickets commonly contain a:

```text
Privilege Attribute Certificate
```

or:

```text
PAC
```

The PAC carries authorisation-related information used by Windows services.

Conceptually:

```text
Ticket
 |
 +--> Identity
 |
 +--> Session Information
 |
 +--> PAC
       |
       +--> User SID
       +--> Group information
       +--> Authorisation data
```

Kerberos therefore provides authentication while the PAC contributes information used for Windows authorisation decisions.

---

# Ticket Types

Important ticket categories:

```text
TGT
Service Ticket
Referral Ticket
```

For security testing, also understand:

```text
Legitimate tickets
Cached tickets
Forged tickets
```

---

# Ticket Storage - Windows

Windows manages Kerberos tickets through the Local Security Authority authentication infrastructure.

The built-in:

```powershell
klist
```

command provides a safe way to inspect the current ticket cache.

---

# Ticket Storage - Linux

Linux Kerberos implementations may use credential caches.

The environment variable:

```text
KRB5CCNAME
```

identifies the credential cache location or type.

Check:

```bash
echo "$KRB5CCNAME"
```

---

# List Linux Tickets

```bash
klist
```

---

# Ccache

A common credential cache format is:

```text
ccache
```

Conceptually:

```text
Authenticated User
      |
      v
Kerberos Tickets
      |
      v
Credential Cache
      |
      v
Subsequent Kerberos Authentication
```

Credential cache files must therefore be treated as sensitive authentication material.

---

# Impacket and Ccache

Impacket supports Kerberos authentication using:

```text
KRB5CCNAME
```

Example:

```bash
export KRB5CCNAME=/path/to/alice.ccache
```

Check:

```bash
klist
```

Then supported Impacket tools can use:

```text
-k
```

to attempt Kerberos authentication using available cache credentials.

Exact options depend on the individual tool.

---

# Impacket getTGT

Impacket provides:

```text
getTGT.py
```

or:

```text
impacket-getTGT
```

The tool requests a TGT for an account.

Check:

```bash
impacket-getTGT -h
```

Typical authorised lab pattern:

```bash
impacket-getTGT example.local/alice
```

The tool prompts for the password if it is not supplied.

A successful request normally creates a ccache file.

---

# Use the Resulting TGT

For example:

```bash
export KRB5CCNAME=alice.ccache
```

Check:

```bash
klist
```

Then Kerberos-aware tooling can use the cache where supported.

---

# Authentication Material

Kerberos authentication can be based on different forms of key material.

Conceptually:

```text
Password
   |
   v
Derived Key
   |
   v
Kerberos Authentication
```

Depending on account configuration and supported encryption types, authentication material may involve:

```text
Password-derived keys
AES128 key
AES256 key
Legacy RC4-related key material
```

---

# Pass-the-Key

If valid Kerberos key material is available, it may be possible to authenticate without knowing the plaintext password.

Conceptually:

```text
Kerberos Key
     |
     v
AS-REQ
     |
     v
TGT
```

Detailed methodology belongs in:

```text
active-directory/pass-the-key.md
```

---

# OverPass-the-Hash

OverPass-the-Hash refers to using suitable password-derived key material to obtain Kerberos authentication rather than using it directly with NTLM.

Conceptually:

```text
Credential Material
      |
      v
Kerberos Authentication
      |
      v
TGT
```

Detailed testing belongs in:

```text
active-directory/overpass-the-hash.md
```

---

# Pass-the-Ticket

Pass-the-Ticket uses an existing valid Kerberos ticket rather than requesting authentication using the original plaintext password.

Conceptually:

```text
Existing Ticket
      |
      v
Authentication Context
      |
      v
Kerberos Service Access
```

Ticket handling is covered in:

```text
active-directory/kerberos-tickets.md
```

---

# Kerberoasting

Kerberoasting is based on requesting service tickets for accounts associated with SPNs and analysing the resulting ticket material offline.

Conceptually:

```text
Valid Domain User
       |
       v
Enumerate SPNs
       |
       v
Service Account
       |
       v
Request TGS
       |
       v
Offline Password Analysis
```

The weakness is not:

```text
Kerberos exists
```

The risk is typically related to:

```text
Service account uses password-derived key
          +
Weak / crackable service-account password
          +
Service ticket can be requested
```

Detailed methodology belongs in:

```text
active-directory/kerberoasting.md
```

---

# Kerberoasting Enumeration

Enumeration without requesting tickets:

```bash
impacket-GetUserSPNs \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

This helps identify potential service accounts before deciding whether ticket requests are necessary.

---

# AS-REP Roasting

AS-REP Roasting applies to accounts where Kerberos preauthentication is disabled.

Conceptually:

```text
Preauthentication Disabled
          |
          v
        AS-REQ
          |
          v
        AS-REP
          |
          v
Offline Password Analysis
```

Detailed methodology belongs in:

```text
active-directory/asrep-roasting.md
```

---

# Find Accounts Without Preauthentication - PowerShell

Using the ActiveDirectory module:

```powershell
Get-ADUser \
    -Filter * \
    -Properties DoesNotRequirePreAuth |
    Where-Object {
        $_.DoesNotRequirePreAuth -eq $true
    } |
    Select-Object SamAccountName
```

This is useful for configuration auditing.

---

# LDAP Preauthentication Analysis

The relevant account configuration is represented through AD account-control settings.

Rather than immediately requesting AS-REP material, first identify affected accounts through directory enumeration.

This follows:

```text
Enumerate
   |
   v
Confirm Configuration
   |
   v
Assess Risk
   |
   v
Authorised Validation if Necessary
```

---

# Delegation

Kerberos supports delegation so a service can access another service on behalf of a user.

This enables legitimate multi-tier applications.

Conceptually:

```text
User
 |
 v
Front-End Service
 |
 | Delegation
 v
Back-End Service
```

Misconfigured delegation can create significant privilege escalation paths.

---

# Delegation Types

Important models include:

```text
Unconstrained Delegation

Constrained Delegation

Resource-Based Constrained Delegation

S4U
```

These are covered separately because each has different prerequisites and security implications.

---

# Unconstrained Delegation

Conceptually:

```text
User
 |
 v
Delegated Service
 |
 v
Potential ability to act using delegated credentials
```

See:

```text
active-directory/unconstrained-delegation.md
```

---

# Constrained Delegation

Conceptually:

```text
Service A
   |
   | Allowed to Delegate
   v
Specific Service B
```

See:

```text
active-directory/constrained-delegation.md
```

---

# Resource-Based Constrained Delegation

RBCD changes which side of the relationship controls delegation.

Conceptually:

```text
Service / Computer A
       |
       | AllowedToAct
       v
Computer B
```

See:

```text
active-directory/rbcd.md
```

---

# S4U

Kerberos Service-for-User extensions support service impersonation scenarios.

Important concepts include:

```text
S4U2Self
S4U2Proxy
```

Conceptually:

```text
S4U2Self
   |
   v
Service obtains ticket representing user to itself

S4U2Proxy
   |
   v
Service obtains ticket to another permitted service
```

See:

```text
active-directory/s4u.md
```

---

# Delegation Enumeration - Impacket

Impacket provides:

```text
findDelegation.py
```

or:

```text
impacket-findDelegation
```

Example:

```bash
impacket-findDelegation \
    example.local/alice:'Password' \
    -dc-ip 10.10.20.10
```

This helps identify:

```text
Unconstrained delegation
Constrained delegation
RBCD
```

---

# Delegation Enumeration - PowerShell

Using the ActiveDirectory module:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties TrustedForDelegation,TrustedToAuthForDelegation,msDS-AllowedToDelegateTo |
    Select-Object Name,
                  TrustedForDelegation,
                  TrustedToAuthForDelegation,
                  msDS-AllowedToDelegateTo
```

---

# BloodHound

BloodHound is useful for understanding Kerberos-related relationships in graph context.

Review:

```text
SPNs
Delegation
RBCD
Sessions
Computer control
ACLs
Trusts
AD CS
```

Conceptually:

```text
Kerberos Relationship
        |
        v
BloodHound
        |
        v
Attack Path Context
```

---

# BloodHound Delegation Analysis

BloodHound may expose relationships related to:

```text
AllowedToDelegate
AllowedToAct
Unconstrained delegation
Computer control
Service accounts
```

Always verify the underlying AD configuration.

---

# Kerberos Trusts

Kerberos authentication can operate across trusted Active Directory domains.

Conceptually:

```text
DOMAIN A
   |
   | Trust
   v
DOMAIN B
```

Cross-domain authentication may involve referral tickets.

---

# Referral Tickets

When a user needs a service in another trusted domain:

```text
User in Domain A
       |
       v
KDC Domain A
       |
       v
Referral
       |
       v
KDC Domain B
       |
       v
Service Ticket
```

Trust configuration therefore affects Kerberos attack paths.

---

# Trust Analysis

Review:

```text
Trust direction
Trust type
Transitivity
SID filtering
Selective authentication
Cross-domain group membership
Cross-domain ACLs
```

See:

```text
active-directory/trusts.md
```

---

# Encryption Types

Modern Kerberos environments commonly use AES encryption.

Relevant types include:

```text
AES256
AES128
RC4-HMAC
```

Legacy environments may support older encryption types.

The actual types available depend on:

```text
Domain configuration
Account configuration
Operating system
Service configuration
Password history / account age
Group Policy
```

---

# Why Encryption Types Matter

Encryption type affects:

```text
Compatibility
Security
Ticket behaviour
Kerberoasting resistance
Detection
Legacy-system support
```

Older encryption types should be investigated rather than automatically treated as exploitable vulnerabilities.

---

# RC4

RC4 support may exist for compatibility with older systems.

Security reviews should determine:

```text
Why is RC4 enabled?

Which accounts use it?

Which services require it?

Can AES be used instead?

Is RC4 usage expected?
```

---

# AES

Modern environments should generally prefer:

```text
AES128
AES256
```

where supported.

The exact Kerberos encryption policy should align with Microsoft guidance and application compatibility requirements.

---

# Account Encryption Configuration

PowerShell can inspect relevant account properties.

For example:

```powershell
Get-ADUser svc_sql \
    -Properties msDS-SupportedEncryptionTypes |
    Select-Object SamAccountName,
                  msDS-SupportedEncryptionTypes
```

Interpret the resulting value carefully because it is represented as a bitmask.

---

# Kerberos Ticket Lifetime

Kerberos tickets have defined lifetimes.

Relevant policy includes:

```text
Maximum lifetime for user ticket
Maximum lifetime for service ticket
Maximum lifetime for user ticket renewal
Maximum tolerance for computer clock synchronisation
```

Review domain Kerberos policy rather than assuming defaults.

---

# Kerberos Policy - Windows

Example:

```powershell
net accounts /domain
```

For more complete policy review, use:

```text
Group Policy
Domain policy
PowerShell
Security policy tooling
```

---

# Authentication Failure Codes

Kerberos failures can reveal useful diagnostic information.

Common issues include:

```text
Principal unknown
Preauthentication failed
Clock skew
Ticket expired
SPN unknown
KDC unreachable
Encryption type unsupported
```

Do not rely solely on a tool's friendly error message.

When needed, inspect:

```text
Windows event logs
Network traces
Kerberos client output
Tool debug output
```

---

# Useful Kerberos Errors

Examples include:

```text
KDC_ERR_C_PRINCIPAL_UNKNOWN
KDC_ERR_S_PRINCIPAL_UNKNOWN
KDC_ERR_PREAUTH_FAILED
KDC_ERR_PREAUTH_REQUIRED
KRB_AP_ERR_SKEW
KRB_AP_ERR_TKT_EXPIRED
KDC_ERR_ETYPE_NOSUPP
```

These are extremely useful during troubleshooting.

---

# KDC_ERR_C_PRINCIPAL_UNKNOWN

Conceptually:

```text
Client principal not found
```

Check:

```text
Username
Domain
Realm
Account existence
```

---

# KDC_ERR_S_PRINCIPAL_UNKNOWN

Conceptually:

```text
Service principal not found
```

Check:

```text
SPN
Hostname
FQDN
Service registration
Duplicate / missing SPNs
```

---

# KDC_ERR_PREAUTH_FAILED

Check:

```text
Password
Key
Encryption type
Account state
Time
```

---

# KRB_AP_ERR_SKEW

Usually indicates clock skew.

Check:

```bash
date
```

and compare with the Domain Controller.

---

# KDC_ERR_ETYPE_NOSUPP

Indicates an encryption compatibility problem.

Investigate:

```text
Client supported encryption
Account supported encryption
Domain policy
Service configuration
Legacy systems
```

---

# Kerberos Enumeration Workflow

A low-impact assessment workflow:

```text
Domain
   |
   v
KDC
   |
   v
DNS
   |
   v
Users
   |
   v
SPNs
   |
   v
Preauthentication
   |
   v
Delegation
   |
   v
Encryption Types
   |
   v
Trusts
   |
   v
BloodHound Context
```

Only after understanding this information should higher-impact validation be considered.

---

# Windows Enumeration Workflow

```powershell
whoami
```

```powershell
whoami /groups
```

```powershell
echo $env:USERDOMAIN
```

```powershell
nltest /dsgetdc:example.local
```

```powershell
klist
```

```powershell
setspn -Q */*
```

Then move to:

```text
PowerShell AD module
PowerView
BloodHound
```

as appropriate.

---

# Linux Enumeration Workflow

```bash
dig SRV _kerberos._tcp.example.local
```

```bash
nc -vz dc01.example.local 88
```

```bash
ldapsearch ...
```

```bash
impacket-GetUserSPNs ...
```

```bash
impacket-findDelegation ...
```

Then correlate with:

```text
NetExec
BloodHound
BloodHound.py
```

---

# Tool Map

```text
Kerberos
   |
   +--> Native Windows
   |      |
   |      +--> klist
   |      +--> setspn
   |      +--> nltest
   |
   +--> Linux Native
   |      |
   |      +--> kinit
   |      +--> klist
   |      +--> ldapsearch
   |
   +--> Impacket
   |      |
   |      +--> getTGT
   |      +--> getST
   |      +--> GetUserSPNs
   |      +--> GetNPUsers
   |      +--> findDelegation
   |
   +--> NetExec
   |
   +--> PowerView
   |
   +--> BloodHound
   |
   +--> Certipy
```

---

# Impacket Tool Selection

```text
Need TGT?
   |
   +--> getTGT

Need service ticket?
   |
   +--> getST

Need SPN enumeration?
   |
   +--> GetUserSPNs

Need preauthentication analysis?
   |
   +--> GetNPUsers

Need delegation enumeration?
   |
   +--> findDelegation
```

Use the dedicated technique pages before performing active ticket operations.

---

# Kerberos and AD CS

Certificates can also provide authentication material in Active Directory environments.

Conceptually:

```text
Certificate
    |
    v
PKINIT
    |
    v
Kerberos Authentication
    |
    v
TGT
```

This creates an important relationship between:

```text
AD CS
   +
Kerberos
```

Detailed certificate authentication belongs in the AD CS section.

---

# PKINIT

PKINIT extends Kerberos to support public-key authentication during initial authentication.

Instead of relying only on:

```text
Password-derived key
```

authentication can involve:

```text
Certificate
+
Private Key
```

This is why compromised authentication certificates can sometimes function as domain credentials.

---

# Kerberos Security Review

Review:

```text
Preauthentication disabled accounts
Weak service-account passwords
Privileged SPN accounts
Legacy encryption
Delegation
RBCD
KRBTGT security
Ticket lifetime
Privileged sessions
Trusts
AD CS authentication
Service account privilege
SPN hygiene
```

---

# High-Risk Service Accounts

Pay particular attention to accounts that are:

```text
Kerberoastable
        +
Privileged
```

For example:

```text
Service account
     |
     +--> SPN
     |
     +--> Domain Admin
```

This represents substantially more risk than a low-privileged service account.

---

# Service Account Review

For each service account determine:

```text
What service uses it?

Does it require a user account?

Could gMSA be used?

Is it privileged?

Does it have interactive logon rights?

Is the password strong?

How old is the password?

Which encryption types are supported?

Where is the account used?
```

---

# gMSA

Group Managed Service Accounts can reduce the risks associated with manually managed service-account passwords.

Advantages include:

```text
Automatically managed passwords
Long random passwords
Reduced human password reuse
Service-focused identity management
```

See:

```text
active-directory/gmsa.md
```

---

# Detection

Kerberos is heavily used in normal Active Directory environments.

Therefore detection should focus on:

```text
Context
Volume
Sequence
Encryption
Account
Service
Source
Timing
```

rather than:

```text
Kerberos event exists
```

---

# Important Windows Events

Commonly useful Kerberos-related events include:

```text
4768    Kerberos authentication ticket requested
4769    Kerberos service ticket requested
4770    Kerberos service ticket renewed
4771    Kerberos preauthentication failed
4772    Kerberos authentication ticket request failed
```

Other logon and account events may provide additional context.

---

# Event 4768

```text
A Kerberos authentication ticket was requested
```

Useful fields may include:

```text
Account
Client address
Ticket encryption type
Preauthentication information
Result
```

---

# Event 4769

```text
A Kerberos service ticket was requested
```

Useful for analysing:

```text
Service ticket requests
SPNs
Encryption types
Client systems
Unusual request volume
```

---

# Event 4771

```text
Kerberos preauthentication failed
```

Potential causes include:

```text
Incorrect password
Stale credentials
Password spraying
Misconfigured services
Clock problems
Attack activity
```

Context is essential.

---

# Kerberoasting Detection

Potential indicators include:

```text
Large number of TGS requests
Many distinct SPNs
Unusual requesting account
Unusual requesting host
RC4 service-ticket requests
Privileged service accounts targeted
Rapid service-ticket enumeration
```

A single TGS request is normal.

Detection should correlate:

```text
Account
+
Host
+
Volume
+
Time
+
Encryption
+
Target SPNs
```

---

# AS-REP Roasting Detection

Review:

```text
Accounts with preauthentication disabled
Unexpected AS requests
Source hosts
Account configuration changes
```

The strongest mitigation is generally:

```text
Enable Kerberos preauthentication
```

unless a documented compatibility requirement exists.

---

# Ticket Theft Detection

Potential telemetry may include:

```text
Suspicious access to authentication processes
Ticket cache access
Unusual Kerberos authentication
Tickets used from unexpected systems
Service requests inconsistent with normal logon flow
```

Endpoint and Domain Controller telemetry should be correlated.

---

# Forged Ticket Detection

Potential indicators may include:

```text
Abnormal ticket lifetime
Unexpected encryption types
Unusual PAC characteristics
Service requests without expected authentication sequence
Unexpected account/service combinations
Authentication using disabled/nonexistent identities
```

Detection depends on the ticket type and environment.

---

# Golden Ticket

A Golden Ticket is a forged TGT created using compromised KRBTGT key material.

Conceptually:

```text
KRBTGT Key
    |
    v
Forge TGT
    |
    v
Domain Authentication Material
```

This represents domain-level compromise.

Detailed discussion belongs in:

```text
active-directory/kerberos-tickets.md
```

---

# Silver Ticket

A Silver Ticket is a forged service ticket created using key material associated with a specific service account.

Conceptually:

```text
Service Key
    |
    v
Forge Service Ticket
    |
    v
Specific Service
```

Its scope is generally narrower than a Golden Ticket.

---

# Golden vs Silver

```text
Golden Ticket
    |
    +--> Forged TGT
    +--> KRBTGT key
    +--> Domain-wide significance
    +--> Used to obtain service tickets

Silver Ticket
    |
    +--> Forged service ticket
    +--> Service-account key
    +--> Specific service scope
```

---

# Kerberos ATT&CK Mapping

Relevant MITRE ATT&CK technique:

```text
T1558 - Steal or Forge Kerberos Tickets
```

Sub-techniques include:

```text
T1558.001 - Golden Ticket
T1558.002 - Silver Ticket
T1558.003 - Kerberoasting
T1558.004 - AS-REP Roasting
T1558.005 - Ccache Files
```

Additional techniques may apply depending on how credentials or tickets are obtained and used.

---

# Purple Team Opportunities

Kerberos testing is well suited to purple team exercises.

Example:

```text
Red Team
   |
   v
Controlled TGS Requests
   |
   v
Blue Team
   |
   v
4769 Analysis
   |
   v
Detection Review
   |
   v
Rule Improvement
```

Another:

```text
Known Test Account
      |
      v
Controlled Authentication Failure
      |
      v
4771
      |
      v
Detection
      |
      v
Alert Validation
```

---

# Detection Engineering Questions

Ask:

```text
Can we identify unusual TGS request volume?

Can we identify RC4 where AES is expected?

Can we identify privileged SPN accounts?

Can we identify accounts with preauthentication disabled?

Can we identify abnormal ticket lifetimes?

Can we correlate TGT and TGS activity?

Can we identify unusual Kerberos clients?

Can we detect suspicious ticket-cache access?

Can we detect changes to delegation?
```

---

# Remediation

Kerberos remediation depends on the underlying weakness.

---

# Preauthentication

Prefer:

```text
Kerberos preauthentication enabled
```

Audit exceptions.

---

# Service Accounts

Prefer:

```text
Long random passwords

gMSA where appropriate

Least privilege

No unnecessary Domain Admin membership

No unnecessary interactive logon

AES support

Regular review
```

---

# Encryption

Where compatibility allows:

```text
Prefer modern AES encryption

Reduce legacy RC4 dependency

Remove obsolete encryption support
```

Test application compatibility before making production changes.

---

# Delegation

Review and remove unnecessary:

```text
Unconstrained delegation

Constrained delegation

RBCD relationships

Protocol transition
```

Apply delegation only where required.

---

# KRBTGT Protection

Treat KRBTGT authentication material as Tier-0.

If compromise is confirmed, recovery may require controlled KRBTGT password rotation according to Microsoft's incident-recovery guidance.

Do not perform KRBTGT resets casually.

---

# Privileged Accounts

Apply administrative tiering.

Avoid privileged accounts authenticating to:

```text
User workstations
Untrusted servers
Lower-tier systems
```

where possible.

This reduces credential and ticket exposure.

---

# SPN Hygiene

Regularly review:

```text
Duplicate SPNs
Unused SPNs
Stale service accounts
Privileged service accounts
Old passwords
Legacy encryption
```

---

# Evidence

Create:

```bash
mkdir -p evidence/kerberos/{enumeration,tickets,logs,pcaps,screenshots}
```

Suggested structure:

```text
evidence/
└── kerberos/
    ├── enumeration/
    ├── tickets/
    ├── logs/
    ├── pcaps/
    └── screenshots/
```

Treat ticket material as sensitive.

---

# Evidence to Record

For Kerberos testing record:

```text
Date/time
Domain
Domain Controller
Client
Account
SPN
Ticket type
Encryption type
Tool
Tool version
Command
Result
Relevant event IDs
Scope
```

---

# Do Not Store Secrets in Reports

Avoid placing:

```text
Passwords
NTLM hashes
AES keys
Raw tickets
Private keys
Credential caches
```

directly into final client reports unless specifically required and appropriately protected.

---

# Reporting

Report the underlying security issue rather than the existence of Kerberos.

Bad:

```text
Kerberoasting is possible.
```

Better:

```text
A privileged service account uses a password-derived
Kerberos service key and can be requested by standard
domain users. The account's password policy increases
the risk of offline password recovery.
```

---

# Reporting Preauthentication

Bad:

```text
AS-REP Roastable user found.
```

Better:

```text
Kerberos preauthentication is disabled for the affected
domain account, allowing authentication response material
to be requested without first proving knowledge of the
account password.
```

---

# Reporting Delegation

Describe:

```text
Delegating principal
Target service
Delegation type
Required permissions
Potential identity impersonation
Affected systems
Business impact
```

---

# Common Mistakes

## Treating Kerberos as an Attack

Kerberos itself is not a vulnerability.

```text
Kerberos
   !=
Finding
```

The finding is the insecure configuration or credential condition.

---

## Requesting Tickets Before Enumeration

Prefer:

```text
Enumerate
   |
   v
Understand
   |
   v
Prioritise
   |
   v
Request Only What Is Necessary
```

---

## Ignoring DNS

Many apparent Kerberos problems are actually:

```text
DNS problems
```

---

## Ignoring Time

Always check:

```bash
date
```

before spending significant time debugging Kerberos.

---

## Using IP Addresses Everywhere

Kerberos service identity depends heavily on:

```text
Hostnames
FQDNs
SPNs
```

Using IP addresses can change authentication behaviour.

---

## Assuming Every SPN Is High Risk

An SPN means:

```text
Service identity exists
```

not:

```text
Password is weak
```

Assess:

```text
Account privilege
Password strength
Encryption
Service exposure
```

---

## Assuming RC4 Means Compromise

RC4 usage may represent:

```text
Legacy compatibility
Configuration debt
Older service account
```

Investigate and report the actual risk.

---

## Treating Ticket Files Casually

A ticket or ccache may be:

```text
Authentication material
```

Protect it accordingly.

---

# Troubleshooting

## Cannot Find KDC

Check:

```bash
dig SRV _kerberos._tcp.example.local
```

---

## Cannot Resolve DC

```bash
dig dc01.example.local
```

---

## Port 88 Closed

```bash
nc -vz dc01.example.local 88
```

Check:

```text
Routing
Firewall
VPN
Pivot
Target IP
```

---

## Clock Skew

```bash
date
```

Windows:

```powershell
w32tm /query /status
```

---

## SPN Error

Check:

```powershell
setspn -Q <SPN>
```

---

## Duplicate SPN

```powershell
setspn -X
```

---

## Ticket Expired

Linux:

```bash
klist
```

Windows:

```powershell
klist
```

---

## Ccache Not Found

```bash
echo "$KRB5CCNAME"
```

Then:

```bash
ls -l "$KRB5CCNAME"
```

if the variable represents a file path.

---

## Impacket Kerberos Fails

Check:

```text
KRB5CCNAME
DNS
FQDN
Domain
DC
Time
Ticket validity
Tool -k option
-no-pass where appropriate
```

---

# Pivoting and Kerberos

Kerberos through a pivot requires more than TCP connectivity.

Check:

```text
Routing
DNS
Kerberos
LDAP
SMB
RPC where required
Time
```

Conceptually:

```text
Kali
 |
 v
Pivot
 |
 v
Internal DNS
 |
 v
Domain Controller
 |
 v
Kerberos
```

---

# TUN-Based Pivoting

TUN-based routing can simplify Kerberos-aware tools because they can communicate with internal services using normal network semantics.

Still verify DNS separately.

```bash
ip route
```

```bash
dig dc01.example.local
```

```bash
nc -vz dc01.example.local 88
```

---

# Kerberos Through SOCKS

SOCKS support depends on the application and protocol behaviour.

Kerberos can become difficult when:

```text
DNS resolution occurs locally
UDP is required
Tool lacks proxy support
Multiple protocols are involved
```

Where authorised and appropriate, routed/TUN access may be easier than forcing every Kerberos workflow through a SOCKS proxy.

---

# Assessment Workflow

```text
                       KERBEROS ASSESSMENT
                               |
                               v
                             SCOPE
                               |
                               v
                          DOMAIN / REALM
                               |
                               v
                              DNS
                               |
                               v
                              KDC
                               |
                               v
                             TIME
                               |
                               v
                         PRINCIPALS
                               |
               +---------------+---------------+
               |                               |
               v                               v
             USERS                            SPNs
               |                               |
               v                               v
       PREAUTHENTICATION               SERVICE ACCOUNTS
               |                               |
               +---------------+---------------+
                               |
                               v
                           ENCRYPTION
                               |
                               v
                           DELEGATION
                               |
                               v
                             TRUSTS
                               |
                               v
                          BLOODHOUND
                               |
                               v
                        RISK ANALYSIS
                               |
                               v
                    AUTHORISED VALIDATION
                               |
                               v
                           EVIDENCE
                               |
                               v
                            REPORT
```

---

# Quick Enumeration Workflow

```text
1. Identify domain
2. Identify Domain Controller
3. Verify DNS
4. Verify port 88
5. Verify time
6. Enumerate users
7. Enumerate SPNs
8. Identify preauthentication-disabled accounts
9. Enumerate delegation
10. Review encryption
11. Review trusts
12. Correlate BloodHound
13. Prioritise
14. Validate only where necessary
```

---

# Kerberos Decision Tree

```text
Kerberos Assessment
        |
        v
Can Resolve Domain?
        |
    +---+---+
    |       |
   No      Yes
    |       |
    v       v
 Fix DNS   Port 88?
             |
         +---+---+
         |       |
        No      Yes
         |       |
         v       v
      Routing   Time OK?
                  |
              +---+---+
              |       |
             No      Yes
              |       |
              v       v
           Fix Time   Enumerate
                         |
                         v
                       SPNs?
                         |
                         +--> Service Account Review
                         |
                         v
                  Preauth Disabled?
                         |
                         +--> AS-REP Risk
                         |
                         v
                    Delegation?
                         |
                         +--> Delegation Analysis
                         |
                         v
                     Trusts?
                         |
                         +--> Cross-Domain Analysis
```

---

# Testing Checklist

## Environment

```text
[ ] Scope confirmed
[ ] Domain identified
[ ] Realm identified
[ ] Domain Controller identified
[ ] DNS configured
[ ] Port 88 reachable
[ ] Time synchronised
```

## Authentication

```text
[ ] Current identity understood
[ ] Current tickets reviewed
[ ] Kerberos vs NTLM behaviour understood
[ ] Encryption types considered
[ ] Ticket lifetimes reviewed where relevant
```

## Accounts

```text
[ ] Users enumerated
[ ] SPN accounts identified
[ ] Privileged service accounts identified
[ ] Preauthentication-disabled accounts identified
[ ] gMSA usage reviewed
```

## Delegation

```text
[ ] Unconstrained delegation reviewed
[ ] Constrained delegation reviewed
[ ] RBCD reviewed
[ ] S4U relationships reviewed
```

## Trusts

```text
[ ] Domain trusts reviewed
[ ] Trust direction understood
[ ] Cross-domain relationships reviewed
```

## Graph Analysis

```text
[ ] BloodHound data reviewed
[ ] Kerberos-related edges reviewed
[ ] Owned principals marked
[ ] Delegation paths reviewed
```

## Validation

```text
[ ] Ticket requests limited to necessary validation
[ ] State-changing actions separately authorised
[ ] High-impact techniques separately approved
[ ] Operational impact considered
```

## Evidence

```text
[ ] Commands recorded
[ ] Tool versions recorded
[ ] Relevant events recorded
[ ] Sensitive tickets protected
[ ] Results timestamped
```

## Reporting

```text
[ ] Underlying condition described
[ ] Kerberos itself not presented as vulnerability
[ ] Prerequisites documented
[ ] Impact documented
[ ] Remediation addresses root cause
```

---

# Quick Reference

```text
DNS
    dig SRV _kerberos._tcp.example.local

KDC
    nc -vz dc01.example.local 88

Linux TGT
    kinit alice@EXAMPLE.LOCAL

Linux tickets
    klist

Destroy Linux cache
    kdestroy

Windows tickets
    klist

Windows SPNs
    setspn -Q */*

Specific SPN
    setspn -Q MSSQLSvc/*

Duplicate SPNs
    setspn -X

Account SPNs
    setspn -L EXAMPLE\svc_sql

Impacket SPNs
    impacket-GetUserSPNs \
        example.local/alice:'Password' \
        -dc-ip 10.10.20.10

Delegation
    impacket-findDelegation \
        example.local/alice:'Password' \
        -dc-ip 10.10.20.10

Impacket TGT help
    impacket-getTGT -h

Ccache
    export KRB5CCNAME=/path/to/user.ccache

Check ccache
    klist
```

---

# Kerberos Attack Surface

```text
                           KERBEROS
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
    Authentication           SPNs             Delegation
          |                   |                   |
          v                   v                   v
    Preauthentication    Service Accounts    Unconstrained
          |                   |               Constrained
          v                   v                  RBCD
      AS-REP Risk       Kerberoast Risk          S4U
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                           TICKETS
                              |
               +--------------+--------------+
               |                             |
               v                             v
              TGT                      Service Ticket
               |                             |
               v                             v
        Golden Ticket                 Silver Ticket
               |
               +--------------+
                              |
                              v
                            TRUSTS
                              |
                              v
                       CROSS-DOMAIN AUTH
```

---

# Final Model

```text
Password / Key / Certificate
            |
            v
          AS-REQ
            |
            v
            KDC
            |
            v
          AS-REP
            |
            v
           TGT
            |
            v
         TGS-REQ
            |
            +--> SPN
            |
            v
            KDC
            |
            v
         TGS-REP
            |
            v
      Service Ticket
            |
            v
         Service
            |
            v
     Authorisation
```

From a security-testing perspective:

```text
Kerberos
   |
   +--> Who can authenticate?
   |
   +--> Which accounts have SPNs?
   |
   +--> Is preauthentication required?
   |
   +--> Which encryption types are used?
   |
   +--> Which service accounts are privileged?
   |
   +--> Where is delegation configured?
   |
   +--> Which tickets exist?
   |
   +--> Which trusts exist?
   |
   +--> Can certificates provide Kerberos authentication?
   |
   v
Risk Analysis
```

The key principle is:

```text
Understand the authentication relationship first.

Enumerate before requesting unnecessary tickets.

Treat tickets as credentials.

Validate configuration before attempting exploitation.

Report the underlying identity weakness rather than the tool or technique.
```

---

# Related Notes

```text
active-directory/index.md
active-directory/methodology.md
active-directory/enumeration.md
active-directory/ntlm.md
active-directory/password-spraying.md
active-directory/asrep-roasting.md
active-directory/kerberoasting.md
active-directory/pass-the-hash.md
active-directory/overpass-the-hash.md
active-directory/pass-the-key.md
active-directory/kerberos-tickets.md
active-directory/unconstrained-delegation.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
active-directory/trusts.md
active-directory/bloodhound.md
active-directory/impacket.md
active-directory/netexec.md
active-directory/adcs/index.md
```

---

# Related Cheatsheets

```text
cheatsheets/active-directory.md
cheatsheets/netexec.md
cheatsheets/impacket.md
cheatsheets/bloodhound.md
cheatsheets/windows.md
cheatsheets/powershell.md
cheatsheets/networking.md
```

---

# References

## Microsoft - Kerberos Authentication Overview

[Microsoft - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

## Microsoft - Kerberos Technical Documentation

[Microsoft Learn - microsoft kerberos](https://learn.microsoft.com/en-us/windows/win32/secauthn/microsoft-kerberos){ target="_blank" rel="noopener noreferrer" }

## Microsoft - Key Distribution Center

[Microsoft - Key Distribution Center](https://learn.microsoft.com/en-us/windows/win32/secauthn/key-distribution-center){ target="_blank" rel="noopener noreferrer" }

## Microsoft - klist

[Microsoft - klist](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/klist){ target="_blank" rel="noopener noreferrer" }

## Microsoft - setspn

[Microsoft - setspn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn){ target="_blank" rel="noopener noreferrer" }

## Fortra Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

## MITRE ATT&CK - Steal or Forge Kerberos Tickets

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

## MITRE ATT&CK - Golden Ticket

[MITRE ATT&CK - Golden Ticket](https://attack.mitre.org/techniques/T1558/001/){ target="_blank" rel="noopener noreferrer" }

## MITRE ATT&CK - Silver Ticket

[MITRE ATT&CK - Silver Ticket](https://attack.mitre.org/techniques/T1558/002/){ target="_blank" rel="noopener noreferrer" }

## MITRE ATT&CK - Kerberoasting

[MITRE ATT&CK - Kerberoasting](https://attack.mitre.org/techniques/T1558/003/){ target="_blank" rel="noopener noreferrer" }

## MITRE ATT&CK - AS-REP Roasting

[MITRE ATT&CK - AS-REP Roasting](https://attack.mitre.org/techniques/T1558/004/){ target="_blank" rel="noopener noreferrer" }

## MITRE ATT&CK - Ccache Files

[MITRE ATT&CK - Ccache Files](https://attack.mitre.org/techniques/T1558/005/){ target="_blank" rel="noopener noreferrer" }

---

# Final Quick Reference

```text
                           KERBEROS
                              |
                              v
                         DNS + TIME
                              |
                              v
                             KDC
                         TCP/UDP 88
                              |
                 +------------+------------+
                 |                         |
                 v                         v
                AS                        TGS
                 |                         |
                 v                         v
              AS-REQ                   TGS-REQ
                 |                         |
                 v                         |
              AS-REP                      SPN
                 |                         |
                 v                         v
                TGT                    TGS-REP
                 |                         |
                 |                         v
                 |                  Service Ticket
                 |                         |
                 +------------+------------+
                              |
                              v
                          AUTHENTICATION
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       PREAUTH               SPNs             DELEGATION
          |                   |                   |
          v                   v                   v
       AS-REP            Kerberoasting      Unconstrained
       Roasting                             Constrained
                                                RBCD
                                                S4U
                              |
                              v
                           TICKETS
                              |
               +--------------+--------------+
               |                             |
               v                             v
             TGT                         SERVICE
               |                           TICKET
               v                             |
        Golden Ticket                        v
                                      Silver Ticket
                              |
                              v
                            TRUSTS
                              |
                              v
                       CROSS-DOMAIN AUTH
```
