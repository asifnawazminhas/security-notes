# Constrained Delegation

Kerberos Constrained Delegation (KCD) is an Active Directory feature that allows a service to impersonate users when accessing specifically configured backend services.

It was introduced to reduce the broad trust associated with unconstrained delegation.

The fundamental difference is:

```text
Unconstrained Delegation
        |
        v
Broad Delegation
        |
        v
Many Kerberos Services
```

versus:

```text
Constrained Delegation
        |
        v
Explicit Delegation
        |
        v
Configured Backend Services
```

A typical legitimate architecture is:

```text
User
 |
 v
WEB01
 |
 | Kerberos delegation
 v
SQL01
```

Instead of allowing `WEB01` to delegate authentication to arbitrary services, Active Directory can restrict delegation to specific Service Principal Names (SPNs), such as:

```text
MSSQLSvc/sql01.corp.example:1433
```

The configured destinations are stored in the:

```text
msDS-AllowedToDelegateTo
```

attribute of the delegating account.

Constrained delegation significantly reduces the delegation scope compared with unconstrained delegation, but it remains security-sensitive. If an attacker compromises an account configured for constrained delegation, the attacker may be able to impersonate users to the services permitted by that delegation configuration.

!!! warning "Authorised testing only"
    Kerberos delegation testing can result in user impersonation and reusable service tickets. Only test delegation relationships, accounts, users, and services explicitly included in the engagement scope. Prefer enumeration and controlled test identities before attempting impersonation of privileged users.

---

# Delegation Overview

The main Active Directory Kerberos delegation models are:

```text
Kerberos Delegation
       |
       +--> Unconstrained Delegation
       |
       +--> Constrained Delegation
       |
       +--> Resource-Based
            Constrained Delegation
```

At a high level:

| Delegation Model | Delegation Scope | Configuration Location |
|---|---|---|
| Unconstrained | Broad | Front-end account |
| Constrained | Specific services | Front-end account |
| RBCD | Specific principals | Back-end resource |

---

# Why Constrained Delegation Exists

Consider a web application that accesses a database on behalf of its users.

```text
Alice
 |
 v
WEB01
 |
 v
SQL01
```

The application needs:

```text
Alice -> WEB01 -> SQL01
```

while preserving Alice's identity.

Without delegation:

```text
Alice
 |
 v
WEB01
 |
 X
Cannot automatically authenticate
to SQL01 as Alice
```

Unconstrained delegation solves this by giving the front-end broad delegation capability.

```text
WEB01
 |
 +--> SQL01
 +--> FILE01
 +--> APP02
 +--> Other Kerberos Services
```

Constrained delegation restricts this:

```text
WEB01
 |
 +--> MSSQLSvc/SQL01
 |
 X
FILE01
 |
 X
APP02
```

The security boundary therefore becomes the configured service list.

---

# Core Architecture

The normal constrained delegation architecture is:

```text
             User
              |
              v
        Front-End Service
              |
              v
       Delegating Account
              |
              v
msDS-AllowedToDelegateTo
              |
              v
      Approved SPN(s)
              |
              v
       Back-End Service
```

Example:

```text
Alice
 |
 v
WEB01
 |
 v
svc_web
 |
 v
msDS-AllowedToDelegateTo
 |
 v
MSSQLSvc/sql01.corp.example:1433
 |
 v
SQL01
```

---

# Delegating Account

Delegation is configured against the security principal running the front-end service.

This can be:

```text
Computer Account
```

such as:

```text
WEB01$
```

or:

```text
User / Service Account
```

such as:

```text
svc_web
```

Therefore, constrained delegation enumeration must inspect both:

```text
Users
```

and:

```text
Computers
```

---

# Service Principal Names

Kerberos identifies services using Service Principal Names.

Examples include:

```text
cifs/fileserver01.corp.example
http/web01.corp.example
ldap/dc01.corp.example
host/server01.corp.example
MSSQLSvc/sql01.corp.example:1433
```

Constrained delegation permissions reference these SPNs.

For example:

```text
msDS-AllowedToDelegateTo:
    cifs/fileserver01.corp.example
    MSSQLSvc/sql01.corp.example:1433
```

This means the delegating account has been configured to delegate to those services.

---

# msDS-AllowedToDelegateTo

Traditional constrained delegation stores permitted destination services in:

```text
msDS-AllowedToDelegateTo
```

A conceptual object might look like:

```text
Account:
svc_web

SPNs:
HTTP/web01.corp.example

msDS-AllowedToDelegateTo:
MSSQLSvc/sql01.corp.example:1433
```

The trust relationship is:

```text
svc_web
   |
   v
May delegate to
   |
   v
MSSQLSvc/sql01.corp.example:1433
```

---

# Constrained Delegation Modes

Traditional constrained delegation can operate in two important modes:

```text
Kerberos Only
```

and:

```text
Use Any Authentication Protocol
```

The distinction is important because the latter enables Kerberos protocol transition.

---

# Kerberos Only

The Active Directory GUI option is commonly presented as:

```text
Trust this user/computer for delegation
to specified services only

Use Kerberos only
```

Conceptually:

```text
User
 |
 | Kerberos
 v
Front-End
 |
 | Delegation
 v
Configured Back-End
```

The user's original authentication context is Kerberos-based.

---

# Protocol Transition

The second mode is commonly presented as:

```text
Trust this user/computer for delegation
to specified services only

Use any authentication protocol
```

This enables protocol transition.

The relevant account-control flag is:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

Its `userAccountControl` value is:

```text
0x01000000
```

or:

```text
16777216
```

Protocol transition allows the service to obtain a Kerberos service ticket representing a user even when that user did not originally authenticate to the front-end using Kerberos.

---

# Why Protocol Transition Exists

Consider:

```text
User
 |
 | Forms authentication
 | Certificate
 | NTLM
 | Other front-end authentication
 v
WEB01
 |
 | Needs Kerberos identity
 v
SQL01
```

The front-end may still need to access:

```text
SQL01
```

using Kerberos as the user.

Protocol transition provides:

```text
Non-Kerberos Front-End Authentication
               |
               v
            S4U2Self
               |
               v
Kerberos Service Ticket for User
               |
               v
            S4U2Proxy
               |
               v
Configured Back-End Service
```

---

# S4U

Kerberos Service-for-User extensions are central to constrained delegation.

The two important operations are:

```text
S4U2Self
S4U2Proxy
```

A useful model is:

```text
S4U
 |
 +--> S4U2Self
 |
 +--> S4U2Proxy
```

---

# S4U2Self

S4U2Self allows a service to request a service ticket to itself on behalf of a user.

Conceptually:

```text
Front-End Service
       |
       | "Give me a ticket to myself
       | representing Alice"
       v
      KDC
       |
       v
Service Ticket
Alice -> Front-End
```

This allows the service to establish a Kerberos representation of the user.

---

# S4U2Proxy

S4U2Proxy allows the service to use an appropriate user service ticket to request another service ticket for a permitted backend service.

Conceptually:

```text
Alice -> WEB01 Ticket
        |
        v
      WEB01
        |
        | S4U2Proxy
        v
       KDC
        |
        v
Alice -> SQL01 Ticket
```

The destination is restricted by the delegation configuration.

---

# Complete S4U Flow

A simplified protocol-transition flow is:

```text
User
 |
 | Non-Kerberos Authentication
 v
WEB01
 |
 | S4U2Self
 v
KDC
 |
 v
Ticket:
Alice -> WEB01
 |
 | S4U2Proxy
 v
KDC
 |
 v
Ticket:
Alice -> SQL01
 |
 v
SQL01
```

The configured relationship is:

```text
WEB01
 |
 v
msDS-AllowedToDelegateTo
 |
 v
MSSQLSvc/sql01
```

---

# Security Significance of S4U

S4U exists for legitimate impersonation.

The security problem appears when:

```text
Delegating Account
        |
        v
Compromised
        |
        v
Attacker Controls Delegation Capability
        |
        v
User Impersonation
        |
        v
Configured Service
```

The attacker is still constrained by the services allowed by the delegation configuration.

However, those services may themselves be highly privileged.

---

# Constrained Does Not Mean Low Risk

Consider:

```text
svc_app
 |
 v
AllowedToDelegateTo
 |
 v
cifs/dc01.corp.example
```

If the account can obtain an impersonated service ticket for a sufficiently privileged user to:

```text
CIFS/DC01
```

the delegation scope is technically constrained, but the destination is extremely sensitive.

Therefore:

```text
Constrained
    !=
Automatically Safe
```

---

# Service Class Matters

The SPN's service class is important.

Examples:

```text
cifs/server01
ldap/dc01
http/web01
MSSQLSvc/sql01
host/server01
```

Different service classes provide different capabilities.

A delegation relationship to:

```text
MSSQLSvc/sql01
```

is not equivalent to:

```text
ldap/dc01
```

or:

```text
cifs/dc01
```

Impact analysis must therefore include the actual SPN.

---

# Enumeration Strategy

A practical workflow is:

```text
Active Directory
       |
       v
Find msDS-AllowedToDelegateTo
       |
       v
Identify Delegating Accounts
       |
   +---+---+
   |       |
   v       v
Users   Computers
   |       |
   +---+---+
       |
       v
Enumerate Destination SPNs
       |
       v
Check Protocol Transition
       |
       v
Analyse Account Privilege
       |
       v
Analyse Destination Services
       |
       v
BloodHound Attack Paths
```

---

# Windows - Active Directory PowerShell

Enumerate users with traditional constrained delegation:

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

---

# Enumerate Computers

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

# Search All Relevant Objects

A broader LDAP approach is:

```powershell
Get-ADObject \
    -LDAPFilter '(msDS-AllowedToDelegateTo=*)' \
    -Properties samAccountName,objectClass,msDS-AllowedToDelegateTo,userAccountControl |
    Select-Object \
        samAccountName,
        objectClass,
        msDS-AllowedToDelegateTo,
        userAccountControl
```

---

# Enumerate Protocol Transition

Search for:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

using the bit:

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

# Important Enumeration Nuance

Do not use only:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

to find constrained delegation.

Traditional constrained delegation may exist without protocol transition.

The broader indicator is:

```text
msDS-AllowedToDelegateTo
```

while:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

indicates the protocol-transition capability.

Therefore:

```text
msDS-AllowedToDelegateTo
        |
        v
Traditional Constrained Delegation


TRUSTED_TO_AUTH_FOR_DELEGATION
        |
        v
Protocol Transition Capability
```

---

# LDAP Matching Rule

The LDAP matching rule:

```text
1.2.840.113556.1.4.803
```

allows bitwise comparison.

The protocol-transition filter is:

```text
(userAccountControl:1.2.840.113556.1.4.803:=16777216)
```

---

# ldapsearch

From Linux, search for traditional constrained delegation using:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(msDS-AllowedToDelegateTo=*)' \
    sAMAccountName \
    objectClass \
    servicePrincipalName \
    msDS-AllowedToDelegateTo \
    userAccountControl
```

This directly exposes the configured destination services.

---

# LDAP Protocol Transition Query

Search for the protocol-transition flag:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(userAccountControl:1.2.840.113556.1.4.803:=16777216)' \
    sAMAccountName \
    servicePrincipalName \
    msDS-AllowedToDelegateTo \
    userAccountControl
```

---

# PowerView

PowerView can enumerate delegation relationships through LDAP-backed Active Directory queries.

A direct query is:

```powershell
Get-DomainUser \
    -LDAPFilter '(msDS-AllowedToDelegateTo=*)' \
    -Properties samaccountname,serviceprincipalname,msds-allowedtodelegateto,useraccountcontrol
```

For computers:

```powershell
Get-DomainComputer \
    -LDAPFilter '(msDS-AllowedToDelegateTo=*)' \
    -Properties samaccountname,dnshostname,serviceprincipalname,msds-allowedtodelegateto,useraccountcontrol
```

For protocol transition:

```powershell
Get-DomainObject \
    -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=16777216)' \
    -Properties samaccountname,msds-allowedtodelegateto,useraccountcontrol
```

PowerView forks and versions differ, so verify the installed implementation before relying on convenience switches.

---

# SPN Enumeration

After identifying a delegating account, inspect:

```text
msDS-AllowedToDelegateTo
```

Example:

```text
svc_web
 |
 +--> cifs/fileserver01.corp.example
 |
 +--> MSSQLSvc/sql01.corp.example:1433
```

Each SPN should be analysed individually.

---

# Native setspn

Inspect the SPNs belonging to the delegating account:

```powershell
setspn -L CORP\svc_web
```

For a computer:

```powershell
setspn -L WEB01
```

Remember that:

```text
ServicePrincipalName
```

and:

```text
msDS-AllowedToDelegateTo
```

serve different purposes.

The first describes services represented by the account.

The second describes services to which it may delegate.

---

# Linux - Impacket findDelegation

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

A typical enumeration pattern is:

```bash
impacket-findDelegation \
    'corp.example/alice:<PASSWORD>' \
    -dc-ip 10.10.10.10
```

The output can help distinguish:

```text
Unconstrained
Constrained
RBCD
```

and the relevant delegation configuration.

---

# Analyse findDelegation Output

For every result, identify:

```text
Account
Account Type
Delegation Type
Destination SPN
Protocol Transition
```

Do not stop at:

```text
Delegation found
```

The meaningful question is:

```text
Delegation to what?
```

---

# NetExec

NetExec LDAP can complement delegation enumeration.

Review:

```bash
nxc ldap --help
```

and:

```bash
nxc ldap -L
```

before relying on delegation-specific module names because available modules and syntax can change.

The general workflow is:

```text
NetExec
   |
   v
LDAP Enumeration
   |
   v
Delegation Relationships
   |
   v
Privilege Analysis
```

For detailed NetExec usage:

[NetExec](netexec.md)

---

# BloodHound

BloodHound is valuable because delegation should be analysed as an attack path rather than an isolated attribute.

The core questions are:

```text
Who controls the delegating account?
```

and:

```text
What service can it impersonate users to?
```

and:

```text
What can that service access?
```

---

# BloodHound Attack Path

A conceptual path is:

```text
Low-Privilege User
        |
        v
Controls svc_web
        |
        v
Constrained Delegation
        |
        v
CIFS/SERVER01
        |
        v
Privileged Service Access
```

The delegation configuration becomes exploitable when the delegating principal itself can be compromised.

---

# Account Control Matters

Suppose:

```text
svc_web
```

has constrained delegation.

Ask:

```text
Who can reset svc_web's password?

Who can modify svc_web?

Who owns svc_web?

Who has GenericAll?

Who has GenericWrite?

Who has WriteDACL?

Who has WriteOwner?

Who controls the host where svc_web runs?
```

These relationships may transform a delegation configuration into a practical privilege-escalation path.

---

# BloodHound Questions

For every delegation account:

```text
Which principal controls it?
        |
        v
Which SPNs are allowed?
        |
        v
Which systems host those SPNs?
        |
        v
Are those systems high-value?
        |
        v
Can privileged users be impersonated?
        |
        v
What access would the resulting
service ticket provide?
```

---

# Credential Requirement

To actively use traditional constrained delegation as the delegating account, an attacker normally needs usable authentication material for that account.

This might be:

```text
Password
NT Hash / RC4 Key
AES Key
Kerberos Ticket
```

depending on the workflow.

Therefore:

```text
Delegation Configuration
        |
        X
Immediate Exploitation
```

without control of the delegating identity.

The more complete path is:

```text
Delegation Account
       |
       v
Credential / Account Compromise
       |
       v
Delegation Capability
       |
       v
User Impersonation
       |
       v
Configured Service
```

---

# Controlled S4U Validation

During an authorised assessment, a controlled validation may demonstrate:

```text
Controlled Delegation Account
            |
            v
Request Ticket
            |
            v
S4U
            |
            v
Controlled Test User
            |
            v
Configured Backend Service
            |
            v
Authentication
```

Prefer a dedicated test identity rather than a privileged production user whenever this sufficiently proves the finding.

---

# Rubeus

Rubeus supports extensive Kerberos and S4U testing on Windows.

Its S4U functionality can be used in authorised environments to evaluate constrained delegation.

A conceptual workflow is:

```text
Delegating Account Key
         |
         v
        TGT
         |
         v
       S4U2Self
         |
         v
User -> Delegating Service Ticket
         |
         v
       S4U2Proxy
         |
         v
User -> Allowed Backend Service
```

Because Rubeus evolves over time, review the current help and official repository before using exact command syntax.

---

# Impacket getST

Impacket provides:

```text
getST.py
```

commonly installed as:

```text
impacket-getST
```

It supports Kerberos service-ticket workflows including delegation scenarios.

Check the current options first:

```bash
impacket-getST -h
```

For an explicitly authorised constrained-delegation test, the general workflow is:

```text
Delegating Account
       |
       v
Impacket getST
       |
       v
S4U Request
       |
       v
Impersonated User
       |
       v
Configured SPN
       |
       v
.ccache
```

---

# Controlled Impacket Pattern

Where explicitly authorised and using a dedicated test account, the current Impacket `getST` utility can be used with an impersonated identity and target SPN.

A general pattern is:

```bash
impacket-getST \
    -spn '<SERVICE>/<TARGET_FQDN>' \
    -impersonate '<TEST_USER>' \
    'corp.example/<DELEGATING_ACCOUNT>:<PASSWORD>'
```

For example, in a controlled lab:

```bash
impacket-getST \
    -spn 'cifs/server01.corp.example' \
    -impersonate 'pt-test-user' \
    'corp.example/svc_test:<PASSWORD>'
```

Do not copy real credentials into documentation or shell history.

Use supported password-prompting or alternative credential mechanisms where practical.

---

# Resulting Ticket

A successful request may create a Kerberos credential cache such as:

```text
pt-test-user@cifs_server01.corp.example@CORP.EXAMPLE.ccache
```

The exact filename depends on the tool version and requested service.

Treat it as a credential.

---

# Use KRB5CCNAME

Where a controlled test requires validating the resulting ticket:

```bash
export KRB5CCNAME="$PWD/<TICKET>.ccache"
```

Inspect:

```bash
klist
```

Confirm:

```text
Client Principal
Service Principal
Start Time
Expiration
Encryption Type
```

---

# Minimum-Impact Service Validation

If the ticket is for:

```text
cifs/server01.corp.example
```

a low-impact validation may use:

```bash
impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/<TEST_USER>@server01.corp.example'
```

The objective is:

```text
Delegation
    |
    v
Impersonated Service Ticket
    |
    v
Authentication Proven
```

not:

```text
Immediately execute commands
```

---

# Hostname and SPN

Use the hostname represented by the ticket.

Prefer:

```text
server01.corp.example
```

rather than:

```text
10.10.10.25
```

when Kerberos is intended.

The ticket might contain:

```text
cifs/server01.corp.example
```

and therefore depends on the correct service identity.

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

Kerberos troubleshooting should always include:

```text
DNS
Time
Realm
SPN
KDC
Ticket
```

---

# Time Synchronisation

Check:

```bash
date
```

On Windows:

```powershell
w32tm /query /status
```

Kerberos authentication is time-sensitive.

---

# SPN Target Analysis

A delegation relationship such as:

```text
cifs/server01.corp.example
```

may allow authentication to SMB-related functionality on:

```text
SERVER01
```

A relationship such as:

```text
ldap/dc01.corp.example
```

targets LDAP on a domain controller.

A relationship such as:

```text
MSSQLSvc/sql01.corp.example:1433
```

targets SQL Server.

Therefore:

```text
Allowed SPN
     |
     v
Service Capability
     |
     v
Account Privilege
     |
     v
Impact
```

---

# Service Tickets Are Service-Specific

A ticket for:

```text
MSSQLSvc/sql01
```

is not simply a generic administrator credential.

The normal Kerberos model is:

```text
Service Ticket
      |
      v
Specific SPN
```

This distinction should remain clear in reporting.

---

# Service-Class Substitution

Delegation assessments sometimes encounter situations where service-class handling and host-account SPNs create broader practical impact than the originally displayed delegation entry might suggest.

This is highly environment-dependent.

Do not automatically report:

```text
Allowed SPN
    =
Every service on host
```

Instead validate:

```text
Account owning SPN
        |
        v
Registered SPNs
        |
        v
Kerberos service behaviour
        |
        v
Actual accepted ticket
```

Only report capabilities that were demonstrated or strongly supported by the configuration.

---

# Sensitive Users

Some identities should not be delegatable.

Active Directory provides:

```text
Account is sensitive and cannot be delegated
```

which corresponds to:

```text
NOT_DELEGATED
```

The `userAccountControl` bit is:

```text
0x00100000
```

or:

```text
1048576
```

---

# Enumerate Sensitive Users

Using PowerShell:

```powershell
Get-ADUser \
    -Filter {AccountNotDelegated -eq $true} \
    -Properties AccountNotDelegated |
    Select-Object \
        SamAccountName,
        AccountNotDelegated
```

Check a particular account:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties AccountNotDelegated |
    Select-Object \
        SamAccountName,
        AccountNotDelegated
```

---

# Protected Users

Membership in:

```text
Protected Users
```

provides additional authentication protections for suitable sensitive accounts.

Protected Users should be considered during delegation analysis because some delegation scenarios that work for ordinary users may behave differently for protected identities.

Do not treat a failed impersonation of a protected user as proof that the entire delegation configuration is harmless.

---

# User Impersonation Scope

The security question is not merely:

```text
Can I impersonate Administrator?
```

A better model is:

```text
Which users can be represented?
        |
        v
Which are protected?
        |
        v
Which destination service is allowed?
        |
        v
What permissions does that user
have at the destination?
```

---

# Constrained Delegation vs Unconstrained Delegation

Unconstrained:

```text
Compromised Service
       |
       v
Broad Delegation Capability
```

Constrained:

```text
Compromised Service
       |
       v
Configured Backend SPNs
```

Comparison:

| Property | Unconstrained | Constrained |
|---|---|---|
| Backend scope | Broad | Explicit |
| Primary configuration | `TRUSTED_FOR_DELEGATION` | `msDS-AllowedToDelegateTo` |
| S4U commonly relevant | Not central | Yes |
| Protocol transition | Not defining feature | Optional |
| Risk | Broad credential exposure | Targeted impersonation |

For detailed coverage:

[Unconstrained Delegation](unconstrained-delegation.md)

---

# Constrained Delegation vs RBCD

Traditional constrained delegation defines:

```text
Front-End
   |
   v
Where may I delegate?
```

using:

```text
msDS-AllowedToDelegateTo
```

RBCD defines:

```text
Back-End
   |
   v
Who may delegate to me?
```

using:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

The direction of trust is fundamentally different.

---

# Traditional KCD

```text
WEB01
 |
 v
msDS-AllowedToDelegateTo
 |
 v
SQL01
```

The delegation setting is controlled on:

```text
WEB01
```

---

# RBCD

```text
SQL01
 |
 v
msDS-AllowedToActOnBehalfOfOtherIdentity
 |
 v
WEB01 may delegate
```

The delegation setting is controlled on:

```text
SQL01
```

This distinction is central to understanding RBCD attack paths.

---

# Constrained Delegation vs Pass-the-Ticket

Constrained delegation:

```text
Delegation Account
       |
       v
S4U
       |
       v
Obtain Service Ticket
```

Pass-the-Ticket:

```text
Existing Ticket
       |
       v
Reuse Ticket
```

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# Constrained Delegation vs Pass-the-Key

Pass-the-Key uses long-term Kerberos key material to obtain tickets.

Constrained delegation determines what impersonation capabilities an account has after it can authenticate.

```text
Kerberos Key
     |
     v
Authenticate as
Delegation Account
     |
     v
Constrained Delegation
     |
     v
S4U
```

See:

[Pass-the-Key](pass-the-key.md)

---

# Constrained Delegation vs Kerberoasting

Kerberoasting:

```text
SPN
 |
 v
Request Service Ticket
 |
 v
Offline Password Guessing
```

Constrained delegation:

```text
Delegating Principal
 |
 v
S4U
 |
 v
Impersonated Service Ticket
```

The two techniques use Kerberos for very different purposes.

See:

[Kerberoasting](kerberoasting.md)

---

# Delegation and Account Compromise

The most important practical question is often:

```text
Can the delegating account be compromised?
```

Potential paths include:

```text
Weak service-account password
        |
        v
Kerberoasting
```

```text
Excessive ACL
        |
        v
Password Reset / Key Control
```

```text
Compromised Server
        |
        v
Service Credential Exposure
```

```text
Credential Reuse
        |
        v
Delegating Account Compromise
```

Delegation should therefore be analysed together with broader Active Directory privilege relationships.

---

# Example Attack Chain

```text
Low-Privilege User
       |
       v
Kerberoast svc_web
       |
       v
Service Password Recovered
       |
       v
svc_web Has Constrained Delegation
       |
       v
S4U User Impersonation
       |
       v
CIFS/SERVER01
       |
       v
Privileged Access
```

This demonstrates why a seemingly moderate service-account weakness can become a major privilege-escalation path.

---

# ACL-Based Attack Chain

Another example:

```text
User Alice
   |
   v
GenericAll over svc_web
   |
   v
Control svc_web
   |
   v
Constrained Delegation
   |
   v
Impersonate User
   |
   v
Configured Backend Service
```

BloodHound is particularly useful for identifying these combinations.

---

# Machine Account Delegation

Computer accounts can also have constrained delegation.

Example:

```text
WEB01$
 |
 v
msDS-AllowedToDelegateTo
 |
 v
cifs/FILE01
```

Compromise of:

```text
WEB01
```

may therefore provide control over the machine account's delegation capability.

Do not enumerate only user service accounts.

---

# Protocol Transition Risk

Protocol transition is particularly important because:

```text
User did not need to
authenticate with Kerberos
        |
        v
Front-End Service
        |
        v
S4U2Self
        |
        v
Kerberos Representation
```

Therefore, the service can potentially create a Kerberos representation of a user after authenticating that user through another mechanism.

This is expected functionality but expands the consequences of compromise of the front-end service.

---

# Authentication Protocol Is Not the Main Security Boundary

With protocol transition:

```text
User Authentication Method
       |
       X
Must be Kerberos
```

The important trust boundary becomes:

```text
Can the service legitimately
assert this user's identity?
```

This is why:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

deserves careful review.

---

# Delegation to Domain Controllers

Destination SPNs involving domain controllers deserve particular attention.

Examples:

```text
ldap/dc01.corp.example
cifs/dc01.corp.example
host/dc01.corp.example
```

The exact risk depends on:

```text
Service
Impersonated User
Permissions
Environment
```

Do not assign severity based solely on the hostname being a domain controller, but treat the relationship as high priority for analysis.

---

# Delegation to File Servers

Example:

```text
cifs/fileserver01.corp.example
```

Potential impact depends on the impersonated user's access to:

```text
Shares
Administrative shares
Sensitive files
Backup data
Deployment packages
Configuration files
```

---

# Delegation to SQL Server

Example:

```text
MSSQLSvc/sql01.corp.example:1433
```

Impact depends on:

```text
SQL login mapping
Database roles
Server roles
Impersonated user's SQL privileges
Linked servers
Application permissions
```

---

# Delegation to HTTP

Example:

```text
HTTP/app01.corp.example
```

Potential impact depends entirely on the application using Kerberos authentication.

Do not assume:

```text
HTTP ticket
    =
Server administrator
```

---

# Delegation to LDAP

Example:

```text
ldap/dc01.corp.example
```

This deserves careful privilege analysis because LDAP exposes Active Directory operations.

The ticket only represents the permissions of the impersonated identity.

Therefore:

```text
LDAP Ticket
     +
Low-Privilege User
     =
Low-Privilege LDAP Access
```

whereas:

```text
LDAP Ticket
     +
Highly Privileged User
     =
Potentially High-Impact AD Access
```

---

# Safe Testing Strategy

Use:

```text
Enumeration
    |
    v
Identify Delegation
    |
    v
Analyse Account Control
    |
    v
Analyse Destination
    |
    v
Use Test User
    |
    v
Request Single Service Ticket
    |
    v
Validate Authentication
    |
    v
Stop
```

Avoid:

```text
Immediately impersonating
Domain Admin
```

when a test identity proves the same security condition.

---

# When Active Exploitation Is Unnecessary

Suppose you establish:

```text
svc_test
 |
 v
Constrained Delegation
 |
 v
cifs/server01
```

and:

```text
Tester controls svc_test
```

The combination may already provide strong evidence of the attack path.

Depending on engagement requirements, a controlled service-ticket request using a dedicated user may be enough.

---

# Evidence of Configuration

Strong configuration evidence includes:

```text
Delegating Account
Object Type
msDS-AllowedToDelegateTo
TRUSTED_TO_AUTH_FOR_DELEGATION
SPNs
Destination Host
Destination Service
```

This is preferable to unnecessary destructive proof.

---

# Detection

Detection should cover:

```text
Delegation Configuration
       |
       +
Kerberos S4U Activity
       |
       +
Service Authentication
       |
       +
Endpoint Behaviour
```

---

# Event 4768

Event:

```text
4768
```

records TGT requests.

It can help identify authentication by the delegating account.

Useful context includes:

```text
Account
Client Address
Encryption Type
Pre-Authentication Type
```

---

# Event 4769

Event:

```text
4769
```

records service-ticket requests.

This is particularly important for constrained delegation because S4U workflows ultimately involve service-ticket requests.

Analyse:

```text
Account
Service Name
Client Address
Ticket Options
Ticket Encryption Type
Result
```

---

# Event 4624

The backend Windows service may generate:

```text
4624
```

when the resulting Kerberos authentication is accepted.

Correlate:

```text
4769 on DC
     |
     v
4624 on Backend
```

where possible.

---

# Event 4672

If the impersonated identity receives privileged rights on the backend:

```text
4672
```

may provide useful context.

Do not treat it as a delegation-specific event.

---

# Event 5136

Directory Service Changes auditing can generate:

```text
5136
```

when Active Directory attributes are modified.

Monitor changes involving:

```text
msDS-AllowedToDelegateTo
```

and delegation-related:

```text
userAccountControl
```

values.

---

# Configuration Monitoring

Maintain a baseline of:

```text
Delegating Account
        |
        v
Allowed Destination SPNs
        |
        v
Protocol Transition?
```

Example:

```text
Account     Destination                     Protocol Transition
-----------------------------------------------------------------
svc_web     MSSQLSvc/sql01:1433             No
WEB02$      cifs/fileserver01               Yes
```

Unexpected changes should be investigated.

---

# Monitor New Delegation Relationships

A useful defensive workflow is:

```text
Scheduled AD Enumeration
        |
        v
Current Delegation
        |
        v
Compare to Baseline
        |
     +--+--+
     |     |
    Same  Changed
           |
           v
        Investigate
```

---

# Detect Protocol Transition Changes

Changes introducing:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

should be reviewed.

Ask:

```text
Who changed it?

Why?

Which account?

Which destination SPNs?

Was a change request approved?
```

---

# Behavioural Detection

Because S4U is legitimate Kerberos functionality:

```text
S4U Activity
     |
     X
Automatically Malicious
```

Detection should consider:

```text
Delegating Account
       |
       v
Normal Source Host?
       |
       v
Expected User?
       |
       v
Expected Destination?
       |
       v
Expected Time?
       |
       v
Expected Volume?
```

---

# Endpoint Detection

If the delegating account is compromised through an endpoint, telemetry may include:

```text
Credential access
Service-account credential theft
Suspicious Kerberos tooling
Unexpected processes
Ticket manipulation
Remote administration
```

Correlate endpoint events with domain-controller Kerberos telemetry.

---

# Purple Team Exercise

A controlled exercise can use:

```text
Test Delegation Account
        |
        v
Configured Test Service
        |
        v
Test User
        |
        v
S4U Ticket Request
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
Which account requested the tickets?

Which user was represented?

Which service was targeted?

Was protocol transition involved?

Was the delegation configuration expected?

Was the source host expected?

Was the resulting backend access expected?

Can the team identify how the
delegation account was compromised?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect
Time to identify delegating account
Time to identify impersonated user
Time to identify target SPN
Time to identify source host
Time to reconstruct S4U flow
Time to identify configuration
Correct containment decision?
Correct remediation selected?
```

---

# Hardening

The primary defensive model is:

```text
Delegation Required?
       |
   +---+---+
   |       |
  No      Yes
   |       |
   v       v
Remove   Minimise Scope
           |
           v
      Protect Account
           |
           v
      Protect Users
           |
           v
       Monitor
```

---

# Remove Unnecessary Delegation

If the application no longer requires delegation:

```text
Remove
msDS-AllowedToDelegateTo
```

and remove associated delegation flags where appropriate.

Do not make production changes during an assessment unless explicitly authorised.

---

# Minimise Delegation Scope

Avoid broad destination lists.

Bad:

```text
svc_app
 |
 +--> cifs/server01
 +--> cifs/server02
 +--> cifs/server03
 +--> ldap/dc01
 +--> ldap/dc02
 +--> http/app01
 +--> MSSQLSvc/sql01
```

if the application only requires:

```text
MSSQLSvc/sql01
```

Apply:

```text
Minimum Required SPNs
```

---

# Avoid Sensitive Destination Services

Review delegation to:

```text
Domain Controllers
Management Servers
Backup Infrastructure
Certificate Services
Deployment Systems
Identity Infrastructure
```

with particular care.

---

# Protect Delegating Accounts

Service accounts with delegation rights should be treated as sensitive identities.

Apply:

```text
Strong unique credentials
Long random passwords
gMSA where appropriate
Restricted logon rights
Least privilege
Credential isolation
Monitoring
```

---

# gMSA

Where application compatibility allows, Group Managed Service Accounts can reduce risks associated with manually managed service-account passwords.

A gMSA provides automatically managed long, complex credentials.

Conceptually:

```text
Traditional Service Account
        |
        v
Human-Managed Password
        |
        v
Reuse / Weakness / Age Risk
```

versus:

```text
gMSA
 |
 v
Automatically Managed
Credential
```

Delegation permissions still require review even when a gMSA is used.

---

# Protect the Host

If a machine account has delegation rights, protecting the host itself is critical.

Apply:

```text
Patching
EDR
Application control
Least privilege
Restricted administration
Network segmentation
Credential protection
```

---

# Protect Sensitive Users

For appropriate high-value accounts:

```text
Account is sensitive and cannot be delegated
```

can reduce delegation exposure.

Example PowerShell configuration where explicitly authorised:

```powershell
Set-ADAccountControl \
    -Identity '<USERNAME>' \
    -AccountNotDelegated $true
```

Operational compatibility should be assessed before deployment.

---

# Protected Users

Consider:

```text
Protected Users
```

for suitable privileged human accounts.

Do not blindly place:

```text
Service Accounts
Application Accounts
Legacy Identities
```

into Protected Users without compatibility analysis.

---

# Administrative Tiering

Prevent highly privileged identities from authenticating through lower-trust application tiers.

Bad:

```text
Domain Admin
    |
    v
WEB01
    |
    v
Delegation
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

Use dedicated administrative systems for Tier 0 administration.

This reduces:

```text
Privileged Authentication
        |
        v
Application Servers
```

and therefore reduces delegation exposure.

---

# ACL Hardening

Protect the delegating account itself.

Review who has:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
Reset Password
WriteProperty
```

over:

```text
Delegation Accounts
```

An attacker who can control the account may gain control of its delegation capability.

---

# Protect Delegation Attributes

Monitor and restrict write access to:

```text
msDS-AllowedToDelegateTo
```

and:

```text
userAccountControl
```

Delegation configuration should be controlled through tightly managed administrative processes.

---

# Network Segmentation

A resulting service ticket should not automatically provide network access from arbitrary systems.

Example:

```text
User Workstation Network
        |
        X
Management SMB
        |
        v
Sensitive Server
```

Network controls provide an additional barrier even when authentication material is compromised.

---

# Incident Response

If a constrained-delegation account is compromised:

```text
Delegation Account Compromised
          |
          v
Identify Account
          |
          v
Identify Allowed SPNs
          |
          v
Identify Protocol Transition
          |
          v
Identify Potentially Impersonated Users
          |
          v
Review 4768 / 4769
          |
          v
Review Backend Authentication
          |
          v
Contain Account / Host
          |
          v
Rotate Credential
          |
          v
Review Delegation Requirement
          |
          v
Investigate Lateral Movement
```

---

# Credential Rotation

If the delegating account's long-term credential is compromised:

```text
Password / Key
      |
      v
Rotate
      |
      v
New Key Material
```

For machine accounts and managed service accounts, follow the appropriate Active Directory recovery procedures rather than manually changing credentials without understanding dependencies.

---

# Remove Attacker-Added Delegation

If incident response discovers unauthorised:

```text
msDS-AllowedToDelegateTo
```

changes:

```text
Preserve Evidence
      |
      v
Identify Change Source
      |
      v
Identify Affected Account
      |
      v
Remove Malicious Configuration
      |
      v
Rotate Relevant Credentials
      |
      v
Hunt for Ticket Abuse
```

---

# Reporting

Possible finding titles include:

```text
Constrained Kerberos Delegation Enables Privileged User Impersonation
```

```text
Excessive Kerberos Delegation Rights Assigned to Service Account
```

```text
Compromised Service Account Can Impersonate Users to Sensitive Service
```

```text
Kerberos Protocol Transition Enabled for High-Risk Service Account
```

---

# Avoid Overstatement

Do not report:

```text
msDS-AllowedToDelegateTo exists
        =
Domain Compromise
```

Instead establish:

```text
Delegating Account
       |
       v
Can Tester Control It?
       |
       v
Allowed Destination
       |
       v
Impersonatable User
       |
       v
User Privileges at Destination
       |
       v
Actual Impact
```

---

# Example Finding

```text
Finding:
Constrained Kerberos Delegation Enables User Impersonation to Sensitive Service

Affected Account:
CORP\svc_web

Delegation Destination:
cifs/server01.corp.example

Protocol Transition:
Enabled

Description:
The affected service account is configured for Kerberos constrained
delegation to the CIFS service on SERVER01.

The account is additionally configured for protocol transition,
allowing the service to obtain Kerberos authentication material
representing users even where the original front-end authentication
was not performed using Kerberos.

During the authorised assessment, control of the delegation account
was demonstrated using dedicated test credentials.

A service ticket representing a controlled test user was requested for
the configured CIFS service and used to authenticate successfully to
the designated test server.

No remote command execution was required to demonstrate the issue.

Impact:
An attacker who compromises the affected delegation account may be able
to impersonate users to the configured backend service.

The actual impact depends on the privileges held by the impersonated
identity on SERVER01.

Recommendation:
Confirm whether the delegation relationship remains operationally
required.

Remove unnecessary delegation, minimise the permitted destination SPNs,
protect the service account using strong managed credentials, restrict
who can modify the account and delegation attributes, protect sensitive
users from delegation where appropriate, and monitor changes to
delegation-related Active Directory attributes.
```

---

# Evidence Collection

Record:

```text
Delegating Account
Account Type
Distinguished Name
ServicePrincipalName
msDS-AllowedToDelegateTo
userAccountControl
TRUSTED_TO_AUTH_FOR_DELEGATION
Destination SPN
Destination Host
Destination Service
Test User
Ticket Type
Ticket Lifetime
Authentication Result
Privilege Level
BloodHound Relationships
Relevant Event IDs
Tool
Command
Timestamp
```

---

# Evidence Redaction

Treat resulting:

```text
.ccache
.kirbi
TGT
Service Ticket
NT Hash
AES Key
Password
```

as sensitive credentials.

Reports should use:

```text
[REDACTED]
```

rather than reusable authentication material.

---

# Cleanup

On Linux:

```bash
unset KRB5CCNAME
```

Where appropriate:

```bash
kdestroy
```

Remove temporary test ticket caches according to the engagement evidence-retention policy:

```bash
rm -f <TICKET>.ccache
```

On a dedicated Windows test session:

```powershell
klist
```

and, where appropriate:

```powershell
klist purge
```

Remember that purging tickets can disrupt the current logon session.

---

# Troubleshooting

## No Delegation Results

Possible reasons:

```text
No traditional constrained delegation

Only RBCD is used

Incorrect LDAP search base

Insufficient directory access

Wrong domain controller

LDAP query incorrect
```

Cross-check with:

```text
PowerShell
LDAP
Impacket
BloodHound
```

---

# findDelegation Returns Nothing

Check:

```bash
impacket-findDelegation -h
```

Then verify:

```text
Domain
Credentials
DNS
DC IP
Time
LDAP access
```

---

# S4U Request Fails

Check:

```text
Delegating account credentials
Delegation configuration
Target SPN
Impersonated user
Protocol transition mode
KDC reachability
DNS
Time
```

---

# KDC_ERR_BADOPTION

A Kerberos error involving unsupported or invalid ticket options can indicate that the requested delegation operation is not permitted by the current ticket or delegation configuration.

Investigate:

```text
Forwardability
Delegation Type
User Protection
Target SPN
S4U Requirements
```

rather than repeatedly changing unrelated parameters.

---

# KDC_ERR_S_PRINCIPAL_UNKNOWN

This commonly indicates a service-principal problem.

Check:

```powershell
setspn -Q <SPN>
```

For example:

```powershell
setspn -Q cifs/server01.corp.example
```

Confirm:

```text
SPN exists
SPN spelling
Hostname
Service class
Port where relevant
```

---

# KDC_ERR_ETYPE_NOSUPP

This indicates an encryption-type compatibility issue.

Review:

```text
Account keys
Domain Kerberos policy
RC4 availability
AES availability
Tool configuration
```

Do not weaken domain encryption settings merely to make a test work.

---

# Clock Skew

Check Linux:

```bash
date
```

Windows:

```powershell
w32tm /query /status
```

Kerberos is sensitive to time differences.

---

# DNS Failure

Check:

```bash
getent hosts dc01.corp.example
```

and:

```bash
getent hosts server01.corp.example
```

Use FQDNs when Kerberos is intended.

---

# Ticket Obtained but Authentication Fails

Inspect:

```bash
klist
```

Check:

```text
Client Principal
Service Principal
Expiration
Realm
```

Then verify:

```text
Hostname
SPN
Target service
User authorisation
```

---

# Authentication Works but Access Is Denied

Remember:

```text
Authentication
      !=
Authorisation
```

The impersonated user may authenticate successfully while lacking permissions to the requested resource.

---

# Protected User Cannot Be Impersonated

This may be expected.

Check:

```text
AccountNotDelegated
Protected Users
Delegation restrictions
```

Do not remove defensive protections simply to make the test succeed.

---

# Wrong Service Ticket

A ticket for:

```text
MSSQLSvc/sql01
```

is not automatically suitable for:

```text
cifs/sql01
```

Kerberos tickets are associated with service principals.

---

# Common Mistakes

## Mistake 1 - Confusing Constrained and Unconstrained Delegation

```text
Unconstrained
     =
Broad


Constrained
     =
Specific SPNs
```

---

## Mistake 2 - Confusing KCD and RBCD

```text
KCD
 |
 v
Front-End defines destinations


RBCD
 |
 v
Back-End defines trusted delegators
```

---

## Mistake 3 - Looking Only for TRUSTED_TO_AUTH_FOR_DELEGATION

This finds protocol-transition capability, not every constrained-delegation configuration.

Also enumerate:

```text
msDS-AllowedToDelegateTo
```

---

## Mistake 4 - Assuming Protocol Transition Is Always Enabled

Traditional constrained delegation can operate with:

```text
Kerberos only
```

without:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

---

## Mistake 5 - Ignoring Computer Accounts

Both:

```text
Users
Computers
```

can be delegation principals.

---

## Mistake 6 - Ignoring Destination SPNs

The destination service determines much of the impact.

---

## Mistake 7 - Assuming Every SPN Gives Administrative Access

```text
Service Ticket
      |
      v
Service-Specific Authentication
```

not automatically:

```text
Host Administrator
```

---

## Mistake 8 - Ignoring Account Control Paths

The delegation configuration becomes much more dangerous if a low-privileged principal can control the delegating account.

---

## Mistake 9 - Ignoring Protected Users

High-value identities may have protections that prevent expected delegation behaviour.

---

## Mistake 10 - Testing with Domain Admin Immediately

Use a dedicated test identity where possible.

---

## Mistake 11 - Confusing S4U2Self and S4U2Proxy

```text
S4U2Self
     =
Service obtains ticket to itself
representing user


S4U2Proxy
     =
Service obtains ticket to
permitted backend service
representing user
```

---

## Mistake 12 - Ignoring Protocol Transition

`TRUSTED_TO_AUTH_FOR_DELEGATION` materially changes the front-end authentication requirements.

---

## Mistake 13 - Ignoring Kerberos Basics

Always check:

```text
DNS
Time
Realm
KDC
SPN
Ticket
```

---

## Mistake 14 - Performing Remote Execution When Authentication Is Enough

A valid delegated service ticket and successful authentication may already demonstrate the security impact.

---

## Mistake 15 - Reporting Delegation Without Root Cause

If exploitation depends on:

```text
Weak svc_web Password
```

or:

```text
GenericAll over svc_web
```

report the complete attack chain.

---

# Assessment Checklist

## Preparation

- [ ] Confirm delegation testing is authorised
- [ ] Confirm domains
- [ ] Confirm accounts
- [ ] Confirm systems
- [ ] Confirm allowed impersonation identities
- [ ] Confirm allowed destination services
- [ ] Confirm whether active S4U testing is permitted
- [ ] Confirm remote execution restrictions
- [ ] Identify domain controller
- [ ] Verify DNS
- [ ] Verify time

## Enumeration

- [ ] Query `msDS-AllowedToDelegateTo`
- [ ] Enumerate user accounts
- [ ] Enumerate computer accounts
- [ ] Enumerate destination SPNs
- [ ] Query `TRUSTED_TO_AUTH_FOR_DELEGATION`
- [ ] Record `userAccountControl`
- [ ] Identify protocol transition
- [ ] Enumerate service SPNs
- [ ] Run `impacket-findDelegation`
- [ ] Review NetExec capabilities
- [ ] Collect BloodHound data

## Delegating Account Analysis

- [ ] Identify account type
- [ ] Identify service purpose
- [ ] Determine credential exposure
- [ ] Review password age
- [ ] Review Kerberoasting exposure
- [ ] Review ACL control
- [ ] Review local host compromise paths
- [ ] Review gMSA usage
- [ ] Determine who administers the account

## Destination Analysis

- [ ] Identify service class
- [ ] Identify destination host
- [ ] Determine whether destination is Tier 0
- [ ] Determine user permissions
- [ ] Review network reachability
- [ ] Review service exposure
- [ ] Determine realistic impact

## User Protection

- [ ] Check `AccountNotDelegated`
- [ ] Check Protected Users
- [ ] Identify privileged identities
- [ ] Avoid unnecessary privileged impersonation

## Controlled Validation

- [ ] Use dedicated test identity
- [ ] Request only required service ticket
- [ ] Verify resulting principal
- [ ] Verify destination SPN
- [ ] Validate authentication only where sufficient
- [ ] Avoid unnecessary remote execution
- [ ] Protect resulting ticket
- [ ] Stop after impact is proven

## Detection

- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4624
- [ ] Review 4672 where relevant
- [ ] Review 5136
- [ ] Monitor `msDS-AllowedToDelegateTo`
- [ ] Monitor `userAccountControl`
- [ ] Baseline delegation relationships
- [ ] Monitor unexpected S4U activity
- [ ] Correlate endpoint telemetry

## Remediation

- [ ] Confirm delegation is required
- [ ] Remove unnecessary delegation
- [ ] Minimise allowed SPNs
- [ ] Remove unnecessary protocol transition
- [ ] Protect delegating account
- [ ] Use gMSA where appropriate
- [ ] Protect sensitive users
- [ ] Consider Protected Users
- [ ] Harden account ACLs
- [ ] Harden delegation hosts
- [ ] Segment backend services
- [ ] Monitor configuration changes

## Cleanup

- [ ] Unset `KRB5CCNAME`
- [ ] Destroy temporary ticket cache
- [ ] Remove `.ccache`
- [ ] Remove `.kirbi`
- [ ] Purge dedicated Windows test-session tickets where appropriate
- [ ] Secure retained evidence
- [ ] Redact reusable credentials
- [ ] Confirm no unintended AD changes

---

# Constrained Delegation Testing Model

The architectural model is:

```text
                          User
                           |
                           v
                    Front-End Service
                           |
                           v
                    Delegating Account
                           |
                           v
                msDS-AllowedToDelegateTo
                           |
                           v
                     Approved SPN
                           |
                           v
                    Back-End Service
```

The Kerberos-only model is:

```text
User
 |
 | Kerberos
 v
Front-End
 |
 | Delegation
 v
Configured Backend
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
Ticket Representing User
to Front-End
 |
 | S4U2Proxy
 v
Ticket Representing User
to Allowed Backend
 |
 v
Backend Service
```

The configuration relationship is:

```text
                  Delegating Account
                         |
            +------------+------------+
            |                         |
            v                         v
msDS-AllowedToDelegateTo     userAccountControl
            |                         |
            v                         v
    Destination SPNs        TRUSTED_TO_AUTH_FOR_DELEGATION
                                      |
                                      v
                              Protocol Transition
```

The attack-path model is:

```text
Low-Privilege Principal
        |
        v
Control Delegating Account
        |
        v
Delegation Capability
        |
        v
S4U User Impersonation
        |
        v
Configured Backend SPN
        |
        v
Impersonated User Permissions
        |
        v
Potential Privilege Expansion
```

The comparison model is:

```text
                         Delegation
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
   Unconstrained        Constrained            RBCD
          |                  |                  |
          v                  v                  v
     Broad Scope       Explicit SPNs       Resource-Side
                                            Trust
```

The defensive model is:

```text
Constrained Delegation
        |
        +--> Is It Required?
        |       |
        |       +--> No -> Remove
        |       |
        |       +--> Yes
        |              |
        |              v
        |        Minimise SPNs
        |
        +--> Protect Delegating Account
        |       |
        |       +--> Strong Credentials
        |       +--> gMSA
        |       +--> ACL Hardening
        |
        +--> Protect Users
        |       |
        |       +--> NOT_DELEGATED
        |       +--> Protected Users
        |
        +--> Protect Backend
        |       |
        |       +--> Least Privilege
        |       +--> Segmentation
        |
        +--> Monitor
                |
                +--> 4768
                +--> 4769
                +--> 4624
                +--> 5136
                +--> Delegation Changes
```

A mature assessment should answer:

```text
Which accounts have constrained delegation?
        |
        v
Which destination SPNs are configured?
        |
        v
Is protocol transition enabled?
        |
        v
Who controls the delegating account?
        |
        v
Can its credential be compromised?
        |
        v
Which users can be represented?
        |
        v
Which users are protected?
        |
        v
What access does the resulting
service ticket provide?
        |
        v
Can defenders identify the
delegation activity?
        |
        v
Can the relationship be removed
or reduced?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos tickets:

[Kerberos Tickets](kerberos-tickets.md)

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

The following topics complement constrained delegation and can be linked once their dedicated notes are available:

```text
active-directory/rbcd.md
active-directory/s4u.md
active-directory/authentication-coercion.md
active-directory/acl-ace.md
active-directory/golden-ticket.md
active-directory/silver-ticket.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft Kerberos

[Microsoft - Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Protocol Extensions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Constrained Delegation overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-constrained-delegation-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft S4U

[Microsoft - Service for User and Constrained Delegation Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/){ target="_blank" rel="noopener noreferrer" }

---

## Active Directory Attributes

[Microsoft - msDS-AllowedToDelegateTo](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-allowedtodelegateto){ target="_blank" rel="noopener noreferrer" }

[Microsoft - ADS_USER_FLAG_ENUM](https://learn.microsoft.com/en-us/windows/win32/api/iads/ne-iads-ads_user_flag_enum){ target="_blank" rel="noopener noreferrer" }

[Microsoft - userAccountControl](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties){ target="_blank" rel="noopener noreferrer" }

---

## Credential Protection

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Auditing

[Microsoft - Event 4768](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4769](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4624](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket findDelegation](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py){ target="_blank" rel="noopener noreferrer" }

[Impacket getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

---

## Rubeus

[Rubeus](https://github.com/GhostPack/Rubeus){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Constrained delegation limits Kerberos delegation to explicitly configured backend services.

The fundamental configuration is:

```text
Delegating Account
        |
        v
msDS-AllowedToDelegateTo
        |
        v
Destination SPN
```

The main authentication models are:

```text
Kerberos Only
```

and:

```text
Protocol Transition
```

Protocol transition introduces:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

and makes the S4U flow particularly important:

```text
Front-End Service
      |
      v
S4U2Self
      |
      v
User Representation
      |
      v
S4U2Proxy
      |
      v
Configured Backend Service
```

The central security question is not merely:

```text
Does constrained delegation exist?
```

It is:

```text
Who controls the delegating account?
        |
        v
Which SPNs are permitted?
        |
        v
Which users can be represented?
        |
        v
What privileges do those users
have at the destination?
```

A complete attack path therefore looks like:

```text
Account Compromise
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
Configured Service
       |
       v
User's Permissions
```

Constrained delegation is safer than unconstrained delegation because the delegation scope is restricted, but it should still be treated as a sensitive Active Directory trust relationship.

The defensive objective is:

```text
Remove Unnecessary Delegation
          +
Minimise Destination SPNs
          +
Protect Delegating Accounts
          +
Protect Sensitive Users
          +
Harden Account ACLs
          +
Segment Backend Services
          +
Monitor Delegation Changes
          +
Monitor Kerberos Activity
```

A mature assessment should therefore combine delegation enumeration, SPN analysis, account-control analysis, ACL analysis, BloodHound attack-path analysis, minimum-impact S4U validation, Kerberos telemetry, and application context rather than treating `msDS-AllowedToDelegateTo` as an isolated vulnerability.
