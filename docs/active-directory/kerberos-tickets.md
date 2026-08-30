# Kerberos Tickets

Kerberos tickets are cryptographic authentication artefacts used by Active Directory to allow users and computers to authenticate to services without repeatedly transmitting or supplying their passwords.

Understanding Kerberos tickets is essential before studying techniques such as:

```text
Pass-the-Ticket
OverPass-the-Hash
Pass-the-Key
Kerberoasting
Golden Tickets
Silver Tickets
Delegation Abuse
S4U
Kerberos Relay
```

The basic Kerberos authentication model is:

```text
User / Computer
      |
      | Credentials
      v
     KDC
      |
      v
     TGT
      |
      | Request service access
      v
     KDC
      |
      v
Service Ticket
      |
      v
Target Service
```

Two ticket types are particularly important:

```text
TGT
Ticket Granting Ticket

TGS
Service Ticket
```

A Ticket Granting Ticket proves that an identity has authenticated to the Kerberos Key Distribution Center.

A service ticket proves that the KDC has authorised that identity to authenticate to a particular Kerberos service.

!!! warning "Authorised testing only"
    Kerberos tickets are reusable authentication material. Treat `.ccache`, `.kirbi`, exported tickets, session caches, and screenshots containing ticket data as credentials. Only obtain, export, inject, convert, or reuse tickets for accounts and systems explicitly included in the assessment scope.

---

# Kerberos Ticket Model

A simplified Kerberos workflow is:

```text
              Active Directory
                    |
                    v
                   KDC
              +-----+-----+
              |           |
              v           v
             AS          TGS
              |           |
              v           v
             TGT     Service Ticket
              |           |
              +-----+-----+
                    |
                    v
               Authentication
```

The full client flow is:

```text
Client
  |
  | AS-REQ
  v
KDC Authentication Service
  |
  | AS-REP
  v
TGT
  |
  | TGS-REQ
  v
KDC Ticket Granting Service
  |
  | TGS-REP
  v
Service Ticket
  |
  v
Target Service
```

---

# Key Distribution Center

The Kerberos Key Distribution Center is normally provided by Active Directory domain controllers.

Conceptually, the KDC contains two logical functions:

```text
KDC
 |
 +--> Authentication Service
 |       |
 |       +--> Issues TGTs
 |
 +--> Ticket Granting Service
         |
         +--> Issues service tickets
```

Kerberos normally uses:

```text
TCP/88
UDP/88
```

---

# Authentication Service Exchange

The initial Kerberos authentication exchange is:

```text
AS-REQ
   |
   v
KDC
   |
   v
AS-REP
```

The successful result is normally a Ticket Granting Ticket.

```text
AS-REQ
   |
   v
Identity authentication
   |
   v
AS-REP
   |
   v
TGT
```

---

# AS-REQ

The client sends an Authentication Service Request:

```text
AS-REQ
```

The request identifies the account and asks the KDC for a Ticket Granting Ticket.

Where Kerberos pre-authentication is required, the client must demonstrate possession of appropriate account key material.

Conceptually:

```text
Account
   +
Cryptographic proof
   |
   v
AS-REQ
```

---

# Kerberos Pre-Authentication

In a typical Active Directory environment:

```text
Client
   |
   | Timestamp encrypted
   | with account key
   v
KDC
   |
   | Validate
   v
Authenticated
```

The KDC can verify that the client possesses the correct account key.

This helps prevent arbitrary users from requesting crackable authentication material for accounts.

Accounts where pre-authentication is disabled can be relevant to:

```text
AS-REP Roasting
```

---

# AS-REP

If the AS-REQ succeeds, the KDC returns:

```text
AS-REP
```

The response includes authentication material that allows the client to use the TGT.

Conceptually:

```text
AS-REP
 |
 +--> TGT
 |
 +--> Client/KDC session information
```

---

# Ticket Granting Ticket

The Ticket Granting Ticket is usually abbreviated:

```text
TGT
```

Its service principal typically resembles:

```text
krbtgt/CORP.EXAMPLE@CORP.EXAMPLE
```

The TGT allows the identity to request service tickets without re-entering the password for each service.

```text
User
 |
 v
TGT
 |
 +--> CIFS ticket
 |
 +--> LDAP ticket
 |
 +--> HTTP ticket
 |
 +--> HOST ticket
 |
 +--> MSSQLSvc ticket
```

---

# Why the TGT Matters

Without Kerberos ticketing, a user might need to repeatedly authenticate using long-term credentials.

Instead:

```text
Password / Key
      |
      v
Initial Authentication
      |
      v
TGT
      |
      v
Temporary Authentication Material
      |
      v
Multiple Service Requests
```

This reduces repeated exposure of long-term credentials.

However, it creates another security requirement:

```text
Protect the TGT
```

because the TGT itself becomes valuable authentication material.

---

# krbtgt

The `krbtgt` account is a special Active Directory account used by Kerberos.

Conceptually:

```text
krbtgt secret
      |
      v
Protects TGT integrity
      |
      v
Domain Kerberos trust
```

Ordinary users do not authenticate interactively as `krbtgt`.

Its credential material is critical to the security of the domain.

Compromise of the `krbtgt` secret is associated with:

```text
Golden Ticket
```

attack paths.

---

# TGS Exchange

Once a client possesses a TGT, it can request a ticket for a specific service.

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

---

# TGS-REQ

The Ticket Granting Service Request asks the KDC for access to a particular service principal.

For example:

```text
cifs/server01.corp.example
```

Conceptually:

```text
TGT
 +
Requested SPN
 |
 v
TGS-REQ
```

---

# TGS-REP

If the request is valid, the KDC returns:

```text
TGS-REP
```

containing the service ticket.

```text
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

---

# Service Tickets

A service ticket is intended for a particular Kerberos service.

Common SPNs include:

```text
cifs/server01.corp.example
ldap/dc01.corp.example
host/server01.corp.example
http/web01.corp.example
MSSQLSvc/sql01.corp.example:1433
```

The relationship is:

```text
Identity
   |
   v
TGT
   |
   v
Request access to CIFS
   |
   v
CIFS Service Ticket
   |
   v
SMB Service
```

---

# TGT vs Service Ticket

This distinction is fundamental.

## TGT

```text
TGT
 |
 v
Used with KDC
 |
 v
Request additional tickets
```

## Service Ticket

```text
Service Ticket
      |
      v
Presented to service
      |
      v
Authenticate to resource
```

Comparison:

| Property | TGT | Service Ticket |
|---|---|---|
| Primary purpose | Request service tickets | Authenticate to a service |
| Associated service | `krbtgt` | Specific SPN |
| Presented to | KDC | Target service |
| Useful for obtaining more tickets | Yes | Normally no |
| Security value | Very high | Limited to relevant service/context |

---

# Service Principal Names

Kerberos identifies services using:

```text
Service Principal Names
```

or:

```text
SPNs
```

Examples:

```text
cifs/fileserver.corp.example
ldap/dc01.corp.example
http/intranet.corp.example
MSSQLSvc/sql01.corp.example:1433
```

The relationship is:

```text
Hostname
   +
Service
   |
   v
SPN
   |
   v
Service Ticket
```

---

# Why Hostnames Matter

Kerberos is strongly name-based.

For example:

```text
server01.corp.example
```

may map naturally to:

```text
cifs/server01.corp.example
```

Using:

```text
10.10.10.25
```

instead may prevent the client from obtaining or selecting the expected service ticket.

Therefore:

```text
Kerberos
   |
   +--> DNS
   |
   +--> Hostnames
   |
   +--> SPNs
```

are closely related.

---

# Kerberos Realm

Kerberos uses the concept of a:

```text
Realm
```

An Active Directory DNS domain:

```text
corp.example
```

is commonly represented as the Kerberos realm:

```text
CORP.EXAMPLE
```

You may therefore encounter:

```text
alice@CORP.EXAMPLE
```

---

# NetBIOS vs DNS Domain vs Realm

These values are related but not identical.

Example:

```text
NetBIOS:
CORP

DNS Domain:
corp.example

Kerberos Realm:
CORP.EXAMPLE
```

Different tools may expect different forms.

Do not blindly substitute one for another.

---

# Ticket Contents

Kerberos tickets contain information required to authenticate an identity.

At a conceptual level, a ticket may include:

```text
Client identity
Service identity
Validity period
Session key information
Flags
Authorisation information
Encryption metadata
```

Some information is visible to the client while sensitive ticket portions are cryptographically protected.

---

# Ticket Encryption

Different parts of Kerberos exchanges use different keys.

For a service ticket:

```text
Service Ticket
      |
      v
Encrypted for target service
```

The service can validate the ticket because it possesses the appropriate long-term key.

Conceptually:

```text
KDC
 |
 | Encrypt ticket
 | using service key
 v
Service Ticket
 |
 v
Target Service
 |
 | Decrypt / validate
 v
Authentication
```

---

# TGT Protection

The TGT is protected using key material associated with:

```text
krbtgt
```

Conceptually:

```text
KDC
 |
 | Protect TGT
 v
TGT
 |
 v
Returned to client
```

The client does not need the `krbtgt` key to use the ticket.

It presents the TGT back to the KDC when requesting service tickets.

---

# Session Keys

Kerberos uses temporary session keys during authentication.

A simplified model is:

```text
Long-Term Credential
       |
       v
Initial Authentication
       |
       v
Temporary Session Keys
       |
       v
Ticket-Based Authentication
```

This reduces the need to repeatedly use the account's long-term password-derived key.

---

# Ticket Flags

Kerberos tickets contain flags describing permitted ticket behaviour.

Common flags may include:

```text
forwardable
renewable
initial
pre_authent
name_canonicalize
```

The exact flags depend on ticket type and policy.

---

# Forwardable Tickets

A ticket marked:

```text
forwardable
```

may participate in Kerberos delegation scenarios.

Conceptually:

```text
User Ticket
    |
    v
Delegating Service
    |
    v
Backend Service
```

Delegation requires careful analysis because it can expose powerful authentication paths.

---

# Renewable Tickets

Kerberos tickets may be renewable.

Conceptually:

```text
Ticket
 |
 | Valid until
 v
Expiry

but

Renewable Until
 |
 v
Potential renewal period
```

The exact behaviour depends on domain policy and ticket properties.

---

# Ticket Lifetime

Kerberos tickets are temporary.

Conceptually:

```text
Issue Time
   |
   v
Valid Period
   |
   v
Expiration
```

A ticket may contain:

```text
Start time
End time
Renew-until time
```

This limits how long stolen tickets remain directly useful.

---

# Domain Kerberos Policy

Kerberos ticket lifetime is influenced by domain policy.

Administrators can inspect relevant policy through Group Policy.

Common policy areas include:

```text
Maximum lifetime for user ticket
Maximum lifetime for service ticket
Maximum lifetime for user ticket renewal
Maximum tolerance for computer clock synchronization
```

---

# Time Synchronisation

Kerberos depends on reasonably synchronised clocks.

```text
Client Time
     |
     +---- close enough ----+
                            |
                            v
                         KDC Time
```

Significant clock skew may cause authentication failures.

On Linux:

```bash
date
```

On Windows:

```powershell
Get-Date
```

Windows time status:

```powershell
w32tm /query /status
```

---

# Ticket Storage on Windows

Windows maintains Kerberos tickets in logon sessions.

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

Different logon sessions may contain different ticket sets.

---

# klist on Windows

Windows provides the native:

```text
klist
```

utility.

Display tickets:

```powershell
klist
```

Typical output may include:

```text
Cached Tickets
Client
Server
KerbTicket Encryption Type
Ticket Flags
Start Time
End Time
Renew Time
```

---

# View the Current TGT

Depending on Windows version and context:

```powershell
klist tgt
```

can display information about the current Ticket Granting Ticket.

Use:

```powershell
klist /?
```

to review the options supported by the system being tested.

---

# Purging Tickets on Windows

Tickets for the current logon session can be removed using:

```powershell
klist purge
```

This should be used carefully because it can disrupt authenticated access within the session.

In a controlled test environment, it can be useful for cleanup or for confirming whether access depends on an existing cached ticket.

---

# Ticket Storage on Linux

Kerberos implementations on Linux commonly use credential caches.

A common format is:

```text
FILE credential cache
```

often represented by:

```text
.ccache
```

files.

Example:

```text
alice.ccache
```

---

# KRB5CCNAME

Kerberos-aware Linux tools commonly use:

```text
KRB5CCNAME
```

to locate the active credential cache.

Example:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Check:

```bash
echo "$KRB5CCNAME"
```

---

# klist on Linux

Display cached Kerberos tickets:

```bash
klist
```

More detailed output may be available with:

```bash
klist -e
```

depending on the Kerberos implementation.

This can help identify:

```text
Principal
Ticket start time
Expiration
Service principal
Encryption type
```

---

# kdestroy

Where supported, Linux Kerberos caches can be destroyed using:

```bash
kdestroy
```

This is useful during controlled cleanup.

Be careful when the current shell or environment depends on Kerberos authentication.

---

# .ccache Files

A `.ccache` file can contain reusable Kerberos credentials.

Therefore:

```text
alice.ccache
     |
     v
Credential
```

Do not treat it as ordinary temporary output.

Protect it like:

```text
Password
NT hash
AES key
Private key
```

---

# .kirbi Files

Windows security tooling frequently represents exported Kerberos tickets using:

```text
.kirbi
```

files.

Conceptually:

```text
Windows Kerberos Ticket
        |
        v
Export
        |
        v
ticket.kirbi
```

A `.kirbi` file may contain reusable authentication material and must be protected accordingly.

---

# .ccache vs .kirbi

A useful distinction is:

```text
.ccache
   |
   +--> Common with Linux / MIT Kerberos / Impacket


.kirbi
   |
   +--> Common with Windows Kerberos tooling
```

The underlying Kerberos ticket concept is the same, but the storage representation differs.

---

# Ticket Conversion

During authorised cross-platform testing, ticket conversion may sometimes be required.

Conceptually:

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

Impacket includes tooling capable of converting between common ticket formats.

---

# Impacket ticketConverter

Check whether it is installed:

```bash
which impacket-ticketConverter
```

Review syntax:

```bash
impacket-ticketConverter -h
```

A general conversion pattern is:

```bash
impacket-ticketConverter input.kirbi output.ccache
```

or:

```bash
impacket-ticketConverter input.ccache output.kirbi
```

Always verify the installed tool's current syntax.

---

# Protect Converted Tickets

Conversion does not reduce ticket sensitivity.

```text
ticket.kirbi
     |
     v
Convert
     |
     v
ticket.ccache
     |
     v
Still a credential
```

Remove temporary copies after authorised testing.

---

# Impacket getTGT

Impacket can request a TGT using valid credential material.

Check:

```bash
impacket-getTGT -h
```

Password-based example:

```bash
impacket-getTGT 'corp.example/alice:<PASSWORD>' -dc-ip 10.10.10.10
```

Hash-based workflows may use:

```bash
impacket-getTGT \
    'corp.example/alice' \
    -hashes ':<NT_HASH>' \
    -dc-ip 10.10.10.10
```

AES-based workflows may use:

```bash
impacket-getTGT \
    'corp.example/alice' \
    -aesKey '<AES_KEY>' \
    -dc-ip 10.10.10.10
```

These produce a ticket cache when authentication succeeds.

---

# Impacket getST

Impacket also provides:

```text
getST.py
```

commonly installed as:

```text
impacket-getST
```

It is used in workflows involving service-ticket acquisition.

Review:

```bash
impacket-getST -h
```

This tool becomes particularly important when studying:

```text
Kerberos delegation
S4U2Self
S4U2Proxy
Constrained Delegation
RBCD
```

---

# Kerberos-Aware Impacket Tools

Many Impacket tools support Kerberos authentication.

Common options include:

```text
-k
-no-pass
```

depending on the tool.

Examples include:

```text
impacket-smbclient
impacket-psexec
impacket-wmiexec
impacket-smbexec
impacket-atexec
impacket-secretsdump
```

Use:

```bash
<tool> -h
```

to verify current options.

---

# Using an Existing Cache

A typical Linux workflow is:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

then:

```bash
klist
```

followed by an authorised Kerberos-aware authentication attempt.

For example:

```bash
impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

---

# Kerberos Authentication Without Plaintext Password

Once a valid ticket exists:

```text
Plaintext Password
        |
        X
Not required for each service
```

Instead:

```text
Ticket Cache
     |
     v
Kerberos Authentication
```

This is expected Kerberos behaviour.

The security problem occurs when an unauthorised party obtains the ticket.

---

# Pass-the-Ticket

Pass-the-Ticket uses an already issued Kerberos ticket.

```text
Existing Ticket
      |
      v
Reuse / Inject
      |
      v
Kerberos Authentication
```

The distinction from Pass-the-Key is:

```text
Pass-the-Key
     |
     v
Key
     |
     v
Request Ticket


Pass-the-Ticket
     |
     v
Ticket already exists
     |
     v
Use Ticket
```

Pass-the-Ticket will be covered separately.

---

# OverPass-the-Hash

OverPass-the-Hash starts with password-derived key material:

```text
NT / RC4 material
       |
       v
Request Kerberos TGT
       |
       v
TGT
```

For detailed coverage:

[OverPass-the-Hash](overpass-the-hash.md)

---

# Pass-the-Key

Pass-the-Key uses suitable Kerberos key material:

```text
RC4
AES128
AES256
```

to obtain Kerberos authentication.

For detailed coverage:

[Pass-the-Key](pass-the-key.md)

---

# Kerberoasting Relationship

Kerberoasting focuses on service tickets.

```text
TGT
 |
 v
Request Service Ticket
 |
 v
TGS-REP
 |
 v
Extract crackable material
 |
 v
Offline password guessing
```

The service ticket is therefore central to Kerberoasting.

For detailed coverage:

[Kerberoasting](kerberoasting.md)

---

# AS-REP Roasting Relationship

AS-REP Roasting occurs earlier in the Kerberos process.

```text
Account without pre-authentication
          |
          v
        AS-REQ
          |
          v
        AS-REP
          |
          v
Offline password guessing
```

For detailed coverage:

[AS-REP Roasting](asrep-roasting.md)

---

# Golden Tickets

A Golden Ticket attack involves forging a TGT using compromised domain Kerberos trust material associated with:

```text
krbtgt
```

Conceptually:

```text
krbtgt Key
    |
    v
Forge TGT
    |
    v
Forged Domain Authentication Material
```

This is substantially different from stealing a legitimate user's TGT.

The root issue is compromise of the domain's Kerberos trust material.

---

# Silver Tickets

A Silver Ticket attack involves forging a service ticket using compromised key material associated with the target service account.

Conceptually:

```text
Service Account Key
        |
        v
Forge Service Ticket
        |
        v
Target Service
```

The key distinction is:

```text
Golden Ticket
     |
     +--> Forged TGT


Silver Ticket
     |
     +--> Forged service ticket
```

---

# Ticket Forgery vs Ticket Theft

Do not confuse:

```text
Ticket Theft
     |
     v
Reuse legitimate ticket
```

with:

```text
Ticket Forgery
     |
     v
Create new ticket using
compromised cryptographic key
```

These represent different security failures.

---

# Delegation

Kerberos delegation allows one service to act on behalf of a user when accessing another service.

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

Delegation is necessary for some legitimate application architectures but can create powerful attack paths when misconfigured.

---

# Unconstrained Delegation

A simplified unconstrained delegation model is:

```text
User
 |
 v
Delegation-Enabled Server
 |
 v
Reusable Kerberos Authentication Material
 |
 v
Backend Services
```

Systems configured for unconstrained delegation require particular attention because high-value users authenticating to them may create dangerous credential exposure.

---

# Constrained Delegation

Constrained delegation limits which backend services can be accessed.

```text
Front-End Service
      |
      +--> CIFS/server01
      |
      +--> HTTP/app01
```

rather than unrestricted delegation.

Kerberos tickets remain central to this process.

---

# Resource-Based Constrained Delegation

Resource-Based Constrained Delegation changes which side controls the delegation relationship.

Conceptually:

```text
Resource
   |
   v
Defines who may act
on behalf of users
```

RBCD attack paths commonly involve:

```text
Computer accounts
SPNs
S4U
Service tickets
```

Understanding ticket behaviour is therefore essential before studying RBCD.

---

# S4U

Kerberos Service-for-User extensions allow services to obtain tickets relating to users under specific delegation conditions.

Two important mechanisms are:

```text
S4U2Self
S4U2Proxy
```

Conceptually:

```text
Service
   |
   v
S4U2Self
   |
   v
Ticket representing user
   |
   v
S4U2Proxy
   |
   v
Backend service ticket
```

These will be covered in the delegation notes.

---

# Ticket Theft

Kerberos tickets may become exposed when attackers obtain sufficient access to systems or authentication sessions.

Potential sources can include:

```text
Compromised endpoint
Compromised server
Credential-access tooling
Ticket export
Improperly protected cache files
Backup or diagnostic artefacts
```

The exact acquisition method should be documented separately from ticket reuse.

---

# Ticket Discovery on Linux

In an authorised Linux environment, check the current Kerberos cache:

```bash
echo "$KRB5CCNAME"
```

Then:

```bash
klist
```

Potential credential caches should only be inspected when included in scope.

---

# Ticket Discovery on Windows

The native starting point is:

```powershell
klist
```

This displays tickets available to the current security context.

This is much less invasive than immediately using credential-dumping tooling.

---

# Windows Logon Sessions

Kerberos tickets are associated with logon sessions.

Conceptually:

```text
Windows
 |
 +--> Logon Session A
 |       |
 |       +--> User A tickets
 |
 +--> Logon Session B
 |       |
 |       +--> User B tickets
 |
 +--> SYSTEM sessions
         |
         +--> Machine/service tickets
```

Access to tickets from other sessions may require elevated privileges and should only be attempted where explicitly authorised.

---

# Machine Account Tickets

Domain-joined computers authenticate using computer accounts such as:

```text
WORKSTATION01$
SERVER01$
DC01$
```

These accounts can possess Kerberos tickets.

Conceptually:

```text
Machine Account
      |
      v
TGT
      |
      v
Service Tickets
```

Machine-account tickets can become important in:

```text
RBCD
AD CS
Kerberos Relay
Delegation
Machine-account abuse
```

---

# Service Account Tickets

Services running under domain identities may also possess Kerberos authentication material.

Examples include:

```text
CORP\svc_sql
CORP\svc_web
CORP\svc_backup
```

The security impact of a compromised ticket depends on the account's privileges.

---

# Ticket Privilege

A ticket does not independently create privilege.

```text
Ticket
   |
   v
Represents Identity
   |
   v
Identity Permissions
```

Therefore:

```text
Low-Privilege User TGT
        |
        X
Domain Admin automatically
```

The ticket grants the rights already available to the represented identity.

---

# PAC

Active Directory Kerberos tickets commonly contain authorisation information in the:

```text
Privilege Attribute Certificate
```

or:

```text
PAC
```

Conceptually, the PAC can contain information related to:

```text
User identity
Group memberships
Security identifiers
Authorisation data
```

The PAC allows Windows services to make authorisation decisions based on the authenticated identity.

---

# PAC Model

A simplified model is:

```text
Kerberos Ticket
      |
      +--> Authentication information
      |
      +--> PAC
              |
              +--> User SID
              +--> Group SIDs
              +--> Authorisation data
```

This relationship becomes particularly important when studying forged tickets.

---

# Authentication vs Authorisation

Kerberos provides authentication:

```text
Who are you?
```

The target service then performs authorisation:

```text
What are you allowed to do?
```

Therefore:

```text
Valid Ticket
     |
     v
Authentication Success
     |
     v
Authorisation Check
     |
 +---+---+
 |       |
 v       v
Allow   Deny
```

---

# Ticket Cache Security

Credential caches should be protected from unauthorised access.

Linux:

```text
.ccache
```

Windows/security tooling:

```text
.kirbi
```

Both can represent reusable authentication material.

---

# Do Not Store Tickets in Git

Never run:

```bash
git add alice.ccache
```

or:

```bash
git add ticket.kirbi
```

against real assessment credentials.

Ticket files should be excluded from source repositories.

A defensive `.gitignore` for an assessment workspace might include:

```text
*.ccache
*.kirbi
```

Only add this where it matches the repository's intended workflow.

---

# Ticket Handling

Treat Kerberos tickets like passwords.

```text
Ticket obtained
      |
      v
Store securely
      |
      v
Use only within scope
      |
      v
Collect minimum evidence
      |
      v
Remove unnecessary copies
```

---

# Ticket Expiration

A stolen ticket is normally useful only while valid.

```text
Ticket stolen
     |
     v
Valid
     |
     v
Potential reuse
     |
     v
Expires
```

However, attackers with access to the underlying long-term credential material may be able to request new tickets.

This distinction matters during incident response.

---

# Ticket vs Key Compromise

Ticket compromise:

```text
Ticket
 |
 v
Temporary authentication material
```

Key compromise:

```text
Long-Term Key
      |
      v
Potentially request new tickets
```

Therefore:

```text
Key compromise
```

can have a longer-lasting impact than theft of a single expiring ticket.

---

# Password Changes

Changing a user's password changes password-derived key material.

However, previously issued tickets may not disappear immediately.

Conceptually:

```text
Password A
   |
   v
TGT A
   |
   v
Password changed to B
   |
   v
New key material
```

but:

```text
TGT A
```

may remain relevant until expiration or other invalidation conditions.

---

# krbtgt Password Changes

The `krbtgt` account requires special incident-response handling.

Because Kerberos supports current and previous key material for operational reasons, recovery from `krbtgt` compromise traditionally involves carefully planned password resets rather than an arbitrary single reset.

Follow current Microsoft incident-response guidance for the environment.

Do not reset `krbtgt` casually during an assessment.

---

# Cross-Domain Kerberos

Kerberos also supports authentication across Active Directory trust relationships.

A simplified model is:

```text
User in Domain A
       |
       v
Domain A KDC
       |
       v
Trust Referral
       |
       v
Domain B KDC
       |
       v
Service in Domain B
```

This introduces:

```text
Referral tickets
Trust keys
Inter-realm authentication
```

These topics belong in the trust notes.

---

# Referral Tickets

When accessing services across domain boundaries, the client may receive Kerberos referral tickets.

Conceptually:

```text
Domain A TGT
     |
     v
Request service in Domain B
     |
     v
Referral
     |
     v
Domain B
```

Understanding referrals is important when analysing multi-domain environments.

---

# Kerberos and DNS

Kerberos failures frequently originate from DNS problems.

A useful model is:

```text
Kerberos failure
      |
      +--> Credential?
      |
      +--> DNS?
      |
      +--> Time?
      |
      +--> SPN?
      |
      +--> Realm?
      |
      +--> KDC?
```

Always validate infrastructure before assuming authentication material is invalid.

---

# Kerberos and IP Addresses

Using:

```text
10.10.10.25
```

instead of:

```text
server01.corp.example
```

can interfere with Kerberos authentication.

The client typically needs an SPN such as:

```text
cifs/server01.corp.example
```

not:

```text
cifs/10.10.10.25
```

unless such an SPN is explicitly configured.

---

# Kerberos and NTLM Fallback

Windows applications may use:

```text
Negotiate
```

which can select between Kerberos and NTLM.

Conceptually:

```text
Negotiate
   |
   +--> Kerberos available
   |       |
   |       v
   |    Kerberos
   |
   +--> Kerberos unavailable
           |
           v
          NTLM
```

This can make troubleshooting confusing.

A successful authentication does not automatically prove Kerberos was used.

---

# Verify the Authentication Protocol

Do not assume:

```text
Domain authentication
       =
Kerberos
```

Verify using:

```text
Windows event logs
klist
Packet capture
Service telemetry
```

where appropriate.

---

# Wireshark

Kerberos traffic can be inspected using Wireshark.

Useful display filter:

```text
kerberos
```

You may observe:

```text
AS-REQ
AS-REP
TGS-REQ
TGS-REP
KRB-ERROR
```

Packet capture should only be performed where network monitoring is authorised.

---

# KRB-ERROR

Kerberos failures may produce:

```text
KRB-ERROR
```

messages.

These can provide valuable troubleshooting information.

Possible causes include:

```text
Unknown principal
Incorrect pre-authentication
Clock skew
Unsupported encryption
Expired credentials
Incorrect SPN
Policy restrictions
```

---

# Common Kerberos Errors

Examples frequently encountered during testing include:

```text
KDC_ERR_PREAUTH_FAILED
KDC_ERR_C_PRINCIPAL_UNKNOWN
KDC_ERR_S_PRINCIPAL_UNKNOWN
KDC_ERR_ETYPE_NOSUPP
KRB_AP_ERR_SKEW
KRB_AP_ERR_TKT_EXPIRED
```

Interpret them in context rather than repeatedly changing credentials or commands.

---

# KDC_ERR_PREAUTH_FAILED

Often indicates that Kerberos pre-authentication could not be validated.

Potential causes:

```text
Incorrect password
Incorrect NT/RC4 key
Incorrect AES key
Stale credential material
Account changes
```

---

# KDC_ERR_C_PRINCIPAL_UNKNOWN

This generally relates to the client principal not being found.

Check:

```text
Username
Domain
Realm
Account existence
```

---

# KDC_ERR_S_PRINCIPAL_UNKNOWN

This generally relates to the requested service principal.

Check:

```text
SPN
Hostname
Service
DNS
```

---

# KDC_ERR_ETYPE_NOSUPP

This indicates an encryption-type compatibility problem.

Review:

```text
Client-supported encryption
Account-supported encryption
Domain policy
Service configuration
```

---

# KRB_AP_ERR_SKEW

This relates to clock skew.

Check:

```bash
date
```

and on Windows:

```powershell
w32tm /query /status
```

---

# Expired Tickets

An expired ticket cannot normally be used for authentication.

Check:

```bash
klist
```

Review:

```text
Start Time
End Time
Renew Until
```

before troubleshooting more complicated causes.

---

# Detection

Kerberos provides valuable domain-controller telemetry.

Important events include:

```text
4768 - Kerberos authentication ticket requested
4769 - Kerberos service ticket requested
4770 - Kerberos service ticket renewed
4771 - Kerberos pre-authentication failed
4772 - Kerberos authentication ticket request failed
```

Availability and detail depend on auditing configuration and Windows version.

---

# Event 4768

Event `4768` records a request for a Kerberos TGT.

Conceptually:

```text
Client
 |
 | AS-REQ
 v
Domain Controller
 |
 +--> 4768
```

Useful context can include:

```text
Account
Client address
Service
Ticket options
Encryption type
Pre-authentication information
Result
```

---

# Event 4769

Event `4769` records a Kerberos service-ticket request.

```text
Client with TGT
      |
      | TGS-REQ
      v
Domain Controller
      |
      +--> 4769
```

This can help identify which services an account is accessing.

---

# Event 4770

Event `4770` relates to Kerberos service-ticket renewal.

Ticket renewal activity should be interpreted within the normal behaviour of the account and system.

---

# Event 4771

Event `4771` records Kerberos pre-authentication failures.

Potential causes include:

```text
Incorrect password
Incorrect key
Password spraying
Stale credentials
Misconfiguration
Testing
```

Repeated failures across multiple accounts can be particularly useful for detecting password spraying.

---

# Event 4624

Successful authentication to a Windows target may generate:

```text
4624
```

Correlate target logon events with domain-controller Kerberos events.

```text
4768
 |
 v
4769
 |
 v
4624
```

This provides a broader view of the authentication path.

---

# Event 4672

Privileged Windows logons may also generate:

```text
4672
```

Correlate:

```text
4624
 +
4672
```

where appropriate.

---

# Kerberos Detection Model

```text
AS-REQ
  |
  v
4768
  |
  v
TGT
  |
  v
TGS-REQ
  |
  v
4769
  |
  v
Service Ticket
  |
  v
Target Logon
  |
  v
4624
  |
  v
Potential Privileged Logon
  |
  v
4672
```

---

# Detecting Ticket Abuse

Ticket abuse can resemble legitimate Kerberos activity.

Detection should therefore consider:

```text
Account
   |
   v
Source Host
   |
   v
Ticket Type
   |
   v
Encryption Type
   |
   v
Requested Service
   |
   v
Target Host
   |
   v
Subsequent Behaviour
```

---

# Source Baselines

A high-value account might normally authenticate only from:

```text
PAW01
MGMT01
```

A TGT request from:

```text
EMPLOYEE-LAPTOP-37
```

could therefore deserve investigation.

The unusual relationship matters more than the existence of a normal Kerberos ticket.

---

# Ticket Encryption Monitoring

Monitor for unexpected changes such as:

```text
Account normally uses AES
          |
          v
Unexpected RC4 tickets
```

However:

```text
RC4
 |
 X
Proof of malicious activity
```

Compatibility requirements can legitimately produce RC4 tickets.

---

# Ticket Lifetime Anomalies

Forged or unusual tickets may contain suspicious lifetime properties.

Detection can consider:

```text
Unusual start time
Unusual expiration
Unexpected renew period
Unexpected flags
Unexpected identity information
```

Do not rely on one field alone.

---

# Service Access Patterns

Service-ticket activity can reveal unusual movement.

Example:

```text
User normally:
HTTP/intranet
CIFS/home-directory
```

suddenly requests:

```text
CIFS/DC01
LDAP/DC01
HOST/ADMIN01
```

This may deserve investigation depending on the account and environment.

---

# Purple Team Validation

Kerberos ticket monitoring can be validated using a controlled account.

Example:

```text
PT-KerberosUser
      |
      v
Normal TGT request
      |
      v
4768
      |
      v
Controlled CIFS ticket
      |
      v
4769
      |
      v
Test Server
      |
      v
4624
```

The exercise should focus on visibility and interpretation rather than destructive impact.

---

# Purple Team Questions

The blue team should determine:

```text
Who requested the TGT?

Which system generated the request?

Which encryption type was used?

Which service ticket was requested?

Which SPN was involved?

Which target received the authentication?

Was the source expected?

Was the ticket activity normal for the account?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect
Time to triage
Account identified?
Source identified?
TGT identified?
Service ticket identified?
SPN identified?
Target identified?
Encryption type identified?
Authentication path reconstructed?
```

---

# Hardening

Kerberos ticket security requires protecting both long-term credentials and issued authentication material.

```text
Kerberos Security
      |
      +--> Protect account keys
      |
      +--> Protect tickets
      |
      +--> Protect privileged sessions
      |
      +--> Use modern encryption
      |
      +--> Restrict delegation
      |
      +--> Apply least privilege
      |
      +--> Restrict privileged logons
      |
      +--> Monitor KDC activity
```

---

# Credential Guard

Windows Defender Credential Guard can help reduce exposure of reusable credential material.

It is particularly relevant to preventing attackers from obtaining sensitive authentication secrets from compromised endpoints.

Deploy where supported and operationally appropriate.

---

# LSA Protection

Additional LSA protection can make unauthorised access to LSASS more difficult.

This complements:

```text
Credential Guard
EDR
Administrative tiering
Least privilege
Privileged access workstations
```

---

# Protect Privileged Sessions

Avoid placing high-value authentication material on low-trust endpoints.

Bad:

```text
Domain Admin
    |
    v
Ordinary User Workstation
    |
    v
Privileged Kerberos Tickets
```

Better:

```text
Privileged Account
      |
      v
Dedicated Administrative System
      |
      v
Privileged Resources
```

---

# Administrative Tiering

Separate administrative identities and systems according to privilege level.

The goal is to prevent:

```text
Tier 0 Credential
      |
      v
Tier 2 Workstation
```

from becoming a routine authentication path.

---

# Protected Users

The Active Directory Protected Users security group provides additional protections for suitable high-value accounts.

Compatibility should be tested before deployment.

---

# Restrict Delegation

Review systems configured for:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

Delegation should exist only where operationally required.

---

# Prefer AES

Where compatibility permits:

```text
RC4
 |
 v
Reduce
 |
 v
AES
```

This improves Kerberos cryptographic security.

However, credential and ticket protection remain necessary.

---

# Least Privilege

Kerberos tickets represent the privileges of their identities.

Reducing account privileges therefore reduces the impact of stolen tickets.

Review:

```text
Domain groups
Local administrator rights
Delegated AD permissions
Remote logon rights
Application permissions
Service permissions
```

---

# Network Segmentation

Restrict access to sensitive services from ordinary user networks.

For example:

```text
User Workstation
      |
      X
Direct management access
      |
      v
Domain Controller
```

This limits the usefulness of stolen tickets for lateral movement.

---

# Incident Response

When Kerberos ticket theft or abuse is suspected:

```text
Identify Account
      |
      v
Identify Source Host
      |
      v
Determine Ticket Type
      |
      v
Review 4768
      |
      v
Review 4769
      |
      v
Identify Target Services
      |
      v
Review Target Logons
      |
      v
Contain Source
      |
      v
Determine Credential Exposure
      |
      v
Rotate Credentials if Required
      |
      v
Review Existing Sessions/Tickets
```

---

# Determine What Was Compromised

This distinction is critical during response.

```text
Only Ticket Stolen?
       |
       +--> Temporary ticket exposure


Long-Term Key Stolen?
       |
       +--> New tickets may potentially
            be requested
```

The remediation strategy differs.

---

# Reporting

Possible finding titles include:

```text
Kerberos Ticket Exposure Enables Authentication as Another User
```

```text
Reusable Kerberos Ticket Material Exposed on Endpoint
```

```text
Compromised Kerberos Ticket Enables Unauthorised Service Access
```

```text
Privileged Kerberos Authentication Material Exposed
```

The title should describe the actual root cause and demonstrated impact.

---

# Avoid Overstatement

Do not report:

```text
Kerberos tickets exist
      =
Vulnerability
```

Tickets are a normal part of Kerberos.

The meaningful security issue is:

```text
Ticket accessible to unauthorised party
        |
        +
Ticket reusable
        |
        +
Identity has useful access
```

---

# Example Finding

```text
Finding:
Reusable Kerberos Ticket Material Exposed on Endpoint

Affected Account:
CORP\adminuser

Validation:
During the authorised assessment, reusable Kerberos authentication
material associated with the affected account was accessible from the
compromised test system.

The ticket was used only against the authorised test service to confirm
that it represented valid authentication material.

Impact:
An attacker capable of obtaining the ticket may authenticate as the
represented account for the lifetime and scope of the ticket without
knowing the account's plaintext password.

The resulting impact depends on the privileges assigned to the affected
identity and the services accessible using the ticket.

Recommendation:
Prevent privileged accounts from authenticating to lower-trust systems,
strengthen credential and session isolation, deploy credential-protection
controls where appropriate, restrict administrative access paths, and
investigate the original mechanism through which the authentication
material became exposed.
```

---

# Evidence Collection

Record:

```text
Account
Domain
Source Host
Ticket Type
TGT / Service Ticket
Service Principal
Ticket Start Time
Ticket End Time
Renew Time
Encryption Type
Ticket Flags
Target Host
Target Service
Authentication Result
Privilege Level
Relevant Event IDs
Tool
Command
```

---

# Ticket Redaction

Do not include reusable ticket data in reports.

Prefer:

```text
Ticket:
[REDACTED]
```

Do not publish:

```text
Base64 ticket blobs
.ccache files
.kirbi files
Session keys
```

unless there is an explicit secure evidence-handling requirement.

---

# Cleanup

After Linux ticket testing:

```bash
unset KRB5CCNAME
```

Where appropriate:

```bash
kdestroy
```

or securely remove temporary test caches:

```bash
rm -f alice.ccache
```

On a dedicated Windows test session, ticket cleanup may involve:

```powershell
klist purge
```

Be aware that purging tickets can disrupt the current session.

---

# Common Mistakes

## Mistake 1 - Confusing TGT and Service Ticket

Remember:

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

## Mistake 2 - Treating Tickets as Harmless Files

```text
.ccache
.kirbi
```

may be reusable credentials.

Protect them.

---

## Mistake 3 - Assuming Every Domain Logon Uses Kerberos

Windows may fall back to NTLM.

Verify the authentication protocol.

---

## Mistake 4 - Using IP Addresses

Kerberos normally expects service names associated with SPNs.

Prefer correct hostnames.

---

## Mistake 5 - Ignoring DNS

Many apparent Kerberos problems are actually DNS or hostname problems.

---

## Mistake 6 - Ignoring Time

Kerberos is time-sensitive.

Check clock synchronisation early.

---

## Mistake 7 - Assuming a Valid Ticket Means Administrator

Tickets represent identities.

Privileges come from the represented account.

---

## Mistake 8 - Confusing Ticket Theft with Ticket Forgery

```text
Ticket Theft
     =
Steal existing ticket


Ticket Forgery
     =
Create ticket using compromised key
```

---

## Mistake 9 - Confusing Key Theft with Ticket Theft

```text
Key
 |
 v
Can potentially request new tickets


Ticket
 |
 v
Existing authentication material
```

---

## Mistake 10 - Testing Remote Execution Too Early

First determine whether ticket-based authentication itself proves the finding.

Use the minimum necessary validation.

---

# Assessment Checklist

## Environment

- [ ] Confirm Kerberos testing is authorised
- [ ] Identify domain
- [ ] Identify realm
- [ ] Identify domain controller
- [ ] Confirm DNS
- [ ] Confirm time synchronisation
- [ ] Confirm TCP/UDP 88 where relevant

## Ticket Enumeration

- [ ] Identify current principal
- [ ] Enumerate current tickets
- [ ] Distinguish TGT from service tickets
- [ ] Identify service principals
- [ ] Record encryption types
- [ ] Record ticket flags
- [ ] Record expiration times
- [ ] Identify renewable tickets

## Windows

- [ ] Review `klist`
- [ ] Identify current TGT
- [ ] Identify cached service tickets
- [ ] Determine relevant logon session
- [ ] Avoid accessing unrelated sessions without authorisation

## Linux

- [ ] Check `KRB5CCNAME`
- [ ] Run `klist`
- [ ] Identify `.ccache` files relevant to scope
- [ ] Protect ticket caches
- [ ] Verify ticket expiration
- [ ] Remove temporary caches after testing

## Authentication

- [ ] Use correct hostname
- [ ] Identify SPN
- [ ] Use minimum required service
- [ ] Verify Kerberos rather than NTLM fallback
- [ ] Record authentication result
- [ ] Avoid unnecessary execution

## Detection

- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4770 where relevant
- [ ] Review 4771 where relevant
- [ ] Review 4624
- [ ] Review 4672 where relevant
- [ ] Correlate source host
- [ ] Correlate target service
- [ ] Review encryption type
- [ ] Compare against normal account behaviour

## Remediation

- [ ] Identify ticket-exposure root cause
- [ ] Determine whether long-term keys were also compromised
- [ ] Protect privileged sessions
- [ ] Deploy Credential Guard where appropriate
- [ ] Enable LSA protection where appropriate
- [ ] Restrict privileged logons
- [ ] Review delegation
- [ ] Apply least privilege
- [ ] Prefer modern Kerberos encryption
- [ ] Segment administrative services

## Cleanup

- [ ] Remove temporary `.ccache`
- [ ] Remove temporary `.kirbi`
- [ ] Clear unnecessary `KRB5CCNAME`
- [ ] Purge dedicated test-session tickets if required
- [ ] Secure retained evidence
- [ ] Redact ticket material
- [ ] Follow evidence-retention requirements

---

# Kerberos Ticket Testing Model

A useful overall model is:

```text
                         Active Directory
                               |
                               v
                              KDC
                               |
                +--------------+--------------+
                |                             |
                v                             v
        Authentication Service       Ticket Granting Service
                |                             |
                | AS-REQ                      | TGS-REQ
                v                             v
              AS-REP                        TGS-REP
                |                             |
                v                             v
               TGT                     Service Ticket
                |                             |
                +-------------+---------------+
                              |
                              v
                       Target Service
                              |
                              v
                       Authentication
                              |
                              v
                        Authorisation
```

The ticket hierarchy is:

```text
Long-Term Credential
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
        +--> HOST Ticket
        |
        +--> MSSQLSvc Ticket
```

The credential-reuse model is:

```text
                     Authentication Material
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
     NT Hash             Kerberos Key         Kerberos Ticket
        |                     |                     |
        v                     v                     v
 Pass-the-Hash          Pass-the-Key          Pass-the-Ticket
        |                     |                     |
        v                     v                     v
      NTLM                  Kerberos              Kerberos
```

The ticket attack model is:

```text
Kerberos Tickets
      |
      +--> Legitimate Use
      |
      +--> Ticket Theft
      |       |
      |       +--> Pass-the-Ticket
      |
      +--> Ticket Acquisition Abuse
      |       |
      |       +--> Kerberoasting
      |       +--> Delegation Abuse
      |
      +--> Ticket Forgery
              |
              +--> Golden Ticket
              +--> Silver Ticket
```

The defensive model is:

```text
Kerberos Ticket Security
          |
          +--> Protect Long-Term Keys
          |
          +--> Protect Ticket Caches
          |
          +--> Isolate Privileged Sessions
          |
          +--> Credential Guard
          |
          +--> LSA Protection
          |
          +--> Restrict Delegation
          |
          +--> Least Privilege
          |
          +--> Network Segmentation
          |
          +--> Monitor
                  |
                  +--> 4768
                  +--> 4769
                  +--> 4770
                  +--> 4771
                  +--> 4624
```

The assessment should answer:

```text
Which identity owns the ticket?
        |
        v
Is it a TGT or service ticket?
        |
        v
Which service does it represent?
        |
        v
When does it expire?
        |
        v
Which encryption type is used?
        |
        v
Where was the ticket obtained?
        |
        v
Can an unauthorised party access it?
        |
        v
Can it authenticate to an authorised target?
        |
        v
What privileges does the identity have?
        |
        v
Can defenders reconstruct the ticket activity?
        |
        v
Was only the ticket compromised,
or was the long-term key also exposed?
        |
        v
Which control breaks the attack path?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Password Spraying:

[Password Spraying](password-spraying.md)

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

BloodHound:

[BloodHound](bloodhound.md)

The following pages complement Kerberos Tickets and can be linked once their dedicated notes are available:

```text
active-directory/pass-the-ticket.md
active-directory/unconstrained-delegation.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
active-directory/golden-ticket.md
active-directory/silver-ticket.md
active-directory/trust-tickets.md
active-directory/kerberos-relay.md
```

---

# References

## Microsoft Kerberos

[Microsoft - Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos protocol documentation](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos supported encryption types](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-supported-encryption-types){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos policy](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/jj852180(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Event Auditing

[Microsoft - Event 4768](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4769](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4771](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4771){ target="_blank" rel="noopener noreferrer" }

---

## Credential Protection

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Configure added LSA protection](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Use Alternate Authentication Material](https://attack.mitre.org/techniques/T1550/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket getTGT](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

[Impacket getST](https://github.com/fortra/impacket/blob/master/examples/getST.py){ target="_blank" rel="noopener noreferrer" }

[Impacket ticketConverter](https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Kerberos tickets are temporary authentication credentials that form the foundation of Active Directory Kerberos authentication.

The normal authentication chain is:

```text
Password / Key
      |
      v
AS-REQ
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
      v
TGS-REP
      |
      v
Service Ticket
      |
      v
Target Service
```

The most important distinction is:

```text
TGT
 |
 v
Used to request service tickets


Service Ticket
 |
 v
Used to authenticate to a specific service
```

From an offensive-security perspective:

```text
Credential Key
      |
      +--> Request new tickets
      |
      v
Pass-the-Key / OverPass-the-Hash


Existing Ticket
      |
      v
Pass-the-Ticket


krbtgt Key
      |
      v
Golden Ticket


Service Key
      |
      v
Silver Ticket
```

From a defensive perspective:

```text
Kerberos Security
      |
      +--> Protect passwords and keys
      |
      +--> Protect ticket caches
      |
      +--> Protect privileged sessions
      |
      +--> Restrict delegation
      |
      +--> Restrict privileged logons
      |
      +--> Apply least privilege
      |
      +--> Monitor 4768 / 4769
      |
      +--> Correlate target logons
```

A mature Kerberos assessment should not merely determine whether tickets can be obtained. It should identify which identity each ticket represents, distinguish TGTs from service tickets, determine how the ticket was obtained, establish whether an unauthorised party can reuse it, identify the resulting access and privileges, determine whether long-term credential material was also exposed, reconstruct the corresponding domain-controller and target telemetry, and identify the control that most effectively breaks the authentication-abuse path.
