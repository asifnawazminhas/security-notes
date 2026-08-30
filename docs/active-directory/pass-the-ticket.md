# Pass-the-Ticket

Pass-the-Ticket (PtT) is a Kerberos credential-reuse technique in which an attacker uses a valid Kerberos ticket to authenticate as the identity represented by that ticket without supplying the account's plaintext password.

The fundamental concept is:

```text
Kerberos Ticket
      |
      v
Reusable Authentication Material
      |
      v
Kerberos Authentication
      |
      v
Access as Ticket Identity
```

The ticket may have been legitimately issued by the Key Distribution Center and subsequently exposed, exported, copied, or otherwise obtained by an attacker.

Two important ticket types are:

```text
Ticket Granting Ticket (TGT)
Service Ticket (TGS)
```

Their usefulness differs significantly.

A stolen TGT can potentially be used to request additional service tickets:

```text
Stolen TGT
    |
    +--> CIFS ticket
    +--> LDAP ticket
    +--> HTTP ticket
    +--> HOST ticket
    +--> MSSQLSvc ticket
```

A stolen service ticket is normally useful only for the service for which it was issued:

```text
Stolen CIFS Ticket
       |
       v
CIFS / SMB Service
```

Pass-the-Ticket demonstrates an important Active Directory security principle:

> Kerberos tickets are credentials.

Possession of a valid ticket may be sufficient to authenticate as the represented identity for the ticket's valid lifetime and permitted scope.

!!! warning "Authorised testing only"
    Kerberos tickets provide reusable authentication capability. Only obtain, export, convert, inject, or reuse tickets belonging to accounts and systems explicitly included in the assessment scope. Prefer authentication-only validation where possible and securely remove temporary `.ccache`, `.kirbi`, and other ticket artefacts after testing.

---

# Pass-the-Ticket at a Glance

A typical workflow is:

```text
Compromised System
       |
       v
Ticket Discovery
       |
       v
Kerberos Ticket Obtained
       |
   +---+---+
   |       |
   v       v
  TGT     TGS
   |       |
   |       +--> Specific Service
   |
   +--> Request Additional
        Service Tickets
             |
             v
      Kerberos Authentication
             |
             v
       Authorised Target
             |
             v
       Privilege Analysis
             |
             v
       Minimum Validation
             |
             v
           Cleanup
```

---

# Kerberos Refresher

Kerberos authentication normally follows:

```text
Client
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
Target Service
```

The password or another long-term key is required primarily to establish the initial Kerberos authentication context.

After tickets have been issued:

```text
Long-Term Credential
        |
        v
       TGT
        |
        v
Service Tickets
        |
        v
Service Authentication
```

The ticket itself becomes reusable authentication material.

For the underlying ticket model, see:

[Kerberos Tickets](kerberos-tickets.md)

For the broader protocol, see:

[Kerberos](kerberos.md)

---

# Why Pass-the-Ticket Works

Kerberos was intentionally designed so users do not repeatedly send their long-term credentials to every service.

Instead:

```text
User authenticates once
        |
        v
KDC issues tickets
        |
        v
Tickets prove authentication
```

The target service validates the Kerberos ticket rather than asking for the user's password.

Therefore:

```text
Attacker possesses valid ticket
              |
              v
Target receives valid Kerberos
authentication material
              |
              v
Authentication may succeed
```

The target normally cannot determine merely from the ticket whether it is being presented by:

```text
The legitimate user
```

or:

```text
Someone who stole the user's ticket
```

Detection therefore requires contextual analysis.

---

# Authentication vs Credential Knowledge

Pass-the-Ticket demonstrates that:

```text
Knowing Password
      !=
Required for every authentication
```

Once the ticket exists:

```text
Ticket
   |
   v
Authentication
```

may be sufficient.

This is expected Kerberos behaviour.

The vulnerability is the unauthorised exposure or theft of the ticket.

---

# Ticket Granting Ticket

A Ticket Granting Ticket is:

```text
TGT
```

Its service principal normally resembles:

```text
krbtgt/CORP.EXAMPLE@CORP.EXAMPLE
```

The TGT is presented to the KDC to obtain service tickets.

```text
TGT
 |
 v
KDC
 |
 +--> CIFS ticket
 +--> LDAP ticket
 +--> HTTP ticket
 +--> HOST ticket
```

A compromised TGT is therefore generally more flexible than a single compromised service ticket.

---

# Service Ticket

A service ticket is associated with a specific Service Principal Name.

Examples:

```text
cifs/server01.corp.example
ldap/dc01.corp.example
http/web01.corp.example
host/server01.corp.example
MSSQLSvc/sql01.corp.example:1433
```

A stolen service ticket generally provides authentication only to the relevant service.

For example:

```text
CIFS Ticket
    |
    v
CIFS/server01
    |
    v
SMB Authentication
```

It does not normally allow arbitrary new service tickets to be requested.

---

# TGT vs Service Ticket

| Property | TGT | Service Ticket |
|---|---|---|
| Presented to | KDC | Target service |
| Used to obtain additional tickets | Yes | Normally no |
| Associated service | `krbtgt` | Specific SPN |
| Potential reuse scope | Broad | Service-specific |
| Typical PtT impact | Potentially multiple services | Relevant service only |

The distinction is important during both testing and reporting.

---

# Pass-the-Ticket vs Pass-the-Key

Pass-the-Key begins with a Kerberos key:

```text
Kerberos Key
      |
      v
Request TGT
      |
      v
TGT
```

Pass-the-Ticket begins with an existing ticket:

```text
Existing Ticket
      |
      v
Use Ticket
```

Therefore:

```text
Pass-the-Key
     =
Key -> Ticket


Pass-the-Ticket
     =
Ticket -> Authentication
```

For detailed coverage:

[Pass-the-Key](pass-the-key.md)

---

# Pass-the-Ticket vs Pass-the-Hash

Pass-the-Hash normally uses an NT hash through NTLM:

```text
NT Hash
   |
   v
NTLM
   |
   v
Authentication
```

Pass-the-Ticket uses:

```text
Kerberos Ticket
      |
      v
Kerberos
      |
      v
Authentication
```

Comparison:

| Technique | Material | Protocol |
|---|---|---|
| Pass-the-Hash | NT hash | NTLM |
| Pass-the-Ticket | Kerberos ticket | Kerberos |

For detailed coverage:

[Pass-the-Hash](pass-the-hash.md)

---

# Pass-the-Ticket vs OverPass-the-Hash

OverPass-the-Hash uses NT/RC4-derived credential material to obtain Kerberos authentication:

```text
NT / RC4 Material
       |
       v
Request TGT
       |
       v
Kerberos
```

Pass-the-Ticket skips the ticket-request stage when a usable ticket has already been obtained:

```text
Existing Ticket
      |
      v
Kerberos Authentication
```

For detailed coverage:

[OverPass-the-Hash](overpass-the-hash.md)

---

# Pass-the-Ticket vs Kerberoasting

Kerberoasting:

```text
Request Service Ticket
        |
        v
Extract Crackable Material
        |
        v
Offline Password Guessing
```

Pass-the-Ticket:

```text
Existing Ticket
      |
      v
Reuse Ticket
      |
      v
Authentication
```

Kerberoasting attempts credential recovery.

Pass-the-Ticket performs credential reuse.

For detailed coverage:

[Kerberoasting](kerberoasting.md)

---

# Pass-the-Ticket vs Golden Ticket

Pass-the-Ticket usually reuses a legitimate ticket:

```text
Legitimate Ticket
      |
      v
Stolen
      |
      v
Reused
```

Golden Ticket attacks involve forged TGTs:

```text
Compromised krbtgt Key
        |
        v
Forge TGT
        |
        v
Forged Ticket
```

Therefore:

```text
Pass-the-Ticket
      =
Ticket reuse


Golden Ticket
      =
Ticket forgery
```

---

# Pass-the-Ticket vs Silver Ticket

A Silver Ticket is a forged service ticket created using compromised service-account key material.

```text
Service Key
    |
    v
Forge Service Ticket
    |
    v
Target Service
```

Pass-the-Ticket instead reuses an existing ticket.

```text
Existing Service Ticket
         |
         v
        Reuse
```

---

# Ticket Formats

Two formats frequently encountered during security testing are:

```text
.ccache
.kirbi
```

A useful model is:

```text
Linux / MIT Kerberos / Impacket
              |
              v
           .ccache


Windows Kerberos Tooling
              |
              v
            .kirbi
```

Both can contain sensitive reusable authentication material.

---

# .ccache

Credential cache files are commonly used by Linux Kerberos implementations and Impacket.

Example:

```text
alice.ccache
```

The file may contain:

```text
TGT
Service Tickets
Kerberos principals
Ticket validity information
```

Treat the entire file as a credential.

---

# .kirbi

Windows Kerberos tooling frequently exports tickets using:

```text
.kirbi
```

files.

Example:

```text
alice_tgt.kirbi
```

Again:

```text
.kirbi
   =
Credential
```

Do not store these files in public repositories or unsecured assessment folders.

---

# Ticket Conversion

During authorised cross-platform testing, a ticket may need conversion between formats.

```text
.kirbi
   |
   v
Convert
   |
   v
.ccache
```

or:

```text
.ccache
   |
   v
Convert
   |
   v
.kirbi
```

Impacket includes:

```text
ticketConverter.py
```

commonly installed as:

```text
impacket-ticketConverter
```

---

# Impacket ticketConverter

Check:

```bash
impacket-ticketConverter -h
```

General pattern:

```bash
impacket-ticketConverter input.kirbi output.ccache
```

The reverse conversion uses the same input/output concept:

```bash
impacket-ticketConverter input.ccache output.kirbi
```

Verify the current tool's help before relying on syntax copied from older documentation.

---

# Linux Pass-the-Ticket

On Linux, a common Pass-the-Ticket workflow uses:

```text
.ccache
    |
    v
KRB5CCNAME
    |
    v
Kerberos-aware application
```

---

# KRB5CCNAME

Set the ticket cache:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Check:

```bash
echo "$KRB5CCNAME"
```

---

# Inspect the Ticket

Use:

```bash
klist
```

Depending on the installed Kerberos implementation, encryption details may be shown with:

```bash
klist -e
```

Review:

```text
Default principal
Valid starting
Expires
Service principal
Encryption type
```

---

# Identify the Ticket Type

A TGT commonly appears as:

```text
krbtgt/CORP.EXAMPLE@CORP.EXAMPLE
```

A service ticket might appear as:

```text
cifs/server01.corp.example@CORP.EXAMPLE
```

or:

```text
ldap/dc01.corp.example@CORP.EXAMPLE
```

Always identify which ticket you possess before attempting validation.

---

# Validate Ticket Lifetime

Before troubleshooting authentication, check:

```bash
klist
```

Review:

```text
Start Time
End Time
Renew Until
```

An expired ticket will normally not authenticate.

---

# Kerberos-Aware Impacket Authentication

Many Impacket utilities support existing Kerberos ticket caches using:

```text
-k
-no-pass
```

depending on the tool.

The general concept is:

```text
KRB5CCNAME
     |
     v
Impacket
     |
     v
Existing Ticket
     |
     v
Kerberos Authentication
```

---

# SMB Authentication

A relatively low-impact validation can use:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This demonstrates:

```text
Ticket
  |
  v
Kerberos
  |
  v
SMB Authentication
```

without automatically executing commands.

---

# Hostnames Matter

Prefer:

```text
server01.corp.example
```

instead of:

```text
10.10.10.25
```

Kerberos service tickets are associated with SPNs such as:

```text
cifs/server01.corp.example
```

Using the IP address can prevent the expected Kerberos authentication path.

---

# DNS Resolution

Check:

```bash
getent hosts server01.corp.example
```

and:

```bash
getent hosts dc01.corp.example
```

Kerberos depends heavily on correct:

```text
DNS
Hostname
SPN
Realm
```

relationships.

---

# Time Synchronisation

Check:

```bash
date
```

Kerberos is time-sensitive.

Do not immediately conclude that a stolen ticket is invalid if authentication fails.

First verify:

```text
Ticket lifetime
DNS
Time
Hostname
SPN
Realm
KDC connectivity
```

---

# Remote Execution

A valid ticket may represent an account with administrative access.

Where explicitly authorised, Kerberos-aware remote administration tools may include:

```text
psexec
wmiexec
smbexec
atexec
```

However:

```text
Authentication Proof
        |
        v
Finding Demonstrated?
        |
    +---+---+
    |       |
   Yes      No
    |       |
    v       v
   Stop   Additional
          Validation
```

Do not automatically perform remote execution simply because the ticket permits it.

---

# psexec

Where remote execution is explicitly required and authorised:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-psexec \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This is not Pass-the-Ticket itself.

The stages are:

```text
Pass-the-Ticket
      |
      v
Kerberos Authentication
      |
      v
Administrative Access
      |
      v
PsExec-style Execution
```

---

# wmiexec

Where authorised:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-wmiexec \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

Again, distinguish:

```text
Authentication Technique
```

from:

```text
Execution Technique
```

---

# NetExec

NetExec supports Kerberos-aware workflows.

Review the current installed version:

```bash
nxc smb --help
```

because command-line options can change between releases.

Conceptually:

```text
Ticket Cache
     |
     v
NetExec
     |
     v
Kerberos Authentication
     |
     v
Access Analysis
```

For detailed usage:

[NetExec](netexec.md)

---

# Windows Pass-the-Ticket

Windows maintains Kerberos tickets inside logon sessions.

Conceptually:

```text
Windows Logon Session
        |
        +--> TGT
        |
        +--> CIFS Ticket
        |
        +--> LDAP Ticket
        |
        +--> HTTP Ticket
```

Pass-the-Ticket on Windows commonly involves placing reusable Kerberos authentication material into an appropriate logon session or otherwise making it available to the Windows Kerberos authentication stack.

---

# Native Windows Ticket Enumeration

Start with:

```powershell
klist
```

This allows inspection of tickets available to the current context without immediately using credential-access tooling.

Typical information includes:

```text
Client
Server
Ticket encryption type
Ticket flags
Start time
End time
Renew time
```

---

# Current TGT

Where supported:

```powershell
klist tgt
```

can display information about the current Ticket Granting Ticket.

Check:

```powershell
klist /?
```

for the exact capabilities of the Windows version being tested.

---

# Windows Logon Sessions

Tickets belong to logon sessions.

Conceptually:

```text
Windows
 |
 +--> Session A
 |      |
 |      +--> Alice TGT
 |      +--> Alice Service Tickets
 |
 +--> Session B
 |      |
 |      +--> Bob TGT
 |
 +--> SYSTEM
        |
        +--> Machine Tickets
```

Tickets in another security context should not be accessed during testing unless explicitly authorised.

---

# Rubeus

Rubeus is a Windows Kerberos security research tool frequently used for:

```text
Ticket enumeration
Ticket requests
Ticket import
Ticket export
Kerberos delegation testing
```

In Pass-the-Ticket workflows, the important conceptual capability is:

```text
Ticket
   |
   v
Import into Kerberos context
   |
   v
Windows authentication
```

Review the current Rubeus documentation and help output before testing because syntax and supported options depend on the build.

---

# Ticket Injection

Windows security tooling may allow a Kerberos ticket to be inserted into a logon session.

Conceptually:

```text
ticket.kirbi
      |
      v
Ticket Import
      |
      v
Windows Logon Session
      |
      v
Kerberos-Aware Application
```

The important point is that:

```text
Ticket Injection
      !=
Ticket Creation
```

The ticket already exists.

---

# Mimikatz

Mimikatz historically demonstrated Kerberos ticket manipulation and Pass-the-Ticket workflows.

Conceptually:

```text
Exported Kerberos Ticket
          |
          v
Import into Windows
authentication context
          |
          v
Kerberos Authentication
```

Use of credential-access tooling should be limited to environments where that level of testing is explicitly authorised.

---

# Linux vs Windows PtT

Linux:

```text
.ccache
   |
   v
KRB5CCNAME
   |
   v
Kerberos-Aware Tool
```

Windows:

```text
.kirbi / Ticket
       |
       v
Windows Logon Session
       |
       v
Kerberos-Aware Application
```

The underlying authentication principle is the same.

---

# TGT Reuse

A stolen TGT can be particularly useful because:

```text
TGT
 |
 v
KDC
 |
 +--> Request CIFS ticket
 |
 +--> Request LDAP ticket
 |
 +--> Request HTTP ticket
 |
 +--> Request HOST ticket
```

The available access still depends on the identity's privileges.

---

# Service Ticket Reuse

A stolen service ticket has a narrower scope.

Example:

```text
cifs/server01
      |
      v
CIFS Ticket
      |
      v
SMB on server01
```

It does not automatically provide:

```text
LDAP/DC01
HTTP/web01
MSSQLSvc/sql01
```

unless additional appropriate tickets are available.

---

# TGT Does Not Mean Domain Admin

Remember:

```text
TGT
 |
 v
Authenticated Identity
 |
 X
Automatic Privilege Escalation
```

A low-privilege user's TGT remains a low-privilege user's credential.

---

# Privileged Tickets

The impact becomes significantly greater when the ticket represents:

```text
Domain Admin
Server Administrator
Backup Administrator
Privileged Service Account
Highly Delegated Identity
```

The root problem is then:

```text
Privileged Authentication Material
             |
             v
Exposed to Lower-Trust Context
```

---

# Machine Account Tickets

Computer accounts can also possess tickets.

Examples:

```text
WORKSTATION01$
SERVER01$
DC01$
```

A compromised machine ticket represents the machine identity.

Its usefulness depends on the permissions assigned to that computer account.

Machine identities become particularly relevant to:

```text
RBCD
AD CS
Delegation
Kerberos Relay
Domain Controller Operations
```

---

# Service Account Tickets

Services running under domain identities may possess Kerberos tickets.

Examples:

```text
CORP\svc_sql
CORP\svc_web
CORP\svc_backup
```

A compromised service-account ticket can be particularly significant when the account has excessive privileges.

---

# Ticket Theft and Lateral Movement

A common attack path is:

```text
Workstation Compromise
        |
        v
Privileged User Authenticates
        |
        v
Privileged Ticket Present
        |
        v
Ticket Obtained
        |
        v
Pass-the-Ticket
        |
        v
Server Authentication
```

This is why privileged credential isolation is critical.

---

# BloodHound Analysis

BloodHound can help determine whether the ticket's identity has useful access before active validation.

```text
Ticket Identity
      |
      v
BloodHound
      |
      +--> Group Membership
      +--> AdminTo
      +--> CanRDP
      +--> CanPSRemote
      +--> ACL Rights
      +--> Sessions
```

This can reduce unnecessary authentication attempts.

For detailed usage:

[BloodHound](bloodhound.md)

---

# Authentication vs Lateral Movement

Keep the stages separate.

```text
Ticket Theft
     |
     v
Credential Access


Pass-the-Ticket
     |
     v
Credential Use


Remote SMB / WinRM / WMI
     |
     v
Lateral Movement
```

This improves technical reporting and ATT&CK mapping.

---

# Ticket Lifetime

Tickets are normally temporary.

```text
Issue
  |
  v
Valid
  |
  v
Expires
```

A stolen ticket's usefulness is therefore normally bounded by:

```text
Start Time
End Time
Renewal Conditions
Service Scope
Account Permissions
```

---

# Expired Tickets

Before attempting reuse:

```bash
klist
```

Check:

```text
Valid starting
Expires
Renew until
```

An expired ticket should not normally authenticate.

---

# Renewable Tickets

Some tickets can be renewed within the configured renewal period.

Conceptually:

```text
Ticket
 |
 v
Expires
 |
 +--> Renewable?
         |
      +--+--+
      |     |
     No    Yes
            |
            v
         Renewal
```

The ability to renew depends on ticket properties and policy.

---

# Password Rotation

Changing an account password changes its long-term password-derived keys.

However, an already issued ticket may remain usable for some period.

```text
Password A
    |
    v
Ticket Issued
    |
    v
Password Changed
    |
    v
Existing Ticket
```

The existing ticket does not necessarily disappear instantly.

This matters during incident response.

---

# Ticket vs Long-Term Credential Compromise

Determine whether the attacker obtained:

```text
Only Ticket
```

or:

```text
Password / NT Hash / AES Key
```

The difference is significant.

```text
Ticket Compromise
      |
      v
Temporary credential reuse


Long-Term Key Compromise
      |
      v
Potentially obtain new tickets
```

---

# Ticket Renewal vs New Ticket

Do not confuse:

```text
Renew existing ticket
```

with:

```text
Authenticate using long-term key
and obtain new ticket
```

They have different prerequisites.

---

# Cross-Domain Tickets

Active Directory trusts can involve Kerberos referral tickets.

Conceptually:

```text
Domain A User
     |
     v
Domain A TGT
     |
     v
Referral Ticket
     |
     v
Domain B
     |
     v
Service Ticket
```

Pass-the-Ticket analysis in multi-domain environments should identify exactly which domain and trust relationship the ticket belongs to.

---

# Delegation Relationship

Kerberos delegation can result in services handling authentication material representing other users.

```text
User
 |
 v
Front-End Service
 |
 v
Delegation
 |
 v
Back-End Service
```

This makes ticket security particularly important on delegation-enabled systems.

---

# Unconstrained Delegation

Systems configured for unconstrained delegation are especially sensitive because authentication by high-value identities can expose reusable Kerberos material to the delegated system.

A simplified security model is:

```text
Privileged User
      |
      v
Delegation-Enabled Host
      |
      v
Reusable Kerberos Material
      |
      v
Host Compromise
      |
      v
Potential Ticket Theft
```

This is one reason unconstrained delegation is considered high risk.

---

# Constrained Delegation

Constrained delegation limits delegation to defined services.

Conceptually:

```text
Front-End Service
      |
      +--> CIFS/server01
      |
      +--> HTTP/app01
```

The resulting Kerberos flows rely heavily on service tickets and S4U extensions.

---

# Resource-Based Constrained Delegation

RBCD controls delegation from the resource side.

A simplified model is:

```text
Target Resource
      |
      v
Who may act on behalf
of users to this resource?
```

Ticket acquisition and service-ticket use are central to RBCD attack paths.

---

# Detection

Pass-the-Ticket is difficult to detect using one event because the ticket itself may be cryptographically valid.

Detection should focus on context.

```text
Valid Kerberos Ticket
         |
         v
Which Account?
         |
         v
Which Source?
         |
         v
Which Service?
         |
         v
Expected Behaviour?
         |
         v
What Happened Next?
```

---

# Important Event IDs

Useful Windows events include:

```text
4768 - Kerberos TGT requested
4769 - Kerberos service ticket requested
4770 - Kerberos service ticket renewed
4771 - Kerberos pre-authentication failed
4624 - Successful logon
4672 - Special privileges assigned
```

The exact events available depend on audit configuration and the particular PtT workflow.

---

# Important Detection Nuance

A key distinction is whether the attacker reuses:

```text
TGT
```

or:

```text
Existing Service Ticket
```

For example, reuse of an already issued service ticket may not require a fresh TGS request at the moment it is presented to the target.

Therefore:

```text
No new 4769
     |
     X
Does not prove PtT did not occur
```

Target-side and endpoint telemetry remain important.

---

# Event 4768

Event `4768` records TGT requests.

If the attacker already possesses a valid TGT:

```text
Stolen TGT
    |
    v
Reuse
```

there may be no need for a new AS exchange simply to use that TGT.

Therefore `4768` should not be treated as a universal PtT detection event.

---

# Event 4769

If a stolen TGT is used to request a new service ticket:

```text
Stolen TGT
    |
    v
TGS-REQ
    |
    v
4769
```

This can provide useful domain-controller telemetry.

Analyse:

```text
Account
Client Address
Service Name
Ticket Encryption Type
Ticket Options
Result
```

---

# Event 4624

When the resulting ticket is presented to a Windows service, the target may generate:

```text
4624
```

Review:

```text
Account Name
Account Domain
Logon Type
Authentication Package
Source Network Address
Workstation
```

---

# Event 4672

Privileged logons may produce:

```text
4672
```

Correlate:

```text
4624
 +
4672
```

where relevant.

---

# Source Host Analysis

Suppose an administrator normally authenticates from:

```text
PAW01
MGMT01
```

but ticket-based access suddenly appears from:

```text
WKSTN042
```

The unusual source relationship may be more useful than the Kerberos protocol itself.

---

# Ticket Behaviour Analysis

Detection can consider:

```text
Account
   |
   v
Normal Source Hosts
   |
   v
Observed Source Host
   |
   v
Requested SPNs
   |
   v
Target Systems
   |
   v
Time
   |
   v
Subsequent Activity
```

---

# Network Detection

Kerberos-aware network monitoring may identify:

```text
AS-REQ
AS-REP
TGS-REQ
TGS-REP
AP-REQ
```

However, Pass-the-Ticket uses valid protocol messages.

Detection should therefore not rely only on malformed Kerberos traffic.

---

# Endpoint Detection

On Windows endpoints, additional signals may include:

```text
Unusual ticket manipulation
Credential-access tooling
Suspicious LSASS access
Unexpected logon-session changes
Unusual processes using privileged identities
```

The exact signals depend on the method used to obtain and inject the ticket.

---

# Ticket Theft Detection

Detecting PtT should begin before the ticket is actually reused.

Monitor for credential-access behaviour involving:

```text
LSASS
Kerberos ticket caches
Privileged sessions
Security process memory
Credential files
```

Preventing ticket theft is generally stronger than trying to distinguish malicious use of an otherwise valid ticket.

---

# Purple Team Validation

A safe Pass-the-Ticket exercise can use:

```text
Dedicated Test Account
        |
        v
Legitimate TGT
        |
        v
Export / Controlled Transfer
        |
        v
Authorised Assessment Host
        |
        v
Single Service Authentication
        |
        v
Blue Team Investigation
```

Use an account with limited permissions and a dedicated test server where possible.

---

# Purple Team Exercise Flow

```text
Red Team
   |
   | Controlled ticket
   v
Assessment Host
   |
   | TGS request if needed
   v
Domain Controller
   |
   | 4769
   v
Target Server
   |
   | Kerberos authentication
   v
4624
   |
   v
Blue Team
```

---

# Purple Team Questions

Defenders should determine:

```text
Which account was used?

Which system initiated the activity?

Was a new TGT requested?

Was a new service ticket requested?

Which SPN was involved?

Which target accepted the ticket?

Was the source expected?

Did privileged activity follow?

Can the original ticket-theft event be identified?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect
Time to triage
Account identified?
Source identified?
Target identified?
Service identified?
Ticket type identified?
Credential reuse recognised?
Original ticket exposure identified?
Containment decision correct?
```

---

# Hardening

Pass-the-Ticket is primarily prevented by protecting Kerberos authentication material.

```text
Pass-the-Ticket
      |
      +--> Protect credentials
      |
      +--> Protect ticket caches
      |
      +--> Credential Guard
      |
      +--> LSA protection
      |
      +--> Privileged access isolation
      |
      +--> Administrative tiering
      |
      +--> Restricted privileged logons
      |
      +--> Delegation hardening
      |
      +--> Least privilege
      |
      +--> Segmentation
      |
      +--> Monitoring
```

---

# Credential Guard

Windows Defender Credential Guard can reduce exposure of reusable credential material.

Its defensive objective is:

```text
Compromised Process
        |
        X
Protected Credentials
```

Deploy where supported and operationally appropriate.

---

# LSA Protection

Additional LSA protection can make unauthorised access to LSASS more difficult.

This should complement:

```text
Credential Guard
EDR
Least privilege
Administrative isolation
Patch management
```

---

# Protect Privileged Sessions

Avoid allowing privileged accounts to authenticate to lower-trust systems.

Bad:

```text
Domain Admin
    |
    v
Employee Workstation
    |
    v
Privileged Ticket Exposure
```

Better:

```text
Domain Admin
    |
    v
Privileged Access Workstation
    |
    v
Tier 0 Systems
```

---

# Administrative Tiering

Separate administrative identities and systems by privilege level.

A useful model is:

```text
Tier 0
 |
 +--> Domain Controllers
 +--> Identity Infrastructure
 +--> Enterprise Admin Functions


Tier 1
 |
 +--> Servers
 +--> Applications


Tier 2
 |
 +--> Workstations
 +--> User Devices
```

Avoid credential paths from higher trust to lower trust.

---

# Privileged Access Workstations

Dedicated administrative systems reduce the opportunity for privileged tickets to appear on compromised user endpoints.

```text
Privileged Identity
       |
       v
PAW
       |
       v
Privileged Resource
```

---

# Protected Users

The Protected Users security group can provide additional protections for suitable high-value accounts.

Evaluate compatibility before deployment.

---

# Authentication Policies

Authentication policies and silos can restrict where sensitive accounts are permitted to authenticate.

Conceptually:

```text
Tier 0 Admin
     |
     +--> PAW01
     |
     X
USER-PC01
```

This limits the environments where privileged tickets can be created.

---

# Restrict Delegation

Review:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

Remove unnecessary delegation and protect systems that legitimately require it.

---

# Least Privilege

If a low-privilege user's ticket is stolen:

```text
Low Privilege
     |
     v
Limited Impact
```

If a highly privileged ticket is stolen:

```text
High Privilege
     |
     v
High Impact
```

Reducing standing privilege directly reduces PtT impact.

---

# Network Segmentation

A stolen ticket should not automatically provide network reachability to every service.

Example:

```text
User Network
     |
     X
SMB / WinRM / WMI
     |
     v
Server Management Network
```

Authentication and network access should be separate security controls.

---

# Ticket Lifetime

Appropriate Kerberos ticket lifetimes can reduce the window in which stolen tickets remain useful.

However:

```text
Shorter Lifetime
       |
       X
Prevents ticket theft
```

It limits exposure duration rather than fixing the root cause.

---

# Credential Rotation

If only an individual ticket was exposed, determine whether the underlying account credential was also compromised.

If the long-term credential is compromised:

```text
Password / Key Compromised
          |
          v
Rotate Credential
          |
          v
New Key Material
```

The response should address the source of credential exposure as well.

---

# Incident Response

A Pass-the-Ticket response workflow can be:

```text
Suspicious Authentication
        |
        v
Identify Account
        |
        v
Identify Source Host
        |
        v
Identify Target
        |
        v
Determine Ticket Type
        |
        v
Review 4768 / 4769
        |
        v
Review Target 4624
        |
        v
Identify Ticket Exposure Source
        |
        v
Determine Long-Term Credential Exposure
        |
        v
Contain Systems
        |
        v
Rotate Credentials if Required
        |
        v
Investigate Lateral Movement
```

---

# Reporting

The finding should describe the root cause.

Possible titles include:

```text
Exposed Kerberos Ticket Enables Authentication Without Password
```

```text
Reusable Kerberos Authentication Material Accessible to Unprivileged Context
```

```text
Privileged Kerberos Ticket Exposure Enables Lateral Movement
```

```text
Compromised Kerberos Ticket Enables Unauthorised Service Access
```

---

# Avoid Overstatement

Do not report:

```text
Kerberos ticket exists
      =
Vulnerability
```

Kerberos tickets are expected.

The vulnerability normally requires:

```text
Unauthorised Ticket Access
          |
          +
Ticket Reusable
          |
          +
Useful Identity Permissions
```

---

# Report the Actual Ticket Type

Avoid writing only:

```text
A Kerberos ticket was stolen.
```

Prefer:

```text
A valid Ticket Granting Ticket for CORP\adminuser was accessible
from the compromised endpoint.
```

or:

```text
A valid CIFS service ticket for server01.corp.example was exposed.
```

This makes the demonstrated impact clearer.

---

# Example Finding

```text
Finding:
Privileged Kerberos Ticket Exposure Enables Authentication Without Password

Affected Account:
CORP\adminuser

Affected Host:
WORKSTATION01

Validation:
During the authorised assessment, a valid Kerberos Ticket Granting
Ticket associated with the affected account was accessible from the
compromised test endpoint.

The ticket was transferred to the authorised assessment environment
and used to authenticate to a designated test service without supplying
the account's plaintext password or long-term key.

No additional remote execution was required to demonstrate the issue.

Impact:
An attacker capable of obtaining the exposed TGT may authenticate as
the affected identity for the valid lifetime of the ticket and may
request service tickets for resources available to that account.

The impact is therefore determined by the privileges and network access
assigned to the affected identity.

Recommendation:
Prevent privileged accounts from authenticating to lower-trust systems,
strengthen credential and ticket isolation, deploy Credential Guard and
LSA protection where appropriate, restrict privileged logon locations,
review delegation, and investigate the mechanism that allowed the ticket
to become accessible.
```

---

# Evidence Collection

Record:

```text
Account
Domain
Source Host
Ticket Type
Ticket Source
Ticket Service Principal
Ticket Start Time
Ticket End Time
Renew Time
Encryption Type
Ticket Flags
Assessment Host
Target Host
Target Service
Authentication Result
Privilege Level
Relevant Event IDs
Tool
Command
```

---

# Evidence Redaction

Do not include complete:

```text
.ccache files
.kirbi files
Base64 tickets
Session keys
Kerberos keys
```

in ordinary reports.

Use:

```text
Ticket:
[REDACTED]
```

or appropriately masked evidence.

---

# Secure Ticket Storage

Temporary assessment tickets should be stored only where required.

For example:

```bash
chmod 600 alice.ccache
```

where appropriate.

Do not:

```text
Commit to Git
Upload to public issue trackers
Place in shared screenshots
Store in world-readable directories
Retain indefinitely
```

---

# Cleanup on Linux

Unset the active cache:

```bash
unset KRB5CCNAME
```

Where appropriate:

```bash
kdestroy
```

Remove temporary ticket files according to the engagement's evidence-retention policy:

```bash
rm -f alice.ccache
```

---

# Cleanup on Windows

In a dedicated test session, tickets can be reviewed with:

```powershell
klist
```

and where appropriate purged using:

```powershell
klist purge
```

Be aware that purging Kerberos tickets can disrupt authenticated access in the current logon session.

---

# Troubleshooting

## Ticket Not Found

Check:

```bash
echo "$KRB5CCNAME"
```

Then:

```bash
ls -l "$KRB5CCNAME"
```

and:

```bash
klist
```

---

# Expired Ticket

Check:

```bash
klist
```

Review:

```text
Expires
Renew until
```

Do not repeatedly change unrelated settings when the ticket has simply expired.

---

# Incorrect Principal

The ticket's principal must match the identity expected by the Kerberos-aware application.

Inspect:

```bash
klist
```

and verify:

```text
Username
Domain
Realm
```

---

# DNS Failure

Check:

```bash
getent hosts server01.corp.example
```

and:

```bash
getent hosts dc01.corp.example
```

Kerberos depends heavily on correct name resolution.

---

# SPN Failure

If the requested service principal does not exist or does not match the target:

```text
Hostname
   |
   v
SPN mismatch
   |
   v
Kerberos failure
```

Check the actual service and hostname.

---

# IP Address Authentication Fails

Prefer:

```text
server01.corp.example
```

rather than:

```text
10.10.10.25
```

when Kerberos authentication is intended.

---

# Clock Skew

Check:

```bash
date
```

On Windows:

```powershell
w32tm /query /status
```

Kerberos may reject requests when clock skew exceeds policy tolerances.

---

# Authentication Works but Access Is Denied

Remember:

```text
Authentication
      !=
Authorisation
```

The ticket may be valid while the represented account lacks permission to the resource.

---

# Kerberos Falls Back to NTLM

If the application supports Negotiate:

```text
Kerberos fails
     |
     v
NTLM fallback
```

may occur.

Do not claim Pass-the-Ticket success without verifying that Kerberos was actually used.

---

# Verify Kerberos

Use combinations of:

```text
klist
Domain Controller Events
Target Events
Packet Capture
Application Telemetry
```

where appropriate.

---

# Common Mistakes

## Mistake 1 - Treating `.ccache` as a Normal File

```text
.ccache
   =
Credential
```

---

## Mistake 2 - Treating `.kirbi` as Harmless Output

```text
.kirbi
   =
Credential
```

---

## Mistake 3 - Confusing Pass-the-Key and Pass-the-Ticket

```text
Key -> Obtain Ticket
     =
Pass-the-Key


Existing Ticket -> Authentication
     =
Pass-the-Ticket
```

---

## Mistake 4 - Confusing TGT and TGS

```text
TGT
 |
 v
KDC


Service Ticket
 |
 v
Target Service
```

---

## Mistake 5 - Assuming a TGT Gives Administrator Access

The TGT represents the existing account privileges.

---

## Mistake 6 - Using IP Addresses Everywhere

Kerberos normally depends on hostnames and SPNs.

---

## Mistake 7 - Ignoring Ticket Expiration

Check `klist` before troubleshooting complex issues.

---

## Mistake 8 - Ignoring DNS

Many Kerberos failures are actually name-resolution failures.

---

## Mistake 9 - Ignoring Time

Clock skew can break otherwise valid Kerberos authentication.

---

## Mistake 10 - Assuming 4768 Must Appear During PtT

Reusing an already issued TGT does not inherently require a new AS request.

---

## Mistake 11 - Assuming 4769 Must Always Appear

Reusing an already obtained service ticket against its target may not require requesting another service ticket at that moment.

---

## Mistake 12 - Performing Remote Execution Immediately

Authentication-only validation may already prove the finding.

---

## Mistake 13 - Reporting the Ticket Instead of the Root Cause

The ticket's existence is normal.

Investigate why an unauthorised party could obtain it.

---

# Assessment Checklist

## Preparation

- [ ] Confirm Pass-the-Ticket testing is authorised
- [ ] Confirm permitted accounts
- [ ] Confirm permitted hosts
- [ ] Confirm permitted services
- [ ] Confirm remote execution restrictions
- [ ] Identify domain
- [ ] Identify realm
- [ ] Identify domain controller
- [ ] Confirm DNS
- [ ] Confirm time synchronisation

## Ticket Analysis

- [ ] Identify ticket owner
- [ ] Identify TGT or service ticket
- [ ] Identify service principal
- [ ] Identify ticket source
- [ ] Record start time
- [ ] Record expiration
- [ ] Record renewal time
- [ ] Record encryption type
- [ ] Record ticket flags
- [ ] Protect ticket material

## Linux Validation

- [ ] Identify `.ccache`
- [ ] Set `KRB5CCNAME`
- [ ] Run `klist`
- [ ] Confirm principal
- [ ] Confirm ticket validity
- [ ] Use hostname
- [ ] Perform minimum authentication test

## Windows Validation

- [ ] Review `klist`
- [ ] Identify current logon context
- [ ] Identify ticket type
- [ ] Avoid unrelated user sessions
- [ ] Perform only authorised ticket operations
- [ ] Confirm Kerberos authentication

## Privilege Analysis

- [ ] Review group memberships
- [ ] Review BloodHound
- [ ] Identify `AdminTo`
- [ ] Identify remote-management rights
- [ ] Identify delegated AD permissions
- [ ] Determine actual business impact

## Detection

- [ ] Review 4768 where relevant
- [ ] Review 4769 where relevant
- [ ] Review 4770 where relevant
- [ ] Review 4624
- [ ] Review 4672 where relevant
- [ ] Identify source host
- [ ] Identify target service
- [ ] Compare source against account baseline
- [ ] Investigate ticket acquisition
- [ ] Correlate subsequent activity

## Remediation

- [ ] Identify root cause of ticket exposure
- [ ] Determine whether long-term credentials were compromised
- [ ] Rotate credentials where required
- [ ] Deploy Credential Guard where appropriate
- [ ] Enable LSA protection where appropriate
- [ ] Restrict privileged logons
- [ ] Implement administrative tiering
- [ ] Review delegation
- [ ] Apply least privilege
- [ ] Segment management services
- [ ] Improve Kerberos monitoring

## Cleanup

- [ ] Unset `KRB5CCNAME`
- [ ] Destroy temporary Kerberos caches
- [ ] Remove `.ccache` files
- [ ] Remove `.kirbi` files
- [ ] Purge dedicated Windows test-session tickets if appropriate
- [ ] Secure retained evidence
- [ ] Redact reusable ticket data

---

# Pass-the-Ticket Testing Model

The core model is:

```text
                         Kerberos Ticket
                               |
                   +-----------+-----------+
                   |                       |
                   v                       v
                  TGT                Service Ticket
                   |                       |
                   v                       |
                  KDC                      |
                   |                       |
                   v                       |
          Request Service Ticket           |
                   |                       |
                   +-----------+-----------+
                               |
                               v
                        Target Service
                               |
                               v
                         Authentication
                               |
                               v
                         Authorisation
                               |
                         +-----+-----+
                         |           |
                         v           v
                       Allow        Deny
```

The credential relationship is:

```text
                    Credential Material
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
     NT Hash          Kerberos Key       Kerberos Ticket
        |                  |                  |
        v                  v                  v
 Pass-the-Hash       Pass-the-Key       Pass-the-Ticket
        |                  |                  |
        v                  v                  v
      NTLM               Kerberos           Kerberos
```

Ticket theft should be modelled separately from ticket use:

```text
Compromised Host
       |
       v
Credential Access
       |
       v
Kerberos Ticket Obtained
       |
       v
Pass-the-Ticket
       |
       v
Authentication
       |
       v
Potential Lateral Movement
```

Ticket theft and ticket forgery are also distinct:

```text
                  Kerberos Ticket Abuse
                          |
             +------------+------------+
             |                         |
             v                         v
         Ticket Theft              Ticket Forgery
             |                         |
             v                  +------+------+
      Pass-the-Ticket           |             |
                                v             v
                           Golden Ticket  Silver Ticket
```

The defensive model is:

```text
Pass-the-Ticket
      |
      +--> Prevent Ticket Theft
      |       |
      |       +--> Credential Guard
      |       +--> LSA Protection
      |       +--> EDR
      |
      +--> Protect Privileged Sessions
      |       |
      |       +--> PAWs
      |       +--> Administrative Tiering
      |       +--> Restricted Logons
      |
      +--> Reduce Ticket Exposure
      |       |
      |       +--> Delegation Hardening
      |       +--> Protected Users
      |       +--> Authentication Policies
      |
      +--> Reduce Impact
      |       |
      |       +--> Least Privilege
      |       +--> Segmentation
      |
      +--> Detect
              |
              +--> 4768
              +--> 4769
              +--> 4770
              +--> 4624
              +--> Endpoint Telemetry
              +--> Behaviour Baselines
```

The assessment should answer:

```text
Where did the ticket come from?
        |
        v
Which identity does it represent?
        |
        v
Is it a TGT or service ticket?
        |
        v
Is it still valid?
        |
        v
What service or services can it access?
        |
        v
Can it authenticate without the password?
        |
        v
What privileges does the identity possess?
        |
        v
Was only the ticket compromised?
        |
        v
Or was long-term key material also exposed?
        |
        v
Can defenders detect the ticket acquisition?
        |
        v
Can defenders detect the ticket reuse?
        |
        v
Which defensive control breaks the path?
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

NTLM:

[NTLM](ntlm.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement Pass-the-Ticket and can be linked once their dedicated notes are available:

```text
active-directory/unconstrained-delegation.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
active-directory/golden-ticket.md
active-directory/silver-ticket.md
active-directory/trust-tickets.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft Kerberos

[Microsoft - Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Protocol Extensions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos supported encryption types](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-supported-encryption-types){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Credential Protection

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Configure added LSA protection](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Auditing

[Microsoft - Event 4768](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4769](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4624](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Use Alternate Authentication Material](https://attack.mitre.org/techniques/T1550/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket ticketConverter](https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py){ target="_blank" rel="noopener noreferrer" }

[Impacket getTGT](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

[Impacket getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

---

## Rubeus

[Rubeus](https://github.com/GhostPack/Rubeus){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Pass-the-Ticket is fundamentally a credential-reuse technique.

The attacker does not need to know:

```text
Plaintext Password
```

and does not necessarily need:

```text
NT Hash
AES Key
```

if a usable Kerberos ticket has already been obtained.

The core attack path is:

```text
Kerberos Ticket
      |
      v
Ticket Reuse
      |
      v
Kerberos Authentication
      |
      v
Account Permissions
```

The most important ticket distinction is:

```text
TGT
 |
 +--> Presented to KDC
 |
 +--> Can obtain service tickets


Service Ticket
 |
 +--> Presented to specific service
 |
 +--> Narrower scope
```

The major authentication-material distinctions are:

```text
Pass-the-Hash
     =
NT hash -> NTLM


OverPass-the-Hash
     =
NT / RC4 material -> Kerberos TGT


Pass-the-Key
     =
Kerberos key -> Kerberos TGT


Pass-the-Ticket
     =
Existing ticket -> Kerberos authentication


Golden Ticket
     =
Forged TGT


Silver Ticket
     =
Forged service ticket
```

The defensive lesson is:

```text
Strong Password
      |
      X
Protects already stolen ticket
```

Once a valid ticket has been stolen, password knowledge is not required to present that ticket during its usable lifetime.

The complete defensive model therefore requires:

```text
Credential Protection
        +
Ticket Protection
        +
Privileged Session Isolation
        +
Credential Guard
        +
LSA Protection
        +
Administrative Tiering
        +
Restricted Privileged Logons
        +
Delegation Hardening
        +
Least Privilege
        +
Network Segmentation
        +
Kerberos and Endpoint Monitoring
```

A mature Pass-the-Ticket assessment should determine how the ticket became exposed, whether it is a TGT or service ticket, which identity and service it represents, whether it remains valid, whether it can authenticate to an authorised target without the account password, what privileges become available, whether long-term credential material was also compromised, whether defenders can identify both the ticket acquisition and subsequent reuse, and which defensive control most effectively breaks the attack path.
