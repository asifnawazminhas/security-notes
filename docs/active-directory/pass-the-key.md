# Pass-the-Key

Pass-the-Key is an Active Directory authentication technique in which an attacker uses a user's **Kerberos cryptographic key** directly instead of knowing or supplying the plaintext password.

Depending on the account and domain configuration, the reusable key material may include:

```text
RC4 / NT key
AES128 key
AES256 key
```

The fundamental concept is:

```text
Plaintext Password
        |
        v
Kerberos Key Derivation
        |
        v
Cryptographic Key
        |
        v
Kerberos Authentication
```

If the cryptographic key has already been obtained:

```text
Plaintext Password
        |
        X
Not required

Kerberos Key
        |
        v
Kerberos Authentication
```

Pass-the-Key therefore demonstrates an important Active Directory security principle:

> Kerberos keys are credentials.

An attacker does not necessarily need to recover the user's plaintext password if reusable Kerberos key material has already been compromised.

!!! warning "Authorised testing only"
    Kerberos keys provide reusable authentication material and must be treated like passwords and NT hashes. Only perform Pass-the-Key testing against accounts, domains, and systems explicitly included in the assessment scope. Use the minimum validation required to demonstrate impact and securely remove collected tickets and keys after testing.

---

# Pass-the-Key at a Glance

A typical workflow is:

```text
Credential Exposure
        |
        v
Kerberos Key Obtained
        |
   +----+-----+
   |          |
   v          v
 RC4         AES
   |       +--+--+
   |       |     |
   |       v     v
   |     AES128 AES256
   |       |     |
   +-------+-----+
           |
           v
    Identify Account
           |
           v
    Identify Domain
           |
           v
      Contact KDC
           |
           v
       Request TGT
           |
      +----+----+
      |         |
      v         v
    Failed    Success
                |
                v
               TGT
                |
                v
       Request Service Ticket
                |
                v
       Authenticate to Service
                |
                v
        Privilege Analysis
                |
                v
        Minimum Validation
```

---

# Kerberos Refresher

Kerberos is the primary authentication protocol used by modern Active Directory environments.

A simplified authentication process is:

```text
User
 |
 | Credentials
 v
Kerberos Client
 |
 | AS-REQ
 v
KDC
 |
 | AS-REP
 v
Ticket Granting Ticket
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

The Key Distribution Center normally runs on domain controllers.

The KDC provides two logical services:

```text
Authentication Service
        |
        +--> Issues TGTs

Ticket Granting Service
        |
        +--> Issues service tickets
```

For detailed Kerberos coverage, see:

[Kerberos](kerberos.md)

---

# Normal Kerberos Authentication

Normally:

```text
Username
   +
Password
   |
   v
Kerberos Client
   |
   v
Derive Kerberos Key
   |
   v
Pre-authentication
   |
   v
KDC
   |
   v
TGT
```

The password is used to derive cryptographic key material.

The KDC does not need the user's plaintext password to perform Kerberos authentication.

---

# Pass-the-Key Authentication

Pass-the-Key starts later in this process.

```text
Password
   |
   X

Key already known
   |
   v
Kerberos Client
   |
   v
Pre-authentication
   |
   v
KDC
   |
   v
TGT
```

Therefore:

```text
Password
   =
Source of key material


Kerberos Key
   =
Actual cryptographic credential
```

---

# Why Pass-the-Key Works

Kerberos authentication is based on cryptographic proof that the client possesses the correct key.

Conceptually:

```text
User
 |
 | possesses key
 v
Encrypted authentication data
 |
 v
KDC
 |
 | validates using account key
 v
Authentication succeeds
```

If an attacker obtains the same key:

```text
Attacker
 |
 | possesses key
 v
Can potentially generate
valid Kerberos authentication
```

The KDC cannot determine whether the cryptographic operation was performed using:

```text
A key derived from the user's password
```

or:

```text
A previously stolen copy of that key
```

if both produce valid protocol messages.

---

# Kerberos Key Types

Active Directory may maintain multiple Kerberos keys for an account.

Common examples include:

```text
RC4
AES128
AES256
```

These correspond to different Kerberos encryption types.

A useful model is:

```text
                 Account Password
                       |
          +------------+------------+
          |                         |
          v                         v
       NT Hash                  AES Keys
          |                  +------+------+
          |                  |             |
          v                  v             v
      RC4-HMAC             AES128        AES256
```

The exact keys available depend on:

- domain configuration
- account configuration
- operating system support
- password history/state
- supported encryption types

---

# NT Hash and RC4

In traditional Active Directory environments, the account's NT hash is also related to the key material used for RC4-HMAC Kerberos authentication.

Conceptually:

```text
Password
   |
   v
NT Hash
   |
   +--> NTLM authentication
   |
   +--> RC4 Kerberos key material
```

This relationship explains the overlap between:

```text
Pass-the-Hash
```

and:

```text
OverPass-the-Hash
```

---

# AES128

Modern Active Directory environments can use AES128 Kerberos keys.

Conceptually:

```text
Password
   |
   v
Kerberos key derivation
   |
   v
AES128 key
```

The AES128 key is reusable authentication material.

It should therefore be treated as a credential.

---

# AES256

AES256 is generally preferred over older RC4-based Kerberos encryption where supported.

Conceptually:

```text
Password
   |
   v
Kerberos key derivation
   |
   v
AES256 key
```

However:

```text
AES256
   |
   X
Protection against stolen AES256 key
```

A stronger encryption algorithm does not make a stolen key unusable.

---

# Strong Encryption vs Credential Theft

This distinction is important.

AES protects Kerberos cryptography.

It does not solve credential theft.

```text
Weak Encryption
      |
      v
Cryptographic risk


Strong Encryption
      |
      v
Improved cryptographic security
```

but:

```text
Strong Encryption
      +
Stolen Key
      |
      v
Credential compromise remains
```

---

# Pass-the-Key vs Pass-the-Hash

Traditional Pass-the-Hash uses an NT hash through NTLM.

```text
NT Hash
   |
   v
NTLM
   |
   v
Remote Authentication
```

Pass-the-Key uses suitable cryptographic key material through Kerberos.

```text
Kerberos Key
     |
     v
Kerberos
     |
     v
TGT
     |
     v
Service Ticket
```

Comparison:

| Technique | Credential Material | Authentication Protocol |
|---|---|---|
| Pass-the-Hash | NT hash | NTLM |
| Pass-the-Key | Kerberos key | Kerberos |

For detailed Pass-the-Hash coverage, see:

[Pass-the-Hash](pass-the-hash.md)

---

# Pass-the-Key vs OverPass-the-Hash

These terms overlap substantially.

Historically:

```text
OverPass-the-Hash
        |
        v
Use NT hash
        |
        v
Obtain Kerberos authentication
```

Pass-the-Key can be treated as the broader concept:

```text
Pass-the-Key
      |
      +--> RC4 / NT key
      |
      +--> AES128
      |
      +--> AES256
```

Therefore:

```text
OverPass-the-Hash
       |
       v
Special case / closely related
Pass-the-Key workflow
```

Terminology varies between tools and security literature.

In reporting, describe exactly what was used.

For example:

```text
The AES256 Kerberos key associated with the authorised test account
was used to request a Kerberos Ticket Granting Ticket without supplying
the account's plaintext password.
```

For detailed coverage, see:

[OverPass-the-Hash](overpass-the-hash.md)

---

# Pass-the-Key vs Pass-the-Ticket

These techniques begin with different credential material.

Pass-the-Key:

```text
Kerberos Key
     |
     v
Request Ticket
     |
     v
TGT
```

Pass-the-Ticket:

```text
Existing Ticket
      |
      v
Use Ticket
      |
      v
Authentication
```

The distinction is:

```text
Pass-the-Key
     =
Key -> Ticket


Pass-the-Ticket
     =
Ticket -> Authentication
```

---

# Pass-the-Key vs Kerberoasting

Kerberoasting attempts to recover a service account password from Kerberos service-ticket material.

```text
Service Ticket
      |
      v
Offline Password Guessing
      |
      v
Potential Password
```

Pass-the-Key begins with already compromised credential material:

```text
Kerberos Key
      |
      v
Authentication
```

Therefore:

```text
Kerberoasting
     =
Credential acquisition


Pass-the-Key
     =
Credential use
```

---

# Pass-the-Key vs AS-REP Roasting

AS-REP Roasting:

```text
Account without Kerberos pre-authentication
              |
              v
            AS-REP
              |
              v
       Offline guessing
```

Pass-the-Key:

```text
Known Kerberos key
       |
       v
Kerberos authentication
```

Again, one attempts credential recovery while the other uses already obtained credential material.

---

# Credential Material Overview

During Active Directory assessments, several credential forms may appear:

```text
Plaintext Password
       |
       +--> NT hash
       |
       +--> Kerberos keys


NT Hash
       |
       +--> Pass-the-Hash
       |
       +--> RC4-related Kerberos workflows


AES128 Key
       |
       +--> Kerberos authentication


AES256 Key
       |
       +--> Kerberos authentication


Kerberos Ticket
       |
       +--> Pass-the-Ticket


NetNTLMv2
       |
       +--> Offline password guessing
       |
       +--> Relay when conditions permit
```

Do not treat these credential forms as interchangeable.

---

# Pass-the-Key Requirements

Typical requirements include:

```text
Valid Kerberos key
        |
        +
Username
        |
        +
Domain
        |
        +
Reachable KDC
        |
        +
Correct DNS
        |
        +
Correct time
```

---

# Identify the Account

Before using any key, determine which account it belongs to.

For example:

```text
CORP\alice
```

or:

```text
alice@corp.example
```

A cryptographic key without correct identity context is not sufficient.

---

# Identify the Domain

Determine:

```text
DNS Domain
NetBIOS Domain
Kerberos Realm
```

Example:

```text
DNS Domain:
corp.example

NetBIOS:
CORP

Kerberos Realm:
CORP.EXAMPLE
```

Different tools may require different forms.

---

# Identify the Domain Controller

Useful discovery methods may include:

```bash
nslookup -type=SRV _kerberos._tcp.corp.example
```

or:

```bash
dig _kerberos._tcp.corp.example SRV
```

A typical result identifies domain controllers offering Kerberos.

---

# Kerberos Port

Kerberos commonly uses:

```text
TCP/88
UDP/88
```

Check basic reachability:

```bash
nc -vz dc01.corp.example 88
```

---

# DNS

Correct DNS is particularly important for Kerberos.

Check:

```bash
getent hosts dc01.corp.example
```

and:

```bash
getent hosts server01.corp.example
```

Kerberos authentication frequently fails when:

```text
DNS
SPN
Hostname
Realm
```

do not align.

---

# Time Synchronisation

Kerberos has clock-skew protections.

Check:

```bash
date
```

If troubleshooting a lab or authorised environment, compare the assessment host's time with the domain controller.

A useful troubleshooting sequence is:

```text
Credential correct?
      |
      v
Domain correct?
      |
      v
DNS correct?
      |
      v
Time correct?
      |
      v
KDC reachable?
      |
      v
Encryption type supported?
```

---

# Impacket

Impacket provides several Kerberos-aware utilities.

For Pass-the-Key testing, one of the most useful is:

```text
getTGT.py
```

which is commonly installed as:

```text
impacket-getTGT
```

Check:

```bash
impacket-getTGT -h
```

For detailed Impacket coverage, see:

[Impacket](impacket.md)

---

# Request a TGT with an AES Key

A general authorised testing pattern is:

```bash
impacket-getTGT \
    'corp.example/alice' \
    -aesKey '<AES_KEY>' \
    -dc-ip 10.10.10.10
```

Conceptually:

```text
AES Key
   |
   v
getTGT
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
```

If successful, a credential-cache file is commonly created.

Example:

```text
alice.ccache
```

---

# Request a TGT with NT/RC4 Material

For credential material represented by an NT hash, Impacket supports hash-based authentication where applicable.

A common pattern is:

```bash
impacket-getTGT \
    'corp.example/alice' \
    -hashes ':<NT_HASH>' \
    -dc-ip 10.10.10.10
```

This workflow overlaps with OverPass-the-Hash.

---

# Use Current Tool Help

Authentication syntax can evolve between releases.

Always check:

```bash
impacket-getTGT -h
```

before relying on copied commands.

The same applies to other Impacket tools:

```bash
impacket-smbclient -h
impacket-psexec -h
impacket-wmiexec -h
```

---

# Kerberos Credential Cache

Impacket commonly writes Kerberos tickets to:

```text
.ccache
```

files.

Example:

```text
alice.ccache
```

This file is reusable credential material.

Protect it accordingly.

---

# KRB5CCNAME

Linux Kerberos-aware tools commonly use:

```text
KRB5CCNAME
```

to identify the active ticket cache.

Set:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Check:

```bash
echo "$KRB5CCNAME"
```

---

# Inspect the Ticket

If Kerberos client utilities are available:

```bash
klist
```

can display the current ticket cache.

A TGT commonly references:

```text
krbtgt/CORP.EXAMPLE@CORP.EXAMPLE
```

Conceptually:

```text
Kerberos Key
     |
     v
TGT obtained
     |
     v
klist
     |
     v
Ticket visible
```

---

# TGT

A Ticket Granting Ticket allows the account to request service tickets.

```text
TGT
 |
 +--> CIFS
 |
 +--> LDAP
 |
 +--> HTTP
 |
 +--> HOST
 |
 +--> MSSQLSvc
```

The account's permissions still determine which resources can actually be used.

---

# TGT Does Not Equal Privilege

Remember:

```text
Valid Kerberos Key
       |
       v
Valid TGT
       |
       v
Authenticated Identity
       |
       X
Automatic Administrator
```

Kerberos authenticates the account.

It does not grant additional privileges.

---

# Service Tickets

After obtaining a TGT:

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

Examples of SPNs include:

```text
cifs/server01.corp.example
ldap/dc01.corp.example
http/web01.corp.example
host/server01.corp.example
MSSQLSvc/sql01.corp.example:1433
```

---

# Using the Ticket Cache

After obtaining the ticket:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Kerberos-aware tools can attempt authentication using the cache.

---

# SMB Validation

A low-impact validation may use:

```bash
impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This can demonstrate:

```text
Kerberos Key
      |
      v
TGT
      |
      v
Service Ticket
      |
      v
SMB Authentication
```

without immediately performing remote command execution.

---

# Hostnames and SPNs

Kerberos is strongly name-based.

Prefer:

```text
server01.corp.example
```

instead of:

```text
10.10.10.25
```

when using Kerberos.

Why?

```text
Hostname
   |
   v
Service Principal Name
   |
   v
Kerberos Service Ticket
```

Using an IP address may prevent normal SPN matching.

---

# Remote Execution

If authentication-only testing already demonstrates the security impact:

```text
Stop
```

Remote execution should only be performed when required by the engagement.

Where explicitly authorised, Kerberos-aware Impacket tools may include:

```text
psexec
wmiexec
smbexec
atexec
```

---

# psexec

Where remote administrative execution is explicitly authorised:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-psexec \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This adds a separate execution stage:

```text
Pass-the-Key
      |
      v
Kerberos Authentication
      |
      v
Administrative Access
      |
      v
Remote Execution
```

Do not conflate the authentication technique with the execution method.

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

This uses Kerberos authentication with a WMI-related execution workflow.

---

# NetExec

NetExec can also perform Kerberos-aware authentication.

Check the installed version:

```bash
nxc smb --help
```

Relevant Kerberos options may include mechanisms for:

```text
Kerberos authentication
KDC specification
Ticket-cache use
```

depending on the current NetExec version.

For detailed usage, see:

[NetExec](netexec.md)

---

# Windows Kerberos Tooling

Windows Active Directory assessments commonly use Kerberos-focused security research tools such as:

```text
Rubeus
Mimikatz
```

These should only be used where explicitly authorised.

---

# Rubeus

Rubeus is designed for interacting with Kerberos on Windows.

Conceptually, Pass-the-Key workflows may involve:

```text
AES / RC4 key
      |
      v
Rubeus
      |
      v
Request TGT
      |
      v
Kerberos ticket
```

Because command-line syntax and supported functionality can differ between builds, review the tool's current usage before testing.

---

# Ticket Injection

Some Windows Kerberos workflows can request a ticket and place it into the current logon session.

Conceptually:

```text
Kerberos Key
      |
      v
Request TGT
      |
      v
Ticket
      |
      v
Windows Logon Session
      |
      v
Kerberos-Aware Applications
```

This introduces another distinction:

```text
Obtaining ticket
       !=
Injecting ticket
```

---

# Mimikatz

Mimikatz historically demonstrated several credential-reuse techniques involving:

```text
NT hashes
Kerberos keys
Windows logon sessions
```

The important conceptual relationship for these notes is:

```text
Credential Material
       |
       v
Create / manipulate authentication context
       |
       v
Authenticate without plaintext password
```

The precise implementation should be tested only in controlled authorised environments.

---

# Linux vs Windows

Linux workflow:

```text
Kerberos Key
      |
      v
Impacket
      |
      v
.ccache
      |
      v
KRB5CCNAME
      |
      v
Kerberos-aware tools
```

Windows workflow:

```text
Kerberos Key
      |
      v
Kerberos tooling
      |
      v
Ticket
      |
      v
Windows ticket cache
      |
      v
Kerberos-aware applications
```

---

# Account Encryption Types

Active Directory exposes information related to supported encryption types through:

```text
msDS-SupportedEncryptionTypes
```

PowerShell:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties msDS-SupportedEncryptionTypes |
    Select-Object \
        SamAccountName,
        msDS-SupportedEncryptionTypes
```

For computer accounts:

```powershell
Get-ADComputer \
    -Identity '<COMPUTER>' \
    -Properties msDS-SupportedEncryptionTypes |
    Select-Object \
        Name,
        msDS-SupportedEncryptionTypes
```

---

# Do Not Interpret the Value as a Simple Number

`msDS-SupportedEncryptionTypes` is a bit field.

Therefore:

```text
Value = 24
```

should not simply be interpreted as:

```text
Encryption type 24
```

The individual flags represent supported Kerberos capabilities.

Use Microsoft documentation when interpreting the exact value.

---

# RC4 Dependencies

Older applications and systems may still depend on RC4 Kerberos encryption.

A migration model is:

```text
Inventory
   |
   v
Identify RC4 dependencies
   |
   v
Upgrade systems/services
   |
   v
Enable AES support
   |
   v
Reduce RC4
```

Do not disable legacy encryption blindly in production.

---

# AES Does Not Prevent Pass-the-Key

A common misconception is:

```text
RC4 removed
    |
    v
Pass-the-Key solved
```

This is incorrect.

If an AES key is compromised:

```text
AES256 Key
    |
    v
Kerberos Authentication
```

may still be possible.

The security objective is protecting credential material, not merely changing algorithms.

---

# Domain Accounts

Pass-the-Key primarily applies to Active Directory accounts with Kerberos keys.

Examples:

```text
CORP\alice
CORP\svc_sql
CORP\Administrator
```

The impact depends on the account's privileges.

---

# Computer Accounts

Domain computers also have Kerberos keys.

Examples:

```text
WORKSTATION01$
SERVER01$
DC01$
```

Conceptually:

```text
Computer Password
       |
       v
Kerberos Keys
```

If machine-account key material is compromised, it may be usable for authentication as that computer account.

The security impact depends on what that computer identity is permitted to do.

---

# Service Accounts

Traditional service accounts often have:

```text
Password
   |
   v
Kerberos Keys
```

If a service account is highly privileged:

```text
Compromised Key
      |
      v
Kerberos Authentication
      |
      v
Privileged Identity
```

can produce significant impact.

---

# gMSA

Group Managed Service Accounts use automatically managed credentials.

Their long, automatically generated passwords provide strong resistance to password guessing.

However:

```text
gMSA Password Material
        |
        v
Kerberos Keys
```

still represents sensitive credential material.

Permissions controlling access to managed passwords must therefore be tightly restricted.

---

# krbtgt

The `krbtgt` account is particularly sensitive because it is fundamental to the Kerberos trust model within the domain.

```text
krbtgt
   |
   v
Kerberos TGT protection
```

Compromise of `krbtgt` credential material represents a substantially different and more severe scenario than ordinary Pass-the-Key against a user account.

It is associated with Golden Ticket attack paths and should be treated separately.

---

# Trust Accounts

Active Directory trust relationships also involve cryptographic secrets.

These credentials support authentication between trusted domains.

Trust credential compromise can therefore have implications beyond a single account or host.

Trust attacks should be analysed separately in the dedicated trust notes.

---

# Credential Lifetime

A Kerberos key normally remains valid until the underlying account credential changes.

Conceptually:

```text
Password A
   |
   v
Key A
   |
   v
Valid authentication
```

After password rotation:

```text
Password B
   |
   v
Key B
```

Key A should no longer represent the current credential, subject to Kerberos password-history and ticket-lifetime considerations.

---

# Existing Tickets

Password rotation does not necessarily remove already issued tickets immediately.

```text
Key A
 |
 v
TGT issued
 |
 v
Password rotated
 |
 v
Existing TGT
 |
 v
May remain valid until
expiration/invalidation conditions
```

Incident response should therefore consider both:

```text
Credential material
```

and:

```text
Issued tickets
```

---

# Lateral Movement

Pass-the-Key can support lateral movement when the associated account has access to other systems.

```text
Compromised Host
       |
       v
Kerberos Key
       |
       v
TGT
       |
       v
Service Ticket
       |
       v
Remote System
```

Potential targets may include:

```text
File Servers
Application Servers
Database Servers
Management Servers
Domain Controllers
```

depending entirely on the account's privileges.

---

# BloodHound Analysis

Before performing active authentication, BloodHound can help identify likely access paths.

```text
Compromised Account
        |
        v
BloodHound
        |
        +--> AdminTo
        +--> CanRDP
        +--> CanPSRemote
        +--> Group Membership
        +--> ACL Rights
        +--> Sessions
```

This reduces unnecessary authentication attempts.

For detailed BloodHound usage, see:

[BloodHound](bloodhound.md)

---

# Credential Access vs Lateral Movement

Keep these stages separate.

```text
Credential Access
      |
      v
Kerberos key obtained
```

then:

```text
Credential Use
      |
      v
Pass-the-Key
```

then potentially:

```text
Lateral Movement
      |
      v
Remote service access
```

This distinction improves technical analysis and reporting.

---

# Detection

Pass-the-Key authentication can appear similar to legitimate Kerberos authentication.

The KDC sees a client capable of producing valid cryptographic authentication.

Detection therefore requires context.

```text
Kerberos Authentication
       |
       v
Account
       |
       v
Source Host
       |
       v
Encryption Type
       |
       v
Target Service
       |
       v
Subsequent Behaviour
```

---

# Event 4768

Event `4768` records Kerberos authentication-ticket requests.

This is particularly important because Pass-the-Key commonly involves obtaining a TGT.

Useful fields may include:

```text
Account Name
Service Name
Client Address
Ticket Options
Ticket Encryption Type
Pre-Authentication Type
Status
```

---

# Event 4769

Event `4769` records Kerberos service-ticket requests.

A sequence may appear as:

```text
4768
 |
 v
TGT requested
 |
 v
4769
 |
 v
Service ticket requested
```

Correlating these events provides a view of the Kerberos authentication chain.

---

# Event 4624

Successful authentication to Windows services may result in Event `4624`.

Useful fields include:

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

Privileged logons may generate:

```text
4672
```

indicating special privileges assigned to a new logon.

Correlate:

```text
4624
  +
4672
```

where appropriate.

---

# Event 4771

Event `4771` records Kerberos pre-authentication failures.

Repeated failures may indicate:

- incorrect keys
- stale credential material
- malformed authentication attempts
- password changes
- testing activity

Do not assume every `4771` represents malicious behaviour.

---

# Encryption Type Monitoring

Ticket encryption types can provide useful detection context.

For example:

```text
Account normally uses AES
         |
         v
Unexpected RC4 request
```

may deserve investigation.

However:

```text
RC4
 |
 X
Proof of attack
```

Legacy applications may legitimately require RC4.

---

# Source-System Baselines

A strong detection approach is to understand where accounts normally authenticate.

Expected:

```text
AdminUser
   |
   +--> PAW01
   |
   +--> Management01
```

Unexpected:

```text
AdminUser
   |
   v
Employee-Laptop-42
```

This context can be more valuable than simply detecting Kerberos itself.

---

# Detection Model

```text
4768
 |
 v
Who requested the TGT?
 |
 v
From where?
 |
 v
Expected source?
 |
 v
Which encryption type?
 |
 v
4769
 |
 v
Which service?
 |
 v
4624
 |
 v
Which target?
 |
 v
What happened afterwards?
```

---

# Linux-Originated Pass-the-Key

When Impacket is used from Linux:

```text
Kali
 |
 | AS-REQ
 v
Domain Controller
 |
 | 4768
 v
TGT
 |
 | TGS-REQ
 v
Domain Controller
 |
 | 4769
 v
Target
```

There may be no Windows endpoint telemetry on the originating assessment system.

Domain-controller and network telemetry therefore become particularly important.

---

# Windows-Originated Pass-the-Key

A Windows-based workflow may additionally generate endpoint telemetry relating to:

- process execution
- ticket manipulation
- unusual logon sessions
- security tool execution
- credential access
- LSASS interaction

The exact telemetry depends on the implementation.

---

# Purple Team Validation

Pass-the-Key can be tested using a dedicated low-privilege account.

Example:

```text
PT-KerberosUser
       |
       +--> Controlled AES key
       |
       +--> Access to one test service
```

The red team performs one controlled authentication while defenders observe the complete Kerberos sequence.

---

# Purple Team Exercise Flow

```text
Red Team
   |
   | Controlled Kerberos key
   v
KDC
   |
   | AS-REQ
   v
4768
   |
   v
TGT
   |
   | TGS-REQ
   v
4769
   |
   v
Test Server
   |
   v
4624
   |
   v
Blue Team
```

---

# Purple Team Questions

Defenders should attempt to determine:

```text
Which account authenticated?

Which system initiated authentication?

Which Kerberos encryption type was used?

Was the source expected?

Which service ticket was requested?

Which target received the authentication?

Did privileged activity follow?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect
Time to triage
Account identified?
Source identified?
KDC identified?
Encryption type identified?
Service identified?
Target identified?
Technique classified correctly?
```

---

# Hardening

Pass-the-Key should be addressed through multiple controls.

```text
Pass-the-Key
     |
     +--> Protect credentials
     |
     +--> Credential Guard
     |
     +--> LSA protection
     |
     +--> Administrative tiering
     |
     +--> Privileged access workstations
     |
     +--> Authentication restrictions
     |
     +--> Least privilege
     |
     +--> Kerberos monitoring
```

---

# Protect Credential Material

The most important defence is preventing attackers from obtaining reusable Kerberos keys.

Protect:

```text
NT hashes
RC4 keys
AES128 keys
AES256 keys
Kerberos tickets
```

All should be treated as credentials.

---

# Credential Guard

Windows Defender Credential Guard can reduce exposure of reusable authentication secrets.

Its objective is:

```text
Compromised process
       |
       X
Protected credential material
```

Deploy where supported and operationally appropriate.

---

# LSA Protection

LSA protection can help protect LSASS against unauthorised access.

It complements:

```text
Credential Guard
EDR
Least privilege
Administrative isolation
```

---

# Administrative Tiering

Avoid allowing highly privileged credentials onto ordinary endpoints.

Bad:

```text
Domain Admin
    |
    v
User Workstation
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

# Privileged Access Workstations

Use dedicated administrative systems for high-value identities.

The objective is to isolate:

```text
Web browsing
Email
Office applications
General user activity
```

from:

```text
Privileged administration
```

---

# Protected Users

Consider the Protected Users security group for suitable privileged accounts after compatibility testing.

It introduces stronger authentication restrictions intended to reduce credential exposure and legacy authentication use.

---

# Authentication Policies and Silos

Authentication policies can restrict where privileged accounts are allowed to authenticate.

Conceptually:

```text
Privileged Account
      |
      +--> Approved Admin Host
      |
      X
Ordinary Workstation
```

This limits the usefulness of stolen credential material.

---

# Prefer Modern Kerberos Encryption

Where possible:

```text
RC4
 |
 v
Migrate
 |
 v
AES
```

However, remember:

```text
AES migration
      |
      X
Credential-theft prevention
```

Both cryptographic modernisation and credential protection are necessary.

---

# Least Privilege

Reduce the privileges available to each account.

A compromised low-privilege key should not automatically provide:

```text
Local Administrator
Domain Administrator
Server Administrator
Database Administrator
```

unless operationally necessary.

---

# Network Segmentation

Restrict access to administrative protocols.

For example:

```text
User Network
     |
     X
SMB / WinRM / WMI
     |
     v
Server Management Network
```

This limits lateral movement even when credentials are compromised.

---

# Credential Rotation

If a Kerberos key is exposed:

```text
Key compromised
      |
      v
Account credential compromised
      |
      v
Rotate password
      |
      v
New keys generated
```

For highly sensitive accounts, follow the appropriate credential-reset procedure rather than performing an ordinary password change without understanding service dependencies.

---

# Service Account Rotation

Before rotating service-account credentials, determine:

```text
Which services use the account?
Which scheduled tasks use it?
Which applications use it?
Which application pools use it?
Which integrations depend on it?
```

Unplanned rotation can cause outages.

---

# Incident Response

If Pass-the-Key is suspected:

```text
Identify Account
      |
      v
Identify Credential Source
      |
      v
Identify Source Host
      |
      v
Review 4768
      |
      v
Review 4769
      |
      v
Identify Target Systems
      |
      v
Contain Compromised Hosts
      |
      v
Rotate Credentials
      |
      v
Review Existing Tickets
      |
      v
Investigate Lateral Movement
```

---

# Reporting

The finding should focus on the actual weakness.

Possible titles include:

```text
Exposed Kerberos Key Enables Authentication Without Plaintext Password
```

```text
Compromised AES Key Permits Kerberos Authentication
```

```text
Reusable Domain Credential Material Enables Pass-the-Key
```

```text
Credential Exposure Enables Kerberos Lateral Movement
```

---

# Avoid Overstatement

Do not report:

```text
AES key exists
     =
Vulnerability
```

Kerberos requires cryptographic keys by design.

The vulnerability is generally:

```text
Key exposed
    +
Attacker can obtain it
    +
Useful account privileges
```

---

# Example Finding

```text
Finding:
Exposed Kerberos AES Key Enables Authentication Without Plaintext Password

Affected Account:
CORP\svc_example

Validation:
During the authorised assessment, the AES256 Kerberos key associated
with the test account was obtained through the identified credential
exposure.

The key was subsequently used to request a valid Kerberos Ticket
Granting Ticket from the domain controller without supplying the
account's plaintext password.

The resulting ticket successfully authenticated to the authorised
test service.

Impact:
An attacker who obtains the account's Kerberos key material may
authenticate as that identity without recovering or knowing the
plaintext password. Any permissions assigned to the account may
therefore become available to the attacker.

Recommendation:
Rotate the affected credential, remediate the original credential
exposure, strengthen privileged credential isolation, restrict where
the account can authenticate, and deploy credential-protection
controls where appropriate.
```

---

# Evidence Collection

Record:

```text
Account
Domain
Domain Controller
Credential Type
Encryption Type
Credential Source
Source Assessment Host
TGT Request Time
Ticket Encryption Type
Ticket Lifetime
Service Ticket
Target Service
Target Host
Authentication Result
Privilege Level
Relevant Event IDs
Tool
Command
```

---

# Credential Redaction

Never expose full keys unnecessarily.

Instead of:

```text
AES256:
0123456789abcdef...
```

use:

```text
AES256:
[REDACTED]
```

or an appropriately masked representation.

---

# Ticket Protection

Protect:

```text
.ccache
.kirbi
```

files as credentials.

Do not:

- commit them to Git
- attach them to public issues
- store them unencrypted
- include them in public screenshots
- retain them beyond assessment requirements

---

# Cleanup

After testing:

```bash
unset KRB5CCNAME
```

Remove temporary ticket files where permitted:

```bash
rm -f alice.ccache
```

Ensure collected key material is handled according to the engagement's evidence-retention requirements.

---

# Troubleshooting

## KDC Unreachable

Check:

```bash
nc -vz dc01.corp.example 88
```

Review:

```text
Routing
VPN
Firewall
DNS
Domain Controller availability
```

---

# KDC_ERR_PREAUTH_FAILED

Possible causes include:

```text
Incorrect key
Incorrect username
Incorrect domain
Old credential
Unsupported encryption type
```

---

# Clock Skew

Check:

```bash
date
```

Kerberos authentication may fail if client and domain-controller time differ significantly.

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

Do not immediately assume the key is invalid when Kerberos fails.

---

# Unsupported Encryption Type

The supplied key and account configuration must support compatible Kerberos encryption.

Review:

```text
msDS-SupportedEncryptionTypes
```

and domain Kerberos policy where appropriate.

---

# TGT Obtained but Access Denied

Remember:

```text
Authentication
     !=
Authorisation
```

The account may successfully authenticate but lack permission to the target service.

---

# IP Address Fails

Use:

```text
server01.corp.example
```

instead of:

```text
10.10.10.25
```

when Kerberos requires an SPN associated with the hostname.

---

# Ticket Cache Problems

Check:

```bash
echo "$KRB5CCNAME"
```

then:

```bash
klist
```

If necessary:

```bash
export KRB5CCNAME="$(pwd)/alice.ccache"
```

---

# Common Mistakes

## Mistake 1 - Treating AES Keys as Harmless

An AES key is reusable authentication material.

```text
AES Key
   =
Credential
```

---

## Mistake 2 - Calling Everything Pass-the-Hash

Be precise:

```text
NT hash -> NTLM
    =
Pass-the-Hash


Kerberos key -> Kerberos
    =
Pass-the-Key
```

---

## Mistake 3 - Confusing Key and Ticket

```text
Key
 |
 v
Obtains ticket


Ticket
 |
 v
Used for authentication
```

---

## Mistake 4 - Assuming AES Prevents Credential Reuse

AES improves cryptographic security.

It does not prevent use of a stolen AES key.

---

## Mistake 5 - Assuming a TGT Means Administrator

A TGT represents an authenticated identity.

Privileges remain unchanged.

---

## Mistake 6 - Ignoring DNS

Kerberos is highly dependent on correct naming and SPNs.

---

## Mistake 7 - Ignoring Time

Always check time during Kerberos troubleshooting.

---

## Mistake 8 - Using IP Addresses Everywhere

Kerberos generally works more reliably with correct hostnames.

---

## Mistake 9 - Performing Remote Execution Automatically

Ticket acquisition and service authentication may already prove the finding.

---

## Mistake 10 - Publishing Keys or Tickets

Keys and tickets are credentials.

Protect them accordingly.

---

# Assessment Checklist

## Preparation

- [ ] Confirm Pass-the-Key testing is authorised
- [ ] Confirm permitted accounts
- [ ] Confirm permitted systems
- [ ] Confirm remote execution rules
- [ ] Identify domain
- [ ] Identify domain controller
- [ ] Confirm DNS
- [ ] Confirm time synchronisation
- [ ] Confirm KDC reachability

## Credential Analysis

- [ ] Identify account
- [ ] Identify key type
- [ ] Distinguish RC4, AES128 and AES256
- [ ] Identify credential source
- [ ] Determine whether credential is current
- [ ] Protect key material

## Kerberos Validation

- [ ] Request TGT
- [ ] Record KDC
- [ ] Record timestamp
- [ ] Record encryption type
- [ ] Protect resulting ticket
- [ ] Verify ticket with `klist`

## Service Validation

- [ ] Identify authorised target
- [ ] Use hostname
- [ ] Identify target SPN
- [ ] Request minimum required service access
- [ ] Record authentication result
- [ ] Avoid unnecessary remote execution

## Privilege Analysis

- [ ] Review group membership
- [ ] Review BloodHound
- [ ] Determine administrative rights
- [ ] Determine remote management rights
- [ ] Determine delegated AD permissions
- [ ] Record actual impact

## Detection

- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4624
- [ ] Review 4672
- [ ] Review 4771 where relevant
- [ ] Correlate source and account
- [ ] Review ticket encryption type
- [ ] Review target service
- [ ] Review subsequent activity

## Remediation

- [ ] Rotate compromised credential
- [ ] Remediate credential source
- [ ] Deploy Credential Guard where appropriate
- [ ] Enable LSA protection where appropriate
- [ ] Implement administrative tiering
- [ ] Restrict privileged logons
- [ ] Consider Protected Users
- [ ] Consider authentication policies
- [ ] Reduce unnecessary RC4
- [ ] Apply least privilege
- [ ] Segment management protocols

## Cleanup

- [ ] Remove temporary ticket caches
- [ ] Remove test artefacts
- [ ] Clear unnecessary environment variables
- [ ] Secure retained evidence
- [ ] Redact keys from reports
- [ ] Follow credential-retention requirements

---

# Pass-the-Key Testing Model

A useful mental model is:

```text
                        Account Password
                              |
                              v
                      Kerberos Key Material
                              |
                  +-----------+-----------+
                  |           |           |
                  v           v           v
                RC4        AES128       AES256
                  |           |           |
                  +-----------+-----------+
                              |
                              v
                       Key Compromised
                              |
                              v
                         Pass-the-Key
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
                              v
                       Service Ticket
                              |
                              v
                    Target Authentication
                              |
                     +--------+--------+
                     |                 |
                     v                 v
                   Denied            Allowed
                                         |
                                         v
                                 Privilege Analysis
                                         |
                                         v
                                 Minimum Validation
```

The credential relationship is:

```text
                    Credential Material
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       NT Hash        Kerberos Key     Kerberos Ticket
          |                |                |
          v                v                v
 Pass-the-Hash       Pass-the-Key     Pass-the-Ticket
          |                |                |
          v                v                v
        NTLM            Kerberos          Kerberos
```

The broader Kerberos attack model is:

```text
Credential Discovery
        |
        v
Credential Material
        |
   +----+-------------------+
   |                        |
   v                        v
Password                  Key
   |                        |
   v                        v
Normal Kerberos       Pass-the-Key
   |                        |
   +-----------+------------+
               |
               v
              TGT
               |
               v
        Service Tickets
               |
               v
        Resource Access
```

The defensive model is:

```text
Pass-the-Key
     |
     +--> Prevent credential theft
     |       |
     |       +--> Credential Guard
     |       +--> LSA protection
     |       +--> EDR
     |
     +--> Protect privileged identities
     |       |
     |       +--> PAWs
     |       +--> Administrative tiering
     |       +--> Protected Users
     |
     +--> Restrict credential use
     |       |
     |       +--> Authentication policies
     |       +--> Restricted logon
     |       +--> Segmentation
     |
     +--> Reduce impact
     |       |
     |       +--> Least privilege
     |
     +--> Detect
             |
             +--> 4768
             +--> 4769
             +--> 4624
             +--> 4771
             +--> Source baselines
```

The assessment should answer:

```text
How was the Kerberos key obtained?
        |
        v
Which account does it belong to?
        |
        v
Which key type was exposed?
        |
        v
Is the key still valid?
        |
        v
Can it obtain a TGT?
        |
        v
Which service tickets can be obtained?
        |
        v
Where can the account authenticate?
        |
        v
What privileges does the account have?
        |
        v
Can defenders detect the authentication?
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

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement Pass-the-Key and can be linked once their dedicated notes are available:

```text
active-directory/kerberos-tickets.md
active-directory/pass-the-ticket.md
active-directory/lateral-movement.md
active-directory/smb.md
active-directory/winrm.md
active-directory/wmi.md
active-directory/gmsa.md
active-directory/trusts.md
```

---

# References

## Microsoft Kerberos

[Microsoft - Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos supported encryption types](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-supported-encryption-types){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows authentication overview](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/windows-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Credential Protection

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Configure added LSA protection](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## Kerberos Protocol

[Microsoft Open Specifications - Kerberos Protocol Extensions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Use Alternate Authentication Material](https://attack.mitre.org/techniques/T1550/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Hash](https://attack.mitre.org/techniques/T1550/002/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket getTGT](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Pass-the-Key demonstrates that a password is not the only form of reusable authentication material in Active Directory.

The important credential hierarchy is:

```text
Password
   |
   v
Cryptographic Keys
   |
   +--> NT / RC4
   |
   +--> AES128
   |
   +--> AES256
```

Once a suitable Kerberos key is compromised:

```text
Plaintext password
        |
        X
Not necessarily required
```

The attacker may instead perform:

```text
Kerberos Key
     |
     v
AS-REQ
     |
     v
KDC
     |
     v
TGT
     |
     v
Service Ticket
     |
     v
Authenticated Access
```

The key distinctions are:

```text
Pass-the-Hash
     =
NT hash -> NTLM


OverPass-the-Hash
     =
NT/RC4 material -> Kerberos


Pass-the-Key
     =
Kerberos key -> Kerberos


Pass-the-Ticket
     =
Existing Kerberos ticket -> Kerberos


Kerberoasting
     =
Service ticket -> Offline password guessing


AS-REP Roasting
     =
AS-REP -> Offline password guessing
```

The defensive lesson is equally important:

```text
Strong Password
      |
      X
Enough if key is stolen


AES256
      |
      X
Enough if AES key is stolen
```

The complete defensive model therefore requires:

```text
Strong credentials
        +
Credential isolation
        +
Credential Guard
        +
LSA protection
        +
Administrative tiering
        +
Restricted privileged logons
        +
Least privilege
        +
Network segmentation
        +
Kerberos monitoring
```

A mature Pass-the-Key assessment should determine how the Kerberos key became exposed, what type of key was obtained, which identity it represents, whether the key can obtain a valid TGT, which services and systems the identity can access, what privileges are available, whether defenders can identify the unusual authentication path, and which defensive control would most effectively prevent the credential material from being stolen or reused.
