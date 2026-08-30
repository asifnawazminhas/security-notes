# OverPass-the-Hash

OverPass-the-Hash is an Active Directory authentication technique in which password-derived key material, most commonly an **NT hash**, is used to obtain Kerberos authentication material instead of authenticating directly through NTLM.

The technique is also commonly called:

```text
Pass-the-Key
```

although terminology can vary between tools and documentation.

The central idea is:

```text
Password
   |
   v
Password-derived key
   |
   v
Kerberos authentication
   |
   v
TGT
```

Normally, a user enters a plaintext password and the Kerberos client derives the cryptographic key required to perform authentication.

With OverPass-the-Hash, the tester already possesses suitable password-derived key material and attempts to use it directly.

A simplified flow is:

```text
NT hash / Kerberos key
        |
        v
Kerberos AS-REQ
        |
        v
Domain Controller / KDC
        |
        v
AS-REP
        |
        v
Ticket Granting Ticket
        |
        v
Kerberos service tickets
```

The important difference from traditional Pass-the-Hash is the authentication protocol ultimately used:

```text
Pass-the-Hash
      |
      v
NT hash
      |
      v
NTLM


OverPass-the-Hash
      |
      v
Password-derived key
      |
      v
Kerberos
```

!!! warning "Authorised testing only"
    OverPass-the-Hash uses reusable credential material to authenticate as another account and can provide access to domain resources. Only perform this technique against accounts, systems, and domains explicitly included in the assessment scope. Protect hashes, keys, and Kerberos tickets as credentials and validate only the minimum access necessary to demonstrate impact.

---

# OverPass-the-Hash at a Glance

A typical assessment workflow is:

```text
Obtain authorised credential material
              |
              v
      Identify account
              |
              v
      Identify key type
              |
       +------+------+
       |      |      |
       v      v      v
      NT     AES128  AES256
     hash      key     key
       |       |       |
       +-------+-------+
               |
               v
      Contact Kerberos KDC
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
            Request service ticket
                    |
                    v
           Access authorised service
                    |
                    v
             Minimum validation
                    |
                    v
           Detection / Remediation
```

---

# Kerberos Refresher

OverPass-the-Hash operates during the Kerberos authentication process.

A simplified normal Kerberos flow is:

```text
User
 |
 | Password
 v
Kerberos client
 |
 | Derive cryptographic key
 v
AS-REQ
 |
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
Service
```

For detailed Kerberos architecture, see:

[Kerberos](kerberos.md)

---

# Normal Password-Based Kerberos Authentication

Under normal circumstances:

```text
User enters password
        |
        v
Client derives key
        |
        v
Kerberos pre-authentication
        |
        v
KDC validates proof
        |
        v
TGT returned
```

The password itself does not need to be transmitted to the KDC.

Instead, the password is used to derive cryptographic key material.

---

# OverPass-the-Hash Authentication

If the tester already possesses the required key material:

```text
Password
   X
Not required
```

Instead:

```text
Known key
   |
   v
Generate Kerberos authentication
   |
   v
Request TGT
```

This is why password-derived hashes and Kerberos keys must be treated as reusable credentials.

---

# Why the Technique Works

Kerberos authentication ultimately depends on possession of appropriate cryptographic key material.

Conceptually:

```text
Password
   |
   v
Key derivation
   |
   v
Kerberos key
```

If the key is already known:

```text
Known Kerberos key
       |
       v
No need to recover password
       |
       v
Authenticate using key
```

The password is only one way to obtain the key.

---

# Credential Material

Depending on account and domain configuration, useful credential material may include:

```text
NT hash
AES128 key
AES256 key
```

These values are not interchangeable in every context.

Always determine:

```text
What credential material do I have?
        |
        v
Which encryption type does it represent?
        |
        v
Which authentication method accepts it?
```

---

# NT Hash

An NT hash is derived from the user's password.

Conceptually:

```text
Password
   |
   v
UTF-16LE
   |
   v
MD4
   |
   v
NT hash
```

The NT hash is strongly associated with NTLM authentication but can also be relevant to Kerberos workflows involving RC4 key material.

This is what historically gives rise to the term:

```text
OverPass-the-Hash
```

---

# AES Kerberos Keys

Modern Active Directory environments may support AES Kerberos keys.

Common key sizes include:

```text
AES128
AES256
```

These keys can also represent reusable Kerberos authentication material.

Therefore, the broader concept can be represented as:

```text
Credential key material
        |
   +----+----+------+
   |         |      |
   v         v      v
 NT hash   AES128  AES256
   |         |      |
   +---------+------+
             |
             v
       Kerberos authentication
```

---

# OverPass-the-Hash vs Pass-the-Hash

This distinction is essential.

## Pass-the-Hash

```text
NT hash
   |
   v
NTLM challenge-response
   |
   v
Remote service
```

## OverPass-the-Hash

```text
NT hash / Kerberos key
        |
        v
Kerberos authentication
        |
        v
TGT
        |
        v
Service ticket
```

Comparison:

| Property | Pass-the-Hash | OverPass-the-Hash |
|---|---|---|
| Initial credential | NT hash | NT hash or suitable Kerberos key |
| Main protocol | NTLM | Kerberos |
| TGT obtained | No | Yes |
| Service tickets | Not required | Used |
| Plaintext password required | No | No |
| Credential reuse | Yes | Yes |

For Pass-the-Hash details, see:

[Pass-the-Hash](pass-the-hash.md)

---

# OverPass-the-Hash vs Pass-the-Ticket

These techniques begin at different stages.

OverPass-the-Hash:

```text
Key material
     |
     v
Request TGT
     |
     v
Kerberos ticket obtained
```

Pass-the-Ticket:

```text
Existing Kerberos ticket
        |
        v
Inject / use ticket
        |
        v
Kerberos authentication
```

The distinction is:

```text
OverPass-the-Hash
      =
Key -> Ticket


Pass-the-Ticket
      =
Existing Ticket -> Authentication
```

---

# OverPass-the-Hash vs Kerberoasting

Kerberoasting:

```text
SPN
 |
 v
Service ticket
 |
 v
Offline password guessing
 |
 v
Potential password recovery
```

OverPass-the-Hash:

```text
Already possess key material
        |
        v
Request Kerberos TGT
```

Kerberoasting is a credential-recovery technique.

OverPass-the-Hash is a credential-use technique.

---

# OverPass-the-Hash vs AS-REP Roasting

AS-REP Roasting:

```text
Pre-authentication disabled
          |
          v
AS-REP obtained
          |
          v
Offline password guessing
```

OverPass-the-Hash:

```text
Credential key already known
          |
          v
Kerberos authentication
```

These represent different stages of an attack chain.

---

# OverPass-the-Hash vs Password Spraying

Password spraying attempts to discover credentials:

```text
Candidate password
       |
       v
Multiple accounts
```

OverPass-the-Hash starts after credential material has already been obtained:

```text
Known hash/key
      |
      v
Kerberos authentication
```

---

# Requirements

Typical requirements include:

```text
Valid credential key material
          |
          +
Known username
          |
          +
Known domain
          |
          +
Reachable KDC
          |
          +
Correct time
          |
          +
Correct DNS/domain context
```

Kerberos commonly uses:

```text
88/TCP
88/UDP
```

---

# Domain Controller Reachability

Check Kerberos connectivity:

```bash
nc -vz 10.10.10.10 88
```

Successful TCP connectivity does not prove the entire Kerberos configuration is correct, but it confirms basic reachability.

---

# DNS

Kerberos relies heavily on correct naming.

Important values include:

```text
Domain
Realm
Domain controller hostname
Service hostname
SPN
```

A typical environment might be:

```text
Domain:
corp.example

Realm:
CORP.EXAMPLE

Domain Controller:
dc01.corp.example
```

Incorrect DNS frequently causes Kerberos testing problems.

---

# Time Synchronisation

Kerberos is time-sensitive.

Check the assessment host:

```bash
date
```

A significant time difference between the client and KDC can cause Kerberos authentication failures.

A useful troubleshooting model is:

```text
Kerberos failure
      |
      +--> Credentials?
      +--> DNS?
      +--> Time?
      +--> SPN?
      +--> Encryption type?
      +--> KDC?
```

---

# Obtaining Credential Material

During an authorised assessment, suitable credential material may have been obtained through:

- authorised credential extraction
- local credential stores
- Active Directory credential access
- memory credential exposure
- client-provided testing credentials
- secrets recovered during another approved assessment stage

The source of the credential should be recorded separately from its later use.

---

# Credential Access vs Credential Use

Maintain this distinction:

```text
Credential Access
       |
       v
NT hash / AES key obtained
```

versus:

```text
Credential Use
       |
       v
OverPass-the-Hash
```

This improves both attack-path analysis and reporting.

---

# Impacket getTGT

Impacket provides `getTGT.py`, commonly installed as:

```text
impacket-getTGT
```

Check:

```bash
which impacket-getTGT
```

Review current syntax:

```bash
impacket-getTGT -h
```

---

# Requesting a TGT with an NT Hash

A common authorised pattern is:

```bash
impacket-getTGT \
    'corp.example/alice' \
    -hashes ':<NT_HASH>' \
    -dc-ip 10.10.10.10
```

Conceptually:

```text
NT hash
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

If successful, Impacket commonly writes a Kerberos credential cache file.

For example:

```text
alice.ccache
```

---

# Requesting a TGT with an AES Key

Where the appropriate AES key is available, current Impacket versions may support authentication using:

```text
-aesKey
```

General pattern:

```bash
impacket-getTGT \
    'corp.example/alice' \
    -aesKey '<AES_KEY>' \
    -dc-ip 10.10.10.10
```

The supplied key must correspond to the account and supported encryption type.

Review:

```bash
impacket-getTGT -h
```

for the installed version.

---

# Kerberos Credential Cache

Impacket commonly stores tickets using the MIT Kerberos credential-cache format:

```text
.ccache
```

Example:

```text
alice.ccache
```

This file is credential-sensitive.

Treat it like:

```text
Password
NT hash
AES key
Kerberos ticket
```

---

# KRB5CCNAME

Linux Kerberos-aware tools commonly use:

```text
KRB5CCNAME
```

to identify the credential cache.

Example:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Verify:

```bash
echo "$KRB5CCNAME"
```

---

# Inspecting the Ticket Cache

If Kerberos client utilities are installed:

```bash
klist
```

can display cached tickets.

Example conceptual output:

```text
Default principal:
alice@CORP.EXAMPLE

Valid starting
Expires
Service principal:
krbtgt/CORP.EXAMPLE@CORP.EXAMPLE
```

Do not publish real ticket information unnecessarily.

---

# TGT

A Ticket Granting Ticket allows the authenticated principal to request service tickets.

```text
TGT
 |
 +--> CIFS
 |
 +--> LDAP
 |
 +--> HTTP
 |
 +--> MSSQLSvc
 |
 +--> HOST
```

Actual access still depends on the account's permissions.

---

# TGT Does Not Mean Administrator

This distinction is critical:

```text
TGT obtained
     |
     v
Authentication as user
     |
     X
Administrator automatically
```

The TGT represents the identity of the account.

Privileges remain determined by:

- group membership
- ACLs
- target permissions
- local administrator membership
- service permissions

---

# Using the Kerberos Cache with Impacket

Many Impacket tools support Kerberos authentication through:

```text
-k
```

and can use an existing ticket cache.

A common pattern is:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

followed by:

```bash
impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This attempts Kerberos authentication using the existing cache rather than a plaintext password.

---

# Why Hostnames Matter

Kerberos service tickets are associated with SPNs.

Therefore:

```text
server01.corp.example
```

is generally preferable to:

```text
10.10.10.25
```

for Kerberos authentication.

Conceptually:

```text
Hostname
   |
   v
SPN resolution
   |
   v
Kerberos service ticket
```

Using an IP address can interfere with normal Kerberos SPN matching.

---

# SMB Validation

Where SMB authentication is authorised:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-smbclient \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This can validate Kerberos authentication without immediately performing remote command execution.

---

# Impacket psexec with Kerberos

If remote administrative execution is explicitly required:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-psexec \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

Remote execution should only be used after determining that authentication-only validation is insufficient.

---

# Impacket wmiexec with Kerberos

Where authorised:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-wmiexec \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

This represents a separate execution stage after Kerberos authentication.

---

# Impacket smbexec with Kerberos

Where supported and explicitly authorised:

```bash
export KRB5CCNAME="$PWD/alice.ccache"

impacket-smbexec \
    -k \
    -no-pass \
    'corp.example/alice@server01.corp.example'
```

Always review:

```bash
impacket-smbexec -h
```

because exact authentication options can vary between versions.

---

# Authentication Before Execution

Use the least invasive validation path.

```text
Hash / key
    |
    v
Request TGT
    |
    v
TGT obtained
    |
    v
Authenticate to service
    |
    v
Success?
   +--+--+
   |     |
  No    Yes
         |
         v
Impact proven?
      +--+--+
      |     |
     Yes    No
      |     |
      v     v
    Stop   Additional authorised
           validation if required
```

---

# NetExec

NetExec supports Kerberos authentication for several protocols and can be useful when validating ticket-based access.

Because syntax and protocol capabilities can evolve, review the installed version:

```bash
nxc --help
```

and protocol-specific help:

```bash
nxc smb --help
```

Kerberos authentication commonly involves options relating to:

```text
-k
--use-kcache
```

depending on the current version and workflow.

For detailed NetExec usage, see:

[NetExec](netexec.md)

---

# Windows Tooling

On Windows, OverPass-the-Hash has historically been associated with tools capable of using password-derived key material to establish Kerberos authentication contexts.

Common security research tooling has included:

```text
Mimikatz
Rubeus
```

These tools can be highly monitored and should only be used in explicitly authorised environments.

---

# Mimikatz Concept

A commonly discussed Mimikatz workflow uses:

```text
sekurlsa::pth
```

to create a logon context using supplied credential material.

Conceptually:

```text
Username
   +
Domain
   +
NT hash
   |
   v
New logon context
   |
   v
Kerberos-capable process
```

The important concept is the creation of an authentication context from key material rather than recovery of the plaintext password.

Exact behaviour depends on:

- Windows version
- security controls
- privileges
- tool version
- credential type

---

# Rubeus Concept

Rubeus is a Kerberos-focused security research tool commonly used in Windows Active Directory labs and assessments.

Relevant capabilities include workflows for:

```text
Requesting TGTs
Using RC4 material
Using AES keys
Inspecting tickets
Managing ticket caches
```

Use the tool's current help output rather than relying on old syntax:

```text
Rubeus.exe
```

or the relevant action-specific help supported by the version in use.

---

# Linux vs Windows Workflows

A useful distinction is:

```text
Linux / Kali
     |
     +--> Impacket
     +--> MIT Kerberos tools
     +--> .ccache
     +--> KRB5CCNAME


Windows
     |
     +--> Native Kerberos cache
     +--> Rubeus
     +--> Mimikatz
     +--> Windows logon sessions
```

The underlying authentication concept remains the same.

---

# Pass-the-Key Terminology

Modern Kerberos environments increasingly use AES keys.

Therefore, the term:

```text
Pass-the-Key
```

can sometimes be more technically descriptive than:

```text
OverPass-the-Hash
```

when the supplied material is an AES key rather than an NT hash.

A useful model is:

```text
OverPass-the-Hash
      |
      +--> Historically associated with NT/RC4 key


Pass-the-Key
      |
      +--> Broader use of Kerberos key material
           |
           +--> RC4
           +--> AES128
           +--> AES256
```

Terminology varies between security tools and practitioners, so reports should state exactly what credential material was used.

---

# Do Not Over-Focus on Terminology

Instead of writing only:

```text
OverPass-the-Hash was performed
```

a clearer report statement is:

```text
The NT hash associated with the authorised test account was used to
obtain a Kerberos Ticket Granting Ticket without knowledge of the
plaintext password.
```

This describes exactly what was demonstrated.

---

# Encryption Types

Kerberos authentication can involve several encryption types.

Common Active Directory examples include:

```text
RC4-HMAC
AES128
AES256
```

Account configuration and domain policy influence which keys are available.

---

# RC4 Relationship

The NT hash corresponds to key material historically used by RC4-HMAC Kerberos authentication.

Conceptually:

```text
NT hash
   |
   v
RC4 Kerberos key material
   |
   v
Kerberos authentication
```

This relationship enables classic OverPass-the-Hash workflows.

---

# AES Relationship

For AES authentication, the relevant AES key must be available.

```text
AES key
   |
   v
Kerberos pre-authentication
   |
   v
TGT
```

An NT hash should not simply be described as an AES key.

Keep credential types explicit.

---

# Account Encryption Configuration

Active Directory account properties can influence supported Kerberos encryption types.

PowerShell can inspect:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties msDS-SupportedEncryptionTypes |
    Select-Object \
        SamAccountName,
        msDS-SupportedEncryptionTypes
```

Interpret the value carefully because it represents a bit field.

---

# Domain Encryption Policy

Kerberos encryption behaviour can also be influenced by:

- domain controller configuration
- operating system versions
- group policy
- account settings
- service compatibility
- trust configuration

Do not infer the environment's encryption posture from a single ticket.

---

# Service Tickets

Once a TGT exists, Kerberos can request tickets for specific services.

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

Examples include:

```text
cifs/server01.corp.example
ldap/dc01.corp.example
http/web01.corp.example
MSSQLSvc/sql01.corp.example:1433
```

---

# Service Ticket Access

Possession of a TGT does not grant universal service access.

The account must still have permission to use the requested service.

```text
Valid TGT
   |
   v
Valid identity
   |
   v
Service authorisation
   |
   +--> Allowed
   |
   +--> Denied
```

Kerberos provides authentication.

The service still performs authorisation.

---

# BloodHound

BloodHound can help determine where the account represented by the key material has useful access.

```text
NT hash / AES key
       |
       v
Associated account
       |
       v
BloodHound
       |
       +--> Group membership
       +--> AdminTo
       +--> CanRDP
       +--> CanPSRemote
       +--> ACL relationships
       +--> Sessions
       +--> Paths to high-value systems
```

This can reduce unnecessary active authentication attempts.

For detailed BloodHound coverage, see:

[BloodHound](bloodhound.md)

---

# Local Accounts

OverPass-the-Hash is primarily relevant to domain Kerberos authentication.

A local Windows account:

```text
SERVER01\LocalAdmin
```

does not normally have an Active Directory Kerberos identity capable of obtaining a domain TGT.

Therefore:

```text
Local account NT hash
       |
       +--> Pass-the-Hash may be relevant
       |
       X
Normal domain OverPass-the-Hash
```

This is an important difference from traditional Pass-the-Hash.

---

# Domain Accounts

A domain account has Kerberos key material maintained within Active Directory.

Example:

```text
CORP\alice
```

or:

```text
alice@corp.example
```

Suitable key material for that account may potentially be used to obtain Kerberos tickets.

---

# Machine Accounts

Domain-joined computers also possess Active Directory accounts:

```text
SERVER01$
WORKSTATION01$
DC01$
```

These accounts have Kerberos credentials and can authenticate within the domain.

Machine-account key material can therefore be relevant to advanced Kerberos attack paths.

However, computer accounts have different privileges and intended uses from ordinary users.

Analyse their permissions separately.

---

# Service Accounts

Traditional domain service accounts may also possess reusable Kerberos key material.

If such an account is privileged:

```text
Service account key
       |
       v
Kerberos TGT
       |
       v
Service tickets
       |
       v
Potential privileged access
```

The impact depends on the account's actual permissions.

---

# gMSA Accounts

Group Managed Service Accounts use automatically managed passwords.

This significantly improves resistance to human password guessing.

However, if authorised testing demonstrates that an attacker can retrieve the gMSA's current credential material through excessive permissions, that material may still represent authentication capability.

Therefore:

```text
gMSA strong password
        |
        v
Good protection against guessing


Improper gMSA password-read permissions
        |
        v
Separate credential-access risk
```

---

# Credential Reuse

OverPass-the-Hash demonstrates an important principle:

```text
Password changed?
```

If the password has not changed:

```text
Old key material remains valid
```

If the password is changed:

```text
New password
     |
     v
New cryptographic key material
```

Previously compromised keys should eventually cease to provide normal authentication once the credential change has propagated and relevant ticket lifetimes have expired.

---

# Existing Kerberos Tickets

Changing a password does not necessarily instantly invalidate every Kerberos ticket already issued.

Consider:

```text
Credential compromised
       |
       v
TGT issued
       |
       v
Password changed
       |
       v
Existing ticket may remain
usable until invalidated/expired
```

Incident response should therefore consider both:

```text
Credential rotation
```

and:

```text
Existing authentication material
```

---

# Lateral Movement

OverPass-the-Hash can enable lateral movement when the represented account has remote access.

```text
Compromised system
       |
       v
Domain key material
       |
       v
TGT
       |
       v
Service ticket
       |
       v
Remote server
```

Possible services may include:

```text
SMB
WinRM
WMI
HTTP
SQL
LDAP
```

depending on account permissions and environment configuration.

---

# Avoid Unnecessary Lateral Movement

A controlled assessment should not automatically proceed:

```text
Hash
 |
 v
TGT
 |
 v
Server A
 |
 v
Credential dump
 |
 v
Server B
 |
 v
Credential dump
```

unless the engagement specifically requires demonstrating the complete attack chain.

Prefer:

```text
Key material
     |
     v
TGT obtained
     |
     v
One authorised service
     |
     v
Impact demonstrated
     |
     v
Stop
```

---

# Kerberos-Only Environments

An important security implication is that disabling or restricting NTLM does not automatically make stolen password-derived key material harmless.

Conceptually:

```text
NTLM disabled
     |
     v
Traditional Pass-the-Hash blocked
```

but:

```text
Suitable Kerberos key material
        |
        v
Kerberos authentication
```

may remain relevant.

The defensive priority must therefore include protecting credentials themselves.

---

# Credential Guard

Windows Defender Credential Guard helps protect credential material using virtualization-based security.

Its objective includes reducing exposure of reusable credentials from compromised systems.

Conceptually:

```text
Attacker process
       |
       X
Protected credential secrets
       |
       v
Isolated security environment
```

Credential Guard addresses the credential-acquisition stage rather than changing the fundamental Kerberos protocol.

---

# LSA Protection

LSA protection can make unauthorised access to LSASS more difficult.

This can help reduce exposure of:

```text
NT hashes
Kerberos keys
Authentication secrets
```

It should be considered alongside:

- Credential Guard
- endpoint security
- least privilege
- administrative isolation

---

# Administrative Tiering

Privileged credentials should not be exposed to lower-trust systems.

Bad model:

```text
Domain Admin
    |
    v
Ordinary workstation
    |
    v
Credential exposure
    |
    v
Domain compromise
```

Better model:

```text
Privileged Account
       |
       v
Dedicated administrative system
       |
       v
Privileged systems only
```

---

# Privileged Access Workstations

Privileged Access Workstations can reduce the likelihood that administrative credential material is exposed on compromised user endpoints.

The objective is:

```text
User activity
     |
     X
Privileged credentials


Administrative activity
     |
     v
Controlled privileged workstation
```

---

# Protected Users

The Active Directory **Protected Users** security group introduces additional authentication protections for high-value accounts.

Among other restrictions, it reduces dependence on weaker or reusable authentication mechanisms.

Compatibility should be tested before deployment because legacy services may not support the resulting authentication requirements.

---

# Authentication Policies and Silos

Active Directory authentication policies and authentication policy silos can further restrict where privileged identities are allowed to authenticate.

Conceptually:

```text
Privileged Account
      |
      v
Allowed only on
approved systems
```

This reduces the usefulness of compromised credentials on unrelated hosts.

---

# Detection

OverPass-the-Hash is challenging to detect solely from Kerberos authentication events because the resulting Kerberos activity may resemble legitimate authentication.

Detection therefore requires context.

```text
Kerberos authentication
       |
       v
Which account?
       |
       v
Which source?
       |
       v
Was this source expected?
       |
       v
What happened afterwards?
```

---

# Event 4768

Event `4768` records Kerberos authentication-ticket requests.

This is highly relevant because OverPass-the-Hash involves obtaining a TGT.

Useful fields can include:

```text
Account Name
Supplied Realm Name
Service Name
Client Address
Ticket Options
Ticket Encryption Type
Pre-Authentication Type
Status
```

Field availability depends on Windows version and auditing configuration.

---

# Event 4769

Event `4769` records Kerberos service-ticket requests.

After obtaining a TGT:

```text
4768
 |
 v
TGT obtained
 |
 v
4769
 |
 v
Service ticket requested
```

Correlating these events can reveal the subsequent services accessed by the account.

---

# Event 4624

When the Kerberos credential is used to access a Windows system, Event `4624` may record successful logon activity.

Useful fields include:

```text
Account
Domain
Logon Type
Authentication Package
Source Network Address
Workstation
```

---

# Event 4672

If the authenticated account receives special privileges:

```text
4672
```

may appear.

Correlate:

```text
4624
  +
4672
```

to identify privileged logons.

---

# Authentication Package

Kerberos-authenticated sessions may show:

```text
Kerberos
```

rather than:

```text
NTLM
```

This is one of the key telemetry differences from traditional Pass-the-Hash.

---

# Detection Context

A suspicious sequence might look like:

```text
User workstation
       |
       v
4768 for privileged account
       |
       v
4769 for CIFS/server01
       |
       v
4624 on server01
       |
       v
Administrative activity
```

The individual events may be legitimate.

The unusual source-account relationship provides the context.

---

# Baseline Administrative Authentication

Defenders should understand where privileged accounts normally authenticate.

Example:

```text
CORP\AdminUser
       |
       +--> PAW01
       |
       +--> Management01
```

Unexpected:

```text
CORP\AdminUser
       |
       v
Employee-Laptop-27
```

may deserve investigation.

---

# Encryption-Type Detection

Kerberos ticket encryption can provide additional context.

Monitor:

```text
Expected AES
     |
     v
Unexpected RC4
```

where appropriate.

However:

```text
RC4 ticket
    X
Proof of OverPass-the-Hash
```

Legacy systems may legitimately use RC4.

Use encryption type as one signal among several.

---

# Endpoint Detection

Windows-based tooling used to perform OverPass-the-Hash may also produce endpoint telemetry.

Possible signals include:

- suspicious LSASS access
- unusual logon-session creation
- security-tool detections
- unusual process trees
- Kerberos ticket manipulation
- credential-access activity

Detection depends strongly on the implementation used.

---

# Linux-Originated Authentication

An Impacket-based workflow may originate from a Linux assessment system.

In that case:

```text
Windows endpoint tool telemetry
        |
        X
May not exist on source
```

but domain controllers and targets may still observe:

```text
4768
4769
4624
Network connections
```

This demonstrates why network and domain-controller telemetry remain important.

---

# Purple Team Validation

OverPass-the-Hash can be tested using a dedicated account.

Example:

```text
PT-KerberosUser
      |
      +--> Known controlled NT hash/key
      |
      +--> No production privilege
```

The red team requests a TGT while defenders monitor the authentication path.

---

# Purple Team Exercise Flow

```text
Red Team
   |
   | Use controlled key material
   v
KDC
   |
   | TGT request
   v
4768
   |
   v
TGT
   |
   | Service ticket request
   v
4769
   |
   v
Controlled server
   |
   v
4624
   |
   v
Blue Team
```

---

# Purple Team Questions

The blue team should determine:

```text
Which account requested the TGT?

Which host generated the request?

Was the source expected?

Which encryption type was used?

Which service ticket was requested?

Which target was accessed?

Was privileged activity performed?
```

---

# Purple Team Metrics

Useful measurements include:

```text
Time to detect
Time to triage
Account identified?
Source identified?
TGT request identified?
Service ticket identified?
Target identified?
Authentication protocol identified?
Technique correctly classified?
```

---

# Hardening

OverPass-the-Hash should be addressed primarily by protecting reusable credential material.

```text
OverPass-the-Hash
       |
       +--> Protect credentials
       |
       +--> Credential Guard
       |
       +--> LSA protection
       |
       +--> Administrative tiering
       |
       +--> Protected Users
       |
       +--> Authentication restrictions
       |
       +--> Least privilege
       |
       +--> Strong monitoring
```

---

# Protect Credential Material

The fundamental control is:

```text
Prevent attackers from obtaining
password-derived key material
```

This includes protecting:

```text
NT hashes
AES keys
Kerberos tickets
LSASS secrets
Credential stores
```

---

# Credential Guard

Deploy Credential Guard where supported and operationally appropriate.

Its purpose is to reduce the ability of malicious processes to obtain reusable credentials from the operating system.

---

# LSA Protection

Enable appropriate LSA protections to make credential theft more difficult.

Test application compatibility before broad deployment.

---

# Reduce Local Administrative Access

Credential theft commonly requires elevated access.

Reducing local administrator privileges therefore reduces opportunities for attackers to access sensitive credential material.

---

# Administrative Separation

Use separate identities for:

```text
Normal user activity
```

and:

```text
Administrative activity
```

For example:

```text
alice
```

for ordinary work and:

```text
adm-alice
```

for privileged administration.

The administrative identity should only be used from controlled systems.

---

# Restrict Privileged Logon

Prevent privileged accounts from authenticating to lower-trust systems where possible.

Conceptually:

```text
Domain Admin
      |
      X
User workstations
```

This reduces opportunities for high-value key material to become exposed.

---

# Use Protected Users Where Appropriate

Consider placing suitable high-value accounts in the Protected Users group after compatibility testing.

This can strengthen authentication behaviour and reduce exposure to legacy credential mechanisms.

---

# Authentication Policies

Use authentication policies or equivalent access restrictions to limit where high-value accounts can authenticate.

The objective is:

```text
Credential stolen
      |
      v
Attacker tries unrelated server
      |
      X
Authentication policy
```

---

# Kerberos Encryption

Prefer modern Kerberos encryption where compatibility permits.

Reduce unnecessary RC4 dependencies.

However:

```text
AES
 |
 X
Does not make stolen AES keys harmless
```

The key itself remains credential material.

---

# Password Rotation

If an NT hash or Kerberos key has been exposed:

```text
Credential material compromised
          |
          v
Rotate password
          |
          v
New key material generated
```

Also consider existing tickets and sessions as part of incident response.

---

# Least Privilege

A compromised credential should provide as little access as possible.

Review:

- domain group membership
- local administrator rights
- delegated permissions
- remote logon rights
- application access
- service permissions

---

# Network Segmentation

Restrict administrative services to controlled management networks.

For example:

```text
User Network
     |
     X
SMB / WMI / WinRM
     |
     v
Privileged Servers
```

This limits where stolen credentials can be exercised.

---

# Incident Response

If OverPass-the-Hash is suspected:

```text
Identify affected account
          |
          v
Identify credential source
          |
          v
Identify source systems
          |
          v
Review 4768 activity
          |
          v
Review 4769 activity
          |
          v
Identify accessed systems
          |
          v
Rotate credentials
          |
          v
Review existing tickets/sessions
          |
          v
Contain compromised hosts
```

---

# Reporting

The finding should describe what was actually demonstrated.

Possible titles include:

```text
Compromised NT Hash Permits Kerberos Authentication
```

```text
Reusable Kerberos Key Material Enables Authentication Without Plaintext Password
```

```text
Exposed Domain Credential Material Permits OverPass-the-Hash
```

If the root cause is credential exposure, that issue may need to be reported separately.

---

# Avoid Overstatement

Do not report:

```text
Kerberos enabled
     =
OverPass-the-Hash vulnerability
```

Kerberos requires reusable cryptographic keys by design.

The meaningful attack path is:

```text
Credential material exposed
        |
        +
Attacker can use material
        |
        +
Account has useful privileges
```

---

# Example Finding

```text
Finding:
Compromised NT Hash Permits Kerberos Authentication

Affected Account:
CORP\adminuser

Validation:
The authorised NT hash associated with the affected account was used
without knowledge of the plaintext password to request a Kerberos
Ticket Granting Ticket from the domain controller.

The resulting Kerberos credential was then used to authenticate to an
authorised server.

Impact:
An attacker who obtains the account's password-derived credential
material may authenticate as the account through Kerberos without
recovering the plaintext password and gain any access available to
that identity.

Recommendation:
Rotate the affected credential, investigate and remediate the original
credential-exposure path, strengthen privileged credential isolation,
restrict where administrative identities can authenticate, and deploy
credential-protection technologies where appropriate.
```

---

# Evidence Collection

Record:

```text
Domain
Domain controller
Account
Credential type
NT / RC4 / AES128 / AES256
Credential source
Assessment source host
TGT request timestamp
Ticket encryption type
Ticket lifetime
Target service
Target host
Authentication result
Account privileges
Tool
Command
Relevant event IDs
```

---

# Credential Redaction

Do not include complete values such as:

```text
NT hash
AES key
.ccache contents
Kirbi tickets
```

in public documentation or unnecessary report sections.

Prefer:

```text
NT hash:
[REDACTED]
```

or:

```text
AES256 key:
[REDACTED]
```

---

# Ticket Evidence

Kerberos ticket files should be treated as authentication credentials.

Examples include:

```text
.ccache
.kirbi
```

Store them:

- encrypted
- access controlled
- outside public repositories
- according to evidence-retention requirements

---

# Troubleshooting

## KDC Unreachable

Check:

```bash
nc -vz 10.10.10.10 88
```

Review:

```text
VPN
Routing
Firewall
Domain controller
```

---

# KDC_ERR_PREAUTH_FAILED

This may indicate incorrect key material.

Check:

```text
Username
Domain
NT hash
AES key
Encryption type
Account password changes
```

---

# Clock Skew

Check:

```bash
date
```

Kerberos authentication can fail when client and KDC clocks differ significantly.

---

# DNS Problems

Check:

```bash
getent hosts dc01.corp.example
```

and:

```bash
getent hosts server01.corp.example
```

Kerberos depends on correct hostname and domain resolution.

---

# Ticket Obtained but Service Access Fails

Remember:

```text
Valid TGT
     |
     X
Permission to every service
```

Possible causes include:

- insufficient account privileges
- incorrect SPN
- DNS problems
- service unavailable
- firewall
- account restrictions
- ticket-cache problems

---

# IP Address Authentication Fails

Use the service hostname where possible:

```text
server01.corp.example
```

rather than:

```text
10.10.10.25
```

Kerberos depends on SPNs associated with service names.

---

# KRB5CCNAME Not Set

Check:

```bash
echo "$KRB5CCNAME"
```

Set:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Then:

```bash
klist
```

---

# Ticket Cache Not Found

Check:

```bash
ls -lh *.ccache
```

Then set the absolute path:

```bash
export KRB5CCNAME="$(pwd)/alice.ccache"
```

---

# Wrong Domain

Kerberos realm information must correspond to the actual Active Directory domain.

Verify:

```text
corp.example
```

versus:

```text
CORP
```

The DNS domain, NetBIOS name, and Kerberos realm are related but should not be blindly treated as interchangeable strings in every tool.

---

# Credential Changed

If the password changed after the credential material was collected:

```text
Old NT hash / key
       |
       X
May no longer authenticate
```

Confirm the timeline before concluding the technique failed.

---

# Common Mistakes

## Mistake 1 - Calling OverPass-the-Hash NTLM

The defining objective is Kerberos authentication.

```text
Pass-the-Hash
     |
     +--> NTLM


OverPass-the-Hash
     |
     +--> Kerberos
```

---

## Mistake 2 - Assuming Only NT Hashes Matter

Modern Kerberos environments also use AES key material.

Think:

```text
Reusable Kerberos key
```

rather than only:

```text
NT hash
```

---

## Mistake 3 - Confusing Key Material with Tickets

Remember:

```text
Hash / AES key
       |
       v
Used to obtain ticket


Kerberos ticket
       |
       v
Used for authentication
```

---

## Mistake 4 - Confusing OverPass-the-Hash with Pass-the-Ticket

```text
OverPass-the-Hash
      =
Key -> TGT


Pass-the-Ticket
      =
Existing ticket -> Authentication
```

---

## Mistake 5 - Using IP Addresses Unnecessarily

Kerberos authentication is name and SPN oriented.

Prefer hostnames where appropriate.

---

## Mistake 6 - Ignoring Time Synchronisation

Kerberos is time-sensitive.

Always check time when troubleshooting unexpected failures.

---

## Mistake 7 - Assuming a TGT Means Administrator

A TGT authenticates an identity.

It does not change that identity's privileges.

---

## Mistake 8 - Performing Remote Execution Immediately

Obtaining the TGT may already demonstrate that the credential material is reusable.

Authenticate to the minimum required service before considering execution.

---

## Mistake 9 - Publishing Ticket Files

A `.ccache` or `.kirbi` file can contain reusable authentication material.

Treat it as a credential.

---

## Mistake 10 - Fixing Only Kerberos

The root problem is often:

```text
Credential material exposure
```

not a Kerberos configuration error.

Investigate how the NT hash or AES key became available.

---

# Assessment Checklist

## Preparation

- [ ] Confirm OverPass-the-Hash is authorised
- [ ] Confirm permitted accounts
- [ ] Confirm permitted targets
- [ ] Confirm whether remote execution is permitted
- [ ] Identify domain
- [ ] Identify domain controller
- [ ] Confirm Kerberos connectivity
- [ ] Confirm DNS
- [ ] Confirm time synchronisation

## Credential Analysis

- [ ] Identify username
- [ ] Identify domain
- [ ] Determine credential type
- [ ] Distinguish NT hash from AES key
- [ ] Identify credential source
- [ ] Record whether credential is current
- [ ] Protect credential material

## Kerberos Authentication

- [ ] Select appropriate key type
- [ ] Request TGT
- [ ] Record timestamp
- [ ] Record KDC
- [ ] Record encryption type
- [ ] Protect resulting ticket
- [ ] Verify ticket cache

## Service Validation

- [ ] Identify authorised target
- [ ] Use hostname where appropriate
- [ ] Request minimum required service access
- [ ] Record service/SPN
- [ ] Record authentication result
- [ ] Avoid unnecessary remote execution

## Privilege Analysis

- [ ] Determine account groups
- [ ] Review BloodHound
- [ ] Determine local administrator rights
- [ ] Determine remote-management rights
- [ ] Determine delegated AD permissions
- [ ] Record actual impact

## Detection

- [ ] Review Event 4768
- [ ] Review Event 4769
- [ ] Review Event 4624
- [ ] Review Event 4672
- [ ] Correlate account and source
- [ ] Review encryption type
- [ ] Review unusual source systems
- [ ] Correlate subsequent activity

## Remediation

- [ ] Rotate compromised credentials
- [ ] Investigate credential exposure
- [ ] Protect LSASS
- [ ] Deploy Credential Guard where appropriate
- [ ] Implement administrative tiering
- [ ] Restrict privileged logon locations
- [ ] Consider Protected Users
- [ ] Apply authentication restrictions
- [ ] Reduce unnecessary privileges
- [ ] Segment administrative protocols

---

# OverPass-the-Hash Testing Model

A useful mental model is:

```text
                     Credential Exposure
                            |
                            v
                    Password-Derived Key
                            |
                  +---------+---------+
                  |         |         |
                  v         v         v
               NT/RC4    AES128    AES256
                  |         |         |
                  +---------+---------+
                            |
                            v
                       Kerberos KDC
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
                     Service Ticket
                            |
                            v
                    Target Authentication
                            |
                   +--------+--------+
                   |                 |
                   v                 v
                Denied             Allowed
                                      |
                                      v
                              Privilege Analysis
                                      |
                                      v
                              Minimum Validation
```

The technique comparison model is:

```text
                 Reusable Authentication Material
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
       NT Hash        Kerberos Key      Kerberos Ticket
          |                 |                 |
          v                 v                 v
 Pass-the-Hash       OverPass-the-Hash   Pass-the-Ticket
          |                 |                 |
          v                 v                 v
        NTLM             Kerberos           Kerberos
```

The defensive model is:

```text
OverPass-the-Hash
       |
       +--> Prevent credential theft
       |       |
       |       +--> Credential Guard
       |       +--> LSA protection
       |       +--> EDR
       |
       +--> Protect privileged identities
       |       |
       |       +--> Administrative tiering
       |       +--> PAWs
       |       +--> Protected Users
       |
       +--> Restrict credential use
       |       |
       |       +--> Authentication policies
       |       +--> Network segmentation
       |       +--> Restricted logon
       |
       +--> Limit impact
       |       |
       |       +--> Least privilege
       |
       +--> Detect
               |
               +--> 4768
               +--> 4769
               +--> 4624
               +--> Source/account baselines
```

The assessment should answer:

```text
How was the credential material exposed?
        |
        v
What type of key was obtained?
        |
        v
Which identity does it represent?
        |
        v
Can it obtain a Kerberos TGT?
        |
        v
Which encryption type is used?
        |
        v
Which services can the account access?
        |
        v
What privileges does the identity possess?
        |
        v
Can defenders identify the unusual authentication?
        |
        v
Which controls would prevent credential reuse?
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

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

Password spraying:

[Password Spraying](password-spraying.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement OverPass-the-Hash and can be linked once their dedicated notes are available:

```text
active-directory/pass-the-key.md
active-directory/pass-the-ticket.md
active-directory/kerberos-tickets.md
active-directory/lateral-movement.md
active-directory/smb.md
active-directory/winrm.md
active-directory/wmi.md
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

OverPass-the-Hash demonstrates that password-derived cryptographic keys must be protected as credentials in their own right.

The critical distinctions are:

```text
Pass-the-Hash
     =
NT hash -> NTLM


OverPass-the-Hash
     =
Key material -> Kerberos TGT


Pass-the-Ticket
     =
Existing ticket -> Kerberos authentication


Kerberoasting
     =
Service ticket -> Offline password guessing


AS-REP Roasting
     =
AS-REP -> Offline password guessing
```

The fundamental attack path is:

```text
Credential exposure
      |
      v
NT hash / Kerberos key
      |
      v
Kerberos AS-REQ
      |
      v
KDC
      |
      v
TGT
      |
      v
Service ticket
      |
      v
Target authentication
      |
      v
Privilege analysis
      |
      v
Potential lateral movement
```

A mature defence breaks the path before authentication material can be reused:

```text
Protect credential material
        +
Credential Guard
        +
LSA protection
        +
Administrative isolation
        +
Restricted privileged logon
        +
Least privilege
        +
Authentication monitoring
```

The objective of an authorised OverPass-the-Hash assessment is therefore not simply to obtain a Kerberos ticket. It is to determine whether compromised password-derived key material can be converted into usable Kerberos authentication, identify the privileges associated with that identity, validate the minimum required impact, determine whether defenders can recognise the authentication path, and identify the controls necessary to prevent credential material from being exposed or reused.
