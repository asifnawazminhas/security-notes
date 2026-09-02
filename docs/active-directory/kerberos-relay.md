# Kerberos Relay

Kerberos relay is an authentication attack in which an attacker obtains or redirects a Kerberos authentication exchange and attempts to use that authentication against another service.

At a high level:

```text
Victim
  |
  v
Kerberos Authentication
  |
  v
Attacker-Controlled Path
  |
  v
Target Service
```

Kerberos relay is significantly different from traditional NTLM relay.

NTLM relay commonly exploits weaknesses where authentication is insufficiently bound to the intended destination.

Kerberos normally provides stronger service binding through:

```text
Service Principal Names
```

or:

```text
SPNs
```

because Kerberos service tickets are issued for specific services.

The simplified model is:

```text
Kerberos Ticket
      |
      v
Service Principal Name
      |
      v
Intended Service
```

This makes arbitrary Kerberos relay substantially more constrained than NTLM relay.

However, particular combinations of:

```text
DNS
SPNs
Service Configuration
Authentication Coercion
Delegation
Protocol Behaviour
Directory Permissions
```

can still create relay or authentication-redirection opportunities.

!!! warning "Authorised testing only"
    Kerberos relay testing can involve manipulating name resolution, causing systems to authenticate, modifying Active Directory objects, or interacting with privileged services. Begin with passive enumeration and configuration analysis. Use dedicated test identities and hosts where possible, and avoid production directory changes unless they are explicitly authorised.

---

# Kerberos Authentication Refresher

Kerberos authentication normally involves:

```text
Client
  |
  v
KDC
  |
  v
TGT
  |
  v
TGS Request
  |
  v
Service Ticket
  |
  v
Target Service
```

The important point for relay analysis is:

```text
Service Ticket
     |
     v
Specific SPN
```

---

# Service Principal Names

An SPN identifies a Kerberos-enabled service.

Examples include:

```text
cifs/fileserver.corp.example
ldap/dc01.corp.example
http/web01.corp.example
host/server01.corp.example
```

The client requests a service ticket for the SPN it believes it is accessing.

Conceptually:

```text
Client wants FILE01
      |
      v
cifs/file01.corp.example
      |
      v
KDC
      |
      v
Service Ticket
```

See:

[Kerberos](kerberos.md)

---

# Why Kerberos Relay Is Different

NTLM authentication is comparatively flexible from a relay perspective.

A simplified NTLM relay model is:

```text
Victim
  |
  v
NTLM
  |
  v
Attacker
  |
  v
Different Target
```

Kerberos introduces service binding:

```text
Victim
  |
  v
Ticket for SPN A
  |
  v
Attacker
  |
  X
Service B
```

A ticket issued for one service generally cannot simply be presented to an unrelated service.

---

# Kerberos Relay vs NTLM Relay

The fundamental difference is:

```text
NTLM
 |
 v
Challenge / Response
```

versus:

```text
Kerberos
   |
   v
Service-Specific Ticket
```

Therefore:

```text
Kerberos Relay
      !=
NTLM Relay with Kerberos
```

See:

[NTLM Relay](ntlm-relay.md)

---

# Kerberos Relay vs Pass-the-Ticket

These techniques should also remain separate.

## Pass-the-Ticket

```text
Attacker Obtains Ticket
        |
        v
Reuse Ticket
        |
        v
Service
```

See:

[Pass-the-Ticket](pass-the-ticket.md)

## Kerberos Relay

```text
Victim Authentication
        |
        v
Attacker-Controlled Authentication Path
        |
        v
Compatible Service
```

Relay focuses on forwarding or redirecting authentication.

Pass-the-Ticket focuses on reusing already obtained ticket material.

---

# Kerberos Relay vs Delegation

Delegation is a legitimate Kerberos mechanism allowing one service to obtain or use authentication on behalf of another identity.

Examples include:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
S4U
```

Kerberos relay may interact with delegation concepts, but:

```text
Relay
   !=
Delegation
```

See:

[Unconstrained Delegation](unconstrained-delegation.md)

[Constrained Delegation](constrained-delegation.md)

[Resource-Based Constrained Delegation](rbcd.md)

[Kerberos S4U](s4u.md)

---

# Kerberos Relay Requirements

A useful assessment model is:

```text
Authentication Source
        |
        v
Kerberos Authentication
        |
        v
Service / SPN Compatibility
        |
        v
Relay-Compatible Target
        |
        v
Victim Privilege
        |
        v
Useful Action
```

Unlike NTLM relay, the SPN relationship becomes particularly important.

---

# Requirement 1 - Kerberos Authentication

The client must actually use:

```text
Kerberos
```

rather than:

```text
NTLM
```

Windows commonly uses the:

```text
Negotiate
```

security package.

Conceptually:

```text
Negotiate
   |
   +--> Kerberos
   |
   +--> NTLM
```

Whether Kerberos is selected depends on conditions such as:

```text
SPN Availability
DNS
Target Name
Domain Connectivity
Service Configuration
```

---

# Requirement 2 - Correct Name Resolution

Kerberos depends heavily on names.

A client typically needs to determine:

```text
Target Hostname
      |
      v
SPN
      |
      v
Service Ticket
```

This makes DNS and hostname handling security-relevant.

---

# Requirement 3 - SPN Compatibility

A Kerberos ticket is associated with a service principal.

Conceptually:

```text
Ticket
 |
 v
cifs/server01.corp.example
```

The relay destination must be compatible with the ticket and service context.

This prevents arbitrary forwarding to unrelated services.

---

# Requirement 4 - Target Accepts Kerberos

The destination must support the relevant Kerberos authentication mechanism.

Examples can include:

```text
LDAP
HTTP
SMB
HOST-Based Services
```

depending on service configuration.

---

# Requirement 5 - Useful Victim Privilege

As with NTLM relay:

```text
Successful Authentication
      !=
Useful Privilege
```

Example:

```text
User
 |
 v
Kerberos Authentication
 |
 v
Target
 |
 X
No Write Permission
```

Compare:

```text
Privileged Computer Account
          |
          v
Kerberos Authentication
          |
          v
Directory Service
          |
          v
Useful Directory Rights
```

---

# Authentication Source

A Kerberos relay chain first requires authentication.

Potential sources may include:

```text
Normal Application Behaviour
Authentication Coercion
Name Resolution Manipulation
Service Interaction
Controlled User Action
```

Do not automatically attempt coercion.

Start by understanding where Kerberos authentication naturally occurs.

---

# Authentication Coercion

Authentication coercion means causing another system to authenticate to an attacker-controlled destination.

Conceptually:

```text
Attacker
   |
   v
Trigger
   |
   v
Victim
   |
   v
Outbound Authentication
```

The resulting authentication may use:

```text
NTLM
```

or:

```text
Kerberos
```

depending on the environment and target naming.

The next dedicated page covers coercion in detail:

```text
active-directory/authentication-coercion.md
```

---

# Kerberos Authentication and DNS

Kerberos relies heavily on DNS.

Conceptually:

```text
Hostname
   |
   v
DNS Resolution
   |
   v
Target
   |
   v
SPN Selection
   |
   v
Kerberos Ticket
```

Incorrect or attacker-influenced name resolution can therefore become part of a Kerberos relay chain.

---

# Why IP Addresses Matter

Kerberos commonly relies on hostnames rather than raw IP addresses for SPN selection.

For example:

```text
\\fileserver.corp.example\share
```

is more naturally associated with:

```text
cifs/fileserver.corp.example
```

than:

```text
\\10.10.10.20\share
```

Using an IP address may cause Windows authentication to behave differently or fall back to another authentication mechanism.

---

# Verify Kerberos Usage

Do not assume an authentication attempt is Kerberos simply because both systems are domain joined.

On Windows:

```powershell
klist
```

can display Kerberos tickets associated with the current logon session.

Look for service tickets such as:

```text
cifs/server01.corp.example
ldap/dc01.corp.example
http/web01.corp.example
```

---

# Purging Test Tickets

In a dedicated test environment, existing tickets can affect authentication testing.

The command:

```powershell
klist purge
```

removes Kerberos tickets from the current logon session.

!!! warning
    Purging tickets can disrupt active authentication in the current session. Do not run this on production administrative sessions merely to simplify testing.

---

# SPN Enumeration

Using native Active Directory PowerShell:

```powershell
Get-ADComputer -Filter * -Properties servicePrincipalName |
    Select-Object Name,servicePrincipalName
```

For users:

```powershell
Get-ADUser -Filter * -Properties servicePrincipalName |
    Where-Object { $_.servicePrincipalName } |
    Select-Object SamAccountName,servicePrincipalName
```

---

# setspn

Windows provides:

```text
setspn.exe
```

for SPN administration and querying.

Query an account:

```cmd
setspn -L SERVER01
```

Search for an SPN:

```cmd
setspn -Q cifs/server01.corp.example
```

Search for duplicate SPNs:

```cmd
setspn -X
```

Duplicate SPNs can cause Kerberos authentication problems and should be investigated.

---

# LDAP SPN Enumeration

From Linux:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'DC=corp,DC=example' \
    '(servicePrincipalName=*)' \
    sAMAccountName \
    servicePrincipalName
```

Use an approved assessment identity.

---

# NetExec

NetExec can help enumerate Active Directory systems and authentication behaviour.

Check the installed LDAP options:

```bash
nxc ldap --help
```

and SMB options:

```bash
nxc smb --help
```

Because NetExec functionality evolves, verify module and option names against the installed version before relying on older examples.

See:

[NetExec](netexec.md)

---

# Impacket

Impacket contains several Kerberos-capable tools useful for understanding authentication and service tickets.

Examples include:

```text
getTGT.py
getST.py
ticketer.py
```

Modern installations commonly expose commands such as:

```bash
impacket-getTGT
```

and:

```bash
impacket-getST
```

Review:

```bash
impacket-getTGT -h
impacket-getST -h
```

before using version-specific syntax.

See:

[Impacket](impacket.md)

---

# Kerberos Tickets on Linux

Kerberos ticket caches are commonly referenced through:

```text
KRB5CCNAME
```

Example:

```bash
export KRB5CCNAME=/tmp/test.ccache
```

Inspect:

```bash
klist
```

where Kerberos client utilities are installed.

---

# Service Ticket Analysis

A useful workflow is:

```text
Trigger Normal Authentication
        |
        v
Inspect Ticket Cache
        |
        v
Identify Service Ticket
        |
        v
Identify SPN
        |
        v
Understand Target Relationship
```

This can often reveal whether a proposed relay path is plausible without performing the relay.

---

# Kerberos and SMB

SMB commonly uses the:

```text
cifs
```

service class.

Example:

```text
cifs/fileserver.corp.example
```

A client connecting to:

```text
\\fileserver.corp.example\share
```

may request a service ticket for this SPN.

---

# SMB Signing

SMB signing remains an important integrity control.

However, Kerberos relay analysis should not simply reuse the rule:

```text
SMB Signing Disabled
      =
Kerberos Relay
```

Kerberos has additional service-binding constraints.

The authentication mechanism and SPN must be analysed.

---

# Kerberos and LDAP

LDAP commonly uses an SPN similar to:

```text
ldap/dc01.corp.example
```

Kerberos-authenticated LDAP is central to many Active Directory administrative operations.

A relay or redirection path involving LDAP becomes important if the authenticated principal has useful directory permissions.

---

# LDAP Permissions

The impact model is:

```text
Kerberos Authentication
        |
        v
LDAP
        |
        v
Principal Permissions
        |
        v
Directory Operation
```

Potential permissions might involve:

```text
WriteProperty
GenericWrite
GenericAll
WriteDACL
Extended Rights
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# LDAP Signing

LDAP signing provides message integrity.

For NTLM relay, LDAP signing is a particularly important mitigation.

Kerberos-authenticated LDAP already has different integrity characteristics depending on the negotiated security layer.

Do not treat all LDAP relay scenarios as equivalent.

---

# LDAP Channel Binding

Channel binding is particularly associated with authentication over TLS.

Conceptually:

```text
Authentication
      |
      v
TLS Channel
      |
      v
Channel Binding
```

The precise impact depends on:

```text
Authentication Mechanism
LDAP Configuration
TLS
Client Behaviour
```

---

# Kerberos and HTTP

HTTP services using Windows Integrated Authentication may negotiate Kerberos.

Example SPN:

```text
HTTP/intranet.corp.example
```

The browser may request a ticket for that service.

---

# HTTP SPNs

A common HTTP Kerberos flow is:

```text
Browser
  |
  v
https://portal.corp.example
  |
  v
HTTP/portal.corp.example
  |
  v
KDC
  |
  v
Service Ticket
```

The service account responsible for the application must have the appropriate SPN configuration.

---

# Extended Protection for Authentication

EPA provides additional protection for Windows Integrated Authentication.

Conceptually:

```text
Authentication
      |
      v
Service / Channel Binding
      |
      v
Validation
```

EPA is relevant to both NTLM and Kerberos authentication scenarios, depending on the application and configuration.

---

# Service Binding

Kerberos already provides service binding through SPNs.

EPA can provide additional application-layer protections associated with:

```text
Service Binding
Channel Binding
```

This is especially important for sensitive Windows-authenticated HTTP services.

---

# Kerberos Relay and Active Directory

A particularly important area of research involves relaying Kerberos authentication to Active Directory services.

Conceptually:

```text
Victim
  |
  v
Kerberos Authentication
  |
  v
Attacker-Controlled Endpoint
  |
  v
Directory Service
```

The resulting impact depends on whether:

```text
Ticket / SPN Is Compatible
```

and:

```text
Victim Has Useful Directory Permissions
```

---

# Kerberos Relay and Computer Accounts

Computer accounts are full Active Directory security principals.

Examples:

```text
WS01$
APP01$
DC01$
```

They can authenticate using Kerberos and may possess directory permissions.

Therefore:

```text
Computer Account
      |
      X
Low Privilege by Definition
```

is incorrect.

---

# Domain Controller Computer Accounts

Domain Controller machine accounts are particularly sensitive.

Example:

```text
DC01$
```

Domain Controllers require significant Active Directory privileges to perform legitimate operations.

Authentication originating from a Domain Controller should therefore be treated carefully.

---

# Kerberos Relay and RBCD

Kerberos relay may become relevant to an RBCD attack path if the relayed identity has permission to modify the target computer object's:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Conceptually:

```text
Victim Authentication
        |
        v
Kerberos Relay
        |
        v
Directory Write
        |
        v
RBCD Configuration
        |
        v
S4U
```

The critical prerequisite remains:

```text
Directory Write Permission
```

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# RBCD Is a Separate Primitive

Do not report:

```text
Kerberos Relay
```

as automatically implying:

```text
RBCD
```

The chain requires:

```text
Relay
+
Compatible LDAP Operation
+
Write Permission
+
Controlled Principal
```

---

# Machine Account Quota

Machine Account Quota may allow an authorised domain user to create computer accounts through the default quota mechanism where the domain configuration permits it.

See:

[Active Directory Machine Account Quota](machine-account-quota.md)

The relationship can conceptually be:

```text
Controlled Computer
       +
Target Computer Write
       |
       v
RBCD
```

MAQ alone does not create the relay vulnerability.

---

# Kerberos Relay and S4U

If an RBCD or constrained-delegation path is established, S4U may then be used to request service tickets.

```text
Relay
  |
  v
Directory Modification
  |
  v
Delegation
  |
  v
S4U
```

See:

[Kerberos S4U](s4u.md)

---

# Kerberos Relay and Shadow Credentials

A directory write obtained through an authentication path could also be significant if it permits modification of:

```text
msDS-KeyCredentialLink
```

Conceptually:

```text
Authentication
      |
      v
Directory Write
      |
      v
Key Credential
      |
      v
Certificate-Based Authentication
```

See:

[Active Directory Shadow Credentials](shadow-credentials.md)

This is not inherently a Kerberos relay technique; it is a possible downstream directory-abuse primitive.

---

# Kerberos Relay and AD CS

Certificate services can provide alternative authentication mechanisms.

A successful authentication relay that results in certificate issuance may produce long-lived authentication capability depending on:

```text
Template
Enrollment Endpoint
Requester
Certificate Mapping
EKU
CA Configuration
```

A dedicated AD CS section should cover these relationships separately.

---

# DNS and Kerberos Relay

DNS deserves particular attention because Kerberos depends heavily on service names.

The model is:

```text
DNS Name
   |
   v
SPN
   |
   v
Service Ticket
```

If an attacker can influence the name a client uses, the resulting SPN selection may also be influenced.

---

# DNS Is Not Automatically a Relay Primitive

Finding:

```text
DNS Record Can Be Created
```

does not automatically prove:

```text
Kerberos Relay
```

The full path requires analysis of:

```text
Who Uses the Name?
Which SPN Is Requested?
Which Account Owns the SPN?
Which Service Accepts the Ticket?
What Privilege Results?
```

---

# Active Directory Integrated DNS

Active Directory environments commonly use AD-integrated DNS.

DNS records are stored in directory partitions such as:

```text
DomainDnsZones
ForestDnsZones
```

depending on configuration.

A later ADIDNS page should cover DNS permissions and record manipulation in detail.

---

# DNS Record Permissions

Assess:

```text
Who Can Create Records?
Who Can Modify Records?
Who Owns Existing Records?
Which Names Are Security-Sensitive?
```

Do not modify production DNS records merely to test theoretical Kerberos relay paths.

---

# SPN Ownership

SPNs are stored on Active Directory objects.

Conceptually:

```text
Service
   |
   v
SPN
   |
   v
Account
```

Example:

```text
HTTP/portal.corp.example
          |
          v
CORP\svc-web
```

The account associated with the SPN possesses the Kerberos keys used for that service.

---

# Duplicate SPNs

Duplicate SPNs can cause:

```text
Kerberos Authentication Failure
```

and may lead to fallback behaviour.

They should be treated as an identity/configuration issue.

Use:

```cmd
setspn -X
```

to search for duplicate SPNs where authorised.

---

# Kerberos Fallback to NTLM

One of the most important practical observations is that failed Kerberos authentication may result in NTLM being used instead.

Conceptually:

```text
Kerberos Attempt
      |
      X
Cannot Obtain / Use Ticket
      |
      v
NTLM Fallback
```

This can transform what appears to be a Kerberos problem into an NTLM relay opportunity.

---

# Verify the Actual Protocol

Never report:

```text
Kerberos Relay
```

simply because the application was expected to use Kerberos.

Verify:

```text
Kerberos Ticket
Network Authentication
Windows Logs
Application Behaviour
```

It may actually be:

```text
NTLM Relay
```

---

# Negotiate

Applications using:

```text
Negotiate
```

may use either Kerberos or NTLM.

Therefore:

```text
WWW-Authenticate: Negotiate
```

does not prove Kerberos was used.

Likewise, Windows Integrated Authentication does not automatically mean Kerberos.

---

# Kerberos Relay Tooling

Kerberos relay research and tooling changes faster than traditional NTLM relay tooling.

Tools encountered in security research include projects designed to:

```text
Receive Kerberos Authentication
Relay Kerberos Authentication
Interact with LDAP
Manipulate DNS / SPNs
Combine Coercion with Relay
```

Because exact support is highly version-dependent, do not blindly copy commands from historical research.

---

# KrbRelayUp

`KrbRelayUp` is a well-known research tool demonstrating Windows local privilege escalation chains involving Kerberos relay and Active Directory configuration.

It should not be interpreted as a generic:

```text
Relay Kerberos Anywhere
```

tool.

The original attack chain combined several Active Directory primitives.

Conceptually:

```text
Domain User Context
       |
       v
Kerberos Relay Primitive
       |
       v
Directory Modification
       |
       v
Delegation / Service Abuse
       |
       v
Local Privilege Escalation
```

Modern Windows and Active Directory hardening may affect these paths.

Always assess the actual environment rather than assuming an older chain remains exploitable.

---

# KrbRelay

Research tooling such as:

```text
KrbRelay
```

has demonstrated Kerberos relaying under specific Windows authentication conditions.

These tools rely on detailed behaviour involving:

```text
SSPI
SPNs
LDAP
COM / RPC
Authentication Context
```

Treat them as research implementations rather than universal relay tools.

---

# Tool Version Verification

Before using any Kerberos relay research tool:

```text
1. Read the project's current documentation
2. Check supported Windows versions
3. Check supported Domain Controller versions
4. Check required privileges
5. Check required domain configuration
6. Check mitigation status
7. Test in a lab first
```

Do not use outdated exploit commands as generic production testing procedures.

---

# Local Kerberos Relay

Some Kerberos relay research focuses on authentication occurring on the same Windows host.

Conceptually:

```text
Local Service
    |
    v
Kerberos Authentication
    |
    v
Attacker-Controlled Local Endpoint
    |
    v
Directory / Service
```

This differs from a traditional network attacker receiving authentication from another host.

---

# Local Relay vs Network Relay

Keep these models separate.

## Network

```text
Victim Host
    |
    v
Network
    |
    v
Attacker
    |
    v
Target
```

## Local

```text
Compromised Host
      |
      v
Local Authentication Primitive
      |
      v
Relay
      |
      v
Target Service
```

The prerequisites and mitigations may differ significantly.

---

# Local Privilege Escalation Context

Some Kerberos relay research has demonstrated escalation from:

```text
Domain User
```

to:

```text
Local SYSTEM
```

under specific Active Directory and Windows configurations.

This does not mean:

```text
Every Domain User
      |
      v
SYSTEM
```

is generally possible.

The chain depends on multiple prerequisites.

---

# Attack Chain Analysis

When reviewing a proposed Kerberos relay chain, break it into primitives.

Example:

```text
Can Authentication Be Triggered?
            |
            v
Will Kerberos Be Used?
            |
            v
Which SPN Is Requested?
            |
            v
Can Authentication Be Received?
            |
            v
Can It Be Forwarded?
            |
            v
Will Target Accept It?
            |
            v
What Rights Does Victim Have?
            |
            v
What Action Becomes Possible?
```

This prevents overstating a theoretical attack.

---

# Safe Enumeration First

Before running relay tooling, collect:

```text
Domain
Domain Controllers
DNS Configuration
SPNs
LDAP Configuration
SMB Configuration
HTTP Authentication
Computer Permissions
Machine Account Quota
Delegation
Victim Privileges
```

Many proposed paths can be ruled in or out from configuration alone.

---

# PowerShell Domain Information

```powershell
Get-ADDomain |
    Select-Object DNSRoot,DistinguishedName,DomainMode
```

---

# Domain Controllers

```powershell
Get-ADDomainController -Filter * |
    Select-Object HostName,IPv4Address,Site,IsGlobalCatalog
```

---

# Computer SPNs

```powershell
Get-ADComputer -Filter * -Properties servicePrincipalName |
    Select-Object Name,DNSHostName,servicePrincipalName
```

---

# User SPNs

```powershell
Get-ADUser -Filter * -Properties servicePrincipalName |
    Where-Object { $_.servicePrincipalName } |
    Select-Object SamAccountName,servicePrincipalName
```

---

# Delegation Enumeration

```powershell
Get-ADComputer -Filter * -Properties TrustedForDelegation,TrustedToAuthForDelegation,'msDS-AllowedToDelegateTo' |
    Select-Object `
        Name,
        TrustedForDelegation,
        TrustedToAuthForDelegation,
        'msDS-AllowedToDelegateTo'
```

For RBCD:

```powershell
Get-ADComputer -Filter * -Properties 'msDS-AllowedToActOnBehalfOfOtherIdentity' |
    Where-Object { $_.'msDS-AllowedToActOnBehalfOfOtherIdentity' } |
    Select-Object Name,'msDS-AllowedToActOnBehalfOfOtherIdentity'
```

---

# BloodHound

BloodHound can help identify downstream permissions relevant to a relay chain.

Examples include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
AddMember
AddSelf
AllowedToAct
AdminTo
```

The relay primitive itself still needs separate validation.

---

# Example Analysis

Suppose:

```text
WS01$
```

can be caused to authenticate.

Before attempting relay, determine:

```text
Does WS01$ use Kerberos?

Which SPN is requested?

Which service receives the authentication?

What objects can WS01$ modify?

Is WS01$ privileged anywhere?

Does it have delegation-related rights?
```

If the answer is:

```text
No Useful Rights
```

then active relay testing may provide little value.

---

# Machine Account Privilege

Machine accounts commonly belong to:

```text
Domain Computers
```

and receive permissions through:

```text
Authenticated Users
Domain Computers
Explicit ACLs
Application Roles
```

Do not assume machine credentials are harmless.

---

# Domain Controller Privilege

Domain Controllers commonly belong to:

```text
Domain Controllers
```

and participate in highly privileged directory operations.

Therefore:

```text
DC Authentication
```

deserves special attention.

---

# Kerberos Relay Detection

Detection should focus on the behaviour surrounding authentication rather than a particular tool.

Potential data sources include:

```text
Kerberos Events
Directory Changes
DNS Changes
Network Traffic
LDAP Activity
Endpoint Telemetry
SPN Changes
Delegation Changes
```

---

# Event 4768

Event:

```text
4768
```

records Kerberos Authentication Service activity involving Ticket Granting Ticket requests.

Useful fields include:

```text
Account
Client Address
Encryption Type
Result
```

---

# Event 4769

Event:

```text
4769
```

records Kerberos service-ticket requests.

This is particularly relevant to SPN analysis.

Useful fields can include:

```text
Account Name
Service Name
Client Address
Ticket Encryption Type
Status
```

---

# Event 4771

Event:

```text
4771
```

records Kerberos pre-authentication failures.

It may provide context during unusual authentication behaviour but does not independently identify relay.

---

# Event 4624

Successful authentication to the target may generate:

```text
4624
```

depending on the service and logon type.

Correlate:

```text
Identity
Source Address
Authentication Package
Target
Timestamp
```

---

# Directory Changes

If a relay results in Active Directory modification, events such as:

```text
5136
```

may record the changed object and attribute when appropriate auditing is configured.

High-value attributes include:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
msDS-KeyCredentialLink
servicePrincipalName
```

---

# Computer Creation

If the attack path involves creation of a computer object, monitor:

```text
4741
```

and potentially:

```text
5137
```

depending on auditing configuration.

---

# SPN Changes

Changes to:

```text
servicePrincipalName
```

should be monitored on sensitive identities.

Unexpected SPN manipulation may affect Kerberos service resolution and authentication.

---

# DNS Changes

If DNS manipulation is part of the attack chain, monitor:

```text
New DNS Records
Modified DNS Records
Unexpected Record Owners
Sensitive Hostnames
```

especially within AD-integrated DNS.

---

# RBCD Changes

Monitor:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

on computer objects.

An unexpected modification should be treated as highly suspicious.

---

# Shadow Credential Changes

Monitor:

```text
msDS-KeyCredentialLink
```

especially on privileged users and computers.

See:

[Active Directory Shadow Credentials](shadow-credentials.md)

---

# Detection Correlation

A useful detection chain might be:

```text
Unexpected DNS Change
        |
        v
Kerberos Service Ticket
        |
        v
Unusual Authentication
        |
        v
LDAP Modification
        |
        v
Delegation Change
```

No single event necessarily proves relay.

Correlation is essential.

---

# Another Detection Chain

```text
Authentication Coercion
        |
        v
Victim Kerberos Authentication
        |
        v
Attacker-Controlled Host
        |
        v
Directory Modification
```

Investigate the full sequence.

---

# Baseline Machine Authentication

Computer accounts legitimately authenticate frequently.

Therefore:

```text
Machine Account Kerberos
```

alone is not suspicious.

Look for:

```text
Unusual Destination
Unusual Source
Unusual SPN
Unusual Directory Change
Unusual Timing
```

---

# Detect Behaviour, Not Tool Names

Do not rely solely on detecting:

```text
KrbRelay.exe
KrbRelayUp.exe
```

Tool names can change.

Focus on:

```text
Authentication Flow
SPN Behaviour
Directory Modifications
DNS Changes
Delegation Changes
```

---

# Hardening

Kerberos relay mitigation requires addressing the primitives that make the attack chain possible.

A useful model is:

```text
Secure Name Resolution
        +
Secure SPN Management
        +
Protect Directory ACLs
        +
Restrict Authentication Coercion
        +
Protocol Protection
        +
Least Privilege
```

---

# Protect DNS

Restrict who can:

```text
Create DNS Records
Modify DNS Records
Control Sensitive Names
```

in AD-integrated DNS.

Review stale and attacker-controlled records.

---

# Secure Dynamic DNS

Dynamic DNS is useful in Active Directory but should be configured securely.

Prefer:

```text
Secure Dynamic Updates
```

for AD-integrated zones where appropriate.

---

# Protect SPNs

Restrict unnecessary rights to modify:

```text
servicePrincipalName
```

on users and computers.

Review principals with:

```text
GenericWrite
GenericAll
WriteProperty
```

over sensitive service accounts.

---

# Detect Duplicate SPNs

Periodically check:

```cmd
setspn -X
```

and investigate duplicate registrations.

Duplicate SPNs can cause authentication failures and unexpected fallback behaviour.

---

# Protect Computer Objects

Review who can modify:

```text
Computer Accounts
```

particularly sensitive servers and Domain Controllers.

Relevant rights include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
```

---

# Protect RBCD

Monitor and restrict writes to:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# Protect KeyCredentialLink

Restrict modification of:

```text
msDS-KeyCredentialLink
```

See:

[Active Directory Shadow Credentials](shadow-credentials.md)

---

# Machine Account Quota

Where self-service computer creation is not required, consider reducing:

```text
ms-DS-MachineAccountQuota
```

including potentially setting it to:

```text
0
```

after validating organisational requirements.

This removes one possible primitive but does not fix unrelated delegated computer-creation permissions.

See:

[Active Directory Machine Account Quota](machine-account-quota.md)

---

# Authentication Coercion Hardening

Reduce unnecessary services and configurations capable of causing privileged systems to authenticate to arbitrary destinations.

The next page covers this area in detail:

```text
active-directory/authentication-coercion.md
```

---

# LDAP Hardening

Follow current Microsoft guidance for:

```text
LDAP Signing
LDAP Channel Binding
```

especially where NTLM fallback remains possible.

---

# SMB Hardening

Require SMB signing where appropriate and follow current Microsoft SMB hardening guidance.

This is particularly important because a failed Kerberos path may sometimes result in NTLM fallback.

See:

[NTLM Relay](ntlm-relay.md)

---

# EPA

Enable:

```text
Extended Protection for Authentication
```

for supported Windows-authenticated applications.

EPA can provide additional protection against credential forwarding.

---

# Reduce NTLM Fallback

One of the most important hardening goals is:

```text
Kerberos Failure
      |
      X
Silent NTLM Exposure
```

Monitor where NTLM fallback occurs and remediate the underlying causes.

---

# Fix SPN Configuration

Common Kerberos problems include:

```text
Missing SPN
Duplicate SPN
Wrong Service Account
Incorrect DNS Name
Alias Without SPN
```

Fixing these problems can reduce unnecessary NTLM fallback.

---

# Use Correct DNS Names

Applications should use names that correspond correctly to registered SPNs.

Avoid configurations where clients routinely access domain services using:

```text
Raw IP Addresses
Unregistered Aliases
Incorrect Hostnames
```

if Kerberos authentication is expected.

---

# Least Privilege

Even if authentication is relayed:

```text
Relayed Identity
      |
      v
Minimal Permission
      |
      v
Minimal Impact
```

Review:

```text
Computer ACLs
Directory ACLs
Local Administrator Rights
Service Permissions
Delegation Rights
```

---

# Administrative Tiering

Privileged identities should authenticate only to systems appropriate for their security tier.

Conceptually:

```text
Tier 0 Credential
      |
      X
Lower-Trust System
```

This reduces both credential exposure and relay opportunities.

---

# Network Segmentation

Restrict unnecessary access to:

```text
LDAP
SMB
HTTP Management
RPC
Domain Controller Services
```

from lower-trust network segments.

---

# Host Firewalling

Host firewalls can reduce relay reachability.

For example:

```text
Workstation
    |
    X
Direct LDAP Access to DC
```

may be appropriate in some highly controlled architectures, although Active Directory client requirements must be understood before implementing restrictions.

---

# Protected Users

For suitable privileged user accounts, membership in:

```text
Protected Users
```

can reduce exposure to weaker authentication mechanisms.

This does not directly solve every Kerberos relay scenario.

---

# Sensitive Accounts and Delegation

Marking suitable privileged accounts as:

```text
Account is sensitive and cannot be delegated
```

can reduce delegation-related exposure.

This is not a universal relay mitigation but forms part of Kerberos hardening.

---

# Incident Response

If Kerberos relay is suspected:

```text
Identify Victim
      |
      v
Identify Authentication Trigger
      |
      v
Identify Requested SPN
      |
      v
Identify Relay Destination
      |
      v
Identify Directory / Service Actions
      |
      v
Contain
      |
      v
Remove Persistence
```

---

# Identify the Authentication Source

Determine:

```text
Which User or Computer Authenticated?
```

Then determine:

```text
Why?
```

Potential causes include:

```text
Application Behaviour
Coercion
Name Resolution
DNS Manipulation
Local Authentication Primitive
```

---

# Identify the SPN

Review:

```text
4769
```

and other Kerberos telemetry to determine the service involved.

The SPN can help reconstruct:

```text
What Service the Client Believed It Was Accessing
```

---

# Identify DNS Changes

Review whether:

```text
DNS Records
```

were created or modified shortly before the suspicious authentication.

---

# Identify SPN Changes

Review:

```text
servicePrincipalName
```

changes on relevant users and computers.

Unexpected SPN modification may be part of the attack chain.

---

# Review Directory Modifications

Look for:

```text
RBCD
Shadow Credentials
ACL Changes
Group Changes
Computer Creation
SPN Changes
```

---

# Review Delegation

Check whether:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

or:

```text
msDS-AllowedToDelegateTo
```

changed.

---

# Review Certificates

If certificate-based authentication appears in the downstream chain, investigate:

```text
Certificate Requests
Issued Certificates
Template
Requester
Subject
SAN
EKU
```

---

# Remove Persistence

Potential persistence may include:

```text
RBCD
Shadow Credentials
Certificates
ACLs
Groups
Accounts
SPNs
DNS Records
```

Remove only after collecting forensic evidence and understanding the original configuration.

---

# Credential Rotation

Kerberos relay does not automatically mean:

```text
Victim Password Was Stolen
```

Do not assume credential rotation alone resolves the issue.

If the attack resulted in:

```text
Certificate
Delegation
ACL
New Account
```

those persistence mechanisms must also be addressed.

---

# Reporting

Kerberos relay findings should describe the actual chain rather than using a generic title.

Possible titles include:

```text
Kerberos Authentication Can Be Relayed to Active Directory
```

```text
Kerberos Relay Enables Modification of Computer Objects
```

```text
Directory Permissions Enable Kerberos Relay Privilege Escalation
```

```text
Insecure Name and SPN Configuration Enables Kerberos Authentication Redirection
```

Use the title supported by the evidence.

---

# Avoid Generic Findings

Avoid:

```text
Kerberos Is Vulnerable to Relay
```

This is too broad.

Kerberos normally includes strong service binding.

The finding should identify the specific combination of configuration and permissions that created the path.

---

# Example Finding

```text
Finding:
Kerberos Relay Enables Unauthorised Computer Object Modification

Affected Environment:
corp.example

Description:
A controlled Kerberos authentication from a dedicated test computer
could be redirected through the assessed authentication path to an
Active Directory service.

The authenticated computer account possessed write permissions over
the designated test computer object.

During validation, the assessment confirmed the ability to perform an
approved directory modification using the relayed authentication.

No privileged production account was used and the test modification
was reverted immediately.

Impact:
An attacker able to reproduce the authentication path could perform
directory operations using the permissions of the relayed identity.

Where the affected identity has control over sensitive computer
objects, this may enable additional Active Directory attack paths such
as delegation or credential-based persistence.

Recommendation:
Remove unnecessary directory write permissions from computer and
service accounts.

Review DNS and SPN configuration involved in the authentication path.

Restrict authentication-coercion opportunities and enforce applicable
protocol protections.

Monitor unexpected Kerberos authentication followed by sensitive
directory modifications.
```

---

# Example Configuration Finding

```text
Finding:
Kerberos Authentication Configuration Permits NTLM Fallback

Description:
Several internal services are accessed through aliases that do not
have corresponding Service Principal Names.

Kerberos authentication therefore fails for these access paths and
clients fall back to NTLM.

Impact:
The fallback increases exposure to NTLM-specific attacks, including
authentication relay where target protocol protections are not
enforced.

Recommendation:
Register and maintain the required SPNs for approved service aliases.

Remove duplicate or stale SPNs.

Monitor NTLM usage and investigate authentication paths where Kerberos
is expected but NTLM is negotiated.
```

---

# Severity

Severity depends on the complete chain:

```text
Authentication Source
        +
Kerberos Relay Primitive
        +
Target
        +
Victim Privilege
        +
Resulting Action
        =
Severity
```

A theoretical relay condition with no useful privilege may be:

```text
Informational / Low
```

depending on context.

A validated chain resulting in control of a sensitive computer or directory object may be:

```text
High
```

or potentially:

```text
Critical
```

if it crosses a domain-level trust boundary.

---

# Evidence

Record:

```text
Victim Identity
Victim Type
Authentication Source
Kerberos Confirmation
Requested SPN
DNS Name
Relay Host
Target
Target Protocol
Victim Permissions
Directory Operation
Timestamp
Kerberos Events
Directory Events
Cleanup
```

---

# Do Not Store Tickets Unnecessarily

Kerberos tickets are reusable authentication material.

Do not:

```text
Commit Tickets to Git
Upload Tickets to Public Services
Paste Tickets into Reports
Leave Tickets on Shared Systems
```

Common ticket-related files include:

```text
*.ccache
*.kirbi
```

Treat them as credentials.

---

# Safe Validation Strategy

Use:

```text
Level 1
Enumerate DNS / SPNs

Level 2
Determine Authentication Protocol

Level 3
Map Victim Permissions

Level 4
Identify Relay Preconditions

Level 5
Use Dedicated Test Identity

Level 6
Perform One Controlled Relay

Level 7
Perform Harmless Approved Operation

Level 8
Revert

Level 9
Stop
```

---

# Kerberos Relay Assessment Checklist

## Preparation

- [ ] Confirm Kerberos relay testing is authorised
- [ ] Confirm coercion restrictions
- [ ] Confirm DNS modification restrictions
- [ ] Confirm SPN modification restrictions
- [ ] Confirm Active Directory modification restrictions
- [ ] Confirm target services
- [ ] Define dedicated test identities
- [ ] Define cleanup procedures
- [ ] Define stop conditions

## Domain Enumeration

- [ ] Identify domain
- [ ] Identify Domain Controllers
- [ ] Identify DNS servers
- [ ] Identify domain functional level
- [ ] Identify Kerberos services
- [ ] Identify sensitive computer accounts
- [ ] Identify service accounts

## Kerberos

- [ ] Confirm Kerberos is actually used
- [ ] Review TGTs
- [ ] Review service tickets
- [ ] Identify requested SPNs
- [ ] Identify service classes
- [ ] Identify NTLM fallback
- [ ] Review Negotiate behaviour

## SPNs

- [ ] Enumerate computer SPNs
- [ ] Enumerate user SPNs
- [ ] Search target SPNs
- [ ] Search duplicate SPNs
- [ ] Identify missing SPNs
- [ ] Identify service aliases
- [ ] Identify SPN owners
- [ ] Review SPN write permissions

## DNS

- [ ] Identify AD-integrated DNS
- [ ] Review secure dynamic updates
- [ ] Review DNS record creation permissions
- [ ] Review sensitive hostnames
- [ ] Review record ownership
- [ ] Identify stale records
- [ ] Identify aliases used by Kerberos services
- [ ] Avoid production DNS modification unless required

## Permissions

- [ ] Map victim directory permissions
- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteProperty
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Review RBCD write permissions
- [ ] Review KeyCredentialLink permissions
- [ ] Review group-control paths
- [ ] Review local administrative relationships

## Delegation

- [ ] Enumerate unconstrained delegation
- [ ] Enumerate constrained delegation
- [ ] Enumerate RBCD
- [ ] Enumerate S4U relationships
- [ ] Identify sensitive accounts
- [ ] Review delegation-related ACLs

## Machine Accounts

- [ ] Identify potential machine authentication
- [ ] Review machine privileges
- [ ] Review Machine Account Quota
- [ ] Review computer creation delegation
- [ ] Review Domain Controller accounts
- [ ] Do not assume machine accounts are low privilege

## Validation

- [ ] Prefer configuration analysis first
- [ ] Use dedicated test identity
- [ ] Use dedicated target object
- [ ] Confirm Kerberos
- [ ] Confirm exact SPN
- [ ] Confirm relay prerequisite
- [ ] Perform one controlled authentication
- [ ] Perform minimum approved action
- [ ] Avoid persistence
- [ ] Revert directory changes
- [ ] Stop after sufficient evidence

## Detection

- [ ] Review event 4768
- [ ] Review event 4769
- [ ] Review event 4771
- [ ] Review event 4624
- [ ] Review event 5136
- [ ] Review event 4741
- [ ] Review event 5137 where configured
- [ ] Monitor SPN changes
- [ ] Monitor DNS changes
- [ ] Monitor RBCD changes
- [ ] Monitor KeyCredentialLink changes
- [ ] Correlate authentication and directory modification

## Hardening

- [ ] Secure DNS updates
- [ ] Restrict DNS record modification
- [ ] Protect sensitive DNS names
- [ ] Protect SPNs
- [ ] Remove duplicate SPNs
- [ ] Fix missing SPNs
- [ ] Reduce NTLM fallback
- [ ] Protect computer objects
- [ ] Protect RBCD attributes
- [ ] Protect KeyCredentialLink
- [ ] Review Machine Account Quota
- [ ] Restrict authentication coercion
- [ ] Apply LDAP hardening
- [ ] Apply SMB hardening
- [ ] Enable EPA where supported
- [ ] Apply least privilege
- [ ] Apply administrative tiering
- [ ] Apply network segmentation

## Incident Response

- [ ] Identify victim identity
- [ ] Identify authentication trigger
- [ ] Identify requested SPN
- [ ] Identify relay host
- [ ] Identify target
- [ ] Identify directory changes
- [ ] Review DNS changes
- [ ] Review SPN changes
- [ ] Review delegation changes
- [ ] Review Shadow Credentials
- [ ] Review certificate issuance
- [ ] Identify persistence
- [ ] Remove malicious configuration
- [ ] Preserve forensic evidence

## Cleanup

- [ ] Stop relay tooling
- [ ] Remove temporary DNS records
- [ ] Remove temporary SPNs
- [ ] Remove temporary computer accounts
- [ ] Restore original ACLs
- [ ] Restore original RBCD value
- [ ] Restore original KeyCredentialLink
- [ ] Remove temporary certificates
- [ ] Delete temporary tickets
- [ ] Verify no test persistence remains
- [ ] Record cleanup evidence

---

# Kerberos Relay Testing Model

The normal Kerberos model is:

```text
Client
  |
  v
KDC
  |
  v
Service Ticket
  |
  v
SPN
  |
  v
Service
```

The service-binding model is:

```text
Ticket
  |
  v
Specific SPN
  |
  v
Expected Service
```

The relay problem is therefore not simply:

```text
Receive Ticket
     |
     v
Send Anywhere
```

Instead:

```text
Receive Authentication
        |
        v
Understand SPN
        |
        v
Find Compatible Target
        |
        v
Preserve Authentication Context
        |
        v
Target Accepts Authentication
```

The authentication-selection model is:

```text
Application
    |
    v
Negotiate
    |
    +--> Kerberos
    |
    +--> NTLM
```

The fallback model is:

```text
Kerberos
   |
   X
SPN / DNS / Configuration Failure
   |
   v
NTLM
   |
   v
Potential NTLM Relay Surface
```

The DNS relationship is:

```text
DNS Name
   |
   v
SPN Selection
   |
   v
Kerberos Ticket
```

The privilege model is:

```text
Successful Authentication
          |
          v
Victim Permissions
          |
          +--> No Useful Rights
          |
          +--> Directory Write
          |
          +--> Administrative Rights
```

The directory-abuse model is:

```text
Kerberos Authentication
          |
          v
Compatible Directory Service
          |
          v
Victim Write Permission
          |
          +--> RBCD
          |
          +--> Shadow Credentials
          |
          +--> ACL / Object Changes
```

The RBCD relationship is:

```text
Relay
  |
  v
Write Target Computer
  |
  v
msDS-AllowedToActOnBehalfOfOtherIdentity
  |
  v
S4U
```

The safe-testing model is:

```text
Enumerate
   |
   v
Confirm Kerberos
   |
   v
Identify SPN
   |
   v
Map Permissions
   |
   v
Controlled Test Identity
   |
   v
Minimum Relay Validation
   |
   v
Revert
```

The detection model is:

```text
Authentication Trigger
        |
        v
Kerberos Ticket Request
        |
        v
Unexpected Authentication Path
        |
        v
Sensitive Operation
        |
        v
Directory / Endpoint Telemetry
```

The hardening model is:

```text
Secure DNS
    +
Secure SPNs
    +
Protect Directory ACLs
    +
Restrict Coercion
    +
Protocol Hardening
    +
Least Privilege
    =
Reduced Kerberos Relay Risk
```

The most important distinction is:

```text
Kerberos Relay
      !=
NTLM Relay
```

because:

```text
Kerberos
   |
   v
Service-Specific Tickets
```

Another important distinction is:

```text
Kerberos Relay
      !=
Pass-the-Ticket
```

because Pass-the-Ticket reuses ticket material already controlled by the attacker.

Another important distinction is:

```text
Kerberos Relay Primitive
        |
        X
Automatic Privilege Escalation
```

The relayed identity still requires useful rights.

For penetration testers:

```text
Do Not Ask:
"Can I run a Kerberos relay tool?"

Ask:
"What Kerberos identity is authenticating,
which SPN is involved, where can that
authentication be accepted, and what can
that identity do there?"
```

For defenders:

```text
Do Not Ask:
"Is Kerberos enabled?"

Ask:
"Are DNS, SPNs, service configuration,
directory permissions, delegation, and
authentication flows configured so that
Kerberos authentication cannot be redirected
into a useful attack path?"
```

The final security relationship is:

```text
Name
  |
  v
SPN
  |
  v
Kerberos Ticket
  |
  v
Service
  |
  v
Identity Permissions
  |
  v
Impact
```

Kerberos relay analysis therefore requires understanding the complete identity and service relationship rather than treating Kerberos as a generic reusable authentication protocol.

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

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Machine Account Quota:

[Active Directory Machine Account Quota](machine-account-quota.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

RBCD:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[Kerberos S4U](s4u.md)

Shadow Credentials:

[Active Directory Shadow Credentials](shadow-credentials.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The next page in this section is:

```text
active-directory/authentication-coercion.md
```

---

# References

## Microsoft - Kerberos Authentication

[Microsoft - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Service Principal Names

[Microsoft - Service Principal Names](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - setspn

[Microsoft - setspn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos Event 4768

[Microsoft - Event 4768](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos Event 4769

[Microsoft - Event 4769](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos Event 4771

[Microsoft - Event 4771](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4771){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - LDAP Signing

[Microsoft - LDAP Signing](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - LDAP Channel Binding

[Microsoft - LDAP Channel Binding and LDAP Signing Requirements](https://support.microsoft.com/en-us/topic/2020-2023-and-2024-ldap-channel-binding-and-ldap-signing-requirements-for-windows-kb4520412-ef185fb8-00f7-167d-744c-f299a66fc00a){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Signing

[Microsoft - SMB Signing](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Extended Protection

[Microsoft - Extended Protection for Authentication](https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/extended-protection-for-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Kerberos Relay Research

[Google Project Zero - The Kerberos Relay Attack](https://googleprojectzero.blogspot.com/2021/10/using-kerberos-for-authentication-relay.html){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Forced Authentication](https://attack.mitre.org/techniques/T1187/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Kerberos relay is fundamentally different from NTLM relay because Kerberos authentication is normally tied to:

```text
Service Principal Names
```

The normal trust relationship is:

```text
Client
  |
  v
Target Name
  |
  v
SPN
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

This creates a stronger authentication binding than traditional NTLM challenge-response authentication.

However, Active Directory environments contain many interacting components:

```text
DNS
SPNs
Kerberos
LDAP
SMB
HTTP
Delegation
Computer Accounts
Directory ACLs
Authentication Coercion
```

A weakness across several of these layers can create an exploitable chain.

The key lesson is therefore:

```text
Kerberos Relay
      |
      X
Single Misconfiguration
```

It is usually better represented as:

```text
Authentication Primitive
        +
Name / SPN Relationship
        +
Compatible Service
        +
Useful Identity Permission
        =
Attack Path
```

Another important practical relationship is:

```text
Broken Kerberos
      |
      v
NTLM Fallback
      |
      v
NTLM Relay Exposure
```

Therefore Kerberos configuration errors can increase NTLM attack surface even when a direct Kerberos relay path is unavailable.

For testers, begin with:

```text
Which identity authenticates?
```

Then:

```text
Is it actually Kerberos?
```

Then:

```text
Which SPN is requested?
```

Then:

```text
Where can that authentication be accepted?
```

Finally:

```text
What can the identity do there?
```

For defenders, the corresponding questions are:

```text
Are DNS records protected?

Are SPNs correct?

Are duplicate SPNs detected?

Are sensitive object ACLs restricted?

Are authentication-coercion paths reduced?

Are LDAP and SMB appropriately hardened?

Is NTLM fallback monitored?

Are privileged identities prevented from
authenticating to lower-trust systems?
```

The complete model is:

```text
Identity
   |
   v
Name Resolution
   |
   v
SPN
   |
   v
Kerberos Authentication
   |
   v
Service
   |
   v
Authorisation
   |
   v
Impact
```

Kerberos relay security is therefore not just a Kerberos problem.

It is an Active Directory identity, naming, service, permission, and authentication-flow problem.
