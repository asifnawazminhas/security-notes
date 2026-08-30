# Kerberos S4U

Service for User (S4U) is a set of Microsoft Kerberos extensions that allow a service to obtain Kerberos service tickets on behalf of another user.

S4U is fundamental to understanding:

```text
Kerberos Constrained Delegation
Resource-Based Constrained Delegation
Protocol Transition
Service Impersonation
```

The two primary S4U extensions are:

```text
S4U2Self
S4U2Proxy
```

A simplified model is:

```text
                    S4U
                     |
             +-------+-------+
             |               |
             v               v
         S4U2Self         S4U2Proxy
             |               |
             v               v
       Ticket to Self    Ticket to Another
       for a User        Service for a User
```

Microsoft's S4U specification defines both extensions as mechanisms allowing a service to request a ticket from the Key Distribution Center (KDC) on behalf of a user.

The distinction is:

```text
S4U2Self
    |
    v
Service asks:
"Give me a ticket to myself
representing this user."


S4U2Proxy
    |
    v
Service asks:
"Give me a ticket to another
service representing this user."
```

S4U is legitimate Kerberos functionality.

Its security importance comes from the fact that delegation-enabled services are deliberately trusted to act on behalf of other identities.

If such a service or its authentication material becomes compromised, the attacker may inherit that delegation capability.

!!! warning "Authorised testing only"
    S4U testing can involve requesting Kerberos tickets representing other users and may result in access to backend services under those identities. Only test accounts, services, systems, and delegation relationships explicitly included in the engagement scope. Prefer dedicated test identities and minimum-impact service authentication rather than privileged-user impersonation or remote command execution.

---

# Why S4U Exists

Consider a multi-tier application:

```text
User
 |
 v
WEB01
 |
 v
SQL01
```

The application may need:

```text
WEB01
```

to access:

```text
SQL01
```

while preserving the user's identity.

The desired model is:

```text
Alice
 |
 v
WEB01
 |
 | acts as Alice
 v
SQL01
```

This creates an authentication problem.

The backend needs to know:

```text
Who is the user?
```

rather than simply seeing:

```text
WEB01
```

S4U provides mechanisms allowing the service to obtain Kerberos tickets containing the user's identity.

---

# S4U Architecture

A simplified architecture is:

```text
                     Active Directory
                           |
                           v
                          KDC
                           |
              +------------+------------+
              |                         |
              v                         v
          S4U2Self                  S4U2Proxy
              |                         |
              v                         v
      User -> Front-End        User -> Back-End
          Service Ticket          Service Ticket
```

The important components are:

```text
User
Service 1
Service 2
KDC
Service Principal Names
Delegation Configuration
Kerberos Tickets
```

---

# S4U Is a Kerberos Extension

S4U does not replace Kerberos.

It extends the normal Kerberos service-ticket model.

Normal Kerberos:

```text
User
 |
 v
KDC
 |
 v
Service Ticket
 |
 v
Service
```

S4U:

```text
Service
 |
 | requests on behalf of User
 v
KDC
 |
 v
Service Ticket
 |
 v
Service
```

The service therefore becomes an active participant in obtaining authentication material representing the user.

---

# Normal Kerberos Refresher

A simplified normal Kerberos flow is:

```text
User
 |
 | AS-REQ
 v
KDC
 |
 | AS-REP
 v
TGT
 |
 | TGS-REQ
 v
KDC
 |
 | TGS-REP
 v
Service Ticket
 |
 v
Application Service
```

The user obtains:

```text
TGT
```

and then requests:

```text
Service Ticket
```

for a particular SPN.

---

# S4U Changes the Requesting Principal

With S4U, the service can request tickets involving another user's identity.

Conceptually:

```text
Service
 |
 | S4U request
 |
 | User = Alice
 v
KDC
 |
 v
Ticket containing
Alice's identity
```

The ticket is still issued by the legitimate KDC.

This is important.

S4U is not:

```text
Forging arbitrary Kerberos tickets
```

It is:

```text
Requesting KDC-issued tickets
using delegation functionality
```

---

# S4U2Self

S4U2Self means:

```text
Service for User to Self
```

It allows a service to obtain a service ticket to itself representing another user.

The basic model is:

```text
Service
 |
 | S4U2Self
 | User = Alice
 v
KDC
 |
 v
Service Ticket
 |
 v
Alice -> Service
```

The destination service is the requesting service itself.

---

# Why S4U2Self Exists

A service may authenticate a user using something other than Kerberos.

For example:

```text
User
 |
 | Forms Authentication
 v
WEB01
```

or:

```text
User
 |
 | Certificate Authentication
 v
WEB01
```

or another application-specific authentication mechanism.

WEB01 may still need Windows authorization information for the user.

S4U2Self allows:

```text
WEB01
 |
 | User = Alice
 v
KDC
 |
 v
Alice -> WEB01
Service Ticket
```

The service can then obtain a Kerberos representation of Alice.

---

# Protocol Transition

This capability is closely associated with:

```text
Protocol Transition
```

The conceptual transition is:

```text
Non-Kerberos Authentication
          |
          v
       Service
          |
          v
       S4U2Self
          |
          v
Kerberos Representation
      of the User
```

For example:

```text
Alice
 |
 | Web Forms Authentication
 v
WEB01
 |
 | S4U2Self
 v
KDC
 |
 v
Kerberos Ticket
Alice -> WEB01
```

The user's original authentication to WEB01 did not have to be Kerberos for the application architecture to obtain a Kerberos representation of that user.

---

# S4U2Self Flow

A simplified protocol flow is:

```text
             Service
                |
                | Has its own Kerberos
                | authentication context
                v
               KDC
                |
                |
                | S4U2Self:
                | "Ticket to me as Alice"
                |
                v
               KDC
                |
                | Service Ticket
                v
         Alice -> Service
```

The resulting ticket represents:

```text
Alice
```

but targets:

```text
Service
```

---

# User Does Not Supply a Password to S4U2Self

An important distinction is:

```text
S4U2Self
    |
    X
Requires Alice's password
```

The requesting service does not authenticate as Alice using Alice's password.

Instead:

```text
Service authenticates as itself
        |
        v
Requests ticket representing Alice
        |
        v
KDC applies S4U policy
```

This is what makes the service's delegation privileges security-sensitive.

---

# The User's Key Is Not Required by the Service

The service does not need:

```text
Alice's NT hash
Alice's AES key
Alice's password
```

to perform a legitimate S4U request.

Instead, it relies on:

```text
Its own identity
        +
KDC trust
        +
Delegation policy
```

---

# S4U2Self Ticket Identity

The resulting service ticket contains the user's identity and authorization information.

Conceptually:

```text
Ticket
 |
 +--> Client: Alice
 |
 +--> Service: HTTP/web01
 |
 +--> Authorization Data
 |
 +--> Lifetime
 |
 +--> Flags
```

The ticket therefore allows the service to reason about the user's Windows authorization context.

---

# S4U2Proxy

S4U2Proxy means:

```text
Service for User to Proxy
```

It allows a service to request a service ticket to another service on behalf of the user.

Conceptually:

```text
Alice
 |
 v
Service 1
 |
 | S4U2Proxy
 v
KDC
 |
 v
Alice -> Service 2
```

This is the Kerberos mechanism underlying constrained delegation.

---

# Why S4U2Proxy Exists

Consider:

```text
Alice
 |
 v
WEB01
 |
 v
SQL01
```

WEB01 needs to access SQL01:

```text
as Alice
```

rather than:

```text
as WEB01
```

S4U2Proxy allows WEB01 to obtain:

```text
Alice -> SQL01
```

subject to the KDC's delegation policy.

---

# S4U2Proxy Flow

A simplified model is:

```text
Alice -> WEB01
Service Ticket
       |
       v
     WEB01
       |
       | S4U2Proxy
       |
       | Additional Ticket:
       | Alice -> WEB01
       v
      KDC
       |
       v
Alice -> SQL01
Service Ticket
```

The backend receives a normal KDC-issued Kerberos service ticket representing Alice.

---

# Additional Ticket

S4U2Proxy uses a service ticket representing the user to the first service as part of the request.

Conceptually:

```text
TGS-REQ
 |
 +--> Requesting Service
 |
 +--> Target Service
 |
 +--> User's Ticket to Service 1
 |
 +--> S4U Delegation Information
```

The KDC then evaluates whether delegation to the requested second service is permitted.

---

# Complete S4U Flow

A common application flow is:

```text
Alice
 |
 | Non-Kerberos authentication
 v
WEB01
 |
 | S4U2Self
 v
KDC
 |
 v
Alice -> WEB01
 |
 | S4U2Proxy
 v
KDC
 |
 v
Alice -> SQL01
 |
 v
SQL01
```

This combines:

```text
Protocol Transition
        +
Constrained Delegation
```

---

# S4U2Self vs S4U2Proxy

| Property | S4U2Self | S4U2Proxy |
|---|---|---|
| Meaning | Service for User to Self | Service for User to Proxy |
| Ticket destination | Requesting service | Another service |
| Represents another user | Yes | Yes |
| Backend delegation | No by itself | Yes |
| Used for protocol transition | Central | Often follows it |
| Used by constrained delegation | Supporting mechanism | Central |

The easiest way to remember them is:

```text
S4U2Self
    =
User -> Me


S4U2Proxy
    =
User -> Another Service
```

---

# S4U2Self Does Not Equal S4U2Proxy

Obtaining:

```text
Alice -> WEB01
```

does not automatically mean WEB01 can obtain:

```text
Alice -> DC01
```

The second operation requires the appropriate delegation conditions.

Therefore:

```text
S4U2Self Capability
       |
       X
Unlimited Delegation
```

---

# Delegation Policy

S4U2Proxy is constrained by policy.

The KDC determines whether the requesting service may delegate to the requested destination.

The two important Active Directory delegation models are:

```text
Traditional Constrained Delegation
```

and:

```text
Resource-Based Constrained Delegation
```

---

# Traditional Constrained Delegation

Traditional KCD stores the allowed destinations on the delegating account.

The important attribute is:

```text
msDS-AllowedToDelegateTo
```

Conceptually:

```text
WEB01
 |
 v
msDS-AllowedToDelegateTo
 |
 +--> MSSQLSvc/sql01
 |
 +--> cifs/fileserver01
```

The question is:

```text
Where may WEB01 delegate?
```

---

# RBCD

Resource-Based Constrained Delegation reverses the trust direction.

The important attribute is:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

The configuration exists on the backend resource.

```text
SERVER01
 |
 v
msDS-AllowedToActOnBehalfOfOtherIdentity
 |
 v
WEB01 may delegate to me
```

The question becomes:

```text
Who may delegate to SERVER01?
```

---

# S4U Across Delegation Models

The relationship can be visualised as:

```text
                         S4U
                          |
                  +-------+-------+
                  |               |
                  v               v
              S4U2Self         S4U2Proxy
                                  |
                     +------------+------------+
                     |                         |
                     v                         v
             Traditional KCD                 RBCD
                     |                         |
                     v                         v
       msDS-AllowedToDelegateTo   msDS-AllowedToActOnBehalf
                                      OfOtherIdentity
```

---

# Protocol Transition Flag

Traditional constrained delegation may be configured with protocol transition.

The relevant `userAccountControl` flag is:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

Its value is:

```text
0x01000000
```

or:

```text
16777216
```

Conceptually:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
            |
            v
Protocol Transition
            |
            v
S4U2Self Ticket May Be
Suitable for Further Delegation
```

The exact ticket behaviour depends on the delegation model and account protections.

---

# Forwardable Tickets

The:

```text
FORWARDABLE
```

ticket flag is important to traditional S4U2Proxy.

In the traditional constrained-delegation model, the user's service ticket supplied for S4U2Proxy normally needs to be suitable for delegation.

Conceptually:

```text
S4U2Self
    |
    v
User -> Service 1
    |
    v
Forwardable?
    |
 +--+--+
 |     |
Yes    No
 |     |
 v     v
Potential    Traditional
S4U2Proxy    delegation may fail
```

However, RBCD introduces important differences to this simple model.

---

# RBCD and Non-Forwardable S4U2Self Tickets

Do not apply the traditional forwardable-ticket rule blindly to RBCD.

Modern Microsoft S4U behaviour permits resource-based constrained delegation in scenarios involving a non-forwardable S4U2Self-generated service ticket for a user who is not marked as sensitive for delegation, subject to the applicable KDC and domain-controller behaviour.

Therefore:

```text
Traditional KCD
       |
       v
Forwardable ticket
typically central


RBCD
 |
 v
Different KDC policy
and protocol behaviour
```

This distinction is one of the reasons S4U troubleshooting must begin by identifying the exact delegation model.

---

# Sensitive Users

Active Directory can mark an account:

```text
Account is sensitive and cannot be delegated
```

This corresponds to:

```text
NOT_DELEGATED
```

in `userAccountControl`.

The value is:

```text
0x00100000
```

or:

```text
1048576
```

This protection affects delegation behaviour.

---

# Enumerate AccountNotDelegated

PowerShell:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties AccountNotDelegated |
    Select-Object \
        SamAccountName,
        AccountNotDelegated
```

Enumerate accounts where it is enabled:

```powershell
Get-ADUser \
    -Filter {AccountNotDelegated -eq $true} \
    -Properties AccountNotDelegated |
    Select-Object \
        SamAccountName,
        AccountNotDelegated
```

---

# Protected Users

The:

```text
Protected Users
```

security group provides additional authentication protections for suitable sensitive identities.

Delegation testing involving Protected Users may therefore behave differently from testing with ordinary users.

A failed S4U operation against a protected identity does not necessarily mean:

```text
Delegation configuration is safe
```

Instead determine:

```text
Is the user protected?
        |
        v
Is delegation blocked for this identity?
        |
        v
Would another permitted identity
still be delegatable?
```

---

# S4U Requirements

A typical S4U workflow requires:

```text
Valid Service Principal
        |
        +
Service Authentication Material
        |
        +
KDC Reachability
        |
        +
Correct Domain / Realm
        |
        +
Correct SPNs
        |
        +
Delegation Configuration
        |
        +
Delegatable User
```

---

# Service Authentication Material

The requesting service must authenticate as itself.

Depending on the workflow, usable material may include:

```text
Password
NT Hash / RC4 Key
AES128 Key
AES256 Key
TGT
```

This does not mean the service possesses the target user's credentials.

The model is:

```text
Service Credential
       |
       v
Authenticate Service
       |
       v
S4U
       |
       v
Ticket Representing User
```

---

# Service Principal Names

SPNs are fundamental to S4U.

Examples:

```text
HTTP/web01.corp.example
cifs/fileserver01.corp.example
ldap/dc01.corp.example
MSSQLSvc/sql01.corp.example:1433
HOST/server01.corp.example
```

S4U2Proxy ultimately requests a ticket to a specific service principal.

---

# Enumerate SPNs

Windows:

```powershell
setspn -L WEB01
```

For a service account:

```powershell
setspn -L CORP\svc_web
```

Search for a particular SPN:

```powershell
setspn -Q cifs/server01.corp.example
```

PowerShell:

```powershell
Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties ServicePrincipalName |
    Select-Object \
        Name,
        ServicePrincipalName
```

---

# Enumerate Traditional Delegation

Users:

```powershell
Get-ADUser \
    -LDAPFilter '(msDS-AllowedToDelegateTo=*)' \
    -Properties ServicePrincipalName,msDS-AllowedToDelegateTo,userAccountControl |
    Select-Object \
        SamAccountName,
        ServicePrincipalName,
        msDS-AllowedToDelegateTo,
        userAccountControl
```

Computers:

```powershell
Get-ADComputer \
    -LDAPFilter '(msDS-AllowedToDelegateTo=*)' \
    -Properties DNSHostName,ServicePrincipalName,msDS-AllowedToDelegateTo,userAccountControl |
    Select-Object \
        Name,
        DNSHostName,
        ServicePrincipalName,
        msDS-AllowedToDelegateTo,
        userAccountControl
```

---

# Enumerate Protocol Transition

Search for:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

using:

```text
16777216
```

For users:

```powershell
Get-ADUser \
    -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=16777216)' \
    -Properties ServicePrincipalName,msDS-AllowedToDelegateTo,userAccountControl |
    Select-Object \
        SamAccountName,
        ServicePrincipalName,
        msDS-AllowedToDelegateTo,
        userAccountControl
```

For computers:

```powershell
Get-ADComputer \
    -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=16777216)' \
    -Properties DNSHostName,msDS-AllowedToDelegateTo,userAccountControl |
    Select-Object \
        Name,
        DNSHostName,
        msDS-AllowedToDelegateTo,
        userAccountControl
```

---

# Enumerate RBCD

Search:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

For computers:

```powershell
Get-ADComputer \
    -LDAPFilter '(msDS-AllowedToActOnBehalfOfOtherIdentity=*)' \
    -Properties DNSHostName,msDS-AllowedToActOnBehalfOfOtherIdentity |
    Select-Object \
        Name,
        DNSHostName,
        msDS-AllowedToActOnBehalfOfOtherIdentity
```

The attribute contains a security descriptor rather than a simple list of SPNs.

For detailed RBCD analysis:

[Resource-Based Constrained Delegation](rbcd.md)

---

# Linux Enumeration with Impacket

Impacket provides:

```text
findDelegation.py
```

commonly installed as:

```text
impacket-findDelegation
```

Check:

```bash
impacket-findDelegation -h
```

A typical authorised enumeration pattern is:

```bash
impacket-findDelegation \
    'corp.example/alice:<PASSWORD>' \
    -dc-ip 10.10.10.10
```

This can help identify:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

depending on the directory configuration.

---

# S4U with Impacket getST

Impacket provides:

```text
getST.py
```

commonly installed as:

```text
impacket-getST
```

The utility can request Kerberos service tickets and supports S4U workflows.

Always check the installed version:

```bash
impacket-getST -h
```

A controlled delegation test commonly follows the pattern:

```bash
impacket-getST \
    -spn '<SERVICE>/<TARGET_FQDN>' \
    -impersonate '<TEST_USER>' \
    'corp.example/<DELEGATING_ACCOUNT>:<PASSWORD>'
```

Example in a dedicated lab:

```bash
impacket-getST \
    -spn 'cifs/server01.corp.example' \
    -impersonate 'pt-test-user' \
    'corp.example/svc_test:<PASSWORD>'
```

The delegating account must actually possess the required delegation rights for the requested operation.

---

# What getST Is Doing Conceptually

The workflow can be represented as:

```text
svc_test
   |
   v
Authenticate
   |
   v
S4U2Self
   |
   v
pt-test-user -> svc_test
   |
   v
S4U2Proxy
   |
   v
pt-test-user -> cifs/server01
   |
   v
.ccache
```

The output is a legitimate KDC-issued service ticket.

---

# Existing TGT

Impacket can also operate in Kerberos workflows where authentication material is already available through a credential cache.

The model becomes:

```text
Existing Service TGT
        |
        v
KRB5CCNAME
        |
        v
getST
        |
        v
S4U
        |
        v
Service Ticket
```

Always inspect current `getST` help for the exact authentication options supported by the installed release.

---

# Resulting Credential Cache

A successful request may produce:

```text
pt-test-user@cifs_server01.corp.example@CORP.EXAMPLE.ccache
```

The exact filename depends on the Impacket version and requested service.

Treat the resulting file as a credential.

---

# Use the Ticket Cache

Set:

```bash
export KRB5CCNAME="$PWD/<TICKET>.ccache"
```

Inspect:

```bash
klist
```

Verify:

```text
Client Principal
Service Principal
Realm
Start Time
Expiration
Ticket Flags
```

---

# Minimum-Impact Validation

If the ticket targets:

```text
cifs/server01.corp.example
```

a controlled authentication check may use:

```bash
impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/<TEST_USER>@server01.corp.example'
```

The objective is:

```text
S4U
 |
 v
Impersonated Ticket
 |
 v
Authentication Proven
```

not:

```text
S4U
 |
 v
Immediately Execute Commands
```

---

# S4U with Rubeus

Rubeus provides extensive Windows Kerberos functionality including S4U operations.

Check:

```powershell
Rubeus.exe s4u
```

or the current Rubeus help before constructing a command because available options can change between releases.

The conceptual workflow is:

```text
Delegating Account
       |
       v
Authentication Material
       |
       v
TGT
       |
       v
Rubeus S4U
       |
       +--> S4U2Self
       |
       +--> S4U2Proxy
       |
       v
Service Ticket
```

---

# Controlled Rubeus Pattern

In an explicitly authorised lab, the S4U operation typically needs:

```text
Delegating User
Credential / Key
Impersonated User
Target SPN
Domain
Domain Controller
```

A conceptual command structure is:

```text
Rubeus.exe s4u
    /user:<DELEGATING_ACCOUNT>
    /<KEY_TYPE>:<KEY>
    /impersonateuser:<TEST_USER>
    /msdsspn:<TARGET_SPN>
    /domain:<DOMAIN>
    /dc:<DOMAIN_CONTROLLER>
```

Use the current official Rubeus usage output to confirm exact switches before execution.

Do not place real reusable key material in documentation.

---

# Rubeus Ticket Injection

Some Rubeus workflows can apply a resulting ticket to the current or specified logon session.

This is commonly associated with:

```text
/ptt
```

Conceptually:

```text
S4U
 |
 v
Service Ticket
 |
 v
Ticket Injection
 |
 v
Current Logon Session
```

Keep these concepts separate:

```text
S4U
 =
Obtain ticket


Pass-the-Ticket
 =
Use existing ticket
```

The workflow may combine them, but they are not the same technique.

---

# Windows Ticket Inspection

Use:

```powershell
klist
```

to inspect the current Kerberos ticket cache.

Useful information includes:

```text
Client
Server
Kerberos Encryption Type
Ticket Flags
Start Time
End Time
Renew Time
```

---

# Purging Test Tickets

In a dedicated test session:

```powershell
klist purge
```

can clear Kerberos tickets.

!!! warning
    `klist purge` can disrupt authentication in the current logon session. Do not use it casually on production administrative sessions.

---

# S4U and Pass-the-Ticket

S4U obtains:

```text
New KDC-Issued Ticket
```

Pass-the-Ticket begins with:

```text
Existing Ticket
```

The relationship is:

```text
S4U
 |
 v
Obtain Service Ticket
 |
 v
Ticket Cache
 |
 v
Pass-the-Ticket Style Usage
```

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# S4U and Pass-the-Key

Pass-the-Key uses:

```text
Long-Term Kerberos Key
```

to authenticate an account.

If the account has delegation capability:

```text
Kerberos Key
     |
     v
Authenticate Delegating Account
     |
     v
S4U
     |
     v
Impersonated Service Ticket
```

The key authenticates the service account.

S4U provides the impersonation mechanism.

See:

[Pass-the-Key](pass-the-key.md)

---

# S4U and OverPass-the-Hash

OverPass-the-Hash commonly uses:

```text
NT Hash / RC4 Key
```

to obtain Kerberos authentication.

A combined chain can therefore be:

```text
NT Hash
   |
   v
Kerberos TGT
   |
   v
Delegating Account
   |
   v
S4U
   |
   v
Impersonated Service Ticket
```

These remain separate concepts.

See:

[OverPass-the-Hash](overpass-the-hash.md)

---

# S4U and Kerberoasting

Kerberoasting:

```text
User
 |
 v
Requests Service Ticket
 |
 v
Offline Password Guessing
```

S4U:

```text
Service
 |
 v
Requests Ticket
on behalf of User
 |
 v
Delegated Authentication
```

Kerberoasting targets:

```text
Service Credential Strength
```

S4U evaluates:

```text
Delegation Trust
```

See:

[Kerberoasting](kerberoasting.md)

---

# S4U and Golden Tickets

S4U requests legitimate tickets from the KDC.

Golden Ticket attacks involve:

```text
KRBTGT Key
     |
     v
Forged TGT
```

Therefore:

```text
S4U
 =
KDC-Issued Tickets


Golden Ticket
 =
Forged TGT
```

Do not describe an S4U ticket as forged.

---

# S4U and Silver Tickets

Similarly:

```text
S4U
 |
 v
KDC issues service ticket
```

whereas a Silver Ticket technique involves forging service-ticket material using the relevant service-account key.

These are different trust models.

---

# Service-Class Importance

S4U2Proxy requests a ticket for a specific service.

Examples:

```text
cifs/server01
ldap/dc01
http/web01
MSSQLSvc/sql01
```

The resulting impact depends heavily on the service class.

---

# CIFS

Example:

```text
cifs/fileserver01.corp.example
```

The service ticket may allow the represented user to authenticate to SMB functionality.

Actual access depends on:

```text
Share Permissions
NTFS Permissions
Administrative Rights
Server Configuration
```

---

# LDAP

Example:

```text
ldap/dc01.corp.example
```

This represents LDAP authentication.

The resulting authorization is still based on the represented identity.

```text
Low-Privilege User
       |
       v
LDAP Ticket
       |
       v
Low-Privilege LDAP Access
```

versus:

```text
Privileged User
       |
       v
LDAP Ticket
       |
       v
Privileged LDAP Access
```

---

# HTTP

Example:

```text
HTTP/app01.corp.example
```

Impact depends on how the application maps the Kerberos-authenticated identity to application permissions.

A valid HTTP ticket does not automatically provide operating-system administrative access.

---

# MSSQLSvc

Example:

```text
MSSQLSvc/sql01.corp.example:1433
```

Impact depends on:

```text
SQL Login Mapping
Database Roles
Server Roles
Linked Servers
Application Configuration
```

---

# HOST

The:

```text
HOST
```

service class can be associated with multiple Windows service relationships.

Do not automatically assume:

```text
HOST/server01
 =
Every service on SERVER01
```

Validate the actual target service, registered SPNs, ticket handling, and resulting authorization.

---

# SPN Substitution

Some delegation scenarios involve alternative service classes associated with the same underlying computer account.

This can affect practical impact.

However, avoid reporting:

```text
Delegation to one SPN
        =
Unrestricted access to every
service on the host
```

without validation.

Analyse:

```text
Target Account
      |
      v
Registered SPNs
      |
      v
Requested Service
      |
      v
Ticket
      |
      v
Service Acceptance
```

---

# Hostnames Matter

Kerberos relies heavily on SPNs.

If the ticket contains:

```text
cifs/server01.corp.example
```

prefer:

```text
server01.corp.example
```

rather than:

```text
10.10.10.25
```

when accessing the service.

---

# DNS

Check:

```bash
getent hosts server01.corp.example
```

and:

```bash
getent hosts dc01.corp.example
```

On Windows:

```powershell
Resolve-DnsName server01.corp.example
```

Kerberos troubleshooting should always include DNS.

---

# Time

Check Linux:

```bash
date
```

Windows:

```powershell
w32tm /query /status
```

Kerberos depends on acceptable clock synchronization.

---

# Domain Controller

Identify the correct KDC.

Windows:

```powershell
nltest /dsgetdc:corp.example
```

DNS:

```powershell
Resolve-DnsName -Type SRV _kerberos._tcp.corp.example
```

Linux:

```bash
dig +short SRV _kerberos._tcp.corp.example
```

---

# Network Requirements

Kerberos commonly requires access to:

```text
TCP/UDP 88
```

for the KDC.

Directory enumeration may additionally require:

```text
389 LDAP
636 LDAPS
3268 Global Catalog
3269 Global Catalog over TLS
```

depending on the workflow.

The backend service requires its own network connectivity.

---

# Authorisation Still Applies

S4U changes:

```text
Authentication Identity
```

It does not bypass:

```text
Service Authorization
```

The backend evaluates the represented user.

```text
S4U Ticket
    |
    v
Backend Service
    |
    v
User Permissions
    |
 +--+--+
 |     |
Allow Deny
```

---

# S4U Does Not Automatically Mean Privilege Escalation

Finding an S4U-capable account does not automatically prove:

```text
Domain Admin
```

The actual impact depends on:

```text
Who controls the service?
        |
        v
Which delegation model?
        |
        v
Which backend services?
        |
        v
Which users are delegatable?
        |
        v
What permissions do those users have?
```

---

# Account Control Analysis

For every S4U-capable service account, investigate:

```text
Who knows the password?
Who controls the computer?
Who can reset the password?
Who can modify the account?
Who can modify delegation?
Who owns the object?
Who has GenericAll?
Who has GenericWrite?
Who has WriteDACL?
Who has WriteOwner?
```

This turns protocol knowledge into practical attack-path analysis.

---

# BloodHound

BloodHound helps connect:

```text
Account Control
       |
       v
Delegation
       |
       v
Target Service
       |
       v
Privilege
```

A conceptual path might be:

```text
Alice
 |
 v
GenericAll
 |
 v
svc_web
 |
 v
Constrained Delegation
 |
 v
SERVER01
 |
 v
Privileged Access
```

---

# RBCD BloodHound Path

An RBCD path might look like:

```text
Alice
 |
 v
GenericWrite
 |
 v
SERVER01$
 |
 v
RBCD
 |
 v
Controlled Computer
 |
 v
S4U
 |
 v
SERVER01
```

For detailed BloodHound usage:

[BloodHound](bloodhound.md)

---

# Safe S4U Validation

A preferred testing workflow is:

```text
Enumerate Delegation
       |
       v
Understand Trust
       |
       v
Identify Controlled Service
       |
       v
Select Test User
       |
       v
Select One Allowed SPN
       |
       v
Request One Ticket
       |
       v
Inspect Ticket
       |
       v
Authenticate Once
       |
       v
Stop
```

---

# Minimum-Impact Principle

Avoid:

```text
S4U works
   |
   v
Impersonate Domain Admin
   |
   v
Remote Execute on DC
```

when:

```text
Dedicated Test User
        |
        v
S4U Ticket
        |
        v
Successful Authentication
```

already proves the security condition.

---

# Evidence from S4U

Useful evidence includes:

```text
Delegating Account
Delegation Type
Target User
Target SPN
KDC
Ticket Client
Ticket Server
Ticket Flags
Ticket Lifetime
Authentication Result
```

Do not expose reusable ticket material.

---

# Detection

S4U uses legitimate Kerberos protocol exchanges.

Therefore detection should focus on:

```text
Context
    +
Delegation Configuration
    +
Kerberos Ticket Requests
    +
Source Host
    +
Target Service
    +
Represented Identity
```

rather than assuming a single event uniquely identifies malicious S4U.

---

# Event 4768

Event:

```text
4768
```

records Kerberos TGT requests.

It can help establish how and when the delegating principal obtained Kerberos authentication.

Useful fields can include:

```text
Account
Client Address
Ticket Encryption Type
Pre-Authentication Information
Result
```

The exact event fields depend on Windows version and event schema.

---

# Event 4769

Event:

```text
4769
```

records Kerberos service-ticket requests.

This is particularly important for S4U analysis.

Useful context includes:

```text
Account
Service Name
Client Address
Ticket Options
Ticket Encryption Type
Status
```

Modern Windows event schemas may expose additional Kerberos details.

---

# Event 4624

Successful authentication to the backend may generate:

```text
4624
```

Correlate:

```text
4769 on Domain Controller
          |
          v
4624 on Backend Server
```

where possible.

---

# Event 4672

If the represented user receives special privileges:

```text
4672
```

may provide supporting context.

It is not specific to S4U.

---

# Event 5136

Directory Service Changes auditing may expose modifications to delegation attributes such as:

```text
msDS-AllowedToDelegateTo
```

or:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

This is particularly important where the attack path begins with changing delegation configuration.

---

# Detection Model

```text
Delegation Configuration
        |
        v
Service Authentication
        |
        v
S4U Ticket Request
        |
        v
Backend Authentication
        |
        v
Post-Authentication Activity
```

Correlating the entire chain is more valuable than relying on a single Kerberos event.

---

# Baseline Delegation

Maintain an inventory:

```text
Delegating Account
Delegation Model
Allowed Resource
Allowed SPN
Protocol Transition
Business Purpose
Owner
```

Example:

```text
Account     Model      Destination                Purpose
----------------------------------------------------------------
svc_web     KCD        MSSQLSvc/sql01:1433        Web backend
WEB02$      RBCD       FILE01                     File workflow
```

---

# Detect Unexpected S4U Sources

Suppose:

```text
svc_web
```

normally operates from:

```text
WEB01
```

but related Kerberos activity suddenly originates from:

```text
WS123
```

That discrepancy may deserve investigation.

The behavioural model is:

```text
Delegating Identity
       |
       v
Expected Source?
       |
   +---+---+
   |       |
  Yes      No
           |
           v
      Investigate
```

---

# Detect Unusual Target Services

Baseline:

```text
svc_web
 |
 v
MSSQLSvc/sql01
```

Unexpected:

```text
svc_web
 |
 v
cifs/dc01
```

may indicate:

```text
Configuration Change
Tool Misuse
Compromise
Unexpected Application Behaviour
```

depending on the environment.

---

# Endpoint Telemetry

Endpoint monitoring can provide context around:

```text
Credential Access
Kerberos Tool Execution
Ticket Manipulation
Unexpected Service-Account Use
Remote Administration
PowerShell
Unusual Network Connections
```

Do not rely solely on detecting names such as:

```text
Rubeus.exe
```

or:

```text
getST.py
```

The underlying protocol can be implemented using other tooling.

---

# Purple Team Exercise

A controlled exercise can test:

```text
Delegation Enumeration
        |
        v
Test S4U Request
        |
        v
Test User Representation
        |
        v
Backend Authentication
        |
        v
Blue Team Investigation
```

---

# Purple Team Questions

Defenders should determine:

```text
Which service performed S4U?

Which user was represented?

Was S4U2Self used?

Was S4U2Proxy used?

Which delegation model applied?

Which target SPN was requested?

Which source host performed the activity?

Was protocol transition enabled?

Was the user protected?

Was the backend access expected?

Was delegation configuration changed?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect
Time to identify delegating account
Time to identify represented user
Time to identify target SPN
Time to identify source host
Time to determine KCD vs RBCD
Time to identify S4U2Self
Time to identify S4U2Proxy
Time to reconstruct complete chain
Correct containment?
Correct remediation?
```

---

# Hardening

The S4U defensive model is:

```text
Delegation Required?
       |
   +---+---+
   |       |
  No      Yes
   |       |
   v       v
Remove   Minimise
           |
           v
Protect Service Identity
           |
           v
Protect Sensitive Users
           |
           v
Restrict ACLs
           |
           v
Monitor Kerberos
```

---

# Remove Unnecessary Delegation

If the application no longer requires delegation:

```text
Remove the Delegation Relationship
```

This may involve:

```text
msDS-AllowedToDelegateTo
```

for traditional KCD or:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

for RBCD.

Production changes should follow normal change-management procedures.

---

# Minimise Traditional KCD Destinations

Only permit required SPNs.

Instead of:

```text
svc_web
 |
 +--> cifs/server01
 +--> ldap/server01
 +--> http/server01
 +--> MSSQLSvc/sql01
```

if the application requires only:

```text
MSSQLSvc/sql01
```

configure only the required service.

---

# Restrict RBCD

Limit which principals are present in:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

and restrict who can modify the target resource object.

---

# Remove Unnecessary Protocol Transition

If the application does not require non-Kerberos front-end authentication to transition into Kerberos delegation, evaluate whether:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

is necessary.

Do not remove it without application compatibility testing.

---

# Protect Delegating Credentials

Because S4U privileges belong to the service principal, compromise of that principal can expose its delegation capabilities.

Protect:

```text
Service Account Passwords
Machine Account Credentials
NT Hashes
AES Keys
TGTs
```

---

# Use gMSA Where Appropriate

Group Managed Service Accounts can reduce risk associated with manually managed service-account passwords.

Conceptually:

```text
Static Service Password
        |
        v
Human Management
        |
        v
Password Age / Reuse Risk
```

versus:

```text
gMSA
 |
 v
Managed Long Credential
 |
 v
Automatic Rotation
```

Delegation permissions still need independent review.

---

# Protect Sensitive Users

Where appropriate:

```text
Account is sensitive and cannot be delegated
```

can prevent delegation of high-value identities.

PowerShell:

```powershell
Set-ADAccountControl \
    -Identity '<USERNAME>' \
    -AccountNotDelegated $true
```

Only make such changes through authorised administration and after compatibility assessment.

---

# Protected Users

Consider:

```text
Protected Users
```

for suitable privileged human identities.

Test application compatibility before deployment.

---

# Administrative Tiering

Avoid allowing highly privileged identities to authenticate to lower-trust systems unnecessarily.

Bad:

```text
Domain Admin
    |
    v
WEB01
    |
    v
Delegation-Capable Service
```

Better:

```text
Domain Admin
    |
    v
PAW
    |
    v
Tier 0
```

---

# Privileged Access Workstations

Use dedicated administrative workstations for sensitive administrative operations.

This reduces the likelihood that highly privileged authentication contexts interact with delegation-enabled application servers.

---

# ACL Hardening

Review who can control:

```text
Delegating Accounts
Target Computer Objects
Delegation Attributes
```

Pay attention to:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
Reset Password
```

An S4U configuration may become exploitable through an unrelated ACL weakness.

---

# Network Segmentation

A valid Kerberos service ticket should not imply unrestricted network access.

Apply:

```text
Firewalling
Network segmentation
Administrative network separation
Service-specific access controls
```

---

# Incident Response

If S4U abuse is suspected:

```text
Suspicious Delegation Activity
          |
          v
Identify Delegating Principal
          |
          v
Identify Source Host
          |
          v
Identify Represented Users
          |
          v
Identify Target SPNs
          |
          v
Determine KCD / RBCD
          |
          v
Review Delegation Changes
          |
          v
Review 4768 / 4769
          |
          v
Review Backend Logons
          |
          v
Contain Principal / Host
          |
          v
Rotate Compromised Credential
          |
          v
Remove Malicious Delegation
          |
          v
Hunt for Lateral Movement
```

---

# Credential Rotation

If the delegating account's long-term key has been compromised:

```text
Service Credential
       |
       v
Rotate
       |
       v
New Long-Term Key
```

The appropriate procedure depends on whether the identity is:

```text
User Service Account
Computer Account
gMSA
```

Do not manually rotate managed credentials without understanding operational dependencies.

---

# Review Existing Tickets

Credential rotation does not necessarily make every already issued ticket disappear instantly.

Incident response should consider:

```text
Ticket Lifetimes
Existing Sessions
Service Tickets
TGTs
```

in addition to rotating the underlying account credential.

---

# Reporting

Possible finding titles include:

```text
Kerberos S4U Delegation Enables Privileged User Impersonation
```

```text
Compromised Service Account Can Abuse Kerberos Delegation
```

```text
Excessive Kerberos Delegation Rights Enable Service Impersonation
```

```text
Kerberos Protocol Transition Enabled on High-Risk Service Account
```

```text
Active Directory ACL Weakness Enables S4U Delegation Abuse
```

---

# Avoid Reporting S4U as a Vulnerability by Itself

S4U is legitimate Kerberos functionality.

Avoid:

```text
S4U Enabled
   =
Vulnerability
```

Instead establish:

```text
Service Account Compromise
        |
        +
Delegation Configuration
        |
        +
Representable User
        |
        +
Sensitive Target Service
        |
        v
Security Impact
```

---

# Root Cause

Potential root causes include:

```text
Weak Service Credential
Kerberoastable Service Account
Excessive ACL
Writable Computer Object
Excessive Delegation Scope
Unnecessary Protocol Transition
Poor Administrative Tiering
Compromised Application Server
```

Report the condition that makes S4U abuse practical.

---

# Example Finding

```text
Finding:
Compromised Service Account Can Abuse Kerberos S4U Delegation

Affected Account:
CORP\svc_web

Delegation Model:
Traditional Constrained Delegation

Allowed Service:
MSSQLSvc/sql01.corp.example:1433

Description:
The affected service account is configured for Kerberos constrained
delegation to the SQL Server service hosted by SQL01.

Control of the service account permits use of the Kerberos Service for
User extensions to request service tickets representing other
delegatable users to the configured backend service.

During controlled validation, a dedicated test identity was represented
using the S4U workflow and a KDC-issued service ticket was obtained for
the authorised SQL Server SPN.

The resulting ticket was validated without performing unnecessary
privileged operations.

Impact:
An attacker who compromises the service account may inherit its
delegation capabilities and potentially authenticate to the configured
backend service as other delegatable users.

The resulting impact depends on the permissions held by those users on
the backend service.

Recommendation:
Confirm whether the delegation relationship and protocol-transition
configuration remain operationally necessary.

Reduce delegation to the minimum required SPNs, protect the service
account using strong managed credentials, restrict ACL control over the
service account, protect sensitive administrative identities from
delegation, apply administrative tiering, and monitor Kerberos
service-ticket activity and delegation configuration changes.
```

---

# Evidence Collection

Record:

```text
Delegating Account
Account Type
Delegation Model
Protocol Transition
ServicePrincipalName
msDS-AllowedToDelegateTo
msDS-AllowedToActOnBehalfOfOtherIdentity
Target User
AccountNotDelegated
Protected Users Membership
Target SPN
Target Host
KDC
Ticket Client
Ticket Service
Ticket Flags
Ticket Encryption Type
Ticket Lifetime
Authentication Result
Source Host
Relevant Event IDs
Tool
Command
Timestamp
```

---

# Evidence Redaction

Treat:

```text
Password
NT Hash
RC4 Key
AES Key
TGT
Service Ticket
.ccache
.kirbi
```

as sensitive authentication material.

Use:

```text
[REDACTED]
```

in reports and screenshots where necessary.

---

# Cleanup

Linux:

```bash
unset KRB5CCNAME
```

Where appropriate:

```bash
kdestroy
```

Remove temporary ticket files according to the engagement evidence-retention policy:

```bash
rm -f <TICKET>.ccache
```

Windows dedicated testing session:

```powershell
klist
```

and, where appropriate:

```powershell
klist purge
```

If delegation configuration was modified during an authorised test, restore the exact original configuration.

---

# Troubleshooting

## S4U2Self Fails

Check:

```text
Delegating Account Credential
Account Status
SPN
Domain
Realm
KDC
DNS
Time
```

Also determine whether the requested operation is valid for the service principal.

---

# S4U2Proxy Fails

Check:

```text
Delegation Model
Delegation Configuration
Target SPN
User Protection
Ticket Flags
KDC
DNS
Time
```

Do not assume traditional KCD and RBCD have identical ticket requirements.

---

# KDC_ERR_BADOPTION

This error commonly indicates that the requested Kerberos operation or ticket options are not permitted.

Investigate:

```text
Forwardable Ticket?
Delegation Configured?
Correct Delegation Model?
User Delegatable?
Correct Target SPN?
S4U2Proxy Allowed?
```

---

# KDC_ERR_S_PRINCIPAL_UNKNOWN

The KDC cannot identify the requested service principal.

Check:

```powershell
setspn -Q <SPN>
```

Example:

```powershell
setspn -Q cifs/server01.corp.example
```

Verify:

```text
Service Class
Hostname
FQDN
Port
SPN Registration
```

---

# KDC_ERR_ETYPE_NOSUPP

Review:

```text
Service Account Keys
Kerberos Encryption Types
Domain Policy
Tool Options
```

Do not enable obsolete encryption merely to make the test succeed.

---

# KDC_ERR_PREAUTH_FAILED

If authentication of the delegating principal fails, verify:

```text
Password
NT Hash
AES Key
Username
Realm
Key Version
Account State
```

A stale key after password rotation will fail.

---

# KRB_AP_ERR_MODIFIED

This commonly indicates a mismatch involving the service key or SPN ownership.

Check:

```text
Requested SPN
SPN Owner
Duplicate SPNs
Target Service Account
Ticket Encryption
```

Search:

```powershell
setspn -Q <SPN>
```

and investigate duplicate or incorrect registrations.

---

# Clock Skew

Linux:

```bash
date
```

Windows:

```powershell
w32tm /query /status
```

Do not weaken domain time configuration for testing.

---

# DNS Failure

Check:

```bash
getent hosts dc01.corp.example
getent hosts server01.corp.example
```

Windows:

```powershell
Resolve-DnsName dc01.corp.example
Resolve-DnsName server01.corp.example
```

---

# Ticket Obtained but Service Fails

Inspect:

```bash
klist
```

Check:

```text
Client Principal
Service Principal
Realm
Expiration
Flags
```

Then verify:

```text
Hostname
SPN
Service Availability
Network Reachability
User Authorization
```

---

# Authentication Works but Access Is Denied

This usually means:

```text
Kerberos Authentication
        |
        v
Succeeded
```

but:

```text
Application Authorization
        |
        v
Denied
```

This can still prove that the S4U delegation mechanism worked.

---

# Protected User Fails

Check:

```text
AccountNotDelegated
Protected Users
```

A protected identity may intentionally be unavailable for delegation.

Do not remove those protections merely to demonstrate the technique.

---

# Wrong Delegation Model

Before troubleshooting ticket flags, determine whether the environment uses:

```text
Traditional KCD
```

or:

```text
RBCD
```

The rules are not identical.

---

# Common Mistakes

## Mistake 1 - Treating S4U as an Attack

S4U is legitimate Kerberos functionality.

The security issue is misuse of delegation capability after compromise or misconfiguration.

---

## Mistake 2 - Confusing S4U2Self and S4U2Proxy

```text
S4U2Self
     =
Ticket to requesting service


S4U2Proxy
     =
Ticket to another service
```

---

## Mistake 3 - Assuming S4U2Self Means Unlimited Delegation

It does not.

Further delegation depends on additional policy.

---

## Mistake 4 - Assuming the Service Knows the User's Password

S4U does not require the service to possess the represented user's plaintext password.

---

## Mistake 5 - Calling the Resulting Ticket Forged

The KDC issues the S4U ticket.

It is not a Golden or Silver Ticket merely because another identity is represented.

---

## Mistake 6 - Confusing KCD and RBCD

```text
KCD
 |
 v
Delegator-side policy


RBCD
 |
 v
Resource-side policy
```

---

## Mistake 7 - Applying Traditional Forwardable Rules Blindly to RBCD

RBCD has different protocol behaviour for S4U2Proxy.

Identify the delegation model first.

---

## Mistake 8 - Ignoring AccountNotDelegated

Sensitive accounts may intentionally be protected from delegation.

---

## Mistake 9 - Ignoring Protected Users

Authentication protections can materially affect S4U behaviour.

---

## Mistake 10 - Ignoring SPNs

S4U2Proxy ultimately requests a ticket to a particular service principal.

---

## Mistake 11 - Assuming Every Service Ticket Means Administrator

Authentication and authorization remain separate.

---

## Mistake 12 - Using IP Addresses

Kerberos normally expects service identities represented through SPNs and hostnames.

---

## Mistake 13 - Ignoring DNS

Kerberos failures are frequently DNS-related.

---

## Mistake 14 - Ignoring Time

Clock synchronization remains fundamental.

---

## Mistake 15 - Immediately Impersonating Domain Admin

Use a dedicated test identity where possible.

---

## Mistake 16 - Performing Remote Execution Unnecessarily

Successful ticket acquisition and controlled service authentication may already prove the issue.

---

## Mistake 17 - Ignoring ACL Paths

The real root cause may be control of the delegation-enabled account rather than the delegation configuration itself.

---

## Mistake 18 - Ignoring Ticket Cleanup

S4U output can be reusable credential material.

---

## Mistake 19 - Ignoring Delegation Configuration Changes

RBCD and traditional KCD abuse may involve modifying Active Directory.

Monitor and restore those changes.

---

## Mistake 20 - Reporting Tool Output Without Understanding the Protocol

Always map:

```text
Tool Output
    |
    v
S4U2Self?
    |
    v
S4U2Proxy?
    |
    v
Delegation Model?
    |
    v
Target SPN?
    |
    v
Represented User?
```

---

# Assessment Checklist

## Preparation

- [ ] Confirm S4U testing is authorised
- [ ] Confirm delegation relationships are in scope
- [ ] Confirm permitted users
- [ ] Confirm permitted target services
- [ ] Confirm whether AD modifications are allowed
- [ ] Confirm whether ticket injection is allowed
- [ ] Confirm remote execution restrictions
- [ ] Identify domain controller
- [ ] Verify DNS
- [ ] Verify time

## Delegation Enumeration

- [ ] Enumerate `msDS-AllowedToDelegateTo`
- [ ] Enumerate `TRUSTED_TO_AUTH_FOR_DELEGATION`
- [ ] Enumerate `msDS-AllowedToActOnBehalfOfOtherIdentity`
- [ ] Enumerate service accounts
- [ ] Enumerate computer accounts
- [ ] Enumerate SPNs
- [ ] Run `impacket-findDelegation`
- [ ] Review BloodHound paths
- [ ] Determine KCD vs RBCD

## Service Analysis

- [ ] Identify delegating principal
- [ ] Identify service purpose
- [ ] Identify authentication material
- [ ] Review account ACLs
- [ ] Review account owner
- [ ] Review credential exposure
- [ ] Review Kerberoasting exposure
- [ ] Identify source host

## User Analysis

- [ ] Select dedicated test user
- [ ] Check `AccountNotDelegated`
- [ ] Check Protected Users
- [ ] Determine backend permissions
- [ ] Avoid privileged production identities where unnecessary

## S4U2Self

- [ ] Confirm service identity
- [ ] Confirm service SPN
- [ ] Request only authorised user representation
- [ ] Inspect resulting ticket
- [ ] Review forwardable flag where relevant
- [ ] Determine protocol-transition context

## S4U2Proxy

- [ ] Confirm delegation model
- [ ] Confirm destination SPN
- [ ] Confirm delegation permission
- [ ] Confirm user is delegatable
- [ ] Request only one required ticket
- [ ] Inspect resulting service ticket
- [ ] Validate only required service

## Detection

- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4624
- [ ] Review 4672 where relevant
- [ ] Review 5136 where configuration changed
- [ ] Identify represented user
- [ ] Identify delegating account
- [ ] Identify target SPN
- [ ] Identify source host
- [ ] Correlate endpoint telemetry

## Hardening

- [ ] Confirm delegation is required
- [ ] Remove unnecessary delegation
- [ ] Minimise KCD destination SPNs
- [ ] Restrict RBCD trusted principals
- [ ] Remove unnecessary protocol transition
- [ ] Protect service credentials
- [ ] Use gMSA where appropriate
- [ ] Protect sensitive users
- [ ] Review Protected Users
- [ ] Apply administrative tiering
- [ ] Harden delegation-related ACLs
- [ ] Segment sensitive services
- [ ] Monitor delegation changes

## Cleanup

- [ ] Unset `KRB5CCNAME`
- [ ] Destroy temporary ticket cache
- [ ] Remove `.ccache`
- [ ] Remove `.kirbi`
- [ ] Purge dedicated Windows test-session tickets where appropriate
- [ ] Restore modified delegation configuration
- [ ] Verify legitimate configuration remains
- [ ] Secure retained evidence
- [ ] Redact reusable credentials

---

# S4U Testing Model

The fundamental model is:

```text
                           S4U
                            |
                +-----------+-----------+
                |                       |
                v                       v
            S4U2Self                S4U2Proxy
                |                       |
                v                       v
        Ticket to Service       Ticket to Another
          Representing User     Service Representing User
```

The protocol-transition model is:

```text
User
 |
 | Non-Kerberos Authentication
 v
Front-End Service
 |
 | S4U2Self
 v
KDC
 |
 v
User -> Front-End
Kerberos Ticket
```

The constrained-delegation model is:

```text
User -> Service 1
        |
        v
     Service 1
        |
        | S4U2Proxy
        v
       KDC
        |
        v
User -> Service 2
```

The combined model is:

```text
User
 |
 | Non-Kerberos
 v
Service 1
 |
 | S4U2Self
 v
User -> Service 1
 |
 | S4U2Proxy
 v
User -> Service 2
 |
 v
Backend Authorization
```

Traditional KCD controls:

```text
Service 1
    |
    v
msDS-AllowedToDelegateTo
    |
    v
Allowed Service 2
```

RBCD controls:

```text
Service 2
    |
    v
msDS-AllowedToActOnBehalfOfOtherIdentity
    |
    v
Allowed Service 1
```

The attack-path model is:

```text
Attacker
   |
   v
Controls Delegating Principal
   |
   v
Authenticates as Service
   |
   v
S4U
   |
   v
Represents Another User
   |
   v
Configured Backend Service
   |
   v
User's Backend Permissions
```

The ACL-driven model is:

```text
Low-Privilege Principal
        |
        v
Controls Delegation Account
or Resource Object
        |
        v
Delegation Capability
        |
        v
S4U
        |
        v
User Impersonation
        |
        v
Privilege Expansion
```

The detection model is:

```text
Delegation Configuration
        |
        v
Service Authentication
        |
        v
S4U Ticket Request
      4769
        |
        v
Backend Authentication
      4624
        |
        v
Post-Authentication Activity
```

The defensive model is:

```text
S4U / Delegation
       |
       +--> Is Delegation Required?
       |          |
       |       +--+--+
       |       |     |
       |      No    Yes
       |       |     |
       |       v     v
       |    Remove  Minimise
       |
       +--> Protect Service Principal
       |
       +--> Protect Sensitive Users
       |
       +--> Restrict Delegation ACLs
       |
       +--> Restrict RBCD Writes
       |
       +--> Administrative Tiering
       |
       +--> Segment Backend Services
       |
       +--> Monitor Kerberos
       |
       +--> Monitor AD Changes
```

A mature S4U assessment should answer:

```text
Which services can perform delegation?
        |
        v
Is S4U2Self relevant?
        |
        v
Is protocol transition enabled?
        |
        v
Can S4U2Proxy be performed?
        |
        v
Is this traditional KCD or RBCD?
        |
        v
Which SPNs are reachable?
        |
        v
Which users can be represented?
        |
        v
Which users are protected?
        |
        v
Who controls the service identity?
        |
        v
Who can modify delegation?
        |
        v
What permissions result at the backend?
        |
        v
Can defenders reconstruct the S4U chain?
        |
        v
Can delegation be removed or reduced?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The following topics complement S4U and can be linked once their dedicated notes are available:

```text
active-directory/acl-ace.md
active-directory/machine-account-quota.md
active-directory/shadow-credentials.md
active-directory/gmsa.md
active-directory/golden-ticket.md
active-directory/silver-ticket.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft S4U

[Microsoft - Kerberos Protocol Extensions: Service for User and Constrained Delegation Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/3bff5864-8135-400e-bdd9-33b552051d94){ target="_blank" rel="noopener noreferrer" }

[Microsoft - S4U Overview](https://learn.microsoft.com/en-us/openspecs/windows_protocols/MS-SFU/36d103d2-61a6-42d5-a725-74de3205cdaf){ target="_blank" rel="noopener noreferrer" }

[Microsoft - S4U2Proxy](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/bde93b0e-f3c9-4ddf-9f44-e1453be7af5a){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Kerberos

[Microsoft - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Protocol Extensions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

---

## Kerberos Standard

[RFC 4120 - The Kerberos Network Authentication Service V5](https://www.rfc-editor.org/rfc/rfc4120){ target="_blank" rel="noopener noreferrer" }

---

## Active Directory Delegation

[Microsoft - msDS-AllowedToDelegateTo](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtodelegateto){ target="_blank" rel="noopener noreferrer" }

[Microsoft - msDS-AllowedToActOnBehalfOfOtherIdentity](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtoactonbehalfofotheridentity){ target="_blank" rel="noopener noreferrer" }

[Microsoft - ADS_USER_FLAG_ENUM](https://learn.microsoft.com/en-us/windows/win32/api/iads/ne-iads-ads_user_flag_enum){ target="_blank" rel="noopener noreferrer" }

---

## Account Protection

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

[Impacket findDelegation](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py){ target="_blank" rel="noopener noreferrer" }

---

## Rubeus

[Rubeus](https://github.com/GhostPack/Rubeus){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

S4U is one of the most important concepts for understanding modern Active Directory Kerberos delegation.

The two mechanisms are:

```text
S4U2Self
```

and:

```text
S4U2Proxy
```

The simplest distinction is:

```text
S4U2Self
    |
    v
Service obtains ticket
to itself as User


S4U2Proxy
    |
    v
Service obtains ticket
to another service as User
```

Together they can create:

```text
User
 |
 | Non-Kerberos Authentication
 v
Service 1
 |
 | S4U2Self
 v
User -> Service 1
 |
 | S4U2Proxy
 v
User -> Service 2
```

Traditional constrained delegation controls this through:

```text
msDS-AllowedToDelegateTo
```

while RBCD controls delegation through:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

The central security principle is:

```text
S4U
 |
 X
Vulnerability by itself
```

Instead:

```text
Compromised Service
        +
Delegation Rights
        +
Delegatable User
        +
Sensitive Backend
        |
        v
Potential Privilege Expansion
```

The KDC remains involved in issuing the tickets.

Therefore S4U should not be confused with ticket forgery:

```text
S4U
 |
 v
KDC-Issued Ticket


Golden / Silver Ticket
 |
 v
Forged Ticket Material
```

The most important assessment questions are:

```text
Who controls the service?
        |
        v
Which delegation model applies?
        |
        v
Is protocol transition enabled?
        |
        v
Which users can be represented?
        |
        v
Which services can be reached?
        |
        v
What permissions do those users
have at those services?
```

The most important defensive questions are:

```text
Is delegation required?
        |
        v
Can its scope be reduced?
        |
        v
Can the service identity be
better protected?
        |
        v
Can privileged users be
prevented from delegation?
        |
        v
Can ACL control over delegation
objects be reduced?
        |
        v
Can S4U activity and delegation
changes be detected?
```

S4U should therefore be analysed as part of the complete Kerberos trust architecture:

```text
Service Identity
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
Backend Authentication
      |
      v
User Authorization
```

Understanding that chain makes constrained delegation, RBCD, protocol transition, Kerberos ticket abuse, delegation-related ACL paths, and their defensive controls significantly easier to analyse during an authorised Active Directory assessment.
