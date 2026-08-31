# NTDS.dit and Active Directory Credential Extraction

`NTDS.dit` is the primary Active Directory database file used by a writable Domain Controller.

It contains directory information for the domain, including security-sensitive material associated with domain identities.

From an offensive-security perspective, obtaining sufficient access to extract credential material from Active Directory can represent one of the highest-impact stages of a domain compromise.

The simplified model is:

```text
Domain Controller / Directory Replication
                |
                v
        Active Directory Data
                |
                v
         Credential Material
                |
                v
      Domain Account Compromise
```

Credential extraction may occur through several different mechanisms:

```text
Active Directory Credentials
        |
        +--> DCSync
        |
        +--> NTDS.dit + SYSTEM
        |
        +--> Domain Controller Backup
        |
        +--> Volume Shadow Copy
        |
        +--> IFM / Backup Artifacts
        |
        +--> Replicated Directory Data
```

These mechanisms should not be treated as identical.

The most important distinction is:

```text
DCSync
   !=
Copying NTDS.dit
```

DCSync uses Active Directory replication protocols to request credential data.

Offline NTDS extraction instead requires access to database material and the cryptographic information required to decrypt protected secrets.

!!! danger "High-impact credential access"
    Extracting credentials from a Domain Controller can expose credentials for a large part of the domain, including privileged accounts and computer accounts. During an authorised assessment, begin with permission analysis and non-destructive validation. Do not dump an entire production directory merely because tooling permits it. Collect the minimum evidence necessary to demonstrate impact and protect all resulting credential material as highly sensitive.

---

# What Is NTDS.dit?

The Active Directory Domain Services database is stored in:

```text
NTDS.dit
```

On a standard Domain Controller, the default location is commonly:

```text
C:\Windows\NTDS\NTDS.dit
```

The database is managed by:

```text
Extensible Storage Engine
```

also known as:

```text
ESE
```

or historically:

```text
JET Blue
```

---

# What Does NTDS.dit Contain?

The database contains Active Directory objects and attributes.

Conceptually:

```text
NTDS.dit
 |
 +--> Users
 |
 +--> Groups
 |
 +--> Computers
 |
 +--> Organizational Units
 |
 +--> Group Policy References
 |
 +--> Trust Information
 |
 +--> Security Descriptors
 |
 +--> Password-Related Data
 |
 +--> Kerberos Key Material
 |
 +--> Directory Metadata
```

It is therefore much more than a password database.

---

# Credential Material

Security-sensitive information associated with accounts can include:

```text
NT Password Hashes
Kerberos Keys
Password History
Supplemental Credentials
Machine Account Secrets
Trust-Related Secrets
```

depending on the extraction technique, account configuration, and available privileges.

---

# NT Hashes

Active Directory stores password-derived information rather than normal plaintext user passwords.

A commonly extracted value is the:

```text
NT Hash
```

Conceptually:

```text
User Password
     |
     v
NT Hash
     |
     v
Active Directory Credential Material
```

An NT hash can itself be security-sensitive because some authentication mechanisms can use it without recovering the original password.

See:

[Pass-the-Hash](pass-the-hash.md)

---

# Password History

Where password history is retained, historical password-derived material may also exist.

This matters because users sometimes rotate passwords predictably.

For example:

```text
Summer2025!
      |
      v
Winter2025!
      |
      v
Summer2026!
```

Historical credential material should therefore be treated as sensitive even when it is no longer the current password.

---

# Kerberos Keys

Active Directory identities may also have Kerberos key material derived from their credentials.

Depending on configuration, this can include keys associated with encryption types such as:

```text
RC4
AES128
AES256
```

This can support Kerberos authentication without knowing the original plaintext password.

See:

[Pass-the-Key](pass-the-key.md)

---

# Domain Controller Security Boundary

A writable Domain Controller holds authoritative directory information for its domain.

Conceptually:

```text
Domain Controller
       |
       v
Active Directory Database
       |
       v
Domain Identities
```

Compromise of a writable Domain Controller should therefore generally be treated as compromise of the domain security boundary.

---

# Credential Extraction Paths

Several paths may lead to Active Directory credential exposure.

```text
Credential Extraction
        |
        +--> Replication Rights
        |       |
        |       v
        |     DCSync
        |
        +--> DC Administrative Access
        |       |
        |       v
        |   NTDS Acquisition
        |
        +--> Backup Access
        |       |
        |       v
        |   Offline NTDS
        |
        +--> Exposed Backup
                |
                v
           Offline NTDS
```

---

# DCSync

DCSync abuses legitimate directory replication functionality.

Instead of directly reading:

```text
C:\Windows\NTDS\NTDS.dit
```

the requesting principal behaves like a replication partner and asks a Domain Controller for directory data.

Conceptually:

```text
Attacker
   |
   v
Directory Replication Request
   |
   v
Domain Controller
   |
   v
Credential Data
```

---

# DCSync Is Not File Access

This distinction is critical.

```text
DCSync
```

does not require:

```text
Copy NTDS.dit
```

and does not inherently require interactive login to a Domain Controller.

The critical security boundary is:

```text
Directory Replication Rights
```

---

# DCSync Rights

Important extended rights commonly associated with DCSync include:

```text
Replicating Directory Changes
Replicating Directory Changes All
```

and, for some directory data:

```text
Replicating Directory Changes In Filtered Set
```

These rights are represented through Active Directory ACLs.

---

# Replication Rights Model

```text
Principal
   |
   v
Domain ACL
   |
   v
Replication Rights
   |
   v
Directory Replication
   |
   v
Credential Material
```

A non-administrative account with these rights can therefore represent a severe attack path.

---

# Replicating Directory Changes

The extended right commonly known as:

```text
Replicating Directory Changes
```

allows replication of directory changes.

Its rights GUID is:

```text
1131f6aa-9c07-11d1-f79f-00c04fc2dcd2
```

---

# Replicating Directory Changes All

The extended right:

```text
Replicating Directory Changes All
```

is particularly important for replication of secret domain data.

Its rights GUID is:

```text
1131f6ad-9c07-11d1-f79f-00c04fc2dcd2
```

---

# Replicating Directory Changes In Filtered Set

The right:

```text
Replicating Directory Changes In Filtered Set
```

has GUID:

```text
89e95b76-444d-4c62-991a-0facbeda640c
```

This right is relevant to replication of attributes in the filtered attribute set.

---

# DCSync ACL Enumeration

Using PowerView:

```powershell
Get-DomainObjectAcl `
    -Identity 'DC=corp,DC=example' `
    -ResolveGUIDs |
    Where-Object {
        $_.ObjectAceType -match 'Replication-Get'
    }
```

Exact output depends on the PowerView version.

---

# Native PowerShell ACL Enumeration

```powershell
$domain = Get-ADDomain

$acl = Get-Acl "AD:\$($domain.DistinguishedName)"

$acl.Access |
    Select-Object `
        IdentityReference,
        ActiveDirectoryRights,
        ObjectType,
        AccessControlType,
        IsInherited
```

Look specifically for replication-related extended rights.

---

# BloodHound

BloodHound commonly represents DCSync capability using:

```text
DCSync
```

relationships.

Example:

```text
alice
 |
 v
MemberOf
 |
 v
Backup-Admins
 |
 v
DCSync
 |
 v
CORP.EXAMPLE
```

This is a high-value attack path.

---

# Validate BloodHound DCSync

Do not stop at:

```text
BloodHound Edge
```

Validate:

```text
Source Principal
      |
      v
Group Membership
      |
      v
Domain ACL
      |
      v
Replication Rights
```

This provides stronger evidence and helps identify the underlying misconfiguration.

See:

[BloodHound](bloodhound.md)

---

# Accounts That Commonly Have Replication Rights

Legitimate replication capability is normally tightly restricted.

Expected principals may include:

```text
Domain Controllers
Enterprise Domain Controllers
Administrators
Domain Admins
Enterprise Admins
```

depending on the exact operation and domain configuration.

Additional applications may legitimately receive replication permissions, but such delegation should be carefully reviewed.

---

# Dangerous Delegation

A configuration such as:

```text
Backup-Service
      |
      v
Replicating Directory Changes
+
Replicating Directory Changes All
```

may allow the account to request sensitive directory credential material.

The account does not need to be visibly present in:

```text
Domain Admins
```

for the resulting impact to be severe.

---

# DCSync and Nested Groups

Always resolve nested membership.

```text
User
 |
 v
Group A
 |
 v
Group B
 |
 v
Replication Rights
```

A user may inherit effective DCSync capability through several group relationships.

See:

[Active Directory Groups](groups.md)

---

# DCSync and ACL Abuse

A principal may not initially possess replication rights but may have:

```text
WriteDACL
```

over the domain object.

Conceptually:

```text
Attacker
   |
   v
WriteDACL on Domain
   |
   v
Grant Replication Rights
   |
   v
DCSync
```

This represents an indirect path to domain credential access.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# DCSync and WriteOwner

Another potential chain is:

```text
WriteOwner
    |
    v
Ownership
    |
    v
DACL Modification
    |
    v
Replication Rights
    |
    v
DCSync
```

This involves multiple directory changes and should not be actively validated unless specifically authorised.

---

# DCSync with Impacket

Impacket's:

```text
secretsdump.py
```

supports Active Directory credential extraction workflows.

Modern package installations commonly expose the command as:

```bash
impacket-secretsdump
```

Check the installed version first:

```bash
impacket-secretsdump -h
```

---

# Targeted DCSync

For authorised validation, prefer requesting one specifically approved test account rather than extracting the entire domain.

A typical Impacket workflow can use:

```text
-just-dc-user
```

to restrict extraction to a particular directory principal.

Conceptual example:

```bash
impacket-secretsdump \
    -just-dc-user 'test-user' \
    'corp.example/audit-user@dc01.corp.example'
```

The tool will request authentication material according to the supplied authentication method.

Use a dedicated assessment identity and avoid placing passwords directly in shell history where possible.

---

# Why Targeted Extraction Is Better

Compare:

```text
Full Domain Dump
      |
      v
Thousands of Credentials
```

with:

```text
Approved Test User
      |
      v
Single Credential Record
```

If both demonstrate the same privilege boundary, the second approach provides adequate evidence with substantially less credential exposure.

---

# Full DCSync

Impacket can also request broader directory credential data.

A commonly used option is:

```text
-just-dc
```

This can expose substantial domain credential material.

Do not use broad extraction merely to prove that replication rights exist.

---

# secretsdump Authentication Options

Depending on the environment and installed Impacket version, authentication may involve:

```text
Password
NT Hash
Kerberos Ticket
Kerberos Key
```

Review:

```bash
impacket-secretsdump -h
```

before using version-specific options.

See:

[Impacket](impacket.md)

---

# DCSync with NetExec

NetExec can interact with Domain Controllers and may provide credential-extraction workflows depending on protocol, privilege, and installed version.

Check:

```bash
nxc smb --help
```

and:

```bash
nxc ldap --help
```

before relying on syntax from older CrackMapExec documentation.

For a production assessment, targeted replication validation is preferable to broad credential dumping.

See:

[NetExec](netexec.md)

---

# Mimikatz DCSync

Mimikatz includes DCSync functionality through:

```text
lsadump::dcsync
```

Conceptually:

```text
mimikatz
   |
   v
DRS Replication
   |
   v
Domain Controller
   |
   v
Requested Account Secret
```

A targeted example frequently seen in controlled labs is:

```text
lsadump::dcsync /domain:corp.example /user:CORP\test-user
```

Because this retrieves credential material, use it only where explicitly authorised.

---

# DRSUAPI

DCSync commonly interacts with the Active Directory replication protocol through:

```text
Directory Replication Service Remote Protocol
```

often referred to as:

```text
DRSUAPI
```

This is legitimate Domain Controller functionality.

The attack abuses permission to perform replication rather than exploiting a software vulnerability.

---

# Important Security Principle

```text
DCSync Capability
      |
      X
Software Vulnerability
```

Instead:

```text
DCSync Capability
      |
      v
Privilege / ACL Configuration
```

This distinction matters when writing findings.

---

# NTDS.dit Offline Extraction

Another credential-access path involves obtaining:

```text
NTDS.dit
```

and the cryptographic material required to process protected secrets.

Conceptually:

```text
NTDS.dit
   +
SYSTEM Hive
   |
   v
Offline Processing
   |
   v
Credential Material
```

---

# Why SYSTEM Is Important

Sensitive values inside the Active Directory database are protected using keys ultimately related to information in the:

```text
SYSTEM
```

registry hive.

Therefore simply copying:

```text
NTDS.dit
```

is not generally sufficient for offline password-hash extraction.

The simplified model is:

```text
SYSTEM
  |
  v
Boot Key
  |
  v
Directory Secret Protection
  |
  v
NTDS Credential Data
```

---

# Boot Key

The Windows boot key is often referred to as:

```text
SysKey
```

or:

```text
BootKey
```

in security tooling and documentation.

It is derived from information in the SYSTEM registry hive and participates in protecting local and directory secrets.

---

# Offline Extraction Requirements

A common offline workflow requires:

```text
NTDS.dit
+
SYSTEM
```

Additional artifacts may be useful depending on the objective.

For example:

```text
SECURITY
```

may contain other Windows security information but is not the primary requirement for decrypting NTDS password hashes.

---

# NTDS File Locking

On a running Domain Controller:

```text
NTDS.dit
```

is actively used by Active Directory Domain Services.

Normal file copying may therefore fail.

Legitimate administrative mechanisms can create consistent copies.

These include:

```text
Volume Shadow Copy
Windows Server Backup
Install From Media
System State Backup
```

---

# Volume Shadow Copy

Volume Shadow Copy Service can create point-in-time snapshots of volumes.

Conceptually:

```text
Live Volume
    |
    v
VSS Snapshot
    |
    v
Consistent NTDS Copy
```

Administrative access is required.

Creating snapshots changes system state and may consume disk space, so it should not be performed casually during an assessment.

---

# ntdsutil

Windows includes:

```text
ntdsutil.exe
```

for Active Directory database administration.

One legitimate feature is:

```text
Install From Media
```

commonly abbreviated:

```text
IFM
```

IFM can produce directory installation media containing Active Directory database material.

---

# IFM

Conceptually:

```text
ntdsutil
   |
   v
IFM
   |
   v
Directory Database Copy
+
Registry Material
```

These files are extremely sensitive.

Creating IFM media during a penetration test is a high-impact action and generally unnecessary unless specifically authorised.

---

# System State Backups

Domain Controller system-state backups may contain:

```text
Active Directory Database
Registry
Boot Files
SYSVOL
Other Critical System State
```

A poorly protected backup can therefore represent an alternative route to domain credential compromise.

---

# Backup Security

The security model is:

```text
Domain Controller
      |
      v
Backup
      |
      v
Contains Sensitive Domain Data
```

Therefore:

```text
Backup Administrator
```

or:

```text
Backup Repository Compromise
```

may become equivalent to a high-impact directory compromise.

---

# Backup Infrastructure Attack Path

```text
Attacker
   |
   v
Backup Server
   |
   v
Domain Controller Backup
   |
   v
NTDS + SYSTEM
   |
   v
Offline Credential Extraction
```

This is why backup infrastructure should be treated as a highly privileged security tier.

---

# Offline secretsdump

If authorised NTDS and SYSTEM files have already been obtained, Impacket can process them offline.

Conceptually:

```bash
impacket-secretsdump \
    -ntds ntds.dit \
    -system SYSTEM \
    LOCAL
```

This performs local processing of the supplied files rather than contacting a Domain Controller for DCSync.

Only use approved copies of directory data.

---

# Offline vs Remote secretsdump

These are different workflows.

## Remote / Replication

```text
secretsdump
   |
   v
Domain Controller
   |
   v
Replication / Remote Collection
```

## Offline

```text
NTDS.dit + SYSTEM
        |
        v
secretsdump
        |
        v
Offline Credential Processing
```

Do not describe both simply as:

```text
Dumping NTDS
```

when reporting evidence.

---

# Output Structure

Credential-extraction tools may display records conceptually similar to:

```text
domain\username:RID:LM_HASH:NT_HASH:::
```

Modern environments commonly show the historical empty LM value when LM hashes are not stored.

Do not place real credential material in documentation, screenshots, tickets, chat systems, or reports.

---

# RID

Each security principal has a:

```text
Relative Identifier
```

or:

```text
RID
```

as part of its SID.

Example conceptual SID:

```text
S-1-5-21-111111111-222222222-333333333-1105
```

where:

```text
1105
```

is the RID.

---

# High-Value RIDs

Some well-known domain accounts use familiar RIDs.

For example:

```text
Administrator -> 500
Guest         -> 501
krbtgt        -> 502
```

Do not use RID alone to determine privilege.

Renaming an account does not change its SID.

---

# krbtgt

The:

```text
krbtgt
```

account is particularly sensitive.

Its key material is used by the Kerberos Key Distribution Center for Ticket Granting Ticket protection.

Conceptually:

```text
krbtgt Key
    |
    v
TGT Cryptographic Trust
```

Compromise of this material can enable ticket-forging attacks.

---

# Golden Ticket Relationship

```text
krbtgt Credential Material
          |
          v
Forge TGT
          |
          v
Golden Ticket
```

Therefore extraction of:

```text
krbtgt
```

material is significantly more impactful than obtaining an ordinary user hash.

A dedicated persistence page should cover Golden Tickets separately.

---

# Do Not Extract krbtgt by Default

If the assessment objective is simply:

```text
Prove DCSync
```

requesting:

```text
krbtgt
```

is usually unnecessary.

Prefer:

```text
Dedicated Test Account
```

unless the rules of engagement specifically require validation of domain-level credential compromise.

---

# Domain Administrator Credentials

Similarly:

```text
Domain Admin
```

credential extraction is generally unnecessary if a controlled account can demonstrate the same replication privilege.

The testing principle is:

```text
Minimum Credential Exposure
```

---

# Computer Account Hashes

NTDS extraction can also expose computer-account credential material.

Example:

```text
SERVER01$
```

Computer accounts are real domain security principals.

Their credentials can matter for:

```text
Kerberos
NTLM
RBCD
Service Authentication
Directory Access
Machine-to-Machine Trust
```

---

# Domain Controller Computer Accounts

Domain Controller machine accounts are particularly sensitive because they participate in domain infrastructure and replication.

Example:

```text
DC01$
```

Credential material associated with a Domain Controller should be handled as Tier 0 data.

---

# Trust Accounts

Active Directory trust relationships also rely on secret material.

Directory credential extraction may expose trust-related information depending on the technique and requested data.

This can affect:

```text
Parent / Child Trusts
Forest Trusts
External Trusts
```

A dedicated trust section should analyse these relationships separately.

---

# Supplemental Credentials

Active Directory may store additional credential representations used for authentication.

These are often referred to broadly as:

```text
Supplemental Credentials
```

They may include Kerberos key information and other authentication-related data.

Their exact availability depends on account state and domain configuration.

---

# Reversible Encryption

Some accounts may be configured to store passwords using reversible encryption.

This is unusual and should be reviewed carefully.

Conceptually:

```text
Store Password Using Reversible Encryption
               |
               v
Higher Credential Exposure Risk
```

Do not assume this setting means the password is stored as a simple plaintext field inside NTDS.

---

# Password History Risk

Historical hashes can reveal password patterns.

Example:

```text
Current:
BlueTeam2026!

History:
BlueTeam2025!
BlueTeam2024!
```

Even if the current password is strong enough to resist immediate cracking, historical patterns can reveal organisational password conventions.

---

# Credential Cracking

Offline password cracking may be possible against extracted password hashes.

This should be explicitly authorised because:

```text
Credential Dump
      |
      v
Password Cracking
```

creates additional sensitive information.

Where password-strength assessment is in scope, use controlled handling procedures and avoid unnecessary recovery of real user passwords.

---

# NTDS and Pass-the-Hash

An extracted NT hash may potentially be used directly for NTLM authentication.

```text
NTDS
 |
 v
NT Hash
 |
 v
Pass-the-Hash
```

See:

[Pass-the-Hash](pass-the-hash.md)

---

# NTDS and Pass-the-Key

Kerberos keys obtained from directory credential material may support key-based Kerberos authentication.

```text
NTDS
 |
 v
Kerberos Key
 |
 v
Pass-the-Key
```

See:

[Pass-the-Key](pass-the-key.md)

---

# NTDS and OverPass-the-Hash

Depending on the available credential material and environment:

```text
NT Hash
   |
   v
Kerberos Authentication
```

may be possible through OverPass-the-Hash style workflows.

See:

[OverPass-the-Hash](overpass-the-hash.md)

---

# NTDS and Pass-the-Ticket

Credential extraction can ultimately lead to Kerberos ticket acquisition.

```text
Credential Material
      |
      v
Kerberos Authentication
      |
      v
TGT / TGS
      |
      v
Pass-the-Ticket
```

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# NTDS and Lateral Movement

Credential material should not automatically be used against every reachable system.

Instead:

```text
Credential
   |
   v
Determine Privilege
   |
   v
Select Approved Target
   |
   v
Minimal Validation
```

A later lateral-movement section should cover remote administration techniques separately.

---

# NTDS and gMSA

gMSAs use managed password mechanisms and their credentials may also become security-relevant during domain credential compromise.

See:

[Group Managed Service Accounts](gmsa.md)

The normal gMSA attack path is different:

```text
Read msDS-ManagedPassword
```

rather than:

```text
Extract NTDS
```

---

# NTDS and LAPS

LAPS credentials are associated with managed local administrator passwords rather than normal domain-account password hashes.

Their storage and protection model differs from ordinary NTDS credential extraction.

See:

[Active Directory LAPS](laps.md)

---

# NTDS and Shadow Credentials

Shadow Credentials adds alternative authentication material to:

```text
msDS-KeyCredentialLink
```

It does not require dumping NTDS.

See:

[Active Directory Shadow Credentials](shadow-credentials.md)

---

# NTDS and AD CS

Certificate-based authentication may provide alternative ways to impersonate domain identities without obtaining NT hashes.

Therefore:

```text
Credential Access
```

in Active Directory is broader than:

```text
NTDS Dumping
```

A later AD CS section should cover certificate-based attack paths separately.

---

# Read-Only DCSync Assessment

Before retrieving credentials, determine whether the principal has the required ACLs.

Workflow:

```text
Enumerate Domain ACL
      |
      v
Identify Replication Rights
      |
      v
Resolve Principal
      |
      v
Determine Whether Rights Are Legitimate
      |
      v
Report / Validate
```

This may be sufficient for many assessments.

---

# Safe DCSync Validation

If proof is required:

```text
Dedicated Test User
      |
      v
Targeted Replication Request
      |
      v
Single Credential Record
      |
      v
Evidence
      |
      v
Stop
```

Avoid:

```text
Entire Domain
```

unless explicitly required.

---

# DCSync Test Account

A dedicated account can be created by the organisation for testing.

Example:

```text
PT-DCSYNC-TEST
```

The assessment can request only that account's credential material.

This demonstrates:

```text
Replication Capability
```

without unnecessarily exposing real user credentials.

---

# DCSync Evidence

Good evidence includes:

```text
Source Principal
Domain
Replication Rights
Target Test Account
Successful Replication
Timestamp
Domain Controller
Tool
Relevant Logs
```

Redact:

```text
NT Hash
AES Key
Password
Ticket
```

---

# Offline NTDS Validation

If backup exposure is the finding, it may not be necessary to extract all credentials.

A safer model is:

```text
Locate Backup
     |
     v
Confirm NTDS + SYSTEM Present
     |
     v
Confirm Read Access
     |
     v
Document Exposure
```

This can be sufficient to demonstrate impact.

---

# Proof Without Credential Dumping

For example:

```text
Finding:
Unauthorised User Can Read Domain Controller Backup
```

Evidence may include:

```text
Backup Path
File Names
File Sizes
ACL
Read Permission
NTDS Presence
SYSTEM Presence
```

without processing the database.

---

# Detection - DCSync

DCSync is fundamentally a replication operation.

Useful defensive telemetry may include:

```text
Directory Service Access
Replication Activity
Network Traffic to Domain Controllers
Unexpected Replication Sources
ACL Changes
```

---

# Event 4662

Event:

```text
4662
```

can record operations performed on Active Directory objects where appropriate auditing and SACLs are configured.

This is one of the key events commonly used for DCSync detection.

---

# Replication GUID Monitoring

Detection logic may look for access involving replication extended rights such as:

```text
1131f6aa-9c07-11d1-f79f-00c04fc2dcd2
```

and:

```text
1131f6ad-9c07-11d1-f79f-00c04fc2dcd2
```

with careful environment-specific tuning.

---

# Expected Replication Sources

A strong detection model is:

```text
Replication Request
      |
      v
Source Host
      |
      v
Is Domain Controller?
```

Unexpected replication activity originating from:

```text
Workstation
Member Server
Jump Host
Application Server
```

should receive scrutiny.

---

# Network Detection

DCSync uses legitimate Active Directory replication protocols.

Network monitoring can therefore look for:

```text
DRSUAPI
RPC
Domain Controller Traffic
```

originating from unexpected systems.

---

# DCSync Detection Model

```text
Non-DC Host
    |
    v
DRSUAPI
    |
    v
Domain Controller
    |
    v
Replication Request
```

This is often more meaningful than merely detecting a particular offensive tool.

---

# Detect the Behaviour, Not the Tool

Avoid detection strategies based solely on:

```text
secretsdump.exe
mimikatz.exe
```

Attackers can use different implementations.

Prefer:

```text
Replication Rights Usage
Unexpected Replication Source
Directory Object Access
```

---

# Event 5136

Changes to Active Directory ACLs may generate:

```text
5136
```

when Directory Service Changes auditing is configured.

This can help detect:

```text
Grant DCSync Rights
```

before the actual replication occurs.

---

# DCSync Persistence

An attacker may grant replication rights to an innocuous-looking principal.

```text
Compromised Admin
      |
      v
Modify Domain ACL
      |
      v
Service Account Gets DCSync
      |
      v
Persistent Credential Access
```

Therefore defenders should periodically review domain-root ACLs.

---

# Monitor Domain ACL

Particularly review:

```text
ExtendedRight
GenericAll
WriteDACL
WriteOwner
```

on:

```text
Domain Root
```

Unexpected replication rights should be investigated immediately.

---

# Detect NTDS File Access

Direct NTDS acquisition may produce different telemetry.

Potential signals include:

```text
VSS Activity
ntdsutil Execution
Backup Operations
Registry Hive Export
NTDS File Access
Temporary Database Copies
Archive Creation
Large File Transfers
```

---

# Volume Shadow Copy Detection

Monitor unexpected use of tools or interfaces that create shadow copies.

Potential administrative tools include:

```text
vssadmin
diskshadow
wmic
PowerShell / WMI
Backup APIs
```

Do not alert on command names alone.

Legitimate backup software commonly interacts with VSS.

---

# ntdsutil Detection

Unexpected execution of:

```text
ntdsutil.exe
```

on a Domain Controller deserves investigation.

However, it is a legitimate administrative tool.

Context matters:

```text
Who Ran It?
When?
Which Arguments?
Was Maintenance Scheduled?
What Files Were Created?
```

---

# Registry Hive Access

Offline NTDS processing commonly requires:

```text
SYSTEM
```

Monitor suspicious registry hive export or backup activity on Domain Controllers.

---

# File Creation

Potential suspicious locations include temporary or staging directories containing files named similar to:

```text
ntds.dit
SYSTEM
SECURITY
SAM
```

Names can be changed, so behavioural context is more reliable than filenames alone.

---

# Exfiltration Detection

A credential dump may be compressed before transfer.

Potential signals include:

```text
NTDS Copy
      |
      v
Archive
      |
      v
Network Transfer
```

Monitor unusual large outbound transfers from Domain Controllers and backup infrastructure.

---

# Domain Controller EDR

Where organisational policy permits, Domain Controllers should have appropriate endpoint detection capabilities capable of monitoring:

```text
Process Creation
File Access
Registry Access
Network Connections
PowerShell
Credential Access
```

without destabilising critical directory services.

---

# Backup Monitoring

Monitor:

```text
Who Reads DC Backups?
Who Exports Them?
Where Are They Copied?
Who Can Restore Them?
```

Backup systems frequently provide an overlooked path to Active Directory credential data.

---

# Detection Correlation

A high-confidence chain may look like:

```text
ACL Modification
      |
      v
Replication Right Granted
      |
      v
Unexpected DRSUAPI Request
      |
      v
Credential Use
      |
      v
Lateral Movement
```

Another chain:

```text
Admin Logon to DC
      |
      v
VSS / IFM Activity
      |
      v
NTDS Copy
      |
      v
Archive Creation
      |
      v
Outbound Transfer
```

---

# Hardening

The primary defensive objective is:

```text
Prevent Unauthorised Access
to Domain Credential Material
```

This requires more than protecting:

```text
NTDS.dit
```

---

# Protect Replication Rights

Review who has:

```text
Replicating Directory Changes
Replicating Directory Changes All
Replicating Directory Changes In Filtered Set
```

Remove unnecessary delegation.

---

# Protect Domain ACL

Because:

```text
WriteDACL
```

over the domain root can potentially become:

```text
DCSync
```

protect ACL modification rights carefully.

---

# Protect Domain Controllers

Apply strong controls to Domain Controllers:

```text
Dedicated Administration
Tier 0 Isolation
Restricted Interactive Logon
Patching
Application Control
EDR
Firewalling
Credential Guard Where Applicable
Secure Backup
Audit Logging
```

---

# Administrative Tiering

Avoid:

```text
Normal Workstation
      |
      v
Domain Admin Logon
```

A compromised workstation with cached or active privileged credentials can become a path to Domain Controller compromise.

---

# Dedicated Administration

Use dedicated administrative workstations or equivalent privileged-access architectures for Tier 0 administration.

The goal is:

```text
Internet / Email Workstation
           |
           X
      Tier 0 Credentials
```

---

# Restrict Domain Controller Logon

Only principals with a genuine operational requirement should be able to log on to Domain Controllers.

Review:

```text
RDP
WinRM
SMB Administration
Console Access
Service Logon
Scheduled Tasks
```

---

# Protect Backup Infrastructure

Treat Domain Controller backups as:

```text
Tier 0 Assets
```

because:

```text
DC Backup
   |
   v
NTDS + SYSTEM
   |
   v
Domain Credential Material
```

---

# Encrypt Backups

Where supported:

```text
Encrypt Backups
```

and protect the corresponding encryption keys separately.

Encryption does not help if the same compromised administrator can access both:

```text
Backup
+
Decryption Key
```

---

# Restrict Backup Operators

Review membership and delegated privileges associated with:

```text
Backup Operators
```

and backup-service identities.

Do not assume a backup account is low-risk merely because it is not a Domain Admin.

---

# gMSA for Backup Services

Where supported, managed service accounts may reduce the risks associated with static service-account passwords.

See:

[Group Managed Service Accounts](gmsa.md)

The backup account's privileges must still be minimised.

---

# Monitor Replication Rights

Periodically inventory principals capable of DCSync.

A useful review model is:

```text
Principal
 |
 v
Replication Rights
 |
 v
Business Justification
```

Any unexplained entry should be investigated.

---

# Monitor Domain ACL Drift

Compare domain ACLs against an approved baseline.

This can identify:

```text
New Replication Rights
Unexpected WriteDACL
Unexpected GenericAll
Unexpected Ownership
```

---

# Protect krbtgt

Credential exposure involving:

```text
krbtgt
```

requires special incident-response handling.

Changing the `krbtgt` password affects Kerberos trust and should follow Microsoft-supported recovery procedures.

Do not casually reset it during a penetration test.

---

# krbtgt Double Reset

Following a confirmed domain compromise, incident-response procedures may require changing the `krbtgt` password twice with appropriate replication and operational considerations.

This invalidates key material associated with both the current and previous `krbtgt` passwords.

This is an incident-response action, not a penetration-testing cleanup step.

---

# Credential Rotation After NTDS Exposure

If the entire directory credential database was exposed, remediation cannot be limited to:

```text
Change One Password
```

Potentially exposed material may include:

```text
Users
Administrators
Service Accounts
Computer Accounts
krbtgt
Trust Secrets
Historical Password Material
```

A coordinated domain-recovery process may be required.

---

# Incident Response - DCSync

If unauthorised DCSync is suspected:

```text
Identify Source
      |
      v
Identify Replicated Accounts
      |
      v
Identify How Replication Rights Were Obtained
      |
      v
Remove Unauthorised Rights
      |
      v
Contain Source Principal
      |
      v
Assess Credential Exposure
      |
      v
Rotate Credentials
      |
      v
Investigate Downstream Use
```

---

# Incident Response - NTDS Theft

If:

```text
NTDS.dit + SYSTEM
```

were exfiltrated:

```text
Assume Offline Credential Exposure
```

because an attacker can continue processing the data after containment.

---

# Offline Exposure Is Persistent

```text
Attacker Copies NTDS
       |
       v
Organisation Removes Access
       |
       X
Attacker Loses Copy
```

Once the database has been exfiltrated, credential rotation becomes essential.

---

# Determine Snapshot Time

For an exposed backup or database copy, establish:

```text
When Was the Snapshot Created?
```

This determines which credential versions were potentially exposed.

---

# Password Changes After Snapshot

Suppose:

```text
NTDS Backup: January
Password Changed: March
Compromise Found: April
```

The January backup may contain:

```text
January Credential Material
```

Password history and password reuse can still make this relevant.

---

# Investigate Hash Reuse

If an old NT hash was exposed and the same password remained in use elsewhere, the compromise may extend beyond the snapshot date.

Avoid automatically cracking credentials unless authorised; use identity and password-reset history where possible.

---

# Purple Team Exercise

A controlled DCSync exercise can validate:

```text
Replication Detection
Domain Controller Network Monitoring
Directory Auditing
Identity Correlation
Incident Response
```

Prefer a dedicated test account.

---

# Purple Team DCSync Model

```text
Test Principal
      |
      v
Temporary Replication Permission
      |
      v
Request Test Account
      |
      v
Defender Detection
      |
      v
Remove Permission
```

Only use temporary replication rights where the exercise explicitly authorises directory ACL changes.

A safer alternative is to use an existing controlled lab domain.

---

# Purple Team Questions

Defenders should be able to answer:

```text
Which account initiated replication?

Which host initiated it?

Was the host a Domain Controller?

Which directory rights enabled it?

Which accounts were requested?

Was the source expected?

Were replication rights recently changed?

Was credential material subsequently used?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect unexpected replication
Time to identify source principal
Time to identify source host
Time to identify replication-right change
Time to contain the principal
Time to assess credential exposure
Time to begin credential rotation
```

---

# Reporting DCSync

A strong finding title might be:

```text
Service Account Has Active Directory Replication Rights
```

or:

```text
Low-Privilege Principal Can Perform DCSync
```

Avoid simply:

```text
DCSync Vulnerability
```

because the underlying issue is normally excessive directory permission.

---

# Example Finding - DCSync

```text
Finding:
Service Account Can Replicate Domain Credential Data

Source Principal:
CORP\svc-backup

Affected Domain:
corp.example

Description:
The svc-backup account has Active Directory replication permissions on
the domain root.

The effective permissions include the rights required to request
sensitive directory replication data from a Domain Controller.

The account is not intended to perform Active Directory replication.

During the authorised assessment, the permission was validated using a
single dedicated test account. No broad domain credential dump was
performed.

Impact:
Compromise of svc-backup could allow an attacker to request
password-derived credential material for domain identities.

Depending on the accounts requested, this could result in compromise
of privileged users and potentially the entire domain.

Recommendation:
Remove unnecessary replication rights from svc-backup.

Review the domain root ACL for other non-Domain Controller principals
with replication permissions.

Investigate why the rights were originally delegated and replace them
with the minimum permissions required for the service.

Monitor replication requests originating from systems that are not
Domain Controllers.
```

---

# Reporting Backup Exposure

A strong finding title might be:

```text
Domain Controller Backup Accessible to Non-Privileged Users
```

---

# Example Finding - NTDS Backup Exposure

```text
Finding:
Domain Controller Backup Accessible to Non-Privileged Users

Location:
\\backup01\archives\dc01\

Description:
A backup of the Domain Controller is accessible to a user group that
does not require access to Active Directory backup material.

The backup contains the Active Directory database and SYSTEM registry
data required for offline processing of protected directory
credentials.

No credential extraction was performed because file access alone was
sufficient to demonstrate the exposure.

Impact:
An attacker who compromises a member of the affected group could copy
the Domain Controller backup and process it offline.

This could expose password-derived credential material for domain
users, computers, service accounts, and privileged identities.

Because offline processing can continue after access is revoked, the
impact may persist until affected credentials are rotated.

Recommendation:
Restrict access to Domain Controller backups to explicitly authorised
Tier 0 backup and recovery personnel and services.

Review backup-server administrators, service accounts, share
permissions, NTFS permissions, and backup-management permissions.

Encrypt backup data and protect encryption keys separately.

Monitor access and export activity involving Domain Controller
backups.
```

---

# Reporting NTDS Extraction

If actual database extraction occurred during an authorised test, record:

```text
Method
Source
Database Timestamp
Files Accessed
Accounts Extracted
Number of Credentials
Storage Location
Deletion / Cleanup
```

Do not include reusable credential values in the final report.

---

# Severity

Severity depends on the actual exposure.

Example:

```text
Read Access to Old Test DC Backup
          |
          v
Limited Test Credentials
```

may have lower impact.

Compare:

```text
Low-Privilege User
       |
       v
DCSync
       |
       v
Current Production Domain
       |
       v
Privileged Credential Material
```

which is generally critical.

---

# DCSync Severity Model

```text
Replication Rights
      +
Current Domain
      +
Sensitive Accounts
      +
Low-Privilege Source
      =
Very High Risk
```

---

# Backup Exposure Severity Model

```text
Backup Read Access
      +
NTDS
      +
SYSTEM
      +
Current Credentials
      =
Domain Credential Exposure
```

---

# Do Not Overstate Findings

Finding:

```text
User Can Read Backup Directory
```

does not automatically prove:

```text
All Domain Credentials Compromised
```

Verify:

```text
Does Backup Contain NTDS?

Is SYSTEM Present?

Is Backup Current?

Can Files Actually Be Read?

Is Encryption Applied?
```

Similarly:

```text
Replication-Related ACE
```

does not automatically prove:

```text
Successful DCSync
```

Validate effective permissions and the exact rights involved.

---

# Evidence Handling

NTDS-derived data should be treated as:

```text
Highly Sensitive
```

Store it only in:

```text
Approved Encrypted Assessment Storage
```

Do not:

```text
Email It
Upload It to Public Services
Commit It to Git
Paste It into Tickets
Store It in Screenshots
Leave It on Shared Hosts
```

---

# Git Warning

Never run:

```bash
git add .
```

in a directory containing:

```text
ntds.dit
SYSTEM
secretsdump output
hash files
Kerberos tickets
PFX files
```

without first verifying exactly what will be committed.

Use:

```bash
git status
```

and appropriate `.gitignore` rules.

---

# Suggested Sensitive Artifact Patterns

For assessment workspaces, consider excluding patterns such as:

```text
*.dit
*.ccache
*.kirbi
*.pfx
*.key
*.pem
```

and dedicated credential-output directories.

Do not rely on `.gitignore` as the only credential-protection mechanism.

---

# NTDS Assessment Checklist

## Preparation

- [ ] Confirm credential-access testing is authorised
- [ ] Confirm DCSync testing restrictions
- [ ] Confirm Domain Controller access restrictions
- [ ] Confirm backup testing restrictions
- [ ] Confirm credential cracking restrictions
- [ ] Prepare encrypted evidence storage
- [ ] Define credential-redaction process
- [ ] Define secure cleanup procedure

## Domain Enumeration

- [ ] Identify domain
- [ ] Identify Domain Controllers
- [ ] Identify writable Domain Controllers
- [ ] Identify RODCs
- [ ] Identify domain functional level
- [ ] Identify privileged groups
- [ ] Identify backup infrastructure
- [ ] Identify replication-related service accounts

## Replication Rights

- [ ] Review domain-root ACL
- [ ] Identify Replicating Directory Changes
- [ ] Identify Replicating Directory Changes All
- [ ] Identify Replicating Directory Changes In Filtered Set
- [ ] Resolve principal SIDs
- [ ] Resolve nested groups
- [ ] Identify non-DC principals
- [ ] Review GenericAll
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Validate BloodHound DCSync edges

## DCSync Validation

- [ ] Prefer ACL evidence first
- [ ] Use dedicated test account
- [ ] Use targeted extraction
- [ ] Avoid full-domain extraction
- [ ] Avoid `krbtgt` unless required
- [ ] Avoid Domain Admin credentials unless required
- [ ] Record Domain Controller used
- [ ] Record source principal
- [ ] Redact returned credentials
- [ ] Stop when impact is demonstrated

## NTDS File Exposure

- [ ] Identify NTDS location
- [ ] Identify accessible backups
- [ ] Identify IFM media
- [ ] Identify system-state backups
- [ ] Identify VSS snapshots where relevant
- [ ] Identify SYSTEM hive availability
- [ ] Review backup ACLs
- [ ] Review share permissions
- [ ] Review backup administrators
- [ ] Review backup service accounts
- [ ] Determine backup age
- [ ] Determine encryption status

## Offline Processing

- [ ] Confirm processing is authorised
- [ ] Copy only required files
- [ ] Use encrypted workspace
- [ ] Avoid extracting unnecessary accounts
- [ ] Avoid password cracking unless authorised
- [ ] Record exact source
- [ ] Record snapshot date
- [ ] Secure tool output
- [ ] Delete temporary copies after assessment

## Credential Analysis

- [ ] Identify NT hashes
- [ ] Identify Kerberos keys where relevant
- [ ] Identify password history only if authorised
- [ ] Identify computer-account material
- [ ] Identify privileged identities
- [ ] Identify `krbtgt` exposure
- [ ] Identify trust-related exposure
- [ ] Avoid unnecessary credential use

## Detection

- [ ] Monitor event 4662
- [ ] Monitor replication extended rights
- [ ] Monitor unexpected DRSUAPI sources
- [ ] Monitor non-DC replication traffic
- [ ] Monitor event 5136 for ACL changes
- [ ] Monitor VSS activity
- [ ] Monitor `ntdsutil`
- [ ] Monitor registry hive export
- [ ] Monitor suspicious NTDS copies
- [ ] Monitor archive creation
- [ ] Monitor outbound transfers
- [ ] Monitor backup access

## Hardening

- [ ] Restrict replication rights
- [ ] Review domain-root ACL
- [ ] Remove stale DCSync delegation
- [ ] Protect Domain Controllers
- [ ] Apply Tier 0 administration
- [ ] Restrict DC logon
- [ ] Protect backup infrastructure
- [ ] Encrypt backups
- [ ] Protect backup encryption keys
- [ ] Review Backup Operators
- [ ] Review backup service accounts
- [ ] Monitor ACL drift
- [ ] Monitor replication behaviour

## Incident Response

- [ ] Identify DCSync source
- [ ] Identify replicated accounts
- [ ] Identify source host
- [ ] Identify source principal
- [ ] Remove unauthorised replication rights
- [ ] Investigate ACL changes
- [ ] Determine whether NTDS was copied
- [ ] Determine whether SYSTEM was copied
- [ ] Determine snapshot date
- [ ] Assess credential exposure
- [ ] Rotate affected credentials
- [ ] Review `krbtgt`
- [ ] Review trust secrets
- [ ] Investigate downstream authentication
- [ ] Investigate lateral movement
- [ ] Preserve forensic evidence

## Cleanup

- [ ] Delete temporary NTDS copies
- [ ] Delete temporary registry hives
- [ ] Delete secretsdump output
- [ ] Delete temporary hash files
- [ ] Delete temporary tickets
- [ ] Remove temporary shares
- [ ] Remove temporary snapshots if created and authorised
- [ ] Verify no ACL changes remain
- [ ] Verify secure evidence retention
- [ ] Document cleanup

---

# NTDS Testing Model

The Active Directory database model is:

```text
Domain Controller
      |
      v
NTDS.dit
      |
      v
Directory Objects
      |
      v
Credential Material
```

The offline extraction model is:

```text
NTDS.dit
   +
SYSTEM
   |
   v
Boot Key
   |
   v
Protected Directory Secrets
   |
   v
Credential Material
```

The DCSync model is:

```text
Principal
   |
   v
Replication Rights
   |
   v
DRSUAPI
   |
   v
Domain Controller
   |
   v
Credential Data
```

The ACL attack model is:

```text
Attacker
   |
   v
WriteDACL
   |
   v
Grant Replication Rights
   |
   v
DCSync
```

The backup attack model is:

```text
Compromise Backup Infrastructure
          |
          v
Domain Controller Backup
          |
          v
NTDS + SYSTEM
          |
          v
Offline Credential Extraction
```

The credential-use model is:

```text
NTDS
 |
 +--> NT Hash
 |      |
 |      v
 |   Pass-the-Hash
 |
 +--> Kerberos Keys
 |      |
 |      v
 |   Pass-the-Key
 |
 +--> krbtgt
        |
        v
   Kerberos Forgery Risk
```

The detection model is:

```text
Unexpected Principal / Host
          |
          v
Replication Request
          |
          v
Domain Controller
          |
          v
4662 / Network Telemetry
          |
          v
Investigation
```

The direct-acquisition detection model is:

```text
Domain Controller
      |
      v
VSS / IFM / Backup Activity
      |
      v
NTDS + Registry Copy
      |
      v
Staging / Transfer
```

The safe validation model is:

```text
Enumerate Rights
      |
      v
Validate Effective Permission
      |
      v
Use Test Account
      |
      v
Targeted Replication
      |
      v
Redact Credential
      |
      v
Stop
```

The unsafe model is:

```text
Find DCSync
   |
   v
Dump Entire Domain
   |
   v
Thousands of Credentials
   |
   v
Unnecessary Exposure
```

The preferred model is:

```text
Minimum Evidence
      |
      v
Maximum Confidence
      |
      v
Minimum Credential Exposure
```

The most important distinction is:

```text
DCSync
   !=
NTDS File Theft
```

DCSync abuses:

```text
Replication Privilege
```

while offline extraction abuses access to:

```text
Directory Database Material
```

Another important distinction is:

```text
Not Domain Admin
      |
      X
Cannot Extract Domain Credentials
```

A principal with appropriate replication rights may have DCSync capability without conventional Domain Admin membership.

Similarly:

```text
Cannot Log On to DC
      |
      X
Cannot Obtain Domain Credentials
```

because:

```text
DCSync
```

may be performed remotely through legitimate replication interfaces.

For penetration testers:

```text
Do Not Ask:
"Can I dump the whole domain?"

Ask:
"What is the minimum credential-access action
required to demonstrate this privilege boundary?"
```

For defenders:

```text
Do Not Ask:
"Who is a Domain Admin?"

Ask:
"Which principals can replicate directory secrets,
modify replication permissions, access Domain
Controller backups, or otherwise obtain NTDS data?"
```

The final security model is:

```text
Domain Credentials
      |
      +--> Domain Controller Security
      |
      +--> Replication Rights
      |
      +--> Domain ACL
      |
      +--> Backup Security
      |
      +--> Privileged Administration
      |
      +--> Monitoring
```

Protecting `NTDS.dit` therefore requires protecting the entire ecosystem capable of accessing or reproducing its sensitive contents.

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Groups:

[Active Directory Groups](groups.md)

Credential Access:

[Active Directory Credential Access](credential-access.md)

Group Policy Preferences:

[Group Policy Preferences Passwords](gpp-passwords.md)

LAPS:

[Active Directory LAPS](laps.md)

gMSA:

[Group Managed Service Accounts](gmsa.md)

Shadow Credentials:

[Active Directory Shadow Credentials](shadow-credentials.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

---

# References

## Microsoft - Active Directory Database

[Microsoft - Data Store](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/active-directory-domain-services-data-store){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Directory Replication

[Microsoft - MS-DRSR: Directory Replication Service Remote Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-drsr/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Control Access Rights

[Microsoft - Control Access Rights](https://learn.microsoft.com/en-us/windows/win32/ad/control-access-rights){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Replication Rights

[Microsoft - DS-Replication-Get-Changes](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes){ target="_blank" rel="noopener noreferrer" }

[Microsoft - DS-Replication-Get-Changes-All](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes-all){ target="_blank" rel="noopener noreferrer" }

[Microsoft - DS-Replication-Get-Changes-In-Filtered-Set](https://learn.microsoft.com/en-us/windows/win32/adschema/r-ds-replication-get-changes-in-filtered-set){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Directory Service Access Auditing

[Microsoft - Audit Directory Service Access](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-directory-service-access){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4662](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4662){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Directory Service Changes

[Microsoft - Event 5136](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - ntdsutil

[Microsoft - ntdsutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ntdsutil){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Backup and Recovery

[Microsoft - Active Directory Forest Recovery Guide](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket - secretsdump.py](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py){ target="_blank" rel="noopener noreferrer" }

---

## Mimikatz

[Mimikatz](https://github.com/gentilkiwi/mimikatz){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - OS Credential Dumping: NTDS](https://attack.mitre.org/techniques/T1003/003/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - OS Credential Dumping: DCSync](https://attack.mitre.org/techniques/T1003/006/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

`NTDS.dit` represents one of the most security-sensitive data stores in an Active Directory environment.

The obvious attack model is:

```text
Compromise Domain Controller
        |
        v
Copy NTDS
        |
        v
Extract Credentials
```

but this is only one path.

A more complete model is:

```text
Domain Credential Material
        |
        +--> Direct DC Compromise
        |
        +--> DCSync
        |
        +--> Domain ACL Abuse
        |
        +--> Backup Compromise
        |
        +--> VSS / IFM
        |
        +--> Stolen System State
```

The DCSync relationship is particularly important:

```text
Principal
   |
   v
Replication Rights
   |
   v
Domain Credentials
```

This means a principal does not necessarily need:

```text
Domain Admin
```

membership to represent a domain-wide credential risk.

Likewise:

```text
Backup Server
```

should not be treated as ordinary infrastructure if it stores:

```text
Domain Controller Backups
```

because:

```text
DC Backup
   |
   v
NTDS + SYSTEM
   |
   v
Offline Domain Credential Access
```

For penetration testers, the preferred workflow is:

```text
Enumerate
   |
   v
Identify Replication / Backup Exposure
   |
   v
Determine Effective Privilege
   |
   v
Use Minimum Validation
   |
   v
Collect Minimum Credential Material
   |
   v
Stop
```

For defenders:

```text
Protect DCs
   |
   v
Protect Replication Rights
   |
   v
Protect Domain ACL
   |
   v
Protect Backups
   |
   v
Monitor Replication
   |
   v
Monitor Credential Access
```

The central question should not simply be:

```text
Who can log on to the Domain Controller?
```

It should be:

```text
Who can obtain the domain's credential material?
```

That includes principals capable of:

```text
Replicating Directory Secrets
Modifying Replication Rights
Reading Domain Controller Backups
Accessing NTDS Copies
Controlling Backup Infrastructure
Compromising Domain Controllers
```

The final security relationship is therefore:

```text
Active Directory
      |
      v
Credential Material
      |
      v
Authentication
      |
      v
Domain Trust
```

Once current domain credential material has been broadly exposed, the problem is no longer merely an isolated host compromise.

It becomes a domain recovery problem.
